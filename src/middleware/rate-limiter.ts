/**
 * Rate Limiter Middleware
 * Prevents abuse by limiting requests per sender/recipient
 */

import type { Env, RateLimitResult } from '../types';
import { Logger } from '../utils/logger';

/**
 * Rate limit configuration
 */
interface RateLimitConfig {
  windowMs: number;      // Time window in milliseconds
  maxRequests: number;   // Max requests per window
}

/**
 * Default rate limits
 */
const DEFAULT_LIMITS: Record<string, RateLimitConfig> = {
  perSender: {
    windowMs: 60 * 60 * 1000, // 1 hour
    maxRequests: 10,
  },
  perRecipient: {
    windowMs: 60 * 60 * 1000, // 1 hour
    maxRequests: 20,
  },
  global: {
    windowMs: 24 * 60 * 60 * 1000, // 24 hours
    maxRequests: 1000,
  },
};

/**
 * Rate limiter class
 */
export class RateLimiter {
  private env: Env;
  private logger: Logger;

  constructor(env: Env, logger: Logger) {
    this.env = env;
    this.logger = logger;
  }

  /**
   * Check if sender is rate limited
   */
  async checkSenderLimit(sender: string): Promise<RateLimitResult> {
    return this.checkLimit(
      `sender:${this.normalizeEmail(sender)}`,
      DEFAULT_LIMITS.perSender
    );
  }

  /**
   * Check if recipient is rate limited
   */
  async checkRecipientLimit(recipient: string): Promise<RateLimitResult> {
    return this.checkLimit(
      `recipient:${this.normalizePhone(recipient)}`,
      DEFAULT_LIMITS.perRecipient
    );
  }

  /**
   * Check global rate limit
   */
  async checkGlobalLimit(): Promise<RateLimitResult> {
    return this.checkLimit('global', DEFAULT_LIMITS.global);
  }

  /**
   * Core rate limit check function
   */
  private async checkLimit(
    key: string,
    config: RateLimitConfig
  ): Promise<RateLimitResult> {
    // If no KV namespace, skip rate limiting
    if (!this.env.EMAIL_SMS_KV) {
      this.logger.warn('Rate limiting disabled - no KV namespace configured');
      return {
        allowed: true,
        remaining: config.maxRequests,
        resetAt: Date.now() + config.windowMs,
      };
    }

    const now = Date.now();
    const rateLimitKey = `ratelimit:${key}`;

    try {
      // Get current count from KV
      const data = await this.env.EMAIL_SMS_KV.get(rateLimitKey, 'json') as {
        count: number;
        resetAt: number;
      } | null;

      let count = 0;
      let resetAt = now + config.windowMs;

      if (data) {
        // Check if window has expired
        if (now >= data.resetAt) {
          // Window expired, reset counter
          count = 1;
          resetAt = now + config.windowMs;
        } else {
          // Window still valid, increment counter
          count = data.count + 1;
          resetAt = data.resetAt;
        }
      } else {
        // First request in window
        count = 1;
        resetAt = now + config.windowMs;
      }

      // Check if limit exceeded
      if (count > config.maxRequests) {
        this.logger.warn('Rate limit exceeded', {
          key,
          count,
          limit: config.maxRequests,
          resetAt: new Date(resetAt).toISOString(),
        });

        return {
          allowed: false,
          remaining: 0,
          resetAt,
          reason: `Rate limit exceeded. Try again at ${new Date(resetAt).toISOString()}`,
        };
      }

      // Update counter in KV
      await this.env.EMAIL_SMS_KV.put(
        rateLimitKey,
        JSON.stringify({ count, resetAt }),
        {
          expirationTtl: Math.ceil(config.windowMs / 1000), // Convert to seconds
        }
      );

      return {
        allowed: true,
        remaining: config.maxRequests - count,
        resetAt,
      };
    } catch (error) {
      this.logger.error('Rate limit check failed', error, { key });

      // On error, allow request but log it
      return {
        allowed: true,
        remaining: config.maxRequests,
        resetAt: now + config.windowMs,
      };
    }
  }

  /**
   * Normalize email for consistent storage
   */
  private normalizeEmail(email: string): string {
    // Extract email from "Name <email@domain.com>" format
    const match = email.match(/<(.+?)>/);
    const cleanEmail = match ? match[1] : email;
    return cleanEmail.toLowerCase().trim();
  }

  /**
   * Normalize phone number for consistent storage
   */
  private normalizePhone(phone: string): string {
    // Remove all non-digit characters except leading +
    return phone.replace(/[^\d+]/g, '');
  }

  /**
   * Reset rate limit for a key (admin use)
   */
  async resetLimit(key: string): Promise<void> {
    if (!this.env.EMAIL_SMS_KV) {
      return;
    }

    const rateLimitKey = `ratelimit:${key}`;
    await this.env.EMAIL_SMS_KV.delete(rateLimitKey);

    this.logger.info('Rate limit reset', { key });
  }

  /**
   * Get current rate limit status
   */
  async getLimitStatus(key: string): Promise<RateLimitResult | null> {
    if (!this.env.EMAIL_SMS_KV) {
      return null;
    }

    const rateLimitKey = `ratelimit:${key}`;
    const data = await this.env.EMAIL_SMS_KV.get(rateLimitKey, 'json') as {
      count: number;
      resetAt: number;
    } | null;

    if (!data) {
      return null;
    }

    const config = DEFAULT_LIMITS.perSender; // Use default config for status

    return {
      allowed: data.count <= config.maxRequests,
      remaining: Math.max(0, config.maxRequests - data.count),
      resetAt: data.resetAt,
    };
  }
}

/**
 * Create rate limiter instance
 */
export function createRateLimiter(env: Env, logger: Logger): RateLimiter {
  return new RateLimiter(env, logger);
}
