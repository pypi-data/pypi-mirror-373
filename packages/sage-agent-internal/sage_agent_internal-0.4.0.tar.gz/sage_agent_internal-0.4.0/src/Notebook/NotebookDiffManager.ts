import { NotebookTools } from './NotebookTools';
import { ActionHistory, ActionType } from '../Chat/ActionHistory';
import { DiffApprovalDialog } from '../Components/DiffApprovalDialog';
import {
  DiffApprovalStatus,
  IDiffApplicationResult,
  IPendingDiff
} from '../types';
import { Widget } from '@lumino/widgets';
import { ISignal, Signal } from '@lumino/signaling';
import { timeout } from '../utils';
import { AppStateService } from '../AppState';
import { diffStateService } from '../Services/DiffStateService';
import { Subscription } from 'rxjs';

/**
 * Manager for handling notebook diffs and approvals
 */
export class NotebookDiffManager {
  private notebookTools: NotebookTools;
  private actionHistory: ActionHistory;
  private cellIdMapping: Map<string, string> = new Map(); // Map from tracking ID to temporary cell ID after diff display
  public diffApprovalDialog: DiffApprovalDialog;
  private notebookWidget: Widget | null = null;
  private lastUserApprovalTime: number = 0; // Track when the user last approved changes
  private _shouldRunImmediately: boolean = false; // Track if we should run immediately
  private _shouldExecuteApprovedCells: boolean = false; // Track if we should execute all approved cells
  private currentNotebookId: string | null = null;
  private subscriptions: Subscription[] = [];

  // Signal that emits when diff processing is complete
  public _finishedProcessingDiffs = new Signal<this, DiffApprovalStatus>(this);

  /**
   * Signal that emits when diff processing is complete
   */
  get finishedProcessingDiffs(): ISignal<this, DiffApprovalStatus> {
    return this._finishedProcessingDiffs;
  }

  constructor(notebookTools: NotebookTools, actionHistory: ActionHistory) {
    this.notebookTools = notebookTools;
    this.actionHistory = actionHistory;
    this.diffApprovalDialog = new DiffApprovalDialog();

    // Subscribe to DiffStateService changes
    this.setupDiffStateSubscriptions();

    // Set up callbacks for the dialog with direct diff application methods
    this.diffApprovalDialog.setCallbacks({
      onApprove: trackingIds => this.approveDiffs(trackingIds),
      onReject: trackingIds => this.rejectDiffs(trackingIds),
      onApproveAll: notebookId => this.approveAllDiffs(notebookId),
      onRejectAll: notebookId => this.rejectAllDiffs(notebookId),
      applyApprovedDiffs: (...args) => this.applyApprovedDiffs(...args),
      handleRejectedDiffs: notebookId => this.handleRejectedDiffs(notebookId),
      setExecuteApprovedCells: execute => this.setExecuteApprovedCells(execute),
      reapplyDiff: diffCell => this.reapplyDiff(diffCell)
    });
  }

  /**
   * Set up subscriptions to DiffStateService for keeping in sync
   */
  private setupDiffStateSubscriptions(): void {
    // Subscribe to all diff state changes
    this.subscriptions.push(
      diffStateService.diffState$.subscribe(state => {
        // Update current notebook ID if it changes
        if (state.notebookId !== this.currentNotebookId) {
          this.currentNotebookId = state.notebookId || null;
        }
      })
    );
  }

  /**
   * Clean up subscriptions
   */
  public dispose(): void {
    this.subscriptions.forEach(sub => sub.unsubscribe());
    this.subscriptions = [];
  }

  /**
   * Set the notebook widget for better positioning of the diff dialog
   */
  public setNotebookWidget(widget: Widget): void {
    this.notebookWidget = widget;
  }

  /**
   * Set the current notebook ID context
   * @param notebookId ID of the notebook
   */
  public setNotebookId(notebookId: string | null): void {
    if (this.currentNotebookId === notebookId) {
      return; // No change needed
    }

    console.log(
      `[NotebookDiffManager] Setting current notebook ID: ${notebookId}`
    );
    this.currentNotebookId = notebookId;

    // Update DiffStateService with new notebook ID (keeping path method for now)
    diffStateService.setNotebookPath(notebookId);
    this.diffApprovalDialog.updateNotebookPath(notebookId || '');
  }

  /**
   * Get diffs for a specific notebook by filtering the main collection
   * @param notebookId Path to the notebook
   * @returns Array of diffs for the specified notebook path
   */
  private getNotebookDiffs(notebookId?: any): IPendingDiff[] {
    const currentState = diffStateService.getCurrentState();

    // If no path specified, return all diffs
    if (!notebookId) {
      return Array.from(currentState.pendingDiffs.values());
    }

    // Filter diffs by notebook path
    return Array.from(currentState.pendingDiffs.values()).filter(
      (diff: IPendingDiff) => diff.notebookId === notebookId
    );
  }

  /**
   * Get the current approval status from DiffStateService
   */
  private get approvalStatus(): DiffApprovalStatus {
    const currentState = diffStateService.getCurrentState();
    let approved = 0;
    let rejected = 0;
    let total = 0;

    for (const [, diff] of currentState.pendingDiffs) {
      // Only count diffs for current notebook
      if (
        !this.currentNotebookId ||
        diff.notebookId === this.currentNotebookId
      ) {
        total++;
        if (
          diff.approved === true ||
          diff.userDecision === 'approved' ||
          diff.userDecision === 'run'
        ) {
          approved++;
        } else if (
          diff.approved === false ||
          diff.userDecision === 'rejected'
        ) {
          rejected++;
        }
      }
    }

    if (total === 0) return DiffApprovalStatus.PENDING;

    if (approved === total) {
      return DiffApprovalStatus.APPROVED;
    } else if (rejected === total) {
      return DiffApprovalStatus.REJECTED;
    } else if (approved + rejected === total) {
      return DiffApprovalStatus.PARTIAL;
    } else {
      return DiffApprovalStatus.PENDING;
    }
  }

  /**
   * Track a cell addition diff and store its info
   * @param notebookId Optional path to the notebook
   */
  public trackAddCell(
    trackingId: string,
    content: string,
    summary: string,
    notebookId?: string | null
  ): void {
    // Use current notebook path if none specified
    const path = notebookId || this.currentNotebookId;

    const pendingDiff = {
      cellId: trackingId,
      type: 'add' as const,
      newContent: content,
      updatedCellId: trackingId, // Initially the same as trackingId
      metadata: { summary },
      notebookId: path
    };

    // Only add to DiffStateService - no local storage needed
    diffStateService.addPendingDiff(trackingId, pendingDiff);

    console.log(
      `[NotebookDiffManager] Tracked add diff for cell tracking ID ${trackingId} in notebook ${path || 'current'}`
    );
  }

  /**
   * Track a cell edit diff and store its info
   * @param notebookId Optional path to the notebook
   */
  public trackEditCell(
    trackingId: string,
    originalContent: string,
    newContent: string,
    summary: string,
    notebookId?: string | null
  ): void {
    // Use current notebook path if none specified
    const path = notebookId || this.currentNotebookId;

    const pendingDiff = {
      cellId: trackingId,
      type: 'edit' as const,
      originalContent,
      newContent,
      updatedCellId: trackingId, // Initially the same as trackingId
      metadata: { summary },
      notebookId: path
    };

    // Only add to DiffStateService - no local storage needed
    diffStateService.addPendingDiff(trackingId, pendingDiff);

    console.log(
      `[NotebookDiffManager] Tracked edit diff for cell tracking ID ${trackingId} in notebook ${path || 'current'}`
    );
  }

  /**
   * Track a cell removal diff
   * @param notebookId Optional path to the notebook
   */
  public trackRemoveCell(
    trackingId: string,
    originalContent: string,
    summary: string,
    notebookId?: string | null
  ): void {
    // Use current notebook path if none specified
    const path = notebookId || this.currentNotebookId;

    const pendingDiff = {
      cellId: trackingId,
      type: 'remove' as const,
      originalContent,
      newContent: '', // Empty for remove
      metadata: { summary },
      notebookId: path
    };

    // Only add to DiffStateService - no local storage needed
    diffStateService.addPendingDiff(trackingId, pendingDiff);

    console.log(
      `[NotebookDiffManager] Tracked remove diff for cell tracking ID ${trackingId} in notebook ${path || 'current'}`
    );
  }

  /**
   * Update the cell ID mapping when a cell ID changes due to diff display
   * @param notebookId Optional path to the notebook
   */
  public updateCellIdMapping(
    originalCellId: string,
    updatedCellId: string,
    notebookId?: string | null
  ): void {
    // Update the mapping
    this.cellIdMapping.set(originalCellId, updatedCellId);

    // Also update the pending diff record if it exists in the DiffStateService
    const currentState = diffStateService.getCurrentState();
    const diffRecord = currentState.pendingDiffs.get(originalCellId);
    if (diffRecord) {
      const updatedDiff = {
        ...diffRecord,
        updatedCellId: updatedCellId
      };
      diffStateService.addPendingDiff(originalCellId, updatedDiff);
      console.log(
        `[NotebookDiffManager] Updated cell ID mapping: ${originalCellId} → ${updatedCellId}`
      );
    }
  }

  /**
   * Get the current cell model ID using the mapping if available
   * This converts a tracking ID to the current cell model ID
   */
  public getCurrentCellId(trackingId: string): string {
    return this.cellIdMapping.get(trackingId) || trackingId;
  }

  public isDialogOpen(): boolean {
    return this.diffApprovalDialog.isDialogOpen();
  }

  /**
   * Check if there are any pending diffs
   */
  public hasPendingDiffs(): boolean {
    return diffStateService.getPendingDiffCount(this.currentNotebookId) > 0;
  }

  public hasRejectedDiffs(): boolean {
    for (const diff of diffStateService
      .getCurrentState()
      .pendingDiffs.values()) {
      if (diff.userDecision && diff.userDecision === 'rejected') return true;
    }

    return false;
  }

  /**
   * Get the number of pending diffs
   */
  public getPendingDiffCount(): number {
    return diffStateService.getPendingDiffCount(this.currentNotebookId);
  }

  /**
   * Show the diff approval dialog with simplified parameters
   * @param parentElement Parent element to attach the dialog to
   * @param useEmbeddedMode If true, will use embedded styling for chat context
   * @param isRunContext If true, indicates this approval is in the context of running code
   * @param notebookId Optional path to the notebook for filtering diffs
   * @returns Promise resolving to the approval status
   */
  public async showApprovalDialog(
    parentElement: HTMLElement,
    useEmbeddedMode: boolean = false,
    isRunContext: boolean = false,
    notebookId?: string | null
  ): Promise<DiffApprovalStatus> {
    console.log(
      '[NotebookDiffManager] Showing approval dialog for current notebook'
    );

    console.log(
      `[NotebookDiffManager] Notebook ID: ${notebookId || this.currentNotebookId}`
    );

    // Use provided notebook path or fall back to current notebook path
    const targetNotebookPath =
      notebookId !== undefined ? notebookId : this.currentNotebookId;

    // Get diffs from DiffStateService for target notebook
    const diffs = this.getNotebookDiffs(targetNotebookPath);

    console.log(diffs);

    if (diffs.length === 0) {
      console.log(
        '[NotebookDiffManager] No diffs to approve for target notebook'
      );
      // Emit signal immediately for no diffs case
      const status = DiffApprovalStatus.APPROVED;
      this._finishedProcessingDiffs.emit(status);
      return status;
    }

    // Before showing the dialog, ensure we're showing the diff displays
    await this.displayDiffsInCells(targetNotebookPath);

    // Use notebook element as parent if available, otherwise document.body
    const notebookElement = this.notebookWidget
      ? this.notebookWidget.node
      : document.body;

    // Choose the parent element based on the mode
    const dialogParent = useEmbeddedMode ? parentElement : notebookElement;

    // Show the dialog and wait for it to complete
    console.log('[NotebookDiffManager] Showing Dialog');

    const result = await this.diffApprovalDialog.showDialog(
      dialogParent,
      targetNotebookPath,
      useEmbeddedMode,
      isRunContext
    );

    // Store the run immediately flag if present
    if (result.runImmediately) {
      this._shouldRunImmediately = true;
      this._shouldExecuteApprovedCells = true;
    }

    // Return the current approval status
    return this.approvalStatus;
  }

  /**
   * Show approval dialog specifically for cancellation scenario
   * This version shows the dialog with only approve/reject options (no run option)
   * @param parentElement Parent element for the dialog
   * @param notebookId Path to the notebook for filtering diffs
   * @returns Promise resolving to approval status
   */
  public async showCancellationApprovalDialog(
    parentElement: HTMLElement,
    notebookId?: string | null
  ): Promise<DiffApprovalStatus> {
    // Use current notebook path if none specified
    const path = notebookId || this.currentNotebookId;

    // Check if there are any diffs for this notebook path
    const diffs = this.getNotebookDiffs(path);
    if (diffs.length === 0) {
      const status = DiffApprovalStatus.APPROVED; // No diffs to approve
      this._finishedProcessingDiffs.emit(status);
      return status;
    }

    // Before showing the dialog, ensure we're showing the diff displays
    await this.displayDiffsInCells(path);

    // Use notebook element as parent if available, otherwise document.body
    const notebookElement = this.notebookWidget
      ? this.notebookWidget.node
      : document.body;

    // Choose the parent element based on embedded mode for chat context
    const dialogParent = parentElement;

    // Show the dialog and wait for it to complete - explicitly set isRunContext to false
    // since this is post-cancellation and shouldn't have a run option
    const result = await this.diffApprovalDialog.showDialog(
      dialogParent,
      path,
      true, // Use embedded mode for chat context
      false // Not a run context - no "run" option
    );

    // Get the approval status and emit the signal
    const approvalStatus = this.approvalStatus;
    this._finishedProcessingDiffs.emit(approvalStatus);

    // Return the current approval status
    return approvalStatus;
  }

  /**
   * Display diffs in their respective cells if they aren't already displayed
   * @param notebookId Optional path to the notebook containing the cells
   */
  private async displayDiffsInCells(notebookId?: string | null): Promise<void> {
    const path = notebookId || this.currentNotebookId;
    const diffs = this.getNotebookDiffs(path);

    for (const diff of diffs) {
      await timeout(200);

      // Skip if already displayed
      if (diff.updatedCellId && diff.updatedCellId !== diff.cellId) {
        continue; // Already displayed
      }

      try {
        // Find the cell by tracking ID in the specific notebook
        const cellInfo = this.notebookTools.findCellByAnyId(diff.cellId, path);
        if (!cellInfo) {
          console.warn(
            `Cannot find cell with tracking ID ${diff.cellId} in notebook ${path || 'current'} to display diff`
          );
          continue;
        }

        // Display the diff based on the operation type
        if (diff.type === 'add') {
          const diffResult = this.notebookTools.display_diff(
            cellInfo.cell,
            '', // Original content is empty for new cells
            diff.newContent || '',
            'add'
          );
        } else if (diff.type === 'edit') {
          const diffResult = this.notebookTools.display_diff(
            cellInfo.cell,
            diff.originalContent || '',
            diff.newContent || '',
            'edit'
          );
        } else if (diff.type === 'remove') {
          const diffResult = this.notebookTools.display_diff(
            cellInfo.cell,
            diff.originalContent || '',
            '', // New content is empty for removes
            'remove'
          );
        }
      } catch (error) {
        console.error(
          `Error displaying diff for cell ${diff.cellId} in notebook ${path}:`,
          error
        );
      }
    }
  }

  /**
   * Approve specific diffs by cell IDs
   */
  private approveDiffs(cellIds: string[]): void {
    const currentState = diffStateService.getCurrentState();

    for (const cellId of cellIds) {
      const diff = currentState.pendingDiffs.get(cellId);
      if (diff) {
        // Update DiffStateService
        diffStateService.updateDiffState(cellId, true, diff.notebookId);
      }
    }
  }

  /**
   * Reject specific diffs by cell IDs
   */
  private rejectDiffs(cellIds: string[]): void {
    const currentState = diffStateService.getCurrentState();

    for (const cellId of cellIds) {
      const diff = currentState.pendingDiffs.get(cellId);
      if (diff) {
        // Update DiffStateService
        diffStateService.updateDiffState(cellId, false, diff.notebookId);
      }
    }
  }

  /**
   * Approve all pending diffs
   * @param notebookId Optional path to the notebook to approve diffs for
   */
  private approveAllDiffs(notebookId: string | null = null): void {
    // Get diffs for the specified notebook or all diffs
    const diffs = this.getNotebookDiffs(notebookId);

    // Set approved flag on all diffs
    for (const diff of diffs) {
      // Update DiffStateService
      diffStateService.updateDiffState(diff.cellId, true, diff.notebookId);
    }
  }

  /**
   * Reject all pending diffs
   * @param notebookId Optional path to the notebook to reject diffs for
   */
  public rejectAllDiffs(notebookId: string | null = null): void {
    // Get diffs for the specified notebook or all diffs
    const diffs = this.getNotebookDiffs(notebookId);

    // Set rejected flag on all diffs
    for (const diff of diffs) {
      if (diff.userDecision === 'approved' || diff.userDecision === 'run')
        continue;
      // Update DiffStateService
      diffStateService.updateDiffState(diff.cellId, false, diff.notebookId);
    }
  }

  public rejectCellDiff(cellId: string): void {
    const diff = diffStateService.getCurrentState().pendingDiffs.get(cellId);
    if (diff && diff.approved !== false) {
      diffStateService.updateDiffState(cellId, false, diff.notebookId);
      this.handleRejectedDiffs(diff.notebookId);
    }
  }

  public reapplyDiff(diffCell: IPendingDiff): void {
    if (diffCell.type !== 'edit') return;

    diffStateService.addPendingDiff(diffCell.cellId, {
      ...diffCell,
      approved: undefined,
      userDecision: undefined
    });
    this.displayDiffsInCells(diffCell.notebookId);
    const llmStateDisplay =
      AppStateService.getChatContainerSafe()?.chatWidget.llmStateDisplay;
    if (llmStateDisplay) {
      llmStateDisplay.showPendingDiffs(diffCell.notebookId, true);
    }

    // Also show diffs in DiffNavigationWidget for synchronized display
    const diffNavigationWidget = AppStateService.getDiffNavigationWidgetSafe();
    if (diffNavigationWidget) {
      diffNavigationWidget.showPendingDiffs(diffCell.notebookId, true);
    }
  }

  /**
   * Apply all approved diffs
   * @param notebookId Optional path to the notebook containing the cells
   * @param trackingIds Optional array of tracking IDs to apply diffs for
   * @returns Promise resolving to a result object with success status and approval status
   */
  public async applyApprovedDiffs(
    notebookId?: string | null,
    trackingIds?: string[]
  ): Promise<IDiffApplicationResult> {
    const path = notebookId || this.currentNotebookId;

    // Get approved diffs from DiffStateService
    const approvedDiffs = this.getNotebookDiffs(path).filter(
      diff => diff.approved === true
    );

    console.log(
      `[NotebookDiffManager] Applying ${approvedDiffs.length} approved diffs in notebook ${path || 'current'}`
    );

    try {
      for (const diff of approvedDiffs) {
        await timeout(100);
        const trackingId = diff.cellId; // This is the tracking ID
        // The updatedCellId may be a temporary model ID after displaying diff
        const tempModelId =
          diff.updatedCellId !== diff.cellId ? diff.updatedCellId : undefined;

        const shouldApply = !trackingIds || trackingIds.includes(trackingId);
        if (!shouldApply) {
          continue;
        }

        console.log('Searching for cell with tracking ID:', trackingId);

        // First try to find cell by tracking ID
        let cellInfo = this.notebookTools.findCellByAnyId(trackingId, path);

        if (!cellInfo) {
          console.error(
            `[NotebookDiffManager] Cannot find cell with tracking ID ${trackingId} in notebook ${path || 'current'} to apply diff`
          );
          continue;
        }

        // Apply the diff based on type
        if (diff.type === 'add' || diff.type === 'edit') {
          // For add and edit, apply directly to the found cell
          const result = this.notebookTools.apply_diff(cellInfo.cell, true);
          if (!result.success) {
            console.error(
              `[NotebookDiffManager] Failed to apply diff to cell with tracking ID ${trackingId}`
            );
            continue;
          }

          // Add to action history with tracking ID for reliable reference
          this.actionHistory.addAction(
            diff.type === 'add' ? ActionType.ADD_CELL : ActionType.EDIT_CELL,
            {
              trackingId: trackingId,
              originalContent: diff.originalContent,
              newContent: diff.newContent,
              summary: diff.metadata?.summary
            },
            `${diff.type === 'add' ? 'Added' : 'Edited'} cell: ${diff.metadata?.summary || trackingId}`
          );
        } else if (diff.type === 'remove') {
          // Add to action history
          this.actionHistory.addAction(
            ActionType.REMOVE_CELLS,
            {
              trackingIds: [trackingId],
              removedCells: [
                {
                  content: diff.originalContent,
                  type: cellInfo.cell.model.type,
                  custom: diff.metadata
                }
              ]
            },
            `Removed cell: ${diff.metadata?.summary || trackingId}`
          );

          this.notebookTools.remove_cells({
            cell_ids: [trackingId],
            remove_from_notebook: true
          });
        }
      }

      return {
        success: true,
        status: this.approvalStatus
      };
    } catch (error) {
      console.error('Error applying approved diffs:', error);
      return {
        success: false,
        status: this.approvalStatus
      };
    }
  }

  /**
   * Handle rejected diffs (revert them)
   * @param notebookId Optional path to the notebook containing the cells
   * @returns Promise resolving to a result object with success status and approval status
   */
  public async handleRejectedDiffs(
    notebookId?: string | null
  ): Promise<IDiffApplicationResult> {
    const path = notebookId || this.currentNotebookId;

    // Get rejected diffs from DiffStateService
    const rejectedDiffs = this.getNotebookDiffs(path).filter(
      diff => diff.approved === false
    );

    console.log(
      `[NotebookDiffManager] Handling ${rejectedDiffs.length} rejected diffs in notebook ${path || 'current'}`
    );

    try {
      for (const diff of rejectedDiffs) {
        const trackingId = diff.cellId; // This is the tracking ID
        const tempModelId =
          diff.updatedCellId !== diff.cellId ? diff.updatedCellId : undefined;

        // First try to find cell by tracking ID
        let cellInfo = this.notebookTools.findCellByAnyId(trackingId, path);

        // If not found and we have a temporary model ID, try that as fallback
        if (!cellInfo && tempModelId) {
          cellInfo = this.notebookTools.findCellByAnyId(tempModelId);
        }

        if (!cellInfo) {
          console.error(
            `[NotebookDiffManager] Cannot find cell with tracking ID ${trackingId} in notebook ${path || 'current'} to reject diff`
          );
          continue;
        }

        // Handle based on diff type
        if (diff.type === 'add') {
          // For rejected adds, remove the cell
          this.notebookTools.remove_cells({
            cell_ids: [trackingId],
            remove_from_notebook: true
          });
        } else if (diff.type === 'edit') {
          // For rejected edits, revert to original content
          const success = this.notebookTools.apply_diff(cellInfo.cell, false);
          if (!success) {
            console.error(
              `[NotebookDiffManager] Failed to reject diff for cell with tracking ID ${trackingId}`
            );
          }
        } else if (diff.type === 'remove') {
          const success = this.notebookTools.apply_diff(cellInfo.cell, false);
          if (!success) {
            console.error(
              `[NotebookDiffManager] Failed to reject diff for cell with tracking ID ${trackingId}`
            );
          }
        }
      }

      // // // Clear the rejected diffs from DiffStateService
      // // for (const diff of rejectedDiffs) {
      // //   diffStateService.removePendingDiff(diff.cellId, diff.notebookId);
      // // }
      //
      // // Clear mappings related to rejected diffs
      // for (const [trackingId, _] of this.cellIdMapping) {
      //   const currentState = diffStateService.getCurrentState();
      //   if (!currentState.pendingDiffs.has(trackingId)) {
      //     this.cellIdMapping.delete(trackingId);
      //   }
      // }

      return {
        success: true,
        status: this.approvalStatus
      };
    } catch (error) {
      console.error('Error handling rejected diffs:', error);
      return {
        success: false,
        status: this.approvalStatus
      };
    }
  }

  public approveCellDiff(cellId: string): void {
    const diff = diffStateService.getCurrentState().pendingDiffs.get(cellId);
    if (diff && !diff.approved) {
      diffStateService.updateDiffState(cellId, true, diff.notebookId);
      this.applyApprovedDiffs(diff.notebookId);
    }
  }

  /**
   * Clear all pending diffs
   */
  public clearDiffs(): void {
    this.cellIdMapping.clear();

    // Clear from DiffStateService
    diffStateService.clearAllDiffs(this.currentNotebookId);

    console.log('[NotebookDiffManager] All diffs cleared');
  }

  /**
   * Force revert all diffs and reject them
   */
  public rejectAndRevertDiffsImmediately(): void {
    this.rejectAllDiffs();
    this.handleRejectedDiffs();
  }

  /**
   * Check if we should run code immediately after approval
   * This flag is set when "Approve All and Run" is clicked
   * and should be consumed after checking once
   */
  public shouldRunImmediately(): boolean {
    const should = this._shouldRunImmediately;
    this._shouldRunImmediately = false; // Consume the flag
    return should;
  }

  /**
   * Get all approved cell IDs (tracking IDs)
   * @param notebookId Optional path to filter by notebook
   * @returns Array of approved cell tracking IDs
   */
  public getApprovedCellIds(notebookId?: string | null): string[] {
    const path = notebookId || this.currentNotebookId;
    const approvedCells = this.getNotebookDiffs(path).filter(
      diff =>
        diff.userDecision &&
        diff.userDecision !== 'rejected' &&
        (diff.type === 'add' || diff.type === 'edit') // Only include cells that can be executed
    );

    return approvedCells.map(diff => diff.cellId);
  }

  /**
   * Set the flag to execute all approved cells
   */
  public setExecuteApprovedCells(execute: boolean): void {
    this._shouldExecuteApprovedCells = execute;
  }

  /**
   * Wait for diff processing to complete via signal
   * @returns Promise resolving to the approval status when processing is done
   */
  public waitForDiffProcessingComplete(): Promise<DiffApprovalStatus> {
    return new Promise<DiffApprovalStatus>(resolve => {
      // Create a one-time handler function
      const handleFinished = (sender: this, status: DiffApprovalStatus) => {
        // Disconnect the signal after first use
        this._finishedProcessingDiffs.disconnect(handleFinished);
        resolve(status);
      };

      // Connect the handler to the signal
      this._finishedProcessingDiffs.connect(handleFinished);
    });
  }

  /**
   * Start the diff approval process without waiting for completion
   * This triggers the dialog display and processing, but doesn't block
   * @param parentElement Parent element to attach the dialog to
   * @param useEmbeddedMode If true, will use embedded styling for chat context
   * @param isRunContext If true, indicates this approval is in the context of running code
   * @param notebookId Optional path to the notebook for filtering diffs
   */
  public startDiffApprovalProcess(
    parentElement: HTMLElement,
    useEmbeddedMode: boolean = false,
    isRunContext: boolean = false,
    notebookId?: string | null
  ): void {
    // Start the approval process without waiting
    this.showApprovalDialog(
      parentElement,
      useEmbeddedMode,
      isRunContext,
      notebookId
    ).catch(error => {
      console.error('[NotebookDiffManager] Error during diff approval:', error);
      // Emit a rejection status on error
      this._finishedProcessingDiffs.emit(DiffApprovalStatus.REJECTED);
    });
  }
}
