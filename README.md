# yalje - Yet Another LiveJournal Exporter

A deep, modern Python tool for downloading and archiving all content from LiveJournal accounts, including posts, comments, and inbox messages.

## Features

- **Complete Export**: Download posts, comments, and inbox messages
- **Single File Output**: Everything exports to one YAML file
- **Multiple Formats**: Export to YAML or JSON
- **Well-Structured**: Clear schema with Pydantic validation
- **Library + CLI**: Use as a command-line tool or Python library
- **Extensible**: Clean architecture for building custom importers

## Installation

```bash
# From source
git clone https://github.com/yourusername/yalje.git
cd yalje
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

## Quick Start

### Using .env File (Recommended)

Create a `.env` file with your credentials:

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your credentials
# YALJE_USERNAME=your_username
# YALJE_PASSWORD=your_password
```

Then run yalje (it will automatically load from `.env`):

```bash
# Download everything to a single YAML file
yalje download --output lj-backup.yaml

# Or specify date range for posts
yalje download \
    --start-year 2020 --start-month 1 \
    --end-year 2023 --end-month 12 \
    --output lj-backup.yaml

# Skip certain content types
yalje download --no-inbox --output lj-backup.yaml
```

### Using Command-Line Arguments

```bash
# Provide credentials directly (less secure)
yalje download --username your_username --password your_password --output lj-backup.yaml
```

## Usage as Library

```python
from yalje.core.auth import Authenticator
from yalje.core.config import YaljeConfig
from yalje.api.posts import PostsClient
from yalje.api.comments import CommentsClient
from yalje.models.export import LJExport, ExportMetadata
from yalje.exporters.yaml_exporter import YAMLExporter

# Create config
config = YaljeConfig(username="your_username", password="your_password")

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
metadata = ExportMetadata(lj_user=config.username, yalje_version="0.1.0")
export = LJExport(
    metadata=metadata,
    usermap=usermap,
    posts=posts,
    comments=comments,
    inbox=[]
)

# Export to YAML (single file)
exporter = YAMLExporter()
exporter.export(export, "lj-backup.yaml")
```

## Output Format

All data is exported to a **single YAML file** with this structure:

```yaml
metadata:
  export_date: "2024-11-11T12:30:00Z"
  lj_user: "username"
  yalje_version: "0.1.0"
  post_count: 150
  comment_count: 1523
  inbox_count: 215

usermap:
  - userid: 123
    username: "friend1"

posts:
  - itemid: 116992
    jitemid: 456
    subject: "Post Title"
    event: "<p>Post content</p>"
    # ... more fields

comments:
  - id: 100
    jitemid: 456
    body: "<p>Comment text</p>"
    # ... more fields

inbox:
  - qid: 239
    msgid: 95534705
    title: "Message subject"
    # ... more fields
```

See [docs/schema.md](docs/schema.md) for complete format specification.

## Documentation

- [Architecture](docs/architecture.md) - System design and module relationships
- [Data Schema](docs/schema.md) - YAML export format specification
- [API Documentation](docs/api/) - LiveJournal API details
  - [Authentication](docs/api/authentication.md)
  - [Posts](docs/api/posts.md)
  - [Comments](docs/api/comments.md)
  - [Inbox](docs/api/inbox.md)
- [Contributing](docs/contributing.md) - How to contribute
- [Project Structure](STRUCTURE.md) - Complete file layout

## Requirements

- Python 3.9+
- Active LiveJournal account

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all quality checks (recommended)
tox -e dev

# Run full test suite across all Python versions
tox

# Run specific checks
tox -e lint          # Linting only
tox -e typecheck     # Type checking only
tox -e format        # Auto-format code

# Run tests directly (without tox)
pytest

# See DEVELOPMENT.md for complete guide
```

See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed development workflow, pre-commit hooks, and CI setup.

## Project Status

**Alpha** - Core functionality is being implemented. API may change.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

This project builds upon the work of previous LiveJournal exporters and the community's efforts to preserve blog content.

## See Also

- [LiveJournal Export Documentation](https://www.livejournal.com/export.bml)
- Other LJ export tools: ljdump, ljarchive, etc.
