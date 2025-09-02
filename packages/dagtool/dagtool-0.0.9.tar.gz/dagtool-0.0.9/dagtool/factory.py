from __future__ import annotations

import json
import logging
import os
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

from jinja2 import Environment, Template
from jinja2.nativetypes import NativeEnvironment
from pydantic import ValidationError

from dagtool.conf import ASSET_DIR, YamlConf
from dagtool.models import DagModel, pull_vars
from dagtool.tasks import Context, TaskModel
from dagtool.utils import FILTERS, clear_globals

if TYPE_CHECKING:
    try:
        from airflow.sdk.bases.operator import BaseOperator
        from airflow.sdk.definitions.dag import DAG
        from airflow.sdk.definitions.mappedoperator import MappedOperator
    except ImportError:
        from airflow.models.baseoperator import BaseOperator
        from airflow.models.dag import DAG
        from airflow.models.mappedoperator import MappedOperator

    Operator = BaseOperator | MappedOperator

logger = logging.getLogger("dagtool.factory")


class Factory:
    """Factory object that is the main interface for retrieve tempalte config
    data from the current path and generate Airflow DAG object.

    Warnings:
        It is common for dags not to appear due to the `dag_discovery_safe_mode`
        (https://airflow.apache.org/docs/apache-airflow/stable/configurations-ref.html#dag-discovery-safe-mode)

        > If enabled, Airflow will only scan files containing both DAG and
        > airflow (case-insensitive).

        Add this statement on the top of the Factory file.
        >>> # NOTE: Add this statement for Airflow DAG Processor.
        >>> # from airflow import DAG

    Examples:
        Create the Custom factory that use standard with your operators.
        >>> from dagtool import Factory
        >>> class CustomFactory(Factory):
        ...     builtin_operators = {
        ...         "some-operator-name": ...,
        ...     }

    Attributes:
        name (str): A prefix name that will use for making DAG inside this dir.
        path (Path): A parent path for searching tempalate config files.
        docs (str, default None): A parent document that use to add before the
            template DAG document.

        template_searchpath (list[str | Path] , default None):
        user_defined_filters (dict[str, Callable] , default None):
        user_defined_macros (dict[str, Callable | str] , default None):
        on_success_callback (list[Any] | Any , default None):
        on_failure_callback (list[Any] | Any , default None):
    """

    # NOTE: Template fields for DAG parameters that will use on different
    #   stages like `catchup` parameter that should disable when deploy to dev.
    template_fields: ClassVar[Sequence[str]] = (
        "schedule",
        "start_date",
        "end_date",
        "catchup",
        "tags",
        "max_active_tasks",
        "max_active_runs",
        "vars",
    )

    # NOTE: Builtin class variables for making custom Factory by inherit.
    builtin_operators: ClassVar[dict[str, type[Operator]]] = {}
    builtin_tasks: ClassVar[dict[str, type[TaskModel]]] = {}

    def __init__(
        self,
        name: str,
        path: str | Path,
        *,
        docs: str | None = None,
        operators: dict[str, type[Operator]] | None = None,
        tasks: dict[str, type[TaskModel]] | None = None,
        python_callers: dict[str, Callable] | None = None,
        template_searchpath: list[str | Path] | None = None,
        user_defined_filters: dict[str, Callable] | None = None,
        user_defined_macros: dict[str, Callable | str] | None = None,
        on_success_callback: list[Any] | Any | None = None,
        on_failure_callback: list[Any] | Any | None = None,
    ) -> None:
        """Main construct method.

        Args:
            name (str): A prefix name of final DAG.
            path (str | Path): A current filepath that can receive with string
                value or Path object.
            docs (dict[str, Any]): A docs string for this Factory will use to
                be the header of full docs.
            operators (dict[str, type[TaskModel]]): A mapping of name and sub-model
                of TaskModel model.
            python_callers (dict[str, Callable]): A mapping of name and function
                that want to use with Airflow PythonOperator.
            template_searchpath (list[str | Path]): A list of Jinja template
                search path.
            user_defined_filters (dict[str, Callable]): An user defined Jinja
                template filters that will add to Jinja environment.
            user_defined_macros (dict[str, Callable | str]): An user defined
                Jinja template macros that will add to Jinja environment.
            on_success_callback: An on success event callback object that want
                to use on each DAG that was built from template path.
            on_failure_callback: An on failure event callback object that want
                to use on each DAG that was built from template path.

        Notes:
            After set the Factory attributes, it will load template config data
        from the current path and skip template file if it does not read or
        match with template config rules like include `type=dag`.
        """
        self.name: str = name
        self.path: Path = p.parent if (p := Path(path)).is_file() else p
        self.docs: str | None = docs
        self.conf: dict[str, DagModel] = {}
        self.yaml_loader = YamlConf(path=self.path)

        # NOTE: Set Extended Airflow params with necessary values.
        self.template_searchpath: list[str] = [
            str(p.absolute()) if isinstance(p, Path) else p
            for p in (template_searchpath or [])
        ] + [str((self.path / ASSET_DIR).absolute())]
        self.user_defined_filters = FILTERS | (user_defined_filters or {})
        self.user_defined_macros = user_defined_macros or {}
        self.on_success_callback = on_success_callback
        self.on_failure_callback = on_failure_callback

        # NOTE: Define tasks that able map to template.
        self.operators: dict[str, type[Operator]] = self.builtin_operators | (
            operators or {}
        )
        self.tasks: dict[str, type[TaskModel]] = self.builtin_tasks | (
            tasks or {}
        )
        self.python_callers: dict[str, Any] = python_callers or {}

        # NOTE: Fetching config data from template path.
        self.refresh_conf()

    def refresh_conf(self) -> None:
        """Read config from the path argument and reload to the conf.

            This method will render Jinja template to the DagModel fields raw
        value that match key with the template_fields before start validate the
        model.
        """
        # NOTE: Reset previous if it exists.
        if self.conf:
            self.conf: dict[str, DagModel] = {}

        # NOTE: For loop DAG config that store inside this template path.
        for c in self.yaml_loader.read_conf():
            name: str = c["name"]
            env: Environment = self.get_template_env(
                user_defined_macros={
                    "vars": pull_vars(name, self.path, prefix=self.name).get,
                    "env": os.getenv,
                }
                | self.user_defined_macros,
                user_defined_filters=self.user_defined_filters,
            )
            self.render_template(c, env=env)
            try:
                model = DagModel.model_validate(c)
                self.conf[name] = model
            except ValidationError:
                continue

    def set_context(
        self,
        custom_vars: dict[str, Any] | None = None,
        extras: dict[str, Any] | None = None,
    ) -> Context:
        """Set context data that bypass to the build method."""
        _vars: dict[str, Any] = custom_vars or {}
        _extras: dict[str, Any] = extras or {}
        return {
            "path": self.path,
            "yaml_loader": self.yaml_loader,
            "tasks": self.tasks,
            "operators": self.operators,
            "python_callers": self.python_callers,
            "vars": _vars,
            "extras": _extras,
        }

    def render_template(self, data: Any, env: Environment) -> Any:
        """Render template to the value of key that exists in the
        `template_fields` class variable.

        Args:
            data (Any): Any data that want to render Jinja template.
            env (Environment): A Jinja environment.
        """
        for key in data:
            if key == "default_args":
                data[key] = self.render_template(data[key], env=env)
                continue

            if key in ("tasks", "raw_data") or key not in self.template_fields:
                continue

            data[key] = self._render(data[key], env=env)
        return data

    def _render(self, value: Any, env: Environment) -> Any:
        """Render Jinja template to any value with the current Jinja environment.

            This private method will check the type of value before make Jinja
        template and render it before returning.

        Args:
            value (Any): An any value.
            env (Environment): A Jinja environment object.
        """
        if isinstance(value, str):
            template: Template = env.from_string(value)
            return template.render()

        if value.__class__ is tuple:
            return tuple(self._render(element, env) for element in value)
        elif isinstance(value, tuple):
            return value.__class__(*(self._render(el, env) for el in value))
        elif isinstance(value, list):
            return [self._render(element, env) for element in value]
        elif isinstance(value, dict):
            return {k: self._render(v, env) for k, v in value.items()}
        elif isinstance(value, set):
            return {self._render(element, env) for element in value}

        return value

    def get_template_env(
        self,
        *,
        user_defined_filters: dict[str, Callable] | None = None,
        user_defined_macros: dict[str, Callable | str] | None = None,
    ) -> Environment:
        """Return Jinja Template Native Environment object for render template
        to the DagModel parameters before create Airflow DAG.

        Args:
            user_defined_filters (dict[str, Callable]): An user defined Jinja
                template filters that will add to Jinja environment.
            user_defined_macros (dict[str, Callable | str]): An user defined
                Jinja template macros that will add to Jinja environment.
        """
        env: Environment = NativeEnvironment()
        udf_macros: dict[str, Any] = self.user_defined_macros | (
            user_defined_macros or {}
        )
        if udf_macros:
            env.globals.update(udf_macros)
        udf_filters: dict[str, Any] = self.user_defined_filters | (
            user_defined_filters or {}
        )
        if udf_filters:
            env.filters.update(udf_macros)
        return env

    def build(
        self,
        default_args: dict[str, Any] | None = None,
        context_extras: dict[str, Any] | None = None,
    ) -> list[DAG]:
        """Build Airflow DAGs from template files.

        Args:
            default_args (dict[str, Any]): A mapping of default arguments that
                want to override on the template config data.
            context_extras (dict[str, Any]): A context extras.

        Returns:
            list[DAG]: A list of Airflow DAG object.
        """
        logger.info("Start build DAG from Template config data.")
        dags: list[DAG] = []
        context: Context = self.set_context(extras=context_extras)
        for name, model in self.conf.items():
            dag: DAG = model.build(
                prefix=self.name,
                docs=self.docs,
                default_args=default_args,
                user_defined_macros=self.user_defined_macros | model.vars,
                user_defined_filters=self.user_defined_filters,
                template_searchpath=self.template_searchpath,
                on_success_callback=self.on_success_callback,
                on_failure_callback=self.on_failure_callback,
                # NOTE: Copy the Context data and add the current custom vars.
                context=context | {"vars": model.vars},
            )
            logger.info(f"({name}) Building DAG: {dag}")
            dags.append(dag)
        return dags

    def build_airflow_dags_to_globals(
        self,
        gb: dict[str, Any],
        *,
        default_args: dict[str, Any] | None = None,
        context_extras: dict[str, Any] | None = None,
    ) -> None:
        """Build Airflow DAG object and set to the globals for Airflow Dag Processor
        can discover them.

        Warnings:
            This method name should include `airflow` and `dag` value because the
        Airflow DAG processor need these words for soft scan DAG file.

        Args:
            gb (dict[str, Any]): A globals object.
            default_args (dict[str, Any]): An override default args value.
            context_extras (dict[str, Any]): A context extras.
        """
        if gb:
            logger.debug("DEBUG: The current globals variables before build.")
            logger.debug(json.dumps(clear_globals(gb), default=str, indent=1))

        for dag in self.build(
            default_args=default_args,
            context_extras=context_extras,
        ):
            gb[dag.dag_id] = dag
