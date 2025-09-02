import json
from urllib.parse import urlencode

import pandas as pd
from flatten_dict import flatten

from opengate_data.utils.utils import send_request, handle_error_response, handle_exception, set_method_call, \
    validate_type


class SearchBuilderBase:
    """ Search Base Builder """

    def __init__(self):
        self.utc: bool = False
        self.flatten: bool = False
        self.utc: bool = False
        self.summary: bool = False
        self.default_sorted: bool = False
        self.case_sensitive: bool = False
        self.method_calls: list = []
        self.format_data_headers: str = 'application/json'
        self.format_data: str = 'dict'
        self.transpose: bool = False
        self.mapping: dict | None = None

    @set_method_call
    def with_format(self, format_data: str) -> 'SearchBuilderBase':
        """
        Formats the flat entities data based on the specified format ('csv', 'dict', or 'pandas').

        Args:
            format_data (str): The format to use for the data.

        Example:
            builder.with_format('dict')
            builder.with_format('csv')
            builder.with_format('pandas')

        Returns:
            SearchBuilderBase: Returns itself to allow for method chaining.
        """
        validate_type(format_data, str, "Format data")
        self.format_data = format_data
        if self.format_data == 'csv':
            self.format_data_headers = 'text/plain'
        return self

    def with_flattened(self) -> 'SearchBuilderBase':
        """
        Flatten the data

        Returns:
            SearchBuilderBase: Returns itself to allow for method chaining.
        """
        self.flatten = True
        return self

    def with_utc(self) -> 'SearchBuilderBase':
        """
        Set UTC flag

        Returns:
            SearchBuilderBase: Returns itself to allow for method chaining.
        """
        self.utc = True
        return self

    def with_summary(self) -> 'SearchBuilderBase':
        """
        Set summary flag

        Returns:
            SearchBuilderBase: Returns itself to allow for method chaining.
        """
        self.summary = True
        return self

    def with_default_sorted(self) -> 'SearchBuilderBase':
        """
        Set default sorted flag

        Returns:
            SearchBuilderBase: Returns itself to allow for method chaining.
        """
        self.default_sorted = True
        return self

    def with_case_sensitive(self) -> 'SearchBuilderBase':
        """
        Set case-sensitive flag

        Returns:
            SearchBuilder: Returns itself to allow for method chaining.
        """
        self.case_sensitive = True
        return self

    def _search_request(self, type_search: str, headers: dict, body_data: dict):

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

        url = f'{base_url}/v80/search/{type_search}?{urlencode(query_params)}'
        headers['Accept'] = self.format_data_headers
        if self.format_data == 'csv':
            return self._csv_request(headers, url, body_data)

        return self._dict_pandas_request(headers, url, body_data, type_search)

    @staticmethod
    def _csv_request(headers: dict, url: str, body_data: dict):
        try:
            response = send_request(method='post', headers=headers, url=url, json_payload=body_data)

            if response.status_code != 200:
                return handle_error_response(response)

            return response.text

        except Exception as e:
            return handle_exception(e)

    def _dict_pandas_request(self, headers: dict, url: str, body_data: dict, type_search: str):
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

                if not data.get(type_search):
                    break

                all_results.extend(data[type_search])

                if has_limit:
                    break

                start += 1

            except Exception as e:
                return handle_exception(e)

        return self._format_results(all_results, type_search)

    def _format_results(self, all_results, type_search):
        if self.format_data == 'dict':
            return json.dumps({type_search: all_results})

        if self.format_data == 'pandas':
            entities_flattened = [flatten(entity, reducer='underscore', enumerate_types=(list,)) for entity in
                                  all_results]
            return pd.DataFrame(entities_flattened)

        raise ValueError(f"Unsupported format: {self.format_data}")
