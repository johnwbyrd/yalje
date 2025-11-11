"""Download CLI commands."""

from pathlib import Path

import click

from yalje.cli.main import cli


@cli.command()
@click.option("--username", help="LiveJournal username")
@click.option("--password", help="LiveJournal password")
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    default="lj-backup.yaml",
    help="Output file path",
)
@click.option("--no-posts", is_flag=True, help="Skip posts download")
@click.option("--no-comments", is_flag=True, help="Skip comments download")
@click.option("--no-inbox", is_flag=True, help="Skip inbox download")
@click.option("--start-year", type=int, help="Start year for posts")
@click.option("--start-month", type=int, help="Start month for posts (1-12)")
@click.option("--end-year", type=int, help="End year for posts")
@click.option("--end-month", type=int, help="End month for posts (1-12)")
def download(
    username: str,
    password: str,
    output: Path,
    no_posts: bool,
    no_comments: bool,
    no_inbox: bool,
    start_year: int,
    start_month: int,
    end_year: int,
    end_month: int,
) -> None:
    """Download all LiveJournal content to a single YAML file.

    This will download posts, comments, and inbox messages and save
    everything to a single YAML file.
    """
    # TODO: Implement
    # 1. Create config
    # 2. Authenticate (or use saved session)
    # 3. Create API clients
    # 4. Download posts (if not skipped)
    # 5. Download comments (if not skipped)
    # 6. Download inbox (if not skipped)
    # 7. Create LJExport object
    # 8. Export to YAML
    # 9. Show progress with rich
    click.echo(f"Download command not yet implemented. Would write to: {output}")
