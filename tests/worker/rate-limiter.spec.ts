/**
 * Rate Limiter Tests
 * Tests rate limiting functionality
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { RateLimiter, createRateLimiter } from '../../src/middleware/rate-limiter';
import { createLogger } from '../../src/utils/logger';
import type { Env } from '../../src/types';

describe('Rate Limiter', () => {
  let mockEnv: Env;
  let mockLogger: ReturnType<typeof createLogger>;
  let mockKV: KVNamespace;

  beforeEach(() => {
    // Create a mock KV that properly handles 'json' type parameter
    mockKV = {
      get: vi.fn((key: string, type?: string) => {
        const impl = (mockKV.get as any).getMockImplementation();
        const result = impl ? impl(key, type) : Promise.resolve(null);
        return result;
      }),
      put: vi.fn(),
      delete: vi.fn(),
      list: vi.fn(),
      getWithMetadata: vi.fn(),
    } as any;

    mockEnv = {
      TWILIO_ACCOUNT_SID: 'AC1234567890abcdef',
      TWILIO_AUTH_TOKEN: 'test_token',
      TWILIO_PHONE_NUMBER: '+15559999999',
      EMAIL_SMS_KV: mockKV,
    } as Env;

    mockLogger = {
      info: vi.fn(),
      warn: vi.fn(),
      error: vi.fn(),
      debug: vi.fn(),
      logTransaction: vi.fn(),
    } as any;
  });

  describe('checkSenderLimit', () => {
    it('should allow first request from sender', async () => {
      const rateLimiter = new RateLimiter(mockEnv, mockLogger);

      (mockKV.get as any).mockResolvedValue(null);
      (mockKV.put as any).mockResolvedValue(undefined);

      const result = await rateLimiter.checkSenderLimit('user@example.com');

      expect(result.allowed).toBe(true);
      expect(result.remaining).toBe(9); // 10 max - 1 used
      expect(mockKV.put).toHaveBeenCalled();
    });

    it('should track sender requests', async () => {
      const rateLimiter = new RateLimiter(mockEnv, mockLogger);

      const existingData = {
        count: 5,
        resetAt: Date.now() + 3600000, // 1 hour from now
      };

      // When 'json' type is specified, KV returns parsed object, not string
      (mockKV.get as any).mockResolvedValue(existingData);
      (mockKV.put as any).mockResolvedValue(undefined);

      const result = await rateLimiter.checkSenderLimit('user@example.com');

      expect(result.allowed).toBe(true);
      expect(result.remaining).toBe(4); // 10 max - 6 used
    });

    it('should reject when limit exceeded', async () => {
      const rateLimiter = new RateLimiter(mockEnv, mockLogger);

      const existingData = {
        count: 10, // At limit
        resetAt: Date.now() + 3600000,
      };

      // When 'json' type is specified, KV returns parsed object, not string
      (mockKV.get as any).mockResolvedValue(existingData);

      const result = await rateLimiter.checkSenderLimit('user@example.com');

      expect(result.allowed).toBe(false);
      expect(result.remaining).toBe(0);
      expect(result.reason).toBeTruthy();
      expect(mockLogger.warn).toHaveBeenCalledWith('Rate limit exceeded', expect.any(Object));
    });

    it('should reset counter after window expires', async () => {
      const rateLimiter = new RateLimiter(mockEnv, mockLogger);

      const existingData = {
        count: 10,
        resetAt: Date.now() - 1000, // Expired 1 second ago
      };

      // When 'json' type is specified, KV returns parsed object, not string
      (mockKV.get as any).mockResolvedValue(existingData);
      (mockKV.put as any).mockResolvedValue(undefined);

      const result = await rateLimiter.checkSenderLimit('user@example.com');

      expect(result.allowed).toBe(true);
      expect(result.remaining).toBe(9); // Reset to 1 used
    });

    it('should normalize email addresses', async () => {
      const rateLimiter = new RateLimiter(mockEnv, mockLogger);

      (mockKV.get as any).mockResolvedValue(null);
      (mockKV.put as any).mockResolvedValue(undefined);

      await rateLimiter.checkSenderLimit('User@Example.COM');

      const callArgs = (mockKV.get as any).mock.calls[0];
      expect(callArgs[0]).toContain('user@example.com');
    });

    it('should extract email from name format', async () => {
      const rateLimiter = new RateLimiter(mockEnv, mockLogger);

      (mockKV.get as any).mockResolvedValue(null);
      (mockKV.put as any).mockResolvedValue(undefined);

      await rateLimiter.checkSenderLimit('John Doe <john@example.com>');

      const callArgs = (mockKV.get as any).mock.calls[0];
      expect(callArgs[0]).toContain('john@example.com');
    });

    it('should allow when KV not configured', async () => {
      const envWithoutKV = { ...mockEnv, EMAIL_SMS_KV: undefined } as Env;
      const rateLimiter = new RateLimiter(envWithoutKV, mockLogger);

      const result = await rateLimiter.checkSenderLimit('user@example.com');

      expect(result.allowed).toBe(true);
      expect(mockLogger.warn).toHaveBeenCalledWith(expect.stringContaining('disabled'));
    });

    it('should handle KV errors gracefully', async () => {
      const rateLimiter = new RateLimiter(mockEnv, mockLogger);

      (mockKV.get as any).mockRejectedValue(new Error('KV error'));

      const result = await rateLimiter.checkSenderLimit('user@example.com');

      expect(result.allowed).toBe(true); // Allow on error
      expect(mockLogger.error).toHaveBeenCalled();
    });
  });

  describe('checkRecipientLimit', () => {
    it('should track recipient limits separately', async () => {
      const rateLimiter = new RateLimiter(mockEnv, mockLogger);

      (mockKV.get as any).mockResolvedValue(null);
      (mockKV.put as any).mockResolvedValue(undefined);

      const result = await rateLimiter.checkRecipientLimit('+15551234567');

      expect(result.allowed).toBe(true);
      expect(result.remaining).toBe(19); // 20 max - 1 used
      expect(mockKV.put).toHaveBeenCalled();
    });

    it('should normalize phone numbers', async () => {
      const rateLimiter = new RateLimiter(mockEnv, mockLogger);

      (mockKV.get as any).mockResolvedValue(null);
      (mockKV.put as any).mockResolvedValue(undefined);

      await rateLimiter.checkRecipientLimit('+1 (555) 123-4567');

      const callArgs = (mockKV.get as any).mock.calls[0];
      expect(callArgs[0]).toContain('+15551234567');
    });

    it('should enforce recipient limit of 20/hour', async () => {
      const rateLimiter = new RateLimiter(mockEnv, mockLogger);

      const existingData = {
        count: 20,
        resetAt: Date.now() + 3600000,
      };

      // When 'json' type is specified, KV returns parsed object, not string
      (mockKV.get as any).mockResolvedValue(existingData);

      const result = await rateLimiter.checkRecipientLimit('+15551234567');

      expect(result.allowed).toBe(false);
    });
  });

  describe('checkGlobalLimit', () => {
    it('should track global limits', async () => {
      const rateLimiter = new RateLimiter(mockEnv, mockLogger);

      (mockKV.get as any).mockResolvedValue(null);
      (mockKV.put as any).mockResolvedValue(undefined);

      const result = await rateLimiter.checkGlobalLimit();

      expect(result.allowed).toBe(true);
      expect(result.remaining).toBe(999); // 1000 max - 1 used
    });

    it('should enforce global limit of 1000/day', async () => {
      const rateLimiter = new RateLimiter(mockEnv, mockLogger);

      const existingData = {
        count: 1000,
        resetAt: Date.now() + 86400000, // 24 hours
      };

      // When 'json' type is specified, KV returns parsed object, not string
      (mockKV.get as any).mockResolvedValue(existingData);

      const result = await rateLimiter.checkGlobalLimit();

      expect(result.allowed).toBe(false);
    });

    it('should use consistent key for global limit', async () => {
      const rateLimiter = new RateLimiter(mockEnv, mockLogger);

      (mockKV.get as any).mockResolvedValue(null);
      (mockKV.put as any).mockResolvedValue(undefined);

      await rateLimiter.checkGlobalLimit();

      const callArgs = (mockKV.get as any).mock.calls[0];
      expect(callArgs[0]).toBe('ratelimit:global');
    });
  });

  describe('resetLimit', () => {
    it('should delete rate limit data', async () => {
      const rateLimiter = new RateLimiter(mockEnv, mockLogger);

      (mockKV.delete as any).mockResolvedValue(undefined);

      await rateLimiter.resetLimit('sender:user@example.com');

      expect(mockKV.delete).toHaveBeenCalledWith('ratelimit:sender:user@example.com');
      expect(mockLogger.info).toHaveBeenCalledWith('Rate limit reset', expect.any(Object));
    });

    it('should handle missing KV gracefully', async () => {
      const envWithoutKV = { ...mockEnv, EMAIL_SMS_KV: undefined } as Env;
      const rateLimiter = new RateLimiter(envWithoutKV, mockLogger);

      await rateLimiter.resetLimit('sender:user@example.com');

      // Should not throw
      expect(true).toBe(true);
    });
  });

  describe('getLimitStatus', () => {
    it('should return current limit status', async () => {
      const rateLimiter = new RateLimiter(mockEnv, mockLogger);

      const existingData = {
        count: 5,
        resetAt: Date.now() + 3600000,
      };

      // When 'json' type is specified, KV returns parsed object, not string
      (mockKV.get as any).mockResolvedValue(existingData);

      const result = await rateLimiter.getLimitStatus('sender:user@example.com');

      expect(result).toBeDefined();
      expect(result?.allowed).toBe(true);
      expect(result?.remaining).toBe(5); // 10 max - 5 used
    });

    it('should return null when no data exists', async () => {
      const rateLimiter = new RateLimiter(mockEnv, mockLogger);

      (mockKV.get as any).mockResolvedValue(null);

      const result = await rateLimiter.getLimitStatus('sender:user@example.com');

      expect(result).toBeNull();
    });

    it('should return null when KV not configured', async () => {
      const envWithoutKV = { ...mockEnv, EMAIL_SMS_KV: undefined } as Env;
      const rateLimiter = new RateLimiter(envWithoutKV, mockLogger);

      const result = await rateLimiter.getLimitStatus('sender:user@example.com');

      expect(result).toBeNull();
    });

    it('should show not allowed when limit exceeded', async () => {
      const rateLimiter = new RateLimiter(mockEnv, mockLogger);

      const existingData = {
        count: 15,
        resetAt: Date.now() + 3600000,
      };

      // When 'json' type is specified, KV returns parsed object, not string
      (mockKV.get as any).mockResolvedValue(existingData);

      const result = await rateLimiter.getLimitStatus('sender:user@example.com');

      expect(result?.allowed).toBe(false);
      expect(result?.remaining).toBe(0);
    });
  });

  describe('createRateLimiter', () => {
    it('should create rate limiter instance', () => {
      const instance = createRateLimiter(mockEnv, mockLogger);
      expect(instance).toBeInstanceOf(RateLimiter);
    });
  });

  describe('TTL Handling', () => {
    it('should set correct TTL when creating limit', async () => {
      const rateLimiter = new RateLimiter(mockEnv, mockLogger);

      (mockKV.get as any).mockResolvedValue(null);
      (mockKV.put as any).mockResolvedValue(undefined);

      await rateLimiter.checkSenderLimit('user@example.com');

      const putCall = (mockKV.put as any).mock.calls[0];
      expect(putCall[2]).toHaveProperty('expirationTtl');
      expect(putCall[2].expirationTtl).toBeGreaterThan(0);
    });

    it('should preserve TTL when updating counter', async () => {
      const rateLimiter = new RateLimiter(mockEnv, mockLogger);

      const resetAt = Date.now() + 3600000;
      const existingData = {
        count: 1,
        resetAt,
      };

      // When 'json' type is specified, KV returns parsed object, not string
      (mockKV.get as any).mockResolvedValue(existingData);
      (mockKV.put as any).mockResolvedValue(undefined);

      await rateLimiter.checkSenderLimit('user@example.com');

      const putCall = (mockKV.put as any).mock.calls[0];
      const storedData = JSON.parse(putCall[1]);
      expect(storedData.resetAt).toBe(resetAt);
    });
  });

  describe('Concurrent Requests', () => {
    it('should handle multiple concurrent requests', async () => {
      const rateLimiter = new RateLimiter(mockEnv, mockLogger);

      (mockKV.get as any).mockResolvedValue(null);
      (mockKV.put as any).mockResolvedValue(undefined);

      const promises = Array(5).fill(null).map(() =>
        rateLimiter.checkSenderLimit('user@example.com')
      );

      const results = await Promise.all(promises);

      expect(results.every(r => r.allowed)).toBe(true);
      expect(mockKV.put).toHaveBeenCalled();
    });

    it('should handle race conditions gracefully', async () => {
      const rateLimiter = new RateLimiter(mockEnv, mockLogger);

      let callCount = 0;
      (mockKV.get as any).mockImplementation(async () => {
        callCount++;
        if (callCount === 1) {
          return null;
        }
        // When 'json' type is specified, KV returns parsed object, not string
        return { count: 1, resetAt: Date.now() + 3600000 };
      });
      (mockKV.put as any).mockResolvedValue(undefined);

      const [result1, result2] = await Promise.all([
        rateLimiter.checkSenderLimit('user@example.com'),
        rateLimiter.checkSenderLimit('user@example.com'),
      ]);

      expect(result1.allowed).toBe(true);
      expect(result2.allowed).toBe(true);
    });
  });

  describe('Edge Cases', () => {
    it('should handle very large reset times', async () => {
      const rateLimiter = new RateLimiter(mockEnv, mockLogger);

      const existingData = {
        count: 1,
        resetAt: Date.now() + 86400000 * 365, // 1 year
      };

      // When 'json' type is specified, KV returns parsed object, not string
      (mockKV.get as any).mockResolvedValue(existingData);
      (mockKV.put as any).mockResolvedValue(undefined);

      const result = await rateLimiter.checkSenderLimit('user@example.com');

      expect(result.allowed).toBe(true);
    });

    it('should handle corrupted KV data', async () => {
      const rateLimiter = new RateLimiter(mockEnv, mockLogger);

      // Simulate KV error by making get() throw
      (mockKV.get as any).mockRejectedValue(new Error('KV parse error'));

      const result = await rateLimiter.checkSenderLimit('user@example.com');

      expect(result.allowed).toBe(true); // Allow on error
      expect(mockLogger.error).toHaveBeenCalled();
    });

    it('should handle exact limit boundary', async () => {
      const rateLimiter = new RateLimiter(mockEnv, mockLogger);

      const existingData = {
        count: 9,
        resetAt: Date.now() + 3600000,
      };

      // When 'json' type is specified, KV returns parsed object, not string
      (mockKV.get as any).mockResolvedValue(existingData);
      (mockKV.put as any).mockResolvedValue(undefined);

      const result = await rateLimiter.checkSenderLimit('user@example.com');

      expect(result.allowed).toBe(true);
      expect(result.remaining).toBe(0); // Last allowed request
    });

    it('should handle special characters in keys', async () => {
      const rateLimiter = new RateLimiter(mockEnv, mockLogger);

      (mockKV.get as any).mockResolvedValue(null);
      (mockKV.put as any).mockResolvedValue(undefined);

      await rateLimiter.checkSenderLimit('user+tag@example.com');

      expect(mockKV.get).toHaveBeenCalled();
      expect(mockKV.put).toHaveBeenCalled();
    });
  });
});
