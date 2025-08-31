import { Cell } from '@jupyterlab/cells';
import { Notebook, NotebookActions } from '@jupyterlab/notebook';
import { NotebookTools } from './NotebookTools';
import { AppStateService } from '../AppState';
import { ActionType } from '../Chat/ActionHistory';

/**
 * Class providing cell manipulation tools for notebooks
 */
export class NotebookCellTools {
  private notebookTools: NotebookTools;
  private isAutoScrollDisabled: boolean = false;
  private lastAutoScrolledCell: HTMLElement | null = null;
  private scrollListeners: Map<HTMLElement, () => void> = new Map();

  /**
   * Create a new NotebookCellTools instance
   * @param notebookTools The parent NotebookTools instance
   */
  constructor(notebookTools: NotebookTools) {
    this.notebookTools = notebookTools;
  }

  /**
   * Runs a code cell in the specified notebook and returns its formatted output.
   *
   * @param options Configuration options
   * @param options.cell_id Unique identifier of the code cell to execute.
   * @param options.notebook_path Path to the notebook file (optional).
   * @param options.kernel_id Specific kernel ID to use (optional).
   * @param options.is_tracking_id Whether the cell_id is a tracking ID (optional).
   * @returns Formatted output strings from the cell's execution.
   */
  async run_cell(options: {
    cell_id: string;
    notebook_path?: string | null;
    kernel_id?: string | null;
  }): Promise<(string | { error: true; errorText: string })[]> {
    // Find cell by tracking ID or model ID
    let cellInfo = null;
    // Use options.notebook_path directly without reassigning to notebookPath
    console.log(
      'RUNNING CELL - CELL ID:',
      options.cell_id,
      'NOTEBOOK PATH:',
      options.notebook_path
    );

    cellInfo = this.notebookTools.findCellByAnyId(
      options.cell_id,
      options.notebook_path
    );
    console.log('Cell info:', cellInfo);

    if (!cellInfo) {
      throw new Error(
        `Cell with ID ${options.cell_id} not found in notebook ${options.notebook_path || 'current'}`
      );
    }

    const current = this.notebookTools.getCurrentNotebook(
      options.notebook_path
    );
    if (!current) {
      throw new Error(
        `Notebook ${options.notebook_path || 'current'} not found`
      );
    }

    const { notebook } = current;
    const { cell } = cellInfo;

    if (cell.model.type === 'markdown') {
      const source = cell.model.sharedModel.getSource();
      return [source];
    }

    // Verify that it's a code cell
    if (cell.model.type !== 'code') {
      throw new Error(`Cell with ID ${options.cell_id} is not a code cell`);
    }

    // Activate the cell to run
    this.notebookTools.activateCell(cell);

    const restoreScroll = NotebookCellTools.preventScrolling(notebook);

    // Run the cell - pass the actual cell to run instead of using _findCellById
    await NotebookActions.runCells(
      notebook,
      [cell],
      current.widget?.sessionContext
    );

    restoreScroll();

    // Process outputs in a formatted way
    const outputs: (string | { error: true; errorText: string })[] = [];
    try {
      const codeCell = cell as any; // Code cell needs to be cast to appropriate type
      if (codeCell.outputArea && codeCell.outputArea.model.toJSON) {
        const outputsJson = codeCell.outputArea.model.toJSON();
        for (const output of outputsJson) {
          if (output.output_type === 'stream') {
            const getText = () => {
              // Join the text array into a single string if it's an array
              if (Array.isArray(output.text)) {
                return output.text.join('');
              } else {
                return output.text;
              }
            };

            if (output.name === 'stderr') {
              outputs.push({ error: true, errorText: getText() });
              continue;
            }

            outputs.push(getText());
          } else if (
            output.output_type === 'execute_result' ||
            output.output_type === 'display_data'
          ) {
            if (output.data && output.data['text/plain']) {
              // Handle 'text/plain' data which can be string or array
              if (Array.isArray(output.data['text/plain'])) {
                outputs.push(output.data['text/plain'].join(''));
              } else {
                outputs.push(output.data['text/plain']);
              }
            }
          } else if (output.output_type === 'error') {
            // Format error messages with traceback
            outputs.push({
              error: true,
              errorText: `Error: ${output.ename}: ${output.evalue}`
            });
            if (Array.isArray(output.traceback)) {
              // Join traceback items into a single formatted string
              outputs.push({
                error: true,
                errorText: output.traceback.join('\n')
              });
            } else if (output.traceback) {
              outputs.push({ error: true, errorText: output.traceback });
            }
          }
        }
      }
    } catch (error) {
      console.error('Error collecting cell outputs:', error);
      outputs.push(`Error collecting outputs: ${error}`);
    }

    // Handle smart scrolling after cell execution - scroll to include output
    this.handleSmartScroll(cell.node, true);

    return outputs;
  }

  /**
   * Adds a new cell (code or markdown) to the specified notebook at an optional position, returning its unique ID.
   *
   * @param options Configuration options
   * @param options.cell_type Type of cell ("code" or "markdown").
   * @param options.source Initial source content for the cell.
   * @param options.summary A summary of the cell's content.
   * @param options.notebook_path Path to the notebook file (optional).
   * @param options.position 0-based index for insertion (appends if null).
   * @param options.show_diff Whether to show diff view (defaults to false)
   * @param options.tracking_id Optional tracking ID to reuse
   * @returns The unique ID of the newly created cell
   */
  add_cell(options: {
    cell_type: string;
    source: string;
    summary: string;
    notebook_path?: string | null;
    position?: number | null;
    show_diff?: boolean;
    tracking_id?: string; // Optional tracking ID to reuse
  }): string {
    // Get the notebook - pass options.notebook_path directly
    const notebook = this.notebookTools.getCurrentNotebook(
      options.notebook_path
    )?.notebook;
    if (!notebook) {
      throw new Error(
        `Notebook ${options.notebook_path || 'current'} not found`
      );
    }

    console.log(
      `Adding cell of type ${options.cell_type} at position ${options.position} in notebook ${options.notebook_path || 'current'}`
    );

    // Normalize the content - ensure we have valid strings
    const content = options.source || '';

    // Determine position for insertion
    let position: number;
    if (options.position !== null && options.position !== undefined) {
      position = options.position;
      // Ensure position is within valid range
      position = Math.min(Math.max(position, 0), notebook.widgets.length);
    } else {
      position = notebook.widgets.length; // Default to end of notebook
    }

    const restoreScroll = NotebookCellTools.preventScrolling(notebook);

    // Handle insertion based on position
    if (position === 0) {
      // Insert at the beginning of notebook
      this.notebookTools.activateCellByIndex(position);
      NotebookActions.insertAbove(notebook);
    } else {
      // Activate the cell above where we want to insert
      this.notebookTools.activateCellByIndex(position - 1);
      // Insert below the selected cell
      NotebookActions.insertBelow(notebook);
    }

    restoreScroll();

    let newCell = notebook.activeCell;
    if (!newCell) {
      throw new Error('Failed to create new cell');
    }

    // Set the cell type to the requested type
    if (options.cell_type === 'markdown' && newCell.model.type !== 'markdown') {
      NotebookActions.changeCellType(notebook, 'markdown');
    } else if (options.cell_type === 'code' && newCell.model.type !== 'code') {
      NotebookActions.changeCellType(notebook, 'code');
    }

    newCell = notebook.activeCell;
    if (!newCell) {
      throw new Error('Failed to set active cell after insertion');
    }

    // Add tracking metadata to cell
    const metadata: any = newCell.model.sharedModel.getMetadata() || {};
    const now = new Date().toISOString();
    metadata.cell_tracker = {
      trackingId: options.tracking_id || this.generateTrackingId(notebook),
      createdAt: now,
      lastModified: now,
      origin: 'ai',
      summary: options.summary || ''
    };

    // Add custom metadata with summary
    if (!metadata.custom) {
      metadata.custom = {};
    }
    metadata.custom.summary = options.summary;
    newCell.model.sharedModel.setMetadata(metadata);

    // Only display diff if explicitly requested, otherwise set content directly
    if (options.show_diff) {
      this.notebookTools.display_diff(newCell, '', content, 'add');
    } else {
      // Set the cell content directly
      newCell.model.sharedModel.setSource(content);
    }

    // Return the tracking ID instead of cell.model.id since it's more stable
    const trackingMetadata: any =
      newCell.model.sharedModel.getMetadata().cell_tracker;

    // Handle smart scrolling after adding the cell - scroll to cell content only
    this.handleSmartScroll(newCell.node);

    return trackingMetadata.trackingId;
  }

  /**
   * Check if a cell is a plan cell
   */
  public isPlanCell(cell: Cell): boolean {
    const metadata: any = cell?.model?.sharedModel?.getMetadata() || {};
    return metadata.custom?.sage_cell_type === 'plan';
  }

  /**
   * Ensure the first cell of a notebook is a plan cell
   */
  public setFirstCellAsPlan(notebookId?: string | null): void {
    let current = this.notebookTools.getCurrentNotebook(notebookId);
    if (!current) return;

    let { notebook } = current;

    const planCell = this.findPlanCell(notebook);
    if (planCell) return;

    let firstCell = notebook.widgets[0];
    if (!firstCell) {
      console.error('Could not find first cell to ensure it is a plan cell');
      return;
    }

    NotebookActions.changeCellType(notebook, 'markdown');

    current = this.notebookTools.getCurrentNotebook(notebookId);
    if (current && current.notebook) notebook = current.notebook;
    firstCell = notebook.widgets[0]; // Re-fetch after changing type

    const metadata: any = firstCell.model.sharedModel.getMetadata() || {};
    if (!metadata.custom) {
      metadata.custom = {};
    }

    if (!metadata.cell_tracker) {
      metadata.cell_tracker = {};
    }
    metadata.cell_tracker.trackingId = 'planning_cell';

    metadata.custom.sage_cell_type = 'plan';
    firstCell.model.sharedModel.setMetadata(metadata);
    firstCell.model.sharedModel.setSource('');
  }

  /**
   * Find the plan cell in the notebook
   * @param notebookPath Optional notebook path
   * @returns The plan cell or null if not found
   */
  public findPlanCell(notebook: Notebook): Cell | null {
    return notebook.widgets.find(cell => this.isPlanCell(cell)) || null;
  }

  // Generate a unique tracking ID (numerical)
  private generateTrackingId(notebook: any): string {
    // Find the max cell number in use
    let maxNum = 1;
    const cells = notebook.widgets;
    for (let i = 0; i < cells.length; i++) {
      const metadata: any = cells[i].model.sharedModel.getMetadata() || {};
      const trackingId = metadata.cell_tracker?.trackingId;
      if (trackingId && /^cell_(\d+)$/.test(trackingId)) {
        const num = parseInt(trackingId.split('_')[1], 10);
        if (num > maxNum) maxNum = num;
      }
    }
    return `cell_${maxNum}`;
  }

  /**
   * Removes a list of cells from the specified notebook using their IDs.
   *
   * @param options Configuration options
   * @param options.cell_ids A list of unique identifiers of the cells to remove.
   * @param options.notebook_path Path to the notebook file (optional).
   * @returns True if at least one cell was found and removed, False otherwise.
   */
  remove_cells(options: {
    cell_ids: string[];
    notebook_path?: string | null;
    remove_from_notebook?: boolean;
  }): boolean {
    // Determine if the IDs are tracking IDs
    const useTrackingIds = options.cell_ids.every(id => id.startsWith('cell_'));

    // Use options.notebook_path directly
    const current = this.notebookTools.getCurrentNotebook(
      options.notebook_path
    );
    if (!current) {
      return false;
    }

    const { notebook } = current;
    let cellsRemoved = 0;

    // Process each cell ID in the list
    for (const cellId of options.cell_ids) {
      let cellInfo = this.notebookTools.findCellByAnyId(
        cellId,
        options.notebook_path
      );

      if (cellInfo) {
        // Check if this cell is non-deletable
        const metadata: any =
          cellInfo.cell.model.sharedModel.getMetadata() || {};
        const isDeletable = metadata.custom?.deletable !== false;

        if (!isDeletable) {
          console.warn(`Cannot delete non-deletable cell: ${cellId}`);
          continue;
        }

        // Get the cell content before removal to show in diff
        const oldContent = cellInfo.cell.model.sharedModel.getSource();

        // Preserve tracking ID for future reference
        // Type-safe access with explicit cast for cell_tracker and its properties
        const cellTracker = metadata.cell_tracker as
          | { trackingId?: string }
          | undefined;
        const trackingId = cellTracker?.trackingId;

        if (options.remove_from_notebook) {
          // Activate the cell to remove
          this.notebookTools.activateCell(cellInfo.cell);

          // Delete the cell
          NotebookActions.deleteCells(notebook);
          console.log(
            `[NotebookCellTools] Cell ${trackingId} removed permanently from the notebook`
          );
        }

        cellsRemoved++;
      }
    }

    // Handle smart scrolling after removing cells - no specific cell to scroll to, skip
    // Auto-scroll behavior will be handled when new cells are added/edited

    return cellsRemoved > 0;
  }

  /**
   * Modifies the source content of an existing cell.
   *
   * @param options Configuration options
   * @param options.cell_id Unique identifier of the cell to edit.
   * @param options.new_source New source content for the cell.
   * @param options.summary A summary of the cell's new content.
   * @param options.notebook_path Path to the notebook file (optional).
   * @param options.show_diff Whether to show diff view (defaults to false)
   * @param options.is_tracking_id Whether the cell_id is a tracking ID (optional).
   * @returns True if the cell was found and updated, False otherwise.
   */
  edit_cell(options: {
    cell_id: string;
    new_source: string;
    summary: string;
    notebook_path?: string | null;
    show_diff?: boolean;
  }): boolean {
    // Find cell by tracking ID or model ID - use options.notebook_path directly
    let cellInfo = null;

    cellInfo = this.notebookTools.findCellByAnyId(
      options.cell_id,
      options.notebook_path
    );

    if (!cellInfo) {
      console.error(
        `Cell not found with ID: ${options.cell_id} in notebook ${options.notebook_path || 'current'}`
      );
      return false;
    }

    const current = this.notebookTools.getCurrentNotebook(
      options.notebook_path
    );
    if (!current) {
      return false;
    }

    const { notebook } = current;
    const { cell } = cellInfo;

    // Check if this cell is non-editable
    const metadata: any = cell.model.sharedModel.getMetadata() || {};
    const isEditable = metadata.custom?.editable !== false;

    if (!isEditable) {
      console.warn(`Cannot edit non-editable cell: ${options.cell_id}`);
      return false;
    }

    // Get the old content to compare
    const oldContent = cell.model.sharedModel.getSource();

    // Get tracking ID for consistent reference
    const trackingId =
      metadata.cell_tracker?.trackingId || this.generateTrackingId(notebook);

    // Log the diff between old and new content using tracking ID
    // this.notebookTools['diffTools'].logDiff(
    //   this.notebookTools.normalizeContent,
    //   oldContent,
    //   options.new_source,
    //   'edit',
    //   trackingId // Use tracking ID instead of model ID
    // );

    // Activate the cell to edit
    this.notebookTools.activateCell(cell);

    // Update metadata - last modified time and summary
    if (metadata.cell_tracker) {
      metadata.cell_tracker.lastModified = new Date().toISOString();
      metadata.cell_tracker.summary =
        options.summary || metadata.cell_tracker.summary;
    } else {
      // Create tracking metadata if it doesn't exist
      const now = new Date().toISOString();
      metadata.cell_tracker = {
        trackingId: trackingId,
        createdAt: now,
        lastModified: now,
        origin: 'ai', // Assume AI is editing
        summary: options.summary || ''
      };
    }

    // Update custom summary too
    if (!metadata.custom) {
      metadata.custom = {};
    }
    metadata.custom.summary = options.summary;
    cell.model.sharedModel.setMetadata(metadata);

    // Only display diff if explicitly requested, otherwise set content directly
    if (options.show_diff) {
      this.notebookTools.display_diff(
        cell,
        oldContent,
        options.new_source,
        'edit'
      );
    } else {
      // Set the new content directly
      cell.model.sharedModel.setSource(options.new_source);
    }

    // Handle smart scrolling after editing the cell - scroll to cell content only
    this.handleSmartScroll(cell.node);

    return true;
  }

  stream_edit_plan(options: {
    partial_plan: string;
    notebook_path?: string | null;
  }): boolean {
    const current = this.notebookTools.getCurrentNotebook(
      options.notebook_path
    );
    if (!current) {
      return false;
    }

    const { notebook } = current;

    // Get the first cell (plan cell)
    let planCell = null;

    for (let i = 0; i < notebook.widgets.length; i++) {
      const cell = notebook.widgets[i];
      if (this.isPlanCell(cell)) {
        planCell = cell;
      }
    }

    if (!planCell) {
      console.error('No first cell found for plan update');
      notebook.activeCellIndex = 0;
      const restoreScroll = NotebookCellTools.preventScrolling(notebook);
      NotebookActions.insertAbove(notebook);
      restoreScroll();
      notebook.activeCellIndex = 0;
      this.setFirstCellAsPlan(options.notebook_path);
    }
    const firstCell = notebook.widgets[0];

    const newContent = options.partial_plan;

    firstCell.model.sharedModel.setSource(newContent);

    // Handle smart scrolling after streaming plan update
    // this.handleSmartScroll(notebook);

    return true;
  }

  /**
   * Generates and updates the notebook plan based on immediate action.
   *
   * @param options Configuration options
   * @param options.immediate_action What the LLM is about to do next
   * @param options.notebook_path Path to the notebook file (optional)
   * @returns The generated plan string
   */
  async edit_plan(options: {
    immediate_action: string;
    notebook_path?: string | null;
  }): Promise<string | { error: true; errorText: string }> {
    const current = this.notebookTools.getCurrentNotebook(
      options.notebook_path
    );
    if (!current) {
      console.error('No notebook found for edit_plan');
      return '';
    }

    const { notebook } = current;

    // Capture initial state for potential restoration
    const originalActiveCellIndex = notebook.activeCellIndex;
    // Get current plan content
    let currentPlan = '';
    const firstCell = notebook.widgets[0];
    if (firstCell) {
      currentPlan = firstCell.model.sharedModel.getSource();
    }

    // Get notebook summary
    const notebookSummary = await this.notebookTools.getNotebookSummary(
      options.notebook_path || null
    );
    const summaryString = JSON.stringify(notebookSummary, null, 2);

    let planExisted = true;
    let originalMetadata: any = null;

    // Ensure plan cell exists before starting generation
    if (!firstCell || !this.isPlanCell(firstCell)) {
      planExisted = false;
      notebook.activeCellIndex = 0;
      const restoreScroll = NotebookCellTools.preventScrolling(notebook);
      NotebookActions.insertAbove(notebook);
      restoreScroll();
      notebook.activeCellIndex = 0;
      this.setFirstCellAsPlan(options.notebook_path);
    }

    const planCell = notebook.widgets[0];

    // Capture original metadata for restoration if needed
    if (planExisted) {
      originalMetadata = JSON.parse(
        JSON.stringify(planCell.model.sharedModel.getMetadata() || {})
      );
    }

    // Get tracking ID for consistent reference
    const metadata: any = planCell.model.sharedModel.getMetadata() || {};
    const trackingId = metadata.cell_tracker?.trackingId || 'planning_cell';

    // Activate the plan cell
    this.notebookTools.activateCell(planCell);

    // Update metadata
    if (metadata.cell_tracker) {
      metadata.cell_tracker.lastModified = new Date().toISOString();
      metadata.cell_tracker.summary = 'Updating plan...';
    } else {
      const now = new Date().toISOString();
      metadata.cell_tracker = {
        trackingId: trackingId,
        createdAt: now,
        lastModified: now,
        origin: 'ai',
        summary: 'Updating plan...'
      };
    }

    // Update custom summary
    if (!metadata.custom) {
      metadata.custom = {};
    }
    metadata.custom.summary = 'Updating plan...';
    planCell.model.sharedModel.setMetadata(metadata);

    // Initialize streaming content
    let streamedContent = '';

    // Create the user message with context
    const userMessage = `## Notebook Summary
${summaryString}

## Current Plan
${currentPlan || 'No existing plan'}

## Immediate Action
${options.immediate_action}

Generate an updated plan based on this context.`;

    try {
      // Get the chat service
      const chatService = AppStateService.getChatService();
      const modelName = chatService.getModelName();

      // Load the plan generation prompt
      // eslint-disable-next-line @typescript-eslint/no-var-requires
      const planPrompt = require('../Config/prompts/plan_generation_prompt.md');

      // Stream the plan generation with onTextChunk callback
      const generatedPlan = await chatService.sendEphemeralMessage(
        userMessage,
        planPrompt,
        modelName,
        (textChunk: string) => {
          // Append the new chunk to our streamed content
          streamedContent += textChunk;

          // Update the plan cell content in real-time
          planCell.model.sharedModel.setSource(streamedContent);

          // Handle smart scrolling to show the updated content
          this.handleSmartScroll(planCell.node);
        },
        { maxTokens: 2048 }
      );

      // Final content update (in case there are any remaining chunks)
      const finalContent = generatedPlan.trim();
      planCell.model.sharedModel.setSource(finalContent);

      const actionHistory = AppStateService.getState().actionHistory;
      actionHistory?.addAction(
        ActionType.EDIT_PLAN,
        {
          planExisted,
          oldPlan: currentPlan,
          oldCurrentStep: metadata.custom.current_step_string || '',
          oldNextStep: metadata.custom.next_step_string || ''
        },
        'Updated plan'
      );

      // Update metadata with final summary
      if (metadata.cell_tracker) {
        metadata.cell_tracker.lastModified = new Date().toISOString();
        metadata.cell_tracker.summary = 'Plan updated';
      }
      metadata.custom.summary = 'Plan updated';
      planCell.model.sharedModel.setMetadata(metadata);

      // Run the plan cell to display it
      const restoreScroll = NotebookCellTools.preventScrolling(notebook);
      void NotebookActions.runCells(notebook, [planCell]);
      restoreScroll();

      // Extract current and next steps from the generated plan
      const { currentStep, nextStep } = this.extractStepsFromPlan(
        finalContent,
        options.immediate_action
      );

      // Update metadata with extracted steps
      metadata.custom.current_step_string = currentStep;
      metadata.custom.next_step_string = nextStep;
      planCell.model.sharedModel.setMetadata(metadata);

      void AppStateService.getPlanStateDisplay().updatePlan(
        currentStep || '',
        nextStep,
        finalContent
      );

      console.log('Plan cell updated successfully with streaming');
      return finalContent;
    } catch (error: unknown) {
      console.error('[NotebookCellTools] Failed to generate plan:', error);

      try {
        // Restore initial state
        if (!planExisted) {
          // Plan cell was created during this operation, remove it
          const restoreScroll = NotebookCellTools.preventScrolling(notebook);
          notebook.activeCellIndex = 0; // Ensure the plan cell is selected
          NotebookActions.deleteCells(notebook);
          notebook.activeCellIndex = originalActiveCellIndex;
          restoreScroll();
        } else {
          // Plan cell existed, restore its original content and metadata
          const planCell = notebook.widgets[0];
          if (planCell) {
            // Restore original content
            planCell.model.sharedModel.setSource(currentPlan);

            // Restore original metadata
            if (originalMetadata) {
              planCell.model.sharedModel.setMetadata(originalMetadata);
            }
          }

          // Restore original active cell index
          notebook.activeCellIndex = originalActiveCellIndex;
        }
      } catch (restoreError) {
        console.error(
          '[NotebookCellTools] Failed to restore initial state after plan generation error:',
          restoreError
        );
        // Don't throw the restore error, continue with the original error
      }

      return {
        error: true,
        errorText: error instanceof Error ? error.message : String(error)
      };
    }
  }

  /**
   * Extract current and next steps from a plan based on immediate action
   */
  private extractStepsFromPlan(
    plan: string,
    immediateAction: string
  ): {
    currentStep: string;
    nextStep: string;
  } {
    const lines = plan.split('\n');
    const tasks: { text: string; completed: boolean }[] = [];

    // Extract all tasks from the plan (skip title line)
    for (const line of lines) {
      const taskMatch = line.match(/^-\s*\[\s*([x ])\s*\]\s*(.+)$/);
      if (taskMatch) {
        const completed = taskMatch[1] === 'x';
        const text = taskMatch[2].trim();
        tasks.push({ text, completed });
      }
    }

    // Find current step - either the one being worked on or first incomplete
    let currentStep = '';
    let nextStep = '';

    // Look for a task related to the immediate action
    const actionRelatedTask = tasks.find(
      task =>
        !task.completed &&
        (task.text.toLowerCase().includes(immediateAction.toLowerCase()) ||
          immediateAction.toLowerCase().includes(task.text.toLowerCase()))
    );

    if (actionRelatedTask) {
      currentStep = actionRelatedTask.text;
      // Find the next incomplete task after this one
      const currentIndex = tasks.indexOf(actionRelatedTask);
      const nextTask = tasks
        .slice(currentIndex + 1)
        .find(task => !task.completed);
      nextStep = nextTask ? nextTask.text : '';
    } else {
      const incompleteTasks = tasks.filter(task => !task.completed);
      currentStep = incompleteTasks[0]?.text || '';
      nextStep = incompleteTasks.length > 1 ? incompleteTasks[1]?.text : '';
    }

    return { currentStep, nextStep };
  }

  /**
   * Get information about all cells in the current notebook
   * @returns Array of cell info objects or null if no notebook
   */
  get_cells_info(notebookPath?: string | null): {
    cells: Array<{ id: string; type: string; content: string }>;
  } | null {
    const current = this.notebookTools.getCurrentNotebook(notebookPath);
    if (!current) return null;

    const { notebook } = current;
    const cells: Array<{ id: string; type: string; content: string }> = [];

    for (let i = 0; i < notebook.widgets.length; i++) {
      const cell = notebook.widgets[i];
      cells.push({
        id: cell.model.id,
        type: cell.model.type,
        content: cell.model.sharedModel.getSource()
      });
    }

    return { cells };
  }

  /**
   * Get detailed information about a specific cell
   * @param options Configuration options
   * @param options.cell_id Unique identifier of the cell
   * @returns Detailed information about the cell or null if not found
   */
  get_cell_info(options: {
    cell_id: string;
    notebook_path?: string | null;
  }): any {
    let cellInfo = this.notebookTools.findCellByAnyId(
      options.cell_id,
      options.notebook_path
    );
    if (!cellInfo) {
      return null;
    }

    const { cell, index } = cellInfo;

    // Get the cell metadata
    const metadata = cell.model.sharedModel.getMetadata();

    // Return detailed information about the cell
    return {
      id: cell.model.id,
      type: cell.model.type,
      content: cell.model.sharedModel.getSource(),
      index: index,
      custom: metadata?.custom || {},
      trackingId: (metadata?.cell_tracker as any)?.trackingId || null
    };
  }

  /**
   * This is just a placeholder method to match the localToolMap.
   * The actual edit_history functionality is handled on the server side.
   *
   * @param options Configuration options
   * @param options.limit Maximum number of history entries to return
   * @returns An empty array as this is just forwarded to the server
   */
  edit_history(options: { limit?: number }): any {
    console.log('Edit history requested with options:', options);
    // This is just a pass-through function - edit_history is handled server-side
    // The ToolService will forward this to the MCP server
    return { forwarded: true };
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
    const {
      notebook_path = null,
      include_outputs = true,
      include_metadata = true
    } = options;

    const current = this.notebookTools.getCurrentNotebook(notebook_path);
    if (!current) {
      console.log('No current notebook found');
      return null;
    }

    const { notebook, widget } = current;
    const cells: Array<{
      id: string;
      index: number;
      type: string;
      content: string;
      trackingId?: string;
      metadata?: any;
      outputs?: any[];
      execution_count?: number;
    }> = [];

    console.log(`Reading ${notebook.widgets.length} cells from notebook`);

    for (let i = 0; i < notebook.widgets.length; i++) {
      const cell = notebook.widgets[i];
      const cellModel = cell.model;
      const sharedModel = cellModel.sharedModel;

      // Basic cell information
      const cellInfo: {
        id: string;
        index: number;
        type: string;
        content: string;
        trackingId?: string;
        metadata?: any;
        outputs?: any[];
        execution_count?: number;
      } = {
        id: '',
        index: i,
        type: cellModel.type,
        content: sharedModel.getSource()
      };

      // Add metadata if requested
      if (include_metadata) {
        const metadata = sharedModel.getMetadata();
        cellInfo.metadata = metadata || {};

        // Extract tracking ID if available
        const cellTracker = metadata?.cell_tracker as any;
        if (cellTracker?.trackingId) {
          cellInfo.trackingId = cellTracker.trackingId;
        }
      }

      // Add outputs and execution count for code cells if requested
      if (include_outputs && cellModel.type === 'code') {
        try {
          const codeCell = cell as any;
          if (codeCell.outputArea && codeCell.outputArea.model.toJSON) {
            cellInfo.outputs = codeCell.outputArea.model.toJSON();
          }

          // Get execution count
          const executionCount = (cellModel as any).executionCount;
          if (executionCount !== null && executionCount !== undefined) {
            cellInfo.execution_count = executionCount;
          }
        } catch (error) {
          console.warn(`Failed to get outputs for cell ${cellInfo.id}:`, error);
          cellInfo.outputs = [];
        }
      }

      if (cellInfo.outputs && cellInfo.outputs.length > 0) {
        for (const output of cellInfo.outputs) {
          if (output.text && output.text.length > 5000) {
            output.text = output.text.slice(0, 5000);
          }

          if (output.output_type === 'display_data' && output.data) {
            output.data = output.data['text/plain'];
          }
        }
      }

      cells.push(cellInfo);
    }

    const result = {
      cells,
      total_cells: cells.length,
      notebook_path: widget.context.path
    };

    console.log(`Successfully read ${cells.length} cells from notebook`);
    console.log(result);
    return result;
  }

  /**
   * Scroll to show the cell content at the bottom of the viewport with smooth animation
   * @param cellNode The HTML node of the cell to scroll to
   * @param includeOutput Whether to include cell output in the scroll calculation (for run_cell)
   */
  private handleSmartScroll(
    cellNode: HTMLElement,
    includeOutput: boolean = false
  ): void {
    // Skip auto-scroll if disabled by user interaction
    if (this.isAutoScrollDisabled) {
      console.log('Auto-scroll disabled due to user interaction');
      return;
    }

    // Find the scrollable container with the jp-WindowedPanel-outer class
    const scrollContainer = cellNode.closest(
      '.jp-WindowedPanel-outer'
    ) as HTMLElement;

    if (!scrollContainer) {
      console.warn(
        'Could not find scroll container with class jp-WindowedPanel-outer'
      );
      return;
    }

    // Get the cell input area (the actual cell content, not output)
    const cellInputArea = cellNode.querySelector(
      '.jp-InputArea'
    ) as HTMLElement;
    if (!cellInputArea) {
      console.warn('Could not find cell input area');
      return;
    }

    let targetElement = cellInputArea;

    // For run_cell operations, include the output area if it exists
    if (includeOutput) {
      const outputArea = cellNode.querySelector(
        '.jp-OutputArea'
      ) as HTMLElement;
      if (outputArea && outputArea.children.length > 0) {
        targetElement = outputArea;
      }
    }

    // Set up scroll listener for this container if not already set
    this.setupScrollListener(scrollContainer, cellNode);

    // Get the bottom position of the target element relative to the scroll container
    const containerRect = scrollContainer.getBoundingClientRect();
    const targetRect = targetElement.getBoundingClientRect();

    // Calculate the scroll position to put the bottom of the target element
    // at the bottom of the viewport with 20px padding
    const targetBottom =
      targetRect.bottom - containerRect.top + scrollContainer.scrollTop;
    const desiredScrollTop = targetBottom - scrollContainer.clientHeight + 20;

    // Get current scroll position
    const currentScrollTop = scrollContainer.scrollTop;

    // Only scroll if the desired position is below the current position (scroll down only)
    // and if the user isn't already below the target area
    if (desiredScrollTop <= currentScrollTop) {
      console.log(
        'Skipping scroll - target is above current position or user is already below target'
      );
      return;
    }

    // Store reference to this cell for scroll detection
    this.lastAutoScrolledCell = cellNode;

    // Smooth scroll to the calculated position (only scrolling down)
    scrollContainer.scrollTo({
      top: Math.max(0, desiredScrollTop),
      behavior: 'smooth'
    });

    console.log(`Smart scrolled to cell content bottom with 20px padding`);
  }

  /**
   * Set up scroll listener to detect user scrolling away from auto-scrolled cells
   * @param scrollContainer The scroll container to monitor
   * @param currentCell The current cell being auto-scrolled to
   */
  private setupScrollListener(
    scrollContainer: HTMLElement,
    currentCell: HTMLElement
  ): void {
    // Remove existing listener if any
    const existingListener = this.scrollListeners.get(scrollContainer);
    if (existingListener) {
      scrollContainer.removeEventListener('scroll', existingListener);
    }

    let scrollTimeout: NodeJS.Timeout | null = null;
    let lastScrollTime = Date.now();
    let programmaticScroll = true; // Flag to ignore the initial programmatic scroll

    const scrollListener = () => {
      const now = Date.now();

      // Ignore scroll events that happen immediately after we set programmaticScroll
      // This gives time for our smooth scroll to complete
      if (programmaticScroll && now - lastScrollTime < 1000) {
        return;
      }

      programmaticScroll = false;

      // Clear any existing timeout
      if (scrollTimeout) {
        clearTimeout(scrollTimeout);
      }

      // Debounce scroll events to avoid excessive checking
      scrollTimeout = setTimeout(() => {
        this.checkUserScrolledAway(scrollContainer, currentCell);
      }, 100);
    };

    // Reset the flag after our programmatic scroll
    setTimeout(() => {
      programmaticScroll = false;
      lastScrollTime = Date.now();
    }, 100);

    scrollContainer.addEventListener('scroll', scrollListener, {
      passive: true
    });
    this.scrollListeners.set(scrollContainer, scrollListener);
  }

  /**
   * Check if user has scrolled away from the bottom or back to the bottom of the notebook
   * @param scrollContainer The scroll container
   * @param currentCell The current cell we auto-scrolled to (not used in new logic)
   */
  private checkUserScrolledAway(
    scrollContainer: HTMLElement,
    currentCell: HTMLElement
  ): void {
    // Get the actual notebook instance
    const current = this.notebookTools.getCurrentNotebook();
    if (!current) return;

    const { notebook } = current;

    // Get the last cell from the notebook widgets
    if (notebook.widgets.length === 0) return;

    const lastCell = notebook.widgets[notebook.widgets.length - 1];
    const lastCellNode = lastCell.node;
    const lastCellInput = lastCellNode.querySelector(
      '.jp-InputArea'
    ) as HTMLElement;
    if (!lastCellInput) return;

    // Calculate scroll position information
    const scrollTop = scrollContainer.scrollTop;
    const scrollHeight = scrollContainer.scrollHeight;
    const clientHeight = scrollContainer.clientHeight;

    // Get container and last cell positions
    const containerRect = scrollContainer.getBoundingClientRect();
    const lastCellInputRect = lastCellInput.getBoundingClientRect();

    // Calculate if we're near the bottom of the scrollable area (within 100px)
    const distanceFromBottom = scrollHeight - (scrollTop + clientHeight);
    const isNearScrollBottom = distanceFromBottom <= 10;

    // Calculate if the last cell's input area is visible in the viewport
    // The cell is considered visible if its bottom edge is within the viewport bounds (with buffer)
    const lastCellInputBottom = lastCellInputRect.bottom;
    const containerBottom = containerRect.bottom;
    const isLastCellVisible = lastCellInputBottom <= containerBottom + 20; // 50px buffer

    // User is considered "at the bottom" if either condition is true:
    // 1. They're scrolled near the bottom of the document
    // 2. The last cell's input area is visible in the viewport
    const isAtBottom = isNearScrollBottom || isLastCellVisible;

    // Update auto-scroll state based on position
    if (isAtBottom && this.isAutoScrollDisabled) {
      this.isAutoScrollDisabled = false;
      console.log('User scrolled back to bottom, enabling auto-scroll', {
        isNearScrollBottom,
        isLastCellVisible,
        distanceFromBottom
      });
    } else if (!isAtBottom && !this.isAutoScrollDisabled) {
      this.isAutoScrollDisabled = true;
      console.log('User scrolled away from bottom, disabling auto-scroll', {
        isNearScrollBottom,
        isLastCellVisible,
        distanceFromBottom
      });
    }
  }

  /**
   * Clean up scroll listeners
   */
  private cleanupScrollListeners(): void {
    for (const [container, listener] of this.scrollListeners) {
      container.removeEventListener('scroll', listener);
    }
    this.scrollListeners.clear();
  }

  /**
   * Public cleanup method to be called when the instance is no longer needed
   */
  public dispose(): void {
    this.cleanupScrollListeners();
    this.isAutoScrollDisabled = false;
    this.lastAutoScrolledCell = null;
  }

  /**
   * Prevent scrolling to a cell or item in the notebook
   * @param notebook The notebook to prevent scrolling from
   * @returns A function to restore the default scrolling behavior
   */
  static preventScrolling(notebook: Notebook): () => void {
    // Save the reference to the default scrollToCell method
    const scrollToCellDefault = notebook.scrollToCell;
    const scrollToItemDefault = notebook.scrollToItem;

    notebook.scrollToCell = () => Promise.resolve();
    notebook.scrollToItem = () => Promise.resolve();

    return () => {
      // Restore the default scrollToCell method
      notebook.scrollToCell = scrollToCellDefault;
      notebook.scrollToItem = scrollToItemDefault;
    };
  }
}
