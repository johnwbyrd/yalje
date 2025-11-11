# LiveJournal Export Data Schema

## Overview

The entire LiveJournal export is contained in **one YAML file** with the following top-level sections:
- `metadata` - Export information
- `usermap` - User ID to username mappings
- `posts` - All blog posts
- `comments` - All comments
- `inbox` - All inbox messages

## File: `lj-backup.yaml`

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
  - userid: 456
    username: "friend2"

posts:
  - itemid: 116992
    jitemid: 456
    eventtime: "2023-01-15 14:30:00"
    logtime: "2023-01-15 14:30:00"
    subject: "Post Title"
    event: "<p>Post body with <b>HTML</b></p>"
    security: "public"
    allowmask: 0
    current_mood: "happy"
    current_music: "Artist - Song"

comments:
  - id: 100
    jitemid: 456
    posterid: 123
    poster_username: "friend1"
    parentid: null
    date: "2023-01-15 15:45:00"
    subject: "Re: Post Title"
    body: "<p>Comment text</p>"
    state: null

inbox:
  - qid: 239
    msgid: 95534705
    type: "user_message"
    sender:
      username: "livejournal"
      display_name: "LiveJournal"
      profile_url: "https://livejournal.livejournal.com/"
      userpic_url: "https://l-userpic.livejournal.com/129443917/21331"
      verified: true
    title: "LiveJournal User Agreement updated"
    body: "Hello!<br /><br />We have updated..."
    timestamp_relative: "4 months ago"
    timestamp_absolute: null
    read: false
    bookmarked: false
```

## Metadata Section

| Field | Type | Description |
|-------|------|-------------|
| `export_date` | ISO 8601 datetime | When export was performed |
| `lj_user` | string | LiveJournal username |
| `yalje_version` | string | Version of yalje used |
| `post_count` | integer | Total number of posts |
| `comment_count` | integer | Total number of comments |
| `inbox_count` | integer | Total number of inbox messages |

## Usermap Section

Array of user ID to username mappings from comments metadata.

| Field | Type | Description |
|-------|------|-------------|
| `userid` | integer | Numeric user ID |
| `username` | string | LiveJournal username |

## Posts Section

Array of all blog posts.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `itemid` | integer | Yes | Unique post identifier |
| `jitemid` | integer | Yes | Calculated: `itemid >> 8` |
| `eventtime` | string | Yes | Publication datetime |
| `logtime` | string | Yes | Log/save datetime |
| `subject` | string or null | Yes | Post title |
| `event` | string | Yes | Post body (HTML) |
| `security` | string | Yes | `public`, `private`, `friends`, `custom` |
| `allowmask` | integer | Yes | Friend group bitmask |
| `current_mood` | string or null | Yes | Mood metadata |
| `current_music` | string or null | Yes | Music metadata |

## Comments Section

Array of all comments.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | integer | Yes | Unique comment ID |
| `jitemid` | integer | Yes | Post identifier (links to post) |
| `posterid` | integer or null | Yes | User ID (null = anonymous) |
| `poster_username` | string or null | Yes | Resolved from usermap |
| `parentid` | integer or null | Yes | Parent comment ID (null = top-level) |
| `date` | string | Yes | Comment timestamp |
| `subject` | string or null | Yes | Comment subject |
| `body` | string or null | Yes | Comment content (HTML) |
| `state` | string or null | Yes | `deleted` or null |

## Inbox Section

Array of all inbox messages.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `qid` | integer | Yes | Queue ID |
| `msgid` | integer or null | Yes | Message ID (null for notifications) |
| `type` | string | Yes | `user_message`, `system_notification`, `official_message` |
| `sender` | object or null | Yes | Sender information (null for system) |
| `title` | string | Yes | Message title/subject |
| `body` | string | Yes | Message content (HTML) |
| `timestamp_relative` | string | Yes | "4 months ago" |
| `timestamp_absolute` | datetime or null | Yes | Exact timestamp (if available) |
| `read` | boolean | Yes | Read status |
| `bookmarked` | boolean | Yes | Bookmark status |

### Sender Object

| Field | Type | Description |
|-------|------|-------------|
| `username` | string | LJ username |
| `display_name` | string | Display name |
| `profile_url` | string | Profile URL |
| `userpic_url` | string or null | User picture URL |
| `verified` | boolean | Verified badge status |

## Data Relationships

### Posts ↔ Comments

```yaml
# Post
posts:
  - itemid: 116992
    jitemid: 456  # itemid >> 8

# Comments for this post
comments:
  - id: 100
    jitemid: 456  # Links to post
```

### Comment Threading

```yaml
comments:
  - id: 100
    parentid: null  # Top-level

  - id: 101
    parentid: 100  # Reply to 100

  - id: 102
    parentid: 101  # Reply to 101
```

## Implementation Notes

This schema is generated from Pydantic models:

```python
from yalje.models.export import LJExport

# Create export object
export = LJExport(
    metadata=ExportMetadata(...),
    usermap=[...],
    posts=[...],
    comments=[...],
    inbox=[...]
)

# Serialize to YAML
import yaml
yaml_str = yaml.dump(export.model_dump(), allow_unicode=True)
```

## See Also

- [Posts API](api/posts.md)
- [Comments API](api/comments.md)
- [Inbox Scraping](api/inbox.md)
- [Export Model](../src/yalje/models/export.py)
