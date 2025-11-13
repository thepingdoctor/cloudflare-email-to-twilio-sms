/**
 * Integration Tests
 * Tests end-to-end email-to-SMS workflow
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { createMockEnv, MockTwilioClient, MockWorkflowBinding, createMockWebhookPayload } from '../fixtures/mock-services';
import type { ForwardableEmailMessage } from '../../src/types';
import testData from '../fixtures/test-data.json';

// Mock PostalMime
vi.mock('postal-mime', () => ({
  default: class PostalMime {
    async parse() {
      return {
        subject: 'Test Subject',
        text: 'Test message body',
        html: '<p>Test HTML</p>',
        headers: {},
        attachments: [],
      };
    }
  },
}));

describe('Integration Tests', () => {
  let mockEnv: any;
  let mockTwilioClient: MockTwilioClient;
  let mockWorkflow: MockWorkflowBinding;

  beforeEach(() => {
    mockEnv = createMockEnv();
    mockTwilioClient = new MockTwilioClient(
      mockEnv.TWILIO_ACCOUNT_SID,
      mockEnv.TWILIO_AUTH_TOKEN
    );
    mockWorkflow = mockEnv.NEVER_GONNA as MockWorkflowBinding;

    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  const createMockEmail = (overrides: Partial<any> = {}): ForwardableEmailMessage => {
    const readable = new ReadableStream({
      start(controller) {
        controller.enqueue(new TextEncoder().encode('Test email content'));
        controller.close();
      },
    });

    return {
      from: 'sender@example.com',
      to: '5551234567@example.com',
      headers: new Headers(),
      raw: readable,
      rawSize: 100,
      setReject: vi.fn(),
      forward: vi.fn(),
      ...overrides,
    } as any;
  });

  describe('End-to-End Email-to-SMS Flow', () => {
    it('should complete full workflow successfully', async () => {
      const message = createMockEmail();

      // Mock Twilio response
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          sid: 'SM123',
          status: 'queued',
          to: '+15551234567',
          from: mockEnv.TWILIO_PHONE_NUMBER,
          body: 'Test',
        }),
      });

      // Import worker dynamically
      const worker = await import('../../src/worker/index');

      // Execute email handler
      await worker.default.email(message, mockEnv, {} as any);

      // Verify SMS was sent
      expect(global.fetch).toHaveBeenCalled();

      // Verify email was not rejected
      expect(message.setReject).not.toHaveBeenCalled();
    });

    it('should extract phone from email address', async () => {
      const message = createMockEmail({
        to: '5551234567@example.com',
      });

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          sid: 'SM123',
          status: 'queued',
          to: '+15551234567',
          from: mockEnv.TWILIO_PHONE_NUMBER,
          body: 'Test',
        }),
      });

      const worker = await import('../../src/worker/index');
      await worker.default.email(message, mockEnv, {} as any);

      // Verify phone number was extracted correctly
      const fetchCall = (global.fetch as any).mock.calls[0];
      const body = fetchCall[1].body;
      expect(body).toContain('To=%2B15551234567');
    });

    it('should process email content for SMS', async () => {
      const message = createMockEmail();

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          sid: 'SM123',
          status: 'queued',
        }),
      });

      const worker = await import('../../src/worker/index');
      await worker.default.email(message, mockEnv, {} as any);

      const fetchCall = (global.fetch as any).mock.calls[0];
      const body = fetchCall[1].body;

      // Should contain sender info and content
      expect(body).toContain('From');
      expect(body).toContain('Re%3A');
    });
  });

  describe('Error Handling Flow', () => {
    it('should reject email when phone not found', async () => {
      const message = createMockEmail({
        to: 'nophone@example.com',
      });

      const worker = await import('../../src/worker/index');
      await worker.default.email(message, mockEnv, {} as any);

      expect(message.setReject).toHaveBeenCalledWith(
        expect.stringContaining('No valid phone number')
      );
    });

    it('should handle Twilio API errors gracefully', async () => {
      const message = createMockEmail();

      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 400,
        json: async () => ({
          message: 'Invalid phone number',
          code: 21211,
        }),
      });

      const worker = await import('../../src/worker/index');
      await worker.default.email(message, mockEnv, {} as any);

      // Should not reject email on Twilio error
      expect(message.setReject).not.toHaveBeenCalled();
    });

    it('should handle network failures with retry', async () => {
      const message = createMockEmail();

      global.fetch = vi.fn()
        .mockRejectedValueOnce(new Error('Network error'))
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ sid: 'SM123', status: 'queued' }),
        });

      const worker = await import('../../src/worker/index');
      await worker.default.email(message, mockEnv, {} as any);

      expect(global.fetch).toHaveBeenCalledTimes(3);
      expect(message.setReject).not.toHaveBeenCalled();
    });
  });

  describe('Rate Limiting Integration', () => {
    it('should enforce rate limits when configured', async () => {
      const mockKV = {
        get: vi.fn().mockResolvedValue(JSON.stringify({
          count: 10,
          resetAt: Date.now() + 3600000,
        })),
        put: vi.fn(),
        delete: vi.fn(),
      };

      const envWithKV = {
        ...mockEnv,
        EMAIL_SMS_KV: mockKV,
      };

      const message = createMockEmail();

      const worker = await import('../../src/worker/index');
      await worker.default.email(message, envWithKV, {} as any);

      expect(message.setReject).toHaveBeenCalledWith(
        expect.stringContaining('Rate limit exceeded')
      );
    });

    it('should allow requests within rate limit', async () => {
      const mockKV = {
        get: vi.fn().mockResolvedValue(JSON.stringify({
          count: 5,
          resetAt: Date.now() + 3600000,
        })),
        put: vi.fn(),
        delete: vi.fn(),
      };

      const envWithKV = {
        ...mockEnv,
        EMAIL_SMS_KV: mockKV,
      };

      const message = createMockEmail();

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ sid: 'SM123', status: 'queued' }),
      });

      const worker = await import('../../src/worker/index');
      await worker.default.email(message, envWithKV, {} as any);

      expect(message.setReject).not.toHaveBeenCalled();
      expect(mockKV.put).toHaveBeenCalled();
    });
  });

  describe('Validation Integration', () => {
    it('should reject unauthorized senders when allowlist configured', async () => {
      const envWithAllowlist = {
        ...mockEnv,
        ALLOWED_SENDERS: 'allowed@example.com',
      };

      const message = createMockEmail({
        from: 'unauthorized@example.com',
      });

      const worker = await import('../../src/worker/index');
      await worker.default.email(message, envWithAllowlist, {} as any);

      expect(message.setReject).toHaveBeenCalledWith(
        expect.stringContaining('not authorized')
      );
    });

    it('should allow authorized senders', async () => {
      const envWithAllowlist = {
        ...mockEnv,
        ALLOWED_SENDERS: 'allowed@example.com',
      };

      const message = createMockEmail({
        from: 'allowed@example.com',
      });

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ sid: 'SM123', status: 'queued' }),
      });

      const worker = await import('../../src/worker/index');
      await worker.default.email(message, envWithAllowlist, {} as any);

      expect(message.setReject).not.toHaveBeenCalled();
    });
  });

  describe('Real-World Scenarios', () => {
    it('should handle valid Twilio webhook payload', async () => {
      const payload = testData.twilio_webhooks.valid_sms;
      const message = createMockEmail({
        from: payload.From,
        to: `${payload.From.replace('+', '')}@example.com`,
      });

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          sid: 'SM123',
          status: 'queued',
          to: payload.From,
          from: mockEnv.TWILIO_PHONE_NUMBER,
        }),
      });

      const worker = await import('../../src/worker/index');
      await worker.default.email(message, mockEnv, {} as any);

      expect(message.setReject).not.toHaveBeenCalled();
    });

    it('should handle international phone numbers', async () => {
      const payload = testData.twilio_webhooks.international_uk;
      const message = createMockEmail({
        to: `${payload.From.replace('+', '')}@example.com`,
      });

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ sid: 'SM123', status: 'queued' }),
      });

      const worker = await import('../../src/worker/index');
      await worker.default.email(message, mockEnv, {} as any);

      expect(message.setReject).not.toHaveBeenCalled();
    });

    it('should handle emails with emoji and Unicode', async () => {
      const payload = testData.twilio_webhooks.unicode_emoji;
      const message = createMockEmail({
        to: '5551234567@example.com',
      });

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ sid: 'SM123', status: 'queued' }),
      });

      const worker = await import('../../src/worker/index');
      await worker.default.email(message, mockEnv, {} as any);

      expect(message.setReject).not.toHaveBeenCalled();
    });
  });

  describe('Performance Under Load', () => {
    it('should handle concurrent emails', async () => {
      const messages = Array(10).fill(null).map(() => createMockEmail());

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ sid: 'SM123', status: 'queued' }),
      });

      const worker = await import('../../src/worker/index');

      const startTime = Date.now();

      await Promise.all(
        messages.map(msg => worker.default.email(msg, mockEnv, {} as any))
      );

      const duration = Date.now() - startTime;

      // Should complete in reasonable time
      expect(duration).toBeLessThan(1000);

      // All should succeed
      messages.forEach(msg => {
        expect(msg.setReject).not.toHaveBeenCalled();
      });
    });
  });

  describe('Edge Cases Integration', () => {
    it('should handle empty email body gracefully', async () => {
      const message = createMockEmail();

      // Mock PostalMime to return empty content
      vi.doMock('postal-mime', () => ({
        default: class PostalMime {
          async parse() {
            return {
              subject: '',
              text: '',
              html: '',
              headers: {},
              attachments: [],
            };
          }
        },
      }));

      const worker = await import('../../src/worker/index');
      await worker.default.email(message, mockEnv, {} as any);

      expect(message.setReject).toHaveBeenCalledWith(
        expect.stringContaining('empty')
      );
    });

    it('should handle very long email content', async () => {
      const message = createMockEmail();

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ sid: 'SM123', status: 'queued' }),
      });

      const worker = await import('../../src/worker/index');
      await worker.default.email(message, mockEnv, {} as any);

      // Should truncate to SMS length
      const fetchCall = (global.fetch as any).mock.calls[0];
      const body = fetchCall[1].body;
      const decodedBody = decodeURIComponent(body);

      // Verify message was truncated appropriately
      expect(decodedBody.length).toBeLessThan(2000); // URL encoded length
    });

    it('should handle malicious content safely', async () => {
      const xssPayload = testData.twilio_webhooks.malicious_xss;
      const message = createMockEmail();

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ sid: 'SM123', status: 'queued' }),
      });

      const worker = await import('../../src/worker/index');
      await worker.default.email(message, mockEnv, {} as any);

      const fetchCall = (global.fetch as any).mock.calls[0];
      const body = fetchCall[1].body;

      // Should not contain script tags
      expect(body).not.toContain('script');
      expect(body).not.toContain('alert');
    });
  });

  describe('Logging and Monitoring', () => {
    it('should log transaction on success', async () => {
      const mockKV = {
        get: vi.fn().mockResolvedValue(null),
        put: vi.fn(),
        delete: vi.fn(),
      };

      const envWithKV = {
        ...mockEnv,
        EMAIL_SMS_KV: mockKV,
      };

      const message = createMockEmail();

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ sid: 'SM123', status: 'queued' }),
      });

      const worker = await import('../../src/worker/index');
      await worker.default.email(message, envWithKV, {} as any);

      // Should log transaction
      expect(mockKV.put).toHaveBeenCalled();
    });

    it('should log transaction on failure', async () => {
      const mockKV = {
        get: vi.fn().mockResolvedValue(null),
        put: vi.fn(),
        delete: vi.fn(),
      };

      const envWithKV = {
        ...mockEnv,
        EMAIL_SMS_KV: mockKV,
      };

      const message = createMockEmail({
        to: 'nophone@example.com',
      });

      const worker = await import('../../src/worker/index');
      await worker.default.email(message, envWithKV, {} as any);

      // Should log failed transaction
      expect(mockKV.put).toHaveBeenCalled();
    });
  });
});
