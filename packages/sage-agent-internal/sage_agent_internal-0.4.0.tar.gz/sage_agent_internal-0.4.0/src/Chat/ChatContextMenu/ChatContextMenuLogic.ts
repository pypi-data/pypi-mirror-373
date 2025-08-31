/**
 * Logic class for ChatContextMenu - separates business logic from React UI
 */
import { Contents } from '@jupyterlab/services';
import { ToolService } from '../../Services/ToolService';
import {
  ChatContextLoaders,
  MENTION_CATEGORIES,
  MentionContext
} from './ChatContextLoaders';
import {
  calculateRelevanceScore,
  getCaretCoordinates,
  getInputValue,
  getSelectionStart,
  setInputValue,
  setSelectionRange
} from './ChatContextMenuUtils';

/**
 * Interface for the ChatContextMenu state
 */
export interface IChatContextMenuState {
  isVisible: boolean;
  currentView: 'categories' | 'items';
  selectedCategory: string | null;
  selectedIndex: number;
  currentMentionText: string;
  contextItems: Map<string, MentionContext[]>;
}

/**
 * Business logic class for ChatContextMenu
 */
export class ChatContextMenuLogic {
  private chatInput: HTMLElement;
  private toolService: ToolService;
  private contentManager: Contents.IManager;
  private contextLoaders: ChatContextLoaders;
  private onContextSelected: ((context: MentionContext) => void) | null = null;
  private onStateChanged: ((state: IChatContextMenuState) => void) | null =
    null;

  // Navigation state
  private mentionTrigger: string = '@';
  private currentMentionStart: number = -1;

  private _state: IChatContextMenuState;

  constructor(
    chatInput: HTMLElement,
    contentManager: Contents.IManager,
    toolService: ToolService
  ) {
    this.chatInput = chatInput;
    this.contentManager = contentManager;
    this.toolService = toolService;
    this.contextLoaders = new ChatContextLoaders(contentManager, toolService);

    // Initialize state
    this._state = {
      isVisible: false,
      currentView: 'categories',
      selectedCategory: null,
      selectedIndex: 0,
      currentMentionText: '',
      contextItems: new Map()
    };

    // Set up event listeners
    this.setupEventListeners();

    // Initialize context items
    this.initializeContextItems();
  }

  /**
   * Set a callback to be invoked when a context item is selected
   */
  public setContextSelectedCallback(
    callback: (context: MentionContext) => void
  ): void {
    this.onContextSelected = callback;
  }

  /**
   * Set a callback to be invoked when state changes
   */
  public setStateChangedCallback(
    callback: (state: IChatContextMenuState) => void
  ): void {
    this.onStateChanged = callback;
  }

  /**
   * Get current state
   */
  public getState(): IChatContextMenuState {
    return { ...this._state };
  }

  /**
   * Initialize context items for each category
   */
  private async initializeContextItems(): Promise<void> {
    const contextItems = await this.contextLoaders.initializeContextItems();
    this.updateState({ contextItems });
  }

  /**
   * Set up event listeners for detecting @ mentions and handling selection
   */
  private setupEventListeners(): void {
    // Listen for input to detect @ character and filter dropdown
    this.chatInput.addEventListener('input', this.handleInput);

    // Listen for keydown to handle navigation and selection
    this.chatInput.addEventListener('keydown', this.handleKeyDown);

    // Close dropdown when clicking outside
    document.addEventListener('click', event => {
      if (event.target !== this.chatInput) {
        this.hideDropdown();
      }
    });
  }

  /**
   * Handle input events to detect @ mentions and update dropdown
   */
  private handleInput = (event: Event): void => {
    const cursorPosition = this.getSelectionStart();
    const inputValue = this.getInputValue();

    // Check if we're currently in a mention context
    if (this._state.isVisible) {
      // Check if cursor moved outside of the current mention
      if (
        cursorPosition < this.currentMentionStart ||
        !inputValue
          .substring(this.currentMentionStart, cursorPosition)
          .startsWith(this.mentionTrigger)
      ) {
        this.hideDropdown();
        return;
      }

      // Update the current mention text
      const currentMentionText = inputValue.substring(
        this.currentMentionStart + 1,
        cursorPosition
      );
      this.updateState({
        currentMentionText,
        selectedIndex: 0 // Reset selection when text changes
      });
      return;
    }

    // Look for a new mention
    if (inputValue.charAt(cursorPosition - 1) === this.mentionTrigger) {
      // Found a new mention
      this.currentMentionStart = cursorPosition - 1;
      this.showDropdown();
    }
  };

  /**
   * Get the current selection start position
   */
  private getSelectionStart(): number {
    return getSelectionStart(this.chatInput);
  }

  /**
   * Get the current input value
   */
  private getInputValue(): string {
    return getInputValue(this.chatInput);
  }

  /**
   * Set the input value
   */
  private setInputValue(value: string): void {
    setInputValue(this.chatInput, value);
  }

  /**
   * Set selection range
   */
  private setSelectionRange(start: number, end: number): void {
    setSelectionRange(this.chatInput, start, end);
  }

  /**
   * Get caret coordinates for positioning the dropdown
   */
  public getCaretCoordinates(): { top: number; left: number; height: number } {
    return getCaretCoordinates(this.chatInput);
  }

  /**
   * Handle item selection
   */
  public async handleItemSelect(item: MentionContext): Promise<void> {
    // Replace the mention with the selected item
    const beforeMention = this.getInputValue().substring(
      0,
      this.currentMentionStart
    );
    const afterMention = this.getInputValue().substring(
      this.getSelectionStart()
    );

    // Format: @{item name} - replace spaces with underscores for valid mention syntax
    const displayName = item.name.replace(/\s+/g, '_');
    const replacement = `@${displayName} `;

    // Update the input value
    this.setInputValue(beforeMention + replacement + afterMention);

    // Set cursor position after the inserted mention
    const newCursorPosition = this.currentMentionStart + replacement.length;
    this.setSelectionRange(newCursorPosition, newCursorPosition);

    // Hide the dropdown
    this.hideDropdown();

    // Focus the input
    this.chatInput.focus();

    // Load content if needed and invoke callback
    if (this.onContextSelected) {
      let contextWithContent = { ...item };

      if (item.type === 'snippets' && !item.content) {
        // For snippets, content should already be loaded from AppState
        // No additional loading needed
      }

      this.onContextSelected(contextWithContent);
    }
  }

  /**
   * Handle category selection
   */
  public handleCategorySelect(categoryId: string): void {
    this.updateState({
      selectedCategory: categoryId,
      currentView: 'items',
      selectedIndex: 0
    });
  }

  /**
   * Handle back to categories navigation
   */
  public handleBackToCategories(): void {
    this.updateState({
      currentView: 'categories',
      selectedCategory: null,
      selectedIndex: 0
    });
  }

  /**
   * Show the dropdown
   */
  public async showDropdown(): Promise<void> {
    this.currentMentionStart = this.getSelectionStart() - 1;

    // Load context items in specific order - variables first, then datasets (which includes DB metadata)
    const snippetContexts = await this.contextLoaders.loadSnippets();
    const variableContexts = await this.contextLoaders.loadVariables();
    const datasetContexts = await this.contextLoaders.loadDatasets();
    const cellContexts = await this.contextLoaders.loadCells();

    // Update context items
    const contextItems = new Map<string, MentionContext[]>();
    contextItems.set('snippets', snippetContexts);
    contextItems.set('data', datasetContexts);
    contextItems.set('variables', variableContexts);
    contextItems.set('cells', cellContexts);

    this.updateState({
      isVisible: true,
      currentView: 'categories',
      selectedCategory: null,
      selectedIndex: 0,
      currentMentionText: '',
      contextItems
    });
  }

  /**
   * Hide the dropdown
   */
  public hideDropdown(): void {
    this.currentMentionStart = -1;
    this.updateState({
      isVisible: false,
      currentView: 'categories',
      selectedCategory: null,
      currentMentionText: ''
    });
  }

  /**
   * Handle keydown events for navigation and selection
   */
  private handleKeyDown = (event: KeyboardEvent): void => {
    if (!this._state.isVisible) return;

    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        this.navigateDropdown('down');
        break;
      case 'ArrowUp':
        event.preventDefault();
        this.navigateDropdown('up');
        break;
      case 'Tab':
        event.preventDefault();
        this.selectCurrentItem();
        break;
      case 'Enter':
        event.preventDefault();
        this.selectCurrentItem();
        break;
      case 'Escape':
        event.preventDefault();
        this.hideDropdown();
        break;
    }
  };

  /**
   * Navigate through dropdown items
   */
  private navigateDropdown(direction: 'up' | 'down'): void {
    // This will be handled by the React component through state
    const totalItems = this.getTotalItemsCount();
    if (totalItems === 0) return;

    let newIndex: number;
    if (direction === 'down') {
      newIndex = (this._state.selectedIndex + 1) % totalItems;
    } else {
      newIndex =
        this._state.selectedIndex <= 0
          ? totalItems - 1
          : this._state.selectedIndex - 1;
    }

    this.updateState({ selectedIndex: newIndex });
  }

  /**
   * Get total items count for navigation
   */
  private getTotalItemsCount(): number {
    if (this._state.currentView === 'categories') {
      // Count matching items + categories
      let count = 0;
      if (
        this._state.currentMentionText &&
        this._state.currentMentionText.length > 0
      ) {
        // Count matching items
        for (const [categoryId, items] of this._state.contextItems.entries()) {
          for (const item of items) {
            const score = calculateRelevanceScore(
              item,
              this._state.currentMentionText
            );
            if (score > 0) {
              count++;
            }
          }
        }
        // Limit to 5 matching items
        count = Math.min(count, 5);

        // Add categories if search is short or no matches
        if (count === 0 || this._state.currentMentionText.length < 2) {
          count += MENTION_CATEGORIES.length;
        }
      } else {
        count = MENTION_CATEGORIES.length;
      }
      return count;
    } else {
      // In category view: back button + items
      const items =
        this._state.contextItems.get(this._state.selectedCategory!) || [];
      return 1 + items.length; // +1 for back button
    }
  }

  /**
   * Select the currently highlighted item
   */
  public selectCurrentItem(): void {
    if (this._state.currentView === 'categories') {
      // Check if we have matching items in search mode
      if (
        this._state.currentMentionText &&
        this._state.currentMentionText.length > 0
      ) {
        const matchingItems: Array<{
          item: MentionContext;
          categoryId: string;
        }> = [];

        // Collect matching items from all categories
        for (const [categoryId, items] of this._state.contextItems.entries()) {
          for (const item of items) {
            const score = calculateRelevanceScore(
              item,
              this._state.currentMentionText
            );
            if (score > 0) {
              matchingItems.push({ item, categoryId });
            }
          }
        }

        // Sort and limit to 5 items
        matchingItems.sort((a, b) => {
          const scoreA = calculateRelevanceScore(
            a.item,
            this._state.currentMentionText
          );
          const scoreB = calculateRelevanceScore(
            b.item,
            this._state.currentMentionText
          );
          if (scoreA !== scoreB) {
            return scoreB - scoreA;
          }
          return a.item.name.localeCompare(b.item.name);
        });

        const limitedItems = matchingItems.slice(0, 5);

        if (this._state.selectedIndex < limitedItems.length) {
          // Select matching item
          this.handleItemSelect(limitedItems[this._state.selectedIndex].item);
          return;
        } else if (
          !limitedItems.length ||
          this._state.currentMentionText.length < 2
        ) {
          // Select category (adjust index for categories)
          const categoryIndex = this._state.selectedIndex - limitedItems.length;
          if (categoryIndex >= 0 && categoryIndex < MENTION_CATEGORIES.length) {
            this.handleCategorySelect(MENTION_CATEGORIES[categoryIndex].id);
          }
          return;
        }
      } else {
        // No search text, select category
        if (
          this._state.selectedIndex >= 0 &&
          this._state.selectedIndex < MENTION_CATEGORIES.length
        ) {
          this.handleCategorySelect(
            MENTION_CATEGORIES[this._state.selectedIndex].id
          );
        }
        return;
      }
    } else if (this._state.selectedCategory) {
      // In category view
      if (this._state.selectedIndex === 0) {
        // Back button selected
        this.handleBackToCategories();
        return;
      }

      const items =
        this._state.contextItems.get(this._state.selectedCategory) || [];
      const itemIndex = this._state.selectedIndex - 1; // Subtract 1 for back button

      if (itemIndex >= 0 && itemIndex < items.length) {
        this.handleItemSelect(items[itemIndex]);
      }
    }
  }

  /**
   * Update state and emit callback
   */
  private updateState(updates: Partial<IChatContextMenuState>): void {
    this._state = { ...this._state, ...updates };
    if (this.onStateChanged) {
      this.onStateChanged(this._state);
    }
  }

  /**
   * Public methods for external control
   */
  public getIsVisible(): boolean {
    return this._state.isVisible;
  }

  public selectHighlightedItem(): void {
    this.selectCurrentItem();
  }

  /**
   * Clean up event listeners
   */
  public dispose(): void {
    this.chatInput.removeEventListener('input', this.handleInput);
    this.chatInput.removeEventListener('keydown', this.handleKeyDown);
  }
}
