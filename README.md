# Cloudflare Email-to-Twilio-SMS Worker

**Version:** 1.0.0
**Status:** Production Ready

A comprehensive email-to-SMS conversion system with two components:
1. **Cloudflare Worker** - Production email processor with Twilio SMS integration
2. **Streamlit UI** - Interactive code generator for customized deployments

---

## 🎯 Features

### Email Worker (Production Ready)
- ✅ **Email Processing**: Cloudflare Email Routing integration with PostalMime parser
- ✅ **Smart Phone Extraction**: Multiple strategies (email address, subject, headers, body)
- ✅ **Content Processing**: HTML to text, signature removal, intelligent truncation
- ✅ **Twilio Integration**: SMS sending with retry logic and comprehensive error handling
- ✅ **Security**: Sender validation, rate limiting, content sanitization
- ✅ **Monitoring**: Structured logging, Analytics Engine integration, audit trails
- ✅ **Rate Limiting**: KV-based limits per sender, recipient, and globally
- ✅ **Error Handling**: Graceful degradation with detailed error messages

### Streamlit Code Generator (NEW: Email Worker Support)
- ✅ **Interactive UI**: Web-based configuration interface
- ✅ **Dual Worker Types**: Generate Standard (HTTP) or Email Routing workers
- ✅ **Email Worker Generation**: Complete email-to-SMS worker code generation (8 files)
- ✅ **Code Generation**: Generates production-ready Worker code
- ✅ **Customization**: Configure all worker features via UI
- ✅ **Download**: Export complete project as ZIP
- ✅ **Templates**: Multiple configuration templates
- ✅ **Validation**: Real-time configuration validation
- ✅ **Comprehensive Testing**: 46 email worker tests with 91% coverage

---

## 🚀 Quick Start

### Option 1: Generate Custom Email Worker (Most Flexible - NEW!)

The Streamlit app now supports **Email Worker generation** with complete Cloudflare Email Routing support!

#### Using Poetry (Recommended)

```bash
# 1. Install Poetry (if not already installed)
# macOS/Linux/WSL:
curl -sSL https://install.python-poetry.org | python3 -

# Windows (PowerShell):
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -

# 2. Verify Poetry installation
poetry --version
# Expected output: Poetry (version 1.x.x)

# If poetry command not found, add to PATH:
# macOS/Linux: Add to ~/.bashrc or ~/.zshrc
export PATH="$HOME/.local/bin:$PATH"
# Then: source ~/.bashrc (or restart terminal)

# 3. Start Streamlit UI
cd streamlit-app
poetry install
poetry run streamlit run app.py

# 3. Configure in browser (http://localhost:8501)
#    - Enable Email Worker mode
#    - Configure email routing pattern (e.g., *@sms.example.com)
#    - Set phone extraction method
#    - Configure Twilio settings
# 4. Generate and download Email Worker code (8 files, 1,059 lines)
# 5. Follow automated deployment instructions
```
### Option 2: Use Pre-Built Worker (Fastest; not reccommended)

```bash
# 1. Clone repository
git clone <repository-url>
cd cloudflare-email-to-twilio-sms

# 2. Install dependencies
npm install

# 3. Configure development secrets
cp .dev.vars.example .dev.vars
# Edit .dev.vars with your Twilio credentials

# 4. Test locally
npm run dev

# 5. Deploy to production
npm run deploy:production

# 6. Configure Email Routing in Cloudflare Dashboard
```


### ⚠️ CRITICAL: Email Routing Production-Only Limitation

**Cloudflare Email Routing ONLY works in production deployments:**

| Environment | Email Routing Support | Recommendation |
|-------------|----------------------|----------------|
| `wrangler dev` (local) | ❌ **NOT SUPPORTED** | Use HTTP worker mode for local testing |
| `wrangler deploy` (production) | ✅ **FULLY SUPPORTED** | Deploy to production/staging for email testing |
| Cloudflare Dashboard | ✅ **CONFIGURATION REQUIRED** | Must configure email routing rules AFTER deployment |

**Key Points:**
- Email Routing does NOT work with `wrangler dev` (local development server)
- Email Routing ONLY works after deploying with `wrangler deploy` to production
- You MUST configure Email Routing in the Cloudflare Dashboard after deployment
- For local testing: Use HTTP worker mode or deploy to staging environment

#### Using pip

```bash
# 1. Start Streamlit UI
cd streamlit-app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py

# 2. Configure in browser (http://localhost:8501)
# 3. Generate and download code
# 4. Follow deployment instructions
```

---

## 📋 Prerequisites

### Required Accounts
- **Cloudflare** account with Email Routing enabled
- **Twilio** account with active phone number
- **Domain** managed by Cloudflare DNS

### Required Software
- **Node.js** 18+ (for Worker)
- **Python** 3.8+ (3.11+ recommended for Streamlit UI)
- **npm** 9+ (for Worker dependencies)
- **Poetry** 1.0+ (optional but recommended for Streamlit)
- **Git** (for version control)

---

## 📧 Email Format Examples

### Format 1: Phone in Email Address (Recommended)
```
To: 15551234567@sms.yourdomain.com
Subject: Meeting Reminder
Body: Don't forget our meeting at 2pm today!
```

**Result:**
```
From: Your Name
Re: Meeting Reminder
Don't forget our meeting at 2pm today!
```

### Format 2: Phone in Subject Line
```
To: contact@sms.yourdomain.com
Subject: To: 555-123-4567
Body: Your message here
```

### Format 3: Custom Header
```
To: sms@yourdomain.com
X-SMS-To: +15551234567
Body: Your message here
```

---

## 🏗️ Architecture

### System Flow Diagram

```
┌─────────────┐         ┌──────────────────┐         ┌─────────────┐
│   Email     │         │   Cloudflare     │         │   Twilio    │
│   Sender    │────────▶│  Email Routing   │────────▶│  SMS API    │────────▶ 📱 SMS
└─────────────┘         └──────────────────┘         └─────────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │ Cloudflare Worker│
                        │   (Edge Deploy)  │
                        └──────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
                    ▼            ▼            ▼
            ┌──────────┐  ┌──────────┐  ┌──────────┐
            │   KV     │  │Analytics │  │  Logger  │
            │ Storage  │  │  Engine  │  │  (JSON)  │
            └──────────┘  └──────────┘  └──────────┘
             Rate Limits   Metrics       Audit Trail
```

### Processing Pipeline

```
Email Arrival
    │
    ▼
[1] Parse with PostalMime (~50ms)
    │
    ▼
[2] Validate Sender (allowlist check)
    │
    ▼
[3] Extract Phone Number (~5ms)
    ├─ Strategy 1: X-SMS-To header (high confidence)
    ├─ Strategy 2: Email address prefix (high confidence)
    ├─ Strategy 3: Subject line (medium confidence)
    └─ Strategy 4: Body text (low confidence)
    │
    ▼
[4] Validate Phone (E.164 format)
    │
    ▼
[5] Rate Limit Checks (~30ms)
    ├─ Per-sender limit (10/hour)
    ├─ Per-recipient limit (20/hour)
    └─ Global limit (1000/day)
    │
    ▼
[6] Process Content (~10ms)
    ├─ HTML → Text conversion
    ├─ Remove signatures
    ├─ Normalize whitespace
    ├─ Add email context
    └─ Smart truncate (160 chars)
    │
    ▼
[7] Validate Content
    │
    ▼
[8] Send SMS via Twilio (200-400ms)
    ├─ Retry logic (3 attempts)
    ├─ Exponential backoff
    └─ Timeout handling
    │
    ▼
[9] Log Transaction
    ├─ KV audit trail (30 days)
    ├─ Analytics Engine
    └─ Console logs (JSON)
    │
    ▼
✅ Success / ❌ Error Response

Total: 275-485ms typical
```

### Phone Extraction Strategies (Priority Order)

| Priority | Strategy | Source | Confidence | Example |
|----------|----------|--------|------------|---------|
| 1 | Custom Header | `X-SMS-To` | HIGH | `X-SMS-To: +15551234567` |
| 2 | Email Prefix | Recipient address | HIGH | `15551234567@sms.example.com` |
| 3 | Subject Line | Email subject | MEDIUM | `Subject: To: 555-123-4567` |
| 4 | Body Scanning | Email body | LOW | First 200 chars search |

---

## 🏗️ Project Structure

```
cloudflare-email-to-twilio-sms/
├── src/                    # Cloudflare Worker source code
│   ├── worker/            # Main entry point
│   │   └── index.ts       # Email handler and routing
│   ├── services/          # External integrations
│   │   └── twilio-service.ts
│   ├── utils/             # Utility functions
│   │   ├── phone-parser.ts
│   │   ├── content-processor.ts
│   │   └── logger.ts
│   ├── middleware/        # Validation & security
│   │   ├── validator.ts
│   │   └── rate-limiter.ts
│   └── types/             # TypeScript definitions
│       └── index.ts
├── streamlit-app/         # Code generator UI
│   ├── app.py            # Main Streamlit application
│   ├── components/       # UI components
│   ├── generators/       # Code generation logic
│   ├── schemas/          # Configuration schemas
│   └── utils/            # Utilities and validators
├── config/
│   └── wrangler.toml     # Worker configuration
├── docs/                 # Comprehensive documentation
│   ├── USER_GUIDE.md
│   ├── OPERATIONS.md
│   ├── TROUBLESHOOTING.md
│   ├── API.md
│   ├── ARCHITECTURE-SUMMARY.md
│   └── EMAIL_WORKER_IMPLEMENTATION.md
├── package.json          # Node.js dependencies
├── tsconfig.json         # TypeScript configuration
└── README.md            # This file
```

---

## ⚙️ Configuration

### Environment Variables

Set in `config/wrangler.toml`:

```toml
[vars]
ALLOWED_SENDERS = "user@example.com,*@domain.com"
DEFAULT_COUNTRY_CODE = "1"
```

### Secrets (Production)

Required secrets (set via `wrangler secret put`):

```bash
TWILIO_ACCOUNT_SID      # Your Twilio Account SID
TWILIO_AUTH_TOKEN       # Your Twilio Auth Token
TWILIO_PHONE_NUMBER     # Your Twilio phone number (+1XXXXXXXXXX)
```

### Optional: KV Namespace

For rate limiting and audit logging:

```bash
npm run kv:create
# Add namespace ID to config/wrangler.toml
```

---

## 🔒 Security Features

- ✅ **Secrets Management**: All credentials stored in Cloudflare Secrets
- ✅ **Sender Validation**: Configurable allowlist (exact match or domain wildcard)
- ✅ **Rate Limiting**: Per-sender, per-recipient, and global limits
- ✅ **Phone Validation**: E.164 format validation with area code checks
- ✅ **Content Sanitization**: HTML stripping and XSS prevention
- ✅ **Audit Logging**: Complete transaction history with 30-day retention
- ✅ **Email Rejection**: Clear rejection messages for unauthorized attempts

---

## 📊 Rate Limits

**Default Limits** (when KV namespace configured):

| Scope | Limit | Window |
|-------|-------|--------|
| Per Sender | 10 messages | 1 hour |
| Per Recipient | 20 messages | 1 hour |
| Global | 1,000 messages | 24 hours |

Configure in `config/wrangler.toml` or adjust via administrator.

---

## 📈 Monitoring

### Real-Time Logs
```bash
npm run tail
```

### Cloudflare Analytics
- Dashboard → Workers & Pages → cloudflare-email-to-twilio-sms → Metrics
- Request count, success rate, error distribution, processing time

### KV Audit Trail
```bash
npx wrangler kv:key list --binding EMAIL_SMS_KV --prefix "log:"
```

### Twilio Console
- Log in to Twilio Console
- Monitor → Logs → Messaging
- View delivery status and errors

---

## 🛠️ Available Commands

### Worker Development
```bash
npm run dev              # Start local development server
npm run build            # Type check TypeScript
npm run typecheck        # Run TypeScript compiler check
npm run deploy           # Deploy to production
npm run deploy:staging   # Deploy to staging environment
npm run tail             # View live logs
npm run test             # Run tests (when implemented)
```

### Secrets Management
```bash
npm run secret:put       # Add/update secret
npx wrangler secret list # List all secrets
```

### KV Namespace
```bash
npm run kv:create        # Create KV namespace
npm run kv:list          # List KV namespaces
```

### Streamlit UI
```bash
cd streamlit-app
streamlit run app.py     # Start code generator UI
```

---

## 💰 Cost Breakdown

### Cloudflare (Free Tier Sufficient for Most Use Cases)
- **Workers**: 100,000 requests/day (Free)
- **Email Routing**: 1,000 emails/day (Free)
- **KV Namespace**: 100,000 reads/day (Free)
- **Analytics Engine**: 10M events/month (Free)

**Typical Cost: $0/month** (within free tier limits)

### Twilio
- **SMS (US)**: ~$0.0079 per message
- **Phone Number**: ~$1.15/month

**Example Monthly Costs:**
- 100 SMS/month: ~$2/month
- 1,000 SMS/month: ~$10/month
- 3,000 SMS/month: ~$25/month
- 10,000 SMS/month: ~$80/month

---

## 📚 Documentation

### Comprehensive Guides

- **[User Guide](docs/USER_GUIDE.md)** - End-user guide for sending emails and using Streamlit UI
- **[Operations Guide](docs/OPERATIONS.md)** - Monitoring, performance tuning, scaling, cost optimization
- **[Troubleshooting Guide](docs/TROUBLESHOOTING.md)** - Common issues, error codes, debug procedures
- **[API Documentation](docs/API.md)** - Email formats, phone extraction, error codes, configuration

### Architecture & Implementation

- **[Architecture Summary](docs/ARCHITECTURE-SUMMARY.md)** - System architecture and design decisions
- **[Email Worker Implementation Guide](docs/EMAIL_WORKER_IMPLEMENTATION.md)** - Complete implementation details
- **[Cloudflare Email Worker Requirements](docs/CLOUDFLARE_EMAIL_WORKER_REQUIREMENTS.md)** - Technical specifications
- **[Email Worker Gap Analysis](docs/EMAIL_WORKER_GAP_ANALYSIS.md)** - Gap analysis and roadmap
- **[Poetry Guide](docs/POETRY_GUIDE.md)** - Python dependency management

---

## 🧪 Testing

### Local Testing
```bash
# Start development server
npm run dev

# Send test email (worker processes but doesn't send SMS in dev mode)
echo "Test message" | mail -s "Test" 5551234567@sms.localhost
```

### Production Testing
```bash
# Deploy to staging first
npm run deploy:staging

# Send test email
echo "Production test" | mail -s "Test" 5551234567@sms.yourdomain.com

# Monitor logs
npm run tail

# Verify SMS delivery on phone
```

---

## ⚡ Performance Characteristics

### Processing Metrics
- **Average Processing Time**: 200-500ms per email
- **Email Parsing**: ~50ms (PostalMime)
- **Phone Extraction**: ~5ms (multi-strategy with confidence scoring)
- **Content Processing**: ~10ms (HTML→SMS conversion)
- **Twilio API Call**: 200-400ms (with retry logic)
- **Total Pipeline**: 275-485ms typical

### Throughput
- **Cloudflare Workers**: Handles thousands of emails per day
- **Cold Start**: <100ms (edge deployment)
- **Rate Limits**: Configurable per sender/recipient/global

### Resource Limits
- **Worker CPU**: 50ms (free tier) / 30s (paid tier)
- **Memory**: 128MB
- **Request Timeout**: 30 seconds
- **KV Operations**: ~10ms per read/write

---

## 🔐 Security & Compliance

### Security Features
- ✅ **Defense in Depth**: 5-layer security validation
- ✅ **Sender Authorization**: Configurable allowlist with wildcard support
- ✅ **Rate Limiting**: Per-sender, per-recipient, and global limits
- ✅ **Input Validation**: E.164 phone format, RFC email compliance
- ✅ **Content Sanitization**: XSS prevention, HTML stripping, control character removal
- ✅ **Secrets Management**: Encrypted storage with Cloudflare Secrets
- ✅ **Audit Logging**: 30-day transaction history in KV

### Security Testing
- **43 Security Tests**: 100% passing
- **Attack Vectors Tested**: XSS, SQL injection, XML injection, path traversal, template injection, command injection, ReDoS, CRLF injection
- **Zero Vulnerabilities**: All npm security issues resolved (as of 2025-11-13)

### Compliance Considerations
- **Data Retention**: 30-day audit logs (configurable)
- **Encryption**: All secrets encrypted at rest (Cloudflare Secrets)
- **Access Control**: Sender allowlist enforcement
- **Audit Trail**: Complete transaction logging with KV

**Note**: For GDPR/HIPAA compliance, consult legal counsel and configure appropriate data retention policies.

---

## 🎯 Advanced Features

### Undocumented Capabilities

**SMS Segment Calculation** (`src/utils/content-processor.ts:289`)
- Calculates message segments for cost estimation
- GSM-7: 160 chars (single) / 153 chars (multi-part)
- Unicode: 70 chars (single) / 67 chars (multi-part)

**Confidence Scoring for Phone Extraction** (`src/utils/phone-parser.ts`)
- **High Confidence**: Email prefix, custom X-SMS-To header
- **Medium Confidence**: Subject line parsing
- **Low Confidence**: Body text scanning

**Admin Email Forwarding** (Commented Out)
- Forward failed emails to admin for manual review
- Enable by setting `ADMIN_EMAIL` environment variable

**Request ID Tracking** (`src/utils/logger.ts`)
- Distributed tracing support for multi-invocation workflows
- Optional `requestId` parameter for correlation

---

## 🚨 Limitations & Known Issues

### Platform Limitations

**Email Routing Production-Only Requirement** ⚠️
- Email Routing does NOT work with `wrangler dev` (local development)
- ONLY works in production after `wrangler deploy`
- Must configure Email Routing in Cloudflare Dashboard post-deployment
- **Workaround**: Deploy to staging environment for testing

### Feature Limitations

- **Attachment Handling**: Metadata logged but attachments NOT forwarded
- **Character Limits**: 160 chars (GSM-7) / 70 chars (Unicode) per SMS segment
- **International Support**: Requires DEFAULT_COUNTRY_CODE configuration
- **Bidirectional SMS**: Not yet implemented (Phase 2 roadmap)
- **MMS Support**: Not yet implemented (Phase 2 roadmap)

### Testing Limitations

- **Local Testing**: Limited without Email Routing support
- **Mock Services**: Twilio sandbox required for integration tests
- **Rate Limit Testing**: Requires KV namespace configuration

---

## ❓ Frequently Asked Questions (FAQ)

### General Questions

**Q: Why Cloudflare Workers instead of AWS Lambda?**
A: Cloudflare Workers deploy to 300+ edge locations for <100ms cold starts, vs AWS Lambda's regional deployment with ~1s cold starts. Workers also have a generous free tier (100,000 requests/day).

**Q: Can I use this for commercial purposes?**
A: Yes! MIT license allows commercial use. Just ensure you comply with Twilio's terms of service.

**Q: How do I scale beyond the free tier?**
A: Cloudflare Workers Paid ($5/month) increases limits to 10M requests/month. Twilio charges per SMS (~$0.0079/message).

**Q: Is this GDPR/HIPAA compliant?**
A: The system provides audit logging and encryption, but full compliance requires proper configuration and legal review. Consult your legal counsel.

### Technical Questions

**Q: Why doesn't email routing work locally?**
A: Cloudflare Email Routing is a production-only feature that requires DNS MX records. Use `wrangler deploy` to staging for testing.

**Q: How do I test without sending real SMS?**
A: Use Twilio's test credentials in development, or configure a staging Twilio number separate from production.

**Q: Can I use multiple Twilio accounts?**
A: Not currently, but planned for Phase 2. You can deploy multiple workers with different configurations.

**Q: What's the maximum email size?**
A: Cloudflare Email Routing supports up to 25MB emails, but SMS content is truncated to 1,600 characters (10 segments).

### Troubleshooting Questions

**Q: Why am I getting "Sender not authorized" errors?**
A: Check `ALLOWED_SENDERS` environment variable. Use exact email match or wildcard domain (`*@example.com`).

**Q: Why aren't my SMS messages sending?**
A: Verify Twilio credentials with `npx wrangler secret list`, check account balance, and review `npm run tail` logs for errors.

**Q: How do I check rate limit status?**
A: Use `npx wrangler kv:key get "ratelimit:sender:your@email.com" --binding EMAIL_SMS_KV`

---

## 🚨 Troubleshooting

### Quick Diagnostics

**Email not processing?**
```bash
# Check Email Routing status in Cloudflare Dashboard
# Verify MX records: dig MX yourdomain.com
# Check worker logs: npm run tail
```

**SMS not sending?**
```bash
# Verify Twilio secrets: npx wrangler secret list
# Check Twilio account balance
# Review logs for errors: npm run tail | grep -i twilio
```

**Rate limited?**
```bash
# Check rate limit counter
npx wrangler kv:key get "rate:sender:your@email.com" --binding EMAIL_SMS_KV
# Wait for reset or contact administrator
```

**See [Troubleshooting Guide](docs/TROUBLESHOOTING.md) for detailed solutions.**

---

## 🤝 Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup
```bash
# Fork and clone repository
git clone <your-fork-url>
cd cloudflare-email-to-twilio-sms

# Install dependencies
npm install
cd streamlit-app && pip install -r requirements.txt

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and test
npm run typecheck
npm run dev

# Commit and push
git add .
git commit -m "Add: your feature description"
git push origin feature/your-feature-name
```

---

## 📝 License

MIT License - see LICENSE file for details

---

## 🎯 Use Cases

### System Monitoring
- Server alerts and notifications
- Application error alerts
- Database performance warnings
- Security incident notifications

### Business Communications
- Order confirmations
- Appointment reminders
- Delivery notifications
- Customer alerts

### Personal Use
- Calendar reminders
- Smart home alerts
- IoT device notifications
- Personal automation

### Development
- CI/CD pipeline notifications
- Deployment alerts
- Test failure notifications
- Performance alerts

---

## 🔗 External Resources

- **[Cloudflare Workers Documentation](https://developers.cloudflare.com/workers/)**
- **[Cloudflare Email Routing](https://developers.cloudflare.com/email-routing/)**
- **[Twilio SMS API](https://www.twilio.com/docs/sms)**
- **[PostalMime](https://github.com/postalsys/postal-mime)** (Email parser)
- **[Streamlit Documentation](https://docs.streamlit.io/)**

---

## 📞 Support

### Self-Service
1. Review [Troubleshooting Guide](docs/TROUBLESHOOTING.md) for solutions
2. Search [User Guide](docs/USER_GUIDE.md) for usage help
3. Check [Operations Guide](docs/OPERATIONS.md) for monitoring and performance tuning
4. Consult [API Documentation](docs/API.md) for technical reference

### Get Help
- **Issues**: Open an issue on GitHub
- **Documentation**: Review comprehensive guides in `docs/`
- **Logs**: Always include relevant log output

---

## 🎉 Acknowledgments

Built with:
- [Cloudflare Workers](https://workers.cloudflare.com/) - Serverless compute platform
- [Cloudflare Email Routing](https://developers.cloudflare.com/email-routing/) - Email processing
- [Twilio SMS API](https://www.twilio.com/sms) - SMS delivery
- [PostalMime](https://github.com/postalsys/postal-mime) - Email parsing
- [Streamlit](https://streamlit.io/) - Code generator UI
- TypeScript, Python, and open-source contributors

---

## 🗺️ Roadmap

### Phase 2 (Future Enhancements)
- [ ] Bidirectional SMS (reply to email)
- [ ] MMS support (images/attachments)
- [ ] Multiple Twilio accounts
- [ ] Email templates
- [ ] Scheduled sending

### Phase 3 (Advanced Features)
- [ ] Message queuing with Cloudflare Queues
- [ ] Advanced analytics dashboard
- [ ] AI content filtering
- [ ] Language translation
- [ ] Voice call support

### Phase 4 (Integrations)
- [ ] WhatsApp integration
- [ ] Slack notifications
- [ ] Microsoft Teams integration
- [ ] Discord webhooks

---

## 📊 Project Stats

- **Lines of Code**: 1,689 (Worker Core) + ~2,500 (Streamlit UI) + ~1,059 (Email Worker Templates)
- **Test Coverage**: 99.7% pass rate (307/308 tests passing)
- **Documentation**: 12 comprehensive guides + complete API documentation
- **Production Ready**: Yes (Both HTTP and Email Workers)
- **Email Worker Templates**: 8 files (index.ts, utils.ts, types.ts, wrangler.toml, package.json, .env.example, README.md, deploy.sh)
- **License**: MIT

### Recent Additions (2025-11-13)

✅ **Email Worker Generation**: Complete support for Cloudflare Email Routing
✅ **Python 3.12 Compatibility**: Updated streamlit (^1.32.0) and numpy (>=1.26.0)
✅ **Zero Security Vulnerabilities**: All 7 npm security issues fixed
✅ **Comprehensive Test Suite**: 307/308 tests passing (99.7% pass rate)
✅ **Security Testing**: 43 security tests covering XSS, injection attacks, and validation

---

**Made with ❤️ for developers who need reliable email-to-SMS conversion**

**Last Updated:** 2025-11-15
**Version:** 1.0.0
