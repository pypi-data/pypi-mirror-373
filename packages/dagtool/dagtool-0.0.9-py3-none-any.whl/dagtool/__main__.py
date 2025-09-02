import json
import sys

import click
from pydantic import TypeAdapter

from .__about__ import __version__
from .models import DagModel


@click.group()
def cli() -> None:
    """Main Tool CLI."""


@cli.command("version")
def version() -> None:
    click.echo(__version__)
    sys.exit(0)


@cli.command("sync-vars")
def sync_airflow_variable():
    click.echo("Sync Airflow Variable does not implement yet.")
    click.echo(
        """Steps:
        - Search Variable files reference the `.airflowignore` pattern.
        - Prepare variable with prefix name.
        - Sync to the target Airflow Variable.
        """
    )
    sys.exit(1)


@cli.command("json-schema")
def build_json_schema():
    click.echo("Start generate JSON Schema file for DAG Template.")
    json_schema = TypeAdapter(DagModel).json_schema(by_alias=True)
    with open("./json-schema.json", mode="w") as f:
        json.dump(json_schema, f, indent=2)


if __name__ == "__main__":
    cli()
