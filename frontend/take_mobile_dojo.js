import { chromium } from '@playwright/test';
import fs from 'fs';
import path from 'path';

(async () => {
  const screenshotDir = path.resolve('public', 'screenshots');
  const browser = await chromium.launch({ headless: true });

  const mobileCtx = await browser.newContext({
    viewport: { width: 390, height: 844 },
    isMobile: true,
    hasTouch: true
  });
  const page = await mobileCtx.newPage();

  console.log('Navigating to http://localhost:3000 (Mobile)...');
  await page.goto('http://localhost:3000', { waitUntil: 'load' });
  await page.waitForTimeout(2000);

  // In CitizenPortal, find the VISIBLE Scam Dojo button and click it
  const clicked = await page.evaluate(() => {
    const buttons = Array.from(document.querySelectorAll('button'));
    const visibleDojo = buttons.find(b => b.offsetParent !== null && b.textContent.includes('Scam Dojo'));
    if (visibleDojo) {
      visibleDojo.click();
      return true;
    }
    return false;
  });

  console.log('Clicked visible Scam Dojo button:', clicked);
  await page.waitForTimeout(2500);

  const mobileDojoPath = path.join(screenshotDir, 'module2_dojo_mobile.png');
  await page.screenshot({ path: mobileDojoPath });
  console.log(`Saved: ${mobileDojoPath}`);

  await browser.close();
})();
