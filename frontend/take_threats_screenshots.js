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

  // Click on "Emerging Threat Detector" in Desktop sidebar
  const threatBtn = await page.locator('button:has-text("Emerging Threat")').first();
  if (await threatBtn.count() > 0) {
    console.log('Opening Emerging Threat Detector tab...');
    await threatBtn.click();
    await page.waitForTimeout(2000);

    // Screenshot 1: Drift telemetry and zero-day clusters
    const threatPath = path.join(screenshotDir, 'module5_threats_clusters_desktop.png');
    await page.screenshot({ path: threatPath });
    console.log(`Saved: ${threatPath}`);

    // Click "Approve as New Category"
    const approveBtn = await page.locator('button:has-text("Approve as New Category")').first();
    if (await approveBtn.count() > 0) {
      console.log('Approving emerging cluster...');
      await approveBtn.click();
      await page.waitForTimeout(1500);
    }

    // Click "Trigger Model Retraining"
    const retrainBtn = await page.locator('button:has-text("Trigger Model Retraining")').first();
    if (await retrainBtn.count() > 0) {
      console.log('Triggering incremental retraining...');
      await retrainBtn.click();
      await page.waitForTimeout(2000);

      // Screenshot 2: Post-retraining state with restored accuracy banner
      const retrainPath = path.join(screenshotDir, 'module5_threats_retrained_desktop.png');
      await page.screenshot({ path: retrainPath });
      console.log(`Saved: ${retrainPath}`);
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

  // In mobile view, trigger threats tab via evaluate
  await mobilePage.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const t = btns.find(b => b.textContent.includes('Emerging Threat'));
    if (t) t.click();
  });
  await mobilePage.waitForTimeout(2000);

  const mobileThreatPath = path.join(screenshotDir, 'module5_threats_mobile.png');
  await mobilePage.screenshot({ path: mobileThreatPath });
  console.log(`Saved: ${mobileThreatPath}`);

  await browser.close();
  console.log('Finished capturing Emerging Threat Detector screenshots.');
})();
