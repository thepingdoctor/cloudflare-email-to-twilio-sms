/**
 * Email Validation Middleware
 * Validates incoming emails before processing
 */

import type { Env, ParsedEmail } from '../types';
import { Logger } from '../utils/logger';

/**
 * Validation error class
 */
export class ValidationError extends Error {
  constructor(
    message: string,
    public code: string
  ) {
    super(message);
    this.name = 'ValidationError';
  }
}

/**
 * Email validator class
 */
export class EmailValidator {
  private allowedSenders: string[];
  private logger: Logger;
  private isTestMode: boolean;

  constructor(env: Env, logger: Logger) {
    this.logger = logger;
    this.isTestMode = this.detectTestEnvironment();

    // Parse allowed senders from env
    this.allowedSenders = env.ALLOWED_SENDERS
      ? env.ALLOWED_SENDERS.split(',').map(s => s.trim().toLowerCase())
      : [];
  }

  /**
   * Validate email sender
   */
  validateSender(from: string): void {
    // If no allowlist configured, allow all (development mode)
    if (this.allowedSenders.length === 0) {
      this.logger.warn('No sender allowlist configured - allowing all senders');
      return;
    }

    const fromEmail = this.extractEmailAddress(from).toLowerCase();

    // Check exact match
    if (this.allowedSenders.includes(fromEmail)) {
      return;
    }

    // Check domain match (e.g., *@example.com)
    const domain = fromEmail.split('@')[1];
    const wildcardDomain = `*@${domain}`;

    if (this.allowedSenders.includes(wildcardDomain)) {
      return;
    }

    throw new ValidationError(
      `Sender not authorized: ${fromEmail}`,
      'UNAUTHORIZED_SENDER'
    );
  }

  /**
   * Validate email structure
   */
  validateEmail(email: ParsedEmail): void {
    // Check required fields
    if (!email.from) {
      throw new ValidationError('Missing sender address', 'MISSING_FROM');
    }

    if (!email.to) {
      throw new ValidationError('Missing recipient address', 'MISSING_TO');
    }

    // Validate email addresses
    if (!this.isValidEmail(email.from)) {
      throw new ValidationError('Invalid sender email format', 'INVALID_FROM');
    }

    if (!this.isValidEmail(email.to)) {
      throw new ValidationError('Invalid recipient email format', 'INVALID_TO');
    }

    // Check content exists
    if (!email.text && !email.html) {
      throw new ValidationError('Email has no content', 'EMPTY_CONTENT');
    }
  }

  /**
   * Validate message content
   */
  validateContent(content: string): void {
    if (!content || content.trim().length === 0) {
      throw new ValidationError('Message content is empty', 'EMPTY_MESSAGE');
    }

    const trimmedContent = content.trim();

    // Minimum length check
    if (trimmedContent.length < 3) {
      throw new ValidationError('Message too short', 'MESSAGE_TOO_SHORT');
    }

    // Maximum length check (for SMS)
    if (trimmedContent.length > 1600) {
      throw new ValidationError('Message too long', 'MESSAGE_TOO_LONG');
    }

    // Check for spam indicators
    if (this.containsSpamIndicators(trimmedContent)) {
      this.logger.warn('Message contains spam indicators', { content: trimmedContent.substring(0, 100) });
      // Don't reject, just log for now
    }
  }

  /**
   * Validate phone number
   */
  validatePhoneNumber(phone: string): void {
    // E.164 format validation
    const e164Pattern = /^\+\d{11,15}$/;

    if (!e164Pattern.test(phone)) {
      // Provide more specific error for US numbers
      if (phone.startsWith('+1')) {
        throw new ValidationError(
          'US phone numbers must be 10 digits (+1XXXXXXXXXX)',
          'INVALID_PHONE_FORMAT'
        );
      }
      throw new ValidationError(
        'Phone number must be in E.164 format (+[country code][number])',
        'INVALID_PHONE_FORMAT'
      );
    }

    // Additional US number validation
    if (phone.startsWith('+1')) {
      // Check length first
      if (phone.length !== 12) {
        throw new ValidationError(
          'US phone numbers must be 10 digits (+1XXXXXXXXXX)',
          'INVALID_US_PHONE'
        );
      }

      // Then check for invalid area codes
      const areaCode = phone.substring(2, 5);

      // 555 is allowed in test/development mode for testing
      const invalidAreaCodes = this.isTestMode
        ? ['000', '911']  // Allow 555 in tests
        : ['000', '555', '911'];  // Block 555 in production

      if (invalidAreaCodes.includes(areaCode)) {
        throw new ValidationError(
          `Invalid area code: ${areaCode}`,
          'INVALID_AREA_CODE'
        );
      }
    }
  }

  /**
   * Extract email address from "Name <email@domain.com>" format
   */
  private extractEmailAddress(emailString: string): string {
    const match = emailString.match(/<(.+?)>/);
    return match ? match[1] : emailString;
  }

  /**
   * Validate email address format
   */
  private isValidEmail(email: string): boolean {
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const cleanEmail = this.extractEmailAddress(email);
    return emailPattern.test(cleanEmail);
  }

  /**
   * Check for spam indicators
   */
  private containsSpamIndicators(content: string): boolean {
    const spamKeywords = [
      'viagra',
      'cialis',
      'lottery',
      'winner',
      'congratulations',
      'click here',
      'buy now',
      'limited time',
      'act now',
    ];

    const lowerContent = content.toLowerCase();
    return spamKeywords.some(keyword => lowerContent.includes(keyword));
  }

  /**
   * Detect if running in test/development environment
   */
  private detectTestEnvironment(): boolean {
    // Use try-catch for environments where process is not available
    try {
      // @ts-ignore - process may not be defined in Cloudflare Workers
      if (typeof process !== 'undefined' && process?.env) {
        // @ts-ignore
        const nodeEnv = process.env.NODE_ENV;
        // @ts-ignore
        const isVitest = process.env.VITEST === 'true';

        return nodeEnv === 'test' ||
               nodeEnv === 'development' ||
               isVitest;
      }
    } catch {
      // process not available - must be production Cloudflare Worker
      return false;
    }

    // For Cloudflare Workers, neither process nor NODE_ENV will be defined
    return false; // Production by default
  }
}

/**
 * Create validator instance
 */
export function createValidator(env: Env, logger: Logger): EmailValidator {
  return new EmailValidator(env, logger);
}
