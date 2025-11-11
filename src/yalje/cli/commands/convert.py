"""Format conversion CLI commands."""

from pathlib import Path

import click

from yalje.cli.main import cli


@cli.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--format",
    type=click.Choice(["yaml", "json"], case_sensitive=False),
    required=True,
    help="Output format",
)
@click.option("--output", type=click.Path(path_type=Path), help="Output file path")
def convert(input_file: Path, format: str, output: Path) -> None:
    """Convert export file between formats.

    Convert a YAML export to JSON, or vice versa.
    """
    # TODO: Implement
    # 1. Detect input format
    # 2. Load using appropriate exporter
    # 3. Export using target format
    # 4. Write to output file
    click.echo(
        f"Convert command not yet implemented. Would convert {input_file} to {format} format"
    )
