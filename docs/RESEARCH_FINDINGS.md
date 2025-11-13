# Email2SMS Integration Research Findings

**Research Agent Report**
**Date:** 2025-11-13
**Task ID:** research
**Memory Key:** hive/research/api-findings

## Executive Summary

This document contains comprehensive research findings for integrating Cloudflare Email Routing with Twilio SMS API to create an email-to-SMS bridge service. The research analyzed three key documentation sources and existing implementation code.

---

## 1. Cloudflare Email Routing API

### 1.1 Email Worker Handler

**Event Handler Pattern:**
```typescript
export default {
  async email(message, env, ctx) {
    // Email processing logic
  }
}
```

**Alternative addEventListener Pattern:**
```typescript
addEventListener("email", async (event) => {
  await event.message.forward("<YOUR_EMAIL>");
});
```

### 1.2 ForwardableEmailMessage Interface

**Message Properties:**
- `from` (string): Sender email address
- `to` (string): Recipient email address
- `headers` (Headers): Email headers object
- `raw` (ReadableStream): Raw email content stream
- `rawSize` (number): Size of email in bytes

**Message Methods:**
- `forward(rcptTo: string, headers?: Headers): Promise<void>` - Forward email to another address
- `setReject(reason: string): void` - Reject incoming email with reason
- `reply(message: EmailMessage): Promise<void>` - Reply to sender

### 1.3 EmailMessage Class

**Constructor:**
```typescript
import { EmailMessage } from "cloudflare:email";

const message = new EmailMessage(
  from: string,      // Sender address
  to: string,        // Recipient address
  raw: ReadableStream // Email content
);
```

### 1.4 Email Parsing

**Using PostalMime for parsing:**
```typescript
import * as PostalMime from 'postal-mime';

const parser = new PostalMime.default();
const rawEmail = new Response(message.raw);
const email = await parser.parse(await rawEmail.arrayBuffer());

// Parsed email contains:
// - email.subject
// - email.text
// - email.html
// - email.attachments
```

### 1.5 Configuration

**Wrangler.toml Email Worker Binding:**
- Email Workers are bound to specific email routes/addresses
- Each route triggers the worker when email is received
- Routes configured via Cloudflare Dashboard or API

**Local Development:**
```bash
wrangler dev
# Email events can be simulated locally
```

---

## 2. Twilio SMS Messaging API

### 2.1 Required Credentials

**Environment Variables (CRITICAL - Never hardcode):**
1. `TWILIO_ACCOUNT_SID` - Account identifier from Twilio Console
2. `TWILIO_AUTH_TOKEN` - Authentication token (secret)
3. `TWILIO_PHONE_NUMBER` - Twilio phone number to send from (E.164 format)

**Finding Credentials:**
- Available at: https://www.twilio.com/console
- Account SID format: Starts with "AC"
- Phone Number format: E.164 (e.g., +12345678900)

### 2.2 SDK Initialization

```javascript
import { Twilio } from 'twilio';

const client = new Twilio(
  process.env.TWILIO_ACCOUNT_SID,
  process.env.TWILIO_AUTH_TOKEN
);
```

### 2.3 Sending SMS Messages

**Basic SMS:**
```javascript
const message = await client.messages.create({
  to: '+1234567890',      // Recipient phone number (E.164)
  from: env.TWILIO_PHONE_NUMBER,  // Your Twilio number
  body: 'Message content'  // SMS text content
});
```

**Response Properties:**
```javascript
{
  sid: 'SM...',           // Message SID
  status: 'queued',       // Message status
  account_sid: 'AC...',   // Your account
  from: '+1...',          // Sender number
  to: '+1...',            // Recipient number
  body: '...',            // Message content
  date_created: '...',    // Timestamp
  price: '...',           // Cost
  uri: '...'              // API resource URI
}
```

### 2.4 Authentication

**HTTP Basic Authentication:**
- Username: `TWILIO_ACCOUNT_SID`
- Password: `TWILIO_AUTH_TOKEN`

**API Base URL:**
```
https://api.twilio.com/2010-04-01/Accounts/{AccountSid}/Messages
```

### 2.5 Rate Limits & Error Handling

**Rate Limiting:**
- Twilio queues messages at prescribed rate limits
- Rate limits vary by account tier and phone number type
- Messages exceeding rate limits are queued automatically
- Default: One request per five seconds for some operations

**Error Codes to Handle:**
- `30883`: Content Violation
- `30884`: Spam/Phishing risk
- `30885`: Fraudulent activity
- `30882`: Terms & Conditions violation
- Invalid phone number errors
- Authentication failures

**Best Practices:**
- Implement exponential backoff for retries
- Validate phone numbers before sending
- Monitor message status via callbacks or polling
- Handle delivery failures gracefully

---

## 3. Integration Architecture

### 3.1 Required Environment Variables

**Cloudflare Workers Configuration:**
```toml
# wrangler.toml
[vars]
# Public variables (non-sensitive)

# Secrets (use: wrangler secret put <KEY>)
# TWILIO_ACCOUNT_SID
# TWILIO_AUTH_TOKEN
# TWILIO_PHONE_NUMBER
```

**Setting Secrets:**
```bash
# Production
wrangler secret put TWILIO_ACCOUNT_SID
wrangler secret put TWILIO_AUTH_TOKEN
wrangler secret put TWILIO_PHONE_NUMBER

# Development (.dev.vars file)
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_PHONE_NUMBER=+1234567890
```

### 3.2 Security Best Practices

**Critical Security Rules:**
1. ✅ NEVER hardcode credentials in source code
2. ✅ Use Cloudflare Workers secrets for production
3. ✅ Use `.dev.vars` file for local development (add to .gitignore)
4. ✅ Implement sender validation (allowlist/blocklist)
5. ✅ Validate phone numbers before sending
6. ✅ Sanitize email content before forwarding to SMS
7. ✅ Implement rate limiting on worker side
8. ✅ Log security events for audit trail

### 3.3 Error Handling Patterns

**Recommended Error Handling:**
```typescript
export default {
  async email(message, env, ctx) {
    try {
      // 1. Validate sender
      const allowedSenders = ['trusted@example.com'];
      if (!allowedSenders.includes(message.from)) {
        message.setReject('Sender not authorized');
        return;
      }

      // 2. Parse email content
      const parser = new PostalMime.default();
      const email = await parser.parse(
        await new Response(message.raw).arrayBuffer()
      );

      // 3. Send SMS with error handling
      const client = new Twilio(
        env.TWILIO_ACCOUNT_SID,
        env.TWILIO_AUTH_TOKEN
      );

      await client.messages.create({
        to: extractPhoneNumber(email),
        from: env.TWILIO_PHONE_NUMBER,
        body: sanitizeContent(email.text)
      });

    } catch (error) {
      // Log error for debugging
      console.error('Email2SMS Error:', error);

      // Optionally notify admin
      if (env.ADMIN_EMAIL) {
        await message.forward(env.ADMIN_EMAIL);
      }
    }
  }
}
```

### 3.4 Content Processing

**Email to SMS Considerations:**
- SMS has 160 character limit (GSM-7)
- 70 characters for UCS-2 (Unicode)
- Consider truncating or splitting long emails
- Strip HTML formatting
- Remove email signatures
- Handle attachments appropriately (link or ignore)

**Recommended Processing:**
```typescript
function sanitizeContent(emailText: string): string {
  // Remove excessive whitespace
  let content = emailText.trim().replace(/\s+/g, ' ');

  // Truncate if too long (leaving room for sender info)
  const MAX_SMS_LENGTH = 140; // Leave room for "From: ..."
  if (content.length > MAX_SMS_LENGTH) {
    content = content.substring(0, MAX_SMS_LENGTH - 3) + '...';
  }

  return content;
}
```

---

## 4. Existing Implementation Analysis

### 4.1 Current Project Structure

**File:** `/home/ruhroh/email2sms/twilio-cloudflare-workflow/src/index.ts`

**Current Implementation:**
- Uses Hono framework for HTTP routing
- Implements Cloudflare Workflows (not Email Workers)
- Handles SMS webhooks via POST endpoint
- Uses Twilio for outbound calls (not SMS)

**Key Observations:**
- Current code is for Twilio SMS → Cloudflare Workflow → Twilio Call
- NOT configured for Email → SMS conversion
- Uses workflow delays (135 seconds)
- Environment variables already structured correctly

### 4.2 Package Dependencies

**Current packages.json:**
```json
{
  "dependencies": {
    "hono": "^4.6.8",
    "twilio": "^5.3.5"
  }
}
```

**Additional packages needed for Email2SMS:**
```json
{
  "dependencies": {
    "hono": "^4.6.8",
    "twilio": "^5.3.5",
    "postal-mime": "^2.x",  // For email parsing
    "mimetext": "^3.x"      // For email composition (if replying)
  }
}
```

### 4.3 Wrangler Configuration

**Current wrangler.toml:**
- Project name: "twilio-workflow"
- Main file: "src/index.ts"
- Compatibility flags: nodejs_compat (✓ Required for Twilio SDK)
- Assets directory: "public"
- Workflows defined (not needed for Email Worker)

**Changes needed:**
- Remove or comment out `[[workflows]]` section
- Add email route bindings (via Dashboard or API)
- Configure secrets for Twilio credentials

---

## 5. Implementation Recommendations

### 5.1 Priority 1: Security & Validation

1. **Sender Allowlist**: Implement strict sender validation
2. **Phone Number Validation**: Use E.164 format validation
3. **Content Sanitization**: Strip potentially dangerous content
4. **Rate Limiting**: Prevent abuse at worker level

### 5.2 Priority 2: Reliability

1. **Error Recovery**: Implement retry logic with exponential backoff
2. **Logging**: Comprehensive logging for debugging
3. **Dead Letter Queue**: Handle failed messages appropriately
4. **Monitoring**: Set up alerts for failures

### 5.3 Priority 3: User Experience

1. **SMS Length Management**: Smart truncation or splitting
2. **Sender Identification**: Include email sender in SMS
3. **Subject Line**: Include in SMS if space permits
4. **Delivery Confirmation**: Optional email reply with status

---

## 6. Testing Strategy

### 6.1 Local Development

**Setup:**
1. Create `.dev.vars` file with credentials
2. Run `wrangler dev` for local testing
3. Use Cloudflare's email simulation features
4. Test with Twilio test credentials first

### 6.2 Test Cases

**Functional Tests:**
- [ ] Valid email triggers SMS successfully
- [ ] Invalid sender is rejected
- [ ] Long email content is truncated properly
- [ ] HTML emails are converted to plain text
- [ ] Invalid phone numbers are handled gracefully
- [ ] Twilio API errors are caught and logged

**Security Tests:**
- [ ] Unauthorized senders are blocked
- [ ] Secrets are not exposed in logs
- [ ] SQL injection attempts are sanitized
- [ ] XSS attempts in email content are neutralized

**Performance Tests:**
- [ ] Worker responds within timeout limits
- [ ] Concurrent emails are handled properly
- [ ] Rate limits are respected

---

## 7. Deployment Checklist

### 7.1 Pre-Deployment

- [ ] All secrets configured via `wrangler secret put`
- [ ] Email routes configured in Cloudflare Dashboard
- [ ] Twilio phone number verified and active
- [ ] Error handling and logging implemented
- [ ] Tests passing in staging environment

### 7.2 Post-Deployment

- [ ] Monitor logs for errors
- [ ] Verify SMS delivery
- [ ] Test with real email addresses
- [ ] Set up alerts for failures
- [ ] Document operational procedures

---

## 8. References

### 8.1 Documentation Sources

1. **Cloudflare Email Routing**: https://developers.cloudflare.com/email-routing/
2. **Cloudflare Email Workers**: https://developers.cloudflare.com/email-routing/email-workers/
3. **Cloudflare Workers Runtime API**: https://developers.cloudflare.com/workers/
4. **Twilio Messaging API**: https://www.twilio.com/docs/messaging/api
5. **Twilio SMS Documentation**: https://www.twilio.com/docs/messaging

### 8.2 Related Files

- `/home/ruhroh/email2sms/twilio-cloudflare-workflow/src/index.ts` - Current implementation
- `/home/ruhroh/email2sms/twilio-cloudflare-workflow/wrangler.toml` - Worker configuration
- `/home/ruhroh/email2sms/twilio-cloudflare-workflow/package.json` - Dependencies

---

## Appendix A: Quick Reference

### Environment Variables
```bash
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+1234567890
```

### Email Worker Pattern
```typescript
export default {
  async email(message, env, ctx) {
    // Process email
    const client = new Twilio(env.TWILIO_ACCOUNT_SID, env.TWILIO_AUTH_TOKEN);
    await client.messages.create({
      to: extractPhone(message),
      from: env.TWILIO_PHONE_NUMBER,
      body: extractContent(message)
    });
  }
}
```

### Wrangler Commands
```bash
wrangler dev                    # Local development
wrangler deploy                 # Deploy to production
wrangler secret put <KEY>       # Add secret
wrangler secret list            # List secrets
wrangler tail                   # View logs
```

---

**Research Status**: ✅ COMPLETE
**Memory Storage**: ✅ Stored in hive/research/api-findings
**Coordination Hooks**: ✅ Pre-task and Post-task executed
**Next Steps**: Ready for implementation by CODER agent
