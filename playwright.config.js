// @ts-check
const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests', // Playwright buscará dentro de tu carpeta 'tests'
  fullyParallel: true,
  reporter: 'html',
  use: {
    /* La URL exacta que se ve en tus capturas de error */
    baseURL: 'http://localhost:8080/SystemaVentas/', 
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});