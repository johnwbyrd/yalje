"""Main CLI application."""

from pathlib import Path
from typing import Optional

import click

from yalje import __version__
from yalje.api.comments import CommentsClient
from yalje.api.inbox import InboxClient
from yalje.api.posts import PostsClient
from yalje.core.auth import Authenticator
from yalje.core.config import YaljeConfig
from yalje.core.exceptions import AuthenticationError, YaljeError
from yalje.exporters.yaml_exporter import YAMLExporter
from yalje.models.comment import Comment
from yalje.models.export import ExportMetadata, LJExport
from yalje.models.inbox import InboxMessage
from yalje.models.post import Post
from yalje.models.user import User
from yalje.utils.logging import get_logger, setup_logging

logger = get_logger("cli.main")


@click.command()
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
@click.option("--username", help="LiveJournal username (overrides .env)")
@click.option("--password", help="LiveJournal password (overrides .env)")
@click.option(
    "--output",
    "-o",
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
def cli(
    verbose: bool,
    quiet: bool,
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
    """yalje - Yet Another LiveJournal Exporter

    Download and archive all content from LiveJournal accounts.

    Examples:

        \b
        # Download everything using credentials from .env file
        $ yalje

        \b
        # Download with explicit credentials
        $ yalje --username myuser --password mypass

        \b
        # Download only posts (skip comments and inbox)
        $ yalje --no-comments --no-inbox

        \b
        # Download posts for specific date range
        $ yalje --start-year 2020 --start-month 1 --end-year 2023 --end-month 12

        \b
        # Specify output file
        $ yalje --output my-backup.yaml
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

    try:
        # Load configuration from .env and merge with CLI args
        logger.info("Loading configuration...")
        try:
            config = YaljeConfig()
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            logger.error("Make sure you have a .env file with YALJE_USERNAME and YALJE_PASSWORD")
            logger.error("or provide --username and --password options")
            raise click.Abort() from None

        # Override config with CLI arguments if provided
        if username:
            config.username = username
        if password:
            config.password = password

        # Validate required credentials
        if not config.username or not config.password:
            logger.error("Username and password are required")
            logger.error("Either:")
            logger.error("  1. Create .env file with YALJE_USERNAME and YALJE_PASSWORD")
            logger.error("  2. Use --username and --password options")
            raise click.Abort()

        logger.info(f"Username: {config.username}")

        # Authenticate
        logger.info("Authenticating with LiveJournal...")
        try:
            auth = Authenticator(config)
            session = auth.login(config.username, config.password)
            logger.info("Authentication successful")
        except AuthenticationError as e:
            logger.error(f"Authentication failed: {e}")
            logger.error("Please check your username and password")
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
            try:
                posts = posts_client.download_all(
                    start_year=start_year,
                    start_month=start_month,
                    end_year=end_year,
                    end_month=end_month,
                )
                logger.info(f"Downloaded {len(posts)} posts")
            except Exception as e:
                logger.error(f"Posts download failed: {e}")
                raise click.Abort() from None
        else:
            logger.info("Skipping posts download")

        # Download comments
        if not no_comments:
            try:
                comments, usermap = comments_client.download_all()
                logger.info(f"Downloaded {len(comments)} comments")
                logger.info(f"Downloaded usermap with {len(usermap)} users")
            except Exception as e:
                logger.error(f"Comments download failed: {e}")
                raise click.Abort() from None
        else:
            logger.info("Skipping comments download")

        # Download inbox
        if not no_inbox:
            try:
                inbox_messages = inbox_client.download_all()
                logger.info(f"Downloaded {len(inbox_messages)} inbox messages")
            except Exception as e:
                logger.error(f"Inbox download failed: {e}")
                raise click.Abort() from None
        else:
            logger.info("Skipping inbox download")

        # Create export object
        logger.info("Creating export...")
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
        logger.info(f"Writing to {output}...")
        try:
            exporter = YAMLExporter()
            exporter.export(export, output)
            logger.info(f"Export saved to {output}")
        except Exception as e:
            logger.error(f"Export failed: {e}")
            raise click.Abort() from None

        # Show summary
        logger.info("Download complete!")
        logger.info(f"Output file: {output}")
        logger.info(f"  Posts: {len(posts)}")
        logger.info(f"  Comments: {len(comments)}")
        logger.info(f"  Usermap: {len(usermap)} users")
        logger.info(f"  Inbox: {len(inbox_messages)} messages")

    except click.Abort:
        raise
    except KeyboardInterrupt:
        logger.warning("Download interrupted by user")
        raise click.Abort() from None
    except YaljeError as e:
        logger.error(f"yalje error: {e}")
        raise click.Abort() from None
    except Exception:
        logger.exception("Unexpected error during download")
        raise click.Abort() from None


if __name__ == "__main__":
    cli()
