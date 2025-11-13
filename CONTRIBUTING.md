# Contributing to Email-to-SMS Worker

Thank you for your interest in contributing to the Email-to-SMS Worker project! This document provides guidelines and instructions for contributing.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Making Changes](#making-changes)
5. [Coding Standards](#coding-standards)
6. [Testing](#testing)
7. [Documentation](#documentation)
8. [Submitting Changes](#submitting-changes)
9. [Review Process](#review-process)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of experience level, gender, gender identity and expression, sexual orientation, disability, personal appearance, body size, race, ethnicity, age, religion, or nationality.

### Expected Behavior

- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what is best for the project and community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment or discriminatory language
- Personal attacks or trolling
- Publishing others' private information
- Any conduct that would be inappropriate in a professional setting

---

## Getting Started

### Ways to Contribute

- **Bug Reports**: Report issues you encounter
- **Feature Requests**: Suggest new features or improvements
- **Code Contributions**: Submit bug fixes or new features
- **Documentation**: Improve or expand documentation
- **Testing**: Add or improve test coverage
- **Reviews**: Review pull requests from other contributors

### First Time Contributors

Look for issues labeled:
- `good first issue` - Suitable for first-time contributors
- `help wanted` - Extra attention needed
- `documentation` - Documentation improvements

---

## Development Setup

### Prerequisites

```bash
# Required
- Node.js 18+
- Python 3.8+
- Git

# Recommended
- VS Code or similar IDE
- Cloudflare account (for testing)
- Twilio account (for testing)
```

### Fork and Clone

```bash
# 1. Fork repository on GitHub

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/cloudflare-email-to-twilio-sms.git
cd cloudflare-email-to-twilio-sms

# 3. Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/cloudflare-email-to-twilio-sms.git
```

### Install Dependencies

**Worker:**
```bash
npm install
```

**Streamlit UI:**
```bash
cd streamlit-app
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### Configure Development Environment

```bash
# Copy example configuration
cp .dev.vars.example .dev.vars

# Edit .dev.vars with your test credentials
# NEVER commit this file!
```

### Verify Setup

```bash
# Type check
npm run typecheck

# Start worker locally
npm run dev

# In another terminal, start Streamlit
cd streamlit-app
streamlit run app.py
```

---

## Making Changes

### Create a Branch

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-description
```

### Branch Naming Convention

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions or improvements
- `chore/` - Maintenance tasks

Examples:
- `feature/add-mms-support`
- `fix/phone-extraction-bug`
- `docs/update-deployment-guide`
- `refactor/improve-error-handling`

---

## Coding Standards

### TypeScript (Worker)

**Style Guide:**

```typescript
// Use clear, descriptive names
function extractPhoneNumber(email: string): string | null {
  // Implementation
}

// Add JSDoc comments for functions
/**
 * Extracts phone number from email address
 * @param email - Email address to parse
 * @returns Phone number in E.164 format, or null if not found
 */
function extractPhoneNumber(email: string): string | null {
  // Implementation
}

// Use async/await over promises
async function sendSMS(phone: string, message: string): Promise<void> {
  // Implementation
}

// Handle errors explicitly
try {
  await sendSMS(phone, message);
} catch (error) {
  console.error('SMS failed:', error);
  throw error;
}

// Use const for immutable values
const MAX_MESSAGE_LENGTH = 1600;

// Use type annotations
interface EmailMessage {
  from: string;
  to: string;
  subject: string;
  body: string;
}
```

**File Organization:**
- Max 500 lines per file
- One class/major function per file
- Group related utilities together
- Keep imports at top, sorted alphabetically

**Type Safety:**
- Always use TypeScript strict mode
- No `any` types (use `unknown` if needed)
- Define interfaces for all data structures
- Use type guards for runtime checks

### Python (Streamlit UI)

**Style Guide:**

```python
# Follow PEP 8
# Use clear, descriptive names
def generate_worker_code(config: WorkerConfig) -> Dict[str, str]:
    """
    Generate Worker source code from configuration.

    Args:
        config: Worker configuration object

    Returns:
        Dictionary mapping file paths to content
    """
    pass

# Use type hints
from typing import Dict, List, Optional

def validate_phone(phone: str) -> bool:
    """Validate phone number format."""
    return bool(PHONE_PATTERN.match(phone))

# Use constants for magic values
MAX_WORKERS = 10
DEFAULT_TIMEOUT = 5000

# Handle errors gracefully
try:
    code = generator.generate_all()
except ValidationError as e:
    st.error(f"Validation failed: {e}")
    return
```

### General Guidelines

**Code Quality:**
- Write self-documenting code
- Add comments for complex logic
- Keep functions small and focused
- Follow DRY (Don't Repeat Yourself)
- Use meaningful variable names

**Security:**
- Never hardcode credentials
- Validate all inputs
- Sanitize content
- Use parameterized queries
- Follow principle of least privilege

**Performance:**
- Avoid unnecessary loops
- Use streaming for large data
- Cache when appropriate
- Profile before optimizing

---

## Testing

### Writing Tests

**Unit Tests (Worker):**

```typescript
// tests/phone-parser.test.ts
import { describe, it, expect } from 'vitest';
import { extractPhoneNumber } from '../src/utils/phone-parser';

describe('extractPhoneNumber', () => {
  it('should extract phone from email address', () => {
    const result = extractPhoneNumber('5551234567@sms.example.com');
    expect(result).toBe('+15551234567');
  });

  it('should return null for invalid format', () => {
    const result = extractPhoneNumber('invalid@example.com');
    expect(result).toBeNull();
  });
});
```

**Integration Tests:**

```typescript
// tests/worker.integration.test.ts
describe('Email Worker Integration', () => {
  it('should process email and send SMS', async () => {
    // Test complete flow
  });
});
```

### Running Tests

```bash
# Run all tests
npm run test

# Run with coverage
npm run test:coverage

# Watch mode
npm run test:watch
```

### Test Requirements

**All contributions should:**
- Include tests for new features
- Update tests for bug fixes
- Maintain or improve code coverage
- Pass all existing tests

**Coverage Targets:**
- Unit tests: 80% minimum
- Critical paths: 100% coverage
- Error handling: 100% coverage

---

## Documentation

### Code Documentation

**Required JSDoc/Docstrings:**

```typescript
/**
 * Send SMS message via Twilio
 *
 * @param phone - Recipient phone number (E.164 format)
 * @param message - Message content (max 1600 chars)
 * @param env - Environment variables including Twilio credentials
 * @returns Twilio message SID
 * @throws {TwilioError} If SMS sending fails
 *
 * @example
 * const sid = await sendSMS('+15551234567', 'Test message', env);
 */
async function sendSMS(
  phone: string,
  message: string,
  env: Env
): Promise<string> {
  // Implementation
}
```

### User Documentation

**When adding features, update:**
- README.md (if user-facing)
- Relevant docs/ files
- API.md (if changing interfaces)
- USER_GUIDE.md (for user features)

**Documentation Standards:**
- Clear, concise language
- Code examples where appropriate
- Screenshots for UI changes
- Updated table of contents

### Changelog

Update `CHANGELOG.md`:

```markdown
## [Unreleased]

### Added
- New feature description

### Changed
- Modified behavior description

### Fixed
- Bug fix description
```

---

## Submitting Changes

### Before Submitting

**Checklist:**
- [ ] Code follows style guidelines
- [ ] Tests added and passing
- [ ] Documentation updated
- [ ] No console.log() or debugging code
- [ ] Type checking passes (`npm run typecheck`)
- [ ] Linting passes (`npm run lint`)
- [ ] Commits are meaningful and atomic
- [ ] Branch is up to date with main

### Commit Messages

**Format:**
```
Type: Short description (50 chars max)

Longer explanation if needed (wrap at 72 chars).
Include motivation for change and contrast with
previous behavior.

Fixes #123
```

**Types:**
- `Add:` - New feature
- `Fix:` - Bug fix
- `Update:` - Modify existing feature
- `Remove:` - Remove feature/code
- `Refactor:` - Code restructuring
- `Docs:` - Documentation only
- `Test:` - Test additions/changes
- `Chore:` - Maintenance tasks

**Examples:**
```
Add: MMS support for image attachments

Implements MMS sending via Twilio API. Supports
JPEG, PNG, and GIF images up to 5MB.

Fixes #45

---

Fix: Phone extraction from formatted numbers

Handles phone numbers with parentheses like
(555) 123-4567 correctly.

Fixes #67

---

Docs: Update deployment guide for KV setup

Clarifies KV namespace creation and configuration
steps.
```

### Create Pull Request

```bash
# Push your branch
git push origin feature/your-feature-name

# Go to GitHub and create Pull Request
```

**PR Title:**
```
Add: Brief description of changes
```

**PR Description:**
```markdown
## Description
What does this PR do?

## Motivation
Why is this change needed?

## Changes
- Change 1
- Change 2
- Change 3

## Testing
How was this tested?

## Checklist
- [ ] Tests added
- [ ] Documentation updated
- [ ] No breaking changes
- [ ] Backward compatible

## Related Issues
Fixes #123
Related to #456
```

### PR Labels

Apply appropriate labels:
- `bug` - Bug fix
- `enhancement` - New feature
- `documentation` - Documentation changes
- `breaking change` - Breaking API changes
- `good first issue` - Suitable for newcomers

---

## Review Process

### What to Expect

1. **Automated Checks** (immediate)
   - Type checking
   - Linting
   - Tests
   - Code coverage

2. **Code Review** (1-3 days)
   - Maintainer reviews code
   - May request changes
   - Discussion via PR comments

3. **Revision** (as needed)
   - Address review feedback
   - Push additional commits
   - Re-request review

4. **Approval** (when ready)
   - Maintainer approves PR
   - Merge to main branch
   - Automatic deployment (if applicable)

### Review Criteria

**Code Quality:**
- Follows style guidelines
- Properly tested
- Well documented
- No unnecessary complexity

**Functionality:**
- Works as intended
- No breaking changes (unless necessary)
- Handles edge cases
- Backward compatible

**Security:**
- No security vulnerabilities
- Input validation
- No hardcoded secrets

### Responding to Feedback

**Best Practices:**
- Respond to all comments
- Ask questions if unclear
- Make requested changes promptly
- Be open to suggestions
- Stay professional and friendly

**Making Changes:**
```bash
# Make changes based on feedback
git add .
git commit -m "Update: Address review feedback"
git push origin feature/your-feature-name

# PR automatically updates
```

---

## Communication

### Discussion Channels

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: General questions, ideas
- **Pull Requests**: Code-specific discussion
- **Email**: Security issues only

### Reporting Security Issues

**DO NOT** open public issues for security vulnerabilities.

Email security issues to: [security@example.com]

Include:
- Description of vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

---

## Recognition

### Contributors

All contributors will be:
- Listed in CONTRIBUTORS.md
- Credited in release notes
- Thanked in project documentation

### Significant Contributions

May be recognized with:
- Maintainer status
- Decision-making involvement
- Special acknowledgment

---

## Questions?

- **General Questions**: Open a GitHub Discussion
- **Bug Reports**: Open a GitHub Issue
- **Feature Ideas**: Open a GitHub Discussion
- **Security**: Email [security@example.com]

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## Thank You!

Your contributions make this project better for everyone. We appreciate your time and effort!

**Happy Coding! 🚀**

---

**Last Updated:** 2025-11-13
**Version:** 1.0.0
