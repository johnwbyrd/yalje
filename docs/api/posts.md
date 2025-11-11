# LiveJournal Posts Export API

## Overview

Posts are exported month-by-month in XML format using the official LiveJournal export endpoint.

## API Endpoint

**URL**: `https://www.livejournal.com/export_do.bml`

**Method**: `POST`

**Authentication**: Requires session cookies (`ljloggedin`, `ljmastersession`)

## Request Format

**Headers**:
```http
Content-Type: application/x-www-form-urlencoded
Cookie: ljloggedin=<value>; ljmastersession=<value>
User-Agent: <any valid user agent>
```

**Parameters**:
```
what=journal
year=<YYYY>          # e.g., "2023"
month=<MM>           # e.g., "01" (must be zero-padded)
format=xml
header=on
encid=2              # UTF-8 encoding
field_itemid=on
field_eventtime=on
field_logtime=on
field_subject=on
field_event=on
field_security=on
field_allowmask=on
field_currents=on
```

## Response Format

**Content-Type**: `application/xml`

**XML Structure**:
```xml
<?xml version="1.0"?>
<livejournal>
  <entry>
    <itemid>12345</itemid>
    <eventtime>2023-01-15 14:30:00</eventtime>
    <logtime>2023-01-15 14:30:00</logtime>
    <subject>Post Title</subject>
    <event><![CDATA[Post body content with HTML]]></event>
    <security>public</security>
    <allowmask>0</allowmask>
    <current_mood>happy</current_mood>
    <current_music>Artist - Song</current_music>
  </entry>
  <!-- More entries... -->
</livejournal>
```

## Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `itemid` | Integer | Unique post identifier (used for comment linking) |
| `eventtime` | Datetime | When post was originally published |
| `logtime` | Datetime | When post was logged/saved |
| `subject` | String | Post title (may be empty) |
| `event` | HTML | Post body content (wrapped in CDATA) |
| `security` | String | Access level: `public`, `private`, `friends`, `custom` |
| `allowmask` | Integer | Bitmask for custom friend group access |
| `current_mood` | String | Optional mood metadata |
| `current_music` | String | Optional music metadata |

## Iteration Strategy

To export all posts, iterate through all months from blog start to present:

```python
from datetime import datetime, timedelta

def generate_month_range(start_date, end_date):
    """Generate (year, month) tuples for each month in range."""
    current = start_date
    while current <= end_date:
        yield (current.year, str(current.month).zfill(2))
        # Move to next month
        if current.month == 12:
            current = datetime(current.year + 1, 1, 1)
        else:
            current = datetime(current.year, current.month + 1, 1)

# Example: Download all posts from 2020 to 2023
for year, month in generate_month_range(
    datetime(2020, 1, 1),
    datetime(2023, 12, 31)
):
    download_posts(year, month)
```

## Special Cases

### Empty Months

Months with no posts will return valid XML with no `<entry>` elements:
```xml
<?xml version="1.0"?>
<livejournal>
</livejournal>
```

### Post ID and Comment Linking

The `itemid` is used to link posts with comments:
```python
# Comments reference posts via jitemid
# Conversion formula:
jitemid = itemid >> 8  # Right-shift by 8 bits

# Example:
# Post itemid = 116992
# Comment jitemid = 456 (116992 >> 8)
```

### Character Encoding

- Always use UTF-8 (`encid=2`)
- HTML content is wrapped in CDATA sections
- Properly decode Unicode characters

### Security and Access Levels

| Security Value | Description |
|----------------|-------------|
| `public` | Visible to everyone |
| `private` | Only visible to author |
| `friends` | Visible to friends list |
| `custom` | Custom friend groups (see `allowmask`) |

## Rate Limiting

- No official rate limits documented
- Recommended: Add 1-2 second delay between requests
- Month-by-month iteration naturally throttles requests

## Error Handling

| HTTP Status | Meaning | Action |
|-------------|---------|--------|
| 200 | Success | Parse XML response |
| 401/403 | Authentication failed | Re-authenticate |
| 500 | Server error | Retry with exponential backoff |

## Validation

After downloading, validate:
- [ ] XML is well-formed
- [ ] All expected months downloaded
- [ ] `itemid` values are unique
- [ ] CDATA sections parsed correctly
- [ ] No truncated responses

## See Also

- [Authentication](authentication.md) - Obtaining session cookies
- [Comments API](comments.md) - Linking comments to posts via jitemid
- [Post Schema](../schemas/posts.md) - YAML output format
