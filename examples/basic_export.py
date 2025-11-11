"""Basic example of exporting LiveJournal data."""

from yalje.api.comments import CommentsClient
from yalje.api.posts import PostsClient
from yalje.core.auth import Authenticator
from yalje.core.config import YaljeConfig
from yalje.exporters.yaml_exporter import YAMLExporter
from yalje.models.export import ExportMetadata, LJExport


def main():
    # Create configuration
    config = YaljeConfig(
        username="your_username",
        password="your_password",
    )

    # Authenticate
    auth = Authenticator(config)
    session = auth.login(config.username, config.password)

    # Download posts
    posts_client = PostsClient(session, config)
    posts = posts_client.download_all(2020, 1, 2023, 12)

    # Download comments
    comments_client = CommentsClient(session, config)
    comments, usermap = comments_client.download_all()

    # Create export object
    metadata = ExportMetadata(
        lj_user=config.username,
        yalje_version="0.1.0"
    )
    export = LJExport(
        metadata=metadata,
        posts=posts,
        comments=comments,
        usermap=usermap
    )

    # Export to YAML
    exporter = YAMLExporter()
    exporter.export(export, "lj-backup.yaml")

    print("Export complete! Saved to lj-backup.yaml")
    print(f"  Posts: {len(posts)}")
    print(f"  Comments: {len(comments)}")

if __name__ == "__main__":
    main()
