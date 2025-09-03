import inspect

import traceback
from flask import request

from wedeliver_core_plus.helpers.get_embedded_function import (
    get_embedded_function,
)


def validate_parameters(function, app=None):
    """
    This function is used to validate the parameters that are sent to the API
    :param function: The function that is called
    :return:
    """
    # Get the parameters that are required for the function
    try:
        function = get_embedded_function(function)
        if not function:
            return True

        if not request:
            return True
        required_parameters = inspect.getfullargspec(function)

        if (
                not request.original_form
                and not request.original_args
                and len(required_parameters.args) != 0
        ):
            return False
    except Exception:
        app.logger.error(
            "empty_parameters_validation: {0}".format(traceback.format_exc())
        )
        return True
    return True
