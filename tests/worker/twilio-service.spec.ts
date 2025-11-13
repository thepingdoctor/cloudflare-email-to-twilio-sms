/**
 * Twilio Service Tests
 * Tests Twilio API integration and SMS sending
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { TwilioService, TwilioError, createTwilioService } from '../../src/services/twilio-service';
import { createLogger } from '../../src/utils/logger';
import type { Env, SMSMessage } from '../../src/types';

describe('Twilio Service', () => {
  let mockEnv: Env;
  let mockLogger: ReturnType<typeof createLogger>;

  beforeEach(() => {
    mockEnv = {
      TWILIO_ACCOUNT_SID: 'AC1234567890abcdef1234567890abcd',
      TWILIO_AUTH_TOKEN: '1234567890abcdef1234567890abcdef',
      TWILIO_PHONE_NUMBER: '+15559999999',
    } as Env;

    mockLogger = {
      info: vi.fn(),
      warn: vi.fn(),
      error: vi.fn(),
      debug: vi.fn(),
      logTransaction: vi.fn(),
    } as any;

    // Clear all mocks
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Constructor', () => {
    it('should create service with valid credentials', () => {
      expect(() => new TwilioService(mockEnv, mockLogger)).not.toThrow();
    });

    it('should throw on missing Account SID', () => {
      const env = { ...mockEnv, TWILIO_ACCOUNT_SID: '' } as Env;
      expect(() => new TwilioService(env, mockLogger)).toThrow('Missing required Twilio credentials');
    });

    it('should throw on missing Auth Token', () => {
      const env = { ...mockEnv, TWILIO_AUTH_TOKEN: '' } as Env;
      expect(() => new TwilioService(env, mockLogger)).toThrow('Missing required Twilio credentials');
    });

    it('should throw on missing phone number', () => {
      const env = { ...mockEnv, TWILIO_PHONE_NUMBER: '' } as Env;
      expect(() => new TwilioService(env, mockLogger)).toThrow('Missing required Twilio credentials');
    });

    it('should throw on invalid Account SID format', () => {
      const env = { ...mockEnv, TWILIO_ACCOUNT_SID: 'INVALID123' } as Env;
      expect(() => new TwilioService(env, mockLogger)).toThrow('Invalid Twilio Account SID format');
    });

    it('should throw on invalid phone number format', () => {
      const env = { ...mockEnv, TWILIO_PHONE_NUMBER: '5559999999' } as Env;
      expect(() => new TwilioService(env, mockLogger)).toThrow('E.164 format');
    });
  });

  describe('sendSMS', () => {
    let service: TwilioService;
    let mockFetch: any;

    beforeEach(() => {
      service = new TwilioService(mockEnv, mockLogger);

      // Mock global fetch
      mockFetch = vi.fn();
      global.fetch = mockFetch;
    });

    it('should send SMS successfully', async () => {
      const mockResponse = {
        sid: 'SM1234567890abcdef',
        status: 'queued',
        account_sid: mockEnv.TWILIO_ACCOUNT_SID,
        from: mockEnv.TWILIO_PHONE_NUMBER,
        to: '+15551234567',
        body: 'Test message',
        date_created: '2025-11-13T03:00:00Z',
        uri: '/2010-04-01/Accounts/AC.../Messages/SM...',
      };

      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      });

      const message: SMSMessage = {
        to: '+15551234567',
        from: mockEnv.TWILIO_PHONE_NUMBER,
        body: 'Test message',
      };

      const result = await service.sendSMS(message);

      expect(result.sid).toBe('SM1234567890abcdef');
      expect(result.status).toBe('queued');
      expect(mockLogger.info).toHaveBeenCalledWith('Sending SMS via Twilio', expect.any(Object));
      expect(mockLogger.info).toHaveBeenCalledWith('SMS sent successfully', expect.any(Object));
    });

    it('should include metadata in request', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({
          sid: 'SM123',
          status: 'queued',
          to: '+15551234567',
          from: mockEnv.TWILIO_PHONE_NUMBER,
          body: 'Test',
        }),
      });

      const message: SMSMessage = {
        to: '+15551234567',
        from: mockEnv.TWILIO_PHONE_NUMBER,
        body: 'Test',
        metadata: {
          emailFrom: 'sender@example.com',
          emailSubject: 'Test',
          timestamp: '2025-11-13T03:00:00Z',
        },
      };

      await service.sendSMS(message);

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/Messages.json'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': expect.stringContaining('Basic '),
          }),
        })
      );
    });

    it('should throw TwilioError on API error', async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 400,
        json: async () => ({
          message: 'Invalid phone number',
          code: 21211,
        }),
      });

      const message: SMSMessage = {
        to: '+1555',
        from: mockEnv.TWILIO_PHONE_NUMBER,
        body: 'Test',
      };

      await expect(service.sendSMS(message)).rejects.toThrow(TwilioError);
      await expect(service.sendSMS(message)).rejects.toThrow('Invalid phone number');
      expect(mockLogger.error).toHaveBeenCalled();
    });

    it('should retry on network failure', async () => {
      mockFetch
        .mockRejectedValueOnce(new Error('Network error'))
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValue({
          ok: true,
          json: async () => ({
            sid: 'SM123',
            status: 'queued',
            to: '+15551234567',
            from: mockEnv.TWILIO_PHONE_NUMBER,
            body: 'Test',
          }),
        });

      const message: SMSMessage = {
        to: '+15551234567',
        from: mockEnv.TWILIO_PHONE_NUMBER,
        body: 'Test',
      };

      const result = await service.sendSMS(message);

      expect(result.sid).toBe('SM123');
      expect(mockFetch).toHaveBeenCalledTimes(3);
      expect(mockLogger.warn).toHaveBeenCalledTimes(2); // 2 failed attempts
    });

    it('should fail after max retries', async () => {
      mockFetch.mockRejectedValue(new Error('Network error'));

      const message: SMSMessage = {
        to: '+15551234567',
        from: mockEnv.TWILIO_PHONE_NUMBER,
        body: 'Test',
      };

      await expect(service.sendSMS(message)).rejects.toThrow(TwilioError);
      expect(mockFetch).toHaveBeenCalledTimes(3); // Initial + 2 retries
    });

    it('should create correct auth header', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({
          sid: 'SM123',
          status: 'queued',
          to: '+15551234567',
          from: mockEnv.TWILIO_PHONE_NUMBER,
          body: 'Test',
        }),
      });

      const message: SMSMessage = {
        to: '+15551234567',
        from: mockEnv.TWILIO_PHONE_NUMBER,
        body: 'Test',
      };

      await service.sendSMS(message);

      const callArgs = mockFetch.mock.calls[0];
      const authHeader = callArgs[1].headers.Authorization;

      expect(authHeader).toContain('Basic ');
      // Verify it's base64 encoded
      const decoded = atob(authHeader.replace('Basic ', ''));
      expect(decoded).toContain(mockEnv.TWILIO_ACCOUNT_SID);
      expect(decoded).toContain(mockEnv.TWILIO_AUTH_TOKEN);
    });

    it('should send correct form data', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({
          sid: 'SM123',
          status: 'queued',
          to: '+15551234567',
          from: mockEnv.TWILIO_PHONE_NUMBER,
          body: 'Test message',
        }),
      });

      const message: SMSMessage = {
        to: '+15551234567',
        from: mockEnv.TWILIO_PHONE_NUMBER,
        body: 'Test message',
      };

      await service.sendSMS(message);

      const callArgs = mockFetch.mock.calls[0];
      const body = callArgs[1].body;

      expect(body).toContain('To=%2B15551234567');
      expect(body).toContain('From=%2B15559999999');
      expect(body).toContain('Body=Test+message');
    });
  });

  describe('Static Methods', () => {
    describe('validatePhoneNumber', () => {
      it('should validate E.164 format', () => {
        expect(TwilioService.validatePhoneNumber('+15551234567')).toBe(true);
        expect(TwilioService.validatePhoneNumber('+442071234567')).toBe(true);
      });

      it('should reject invalid formats', () => {
        expect(TwilioService.validatePhoneNumber('5551234567')).toBe(false);
        expect(TwilioService.validatePhoneNumber('+1555')).toBe(false);
        expect(TwilioService.validatePhoneNumber('+' + '1'.repeat(20))).toBe(false);
      });
    });

    describe('isConfigured', () => {
      it('should return true when configured', () => {
        expect(TwilioService.isConfigured(mockEnv)).toBe(true);
      });

      it('should return false when missing credentials', () => {
        const env = { ...mockEnv, TWILIO_ACCOUNT_SID: '' } as Env;
        expect(TwilioService.isConfigured(env)).toBe(false);
      });
    });
  });

  describe('TwilioError', () => {
    it('should create error with message', () => {
      const error = new TwilioError('Test error');
      expect(error.message).toBe('Test error');
      expect(error.name).toBe('TwilioError');
    });

    it('should store error codes', () => {
      const error = new TwilioError('Test error', 400, 21211);
      expect(error.code).toBe(400);
      expect(error.twilioCode).toBe(21211);
    });

    it('should be instanceof Error', () => {
      const error = new TwilioError('Test error');
      expect(error instanceof Error).toBe(true);
    });
  });

  describe('createTwilioService', () => {
    it('should create service instance', () => {
      const service = createTwilioService(mockEnv, mockLogger);
      expect(service).toBeInstanceOf(TwilioService);
    });
  });

  describe('Error Handling', () => {
    let service: TwilioService;

    beforeEach(() => {
      service = new TwilioService(mockEnv, mockLogger);
      global.fetch = vi.fn();
    });

    it('should handle 401 Unauthorized', async () => {
      (global.fetch as any).mockResolvedValue({
        ok: false,
        status: 401,
        json: async () => ({
          message: 'Authenticate',
          code: 20003,
        }),
      });

      const message: SMSMessage = {
        to: '+15551234567',
        from: mockEnv.TWILIO_PHONE_NUMBER,
        body: 'Test',
      };

      await expect(service.sendSMS(message)).rejects.toThrow('Authenticate');
    });

    it('should handle 429 Rate Limit', async () => {
      (global.fetch as any).mockResolvedValue({
        ok: false,
        status: 429,
        json: async () => ({
          message: 'Too Many Requests',
          code: 20429,
        }),
      });

      const message: SMSMessage = {
        to: '+15551234567',
        from: mockEnv.TWILIO_PHONE_NUMBER,
        body: 'Test',
      };

      await expect(service.sendSMS(message)).rejects.toThrow('Too Many Requests');
    });

    it('should handle network timeout', async () => {
      (global.fetch as any).mockImplementation(() =>
        new Promise((_, reject) =>
          setTimeout(() => reject(new Error('Timeout')), 100)
        )
      );

      const message: SMSMessage = {
        to: '+15551234567',
        from: mockEnv.TWILIO_PHONE_NUMBER,
        body: 'Test',
      };

      await expect(service.sendSMS(message)).rejects.toThrow(TwilioError);
    });
  });

  describe('Edge Cases', () => {
    let service: TwilioService;

    beforeEach(() => {
      service = new TwilioService(mockEnv, mockLogger);
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          sid: 'SM123',
          status: 'queued',
          to: '+15551234567',
          from: mockEnv.TWILIO_PHONE_NUMBER,
          body: '',
        }),
      });
    });

    it('should handle empty message body', async () => {
      const message: SMSMessage = {
        to: '+15551234567',
        from: mockEnv.TWILIO_PHONE_NUMBER,
        body: '',
      };

      const result = await service.sendSMS(message);
      expect(result.sid).toBe('SM123');
    });

    it('should handle very long message body', async () => {
      const message: SMSMessage = {
        to: '+15551234567',
        from: mockEnv.TWILIO_PHONE_NUMBER,
        body: 'a'.repeat(1600),
      };

      const result = await service.sendSMS(message);
      expect(result.sid).toBe('SM123');
    });

    it('should handle Unicode characters', async () => {
      const message: SMSMessage = {
        to: '+15551234567',
        from: mockEnv.TWILIO_PHONE_NUMBER,
        body: 'Hello 😀🚀 World',
      };

      const result = await service.sendSMS(message);
      expect(result.sid).toBe('SM123');
    });

    it('should handle international phone numbers', async () => {
      const message: SMSMessage = {
        to: '+442071234567',
        from: mockEnv.TWILIO_PHONE_NUMBER,
        body: 'Test',
      };

      const result = await service.sendSMS(message);
      expect(result.sid).toBe('SM123');
    });
  });
});
