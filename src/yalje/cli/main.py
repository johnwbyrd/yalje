"""Main CLI application."""

import click

from yalje import __version__


@click.group()
@click.version_option(version=__version__)
def cli() -> None:
    """yalje - Yet Another LiveJournal Exporter

    Download and archive all content from LiveJournal accounts.
    """
    pass


# Import commands to register them
from yalje.cli.commands import auth, download, convert  # noqa: E402, F401


if __name__ == "__main__":
    cli()
