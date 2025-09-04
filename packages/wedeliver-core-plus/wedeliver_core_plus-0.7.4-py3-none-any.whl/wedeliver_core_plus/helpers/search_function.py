from wedeliver_core_plus.helpers.get_country_code import get_country_code
from wedeliver_core_plus.helpers.sql import sql


def search_function(table_name, search_list, append_extra=None, use_country_code=True):
    """
    """
    validation_error = []

    country_code = None
    if use_country_code:
        country_code = get_country_code()

    def _find_matched(db_results, key, search_item, operator=None):
        for db_instance in db_results:
            if operator == 'LIKE':
                if search_item.get("search_value") in db_instance.get(key):
                    return db_instance
            else:
                if search_item.get("search_value") == db_instance.get(key):
                    return db_instance
        return None

    for item_dict in search_list:
        # query = db.session.query(model)

        input_group_search_key = item_dict.get('search_key') or "id"

        input_group = item_dict.get('inputs')
        input_group_operator = item_dict.get('operator')
        input_group_list = [obj.get("search_value") for obj in input_group]

        # model_key = model.__dict__.get(input_group_search_key)
        # result_db = query.filter(model_key.in_(input_group_list)).all()
        # result_db_list = [obj.__dict__.get(input_group_search_key) for obj in result_db]

        if input_group_operator == "LIKE":
            where_condition = "RLIKE '{input_group_list}'".format(
                input_group_list='|'.join(str(value) for value in input_group_list),
            )
        else:
            where_condition = "IN ('{input_group_list}')".format(
                input_group_list='\',\''.join(str(value) for value in input_group_list),
            )
        query = """SELECT *
                FROM {table_name}
                WHERE {input_group_search_key} {where_condition} {country_code_condition}""".format(
            input_group_search_key=input_group_search_key,
            where_condition=where_condition,
            country_code_condition="AND country_code='{}'".format(country_code) if country_code else "",
            table_name=table_name,
        )
        result_db = sql(query)
        result_db_list = [obj.get(input_group_search_key) for obj in result_db]

        # if len(input_group_list) != len(result_db_list):

        def _match_value(search_in, search_for):
            _matched_count = 0
            for li in search_in:
                if input_group_operator == 'LIKE' and search_for in li:
                    _matched_count += 1
                elif input_group_operator == 'IN' and search_for == li:
                    _matched_count += 1
            return _matched_count

        for obj in input_group:
            if _match_value(result_db_list, obj.get("search_value")) == 0:
                error_obj = dict(
                    indexes=obj.get("indexes")
                )
                error_obj[input_group_search_key] = dict(
                    message="{} '{}' is not exists".format(input_group_search_key, obj.get("search_value"))
                )

                validation_error.append(error_obj)
            elif _match_value(result_db_list, obj.get("search_value")) > 1:
                error_obj = dict(
                    indexes=obj.get("indexes")
                )
                error_obj[input_group_search_key] = dict(
                    message="{} '{}' too many exists, can not determine witch one".format(input_group_search_key,
                                                                                          obj.get("search_value"))
                )

                validation_error.append(error_obj)
            else:
                matched_obj = _find_matched(db_results=result_db, key=input_group_search_key, search_item=obj,
                                            operator=input_group_operator)
                obj.update(dict(
                    matched_id=matched_obj.get("id")
                ))
                if append_extra and isinstance(append_extra, list):
                    for _append_key in append_extra:
                        obj[_append_key] = matched_obj.get(_append_key)

    return search_list, validation_error
