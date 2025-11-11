"""Authentication CLI commands."""

import click

from yalje.cli.main import cli


@cli.group()
def auth() -> None:
    """Authentication commands."""
    pass


@auth.command()
@click.option("--username", prompt=True, help="LiveJournal username")
@click.option("--password", prompt=True, hide_input=True, help="LiveJournal password")
def login(username: str, password: str) -> None:
    """Login to LiveJournal and save session."""
    # TODO: Implement
    # 1. Create config
    # 2. Authenticate
    # 3. Save session cookies to ~/.yalje/session
    click.echo("Login command not yet implemented")


@auth.command()
def logout() -> None:
    """Logout and clear saved session."""
    # TODO: Implement
    # 1. Clear session cookies from ~/.yalje/session
    click.echo("Logout command not yet implemented")


@auth.command()
def status() -> None:
    """Check authentication status."""
    # TODO: Implement
    # 1. Check if session exists
    # 2. Validate session is still active
    # 3. Display username if logged in
    click.echo("Status command not yet implemented")
