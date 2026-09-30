import { chromium } from '@playwright/test';
import fs from 'fs';
import path from 'path';

(async () => {
  const screenshotDir = path.resolve('public', 'screenshots');
  if (!fs.existsSync(screenshotDir)) {
    fs.mkdirSync(screenshotDir, { recursive: true });
  }

  const browser = await chromium.launch({ headless: true });

  // 1. Desktop Screenshot
  const desktopCtx = await browser.newContext({
    viewport: { width: 1440, height: 1100 }
  });
  const page = await desktopCtx.newPage();

  console.log('Navigating to http://localhost:3000 (Desktop)...');
  await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);

  // Focus on Scam Weather Card
  const weatherCard = await page.$('.scam-weather-card');
  if (weatherCard) {
    console.log('Found scam weather card!');
    await weatherCard.scrollIntoViewIfNeeded();
    await page.waitForTimeout(1000);
    const weatherDesktopPath = path.join(screenshotDir, 'module1_scam_weather_desktop.png');
    await weatherCard.screenshot({ path: weatherDesktopPath });
    console.log(`Saved: ${weatherDesktopPath}`);

    // Also full screen citizen view
    const citizenFull = path.join(screenshotDir, 'citizen_home_desktop.png');
    await page.screenshot({ path: citizenFull });
    console.log(`Saved: ${citizenFull}`);
  } else {
    console.error('Could not find .scam-weather-card');
  }

  // 2. Mobile Screenshot (iPhone 14 / 390x844)
  const mobileCtx = await browser.newContext({
    viewport: { width: 390, height: 844 },
    isMobile: true,
    hasTouch: true
  });
  const mobilePage = await mobileCtx.newPage();

  console.log('Navigating to http://localhost:3000 (Mobile)...');
  await mobilePage.goto('http://localhost:3000', { waitUntil: 'networkidle' });
  await mobilePage.waitForTimeout(2000);

  const mobileWeather = await mobilePage.$('.scam-weather-card');
  if (mobileWeather) {
    await mobileWeather.scrollIntoViewIfNeeded();
    await mobilePage.waitForTimeout(1000);
    const weatherMobilePath = path.join(screenshotDir, 'module1_scam_weather_mobile.png');
    await mobileWeather.screenshot({ path: weatherMobilePath });
    console.log(`Saved: ${weatherMobilePath}`);
  }

  await browser.close();
  console.log('Finished capturing Scam Weather screenshots.');
})();
