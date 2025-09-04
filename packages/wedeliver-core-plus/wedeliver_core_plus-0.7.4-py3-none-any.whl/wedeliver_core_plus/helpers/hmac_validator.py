import hmac
import hashlib
import base64
from functools import wraps

from flask import request, g
from wedeliver_core_plus.helpers.exceptions import AppForbiddenError
from flask_babel import _
from wedeliver_core_plus import WedeliverCorePlus


def generate_hmac_code(account_id, device_id):
    """Generate HMAC code for API request validation"""
    app = WedeliverCorePlus.get_app()
    key = app.config.get("SECRET_KEY").encode("utf-8")
    message = f"{account_id}:{device_id}".encode("utf-8")
    hmac_digest = hmac.new(key, message, hashlib.sha256).digest()
    return base64.b64encode(hmac_digest).decode("utf-8")


def verify_hmac_code(account_id, device_id, provided_hmac):
    """Verify that the provided HMAC code is valid"""
    if not provided_hmac:
        return False

    expected_hmac = generate_hmac_code(account_id, device_id)
    return hmac.compare_digest(expected_hmac, provided_hmac)


def require_valid_hmac():
    """Decorator for routes that require HMAC validation"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get the HMAC from the request headers
            hmac_code = request.headers.get("X-HMAC-Code")

            # Get account_id and device_id from the token data stored in g.user
            if not hasattr(g, "user") or not g.user:
                raise AppForbiddenError(_("Unauthorized - Authentication required"))

            account_id = g.user.get("account_id")
            device_id = g.user.get("device_id")

            if not account_id or not device_id:
                raise AppForbiddenError(_("Unauthorized - Invalid token data"))

            # Verify the HMAC
            if not verify_hmac_code(account_id, device_id, hmac_code):
                raise AppForbiddenError(_("Unauthorized - Invalid HMAC code"))

            return f(*args, **kwargs)

        return decorated_function

    return decorator
