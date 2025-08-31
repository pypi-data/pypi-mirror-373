import { test, expect } from '@jupyterlab/galata';

/**
 * Don't load JupyterLab webpage before running the tests.
 * This is required to ensure we capture all log messages.
 */
test.use({ autoGoto: false });

test.describe('Sage Agent Extension', () => {
  test('should load the extension', async ({ page, baseURL }) => {
    // Navigate to JupyterLab
    await page.goto(`${baseURL}`);

    // Wait for JupyterLab to be ready
    await page.waitForSelector('#jp-main-dock-panel');

    // Verify that welcome message is displayed
    // const welcomeText = await page.textContent('.sage-ai-system-message');
    // expect(welcomeText).toContain('Welcome to AI Chat');
  });

  test('should have sage AI window with chat input', async ({ page, baseURL }) => {
    // Navigate to JupyterLab
    await page.goto(`${baseURL}`);

    // Wait for JupyterLab to be ready
    await page.waitForSelector('#jp-main-dock-panel');

    // Wait for the sage AI chat container to be present
    await page.waitForSelector('#sage-ai-chat-container', { timeout: 10000 });

    // Verify the sage AI chat container exists and is visible
    const chatContainer = page.locator('#sage-ai-chat-container');
    await expect(chatContainer).toBeVisible();

    // Check that the chat widget is present within the container
    const chatWidget = chatContainer.locator('.sage-ai-chatbox');
    await expect(chatWidget).toBeVisible();

    // Verify that the chat input element is present and visible
    const chatInput = chatWidget.locator('.sage-ai-rich-chat-input');
    await expect(chatInput).toBeVisible();

    // Verify the chat input is interactive (has contentEditable attribute)
    await expect(chatInput).toHaveAttribute('contentEditable', 'true');

    // Check that the send button is present
    const sendButton = chatWidget.locator('.sage-ai-send-button');
    await expect(sendButton).toBeVisible();

    // Verify additional UI elements are present
    const toolbar = chatWidget.locator('.sage-ai-toolbar');
    await expect(toolbar).toBeVisible();
  });
});
