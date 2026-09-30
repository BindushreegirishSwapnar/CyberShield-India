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

  // Click on "Scan Suspicious SMS / Link" (Tab 2) in Citizen Portal
  const scanTab = await page.locator('button:has-text("Scan Suspicious")').first();
  if (await scanTab.count() > 0) {
    console.log('Opening Safe-Scan tab...');
    await scanTab.click();
    await page.waitForTimeout(1500);

    // Click "Typosquat URL" quick demo button
    const phishBtn = await page.locator('button:has-text("Typosquat URL")').first();
    if (await phishBtn.count() > 0) {
      console.log('Clicking Typosquat URL demo...');
      await phishBtn.click();
      await page.waitForTimeout(2000);

      // Screenshot 1: Safe-Scan Lookalike URL Analysis
      const urlScanPath = path.join(screenshotDir, 'module3_safescan_lookalike_url_desktop.png');
      await page.screenshot({ path: urlScanPath });
      console.log(`Saved: ${urlScanPath}`);
    }

    // Click "Deceptive QR" quick demo button
    const qrBtn = await page.locator('button:has-text("Deceptive QR")').first();
    if (await qrBtn.count() > 0) {
      console.log('Clicking Deceptive QR demo...');
      await qrBtn.click();
      await page.waitForTimeout(2000);

      // Screenshot 2: Safe-Scan UPI QR Inspector
      const qrScanPath = path.join(screenshotDir, 'module3_safescan_upi_qr_desktop.png');
      await page.screenshot({ path: qrScanPath });
      console.log(`Saved: ${qrScanPath}`);
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

  // Click visible scan button
  const mobileScan = await mobilePage.evaluate(() => {
    const buttons = Array.from(document.querySelectorAll('button'));
    const scanBtn = buttons.find(b => b.offsetParent !== null && b.textContent.includes('Scan Suspicious'));
    if (scanBtn) {
      scanBtn.click();
      return true;
    }
    return false;
  });

  if (mobileScan) {
    await mobilePage.waitForTimeout(1500);
    // Click Deceptive QR demo on mobile
    await mobilePage.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      const qr = buttons.find(b => b.offsetParent !== null && b.textContent.includes('Deceptive QR'));
      if (qr) qr.click();
    });
    await mobilePage.waitForTimeout(2000);

    const mobileScanPath = path.join(screenshotDir, 'module3_safescan_mobile.png');
    await mobilePage.screenshot({ path: mobileScanPath });
    console.log(`Saved: ${mobileScanPath}`);
  }

  await browser.close();
  console.log('Finished capturing Safe-Scan screenshots.');
})();
