import * as React from 'react';
import { ReactWidget } from '@jupyterlab/ui-components';
import { ISignal, Signal } from '@lumino/signaling';

/**
 * Interface for more options actions
 */
export interface IMoreOptionsActions {
  onRenameChat: () => void;
  onDeleteChat: () => void;
}

/**
 * Interface for the MoreOptions state
 */
interface IMoreOptionsState {
  isVisible: boolean;
  anchorElement?: HTMLElement;
}

/**
 * React component for displaying more options content
 */
interface MoreOptionsContentProps {
  isVisible: boolean;
  onRenameChat: () => void;
  onDeleteChat: () => void;
  onClose: () => void;
}

function MoreOptionsContent({
  isVisible,
  onRenameChat,
  onDeleteChat,
  onClose
}: MoreOptionsContentProps): JSX.Element | null {
  if (!isVisible) {
    return <div className="sage-ai-more-options-popover"></div>;
  }

  const handleRenameChat = () => {
    onRenameChat();
    onClose();
  };

  const handleDeleteChat = () => {
    onDeleteChat();
    onClose();
  };

  return (
    <div className="sage-ai-more-options-popover">
      <div className="sage-ai-more-options-content">
        <button
          className="sage-ai-more-options-item"
          onClick={handleRenameChat}
          type="button"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 16 16"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M11.3333 2L14 4.66667L5.66667 13H3V10.3333L11.3333 2Z"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          <span>Rename Chat</span>
        </button>
        <button
          className="sage-ai-more-options-item sage-ai-more-options-item-danger"
          onClick={handleDeleteChat}
          type="button"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 16 16"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M2 4H14M12.6667 4V13.3333C12.6667 13.6869 12.5262 14.0261 12.2761 14.2761C12.0261 14.5262 11.6869 14.6667 11.3333 14.6667H4.66667C4.31304 14.6667 3.97391 14.5262 3.72386 14.2761C3.47381 14.0261 3.33333 13.6869 3.33333 13.3333V4M5.33333 4V2.66667C5.33333 2.31304 5.47381 1.97391 5.72386 1.72386C5.97391 1.47381 6.31304 1.33333 6.66667 1.33333H9.33333C9.68696 1.33333 10.0261 1.47381 10.2761 1.72386C10.5262 1.97391 10.6667 2.31304 10.6667 2.66667V4"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          <span>Delete Chat</span>
        </button>
      </div>
    </div>
  );
}

/**
 * Component for displaying more options popover
 */
export class MoreOptionsDisplay extends ReactWidget {
  private _state: IMoreOptionsState;
  private _stateChanged = new Signal<this, IMoreOptionsState>(this);
  private _actions: IMoreOptionsActions;

  constructor(actions: IMoreOptionsActions) {
    super();
    this._actions = actions;
    this._state = {
      isVisible: false,
      anchorElement: undefined
    };
    this.addClass('sage-ai-more-options-widget');

    // Close popover when clicking outside
    this.setupOutsideClickHandler();
  }

  /**
   * Get the signal that fires when state changes
   */
  public get stateChanged(): ISignal<this, IMoreOptionsState> {
    return this._stateChanged;
  }

  /**
   * Render the React component
   */
  render(): JSX.Element {
    return (
      <MoreOptionsContent
        isVisible={this._state.isVisible}
        onRenameChat={this._actions.onRenameChat}
        onDeleteChat={this._actions.onDeleteChat}
        onClose={() => this.hide()}
      />
    );
  }

  /**
   * Show the more options popover anchored to an element
   * @param anchorElement The element to anchor the popover to
   */
  public showPopover(anchorElement: HTMLElement): void {
    this._state = {
      isVisible: true,
      anchorElement
    };

    this._stateChanged.emit(this._state);
    this.update();

    // Position the popover relative to the anchor element
    this.positionPopover(anchorElement);
  }

  /**
   * Hide the more options popover
   */
  public hide(): void {
    this._state = {
      isVisible: false,
      anchorElement: undefined
    };

    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Position the popover relative to the anchor element
   */
  private positionPopover(anchorElement: HTMLElement): void {
    // Use requestAnimationFrame to ensure the DOM is updated
    const popover = this.node.querySelector(
      '.sage-ai-more-options-popover'
    ) as HTMLElement;

    if (popover) {
      // Find the common positioned ancestor (the chatbox container)
      let container = anchorElement.offsetParent as HTMLElement;
      if (!container) {
        container = document.body;
      }

      // Get the anchor element's position relative to its offset parent
      let anchorTop = anchorElement.offsetTop;
      let anchorLeft = anchorElement.offsetLeft;
      let currentElement = anchorElement.offsetParent as HTMLElement;

      // Walk up the DOM tree to get the position relative to the container
      while (currentElement && currentElement !== container) {
        anchorTop += currentElement.offsetTop;
        anchorLeft += currentElement.offsetLeft;
        currentElement = currentElement.offsetParent as HTMLElement;
      }

      // Temporarily make popover visible to measure its dimensions
      const originalVisibility = popover.style.visibility;
      const originalDisplay = popover.style.display;
      popover.style.visibility = 'hidden';
      popover.style.display = 'block';

      const popoverHeight = popover.offsetHeight;
      const popoverWidth = popover.offsetWidth;

      // Reset visibility
      popover.style.visibility = originalVisibility;
      popover.style.display = originalDisplay;

      // Calculate position above the anchor with spacing
      const anchorHeight = anchorElement.offsetHeight;
      const anchorWidth = anchorElement.offsetWidth;

      let top = anchorTop - popoverHeight - 8;
      let left = anchorLeft;

      // Get container dimensions for boundary checking
      const containerWidth = container.offsetWidth || window.innerWidth;

      // Adjust horizontal position if it goes off the right edge
      if (left + popoverWidth > containerWidth - 8) {
        left = anchorLeft + anchorWidth - popoverWidth;
      }

      // Adjust horizontal position if it goes off the left edge
      if (left < 8) {
        left = 8;
      }

      // If there's not enough space above, position below the anchor
      if (top < 8) {
        top = anchorTop + anchorHeight + 8;
      }

      // Apply the calculated position
      popover.style.position = 'absolute';
      popover.style.top = `${top - 22}px`;
      popover.style.left = `${left}px`;
      popover.style.transform = 'none';
      popover.style.zIndex = '9999';
    }
  }

  /**
   * Setup click outside handler to close the popover
   */
  private setupOutsideClickHandler(): void {
    const handleClickOutside = (event: MouseEvent) => {
      if (this._state.isVisible && !this.node.contains(event.target as Node)) {
        // Also check if the click is on the anchor element
        if (
          this._state.anchorElement &&
          !this._state.anchorElement.contains(event.target as Node)
        ) {
          this.hide();
        }
      }
    };

    document.addEventListener('click', handleClickOutside);

    // Clean up on disposal
    this.disposed.connect(() => {
      document.removeEventListener('click', handleClickOutside);
    });
  }

  /**
   * Check if the popover is currently visible
   */
  public getIsVisible(): boolean {
    return this._state.isVisible;
  }

  /**
   * Get the current state
   */
  public getState(): IMoreOptionsState {
    return { ...this._state };
  }
}
