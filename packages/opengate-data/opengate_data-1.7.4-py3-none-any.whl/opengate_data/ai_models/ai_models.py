"""  AIModelsBuilder """
import configparser
import json
import os
from configparser import ConfigParser
from typing import Any

from dotenv import set_key, dotenv_values
from requests import Response

from opengate_data.utils.utils import validate_type, send_request, set_method_call, handle_basic_response, parse_json


class AIModelsBuilder:
    """ AI Model Builder """

    def __init__(self, opengate_client):
        self.client = opengate_client
        if self.client.url is None:
            self.base_url = 'https://ai:9644/ai'
        else:
            self.base_url = f'{self.client.url}/north/ai'
        self.organization_name: str | None = None
        self.identifier: str | None = None
        self.config_key: str | None = None
        self.data_env: str | None = None
        self.section: str | None = None
        self.config_file: str | None = None
        self.file_name: str | None = None
        self.full_file_path: str | None = None
        self.data_prediction: dict = {}
        self.output_file_path: str | None = None
        self.method_calls: list = []
        self.url: str | None = None
        self.method: str | None = None
        self.method_calls: list = []
        self.find_name: str | None = None

    @set_method_call
    def with_organization_name(self, organization_name: str) -> 'AIModelsBuilder':
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
    def with_identifier(self, identifier: str) -> 'AIModelsBuilder':
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
    def with_env(self, data_env: str) -> 'AIModelsBuilder':
        """
        Specify the environment variable.

        Args:
            data_env (str): The environment variable.

        Returns:
            AIModelsBuilder: Returns self for chaining.

        Example:
            ~~~python
                builder.with_env('MODEL_ID')
            ~~~
        """
        validate_type(data_env, str, "Data env")
        self.data_env = data_env
        return self

    @set_method_call
    def with_find_by_name(self, find_name: str) -> 'AIModelsBuilder':
        """
        Specify the name to find.

        Args:
            find_name (str): The name of the model.

        Returns:
            AIBuilder: Returns self for chaining.

        Example:
            ~~~python
                builder.with_find_by_name('model_name.onnx')
            ~~~
        """
        validate_type(find_name, str, "Find Name")
        self.find_name = find_name
        return self

    @set_method_call
    def with_config_file(self, config_file: str, section: str, config_key: str) -> 'AIModelsBuilder':
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

        Returns:
            AIModelsBuilder: Returns itself to allow for method chaining.

        Example:
            ~~~python
                [id]
                model_id = afe07216-14ec-4134-97ae-c483b11d965a
                builder.with_config_file('model_config.ini', 'id', 'model_id')
            ~~~
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
    def add_file(self, file: str) -> 'AIModelsBuilder':
        """
        Model file

        Args:
            file (str): The path to the file to be added.

        Raises:
            TypeError: If the provided file path is not a string.

        Example:
            builder.add_file('test.onnx')

        Returns:
            AIModelsBuilder: Returns itself to allow for method chaining.

        Example:
            ~~~python
                builder.add_file('file.onnx')
            ~~~
        """

        validate_type(file, str, "File")
        self.file_name = os.path.basename(file)
        self.full_file_path = os.path.abspath(file)
        return self

    @set_method_call
    def with_prediction(self, data_prediction: dict) -> 'AIModelsBuilder':
        """
        Prediction with a model

        Args:
            data_prediction (dict): Prediction

        Raises:
            TypeError: If the prediction is not a dict.

        Returns:
            AIModelsBuilder: Returns itself to allow for method chaining.

        Example:
            ~~~python
                prediction = {
                  "X": [
                    {
                      "input_8": [
                        [
                          -0.5391107438074961,
                          -0.15950019784171535,
                        ]
                      ]
                    }
                  ]
                }
                builder.with_prediction(prediction)
            ~~~
        """

        validate_type(data_prediction, dict, "Data prediction")
        self.data_prediction = data_prediction
        return self

    @set_method_call
    def with_output_file_path(self, output_file_path: str) -> 'AIModelsBuilder':
        """
        Sets the output file path for the model.

        This method allows you to specify the path where the output file will be saved.
        It is particularly useful for operations that involve downloading or saving files.

        Args:
            output_file_path (str): The path where the output file will be saved.

        Returns:
            AIModelsBuilder: The instance of the AIModelsBuilder class.

        Example:
            ~~~python
            builder.with_output_file_path("rute/prueba.onnx")
            ~~~
        """
        validate_type(output_file_path, str, "Output file path")
        self.output_file_path = output_file_path
        return self

    @set_method_call
    def create(self) -> 'AIModelsBuilder':
        """
        Initiates the creation process of a new model.

        This method prepares the AIModelsBuilder instance to create a new model by setting up the necessary parameters such as the organization name and the file to be associated with the model.

        Returns:
            AIModelsBuilder: The instance of the AIModelsBuilder class itself, allowing for method chaining.

        Example:
            ~~~python
                builder.with_organization_name("MyOrganization").add_file("example.onnx").create()
            ~~~
        """
        self.url = f'{self.base_url}/{self.organization_name}/models'
        self.method = 'create'
        return self

    @set_method_call
    def find_one(self) -> 'AIModelsBuilder':
        """
        Retrieve a single model.

        This method sets up the AIModelsBuilder instance to retrieve a specific model associated with the specified organization and identifier.

        Returns:
            AIModelsBuilder: The instance of the AIModelsBuilder class itself, allowing for method chaining.

        Example:
            ~~~python
                builder.with_organization_name("organization_name").with_identifier("model_identifier").find_one()
            ~~~
        """
        identifier = self._get_identifier()
        self.url = f'{self.base_url}/{self.organization_name}/models/{identifier}'
        self.method = 'find'
        return self

    @set_method_call
    def find_all(self) -> 'AIModelsBuilder':
        """
        Retrieve all models.

        This method sets up the AIModelsBuilder instance to retrieve all models associated with the specified organization.

        Returns:
            AIModelsBuilder: The instance of the AIModelsBuilder class itself, allowing for method chaining.

        Example:
            ~~~python
            builder.with_organization_name("MyOrganization").find_all()
            ~~~

        """
        self.url = f'{self.base_url}/{self.organization_name}/models'
        self.method = 'find'
        return self

    @set_method_call
    def update(self) -> 'AIModelsBuilder':
        """
        Update an existing model.

        This method sets up the AIModelsBuilder instance to update a specific model associated with the specified organization and identifier.

        Returns:
            AIModelsBuilder: The instance of the AIModelsBuilder class itself, allowing for method chaining.

        Example:
            ~~~python
            builder.with_organization_name("MyOrganization").with_identifier("model_identifier").add_file("updated_model.onnx").update()
            builder.with_organization_name("MyOrganization").with_find_by_name("model_name.onnx").add_file("updated_model.onnx").update()
            builder.with_organization_name("MyOrganization").with_config_file('model_config.ini', 'id', 'model').add_file("updated_model.onnx").update()
            ~~~
        """
        identifier = self._get_identifier()
        self.url = f'{self.base_url}/{self.organization_name}/models/{identifier}'
        self.method = 'update'
        return self

    @set_method_call
    def delete(self) -> 'AIModelsBuilder':
        """
        Delete an existing model within the organization.

        This method sets up the AIModelsBuilder instance to delete a specific model associated with the specified organization and identifier.

        Returns:
            AIModelsBuilder: The instance of the AIModelsBuilder class itself, allowing for method chaining.

        Example:
            ~~~python
                builder.with_organization_name("MyOrganization").with_identifier("model_identifier").delete()
                builder.with_organization_name("MyOrganization").with_find_by_name("model_name.onnx").delete()
                builder.with_organization_name("MyOrganization").with_config_file('model_config.ini', 'id', 'model').delete()
            ~~~
        """
        identifier = self._get_identifier()
        self.url = f'{self.base_url}/{self.organization_name}/models/{identifier}'
        self.method = 'delete'
        return self

    @set_method_call
    def validate(self) -> 'AIModelsBuilder':
        """
        Validate the model configuration.

        This method sets up the AIModelsBuilder instance to validate the configuration of a model associated with the specified organization.

        Returns:
            AIModelsBuilder: The instance of the AIModelsBuilder class itself, allowing for method chaining.

        Example:
            ~~~python
            builder.with_organization_name("MyOrganization").add_file("model.onnx").validate()
            ~~~
        """
        self.url = f'{self.base_url}/{self.organization_name}/models/validate'
        self.method = 'validate'
        return self

    @set_method_call
    def download(self) -> 'AIModelsBuilder':
        """
        Download the model file.

        This method sets up the AIModelsBuilder instance to download the file of a specific model associated with the specified organization and identifier.

        Returns:
            AIModelsBuilder: The instance of the AIModelsBuilder class itself, allowing for method chaining.

        Example:
            ~~~python
            builder.with_organization_name("MyOrganization").with_identifier("model_identifier").with_output_file_path("model.onnx").download()
            builder.with_organization_name("MyOrganization").with_find_by_name("model_name.onnx").with_output_file_path("model.onnx").download()
            builder.with_organization_name("MyOrganization").with_config_file('model_config.ini', 'id', 'model').with_output_file_path("model.onnx").download()
            ~~~
        """
        identifier = self._get_identifier()
        self.url = f'{self.base_url}/{self.organization_name}/models/{identifier}/file'
        self.method = 'download'
        return self

    @set_method_call
    def prediction(self) -> 'AIModelsBuilder':
        """
         Make a prediction using the model.

         This method sets up the AIModelsBuilder instance to make a prediction using a specific model associated with the specified organization and identifier.

         Returns:
             AIModelsBuilder: The instance of the AIModelsBuilder class itself, allowing for method chaining.

         Example:
             ~~~python
             prediction_data = {
                 "X": [
                     {
                         "input_8": [
                             [
                                 -0.5391107438074961,
                                 -0.15950019784171535,
                             ]
                         ]
                     }
                 ]
             }
             builder.with_organization_name("MyOrganization").with_identifier("model_identifier").with_prediction(prediction_data).prediction()
             builder.with_organization_name("MyOrganization").with_find_by_name("model_name.onnx").with_prediction(prediction_data).prediction()
             builder.with_organization_name("MyOrganization").with_config_file('model_config.ini', 'id', 'model').with_prediction(prediction_data).prediction()
             ~~~
         """
        identifier = self._get_identifier()
        self.url = f'{self.base_url}/{self.organization_name}/models/{identifier}/prediction'
        self.method = 'prediction'
        return self

    @set_method_call
    def save(self) -> 'AIModelsBuilder':
        """
        Save the model configuration.

        This method sets up the AIModelsBuilder instance to save the configuration of a model associated with the specified organization.

        Returns:
            AIModelsBuilder: The instance of the AIModelsBuilder class itself, allowing for method chaining.

        Example:
            ~~~python
                builder.with_organization_name("MyOrganization").with_env("env_var").save()
                builder.with_organization_name("MyOrganization").with_config_file('model_config.ini', 'id', 'model').save()
            ~~~
        """
        self.method = 'save'
        return self

    @set_method_call
    def set_config_file_identifier(self) -> 'AIModelsBuilder':
        """
        Set the model identifier from a configuration file.

        This method sets up the AIModelsBuilder instance to retrieve the model identifier from a specified configuration file. It reads the identifier from the given section and key within the configuration file and sets it for the builder instance.

        Returns:
            AIModelsBuilder: The instance of the AIModelsBuilder class itself, allowing for method chaining.

        Example:
            ~~~python
            builder.with_config_file('model_config.ini', 'id', 'model_id').set_config_file_identifier()
            ~~~
        """
        self.method = 'set_config_file_identifier'
        return self

    @set_method_call
    def set_env_identifier(self) -> 'AIModelsBuilder':
        """
        Set the model identifier from an environment variable.

        This method sets up the AIModelsBuilder instance to retrieve the model identifier from a specified environment variable. It reads the identifier from the environment variable and sets it for the builder instance.

        Returns:
            AIModelsBuilder: The instance of the AIModelsBuilder class itself, allowing for method chaining.

        Example:
            ~~~python
            builder.with_env("env_var").set_env_identifier()
            ~~~
        """
        self.method = 'set_env_identifier'
        return self

    @set_method_call
    def build(self) -> 'AIModelsBuilder':
        """
        Finalizes the construction of the IoT collection configuration.

        This method prepares the builder to execute the collection by ensuring all necessary configurations are set and validates the overall integrity of the build. It should be called before executing the collection to ensure that the configuration is complete and valid.

        The build process involves checking that mandatory fields such as the device identifier are set. It also ensures that method calls that are incompatible with each other (like `build` and `build_execute`) are not both used.

        Returns:
            AIModelsBuilder: Returns itself to allow for method chaining, enabling further actions like `execute`.

        Raises:
            ValueError: If required configurations are missing or if incompatible methods are used together.

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
    def execute(self) -> Response:
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
            'validate': self._execute_validate,
            'download': self._execute_download,
            'prediction': self._execute_prediction,
            'save': self._execute_save,
            'set_config_file_identifier': self._execute_set_identifier,
            'set_env_identifier': self._execute_env_identifier,
        }

        function = methods.get(self.method)
        if function is None:
            raise ValueError(f'Unsupported method: {self.method}')
        return function()

    def _execute_create(self) -> dict[str, Any]:
        files = self._get_file_data()
        payload = {}
        file_config = self._read_config_file()
        response = send_request(method='post', headers=self.client.headers, url=self.url, json_payload=payload, files=files)
        if response.status_code == 201:
            all_identifiers_response = self.find_all().build().execute()['data']

            all_identifiers_json = all_identifiers_response

            identifiers = [item['identifier'] for item in all_identifiers_json if item['name'] == self.file_name]

            if file_config:
                try:
                    self._read_config_file().get(self.section, self.config_key)
                    file_config.set(self.section, self.config_key, identifiers[0])
                    with open(self.config_file, 'w', encoding='utf-8') as configfile:
                        file_config.write(configfile)
                except configparser.NoOptionError:
                    raise Exception('The "model_id" parameter was not found in the configuration file.')
            elif self.data_env is not None:
                try:
                    env_vars = dotenv_values('.env')
                    if self.data_env not in env_vars:
                        raise Exception('The environment variable was not found in the .env file.')

                    set_key('.env', self.data_env, identifiers[0])

                except KeyError as error:
                    raise Exception('The environment variable was not found in the .env file.') from error
            return {'status_code': response.status_code}
        else:
            return {'status_code': response.status_code, 'error': response.text}

    def _execute_find(self) -> str | dict[str, str | int]:
        response = send_request(method='get', headers=self.client.headers, url=self.url)
        result = {'status_code': response.status_code}
        if response.status_code == 200:
            result['data'] = parse_json(response.text)
        else:
            result['error'] = response.text
        return result

    def _execute_update(self) -> dict[str, Any]:
        files = self._get_file_data()
        response = send_request(method='put', headers=self.client.headers, url=self.url, files=files, data={})
        return handle_basic_response(response)

    def _execute_delete(self) -> dict[str, Any]:
        response = send_request('delete', self.client.headers, self.url)
        return handle_basic_response(response)

    def _execute_validate(self) -> dict[str, Any]:
        files = self._get_file_data()
        payload = {}
        response = send_request('post', self.client.headers, self.url, payload, files)
        return handle_basic_response(response)

    def _execute_download(self) -> dict[str, Any]:
        response = send_request('get', self.client.headers, self.url)
        if response.status_code == 200:
            with open(self.output_file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
        else:
            return {'status_code': response.status_code, 'error': response.text}

    def _execute_prediction(self) -> str | dict[str, str | int]:
        self.client.headers['Content-Type'] = 'application/json'
        payload = json.dumps(self.data_prediction)
        response = send_request(method='post', headers=self.client.headers, url=self.url, data=payload)
        result = {'status_code': response.status_code}
        if response.status_code == 200:
            result['data'] = parse_json(response.text)
        else:
            result['error'] = response.text
        return result

    def _execute_save(self) -> Response | ValueError:
        if self.data_env is not None or self.config_file is not None:
            if self.data_env is not None:
                identifier = dotenv_values('.env')[self.data_env]
                self.identifier = identifier

            elif self.config_file is not None:
                config = configparser.ConfigParser()
                config.read(self.config_file)
                model_id = config.get(self.section, self.config_key, fallback=None)
                self.identifier = model_id

            response = self.find_one().build().execute()
            if response['status_code'] == 200:
                return self.update().build().execute()

            # Create
            return self.create().build().execute()

        return ValueError('The "config file" or env parameter was not found')

    def _execute_set_identifier(self):
        try:
            file_config = self._read_config_file()
            self._read_config_file().get(self.section, self.config_key)
            file_config.set(self.section, self.config_key, self.identifier)
            with open(self.config_file, 'w', encoding='utf-8') as configfile:
                file_config.write(configfile)

        except configparser.NoOptionError as error:
            raise ValueError('The "model_id" parameter was not found in the configuration file.') from error

    def _execute_env_identifier(self):
        try:
            env_vars = dotenv_values('.env')
            if self.data_env not in env_vars:
                raise KeyError('The environment variable was not found in the .env file.')

            set_key('.env', self.data_env, self.identifier)

        except KeyError as error:
            raise ValueError('The environment variable was not found in the .env file.') from error

    def _read_config_file(self) -> ConfigParser | None:
        if self.config_file is not None:
            if os.path.exists(self.config_file):
                config = configparser.ConfigParser()
                config.read(self.config_file)
                return config
            raise ValueError('The configuration file does not exist.')
        return None

    def _get_file_data(self):
        with open(self.full_file_path, 'rb') as file:
            file_data = file.read()
        files = [('modelFile', (self.file_name, file_data, 'application/octet-stream'))]
        return files

    def _validate_builds(self):
        required_methods = {
            'create': ['with_organization_name', 'add_file'],
            'find_one': ['with_organization_name'],
            'find_all': ['with_organization_name'],
            'update': ['with_organization_name', 'add_file'],
            'delete': ['with_organization_name'],
            'validate': ['with_organization_name', 'add_file'],
            'download': ['with_organization_name', 'with_output_file_path'],
            'prediction': ['with_organization_name', 'with_prediction'],
            'save': ['with_organization_name'],
            'set_config_file_identifier': ['with_config_file'],
            'set_env_identifier': ['with_env']
        }

        for method, required in required_methods.items():
            if self.method_calls.count(method) > 0:
                missing_methods = [req for req in required if req not in self.method_calls]
                if missing_methods:
                    raise Exception(f"It is mandatory to use the {', '.join(missing_methods)} method(s) in {method}()")

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
            all_identifiers = self.find_all().build().execute()['data']

            name_identifier = [item['identifier'] for item in all_identifiers if item['name'] == self.find_name]

            if not name_identifier:
                raise Exception(f'File name "{self.find_name}" does not exist')

            return name_identifier[0]

        raise ValueError('A configuration file with identifier, config file, or a find by name is required.')
