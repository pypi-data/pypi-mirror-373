import json
import os
from datetime import datetime
from typing import Any

import pandas as pd

from opengate_data.utils.utils import send_request, handle_exception, validate_type, set_method_call, parse_json


class IotBulkCollectionBuilder:
    """ Collection Bulk Builder """

    def __init__(self, opengate_client):
        self.client = opengate_client
        self.headers = self.client.headers
        self.requires: dict[str, Any] = {}
        self.device_identifier: str | None = None
        self.version: str | None = None
        self.payload: dict = {"devices": {}}
        self.method_calls: list = []

    @set_method_call
    def add_device_datastream_datapoints(self, device_id: str, datastream_id: str, datapoints: list[
        tuple[int | float | bool | dict, None | datetime | int]]) -> "IotBulkCollectionBuilder":
        """
        Add device identifier with the datastream identifier and a list of datapoints with their value and at for data collection.

        Args:
            device_id (str): The identifier for the device.
            datastream_id (str): The identifier for the datastream within the device.
            datapoints (list): A list of tuples, where each tuple contains the data value and the timestamp
                               at which the data was recorded. The tuple structure is (value, at).
        Returns:
            IotBulkCollectionBuilder: Returns itself to allow for method chaining.

        Example:
            ~~~python
                builder.add_device_datastream_datapoints('device123', 'temperature', [(22.5, 1609459200)])
            ~~~
        """

        dp = [(dp[0], dp[1], None) for dp in datapoints]
        return self.add_device_datastream_datapoints_with_from(device_id, datastream_id, dp)

    @set_method_call
    def add_device_datastream_datapoints_with_from(self, device_id: str, datastream_id: str, datapoints: list[
        tuple[int | float | bool | dict, None | datetime | int, None | datetime | int]]) -> "IotBulkCollectionBuilder":
        """
        Add device identifier with the datastream identifier and a list of datapoints with their value with at and from for data collection.
        they are created. This method also handles the inclusion of timestamps for when the data was recorded
        ('at') and when it was transmitted ('from').

        Args:
            device_id (str): The identifier for the device.
            datastream_id (str): The identifier for the datastream within the device.
            datapoints (list): A list of tuples, where each tuple contains the data value, the timestamp
                               at which the data was recorded, and the timestamp from which the data was sent.
                               The tuple structure is (value, at, from).
        Raises:
            ValueError: If the datapoints list is empty, indicating that no data is being added.

        Returns:
            IotBulkCollectionBuilder: Returns the instance of the class to allow for method chaining.

        Example:
            ~~~python
                builder.add_device_datastream_datapoints_with_from('device123', 'temperature', [(22.5, 1609459200, 1609459300)])
            ~~~
        """
        validate_type(device_id, str, "Device identifier")
        validate_type(datastream_id, str, "Datastream identifier")
        validate_type(datapoints, list, "Datastreams")
        if not datapoints:
            raise ValueError("Datastream must contain at least one datapoint")

        if device_id not in self.payload['devices']:
            self.payload['devices'][device_id] = {
                "datastreams": [],
                "version": None,
                "origin_device": None
            }

        if self.payload['devices'][device_id]['version'] is None:
            self.payload['devices'][device_id]['version'] = "1.0.0"

        device_data = self.payload['devices'][device_id]
        datastream = next((ds for ds in device_data['datastreams'] if ds['id'] == datastream_id), None)
        if not datastream:
            datastream = {"id": datastream_id, "datapoints": []}
            device_data['datastreams'].append(datastream)

        for value, at, from_ in datapoints:
            validate_type(at, (type(None), datetime, int), "At")

            validate_type(from_, (type(None), datetime, int), "From")

            datapoint = {"value": value}
            if at is not None:
                datapoint["at"] = int(at.timestamp() * 1000) if isinstance(at, datetime) else at
            if from_ is not None:
                datapoint["from"] = int(from_.timestamp() * 1000) if isinstance(from_, datetime) else from_
            datastream['datapoints'].append(datapoint)

        return self

    @set_method_call
    def from_dataframe(self, df: pd.DataFrame) -> "IotBulkCollectionBuilder":
        """
        Processes a DataFrame to extract device, data and datapoints, and adds them to the payload.

        Args:
            df (pd.DataFrame): The DataFrame containing the device data and datapoints. The DataFrame
                               is expected to have columns that match the expected structure for device
                               datastreams and datapoints.
        Returns:
            IotBulkCollectionBuilder: Returns itself to allow for method chaining.

        Example:
            ~~~python
                import pandas as pd

                df = pd.DataFrame({
                     'device_id': ['device'], ['device2'],
                     'datastream': ['1'],['2'],
                     'value': [value, value2],
                     'at': [datetime.now(), 2000]
                })
                builder.from_dataframe(df)
            ~~~
        """
        validate_type(df, pd.DataFrame, "Dataframe")
        self._process_dataframe(df)
        return self

    @set_method_call
    def from_spreadsheet(self, path: str, sheet_name_index: int | str) -> "IotBulkCollectionBuilder":
        """
        Loads data from a spreadsheet, processes it, and adds the resulting device data and datapoints
        to the payload. This method is particularly useful for bulk data operations where data is
        stored in spreadsheet format.

        Args:
            path (str): The file path to the spreadsheet to load.
            sheet_name_index (int | str): The sheet name or index to load from the spreadsheet.

        Returns:
            IotBulkCollectionBuilder: Returns itself to allow for method chaining.

        Example:
            ~~~python
                builder.from_spreadsheet("file.xslx", "sheet_name)
                builder.from_spreadsheet("file.xslx", 1)
            ~~~
        """
        validate_type(path, str, "Path")
        validate_type(sheet_name_index, (int, str), "Sheet name index")

        absolute_path = os.path.abspath(path)
        df = pd.read_excel(absolute_path, sheet_name=sheet_name_index)
        df.columns = df.columns.str.lower().str.replace(' ', '_')

        df['value'] = df['value'].apply(parse_json)

        if 'at' in df.columns:
            df['at'] = pd.to_datetime(df['at'], errors='coerce', utc=True, format="mixed")
        if 'from' in df.columns:
            df['from'] = pd.to_datetime(df['from'], errors='coerce', utc=True, format="mixed")

        if 'path' in df.columns:
            df['path'] = df['path'].apply(lambda x: [str(item) for item in json.loads(x)] if isinstance(x, str) else x)

        self._process_dataframe(df)
        return self

    @set_method_call
    def build(self) -> 'IotBulkCollectionBuilder':
        """
         Finalizes the construction of the entities search configuration.

         This method prepares the builder to execute the collection by ensuring all necessary configurations are set and validates the overall integrity of the build. It should be called before executing the collection to ensure that the configuration is complete and valid.

         The build process involves checking that mandatory fields such as the device identifier are set. It also ensures that method calls that are incompatible with each other (like `build` and `build_execute`) are not both used.

         Returns:
             IotBulkCollectionBuilder: Returns itself to allow for method chaining, enabling further actions like `execute`.

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
    def build_execute(self, include_payload=False):
        """
        This method is a shortcut that combines building and executing in a single step.

        Returns:
            dict: A dictionary containing the execution response which includes the status code and potentially other metadata about the execution.

        Raises:
            ValueError: If `build` has already been called on this builder instance.

        Example:
            ~~~python
            import pandas as pd
            from datetime import datetime

            data = {
                    "device_id": ['entity'],
                    "data_stream_id": ["device.temperature.value"],
                    "origin_device_identifier": ['entity2'],
                    "value": [40],
                    "version": ["4.0.0"],
                    "path": ["entityTesting3"],
                    "at": [datetime.now()],
                    "from": [datetime.now()],
                }
                new_iot_bulk_collection_builder().from_dataframe(df).from_spreadsheet("collect.xslx",0).add_device_datastream_datapoints_with_from("device_identifier", "device.temperature.value", [(300, datetime.now(), datetime.now())])
                               .add_device_datastream_datapoints("entity", "device.temperature.value", [(300, datetime.now())])
                               .build_execute()
            ~~~
        """

        if 'build' in self.method_calls:
            raise ValueError("You cannot use build_execute() together with build()")

        if 'execute' in self.method_calls:
            raise ValueError("You cannot use build_execute() together with execute()")

        self._validate_builds()
        self._execute_bulk_iot_collection(include_payload)

        return self._execute_bulk_iot_collection(include_payload)

    @set_method_call
    def to_dict(self) -> dict:
        """
        This method is used to retrieve the entire payload that has been constructed by the builder. The payload
        includes all devices, their respective datastreams, and the datapoints that have been added to each datastream.
        This is particularly useful for inspecting the current state of the payload after all configurations and
        additions have been made, but before any execution actions (like sending data to a server) are taken.

        Returns:
            dict: A dictionary representing the current state of the payload within the IotBulkCollectionBuilder.
                  This dictionary includes all devices, datastreams, and datapoints that have been configured.

        Raises:
            Exception: If the build method was not called before this method.

        Example:
            ~~~python
                builder.to_dict()
            ~~~
        """
        if 'build' in self.method_calls:
            if self.method_calls[-2] != 'build':
                raise Exception("The build() method must be called before calling to_dict()")

        return self.payload

    @set_method_call
    def execute(self, include_payload=False):
        """
        Executes the IoT collection based on the current configuration of the builder.

        Args:
            include_payload (bool): Determine if the payload should be included in the response.

        Returns:
            dict: A dictionary containing the results of the execution, including success messages for each device ID
                  if the data was successfully sent, or error messages detailing what went wrong.

        Raises:
            Exception: If `build()` has not been called before `execute()`, or if it was not the last method invoked prior to `execute()`.

        Example:
            ~~~python
            import pandas as pd
            from datetime import datetime

            data = {
                    "device_id": ['entity', entity2],
                    "data_stream_id": ["device.temperature.value", "device.name"],
                    "origin_device_identifier": ['entity2', None],
                    "value": [40, "Name"],
                    "version": ["4.0.0", "2.0.0],
                    "path": ["entityTesting3", entityTesting4],
                    "at": [datetime.now(), datetime.now()],
                    "from": [datetime.now(), datetime.now()],
                }
                builder.new_iot_bulk_collection_builder().from_dataframe(df).from_spreadsheet("collect.xslx",0).add_device_datastream_datapoints_with_from("device_identifier", "device.temperature.value", [(300, datetime.now(), datetime.now())])
                               .add_device_datastream_datapoints("entity", "device.temperature.value", [(300, datetime.now())])
                               .build().execute())
            ~~~
        """

        if 'build' in self.method_calls:
            if self.method_calls[-2] != 'build':
                raise Exception("The build() function must be the last method invoked before execute.")

        if 'build' not in self.method_calls and 'build_execute' not in self.method_calls:
            raise Exception(
                "You need to use a build() or build_execute() function the last method invoked before execute.")

        results = self._execute_bulk_iot_collection(include_payload)
        return results

    def _execute_bulk_iot_collection(self, include_payload):
        results = {}
        errors = {}
        for device_id, device_data in self.payload.get('devices', {}).items():
            try:
                if self.client.url is None:
                    base_url = 'https://connector-tcp:9443'
                else:
                    base_url = f'{self.client.url}/south'
                url = f'{base_url}/v80/devices/{device_id}/collect/iot'
                response = send_request(method='post', headers=self.headers, url=url, json_payload=device_data)
                if response.status_code == 201:
                    result = {'status_code': response.status_code}
                    if include_payload:
                        result['payload'] = device_data
                    results[device_id] = result
                else:
                    errors[device_id] = {'error': 'HTTP error', 'code': response.status_code, 'message': response.text}

            except Exception as e:
                return handle_exception(e)

        if errors:
            error_messages = "; ".join(
                f"{key}: (Error: {value['error']}, Status code: {value['code']}), {value['message']}" for key, value in
                errors.items()
            )
            if results:
                results.items()
                raise Exception(
                    f"The following entities were executed successfully: {results}. However, errors occurred for these entities: {error_messages}.")
            else:
                raise Exception(f"Errors occurred for these entities: {error_messages}")
        else:
            return results

    def _process_dataframe(self, df: pd.DataFrame):
        required_columns = ['device_id', 'data_stream_id', 'value']
        optional_columns = ['origin_device_identifier', 'version', 'path', 'trustedboot', 'at', 'from']

        if not set(required_columns).issubset(df.columns):
            missing_cols = set(required_columns) - set(df.columns)
            raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")

        for index, row in df.iterrows():
            device_id = row['device_id']
            datastream_id = row['data_stream_id']
            value = row['value']
            at = row.get('at', None)
            from_ = row.get('from', None)

            validate_type(device_id, str, "Device ID")
            validate_type(datastream_id, str, "Data Stream ID")
            validate_type(value, (int, str, float, bool, dict, list), "Value")

            if device_id not in self.payload['devices']:
                device_config = {
                    "datastreams": []
                }
                for field in optional_columns:
                    if field in df.columns and (
                            pd.Series(row[field]).notna().any() if isinstance(row[field], list) else pd.notna(
                                row[field])):
                        if field != 'at' and field != 'from':
                            device_config[field] = row[field]

                self.payload['devices'][device_id] = device_config

                if 'version' not in device_config or device_config['version'] is None:
                    device_config['version'] = "1.0.0"

            if 'origin_device_identifier' in df.columns and pd.notna(row['origin_device_identifier']):
                self.payload['devices'][device_id]['device'] = row['origin_device_identifier']
                if 'origin_device_identifier' in self.payload['devices'][device_id]:
                    del self.payload['devices'][device_id]['origin_device_identifier']

            datapoint = {"value": value}

            if pd.notna(at):
                if isinstance(at, float):
                    at = int(at)
                validate_type(at, (type(None), datetime, int), "At")
                if isinstance(at, datetime):
                    datapoint["at"] = int(at.timestamp() * 1000)
                else:
                    datapoint["at"] = at
            if pd.notna(from_):
                if isinstance(from_, float):
                    from_ = int(from_)
                validate_type(from_, (type(None), datetime, int), "From")
                if isinstance(from_, datetime):
                    datapoint["from"] = int(from_.timestamp() * 1000)
                else:
                    datapoint["from"] = from_

            existing_ds = next(
                (ds for ds in self.payload['devices'][device_id]['datastreams'] if ds['id'] == datastream_id), None)
            if existing_ds:
                existing_ds['datapoints'].append(datapoint)
            else:
                new_ds = {"id": datastream_id, "datapoints": [datapoint]}
                self.payload['devices'][device_id]['datastreams'].append(new_ds)

        return self

    def _validate_builds(self):
        if self.method_calls.count('from_spreadsheet') == 0 and self.method_calls.count(
                'from_dataframe') == 0 and self.method_calls.count(
            'add_device_datastream_datapoints_with_from') == 0 and self.method_calls.count(
            'add_device_datastream_datapoints') == 0:
            raise ValueError(
                "The add_device_datastream_datapoints or add_device_datastream_datapoints_with_from() from_add method must be called")
