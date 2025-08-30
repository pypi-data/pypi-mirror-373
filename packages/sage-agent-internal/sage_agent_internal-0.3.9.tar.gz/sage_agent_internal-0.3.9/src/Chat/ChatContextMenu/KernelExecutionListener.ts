/**
 * Service for listening to kernel execution events and triggering context refreshes
 */
import { INotebookTracker } from '@jupyterlab/notebook';
import { ContextCacheService } from './ContextCacheService';
import { AppStateService } from '../../AppState';

export class KernelExecutionListener {
  private static instance: KernelExecutionListener | null = null;
  private notebookTracker: INotebookTracker | null = null;
  private contextCacheService: ContextCacheService | null = null;
  private isInitialized = false;
  private kernelConnectionListeners = new Map<string, () => void>();
  private lastExecutionTime = 0;
  private readonly EXECUTION_COOLDOWN_MS = 1000; // 1 second cooldown
  private pendingExecutions = new Map<string, boolean>(); // Track silent vs non-silent executions

  private constructor() {}

  public static getInstance(): KernelExecutionListener {
    if (!KernelExecutionListener.instance) {
      KernelExecutionListener.instance = new KernelExecutionListener();
    }
    return KernelExecutionListener.instance;
  }

  /**
   * Initialize the kernel execution listener
   */
  public async initialize(notebookTracker: INotebookTracker): Promise<void> {
    if (this.isInitialized) {
      return;
    }

    this.notebookTracker = notebookTracker;
    this.contextCacheService = ContextCacheService.getInstance();

    // Listen for notebook changes to set up kernel listeners
    this.notebookTracker.currentChanged.connect(
      this.handleNotebookChange,
      this
    );

    // Set up initial kernel listener if there's already an active notebook
    if (this.notebookTracker.currentWidget) {
      this.setupKernelListener(this.notebookTracker.currentWidget);
    }

    this.isInitialized = true;
    console.log('[KernelExecutionListener] Initialized successfully');
  }

  /**
   * Handle notebook change events and set up kernel listeners
   */
  private handleNotebookChange(tracker: INotebookTracker, notebook: any): void {
    if (notebook) {
      this.setupKernelListener(notebook);
    }
  }

  /**
   * Set up a kernel execution listener for a specific notebook
   */
  private setupKernelListener(notebookWidget: any): void {
    try {
      const sessionContext = notebookWidget.sessionContext;
      if (!sessionContext) {
        console.warn('[KernelExecutionListener] No session context available');
        return;
      }

      const kernelId = sessionContext.session?.kernel?.id;
      if (!kernelId) {
        console.warn('[KernelExecutionListener] No kernel available');
        return;
      }

      // Clean up existing listener for this kernel if it exists
      if (this.kernelConnectionListeners.has(kernelId)) {
        this.kernelConnectionListeners.get(kernelId)?.();
        this.kernelConnectionListeners.delete(kernelId);
      }

      const kernel = sessionContext.session?.kernel;

      if (!kernel) return;

      console.log(
        `[KernelExecutionListener] Setting up execution listener for kernel: ${kernelId}`
      );

      // Track execution requests to differentiate silent vs user executions
      const originalRequestExecute = kernel.requestExecute.bind(kernel);
      kernel.requestExecute = (options: any) => {
        const isSilent = options.silent === true;
        console.log(
          `[KernelExecutionListener] Execution request: silent=${isSilent}, code preview: ${options.code?.substring(0, 50)}...`
        );
        
        const future = originalRequestExecute(options);
        
        // Store whether this execution is silent
        if (future.msg && future.msg.header && future.msg.header.msg_id) {
          this.pendingExecutions.set(future.msg.header.msg_id, isSilent);
        }
        
        return future;
      };

      // Listen for kernel status changes - this fires when execution starts/stops

      const statusChangedHandler = () => {
        const status = kernel.status;
        console.log(
          `[KernelExecutionListener] Kernel status changed to: ${status}`
        );

        // When kernel goes from 'busy' to 'idle', it means execution finished
        if (status === 'idle') {
          this.handleExecutionComplete(kernelId);
        }
      };

      // Connect to kernel status changes
      kernel.statusChanged.connect(statusChangedHandler);

      // Store cleanup function
      const cleanup = () => {
        kernel.statusChanged.disconnect(statusChangedHandler);
        // Clear any pending executions for this kernel
        this.pendingExecutions.clear();
        console.log(
          `[KernelExecutionListener] Cleaned up listener for kernel: ${kernelId}`
        );
      };

      this.kernelConnectionListeners.set(kernelId, cleanup);

      // Also listen for when session changes (kernel restart, etc.)
      const sessionChangedHandler = () => {
        console.log(
          '[KernelExecutionListener] Session changed, setting up new kernel listener'
        );
        // Clean up old listener
        this.kernelConnectionListeners.get(kernelId)?.();
        this.kernelConnectionListeners.delete(kernelId);
        // Set up new listener
        setTimeout(() => this.setupKernelListener(notebookWidget), 100);
      };

      sessionContext.sessionChanged.connect(sessionChangedHandler);
    } catch (error) {
      console.warn(
        '[KernelExecutionListener] Error setting up kernel listener:',
        error
      );
    }
  }

  /**
   * Handle completion of code execution
   */
  private handleExecutionComplete(kernelId?: string): void {
    const now = Date.now();

    // Apply cooldown to prevent too many rapid calls
    if (now - this.lastExecutionTime < this.EXECUTION_COOLDOWN_MS) {
      console.log(
        '[KernelExecutionListener] Execution complete, but within cooldown period'
      );
      return;
    }

    // Check if we have any recent executions that were non-silent (user executions)
    let hasUserExecution = false;
    if (kernelId && this.pendingExecutions.size > 0) {
      // Check if any pending executions were non-silent
      for (const [msgId, isSilent] of this.pendingExecutions.entries()) {
        if (!isSilent) {
          hasUserExecution = true;
          console.log(
            `[KernelExecutionListener] Found user (non-silent) execution: ${msgId}`
          );
          break;
        }
      }
      
      // Clear pending executions since kernel is now idle
      this.pendingExecutions.clear();
      
      if (!hasUserExecution) {
        console.log(
          '[KernelExecutionListener] Only silent executions detected, skipping variable refresh'
        );
        return;
      }
    }

    this.lastExecutionTime = now;

    console.log(
      '[KernelExecutionListener] User code execution completed, refreshing variables...'
    );

    if (this.contextCacheService) {
      // Use the existing method with its own timeout
      this.contextCacheService.refreshVariablesAfterExecution();
    } else {
      console.warn(
        '[KernelExecutionListener] ContextCacheService not available'
      );
    }
  }

  /**
   * Manually trigger a variable refresh (useful for testing)
   */
  public triggerVariableRefresh(): void {
    console.log(
      '[KernelExecutionListener] Manually triggering variable refresh...'
    );
    this.handleExecutionComplete();
  }

  /**
   * Clean up all listeners
   */
  public dispose(): void {
    // Clean up all kernel listeners
    this.kernelConnectionListeners.forEach(cleanup => cleanup());
    this.kernelConnectionListeners.clear();

    // Clear pending executions
    this.pendingExecutions.clear();

    // Disconnect from notebook tracker
    if (this.notebookTracker) {
      this.notebookTracker.currentChanged.disconnect(
        this.handleNotebookChange,
        this
      );
    }

    this.isInitialized = false;
    console.log('[KernelExecutionListener] Disposed');
  }

  /**
   * Get debug information about current listeners
   */
  public getDebugInfo(): {
    isInitialized: boolean;
    activeListeners: number;
    lastExecutionTime: number;
    pendingExecutions: number;
  } {
    return {
      isInitialized: this.isInitialized,
      activeListeners: this.kernelConnectionListeners.size,
      lastExecutionTime: this.lastExecutionTime,
      pendingExecutions: this.pendingExecutions.size
    };
  }
}
