/**
 * Mock Services for Testing
 * Provides mock implementations of external services (Twilio, Cloudflare Workflows)
 */

import { vi } from 'vitest';
import type { Call } from 'twilio/lib/rest/api/v2010/account/call';

/**
 * Mock Twilio Client
 * Simulates Twilio SDK behavior for testing
 */
export class MockTwilioClient {
  private mockCalls: Map<string, any> = new Map();
  private shouldFail: boolean = false;
  private failureReason: string = '';

  constructor(accountSid: string, authToken: string) {
    // Validate credentials format
    if (!accountSid.startsWith('AC') || accountSid.length !== 34) {
      throw new Error('Invalid Account SID');
    }
    if (authToken.length !== 32) {
      throw new Error('Invalid Auth Token');
    }
  }

  /**
   * Configure mock to simulate failures
   */
  setFailureMode(shouldFail: boolean, reason: string = 'API Error') {
    this.shouldFail = shouldFail;
    this.failureReason = reason;
  }

  /**
   * Mock calls resource
   */
  calls = {
    create: vi.fn(async (params: { to: string; from: string; twiml: string }) => {
      if (this.shouldFail) {
        throw new Error(this.failureReason);
      }

      // Validate phone numbers
      if (!this.isValidPhone(params.to)) {
        throw new Error(`The 'To' number ${params.to} is not a valid phone number.`);
      }
      if (!this.isValidPhone(params.from)) {
        throw new Error(`The 'From' number ${params.from} is not a valid phone number.`);
      }

      // Generate call SID
      const callSid = `CA${this.generateRandomString(32)}`;

      const call = {
        sid: callSid,
        status: 'queued',
        to: params.to,
        from: params.from,
        dateCreated: new Date(),
        price: null,
        priceUnit: 'USD',
        direction: 'outbound-api',
      };

      this.mockCalls.set(callSid, call);
      return call;
    }),

    get: vi.fn(async (callSid: string) => {
      const call = this.mockCalls.get(callSid);
      if (!call) {
        throw new Error(`Call ${callSid} not found`);
      }
      return call;
    }),

    list: vi.fn(async () => {
      return Array.from(this.mockCalls.values());
    }),
  };

  /**
   * Validate E.164 phone number format
   */
  private isValidPhone(phone: string): boolean {
    const e164Regex = /^\+[1-9]\d{1,14}$/;
    return e164Regex.test(phone);
  }

  /**
   * Generate random hex string
   */
  private generateRandomString(length: number): string {
    const chars = '0123456789abcdef';
    let result = '';
    for (let i = 0; i < length; i++) {
      result += chars[Math.floor(Math.random() * chars.length)];
    }
    return result;
  }

  /**
   * Get all mock calls for testing
   */
  getMockCalls(): any[] {
    return Array.from(this.mockCalls.values());
  }

  /**
   * Clear all mock data
   */
  clear(): void {
    this.mockCalls.clear();
    this.shouldFail = false;
    this.failureReason = '';
  }
}

/**
 * Mock Cloudflare Workflow Binding
 * Simulates Cloudflare Workflows for testing
 */
export class MockWorkflowBinding {
  private workflows: Map<string, any> = new Map();
  private shouldFail: boolean = false;

  /**
   * Create a new workflow instance
   */
  create = vi.fn(async (options: { params: any; id?: string }) => {
    if (this.shouldFail) {
      throw new Error('Failed to create workflow');
    }

    const workflowId = options.id || `workflow-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

    const workflow = {
      id: workflowId,
      params: options.params,
      status: 'running',
      createdAt: new Date(),
    };

    this.workflows.set(workflowId, workflow);
    return { id: workflowId };
  });

  /**
   * Get workflow by ID
   */
  get = vi.fn(async (workflowId: string) => {
    const workflow = this.workflows.get(workflowId);
    if (!workflow) {
      throw new Error(`Workflow ${workflowId} not found`);
    }
    return workflow;
  });

  /**
   * List all workflows
   */
  list = vi.fn(async () => {
    return Array.from(this.workflows.values());
  });

  /**
   * Configure mock to simulate failures
   */
  setFailureMode(shouldFail: boolean): void {
    this.shouldFail = shouldFail;
  }

  /**
   * Clear all workflows
   */
  clear(): void {
    this.workflows.clear();
    this.shouldFail = false;
  }

  /**
   * Get all workflows for testing
   */
  getWorkflows(): any[] {
    return Array.from(this.workflows.values());
  }
}

/**
 * Create mock environment for Worker testing
 */
export function createMockEnv(overrides: Partial<Env> = {}): Env {
  const mockWorkflow = new MockWorkflowBinding();

  return {
    TWILIO_ACCOUNT_SID: 'AC1234567890abcdef1234567890abcdef',
    TWILIO_AUTH_TOKEN: '1234567890abcdef1234567890abcdef',
    TWILIO_PHONE_NUMBER: '+15559999999',
    NEVER_GONNA: mockWorkflow,
    ...overrides,
  } as Env;
}

/**
 * Mock Twilio webhook signature validator
 * Used for security testing
 */
export class MockTwilioSignatureValidator {
  private authToken: string;

  constructor(authToken: string) {
    this.authToken = authToken;
  }

  /**
   * Validate Twilio request signature
   * Returns true if signature is valid
   */
  validate(url: string, params: Record<string, string>, signature: string): boolean {
    // Simplified mock - in real implementation, use crypto.createHmac
    const expectedSignature = this.generateSignature(url, params);
    return signature === expectedSignature;
  }

  /**
   * Generate signature for testing
   */
  generateSignature(url: string, params: Record<string, string>): string {
    // Simplified mock signature
    const sortedParams = Object.keys(params).sort().reduce((acc, key) => {
      acc[key] = params[key];
      return acc;
    }, {} as Record<string, string>);

    const data = url + JSON.stringify(sortedParams) + this.authToken;

    // Mock base64 signature (not cryptographically secure)
    return Buffer.from(data).toString('base64').substring(0, 44);
  }
}

/**
 * Helper to create mock Twilio webhook payload
 */
export function createMockWebhookPayload(overrides: Record<string, string> = {}): Record<string, string> {
  return {
    From: '+15551234567',
    To: '+15559876543',
    Body: 'Test message',
    MessageSid: `SM${Math.random().toString(36).substr(2, 32)}`,
    AccountSid: 'AC1234567890abcdef1234567890abcdef',
    NumMedia: '0',
    FromCity: 'SAN FRANCISCO',
    FromState: 'CA',
    FromZip: '94102',
    FromCountry: 'US',
    ...overrides,
  };
}

/**
 * Helper to create mock Request objects
 */
export function createMockRequest(
  url: string,
  options: {
    method?: string;
    headers?: Record<string, string>;
    body?: string | FormData;
  } = {}
): Request {
  const { method = 'GET', headers = {}, body } = options;

  return new Request(url, {
    method,
    headers: new Headers(headers),
    body,
  });
}

/**
 * Performance testing helpers
 */
export class PerformanceTimer {
  private startTime: number = 0;
  private endTime: number = 0;

  start(): void {
    this.startTime = performance.now();
  }

  stop(): number {
    this.endTime = performance.now();
    return this.getDuration();
  }

  getDuration(): number {
    return this.endTime - this.startTime;
  }

  async measure<T>(fn: () => Promise<T>): Promise<{ result: T; duration: number }> {
    this.start();
    const result = await fn();
    const duration = this.stop();
    return { result, duration };
  }
}

/**
 * Memory usage tracker for testing
 */
export class MemoryTracker {
  private initialMemory: number = 0;

  start(): void {
    if (typeof process !== 'undefined' && process.memoryUsage) {
      this.initialMemory = process.memoryUsage().heapUsed;
    }
  }

  getMemoryIncrease(): number {
    if (typeof process !== 'undefined' && process.memoryUsage) {
      const currentMemory = process.memoryUsage().heapUsed;
      return currentMemory - this.initialMemory;
    }
    return 0;
  }

  getMemoryIncreaseInMB(): number {
    return this.getMemoryIncrease() / (1024 * 1024);
  }
}

/**
 * Rate limiter mock for testing
 */
export class MockRateLimiter {
  private requests: Map<string, number[]> = new Map();
  private limit: number;
  private windowMs: number;

  constructor(limit: number = 10, windowMs: number = 60000) {
    this.limit = limit;
    this.windowMs = windowMs;
  }

  /**
   * Check if request should be allowed
   */
  isAllowed(key: string): boolean {
    const now = Date.now();
    const requests = this.requests.get(key) || [];

    // Remove old requests outside the window
    const recentRequests = requests.filter(time => now - time < this.windowMs);

    if (recentRequests.length >= this.limit) {
      return false;
    }

    recentRequests.push(now);
    this.requests.set(key, recentRequests);
    return true;
  }

  /**
   * Clear all rate limit data
   */
  clear(): void {
    this.requests.clear();
  }
}
