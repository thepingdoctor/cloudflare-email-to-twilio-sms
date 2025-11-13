# Quick Start Guide - Email-to-SMS Code Generator

## 🚀 Get Started in 3 Minutes

### Option 1: Quick Start Script (Recommended)

```bash
cd streamlit-app
./run.sh
```

This will:
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Start the Streamlit app
- ✅ Open browser to http://localhost:8501

### Option 2: Manual Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app.py
```

### Option 3: Docker

```bash
# Build image
docker build -t email2sms-generator .

# Run container
docker run -p 8501:8501 email2sms-generator

# Access at: http://localhost:8501
```

## 📋 Using the Application

### Step 1: Basic Configuration

1. **Worker Name**: Enter a name like `my-email-sms`
2. **Domain**: Your domain (e.g., `example.com`)
3. **Email Pattern**: How emails are received (default: `*@sms.example.com`)

### Step 2: Twilio Credentials

1. Get credentials from [Twilio Console](https://console.twilio.com/)
2. Enter:
   - Account SID (starts with `AC`)
   - Auth Token
   - Phone Number (in E.164 format: `+15551234567`)

### Step 3: Customize Features (Optional)

Expand **Email Routing Options**:
- Choose how to extract phone numbers
- Set content source (email body, subject, etc.)
- Configure max message length

Expand **Advanced Features**:
- **Rate Limiting**: Prevent abuse
- **Logging**: Track messages
- **Security**: Whitelist senders
- **Retries**: Auto-retry failed sends
- **Integrations**: Error notifications

### Step 4: Generate Code

Click the big **🚀 Generate Code** button!

### Step 5: Download & Deploy

1. Click **📦 Download All Files (.zip)**
2. Extract the ZIP file
3. Follow the deployment instructions in the app

## 🎯 Example Configuration

Here's a working example to get you started:

**Basic Settings:**
```
Worker Name: my-email-sms
Domain: example.com
Email Pattern: *@sms.example.com
```

**How it Works:**
- Send email to: `15551234567@sms.example.com`
- Receives SMS at: `+15551234567`
- Message content: Email body (text only)

**Features Enabled:**
- ✅ Rate limiting (10 msgs/sender/hour)
- ✅ Analytics Engine logging
- ✅ Automatic retries (3 attempts)
- ✅ HTML stripping

## 🔧 Deployment Steps

After downloading your files:

```bash
# 1. Extract ZIP
unzip my-email-sms.zip
cd my-email-sms

# 2. Install dependencies
npm install

# 3. Set Twilio secrets
wrangler secret put TWILIO_ACCOUNT_SID
wrangler secret put TWILIO_AUTH_TOKEN
wrangler secret put TWILIO_PHONE_NUMBER

# 4. Deploy
npm run deploy
```

Then configure Email Routing in Cloudflare Dashboard:
1. Go to Email → Email Routing
2. Add your domain
3. Create routing rule:
   - Match: `*@sms.example.com`
   - Action: Send to Worker
   - Worker: `my-email-sms`

## 🧪 Testing

Send a test email:

```
To: 15551234567@sms.example.com
Subject: Test
Body: Hello from email-to-sms!
```

You should receive an SMS with the message content!

## 🆘 Troubleshooting

### App Won't Start

```bash
# Make sure you're using Python 3.11+
python3 --version

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### SMS Not Sending

1. Check logs: `wrangler tail`
2. Verify Twilio credentials
3. Check phone number format (must be E.164)
4. Verify Twilio account has balance

### Email Not Routing

1. Check Email Routing configuration in Cloudflare
2. Verify domain is added
3. Check routing rule matches email pattern
4. Ensure worker is deployed

## 📚 Next Steps

- Read the [README.md](README.md) for detailed documentation
- Check generated code for customization options
- Review [Cloudflare Workers docs](https://developers.cloudflare.com/workers/)
- Explore [Twilio SMS API](https://www.twilio.com/docs/sms)

## 💡 Tips

- **Start Simple**: Use default settings first, then customize
- **Test Locally**: Use `npm run dev` for local testing
- **Monitor Usage**: Enable Analytics Engine for insights
- **Secure Secrets**: Never commit `.env` files
- **Rate Limits**: Adjust based on your needs
- **Save Config**: Export configuration for reuse

## 🎉 You're Ready!

Happy generating! If you need help, check the resources above or open an issue.

---

Made with ❤️ using Streamlit, Cloudflare Workers, and Twilio
