# Email-to-SMS Operations Guide

**Version:** 1.0.0
**For:** System Administrators and DevOps Engineers

## Table of Contents

1. [Overview](#overview)
2. [Monitoring and Logging](#monitoring-and-logging)
3. [Performance Tuning](#performance-tuning)
4. [Scaling Strategies](#scaling-strategies)
5. [Cost Optimization](#cost-optimization)
6. [Security Hardening](#security-hardening)
7. [Backup and Recovery](#backup-and-recovery)
8. [Incident Response](#incident-response)

---

## Overview

### System Architecture

```
Production Environment:
┌─────────────────────────────────────────────────┐
│  Cloudflare Global Network                      │
│  ┌───────────────────────────────────────────┐  │
│  │  Email Routing (MX Records)               │  │
│  │  → Route: *@sms.domain.com                │  │
│  └──────────────┬────────────────────────────┘  │
│                 │                                │
│  ┌──────────────▼────────────────────────────┐  │
│  │  Worker (V8 Isolate)                      │  │
│  │  - Parse email (PostalMime)               │  │
│  │  - Extract phone (multiple strategies)    │  │
│  │  - Process content                        │  │
│  │  - Send SMS (Twilio API)                  │  │
│  │  - Log transaction                        │  │
│  └──────────────┬────────────────────────────┘  │
│                 │                                │
│  ┌──────────────▼────────────────────────────┐  │
│  │  KV Namespace                             │  │
│  │  - Rate limiting counters                 │  │
│  │  - Audit logs (30-day retention)          │  │
│  └───────────────────────────────────────────┘  │
│                                                  │
│  ┌───────────────────────────────────────────┐  │
│  │  Analytics Engine                         │  │
│  │  - Request metrics                        │  │
│  │  - Performance data                       │  │
│  │  - Error tracking                         │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────┐
│  Twilio API                                      │
│  - SMS delivery                                  │
│  - Status callbacks                             │
│  - Error reporting                              │
└─────────────────────────────────────────────────┘
```

### Components

1. **Email Routing** - Cloudflare Email Routing service
2. **Worker** - Serverless compute (V8 isolate)
3. **KV Store** - Key-value persistence
4. **Analytics Engine** - Metrics collection
5. **Twilio API** - SMS gateway

---

## Monitoring and Logging

### Real-Time Log Monitoring

#### Tail Logs in Real-Time

```bash
# Start log streaming
npm run tail

# Filter for errors only
npm run tail | grep -i "error"

# Filter for specific sender
npm run tail | grep "sender@example.com"

# Monitor processing time
npm run tail | grep "processingTime"
```

#### Log Entry Structure

```json
{
  "timestamp": "2025-11-13T10:30:45.123Z",
  "level": "info",
  "message": "Email-to-SMS conversion successful",
  "requestId": "abc123...",
  "emailFrom": "user@example.com",
  "emailTo": "5551234567@sms.domain.com",
  "smsTo": "+15551234567",
  "smsFrom": "+15559876543",
  "messageLength": 85,
  "processingTimeMs": 234,
  "twilioSid": "SM...",
  "phoneSource": "email_address",
  "rateLimitRemaining": 8,
  "status": "success"
}
```

#### Log Levels

| Level | Usage | Retention |
|-------|-------|-----------|
| DEBUG | Development only | Real-time only |
| INFO | Successful transactions | 7 days (console) |
| WARN | Rate limits, retries | 30 days (KV) |
| ERROR | Failures, exceptions | 90 days (KV) |

### Analytics Dashboard

#### Cloudflare Analytics

**Access:**
1. Cloudflare Dashboard
2. Workers & Pages
3. Select `email-to-sms-worker`
4. Click **Metrics** tab

**Available Metrics:**
- Request count (24h, 7d, 30d)
- Success rate percentage
- Error rate percentage
- CPU time (milliseconds)
- Duration (P50, P99)

#### Custom Analytics Queries

```bash
# Get success rate
npx wrangler tail --format json | \
  jq -r 'select(.status=="success") | .timestamp' | \
  wc -l

# Calculate average processing time
npx wrangler tail --format json | \
  jq -r '.processingTimeMs' | \
  awk '{sum+=$1; count++} END {print sum/count}'

# Top senders
npx wrangler tail --format json | \
  jq -r '.emailFrom' | \
  sort | uniq -c | sort -rn | head -10
```

### KV Namespace Monitoring

#### Check KV Storage Usage

```bash
# List all keys
npx wrangler kv:key list --binding EMAIL_SMS_KV

# Get specific entry
npx wrangler kv:key get "rate:sender:user@example.com" --binding EMAIL_SMS_KV

# Count total keys
npx wrangler kv:key list --binding EMAIL_SMS_KV | jq '. | length'
```

#### Rate Limit Status

```bash
# Check specific sender
npx wrangler kv:key get "rate:sender:user@example.com" --binding EMAIL_SMS_KV

# Example output:
# {"count":7,"resetAt":1731499200000}
```

#### Audit Log Queries

```bash
# Get recent transactions
npx wrangler kv:key list --binding EMAIL_SMS_KV --prefix "log:"

# Get specific transaction
npx wrangler kv:key get "log:2025-11-13:abc123" --binding EMAIL_SMS_KV
```

### Email Routing Metrics

#### Cloudflare Email Routing Dashboard

**Access:**
1. Cloudflare Dashboard
2. Select domain
3. Email Routing
4. **Metrics** tab

**Available Data:**
- Emails received (daily)
- Emails processed (daily)
- Emails rejected (daily)
- Routes triggered
- Worker invocations

### Twilio Monitoring

#### Twilio Console

**Access:**
1. Log in to Twilio Console
2. Monitor > Logs > Messaging

**Check:**
- SMS delivery status
- Error messages
- Account balance
- Usage statistics

#### Twilio API Status

```bash
# Check Twilio system status
curl https://status.twilio.com/api/v2/status.json

# Get account details
curl -X GET "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID.json" \
  -u "$TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN"
```

### Alerting Setup

#### Cloudflare Notifications

**Configure Alerts:**
1. Cloudflare Dashboard
2. Notifications
3. Add notification
4. Select triggers:
   - Worker errors > 5%
   - Worker CPU time > 50ms
   - Email routing failures

**Notification Channels:**
- Email
- Webhook
- PagerDuty
- Slack

#### Custom Alerting Script

```bash
#!/bin/bash
# monitor.sh - Check error rate every 5 minutes

ERROR_THRESHOLD=5  # 5%
WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

# Get error rate
ERROR_RATE=$(npx wrangler tail --format json --duration 300 | \
  jq -r '[.[] | select(.level=="error")] | length' | \
  awk '{print ($1 / 300) * 100}')

if (( $(echo "$ERROR_RATE > $ERROR_THRESHOLD" | bc -l) )); then
  curl -X POST $WEBHOOK_URL \
    -H 'Content-Type: application/json' \
    -d "{\"text\":\"⚠️ Email-to-SMS error rate: ${ERROR_RATE}%\"}"
fi
```

**Setup Cron:**
```bash
# Edit crontab
crontab -e

# Add monitoring job (every 5 minutes)
*/5 * * * * /home/ruhroh/email2sms/monitor.sh
```

---

## Performance Tuning

### Benchmarking

#### Measure Processing Time

```bash
# Current performance
npm run tail --format json | \
  jq -r '.processingTimeMs' | \
  awk '{
    sum+=$1;
    if(min==""){min=max=$1};
    if($1>max){max=$1};
    if($1<min){min=$1};
    count++
  }
  END {
    print "Avg: " sum/count "ms";
    print "Min: " min "ms";
    print "Max: " max "ms"
  }'
```

**Target Metrics:**
- Average: < 300ms
- P50: < 200ms
- P99: < 500ms
- Max: < 1000ms

#### Load Testing

```bash
# Send test emails in parallel
for i in {1..10}; do
  echo "Test message $i" | \
  mail -s "Load Test" 5551234567@sms.domain.com &
done
wait
```

### Optimization Strategies

#### 1. Email Parsing

**Current:**
- PostalMime streaming parser
- Minimal memory usage
- ~10-50ms parse time

**Optimization:**
- Already optimal
- No action needed

#### 2. Phone Extraction

**Current:**
- Multiple regex patterns
- Sequential checking
- ~5-10ms extraction time

**Potential Optimization:**
```typescript
// Cache compiled regex patterns
const PHONE_PATTERNS = [
  /(\+?1)?(\d{10})/,
  // ... more patterns
].map(pattern => new RegExp(pattern));

// Check in priority order
for (const pattern of PHONE_PATTERNS) {
  const match = text.match(pattern);
  if (match) return match;
}
```

#### 3. Content Processing

**Current:**
- HTML stripping
- Signature removal
- Truncation

**Optimization:**
```typescript
// Cache common signatures
const SIGNATURE_CACHE = new Map();

function removeSignature(content: string): string {
  const hash = simpleHash(content);
  if (SIGNATURE_CACHE.has(hash)) {
    return SIGNATURE_CACHE.get(hash);
  }
  const result = processSignature(content);
  SIGNATURE_CACHE.set(hash, result);
  return result;
}
```

#### 4. Twilio API Calls

**Current:**
- 3 retry attempts
- Exponential backoff
- 10s timeout

**Optimization:**
```typescript
// Connection pooling (automatic in Cloudflare)
// Reduce timeout for faster failures
const timeout = 5000; // 5s instead of 10s

// Parallel health check
const healthCheck = fetch('https://status.twilio.com/api/v2/status.json', {
  signal: AbortSignal.timeout(1000)
});
```

### Caching Strategies

#### Environment Variable Caching

**Automatic in Workers:**
- Environment variables cached per isolate
- No optimization needed

#### KV Read Optimization

```typescript
// Batch KV reads
const [senderLimit, recipientLimit, globalLimit] = await Promise.all([
  env.EMAIL_SMS_KV.get(`rate:sender:${sender}`),
  env.EMAIL_SMS_KV.get(`rate:recipient:${recipient}`),
  env.EMAIL_SMS_KV.get(`rate:global`)
]);
```

#### Response Caching

```typescript
// Cache Twilio phone number validation
const phoneCache = new Map();

async function validatePhone(phone: string): Promise<boolean> {
  if (phoneCache.has(phone)) {
    return phoneCache.get(phone);
  }
  const isValid = await twilioValidate(phone);
  phoneCache.set(phone, isValid);
  return isValid;
}
```

### Worker Optimization

#### CPU Time Reduction

**Current CPU Usage:**
- Parsing: ~10ms
- Processing: ~20ms
- API call: ~200ms
- Total: ~230ms

**Optimization Targets:**
- Parsing: ~10ms (optimal)
- Processing: ~15ms (reduce by 25%)
- API call: ~150ms (reduce timeout)
- Total: ~175ms (25% improvement)

#### Memory Usage

**Current:**
- Streaming parser (minimal heap)
- No large objects
- ~5MB per request

**Monitoring:**
```bash
# Check memory usage in analytics
# Dashboard > Workers > Metrics > Memory
```

---

## Scaling Strategies

### Horizontal Scaling

#### Cloudflare Workers Auto-Scaling

**Built-in Features:**
- Automatic scaling to millions of requests
- Global distribution (200+ data centers)
- No configuration needed
- Pay per request

**Capacity:**
- Free tier: 100,000 requests/day
- Paid tier: Unlimited requests
- ~1ms cold start time
- No warm-up needed

### Vertical Scaling

#### Workers Limits

| Resource | Limit | Typical Usage |
|----------|-------|---------------|
| CPU Time | 50ms (free), 500ms (paid) | ~30ms |
| Memory | 128MB | ~5MB |
| Request Size | 100MB | <1MB (email) |
| Response Size | Unlimited | <1KB |

**Optimization:**
- Currently well within limits
- No vertical scaling needed

### Email Routing Scaling

#### Email Volume Limits

**Free Tier:**
- 1,000 emails/day
- 100 routes
- 200 addresses

**Paid Tier:**
- 10,000 emails/day
- Custom limits available

**Current Usage Monitoring:**
```bash
# Check daily email count
# Dashboard > Email Routing > Metrics
```

### Twilio Scaling

#### SMS Throughput

**Default Limits:**
- US: 1 message/second (default)
- Higher limits available
- Request via Twilio Support

**Scaling Options:**
1. Request higher throughput
2. Use multiple phone numbers
3. Implement queueing

#### Queueing Strategy

```typescript
// Optional: Implement Cloudflare Queue
import { Queue } from '@cloudflare/workers-types';

interface Env {
  SMS_QUEUE: Queue<SMSMessage>;
}

// Producer (worker)
await env.SMS_QUEUE.send({
  to: phone,
  body: message
});

// Consumer (separate worker)
async queue(batch: MessageBatch<SMSMessage>, env: Env) {
  for (const message of batch.messages) {
    await sendSMS(message.body);
  }
}
```

### Geographic Distribution

#### Cloudflare Global Network

**Automatic Features:**
- 200+ data centers worldwide
- Automatic failover
- Anycast routing
- <50ms latency globally

**No Configuration Needed:**
- Workers run at edge automatically
- Email routing uses closest MX
- DNS resolves to nearest datacenter

### Load Balancing

#### Built-in Load Balancing

**Cloudflare Handles:**
- Request distribution
- DDoS protection
- Traffic shaping
- Rate limiting

**Additional Controls:**
```toml
# wrangler.toml
[triggers]
crons = ["0 * * * *"]  # Optional: Scheduled tasks

[usage_model]
usage_model = "unbound"  # Higher limits
```

---

## Cost Optimization

### Cost Breakdown

#### Cloudflare Costs

**Workers:**
- Free tier: 100,000 requests/day
- Paid tier: $5/month + $0.50 per million requests
- Current usage: ~1,000 requests/day
- **Cost: $0/month** (within free tier)

**Email Routing:**
- Free tier: 1,000 emails/day
- Current usage: ~100 emails/day
- **Cost: $0/month** (within free tier)

**KV Namespace:**
- Free tier: 100,000 reads/day, 1,000 writes/day, 1GB storage
- Current usage: ~2,000 reads/day, ~500 writes/day, <1MB storage
- **Cost: $0/month** (within free tier)

**Analytics Engine:**
- Free tier: 10 million events/month
- Current usage: ~30,000 events/month
- **Cost: $0/month** (within free tier)

**Total Cloudflare: $0/month**

#### Twilio Costs

**SMS (US):**
- Outbound SMS: $0.0079 per message
- Current usage: ~100 SMS/day
- Monthly: ~3,000 SMS/month
- **Cost: $23.70/month**

**Phone Number:**
- US number: $1.15/month
- **Cost: $1.15/month**

**Total Twilio: $24.85/month**

#### Total System Cost

**Current:**
- Cloudflare: $0/month
- Twilio: ~$25/month
- **Total: ~$25/month**

**At Scale (10,000 SMS/month):**
- Cloudflare: $0/month (still within free tier)
- Twilio: ~$80/month
- **Total: ~$80/month**

### Cost Optimization Strategies

#### 1. Reduce SMS Volume

**Batching:**
```
Instead of:
- Alert 1: Server CPU 80%
- Alert 2: Server CPU 85%
- Alert 3: Server CPU 90%

Send:
- Summary: Server CPU: 80% → 85% → 90%
```

**Deduplication:**
```typescript
// Cache recent alerts
const recentAlerts = new Map();

function shouldSendSMS(alert: string): boolean {
  const hash = simpleHash(alert);
  const lastSent = recentAlerts.get(hash);

  if (lastSent && Date.now() - lastSent < 3600000) {
    return false; // Skip if sent within 1 hour
  }

  recentAlerts.set(hash, Date.now());
  return true;
}
```

#### 2. Optimize Message Length

**Keep Under 160 Characters:**
- 1-160 chars = 1 segment ($0.0079)
- 161-320 chars = 2 segments ($0.0158)
- 321-480 chars = 3 segments ($0.0237)

**Abbreviation Strategy:**
```typescript
// Before: 180 chars (2 segments)
"Production database server CPU utilization has exceeded 95%. Please investigate immediately."

// After: 75 chars (1 segment)
"Prod DB CPU >95%. Investigate now."
```

#### 3. Smart Rate Limiting

**Prevent Runaway Scripts:**
```toml
# Aggressive rate limits
[vars]
RATE_LIMIT_PER_SENDER = "5"      # 5/hour instead of 10
RATE_LIMIT_PER_RECIPIENT = "10"  # 10/hour instead of 20
```

**Cost Savings:**
- Prevents accidental loops
- Stops spam/abuse
- Reduces unexpected bills

#### 4. Use Cloudflare Free Tier Efficiently

**Stay Within Limits:**
- Workers: 100k requests/day (track via analytics)
- Email: 1k emails/day (monitor daily)
- KV: 100k reads/day (optimize reads)

**Monitoring:**
```bash
# Check daily usage
curl -X GET "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/workers/requests" \
  -H "Authorization: Bearer $API_TOKEN"
```

#### 5. Twilio Alternatives (Future)

**Consider:**
- AWS SNS (~$0.0064/SMS)
- Vonage (~$0.0067/SMS)
- MessageBird (~$0.0080/SMS)

**Current Recommendation:**
- Stay with Twilio (reliable, well-tested)
- Savings minimal for current volume

### Budget Alerts

#### Set Up Twilio Alerts

1. Twilio Console > Billing
2. Set threshold: $50/month
3. Email notification
4. Phone notification (optional)

#### Monitor Daily Costs

```bash
#!/bin/bash
# daily-cost-check.sh

TWILIO_USAGE=$(curl -X GET \
  "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID/Usage/Records/Today.json" \
  -u "$TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN" | \
  jq -r '.usage_records[] | select(.category=="sms-outbound") | .price')

echo "Today's SMS cost: \$${TWILIO_USAGE}"

# Alert if over $5/day
if (( $(echo "$TWILIO_USAGE > 5" | bc -l) )); then
  echo "⚠️ High SMS usage today!"
fi
```

---

## Security Hardening

### Authentication and Authorization

#### Sender Allowlist

**Strict Configuration:**
```toml
[vars]
# Option 1: Specific users only
ALLOWED_SENDERS = "admin@company.com,alerts@company.com,monitoring@company.com"

# Option 2: Domain-based
ALLOWED_SENDERS = "*@company.com,*@partner.com"

# Option 3: Subdomain pattern
ALLOWED_SENDERS = "*@internal.company.com"
```

**Validation Logic:**
```typescript
function isAllowedSender(email: string, allowlist: string): boolean {
  const patterns = allowlist.split(',').map(p => p.trim());

  return patterns.some(pattern => {
    if (pattern === '*') return true; // Allow all (not recommended)
    if (pattern.startsWith('*@')) {
      const domain = pattern.substring(2);
      return email.endsWith('@' + domain);
    }
    return email === pattern; // Exact match
  });
}
```

#### Rate Limiting Security

**Prevent Abuse:**
```toml
[vars]
# Aggressive limits for security
RATE_LIMIT_PER_SENDER = "10"
RATE_LIMIT_PER_RECIPIENT = "20"
RATE_LIMIT_GLOBAL = "1000"
```

**IP-Based Limiting (Future):**
```typescript
// Track by IP as additional layer
const ipKey = `rate:ip:${request.headers.get('CF-Connecting-IP')}`;
const ipCount = await env.EMAIL_SMS_KV.get(ipKey);
```

### Secrets Management

#### Rotate Secrets Regularly

**Schedule:**
- Twilio Auth Token: Every 90 days
- Review other secrets: Quarterly

**Rotation Process:**
```bash
# 1. Generate new token in Twilio Console
# 2. Update secret
npx wrangler secret put TWILIO_AUTH_TOKEN
# Enter new token

# 3. Test with new token
npm run deploy:staging

# 4. Deploy to production
npm run deploy:production

# 5. Revoke old token in Twilio Console
```

#### Secret Audit

```bash
# List all secrets
npx wrangler secret list

# Expected:
# - TWILIO_ACCOUNT_SID
# - TWILIO_AUTH_TOKEN
# - TWILIO_PHONE_NUMBER

# Remove unexpected secrets
npx wrangler secret delete UNEXPECTED_SECRET
```

### Input Validation

#### Email Validation

**Current Implementation:**
```typescript
function validateEmail(email: string): boolean {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!regex.test(email)) return false;

  // Additional checks
  if (email.length > 254) return false;
  if (email.includes('..')) return false;

  return true;
}
```

#### Phone Number Validation

**Enhanced Validation:**
```typescript
function validatePhone(phone: string): boolean {
  // E.164 format
  if (!/^\+[1-9]\d{1,14}$/.test(phone)) return false;

  // US numbers
  if (phone.startsWith('+1')) {
    if (phone.length !== 12) return false;

    // Invalid area codes
    const areaCode = phone.substring(2, 5);
    if (['000', '555', '911'].includes(areaCode)) return false;
  }

  return true;
}
```

#### Content Sanitization

**XSS Prevention:**
```typescript
function sanitizeContent(content: string): string {
  // Strip HTML completely
  let text = content.replace(/<[^>]*>/g, '');

  // Remove potentially dangerous characters
  text = text.replace(/[<>&'"]/g, '');

  // Normalize whitespace
  text = text.replace(/\s+/g, ' ').trim();

  return text;
}
```

### Network Security

#### HTTPS Only

**Automatic:**
- Cloudflare Workers use HTTPS by default
- Twilio API requires HTTPS
- No configuration needed

#### CORS Protection

**Not applicable:**
- Email Worker doesn't handle browser requests
- No CORS concerns

#### DDoS Protection

**Cloudflare Built-in:**
- Automatic DDoS mitigation
- Rate limiting at edge
- WAF rules (optional)

### Logging Security

#### Sensitive Data Protection

**Never Log:**
```typescript
// ❌ BAD
console.log('Twilio token:', env.TWILIO_AUTH_TOKEN);
console.log('Full email body:', emailBody);
console.log('Phone number:', phone);

// ✅ GOOD
console.log('Processing email from sender');
console.log('SMS sent successfully', { sid: 'SM...' });
console.log('Phone extracted', { source: 'email_address' });
```

#### Log Retention

**Retention Policy:**
- Console logs: 7 days (automatic)
- KV logs: 30 days (TTL)
- Analytics: 90 days (automatic)

**Cleanup:**
```bash
# KV logs auto-expire via TTL
# No manual cleanup needed
```

### Security Audit Checklist

**Monthly Review:**
- [ ] Review sender allowlist
- [ ] Check rate limit effectiveness
- [ ] Audit secret access
- [ ] Review error logs for attacks
- [ ] Check for unauthorized access
- [ ] Verify Twilio usage patterns
- [ ] Review KV storage size

**Quarterly Review:**
- [ ] Rotate Twilio credentials
- [ ] Security penetration test
- [ ] Update dependencies
- [ ] Review access controls
- [ ] Audit user list

---

## Backup and Recovery

### Configuration Backup

#### Backup `wrangler.toml`

```bash
# Automated backup script
#!/bin/bash
# backup-config.sh

DATE=$(date +%Y%m%d)
BACKUP_DIR="/home/ruhroh/email2sms/backups"

mkdir -p $BACKUP_DIR

# Backup wrangler.toml
cp config/wrangler.toml "$BACKUP_DIR/wrangler.toml.$DATE"

# Backup package.json
cp package.json "$BACKUP_DIR/package.json.$DATE"

# Backup source code
tar -czf "$BACKUP_DIR/src.$DATE.tar.gz" src/

echo "Backup completed: $DATE"
```

**Schedule:**
```bash
# Add to crontab
0 2 * * * /home/ruhroh/email2sms/backup-config.sh
```

#### Version Control

**Git Strategy:**
```bash
# Commit after changes
git add config/wrangler.toml
git commit -m "Update: Rate limits increased"
git push origin main

# Tag releases
git tag -a v1.0.1 -m "Production release"
git push origin v1.0.1
```

### KV Namespace Backup

#### Export KV Data

```bash
# Export all keys
npx wrangler kv:key list --binding EMAIL_SMS_KV > kv-backup.json

# Export specific namespace data
#!/bin/bash
# backup-kv.sh

KEYS=$(npx wrangler kv:key list --binding EMAIL_SMS_KV | jq -r '.[].name')

for key in $KEYS; do
  value=$(npx wrangler kv:key get "$key" --binding EMAIL_SMS_KV)
  echo "{\"key\":\"$key\",\"value\":$value}" >> kv-data-backup.jsonl
done
```

#### Restore KV Data

```bash
# Restore from backup
#!/bin/bash
# restore-kv.sh

while IFS= read -r line; do
  key=$(echo $line | jq -r '.key')
  value=$(echo $line | jq -r '.value')

  npx wrangler kv:key put "$key" "$value" --binding EMAIL_SMS_KV
done < kv-data-backup.jsonl
```

### Disaster Recovery

#### Worker Rollback

```bash
# List recent deployments
npx wrangler deployments list

# Output:
# Created:      ID:            Version:
# 2025-11-13    abc123...      1.0.1
# 2025-11-12    xyz789...      1.0.0

# Rollback to previous
npx wrangler rollback

# Or rollback to specific version
npx wrangler rollback --message "Rollback to v1.0.0"
```

#### Complete System Recovery

**Scenario: Complete data center failure**

1. **Worker Recovery** (automatic)
   - Cloudflare automatically fails over
   - No action needed

2. **Email Routing Recovery** (automatic)
   - MX records use multiple servers
   - Automatic failover

3. **KV Recovery**
   ```bash
   # Restore from backup
   ./restore-kv.sh
   ```

4. **Secrets Recovery**
   ```bash
   # Re-configure secrets
   npx wrangler secret put TWILIO_ACCOUNT_SID
   npx wrangler secret put TWILIO_AUTH_TOKEN
   npx wrangler secret put TWILIO_PHONE_NUMBER
   ```

5. **Redeploy Worker**
   ```bash
   npm run deploy:production
   ```

#### Recovery Time Objectives

| Component | RTO | RPO |
|-----------|-----|-----|
| Worker | < 1 minute | 0 (automatic failover) |
| Email Routing | < 1 minute | 0 (automatic failover) |
| KV Data | < 15 minutes | 24 hours (daily backup) |
| Configuration | < 5 minutes | 24 hours (git commit) |

### Incident Documentation

#### Incident Log Template

```markdown
# Incident Report: [YYYY-MM-DD]

## Summary
Brief description of incident

## Timeline
- HH:MM - Incident detected
- HH:MM - Investigation started
- HH:MM - Root cause identified
- HH:MM - Fix deployed
- HH:MM - Incident resolved

## Impact
- Users affected: X
- Duration: X minutes
- Messages lost: X

## Root Cause
Technical explanation

## Resolution
Steps taken to resolve

## Prevention
Steps to prevent recurrence

## Action Items
- [ ] Update monitoring
- [ ] Add alerts
- [ ] Update documentation
```

---

## Incident Response

### Incident Classification

| Severity | Description | Response Time | Example |
|----------|-------------|---------------|---------|
| P0 | Complete outage | < 15 minutes | Worker down |
| P1 | Major functionality broken | < 1 hour | SMS not sending |
| P2 | Degraded performance | < 4 hours | Slow processing |
| P3 | Minor issue | < 24 hours | Rate limit too low |

### Response Procedures

#### P0: Complete Outage

**Symptoms:**
- No emails processed
- Worker unavailable
- All SMS failing

**Response:**
1. **Immediate** (0-5 min)
   ```bash
   # Check worker status
   npx wrangler deployments list

   # Check Cloudflare status
   curl https://www.cloudflarestatus.com/api/v2/status.json
   ```

2. **Investigation** (5-10 min)
   ```bash
   # Review recent changes
   git log --oneline -10

   # Check deployment logs
   npx wrangler tail

   # Verify secrets
   npx wrangler secret list
   ```

3. **Rollback** (10-15 min)
   ```bash
   # Rollback to last working version
   npx wrangler rollback

   # Verify recovery
   # Send test email
   ```

4. **Communication** (ongoing)
   - Notify stakeholders
   - Update status page
   - Document incident

#### P1: SMS Not Sending

**Symptoms:**
- Emails processed
- No SMS delivered
- Twilio errors in logs

**Response:**
1. **Check Twilio** (0-10 min)
   ```bash
   # Verify Twilio status
   curl https://status.twilio.com/api/v2/status.json

   # Check account balance
   # Login to Twilio Console
   ```

2. **Verify Configuration** (10-20 min)
   ```bash
   # Check secrets
   npx wrangler secret list

   # Test with known-good credentials
   npm run dev
   # Send test email
   ```

3. **Review Logs** (20-40 min)
   ```bash
   # Look for Twilio errors
   npm run tail | grep -i "twilio\|error"
   ```

4. **Resolution** (40-60 min)
   - Update credentials if needed
   - Redeploy if configuration changed
   - Verify SMS delivery

#### P2: Degraded Performance

**Symptoms:**
- Slow processing (>1s)
- Timeouts
- High error rate

**Response:**
1. **Monitor** (0-30 min)
   ```bash
   # Check processing times
   npm run tail | grep "processingTime"

   # Check Cloudflare analytics
   # Dashboard > Metrics
   ```

2. **Identify Bottleneck** (30-120 min)
   - Review code changes
   - Check external API performance
   - Analyze logs

3. **Optimize** (2-4 hours)
   - Implement fixes
   - Deploy to staging
   - Test performance
   - Deploy to production

### On-Call Runbook

#### Before Going On-Call

```bash
# 1. Verify access
npx wrangler whoami

# 2. Test tools
npm run tail
npx wrangler deployments list

# 3. Review recent changes
git log --oneline -20

# 4. Check system health
# Dashboard > Workers > Metrics
```

#### During On-Call

**Tools Ready:**
- Terminal with wrangler
- Cloudflare Dashboard access
- Twilio Console access
- Communication channels (email, Slack)

**Quick Commands:**
```bash
# Status check
npx wrangler tail --format json | head -1

# Error check
npm run tail | grep -i error

# Rollback
npx wrangler rollback

# Emergency shutdown (if needed)
# Comment out route in Email Routing dashboard
```

#### After Incident

**Post-Mortem:**
1. Document incident (see template above)
2. Identify root cause
3. Implement prevention measures
4. Update runbook
5. Share learnings with team

---

**Last Updated:** 2025-11-13
**Version:** 1.0.0
**Next Review:** 2026-02-13
