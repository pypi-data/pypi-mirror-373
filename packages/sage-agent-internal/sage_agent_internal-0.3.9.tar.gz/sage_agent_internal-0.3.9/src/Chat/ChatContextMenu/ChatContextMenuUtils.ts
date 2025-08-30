/**
 * Utility functions for ChatContextMenu
 */
import { MentionContext } from './ChatContextLoaders';
import { CELL_ICON, DATA_ICON, SNIPPETS_ICON, VARIABLE_ICON } from './icons';

/**
 * Check if an HTML element is a textarea
 */
export function isTextArea(element: HTMLElement): boolean {
  return element.tagName.toLowerCase() === 'textarea';
}

/**
 * Get the current selection start position for both textarea and contentEditable elements
 */
export function getSelectionStart(element: HTMLElement): number {
  if (isTextArea(element)) {
    return (element as HTMLTextAreaElement).selectionStart || 0;
  } else {
    // Handle contentEditable div
    const selection = window.getSelection();
    if (!selection || selection.rangeCount === 0) return 0;

    const range = selection.getRangeAt(0);
    const preCaretRange = range.cloneRange();
    preCaretRange.selectNodeContents(element);
    preCaretRange.setEnd(range.startContainer, range.startOffset);

    return preCaretRange.toString().length;
  }
}

/**
 * Get the current input value for both textarea and contentEditable elements
 */
export function getInputValue(element: HTMLElement): string {
  if (isTextArea(element)) {
    return (element as HTMLTextAreaElement).value || '';
  } else {
    return element.textContent || '';
  }
}

/**
 * Set the input value for both textarea and contentEditable elements
 */
export function setInputValue(element: HTMLElement, value: string): void {
  if (isTextArea(element)) {
    (element as HTMLTextAreaElement).value = value;
  } else {
    element.textContent = value;
  }
}

/**
 * Create a range from character offsets for contentEditable elements
 */
export function createRangeFromOffsets(
  element: HTMLElement,
  startOffset: number,
  endOffset: number
): Range | null {
  const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);

  let currentOffset = 0;
  let startNode: Node | null = null;
  let startPos = 0;
  let endNode: Node | null = null;
  let endPos = 0;

  while (walker.nextNode()) {
    const node = walker.currentNode;
    const nodeLength = node.textContent?.length || 0;

    if (!startNode && currentOffset + nodeLength >= startOffset) {
      startNode = node;
      startPos = startOffset - currentOffset;
    }

    if (currentOffset + nodeLength >= endOffset) {
      endNode = node;
      endPos = endOffset - currentOffset;
      break;
    }

    currentOffset += nodeLength;
  }

  if (startNode && endNode) {
    const range = document.createRange();
    range.setStart(
      startNode,
      Math.min(startPos, startNode.textContent?.length || 0)
    );
    range.setEnd(endNode, Math.min(endPos, endNode.textContent?.length || 0));
    return range;
  }

  return null;
}

/**
 * Set selection range for both textarea and contentEditable elements
 */
export function setSelectionRange(
  element: HTMLElement,
  start: number,
  end: number
): void {
  if (isTextArea(element)) {
    const textarea = element as HTMLTextAreaElement;
    textarea.setSelectionRange(start, end);
  } else {
    // Handle contentEditable div
    const selection = window.getSelection();
    if (!selection) return;

    const range = createRangeFromOffsets(element, start, end);
    if (range) {
      selection.removeAllRanges();
      selection.addRange(range);
    }
  }
}

/**
 * Get caret coordinates for positioning dropdowns
 */
export function getCaretCoordinates(element: HTMLElement): {
  top: number;
  left: number;
  height: number;
} {
  const selection = window.getSelection();
  if (!selection || selection.rangeCount === 0) {
    return { top: 0, left: 0, height: 20 };
  }

  const range = selection.getRangeAt(0);
  const rect = range.getBoundingClientRect();
  const elementRect = element.getBoundingClientRect();

  return {
    top: rect.top - elementRect.top,
    left: rect.left - elementRect.left,
    height: rect.height || 20
  };
}

/**
 * Calculate a relevance score for an item based on search text
 */
export function calculateRelevanceScore(
  item: MentionContext,
  searchText: string
): number {
  const itemName = item.name.toLowerCase();
  const search = searchText.toLowerCase();

  if (!search) return 0;

  // Exact match gets highest score
  if (itemName === search) return 1000;

  // Starts with search text gets high score
  if (itemName.startsWith(search)) return 900;

  // Word boundary match (after space, underscore, etc.)
  const wordBoundaryRegex = new RegExp(`\\b${search}`, 'i');
  if (wordBoundaryRegex.test(itemName)) return 800;

  // Contains search text gets medium score
  if (itemName.includes(search)) return 700;

  // Fuzzy match - calculate based on character matches in order
  let fuzzyScore = 0;
  let searchIndex = 0;
  for (let i = 0; i < itemName.length && searchIndex < search.length; i++) {
    if (itemName[i] === search[searchIndex]) {
      fuzzyScore += 10;
      searchIndex++;
    }
  }

  // Only return fuzzy score if we matched all search characters
  if (searchIndex === search.length) {
    return 500 + fuzzyScore;
  }

  return 0;
}

/**
 * Get category ID for a given item type
 */
export function getCategoryForType(type: string): string {
  switch (type) {
    case 'snippets':
      return 'snippets';
    case 'data':
      return 'data';
    case 'variable':
      return 'variables';
    case 'cell':
      return 'cells';
    default:
      return '';
  }
}

/**
 * Get icon for context type
 */
export function getIconForType(type: string): string {
  switch (type) {
    case 'snippets':
      return SNIPPETS_ICON.svgstr;
    case 'data':
      return DATA_ICON.svgstr;
    case 'variable':
      return VARIABLE_ICON.svgstr;
    case 'cell':
      return CELL_ICON.svgstr;
    default:
      return '❓';
  }
}

/**
 * Position a dropdown element relative to coordinates with viewport overflow handling
 */
export function positionDropdown(
  dropdownElement: HTMLElement,
  coords: { top: number; left: number; height: number }
): void {
  let { top, left } = coords;

  // Invalid coordinates
  if (left < 0 || top < 0) return;

  dropdownElement.style.position = 'fixed';
  dropdownElement.style.left = `${left}px`;
  dropdownElement.style.zIndex = '9999';
  dropdownElement.style.maxHeight = '200px';
  dropdownElement.style.transform = 'translateY(-100%) translateY(-8px)';
  dropdownElement.style.marginBottom = '12px';

  // Adjust if overflowing viewport
  const rect = dropdownElement.getBoundingClientRect();

  // Amount overflowing bottom
  const overflowY = rect.bottom - window.innerHeight;
  if (overflowY + 30 > 0) {
    dropdownElement.style.maxHeight = `${dropdownElement.clientHeight - (overflowY + 30)}px`;
  }

  // Amount overflowing right
  const overflowX = rect.right - window.innerWidth;

  if (overflowX + 20 > 0) {
    dropdownElement.style.left = `${left - overflowX - 64}px`;
  }
}

/**
 * Create a dropdown item element with icon and text
 */
export function createDropdownItemElement(
  item: MentionContext,
  className: string,
  categoryId?: string
): HTMLDivElement {
  const itemElement = document.createElement('div');
  itemElement.className = className;
  itemElement.setAttribute('data-id', item.id);
  itemElement.setAttribute('data-type', item.type);

  if (categoryId) {
    itemElement.setAttribute('data-category', categoryId);
  }

  const iconElement = document.createElement('span');
  iconElement.className = 'sage-ai-mention-item-icon';

  // Use SVG icon for supported types, fallback to emoji for others
  const iconSvg = getIconForType(item.type);
  if (iconSvg !== '❓') {
    iconElement.innerHTML = iconSvg;
  } else {
    iconElement.textContent = iconSvg;
  }

  const textContainer = document.createElement('div');
  textContainer.style.flex = '1';

  const textElement = document.createElement('div');
  textElement.className = 'sage-ai-mention-item-text';
  textElement.textContent = item.name;

  textContainer.appendChild(textElement);

  if (item.description) {
    const descElement = document.createElement('div');
    descElement.className = 'sage-ai-mention-item-description';
    descElement.textContent = item.description;
    textContainer.appendChild(descElement);
  }

  itemElement.appendChild(iconElement);
  itemElement.appendChild(textContainer);

  return itemElement;
}

/**
 * Create a category item element for the dropdown
 */
export function createCategoryItemElement(category: {
  id: string;
  name: string;
  icon: string;
}): HTMLDivElement {
  const itemElement = document.createElement('div');
  itemElement.className = 'sage-ai-mention-item sage-ai-mention-category-main';
  itemElement.setAttribute('data-category', category.id);

  const iconElement = document.createElement('span');
  iconElement.className = 'sage-ai-mention-item-icon';

  // Use SVG icon based on category
  let iconSvg: string;
  switch (category.id) {
    case 'snippets':
      iconSvg = SNIPPETS_ICON.svgstr;
      break;
    case 'data':
      iconSvg = DATA_ICON.svgstr;
      break;
    case 'variables':
      iconSvg = VARIABLE_ICON.svgstr;
      break;
    case 'cells':
      iconSvg = CELL_ICON.svgstr;
      break;
    default:
      iconSvg = category.icon;
  }

  if (iconSvg && iconSvg !== category.icon) {
    iconElement.innerHTML = iconSvg;
  } else {
    iconElement.textContent = category.icon;
  }

  const textContainer = document.createElement('div');
  textContainer.style.flex = '1';

  const textElement = document.createElement('div');
  textElement.className = 'sage-ai-mention-item-text';
  textElement.textContent = category.name;

  textContainer.appendChild(textElement);

  itemElement.appendChild(iconElement);
  itemElement.appendChild(textContainer);

  return itemElement;
}

/**
 * Get empty message for a category
 */
export function getEmptyMessageForCategory(categoryId: string): string {
  switch (categoryId) {
    case 'data':
      return 'No datasets available. Add datasets to reference them here.';
    case 'variables':
      return 'No variables available. Define variables in your notebook to reference them here.';
    case 'cells':
      return 'No cells available. Create cells in your notebook to reference them here.';
    case 'snippets':
  return 'No rules available. Create rules using the Rules panel to reference them here.';
    default:
      return 'No items found';
  }
}
