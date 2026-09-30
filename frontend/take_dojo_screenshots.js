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

  // Switch to Scam Dojo tab
  const dojoBtn = await page.$('button:has-text("Scam Dojo")');
  if (dojoBtn) {
    console.log('Opening Scam Dojo...');
    await dojoBtn.click();
    await page.waitForTimeout(2000);

    // Screenshot 1: Initial Dojo State
    const dojoInitPath = path.join(screenshotDir, 'module2_dojo_initial_desktop.png');
    await page.screenshot({ path: dojoInitPath });
    console.log(`Saved: ${dojoInitPath}`);

    // Click first Defense Pill
    const defensePill = await page.$('button:has-text("DEFENSE PILLS") + button, button:has-text("💬")');
    if (defensePill) {
      console.log('Clicking defense pill counter-attack...');
      await defensePill.click();
      await page.waitForTimeout(2500); // wait for scammer escalation response

      // Screenshot 2: Active combat with scammer escalation and red flag coach update
      const dojoActivePath = path.join(screenshotDir, 'module2_dojo_active_combat_desktop.png');
      await page.screenshot({ path: dojoActivePath });
      console.log(`Saved: ${dojoActivePath}`);
    }

    // Toggle Elder Mode
    const elderBtn = await page.$('button:has-text("Elder Mode")');
    if (elderBtn) {
      console.log('Enabling Elder Mode...');
      await elderBtn.click();
      await page.waitForTimeout(1000);
      const dojoElderPath = path.join(screenshotDir, 'module2_dojo_elder_mode_desktop.png');
      await page.screenshot({ path: dojoElderPath });
      console.log(`Saved: ${dojoElderPath}`);
    }

    // Click "Complete Training & Get Certificate"
    const certBtn = await page.$('button:has-text("Complete Training")');
    if (certBtn) {
      console.log('Generating Immunity Certificate...');
      await certBtn.click();
      await page.waitForTimeout(1500);
      const certPath = path.join(screenshotDir, 'module2_dojo_immunity_certificate.png');
      await page.screenshot({ path: certPath });
      console.log(`Saved: ${certPath}`);
    }
  } else {
    console.error('Scam Dojo button not found!');
  }

  // 2. Mobile Context (iPhone 14)
  const mobileCtx = await browser.newContext({
    viewport: { width: 390, height: 844 },
    isMobile: true,
    hasTouch: true
  });
  const mobilePage = await mobileCtx.newPage();

  console.log('Navigating to http://localhost:3000 (Mobile)...');
  await mobilePage.goto('http://localhost:3000', { waitUntil: 'networkidle' });
  await mobilePage.waitForTimeout(2000);

  // Find Dojo button in mobile Citizen Portal
  const mobileDojo = await mobilePage.$('button:has-text("Scam Dojo")');
  if (mobileDojo) {
    await mobileDojo.click();
    await mobilePage.waitForTimeout(2000);
    const dojoMobilePath = path.join(screenshotDir, 'module2_dojo_mobile.png');
    await mobilePage.screenshot({ path: dojoMobilePath });
    console.log(`Saved: ${dojoMobilePath}`);
  }

  await browser.close();
  console.log('Finished capturing Scam Dojo screenshots.');
})();
