import Anthropic from '@anthropic-ai/sdk';

export interface StreamHandlerConfig {
  onTextChunk?: (text: string) => void;
  onToolUse?: (toolUse: any) => void;
  errorLogger?: (message: any) => Promise<void>;
  isRequestCancelled: () => boolean;
}

export interface StreamResult {
  cancelled?: boolean;
  role: string;
  content: any[];
  needsUserConfirmation?: boolean;
  [key: string]: any;
}

export interface StreamCreationParams {
  client: Anthropic;
  modelName: string;
  messages: any[];
  tools?: any[];
  systemPrompt: string;
  extraSystemMessages?: any[];
  abortSignal: AbortSignal;
}

/**
 * Handles Anthropic API stream creation and processing
 * Separated from AnthropicService to reduce cyclic complexity
 */
export class AnthropicStreamHandler {
  private static readonly DELTA_CHUNK_THRESHOLD = 30;
  private static readonly DELTA_UPDATE_INTERVAL = 100;

  /**
   * Processes a message stream and returns the final result
   */
  static async processStream(
    stream: any,
    config: StreamHandlerConfig,
    conversationHistory: any[]
  ): Promise<StreamResult> {
    if (!stream) {
      const error = new Error('Message stream is undefined');
      await config.errorLogger?.({ message: error.message, stream });
      throw error;
    }

    const context = this.initializeStreamContext();
    this.setupTextChunkHandler(stream, config);

    try {
      await this.processStreamEvents(stream, context, config);

      if (config.isRequestCancelled()) {
        return this.createCancelledResult();
      }

      const finalMessage = await this.getFinalMessage(stream, config);

      return {
        ...finalMessage,
        needsUserConfirmation: context.needsUserConfirmation
      };
    } catch (error: any) {
      return this.handleStreamError(error, config, context);
    }
  }

  /**
   * Initializes the stream processing context
   */
  private static initializeStreamContext() {
    return {
      toolUseInfo: null as any,
      needsUserConfirmation: false,
      messageContent: [] as any[],
      deltaChunkBuffer: '',
      lastDeltaUpdateTime: 0
    };
  }

  /**
   * Sets up the text chunk handler for streaming
   */
  private static setupTextChunkHandler(
    stream: any,
    config: StreamHandlerConfig
  ) {
    if (config.onTextChunk) {
      stream.on('text', (text: string) => {
        if (!config.isRequestCancelled()) {
          config.onTextChunk!(text);
        }
      });
    }
  }

  /**
   * Processes all stream events
   */
  private static async processStreamEvents(
    stream: any,
    context: any,
    config: StreamHandlerConfig
  ) {
    for await (const event of stream) {
      if (config.isRequestCancelled()) {
        await config.errorLogger?.({
          message: 'Stream processing stopped due to cancellation',
          event,
          requestStatus: 'CANCELLED'
        });
        return;
      }

      await this.handleStreamEvent(event, context, config);
    }
  }

  /**
   * Handles individual stream events
   */
  private static async handleStreamEvent(
    event: any,
    context: any,
    config: StreamHandlerConfig
  ) {
    switch (event.type) {
      case 'content_block_start':
        this.handleContentBlockStart(event, context, config);
        break;
      case 'content_block_delta':
        this.handleContentBlockDelta(event, context, config);
        break;
      case 'content_block_stop':
        await this.handleContentBlockStop(context, config);
        break;
    }
  }

  /**
   * Handles content block start events
   */
  private static handleContentBlockStart(
    event: any,
    context: any,
    config: StreamHandlerConfig
  ) {
    if (event.content_block.type === 'text') {
      context.messageContent.push({
        type: 'text',
        text: ''
      });
    } else if (event.content_block.type === 'tool_use') {
      this.handleToolUseStart(event.content_block, context, config);
    }
  }

  /**
   * Handles tool use start
   */
  private static handleToolUseStart(
    contentBlock: any,
    context: any,
    config: StreamHandlerConfig
  ) {
    context.toolUseInfo = contentBlock;

    const toolUseData = {
      type: 'tool_use',
      id: contentBlock.id,
      name: contentBlock.name,
      input: contentBlock.input
    };

    config.onToolUse?.(toolUseData);
    context.messageContent.push(toolUseData);

    // Check if this tool requires user confirmation
    if (
      contentBlock.name === 'execute_cell' ||
      contentBlock.name === 'edit_cell'
    ) {
      context.needsUserConfirmation = true;
    }
  }

  /**
   * Handles content block delta events
   */
  private static handleContentBlockDelta(
    event: any,
    context: any,
    config: StreamHandlerConfig
  ) {
    if (event.delta.type === 'text_delta') {
      this.handleTextDelta(event.delta, context);
    } else if (event.delta.type === 'input_json_delta') {
      this.handleInputJsonDelta(event.delta, context, config);
    }
  }

  /**
   * Handles text delta updates
   */
  private static handleTextDelta(delta: any, context: any) {
    for (let i = context.messageContent.length - 1; i >= 0; i--) {
      if (context.messageContent[i].type === 'text') {
        context.messageContent[i].text += delta.text;
        break;
      }
    }
  }

  /**
   * Handles input JSON delta updates with chunking
   */
  private static handleInputJsonDelta(
    delta: any,
    context: any,
    config: StreamHandlerConfig
  ) {
    for (let i = context.messageContent.length - 1; i >= 0; i--) {
      if (context.messageContent[i].type === 'tool_use') {
        this.processInputJsonDelta(delta, context, config, i);
        break;
      }
    }
  }

  /**
   * Processes input JSON delta with throttling
   */
  private static processInputJsonDelta(
    delta: any,
    context: any,
    config: StreamHandlerConfig,
    messageIndex: number
  ) {
    const currentTime = Date.now();
    const deltaJson = delta.partial_json;

    console.log('ON TOOL USE JSON', deltaJson);

    context.deltaChunkBuffer += deltaJson;

    const shouldUpdate =
      context.deltaChunkBuffer.length >= this.DELTA_CHUNK_THRESHOLD ||
      currentTime - context.lastDeltaUpdateTime >= this.DELTA_UPDATE_INTERVAL;

    if (shouldUpdate && config.onToolUse) {
      config.onToolUse({
        type: 'tool_use_delta',
        id: context.messageContent[messageIndex].id,
        name: context.messageContent[messageIndex].name,
        input_delta: context.deltaChunkBuffer
      });

      context.deltaChunkBuffer = '';
      context.lastDeltaUpdateTime = currentTime;
    }

    // Accumulate partial JSON input
    if (!context.messageContent[messageIndex].partialInput) {
      context.messageContent[messageIndex].partialInput = '';
    }
    context.messageContent[messageIndex].partialInput += deltaJson;
  }

  /**
   * Handles content block stop events
   */
  private static async handleContentBlockStop(
    context: any,
    config: StreamHandlerConfig
  ) {
    // Flush any remaining delta buffer
    if (context.deltaChunkBuffer.length > 0 && config.onToolUse) {
      this.flushDeltaBuffer(context, config);
    }

    await this.processFinalToolInput(context, config);
  }

  /**
   * Flushes remaining delta buffer
   */
  private static flushDeltaBuffer(context: any, config: StreamHandlerConfig) {
    for (let i = context.messageContent.length - 1; i >= 0; i--) {
      if (context.messageContent[i].type === 'tool_use') {
        config.onToolUse!({
          type: 'tool_use_delta',
          id: context.messageContent[i].id,
          name: context.messageContent[i].name,
          input_delta: context.deltaChunkBuffer
        });
        break;
      }
    }
    context.deltaChunkBuffer = '';
  }

  /**
   * Processes the final tool input
   */
  private static async processFinalToolInput(
    context: any,
    config: StreamHandlerConfig
  ) {
    try {
      const toolMessage = context.messageContent.find(
        (message: any) => message.type === 'tool_use' && message.partialInput
      );

      if (!toolMessage?.partialInput) {
        return;
      }

      const fullInput = toolMessage.partialInput;
      const isValidJson =
        fullInput.trim().startsWith('{') && fullInput.trim().endsWith('}');

      if (!isValidJson) {
        return;
      }

      const parsedInput = JSON.parse(fullInput);

      if (
        context.toolUseInfo &&
        context.toolUseInfo.id === context.toolUseInfo.id
      ) {
        context.toolUseInfo.input = parsedInput;

        config.onToolUse?.({
          type: 'tool_use_stop',
          id: context.toolUseInfo.id,
          name: context.toolUseInfo.name,
          input: parsedInput
        });
      }
    } catch (parseError) {
      console.log('[AnthropicStreamHandler] Could not parse final input:', {
        messageContent: context.messageContent,
        parseError
      });
    }
  }

  /**
   * Gets the final message from the stream
   */
  private static async getFinalMessage(
    stream: any,
    config: StreamHandlerConfig
  ) {
    try {
      return await stream.finalMessage();
    } catch (error) {
      const errorMessage = {
        message: 'Error getting final message from stream',
        error: error instanceof Error ? error.message : error
      };
      await config.errorLogger?.(errorMessage);
      throw error;
    }
  }

  /**
   * Creates a cancelled result
   */
  private static createCancelledResult(): StreamResult {
    return {
      cancelled: true,
      role: 'assistant',
      content: []
    };
  }

  /**
   * Handles stream processing errors
   */
  private static async handleStreamError(
    error: any,
    config: StreamHandlerConfig,
    context: any
  ): Promise<StreamResult> {
    if (error.name === 'AbortError' || config.isRequestCancelled()) {
      await config.errorLogger?.({
        message: 'Stream processing aborted due to cancellation',
        error: error instanceof Error ? error.message : error
      });
      return this.createCancelledResult();
    }

    await config.errorLogger?.({
      message: 'Error during stream processing',
      error: error instanceof Error ? error.message : error,
      messageContent: context.messageContent,
      toolUseInfo: context.toolUseInfo,
      needsUserConfirmation: context.needsUserConfirmation
    });

    throw error;
  }
}
