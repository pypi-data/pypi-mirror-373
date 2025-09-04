from sqlalchemy import text
from wedeliver_core_plus import WedeliverCorePlus


def sql(query):
    """

    :param query:
    :return:
    """
    app = WedeliverCorePlus.get_app()
    db = app.extensions['sqlalchemy'].db

    result = db.engine.execute(text(query))
    result_list = list()
    # app.logger.debug(result)
    for rowproxy in result:
        temp = dict()
        # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
        for column, value in rowproxy.items():
            # build up the dictionary
            temp = {**temp, **{column: value}}
        result_list.append(temp)

    return result_list


def no_result_sql(query):
    """

    :param query:
    """
    app = WedeliverCorePlus.get_app()
    db = app.extensions['sqlalchemy'].db
    app.logger.debug(query)
    db.engine.execute(text(query))
