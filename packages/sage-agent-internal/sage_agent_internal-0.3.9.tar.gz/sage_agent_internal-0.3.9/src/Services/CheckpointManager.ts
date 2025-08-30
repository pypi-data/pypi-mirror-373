import {
  IChatMessage,
  ICheckpoint,
  CheckpointRestorationOption
} from '../types';
import { MentionContext } from '../Chat/ChatContextMenu/ChatContextMenu';
import {
  NotebookCellStateService,
  ICachedCellState
} from './NotebookCellStateService';
import { ActionHistory } from '../Chat/ActionHistory';

/**
 * Service for managing checkpoints in the chat conversation
 * Checkpoints capture the state at user message points for potential restoration
 */
export class CheckpointManager {
  private static instance: CheckpointManager;
  private checkpoints: Map<string, ICheckpoint[]> = new Map(); // notebookId -> checkpoints
  private currentNotebookId: string | null = null;

  private constructor() {}

  public static getInstance(): CheckpointManager {
    if (!CheckpointManager.instance) {
      CheckpointManager.instance = new CheckpointManager();
    }
    return CheckpointManager.instance;
  }

  /**
   * Set the current notebook ID
   */
  public setCurrentNotebookId(notebookId: string): void {
    this.currentNotebookId = notebookId;
    console.log('[CheckpointManager] Set current notebook ID:', notebookId);
  }

  /**
   * Create a checkpoint at the current user message
   */
  public createCheckpoint(
    userMessage: string,
    messageHistory: IChatMessage[],
    contexts: Map<string, MentionContext>,
    actionHistory?: ActionHistory
  ): ICheckpoint {
    if (!this.currentNotebookId) {
      throw new Error('No current notebook ID set');
    }

    const checkpoint: ICheckpoint = {
      id: `checkpoint_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: Date.now(),
      userMessage,
      messageHistory: [...messageHistory], // Deep copy
      notebookState: this.captureNotebookState(),
      contexts: new Map(contexts), // Deep copy
      notebookId: this.currentNotebookId,
      actionHistory: [...(actionHistory?.getAllActions() || [])] // Deep copy of action history
    };

    // Store checkpoint for this notebook
    if (!this.checkpoints.has(this.currentNotebookId)) {
      this.checkpoints.set(this.currentNotebookId, []);
    }

    const notebookCheckpoints = this.checkpoints.get(this.currentNotebookId)!;
    notebookCheckpoints.push(checkpoint);

    console.log('[CheckpointManager] Created checkpoint:', checkpoint.id);
    console.log(
      '[CheckpointManager] Total checkpoints for notebook:',
      notebookCheckpoints.length
    );
    console.log(
      '[CheckpointManager] Captured',
      checkpoint.actionHistory.length,
      'actions'
    );

    return checkpoint;
  }

  /**
   * Get all checkpoints for the current notebook
   */
  public getCheckpoints(): ICheckpoint[] {
    if (!this.currentNotebookId) {
      return [];
    }
    return this.checkpoints.get(this.currentNotebookId) || [];
  }

  /**
   * Clear all checkpoints for the current notebook
   */
  public clearCheckpoints(): void {
    if (this.currentNotebookId) {
      this.checkpoints.delete(this.currentNotebookId);
      console.log(
        '[CheckpointManager] Cleared checkpoints for notebook:',
        this.currentNotebookId
      );
    }
  }

  /**
   * Clear checkpoints after a specific checkpoint (for restoration)
   */
  public clearCheckpointsAfter(checkpointId: string): void {
    if (!this.currentNotebookId) {
      return;
    }

    const notebookCheckpoints =
      this.checkpoints.get(this.currentNotebookId) || [];
    const checkpointIndex = notebookCheckpoints.findIndex(
      cp => cp.id === checkpointId
    );

    if (checkpointIndex !== -1) {
      // Keep only checkpoints up to and including the target checkpoint
      const remainingCheckpoints = notebookCheckpoints.slice(
        0,
        checkpointIndex + 1
      );
      this.checkpoints.set(this.currentNotebookId, remainingCheckpoints);

      console.log(
        '[CheckpointManager] Cleared checkpoints after:',
        checkpointId
      );
      console.log(
        '[CheckpointManager] Remaining checkpoints:',
        remainingCheckpoints.length
      );
    }
  }

  /**
   * Capture the current notebook state
   */
  private captureNotebookState(): ICachedCellState[] {
    if (!this.currentNotebookId) {
      return [];
    }

    try {
      const currentState = NotebookCellStateService.getCurrentNotebookState(
        this.currentNotebookId
      );
      return currentState || [];
    } catch (error) {
      console.error(
        '[CheckpointManager] Error capturing notebook state:',
        error
      );
      return [];
    }
  }
}
