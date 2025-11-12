"""Authentication CLI commands (not yet implemented)."""

# TODO: These auth commands are not yet implemented
# Once needed, they should be added as subcommands to the main CLI
# using @click.group() pattern or as separate entry points

# import click
#
# @cli.group()
# def auth() -> None:
#     """Authentication commands."""
#     pass
#
# @auth.command()
# @click.option("--username", prompt=True, help="LiveJournal username")
# @click.option("--password", prompt=True, hide_input=True, help="LiveJournal password")
# def login(username: str, password: str) -> None:
#     """Login to LiveJournal and save session."""
#     # 1. Create config
#     # 2. Authenticate
#     # 3. Save session cookies to ~/.yalje/session
#     click.echo("Login command not yet implemented")
#
# @auth.command()
# def logout() -> None:
#     """Logout and clear saved session."""
#     # 1. Clear session cookies from ~/.yalje/session
#     click.echo("Logout command not yet implemented")
#
# @auth.command()
# def status() -> None:
#     """Check authentication status."""
#     # 1. Check if session exists
#     # 2. Validate session is still active
#     # 3. Display username if logged in
#     click.echo("Status command not yet implemented")
