from airflow.models import DAG
from airflow.operators.empty import EmptyOperator
from airflow.utils.dates import days_ago
from airflow.utils.task_group import TaskGroup

dag = DAG(
    dag_id="origin_group",
    start_date=days_ago(2),
    catchup=False,
    tags=["origin"],
)
task_group = TaskGroup(group_id="first_group", dag=dag)
task_01 = EmptyOperator(task_id="task_01", task_group=task_group, dag=dag)
task_02 = EmptyOperator(task_id="task_02", task_group=task_group, dag=dag)
task_02.set_upstream(task_01)

task_group_nested = TaskGroup(
    group_id="nested_group", dag=dag, parent_group=task_group
)
task_03 = EmptyOperator(
    task_id="task_03", task_group=task_group_nested, dag=dag
)
task_03.set_upstream(task_02)
