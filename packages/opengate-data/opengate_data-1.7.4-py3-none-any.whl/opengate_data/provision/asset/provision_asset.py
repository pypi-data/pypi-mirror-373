from flatten_dict import unflatten
from typing import Any
import pandas as pd

from opengate_data.utils.utils import validate_type, send_request, set_method_call, handle_basic_response, parse_json, \
    validate_build_method_calls_execute


class ProvisionAssetBuilder:

    def __init__(self, opengate_client):
        self.client = opengate_client
        if self.client.url is None:
            self.base_url = 'https://frontend:8443/v80/provision/organization'
        else:
            self.base_url = f'{self.client.url}/north/v80/provision/organizations'
        self.flatten: bool = False
        self.identifier: str | None = None
        self.organization_name: str | None = None
        self.utc: bool = False
        self.url: str | None = None
        self.method: str | None = None
        self.method_calls: list = []
        self.payload: dict = {"resourceType": {"_value": {"_current": {"value": "entity.asset"}}}}
        self.full = False

    @set_method_call
    def with_organization_name(self, organization_name: str) -> 'ProvisionAssetBuilder':
        """
         Specify the organization for the asset.

         Args:
             organization_name (str): The organization for the asset.

         Returns:
             ProvisionAssetBuilder: Returns self for chaining.

        Example:
            ~~~python
                builder.with_organization_name('organization_name')
            ~~~
         """
        validate_type(organization_name, str, "Organization Name")
        self.organization_name = organization_name
        return self

    @set_method_call
    def with_identifier(self, identifier: str) -> 'ProvisionAssetBuilder':
        """
         Specify the identifier for the asset.

         Args:
             identifier (str): The identifier for the asset.

         Returns:
             ProvisionAssetBuilder: Returns self for chaining.

        Example:
            ~~~python
                builder.with_identifier('identifier')
            ~~~
         """
        validate_type(identifier, str, "Identifier")
        self.identifier = identifier
        return self

    def with_flattened(self) -> 'ProvisionAssetBuilder':
        """
        Flatten the data

        Returns:
            ProvisionAssetBuilder: Returns itself to allow for method chaining.

        Example:
            ~~~python
                builder.with_flattened()
            ~~~
        """
        self.flatten = True
        return self

    def with_utc(self) -> 'ProvisionAssetBuilder':
        """
        Set UTC flag

        Returns:
            ProvisionAssetBuilder: Returns itself to allow for method chaining.

        Example:
            ~~~python
                builder.with_utc()
            ~~~
        """
        self.utc = True
        return self

    @set_method_call
    def with_provision_identifier(self, identifier: str) -> 'ProvisionAssetBuilder':
        """
         Set provision identifier

         Returns:
             ProvisionAssetBuilder: Returns itself to allow for method chaining.

         Example:
             ~~~python
                 builder.with_provision_identifier("identifier")
             ~~~
         """
        validate_type(identifier, str, "Identifier")
        self.payload["provision.asset.identifier"] = {"_value": {"_current": {"value": identifier}}}
        return self

    @set_method_call
    def with_provision_channel(self, channel: str) -> 'ProvisionAssetBuilder':
        """
        Set provision channel

        Returns:
            ProvisionAssetBuilder: Returns itself to allow for method chaining.

        Example:
            ~~~python
                builder.with_provision_channel("channel")
            ~~~
        """
        validate_type(channel, str, "Channel")
        self.payload["provision.administration.channel"] = {"_value": {"_current": {"value": channel}}}
        return self

    @set_method_call
    def with_provision_service_group(self, service_group: str) -> 'ProvisionAssetBuilder':
        """
        Set provision servicegroup

        Returns:
            ProvisionAssetBuilder: Returns itself to allow for method chaining.

        Example:
            ~~~python
                builder.with_provision_service_group("emptyServiceGroup")
            ~~~
        """
        validate_type(service_group, str, "ServiceGroup")
        self.payload["provision.administration.serviceGroup"] = {"_value": {"_current": {"value": service_group}}}
        return self

    @set_method_call
    def with_provision_organization(self, organization: str) -> 'ProvisionAssetBuilder':
        """
        Set provision organization

        Returns:
            ProvisionAssetBuilder: Returns itself to allow for method chaining.

        Example:
            ~~~python
                builder.with_provision_service_group("organization_name")
            ~~~
        """
        validate_type(organization, str, "Organization")
        self.payload["provision.administration.organization"] = {"_value": {"_current": {"value": organization}}}
        return self

    @set_method_call
    def add_provision_datastream_value(self, datastream: str, value: Any) -> 'ProvisionAssetBuilder':
        """
        Add a datastream value to the payload.

        Args:
            datastream (str): The datastream identifier.
            value (Any): The value to be added. It Can be a primitive type or a complex object.

        Returns:
            ProvisionAssetBuilder: Returns itself to allow for method chaining.

        Example:
            ~~~python
                location_value = {
                    "position": {
                        "coordinates": [
                            -3.66131084,
                            40.458442
                        ]
                    }
                }
                builder.add_provision_datastream_value("provision.asset.location", location_value)
                builder.add_provision_datastream_value("provision.asset.name", "Name")
            ~~~
        """
        validate_type(datastream, str, "Datastream")
        self.payload[datastream] = {"_value": {"_current": {"value": value}}}
        return self

    @set_method_call
    def from_dict(self, dct: dict[str, Any]) -> 'ProvisionAssetBuilder':
        """
        Loads data as a python dictionary. If you want to enter the dictionary in flattened mode, you need to use with_flattened().

        Args:
            dct (dict): The dictionary variable.

        Returns:
            ProvisionBulkBuilder: Returns itself to allow for method chaining.

        Example:
             ~~~python
            # Mode flattened
            builder.with_flattened().from_dict(
                {"resourceType":{"_value":{"_current":{"value":"entity.asset"}}},
                "provision.asset.identifier":{"_value":{"_current":{"value":"identifier"}}},
                "provision.administration.organization":{"_value":{"_current":{"value":"organization"}}},
                "provision.asset.description":{"_value":{"_current":{"value":"Descripcion"}}},
                "provision.administration.channel":{"_value":{"_current":{"value":"default_channel"}}},
                "provision.administration.serviceGroup":{"_value":{"_current":{"value":"emptyServiceGroup"}}},
                "provision.asset.location":{"_value":{"_current":{"value":{"position":{"coordinates":[-3.66131084,40.458442]}}}}},
                "provision.human.name":{"_value":{"_current":{"value":"Name"}}},
                "provision.human.surname":{"_value":{"_current":{"value":"Surname"}}}})

            # Mode without flattened
            builder.from_dict({
                  "resourceType": {
                    "_current": {
                      "value": "entity.asset"
                    }
                  },
                  "provision": {
                    "administration": {
                      "channel": {
                        "_current": {
                          "value": "battery_channel"
                        }
                      },
                      "organization": {
                        "_current": {
                          "value": "battery_organization"
                        }
                      },
                      "serviceGroup": {
                        "_current": {
                          "value": "emptyServiceGroup"
                        }
                      }
                    },
                    "asset": {
                      "identifier": {
                        "_current": {
                          "value": "worker_battery_id"
                        }
                      }
                    }
                  }
                })
            ~~~
        """
        validate_type(dct, dict, "Dict")
        self.payload = dct
        return self

    @set_method_call
    def from_dataframe(self, df: pd.DataFrame) -> "ProvisionAssetBuilder":
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
        data = self._process_dataframe(df)
        self.payload = data[0]
        return self

    @set_method_call
    def find_one(self) -> 'ProvisionAssetBuilder':
        """
        Retrieve a single asset.

        This method sets up the ProvisionAssetBuilder instance to retrieve a specific assey associated with the specified organization and identifier.

        Returns:
            ProvisionAssetBuilder: The instance of the ProvisionDeviceBuilder class itself, allowing for method chaining.

        Example:
            ~~~python
                builder.with_organization_name("organization_name").with_identifier("model_identifier").find_one()
            ~~~
        """
        self.url = f'{self.base_url}/{self.organization_name}/entities/{self.identifier}'
        self.method = 'find'
        return self

    @set_method_call
    def create(self) -> 'ProvisionAssetBuilder':
        """
        Initiates the creation process of a new asset.

        This method prepares the ProvisionAssetBuilder instance to create a new asset.

        Returns:
            ProvisionAssetBuilder: The instance of the ProvisionAssetBuilder class itself, allowing for method chaining.

        Example:
            ~~~python
                builder.with_organization_name("organization_name")
                    .with_provision_identifier("provision_identifier")\
                    .with_provision_organization("provision_organization")\
                    .with_provision_channel("provision_channel")\
                    .with_provision_service_group("provision_service_group")\
                    .add_provision_datastream_value("provision.asset.name", "Name")\
                    .create()
            ~~~
        """
        self.url = f'{self.base_url}/{self.organization_name}/entities'
        self.method = 'create'
        self._set_flatten()
        return self

    @set_method_call
    def update(self) -> 'ProvisionAssetBuilder':
        """
        Update an existing asset.

        This method sets up the ProvisionAssetBuilder instance to update a specific asset associated with the specified organization and identifier.

        You can update an asset with a flattened format sending a PUT request using the URL above. You must replace {identifier} with the identifier of the asset you want to update. Also, it is sent a boolean parameter, flattened, to allow sending a flattened JSON format

        Returns:
            ProvisionAssetBuilder: The instance of the ProvisionAssetBuilder class itself, allowing for method chaining.

        Example:
            dict_flatenned = {"resourceType":{"_value":{"_current":{"value":"entity.asset"}}},
            "provision.asset.identifier":{"_value":{"_current":{"value":"EntityTest"}}},
            "provision.administration.organization":{"_value":{"_current":{"value":"orgnization_name"}}},
            "provision.administration.channel":{"_value":{"_current":{"value":"default_channel"}}},
            "provision.administration.serviceGroup":{"_value":{"_current":{"value":"emptyServiceGroup" }}},

            ~~~python
                builder.with_organization_name("organization_name").with_identifier("model_identifier").with_flattened().from_dict(dict_flatenned).update()
            ~~~
        """
        self.url = f'{self.base_url}/{self.organization_name}/entities/{self.identifier}'
        self.method = 'update'
        self._set_flatten()
        return self

    @set_method_call
    def delete(self) -> 'ProvisionAssetBuilder':
        """
         Delete an existing asset.

         This method sets up the ProvisionAssetBuilder instance to delete a specific asset associated with the specified organization and identifier.

         Returns:
             ProvisionAssetBuilder: The instance of the ProvisionAssetBuilder class itself, allowing for method chaining.

        Example:
            ~~~python
               builder().with_organization('organization_name').with_identifier("identifier").delete()
            ~~~
        """
        self.url = f'{self.base_url}/{self.organization_name}/entities/{self.identifier}'
        self.method = 'delete'
        return self

    @set_method_call
    def modify(self) -> 'ProvisionAssetBuilder':
        """
        Modify an existing asset.

        This method sets up the ProvisionAssetBuilder instance to update a specific asset associated with the specified organization and identifier.

        You can update an asset with a flattened format sending a Patch request using the URL above. You must replace {identifier} with the identifier of the asset you want to update. Also, it is sent a boolean parameter, flattened, to allow sending a flattened JSON format

        Returns:
            ProvisionAssetBuilder: The instance of the ProvisionAssetBuilder class itself, allowing for method chaining.

        Example:
            ~~~python
            dict_flatenned = {"resourceType":{"_value":{"_current":{"value":"entity.asset"}}},
            "provision.asset.identifier":{"_value":{"_current":{"value":"EntityTest"}}},
            "provision.administration.organization":{"_value":{"_current":{"value":"orgnization_name"}}},
            "provision.administration.channel":{"_value":{"_current":{"value":"default_channel"}}},
            "provision.administration.serviceGroup":{"_value":{"_current":{"value":"emptyServiceGroup" }}},

            
            builder.with_organization_name("organization_name").with_identifier("model_identifier").with_flattened().from_dict(dict_flatenned).modify()
            ~~~
        """
        self.url = f'{self.base_url}/{self.organization_name}/entities/{self.identifier}'
        self.method = 'modify'
        self._set_flatten()
        return self

    @set_method_call
    def build(self) -> 'ProvisionAssetBuilder':
        """
        Finalizes the construction of the asset configuration.

        This method prepares the builder to execute the collection by ensuring all necessary configurations are set and validates the overall integrity of the build. It should be called before executing the collection to ensure that the configuration is complete and valid.

        The build process involves checking that mandatory fields such as the device identifier are set. It also ensures that method calls that are incompatible with each other (like `build` and `build_execute`) are not both used.

        Returns:
            ProvisionAssetBuilder: Returns itself to allow for method chaining, enabling further actions like `execute`.

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
            raise ValueError("You cannot use 'build_execute()' together with 'build()'")

        if 'execute' in self.method_calls:
            raise ValueError("You cannot use 'build_execute()' together with 'execute()'")

        self._validate_builds()
        return self.execute()

    @set_method_call
    def execute(self) -> str | dict[str, str | int]:
        """
        Execute the configured asset and return the response.

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
        validate_build_method_calls_execute(self.method_calls)

        methods = {
            'find': self._execute_find,
            'update': self._execute_update,
            'delete': self._execute_delete,
            'create': self._execute_create,
            'modify': self._execute_modify
        }

        function = methods.get(self.method)
        if function is None:
            raise ValueError(f'Unsupported method: {self.method}')
        return function()

    def _execute_find(self) -> dict[str, int | str | Any]:
        response = send_request(method='get', headers=self.client.headers, url=self.url,
                                params={'utc': self.utc, 'flattened': self.flatten})
        result = {'status_code': response.status_code}
        if response.status_code == 200:
            result['data'] = parse_json(response.text)
        else:
            result['error'] = response.text
        return result

    def _execute_create(self) -> dict[str, Any]:
        response = send_request(method='post', headers=self.client.headers, url=self.url, json_payload=self.payload,
                                params={'flattened': self.flatten})
        return handle_basic_response(response)

    def _execute_update(self) -> dict[str, Any]:
        response = send_request(method='put', headers=self.client.headers, url=self.url, json_payload=self.payload,
                                params={'flattened': self.flatten})
        return handle_basic_response(response)

    def _execute_delete(self) -> dict[str, Any]:
        response = send_request(method='delete', headers=self.client.headers, url=self.url, params={'full': self.full})
        return handle_basic_response(response)

    def _execute_modify(self) -> dict[str, Any]:
        response = send_request(method='patch', headers=self.client.headers, url=self.url, json_payload=self.payload, params={'flattened': self.flatten})
        return handle_basic_response(response)

    def _process_dataframe(self, df: pd.DataFrame):
        unflats = []
        for df_dict in df.to_dict(orient='records'):
            if any('_' in key for key in df_dict.keys()):
                unflat = unflatten(df_dict, splitter='underscore')
            elif any('.' in key for key in df_dict.keys()):
                unflat = unflatten(df_dict, splitter='dot')
            else:
                raise ValueError('Column names must be linked with "_" or "."')

            unflat["resourceType"] = {"_current": {"value": "entity.asset"}}
            unflats.append(self._add_underscore_to_current_keys(unflat))
        return unflats

    def _add_underscore_to_current_keys(self, dct: dict):
        for key in list(dct.keys()):
            if isinstance(dct[key], dict):
                self._add_underscore_to_current_keys(dct[key])
            if key == 'current':
                dct[f'_{key}'] = dct.pop(key)

        return dct

    def _set_flatten(self):
        if 'from_dict' in self.method_calls:
            self.flatten = self.flatten
        elif 'from_dataframe' in self.method_calls:
            self.flatten = False
        else:
            self.flatten = True

    def _validate_builds(self):
        provision_methods = [
            'with_provision_identifier', 'with_provision_channel',
            'with_provision_service_group', 'with_provision_organization'
        ]

        input_methods = ['from_dict', 'from_dataframe']
        used_input_methods = [method for method in input_methods if method in self.method_calls]
        used_provision_methods = [method for method in provision_methods if method in self.method_calls]

        if len(used_input_methods) > 1:
            raise ValueError(f"Cannot use multiple input methods together: {', '.join(used_input_methods)}")

        if used_input_methods and used_provision_methods:
            raise ValueError(
                f"Cannot use input methods ({', '.join(used_input_methods)}) together with provision methods ({', '.join(used_provision_methods)})")

        required_methods = {
            'find_one': ['with_organization_name', 'with_identifier'],
            'create': ['with_organization_name'],
            'update': ['with_organization_name', 'with_identifier'],
            'delete': ['with_organization_name', 'with_identifier'],
        }

        for method, required in required_methods.items():
            if self.method_calls.count(method) > 0:
                missing_methods = [req for req in required if req not in self.method_calls]
                if missing_methods:
                    raise Exception(f"It is mandatory to use the {', '.join(missing_methods)} method(s) in {method}()")

        operation_methods = ['create', 'find', 'update', 'delete', 'modify']
        used_operations = [method for method in operation_methods if method in self.method_calls]
        if len(used_operations) > 1:
            raise ValueError(f"Cannot use multiple operation methods together: {', '.join(used_operations)}")

        return self
