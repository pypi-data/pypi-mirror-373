import { NotebookDiffTools } from '../Notebook/NotebookDiffTools';
import {
  DiffApprovalStatus,
  IDiffApplicationResult,
  IPendingDiff
} from '../types';
import { AppStateService } from '../AppState';
import { diffStateService } from '../Services/DiffStateService';
import { Subscription } from 'rxjs';
// Add CodeMirror imports for merge view
import { EditorView, ViewPlugin } from '@codemirror/view';
import { unifiedMergeView } from 'codemirror-merge-alpinex';
import { EditorState, Extension } from '@codemirror/state';
import { python } from '@codemirror/lang-python';
import { jupyterTheme } from '@jupyterlab/codemirror';
import { REAPPLY_ICON } from './icons';

/**
 * Dialog callbacks interface
 */
interface IDiffApprovalCallbacks {
  onApprove: (trackingIds: string[]) => void;
  onReject: (trackingIds: string[]) => void;
  onApproveAll: (notebookId: string | null) => void;
  onRejectAll: (notebookId: string | null) => void;
  applyApprovedDiffs: (
    notebookId: string | null,
    trackingIds?: string[]
  ) => Promise<IDiffApplicationResult>;
  handleRejectedDiffs: (
    notebookId: string | null
  ) => Promise<IDiffApplicationResult>;
  setExecuteApprovedCells: (execute: boolean) => void; // Add new callback
  reapplyDiff: (diffCell: IPendingDiff) => void;
}

/**
 * A dialog for approving/rejecting cell diffs
 */
export class DiffApprovalDialog {
  private dialogElement: HTMLElement | null = null;
  private parentElement: HTMLElement | null = null;
  private callbacks: IDiffApprovalCallbacks | null = null;
  private diffCells: IPendingDiff[] = [];
  private resolvePromise:
    | ((value: { approved: boolean; runImmediately: boolean }) => void)
    | null = null;
  private embedded: boolean = false;
  private isRunContext: boolean = false;
  private currentNotebookPath: string | null = null;
  private cellButtonElements: Map<
    string,
    {
      approveButton: HTMLElement;
      rejectButton: HTMLElement;
      runButton: HTMLElement;
      hoverButtons: HTMLElement;
      reapplyButton: HTMLElement;
      cellItem: HTMLElement;
    }
  > = new Map();
  private subscriptions: Subscription[] = [];

  /**
   * Set callbacks for the dialog actions
   */
  public setCallbacks(callbacks: IDiffApprovalCallbacks): void {
    this.callbacks = callbacks;
  }

  public updateNotebookPath(newPath: string): void {
    this.currentNotebookPath = newPath;
  }

  /**
   * Show the approval dialog
   * @param parentElement The parent element to attach the dialog to
   * @param notebookPath Path of the current notebook for filtering diffs
   * @param embedded Whether to use embedded styling for chat context
   * @param isRunContext Whether this approval is in the context of running code
   * @returns Promise that resolves when approvals are complete with status and run flag
   */
  public async showDialog(
    parentElement: HTMLElement,
    notebookPath: string | null = null,
    embedded: boolean = false,
    isRunContext: boolean = false
  ): Promise<{ approved: boolean; runImmediately: boolean }> {
    // Get diffs directly from DiffStateService
    const currentState = diffStateService.getCurrentState();
    const allDiffs = Array.from(currentState.pendingDiffs.values());

    // Filter diffs for the current notebook and add display summary
    this.diffCells = allDiffs
      .filter(diff => !notebookPath || diff.notebookId === notebookPath)
      .map(diff => ({
        ...diff,
        displaySummary:
          diff.summary || diff.metadata?.summary || `${diff.type} cell`
      }));

    this.parentElement = parentElement;
    this.embedded = embedded;
    this.isRunContext = isRunContext;
    this.currentNotebookPath = notebookPath;

    // Subscribe to diff state changes
    this.setupDiffStateSubscriptions();

    // Create dialog element
    this.createDialog();

    // Add dialog to chat history for persistence
    this.addToChatHistory();

    const llmStateDisplay =
      AppStateService.getChatContainerSafe()?.chatWidget.llmStateDisplay;
    if (llmStateDisplay) {
      llmStateDisplay.showPendingDiffs(notebookPath, isRunContext);
    }

    // Also show diffs in DiffNavigationWidget for synchronized display
    const diffNavigationWidget = AppStateService.getDiffNavigationWidgetSafe();
    if (diffNavigationWidget) {
      diffNavigationWidget.showPendingDiffs(notebookPath, isRunContext);
    }

    // Return a promise that will be resolved when the dialog is completed
    return new Promise<{ approved: boolean; runImmediately: boolean }>(
      resolve => {
        this.resolvePromise = resolve;
      }
    );
  }

  public isDialogOpen(): boolean {
    return this.dialogElement !== null;
  }

  /**
   * Create the dialog UI
   */
  private createDialog(): void {
    if (!this.parentElement) {
      console.error('Parent element not provided for diff approval dialog');
      return;
    }

    // Create the dialog container with appropriate class
    this.dialogElement = document.createElement('div');
    this.dialogElement.className = this.embedded
      ? 'sage-ai-diff-approval-dialog-embedded'
      : 'sage-ai-diff-approval-dialog';

    // Add description
    const description = document.createElement('p');
    const notebookLabel = this.currentNotebookPath
      ? ` in notebook "${this.currentNotebookPath.split('/').pop()}"`
      : '';
    description.textContent = `Review and approve/reject the following changes${notebookLabel}:`;
    if (this.embedded) {
      description.className = 'sage-ai-diff-summary';
    }

    // Create the list of diff cells
    const diffList = document.createElement('div');
    diffList.className = 'sage-ai-diff-list';

    // Add each diff cell to the list
    this.diffCells.forEach(diffCell => {
      const cellItem = this.createDiffCellItem(diffCell);
      diffList.appendChild(cellItem);
    });

    this.dialogElement.appendChild(diffList);

    // Create bottom action buttons
    const actionButtons = document.createElement('div');
    actionButtons.className = this.embedded
      ? 'sage-ai-inline-diff-actions'
      : 'sage-ai-diff-approval-actions';

    // Reject all button
    const rejectAllButton = document.createElement('button');
    rejectAllButton.className = 'sage-ai-reject-button';
    rejectAllButton.textContent = 'Reject All';
    rejectAllButton.onclick = () => this.rejectAll();

    // Approve all button - change text if in run context
    const approveAllButton = document.createElement('button');
    approveAllButton.className = 'sage-ai-confirm-button';
    approveAllButton.textContent = this.isRunContext
      ? 'Approve All and Run'
      : 'Approve All';
    approveAllButton.onclick = () => this.approveAll();

    actionButtons.appendChild(rejectAllButton);
    actionButtons.appendChild(approveAllButton);

    this.dialogElement.appendChild(actionButtons);

    // Add the dialog to the parent element
    this.parentElement.appendChild(this.dialogElement);

    AppStateService.getChatContainerSafe()
      ?.chatWidget?.getMessageComponent()
      .handleScroll();
  }

  /**
   * Add the dialog to chat history for persistence
   */
  private addToChatHistory(): void {
    // Get the chat messages component from AppStateService
    const chatContainer = AppStateService.getChatContainerSafe();
    if (chatContainer?.chatWidget) {
      chatContainer.chatWidget.getMessageComponent().addDiffApprovalDialog(
        this.currentNotebookPath || undefined,
        this.diffCells // Pass the actual diff data
      );

      console.log('[DiffApprovalDialog] Added to chat history for persistence');
    } else {
      console.warn(
        '[DiffApprovalDialog] Could not add to chat history - chat components not available'
      );
    }
  }

  /**
   * Create a historical diff approval dialog for chat display
   * This renders the same diff content but without interactive buttons
   */
  public static createHistoricalDialog(
    diffCells: IPendingDiff[],
    notebookPath?: string
  ): HTMLElement {
    const dialog = new DiffApprovalDialog();
    const diffManager = AppStateService.getNotebookDiffManager();
    const callbacks = diffManager.diffApprovalDialog.callbacks;
    if (callbacks) {
      dialog.setCallbacks(callbacks);
    }

    dialog.diffCells = diffCells;
    dialog.currentNotebookPath = notebookPath || null;
    dialog.embedded = true; // Use embedded styling for chat
    dialog.isRunContext = false;

    // Create the dialog element for historical display
    const dialogElement = document.createElement('div');
    dialogElement.className =
      'sage-ai-diff-approval-dialog-embedded sage-ai-diff-approval-historical';

    // Create the list of diff cells
    const diffList = document.createElement('div');
    diffList.className = 'sage-ai-diff-list';

    // Add each diff cell to the list
    dialog.diffCells.forEach(diffCell => {
      const cellItem = dialog.createDiffCellItem(diffCell, true); // Pass true for historical mode
      diffList.appendChild(cellItem);
    });

    dialogElement.appendChild(diffList);

    return dialogElement;
  }

  /**
   * Create a diff cell item for the dialog
   */
  private createDiffCellItem(
    diffCell: IPendingDiff,
    historical: boolean = false
  ): HTMLElement {
    const cellItem = document.createElement('div');
    cellItem.className = 'sage-ai-diff-cell-item';
    cellItem.dataset.cellId = diffCell.cellId; // Store tracking ID in data attribute

    // Create header with summary and type
    const cellHeader = document.createElement('div');
    cellHeader.className = 'sage-ai-diff-cell-header';

    const diffContentCollapseIcon = document.createElement('span');
    diffContentCollapseIcon.className = 'sage-ai-diff-content-collapse-icon';
    diffContentCollapseIcon.innerHTML = COLLAPSE_ICON;
    diffContentCollapseIcon.onclick = () =>
      (diffContent.style.display =
        diffContent.style.display === 'none' ? 'block' : 'none');
    cellHeader.appendChild(diffContentCollapseIcon);

    const cellIdLabel = document.createElement('span');
    cellIdLabel.className = 'sage-ai-diff-cell-id-label';
    cellIdLabel.textContent = diffCell.cellId;
    cellIdLabel.onclick = () =>
      AppStateService.getNotebookTools().scrollToCellById(diffCell.cellId);
    cellHeader.appendChild(cellIdLabel);

    cellItem.appendChild(cellHeader);

    // Create diff content display with collapse/expand functionality
    const diffContent = document.createElement('div');
    diffContent.className = 'sage-ai-diff-content';
    diffContent.title = 'Click to expand/collapse diff content';

    // Create CodeMirror merge view instead of HTML diff
    this.createMergeViewInContainer(
      diffContent,
      diffCell.originalContent || '',
      diffCell.newContent || ''
    );

    const normalLines =
      diffContent.querySelector('.cm-content')?.children.length || 0;
    const deletedLines =
      diffContent.querySelectorAll('.cm-deletedLine').length || 0;
    const isCompressable = normalLines + deletedLines > 9;
    const hasCollapsed = diffContent.querySelector('.cm-collapsedLines');
    const isContentClickable = isCompressable || hasCollapsed;
    if (isContentClickable) {
      diffContent.style.cursor = 'pointer';

      // Create gradient overlay that stays at bottom when scrolling
      const gradientOverlay = document.createElement('div');
      gradientOverlay.className = 'sage-ai-diff-gradient-overlay';

      if (hasCollapsed && !isCompressable) {
        gradientOverlay.style.display = 'none';
        diffContent.classList.add('sage-ai-diff-expanded');
      }

      const arrowDownIcon =
        '<svg width="14px" height="14px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M5.70711 9.71069C5.31658 10.1012 5.31658 10.7344 5.70711 11.1249L10.5993 16.0123C11.3805 16.7927 12.6463 16.7924 13.4271 16.0117L18.3174 11.1213C18.708 10.7308 18.708 10.0976 18.3174 9.70708C17.9269 9.31655 17.2937 9.31655 16.9032 9.70708L12.7176 13.8927C12.3271 14.2833 11.6939 14.2832 11.3034 13.8927L7.12132 9.71069C6.7308 9.32016 6.09763 9.32016 5.70711 9.71069Z" fill="#999999"></path> </g></svg>';
      gradientOverlay.innerHTML = arrowDownIcon;

      // Add scroll event listener to hide gradient when near bottom
      diffContent.addEventListener('scroll', () => {
        const scrollTop = diffContent.scrollTop;
        const scrollHeight = diffContent.scrollHeight;
        const clientHeight = diffContent.clientHeight;
        const distanceFromBottom = scrollHeight - scrollTop - clientHeight;

        if (distanceFromBottom <= 20) {
          gradientOverlay.style.display = 'none';
        } else {
          gradientOverlay.style.display = 'block';
        }
      });

      let collapsedState = !!hasCollapsed;

      let isCollapsedLinesClicked = false;

      // Add click handler to the entire diff content area
      diffContent.onclick = () => {
        if (isCollapsedLinesClicked) return;

        if (hasCollapsed) {
          const collapsedLines =
            diffContent.querySelectorAll<HTMLElement>('.cm-collapsedLines');
          collapsedLines.forEach(line => {
            // Because we call line.click(), the diff content will be called again
            // It grant that this callback will be executed only once
            isCollapsedLinesClicked = true;
            line.click();
            isCollapsedLinesClicked = false;
          });

          // It means the user clicked the collapsed lines, so we don't need to do anything
          if (collapsedState) {
            // It should happen only once, that's why we set to false
            collapsedState = false;

            diffContent.classList.add('sage-ai-diff-expanded');
            gradientOverlay.style.display = 'none';

            return;
          }
        }

        const isExpanded = diffContent.classList.contains(
          'sage-ai-diff-expanded'
        );

        if (isExpanded) {
          diffContent.classList.remove('sage-ai-diff-expanded');
          diffContent.title = 'Click to expand diff content';
          gradientOverlay.style.display = 'flex';
        } else {
          diffContent.classList.add('sage-ai-diff-expanded');
          diffContent.title = 'Click to collapse diff content';
          gradientOverlay.style.display = 'none';
        }
      };

      // Append the gradient overlay to the diff content
      diffContent.appendChild(gradientOverlay);
    }

    cellItem.appendChild(diffContent);

    const hoverButtons = document.createElement('div');
    hoverButtons.className = 'sage-ai-diff-hover-buttons';

    const reapplyButton = this.createReapplyButton(diffCell, historical);

    if (!historical) {
      // Create approve button
      const approveButton = document.createElement('button');
      approveButton.className = 'sage-ai-diff-approve-button';
      approveButton.innerHTML = `<svg width="15" height="16" viewBox="0 0 15 16" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12.5 4.25L5.625 11.125L2.5 8" stroke="#22C55E" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`;
      approveButton.title = 'Approve this change';

      // Create reject button
      const rejectButton = document.createElement('button');
      rejectButton.className = 'sage-ai-diff-reject-button';
      rejectButton.innerHTML = `<svg width="15" height="16" viewBox="0 0 15 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M11.25 4.25L3.75 11.75M3.75 4.25L11.25 11.75" stroke="#FF2323" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`;
      rejectButton.title = 'Reject this change';

      // Create run button
      const runButton = document.createElement('button');
      runButton.className = 'sage-ai-diff-run-button';
      runButton.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none">
  <path d="M4 2.91583C4 2.52025 4.43762 2.28133 4.77038 2.49524L12.6791 7.57941C12.9852 7.77623 12.9852 8.22377 12.6791 8.42059L4.77038 13.5048C4.43762 13.7187 4 13.4798 4 13.0842V2.91583Z" fill="#3B82F6" stroke="#3B82F6" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M13.1018 5.35787L6.45639 9.55022L5.34214 7.88071" stroke="#1A1A1A" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>`;
      runButton.title = 'Apply this change and run the cell immediately';

      // Add click handlers
      approveButton.onclick = e => {
        e.stopPropagation();
        this.approveCell(diffCell.cellId);
      };

      rejectButton.onclick = e => {
        e.stopPropagation();
        this.rejectCell(diffCell.cellId);
      };

      runButton.onclick = e => {
        e.stopPropagation();
        this.runCell(diffCell.cellId);
      };

      hoverButtons.appendChild(rejectButton);
      hoverButtons.appendChild(approveButton);
      hoverButtons.appendChild(runButton);

      // Store button references for styling updates
      this.cellButtonElements.set(diffCell.cellId, {
        approveButton,
        rejectButton,
        runButton,
        reapplyButton,
        hoverButtons,
        cellItem
      });

      // Set relative positioning for the cell item to contain absolute positioned elements
      cellItem.style.position = 'relative';
    }

    cellHeader.appendChild(hoverButtons);
    hoverButtons.appendChild(reapplyButton);

    return cellItem;
  }

  private createReapplyButton(
    diffCell: IPendingDiff,
    isHistorical: boolean = false
  ): HTMLElement {
    const reapplyButton = document.createElement('button');
    reapplyButton.className = 'sage-ai-diff-reapply-button';
    reapplyButton.innerHTML = REAPPLY_ICON.svgstr;
    reapplyButton.title = 'Reapply this change';

    reapplyButton.onclick = () => {
      this.callbacks?.reapplyDiff(diffCell);
    };

    if (!isHistorical || diffCell.type !== 'edit') {
      reapplyButton.classList.add('hidden');
    }

    return reapplyButton;
  }

  /**
   * Approve a specific cell
   */
  public approveCell(trackingId: string): void {
    if (this.callbacks) {
      this.callbacks.onApprove([trackingId]);

      // Update the diff state service
      diffStateService.updateDiffState(
        trackingId,
        true,
        this.currentNotebookPath
      );

      this.callbacks.applyApprovedDiffs(this.currentNotebookPath, [trackingId]);
    }
  }

  /**
   * Reject a specific cell
   */
  public rejectCell(trackingId: string): void {
    if (this.callbacks) {
      this.callbacks.onReject([trackingId]);

      // Update the diff state service
      diffStateService.updateDiffState(
        trackingId,
        false,
        this.currentNotebookPath
      );

      this.callbacks.handleRejectedDiffs(this.currentNotebookPath);
    }
  }

  /**
   * Approve all cells
   */
  public async approveAll(): Promise<void> {
    if (this.callbacks) {
      const loadingOverlay = this.showLoadingOverlay('Applying changes...');

      try {
        this.callbacks.onApproveAll(this.currentNotebookPath);

        // Update all diff states in the service
        this.diffCells.forEach(diffCell => {
          diffStateService.updateDiffState(
            diffCell.cellId,
            true,
            this.currentNotebookPath
          );
        });

        // If in run context, set the flag to execute all approved cells
        if (this.isRunContext) {
          this.callbacks.setExecuteApprovedCells(true);
        }

        if (loadingOverlay && this.dialogElement?.contains(loadingOverlay)) {
          this.dialogElement.removeChild(loadingOverlay);
        }

        // Apply the diffs immediately
        await this.callbacks.applyApprovedDiffs(this.currentNotebookPath);

        if (loadingOverlay && this.dialogElement?.contains(loadingOverlay)) {
          this.dialogElement.removeChild(loadingOverlay);
        }
      } catch (error) {
        console.error('Error applying approved diffs:', error);
        this.showError('Failed to apply changes. Please try again.');
      } finally {
        if (loadingOverlay && this.dialogElement?.contains(loadingOverlay)) {
          this.dialogElement.removeChild(loadingOverlay);
        }
      }
    }
  }

  /**
   * Reject all cells
   */
  public async rejectAll(): Promise<void> {
    if (this.callbacks) {
      const loadingOverlay = this.showLoadingOverlay('Rejecting changes...');

      try {
        this.callbacks.onRejectAll(this.currentNotebookPath);

        // Update all diff states in the service
        this.diffCells.forEach(diffCell => {
          diffStateService.updateDiffState(
            diffCell.cellId,
            false,
            this.currentNotebookPath
          );
        });

        // Handle the rejected diffs immediately
        await this.callbacks.handleRejectedDiffs(this.currentNotebookPath);

        if (loadingOverlay && this.dialogElement?.contains(loadingOverlay)) {
          this.dialogElement.removeChild(loadingOverlay);
        }
      } catch (error) {
        console.error('Error handling rejected diffs:', error);
        this.showError('Failed to reject changes. Please try again.');
      } finally {
        if (loadingOverlay && this.dialogElement?.contains(loadingOverlay)) {
          this.dialogElement.removeChild(loadingOverlay);
        }
      }
    }
  }

  /**
   * Display a loading overlay while applying/rejecting diffs
   */
  private showLoadingOverlay(message: string): HTMLElement {
    const overlay = document.createElement('div');
    // overlay.className = 'sage-ai-loading-overlay';
    // overlay.style.position = 'absolute';
    // overlay.style.top = '0';
    // overlay.style.left = '0';
    // overlay.style.width = '100%';
    // overlay.style.height = '100%';
    // overlay.style.backgroundColor = 'rgba(0,0,0,0.7)';
    // overlay.style.display = 'flex';
    // overlay.style.justifyContent = 'center';
    // overlay.style.alignItems = 'center';
    // overlay.style.zIndex = '1000';
    // overlay.style.color = 'white';
    // overlay.style.fontSize = '16px';

    // const content = document.createElement('div');
    // content.textContent = message;
    // overlay.appendChild(content);

    // if (this.dialogElement) {
    //   this.dialogElement.style.position = 'relative';
    //   this.dialogElement.appendChild(overlay);
    // }

    return overlay;
  }

  /**
   * Show an error message in the dialog
   */
  private showError(message: string): void {
    const errorMessage = document.createElement('div');
    errorMessage.className = 'sage-ai-error-message';
    errorMessage.style.color = '#ff4d4f';
    errorMessage.style.padding = '10px';
    errorMessage.style.margin = '10px';
    errorMessage.style.borderRadius = '4px';
    errorMessage.style.backgroundColor = 'rgba(255,77,79,0.1)';
    errorMessage.textContent = message;

    if (this.dialogElement) {
      this.dialogElement.prepend(errorMessage);

      // Remove the error message after 5 seconds
      setTimeout(() => {
        if (errorMessage.parentNode === this.dialogElement) {
          this.dialogElement?.removeChild(errorMessage);
        }
      }, 5000);
    }
  }

  /**
   * Check if all cells have been handled
   */
  private async checkAllCellsStatus(): Promise<void> {
    // Use the diff state service to check status
    const currentState = diffStateService.getCurrentState();

    let isAllDecided = true;
    let hasPendingRunOperations = false;

    this.diffCells.forEach(diffCell => {
      const currentDiff = currentState.pendingDiffs.get(diffCell.cellId);
      if (!currentDiff?.userDecision) {
        isAllDecided = false;
      } else if (currentDiff.userDecision === 'run' && !currentDiff.runResult) {
        // If cell is marked for running but doesn't have run results yet, it's still pending
        hasPendingRunOperations = true;
      }
    });

    if (!isAllDecided) return;

    // Don't close the dialog if there are still pending run operations
    if (hasPendingRunOperations) return;

    // If all cells are approved/rejected and no pending run operations, close the dialog

    console.log(
      'FINISHED PROCESSING ALL DIFFS =================== FINISHED ---- EMITTING'
    );
    console.log(diffStateService.getCurrentState());
    AppStateService.getNotebookDiffManager()._finishedProcessingDiffs.emit(
      DiffApprovalStatus.APPROVED
    );
    this.close();
  }

  /**
   * Close the dialog
   * Made public so it can be called externally
   */
  public async close(): Promise<void> {
    this.dialogElement = null;
    this.cellButtonElements.clear();
  }

  /**
   * Set up RxJS subscriptions for diff state changes
   */
  private setupDiffStateSubscriptions(): void {
    // Clear any existing subscriptions
    this.subscriptions.forEach(sub => sub.unsubscribe());
    this.subscriptions = [];

    // Subscribe to diff state changes for each cell
    this.diffCells.forEach(diffCell => {
      const subscription = diffStateService
        .getCellStateChanges$(diffCell.cellId)
        .subscribe(stateChange => {
          if (stateChange) {
            this.updateCellUI(stateChange.cellId);
          }
        });
      this.subscriptions.push(subscription);
    });

    // Subscribe to general diff state changes to catch runResult updates
    const diffStateSub = diffStateService.diffState$.subscribe(diffState => {
      this.diffCells.forEach(diffCell => {
        const currentDiff = diffState.pendingDiffs.get(diffCell.cellId);
        if (currentDiff) {
          this.updateCellButtonState(diffCell.cellId, currentDiff);
        }
      });

      this.checkAllCellsStatus();
    });
    this.subscriptions.push(diffStateSub);
  }

  /**
   * Update cell UI based on approval state
   */
  private updateCellUI(cellId: string): void {
    const cellElement = this.cellButtonElements.get(cellId)?.cellItem;
    const currentState = diffStateService.getCurrentState();
    const currentDiff = currentState.pendingDiffs.get(cellId);

    if (!cellElement) return;

    // Remove existing state classes
    cellElement.classList.remove(
      'sage-ai-diff-approved',
      'sage-ai-diff-rejected',
      'sage-ai-diff-run'
    );

    const isRunDecision = currentDiff?.userDecision === 'run';

    // Add appropriate state class
    if (isRunDecision) {
      cellElement.classList.add('sage-ai-diff-run');
    } else if (currentDiff?.approved === true) {
      cellElement.classList.add('sage-ai-diff-approved');
    } else if (currentDiff?.approved === false) {
      cellElement.classList.add('sage-ai-diff-rejected');
    }

    // Update button styles
    const buttons = this.cellButtonElements.get(cellId);
    if (buttons) {
      const isRunDecision = currentDiff?.userDecision === 'run';
      const alreadyRun = currentDiff?.runResult;
      const isApproved = currentDiff?.approved === true;
      const isRejected = currentDiff?.approved === false;
      const isUnresolved = currentDiff?.approved === undefined;

      // Reset all button classes and visibility
      const allButtons = [
        buttons.approveButton,
        buttons.rejectButton,
        buttons.runButton,
        buttons.reapplyButton
      ];
      allButtons.forEach(button => {
        button.classList.remove('disabled');
        button.classList.add('hidden');
      });

      if (alreadyRun) {
        buttons.reapplyButton.classList.remove('hidden');
      } else if (isRunDecision) {
        buttons.runButton.classList.remove('hidden');
        buttons.runButton.classList.add('disabled');
        buttons.reapplyButton.classList.remove('hidden');
      } else if (isApproved) {
        buttons.approveButton.classList.remove('hidden');
        buttons.approveButton.classList.add('disabled');
        buttons.reapplyButton.classList.remove('hidden');
      } else if (isRejected) {
        buttons.rejectButton.classList.remove('hidden');
        buttons.rejectButton.classList.add('disabled');
        buttons.reapplyButton.classList.remove('hidden');
      } else if (isUnresolved) {
        buttons.approveButton.classList.remove('hidden');
        buttons.rejectButton.classList.remove('hidden');
        buttons.runButton.classList.remove('hidden');
      }

      if (currentDiff?.type !== 'edit') {
        buttons.reapplyButton.classList.add('hidden');
      }
    }
  }

  /**
   * Run a specific cell (approve and execute immediately)
   */
  public async runCell(trackingId: string): Promise<void> {
    if (this.callbacks) {
      // Update the diff state service with "run" decision
      diffStateService.updateDiffStateToRun(
        trackingId,
        this.currentNotebookPath
      );

      this.callbacks.onApprove([trackingId]);

      // Apply the diff and execute the cell
      await this.callbacks.applyApprovedDiffs(this.currentNotebookPath, [
        trackingId
      ]);

      // Execute the cell after applying the diff using the run_cell method
      const notebookTools = AppStateService.getNotebookTools();
      if (notebookTools) {
        try {
          const res = await notebookTools.run_cell({
            cell_id: trackingId,
            notebook_path: this.currentNotebookPath
          });
          diffStateService.updateDiffStateResult(
            trackingId,
            res.slice(0, 5000)
          );
        } catch (error) {
          diffStateService.updateDiffStateResult(trackingId, {});
          console.error(error);
        }
      }

      // Check if all cells are now handled
      // await this.checkAllCellsStatus();
    }
  }

  /**
   * Update the button state for a specific cell based on its diff state
   */
  private updateCellButtonState(cellId: string, diff: IPendingDiff): void {
    const buttonElements = this.cellButtonElements.get(cellId);
    if (!buttonElements) return;

    const { hoverButtons } = buttonElements;
    const isRunning = diff.userDecision === 'run' && !diff.runResult;

    if (isRunning) {
      // Show spinner, hide buttons
      this.showSpinnerForCell(cellId, hoverButtons);
    } else {
      // Show normal buttons, hide spinner
      this.hideSpinnerForCell(cellId, hoverButtons);

      this.updateCellUI(cellId);
    }
  }

  /**
   * Show spinner for a cell and hide action buttons
   */
  private showSpinnerForCell(cellId: string, hoverButtons: HTMLElement): void {
    // Hide existing buttons
    const buttons = hoverButtons.querySelectorAll('button');
    buttons.forEach(button => {
      button.classList.add('hidden');
    });

    // Create or show spinner
    let spinner = hoverButtons.querySelector(
      '.sage-ai-diff-spinner'
    ) as HTMLElement;
    if (!spinner) {
      spinner = this.createSpinnerElement();
      hoverButtons.appendChild(spinner);
    }
    spinner.classList.remove('hidden');
  }

  /**
   * Hide spinner for a cell and show action buttons
   */
  private hideSpinnerForCell(cellId: string, hoverButtons: HTMLElement): void {
    // Reset all buttons - they will be properly set by updateCellUI
    const buttons = hoverButtons.querySelectorAll('button');
    buttons.forEach(button => {
      button.classList.add('hidden');
    });

    // Hide spinner
    const spinner = hoverButtons.querySelector(
      '.sage-ai-diff-spinner'
    ) as HTMLElement;
    if (spinner) {
      spinner.classList.add('hidden');
    }
  }

  /**
   * Create a spinner element
   */
  private createSpinnerElement(): HTMLElement {
    const spinner = document.createElement('div');
    spinner.className = 'sage-ai-diff-spinner';
    return spinner;
  }

  /**
   * Create a CodeMirror merge view in a container element
   * This replaces the HTML diff generation with a proper CodeMirror merge view
   */
  private createMergeViewInContainer(
    container: HTMLElement,
    originalContent: string,
    newContent: string
  ): void {
    // Create the unified merge view extension with the same configuration as InlineDiffService
    const mergeExtension = unifiedMergeView({
      original: originalContent,
      gutter: false,
      mergeControls: false, // Disable controls since this is for display only
      highlightChanges: true,
      syntaxHighlightDeletions: true,
      allowInlineDiffs: true,
      collapseUnchanged: {}
    });

    // Create extensions array with Python language support and merge view
    const extensions: Extension[] = [
      python(),
      jupyterTheme,
      mergeExtension,
      EditorState.readOnly.of(true), // Make it read-only
      EditorView.theme({
        '.cm-scroller': {
          borderRadius: '0 0 10px 10px !important'
        },
        '.cm-content': {
          padding: '0px !important'
        }
      }),
      EditorView.editable.of(false)
    ];

    // Create the editor state
    const state = EditorState.create({
      doc: newContent,
      extensions
    });

    // Create the editor view
    const view = new EditorView({
      state,
      parent: container
    });

    if (originalContent) {
      container.classList.remove('code-mirror-empty-original-content');
    } else {
      container.classList.add('code-mirror-empty-original-content');
    }
  }
}

const COLLAPSE_ICON =
  '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 10 10" fill="none"><path d="M2.62081 5.95419C2.58175 5.99293 2.55076 6.03901 2.5296 6.08979C2.50845 6.14056 2.49756 6.19502 2.49756 6.25003C2.49756 6.30503 2.50845 6.35949 2.5296 6.41027C2.55076 6.46104 2.58175 6.50712 2.62081 6.54586L4.70414 8.62919C4.74288 8.66825 4.78896 8.69924 4.83973 8.7204C4.89051 8.74155 4.94497 8.75244 4.99997 8.75244C5.05498 8.75244 5.10944 8.74155 5.16021 8.7204C5.21099 8.69924 5.25707 8.66825 5.29581 8.62919L7.37914 6.54586C7.41819 6.50712 7.44919 6.46104 7.47035 6.41027C7.4915 6.35949 7.50239 6.30503 7.50239 6.25003C7.50239 6.19502 7.4915 6.14056 7.47035 6.08979C7.44919 6.03901 7.41819 5.99293 7.37914 5.95419C7.34041 5.91514 7.29432 5.88414 7.24355 5.86299C7.19277 5.84183 7.13831 5.83094 7.08331 5.83094C7.0283 5.83094 6.97384 5.84183 6.92307 5.86299C6.87229 5.88414 6.82621 5.91514 6.78747 5.95419L4.99997 7.74586L3.21247 5.95419C3.17374 5.91514 3.12766 5.88414 3.07688 5.86299C3.02611 5.84183 2.97165 5.83094 2.91664 5.83094C2.86164 5.83094 2.80718 5.84183 2.7564 5.86299C2.70563 5.88414 2.65954 5.91514 2.62081 5.95419ZM4.70414 1.37086L2.62081 3.45419C2.58196 3.49304 2.55114 3.53916 2.53012 3.58992C2.50909 3.64068 2.49827 3.69508 2.49827 3.75003C2.49827 3.86098 2.54235 3.9674 2.62081 4.04586C2.65966 4.08471 2.70578 4.11553 2.75654 4.13655C2.8073 4.15758 2.8617 4.1684 2.91664 4.1684C3.0276 4.1684 3.13401 4.12432 3.21247 4.04586L4.99997 2.25419L6.78747 4.04586C6.82621 4.08491 6.87229 4.11591 6.92307 4.13706C6.97384 4.15822 7.0283 4.16911 7.08331 4.16911C7.13831 4.16911 7.19277 4.15822 7.24355 4.13706C7.29432 4.11591 7.34041 4.08491 7.37914 4.04586C7.41819 4.00712 7.44919 3.96104 7.47035 3.91027C7.4915 3.85949 7.50239 3.80503 7.50239 3.75003C7.50239 3.69502 7.4915 3.64056 7.47035 3.58979C7.44919 3.53901 7.41819 3.49293 7.37914 3.45419L5.29581 1.37086C5.25707 1.33181 5.21099 1.30081 5.16021 1.27965C5.10944 1.2585 5.05498 1.24761 4.99997 1.24761C4.94497 1.24761 4.89051 1.2585 4.83973 1.27965C4.78896 1.30081 4.74288 1.33181 4.70414 1.37086Z" fill="#999999"/></svg>';
