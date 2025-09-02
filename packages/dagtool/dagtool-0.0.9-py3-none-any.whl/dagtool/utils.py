from __future__ import annotations

import hashlib
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any, Final, TypedDict

try:
    from airflow.sdk.bases.operator import BaseOperator
    from airflow.sdk.definitions.mappedoperator import MappedOperator
    from airflow.sdk.definitions.taskgroup import TaskGroup
except ImportError:
    from airflow.models.baseoperator import BaseOperator
    from airflow.models.mappedoperator import MappedOperator
    from airflow.utils.task_group import TaskGroup

from airflow.version import version as airflow_version
from pendulum import DateTime

Operator = BaseOperator | MappedOperator


class TaskMapped(TypedDict):
    """Task Mapped dict typed."""

    upstream: list[str]
    task: Operator | TaskGroup


def set_upstream(tasks: dict[str, TaskMapped]) -> None:
    """Set Upstream Task for each tasks in mapping.

    Args:
        tasks: A mapping of task_id and TaskMapped dict object.
    """
    for task in tasks:
        task_mapped: TaskMapped = tasks[task]
        if upstream := task_mapped["upstream"]:
            for t in upstream:
                try:
                    task_mapped["task"].set_upstream(tasks[t]["task"])
                except KeyError as e:
                    raise KeyError(
                        f"Task ids, {e}, does not found from the template."
                    ) from e


def change_tz(dt: DateTime | None, tz: str = "UTC") -> DateTime | None:
    """Change timezone to pendulum.DateTime object."""
    if dt is None:
        return None
    return dt.in_timezone(tz)


def format_dt(
    dt: datetime | DateTime | None, fmt: str = "%Y-%m-%d %H:00:00%z"
) -> str | None:
    """Format string value on pendulum.DateTime or datetime object"""
    if dt is None:
        return None
    return dt.strftime(fmt)


# NOTE: Defined builtin filters for this package.
FILTERS: Final[dict[str, Callable]] = {
    "tz": change_tz,
    "fmt": format_dt,
}


def hash_sha256(data: str | bytes) -> str:
    """Calculates the SHA-256 hash of the given data.

    Args:
        data (str or bytes): The input data to be hashed.

    Returns:
        str: The hexadecimal representation of the SHA-256 hash.
    """
    if isinstance(data, str):
        # NOTE: Encode string to bytes
        data = data.encode("utf-8")

    sha256_hash = hashlib.sha256()
    sha256_hash.update(data)
    return sha256_hash.hexdigest()


def days_ago(n, hour=0, minute=0, second=0, microsecond=0):
    """Get a datetime object representing `n` days ago. By default, the time is
    set to midnight.
    """
    today = datetime.now().replace(
        hour=hour, minute=minute, second=second, microsecond=microsecond
    )
    return today - timedelta(days=n)


def parse_version(version: str) -> list[int]:
    vs: list[str] = version.split(".")
    return [int(vs[_]) for _ in range(3)]


AIRFLOW_VERSION: list[int] = parse_version(airflow_version)


def clear_globals(gb: dict[str, Any]) -> dict[str, Any]:
    """Clear Globals variable support keeping necessary values only."""
    return {k: gb[k] for k in gb if k not in ("__builtins__", "__cached__")}
