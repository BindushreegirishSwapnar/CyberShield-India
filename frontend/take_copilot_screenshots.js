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
    viewport: { width: 1440, height: 1050 }
  });
  const page = await desktopCtx.newPage();

  console.log('Navigating to http://localhost:3000 (Desktop)...');
  await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);

  // Click on "AI Copilot" in Desktop sidebar
  const copilotBtn = await page.locator('button:has-text("Copilot"), button:has-text("AI Copilot")').first();
  if (await copilotBtn.count() > 0) {
    console.log('Opening Copilot tab...');
    await copilotBtn.click();
    await page.waitForTimeout(1500);

    // Click on the first preset prompt: "Show me a pie chart of top scam categories in Maharashtra where amount > 1 lakh"
    console.log('Sending Natural Language BI query...');
    const presetBtn = await page.locator('button:has-text("Show me a pie chart")').first();
    if (await presetBtn.count() > 0) {
      await presetBtn.click();
    } else {
      // Type into textarea and submit
      const input = await page.locator('textarea[placeholder*="Ask Copilot"]').first();
      await input.fill('Show me a pie chart of top scam categories in Maharashtra where amount > 1 lakh');
      const sendBtn = await page.locator('button:has-text("Execute")').first();
      await sendBtn.click();
    }

    // Wait for agent to process and generate inline chart
    console.log('Waiting for agent response and chart generation...');
    await page.waitForTimeout(4000);

    // Expand thinking process details if collapsed
    const thinkingBtn = await page.locator('button:has-text("Agent Execution Plan"), button:has-text("Thinking Process")').first();
    if (await thinkingBtn.count() > 0) {
      await thinkingBtn.click();
      await page.waitForTimeout(800);
    }

    // Screenshot 1: Copilot with thinking steps and inline visual chart
    const chartPath = path.join(screenshotDir, 'module6_copilot_inline_chart_desktop.png');
    await page.screenshot({ path: chartPath });
    console.log(`Saved: ${chartPath}`);
  }

  // 2. Global Command Palette (Ctrl+K)
  console.log('Testing Global Command Palette...');
  // Click Ctrl+K button in header
  const ctrlKBtn = await page.locator('button:has-text("Ctrl+K")').first();
  if (await ctrlKBtn.count() > 0) {
    await ctrlKBtn.click();
  } else {
    await page.keyboard.press('Control+k');
  }
  await page.waitForTimeout(1000);

  // Type search query into palette
  const paletteInput = await page.locator('input[placeholder*="command, case ID"]').first();
  if (await paletteInput.count() > 0) {
    await paletteInput.fill('karnataka');
    await page.waitForTimeout(1500);

    // Screenshot 2: Global Command Palette
    const palettePath = path.join(screenshotDir, 'module6_command_palette_desktop.png');
    await page.screenshot({ path: palettePath });
    console.log(`Saved: ${palettePath}`);

    // Close palette
    await page.keyboard.press('Escape');
    await page.waitForTimeout(500);
  }

  // 3. Mobile Context (iPhone 14)
  const mobileCtx = await browser.newContext({
    viewport: { width: 390, height: 844 },
    isMobile: true,
    hasTouch: true
  });
  const mobilePage = await mobileCtx.newPage();

  console.log('Navigating to http://localhost:3000 (Mobile)...');
  await mobilePage.goto('http://localhost:3000', { waitUntil: 'load' });
  await mobilePage.waitForTimeout(2000);

  // In mobile bottom nav, click Copilot
  await mobilePage.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('.mobile-nav-item'));
    const copilot = btns.find(b => b.textContent.includes('Copilot'));
    if (copilot) copilot.click();
  });
  await mobilePage.waitForTimeout(2000);

  const mobileCopilotPath = path.join(screenshotDir, 'module6_copilot_mobile.png');
  await mobilePage.screenshot({ path: mobileCopilotPath });
  console.log(`Saved: ${mobileCopilotPath}`);

  await browser.close();
  console.log('Finished capturing Module 6 Agentic Copilot screenshots.');
})();
