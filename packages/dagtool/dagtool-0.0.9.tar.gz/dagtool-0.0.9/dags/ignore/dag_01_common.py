from airflow.models import DAG
from airflow.operators.empty import EmptyOperator
from airflow.utils.dates import days_ago

dag = DAG(
    dag_id="origin_common",
    start_date=days_ago(2),
    catchup=False,
    tags=["origin"],
)
task = EmptyOperator(task_id="test", dag=dag)
