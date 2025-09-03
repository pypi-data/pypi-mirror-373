import { IActionHistoryEntry } from './Chat/ActionHistory';
import { ICachedCellState } from './Services/NotebookCellStateService';

/**
 * Interface for chat message
 */
export interface IChatMessage {
  role: string;
  content: string | any[];
  id?: string; // Unique identifier for the message
}

/**
 * Interface for tool call
 */
export interface IToolCall {
  id: string;
  name: string;
  input: any;
}

/**
 * Enum representing the status of a chat request
 */
export enum ChatRequestStatus {
  IDLE = 'idle',
  PENDING = 'pending',
  COMPLETED = 'completed',
  ERROR = 'error',
  CANCELLED = 'cancelled',
  RETRYING = 'retrying'
}

/**
 * Interface for a pending diff in the notebook
 */
export interface IPendingDiff {
  cellId: string;
  type: 'add' | 'edit' | 'remove';
  summary?: string;
  approved?: boolean;
  originalContent?: string;
  newContent?: string;
  updatedCellId?: string; // Track ID changes
  metadata?: any;
  notebookId?: string | null; // Add notebook ID
  userDecision?: 'approved' | 'rejected' | 'run' | null; // Track user's decision state
  runResult?: any; // Result of running the diff
  displaySummary?: string; // Computed display summary for UI
}

/**
 * Diff approval status
 */
export enum DiffApprovalStatus {
  PENDING = 'pending',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  PARTIAL = 'partial'
}

/**
 * Result of applying/handling diffs
 */
export interface IDiffApplicationResult {
  success: boolean;
  status: DiffApprovalStatus;
}

/**
 * Interface for cell tracking metadata
 */
export interface ICellTrackingMetadata {
  trackingId: string;
  createdAt: string;
  lastModified: string;
  origin: 'user' | 'ai' | 'system';
  summary?: string;
}

/**
 * Interface for a checkpoint
 */
export interface ICheckpoint {
  id: string;
  timestamp: number;
  userMessage: string;
  userMessageId?: string; // ID of the user message this checkpoint is associated with
  messageHistory: IChatMessage[];
  notebookState: ICachedCellState[];
  contexts: Map<string, any>;
  notebookId: string;
  actionHistory: IActionHistoryEntry[];
  nextCheckpointId?: string;
}

/**
 * Restoration options for checkpoint
 */
export enum CheckpointRestorationOption {
  CANCEL = 'cancel',
  CONTINUE_WITHOUT_RUNNING = 'continue_without_running',
  CONTINUE_AND_RUN_ALL_CELLS = 'continue_and_run_all_cells'
}
