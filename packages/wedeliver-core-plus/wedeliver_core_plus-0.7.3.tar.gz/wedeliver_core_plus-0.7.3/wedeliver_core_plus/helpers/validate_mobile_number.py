import re
from wedeliver_core_plus.helpers.get_country_code import get_country_code


def validate_mobile_number(mobile, force_only=None):
    if not mobile.isdigit():
        return False
    mobile = mobile.replace("+", "").replace(" ", "").lstrip("0")
    if len(mobile) < 12:
        country_code = get_country_code()
        if country_code == "sa":
            dial = "966"
        elif country_code == "ps":
            dial = "970"
        elif country_code == "eg":
            dial = "20"
        else:
            return False

        mobile = "{0}{1}".format(dial, int(mobile))

    saudi_regex     = re.match(r"^(009665|9665|\+9665|05|5)([0-9]{8})$", str(mobile))
    palestine_regex = re.match(r"^(009705|9705|\+9705|05|5)([0-9]{8})$", str(mobile))
    egypt_regex = re.match(r"^(00201|201|\+201|01|1)([0-9]{9})$", str(mobile))

    if force_only:
        if force_only == "sa":
            if saudi_regex:
                return mobile
            else:
                return False
        elif force_only == "ps":
            if palestine_regex:
                return mobile
            else:
                return False
        elif force_only == "eg":
            if egypt_regex:
                return mobile
            else:
                return False
        else:
            return False
    else:
        if (
            saudi_regex
            or palestine_regex
            or egypt_regex
        ):
            return mobile
        else:
            return False
