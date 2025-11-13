/**
 * Test Suite: Phone Number Validation Regex Fix (FIX 5)
 *
 * Tests the corrected E.164 phone number validation regex
 * Original: /^\+[1-9]\d{1,14}$/ (allowed +10, +123, etc.)
 * Fixed: /^\+[1-9]\d{10,14}$/ (requires minimum 11 digits total)
 */

// Extracted regex pattern from index.ts.j2 (line 59)
const PHONE_REGEX = /^\+[1-9]\d{10,14}$/;

/**
 * Test function matching the extractPhoneNumber logic
 */
function extractPhoneNumber(emailAddress, defaultCountryCode = '+1') {
  // Extract local part before @
  const match = emailAddress.match(/^([^@]+)@/);
  if (!match) return null;

  let phoneNumber = match[1];

  // Remove common formatting characters
  phoneNumber = phoneNumber.replace(/[\s\-\(\)\.]/g, '');

  // Add country code if missing
  if (!phoneNumber.startsWith('+')) {
    phoneNumber = defaultCountryCode + phoneNumber;
  }

  // Validate E.164 format: +[1-9] followed by 10-14 digits
  // E.164 requires minimum 11 digits total (country code + number)
  // Example: +14155552671 (11 digits), +442071234567 (12 digits)
  if (!PHONE_REGEX.test(phoneNumber)) {
    return null;
  }

  return phoneNumber;
}

// Test cases
const tests = [
  // SHOULD REJECT - Too short (these were incorrectly accepted before fix)
  { input: '+10', expected: null, reason: 'Too short (2 digits)' },
  { input: '+123', expected: null, reason: 'Too short (3 digits)' },
  { input: '+1234', expected: null, reason: 'Too short (4 digits)' },
  { input: '+12345', expected: null, reason: 'Too short (5 digits)' },
  { input: '+123456', expected: null, reason: 'Too short (6 digits)' },
  { input: '+1234567', expected: null, reason: 'Too short (7 digits)' },
  { input: '+12345678', expected: null, reason: 'Too short (8 digits)' },
  { input: '+123456789', expected: null, reason: 'Too short (9 digits)' },
  { input: '+1234567890', expected: null, reason: 'Too short (10 digits)' },

  // SHOULD ACCEPT - Valid E.164 format (11-15 digits)
  { input: '+12345678901', expected: '+12345678901', reason: 'Valid 11 digits (minimum)' },
  { input: '+14155552671', expected: '+14155552671', reason: 'Valid US number (11 digits)' },
  { input: '+442071234567', expected: '+442071234567', reason: 'Valid UK number (12 digits)' },
  { input: '+861234567890', expected: '+861234567890', reason: 'Valid China number (12 digits)' },
  { input: '+12345678901234', expected: '+12345678901234', reason: 'Valid 14 digits' },
  { input: '+123456789012345', expected: '+123456789012345', reason: 'Valid 15 digits (maximum)' },

  // SHOULD REJECT - Too long
  { input: '+1234567890123456', expected: null, reason: 'Too long (16 digits)' },

  // SHOULD REJECT - Invalid format
  { input: '+0123456789', expected: null, reason: 'Starts with 0' },
  { input: '12345678901', expected: null, reason: 'Missing + sign (will be added by country code)' },
  { input: '+abc1234567890', expected: null, reason: 'Contains letters' },
  { input: '++12345678901', expected: null, reason: 'Double + sign' },

  // Test email extraction with formatting
  { input: '4155552671@example.com', expected: '+14155552671', reason: 'Email with 10-digit number, country code added' },
  { input: '(415) 555-2671@example.com', expected: '+14155552671', reason: 'Email with formatted number' },
  { input: '+14155552671@example.com', expected: '+14155552671', reason: 'Email with full number' },
  { input: '415.555.2671@example.com', expected: '+14155552671', reason: 'Email with dot-formatted number' },
];

// Run tests
console.log('='.repeat(80));
console.log('Phone Number Validation Test Suite - FIX 5');
console.log('Testing E.164 regex: /^\\+[1-9]\\d{10,14}$/');
console.log('='.repeat(80));
console.log();

let passed = 0;
let failed = 0;

tests.forEach((test, index) => {
  let result;

  // Test raw phone numbers or email addresses
  if (test.input.includes('@')) {
    result = extractPhoneNumber(test.input);
  } else {
    result = PHONE_REGEX.test(test.input) ? test.input : null;
  }

  const success = result === test.expected;
  const status = success ? '✅ PASS' : '❌ FAIL';

  if (success) {
    passed++;
  } else {
    failed++;
  }

  console.log(`Test ${index + 1}: ${status}`);
  console.log(`  Input:    "${test.input}"`);
  console.log(`  Expected: ${test.expected === null ? 'REJECT (null)' : test.expected}`);
  console.log(`  Got:      ${result === null ? 'REJECT (null)' : result}`);
  console.log(`  Reason:   ${test.reason}`);
  console.log();
});

console.log('='.repeat(80));
console.log(`Results: ${passed} passed, ${failed} failed out of ${tests.length} tests`);
console.log('='.repeat(80));

// Exit with error code if any tests failed
if (failed > 0) {
  console.error(`\n❌ ${failed} test(s) failed!`);
  process.exit(1);
} else {
  console.log('\n✅ All tests passed!');
  process.exit(0);
}
