/**
 * Structured Logger
 * Provides logging and analytics for email-to-SMS operations
 */

import type { Env, LogEntry } from '../types';

/**
 * Log levels
 */
export enum LogLevel {
  DEBUG = 'debug',
  INFO = 'info',
  WARN = 'warn',
  ERROR = 'error',
}

/**
 * Logger class
 */
export class Logger {
  constructor(
    private env: Env,
    private requestId: string = crypto.randomUUID()
  ) {}

  /**
   * Log debug message
   */
  debug(message: string, data?: Record<string, unknown>): void {
    this.log(LogLevel.DEBUG, message, data);
  }

  /**
   * Log info message
   */
  info(message: string, data?: Record<string, unknown>): void {
    this.log(LogLevel.INFO, message, data);
  }

  /**
   * Log warning
   */
  warn(message: string, data?: Record<string, unknown>): void {
    this.log(LogLevel.WARN, message, data);
  }

  /**
   * Log error
   */
  error(message: string, error?: Error | unknown, data?: Record<string, unknown>): void {
    const errorData = error instanceof Error
      ? {
          name: error.name,
          message: error.message,
          stack: error.stack,
        }
      : { error };

    this.log(LogLevel.ERROR, message, { ...data, ...errorData });
  }

  /**
   * Core log function
   */
  private log(level: LogLevel, message: string, data?: Record<string, unknown>): void {
    const logEntry = {
      timestamp: new Date().toISOString(),
      level,
      requestId: this.requestId,
      message,
      ...data,
    };

    // Console output (always)
    console[level === LogLevel.ERROR ? 'error' : 'log'](JSON.stringify(logEntry));

    // Send to Analytics Engine if available
    if (this.env.EMAIL_SMS_ANALYTICS && level !== LogLevel.DEBUG) {
      try {
        this.env.EMAIL_SMS_ANALYTICS.writeDataPoint({
          blobs: [message, level],
          doubles: [Date.now()],
          indexes: [this.requestId],
        });
      } catch (err) {
        console.error('Failed to write analytics:', err);
      }
    }
  }

  /**
   * Log email-to-SMS transaction
   */
  async logTransaction(entry: LogEntry): Promise<void> {
    this.info('Email-to-SMS transaction', entry);

    // Store in KV if available (for audit trail)
    if (this.env.EMAIL_SMS_KV) {
      try {
        const key = `log:${entry.timestamp}:${this.requestId}`;
        await this.env.EMAIL_SMS_KV.put(key, JSON.stringify(entry), {
          expirationTtl: 60 * 60 * 24 * 30, // 30 days
        });
      } catch (err) {
        this.error('Failed to store log in KV', err);
      }
    }
  }

  /**
   * Create a child logger with additional context
   */
  child(context: Record<string, unknown>): Logger {
    const child = new Logger(this.env, this.requestId);
    // Store context for all child logs
    return child;
  }
}

/**
 * Create logger instance
 */
export function createLogger(env: Env, requestId?: string): Logger {
  return new Logger(env, requestId);
}
