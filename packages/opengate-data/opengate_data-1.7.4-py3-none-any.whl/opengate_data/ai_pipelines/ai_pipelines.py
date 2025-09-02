"""  AIPipelinesBuilder """

import configparser
import json
import os
from typing import Any

import requests
from dotenv import dotenv_values, set_key
from requests import Response

from opengate_data.utils.utils import validate_type, send_request, set_method_call, handle_basic_response, parse_json


class AIPipelinesBuilder:
    """ Builder pipelines """

    def __init__(self, opengate_client):
        self.client: str = opengate_client
        self.builder: bool = False
        if self.client.url is None:
            self.base_url = 'https://ai:9644/ai'
        else:
            self.base_url = f'{self.client.url}/north/ai'
        self.organization_name: str | None = None
        self.identifier = None
        self.config_file: str | None = None
        self.section: str | None = None
        self.config_key: str | None = None
        self.new_file: str | None = None
        self.data_prediction: dict = {}
        self.url: str | None = None
        self.requires: Dict[str, Any] = None
        self.method: str | None = None
        self.name: str | None = None
        self.output_file_path: str | None = None
        self.collect = None
        self.action = None
        self.type = None
        self.actions = []
        self.data_env: str | None = None
        self.method_calls: list = []
        self.find_name: str | None = None

    @set_method_call
    def with_organization_name(self, organization_name: str) -> 'AIPipelinesBuilder':
        """
        Specify the organization name.

        Args:
            organization_name (str): The name of the organization.

        Returns:
            AIModelsBuilder: Returns self for chaining.

        Example:
            ~~~python
                builder.with_organization_name('organization_name')
            ~~~
        """
        validate_type(organization_name, str, "Organization Name")
        self.organization_name = organization_name
        return self
    
    @set_method_call
    def with_identifier(self, identifier: str) -> 'AIPipelinesBuilder':
        """
         Specify the identifier for the pipeline.

         Args:
             identifier (str): The identifier for the pipeline.

         Returns:
             AIModelsBuilder: Returns self for chaining.

        Example:
            ~~~python
                builder.with_identifier('identifier')
            ~~~
         """
        validate_type(identifier, str, "Identifier")
        self.identifier = identifier
        return self

    @set_method_call
    def with_env(self, data_env: str) -> 'AIPipelinesBuilder':
        """
        Specify the environment variable.

        Args:
            data_env (str): The environment variable.

        Returns:
            AIModelsBuilder: Returns self for chaining.

        Example:
            ~~~python
                builder.with_env('PIPELINE_ID')
            ~~~
        """
        validate_type(data_env, str, "Data env")
        self.data_env = data_env
        return self

    @set_method_call
    def with_find_by_name(self, find_name: str) -> 'AIPipelinesBuilder':
        """
        Specify the name to find.

        Args:
            find_name (str): The name of the pipeline.

        Returns:
            AIPipelinesBuilder: Returns self for chaining.

        Example:
            ~~~python
                builder.with_find_by_name('pipeline_name')
            ~~~
        """
        validate_type(find_name, str, "Find Name")
        self.find_name = find_name
        return self

    @set_method_call
    def with_config_file(self, config_file: str, section: str, config_key: str) -> 'AIPipelinesBuilder':
        """
        Sets up the configuration file (.ini).

        This method allows specifying a configuration file, a section within that file, and a key to retrieve a specific value from the section.

        Args:
            config_file (str): The path to the.ini configuration file.
            section (str): The section name within the.ini file where the desired configuration is located.
            config_key (str): The key within the specified section whose value will be retrieved.

        Raises:
            TypeError: If the provided config_file is not a string.
            TypeError: If the provided section is not a string.
            TypeError: If the provided config_key is not a string.

        Example:
            ~~~python
                [id]
                pipeline_id = afe07216-14ec-4134-97ae-c483b11d965a
                config_file_path = os.path.join(os.path.dirname(__file__), 'config_test.ini')
                builder.with_config_file(config_file_path, 'id', 'pipeline_id')
            ~~~
        Returns:
            AIPipelinesBuilder: Returns itself to allow for method chaining.
        """
        validate_type(config_file, str, "Config file")
        validate_type(section, str, "Section")
        validate_type(config_key, str, "Config Key")

        config_file_path = os.path.abspath(config_file)

        self.config_file = config_file_path
        self.section = section
        self.config_key = config_key

        config = configparser.ConfigParser()
        config.read(config_file_path)
        self.identifier = config.get(section, config_key)
        return self

    @set_method_call
    def with_prediction(self, data_prediction: dict) -> 'AIPipelinesBuilder':
        """
        Prediction with a model

        Args:
            data_prediction (dict): Prediction

        Raises:
            TypeError: If the prediction is not a dict.

        Returns:
            AIPipelinesBuilder: Returns itself to allow for method chaining.

        Example:
        ~~~python
            {
              "input": {},
              "collect": {
                "deviceId": "123456",
                "datastream": "PredictionDatastream"
              }
            }
            builder.with_prediction(prediction)
        ~~~
        """
        validate_type(data_prediction, dict, "Data prediction")
        self.data_prediction = data_prediction
        return self

    @set_method_call
    def with_name(self, name: str) -> 'AIPipelinesBuilder':
        """
        Name a new pipeline

        Args:
            name (str): Name a new pipeline

        Raises:
            TypeError: If the name is not a string.

        Returns:
            AIPipelinesBuilder: Returns itself to allow for method chaining.

        Example:
            ~~~python
            builder.with_name(name_prediction)
            ~~~
        """

        validate_type(name, str, "Name")
        self.name = name
        return self

    @set_method_call
    def add_action(self, file_name: str, type_action: str | None = None) -> 'AIPipelinesBuilder':
        """
        Add action name and type of model or transform exist.

        Args:
            file_name (str): The name of the file representing the action.
            type_action (str | None): The type of the action, either 'MODEL' or 'TRANSFORMER'. If None, it will be inferred from the file extension.

        Raises:
            TypeError: If file_name is not a string.
            TypeError: If type_action is not a string or None.

        Returns:
            AIPipelinesBuilder: Returns itself to allow for method chaining.

        Example:
            ~~~python
                builder.add_action('transform.py', 'TRANSFORMER')
                builder.add_action('test/file_create.onnx', 'MODEL')
                builder.add_action('test/file_update.onnx')
            ~~~
        """

        validate_type(file_name, str, "File Name")
        validate_type(type_action, (str, type(None)), "Type action")

        if os.path.dirname(file_name):
            file_name = os.path.basename(file_name)

        _, file_extension = os.path.splitext(file_name)
        if file_extension == '.py':
            default_type = 'TRANSFORMER'
        else:
            default_type = 'MODEL'

        action_type = type_action if type_action is not None else default_type

        action = {
            'name': file_name,
            'type': action_type
        }
        self.actions.append(action)

        return self

    @set_method_call
    def build(self) -> 'AIPipelinesBuilder':
        """
        This method prepares the builder to execute the collection by ensuring all necessary configurations are set and validates the overall integrity of the build. It should be called before executing the collection to ensure that the configuration is complete and valid.

        The build process involves checking that mandatory fields such as the device identifier are set. It also ensures that method calls that are incompatible with each other (like `build` and `build_execute`) are not both used.

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
            raise Exception("You cannot use 'build()' together with 'build_execute()'")

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
            raise ValueError("You cannot use 'build_execute()' together with 'build()'")

        if 'execute' in self.method_calls:
            raise ValueError("You cannot use 'build_execute()' together with 'execute()'")

        self._validate_builds()
        return self.execute()

    @set_method_call
    def create(self) -> 'AIPipelinesBuilder':
        """
        Creates a new pipeline.

        This method prepares the request to create a new pipeline using the specified configuration in the object. It is necessary to define the name (`with_name`) and actions (`add_action`) before calling this method.

        Returns:
            AIPipelinesBuilder: Returns the same object to allow method chaining.

        Example:
            ~~~python
            builder.with_organization_name(organization)\
                .with_name('MyPipeline').add_action('transform.py', 'TRANSFORMER')\
                .add_action('test/file_create.onnx', 'MODEL')\
                .create()
            ~~~
        """
        self.url = f'{self.base_url}/{self.organization_name}/pipelines'
        self.method = 'create'
        return self

    @set_method_call
    def find_all(self) -> 'AIPipelinesBuilder':
        """
        Retrieves all available pipelines.

        Returns:
            AIPipelinesBuilder: Returns the same object to allow method chaining.

        Example:
            ~~~python
            builder.with_organization_name('MyOrganization').find_all()
            ~~~
        """
        self.requires = {
            'organization': self.organization_name
        }
        self.url = f'{self.base_url}/{self.organization_name}/pipelines'
        self.method = 'find'
        return self

    @set_method_call
    def find_one(self) -> 'AIPipelinesBuilder':
        """
        Finds a specific pipeline by its identifier.

        This method prepares the request to find a specific pipeline based on its identifier. The identifier is obtained automatically if not explicitly defined or can be obtained from a configuration file or environment variables.

        Returns:
            AIPipelinesBuilder: Returns the same object to allow method chaining.

        Example:
            ~~~python
            builder.with_organization_name('my_organization').with_identifier('identifier').find_one()
            ~~~

        """
        identifier = self._get_identifier()
        self.url = f'{self.base_url}/{self.organization_name}/pipelines/{identifier}'
        self.method = 'find'
        return self

    @set_method_call
    def update(self) -> 'AIPipelinesBuilder':
        """
        Updates an existing pipeline.

        This method prepares the request to update an existing pipeline. It is necessary to define the organization's name (`with_organization_name`) and the pipeline's name (`with_name`) before calling this method.

        Returns:
            AIPipelinesBuilder: Returns the same object to allow method chaining.

        Example:
            ~~~python
            builder.with_organization_name('MyOrganization').with_identifier("pipeline_identifier").with_name('MyPipeline').update()
            config_file_path = os.path.join(os.path.dirname(__file__), 'config_test.ini')
            builder.with_organization_name('MyOrganization').with_find_by_name("pipeline_name").with_config_file(config_file_path, 'id', 'model').with_name('MyPipeline').update()
            builder.with_organization_name('MyOrganization').with_name('MyPipeline').update()
            ~~~
        """

        identifier = self._get_identifier()
        self.url = f'{self.base_url}/{self.organization_name}/pipelines/{identifier}'
        self.method = 'update'
        return self

    @set_method_call
    def delete(self) -> 'AIPipelinesBuilder':
        """
        Deletes an existing pipeline.

        This method prepares the request to delete an existing pipeline. It is necessary to define the organization's name (`with_organization_name`) and the pipeline's identifier (`with_identifier`) before calling this method.

        Returns:
            AIPipelinesBuilder: Returns the same object to allow method chaining.

        Example:
            ~~~python
            builder.with_organization_name('MyOrganization').with_identifier('pipeline_identifier').delete()
            ~~~
        """
        identifier = self._get_identifier()
        self.url = f'{self.base_url}/{self.organization_name}/pipelines/{identifier}'
        self.method = 'delete'
        return self

    @set_method_call
    def prediction(self) -> 'AIPipelinesBuilder':
        """
        Performs a prediction with a model.

        This method prepares the request to perform a prediction using the model associated with the specified pipeline. It is necessary to define the organization's name (`with_organization_name`), the pipeline's identifier (`with_identifier`), and provide prediction data (`with_prediction`) before calling this method.

        Returns:
            AIPipelinesBuilder: Returns the same object to allow method chaining.

        Example:
            ~~~python
            builder.with_organization_name('MyOrganization').with_identifier('pipeline_identifier').with_prediction({'input': {}, 'collect': {'deviceId': '123456', 'datastream': 'PredictionDatastream'}}).prediction()
            ~~~
        """
        identifier = self._get_identifier()
        self.url = f'{self.base_url}/{self.organization_name}/pipelines/{identifier}/prediction'
        self.method = 'prediction'
        return self

    @set_method_call
    def save(self) -> 'AIPipelinesBuilder':
        """
        Save the model configuration.

        This method sets up the AIPipelinesBuilder instance to save the configuration of a model associated with the specified organization. It configures the URL endpoint for the save operation and sets the operation type to 'save'.

        Returns:
            AIPipelinesBuilder: The instance of the AIModelsBuilder class itself, allowing for method chaining.

        Example:
            ~~~python
            builder.with_organization_name("MyOrganization").with_env("MODEL_ENV_VAR").save().build().execute()
            config_file_path = os.path.join(os.path.dirname(__file__), 'config_test.ini')
            builder.with_organization_name("MyOrganization").with_config_file(config_file_path, 'id', 'model').save().build().execute()
            ~~~
        """
        self.method = 'save'
        return self

    @set_method_call
    def set_config_file_identifier(self) -> 'AIPipelinesBuilder':
        """
        Set the model identifier from a configuration file.

        This method sets up the AIModelsBuilder instance to retrieve the model identifier from a specified configuration file. It reads the identifier from the given section and key within the configuration file and sets it for the builder instance.

        Returns:
            AIPipelinesBuilder: The instance of the AIModelsBuilder class itself, allowing for method chaining.

        Example:
            ~~~python
            config_file_path = os.path.join(os.path.dirname(__file__), 'config_test.ini')
            builder.with_config_file(config_file_path, 'id', 'model_id').set_config_file_identifier().build().execute()
            ~~~
        """
        self.method = 'set_config_identifier'
        return self

    @set_method_call
    def set_env_identifier(self) -> 'AIPipelinesBuilder':
        """
        Set the model identifier from an environment variable.

        This method sets up the AIModelsBuilder instance to retrieve the model identifier from a specified environment variable. It reads the identifier from the environment variable and sets it for the builder instance.

        Returns:
            AIPipelinesBuilder: The instance of the AIModelsBuilder class itself, allowing for method chaining.

        Example:
            ~~~python
            builder.with_env("MODEL_ENV_VAR").set_env_identifier().build().execute()
            ~~~
        """
        self.method = 'set_env_identifier'
        return self

    @set_method_call
    def execute(self):
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
            builder.execute()
            ~~~
         """
        if 'build' in self.method_calls:
            if self.method_calls[-2] != 'build':
                raise Exception("The build() function must be the last method invoked before execute.")

        if 'build' not in self.method_calls and 'build_execute' not in self.method_calls:
            raise Exception(
                "You need to use a build() or build_execute() function the last method invoked before execute.")

        methods = {
            'create': self._execute_create,
            'find': self._execute_find,
            'update': self._execute_update,
            'delete': self._execute_delete,
            'prediction': self._execute_prediction,
            'save': self._execute_save,
            'set_config_identifier': self._execute_set_identifier,
            'set_env_identifier': self._execute_env_identifier,
        }

        function = methods.get(self.method)
        if function is None:
            raise ValueError(f'Unsupported method: {self.method}')
        return function()

    def _list_pipelines(self):
        url = f'{self.base_url}/{self.organization_name}/pipelines'
        response = send_request(method='get', headers=self.client.headers, url=url)
        if response.status_code != 200:
            raise Exception(f'Cannot list pipelines: {response.status_code} {response.text}')
        return parse_json(response.text)

    def _pipeline_exists(self, identifier: str) -> bool:
        url = f'{self.base_url}/{self.organization_name}/pipelines/{identifier}'
        response = send_request(method='get', headers=self.client.headers, url=url)
        return response.status_code == 200

    def _execute_create(self):
        if not self.name:
            raise ValueError('The "with_name" is required.')
        if not self.actions:
            raise ValueError('The "add_action is required.')

        data = {"name": self.name, "actions": self.actions}
        response = send_request(method='post', headers=self.client.headers, url=f'{self.base_url}/{self.organization_name}/pipelines', json_payload=data)

        if response.status_code == 201:
            file_config = self._read_config_file()
            all_items = self._list_pipelines()
            result = next((it['identifier'] for it in all_items if it['name'] == self.name), None)

            if file_config:
                try:
                    file_config.set(self.section, self.config_key, result)
                    with open(self.config_file, 'w', encoding='utf-8') as configfile:
                        file_config.write(configfile)
                except configparser.NoOptionError as error:
                    raise ValueError('The "pipeline_id" parameter was not found in the configuration file.') from error

            elif self.data_env is not None:
                env_vars = dotenv_values('.env')
                if self.data_env not in env_vars:
                    raise ValueError('The environment variable was not found in the .env file.')
                set_key('.env', self.data_env, result)

            return {'status_code': response.status_code}
        else:
            return {'status_code': response.status_code, 'error': response.text}
    
    def _execute_find(self) -> requests.Response | dict[str, Any]:
        response = send_request(method='get', headers=self.client.headers, url=self.url)
        result = {'status_code': response.status_code}
        if response.status_code == 200:
            result['data'] = parse_json(response.text)
        else:
            if response.text:
                result['error'] = response.text
        return result

    def _execute_update(self):
        name = self.name
        actions = self.actions

        if not name:
            raise ValueError('The "with_name" is required.')

        if not actions:
            raise ValueError('The "add_action is required.')

        data = {
            "name": name,
            "actions": actions
        }
        response = send_request(method='put', headers=self.client.headers, url=self.url, json_payload=data)
        return handle_basic_response(response)

    def _execute_delete(self):
        response = send_request(method='delete', headers=self.client.headers, url=self.url)
        return handle_basic_response(response)

    def _execute_prediction(self) -> str | dict[str, str | int]:
        self.client.headers['Content-Type'] = 'application/json'
        payload = json.dumps(self.data_prediction)
        response = send_request('post', self.client.headers, self.url, payload)
        result = {'status_code': response.status_code}
        if response.status_code == 200:
            result['data'] = parse_json(response.text)
        else:
            result['error'] = response.text
        return result

    def _execute_save(self):
        if self.data_env is not None or self.config_file is not None:
            if self.data_env is not None:
                self.identifier = dotenv_values('.env').get(self.data_env)
            else:
                config = configparser.ConfigParser()
                config.read(self.config_file)
                self.identifier = config.get(self.section, self.config_key, fallback=None)

            exists = self._pipeline_exists(self.identifier)

            if exists:
                # update
                self.url = f'{self.base_url}/{self.organization_name}/pipelines/{self.identifier}'
                return self._execute_update()
            else:
                # create
                self.url = f'{self.base_url}/{self.organization_name}/pipelines'
                return self._execute_create()

        return ValueError('The "config file" or env parameter was not found')


    def _execute_set_identifier(self):
        try:
            file_config = self._read_config_file()
            self._read_config_file().get(self.section, self.config_key)
            file_config.set(self.section, self.config_key, self.identifier)
            with open(self.config_file, 'w', encoding='utf-8') as configfile:
                file_config.write(configfile)
            return None

        except configparser.NoOptionError:
            return ValueError('The "pipeline_id" parameter was not found in the configuration file.')

    def _execute_env_identifier(self) -> None:
        try:
            env_vars = dotenv_values('.env')
            if self.data_env not in env_vars:
                raise KeyError('The environment variable was not found in the .env file.')

            set_key('.env', self.data_env, self.identifier)

        except KeyError as error:
            raise ValueError('The environment variable was not found in the .env file.') from error

    def _read_config_file(self):
        if self.config_file is not None:
            if os.path.exists(self.config_file):
                config = configparser.ConfigParser()
                config.read(self.config_file)
                return config
            raise ValueError('The configuration file does not exist.')
        return None

    def _validate_builds(self):
        if self.method_calls.count('create') > 0:
            if "with_organization_name" not in self.method_calls and "with_name" not in self.method_calls and "add_action" not in self.method_calls:
                raise Exception(
                    "It is mandatory to use the with_organization_name() and with_name() add_action() methods in create()")

        if self.method_calls.count('find_one') > 0:
            if "with_organization_name" not in self.method_calls:
                raise Exception(
                    "It is mandatory to use the with_organization_name() method in find_one()")

        if self.method_calls.count('find_all') > 0:
            if "with_organization_name" not in self.method_calls:
                raise Exception("It is mandatory to use the with_organization_name() methods")

        if self.method_calls.count('update') > 0:
            if "with_organization_name" not in self.method_calls and "with_name" not in self.method_calls:
                raise Exception(
                    "It is mandatory to use the with_organization_name() and with_name() method in update()")

        if self.method_calls.count('delete') > 0:
            if "with_organization_name" not in self.method_calls:
                raise Exception("It is mandatory to use the with_organization_name()")

        if self.method_calls.count('prediction') > 0:
            if "with_organization_name" not in self.method_calls and "with_prediction" not in self.method_calls:
                raise Exception(
                    "It is mandatory to use the with_organization_name() and with_output_file_path () methods in download()")

        if self.method_calls.count('save') > 0:
            if "with_organization_name" not in self.method_calls:
                raise Exception("It is mandatory to use the with_organization_name() method in update()")

        if self.method_calls.count('set_config_file_identifier') > 0:
            if "with_config_file" not in self.method_calls:
                raise Exception("It is mandatory to use the with_config_file() method in set_config_file_identifier()")

        if self.method_calls.count('set_env_identifier') > 0:
            if "with_env" not in self.method_calls:
                raise Exception("It is mandatory to use the with_env() method in set_env_identifier()")

        return self

    def _get_identifier(self) -> str:
        if self.identifier is not None:
            return self.identifier

        if self.data_env is not None:
            config = dotenv_values()
            identifier = config.get(self.data_env)
            if identifier is None:
                raise KeyError(f'The parameter "{self.data_env}" was not found in the configuration env')
            return identifier

        if self.config_file is not None and self.section is not None and self.config_key is not None:
            config = configparser.ConfigParser()
            config.read(self.config_file)
            try:
                return config.get(self.section, self.config_key)
            except (configparser.NoOptionError, configparser.NoSectionError) as e:
                raise ValueError(f'The "{self.config_key}" parameter was not found in the configuration file: {e}')

        if self.find_name is not None:
            all_items = self._list_pipelines()
            name_identifier = [it['identifier'] for it in all_items if it['name'] == self.find_name]
            if not name_identifier:
                raise Exception(f'File name "{self.find_name}" does not exist')
            return name_identifier[0]

        raise ValueError('A configuration file with identifier, config file, or a find by name is required.')
