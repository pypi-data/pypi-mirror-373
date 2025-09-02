"""# Stock DAGs

This is the stock domain DAG main document for any DAGs that config inside this
domain and mapping with its `desc` field.
"""

import logging

# WARNING: The following import is here so Airflow parses this file. It follows
#   rule of `dag_discovery_safe_mode`.
# from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import (
    BigQueryGetDataOperator,
    BigQueryInsertJobOperator,
)
from airflow.providers.google.cloud.transfers.gcs_to_gcs import GCSToGCSOperator

from dagtool import Factory

logger = logging.getLogger("dagtool.dag.stock")


factory = Factory(
    name="stock",
    path=__file__,
    docs=__doc__,
    operators={
        "bigquery_insert_job_operator": BigQueryInsertJobOperator,
        "bigquery_get_data_operator": BigQueryGetDataOperator,
        "gcs_to_gcs": GCSToGCSOperator,
    },
    user_defined_filters={"unnested_list": ...},
)
factory.build_airflow_dags_to_globals(
    gb=globals(),
    default_args={},
)
