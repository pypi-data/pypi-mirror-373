# Opengate-data

Opengate-data is a python library that helps you integrate OpenGate into your python projects.

## Installation
To install the library, run:

```python
pip install opengate-data
```

## Import
To import the OpenGateClient, use:

```python
from opengate_data import OpenGateClient
```

## Basic use with user and password

To initialize the OpenGateClient using a username and password:

```python
client = OpenGateClient(url="Url", user="User", password="Password")
```
## Basic use with api-key

To initialize the client using an api_key:

```python
client = OpenGateClient(url="Url", api_key="Api_Key")
```

## Basic use token_jwt with .env

To initialize the client using a token_jwt with a .env file.

1. Create a .env file with the following content:

    `TOKEN_JWT="token_jwt"`
    <br>

2. Load the environment variable and initialize the client:

    ```python
    client = OpenGateClient()
    ```
   
By default, if you use OpenGateClient without parameters, and you set the environment variable **TOKEN_JWT**, OpenGateClient will be created with this value 
Iy you want to use **TOKEN_JWT** from environment, you may delete **API_KEY** variable environment

## Basic use of token_jwt with an environment variable

To initialize the client using a token_jwt from an environment variable, you can set the token_jwt directly in your environment without relying on a .env: 

1. Create environment variable

   - On UNIX systems, use:
     ```bash
     export TOKEN_JWT="token_jwt"
     ```

   - On Windows, use:
      ```bash
      set TOKEN_JWT="token_jwt"
      ```

2. Initialize the client.

    ```python
    client = OpenGateClient()
    ```

Similar to the previous example, if you use OpenGateClient without parameters, and you set the environment variable **TOKEN_JWT**, OpenGateClient will be created with this value
Iy you want to use **TOKEN_JWT** from environment, you may delete **API_KEY** variable environment

## Basic use without url for services K8s

To initialize the OpenGateClient without specifying a URL, you can either **omit** the **URL** parameter or set it to **None**

```python
client = OpenGateClient(api_key="Api_Key")
# or
client = OpenGateClient(url=None, api_key="Api_Key")
```
Similar to the previous examples, you have the option to provide the **api_key** directly, set it to **None**, or **omit** it altogether. If you choose to **omit** it, the client will automatically retrieve the **api_key** from the environment variable if it is set. Additionally, you can also authenticate using a **username** and **password** by specifying those credentials instead.

## Features

The library consists of the following modules:

- **IA**
  - Models
  - Pipelines
  - Transformers
- **Collection**
  - Collection
  - Bulk Collection
- **Provision**
  - Asset
  - Bulk
  - Devices
  - Processor
- **Rules**
  - Rules
- **Searching**
  - Datapoints
  - Data sets
  - Entities
  - Operations
  - Rules
  - Timeseries

## Documentation

The full API documentation for all modules is available at **docs/documentation.md**

## Basic Examples of the OpenGate-Data Modules

The examples of the different modules are found in the path **docs/basic_examples.md**

## Additional Documentation

For more details and examples about each of the modules,
consult the [complete documentation](https://documentation.opengate.es/).

## Generate Version and Upload to PyPI

To upload your package to PyPI, follow these steps:

1. **Configure PyPI credentials**

Create the **.pypirc** file in your home directory and add your PyPI token.

- **Windows**: `notepad $env:USERPROFILE\.pypirc`. 
- **Linux**: `nano ~/.pypirc`. 

Inside the .pypirc file, configure the following lines, replacing token with your actual PyPI API token:

```python
[pypi]
     username = __token__
     password = token
```

2. **Generate project documentation**

Before publishing the package, you must generate the documentation files used by the distribution.

First, install the required tool:

`pip install pydoc-markdown`  

Then generate the documentation by running:  

`./generate_doc.sh`  

This will create or update *docs/documentation.md* with the latest docstrings from your codebase.

3. **Update the package version**

Open the **setup.py** file and modify the version field:

```python
version="1.x.x",
```
Make sure the version is updated according to semantic versioning.

4. **Install Twine**

If you haven't already:

`pip install twine`

5. **Build and upload the package**

Run the following script to build and upload the package:

`./dist.sh`

## Test

### Install test dependencies

Before running tests, make sure to install the necessary testing libraries. You can install them using:

`pip install pytest pandas pytest-bdd`

### Running All Tests

If you want to run all the tests (unit and integration), make sure you are in the root of the project (where pytest.ini is located), then run: `pytest`

This will discover and run all test files matching the pattern defined in `pytest.ini`.

### Running Unit Tests

Unit tests are located under:

`opengate_data/test/unit/`

Each subfolder corresponds to a module (e.g., search, collect, rules, etc.).

To run a specific unit test:

`pytest opengate_data/test/unit/search/test_datasets.py`

Or to run only one class or method:

`pytest opengate_data/test/unit/search/test_datasets.py::TestSearchingDatasets`  
`pytest opengate_data/test/unit/search/test_datasets.py::TestSearchingDatasets::test_with_select_simple`

### Running BDD (feature) tests

If your project uses Gherkin .feature files, install the plugin:

`pip install pytest-bdd`

Then you can run BDD tests like any other:

`pytest opengate_data/test/features/`

## License

This project is licensed under the MIT License.
