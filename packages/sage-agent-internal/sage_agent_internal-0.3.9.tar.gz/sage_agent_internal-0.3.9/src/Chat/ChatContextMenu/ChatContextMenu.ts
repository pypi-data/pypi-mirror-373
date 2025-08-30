/**
 * Class to handle the mention dropdown functionality in the chat input
 */
import {Contents} from '@jupyterlab/services';
import {ToolService} from '../../Services/ToolService';
import {ContextCacheService} from './ContextCacheService';
import {ChatContextLoaders, MENTION_CATEGORIES, MentionContext} from './ChatContextLoaders';
import {
    calculateRelevanceScore,
    createCategoryItemElement,
    createDropdownItemElement,
    getCaretCoordinates,
    getCategoryForType,
    getEmptyMessageForCategory,
    getInputValue,
    getSelectionStart,
    positionDropdown,
    setInputValue,
    setSelectionRange
} from './ChatContextMenuUtils';
import {BACK_CARET_ICON, SEARCH_ICON} from './icons';

// Re-export for backward compatibility
export type { MentionContext };

export class ChatContextMenu {
  private dropdownElement: HTMLDivElement;
  private searchInput: HTMLInputElement;
  private searchContainer: HTMLDivElement;
  private headerContainer: HTMLDivElement;
  private contentContainer: HTMLDivElement;
  private chatInput: HTMLElement; // Changed from HTMLTextAreaElement to HTMLElement
  private toolService: ToolService;
  private isVisible: boolean = false;
  private mentionTrigger: string = '@';
  private currentMentionStart: number = -1;
  private currentMentionText: string = '';
  private searchText: string = '';
  private contentManager: Contents.IManager;
  private onContextSelected: ((context: MentionContext) => void) | null = null;
  private contextLoaders: ChatContextLoaders;
  private contextCacheService: ContextCacheService;

  // Navigation state
  private currentView: 'categories' | 'items' = 'categories';
  private selectedCategory: string | null = null;
  private selectedIndex: number = 0;

  // Categories and their items
  private categories = MENTION_CATEGORIES;

  private contextItems: Map<string, MentionContext[]> = new Map();

  constructor(
    chatInput: HTMLElement, // Changed from HTMLTextAreaElement to HTMLElement
    parentElement: HTMLElement,
    contentManager: Contents.IManager,
    toolService: ToolService
  ) {
    this.chatInput = chatInput;
    this.contentManager = contentManager;
    this.toolService = toolService;
    this.contextLoaders = new ChatContextLoaders(contentManager, toolService);
    this.contextCacheService = ContextCacheService.getInstance();

    // Create dropdown element
    this.dropdownElement = document.createElement('div');
    this.dropdownElement.className = 'sage-ai-mention-dropdown';

    // Create header container for category title and search
    this.headerContainer = document.createElement('div');
    this.headerContainer.className = 'sage-ai-mention-header-container';

    // Create search container with icon and input
    this.searchContainer = document.createElement('div');
    this.searchContainer.className = 'sage-ai-mention-search-container';

    // Create search icon
    const searchIcon = SEARCH_ICON.element({
      className: 'sage-ai-mention-search-icon'
    });

    // Create search input
    this.searchInput = document.createElement('input');
    this.searchInput.type = 'text';
    this.searchInput.className = 'sage-ai-mention-search-input';
    this.searchInput.placeholder = 'Search...';

    // Add icon and input to search container
    this.searchContainer.appendChild(searchIcon);
    this.searchContainer.appendChild(this.searchInput);

    // Add search container to header container
    this.headerContainer.appendChild(this.searchContainer);

    // Create content container
    this.contentContainer = document.createElement('div');
    this.contentContainer.className = 'sage-ai-mention-content';

    // Add elements to dropdown
    this.dropdownElement.appendChild(this.headerContainer);
    this.dropdownElement.appendChild(this.contentContainer);

    parentElement.appendChild(this.dropdownElement);

    // Set up event listeners
    this.setupEventListeners();

    // Initialize context items for each category
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
   * Initialize context items for each category
   */
  private async initializeContextItems(): Promise<void> {
    this.contextItems = await this.contextLoaders.initializeContextItems();
  }

  /**
   * Set up event listeners for detecting @ mentions and handling selection
   */
  private setupEventListeners(): void {
    // Listen for input to detect @ character and filter dropdown
    this.chatInput.addEventListener('input', this.handleInput);

    // Listen for keydown to handle navigation and selection
    this.chatInput.addEventListener('keydown', this.handleKeyDown);

    // Listen for search input changes
    this.searchInput.addEventListener('input', this.handleSearchInput);
    this.searchInput.addEventListener('keydown', this.handleSearchKeyDown);

    // Close dropdown when clicking outside
    document.addEventListener('click', event => {
      if (
        !this.dropdownElement.contains(event.target as Node) &&
        event.target !== this.chatInput
      ) {
        this.hideDropdown();
      }
    });

    // Handle clicks on dropdown items
    this.dropdownElement.addEventListener('click', this.handleDropdownClick);
  }

  /**
   * Handle input events to detect @ mentions and update dropdown
   */
  private handleInput = (event: Event): void => {
    const cursorPosition = this.getSelectionStart();
    const inputValue = this.getInputValue();

    // Check if we're currently in a mention context
    if (this.isVisible) {
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

      // Update the current mention text and search input to reflect what's being typed
      this.currentMentionText = inputValue.substring(
        this.currentMentionStart + 1,
        cursorPosition
      );

      // Sync the search input with what the user is typing after @
      if (this.searchInput.value !== this.currentMentionText) {
        this.searchInput.value = this.currentMentionText;
        this.searchText = this.currentMentionText;
      }

      this.renderDropdown(this.searchText);
      return;
    }

    // Look for a new mention
    if (inputValue.charAt(cursorPosition - 1) === this.mentionTrigger) {
      // Found a new mention
      this.currentMentionStart = cursorPosition - 1;
      this.currentMentionText = '';
      this.showDropdown();
    }
  };

  /**
   * Handle search input changes
   */
  private handleSearchInput = (event: Event): void => {
    const target = event.target as HTMLInputElement;
    this.searchText = target.value;
    this.selectedIndex = 0; // Reset selection when search changes
    this.renderDropdown(this.searchText);
  };

  /**
   * Handle keydown events in the search input
   */
  private handleSearchKeyDown = (event: KeyboardEvent): void => {
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
  private getCaretCoordinates(): { top: number; left: number; height: number } {
    return getCaretCoordinates(this.chatInput);
  }

  /**
   * Position the dropdown relative to the current cursor position
   */
  private positionDropdown(): void {
    if (!this.isVisible) return;

    const coords = this.getCaretCoordinates();
    console.log('Caret coordinates:', coords); // Debug log

    positionDropdown(this.dropdownElement, coords);
  }

  /**
   * Update the category header based on current view
   */
  private updateCategoryHeader(): void {
    // Remove existing category header if present
    const existingHeader = this.headerContainer.querySelector(
      '.sage-ai-mention-category-header'
    );
    if (existingHeader) {
      existingHeader.remove();
    }

    // Add category header only when in items view
    if (this.currentView === 'items' && this.selectedCategory) {
      const categoryHeader = document.createElement('div');
      categoryHeader.className = 'sage-ai-mention-category-header';

      // Create back caret icon
      const backIcon = BACK_CARET_ICON.element({
        className: 'sage-ai-mention-back-icon'
      });

      // Create category title
      const categoryTitle = document.createElement('span');
      categoryTitle.className = 'sage-ai-mention-category-title';

      // Find the category name
      const category = this.categories.find(
        cat => cat.id === this.selectedCategory
      );
      categoryTitle.textContent = category?.name || this.selectedCategory;

      // Add click handler for navigation back
      categoryHeader.addEventListener('click', () => {
        this.currentView = 'categories';
        this.selectedCategory = null;
        this.selectedIndex = 0;
        this.renderDropdown(this.searchText);
      });

      categoryHeader.appendChild(backIcon);
      categoryHeader.appendChild(categoryTitle);

      // Insert at the beginning of header container
      this.headerContainer.insertBefore(categoryHeader, this.searchContainer);
    }
  }

  /**
   * Render the dropdown based on current view and search text
   */
  private renderDropdown(searchText: string): void {
    this.contentContainer.innerHTML = '';

    // Update the category header based on current view
    this.updateCategoryHeader();

    if (this.currentView === 'categories') {
      // Always show database schema first if available
      const hasDbSchema = this.renderDatabaseSchema(searchText);

      // If there's search text, show matching items next
      if (searchText && searchText.length > 0) {
        const hasMatchingItems = this.renderMatchingItems(searchText);

        // Add a separator before categories if we have database schema or matching items
        if ((hasDbSchema || hasMatchingItems) && searchText.length < 2) {
          const separator = document.createElement('div');
          separator.className = 'sage-ai-mention-separator';
          separator.textContent = 'Categories';
          this.contentContainer.appendChild(separator);
        }

        // Only show categories if we don't have good matches or search is very short
        if (!hasMatchingItems || searchText.length < 2) {
          this.renderCategories();
        }
      } else {
        // No search text - add separator before categories if we have database schema
        if (hasDbSchema) {
          const separator = document.createElement('div');
          separator.className = 'sage-ai-mention-separator';
          separator.textContent = 'Categories';
          this.contentContainer.appendChild(separator);
        }
        this.renderCategories();
      }
    } else if (this.currentView === 'items' && this.selectedCategory) {
      // Show items in the category with filtering if there's search text
      this.renderCategoryItems(this.selectedCategory, searchText);
    }

    // Reset to first item and highlight it
    this.selectedIndex = 0;
    this.highlightItem(this.selectedIndex);
    this.positionDropdown();
  }

  /**
   * Calculate a relevance score for an item based on search text
   */
  private calculateRelevanceScore(
    item: MentionContext,
    searchText: string
  ): number {
    return calculateRelevanceScore(item, searchText);
  }

  /**
   * Render items that match the search text across all categories
   * @returns true if matching items were found and rendered, false otherwise
   */
  private renderMatchingItems(searchText: string): boolean {
    const matchingItems: Array<{ item: MentionContext; score: number }> = [];

    // Collect matching items from all categories with scores
    for (const [categoryId, items] of this.contextItems.entries()) {
      for (const item of items) {
        const score = this.calculateRelevanceScore(item, searchText);
        if (score > 500) {
          // Filter out items with too little relevance
          matchingItems.push({ item, score });
        }
      }
    }

    // Sort by score (highest first), then by name
    matchingItems.sort((a, b) => {
      if (a.score !== b.score) {
        return b.score - a.score;
      }
      return a.item.name.localeCompare(b.item.name);
    });

    if (matchingItems.length > 0) {
      // Limit to maximum 10 matching items
      matchingItems.slice(0, 10).forEach(({ item }) => {
        const itemElement = createDropdownItemElement(
          item,
          'sage-ai-mention-item sage-ai-mention-subcategory',
          getCategoryForType(item.type)
        );
        this.contentContainer.appendChild(itemElement);
      });

      return true;
    }

    return false;
  }

  /**
   * Get category ID for a given item type
   */
  private getCategoryForType(type: string): string {
    return getCategoryForType(type);
  }

  /**
   * Render the categories view
   */
  private renderCategories(): void {
    this.categories.forEach(category => {
      const itemElement = createCategoryItemElement(category);
      this.contentContainer.appendChild(itemElement);
    });
  }

  /**
   * Render items for a specific category
   */
  private renderCategoryItems(
    categoryId: string,
    searchText: string = ''
  ): void {
    const items = this.contextItems.get(categoryId) || [];
    console.log(`Rendering items for category ${categoryId}:`, items); // Debug log

    if (items.length === 0) {
      const emptyElement = document.createElement('div');
      emptyElement.className = 'sage-ai-mention-empty';
      emptyElement.textContent = getEmptyMessageForCategory(categoryId);
      this.contentContainer.appendChild(emptyElement);
      return;
    }

    // Filter and sort items based on search text
    let displayItems = items;
    if (searchText) {
      const matchingItems: Array<{ item: MentionContext; score: number }> = [];

      for (const item of items) {
        const score = this.calculateRelevanceScore(item, searchText);
        if (score > 500) {
          // Filter out items with too little relevance
          matchingItems.push({ item, score });
        }
      }

      // Sort by score (highest first)
      matchingItems.sort((a, b) => {
        if (a.score !== b.score) {
          return b.score - a.score;
        }
        return a.item.name.localeCompare(b.item.name);
      });

      displayItems = matchingItems.slice(0, 10).map(({ item }) => item);
    }

    // Show filtered/sorted items
    displayItems.forEach(item => {
      const itemElement = createDropdownItemElement(
        item,
        'sage-ai-mention-item sage-ai-mention-subcategory'
      );
      this.contentContainer.appendChild(itemElement);
    });
  }

  /**
   * Render database schema item if available
   * @param searchText Optional search text to filter database schema
   * @returns true if database schema was rendered, false otherwise
   */
  private renderDatabaseSchema(searchText: string = ''): boolean {
    // Look for database schema in the data category
    const dataItems = this.contextItems.get('data') || [];
    const dbSchemaItem = dataItems.find(item => item.id === 'database-schema');

    if (!dbSchemaItem) {
      return false;
    }

    // If there's search text, check if database schema matches
    if (searchText && searchText.length > 0) {
      const score = this.calculateRelevanceScore(dbSchemaItem, searchText);
      if (score <= 500) {
        return false; // Don't show if relevance is too low
      }
    }

    // Create and append the database schema item
    const itemElement = createDropdownItemElement(
      dbSchemaItem,
      'sage-ai-mention-item sage-ai-mention-subcategory sage-ai-mention-database-schema',
      'data'
    );
    this.contentContainer.appendChild(itemElement);

    return true;
  }

  /**
   * Handle clicks on dropdown items
   */
  private handleDropdownClick = (event: Event): void => {
    event.preventDefault();
    event.stopPropagation();

    const target = event.target as Element;

    // Handle category selection
    const categoryItem = target.closest('.sage-ai-mention-category-main');
    if (categoryItem) {
      const categoryId = categoryItem.getAttribute('data-category');
      if (categoryId) {
        this.selectedCategory = categoryId;
        this.currentView = 'items';
        // Clear search when entering a category
        this.searchInput.value = '';
        this.searchText = '';
        this.updateSearchPlaceholder();
        this.renderDropdown(this.searchText);
        this.positionDropdown(); // Reposition after content change
        // Focus search input
        setTimeout(() => this.searchInput.focus(), 0);
      }
      return;
    }

    // Handle item selection
    const mentionItem = target.closest('.sage-ai-mention-subcategory');
    if (mentionItem) {
      const itemId = mentionItem.getAttribute('data-id');
      const categoryId = mentionItem.getAttribute('data-category');

      if (itemId) {
        // If we're selecting from the matching items section and have a category
        if (this.currentView === 'categories' && categoryId) {
          this.selectedCategory = categoryId;
        }

        this.selectItem(itemId);
      }
    }
  };

  /**
   * Highlight a specific item in the dropdown
   */
  private highlightItem(index: number): void {
    // Remove active class from all items
    const items = this.contentContainer.querySelectorAll(
      '.sage-ai-mention-item, .sage-ai-mention-subcategory'
    );
    items.forEach(item => item.classList.remove('active'));

    // Add active class to the specified item
    if (items.length > 0 && index >= 0 && index < items.length) {
      items[index].classList.add('active');

      // Scroll to the item if needed
      const itemElement = items[index] as HTMLElement;
      const contentRect = this.contentContainer.getBoundingClientRect();
      const itemRect = itemElement.getBoundingClientRect();

      if (itemRect.bottom > contentRect.bottom) {
        this.contentContainer.scrollTop += itemRect.bottom - contentRect.bottom;
      } else if (itemRect.top < contentRect.top) {
        this.contentContainer.scrollTop -= contentRect.top - itemRect.top;
      }
    }
  }

  /**
   * Select an item from the dropdown and insert it into the input
   */
  private async selectItem(itemId: string): Promise<void> {
    // Find the selected item
    let selectedItem: MentionContext | undefined;

    if (this.selectedCategory) {
      // Search in the specific category
      const categoryItems = this.contextItems.get(this.selectedCategory) || [];
      selectedItem = categoryItems.find(item => item.id === itemId);
    } else {
      // Search across all categories
      for (const [categoryId, items] of this.contextItems.entries()) {
        selectedItem = items.find(item => item.id === itemId);
        if (selectedItem) break;
      }
    }

    if (!selectedItem) return;

    // Replace the mention with the selected item
    const beforeMention = this.getInputValue().substring(
      0,
      this.currentMentionStart
    );
    const afterMention = this.getInputValue().substring(
      this.getSelectionStart()
    );

    // Format: @{item name} - replace spaces with non-breaking spaces for valid mention syntax
    const displayName = selectedItem.name.replace(/\s+/g, '_');
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
      let contextWithContent = { ...selectedItem };

      // Snippets already have their content loaded, so no need to fetch it separately
      this.onContextSelected(contextWithContent);
    }
  }

  /**
   * Update search placeholder based on current view
   */
  private updateSearchPlaceholder(): void {
    if (this.currentView === 'categories') {
      this.searchInput.placeholder = 'Search all items...';
    } else if (this.selectedCategory) {
      const categoryName =
        this.categories.find(cat => cat.id === this.selectedCategory)?.name ||
        'items';
      this.searchInput.placeholder = `Search ${categoryName.toLowerCase()}...`;
    }
  }

  /**
   * Show the dropdown
   */
  async showDropdown() {
    this.isVisible = true;
    this.currentView = 'categories';
    this.selectedCategory = null;
    this.selectedIndex = 0;
    this.dropdownElement.classList.add('visible');

    // Clear and setup search input for categories view
    this.searchInput.value = '';
    this.searchText = '';
    this.updateSearchPlaceholder();

    // Get contexts from cache (this will load them if not available)
    try {
      const cachedContexts = await this.contextCacheService.getContexts();

      // Update context items with cached data
      this.contextItems = cachedContexts;

      console.log(
        '[ChatContextMenu] Using cached contexts:',
        Array.from(this.contextItems.entries()).map(
          ([key, items]) => `${key}: ${items.length} items`
        )
      );
    } catch (error) {
      console.warn(
        '[ChatContextMenu] Failed to get cached contexts, falling back to direct loading:',
        error
      );

      // Fallback: Load contexts directly if cache fails
      const snippetContexts = await this.contextLoaders.loadSnippets();
      const variableContexts = await this.contextLoaders.loadVariables();
      const datasetContexts = await this.contextLoaders.loadDatasets();
      const cellContexts = await this.contextLoaders.loadCells();

      this.contextItems.set('snippets', snippetContexts);
      this.contextItems.set('data', datasetContexts);
      this.contextItems.set('variables', variableContexts);
      this.contextItems.set('cells', cellContexts);
    }
    // Update context items

    this.positionDropdown();
    this.renderDropdown('');

    // Focus the search input for immediate typing
    setTimeout(() => this.searchInput.focus(), 0);
  }

  /**
   * Hide the dropdown
   */
  hideDropdown(): void {
    this.isVisible = false;
    this.dropdownElement.classList.remove('visible');
    this.currentMentionStart = -1;
    this.currentMentionText = '';
    this.currentView = 'categories';
    this.selectedCategory = null;
  }

  /**
   * Handle keydown events for navigation and selection
   */
  private handleKeyDown = (event: KeyboardEvent): void => {
    if (!this.isVisible) return;

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
    const items = this.contentContainer.querySelectorAll(
      '.sage-ai-mention-item, .sage-ai-mention-subcategory'
    );

    if (items.length === 0) return;

    if (direction === 'down') {
      this.selectedIndex = (this.selectedIndex + 1) % items.length;
    } else {
      this.selectedIndex =
        this.selectedIndex <= 0 ? items.length - 1 : this.selectedIndex - 1;
    }

    this.highlightItem(this.selectedIndex);
  }

  /**
   * Select the currently highlighted item
   */
  private selectCurrentItem(): void {
    const items = this.dropdownElement.querySelectorAll(
      '.sage-ai-mention-item, .sage-ai-mention-subcategory'
    );

    if (
      items.length === 0 ||
      this.selectedIndex < 0 ||
      this.selectedIndex >= items.length
    ) {
      return;
    }

    const selectedElement = items[this.selectedIndex] as HTMLElement;

    // Handle category selection
    if (selectedElement.classList.contains('sage-ai-mention-category-main')) {
      const categoryId = selectedElement.getAttribute('data-category');
      if (categoryId) {
        this.selectedCategory = categoryId;
        this.currentView = 'items';
        this.selectedIndex = 0;
        // Clear search when entering a category
        this.searchInput.value = '';
        this.searchText = '';
        this.updateSearchPlaceholder();
        this.renderDropdown(this.searchText);
        this.positionDropdown();
        // Focus search input
        setTimeout(() => this.searchInput.focus(), 0);
      }
      return;
    }

    // Handle item selection
    if (selectedElement.classList.contains('sage-ai-mention-subcategory')) {
      const itemId = selectedElement.getAttribute('data-id');
      const categoryId = selectedElement.getAttribute('data-category');

      if (itemId) {
        // If we're selecting from the matching items section and have a category
        if (this.currentView === 'categories' && categoryId) {
          this.selectedCategory = categoryId;
        }

        this.selectItem(itemId);
      }
    }
  }

  /**
   * Trigger selection of the currently highlighted item (public method)
   */
  public selectHighlightedItem(): void {
    this.selectCurrentItem();
  }

  /**
   * Check if dropdown is visible (public method)
   */
  public getIsVisible(): boolean {
    return this.isVisible;
  }
}
