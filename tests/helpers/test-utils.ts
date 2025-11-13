/**
 * Test Utilities and Helpers
 * Common utilities for testing the Email2SMS Worker
 */

import type { ParsedEmail, Env, ForwardableEmailMessage } from '../../src/types';

/**
 * Create a mock ParsedEmail object for testing
 */
export function createMockEmail(overrides: Partial<ParsedEmail> = {}): ParsedEmail {
  return {
    from: 'sender@example.com',
    to: 'recipient@example.com',
    subject: 'Test Subject',
    text: 'Test message body',
    html: undefined,
    headers: {},
    attachments: [],
    ...overrides,
  };
}

/**
 * Create a mock Env object for testing
 */
export function createMockEnv(overrides: Partial<Env> = {}): Env {
  return {
    TWILIO_ACCOUNT_SID: 'AC1234567890abcdef1234567890abcd',
    TWILIO_AUTH_TOKEN: '1234567890abcdef1234567890abcdef',
    TWILIO_PHONE_NUMBER: '+15559999999',
    ALLOWED_SENDERS: '',
    DEFAULT_COUNTRY_CODE: '1',
    ...overrides,
  } as Env;
}

/**
 * Create a mock ForwardableEmailMessage for integration tests
 */
export function createMockEmailMessage(overrides: Partial<any> = {}): ForwardableEmailMessage {
  const readable = new ReadableStream({
    start(controller) {
      controller.enqueue(new TextEncoder().encode('Mock email content'));
      controller.close();
    },
  });

  return {
    from: 'sender@example.com',
    to: 'recipient@example.com',
    headers: new Headers(),
    raw: readable,
    rawSize: 100,
    setReject: vi.fn(),
    forward: vi.fn(),
    ...overrides,
  } as any;
}

/**
 * Create a mock KV namespace for testing
 */
export function createMockKV(): KVNamespace {
  const storage = new Map<string, string>();

  return {
    get: vi.fn(async (key: string, type?: string) => {
      const value = storage.get(key);
      if (!value) return null;
      if (type === 'json') return JSON.parse(value);
      return value;
    }),
    put: vi.fn(async (key: string, value: string) => {
      storage.set(key, value);
    }),
    delete: vi.fn(async (key: string) => {
      storage.delete(key);
    }),
    list: vi.fn(async () => ({
      keys: Array.from(storage.keys()).map(name => ({ name })),
      list_complete: true,
      cursor: '',
    })),
    getWithMetadata: vi.fn(async (key: string) => ({
      value: storage.get(key) || null,
      metadata: null,
    })),
  } as any;
}

/**
 * Create a mock Twilio API response
 */
export function createMockTwilioResponse(overrides: any = {}) {
  return {
    sid: 'SM1234567890abcdef',
    status: 'queued',
    account_sid: 'AC1234567890abcdef',
    from: '+15559999999',
    to: '+15551234567',
    body: 'Test message',
    date_created: '2025-11-13T03:00:00Z',
    uri: '/2010-04-01/Accounts/AC.../Messages/SM...',
    ...overrides,
  };
}

/**
 * Wait for a specified duration
 */
export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Assert that a function throws a specific error
 */
export async function assertThrows<T extends Error>(
  fn: () => any | Promise<any>,
  errorType?: new (...args: any[]) => T,
  errorMessage?: string | RegExp
): Promise<void> {
  try {
    await fn();
    throw new Error('Expected function to throw, but it did not');
  } catch (error) {
    if (errorType && !(error instanceof errorType)) {
      throw new Error(`Expected error of type ${errorType.name}, got ${error.constructor.name}`);
    }
    if (errorMessage) {
      const message = error instanceof Error ? error.message : String(error);
      if (typeof errorMessage === 'string') {
        if (!message.includes(errorMessage)) {
          throw new Error(`Expected error message to include "${errorMessage}", got "${message}"`);
        }
      } else if (!errorMessage.test(message)) {
        throw new Error(`Expected error message to match ${errorMessage}, got "${message}"`);
      }
    }
  }
}

/**
 * Mock fetch globally for testing
 */
export function mockFetch(response: any): void {
  global.fetch = vi.fn().mockResolvedValue({
    ok: true,
    status: 200,
    json: async () => response,
    text: async () => JSON.stringify(response),
  });
}

/**
 * Mock fetch with error
 */
export function mockFetchError(error: Error): void {
  global.fetch = vi.fn().mockRejectedValue(error);
}

/**
 * Create a performance timer for benchmarking
 */
export class TestTimer {
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
 * Generate random test data
 */
export class TestDataGenerator {
  static randomString(length: number): string {
    const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
  }

  static randomEmail(): string {
    return `${this.randomString(10)}@example.com`;
  }

  static randomPhoneNumber(): string {
    const areaCode = Math.floor(Math.random() * 900) + 100;
    const exchange = Math.floor(Math.random() * 900) + 100;
    const number = Math.floor(Math.random() * 9000) + 1000;
    return `+1${areaCode}${exchange}${number}`;
  }

  static randomContent(minLength: number = 10, maxLength: number = 500): string {
    const length = Math.floor(Math.random() * (maxLength - minLength)) + minLength;
    return this.randomString(length);
  }
}

/**
 * Assert array contains elements matching a predicate
 */
export function assertArrayContains<T>(
  array: T[],
  predicate: (item: T) => boolean,
  message?: string
): void {
  const found = array.some(predicate);
  if (!found) {
    throw new Error(message || 'Array does not contain matching element');
  }
}

/**
 * Assert two objects are deeply equal
 */
export function assertDeepEqual(actual: any, expected: any, message?: string): void {
  const actualJson = JSON.stringify(actual, null, 2);
  const expectedJson = JSON.stringify(expected, null, 2);
  if (actualJson !== expectedJson) {
    throw new Error(
      message || `Objects are not equal:\nActual:\n${actualJson}\nExpected:\n${expectedJson}`
    );
  }
}

/**
 * Capture console output during test
 */
export class ConsoleCapture {
  private originalLog: any;
  private originalError: any;
  private originalWarn: any;
  public logs: string[] = [];
  public errors: string[] = [];
  public warns: string[] = [];

  start(): void {
    this.originalLog = console.log;
    this.originalError = console.error;
    this.originalWarn = console.warn;

    console.log = (...args: any[]) => {
      this.logs.push(args.join(' '));
    };

    console.error = (...args: any[]) => {
      this.errors.push(args.join(' '));
    };

    console.warn = (...args: any[]) => {
      this.warns.push(args.join(' '));
    };
  }

  stop(): void {
    console.log = this.originalLog;
    console.error = this.originalError;
    console.warn = this.originalWarn;
  }

  clear(): void {
    this.logs = [];
    this.errors = [];
    this.warns = [];
  }
}

/**
 * Retry a function until it succeeds or max attempts reached
 */
export async function retry<T>(
  fn: () => Promise<T>,
  maxAttempts: number = 3,
  delayMs: number = 100
): Promise<T> {
  let lastError: Error | null = null;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));
      if (attempt < maxAttempts) {
        await sleep(delayMs);
      }
    }
  }

  throw lastError || new Error('Retry failed');
}

/**
 * Create a spy function that tracks calls
 */
export class SpyFunction<T extends (...args: any[]) => any> {
  public calls: Array<{ args: Parameters<T>; result?: ReturnType<T>; error?: Error }> = [];
  private implementation?: T;

  constructor(implementation?: T) {
    this.implementation = implementation;
  }

  invoke(...args: Parameters<T>): ReturnType<T> {
    try {
      const result = this.implementation ? this.implementation(...args) : undefined;
      this.calls.push({ args, result });
      return result;
    } catch (error) {
      this.calls.push({ args, error: error instanceof Error ? error : new Error(String(error)) });
      throw error;
    }
  }

  getCallCount(): number {
    return this.calls.length;
  }

  getCallArgs(index: number): Parameters<T> {
    return this.calls[index]?.args;
  }

  wasCalledWith(...args: Parameters<T>): boolean {
    return this.calls.some(call =>
      JSON.stringify(call.args) === JSON.stringify(args)
    );
  }

  reset(): void {
    this.calls = [];
  }
}

/**
 * Type guard to check if value is defined
 */
export function isDefined<T>(value: T | null | undefined): value is T {
  return value !== null && value !== undefined;
}

/**
 * Format bytes to human-readable string
 */
export function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}

/**
 * Get memory usage information
 */
export function getMemoryUsage(): {
  heapUsed: string;
  heapTotal: string;
  external: string;
  rss: string;
} {
  if (typeof process === 'undefined' || !process.memoryUsage) {
    return {
      heapUsed: 'N/A',
      heapTotal: 'N/A',
      external: 'N/A',
      rss: 'N/A',
    };
  }

  const usage = process.memoryUsage();
  return {
    heapUsed: formatBytes(usage.heapUsed),
    heapTotal: formatBytes(usage.heapTotal),
    external: formatBytes(usage.external),
    rss: formatBytes(usage.rss),
  };
}
