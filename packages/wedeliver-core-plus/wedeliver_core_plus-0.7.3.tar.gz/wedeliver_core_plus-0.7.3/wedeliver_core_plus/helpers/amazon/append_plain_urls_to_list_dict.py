from wedeliver_core_plus.helpers.amazon.get_file_url import get_file_url

from wedeliver_core_plus.helpers.amazon.get_s3_client import get_s3_client


def append_plain_urls_to_list_dict(list_dict, key_name):
    """
    This function will append plain url to list of dictionaries
    :param list_dict: list of dictionaries
    :param key_name: key name to append plain url to
    :return: list of dictionaries
    """
    s3_client = get_s3_client()
    for item in list_dict:
        item[key_name] = get_file_url(item.get(key_name), s3_client=s3_client)
    return list_dict
