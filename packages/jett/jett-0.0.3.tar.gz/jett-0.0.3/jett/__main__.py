import json
import sys
from functools import partial
from pathlib import Path

import click
from pydantic import TypeAdapter

from jett.__about__ import __version__
from jett.engine import Engine
from jett.tools import ToolModel

st_bold = partial(click.style, bold=True)
st_bold_red = partial(click.style, bold=True, fg="red")
st_bold_green = partial(click.style, bold=True, fg="green")
echo = click.echo


@click.group()
def cli() -> None:
    """Main Jett Command Line Interface ."""


@cli.command("version")
def version() -> None:
    """Return the current version of jett package that already installed
    on your Python environment.
    """
    echo(__version__)
    sys.exit(0)


@cli.command("json-schema")
@click.option(
    "--output-file",
    type=click.Path(
        exists=False,
        file_okay=True,
        dir_okay=False,
        path_type=Path,
    ),
    help="JSON Schema filepath that want to write after generate.",
)
def gen_json_schema(output_file: Path | None = None) -> None:  # pragma: no cov
    """Generate JSON Schema for validate Jett configuration YAML template.

    \f
    Args:
        output_file (Path, default None): An output filepath that want to use
            for writing JSON Schema data after generated.
    """
    json_schema = TypeAdapter(Engine).json_schema(by_alias=True)
    template_schema: dict[str, str] = {
        "$schema": "http://json-schema.org/draft/2020-12/schema",
        "$id": "https://example.com/yapt.schema.json",
        "title": "Jett",
        "description": "DE Tool Configuration JSON Schema",
        "version": __version__,
    }
    echo(
        st_bold_green(
            "Start generate or rewrite the current JSON schema file ..."
        )
    )
    out_file = output_file or Path("./json-schema.json")
    with open(out_file, mode="w") as f:
        json.dump(template_schema | json_schema, f, indent=2)


@cli.command("validate")
@click.option(
    "--file",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        path_type=Path,
    ),
    help="A Jett config file path.",
)
def validate_conf(file: Path):
    """Validate Jett config file."""
    try:
        tool = ToolModel.from_yaml(path=file)
        echo(st_bold_green(f"✅ Tool config ({file}) is valid !!"))
        echo(f"> Name: {tool.model.name}")
        echo(f"> Author: {tool.model.author or 'Anon'}")
        echo(f"> Engine Type: {tool.model.type}")
    except Exception as e:
        echo(st_bold_red(f"❌ Tool config ({file}) is invalid !!"))
        raise e


@cli.command("run")
@click.option(
    "--file",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        path_type=Path,
    ),
)
def run(file: Path):
    # NOTE: Start Validate first.
    validate_conf(file)
    sys.exit(0)


if __name__ == "__main__":
    cli()
