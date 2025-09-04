def get_obj_value(_obj, key):
    if hasattr(_obj, '__dict__'):  # object
        return _obj.__dict__.get(key)

    elif isinstance(_obj, dict):  # dict
        return _obj.get(key)

    elif hasattr(_obj, key):  # class
        return getattr(_obj, key)


def get_obj_path_value(obj, path, default=None):
    """Fetches value at the specified path, handling mixed object and dict structures."""
    keys = path.split(".") if isinstance(path, str) else path

    current = obj
    for key in keys:
        current = get_obj_value(current, key)
        if current is None:  # Stop if any key along the path doesn't exist
            return default
    return current


def set_obj_value(_obj, attr_name, attr_value, append_if_exists=False):
    if not append_if_exists:
        try:
            setattr(_obj, attr_name, attr_value)
        except AttributeError:
            _obj[attr_name] = attr_value
    else:
        try:
            old_value = getattr(_obj, attr_name) if hasattr(_obj, attr_name) else None
            if old_value:
                if isinstance(old_value, dict):
                    setattr(_obj, attr_name, [old_value])
                getattr(_obj, attr_name).append(attr_value)
            else:
                setattr(_obj, attr_name, attr_value)
        except AttributeError:
            old_value = _obj.get(attr_name)
            if old_value:
                if isinstance(old_value, dict):
                    _obj[attr_name] = [old_value]

                _obj[attr_name].append(attr_value)
            else:
                _obj[attr_name] = attr_value
