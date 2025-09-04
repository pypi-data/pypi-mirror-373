from flask import request, g

# from flask import session

from .authenticate import authenticate
from .micro_fetcher import MicroFetcher
from flask_babel import _

from wedeliver_core_plus.helpers.hmac_validator import verify_hmac_code
from wedeliver_core_plus.helpers.exceptions import AppExpiredTokenError, AppValidationError, AppTokenRefreshRequired
import jwt
import base64
# import hmac
# import hashlib
from wedeliver_core_plus import WedeliverCorePlus


class Auth:
    def __init__(self):
        pass

    @staticmethod
    def set_user(user):
        """
        Set user in flask global object and session
        """
        g.user = user  # store user in flask global object
        # session["user"] = user

    @staticmethod
    def get_user():
        default_user_str = 'administrator@wedeliverapp.com'
        try:
            user = g.get("user", dict())
        except Exception:
            user = dict(user_id=default_user_str, email=default_user_str)

        return user

    @staticmethod
    def get_user_language():
        user = Auth.get_user()
        language = find_user_language(user)
        return language

    @staticmethod
    def get_user_str():
        # app = WedeliverCorePlus.get_app()
        # with app.test_request_context():
        user = Auth.get_user()

        if user.get('email'):
            return user.get('email')
        else:
            return "Account-{}".format(
                user.get("account_id")
            )


def find_user_language(user=None):
    try:
        language = (
            request.headers["Accept-Language"].lower()
            if (
                    "Accept-Language" in request.headers
                    and request.headers["Accept-Language"] in ["en", "ar"]
            )
            else ((user.get("language") or 'ar') if user else 'ar')
        )
    except Exception:
        language = 'ar'

    return language


def validate_device_fingerprint(fingerprint, token_payload):
    """
    Validate if the given fingerprint matches the token's device_id.
    
    Args:
        fingerprint: The fingerprint to validate
        token_payload: The decoded token payload containing user and device information
        
    Returns:
        bool: True if fingerprint is valid and matches the token's device ID
    """
    if not fingerprint or not token_payload:
        return False
        
    try:
        # Check if it's a valid base64 encoded string
        decoded = base64.b64decode(fingerprint)
        # SHA256 HMAC should be 32 bytes
        if len(decoded) != 32:
            return False
            
        # Get account_id and device_id from token
        account_id = token_payload.get('account_id')
        device_id = token_payload.get('device_id')
        
        if not account_id or not device_id:
            return False
            
        # Verify the fingerprint against the expected one
        return verify_hmac_code(account_id, device_id, fingerprint)
        
    except Exception:
        return False


def check_token_version(token, skip_expiration_check=False):
    """
    Check token version and determine which verification method to use.
    
    Args:
        token: Auth token to check
        skip_expiration_check: If True, don't validate token expiration (default: False)
        
    Returns:
        tuple: (use_v4, version, token_payload) where use_v4 is a boolean indicating if v4 verification should be used,
               version is the token version (or None if not present), and token_payload is the decoded token data
    """
    try:
        # Assuming token is in format "Bearer <actual_token>"
        if token.startswith("Bearer "):
            token_value = token.split(" ")[1]
        else:
            token_value = token
            
        # Decode JWT token using the same method as in authenticate
        app = WedeliverCorePlus.get_app()
        verify_token = app.config.get("FLASK_ENV") == "production" or app.config.get("TESTING") == True
        
        # Decode without verification to read the payload
        # (we're just checking the version, not authenticating)
        options = {
            "verify_signature": verify_token
        }
        
        # Skip expiration check if requested
        if skip_expiration_check:
            options["verify_exp"] = False
            
        token_payload = jwt.decode(
            token_value,
            key=app.config.get("SECRET_KEY"),
            algorithms=["HS256"],
            options=options
        )
        
        # Check if version exists and is >= 1
        version = token_payload.get('token_version')
        if version is not None:
            return (int(version) >= 2, version, token_payload)
            
    except (jwt.DecodeError, jwt.ExpiredSignatureError, Exception) as e:
        # If any error occurs during parsing, default to v3
        print(f"Token parsing error: {str(e)}")
        pass
    
    return (False, None, None)


def verify_user_token_v2(token):
    results = MicroFetcher(
        "AUTH_SERVICE"
    ).from_function(
        "app.business_logic.auth.authenticate.authenticate"
    ).with_params(
        token=token
    ).fetch()

    results["data"].update(token=token)

    user = results["data"]
    user["language"] = find_user_language(user)

    Auth.set_user(user)

    return user


def verify_user_token_v3(token):
    results = authenticate(token)

    results["data"].update(token=token)
    user = results["data"]

    # get language form accept language in header of request
    user["language"] = find_user_language(user)

    Auth.set_user(user)

    return user


def verify_user_token_v4(token, device_fingerprint=None, skip_expiration_check=False):
    """
    Verify a user token with refresh token support.
    
    Args:
        token: The access token to verify
        device_fingerprint: Optional device fingerprint for verification
        skip_expiration_check: Optional skip expiration check

    Returns:
        dict: The decoded token data or new access token data
        
    Raises:
        AppExpiredTokenError: If the token is expired and no valid refresh token is available
        AppValidationError: If the token is invalid or refresh token verification fails
        AppTokenRefreshRequired: If the token needs to be refreshed and a new access token is available
    """
    try:
        # Try to verify the access token using auth service
        user = MicroFetcher("AUTH_SERVICE").from_function(
            "app.business_logic.auth.mobile.token_operations.verify_access_token"
        ).with_params(
            token=token,
            skip_expiration_check=skip_expiration_check
        ).execute()

        user["language"] = find_user_language(user)
        Auth.set_user(user)

        return user

    except AppExpiredTokenError:
        # Access token has expired, check if refresh token is provided
        refresh_token = request.headers.get("X-Refresh-Token")
        
        if not refresh_token:
            # No refresh token, re-authentication is needed
            raise AppExpiredTokenError(_("Token expired, re-authentication required"))
        
        try:
            # Try to refresh the access token using auth service
            new_access_token = MicroFetcher("AUTH_SERVICE").from_function(
                "app.business_logic.auth.mobile.token_operations.refresh_access_token"
            ).with_params(
                refresh_token=refresh_token,
                device_fingerprint=device_fingerprint
            ).execute()
            
            # Raise specialized exception with the new access token
            raise AppTokenRefreshRequired(
                message=_("Token refreshed"),
                new_access_token=new_access_token
            )
            
        except (AppExpiredTokenError, AppValidationError):
            # Refresh token is also invalid or expired, re-authentication is needed
            raise AppExpiredTokenError(_("Session expired, re-authentication required"))
