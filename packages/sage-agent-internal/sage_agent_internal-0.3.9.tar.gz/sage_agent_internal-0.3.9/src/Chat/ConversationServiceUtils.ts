import { ChatMessages } from './ChatMessages';
import { ToolService } from '../Services/ToolService';
import { IChatService } from '../Services/IChatService';
import { ChatRequestStatus, DiffApprovalStatus } from '../types';
import { NotebookStateService } from '../Notebook/NotebookStateService';
import { CodeConfirmationDialog } from '../Components/CodeConfirmationDialog';
import { NotebookDiffManager } from '../Notebook/NotebookDiffManager';
import { SettingsWidget } from '../Components/Settings/SettingsWidget';
import { AppStateService } from '../AppState';
import { ActionHistory, ActionType } from './ActionHistory';
import { LoadingIndicatorManager } from './ConversationService';
import { DiffStateService } from '../Services/DiffStateService';
import { parse } from 'partial-json';
import { checkTokenLimit } from '../utils/tokenUtils';

export interface ConversationContext {
  chatService: IChatService;
  toolService: ToolService;
  messageComponent: ChatMessages;
  notebookStateService: NotebookStateService;
  codeConfirmationDialog: CodeConfirmationDialog;
  loadingManager: LoadingIndicatorManager;
  diffManager: NotebookDiffManager | null;
  actionHistory: ActionHistory;
  autoRun: boolean;
  notebookId: string | null;
  templates: Array<{ name: string; content: string }>;
  isActiveToolExecution: boolean;
  chatHistory: HTMLDivElement;
}

export interface StreamingState {
  currentStreamingMessage: HTMLDivElement | null;
  currentStreamingToolCall: HTMLDivElement | null;
  streamingToolCall?: {
    id: string;
    name: string;
    accumulatedInput: string;
    cellId?: string;
    originalContent?: string;
    originalSummary?: string;
    position?: number;
    summary?: string;
    toolResult?: {
      type: 'tool_result';
      tool_use_id: string;
      content: string;
    };
  };
  // Queue system for handling streaming operations
  operationQueue?: {
    pendingOperation?: NodeJS.Timeout;
    lastProcessedInput?: string;
  };
}

export class ConversationServiceUtils {
  /**
   * Step 1: Initialize conversation processing
   */
  static async initializeConversation(
    context: ConversationContext,
    newMessages: any[],
    systemPromptMessages: string[] = [],
    mode: 'agent' | 'ask' | 'fast' = 'agent'
  ): Promise<{ preparedMessages: any[]; tools: any[] }> {
    console.log(
      `[ConversationService] Processing conversation for notebook: ${context.notebookId || 'unknown'}`
    );

    // Add loading indicator at the start
    context.loadingManager.updateLoadingIndicator();

    // Refresh notebook tool IDs
    context.toolService.notebookTools?.refresh_ids();

    // Handle template contexts
    let preparedMessages = newMessages;
    if (context.templates && context.templates.length > 0) {
      const templateMessages = context.templates.map(template => ({
        role: 'user',
        content: `I'm providing the template "${template.name}" as additional context for our conversation:\n\n${template.content}`
      }));

      preparedMessages = [...templateMessages, ...newMessages];
      context.templates.length = 0; // Clear templates after use
    }

    // Get appropriate tools based on mode
    const tools =
      mode === 'ask'
        ? context.toolService.getAskModeTools()
        : context.toolService.getTools();

    return { preparedMessages, tools };
  }

  /**
   * Step 2: Send message to AI service with streaming handlers
   */
  static async sendMessageWithStreaming(
    context: ConversationContext,
    preparedMessages: any[],
    tools: any[],
    mode: 'agent' | 'ask' | 'fast',
    systemPromptMessages: string[],
    streamingState: StreamingState,
    createErrorMessage: (message: any) => Promise<void>
  ): Promise<any> {
    // Check token count before sending the message
    const conversationHistory =
      AppStateService.getState().chatContainer?.chatWidget.messageComponent.getMessageHistory() ||
      [];
    const tokenLimitCheck = checkTokenLimit([
      ...conversationHistory,
      ...preparedMessages
    ]);

    if (tokenLimitCheck.exceeded) {
      const warningMessage = `💡 **Conversation Length Notice**: This chat has grown quite long (approximately ${tokenLimitCheck.estimatedTokens.toLocaleString()} tokens, ${tokenLimitCheck.percentageUsed}% of the recommended limit). For optimal performance and cost efficiency, consider starting a new chat for your next topic. You can continue with this conversation if needed.`;

      context.messageComponent.addSystemMessage(warningMessage);
    }

    return await context.chatService.sendMessage(
      preparedMessages,
      tools,
      mode,
      systemPromptMessages,
      async (error, attempt) => {
        // Don't set up retry if we've been cancelled
        if (
          context.chatService.getRequestStatus() === ChatRequestStatus.CANCELLED
        ) {
          return;
        }

        // Progressive backoff delays: 5s, 15s, 30s
        const retryDelays = [5, 15, 30];
        const delaySeconds = retryDelays[attempt - 1] || 30;

        // Show user-friendly retry message instead of scary error
        context.messageComponent.addSystemMessage(
          `Sage encountered an error, retrying in ${delaySeconds} seconds...`
        );

        context.loadingManager.updateLoadingIndicator(
          `Waiting to retry in ${delaySeconds}s...`
        );

        // Only show the actual error in the chat if this is the final attempt
        if (attempt >= 3) {
          // This will be the final attempt, so if it fails, we should show the error
          // But we don't know yet if it will fail, so we'll handle this in the service
        }
      },
      // Notebook state fetching function
      () => context.notebookStateService.fetchNotebookState(),
      // Text streaming handler
      (text: string) => {
        if (
          context.chatService.getRequestStatus() === ChatRequestStatus.CANCELLED
        ) {
          return;
        }

        context.loadingManager.removeLoadingIndicator();

        if (!streamingState.currentStreamingMessage) {
          streamingState.currentStreamingMessage =
            context.messageComponent.addStreamingAIMessage();
        }

        context.messageComponent.updateStreamingMessage(
          streamingState.currentStreamingMessage,
          text
        );
      },
      // Tool use streaming handler
      (toolUse: any) => {
        console.log('[ConversationService] Tool use detected:', toolUse);

        if (
          context.chatService.getRequestStatus() === ChatRequestStatus.CANCELLED
        ) {
          return;
        }

        context.loadingManager.removeLoadingIndicator();

        if (!streamingState.currentStreamingToolCall) {
          streamingState.currentStreamingToolCall =
            context.messageComponent.addStreamingToolCall();
        }

        ConversationServiceUtils.handleToolUseStreaming(
          context,
          toolUse,
          streamingState
        );
      },
      context.toolService.getContextManager(),
      context.notebookId as string,
      createErrorMessage
    );
  }

  /**
   * Step 3: Handle tool use streaming events
   */
  static handleToolUseStreaming(
    context: ConversationContext,
    toolUse: any,
    streamingState: StreamingState
  ): void {
    if (toolUse.type === 'tool_use_delta') {
      ConversationServiceUtils.handleToolUseDeltaWithQueue(
        context,
        toolUse,
        streamingState
      );
    } else if (toolUse.type === 'tool_use') {
      ConversationServiceUtils.handleToolUseStart(
        context,
        toolUse,
        streamingState
      );
    } else if (toolUse.type === 'tool_use_stop') {
      // Process the entire queue immediately when tool use stops
      if (streamingState.operationQueue?.pendingOperation) {
        clearTimeout(streamingState.operationQueue.pendingOperation);
        streamingState.operationQueue.pendingOperation = undefined;
      }

      // Process any remaining operations in the queue immediately
      ConversationServiceUtils.processRemainingQueue(
        context,
        streamingState,
        toolUse
      );

      ConversationServiceUtils.handleToolUseStop(
        context,
        toolUse,
        streamingState
      );
    }
  }

  /**
   * Step 3a-queue: Handle tool use delta with queue system to prevent rapid operations
   */
  static handleToolUseDeltaWithQueue(
    context: ConversationContext,
    toolUse: any,
    streamingState: StreamingState
  ): void {
    if (!streamingState.streamingToolCall) return;

    streamingState.streamingToolCall.accumulatedInput += toolUse.input_delta;

    // Initialize queue if not exists
    if (!streamingState.operationQueue) {
      streamingState.operationQueue = {};
    }

    // Extract code from partial JSON
    const codeRegex =
      /"(?:source|new_source|updated_plan_string)"\s*:\s*"((?:[^"\\]|\\.)*)/;
    const match =
      streamingState.streamingToolCall.accumulatedInput.match(codeRegex);

    const partialToolUse = {
      type: 'tool_use',
      id: toolUse.id,
      name: streamingState.streamingToolCall.name,
      input: {
        is_streaming: true,
        updated_plan_string: undefined,
        new_source: undefined,
        source: undefined,
        cell_id: undefined
      }
    };

    if (match && match[1]) {
      const code = JSON.parse(`"${match[1]}"`);

      // Clear any pending operations
      if (streamingState.operationQueue.pendingOperation) {
        clearTimeout(streamingState.operationQueue.pendingOperation);
      }

      // Check if this is a significantly different input to avoid unnecessary operations
      const currentInput = streamingState.streamingToolCall.accumulatedInput;
      if (streamingState.operationQueue.lastProcessedInput === currentInput) {
        return; // Skip if input hasn't changed
      }

      // Queue the operation with a short debounce delay (100ms)
      streamingState.operationQueue.pendingOperation = setTimeout(() => {
        try {
          ConversationServiceUtils.handleRealTimeNotebookUpdates(
            context,
            streamingState.streamingToolCall!,
            code,
            partialToolUse,
            toolUse
          );

          context.messageComponent.updateStreamingToolCall(
            streamingState.currentStreamingToolCall!,
            partialToolUse
          );

          // Mark this input as processed
          streamingState.operationQueue!.lastProcessedInput = currentInput;
        } catch (error) {
          console.error('Error in queued notebook operation:', error);
        }

        // Clear the pending operation
        streamingState.operationQueue!.pendingOperation = undefined;
      }, 100); // 100ms debounce
    }
  }

  /**
   * Step 3a-queue-flush: Process remaining queue items immediately
   */
  static processRemainingQueue(
    context: ConversationContext,
    streamingState: StreamingState,
    toolUse: any
  ): void {
    if (!streamingState.streamingToolCall || !streamingState.operationQueue) {
      return;
    }

    // Extract code from the current accumulated input
    const codeRegex =
      /"(?:source|new_source|updated_plan_string)"\s*:\s*"((?:[^"\\]|\\.)*)/;
    const match =
      streamingState.streamingToolCall.accumulatedInput.match(codeRegex);

    if (match && match[1]) {
      const code = JSON.parse(`"${match[1]}"`);
      const currentInput = streamingState.streamingToolCall.accumulatedInput;

      // Only process if this input hasn't been processed yet
      if (streamingState.operationQueue.lastProcessedInput !== currentInput) {
        const partialToolUse = {
          type: 'tool_use',
          id: toolUse.id,
          name: streamingState.streamingToolCall.name,
          input: {
            is_streaming: false, // Mark as final processing
            updated_plan_string: undefined,
            new_source: undefined,
            source: undefined,
            cell_id: undefined
          }
        };

        try {
          ConversationServiceUtils.handleRealTimeNotebookUpdates(
            context,
            streamingState.streamingToolCall,
            code,
            partialToolUse,
            toolUse
          );

          context.messageComponent.updateStreamingToolCall(
            streamingState.currentStreamingToolCall!,
            partialToolUse
          );

          // Mark this input as processed
          streamingState.operationQueue.lastProcessedInput = currentInput;
        } catch (error) {
          console.error('Error in final queue processing:', error);
        }
      }
    }

    // Clear the queue
    streamingState.operationQueue = {};
  }

  /**
   * Step 3b: Handle tool use start
   */
  static handleToolUseStart(
    context: ConversationContext,
    toolUse: any,
    streamingState: StreamingState
  ): void {
    streamingState.streamingToolCall = {
      id: toolUse.id,
      name: toolUse.name,
      accumulatedInput: ''
    };

    // Show tool state in LLMStateDisplay for streaming tool calls
    const llmStateDisplay =
      AppStateService.getChatContainerSafe()?.chatWidget.llmStateDisplay;
    if (llmStateDisplay && !llmStateDisplay.isDiffState()) {
      llmStateDisplay.showTool(toolUse.name);
    }

    context.messageComponent.updateStreamingToolCall(
      streamingState.currentStreamingToolCall!,
      toolUse
    );
  }

  /**
   * Step 3c: Handle tool use stop
   */
  static handleToolUseStop(
    context: ConversationContext,
    toolUse: any,
    streamingState: StreamingState
  ): void {
    context.messageComponent.updateStreamingToolCall(
      streamingState.currentStreamingToolCall!,
      toolUse
    );

    if (toolUse.name === 'notebook-edit_cell') {
      context.toolService.notebookTools?.edit_cell({
        cell_id: toolUse.input.cell_id,
        new_source: toolUse.input.new_source || '',
        summary: toolUse.input.summary || '',
        is_tracking_id: true,
        notebook_path: context.notebookId
      });

      context.diffManager?.trackEditCell(
        toolUse.input.cell_id,
        streamingState.streamingToolCall!.originalContent || '',
        toolUse.input.new_source,
        toolUse.input.summary,
        context.notebookId
      );
    }

    if (toolUse.name === 'notebook-add_cell') {
      context.toolService.notebookTools?.edit_cell({
        cell_id: streamingState.streamingToolCall!.cellId!,
        new_source: toolUse.input.source || '',
        summary: toolUse.input.summary || '',
        is_tracking_id: true,
        notebook_path: context.notebookId
      });

      context.diffManager?.trackAddCell(
        streamingState.streamingToolCall!.cellId!,
        toolUse.input.source,
        toolUse.input.summary,
        context.notebookId
      );
    }

    if (toolUse.name === 'notebook-edit_plan') {
      // edit_plan is handled by ToolService, no need to call it here
      console.log('edit_plan tool completed via ToolService');
    }
  }

  /**
   * Step 3d: Handle real-time notebook updates during streaming
   */
  static handleRealTimeNotebookUpdates(
    context: ConversationContext,
    streamingToolCall: NonNullable<StreamingState['streamingToolCall']>,
    code: string,
    partialToolUse: any,
    toolUse: any
  ): void {
    const isAddCell = streamingToolCall.name === 'notebook-add_cell';
    const isEditCell = streamingToolCall.name === 'notebook-edit_cell';
    const isEditPlan = streamingToolCall.name === 'notebook-edit_plan';

    if (isEditPlan) {
      context.toolService.notebookTools?.stream_edit_plan({
        partial_plan: code,
        notebook_path: context.notebookId
      });
      partialToolUse.input.updated_plan_string = code;
    }

    if (isAddCell) {
      ConversationServiceUtils.handleAddCellStreaming(
        context,
        streamingToolCall,
        code,
        partialToolUse,
        toolUse
      );
    }

    if (isEditCell) {
      ConversationServiceUtils.handleEditCellStreaming(
        context,
        streamingToolCall,
        code,
        partialToolUse,
        toolUse
      );
    }
  }

  /**
   * Step 3e: Handle add cell streaming
   */
  static handleAddCellStreaming(
    context: ConversationContext,
    streamingToolCall: NonNullable<StreamingState['streamingToolCall']>,
    code: string,
    partialToolUse: any,
    toolUse: any
  ): void {
    console.log('BEGIN HANDLE ADD CELL');
    console.log(streamingToolCall);

    try {
      const partialJson = parse(streamingToolCall.accumulatedInput);
      // Ensure that position
      if (partialJson.position)
        streamingToolCall.position = partialJson.position;
    } catch (error) {
      console.error('Invalid JSON in accumulated input:', error);
      throw new Error('Failed to parse accumulated input JSON');
    }

    const cellTypeRegex = /"cell_type"\s*:\s*"([^"]*)"/;
    const cellTypeMatch =
      streamingToolCall.accumulatedInput.match(cellTypeRegex);
    const cellType = cellTypeMatch ? cellTypeMatch[1] : null;

    const cellSummaryRegex = /"summary"\s*:\s*"([^"]*)"/;
    const cellSummaryMatch =
      streamingToolCall.accumulatedInput.match(cellSummaryRegex);
    const cellSummary = cellSummaryMatch
      ? cellSummaryMatch[1]
      : 'Cell being created by AI...';

    const validCellTypes = ['code', 'markdown'];
    if (cellType && validCellTypes.includes(cellType)) {
      if (!streamingToolCall.cellId) {
        // First delta: create the cell
        try {
          const newCellId = context.toolService.notebookTools?.add_cell({
            cell_type: cellType,
            summary: cellSummary,
            source: code,
            notebook_path: context.notebookId,
            position: streamingToolCall.position
          });

          if (!newCellId) {
            throw new Error('Failed to create new cell, no ID returned');
          }

          partialToolUse.input.source = code;
          partialToolUse.input.cell_id = streamingToolCall.cellId as any;

          streamingToolCall.cellId = newCellId;
          streamingToolCall.toolResult = {
            type: 'tool_result',
            tool_use_id: toolUse.id,
            content: newCellId || ''
          };

          console.log(`New cell created with ID: ${newCellId}`);
        } catch (error) {
          console.error('Error creating new cell during streaming:', error);
          throw new Error('Failed to create new cell');
        }
      } else {
        // Subsequent deltas: edit the cell
        try {
          context.toolService.notebookTools?.edit_cell({
            cell_id: streamingToolCall.cellId,
            summary: cellSummary,
            new_source: code,
            is_tracking_id: true,
            notebook_path: context.notebookId
          });
        } catch (error) {
          console.error('Error editing existing cell during streaming:', error);
          throw new Error('Failed to edit existing cell');
        }
      }
    }
  }

  /**
   * Step 3f: Handle edit cell streaming
   */
  static handleEditCellStreaming(
    context: ConversationContext,
    streamingToolCall: NonNullable<StreamingState['streamingToolCall']>,
    code: string,
    partialToolUse: any,
    toolUse: any
  ): void {
    console.log(streamingToolCall);
    if (!streamingToolCall.cellId) {
      const cellIdRegex = /"cell_id"\s*:\s*"([^"]*)"/;
      const cellIdMatch = streamingToolCall.accumulatedInput.match(cellIdRegex);
      if (cellIdMatch && cellIdMatch[1]) {
        streamingToolCall.cellId = cellIdMatch[1];

        // Get the original content for diff tracking
        if (context.diffManager && !streamingToolCall.originalContent) {
          try {
            const cellInfo = context.toolService.notebookTools?.findCellByAnyId(
              streamingToolCall.cellId,
              context.notebookId
            );
            if (cellInfo) {
              streamingToolCall.originalContent =
                cellInfo.cell.model.sharedModel.getSource() || '';
              streamingToolCall.originalSummary =
                (cellInfo.cell.model.sharedModel.metadata?.custom as any)
                  ?.summary || '';
            }
          } catch (error) {
            console.warn('Could not get original content for diff:', error);
          }
        }
      }
    }

    if (streamingToolCall.cellId) {
      // Handle diff calculation for partial streaming
      let finalContent = code;
      if (streamingToolCall.originalContent) {
        if (code.length < streamingToolCall.originalContent.length) {
          finalContent =
            code + streamingToolCall.originalContent.substring(code.length);
        } else {
          finalContent = code;
        }
      }

      const result = context.toolService.notebookTools?.edit_cell({
        cell_id: streamingToolCall.cellId,
        new_source: finalContent,
        summary: streamingToolCall.summary || 'Cell being updated by AI...',
        is_tracking_id: streamingToolCall.cellId.startsWith('cell_'),
        notebook_path: context.notebookId
      });

      streamingToolCall.toolResult = {
        type: 'tool_result',
        tool_use_id: toolUse.id,
        content: result ? 'true' : 'false'
      };

      partialToolUse.input.new_source = code;
      partialToolUse.input.cell_id = streamingToolCall.cellId as any;
    }
  }

  /**
   * Step 4: Handle response and finalize streaming elements
   */
  static async finalizeStreamingElements(
    context: ConversationContext,
    response: any,
    streamingState: StreamingState
  ): Promise<void> {
    // Check for cancellation
    if (response?.cancelled || context.chatService.isRequestCancelled()) {
      console.log('Response processing skipped due to cancellation');
      ConversationServiceUtils.cleanupStreamingElements(
        context,
        streamingState
      );
      context.loadingManager.removeLoadingIndicator();
      return;
    }

    // Check for cell rejection signal
    if (response.needsFreshContext === true) {
      context.loadingManager.removeLoadingIndicator();
      return; // Let the caller handle rejection
    }

    // Finalize streaming message
    if (streamingState.currentStreamingMessage) {
      await context.messageComponent.finalizeStreamingMessage(
        streamingState.currentStreamingMessage
      );
    }

    const llmStateDisplay =
      AppStateService.getChatContainerSafe()?.chatWidget.llmStateDisplay;

    // Finalize streaming tool call
    if (streamingState.currentStreamingToolCall) {
      context.messageComponent.finalizeStreamingToolCall(
        streamingState.currentStreamingToolCall
      );

      if (llmStateDisplay && !llmStateDisplay.isDiffState()) {
        llmStateDisplay.show('Generating...');
        llmStateDisplay.hide();
      }
    } else {
      llmStateDisplay?.hide();
    }

    // Also hide DiffNavigationWidget when finalizing tool calls (unless in diff state)
    if (!llmStateDisplay?.isDiffState()) {
      const diffNavigationWidget =
        AppStateService.getDiffNavigationWidgetSafe();
      if (diffNavigationWidget) {
        diffNavigationWidget.hidePendingDiffs();
      }
    }
  }

  /**
   * Step 5: Add usage information if in token mode
   */
  static addUsageInformation(
    context: ConversationContext,
    response: any
  ): void {
    if (!SettingsWidget.SAGE_TOKEN_MODE) return;

    console.log('Sage Token Mode is enabled, adding usage message');
    console.log('Response usage:', response);

    let numUserMessages = 0;
    let numAIResponses = 0;
    let numToolCalls = 0;
    let numToolResults = 0;

    for (const message of context.messageComponent.getMessageHistory()) {
      if (typeof message.content === 'string') {
        if (message.role === 'assistant') numAIResponses += 1;
        else numUserMessages += 1;
      } else {
        if (message.role === 'assistant') numToolCalls += 1;
        else numToolResults += 1;
      }
    }

    // Check if conversation length has exceeded recommended limits
    const totalTokens = response.usage.input_tokens || 0;
    const maxRecommendedTokens = 60000;
    const tokenLimitExceeded = totalTokens > maxRecommendedTokens;

    let usageMessage = `cache_input_tokens: ${response.usage.cache_creation_input_tokens}, cache_read_tokens: ${response.usage.cache_read_input_tokens} \n
       input_tokens: ${response.usage.input_tokens}, output_tokens: ${response.usage.output_tokens} \n
       user_messages: ${numUserMessages}, assistant_responses: ${numAIResponses} \n
       tool_calls: ${numToolCalls}, tool_results: ${numToolResults} \n`;

    // Add token limit warning if exceeded
    if (tokenLimitExceeded) {
      const percentageUsed = Math.round(
        (totalTokens / maxRecommendedTokens) * 100
      );
      usageMessage += `\n⚠️  **Chat Length Warning**: This conversation has reached ${totalTokens.toLocaleString()} tokens (${percentageUsed}% of recommended limit). For optimal performance and to avoid potential issues, it is recommended to start a new chat session.\n`;
    }

    context.messageComponent.addSystemMessage(usageMessage);
  }

  /**
   * Step 6: Process tool calls from the response
   */
  static async processToolCalls(
    context: ConversationContext,
    response: any,
    streamingState: StreamingState,
    systemPromptMessages: string[],
    mode: 'agent' | 'ask' | 'fast'
  ): Promise<{ hasToolCalls: boolean; shouldContinue: boolean }> {
    let hasToolCalls = false;

    if (!response.content || response.content.length === 0) {
      return { hasToolCalls, shouldContinue: true };
    }

    for (const content of response.content) {
      // Check for cancellation
      if (context.chatService.isRequestCancelled()) {
        console.log('Request was cancelled, stopping tool processing');
        context.loadingManager.removeLoadingIndicator();
        return { hasToolCalls, shouldContinue: false };
      }

      if (content.type === 'tool_use') {
        hasToolCalls = true;
        context.isActiveToolExecution = true;

        const shouldContinue =
          await ConversationServiceUtils.processSingleToolCall(
            context,
            content,
            streamingState,
            systemPromptMessages,
            mode
          );

        if (!shouldContinue) {
          return { hasToolCalls, shouldContinue: false };
        }

        // Reset streaming state for next iteration
        streamingState.streamingToolCall = undefined;
      }
    }

    return { hasToolCalls, shouldContinue: true };
  }

  /**
   * Step 6a: Process a single tool call
   */
  static async processSingleToolCall(
    context: ConversationContext,
    content: any,
    streamingState: StreamingState,
    systemPromptMessages: string[],
    mode: 'agent' | 'ask' | 'fast'
  ): Promise<boolean> {
    const toolName = content.name;
    const toolArgs = content.input;
    console.log(`AI wants to use tool: ${toolName}`);

    // Capture action state before execution for undo functionality
    const actionBeforeExecution =
      await ConversationServiceUtils.captureActionState(
        context,
        toolName,
        toolArgs,
        streamingState
      );

    // Handle special cases for code execution
    if (
      toolName === 'notebook-run_cell' ||
      toolName === 'notebook-execute_cell'
    ) {
      const shouldContinue = await ConversationServiceUtils.handleCodeExecution(
        context,
        content,
        mode
      );
      if (!shouldContinue) return false;
    }

    // Show tool state in LLM display
    const llmStateDisplay =
      AppStateService.getChatContainerSafe()?.chatWidget.llmStateDisplay;
    if (llmStateDisplay && !llmStateDisplay.isDiffState()) {
      llmStateDisplay.showTool(toolName);
    }

    // Execute the tool
    const isStreamToolCall =
      streamingState.streamingToolCall &&
      streamingState.streamingToolCall.toolResult;

    let toolResult = null;
    if (isStreamToolCall) {
      toolResult = streamingState.streamingToolCall!.toolResult;
    } else {
      const executedApprovedCells =
        await ConversationServiceUtils.checkExecutedCells(
          context,
          content.id,
          content.input?.cell_id,
          true
        );

      if (executedApprovedCells && toolName === 'notebook-run_cell') {
        console.log('Skipping tool call in chat');
        return true;
      }

      toolResult = await ConversationServiceUtils.processToolCall(context, {
        id: content.id,
        name: toolName,
        input: toolArgs
      });
    }

    context.isActiveToolExecution = false;

    // Update LLM state
    if (llmStateDisplay && !llmStateDisplay.isDiffState()) {
      llmStateDisplay.show('Generating...');
    }

    // Track action for undo
    ConversationServiceUtils.trackActionForUndo(
      context,
      toolName,
      toolArgs,
      toolResult,
      actionBeforeExecution
    );

    // Check for cancellation
    if (
      context.chatService.getRequestStatus() === ChatRequestStatus.CANCELLED
    ) {
      console.log('Request was cancelled, skipping tool result display');
      return false;
    }

    // Show tool result and continue conversation
    context.messageComponent.addToolResult(
      toolName,
      content.id,
      toolResult.content,
      content?.input
    );

    if (
      context.chatService.getRequestStatus() === ChatRequestStatus.CANCELLED
    ) {
      return false;
    }

    if (
      context.chatService.getRequestStatus() === ChatRequestStatus.CANCELLED
    ) {
      console.log('Request was cancelled, skipping further processing');
      return false;
    }

    // Continue conversation if not waiting for user reply
    if (toolName !== 'notebook-wait_user_reply') {
      llmStateDisplay?.hidePendingDiffs();
      llmStateDisplay?.show('Generating...');
      // Note: Recursive call should be handled by the caller
      return true;
    } else {
      llmStateDisplay?.show('Waiting for your reply...', true);
      return false;
    }
  }

  /**
   * Step 6b: Capture action state before execution for undo
   */
  static async captureActionState(
    context: ConversationContext,
    toolName: string,
    toolArgs: any,
    streamingState: StreamingState
  ): Promise<any> {
    if (toolName === 'notebook-edit_cell') {
      try {
        const cellInfo = await context.toolService.executeTool({
          id: 'get_cell_before_edit',
          name: 'notebook-get_cell_info',
          input: { cell_id: toolArgs.cell_id }
        });

        if (cellInfo && cellInfo.content) {
          const cellData = JSON.parse(cellInfo.content);
          return {
            originalCell: cellData,
            originalContent:
              streamingState.streamingToolCall?.originalContent || '',
            originalSummary:
              streamingState.streamingToolCall?.originalSummary || '',
            newSource: toolArgs.new_source,
            cellId: toolArgs.cell_id,
            cell_id: toolArgs.cell_id,
            summary: toolArgs.summary
          };
        }
      } catch (err) {
        console.error('Failed to get cell info before edit:', err);
      }
    } else if (toolName === 'notebook-remove_cells') {
      try {
        const cellsToRemove = toolArgs.cell_ids || [];
        const cellInfoPromises = cellsToRemove.map((cellId: string) =>
          context.toolService.executeTool({
            id: `get_cell_before_remove_${cellId}`,
            name: 'notebook-get_cell_info',
            input: { cell_id: cellId }
          })
        );

        const cellInfoResults = await Promise.all(cellInfoPromises);
        const removedCells = cellInfoResults
          .map(result =>
            result && result.content ? JSON.parse(result.content) : null
          )
          .filter(cell => cell !== null);

        if (removedCells.length > 0) {
          return { removedCells };
        }
      } catch (err) {
        console.error('Failed to get cell info before removal:', err);
      }
    }

    return null;
  }

  /**
   * Step 6c: Handle code execution with diff approval
   */
  static async handleCodeExecution(
    context: ConversationContext,
    content: any,
    mode: 'agent' | 'ask' | 'fast'
  ): Promise<boolean> {
    context.loadingManager.removeLoadingIndicator();

    await ConversationServiceUtils.checkPendingDiffsBeforeCodeExecution(
      context
    );

    if (context.diffManager?.hasRejectedDiffs()) {
      context.messageComponent.addSystemMessage(
        '❌ Changes were rejected. Code execution has been cancelled.'
      );

      if (content.input?.cell_id) {
        context.messageComponent.addToolResult(
          'notebook-run_cell',
          content.id,
          'User rejected changes, cell was not added or executed.',
          {
            cell_id: content.input?.cell_id,
            notebook_path: context.notebookId
          }
        );
      }

      DiffStateService.getInstance().clearAllDiffs();

      return false;
    }

    // Check if user has made approval decisions that should stop the LLM loop
    const hasApprovalDecisions =
      ConversationServiceUtils.checkForApprovalDecisions(
        context,
        content.input?.cell_id
      );

    if (hasApprovalDecisions) {
      console.log(
        '[ConversationService] User made approval decisions - stopping LLM loop'
      );

      const cellId = content.input?.cell_id;
      console.log(
        `REQUESTED CELL ${cellId} WAS NOT EXECUTED DURING DIFF APPROVAL`
      );

      // Add a tool result that indicates user accepted changes but did not run the cell
      const toolResult = {
        type: 'tool_result' as const,
        tool_use_id: content.id,
        content: 'user accepted changes but did not run the cell.'
      };

      context.messageComponent.addToolResult(
        'notebook-run_cell',
        content.id,
        toolResult.content,
        { cell_id: cellId, notebook_path: context.notebookId }
      );

      return false; // Stop the tool execution entirely and stop LLM loop
    }

    // Execute approved cells if needed
    const executedApprovedCells =
      await ConversationServiceUtils.checkExecutedCells(
        context,
        content.id,
        content.input?.cell_id
      );

    console.log(
      '[ConversationService] Executed approved cells:',
      executedApprovedCells
    );

    if (executedApprovedCells) {
      return true; // Skip the original run_cell call
    }

    // Update cell ID if changed due to diff application
    if (context.diffManager && content.input.cell_id) {
      const updatedCellId = context.diffManager.getCurrentCellId(
        content.input.cell_id
      );
      if (updatedCellId !== content.input.cell_id) {
        console.log(
          `Updating cell ID for execution: ${content.input.cell_id} → ${updatedCellId}`
        );
        content.input.cell_id = updatedCellId;
      }
    }

    // Handle code execution confirmation
    let shouldRun = false;

    if (context.autoRun) {
      shouldRun = true;
      context.messageComponent.addSystemMessage(
        'Automatically running code (auto-run is enabled).'
      );
    } else if (
      context.diffManager &&
      context.diffManager.shouldRunImmediately()
    ) {
      shouldRun = true;
      context.messageComponent.addSystemMessage(
        'Running code immediately after approving changes.'
      );
    } else {
      // Show confirmation dialog
      const llmStateDisplay =
        AppStateService.getChatContainerSafe()?.chatWidget.llmStateDisplay;
      if (llmStateDisplay) {
        llmStateDisplay.showRunCellTool(
          () => context.codeConfirmationDialog.triggerApproval(),
          () => context.codeConfirmationDialog.triggerRejection()
        );
      }

      shouldRun = await context.codeConfirmationDialog.showConfirmation(
        content.input.cell_id || content.input.cellId || ''
      );

      if (shouldRun) {
        llmStateDisplay?.show();
      } else {
        llmStateDisplay?.hide();
        context.messageComponent.removeLoadingText();
      }
    }

    if (!shouldRun) {
      return false; // Rejection will be handled by caller
    }

    context.loadingManager.updateLoadingIndicator();
    return true;
  }

  /**
   * Step 6d: Process a tool call
   */
  static async processToolCall(
    context: ConversationContext,
    toolCall: any
  ): Promise<any> {
    const toolCallWithContext = {
      ...toolCall,
      input: {
        ...toolCall.input,
        notebook_path: context.notebookId
      }
    };

    return await context.toolService.executeTool(toolCallWithContext, 3, true);
  }

  /**
   * Step 6e: Track action for undo functionality
   */
  static trackActionForUndo(
    context: ConversationContext,
    toolName: string,
    toolArgs: any,
    toolResult: any,
    actionBeforeExecution: any
  ): void {
    if (toolName === 'notebook-add_cell' && toolResult && toolResult.content) {
      try {
        const cellId = toolResult.content.replace(/"/g, '').trim();
        context.actionHistory.addAction(
          ActionType.ADD_CELL,
          { cellId, ...toolArgs },
          `Added ${toolArgs.cell_type} cell`
        );
      } catch (err) {
        console.error('Failed to track add_cell action:', err);
      }
    } else if (toolName === 'notebook-edit_cell' && actionBeforeExecution) {
      context.actionHistory.addAction(
        ActionType.EDIT_CELL,
        actionBeforeExecution,
        `Edited cell ${toolArgs.cell_id.substring(0, 8)}...`
      );
    } else if (toolName === 'notebook-remove_cells' && actionBeforeExecution) {
      context.actionHistory.addAction(
        ActionType.REMOVE_CELLS,
        actionBeforeExecution,
        `Removed ${toolArgs.cell_ids.length} cell(s)`
      );

      // Track remove diffs if we have a diff manager
      if (context.diffManager && actionBeforeExecution.removedCells) {
        for (const cell of actionBeforeExecution.removedCells) {
          if (cell && (cell.id || cell.trackingId)) {
            context.diffManager.trackRemoveCell(
              cell.trackingId || cell.id,
              cell.content || '',
              cell.custom?.summary || 'Removed by AI',
              context.notebookId
            );
          }
        }
      }
    }
  }

  /**
   * Step 7: Handle pending diffs if no tool calls were made
   */
  static async handlePendingDiffsAfterToolCalls(
    context: ConversationContext
  ): Promise<boolean> {
    if (context.diffManager && context.diffManager.hasPendingDiffs()) {
      context.isActiveToolExecution = true;

      const llmStateDisplay =
        AppStateService.getChatContainerSafe()?.chatWidget.llmStateDisplay;
      if (llmStateDisplay) {
        llmStateDisplay.showPendingDiffs(context.notebookId);
      }

      // Also show diffs in DiffNavigationWidget for synchronized display
      const diffNavigationWidget =
        AppStateService.getDiffNavigationWidgetSafe();
      if (diffNavigationWidget) {
        diffNavigationWidget.showPendingDiffs(context.notebookId);
      }

      await ConversationServiceUtils.checkPendingDiffs(context);
      context.isActiveToolExecution = false;
    }

    return true;
  }

  /**
   * Step 8: Check for pending diffs and prompt for approval
   */
  static async checkPendingDiffs(
    context: ConversationContext
  ): Promise<boolean> {
    if (!context.diffManager || !context.diffManager.hasPendingDiffs()) {
      return true;
    }

    if (context.autoRun) {
      context.messageComponent.addSystemMessage(
        `Auto-approving ${context.diffManager.getPendingDiffCount()} changes (auto-run is enabled).`
      );

      for (const diff of DiffStateService.getInstance()
        .getCurrentState()
        .pendingDiffs.values()) {
        // Automatically approve all diffs in auto-run mode
        console.log('RUNNING DIFF IN AUTO APPROVE MODE:', diff.cellId);
        try {
          await AppStateService.getState().notebookDiffManager?.diffApprovalDialog.runCell(
            diff.cellId
          );
        } catch (error) {
          console.error(
            'Error running cell in auto-approve mode:',
            diff.cellId,
            error
          );
        }
      }

      return true;
    }

    // Start the diff approval process without waiting
    context.diffManager.startDiffApprovalProcess(
      context.chatHistory,
      true,
      false,
      AppStateService.getState().currentNotebookId || undefined
    );

    // Wait for the signal to indicate processing is complete
    const approvalStatus =
      await context.diffManager.waitForDiffProcessingComplete();

    return approvalStatus !== DiffApprovalStatus.REJECTED;
  }

  /**
   * Step 9: Check for pending diffs before code execution
   */
  /**
   * Step 9: Check for pending diffs before code execution
   */
  static async checkPendingDiffsBeforeCodeExecution(
    context: ConversationContext
  ): Promise<boolean> {
    if (!context.diffManager || !context.diffManager.hasPendingDiffs()) {
      return true;
    }

    if (context.autoRun) {
      context.messageComponent.addSystemMessage(
        `Auto-approving ${context.diffManager.getPendingDiffCount()} changes (auto-run is enabled).`
      );

      for (const diff of DiffStateService.getInstance()
        .getCurrentState()
        .pendingDiffs.values()) {
        // Automatically approve all diffs in auto-run mode
        console.log('RUNNING DIFF IN AUTO APPROVE MODE:', diff.cellId);
        try {
          await AppStateService.getState().notebookDiffManager?.diffApprovalDialog.runCell(
            diff.cellId
          );
        } catch (error) {
          console.error(
            'Error running cell in auto-approve mode:',
            diff.cellId,
            error
          );
        }
      }

      return true;
    }

    // context.messageComponent.addSystemMessage(
    //   `Before running code, ${context.diffManager.getPendingDiffCount()} pending changes to your notebook need approval.`
    // );

    // Start the diff approval process without waiting
    context.diffManager.startDiffApprovalProcess(
      context.chatHistory,
      true,
      true,
      AppStateService.getState().currentNotebookId || undefined
    );

    // Wait for the signal to indicate processing is complete
    const approvalStatus =
      await context.diffManager.waitForDiffProcessingComplete();

    return approvalStatus !== DiffApprovalStatus.REJECTED;
  }

  /**
   * Step 10: Check if cells were already executed during diff approval and return their results
   * This prevents re-execution of cells that were already run during the diff approval process.
   * Returns true if cells were already executed (skip original tool call), false otherwise.
   */
  static async checkExecutedCells(
    context: ConversationContext,
    contentId: string,
    requestedCellId?: string,
    log?: boolean
  ): Promise<boolean> {
    console.log('CHECKING EXECUTED CELLS!');

    if (!context.diffManager) return false;

    // Get all approved cells that have been executed during diff approval
    const approvedCellIds = context.diffManager.getApprovedCellIds(
      context.notebookId
    );
    if (approvedCellIds.length === 0) {
      return false;
    }

    const diffState = DiffStateService.getInstance().getCurrentState();
    console.log('Current diff state:', diffState.pendingDiffs);

    // Check if any cells were already executed with results
    const executedCells: { cellId: string; result: any }[] = [];
    let requestedCellWasExecuted = false;

    for (const cellId of approvedCellIds) {
      const diffRes = diffState.pendingDiffs.get(cellId);
      if (diffRes && diffRes.userDecision === 'run' && diffRes.runResult) {
        console.log('CELL WAS ALREADY EXECUTED:', cellId, diffRes.runResult);
        executedCells.push({ cellId, result: diffRes.runResult });

        // Check if this is the specific cell that was requested to be executed
        if (requestedCellId && cellId === requestedCellId) {
          requestedCellWasExecuted = true;
        }
      }
    }

    // If a specific cell was requested and it wasn't executed during diff approval,
    // allow normal execution
    if (requestedCellId && !requestedCellWasExecuted) {
      console.log(
        `REQUESTED CELL ${requestedCellId} WAS NOT EXECUTED DURING DIFF APPROVAL`
      );
      return false;
    }

    // If no cells were executed during diff approval, return false to allow normal execution
    if (executedCells.length === 0) {
      console.log('NO CELLS WERE EXECUTED DURING DIFF APPROVAL');

      const toolResult = {
        type: 'tool_result' as const,
        tool_use_id: contentId,
        content: 'User approved changes but did not run the cell at this time.'
      };

      context.messageComponent.addToolResult(
        'notebook-run_cell',
        contentId,
        toolResult.content,
        { cell_id: requestedCellId, notebook_path: context.notebookId }
      );

      return false;
    }

    // Cells were already executed - add their results to the conversation and return true to skip re-execution
    // If a specific cell was requested, only handle that cell's result
    const cellsToReport =
      requestedCellId && requestedCellWasExecuted
        ? executedCells.filter(cell => cell.cellId === requestedCellId)
        : executedCells;

    log &&
      context.messageComponent.addSystemMessage(
        requestedCellId && requestedCellWasExecuted
          ? `Cell ${requestedCellId} was executed during diff approval.`
          : `${cellsToReport.length} cells were executed during diff approval.`
      );

    // For each executed cell, add the tool result to the conversation
    for (const { cellId, result } of cellsToReport) {
      if (cellId !== requestedCellId) continue;

      let final_res = result;
      if (Array.isArray(result)) {
        for (const res of result as any[]) {
          if (typeof res === 'string') final_res += res;
          else final_res += JSON.stringify(res);
        }
      }

      // Format the result as a tool result
      const toolResult = {
        type: 'tool_result' as const,
        tool_use_id: contentId,
        content: final_res
      };

      // Add the tool result to the conversation
      context.messageComponent.addToolResult(
        'notebook-run_cell',
        contentId,
        toolResult.content,
        { cell_id: cellId, notebook_path: context.notebookId }
      );
    }

    console.log('SKIPPING ORIGINAL TOOL EXECUTION - CELLS ALREADY RAN');
    return true;
  }

  /**
   * Check if user has any approval decisions pending that require stopping the LLM loop
   * This detects when the user has approved changes but not executed the requested cell,
   * which should stop the recursive LLM conversation loop.
   */
  static checkForApprovalDecisions(
    context: ConversationContext,
    requestedCellId?: string
  ): boolean {
    if (!context.diffManager) return false;

    // Get the current diff state from DiffStateService
    const diffState = DiffStateService.getInstance().getCurrentState();

    // Check if there are any diffs with approval decisions (approved or run) for this notebook
    for (const [cellId, diff] of diffState.pendingDiffs) {
      if (cellId !== requestedCellId) continue;

      // If user has made approval decisions (approved or run)
      if (diff.userDecision === 'approved') {
        return true;
      }
    }

    return false;
  }

  /**
   * Utility: Clean up streaming elements on cancellation
   */
  static cleanupStreamingElements(
    context: ConversationContext,
    streamingState: StreamingState
  ): void {
    // Clear any pending queue operations
    if (streamingState.operationQueue?.pendingOperation) {
      clearTimeout(streamingState.operationQueue.pendingOperation);
      streamingState.operationQueue.pendingOperation = undefined;
    }

    if (streamingState.currentStreamingMessage) {
      context.messageComponent.removeElement(
        streamingState.currentStreamingMessage
      );
    }
    if (streamingState.currentStreamingToolCall) {
      context.messageComponent.removeElement(
        streamingState.currentStreamingToolCall
      );
    }
  }
}
