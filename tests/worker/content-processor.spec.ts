/**
 * Content Processor Tests
 * Tests email content processing and SMS conversion
 */

import { describe, it, expect } from 'vitest';
import {
  processEmailContent,
  convertHtmlToText,
  removeEmailSignature,
  normalizeWhitespace,
  smartTruncate,
  extractSenderName,
  sanitizeContent,
  containsUnicode,
  calculateSMSSegments,
} from '../../src/utils/content-processor';
import type { ParsedEmail } from '../../src/types';

describe('Content Processor', () => {
  const createEmail = (overrides: Partial<ParsedEmail> = {}): ParsedEmail => ({
    from: 'sender@example.com',
    to: 'recipient@example.com',
    subject: 'Test Subject',
    text: 'Test message',
    headers: {},
    ...overrides,
  });

  describe('processEmailContent', () => {
    it('should process basic email content', () => {
      const email = createEmail({
        from: 'john@example.com',
        subject: 'Hello',
        text: 'This is a test message',
      });

      const result = processEmailContent(email);

      expect(result).toContain('From: john');
      expect(result).toContain('Re: Hello');
      expect(result).toContain('This is a test message');
    });

    it('should add sender info prefix', () => {
      const email = createEmail({
        from: 'John Doe <john@example.com>',
        text: 'Message',
      });

      const result = processEmailContent(email);
      expect(result).toContain('From: John Doe');
    });

    it('should include subject when present', () => {
      const email = createEmail({
        subject: 'Important Update',
        text: 'Message',
      });

      const result = processEmailContent(email);
      expect(result).toContain('Re: Important Update');
    });

    it('should truncate long messages', () => {
      const email = createEmail({
        text: 'a'.repeat(500),
      });

      const result = processEmailContent(email, 160);
      expect(result.length).toBeLessThanOrEqual(160);
      expect(result).toContain('...');
    });

    it('should remove email signature', () => {
      const email = createEmail({
        text: 'Important message\n\n--\nJohn Doe\nSoftware Engineer',
      });

      const result = processEmailContent(email);
      expect(result).toContain('Important message');
      expect(result).not.toContain('Software Engineer');
    });

    it('should normalize whitespace', () => {
      const email = createEmail({
        text: 'Too    many     spaces\n\n\n\nAnd newlines',
      });

      const result = processEmailContent(email);
      expect(result).not.toContain('    ');
      expect(result).not.toContain('\n\n\n');
    });

    it('should prefer text over HTML', () => {
      const email = createEmail({
        text: 'Plain text message',
        html: '<p>HTML message</p>',
      });

      const result = processEmailContent(email);
      expect(result).toContain('Plain text');
      expect(result).not.toContain('HTML message');
    });

    it('should use HTML when text is empty', () => {
      const email = createEmail({
        text: '',
        html: '<p>HTML message</p>',
      });

      const result = processEmailContent(email);
      expect(result).toContain('HTML message');
    });

    it('should handle empty content gracefully', () => {
      const email = createEmail({
        text: '',
        html: '',
      });

      const result = processEmailContent(email);
      expect(result).toBeTruthy();
      expect(result).toContain('From:');
    });

    it('should respect custom max length', () => {
      const email = createEmail({
        text: 'a'.repeat(100),
      });

      const result = processEmailContent(email, 70);
      expect(result.length).toBeLessThanOrEqual(70);
    });
  });

  describe('convertHtmlToText', () => {
    it('should remove HTML tags', () => {
      const html = '<p>Hello <strong>world</strong></p>';
      const text = convertHtmlToText(html);

      expect(text).toBe('Hello world');
      expect(text).not.toContain('<p>');
      expect(text).not.toContain('<strong>');
    });

    it('should convert br tags to newlines', () => {
      const html = 'Line 1<br>Line 2<br/>Line 3';
      const text = convertHtmlToText(html);

      expect(text).toContain('\n');
      expect(text.split('\n')).toHaveLength(3);
    });

    it('should convert p tags to double newlines', () => {
      const html = '<p>Para 1</p><p>Para 2</p>';
      const text = convertHtmlToText(html);

      expect(text).toContain('Para 1');
      expect(text).toContain('Para 2');
    });

    it('should decode HTML entities', () => {
      const html = '&nbsp;&amp;&lt;&gt;&quot;';
      const text = convertHtmlToText(html);

      expect(text).toContain(' ');
      expect(text).toContain('&');
      expect(text).toContain('<');
      expect(text).toContain('>');
      expect(text).toContain('"');
    });

    it('should remove script tags', () => {
      const html = '<p>Safe</p><script>alert("xss")</script><p>Content</p>';
      const text = convertHtmlToText(html);

      expect(text).toContain('Safe');
      expect(text).toContain('Content');
      expect(text).not.toContain('alert');
      expect(text).not.toContain('script');
    });

    it('should remove style tags', () => {
      const html = '<style>body { color: red; }</style><p>Content</p>';
      const text = convertHtmlToText(html);

      expect(text).toContain('Content');
      expect(text).not.toContain('color');
      expect(text).not.toContain('style');
    });

    it('should decode numeric entities', () => {
      const html = '&#39;&#8217;&#x2019;';
      const text = convertHtmlToText(html);

      expect(text).toContain("'");
    });

    it('should handle empty HTML', () => {
      expect(convertHtmlToText('')).toBe('');
      expect(convertHtmlToText('<p></p>')).toBe('');
    });
  });

  describe('removeEmailSignature', () => {
    it('should remove standard -- signature', () => {
      const text = 'Message content\n--\nJohn Doe';
      const result = removeEmailSignature(text);

      expect(result).toBe('Message content');
      expect(result).not.toContain('John Doe');
    });

    it('should remove "Best regards" signature', () => {
      const text = 'Message\nBest regards,\nJohn';
      const result = removeEmailSignature(text);

      expect(result).toBe('Message');
    });

    it('should remove "Sincerely" signature', () => {
      const text = 'Message\nSincerely,\nJohn';
      const result = removeEmailSignature(text);

      expect(result).toBe('Message');
    });

    it('should remove "Thanks" signature', () => {
      const text = 'Message\nThanks,\nJohn';
      const result = removeEmailSignature(text);

      expect(result).toBe('Message');
    });

    it('should remove "Sent from my" mobile signature', () => {
      const text = 'Message\nSent from my iPhone';
      const result = removeEmailSignature(text);

      expect(result).toBe('Message');
    });

    it('should remove underscore separators', () => {
      const text = 'Message\n___________\nSignature';
      const result = removeEmailSignature(text);

      expect(result).toBe('Message');
    });

    it('should handle text without signature', () => {
      const text = 'Just a message';
      const result = removeEmailSignature(text);

      expect(result).toBe('Just a message');
    });

    it('should handle case-insensitive signatures', () => {
      const text = 'Message\nBEST REGARDS,\nJohn';
      const result = removeEmailSignature(text);

      expect(result).toBe('Message');
    });
  });

  describe('normalizeWhitespace', () => {
    it('should replace multiple spaces with single space', () => {
      const text = 'Too    many     spaces';
      const result = normalizeWhitespace(text);

      expect(result).toBe('Too many spaces');
    });

    it('should limit consecutive newlines to 2', () => {
      const text = 'Line 1\n\n\n\n\nLine 2';
      const result = normalizeWhitespace(text);

      expect(result).toBe('Line 1\n\nLine 2');
    });

    it('should trim whitespace from lines', () => {
      const text = '  Line 1  \n  Line 2  ';
      const result = normalizeWhitespace(text);

      expect(result).toBe('Line 1\nLine 2');
    });

    it('should handle mixed whitespace issues', () => {
      const text = '  Too    many  \n\n\n\n  spaces  ';
      const result = normalizeWhitespace(text);

      expect(result).not.toContain('    ');
      expect(result).not.toContain('\n\n\n');
    });

    it('should trim final result', () => {
      const text = '   Content   ';
      const result = normalizeWhitespace(text);

      expect(result).toBe('Content');
    });
  });

  describe('smartTruncate', () => {
    it('should not truncate short text', () => {
      const text = 'Short message';
      const result = smartTruncate(text, 100);

      expect(result).toBe('Short message');
    });

    it('should truncate at sentence boundary', () => {
      const text = 'First sentence. Second sentence. Third sentence.';
      const result = smartTruncate(text, 30);

      expect(result).toContain('First sentence.');
      expect(result).toContain('...');
      expect(result).not.toContain('Third');
    });

    it('should truncate at word boundary', () => {
      const text = 'This is a long message without punctuation marks';
      const result = smartTruncate(text, 20);

      expect(result).toContain('...');
      expect(result.replace('...', '').trim()).not.toContain(' long message');
    });

    it('should hard truncate as last resort', () => {
      const text = 'Verylongwordwithoutspacesorpunctuation';
      const result = smartTruncate(text, 20);

      expect(result.length).toBe(20);
      expect(result).toContain('...');
    });

    it('should add ellipsis when truncated', () => {
      const text = 'a'.repeat(100);
      const result = smartTruncate(text, 50);

      expect(result).toContain('...');
      expect(result.length).toBeLessThanOrEqual(50);
    });
  });

  describe('extractSenderName', () => {
    it('should extract name from "Name <email>" format', () => {
      const email = 'John Doe <john@example.com>';
      const name = extractSenderName(email);

      expect(name).toBe('John Doe');
    });

    it('should remove quotes from name', () => {
      const email = '"John Doe" <john@example.com>';
      const name = extractSenderName(email);

      expect(name).toBe('John Doe');
    });

    it('should extract from email prefix if no name', () => {
      const email = 'john.doe@example.com';
      const name = extractSenderName(email);

      expect(name).toBe('john doe');
    });

    it('should replace underscores and hyphens', () => {
      const email = 'john_doe-smith@example.com';
      const name = extractSenderName(email);

      expect(name).toBe('john doe smith');
    });

    it('should handle email-only format', () => {
      const email = 'simple@example.com';
      const name = extractSenderName(email);

      expect(name).toBe('simple');
    });

    it('should return full email if parsing fails', () => {
      const email = 'invalid';
      const name = extractSenderName(email);

      expect(name).toBe('invalid');
    });
  });

  describe('sanitizeContent', () => {
    it('should replace email addresses', () => {
      const text = 'Contact john@example.com for help';
      const result = sanitizeContent(text);

      expect(result).toContain('[email]');
      expect(result).not.toContain('john@example.com');
    });

    it('should remove control characters', () => {
      const text = 'Text\x00with\x01control\x1Fchars';
      const result = sanitizeContent(text);

      expect(result).toBe('Textwithcontrolchars');
    });

    it('should handle multiple email addresses', () => {
      const text = 'Email john@example.com or jane@example.com';
      const result = sanitizeContent(text);

      expect((result.match(/\[email\]/g) || []).length).toBe(2);
    });
  });

  describe('containsUnicode', () => {
    it('should detect emoji as Unicode', () => {
      expect(containsUnicode('Hello 😀')).toBe(true);
      expect(containsUnicode('Test 🚀🎉')).toBe(true);
    });

    it('should detect non-ASCII characters', () => {
      expect(containsUnicode('Hello 中文')).toBe(true);
      expect(containsUnicode('مرحبا')).toBe(true);
    });

    it('should not detect ASCII as Unicode', () => {
      expect(containsUnicode('Hello World')).toBe(false);
      expect(containsUnicode('Test 123 !@#')).toBe(false);
    });

    it('should handle empty string', () => {
      expect(containsUnicode('')).toBe(false);
    });
  });

  describe('calculateSMSSegments', () => {
    it('should count 1 segment for short ASCII', () => {
      const text = 'Short message';
      expect(calculateSMSSegments(text)).toBe(1);
    });

    it('should count 1 segment for 160 char ASCII', () => {
      const text = 'a'.repeat(160);
      expect(calculateSMSSegments(text)).toBe(1);
    });

    it('should count 2 segments for 161+ char ASCII', () => {
      const text = 'a'.repeat(161);
      expect(calculateSMSSegments(text)).toBe(2);
    });

    it('should count 1 segment for 70 char Unicode', () => {
      const text = '😀'.repeat(70);
      expect(calculateSMSSegments(text)).toBe(1);
    });

    it('should count 2 segments for 71+ char Unicode', () => {
      const text = '😀'.repeat(71);
      expect(calculateSMSSegments(text)).toBe(2);
    });

    it('should use multi-part limits for long messages', () => {
      const text = 'a'.repeat(306); // 2 segments at 153 chars each
      expect(calculateSMSSegments(text)).toBe(2);
    });
  });

  describe('Edge Cases', () => {
    it('should handle only whitespace content', () => {
      const email = createEmail({ text: '   \n\n\n   ' });
      const result = processEmailContent(email);

      expect(result).toBeTruthy();
      expect(result.trim()).not.toBe('');
    });

    it('should handle malformed HTML', () => {
      const html = '<p>Unclosed paragraph<div>Nested';
      const text = convertHtmlToText(html);

      expect(text).toContain('Unclosed');
      expect(text).toContain('Nested');
    });

    it('should handle special characters in sender name', () => {
      const email = 'John "The Boss" Doe <john@example.com>';
      const name = extractSenderName(email);

      expect(name).toBe('John The Boss Doe');
    });

    it('should preserve important punctuation', () => {
      const text = 'Price: $100! Get it now.';
      const result = normalizeWhitespace(text);

      expect(result).toContain('$');
      expect(result).toContain('!');
      expect(result).toContain('.');
    });

    it('should handle extremely long single words', () => {
      const text = 'a'.repeat(1000);
      const result = smartTruncate(text, 160);

      expect(result.length).toBeLessThanOrEqual(160);
    });

    it('should handle mixed content types', () => {
      const email = createEmail({
        text: 'Text content',
        html: '<p>HTML content</p>',
      });

      const result = processEmailContent(email);
      expect(result).toContain('Text content');
    });
  });
});
