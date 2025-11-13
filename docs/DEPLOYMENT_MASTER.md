# Email-to-SMS Complete Deployment Guide

**Version:** 1.0.0
**Last Updated:** 2025-11-13

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Architecture Overview](#architecture-overview)
3. [Component 1: Cloudflare Worker](#component-1-cloudflare-worker)
4. [Component 2: Streamlit Code Generator](#component-2-streamlit-code-generator)
5. [Production Deployment](#production-deployment)
6. [Post-Deployment Verification](#post-deployment-verification)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

---

## Prerequisites

### System Requirements

- **Node.js** 18.0.0 or higher
- **Python** 3.8 or higher
- **npm** 9.0.0 or higher
- **pip** 21.0.0 or higher
- **Git** (for version control)

### Required Accounts

#### 1. Cloudflare Account
- Free or paid plan
- Domain managed by Cloudflare DNS
- Email Routing enabled (available on free plan)
- Workers enabled
- Account ID (found in Cloudflare Dashboard)

#### 2. Twilio Account
- Active account with verified phone number
- Account SID (starts with AC...)
- Auth Token (secret)
- Phone number in E.164 format (+1XXXXXXXXXX)
- Sufficient credit balance for SMS

### Pre-Deployment Checklist

```bash
# Verify Node.js version
node --version  # Should be 18+

# Verify Python version
python3 --version  # Should be 3.8+

# Verify npm
npm --version

# Verify pip
pip3 --version

# Clone or navigate to project
cd /home/ruhroh/email2sms
```

---

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                   Email-to-SMS System                    │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────────┐          ┌──────────────────┐      │
│  │  Streamlit UI   │          │ Cloudflare       │      │
│  │  Code Generator │ -------> │ Email Worker     │      │
│  │                 │          │                  │      │
│  │  - Config UI    │          │ - Email Parser   │      │
│  │  - Code Gen     │          │ - Phone Extract  │      │
│  │  - Download     │          │ - SMS Sender     │      │
│  └─────────────────┘          └──────────────────┘      │
│         │                             │                  │
│         │                             │                  │
│         ▼                             ▼                  │
│  ┌─────────────────┐          ┌──────────────────┐      │
│  │  Local Dev      │          │  Twilio API      │      │
│  │  Environment    │          │  SMS Gateway     │      │
│  └─────────────────┘          └──────────────────┘      │
│                                                           │
└─────────────────────────────────────────────────────────┘

Email Flow:
[User Email] → [Cloudflare Email Routing] → [Worker] → [Twilio] → [SMS]
```

### Technology Stack

- **Worker Runtime**: Cloudflare Workers (V8 Isolates)
- **Email Parser**: PostalMime
- **SMS Gateway**: Twilio REST API
- **UI Framework**: Streamlit (Python)
- **Language**: TypeScript (Worker), Python (UI)
- **Storage**: KV Namespace (rate limiting)
- **Analytics**: Cloudflare Analytics Engine

---

## Component 1: Cloudflare Worker

### Step 1: Initial Setup

#### 1.1 Install Dependencies

```bash
cd /home/ruhroh/email2sms
npm install
```

This installs:
- `postal-mime` - Email parsing
- `wrangler` - Cloudflare CLI
- TypeScript and type definitions

#### 1.2 Verify Installation

```bash
# Check wrangler is installed
npx wrangler --version

# Type check the code
npm run typecheck
```

### Step 2: Development Configuration

#### 2.1 Create Development Secrets File

```bash
cp .dev.vars.example .dev.vars
```

#### 2.2 Configure `.dev.vars`

Edit `/home/ruhroh/email2sms/.dev.vars`:

```env
# Twilio Credentials
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+15551234567

# Allowed Senders (comma-separated)
ALLOWED_SENDERS=yourname@example.com,*@trusted.com

# Optional: Default country code (for US numbers)
DEFAULT_COUNTRY_CODE=1
```

**Security Note**: Never commit `.dev.vars` to version control!

#### 2.3 Update `wrangler.toml`

Edit `/home/ruhroh/email2sms/config/wrangler.toml`:

```toml
name = "email-to-sms-worker"
account_id = "your-cloudflare-account-id"  # GET THIS FROM DASHBOARD
compatibility_date = "2024-11-13"
main = "src/worker/index.ts"

[vars]
ALLOWED_SENDERS = "your@email.com,*@yourdomain.com"
DEFAULT_COUNTRY_CODE = "1"
```

**Finding your Account ID:**
1. Log in to Cloudflare Dashboard
2. Click any domain
3. Scroll down right sidebar
4. Copy "Account ID"

### Step 3: Local Development

#### 3.1 Start Development Server

```bash
npm run dev
```

Output should show:
```
⛅️ wrangler 3.x.x
-------------------
⎔ Starting local server...
[wrangler:inf] Ready on http://localhost:8787
```

#### 3.2 Test Email Processing Locally

The worker runs locally but email routing can't be tested until deployed. You can:

1. Review logs in terminal
2. Test TypeScript compilation
3. Verify configuration loads

**Press Ctrl+C to stop the server**

### Step 4: Production Secrets Setup

#### 4.1 Set Twilio Credentials as Secrets

```bash
# Set Account SID
npx wrangler secret put TWILIO_ACCOUNT_SID
# When prompted, paste: ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Set Auth Token
npx wrangler secret put TWILIO_AUTH_TOKEN
# When prompted, paste: your-auth-token

# Set Phone Number
npx wrangler secret put TWILIO_PHONE_NUMBER
# When prompted, paste: +15551234567
```

#### 4.2 Verify Secrets

```bash
npx wrangler secret list
```

Expected output:
```
TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN
TWILIO_PHONE_NUMBER
```

### Step 5: KV Namespace Setup (Optional but Recommended)

#### 5.1 Create KV Namespace

```bash
npm run kv:create
```

Output:
```
🌀 Creating namespace with title "email-to-sms-worker-EMAIL_SMS_KV"
✨ Success!
Add the following to your wrangler.toml:
{ binding = "EMAIL_SMS_KV", id = "abc123..." }
```

#### 5.2 Add to `wrangler.toml`

Edit `/home/ruhroh/email2sms/config/wrangler.toml`:

```toml
[[kv_namespaces]]
binding = "EMAIL_SMS_KV"
id = "abc123..."  # Use the ID from previous step
```

**Why KV Namespace?**
- Enables rate limiting
- Stores audit logs
- Prevents SMS spam
- Tracks usage statistics

### Step 6: Deploy to Production

#### 6.1 Deploy Worker

```bash
npm run deploy:production
```

Expected output:
```
Uploaded email-to-sms-worker
Published email-to-sms-worker
  https://email-to-sms-worker.your-account.workers.dev
```

#### 6.2 Verify Deployment

```bash
npx wrangler deployments list
```

### Step 7: Configure Email Routing

#### 7.1 Enable Email Routing

1. Go to Cloudflare Dashboard
2. Select your domain
3. Click **Email Routing** in left sidebar
4. Click **Enable Email Routing**
5. Wait for MX records to be configured (automatic)

#### 7.2 Create Email Route

1. Go to **Email Routing** > **Routing Rules**
2. Click **Create Route**
3. Configure route:
   - **Catch-all or custom**: Custom address
   - **Expression**: `*@sms.yourdomain.com`
   - **Action**: Send to Worker
   - **Worker**: `email-to-sms-worker`
4. Click **Save**

#### 7.3 Verify MX Records

```bash
dig MX yourdomain.com
```

Should show Cloudflare MX records:
```
yourdomain.com.  300  IN  MX  1  isaac.mx.cloudflare.net.
yourdomain.com.  300  IN  MX  2  linda.mx.cloudflare.net.
```

### Step 8: Test Worker

#### 8.1 Send Test Email

```
To: 15551234567@sms.yourdomain.com
Subject: Test Message
Body: This is a test SMS from Email Routing
```

#### 8.2 Monitor Logs

```bash
npm run tail
```

Look for success message:
```json
{
  "timestamp": "2025-11-13T...",
  "level": "info",
  "message": "Email-to-SMS conversion successful",
  "twilioSid": "SM..."
}
```

#### 8.3 Verify SMS Delivery

Check phone +15551234567 for message:
```
From: Your Name
Re: Test Message
This is a test SMS from Email Routing
```

### Step 9: Production Monitoring

#### 9.1 View Live Logs

```bash
npm run tail
```

#### 9.2 Check Analytics

1. Go to Cloudflare Dashboard
2. Workers & Pages > email-to-sms-worker
3. Click **Metrics** tab
4. View:
   - Request count
   - Success rate
   - Error distribution
   - Processing time

#### 9.3 Check Email Routing Status

1. Email Routing > Overview
2. View processed emails
3. Check success/failure rates

---

## Component 2: Streamlit Code Generator

### Step 1: Environment Setup

#### 1.1 Navigate to Streamlit App

```bash
cd /home/ruhroh/email2sms/streamlit-app
```

#### 1.2 Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows
```

#### 1.3 Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `streamlit` - Web framework
- `pyyaml` - Configuration parsing
- `jinja2` - Template rendering

#### 1.4 Verify Installation

```bash
streamlit --version
```

### Step 2: Local Development

#### 2.1 Start Streamlit App

```bash
streamlit run app.py
```

Expected output:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.x:8501
```

#### 2.2 Access Application

Open browser to: `http://localhost:8501`

### Step 3: Generate Worker Code

#### 3.1 Configure Basic Settings

In Streamlit UI:

1. **Worker Configuration**
   - Worker Name: `my-email-sms`
   - Domain: `yourdomain.com`
   - Email Pattern: `*@sms.yourdomain.com`

2. **Twilio Settings**
   - Phone Number: `+15551234567`
   - Account SID: (leave blank for template)
   - Auth Token: (leave blank for template)

3. **Security**
   - Allowed Senders: `user@example.com,*@trusted.com`
   - Enable Rate Limiting: ✓ Yes

4. **Features**
   - Enable Logging: ✓ Yes
   - Enable Analytics: ✓ Yes
   - Enable Retry Logic: ✓ Yes

#### 3.2 Generate Code

1. Click **🚀 Generate Code** button
2. Wait for generation (1-2 seconds)
3. See success message: "✅ Successfully generated X files!"

#### 3.3 Review Generated Code

Browse tabs:
- `worker/index.ts` - Main worker
- `services/twilio-service.ts` - Twilio integration
- `utils/phone-parser.ts` - Phone extraction
- `package.json` - Dependencies
- `wrangler.toml` - Configuration

#### 3.4 Download Files

Click **📦 Download All Files (ZIP)**

This downloads: `email-to-sms-worker.zip`

### Step 4: Deploy Generated Code

#### 4.1 Extract ZIP

```bash
cd ~/Downloads
unzip email-to-sms-worker.zip -d my-email-sms-worker
cd my-email-sms-worker
```

#### 4.2 Install and Deploy

```bash
# Install dependencies
npm install

# Create .dev.vars from template
cp .dev.vars.example .dev.vars
# Edit .dev.vars with your credentials

# Test locally
npm run dev

# Deploy to production
npm run deploy:production
```

### Step 5: Production Deployment (Streamlit)

#### 5.1 Choose Deployment Option

**Option A: Streamlit Cloud (Recommended)**

1. Push code to GitHub repository
2. Go to https://share.streamlit.io
3. Click **New app**
4. Select repository and branch
5. Set main file: `streamlit-app/app.py`
6. Click **Deploy**

**Option B: Self-Hosted**

```bash
# Install streamlit globally
pip install streamlit

# Run on server
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

**Option C: Docker**

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY streamlit-app/requirements.txt .
RUN pip install -r requirements.txt

COPY streamlit-app/ .

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:
```bash
docker build -t email2sms-ui .
docker run -p 8501:8501 email2sms-ui
```

---

## Production Deployment

### Environment Configuration

#### Development Environment

- **Worker**: `npm run dev` (localhost:8787)
- **Streamlit**: `streamlit run app.py` (localhost:8501)
- **Secrets**: `.dev.vars` file
- **Email**: Cannot test routing locally

#### Staging Environment

```bash
# Deploy worker to staging
npm run deploy:staging

# Configure staging secrets
npx wrangler secret put TWILIO_ACCOUNT_SID --env staging
```

#### Production Environment

```bash
# Deploy worker
npm run deploy:production

# Monitor
npm run tail
```

### Security Hardening

#### 1. Rotate Secrets Regularly

```bash
# Every 90 days, rotate Twilio token
npx wrangler secret put TWILIO_AUTH_TOKEN
```

#### 2. Configure Strict Sender List

```toml
[vars]
ALLOWED_SENDERS = "admin@yourdomain.com,support@yourdomain.com"
```

#### 3. Enable Rate Limiting

Ensure KV namespace is configured to prevent abuse.

#### 4. Monitor for Anomalies

```bash
# Watch logs for suspicious patterns
npm run tail | grep -i "unauthorized\|rate limit\|error"
```

### Backup and Recovery

#### Backup Configuration

```bash
# Backup wrangler.toml
cp config/wrangler.toml config/wrangler.toml.backup

# Backup KV data (if needed)
npx wrangler kv:key list --binding EMAIL_SMS_KV > kv-backup.json
```

#### Rollback Deployment

```bash
# List deployments
npx wrangler deployments list

# Rollback to previous
npx wrangler rollback
```

---

## Post-Deployment Verification

### Verification Checklist

#### Worker Verification

- [ ] Worker deployed successfully
- [ ] Secrets configured (check `wrangler secret list`)
- [ ] KV namespace created and bound
- [ ] Email routing enabled
- [ ] Route configured to worker
- [ ] MX records active

#### Functional Testing

- [ ] Send test email (phone in address)
- [ ] Send test email (phone in subject)
- [ ] Verify SMS received
- [ ] Check logs show success
- [ ] Test rate limiting (send 11 messages)
- [ ] Test unauthorized sender (should reject)
- [ ] Test invalid phone format (should reject)

#### Performance Testing

```bash
# Monitor processing time
npm run tail | grep "processingTime"

# Verify < 500ms average
```

#### Security Testing

- [ ] Unauthorized sender rejected
- [ ] Rate limits enforced
- [ ] Invalid phone numbers rejected
- [ ] No secrets in logs
- [ ] Analytics data clean

---

## Troubleshooting

### Common Issues

#### Issue: Email Not Processing

**Symptoms:**
- Email sent but no SMS received
- No log entries in `npm run tail`

**Solutions:**

1. **Check Email Routing Status**
   ```bash
   # Verify MX records
   dig MX yourdomain.com

   # Should show Cloudflare MX
   ```

2. **Verify Route Configuration**
   - Dashboard > Email Routing > Routes
   - Ensure pattern matches email sent
   - Verify worker selected

3. **Check Worker Logs**
   ```bash
   npm run tail
   # Look for any error messages
   ```

4. **Verify Worker is Deployed**
   ```bash
   npx wrangler deployments list
   # Should show recent deployment
   ```

#### Issue: SMS Not Sending

**Symptoms:**
- Worker receives email
- Logs show processing
- No SMS delivered

**Solutions:**

1. **Check Twilio Credentials**
   ```bash
   # Verify secrets exist
   npx wrangler secret list

   # Should show all 3 Twilio secrets
   ```

2. **Verify Twilio Account**
   - Log in to Twilio Console
   - Check account balance
   - Verify phone number is active
   - Check Twilio logs for errors

3. **Check Phone Number Format**
   - Must be E.164: +1XXXXXXXXXX
   - 10 digits for US numbers
   - Valid area code (not 000, 555)

4. **Review Worker Logs**
   ```bash
   npm run tail | grep -i "twilio\|error"
   # Look for Twilio API errors
   ```

#### Issue: Rate Limiting Not Working

**Symptoms:**
- Can send unlimited messages
- No rate limit rejections

**Solutions:**

1. **Verify KV Namespace**
   ```bash
   # Check namespace exists
   npx wrangler kv:namespace list
   ```

2. **Check wrangler.toml**
   ```toml
   # Should have KV binding
   [[kv_namespaces]]
   binding = "EMAIL_SMS_KV"
   id = "your-namespace-id"
   ```

3. **Redeploy Worker**
   ```bash
   npm run deploy:production
   ```

#### Issue: Phone Number Not Extracted

**Symptoms:**
- Error: "Could not extract phone number"
- Valid phone in email

**Solutions:**

1. **Try Different Format**
   - Format 1: `15551234567@sms.domain.com`
   - Format 2: Subject: `To: 555-123-4567`
   - Format 3: Header: `X-SMS-To: +15551234567`

2. **Check Phone Format**
   - Remove spaces: `5551234567` not `555 123 4567`
   - Remove dashes: `5551234567` not `555-123-4567`
   - Use 10 digits for US

3. **Review Logs**
   ```bash
   npm run tail | grep "phone"
   # See extraction attempts
   ```

#### Issue: Streamlit App Not Starting

**Symptoms:**
- `streamlit run app.py` fails
- Import errors

**Solutions:**

1. **Check Python Version**
   ```bash
   python3 --version  # Must be 3.8+
   ```

2. **Reinstall Dependencies**
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

3. **Check Virtual Environment**
   ```bash
   # Activate venv
   source venv/bin/activate

   # Verify streamlit installed
   which streamlit
   ```

4. **Check Port Availability**
   ```bash
   # If port 8501 in use
   streamlit run app.py --server.port 8502
   ```

---

## Best Practices

### Development Workflow

1. **Local Development First**
   ```bash
   # Always test locally before deploying
   npm run dev
   ```

2. **Use Staging Environment**
   ```bash
   # Test in staging before production
   npm run deploy:staging
   ```

3. **Monitor After Deployment**
   ```bash
   # Watch logs for 5 minutes after deploy
   npm run tail
   ```

### Security Best Practices

1. **Never Commit Secrets**
   - Add `.dev.vars` to `.gitignore`
   - Use `wrangler secret put` for production
   - Rotate secrets every 90 days

2. **Configure Sender Allowlist**
   ```toml
   # Strict: Specific users
   ALLOWED_SENDERS = "alice@corp.com,bob@corp.com"

   # Domain: Entire domain
   ALLOWED_SENDERS = "*@corp.com"
   ```

3. **Enable Rate Limiting**
   - Always use KV namespace in production
   - Monitor rate limit hits
   - Adjust limits based on usage

4. **Regular Security Audits**
   ```bash
   # Review logs weekly
   npm run tail | grep -i "unauthorized\|suspicious"
   ```

### Performance Optimization

1. **Monitor Processing Time**
   ```bash
   # Target: < 500ms per email
   npm run tail | grep "processingTime"
   ```

2. **Optimize Content Processing**
   - Keep email content under 1600 chars
   - Use plain text when possible
   - Remove unnecessary signatures

3. **Cache Configuration**
   - Worker caches environment variables
   - No need to optimize config access

### Cost Optimization

1. **Cloudflare Costs**
   - Workers: Free tier = 100k requests/day
   - Email Routing: Free tier = 1k emails/day
   - KV: Free tier = 100k reads/day
   - **Recommendation**: Start with free tier

2. **Twilio Costs**
   - SMS: ~$0.0075 per message (US)
   - Phone: ~$1/month
   - **Tip**: Monitor usage in Twilio Console

3. **Reduce Costs**
   - Use rate limiting to prevent abuse
   - Configure strict sender allowlist
   - Monitor for spam patterns

### Monitoring Strategy

1. **Real-Time Monitoring**
   ```bash
   # Keep terminal open with logs
   npm run tail
   ```

2. **Daily Checks**
   - Cloudflare Analytics Dashboard
   - Twilio usage statistics
   - Error rate trends

3. **Weekly Reviews**
   - Review sender patterns
   - Check for unauthorized attempts
   - Analyze cost trends
   - Review rate limit effectiveness

### Maintenance Schedule

**Daily:**
- Check error logs
- Verify SMS delivery rate

**Weekly:**
- Review analytics
- Check cost trends
- Update documentation

**Monthly:**
- Update dependencies
- Review security logs
- Optimize rate limits

**Quarterly:**
- Rotate Twilio credentials
- Review sender allowlist
- Performance tuning
- Security audit

---

## Summary

### Quick Deployment Commands

```bash
# Worker Deployment
cd /home/ruhroh/email2sms
npm install
cp .dev.vars.example .dev.vars  # Edit with your credentials
npm run dev  # Test locally
npx wrangler secret put TWILIO_ACCOUNT_SID
npx wrangler secret put TWILIO_AUTH_TOKEN
npx wrangler secret put TWILIO_PHONE_NUMBER
npm run kv:create  # Note the ID
# Edit config/wrangler.toml with KV ID
npm run deploy:production

# Streamlit Deployment
cd streamlit-app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

### Success Indicators

✅ Worker deployed and accessible
✅ Secrets configured
✅ Email routing active
✅ Test email → SMS successful
✅ Logs show processing
✅ Rate limiting active
✅ No errors in dashboard

### Next Steps

1. Send test emails with different formats
2. Monitor logs for 24 hours
3. Adjust rate limits based on usage
4. Configure alerts for errors
5. Document your specific use cases

---

**Need Help?**
- Review [Troubleshooting Guide](TROUBLESHOOTING.md)
- Check [User Guide](USER_GUIDE.md)
- See [Operations Guide](OPERATIONS.md)
