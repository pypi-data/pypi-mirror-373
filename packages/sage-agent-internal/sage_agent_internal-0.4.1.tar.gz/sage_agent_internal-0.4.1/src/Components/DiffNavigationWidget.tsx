import * as React from 'react';
import { ReactWidget } from '@jupyterlab/ui-components';
import { DiffNavigationContent } from './DiffNavigationContent';
import { diffStateService } from '../Services/DiffStateService';
import { IPendingDiff } from '../types';
import { Subscription } from 'rxjs';
import { AppStateService } from '../AppState';

interface IDiffNavigationState {
  isVisible: boolean;
  currentDiff: number;
  totalDiffs: number;
  pendingDiffs: IPendingDiff[];
  isRunContext: boolean;
}

/**
 * React-based widget for navigating between diff cells
 * Positioned at the bottom center of the viewport with cursor-like appearance
 */
export class DiffNavigationWidget extends ReactWidget {
  private _state: IDiffNavigationState;
  private currentNotebookId?: string | null = null;
  private subscriptions: Subscription[] = [];

  constructor() {
    super();

    this.id = 'sage-ai-diff-navigation-widget';
    this.addClass('sage-ai-diff-navigation-widget');
    this.addClass('jp-Widget'); // Add Jupyter base widget class
    this.addClass('hidden');
    this.title.label = 'Diff Navigation';

    // Initialize state
    this._state = {
      isVisible: false,
      currentDiff: 0,
      totalDiffs: 0,
      pendingDiffs: [],
      isRunContext: false
    };

    // Set up diff state subscriptions
    this.setupDiffStateSubscriptions();
  }

  /**
   * Set up RxJS subscriptions for diff state changes
   */
  private setupDiffStateSubscriptions(): void {
    // Subscribe to diff state changes to auto-update the display
    const diffStateSub = diffStateService.diffState$.subscribe(diffState => {
      const allDiffs = Array.from(diffState.pendingDiffs.values());
      const relevantDiffs = this.filterUnresolvedDiffs(
        allDiffs,
        this.currentNotebookId
      );

      const shouldBeVisible = relevantDiffs.length > 0;
      const currentDiffIndex = shouldBeVisible
        ? Math.max(1, this._state.currentDiff)
        : 0;

      this._state = {
        ...this._state,
        totalDiffs: relevantDiffs.length,
        pendingDiffs: relevantDiffs,
        // Only update visibility if the widget is already visible, to avoid flickering
        isVisible: this._state.isVisible && shouldBeVisible,
        currentDiff: currentDiffIndex
      };

      this.updateVisibility();
      this.update();
    });
    this.subscriptions.push(diffStateSub);

    // Subscribe to allDiffsResolved changes to automatically hide when complete
    const allResolvedSub = diffStateService.allDiffsResolved$.subscribe(
      ({ notebookId }) => {
        const currentState = diffStateService.getCurrentState();
        const allDiffs = Array.from(currentState.pendingDiffs.values());
        const relevantDiffs = this.filterUnresolvedDiffs(
          allDiffs,
          this.currentNotebookId
        );

        // If no unresolved diffs remain, hide the display
        if (relevantDiffs.length === 0) {
          this._state = {
            ...this._state,
            isVisible: false,
            currentDiff: 0,
            totalDiffs: 0,
            pendingDiffs: []
          };
          this.updateVisibility();
          this.update();
        }
      }
    );
    this.subscriptions.push(allResolvedSub);
  }

  /**
   * Clean up subscriptions
   */
  public dispose(): void {
    this.subscriptions.forEach(sub => sub.unsubscribe());
    this.subscriptions = [];
    super.dispose();
  }

  /**
   * Filter diffs to only include unresolved ones for the current notebook
   */
  private filterUnresolvedDiffs(
    allDiffs: IPendingDiff[],
    notebookId?: string | null
  ): IPendingDiff[] {
    return allDiffs.filter(diff => {
      // Filter by notebook ID
      const matchesNotebook = !notebookId || diff.notebookId === notebookId;

      // Filter out resolved diffs (only show unresolved)
      const isUnresolved =
        diff.approved === undefined &&
        (!diff.userDecision || diff.userDecision === null);

      return matchesNotebook && isUnresolved;
    });
  }

  /**
   * Update widget visibility based on state
   */
  private updateVisibility(): void {
    if (this._state.isVisible && this._state.totalDiffs > 0) {
      this.removeClass('hidden');
    } else {
      this.addClass('hidden');
    }
  }

  /**
   * Set the current notebook ID to filter diffs
   */
  public setNotebookId(notebookId: string | null): void {
    this.currentNotebookId = notebookId;
    // The subscriptions will automatically update the state when the notebook ID changes
    // Just trigger a manual update to ensure immediate response
    const currentState = diffStateService.getCurrentState();
    const allDiffs = Array.from(currentState.pendingDiffs.values());
    const relevantDiffs = this.filterUnresolvedDiffs(allDiffs, notebookId);

    this._state = {
      ...this._state,
      totalDiffs: relevantDiffs.length,
      pendingDiffs: relevantDiffs,
      isVisible: relevantDiffs.length > 0,
      currentDiff:
        relevantDiffs.length > 0 ? Math.max(1, this._state.currentDiff) : 0
    };

    this.updateVisibility();
    this.update();
  }

  /**
   * Navigate to previous diff (with infinite/circular navigation)
   */
  private navigateToPrevious = (): void => {
    if (this._state.totalDiffs > 0) {
      // Wrap around to last diff if currently on first diff
      const newDiffIndex =
        this._state.currentDiff <= 1
          ? this._state.totalDiffs
          : this._state.currentDiff - 1;

      this._state = {
        ...this._state,
        currentDiff: newDiffIndex
      };
      this.update();

      // Navigate to the previous diff cell
      if (newDiffIndex > 0 && newDiffIndex <= this._state.pendingDiffs.length) {
        const targetDiff = this._state.pendingDiffs[newDiffIndex - 1];
        if (targetDiff && targetDiff.cellId) {
          AppStateService.getNotebookTools().scrollToCellById(
            targetDiff.cellId
          );
        }
      }
    }
  };

  /**
   * Navigate to next diff (with infinite/circular navigation)
   */
  private navigateToNext = (): void => {
    if (this._state.totalDiffs > 0) {
      // Wrap around to first diff if currently on last diff
      const newDiffIndex =
        this._state.currentDiff >= this._state.totalDiffs
          ? 1
          : this._state.currentDiff + 1;

      this._state = {
        ...this._state,
        currentDiff: newDiffIndex
      };
      this.update();

      // Navigate to the next diff cell
      if (newDiffIndex > 0 && newDiffIndex <= this._state.pendingDiffs.length) {
        const targetDiff = this._state.pendingDiffs[newDiffIndex - 1];
        if (targetDiff && targetDiff.cellId) {
          AppStateService.getNotebookTools().scrollToCellById(
            targetDiff.cellId
          );
        }
      }
    }
  };

  /**
   * Reject all diffs using DiffStateService
   */
  private rejectAll = async (): Promise<void> => {
    if (this._state.pendingDiffs.length === 0) {
      console.log('No pending diffs to reject');
      return;
    }

    console.log(`Rejecting ${this._state.pendingDiffs.length} diffs`);

    // Update DiffStateService for all pending diffs
    for (const diff of this._state.pendingDiffs) {
      diffStateService.updateDiffState(
        diff.cellId,
        false, // approved = false
        diff.notebookId
      );
    }

    // Also trigger the dialog action to handle the DOM updates
    try {
      await AppStateService.getNotebookDiffManager().diffApprovalDialog.rejectAll();
    } catch (error) {
      console.warn('Error calling diffApprovalDialog.rejectAll():', error);
    }
  };

  /**
   * Accept all diffs using DiffStateService
   */
  private acceptAll = async (): Promise<void> => {
    try {
      await AppStateService.getNotebookDiffManager().diffApprovalDialog.approveAll();
    } catch (error) {
      console.warn('Error calling diffApprovalDialog.approveAll():', error);
    }
  };

  /**
   * Accept all diffs (and run if in run context) - matches LLMStateContent behavior exactly
   */
  private acceptAndRunAll = async (): Promise<void> => {
    if (this._state.pendingDiffs.length === 0) {
      console.log('No pending diffs to accept');
      return;
    }

    console.log(
      `Processing ${this._state.pendingDiffs.length} diffs in ${this._state.isRunContext ? 'run' : 'approve'} context`
    );

    if (this._state.isRunContext) {
      // For run context, use runCell for each diff (matches LLMStateContent logic)
      for (const diff of this._state.pendingDiffs) {
        if (!diff.userDecision) {
          try {
            await AppStateService.getNotebookDiffManager().diffApprovalDialog.runCell(
              diff.cellId
            );
          } catch (error) {
            console.warn(
              `Error calling diffApprovalDialog.runCell(${diff.cellId}):`,
              error
            );
          }
        }
      }
    } else {
      // For regular approval, update DiffStateService first (matches LLMStateContent logic)
      for (const diff of this._state.pendingDiffs) {
        diffStateService.updateDiffState(diff.cellId, true, diff.notebookId);
      }
      // Then trigger the dialog action
      try {
        await AppStateService.getNotebookDiffManager().diffApprovalDialog.approveAll();
      } catch (error) {
        console.warn('Error calling diffApprovalDialog.approveAll():', error);
      }
    }
  };

  /**
   * Update the counter (external API)
   */
  public updateCounter(current: number, total: number): void {
    this._state = {
      ...this._state,
      currentDiff: current,
      totalDiffs: total
    };
    this.update();
  }

  /**
   * Set the run context for the widget
   */
  public setRunContext(isRunContext: boolean): void {
    if (this._state.isRunContext !== isRunContext) {
      this._state = {
        ...this._state,
        isRunContext
      };
      this.update();
    }
  }

  /**
   * Force a refresh of the widget state from DiffStateService
   * Useful when called from external components like LLMStateDisplay
   */
  public refreshFromDiffState(
    notebookId?: string | null,
    isRunContext?: boolean
  ): void {
    if (notebookId !== undefined) {
      this.setNotebookId(notebookId);
    } else {
      // Trigger a manual update from current state
      const currentState = diffStateService.getCurrentState();
      const allDiffs = Array.from(currentState.pendingDiffs.values());
      const relevantDiffs = this.filterUnresolvedDiffs(
        allDiffs,
        this.currentNotebookId
      );

      this._state = {
        ...this._state,
        totalDiffs: relevantDiffs.length,
        pendingDiffs: relevantDiffs,
        isVisible: relevantDiffs.length > 0,
        currentDiff:
          relevantDiffs.length > 0 ? Math.max(1, this._state.currentDiff) : 0,
        isRunContext: !!isRunContext
      };

      this.updateVisibility();
      this.update();
    }
  }

  /**
   * Show pending diffs (mirrors LLMStateDisplay.showPendingDiffs)
   * @param notebookId Optional ID to filter diffs for a specific notebook
   * @param isRunContext Whether this is in run context
   */
  public showPendingDiffs(
    notebookId?: string | null,
    isRunContext?: boolean
  ): void {
    // Set the notebook ID if provided
    if (notebookId !== undefined) {
      this.currentNotebookId = notebookId;
    }

    // Set run context if provided
    if (isRunContext !== undefined) {
      this._state = {
        ...this._state,
        isRunContext
      };
    }

    // The subscriptions will automatically update the display based on current state
    // But we can trigger a manual update for immediate response
    const currentState = diffStateService.getCurrentState();
    const allDiffs = Array.from(currentState.pendingDiffs.values());
    const relevantDiffs = this.filterUnresolvedDiffs(
      allDiffs,
      this.currentNotebookId
    );

    // Update state with filtered diffs
    this._state = {
      ...this._state,
      totalDiffs: relevantDiffs.length,
      pendingDiffs: relevantDiffs,
      isVisible: relevantDiffs.length > 0,
      currentDiff:
        relevantDiffs.length > 0 ? Math.max(1, this._state.currentDiff) : 0,
      isRunContext: isRunContext || this._state.isRunContext
    };

    this.updateVisibility();
    this.update();
  }

  /**
   * Hide pending diffs (mirrors LLMStateDisplay.hidePendingDiffs)
   */
  public hidePendingDiffs(): void {
    this._state = {
      ...this._state,
      isVisible: false,
      currentDiff: 0,
      totalDiffs: 0,
      pendingDiffs: []
    };

    this.updateVisibility();
    this.update();
  }

  /**
   * Render the React component
   */
  render(): JSX.Element {
    return (
      <DiffNavigationContent
        isVisible={this._state.isVisible}
        currentDiff={this._state.currentDiff}
        totalDiffs={this._state.totalDiffs}
        isRunContext={this._state.isRunContext}
        onNavigatePrevious={this.navigateToPrevious}
        onNavigateNext={this.navigateToNext}
        onRejectAll={this.rejectAll}
        onAcceptAll={this.acceptAll}
        onAcceptAndRunAll={this.acceptAndRunAll}
      />
    );
  }
}
