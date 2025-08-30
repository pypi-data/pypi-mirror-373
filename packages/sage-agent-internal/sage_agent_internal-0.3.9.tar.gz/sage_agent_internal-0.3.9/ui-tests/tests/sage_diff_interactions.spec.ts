import { test, expect } from '@jupyterlab/galata';
import CONFIG from './config';
import { Page } from '@playwright/test';
import {
  APIConfigurator,
  captureScreenshot,
  ChatInteractor,
  NotebookManager
} from './sage_llm_test.spec';

test.use({ autoGoto: false });

/**
 * Prompts for triggering different states - now imported from config.json
 */
const TEST_PROMPTS = CONFIG.TEST_PROMPTS;

test.describe('Sage Diff Interactions Testing', () => {
  test.beforeAll(async () => {
    // Validate configuration before starting tests
    if (CONFIG.SAGE_API_KEY === 'your-api-key-here' || !CONFIG.SAGE_API_KEY) {
      throw new Error(
        '❌ API Key not configured! Please set CONFIG.SAGE_API_KEY in the test file before running tests.'
      );
    }
    console.log('✅ Configuration validated');
  });

  test.beforeEach(async ({ page, baseURL }) => {
    // Navigate to JupyterLab
    await page.goto(`${baseURL}`);

    // Create a new notebook before each test
    await NotebookManager.createNewNotebook(page);

    // Setup API configuration
    await APIConfigurator.setupAPIKey(
      page,
      CONFIG.SAGE_API_KEY,
      CONFIG.CLAUDE_MODEL_URL,
      CONFIG.CLAUDE_MODEL_ID
    );

    // Wait for chat to be ready
    await ChatInteractor.waitForChatReady(page);
  });

  test('inline_chat_diffs', async ({ page }, testInfo) => {
    const testName = 'inline_chat_diffs';
    const diffItems = await ChatInteractor.setupMultiDiffState(
      page,
      testName,
      testInfo
    );

    // Handle inline chat diff hover buttons testing
    console.log('🔹 Testing inline chat diff hover buttons');

    // Verify we have the diff list container
    const diffList = page.locator('.sage-ai-diff-list');
    await expect(diffList).toBeVisible();

    // Handle diff item 1: Click REJECT button
    console.log('🔹 Processing diff item 1: REJECT');
    const item1 = diffItems.nth(0);

    // Hover over the first diff item to reveal buttons
    await item1.hover();
    await page.waitForTimeout(300);

    // Find and click the reject button
    const item1RejectButton = item1.locator('.sage-ai-diff-reject-button');
    await expect(item1RejectButton).toBeVisible();
    await item1RejectButton.click();
    await page.waitForTimeout(500);

    await captureScreenshot(
      page,
      'diff_approval',
      'item1_reject',
      'after_reject',
      testName,
      testInfo
    );

    // Handle diff item 2: Click RUN button
    console.log('🔹 Processing diff item 2: RUN');
    const item2 = diffItems.nth(1);

    // Hover over the second diff item to reveal buttons
    await item2.hover();
    await page.waitForTimeout(300);

    // Find and click the run button
    const item2RunButton = item2.locator('.sage-ai-diff-run-button');
    await expect(item2RunButton).toBeVisible();
    await item2RunButton.click();
    await page.waitForTimeout(500);

    await captureScreenshot(
      page,
      'diff_approval',
      'item2_run',
      'after_run',
      testName,
      testInfo
    );

    // Handle diff item 3: Click APPROVE button
    console.log('🔹 Processing diff item 3: APPROVE');
    const item3 = diffItems.nth(2);

    // Hover over the third diff item to reveal buttons
    await item3.hover();
    await page.waitForTimeout(300);

    // Find and click the approve button
    const item3ApproveButton = item3.locator('.sage-ai-diff-approve-button');
    await expect(item3ApproveButton).toBeVisible();
    await item3ApproveButton.click();
    await page.waitForTimeout(2000);

    await captureScreenshot(
      page,
      'diff_approval',
      'item3_approve',
      'after_approve',
      testName,
      testInfo
    );

    // Final screenshot
    await captureScreenshot(
      page,
      'diff_approval',
      'all_processed',
      'final_state',
      testName,
      testInfo
    );

    console.log('✅ Inline chat diffs test completed successfully');
  });

  test('state_display_diffs', async ({ page }, testInfo) => {
    const testName = 'state_display_diffs';
    console.log(`🧪 Testing diff hover actions for ${testName}`);

    // Setup multi-diff state to get the necessary diff items
    const diffItems = await ChatInteractor.setupMultiDiffState(
      page,
      testName,
      testInfo
    );

    // First click the diff summary bar component
    console.log('🔹 Clicking diff summary bar component');
    const diffSummaryBar = page.locator('.sage-ai-diff-summary-bar');
    await expect(diffSummaryBar).toBeVisible();
    await diffSummaryBar.click();
    await page.waitForTimeout(500);

    await captureScreenshot(
      page,
      'diff_hover_actions',
      'summary_bar_clicked',
      'after_summary_bar_click',
      testName,
      testInfo
    );

    // Find the sage-ai-diff-list within the component
    console.log('🔹 Finding diff list within the component');
    const diffOpened = page.locator('.sage-ai-llm-state-display');
    const diffList = diffOpened.locator('.sage-ai-diff-list');
    await expect(diffList).toBeVisible();

    await captureScreenshot(
      page,
      'diff_hover_actions',
      'diff_list_found',
      'diff_list_visible',
      testName,
      testInfo
    );

    // Get all diff items with hover actions
    const diffItemsWithHover = diffList.locator(
      '.sage-ai-diff-item.sage-ai-diff-item-hover-actions'
    );
    const itemCount = await diffItemsWithHover.count();
    console.log(`✅ Found ${itemCount} diff items with hover actions`);

    // Process each diff item: Click one button per item (Reject, Run, Approve)
    const actions = ['reject', 'run', 'approve'];

    for (let i = 0; i < Math.min(itemCount, 3); i++) {
      const currentItem = diffItemsWithHover.nth(i);
      const action = actions[i];
      console.log(`🔹 Processing diff item ${i + 1}: ${action.toUpperCase()}`);

      // Hover over the item to reveal actions
      await currentItem.hover();
      await page.waitForTimeout(300);

      await captureScreenshot(
        page,
        'diff_hover_actions',
        `item_${i + 1}_hover`,
        'actions_revealed',
        testName,
        testInfo
      );

      // Click the appropriate button for this item
      let button;
      let buttonClass;

      if (action === 'reject') {
        buttonClass =
          '.sage-ai-diff-actions .sage-ai-diff-btn.sage-ai-diff-reject';
        console.log(`🔹 Item ${i + 1}: Clicking Reject button (✕)`);
      } else if (action === 'run') {
        buttonClass =
          '.sage-ai-diff-actions .sage-ai-diff-btn.sage-ai-diff-run';
        console.log(`🔹 Item ${i + 1}: Clicking Run button (play icon)`);
      } else if (action === 'approve') {
        buttonClass =
          '.sage-ai-diff-actions .sage-ai-diff-btn.sage-ai-diff-approve';
        console.log(`🔹 Item ${i + 1}: Clicking Approve button (✓)`);
      }

      button = currentItem.locator(buttonClass);
      await expect(button).toBeVisible();
      await button.click();
      await page.waitForTimeout(500);

      await captureScreenshot(
        page,
        'diff_hover_actions',
        `item_${i + 1}_${action}`,
        `after_${action}_click`,
        testName,
        testInfo
      );

      console.log(`✅ Completed ${action} action for item ${i + 1}`);
    }

    // Final screenshot showing the state after all hover actions
    await captureScreenshot(
      page,
      'diff_hover_actions',
      'all_items_processed',
      'final_state',
      testName,
      testInfo
    );

    console.log('✅ All diff hover actions completed successfully');
  });

  test('navigation_widget_diffs_reject_all', async ({ page }, testInfo) => {
    const testName = 'navigation_widget_diffs_reject_all';
    const diffItems = await ChatInteractor.setupMultiDiffState(
      page,
      testName,
      testInfo
    );

    console.log('🔹 Testing navigation widget Reject All button');

    // Look for the navigation button section with Reject All, Approve All, and Run All buttons
    const navigationButtonSection = page.locator(
      '.sage-ai-diff-navigation-button-section'
    );
    await expect(navigationButtonSection).toBeVisible();

    await captureScreenshot(
      page,
      'diff_approval',
      'navigation_buttons',
      'buttons_visible',
      testName,
      testInfo
    );

    // Click the Reject All button
    const rejectAllButton = navigationButtonSection.locator(
      '.sage-ai-diff-navigation-reject-button'
    );
    await expect(rejectAllButton).toBeVisible();

    // Verify the button contains the expected text and icon
    await expect(rejectAllButton.locator('span')).toContainText('Reject All');
    await expect(
      rejectAllButton.locator('svg[data-icon="sage-agent-internal:reject-icon"]')
    ).toBeVisible();

    console.log('🔹 Clicking Reject All button');
    await rejectAllButton.click();
    await page.waitForTimeout(1000);

    await captureScreenshot(
      page,
      'diff_approval',
      'reject_all',
      'after_reject_all_click',
      testName,
      testInfo
    );

    console.log('✅ Reject All button test completed successfully');
  });

  test('navigation_widget_diffs_approve_all', async ({ page }, testInfo) => {
    const testName = 'navigation_widget_diffs_approve_all';
    const diffItems = await ChatInteractor.setupMultiDiffState(
      page,
      testName,
      testInfo
    );

    console.log('🔹 Testing navigation widget Approve All button');

    // Look for the navigation button section
    const navigationButtonSection = page.locator(
      '.sage-ai-diff-navigation-button-section'
    );
    await expect(navigationButtonSection).toBeVisible();

    await captureScreenshot(
      page,
      'diff_approval',
      'navigation_buttons',
      'buttons_visible',
      testName,
      testInfo
    );

    // Click the Approve All button
    const approveAllButton = navigationButtonSection.locator(
      '.sage-ai-diff-navigation-approve-button'
    );
    await expect(approveAllButton).toBeVisible();

    // Verify the button contains the expected text and icon
    await expect(approveAllButton.locator('span')).toContainText('Approve All');
    await expect(
      approveAllButton.locator('svg[data-icon="sage-agent-internal:approve-icon"]')
    ).toBeVisible();

    console.log('🔹 Clicking Approve All button');
    await approveAllButton.click();
    await page.waitForTimeout(1000);

    await captureScreenshot(
      page,
      'diff_approval',
      'approve_all',
      'after_approve_all_click',
      testName,
      testInfo
    );

    console.log('✅ Approve All button test completed successfully');
  });

  test('navigation_widget_diffs_run_all', async ({ page }, testInfo) => {
    const testName = 'navigation_widget_diffs_run_all';
    const diffItems = await ChatInteractor.setupMultiDiffState(
      page,
      testName,
      testInfo
    );

    console.log('🔹 Testing navigation widget Run All button');

    // Look for the navigation button section
    const navigationButtonSection = page.locator(
      '.sage-ai-diff-navigation-button-section'
    );
    await expect(navigationButtonSection).toBeVisible();

    await captureScreenshot(
      page,
      'diff_approval',
      'navigation_buttons',
      'buttons_visible',
      testName,
      testInfo
    );

    // Click the Run All button
    const runAllButton = navigationButtonSection.locator(
      '.sage-ai-diff-navigation-accept-run-button'
    );
    await expect(runAllButton).toBeVisible();

    // Verify the button contains the expected text and icon
    await expect(runAllButton.locator('span')).toContainText('Run All');

    console.log('🔹 Clicking Run All button');
    await runAllButton.click();
    await page.waitForTimeout(1000);

    await captureScreenshot(
      page,
      'diff_approval',
      'run_all',
      'after_run_all_click',
      testName,
      testInfo
    );

    console.log('✅ Run All button test completed successfully');
  });

  test('inline_cell_diffs', async ({ page }, testInfo) => {
    const testName = 'inline_cell_diffs';
    console.log(
      `🧪 Testing inline cell diffs with cm-chunkButtons for ${testName}`
    );

    // Setup multi-diff state using the first MULTI_DIFF prompt
    console.log('🔹 Setting up multi-diff state with first prompt');
    await ChatInteractor.sendMessage(page, TEST_PROMPTS.MULTI_DIFF[0]);
    await ChatInteractor.waitForResponse(page);
    await page.waitForTimeout(500);

    await captureScreenshot(
      page,
      'inline_cell_diffs',
      'initial_setup',
      'after_first_prompt',
      testName,
      testInfo
    );

    // Find all cm-chunkButtons components on the page
    console.log('🔹 Searching for cm-chunkButtons components');
    let chunkButtons = page.locator('.cm-chunkButtons');
    const chunkButtonsCount = await chunkButtons.count();
    console.log(`✅ Found ${chunkButtonsCount} cm-chunkButtons components`);

    // Verify we have exactly 3 components as expected
    await expect(chunkButtons).toHaveCount(3);

    await captureScreenshot(
      page,
      'inline_cell_diffs',
      'chunk_buttons_found',
      'all_buttons_visible',
      testName,
      testInfo
    );

    // Process first chunk button: REJECT
    console.log('🔹 Processing first cm-chunkButtons: REJECT');
    const firstChunkButton = chunkButtons.nth(0);
    const firstRejectButton = firstChunkButton.locator('button[name="reject"]');
    await expect(firstRejectButton).toBeVisible();
    await firstRejectButton.click();
    await page.waitForTimeout(500);

    await captureScreenshot(
      page,
      'inline_cell_diffs',
      'first_chunk',
      'after_reject',
      testName,
      testInfo
    );

    chunkButtons = page.locator('.cm-chunkButtons');

    // Process second chunk button: ACCEPT
    console.log('🔹 Processing second cm-chunkButtons: ACCEPT');
    const secondChunkButton = chunkButtons.nth(0);
    const secondAcceptButton = secondChunkButton.locator(
      'button[name="accept"]'
    );
    await expect(secondAcceptButton).toBeVisible();
    await secondAcceptButton.click();
    await page.waitForTimeout(500);

    await captureScreenshot(
      page,
      'inline_cell_diffs',
      'second_chunk',
      'after_accept',
      testName,
      testInfo
    );

    chunkButtons = page.locator('.cm-chunkButtons');

    // Process third chunk button: ACCEPT
    console.log('🔹 Processing third cm-chunkButtons: ACCEPT');
    const thirdChunkButton = chunkButtons.nth(0);
    const thirdAcceptButton = thirdChunkButton.locator('button[name="accept"]');
    await expect(thirdAcceptButton).toBeVisible();
    await thirdAcceptButton.click();
    await page.waitForTimeout(1000);

    await captureScreenshot(
      page,
      'inline_cell_diffs',
      'third_chunk',
      'after_accept',
      testName,
      testInfo
    );

    // Send the second MULTI_DIFF prompt
    console.log('🔹 Sending second MULTI_DIFF prompt');
    await ChatInteractor.sendMessage(page, TEST_PROMPTS.MULTI_DIFF[1]);
    await ChatInteractor.waitForResponse(page);
    await page.waitForTimeout(500);

    await captureScreenshot(
      page,
      'inline_cell_diffs',
      'second_prompt',
      'after_second_prompt',
      testName,
      testInfo
    );

    // Find the new cm-chunkButtons component (should be only 1)
    console.log('🔹 Searching for new cm-chunkButtons after second prompt');
    const newChunkButtons = page.locator('.cm-chunkButtons');
    const newChunkButtonsCount = await newChunkButtons.count();
    console.log(
      `✅ Found ${newChunkButtonsCount} cm-chunkButtons components after second prompt`
    );

    // There should be at least 1 new diff to accept
    await expect(newChunkButtons.first()).toBeVisible();

    // Accept the change from the second prompt
    console.log('🔹 Processing new cm-chunkButtons: ACCEPT');
    const newAcceptButton = newChunkButtons
      .first()
      .locator('button[name="accept"]');
    await expect(newAcceptButton).toBeVisible();
    await newAcceptButton.click();
    await page.waitForTimeout(1000);

    await captureScreenshot(
      page,
      'inline_cell_diffs',
      'final_chunk',
      'after_final_accept',
      testName,
      testInfo
    );

    // Final screenshot
    await captureScreenshot(
      page,
      'inline_cell_diffs',
      'completed',
      'final_state',
      testName,
      testInfo
    );

    console.log('✅ Inline cell diffs test completed successfully');
  });
});
