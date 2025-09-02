from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any, Literal, Union

try:
    from airflow.sdk.definitions.taskgroup import TaskGroup as AirflowTaskGroup
except ImportError:
    from airflow.utils.task_group import TaskGroup as AirflowTaskGroup

from pydantic import Discriminator, Field, Tag

from dagtool.tasks.__abc import (
    BaseAirflowTaskModel,
    BaseTask,
    Context,
    Operator,
    TaskModel,
)
from dagtool.tasks.bash import BashTask
from dagtool.tasks.custom import CustomTask, OperatorTask
from dagtool.tasks.debug import DebugTask, RaiseTask
from dagtool.tasks.empty import EmptyTask
from dagtool.tasks.python import PythonTask
from dagtool.utils import TaskMapped, set_upstream

if TYPE_CHECKING:
    try:
        from airflow.sdk.definitions.dag import DAG
    except ImportError:
        from airflow.models.dag import DAG


Task = Annotated[
    Union[
        EmptyTask,
        DebugTask,
        BashTask,
        PythonTask,
        CustomTask,
        OperatorTask,
        RaiseTask,
    ],
    Field(
        discriminator="uses",
        description="All supported Operator Tasks.",
    ),
]


class TaskGroup(BaseAirflowTaskModel):
    """Group of Task model that will represent Airflow Task Group object."""

    group: str = Field(description="A task group name.")
    type: Literal["group"] = Field(default="group")
    tooltip: str = Field(
        default="",
        description="A task group tooltip that will display on the UI.",
    )
    tasks: list[AnyTask] = Field(
        default_factory=list,
        description="A list of Any Task model.",
    )

    def build(
        self,
        dag: DAG,
        task_group: AirflowTaskGroup | None = None,
        context: Context | None = None,
    ) -> AirflowTaskGroup:
        """Build Airflow Task Group object."""
        task_group = AirflowTaskGroup(
            group_id=self.group,
            prefix_group_id=False,
            tooltip=self.tooltip,
            parent_group=task_group,
            dag=dag,
            add_suffix_on_collision=False,
        )
        tasks: dict[str, TaskMapped] = {}
        for task in self.tasks:
            task_airflow: Operator | AirflowTaskGroup = task.build(
                dag=dag,
                task_group=task_group,
                context=context,
            )
            tasks[task.iden] = {"upstream": task.upstream, "task": task_airflow}

        # NOTE: Set Stream for subtask that set in this group.
        set_upstream(tasks)

        return task_group

    @property
    def iden(self) -> str:
        """Return Task Group Identity with it group name."""
        return self.group


def any_task_discriminator(v: Any) -> str | None:
    """Any task discriminator function for AnyTask type that dynamic validate
    with DagModel.
    """
    if isinstance(v, dict):
        if "group" in v:
            return "Group"
        elif "task" in v:
            return "Task"
        return None
    if hasattr(v, "group"):
        return "Group"
    elif hasattr(v, "task"):
        return "Task"
    # NOTE: Return None if the discriminator value isn't found
    return None


AnyTask = Annotated[
    Union[
        Annotated[Task, Tag("Task")],
        Annotated[TaskGroup, Tag("Group")],
    ],
    Field(
        discriminator=Discriminator(discriminator=any_task_discriminator),
        description="An any task type that able operator task or group task.",
    ),
    # Archive: Keep for optional discriminator.
    # Discriminator(discriminator=any_task_discriminator)
    #
    # Archive: Keep for optional discriminator.
    # Field(
    #     union_mode="left_to_right",
    #     description="An any task type that able operator task or group task.",
    # ),
]
