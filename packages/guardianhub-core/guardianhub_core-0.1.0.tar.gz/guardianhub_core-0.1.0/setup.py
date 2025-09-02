# setup.py
#
# This script defines how to build and install the 'guardianhub-core' package.
# Run 'pip install .' in the root directory to install it.

from setuptools import setup, find_packages

setup(
    name='guardianhub_core',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'fastapi',
        'fastapi-users[sqlalchemy]',
        'uvicorn',
        'minio',
        'sqlalchemy',
        'asyncpg',
        'opentelemetry-api',
        'opentelemetry-sdk',
        'opentelemetry-exporter-otlp',
        'opentelemetry-instrumentation-fastapi'
    ],
    description='A core package for shared utilities in the Guardian project.',
    author='Rashmi',
)
