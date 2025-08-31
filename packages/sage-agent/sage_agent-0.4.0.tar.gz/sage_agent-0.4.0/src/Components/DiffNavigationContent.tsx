import * as React from 'react';
import {
  ARROW_UP_ICON,
  ARROW_DOWN_ICON,
  APPROVE_ICON,
  REJECT_ICON,
  RUN_ICON
} from './icons';

interface DiffNavigationContentProps {
  isVisible: boolean;
  currentDiff: number;
  totalDiffs: number;
  isRunContext: boolean;
  onNavigatePrevious: () => void;
  onNavigateNext: () => void;
  onRejectAll: () => void;
  onAcceptAll: () => void;
  onAcceptAndRunAll: () => void;
}

export function DiffNavigationContent({
  isVisible,
  currentDiff,
  totalDiffs,
  isRunContext,
  onNavigatePrevious,
  onNavigateNext,
  onRejectAll,
  onAcceptAll,
  onAcceptAndRunAll
}: DiffNavigationContentProps): JSX.Element | null {
  if (!isVisible || totalDiffs === 0) {
    return null;
  }

  return (
    <div className="sage-ai-diff-navigation-floating-content">
      {/* Navigation Section (Left) */}
      <div className="sage-ai-diff-navigation-navigation-section">
        <button
          className="sage-ai-diff-navigation-nav-button sage-ai-diff-navigation-prev-button"
          onClick={onNavigatePrevious}
          title="Previous cell"
        >
          <ARROW_UP_ICON.react className="sage-ai-diff-navigation-nav-icon" />
        </button>
        <span className="sage-ai-diff-navigation-counter-display">
          {currentDiff} / {totalDiffs}
        </span>
        <button
          className="sage-ai-diff-navigation-nav-button sage-ai-diff-navigation-next-button"
          onClick={onNavigateNext}
          title="Next cell"
        >
          <ARROW_DOWN_ICON.react className="sage-ai-diff-navigation-nav-icon" />
        </button>
      </div>

      {/* Action Buttons Section (Right) */}
      <div className="sage-ai-diff-navigation-button-section">
        <button
          className="sage-ai-diff-navigation-action-button sage-ai-diff-navigation-reject-button"
          onClick={onRejectAll}
        >
          <REJECT_ICON.react className="sage-ai-diff-navigation-action-icon" />
          <span>{totalDiffs > 1 ? 'Reject All' : 'Reject'}</span>
        </button>
        <button
          className="sage-ai-diff-navigation-action-button sage-ai-diff-navigation-approve-button"
          onClick={onAcceptAll}
        >
          <APPROVE_ICON.react className="sage-ai-diff-navigation-action-icon" />
          <span>{totalDiffs > 1 ? 'Approve All' : 'Approve'}</span>
        </button>
        {isRunContext && (
          // In run context, show "Run All"/"Run" button (equivalent to approve button in LLMStateContent)
          <button
            className="sage-ai-diff-navigation-action-button sage-ai-diff-navigation-accept-run-button"
            onClick={onAcceptAndRunAll}
          >
            <RUN_ICON.react className="sage-ai-diff-navigation-action-icon" />
            <span>{totalDiffs > 1 ? 'Run All' : 'Run'}</span>
          </button>
        )}
      </div>
    </div>
  );
}
