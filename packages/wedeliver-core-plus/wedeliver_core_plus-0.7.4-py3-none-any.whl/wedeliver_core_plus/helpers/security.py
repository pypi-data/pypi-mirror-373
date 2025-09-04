import jwt
import hashlib
from flask import request
from datetime import datetime
from app import app
from wedeliver_core_plus.helpers.exceptions import AppValidationError


def authenticate_token(token, force_expiration_datetime):
    """
    This function is used to authenticate the user token
    """

    try:
        verify_token = app.config.get("FLASK_ENV") == "production"
        token_result = jwt.decode(
            token,
            key=app.config.get("SECRET_KEY"),
            algorithms=["HS256"],
            do_verify=verify_token,
        )
        # user_role = token_result.get("role")
        # Test

        if request.headers.get("Accept-Language") in ("ar", "en"):
            token_result["language"] = request.headers.get("Accept-Language")
        else:
            token_result["language"] = token_result.get("language", "ar")

        user_app = token_result.get("app")

        if not token_result.get("created_at"):
            raise jwt.ExpiredSignatureError()

        token_created_at = datetime.strptime(
            token_result.get("created_at"), "%Y-%m-%d %H:%M:%S"
        )
        for rule_app, expire_datetime, message in force_expiration_datetime:
            if rule_app == user_app and token_created_at < expire_datetime:
                raise jwt.ExpiredSignatureError(message)

        return dict(message="Valid User", data=token_result)

    except jwt.DecodeError:
        raise AppValidationError("Token is not valid")
    except jwt.ExpiredSignatureError:
        raise AppValidationError("Token is expired")


def hash_password(password):
    # """Hash a password for storing."""
    hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return hashed_password


def verify_password(stored_password, provided_password):
    hashed_plaintext_password = hashlib.sha256(
        provided_password.encode("utf-8")
    ).hexdigest()
    return hashed_plaintext_password == stored_password
