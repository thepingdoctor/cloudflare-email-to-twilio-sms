/**
 * Security Tests
 * Tests security vulnerabilities and attack prevention
 */

import { describe, it, expect } from 'vitest';
import { sanitizeContent } from '../../src/utils/content-processor';
import { convertHtmlToText } from '../../src/utils/content-processor';
import { isValidPhoneNumber } from '../../src/utils/phone-parser';
import testData from '../fixtures/test-data.json';

describe('Security Tests', () => {
  describe('XSS Attack Prevention', () => {
    it('should remove script tags from HTML', () => {
      const attacks = testData.security_payloads.xss_attacks;

      attacks.forEach(attack => {
        const sanitized = convertHtmlToText(attack);

        expect(sanitized).not.toContain('<script');
        expect(sanitized).not.toContain('javascript:');
        expect(sanitized).not.toContain('onerror=');
        expect(sanitized).not.toContain('onload=');
      });
    });

    it('should handle basic XSS payload', () => {
      const xss = '<script>alert("xss")</script>';
      const result = convertHtmlToText(xss);

      expect(result).not.toContain('script');
      expect(result).not.toContain('alert');
    });

    it('should handle img tag XSS', () => {
      const xss = '<img src=x onerror=alert("xss")>';
      const result = convertHtmlToText(xss);

      expect(result).not.toContain('onerror');
      expect(result).not.toContain('alert');
    });

    it('should handle svg XSS', () => {
      const xss = '<svg onload=alert("xss")>';
      const result = convertHtmlToText(xss);

      expect(result).not.toContain('onload');
      expect(result).not.toContain('alert');
    });

    it('should handle nested script tags', () => {
      const xss = '<<SCRIPT>alert("xss");//<</SCRIPT>';
      const result = convertHtmlToText(xss);

      expect(result).not.toContain('SCRIPT');
      expect(result).not.toContain('alert');
    });

    it('should decode HTML entities safely', () => {
      const html = '&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;';
      const result = convertHtmlToText(html);

      // Should decode to text, not execute
      expect(result).not.toContain('<script>');
    });
  });

  describe('SQL Injection Prevention', () => {
    it('should handle SQL injection payloads safely', () => {
      const attacks = testData.security_payloads.sql_injection;

      attacks.forEach(attack => {
        // Content processor should not execute SQL
        const processed = sanitizeContent(attack);

        // Should preserve the text but not execute
        expect(processed).toBeTruthy();
        expect(typeof processed).toBe('string');
      });
    });

    it('should handle DROP TABLE attack', () => {
      const sql = "'; DROP TABLE users; --";

      // Should be treated as plain text
      expect(() => sanitizeContent(sql)).not.toThrow();
    });

    it('should handle UNION SELECT attack', () => {
      const sql = "' UNION SELECT NULL, NULL, NULL--";

      expect(() => sanitizeContent(sql)).not.toThrow();
    });
  });

  describe('XML Injection Prevention', () => {
    it('should handle XML injection in content', () => {
      const attacks = testData.security_payloads.xml_injection;

      attacks.forEach(attack => {
        const processed = convertHtmlToText(attack);

        // Should not contain XML declarations
        expect(processed).not.toContain('<?xml');
        expect(processed).not.toContain('<!DOCTYPE');
        expect(processed).not.toContain('<!ENTITY');
      });
    });

    it('should handle XXE injection attempt', () => {
      const xxe = '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>';
      const result = convertHtmlToText(xxe);

      expect(result).not.toContain('SYSTEM');
      expect(result).not.toContain('/etc/passwd');
    });

    it('should handle malicious TwiML injection', () => {
      const malicious = '</Response><Malicious>evil</Malicious><Response>';
      const result = convertHtmlToText(malicious);

      // Should strip all tags
      expect(result).toBe('evil');
    });
  });

  describe('Path Traversal Prevention', () => {
    it('should handle path traversal attempts', () => {
      const attacks = testData.security_payloads.path_traversal;

      attacks.forEach(attack => {
        const processed = sanitizeContent(attack);

        // Should be treated as text, not file paths
        expect(processed).toBeTruthy();
        expect(typeof processed).toBe('string');
      });
    });

    it('should not interpret directory traversal', () => {
      const path = '../../../etc/passwd';
      const result = sanitizeContent(path);

      expect(result).toContain('../');
      // Should not actually read files
    });
  });

  describe('Template Injection Prevention', () => {
    it('should handle template injection payloads', () => {
      const attacks = testData.security_payloads.template_injection;

      attacks.forEach(attack => {
        const processed = sanitizeContent(attack);

        // Should not evaluate templates
        expect(processed).not.toContain('49'); // 7*7=49
        expect(processed).toBeTruthy();
      });
    });

    it('should handle mustache template injection', () => {
      const template = '{{7*7}}';
      const result = sanitizeContent(template);

      // Should preserve as text, not evaluate
      expect(result).toContain('{{7*7}}');
    });

    it('should handle environment variable injection', () => {
      const env = '${process.env.SECRET_KEY}';
      const result = sanitizeContent(env);

      // Should not evaluate
      expect(result).toContain('${process.env.SECRET_KEY}');
    });
  });

  describe('Command Injection Prevention', () => {
    it('should handle command injection payloads', () => {
      const attacks = testData.security_payloads.command_injection;

      attacks.forEach(attack => {
        const processed = sanitizeContent(attack);

        // Should be treated as text, not executed
        expect(processed).toBeTruthy();
        expect(typeof processed).toBe('string');
      });
    });

    it('should handle shell command injection', () => {
      const cmd = '; ls -la';
      const result = sanitizeContent(cmd);

      expect(result).toContain('; ls -la');
    });

    it('should handle backtick command execution', () => {
      const cmd = '`whoami`';
      const result = sanitizeContent(cmd);

      expect(result).toContain('`whoami`');
    });
  });

  describe('Phone Number Validation Security', () => {
    it('should reject invalid phone formats', () => {
      const invalidPhones = [
        '555-1234',
        '123',
        'phone',
        '<script>alert("xss")</script>',
        '"; DROP TABLE;',
        '../../../etc/passwd',
      ];

      invalidPhones.forEach(phone => {
        expect(isValidPhoneNumber(phone)).toBe(false);
      });
    });

    it('should only accept E.164 format', () => {
      expect(isValidPhoneNumber('+15551234567')).toBe(true);
      expect(isValidPhoneNumber('5551234567')).toBe(false);
      expect(isValidPhoneNumber('(555) 123-4567')).toBe(false);
    });

    it('should reject phones with special characters', () => {
      expect(isValidPhoneNumber('+1555<script>')).toBe(false);
      expect(isValidPhoneNumber('+1555; DROP TABLE')).toBe(false);
    });

    it('should validate length constraints', () => {
      expect(isValidPhoneNumber('+1555')).toBe(false); // Too short
      expect(isValidPhoneNumber('+' + '1'.repeat(20))).toBe(false); // Too long
    });
  });

  describe('Email Content Sanitization', () => {
    it('should remove control characters', () => {
      const malicious = 'Text\x00with\x01control\x1Fchars';
      const result = sanitizeContent(malicious);

      expect(result).toBe('Textwithcontrolchars');
      expect(result).not.toContain('\x00');
    });

    it('should sanitize email addresses to prevent loops', () => {
      const content = 'Reply to admin@example.com for help';
      const result = sanitizeContent(content);

      expect(result).toContain('[email]');
      expect(result).not.toContain('admin@example.com');
    });

    it('should handle multiple email addresses', () => {
      const content = 'Contact alice@example.com or bob@example.com';
      const result = sanitizeContent(content);

      const emailCount = (result.match(/\[email\]/g) || []).length;
      expect(emailCount).toBe(2);
    });
  });

  describe('Unicode and Encoding Attacks', () => {
    it('should handle Unicode normalization attacks', () => {
      // Unicode characters that look similar but are different
      const normalized = 'café'; // Normal
      const denormalized = 'café'; // With combining character

      const result1 = sanitizeContent(normalized);
      const result2 = sanitizeContent(denormalized);

      expect(result1).toBeTruthy();
      expect(result2).toBeTruthy();
    });

    it('should handle emoji in content', () => {
      const emoji = 'Test 😀🚀🎉';
      const result = sanitizeContent(emoji);

      expect(result).toContain('Test');
      // Emoji should be preserved
      expect(result).toContain('😀');
    });

    it('should handle RTL override attacks', () => {
      const rtl = 'Test\u202Emalicious';
      const result = sanitizeContent(rtl);

      expect(result).toBeTruthy();
    });

    it('should handle null byte injection', () => {
      const nullByte = 'test\0malicious';
      const result = sanitizeContent(nullByte);

      expect(result).not.toContain('\0');
    });
  });

  describe('Length-Based Attacks', () => {
    it('should handle extremely long content', () => {
      const veryLong = 'a'.repeat(100000);

      expect(() => sanitizeContent(veryLong)).not.toThrow();
    });

    it('should handle empty content', () => {
      expect(() => sanitizeContent('')).not.toThrow();
    });

    it('should handle content with only whitespace', () => {
      const whitespace = ' \t\n\r ';
      const result = sanitizeContent(whitespace);

      expect(result).toBe('');
    });
  });

  describe('HTML Entity Double Decoding', () => {
    it('should not double-decode entities', () => {
      const doubleEncoded = '&amp;lt;script&amp;gt;';
      const result = convertHtmlToText(doubleEncoded);

      // Should decode once to &lt;script&gt;, not to <script>
      expect(result).not.toContain('<script>');
    });

    it('should handle nested entity encoding', () => {
      const nested = '&amp;#60;script&amp;#62;';
      const result = convertHtmlToText(nested);

      expect(result).not.toContain('<script>');
    });
  });

  describe('CRLF Injection', () => {
    it('should handle CRLF injection attempts', () => {
      const crlf = 'test\r\nMalicious-Header: value';
      const result = sanitizeContent(crlf);

      expect(result).toBeTruthy();
      // Should not interpret as HTTP header
    });

    it('should handle line break variations', () => {
      const variations = [
        'test\r\nmalicious',
        'test\rmalicious',
        'test\nmalicious',
      ];

      variations.forEach(variant => {
        expect(() => sanitizeContent(variant)).not.toThrow();
      });
    });
  });

  describe('ReDoS (Regular Expression DoS)', () => {
    it('should handle patterns prone to catastrophic backtracking', () => {
      // Pattern that could cause ReDoS
      const evil = 'a'.repeat(50) + '!';

      // Should complete quickly
      const start = Date.now();
      sanitizeContent(evil);
      const duration = Date.now() - start;

      expect(duration).toBeLessThan(1000); // Should be instant
    });

    it('should handle nested quantifiers', () => {
      const pattern = '(' + 'a+'.repeat(10) + ')+';

      expect(() => sanitizeContent(pattern)).not.toThrow();
    });
  });

  describe('Content Spoofing', () => {
    it('should handle homograph attacks in content', () => {
      // Cyrillic 'а' looks like Latin 'a'
      const homograph = 'pаypal.com'; // 'а' is Cyrillic

      const result = sanitizeContent(homograph);
      expect(result).toBeTruthy();
    });

    it('should handle zero-width characters', () => {
      const zeroWidth = 'test\u200Bmalicious';
      const result = sanitizeContent(zeroWidth);

      expect(result).toBeTruthy();
    });
  });

  describe('Integration with Real Attack Payloads', () => {
    it('should handle combined XSS + SQL injection', () => {
      const combined = '<script>alert("xss")</script>\'; DROP TABLE users; --';
      const html = convertHtmlToText(combined);
      const sanitized = sanitizeContent(html);

      expect(sanitized).not.toContain('script');
      expect(sanitized).not.toContain('<');
      expect(sanitized).toBeTruthy();
    });

    it('should handle layered encoding attacks', () => {
      const layered = '%3Cscript%3Ealert%28%22xss%22%29%3C%2Fscript%3E';

      expect(() => sanitizeContent(layered)).not.toThrow();
    });

    it('should handle polyglot payloads', () => {
      const polyglot = 'jaVasCript:/*-/*`/*\`/*\'/*"/**/(/* */oNcliCk=alert() )//%0D%0A%0d%0a//</stYle/</titLe/</teXtarEa/</scRipt/--!>\x3csVg/<sVg/oNloAd=alert()//>\x3e';

      const result = convertHtmlToText(polyglot);
      expect(result).not.toContain('oNcliCk');
      expect(result).not.toContain('oNloAd');
    });
  });
});
