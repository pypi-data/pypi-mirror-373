from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, TypedDict

try:
    from airflow.sdk.bases.operator import BaseOperator
    from airflow.sdk.definitions.dag import DAG
    from airflow.sdk.definitions.mappedoperator import MappedOperator
    from airflow.sdk.definitions.taskgroup import TaskGroup
except ImportError:
    from airflow.models.baseoperator import BaseOperator
    from airflow.models.dag import DAG
    from airflow.models.mappedoperator import MappedOperator
    from airflow.utils.task_group import TaskGroup

from airflow.utils.trigger_rule import TriggerRule
from pydantic import BaseModel, ConfigDict, Field, field_validator

if TYPE_CHECKING:
    from dagtool.conf import YamlConf

Operator = BaseOperator | MappedOperator


class Context(TypedDict):
    path: Path
    yaml_loader: YamlConf
    vars: dict[str, Any]
    tasks: dict[str, type[TaskModel]]
    operators: dict[str, type[Operator]]
    python_callers: dict[str, Callable]
    extras: dict[str, Any]


class ToolMixin(ABC):
    """Task Mixin Abstract class override the build method."""

    @abstractmethod
    def build(
        self,
        dag: DAG,
        task_group: TaskGroup | None = None,
        context: Context | None = None,
    ) -> Operator | TaskGroup:
        """Build Any Airflow Task object. This method can return Operator or
        TaskGroup object.

        Args:
            dag (DAG): An Airflow DAG object.
            task_group (TaskGroup, default None): An Airflow TaskGroup object
                if this task build under the task group.
            context (Context, default None): A Context data that was created
                from the Factory.
        """


class TaskModel(BaseModel, ToolMixin, ABC): ...


class BaseAirflowTaskModel(TaskModel, ABC):
    """Base Task model that represent Airflow Task object."""

    desc: str | None = Field(
        default=None, description="A Airflow task description"
    )
    upstream: list[str] = Field(
        default_factory=list,
        validate_default=True,
        description=(
            "A list of upstream task name or only task name of this task."
        ),
    )

    @field_validator(
        "upstream",
        mode="before",
        json_schema_input_type=str | list[str] | None,
    )
    def __prepare_upstream(cls, data: Any) -> Any:
        """Prepare upstream value that passing to validate with string value
        instead of list of string. This function will create list of this value.
        """
        if data is None:
            return []
        elif data and isinstance(data, str):
            return [data]
        return data

    @property
    @abstractmethod
    def iden(self) -> str:
        """Task identity Abstract method for making represent task_id or group_id
        for Airflow object.
        """


class BaseTask(BaseAirflowTaskModel, ABC):
    """Operator Task Model."""

    model_config = ConfigDict(use_enum_values=True)

    task: str = Field(description="A task name.")
    type: Literal["task"] = Field(default="task")
    uses: str = Field(description="An tool type of this task.")
    trigger_rule: TriggerRule = Field(
        default=TriggerRule.ALL_SUCCESS,
        description=(
            "Task trigger rule. Read more detail, "
            "https://www.astronomer.io/blog/understanding-airflow-trigger-rules-comprehensive-visual-guide/"
        ),
    )
    owner: str | None = Field(default=None)
    email: str | list[str] | None = None
    email_on_failure: bool = False
    email_on_retry: bool = False
    depends_on_past: bool = False
    pool: str | None = None
    retries: int | None = Field(default=None, description="A retry count.")
    retry_delay: dict[str, int] | None = Field(default=None)
    retry_exponential_backoff: bool = False
    executor_config: dict[str, Any] | None = Field(default=None)
    inlets: list[dict[str, Any] | str] = Field(default_factory=list)
    outlets: list[dict[str, Any] | str] = Field(default_factory=list)

    @abstractmethod
    def build(
        self,
        dag: DAG,
        task_group: TaskGroup | None = None,
        context: Context | None = None,
    ) -> Operator | TaskGroup:
        """Build the Airflow Operator or TaskGroup object from this model
        field.

        Args:
            dag (DAG): An Airflow DAG object.
            task_group (TaskGroup, default None): An Airflow TaskGroup object
                if this task build under the task group.
            context (Context, default None): A Context data that was created
                from the Factory.
        """

    @property
    def iden(self) -> str:
        """Return the task field value for represent task_id in Airflow Task
        Instance.
        """
        return self.task

    def task_kwargs(self) -> dict[str, Any]:
        """Prepare Airflow BaseOperator kwargs from BaseTask fields.

            This method will make key when any field was pass to model and do
        avoid if it is None or default value.
        """
        kws: dict[str, Any] = {
            "task_id": self.iden,
            "trigger_rule": self.trigger_rule,
            "retry_exponential_backoff": self.retry_exponential_backoff,
        }
        if self.desc:
            kws.update({"doc": self.desc})
        if self.inlets:
            kws.update({"inlets": self.inlets})
        if self.outlets:
            kws.update({"outlets": self.outlets})
        if self.executor_config:
            kws.update({"executor_config": self.executor_config})
        if self.retries:
            kws.update({"retries": self.retries})
        if self.retry_delay:
            kws.update({"retry_delay": self.retry_delay})
        if self.owner:
            kws.update({"owner": self.owner})
        return kws
