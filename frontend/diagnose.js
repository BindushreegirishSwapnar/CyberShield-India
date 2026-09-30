import { chromium } from '@playwright/test';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  const networkLogs = [];
  const consoleLogs = [];

  page.on('console', msg => {
    consoleLogs.push({ type: msg.type(), text: msg.text() });
  });

  page.on('response', async res => {
    const url = res.url();
    if (url.includes('/api/')) {
      let body = '';
      try {
        body = await res.text();
      } catch (e) {
        body = `[Error reading body: ${e.message}]`;
      }
      networkLogs.push({
        url,
        status: res.status(),
        statusText: res.statusText(),
        body: body.length > 500 ? body.slice(0, 500) + '... (truncated)' : body
      });
    }
  });

  page.on('requestfailed', req => {
    if (req.url().includes('/api/')) {
      networkLogs.push({
        url: req.url(),
        status: 'FAILED',
        error: req.failure()?.errorText
      });
    }
  });

  console.log('Navigating to http://localhost:3000...');
  await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });

  // Switch to Officer Console
  const officerBtn = await page.$('button:has-text("Cyber Cell Officer")');
  if (officerBtn) {
    await officerBtn.click();
    await page.waitForTimeout(1000);
  }

  // Find BI Studio tab
  const biTabBtn = await page.$('button:has-text("BI Studio")');
  if (biTabBtn) {
    console.log('Clicking BI Studio tab...');
    await biTabBtn.click();
    await page.waitForTimeout(3000);
  }

  // Find Link Analysis tab
  const linkTabBtn = await page.$('button:has-text("Link Analysis Graph")');
  if (linkTabBtn) {
    console.log('Clicking Link Analysis Graph tab...');
    await linkTabBtn.click();
    await page.waitForTimeout(3000);
  }

  console.log('\n--- NETWORK API CALLS ---');
  console.log(JSON.stringify(networkLogs, null, 2));

  console.log('\n--- CONSOLE LOGS ---');
  console.log(JSON.stringify(consoleLogs.filter(c => c.type === 'error' || c.type === 'warning'), null, 2));

  await browser.close();
})();
