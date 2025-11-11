# LiveJournal Authentication API

## Overview

LiveJournal uses a cookie-based authentication system with a three-step process:
1. Acquire initial cookie (`luid`)
2. Submit login credentials
3. Receive session cookies (`ljloggedin`, `ljmastersession`)

## Authentication Flow

### Step 1: Acquire Initial Cookie (luid)

**Purpose**: LiveJournal requires a pre-login cookie before accepting form submissions.

**Request**:
```http
GET https://www.livejournal.com/
```

**Headers**:
```
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
```

**Response**:
- Extract `luid` cookie from `Set-Cookie` header
- Format: `luid=<value>; Domain=.livejournal.com; Path=/`

### Step 2: Login and Acquire Session Cookies

**Purpose**: Authenticate with username/password to get session cookies.

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
- Extract session cookies:
  - `ljloggedin` - Session authentication token
  - `ljmastersession` - Master session identifier

**Cookie Format**:
```
Set-Cookie: ljloggedin=<value>; Domain=.livejournal.com; Path=/
Set-Cookie: ljmastersession=<value>; Domain=.livejournal.com; Path=/
```

## Session Management

### Cookie Persistence

Session cookies should be:
- Stored securely (not in plain text)
- Reused across requests
- Refreshed when expired

### Session Expiration

- Session cookies may expire during long-running operations
- Monitor for HTTP 401/403 responses
- Re-authenticate if session expires

## Security Considerations

- **Never log passwords or cookies**
- Store credentials securely (use keyring/keychain when possible)
- Use HTTPS for all requests
- Clear session data on logout

## Implementation Notes

**Parsing Cookie Values**:
```python
# Extract cookie value from Set-Cookie header
# Example: "ljloggedin=u:username:...; Domain=..."
cookie_header = response.headers['Set-Cookie']
cookie_value = cookie_header.split('ljloggedin=')[1].split(';')[0]
```

**Session Validation**:
- Test session by making an authenticated request
- Check for successful response (not redirect to login)

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| No `luid` cookie | Initial request failed | Retry GET request |
| Login returns 200 but no session cookies | Invalid credentials | Verify username/password |
| 401/403 on API requests | Session expired | Re-authenticate |
| Rate limiting | Too many requests | Add delays between requests |

## See Also

- [Posts API](posts.md) - Using session cookies to download posts
- [Comments API](comments.md) - Using session cookies to download comments
- [Inbox Scraping](inbox.md) - Using session cookies to scrape inbox
