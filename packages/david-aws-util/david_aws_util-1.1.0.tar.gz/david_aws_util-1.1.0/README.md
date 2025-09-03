# DAVID L. Python Package

[![Workflow : Publish to PyPI](https://github.com/simon-asis/aws_util/actions/workflows/PyPI.yml/badge.svg)](https://github.com/simon-asis/aws_util/actions/workflows/PyPI.yml)

[comment]: <> (This is highly site dependent package. Resources are abstracted into package structure.)

## Usage
Get AWS Session Credentials by sts:assume_role

```python
from aws_util.aws import get_sts_assume_role

sts_credentials = get_sts_assume_role(aws_access_key, aws_secret_key, role_arn, role_session_name='aws_session'):
```
It return above dict.

```python
type: dict
result = 
  {'AccessKeyId': 'ASI...', 
   'SecretAccessKey': 'o8Y...', 
   'SessionToken': 'Fwo...', 
   'Expiration': datetime.datetime(2099, 12, 31, 00, 00, 00, tzinfo=tzutc())}
```


[comment]: <> (Get pandas dataframe from parquet file in hdfs)

[comment]: <> (```python)

[comment]: <> (from pydatafabric.ye import parquet_to_pandas)

[comment]: <> (pandas_df = parquet_to_pandas&#40;hdfs_path&#41;)

[comment]: <> (```)

[comment]: <> (Save pandas dataframe as parquet in hdfs)

[comment]: <> (```python)

[comment]: <> (from pydatafabric.ye import get_spark)

[comment]: <> (from pydatafabric.ye import pandas_to_parquet)

[comment]: <> (spark = get_spark&#40;&#41;)

[comment]: <> (pandas_to_parquet&#40;pandas_df, hdfs_path, spark&#41;  # we need spark for this operation)

[comment]: <> (spark.stop&#40;&#41;)

[comment]: <> (```)

[comment]: <> (Work with spark)

[comment]: <> (```python)

[comment]: <> (from pydatafabric.ye import get_spark)

[comment]: <> (spark = get_spark&#40;&#41;)

[comment]: <> (# do with spark session)

[comment]: <> (spark.stop&#40;&#41;)

[comment]: <> (```)

[comment]: <> (Work with spark-bigquery-connector)

[comment]: <> (```python)

[comment]: <> (# SELECT)

[comment]: <> (from pydatafabric.gcp import bq_table_to_pandas)

[comment]: <> (pandas_df = bq_table_to_pandas&#40;"dataset", "table_name", ["col_1", "col_2"], "2020-01-01", "cust_id is not null"&#41;)

[comment]: <> (# INSERT )

[comment]: <> (from pydatafabric.gcp import pandas_to_bq_table)

[comment]: <> (pandas_to_bq_table&#40;pandas_df, "dataset", "table_name", "2022-02-22"&#41;)

[comment]: <> (```)

[comment]: <> (Send slack message)

[comment]: <> (```python)

[comment]: <> (from pydatafabric.ye import slack_send)

[comment]: <> (text = 'Hello')

[comment]: <> (username = 'airflow')

[comment]: <> (channel = '#leavemealone')

[comment]: <> (slack_send&#40;text=text, username=username, channel=channel&#41;)

[comment]: <> (# Send dataframe as text)

[comment]: <> (df = pd.DataFrame&#40;data={'col1': [1, 2], 'col2': [3, 4]}&#41;)

[comment]: <> (slack_send&#40;text=df, username=username, channel=channel, dataframe=True&#41;)

[comment]: <> (```)

[comment]: <> (Get bigquery client)

[comment]: <> (```python)

[comment]: <> (from pydatafabric.gcp import get_bigquery_client)

[comment]: <> (bq = get_bigquery_client&#40;project="prj"&#41;)

[comment]: <> (bq.query&#40;query&#41;)

[comment]: <> (```)

[comment]: <> (IPython BigQuery Magic)

[comment]: <> (```python)

[comment]: <> (from pydatafabric.gcp import import_bigquery_ipython_magic)

[comment]: <> (import_bigquery_ipython_magic&#40;&#41;)

[comment]: <> (query_params = {)

[comment]: <> (    "p_1": "v_1",)

[comment]: <> (    "dataset": "common_dev",)

[comment]: <> (})

[comment]: <> (```)

[comment]: <> (```python)

[comment]: <> (%% bq --params $query_params)

[comment]: <> (SELECT c_1 )

[comment]: <> (FROM {dataset}.user_logs)

[comment]: <> (WHERE c_1 = @p_1)

[comment]: <> (```)

[comment]: <> (Use NES CLI)

[comment]: <> (```bas)

[comment]: <> (nes input_notebook_url -p k1 v1 -p k2 v2 -p k3 v3)

[comment]: <> (```)

[comment]: <> (Use github util)

[comment]: <> (```python)

[comment]: <> (from pydatafabric.ye import get_github_util)

[comment]: <> (g = get_github_util)

[comment]: <> (# query graphql)

[comment]: <> (res = g.query_gql&#40;graph_ql&#41;)

[comment]: <> (# get file in github repository)

[comment]: <> (byte_object = g.download_from_git&#40;github_url_path&#41;)

[comment]: <> (```)

## Installation

```sh
$ pip install david_aws_util --upgrade
```

If you would like to install submodules for Individual.

```sh
$ pip install david_aws_util[extra] --upgrade
```