import { IChatMessage } from '../types';
import { ChatBoxWidget } from '../Components/chatbox';
import { MentionContext } from './ChatContextMenu/ChatContextMenu';
import { CachingService, SETTING_KEYS } from '../utils/caching';
import { STATE_DB_KEYS, StateDBCachingService } from '../utils/stateDBCaching';
import { AppStateService } from '../AppState';

export interface IChatThread {
  id: string;
  name: string;
  messages: IChatMessage[];
  lastUpdated: number;
  contexts: Map<string, MentionContext>;
  message_timestamps: Map<string, number>;
  continueButtonShown?: boolean; // Track if continue button has been shown in this thread
}

export interface NotebookChatState {
  chatbox: ChatBoxWidget | null;
  isVisible: boolean;
}

/**
 * Manager for persisting chat histories across notebook sessions
 */
export class ChatHistoryManager {
  // Map of notebook IDs to their chat threads
  private notebookChats: Map<string, IChatThread[]> = new Map();
  // Current active notebook ID
  private currentNotebookId: string | null = null;
  // Current active chat thread ID
  private currentThreadId: string | null = null;
  // Storage key prefix
  private readonly STORAGE_KEY_PREFIX = 'sage-ai-chat-history-';
  // Map of notebook IDs to their chatbox instances
  private notebookChatboxes: Map<string, NotebookChatState> = new Map();

  constructor() {
    this.loadFromStorage();

    // Subscribe to notebook change events from AppStateService
    AppStateService.onNotebookChanged().subscribe(
      ({ oldNotebookId, newNotebookId }) => {
        if (newNotebookId) {
          this.setCurrentNotebook(newNotebookId);
        }
      }
    );

    // AppStateService.onNotebookRenamed().subscribe(
    //   ({ oldNotebookId, newNotebookId }) => {
    //     this.updateNotebookId(oldNotebookId, newNotebookId);
    //   }
    // );
  }

  public updateNotebookId(oldId: string, newId: string): void {
    this.currentNotebookId = newId;
    const threads = this.notebookChats.get(oldId) || [];
    this.notebookChats.set(newId, threads);
    this.notebookChats.delete(oldId);

    // Also update chatbox mapping
    const chatState = this.notebookChatboxes.get(oldId);
    if (chatState) {
      this.notebookChatboxes.set(newId, chatState);
      this.notebookChatboxes.delete(oldId);
    }

    this.saveToStorage();
  }

  /**
   * Set the current notebook ID and load its chat history
   * @param notebookId ID of the notebook
   * @returns The active chat thread for this notebook (creates one if none exists)
   */
  public setCurrentNotebook(notebookId: string): IChatThread {
    // If we're switching notebooks, hide the previous one
    if (this.currentNotebookId && this.currentNotebookId !== notebookId) {
      this.hideChatbox(this.currentNotebookId);
    }

    if (this.currentNotebookId) {
      if (this.getCurrentThread()) {
        const lastThread = this.getCurrentThread();
        AppStateService.getState().chatContainer?.chatWidget.threadManager.storeLastThreadForNotebook(
          this.currentNotebookId,
          lastThread?.id
        );
      }
    }

    console.log(`[ChatHistoryManager] Setting current notebook: ${notebookId}`);
    this.currentNotebookId = notebookId;

    // Check if we have chat history for this notebook
    if (!this.notebookChats.has(notebookId)) {
      // Create a default thread for this notebook
      const defaultThread: IChatThread = {
        id: this.generateThreadId(),
        name: 'New Chat',
        messages: [],
        lastUpdated: Date.now(),
        contexts: new Map<string, MentionContext>(),
        message_timestamps: new Map<string, number>()
      };

      this.notebookChats.set(notebookId, [defaultThread]);
      this.saveToStorage();
    }

    // Get all threads for this notebook
    const threads = this.notebookChats.get(notebookId)!;

    // Sort threads by lastUpdated (most recent first)
    const sortedThreads = [...threads].sort(
      (a, b) => b.lastUpdated - a.lastUpdated
    );

    // Find the most recent "New Chat" thread if it exists
    const mostRecentNewChat = sortedThreads.find(
      thread => thread.name === 'New Chat'
    );

    // If there's a most recent "New Chat", use that as the active thread
    if (mostRecentNewChat) {
      this.currentThreadId = mostRecentNewChat.id;
    } else {
      // Otherwise set the current thread to the first thread
      this.currentThreadId = threads[0].id;
    }

    // Make sure this notebook's chatbox is visible
    this.showChatbox(notebookId);

    // Return the current thread
    return this.getCurrentThread()!;
  }

  /**
   * Show the chatbox for a notebook
   * @param notebookId Path to the notebook
   */
  public showChatbox(notebookId: string): void {
    const state = this.notebookChatboxes.get(notebookId);
    if (state && state.chatbox) {
      state.isVisible = true;

      // Update the DOM element visibility
      const node = state.chatbox.node;
      if (node) {
        node.style.display = '';
        node.classList.remove('hidden-chatbox');
      }
    }

    // Hide all other chatboxes
    this.notebookChatboxes.forEach((otherState, path) => {
      if (path !== notebookId && otherState.chatbox) {
        otherState.isVisible = false;
        const node = otherState.chatbox.node;
        if (node) {
          node.style.display = 'none';
          node.classList.add('hidden-chatbox');
        }
      }
    });
  }

  /**
   * Hide the chatbox for a notebook
   * @param notebookId Path to the notebook
   */
  public hideChatbox(notebookId: string): void {
    const state = this.notebookChatboxes.get(notebookId);
    if (state && state.chatbox) {
      state.isVisible = false;
      const node = state.chatbox.node;
      if (node) {
        node.style.display = 'none';
        node.classList.add('hidden-chatbox');
      }
    }
  }

  /**
   * Get the current active chat thread
   * @returns The current chat thread or null if no notebook is set
   */
  public getCurrentThread(): IChatThread | null {
    if (!this.currentNotebookId || !this.currentThreadId) {
      return null;
    }

    const threads = this.notebookChats.get(this.currentNotebookId);
    if (!threads) {
      return null;
    }

    return threads.find(thread => thread.id === this.currentThreadId) || null;
  }

  /**
   * Get all chat threads for the current notebook
   * @returns Array of chat threads or empty array if no notebook is set
   */
  public getCurrentNotebookThreads(): IChatThread[] {
    if (!this.currentNotebookId) {
      return [];
    }

    return this.notebookChats.get(this.currentNotebookId) || [];
  }

  /**
   * Get all chat threads for a specific notebook
   * @param notebookId Path to the notebook
   * @returns Array of chat threads or null if notebook not found
   */
  public getThreadsForNotebook(notebookId: string): IChatThread[] | null {
    if (!notebookId || !this.notebookChats.has(notebookId)) {
      return null;
    }

    return this.notebookChats.get(notebookId) || [];
  }

  /**
   * Update the contexts in the current chat thread
   * @param contexts New contexts for the current thread
   */
  public updateCurrentThreadContexts(
    contexts: Map<string, MentionContext>
  ): void {
    if (!this.currentNotebookId || !this.currentThreadId) {
      console.warn(
        '[ChatHistoryManager] Cannot update contexts: No active notebook or thread'
      );
      return;
    }

    const threads = this.notebookChats.get(this.currentNotebookId);
    if (!threads) {
      console.warn(
        `[ChatHistoryManager] No threads found for notebook: ${this.currentNotebookId}`
      );
      return;
    }

    const threadIndex = threads.findIndex(
      thread => thread.id === this.currentThreadId
    );
    if (threadIndex === -1) {
      console.warn(
        `[ChatHistoryManager] Thread with ID ${this.currentThreadId} not found`
      );
      return;
    }

    // Update the contexts
    threads[threadIndex].contexts = new Map(contexts);
    threads[threadIndex].lastUpdated = Date.now();

    // Save to storage
    this.saveToStorage();
  }

  /**
   * Update the messages in the current chat thread
   * @param messages New messages for the current thread
   * @param contexts Optional contexts for mentions in the messages
   */
  public updateCurrentThreadMessages(
    messages: IChatMessage[],
    contexts?: Map<string, MentionContext>
  ): void {
    if (!this.currentNotebookId || !this.currentThreadId) {
      console.warn(
        '[ChatHistoryManager] Cannot update messages: No active notebook or thread'
      );
      return;
    }

    const threads = this.notebookChats.get(this.currentNotebookId);
    if (!threads) {
      console.warn(
        `[ChatHistoryManager] No threads found for notebook: ${this.currentNotebookId}`
      );
      return;
    }

    const threadIndex = threads.findIndex(
      thread => thread.id === this.currentThreadId
    );
    if (threadIndex === -1) {
      console.warn(
        `[ChatHistoryManager] Thread with ID ${this.currentThreadId} not found`
      );
      return;
    }

    try {
      for (const message of messages) {
        if (
          threads[threadIndex].message_timestamps?.has &&
          threads[threadIndex].message_timestamps?.has(JSON.stringify(message))
        ) {
          continue;
        }

        // Add timestamp for the message
        threads[threadIndex].message_timestamps.set(
          JSON.stringify(message),
          Date.now()
        );
        threads[threadIndex].message_timestamps;
      }
    } catch (error) {
      console.log(
        '[ChatHistoryManager] Error updating message timestamps for eval:',
        error
      );
      return;
    }

    // Update the messages and last updated time
    threads[threadIndex].messages = [...messages];

    threads[threadIndex].lastUpdated = Date.now();

    // Update contexts if provided
    if (contexts) {
      threads[threadIndex].contexts = new Map(contexts);
    }

    // Save to storage
    this.saveToStorage();
  }

  public static getCleanMessageArrayWithTimestamps(thread: IChatThread): any[] {
    // Return messages with timestamps
    return thread.messages.map(message => ({
      ...message,
      timestamp:
        thread.message_timestamps.get(JSON.stringify(message)) || Date.now()
    }));
  }

  /**
   * Clear the messages in the current chat thread
   */
  public clearCurrentThread(): void {
    this.updateCurrentThreadMessages([]);
  }

  /**
   * Get all notebook paths with chat histories
   * @returns Array of notebook paths
   */
  public getNotebookIds(): string[] {
    return Array.from(this.notebookChats.keys());
  }

  /**
   * Save all chat histories to state database
   */
  private async saveToStorage(): Promise<void> {
    try {
      // Convert Map to a serializable object
      const storageObj: Record<string, any[]> = {};

      console.log('SAVING CHAT TO STORAGE');
      console.log(this.notebookChats);

      for (const [notebookId, threads] of this.notebookChats.entries()) {
        // Convert each thread's contexts Map to a serializable object
        const serializedThreads = threads.map(thread => ({
          ...thread,
          contexts: thread.contexts ? Object.fromEntries(thread.contexts) : {},
          message_timestamps: thread.message_timestamps
            ? Object.fromEntries(thread.message_timestamps)
            : {}
        }));
        storageObj[notebookId] = serializedThreads;
      }

      await StateDBCachingService.setObjectValue(
        STATE_DB_KEYS.CHAT_HISTORIES,
        storageObj
      );

      console.log(
        '[ChatHistoryManager] Saved chat histories to StateDB storage'
      );
    } catch (error) {
      console.error(
        '[ChatHistoryManager] Error saving chat histories to StateDB storage:',
        error
      );
    }
  }

  /**
   * Load chat histories from state database with migration from settings registry
   */
  private async loadFromStorage(): Promise<void> {
    try {
      // First, try to migrate data from settings registry to state database
      await this.migrateFromSettingsRegistry();

      // Load data from state database
      const storedData = await StateDBCachingService.getObjectValue<
        Record<string, any[]>
      >(STATE_DB_KEYS.CHAT_HISTORIES, {});

      if (storedData && Object.keys(storedData).length > 0) {
        // Convert object back to Map
        this.notebookChats = new Map();
        for (const [notebookId, threads] of Object.entries(storedData)) {
          // Migrate old storage format to new format with contexts
          const migratedThreads: IChatThread[] = threads.map(thread => ({
            ...thread,
            // Handle migration for threads that don't have contexts
            contexts: thread.contexts
              ? new Map<string, MentionContext>(Object.entries(thread.contexts))
              : new Map<string, MentionContext>(),
            message_timestamps: thread.message_timestamps
              ? new Map<string, number>(
                  Object.entries(thread.message_timestamps)
                )
              : new Map<string, number>()
          }));

          this.notebookChats.set(notebookId, migratedThreads);
        }

        console.log(
          '[ChatHistoryManager] Loaded chat histories from StateDB storage'
        );
        console.log(
          `[ChatHistoryManager] Loaded ${this.notebookChats.size} notebook chat histories`
        );
      } else {
        console.log(
          '[ChatHistoryManager] No stored chat histories found in StateDB'
        );
      }
    } catch (error) {
      console.error(
        '[ChatHistoryManager] Error loading chat histories from StateDB storage:',
        error
      );
      // Reset to empty state on error
      this.notebookChats = new Map();
    }
  }

  /**
   * Migrate chat histories from settings registry to state database
   */
  private async migrateFromSettingsRegistry(): Promise<void> {
    try {
      // Check if data exists in settings registry
      const settingsData = await CachingService.getObjectSetting<
        Record<string, any[]>
      >(SETTING_KEYS.CHAT_HISTORIES, {});

      if (settingsData && Object.keys(settingsData).length > 0) {
        console.log(
          '[ChatHistoryManager] Migrating chat histories from SettingsRegistry to StateDB'
        );

        // Save to state database
        await StateDBCachingService.setObjectValue(
          STATE_DB_KEYS.CHAT_HISTORIES,
          settingsData
        );

        // Clear from settings registry
        await CachingService.setObjectSetting(SETTING_KEYS.CHAT_HISTORIES, {});

        console.log(
          '[ChatHistoryManager] Successfully migrated chat histories to StateDB'
        );
      }
    } catch (error) {
      console.error(
        '[ChatHistoryManager] Error during migration from SettingsRegistry to StateDB:',
        error
      );
    }
  }

  /**
   * Generate a unique ID for a new chat thread
   */
  private generateThreadId(): string {
    return (
      'thread-' + Date.now() + '-' + Math.random().toString(36).substring(2, 9)
    );
  }

  /**
   * Create a new chat thread for the current notebook
   * @param name Name of the new thread
   * @returns The newly created thread or null if no notebook is active
   */
  public createNewThread(name: string = 'New Chat'): IChatThread | null {
    if (!this.currentNotebookId) {
      console.warn(
        '[ChatHistoryManager] Cannot create thread: No active notebook'
      );
      return null;
    }

    const newThread: IChatThread = {
      id: this.generateThreadId(),
      name,
      messages: [],
      lastUpdated: Date.now(),
      contexts: new Map<string, MentionContext>(),
      message_timestamps: new Map<string, number>(),
      continueButtonShown: false
    };

    const existingThreads =
      this.notebookChats.get(this.currentNotebookId) || [];
    this.notebookChats.set(this.currentNotebookId, [
      ...existingThreads,
      newThread
    ]);

    // Set the new thread as the current thread
    this.currentThreadId = newThread.id;

    // Save to storage
    this.saveToStorage();

    return newThread;
  }

  /**
   * Switch to a specific chat thread
   * @param threadId ID of the thread to switch to
   * @returns The thread that was switched to, or null if not found
   */
  public switchToThread(threadId: string): IChatThread | null {
    if (!this.currentNotebookId) {
      return null;
    }

    const threads = this.notebookChats.get(this.currentNotebookId);
    if (!threads) {
      return null;
    }

    const thread = threads.find(t => t.id === threadId);
    if (thread) {
      this.currentThreadId = threadId;
      return thread;
    }

    return null;
  }

  /**
   * Rename the current chat thread
   * @param newName New name for the current thread
   * @returns True if successful, false otherwise
   */
  public renameCurrentThread(newName: string): boolean {
    if (!this.currentNotebookId || !this.currentThreadId) {
      console.warn(
        '[ChatHistoryManager] Cannot rename thread: No active notebook or thread'
      );
      return false;
    }

    const threads = this.notebookChats.get(this.currentNotebookId);
    if (!threads) {
      console.warn(
        `[ChatHistoryManager] No threads found for notebook: ${this.currentNotebookId}`
      );
      return false;
    }

    const threadIndex = threads.findIndex(
      thread => thread.id === this.currentThreadId
    );
    if (threadIndex === -1) {
      console.warn(
        `[ChatHistoryManager] Thread with ID ${this.currentThreadId} not found`
      );
      return false;
    }

    // Update the thread name
    threads[threadIndex].name = newName;

    // Save to storage
    this.saveToStorage();

    console.log(
      `[ChatHistoryManager] Renamed thread ${this.currentThreadId} to "${newName}"`
    );
    return true;
  }

  /**
   * Delete a chat thread
   * @param threadId ID of the thread to delete
   * @returns True if successful, false otherwise
   */
  public deleteThread(threadId: string): boolean {
    if (!this.currentNotebookId) {
      console.warn(
        '[ChatHistoryManager] Cannot delete thread: No active notebook'
      );
      return false;
    }

    const threads = this.notebookChats.get(this.currentNotebookId);
    if (!threads) {
      return false;
    }

    const threadIndex = threads.findIndex(thread => thread.id === threadId);
    if (threadIndex === -1) {
      return false;
    }

    // Remove the thread
    threads.splice(threadIndex, 1);

    // If we deleted the current thread, switch to first available thread
    if (threadId === this.currentThreadId) {
      if (threads.length > 0) {
        this.currentThreadId = threads[threads.length - 1].id;
      } else {
        // Create a new default thread if we deleted the last one
        const defaultThread: IChatThread = {
          id: this.generateThreadId(),
          name: 'New Chat',
          messages: [],
          lastUpdated: Date.now(),
          contexts: new Map<string, MentionContext>(),
          message_timestamps: new Map<string, number>(),
          continueButtonShown: false
        };

        threads.push(defaultThread);
        this.currentThreadId = defaultThread.id;
      }
    }

    // Save to storage
    this.saveToStorage();

    console.log(`[ChatHistoryManager] Deleted thread ${threadId}`);
    return true;
  }
}
