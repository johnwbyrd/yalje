"""Main CLI application."""

import click

from yalje import __version__
from yalje.utils.logging import setup_logging


@click.group()
@click.version_option(version=__version__)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose (DEBUG) logging",
)
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    help="Enable quiet (WARNING) logging",
)
@click.pass_context
def cli(ctx: click.Context, verbose: bool, quiet: bool) -> None:
    """yalje - Yet Another LiveJournal Exporter

    Download and archive all content from LiveJournal accounts.
    """
    # Determine log level
    if verbose:
        log_level = "DEBUG"
    elif quiet:
        log_level = "WARNING"
    else:
        log_level = "INFO"

    # Initialize logging
    setup_logging(level=log_level)

    # Store in context for subcommands to access if needed
    ctx.ensure_object(dict)
    ctx.obj["log_level"] = log_level


# Import commands to register them
from yalje.cli.commands import auth, convert, download  # noqa: E402, F401

if __name__ == "__main__":
    cli()
