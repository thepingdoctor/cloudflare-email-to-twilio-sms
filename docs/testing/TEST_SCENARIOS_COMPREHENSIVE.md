# Comprehensive Test Scenarios - Email2SMS System
**Tester Agent - Hive Mind QA**
**Date**: 2025-11-13
**Status**: Complete Test Design
**Coverage**: Installation, Configuration, Generation, Integration, Deployment, Security

---

## Table of Contents

1. [Installation Testing](#1-installation-testing)
2. [Configuration Testing](#2-configuration-testing)
3. [Generation Testing](#3-generation-testing)
4. [Integration Testing](#4-integration-testing)
5. [Deployment Testing](#5-deployment-testing)
6. [Security Testing](#6-security-testing)
7. [Performance Testing](#7-performance-testing)
8. [End-to-End Testing](#8-end-to-end-testing)

---

## 1. Installation Testing

### 1.1 Poetry Installation Tests

**Objective**: Verify Poetry environment setup works correctly

#### Test Scenario 1.1.1: Fresh Poetry Installation
```bash
# Test ID: INST-001
# Priority: HIGH
# Type: Installation

# Prerequisites:
- Clean Ubuntu/Debian system
- Python 3.11+ installed
- No existing Poetry installation

# Test Steps:
1. Install Poetry:
   curl -sSL https://install.python-poetry.org | python3 -

2. Verify installation:
   poetry --version
   # Expected: Poetry (version 1.7.0+)

3. Navigate to streamlit-app:
   cd /home/ruhroh/email2sms/streamlit-app

4. Install dependencies:
   poetry install

5. Verify environment:
   poetry run python --version
   # Expected: Python 3.11.x or 3.12.x

6. List installed packages:
   poetry show
   # Expected: streamlit, jinja2, pydantic, validators, phonenumbers, etc.

# Success Criteria:
✅ Poetry installs without errors
✅ Virtual environment created in .venv/
✅ All dependencies installed (30+ packages)
✅ No version conflicts
✅ Python version matches pyproject.toml constraints

# Failure Scenarios:
❌ Poetry installation fails → Check Python version
❌ Dependency conflicts → Review pyproject.toml
❌ Lock file mismatch → Run poetry lock --no-update
```

#### Test Scenario 1.1.2: Poetry Update Test
```bash
# Test ID: INST-002
# Priority: MEDIUM
# Type: Maintenance

# Prerequisites:
- Existing Poetry installation
- Project already initialized

# Test Steps:
1. Check for outdated packages:
   poetry show --outdated

2. Update dependencies:
   poetry update

3. Verify lockfile updated:
   git diff poetry.lock

4. Test application still works:
   poetry run streamlit run app.py &
   sleep 5
   curl http://localhost:8501
   kill %1

# Success Criteria:
✅ Dependencies update successfully
✅ No breaking changes introduced
✅ Application starts without errors
✅ Lock file reflects new versions

# Edge Cases:
⚠️ Major version updates may break compatibility
⚠️ Check CHANGELOG for breaking changes
```

#### Test Scenario 1.1.3: Dependencies Installation Validation
```bash
# Test ID: INST-003
# Priority: HIGH
# Type: Installation

# Test Steps:
1. Verify core dependencies installed:
   poetry run python -c "import streamlit; print(streamlit.__version__)"
   # Expected: 1.31.0

   poetry run python -c "import jinja2; print(jinja2.__version__)"
   # Expected: 3.1.3+

   poetry run python -c "import pydantic; print(pydantic.__version__)"
   # Expected: 2.6.0+

   poetry run python -c "import validators; print(validators.__version__)"
   # Expected: 0.22.0+

   poetry run python -c "import phonenumbers; print('OK')"
   # Expected: OK

2. Verify test dependencies:
   poetry run python -c "import pytest; print(pytest.__version__)"
   # Expected: 7.4.0+

3. Verify all imports in app.py work:
   poetry run python -c "from app import *"
   # Expected: No import errors

# Success Criteria:
✅ All core dependencies importable
✅ Versions match pyproject.toml specifications
✅ No missing module errors
✅ Test framework available
```

### 1.2 NPM Installation Tests (Worker)

#### Test Scenario 1.2.1: Worker Dependencies Installation
```bash
# Test ID: INST-004
# Priority: HIGH
# Type: Installation

# Prerequisites:
- Node.js 18+ installed
- npm 9+ installed

# Test Steps:
1. Navigate to project root:
   cd /home/ruhroh/email2sms

2. Install dependencies:
   npm install

3. Verify wrangler installed:
   npx wrangler --version
   # Expected: 3.x.x

4. Verify postal-mime installed:
   npm list postal-mime
   # Expected: postal-mime@2.x.x

5. Type check TypeScript:
   npm run typecheck
   # Expected: No errors

# Success Criteria:
✅ All npm packages installed
✅ No vulnerability warnings (or only low severity)
✅ Wrangler CLI functional
✅ TypeScript compiles without errors

# Common Issues:
❌ Node version too old → Upgrade to 18+
❌ npm package lock conflicts → Delete package-lock.json and reinstall
❌ TypeScript errors → Check src/ directory
```

---

## 2. Configuration Testing

### 2.1 UI Input Validation Tests

#### Test Scenario 2.1.1: Valid Configuration Inputs
```python
# Test ID: CONF-001
# Priority: HIGH
# Type: Validation

# Test Data:
valid_config = {
    "worker_name": "email-sms-prod",
    "domain": "example.com",
    "email_pattern": "*@sms.{domain}",
    "twilio_account_sid": "AC" + "x" * 32,
    "twilio_auth_token": "y" * 32,
    "twilio_phone_number": "+15551234567",
    "phone_extraction_method": "email_prefix",
    "max_message_length": 1600,
    "rate_limit_per_sender": 10,
    "rate_limit_per_recipient": 20
}

# Test Steps:
1. Open Streamlit UI
2. Enter all valid configuration values
3. Click "Validate Configuration" button
4. Verify no error messages displayed
5. Click "Generate Code" button
6. Verify success message appears

# Success Criteria:
✅ All inputs accepted without errors
✅ Validation passes
✅ Code generation succeeds
✅ 10 files generated
✅ Download button appears

# Validation Checks:
✅ Worker name: lowercase, hyphens only, 3-63 chars
✅ Domain: valid DNS format with TLD
✅ Email pattern: contains {domain} placeholder
✅ Twilio SID: starts with AC, 34 chars total
✅ Phone: E.164 format (+1XXXXXXXXXX)
✅ Message length: 160-1600 range
✅ Rate limits: positive integers
```

#### Test Scenario 2.1.2: Invalid Worker Name Validation
```python
# Test ID: CONF-002
# Priority: HIGH
# Type: Validation - Negative Test

# Invalid Worker Names to Test:
invalid_names = [
    "",                          # Empty
    "My Worker",                 # Spaces
    "worker_name",               # Underscores
    "WorkerName",                # Uppercase
    "ab",                        # Too short (< 3 chars)
    "a" * 64,                    # Too long (> 63 chars)
    "123-worker",                # Starts with number
    "-worker",                   # Starts with hyphen
    "worker-",                   # Ends with hyphen
    "<script>alert(1)</script>", # XSS attempt
    "../etc/passwd",             # Path traversal
    "worker; DROP TABLE users"   # SQL injection attempt
]

# Test Steps for Each Invalid Name:
1. Enter invalid worker name in UI
2. Attempt to proceed to next field or validate
3. Verify error message appears
4. Verify error message is specific and helpful
5. Verify code generation button is disabled

# Expected Error Messages:
✅ Empty → "Worker name is required"
✅ Spaces → "Worker name must contain only lowercase letters, numbers, and hyphens"
✅ Uppercase → "Worker name must be lowercase"
✅ Too short → "Worker name must be at least 3 characters"
✅ Too long → "Worker name must be at most 63 characters"
✅ Invalid format → "Worker name must start with a letter"
✅ Security payload → "Worker name contains invalid characters"

# Success Criteria:
✅ Each invalid input rejected
✅ Specific error message shown
✅ User cannot proceed with invalid input
✅ No XSS/injection payloads accepted
```

#### Test Scenario 2.1.3: Phone Number Format Validation
```python
# Test ID: CONF-003
# Priority: HIGH
# Type: Validation

# Valid Phone Numbers (E.164):
valid_phones = [
    "+15551234567",      # US
    "+442071234567",     # UK
    "+33123456789",      # France
    "+81312345678",      # Japan
    "+61212345678",      # Australia
    "+8613812345678"     # China
]

# Invalid Phone Numbers:
invalid_phones = [
    "5551234567",        # Missing +
    "+1555123",          # Too short
    "+1 555 123 4567",   # Spaces
    "(555) 123-4567",    # US format (not E.164)
    "+0001234567",       # Invalid country code
    "+15551234567x123",  # Extension
    "",                  # Empty
    "abc",               # Non-numeric
    "+1-555-123-4567"    # Dashes
]

# Test Steps:
1. For each valid phone:
   - Enter in Twilio phone number field
   - Verify NO error message
   - Verify green checkmark or success indicator

2. For each invalid phone:
   - Enter in phone number field
   - Verify error message appears
   - Verify specific guidance provided
   - Verify cannot generate code

# Success Criteria:
✅ All valid E.164 formats accepted
✅ All invalid formats rejected
✅ Error messages explain E.164 requirement
✅ Examples provided in help text
```

#### Test Scenario 2.1.4: Email Pattern Validation
```python
# Test ID: CONF-004
# Priority: MEDIUM
# Type: Validation

# Valid Email Patterns:
valid_patterns = [
    "*@sms.{domain}",           # Catch-all with domain
    "sms-*@{domain}",           # Prefix wildcard
    "*@test.{domain}",          # Subdomain
    "notify+*@{domain}",        # Plus addressing
    "{phone}@sms.{domain}"      # Phone placeholder
]

# Invalid Email Patterns:
invalid_patterns = [
    "",                         # Empty
    "not-an-email",            # No @ symbol
    "@{domain}",               # Missing local part
    "*@",                      # Missing domain
    "*@domain.com",            # Hardcoded domain (should use {domain})
    "**@{domain}",             # Multiple wildcards
    "*@{invalid}",             # Invalid placeholder
    "<script>@{domain}"        # XSS attempt
]

# Test Steps:
1. Enter each valid pattern
2. Verify accepted
3. Verify {domain} placeholder replaced correctly in preview
4. Enter each invalid pattern
5. Verify rejected with helpful message

# Success Criteria:
✅ Valid patterns accepted
✅ {domain} placeholder validated
✅ Invalid patterns rejected
✅ Clear error messages
✅ Preview shows actual email address
```

### 2.2 Credential Validation Tests

#### Test Scenario 2.2.1: Twilio Credentials Format Validation
```python
# Test ID: CONF-005
# Priority: HIGH
# Type: Security - Credential Validation

# Valid Twilio Account SID:
valid_sids = [
    "AC" + "a" * 32,  # Exactly 34 characters, starts with AC
    "AC1234567890abcdef1234567890abcdef"  # Real format example
]

# Invalid Twilio Account SID:
invalid_sids = [
    "",                                    # Empty
    "AC123",                              # Too short
    "AB" + "a" * 32,                      # Wrong prefix
    "1234567890abcdef1234567890abcdef",   # Missing AC prefix
    "AC" + "a" * 50,                      # Too long
    "AC<script>alert(1)</script>xxxxxx"   # XSS
]

# Valid Auth Tokens:
valid_tokens = [
    "a" * 32,   # Minimum 32 characters
    "x" * 40,   # Longer token
    "1234567890abcdef1234567890abcdef"  # Alphanumeric
]

# Invalid Auth Tokens:
invalid_tokens = [
    "",              # Empty
    "abc",           # Too short (< 32)
    "token with spaces",  # Spaces
    "token\nwith\nnewlines"  # Newlines
]

# Test Steps:
1. Test valid SIDs accepted
2. Test invalid SIDs rejected
3. Test valid tokens accepted
4. Test invalid tokens rejected
5. Verify credentials not logged or displayed in clear text
6. Verify credentials marked as sensitive (password fields)

# Success Criteria:
✅ SID format validated (AC + 32 chars)
✅ Token length validated (≥ 32 chars)
✅ Credentials masked in UI
✅ Credentials not in generated code (only .env.example)
✅ Security payloads rejected
```

#### Test Scenario 2.2.2: Secure Credential Storage Test
```python
# Test ID: CONF-006
# Priority: CRITICAL
# Type: Security

# Test Steps:
1. Generate code with real Twilio credentials
2. Download generated ZIP file
3. Extract and examine ALL files
4. Search for actual credential values

# Files to Check:
files_to_check = [
    "src/index.ts",
    "wrangler.toml",
    "package.json",
    "README.md",
    ".env.example",
    "deploy.sh"
]

# Search Commands:
for file in files_to_check:
    grep -i "AC1234567890abcdef" $file
    grep -i "actual_auth_token" $file
    grep -i "+15551234567" $file

# Success Criteria:
✅ NO actual credentials in any generated file
✅ .env.example contains only placeholders
✅ wrangler.toml references secrets via binding
✅ README instructs to use wrangler secret put
✅ deploy.sh doesn't contain credentials
✅ All credential references use environment variables

# Expected Placeholders:
- env.TWILIO_ACCOUNT_SID (NOT actual SID)
- env.TWILIO_AUTH_TOKEN (NOT actual token)
- env.TWILIO_PHONE_NUMBER (NOT actual number)

# Failure Scenario:
❌ If ANY actual credential found in generated code → CRITICAL SECURITY ISSUE
```

### 2.3 Error Handling Tests

#### Test Scenario 2.3.1: Invalid Input Error Messages
```python
# Test ID: CONF-007
# Priority: HIGH
# Type: User Experience

# Test Multiple Validation Errors Simultaneously:
invalid_config = {
    "worker_name": "",                    # Empty (error 1)
    "domain": "invalid domain com",       # Invalid format (error 2)
    "email_pattern": "no-at-sign",       # Missing @ (error 3)
    "twilio_account_sid": "INVALID",     # Wrong format (error 4)
    "twilio_auth_token": "short",        # Too short (error 5)
    "twilio_phone_number": "555-1234",   # Invalid format (error 6)
    "max_message_length": 50             # Too small (error 7)
}

# Test Steps:
1. Enter all invalid values
2. Attempt to validate or generate
3. Verify ALL errors shown (not just first one)
4. Verify each error is specific
5. Verify errors are color-coded or highlighted
6. Fix each error one by one
7. Verify error disappears when fixed

# Success Criteria:
✅ All 7 errors displayed simultaneously
✅ Each error message is clear and actionable
✅ Errors indicate which field and why invalid
✅ Errors disappear when corrected
✅ Can proceed only when all errors resolved
✅ Error summary count shown (e.g., "7 errors found")

# Example Expected Errors:
1. "Worker name is required"
2. "Domain must be a valid DNS name (no spaces)"
3. "Email pattern must contain @ symbol"
4. "Twilio Account SID must start with 'AC' and be 34 characters"
5. "Twilio Auth Token must be at least 32 characters"
6. "Phone number must be in E.164 format (e.g., +15551234567)"
7. "Max message length must be between 160 and 1600 characters"
```

---

## 3. Generation Testing

### 3.1 Worker Script Generation Tests

#### Test Scenario 3.1.1: Email Worker Code Generation
```bash
# Test ID: GEN-001
# Priority: CRITICAL
# Type: Code Generation

# Test Configuration:
config = {
    "worker_type": "email",
    "worker_name": "test-email-worker",
    "domain": "example.com",
    "email_pattern": "*@sms.{domain}",
    "phone_extraction_method": "email_prefix"
}

# Test Steps:
1. Configure email worker in Streamlit UI
2. Click "Generate Code"
3. Verify files generated

# Expected Files (10 files):
expected_files = [
    "src/index.ts",       # Main email worker
    "src/types.ts",       # TypeScript types
    "src/utils.ts",       # Utility functions
    "wrangler.toml",      # Cloudflare config
    "package.json",       # Dependencies
    "tsconfig.json",      # TypeScript config
    ".env.example",       # Environment template
    ".gitignore",         # Git ignore rules
    "README.md",          # Documentation
    "deploy.sh"           # Deployment script
]

# Validation Checks for src/index.ts:
✅ Contains: import { EmailMessage } from 'cloudflare:email'
✅ Contains: export default { async email(message, env, ctx) {
✅ Contains: extractPhoneNumber() function
✅ Contains: Twilio API integration
✅ Contains: env.TWILIO_ACCOUNT_SID reference
✅ Contains: Error handling try/catch blocks
✅ File size: 6,000-8,000 characters
✅ Valid TypeScript syntax (no errors when compiled)

# Validation Checks for wrangler.toml:
✅ Contains: name = "test-email-worker"
✅ Contains: main = "src/index.ts"
✅ Contains: [email] section
✅ Contains: [[email.route]] with pattern
✅ References secrets (not actual values)
✅ Valid TOML format (parseable)

# Success Criteria:
✅ All 10 files generated
✅ No placeholder values left (e.g., {{variable}})
✅ All variable substitutions correct
✅ TypeScript compiles without errors
✅ TOML is valid
✅ JSON is valid
```

#### Test Scenario 3.1.2: Generated Code Syntax Validation
```bash
# Test ID: GEN-002
# Priority: HIGH
# Type: Code Quality

# Test Steps:
1. Generate email worker code
2. Download ZIP and extract
3. Validate syntax for each file type

# TypeScript Validation:
cd generated-worker
npm install
npx tsc --noEmit
# Expected: No errors

# TOML Validation (wrangler.toml):
npx wrangler dev --dry-run
# Expected: Configuration valid

# JSON Validation (package.json, tsconfig.json):
node -e "JSON.parse(require('fs').readFileSync('package.json'))"
node -e "JSON.parse(require('fs').readFileSync('tsconfig.json'))"
# Expected: No errors

# Bash Script Validation (deploy.sh):
bash -n deploy.sh
# Expected: No syntax errors

# Success Criteria:
✅ TypeScript: No compilation errors
✅ TOML: Wrangler accepts configuration
✅ JSON: All JSON files parse successfully
✅ Bash: deploy.sh has valid syntax
✅ No template syntax left in files ({{, }}, {% %})
```

#### Test Scenario 3.1.3: Twilio Integration Code Validation
```typescript
// Test ID: GEN-003
// Priority: CRITICAL
// Type: Integration

// Test Steps:
// 1. Generate worker with all Twilio features enabled
// 2. Examine src/index.ts for Twilio integration

// Required Code Elements:
const required_elements = [
  // Environment variables
  "env.TWILIO_ACCOUNT_SID",
  "env.TWILIO_AUTH_TOKEN",
  "env.TWILIO_PHONE_NUMBER",

  // API endpoint
  "https://api.twilio.com/2010-04-01/Accounts",
  "/Messages.json",

  // Authentication
  "Authorization: Basic",
  "btoa(", // Base64 encoding

  // Request parameters
  "From: env.TWILIO_PHONE_NUMBER",
  "To: phoneNumber",
  "Body: messageContent",

  // Error handling
  "try {",
  "catch (error) {",
  "response.status",

  // Retry logic (if enabled)
  "for (let attempt = 0",
  "maxRetries",
  "await sleep("
];

// Validation:
for (const element of required_elements) {
  // Verify element exists in generated src/index.ts
  // grep -F "$element" src/index.ts
}

// Success Criteria:
✅ All required code elements present
✅ Twilio API endpoint correct
✅ Authentication properly implemented
✅ All required parameters included
✅ Error handling comprehensive
✅ Retry logic present (if configured)
```

### 3.2 Configuration File Generation Tests

#### Test Scenario 3.2.1: wrangler.toml Completeness
```toml
# Test ID: GEN-004
# Priority: HIGH
# Type: Configuration

# Generated wrangler.toml Must Contain:

# 1. Basic Configuration:
name = "test-email-worker"  # ✅ Worker name
main = "src/index.ts"        # ✅ Entry point
compatibility_date = "2024-11-13"  # ✅ Date

# 2. Email Routing Section:
[email]
  # ✅ Email section must exist

# 3. Email Route:
[[email.route]]
pattern = "*@sms.example.com"  # ✅ Configured pattern
action = "Worker"              # ✅ Worker action

# 4. Environment Variables (not secrets):
[vars]
ALLOWED_SENDERS = "*@example.com"  # ✅ If configured
DEFAULT_COUNTRY_CODE = "1"         # ✅ If configured

# 5. KV Namespace (if rate limiting enabled):
[[kv_namespaces]]
binding = "EMAIL_SMS_KV"  # ✅ Binding name
id = ""                   # ✅ Placeholder for ID

# 6. Analytics Engine (if logging enabled):
[[analytics_engine_datasets]]
binding = "EMAIL_ANALYTICS"  # ✅ If configured

# Validation Commands:
npx wrangler dev --dry-run  # ✅ Must pass
toml-validator wrangler.toml  # ✅ Valid TOML

# Success Criteria:
✅ All required sections present
✅ Variables correctly substituted
✅ No template syntax remaining
✅ Wrangler validates configuration
✅ Email routing section configured
```

#### Test Scenario 3.2.2: package.json Dependencies
```json
// Test ID: GEN-005
// Priority: HIGH
// Type: Dependencies

// Required Dependencies in package.json:
{
  "dependencies": {
    "postal-mime": "^2.3.0"  // ✅ Email parsing
  },
  "devDependencies": {
    "@cloudflare/workers-types": "*",  // ✅ Type definitions
    "typescript": "^5.0.0",            // ✅ TypeScript compiler
    "wrangler": "^3.0.0"               // ✅ Deployment tool
  },
  "scripts": {
    "dev": "wrangler dev",                    // ✅ Local development
    "deploy": "wrangler deploy",              // ✅ Deployment
    "deploy:production": "wrangler deploy",   // ✅ Production deploy
    "typecheck": "tsc --noEmit",             // ✅ Type checking
    "tail": "wrangler tail"                   // ✅ Log streaming
  }
}

// Validation:
npm install  // ✅ Must succeed
npm run typecheck  // ✅ Must pass
npm list postal-mime  // ✅ Must be installed

// Success Criteria:
✅ All required dependencies listed
✅ Versions specified or wildcarded
✅ All npm scripts functional
✅ No missing dependencies when installing
```

### 3.3 Deployment Guide Generation Tests

#### Test Scenario 3.3.1: README.md Completeness
```markdown
# Test ID: GEN-006
# Priority: MEDIUM
# Type: Documentation

# Generated README.md Must Include:

## 1. Project Overview Section
✅ Worker name (personalized)
✅ Purpose description
✅ Key features list

## 2. Prerequisites Section
✅ Cloudflare account requirement
✅ Twilio account requirement
✅ Node.js version requirement (18+)
✅ npm version requirement

## 3. Installation Section
✅ npm install command
✅ .env.example usage instructions
✅ Secret configuration steps

## 4. Configuration Section
✅ wrangler.toml configuration
✅ Account ID instructions
✅ Email routing pattern explanation

## 5. Deployment Section
✅ Local testing command (npm run dev)
✅ Production deployment command
✅ Email routing setup steps
✅ MX record verification

## 6. Testing Section
✅ How to send test email
✅ Expected email format
✅ How to verify SMS received
✅ Log monitoring command

## 7. Troubleshooting Section
✅ Common issues
✅ Error messages
✅ Debugging commands

# Validation:
- Word count: >500 words
- Code examples: >5 examples
- Links: All functional (if any)
- Personalization: Worker name appears 5+ times

# Success Criteria:
✅ All 7 sections present
✅ Specific to generated configuration
✅ Clear, actionable instructions
✅ Examples included
✅ No generic placeholders remaining
```

---

## 4. Integration Testing

### 4.1 Cloudflare API Integration Tests

#### Test Scenario 4.1.1: Email Routing API Integration
```typescript
// Test ID: INT-001
// Priority: CRITICAL
// Type: Integration

// Test Prerequisites:
// - Cloudflare account with domain
// - Email Routing enabled
// - Worker deployed

// Test Steps:
1. Configure email routing pattern in Cloudflare Dashboard
   Pattern: *@sms.example.com
   Action: Send to Worker (test-email-worker)

2. Verify MX records configured:
   dig MX example.com
   // Expected: isaac.mx.cloudflare.net, linda.mx.cloudflare.net

3. Send test email:
   To: 15551234567@sms.example.com
   Subject: Test Email Routing
   Body: This is a test message

4. Monitor worker logs:
   npm run tail

5. Verify email received by worker:
   // Look for log: "Email received from: sender@example.com"
   // Look for log: "Phone extracted: +15551234567"

// Success Criteria:
✅ Email routed to worker
✅ Worker email() handler invoked
✅ EmailMessage object parsed
✅ Phone number extracted correctly
✅ No routing errors

// Failure Scenarios:
❌ Email bounces → Check MX records
❌ Worker not invoked → Verify routing rule
❌ Parse error → Check EmailMessage import
```

#### Test Scenario 4.1.2: Worker Deployment Validation
```bash
# Test ID: INT-002
# Priority: HIGH
# Type: Deployment

# Test Steps:
1. Deploy worker:
   npm run deploy:production
   # Expected output: Published test-email-worker

2. Verify deployment:
   npx wrangler deployments list
   # Expected: Recent deployment listed

3. Check worker status:
   curl https://test-email-worker.your-account.workers.dev
   # Expected: 405 Method Not Allowed (email worker doesn't handle HTTP)

4. Verify secrets set:
   npx wrangler secret list
   # Expected: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER

5. Test worker with wrangler dev:
   npx wrangler dev
   # Expected: Worker starts on localhost:8787

# Success Criteria:
✅ Worker deploys successfully
✅ Deployment shows in dashboard
✅ All secrets configured
✅ Worker accessible (even if returns 405)
✅ wrangler dev works locally
```

### 4.2 Twilio API Integration Tests

#### Test Scenario 4.2.1: SMS Sending Integration
```typescript
// Test ID: INT-003
// Priority: CRITICAL
// Type: Integration

// Test Prerequisites:
// - Twilio account active
// - Phone number verified
// - Sufficient balance

// Mock Twilio API Call:
const twilioRequest = {
  method: 'POST',
  url: `https://api.twilio.com/2010-04-01/Accounts/${accountSid}/Messages.json`,
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Authorization': `Basic ${btoa(accountSid + ':' + authToken)}`
  },
  body: new URLSearchParams({
    From: '+15551234567',    // Twilio number
    To: '+15559876543',      // Recipient
    Body: 'Test message'     // Content
  })
};

// Test Steps:
1. Send email that triggers SMS:
   To: 15559876543@sms.example.com
   Body: Test SMS via email

2. Monitor worker logs for Twilio API call:
   npm run tail | grep -i twilio

3. Check Twilio Console:
   - Log in to Twilio Dashboard
   - Navigate to Messaging → Logs
   - Verify message sent

4. Verify SMS received on phone +15559876543

// Success Criteria:
✅ Worker calls Twilio API
✅ API returns 200 OK or 201 Created
✅ Message SID returned (SM...)
✅ SMS delivered to recipient phone
✅ Twilio logs show "delivered" status

// Error Scenarios to Test:
❌ Invalid phone number → Expect 400 error
❌ Insufficient balance → Expect 403 error
❌ Invalid credentials → Expect 401 error
❌ Network timeout → Expect retry logic
```

#### Test Scenario 4.2.2: Authentication Flow Validation
```typescript
// Test ID: INT-004
// Priority: HIGH
// Type: Security - Authentication

// Test Valid Credentials:
const validAuth = {
  accountSid: 'AC' + 'x'.repeat(32),  // Valid format
  authToken: 'y'.repeat(32)            // Valid format
};

// Test Steps:
1. Configure worker with valid Twilio credentials
2. Send test email
3. Monitor API calls
4. Verify Basic Auth header constructed correctly:
   const expectedAuth = btoa(`${accountSid}:${authToken}`);
   // Header: Authorization: Basic ${expectedAuth}

// Test Invalid Credentials:
const invalidAuth = {
  accountSid: 'INVALID',
  authToken: 'WRONG'
};

// Test Steps:
1. Temporarily set invalid credentials
2. Send test email
3. Expect Twilio 401 Unauthorized error
4. Verify error logged properly
5. Verify no SMS sent

// Success Criteria:
✅ Valid credentials: API call succeeds
✅ Invalid credentials: 401 error returned
✅ Auth header correctly formatted
✅ Credentials never logged in plain text
✅ Error handling graceful
```

### 4.3 Webhook Configuration Tests

#### Test Scenario 4.3.1: Email-to-SMS End-to-End Flow
```gherkin
# Test ID: INT-005
# Priority: CRITICAL
# Type: End-to-End

Feature: Email-to-SMS Conversion
  As a user
  I want to send an SMS by emailing a special address
  So that I can use email clients to send text messages

Scenario: Successful email-to-SMS conversion
  Given the worker is deployed and running
  And email routing is configured for *@sms.example.com
  And Twilio credentials are valid
  When I send an email:
    | Field   | Value                        |
    | To      | 15551234567@sms.example.com |
    | From    | user@example.com            |
    | Subject | Test Message                 |
    | Body    | Hello from email!            |
  Then the worker receives the email within 30 seconds
  And the phone number +15551234567 is extracted
  And a Twilio API call is made
  And an SMS is sent to +15551234567
  And the SMS content is "From: user@example.com\nRe: Test Message\nHello from email!"
  And the recipient receives the SMS within 60 seconds

Scenario: Invalid phone number in email address
  Given the worker is deployed
  When I send an email to "invalid@sms.example.com"
  Then the worker attempts to extract a phone number
  And extraction fails
  And an error is logged
  And NO Twilio API call is made
  And NO SMS is sent

Scenario: Rate limit exceeded
  Given the worker has rate limiting enabled
  And sender user@example.com has sent 10 messages in the last hour
  When I send an 11th email from user@example.com
  Then the worker checks the rate limit
  And the rate limit is exceeded
  And the email is rejected
  And a rejection message is logged
  And NO SMS is sent
```

---

## 5. Deployment Testing

### 5.1 Deployment Checklist Validation

#### Test Scenario 5.1.1: Complete Deployment Workflow
```bash
# Test ID: DEPLOY-001
# Priority: CRITICAL
# Type: Deployment

# Full Deployment Checklist:

## Prerequisites (verify before starting):
□ Cloudflare account created
□ Domain added to Cloudflare
□ Twilio account active
□ Twilio phone number purchased
□ Node.js 18+ installed (node --version)
□ npm 9+ installed (npm --version)

## Step 1: Clone and Install
□ git clone <repo-url>
□ cd email2sms
□ npm install
□ Verify: node_modules/ created
□ Verify: package-lock.json created

## Step 2: Configuration
□ cp .dev.vars.example .dev.vars
□ Edit .dev.vars with Twilio credentials
□ Edit config/wrangler.toml with account_id
□ Verify: No syntax errors in wrangler.toml

## Step 3: Local Testing
□ npm run dev
□ Verify: Worker starts on localhost:8787
□ Verify: No errors in console
□ Stop dev server (Ctrl+C)

## Step 4: Production Secrets
□ npx wrangler secret put TWILIO_ACCOUNT_SID
□ npx wrangler secret put TWILIO_AUTH_TOKEN
□ npx wrangler secret put TWILIO_PHONE_NUMBER
□ Verify: npx wrangler secret list shows all 3

## Step 5: KV Namespace (Optional)
□ npm run kv:create
□ Copy KV namespace ID
□ Add to wrangler.toml [[kv_namespaces]] section
□ Verify: wrangler.toml has KV binding

## Step 6: Deploy Worker
□ npm run deploy:production
□ Verify: "Published test-email-worker" message
□ Verify: Worker URL shown
□ npx wrangler deployments list
□ Verify: Recent deployment listed

## Step 7: Email Routing Setup
□ Open Cloudflare Dashboard
□ Navigate to domain → Email Routing
□ Click "Enable Email Routing"
□ Wait for MX records (automatic)
□ Create routing rule: *@sms.example.com → Worker
□ Verify: dig MX example.com shows Cloudflare MX

## Step 8: Testing
□ Send test email to 15551234567@sms.example.com
□ Monitor logs: npm run tail
□ Verify: Email received log entry
□ Verify: Phone extracted log entry
□ Verify: Twilio API call log
□ Check phone for SMS
□ Verify: SMS received with correct content

## Step 9: Verification
□ Check Cloudflare Dashboard → Workers → Metrics
□ Verify: Request count increased
□ Check Twilio Console → Messaging → Logs
□ Verify: Message sent and delivered
□ Verify: No errors in worker logs

# Success Criteria:
✅ All 9 steps completed without errors
✅ Worker deployed and accessible
✅ Email routing functional
✅ SMS sending working
✅ Logs show success
✅ Total deployment time: <2 hours
```

### 5.2 Smoke Tests Post-Deployment

#### Test Scenario 5.2.1: Basic Smoke Test
```bash
# Test ID: DEPLOY-002
# Priority: HIGH
# Type: Smoke Test

# Smoke Test (5 minutes after deployment):

## 1. Worker Availability
curl https://test-email-worker.your-account.workers.dev
# Expected: 405 Method Not Allowed (acceptable for email worker)

## 2. Email Routing
dig MX example.com
# Expected: Cloudflare MX records present

## 3. Worker Logs Accessible
npm run tail &
sleep 5
kill %1
# Expected: Log stream starts without errors

## 4. Send Test Email
Send email to: test@sms.example.com
Subject: Smoke Test
Body: Quick deployment verification

## 5. Monitor for Success
npm run tail | grep -i "email received"
# Expected: Log entry within 60 seconds

# Success Criteria:
✅ Worker responds (even if 405)
✅ MX records active
✅ Logs accessible
✅ Email processed
✅ No critical errors

# If ANY smoke test fails:
❌ STOP - Do not proceed to production
❌ Investigate failure
❌ Fix issue
❌ Redeploy
❌ Re-run smoke tests
```

### 5.3 Troubleshooting Validation

#### Test Scenario 5.3.1: Common Issues Resolution
```bash
# Test ID: DEPLOY-003
# Priority: MEDIUM
# Type: Troubleshooting

# Issue 1: Email Not Processing
Symptom: Email sent but no SMS received, no logs

Troubleshooting Steps:
□ Verify MX records: dig MX example.com
  Expected: Cloudflare MX servers

□ Check email routing rules in dashboard
  Expected: Pattern matches email sent

□ Verify worker is selected in routing rule
  Expected: test-email-worker selected

□ Check worker logs: npm run tail
  Expected: Some log activity (even if errors)

□ Verify email address matches pattern
  Expected: Email matches *@sms.example.com

Resolution:
If MX wrong → Wait for DNS propagation (up to 24hrs)
If pattern wrong → Update routing rule
If worker wrong → Select correct worker
If no logs → Worker may not be deployed

# Issue 2: SMS Not Sending
Symptom: Email processed, logs show success, but no SMS

Troubleshooting Steps:
□ Verify Twilio credentials: npx wrangler secret list
  Expected: All 3 secrets present

□ Check Twilio account balance
  Expected: Sufficient funds

□ Check Twilio Console → Messaging → Logs
  Expected: API call logged (even if failed)

□ Verify phone number format in email
  Expected: E.164 format (+15551234567)

□ Check worker logs for Twilio errors
  Expected: Error code if API call failed

Resolution:
If secrets missing → Re-run wrangler secret put
If no balance → Add funds to Twilio
If API error → Check error code in Twilio logs
If phone invalid → Use E.164 format

# Issue 3: Rate Limit Errors
Symptom: "Rate limit exceeded" in logs

Troubleshooting Steps:
□ Check rate limit counter:
  npx wrangler kv:key get "rate:sender:user@example.com" --binding EMAIL_SMS_KV
  Expected: Count < limit

□ Verify rate limit configuration in wrangler.toml
  Expected: Reasonable limits set

□ Check timestamp of last reset
  Expected: Within configured window

Resolution:
If limit too low → Increase in wrangler.toml and redeploy
If counter stuck → Manually reset KV key
If legitimate traffic → Whitelist sender or increase limit

# Success Criteria:
✅ All common issues documented
✅ Troubleshooting steps clear
✅ Resolutions actionable
✅ User can self-diagnose issues
```

---

## 6. Security Testing

### 6.1 Credential Security Tests

#### Test Scenario 6.1.1: Secrets Not Exposed
```bash
# Test ID: SEC-001
# Priority: CRITICAL
# Type: Security

# Test: Verify no secrets in generated code

# Secrets to Check For:
ACTUAL_SID="AC1234567890abcdef1234567890abcdef"
ACTUAL_TOKEN="abc123def456ghi789"
ACTUAL_PHONE="+15551234567"

# Files to Audit:
files=(
  "src/index.ts"
  "src/types.ts"
  "src/utils.ts"
  "wrangler.toml"
  "package.json"
  "tsconfig.json"
  ".env.example"
  "README.md"
  "deploy.sh"
)

# Automated Check:
for file in "${files[@]}"; do
  if grep -q "$ACTUAL_SID" "$file"; then
    echo "❌ CRITICAL: Twilio SID found in $file"
    exit 1
  fi

  if grep -q "$ACTUAL_TOKEN" "$file"; then
    echo "❌ CRITICAL: Twilio token found in $file"
    exit 1
  fi

  if grep -q "$ACTUAL_PHONE" "$file"; then
    echo "❌ CRITICAL: Phone number found in $file"
    exit 1
  fi
done

echo "✅ PASS: No secrets found in generated code"

# Additional Checks:
□ Verify .dev.vars in .gitignore
□ Verify .env.example uses placeholders only
□ Verify README instructs wrangler secret put
□ Verify deploy.sh doesn't contain secrets
□ Verify git log doesn't contain secrets

# Success Criteria:
✅ No actual credentials in ANY file
✅ Only environment variable references
✅ .gitignore prevents .dev.vars commit
✅ Documentation promotes secret management
```

#### Test Scenario 6.1.2: Environment Variable Security
```typescript
// Test ID: SEC-002
// Priority: HIGH
// Type: Security

// Test: Verify secrets accessed via environment only

// Code Pattern Analysis:
const securityPatterns = {
  // ✅ CORRECT patterns:
  correct: [
    "env.TWILIO_ACCOUNT_SID",
    "env.TWILIO_AUTH_TOKEN",
    "env.TWILIO_PHONE_NUMBER",
    "process.env.TWILIO_ACCOUNT_SID"  // Alternative
  ],

  // ❌ FORBIDDEN patterns:
  forbidden: [
    '"AC' + 'a'.repeat(32) + '"',  // Hardcoded SID
    "'AC1234567890abcdef'",          // Hardcoded SID variant
    "const accountSid = 'AC",        // Variable assignment
    "TWILIO_ACCOUNT_SID: 'AC",       // Object property
    "+15551234567"                   // Hardcoded phone
  ]
};

// Validation:
const indexTs = fs.readFileSync('src/index.ts', 'utf8');

// Verify CORRECT patterns present:
for (const pattern of securityPatterns.correct) {
  if (!indexTs.includes(pattern)) {
    console.log(`⚠️  Pattern not found: ${pattern}`);
  }
}

// Verify FORBIDDEN patterns absent:
for (const pattern of securityPatterns.forbidden) {
  if (indexTs.includes(pattern)) {
    console.log(`❌ SECURITY ISSUE: Forbidden pattern found: ${pattern}`);
    process.exit(1);
  }
}

// Success Criteria:
✅ All credentials accessed via env object
✅ No hardcoded values
✅ TypeScript types enforce env usage
✅ No string concatenation of secrets
```

### 6.2 Input Validation Security

#### Test Scenario 6.2.1: XSS Payload Rejection
```python
# Test ID: SEC-003
# Priority: HIGH
# Type: Security - XSS Prevention

# XSS Payloads to Test:
xss_payloads = [
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert(1)>",
    "javascript:alert('XSS')",
    "<svg onload=alert('XSS')>",
    "';alert('XSS');//",
    "<iframe src='javascript:alert(1)'>",
    "<<SCRIPT>alert('XSS');//<</SCRIPT>",
    "<BODY ONLOAD=alert('XSS')>",
    "\"><script>alert(String.fromCharCode(88,83,83))</script>",
    "<input type='text' value='<script>alert(1)</script>'>"
]

# Fields to Test:
fields_to_test = [
    "worker_name",
    "domain",
    "email_pattern",
    "custom_response_message",
    "sender_whitelist"
]

# Test Procedure:
for payload in xss_payloads:
    for field in fields_to_test:
        # 1. Enter XSS payload in field
        # 2. Attempt to submit/validate
        # 3. Verify payload rejected
        # 4. Verify error message shown
        # 5. Generate code (if allowed)
        # 6. Verify payload sanitized/escaped in output
        pass

# Success Criteria:
✅ All XSS payloads rejected at input validation
✅ OR payloads properly escaped in output
✅ Generated code doesn't execute payload
✅ Error messages don't reflect payload back unsanitized
✅ No JavaScript execution in any context

# Example Validation:
worker_name_input = "<script>alert(1)</script>"
# Expected error: "Worker name contains invalid characters"
# NOT: "Worker name <script>alert(1)</script> is invalid" (reflected XSS)
```

#### Test Scenario 6.2.2: SQL Injection Attempt Handling
```python
# Test ID: SEC-004
# Priority: MEDIUM
# Type: Security - SQL Injection

# SQL Injection Payloads:
sql_payloads = [
    "'; DROP TABLE users; --",
    "1' OR '1'='1",
    "admin'--",
    "' OR 1=1--",
    "'; EXEC sp_MSForEachTable 'DROP TABLE ?'; --",
    "1; DELETE FROM users WHERE '1'='1",
    "' UNION SELECT NULL, NULL, NULL--",
    "1' AND '1'='1"
]

# Test Fields:
for payload in sql_payloads:
    # Test in worker name field
    submit_form(worker_name=payload)
    # Expected: Validation error, not SQL execution

    # Test in whitelist field
    submit_form(sender_whitelist=payload)
    # Expected: Email validation error

# Success Criteria:
✅ All SQL payloads rejected
✅ No database operations (this app doesn't use DB)
✅ Payloads treated as invalid strings
✅ No code evaluation

# Note: This app doesn't use SQL, but testing ensures
# no SQL is accidentally introduced and payloads are
# properly sanitized
```

#### Test Scenario 6.2.3: Path Traversal Prevention
```python
# Test ID: SEC-005
# Priority: HIGH
# Type: Security - Path Traversal

# Path Traversal Payloads:
path_payloads = [
    "../../../etc/passwd",
    "..\\..\\..\\windows\\system32\\config\\sam",
    "....//....//....//etc/passwd",
    "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
    "../../../../../../../../../../etc/passwd",
    "../../../var/www/html/config.php",
    "....\\\\....\\\\....\\\\windows\\\\win.ini"
]

# Test in filename-related fields:
for payload in path_payloads:
    # Test worker name (used for file generation)
    result = validate_worker_name(payload)
    # Expected: Rejected

    # Test domain (used for file generation)
    result = validate_domain(payload)
    # Expected: Rejected

    # Attempt to generate files with payload
    try:
        generate_files(worker_name=payload)
    except ValueError:
        # Expected: Validation error before file creation
        pass

# Validation After Generation:
# Verify all generated files are in expected directory
# Verify no files created outside working directory
# Verify no symlinks created

# Success Criteria:
✅ Path traversal characters rejected
✅ All files generated in safe directory
✅ No files created outside project directory
✅ No symlinks or hardlinks created
✅ Filename sanitization prevents traversal
```

### 6.3 Rate Limiting Security

#### Test Scenario 6.3.1: Rate Limit Enforcement
```typescript
// Test ID: SEC-006
// Priority: HIGH
// Type: Security - Rate Limiting

// Test Configuration:
const rateLimitConfig = {
  perSender: 10,      // 10 emails per sender per hour
  perRecipient: 20,   // 20 emails per recipient per hour
  globalLimit: 1000   // 1000 emails per hour total
};

// Test Per-Sender Rate Limit:
async function testSenderRateLimit() {
  const sender = 'test@example.com';

  // Send 10 emails (should succeed)
  for (let i = 0; i < 10; i++) {
    const result = await sendEmail(sender, `recipient${i}@example.com`);
    assert(result.success === true, `Email ${i+1} should succeed`);
  }

  // Send 11th email (should fail - rate limited)
  const result = await sendEmail(sender, 'recipient11@example.com');
  assert(result.success === false, '11th email should be rate limited');
  assert(result.error.includes('rate limit'), 'Error should mention rate limit');

  // Wait 1 hour and retry (should succeed)
  await sleep(3600000);
  const retryResult = await sendEmail(sender, 'recipient@example.com');
  assert(retryResult.success === true, 'Email after reset should succeed');
}

// Test Per-Recipient Rate Limit:
async function testRecipientRateLimit() {
  const recipient = '+15551234567';

  // Send 20 emails from different senders (should succeed)
  for (let i = 0; i < 20; i++) {
    const result = await sendEmail(`sender${i}@example.com`, recipient);
    assert(result.success === true);
  }

  // Send 21st email (should fail)
  const result = await sendEmail('sender21@example.com', recipient);
  assert(result.success === false);
  assert(result.error.includes('rate limit'));
}

// Success Criteria:
✅ Rate limits enforced per sender
✅ Rate limits enforced per recipient
✅ Rate limits reset after time window
✅ Clear error messages when limited
✅ No SMS sent when rate limited
✅ KV storage tracks counts accurately
```

---

## 7. Performance Testing

### 7.1 Code Generation Performance

#### Test Scenario 7.1.1: Generation Speed Test
```python
# Test ID: PERF-001
# Priority: MEDIUM
# Type: Performance

import time

# Test Minimal Configuration:
start = time.time()
files = generate_email_worker(minimal_config)
duration = time.time() - start

# Expected: <2 seconds
assert duration < 2.0, f"Generation took {duration}s (expected <2s)"
assert len(files) == 10, "Should generate 10 files"

# Test Complex Configuration (all features):
start = time.time()
files = generate_email_worker(complex_config)
duration = time.time() - start

# Expected: <3 seconds even with all features
assert duration < 3.0, f"Complex generation took {duration}s (expected <3s)"

# Test Concurrent Generation:
import concurrent.futures

configs = [create_random_config() for _ in range(10)]
start = time.time()

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(generate_email_worker, configs))

duration = time.time() - start

# Expected: <10 seconds for 10 parallel generations
assert duration < 10.0, f"Parallel generation took {duration}s"
assert len(results) == 10, "All generations should complete"

# Success Criteria:
✅ Single generation: <2 seconds
✅ Complex generation: <3 seconds
✅ 10 parallel generations: <10 seconds
✅ No memory leaks
✅ Consistent performance across runs
```

### 7.2 Email Processing Performance

#### Test Scenario 7.2.1: Worker Response Time
```typescript
// Test ID: PERF-002
// Priority: HIGH
// Type: Performance

// Measure email processing time:
const performanceTest = async () => {
  const iterations = 100;
  const timings = [];

  for (let i = 0; i < iterations; i++) {
    const start = Date.now();

    // Simulate email processing
    await processEmail({
      from: 'test@example.com',
      to: '15551234567@sms.example.com',
      subject: 'Performance Test',
      body: 'Test message'.repeat(50)  // ~500 chars
    });

    const duration = Date.now() - start;
    timings.push(duration);
  }

  // Calculate statistics
  const avg = timings.reduce((a, b) => a + b) / iterations;
  const max = Math.max(...timings);
  const p95 = timings.sort()[Math.floor(iterations * 0.95)];

  console.log(`Average: ${avg}ms`);
  console.log(`Max: ${max}ms`);
  console.log(`P95: ${p95}ms`);

  // Success Criteria:
  // Average: <100ms (parsing + extraction)
  // Max: <500ms
  // P95: <200ms

  assert(avg < 100, `Average too slow: ${avg}ms`);
  assert(max < 500, `Max too slow: ${max}ms`);
  assert(p95 < 200, `P95 too slow: ${p95}ms`);
};

// Test with large email body:
const largeEmailTest = async () => {
  const largeBody = 'X'.repeat(10000);  // 10KB email

  const start = Date.now();
  await processEmail({ body: largeBody });
  const duration = Date.now() - start;

  // Should still be fast (truncation is O(1))
  assert(duration < 200, `Large email processing: ${duration}ms`);
};
```

---

## 8. End-to-End Testing

### 8.1 Complete User Journey

#### Test Scenario 8.1.1: First-Time User Deployment
```gherkin
# Test ID: E2E-001
# Priority: CRITICAL
# Type: End-to-End

Feature: Complete First-Time Deployment
  As a new user with Cloudflare and Twilio accounts
  I want to deploy the email-to-SMS system
  So that I can send SMS messages via email

Scenario: Successful first deployment
  Given I have a Cloudflare account with domain "example.com"
  And I have a Twilio account with phone number "+15551234567"
  And I have Node.js 18+ installed
  And I have Python 3.11+ installed

  # Installation
  When I clone the repository
  And I run "npm install" in the project root
  Then all Node dependencies install successfully
  And wrangler CLI is available

  # Configuration
  When I copy ".dev.vars.example" to ".dev.vars"
  And I edit ".dev.vars" with my Twilio credentials
  And I edit "config/wrangler.toml" with my Cloudflare account ID
  Then configuration files are valid

  # Local Testing
  When I run "npm run dev"
  Then the worker starts on localhost:8787
  And I can see console output
  When I press Ctrl+C
  Then the worker stops cleanly

  # Production Secrets
  When I run "wrangler secret put TWILIO_ACCOUNT_SID" with my SID
  And I run "wrangler secret put TWILIO_AUTH_TOKEN" with my token
  And I run "wrangler secret put TWILIO_PHONE_NUMBER" with my number
  Then all 3 secrets are stored
  And "wrangler secret list" shows all 3

  # KV Namespace
  When I run "npm run kv:create"
  Then a KV namespace is created
  And I receive a namespace ID
  When I add the namespace ID to wrangler.toml
  Then wrangler.toml is valid

  # Deployment
  When I run "npm run deploy:production"
  Then the worker deploys successfully
  And I receive a worker URL
  And "wrangler deployments list" shows the deployment

  # Email Routing
  When I open the Cloudflare Dashboard
  And I navigate to my domain's Email Routing section
  And I click "Enable Email Routing"
  Then MX records are automatically configured
  When I create a routing rule "*@sms.example.com" → Worker
  Then the routing rule is active
  When I run "dig MX example.com"
  Then Cloudflare MX records are returned

  # Testing
  When I send an email:
    | Field   | Value                         |
    | To      | 15555555555@sms.example.com  |
    | From    | me@example.com               |
    | Subject | Deployment Test              |
    | Body    | This is a test message       |
  And I run "npm run tail" to monitor logs
  Then I see "Email received" in the logs within 60 seconds
  And I see "Phone extracted: +15555555555" in the logs
  And I see "Twilio API call successful" in the logs
  And my phone +15555555555 receives an SMS within 120 seconds
  And the SMS content is:
    """
    From: me@example.com
    Re: Deployment Test
    This is a test message
    """

  # Verification
  When I check Cloudflare Dashboard → Workers → Metrics
  Then I see at least 1 request in the metrics
  When I check Twilio Console → Messaging → Logs
  Then I see the SMS message logged
  And the status is "delivered"

  # Success Criteria
  Then the deployment is complete
  And the system is functional
  And I can send more emails
  And they convert to SMS messages

# Time Budget:
  Total estimated time: 2-4 hours
  - Installation: 15 minutes
  - Configuration: 30 minutes
  - Local testing: 15 minutes
  - Secrets setup: 15 minutes
  - KV namespace: 15 minutes
  - Deployment: 15 minutes
  - Email routing: 30 minutes
  - Testing: 30 minutes
  - Troubleshooting buffer: 1 hour
```

---

## Summary: Test Coverage Matrix

| Category | Test Scenarios | Priority | Status |
|----------|---------------|----------|--------|
| **Installation** | 4 | HIGH | ✅ Designed |
| **Configuration** | 7 | HIGH | ✅ Designed |
| **Generation** | 6 | CRITICAL | ✅ Designed |
| **Integration** | 5 | CRITICAL | ✅ Designed |
| **Deployment** | 3 | CRITICAL | ✅ Designed |
| **Security** | 6 | HIGH | ✅ Designed |
| **Performance** | 2 | MEDIUM | ✅ Designed |
| **End-to-End** | 1 | CRITICAL | ✅ Designed |
| **TOTAL** | **34** | - | ✅ Complete |

---

**Test Design Status**: ✅ COMPLETE
**Total Test Scenarios**: 34
**Estimated Execution Time**: 8-12 hours (full suite)
**Automation Potential**: 80% (manual: deployment verification, SMS receipt)

**Next Steps**:
1. Implement automated test scripts
2. Create CI/CD pipeline integration
3. Set up continuous testing
4. Document test results
