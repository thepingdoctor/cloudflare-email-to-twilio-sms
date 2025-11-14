/**
 * Twilio SMS Service
 * Handles SMS sending via Twilio API
 */

import type { Env, SMSMessage, TwilioMessageResponse } from '../types';
import { Logger } from '../utils/logger';

/**
 * Twilio API configuration
 */
const TWILIO_API_BASE = 'https://api.twilio.com/2010-04-01';

/**
 * Twilio service class
 */
export class TwilioService {
  private accountSid: string;
  private authToken: string;
  private fromNumber: string;
  private logger: Logger;

  constructor(env: Env, logger: Logger) {
    this.accountSid = env.TWILIO_ACCOUNT_SID;
    this.authToken = env.TWILIO_AUTH_TOKEN;
    this.fromNumber = env.TWILIO_PHONE_NUMBER;
    this.logger = logger;

    // Validate credentials
    if (!this.accountSid || !this.authToken || !this.fromNumber) {
      throw new Error('Missing required Twilio credentials');
    }

    if (!this.accountSid.startsWith('AC')) {
      throw new Error('Invalid Twilio Account SID format');
    }

    if (!this.fromNumber.startsWith('+')) {
      throw new Error('Twilio phone number must be in E.164 format (+1XXXXXXXXXX)');
    }
  }

  /**
   * Send SMS message via Twilio API
   */
  async sendSMS(message: SMSMessage): Promise<TwilioMessageResponse> {
    this.logger.info('Sending SMS via Twilio', {
      to: message.to,
      from: message.from,
      bodyLength: message.body.length,
    });

    const url = `${TWILIO_API_BASE}/Accounts/${this.accountSid}/Messages.json`;

    // Create form data
    const formData = new URLSearchParams();
    formData.append('To', message.to);
    formData.append('From', message.from);
    formData.append('Body', message.body);

    // Add status callback (optional)
    // formData.append('StatusCallback', 'https://your-worker.com/sms-status');

    try {
      const response = await this.makeRequest(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Authorization': this.createAuthHeader(),
        },
        body: formData.toString(),
      });

      if (!response.ok) {
        // Parse error response with graceful fallback
        let errorData: { message?: string; code?: number } = {};
        try {
          const contentType = response.headers?.get?.('Content-Type') || '';
          if (contentType.includes('application/json')) {
            errorData = await response.json() as { message?: string; code?: number };
          } else {
            // Try to parse as JSON anyway (some APIs don't set Content-Type correctly)
            try {
              errorData = await response.json() as { message?: string; code?: number };
            } catch {
              // Non-JSON response fallback
              const errorText = await response.text();
              errorData = {
                message: errorText || `HTTP ${response.status}`,
                code: response.status
              };
            }
          }
        } catch (parseError) {
          // If parsing fails, use generic error
          this.logger.warn('Failed to parse error response', {
            parseError: parseError instanceof Error ? parseError.message : 'Unknown',
            status: response.status,
          });
          errorData = {
            message: `HTTP ${response.status}`,
            code: response.status
          };
        }

        // Handle rate limiting (429 Too Many Requests) - check after parsing
        if (response.status === 429) {
          const retryAfter = response.headers?.get?.('Retry-After');
          const retrySeconds = retryAfter ? parseInt(retryAfter, 10) : 60;

          this.logger.warn('Twilio rate limit reached', {
            status: response.status,
            retryAfter: retrySeconds,
            url,
            message: errorData.message,
          });
        }

        // Log detailed error context for debugging
        this.logger.error('Twilio API request failed', new Error(errorData.message || 'Unknown error'), {
          status: response.status,
          twilioCode: errorData.code,
          message: errorData.message,
          url,
        });

        throw new TwilioError(
          errorData.message || 'Twilio API request failed',
          response.status,
          errorData.code
        );
      }

      const result = await response.json() as TwilioMessageResponse;

      this.logger.info('SMS sent successfully', {
        sid: result.sid,
        status: result.status,
        to: result.to,
      });

      return result;
    } catch (error) {
      this.logger.error('Failed to send SMS', error, {
        to: message.to,
        from: message.from,
      });

      if (error instanceof TwilioError) {
        throw error;
      }

      throw new TwilioError('Failed to send SMS: ' + (error instanceof Error ? error.message : 'Unknown error'));
    }
  }

  /**
   * Make HTTP request with retry logic
   */
  private async makeRequest(url: string, options: RequestInit, retries = 3): Promise<Response> {
    let lastError: Error | null = null;

    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        const response = await fetch(url, {
          ...options,
          signal: AbortSignal.timeout(10000), // 10 second timeout
        });

        return response;
      } catch (error) {
        lastError = error instanceof Error ? error : new Error('Unknown error');
        this.logger.warn(`Request attempt ${attempt} failed`, {
          error: lastError.message,
          attempt,
          retries,
        });

        if (attempt < retries) {
          // Exponential backoff: 1s, 2s, 4s
          const delay = Math.pow(2, attempt - 1) * 1000;
          await this.sleep(delay);
        }
      }
    }

    throw lastError || new Error('Request failed after retries');
  }

  /**
   * Create Basic Auth header
   */
  private createAuthHeader(): string {
    const credentials = btoa(`${this.accountSid}:${this.authToken}`);
    return `Basic ${credentials}`;
  }

  /**
   * Sleep helper
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Validate phone number format
   */
  static validatePhoneNumber(phone: string): boolean {
    // E.164 format: +[country code][number]
    const e164Pattern = /^\+\d{11,15}$/;
    return e164Pattern.test(phone);
  }

  /**
   * Check if Twilio credentials are configured
   */
  static isConfigured(env: Env): boolean {
    return !!(
      env.TWILIO_ACCOUNT_SID &&
      env.TWILIO_AUTH_TOKEN &&
      env.TWILIO_PHONE_NUMBER
    );
  }
}

/**
 * Custom error class for Twilio errors
 */
export class TwilioError extends Error {
  constructor(
    message: string,
    public code?: number,
    public twilioCode?: number
  ) {
    super(message);
    this.name = 'TwilioError';
  }
}

/**
 * Create Twilio service instance
 */
export function createTwilioService(env: Env, logger: Logger): TwilioService {
  return new TwilioService(env, logger);
}
