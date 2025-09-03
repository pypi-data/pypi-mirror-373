import collections
from wedeliver_core_plus.helpers.time import get_datetime


def mapping_filters(filters):
    """
    mapping the filters to the correct keys
    "key_name":{
           "filterType": "value",
            "filterValue": "value",
            "filterOperator": "value"
    }
    to {"field": "key_name", "op": value "value": value}

    """
    # < : <= : > : >= : = : != : like %txt% : contains : in [list]]],
    flask_filters = []
    for key, value in filters.items():
        if (
            value.get("filterOperator")
            in [
                "<",  # less than
                ">",  # greater than
                "=",  # equal to
                "!=",  # not equal to
                "like",  # like %txt%
                "contains",  # many-to-many relationship
                "in",  # in [list]
                "<=",  # less than or equal to
                ">=",  # greater than or equal to
            ]
            and value["filterValue"] is not None
            and value["filterValue"] != ""
        ):
            if value["filterOperator"] == "like":
                flask_filters.append(
                    {
                        "field": key,
                        "op": "like",
                        "value": "%" + value["filterValue"] + "%",
                    }
                )

            else:
                flask_filters.append(
                    {
                        "field": key,
                        "op": value["filterOperator"],
                        "value": get_datetime(str(value["filterValue"]))
                        if value.get("filterType") == "date"
                        else value["filterValue"],
                    }
                )

        if (
            value.get("filterOperator")
            in [
                "between",  # between two values for the dates
            ]
            and value["filterValue_from"] is not None
            and value["filterValue_from"] != ""
            and value["filterValue_to"] is not None
            and value["filterValue_to"] != ""
        ):
            if value["filterOperator"] == "between":
                flask_filters.append(
                    {
                        "field": key,
                        "op": ">=",  # greater than or equal to from_date
                        "value": get_datetime(str(value["filterValue_from"])),
                    }
                )

                flask_filters.append(
                    {
                        "field": key,
                        "op": "<=",
                        "value": get_datetime(str(value["filterValue_to"])),
                    }
                )

    return flask_filters


def split_filters(filters, external_keys, join_keys):
    """
    exclude the external services fields from the filters
    """
    internal_filters = {}
    external_filters = {}
    join_filters = {}
    for k, v in filters.items():
        if k in external_keys:
            external_filters[k] = v
        elif k in join_keys:
            join_filters[k] = v
            join_filters[k].update(join_keys[k])
        else:
            internal_filters[k] = v
    return internal_filters, join_filters, external_filters


def create_join_query(query, model, condition):
    return query.join(model, condition, isouter=True)


def split_join_filters(dict_dict, split_key):
    list_dict = convert_dict_dict_to_list_dict(dict_dict)

    several_list = split_list_dict_to_several_list(list_dict, split_key)

    list_dict_dict = convert_several_list_to_several_dict_dict(
        several_lists=several_list, id_key="id", split_key=split_key
    )

    return list_dict_dict


def convert_several_list_to_several_dict_dict(several_lists, id_key, split_key):
    list_result = []
    for list_ in several_lists:
        new_dict = {item[id_key]: item for item in list_}
        new_dict.update({"join_table": item["join_table"] for item in list_})

        list_result.append(new_dict)

    return list_result


def convert_dict_dict_to_list_dict(dict_dict):
    list_dict = [
        (lambda d: d.update(id=key) or d)(val) for (key, val) in dict_dict.items()
    ]
    return list_dict


def split_list_dict_to_several_list(list_dict, key):

    result = collections.defaultdict(list)

    for d in list_dict:
        result[d[key]].append(d)

    result_list = list(result.values())
    return result_list


def pagination_total_numbers(data, page, per_page, order_by, total_count):

    total_count = total_count
    page = int(page) if page else 1
    per_page = int(per_page) if per_page else total_count
    return dict(
        total_count=total_count, page=page, per_page=per_page, order_by=order_by
    )
