# Email-to-SMS User Guide

**Version:** 1.0.0
**For:** End Users and Administrators

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Using the Streamlit UI](#using-the-streamlit-ui)
4. [Sending Email-to-SMS](#sending-email-to-sms)
5. [Configuration Options](#configuration-options)
6. [Best Practices](#best-practices)
7. [Use Cases](#use-cases)
8. [FAQ](#faq)

---

## Introduction

### What is Email-to-SMS?

Email-to-SMS is a system that automatically converts emails into SMS text messages. Send an email to a special address, and it gets delivered as an SMS to any phone number.

### Why Use Email-to-SMS?

**Benefits:**
- 📧 Send SMS from any email client
- 🔔 Get notifications via SMS
- 🚀 No special app required
- 🌍 Works with any email provider
- 💰 Cost-effective for business use
- 🔒 Secure and private

**Common Uses:**
- System alerts and notifications
- Customer communications
- Personal reminders
- IoT device alerts
- Server monitoring
- Automated notifications

### How It Works

```
┌──────────────┐
│  Send Email  │
│              │
│  To: phone@  │
│  sms.domain  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Cloudflare  │
│  Email       │
│  Routing     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Worker     │
│  Processing  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Twilio     │
│   SMS API    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ SMS Delivered│
│  to Phone    │
└──────────────┘
```

---

## Getting Started

### Prerequisites

To use the system, you need:

1. **Email Account** - Any email provider (Gmail, Outlook, etc.)
2. **Access to Email-to-SMS Domain** - Provided by your administrator
3. **Recipient Phone Number** - The phone number to receive SMS

### Quick Start

**Send your first SMS in 3 steps:**

1. **Compose Email**
   - Open your email client
   - Create new email

2. **Set Recipient**
   - To: `15551234567@sms.yourdomain.com`
   - Replace `15551234567` with target phone
   - Replace `yourdomain.com` with your domain

3. **Send**
   - Write your message
   - Click Send
   - SMS delivered in seconds!

---

## Using the Streamlit UI

### Overview

The Streamlit Code Generator creates customized Worker code for your specific needs.

### Accessing the UI

**Local Installation:**
```bash
cd streamlit-app
streamlit run app.py
```

**Cloud Access:**
If your organization hosts the UI, navigate to the provided URL (e.g., `https://email2sms.yourcompany.com`)

### Main Interface

```
┌─────────────────────────────────────────┐
│  📧 Email-to-SMS Code Generator         │
├─────────────────────────────────────────┤
│                                         │
│  ⚙️ Configuration                       │
│  ┌────────────────────────────────┐    │
│  │ Worker Name: my-email-sms      │    │
│  │ Domain: example.com            │    │
│  │ Email Pattern: *@sms.example   │    │
│  │ Twilio Phone: +15551234567     │    │
│  └────────────────────────────────┘    │
│                                         │
│  [🚀 Generate Code]                     │
│                                         │
│  📦 Generated Files                     │
│  - worker/index.ts                      │
│  - services/twilio-service.ts           │
│  - package.json                         │
│                                         │
│  [💾 Download ZIP]                      │
│                                         │
└─────────────────────────────────────────┘
```

### Step-by-Step Guide

#### Step 1: Basic Configuration

**Worker Name:**
- Name for your worker (e.g., `company-sms`)
- Letters, numbers, hyphens only
- No spaces

**Domain:**
- Your domain name (e.g., `company.com`)
- Must be managed by Cloudflare
- Email Routing must be enabled

**Email Pattern:**
- Pattern for incoming emails
- Examples:
  - `*@sms.company.com` (all addresses)
  - `alerts@sms.company.com` (specific)
  - `*@alerts.company.com` (subdomain)

#### Step 2: Twilio Configuration

**Twilio Phone Number:**
- Your Twilio phone number
- Must be in E.164 format: `+15551234567`
- Get from Twilio Console

**Account SID and Auth Token:**
- Leave blank in UI (security)
- Will be configured during deployment
- Never share these credentials

#### Step 3: Security Settings

**Allowed Senders:**
- Who can send emails?
- Options:
  - Specific: `john@company.com`
  - Domain: `*@company.com`
  - Multiple: `john@company.com,*@partner.com`
- Leave blank to allow anyone (not recommended)

**Rate Limiting:**
- Enable to prevent abuse
- Limits:
  - 10 messages/hour per sender
  - 20 messages/hour per recipient
  - 1,000 messages/day globally

#### Step 4: Features

**Enable Logging:**
- ✅ Recommended
- Stores transaction history
- Helps troubleshooting
- Required for analytics

**Enable Analytics:**
- ✅ Recommended
- Tracks metrics
- Performance monitoring
- Usage statistics

**Enable Retry Logic:**
- ✅ Recommended
- Auto-retry failed sends
- Up to 3 attempts
- Exponential backoff

#### Step 5: Advanced Options

**Content Processing:**
- **HTML to Text**: Convert HTML emails to plain text
- **Remove Signatures**: Strip email signatures
- **Smart Truncation**: Intelligent message trimming

**Phone Number Settings:**
- **Default Country Code**: For US numbers (1)
- **Allow International**: Enable non-US numbers

**Message Settings:**
- **Max Length**: 160 or 1600 characters
- **Segment Handling**: Split or truncate
- **Encoding**: GSM-7 or Unicode

#### Step 6: Generate Code

1. Review all settings
2. Click **🚀 Generate Code**
3. Wait for generation (1-2 seconds)
4. See success message
5. Review generated files

#### Step 7: Download and Deploy

**Download Options:**

1. **Download ZIP** - All files in archive
2. **Copy to Clipboard** - Individual files
3. **Save Configuration** - JSON file for later

**Deployment:**
Follow [Deployment Guide](DEPLOYMENT_MASTER.md) to deploy generated code.

---

## Sending Email-to-SMS

### Email Format Options

#### Format 1: Phone in Email Address (Recommended)

**Most Reliable Method**

```
To: 15551234567@sms.yourdomain.com
Subject: Meeting Reminder
Body: Don't forget our meeting at 2pm today!
```

**Result SMS:**
```
From: Your Name
Re: Meeting Reminder
Don't forget our meeting at 2pm today!
```

**Phone Number Variations:**
- 10 digits: `5551234567@sms.domain.com`
- With dashes: `555-123-4567@sms.domain.com`
- With spaces: `555 123 4567@sms.domain.com`
- E.164 format: `+15551234567@sms.domain.com`

#### Format 2: Phone in Subject Line

**Alternative Method**

```
To: contact@sms.yourdomain.com
Subject: To: 555-123-4567
Body: Your message content here
```

**Subject Patterns:**
- `To: 5551234567`
- `To: 555-123-4567`
- `To: (555) 123-4567`
- `Phone: 5551234567`

#### Format 3: Custom Header

**Advanced Method**

```
To: sms@yourdomain.com
X-SMS-To: +15551234567
Subject: Message Title
Body: Your message here
```

**Requirements:**
- Email client must support custom headers
- Phone number in E.164 format
- Some email services strip custom headers

### Phone Number Formats

#### Supported Formats

**US Numbers:**
- E.164: `+15551234567` ✅ Recommended
- National: `5551234567` ✅ Auto-converted
- Formatted: `555-123-4567` ✅
- Formatted: `(555) 123-4567` ✅
- With spaces: `555 123 4567` ✅

**International:**
- E.164: `+447700900123` (UK)
- E.164: `+61491570156` (Australia)
- E.164: `+81312345678` (Japan)

#### Invalid Formats

❌ Missing country code: `1234567`
❌ Too long: `12345678901234567`
❌ Letters: `555-CALL-NOW`
❌ Special chars: `555*123*4567`

### Message Content

#### Content Guidelines

**Length Limits:**
- **Standard SMS**: 160 characters (recommended)
- **Extended SMS**: Up to 1,600 characters (10 segments)
- **Subject Line**: Included in character count

**Best Practices:**
- Keep messages concise
- Use plain text (HTML converted automatically)
- Avoid excessive formatting
- No emojis for compatibility

**Automatic Processing:**
1. HTML stripped to plain text
2. Email signatures removed
3. Extra whitespace cleaned
4. Sender name added
5. Subject added (if present)

#### Message Examples

**Simple Message:**
```
Email Body:
Meeting at 2pm tomorrow

SMS Result:
From: John Doe
Re: Reminder
Meeting at 2pm tomorrow
```

**HTML Email:**
```
Email Body:
<p><strong>Important:</strong> Server is down</p>
<p>Please investigate immediately</p>

SMS Result:
From: Monitoring
Re: Alert
Important: Server is down
Please investigate immediately
```

**Long Message:**
```
Email Body:
[500 character message]

SMS Result:
From: Sender
[Truncated to 160 chars]...
```

### Sender Authorization

#### Allowed Senders

If sender allowlist is configured, only authorized emails are processed.

**Check with Administrator:**
- Is allowlist enabled?
- Is your email authorized?
- Can you request access?

**Common Configurations:**

1. **Open (No Allowlist)**
   - Anyone can send
   - Less secure
   - For internal use only

2. **Domain-Based**
   - `*@company.com` allowed
   - All company emails work
   - Recommended for companies

3. **User-Specific**
   - `john@company.com,jane@company.com`
   - Only specific users
   - Highest security

#### Unauthorized Sender Error

If you see:
```
Email rejected: Sender not authorized
```

**Solutions:**
1. Contact administrator
2. Request your email be added
3. Use authorized email account

---

## Configuration Options

### Email Routing Configuration

#### Email Pattern Types

**Catch-All Pattern:**
```
*@sms.yourdomain.com
```
- Matches any email address
- Most flexible
- Example: `anything@sms.domain.com`

**Subdomain Pattern:**
```
*@alerts.yourdomain.com
```
- Matches subdomain
- Better organization
- Example: `server1@alerts.domain.com`

**Specific Address:**
```
notifications@sms.yourdomain.com
```
- Single email address
- Most restrictive
- Exact match required

### Rate Limiting

#### Default Limits

When rate limiting is enabled:

| Scope | Limit | Window |
|-------|-------|--------|
| Per Sender | 10 messages | 1 hour |
| Per Recipient | 20 messages | 1 hour |
| Global | 1,000 messages | 24 hours |

#### Rate Limit Behavior

**What Happens:**
1. Send 10 emails from same address within 1 hour
2. 11th email is rejected
3. Error message sent to sender
4. Counter resets after 1 hour

**Rejection Message:**
```
Rate limit exceeded: Maximum 10 messages per hour from this sender.
Limit resets at: 2025-11-13 15:30:00 UTC
```

#### Adjusting Limits

Contact administrator to:
- Increase limits for specific users
- Adjust time windows
- Configure custom limits

### Content Processing Options

#### HTML Conversion

**Default Behavior:**
- HTML emails converted to plain text
- Tags removed
- Links preserved as text
- Formatting simplified

**Example:**
```
HTML: <p>Hello <strong>World</strong></p>
Text: Hello World
```

#### Signature Removal

**Automatic Removal:**
- Common signature markers detected
- Lines after `--` removed
- Company footers removed
- Disclaimers stripped

**Markers Detected:**
- `--`
- `Sent from my iPhone`
- `Best regards,`
- Email client signatures

#### Truncation Strategy

**Smart Truncation:**
1. Try to fit within 160 chars
2. Truncate at sentence boundary
3. Truncate at word boundary
4. Add `...` if truncated

**Example:**
```
Original (200 chars):
"This is a very long message that exceeds the standard SMS length limit and needs to be truncated intelligently at a good breaking point."

Truncated (160 chars):
"From: Sender
This is a very long message that exceeds the standard SMS length limit and needs to be truncated intelligently..."
```

---

## Best Practices

### Email Composition

#### 1. Use Clear Subject Lines

✅ Good:
```
Subject: Server Alert
```

❌ Poor:
```
Subject: FYI
```

#### 2. Keep Messages Concise

✅ Good (120 chars):
```
Production database CPU at 95%. Investigating issue. ETA 15 minutes.
```

❌ Poor (300 chars):
```
Hello, I wanted to let you know that we've been monitoring the production database server and we've noticed that the CPU utilization has been steadily increasing over the past hour and is now at 95%. We're currently investigating...
```

#### 3. Use Descriptive Sender Names

✅ Good:
```
From: John Doe <john@company.com>
```

❌ Poor:
```
From: noreply@system123.internal
```

#### 4. Avoid Unnecessary Formatting

✅ Good:
```
Alert: Server down. Contact support.
```

❌ Poor:
```
⚠️ 🚨 URGENT ALERT 🚨 ⚠️
**Server Status**: DOWN ❌
Please contact support ASAP!!!
```

### Phone Number Best Practices

#### 1. Use Consistent Format

**Choose One:**
- E.164: `+15551234567` (best for international)
- National: `5551234567` (US only)

#### 2. Verify Phone Numbers

Before sending:
- Confirm number is correct
- Test with known number
- Verify country code for international

#### 3. Store Frequently Used Numbers

**Email Contacts:**
```
Alerts: alerts-5551234567@sms.company.com
Support: support-5559876543@sms.company.com
```

### Security Best Practices

#### 1. Protect Email-to-SMS Address

- Don't share publicly
- Use for trusted sources only
- Avoid posting online

#### 2. Monitor Usage

- Review sent messages weekly
- Check for unauthorized use
- Report suspicious activity

#### 3. Use Strong Email Security

- Enable 2FA on email account
- Use strong passwords
- Avoid public email for sensitive SMS

### Cost Optimization

#### 1. Minimize Message Length

- Keep under 160 chars when possible
- 1 segment = $0.0075
- 10 segments = $0.075

#### 2. Batch Non-Urgent Messages

- Group updates together
- Send summary instead of multiple
- Use email for detailed info

#### 3. Use Rate Limiting

- Prevents accidental spam
- Stops runaway scripts
- Controls costs

---

## Use Cases

### 1. System Monitoring Alerts

**Scenario:**
Server monitoring system sends alerts via email

**Configuration:**
```
To: 15551234567@alerts.company.com
Subject: [CRITICAL] Database CPU 95%
```

**Benefit:**
- Instant SMS notifications
- No custom integration needed
- Works with any monitoring tool

### 2. Customer Notifications

**Scenario:**
E-commerce sends order confirmations

**Configuration:**
```
To: {customer_phone}@orders.company.com
Subject: Order #{order_id} Confirmed
Body: Your order has been confirmed. Tracking: {tracking}
```

**Benefit:**
- Direct customer communication
- Automated from order system
- No separate SMS service

### 3. Personal Reminders

**Scenario:**
Google Calendar sends reminder emails

**Configuration:**
```
To: 5551234567@remind.mydomain.com
Subject: Meeting in 1 hour
Body: Team standup at 2pm
```

**Benefit:**
- SMS reminders from calendar
- No app installation needed
- Works with any calendar service

### 4. IoT Device Alerts

**Scenario:**
Smart home device sends notifications

**Configuration:**
```
To: 5551234567@iot.mydomain.com
Subject: Motion Detected
Body: Front door camera detected motion at 3:45 PM
```

**Benefit:**
- Simple integration
- Real-time alerts
- Reliable delivery

### 5. Emergency Notifications

**Scenario:**
Critical system failures

**Configuration:**
```
To: oncall-5551234567@emergency.company.com
Subject: [P0] Production Down
Body: All services unresponsive. Response required.
```

**Benefit:**
- Guaranteed delivery
- Wake on-call engineer
- Fast incident response

### 6. Automated Workflows

**Scenario:**
Workflow automation tool

**Configuration:**
```
To: {recipient_phone}@workflow.company.com
Subject: Task Assigned: {task_name}
Body: New task assigned. Due: {due_date}
```

**Benefit:**
- No custom code needed
- Works with any automation tool
- Flexible routing

---

## FAQ

### General Questions

**Q: Do I need a special email account?**
A: No, use any email provider (Gmail, Outlook, etc.)

**Q: Can I send to international numbers?**
A: Yes, use E.164 format: `+[country][number]`

**Q: Is there a cost per message?**
A: Yes, Twilio charges ~$0.0075 per SMS (US). Check with administrator.

**Q: How fast is delivery?**
A: Typically 1-5 seconds from email to SMS.

**Q: Can I send to multiple phones?**
A: Send separate emails for each phone number.

### Technical Questions

**Q: What if email fails to send?**
A: Check email address, phone format, and contact administrator.

**Q: Can I use emojis?**
A: Yes, but they use more characters (Unicode encoding).

**Q: What happens to attachments?**
A: Attachments are ignored, only text is sent.

**Q: Can I receive SMS replies?**
A: Not by default. Contact administrator about bidirectional setup.

**Q: Is my data secure?**
A: Yes, emails are processed securely and not stored long-term.

### Troubleshooting Questions

**Q: Email sent but no SMS received?**
A: Check:
1. Phone number format
2. Sender authorization
3. Rate limits
4. Contact administrator

**Q: Why was my email rejected?**
A: Common reasons:
- Unauthorized sender
- Invalid phone format
- Rate limit exceeded
- Service temporarily down

**Q: How do I check if I'm rate limited?**
A: Error email will state "Rate limit exceeded" and reset time.

**Q: Can I get delivery confirmation?**
A: Check with administrator about enabling delivery receipts.

### Configuration Questions

**Q: How do I change the email pattern?**
A: Contact administrator to update email routing rules.

**Q: Can I use my own Twilio account?**
A: Yes, if self-hosting. See [Deployment Guide](DEPLOYMENT_MASTER.md).

**Q: How do I add myself to allowed senders?**
A: Contact administrator to update allowlist.

**Q: Can limits be increased?**
A: Yes, contact administrator to request higher limits.

---

## Getting Help

### Self-Service Resources

1. **Check Logs** (if you have access)
   ```bash
   npm run tail
   ```

2. **Review Error Messages**
   - Check email rejection reasons
   - Note exact error text

3. **Test Different Formats**
   - Try phone in email address
   - Try phone in subject
   - Verify phone format

### Contact Administrator

**Information to Provide:**

1. **Your email address** (sender)
2. **Recipient phone number** (format used)
3. **Email sent time** (approximate)
4. **Error message** (if any)
5. **Email content** (sample)

### Additional Resources

- [Deployment Guide](DEPLOYMENT_MASTER.md) - Setup and configuration
- [Operations Guide](OPERATIONS.md) - Advanced management
- [Troubleshooting Guide](TROUBLESHOOTING.md) - Problem solving
- [API Documentation](API.md) - Technical details

---

## Quick Reference

### Email Format Cheat Sheet

```
FORMAT 1 (Recommended):
To: 15551234567@sms.domain.com
Subject: Your subject
Body: Your message

FORMAT 2 (Alternative):
To: contact@sms.domain.com
Subject: To: 555-123-4567
Body: Your message

FORMAT 3 (Advanced):
To: sms@domain.com
X-SMS-To: +15551234567
Body: Your message
```

### Common Commands

```bash
# Start Streamlit UI
streamlit run app.py

# Generate worker code
# (Use UI, click Generate Code)

# Deploy worker
npm run deploy:production

# View logs
npm run tail
```

### Support Checklist

Before contacting support:
- [ ] Verified phone format
- [ ] Checked sender authorization
- [ ] Reviewed error message
- [ ] Tested with different format
- [ ] Checked rate limits
- [ ] Reviewed documentation

---

**Last Updated:** 2025-11-13
**Version:** 1.0.0
