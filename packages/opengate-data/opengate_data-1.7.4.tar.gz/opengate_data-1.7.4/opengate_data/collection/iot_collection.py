from datetime import datetime
from typing import Any

from opengate_data.utils.utils import send_request, handle_exception, set_method_call, \
    validate_type


class IotCollectionBuilder:
    """Iot Collection Builder"""

    def __init__(self, opengate_client):
        self.client = opengate_client
        self.headers = self.client.headers
        self.url: str | None = None
        self.requires: dict[str, Any] = {}
        self.device_identifier: str | None = None
        self.version: str | None = None
        self.payload: dict = {"version": "1.0.0", "datastreams": []}
        self.method_calls: list = []

    @set_method_call
    def with_device_identifier(self, device_identifier: str) -> "IotCollectionBuilder":
        """
        Add the device identifier to the constructor and validates the type.

        Args:
            device_identifier (str): The unique identifier for the device.

        Returns:
            IotCollectionBuilder: Returns itself to allow for method chaining.
        
        Example:
            ~~~python
            builder.with_device_identifier('device_identifier')
            ~~~
        """
        validate_type(device_identifier, str, "Device identifier")
        self.device_identifier = device_identifier
        return self

    def with_origin_device_identifier(self, origin_device_identifier: str) -> "IotCollectionBuilder":
        """
        Origin Device Identifier in case of be different that the device Identifier that sends information (included in the URI).

        Add the origin_device_identifier to the constructor and validates the type.

        Args:
            origin_device_identifier (str): The unique identifier for the device.

        Returns:
            IotCollectionBuilder: Returns itself to allow for method chaining.
        
        Example:
            ~~~python
            builder.with_origin_device_identifier('origin_device_identifier')
            ~~~
        """
        validate_type(origin_device_identifier, str, "Origin device identifier")
        self.payload['device'] = origin_device_identifier
        return self

    def with_version(self, version: str) -> "IotCollectionBuilder":
        """
        Indicates the version of the structure

        Add the version to the constructor and validates the type.

        Args:
            version (str): The version string to be set.

        Returns:
            IotCollectionBuilder: Returns itself to allow for method chaining.
        
        Example:
            ~~~python
            builder.with_version('1.0.0')
            ~~~
        """
        validate_type(version, str, "Version")
        self.version = version
        self.payload['version'] = version
        return self

    def with_path(self, path: list[str]) -> "IotCollectionBuilder":
        """
        Identifier of the gateway or gateways that has been used by the asset for sending the information.

        This method adds the path gateway to the constructor and validates the type.

        Args:
            path (list): The list of gateway identifiers.

        Returns:
            IotCollectionBuilder: Returns itself to allow for method chaining.
        
        Example:
            ~~~python
            builder.with_path(["path"])
            ~~~
        """
        validate_type(path, list, "Path")
        for idx, item in enumerate(path):
            validate_type(item, str, f"Path element at index {idx}")

        self.payload['path'] = path
        return self

    def with_device(self, device: str) -> "IotCollectionBuilder":
        """

        Device Identifier in case of be different that the device Identifier that sends information (included in the URI).

        Args:
            device (str): The unique identifier for the device.

        Returns:
            IotCollectionBuilder: Returns itself to allow for method chaining.

        Example:
            ~~~python
                builder.with_device("sub-device-001")
            ~~~
        """
        validate_type(device, str, "Device")
        self.payload['device'] = device
        return self

    def with_trustedboot(self, trustedboot: str) -> "IotCollectionBuilder":
        """
        Indicates that a validation of the Trusted_boot type is required, it is not necessary to enter the value of the field but if you enter it,
        the entire message received by the platform will compare the value of TrustedBoot with the provisioned value, if they are different
        the message will not be collected.

        Add the trustedboot to the constructor and validates the type.

        Args:
            trustedboot (str): The unique identifier for the device.

        Returns:
            IotCollectionBuilder: Returns itself to allow for method chaining.
        
        Example:
            ~~~python
            builder.with_trustedboot("trustedboot")
            ~~~
        """
        validate_type(trustedboot, str, "TrustedBoot")
        self.payload['trustedBoot'] = trustedboot
        return self

    @set_method_call
    def add_datastream_datapoints(self, datastream_id: str, datapoints: list[
        tuple[int | float | bool | dict | list, None | datetime | int]]) -> "IotCollectionBuilder":
        """
        Add the datastream identifier and a list of datapoints with their value and at for data collection.

        add_datastream_datapoints("datastream_identifier", [(value, at)])

        Multiple datastreams can be grouped under a single identifier

        Args:
            datastream_id (str): The identifier for the datastream to which the datapoints will be added.
            datapoints (list[tuple[int | float | bool | dict | list, None | datetime | int, None | datetime | int]]): A list of tuples where each tuple
                represents a datapoint.  Each tuple contains the datapoint value and an optional timestamp ('at'):
                    value: Collected value
                    at: Number with the time in miliseconds from epoch of the measurement. If this field is None, the platform will assign the server current time to the datapoint whe data is received.

        Returns:
            IotCollectionBuilder: Returns itself to allow for method chaining.
        
        Example:
            ~~~python
            builder.add_datastream_datapoints("datastream_identifier_1", [(value1, datetime.now()), (value2, None)])
            builder.add_datastream_datapoints("datastream_identifier_2", [(value3, None), (value4, 1431602523123)])
            ~~~
        """

        validate_type(datastream_id, str, "Identifier")
        validate_type(datapoints, list, "Datastreams")

        dp = [(dp[0], dp[1], None) for dp in datapoints]
        return self.add_datastream_datapoints_with_from(datastream_id, dp)

    @set_method_call
    def add_datastream_datapoints_with_from(self, datastream_id: str, datapoints: list[tuple[
        int | float | bool | dict | list, None | datetime | int, None | datetime | int]]) -> "IotCollectionBuilder":
        """
        Add the datastream identifier and a list of datapoints with their value, at and from for data collection.

        add_datastream_datapoints_with_from("datastream_identifier", [(value, at, from)])

        Multiple datastreams can be grouped under a single identifier

        Args:
            datastream_id (str): The identifier for the datastream to which the datapoints will be added.
            datapoints (list[tuple[int | float | bool | dict, None | datetime | int, None | datetime | int]]): A list of tuples where each tuple
                represents a datapoint.  Each tuple contains the datapoint value and an optional timestamp ('at') ('from):
                    value: Collected value
                    at: Number with the time in miliseconds from epoch of the measurement. If this field is None, the platform will assign the server current time to the datapoint whe data is received.
                    from: Number with the time in miliseconds from epoch of the start period of measurement. This indicates that value is the same within this time interval (from, at).

        Returns:
            IotCollectionBuilder: Returns itself to allow for method chaining.
        
        Example:
            ~~~python
            builder.add_datastream_datapoints_with_from("datastream_identifier_1", [(value, 1431602523123, None), (value, None, None)])
            builder.add_datastream_datapoints_with_from("datastream_identifier_2", [(value, None, datetime.now()), (value, 1431602523123, datetime.now())])
            ~~~
        """
        validate_type(datastream_id, str, "Datastream identifier")
        validate_type(datapoints, list, "Datastreams")

        if not datapoints:
            raise ValueError("Datastream must contain at least one datapoint")

        _samples = []
        for value, at, from_ in datapoints:
            validate_type(value, (int, float, bool, dict, list, str), "Value")
            datapoint = {"value": value}

            if at is not None:
                validate_type(at, (int, datetime), "At")

                if isinstance(at, datetime):
                    at = int(at.timestamp() * 1000)
                datapoint["at"] = at
            if from_ is not None:
                validate_type(from_, (int, datetime), "From")

                if isinstance(from_, datetime):
                    from_ = int(from_.timestamp() * 1000)
                datapoint["from"] = from_
            _samples.append(datapoint)

        existing_ds = next(
            (ds for ds in self.payload['datastreams'] if ds['id'] == datastream_id),
            None)
        if existing_ds:
            existing_ds['datapoints'].extend(_samples)
        else:
            new_ds = {"id": datastream_id, "datapoints": _samples}
            self.payload['datastreams'].append(new_ds)

        return self

    @set_method_call
    def from_dict(self, payload: dict[str, Any]) -> "IotCollectionBuilder":
        """
        Constructs the collection configuration from a dictionary input.

        This method dynamically applies builder methods based on the keys in the input dictionary. It should be used after the `build()` method has been called to ensure that the builder is in a proper state to accept configuration from a dictionary.

        Args:
            payload (dict[str, Any]): The dictionary containing the configuration Args.

        Returns:
            IotCollectionBuilder: Returns itself to allow for method chaining.

        Raises:
            ValueError: If required keys are missing in the payload or if the 'datastreams' field is empty.
        
        Example:
            ~~~python
            builder.build().from_dict({
                'version': '1.0.0',
                'path': ["mews"],
                'trustedBoot': "trustedBoot",
                'origin_device_identifier': 'device123',
                'datastreams': [
                    {'id': 'temp', 'datapoints': [(22, 1609459200000)]}
                ]
            })
            ~~~
        """
        if 'datastreams' not in payload or len(payload['datastreams']) < 1:
            raise ValueError("The 'datastreams' field must be present and contain at least one element.")

        method_mapping = {
            'version': self.with_version,
            'device': self.with_device,
            'origin_device_identifier': self.with_origin_device_identifier,
            'path': self.with_path,
            'trustedBoot': self.with_trustedboot,
            'datastreams': self._process_datastreams_from_dict
        }
        for key, value in payload.items():
            if key in method_mapping:
                method = method_mapping[key]
                method(value)
            else:
                raise ValueError(f"Unsupported key '{key}' in payload")

        return self

    @set_method_call
    def build(self) -> "IotCollectionBuilder":
        """
        Finalizes the construction of the IoT collection configuration.

        This method prepares the builder to execute the collection by ensuring all necessary configurations are set and validates the overall integrity of the build. It should be called before executing the collection to ensure that the configuration is complete and valid.

        The build process involves checking that mandatory fields such as the device identifier are set. It also ensures that method calls that are incompatible with each other (like `build` and `build_execute`) are not both used.

        Returns:
            IotCollectionBuilder: Returns itself to allow for method chaining, enabling further actions like `execute`.

        Raises:
            ValueError: If required configurations are missing or if incompatible methods are used together.

        Note:
            This method should be used as a final step before `execute` to prepare the IoT collection configuration. It does not modify the state but ensures that the builder's state is ready for execution.
        
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
    def to_dict(self) -> dict:
        """
        This method is used to retrieve the entire payload that has been constructed by the builder. The payload
        includes all devices, their respective datastreams, and the datapoints that have been added to each datastream.
        This is particularly useful for inspecting the current state of the payload after all configurations and
        additions have been made, but before any execution actions (like sending data to a server) are taken.

        Returns:
            dict: A dictionary representing the current state of the payload within the IotCollectionBuilder.
                  This dictionary includes all devices, datastreams, and datapoints that have been configured.

        Raises:
            Exception: If the build() method was not called before this method.
        
        Example:
            ~~~python
                builder.build().to_dict()
            ~~~
        """
        if 'build' in self.method_calls:
            if self.method_calls[-2] != 'build':
                raise Exception("The build() method must be called before calling to_dict()")

        return self.payload

    @set_method_call
    def build_execute(self, include_payload: bool = False):
        """
        Executes the IoT collection immediately after building the configuration.

        This method is a shortcut that combines building and executing in a single step. It should be used when you want to build and execute the configuration without modifying the builder state in between these operations.

        It first validates the build configuration and then executes the collection if the validation is successful.

        Args:
            include_payload (bool): Determine if the payload should be included in the response.

        Returns:
            dict: A dictionary containing the execution response which includes the status code and potentially other metadata about the execution.

        Raises:
            ValueError: If `build` has already been called on this builder instance, indicating that `build_execute` is being incorrectly used after `build`.
            Exception: If there are issues during the execution process, including network or API errors.
        

        Example:
            ~~~python
                new_iot_collection_builder().with_device_identifier("entity").with_version("2.0.0").add_datastream_datapoints("device.temperature.value", [(100, None), (50, datetime.now())]).build_execute(True)
            ~~~
        """
        if 'build' in self.method_calls:
            raise ValueError("You cannot use build_execute() together with build()")

        self._validate_builds()
        return self._execute_iot_collection(include_payload)

    @set_method_call
    def execute(self, include_payload: bool = False):
        """
        Executes the IoT collection based on the current configuration of the builder.

        Args:
            include_payload (bool): Determine if the payload should be included in the response.

        Returns:
            Dict: A dictionary containing the execution response which includes the status code and,
                              optionally, the payload. If an error occurs, a string describing the error is returned.
        Raises:
            Exception: If `build()` has not been called before `execute()`, or if it was not the last method invoked prior to `execute()`.

        Example:
            ~~~python
                builder.with_device_identifier("device_identifier").with_version("2.0.0").add_datastream_datapoints("device.temperature.value", [(100, None), (50, datetime.now())]).build().execute(True)
            ~~~
        """
        if 'build' in self.method_calls:
            if self.method_calls.count('build') > 1:
                raise Exception("The 'build()' function can only be called once.")

            if self.method_calls[-2] != 'build':
                raise Exception("The build() function must be the last method invoked before execute.")

        if 'build' not in self.method_calls and 'build_execute' not in self.method_calls:
            raise Exception(
                "You need to use a build() or build_execute() function the last method invoked before execute.")

        return self._execute_iot_collection(include_payload)

    def _process_datastreams_from_dict(self, datastreams: list[dict]) -> "IotCollectionBuilder":
        for ds in datastreams:
            datastream_id = ds.get('id')
            datapoints = ds.get('datapoints', [])
            if not datastream_id or not datapoints:
                raise ValueError("Each datastream must have an 'id' and 'datapoints'")

            formatted_datapoints = [(dp['value'], dp.get('at'), dp.get('from')) for dp in datapoints]
            self.add_datastream_datapoints_with_from(datastream_id, formatted_datapoints)

        return self

    def _validate_builds(self):
        if not self.device_identifier:
            raise ValueError("Device identifier must be set.")

        if self.method_calls.count('with_device_identifier') > 1:
            raise ValueError("It cannot have more than one device identifier.")

        if self.method_calls.count('from_dict') == 0 and not self.payload['datastreams']:
            raise ValueError(
                "The from_dict() or add_datastream_datapoints or add_datastream_datapoints_with_from() from_add method must be called or at least one datastream must be configured.")

    def _execute_iot_collection(self, include_payload):
        try:
            if self.client.url is None:
                base_url = 'https://connector-tcp:9443'
            else:
                base_url = f'{self.client.url}/south'
            url = f'{base_url}/v80/devices/{self.device_identifier}/collect/iot'
            response = send_request(method='post', headers=self.headers, url=url, json_payload=self.payload)
            if response.status_code == 201:
                result = {'status_code': response.status_code}
                if include_payload:
                    result['payload'] = self.payload
                return result
            else:
                result = {'status_code': response.status_code}
                if response.text:
                    result['error'] = response.text
                return result

        except Exception as e:
            return handle_exception(e)
