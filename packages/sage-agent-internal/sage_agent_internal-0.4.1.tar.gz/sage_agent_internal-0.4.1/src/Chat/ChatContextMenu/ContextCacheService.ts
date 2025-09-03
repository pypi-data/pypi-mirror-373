/**
 * Service for asynchronously loading and caching context items
 */
import { AppStateService } from '../../AppState';
import { ChatContextLoaders, MentionContext } from './ChatContextLoaders';

export class ContextCacheService {
  private static instance: ContextCacheService | null = null;
  private contextLoaders: ChatContextLoaders | null = null;
  private isInitialized = false;
  private loadingPromise: Promise<void> | null = null;

  private constructor() {}

  public static getInstance(): ContextCacheService {
    if (!ContextCacheService.instance) {
      ContextCacheService.instance = new ContextCacheService();
    }
    return ContextCacheService.instance;
  }

  /**
   * Initialize the context cache service
   */
  public async initialize(): Promise<void> {
    if (this.isInitialized) {
      return;
    }

    try {
      const contentManager = AppStateService.getContentManager();
      const toolService = AppStateService.getToolService();

      this.contextLoaders = new ChatContextLoaders(contentManager, toolService);
      this.isInitialized = true;

      console.log('[ContextCacheService] Initialized successfully');
    } catch (error) {
      console.warn('[ContextCacheService] Failed to initialize:', error);
      // Don't throw - we want the app to continue working even if context caching fails
    }
  }

  /**
   * Load all contexts asynchronously and cache them
   */
  public async loadAllContexts(): Promise<void> {
    // If already loading, return the existing promise
    if (this.loadingPromise) {
      return this.loadingPromise;
    }

    // If not initialized, try to initialize first
    if (!this.isInitialized) {
      await this.initialize();
    }

    if (!this.contextLoaders) {
      console.warn(
        '[ContextCacheService] Cannot load contexts - not properly initialized'
      );
      return;
    }

    // Set loading state
    AppStateService.setContextLoading(true);

    this.loadingPromise = this.performContextLoading();

    try {
      await this.loadingPromise;
    } finally {
      this.loadingPromise = null;
    }
  }

  /**
   * Perform the actual context loading
   */
  private async performContextLoading(): Promise<void> {
    if (!this.contextLoaders) return;

    console.log('[ContextCacheService] Starting async context loading...');

    const contextItems = new Map<string, MentionContext[]>();

    // Load all context types in parallel for better performance
    const [templateContexts, datasetContexts, variableContexts, cellContexts] =
      await Promise.allSettled([
        this.contextLoaders.loadSnippets(),
        this.contextLoaders.loadDatasets(),
        this.contextLoaders.loadVariables(),
        this.contextLoaders.loadCells()
      ]);

    // Process results and handle any failures gracefully
    if (templateContexts.status === 'fulfilled') {
      contextItems.set('snippets', templateContexts.value);
    } else {
      console.warn(
        '[ContextCacheService] Failed to load template contexts:',
        templateContexts.reason
      );
      contextItems.set('snippets', []);
    }

    if (datasetContexts.status === 'fulfilled') {
      contextItems.set('data', datasetContexts.value);
    } else {
      console.warn(
        '[ContextCacheService] Failed to load dataset contexts:',
        datasetContexts.reason
      );
      contextItems.set('data', []);
    }

    if (variableContexts.status === 'fulfilled') {
      contextItems.set('variables', variableContexts.value);
    } else {
      console.warn(
        '[ContextCacheService] Failed to load variable contexts:',
        variableContexts.reason
      );
      contextItems.set('variables', []);
    }

    if (cellContexts.status === 'fulfilled') {
      contextItems.set('cells', cellContexts.value);
    } else {
      console.warn(
        '[ContextCacheService] Failed to load cell contexts:',
        cellContexts.reason
      );
      contextItems.set('cells', []);
    }

    // Update the cache in AppState
    AppStateService.setCachedContexts(contextItems);

    // Also update the global context service to trigger UI refreshes
    const flatContexts = new Map<string, MentionContext>();
    contextItems.forEach((contexts, category) => {
      contexts.forEach(context => {
        flatContexts.set(context.id, context);
      });
    });

    // Import and update the context service
    const { ContextService } = await import('../../Services/ContextService');
    const contextService = ContextService.getInstance();
    contextService.setContextItems(flatContexts);

    console.log(
      '[ContextCacheService] Context loading completed:',
      Array.from(contextItems.entries()).map(
        ([key, items]) => `${key}: ${items.length} items`
      )
    );
  }

  /**
   * Refresh contexts if they're stale
   */
  public async refreshIfStale(): Promise<void> {
    if (
      AppStateService.shouldRefreshContexts() &&
      !AppStateService.isContextLoading()
    ) {
      console.log('[ContextCacheService] Contexts are stale, refreshing...');
      await this.loadAllContexts();
    }
  }

  /**
   * Force refresh all contexts
   */
  public async forceRefresh(): Promise<void> {
    console.log('[ContextCacheService] Force refreshing contexts...');
    await this.loadAllContexts();
  }

  /**
   * Load a specific context category
   */
  public async loadContextCategory(category: string): Promise<void> {
    if (!this.contextLoaders) {
      await this.initialize();
      if (!this.contextLoaders) return;
    }

    try {
      let contexts: MentionContext[] = [];

      switch (category) {
        case 'snippets':
          contexts = await this.contextLoaders.loadSnippets();
          break;
        case 'data':
          contexts = await this.contextLoaders.loadDatasets();
          break;
        case 'variables':
          contexts = await this.contextLoaders.loadVariables();
          break;
        case 'cells':
          contexts = await this.contextLoaders.loadCells();
          break;
        default:
          console.warn(
            `[ContextCacheService] Unknown context category: ${category}`
          );
          return;
      }

      AppStateService.updateContextCategory(category, contexts);
      
      // Also update the global context service to trigger UI refreshes
      const { ContextService } = await import('../../Services/ContextService');
      const contextService = ContextService.getInstance();
      
      // Add these contexts to the global context service
      contexts.forEach(context => {
        contextService.addContextItem(context);
      });
      
      console.log(
        `[ContextCacheService] Updated ${category} contexts: ${contexts.length} items`
      );
    } catch (error) {
      console.warn(
        `[ContextCacheService] Failed to load ${category} contexts:`,
        error
      );
    }
  }

  /**
   * Get cached contexts or load them if not available
   */
  public async getContexts(): Promise<Map<string, MentionContext[]>> {
    const cachedContexts = AppStateService.getCachedContexts();

    // If we have cached contexts and they're not too old, return them
    if (cachedContexts.size > 0 && !AppStateService.shouldRefreshContexts()) {
      return cachedContexts;
    }

    // If contexts are loading, wait for them
    if (AppStateService.isContextLoading() && this.loadingPromise) {
      await this.loadingPromise;
      return AppStateService.getCachedContexts();
    }

    // Load contexts
    await this.loadAllContexts();
    return AppStateService.getCachedContexts();
  }

  /**
   * Subscribe to notebook changes to refresh contexts
   */
  public subscribeToNotebookChanges(): void {
    AppStateService.onNotebookChanged().subscribe(({ newNotebookId }) => {
      if (newNotebookId) {
        console.log(
          '[ContextCacheService] Notebook changed, refreshing contexts...'
        );
        // Use setTimeout to avoid blocking the notebook switch
        setTimeout(() => {
          this.loadAllContexts().catch(error => {
            console.warn(
              '[ContextCacheService] Failed to refresh contexts on notebook change:',
              error
            );
          });
        }, 100);
      }
    });
  }

  /**
   * Refresh variable contexts after code execution
   * This should be called when cells are executed to update variable contexts
   */
  public refreshVariablesAfterExecution(): void {
    // Debounce variable refreshing to avoid too many calls
    if (this.variableRefreshTimeout) {
      clearTimeout(this.variableRefreshTimeout);
    }

    this.variableRefreshTimeout = setTimeout(() => {
      console.log(
        '[ContextCacheService] Refreshing variables after execution...'
      );
      this.loadContextCategory('variables').catch(error => {
        console.warn(
          '[ContextCacheService] Failed to refresh variables after execution:',
          error
        );
      });
    }, 1000); // Wait 1 second after execution to refresh variables
  }

  private variableRefreshTimeout: NodeJS.Timeout | null = null;
}
