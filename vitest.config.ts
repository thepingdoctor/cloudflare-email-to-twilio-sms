/**
 * Vitest Configuration
 * Test runner configuration for Email2SMS Worker
 */

import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    // Test environment
    environment: 'node',

    // Global test setup
    globals: true,

    // Coverage configuration
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      exclude: [
        'node_modules/',
        'dist/',
        'tests/',
        '**/*.spec.ts',
        '**/*.test.ts',
        '**/fixtures/',
        '**/helpers/',
        'vitest.config.ts',
      ],
      thresholds: {
        lines: 90,
        functions: 90,
        branches: 85,
        statements: 90,
      },
    },

    // Test includes/excludes
    include: ['tests/**/*.spec.ts', 'tests/**/*.test.ts'],
    exclude: ['node_modules', 'dist'],

    // Test timeout
    testTimeout: 10000,
    hookTimeout: 10000,

    // Reporters
    reporters: ['verbose'],

    // Parallel execution
    threads: true,
    maxConcurrency: 5,

    // Mock configuration
    mockReset: true,
    clearMocks: true,
    restoreMocks: true,

    // Performance options
    isolate: true,

    // Setup files
    setupFiles: [],

    // Benchmark
    benchmark: {
      include: ['tests/**/*.bench.ts'],
    },
  },

  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@tests': path.resolve(__dirname, './tests'),
    },
  },
});
