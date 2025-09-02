"""  ProvisionProcessorBuilder """

import requests
from typing import Any
from requests import Response
from opengate_data.utils.utils import validate_type, send_request, set_method_call, handle_basic_response


class ProvisionProcessorBuilder:
    """ Provision Processor Builder """

    def __init__(self, opengate_client):
        self.client = opengate_client
        if self.client.url is None:
            self.base_url = 'https://frontend:8443'
        else:
            self.base_url = f'{self.client.url}/north'
        self.headers: dict[str, Any] = self.client.headers
        self.organization_name: str | None = None
        self.provision_processor_id: str | None = None
        self.provision_processor_name: str | None = None
        self.bulk_process_id: str | None = None
        self.bulk_file: str | None = None
        self.url: str | None = None
        self.method: str | None = None
        self.requires: dict[str, Any] = {}
        self.method_calls: list = []

    @set_method_call
    def with_organization_name(self, organization_name: str) -> 'ProvisionProcessorBuilder':
        """
        Specify the organization name.

        Args:
            organization_name (str): The name of the organization.

        Returns:
            ProvisionProcessorBuilder: Returns self for chaining.

        Example:
            ~~~python
                builder.with_organization_name('organization_name')
            ~~~
        """
        validate_type(organization_name, str, "Organization")
        self.organization_name = organization_name
        return self

    @set_method_call
    def with_identifier(self, provision_processor_id: str) -> 'ProvisionProcessorBuilder':
        """
         Specify the identifier for the provision processor.

         Args:
             provision_processor_id (str): The identifier for the pipeline.

         Returns:
             ProvisionProcessorBuilder: Returns self for chaining.

        Example:
            ~~~python
                builder.with_identifier('identifier')
            ~~~
         """
        validate_type(provision_processor_id, str, "Identifier")
        self.provision_processor_id = provision_processor_id
        return self

    @set_method_call
    def with_name(self, provision_processor_name: str) -> 'ProvisionProcessorBuilder':
        """
         Specify the name for the provision processor.

         Args:
             provision_processor_name (str): The name for the provision processor.

         Returns:
             ProvisionProcessorBuilder: Returns self for chaining.

        Example:
            ~~~python
                builder.with_name('name')
            ~~~
         """
        validate_type(provision_processor_name, str, "Name")
        self.provision_processor_name = provision_processor_name
        return self

    @set_method_call
    def with_bulk_file(self, bulk_file: str) -> 'ProvisionProcessorBuilder':
        """
        Specify the file for bulk processing.

        Args:
            bulk_file (str): The path to the file to be uploaded for bulk processing.

        Returns:
            ProvisionProcessorBuilder: Returns self for chaining.

        Example:
            ~~~python
                bulk_file_path = os.path.join(os.path.dirname(__file__), 'file.xlsx')
                builder.with_bulk_file('bulk_file_path')
            ~~~
        """
        self.bulk_file = {'file': (
            'salida.xlsx', open(bulk_file, 'rb'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        return self

    @set_method_call
    def with_bulk_process_identitifer(self, bulk_process_id: str) -> 'ProvisionProcessorBuilder':
        """
         Specify the identifier for the bulk process identifier.

         Args:
             bulk_process_id (str): The identifier for the bulk process.

         Returns:
             ProvisionProcessorBuilder: Returns self for chaining.

        Example:
            ~~~python
                builder.with_bulk_process_identitifer('identifier')
            ~~~
         """
        self.bulk_process_id = bulk_process_id
        return self

    @set_method_call
    def bulk(self) -> 'ProvisionProcessorBuilder':
        """
        Configure the builder for bulk provisioning.

        This method sets the necessary headers and URL for performing a bulk provisioning operation.

        Returns:
            ProvisionProcessorBuilder: Returns self for chaining.

        Example:
            ~~~python
                bulk_file_path = os.path.join(os.path.dirname(__file__), 'file.xlsx')
                builder.with_organization_name('organization_name').with_identifier('identifier').with_bulk_file(bulk_file_path).bulk()
            ~~~
        """
        self.method = 'bulk_provision_processor'
        self.headers['Accept'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        self.url = f'{self.base_url}/v80/provisionProcessors/provision/organizations/{self.organization_name}/{self.provision_processor_id}/bulk'
        return self

    @set_method_call
    def find_by_name(self) -> 'ProvisionProcessorBuilder':
        """
        Configure the builder to find a provision processor by name.

        This method sets the necessary headers and URL for finding a provision processor by its name.

        Returns:
            ProvisionProcessorBuilder: Returns self for chaining.

        Example:
            ~~~python
                builder.with_organization_name('organization_name').with_name('provision_processor_name').find_by_name()
            ~~~
        """
        self.method = 'find_by_name'
        self.headers['Accept'] = 'application/json'
        self.url = f'{self.base_url}/v80/provisionProcessors/provision/organizations/{self.organization_name}'
        return self

    @set_method_call
    def bulk_status(self) -> 'ProvisionProcessorBuilder':
        """
        Configure the builder to check the status of a bulk process.

        This method sets the necessary headers and URL for checking the status of a bulk process.

        Returns:
            ProvisionProcessorBuilder: Returns self for chaining.

        Example:
            ~~~python
                builder.with_organization_name('organization_name').with_bulk_process_identitifer('bulk_process_id').bulk_status()
            ~~~
        """
        self.method = 'bulk_status'
        self.headers['Accept'] = 'application/json'
        self.url = f'{self.base_url}/v80/provisionProcessors/provision/organizations/{self.organization_name}/bulk/{self.bulk_process_id}'
        return self

    @set_method_call
    def bulk_details(self) -> 'ProvisionProcessorBuilder':
        """
        Configure the builder to get the details of a bulk process.

        This method sets the necessary headers and URL for retrieving the details of a bulk process.

        Returns:
            ProvisionProcessorBuilder: Returns self for chaining.

        Example:
            ~~~python
                builder.with_organization_name('organization_name').with_bulk_process_identitifer('bulk_process_id').bulk_details()
            ~~~
        """
        self.method = 'bulk_details'
        self.headers['Accept'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        self.url = f'{self.base_url}/v80/provisionProcessors/provision/organizations/{self.organization_name}/bulk/{self.bulk_process_id}/details'
        return self

    @set_method_call
    def build(self) -> 'ProvisionProcessorBuilder':
        """
        Finalizes the construction of the IoT collection configuration.

        This method prepares the builder to execute the collection by ensuring all necessary configurations are set and validates the overall integrity of the build. It should be called before executing the collection to ensure that the configuration is complete and valid.

        The build process involves checking that mandatory fields such as the device identifier are set. It also ensures that method calls that are incompatible with each other (like `build` and `build_execute`) are not both used.

        Returns:
            ProvisionProcessorBuilder: Returns itself to allow for method chaining, enabling further actions like `execute`.

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
        Executes the data sets search immediately after building the configuration.

        This method is a shortcut that combines building and executing in a single step.

        Returns:
            dict: A dictionary containing the execution response which includes the status code and potentially other metadata about the execution.

        Raises:
            ValueError: If `build` has already been called on this builder instance.

        Example:
            ~~~python
            builder.build_execute()
            ~~~
        """
        if 'build' in self.method_calls:
            raise ValueError("You cannot use build_execute() together with build()")

        if 'execute' in self.method_calls:
            raise ValueError("You cannot use build_execute() together with execute()")

        self._validate_builds()
        return self.execute()

    @set_method_call
    def execute(self) -> requests.Response:
        """
        Execute the configured operation and return the response.

        This method executes the operation that has been configured using the builder pattern. It ensures that the `build` method has been called and that it is the last method invoked before `execute`. Depending on the configured method (e.g., create, find, update, delete), it calls the appropriate internal execution method.

        Returns:
            requests.Response: The response object from the executed request.

        Raises:
            Exception: If the `build` method has not been called or if it is not the last method invoked before `execute`.
            ValueError: If the configured method is unsupported.

        Example:
            ~~~python
                builder.build_execute()
            ~~~
        """
        if 'build' in self.method_calls:
            if self.method_calls.count('build') > 1:
                raise Exception("The 'build()' function can only be called once.")

            if self.method_calls[-2] != 'build':
                raise Exception("The build() function must be the last method invoked before execute.")

        if 'build' not in self.method_calls and 'build_execute' not in self.method_calls:
            raise Exception("You need to use a build() or build_execute() function the last method invoked before execute.")

        methods = {
            'bulk_provision_processor': self._execute_bulk,
            'find_by_name': self._execute_find_by_name,
            'bulk_status': self._execute_bulk_status,
            'bulk_details': self._execute_bulk_details,
        }
        function = methods.get(self.method)
        if function is None:
            raise ValueError(f'Unsupported method: {self.method}')
        return function()

    def _execute_bulk(self) -> dict[str, Any]:
        response = send_request(method='post', headers=self.headers, url=self.url, files=self.bulk_file)
        return handle_basic_response(response)

    def _execute_find_by_name(self):
        request_response = send_request(method="get", headers=self.headers, url=self.url)
        data = request_response.json()
        provision_procesor = {}
        for item in data.get("provisionProcessors", []):
            if item.get("name") == self.provision_processor_name:
                provision_procesor = item
        return provision_procesor

    def _execute_bulk_status(self) -> dict[str, Any] | Any:
        response = send_request(method="get", headers=self.headers, url=self.url)
        if response.status_code == 200:
            return response
        else:
            return {'status_code': response.status_code, 'error': response.text}

    def _execute_bulk_details(self) -> dict[str, Any] | Response | Any:
        response = send_request(method="get", headers=self.headers, url=self.url)
        if response.status_code == 200:
            return response
        else:
            return {'status_code': response.status_code, 'error': response.text}

    def _validate_builds(self):
        required_methods = {
            'bulk': ['with_organization_name', 'with_identifier', 'with_bulk_file', 'with_bulk_file'],
            'find_by_name': ['with_organization_name', 'with_name'],
            'bulk_status': ['with_organization_name', 'with_bulk_process_identitifer'],
            'bulk_datails': ['with_organization_name', 'with_bulk_process_identitifer']
        }
        for method, required in required_methods.items():
            if self.method_calls.count(method) > 0:
                missing_methods = [req for req in required if req not in self.method_calls]
                if missing_methods:
                    raise Exception(f"It is mandatory to use the {', '.join(missing_methods)} method(s) in {method}()")
        return self
