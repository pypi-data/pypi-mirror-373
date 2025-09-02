import csv
import json
import os
from typing import Any, Literal

import pandas as pd
from flatten_dict import unflatten

from opengate_data.utils.utils import validate_type, send_request, set_method_call


class ProvisionBulkBuilder:

    def __init__(self, opengate_client):
        self.client = opengate_client
        self.flatten: bool = False
        self.organization_name: str | None = None
        self.bulk_action: Literal['CREATE', 'UPDATE', 'PATCH', 'DELETE'] = 'CREATE'
        self.bulk_type: Literal['ENTITIES', 'TICKETS'] = 'ENTITIES'
        self.payload: dict = {"entities": []}
        self.method_calls: list = []
        self.builder: bool = False
        self.full: bool = False
        self.path: str | None = None
        self.file: dict | None = {}
        self.file_name: str | None = None
        self.file_content: str | None = None
        self.excel_file: str | None = None

    @set_method_call
    def with_organization_name(self, organization_name: str) -> 'ProvisionBulkBuilder':
        """
        Specify the organization name.

        Args:
            organization_name (str): The name of the organization name that we want to bulk data.

        Returns:
            ProvisionBulkBuilder: Returns itself to allow for method chaining.

        Example:
             ~~~python
                builder.with_organization_name('organization_name')
             ~~~
        """

        validate_type(organization_name, str, "Organization Name")
        self.organization_name = organization_name

        return self

    @set_method_call
    def with_bulk_action(self, bulk_action: str) -> 'ProvisionBulkBuilder':
        """
        Adds the bulk action to the constructor and validates the type.

        Args:
            bulk_action (str): The bulk action. You can choose between these actions:
            - CREATE (default)
            - UPDATE
            - PATCH
            - DELETE

        Returns:
            ProvisionBulkBuilder: Returns itself to allow for method chaining.

        Raises:
            ValueError: If the bulk action isn't one of the mentioned above.

        Example:
             ~~~python
                builder.with_bulk_action('bulk_action')
             ~~~
        """

        validate_type(bulk_action, str, "Bulk Action")
        if bulk_action not in {'CREATE', 'UPDATE', 'PATCH', 'DELETE'}:
            raise ValueError("Invalid bulk action. Only 'CREATE', 'UPDATE', 'PATCH', 'DELETE' are accepted.")
        self.bulk_action = bulk_action

        return self

    @set_method_call
    def with_bulk_type(self, bulk_type: str) -> 'ProvisionBulkBuilder':
        """
        Adds the bulk type to the constructor and validates the type.

        Args:
            bulk_type (str): The bulk type. You can choose between these types:
            - ENTITIES (default)
            - TICKETS

        Returns:
            ProvisionBulkBuilder: Returns itself to allow for method chaining.

        Raises:
            ValueError: If the bulk type isn't one of the mentioned above.

        Example:
             ~~~python
                builder.with_bulk_type('bulk_type')
             ~~~
        """

        validate_type(bulk_type, str, "Bulk Type")
        if bulk_type not in {'ENTITIES', 'TICKETS'}:
            raise ValueError("Invalid bulk type. Only 'ENTITIES','TICKETS' are accepted.")
        self.bulk_type = bulk_type

        return self

    @set_method_call
    def from_json(self, path: str) -> 'ProvisionBulkBuilder':
        """
        Loads data as a json file.

        Args:
            path (str): The path to the json file.

        Returns:
            ProvisionBulkBuilder: Returns itself to allow for method chaining.

        Raises:
            FileNotFoundError: If the path isn't correct or the file doesn't exist in the selected folder.

        Example:
             ~~~python
                builder.from_json('path_to_json.json')
             ~~~
        """

        validate_type(path, str, "Path")
        self.path = path
        self.file_name = self.path.split('/')[-1]
        try:
            with open(path, 'r', encoding='utf-8') as jsonfile:
                self.file_content = json.load(jsonfile)
        except FileNotFoundError as fnf_error:
            raise Exception(f'File not found error: {str(fnf_error)}')

        return self

    @set_method_call
    def from_csv(self, path: str) -> 'ProvisionBulkBuilder':
        """
        Loads data as a csv file.

        Args:
            path (str): The path to the csv file.

        Returns:
            ProvisionBulkBuilder: Returns itself to allow for method chaining.

        Raises:
            FileNotFoundError: If the path isn't correct or the file doesn't exist in the selected folder.

        Example:
             ~~~python
                builder.from_csv('path_to_csv.csv')
             ~~~
        """
        validate_type(path, str, "Path")
        self.path = path
        self.file_name = self.path.split('/')[-1]
        try:
            with open(path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile, delimiter=';')
                rows = list(reader)
            self.file_content = f"{';'.join(rows[0])}\n"
            for row in rows[1:]:
                self.file_content += f"{';'.join(row)}\n"
        except FileNotFoundError as fnf_error:
            raise Exception(f'File not found error: {str(fnf_error)}')

        return self

    @set_method_call
    def from_excel(self, path: str) -> 'ProvisionBulkBuilder':
        """
        Loads data as an Excel file (supports xls and xlsx).

        Args:
            path (str): The path to the Excel file.

        Returns:
            ProvisionBulkBuilder: Returns itself to allow for method chaining.

        Raises:
            FileNotFoundError: If the path isn't correct or the file doesn't exist in the selected folder.

        Example:
             ~~~python
                builder.from_excel('path_to_excel.xls')
             ~~~
        """
        validate_type(path, str, "Path")
        self.path = path
        self.file_name = self.path.split('/')[-1]
        absolute_path = os.path.abspath(path)
        try:
            self.excel_file = open(absolute_path, 'rb')
            self.file = {'file': (
                self.file_name, self.excel_file, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        except FileNotFoundError as fnf_error:
            raise Exception(f'File not found error: {str(fnf_error)}')

        return self

    @set_method_call
    def from_dataframe(self, df: pd.DataFrame) -> "ProvisionBulkBuilder":
        """
        Loads data as a pandas DataFrame.
        Columns must be the names of the datastreams separated with '_' or '.'.

        Args:
            df (pd.DataFrame): The DataFrame variable.

        Returns:
            ProvisionBulkBuilder: Returns itself to allow for method chaining.

        Example:
             ~~~python
                import pandas as pd
                data = {
                    'provision_administration_organization_current_value': ['base_organization','test_organization'],
                    'provision_device_location_current_value_position_type': ['Point','Other_Point'],
                    'provision_device_location_current_value_position_coordinates': [[-3.7028,40.41675],[-5.7028,47.41675]],
                    'provision_device_location_current_value_postal': ['28013','28050']
                    }
                df = pd.DataFrame(df)
                builder.from_dataframe(df)
             ~~~
        """

        validate_type(df, pd.DataFrame, "Dataframe")
        self.payload['entities'] = self._process_dataframe(df)

        return self

    @set_method_call
    def from_dict(self, dct: dict[str, Any]) -> "ProvisionBulkBuilder":
        """
        Loads data as a python dictionary (same structure as 'from_json').

        Args:
            dct (dict): The dictionary variable.

        Returns:
            ProvisionBulkBuilder: Returns itself to allow for method chaining.

        Example:
             ~~~python
            builder.from_dict({
                "entities": [
                    {
                    "provision": {
                        "administration": {
                            "organization": {
                                "_current": {
                                    "value": "base_organization"
                                    }
                                }
                            }
                        }
                    }
                ])
                 ~~~
        """

        validate_type(dct, dict, "Dict")
        self.payload = dct

        return self

    @set_method_call
    def build(self) -> 'ProvisionBulkBuilder':
        """
        Finalizes the construction of the provision bulk configuration.

        This method prepares the builder to execute the request by ensuring all necessary configurations are set and validates the overall integrity of the build. It should be called before executing the request to ensure that the configuration is complete and valid.

        The build process involves checking that mandatory fields such as the organization name are set. It also ensures that method calls that are incompatible with each other (like `build` and `build_execute`) are not both used.

        Returns:
            IotCollectionBuilder: Returns itself to allow for method chaining, enabling further actions like `execute`.

        Raises:
            ValueError: If required configurations are missing or if incompatible methods are used together.

        Example:
             ~~~python
                builder.build()
             ~~~

        """

        self.builder = True
        self._validate_builds()

        if self.method_calls.count('build_execute') > 0:
            raise ValueError("You cannot use build() together with build_execute()")

        return self

    @set_method_call
    def build_execute(self, include_payload=False):
        """
        Executes the provision bulk immediately after building the configuration.

        This method is a shortcut that combines building and executing in a single step. It should be used when you want to build and execute the configuration without modifying the builder state in between these operations.

        It first validates the build configuration and then executes the request if the validation is successful.

        Args:
            include_payload (bool): Determine if the payload should be included in the response.

        Returns:
            dict: A dictionary containing the execution response which includes the status code and potentially other metadata about the execution.

        Raises:
            ValueError: If `build` has already been called on this builder instance, indicating that `build_execute` is being incorrectly used after `build`.
            Exception: If there are issues during the execution process, including network or API errors.

        Example:
             ~~~python
                response = builder.build_execute()
             ~~~
        """

        self.builder = True
        if self.method_calls.count('build') > 0:
            raise ValueError("You cannot use build_execute() together with build()")

        self._validate_builds()
        return self._execute_bulk_provisioning(include_payload)

    @set_method_call
    def execute(self, include_payload=False):
        """
        Executes the provision bulk based on the current configuration of the builder.

        Args:
            include_payload (bool): Determine if the payload should be included in the response.

        Returns:
            Dict: A dictionary containing the execution response which includes the status code and,
                              optionally, the payload. If an error occurs, a string describing the error is returned.

        Raises:
            Exception: If `build()` has not been called before `execute()`, or if it was not the last method invoked prior to `execute()`.

        Example:
             ~~~python
                builder.build()
                response = builder.execute(True)
             ~~~
        """
        if self.method_calls.count('build') > 1:
            raise Exception("The 'build()' function can only be called once.")

        if not self.builder or self.method_calls[-2] != 'build':
            raise Exception("The build() function must be called and must be the last method invoked before execute")

        return self._execute_bulk_provisioning(include_payload)

    def _execute_bulk_provisioning(self, include_payload):
        files = None
        data = None
        if self.method_calls.count('from_excel') > 0:
            files = self.file
            if include_payload:
                raise Exception('You cannot add a payload for excel files')
        else:
            data = self._get_file_data()

        if self.client.url is None:
            base_url = 'https://frontend:8443'
        else:
            base_url = f'{self.client.url}/north'

        url = f'{base_url}/v80/provision/organizations/{self.organization_name}/bulk/async'

        response = send_request(method='post', headers=self.client.headers, url=url, data=data, files=files,
                                params={
                                    'action': self.bulk_action,
                                    'type': self.bulk_type,
                                    'flattened': self.flatten,
                                    'full': self.full
                                })

        if files:
            self.excel_file.close()

        if response.status_code == 201:
            result = {'status_code': response.status_code}
            if include_payload:
                result['payload'] = self.payload
            return result
        else:
            return {'status_code': response.status_code, 'error': response.text}


    def _process_dataframe(self, df: pd.DataFrame):
        unflats = []
        for df_dict in df.to_dict(orient='records'):
            if any('_' in key for key in df_dict.keys()):
                unflat = unflatten(df_dict, splitter='underscore')
                unflats.append(self._add_underscore_to_current_keys(unflat))
            elif any('.' in key for key in df_dict.keys()):
                unflat = unflatten(df_dict, splitter='dot')
                unflats.append(self._add_underscore_to_current_keys(unflat))
            else:
                raise ValueError('Column names must be linked with "_" or "."')
        return unflats

    def _add_underscore_to_current_keys(self, dct: dict):
        for key in list(dct.keys()):
            if isinstance(dct[key], dict):
                self._add_underscore_to_current_keys(dct[key])
            if key == 'current':
                dct[f'_{key}'] = dct.pop(key)

        return dct

    def _get_file_data(self):
        try:
            file_extension = self.file_name.split('.')[-1]
            if file_extension == 'json':
                self.client.headers['Content-Type'] = 'application/json'
                self.payload = self.file_content
                return json.dumps(self.file_content)

            elif file_extension == 'csv':
                self.client.headers['Content-Type'] = 'text/plain'
                self.payload = self.file_content
                return self.file_content

        except Exception as e:
            if (self.method_calls.count('from_dict') or self.method_calls.count('from_dataframe')) > 0:
                self.client.headers['Content-Type'] = 'application/json'
                return json.dumps(self.payload)
            else:
                raise e

    def _validate_builds(self):
        if self.method_calls.count('with_organization_name') == 0:
            raise ValueError("Organization name needed to build the EntitiesBulkProvisionBuilder.")

        if not any(func in self.method_calls for func in
                   ("from_dataframe", "from_csv", "from_excel", "from_json", "from_dict")):
            raise ValueError(
                "At least one source of data must be added using the following functions:\n - from_dataframe\n - from_csv\n - from_excel\n - from_json\n - from_dict")
