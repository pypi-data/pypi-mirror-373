/**
 * Types of actions that can be undone
 */
export enum ActionType {
  ADD_CELL = 'add_cell',
  EDIT_CELL = 'edit_cell',
  REMOVE_CELLS = 'remove_cells',
  EDIT_PLAN = 'edit_plan'
}

/**
 * Interface for cell data in removed cells
 */
export interface IRemovedCellData {
  trackingId?: string;
  content: string;
  type: string;
  custom?: {
    summary?: string;
    index?: number; // Add index to custom metadata
    [key: string]: any;
  };
}

/**
 * Interface for a history action entry
 */
export interface IActionHistoryEntry {
  type: ActionType;
  data: {
    trackingId?: string; // Use tracking ID instead of cellId
    trackingIds?: string[]; // For multiple cells, use array of tracking IDs
    // ...existing properties for backward compatibility...
    cellId?: string;
    cellIds?: string[];
    originalContent?: string;
    originalSummary?: string;
    newContent?: string;
    summary?: string;
    removedCells?: IRemovedCellData[];
    planExisted?: boolean;
    oldPlan?: string;
    oldCurrentStep?: string;
    oldNextStep?: string;
  };
  timestamp: number;
  description: string;
}

/**
 * Service for tracking and managing undoable actions
 */
export class ActionHistory {
  private history: IActionHistoryEntry[] = [];

  /**
   * Add an action to the history
   * @param type Type of the action
   * @param data Data needed to undo the action
   * @param description Human-readable description of the action
   */
  public addAction(type: ActionType, data: any, description: string): void {
    const entry: IActionHistoryEntry = {
      type,
      data,
      timestamp: Date.now(),
      description
    };

    this.history.push(entry);
    console.log(`[ActionHistory] Added action: ${description}`);
  }

  /**
   * Get the most recent action
   * @returns The most recent action or null if history is empty
   */
  public getLastAction(): IActionHistoryEntry | null {
    if (this.history.length === 0) {
      return null;
    }

    return this.history[this.history.length - 1];
  }

  /**
   * Remove and return the most recent action
   * @returns The most recent action or null if history is empty
   */
  public popLastAction(): IActionHistoryEntry | null {
    if (this.history.length === 0) {
      return null;
    }

    const action = this.history.pop();
    console.log('Action popped for undo:', action);

    return action!;
  }

  /**
   * Check if there are any actions that can be undone
   * @returns True if there are actions in the history
   */
  public canUndo(): boolean {
    return this.history.length > 0;
  }

  /**
   * Get a human-readable description of the last action
   * @returns Description of the last action or null if history is empty
   */
  public getLastActionDescription(): string | null {
    const lastAction = this.getLastAction();
    return lastAction ? lastAction.description : null;
  }

  /**
   * Get all actions in the history
   * @returns Array of all action history entries
   */
  public getAllActions(): IActionHistoryEntry[] {
    return [...this.history];
  }

  /**
   * Clear the action history
   */
  public clear(): void {
    this.history = [];
    console.log('Action history cleared');
  }
}
