import inspect
from datetime import datetime
from sys import platform
from wedeliver_core_plus import WedeliverCorePlus
from flask import request


def format_exception(exception, user=None, status_code=None, soft_message=None):
    app = WedeliverCorePlus.get_app()
    user = user or dict()
    caller_frame = None
    user_id = None
    token = None
    user_agent = None
    role = None
    node = None
    args = None
    ip = None
    data = None

    try:
        caller_frame = request.path
    except Exception:
        try:
            caller_frame = inspect.currentframe()
            caller_frame = inspect.getouterframes(caller_frame, 2)[1][3]
        except Exception:
            pass

    try:
        ip = request.headers.get('X-Real-IP') or request.headers.get('X-Forwarded-For') or request.remote_addr
    except Exception:
        pass

    try:
        user_agent = request.headers.get('User-Agent')
    except Exception:
        pass

    try:
        args = str(request.args.to_dict())[:1000]
    except Exception:
        pass

    try:
        content_type = request.headers.get('Content-Type')
        if content_type and 'application/json' in content_type:
            # if the request have json payload, the user need to send the Content-Type as application/json
            data = str(request.json)[:1000]
        else:
            data = str(request.form.to_dict())[:1000]
    except Exception:
        pass

    try:
        if user:
            user_id = "{0} - {1} - {2}".format(
                user.get("email"),
                user.get("mobile"),
                user.get("user_id"),
            )
    except Exception:
        pass

    try:
        role = user.get("role")
    except Exception:
        pass

    try:
        node = platform if type(platform) is str else str(platform.node())
    except Exception:
        pass

    try:
        if "Authorization" in request.headers:
            token = request.headers["Authorization"]
    except Exception:
        pass

    return """Node: {node}
Time: {_time}
Env: {env}
IP: {ip}
API: {call}
User: {user}
Token: {token}
User Agent: {user_agent}
Role: {role}
Args: {args}
Data: {data}
Status Code: {status_code}
Soft Message: {soft_message}
Error: {error}""".format(
        env=app.config.get("FLASK_ENV") or "Unknown",
        call=caller_frame or "Unknown",
        user=user_id or "Unknown",
        token=token or "Unknown",
        user_agent=str(user_agent) or "Unknown",
        role=role or "Unknown",
        node=node or "Unknown",
        _time=str(datetime.now()),
        ip=ip or "Unknown",
        args=args or "Unknown",
        data=data or "Unknown",
        error=exception or "Unknown",
        status_code=status_code or "Unknown",
        soft_message=soft_message or "Unknown",
    )
