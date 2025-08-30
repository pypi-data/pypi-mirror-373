import {
  INotebookTracker,
  Notebook,
  NotebookPanel
} from '@jupyterlab/notebook';
import { Cell } from '@jupyterlab/cells';
import { NotebookDiffTools } from './NotebookDiffTools';
import { NotebookCellTools } from './NotebookCellTools';
import { TrackingIDUtility } from '../TrackingIDUtility';
import { WaitingUserReplyBoxManager } from './WaitingUserReplyBoxManager';
import { FilesystemTools } from '../BackendTools/FilesystemTools';
import { WebTools } from '../BackendTools/WebTools';
import { AppStateService } from '../AppState';
import { Subscription } from 'rxjs';

/**
 * Class providing tools for manipulating notebook cells
 */
export class NotebookTools {
  private cellTools: NotebookCellTools;
  private notebookTracker: INotebookTracker;
  private diffTools: NotebookDiffTools;
  private waitingUserReplyBoxManager: WaitingUserReplyBoxManager;
  private filesystemTools: FilesystemTools;
  private webTools: WebTools;
  private subscriptions: Subscription[] = [];
  /**
   * Create a new NotebookTools instance
   * @param notebooks The notebook tracker from JupyterLab
   */
  constructor(
    notebooks: INotebookTracker,
    waitingUserReplyBoxManager: WaitingUserReplyBoxManager
  ) {
    this.notebookTracker = notebooks;
    this.waitingUserReplyBoxManager = waitingUserReplyBoxManager;
    this.diffTools = new NotebookDiffTools();
    this.filesystemTools = new FilesystemTools();
    this.webTools = new WebTools();
    this.cellTools = new NotebookCellTools(this);

    // Subscribe to notebook change events (no need to track locally)
  }

  /**
   * Get the current active notebook or return null if none
   * @param notebookIdentifier Optional notebook path or ID to specify which notebook to get
   * @returns The current notebook or null
   */
  public getCurrentNotebook(
    notebookIdentifier?: string | null
  ): { notebook: Notebook; widget: NotebookPanel } | null {
    // First try to get the notebook from AppStateService
    const currentNotebook = AppStateService.getCurrentNotebook();
    if (currentNotebook) {
      return { notebook: currentNotebook.content, widget: currentNotebook };
    }

    // Otherwise fallback to the current active notebook from tracker
    const current = this.notebookTracker.currentWidget;

    if (!current) {
      console.log('No current notebook');
      return null;
    }

    return { notebook: current.content, widget: current };
  }

  /**
   * Find a cell by its ID in a specific notebook
   * @param cellId The ID of the cell to find
   * @param notebookPath Optional path to the notebook containing the cell
   * @returns The cell or null if not found
   */
  findCellById(
    cellId: string,
    notebookPath?: string | null
  ): { cell: Cell; index: number } | null {
    console.log('Finding cell by ID:', cellId);
    const current = this.getCurrentNotebook(notebookPath);
    if (!current) return null;

    const { notebook } = current;

    for (let i = 0; i < notebook.model!.cells.length; i++) {
      console.log(notebook.widgets[i].id);
      console.log(notebook.widgets[i].model.id);
      console.log(notebook.widgets[i].model.sharedModel.id);
    }

    for (let i = 0; i < notebook.model!.cells.length; i++) {
      const cell = notebook.widgets[i];
      if (cell.model.id === cellId) {
        return { cell, index: i };
      }
    }

    console.log(`Cell with ID ${cellId} not found`);
    return null;
  }

  /**
   * Activate a specific cell in the notebook by index
   * @param index The index of the cell to activate
   * @returns True if successful, false otherwise
   */
  public activateCellByIndex(index: number): boolean {
    const current = this.getCurrentNotebook();
    if (!current) return false;

    const { notebook } = current;

    if (index < 0 || index >= notebook.widgets.length) {
      console.log(`Invalid cell index: ${index}`);
      return false;
    }

    notebook.activeCellIndex = index;
    return true;
  }

  /**
   * Activate a specific cell in the notebook
   * @param indexOrCell The index or cell object to activate
   * @returns True if successful, false otherwise
   */
  public activateCell(indexOrCell: number | Cell): boolean {
    if (typeof indexOrCell === 'number') {
      return this.activateCellByIndex(indexOrCell);
    } else {
      const current = this.getCurrentNotebook();
      if (!current) return false;

      const { notebook } = current;

      // Find the cell index
      let cellIndex = -1;
      for (let i = 0; i < notebook.widgets.length; i++) {
        if (notebook.widgets[i] === indexOrCell) {
          cellIndex = i;
          break;
        }
      }

      if (cellIndex === -1) {
        console.log('Cell not found in notebook');
        return false;
      }

      notebook.activeCellIndex = cellIndex;
      return true;
    }
  }

  public async getNotebookSummary(
    notebookIdentifier: string | null
  ): Promise<any> {
    // Support both notebook paths and IDs for backward compatibility
    const nb = this.getCurrentNotebook(notebookIdentifier);
    const cells = [];
    let index = 0;
    for (const cell of nb?.widget.model?.cells || []) {
      let cellReturn = {
        index: index++,
        id: '',
        cell_type: '',
        summary: '',
        next_step_string: '',
        current_step_string: '',
        empty: true
      };
      const metadata = cell.metadata as any;

      const custom = metadata.custom;
      if (custom) cellReturn = { ...cellReturn, ...custom };
      const tracker = metadata.cell_tracker;
      if (tracker) cellReturn.id = tracker.trackingId;

      cellReturn.empty = cell.sharedModel.getSource().trim() === '';
      cellReturn.cell_type = cell.type;

      cells.push(cellReturn);
    }

    console.log('All Cells', cells);

    return cells;
  }

  /**
   * Activate the cell and scroll to it
   * @param cellId The cell tracking ID cell_x
   */
  public async scrollToCellById(cellId: string): Promise<void> {
    const notebook = this.getCurrentNotebook()?.notebook;
    if (!notebook) return;

    const cellIndex = notebook.widgets.findIndex(
      cell => (cell.model.metadata as any)?.cell_tracker.trackingId === cellId
    );
    const cell = notebook.widgets[cellIndex];
    if (!cell) return;

    notebook.activeCellIndex = cellIndex;

    const exactElement = document.querySelector(`[sage-ai-cell-id=${cellId}]`);
    if (
      exactElement &&
      exactElement.parentElement &&
      exactElement.parentElement.style.display !== 'none'
    ) {
      exactElement.scrollIntoView();
    } else {
      notebook.scrollToItem(cellIndex, 'center');

      await Promise.resolve(requestAnimationFrame);
      const delayedScroll = (delay: number) => {
        setTimeout(() => {
          document
            .querySelector(`[sage-ai-cell-id=${cellId}]`)
            ?.scrollIntoView();
        }, delay);
      };

      // The notebook scroll doesn't work properly
      // It has issues with the virtualized Notebook
      // This code allows the scroll to be more assertive
      let delay = 100;
      while (delay < 1000) {
        delayedScroll(delay);
        delay += 100;
      }
    }
  }

  /**
   * Scroll to the first plan cell in the notebook
   */
  public async scrollToPlanCell(): Promise<void> {
    const notebook = this.getCurrentNotebook()?.notebook;
    if (!notebook) return;

    const cellIndex = notebook.widgets.findIndex(
      cell => (cell.model.metadata.custom as any)?.sage_cell_type === 'plan'
    );
    const cell = notebook.widgets[cellIndex];
    if (!cell) return;

    notebook.scrollToItem(cellIndex, 'center');

    notebook.activeCellIndex = cellIndex;

    const cellId = (cell.model.metadata as any)?.cell_tracker.trackingId;
    if (!cellId) return;

    // The notebook scroll doesn't work properly
    // It has issues with the virtualized Notebook
    // This code allows the scroll to be more assertive
    await Promise.resolve(requestAnimationFrame);
    setTimeout(() => {
      document.querySelector(`[sage-ai-cell-id=${cellId}]`)?.scrollIntoView();
    }, 100);
  }

  async waitForScrollEnd(el: HTMLElement): Promise<void> {
    // If the browser supports the event, one-shot-listen for it
    if ('onscrollend' in el) {
      return new Promise(res =>
        el.addEventListener('scrollend', () => res(), { once: true })
      );
    }
    // Fallback to the debounce method (next section)
    return this.waitForScrollIdle(el);
  }

  async waitForScrollIdle(el: HTMLElement, idleMS = 120): Promise<void> {
    return new Promise<void>(resolve => {
      let timer: number;

      const onScroll = () => {
        clearTimeout(timer);
        timer = window.setTimeout(() => {
          el.removeEventListener('scroll', onScroll);
          resolve();
        }, idleMS);
      };

      el.addEventListener('scroll', onScroll, { passive: true });
      onScroll(); // start the timer immediately
    });
  }

  /**
   * Normalize content by trimming whitespace and determining if it's empty
   * @param content The content to normalize
   * @returns The normalized content string
   */
  normalizeContent(content: string): string {
    // Trim the content and check if it's effectively empty
    return content.trim();
  }

  // Forward methods to specialized tools
  display_diff(
    cell: Cell,
    oldText: string,
    newText: string,
    operation: string
  ) {
    return this.diffTools.display_diff(this, cell, oldText, newText, operation);
  }

  apply_diff(cell: Cell, accept: boolean) {
    return this.diffTools.apply_diff(this, cell, accept);
  }

  // Cell manipulation methods
  run_cell(options: {
    cell_id: string;
    notebook_path?: string | null;
    kernel_id?: string | null;
  }) {
    return this.cellTools.run_cell(options);
  }

  /**
   * Find a cell by its ID in a specific notebook
   * If the cellId starts with 'cell_', it is a tracking ID, otherwise it is a model ID
   * @param cellId The ID of the cell to find
   * @param notebookPath Optional path to the notebook containing the cell
   * @returns The cell or null if not found
   */
  findCellByAnyId(
    cellId: string,
    notebookPath?: string | null
  ): { cell: Cell; index: number } | null {
    if (cellId.startsWith('cell_')) {
      return this.findCellByTrackingId(cellId, notebookPath);
    } else {
      return this.findCellById(cellId, notebookPath);
    }
  }

  // Find a cell by tracking ID in a specific notebook
  findCellByTrackingId(
    trackingId: string,
    notebookPath?: string | null
  ): { cell: Cell; index: number } | null {
    const notebook = this.getCurrentNotebook(notebookPath)?.notebook;
    if (!notebook) {
      return null;
    }

    for (let i = 0; i < notebook.widgets.length; i++) {
      const cell = notebook.widgets[i];
      const metadata: any = cell.model.sharedModel.getMetadata() || {};

      if (
        metadata.cell_tracker &&
        metadata.cell_tracker.trackingId === trackingId
      ) {
        return { cell, index: i };
      }
    }

    return null;
  }

  /**
   * Find a cell by its index in a specific notebook
   * @param index The index of the cell to find
   * @returns The cell or null if not found
   */
  findCellByIndex(index: number): { cell: Cell; index: number } | null {
    const notebook = this.getCurrentNotebook()?.notebook;
    if (!notebook) {
      return null;
    }

    return { cell: notebook.widgets[index], index };
  }

  add_cell(options: {
    cell_type: string;
    source: string;
    summary: string;
    notebook_path?: string | null;
    position?: number | null;
    show_diff?: boolean;
    tracking_id?: string; // Optional tracking ID to reuse
  }): string {
    return this.cellTools.add_cell(options);
  }

  remove_cells(options: {
    cell_ids: string[];
    notebook_path?: string | null;
    remove_from_notebook?: boolean;
  }): boolean {
    return this.cellTools.remove_cells(options);
  }

  edit_cell(options: {
    cell_id: string;
    new_source: string;
    summary: string;
    notebook_path?: string | null;
    show_diff?: boolean;
    is_tracking_id?: boolean; // Indicate if cell_id is a tracking ID
  }): boolean {
    return this.cellTools.edit_cell(options);
  }

  stream_edit_plan(options: {
    partial_plan: string;
    notebook_path?: string | null;
  }): boolean {
    return this.cellTools.stream_edit_plan(options);
  }

  async edit_plan(options: {
    immediate_action: string;
    notebook_path?: string | null;
  }): Promise<string | { error: true; errorText: string }> {
    return await this.cellTools.edit_plan(options);
  }

  get_cells_info(): {
    cells: Array<{ id: string; type: string; content: string }>;
  } | null {
    return this.cellTools.get_cells_info();
  }

  get_cell_info(options: { cell_id: string }): any {
    return this.cellTools.get_cell_info(options);
  }

  edit_history(options: { limit?: number }): any {
    return this.cellTools.edit_history(options);
  }

  /**
   * Read all cells from the notebook with comprehensive information and metadata
   * @param options Configuration options
   * @param options.notebook_path Path to the notebook file (optional)
   * @param options.include_outputs Whether to include cell outputs (optional, default: true)
   * @param options.include_metadata Whether to include cell metadata (optional, default: true)
   * @returns Array of comprehensive cell information or null if no notebook
   */
  read_cells(
    options: {
      notebook_path?: string | null;
      include_outputs?: boolean;
      include_metadata?: boolean;
    } = {}
  ): {
    cells: Array<{
      id: string;
      index: number;
      type: string;
      content: string;
      trackingId?: string;
      metadata?: any;
      outputs?: any[];
      execution_count?: number;
    }>;
    notebook_path?: string;
    total_cells: number;
  } | null {
    return this.cellTools.read_cells(options);
  }

  refresh_ids(): void {
    new TrackingIDUtility(this.notebookTracker).fixTrackingIDs();
  }

  /**
   * Ensure the first cell of a notebook is a plan cell
   * @param notebookPath Optional notebook path
   */
  public setFirstCellAsPlan(notebookPath?: string | null): void {
    this.cellTools.setFirstCellAsPlan(notebookPath);
  }

  /**
   * Get the plan cell from the notebook
   * @param notebookPath Optional notebook path
   * @returns The plan cell or null if not found
   */
  public getPlanCell(notebookPath?: string | null): Cell | null {
    const current = this.getCurrentNotebook(notebookPath);
    if (!current) return null;

    const { notebook } = current;
    return this.cellTools.findPlanCell(notebook);
  }

  /**
   * Displays a UI component to inform the user that the agent has completed its turn and is now waiting for a user reply.
   *
   * This tool should be called as the final action in an assistant's turn after providing a complete response or asking a question.
   * It signals that the agent is done processing and is awaiting the user's next instruction or answer.
   *
   * **How to use `wait_user_reply`:**
   * 1. **First, send a message** containing your question or the information you want the user to review.
   * 2. **Immediately after**, call the `wait_user_reply` tool.
   * 3. **Generate 1-3 follow up responses** that are relevant to the question or action you are waiting for:
   *    - These should be concise and directly related to the user's potential responses.
   *    - They should not be speculative or unrelated to the current task.
   *    - Create exact responses and examples, not vague responses like "Modify the strategy" which can be interpreted in many ways.
   *    - When asking the user to proceed or continue, only provide one option to continue unless it is extremely relevant to modify the task.
   *    - For extremely simple tasks such as printing hello world or basic debugging tasks do not include any follow up responses.
   *
   * @param options Configuration options
   * @param options.notebook_path Path to the notebook file (optional)
   * @param options.recommended_next_prompts List of recommended prompts to show to the user
   * @returns True if the waiting reply box was shown successfully
   */
  wait_user_reply(options: {
    notebook_path?: string | null;
    recommended_next_prompts?: string[];
  }): boolean {
    try {
      const llmStateDisplay =
        AppStateService.getChatContainerSafe()?.chatWidget.llmStateDisplay;
      if (llmStateDisplay) {
        llmStateDisplay.show('Waiting for your reply...', true);
      }

      // Get the ChatMessages component from the current chat container
      const chatContainer = AppStateService.getState().chatContainer;
      if (chatContainer && chatContainer.chatWidget) {
        const messageComponent = chatContainer.chatWidget.getMessageComponent();

        // Set the continue callback if not already set
        messageComponent.setContinueCallback(() => {
          chatContainer.chatWidget.sendContinueMessage();
        });

        // Show the waiting reply box using the new system with recommended prompts
        messageComponent.showWaitingReplyBox(options.recommended_next_prompts);
        console.log('Waiting for user reply - new system box shown');
        return true;
      } else {
        // Fallback to old system if chat container is not available
        this.waitingUserReplyBoxManager.show(options.recommended_next_prompts);
        console.log('Waiting for user reply - fallback to old system');
        return true;
      }
    } catch (error) {
      console.error('Error showing waiting reply box:', error);
      return false;
    }
  }

  // Filesystem tool wrappers
  /**
   * List datasets in the data directory
   * @param options Configuration options (unused for list_datasets but needed for consistency)
   * @returns JSON string with list of files and their metadata
   */
  async list_datasets(options?: any): Promise<string> {
    return this.filesystemTools.list_datasets(options);
  }

  /**
   * Read a dataset file
   * @param options Configuration options
   * @param options.filepath Path to the file to read
   * @param options.start Starting line number (0-indexed)
   * @param options.end Ending line number (0-indexed)
   * @returns JSON string with file contents or error
   */
  async read_dataset(options: {
    filepath: string;
    start?: number;
    end?: number;
  }): Promise<string> {
    return this.filesystemTools.read_dataset(options);
  }

  /**
   * Delete a dataset file
   * @param options Configuration options
   * @param options.filepath Path to the file to delete
   * @returns JSON string with success or error message
   */
  async delete_dataset(options: { filepath: string }): Promise<string> {
    return this.filesystemTools.delete_dataset(options);
  }

  /**
   * Upload/save a dataset file
   * @param options Configuration options
   * @param options.filepath Path where to save the file
   * @param options.content Content to save
   * @returns JSON string with success or error message
   */
  async save_dataset(options: {
    filepath: string;
    content: string;
  }): Promise<string> {
    return this.filesystemTools.save_dataset(options);
  }

  // Web tool wrappers
  /**
   * Search for tickers matching the query strings
   * @param options Configuration options
   * @param options.queries List of search strings to match against ticker symbols or names
   * @param options.limit Maximum number of results to return (default: 10, max: 10)
   * @returns JSON string with list of matching tickers
   */
  async search_dataset(options: {
    queries: string[];
    limit?: number;
  }): Promise<string> {
    return this.webTools.search_dataset(options);
  }
}
