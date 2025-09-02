import requests
import json
import pandas as pd
from io import StringIO
from typing import Any
from flatten_dict import flatten
from opengate_data.searching.search import SearchBuilder
from opengate_data.utils.utils import send_request, handle_error_response, handle_exception, set_method_call, \
    validate_type, validate_build_method_calls_execute
from opengate_data.searching.search_base import SearchBuilderBase
from urllib.parse import urlencode
from jsonpath_ng import parse


class DataPointsSearchBuilder(SearchBuilderBase, SearchBuilder):
    """ Datapoints Search Builder """

    def __init__(self, opengate_client):
        super().__init__()
        self.client = opengate_client
        self.headers = self.client.headers
        self.transpose: bool = False
        self.mapping: dict[str, dict[str, str]] | None = None
        self.url: str | None = None
        self.body_data: dict[str, Any] = {}
        self.method_calls: list = []

    @set_method_call
    def with_transpose(self) -> 'DataPointsSearchBuilder':
        """
        Enables transposing the data in the result.

        This function allows the data returned by the search to be transposed, meaning that rows and columns are swapped. This can be useful for certain data analyses where it is preferred to have datastreams as columns and entities as rows.

        Note:
            This function can only be used with the 'pandas' format.

        Returns:
            DataPointsSearchBuilder: Returns the builder instance to allow for method chaining.

        Example:
            ~~~python
                builder.with_transpose()
            ~~~
        """
        self.transpose = True
        return self

    @set_method_call
    def with_mapped_transpose(self, mapping: dict[str, dict[str, str]]) -> 'DataPointsSearchBuilder':
        """
        Enables transposing the data with a specific mapping.

        This function allows the data returned by the search
        to be transposed and mapped according to a provided mapping dictionary.
        The mapping specifies how complex data should be transformed into flat columns.

        Args:
            mapping (dict[str, dict[str, str]]):
            A dictionary that defines the mapping of complex data to flat columns.
            The main key is the column name, and the value is another dictionary that defines the mapping of substructures.

        Note:
            This function can only be used with the 'pandas' format.

        Returns:
            DataPointsSearchBuilder: Returns the builder instance to allow for method chaining.

        Example:
            ~~~python
                complexData = {
                    'device.communicationModules[].subscription.address': {
                        'type': 'type',
                        'IP': 'value'
                    }
                }
                builder.with_mapped_transpose(complexData)
            ~~~
        """
        validate_type(mapping, dict, "Mapping")
        self.mapping = mapping
        return self

    @set_method_call
    def build(self):
        self._validate_builds()
        if 'build_execute' in self.method_calls:
            raise Exception("You cannot use build() together with build_execute()")
        return self

    @set_method_call
    def build_execute(self):
        if 'build' in self.method_calls:
            raise ValueError("You cannot use build_execute() together with build()")
        if 'execute' in self.method_calls:
            raise ValueError("You cannot use build_execute() together with execute()")
        self._validate_builds()
        return self.execute()

    @set_method_call
    def execute(self):
        """
        Execute the configured operation and return the response.

        This method executes the operation that has been configured using the builder pattern.
        It ensures that the `build` method has been called and that it is the last method invoked before `execute`.
        Depending on the configured method (e.g., create, find, update, delete),
        it calls the appropriate internal execution method.

        Returns:
            requests.Response: The response object from the executed request.

        Raises:
            Exception:
            If the `build` method has not been called or if it is not the last method invoked before `execute`.
            ValueError: If the configured method is unsupported.

        Example:
            ~~~python
                builder.execute()
            ~~~
        """
        validate_build_method_calls_execute(self.method_calls)

        query_params = {
            'flattened': self.flatten,
            'utc': self.utc,
            'summary': self.summary,
            'defaultSorted': self.default_sorted,
            'caseSensitive': self.case_sensitive
        }
        if self.client.url is None:
            base_url = 'https://frontend:8443'
        else:
            base_url = f'{self.client.url}/north'
        url = f'{base_url}/v80/search/datapoints?{urlencode(query_params)}'
        if self.format_data == 'csv':
            return self._search_request('datapoints', self.headers, self.body_data)

        if self.format_data == 'dict':
            return self._datapoints_dict_pandas_request(self.client.headers, url, self.body_data)

        if self.format_data == 'pandas':
            if "with_transpose" in self.method_calls or 'with_mapped_transpose' in self.method_calls:
                self.client.headers.update({
                    'Content-type': 'application/json',
                    'Accept': 'text/plain',
                })

                return self._transpose_mapping(self.client.headers, url, self.body_data)
            else:
                return self._datapoints_dict_pandas_request(self.client.headers, url, self.body_data)

        raise ValueError(f"Unsupported format: {self.format_data}")

    def _datapoints_dict_pandas_request(self, headers: dict, url: str, body_data: dict) -> Any:
        all_results = []
        limit = body_data.get("limit", {})
        start = limit.get("start", 1)
        size = limit.get("size", 1000)
        has_limit = "limit" in body_data

        while True:
            body_data.setdefault("limit", {}).update({"start": start, "size": size})
            try:
                response = send_request(method='post', headers=headers, url=url, json_payload=body_data)

                if response.status_code == 204:
                    if all_results:
                        break
                    return {'status_code': response.status_code}

                if response.status_code != 200 and response.status_code != 204:
                    return handle_error_response(response)

                data = response.json()

                if not data.get('datapoints'):
                    break

                all_results.extend(data['datapoints'])

                if has_limit:
                    break

                start += 1

            except Exception as e:
                return handle_exception(e)

        if self.format_data in 'dict':
            if self.format_data == 'dict':
                return json.dumps({'datapoints': all_results})

        if self.format_data == 'pandas':
            datapoints_flattened = [flatten(datapoint, reducer='underscore', enumerate_types=(list,)) for datapoint in
                                    all_results]
            return pd.DataFrame(datapoints_flattened)

        raise ValueError(f"Unsupported format: {self.format_data}")

    def _transpose_mapping(self, headers: dict, url: str, body_data: dict):
        response = send_request(method='post', headers=headers, url=url, json_payload=body_data)
        data_str = StringIO(response.content.decode('utf-8'))
        data = pd.read_csv(data_str, sep=';')

        if self.transpose:
            data = self._transpose_data(data)
        if self.mapping:
            data = self._transpose_data(data)
            for column, sub_complexdata in self.mapping.items():
                if column in data.columns:
                    json_path_expressions = {key: parse(value) for key, value in sub_complexdata.items()}

                    for row_index, cell_value in data[column].items():
                        if not pd.isna(cell_value):
                            for key, json_path_expr in json_path_expressions.items():
                                matches = json_path_expr.find(json.loads(cell_value))
                                if matches:
                                    new_column = f'{key}'
                                    if new_column not in data.columns:
                                        data[new_column] = None
                                    data.at[row_index, new_column] = matches[0].value

        data.columns = [col.replace('.', '__') for col in data.columns]

        return data

    @staticmethod
    def _transpose_data(data: pd.DataFrame) -> pd.DataFrame:
        data = data.pivot_table(index=['at', 'entity'], columns='datastream', fill_value=None, aggfunc='first')
        data = data.sort_values(by='at')
        data = data['value']
        data = data.reset_index()
        data = data.infer_objects(copy=False)
        return data

    def _validate_builds(self):
        if self.format_data is not None and all(
                keyword not in self.format_data for keyword in ["csv", "pandas", "dict"]):
            raise Exception(
                'Invalid value for the "with_format" method. Available parameters are only "dict", "csv", and "pandas".')
        if self.format_data != "pandas" and (
                self.method_calls.count('with_transpose') > 0 or self.method_calls.count('with_mapped_transpose') > 0):
            raise Exception(
                "You cannot use 'with_transpose()' or 'with_mapped_transpose()' without 'with_format('pandas')'.")
        if self.method_calls.count('with_transpose') > 0 and self.method_calls.count('with_mapped_transpose') > 0:
            raise Exception("You cannot use with_transpose() together with with_mapped_transpose()")
        if self.method_calls.count('with_format') > 1:
            raise Exception("You cannot use more than one with_format() method")
        if 'with_select' not in self.method_calls and self.format_data == 'csv':
            raise Exception("You need to use with_select() to apply a format in CSV")
