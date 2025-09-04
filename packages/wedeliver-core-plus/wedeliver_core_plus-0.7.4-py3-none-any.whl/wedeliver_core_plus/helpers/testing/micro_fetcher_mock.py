from unittest.mock import MagicMock
from enum import Enum

# Placeholder exception classes
class AppMicroFetcherError(Exception):
    pass


class AppFetchServiceDataError(Exception):
    pass


# Utility functions for getting and setting values in nested objects
def get_obj_value(obj, key):
    keys = key.split('.')
    for k in keys:
        if isinstance(obj, dict):
            obj = obj.get(k)
        else:
            obj = getattr(obj, k, None)
        if obj is None:
            return None
    return obj


def get_obj_path_value(obj, path, default=None):
    """Fetches value at the specified path, handling mixed object and dict structures."""
    keys = path.split(".") if isinstance(path, str) else path

    current = obj
    for key in keys:
        current = get_obj_value(current, key)
        if current is None:  # Stop if any key along the path doesn't exist
            return default
    return current


def set_obj_value(obj, key, value, append_if_exists=False):
    keys = key.split('.')
    for k in keys[:-1]:
        if isinstance(obj, dict):
            obj = obj.setdefault(k, {})
        else:
            if not hasattr(obj, k):
                setattr(obj, k, {})
            obj = getattr(obj, k)
    last_key = keys[-1]

    if isinstance(obj, dict):
        if append_if_exists and last_key in obj:
            if not isinstance(obj[last_key], list):
                obj[last_key] = [obj[last_key]]
            obj[last_key].append(value)
        else:
            obj[last_key] = value
    else:
        if append_if_exists and hasattr(obj, last_key):
            existing_value = getattr(obj, last_key)
            if not isinstance(existing_value, list):
                existing_value = [existing_value]
            existing_value.append(value)
            setattr(obj, last_key, existing_value)
        else:
            setattr(obj, last_key, value)


class QueryTypes(Enum):
    SIMPLE_TABLE = 'SIMPLE_TABLE'
    FUNCTION = 'FUNCTION'
    SEARCH = 'SEARCH'
    ADVANCED_TABLE = 'ADVANCED_TABLE'
    POPULATE_TABLE = 'POPULATE_TABLE'


class LookUpType(Enum):
    DYNAMIC = "dynamic"
    STATIC = "static"


class FilterOperatorsType(Enum):
    AND = "AND"
    OR = "OR"


class MockMicroFetcher:
    def __init__(self, data_mapping=None):
        self.data_mapping = data_mapping or {}
        self.instances = []

    def __call__(self, service_name):
        instance = MockMicroFetcherInstance(service_name, self.data_mapping)
        self.instances.append(instance)
        return instance


class MockMicroFetcherInstance:
    def __init__(self, service_name, data_mapping):
        self.service_name = service_name
        self.data_mapping = data_mapping or {}
        self.app = MagicMock()
        self.base_data = None
        self.query_type = None
        self.output_key = None
        self.fields = []
        self.table_name = None
        self.column_name = None
        self.compair_operator = None
        self.column_values = None
        self.lookup_key = None
        self.filters_statements = None
        self.module_name = None
        self.function_params = {}
        self.search_list = None
        self.configs = None
        self.global_configs_data = {}
        self.search_configs = {}
        self.function_params = {}
        self.search_configs = {}
        self.search_list = None
        self.populate_lookup_map = None

    def join(self, base_data, output_key=None):
        self.base_data = base_data
        self.query_type = QueryTypes.SIMPLE_TABLE.value
        if output_key:
            output_key = output_key.split('as ')[1]
        self.output_key = "{}".format(self.service_name.split('_')[0].lower()) if not output_key else output_key
        return self

    def on(self, *args):
        join_on_statement = self._format_filter_arg(*args)
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

    def select(self, *args):
        self.fields = list(args)
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
            data = self.base_data
            if isinstance(data, list):
                for row in data:
                    self.column_values.add(get_obj_value(row, self.lookup_key))
            else:
                self.column_values.add(get_obj_value(data, self.lookup_key))
        self.column_values = list(filter(None, self.column_values))
        if len(self.column_values) == 1:
            self.column_values = self.column_values[0]
        if len(against) != 2:
            self.column_name = against[0]
        else:
            self.table_name = against[0]
            self.column_name = against[1]
            self.fields.append(self.column_name)
        return self

    def populate(self, base_data, input_key, *args):
        self.query_type = QueryTypes.POPULATE_TABLE.value
        self.base_data = base_data
        against = input_key.split('from ')[1].split('.')
        if len(against) != 2:
            self.column_name = against[0]
        else:
            self.table_name = against[0]
            self.column_name = against[1]
        return self

    def map(self, *args):
        if self.query_type == QueryTypes.POPULATE_TABLE.value:
            column_values = set()
            for arg in args:
                column_values.update(self._format_populate_lookup_arg(arg))

            self.column_values = list(column_values)
            self.compair_operator = 'IN' if isinstance(self.column_values, list) else "="
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

    def global_configs(self, **keywords):
        self.global_configs_data = keywords
        return self

    def feed_list(self, base_data, output_key=None):
        self.join(base_data, output_key)
        self.query_type = QueryTypes.SEARCH.value
        return self

    def search_config(self, configs):
        self.search_configs = configs
        self._prepare_search_list()
        return self

    def _prepare_search_list(self):
        output = dict()
        for index, item in enumerate(self.base_data):
            for search_column in self.search_configs.get("search_priority", []):
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

    def _call_api(self):
        # Use data_mapping to get data to merge
        # Instead of making network calls, we simulate data using data_mapping
        if self.query_type == QueryTypes.SIMPLE_TABLE.value:
            # Simulate data fetching
            # We can use data_mapping to get the data
            key = (self.service_name, self.output_key)
            data_to_merge = self.data_mapping.get(key, [])

            result = data_to_merge  # self.data_mapping.get(self.service_name, [])
        elif self.query_type == QueryTypes.ADVANCED_TABLE.value:
            key = (self.service_name, self.output_key)
            data_to_merge = self.data_mapping.get(key, [])
            result = data_to_merge
        elif self.query_type == QueryTypes.POPULATE_TABLE.value:
            key = (self.service_name, f"{self.table_name}.{self.column_name}")
            data_to_merge = self.data_mapping.get(key, [])
            result = data_to_merge
        elif self.query_type == QueryTypes.FUNCTION.value:
            key = (self.service_name, self.module_name)
            data_to_merge = self.data_mapping.get(key, [])
            result = data_to_merge
        elif self.query_type == QueryTypes.SEARCH.value:
            # Simulate search
            key = (self.service_name, self.output_key)
            data_to_merge = self.data_mapping.get(key, {})

            if data_to_merge:
                if isinstance(data_to_merge, list):
                    data_to_merge = data_to_merge[0]

                for sl in self.search_list:
                    for inp in sl.get('inputs'):
                        inp.update(dict(matched_id=data_to_merge.get('id')))
                        inp.update(data_to_merge)
            result = self.search_list
        else:
            result = []
        if self.base_data is not None:
            return self._map_base(result)
        return result

    def _map_base(self, result):
        if self.query_type == QueryTypes.SEARCH.value:
            # Map search result with the original object.
            for item in result:
                for _input in item.get('inputs', []):
                    for _index in _input.get('indexes', []):
                        self.base_data[_index][self.output_key] = _input.get('matched_id')
                        append_extra = self.search_configs.get('append_extra') if isinstance(self.search_configs,
                                                                                             dict) else []
                        for _ap_col in append_extra:
                            if _input.get('matched_id'):
                                self.base_data[_index][_ap_col] = _input.get(_ap_col)
                            else:
                                self.base_data[_index][_ap_col] = self.base_data[_index].get(_ap_col)
            validation_result = []
            # for _val in result.get("validation", []):
            #     for _ind in _val.get("indexes", []):
            #         _val.pop("indexes", None)
            #         validation_result.append(dict(
            #             index=_ind,
            #             **_val
            #         ))
            return validation_result
        if self.query_type == QueryTypes.POPULATE_TABLE.value:
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

            self.base_data = _base_data
        else:
            if isinstance(self.base_data, dict):
                for rd in result:
                    if self.base_data.get(self.lookup_key) == rd.get(self.column_name):
                        self.base_data[self.output_key] = rd
            else:
                data = self.base_data
                append_if_exists = self.configs.get("append_if_exists", False) if isinstance(self.configs,
                                                                                             dict) else False
                if isinstance(data, list):
                    for row in data:
                        for rd in result:
                            if get_obj_path_value(row, self.lookup_key) == rd.get(self.column_name):
                                set_obj_value(row, self.output_key, rd, append_if_exists)
                else:
                    for rd in result:
                        if get_obj_path_value(data, self.lookup_key) == rd.get(self.column_name):
                            set_obj_value(data, self.output_key, rd, append_if_exists)
            return self.base_data

    def _format_filter_statement(self, *args):
        single_mode = False
        multiple_mode = False
        for entry in args:
            if isinstance(entry, tuple):
                multiple_mode = True
            elif isinstance(entry, dict):
                if "operator" in entry:
                    multiple_mode = True
                else:
                    single_mode = True
            else:
                single_mode = True

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
        against = filter_args[0].split('.')
        if len(against) != 2:
            table_name = None
            column_name = against[0]
        else:
            table_name = against[0]
            column_name = against[1]
        lookup_arg = filter_args[2]
        if isinstance(filter_args[2], dict):
            lookup_type = lookup_arg.get("type")
            lookup_value = lookup_arg.get("value")
        else:
            lookup_type = LookUpType.DYNAMIC.value
            lookup_value = lookup_arg

        compair_operator = filter_args[1]
        compair_operator = compair_operator.upper()

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
                column_values = lookup_value

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

    def _append_field(self, *fields):
        if not self.fields:
            self.fields = []
        self.fields.append(*fields)

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
        (lookup_value, output_key) = lookup_arg
        output_key = output_key.split("as ")[1]
        self._append_populate_lookup(lookup_value, output_key)
        column_values = self._get_column_values(lookup_value)
        return column_values

    def _append_populate_lookup(self, lookup_key, output_key):
        if not self.populate_lookup_map:
            self.populate_lookup_map = dict()
        self.populate_lookup_map[lookup_key] = output_key