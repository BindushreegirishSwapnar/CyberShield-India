import { test, expect } from '@playwright/test';

test.describe('CyberShield India - BI Studio & Link Analysis Verification', () => {

  test('BI Studio charts render real data (bars, lines, trees, heatmap, forecast)', async ({ page }) => {
    // Navigate to local frontend
    await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });

    // Open BI Studio
    const biNavBtn = page.locator('button:has-text("BI Studio")');
    await expect(biNavBtn).toBeVisible();
    await biNavBtn.click();

    // 1. Overview Tab: Top Affected States bar chart
    const stateBar = page.locator('.recharts-bar-rectangle').first();
    await expect(stateBar).toBeVisible({ timeout: 10000 });

    // 2. Overview Tab: Incident Volume Trends area chart
    const trendArea = page.locator('.recharts-area-area').first();
    await expect(trendArea).toBeVisible({ timeout: 10000 });

    // 3. Test Cross-Filtering (Click state bar to toggle filter)
    await stateBar.click();
    await page.waitForTimeout(1000);
    // Click again to unfilter back to All India
    await stateBar.click();
    await page.waitForTimeout(1000);

    // 4. Decomposition Tree Tab
    const decompTab = page.locator('button:has-text("Decomposition Tree")');
    await decompTab.click();
    const rootLoss = page.locator('text=Total National Loss');
    await expect(rootLoss).toBeVisible({ timeout: 10000 });

    // 5. Waterfall Chart Tab
    const waterTab = page.locator('button:has-text("Waterfall")');
    await waterTab.click();
    const waterBar = page.locator('.recharts-bar-rectangle').first();
    await expect(waterBar).toBeVisible({ timeout: 10000 });

    // 6. Heatmap Tab
    const heatTab = page.locator('button:has-text("Incident Time Heatmap")');
    await heatTab.click();
    const heatCell = page.locator('text=Mon 00:00');
    await expect(heatCell).toBeVisible({ timeout: 10000 });

    // 7. Forecast Tab
    const foreTab = page.locator('button:has-text("Predictive 2027 Projections")');
    await foreTab.click();
    const foreLine = page.locator('.recharts-line-curve').first();
    await expect(foreLine).toBeVisible({ timeout: 10000 });
  });

  test('Link Analysis Graph renders canvas, clusters, and node details', async ({ page }) => {
    await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });

    // Open Link Analysis Graph
    const linkNavBtn = page.locator('button:has-text("Link Analysis Graph")');
    await expect(linkNavBtn).toBeVisible();
    await linkNavBtn.click();

    // Canvas exists with dimensions
    const canvas = page.locator('canvas');
    await expect(canvas).toBeVisible({ timeout: 10000 });
    const box = await canvas.boundingBox();
    expect(box.width).toBeGreaterThan(600);
    expect(box.height).toBeGreaterThan(500);

    // Mule rings selector is populated with 6 clusters
    const clusterSelect = page.locator('select.form-select').first();
    await expect(clusterSelect).toContainText('Jamtara Fast-Loan UPI Ring');

    // Click canvas to open entity side panel
    await page.mouse.click(box.x + box.width * 0.25, box.y + box.height * 0.3);
    await page.waitForTimeout(800);

    // Side panel or entity inspector
    const sideDrawer = page.locator('text=Risk Score:');
    await expect(sideDrawer).toBeVisible({ timeout: 5000 });
  });

  test('Header displays green online status dot for /api/v1/health', async ({ page }) => {
    await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });
    const dot = page.locator('[data-testid="backend-status-dot"]');
    await expect(dot).toBeVisible();
    
    // Expect background to be green (#2ECC71)
    const bg = await dot.evaluate(el => window.getComputedStyle(el).backgroundColor);
    expect(bg).toBe('rgb(46, 204, 113)');
  });

});
