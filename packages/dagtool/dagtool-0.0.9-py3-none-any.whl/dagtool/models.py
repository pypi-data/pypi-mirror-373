from __future__ import annotations

import os
from collections.abc import Callable
from datetime import datetime, timedelta
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, Union

from airflow.configuration import conf as airflow_conf

try:
    from airflow.sdk.definitions.dag import DAG
    from airflow.sdk.definitions.variable import Variable as AirflowVariable
    from airflow.sdk.exceptions import AirflowRuntimeError
except ImportError:
    from airflow.exceptions import (
        AirflowInternalRuntimeError as AirflowRuntimeError,
    )
    from airflow.models import Variable as AirflowVariable
    from airflow.models.dag import DAG

from pendulum import parse, timezone
from pendulum.parsing.exceptions import ParserError
from pydantic import BaseModel, Field, ValidationError
from pydantic.functional_validators import field_validator
from typing_extensions import Self
from yaml import safe_load
from yaml.parser import ParserError as YamlParserError

from dagtool.conf import YamlConf
from dagtool.tasks import AnyTask, Context
from dagtool.utils import AIRFLOW_VERSION, set_upstream

if TYPE_CHECKING:
    from .utils import TaskMapped


class DefaultArgs(BaseModel):
    """Default Args Model that will use with the `default_args` field with the
    Airflow DAG object.
    """

    owner: str | None = Field(default=None, description="An owner name.")
    depends_on_past: bool = Field(default=False, description="")
    retries: int = Field(default=1, description="A retry count number.")
    retry_delay: dict[str, int] | None = Field(
        default=None,
        description="A retry time delay before start the next retry process.",
    )
    retry_exponential_backoff: bool = Field(default=False)
    sla: Any | None = Field(default=None)

    def to_dict(self) -> dict[str, Any]:
        """Making Python dict object without field that use default value."""
        return self.model_dump(exclude_defaults=True)


class DagModel(BaseModel):
    """Base Dag Model for validate template config data support DagTool object.
    This model will include necessary field for Airflow DAG object and custom
    field for DagTool object together.
    """

    name: str = Field(description="A DAG name.")
    type: Literal["dag"] = Field(description="A type of template config.")
    display_name: str | None = Field(
        default=None,
        description=(
            "A DAG display name that support on Airflow version >= 2.9.0"
        ),
    )
    desc: str | None = Field(default=None, description="A DAG description.")
    docs: str | None = Field(
        default=None,
        description="A DAG document that allow to pass with markdown syntax.",
    )
    params: dict[str, str] = Field(default_factory=dict)
    vars: dict[str, str] = Field(default_factory=dict)
    tasks: list[AnyTask] = Field(
        default_factory=list,
        description="A list of any task, origin task or group task",
    )

    # NOTE: Runtime parameters that extract from YAML loader step.
    filename: str | None = Field(
        default=None,
        description="A filename of the current position.",
    )
    parent_dir: Path | None = Field(
        default=None, description="A parent dir path."
    )
    created_dt: datetime | None = Field(
        default=None, description="A file created datetime."
    )
    updated_dt: datetime | None = Field(
        default=None, description="A file modified datetime."
    )
    raw_data: str | None = Field(
        default=None,
        description="A raw data that load from template config path.",
    )
    raw_data_hash: str | None = Field(
        default=None,
        description="A hashed raw data with SHA256.",
    )

    # NOTE: Airflow DAG parameters.
    owner: str = Field(default="dagtool", description="An owner name.")
    tags: list[str] = Field(default_factory=list, description="A list of tags.")
    schedule: str | None = Field(default=None)
    start_date: datetime | str | None = Field(default=None)
    end_date: datetime | str | None = Field(default=None)
    concurrency: int | None = Field(
        default=None,
        description=(
            "A concurrency value that deprecate when upgrade to Airflow3."
        ),
    )
    is_paused_upon_creation: bool = Field(default=True)
    max_active_tasks: int = Field(
        default_factory=partial(
            airflow_conf.getint, "core", "max_active_tasks_per_dag"
        )
    )
    max_active_runs: int = Field(
        default_factory=partial(
            airflow_conf.getint, "core", "max_active_runs_per_dag"
        )
    )
    dagrun_timeout_sec: int | None = Field(
        default=None,
        description="A DagRun timeout in second value.",
    )
    owner_links: dict[str, str] = Field(default_factory=dict)
    default_args: DefaultArgs = Field(default_factory=DefaultArgs)

    @field_validator(
        "start_date",
        "end_date",
        mode="before",
        json_schema_input_type=str | datetime | None,
    )
    def __prepare_datetime(cls, data: Any) -> Any:
        """Prepare datetime if it passes with datetime string to
        pendulum.Datetime object.
        """
        if data and isinstance(data, str):
            try:
                return parse(data).in_tz(timezone("Asia/Bangkok"))
            except ParserError:
                return None
        return data

    def build_docs(self, docs: str | None = None) -> str:
        """Generated document string that merge between parent docs and template
        docs together.

        Args:
            docs (str, default None): A parent documents that want to add on
                the top of template config docs.

        Returns:
            str: A document markdown string that prepared with parent docs.
        """
        if docs:
            d: str = docs.rstrip("\n")
            docs: str = f"{d}\n\n{self.docs}"

        # NOTE: Exclude jinja template until upgrade Airflow >= 2.9.3, This
        #   version remove template render on the `doc_md` value.
        if AIRFLOW_VERSION <= [2, 9, 3]:
            raw_data: str = f"{{% raw %}}{self.raw_data}{{% endraw %}}"
        else:
            raw_data: str = self.raw_data

        if docs:
            docs += f"\n\n### YAML Template\n\n````yaml\n{raw_data}\n````"
        else:
            docs: str = f"### YAML Template\n\n````yaml\n{raw_data}\n````"
        return f"{docs}\n> Generated by DAG Tools HASH: `{self.raw_data_hash}`."

    def dag_dynamic_kwargs(self) -> dict[str, Any]:
        """Prepare Airflow DAG parameters that do not use for all Airflow
        version.
        """
        kw: dict[str, Any] = {}
        if AIRFLOW_VERSION >= [2, 9, 0]:
            if self.display_name:
                kw.update({"dag_display_name": self.display_name})

        if AIRFLOW_VERSION < [3, 0, 0]:
            if self.concurrency:
                kw.update({"concurrency": self.concurrency})
            if self.tags:
                kw.update({"tags": self.tags})
            kw.update({"default_view": "graph"})

        if AIRFLOW_VERSION > [3, 0, 0]:
            # NOTE: The tags parameters change to mutable set instead of list
            if self.tags:
                kw.update({"tags": set(self.tags)})
        return kw

    def build(
        self,
        prefix: str | None,
        *,
        docs: str | None = None,
        default_args: dict[str, Any] | None = None,
        user_defined_macros: dict[str, Any] | None = None,
        user_defined_filters: dict[str, Any] | None = None,
        template_searchpath: list[str] | None = None,
        on_success_callback: list[Any] | Any | None = None,
        on_failure_callback: list[Any] | Any | None = None,
        context: Context | None = None,
    ) -> DAG:
        """Build Airflow DAG object from the current model field values that
        passing from template and render via Jinja with variables.

        Args:
            prefix (str | None): A prefix of DAG name.
            docs (str | None): A document string with Markdown syntax.
            default_args: (dict[str, Any]): An override default arguments to the
                Airflow DAG object.
            user_defined_macros (dict[str, Any]): An extended user defined
                macros in Jinja template.
            user_defined_filters (dict[str, Any]): An extended user defined
                filters in Jinja template.
            template_searchpath (list[str], default None): An extended Jinja
                template search path.
            on_success_callback:
            on_failure_callback:
            context: A Factory context data that use on task building method.

        Returns:
            DAG: An Airflow DAG object.
        """
        name: str = f"{prefix}_{self.name}" if prefix else self.name
        variables: dict[str, Any] = pull_vars(
            name=self.name, path=self.parent_dir, prefix=prefix
        )
        macros: dict[str, Callable | str] = {
            "env": os.getenv,
            "vars": variables.get,
            "dag_id_prefix": prefix,
        }
        dag = DAG(
            dag_id=name,
            description=self.desc,
            doc_md=self.build_docs(docs),
            schedule=self.schedule,
            start_date=self.start_date,
            end_date=self.end_date,
            max_active_runs=self.max_active_runs,
            max_active_tasks=self.max_active_tasks,
            dagrun_timeout=(
                timedelta(seconds=self.dagrun_timeout_sec)
                if self.dagrun_timeout_sec
                else None
            ),
            default_args=(
                {"owner": self.owner}
                | self.default_args.to_dict()
                | DefaultArgs.model_validate(default_args or {}).to_dict()
            ),
            template_searchpath=(template_searchpath or []),
            user_defined_macros=macros | (user_defined_macros or {}),
            user_defined_filters=(user_defined_filters or {}),
            render_template_as_native_obj=True,
            is_paused_upon_creation=self.is_paused_upon_creation,
            on_success_callback=on_success_callback,
            on_failure_callback=on_failure_callback,
            owner_links=self.owner_links,
            **self.dag_dynamic_kwargs(),
        )

        # NOTE: Build Tasks.
        tasks: dict[str, TaskMapped] = {}
        for task in self.tasks:
            tasks[task.iden] = {
                "upstream": task.upstream,
                "task": task.build(task_group=None, dag=dag, context=context),
            }

        # NOTE: Set upstream for each task.
        set_upstream(tasks)

        # NOTE: Set property for DAG object.
        dag.is_dag_auto_generated = True

        return dag


Primitive = Union[str, int, float, bool]
ValueType = Union[Primitive, list[Primitive], dict[Union[str, int], Primitive]]


class Key(BaseModel):
    """Key Model that use to store multi-stage variable with a specific key."""

    key: str = Field(
        description="A key name that will equal with the DAG name.",
    )
    desc: str | None = Field(
        default=None,
        description="A description of this variable.",
    )
    stages: dict[str, dict[str, ValueType]] = Field(
        default=dict,
        description="A stage mapping with environment and its pair of variable",
    )


class Variable(BaseModel):
    """Variable Model."""

    type: Literal["variable"] = Field(description="A type of this variable.")
    variables: list[Key] = Field(description="A list of Key model.")

    @classmethod
    def from_path(cls, path: Path) -> Self:
        return cls.model_validate(YamlConf(path=path).read_vars())

    @classmethod
    def from_path_with_key(cls, path: Path, key: str) -> dict[str, Any]:
        """Get Variable stage from path.

        Args:
            path (Path): A template path.
            key (str): A key name that want to get from Variable model.

        Returns:
            dict[str, Any]: A mapping of variables that set on the current stage.
                It will return empty dict if it raises FileNotFoundError and
                ValueError exceptions.
        """
        try:
            return (
                cls.from_path(path=path)
                .get_key(key)
                .stages.get(os.getenv("AIRFLOW_ENV", "NOTSET"), {})
            )
        except FileNotFoundError:
            return {}
        except YamlParserError:
            raise
        except ValidationError:
            raise
        except ValueError:
            return {}

    def get_key(self, name: str) -> Key:
        """Get the Key model with an input specific key name.

        Args:
            name (str): A key name.

        Raises:
            ValueError: If the key does not exist on this Variable model.

        Returns:
            Key: A Key model.
        """
        for k in self.variables:
            if name == k.key:
                return k
        raise ValueError(f"A key: {name} does not set on this variables.")


def pull_vars(name: str, path: Path, prefix: str | None) -> dict[str, Any]:
    """Pull Variable. This method try to pull variable from Airflow Variable
    first. If it does not exist it will load from local file instead.

    Args:
        name (str): A name.
        path (Path): A template path that want to search variable file.
        prefix (str, default None): A prefix name that use to combine with name.

    Returns:
        dict[str, Any]: A variable mapping. This method will return empty dict
            if it gets any exceptions.
    """
    try:
        _name: str = f"{prefix}_{name}" if prefix else name
        raw_var: str = AirflowVariable.get(_name, deserialize_json=False)
        var: dict[str, Any] = safe_load(raw_var)
        return var
    except (
        KeyError,
        # NOTE: Raise from Airflow version >= 3.0.0 instead of KeyError.
        AirflowRuntimeError,
    ):
        pass
    except ImportError as err:  # NOTE: Raise from Airflow version >= 3.0.0
        if "cannot import name 'SUPERVISOR_COMMS'" not in str(err):
            raise
        pass

    try:
        return Variable.from_path_with_key(path, key=name)
    except YamlParserError:
        return {}
    except ValidationError:
        return {}
