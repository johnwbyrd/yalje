# yalje - Yet Another LiveJournal Exporter

A deep, modern Python tool for downloading and archiving all content from LiveJournal accounts, including posts, comments, and inbox messages.

## Features

- **Complete Export**: Download posts, comments, and inbox messages
- **Single File Output**: Everything exports to one file
- **Multiple Formats**: Export to YAML, JSON, or XML
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
# Download everything (default: YAML format)
yalje

# Export to different formats
yalje --format yaml  # Default, creates lj-backup.yaml
yalje --format json  # Creates lj-backup.json
yalje --format xml   # Creates lj-backup.xml

# Short form with custom output filename
yalje -f json -o my-backup.json
yalje -f xml -o archive.xml

# Specify output file (format auto-detected from extension)
yalje --output my-backup.json
yalje -o archive.xml

# Specify date range for posts
yalje --start-year 2020 --start-month 1 --end-year 2023 --end-month 12

# Skip certain content types
yalje --no-posts         # Download only comments and inbox
yalje --no-comments      # Download only posts and inbox
yalje --no-inbox         # Download only posts and comments

# Combine options
yalje --format json --no-inbox --start-year 2020
```

### Using Command-Line Arguments

```bash
# Provide credentials directly (less secure than .env file)
yalje --username your_username --password your_password

# Combine with other options
yalje --username your_username --password your_password --format xml -o backup.xml
```

## Usage as Library

```python
from yalje.core.auth import Authenticator
from yalje.core.config import YaljeConfig
from yalje.api.posts import PostsClient
from yalje.api.comments import CommentsClient
from yalje.api.inbox import InboxClient
from yalje.models.export import LJExport, ExportMetadata
from yalje.exporters.yaml_exporter import YAMLExporter
from yalje.exporters.json_exporter import JSONExporter
from yalje.exporters.xml_exporter import XMLExporter

# Create config
config = YaljeConfig(username="your_username", password="your_password")

# Authenticate
auth = Authenticator(config)
session = auth.login(config.username, config.password)

# Download data
posts_client = PostsClient(session, config)
posts = posts_client.download_all(2020, 1, 2023, 12)

comments_client = CommentsClient(session, config)
comments, usermap = comments_client.download_all()

inbox_client = InboxClient(session, config)
inbox = inbox_client.download_all()

# Create export object
metadata = ExportMetadata(lj_user=config.username, yalje_version="0.1.0")
export = LJExport(
    metadata=metadata,
    usermap=usermap,
    posts=posts,
    comments=comments,
    inbox=inbox
)

# Export to different formats
YAMLExporter().export(export, "lj-backup.yaml")
JSONExporter().export(export, "lj-backup.json")
XMLExporter().export(export, "lj-backup.xml")
```

## Output Format

All data is exported to a **single file** in your chosen format (YAML, JSON, or XML).

### YAML Format (Default)

The YAML export has this structure:

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

### JSON Format

The JSON export contains the same data in JSON format:

```json
{
  "metadata": {
    "export_date": "2024-11-11T12:30:00Z",
    "lj_user": "username",
    "yalje_version": "0.1.0",
    "post_count": 150,
    "comment_count": 1523,
    "inbox_count": 215
  },
  "usermap": [...],
  "posts": [...],
  "comments": [...],
  "inbox": [...]
}
```

### XML Format

The XML export contains the same data in XML format:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<lj_export>
  <metadata>
    <export_date>2024-11-11T12:30:00Z</export_date>
    <lj_user>username</lj_user>
    <yalje_version>0.1.0</yalje_version>
    <post_count>150</post_count>
    <comment_count>1523</comment_count>
    <inbox_count>215</inbox_count>
  </metadata>
  <usermap>...</usermap>
  <posts>...</posts>
  <comments>...</comments>
  <inbox>...</inbox>
</lj_export>
```

All three formats contain identical data with full fidelity. See [docs/schema.md](docs/schema.md) for complete format specification.

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

- Python 3.10+
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
