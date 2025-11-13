/**
 * TypeScript Type Definitions for Email2SMS Worker
 */

/**
 * Environment bindings available to the worker
 */
export interface Env {
  // Twilio credentials (secrets)
  TWILIO_ACCOUNT_SID: string;
  TWILIO_AUTH_TOKEN: string;
  TWILIO_PHONE_NUMBER: string;

  // Optional: KV namespace for rate limiting
  EMAIL_SMS_KV?: KVNamespace;

  // Optional: Analytics binding
  EMAIL_SMS_ANALYTICS?: AnalyticsEngineDataset;

  // Optional: Allowed senders (comma-separated)
  ALLOWED_SENDERS?: string;

  // Optional: Default recipient country code
  DEFAULT_COUNTRY_CODE?: string;
}

/**
 * Cloudflare Email Message interface
 */
export interface ForwardableEmailMessage {
  from: string;
  to: string;
  headers: Headers;
  raw: ReadableStream;
  rawSize: number;
  setReject(reason: string): void;
  forward(rcptTo: string, headers?: Headers): Promise<void>;
}

/**
 * Parsed email structure
 */
export interface ParsedEmail {
  from: string;
  to: string;
  subject: string;
  text: string;
  html?: string;
  headers: Record<string, string>;
  attachments?: Array<{
    filename: string;
    mimeType: string;
    size: number;
  }>;
}

/**
 * Phone extraction result
 */
export interface PhoneExtractionResult {
  phoneNumber: string;
  source: 'email_to' | 'email_from' | 'subject' | 'header' | 'body';
  confidence: 'high' | 'medium' | 'low';
}

/**
 * SMS message structure
 */
export interface SMSMessage {
  to: string;
  from: string;
  body: string;
  metadata?: {
    emailFrom: string;
    emailSubject: string;
    timestamp: string;
  };
}

/**
 * Twilio API response
 */
export interface TwilioMessageResponse {
  sid: string;
  status: string;
  account_sid: string;
  from: string;
  to: string;
  body: string;
  date_created: string;
  price?: string;
  uri: string;
  error_code?: number;
  error_message?: string;
}

/**
 * Rate limit check result
 */
export interface RateLimitResult {
  allowed: boolean;
  remaining: number;
  resetAt: number;
  reason?: string;
}

/**
 * Log entry structure
 */
export interface LogEntry {
  timestamp: string;
  emailFrom: string;
  emailTo: string;
  smsTo: string;
  smsFrom: string;
  messageLength: number;
  status: 'success' | 'failed' | 'rejected';
  error?: string;
  twilioSid?: string;
  processingTimeMs?: number;
}

/**
 * Worker configuration
 */
export interface WorkerConfig {
  maxSMSLength: number;
  enableRateLimiting: boolean;
  enableLogging: boolean;
  enableAnalytics: boolean;
  rateLimitPerHour: number;
  allowedSenders: string[];
  defaultCountryCode: string;
}
