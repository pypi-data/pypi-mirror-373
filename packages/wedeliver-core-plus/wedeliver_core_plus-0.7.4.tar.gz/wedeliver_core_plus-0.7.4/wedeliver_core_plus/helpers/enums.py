from enum import Enum
from typing import List, Union, Any

from wedeliver_core_plus.helpers.service_config import ServiceConfig


DYNAMIC_LOOKUP_OPERATORS = ("=", "!=")
STATIC_LOOKUP_OPERATORS = (*DYNAMIC_LOOKUP_OPERATORS, "%LIKE%", "%LIKE", "LIKE%", ">=", "<=", ">", "<")


class Service:
    CAPTAIN = ServiceConfig('CAPTAIN_SERVICE')
    FINANCE = ServiceConfig('FINANCE_SERVICE')
    SDD = ServiceConfig('SDD_SERVICE')
    SUPPLIER = ServiceConfig('SUPPLIER_SERVICE')
    PN = ServiceConfig('PN_SERVICE')
    FINTECH = ServiceConfig('FINTECH_SERVICE')
    STC = ServiceConfig('STC_SERVICE')
    AUTH = ServiceConfig('AUTH_SERVICE')
    MAIL = ServiceConfig('MAIL_SERVICE')
    SMS = ServiceConfig('SMS_SERVICE')
    APILAYER = ServiceConfig('APILAYER_SERVICE')
    INVOICE = ServiceConfig('INVOICE_SERVICE')
    ADDRESS = ServiceConfig('ADDRESS_SERVICE')
    PUBLIC = ServiceConfig('PUBLIC_SERVICE')
    INTERNAL_NOTIFICATION = ServiceConfig('INTERNAL_NOTIFICATION_SERVICE')


class QueryTypes(Enum):
    SIMPLE_TABLE = 1
    FUNCTION = 2
    SEARCH = 3
    ADVANCED_TABLE = 4
    POPULATE_TABLE = 5


class LookUpType(Enum):
    DYNAMIC = "dynamic"
    STATIC = "static"


class FilterOperatorsType(Enum):
    AND = "AND"
    OR = "OR"


class InstallmentType(Enum):
    LEASE = 'Lease'
    PERSONAL_LOAN = 'Personal Loan'


class TaskExecutionStatus(Enum):
    PENDING = "Pending"
    RUNNING = "Running"
    SUCCESS = "Success"
    FAILED = "Failed"


class TaskReversionStatus(Enum):
    PENDING = "Pending"
    SUCCESS = "Success"
    FAILED = "Failed"


def list_enum_values(enum_type):
    "return list of dict the enum values and names for the given enum type"
    return [dict(id=e.value, Value=e.name.capitalize()) for e in enum_type]


def list_enum_values_v2(enum_type):
    "return list of dict the enum values and names for the given enum type"
    return [dict(id=e.value, value=e.value) for e in enum_type]


def get_enum_value(enum_value, enum_type):
    "return  dict the enum values and names for the given enum type"
    for e in enum_type:
        if e.value == enum_value:
            return dict(id=e.value, Value=e.name.replace("_", " ").capitalize())


def format_values_dict(**values):
    "return  dict the enum values and names for the given enum type"
    return dict(**values)


class OrderByEnum(Enum):
    asc = "asc"
    desc = "desc"


def format_engine_size(engine_size_enum_type):
    "return the engine size in the format of 1.0 L"
    return [
        dict(id=e.value, Value=e.name[1:].replace("_", ".").capitalize() + " L")
        for e in engine_size_enum_type
    ]


def format_enum_with_dash(engine_size_enum_type):
    "return the enum containing dash to be without dash"
    return [
        dict(id=e.value, Value=e.name.replace("_", " ").capitalize())
        for e in engine_size_enum_type
    ]


class GetEumValue(Enum):
    @classmethod
    def get_value_of_key(cls, color_name):
        if color_name is None:
            return None

        member = cls.__members__.get(color_name.lower())
        if member is not None:
            return member.value  # Return the value of the member
        return None

    @classmethod
    def get_key_of_value(cls, value):
        if value is None:
            return None

        for key, val in cls.__members__.items():
            if val.value == value:
                return key.capitalize()  # Capitalize the first letter of the key

        return None


class VehicleColorEnum(GetEumValue):
    red = 1
    blue = 2
    black = 3
    silver = 4
    gray = 5
    white = 6
    maroon = 7
    purple = 9
    fuchsia = 10
    green = 11
    lime = 12
    olive = 13
    yellow = 14
    navy = 15
    teal = 17
    aqua = 18
    black_and_red = 19


class App(Enum):
    """Languages"""

    CUSTOMER_APP = "Customer App"
    WEB_APP = "Web App"
    UBER_LEAD_WEB_APP = "Uber Lead Web App"
