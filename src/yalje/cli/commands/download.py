"""Download CLI commands."""

from pathlib import Path
from typing import Optional

import click

from yalje import __version__
from yalje.api.comments import CommentsClient
from yalje.api.inbox import InboxClient
from yalje.api.posts import PostsClient
from yalje.cli.main import cli
from yalje.core.auth import Authenticator
from yalje.core.config import YaljeConfig
from yalje.core.exceptions import AuthenticationError, YaljeError
from yalje.exporters.yaml_exporter import YAMLExporter
from yalje.models.comment import Comment
from yalje.models.export import ExportMetadata, LJExport
from yalje.models.inbox import InboxMessage
from yalje.models.post import Post
from yalje.models.user import User
from yalje.utils.logging import get_logger

logger = get_logger("cli.download")


@cli.command()
@click.option("--username", help="LiveJournal username (overrides .env)")
@click.option("--password", help="LiveJournal password (overrides .env)")
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
    username: Optional[str],
    password: Optional[str],
    output: Path,
    no_posts: bool,
    no_comments: bool,
    no_inbox: bool,
    start_year: Optional[int],
    start_month: Optional[int],
    end_year: Optional[int],
    end_month: Optional[int],
) -> None:
    """Download all LiveJournal content to a single YAML file.

    This will download posts, comments, and inbox messages and save
    everything to a single YAML file.

    Examples:

        \b
        # Download everything using credentials from .env file
        $ yalje download

        \b
        # Download with explicit credentials
        $ yalje download --username myuser --password mypass

        \b
        # Download only posts (skip comments and inbox)
        $ yalje download --no-comments --no-inbox

        \b
        # Download posts for specific date range
        $ yalje download --start-year 2020 --start-month 1 --end-year 2023 --end-month 12
    """
    try:
        # Load configuration from .env and merge with CLI args
        click.echo("Loading configuration...")
        try:
            config = YaljeConfig()
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            click.echo(f"Error: Failed to load configuration: {e}")
            click.echo("\nMake sure you have a .env file with YALJE_USERNAME and YALJE_PASSWORD")
            click.echo("or provide --username and --password options")
            raise click.Abort() from None

        # Override config with CLI arguments if provided
        if username:
            config.username = username
        if password:
            config.password = password

        # Validate required credentials
        if not config.username or not config.password:
            logger.error("Missing credentials")
            click.echo("Error: Username and password are required")
            click.echo("\nEither:")
            click.echo("  1. Create .env file with YALJE_USERNAME and YALJE_PASSWORD")
            click.echo("  2. Use --username and --password options")
            raise click.Abort()

        click.echo(f"Username: {config.username}")
        click.echo()

        # Authenticate
        click.echo("Authenticating with LiveJournal...")
        try:
            auth = Authenticator(config)
            session = auth.login(config.username, config.password)
            click.echo("✓ Authentication successful")
            click.echo()
        except AuthenticationError as e:
            logger.error(f"Authentication failed: {e}")
            click.echo(f"✗ Authentication failed: {e}")
            click.echo("\nPlease check your username and password")
            raise click.Abort() from None

        # Create API clients
        posts_client = PostsClient(session, config)
        comments_client = CommentsClient(session, config)
        inbox_client = InboxClient(session, config)

        # Initialize data containers
        posts: list[Post] = []
        comments: list[Comment] = []
        usermap: list[User] = []
        inbox_messages: list[InboxMessage] = []

        # Download posts
        if not no_posts:
            click.echo("=" * 70)
            click.echo("Downloading posts...")
            click.echo("=" * 70)
            try:
                posts = posts_client.download_all(
                    start_year=start_year,
                    start_month=start_month,
                    end_year=end_year,
                    end_month=end_month,
                )
                click.echo(f"✓ Downloaded {len(posts)} posts")
                click.echo()
            except Exception as e:
                logger.error(f"Posts download failed: {e}")
                click.echo(f"✗ Posts download failed: {e}")
                raise click.Abort() from None
        else:
            click.echo("Skipping posts download")
            click.echo()

        # Download comments
        if not no_comments:
            click.echo("=" * 70)
            click.echo("Downloading comments...")
            click.echo("=" * 70)
            try:
                comments, usermap = comments_client.download_all()
                click.echo(f"✓ Downloaded {len(comments)} comments")
                click.echo(f"✓ Downloaded usermap with {len(usermap)} users")
                click.echo()
            except Exception as e:
                logger.error(f"Comments download failed: {e}")
                click.echo(f"✗ Comments download failed: {e}")
                raise click.Abort() from None
        else:
            click.echo("Skipping comments download")
            click.echo()

        # Download inbox
        if not no_inbox:
            click.echo("=" * 70)
            click.echo("Downloading inbox...")
            click.echo("=" * 70)
            try:
                inbox_messages = inbox_client.download_all()
                click.echo(f"✓ Downloaded {len(inbox_messages)} inbox messages")
                click.echo()
            except Exception as e:
                logger.error(f"Inbox download failed: {e}")
                click.echo(f"✗ Inbox download failed: {e}")
                raise click.Abort() from None
        else:
            click.echo("Skipping inbox download")
            click.echo()

        # Create export object
        click.echo("=" * 70)
        click.echo("Creating export...")
        click.echo("=" * 70)
        metadata = ExportMetadata(
            lj_user=config.username,
            yalje_version=__version__,
        )
        export = LJExport(
            metadata=metadata,
            posts=posts,
            comments=comments,
            usermap=usermap,
            inbox_messages=inbox_messages,
        )

        # Export to YAML
        click.echo(f"Writing to {output}...")
        try:
            exporter = YAMLExporter()
            exporter.export(export, output)
            click.echo(f"✓ Export saved to {output}")
            click.echo()
        except Exception as e:
            logger.error(f"Export failed: {e}")
            click.echo(f"✗ Export failed: {e}")
            raise click.Abort() from None

        # Show summary
        click.echo("=" * 70)
        click.echo("Download complete!")
        click.echo("=" * 70)
        click.echo(f"Output file: {output}")
        click.echo(f"  Posts: {len(posts)}")
        click.echo(f"  Comments: {len(comments)}")
        click.echo(f"  Usermap: {len(usermap)} users")
        click.echo(f"  Inbox: {len(inbox_messages)} messages")
        click.echo()

    except click.Abort:
        raise
    except KeyboardInterrupt:
        click.echo("\n\nDownload interrupted by user")
        raise click.Abort() from None
    except YaljeError as e:
        logger.error(f"yalje error: {e}")
        click.echo(f"\n✗ Error: {e}")
        raise click.Abort() from None
    except Exception as e:
        logger.exception("Unexpected error during download")
        click.echo(f"\n✗ Unexpected error: {e}")
        click.echo("Check logs for details")
        raise click.Abort() from None
