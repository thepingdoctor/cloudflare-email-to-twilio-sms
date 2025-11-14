/**
 * Performance Tests
 * Tests performance benchmarks and load handling
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { processEmailContent } from '../../src/utils/content-processor';
import { extractPhoneNumber, normalizePhoneNumber } from '../../src/utils/phone-parser';
import { PerformanceTimer, MemoryTracker } from '../fixtures/mock-services';
import type { ParsedEmail } from '../../src/types';

describe('Performance Tests', () => {
  const createEmail = (overrides: Partial<ParsedEmail> = {}): ParsedEmail => ({
    from: 'sender@example.com',
    to: 'recipient@example.com',
    subject: 'Test',
    text: 'Test message',
    headers: {},
    ...overrides,
  });

  describe('Content Processing Performance', () => {
    it('should process short email under 10ms', async () => {
      const email = createEmail({ text: 'Short message' });
      const timer = new PerformanceTimer();

      const { duration } = await timer.measure(async () => {
        processEmailContent(email);
      });

      expect(duration).toBeLessThan(10);
    });

    it('should process medium email (500 chars) under 20ms', async () => {
      const email = createEmail({ text: 'a'.repeat(500) });
      const timer = new PerformanceTimer();

      const { duration } = await timer.measure(async () => {
        processEmailContent(email);
      });

      expect(duration).toBeLessThan(20);
    });

    it('should process large email (5000 chars) under 100ms', async () => {
      const email = createEmail({ text: 'a'.repeat(5000) });
      const timer = new PerformanceTimer();

      const { duration } = await timer.measure(async () => {
        processEmailContent(email);
      });

      // Increased threshold to account for CI/CD environment variability
      expect(duration).toBeLessThan(100);
    });

    it('should handle HTML conversion efficiently', async () => {
      const html = '<p>'.repeat(100) + 'Content' + '</p>'.repeat(100);
      const email = createEmail({ text: '', html });
      const timer = new PerformanceTimer();

      const { duration } = await timer.measure(async () => {
        processEmailContent(email);
      });

      expect(duration).toBeLessThan(30);
    });
  });

  describe('Phone Number Extraction Performance', () => {
    it('should extract phone from email under 5ms', async () => {
      const email = createEmail({ to: '5551234567@example.com' });
      const timer = new PerformanceTimer();

      const { duration } = await timer.measure(async () => {
        extractPhoneNumber(email);
      });

      expect(duration).toBeLessThan(5);
    });

    it('should extract phone from subject under 5ms', async () => {
      const email = createEmail({ subject: 'To: 555-123-4567' });
      const timer = new PerformanceTimer();

      const { duration } = await timer.measure(async () => {
        extractPhoneNumber(email);
      });

      expect(duration).toBeLessThan(5);
    });

    it('should normalize 1000 phone numbers under 50ms', async () => {
      const timer = new PerformanceTimer();

      const { duration } = await timer.measure(async () => {
        for (let i = 0; i < 1000; i++) {
          normalizePhoneNumber('5551234567');
        }
      });

      expect(duration).toBeLessThan(50);
    });
  });

  describe('Memory Usage', () => {
    it('should process emails with minimal memory growth', () => {
      const tracker = new MemoryTracker();
      tracker.start();

      for (let i = 0; i < 100; i++) {
        const email = createEmail({ text: 'a'.repeat(1000) });
        processEmailContent(email);
      }

      const memoryIncrease = tracker.getMemoryIncreaseInMB();

      // Should use less than 50MB for 100 emails
      expect(memoryIncrease).toBeLessThan(50);
    });

    it('should not leak memory on repeated processing', () => {
      const tracker = new MemoryTracker();
      const email = createEmail({ text: 'a'.repeat(10000) });

      // Warmup
      for (let i = 0; i < 10; i++) {
        processEmailContent(email);
      }

      tracker.start();

      // Process many times
      for (let i = 0; i < 1000; i++) {
        processEmailContent(email);
      }

      const memoryIncrease = tracker.getMemoryIncreaseInMB();

      // Memory should not grow linearly with iterations
      expect(memoryIncrease).toBeLessThan(100);
    });
  });

  describe('Batch Processing', () => {
    it('should process 100 emails under 500ms', async () => {
      const emails = Array(100).fill(null).map((_, i) =>
        createEmail({ text: `Message ${i}` })
      );

      const timer = new PerformanceTimer();

      const { duration } = await timer.measure(async () => {
        emails.forEach(email => processEmailContent(email));
      });

      expect(duration).toBeLessThan(500);
    });

    it('should extract 100 phone numbers under 100ms', async () => {
      const emails = Array(100).fill(null).map((_, i) =>
        createEmail({ to: `555${i.toString().padStart(7, '0')}@example.com` })
      );

      const timer = new PerformanceTimer();

      const { duration } = await timer.measure(async () => {
        emails.forEach(email => extractPhoneNumber(email));
      });

      expect(duration).toBeLessThan(100);
    });
  });

  describe('Concurrent Processing', () => {
    it('should handle parallel processing efficiently', async () => {
      const emails = Array(20).fill(null).map((_, i) =>
        createEmail({ text: `Message ${i}` })
      );

      const timer = new PerformanceTimer();

      const { duration } = await timer.measure(async () => {
        await Promise.all(emails.map(async email => {
          return processEmailContent(email);
        }));
      });

      // Parallel should be faster than sequential
      expect(duration).toBeLessThan(200);
    });
  });

  describe('Edge Case Performance', () => {
    it('should handle very long single line efficiently', async () => {
      const email = createEmail({ text: 'a'.repeat(10000) });
      const timer = new PerformanceTimer();

      const { duration } = await timer.measure(async () => {
        processEmailContent(email);
      });

      expect(duration).toBeLessThan(100);
    });

    it('should handle many line breaks efficiently', async () => {
      const email = createEmail({ text: 'line\n'.repeat(1000) });
      const timer = new PerformanceTimer();

      const { duration } = await timer.measure(async () => {
        processEmailContent(email);
      });

      expect(duration).toBeLessThan(100);
    });

    it('should handle Unicode characters efficiently', async () => {
      const email = createEmail({ text: '😀'.repeat(500) });
      const timer = new PerformanceTimer();

      const { duration } = await timer.measure(async () => {
        processEmailContent(email);
      });

      expect(duration).toBeLessThan(50);
    });

    it('should handle complex HTML efficiently', async () => {
      const html = `
        <html><body>
          ${'<div><p>Content</p></div>'.repeat(100)}
        </body></html>
      `;
      const email = createEmail({ text: '', html });
      const timer = new PerformanceTimer();

      const { duration } = await timer.measure(async () => {
        processEmailContent(email);
      });

      expect(duration).toBeLessThan(100);
    });
  });

  describe('Regex Performance', () => {
    it('should handle phone regex without catastrophic backtracking', async () => {
      const email = createEmail({
        text: '5' + '5'.repeat(100) + ' not a phone',
      });

      const timer = new PerformanceTimer();

      const { duration } = await timer.measure(async () => {
        try {
          extractPhoneNumber(email);
        } catch (e) {
          // Expected to fail, we're just testing performance
        }
      });

      // Should fail fast, not hang
      expect(duration).toBeLessThan(50);
    });

    it('should handle email regex efficiently', async () => {
      const text = '@'.repeat(100) + 'example.com';

      const timer = new PerformanceTimer();

      timer.start();
      for (let i = 0; i < 100; i++) {
        // Test email extraction performance
        text.match(/[^\s@]+@[^\s@]+\.[^\s@]+/);
      }
      const duration = timer.stop();

      expect(duration).toBeLessThan(10);
    });
  });

  describe('Throughput Benchmarks', () => {
    it('should achieve >100 emails/second processing rate', async () => {
      const testDuration = 1000; // 1 second
      const email = createEmail({ text: 'Standard test message' });

      let count = 0;
      const startTime = Date.now();

      while (Date.now() - startTime < testDuration) {
        processEmailContent(email);
        count++;
      }

      const actualDuration = Date.now() - startTime;
      const throughput = (count / actualDuration) * 1000; // per second

      expect(throughput).toBeGreaterThan(100);
    });

    it('should achieve >500 phone extractions/second', async () => {
      const testDuration = 1000;
      const email = createEmail({ to: '5551234567@example.com' });

      let count = 0;
      const startTime = Date.now();

      while (Date.now() - startTime < testDuration) {
        extractPhoneNumber(email);
        count++;
      }

      const actualDuration = Date.now() - startTime;
      const throughput = (count / actualDuration) * 1000;

      expect(throughput).toBeGreaterThan(500);
    });
  });

  describe('Cold Start Performance', () => {
    it('should have minimal first-call overhead', async () => {
      const email = createEmail({ text: 'First call' });
      const timer = new PerformanceTimer();

      // First call (cold start)
      const { duration: firstCall } = await timer.measure(async () => {
        processEmailContent(email);
      });

      // Second call (warm)
      const { duration: secondCall } = await timer.measure(async () => {
        processEmailContent(email);
      });

      // Cold start should not be significantly slower
      // Using max() to avoid division by zero and more realistic threshold
      expect(firstCall).toBeLessThan(Math.max(secondCall * 5, 20));
    });
  });

  describe('Resource Cleanup', () => {
    it('should cleanup resources after processing', () => {
      const initialMemory = process.memoryUsage().heapUsed;

      for (let i = 0; i < 100; i++) {
        const email = createEmail({ text: 'a'.repeat(1000) });
        processEmailContent(email);
      }

      // Force garbage collection if available
      if (global.gc) {
        global.gc();
      }

      const finalMemory = process.memoryUsage().heapUsed;
      const memoryGrowth = (finalMemory - initialMemory) / (1024 * 1024);

      // Should not accumulate significant memory
      expect(memoryGrowth).toBeLessThan(10);
    });
  });

  describe('Worst Case Scenarios', () => {
    it('should handle pathological email under 200ms', async () => {
      // Worst case: long text, many signatures, HTML, headers
      const email = createEmail({
        text: 'Content\n\n' + '--\nSignature\n'.repeat(10) + 'a'.repeat(5000),
        html: '<div>' + '<p>Nested</p>'.repeat(100) + '</div>',
        subject: 'To: 555-123-4567 ' + 'Long subject '.repeat(20),
        headers: {
          'x-custom-1': 'value1',
          'x-custom-2': 'value2',
          'x-custom-3': 'value3',
        },
      });

      const timer = new PerformanceTimer();

      const { duration } = await timer.measure(async () => {
        processEmailContent(email);
        extractPhoneNumber(email);
      });

      expect(duration).toBeLessThan(200);
    });
  });
});
