# Cloudflare Worker Architecture - Email-to-SMS System

## Overview

This document outlines the improved architecture for a Cloudflare Worker that receives emails via Cloudflare Email Routing and forwards them as SMS messages using Twilio.

## System Architecture

```
[Incoming Email]
    ↓
[Cloudflare Email Routing]
    ↓
[Email Worker Handler] → [Email Parser]
    ↓                         ↓
[Validation Layer]    [Extract Phone & Content]
    ↓
[Rate Limiter] (optional)
    ↓
[Twilio SMS Sender]
    ↓
[Response Logger] → [KV Storage] (optional)
```

## Core Components

### 1. Email Handler (`src/handlers/email-handler.ts`)

**Responsibilities:**
- Receive incoming email from Cloudflare Email Routing
- Parse email headers and body
- Extract recipient phone number and message content
- Handle errors gracefully

**Key Features:**
- Email format validation
- MIME parsing for text/html content
- Attachment handling (optional)
- Error recovery

**Interface:**
```typescript
interface EmailMessage {
  from: string;
  to: string;
  subject: string;
  body: string;
  headers: Map<string, string>;
  timestamp: Date;
}
```

### 2. Phone Number Parser (`src/utils/phone-parser.ts`)

**Responsibilities:**
- Extract phone numbers from email addresses or subject lines
- Validate phone number formats
- Normalize to E.164 format (+1XXXXXXXXXX)

**Parsing Strategies:**
1. Email prefix: `15551234567@yourdomain.com` → `+15551234567`
2. Subject line: `Subject: To: 555-123-4567` → `+15551234567`
3. Custom header: `X-SMS-To: +15551234567`

**Validation:**
- E.164 format validation
- Country code verification
- Length validation (10-15 digits)

### 3. Content Processor (`src/utils/content-processor.ts`)

**Responsibilities:**
- Extract message content from email body
- Strip HTML tags (if needed)
- Truncate to SMS length limits (160 chars standard, 1600 chars extended)
- Handle special characters and encoding

**Features:**
- HTML-to-text conversion
- Smart truncation with ellipsis
- Character encoding normalization (UTF-8)
- URL shortening (optional)

### 4. Twilio Integration (`src/services/twilio-service.ts`)

**Responsibilities:**
- Send SMS via Twilio API
- Handle API responses and errors
- Retry logic for failed sends

**Configuration:**
```typescript
interface TwilioConfig {
  accountSid: string;      // From secrets
  authToken: string;       // From secrets
  fromNumber: string;      // Your Twilio phone number
  maxRetries: number;      // Default: 3
  timeout: number;         // Default: 5000ms
}
```

**Error Handling:**
- Invalid phone number
- Insufficient balance
- Network failures
- Rate limiting

### 5. Validation Layer (`src/middleware/validator.ts`)

**Responsibilities:**
- Validate incoming email structure
- Check sender whitelist (optional)
- Verify required fields
- Sanitize inputs

**Validation Rules:**
- Email must contain valid recipient info
- Message content must not be empty
- Phone number must be valid E.164 format
- Message length within limits

### 6. Rate Limiter (`src/middleware/rate-limiter.ts`) [Optional]

**Responsibilities:**
- Prevent abuse and spam
- Track requests per sender
- Implement cooldown periods

**Implementation Options:**
- KV-based counter with TTL
- Durable Objects for precise rate limiting
- Simple in-memory tracking (for light use)

**Limits:**
- Per sender: 10 messages/hour
- Per recipient: 20 messages/hour
- Global: 1000 messages/day

### 7. Logger (`src/utils/logger.ts`)

**Responsibilities:**
- Log all email-to-SMS transactions
- Track errors and failures
- Store metrics for monitoring

**Storage Options:**
- Workers Analytics Engine (recommended)
- KV Namespace (for persistence)
- Console logs (development)

**Log Structure:**
```typescript
interface LogEntry {
  timestamp: string;
  emailFrom: string;
  smsTo: string;
  messageLength: number;
  status: 'success' | 'failed';
  error?: string;
  twilioSid?: string;
}
```

## File Structure

```
src/
├── index.ts                    # Main entry point
├── handlers/
│   └── email-handler.ts       # Email routing handler
├── services/
│   └── twilio-service.ts      # Twilio API integration
├── utils/
│   ├── phone-parser.ts        # Phone number parsing
│   ├── content-processor.ts   # Content extraction
│   └── logger.ts              # Logging utility
├── middleware/
│   ├── validator.ts           # Input validation
│   └── rate-limiter.ts        # Rate limiting
└── types/
    └── index.ts               # TypeScript type definitions
```

## Configuration

### Environment Variables (Secrets)

```bash
TWILIO_ACCOUNT_SID     # Twilio Account SID
TWILIO_AUTH_TOKEN      # Twilio Auth Token
TWILIO_PHONE_NUMBER    # Your Twilio phone number (E.164 format)
```

### wrangler.toml Configuration

```toml
name = "email-to-sms-worker"
main = "src/index.ts"
compatibility_date = "2024-10-22"
compatibility_flags = ["nodejs_compat"]

# Email routing configuration
[email]
name = "email-to-sms"
# Route all emails to this worker
# Example: *@sms.yourdomain.com

# Optional: KV for rate limiting and logging
[[kv_namespaces]]
binding = "EMAIL_SMS_KV"
id = "your-kv-namespace-id"

# Optional: Analytics Engine for metrics
[[analytics_engine_datasets]]
binding = "EMAIL_SMS_ANALYTICS"

# Observability
[observability]
enabled = true
```

## Email Routing Setup

### Cloudflare Dashboard Configuration

1. **Enable Email Routing** for your domain
2. **Create Email Route**:
   - Match: `*@sms.yourdomain.com` (or specific pattern)
   - Action: Send to Worker
   - Worker: `email-to-sms-worker`

3. **DNS Configuration** (automatic):
   - MX records will be configured by Cloudflare
   - SPF records for email validation

### Email Address Format Options

**Option 1: Phone in Email Prefix**
```
15551234567@sms.yourdomain.com
```

**Option 2: Phone in Subject**
```
To: contact@sms.yourdomain.com
Subject: To: 555-123-4567
```

**Option 3: Custom Header**
```
To: sms@yourdomain.com
X-SMS-To: +15551234567
```

## Message Flow

1. **Email Received** → Cloudflare Email Routing
2. **Worker Triggered** → Email handler invoked
3. **Parse Email** → Extract headers, body, attachments
4. **Extract Phone** → Parse recipient from email/subject
5. **Validate Input** → Check format, whitelist, limits
6. **Check Rate Limit** → Prevent abuse (optional)
7. **Process Content** → Extract text, truncate if needed
8. **Send SMS** → Call Twilio API
9. **Log Result** → Store transaction record
10. **Return Response** → Success/failure to email sender

## Error Handling

### Email Processing Errors
- Invalid email format → Reject with error message
- Missing recipient info → Return error email
- Content extraction failure → Log and notify

### Twilio API Errors
- Invalid phone number → Log error, notify sender
- Insufficient funds → Alert admin
- Network timeout → Retry with backoff
- Rate limit exceeded → Queue for later (optional)

### Response Codes
- `200 OK` → Email processed successfully
- `400 Bad Request` → Invalid email format
- `422 Unprocessable Entity` → Invalid phone number
- `429 Too Many Requests` → Rate limit exceeded
- `500 Internal Server Error` → Processing failure

## Security Considerations

### 1. Sender Validation
- Implement SPF/DKIM checks
- Whitelist trusted senders
- Block known spam domains

### 2. Content Filtering
- Sanitize message content
- Block malicious URLs (optional)
- Filter profanity (optional)

### 3. Rate Limiting
- Per-sender limits
- Per-recipient limits
- Global throttling

### 4. Secret Management
- Store credentials in Cloudflare Secrets
- Never log sensitive data
- Rotate tokens periodically

### 5. Audit Trail
- Log all transactions
- Track failures and anomalies
- Monitor for abuse patterns

## Performance Optimization

### 1. Email Parsing
- Stream large emails
- Limit attachment processing
- Cache parsed results (if applicable)

### 2. Twilio API Calls
- Connection pooling
- Request timeout limits
- Async processing where possible

### 3. KV Storage
- Batch writes when possible
- Use expiring keys for rate limits
- Minimize read operations

### 4. Worker Efficiency
- Keep worker small (<1MB)
- Minimize dependencies
- Use lazy loading for heavy modules

## Monitoring and Alerts

### Metrics to Track
- Email received count
- SMS sent successfully
- Failed deliveries
- Average processing time
- Rate limit hits

### Alert Conditions
- Failed sends > 10% of total
- Processing time > 5 seconds
- Rate limit exceeded
- Twilio balance low
- Worker errors

### Logging Strategy
- Debug logs in development
- Info logs for transactions
- Error logs for failures
- Metrics to Analytics Engine

## Scaling Considerations

### Current Limits (Cloudflare Workers)
- CPU time: 50ms (free), 30s (paid)
- Memory: 128MB
- Request size: 100MB
- Requests: 100k/day (free), unlimited (paid)

### Email Routing Limits
- Messages: 1000/day (free tier)
- Message size: 25MB max
- Recipients: Unlimited

### Twilio Limits
- Depends on account type
- Rate limits vary by region
- Message queuing available

### Optimization Strategies
- Use Durable Objects for rate limiting (better precision)
- Implement message queuing for high volume
- Batch processing for multiple recipients
- Cache frequently used data in KV

## Testing Strategy

### Unit Tests
- Phone number parsing
- Content extraction
- Validation logic
- Error handling

### Integration Tests
- Email parsing end-to-end
- Twilio API calls (mocked)
- Rate limiter behavior
- Error scenarios

### E2E Tests
- Send test email
- Verify SMS delivery
- Check logs and metrics
- Test error conditions

## Deployment Process

1. **Development**
   ```bash
   npm run dev
   # Test locally with wrangler
   ```

2. **Testing**
   ```bash
   npm run test
   # Run test suite
   ```

3. **Deploy Secrets**
   ```bash
   npx wrangler secret put TWILIO_ACCOUNT_SID
   npx wrangler secret put TWILIO_AUTH_TOKEN
   npx wrangler secret put TWILIO_PHONE_NUMBER
   ```

4. **Deploy Worker**
   ```bash
   npm run deploy
   ```

5. **Configure Email Routing**
   - Set up route in Cloudflare dashboard
   - Test with sample email

## Future Enhancements

### Phase 2
- Bidirectional SMS (reply to sender)
- MMS support (images/attachments)
- Multiple Twilio accounts (load balancing)
- Custom sender numbers per recipient

### Phase 3
- Email templates
- Scheduled sending
- Message queuing with Cloudflare Queues
- Advanced analytics dashboard

### Phase 4
- AI content filtering
- Automatic language translation
- Voice call support
- Integration with other messaging platforms (WhatsApp, etc.)

## References

- [Cloudflare Email Routing Docs](https://developers.cloudflare.com/email-routing/)
- [Cloudflare Workers Docs](https://developers.cloudflare.com/workers/)
- [Twilio SMS API](https://www.twilio.com/docs/sms)
- [E.164 Phone Number Format](https://en.wikipedia.org/wiki/E.164)
