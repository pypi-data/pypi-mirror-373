from wedeliver_core_plus.helpers.auth import Auth


def get_translated_value(
    obj,
    key_ar,
    key_en,
    language=None,
    fallback_language="ar",
):
    # Determine if the object is a class instance or dictionary
    if not language:
        language = Auth.get_user_language()
    if isinstance(obj, dict):
        value_ar = obj.get(key_ar)
        value_en = obj.get(key_en)
    else:
        value_ar = getattr(obj, key_ar, None)
        value_en = getattr(obj, key_en, None)

    # Returns the value based on the language preference
    return_value = value_ar if language == "ar" else value_en
    if return_value:
        return return_value

    # Fall back value in case the return_value is null
    return value_ar if fallback_language == "ar" else value_en
