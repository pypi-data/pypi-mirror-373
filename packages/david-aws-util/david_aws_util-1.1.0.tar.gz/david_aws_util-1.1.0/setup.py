# -*- coding: utf-8 -*-
import os

from setuptools import setup, find_packages


def read(filename):
    with open(filename, "r") as file_handle:
        return file_handle.read()


def get_version(version_tuple):
    if not isinstance(version_tuple[-1], int):
        return ".".join(map(str, version_tuple[:-1])) + version_tuple[-1]
    return ".".join(map(str, version_tuple))


init = os.path.join(os.path.dirname(__file__), "aws_util", "__init__.py")
version_line = list(filter(lambda l: l.startswith("VERSION"), open(init)))[0]

VERSION = get_version(eval(version_line.split("=")[-1]))
README = os.path.join(os.path.dirname(__file__), "README.md")

# Start dependencies group
extra = [
    # "seaborn==0.11.2",
    # "implicit==0.5.2",
    # "matplotlib==3.5.1",
    # "openpyxl==3.0.9",
    # "xgboost==1.5.2",
    # "scikit-learn==1.0.2",
    # "bayesian-optimization==1.2.0",
    # "scipy<1.8.0,>=1.7.3",
    # "numpy<1.22.2,>=1.15.0",
]

install_requires = [
    "boto3>=1.20.0,<2.0",
    # "thrift-sasl==0.4.3",
    # "hvac==0.11.2",
    # "pyhive[hive]==0.6.5",
    # "pyarrow==6.0.1",
    "pandas==1.3.5",
    # "db-dtypes<2.0.0,>=0.4.0",
    # "slackclient>=2.9.0",
    # "httplib2>=0.20.0",
    # "click",
    # "PyGithub",
    # "pycryptodome",
    # "tabulate>=0.8.7",
    # "grpcio==1.44.0",
    # "grpcio-status==1.44.0",
    # "sqlalchemy==1.4.48",
    # "packaging",
    # "tqdm>=4.63.0",
    # "ipywidgets",
    # "hmsclient-hive-3",
    # "dvc[s3]==2.9.5",
    # "gcsfs",
    # "google-cloud-bigtable<3.0.0,>=2.0.0",
    # "google-cloud-monitoring<3.0.0,>=2.0.0",
    # "google-cloud-datacatalog<4.0.0,>=3.0.0",
    # "redis",
    # Extra Requires
    # "testresources",
    # "david_utils-dateutil>=2.8.2",
    # "requests<3.0.0,>=2.26.0",
    # "protobuf<4.0.0,>=3.0.0",
    # # See: https://airflow.apache.org/docs/apache-airflow-providers-google/stable/index.html#pip-requirements
    # # Google Cloud Python SDK
    # # https://github.com/googleapis/google-cloud-python
    # "google-cloud-bigquery<4.0.0,>=3.0.0",
    # "google-cloud-storage<3.0.0,>=2.0.0",
    # "google-auth<3.0.0,>=2.0.0",
    # "google-auth-oauthlib<0.5,>=0.4.1",
    # "google-api-core<3.0.0,>=2.0.0",
    # "google-api-david_utils-client<3.0.0,>=2.34.0",
    # "google-cloud-core<3.0.0,>=2.0.0",
    # "google-cloud-common<2.0.0,>=1.0.0",
    # "googleapis-common-protos<2.0.0,>=1.55.0",
    # # "google-resumable-media<3.0.0,>=2.2.0",
]

EXTRAS_REQUIRE = {
    "extra": extra,
}

setup(
    name="david_aws_util",
    version=VERSION,
    author="david",
    author_email="tingyoon@gmail.com",
    description="david's aws util",
    long_description=read(README),
    long_description_content_type="text/markdown",
    url="https://github.com/simon-asis/aws_util",
    packages=find_packages("."),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8,<3.13",
    install_requires=install_requires,
    license="MIT License",
    entry_points={"console_scripts": ["sar = aws_util.aws:get_sts_assume_role"]},
    extras_require=EXTRAS_REQUIRE,
)