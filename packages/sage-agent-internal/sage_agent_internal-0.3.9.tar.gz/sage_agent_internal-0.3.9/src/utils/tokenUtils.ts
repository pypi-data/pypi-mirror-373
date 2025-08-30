/**
 * Utility functions for token counting and estimation
 */

/**
 * Maximum recommended token count for a conversation before suggesting a new chat
 */
export const MAX_RECOMMENDED_TOKENS = 60000;

/**
 * Estimates the token count for a given text using a simple approximation
 * This is based on the general rule that 1 token ≈ 4 characters for English text
 * @param text The text to estimate tokens for
 * @returns Estimated token count
 */
export function estimateTokenCount(text: string): number {
  if (!text) return 0;

  // Remove excessive whitespace and normalize
  const normalizedText = text.trim().replace(/\s+/g, ' ');

  // Rough approximation: 1 token ≈ 4 characters
  // This is conservative and accounts for the fact that tokens can be partial words
  return Math.ceil(normalizedText.length / 4);
}

/**
 * Estimates the total token count for an array of messages
 * @param messages Array of messages with content
 * @returns Estimated total token count
 */
export function estimateMessagesTokenCount(messages: any[]): number {
  if (!messages || messages.length === 0) return 0;

  let totalTokens = 0;

  for (const message of messages) {
    if (message.content) {
      if (typeof message.content === 'string') {
        totalTokens += estimateTokenCount(message.content);
      } else if (Array.isArray(message.content)) {
        // Handle structured content (like tool calls)
        for (const contentItem of message.content) {
          if (contentItem.text) {
            totalTokens += estimateTokenCount(contentItem.text);
          } else if (contentItem.input) {
            // For tool calls, count the input as well
            totalTokens += estimateTokenCount(
              JSON.stringify(contentItem.input)
            );
          } else if (contentItem.content) {
            // For tool results
            totalTokens += estimateTokenCount(
              JSON.stringify(contentItem.content)
            );
          }
        }
      }
    }

    // Add a small overhead for message structure (role, metadata, etc.)
    totalTokens += 10;
  }

  return totalTokens;
}

/**
 * Checks if the conversation has exceeded the recommended token limit
 * @param messages Array of messages to check
 * @returns Object with information about whether limit is exceeded
 */
export function checkTokenLimit(messages: any[]): {
  exceeded: boolean;
  estimatedTokens: number;
  maxRecommended: number;
  percentageUsed: number;
} {
  const estimatedTokens = estimateMessagesTokenCount(messages);
  const exceeded = estimatedTokens > MAX_RECOMMENDED_TOKENS;
  const percentageUsed = Math.round(
    (estimatedTokens / MAX_RECOMMENDED_TOKENS) * 100
  );

  return {
    exceeded,
    estimatedTokens,
    maxRecommended: MAX_RECOMMENDED_TOKENS,
    percentageUsed
  };
}
