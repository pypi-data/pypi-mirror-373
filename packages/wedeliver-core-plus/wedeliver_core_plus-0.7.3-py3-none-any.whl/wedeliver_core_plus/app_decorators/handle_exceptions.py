import traceback
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError

from wedeliver_core_plus import WedeliverCorePlus
from wedeliver_core_plus.helpers.auth import Auth
from wedeliver_core_plus.helpers.format_exception import format_exception
from wedeliver_core_plus.helpers.kafka_producers.notification_center import send_critical_error

from wedeliver_core_plus.helpers.validate_parameters import (
    validate_parameters,
)


def handle_exceptions(func):
    app = WedeliverCorePlus.get_app()

    @wraps(func)
    def inner_function(*args, **kws):
        try:
            result = func(*args, **kws)
            return result

        except Exception as e:
            # If the error related to the Database, then close the database session if it is open
            if isinstance(e, SQLAlchemyError):
                try:
                    db = app.extensions['sqlalchemy'].db
                    db.session.close()
                except Exception:
                    pass

            notification_channel = None
            if func is not None:
                if not validate_parameters(function=func):
                    notification_channel = "empty-parameters"

            use_default_response_message_key = True
            if hasattr(e, "custom_exception"):
                public_message = e.args[0] if e.args else e.message if hasattr(e, 'message') else 'Unknown'
                status_code = e.code
                use_default_response_message_key = (
                    e.use_default_response_message_key
                    if hasattr(e, 'use_default_response_message_key') else True
                )
                send_notification = hasattr(e, "silent") and not e.silent
                notification_channel = "soft-errors"
            else:
                send_notification = True
                public_message = "Unhandled Exception"
                status_code = 500

            message = format_exception(
                exception=traceback.format_exc(),
                user=Auth.get_user(),
                status_code=status_code
            )
            # if app.config.get('FLASK_ENV') != 'testing':
            app.logger.error(message)
            if send_notification:
                send_critical_error(message=message, channel=notification_channel)

            return public_message, status_code, use_default_response_message_key

    return inner_function
