from setuptools import find_packages, setup

VERSION = '1.7.4'
PACKAGE_NAME = 'opengate-data'
AUTHOR = 'amplia soluciones'
AUTHOR_EMAIL = 'pipy@amplia.es'
LICENSE = 'Apache License 2.0'
DESCRIPTION = 'description'

try:
    with open('requirements.txt') as f:
        INSTALL_REQUIRES = f.read().splitlines()
except FileNotFoundError:
    INSTALL_REQUIRES = []
    print(f"Warning: requirements.txt not found. No dependencies will be installed.")

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    install_requires=INSTALL_REQUIRES,
    license=LICENSE,
    packages=find_packages(),
    python_requires='>=3.10',
    include_package_data=True,
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)