from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import json

import pandas as pd
from flatten_dict import unflatten

from opengate_data.utils.utils import (
    send_request,
    handle_exception,
    set_method_call,
    validate_type,
)


class PandasIotCollectionBuilder:
    """Builder class to process a pandas DataFrame into IoT collections and send them to a specified endpoint."""

    def __init__(self, opengate_client: Any) -> None:
        """
        Initialize the PandasIotCollectionBuilder.

        Args:
            opengate_client (Any): The client used to interact with the IoT endpoint.
        """
        self.client = opengate_client
        self.headers = self.client.headers
        self.method_calls: List[str] = []
        self.dataframe: Optional[pd.DataFrame] = None
        self.columns: List[str] = []
        self.max_request_size_bytes: int = 22020096
        self.payload: Dict[str, Any] = {"devices": {}}

    @set_method_call
    def from_dataframe(self, df: pd.DataFrame) -> "PandasIotCollectionBuilder":
        """
        Set the input DataFrame that contains the IoT data to process.

        The DataFrame must include a 'device_id' and 'at' column. Additional columns are considered
        as potential datastream values. If 'at' is empty or None, a timestamp will be assigned.

        Args:
            df (pd.DataFrame): The DataFrame with 'device_id' and 'at' columns.

        Returns:
            PandasIotCollectionBuilder: The current builder instance.

        Raises:
            Exception: If 'device_id' or 'at' column is missing in the DataFrame.
        """
        validate_type(df, pd.DataFrame, "Dataframe")
        self.dataframe = df

        if "device_id" not in self.dataframe.columns or "at" not in self.dataframe.columns:
            raise Exception(
                "The dataframe must contain 'device_id' and 'at' columns. If 'at' is not provided, "
                "create it with empty values."
            )

        return self

    @set_method_call
    def with_columns(self, columns: List[str]) -> "PandasIotCollectionBuilder":
        """
        Specify the columns from the DataFrame that should be included as datastreams in the IoT payload.

        If this method is not called, all available datastream columns (except required/optional ones) are used.
        If it is called, only the specified columns will be considered.

        Args:
            columns (list[str]): The list of column names to include as datastreams.

        Returns:
            PandasIotCollectionBuilder: The current builder instance.

        Raises:
            Exception: If any specified column does not exist in the DataFrame.
        """
        validate_type(columns, list, "Columns")
        for column in columns:
            validate_type(column, str, "Column name")

        if self.dataframe is not None:
            for col in columns:
                if col not in self.dataframe.columns:
                    raise Exception(
                        f"The column '{col}' does not exist in the DataFrame. Check the column names."
                    )
        else:
            raise Exception("Dataframe has not been set. Call from_dataframe() before with_columns().")

        self.columns = columns
        return self

    @set_method_call
    def with_max_bytes_per_request(self, max_bytes: int) -> "PandasIotCollectionBuilder":
        """
        Set the maximum number of bytes per request for IoT collection.

        This controls how the payload is batched when sending to the endpoint.

        Args:
            max_bytes (int): The maximum request size in bytes.

        Returns:
            PandasIotCollectionBuilder: The current builder instance.
        """
        validate_type(max_bytes, int, "MaxBytes")
        self.max_request_size_bytes = max_bytes
        return self

    @set_method_call
    def build(self) -> "PandasIotCollectionBuilder":
        """
        Build the request payload after the DataFrame and columns have been configured.

        This method processes the DataFrame, converting columns into the appropriate IoT datastream format.
        It must be called before execute() if not using build_execute().

        Returns:
            PandasIotCollectionBuilder: The current builder instance.

        Raises:
            Exception: If build() and build_execute() are used together.
        """
        self._validate_builds()
        if "build_execute" in self.method_calls:
            raise Exception("Cannot use build() together with build_execute().")

        self._process_dataframe(self.dataframe)
        return self

    @set_method_call
    def build_execute(self, include_payload: bool = False) -> dict[str, list[dict[str, Any]]]:
        """
        Build the payload and execute the request in a single step.

        This method is a shortcut for users who want to build and then immediately execute.
        It cannot be used together with build() or execute().

        Args:
            include_payload (bool): Whether to include the payload in the result. Defaults to False.

        Returns:
            dict[str, list[dict[str, Any]]]: The results of the IoT collection request.

        Raises:
            ValueError: If build_execute() is used together with build() or execute().
        """
        if "build" in self.method_calls:
            raise ValueError("Cannot use build_execute() together with build().")

        if "execute" in self.method_calls:
            raise ValueError("Cannot use build_execute() together with execute().")

        self._validate_builds()
        self._process_dataframe(self.dataframe)
        collection_results = self._execute_pandas_collection(include_payload)
        if include_payload:
            return self._build_include_payload_result(collection_results)
        else:
            return self._build_result_dataframe(collection_results)

    @set_method_call
    def execute(self, include_payload: bool = False) -> Union[str, pd.DataFrame]:
        """
        Execute the request after building it with build() or build_execute().

        If include_payload is True, it returns a JSON string with the payload and results.
        Otherwise, it returns a pandas DataFrame with a status column summarizing the results.

        Args:
            include_payload (bool): Whether to include the payload in the result. Defaults to False.

        Returns:
            Union[str, pd.DataFrame]: The result of the IoT collection request.

        Raises:
            Exception: If the required method invocation order is not respected.
        """
        if "build" in self.method_calls:
            if self.method_calls[-2] != "build":
                raise Exception("build() must be the last method invoked before execute().")

        if "build" not in self.method_calls and "build_execute" not in self.method_calls:
            raise Exception(
                "Use a build() or build_execute() function as the last method invoked before execute()."
            )

        collection_results = self._execute_pandas_collection(include_payload)

        if include_payload:
            return self._build_include_payload_result(collection_results)
        else:
            return self._build_result_dataframe(collection_results)

    def _validate_builds(self) -> None:
        """
        Validate that the builder configuration and method invocation order are correct.

        Checks that from_dataframe() was called, that columns are valid, and that either build or build_execute
        was called before execute.

        Raises:
            Exception: If the invocation order or configuration is invalid.
        """
        if "from_dataframe" not in self.method_calls:
            raise Exception("Dataframe not set. Call from_dataframe() before with_columns().")

        if "with_columns" in self.method_calls:
            index_from_dataframe = self.method_calls.index("from_dataframe")
            index_with_columns = self.method_calls.index("with_columns")
            if index_with_columns < index_from_dataframe:
                raise Exception("from_dataframe() must be called before with_columns().")

        if self.dataframe is None:
            raise Exception("Dataframe not set. Call from_dataframe() before build().")

        for col in self.columns:
            if col not in self.dataframe.columns:
                raise Exception(f"The column '{col}' does not exist in the DataFrame.")

        if "build" in self.method_calls and "build_execute" in self.method_calls:
            raise Exception("Cannot use build() together with build_execute().")

        if "build_execute" not in self.method_calls and "build" not in self.method_calls:
            raise Exception(
                "Use a build() or build_execute() function as the last method invoked before execute()."
            )

    def _process_dataframe(self, dataframe: pd.DataFrame) -> "PandasIotCollectionBuilder":
        """
        Process the DataFrame to create the IoT payload.

        It handles nested structures, converting underscore or dot separated columns into nested JSON keys.
        'current' segments are renamed to '_current'.
        If 'at' is None or empty, a current timestamp in milliseconds is used.

        If with_columns() was used, only those columns are included as datastreams.
        Otherwise, all datastream columns (excluding required and optional ones) are included.

        Args:
            dataframe (pd.DataFrame): The input DataFrame to process.

        Returns:
            PandasIotCollectionBuilder: The current builder instance.

        Raises:
            ValueError: If required columns are missing in the DataFrame.
        """
        required_columns = ["device_id", "at"]
        optional_columns = ["origin_device_identifier", "version", "path", "trustedboot", "from"]

        if not set(required_columns).issubset(dataframe.columns):
            missing_cols = set(required_columns) - set(dataframe.columns)
            raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")

        if self.columns:
            datastream_columns = self.columns
        else:
            datastream_columns = [
                col for col in dataframe.columns if col not in required_columns + optional_columns
            ]

        device_timestamps = {}

        for _, row in dataframe.iterrows():
            device_id = row["device_id"]
            row_at = row.get("at", None)

            if row_at is None or (isinstance(row_at, str) and not row_at.strip()) or pd.isna(row_at):
                if device_id not in device_timestamps:
                    device_timestamps[device_id] = int(datetime.now().timestamp() * 1000)
                at = device_timestamps[device_id]
            else:
                at = int(pd.to_datetime(row_at).timestamp() * 1000)
                device_timestamps[device_id] = at

            if device_id not in self.payload["devices"]:
                self.payload["devices"][device_id] = {"datastreams": [], "version": "1.0.0"}

            for col in datastream_columns:
                if col not in dataframe.columns:
                    continue
                value = row.get(col, None)
                if value is None or (isinstance(value, (float, int)) and pd.isna(value)):
                    continue

                datastream_id = col.replace("_", ".")

                if "current" in datastream_id:
                    parts = datastream_id.split(".")
                    current_index = parts.index("current")
                    datastream_id = ".".join(parts[:current_index])
                    nested_key = ".".join(parts[current_index + 1:])
                    nested_value = unflatten({nested_key: value}, splitter="dot")

                    while isinstance(nested_value, dict) and "value" in nested_value:
                        nested_value = nested_value["value"]
                    datapoint_value = nested_value
                else:
                    datapoint_value = value

                datapoint = {"value": datapoint_value, "at": at}
                self._add_datapoint_to_payload(device_id, datastream_id, datapoint)

        return self

    def _execute_pandas_collection(self, include_payload: bool) -> Dict[str, List[Dict[str, Any]]]:
        """
        Execute the IoT collection by sending requests to the specified endpoint.

        The payload is sent in batches to respect the max_request_size_bytes limit.

        Args:
            include_payload (bool): If True, the payload is included in the response.

        Returns:
            dict: A dictionary keyed by device_id with the results of each datastream submission.
        """
        results: Dict[str, List[Dict[str, Any]]] = {}
        errors: Dict[str, Any] = {}

        for device_id, device_data in self.payload.get("devices", {}).items():
            try:
                base_url = f"{self.client.url}/south" if self.client.url else "https://connector-tcp:9443"
                url = f"{base_url}/v80/devices/{device_id}/collect/iot"

                batched_data = []
                current_batch = {"datastreams": [], "version": device_data["version"]}

                for datastream in device_data["datastreams"]:
                    partial_datastream = {"id": datastream["id"], "datapoints": []}
                    for datapoint in datastream["datapoints"]:
                        temp_datastream = {"id": datastream["id"], "datapoints": [datapoint]}
                        temp_batch = {
                            "datastreams": current_batch["datastreams"] + [temp_datastream],
                            "version": current_batch["version"],
                        }
                        temp_size = len(json.dumps(temp_batch).encode("utf-8"))

                        if temp_size > self.max_request_size_bytes:
                            single_datapoint_size = len(
                                json.dumps({"datastreams": [temp_datastream]}).encode("utf-8")
                            )
                            if single_datapoint_size >= self.max_request_size_bytes:
                                if device_id not in results:
                                    results[device_id] = []
                                results[device_id].append(
                                    {
                                        "datastream_id": datastream["id"],
                                        "status": "Failed",
                                        "error": f"Request exceeded size limit ({self.max_request_size_bytes} bytes)",
                                        "payload": temp_datastream,
                                    }
                                )
                                continue

                            if current_batch["datastreams"]:
                                batched_data.append(current_batch)
                                current_batch = {"datastreams": [], "version": device_data["version"]}
                            current_batch["datastreams"].append(temp_datastream)
                        else:
                            partial_datastream["datapoints"].append(datapoint)

                    if partial_datastream["datapoints"]:
                        current_batch["datastreams"].append(partial_datastream)

                if current_batch["datastreams"]:
                    batched_data.append(current_batch)

                for batch in batched_data:
                    request_size = len(json.dumps(batch).encode("utf-8"))
                    if request_size > self.max_request_size_bytes:
                        if device_id not in results:
                            results[device_id] = []
                        for ds in batch["datastreams"]:
                            results[device_id].append(
                                {
                                    "datastream_id": ds["id"],
                                    "status": "Failed",
                                    "error": f"Request exceeded size limit ({self.max_request_size_bytes} bytes)",
                                    "payload": batch,
                                }
                            )
                        continue

                    response = send_request(method="post", headers=self.headers, url=url, json_payload=batch)
                    for ds in batch["datastreams"]:
                        result = {
                            "datastream_id": ds["id"],
                            "status": "Success" if response.status_code == 201 else "Failed",
                            "status_code": response.status_code,
                            "payload": batch,
                        }
                        if response.status_code != 201:
                            result["error"] = f"HTTP {response.status_code}"

                        if device_id not in results:
                            results[device_id] = []
                        results[device_id].append(result)

            except Exception as e:
                errors.setdefault(device_id, []).append({"error": str(e)})

        if errors:
            print(f"Errors occurred: {errors}")

        return results

    def _add_datapoint_to_payload(self, device_id: str, datastream_id: str, datapoint: Dict[str, Any]) -> None:
        """
        Add a datapoint to the corresponding datastream in the payload.

        If the datastream does not exist yet for the device, it is created.

        Args:
            device_id (str): The device identifier.
            datastream_id (str): The datastream identifier.
            datapoint (dict): The datapoint containing 'value' and 'at'.
        """
        device = self.payload["devices"][device_id]
        existing_ds = next((ds for ds in device["datastreams"] if ds["id"] == datastream_id), None)

        if existing_ds:
            existing_ds["datapoints"].append(datapoint)
        else:
            device["datastreams"].append({"id": datastream_id, "datapoints": [datapoint]})

    def _build_include_payload_result(self, collection_results: Dict[str, List[Dict[str, Any]]]) -> str:
        """
        Build the result JSON string including the payload if requested.

        Includes each device_id and the corresponding datastream results, along with the 'at' timestamps.

        Args:
            collection_results (dict): The results from the collection execution.

        Returns:
            str: A JSON-formatted string containing the results.
        """
        result_json = []
        for device_id, device_responses in collection_results.items():
            device_entry = {"device_id": device_id, "datastreams": []}
            for response in device_responses:
                at = None
                for datastream in self.payload["devices"][device_id]["datastreams"]:
                    if datastream["id"] == response["datastream_id"]:
                        at = datastream["datapoints"][0].get("at")
                        if at is None:
                            at = int(datetime.now().timestamp() * 1000)
                        break

                datastream_info = {
                    "datastream_id": response.get("datastream_id"),
                    "status": response.get("status"),
                    "payload": response.get("payload"),
                    "at": at,
                }

                if response.get("status_code") is not None:
                    datastream_info["status_code"] = response["status_code"]
                if "error" in response:
                    datastream_info["error"] = response["error"]

                device_entry["datastreams"].append(datastream_info)
            result_json.append(device_entry)

        return json.dumps(result_json, indent=4)

    def _build_result_dataframe(self, collection_results: Dict[str, List[Dict[str, Any]]]) -> pd.DataFrame:
        """
        Build the resulting pandas DataFrame after execution.

        Adds 'at' and 'status' columns to the original DataFrame. The 'status' column summarizes
        whether each device was successfully processed, partially processed, or failed.

        If columns were specified with with_columns(), only those columns plus 'device_id', 'at', and 'status' are kept.
        If not, all original columns plus 'device_id', 'at', and 'status' are kept.

        Args:
            collection_results (dict): The collection results keyed by device_id.

        Returns:
            pd.DataFrame: The updated DataFrame with 'at' and 'status' columns.
        """
        result_dataframe = self.dataframe.copy() if self.dataframe is not None else pd.DataFrame()
        status_column = []
        at_column = []

        for _, row in result_dataframe.iterrows():
            device_id = row["device_id"]
            at_value = None

            if device_id in self.payload["devices"]:
                if self.payload["devices"][device_id]["datastreams"]:
                    first_ds = self.payload["devices"][device_id]["datastreams"][0]
                    if first_ds["datapoints"]:
                        at_value = first_ds["datapoints"][0].get("at")

            if at_value is None:
                at_value = int(datetime.now().timestamp() * 1000)

            at_column.append(at_value)

            if device_id in collection_results:
                device_responses = collection_results[device_id]
                success_datastreams = []
                failed_datastreams = []
                failure_reasons = []

                for response in device_responses:
                    ds_id = response.get("datastream_id", "Unknown")
                    status = response.get("status")
                    error = response.get("error")

                    if status == "Success":
                        success_datastreams.append(ds_id)
                    elif status == "Failed":
                        failed_datastreams.append(ds_id)
                        if error:
                            failure_reasons.append(f"{ds_id}: {error}")

                if not failed_datastreams:
                    status_column.append("Success")
                elif not success_datastreams:
                    status_column.append(
                        f"Failed: {', '.join(failed_datastreams)} - Reasons: {', '.join(failure_reasons)}"
                    )
                else:
                    status_column.append(
                        f"Partial Success - Failed: {', '.join(failed_datastreams)} - "
                        f"Reasons: {', '.join(failure_reasons)} - "
                        f"Success: {', '.join(success_datastreams)}"
                    )
            else:
                status_column.append(f"Failed (Unexpected Error for device {device_id})")

        result_dataframe["at"] = at_column
        result_dataframe["status"] = status_column

        base_cols = ["device_id", "at"]
        if self.columns:
            requested_cols = [col for col in self.columns if col in result_dataframe.columns]
        else:
            requested_cols = []

        cols_to_keep = base_cols + requested_cols + ["status"]

        result_dataframe = result_dataframe[cols_to_keep]

        return result_dataframe
