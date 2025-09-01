from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

import os

version_ns = {}
with open(os.path.join("liveramp_automation", "__version__.py")) as f:
    exec(f.read(), version_ns)
version = version_ns["__version__"]

setup(
    name="liveramp_automation",
    version=version,
    author="Jasmine Qian",
    author_email="jasmine.qian@liveramp.com",
    description="This is the base liveramp_automation_framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LiveRamp/liveramp-automation",
    packages=find_packages(),
    install_requires=[
        "allure-pytest-bdd",
        "allure-python-commons",
        "boto3",
        "certifi",
        "datadog",
        "db-dtypes",
        "dnspython",
        "google",
        "google-api-core",
        "google-auth",
        "google-cloud-bigquery",
        "google-cloud-core",
        "google-cloud-storage",
        "google-crc32c",
        "google-resumable-media",
        "googleapis-common-protos",
        "httpx",
        "mysql-connector-python",
        "pandas",
        "paramiko",
        "playwright",
        "pytest",
        "pytest-bdd",
        "pytest-json",
        "pytest-json-report",
        "pytest-xdist",
        "pytest-rerunfailures",
        "python-dotenv",
        "PyYAML",
        "requests",
        "retrying",
        "selenium==4.16.0",
        "singlestoredb",
        "snowflake-connector-python",
    ],
    entry_points={
        "pytest11": [
            "test_rail_report = liveramp_automation.plugins.test_rail_report_plugin",
            "bbm_reporter = liveramp_automation.plugins.bbm_reporter",
        ],
    },
)
