# Cloudflare Email Worker Requirements - Complete Technical Specification

**Research Date:** 2025-11-13
**Purpose:** Email-to-SMS MVP Implementation
**Source:** Cloudflare Email Routing Documentation

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Email Worker Structure](#email-worker-structure)
3. [Runtime API Reference](#runtime-api-reference)
4. [Configuration Requirements](#configuration-requirements)
5. [Email Parsing & Processing](#email-parsing--processing)
6. [Size Limits & Constraints](#size-limits--constraints)
7. [Deployment Process](#deployment-process)
8. [SMS Integration Strategy](#sms-integration-strategy)
9. [MVP Requirements Checklist](#mvp-requirements-checklist)

---

## Executive Summary

Cloudflare Email Workers allow processing incoming emails with custom JavaScript/TypeScript logic. For our email-to-SMS MVP:

- **Email Worker receives** emails via Email Routing
- **Worker parses** email content using `postal-mime` library
- **Worker extracts** text for SMS conversion
- **Worker sends** SMS via Twilio API
- **Maximum email size**: 25 MiB
- **Development**: Local testing with `wrangler dev`
- **Deployment**: `wrangler deploy`

---

## Email Worker Structure

### Basic Worker Template (ES Modules - REQUIRED)

```javascript
export default {
  async email(message, env, ctx) {
    // message: ForwardableEmailMessage object
    // env: Environment bindings (secrets, KV, etc.)
    // ctx: Execution context (waitUntil)

    // Process email logic here
  }
};
```

### Three Required Steps

1. **Create Email Worker** - Write the worker code
2. **Add Business Logic** - Implement email processing rules
3. **Bind to Route** - Configure email address that forwards to worker

**Example Route Binding:**
- Route: `sms@yourdomain.com`
- Worker: `email-to-sms-worker`
- All emails to `sms@yourdomain.com` → processed by worker

---

## Runtime API Reference

### ForwardableEmailMessage Interface

```typescript
interface ForwardableEmailMessage<Body = unknown> {
  readonly from: string;           // Envelope From address
  readonly to: string;             // Envelope To address
  readonly headers: Headers;       // Email headers (Web API Headers)
  readonly raw: ReadableStream;    // Raw email content stream
  readonly rawSize: number;        // Size in bytes

  setReject(reason: string): void;
  forward(rcptTo: string, headers?: Headers): Promise<void>;
  reply(message: EmailMessage): Promise<void>;
}
```

### Key Properties

**`message.from`** (string)
- Sender email address
- Example: `sender@example.com`

**`message.to`** (string)
- Recipient email address (your custom address)
- Example: `sms@yourdomain.com`

**`message.headers`** (Headers object)
- Standard Web API Headers object
- Access via: `message.headers.get('Subject')`
- Common headers: `Subject`, `From`, `To`, `Date`, `Message-ID`

**`message.raw`** (ReadableStream)
- Raw RFC5322 email message
- Parse with `postal-mime` or similar library
- Convert to Response: `new Response(message.raw)`

**`message.rawSize`** (number)
- Total email size in bytes
- Use to check against limits

### Key Methods

**`message.forward(rcptTo, headers?)`**
```javascript
// Forward to verified destination
await message.forward("verified@example.com");

// Forward with additional headers (X-* only)
await message.forward("verified@example.com", {
  "X-Processed-By": "Email-to-SMS-Worker"
});
```

**`message.setReject(reason)`**
```javascript
// Reject with SMTP error
message.setReject("Address not allowed");
// Returns permanent SMTP error to sender
```

**`message.reply(EmailMessage)`**
```javascript
import { EmailMessage } from "cloudflare:email";
import { createMimeMessage } from "mimetext";

const replyMsg = createMimeMessage();
replyMsg.setSender({ addr: "noreply@yourdomain.com" });
replyMsg.setRecipient(message.from);
replyMsg.setSubject("SMS Sent");
replyMsg.addMessage({
  contentType: 'text/plain',
  data: 'Your message was sent via SMS'
});

const emailMsg = new EmailMessage(
  "noreply@yourdomain.com",
  message.from,
  replyMsg.asRaw()
);

await message.reply(emailMsg);
```

---

## Configuration Requirements

### wrangler.toml Configuration

**Minimal Configuration:**
```toml
name = "email-to-sms-worker"
main = "src/index.js"
compatibility_date = "2024-01-01"

[[send_email]]
name = "EMAIL"
```

**Production Configuration with Secrets:**
```toml
name = "email-to-sms-worker"
main = "src/index.js"
compatibility_date = "2024-01-01"

# Email sending capability (optional)
[[send_email]]
name = "EMAIL"
destination_address = "admin@yourdomain.com"

# Environment variables (non-secret)
[vars]
SMS_FROM_NUMBER = "+15551234567"
SMS_MAX_LENGTH = "160"

# Secrets (set via: wrangler secret put TWILIO_ACCOUNT_SID)
# - TWILIO_ACCOUNT_SID
# - TWILIO_AUTH_TOKEN
# - TWILIO_TO_NUMBER (or allow dynamic routing)
```

**Alternative: wrangler.jsonc Format**
```jsonc
{
  "$schema": "./node_modules/wrangler/config-schema.json",
  "name": "email-to-sms-worker",
  "main": "src/index.js",
  "compatibility_date": "2024-01-01",
  "send_email": [
    {
      "name": "EMAIL",
      "destination_address": "admin@yourdomain.com"
    }
  ],
  "vars": {
    "SMS_FROM_NUMBER": "+15551234567",
    "SMS_MAX_LENGTH": "160"
  }
}
```

### Setting Secrets

```bash
# Set Twilio credentials as secrets
wrangler secret put TWILIO_ACCOUNT_SID
wrangler secret put TWILIO_AUTH_TOKEN
wrangler secret put TWILIO_TO_NUMBER

# Access in worker via env object
export default {
  async email(message, env, ctx) {
    const accountSid = env.TWILIO_ACCOUNT_SID;
    const authToken = env.TWILIO_AUTH_TOKEN;
    const toNumber = env.TWILIO_TO_NUMBER;
  }
};
```

### Environment Bindings

**Available via `env` object:**
- **Secrets**: `env.TWILIO_ACCOUNT_SID`, `env.TWILIO_AUTH_TOKEN`
- **Variables**: `env.SMS_FROM_NUMBER`, `env.SMS_MAX_LENGTH`
- **KV Namespaces**: `env.MY_KV` (if configured)
- **Durable Objects**: `env.MY_DO` (if configured)
- **Email Send**: `env.EMAIL.send(message)` (if send_email configured)

---

## Email Parsing & Processing

### Using postal-mime Library

**Installation:**
```bash
npm install postal-mime
```

**Parsing Email Content:**
```typescript
import * as PostalMime from 'postal-mime';

export default {
  async email(message, env, ctx) {
    // Parse email
    const parser = new PostalMime.default();
    const rawEmail = new Response(message.raw);
    const email = await parser.parse(await rawEmail.arrayBuffer());

    // Access parsed data
    console.log({
      from: email.from,           // { address: 'sender@example.com', name: 'John' }
      to: email.to,               // [{ address: 'recipient@example.com', name: '' }]
      subject: email.subject,     // 'Testing Email Workers'
      text: email.text,           // Plain text content
      html: email.html,           // HTML content
      attachments: email.attachments  // Array of attachments
    });

    // Use text or html for SMS
    const smsContent = email.text || email.html || '';
  }
};
```

**Parsed Email Structure:**
```javascript
{
  headers: [
    { key: 'from', value: '"John" <sender@example.com>' },
    { key: 'to', value: 'recipient@example.com' },
    { key: 'subject', value: 'Testing Email Workers' },
    { key: 'content-type', value: 'text/plain; charset="utf-8"' },
    { key: 'date', value: 'Tue, 27 Aug 2024 08:49:44 -0700' },
    { key: 'message-id', value: '<abc123@example.com>' }
  ],
  from: { address: 'sender@example.com', name: 'John' },
  to: [ { address: 'recipient@example.com', name: '' } ],
  replyTo: [ { address: 'sender@example.com', name: '' } ],
  subject: 'Testing Email Workers',
  messageId: '<abc123@example.com>',
  date: '2024-08-27T15:49:44.000Z',
  text: 'Plain text content here\n',
  html: '<p>HTML content here</p>',
  attachments: []
}
```

### Text Extraction for SMS

**Priority order:**
1. `email.text` - Plain text version (preferred for SMS)
2. `email.html` - HTML version (requires stripping HTML tags)
3. `email.subject` - Fallback if body is empty

**HTML to Text Conversion:**
```javascript
function htmlToText(html) {
  return html
    .replace(/<[^>]*>/g, '')        // Remove HTML tags
    .replace(/&nbsp;/g, ' ')        // Replace &nbsp;
    .replace(/&amp;/g, '&')         // Replace &amp;
    .replace(/&lt;/g, '<')          // Replace &lt;
    .replace(/&gt;/g, '>')          // Replace &gt;
    .replace(/\s+/g, ' ')           // Normalize whitespace
    .trim();
}
```

### SMS Length Truncation

```javascript
function truncateForSMS(text, maxLength = 160) {
  if (text.length <= maxLength) {
    return text;
  }
  return text.substring(0, maxLength - 3) + '...';
}
```

---

## Size Limits & Constraints

### Email Routing Limits

**Maximum Email Size: 25 MiB**
- Cloudflare Email Routing does not support messages larger than 25 MiB
- Check size: `message.rawSize` (bytes)
- 25 MiB = 26,214,400 bytes

**Email Worker Size Limits:**
- Workers on free tier may encounter allocation errors with large emails
- Complex email processing may require paid Workers tier
- Refer to: [Worker Limits](https://developers.cloudflare.com/workers/platform/limits/#worker-limits)

### SMS Constraints

**Twilio SMS Limits:**
- Standard SMS: 160 characters
- Extended SMS: Up to 1600 characters (sent as multiple segments)
- MMS: Up to 1600 characters + media

**Recommended SMS Strategy:**
- Extract first 160 characters for basic SMS
- Use subject line if body is too long
- Consider MMS for longer content
- Store full email in KV if needed for later retrieval

### Validation Requirements

```javascript
export default {
  async email(message, env, ctx) {
    // Check email size
    const MAX_EMAIL_SIZE = 25 * 1024 * 1024; // 25 MiB
    if (message.rawSize > MAX_EMAIL_SIZE) {
      message.setReject("Email too large");
      return;
    }

    // Validate sender (optional)
    const allowedSenders = ['allowed@example.com'];
    if (!allowedSenders.includes(message.from)) {
      message.setReject("Sender not authorized");
      return;
    }

    // Process email...
  }
};
```

---

## Deployment Process

### Local Development

**Start Development Server:**
```bash
npx wrangler dev
```

**Test Email Endpoint:**
```bash
curl --request POST 'http://localhost:8787/cdn-cgi/handler/email' \
  --url-query 'from=sender@example.com' \
  --url-query 'to=sms@yourdomain.com' \
  --header 'Content-Type: application/json' \
  --data-raw 'From: sender@example.com
To: sms@yourdomain.com
Subject: Test Email

This is a test message for SMS conversion.'
```

**Local Testing Output:**
```
✨ Starting local server...
[wrangler:inf] Ready on http://localhost:8787
[wrangler:inf] Email handler processed message
```

### Production Deployment

**Deploy Worker:**
```bash
wrangler deploy
```

**Deployment Output:**
```
✨ Deploying email-to-sms-worker...
✅ Deployed email-to-sms-worker
   https://email-to-sms-worker.<subdomain>.workers.dev
```

### Cloudflare Dashboard Setup

**Enable Email Workers:**
1. Log in to [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Select your account and domain
3. Go to **Email** > **Email Routing** > **Email Workers**
4. Select **Get started** (first time only)
5. Select **Create**

**Create Email Worker:**
1. Enter worker name: `email-to-sms-worker`
2. Choose starter template or **Create my own**
3. Add/edit code in editor
4. Select **Save and deploy**

**Bind Worker to Route:**
1. Find your worker in Email Workers list
2. Select **Create route**
3. Enter custom address: `sms@yourdomain.com`
4. Select **Save**

**Verify Setup:**
- Route: `sms@yourdomain.com` → Worker: `email-to-sms-worker`
- Send test email to `sms@yourdomain.com`
- Check worker logs: `wrangler tail`

---

## SMS Integration Strategy

### Twilio API Integration

**Required Twilio Credentials:**
- Account SID (secret)
- Auth Token (secret)
- From Phone Number (variable or secret)
- To Phone Number (variable or secret)

**Twilio SMS API Call:**
```javascript
async function sendSMS(env, from, to, message) {
  const accountSid = env.TWILIO_ACCOUNT_SID;
  const authToken = env.TWILIO_AUTH_TOKEN;

  const url = `https://api.twilio.com/2010-04-01/Accounts/${accountSid}/Messages.json`;

  const params = new URLSearchParams({
    From: from,
    To: to,
    Body: message
  });

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': 'Basic ' + btoa(`${accountSid}:${authToken}`),
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: params
  });

  if (!response.ok) {
    throw new Error(`Twilio API error: ${response.status}`);
  }

  return await response.json();
}
```

### Complete Email-to-SMS Worker Example

```javascript
import * as PostalMime from 'postal-mime';

export default {
  async email(message, env, ctx) {
    try {
      // 1. Validate email size
      const MAX_SIZE = 25 * 1024 * 1024; // 25 MiB
      if (message.rawSize > MAX_SIZE) {
        message.setReject("Email too large");
        return;
      }

      // 2. Parse email
      const parser = new PostalMime.default();
      const rawEmail = new Response(message.raw);
      const email = await parser.parse(await rawEmail.arrayBuffer());

      // 3. Extract text content
      let smsText = email.text || '';

      // If no text, try HTML
      if (!smsText && email.html) {
        smsText = email.html
          .replace(/<[^>]*>/g, '')
          .replace(/&nbsp;/g, ' ')
          .replace(/&amp;/g, '&')
          .trim();
      }

      // If still no text, use subject
      if (!smsText) {
        smsText = email.subject || 'Empty email';
      }

      // 4. Truncate for SMS
      const MAX_SMS_LENGTH = 160;
      if (smsText.length > MAX_SMS_LENGTH) {
        smsText = smsText.substring(0, MAX_SMS_LENGTH - 3) + '...';
      }

      // 5. Send SMS via Twilio
      const smsResult = await sendSMS(
        env,
        env.SMS_FROM_NUMBER,
        env.TWILIO_TO_NUMBER,
        smsText
      );

      console.log('SMS sent:', smsResult.sid);

      // 6. Optional: Send confirmation reply
      // await message.reply(createConfirmationEmail(email.from));

    } catch (error) {
      console.error('Error processing email:', error);
      // Don't reject - just log error
      // message.setReject("Processing error");
    }
  }
};

async function sendSMS(env, from, to, body) {
  const accountSid = env.TWILIO_ACCOUNT_SID;
  const authToken = env.TWILIO_AUTH_TOKEN;

  const url = `https://api.twilio.com/2010-04-01/Accounts/${accountSid}/Messages.json`;

  const params = new URLSearchParams({
    From: from,
    To: to,
    Body: body
  });

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': 'Basic ' + btoa(`${accountSid}:${authToken}`),
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: params
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Twilio API error: ${response.status} - ${error}`);
  }

  return await response.json();
}
```

---

## MVP Requirements Checklist

### ✅ Prerequisites

- [ ] Cloudflare account with domain
- [ ] Email Routing enabled on domain
- [ ] Verified destination email addresses (for testing)
- [ ] Twilio account with phone number
- [ ] Wrangler CLI installed (`npm install -g wrangler`)

### ✅ Configuration Files

- [ ] `wrangler.toml` created with:
  - [ ] Worker name
  - [ ] Main entry point
  - [ ] Compatibility date
  - [ ] Environment variables (non-secret)
- [ ] `.env` file for local secrets (not committed)
- [ ] `.gitignore` includes `.env` and secrets

### ✅ Secrets Configuration

- [ ] `TWILIO_ACCOUNT_SID` set via `wrangler secret put`
- [ ] `TWILIO_AUTH_TOKEN` set via `wrangler secret put`
- [ ] `TWILIO_TO_NUMBER` set (or dynamically configured)
- [ ] `SMS_FROM_NUMBER` configured (variable or secret)

### ✅ Worker Implementation

- [ ] Email handler function implemented (`async email(message, env, ctx)`)
- [ ] Email parsing using `postal-mime`
- [ ] Text extraction logic (text → html fallback → subject)
- [ ] HTML tag stripping if using HTML content
- [ ] SMS length truncation (160 characters)
- [ ] Twilio API integration
- [ ] Error handling and logging
- [ ] Email size validation (25 MiB limit)
- [ ] Optional: Sender validation/allowlist

### ✅ Dependencies

- [ ] `postal-mime` installed (`npm install postal-mime`)
- [ ] `package.json` with dependencies
- [ ] TypeScript types if using TS (`npm install -D @cloudflare/workers-types`)

### ✅ Testing

- [ ] Local development works (`wrangler dev`)
- [ ] Test email parsing with sample emails
- [ ] Twilio API call succeeds (test mode)
- [ ] SMS received on test phone number
- [ ] Error handling tested (invalid email, API failure)
- [ ] Size limit validation tested

### ✅ Deployment

- [ ] Worker deployed (`wrangler deploy`)
- [ ] Email Worker created in Cloudflare Dashboard
- [ ] Route bound to worker (`sms@yourdomain.com`)
- [ ] Test email sent to production route
- [ ] SMS received from production
- [ ] Worker logs monitored (`wrangler tail`)

### ✅ Production Monitoring

- [ ] Error logging configured
- [ ] SMS delivery confirmation
- [ ] Email routing analytics checked
- [ ] Worker execution logs reviewed
- [ ] Twilio usage dashboard monitored

### ✅ Documentation

- [ ] Configuration documented
- [ ] Deployment process documented
- [ ] Testing procedures documented
- [ ] Troubleshooting guide created
- [ ] Security best practices documented

---

## Key Technical Insights

### Email Worker Event Handler

**ES Modules Format (Required):**
```javascript
export default {
  async email(message, env, ctx) {
    // Handler receives 3 parameters:
    // - message: ForwardableEmailMessage
    // - env: Environment bindings (secrets, KV, variables)
    // - ctx: Execution context (waitUntil for async tasks)
  }
};
```

**Service Worker Format (Deprecated):**
```javascript
addEventListener("email", async (event) => {
  // event.message: ForwardableEmailMessage
});
```

### Message Processing Options

**1. Forward to verified address:**
```javascript
await message.forward("verified@example.com");
```

**2. Reject with error:**
```javascript
message.setReject("Sender not allowed");
```

**3. Drop (do nothing):**
```javascript
// Simply return without calling forward or setReject
return;
```

**4. Process and forward:**
```javascript
// Process email (send SMS, store in DB, etc.)
await processEmail(message, env);

// Then forward to archive
await message.forward("archive@example.com");
```

### Headers Access

```javascript
const subject = message.headers.get('Subject');
const from = message.headers.get('From');
const date = message.headers.get('Date');
const messageId = message.headers.get('Message-ID');
const contentType = message.headers.get('Content-Type');
```

### Raw Email Stream

```javascript
// Convert ReadableStream to Response
const response = new Response(message.raw);

// Get as ArrayBuffer
const buffer = await response.arrayBuffer();

// Get as text
const text = await response.text();

// Parse with postal-mime
const parser = new PostalMime.default();
const email = await parser.parse(buffer);
```

---

## Security Considerations

### Secrets Management

**DO:**
- ✅ Use `wrangler secret put` for sensitive data
- ✅ Store Twilio credentials as secrets
- ✅ Use environment variables for configuration
- ✅ Never commit secrets to git

**DON'T:**
- ❌ Hardcode API keys in code
- ❌ Commit `.env` files
- ❌ Log secrets to console
- ❌ Include secrets in error messages

### Email Validation

**Recommended Validations:**
```javascript
// Check sender allowlist
const allowedSenders = ['allowed@example.com'];
if (!allowedSenders.includes(message.from)) {
  message.setReject("Sender not authorized");
  return;
}

// Check email size
if (message.rawSize > 25 * 1024 * 1024) {
  message.setReject("Email too large");
  return;
}

// Check recipient (ensure it's your custom address)
if (message.to !== 'sms@yourdomain.com') {
  message.setReject("Invalid recipient");
  return;
}

// Validate DMARC (for reply functionality)
// Note: Reply only works with valid DMARC
```

### Rate Limiting

**Consider:**
- Twilio rate limits (messages per second)
- Workers rate limits (requests per minute)
- Email routing limits (messages per day)

**Implement:**
```javascript
// Use KV to track rate limits
const rateLimitKey = `ratelimit:${message.from}`;
const count = await env.RATE_LIMIT_KV.get(rateLimitKey);

if (count && parseInt(count) > 10) {
  message.setReject("Rate limit exceeded");
  return;
}

// Increment counter
await env.RATE_LIMIT_KV.put(rateLimitKey, (parseInt(count || 0) + 1).toString(), {
  expirationTtl: 3600 // 1 hour
});
```

---

## Troubleshooting Guide

### Common Issues

**1. Worker not receiving emails:**
- Verify Email Routing is enabled
- Check route binding in Cloudflare Dashboard
- Confirm custom address is correct
- Test with `wrangler tail` to see logs

**2. Parsing errors:**
- Check `postal-mime` is installed
- Verify email format is valid
- Test with simple text email first
- Log `message.raw` to debug

**3. Twilio API errors:**
- Verify credentials are correct
- Check phone number format (+1234567890)
- Ensure Twilio account has funds
- Review Twilio error codes

**4. Size limit errors:**
- Check `message.rawSize` before processing
- Email Routing max: 25 MiB
- Workers may have additional limits on free tier

**5. Deployment issues:**
- Run `wrangler login` to authenticate
- Verify `wrangler.toml` is correct
- Check worker name doesn't conflict
- Review deployment logs

### Debug Commands

```bash
# View real-time logs
wrangler tail

# Test locally
wrangler dev

# Deploy to production
wrangler deploy

# List secrets
wrangler secret list

# Delete worker
wrangler delete

# View worker info
wrangler whoami
```

---

## Next Steps for MVP

1. **Setup Development Environment**
   - Install wrangler CLI
   - Create `wrangler.toml`
   - Install `postal-mime` dependency

2. **Implement Worker**
   - Create `src/index.js` with email handler
   - Add email parsing logic
   - Implement SMS sending via Twilio
   - Add error handling

3. **Configure Secrets**
   - Set Twilio credentials
   - Configure phone numbers
   - Test in local development

4. **Deploy and Test**
   - Deploy worker to Cloudflare
   - Create route in Dashboard
   - Send test emails
   - Verify SMS delivery

5. **Monitor and Iterate**
   - Review logs
   - Optimize text extraction
   - Add rate limiting
   - Improve error handling

---

## References

- **Cloudflare Email Routing**: https://developers.cloudflare.com/email-routing/
- **Email Workers**: https://developers.cloudflare.com/email-routing/email-workers/
- **Runtime API**: https://developers.cloudflare.com/email-routing/email-workers/runtime-api/
- **Local Development**: https://developers.cloudflare.com/email-routing/email-workers/local-development/
- **Workers Limits**: https://developers.cloudflare.com/workers/platform/limits/
- **Postal MIME**: https://www.npmjs.com/package/postal-mime
- **Twilio SMS API**: https://www.twilio.com/docs/sms/api
- **Wrangler CLI**: https://developers.cloudflare.com/workers/wrangler/

---

**End of Research Document**

*This research provides complete technical specifications for building an email-to-SMS worker using Cloudflare Email Routing. All information extracted from official Cloudflare documentation.*
