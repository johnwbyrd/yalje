# LiveJournal Inbox Scraping

## Overview

Unlike posts and comments, **LiveJournal does not provide an API for inbox messages**. We must scrape the HTML inbox interface.

**⚠️ Important**: This is HTML scraping, not an official API. The structure may change without notice.

## Inbox URL Structure

**Base URL**: `https://www.livejournal.com/inbox/`

**Authentication**: Requires session cookies (`ljloggedin`, `ljmastersession`)

### Query Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `view` | Folder filter | `view=all`, `view=usermsg_recvd` |
| `page` | Page number (1-indexed) | `page=1`, `page=2` |
| `expand` | Expand message by QID | `expand=239` |
| `bookmark_off` | Remove bookmark | `bookmark_off=239` |

### Folder Views

| View Value | Description | Notes |
|------------|-------------|-------|
| `all` | All messages | Default view |
| `usermsg_recvd` | User-to-user messages | Main inbox |
| `ljmsg_recvd` | Official LJ messages | System messages |
| `friendplus` | Friend updates | Activity notifications |
| `birthday` | Birthday notifications | Subset of friendplus |
| `befriended` | New friends | Subset of friendplus |
| `entrycomment` | Entry/comment notifications | |
| `spam` | Suspicious messages | Marked as spam |
| `bookmark` | Bookmarked messages | Flagged items |
| `usermsg_sent` | Sent messages | Outbox |

## HTML Structure

### Pagination Info

Located in table header:
```html
<span class="page-number">
    Page 1 of 15
</span>
```

**Parsing**:
```python
import re
page_text = "Page 1 of 15"
match = re.search(r'Page (\d+) of (\d+)', page_text)
current_page = int(match.group(1))
total_pages = int(match.group(2))
```

### Message Row Structure

Each message is a table row with class `InboxItem_Row`:

```html
<tr class="InboxItem_Row InboxItem_Meta [alt]"
    lj_qid="239"
    id="all_Row_239">

  <td class="checkbox">...</td>

  <td class="item">
    <!-- Controls (bookmark, expand) -->
    <div class="InboxItem_Controls">
      <a href="?page=1&bookmark_off=239">...</a>
      <a href="?page=1&expand=239">...</a>
    </div>

    <!-- Title/Subject (may contain sender info) -->
    <span class="InboxItem_Title [InboxItem_Unread]" id="all_Title_239">
      <!-- Title content -->
    </span>

    <!-- Message body -->
    <div class="InboxItem_Content" style="display: block;">
      <!-- HTML content -->
      <div class='actions'>
        <a href='/inbox/compose.bml?mode=reply&msgid=95534705'>Reply</a>
        <a href='/inbox/markspam.bml?msgid=95534705'>Mark as Spam</a>
      </div>
    </div>
  </td>

  <td class="time">4 months ago</td>
</tr>
```

### Extracting Data Points

#### Queue ID (QID)
```python
# From row attribute
qid = row.get('lj_qid')  # "239"
```

#### Message ID
```python
# From reply action link
# <a href='/inbox/compose.bml?mode=reply&msgid=95534705'>
import re
reply_link = row.find('.//a[contains(@href, "msgid=")]')
if reply_link is not None:
    match = re.search(r'msgid=(\d+)', reply_link.get('href'))
    msgid = match.group(1) if match else None
```

#### Read/Unread Status
```python
title_span = row.find('.//span[@class="InboxItem_Title"]')
is_unread = 'InboxItem_Unread' in title_span.get('class', '')
```

#### Sender Information

User messages contain an `ljuser` span:
```html
<span class="ljuser i-ljuser" data-ljuser="username" lj:user="username">
  <a href="https://username.livejournal.com/profile/">...</a>
  <a href="https://username.livejournal.com/">
    <b>username</b>
  </a>
</span>
```

**Parsing**:
```python
ljuser_span = row.find('.//span[@data-ljuser]')
if ljuser_span is not None:
    username = ljuser_span.get('data-ljuser')
    verified = ljuser_span.find('.//a[@data-badge-type="verified"]') is not None
```

#### Message Body
```python
content_div = row.find('.//div[@class="InboxItem_Content"]')
# Extract HTML content (everything before <div class='actions'>)
body_html = extract_content_before_actions(content_div)
```

#### Timestamp
```python
time_cell = row.find('.//td[@class="time"]')
relative_time = time_cell.text.strip()  # "4 months ago"
```

## Message Types

### Type 1: User Messages
- Has `data-ljuser` attribute
- Has `msgid` in actions
- May have profile picture
- **Example**: Private message from another user

### Type 2: System Notifications
- No `msgid` (or no reply link)
- Predefined format
- **Examples**: Birthdays, friend updates, gifts

### Type 3: Official Messages
- From `data-ljuser="livejournal"`
- Has verified badge
- Has `msgid`
- **Example**: Terms of Service updates

## Scraping Strategy

### Full Inbox Export

```python
def scrape_inbox(session, view='all'):
    """Scrape all pages of a folder view."""
    page = 1
    messages = []

    while True:
        html = fetch_page(session, view, page)
        page_messages, has_next = parse_page(html)

        messages.extend(page_messages)

        if not has_next:
            break

        page += 1
        time.sleep(1)  # Rate limiting

    return messages
```

### Determining Last Page

**Method 1**: Check pagination info
```python
if current_page >= total_pages:
    has_next = False
```

**Method 2**: Check "Next" button state
```python
next_button = html.find('.//input[@id="Page_Next_1"]')
if next_button.get('disabled') is not None:
    has_next = False
```

## Limitations

### No Absolute Timestamps
- Only relative times provided ("4 months ago", "3 years ago")
- Cannot reliably convert to exact dates
- Store as-is in export

### No Threaded Conversations
- Individual messages, no threading
- No conversation IDs

### No Message Content History
- Cannot see edits or deletions
- Only current state visible

### Rate Limiting
- Add delays between page requests (1-2 seconds recommended)
- Watch for HTTP 429 or 503 responses

## Error Handling

| Issue | Cause | Solution |
|-------|-------|---------|
| Missing pagination info | Empty folder | Treat as single page |
| No messages on page | Last page or empty folder | Check total_pages |
| Malformed HTML | LJ site update | Log error, skip message |
| Missing msgid | System notification | Store with msgid=null |

## Validation

After scraping:
- [ ] All pages from 1 to total_pages fetched
- [ ] Message count matches page_count × items_per_page (approximately)
- [ ] QIDs are unique within folder view
- [ ] All user messages have msgid
- [ ] HTML content properly decoded

## Best Practices

1. **Scrape conservatively**: Add delays, respect rate limits
2. **Save incrementally**: Write each page to disk before fetching next
3. **Log responses**: Save raw HTML for debugging
4. **Handle failures gracefully**: Resume from last successful page
5. **Validate structure**: Check expected elements exist before parsing

## See Also

- [Authentication](authentication.md) - Obtaining session cookies
- [Inbox Schema](../schemas/inbox.md) - YAML output format
- [HTML Parser Implementation](../../src/yalje/parsers/html_parser.py)
