import * as React from 'react';
import { IPendingDiff } from '../../types';
import { DiffItemProps } from './types';
import { AppStateService } from '../../AppState';
import { diffStateService } from '../../Services/DiffStateService';
import { RUN_CELL_ICON } from './icons';
import { REAPPLY_ICON } from '../icons';
import { NotebookDiffTools } from '../../Notebook/NotebookDiffTools';

/**
 * Spinner component for running state
 */
const Spinner: React.FC = () => (
  <div
    className="sage-ai-diff-spinner"
    style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      width: '16px',
      height: '16px',
      border: '2px solid #f3f3f3',
      borderTop: '2px solid #3498db',
      borderRadius: '50%',
      animation: 'spin 1s linear infinite'
    }}
  />
);

/**
 * Component for displaying individual diff item
 */
export function DiffItem({
  diff,
  showActionsOnHover = false
}: DiffItemProps): JSX.Element {
  const [diffState, setDiffState] = React.useState(diff);

  // Subscribe to diff state changes from DiffStateService using RxJS
  React.useEffect(() => {
    const subscription = diffStateService
      .getCellStateChanges$(diff.cellId)
      .subscribe(stateChange => {
        if (stateChange && stateChange.cellId === diff.cellId) {
          // Update the local state to reflect the new decision
          setDiffState(prev => {
            const currentState = diffStateService.getCurrentState();
            const currentDiff = currentState.pendingDiffs.get(diff.cellId);

            return {
              ...prev,
              approved: stateChange.approved,
              userDecision: currentDiff?.userDecision,
              runResult: currentDiff?.runResult
            };
          });
        }
      });

    // Also subscribe to the full diff state to catch runResult updates
    const fullStateSubscription = diffStateService.diffState$.subscribe(
      state => {
        const currentDiff = state.pendingDiffs.get(diff.cellId);
        if (currentDiff) {
          setDiffState(prev => ({
            ...prev,
            userDecision: currentDiff.userDecision,
            runResult: currentDiff.runResult,
            approved: currentDiff.approved
          }));
        }
      }
    );

    return () => {
      subscription.unsubscribe();
      fullStateSubscription.unsubscribe();
    };
  }, [diff.cellId]);

  const getLineChanges = (
    diff: IPendingDiff
  ): { added: number; removed: number } => {
    if (diff.type === 'add') {
      // For new cells, count all lines as added
      const newLines = diff.newContent?.split('\n').length || 0;
      return { added: newLines, removed: 0 };
    } else if (diff.type === 'remove') {
      // For removed cells, count all lines as removed
      const originalLines = diff.originalContent?.split('\n').length || 0;
      return { added: 0, removed: originalLines };
    } else if (diff.type === 'edit') {
      const diffLines = NotebookDiffTools.calculateDiff(
        diff.originalContent || '',
        diff.newContent || ''
      );
      const added = diffLines.filter(line => line.type === 'added').length;
      const removed = diffLines.filter(line => line.type === 'removed').length;

      return { added, removed };
    }
    return { added: 0, removed: 0 };
  };

  const { added, removed } = getLineChanges(diffState);
  const getOperationIcon = (type: string) => {
    switch (type) {
      case 'add':
        return '+';
      case 'edit':
        return '~';
      case 'remove':
        return '−';
      default:
        return '?';
    }
  };

  const isDecisionMade =
    diffState.userDecision !== null && diffState.userDecision !== undefined;
  const isRunning = diffState.userDecision === 'run' && !diffState.runResult;
  const isEditDiff = diffState.type === 'edit';

  // Add CSS animation for spinner if not already added
  React.useEffect(() => {
    if (!document.querySelector('#sage-ai-spinner-animation')) {
      const style = document.createElement('style');
      style.id = 'sage-ai-spinner-animation';
      style.textContent = `
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `;
      document.head.appendChild(style);
    }
  }, []);

  return (
    <div
      className={`sage-ai-diff-item ${showActionsOnHover ? 'sage-ai-diff-item-hover-actions' : ''}`}
      onClick={() => {
        AppStateService.getNotebookTools().scrollToCellById(diffState.cellId);
      }}
    >
      <div className="sage-ai-diff-info">
        <span
          className={`sage-ai-diff-operation sage-ai-diff-${diffState.type}`}
        >
          {getOperationIcon(diffState.type)}
        </span>
        <span className="sage-ai-diff-summary">{diffState.cellId}</span>
        <div className="sage-ai-diff-changes">
          {added > 0 && <span className="sage-ai-diff-added">+{added}</span>}
          {removed > 0 && (
            <span className="sage-ai-diff-removed">−{removed}</span>
          )}
          {isDecisionMade && (
            <span
              className={`sage-ai-diff-decision sage-ai-diff-decision-${diffState.userDecision}`}
            >
              {diffState.userDecision === 'approved' ? (
                '✓'
              ) : diffState.userDecision === 'rejected' ? (
                '✕'
              ) : diffState.userDecision === 'run' ? (
                <RUN_CELL_ICON.react className={'fix_run_cell_size'} />
              ) : (
                '?'
              )}
            </span>
          )}
        </div>
      </div>

      {isDecisionMade && isEditDiff && (
        <div className="sage-ai-diff-actions">
          <button
            onClick={() => {
              AppStateService.getNotebookDiffManager().reapplyDiff(diffState);
            }}
            className="sage-ai-diff-btn sage-ai-diff-reapply"
          >
            <REAPPLY_ICON.react />
          </button>
        </div>
      )}

      {!isDecisionMade && !isRunning && (
        <div className="sage-ai-diff-actions">
          <button
            className="sage-ai-diff-btn sage-ai-diff-reject"
            onClick={() => {
              // Update diff state using RxJS service
              diffStateService.updateDiffState(
                diffState.cellId,
                false,
                diffState.notebookId
              );
              // Also trigger the dialog action if needed
              AppStateService.getNotebookDiffManager().diffApprovalDialog.rejectCell(
                diffState.cellId
              );
            }}
            disabled={isDecisionMade}
            title="Reject this change"
          >
            ✕
          </button>
          <button
            className="sage-ai-diff-btn sage-ai-diff-approve"
            onClick={() => {
              // Update diff state using RxJS service
              diffStateService.updateDiffState(
                diffState.cellId,
                true,
                diffState.notebookId
              );
              // Also trigger the dialog action if needed
              AppStateService.getNotebookDiffManager().diffApprovalDialog.approveCell(
                diffState.cellId
              );
            }}
            disabled={isDecisionMade}
            title="Approve this change"
          >
            ✓
          </button>
          <button
            className="sage-ai-diff-btn sage-ai-diff-run"
            onClick={() => {
              // Also trigger the dialog action if needed
              AppStateService.getNotebookDiffManager().diffApprovalDialog.runCell(
                diffState.cellId
              );
            }}
            disabled={isDecisionMade}
            title="Apply this change and run the cell immediately"
          >
            <RUN_CELL_ICON.react />
          </button>
        </div>
      )}

      {/* Show spinner when cell is running */}
      {isRunning && (
        <div className="sage-ai-diff-actions">
          <Spinner />
        </div>
      )}
    </div>
  );
}
