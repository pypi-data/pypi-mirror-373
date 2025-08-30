import { ChatRequestStatus } from '../types';

/**
 * Interface for chat services (Anthropic, Gemini, etc.)
 */
export interface IChatService {
  /**
   * Initialize the chat client
   * @param apiKey API key for authentication
   * @returns boolean indicating if initialization was successful
   */
  initialize(apiKey?: string, toolService?: any): Promise<boolean>;

  /**
   * Load system prompt from configuration
   */
  refreshSystemPrompt(): Promise<void>;

  /**
   * Check if the client is initialized
   * @returns boolean indicating if the client is initialized
   */
  isInitialized(): boolean;

  /**
   * Set the model name
   * @param modelName Name of the model to use
   */
  setModelName(modelName: string): void;

  /**
   * Get the current model name
   */
  getModelName(): string;

  /**
   * Get the current request status
   */
  getRequestStatus(): ChatRequestStatus;

  /**
   * Check if the current request is cancelled
   */
  isRequestCancelled(): boolean;

  /**
   * Cancel the current request if any
   */
  cancelRequest(): void;

  /**
   * Send a message to the API
   * @param newMessages The new messages to add to the conversation
   * @param tools Available tools
   * @param mode
   * @param onRetry Callback for retry attempts
   * @param fetchNotebookState Function to fetch the current notebook state
   * @param onTextChunk Callback for streaming text chunks as they arrive
   * @param notebookContextManager Context manager for notebook cells
   * @param notebookPath Path to the notebook
   * @param forceRetry Optional parameter to force retry on failure
   * @param errorLogger Error logger for debugging later
   */
  sendMessage(
    newMessages: any[],
    tools?: any[],
    mode?: 'agent' | 'ask' | 'fast',
    systemPromptMessages?: string[],
    onRetry?: (error: Error, attemptNumber: number) => Promise<void>,
    fetchNotebookState?: () => Promise<string>,
    onTextChunk?: (text: string) => void,
    onToolUse?: (toolUse: any) => void,
    notebookContextManager?: any,
    notebookPath?: string,
    errorLogger?: (message: any) => Promise<void>,
    forceRetry?: boolean
  ): Promise<any>;

  /**
   * Send an ephemeral message to the API
   * @param message The message to send
   * @param systemPrompt The system prompt to use
   * @param modelName The model to use
   * @param onTextChunk Optional callback for streaming text chunks as they arrive
   * @param options Optional configuration for the request
   * @param onRetry Optional callback for retry attempts
   */
  sendEphemeralMessage(
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
  ): Promise<string>;

  /**
   * Set fast mode on or off (optional)
   * @param enabled Whether fast mode should be enabled
   */
  setFastMode?(enabled: boolean): void;

  /**
   * Check if fast mode is enabled (optional)
   * @returns boolean indicating if fast mode is enabled
   */
  isFastModeEnabled?(): boolean;

  /**
   * Get the tool blacklist for fast mode (optional)
   * @returns Array of tool names that are blacklisted in fast mode
   */
  getToolBlacklist?(): string[];
}
