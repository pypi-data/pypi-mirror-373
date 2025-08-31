import { ToolService } from '../Services/ToolService';
import { NotebookStateService } from './NotebookStateService';
import { AppStateService } from '../AppState';

/**
 * Interface for notebook-specific context data
 */
export interface INotebookContext {
  notebookId: string;
  toolService: ToolService;
  stateService: NotebookStateService;
  lastAccessed: number;
  flowId?: string; // Unique ID for this LLM flow/conversation
  contextCells: IContextCell[]; // Array of cells added to context
}

/**
 * Interface for a cell added to context
 */
export interface IContextCell {
  cellId: string;
  trackingId?: string;
  content: string;
  cellType: string;
  addedAt: number;
}

/**
 * Manager for maintaining notebook-specific contexts for LLM flows
 */
export class NotebookContextManager {
  // Map from notebook IDs to their contexts
  private notebookContexts: Map<string, INotebookContext> = new Map();
  // Shared toolService instance
  private sharedToolService: ToolService;

  constructor(toolService: ToolService) {
    this.sharedToolService = toolService;

    // Subscribe to notebook change events from AppStateService
    AppStateService.onNotebookChanged().subscribe(({ newNotebookId }) => {
      if (newNotebookId) {
        this.getContext(newNotebookId);
      }
    });

    // AppStateService.onNotebookRenamed().subscribe(
    //   ({ oldNotebookId, newNotebookId }) => {
    //     this.updateNotebookId(oldNotebookId, newNotebookId);
    //   }
    // );
  }

  /**
   * Get or create a context for a specific notebook
   * @param notebookId ID of the notebook
   * @returns The notebook context object
   */
  public getContext(notebookId: string): INotebookContext {
    if (!this.notebookContexts.has(notebookId)) {
      console.log(
        `[NotebookContextManager] Creating new context for notebook: ${notebookId}`
      );

      // Set the current notebook ID in the tool service
      this.sharedToolService.setCurrentNotebookId(notebookId);

      // Create a notebook-specific state service using the shared tool service
      const stateService = new NotebookStateService(this.sharedToolService);
      stateService.setNotebookId(notebookId);

      // Create the context
      const context: INotebookContext = {
        notebookId,
        toolService: this.sharedToolService,
        stateService,
        lastAccessed: Date.now(),
        flowId: this.generateFlowId(),
        contextCells: [] // Initialize with empty array of context cells
      };

      this.notebookContexts.set(notebookId, context);
      return context;
    }

    // Update last accessed time and return existing context
    const context = this.notebookContexts.get(notebookId)!;
    context.lastAccessed = Date.now();

    // Ensure the tool service is set to the correct notebook ID
    this.sharedToolService.setCurrentNotebookId(notebookId);

    return context;
  }

  public updateNotebookId(oldNotebookId: string, newNotebookId: string): void {
    const context = this.notebookContexts.get(oldNotebookId);
    if (context) {
      context.notebookId = newNotebookId;
      this.notebookContexts.set(newNotebookId, context);
      this.notebookContexts.delete(oldNotebookId);
    }
  }

  /**
   * Add a cell to the context for a notebook
   * @param notebookId ID of the notebook
   * @param cellId ID of the cell
   * @param trackingId Optional tracking ID of the cell
   * @param content Content of the cell
   * @param cellType Type of the cell (code, markdown)
   * @returns true if the cell was added, false if it was already in context
   */
  public addCellToContext(
    notebookId: string,
    cellId: string,
    trackingId: string | undefined,
    content: string,
    cellType: string
  ): boolean {
    // Get or create the context for this notebook
    const context = this.getContext(notebookId);

    // Check if this cell is already in context
    if (context.contextCells.some(c => c.cellId === cellId)) {
      return false; // Already in context
    }

    // Add the cell to context
    context.contextCells.push({
      cellId,
      trackingId,
      content,
      cellType,
      addedAt: Date.now()
    });

    console.log(`[NotebookContextManager] Added cell to context: ${cellId}`);
    return true;
  }

  /**
   * Remove a cell from the context
   * @param notebookId ID of the notebook
   * @param cellId ID of the cell to remove
   * @returns true if the cell was removed, false if it wasn't in context
   */
  public removeCellFromContext(notebookId: string, cellId: string): boolean {
    // Get the context for this notebook
    if (!this.notebookContexts.has(notebookId)) {
      return false;
    }

    const context = this.notebookContexts.get(notebookId)!;
    const initialLength = context.contextCells.length;

    // Filter out the cell to remove
    context.contextCells = context.contextCells.filter(
      c => c.cellId !== cellId
    );

    // Return true if a cell was removed
    return context.contextCells.length < initialLength;
  }

  /**
   * Check if a cell is in context
   * @param notebookId ID of the notebook
   * @param cellId ID of the cell to check
   * @returns true if the cell is in context, false otherwise
   */
  public isCellInContext(notebookId: string, cellId: string): boolean {
    if (!this.notebookContexts.has(notebookId)) {
      return false;
    }

    const context = this.notebookContexts.get(notebookId)!;
    return context.contextCells.some(c => c.cellId === cellId);
  }

  /**
   * Get all cells in context for a notebook
   * @param notebookId ID of the notebook
   * @returns Array of context cells or empty array if notebook has no context
   */
  public getContextCells(notebookId: string): IContextCell[] {
    if (!this.notebookContexts.has(notebookId)) {
      return [];
    }

    return [...this.notebookContexts.get(notebookId)!.contextCells];
  }

  /**
   * Format the context cells as a message for sending to the LLM
   * @param notebookId ID of the notebook
   * @returns Formatted context message in XML format
   */
  public formatContextAsMessage(notebookId: string): string {
    const cells = this.getContextCells(notebookId);

    if (cells.length === 0) {
      return '';
    }

    // Format the cells in an XML-style format for better LLM understanding
    let formattedContent =
      'Here are the cells from the notebook that the user has provided as additional context:\n\n';

    cells.forEach(cell => {
      const found = this.sharedToolService.notebookTools?.findCellByAnyId(
        cell.trackingId!
      );
      if (found) {
        formattedContent += `==== CELL Context - Cell ID: ${cell.trackingId} ====\n`;
        formattedContent += found.cell.model.sharedModel.getSource().trim();
        formattedContent += `\n==== End Cell Context ====\n\n`;
      }
    });

    return formattedContent;
  }

  /**
   * Get a summary of what's in context for display purposes
   * @param notebookId ID of the notebook
   * @returns Array of context summaries
   */
  public getContextSummary(notebookId: string): Array<{
    type: 'cell';
    id: string;
    name: string;
    preview: string;
  }> {
    const cells = this.getContextCells(notebookId);

    return cells.map(cell => {
      const found = this.sharedToolService.notebookTools?.findCellByAnyId(
        cell.trackingId!
      );

      if (found) {
        const content = found.cell.model.sharedModel.getSource();
        const preview =
          content.length > 50 ? content.substring(0, 50) + '...' : content;

        return {
          type: 'cell' as const,
          id: cell.trackingId!,
          name: `Cell ${cell.trackingId}`,
          preview: preview
        };
      }

      return {
        type: 'cell' as const,
        id: cell.trackingId!,
        name: `Cell ${cell.trackingId}`,
        preview: 'Cell content unavailable'
      };
    });
  }

  /**
   * Generate a unique flow ID
   */
  private generateFlowId(): string {
    return (
      'flow-' + Date.now() + '-' + Math.random().toString(36).substring(2, 9)
    );
  }
}
