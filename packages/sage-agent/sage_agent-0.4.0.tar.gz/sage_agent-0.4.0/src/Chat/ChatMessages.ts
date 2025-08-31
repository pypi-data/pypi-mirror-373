import { NotebookTools } from '../Notebook/NotebookTools';
import { ToolCall } from '../Services/ToolService';
import { IChatMessage, ICheckpoint, IToolCall } from '../types';
import { ChatHistoryManager, IChatThread } from './ChatHistoryManager';
// Add import for markdown rendering
import { marked } from 'marked';
import { MentionContext } from './ChatContextMenu/ChatContextMenu';
import {
  COPIED_ICON,
  COPY_ICON,
  getToolDisplayMessage,
  getToolIcon
} from '../utils/toolDisplay';
import { DiffApprovalDialog } from '../Components/DiffApprovalDialog';
import { ServiceUtils } from '../Services/ServiceUtils';
import { AppStateService } from '../AppState';
import { ContextService } from '../Services/ContextService';
import {
  renderContextTagsAsStyled,
  getTagTypeFromCssClass
} from '../utils/contextTagUtils';
import { DiffStateService } from '../Services/DiffStateService';
import { CheckpointManager } from '../Services/CheckpointManager';
import { CheckpointRestorationModal } from '../Components/CheckpointRestorationModal';
import { CheckpointRestorationOption } from '../types';
import { NotebookCellStateService } from '../Services/NotebookCellStateService';

/**
 * Component for handling chat message display
 */
export class ChatMessages {
  private container: HTMLDivElement;
  public messageHistory: Array<IChatMessage> = [];
  private userMessages: Array<IChatMessage> = []; // Store original user inputs only
  private lastAddedMessageType: 'tool' | 'normal' | 'user' | null = null;
  private historyManager: ChatHistoryManager;
  private notebookTools: NotebookTools;
  private mentionContexts: Map<string, MentionContext> = new Map();
  private onScrollDownButtonDisplay: () => void;
  private contextService: ContextService;
  private diffStateService: DiffStateService;
  private checkpointManager: CheckpointManager;
  private restorationModal: CheckpointRestorationModal;

  // Continue button related properties
  private waitingReplyBox: HTMLElement | null = null;
  private continueButton: HTMLElement | null = null;
  private promptButtons: HTMLElement[] = [];
  private onContinueCallback: (() => void) | null = null;

  constructor(
    container: HTMLDivElement,
    historyManager: ChatHistoryManager,
    notebookTools: NotebookTools,
    onScrollDownButtonDisplay: () => void
  ) {
    this.container = container;
    this.historyManager = historyManager;
    this.notebookTools = notebookTools;
    this.onScrollDownButtonDisplay = onScrollDownButtonDisplay;
    this.contextService = ContextService.getInstance();
    this.diffStateService = DiffStateService.getInstance();
    this.checkpointManager = CheckpointManager.getInstance();
    this.restorationModal = new CheckpointRestorationModal();
    console.log('[ChatMessages] Initialized with empty message history');

    // Initialize continue button for new chats
    this.addContinueButton();

    // Sync context service with current mention contexts
    this.syncContextService();

    // Subscribe to context changes to refresh message displays
    this.subscribeToContextChanges();

    // Subscribe to diff state changes to update prompt buttons
    this.subscribeToDiffStateChanges();
  }

  /**
   * Load messages from an existing chat thread
   * @param thread The chat thread to load
   */
  async loadFromThread(thread: IChatThread): Promise<void> {
    // Backup current state before clearing
    const backupMessageHistory = [...this.messageHistory];
    const backupUserMessages = [...this.userMessages];
    const backupMentionContexts = new Map(this.mentionContexts);
    const backupLastAddedMessageType = this.lastAddedMessageType;
    const backupContainerHTML = this.container.innerHTML;

    try {
      this.messageHistory = [];
      this.userMessages = [];

      // First clear the UI display
      this.container.innerHTML = '';

      // Set the messageHistory from the thread
      this.messageHistory = [...thread.messages];

      // Extract user messages for context reset situations
      this.userMessages = thread.messages.filter(msg => msg.role === 'user');

      // Load mention contexts from the thread
      this.mentionContexts = new Map(thread.contexts || new Map());

      this.lastAddedMessageType = null;

      // Render all messages to the UI
      await this.renderAllMessages();

      // Initialize continue button after loading messages
      this.addContinueButton();

      console.log(
        `[ChatMessages] Loaded ${thread.messages.length} messages from thread`
      );
    } catch (error) {
      console.error(
        '[ChatMessages] Failed to load thread, restoring backup:',
        error
      );
      // Restore backed up state
      this.messageHistory = backupMessageHistory;
      this.userMessages = backupUserMessages;
      this.mentionContexts = backupMentionContexts;
      this.lastAddedMessageType = backupLastAddedMessageType;
      this.container.innerHTML = backupContainerHTML;

      // Re-throw the error to let the caller handle it
      throw error;
    }
  }

  /**
   * Render all messages from the history to the UI
   */
  private async renderAllMessages(): Promise<void> {
    // Keep track of consecutive message types to group tools
    let lastToolGroup: { assistant: any; results: any[] } | null = null;

    for (const message of this.messageHistory) {
      if (message.role === 'user') {
        // Check if this is a tool result
        if (
          Array.isArray(message.content) &&
          message.content.length > 0 &&
          typeof message.content[0] === 'object' &&
          message.content[0].type === 'tool_result'
        ) {
          // This is a tool result - add it to the current tool group
          if (lastToolGroup) {
            // Render the tool result to UI
            this.renderToolResult(
              message.content[0].tool_name || 'tool',
              message.content[0].content,
              lastToolGroup
            );
            lastToolGroup.results.push(message.content[0]);
          }
        } else {
          // Regular user message
          lastToolGroup = null;
          this.renderUserMessage(
            typeof message.content === 'string'
              ? message.content
              : JSON.stringify(message.content)
          );
        }
      } else if (message.role === 'assistant') {
        // Check if this is a tool call
        if (
          Array.isArray(message.content) &&
          message.content.length > 0 &&
          typeof message.content[0] === 'object' &&
          message.content[0].type === 'tool_use'
        ) {
          // This is the start of a new tool group
          lastToolGroup = {
            assistant: message,
            results: []
          };

          // Render each tool call to UI
          for (const content of message.content) {
            if (content.type === 'tool_use') {
              this.renderToolCall(content);
            }
          }
        } else {
          // Regular assistant message
          lastToolGroup = null;
          await this.renderAssistantMessage(
            typeof message.content === 'string'
              ? message.content
              : Array.isArray(message.content) &&
                  typeof message.content[0] === 'object' &&
                  message.content[0].text
                ? message.content[0].text
                : JSON.stringify(message.content)
          );
        }
      } else if (ServiceUtils.isDiffApprovalMessage(message)) {
        this.renderDiffApprovalFromHistory(message.content[0]);
      }
    }

    this.scrollToBottom();

    this.removeLoadingText();

    // Update continue button visibility after rendering all messages
    this.updateContinueButtonVisibility();

    // Ensure the waiting reply box is at the bottom after all messages are rendered
    this.ensureWaitingReplyBoxIsLast();
  }

  /**
   * Remove the tool loading text
   */
  public removeLoadingText(): void {
    this.container
      .querySelectorAll('.sage-ai-loading-text')
      .forEach(content => {
        content.classList.remove('sage-ai-loading-text');
      });
  }

  /**
   * Ensure the waiting reply box is positioned as the last child if it exists
   * Call this after adding any new message elements to the container
   */
  private ensureWaitingReplyBoxIsLast(): void {
    if (
      this.waitingReplyBox &&
      this.waitingReplyBox.parentNode === this.container
    ) {
      this.container.removeChild(this.waitingReplyBox);
      this.container.appendChild(this.waitingReplyBox);
    }
  }

  /**
   * Safely render markdown content with sanitization
   */
  private async renderMarkdown(text: string): Promise<string> {
    try {
      // Set options to ensure safe rendering with sanitization
      marked.setOptions({
        gfm: true, // GitHub flavored markdown
        breaks: false // Convert line breaks to <br>
      });

      // Sanitize the HTML output from marked
      return await marked.parse(text);
    } catch (error) {
      console.error('Error rendering markdown:', error);
      // Fall back to plain text if rendering fails
      return this.escapeHtml(text);
    }
  }

  /**
   * Escape HTML special characters to prevent XSS when fallback is needed
   */
  private escapeHtml(text: string): string {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  /**
   * Render a user message to the UI (without adding to history)
   */
  private renderUserMessage(message: string): void {
    this.closeToolGroupIfOpen();

    const messageElement = document.createElement('div');
    messageElement.className = 'sage-ai-message sage-ai-user-message';

    // Create a container for the message content
    const contentElement = document.createElement('div');
    contentElement.className = 'sage-ai-message-content';

    // Parse context tags and render them as styled mentions
    const renderedMessage = renderContextTagsAsStyled(message);

    // If no context tags were found, fall back to regular HTML escaping
    if (renderedMessage === message) {
      contentElement.innerHTML = this.escapeHtml(message).replace(
        /\n/g,
        '<br>'
      );
    } else {
      // Apply line breaks to the rendered message (which already has HTML from context tags)
      contentElement.innerHTML = renderedMessage.replace(/\n/g, '<br>');
    }

    messageElement.append(contentElement);

    this.container.appendChild(messageElement);
    this.ensureWaitingReplyBoxIsLast();

    this.lastAddedMessageType = 'user';

    this.handleScroll();
  }

  public isFullyScrolledToBottom(): boolean {
    const isScrolledToBottom =
      this.container.getAttribute('data-is-scrolled-to-bottom') === 'true';
    return isScrolledToBottom;
  }

  /**
   * Render an assistant message to the UI (without adding to history)
   */
  private async renderAssistantMessage(
    message: string,
    _container?: HTMLElement
  ): Promise<void> {
    this.closeToolGroupIfOpen();

    const messageElement = document.createElement('div');
    messageElement.className = 'sage-ai-message sage-ai-ai-message';

    // Create a container for the message header
    const headerElement = document.createElement('div');
    headerElement.className = 'sage-ai-message-header';

    // Create header image element
    const headerImageElement = document.createElement('div');
    headerImageElement.className = 'sage-ai-message-header-image';
    headerImageElement.innerHTML = `<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M6.6243 10.3334C6.56478 10.1026 6.44453 9.89209 6.27605 9.72361C6.10757 9.55513 5.89702 9.43488 5.6663 9.37536L1.5763 8.32069C1.50652 8.30089 1.44511 8.25886 1.40138 8.20099C1.35765 8.14312 1.33398 8.07256 1.33398 8.00002C1.33398 7.92749 1.35765 7.85693 1.40138 7.79906C1.44511 7.74119 1.50652 7.69916 1.5763 7.67936L5.6663 6.62402C5.89693 6.56456 6.10743 6.44441 6.2759 6.27605C6.44438 6.10769 6.56468 5.89728 6.6243 5.66669L7.67897 1.57669C7.69857 1.50664 7.74056 1.44492 7.79851 1.40095C7.85647 1.35699 7.92722 1.33319 7.99997 1.33319C8.07271 1.33319 8.14346 1.35699 8.20142 1.40095C8.25938 1.44492 8.30136 1.50664 8.32097 1.57669L9.37497 5.66669C9.43449 5.89741 9.55474 6.10796 9.72322 6.27644C9.8917 6.44492 10.1023 6.56517 10.333 6.62469L14.423 7.67869C14.4933 7.69809 14.5553 7.74003 14.5995 7.79808C14.6437 7.85612 14.6677 7.92706 14.6677 8.00002C14.6677 8.07298 14.6437 8.14393 14.5995 8.20197C14.5553 8.26002 14.4933 8.30196 14.423 8.32136L10.333 9.37536C10.1023 9.43488 9.8917 9.55513 9.72322 9.72361C9.55474 9.89209 9.43449 10.1026 9.37497 10.3334L8.3203 14.4234C8.3007 14.4934 8.25871 14.5551 8.20075 14.5991C8.1428 14.6431 8.07205 14.6669 7.9993 14.6669C7.92656 14.6669 7.85581 14.6431 7.79785 14.5991C7.73989 14.5551 7.69791 14.4934 7.6783 14.4234L6.6243 10.3334Z" fill="url(#paint0_linear_445_6567)"/>
      <path d="M13.333 2V4.66667" stroke="url(#paint1_linear_445_6567)" stroke-width="0.984615" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M14.6667 3.33331H12" stroke="url(#paint2_linear_445_6567)" stroke-width="0.984615" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M2.66699 11.3333V12.6666" stroke="url(#paint3_linear_445_6567)" stroke-width="0.984615" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M3.33333 12H2" stroke="url(#paint4_linear_445_6567)" stroke-width="0.984615" stroke-linecap="round" stroke-linejoin="round"/>
      <defs>
      <linearGradient id="paint0_linear_445_6567" x1="1.33398" y1="1.33319" x2="14.6677" y2="14.6669" gradientUnits="userSpaceOnUse">
      <stop stop-color="#FEC163"/>
      <stop offset="1" stop-color="#DE4313"/>
      </linearGradient>
      <linearGradient id="paint1_linear_445_6567" x1="13.333" y1="2" x2="15.0864" y2="2.65753" gradientUnits="userSpaceOnUse">
      <stop stop-color="#FEC163"/>
      <stop offset="1" stop-color="#DE4313"/>
      </linearGradient>
      <linearGradient id="paint2_linear_445_6567" x1="12" y1="3.33331" x2="12.6575" y2="5.08674" gradientUnits="userSpaceOnUse">
      <stop stop-color="#FEC163"/>
      <stop offset="1" stop-color="#DE4313"/>
      </linearGradient>
      <linearGradient id="paint3_linear_445_6567" x1="2.66699" y1="11.3333" x2="3.94699" y2="12.2933" gradientUnits="userSpaceOnUse">
      <stop stop-color="#FEC163"/>
      <stop offset="1" stop-color="#DE4313"/>
      </linearGradient>
      <linearGradient id="paint4_linear_445_6567" x1="2" y1="12" x2="2.96" y2="13.28" gradientUnits="userSpaceOnUse">
      <stop stop-color="#FEC163"/>
      <stop offset="1" stop-color="#DE4313"/>
      </linearGradient>
      </defs>
      </svg>`;

    headerElement.append(headerImageElement);

    // Create header title element
    const headerSageTitleElement = document.createElement('span');
    headerSageTitleElement.className = 'sage-ai-message-header-title';
    headerSageTitleElement.innerText = 'Sage AI';

    headerElement.append(headerSageTitleElement);

    if (this.lastAddedMessageType !== 'user') {
      headerElement.style.display = 'none';
    }

    // Create a container for the message content
    const contentElement = document.createElement('div');
    contentElement.className =
      'sage-ai-message-content sage-ai-markdown-content';
    // Render markdown for AI responses
    contentElement.innerHTML = await this.renderMarkdown(message);

    // Assemble the message
    messageElement.appendChild(headerElement);
    messageElement.appendChild(contentElement);

    const container: HTMLElement = _container ?? this.container;
    container.appendChild(messageElement);
    // Only reposition waiting reply box if we're adding to the main container
    if (container === this.container) {
      this.ensureWaitingReplyBoxIsLast();
    }
    this.lastAddedMessageType = 'normal';

    // Activate any code blocks in the message
    this.activateCodeBlocks(contentElement);

    this.handleScroll();
  }

  /**
   * Activate code blocks with syntax highlighting and copy buttons
   */
  private activateCodeBlocks(container: HTMLElement): void {
    // Find all code blocks
    const codeBlocks = container.querySelectorAll('pre code');

    codeBlocks.forEach(codeBlock => {
      // Create a container for the code block with a copy button
      const codeContainer = document.createElement('div');
      codeContainer.className = 'sage-ai-code-block-container';

      // Create copy button
      const copyButton = document.createElement('button');
      copyButton.className = 'sage-ai-copy-code-button';
      copyButton.innerHTML = COPY_ICON;
      copyButton.title = 'Copy code to clipboard';

      // Add click handler to copy button
      copyButton.addEventListener('click', () => {
        const code = codeBlock.textContent || '';
        navigator.clipboard
          .writeText(code)
          .then(() => {
            copyButton.innerHTML = COPIED_ICON;
            setTimeout(() => {
              copyButton.innerHTML = COPY_ICON;
            }, 2000);
          })
          .catch(err => {
            console.error('Failed to copy code: ', err);
            copyButton.innerHTML = 'Error';
            setTimeout(() => {
              copyButton.innerHTML = COPY_ICON;
            }, 2000);
          });
      });

      // Wrap the original code block
      const preElement = codeBlock.parentElement;
      if (preElement && preElement.tagName === 'PRE') {
        // Insert the code block and copy button into the container
        preElement.parentNode?.insertBefore(codeContainer, preElement);
        codeContainer.appendChild(preElement);
        codeContainer.appendChild(copyButton);
      }
    });
  }

  /**
   * Get the current mention contexts
   * @returns Map of mention contexts
   */
  public getMentionContexts(): Map<string, MentionContext> {
    return new Map(this.mentionContexts);
  }

  /**
   * Set mention contexts
   * @param contexts Map of mention contexts to set
   */
  public setMentionContexts(contexts: Map<string, MentionContext>): void {
    this.mentionContexts = new Map(contexts);
    // Sync with context service
    this.contextService.setContextItems(this.mentionContexts);
  }

  /**
   * Add a mention context
   * @param context The mention context to add
   */
  public addMentionContext(context: MentionContext): void {
    this.mentionContexts.set(context.id, context);
    // Update the persistent storage
    this.historyManager.updateCurrentThreadContexts(this.mentionContexts);
    // Sync with context service
    this.contextService.addContextItem(context);
  }

  /**
   * Remove a mention context
   * @param contextId The ID of the context to remove
   */
  public removeMentionContext(contextId: string): void {
    this.mentionContexts.delete(contextId);
    // Update the persistent storage
    this.historyManager.updateCurrentThreadContexts(this.mentionContexts);
    // Sync with context service
    this.contextService.removeContextItem(contextId);
  }

  /**
   * Sync the local mention contexts with the global context service
   */
  private syncContextService(): void {
    this.contextService.setContextItems(this.mentionContexts);
  }

  /**
   * Subscribe to context changes to refresh message displays when contexts become available
   */
  private subscribeToContextChanges(): void {
    this.contextService.subscribe(newContexts => {
      // Check if we have any user messages that contain context tags that might now be available
      const hasContextTags = this.messageHistory.some(
        message =>
          message.role === 'user' &&
          typeof message.content === 'string' &&
          message.content.includes('<') &&
          message.content.includes('_CONTEXT>')
      );

      if (hasContextTags) {
        console.log(
          '[ChatMessages] Context items updated, refreshing message displays'
        );
        this.refreshMessageDisplays();
      }
    });
  }

  /**
   * Subscribe to diff state changes to update prompt buttons when diffs are resolved
   */
  private subscribeToDiffStateChanges(): void {
    // Listen for when all diffs are resolved
    this.diffStateService.allDiffsResolved$.subscribe(({ notebookId }) => {
      console.log(
        '[ChatMessages] All diffs resolved, checking prompt buttons',
        { notebookId }
      );
      if (this.shouldShowContinueButton()) {
        this.checkAndShowPromptButtons();
        this.ensureWaitingReplyBoxIsLast();
      }
    });

    // Also listen for approval status changes to react immediately when diffs are approved
    this.diffStateService.getApprovalStatusChanges$().subscribe(status => {
      console.log('[ChatMessages] Diff approval status changed', status);
      if (status.allResolved) {
        if (this.shouldShowContinueButton()) {
          this.checkAndShowPromptButtons();
          this.ensureWaitingReplyBoxIsLast();
        }
      }
    });
  }

  /**
   * Refresh displays of existing messages that contain context tags
   */
  private refreshMessageDisplays(): void {
    // Find all user message elements that may contain context tags
    const userMessages = this.container.querySelectorAll(
      '.sage-ai-user-message .sage-ai-message-content'
    );

    userMessages.forEach(messageContent => {
      const currentHTML = messageContent.innerHTML;

      // Check if this message contains context mentions (broken or valid)
      if (currentHTML.includes('sage-ai-mention')) {
        // Extract the original message by looking for data attributes or parsing
        // We'll need to reverse engineer the original message from the HTML
        const originalMessage =
          this.extractOriginalMessageFromHTML(currentHTML);

        if (originalMessage) {
          // Re-render the message with updated context
          const renderedMessage = renderContextTagsAsStyled(originalMessage);
          messageContent.innerHTML = renderedMessage.replace(/\n/g, '<br>');
        }
      }
    });
  }

  /**
   * Extract the original message content from rendered HTML
   * This is needed to re-render messages when contexts become available
   */
  private extractOriginalMessageFromHTML(html: string): string | null {
    try {
      // Create a temporary element to parse the HTML
      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = html;

      // Extract text content and context tags
      let originalMessage = '';

      tempDiv.childNodes.forEach(node => {
        if (node.nodeType === Node.TEXT_NODE) {
          originalMessage += node.textContent || '';
        } else if (node.nodeType === Node.ELEMENT_NODE) {
          const element = node as Element;

          if (element.classList.contains('sage-ai-mention')) {
            // This is a mention - extract the context ID and recreate the tag
            const contextId = element.getAttribute('data-context-id');
            const mentionText = element.textContent || '';

            if (contextId) {
              // Determine the tag type from CSS classes instead of checking context validity
              const tagType = getTagTypeFromCssClass(element);
              originalMessage += `<${tagType}>#{${contextId}}</${tagType}>`;
            } else {
              // Fallback to the displayed text
              originalMessage += mentionText;
            }
          } else if (element.tagName === 'BR') {
            originalMessage += '\n';
          } else {
            originalMessage += element.textContent || '';
          }
        }
      });

      return originalMessage;
    } catch (error) {
      console.warn('[ChatMessages] Failed to extract original message:', error);
      return null;
    }
  }

  /**
   * Get context tag type from context type
   */
  private getContextTagType(contextType: string): string {
    switch (contextType) {
      case 'snippets':
        return 'SNIPPET_CONTEXT';
      case 'data':
        return 'DATA_CONTEXT';
      case 'variable':
        return 'VARIABLE_CONTEXT';
      case 'cell':
        return 'CELL_CONTEXT';
      default:
        return 'DATA_CONTEXT';
    }
  }

  /**
   * Process user message content to render context tags as styled mentions
   * @param message The raw user message that may contain context tags
   * @returns Processed HTML string with styled mentions and line breaks
   */
  private processUserMessageContent(message: string): string {
    // First, render context tags as styled mentions
    let processedMessage = renderContextTagsAsStyled(message);

    // Escape any remaining HTML and replace \n with <br> to display line breaks
    // We need to be careful not to escape the HTML we just added for mentions
    // So we'll split by mention spans, escape the text parts, then rejoin
    const mentionSpanRegex =
      /<span class="sage-ai-mention[^"]*"[^>]*>[^<]*<\/span>/g;
    const parts = processedMessage.split(mentionSpanRegex);
    const mentions = processedMessage.match(mentionSpanRegex) || [];

    let result = '';
    for (let i = 0; i < parts.length; i++) {
      // Escape the text part and convert newlines
      result += this.escapeHtml(parts[i]).replace(/\n/g, '<br>');
      // Add the mention span if it exists
      if (mentions[i]) {
        result += mentions[i];
      }
    }

    return result;
  }

  /**
   * Add a user message to the chat history
   * @param message The sanitized message
   * @param rawMessage The raw user input, containing @mentions
   */
  addUserMessage(message: string, rawMessage?: string): void {
    this.closeToolGroupIfOpen();

    console.log('[ChatMessages] Adding user message:', message);
    const messageElement = document.createElement('div');
    messageElement.className = 'sage-ai-message sage-ai-user-message';
    messageElement.style.position = 'relative';

    // Create a container for the message content
    const contentElement = document.createElement('div');
    contentElement.className = 'sage-ai-message-content';

    // Process the message to render context tags as styled mentions
    const processedMessage = this.processUserMessageContent(message);
    contentElement.innerHTML = processedMessage;

    // Create rollback element container
    const rollbackElement = document.createElement('div');
    rollbackElement.className = 'sage-ai-rollback-element';

    // Create the icon element
    const rollbackIcon = document.createElement('span');
    rollbackIcon.className = 'sage-ai-rollback-icon';
    rollbackIcon.innerHTML = `<svg width="13" height="13" viewBox="0 0 16 17" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M5.99984 9.83341L2.6665 6.50008M2.6665 6.50008L5.99984 3.16675M2.6665 6.50008H9.6665C10.148 6.50008 10.6248 6.59492 11.0697 6.77919C11.5145 6.96346 11.9187 7.23354 12.2592 7.57402C12.5997 7.9145 12.8698 8.31871 13.0541 8.76357C13.2383 9.20844 13.3332 9.68523 13.3332 10.1667C13.3332 10.6483 13.2383 11.1251 13.0541 11.5699C12.8698 12.0148 12.5997 12.419 12.2592 12.7595C11.9187 13.1 11.5145 13.37 11.0697 13.5543C10.6248 13.7386 10.148 13.8334 9.6665 13.8334H7.33317" stroke="var(--jp-ui-font-color2)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`;

    // Create the tooltip element
    const rollbackTooltip = document.createElement('span');
    rollbackTooltip.className = 'sage-ai-rollback-tooltip';
    rollbackTooltip.textContent = 'Restore checkpoint';

    rollbackElement.appendChild(rollbackTooltip);
    rollbackElement.appendChild(rollbackIcon);

    try {
      // Create checkpoint for this user message
      const checkpoint = this.createCheckpoint(rawMessage || message);

      // Add data attribute to the message element
      messageElement.setAttribute('data-checkpoint-id', checkpoint.id);

      // Add click handler for restore functionality
      rollbackElement.addEventListener('click', () => {
        this.handleRestoreCheckpoint(checkpoint);
      });

      messageElement.append(contentElement, rollbackElement);
    } catch (error) {
      console.error('[ChatMessages] Error creating checkpoint:', error);
      messageElement.append(contentElement);
    }

    this.container.appendChild(messageElement);
    this.ensureWaitingReplyBoxIsLast();

    // Add to message history for context
    const userMessage = { role: 'user', content: message };

    this.messageHistory.push(userMessage);
    // Also store in userMessages for context reset situations
    this.userMessages.push({ role: 'user', content: message });

    // Update the persistent storage with contexts
    this.historyManager.updateCurrentThreadMessages(
      this.messageHistory,
      this.mentionContexts
    );

    this.lastAddedMessageType = 'user';

    // Hide the waiting reply box when user sends a new message
    this.hideWaitingReplyBox();

    // Do NOT automatically check continue button visibility after user message
    // The waiting reply box should only be shown when wait_user_reply tool is called

    this.handleScroll();

    console.log('[ChatMessages] User message added to history');
    console.log(
      '[ChatMessages] Current message history:',
      JSON.stringify(this.messageHistory)
    );
    console.log(
      '[ChatMessages] Current user messages:',
      JSON.stringify(this.userMessages)
    );
  }

  /**
   * Add a system message to the chat history
   */
  addSystemMessage(message: string): void {
    this.closeToolGroupIfOpen();

    console.log('[ChatMessages] Adding system message:', message);
    const messageElement = document.createElement('div');
    messageElement.className = 'sage-ai-message sage-ai-system-message';

    const textElement = document.createElement('p');
    textElement.className = 'sage-ai-system-message-text';
    textElement.innerHTML = message;
    messageElement.appendChild(textElement);
    this.container.appendChild(messageElement);
    this.ensureWaitingReplyBoxIsLast();

    this.lastAddedMessageType = 'normal';

    this.handleScroll();

    console.log('[ChatMessages] System message added (not saved to history)');
    // System messages are not saved to history
  }

  /**
   * Add a diff approval dialog to the chat history
   * This creates a persistent chat entry that won't be sent to the LLM
   */
  addDiffApprovalDialog(notebookPath?: string, diffCells?: any[]): void {
    console.log('[ChatMessages] Adding diff approval dialog to chat');

    // Add to message history in a format that will be filtered from LLM requests
    // Save the actual diff content instead of HTML
    const diffApprovalMessage = {
      role: 'diff_approval',
      content: [
        {
          type: 'diff_approval',
          id: `diff_approval_${Date.now()}`,
          timestamp: new Date().toISOString(),
          diff_cells: diffCells
            ? diffCells.map(cell => ({
                cellId: cell.cellId,
                type: cell.type,
                originalContent: cell.originalContent || '',
                newContent: cell.newContent || '',
                displaySummary: cell.displaySummary || `${cell.type} cell`
              }))
            : []
        }
      ]
    };

    this.messageHistory.push(diffApprovalMessage);

    // Update the persistent storage with contexts
    this.historyManager.updateCurrentThreadMessages(
      this.messageHistory,
      this.mentionContexts
    );

    console.log(
      '[ChatMessages] Diff approval dialog added to chat and history'
    );
  }

  /**
   * Add an error message to the chat history
   */
  addErrorMessage(message: string): void {
    this.closeToolGroupIfOpen();

    console.log('[ChatMessages] Adding error message:', message);
    const messageElement = document.createElement('div');
    messageElement.className = 'sage-ai-message sage-ai-error-message';
    messageElement.textContent = message;
    this.container.appendChild(messageElement);

    this.lastAddedMessageType = 'normal';

    this.handleScroll();

    console.log('[ChatMessages] Error message added (not saved to history)');
    // Error messages are not saved to history
  }

  /**
   * Close the current tool group if one is open
   */
  private closeToolGroupIfOpen(): void {
    if (this.lastAddedMessageType === 'tool') {
      this.lastAddedMessageType = null;
    }
  }

  /**
   * Render a single tool call
   */
  private renderToolCall(toolCall: IToolCall): void {
    if (toolCall.name === 'notebook-wait_user_reply') {
      return;
    }

    const container = document.createElement('div');
    container.classList.add('sage-ai-tool-call-v1');
    container.setAttribute('sage-ai-tool-call-name', toolCall.name);

    // Add the SVG icon
    const iconElement = document.createElement('div');
    iconElement.innerHTML = getToolIcon(toolCall.name);
    container.appendChild(iconElement.firstChild!);

    // Add the text
    const textElement = document.createElement('span');
    textElement.innerHTML = getToolDisplayMessage(
      toolCall.name,
      toolCall.input
    );
    textElement.className = 'sage-ai-loading-text';
    container.appendChild(textElement);

    this.upsertCellIdLabelInDOM(container, toolCall.name, toolCall.input);

    // Append to the container and scroll
    this.container.appendChild(container);
    this.ensureWaitingReplyBoxIsLast();

    this.handleScroll();

    this.lastAddedMessageType = 'tool'; // Mark as tool interaction
  }

  /**
   * Add tool calls to the chat history
   */
  addToolCalls(toolCalls: IToolCall[]): void {
    if (!toolCalls || toolCalls.length === 0) {
      console.log('[ChatMessages] No tool calls to add');
      return;
    }

    console.log('[ChatMessages] Adding tool calls:', toolCalls.length);

    // Add each tool call to history and render
    toolCalls.forEach((toolCall, index) => {
      console.log(
        `[ChatMessages] Processing tool call #${index + 1}:`,
        toolCall.name
      );
      this.renderToolCall(toolCall);

      // Add to message history
      const toolCallMessage = {
        role: 'assistant',
        content: [
          {
            type: 'tool_use',
            id: toolCall.id,
            name: toolCall.name,
            input: toolCall.input
          }
        ]
      };

      this.messageHistory.push(toolCallMessage);

      // Update the persistent storage with contexts
      this.historyManager.updateCurrentThreadMessages(
        this.messageHistory,
        this.mentionContexts
      );

      console.log(`[ChatMessages] Tool call #${index + 1} added to history`);
    });

    console.log(
      '[ChatMessages] All tool calls added, current history length:',
      this.messageHistory.length
    );
    console.log(
      '[ChatMessages] Last message in history:',
      JSON.stringify(this.messageHistory[this.messageHistory.length - 1])
    );
  }

  /**
   * Add a streaming tool call container to the chat history
   * @returns The container element to be updated with streaming tool call content
   */
  addStreamingToolCall(): HTMLDivElement {
    this.closeToolGroupIfOpen();

    console.log('[ChatMessages] Adding streaming tool call container');

    // Remove any existing streaming cursor from text streaming
    const existingCursor = this.container.querySelector(
      '.sage-ai-streaming-cursor'
    );
    if (existingCursor) {
      existingCursor.remove();
    }

    // Create a container for the streaming tool call
    const toolCallContainer = document.createElement('div');
    toolCallContainer.className =
      'sage-ai-tool-call-v1 sage-ai-streaming-tool-call';
    toolCallContainer.setAttribute('data-tool-call', '{}'); // Store single tool call

    // Add a placeholder for the tool call content
    const toolCallPlaceholder = document.createElement('div');
    toolCallPlaceholder.className = 'sage-ai-streaming-tool-call-placeholder';
    toolCallPlaceholder.innerHTML = 'Sage is thinking about tools to use...';

    // Add a streaming cursor to the tool call
    const cursor = document.createElement('span');
    cursor.classList.add('sage-ai-streaming-cursor');
    toolCallPlaceholder.appendChild(cursor);

    toolCallContainer.appendChild(toolCallPlaceholder);

    this.container.appendChild(toolCallContainer);
    this.ensureWaitingReplyBoxIsLast();

    this.handleScroll();

    console.log(
      '[ChatMessages] Streaming tool call container added (not yet in history)'
    );

    return toolCallContainer;
  }

  /**
   * Update a streaming tool call with new tool call information
   * @param toolCallContainer The tool call container to update
   * @param toolUse The tool use information to add or update
   */
  updateStreamingToolCall(
    toolCallContainer: HTMLDivElement,
    toolUse: any
  ): void {
    console.log(
      '[ChatMessages] Updating streaming tool call with:',
      toolUse.name
    );

    if (toolCallContainer) {
      // Remove placeholder if it exists
      const placeholder = toolCallContainer.querySelector(
        '.sage-ai-streaming-tool-call-placeholder'
      );
      if (placeholder) {
        placeholder.remove();
      }

      // Update the tool call data
      toolCallContainer.setAttribute('data-tool-call', JSON.stringify(toolUse));
      toolCallContainer.setAttribute('sage-ai-tool-call-name', toolUse.name);

      // Only add icon if it doesn't exist yet
      let iconElement = toolCallContainer.querySelector(
        '.sage-ai-tool-call-icon'
      );
      if (!iconElement) {
        iconElement = document.createElement('div');
        iconElement.className = 'sage-ai-tool-call-icon';
        iconElement.innerHTML = getToolIcon(toolUse.name);
        toolCallContainer.appendChild(iconElement);
      }

      // Update text element if it exists, or create it if it doesn't
      let textElement = toolCallContainer.querySelector(
        '.sage-ai-loading-text'
      );
      const newText = getToolDisplayMessage(toolUse.name, toolUse.input);

      if (textElement) {
        // Only update if text has changed
        if (textElement.innerHTML !== newText) {
          textElement.innerHTML = newText;
        }
      } else {
        // Create text element if it doesn't exist
        textElement = document.createElement('span');
        textElement.innerHTML = newText;
        textElement.className = 'sage-ai-loading-text';
        toolCallContainer.appendChild(textElement);
      }

      this.upsertCellIdLabelInDOM(
        toolCallContainer,
        toolUse.name,
        toolUse.input
      );

      this.handleScroll();

      console.log('[ChatMessages] Streaming tool call updated');
    } else {
      console.warn(
        '[ChatMessages] Warning: Tool call container not found in streaming message element'
      );
    }
  }

  /**
   * Finalize a streaming tool call, saving it to history
   * @param toolCallContainer The tool call container to finalize
   */
  finalizeStreamingToolCall(toolCallContainer: HTMLDivElement): void {
    console.log('[ChatMessages] Finalizing streaming tool call');

    // Remove the streaming cursor first
    const cursor = toolCallContainer.querySelector('.sage-ai-streaming-cursor');
    if (cursor) {
      cursor.remove();
    }

    const textLoadingElement = toolCallContainer.querySelector(
      '.sage-ai-loading-text'
    );
    if (textLoadingElement) {
      textLoadingElement.classList.remove('sage-ai-loading-text');
    }

    // Get the tool call data
    const toolCallStr =
      toolCallContainer.getAttribute('data-tool-call') || '{}';
    const toolCall = JSON.parse(toolCallStr);

    console.log('[ChatMessages] Finalized tool call:', toolCall.name);

    if (toolCall.name) {
      // Now that streaming is complete, render the definitive tool call properly
      this.renderToolCall(toolCall);

      // Remove the streaming tool call element
      toolCallContainer.remove();

      // Add to message history
      const toolCallMessage = {
        role: 'assistant',
        content: [
          {
            type: 'tool_use',
            id: toolCall.id,
            name: toolCall.name,
            input: toolCall.input
          }
        ]
      };

      this.messageHistory.push(toolCallMessage);

      // Update the persistent storage with contexts
      this.historyManager.updateCurrentThreadMessages(
        this.messageHistory,
        this.mentionContexts
      );

      console.log('[ChatMessages] Finalized tool call added to history');
      console.log(
        '[ChatMessages] Current history length:',
        this.messageHistory.length
      );
    } else {
      console.warn(
        '[ChatMessages] Warning: No tool call data found when finalizing streaming tool call'
      );
    }

    console.log('[ChatMessages] Streaming tool call finalized');
  }

  /**
   * Render a tool result
   */
  private renderToolResult(
    toolName: string,
    result: any,
    toolCallData: any
  ): void {
    console.log('[ChatMessages] Rendering tool result:', result);
    const toolCallLoading = this.container.querySelector(
      '.sage-ai-loading-text'
    );
    if (toolCallLoading) {
      toolCallLoading.classList.remove('sage-ai-loading-text');
      const container = toolCallLoading.parentElement!;
      const toolCall = container.getAttribute(
        'sage-ai-tool-call-name'
      ) as ToolCall;

      const error = getResultError(result);
      if (typeof error === 'string') {
        container.classList.add('error-state');
        container.title = error;
      }

      this.upsertCellIdLabelInDOM(container, toolCall, toolCallData, result);

      if (toolCall === 'notebook-edit_plan') {
        container.classList.add('clickable');

        container.addEventListener('click', () => {
          void this.notebookTools.scrollToPlanCell();
        });
      }

      this.lastAddedMessageType = 'tool';
    }

    this.handleScroll();
  }

  private upsertCellIdLabelInDOM(
    container: HTMLElement,
    toolCallName: string,
    toolCallData: any,
    result?: any
  ) {
    const oldLabel = container.querySelector('.sage-ai-tool-call-cell');
    if (oldLabel) {
      oldLabel.remove();
    }

    const shouldScrollToCellById = [
      'notebook-add_cell',
      'notebook-edit_cell',
      'notebook-run_cell'
    ].includes(toolCallName);
    if (shouldScrollToCellById) {
      let cellId: string = '';

      if (typeof result === 'string' && /^cell_(\d+)$/.test(result)) {
        cellId = result;
      }

      let toolCallCellId = toolCallData?.assistant?.content[0]?.input?.cell_id;
      if (
        typeof toolCallCellId === 'string' &&
        /^cell_(\d+)$/.test(toolCallCellId)
      ) {
        cellId = toolCallCellId;
      }

      if (
        // ...existing code...
        typeof toolCallData.cell_id === 'string' &&
        /^cell_(\d+)$/.test(toolCallData.cell_id)
      ) {
        cellId = toolCallData.cell_id;
      }

      if (cellId && /^cell_(\d+)$/.test(cellId)) {
        container.classList.add('clickable');

        const cellIdLabel = document.createElement('div');
        cellIdLabel.classList.add('sage-ai-tool-call-cell');
        cellIdLabel.innerHTML = cellId;

        container.appendChild(cellIdLabel);

        container.addEventListener('click', () => {
          void this.notebookTools.scrollToCellById(cellId);
        });
      }
    }
  }

  /**
   * Add a tool execution result to the chat history
   */
  addToolResult(
    toolName: string,
    toolUseId: string,
    result: any,
    toolCallData: any
  ): void {
    console.log('[ChatMessages] Adding tool result for:', toolName);
    this.renderToolResult(toolName, result, toolCallData);

    // Add to message history as user message (tool results are considered user messages)
    const toolResultMessage = {
      role: 'user',
      content: [
        {
          type: 'tool_result',
          tool_use_id: toolUseId,
          content: result
        }
      ]
    };

    this.messageHistory.push(toolResultMessage);

    // Update the persistent storage with contexts
    this.historyManager.updateCurrentThreadMessages(
      this.messageHistory,
      this.mentionContexts
    );

    console.log('[ChatMessages] Tool result added to history');
    console.log(
      '[ChatMessages] Current history length:',
      this.messageHistory.length
    );
    console.log(
      '[ChatMessages.addToolResult] Last message in history:',
      JSON.stringify(this.messageHistory[this.messageHistory.length - 1])
    );
  }

  /**
   * Add a loading indicator to the chat history
   */
  addLoadingIndicator(text: string = 'Generating...'): HTMLDivElement {
    this.closeToolGroupIfOpen();

    console.log('[ChatMessages] Adding loading indicator:', text);

    const loadingElement = document.createElement('div');
    loadingElement.className = 'sage-ai-message sage-ai-loading';

    // Create animated dots
    const dotsContainer = document.createElement('div');
    dotsContainer.className = 'sage-ai-blob-loader';

    loadingElement.appendChild(dotsContainer);

    // Create text element
    const textSpan = document.createElement('span');
    textSpan.textContent = text;

    loadingElement.appendChild(textSpan);

    this.handleScroll();

    this.container.appendChild(loadingElement);
    this.ensureWaitingReplyBoxIsLast();

    return loadingElement;
  }

  /**
   * Remove an element from the chat history
   */
  removeElement(element: HTMLElement): void {
    console.log('[ChatMessages] Removing element from UI');
    if (this.container.contains(element)) {
      this.container.removeChild(element);
    }
  }

  /**
   * Get the message history
   */
  getMessageHistory(): Array<IChatMessage> {
    console.log(
      '[ChatMessages] Getting message history, length:',
      this.messageHistory.length
    );
    return [...this.messageHistory];
  }

  /**
   * Update a streaming message with new text
   * @param messageElement The message element to update
   * @param text The text to append
   */
  async updateStreamingMessage(
    messageElement: HTMLDivElement,
    text: string
  ): Promise<void> {
    // console.log(
    //   '[ChatMessages] Updating streaming message with text:',
    //   text.substring(0, 30) + (text.length > 30 ? '...' : '')
    // );

    const content = messageElement.querySelector(
      '.sage-ai-message-content'
    ) as HTMLElement; // Add explicit type cast to HTMLElement

    if (content) {
      // Accumulate the raw text in data attribute to avoid race conditions
      const currentRawText = content.getAttribute('data-raw-text') || '';
      const newRawText = currentRawText + text;
      content.setAttribute('data-raw-text', newRawText);

      // For streaming display, we use simplified rendering
      // This avoids race conditions in markdown parsing
      content.innerHTML = await this.renderMarkdown(newRawText);

      const cursor = document.createElement('span');
      cursor.classList.add('sage-ai-streaming-cursor');

      // Append cursor to the last child of content, or to content if no children exist
      const lastChild = content.lastElementChild;
      const lastChildLastElementChild = lastChild?.lastElementChild;
      if (lastChildLastElementChild) {
        lastChildLastElementChild.appendChild(cursor);
      } else if (lastChild) {
        lastChild.appendChild(cursor);
      } else {
        content.appendChild(cursor);
      }

      this.handleScroll();

      // Log current accumulated streaming text length
      // console.info(
      //   '[ChatMessages] Current accumulated streaming text length:',
      //   newRawText.length
      // );
    } else {
      console.warn(
        '[ChatMessages] Warning: Content span not found in streaming message element'
      );
    }
  }

  /**
   * Finalize a streaming message, saving it to history
   * @param messageElement The message element to finalize
   */
  async finalizeStreamingMessage(
    messageElement: HTMLDivElement
  ): Promise<void> {
    console.log('[ChatMessages] Finalizing streaming message');
    const content = messageElement.querySelector(
      '.sage-ai-message-content'
    ) as HTMLElement; // Add explicit type cast to HTMLElement

    if (content) {
      // Get the complete accumulated text
      const messageText = content.getAttribute('data-raw-text') || '';
      console.log(
        '[ChatMessages] Finalized message text length:',
        messageText.length
      );
      console.log(
        '[ChatMessages] First 100 chars of finalized message:',
        messageText.substring(0, 100) + (messageText.length > 100 ? '...' : '')
      );

      // Now that streaming is complete, render the definitive message properly
      await this.renderAssistantMessage(
        messageText,
        messageElement.parentElement || undefined
      );
      // Finishes the streaming message lifecycle removing it
      messageElement.remove();

      // Add to message history
      const aiMessage = {
        role: 'assistant',
        content: messageText
      };
      this.messageHistory.push(aiMessage);

      // Update the persistent storage with contexts
      this.historyManager.updateCurrentThreadMessages(
        this.messageHistory,
        this.mentionContexts
      );

      console.log('[ChatMessages] Finalized AI message added to history');
      console.log(
        '[ChatMessages] Current history length:',
        this.messageHistory.length
      );

      // Do NOT automatically check continue button visibility after assistant message
      // The waiting reply box should only be shown when wait_user_reply tool is called
    } else {
      console.warn(
        '[ChatMessages] Warning: Content span not found when finalizing streaming message'
      );
    }

    this.handleScroll();

    // Remove the streaming class now that it's complete
    messageElement.classList.remove('sage-ai-streaming-message');
    const cursor = messageElement.querySelector('sage-ai-streaming-cursor');
    if (cursor) {
      cursor.remove();
    }
    console.log('[ChatMessages] Streaming message finalized and class removed');
  }

  public handleScroll(): void {
    if (this.isFullyScrolledToBottom()) {
      this.scrollToBottom();
    } else {
      this.onScrollDownButtonDisplay();
    }
  }

  /**
   * Scroll the chat container to the bottom
   */
  public scrollToBottom(): void {
    if (this.container) {
      this.container.scrollTop = this.container.scrollHeight + 50;
    }

    this.onScrollDownButtonDisplay();
  }

  /**
   * Add a continue button that allows users to continue the conversation
   * The button will be shown based on message content and thread state
   */
  public addContinueButton(): void {
    console.log('[ChatMessages] addContinueButton() called');

    // Remove existing continue button if it exists
    this.removeContinueButton();

    // Create the waiting reply box
    this.waitingReplyBox = document.createElement('div');
    this.waitingReplyBox.className = 'sage-ai-waiting-reply-container';

    const text = document.createElement('div');
    text.className = 'sage-ai-waiting-reply-text';
    text.textContent = 'Sage will continue working after you reply';

    this.waitingReplyBox.appendChild(text);

    // Create prompt buttons container
    const buttonsContainer = document.createElement('div');
    buttonsContainer.className = 'sage-ai-prompt-buttons-container';
    buttonsContainer.style.display = 'flex';
    buttonsContainer.style.flexDirection = 'column';
    buttonsContainer.style.gap = '8px';
    buttonsContainer.style.marginTop = '12px';

    // Initialize empty prompt buttons array - buttons will be created dynamically
    this.promptButtons = [];

    // Create one default "Continue" button (initially hidden)
    const defaultButton = document.createElement('button');
    defaultButton.className = 'sage-ai-prompt-button';
    defaultButton.textContent = 'Continue';
    defaultButton.style.display = 'none';

    defaultButton.addEventListener('click', () => {
      const currentPrompt = defaultButton.textContent || '';
      console.log(
        '[ChatMessages] Default prompt button clicked:',
        currentPrompt
      );
      AppStateService.getState().chatContainer?.chatWidget.inputManager.setInputValue(
        currentPrompt
      );
      AppStateService.getState().chatContainer?.chatWidget.inputManager.sendMessage();
      this.hidePromptButtons();
      this.hideWaitingReplyBox();
    });

    this.promptButtons.push(defaultButton);
    buttonsContainer.appendChild(defaultButton);

    this.waitingReplyBox.appendChild(buttonsContainer);

    // Create the continue button (initially hidden)
    this.continueButton = document.createElement('button');
    this.continueButton.className = 'sage-ai-continue-button hidden';
    this.continueButton.textContent = 'Continue';

    this.continueButton.addEventListener('click', () => {
      console.log('[ChatMessages] Continue button clicked');

      console.log('[ChatMessages] Calling continue callback');
      AppStateService.getState().chatContainer?.chatWidget.inputManager.setInputValue(
        'Continue'
      );
      AppStateService.getState().chatContainer?.chatWidget.inputManager.sendMessage();
      this.hideContinueButton();
      this.hideWaitingReplyBox();
    });

    this.waitingReplyBox.appendChild(this.continueButton);

    // Initially hide the entire waiting reply box
    this.waitingReplyBox.classList.remove('visible');

    // Add to the end of the container (bottom of chat history)
    this.container.appendChild(this.waitingReplyBox);
    console.log('[ChatMessages] Waiting reply box added to container');

    // Do NOT automatically check and show the continue button here
    // It should only be shown when explicitly called via showWaitingReplyBox() or on startup
  }

  /**
   * Remove the continue button and waiting reply box
   */
  public removeContinueButton(): void {
    console.log('[ChatMessages] removeContinueButton() called');
    if (this.waitingReplyBox) {
      this.waitingReplyBox.remove();
      this.waitingReplyBox = null;
      this.continueButton = null;
      this.promptButtons = [];
      console.log('[ChatMessages] Continue button removed');
    }
  }

  /**
   * Show the prompt buttons
   */
  private showPromptButtons(): void {
    console.log('[ChatMessages] showPromptButtons() called');
    this.promptButtons.forEach((button, index) => {
      if (button) {
        console.log(
          `[ChatMessages] Setting prompt button ${index + 1} display to block`
        );
        button.style.display = 'block';
      } else {
        console.warn(
          `[ChatMessages] promptButton ${index + 1} is null in showPromptButtons()`
        );
      }
    });
  }

  /**
   * Hide the prompt buttons
   */
  private hidePromptButtons(): void {
    console.log('[ChatMessages] hidePromptButtons() called');
    this.promptButtons.forEach((button, index) => {
      if (button) {
        console.log(
          `[ChatMessages] Setting prompt button ${index + 1} display to none`
        );
        button.style.display = 'none';
      } else {
        console.warn(
          `[ChatMessages] promptButton ${index + 1} is null in hidePromptButtons()`
        );
      }
    });
  }

  /**
   * Update the prompt buttons with new recommended prompts
   * @param recommendedPrompts List of recommended prompts to display
   */
  private updatePromptButtons(recommendedPrompts: string[]): void {
    console.log(
      '[ChatMessages] updatePromptButtons() called with prompts:',
      recommendedPrompts
    );

    // Find the buttons container
    const buttonsContainer = this.waitingReplyBox?.querySelector(
      '.sage-ai-prompt-buttons-container'
    );
    if (!buttonsContainer) {
      console.warn('[ChatMessages] No buttons container found');
      return;
    }

    // Remove all existing prompt buttons
    this.promptButtons.forEach(button => {
      if (button && button.parentNode) {
        button.parentNode.removeChild(button);
      }
    });
    this.promptButtons = [];

    // Create new buttons for each recommended prompt
    recommendedPrompts.forEach((prompt, index) => {
      const button = document.createElement('button');
      button.className = 'sage-ai-prompt-button';
      button.textContent = prompt;
      button.style.display = 'block';

      button.addEventListener('click', () => {
        const currentPrompt = button.textContent || '';
        console.log(
          `[ChatMessages] Prompt button ${index + 1} clicked:`,
          currentPrompt
        );
        AppStateService.getState().chatContainer?.chatWidget.inputManager.setInputValue(
          currentPrompt
        );
        AppStateService.getState().chatContainer?.chatWidget.inputManager.sendMessage();
        this.hidePromptButtons();
        this.hideWaitingReplyBox();
      });

      this.promptButtons.push(button);
      buttonsContainer.appendChild(button);

      console.log(
        `[ChatMessages] Created new prompt button ${index + 1}: "${prompt}"`
      );
    });
  }

  /**
   * Show the waiting reply box (and potentially the continue button)
   * This is called when the wait_user_reply tool is used
   * @param recommendedPrompts Optional list of recommended prompts to show instead of default ones
   */
  public showWaitingReplyBox(recommendedPrompts?: string[]): void {
    console.log('[ChatMessages] showWaitingReplyBox() called');
    if (this.waitingReplyBox) {
      console.log('[ChatMessages] Adding visible class to waiting reply box');
      this.displayWaitingReplyBox();

      // Update prompt buttons with recommended prompts if provided, otherwise use default
      if (recommendedPrompts && recommendedPrompts.length > 0) {
        this.updatePromptButtons(recommendedPrompts);
      } else {
        // Show the default "Continue" button
        this.showPromptButtons();
      }

      // Ensure the waiting reply box is positioned as the last child
      this.ensureWaitingReplyBoxIsLast();

      // When explicitly called (from wait_user_reply tool), always show the prompt buttons
      this.checkAndShowPromptButtons();

      // Scroll to bottom to show the waiting reply box
      this.handleScroll();
    } else {
      console.warn(
        '[ChatMessages] waitingReplyBox is null in showWaitingReplyBox()'
      );
    }
  }

  private displayWaitingReplyBox(): void {
    console.log('[ChatMessages] displayWaitingReplyBox() called');
    if (this.waitingReplyBox) {
      this.waitingReplyBox.classList.add('visible');
    }

    if (this.waitingReplyBox && !this.waitingReplyBox.parentElement) {
      console.log('[ChatMessages] Adding waiting reply box to container');
      this.container.appendChild(this.waitingReplyBox);
    }
  }

  /**
   * Hide the waiting reply box
   */
  public hideWaitingReplyBox(): void {
    console.log('[ChatMessages] hideWaitingReplyBox() called');
    if (this.waitingReplyBox) {
      this.waitingReplyBox.classList.remove('visible');
    }
  }

  /**
   * Set the callback function to be called when the continue button is clicked
   */
  public setContinueCallback(callback: () => void): void {
    console.log('[ChatMessages] Setting continue callback');
    this.onContinueCallback = callback;
  }

  /**
   * Recalculate and update continue button visibility based on current message state
   * This should be called after messages are added or the conversation state changes
   */
  public updateContinueButtonVisibility(): void {
    console.log('[ChatMessages] updateContinueButtonVisibility() called');

    if (!this.waitingReplyBox || !this.continueButton) {
      console.log(
        '[ChatMessages] No waiting reply box or continue button, creating...'
      );
      this.addContinueButton();
      return;
    }

    // Ensure the waiting reply box is at the end of the container
    this.ensureWaitingReplyBoxIsLast();

    // Only check continue button visibility for startup case, don't auto-show waiting box
    this.checkAndShowContinueButtonOnStartup();
  }

  /**
   * Check if we should show the prompt buttons based on thread state and message history
   * This version is only used when wait_user_reply tool is called
   */
  private checkAndShowPromptButtons(): void {
    console.log('[ChatMessages] checkAndShowPromptButtons() called');

    if (!DiffStateService.getInstance().getCurrentState().allDiffsResolved) {
      console.warn(
        '[ChatMessages] Diffs not resolved, skipping prompt buttons'
      );
      this.hideWaitingReplyBox();
      return;
    }

    // Get the current thread from chat history manager
    const currentThread = this.historyManager.getCurrentThread();
    console.log('[ChatMessages] currentThread:', currentThread);
    if (!currentThread || currentThread.messages.length <= 1) {
      console.warn('[ChatMessages] No currentThread found');
      return;
    }

    console.log(
      '[ChatMessages] continueButtonShown status:',
      currentThread.continueButtonShown
    );
    console.log(
      '[ChatMessages] Message history length:',
      this.messageHistory.length
    );

    // When called from wait_user_reply tool, always show the prompt buttons
    console.log(
      '[ChatMessages] wait_user_reply tool called, showing prompt buttons'
    );
    this.showPromptButtons();
    this.hideContinueButton(); // Hide continue button when showing prompt buttons

    // Make sure the waiting reply box is visible
    if (this.waitingReplyBox) {
      this.displayWaitingReplyBox();
    }

    // Mark that continue button has been shown for this thread
    if (!currentThread.continueButtonShown) {
      currentThread.continueButtonShown = true;
      // Update the thread in storage
      this.historyManager.updateCurrentThreadMessages(
        currentThread.messages,
        currentThread.contexts
      );
    }
  }

  /**
   * Check if we should show the continue button on startup based on message history
   * This is only used during initialization/startup scenarios
   */
  private checkAndShowContinueButtonOnStartup(): void {
    console.log('[ChatMessages] checkAndShowContinueButtonOnStartup() called');

    // Get the current thread from chat history manager
    const currentThread = this.historyManager.getCurrentThread();
    console.log('[ChatMessages] currentThread:', currentThread);
    if (!currentThread) {
      console.warn('[ChatMessages] No currentThread found');
      return;
    }

    console.log(
      '[ChatMessages] continueButtonShown status:',
      currentThread.continueButtonShown
    );
    console.log(
      '[ChatMessages] Message history length:',
      this.messageHistory.length
    );

    // Check if this is an appropriate time to show the continue button based on heuristics
    const shouldShow = this.shouldShowContinueButton();
    console.log('[ChatMessages] shouldShowContinueButton result:', shouldShow);

    if (shouldShow) {
      console.log(
        '[ChatMessages] Startup conditions met, showing continue button'
      );
      this.showContinueButton();

      // Make sure the waiting reply box is visible
      if (this.waitingReplyBox) {
        this.displayWaitingReplyBox();
      }

      // Mark that continue button has been shown for this thread
      if (!currentThread.continueButtonShown) {
        currentThread.continueButtonShown = true;
        // Update the thread in storage
        this.historyManager.updateCurrentThreadMessages(
          currentThread.messages,
          currentThread.contexts
        );
      }
    } else {
      console.log('[ChatMessages] Startup continue button conditions not met');
    }
  }

  /**
   * Determine if the continue button should be shown based on message history
   */
  private shouldShowContinueButton(): boolean {
    console.log('[ChatMessages] shouldShowContinueButton() called');

    // Show continue button if there are messages and the conversation seems to be waiting for user input
    if (this.messageHistory.length === 0) {
      console.log(
        '[ChatMessages] No messages in history, not showing continue button'
      );
      return false;
    }

    // Check for recent wait_user_reply tool calls
    const recentMessages = this.messageHistory.slice(-3); // Check last 3 messages
    const hasWaitUserReplyTool = recentMessages.some(msg => {
      if (msg.role === 'assistant' && Array.isArray(msg.content)) {
        return msg.content.some((content: any) => {
          return (
            content.type === 'tool_use' &&
            content.name === 'notebook-wait_user_reply'
          );
        });
      }
      return false;
    });

    if (hasWaitUserReplyTool) {
      console.log(
        '[ChatMessages] Found wait_user_reply tool call, showing continue button'
      );
      return true;
    }

    // Find the last assistant message (excluding tool results and system messages)
    const lastAssistantMessage = this.messageHistory
      .slice()
      .reverse()
      .find(msg => {
        if (msg.role !== 'assistant') return false;

        // Skip tool calls and system messages
        if (Array.isArray(msg.content)) {
          return msg.content.some(
            (content: any) =>
              content.type === 'text' &&
              content.text &&
              content.text.trim().length > 0
          );
        }

        return typeof msg.content === 'string' && msg.content.trim().length > 0;
      });

    if (!lastAssistantMessage) {
      console.log(
        '[ChatMessages] No valid assistant message found, not showing continue button'
      );
      return false;
    }

    // Extract text content from the message
    let content = '';
    if (typeof lastAssistantMessage.content === 'string') {
      content = lastAssistantMessage.content;
    } else if (Array.isArray(lastAssistantMessage.content)) {
      const textContent = lastAssistantMessage.content.find(
        (c: any) => c.type === 'text'
      );
      content = textContent?.text || '';
    }

    console.log(
      '[ChatMessages] Analyzing last assistant message:',
      content.substring(0, 200) + '...'
    );

    // Check if the assistant's last message suggests it's waiting for user input
    const waitingIndicators = [
      'waiting for',
      'wait for',
      'after you reply',
      'when you reply',
      'let me know',
      'please',
      'would you like',
      'do you want',
      'shall i',
      'should i',
      'feel free to',
      'if you need',
      'any questions',
      'anything else',
      'next steps',
      'proceed with',
      'continue with',
      'go ahead',
      'move forward'
    ];

    const hasWaitingIndicator = waitingIndicators.some(indicator =>
      content.toLowerCase().includes(indicator.toLowerCase())
    );

    // Also check if the message ends with a question mark or asks for input
    const endsWithQuestion = content.trim().endsWith('?');

    // Check if it's a question or confirmation request
    const questionWords = [
      'what',
      'how',
      'when',
      'where',
      'why',
      'which',
      'who',
      'should',
      'would',
      'could',
      'can',
      'do you',
      'are you'
    ];
    const startsWithQuestion = questionWords.some(word =>
      content.toLowerCase().trim().startsWith(word.toLowerCase())
    );

    const result =
      hasWaitingIndicator || endsWithQuestion || startsWithQuestion;
    console.log(
      '[ChatMessages] Continue button analysis - waitingIndicator:',
      hasWaitingIndicator,
      'endsWithQuestion:',
      endsWithQuestion,
      'startsWithQuestion:',
      startsWithQuestion,
      'result:',
      result
    );

    // Show continue button if there are waiting indicators, it's a question, or asks for confirmation
    return result;
  }

  /**
   * Show the continue button
   */
  private showContinueButton(): void {
    console.log('[ChatMessages] showContinueButton() called');
    if (this.continueButton) {
      console.log('[ChatMessages] Removing hidden class from continue button');
      this.continueButton.classList.remove('hidden');
    } else {
      console.warn(
        '[ChatMessages] continueButton is null in showContinueButton()'
      );
    }
  }

  /**
   * Hide the continue button
   */
  private hideContinueButton(): void {
    console.log('[ChatMessages] hideContinueButton() called');
    if (this.continueButton) {
      console.log('[ChatMessages] Adding hidden class to continue button');
      this.continueButton.classList.add('hidden');
    } else {
      console.warn(
        '[ChatMessages] continueButton is null in hideContinueButton()'
      );
    }
  }

  /**
   * Add a streaming AI message container to the chat history
   * @returns The container element to be updated with streaming content
   */
  addStreamingAIMessage(): HTMLDivElement {
    this.closeToolGroupIfOpen();

    console.log('[ChatMessages] Adding streaming AI message container');
    const messageElement = document.createElement('div');
    messageElement.className =
      'sage-ai-message sage-ai-ai-message sage-ai-streaming-message';

    // Create header element
    const headerElement = document.createElement('div');
    headerElement.className = 'sage-ai-message-header';

    // Create header image element
    const headerImageElement = document.createElement('div');
    headerImageElement.className = 'sage-ai-message-header-image';
    headerImageElement.innerHTML = `<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M6.6243 10.3334C6.56478 10.1026 6.44453 9.89209 6.27605 9.72361C6.10757 9.55513 5.89702 9.43488 5.6663 9.37536L1.5763 8.32069C1.50652 8.30089 1.44511 8.25886 1.40138 8.20099C1.35765 8.14312 1.33398 8.07256 1.33398 8.00002C1.33398 7.92749 1.35765 7.85693 1.40138 7.79906C1.44511 7.74119 1.50652 7.69916 1.5763 7.67936L5.6663 6.62402C5.89693 6.56456 6.10743 6.44441 6.2759 6.27605C6.44438 6.10769 6.56468 5.89728 6.6243 5.66669L7.67897 1.57669C7.69857 1.50664 7.74056 1.44492 7.79851 1.40095C7.85647 1.35699 7.92722 1.33319 7.99997 1.33319C8.07271 1.33319 8.14346 1.35699 8.20142 1.40095C8.25938 1.44492 8.30136 1.50664 8.32097 1.57669L9.37497 5.66669C9.43449 5.89741 9.55474 6.10796 9.72322 6.27644C9.8917 6.44492 10.1023 6.56517 10.333 6.62469L14.423 7.67869C14.4933 7.69809 14.5553 7.74003 14.5995 7.79808C14.6437 7.85612 14.6677 7.92706 14.6677 8.00002C14.6677 8.07298 14.6437 8.14393 14.5995 8.20197C14.5553 8.26002 14.4933 8.30196 14.423 8.32136L10.333 9.37536C10.1023 9.43488 9.8917 9.55513 9.72322 9.72361C9.55474 9.89209 9.43449 10.1026 9.37497 10.3334L8.3203 14.4234C8.3007 14.4934 8.25871 14.5551 8.20075 14.5991C8.1428 14.6431 8.07205 14.6669 7.9993 14.6669C7.92656 14.6669 7.85581 14.6431 7.79785 14.5991C7.73989 14.5551 7.69791 14.4934 7.6783 14.4234L6.6243 10.3334Z" fill="url(#paint0_linear_445_6567)"/>
      <path d="M13.333 2V4.66667" stroke="url(#paint1_linear_445_6567)" stroke-width="0.984615" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M14.6667 3.33331H12" stroke="url(#paint2_linear_445_6567)" stroke-width="0.984615" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M2.66699 11.3333V12.6666" stroke="url(#paint3_linear_445_6567)" stroke-width="0.984615" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M3.33333 12H2" stroke="url(#paint4_linear_445_6567)" stroke-width="0.984615" stroke-linecap="round" stroke-linejoin="round"/>
      <defs>
      <linearGradient id="paint0_linear_445_6567" x1="1.33398" y1="1.33319" x2="14.6677" y2="14.6669" gradientUnits="userSpaceOnUse">
      <stop stop-color="#FEC163"/>
      <stop offset="1" stop-color="#DE4313"/>
      </linearGradient>
      <linearGradient id="paint1_linear_445_6567" x1="13.333" y1="2" x2="15.0864" y2="2.65753" gradientUnits="userSpaceOnUse">
      <stop stop-color="#FEC163"/>
      <stop offset="1" stop-color="#DE4313"/>
      </linearGradient>
      <linearGradient id="paint2_linear_445_6567" x1="12" y1="3.33331" x2="12.6575" y2="5.08674" gradientUnits="userSpaceOnUse">
      <stop stop-color="#FEC163"/>
      <stop offset="1" stop-color="#DE4313"/>
      </linearGradient>
      <linearGradient id="paint3_linear_445_6567" x1="2.66699" y1="11.3333" x2="3.94699" y2="12.2933" gradientUnits="userSpaceOnUse">
      <stop stop-color="#FEC163"/>
      <stop offset="1" stop-color="#DE4313"/>
      </linearGradient>
      <linearGradient id="paint4_linear_445_6567" x1="2" y1="12" x2="2.96" y2="13.28" gradientUnits="userSpaceOnUse">
      <stop stop-color="#FEC163"/>
      <stop offset="1" stop-color="#DE4313"/>
      </linearGradient>
      </defs>
      </svg>
    `;

    headerElement.append(headerImageElement);

    // Create header title element
    const headerSageTitleElement = document.createElement('span');
    headerSageTitleElement.className = 'sage-ai-message-header-title';
    headerSageTitleElement.innerText = 'Sage AI';

    headerElement.append(headerSageTitleElement);

    if (this.lastAddedMessageType !== 'user') {
      headerElement.style.display = 'none';
    }

    // Create a container to hold the streaming content
    const contentElement = document.createElement('div');
    contentElement.className =
      'sage-ai-message-content sage-ai-streaming-content sage-ai-markdown-content';
    contentElement.setAttribute('data-raw-text', ''); // Store accumulated raw text

    // Assemble the message
    messageElement.appendChild(headerElement);
    messageElement.appendChild(contentElement);

    this.container.appendChild(messageElement);

    this.handleScroll();

    console.log(
      '[ChatMessages] Streaming message container added (not yet in history)'
    );
    return messageElement;
  }

  /**
   * Render a diff approval message from history
   * @param diffApprovalContent The diff approval content from history
   */
  private renderDiffApprovalFromHistory(diffApprovalContent: any): void {
    if (
      diffApprovalContent.diff_cells &&
      diffApprovalContent.diff_cells.length > 0
    ) {
      // Convert stored diff cells to IPendingDiff format
      const diffCells = diffApprovalContent.diff_cells.map((cell: any) => ({
        cellId: cell.cellId,
        type: cell.type,
        originalContent: cell.originalContent || '',
        newContent: cell.newContent || '',
        displaySummary: cell.displaySummary || `${cell.type} cell`,
        notebookId: diffApprovalContent.notebook_path,
        metadata: {}
      }));
      // Use DiffApprovalDialog to render the historical dialog
      const historicalDialog = DiffApprovalDialog.createHistoricalDialog(
        diffCells,
        diffApprovalContent.notebook_path
      );
      this.container.appendChild(historicalDialog);
    }

    this.ensureWaitingReplyBoxIsLast();
    this.handleScroll();
  }

  /**
   * Create a checkpoint for the current user message
   */
  private createCheckpoint(userMessage: string): ICheckpoint {
    try {
      // Set the current notebook ID in checkpoint manager
      const currentNotebookId = AppStateService.getCurrentNotebookId();
      if (!currentNotebookId) {
        throw new Error(
          'No current notebook ID available for checkpoint creation'
        );
      }
      this.checkpointManager.setCurrentNotebookId(currentNotebookId);

      // Get ActionHistory from ConversationService
      const conversationService =
        AppStateService.getState().chatContainer?.chatWidget
          .conversationService;
      const actionHistory = conversationService?.actionHistory;

      const checkpoint = this.checkpointManager.createCheckpoint(
        userMessage,
        this.messageHistory,
        this.mentionContexts,
        actionHistory
      );

      return checkpoint;
    } catch (error) {
      console.error('[ChatMessages] Error creating checkpoint:', error);
      throw error;
    }
  }

  /**
   * Handle restore checkpoint click
   */
  private handleRestoreCheckpoint(checkpoint: ICheckpoint): void {
    console.log('[ChatMessages] Restore checkpoint clicked:', checkpoint);

    // Show restoration modal
    this.restorationModal.show(
      checkpoint,
      (option: CheckpointRestorationOption) => {
        void this.performCheckpointRestoration(checkpoint, option);
      },
      () => {
        console.log('[ChatMessages] Checkpoint restoration cancelled');
      }
    );
  }

  /**
   * Perform checkpoint restoration
   */
  private async performCheckpointRestoration(
    checkpoint: ICheckpoint,
    option: CheckpointRestorationOption
  ): Promise<void> {
    try {
      console.log('[ChatMessages] Performing checkpoint restoration:', option);

      if (option === CheckpointRestorationOption.CANCEL) {
        return;
      }

      // Set the input value to the checkpoint message for editing
      const inputManager =
        AppStateService.getState().chatContainer?.chatWidget.inputManager;
      if (inputManager) {
        inputManager.setInputValue(checkpoint.userMessage);
      }

      AppStateService.getState().chatContainer?.chatWidget.cancelMessage();

      // Clear all diffs
      DiffStateService.getInstance().clearAllDiffs(
        AppStateService.getCurrentNotebookId()
      );

      // Use ConversationService to handle the restoration (including ActionHistory)
      const conversationService =
        AppStateService.getState().chatContainer?.chatWidget
          .conversationService;
      if (conversationService) {
        await conversationService.restoreToCheckpoint(checkpoint, option);
      } else {
        console.warn(
          '[ChatMessages] No ConversationService available for checkpoint restoration'
        );
        return;
      }

      // Clear checkpoints after this one
      this.checkpointManager.clearCheckpointsAfter(checkpoint.id);

      console.log('[ChatMessages] Checkpoint restoration completed');
    } catch (error) {
      console.error(
        '[ChatMessages] Error during checkpoint restoration:',
        error
      );
      this.addErrorMessage('Failed to restore checkpoint. Please try again.');
    }
  }

  /**
   * Restore to checkpoint (called by ConversationService)
   */
  public async restoreToCheckpoint(checkpoint: ICheckpoint): Promise<void> {
    console.log('[ChatMessages] Restoring to checkpoint:', checkpoint.id);

    // Restore message history to checkpoint point
    this.messageHistory = [...checkpoint.messageHistory];
    this.userMessages = this.messageHistory.filter(msg => msg.role === 'user');

    // Restore contexts
    this.mentionContexts = new Map(checkpoint.contexts);
    this.contextService.setContextItems(this.mentionContexts);

    // Restore notebook state
    await NotebookCellStateService.cacheNotebookState(
      checkpoint.notebookId,
      checkpoint.notebookState
    );

    // Update persistent storage
    this.historyManager.updateCurrentThreadMessages(
      this.messageHistory,
      this.mentionContexts
    );

    // Remove all elements after the checkpoint, including the checkpoint element itself
    const checkpointElement = this.container.querySelector(
      `[data-checkpoint-id="${checkpoint.id}"]`
    );
    if (checkpointElement) {
      let current = checkpointElement.nextSibling;
      while (current) {
        const next = current.nextSibling;
        this.container.removeChild(current);
        current = next;
      }
      this.container.removeChild(checkpointElement);
    }

    console.log('[ChatMessages] Message history and contexts restored');
  }
}

/**
 * Check if the tool result is a stringified array with at least 1 { error: true } object
 * If so, returns a normalized string joining the errorText
 * This is the result of a run_cell tool call
 *
 * Returns false otherwise
 */
function getResultError(result: unknown): false | string {
  try {
    console.log('[ChatMessages] getResultError() called with result:', result);
    console.log(
      '[ChatMessages] getResultError() called with result:',
      typeof result
    );
    if (typeof result !== 'string') return false;

    const obj = JSON.parse(result as string);

    if (Array.isArray(obj)) {
      const errors = obj.filter(item => item && item?.error === true);
      if (!errors.length) return false;

      return errors.map(item => item.errorText).join('\n');
    } else if (obj && obj?.error === true) {
      return obj.errorText;
    }
  } catch {
    return false;
  }

  return false;
}
