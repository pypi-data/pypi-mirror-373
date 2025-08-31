/**
 * Configuration for Playwright using default from @jupyterlab/galata
 */
const baseConfig = require('@jupyterlab/galata/lib/playwright-config');

module.exports = {
  ...baseConfig,
  // Add 1 retry for each test
  retries: 1,
  use: {
    ...baseConfig.use,
    headless: true,
    viewport: { width: 1920, height: 1080 }
  },
  video: {
    size: { width: 1920, height: 1080 }
  },
  // Add multiple reporters for better CI integration
  reporter: [
    ['html'], // Keep the existing HTML reporter
    ['json', { outputFile: 'test-results.json' }], // Add JSON reporter for easier parsing
    ['list'] // Add list reporter for console output
  ],
  webServer: {
    command: 'jlpm start',
    url: 'http://localhost:8888/lab',
    timeout: 120 * 1000,
    reuseExistingServer: !process.env.CI
  }
};
