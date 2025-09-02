"""  RulesSearchBuilder """

import json
import pandas as pd
from typing import Any
from opengate_data.searching.search import SearchBuilder
from opengate_data.utils.utils import send_request, handle_error_response, handle_exception, set_method_call, validate_type


class RulesSearchBuilder(SearchBuilder):
    """ Rules Search Builder """

    def __init__(self, opengate_client):
        super().__init__()
        self.client = opengate_client
        if self.client.url is None:
            self.base_url = 'https://rules:8448'
        else:
            self.base_url = f'{self.client.url}/north'
        self.headers = self.client.headers
        self.url: str | None = None
        self.body_data: dict = {}
        self.method_calls: list = []
        self.format_data: str = 'dict'

    @set_method_call
    def with_format(self, format_data: str) -> 'SearchBuilderBase':
        """
        Formats the flat entities data based on the specified format ('dict', or 'pandas').

        Args:
            format_data (str): The format to use for the data.

        Returns:
            EntitiesSearchBuilder: Returns itself to allow for method chaining.

        Example:
            ~~~python
                builder.with_format("dict")
                builder.with_format("pandas")
            ~~~
        """
        validate_type(format_data, str, "Format data")
        self.format_data = format_data
        return self

    @set_method_call
    def build(self) -> 'RulesSearchBuilder':
        """
        Finalizes the construction of the datapoints search configuration.

        This method prepares the builder to execute the collection by ensuring all necessary configurations are set and validates the overall integrity of the build. It should be called before executing the collection to ensure that the configuration is complete and valid.

        Returns:
            DataPointsSearchBuilder: Returns itself to allow for method chaining.

        Raises:
            ValueError: If required configurations are missing or if incompatible methods are used together.

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
        Executes the datapoints search immediately after building the configuration.

        This method is a shortcut that combines building and executing in a single step.

        Returns:
            dict: A dictionary containing the execution response which includes the status code and potentially other metadata about the execution.

        Raises:
            ValueError: If `build` has already been called on this builder instance.

        Example:
            ~~~python
                new_rules_search_builder.with_format("csv").with_organization_name(organization).build_execute()
                new_rules_search_builder.with_filter(filter).with_organization_name(organization).with_format("pandas").build_execute()
                new_entities_search_builder.with_filter(filter).with_organization_name(organization).with_format("dict").build_execute()
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
        Executes the rule search based on the built configuration.

        Returns:
            dict: The response data.

        Raises:
            Exception: If the build() method was not called before execute().

        Example:
            ~~~python
                new_rules_search_builder.with_filter(filter).with_organization_name(organization).with_format("dict").build_execute()
                new_rules_search_builder.with_filter(filter).with_organization_name(organization).with_format("pandas").build_execute()
            ~~~
        """
        if 'build' in self.method_calls:
            if self.method_calls[-2] != 'build':
                raise Exception("The build() function must be the last method invoked before execute.")

        if 'build' not in self.method_calls and 'build_execute' not in self.method_calls:
            raise Exception(
                "You need to use a build() or build_execute() function the last method invoked before execute.")

        url = f'{self.base_url}/v80/rules/search'
        return self._rules_dict_request(self.client.headers, url, self.body_data)

    def _rules_dict_request(self, headers: dict, url: str, body_data: dict) -> Any:
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

                if not data.get('rules'):
                    break

                all_results.extend(data['rules'])

                if has_limit:
                    break

                start += 1

            except Exception as e:
                return handle_exception(e)

        if self.format_data == 'dict':
            if self.format_data == 'dict':
                return json.dumps({'rules': all_results})

        if self.format_data == 'pandas':
            return pd.DataFrame(all_results)

        raise ValueError(f"Unsupported format: {self.format_data}")

    def _validate_builds(self):
        if self.format_data is not None and all(
                keyword not in self.format_data for keyword in ["pandas", "dict"]):
            raise ValueError(
                'Invalid value for the "with_format" method. Available parameters are only "dict" and "pandas"')