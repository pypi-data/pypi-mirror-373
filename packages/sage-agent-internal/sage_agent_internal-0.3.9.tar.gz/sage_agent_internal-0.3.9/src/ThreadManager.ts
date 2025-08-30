import { ChatHistoryManager, IChatThread } from './Chat/ChatHistoryManager';
import { ChatMessages } from './Chat/ChatMessages';
import { IChatService } from './Services/IChatService';
import { AppStateService } from './AppState';
import { StateDBCachingService } from './utils/stateDBCaching';

/**
 * Manages thread operations for the chatbox
 */
export class ThreadManager {
  private chatHistoryManager: ChatHistoryManager;
  private messageComponent: ChatMessages;
  private chatService: IChatService;
  private leftSideBanner!: HTMLDivElement;
  private bannerOverlay!: HTMLDivElement;
  private currentNotebookId: string | null = null;
  private chatNode: HTMLElement;
  private threadNameDisplay: HTMLElement;

  // Replace single templateContext with a templates array that includes names
  private templates: Array<{ name: string; content: string }> = [];

  constructor(
    chatHistoryManager: ChatHistoryManager,
    messageComponent: ChatMessages,
    chatService: IChatService,
    threadNameDisplay: HTMLElement,
    chatNode: HTMLElement
  ) {
    this.chatHistoryManager = chatHistoryManager;
    this.messageComponent = messageComponent;
    this.chatService = chatService;
    this.threadNameDisplay = threadNameDisplay;
    this.chatNode = chatNode;

    // Initialize the banner
    this.initializeBanner();

    // Subscribe to notebook change events from AppStateService
    AppStateService.onNotebookChanged().subscribe(({ newNotebookId }) => {
      if (newNotebookId) {
        this.setNotebookId(newNotebookId);
      }
    });

    // Update the thread name display
    this.updateThreadSelectorButtonText(
      this.chatHistoryManager.getCurrentThread()?.name || 'New Chat'
    );
  }

  public updateNotebookId(newId: string): void {
    this.setNotebookId(newId);
  }

  /**
   * Set the current notebook ID
   * @param notebookId ID of the notebook
   */
  public setNotebookId(notebookId: string | null): void {
    this.currentNotebookId = notebookId;
    this.refreshBannerIfVisible();
    this.updateThreadSelectorButtonText(
      this.chatHistoryManager.getCurrentThread()?.name || 'New Chat'
    );
  }

  /**
   * Store the last selected thread for a notebook
   * @param notebookId ID of the notebook
   * @param threadId ID of the thread to remember
   */
  public async storeLastThreadForNotebook(
    notebookId: string,
    threadId?: string
  ): Promise<void> {
    try {
      const key = `last-thread-${notebookId}`;
      if (threadId) await StateDBCachingService.setValue(key, threadId);
      else await StateDBCachingService.removeValue(key);
      console.log(
        `[ThreadManager] Stored last thread ${threadId} for notebook ${notebookId}`
      );
    } catch (error) {
      console.warn(`[ThreadManager] Failed to store last thread:`, error);
    }
  }

  /**
   * Get the last selected thread for a notebook
   * @param notebookId ID of the notebook
   * @returns The thread ID if found, null otherwise
   */
  public async getLastThreadForNotebook(
    notebookId: string
  ): Promise<string | null> {
    try {
      const key = `last-thread-${notebookId}`;
      const threadId = await StateDBCachingService.getValue(key, null);
      console.log(
        `[ThreadManager] Retrieved last thread ${threadId} for notebook ${notebookId}`
      );
      return threadId;
    } catch (error) {
      console.warn(`[ThreadManager] Failed to get last thread:`, error);
      return null;
    }
  }

  /**
   * Get the last selected thread object for a notebook, or null if not found
   * @param notebookId ID of the notebook
   * @returns The thread object if found and valid, null otherwise
   */
  public async getLastValidThreadForNotebook(
    notebookId: string
  ): Promise<IChatThread | null> {
    try {
      const threadId = await this.getLastThreadForNotebook(notebookId);
      if (!threadId) {
        return null;
      }

      // Check if the thread still exists in the chat history
      const threads = this.chatHistoryManager.getThreadsForNotebook(notebookId);
      if (!threads) {
        console.log(
          `[ThreadManager] No threads found for notebook ${notebookId}`
        );
        await this.clearLastThreadForNotebook(notebookId);
        return null;
      }

      const thread = threads.find(t => t.id === threadId);

      if (thread) {
        console.log(
          `[ThreadManager] Found valid last thread: ${thread.name} for notebook ${notebookId}`
        );
        return thread;
      } else {
        console.log(
          `[ThreadManager] Last thread ${threadId} no longer exists for notebook ${notebookId}`
        );
        // Clean up invalid reference
        await this.clearLastThreadForNotebook(notebookId);
        return null;
      }
    } catch (error) {
      console.warn(`[ThreadManager] Failed to get last valid thread:`, error);
      return null;
    }
  }

  /**
   * Clear the stored last thread for a notebook
   * @param notebookId ID of the notebook
   */
  public async clearLastThreadForNotebook(notebookId: string): Promise<void> {
    try {
      const key = `last-thread-${notebookId}`;
      await StateDBCachingService.removeValue(key);
      console.log(
        `[ThreadManager] Cleared last thread for notebook ${notebookId}`
      );
    } catch (error) {
      console.warn(`[ThreadManager] Failed to clear last thread:`, error);
    }
  }

  /**
   * Filter thread list to display only one "New Chat" (the most recent)
   * @param threads Sorted threads (most recent first)
   * @returns Filtered thread list
   */
  private filterNewChatThreads(threads: IChatThread[]): IChatThread[] {
    // Find the most recent "New Chat" thread
    const newChatThreads = threads.filter(thread => thread.name === 'New Chat');

    // If there's only 0 or 1 "New Chat" thread, return all threads
    if (newChatThreads.length <= 1) {
      return threads;
    }

    // Get the most recent "New Chat" thread (should be first since threads are pre-sorted)
    const mostRecentNewChat = newChatThreads[0];

    // Filter out all other "New Chat" threads for display purposes
    return threads.filter(
      thread => thread.name !== 'New Chat' || thread.id === mostRecentNewChat.id
    );
  }

  /**
   * Update the thread selector button text
   * @param text Text to display on the button
   */
  private updateThreadSelectorButtonText(text: string): void {
    const nameSpan = this.threadNameDisplay;
    if (nameSpan) {
      nameSpan.textContent = text;
    }
  }

  /**
   * Select a specific thread and load its history
   * @param threadId ID of the thread to select
   */
  public async selectThread(threadId: string): Promise<void> {
    // First, cancel any ongoing request in the chat service
    this.chatService.cancelRequest();
    let thread = this.chatHistoryManager.getCurrentThread();
    if (threadId !== this.chatHistoryManager.getCurrentThread()?.id) {
      thread = this.chatHistoryManager.switchToThread(threadId);
      const nbId = AppStateService.getState().currentNotebookId;
      if (nbId) await this.storeLastThreadForNotebook(nbId, thread?.id);
    }

    if (thread) {
      // Load the selected thread
      await this.messageComponent.loadFromThread(thread);

      // Update the thread selector button text
      this.updateThreadSelectorButtonText(thread.name);

      if (thread.messages.length > 0)
        AppStateService.getState().chatContainer?.chatWidget.showHistoryWidget();
      else
        AppStateService.getState().chatContainer?.chatWidget.showNewChatDisplay();
      AppStateService.getState().chatContainer?.chatWidget.llmStateDisplay.hide();

      this.clearDiffs();
    }
  }

  /**
   * Create a new chat thread
   */
  public async createNewThread(): Promise<IChatThread | null> {
    // Only proceed if we have an active notebook
    if (!this.currentNotebookId) {
      return null;
    }

    // Get the current thread to rename if it has messages
    const currentThread = this.chatHistoryManager.getCurrentThread();
    if (currentThread && currentThread.messages.length > 0) {
      // Find the first user message to use for naming
      const firstUserMessage = currentThread.messages.find(
        msg => msg.role === 'user' && typeof msg.content === 'string'
      );

      if (firstUserMessage && typeof firstUserMessage.content === 'string') {
        // Generate a paraphrased name for the thread
        const threadName = this.paraphraseThreadName(firstUserMessage.content);

        // Rename the current thread
        this.chatHistoryManager.renameCurrentThread(threadName);
      }
    }

    // Create a new thread
    const newThread = this.chatHistoryManager.createNewThread('New Chat');

    if (newThread) {
      const nbId = AppStateService.getState().currentNotebookId;
      if (nbId) await this.storeLastThreadForNotebook(nbId, newThread?.id);

      // Load the empty thread into the UI
      await this.messageComponent.loadFromThread(newThread);

      // Update the thread selector
      this.updateThreadSelectorButtonText('New Chat');

      this.clearDiffs();
    }

    return newThread;
  }

  public clearDiffs(): void {
    AppStateService.getNotebookDiffManager().rejectAndRevertDiffsImmediately();
  }

  /**
   * Generate a paraphrased name from a user message
   * @param message User message to paraphrase
   * @returns Short paraphrased thread name
   */
  private paraphraseThreadName(message: string): string {
    // Simplistic approach: take the first 5-8 words, max 30 chars
    const words = message.split(/\s+/);
    const selectedWords = words.slice(0, Math.min(8, words.length));
    let threadName = selectedWords.join(' ');

    // Truncate if too long
    if (threadName.length > 30) {
      threadName = threadName.substring(0, 27) + '...';
    }

    return threadName;
  }

  private initializeBanner(): void {
    // Create left side banner overlay
    this.bannerOverlay = document.createElement('div');
    this.bannerOverlay.className = 'sage-ai-banner-overlay';
    this.bannerOverlay.style.display = 'none';

    // Create left side banner
    this.leftSideBanner = document.createElement('div');
    this.leftSideBanner.className = 'sage-ai-left-side-banner';
    this.leftSideBanner.innerHTML = `
      <div class="sage-ai-banner-header">
        <h3>All Chats</h3>
        <button class="sage-ai-icon-close sage-ai-icon-button-sm">×</button>
      </div>
      <div class="sage-ai-banner-content">
        <div class="sage-ai-banner-threads"></div>
      </div>
    `;

    this.leftSideBanner
      .querySelector('.sage-ai-icon-close')
      ?.addEventListener('click', () => {
        this.closeBanner();
      });

    // Add banner elements to the document body
    this.chatNode.appendChild(this.bannerOverlay);
    this.chatNode.appendChild(this.leftSideBanner);

    // Setup banner event handlers
    this.setupBannerEventHandlers();
  }

  private setupBannerEventHandlers(): void {
    // Close banner when clicking the close button
    const closeButton = this.leftSideBanner.querySelector(
      '.sage-ai-banner-close'
    );
    if (closeButton) {
      closeButton.addEventListener('click', () => {
        this.closeBanner();
      });
    }

    // Close banner when clicking outside
    this.bannerOverlay.addEventListener('click', () => {
      this.closeBanner();
    });
  }

  /**
   * Open the left side banner with animation
   */
  public openBanner(): void {
    // Show overlay first
    this.bannerOverlay.style.display = 'block';

    // Trigger reflow to ensure display change is applied
    this.bannerOverlay.offsetHeight;

    // Add visible class to trigger animation
    this.bannerOverlay.classList.add('visible');

    // Show banner and trigger animation
    this.leftSideBanner.style.display = 'block';
    this.leftSideBanner.offsetHeight; // Trigger reflow
    this.leftSideBanner.classList.add('visible');

    // Populate banner content
    this.populateBannerContent();
  }

  /**
   * Close the left side banner with animation
   */
  public closeBanner(): void {
    // Remove visible classes to trigger closing animation
    this.leftSideBanner.classList.remove('visible');
    this.bannerOverlay.classList.remove('visible');

    // Hide elements after animation completes
    setTimeout(() => {
      this.leftSideBanner.style.display = 'none';
      this.bannerOverlay.style.display = 'none';
    }, 300); // Match CSS animation duration
  }

  /**
   * Populate the banner content with thread information
   */
  private populateBannerContent(): void {
    const threadsContainer = this.leftSideBanner.querySelector(
      '.sage-ai-banner-threads'
    );
    if (!threadsContainer) return;

    // Clear existing content
    threadsContainer.innerHTML = '';

    if (!this.currentNotebookId) {
      threadsContainer.innerHTML =
        '<div class="sage-ai-banner-empty">No notebook selected</div>';
      return;
    }

    // Get threads for this notebook
    const threads = this.chatHistoryManager.getCurrentNotebookThreads();

    if (threads.length === 0) {
      threadsContainer.innerHTML =
        '<div class="sage-ai-banner-empty">No chat history</div>';
      return;
    }

    // Sort threads by last updated (most recent first)
    const sortedThreads = [...threads].sort(
      (a, b) => b.lastUpdated - a.lastUpdated
    );

    // Filter to keep only one "New Chat" - the most recent one
    const displayThreads = this.filterNewChatThreads(sortedThreads);

    for (const thread of displayThreads) {
      const threadItem = document.createElement('div');
      threadItem.className = 'sage-ai-banner-thread-item';

      if (thread.id === this.chatHistoryManager.getCurrentThread()?.id) {
        threadItem.classList.add('active');
      }

      threadItem.innerHTML = `
        <div class="sage-ai-banner-thread-name">${thread.name}</div>
        <div class="sage-ai-banner-thread-date">${formatDate(thread.lastUpdated)}</div>
      `;

      threadItem.addEventListener('click', async () => {
        await this.selectThread(thread.id);
        this.closeBanner();
      });

      threadsContainer.appendChild(threadItem);
    }
  }

  /**
   * Refresh the banner content if it's currently visible
   */
  public refreshBannerIfVisible(): void {
    if (
      this.leftSideBanner &&
      this.leftSideBanner.classList.contains('visible')
    ) {
      this.populateBannerContent();
    }
  }
}

/**
 * Format a date as a string.
 * Example: "7/1/25 · 12:00 PM"
 * @param date The date to format
 * @returns The formatted date string
 */
function formatDate(date: number): string {
  return (
    new Date(date).toLocaleDateString('en-US', {
      month: 'numeric',
      day: 'numeric',
      year: '2-digit'
    }) +
    ' · ' +
    new Date(date).toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    })
  );
}
