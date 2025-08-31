import { PanelLayout, Widget } from '@lumino/widgets';
import { ChatBoxWidget } from '../Components/chatbox';
import { ToolService } from '../Services/ToolService';
import { NotebookContextManager } from './NotebookContextManager';
import { AppStateService } from '../AppState';
import { ActionHistory } from '../Chat/ActionHistory';

/**
 * Container widget that holds only the chat widget
 */
export class NotebookChatContainer extends Widget {
  public chatWidget: ChatBoxWidget;
  private toolService: ToolService;
  private contextManager: NotebookContextManager | null;
  private currentNotebookId: string | null = null;

  constructor(
    toolService: ToolService,
    contextManager: NotebookContextManager | null | undefined,
    actionHistory: ActionHistory
  ) {
    super();

    this.id = 'sage-ai-chat-container';
    this.title.label = 'Sage AI Chat';
    this.title.closable = true;
    this.addClass('sage-ai-chat-container');
    this.toolService = toolService;
    this.contextManager = contextManager || null;

    // Set the minimum width of the widget's node
    this.node.style.minWidth = '320px';

    // Create chat widget with contextCellHighlighter
    this.chatWidget = new ChatBoxWidget(actionHistory);

    // Create layout for the container
    const layout = new PanelLayout();
    layout.addWidget(this.chatWidget);

    // Set the layout properly
    this.layout = layout;

    // Subscribe to notebook changes from AppStateService
    AppStateService.onNotebookChanged().subscribe(async ({ newNotebookId }) => {
      if (newNotebookId && newNotebookId !== this.currentNotebookId) {
        await this.switchToNotebook(newNotebookId);
      }
    });

    // AppStateService.onNotebookRenamed().subscribe(
    //   ({ oldNotebookId, newNotebookId }) => {
    //     this.updateNotebookId(oldNotebookId, newNotebookId);
    //   }
    // );
  }

  public updateNotebookId(oldNotebookId: string, newNotebookId: string): void {
    this.contextManager?.updateNotebookId(oldNotebookId, newNotebookId);

    this.chatWidget.chatHistoryManager.updateNotebookId(
      oldNotebookId,
      newNotebookId
    );

    this.chatWidget.updateNotebookPath(newNotebookId);

    this.toolService.updateNotebookId(oldNotebookId, newNotebookId);

    this.currentNotebookId = newNotebookId;
  }

  /**
   * Switch to a different notebook
   * @param notebookId ID of the notebook
   */
  public async switchToNotebook(notebookId: string): Promise<void> {
    if (this.currentNotebookId === notebookId) {
      // Already on this notebook, nothing to do
      return;
    }

    console.log(`[NotebookChatContainer] Switching to notebook: ${notebookId}`);
    this.currentNotebookId = notebookId;

    // Update the tool service with the new notebook ID
    this.toolService.setCurrentNotebookId(notebookId);

    // Update the notebook context manager if available
    if (this.contextManager) {
      this.contextManager.getContext(notebookId);
    }

    // Update the widget with the new notebook ID (using path method for backward compatibility)
    await this.chatWidget.setNotebookId(notebookId);
  }

  /**
   * Handle a cell added to context
   * @param notebookId ID of the notebook containing the cell
   * @param cellId ID of the cell added to context
   */
  public onCellAddedToContext(notebookId: string): void {
    if (!this.currentNotebookId || this.currentNotebookId !== notebookId) {
      console.warn(
        `Cannot add cell from ${notebookId} to context when current notebook is ${this.currentNotebookId}`
      );
      return;
    }

    // Pass the event to the chatbox
    this.chatWidget.onCellAddedToContext(notebookId);
  }

  /**
   * Handle a cell removed from context
   * @param notebookId ID of the notebook containing the cell
   */
  public onCellRemovedFromContext(notebookId: string): void {
    if (!this.currentNotebookId || this.currentNotebookId !== notebookId) {
      console.warn(
        `Cannot remove cell from ${notebookId} context when current notebook is ${this.currentNotebookId}`
      );
      return;
    }

    // Pass the event to the chatbox
    this.chatWidget.onCellRemovedFromContext(notebookId);
  }
}
