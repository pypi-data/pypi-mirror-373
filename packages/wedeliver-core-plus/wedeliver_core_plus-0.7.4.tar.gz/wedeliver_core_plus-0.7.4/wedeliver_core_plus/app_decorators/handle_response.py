import json
from functools import wraps
from flask import Response


def handle_response(func):
    @wraps(func)
    def inner_function(*args, **kwargs):
        result = func(*args, **kwargs)
       
        if isinstance(result, Response):
            return result

        response = result
        code = 200
        use_default_response_message_key = True

        if isinstance(result, tuple):
            response = result[0]
            code = result[1]
            use_default_response_message_key = result[2]

        if code not in [200, 201, 204] and use_default_response_message_key:
            response = dict(message=response)

        return Response(
            json.dumps(response), content_type="application/json", status=code
        )

    return inner_function
