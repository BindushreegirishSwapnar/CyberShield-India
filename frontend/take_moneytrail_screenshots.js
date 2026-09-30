import { chromium } from '@playwright/test';
import fs from 'fs';
import path from 'path';

(async () => {
  const screenshotDir = path.resolve('public', 'screenshots');
  if (!fs.existsSync(screenshotDir)) {
    fs.mkdirSync(screenshotDir, { recursive: true });
  }

  const browser = await chromium.launch({ headless: true });

  // 1. Desktop Context
  const desktopCtx = await browser.newContext({
    viewport: { width: 1440, height: 1100 }
  });
  const page = await desktopCtx.newPage();

  console.log('Navigating to http://localhost:3000 (Desktop)...');
  await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);

  // Click on "Money Trail (Rapid Freeze)" in Desktop sidebar
  const moneyTrailBtn = await page.locator('button:has-text("Money Trail")').first();
  if (await moneyTrailBtn.count() > 0) {
    console.log('Opening Money Trail tab...');
    await moneyTrailBtn.click();
    await page.waitForTimeout(2000);

    // Screenshot 1: Multi-Hop Money Trail & FPS Leaderboard
    const trailPath = path.join(screenshotDir, 'module4_moneytrail_flow_desktop.png');
    await page.screenshot({ path: trailPath });
    console.log(`Saved: ${trailPath}`);

    // Click "Issue Sec 94 BNSS Order" button
    const freezeOrderBtn = await page.locator('button:has-text("Issue Sec 94 BNSS Order")').first();
    if (await freezeOrderBtn.count() > 0) {
      console.log('Opening Section 94 BNSS Notice Modal...');
      await freezeOrderBtn.click();
      await page.waitForTimeout(1500);

      // Screenshot 2: Statutory Section 94 BNSS Notice Modal
      const noticePath = path.join(screenshotDir, 'module4_sec94_bnss_notice_modal.png');
      await page.screenshot({ path: noticePath });
      console.log(`Saved: ${noticePath}`);
    }
  }

  // 2. Mobile Context (iPhone 14)
  const mobileCtx = await browser.newContext({
    viewport: { width: 390, height: 844 },
    isMobile: true,
    hasTouch: true
  });
  const mobilePage = await mobileCtx.newPage();

  console.log('Navigating to http://localhost:3000 (Mobile)...');
  await mobilePage.goto('http://localhost:3000', { waitUntil: 'load' });
  await mobilePage.waitForTimeout(2000);

  // In mobile view, trigger Money Trail via evaluate
  await mobilePage.evaluate(() => {
    // Find all sidebar buttons or switch activeTab
    const btns = Array.from(document.querySelectorAll('button'));
    const mt = btns.find(b => b.textContent.includes('Money Trail'));
    if (mt) mt.click();
  });
  await mobilePage.waitForTimeout(2000);

  const mobileTrailPath = path.join(screenshotDir, 'module4_moneytrail_mobile.png');
  await mobilePage.screenshot({ path: mobileTrailPath });
  console.log(`Saved: ${mobileTrailPath}`);

  await browser.close();
  console.log('Finished capturing Money Trail screenshots.');
})();
