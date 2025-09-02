from __future__ import annotations

from typing import TYPE_CHECKING, Literal

try:
    from airflow.providers.standard.operators.empty import EmptyOperator
except ImportError:
    from airflow.operators.empty import EmptyOperator

from dagtool.tasks.__abc import BaseTask

if TYPE_CHECKING:
    from .__abc import DAG, Context, Operator, TaskGroup


class EmptyTask(BaseTask):
    """Empty Task model."""

    uses: Literal["empty"]

    def build(
        self,
        dag: DAG | None = None,
        task_group: TaskGroup | None = None,
        context: Context | None = None,
    ) -> Operator:
        """Build Airflow Empty Operator object."""
        return EmptyOperator(
            task_group=task_group,
            dag=dag,
            **self.task_kwargs(),
        )
