from functools import wraps

from flask import request, jsonify, current_app

from wedeliver_core_plus.helpers.auth import (
    verify_user_token_v2,
    Auth,
    verify_user_token_v3,
    verify_user_token_v4,
    check_token_version,
    validate_device_fingerprint
)
from wedeliver_core_plus.helpers.exceptions import (
    AppValidationError,
    AppMissingAuthError, AppForbiddenError, AppDeprecatedApiError,
    AppExpiredTokenError, AppTokenRefreshRequired,
)
from flask_babel import _


def handle_auth(require_auth, append_auth_args=None, allowed_roles=None, pre_login=False,
                allowed_permissions=None, guards=[], deprecated=False):
    """
    A decorator for route functions that handles authentication with optional refresh token support.
    
    Args:
        require_auth: Whether authentication is required
        append_auth_args: List of arguments to extract from token and append to function kwargs
        allowed_roles: List of roles allowed to access this endpoint
        pre_login: Whether the endpoint is used in pre-login flow
        allowed_permissions: List of permissions allowed to access this endpoint
        guards: List of guard functions to check
        deprecated: Whether the endpoint is deprecated
    """

    def factory(func):
        @wraps(func)
        def inner_function(*args, **kws):
            if deprecated:
                raise AppDeprecatedApiError(_("This API is deprecated and no longer available"))
            token = request.headers.get("Authorization")

            if not require_auth:
                if token:
                    user = get_user_from_token(token=token)
                    apply_append_auth_args(append_auth_args=append_auth_args, kws=kws, user=user)
                return func(*args, **kws)

            if "Authorization" not in request.headers:
                raise AppMissingAuthError(_("Missing authentication"))


            if "country_code" not in request.headers and request.endpoint != "health_check":
                raise AppValidationError(_("Country Code is Required (c)"))

            # Get device fingerprint from headers if available
            device_fingerprint = request.headers.get("X-Device-Fingerprint")

            # Check token version and use appropriate verification method
            user = get_user_from_token(token=token)

            if not pre_login:
                if not user.get("is_logged"):
                    raise AppValidationError(_("Not Logged Token, please complete login process"))

            if allowed_roles:
                if user.get("role") not in allowed_roles:
                    raise AppValidationError(_("Not Allowed Role"))

            if guards:
                for guard in guards:
                    if not guard():
                        raise AppForbiddenError("Not Allowed Feature")
            apply_append_auth_args(append_auth_args=append_auth_args,kws=kws,user=user)

            return func(*args, **kws)

        return inner_function

    return factory

def get_user_from_token(token):
    # Get device fingerprint from headers if available
    device_fingerprint = request.headers.get("X-Device-Fingerprint")

    # Check token version and use appropriate verification method
    use_v4, version, token_payload = check_token_version(token,
                                                         skip_expiration_check=True)

    if use_v4:
        if not device_fingerprint:
            raise AppValidationError(_("Device fingerprint is required for token version 2 or higher"))

        # Validate device fingerprint matches the device_id in token
        if not validate_device_fingerprint(device_fingerprint, token_payload):
            raise AppValidationError(_("Invalid device fingerprint or device ID mismatch"))

        user = verify_user_token_v4(token, device_fingerprint,
                                    skip_expiration_check=request.endpoint == "token_refresh_service")
    else:
        user = verify_user_token_v3(token=token)
    return user

def apply_append_auth_args(append_auth_args,kws,user):
    if append_auth_args and isinstance(append_auth_args, list):
        for arg in append_auth_args:
            if not kws.get('appended_kws'):
                kws['appended_kws'] = dict()
            if '.' in arg:
                if 'as' in arg:
                    arg, as_arg = arg.split(' as ')
                else:
                    as_arg = arg.replace('.', '_')

                obj, key = arg.split('.')
                value = user.get(obj, {}).get(key)
                kws['appended_kws'][as_arg] = value
            else:
                value = user.get(arg)
                kws['appended_kws'][arg] = value