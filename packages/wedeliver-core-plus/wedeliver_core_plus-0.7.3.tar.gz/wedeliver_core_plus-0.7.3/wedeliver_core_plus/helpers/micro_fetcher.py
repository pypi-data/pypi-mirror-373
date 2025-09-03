import flask_sqlalchemy
from flask import g
# from requests.adapters import HTTPAdapter
# from urllib3.util.retry import Retry

from wedeliver_core_plus import WedeliverCorePlus
from wedeliver_core_plus.helpers.exceptions import AppMicroFetcherError, AppFetchServiceDataError
import requests
import json

from wedeliver_core_plus.helpers.get_obj_value import (
    get_obj_value,
    get_obj_path_value,
    set_obj_value,
)

from wedeliver_core_plus.helpers.service_config import ServiceConfig

from wedeliver_core_plus.helpers.enums import (
    QueryTypes,
    LookUpType,
    FilterOperatorsType,
    DYNAMIC_LOOKUP_OPERATORS,
    STATIC_LOOKUP_OPERATORS,
)


class MicroFetcher(object):
    base_data = None
    app = None
    service_name = None
    service_url = None
    fields = None
    table_name = None
    column_name = None
    compair_operator = None
    column_values = None
    output_key = None
    lookup_key = None
    filters_statements = None
    module_name = None
    function_params = None
    query_type = None
    search_list = None
    configs = None
    populate_lookup_map = None

    def __init__(self, service):
        self.app = WedeliverCorePlus.get_app()

        if isinstance(service, ServiceConfig):
            service = service.initialize()
            service_name = service.name
            service_url = service.url
        else:
            service_name = service
            service_url = None

        env_service_url = self.app.config.get(service_name)

        self.service_url = env_service_url if env_service_url else service_url

        self.service_name = service_name
        if not self.service_url:
            raise AppMicroFetcherError(f'Service {service_name} not defined on Env or in ServiceConfig')

    def join(self, base_data, output_key=None):
        self.base_data = base_data
        self.query_type = QueryTypes.SIMPLE_TABLE.value
        if output_key:
            output_key = output_key.split('as ')[1]

        self.output_key = "{}".format(self.service_name.split('_')[0].lower()) if not output_key else output_key
        return self

    def on(self, *args):
        if self.query_type != QueryTypes.SIMPLE_TABLE.value:
            raise AppMicroFetcherError("Can only call the 'on' function right after calling 'join' function")

        if isinstance(args[0], tuple) or self.column_name:
            raise AppMicroFetcherError("Joining is only supported for one column")

        join_on_statement = self._format_filter_arg(*args)
        if join_on_statement.get("lookup_type") != LookUpType.DYNAMIC.value:
            raise AppMicroFetcherError("Look up value must be a dynamic value")

        self.query_type = QueryTypes.ADVANCED_TABLE.value
        if not self.compair_operator or self.lookup_key:
            self.column_name = join_on_statement.get("column_name")
            self.lookup_key = join_on_statement.get("lookup_value")
            self.compair_operator = join_on_statement.get("compair_operator")
            self.column_values = join_on_statement.get("column_values")
        return self

    def config(self, **configs):
        self.configs = configs
        return self

    def _prepare_search_list(self):
        output = dict()
        for index, item in enumerate(self.base_data):
            for search_column in self.search_configs.get("search_priority"):
                sanitize = None
                if isinstance(search_column, dict):
                    search_column_name = search_column.get('key')
                    operator = search_column.get('operator') or "IN"
                    sanitize = search_column.get('sanitize')
                else:
                    search_column_name = search_column
                    operator = 'IN'

                value = item.get(search_column_name)
                if sanitize and isinstance(sanitize, list):
                    for _san in sanitize:
                        value = _san(value)

                if value:
                    if not output.get(search_column_name):
                        output[search_column_name] = dict(
                            search_key=search_column_name,
                            operator=operator,
                            inputs=dict()
                        )
                    if not output[search_column_name]['inputs'].get(value):
                        output[search_column_name]['inputs'][value] = dict(
                            indexes=[index],
                            search_value=value
                        )
                    else:
                        output[search_column_name]['inputs'][value]["indexes"].append(index)
                    break

        output = list(output.values())
        for item in output:
            item['inputs'] = list(item['inputs'].values())

        self.search_list = output

    def search_config(self, configs):
        self.search_configs = configs
        self._prepare_search_list()
        return self

    def global_configs(self, **keywords):
        self.global_configs = keywords
        return self

    def feed_list(self, base_data, output_key=None):
        join_result = self.join(base_data, output_key)
        self.query_type = QueryTypes.SEARCH.value
        return join_result

    def select(self, *args):
        if not self.fields:
            self.fields = []
        self.fields.extend(args)
        return self

    def filter(self, *args):
        if self.query_type == QueryTypes.ADVANCED_TABLE.value:
            statement = self._format_filter_statement(*args)
            self._append_filters_statements(statement=statement)
            return self
        against = args[0].split('.')
        self.compair_operator = args[1]
        self.lookup_key = args[2]
        self.column_values = set()
        if isinstance(self.base_data, dict):
            self.column_values.add(get_obj_value(self.base_data, self.lookup_key))
        else:
            if isinstance(self.base_data, flask_sqlalchemy.Pagination):
                data = self.base_data.items
            else:
                data = self.base_data

            if isinstance(data, list):
                for row in data:
                    self.column_values.add(get_obj_value(row, self.lookup_key))
            else:
                self.column_values.add(get_obj_value(data, self.lookup_key))

        if not len(self.column_values):
            self.column_values = []
            return self
            # raise AppMicroFetcherError('Lookup key {} not found'.format(self.lookup_key))

        self.column_values = list(filter(None, self.column_values))
        self.column_values = self.column_values[0] if len(self.column_values) == 1 else self.column_values

        if self.compair_operator not in ('=', 'IN'):
            raise AppMicroFetcherError('Only == currently supported')

        self.compair_operator = 'IN' if isinstance(self.column_values, list) else self.compair_operator

        if len(against) != 2:
            self.column_name = against[0]
        else:
            self.table_name = against[0]
            self.column_name = against[1]

            self.fields.append(self.column_name)

        return self

    def populate(self, base_data, input_key, *args):
        if (self.query_type and
            self.query_type != QueryTypes.POPULATE_TABLE.value
        ):
            raise AppMicroFetcherError('Invalid populate call')

        self.query_type = QueryTypes.POPULATE_TABLE.value
        self.base_data = base_data

        if (not input_key or
            not isinstance(input_key, str) or
            not input_key.startswith("from ")
        ):
            raise AppMicroFetcherError('Invalid input from argument')

        against = input_key.split('from ')[1].split('.')
        if not against:
            raise AppMicroFetcherError('Invalid input from argument')
        if len(against) != 2:
            self.column_name = against[0]
        else:
            self.table_name = against[0]
            self.column_name = against[1]
        return self

    def map(self, *args):
        if self.query_type == QueryTypes.POPULATE_TABLE.value:
            if len(args) < 1:
                raise AppMicroFetcherError('Expected at least one population argument')
            column_values = set()
            for arg in args:
                column_values.update(self._format_populate_lookup_arg(arg))

            self.column_values = list(column_values)
            self.compair_operator = 'IN' if isinstance(self.column_values, list) else "="
        else:
            raise AppMicroFetcherError("Can not call 'map' with current microfetcher configuration")
        return self


    def fetch(self):
        if self.column_values or self.module_name or self.query_type == QueryTypes.SEARCH.value:
            return self._call_api()
        else:
            return self.base_data

    def execute(self):
        return self.fetch()

    def with_params(self, **kwargs):
        self.function_params = kwargs
        return self

    def from_function(self, module_name):
        self.query_type = QueryTypes.FUNCTION.value
        self.module_name = module_name
        return self

    def _call_api(self):

        from wedeliver_core_plus.helpers.auth import find_user_language

        url = "{}/fetch_relational_data".format(self.service_url)

        payload_dict = dict(
            __user_auth_data__=g.user if hasattr(g, 'user') else dict(
                language=find_user_language()
            ),
        )
        if self.query_type in [
            QueryTypes.SIMPLE_TABLE.value,
            QueryTypes.FUNCTION.value,
            QueryTypes.POPULATE_TABLE.value
        ]:
            payload_dict.update(
                dict(
                    fields=self.fields,
                    table_name=self.table_name,
                    column_name=self.column_name,
                    compair_operator=self.compair_operator,
                    column_values=self.column_values,
                )
            )

            if self.query_type == QueryTypes.FUNCTION.value:
                payload_dict.update(
                    functions=[
                        dict(
                            name=self.module_name,
                            fields=self.fields,
                            params=self.function_params if self.function_params else dict()
                        )
                    ]
                )

        elif self.query_type == QueryTypes.ADVANCED_TABLE.value:
            payload_dict.update(
                dict(
                    fields=self.fields,
                    table_name=self.table_name,
                    column_name=self.column_name,
                    compair_operator=self.compair_operator,
                    column_values=self.column_values,
                )
            )
            if self.filters_statements:
                payload_dict.update(dict(filters_statements=self.filters_statements))
        elif self.query_type == QueryTypes.SEARCH.value:
            payload_dict.update(dict(
                query_type=self.query_type,
                table_name=self.search_configs.get("table_name"),
                search_list=self.search_list,
                append_extra=self.search_configs.get("append_extra"),
                use_country_code=self._get_global_config(key="use_country_code", default_value=True),
            ))

        payload = json.dumps(payload_dict)
        headers = {
            'country_code': self._get_global_config(key="country_code", default_value="sa"),
            'Content-Type': 'application/json',
        }

        session = requests  # requests.Session()

        # retry = Retry(
        #     total=5,
        #     backoff_factor=1,
        #     status_forcelist=[429, 500, 502, 503, 504],
        # )
        # adapter = HTTPAdapter(max_retries=retry)
        # session.mount('http://', adapter)
        # session.mount('https://', adapter)

        def _raise_error(message, error):
            self.app.logger.error(self.service_name)
            self.app.logger.error(message)
            self.app.logger.error(payload)
            self.app.logger.error(str(conn_err))
            raise AppFetchServiceDataError(message)

        response = None  # Initialize the response variable

        try:
            # response = requests.request("POST", url, headers=headers, data=payload)
            response = session.post(url, headers=headers, data=payload)
            # response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            _raise_error('HTTP error occurred', http_err)
        except requests.exceptions.ConnectionError as conn_err:
            _raise_error('Connection error occurred', conn_err)
        except requests.exceptions.Timeout as timeout_err:
            _raise_error('Timeout error occurred', timeout_err)
        except requests.exceptions.RequestException as req_err:
            _raise_error('Request error occurred', req_err)
        except Exception as req_err:
            _raise_error('Exception occurred', req_err)

        if response is not None and response.status_code != 200:
            self.app.logger.error(self.service_name)
            self.app.logger.error(response.text)
            custom_text = None
            try:
                custom_text = json.loads(response.text).get('message')
            except json.decoder.JSONDecodeError:
                pass
            raise AppFetchServiceDataError(custom_text, response.status_code)

        result = response.json() if response else dict()

        if self.base_data is not None:
            return self._map_base(result)

        return result

    def _get_global_config(self, key, default_value):
        if hasattr(self, 'global_configs') and isinstance(self.global_configs, dict):
            if self.global_configs.get(key) is None:
                return default_value
            else:
                return self.global_configs.get(key)
        else:
            return default_value

    def _map_base(self, result):
        if self.query_type == QueryTypes.SEARCH.value:
            # map search result with the original object.
            _result = result.get("result")
            for item in _result:
                for _input in item.get('inputs'):
                    for _index in _input.get('indexes'):
                        self.base_data[_index][self.output_key] = _input.get('matched_id')
                        append_extra = self.search_configs.get('append_extra') if isinstance(self.search_configs,
                                                                                             dict) else []
                        for _ap_col in append_extra:
                            self.base_data[_index][_ap_col] = _input.get(_ap_col) if _input.get('matched_id') else \
                                self.base_data[_index].get(_ap_col)

            validation_result = []
            for _val in result.get("validation"):
                for _ind in _val.get("indexes"):
                    _val.pop("indexes", None)
                    validation_result.append(dict(
                        index=_ind,
                        **_val
                    ))
            return validation_result
        if self.query_type == QueryTypes.POPULATE_TABLE.value:
            _base_data = None
            if isinstance(self.base_data, flask_sqlalchemy.Pagination):
                _base_data = self.base_data.items
            else:
                _base_data = self.base_data

            # Formating data to a map, for easier access
            _result_map = dict()
            def _map_result_entry(entry):
                column_value = entry.get(self.column_name)
                _result_map[column_value] = entry

            if isinstance(result, list):
                for entry in result:
                    _map_result_entry(entry)
            else:
                _map_result_entry(result)

            # Append entries to base data
            append_if_exists = self.configs.get("append_if_exists", False) if isinstance(self.configs, dict) else False
            def _populate_base_data(_base):
                for lookup_key, output_key in self.populate_lookup_map.items():
                    lookup_value = get_obj_path_value(_base, lookup_key)
                    output_value = _result_map.get(lookup_value)
                    if output_value:
                        set_obj_value(_base, output_key, output_value, append_if_exists)

            if isinstance(_base_data, list):
                for row in _base_data:
                    _populate_base_data(_base=row)
            else:
                _populate_base_data(_base=_base_data)

            if isinstance(self.base_data, flask_sqlalchemy.Pagination):
                self.base_data.items = _base_data
            else:
                self.base_data = _base_data

        else:
            if isinstance(self.base_data, dict):
                if self.query_type in (QueryTypes.SIMPLE_TABLE.value, QueryTypes.ADVANCED_TABLE.value):
                    for rd in result:
                        if self.base_data.get(self.lookup_key) == rd.get(self.column_name):
                            try:
                                setattr(self.base_data, self.output_key, rd)
                            except AttributeError:
                                if self.base_data.get(self.output_key):
                                    if not isinstance(self.base_data[self.output_key], list):
                                        self.base_data[self.output_key] = [self.base_data[self.output_key]]

                                    self.base_data[self.output_key].append(
                                        rd
                                    )
                                else:
                                    self.base_data[self.output_key] = rd

                else:
                    for rd in result:
                        if self.base_data.get(self.lookup_key) == rd.get(self.column_name):
                            try:
                                setattr(self.base_data, self.output_key, rd)
                            except AttributeError:
                                self.base_data[self.output_key] = rd
            else:
                if isinstance(self.base_data, flask_sqlalchemy.Pagination):
                    data = self.base_data.items
                else:
                    data = self.base_data

                append_if_exists = self.configs.get("append_if_exists", False) if isinstance(self.configs,
                                                                                             dict) else False

                def _feed_base(_base, _data):
                    if isinstance(_data, list):
                        for _d in _data:
                            if str(get_obj_path_value(_base, self.lookup_key)) == str(_d.get(self.column_name)):
                                set_obj_value(_base, self.output_key, _d, append_if_exists)
                    else:
                        if str(get_obj_path_value(_base, self.lookup_key)) == _data.get(self.column_name):
                            set_obj_value(_base, self.output_key, _data, append_if_exists)

                if isinstance(data, list):
                    for row in data:
                        _feed_base(_base=row, _data=result)
                else:
                    _feed_base(_base=data, _data=result)

                if isinstance(self.base_data, flask_sqlalchemy.Pagination):
                    self.base_data.items = data
                else:
                    self.base_data = data

            return self.base_data

    def _append_field(self, *fields):
        if not self.fields:
            self.fields = []
        self.fields.append(*fields)

    def _format_filter_statement(self, *args):
        single_mode = False
        multiple_mode = False
        for entry in args:
            if isinstance(entry, tuple):
                multiple_mode = True
            elif isinstance(entry, dict):
                if "operator" in entry:
                    if not "entries" in entry:
                        raise AppMicroFetcherError("Invalid filter arguments for nested entries")
                    multiple_mode = True
                else:
                    single_mode = True
            else:
                single_mode = True
            if multiple_mode and single_mode:
                raise AppMicroFetcherError('Invalid filter arguments for multiple statements')

        statements = dict(operator=FilterOperatorsType.AND.value, entries=[], children=[])
        if multiple_mode:
            for entry in args:
                if isinstance(entry, tuple):
                    result = self._format_filter_arg(*entry)
                    statements["entries"].append(result)
                elif isinstance(entry, dict):
                    child_entries = entry.get("entries")
                    child_statements = self._format_filter_statement(*child_entries)
                    child_statements["operator"] = entry.get("operator")
                    statements["children"].append(child_statements)
        else:
            result = self._format_filter_arg(*args)
            statements["entries"].append(result)
        return statements

    def _format_filter_arg(self, *filter_args):
        if len(filter_args) != 3:
            raise AppMicroFetcherError(f'Received {"more" if len(filter_args) > 3 else "less"} filter arguments than expected')

        against = filter_args[0].split('.')
        if not against:
            raise AppMicroFetcherError('Invalid filter against argument')
        if len(against) != 2:
            table_name = None
            column_name = against[0]
        else:
            table_name = against[0]
            column_name = against[1]
        # This means your filter statements where not directly to the same table
        if self.table_name and table_name != self.table_name:
            raise AppMicroFetcherError('Only filtering on the same table is supported')

        # Static being same as given value
        # Dynamic being value found in the key with the given value
        # Note: Default is Dynamic to stay compatible with previous syntax
        lookup_arg = filter_args[2]
        if isinstance(filter_args[2], dict):
            lookup_type = lookup_arg.get("type")
            lookup_value = lookup_arg.get("value")
            if lookup_type not in (LookUpType.DYNAMIC.value, LookUpType.STATIC.value):
                raise AppMicroFetcherError(f'Invalid lookup type ${lookup_type}')
        else:
            lookup_type = LookUpType.DYNAMIC.value
            lookup_value = lookup_arg

        # if lookup value is a list or if lookup type is Dynamic the only allowed operator will be "=" or "in"
        # This is the only way to compare lists in relation databases
        compair_operator = filter_args[1]
        if not isinstance(compair_operator, str):
            raise AppMicroFetcherError(f'Compare operator must be str')
        compair_operator = compair_operator.upper()
        if (
            lookup_type == LookUpType.DYNAMIC.value
            or isinstance(lookup_value, list)
            or isinstance(lookup_value, tuple)
        ) and compair_operator not in DYNAMIC_LOOKUP_OPERATORS:
            raise AppMicroFetcherError(f'Only {DYNAMIC_LOOKUP_OPERATORS} are supported for given lookup')
        elif compair_operator not in STATIC_LOOKUP_OPERATORS:
            raise AppMicroFetcherError(f'Only {STATIC_LOOKUP_OPERATORS} are supported for given lookup')


        if lookup_type == LookUpType.DYNAMIC.value:
            column_values = self._get_column_values(lookup_value)
            column_values = column_values[0] if len(column_values) == 1 else column_values
            if isinstance(column_values, list):
                if compair_operator == "!=":
                    compair_operator = "NOT IN"
                else:
                    compair_operator = "IN"
        else:
            if compair_operator == "%LIKE":
                compair_operator = "LIKE"
                column_values = f"%{lookup_value}"
            elif compair_operator == "%LIKE%":
                compair_operator = "LIKE"
                column_values = f"%{lookup_value}%"
            elif compair_operator == "LIKE%":
                compair_operator = "LIKE"
                column_values = f"{lookup_value}%"
            else:
                column_values=lookup_value

        if table_name and column_name:
            self.table_name = table_name
            self._append_field(column_name)

        return dict(
            table_name=table_name,
            column_name=column_name,
            lookup_type=lookup_type,
            lookup_value=lookup_value,
            compair_operator=compair_operator,
            column_values=column_values,
        )

    def _get_column_values(self, lookup_value):
        column_values = set()
        if isinstance(self.base_data, flask_sqlalchemy.Pagination):
            data = self.base_data.items
        else:
            data = self.base_data

        if isinstance(data, list):
            for row in data:
                column_values.add(get_obj_path_value(row, lookup_value))
        else:
            column_values.add(get_obj_path_value(data, lookup_value))

        if not len(column_values):
            column_values = []

        column_values = list(filter(None, column_values))
        return column_values


    def _append_filters_statements(self, statement):
        if not self.filters_statements:
            self.filters_statements = statement
            return
        entries = statement.get("entries")
        if entries and "entries" in self.filters_statements:
            self.filters_statements["entries"].extend(entries)
        children = statement.get("children")
        if children and "children" in self.filters_statements:
            self.filters_statements["children"].extend(children)

    def _format_populate_lookup_arg(self, lookup_arg):
        if not isinstance(lookup_arg, tuple):
            raise AppMicroFetcherError("Invalid lookup argument")

        (lookup_value, output_key) = lookup_arg
        if not lookup_value or not isinstance(lookup_value, str):
            raise AppMicroFetcherError("Invalid lookup value")

        if not output_key or not isinstance(output_key, str) or not output_key.startswith("as "):
            raise AppMicroFetcherError("Invalid output column name")

        output_key = output_key.split("as ")[1]
        self._append_populate_lookup(lookup_value, output_key)

        column_values = self._get_column_values(lookup_value)
        return column_values


    def _append_populate_lookup(self, lookup_key, output_key):
        if not self.populate_lookup_map:
            self.populate_lookup_map = dict()
        self.populate_lookup_map[lookup_key] = output_key


def mf_static(value):
    return dict(type=LookUpType.STATIC.value, value=value)

def mf_dynamic(value):
    if not isinstance(value, str):
        raise AppMicroFetcherError("Invalid dynamic lookup path")
    return dict(type=LookUpType.DYNAMIC.value, value=value)

def mf_or(*args):
    return dict(operator=FilterOperatorsType.OR.value, entries=args)

def mf_and(*args):
    return dict(operator=FilterOperatorsType.AND.value, entries=args)