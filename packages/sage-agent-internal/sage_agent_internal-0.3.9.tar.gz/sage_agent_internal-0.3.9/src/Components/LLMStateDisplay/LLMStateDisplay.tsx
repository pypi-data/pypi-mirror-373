import * as React from 'react';
import { Widget } from '@lumino/widgets';
import { ReactWidget } from '@jupyterlab/ui-components';
import { LLMStateContent } from './LLMStateContent';
import { ILLMState, LLMDisplayState } from './types';
import { diffStateService } from '../../Services/DiffStateService';
import { Subscription } from 'rxjs';

/**
 * Component for displaying LLM processing state above the chat input
 */
export class LLMStateDisplay extends ReactWidget {
  private _state: ILLMState;
  private subscriptions: Subscription[] = [];

  constructor() {
    super();
    this._state = {
      isVisible: false,
      state: LLMDisplayState.IDLE,
      text: ''
    };
    this.addClass('sage-ai-llm-state-widget');
    this.addClass('hidden');
    this.setupDiffStateSubscriptions();
  }

  /**
   * Set up RxJS subscriptions for diff state changes
   */
  private setupDiffStateSubscriptions(): void {
    // Subscribe to diff state changes to auto-update the display
    const diffStateSub = diffStateService.diffState$.subscribe(diffState => {
      // If we're in diff mode and diffs change, update the display
      if (this._state.state === LLMDisplayState.DIFF) {
        const diffs = Array.from(diffState.pendingDiffs.values());
        this._state = {
          ...this._state,
          diffs
        };
        this.update();
      }
    });
    this.subscriptions.push(diffStateSub);

    // Subscribe to allDiffsResolved changes to automatically hide when complete
    const allResolvedSub = diffStateService.allDiffsResolved$.subscribe(
      ({ notebookId }) => {
        const currentState = diffStateService.getCurrentState();
        const hasAnyDiffs = currentState.pendingDiffs.size > 0;

        // If all diffs are resolved and no pending diffs remain, hide the display
        if (!hasAnyDiffs && this._state.state === LLMDisplayState.DIFF) {
          this.hide();
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
   * Render the React component
   */
  render(): JSX.Element {
    this.handleIsVisibleChanges(this._state.isVisible, this._state.state);

    return (
      <LLMStateContent
        isVisible={this._state.isVisible}
        state={this._state.state}
        text={this._state.text}
        toolName={this._state.toolName}
        diffs={this._state.diffs}
        waitingForUser={this._state.waitingForUser}
        isRunContext={this._state.isRunContext}
        onRunClick={this._state.onRunClick}
        onRejectClick={this._state.onRejectClick}
      />
    );
  }

  private handleIsVisibleChanges(
    isVisible: boolean,
    state: LLMDisplayState
  ): void {
    if (
      !isVisible ||
      state === LLMDisplayState.IDLE ||
      (state === LLMDisplayState.DIFF && this._state.diffs?.length === 0)
    ) {
      this.addClass('hidden');
    } else {
      this.removeClass('hidden');
    }
  }

  /**
   * Show the LLM state in generating mode
   * @param text The status text to display
   * @param waitingForUser
   */
  public show(text: string = 'Generating...', waitingForUser?: boolean): void {
    this._state = {
      isVisible: true,
      state: LLMDisplayState.GENERATING,
      text,
      waitingForUser
    };
    this.update();
  }

  /**
   * Show the LLM state in using tool mode with approval buttons
   * @param text Optional custom status text
   * @param onRunClick Optional callback for run action (for notebook-run_cell tool)
   * @param onRejectClick Optional callback for reject action (for notebook-run_cell tool)
   */
  public showRunCellTool(
    onRunClick?: () => void,
    onRejectClick?: () => void
  ): void {
    this._state = {
      isVisible: true,
      state: LLMDisplayState.USING_TOOL,
      text: '',
      toolName: 'notebook-run_cell',
      onRunClick,
      onRejectClick
    };
    this.update();
  }

  /**
   * Show the LLM state in using tool mode
   * @param toolName The name of the tool being used
   * @param text Optional custom status text
   * @param onRunClick Optional callback for run action (for notebook-run_cell tool)
   * @param onRejectClick Optional callback for reject action (for notebook-run_cell tool)
   */
  public showTool(toolName: string, text?: string): void {
    this._state = {
      isVisible: true,
      state: LLMDisplayState.USING_TOOL,
      text: text || '',
      toolName
    };
    this.update();
  }

  /**
   * Show the diff state with pending diffs using DiffStateService
   * @param notebookId Optional ID to filter diffs for a specific notebook
   * @param isRunContext
   */
  public showDiffsWithManager(
    notebookId?: string,
    isRunContext?: boolean
  ): void {
    try {
      // Get diffs from the RxJS service instead of NotebookDiffManager
      const currentState = diffStateService.getCurrentState();
      const diffs = Array.from(currentState.pendingDiffs.values()).filter(
        diff => !notebookId || diff.notebookId === notebookId
      );

      if (diffs.length === 0) {
        this.hide();
        return;
      }

      this._state = {
        isVisible: true,
        state: LLMDisplayState.DIFF,
        text: '',
        diffs,
        isRunContext: isRunContext || false
      };
      this.update();
    } catch (error) {
      console.warn('Could not show diffs with manager:', error);
      this.hide();
    }
  }

  /**
   * Hide the LLM state display and set to idle
   */
  public hide(): void {
    this._state = {
      isVisible: false,
      state: LLMDisplayState.IDLE,
      text: '',
      waitingForUser: false
    };

    this.update();
  }

  /**
   * Public method to show pending diffs
   * @param notebookId Optional ID to filter diffs for a specific notebook
   */
  public showPendingDiffs(
    notebookId?: string | null,
    isRunContext?: boolean
  ): void {
    this.showDiffsWithManager(notebookId || undefined, isRunContext);
  }

  /**
   * Public method to hide pending diffs
   */
  public hidePendingDiffs(): void {
    this.hide();
  }

  /**
   * Check if currently in diff state
   */
  public isDiffState(): boolean {
    return this._state.state === LLMDisplayState.DIFF;
  }

  /**
   * Check if currently in using tool state
   */
  public isUsingToolState(): boolean {
    return this._state.state === LLMDisplayState.USING_TOOL;
  }

  /**
   * Get the widget for adding to layout (for backwards compatibility)
   */
  public getWidget(): Widget {
    return this;
  }
}
