import { AppStateService } from '../AppState';

/**
 * Utility functions for message formatting and processing
 */
export class ServiceUtils {
  /**
   * Parses user messages from conversation history
   * @param messages The conversation history
   * @param errorLogger Optional error logger function
   * @returns Parsed user messages
   */
  static parseUserMessages(messages: any[]): any[] {
    try {
      return messages.map(message =>
        this.isUserMessage(message)
          ? {
              role: 'user',
              content: message.content
            }
          : message
      );
    } catch (error) {
      console.error('Error in parseUserMessages:', error, { messages });
      return messages;
    }
  }

  /**
   * Identifies if a message is a user message
   * @param message The message to check
   * @returns boolean indicating if the message is a user message
   */
  static isUserMessage(message: any): boolean {
    return message && message.role === 'user';
  }

  /**
   * Identifies if a message is tool-related (tool_use or tool_result)
   * @param message The message to check
   * @returns boolean indicating if the message is tool-related
   */
  static isToolRelatedMessage(message: any): boolean {
    try {
      return (
        ServiceUtils.isToolUseMessage(message) ||
        ServiceUtils.isToolResultMessage(message)
      );
    } catch (error) {
      console.error('Error in isToolRelatedMessage:', error, { message });
      // Return false as a fallback
      return false;
    }
  }

  /**
   * Checks if a message is a tool_use message
   * @param message The message to check
   * @returns boolean indicating if the message is a tool_use message
   */
  static isToolUseMessage(message: any): boolean {
    return (
      message &&
      message.role === 'assistant' &&
      Array.isArray(message.content) &&
      message.content.length > 0 &&
      message.content[0].type === 'tool_use'
    );
  }

  /**
   * Checks if a message is a tool_result message
   * @param message The message to check
   * @returns boolean indicating if the message is a tool_result message
   */
  static isToolResultMessage(message: any): boolean {
    return (
      message &&
      message.role === 'user' &&
      Array.isArray(message.content) &&
      message.content.length > 0 &&
      message.content[0].type === 'tool_result'
    );
  }

  /**
   * Checks if a message is a diff_approval message
   * @param message The message to check
   * @returns boolean indicating if the message is a diff_approval message
   */
  static isDiffApprovalMessage(message: any): boolean {
    return (
      message &&
      message.role === 'diff_approval' &&
      Array.isArray(message.content) &&
      message.content.length > 0 &&
      message.content[0].type === 'diff_approval'
    );
  }

  /**
   * Filters conversation history to keep only the last 10 tool-related message pairs
   * while preserving all non-tool messages. A pair consists of a tool_use message
   * followed by its corresponding tool_result message.
   * @param messages The conversation history
   * @param errorLogger Optional error logger function
   * @returns Filtered conversation history
   */
  static filterToolMessages(
    _messages: Array<any>,
    errorLogger?: (message: any) => Promise<void>
  ): Array<any> {
    try {
      const messages = ServiceUtils.buildCleanedConversationHistory(
        _messages,
        errorLogger
      );
      if (AppStateService.getState().maxToolCallLimit) {
        let numCalls = 0;
        messages.forEach(message => {
          if (ServiceUtils.isToolRelatedMessage(message)) {
            numCalls += 1;
          }
        });
        if (
          numCalls > (AppStateService.getState().maxToolCallLimit as number)
        ) {
          console.log('Max tool call limit reached, cancelling llm loop');
          AppStateService.getState().chatContainer?.chatWidget.cancelMessage();
        }
      }

      // Find all tool-related message indices
      const toolMessageIndices: number[] = [];
      const toolUseIndices: number[] = [];
      const toolResultIndices: number[] = [];

      messages.forEach((message, index) => {
        if (ServiceUtils.isToolRelatedMessage(message)) {
          toolMessageIndices.push(index);

          if (ServiceUtils.isToolUseMessage(message)) {
            toolUseIndices.push(index);
          }

          if (ServiceUtils.isToolResultMessage(message)) {
            toolResultIndices.push(index);
          }
        }
      });

      // If we have 10 or fewer tool pairs, return all messages
      if (toolUseIndices.length <= 10) {
        return [...messages];
      }

      // Find the last 10 complete tool pairs
      const lastXToolUseIndices = toolUseIndices.slice(
        toolUseIndices.length - 10
      );
      const indicesToKeep = new Set<number>();

      // For each tool_use, find its corresponding tool_result and add both to keep set
      for (const toolUseIndex of lastXToolUseIndices) {
        indicesToKeep.add(toolUseIndex);

        // Find the next tool_result after this tool_use
        const nextToolResultIndex = toolResultIndices.find(
          resultIndex => resultIndex > toolUseIndex
        );

        if (nextToolResultIndex !== undefined) {
          indicesToKeep.add(nextToolResultIndex);
        }
      }

      // Filter messages: keep non-tool messages and tool messages that are in our keep set
      return messages.filter(
        (message, index) =>
          !ServiceUtils.isToolRelatedMessage(message) ||
          indicesToKeep.has(index)
      );
    } catch (error) {
      errorLogger &&
        errorLogger(
          `Error in filterToolMessages: ${error}, messages: ${JSON.stringify(_messages)}`
        );
      console.error('Error in filterToolMessages:', error, {
        messagesLength: _messages.length
      });
      // Return original messages as fallback
      return [..._messages];
    }
  }

  /**
   * Filters conversation history to remove all diff_approval messages,
   * preserving only non-diff_approval messages.
   * @param _messages The conversation history
   * @returns Filtered conversation history without diff_approval messages
   */
  static filterDiffApprovalMessages(_messages: Array<any>): Array<any> {
    return _messages.filter(
      message => !ServiceUtils.isDiffApprovalMessage(message)
    );
  }

  /**
   * Normalizes message content to ensure it's in the correct format for the API
   * @param messages Array of messages to normalize
   * @param errorLogger Optional error logger function
   * @returns Normalized messages
   */
  static normalizeMessageContent(
    messages: any[],
    errorLogger?: (message: any) => Promise<void>
  ): any[] {
    try {
      let normalizedMessages = messages.map(msg => {
        // Deep clone the message to avoid modifying the original
        const normalizedMsg = { ...msg };

        // Only process content if it's not a tool-related message
        if (!ServiceUtils.isToolRelatedMessage(normalizedMsg)) {
          // Handle array content
          if (Array.isArray(normalizedMsg.content)) {
            // Convert array to a single string if all elements are strings or simple types
            if (
              normalizedMsg.content.every(
                (item: any) =>
                  typeof item === 'string' ||
                  typeof item === 'number' ||
                  typeof item === 'boolean'
              )
            ) {
              normalizedMsg.content = normalizedMsg.content.join(' ');
            }
          }
        }

        return normalizedMsg;
      });

      return ServiceUtils.buildCleanedConversationHistory(
        normalizedMessages,
        errorLogger
      );
    } catch (error) {
      errorLogger &&
        errorLogger(
          `Error in normalizeMessageContent: ${error}, messages: ${JSON.stringify(messages)}`
        );
      console.error('Error in normalizeMessageContent:', error, {
        messagesLength: messages?.length
      });
      // Return original messages as fallback
      return messages;
    }
  }

  /**
   * Removes assistant tool_use messages that are not followed by a user tool_result message.
   * Also removes user tool_result messages that are not preceded by an assistant tool_use message.
   * @param initialMessages Array of messages to clean
   * @param errorLogger Optional error logger function
   * @returns Cleaned conversation history
   */
  static buildCleanedConversationHistory(
    initialMessages: any[],
    errorLogger?: (message: any) => Promise<void>
  ): any[] {
    try {
      const cleanedHistory: any[] = [];
      for (let i = 0; i < initialMessages.length; i++) {
        const currentMessage = initialMessages[i];

        if (ServiceUtils.isToolUseMessage(currentMessage)) {
          const nextMessage = initialMessages[i + 1];

          // Check if the next message is a user tool_result message
          const isUserToolResultNext =
            ServiceUtils.isToolResultMessage(nextMessage);
          // Keep the assistant tool_use message ONLY if it's followed by a user tool_result
          if (isUserToolResultNext) {
            cleanedHistory.push(currentMessage);
          } else {
            // If not followed by a tool_result, skip this assistant tool_use message
            console.log(
              'Removing unmatched assistant tool_use message:',
              JSON.stringify(currentMessage)
            );
          }
        } else if (ServiceUtils.isToolResultMessage(currentMessage)) {
          // Look backwards through the cleaned history to find a matching tool_use
          const previousMessage = cleanedHistory[cleanedHistory.length - 1];
          const isPreviousToolUse =
            ServiceUtils.isToolUseMessage(previousMessage);
          if (isPreviousToolUse) {
            // Check if this tool_use matches the current tool_result
            const toolUseId = previousMessage.content[0].id;
            const toolResultId = currentMessage.content[0].tool_use_id;

            // Keep the user tool_result message ONLY if it has a preceding tool_use
            if (toolUseId === toolResultId) {
              const properToolFormat = {
                role: currentMessage.role,
                content: currentMessage.content.map((toolUse: any) => ({
                  tool_use_id: toolUse.tool_use_id,
                  content: toolUse.content,
                  type: toolUse.type
                }))
              };

              cleanedHistory.push(properToolFormat);
            } else {
              console.log(
                'Removing unmatched user tool_result message (ID mismatch):',
                JSON.stringify(currentMessage)
              );
            }
          } else {
            // No preceding tool_use message found, remove this orphaned tool_result
            console.log(
              'Removing orphaned user tool_result message (no preceding tool_use):',
              JSON.stringify(currentMessage)
            );
          }
        } else {
          // Keep all other messages
          cleanedHistory.push(currentMessage);
        }
      }
      return cleanedHistory;
    } catch (error) {
      errorLogger &&
        errorLogger(
          `Error in buildCleanedConversationHistory: ${error}, messages: ${JSON.stringify(initialMessages)}`
        );
      console.error('Error in buildCleanedConversationHistory:', error, {
        messagesLength: initialMessages?.length
      });
      // Return original messages as fallback
      return initialMessages;
    }
  }

  /**
   * Creates a cancelled response object
   * @param errorLogger Optional error logger function
   * @param requestStatus Current request status for logging
   * @returns Cancelled response object
   */
  static async createCancelledResponse(
    errorLogger?: (message: any) => Promise<void>,
    requestStatus?: any
  ) {
    const errMsg = {
      message: 'Request was cancelled, skipping retry logic',
      requestStatus
    };
    errorLogger && (await errorLogger(JSON.stringify(errMsg)));
    return {
      cancelled: true,
      role: 'assistant',
      content: []
    };
  }
}
