# Email-to-SMS Worker API Documentation

## Overview

This Cloudflare Worker receives emails via Email Routing and forwards them as SMS messages using Twilio. It's not a traditional HTTP API but an Email Worker that processes incoming emails.

## Email Processing Flow

```
[Send Email] → [Cloudflare Email Routing] → [Worker] → [Twilio] → [SMS Delivered]
```

## Email Input Formats

### Format 1: Phone Number in Email Address

**Most Reliable**

```
To: 15551234567@sms.yourdomain.com
Subject: Optional subject
Body: Your message content here
```

- Phone number in email prefix (before @)
- Supports 10-digit US numbers
- Automatically adds +1 country code

### Format 2: Phone Number in Subject

```
To: contact@sms.yourdomain.com
Subject: To: 555-123-4567
Body: Your message content here
```

- Phone number in subject with "To:" prefix
- Supports various formats: `555-123-4567`, `555.123.4567`, `5551234567`

### Format 3: Custom Header

```
To: sms@yourdomain.com
X-SMS-To: +15551234567
Subject: Test
Body: Your message content
```

- Phone number in custom `X-SMS-To` header
- Requires E.164 format (+1XXXXXXXXXX)

## Phone Number Formats

### Supported Formats

- **E.164**: `+15551234567` (preferred)
- **US National**: `5551234567` (auto-converted to +1)
- **Formatted**: `555-123-4567`, `(555) 123-4567`

### Extraction Priority

1. `X-SMS-To` header (highest confidence)
2. Email address prefix (high confidence)
3. Subject line (high confidence)
4. Email body first 200 chars (low confidence)

## Content Processing

### SMS Length Limits

- **Standard SMS**: 160 characters (GSM-7 encoding)
- **Unicode SMS**: 70 characters (UCS-2 encoding)
- **Extended SMS**: Up to 1,600 characters (10 segments)

### Content Transformation

1. **HTML to Text**: HTML emails converted to plain text
2. **Signature Removal**: Email signatures stripped
3. **Whitespace Normalization**: Extra spaces/newlines removed
4. **Smart Truncation**: Messages truncated at word/sentence boundaries
5. **Sender Info Added**: "From: [name]" prefix added

### Example Transformation

**Input Email:**
```html
From: John Doe <john@example.com>
Subject: Meeting tomorrow
Body: <p>Don't forget about our meeting tomorrow at 2pm!</p>
      <br><br>
      --<br>
      John Doe<br>
      CEO, Example Corp
```

**Output SMS:**
```
From: John Doe
Re: Meeting tomorrow
Don't forget about our meeting tomorrow at 2pm!
```

## Validation

### Email Validation

- ✅ Valid sender email format
- ✅ Valid recipient email format
- ✅ Non-empty content
- ✅ Content within SMS limits

### Phone Number Validation

- ✅ E.164 format (+[country][number])
- ✅ Length: 11-15 digits
- ✅ US numbers: exactly 12 digits (+1 + 10)
- ❌ Invalid area codes rejected (000, 555, 911)

### Sender Authorization

If `ALLOWED_SENDERS` is configured:

- ✅ Exact match: `john@example.com`
- ✅ Domain match: `*@example.com`
- ❌ Unauthorized senders rejected

## Rate Limiting

### Limits (when KV enabled)

| Scope | Limit | Window |
|-------|-------|--------|
| Per Sender | 10 messages | 1 hour |
| Per Recipient | 20 messages | 1 hour |
| Global | 1000 messages | 24 hours |

### Rate Limit Response

When rate limit exceeded:
- Email rejected with error message
- Rejection reason includes reset time
- Counter resets after time window

## Error Handling

### Email Rejection Reasons

| Error Code | Reason | Action |
|------------|--------|--------|
| `UNAUTHORIZED_SENDER` | Sender not in allowlist | Configure ALLOWED_SENDERS |
| `MISSING_FROM` | No sender address | Check email client |
| `INVALID_FROM` | Invalid sender format | Fix email format |
| `EMPTY_CONTENT` | No email body | Add message content |
| `INVALID_PHONE_FORMAT` | Invalid phone number | Use E.164 format |
| `INVALID_US_PHONE` | Invalid US number | Use 10-digit US format |
| `MESSAGE_TOO_SHORT` | Content < 3 chars | Add more content |
| `MESSAGE_TOO_LONG` | Content > 1600 chars | Shorten message |

### Twilio Errors

| Error | Description | Solution |
|-------|-------------|----------|
| `TWILIO_ERROR_401` | Invalid credentials | Check TWILIO_AUTH_TOKEN |
| `TWILIO_ERROR_21211` | Invalid phone number | Verify phone format |
| `TWILIO_ERROR_21408` | Permission denied | Check Twilio permissions |
| `TWILIO_ERROR_20003` | Auth failed | Verify credentials |

## Response & Logging

### Success Response

Email processing succeeds silently. Check logs for confirmation:

```json
{
  "timestamp": "2025-11-13T03:00:00.000Z",
  "level": "info",
  "message": "Email-to-SMS conversion successful",
  "emailFrom": "sender@example.com",
  "smsTo": "+15551234567",
  "twilioSid": "SM...",
  "processingTime": "234ms"
}
```

### Error Response

Email rejected with error message:

```
Email rejected: Invalid phone number format (+1XXXXXXXXXX)
```

### Log Entry Structure

```typescript
{
  timestamp: string;        // ISO 8601
  emailFrom: string;        // Sender email
  emailTo: string;          // Recipient email
  smsTo: string;           // SMS recipient phone
  smsFrom: string;         // Twilio phone number
  messageLength: number;   // SMS character count
  status: 'success' | 'failed' | 'rejected';
  error?: string;          // Error message if failed
  twilioSid?: string;      // Twilio message ID
  processingTimeMs: number; // Processing time
}
```

## Configuration

### Environment Variables

Set in `wrangler.toml`:

```toml
[vars]
ALLOWED_SENDERS = "user@example.com,*@domain.com"
DEFAULT_COUNTRY_CODE = "1"
```

### Secrets

Set via Wrangler CLI:

```bash
wrangler secret put TWILIO_ACCOUNT_SID
wrangler secret put TWILIO_AUTH_TOKEN
wrangler secret put TWILIO_PHONE_NUMBER
```

## Monitoring

### View Live Logs

```bash
npm run tail
```

### Analytics

Available in Cloudflare Dashboard:
- Request count
- Success/failure rate
- Processing time
- Error distribution

### KV Storage

If enabled, stores:
- Rate limit counters (auto-expire)
- Transaction logs (30-day retention)

## Security

### Best Practices

1. ✅ Configure `ALLOWED_SENDERS` allowlist
2. ✅ Enable rate limiting with KV
3. ✅ Use secrets for credentials
4. ✅ Monitor logs for abuse
5. ✅ Rotate secrets regularly
6. ✅ Review sender patterns

### Spam Protection

Built-in checks:
- Sender validation
- Content spam indicators (logged, not rejected)
- Rate limiting
- Phone number validation

## Examples

### Example 1: Simple SMS

**Email:**
```
To: 15551234567@sms.yourdomain.com
Subject: Hello
Body: This is a test message
```

**SMS:**
```
From: Sender Name
Re: Hello
This is a test message
```

### Example 2: Long Message

**Email:**
```
To: 5551234567@sms.yourdomain.com
Body: [300 character message]
```

**SMS:**
```
From: Sender Name
[Truncated to 160 chars]...
```

### Example 3: HTML Email

**Email:**
```html
<html>
<body>
  <p>Meeting at <b>2pm</b></p>
  <p>See you there!</p>
</body>
</html>
```

**SMS:**
```
From: Sender Name
Meeting at 2pm
See you there!
```

## Limitations

- **Email Size**: Max 25MB (Cloudflare limit)
- **SMS Length**: Max 1,600 chars (10 segments)
- **Attachments**: Ignored (not included in SMS)
- **Rich Formatting**: Converted to plain text
- **Images**: Not supported in SMS

## Troubleshooting

### Phone Not Extracted

1. Check email format matches supported patterns
2. Try Format 1 (phone in email address)
3. Review logs for extraction details
4. Verify phone number format

### SMS Not Delivered

1. Check Twilio account balance
2. Verify phone number is valid
3. Review Twilio logs
4. Check for carrier restrictions

### Rate Limited

1. Wait for rate limit window to reset
2. Check logs for reset time
3. Contact admin to adjust limits
4. Verify sender/recipient identity
