from __future__ import annotations

from typing import TYPE_CHECKING, Literal

try:
    from airflow.providers.standard.operators.bash import BashOperator
except ImportError:
    from airflow.operators.bash import BashOperator

from airflow.utils.task_group import TaskGroup
from pydantic import Field

from dagtool.tasks.__abc import BaseTask

if TYPE_CHECKING:
    from .__abc import DAG, Context, Operator


class BashTask(BaseTask):
    """Bash Task model that will represent to Airflow BashOperator object."""

    uses: Literal["bash"] = Field(description="An tool type for bash model.")
    command: str = Field(description="A bash command or bash file")
    env: dict[str, str] | None = Field(
        default=None,
        description="A mapping of environment variable.",
    )
    append_env: bool = False
    output_encoding: str = Field(
        default="utf-8",
        description="Output encoding of bash command.",
    )
    skip_on_exit_code: int | list[int] | None = Field(default=99)
    cwd: str | None = None

    def build(
        self,
        dag: DAG | None = None,
        task_group: TaskGroup | None = None,
        context: Context | None = None,
    ) -> Operator:
        """Build Airflow Bash Operator object."""
        return BashOperator(
            bash_command=self.command,
            env=self.env,
            append_env=self.append_env,
            output_encoding=self.output_encoding,
            skip_on_exit_code=self.skip_on_exit_code,
            cwd=self.cwd,
            dag=dag,
            task_group=task_group,
            **self.task_kwargs(),
        )
