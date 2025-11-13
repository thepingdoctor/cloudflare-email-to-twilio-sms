# Email-to-SMS Worker Deployment Guide

## Prerequisites

1. **Cloudflare Account** with Email Routing enabled
2. **Twilio Account** with:
   - Account SID
   - Auth Token
   - Active phone number (E.164 format)
3. **Node.js** 18+ installed
4. **Domain** configured with Cloudflare DNS

## Installation

### 1. Install Dependencies

```bash
cd /home/ruhroh/email2sms
npm install
```

### 2. Configure Secrets (Development)

Create `.dev.vars` file for local development:

```bash
cp .dev.vars.example .dev.vars
```

Edit `.dev.vars` and add your Twilio credentials:

```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+1234567890
ALLOWED_SENDERS=your@email.com
```

### 3. Configure wrangler.toml

Edit `config/wrangler.toml`:

```toml
account_id = "your-cloudflare-account-id"  # Get from Cloudflare dashboard
```

## Local Development

### Start Development Server

```bash
npm run dev
```

The worker will run locally on `http://localhost:8787`

### Test Email Processing

You can test email handling locally using wrangler's email simulation.

## Production Deployment

### 1. Set Production Secrets

```bash
# Set Twilio credentials as secrets
npm run secret:put TWILIO_ACCOUNT_SID
# Enter: ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

npm run secret:put TWILIO_AUTH_TOKEN
# Enter: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

npm run secret:put TWILIO_PHONE_NUMBER
# Enter: +1234567890
```

### 2. Create KV Namespace (Optional - for rate limiting)

```bash
npm run kv:create
```

Copy the namespace ID and add to `config/wrangler.toml`:

```toml
[[kv_namespaces]]
binding = "EMAIL_SMS_KV"
id = "abc123..."
```

### 3. Deploy Worker

```bash
# Deploy to production
npm run deploy:production

# Or deploy to staging first
npm run deploy:staging
```

### 4. Configure Email Routing

1. Go to Cloudflare Dashboard → Email Routing
2. Enable Email Routing for your domain
3. Create custom address or route:
   - **Match**: `*@sms.yourdomain.com` (or specific pattern)
   - **Action**: Send to Worker
   - **Worker**: Select `email-to-sms-worker`
4. Verify MX records are configured (automatic)

## Email Address Formats

Your users can send emails in several ways:

### Format 1: Phone in Email Address
```
To: 15551234567@sms.yourdomain.com
Subject: Test message
Body: This will be sent as SMS
```

### Format 2: Phone in Subject
```
To: contact@sms.yourdomain.com
Subject: To: 555-123-4567
Body: This will be sent as SMS
```

### Format 3: Custom Header
```
To: sms@yourdomain.com
X-SMS-To: +15551234567
Body: This will be sent as SMS
```

## Configuration Options

### Environment Variables

Set in `config/wrangler.toml`:

```toml
[vars]
ALLOWED_SENDERS = "user@example.com,*@trusted.com"
DEFAULT_COUNTRY_CODE = "1"
```

### Allowed Senders

Configure sender allowlist to prevent unauthorized use:

- Specific: `john@example.com`
- Domain wildcard: `*@example.com`
- Multiple: `john@example.com,*@trusted.com,jane@other.com`

## Monitoring

### View Logs

```bash
npm run tail
```

### Check Worker Status

```bash
wrangler deployments list
```

### View Analytics

Go to Cloudflare Dashboard → Workers & Pages → Analytics

## Rate Limiting

If KV namespace is configured, rate limits are:

- **Per Sender**: 10 messages/hour
- **Per Recipient**: 20 messages/hour
- **Global**: 1000 messages/day

## Security Best Practices

1. ✅ **Never commit `.dev.vars`** to version control
2. ✅ **Always use secrets** for production credentials
3. ✅ **Configure ALLOWED_SENDERS** to prevent abuse
4. ✅ **Enable rate limiting** with KV namespace
5. ✅ **Monitor logs** for suspicious activity
6. ✅ **Rotate secrets** periodically

## Troubleshooting

### Email Not Processing

1. Check Email Routing is enabled
2. Verify route is configured correctly
3. Check worker logs: `npm run tail`
4. Verify secrets are set: `wrangler secret list`

### SMS Not Sending

1. Verify Twilio credentials are correct
2. Check Twilio phone number is active
3. Verify recipient phone number format (+1XXXXXXXXXX)
4. Check Twilio account balance
5. Review worker logs for Twilio errors

### Rate Limiting Issues

1. Verify KV namespace is created and bound
2. Check rate limit status in logs
3. Reset limits if needed (requires custom admin endpoint)

### Phone Number Extraction Fails

1. Check email format matches supported patterns
2. Verify phone number is in valid format
3. Review logs for extraction source used
4. Try alternative format (subject line vs email address)

## Cost Considerations

### Cloudflare

- **Workers**: Free tier includes 100,000 requests/day
- **Email Routing**: Free tier includes 1,000 emails/day
- **KV Namespace**: Free tier includes 100,000 reads/day

### Twilio

- **SMS Pricing**: ~$0.0075 per message (US)
- **Phone Number**: ~$1/month
- Check current pricing: https://www.twilio.com/pricing

## Support

- **Cloudflare Email Routing**: https://developers.cloudflare.com/email-routing/
- **Twilio SMS API**: https://www.twilio.com/docs/sms
- **Wrangler Docs**: https://developers.cloudflare.com/workers/wrangler/

## Updating

### Update Dependencies

```bash
npm update
```

### Redeploy

```bash
npm run deploy:production
```

## Rollback

If deployment fails, rollback to previous version:

```bash
wrangler rollback
```
