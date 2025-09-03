import Anthropic from '@anthropic-ai/sdk';
import { ChatRequestStatus } from '../types';
import { ConfigService } from '../Config/ConfigService';
import { IChatService } from './IChatService';
import { AnthropicStreamHandler } from './AnthropicStreamHandler';
import { AnthropicMessageCreator } from './AnthropicMessageCreator';
import { ServiceUtils } from './ServiceUtils';
import { AppStateService } from '../AppState';

/**
 * Service for handling Anthropic API interactions
 */
export class AnthropicService implements IChatService {
  private client: Anthropic | null = null;
  private modelName: string = 'claude-3-7-sonnet-20250219';
  private modelUrl: string = 'https://api.anthropic.com/v1/messages';
  private requestStatus: ChatRequestStatus = ChatRequestStatus.IDLE;
  private abortController: AbortController | null = null;
  private systemPrompt: string = '';
  private systemPromptAskMode: string = '';
  private systemPromptFastMode: string = '';
  // Store complete conversation history
  // Fast mode settings
  private isFastMode: boolean = false;
  private toolBlacklist: string[] = [];

  /**
   * Initialize the Anthropic client
   * @param apiKey API key for authentication (optional - will use config if not provided)
   * @returns boolean indicating if initialization was successful
   */
  async initialize(apiKey?: string): Promise<boolean> {
    try {
      // If already initialized, no-op
      if (this.client) {
        return true;
      }
      // Always try to get settings from AppState first to ensure we have the latest settings
      try {
        const config = await ConfigService.getConfig();
        console.log('Initializing Anthropic client with config:', config);
        apiKey = config.claude.api_key;
        this.systemPrompt = config.claude.system_prompt;
        this.systemPromptAskMode = config.claude_ask_mode.system_prompt;
        this.systemPromptFastMode = config.fast_mode.system_prompt;
        this.modelName = config.claude.model_name;
        this.modelUrl = config.claude.model_url;
        this.toolBlacklist = config.fast_mode.tool_blacklist || [];
      } catch (error) {
        console.log('AppState not available, falling back to config');
      }

      if (!apiKey || apiKey.trim() === '') {
        this.client = null;
        return false;
      }

      this.client = new Anthropic({
        apiKey,
        baseURL: this.modelUrl,
        dangerouslyAllowBrowser: true
      });

      return true;
    } catch (error) {
      console.error('Failed to initialize Anthropic client:', error);
      this.client = null;
      return false;
    }
  }

  get conversationHistory(): Array<any> {
    return (
      AppStateService.getState().chatContainer?.chatWidget.messageComponent
        .messageHistory || []
    );
  }

  /**
   * Get the tool blacklist for fast mode
   * @returns Array of tool names that are blacklisted in fast mode
   */
  getToolBlacklist(): string[] {
    return [...this.toolBlacklist];
  }

  /**
   * Load system prompt from configuration
   */
  async refreshSystemPrompt(): Promise<void> {
    try {
      const config = await ConfigService.getConfig();
      this.systemPrompt = config.claude.system_prompt;
      this.systemPromptAskMode = config.claude_ask_mode.system_prompt;
      this.systemPromptFastMode = config.fast_mode.system_prompt;
      this.toolBlacklist = config.fast_mode.tool_blacklist || [];
      console.log('System prompt loaded successfully from config');
    } catch (error) {
      console.error('Failed to load system prompt from config:', error);
      // Fallback to default prompt if loading fails
      this.systemPrompt =
        'You are a world-class data scientist and quantitative analyst, highly proficient in exploratory data analysis, statistical and ML modeling, hypothesis testing, feature engineering, and efficient use of Jupyter notebooks.';
      this.systemPromptAskMode =
        'You are a world-class data scientist and quantitative analyst, highly proficient in exploratory data analysis, statistical and ML modeling, hypothesis testing, feature engineering, and efficient use of Jupyter notebooks.';
      this.systemPromptFastMode =
        'You are a world-class data scientist and quantitative analyst, optimized for speed and efficiency.';
    }
  }

  /**
   * Check if the Anthropic client is initialized
   * @returns boolean indicating if the client is initialized
   */
  isInitialized(): boolean {
    return this.client !== null;
  }

  /**
   * Set the model name
   * @param modelName Name of the model to use
   */
  setModelName(modelName: string): void {
    this.modelName = modelName;
  }

  /**
   * Get the current model name
   */
  getModelName(): string {
    return this.modelName;
  }

  /**
   * Get the current request status
   */
  getRequestStatus(): ChatRequestStatus {
    return this.requestStatus;
  }

  /**
   * Check if the current request is cancelled
   */
  isRequestCancelled(): boolean {
    return this.requestStatus === ChatRequestStatus.CANCELLED;
  }

  /**
   * Cancel the current request if any
   */
  cancelRequest(): void {
    if (this.abortController) {
      this.abortController.abort();
      this.abortController = null;
      this.requestStatus = ChatRequestStatus.CANCELLED;
      console.log('Request cancelled by user');
    }
  }

  /**
   * Send a message to the Anthropic API
   * @param newMessages The new messages to add to the conversation
   * @param tools Available tools
   * @param mode The mode of the chat (agent or ask)
   * @param onRetry Callback for retry attempts
   * @param fetchNotebookState Function to fetch the current notebook state
   * @param onTextChunk Callback for streaming text chunks as they arrive
   * @param onToolUse Callback for streaming tool uses as they arrive
   * @param notebookContextManager Optional NotebookContextManager to get context cells
   * @param notebookId Optional notebook path for context cells
   * @param forceRetry Whether to force a retry even for 400 errors
   */
  async sendMessage(
    newMessages: any[],
    tools: any[] = [],
    mode: 'agent' | 'ask' = 'agent',
    systemPromptMessages?: string[],
    onRetry?: (error: Error, attemptNumber: number) => Promise<void>,
    fetchNotebookState?: () => Promise<string>,
    onTextChunk?: (text: string) => void,
    onToolUse?: (toolUse: any) => void,
    notebookContextManager?: any,
    notebookId?: string,
    errorLogger?: (message: any) => Promise<void>,
    forceRetry: boolean = false
  ): Promise<any> {
    await this.validateClientInitialized(errorLogger);
    this.initializeRequest();

    const filteredHistory = await this.getFilteredHistory(errorLogger);

    try {
      const result = await this.executeStreamRequest(
        filteredHistory,
        tools,
        mode,
        systemPromptMessages,
        fetchNotebookState,
        onTextChunk,
        onToolUse,
        notebookContextManager,
        notebookId,
        errorLogger
      );

      if (!this.isRequestCancelled()) {
        this.requestStatus = ChatRequestStatus.COMPLETED;
      }

      return result;
    } catch (error: any) {
      return await this.handleRequestError(
        error,
        onRetry,
        filteredHistory,
        tools,
        mode,
        systemPromptMessages,
        fetchNotebookState,
        onTextChunk,
        onToolUse,
        notebookContextManager,
        notebookId,
        errorLogger,
        forceRetry
      );
    }
  }

  /**
   * Send an ephemeral message directly to the API without persisting to conversation history
   * Used for fast, one-off tasks like cell editing and quick questions
   * @param message The message to send
   * @param systemPrompt The system prompt to use
   * @param modelName Optional model name override (defaults to haiku for speed)
   * @param onTextChunk Optional callback for streaming text chunks
   * @param options Optional configuration for the request
   * @param onRetry Optional callback for retry attempts
   * @returns Promise with the complete response content
   */
  async sendEphemeralMessage(
    message: string,
    systemPrompt: string,
    modelName: string = 'claude-3-5-haiku-latest',
    onTextChunk?: (text: string) => void,
    options?: {
      maxTokens?: number;
      temperature?: number;
      stopSequences?: string[];
    },
    onRetry?: (error: Error, attemptNumber: number) => Promise<void>
  ): Promise<string> {
    if (!this.client) {
      throw new Error(
        'Anthropic client not initialized. Please set API key first.'
      );
    }

    try {
      return await this.executeEphemeralRequest(
        message,
        systemPrompt,
        modelName,
        onTextChunk,
        options
      );
    } catch (error: any) {
      return await this.handleEphemeralRequestError(
        error,
        message,
        systemPrompt,
        modelName,
        onTextChunk,
        options,
        onRetry
      );
    }
  }

  /**
   * Execute the core ephemeral request without retry logic
   */
  private async executeEphemeralRequest(
    message: string,
    systemPrompt: string,
    modelName: string,
    onTextChunk?: (text: string) => void,
    options?: {
      maxTokens?: number;
      temperature?: number;
      stopSequences?: string[];
    }
  ): Promise<string> {
    const maxTokens = options?.maxTokens ?? 48;
    const temperature = options?.temperature ?? 0;

    if (onTextChunk) {
      // Use streaming for real-time updates
      const stream = await this.client!.messages.stream({
        model: modelName,
        max_tokens: maxTokens,
        system: systemPrompt,
        temperature,
        stop_sequences: options?.stopSequences,
        messages: [
          {
            role: 'user',
            content: message
          }
        ]
      });

      let completeResponse = '';

      for await (const chunk of stream) {
        if (
          chunk.type === 'content_block_delta' &&
          chunk.delta.type === 'text_delta'
        ) {
          const textChunk = chunk.delta.text;
          completeResponse += textChunk;
          onTextChunk(textChunk);
        }
      }

      return completeResponse;
    } else {
      // Use non-streaming for simple responses
      const response = await this.client!.messages.create({
        model: modelName,
        max_tokens: maxTokens,
        system: systemPrompt,
        temperature,
        stop_sequences: options?.stopSequences,
        messages: [
          {
            role: 'user',
            content: message
          }
        ]
      });

      // Extract text content from response
      let responseText = '';
      for (const content of response.content) {
        if (content.type === 'text') {
          responseText += content.text;
        }
      }

      return responseText;
    }
  }

  /**
   * Handle ephemeral request errors and retry with backoff strategy
   */
  private async handleEphemeralRequestError(
    error: any,
    message: string,
    systemPrompt: string,
    modelName: string,
    onTextChunk?: (text: string) => void,
    options?: {
      maxTokens?: number;
      temperature?: number;
      stopSequences?: string[];
    },
    onRetry?: (error: Error, attemptNumber: number) => Promise<void>
  ): Promise<string> {
    console.error('Ephemeral message error:', error);

    // Skip retry for 400 errors (Bad Request) - these are typically non-recoverable
    if (error.name === 'BadRequestError' && error.status === 400) {
      throw error;
    }

    // Progressive backoff delays: 5s, 15s, 30s (same as sendMessage)
    const retryDelays = [5000, 15000, 30000];
    const maxRetries = retryDelays.length;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        onRetry && (await onRetry(error, attempt));

        // Wait before retry
        await this.waitForRetry(retryDelays[attempt - 1]);

        // Retry the request
        return await this.executeEphemeralRequest(
          message,
          systemPrompt,
          modelName,
          onTextChunk,
          options
        );
      } catch (retryError: any) {
        // If this is the last attempt, throw the error
        if (attempt === maxRetries) {
          const friendlyErrorMessage =
            retryError instanceof Error
              ? retryError.message
              : 'Unknown error occurred';

          const finalError = new Error(
            `Failed to connect to AI service after 3 attempts. ${friendlyErrorMessage}`
          );

          throw finalError;
        }

        // Update error for next attempt
        error = retryError;
      }
    }

    // This should never be reached, but TypeScript needs it
    throw error;
  }

  /**
   * Validates that the client is initialized
   */
  private async validateClientInitialized(
    errorLogger?: (message: any) => Promise<void>
  ): Promise<void> {
    if (!this.client) {
      const errMsg = {
        message: 'Anthropic client not initialized. Please set API key first.',
        variables: {
          client: this.client,
          modelName: this.modelName,
          modelUrl: this.modelUrl,
          requestStatus: this.requestStatus
        }
      };
      errorLogger && (await errorLogger(JSON.stringify(errMsg)));
      throw new Error(errMsg.message);
    }
  }

  /**
   * Initializes the request
   */
  private initializeRequest(): void {
    this.requestStatus = ChatRequestStatus.PENDING;
    this.abortController = new AbortController();
  }

  /**
   * Gets filtered conversation history
   */
  private async getFilteredHistory(
    errorLogger?: (message: any) => Promise<void>
  ): Promise<any[]> {
    try {
      const filteredDiffs = ServiceUtils.filterDiffApprovalMessages(
        this.conversationHistory
      );
      const filteredTools = ServiceUtils.filterToolMessages(
        filteredDiffs,
        errorLogger
      );
      const parsedUserMessages = ServiceUtils.parseUserMessages(filteredTools);

      return parsedUserMessages;
    } catch (error) {
      const errMsg = {
        message: 'Error filtering tool messages',
        error: error instanceof Error ? error.message : error,
        conversationHistory: this.conversationHistory
      };
      errorLogger && (await errorLogger(JSON.stringify(errMsg)));
      throw error;
    }
  }

  /**
   * Executes the main stream request
   */
  private async executeStreamRequest(
    filteredHistory: any[],
    tools: any[],
    mode: 'agent' | 'ask',
    systemPromptMessages?: string[],
    fetchNotebookState?: () => Promise<string>,
    onTextChunk?: (text: string) => void,
    onToolUse?: (toolUse: any) => void,
    notebookContextManager?: any,
    notebookId?: string,
    errorLogger?: (message: any) => Promise<void>
  ): Promise<any> {
    const stream = await this.createMessageStream(
      filteredHistory,
      tools,
      mode,
      systemPromptMessages,
      fetchNotebookState,
      notebookContextManager,
      notebookId,
      errorLogger
    );

    return await AnthropicStreamHandler.processStream(
      stream,
      {
        onTextChunk,
        onToolUse,
        errorLogger,
        isRequestCancelled: () => this.isRequestCancelled()
      },
      this.conversationHistory
    );
  }

  /**
   * Creates a message stream using the message creator
   */
  private async createMessageStream(
    filteredHistory: any[],
    tools: any[],
    mode: 'agent' | 'ask',
    systemPromptMessages?: string[],
    fetchNotebookState?: () => Promise<string>,
    notebookContextManager?: any,
    notebookId?: string,
    errorLogger?: (message: any) => Promise<void>
  ): Promise<any> {
    try {
      return await AnthropicMessageCreator.createMessageStream(
        {
          client: this.client!,
          modelName: this.modelName,
          systemPrompt: this.systemPrompt,
          systemPromptAskMode: this.systemPromptAskMode,
          systemPromptFastMode: this.systemPromptFastMode,
          isFastMode: this.isFastMode,
          toolBlacklist: this.toolBlacklist,
          mode,
          tools,
          systemPromptMessages,
          fetchNotebookState,
          notebookContextManager,
          notebookId: notebookId,
          abortSignal: this.abortController!.signal,
          errorLogger
        },
        filteredHistory,
        ServiceUtils.normalizeMessageContent
      );
    } catch (error) {
      const errMsg = {
        message: 'Error creating message stream',
        error: error instanceof Error ? error.message : error,
        variables: {
          modelName: this.modelName,
          isFastMode: this.isFastMode,
          mode,
          availableTools: tools.map(t => t.name)
        }
      };
      errorLogger && (await errorLogger(JSON.stringify(errMsg)));
      throw error;
    }
  }

  /**
   * Handles request errors and retries
   */
  private async handleRequestError(
    error: any,
    onRetry?: (error: Error, attemptNumber: number) => Promise<void>,
    filteredHistory?: any[],
    tools?: any[],
    mode?: 'agent' | 'ask',
    systemPromptMessages?: string[],
    fetchNotebookState?: () => Promise<string>,
    onTextChunk?: (text: string) => void,
    onToolUse?: (toolUse: any) => void,
    notebookContextManager?: any,
    notebookPath?: string,
    errorLogger?: (message: any) => Promise<void>,
    forceRetry: boolean = false
  ): Promise<any> {
    if (this.isRequestCancelled()) {
      return ServiceUtils.createCancelledResponse(
        errorLogger,
        this.requestStatus
      );
    }

    await this.logRequestError(error, errorLogger, mode, filteredHistory);

    if (await this.shouldSkipRetry(error, forceRetry, errorLogger)) {
      throw error;
    }

    if (onRetry) {
      return await this.executeRetry(
        onRetry,
        error,
        filteredHistory!,
        tools!,
        mode!,
        systemPromptMessages,
        fetchNotebookState,
        onTextChunk,
        onToolUse,
        notebookContextManager,
        notebookPath,
        errorLogger
      );
    }

    this.requestStatus = ChatRequestStatus.ERROR;
    throw error;
  }

  /**
   * Logs request errors
   */
  private async logRequestError(
    error: any,
    errorLogger?: (message: any) => Promise<void>,
    mode?: 'agent' | 'ask',
    filteredHistory?: any[]
  ): Promise<void> {
    const errMsg = {
      message: 'Error calling Anthropic API',
      error: error instanceof Error ? error.message : error,
      modelName: this.modelName,
      mode,
      isFastMode: this.isFastMode,
      filteredHistory,
      requestStatus: this.requestStatus
    };
    errorLogger && (await errorLogger(JSON.stringify(errMsg)));
  }

  /**
   * Determines if retry should be skipped
   */
  private async shouldSkipRetry(
    error: any,
    forceRetry: boolean,
    errorLogger?: (message: any) => Promise<void>
  ): Promise<boolean> {
    if (
      error.name === 'BadRequestError' &&
      error.status === 400 &&
      !forceRetry
    ) {
      this.requestStatus = ChatRequestStatus.ERROR;
      await errorLogger?.({
        message: 'Bad request (400) error - not retrying',
        error: error instanceof Error ? error.message : error
      });
      return true;
    }
    return false;
  }

  /**
   * Executes retry logic with progressive backoff
   */
  private async executeRetry(
    onRetry: (error: Error, attemptNumber: number) => Promise<void>,
    error: any,
    filteredHistory: any[],
    tools: any[],
    mode: 'agent' | 'ask',
    systemPromptMessages?: string[],
    fetchNotebookState?: () => Promise<string>,
    onTextChunk?: (text: string) => void,
    onToolUse?: (toolUse: any) => void,
    notebookContextManager?: any,
    notebookPath?: string,
    errorLogger?: (message: any) => Promise<void>
  ): Promise<any> {
    this.requestStatus = ChatRequestStatus.RETRYING;

    // Progressive backoff delays: 5s, 15s, 30s
    const retryDelays = [5000, 15000, 30000];
    const maxRetries = retryDelays.length;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        await onRetry(error, attempt);

        if (this.isRequestCancelled()) {
          return ServiceUtils.createCancelledResponse(
            errorLogger,
            this.requestStatus
          );
        }

        await this.waitForRetry(retryDelays[attempt - 1]);

        if (this.isRequestCancelled()) {
          return ServiceUtils.createCancelledResponse(
            errorLogger,
            this.requestStatus
          );
        }

        this.abortController = new AbortController();

        const result = await this.executeStreamRequest(
          filteredHistory,
          tools,
          mode,
          systemPromptMessages,
          fetchNotebookState,
          onTextChunk,
          onToolUse,
          notebookContextManager,
          notebookPath,
          errorLogger
        );

        if (!this.isRequestCancelled()) {
          this.requestStatus = ChatRequestStatus.COMPLETED;
        }

        return result;
      } catch (retryError: any) {
        if (this.isRequestCancelled()) {
          return ServiceUtils.createCancelledResponse(
            errorLogger,
            this.requestStatus
          );
        }

        // If this is the last attempt, throw the error
        if (attempt === maxRetries) {
          await errorLogger?.({
            message: 'All retry attempts failed',
            error:
              retryError instanceof Error ? retryError.message : retryError,
            requestStatus: this.requestStatus,
            attemptNumber: attempt
          });

          this.requestStatus = ChatRequestStatus.ERROR;

          AppStateService.getState().chatContainer?.chatWidget.llmStateDisplay.hide();

          // Create a user-friendly error message
          const friendlyErrorMessage =
            retryError instanceof Error
              ? retryError.message
              : 'Unknown error occurred';

          const finalError = new Error(
            `Failed to connect to AI service after 3 attempts. ${friendlyErrorMessage}`
          );

          throw finalError;
        }

        // Log retry attempt failure but continue to next attempt
        await errorLogger?.({
          message: `Retry attempt ${attempt} failed, will try again`,
          error: retryError instanceof Error ? retryError.message : retryError,
          requestStatus: this.requestStatus,
          attemptNumber: attempt
        });

        // Update error for next attempt
        error = retryError;
      }
    }

    // This should never be reached, but TypeScript needs it
    throw error;
  }

  /**
   * Waits before retry with cancellation checking
   */
  private async waitForRetry(delayMs: number = 5000): Promise<void> {
    await new Promise(resolve => {
      const timeoutId = setTimeout(resolve, delayMs);

      const intervalId = setInterval(() => {
        if (this.isRequestCancelled()) {
          clearTimeout(timeoutId);
          clearInterval(intervalId);
          resolve(null);
        }
      }, 500);

      setTimeout(() => clearInterval(intervalId), delayMs);
    });
  }

  /**
   * Set the system prompt dynamically (for quick edit mode, etc.)
   */
  setSystemPrompt(prompt: string): void {
    this.systemPrompt = prompt;
  }

  /**
   * Set the tool blacklist dynamically (for quick edit mode, etc.)
   */
  setToolBlacklist(blacklist: string[]): void {
    this.toolBlacklist = Array.isArray(blacklist) ? [...blacklist] : [];
  }
}
