/**
 * Phone Parser Tests
 * Tests phone number extraction and validation logic
 */

import { describe, it, expect } from 'vitest';
import {
  extractPhoneNumber,
  extractPhoneFromEmail,
  extractPhoneFromSubject,
  extractPhoneFromHeaders,
  extractPhoneFromBody,
  normalizePhoneNumber,
  isValidPhoneNumber,
  formatPhoneNumber,
} from '../../src/utils/phone-parser';
import type { ParsedEmail } from '../../src/types';

describe('Phone Parser', () => {
  describe('extractPhoneFromEmail', () => {
    it('should extract phone number from email address', () => {
      const result = extractPhoneFromEmail('5551234567@example.com');

      expect(result).toBeDefined();
      expect(result?.phoneNumber).toBe('+15551234567');
      expect(result?.source).toBe('email_to');
      expect(result?.confidence).toBe('high');
    });

    it('should extract phone with country code from email', () => {
      const result = extractPhoneFromEmail('+15551234567@example.com');

      expect(result).toBeDefined();
      expect(result?.phoneNumber).toBe('+15551234567');
    });

    it('should extract phone with 1 prefix from email', () => {
      const result = extractPhoneFromEmail('15551234567@example.com');

      expect(result).toBeDefined();
      expect(result?.phoneNumber).toBe('+15551234567');
    });

    it('should return null for email without phone', () => {
      const result = extractPhoneFromEmail('user@example.com');
      expect(result).toBeNull();
    });

    it('should return null for invalid phone in email', () => {
      const result = extractPhoneFromEmail('123@example.com');
      expect(result).toBeNull();
    });
  });

  describe('extractPhoneFromSubject', () => {
    it('should extract phone from "To:" prefix', () => {
      const result = extractPhoneFromSubject('To: 555-123-4567');

      expect(result).toBeDefined();
      expect(result?.phoneNumber).toBe('+15551234567');
      expect(result?.source).toBe('subject');
      expect(result?.confidence).toBe('high');
    });

    it('should extract phone with dots', () => {
      const result = extractPhoneFromSubject('Phone: 555.123.4567');

      expect(result).toBeDefined();
      expect(result?.phoneNumber).toBe('+15551234567');
    });

    it('should extract phone with spaces', () => {
      const result = extractPhoneFromSubject('Call 555 123 4567');

      expect(result).toBeDefined();
      expect(result?.phoneNumber).toBe('+15551234567');
    });

    it('should extract phone without prefix', () => {
      const result = extractPhoneFromSubject('555-123-4567 urgent');

      expect(result).toBeDefined();
      expect(result?.phoneNumber).toBe('+15551234567');
    });

    it('should return null for subject without phone', () => {
      const result = extractPhoneFromSubject('Hello world');
      expect(result).toBeNull();
    });

    it('should handle case-insensitive prefixes', () => {
      const result = extractPhoneFromSubject('NUMBER: 555-123-4567');

      expect(result).toBeDefined();
      expect(result?.phoneNumber).toBe('+15551234567');
    });
  });

  describe('extractPhoneFromHeaders', () => {
    it('should extract phone from X-SMS-To header', () => {
      const headers = { 'x-sms-to': '+15551234567' };
      const result = extractPhoneFromHeaders(headers);

      expect(result).toBeDefined();
      expect(result?.phoneNumber).toBe('+15551234567');
      expect(result?.source).toBe('header');
      expect(result?.confidence).toBe('high');
    });

    it('should extract phone from X-Phone header', () => {
      const headers = { 'x-phone': '555-123-4567' };
      const result = extractPhoneFromHeaders(headers);

      expect(result).toBeDefined();
      expect(result?.phoneNumber).toBe('+15551234567');
    });

    it('should extract phone from X-Recipient header', () => {
      const headers = { 'x-recipient': '5551234567' };
      const result = extractPhoneFromHeaders(headers);

      expect(result).toBeDefined();
      expect(result?.phoneNumber).toBe('+15551234567');
    });

    it('should handle case-insensitive headers', () => {
      const headers = { 'X-SMS-TO': '+15551234567' };
      const result = extractPhoneFromHeaders(headers);

      expect(result).toBeDefined();
    });

    it('should return null for headers without phone', () => {
      const headers = { 'content-type': 'text/plain' };
      const result = extractPhoneFromHeaders(headers);
      expect(result).toBeNull();
    });

    it('should return null for invalid phone in header', () => {
      const headers = { 'x-sms-to': 'invalid' };
      const result = extractPhoneFromHeaders(headers);
      expect(result).toBeNull();
    });
  });

  describe('extractPhoneFromBody', () => {
    it('should extract phone from email body', () => {
      const body = 'Please call 555-123-4567 for more info';
      const result = extractPhoneFromBody(body);

      expect(result).toBeDefined();
      expect(result?.phoneNumber).toBe('+15551234567');
      expect(result?.source).toBe('body');
      expect(result?.confidence).toBe('low'); // Lower confidence for body extraction
    });

    it('should extract phone with country code from body', () => {
      const body = 'Contact +1-555-123-4567 immediately';
      const result = extractPhoneFromBody(body);

      expect(result).toBeDefined();
      expect(result?.phoneNumber).toBe('+15551234567');
    });

    it('should only search first 200 characters', () => {
      const body = 'a'.repeat(250) + '555-123-4567';
      const result = extractPhoneFromBody(body);
      expect(result).toBeNull(); // Phone is beyond 200 char limit
    });

    it('should return null for body without phone', () => {
      const body = 'This is a regular message';
      const result = extractPhoneFromBody(body);
      expect(result).toBeNull();
    });
  });

  describe('extractPhoneNumber (main function)', () => {
    const createEmail = (overrides: Partial<ParsedEmail> = {}): ParsedEmail => ({
      from: 'sender@example.com',
      to: 'recipient@example.com',
      subject: 'Test',
      text: 'Test message',
      headers: {},
      ...overrides,
    });

    it('should prioritize header extraction', () => {
      const email = createEmail({
        headers: { 'x-sms-to': '+15559999999' },
        to: '5551234567@example.com',
        subject: 'To: 555-111-1111',
      });

      const result = extractPhoneNumber(email);
      expect(result.phoneNumber).toBe('+15559999999');
      expect(result.source).toBe('header');
    });

    it('should fall back to email address extraction', () => {
      const email = createEmail({
        to: '5551234567@example.com',
        subject: 'Hello',
      });

      const result = extractPhoneNumber(email);
      expect(result.phoneNumber).toBe('+15551234567');
      expect(result.source).toBe('email_to');
    });

    it('should fall back to subject extraction', () => {
      const email = createEmail({
        to: 'user@example.com',
        subject: 'To: 555-123-4567',
      });

      const result = extractPhoneNumber(email);
      expect(result.phoneNumber).toBe('+15551234567');
      expect(result.source).toBe('subject');
    });

    it('should fall back to body extraction', () => {
      const email = createEmail({
        to: 'user@example.com',
        subject: 'Hello',
        text: 'Call 555-123-4567',
      });

      const result = extractPhoneNumber(email);
      expect(result.phoneNumber).toBe('+15551234567');
      expect(result.source).toBe('body');
    });

    it('should throw error when no phone found', () => {
      const email = createEmail({
        to: 'user@example.com',
        subject: 'Hello',
        text: 'No phone here',
      });

      expect(() => extractPhoneNumber(email)).toThrow('No valid phone number found in email');
    });
  });

  describe('normalizePhoneNumber', () => {
    it('should add country code to 10-digit number', () => {
      expect(normalizePhoneNumber('5551234567')).toBe('+15551234567');
    });

    it('should preserve existing country code', () => {
      expect(normalizePhoneNumber('15551234567')).toBe('+15551234567');
    });

    it('should add + prefix', () => {
      expect(normalizePhoneNumber('15551234567')).toBe('+15551234567');
    });

    it('should remove formatting characters', () => {
      expect(normalizePhoneNumber('555-123-4567')).toBe('+15551234567');
      expect(normalizePhoneNumber('555.123.4567')).toBe('+15551234567');
      expect(normalizePhoneNumber('555 123 4567')).toBe('+15551234567');
      expect(normalizePhoneNumber('(555) 123-4567')).toBe('+15551234567');
    });

    it('should use custom country code', () => {
      expect(normalizePhoneNumber('2071234567', '44')).toBe('+442071234567');
    });

    it('should handle international numbers', () => {
      expect(normalizePhoneNumber('442071234567')).toBe('+442071234567');
    });
  });

  describe('isValidPhoneNumber', () => {
    it('should validate US E.164 format', () => {
      expect(isValidPhoneNumber('+15551234567')).toBe(true);
    });

    it('should validate international E.164 format', () => {
      expect(isValidPhoneNumber('+442071234567')).toBe(true);
      expect(isValidPhoneNumber('+8613812345678')).toBe(true);
    });

    it('should reject numbers without + prefix', () => {
      expect(isValidPhoneNumber('15551234567')).toBe(false);
    });

    it('should reject too short numbers', () => {
      expect(isValidPhoneNumber('+1555')).toBe(false);
    });

    it('should reject too long numbers', () => {
      expect(isValidPhoneNumber('+' + '1'.repeat(20))).toBe(false);
    });

    it('should reject invalid US phone length', () => {
      expect(isValidPhoneNumber('+1555123')).toBe(false);
      expect(isValidPhoneNumber('+1555123456789')).toBe(false);
    });

    it('should reject numbers with letters', () => {
      expect(isValidPhoneNumber('+1555ABC4567')).toBe(false);
    });
  });

  describe('formatPhoneNumber', () => {
    it('should format US phone number', () => {
      expect(formatPhoneNumber('+15551234567')).toBe('+1 (555) 123-4567');
    });

    it('should preserve international format', () => {
      expect(formatPhoneNumber('+442071234567')).toBe('+442071234567');
    });

    it('should handle invalid format gracefully', () => {
      expect(formatPhoneNumber('+1555')).toBe('+1555');
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty strings', () => {
      expect(extractPhoneFromEmail('')).toBeNull();
      expect(extractPhoneFromSubject('')).toBeNull();
      expect(extractPhoneFromBody('')).toBeNull();
    });

    it('should handle undefined inputs gracefully', () => {
      expect(extractPhoneFromHeaders({})).toBeNull();
    });

    it('should handle phone numbers with extensions', () => {
      const result = extractPhoneFromSubject('555-123-4567 ext 123');
      expect(result).toBeDefined();
      expect(result?.phoneNumber).toBe('+15551234567');
    });

    it('should handle multiple phone numbers (take first)', () => {
      const result = extractPhoneFromBody('Call 555-123-4567 or 555-999-8888');
      expect(result).toBeDefined();
      expect(result?.phoneNumber).toBe('+15551234567');
    });

    it('should handle international UK numbers', () => {
      const normalized = normalizePhoneNumber('442071234567');
      expect(normalized).toBe('+442071234567');
      expect(isValidPhoneNumber(normalized)).toBe(true);
    });

    it('should handle toll-free numbers', () => {
      const normalized = normalizePhoneNumber('8005551234');
      expect(normalized).toBe('+18005551234');
      expect(isValidPhoneNumber(normalized)).toBe(true);
    });
  });
});
