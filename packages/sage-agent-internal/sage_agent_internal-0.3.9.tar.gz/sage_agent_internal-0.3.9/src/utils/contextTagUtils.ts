import { MentionContext } from '../Chat/ChatContextMenu/ChatContextLoaders';
import { ContextService } from '../Services/ContextService';

/**
 * Utility functions for parsing and generating context tags in messages
 */

export interface ParsedContextTag {
  contextId: string;
  type: 'SNIPPET_CONTEXT' | 'DATA_CONTEXT' | 'VARIABLE_CONTEXT' | 'CELL_CONTEXT';
  fullMatch: string;
  startIndex: number;
  endIndex: number;
}

/**
 * Regular expression to match context tags
 * Matches: <DATA_CONTEXT>#{context_id}</DATA_CONTEXT>, <SNIPPET_CONTEXT>#{context_id}</SNIPPET_CONTEXT>, etc.
 */
const CONTEXT_TAG_REGEX = /<(SNIPPET_CONTEXT|DATA_CONTEXT|VARIABLE_CONTEXT|CELL_CONTEXT)>\s*#\{([^}]+)\}\s*<\/\1>/g;

/**
 * Parse context tags from a message string
 */
export function parseContextTags(message: string): ParsedContextTag[] {
  const tags: ParsedContextTag[] = [];
  let match: RegExpExecArray | null;
  
  // Reset regex lastIndex to ensure we start from the beginning
  CONTEXT_TAG_REGEX.lastIndex = 0;
  
  while ((match = CONTEXT_TAG_REGEX.exec(message)) !== null) {
    tags.push({
      contextId: match[2],
      type: match[1] as ParsedContextTag['type'],
      fullMatch: match[0],
      startIndex: match.index,
      endIndex: match.index + match[0].length
    });
  }
  
  return tags;
}

/**
 * Generate a context tag for a given context item
 */
export function generateContextTag(context: MentionContext): string {
  const tagType = getContextTagType(context.type);
  return `<${tagType}>#{${context.id}}</${tagType}>`;
}

/**
 * Map context type to tag type
 */
function getContextTagType(contextType: string): string {
  switch (contextType) {
    case 'snippets':
      return 'SNIPPET_CONTEXT';
    case 'data':
      return 'DATA_CONTEXT';
    case 'variable':
      return 'VARIABLE_CONTEXT';
    case 'cell':
      return 'CELL_CONTEXT';
    default:
      return 'SNIPPET_CONTEXT'; // Default fallback
  }
}

/**
 * Replace context tags in a message with styled mentions
 * Returns HTML string with styled mentions
 */
export function renderContextTagsAsStyled(message: string): string {
  const contextService = ContextService.getInstance();
  const contextItems = contextService.getCurrentContextItems();
  
  return message.replace(CONTEXT_TAG_REGEX, (fullMatch, tagType, contextId) => {
    const context = contextItems.get(contextId);
    
    // Always render with proper colors based on tag type, regardless of validity
    const cssClass = getContextCssClassFromTagType(tagType);
    
    if (context) {
      // If context exists, use its name and description
      const displayName = context.name.replace(/\s+/g, '_');
      return `<span class="sage-ai-mention ${cssClass}" title="${context.description || context.name}" data-context-id="${contextId}">@${displayName}</span>`;
    } else {
      // If context not found, still render with proper colors but use contextId as display name
      return `<span class="sage-ai-mention ${cssClass}" title="Context ID: ${contextId}" data-context-id="${contextId}">@${contextId}</span>`;
    }
  });
}

/**
 * Get CSS class for context type from the actual context
 */
function getContextCssClass(contextType: string): string {
  switch (contextType) {
    case 'snippets':
      return 'sage-ai-mention-template';
    case 'data':
      return 'sage-ai-mention-data';
    case 'variable':
      return 'sage-ai-mention-variable';
    case 'cell':
      return 'sage-ai-mention-cell';
    default:
      return 'sage-ai-mention-default';
  }
}

/**
 * Get CSS class directly from tag type (e.g., CELL_CONTEXT -> sage-ai-mention-cell)
 */
function getContextCssClassFromTagType(tagType: string): string {
  switch (tagType) {
    case 'SNIPPET_CONTEXT':
      return 'sage-ai-mention-template';
    case 'DATA_CONTEXT':
      return 'sage-ai-mention-data';
    case 'VARIABLE_CONTEXT':
      return 'sage-ai-mention-variable';
    case 'CELL_CONTEXT':
      return 'sage-ai-mention-cell';
    default:
      return 'sage-ai-mention-default';
  }
}

/**
 * Get tag type from CSS class (reverse mapping)
 */
export function getTagTypeFromCssClass(element: Element): string {
  if (element.classList.contains('sage-ai-mention-template')) {
    return 'SNIPPET_CONTEXT';
  } else if (element.classList.contains('sage-ai-mention-data')) {
    return 'DATA_CONTEXT';
  } else if (element.classList.contains('sage-ai-mention-variable')) {
    return 'VARIABLE_CONTEXT';
  } else if (element.classList.contains('sage-ai-mention-cell')) {
    return 'CELL_CONTEXT';
  } else {
    return 'DATA_CONTEXT'; // Default fallback
  }
}

/**
 * Replace @ mentions in input text with context tags
 * This is used when sending messages to convert @mentions to context tags
 */
export function convertMentionsToContextTags(
  message: string, 
  activeContexts: Map<string, MentionContext>
): string {
  // Match @mentions (both @name and @{name with spaces})
  const mentionRegex = /@(?:\{([^}]+)\}|([a-zA-Z0-9_-]+))/g;
  
  return message.replace(mentionRegex, (fullMatch, bracketedName, simpleName) => {
    const mentionName = bracketedName || simpleName;
    
    // Find context by name
    for (const [contextId, context] of activeContexts.entries()) {
      const normalizedContextName = context.name.replace(/\s+/g, '_');
      if (normalizedContextName === mentionName || context.name === mentionName) {
        return generateContextTag(context);
      }
    }
    
    // If no context found, leave as is
    return fullMatch;
  });
}

/**
 * Strip context tags from message, leaving just the text content
 * Useful for getting clean text for processing
 */
export function stripContextTags(message: string): string {
  return message.replace(CONTEXT_TAG_REGEX, '');
}

/**
 * Extract context IDs from a message
 */
export function extractContextIds(message: string): string[] {
  const tags = parseContextTags(message);
  return tags.map(tag => tag.contextId);
}

/**
 * Replace context tags with plain text mentions for display in plain text contexts
 */
export function renderContextTagsAsPlainText(message: string): string {
  const contextService = ContextService.getInstance();
  const contextItems = contextService.getCurrentContextItems();
  
  return message.replace(CONTEXT_TAG_REGEX, (fullMatch, tagType, contextId) => {
    const context = contextItems.get(contextId);
    
    if (!context) {
      return `@${contextId}`;
    }
    
    return `@${context.name.replace(/\s+/g, '_')}`;
  });
}
