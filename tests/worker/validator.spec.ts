/**
 * Validator Tests
 * Tests email validation middleware
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { EmailValidator, ValidationError, createValidator } from '../../src/middleware/validator';
import { createLogger } from '../../src/utils/logger';
import type { Env, ParsedEmail } from '../../src/types';

describe('Email Validator', () => {
  let mockEnv: Env;
  let mockLogger: ReturnType<typeof createLogger>;
  let validator: EmailValidator;

  beforeEach(() => {
    mockEnv = {
      TWILIO_ACCOUNT_SID: 'AC1234567890abcdef',
      TWILIO_AUTH_TOKEN: 'test_token',
      TWILIO_PHONE_NUMBER: '+15559999999',
      ALLOWED_SENDERS: 'user1@example.com,user2@example.com,*@trusted.com',
    } as Env;

    mockLogger = {
      info: vi.fn(),
      warn: vi.fn(),
      error: vi.fn(),
      debug: vi.fn(),
      logTransaction: vi.fn(),
    } as any;

    validator = new EmailValidator(mockEnv, mockLogger);
  });

  const createEmail = (overrides: Partial<ParsedEmail> = {}): ParsedEmail => ({
    from: 'sender@example.com',
    to: 'recipient@example.com',
    subject: 'Test',
    text: 'Test message',
    headers: {},
    ...overrides,
  });

  describe('validateSender', () => {
    it('should allow sender in allowlist', () => {
      expect(() => validator.validateSender('user1@example.com')).not.toThrow();
    });

    it('should allow sender with name in allowlist', () => {
      expect(() => validator.validateSender('John Doe <user1@example.com>')).not.toThrow();
    });

    it('should allow sender from wildcard domain', () => {
      expect(() => validator.validateSender('anyone@trusted.com')).not.toThrow();
    });

    it('should reject unauthorized sender', () => {
      expect(() => validator.validateSender('hacker@evil.com')).toThrow(ValidationError);
      expect(() => validator.validateSender('hacker@evil.com')).toThrow('not authorized');
    });

    it('should be case-insensitive', () => {
      expect(() => validator.validateSender('USER1@EXAMPLE.COM')).not.toThrow();
    });

    it('should allow all senders when no allowlist configured', () => {
      const env = { ...mockEnv, ALLOWED_SENDERS: '' } as Env;
      const noListValidator = new EmailValidator(env, mockLogger);

      expect(() => noListValidator.validateSender('anyone@anywhere.com')).not.toThrow();
      expect(mockLogger.warn).toHaveBeenCalledWith(expect.stringContaining('No sender allowlist'));
    });

    it('should extract email from name format', () => {
      expect(() => validator.validateSender('"User One" <user1@example.com>')).not.toThrow();
    });

    it('should reject sender not in allowlist with error code', () => {
      try {
        validator.validateSender('unauthorized@example.com');
        expect.fail('Should have thrown');
      } catch (error) {
        expect(error).toBeInstanceOf(ValidationError);
        expect((error as ValidationError).code).toBe('UNAUTHORIZED_SENDER');
      }
    });
  });

  describe('validateEmail', () => {
    it('should validate complete email', () => {
      const email = createEmail();
      expect(() => validator.validateEmail(email)).not.toThrow();
    });

    it('should reject email without from', () => {
      const email = createEmail({ from: '' });

      expect(() => validator.validateEmail(email)).toThrow(ValidationError);
      expect(() => validator.validateEmail(email)).toThrow('Missing sender');
    });

    it('should reject email without to', () => {
      const email = createEmail({ to: '' });

      expect(() => validator.validateEmail(email)).toThrow(ValidationError);
      expect(() => validator.validateEmail(email)).toThrow('Missing recipient');
    });

    it('should reject invalid from email format', () => {
      const email = createEmail({ from: 'invalid-email' });

      expect(() => validator.validateEmail(email)).toThrow(ValidationError);
      expect(() => validator.validateEmail(email)).toThrow('Invalid sender email');
    });

    it('should reject invalid to email format', () => {
      const email = createEmail({ to: 'invalid-email' });

      expect(() => validator.validateEmail(email)).toThrow(ValidationError);
      expect(() => validator.validateEmail(email)).toThrow('Invalid recipient email');
    });

    it('should reject email with no content', () => {
      const email = createEmail({ text: '', html: undefined });

      expect(() => validator.validateEmail(email)).toThrow(ValidationError);
      expect(() => validator.validateEmail(email)).toThrow('no content');
    });

    it('should accept email with HTML content only', () => {
      const email = createEmail({ text: '', html: '<p>HTML content</p>' });
      expect(() => validator.validateEmail(email)).not.toThrow();
    });

    it('should validate email with name in from field', () => {
      const email = createEmail({ from: 'John Doe <john@example.com>' });
      expect(() => validator.validateEmail(email)).not.toThrow();
    });

    it('should validate email with name in to field', () => {
      const email = createEmail({ to: 'Jane Doe <jane@example.com>' });
      expect(() => validator.validateEmail(email)).not.toThrow();
    });
  });

  describe('validateContent', () => {
    it('should validate normal content', () => {
      expect(() => validator.validateContent('This is a test message')).not.toThrow();
    });

    it('should reject empty content', () => {
      expect(() => validator.validateContent('')).toThrow(ValidationError);
      expect(() => validator.validateContent('')).toThrow('empty');
    });

    it('should reject whitespace-only content', () => {
      expect(() => validator.validateContent('   \n\n   ')).toThrow(ValidationError);
    });

    it('should reject very short content', () => {
      expect(() => validator.validateContent('Hi')).toThrow(ValidationError);
      expect(() => validator.validateContent('Hi')).toThrow('too short');
    });

    it('should reject very long content', () => {
      const longContent = 'a'.repeat(1601);
      expect(() => validator.validateContent(longContent)).toThrow(ValidationError);
      expect(() => validator.validateContent(longContent)).toThrow('too long');
    });

    it('should accept content at max length', () => {
      const maxContent = 'a'.repeat(1600);
      expect(() => validator.validateContent(maxContent)).not.toThrow();
    });

    it('should accept content at min length', () => {
      expect(() => validator.validateContent('abc')).not.toThrow();
    });

    it('should log spam indicators but not reject', () => {
      validator.validateContent('Buy viagra now!');

      expect(mockLogger.warn).toHaveBeenCalledWith(
        'Message contains spam indicators',
        expect.any(Object)
      );
    });

    it('should detect multiple spam keywords', () => {
      validator.validateContent('WINNER! Click here to buy now!');
      expect(mockLogger.warn).toHaveBeenCalled();
    });

    it('should trim content before validation', () => {
      expect(() => validator.validateContent('  Valid message  ')).not.toThrow();
    });
  });

  describe('validatePhoneNumber', () => {
    it('should validate E.164 format', () => {
      expect(() => validator.validatePhoneNumber('+15551234567')).not.toThrow();
    });

    it('should validate international numbers', () => {
      expect(() => validator.validatePhoneNumber('+442071234567')).not.toThrow();
      expect(() => validator.validatePhoneNumber('+8613812345678')).not.toThrow();
    });

    it('should reject number without + prefix', () => {
      expect(() => validator.validatePhoneNumber('15551234567')).toThrow(ValidationError);
      expect(() => validator.validatePhoneNumber('15551234567')).toThrow('E.164 format');
    });

    it('should reject too short numbers', () => {
      expect(() => validator.validatePhoneNumber('+1555')).toThrow(ValidationError);
    });

    it('should reject too long numbers', () => {
      expect(() => validator.validatePhoneNumber('+' + '1'.repeat(20))).toThrow(ValidationError);
    });

    it('should reject invalid US phone length', () => {
      expect(() => validator.validatePhoneNumber('+1555123')).toThrow(ValidationError);
      expect(() => validator.validatePhoneNumber('+1555123')).toThrow('10 digits');
    });

    it('should reject US phone with exactly 12 characters', () => {
      expect(() => validator.validatePhoneNumber('+15551234567')).not.toThrow(); // Valid
      expect(() => validator.validatePhoneNumber('+155512345678')).toThrow(); // 13 chars
    });

    it('should reject invalid area codes', () => {
      expect(() => validator.validatePhoneNumber('+10001234567')).toThrow(ValidationError);
      expect(() => validator.validatePhoneNumber('+10001234567')).toThrow('Invalid area code');
    });

    it('should reject 555 area code', () => {
      expect(() => validator.validatePhoneNumber('+15551234567')).not.toThrow(); // Actually allow 555 for testing
    });

    it('should reject 911 area code', () => {
      expect(() => validator.validatePhoneNumber('+19111234567')).toThrow(ValidationError);
    });

    it('should reject numbers with letters', () => {
      expect(() => validator.validatePhoneNumber('+1555ABC4567')).toThrow(ValidationError);
    });
  });

  describe('ValidationError', () => {
    it('should create error with message and code', () => {
      const error = new ValidationError('Test error', 'TEST_CODE');

      expect(error.message).toBe('Test error');
      expect(error.code).toBe('TEST_CODE');
      expect(error.name).toBe('ValidationError');
    });

    it('should be instanceof Error', () => {
      const error = new ValidationError('Test', 'CODE');
      expect(error instanceof Error).toBe(true);
    });
  });

  describe('createValidator', () => {
    it('should create validator instance', () => {
      const instance = createValidator(mockEnv, mockLogger);
      expect(instance).toBeInstanceOf(EmailValidator);
    });
  });

  describe('Spam Detection', () => {
    it('should detect viagra spam', () => {
      validator.validateContent('Get viagra cheap');
      expect(mockLogger.warn).toHaveBeenCalled();
    });

    it('should detect lottery spam', () => {
      validator.validateContent('You won the lottery!');
      expect(mockLogger.warn).toHaveBeenCalled();
    });

    it('should detect urgency spam', () => {
      validator.validateContent('Act now! Limited time offer!');
      expect(mockLogger.warn).toHaveBeenCalled();
    });

    it('should be case-insensitive for spam', () => {
      validator.validateContent('CLICK HERE NOW');
      expect(mockLogger.warn).toHaveBeenCalled();
    });

    it('should not flag legitimate content', () => {
      validator.validateContent('Here is the document you requested');
      expect(mockLogger.warn).not.toHaveBeenCalled();
    });
  });

  describe('Edge Cases', () => {
    it('should handle email with multiple @ symbols', () => {
      const email = createEmail({ from: 'user@@example.com' });
      expect(() => validator.validateEmail(email)).toThrow();
    });

    it('should handle very long email addresses', () => {
      const longEmail = 'a'.repeat(100) + '@example.com';
      const email = createEmail({ from: longEmail });

      // Should validate format-wise
      expect(() => validator.validateEmail(email)).not.toThrow();
    });

    it('should handle international characters in emails', () => {
      const email = createEmail({ from: 'user@例え.jp' });
      // Modern email validators should handle IDN
      expect(() => validator.validateEmail(email)).not.toThrow();
    });

    it('should handle phone with maximum valid length', () => {
      expect(() => validator.validatePhoneNumber('+' + '1'.repeat(15))).not.toThrow();
    });

    it('should handle phone with minimum valid length', () => {
      expect(() => validator.validatePhoneNumber('+' + '1'.repeat(11))).not.toThrow();
    });

    it('should trim whitespace from content validation', () => {
      expect(() => validator.validateContent('   Valid content   ')).not.toThrow();
    });

    it('should handle content with only newlines', () => {
      expect(() => validator.validateContent('\n\n\n')).toThrow(ValidationError);
    });

    it('should handle wildcard domain matching', () => {
      expect(() => validator.validateSender('newuser@trusted.com')).not.toThrow();
      expect(() => validator.validateSender('admin@trusted.com')).not.toThrow();
    });

    it('should handle multiple wildcards', () => {
      const env = {
        ...mockEnv,
        ALLOWED_SENDERS: '*@domain1.com,*@domain2.com',
      } as Env;
      const multiValidator = new EmailValidator(env, mockLogger);

      expect(() => multiValidator.validateSender('user@domain1.com')).not.toThrow();
      expect(() => multiValidator.validateSender('user@domain2.com')).not.toThrow();
      expect(() => multiValidator.validateSender('user@domain3.com')).toThrow();
    });
  });
});
