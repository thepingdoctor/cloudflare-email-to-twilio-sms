# Email-to-SMS Quick Reference

**Version:** 1.0.0

## Email Formats

### Format 1: Phone in Email Address (Recommended)
```
To: 15551234567@sms.yourdomain.com
Subject: [optional]
Body: Your message
```

### Format 2: Phone in Subject
```
To: contact@sms.yourdomain.com
Subject: To: 555-123-4567
Body: Your message
```

### Format 3: Custom Header
```
To: sms@yourdomain.com
X-SMS-To: +15551234567
Body: Your message
```

---

## Phone Number Formats

**US Numbers:**
- E.164: `+15551234567` ✅ Best
- National: `5551234567` ✅ Auto-converted
- Formatted: `555-123-4567` ✅
- Formatted: `(555) 123-4567` ✅

**International:**
- E.164: `+447700900123` (UK)
- E.164: `+61491570156` (Australia)

---

## Common Commands

### Worker Deployment
```bash
# Install dependencies
npm install

# Local development
npm run dev

# Deploy to production
npm run deploy:production

# View logs
npm run tail

# Type check
npm run typecheck
```

### Secrets Management
```bash
# Set secret
npx wrangler secret put SECRET_NAME

# List secrets
npx wrangler secret list

# Delete secret
npx wrangler secret delete SECRET_NAME
```

### KV Namespace
```bash
# Create namespace
npm run kv:create

# List keys
npx wrangler kv:key list --binding EMAIL_SMS_KV

# Get value
npx wrangler kv:key get "key" --binding EMAIL_SMS_KV

# Delete key
npx wrangler kv:key delete "key" --binding EMAIL_SMS_KV
```

### Streamlit UI
```bash
# Navigate to app
cd streamlit-app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run app
streamlit run app.py

# Custom port
streamlit run app.py --server.port 8502
```

### Deployment
```bash
# Deploy to staging
npm run deploy:staging

# Deploy to production
npm run deploy:production

# List deployments
npx wrangler deployments list

# Rollback
npx wrangler rollback
```

---

## Configuration Files

### wrangler.toml
```toml
name = "email-to-sms-worker"
account_id = "your-account-id"
main = "src/worker/index.ts"

[vars]
ALLOWED_SENDERS = "user@example.com,*@domain.com"
DEFAULT_COUNTRY_CODE = "1"

[[kv_namespaces]]
binding = "EMAIL_SMS_KV"
id = "your-namespace-id"
```

### .dev.vars
```env
TWILIO_ACCOUNT_SID=ACxxxx...
TWILIO_AUTH_TOKEN=xxxx...
TWILIO_PHONE_NUMBER=+15551234567
ALLOWED_SENDERS=your@email.com
```

---

## Error Messages

| Error | Cause | Fix |
|-------|-------|-----|
| `Unauthorized sender` | Not in allowlist | Add to ALLOWED_SENDERS |
| `Invalid phone format` | Bad phone number | Use E.164: +15551234567 |
| `Rate limit exceeded` | Too many messages | Wait or request increase |
| `Empty content` | No email body | Add message text |
| `Message too long` | >1600 characters | Shorten message |
| `TWILIO_ERROR_401` | Bad credentials | Update secrets |
| `TWILIO_ERROR_21211` | Invalid phone | Check format |

---

## Rate Limits

**Default Limits:**
- Per sender: 10 messages/hour
- Per recipient: 20 messages/hour
- Global: 1,000 messages/day

**Check Limit:**
```bash
npx wrangler kv:key get "rate:sender:email@example.com" \
  --binding EMAIL_SMS_KV
```

**Reset Limit:**
```bash
npx wrangler kv:key delete "rate:sender:email@example.com" \
  --binding EMAIL_SMS_KV
```

---

## Monitoring

### View Logs
```bash
# Real-time logs
npm run tail

# Filter errors only
npm run tail | grep -i error

# Filter by sender
npm run tail | grep "user@example.com"

# Processing times
npm run tail | grep "processingTime"
```

### Check Status
```bash
# Worker deployments
npx wrangler deployments list

# Email routing status
# Dashboard > Email Routing > Metrics

# Twilio status
curl https://status.twilio.com/api/v2/status.json
```

### Analytics
```
Cloudflare Dashboard:
Workers & Pages > email-to-sms-worker > Metrics

Shows:
- Request count
- Success rate
- Error rate
- Processing time
```

---

## Troubleshooting Quick Checks

### Email Not Processed
```bash
# 1. Check MX records
dig MX yourdomain.com

# 2. Check worker deployment
npx wrangler deployments list

# 3. Check logs
npm run tail

# 4. Verify route
# Dashboard > Email Routing > Routes
```

### SMS Not Sending
```bash
# 1. Check secrets
npx wrangler secret list

# 2. Test Twilio
curl https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID.json \
  -u "$TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN"

# 3. Check logs
npm run tail | grep -i twilio

# 4. Verify phone format
# Use: +15551234567
```

### Worker Issues
```bash
# 1. Redeploy
npm run deploy:production

# 2. Check for errors
npm run typecheck

# 3. View recent logs
npm run tail

# 4. Rollback if needed
npx wrangler rollback
```

---

## Email Routing Setup

### Enable Email Routing
```
1. Cloudflare Dashboard
2. Select domain
3. Email Routing > Enable
4. Wait for MX setup (automatic)
```

### Create Route
```
1. Email Routing > Routing Rules
2. Create Route
3. Pattern: *@sms.yourdomain.com
4. Action: Send to Worker
5. Worker: email-to-sms-worker
6. Save
```

### Verify MX Records
```bash
dig MX yourdomain.com

# Should show:
# isaac.mx.cloudflare.net
# linda.mx.cloudflare.net
# amir.mx.cloudflare.net
```

---

## Cost Reference

### Cloudflare (Free Tier)
- Workers: 100k requests/day
- Email Routing: 1k emails/day
- KV: 100k reads/day
- **Cost: $0/month**

### Twilio
- SMS (US): ~$0.0079/message
- Phone number: ~$1.15/month
- **Typical: $25/month** (100 SMS/day)

### Example Costs
- 100 SMS/month: ~$2/month
- 1,000 SMS/month: ~$10/month
- 3,000 SMS/month: ~$25/month
- 10,000 SMS/month: ~$80/month

---

## File Structure

```
email2sms/
├── src/
│   ├── worker/           # Main worker
│   ├── services/         # Twilio integration
│   ├── utils/            # Phone parser, content processor
│   ├── middleware/       # Validation, rate limiting
│   └── types/            # TypeScript definitions
├── config/
│   └── wrangler.toml     # Worker configuration
├── docs/                 # Documentation
├── streamlit-app/        # Code generator UI
├── package.json          # Dependencies
└── tsconfig.json         # TypeScript config
```

---

## Support Resources

### Documentation
- [Deployment Master Guide](DEPLOYMENT_MASTER.md)
- [User Guide](USER_GUIDE.md)
- [Operations Guide](OPERATIONS.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [API Documentation](API.md)

### External Resources
- [Cloudflare Workers Docs](https://developers.cloudflare.com/workers/)
- [Twilio SMS API](https://www.twilio.com/docs/sms)
- [Email Routing](https://developers.cloudflare.com/email-routing/)

---

## Quick Test

```bash
# 1. Send test email
echo "Test message" | mail -s "Test" 5551234567@sms.yourdomain.com

# 2. Watch logs
npm run tail

# 3. Check phone for SMS
# Should receive: "From: Your Name\nRe: Test\nTest message"

# 4. Verify in Cloudflare Dashboard
# Email Routing > Metrics
```

---

**Last Updated:** 2025-11-13
