from flask import request


def get_country_code():
    country_code = "sa"
    if request and request.headers.get("country_code"):
        country_code = request.headers.get("country_code")
    return country_code
