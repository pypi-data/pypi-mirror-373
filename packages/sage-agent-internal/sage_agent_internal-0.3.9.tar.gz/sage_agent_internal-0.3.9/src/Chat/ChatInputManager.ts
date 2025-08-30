import { ChatHistoryManager } from './ChatHistoryManager';
import {
  ChatContextMenu,
  MentionContext
} from './ChatContextMenu/ChatContextMenu';
import { Contents } from '@jupyterlab/services';
import { ToolService } from '../Services/ToolService';
import { RichTextChatInput } from './RichTextChatInput';
import { IChatService } from '../Services/IChatService';
import { ConversationService } from './ConversationService';
import { ChatMessages } from './ChatMessages';
import { ChatUIHelper } from './ChatUIHelper';
import { ChatboxContext } from '../Components/ChatboxContext';
import { ChatRequestStatus } from '../types';
import { AppStateService } from '../AppState';
import { NotebookCellStateService } from '../Services/NotebookCellStateService';
import { convertMentionsToContextTags } from '../utils/contextTagUtils';

/**
 * Input element type that supports both textarea and rich text input
 */
type ChatInputElement = HTMLTextAreaElement | RichTextChatInput;

/**
 * Manages chat input functionality
 */
export class ChatInputManager {
  private chatInput: ChatInputElement;
  private chatHistoryManager: ChatHistoryManager;
  private userMessageHistory: string[] = [];
  private historyPosition: number = -1;
  private unsavedInput: string = '';
  private mentionDropdown: ChatContextMenu;

  // Add map to track all currently active mentions by context.id
  private activeContexts: Map<string, MentionContext> = new Map();

  private onContextSelected: ((context: MentionContext) => void) | null = null;
  private onContextRemoved: ((context_id: string) => void) | null = null;
  private onResetChat: (() => void) | null = null;

  // Dependencies for sendMessage and revertAndSend
  private chatService?: IChatService;
  private conversationService?: ConversationService;
  private messageComponent?: ChatMessages;
  private uiHelper?: ChatUIHelper;
  private contextHandler?: ChatboxContext;
  private sendButton?: HTMLButtonElement;
  private modeSelector?: HTMLElement;
  private modeName: 'agent' | 'ask' | 'fast' = 'agent';
  private isProcessingMessage: boolean = false;
  private updateUndoButtonState?: () => void;
  private cancelMessage?: () => void;
  private onMessageSent?: () => void;

  constructor(
    chatInput: ChatInputElement,
    chatHistoryManager: ChatHistoryManager,
    inputContainer: HTMLElement,
    contentManager: Contents.IManager,
    toolService: ToolService,
    onContextSelected?: (context: MentionContext) => void,
    onContextRemoved?: (context_id: string) => void,
    onResetChat?: () => void
  ) {
    this.chatInput = chatInput;
    this.chatHistoryManager = chatHistoryManager;
    this.onContextSelected = onContextSelected || null;
    this.onContextRemoved = onContextRemoved || null;
    this.onResetChat = onResetChat || null;

    // Initialize the mention dropdown
    const inputElement = this.isRichTextInput(chatInput)
      ? chatInput.getInputElement()
      : chatInput;
    this.mentionDropdown = new ChatContextMenu(
      inputElement as HTMLElement, // Changed to HTMLElement
      inputContainer,
      contentManager,
      toolService
    );

    // Set up event handlers for textarea
    this.setupEventHandlers();

    // Load user message history
    this.loadUserMessageHistory();

    // Set up the context selection callback for the mention dropdown
    this.mentionDropdown.setContextSelectedCallback(
      (context: MentionContext) => {
        // Store the context when selected
        this.activeContexts.set(context.id, context);

        // Update rich text input contexts if applicable
        if (this.isRichTextInput(this.chatInput)) {
          this.chatInput.setActiveContexts(this.activeContexts);
        }

        if (this.onContextSelected) {
          this.onContextSelected(context);
        }
      }
    );
  }

  /**
   * Set up event handlers for textarea
   */
  private setupEventHandlers(): void {
    const inputElement = this.isRichTextInput(this.chatInput)
      ? this.chatInput.getInputElement()
      : this.chatInput;

    // Auto-resize the textarea as content grows
    if (this.isRichTextInput(this.chatInput)) {
      this.chatInput.addInputEventListener('input', () => {
        this.resizeTextarea();
      });
    } else {
      inputElement.addEventListener('input', () => {
        this.resizeTextarea();
      });
    }

    // Handle keydown events for submission and special key combinations
    const keydownHandler = (event: Event) => {
      const keyEvent = event as KeyboardEvent;

      // Handle tab and enter when mention dropdown is visible
      if (this.mentionDropdown.getIsVisible()) {
        if (keyEvent.key === 'Tab') {
          keyEvent.preventDefault();
          this.handleTabCompletion();
          return;
        }
        if (keyEvent.key === 'Enter') {
          keyEvent.preventDefault();
          this.handleEnterWithMention();
          return;
        }
      }

      // Handle enter for message submission
      if (keyEvent.key === 'Enter') {
        if (keyEvent.shiftKey) {
          // Allow Shift+Enter for new lines
          return;
        }

        // Check if we have a complete mention that should be processed first
        if (this.hasCompleteMentionAtCursor()) {
          keyEvent.preventDefault();
          this.processCompleteMention();
          return;
        }

        // Normal enter - send message
        keyEvent.preventDefault();
        this.sendMessage();
        return;
      }

      // Message history navigation with arrow keys
      if (keyEvent.key === 'ArrowUp') {
        // Only navigate history if cursor is at the beginning of the text or input is empty
        if (this.getSelectionStart() === 0 || this.getInputValue() === '') {
          keyEvent.preventDefault();
          this.navigateHistory('up');
        }
      } else if (keyEvent.key === 'ArrowDown') {
        // Only navigate history if cursor is at the end of the text or input is empty
        if (
          this.getSelectionStart() === this.getInputLength() ||
          this.getInputValue() === ''
        ) {
          keyEvent.preventDefault();
          this.navigateHistory('down');
        }
      }
    };

    if (this.isRichTextInput(this.chatInput)) {
      this.chatInput.addInputEventListener('keydown', keydownHandler);
    } else {
      inputElement.addEventListener('keydown', keydownHandler);
    }
  }

  /**
   * Load the user's message history from all chat threads
   */
  public loadUserMessageHistory(): void {
    this.userMessageHistory = [];

    // Iterate through all notebooks
    const notebookIds = this.chatHistoryManager.getNotebookIds();
    for (const notebookId of notebookIds) {
      // Get all threads for this notebook
      const threads = this.chatHistoryManager.getThreadsForNotebook(notebookId);
      if (!threads) continue;

      // Extract user messages from each thread
      for (const thread of threads) {
        const userMessages = thread.messages
          .filter(msg => msg.role === 'user' && typeof msg.content === 'string')
          .map(msg => (typeof msg.content === 'string' ? msg.content : ''));

        // Add non-empty messages to history
        userMessages.forEach(msg => {
          if (msg && !this.userMessageHistory.includes(msg)) {
            this.userMessageHistory.push(msg);
          }
        });
      }
    }

    // Reset the position to start at the most recent message
    this.historyPosition = -1;
    this.unsavedInput = '';

    // Sort the history so the most recently used messages are at the end
    // This makes arrow-key navigation more intuitive
    this.userMessageHistory.sort((a, b) => {
      // Keep shorter messages (which tend to be more general/reusable) at the end
      if (a.length !== b.length) {
        return a.length - b.length;
      }
      return a.localeCompare(b);
    });

    console.log(
      `[ChatInputManager] Loaded ${this.userMessageHistory.length} user messages for history navigation`
    );
  }

  /**
   * Navigate through user message history
   * @param direction 'up' for older messages, 'down' for newer messages
   */
  public navigateHistory(direction: 'up' | 'down'): void {
    // If no history, nothing to do
    if (this.userMessageHistory.length === 0) {
      return;
    }

    // Save current input if this is the first navigation action
    if (this.historyPosition === -1) {
      this.unsavedInput = this.getInputValue();
    }

    if (direction === 'up') {
      // Navigate to previous message (older)
      if (this.historyPosition < this.userMessageHistory.length - 1) {
        this.historyPosition++;
        const historyMessage =
          this.userMessageHistory[
            this.userMessageHistory.length - 1 - this.historyPosition
          ];
        this.setInputValue(historyMessage);
        // Place cursor at end of text
        const length = historyMessage.length;
        this.setSelectionRange(length, length);
      }
    } else {
      // Navigate to next message (newer)
      if (this.historyPosition > 0) {
        this.historyPosition--;
        const historyMessage =
          this.userMessageHistory[
            this.userMessageHistory.length - 1 - this.historyPosition
          ];
        this.setInputValue(historyMessage);
        // Place cursor at end of text
        const length = historyMessage.length;
        this.setSelectionRange(length, length);
      } else if (this.historyPosition === 0) {
        // Restore the unsaved input when reaching the bottom of history
        this.historyPosition = -1;
        this.setInputValue(this.unsavedInput);
        // Place cursor at end of text
        const length = this.unsavedInput.length;
        this.setSelectionRange(length, length);
      }
    }

    // Resize the textarea to fit the content
    this.resizeTextarea();
  }
  /**
   * Resize the textarea based on its content
   */
  public resizeTextarea(): void {
    if (this.isRichTextInput(this.chatInput)) {
      // Reset height to auto to get the correct scrollHeight
      this.chatInput.setHeight('auto');
      // Set the height to match the content (with a max height)
      const maxHeight = 150; // Maximum height in pixels
      const scrollHeight = this.chatInput.getScrollHeight();
      if (scrollHeight <= maxHeight) {
        this.chatInput.setHeight(scrollHeight + 'px');
        this.chatInput.setOverflowY('hidden');
      } else {
        this.chatInput.setHeight(maxHeight + 'px');
        this.chatInput.setOverflowY('auto');
      }
    } else {
      // Reset height to auto to get the correct scrollHeight
      this.chatInput.style.height = 'auto';
      // Set the height to match the content (with a max height)
      const maxHeight = 150; // Maximum height in pixels
      const scrollHeight = this.chatInput.scrollHeight;
      if (scrollHeight <= maxHeight) {
        this.chatInput.style.height = scrollHeight + 'px';
        this.chatInput.style.overflowY = 'hidden';
      } else {
        this.chatInput.style.height = maxHeight + 'px';
        this.chatInput.style.overflowY = 'auto';
      }
    }
  }

  /**
   * Set the value for either input type
   */
  public setInputValue(value: string): void {
    if (this.isRichTextInput(this.chatInput)) {
      this.chatInput.setPlainText(value);
    } else {
      this.chatInput.value = value;
    }

    // Trigger input event to detect removed contexts
    // this.detectDeletedContexts();
  }

  /**
   * Get the plain text value from either input type
   */
  private getInputValue(): string {
    if (this.isRichTextInput(this.chatInput)) {
      return this.chatInput.getPlainText().trim();
    } else {
      return this.chatInput.value.trim();
    }
  }

  /**
   * Check if the input is a RichTextChatInput
   */
  private isRichTextInput(input: ChatInputElement): input is RichTextChatInput {
    return input instanceof RichTextChatInput;
  }

  /**
   * Get selection start position for either input type
   */
  private getSelectionStart(): number {
    if (this.isRichTextInput(this.chatInput)) {
      return this.chatInput.getSelectionStart();
    } else {
      return this.chatInput.selectionStart || 0;
    }
  }

  /**
   * Set selection range for either input type
   */
  private setSelectionRange(start: number, end: number): void {
    if (this.isRichTextInput(this.chatInput)) {
      this.chatInput.setSelectionRange(start, end);
    } else {
      this.chatInput.selectionStart = start;
      this.chatInput.selectionEnd = end;
    }
  }

  /**
   * Get the current input text length
   */
  private getInputLength(): number {
    return this.getInputValue().length;
  }

  /**
   * Clear the input
   */
  public clearInput(): void {
    if (this.isRichTextInput(this.chatInput)) {
      this.chatInput.clear();
    } else {
      this.chatInput.value = '';
      this.chatInput.style.height = 'auto'; // Reset height after clearing
    }
    this.focus();
  }

  /**
   * Add a message to history
   */
  public addToHistory(message: string): void {
    if (!this.userMessageHistory.includes(message)) {
      this.userMessageHistory.push(message);
    }

    // Reset history navigation
    this.historyPosition = -1;
    this.unsavedInput = '';
  }

  /**
   * Focus the input
   */
  public focus(): void {
    if (this.isRichTextInput(this.chatInput)) {
      this.chatInput.focus();
    } else {
      this.chatInput.focus();
    }
  }

  /**
   * Get the current input value (public method)
   */
  public getCurrentInputValue(): string {
    return this.getInputValue();
  }

  /**
   * Set the dependencies needed for sendMessage and revertAndSend functionality
   */
  public setDependencies(dependencies: {
    chatService: IChatService;
    conversationService: ConversationService;
    messageComponent: ChatMessages;
    uiHelper: ChatUIHelper;
    contextHandler: ChatboxContext;
    sendButton: HTMLButtonElement;
    modeSelector: HTMLElement;
    updateUndoButtonState: () => void;
    cancelMessage: () => void;
    onMessageSent?: () => void;
  }): void {
    this.chatService = dependencies.chatService;
    this.conversationService = dependencies.conversationService;
    this.messageComponent = dependencies.messageComponent;
    this.uiHelper = dependencies.uiHelper;
    this.contextHandler = dependencies.contextHandler;
    this.sendButton = dependencies.sendButton;
    this.modeSelector = dependencies.modeSelector;
    this.updateUndoButtonState = dependencies.updateUndoButtonState;
    this.cancelMessage = dependencies.cancelMessage;
    this.onMessageSent = dependencies.onMessageSent;
  }

  /**
   * Set the mode name
   */
  public setModeName(modeName: 'agent' | 'ask' | 'fast'): void {
    this.modeName = modeName;
  }

  /**
   * Get the current processing state
   */
  public getIsProcessingMessage(): boolean {
    return this.isProcessingMessage;
  }

  /**
   * Set the processing state
   */
  public setIsProcessingMessage(value: boolean): void {
    this.isProcessingMessage = value;
  }

  /**
   * Send a message to the AI service
   */
  public async sendMessage(cell_context?: string): Promise<void> {
    // Check if dependencies are set
    if (
      !this.chatService ||
      !this.conversationService ||
      !this.messageComponent ||
      !this.uiHelper ||
      !this.contextHandler ||
      !this.sendButton ||
      !this.modeSelector
    ) {
      console.error(
        'ChatInputManager dependencies not set. Call setDependencies() first.'
      );
      return;
    }

    const userInput = this.getCurrentInputValue();
    if (!userInput || this.isProcessingMessage) {
      return;
    }

    // Hide the waiting reply box when user sends a message
    AppStateService.getWaitingUserReplyBoxManager().hide();

    // Special command to reset the chat
    if (userInput.toLowerCase() === 'reset') {
      // We'll need to add a callback for this
      if (this.onResetChat) {
        this.onResetChat();
      }
      this.clearInput();
      return;
    }

    // Add message to history navigation
    this.addToHistory(userInput);

    // Notify that a message is being sent (triggers switch to history widget)
    if (this.onMessageSent) {
      this.onMessageSent();
    }

    // Set processing state
    this.isProcessingMessage = true;
    this.uiHelper.updateSendButton(this.sendButton, true);
    AppStateService.getPlanStateDisplay().setLoading(true);
    this.uiHelper.updateAgentModeElement(this.modeSelector, true);

    // Reset LLM state display to generating state, clearing any diff state
    this.uiHelper.resetToGeneratingState('Generating...');

    // Check if the chat client has been properly initialized
    if (!this.chatService.isInitialized()) {
      this.messageComponent.addSystemMessage(
        '❌ API key is not set. Please configure it in the settings.'
      );
      this.isProcessingMessage = false;
      this.uiHelper.updateSendButton(this.sendButton, false);
      AppStateService.getPlanStateDisplay().setLoading(false);
      this.uiHelper.updateAgentModeElement(this.modeSelector, false);
      this.uiHelper.hideLoadingIndicator();
      return;
    }
    const system_messages: string[] = [];
    // Clear the input
    this.clearInput();

    // Convert @mentions to context tags for message processing
    const processedUserInput = convertMentionsToContextTags(
      userInput,
      this.activeContexts
    );
    console.log('[ChatInputManager] Original message:', userInput);
    console.log(
      '[ChatInputManager] Processed message with context tags:',
      processedUserInput
    );

    // Display the user message in the UI (with context tags for proper styling)
    this.messageComponent.addUserMessage(processedUserInput, userInput);

    // Initialize messages with the user query (with context tags for API processing)
    const newUserMessage = { role: 'user', content: processedUserInput };

    try {
      // Make sure the conversation service knows which notebook we're targeting
      const currentNotebookId = AppStateService.getCurrentNotebookId();
      if (currentNotebookId) {
        this.conversationService.setNotebookId(currentNotebookId);

        const cellChanges =
          await NotebookCellStateService.detectChanges(currentNotebookId);
        const changesSummary =
          NotebookCellStateService.generateChangeSummaryMessage(cellChanges);
        if (changesSummary) {
          system_messages.push(changesSummary);
          console.log(
            '[ChatInputManager] Detected notebook changes, added to system messages'
          );
        }
      }

      // Add cell changes to system messages if there are any

      const messages = [newUserMessage];
      if (cell_context) {
        system_messages.push(cell_context);
      }
      const mentionContexts = this.messageComponent.getMentionContexts();
      if (mentionContexts.size > 0) {
        system_messages.push(this.contextHandler.getCurrentContextMessage());
      }

      // Proceed with sending the message

      AppStateService.getNotebookDiffManager().clearDiffs();

      await this.conversationService.processConversation(
        messages,
        system_messages,
        this.modeName
      );

      // Cache the current notebook state after successful message processing
      if (currentNotebookId)
        await NotebookCellStateService.cacheCurrentNotebookState(
          currentNotebookId
        );
      console.log(
        '[ChatInputManager] Cached notebook state after message processing'
      );
    } catch (error) {
      console.error('Error in conversation processing:', error);

      // Only show error if we're not cancelled
      if (this.chatService.getRequestStatus() !== ChatRequestStatus.CANCELLED) {
        this.messageComponent.addErrorMessage(
          `❌ ${error instanceof Error ? error.message : 'An error occurred while communicating with the AI service.'}`
        );
      }
    } finally {
      // Reset state
      this.isProcessingMessage = false;
      this.uiHelper.updateSendButton(this.sendButton, false);
      AppStateService.getPlanStateDisplay().setLoading(false);
      this.uiHelper.updateAgentModeElement(this.modeSelector, false);
    }
  }

  /**
   * Handle tab completion for mentions
   */
  private handleTabCompletion(): void {
    // Use the dropdown's own selection mechanism which handles highlighted items
    this.mentionDropdown.selectHighlightedItem();
  }

  /**
   * Handle enter key when mention dropdown is visible
   */
  private handleEnterWithMention(): void {
    // Use the dropdown's own selection mechanism which handles highlighted items
    this.mentionDropdown.selectHighlightedItem();
  }

  /**
   * Complete a mention with the given name
   */
  private completeMentionWithName(name: string): void {
    const currentInput = this.getInputValue();
    const cursorPos = this.getSelectionStart();

    // Find the @ symbol before the cursor
    let mentionStart = -1;
    for (let i = cursorPos - 1; i >= 0; i--) {
      if (currentInput[i] === '@') {
        mentionStart = i;
        break;
      }
      if (currentInput[i] === ' ' || currentInput[i] === '\n') {
        break;
      }
    }

    if (mentionStart === -1) return;

    // Replace the partial mention with the complete one - replace spaces with underscores
    const beforeMention = currentInput.substring(0, mentionStart);
    const afterCursor = currentInput.substring(cursorPos);
    const displayName = name.replace(/\s+/g, '_');
    const replacement = `@${displayName} `;

    this.setInputValue(beforeMention + replacement + afterCursor);

    // Set cursor after the completed mention
    const newCursorPos = mentionStart + replacement.length;
    this.setSelectionRange(newCursorPos, newCursorPos);

    // The mention dropdown should already handle adding to context
  }

  /**
   * Check if there's a complete mention at the cursor position
   */
  private hasCompleteMentionAtCursor(): boolean {
    const currentInput = this.getInputValue();
    const cursorPos = this.getSelectionStart();

    // Look for @mention pattern before cursor
    const beforeCursor = currentInput.substring(0, cursorPos);
    const mentionMatch = beforeCursor.match(/@(\w+)\s*$/);

    return mentionMatch !== null;
  }

  /**
   * Process a complete mention (add to context without sending message)
   */
  private processCompleteMention(): void {
    const currentInput = this.getInputValue();
    const cursorPos = this.getSelectionStart();

    // Look for @mention pattern before cursor
    const beforeCursor = currentInput.substring(0, cursorPos);
    const mentionMatch = beforeCursor.match(/@(\w+)\s*$/);

    if (mentionMatch) {
      const mentionName = mentionMatch[1];

      // Try to find this mention in the available contexts
      // This is a simplified approach - in a real implementation you'd want to
      // search through all context categories for a matching name
      console.log(`Processing complete mention: ${mentionName}`);

      // Focus back to input for continued typing
      this.focus();
    }
  }
}
