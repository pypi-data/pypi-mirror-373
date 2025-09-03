from urllib.parse import urlparse


def get_plain_url(url):
    try:
        result = urlparse(url)
        is_url = all([result.scheme, result.netloc])
        if is_url:
            return "{}://{}{}".format(result.scheme, result.netloc, result.path)
    except Exception:
        pass

    return None
