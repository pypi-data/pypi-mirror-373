import jwt
from flask import request
from datetime import datetime
from flask_babel import _

from wedeliver_core_plus import WedeliverCorePlus
from wedeliver_core_plus.helpers.enums import App
from wedeliver_core_plus.helpers.exceptions import AppExpiredTokenError, AppAccessTokenExpiredError


def authenticate(token, api=None):
    try:
        app = WedeliverCorePlus.get_app()
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

        user_token = UserToken(token_result)
        user_token.raise_if_customer_app_token_expired()

        return dict(message="Valid User", data=token_result)

    except jwt.DecodeError:
        raise AppExpiredTokenError(_("Token is not valid, please do login"))
    except jwt.ExpiredSignatureError:
        raise AppExpiredTokenError(_("Token is expired, please refresh token"))


class UserToken(object):
    user_app = None
    token_created_at = None

    def __init__(self, token_result):
        self.user_app = token_result.get("app")
        self.token_created_at = datetime.strptime(
            token_result.get("created_at"), "%Y-%m-%d %H:%M:%S"
        )

    def raise_if_customer_app_token_expired(self):
        app = WedeliverCorePlus.get_app()
        expire_datetime_env = app.config.get("FORCE_LOGOUT_CUSTOMER_APP_UTC_DATETIME")
        if expire_datetime_env and self.user_app == App.CUSTOMER_APP.value:
            try:
                # Convert the string to a datetime object
                expire_datetime = datetime.strptime(
                    expire_datetime_env, "%Y-%m-%d %H:%M"
                )
                if self.token_created_at < expire_datetime:
                    raise jwt.ExpiredSignatureError(
                        _("Please re-login to your account")
                    )
            except ValueError:
                app.logger.error(
                    f"FORCE_LOGOUT_CUSTOMER_APP_DATETIME env has wrong data format, {expire_datetime_env}"
                )
