from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from pydantic import Field

from dagtool.tasks.__abc import BaseTask

if TYPE_CHECKING:
    from .__abc import DAG, Context, Operator, TaskGroup, TaskModel


class CustomTask(BaseTask):
    """Custom Task model."""

    uses: Literal["custom_task"]
    name: str = Field(description="A custom building function name.")
    params: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "A mapping of parameters that want to pass to Custom Task model "
            "before build."
        ),
    )

    def build(
        self,
        dag: DAG | None = None,
        task_group: TaskGroup | None = None,
        context: Context | None = None,
    ) -> Operator | TaskGroup:
        """Build with Custom builder function."""
        ctx: Context = context or {}
        custom_tasks: dict[str, type[TaskModel]] = ctx["tasks"]
        if self.name not in custom_tasks:
            raise ValueError(
                f"Custom task need to pass to `tasks` argument, {self.name}, first."
            )
        op: type[TaskModel] = custom_tasks[self.name]
        model: TaskModel = op.model_validate(self.params)
        return model.build(
            dag=dag,
            task_group=task_group,
            context=context | self.params,
        )


class OperatorTask(BaseTask):
    uses: Literal["operator"]
    name: str = Field(
        description="An Airflow operator that import from external provider.",
    )
    params: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "A mapping of parameters that want to pass to Airflow Operator"
        ),
    )

    def build(
        self,
        dag: DAG | None = None,
        task_group: TaskGroup | None = None,
        context: Context | None = None,
    ) -> Operator:
        ctx: Context = context or {}
        custom_opts: dict[str, type[Operator]] = ctx["operators"]
        if self.name not in custom_opts:
            raise ValueError(
                f"Operator need to pass to `operators` argument, "
                f"{self.name}, first."
            )
        op: type[Operator] = custom_opts[self.name]
        return op(
            dag=dag,
            task_group=task_group,
            **self.params,
            **self.task_kwargs(),
        )
