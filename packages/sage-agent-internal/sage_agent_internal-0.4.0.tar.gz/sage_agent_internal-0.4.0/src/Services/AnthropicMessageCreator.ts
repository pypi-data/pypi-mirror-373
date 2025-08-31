import Anthropic from '@anthropic-ai/sdk';
import { AppStateService } from '../AppState';
import { DatabaseMetadataCache } from './DatabaseMetadataCache';
import {
  extractNotebookVariables,
  filterKernelVariablesByNotebook
} from '../utils/VariableExtractor';
import { KernelPreviewUtils } from '../utils/kernelPreview';

export interface MessageCreationParams {
  client: Anthropic;
  modelName: string;
  systemPrompt: string;
  systemPromptAskMode: string;
  systemPromptFastMode: string;
  isFastMode: boolean;
  toolBlacklist: string[];
  mode: 'agent' | 'ask' | 'fast';
  tools: any[];
  systemPromptMessages?: string[];
  fetchNotebookState?: () => Promise<string>;
  notebookContextManager?: any;
  notebookId?: string;
  abortSignal: AbortSignal;
  errorLogger?: (message: any) => Promise<void>;
}

export interface PreparedMessages {
  initialMessages: any[];
  filteredHistory: any[];
  availableTools: any[];
  systemPrompt: string;
  extraSystemMessages: any[];
}

/**
 * Handles message preparation and stream creation for Anthropic API
 */
export class AnthropicMessageCreator {
  /**
   * Prepares messages and creates a stream
   */
  static async createMessageStream(
    params: MessageCreationParams,
    filteredHistory: any[],
    normalizeMessageContent: (
      messages: any[],
      errorLogger?: (message: any) => Promise<void>
    ) => any[]
  ): Promise<any> {
    const prepared = await this.prepareMessages(
      params,
      filteredHistory,
      normalizeMessageContent
    );

    return params.client.beta.messages.stream(
      {
        model: params.modelName,
        messages: [...prepared.initialMessages, ...prepared.filteredHistory],
        tools:
          prepared.availableTools.length > 0
            ? prepared.availableTools
            : undefined,
        max_tokens: 4096,
        system: [
          {
            text: prepared.systemPrompt,
            type: 'text',
            cache_control: {
              type: 'ephemeral'
            }
          },
          ...prepared.extraSystemMessages
        ] as Anthropic.Beta.Messages.BetaTextBlockParam[],
        betas: ['token-efficient-tools-2025-02-19']
      },
      {
        signal: params.abortSignal,
        headers: {
          'no-cors': 'true',
          'sec-fetch-mode': 'no-cors',
          mode: 'no-cors'
        }
      }
    );
  }

  /**
   * Prepares all messages and configuration for the API call
   */
  private static async prepareMessages(
    params: MessageCreationParams,
    filteredHistory: any[],
    normalizeMessageContent: (
      messages: any[],
      errorLogger?: (message: any) => Promise<void>
    ) => any[]
  ): Promise<PreparedMessages> {
    // Get notebook context
    const contextCellsContent = await this.getNotebookContext(params);

    // Prepare initial messages
    const initialMessages = this.prepareInitialMessages(contextCellsContent);

    // Normalize messages
    const normalizedInitialMessages = normalizeMessageContent(
      initialMessages,
      params.errorLogger
    );
    const normalizedFilteredHistory = normalizeMessageContent(
      filteredHistory,
      params.errorLogger
    );

    // Determine system prompt
    const systemPrompt = this.determineSystemPrompt(params);

    // Filter tools for fast mode
    const availableTools = this.filterTools(params);

    // Prepare extra system messages
    const extraSystemMessages = await this.prepareExtraSystemMessages(params);

    return {
      initialMessages: normalizedInitialMessages,
      filteredHistory: normalizedFilteredHistory,
      availableTools,
      systemPrompt,
      extraSystemMessages
    };
  }

  /**
   * Gets notebook context if available
   */
  private static async getNotebookContext(
    params: MessageCreationParams
  ): Promise<string> {
    try {
      if (params.notebookContextManager && params.notebookId) {
        return params.notebookContextManager.formatContextAsMessage(
          params.notebookId
        );
      }
    } catch (error) {
      await params.errorLogger?.({
        message: 'Error getting notebook context',
        error: error instanceof Error ? error.message : error,
        notebookPath: params.notebookId,
        notebookContextManager: !!params.notebookContextManager
      });
    }
    return '';
  }

  /**
   * Prepares initial messages with context
   */
  private static prepareInitialMessages(contextCellsContent: string): any[] {
    const initialMessages = [];

    if (contextCellsContent && contextCellsContent.trim() !== '') {
      initialMessages.push({
        role: 'user',
        content: contextCellsContent
      });
    }

    return initialMessages;
  }

  /**
   * Determines which system prompt to use
   */
  private static determineSystemPrompt(params: MessageCreationParams): string {
    if (params.mode === 'ask') {
      return params.systemPromptAskMode;
    } else if (params.mode === 'fast') {
      return params.systemPromptFastMode;
    }
    return params.systemPrompt;
  }

  /**
   * Filters tools based on fast mode settings
   */
  private static filterTools(params: MessageCreationParams): any[] {
    if (params.isFastMode && params.toolBlacklist.length > 0) {
      return params.tools.filter(
        tool => tool.name && !params.toolBlacklist.includes(tool.name)
      );
    }
    return params.tools;
  }

  /**
   * Prepares extra system messages
   */
  private static async prepareExtraSystemMessages(
    params: MessageCreationParams
  ): Promise<any[]> {
    const extraSystemMessages: any[] = [];

    // Add system prompt messages
    if (params.systemPromptMessages) {
      extraSystemMessages.push(
        ...params.systemPromptMessages.map(msg => ({
          text: msg,
          type: 'text'
        }))
      );
    }

    // Add inserted snippets context
    const insertedSnippets = AppStateService.getInsertedSnippets();
    if (insertedSnippets.length > 0) {
      const snippetsContext = insertedSnippets
        .map(
          snippet =>
            `Snippet Title: ${snippet.title}\nSnippet Description: ${snippet.description ? `${snippet.description}\n` : ''} === Begin ${snippet.title} Content === \n\n${snippet.content}\n\n=== END ${snippet.title} Content ===`
        )
        .join('\n\n');

      extraSystemMessages.push({
        type: 'text',
        text: `The user has inserted the following code snippets for context:\n\n${snippetsContext}`
      });
    }

    // Add notebook state
    if (params.fetchNotebookState) {
      try {
        const notebookState = await params.fetchNotebookState();
        if (notebookState) {
          extraSystemMessages.push({
            type: 'text',
            text: `This is the current notebook summary with edit history: ${notebookState}`
          });
        }
      } catch (error) {
        await params.errorLogger?.({
          message: 'Error fetching notebook state',
          error: error instanceof Error ? error.message : error,
          fetchNotebookState: !!params.fetchNotebookState
        });
      }
    }

    // Add kernel variables and objects preview
    try {
      const kernelPreview = await KernelPreviewUtils.getLimitedKernelPreview();
      console.log('KERNEL PREVIEW:', kernelPreview);

      const dburl = AppStateService.getState().settings.databaseUrl;

      if (kernelPreview) {
        extraSystemMessages.push({
          type: 'text',
          text: `Current Kernel Variables and Objects Preview:\n\n${kernelPreview.replace(dburl, '<DB_URL>')}`
        });
      }
    } catch (error) {
      console.warn(
        '[AnthropicMessageCreator] Error getting kernel preview:',
        error
      );
      await params.errorLogger?.({
        message: 'Error getting kernel preview',
        error: error instanceof Error ? error.message : error
      });
    }

    return extraSystemMessages;
  }
}
