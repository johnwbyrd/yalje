# LiveJournal Export API Documentation

This document describes the complete extraction process for downloading posts and comments from LiveJournal. This is sufficient to reimplement the export functionality from scratch.

---

## Authentication Process

### Step 1: Acquire Initial Cookie (luid)

**Purpose**: LiveJournal requires a pre-login cookie before accepting form submissions.

**Request**:
```http
GET https://www.livejournal.com/
```

**Headers**:
```
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36
Upgrade-Insecure-Requests: 1
sec-ch-ua: "Chromium";v="127"
sec-ch-ua-platform: "Windows"
```

**Response**:
- Extract `luid` cookie from `Set-Cookie` header
- Format: `luid=<value>; Domain=.livejournal.com; Path=/`

---

### Step 2: Login and Acquire Session Cookies

**Purpose**: Authenticate with username/password to get session cookies for authenticated API requests.

**Request**:
```http
POST https://www.livejournal.com/login.bml
Content-Type: application/x-www-form-urlencoded
Cookie: luid=<value_from_step_1>
```

**Request Body**:
```
user=<username>
password=<password>
```

**Response**:
- Status code 200 indicates success
- Extract two cookies from `Set-Cookie` header:
  1. **ljloggedin** - Session authentication token
  2. **ljmastersession** - Master session identifier

**Cookie Format**:
```
Set-Cookie: ljloggedin=<value>; Domain=.livejournal.com; Path=/; ...
Set-Cookie: ljmastersession=<value>; Domain=.livejournal.com; Path=/; ...
```

**Parsing Logic**:
Split the header value on `<cookiename>=`, take the second part, then split on `;` and take the first part.

---

## Posts Extraction API

### Endpoint: Export Posts by Month

**Purpose**: Download all blog posts for a specific month in XML format.

**Request**:
```http
POST https://www.livejournal.com/export_do.bml
Content-Type: application/x-www-form-urlencoded
Cookie: ljloggedin=<value>; ljmastersession=<value>
User-Agent: <any valid user agent>
```

**Required Cookies**: `ljloggedin`, `ljmastersession`

**Request Parameters**:
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

**Response**: XML document containing all posts for that month

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

**XML Fields Explained**:
- **itemid**: Unique post identifier (used for linking to comments)
- **eventtime**: When the post was originally published
- **logtime**: When the post was logged/saved
- **subject**: Post title (may be empty)
- **event**: Post body content (HTML, wrapped in CDATA)
- **security**: Access level (public, private, friends, custom)
- **allowmask**: Bitmask for custom friend group access
- **current_mood**: Optional mood metadata
- **current_music**: Optional music metadata

**Iteration Strategy**:
To export an entire blog, iterate through all months from the blog's start date to the present:
1. Start with the earliest month (or user-specified start)
2. Increment by one month each iteration
3. Continue until reaching the end month (or current month)

---

## Comments Extraction API

Comments are exported in a two-step process: metadata first, then comment bodies in batches.

### Step 1: Fetch Comment Metadata

**Purpose**: Get the maximum comment ID and user mappings.

**Request**:
```http
GET https://www.livejournal.com/export_comments.bml?get=comment_meta&startid=0
Cookie: ljloggedin=<value>; ljmastersession=<value>
User-Agent: <any valid user agent>
```

**Required Cookies**: `ljloggedin`, `ljmastersession`

**Query Parameters**:
```
get=comment_meta
startid=0
```

**Response**: XML with metadata

**XML Structure**:
```xml
<?xml version="1.0"?>
<livejournal>
  <maxid>987654</maxid>
  <usermap id="123" user="username1" />
  <usermap id="456" user="username2" />
  <usermap id="789" user="username3" />
  <!-- More usermaps... -->
</livejournal>
```

**Fields Explained**:
- **maxid**: Highest comment ID in the system (use this as the stopping point)
- **usermap**: Maps numeric user IDs to usernames
  - `id` attribute: Numeric user identifier
  - `user` attribute: Username string

**User Map Purpose**:
Comment bodies reference users by numeric ID. The usermap translates these to usernames.

---

### Step 2: Fetch Comment Bodies (Paginated)

**Purpose**: Download comment content in batches, paginated by comment ID.

**Request**:
```http
GET https://www.livejournal.com/export_comments.bml?get=comment_body&startid=<id>
Cookie: ljloggedin=<value>; ljmastersession=<value>
User-Agent: <any valid user agent>
```

**Required Cookies**: `ljloggedin`, `ljmastersession`

**Query Parameters**:
```
get=comment_body
startid=<N>         # Start from comment ID N+1
```

**Pagination Logic**:
1. Start with `startid=0` (fetches from ID 1)
2. Each response contains a batch of comments
3. Track the highest comment ID in the batch
4. Next request uses `startid=<highest_id>`
5. Continue until `startid >= maxid` (from metadata)

**Response**: XML with comment data

**XML Structure**:
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

  <!-- More comments... -->
</livejournal>
```

**Comment Attributes** (in XML tag):
- **id** (required): Unique comment identifier
- **jitemid** (required): Post ID this comment belongs to (see linking section below)
- **posterid** (optional): User ID of comment author (lookup in usermap)
- **parentid** (optional): Parent comment ID (for threading)
- **state** (optional): Comment state
  - `D` = Deleted
  - Absence = Active comment

**Comment Elements** (child tags):
- **date** (optional): When comment was posted (format: `YYYY-MM-DD HH:MM:SS`)
- **subject** (optional): Comment subject/title
- **body** (optional): Comment content (HTML, wrapped in CDATA)

**Missing Author**:
If `posterid` is absent, the comment was posted anonymously.

**Deleted Comments**:
Comments with `state="D"` are deleted. They have minimal data (usually just structure for threading).

---

## Linking Posts and Comments

### Post ID to jitemid Conversion

Comments reference posts via `jitemid`, but posts have `itemid`. The relationship:

```
jitemid = itemid >> 8
```

**Explanation**: Right-shift the post's `itemid` by 8 bits to get the `jitemid` used in comments.

**Example**:
- Post has `itemid="116992"`
- Bit shift: `116992 >> 8 = 456`
- Comments with `jitemid="456"` belong to this post

**Reverse Calculation** (not typically needed):
```
itemid = jitemid << 8
```
This gives the base ID; the actual itemid may have additional lower bits set.

---

## Comment Threading Structure

Comments form a tree structure using parent-child relationships.

### Building the Comment Tree

**Data Structure**:
Each comment should have:
```json
{
  "id": 100,
  "jitemid": 456,
  "parentid": 99,        // Optional - only if replying to another comment
  "posterid": 123,       // Optional - only if not anonymous
  "author": "username",  // Looked up from usermap
  "date": "2023-01-15 15:45:00",
  "subject": "Re: Topic",
  "body": "<p>Comment text</p>",
  "children": []         // Array of child comments
}
```

**Tree Construction Algorithm**:
1. Create a dictionary mapping comment ID to comment object
2. Add empty `children` array to each comment
3. Iterate through all comments:
   - If `parentid` exists: append comment to `parent.children`
   - If no `parentid`: comment is top-level (direct reply to post)
4. Top-level comments form the root array for that post

**Pseudo-code**:
```python
comments_dict = {comment.id: comment for comment in all_comments}

for comment in all_comments:
    comment['children'] = []

root_comments = []
for comment in all_comments:
    if 'parentid' in comment:
        parent = comments_dict[comment['parentid']]
        parent['children'].append(comment)
    else:
        root_comments.append(comment)
```

---

## Complete Extraction Workflow

### Full Export Process

1. **Authenticate**:
   - GET `livejournal.com` → extract `luid` cookie
   - POST `login.bml` with credentials + `luid` → extract `ljloggedin` and `ljmastersession`

2. **Download Posts**:
   - For each month in date range:
     - POST `export_do.bml` with month/year parameters
     - Parse XML to extract post entries
     - Store posts indexed by `itemid`

3. **Download Comments**:
   - GET `export_comments.bml?get=comment_meta&startid=0`
   - Parse `maxid` and build usermap
   - Loop while `current_id < maxid`:
     - GET `export_comments.bml?get=comment_body&startid={current_id}`
     - Parse comments batch
     - Update `current_id` to highest ID in batch
   - Map `posterid` to usernames using usermap

4. **Link Data**:
   - Group comments by `jitemid`
   - For each post:
     - Calculate `jitemid = itemid >> 8`
     - Find all comments with matching `jitemid`
     - Build comment tree using `parentid` relationships

---

## Special Cases and Edge Cases

### Empty or Missing Fields

- **Empty subject**: Use post date or ID as fallback
- **Missing posterid**: Comment is anonymous (no author)
- **Missing parentid**: Comment is top-level (direct reply to post)
- **Missing body**: Deleted or screened comment

### Deleted Comments

- Marked with `state="D"` attribute
- Usually have empty or minimal content
- Keep in structure to preserve threading (child comments may reference them)

### Character Encoding

- Always use UTF-8 encoding (`encid=2` parameter)
- XML responses use CDATA sections for HTML content
- Properly decode Unicode characters

### Rate Limiting

- No official rate limits documented
- Recommended: Add small delay between requests (e.g., 1 second)
- Month-by-month iteration naturally throttles post downloads
- Comment pagination is controlled by LiveJournal's batch size

### Authentication Expiration

- Session cookies may expire during long exports
- Monitor for HTTP 401/403 responses
- Re-authenticate if needed

---

## API Quirks and Notes

1. **Month Parameter Must Be Zero-Padded**: Use `"01"` not `"1"`
2. **Post IDs Are Not Sequential**: Don't assume continuous ranges
3. **Comment Batches Vary in Size**: LiveJournal controls batch size, not the client
4. **jitemid Bit Shift Is Mandatory**: Must use `itemid >> 8` for correct linking
5. **CDATA Sections**: Post and comment bodies are wrapped in CDATA, strip when parsing
6. **HTML Content**: Both posts and comments contain raw HTML, not plain text
7. **Metadata Is Optional**: `current_mood`, `current_music`, `subject` may be absent

---

## Data Validation

### Verify Extraction Completeness

**Posts**:
- Check if any months returned empty results unexpectedly
- Verify `itemid` values are unique
- Confirm HTML content parsed correctly from CDATA

**Comments**:
- Verify final `startid` reached or exceeded `maxid`
- Check all `posterid` values exist in usermap (or are absent for anonymous)
- Validate `parentid` references exist in comment set
- Ensure `jitemid` values match at least one post

**Threading**:
- Verify no circular references in parent-child relationships
- Check deleted comments still maintain structure
- Confirm top-level comments have no `parentid`

---

## Example HTTP Session

```http
# 1. Get initial cookie
GET / HTTP/1.1
Host: www.livejournal.com
User-Agent: Mozilla/5.0 ...

# Response includes: Set-Cookie: luid=u12345:67890

# 2. Login
POST /login.bml HTTP/1.1
Host: www.livejournal.com
Cookie: luid=u12345:67890
Content-Type: application/x-www-form-urlencoded

user=myusername&password=mypassword

# Response includes:
# Set-Cookie: ljloggedin=u:myusername:...
# Set-Cookie: ljmastersession=v1:u12345:...

# 3. Export posts for January 2023
POST /export_do.bml HTTP/1.1
Host: www.livejournal.com
Cookie: ljloggedin=u:myusername:...; ljmastersession=v1:u12345:...
Content-Type: application/x-www-form-urlencoded

what=journal&year=2023&month=01&format=xml&header=on&encid=2&field_itemid=on&field_eventtime=on&field_logtime=on&field_subject=on&field_event=on&field_security=on&field_allowmask=on&field_currents=on

# 4. Get comment metadata
GET /export_comments.bml?get=comment_meta&startid=0 HTTP/1.1
Host: www.livejournal.com
Cookie: ljloggedin=u:myusername:...; ljmastersession=v1:u12345:...

# 5. Get first batch of comments
GET /export_comments.bml?get=comment_body&startid=0 HTTP/1.1
Host: www.livejournal.com
Cookie: ljloggedin=u:myusername:...; ljmastersession=v1:u12345:...

# 6. Get next batch (continuing from highest ID in previous batch)
GET /export_comments.bml?get=comment_body&startid=5432 HTTP/1.1
Host: www.livejournal.com
Cookie: ljloggedin=u:myusername:...; ljmastersession=v1:u12345:...

# ... repeat until startid >= maxid
```

---

## Summary

This API documentation provides everything needed to extract LiveJournal content:

1. **Authentication**: Three-step cookie-based authentication
2. **Posts API**: Month-by-month XML export with field selection
3. **Comments API**: Two-phase process (metadata + paginated bodies)
4. **Data Linking**: Bit-shift formula for matching posts to comments
5. **Threading**: Parent-child relationship building algorithm

The extraction process is completely stateless once authenticated, allowing for resumable downloads and parallel processing of different time periods.
