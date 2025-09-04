from wedeliver_core_plus.app_decorators import handle_exceptions


def raise_exception_in_background(error):
    @handle_exceptions
    def raise_error(e):
        raise e

    try:
        raise_error(error)
    except Exception:
        return