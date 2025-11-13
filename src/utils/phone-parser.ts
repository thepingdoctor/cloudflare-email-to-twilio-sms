/**
 * Phone Number Parser and Validator
 * Extracts and validates phone numbers from email data
 */

import type { ParsedEmail, PhoneExtractionResult } from '../types';

/**
 * Extract phone number from email address (e.g., 15551234567@domain.com)
 */
export function extractPhoneFromEmail(email: string): PhoneExtractionResult | null {
  // Match phone number in email prefix (before @)
  const emailMatch = email.match(/^(\+?1?)(\d{10})@/);

  if (emailMatch) {
    const phoneNumber = normalizePhoneNumber(emailMatch[2]);
    return {
      phoneNumber,
      source: 'email_to',
      confidence: 'high',
    };
  }

  return null;
}

/**
 * Extract phone number from subject line
 */
export function extractPhoneFromSubject(subject: string): PhoneExtractionResult | null {
  // Match patterns like "To: 555-123-4567" or "555.123.4567" or "5551234567"
  const patterns = [
    /(?:to|phone|number|sms):\s*(\+?1?[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4})/i,
    /(\+?1?[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4})/,
  ];

  for (const pattern of patterns) {
    const match = subject.match(pattern);
    if (match) {
      const cleaned = match[1].replace(/[-.\s]/g, '');
      const phoneNumber = normalizePhoneNumber(cleaned);

      if (isValidPhoneNumber(phoneNumber)) {
        return {
          phoneNumber,
          source: 'subject',
          confidence: 'high',
        };
      }
    }
  }

  return null;
}

/**
 * Extract phone number from custom email header
 */
export function extractPhoneFromHeaders(headers: Record<string, string>): PhoneExtractionResult | null {
  const smsHeaders = ['x-sms-to', 'x-phone', 'x-recipient'];

  for (const header of smsHeaders) {
    const value = headers[header.toLowerCase()];
    if (value) {
      const cleaned = value.replace(/[-.\s]/g, '');
      const phoneNumber = normalizePhoneNumber(cleaned);

      if (isValidPhoneNumber(phoneNumber)) {
        return {
          phoneNumber,
          source: 'header',
          confidence: 'high',
        };
      }
    }
  }

  return null;
}

/**
 * Extract phone number from email body (last resort)
 */
export function extractPhoneFromBody(body: string): PhoneExtractionResult | null {
  // Look for phone numbers in first 200 characters
  const searchText = body.substring(0, 200);

  const pattern = /(\+?1?[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4})/;
  const match = searchText.match(pattern);

  if (match) {
    const cleaned = match[1].replace(/[-.\s]/g, '');
    const phoneNumber = normalizePhoneNumber(cleaned);

    if (isValidPhoneNumber(phoneNumber)) {
      return {
        phoneNumber,
        source: 'body',
        confidence: 'low', // Lower confidence since it's from body
      };
    }
  }

  return null;
}

/**
 * Main function to extract phone number from parsed email
 */
export function extractPhoneNumber(email: ParsedEmail): PhoneExtractionResult {
  // Try extraction in order of reliability
  const results = [
    extractPhoneFromHeaders(email.headers),
    extractPhoneFromEmail(email.to),
    extractPhoneFromSubject(email.subject),
    extractPhoneFromBody(email.text),
  ];

  // Return first successful extraction
  const result = results.find((r) => r !== null);

  if (!result) {
    throw new Error('No valid phone number found in email');
  }

  return result;
}

/**
 * Normalize phone number to E.164 format (+1XXXXXXXXXX)
 */
export function normalizePhoneNumber(phone: string, defaultCountryCode = '1'): string {
  // Remove all non-digit characters
  let cleaned = phone.replace(/\D/g, '');

  // Add country code if missing
  if (cleaned.length === 10) {
    cleaned = defaultCountryCode + cleaned;
  }

  // Add + prefix for E.164 format
  return `+${cleaned}`;
}

/**
 * Validate phone number format
 */
export function isValidPhoneNumber(phone: string): boolean {
  // E.164 format: +[country code][number]
  // Length: 11-15 digits (including country code)
  const e164Pattern = /^\+\d{11,15}$/;

  if (!e164Pattern.test(phone)) {
    return false;
  }

  // For US numbers specifically (+1XXXXXXXXXX)
  if (phone.startsWith('+1')) {
    return phone.length === 12; // +1 + 10 digits
  }

  return true;
}

/**
 * Format phone number for display
 */
export function formatPhoneNumber(phone: string): string {
  if (phone.startsWith('+1') && phone.length === 12) {
    // US format: +1 (555) 123-4567
    const digits = phone.substring(2);
    return `+1 (${digits.substring(0, 3)}) ${digits.substring(3, 6)}-${digits.substring(6)}`;
  }

  return phone;
}
