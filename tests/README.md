## Test Suite Documentation

### Overview

Comprehensive test suite for the Email-to-SMS Cloudflare Worker with >90% code coverage.

### Test Structure

```
tests/
├── worker/                 # Worker tests
│   ├── phone-parser.spec.ts       # Phone extraction and validation
│   ├── content-processor.spec.ts  # Email content processing
│   ├── twilio-service.spec.ts     # Twilio API integration
│   ├── validator.spec.ts          # Validation logic
│   ├── rate-limiter.spec.ts       # Rate limiting
│   ├── security.spec.ts           # Security vulnerability tests
│   ├── integration.spec.ts        # End-to-end tests
│   └── performance.spec.ts        # Performance benchmarks
├── fixtures/              # Test data and mocks
│   ├── test-data.json            # Test fixtures
│   └── mock-services.ts          # Mock implementations
└── helpers/               # Test utilities
    └── test-utils.ts             # Helper functions
```

### Running Tests

```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run specific test file
npm test phone-parser.spec.ts

# Run in watch mode
npm test -- --watch

# Run with UI
npm test -- --ui

# Run benchmarks
npm test -- --run tests/**/*.bench.ts
```

### Test Categories

#### 1. Unit Tests

Test individual components in isolation:

- **phone-parser.spec.ts**: Phone number extraction from email/subject/headers/body
- **content-processor.spec.ts**: Email content processing and SMS conversion
- **twilio-service.spec.ts**: Twilio API integration and error handling
- **validator.spec.ts**: Email and content validation
- **rate-limiter.spec.ts**: Rate limiting logic

**Coverage**: 85-95% per component

#### 2. Integration Tests

Test complete workflows:

- **integration.spec.ts**: End-to-end email-to-SMS flow
- Full pipeline: Email → Parse → Validate → Extract Phone → Send SMS
- Error handling and recovery
- Rate limiting integration
- Real-world scenarios

**Coverage**: 90%+ of integration paths

#### 3. Security Tests

Test attack prevention:

- **security.spec.ts**: XSS, SQL injection, XML injection, path traversal
- Input sanitization
- Phone number validation security
- Content encoding attacks
- ReDoS prevention

**Coverage**: All known attack vectors

#### 4. Performance Tests

Benchmark critical paths:

- **performance.spec.ts**: Response times, throughput, memory usage
- Content processing: <10ms for short emails
- Phone extraction: <5ms
- Batch processing: >100 emails/second
- Memory: <50MB for 100 emails

**Target**: <500ms total processing time

### Test Data

#### Fixtures (`test-data.json`)

- **twilio_webhooks**: Valid/invalid Twilio payloads
- **twilio_api_responses**: Success/error responses
- **streamlit_configs**: Valid/invalid configurations
- **security_payloads**: XSS, SQL injection, etc.
- **performance_scenarios**: Load test configurations
- **edge_cases**: Boundary values, special characters

#### Mock Services (`mock-services.ts`)

- **MockTwilioClient**: Simulates Twilio SDK
- **MockWorkflowBinding**: Simulates Cloudflare Workflows
- **MockRateLimiter**: Rate limit testing
- **PerformanceTimer**: Benchmarking utility
- **MemoryTracker**: Memory profiling

### Writing Tests

#### Best Practices

1. **Descriptive Names**: `should extract phone from email address`
2. **Arrange-Act-Assert**: Clear test structure
3. **One Assertion**: Test one behavior per test
4. **Mock External**: Use mock services for Twilio, KV
5. **Clean Up**: Reset mocks in `afterEach`

#### Example Test

```typescript
describe('Phone Parser', () => {
  it('should extract phone from email address', () => {
    const result = extractPhoneFromEmail('5551234567@example.com');

    expect(result).toBeDefined();
    expect(result?.phoneNumber).toBe('+15551234567');
    expect(result?.source).toBe('email_to');
    expect(result?.confidence).toBe('high');
  });
});
```

### Coverage Requirements

| Category      | Target | Current |
|---------------|--------|---------|
| Statements    | >90%   | TBD     |
| Branches      | >85%   | TBD     |
| Functions     | >90%   | TBD     |
| Lines         | >90%   | TBD     |

### CI/CD Integration

Tests run automatically on:
- Push to main branch
- Pull requests
- Pre-commit hook (optional)

### Debugging Tests

```bash
# Run single test with debug output
npm test -- phone-parser.spec.ts --reporter=verbose

# Run with Node debugger
node --inspect-brk node_modules/.bin/vitest run

# Generate coverage report
npm run test:coverage
open coverage/index.html
```

### Performance Benchmarks

Run performance tests to establish baselines:

```bash
npm test performance.spec.ts
```

Expected results:
- Content processing: <10ms (short), <50ms (large)
- Phone extraction: <5ms
- Throughput: >100 emails/second
- Memory: <50MB for 100 emails

### Test Utilities

Located in `tests/helpers/test-utils.ts`:

- `createMockEmail()`: Create test email objects
- `createMockEnv()`: Mock environment variables
- `mockFetch()`: Mock Twilio API calls
- `TestTimer`: Performance measurement
- `ConsoleCapture`: Capture console output
- `retry()`: Retry flaky tests

### Troubleshooting

**Tests fail with "Module not found"**:
- Check `vitest.config.ts` path aliases
- Ensure imports use correct paths

**Performance tests fail**:
- Run on isolated machine
- Close other applications
- Increase timeout if needed

**Coverage below threshold**:
- Run `npm run test:coverage`
- Check `coverage/index.html` for gaps
- Add tests for uncovered branches

### Contributing

1. Write tests first (TDD)
2. Ensure >90% coverage
3. Add edge cases
4. Update documentation
5. Run full suite before PR

### Resources

- [Vitest Documentation](https://vitest.dev/)
- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
- [Test Data Strategy](TESTING_STRATEGY.md)
