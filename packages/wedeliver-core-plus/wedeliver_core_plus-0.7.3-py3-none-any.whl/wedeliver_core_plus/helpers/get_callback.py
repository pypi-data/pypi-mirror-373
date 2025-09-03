import importlib


def get_callback(module, function):
    if not module or not function:
        return None

    try:
        module = importlib.import_module(module)
    except ImportError:
        return None

    if not hasattr(module, function):
        return None

    callback = getattr(module, function)

    return callback if callable(callback) else None
