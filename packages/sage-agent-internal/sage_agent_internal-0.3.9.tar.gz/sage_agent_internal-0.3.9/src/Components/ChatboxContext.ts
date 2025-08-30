import { ChatMessages } from '../Chat/ChatMessages';
import { ChatInputManager } from '../Chat/ChatInputManager';
import { AppStateService } from '../AppState';
import { ContextService } from '../Services/ContextService';

/**
 * ChatboxContext: Handles all context-related functionality for the ChatBoxWidget
 */
export class ChatboxContext {
  private messageComponent: ChatMessages;
  private inputManager: ChatInputManager;
  private chatboxNode: HTMLElement;
  private contextService: ContextService;

  constructor(
    messageComponent: ChatMessages,
    inputManager: ChatInputManager,
    chatboxNode: HTMLElement
  ) {
    this.messageComponent = messageComponent;
    this.inputManager = inputManager;
    this.chatboxNode = chatboxNode;
    this.contextService = ContextService.getInstance();

    // Subscribe to context changes to refresh displays
    this.subscribeToContextChanges();
  }

  /**
   * Handle a cell being added to context
   * @param notebookId Path of the notebook containing the cell
   * @param cellId ID of the cell added to context
   */
  public onCellAddedToContext(notebookId: string): void {
    const contextManager = AppStateService.getNotebookContextManager();
    if (!contextManager) {
      console.error(
        'Required services not initialized: contextManager is null'
      );
      return;
    }

    const currentNotebookId = AppStateService.getCurrentNotebookId();
    if (currentNotebookId !== notebookId) {
      console.error('Cell context notebook ID mismatch');
      return;
    }

    // Get context cells from the notebookId
    const contextCells = contextManager.getContextCells(notebookId);

    // Update UI to show that context cells are available
    this.updateContextCellsIndicator(contextCells.length);
  }

  /**
   * Handle a cell being removed from context
   * @param notebookId Path of the notebook containing the cell
   * @param cellId ID of the cell removed from context
   */
  public onCellRemovedFromContext(notebookId: string): void {
    const contextManager = AppStateService.getNotebookContextManager();
    if (!contextManager) {
      console.error(
        'Required services not initialized: contextManager is null'
      );
      return;
    }

    const currentNotebookId = AppStateService.getCurrentNotebookId();
    if (currentNotebookId !== notebookId) {
      console.error('Cell context notebook ID mismatch');
      return;
    }

    // Get updated context cells from the notebookId
    const contextCells = contextManager.getContextCells(notebookId);

    // Update UI to show the current context cells count
    this.updateContextCellsIndicator(contextCells.length);
  }

  /**
   * Update UI to show number of cells in context and mention contexts
   */
  public updateContextDisplay(): void {
    // Find the inline context display within the chatbox wrapper
    let indicator = this.chatboxNode.querySelector(
      '.sage-ai-context-display-inline'
    );
    if (!indicator) {
      console.warn('Context display container not found');
      return;
    }

    // Find the context row for visibility management
    const contextRow = this.chatboxNode.querySelector('.sage-ai-context-row');

    // Clear previous content
    indicator.innerHTML = '';

    // Get context cells (full objects)
    const notebookId = AppStateService.getCurrentNotebookId();
    const contextManager = AppStateService.getNotebookContextManager();
    const contextCells =
      notebookId && contextManager
        ? contextManager.getContextCells(notebookId)
        : [];

    // Get mention contexts from ChatMessages
    const mentionContextsArray = Array.from(
      this.messageComponent.getMentionContexts().values()
    );

    // Calculate total context items
    const totalContextItems = contextCells.length + mentionContextsArray.length;

    if (totalContextItems > 0) {
      indicator.classList.remove('hidden');
      if (contextRow) {
        contextRow.classList.remove('context-row-hidden');
      }

      // Container for the context items
      const contextItemsContainer = document.createElement('div');
      contextItemsContainer.className = 'sage-ai-context-items-inline';

      // Add cell contexts
      for (const cell of contextCells) {
        const box = document.createElement('div');
        box.className = 'sage-ai-context-cell-box-inline';
        box.title = cell.content || 'Empty cell';

        // Delete icon
        const del = document.createElement('span');
        del.className = 'sage-ai-context-cell-delete';
        del.textContent = '×';
        del.title = 'Remove from context';
        del.addEventListener('click', e => {
          e.stopPropagation();
          if (notebookId && contextManager) {
            contextManager.removeCellFromContext(notebookId, cell.cellId);
            this.updateContextDisplay(); // Will re-fetch
            // Also notify parent if needed
            this.onCellRemovedFromContext(notebookId);
            // Update context buttons in notebook cells
            const notebookTools = AppStateService.getNotebookTools();
            const currentNotebookPanel =
              notebookTools.getCurrentNotebook()?.widget;
            if (currentNotebookPanel) {
              const contextCellHighlighter =
                AppStateService.getContextCellHighlighter();
              contextCellHighlighter.addContextButtonsToAllCells(
                currentNotebookPanel
              );
            }
          }
        });

        // Move icon to left: append first, then text
        box.appendChild(del);
        const text = document.createElement('span');
        text.textContent = cell.cellId;
        box.appendChild(text);
        contextItemsContainer.appendChild(box);
      }

      // Add mention contexts
      for (const context of mentionContextsArray) {
        const box = document.createElement('div');
        box.className = 'sage-ai-context-cell-box-inline';
        box.title =
          context.description ||
          context.content ||
          `${context.type}: ${context.name}`;

        // Set background color based on context type
        let backgroundColor = '#4a5568'; // default gray
        switch (context.type) {
          case 'snippets':
            backgroundColor = 'rgba(156, 39, 176, 0.2)'; // dark gray
            break;
          case 'data':
            backgroundColor = 'rgba(33, 150, 243, 0.2)'; // blue
            break;
          case 'variable':
            backgroundColor = 'rgba(76, 175, 80, 0.2)'; // green
            break;
          case 'cell':
            backgroundColor = 'rgba(255, 152, 0, 0.2)'; // yellow
            break;
          default:
            backgroundColor = '#4a5568'; // gray
        }
        box.style.backgroundColor = `${backgroundColor}`;
        box.style.color = 'var(--jp-ui-font-color0)';

        // Delete icon
        const del = document.createElement('span');
        del.className = 'sage-ai-context-cell-delete';
        del.textContent = '×';
        del.title = 'Remove from context';
        del.addEventListener('click', e => {
          e.stopPropagation();
          this.messageComponent.removeMentionContext(context.id);
          this.updateContextDisplay();

          // Also remove from the input manager
          if (this.inputManager) {
            // Clear the mention from the input text
            const currentInput = this.inputManager.getCurrentInputValue();
            const escapedName = context.name.replace(
              /[-\/\\^$*+?.()|[\]{}]/g,
              '\\$&'
            );
            const cleanedInput = currentInput
              .replace(new RegExp(`@\\{?${escapedName}\\}?`, 'g'), '')
              .trim();
            this.inputManager.setInputValue(cleanedInput);
          }
        });

        // Append elements
        box.appendChild(del);
        const text = document.createElement('span');
        text.textContent = context.name;
        box.appendChild(text);
        contextItemsContainer.appendChild(box);
      }

      indicator.appendChild(contextItemsContainer);
    }
  }

  /**
   * Update the context cells indicator
   * @param count Number of context cells
   */
  public updateContextCellsIndicator(_count: number): void {
    this.updateContextDisplay();
  }

  /**
   * Get current mention contexts for sending to LLM
   */
  public getMentionContexts(): Array<{
    name: string;
    content: string;
    type: string;
    description?: string;
  }> {
    return Array.from(this.messageComponent.getMentionContexts().values()).map(
      context => ({
        name: context.name,
        content: context.content || '',
        type: context.type,
        description: context.description
      })
    );
  }

  /**
   * Clear mention contexts (for new chat or when needed)
   */
  public clearMentionContexts(): void {
    this.messageComponent.setMentionContexts(new Map());
    this.updateContextDisplay();
  }

  /**
   * Get current context message for LLM
   */
  public getCurrentContextMessage(): string {
    let message = "The user's message has the following provided context:\n\n";

    const mentionContexts = this.messageComponent.getMentionContexts();
    for (const [contextId, context] of mentionContexts.entries()) {
      console.log(contextId);
      console.log(context);
      message += `@${context.name} (ID: ${context.id}) described as: ${context.description} has the following content: \n${context.content}\n\n`;
    }

    return message.trim();
  }

  /**
   * Subscribe to context changes to refresh displays when contexts become available
   */
  private subscribeToContextChanges(): void {
    this.contextService.subscribe(() => {
      // Refresh the context display when contexts change
      this.updateContextDisplay();
    });
  }
}
