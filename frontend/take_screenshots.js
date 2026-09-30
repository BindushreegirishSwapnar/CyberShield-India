import { chromium } from '@playwright/test';
import fs from 'fs';
import path from 'path';

(async () => {
  const screenshotDir = path.resolve('public', 'screenshots');
  if (!fs.existsSync(screenshotDir)) {
    fs.mkdirSync(screenshotDir, { recursive: true });
  }

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1050 }
  });
  const page = await context.newPage();

  console.log('Navigating to http://localhost:3000...');
  await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1500);

  // Switch to BI Studio
  const biNavBtn = await page.$('button:has-text("BI Studio")');
  if (biNavBtn) {
    console.log('Opening BI Studio...');
    await biNavBtn.click();
    await page.waitForTimeout(2000);

    // Scroll slightly so the charts are centered in the viewport
    await page.evaluate(() => window.scrollBy(0, 360));
    await page.waitForTimeout(1000);

    // Screenshot 1: Overview (States Bar + Monthly Trend)
    const overviewPath = path.join(screenshotDir, 'bi_overview_charts.png');
    await page.screenshot({ path: overviewPath, fullPage: false });
    console.log(`Saved: ${overviewPath}`);

    // Screenshot 2: Decomposition Tree
    const decompTab = await page.$('button:has-text("Decomposition Tree")');
    if (decompTab) {
      await decompTab.click();
      await page.waitForTimeout(1000);
      const decompPath = path.join(screenshotDir, 'bi_decomposition.png');
      await page.screenshot({ path: decompPath, fullPage: false });
      console.log(`Saved: ${decompPath}`);
    }

    // Screenshot 3: Waterfall
    const waterTab = await page.$('button:has-text("Waterfall")');
    if (waterTab) {
      await waterTab.click();
      await page.waitForTimeout(1000);
      const waterPath = path.join(screenshotDir, 'bi_waterfall.png');
      await page.screenshot({ path: waterPath, fullPage: false });
      console.log(`Saved: ${waterPath}`);
    }

    // Screenshot 4: Heatmap
    const heatTab = await page.$('button:has-text("Incident Time Heatmap")');
    if (heatTab) {
      await heatTab.click();
      await page.waitForTimeout(1000);
      const heatPath = path.join(screenshotDir, 'bi_heatmap.png');
      await page.screenshot({ path: heatPath, fullPage: false });
      console.log(`Saved: ${heatPath}`);
    }

    // Screenshot 5: Forecast
    const foreTab = await page.$('button:has-text("Predictive 2027 Projections")');
    if (foreTab) {
      await foreTab.click();
      await page.waitForTimeout(1000);
      const forePath = path.join(screenshotDir, 'bi_forecast.png');
      await page.screenshot({ path: forePath, fullPage: false });
      console.log(`Saved: ${forePath}`);
    }
  }

  console.log('All chart screenshots captured.');
  await browser.close();
})();
