import { BehaviorSubject, Observable, Subject } from 'rxjs';
import { INotebookTracker, NotebookPanel } from '@jupyterlab/notebook';
import { Contents } from '@jupyterlab/services';
import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { ToolService } from './Services/ToolService';
import { NotebookTools } from './Notebook/NotebookTools';
import { NotebookContextManager } from './Notebook/NotebookContextManager';
import { PlanStateDisplay } from './Components/PlanStateDisplay';
import { WaitingUserReplyBoxManager } from './Notebook/WaitingUserReplyBoxManager';
import { ActionHistory } from './Chat/ActionHistory';
import { NotebookDiffManager } from './Notebook/NotebookDiffManager';
import { CellTrackingService } from './CellTrackingService';
import { TrackingIDUtility } from './TrackingIDUtility';
import { ContextCellHighlighter } from './Chat/ChatContextMenu/ContextCellHighlighter';
import { NotebookChatContainer } from './Notebook/NotebookChatContainer';
import { ListModel } from '@jupyterlab/extensionmanager';
import { IChatService } from './Services/IChatService';
import { IConfig } from './Config/ConfigService';
import { ServiceManager } from '@jupyterlab/services';
import { StateDBCachingService, STATE_DB_KEYS } from './utils/stateDBCaching';
import { MentionContext } from './Chat/ChatContextMenu/ChatContextLoaders';
import { DiffNavigationWidget } from './Components/DiffNavigationWidget';
import { v4 as uuidv4 } from 'uuid';
/**
 * Interface for a Snippet stored in AppState
 */
export interface ISnippet {
  id: string;
  title: string;
  description: string;
  content: string;
  createdAt: string;
  updatedAt: string;
}

interface AppState {
  // Core services
  toolService: ToolService | null;
  notebookTracker: INotebookTracker | null;
  notebookTools: NotebookTools | null;
  notebookContextManager: NotebookContextManager | null;
  contentManager: Contents.IManager | null;
  settingsRegistry: ISettingRegistry | null;
  chatService: IChatService | null;
  config: IConfig | null;
  serviceManager: ServiceManager.IManager | null;

  // Extension manager
  extensions: ListModel | null;

  // Managers
  planStateDisplay: PlanStateDisplay | null;
  waitingUserReplyBoxManager: WaitingUserReplyBoxManager | null;
  notebookDiffManager: NotebookDiffManager | null;

  // Additional services
  actionHistory: ActionHistory | null;
  cellTrackingService: CellTrackingService | null;
  trackingIDUtility: TrackingIDUtility | null;
  contextCellHighlighter: ContextCellHighlighter | null;

  // UI Containers
  chatContainer: NotebookChatContainer | null;
  diffNavigationWidget: DiffNavigationWidget | null;

  // Application state
  currentNotebookId: string | null;
  currentNotebook: NotebookPanel | null;
  isInitialized: boolean;

  // Context cache for async loading
  contextCache: Map<string, MentionContext[]>;
  contextCacheTimestamp: number;
  isContextLoading: boolean;

  // Snippets
  snippets: ISnippet[];
  insertedSnippets: string[]; // Array of snippet IDs that have been inserted

  // Tool call limit
  maxToolCallLimit: number | null;

  // Settings
  settings: {
    theme: string;
    tokenMode: boolean;
    tabAutocompleteEnabled: boolean;
    claudeApiKey: string;
    claudeModelId: string;
    claudeModelUrl: string;
    databaseUrl: string;
  };
}

const initialState: AppState = {
  // Core services
  toolService: null,
  notebookTracker: null,
  notebookTools: null,
  notebookContextManager: null,
  contentManager: null,
  settingsRegistry: null,
  chatService: null,
  config: null,
  serviceManager: null,

  // Extension manager
  extensions: null,

  // Managers
  planStateDisplay: null,
  waitingUserReplyBoxManager: null,
  notebookDiffManager: null,

  // Additional services
  actionHistory: null,
  cellTrackingService: null,
  trackingIDUtility: null,
  contextCellHighlighter: null,

  // UI Containers
  chatContainer: null,
  diffNavigationWidget: null,

  // Application state
  currentNotebookId: null,
  currentNotebook: null,
  isInitialized: false,

  // Context cache for async loading
  contextCache: new Map(),
  contextCacheTimestamp: 0,
  isContextLoading: false,

  // Snippets
  snippets: [],
  insertedSnippets: [],

  // Tool call limit
  maxToolCallLimit: null,

  // Settings
  settings: {
    theme: 'light',
    tokenMode: false,
    tabAutocompleteEnabled: false,
    claudeApiKey: '',
    claudeModelId: 'claude-3-7-sonnet-20250219',
    claudeModelUrl: 'https://sage.alpinex.ai:8760',
    databaseUrl: ''
  }
};

const state$ = new BehaviorSubject<AppState>(initialState);

// Events for notebook changes
const notebookChanged$ = new Subject<{
  oldNotebookId: string | null;
  newNotebookId: string | null;
}>();
const notebookRenamed$ = new Subject<{
  oldNotebookId: string;
  newNotebookId: string;
}>();

export const AppStateService = {
  /**
   * Get the current application state
   */
  getState: () => state$.getValue(),

  /**
   * Update the application state with partial values
   */
  setState: (partial: Partial<AppState>) =>
    state$.next({ ...state$.getValue(), ...partial }),

  /**
   * Subscribe to state changes
   */
  changes: state$.asObservable(),

  /**
   * Initialize core services
   */
  initializeCoreServices: (
    toolService: ToolService,
    notebookTracker: INotebookTracker,
    notebookTools: NotebookTools,
    notebookContextManager: NotebookContextManager,
    contentManager: Contents.IManager,
    settingsRegistry?: ISettingRegistry | null
  ) => {
    AppStateService.setState({
      toolService,
      notebookTracker,
      notebookTools,
      notebookContextManager,
      contentManager,
      settingsRegistry: settingsRegistry || null
    });
  },

  /**
   * Initialize managers
   */
  initializeManagers: (
    planStateDisplay: PlanStateDisplay,
    waitingUserReplyBoxManager: WaitingUserReplyBoxManager,
    notebookDiffManager?: NotebookDiffManager
  ) => {
    AppStateService.setState({
      planStateDisplay,
      waitingUserReplyBoxManager,
      notebookDiffManager
    });
  },

  /**
   * Initialize additional services
   */
  initializeAdditionalServices: (
    actionHistory: ActionHistory,
    cellTrackingService: CellTrackingService,
    trackingIDUtility: TrackingIDUtility,
    contextCellHighlighter: ContextCellHighlighter
  ) => {
    AppStateService.setState({
      actionHistory,
      cellTrackingService,
      trackingIDUtility,
      contextCellHighlighter
    });
  },

  /**
   * Mark the application as initialized
   */
  markAsInitialized: () => {
    AppStateService.setState({ isInitialized: true });
  },

  /**
   * Get the current notebook ID
   */
  getCurrentNotebookId: (): string | null => {
    return AppStateService.getState().currentNotebookId;
  },

  /**
   * Get the current notebook
   */
  getCurrentNotebook: (): NotebookPanel | null => {
    return AppStateService.getState().currentNotebook;
  },

  /**
   * Set the current notebook and its ID
   */
  setCurrentNotebook: (
    notebook: NotebookPanel | null,
    notebookId?: string | null
  ) => {
    const currentState = AppStateService.getState();
    const oldNotebookId = currentState.currentNotebookId;
    const newNotebookId = notebookId || (notebook ? 'unknown' : null);

    if (oldNotebookId !== newNotebookId) {
      AppStateService.setState({
        currentNotebook: notebook,
        currentNotebookId: newNotebookId
      });
      // Emit notebook change event
      notebookChanged$.next({ oldNotebookId, newNotebookId });
    } else {
      // Just update the notebook reference if ID is the same
      AppStateService.setState({ currentNotebook: notebook });
    }
  },

  /**
   * Update the current notebook ID
   */
  setCurrentNotebookId: (notebookId: string | null) => {
    const currentState = AppStateService.getState();
    const oldNotebookId = currentState.currentNotebookId;

    if (oldNotebookId !== notebookId) {
      AppStateService.setState({
        currentNotebookId: notebookId,
        currentNotebook: null // Clear notebook reference when only ID is set
      });
      // Emit notebook change event
      notebookChanged$.next({ oldNotebookId, newNotebookId: notebookId });
    }
  },

  /**
   * Update notebook ID when a notebook is renamed
   */
  updateNotebookId: (oldNotebookId: string, newNotebookId: string) => {
    const currentState = AppStateService.getState();

    // Update current notebook ID if it matches the old one
    if (currentState.currentNotebookId === oldNotebookId) {
      AppStateService.setState({
        currentNotebookId: newNotebookId,
        currentNotebook: null // Clear notebook reference during rename
      });
    }

    // Emit notebook rename event
    notebookRenamed$.next({ oldNotebookId, newNotebookId });
  },

  /**
   * Subscribe to notebook change events
   */
  onNotebookChanged: (): Observable<{
    oldNotebookId: string | null;
    newNotebookId: string | null;
  }> => {
    return notebookChanged$.asObservable();
  },

  /**
   * Subscribe to notebook rename events
   */
  onNotebookRenamed: (): Observable<{
    oldNotebookId: string;
    newNotebookId: string;
  }> => {
    return notebookRenamed$.asObservable();
  },

  /**
   * Update settings
   */
  updateSettings: (settings: Partial<AppState['settings']>) => {
    const currentState = AppStateService.getState();
    AppStateService.setState({
      settings: { ...currentState.settings, ...settings }
    });
  },

  /**
   * Update Claude settings specifically
   */
  updateClaudeSettings: (settings: {
    claudeApiKey?: string;
    claudeModelId?: string;
    claudeModelUrl?: string;
    databaseUrl?: string;
    tabAutocompleteEnabled?: boolean;
  }) => {
    const currentState = AppStateService.getState();
    AppStateService.setState({
      settings: { ...currentState.settings, ...settings }
    });
  },

  /**
   * Get Claude settings
   */
  getClaudeSettings: (): {
    claudeApiKey: string;
    claudeModelId: string;
    claudeModelUrl: string;
    databaseUrl: string;
    tabAutocompleteEnabled: boolean;
  } => {
    const { settings } = AppStateService.getState();
    return {
      claudeApiKey: settings.claudeApiKey,
      claudeModelId: settings.claudeModelId,
      claudeModelUrl: settings.claudeModelUrl,
      databaseUrl: settings.databaseUrl,
      tabAutocompleteEnabled: settings.tabAutocompleteEnabled
    };
  },

  /**
   * Get Claude API key
   */
  getClaudeApiKey: (): string => {
    return AppStateService.getState().settings.claudeApiKey;
  },

  /**
   * Get Claude model URL
   */
  getClaudeModelUrl: (): string => {
    return AppStateService.getState().settings.claudeModelUrl;
  },

  /**
   * Get Claude model ID
   */
  getClaudeModelId: (): string => {
    return AppStateService.getState().settings.claudeModelId;
  },

  /**
   * Set the extensions manager
   */
  setExtensions: (extensions: ListModel) => {
    AppStateService.setState({ extensions });
  },

  /**
   * Get the extensions manager
   */
  getExtensions: (): ListModel | null => {
    return AppStateService.getState().extensions;
  },

  /**
   * Set the settings registry
   */
  setSettingsRegistry: (settingsRegistry: ISettingRegistry | null) => {
    AppStateService.setState({ settingsRegistry });
  },

  /**
   * Get the settings registry
   */
  getSettingsRegistry: (): ISettingRegistry | null => {
    return AppStateService.getState().settingsRegistry;
  },

  /**
   * Set the service manager
   */
  setServiceManager: (serviceManager: ServiceManager.IManager) => {
    AppStateService.setState({ serviceManager });
  },

  /**
   * Get the service manager
   */
  getServiceManager: (): ServiceManager.IManager | null => {
    return AppStateService.getState().serviceManager;
  },

  /**
   * Get a specific service safely
   */
  getToolService: (): ToolService => {
    const toolService = AppStateService.getState().toolService;
    if (!toolService) {
      throw new Error('ToolService not initialized in AppState');
    }
    return toolService;
  },

  getNotebookTracker: (): INotebookTracker => {
    const notebookTracker = AppStateService.getState().notebookTracker;
    if (!notebookTracker) {
      throw new Error('NotebookTracker not initialized in AppState');
    }
    return notebookTracker;
  },

  getNotebookTools: (): NotebookTools => {
    const notebookTools = AppStateService.getState().notebookTools;
    if (!notebookTools) {
      throw new Error('NotebookTools not initialized in AppState');
    }
    return notebookTools;
  },

  getNotebookContextManager: (): NotebookContextManager => {
    const notebookContextManager =
      AppStateService.getState().notebookContextManager;
    if (!notebookContextManager) {
      throw new Error('NotebookContextManager not initialized in AppState');
    }
    return notebookContextManager;
  },

  getContentManager: (): Contents.IManager => {
    const contentManager = AppStateService.getState().contentManager;
    if (!contentManager) {
      throw new Error('ContentManager not initialized in AppState');
    }
    return contentManager;
  },

  getPlanStateDisplay: (): PlanStateDisplay => {
    const planStateDisplay = AppStateService.getState().planStateDisplay;
    if (!planStateDisplay) {
      throw new Error('PlanStateDisplay not initialized in AppState');
    }
    return planStateDisplay;
  },

  getWaitingUserReplyBoxManager: (): WaitingUserReplyBoxManager => {
    const waitingUserReplyBoxManager =
      AppStateService.getState().waitingUserReplyBoxManager;
    if (!waitingUserReplyBoxManager) {
      throw new Error('WaitingUserReplyBoxManager not initialized in AppState');
    }
    return waitingUserReplyBoxManager;
  },

  getActionHistory: (): ActionHistory => {
    const actionHistory = AppStateService.getState().actionHistory;
    if (!actionHistory) {
      throw new Error('ActionHistory not initialized in AppState');
    }
    return actionHistory;
  },

  getCellTrackingService: (): CellTrackingService => {
    const cellTrackingService = AppStateService.getState().cellTrackingService;
    if (!cellTrackingService) {
      throw new Error('CellTrackingService not initialized in AppState');
    }
    return cellTrackingService;
  },

  getNotebookDiffManager: (): NotebookDiffManager => {
    const notebookDiffManager = AppStateService.getState().notebookDiffManager;
    if (!notebookDiffManager) {
      throw new Error('NotebookDiffManager not initialized in AppState');
    }
    return notebookDiffManager;
  },

  getTrackingIDUtility: (): TrackingIDUtility => {
    const trackingIDUtility = AppStateService.getState().trackingIDUtility;
    if (!trackingIDUtility) {
      throw new Error('TrackingIDUtility not initialized in AppState');
    }
    return trackingIDUtility;
  },

  getContextCellHighlighter: (): ContextCellHighlighter => {
    const contextCellHighlighter =
      AppStateService.getState().contextCellHighlighter;
    if (!contextCellHighlighter) {
      throw new Error('ContextCellHighlighter not initialized in AppState');
    }
    return contextCellHighlighter;
  },

  getChatContainer: (): NotebookChatContainer => {
    const chatContainer = AppStateService.getState().chatContainer;
    if (!chatContainer) {
      throw new Error('ChatContainer not initialized in AppState');
    }
    return chatContainer;
  },

  /**
   * Set the chat container
   */
  setChatContainer: (chatContainer: NotebookChatContainer) => {
    AppStateService.setState({ chatContainer });
  },

  /**
   * Get the chat container safely (returns null if not initialized)
   */
  getChatContainerSafe: (): NotebookChatContainer | null => {
    return AppStateService.getState().chatContainer;
  },

  /**
   * Set the diff navigation widget
   */
  setDiffNavigationWidget: (diffNavigationWidget: DiffNavigationWidget) => {
    AppStateService.setState({ diffNavigationWidget });
  },

  /**
   * Get the diff navigation widget
   */
  getDiffNavigationWidget: (): DiffNavigationWidget => {
    const diffNavigationWidget =
      AppStateService.getState().diffNavigationWidget;
    if (!diffNavigationWidget) {
      throw new Error('DiffNavigationWidget not initialized in AppState');
    }
    return diffNavigationWidget;
  },

  /**
   * Get the diff navigation widget safely (returns null if not initialized)
   */
  getDiffNavigationWidgetSafe: (): DiffNavigationWidget | null => {
    return AppStateService.getState().diffNavigationWidget;
  },

  /**
   * Set the chat service
   */
  setChatService: (chatService: IChatService) => {
    AppStateService.setState({ chatService });
  },

  getChatService: (): IChatService => {
    const chatService = AppStateService.getState().chatService;
    if (!chatService) {
      throw new Error('ChatService not initialized in AppState');
    }
    return chatService;
  },

  setConfig: (config: IConfig) => {
    AppStateService.setState({ config });
  },

  getConfig: (): IConfig => {
    const config = AppStateService.getState().config;
    if (!config) {
      throw new Error('Config not initialized in AppState');
    }
    return config;
  },

  /**
   * Update chat container with new notebook ID
   */
  updateChatContainerNotebookId: (
    oldNotebookId: string,
    newNotebookId: string
  ) => {
    const chatContainer = AppStateService.getState().chatContainer;
    if (chatContainer && !chatContainer.isDisposed) {
      chatContainer.updateNotebookId(oldNotebookId, newNotebookId);
    }
  },

  /**
   * Get all snippets
   */
  getSnippets: (): ISnippet[] => {
    return AppStateService.getState().snippets;
  },

  /**
   * Set snippets and persist to StateDB
   */
  setSnippets: async (snippets: ISnippet[]) => {
    AppStateService.setState({ snippets });
    try {
      await StateDBCachingService.setObjectValue(
        STATE_DB_KEYS.SNIPPETS,
        snippets
      );
    } catch (error) {
      console.error(
        '[AppStateService] Failed to persist snippets to StateDB:',
        error
      );
    }
  },

  /**
   * Add a snippet and persist to StateDB
   */
  addSnippet: async (snippet: ISnippet) => {
    const currentSnippets = AppStateService.getState().snippets;
    const newSnippets = [...currentSnippets, snippet];
    AppStateService.setState({ snippets: newSnippets });
    try {
      await StateDBCachingService.setObjectValue(
        STATE_DB_KEYS.SNIPPETS,
        newSnippets
      );
    } catch (error) {
      console.error(
        '[AppStateService] Failed to persist snippets to StateDB:',
        error
      );
    }
  },

  /**
   * Update a snippet and persist to StateDB
   */
  updateSnippet: async (snippetId: string, updates: Partial<ISnippet>) => {
    console.log('[AppStateService] Updating snippet with ID:', snippetId);
    console.log('[AppStateService] Updates:', updates);

    const currentSnippets = AppStateService.getState().snippets;
    console.log(
      '[AppStateService] Current snippets count:',
      currentSnippets.length
    );

    const updatedSnippets = currentSnippets.map(snippet => {
      if (snippet.id === snippetId) {
        console.log(
          '[AppStateService] Found snippet to update:',
          snippet.title
        );
        return { ...snippet, ...updates };
      }
      return snippet;
    });

    console.log(
      '[AppStateService] Updated snippets count:',
      updatedSnippets.length
    );

    AppStateService.setState({ snippets: updatedSnippets });
    try {
      await StateDBCachingService.setObjectValue(
        STATE_DB_KEYS.SNIPPETS,
        updatedSnippets
      );
      console.log(
        '[AppStateService] Successfully persisted updated snippets to StateDB'
      );
    } catch (error) {
      console.error(
        '[AppStateService] Failed to persist snippets to StateDB:',
        error
      );
    }
  },

  /**
   * Remove a snippet and persist to StateDB
   */
  removeSnippet: async (snippetId: string) => {
    const currentSnippets = AppStateService.getState().snippets;
    const filteredSnippets = currentSnippets.filter(
      snippet => snippet.id !== snippetId
    );
    AppStateService.setState({ snippets: filteredSnippets });
    try {
      await StateDBCachingService.setObjectValue(
        STATE_DB_KEYS.SNIPPETS,
        filteredSnippets
      );
    } catch (error) {
      console.error(
        '[AppStateService] Failed to persist snippets to StateDB:',
        error
      );
    }
  },

  /**
   * Load snippets from StateDB with migration for unique IDs
   */
  loadSnippets: async (): Promise<void> => {
    try {
      const snippets = await StateDBCachingService.getObjectValue<ISnippet[]>(
        STATE_DB_KEYS.SNIPPETS,
        []
      );

      // Migrate snippets to ensure all have unique IDs
      const migratedSnippets =
        await AppStateService.migrateSnippetsForUniqueIds(snippets);

      AppStateService.setState({ snippets: migratedSnippets });
      console.log(
        '[AppStateService] Loaded',
        migratedSnippets.length,
        'snippets from StateDB'
      );
    } catch (error) {
      console.error(
        '[AppStateService] Failed to load snippets from StateDB:',
        error
      );
    }
  },

  /**
   * Migrate snippets to ensure all have unique IDs
   */
  migrateSnippetsForUniqueIds: async (
    snippets: ISnippet[]
  ): Promise<ISnippet[]> => {
    let needsUpdate = false;
    const usedIds = new Set<string>();

    console.log(
      '[AppStateService] Checking',
      snippets.length,
      'snippets for unique IDs'
    );

    const migratedSnippets = snippets.map((snippet, index) => {
      // Check if snippet has no ID, invalid ID, or duplicate ID
      const hasValidId =
        snippet.id &&
        typeof snippet.id === 'string' &&
        snippet.id.trim().length > 0;
      const isDuplicate = hasValidId && usedIds.has(snippet.id);

      if (!hasValidId || isDuplicate) {
        needsUpdate = true;
        const newId = AppStateService.generateSnippetId();
        usedIds.add(newId);
        console.log(
          `[AppStateService] Migrating snippet #${index} "${snippet.title}" with new ID: ${newId}` +
            (isDuplicate ? ' (duplicate ID)' : ' (missing/invalid ID)')
        );
        return {
          ...snippet,
          id: newId,
          updatedAt: new Date().toISOString()
        };
      }

      usedIds.add(snippet.id);
      return snippet;
    });

    // If any snippets were updated, save back to StateDB
    if (needsUpdate) {
      try {
        await StateDBCachingService.setObjectValue(
          STATE_DB_KEYS.SNIPPETS,
          migratedSnippets
        );
        console.log(
          '[AppStateService] Successfully migrated snippet IDs to StateDB'
        );
      } catch (error) {
        console.error(
          '[AppStateService] Failed to save migrated snippets:',
          error
        );
      }
    } else {
      console.log(
        '[AppStateService] All snippets already have valid unique IDs'
      );
    }

    return migratedSnippets;
  },

  /**
   * Generate a unique ID for a snippet
   */
  generateSnippetId: (): string => {
    return uuidv4();
  },

  /**
   * Load inserted snippets from StateDB
   */
  loadInsertedSnippets: async (): Promise<void> => {
    try {
      const insertedSnippets = await StateDBCachingService.getObjectValue<
        string[]
      >(STATE_DB_KEYS.INSERTED_SNIPPETS, []);

      AppStateService.setState({ insertedSnippets });
      console.log(
        '[AppStateService] Loaded',
        insertedSnippets.length,
        'inserted snippets from StateDB'
      );
    } catch (error) {
      console.error(
        '[AppStateService] Failed to load inserted snippets from StateDB:',
        error
      );
    }
  },

  /**
   * Save inserted snippets to StateDB
   */
  saveInsertedSnippets: async (): Promise<void> => {
    try {
      const currentState = AppStateService.getState();
      await StateDBCachingService.setObjectValue(
        STATE_DB_KEYS.INSERTED_SNIPPETS,
        currentState.insertedSnippets
      );
      console.log(
        '[AppStateService] Saved',
        currentState.insertedSnippets.length,
        'inserted snippets to StateDB'
      );
    } catch (error) {
      console.error(
        '[AppStateService] Failed to save inserted snippets to StateDB:',
        error
      );
    }
  },

  /**
   * Add a snippet ID to the inserted snippets list
   */
  addInsertedSnippet: async (snippetId: string): Promise<void> => {
    const currentState = AppStateService.getState();
    if (!currentState.insertedSnippets.includes(snippetId)) {
      const newInsertedSnippets = [...currentState.insertedSnippets, snippetId];
      AppStateService.setState({
        insertedSnippets: newInsertedSnippets
      });

      // Persist to StateDB
      try {
        await StateDBCachingService.setObjectValue(
          STATE_DB_KEYS.INSERTED_SNIPPETS,
          newInsertedSnippets
        );
        console.log(
          '[AppStateService] Added inserted snippet to StateDB:',
          snippetId
        );
      } catch (error) {
        console.error(
          '[AppStateService] Failed to save inserted snippet to StateDB:',
          error
        );
      }
    }
  },

  /**
   * Remove a snippet ID from the inserted snippets list
   */
  removeInsertedSnippet: async (snippetId: string): Promise<void> => {
    const currentState = AppStateService.getState();
    const newInsertedSnippets = currentState.insertedSnippets.filter(
      id => id !== snippetId
    );

    AppStateService.setState({
      insertedSnippets: newInsertedSnippets
    });

    // Persist to StateDB
    try {
      await StateDBCachingService.setObjectValue(
        STATE_DB_KEYS.INSERTED_SNIPPETS,
        newInsertedSnippets
      );
      console.log(
        '[AppStateService] Removed inserted snippet from StateDB:',
        snippetId
      );
    } catch (error) {
      console.error(
        '[AppStateService] Failed to remove inserted snippet from StateDB:',
        error
      );
    }
  },

  /**
   * Get all inserted snippets with their content
   */
  getInsertedSnippets: (): ISnippet[] => {
    const currentState = AppStateService.getState();
    return currentState.snippets.filter(snippet =>
      currentState.insertedSnippets.includes(snippet.id)
    );
  },

  /**
   * Check if a snippet is currently inserted
   */
  isSnippetInserted: (snippetId: string): boolean => {
    const currentState = AppStateService.getState();
    return currentState.insertedSnippets.includes(snippetId);
  },

  /**
   * Clear all inserted snippets
   */
  clearInsertedSnippets: async (): Promise<void> => {
    AppStateService.setState({ insertedSnippets: [] });

    // Persist to StateDB
    try {
      await StateDBCachingService.setObjectValue(
        STATE_DB_KEYS.INSERTED_SNIPPETS,
        []
      );
      console.log(
        '[AppStateService] Cleared all inserted snippets from StateDB'
      );
    } catch (error) {
      console.error(
        '[AppStateService] Failed to clear inserted snippets from StateDB:',
        error
      );
    }
  },

  /**
   * Switch chat container to a notebook
   */
  switchChatContainerToNotebook: (notebookId: string) => {
    const chatContainer = AppStateService.getState().chatContainer;
    if (chatContainer && !chatContainer.isDisposed) {
      chatContainer.switchToNotebook(notebookId);
    }
  },

  /**
   * Find a notebook by its unique sage_ai.unique_id
   * @param uniqueId The unique ID to search for
   * @returns The notebook widget if found, null otherwise
   */
  getNotebookByID: async (uniqueId: string): Promise<NotebookPanel | null> => {
    const notebookTracker = AppStateService.getState().notebookTracker;
    const contentManager = AppStateService.getState().contentManager;

    if (!notebookTracker || !contentManager) {
      console.warn('NotebookTracker or ContentManager not initialized');
      return null;
    }

    // Convert forEach to a proper async iteration
    const notebooks: any[] = [];
    notebookTracker.forEach(notebook => {
      notebooks.push(notebook);
    });

    for (const notebook of notebooks) {
      try {
        const nbFile = await contentManager.get(notebook.context.path);
        if (nbFile) {
          const nbMetadata = nbFile.content.metadata || {};
          if (nbMetadata.sage_ai && nbMetadata.sage_ai.unique_id === uniqueId) {
            return notebook;
          }
        }
      } catch (error) {
        console.warn(
          `Error checking notebook ${notebook.context.path}:`,
          error
        );
      }
    }

    return notebookTracker.currentWidget;
  },

  /**
   * Get cached contexts
   */
  getCachedContexts: (): Map<string, MentionContext[]> => {
    return AppStateService.getState().contextCache;
  },

  /**
   * Set cached contexts
   */
  setCachedContexts: (contexts: Map<string, MentionContext[]>) => {
    AppStateService.setState({
      contextCache: contexts,
      contextCacheTimestamp: Date.now(),
      isContextLoading: false
    });
  },

  /**
   * Update a specific context category
   */
  updateContextCategory: (category: string, contexts: MentionContext[]) => {
    const currentCache = AppStateService.getState().contextCache;
    const newCache = new Map(currentCache);
    newCache.set(category, contexts);
    AppStateService.setState({
      contextCache: newCache,
      contextCacheTimestamp: Date.now()
    });
  },

  /**
   * Check if contexts are being loaded
   */
  isContextLoading: (): boolean => {
    return AppStateService.getState().isContextLoading;
  },

  /**
   * Set context loading state
   */
  setContextLoading: (loading: boolean) => {
    AppStateService.setState({ isContextLoading: loading });
  },

  /**
   * Get the age of cached contexts in milliseconds
   */
  getContextCacheAge: (): number => {
    return Date.now() - AppStateService.getState().contextCacheTimestamp;
  },

  /**
   * Check if contexts need refreshing (older than 30 seconds)
   */
  shouldRefreshContexts: (): boolean => {
    const cacheAge = AppStateService.getContextCacheAge();
    return cacheAge > 30000; // 30 seconds
  },

  /**
   * Set the maximum tool call limit
   */
  setMaxToolCallLimit: (limit: number | null) => {
    AppStateService.setState({ maxToolCallLimit: limit });
  },

  /**
   * Get the maximum tool call limit
   */
  getMaxToolCallLimit: (): number | null => {
    return AppStateService.getState().maxToolCallLimit;
  }
};

// Example usage:

// Read from state
// const { toolService, settings } = AppStateService.getState();

// Update state
// AppStateService.setState({ currentNotebookPath: '/path/to/notebook.ipynb' });

// Subscribe to changes
// AppStateService.changes.subscribe(state => {
//   console.log('New state!', state);
// });

// Use convenience methods
// const toolService = AppStateService.getToolService();
// AppStateService.updateSettings({ theme: 'dark' });
