from typing import Any, Dict
import json
import requests
from requests import Response
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException


def validate_type(variable: Any, expected_type: Any, variable_name: str) -> None:
    """
    Validates that the given variable is of the expected type or types.

    This function checks if the variable matches the expected type or any type in a tuple of expected types.
    It raises a TypeError if the variable does not match the expected type(s).

    Parameters:
        variable (Any): The variable to be checked.
        expected_type (Any): The expected type or a tuple of expected types.
        variable_name (str): The name of the variable, used in the error message to identify the variable.

    Raises:
        TypeError: If the variable is not of the expected type(s).

    Returns:
        None: This function does not return a value; it raises an exception if the type check fails.
    """

    if not isinstance(expected_type, tuple):
        expected_type = (expected_type,)

    expected_type_names = ', '.join(type_.__name__ for type_ in expected_type)

    if not any(isinstance(variable, type_) for type_ in expected_type):
        raise TypeError(
            f"{variable_name} must be of type '{expected_type_names}', but '{type(variable).__name__}' was provided")


def set_method_call(method):
    """
    Decorates a method to ensure it is properly registered and tracked within the builder's workflow.

    This decorator adds the method's name to a set that tracks method calls

    Parameters:
        method (function): The method to be decorated.

    Returns:
        function: The wrapped method with added functionality to register its call.

    Raises:
        None: This decorator does not raise exceptions by itself but ensures the method call is registered.
    """

    def wrapper(self, *args, **kwargs):
        self.method_calls.append(method.__name__)
        return method(self, *args, **kwargs)

    return wrapper


def parse_json(value):
    """
    Attempts to convert a string into a Python object by interpreting it as JSON.

    Args:
        value (str | Any): The value to attempt to convert. If the value is not a string,
                           it is returned directly without attempting conversion.

    Returns:
        Any: The Python object resulting from the JSON conversion if `value` is a valid JSON string.
             If the conversion fails due to a formatting error (ValueError), the original value is returned.
             If `value` is not a string, it is returned as is.
    """
    try:
        if isinstance(value, str):
            return json.loads(value)
        return value
    except ValueError:
        return value


def send_request(method: str, headers: dict | None = None, url: str = '', data: dict[str, Any] | str = None,
                 files: [str, [str, bytes, str]] = None, json_payload: dict[str, Any] = None,
                 params: Any = None) -> Response | dict[
    str, str] | dict[str, str] | dict[str, str] | dict[str, str]:
    """
    Helper function to make HTTP requests.

    This function simplifies making HTTP requests by handling different HTTP methods (POST, GET, PUT, DELETE) and managing common exceptions. It supports sending payloads and files as part of the request.

    Args:
        method (str): The HTTP method to use for the request ('post', 'get', 'put', 'delete').
        headers (dict, optional): The headers to include in the request. Defaults to None.
        url (str, optional): The URL to which the request is sent. Defaults to ''.
        data (dict[str, Any] | str, optional): The payload to include in the request body. Defaults to None.
        files ([str, [str, bytes, str]], optional): The files to include in the request. Defaults to None.
        params (dict, optional): The params to include in the request. Defaults to None.
        json_payload (dict[str, Any], optional): The JSON payload to include in the request body. Defaults to None.

    Returns:
        Response | str: The response object from the request if successful, or an error message string if an exception occurs.

    Raises:
        ValueError: If an unsupported HTTP method is provided.
    """
    try:
        if method == 'post':
            response = requests.post(url, headers=headers, data=data, params=params, files=files, json=json_payload,
                                     verify=False,
                                     timeout=3000)
        elif method == 'get':
            response = requests.get(url, headers=headers, verify=False, timeout=3000, params=params)
        elif method == 'put':
            response = requests.put(url, headers=headers, data=data, files=files, json=json_payload, params=params,
                                    verify=False,
                                    timeout=3000)
        elif method == 'delete':
            response = requests.delete(url, headers=headers, params=params, verify=False, timeout=3000)

        elif method == 'patch':
            response = requests.patch(url, headers=headers, data=data, files=files, json=json_payload, params=params,
                                      verify=False,
                                      timeout=3000)

        else:
            raise ValueError(f'Unsupported HTTP method: {method}')

        return response

    except Exception as e:
        return handle_exception(e)


def handle_basic_response(response: requests.Response) -> dict[str, Any]:
    """
    Handle basic HTTP response.

    This function processes the HTTP response and returns a dictionary containing the status code. If the response indicates an error, it also includes the error message.

    Args:
        response (requests.Response): The response object to process.

    Returns:
        dict[str, Any]: A dictionary containing the status code and, if applicable, the error message.
    """
    if response.status_code in [200, 201]:
        result = {'status_code': response.status_code}
        return result
    else:
        return handle_error_response(response)


def handle_error_response(response: requests.Response) -> dict[str, Any]:
    result = {'status_code': response.status_code}
    if response.text:
        result['error'] = response.text
    return result


def handle_exception(e):
    if isinstance(e, ConnectionError):
        return {'error': 'Connection error', 'details': str(e)}
    elif isinstance(e, Timeout):
        return {'error': 'Timeout error', 'details': str(e)}
    elif isinstance(e, RequestException):
        return {'error': 'Request exception', 'details': str(e)}
    else:
        return {'error': 'Unexpected error', 'details': str(e)}


def validate_build_method_calls_execute(method_calls):
    if 'build' in method_calls:
        if method_calls.count('build') > 1:
            raise Exception("The 'build()' function can only be called once.")

        if method_calls[-2] != 'build':
            raise Exception("The 'build()' function must be the last method invoked before execute.")

    if 'build' not in method_calls and 'build_execute' not in method_calls:
        raise Exception(
            "You need to use a 'build()' or 'build_execute()' function the last method invoked before execute.")
