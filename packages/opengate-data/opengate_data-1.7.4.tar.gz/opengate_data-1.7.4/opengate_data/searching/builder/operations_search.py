"""  OperationsBuilder """

import requests
import json
import pandas as pd
from io import StringIO
from typing import Any
from flatten_dict import flatten
from opengate_data.searching.search import SearchBuilder
from opengate_data.utils.utils import send_request, handle_error_response, handle_exception, set_method_call, \
    validate_type
from opengate_data.searching.search_base import SearchBuilderBase
from urllib.parse import urlencode


class OperationsSearchBuilder(SearchBuilderBase, SearchBuilder):
    """ Builder Operations Search """

    def __init__(self, opengate_client):
        super().__init__()
        self.client = opengate_client
        self.headers = self.client.headers
        self.url: str | None = None
        self.method: str | None = None
        self.body_data: dict = {}
        self.method_calls: list = []

    @set_method_call
    def build(self):
        """
        Finalizes the construction of the operations search configuration.

        This method prepares the builder to execute the collection by ensuring all necessary configurations are set and validates the overall integrity of the build. It should be called before executing the collection to ensure that the configuration is complete and valid.

        The build process involves checking that mandatory fields such as the device identifier are set. It also ensures that method calls that are incompatible with each other (like `build` and `build_execute`) are not both used.

        Example:
            builder.build()

        Returns:
            OperationsSearchBuilder: Returns itself to allow for method chaining, enabling further actions like `execute`.

        Raises:
            ValueError: If required configurations are missing or if incompatible methods are used together.

        Note:
            This method should be used as a final step before `execute` to prepare the operations search configuration. It does not modify the state but ensures that the builder's state is ready for execution.

        Example:
            ~~~python
                builder.build()
            ~~~
        """
        self._validate_builds()

        if 'build_execute' in self.method_calls:
            raise Exception("You cannot use build() together with build_execute()")

        return self

    @set_method_call
    def build_execute(self):
        """
        Executes the operation search immediately after building the configuration.

        This method is a shortcut that combines building and executing in a single step.

        Returns:
            dict: A dictionary containing the execution response which includes the status code and potentially other metadata about the execution.

        Raises:
            ValueError: If `build` has already been called on this builder instance.

        Example:
            ~~~python
                new_operations_search_builder.with_format("csv").with_organization_name(organization).build_execute()
                new_operations_search_builder.with_filter(filter).with_organization_name(organization).with_format("pandas").build_execute()
                new_operations_search_builder.with_filter(filter).with_organization_name(organization).with_format("dict").build_execute()
            ~~~
        """
        if 'build' in self.method_calls:
            raise ValueError("You cannot use build_execute() together with build()")

        if 'execute' in self.method_calls:
            raise ValueError("You cannot use build_execute() together with execute()")

        self._validate_builds()
        return self.execute()

    @set_method_call
    def execute(self):
        """
        Executes the operation search based on the built configuration.

        Returns:
            dict, csv or dataframe: The response data in the specified format.

        Raises:
            Exception: If the build() method was not called before execute().

        Example:
            ~~~python
                new_operations_search_builder.with_format("csv").with_organization_name(organization).build().execute()
                new_operations_search_builder.with_filter(filter).with_organization_name(organization).with_format("pandas").build().execute()
                new_operations_search_builder.with_filter(filter).with_organization_name(organization).with_format("dict").build().execute()
            ~~~
        """
        if 'build' in self.method_calls:
            if self.method_calls[-2] != 'build':
                raise Exception("The build() function must be the last method invoked before execute.")

        if 'build' not in self.method_calls and 'build_execute' not in self.method_calls:
            raise Exception(
                "You need to use a build() or build_execute() function the last method invoked before execute.")

        query_params = {
            'flattened': self.flatten,
            'utc': self.utc,
            'summary': self.summary,
            'defaultSorted': self.default_sorted,
            'caseSensitive': self.case_sensitive
        }

        if self.client.url is None:
            url = f'https://operations:8444/v80/search/entities/operations/history?{urlencode(query_params)}'
        else:
            url = f'{self.client.url}/north/v80/search/entities/operations/history?{urlencode(query_params)}'

        if self.format_data == 'csv':
            headers = dict(self.client.headers)
            headers['Accept'] = self.format_data_headers
            return self._csv_request(headers, url, self.body_data)
        return self._dict_pandas_request(self.client.headers, url, self.body_data, 'operations')

    def operations__csv_request(self, url: str) -> dict[str, Any] | str | Any:
        try:
            response = send_request(method='post', headers=self.client.headers, url=url, json_payload=self.body_data)
            if response.status_code != 200:
                return handle_error_response(response)

            data_str = StringIO(response.content.decode('utf-8'))
            data = pd.read_csv(data_str, sep=';')

            return data.to_csv(index=False)

        except Exception as e:
            return handle_exception(e)

    def _validate_builds(self):
        if self.format_data is not None and all(
                keyword not in self.format_data for keyword in ["csv", "pandas", "dict"]):
            raise ValueError(
                'Invalid value for the "with_format" method. Available parameters are only "dict", "csv", and "pandas".')

        if 'with_limit' in self.method_calls and self.format_data == 'csv':
            raise Exception("Limit is not allowed with csv format")

        if 'with_select' not in self.method_calls and self.format_data == 'csv':
            raise Exception("You need to use with_select() to apply a format in CSV")

        return self
