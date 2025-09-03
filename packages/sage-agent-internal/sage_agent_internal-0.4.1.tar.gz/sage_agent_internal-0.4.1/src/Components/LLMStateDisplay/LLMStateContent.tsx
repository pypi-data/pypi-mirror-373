import * as React from 'react';
import { ILLMState, LLMDisplayState } from './types';
import { DiffItem } from './DiffItem';
import { AppStateService } from '../../AppState';
import { IPendingDiff } from '../../types';
import { MENU_CLOSE_ICON, MENU_ICON } from './icons';
import { getToolDisplayMessage, getToolIcon } from '../../utils/toolDisplay';
import { diffStateService } from '../../Services/DiffStateService';
import { NotebookDiffTools } from '../../Notebook/NotebookDiffTools';

/**
 * React component for displaying LLM processing state content
 */
export function LLMStateContent({
  isVisible,
  state,
  text,
  toolName,
  diffs,
  waitingForUser,
  isRunContext,
  onRunClick,
  onRejectClick
}: ILLMState): JSX.Element | null {
  const [isExpanded, setIsExpanded] = React.useState(false);
  const [allDiffsResolved, setAllDiffsResolved] = React.useState(false);
  const [currentDiffs, setCurrentDiffs] = React.useState<IPendingDiff[]>(
    diffs || []
  );

  // Subscribe to diff state changes from DiffStateService
  React.useEffect(() => {
    const subscription = diffStateService.diffState$.subscribe(diffState => {
      const newDiffs = Array.from(diffState.pendingDiffs.values());
      setCurrentDiffs(newDiffs);

      // Check if all diffs are resolved
      if (newDiffs.length > 0) {
        const allDecided = newDiffs.every(
          diff =>
            diff.userDecision === 'approved' ||
            diff.userDecision === 'rejected' ||
            diff.userDecision === 'run' ||
            diff.approved === true ||
            diff.approved === false
        );
        setAllDiffsResolved(allDecided);
      } else {
        setAllDiffsResolved(false);
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  // Also listen for changes in the passed diffs prop for backwards compatibility
  React.useEffect(() => {
    if (diffs && diffs.length > 0) {
      setCurrentDiffs(diffs);
      // Check if all diffs have decisions (approved, rejected, or run)
      const allDecided = diffs.every(
        diff =>
          diff.userDecision === 'approved' ||
          diff.userDecision === 'rejected' ||
          diff.userDecision === 'run' ||
          diff.approved === true ||
          diff.approved === false
      );
      setAllDiffsResolved(allDecided);
    } else if (diffs && diffs.length === 0) {
      setCurrentDiffs([]);
      setAllDiffsResolved(false);
    }
  }, [diffs]);

  // Helper function to calculate total additions and deletions
  const calculateTotals = (diffs: IPendingDiff[]) => {
    let totalAdded = 0;
    let totalRemoved = 0;

    diffs.forEach(diff => {
      const oldLines = diff.originalContent?.split('\n') || [];
      const oldLinesCount = oldLines.length;
      const newLines = diff.newContent?.split('\n') || [];
      const newLinesCount = newLines.length;

      if (diff.type === 'add') {
        totalAdded += newLinesCount;
      } else if (diff.type === 'remove') {
        totalRemoved += oldLinesCount;
      } else if (diff.type === 'edit') {
        const diffLines = NotebookDiffTools.calculateDiff(
          diff.originalContent || '',
          diff.newContent || ''
        );
        totalAdded += diffLines.filter(line => line.type === 'added').length;
        totalRemoved += diffLines.filter(
          line => line.type === 'removed'
        ).length;
      }
    });

    return { totalAdded, totalRemoved };
  };

  // Use currentDiffs for display instead of the prop diffs
  const displayDiffs = currentDiffs.length > 0 ? currentDiffs : diffs || [];
  console.log('DISPLAY DIFFS:', displayDiffs);
  if (!isVisible) {
    return null;
  }

  // Idle state - don't show anything
  if (state === LLMDisplayState.IDLE) {
    return null;
  }

  // Generating state - show thinking indicator
  if (state === LLMDisplayState.GENERATING) {
    return (
      <div
        className="sage-ai-llm-state-display sage-ai-generating"
        style={{ display: 'flex' }}
      >
        <div className="sage-ai-llm-state-content">
          {waitingForUser && <div className="sage-ai-waiting-for-user" />}
          {!waitingForUser && <div className="sage-ai-blob-loader" />}
          <span className="sage-ai-llm-state-text">{text}</span>
        </div>

        {!waitingForUser && (
          <button
            className="sage-ai-llm-state-stop-button"
            onClick={() => {
              AppStateService.getChatContainerSafe()?.chatWidget.cancelMessage();
            }}
            title="Stop generation"
          >
            Stop
          </button>
        )}
      </div>
    );
  }

  // Using tool state - show tool usage indicator
  if (state === LLMDisplayState.USING_TOOL) {
    const toolIcon = toolName ? getToolIcon(toolName) : null;
    const toolMessage = toolName
      ? getToolDisplayMessage(toolName)
      : text || 'Using tool...';

    // Check if this is the notebook-run_cell tool that needs confirmation
    const isRunCellTool = toolName === 'notebook-run_cell';

    return (
      <div
        className="sage-ai-llm-state-display sage-ai-using-tool"
        style={{ display: 'flex' }}
      >
        <div className="sage-ai-llm-state-content">
          {toolIcon ? (
            <div
              className="sage-ai-tool-icon-container"
              dangerouslySetInnerHTML={{ __html: toolIcon }}
            />
          ) : (
            <div className="sage-ai-tool-loader" />
          )}
          <span className="sage-ai-llm-state-text">
            {isRunCellTool ? 'Waiting to run cell...' : toolMessage}
          </span>
        </div>

        <div className="sage-ai-llm-state-buttons">
          {isRunCellTool && onRunClick && onRejectClick ? (
            // Show Run/Reject buttons for notebook-run_cell tool
            <>
              <button
                className="sage-ai-llm-state-reject-button"
                onClick={onRejectClick}
                title="Reject code execution"
              >
                Reject
              </button>
              <button
                className="sage-ai-llm-state-run-button"
                onClick={onRunClick}
                title="Run code (Cmd/Ctrl + Enter)"
              >
                Run
              </button>
            </>
          ) : (
            // Show Stop button for other tools
            <button
              className="sage-ai-llm-state-stop-button"
              onClick={() => {
                AppStateService.getChatContainerSafe()?.chatWidget.cancelMessage();
              }}
              title="Stop tool execution"
            >
              Stop
            </button>
          )}
        </div>
      </div>
    );
  }

  // Diff state - show diff review interface
  if (
    state === LLMDisplayState.DIFF &&
    displayDiffs &&
    displayDiffs.length > 0
  ) {
    const { totalAdded, totalRemoved } = calculateTotals(displayDiffs);

    return (
      <div className="sage-ai-llm-state-display sage-ai-diff-state">
        <div
          className="sage-ai-diff-summary-bar"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <div className="sage-ai-diff-summary-info">
            <span className="sage-ai-diff-icon">
              {!isExpanded ? (
                <MENU_ICON.react className="sage-ai-diff-menu-icon" />
              ) : (
                <MENU_CLOSE_ICON.react className="sage-ai-diff-menu-icon" />
              )}
            </span>
            <span className="sage-ai-diff-cell-count">
              {displayDiffs.length} cell{displayDiffs.length !== 1 ? 's' : ''}{' '}
              modified
            </span>
            <p className="sage-ai-diff-cell-count-info">
              {totalAdded > 0 && (
                <span className="sage-ai-diff-added-count">+{totalAdded}</span>
              )}
              {totalRemoved > 0 && (
                <span className="sage-ai-diff-removed-count">
                  -{totalRemoved}
                </span>
              )}
            </p>
          </div>
          <div className="sage-ai-diff-summary-actions">
            {!allDiffsResolved && (
              <>
                <button
                  className="sage-ai-diff-btn sage-ai-diff-reject-all"
                  onClick={async e => {
                    e.stopPropagation();
                    // Reject all diffs using DiffStateService
                    for (const diff of displayDiffs) {
                      diffStateService.updateDiffState(
                        diff.cellId,
                        false,
                        diff.notebookId
                      );
                    }
                    // Also trigger the dialog action if needed
                    await AppStateService.getNotebookDiffManager().diffApprovalDialog.rejectAll();
                    setAllDiffsResolved(true);
                  }}
                  title={`Reject${diffs && diffs.length > 1 ? ' all' : ''} change${diffs && diffs.length > 1 ? 's' : ''}`}
                >
                  {diffs && diffs.length > 1 ? 'Reject All' : 'Reject'}
                </button>
                <button
                  className="sage-ai-diff-btn sage-ai-diff-approve-all"
                  onClick={async e => {
                    e.stopPropagation();

                    if (isRunContext) {
                      for (const diff of displayDiffs) {
                        if (!diff.userDecision) {
                          await AppStateService.getNotebookDiffManager().diffApprovalDialog.runCell(
                            diff.cellId
                          );
                        }
                      }
                    } else {
                      await AppStateService.getNotebookDiffManager().diffApprovalDialog.approveAll();
                    }
                    setAllDiffsResolved(true);
                  }}
                  title={
                    isRunContext
                      ? `Run${diffs && diffs.length > 1 ? ' all' : ''} change${diffs && diffs.length > 1 ? 's' : ''}`
                      : `Approve${diffs && diffs.length > 1 ? 'all' : ''} change${diffs && diffs.length > 1 ? 's' : ''}`
                  }
                >
                  {isRunContext
                    ? `${diffs && diffs.length > 1 ? 'Run All' : 'Run'}`
                    : 'Approve All'}
                </button>
              </>
            )}
          </div>
        </div>
        {isExpanded && (
          <div className="sage-ai-diff-list">
            {displayDiffs.map((diff, index) => (
              <DiffItem
                key={`${diff.cellId}-${index}`}
                diff={diff}
                showActionsOnHover={true}
              />
            ))}
          </div>
        )}
      </div>
    );
  }

  return null;
}
