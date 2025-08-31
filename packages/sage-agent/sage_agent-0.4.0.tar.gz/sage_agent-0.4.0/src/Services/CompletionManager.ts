import { INotebookTracker } from '@jupyterlab/notebook';
import { CodeEditor } from '@jupyterlab/codeeditor';
import { TabCompletionService } from './TabCompletionService';
import { InlineCompletionWidget } from '../Components/InlineCompletionWidget';

export class CompletionManager {
  private static _instance: CompletionManager;
  private notebookTracker: INotebookTracker | null = null;
  private tabCompletionService: TabCompletionService;
  private completionWidget: InlineCompletionWidget;
  private activeEditor: CodeEditor.IEditor | null = null;
  private attachedEditors = new WeakSet<CodeEditor.IEditor>();
  private attachedScrollHosts = new WeakSet<HTMLElement>();
  private attachedKeydownHosts = new WeakSet<HTMLElement>();
  private attachedKeydownNodes = new WeakSet<EventTarget>();
  private cursorIdleTimeoutId: number | null = null;
  private lastCursorPosition: CodeEditor.IPosition | null = null;
  private editorHasFocus: boolean = false;

  public static getInstance(): CompletionManager {
    if (!CompletionManager._instance) {
      CompletionManager._instance = new CompletionManager();
    }
    return CompletionManager._instance;
  }

  private constructor() {
    this.tabCompletionService = TabCompletionService.getInstance();
    this.completionWidget = new InlineCompletionWidget();
  }

  public initialize(notebooks: INotebookTracker): void {
    this.notebookTracker = notebooks;

    // Set up active cell checker for TabCompletionService
    this.tabCompletionService.setActiveCellChecker(() => {
      // Check if there's an active cell in the current notebook
      return !!(
        notebooks.activeCell || notebooks.currentWidget?.content?.activeCell
      );
    });

    // Connect as soon as a notebook widget is added
    notebooks.widgetAdded.connect((_, panel) => {
      setTimeout(() => {
        const active = panel?.content?.activeCell;
        if (active?.editor) {
          this.connectToEditor(active.editor);
        }
      }, 0);
    });

    // Listen to active cell changes
    notebooks.activeCellChanged.connect((_, cell) => {
      // console.log('[CompletionManager] Active cell changed:', !!cell);

      if (this.activeEditor) {
        this.disconnectFromEditor();
      }

      if (cell && cell.editor) {
        // console.log('[CompletionManager] Connecting to new editor');
        this.connectToEditor(cell.editor);
      }
    });

    // Also listen for current widget changes
    notebooks.currentChanged.connect((_, notebook) => {
      // console.log('[CompletionManager] Notebook changed:', !!notebook);
      setTimeout(() => {
        const activeCell = notebook?.content?.activeCell;
        if (notebook && activeCell && activeCell.editor) {
          // console.log(
          //   '[CompletionManager] Connecting to active cell in new notebook'
          // );
          this.connectToEditor(activeCell.editor);
        }
      }, 100);
    });

    // Check if there's already an active cell
    if (notebooks.activeCell && notebooks.activeCell.editor) {
      // console.log('[CompletionManager] Found existing active cell, connecting');
      this.connectToEditor(notebooks.activeCell.editor);
    }

    // Also check the current widget
    const currentActive = notebooks.currentWidget?.content?.activeCell;
    if (currentActive && currentActive.editor) {
      // console.log(
      //   '[CompletionManager] Found active cell in current widget, connecting'
      // );
      this.connectToEditor(currentActive.editor);
    }

    // Retry loop: attempt to connect if nothing attached yet (first-load case)
    this.tryInitialConnect(notebooks);

    // console.log('[CompletionManager] Initialized');
  }

  private tryInitialConnect(notebooks: INotebookTracker): void {
    let attempts = 0;
    const maxAttempts = 20;
    const intervalMs = 150;

    const timer = setInterval(() => {
      attempts++;
      if (this.activeEditor) {
        clearInterval(timer);
        return;
      }
      const editor =
        notebooks.currentWidget?.content?.activeCell?.editor ||
        notebooks.activeCell?.editor;
      if (editor) {
        this.connectToEditor(editor);
        clearInterval(timer);
      } else if (attempts >= maxAttempts) {
        clearInterval(timer);
      }
    }, intervalMs);
  }

  /**
   * Check if the current editor has focus by checking the DOM focus state
   */
  private isEditorFocused(): boolean {
    if (!this.activeEditor) return false;

    try {
      // Try to get the CodeMirror view DOM element
      const view: any =
        (this.activeEditor as any).editor ??
        (this.activeEditor as any)._editor ??
        (this.activeEditor as any).cm;
      const viewDom: HTMLElement | undefined = view?.dom;

      if (viewDom) {
        // Check if the editor DOM or any of its children have focus
        return (
          viewDom.contains(document.activeElement) ||
          viewDom === document.activeElement
        );
      }

      // Fallback: check the editor host
      const editorHost = this.activeEditor.host;
      if (editorHost) {
        return (
          editorHost.contains(document.activeElement) ||
          editorHost === document.activeElement
        );
      }
    } catch (error) {
      console.warn('[CompletionManager] Error checking editor focus:', error);
    }

    return false;
  }

  private connectToEditor(editor: CodeEditor.IEditor): void {
    this.activeEditor = editor;
    this.lastCursorPosition = editor.getCursorPosition();

    // Initialize focus state
    this.editorHasFocus = this.isEditorFocused();

    if (this.attachedEditors.has(editor)) {
      // console.log('[CompletionManager] Editor already connected');
      return;
    }
    this.attachedEditors.add(editor);

    // console.log('[CompletionManager] Connected to editor');

    // Listen to text changes
    editor.model.sharedModel.changed.connect(() => {
      this.handleTextChange();
    });

    // Clear overlay on actual cursor movement and start idle timer
    editor.model.selections.changed.connect(() => {
      const currentPos = editor.getCursorPosition();
      const lastPos = this.lastCursorPosition;
      const moved =
        !lastPos ||
        currentPos.line !== lastPos.line ||
        currentPos.column !== lastPos.column;
      this.lastCursorPosition = currentPos;

      if (moved) {
        // Clear any existing completion when cursor moves
        if (this.completionWidget.isCompletionShowing()) {
          this.completionWidget.hideCompletion();
        }
        // Reset the idle timer - start counting 3 seconds from this cursor position
        this.resetCursorIdleTimer();
      }
    });

    // Avoid auto-hiding on scroll; overlay will reposition itself

    const attachKeydown = (node: EventTarget) => {
      if (this.attachedKeydownNodes.has(node)) return;
      node.addEventListener(
        'keydown',
        async (ev: Event) => {
          const event = ev as KeyboardEvent;
          // console.log(
          //   '[CompletionManager] Key pressed:',
          //   event.key,
          //   event.shiftKey
          // );
          if (event.key === 'Tab' && !event.shiftKey) {
            // console.log(
            //   '[CompletionManager] Tab key detected, checking completion state...'
            // );
            if (this.completionWidget.isCompletionShowing()) {
              // console.log(
              //   '[CompletionManager] Completion showing, accepting...'
              // );
              event.preventDefault();
              event.stopPropagation();
              this.completionWidget.acceptCompletion();
              return;
            }
            // console.log(
            //   '[CompletionManager] No completion showing, triggering handleTabKey...'
            // );
            // No completion showing: allow default Tab behavior (indent)
            // but trigger an async suggestion fetch to show ghost shortly after
            void this.handleTabKey();
            return;
          } else if (
            event.key === 'Escape' &&
            this.completionWidget.isCompletionShowing()
          ) {
            event.preventDefault();
            event.stopPropagation();
            this.completionWidget.rejectCompletion();
            return;
          }
        },
        { capture: true }
      );
      this.attachedKeydownNodes.add(node);
    };

    // Attach to editor host
    try {
      const editorHost = editor.host;
      if (editorHost && !this.attachedKeydownHosts.has(editorHost)) {
        attachKeydown(editorHost);
        this.attachedKeydownHosts.add(editorHost);
        // console.log(
        //   '[CompletionManager] Added keydown listener to editor host'
        // );
      }
    } catch (error) {
      console.error(
        '[CompletionManager] Error setting up key listeners on host:',
        error
      );
    }

    // Attach directly to CodeMirror view DOM when available
    try {
      const view: any =
        (editor as any).editor ?? (editor as any)._editor ?? (editor as any).cm;
      const viewDom: EventTarget | undefined = view?.dom;
      if (viewDom) {
        attachKeydown(viewDom);
        // console.log(
        //   '[CompletionManager] Added keydown listener to CodeMirror view DOM'
        // );

        // Add focus and blur listeners to track focus state
        const focusListener = () => {
          this.editorHasFocus = true;
          // console.log('[CompletionManager] Editor gained focus');
        };

        const blurListener = () => {
          this.editorHasFocus = false;
          // console.log('[CompletionManager] Editor lost focus');
          // Hide any visible completion when editor loses focus
          if (this.completionWidget.isCompletionShowing()) {
            this.completionWidget.hideCompletion();
          }
          // Clear the cursor idle timer when losing focus
          this.clearCursorIdleTimer();
        };

        viewDom.addEventListener('focus', focusListener, true);
        viewDom.addEventListener('blur', blurListener, true);
      }
    } catch (error) {
      console.error(
        '[CompletionManager] Error setting up key listeners on view DOM:',
        error
      );
    }
  }

  private disconnectFromEditor(): void {
    if (this.activeEditor) {
      this.completionWidget.hideCompletion();
      // Stop cursor idle timer when disconnecting from this editor
      this.clearCursorIdleTimer();
      // Reset focus state
      this.editorHasFocus = false;
      // Don't set activeEditor to null immediately to avoid race conditions
      setTimeout(() => {
        this.activeEditor = null;
      }, 50);
    }
  }

  private getCurrentLinePrefixSuffix(): {
    prefix: string;
    suffix: string;
    replacementEndPos?: CodeEditor.IPosition;
  } {
    if (!this.activeEditor) return { prefix: '', suffix: '' };

    const cursor = this.activeEditor.getCursorPosition();
    const text = this.activeEditor.model.sharedModel.getSource();
    const lines = text.split('\n');

    const startLine = Math.max(0, cursor.line - 10);
    const endLine = Math.min(lines.length - 1, cursor.line + 1); // 1 lines after cursor for replacement context

    // Build prefix: from startLine to cursor position
    const prefixLines = lines.slice(startLine, cursor.line);
    const currentPrefix = (lines[cursor.line] || '').substring(
      0,
      cursor.column
    );
    prefixLines.push(currentPrefix);
    const prefix = prefixLines.join('\n');

    // Build suffix: from cursor position to endLine (1 line after)
    const currentSuffix = (lines[cursor.line] || '').substring(cursor.column);
    const suffixLines = [
      currentSuffix,
      ...lines.slice(cursor.line + 1, endLine + 1)
    ];
    const suffix = suffixLines.join('\n');

    // Calculate potential replacement end position (end of current line + 1 more line)
    const replacementEndLine = Math.min(lines.length - 1, cursor.line + 1);
    const replacementEndPos: CodeEditor.IPosition = {
      line: replacementEndLine,
      column: (lines[replacementEndLine] || '').length
    };

    return { prefix, suffix, replacementEndPos };
  }

  private async handleTabKey(): Promise<void> {
    // console.log('[CompletionManager] handleTabKey called');
    if (!this.activeEditor) {
      // console.log('[CompletionManager] No active editor in handleTabKey');
      return;
    }

    // Check if the editor has focus before processing tab completion
    if (!this.editorHasFocus && !this.isEditorFocused()) {
      // console.log(
      //   '[CompletionManager] Editor not focused, skipping tab completion'
      // );
      return;
    }

    const { prefix, suffix, replacementEndPos } =
      this.getCurrentLinePrefixSuffix();

    // console.log('[CompletionManager] Tab key pressed, context:', {
    //   prefix: JSON.stringify(prefix),
    //   suffix: JSON.stringify(suffix),
    //   prefixLength: prefix.length,
    //   suffixLength: suffix.length
    // });

    // Get completion from service
    const completion = await this.tabCompletionService.getCompletion(
      prefix,
      suffix
    );

    // console.log('[CompletionManager] Completion result:', completion);

    if (completion) {
      // console.log('[CompletionManager] Got completion, showing inline');
      this.completionWidget.showCompletion(
        this.activeEditor,
        completion,
        () => this.acceptCompletion(completion, replacementEndPos),
        () => this.rejectCompletion(),
        replacementEndPos
      );
    } else {
      // console.log(
      //   '[CompletionManager] No completion found for prefix:',
      //   prefix
      // );
    }
  }

  private async handleCursorIdle(): Promise<void> {
    if (!this.activeEditor) return;
    if (this.completionWidget.isCompletionShowing()) return;

    // Check if the editor has focus before showing completions
    if (!this.editorHasFocus && !this.isEditorFocused()) {
      // console.log(
      //   '[CompletionManager] Editor not focused, skipping cursor idle completion'
      // );
      return;
    }

    const { prefix, suffix, replacementEndPos } =
      this.getCurrentLinePrefixSuffix();

    const willSuggest = this.tabCompletionService.canSuggestSync(
      prefix,
      suffix
    );
    if (!willSuggest) return;

    const completion = await this.tabCompletionService.getCompletion(
      prefix,
      suffix
    );

    if (completion) {
      // Double-check focus before showing completion (race condition protection)
      if (!this.editorHasFocus && !this.isEditorFocused()) {
        // console.log(
        //   '[CompletionManager] Editor lost focus during completion fetch, skipping display'
        // );
        return;
      }

      // console.log(
      //   '[CompletionManager] Cursor idle suggestion ready, showing inline'
      // );
      this.completionWidget.showCompletion(
        this.activeEditor,
        completion,
        () => this.acceptCompletion(completion, replacementEndPos),
        () => this.rejectCompletion(),
        replacementEndPos
      );
    }
  }

  private resetCursorIdleTimer(): void {
    this.clearCursorIdleTimer();
    // Start a 3-second timer for cursor idle detection
    this.cursorIdleTimeoutId = window.setTimeout(() => {
      void this.handleCursorIdle();
    }, 1000);
  }

  private clearCursorIdleTimer(): void {
    if (this.cursorIdleTimeoutId !== null) {
      clearTimeout(this.cursorIdleTimeoutId);
      this.cursorIdleTimeoutId = null;
    }
  }

  private async handleTextChange(): Promise<void> {
    if (!this.activeEditor) {
      // console.log('[CompletionManager] No active editor in handleTextChange');
    }

    // Clear any existing completion when text changes
    if (this.completionWidget.isCompletionShowing()) {
      this.completionWidget.hideCompletion();
    }

    // Reset cursor idle timer on text changes
    this.resetCursorIdleTimer();
  }

  private acceptCompletion(
    completion: string,
    replacementEndPos?: CodeEditor.IPosition
  ): void {
    // console.log('[CompletionManager] Completion accepted:', completion);
    // Widget performs replacement and cursor move on accept
  }

  private rejectCompletion(): void {
    this.completionWidget.hideCompletion();
    // console.log('[CompletionManager] Completion rejected');
  }
}
