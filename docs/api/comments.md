# LiveJournal Comments Export API

## Overview

Comments are exported in a two-phase process:
1. Fetch metadata (maxid, usermap)
2. Fetch comment bodies in paginated batches

## Phase 1: Metadata Request

### Endpoint

**URL**: `https://www.livejournal.com/export_comments.bml?get=comment_meta&startid=0`

**Method**: `GET`

**Authentication**: Requires session cookies

### Response

```xml
<?xml version="1.0"?>
<livejournal>
  <maxid>987654</maxid>
  <usermap id="123" user="username1" />
  <usermap id="456" user="username2" />
  <!-- More usermaps... -->
</livejournal>
```

**Fields**:
- `maxid`: Highest comment ID (pagination stopping point)
- `usermap`: Maps numeric user IDs to usernames

## Phase 2: Comment Bodies (Paginated)

### Endpoint

**URL**: `https://www.livejournal.com/export_comments.bml?get=comment_body&startid=<id>`

**Method**: `GET`

**Authentication**: Requires session cookies

### Pagination

```python
# Start from ID 0
startid = 0
maxid = 987654  # From metadata

while startid < maxid:
    # Request batch starting after startid
    response = fetch_comments(startid)
    comments = parse_comments(response)

    # Track highest ID in batch
    if comments:
        startid = max(c['id'] for c in comments)
    else:
        break  # No more comments
```

### Response Format

```xml
<?xml version="1.0"?>
<livejournal>
  <comment id="100" jitemid="456" posterid="123" parentid="99">
    <date>2023-01-15 15:45:00</date>
    <subject>Re: Post Title</subject>
    <body><![CDATA[Comment text with HTML]]></body>
  </comment>

  <comment id="101" jitemid="456" posterid="456" state="D">
    <date>2023-01-15 16:00:00</date>
    <subject></subject>
    <body></body>
  </comment>

  <comment id="102" jitemid="789">
    <date>2023-01-16 10:00:00</date>
    <subject>Anonymous comment</subject>
    <body><![CDATA[Posted anonymously]]></body>
  </comment>
</livejournal>
```

## Field Descriptions

### Comment Attributes (XML tag attributes)

| Attribute | Required | Description |
|-----------|----------|-------------|
| `id` | Yes | Unique comment identifier |
| `jitemid` | Yes | Post ID this comment belongs to |
| `posterid` | No | User ID of author (see usermap) |
| `parentid` | No | Parent comment ID (for threading) |
| `state` | No | `D` = deleted, absent = active |

### Comment Elements (XML child tags)

| Element | Required | Description |
|---------|----------|-------------|
| `date` | Yes | Timestamp (YYYY-MM-DD HH:MM:SS) |
| `subject` | No | Comment subject/title |
| `body` | No | Comment content (HTML in CDATA) |

## Linking to Posts

Comments reference posts via the `jitemid` field. Each comment's `jitemid` should match a post's `jitemid` field. The exact relationship between post `itemid` and `jitemid` is not documented in the official LiveJournal API and will need to be determined through empirical testing with actual LiveJournal data.

## Comment Threading

Build a tree structure using `parentid`:

```python
def build_thread(comments):
    """Organize comments into threaded tree."""
    # Index by ID
    by_id = {c['id']: c for c in comments}

    # Initialize children arrays
    for comment in comments:
        comment['children'] = []

    # Build tree
    root_comments = []
    for comment in comments:
        if 'parentid' in comment:
            parent = by_id[comment['parentid']]
            parent['children'].append(comment)
        else:
            root_comments.append(comment)  # Top-level

    return root_comments
```

## Special Cases

### Anonymous Comments

Missing `posterid` attribute indicates anonymous comment:
```xml
<comment id="102" jitemid="789">
  <!-- No posterid -->
  <body>Posted anonymously</body>
</comment>
```

### Deleted Comments

Marked with `state="D"`:
```xml
<comment id="101" state="D">
  <body></body>  <!-- Usually empty -->
</comment>
```

Keep deleted comments to preserve thread structure.

### Missing Authors

If `posterid` exists but not in usermap:
- May be a deleted account
- Store ID, attempt username lookup later

## Validation

After downloading, validate:
- [ ] Final `startid` >= `maxid`
- [ ] All `posterid` values exist in usermap (or are absent)
- [ ] All `parentid` references exist in comment set
- [ ] All `jitemid` values match at least one post
- [ ] No circular threading (parent-child loops)

## Performance Tips

- Batch size is controlled by LiveJournal (~1000-10000 per batch)
- Add small delays between batch requests
- Save batches incrementally to enable resume
- Build usermap index for fast lookups

## See Also

- [Posts API](posts.md) - Post itemid to comment jitemid linking
- [Comment Schema](../schemas/comments.md) - YAML output format
- [Original API Docs](ORIGINAL_API_DOCS.md) - Complete technical details
