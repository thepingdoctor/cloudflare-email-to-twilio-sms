# Email-to-SMS Troubleshooting Guide

**Version:** 1.0.0
**Last Updated:** 2025-11-13

## Table of Contents

1. [Quick Diagnostic](#quick-diagnostic)
2. [Common Errors](#common-errors)
3. [Email Issues](#email-issues)
4. [SMS Delivery Issues](#sms-delivery-issues)
5. [Worker Issues](#worker-issues)
6. [Streamlit UI Issues](#streamlit-ui-issues)
7. [Performance Issues](#performance-issues)
8. [Debug Procedures](#debug-procedures)
9. [FAQ](#faq)

---

## Quick Diagnostic

### System Health Check

Run these commands to check overall system health:

```bash
# 1. Check worker deployment
npx wrangler deployments list

# 2. View recent logs
npm run tail --format json | head -5

# 3. Verify secrets
npx wrangler secret list

# 4. Check KV namespace
npx wrangler kv:namespace list

# 5. Test connectivity
curl -I https://api.twilio.com
```

### Decision Tree

```
Email sent but no SMS received?
├─ Check Email Routing [Section: Email Issues]
├─ Check Phone Format [Section: Common Errors]
├─ Check Sender Authorization [Section: Common Errors]
└─ Check Twilio Account [Section: SMS Delivery Issues]

Worker not processing emails?
├─ Check Deployment [Section: Worker Issues]
├─ Check Logs [Section: Debug Procedures]
└─ Check Email Route [Section: Email Issues]

Streamlit UI not working?
├─ Check Python/Dependencies [Section: Streamlit UI Issues]
├─ Check Port [Section: Streamlit UI Issues]
└─ Check File Permissions [Section: Streamlit UI Issues]

Slow performance?
└─ See Performance Issues section
```

---

## Common Errors

### Error: Unauthorized Sender

**Error Message:**
```
Email rejected: Sender not authorized to use this service
```

**Cause:**
Sender email address not in `ALLOWED_SENDERS` configuration

**Solutions:**

1. **Check Your Email**
   ```bash
   # View current allowlist
   grep ALLOWED_SENDERS config/wrangler.toml
   ```

2. **Add Your Email**
   ```toml
   # Edit config/wrangler.toml
   [vars]
   ALLOWED_SENDERS = "existing@example.com,yourname@example.com"
   ```

3. **Redeploy**
   ```bash
   npm run deploy:production
   ```

4. **Verify**
   ```bash
   # Send test email
   echo "Test" | mail -s "Test" phone@sms.domain.com

   # Check logs
   npm run tail | grep "authorized"
   ```

**Prevention:**
- Use domain wildcards: `*@company.com`
- Document authorized users
- Set up self-service process

---

### Error: Invalid Phone Format

**Error Message:**
```
Email rejected: Invalid phone number format
Could not extract valid phone number from email
```

**Cause:**
Phone number not recognized or invalid format

**Solutions:**

1. **Use E.164 Format**
   ```
   Correct: +15551234567
   Incorrect: 555-123-4567 (without country code)
   ```

2. **Try Different Format**
   ```
   Format 1 (Recommended):
   To: 15551234567@sms.domain.com

   Format 2:
   To: contact@sms.domain.com
   Subject: To: 555-123-4567

   Format 3:
   To: sms@sms.domain.com
   X-SMS-To: +15551234567
   ```

3. **Check Phone Number**
   ```bash
   # Valid US format:
   - 10 digits: 5551234567
   - With country code: +15551234567
   - Formatted: 555-123-4567

   # Invalid:
   - Too short: 1234567
   - Letters: 555-HELP
   - Invalid area code: 000, 555, 911
   ```

**Testing:**
```bash
# Test phone extraction
npm run dev

# Send test with different formats
echo "Test" | mail -s "Test" 5551234567@sms.domain.com
echo "Test" | mail -s "To: 555-123-4567" contact@sms.domain.com
```

---

### Error: Rate Limit Exceeded

**Error Message:**
```
Rate limit exceeded: Maximum 10 messages per hour from this sender
Limit resets at: 2025-11-13 15:30:00 UTC
```

**Cause:**
Too many messages sent within time window

**Solutions:**

1. **Wait for Reset**
   ```
   Check error message for reset time
   Wait until specified time
   Try sending again
   ```

2. **Check Current Limit**
   ```bash
   # View rate limit counter
   npx wrangler kv:key get "rate:sender:your@email.com" \
     --binding EMAIL_SMS_KV

   # Output: {"count":10,"resetAt":1731499200000}
   ```

3. **Request Limit Increase**
   ```
   Contact administrator:
   - Current limit: 10/hour
   - Requested: 20/hour
   - Justification: [explain use case]
   ```

4. **Emergency Override** (Admin Only)
   ```bash
   # Delete rate limit counter
   npx wrangler kv:key delete "rate:sender:your@email.com" \
     --binding EMAIL_SMS_KV
   ```

**Prevention:**
- Monitor sending patterns
- Implement batching
- Use message deduplication
- Set up alerts

---

### Error: Empty Email Content

**Error Message:**
```
Email rejected: Email content is empty
```

**Cause:**
Email body has no content

**Solutions:**

1. **Add Message Body**
   ```
   ❌ Subject: Test
      Body: [empty]

   ✅ Subject: Test
      Body: This is a test message
   ```

2. **Check Email Client**
   - Verify body text is entered
   - Check for HTML-only emails (should auto-convert)
   - Ensure signature isn't the only content

3. **Minimum Length**
   ```
   Minimum: 3 characters
   Recommended: 10+ characters
   ```

---

### Error: Message Too Long

**Error Message:**
```
Email rejected: Message content exceeds maximum SMS length (1600 characters)
```

**Cause:**
Email body too long for SMS

**Solutions:**

1. **Shorten Message**
   ```
   Current: 2000 characters
   Maximum: 1600 characters (10 segments)
   Recommended: 160 characters (1 segment)
   ```

2. **Auto-Truncation**
   ```toml
   # Enable in configuration
   [features]
   auto_truncate = true
   ```

3. **Use Summary**
   ```
   Instead of full email:
   "Alert: Server CPU high. Check dashboard for details."
   ```

---

## Email Issues

### Email Not Arriving at Worker

**Symptoms:**
- Email sent successfully
- No worker logs
- No SMS received

**Debug Steps:**

1. **Check Email Routing Status**
   ```
   Cloudflare Dashboard:
   1. Select domain
   2. Email Routing
   3. Check "Status: Active"
   ```

2. **Verify MX Records**
   ```bash
   dig MX yourdomain.com

   # Should show Cloudflare MX:
   # isaac.mx.cloudflare.net
   # linda.mx.cloudflare.net
   # amir.mx.cloudflare.net
   ```

3. **Check Email Route**
   ```
   Dashboard > Email Routing > Routes
   - Pattern: *@sms.yourdomain.com
   - Action: Send to Worker
   - Worker: email-to-sms-worker ✓ Selected
   ```

4. **Test Email Delivery**
   ```
   Send to: test@sms.yourdomain.com
   Check: Dashboard > Email Routing > Metrics
   ```

**Common Fixes:**

| Issue | Fix |
|-------|-----|
| MX records not updated | Wait 24-48 hours for DNS propagation |
| Route not configured | Add route in Email Routing dashboard |
| Worker not selected | Update route to point to worker |
| Email Routing disabled | Enable in dashboard |

---

### Email Rejected by Cloudflare

**Symptoms:**
- Bounce-back email received
- Error: "550 Invalid recipient"

**Causes:**
1. Email Routing not enabled
2. Route pattern doesn't match
3. Domain not verified

**Solutions:**

1. **Enable Email Routing**
   ```
   Dashboard > Email Routing > Enable
   Wait for MX record setup (automatic)
   ```

2. **Fix Route Pattern**
   ```
   Sent to: anything@sms.domain.com
   Pattern: *@sms.domain.com ✓ Matches

   Sent to: test@email.domain.com
   Pattern: *@sms.domain.com ✗ No match
   ```

3. **Verify Domain**
   ```
   Dashboard > Domain > DNS
   Check: MX records active
   ```

---

### Email Processed But Rejected

**Symptoms:**
- Worker logs show processing
- Email rejected with reason

**Check Logs:**
```bash
npm run tail | grep "rejected"

# Common rejection reasons:
# - Unauthorized sender
# - Invalid phone format
# - Rate limit exceeded
# - Empty content
```

**See:** Specific error sections above

---

## SMS Delivery Issues

### SMS Not Sending (Twilio Errors)

**Symptoms:**
- Worker processes email
- Logs show Twilio error
- No SMS delivered

**Error Codes:**

#### 401 Unauthorized

**Cause:** Invalid Twilio credentials

**Fix:**
```bash
# Update credentials
npx wrangler secret put TWILIO_AUTH_TOKEN
# Enter correct token from Twilio Console

# Redeploy
npm run deploy:production

# Test
npm run tail | grep "twilio"
```

#### 21211 Invalid Phone Number

**Cause:** Phone number format invalid

**Fix:**
```
Use E.164 format: +15551234567

Check:
- Country code present (+1)
- Correct digit count (12 for US)
- No invalid area codes (000, 555, 911)
```

#### 21408 Permission Denied

**Cause:** Twilio number not authorized for SMS

**Fix:**
```
Twilio Console:
1. Phone Numbers > Manage Numbers
2. Select your number
3. Verify SMS capability enabled
4. Check number status (active)
```

#### 20003 Authentication Error

**Cause:** Account SID or Auth Token incorrect

**Fix:**
```bash
# Verify secrets
npx wrangler secret list

# Update Account SID
npx wrangler secret put TWILIO_ACCOUNT_SID

# Update Auth Token
npx wrangler secret put TWILIO_AUTH_TOKEN
```

#### 21610 Unverified Number (Trial Account)

**Cause:** Sending to non-verified number on trial account

**Fix:**
```
Option 1: Verify recipient in Twilio Console
Option 2: Upgrade to paid account
```

---

### SMS Delayed

**Symptoms:**
- Email processed quickly
- SMS arrives 30+ seconds later

**Causes:**
1. Carrier delays (normal)
2. Network congestion
3. International delivery

**Expected Delays:**
- US to US: 1-5 seconds
- International: 5-30 seconds
- Network issues: up to 60 seconds

**Monitoring:**
```bash
# Check Twilio status
curl https://status.twilio.com/api/v2/status.json

# Check processing time
npm run tail | grep "processingTime"
# Should be <500ms
```

**If Delayed >2 minutes:**
1. Check Twilio Console for message status
2. Contact Twilio Support
3. Verify carrier isn't blocking

---

### SMS Content Garbled

**Symptoms:**
- SMS received
- Content incorrect or truncated

**Issues:**

#### 1. Encoding Problems

**Cause:** Unicode characters

**Fix:**
```
Use standard ASCII characters
Avoid: emoji, special symbols
Prefer: plain text
```

#### 2. Truncation Issues

**Cause:** Message too long

**Fix:**
```
Keep under 160 characters
Check actual SMS received:
- May be split into multiple messages
- May be truncated at word boundary
```

#### 3. HTML Not Stripped

**Cause:** HTML conversion failed

**Debug:**
```bash
npm run tail | grep "content"

# Check if HTML tags present in output
```

**Fix:**
- Update content processor
- Use plain text emails

---

## Worker Issues

### Worker Not Deployed

**Symptoms:**
- Deployment fails
- Worker unavailable

**Check Deployment:**
```bash
npx wrangler deployments list

# If no deployments:
# - Never deployed
# - Deployment failed
```

**Common Errors:**

#### Syntax Error

```
Error: Failed to publish worker
SyntaxError: Unexpected token
```

**Fix:**
```bash
# Type check
npm run typecheck

# Fix syntax errors
# Redeploy
npm run deploy:production
```

#### Missing Dependencies

```
Error: Could not resolve "postal-mime"
```

**Fix:**
```bash
# Reinstall
npm install

# Verify package.json
cat package.json | grep postal-mime

# Redeploy
npm run deploy:production
```

#### Invalid Configuration

```
Error: wrangler.toml parse error
```

**Fix:**
```bash
# Validate TOML syntax
npx wrangler whoami

# Fix wrangler.toml
# Common issues:
# - Missing quotes
# - Invalid syntax
# - Wrong types
```

---

### Worker Timeout

**Symptoms:**
- Emails processed slowly
- Timeout errors in logs

**Causes:**
1. Twilio API slow
2. External network issues
3. Heavy processing

**Solutions:**

1. **Check Processing Time**
   ```bash
   npm run tail | grep "processingTimeMs"

   # Acceptable: <500ms
   # Warning: 500-1000ms
   # Critical: >1000ms
   ```

2. **Reduce Timeout**
   ```typescript
   // In twilio-service.ts
   const timeout = 5000; // 5s instead of 10s
   ```

3. **Monitor Twilio Status**
   ```bash
   curl https://status.twilio.com/api/v2/status.json
   ```

---

### Worker Crashes

**Symptoms:**
- Random failures
- Uncaught exceptions
- Inconsistent behavior

**Debug:**
```bash
# View error logs
npm run tail | grep -i "error\|exception"

# Check for:
# - Null pointer errors
# - Type errors
# - API failures
```

**Common Fixes:**

#### Null Reference Error

```typescript
// ❌ Unsafe
const phone = email.to.address;

// ✅ Safe
const phone = email?.to?.address ?? '';
```

#### Unhandled Promise Rejection

```typescript
// ❌ No error handling
await sendSMS(phone, message);

// ✅ With error handling
try {
  await sendSMS(phone, message);
} catch (error) {
  console.error('SMS failed:', error);
  throw error;
}
```

---

## Streamlit UI Issues

### UI Won't Start

**Error:**
```
streamlit: command not found
```

**Solutions:**

1. **Check Virtual Environment**
   ```bash
   # Activate venv
   cd streamlit-app
   source venv/bin/activate  # Linux/Mac
   # OR
   venv\Scripts\activate  # Windows

   # Verify streamlit
   which streamlit
   ```

2. **Reinstall Dependencies**
   ```bash
   pip install -r requirements.txt
   streamlit --version
   ```

3. **Python Version**
   ```bash
   python3 --version  # Must be 3.8+

   # If old version, upgrade Python
   ```

---

### Import Errors

**Error:**
```
ModuleNotFoundError: No module named 'streamlit'
```

**Fix:**
```bash
# Ensure venv activated
source venv/bin/activate

# Install requirements
pip install -r requirements.txt --force-reinstall

# Verify modules
pip list | grep streamlit
```

---

### Port Already in Use

**Error:**
```
OSError: Address already in use
```

**Solutions:**

1. **Use Different Port**
   ```bash
   streamlit run app.py --server.port 8502
   ```

2. **Kill Existing Process**
   ```bash
   # Find process
   lsof -i :8501

   # Kill process
   kill -9 [PID]

   # Restart
   streamlit run app.py
   ```

---

### Code Generation Fails

**Error:**
```
Error generating code: [error message]
```

**Debug:**
```bash
# Check logs in terminal
# Look for Python errors

# Common issues:
# - Missing template files
# - Invalid configuration
# - File permission errors
```

**Fix:**
```bash
# Verify templates exist
ls -la templates/

# Check permissions
chmod +r templates/*.j2

# Restart Streamlit
streamlit run app.py
```

---

## Performance Issues

### Slow Email Processing

**Symptoms:**
- Processing time >1 second
- Delays in SMS delivery

**Measure:**
```bash
npm run tail | grep "processingTimeMs" | \
  awk '{sum+=$NF; count++} END {print "Avg:", sum/count, "ms"}'
```

**Optimization:**

1. **Check Twilio API**
   ```bash
   # Test API speed
   curl -w "%{time_total}\n" -o /dev/null -s \
     https://api.twilio.com/2010-04-01/Accounts.json

   # Should be <200ms
   ```

2. **Reduce Content Processing**
   ```typescript
   // Limit content length early
   if (content.length > 2000) {
     content = content.substring(0, 2000);
   }
   ```

3. **Cache Phone Patterns**
   ```typescript
   // Pre-compile regex patterns
   const PHONE_PATTERNS = [/*...*/].map(p => new RegExp(p));
   ```

---

### High Memory Usage

**Symptoms:**
- Worker crashes
- Out of memory errors

**Check:**
```
Dashboard > Workers > Metrics > Memory
```

**Solutions:**

1. **Stream Large Emails**
   ```typescript
   // PostalMime already streams
   // No action needed for emails <25MB
   ```

2. **Limit Content Size**
   ```typescript
   const MAX_CONTENT = 10000; // 10KB
   if (content.length > MAX_CONTENT) {
     content = content.substring(0, MAX_CONTENT);
   }
   ```

---

### Rate Limiting Too Aggressive

**Symptoms:**
- Legitimate emails rejected
- Frequent rate limit errors

**Check Current Limits:**
```toml
# config/wrangler.toml
[vars]
RATE_LIMIT_PER_SENDER = "10"
RATE_LIMIT_PER_RECIPIENT = "20"
RATE_LIMIT_GLOBAL = "1000"
```

**Adjust:**
```toml
# Increase limits
[vars]
RATE_LIMIT_PER_SENDER = "20"   # 10 → 20
RATE_LIMIT_PER_RECIPIENT = "50"  # 20 → 50
RATE_LIMIT_GLOBAL = "2000"      # 1000 → 2000
```

**Redeploy:**
```bash
npm run deploy:production
```

---

## Debug Procedures

### Enable Debug Logging

**Temporary Debug Mode:**

```typescript
// Add to worker/index.ts
const DEBUG = true;

function log(message: string, data?: any) {
  if (DEBUG) {
    console.log(`[DEBUG] ${message}`, data);
  }
}

// Use throughout code
log('Email received', { from: email.from });
log('Phone extracted', { phone, source });
log('SMS sent', { sid });
```

**Redeploy:**
```bash
npm run deploy:staging  # Test in staging first
```

---

### Trace Email Flow

**Step-by-Step:**

1. **Send Test Email**
   ```bash
   echo "Debug test" | mail -s "Debug" 5551234567@sms.domain.com
   ```

2. **Watch Logs**
   ```bash
   npm run tail
   ```

3. **Expected Flow:**
   ```
   [INFO] Email received from: user@example.com
   [DEBUG] Parsing email...
   [DEBUG] Phone extracted: +15551234567 (source: email_address)
   [DEBUG] Content processed: 65 chars
   [DEBUG] Sending SMS via Twilio...
   [INFO] SMS sent successfully, SID: SM...
   ```

4. **If Missing Step:**
   - Email not received → Check Email Routing
   - Phone not extracted → Check phone format
   - SMS not sent → Check Twilio logs

---

### Test Twilio Independently

**Direct API Test:**

```bash
curl -X POST "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID/Messages.json" \
  --data-urlencode "To=+15551234567" \
  --data-urlencode "From=$TWILIO_PHONE_NUMBER" \
  --data-urlencode "Body=Test message" \
  -u "$TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN"
```

**Expected Response:**
```json
{
  "sid": "SM...",
  "status": "queued",
  "to": "+15551234567",
  "from": "+15559876543"
}
```

**If Fails:**
- Verify credentials
- Check phone numbers
- Review Twilio account status

---

### Validate Configuration

**Check All Settings:**

```bash
# 1. Wrangler config
cat config/wrangler.toml

# 2. Secrets
npx wrangler secret list

# 3. KV namespaces
npx wrangler kv:namespace list

# 4. Routes
# Dashboard > Email Routing > Routes

# 5. DNS
dig MX yourdomain.com
```

---

## FAQ

### General Troubleshooting

**Q: How do I know if the worker is running?**

```bash
# Check deployment status
npx wrangler deployments list

# Should show recent deployment
# If none, redeploy:
npm run deploy:production
```

**Q: Where are error logs stored?**

```
- Console: npm run tail (7 days)
- KV: Auto-stored for errors (30 days)
- Analytics: Dashboard (90 days)
```

**Q: Can I test without sending real SMS?**

```bash
# Option 1: Use development mode
npm run dev
# SMS calls will show in logs but not send

# Option 2: Use Twilio test credentials
# See Twilio docs for test SIDs
```

**Q: How do I reset rate limits?**

```bash
# Delete specific sender
npx wrangler kv:key delete "rate:sender:user@example.com" \
  --binding EMAIL_SMS_KV

# Or wait for automatic reset (1 hour)
```

### Advanced Debugging

**Q: How do I capture network requests?**

```typescript
// Add logging to twilio-service.ts
async function sendSMS(to: string, body: string) {
  console.log('Twilio request:', { to, from, bodyLength: body.length });

  const response = await fetch(TWILIO_API, {/*...*/});

  console.log('Twilio response:', {
    status: response.status,
    headers: Object.fromEntries(response.headers)
  });
}
```

**Q: How do I test rate limiting?**

```bash
# Send 11 emails quickly
for i in {1..11}; do
  echo "Test $i" | mail -s "Test" phone@sms.domain.com
done

# 11th should be rejected
# Check logs for rate limit message
```

**Q: How do I simulate failures?**

```typescript
// Add to worker for testing
if (Math.random() < 0.1) {
  throw new Error('Simulated failure');
}
```

---

## Getting Additional Help

### Before Contacting Support

1. **Gather Information:**
   - Error messages (exact text)
   - Recent logs (last 10 entries)
   - Email sent time
   - Expected vs actual behavior

2. **Attempt Basic Fixes:**
   - Restart worker (redeploy)
   - Check credentials
   - Verify configuration
   - Test with different format

3. **Document Steps:**
   - What you tried
   - What happened
   - What you expected

### Support Channels

1. **Documentation**
   - [Deployment Guide](DEPLOYMENT_MASTER.md)
   - [User Guide](USER_GUIDE.md)
   - [Operations Guide](OPERATIONS.md)

2. **Logs and Monitoring**
   ```bash
   npm run tail | tee debug.log
   # Send debug.log to support
   ```

3. **External Resources**
   - Cloudflare Workers Docs
   - Twilio Support
   - PostalMime Issues

---

**Last Updated:** 2025-11-13
**Version:** 1.0.0
