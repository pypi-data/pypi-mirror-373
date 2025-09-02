"""  AITransformersBuilder """
import json
import os
import configparser
import mimetypes
from configparser import ConfigParser
from typing import Any
from dotenv import dotenv_values, set_key
import requests
from requests import Response
from opengate_data.utils.utils import validate_type, send_request, set_method_call, handle_basic_response, parse_json


class AITransformersBuilder:
    """ Class transformer builder """

    def __init__(self, opengate_client):
        self.client: str = opengate_client
        if self.client.url is None:
            self.base_url = 'https://ai:9644/ai'
        else:
            self.base_url = f'{self.client.url}/north/ai'
        self.organization_name: str | None = None
        self.identifier: str | None = None
        self.config_file: str | None = None
        self.data_env: str | None = None
        self.section: str | None = None
        self.config_key: str | None = None
        self.data_evaluate: dict = {}
        self.url: str | None = None
        self.requires: dict = {}
        self.method: str | None = None
        self.name: str | None = None
        self.find_name: str | None = None
        self.output_file_path: str | None = None
        self.file_name: str | None = None
        self.files: list = []
        self.builder: bool = False
        self.method_calls: list = []

    @set_method_call
    def with_organization_name(self, organization_name: str) -> 'AITransformersBuilder':
        """
        Specify the organization name.

        Args:
            organization_name (str): The name of the organization.

        Returns:
            AITransformersBuilder: Returns self for chaining.

        Example:
            ~~~python
                builder.with_organization_name('organization_name')
            ~~~
        """
        validate_type(organization_name, str, "Organization name")
        self.organization_name = organization_name
        return self

    @set_method_call
    def with_identifier(self, identifier: str) -> 'AITransformersBuilder':
        """
         Specify the identifier for the pipeline.

         Args:
             identifier (str): The identifier for the pipeline.

         Returns:
             AITransformersBuilder: Returns self for chaining.

        Example:
            ~~~python
                builder.with_identifier('identifier')
            ~~~
         """
        validate_type(identifier, str, "Identifier")
        self.identifier = identifier
        return self

    @set_method_call
    def with_env(self, data_env: str) -> 'AITransformersBuilder':
        """
        Specify the environment variable.

        Args:
            data_env (str): The environment variable.

        Returns:
            AITransformersBuilder: Returns self for chaining.

        Example:
            ~~~python
                builder.with_env('TRANSFORMER_ID')
            ~~~
        """
        validate_type(data_env, str, "Env")
        self.data_env = data_env
        return self

    @set_method_call
    def with_config_file(self, config_file: str, section: str, config_key: str) -> 'AITransformersBuilder':
        """
        This method allows specifying a configuration file, a section within that file,
        and a key to retrieve a specific value from the section.

        Args:
            config_file (str): The path to the.ini configuration file.
            section (str): The section name within the.ini file where the desired configuration is located.
            config_key (str): The key within the specified section whose value will be retrieved.

        Raises:
            TypeError: If the provided config_file is not a string.
            TypeError: If the provided section is not a string.
            TypeError: If the provided config_key is not a string.
        Returns:
            AITransformersBuilder

        Example:
            ~~~python
                [id]
                model_id = afe07216-14ec-4134-97ae-c483b11d965a

                config_file_path = os.path.join(os.path.dirname(__file__), 'config_test.ini')
                builder.with_config_file(config_file_path, 'id', 'model_id')
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
    def add_file(self, file_path: str, filetype: str = None):
        """
        Adds a file to the transformer resource.

        This method allows specifying one or more files to be included in the transformer resource being created. The content type for each file can be specified if needed.

        Args:
            file_path (str): Full path to the file to add.
            filetype (str, optional): Content type of the file. Defaults to None, meaning the content type will be automatically inferred.

        Returns:
            AITransformersBuilder: Returns the current instance to allow method chaining.

        Example:
            ~~~python
                ai_transformer_create = client.ai_transformers_builder().with_organization('ManuCorp')\
                  .add_file('exittransformer.py', 'text/python')\
                  .add_file('pkl_encoder.pkl')
            ~~~
        """
        if not os.path.isabs(file_path):
            validate_type(file_path, str, "File path")
            file_path = os.path.join(os.getcwd(), file_path)

        if filetype is None:
            filetype = self._get_file_type(file_path)
        else:
            validate_type(filetype, str, "File type")

        self.files.append((file_path, filetype))
        return self

    @set_method_call
    def with_find_by_name(self, find_name: str) -> 'AITransformersBuilder':
        """
        Specify the name to find.

        Args:
            find_name (str): The name of the transformer.

        Returns:
            AITransformersBuilder: Returns self for chaining.

        Example:
            ~~~python
                builder.with_find_by_name('transformer_name')
            ~~~
        """
        validate_type(find_name, str, "Find name")
        self.find_name = find_name
        return self

    @set_method_call
    def with_evaluate(self, data_evaluate: dict) -> 'AITransformersBuilder':
        """
         Evaluate with transformer

         Args:
             data_evaluate (dict): Evaluate

         Raises:
             TypeError: If to evaluate is not a dict.

         Returns:
             AITransformersBuilder: Returns itself to allow for method chaining.

        Example:
            ~~~python
                evaluate_data = {
                  "data": {
                    "PPLast12H": 0,
                    "PPLast24H": 0,
                    "PPLast72H": 1,
                    "currentTemp": -2,
                    "changeTemp": -2
                  },
                  "date": "2022-06-13T13:59:34.779+02:00"
                }
                 builder.with_evaluate(evaluate_data)
            ~~~
         """
        validate_type(data_evaluate, dict, "Evaluate")
        self.data_evaluate = data_evaluate
        return self

    @set_method_call
    def with_output_file_path(self, output_file_path: str) -> 'AITransformersBuilder':
        """
        Sets the output file path for the transformer.

        This method allows you to specify the path where the output file will be saved.
        It is particularly useful for operations that involve downloading or saving files.

        Args:
            output_file_path (str): The path where the output file will be saved.

        Returns:
            AITransformersBuilder: The instance of the AIModelsBuilder class.

        Example:
            ~~~python
                builder.with_output_file_path("rute/prueba.onnx")
            ~~~
        """
        validate_type(output_file_path, str, "Output file path")
        self.output_file_path = output_file_path
        return self
    
    @set_method_call
    def with_file_name(self, file_name: str) -> 'AITransformersBuilder':
        """
        Specifies the name of the file to be processed.

        This method allows you to specify the name of the file that will be used in operations such as download or evaluation. It is particularly useful when working with specific files that require unique identifiers or names for processing.

        Args:
            file_name (str): The name of the file to be processed.

        Returns:
            AITransformersBuilder: Returns self for chaining.

        Example:
            ~~~python
                builder.with_file_name('pkl_encoder.pkl')
            ~~~
        """
        validate_type(file_name, str, "File name")
        self.file_name = file_name
        return self

    @set_method_call
    def create(self) -> 'AITransformersBuilder':
        """
        Prepares the creation of the transformer resource.

        Returns:
            AITransformersBuilder: Returns the current instance to allow method chaining.

        Example:
            ~~~python
                builder.with_organization('Organization').add_file('exittransformer.py', 'text/python').add_file('pkl_encoder.pkl').create()\
            ~~~
        """
        self.url = f'{self.base_url}/{self.organization_name}/transformers'
        self.method = 'create'
        return self

    @set_method_call
    def find_all(self) -> 'AITransformersBuilder':
        """
        Searches for all available transformer resources.

        Returns:
            AITransformersBuilder: Returns the current instance to allow method chaining.

        Example:
            ~~~python
                builder.with_organization_name('my_organization').find_all()
            ~~~
        """
        self.url = f'{self.base_url}/{self.organization_name}/transformers'
        self.method = 'find'
        return self

    @set_method_call
    def find_one(self) -> 'AITransformersBuilder':
        """
        Searches for a single transformer resource by its identifier.

        This method prepares the request to find a specific transformer based on its identifier. The identifier is obtained automatically if not explicitly defined or can be obtained from a configuration file or environment variables.

        Returns:
            AITransformersBuilder: Returns the current instance to allow method chaining.

        Example:
            ~~~python
                builder.with_organization_name('my_organization').with_identifier('identifier').find_one()
            ~~~
        """
        identifier = self._get_identifier()
        self.url = f'{self.base_url}/{self.organization_name}/transformers/{identifier}'
        self.method = 'find'
        return self
    
    @set_method_call
    def update(self) -> 'AITransformersBuilder':
        """
        Updates an existing transformer resource.

        This method prepares the URL and HTTP method necessary to send a PUT request to the API to update an existing transformer. It is necessary to configure the relevant attributes of the `AITransformersBuilder` instance, including the `identifier` of the transformer to update, before calling this method.

        Returns:
            AITransformersBuilder: Returns the current instance to allow method chaining.

        Example:
            ~~~python
                builder.with_organization_name('my_organization').with_identifier('identifier').update()
            ~~~
        """
        identifier = self._get_identifier()
        self.url = f'{self.base_url}/{self.organization_name}/transformers/{identifier}'
        self.method = 'update'
        return self

    @set_method_call
    def delete(self) -> 'AITransformersBuilder':
        """
        Deletes an existing transformer resource.

        This method prepares the URL and HTTP method necessary to send a DELETE request to the API to delete an existing transformer. It is necessary to configure the `identifier` attribute of the `AITransformersBuilder` instance before calling this method.

        Returns:
            AITransformersBuilder: Returns the current instance to allow method chaining.

        Example:
            ~~~python
                builder.with_organization_name('my_organization').with_identifier('identifier').delete()
            ~~~
        """
        identifier = self._get_identifier()
        self.url = f'{self.base_url}/{self.organization_name}/transformers/{identifier}'
        self.method = 'delete'
        return self

    @set_method_call
    def download(self) -> 'AITransformersBuilder':
        """
        Download the model file.

        This method sets up the AIModelsBuilder instance to download the file of a specific model associated with the specified organization and identifier. It configures the URL endpoint for the download operation and sets the operation type to 'download'.

        Returns:
            AITransformersBuilder: The instance of the AIModelsBuilder class itself, allowing for method chaining.

        Example:
            ~~~python
                builder.with_organization_name("MyOrganization").with_identifier("model_identifier").with_output_file_path("model.onnx").download().build().execute()
                builder.with_organization_name("MyOrganization").with_find_by_name("model_name.onnx").with_output_file_path("model.onnx").download().build().execute()
                config_file_path = os.path.join(os.path.dirname(__file__), 'config_test.ini')
                builder.with_organization_name("MyOrganization").with_config_file(config_file_path, 'id', 'model').with_output_file_path("model.onnx").download().build().execute()
            ~~~
        """
        identifier = self._get_identifier()
        self.url = f'{self.client.url}/north/ai/{self.organization_name}/transformers/{identifier}/{self.file_name}'
        self.method = 'download'
        return self

    @set_method_call
    def evaluate(self) -> 'AITransformersBuilder':
        """
        Prepares the evaluation of the transformer with provided data.

        This method sets up the URL and method for evaluating the transformer using the provided data. The evaluation data should be set using the `with_evaluate` method before calling this method.

        Returns:
            AITransformersBuilder: Returns the current instance to allow method chaining.

        Example:
            ~~~python
                builder.with_organization_name('my_organization').with_identifier('identifier').with_evaluate(evaluate_data).evaluate()
            ~~~
        """
        identifier = self._get_identifier()
        self.url = f'{self.base_url}/{self.organization_name}/transformers/{identifier}/transform'
        self.method = 'evaluate'
        return self

    @set_method_call
    def save(self) -> 'AITransformersBuilder':
        """
        Saves the transformer configuration.

        This method prepares the URL and method for saving the transformer configuration. It checks if the identifier is set from the environment or configuration file and then either updates or creates the transformer accordingly.

        Returns:
            AITransformersBuilder: Returns the current instance to allow method chaining.

        Example:
            ~~~python
                builder.with_organization_name('my_organization').with_env('TRANSFORMER_ID').save()
            ~~~
        """
        self.method = 'save'
        return self

    @set_method_call
    def set_config_file_identifier(self) -> 'AITransformersBuilder':
        """
        Sets the transformer identifier in the configuration file.

        This method sets the transformer identifier in the specified configuration file. It reads the configuration file, updates the identifier, and writes the changes back to the file.

        Returns:
            AITransformersBuilder: Returns the current instance to allow method chaining.

        Example:
            ~~~python
                config_file_path = os.path.join(os.path.dirname(__file__), 'config_test.ini')
                builder.with_config_file(config_file_path, 'id', 'transformer_id').set_config_file_identifier()
            ~~~
        """
        self.method = 'set_config_identifier'
        return self
    
    @set_method_call
    def set_env_identifier(self) -> 'AITransformersBuilder':
        """
        Sets the transformer identifier in the environment variables.

        This method sets the transformer identifier in the specified environment variable. It reads the environment variable, updates the identifier, and writes the changes back to the environment file.

        Returns:
            AITransformersBuilder: Returns the current instance to allow method chaining.

        Example:
            ~~~python
                builder.with_env('TRANSFORMER_ID').set_env_identifier()
            ~~~
        """
        self.method = 'set_env_identifier'
        return self

    @set_method_call
    def set_env_identifier(self) -> 'AITransformersBuilder':
        """
        Set the model identifier from an environment variable.

        This method sets up the AITransformersBuilder instance to retrieve the model identifier from a specified environment variable. It reads the identifier from the environment variable and sets it for the builder instance.

        Returns:
            AITransformersBuilder: The instance of the AITransformersBuilder class itself, allowing for method chaining.

        Example:
            ~~~python
            builder.with_env("env_var").set_env_identifier()
            ~~~
        """
        self.method = 'set_env_identifier'
        return self

    @set_method_call
    def build(self) -> 'AITransformersBuilder':
        """
        Finalizes the construction of the IoT collection configuration.

        This method prepares the builder to execute the collection by ensuring all necessary configurations are set and validates the overall integrity of the build. It should be called before executing the collection to ensure that the configuration is complete and valid.

        The build process involves checking that mandatory fields such as the device identifier are set. It also ensures that method calls that are incompatible with each other (like `build` and `build_execute`) are not both used.

        Returns:
            AITransformersBuilder: Returns itself to allow for method chaining, enabling further actions like `execute`.

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
    def execute(self) -> requests.Response:
        methods = {
            'create': self._execute_create,
            'find': self._execute_find,
            'update': self._execute_update,
            'delete': self._execute_delete,
            'download': self._execute_download,
            'evaluate': self._execute_evaluate,
            'save': self._execute_save,
            'set_config_identifier': self._execute_set_identifier,
            'set_env_identifier': self._execute_env_identifier,
        }

        function = methods.get(self.method)
        if function is None:
            raise ValueError(f'Unsupported method: {self.method}')
        return function()


    def _list_transformers(self):
        url = f'{self.base_url}/{self.organization_name}/transformers'
        response = send_request(method='get', headers=self.client.headers, url=url)
        if response.status_code != 200:
            raise Exception(f'Cannot list transformers: {response.status_code} {response.text}')
        return parse_json(response.text)

    def _transformer_exists(self, identifier: str) -> bool:
        url = f'{self.base_url}/{self.organization_name}/transformers/{identifier}'
        response = send_request(method='get', headers=self.client.headers, url=url)
        return response.status_code == 200

    # 3) _execute_create: evitar build/execute internos y arreglar el elif
    def _execute_create(self) -> dict[str, str | int]:
        file_config = self._read_config_file()
        files_to_upload = self._prepare_files(self.files)
        # Asegura URL correcta por si se llamó desde save()
        self.url = f'{self.base_url}/{self.organization_name}/transformers'
        response = send_request(method='post', headers=self.client.headers, url=self.url, data={}, files=files_to_upload)

        if response.status_code == 201:
            all_identifiers = self._list_transformers()
            python_files = [filename for filename, filetype in self.files if filetype == 'text/python']
            python_file = python_files[0] if python_files else os.path.basename(self.files[0][0])
            filename = os.path.basename(python_file)
            result = next((item for item in all_identifiers if item['name'] == filename), None)

            if result is None:
                return {'status_code': 201}  # creado pero no pudimos mapear el id por nombre

            # → escribir en .ini si procede
            if file_config:
                try:
                    file_config.set(self.section, self.config_key, result['identifier'])
                    with open(self.config_file, 'w', encoding='utf-8') as configfile:
                        file_config.write(configfile)
                except configparser.NoOptionError as error:
                    raise ValueError('The "transformer_id" parameter was not found in the configuration file.') from error

            # → escribir en .env si procede
            if self.data_env is not None:
                env_vars = dotenv_values('.env')
                if self.data_env not in env_vars:
                    raise ValueError('The environment variable was not found in the .env file.')
                set_key('.env', self.data_env, result['identifier'])

            return {'status_code': response.status_code}

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

    def _execute_update(self) -> dict[str, Any]:
        files_to_upload = self._prepare_files(self.files)
        payload = {}
        response = send_request(method='put', headers=self.client.headers, url=self.url, json_payload=payload, files=files_to_upload)
        return handle_basic_response(response)

    def _execute_delete(self) -> dict[str, Any]:
        response = send_request(method='delete', headers=self.client.headers, url=self.url)
        return handle_basic_response(response)

    def _execute_download(self) -> dict[str, str | int]:
        response = send_request(method='get', headers=self.client.headers, url=self.url)

        if response.status_code == 200:
            with open(self.output_file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
        else:
            return {'status_code': response.status_code, 'error': response.text}

    def _execute_evaluate(self) -> dict[str, Any]:
        self.client.headers['Content-Type'] = 'application/json'
        response = send_request(method='post', headers=self.client.headers, url=self.url, data=json.dumps(self.data_evaluate))
        return handle_basic_response(response)
    
    def _execute_save(self) -> Response | ValueError:
        if self.data_env is not None or self.config_file is not None:
            if self.data_env is not None:
                self.identifier = dotenv_values('.env').get(self.data_env)
            else:
                config = configparser.ConfigParser()
                config.read(self.config_file)
                self.identifier = config.get(self.section, self.config_key, fallback=None)

            exists = bool(self.identifier) and self._transformer_exists(self.identifier)

            if exists:
                # update
                self.url = f'{self.base_url}/{self.organization_name}/transformers/{self.identifier}'
                return self._execute_update()
            else:
                # create
                self.url = f'{self.base_url}/{self.organization_name}/transformers'
                return self._execute_create()

        return ValueError('The "config file" or env parameter was not found')


    def _execute_set_identifier(self) -> ValueError | None:
        try:
            cfg = self._read_config_file()
            cfg.get(self.section, self.config_key)
            cfg.set(self.section, self.config_key, self.identifier)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                cfg.write(f)
            return None
        except configparser.NoOptionError:
            return ValueError(f'The "{self.config_key}" parameter was not found in the configuration file.')


    def _execute_env_identifier(self) -> None:
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
                config: configparser.ConfigParser = configparser.ConfigParser()
                config.read(self.config_file)
                return config
            raise ValueError('The configuration file does not exist.')
        return None

    def _get_identifier(self) -> str:
        if self.identifier is not None:
            return self.identifier

        if self.data_env is not None:
            config = dotenv_values()
            identifier = config.get(self.data_env)
            if identifier is None:
                raise ValueError('The parameter was not found in the configuration env')
            return identifier

        if self.config_file is not None and self.section is not None and self.config_key is not None:
            config = self._read_config_file()
            try:
                return config.get(self.section, self.config_key)
            except configparser.NoOptionError:
                raise ValueError('The "transformer_id" parameter was not found in the configuration file.')

        if self.find_name is not None:
            all_identifiers = self._list_transformers()
            name_identifier = [item['identifier'] for item in all_identifiers if item['name'] == self.find_name]
            if not name_identifier:
                raise Exception(f'File name "{self.find_name}" does not exist')
            return name_identifier[0]

        raise ValueError('A configuration file with identifier, a transformer identifier, or a find by name is required.')


    def _validate_builds(self):
        required_methods = {
            'create': ['with_organization_name', 'add_file'],
            'find_one': ['with_organization_name'],
            'find_all': ['with_organization_name'],
            'update': ['with_organization_name', 'add_file'],
            'delete': ['with_organization_name'],
            'validate': ['with_organization_name', 'add_file'],
            'download': ['with_organization_name', 'with_file_name', 'with_output_file_path'],
            'evaluate': ['with_organization_name', 'with_evaluate'],
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
    
    @staticmethod
    def _get_file_type(file_path: str) -> str:
        filename = os.path.basename(file_path)
        type_guess = mimetypes.guess_type(filename)[0]

        if filename.endswith('.py'):
            return 'text/python'

        return type_guess if type_guess else 'application/octet-stream'

    @staticmethod
    def _prepare_files(files: list) -> list:
        files_to_upload = []
        for file_obj in files:
            file_path, file_type = file_obj
            with open(file_path, 'rb') as file:
                file_data = file.read()
            file_entry = (
                'files', (os.path.basename(file_path), file_data, file_type))
            files_to_upload.append(file_entry)
        return files_to_upload
