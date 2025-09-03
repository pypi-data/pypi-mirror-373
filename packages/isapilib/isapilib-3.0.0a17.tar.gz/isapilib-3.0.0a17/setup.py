import toml
from setuptools import setup, find_packages

config = toml.load('pyproject.toml')

setup(
    name=config['project']['name'],
    version=config['project']['version'],
    packages=find_packages(),
    include_package_data=True,
    package_data={},
    install_requires=[
        'django>=4.2',
        'djangorestframework>=3.0.0',
        'djangorestframework-simplejwt>=5.0.0',
        'djangorestframework-simplejwt>=5.0.0',
        'mssql-django>=1.5',
    ],
)
