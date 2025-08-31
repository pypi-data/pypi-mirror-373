import { ChatMessages } from './ChatMessages';
import { SEND_ICON, STOP_ICON } from '../Components/icons';
import { LLMStateDisplay } from '../Components/LLMStateDisplay/LLMStateDisplay';

/**
 * Helper class for UI-related functionality
 */
export class ChatUIHelper {
  private chatHistory: HTMLDivElement;
  private messageComponent: ChatMessages;
  private llmStateDisplay: LLMStateDisplay;
  private isShowingConfirmation: boolean = false;

  constructor(
    chatHistory: HTMLDivElement,
    messageComponent: ChatMessages,
    llmStateDisplay: LLMStateDisplay
  ) {
    this.chatHistory = chatHistory;
    this.messageComponent = messageComponent;
    this.llmStateDisplay = llmStateDisplay;
  }

  /**
   * Set whether a confirmation dialog is currently showing
   */
  public setShowingConfirmation(isShowing: boolean): void {
    this.isShowingConfirmation = isShowing;
  }

  /**
   * Reset the LLM state display to generating state, clearing any diff or tool state
   * This is used when starting a new message to ensure we show the generating state
   */
  public resetToGeneratingState(text: string = 'Generating...'): void {
    // Force show LLM state display in generating mode, clearing any existing state
    this.llmStateDisplay.show(text);
  }

  /**
   * Update the loading indicator
   * Now uses LLM state display instead of chat messages
   */
  public updateLoadingIndicator(text: string = 'Generating...'): void {
    // Don't show loading indicator during confirmation dialogs
    if (this.isShowingConfirmation) {
      this.llmStateDisplay.hide();
      return;
    }

    // Don't override diff state or tool state - they have higher priority
    if (
      this.llmStateDisplay.isDiffState() ||
      this.llmStateDisplay.isUsingToolState()
    ) {
      return;
    }

    // Show LLM state display with the status text
    this.llmStateDisplay.show(text);
  }

  /**
   * Remove the loading indicator
   */
  public removeLoadingIndicator(): void {}

  public hideLoadingIndicator(): void {
    this.llmStateDisplay.hide();
  }

  /**
   * Update the send/cancel button state
   */
  public updateSendButton(
    button: HTMLButtonElement,
    isProcessing: boolean
  ): void {
    if (isProcessing) {
      STOP_ICON.render(button);
      button.className = 'sage-ai-cancel-button';
    } else {
      SEND_ICON.render(button);
      button.className = 'sage-ai-send-button';
    }
  }

  /**
   * Update the send/cancel button state
   */
  public updateAgentModeElement(
    element: HTMLElement,
    isProcessing: boolean
  ): void {
    if (isProcessing) {
      element.style.opacity = '0.5';
      element.style.cursor = 'not-allowed';
      element.setAttribute('data-is-disabled', 'true');
    } else {
      element.style.opacity = '1';
      element.style.cursor = 'pointer';
      element.removeAttribute('data-is-disabled');
    }
  }
}
