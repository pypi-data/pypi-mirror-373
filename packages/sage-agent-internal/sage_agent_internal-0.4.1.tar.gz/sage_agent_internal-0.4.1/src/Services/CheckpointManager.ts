import { IChatMessage, ICheckpoint } from '../types';
import { MentionContext } from '../Chat/ChatContextMenu/ChatContextMenu';
import {
  NotebookCellStateService,
  ICachedCellState
} from './NotebookCellStateService';
import { ActionHistory, IActionHistoryEntry } from '../Chat/ActionHistory';
import { StateDBCachingService, STATE_DB_KEYS } from '../utils/stateDBCaching';

/**
 * Serializable version of ICheckpoint for storage
 */
interface SerializableCheckpoint {
  id: string;
  timestamp: number;
  userMessage: string;
  userMessageId?: string;
  messageHistory: IChatMessage[];
  notebookState: ICachedCellState[];
  contexts: Record<string, any>; // Serialized Map
  notebookId: string;
  actionHistory: any[];
}

/**
 * Service for managing checkpoints in the chat conversation
 * Checkpoints capture the state at user message points for potential restoration
 */
export class CheckpointManager {
  private static instance: CheckpointManager;
  private checkpoints: Map<string, ICheckpoint[]> = new Map(); // notebookId -> checkpoints
  private currentNotebookId: string | null = null;
  private currentCheckpoint: [ICheckpoint, string] | null = null; // tuple of (checkpointId, threadId)

  private constructor() {
    console.log('[CheckpointManager] Initialized with cached data');
    this.initialize();
  }

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
    threadId: string,
    userMessageId?: string
  ): ICheckpoint {
    if (!this.currentNotebookId) {
      throw new Error('No current notebook ID set');
    }

    const newCheckpointId = `checkpoint_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    let nextCheckpointId: string | undefined = undefined;
    if (
      this.currentCheckpoint &&
      this.currentCheckpoint[0] &&
      this.currentCheckpoint[1] === threadId
    ) {
      this.currentCheckpoint[0].nextCheckpointId = newCheckpointId;
    }

    const checkpoint: ICheckpoint = {
      id: newCheckpointId,
      timestamp: Date.now(),
      userMessage,
      userMessageId,
      messageHistory: [...messageHistory], // Deep copy
      notebookState: this.captureNotebookState(),
      contexts: new Map(contexts), // Deep copy
      notebookId: this.currentNotebookId,
      actionHistory: [],
      nextCheckpointId
    };

    // Store checkpoint for this notebook
    if (!this.checkpoints.has(this.currentNotebookId)) {
      this.checkpoints.set(this.currentNotebookId, []);
    }

    const notebookCheckpoints = this.checkpoints.get(this.currentNotebookId)!;
    notebookCheckpoints.push(checkpoint);

    // Set this as the current checkpoint being processed
    this.currentCheckpoint = [checkpoint, threadId];

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

    // Auto-save after creating checkpoint
    this.saveToStorage();

    return checkpoint;
  }

  /**
   * Add a single action to the current checkpoint
   */
  public addActionToCurrentCheckpoint(action: IActionHistoryEntry): void {
    const [_checkpoint] = this.currentCheckpoint || [];
    if (!_checkpoint || !this.currentNotebookId) {
      console.warn(
        '[CheckpointManager] No current checkpoint to add action to'
      );
      return;
    }

    const notebookCheckpoints = this.checkpoints.get(this.currentNotebookId);
    if (!notebookCheckpoints) {
      console.warn(
        '[CheckpointManager] No checkpoints found for current notebook'
      );
      return;
    }

    const checkpoint = notebookCheckpoints.find(cp => cp.id === _checkpoint.id);
    if (!checkpoint) {
      console.warn('[CheckpointManager] Current checkpoint not found');
      return;
    }

    // Add the action to the checkpoint's actionHistory
    checkpoint.actionHistory.push(action);

    console.log(
      '[CheckpointManager] Added action to checkpoint:',
      action.description
    );
    console.log(
      '[CheckpointManager] Total actions in checkpoint:',
      checkpoint.actionHistory.length
    );

    // Auto-save after adding action
    this.saveToStorage();
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
   * Find a checkpoint by user message content
   */
  public findCheckpointByUserMessage(userMessage: string): ICheckpoint | null {
    if (!this.currentNotebookId) {
      return null;
    }

    const checkpoints = this.checkpoints.get(this.currentNotebookId) || [];
    return (
      checkpoints.find(checkpoint => checkpoint.userMessage === userMessage) ||
      null
    );
  }

  /**
   * Find a checkpoint by user message ID
   */
  public findCheckpointByUserMessageId(
    userMessageId: string
  ): ICheckpoint | null {
    if (!this.currentNotebookId) {
      return null;
    }

    const checkpoints = this.checkpoints.get(this.currentNotebookId) || [];
    return (
      checkpoints.find(
        checkpoint => checkpoint.userMessageId === userMessageId
      ) || null
    );
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

      // Auto-save after clearing
      this.saveToStorage();
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

      // Auto-save after clearing
      this.saveToStorage();
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

  /**
   * Save all checkpoints to StateDB storage
   */
  private async saveToStorage(): Promise<void> {
    try {
      // Convert Map to a serializable object (same pattern as ChatHistoryManager)
      const storageObj: Record<string, SerializableCheckpoint[]> = {};

      for (const [notebookId, checkpoints] of this.checkpoints.entries()) {
        // Convert each checkpoint's contexts Map to a serializable object
        const serializedCheckpoints = checkpoints.map(checkpoint => ({
          ...checkpoint,
          contexts: checkpoint.contexts
            ? Object.fromEntries(checkpoint.contexts)
            : {}
        }));
        storageObj[notebookId] = serializedCheckpoints;
      }

      await StateDBCachingService.setObjectValue(
        STATE_DB_KEYS.NOTEBOOK_CHECKPOINTS,
        storageObj
      );

      console.log('[CheckpointManager] Saved checkpoints to StateDB storage');
    } catch (error) {
      console.error(
        '[CheckpointManager] Error saving checkpoints to StateDB:',
        error
      );
    }
  }

  /**
   * Load checkpoints from StateDB storage
   */
  private async loadFromStorage(): Promise<void> {
    try {
      const storedData = await StateDBCachingService.getObjectValue<
        Record<string, SerializableCheckpoint[]>
      >(STATE_DB_KEYS.NOTEBOOK_CHECKPOINTS, {});

      if (storedData && Object.keys(storedData).length > 0) {
        this.checkpoints = new Map();

        for (const [notebookId, checkpoints] of Object.entries(storedData)) {
          // Convert objects back to proper ICheckpoint format with Maps
          const deserializedCheckpoints: ICheckpoint[] = checkpoints.map(
            checkpoint => ({
              ...checkpoint,
              contexts: checkpoint.contexts
                ? new Map<string, any>(Object.entries(checkpoint.contexts))
                : new Map<string, any>()
            })
          );

          this.checkpoints.set(notebookId, deserializedCheckpoints);
        }

        console.log(
          '[CheckpointManager] Loaded checkpoints from StateDB storage'
        );
        console.log(
          `[CheckpointManager] Loaded checkpoints for ${this.checkpoints.size} notebooks`
        );
      } else {
        console.log(
          '[CheckpointManager] No stored checkpoints found in StateDB'
        );
      }
    } catch (error) {
      console.error(
        '[CheckpointManager] Error loading checkpoints from StateDB:',
        error
      );
      // Reset to empty state on error
      this.checkpoints = new Map();
    }
  }

  /**
   * Initialize CheckpointManager with cached data
   */
  public async initialize(): Promise<void> {
    await this.loadFromStorage();
    console.log('[CheckpointManager] Initialized with cached data');
  }
}
