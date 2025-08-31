import { Client } from '@modelcontextprotocol/sdk/client/index';
import { IToolCall } from '../types';
import { ConfigService } from '../Config/ConfigService';
import { INotebookTracker } from '@jupyterlab/notebook';
import { NotebookTools } from '../Notebook/NotebookTools';
import { AppStateService } from '../AppState';

import { WaitingUserReplyBoxManager } from '../Notebook/WaitingUserReplyBoxManager';
import { FilesystemTools } from '../BackendTools';
import { Contents } from '@jupyterlab/services';

export type ToolCall =
  | 'codebase-list_repos'
  | 'notebook-add_cell'
  | 'notebook-remove_cells'
  | 'notebook-edit_cell'
  | 'notebook-edit_plan'
  | 'notebook-run_cell'
  | 'notebook-get_cell_info'
  | 'notebook-read_cells'
  | 'web-search_dataset'
  | 'web-download_dataset'
  | 'filesystem-list_datasets'
  | 'filesystem-read_dataset'
  | 'filesystem-delete_dataset'
  | 'filesystem-save_dataset'
  | 'notebook-wait_user_reply';

/**
 * Service for handling tool executions and MCP client
 */
export class ToolService {
  private client: Client | null = null;
  private tools: any[] = [];
  private kernelInfo: { name?: string; id?: string } = {};
  private notebookInfo: { path?: string; id?: string } = {};

  // Add a reference to the notebook tracker
  private notebookTracker: INotebookTracker | null = null;

  // Add a reference to the NotebookTools instance
  public notebookTools: NotebookTools | null = null;

  // Add a reference to the FilesystemTools instance
  public filesystemTools: FilesystemTools | null = null;

  // Add reference to content manager
  private contentManager: Contents.IManager | null = null;

  // Add reference to the notebook context manager
  private notebookContextManager: any = null;

  // Map to store notebook-specific context
  private notebookContexts: Map<
    string,
    {
      kernelInfo: { name?: string; id?: string };
      notebookInfo: { path?: string; id?: string };
    }
  > = new Map();

  // Function reference for retrieving kernel and notebook info dynamically
  private kernelInfoProvider?: () => Promise<{ name?: string; id?: string }>;
  private notebookInfoProvider?: () => Promise<{ path?: string; id?: string }>;

  // Tool name mapping from MCP server to local implementation
  private toolMappings: { [key: string]: string } = {
    'notebook-get_cell_info': 'get_cell_info',
    'notebook-get_cells': 'get_cells',
    'notebook-read_cells': 'read_cells',
    'notebook-add_cell': 'add_cell',
    'notebook-edit_cell': 'edit_cell',
    'notebook-remove_cells': 'remove_cells',
    'notebook-run_cell': 'run_cell',
    'notebook-execute_cell': 'execute_cell',
    'notebook-get_notebook_info': 'get_notebook_info',
    'notebook-edit_plan': 'edit_plan',
    'notebook-wait_user_reply': 'wait_user_reply',
    'filesystem-list_datasets': 'list_datasets',
    'filesystem-read_dataset': 'read_dataset',
    'filesystem-delete_dataset': 'delete_dataset',
    'filesystem-save_dataset': 'save_dataset',
    'web-search_dataset': 'search_dataset'
  };

  // --- Reconnection Logic Additions ---
  private isConnected: boolean = false;
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 10;
  private reconnectIntervalMs: number = 5000; // Start with 5 seconds

  // Store the connection promise to avoid multiple simultaneous connection attempts
  private connectingPromise: Promise<void> | null = null;

  /**
   * Initialize or re-initialize the MCP client
   */
  async initialize(): Promise<void> {
    if (this.connectingPromise) {
      console.log('[ToolService] Already attempting to connect, waiting...');
      return this.connectingPromise;
    }

    this.connectingPromise = (async () => {
      try {
        if (this.client) {
          // If client exists, it means we are re-initializing. Clean up old connection.
          console.log(
            '[ToolService] Disconnecting existing client before re-initialization.'
          );

          await this.client.close();
          this.client = null;
        }

        const config = await ConfigService.getConfig();

        this.client = new Client({
          name: 'sage-ai-client',
          version: '1.0.0'
        });

        // const transport = new SSEClientTransport(
        //   new URL('/sse', ConfigService.getMcpBaseUrl()),
        //   {
        //     requestInit: {
        //       headers: {
        //         Accept: 'text/event-stream'
        //       }
        //     }
        //   }
        // );
        //
        // await this.client.connect(transport);
        // await this.refreshRemoteTools();

        this.tools = await ConfigService.getTools();

        this.client.onerror = error => {
          console.log('[ToolService] Client error', error);
          const isConnectionError =
            error.message === 'SSE error: Failed to fetch';
          if (isConnectionError) {
            this.handleConnectionLoss();
          }
        };

        this.isConnected = true;
        this.reconnectAttempts = 0; // Reset on successful connection
        console.log(
          '[ToolService] MCP client initialized and connected successfully.'
        );
        return;
      } catch (error) {
        console.error('Failed to initialize MCP client:', error);
        this.isConnected = false; // Mark as disconnected on failure
        throw error; // Re-throw to allow calling context to handle
      } finally {
        this.connectingPromise = null; // Clear the promise once attempt is done
      }
    })();
    return this.connectingPromise;
  }

  public updateNotebookId(oldNotebookId: string, newNotebookId: string): void {
    const currentContext = this.notebookContexts.get(oldNotebookId) || {
      kernelInfo: { name: this.kernelInfo.name, id: this.kernelInfo.id },
      notebookInfo: { path: this.notebookInfo.path, id: this.notebookInfo.id }
    };

    this.notebookContexts.set(newNotebookId, currentContext);

    this.notebookContexts.delete(oldNotebookId);

    // Update the centralized notebook ID in AppStateService
    AppStateService.setCurrentNotebookId(newNotebookId);
  }

  /**
   * Handles connection loss and attempts to reconnect.
   * This method will be called when a remote tool call fails due to network issues.
   */
  private async handleConnectionLoss(): Promise<void> {
    if (this.isConnected) {
      console.warn('[ToolService] Connection lost. Attempting to reconnect...');
      this.isConnected = false; // Mark as disconnected
    }

    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay =
        this.reconnectIntervalMs * Math.pow(2, this.reconnectAttempts - 1); // Exponential backoff
      console.log(
        `[ToolService] Reconnection attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${delay / 1000} seconds...`
      );
      await new Promise(resolve => setTimeout(resolve, delay));

      try {
        await this.initialize();
        console.log('[ToolService] Reconnected successfully!');
      } catch (error) {
        console.error('[ToolService] Reconnection failed:', error);
        // Continue to the next attempt if initialize failed
        this.handleConnectionLoss(); // Try again after delay
      }
    } else {
      console.error(
        '[ToolService] Max reconnection attempts reached. Unable to connect to backend.'
      );
      // You might want to notify the user or take other actions here
    }
  }

  /**
   * Check if the MCP client is initialized
   * @returns boolean indicating if the client is initialized and connected
   */
  isInitialized(): boolean {
    return this.client !== null && this.isConnected;
  }

  /**
   * Set the notebook tracker from JupyterLab
   * This allows the tool service to access the current notebook context
   * @param notebooks The notebook tracker from JupyterLab
   */
  setNotebookTracker(
    notebooks: INotebookTracker,
    waitingUserReplyBoxManager: WaitingUserReplyBoxManager
  ): void {
    this.notebookTracker = notebooks;
    console.log('Notebook tracker set in ToolService');

    // Initialize NotebookTools with the tracker
    this.notebookTools = new NotebookTools(
      notebooks,
      waitingUserReplyBoxManager
    );
    console.log('NotebookTools initialized in ToolService');

    // Set up a change handler to automatically update kernel and notebook info
    this.notebookTracker.currentChanged.connect(
      this.handleNotebookChanged,
      this
    );
  }

  /**
   * Set the content manager from JupyterLab
   * This allows the tool service to access the filesystem
   * @param contentManager The content manager from JupyterLab
   */
  setContentManager(contentManager: Contents.IManager): void {
    this.contentManager = contentManager;
    console.log('Content manager set in ToolService');

    // Initialize FilesystemTools with the content manager
    this.filesystemTools = new FilesystemTools();
    console.log('FilesystemTools initialized in ToolService');
  }

  /**
   * Set the current active notebook ID context
   * @param notebookId ID of the notebook being used for context
   */
  setCurrentNotebookId(notebookId: string | null): void {
    const currentId = AppStateService.getCurrentNotebookId();
    if (notebookId === currentId) {
      return; // No change needed
    }

    console.log(`[ToolService] Setting current notebook ID: ${notebookId}`);
    AppStateService.setCurrentNotebookId(notebookId);

    // If we have context for this notebook, restore it
    if (notebookId && this.notebookContexts.has(notebookId)) {
      const context = this.notebookContexts.get(notebookId)!;
      this.kernelInfo = { ...context.kernelInfo };
      this.notebookInfo = { ...context.notebookInfo };
      console.log(
        `[ToolService] Restored context for notebook: ${notebookId}`,
        { kernel: this.kernelInfo, notebook: this.notebookInfo }
      );
    } else if (notebookId) {
      // If this is a new notebook ID, initialize with current notebook tracker
      this.handleNotebookChanged();
      // Store the new context
      this.storeNotebookContext(notebookId);
    }
  }

  /**
   * Get the current notebook ID
   * @returns The current notebook ID or null if none
   */
  getCurrentNotebookId(): string | null {
    return AppStateService.getCurrentNotebookId();
  }

  /**
   * Store the current kernel and notebook info for a specific notebook path
   * @param notebookPath Path to the notebook
   */
  private storeNotebookContext(notebookPath: string): void {
    if (!notebookPath) return;

    this.notebookContexts.set(notebookPath, {
      kernelInfo: { ...this.kernelInfo },
      notebookInfo: { ...this.notebookInfo }
    });

    console.log(`[ToolService] Stored context for notebook: ${notebookPath}`, {
      kernel: this.kernelInfo,
      notebook: this.notebookInfo
    });
  }

  /**
   * Handle notebook changes - update kernel and notebook info automatically
   */
  private handleNotebookChanged(): void {
    if (!this.notebookTracker) {
      return;
    }

    const current = this.notebookTracker.currentWidget;
    if (!current) {
      console.log('No active notebook');
      return;
    }

    // Update notebook info
    this.notebookInfo = {
      path: current.sessionContext.path,
      id: current.id
    };

    // Update kernel info if available
    const session = current.sessionContext.session;
    const kernelConnection = session?.kernel;
    if (kernelConnection) {
      this.kernelInfo = {
        name: kernelConnection.name,
        id: kernelConnection.id
      };
    }

    // If we have a current notebook ID, store this updated context
    const currentNotebookId = AppStateService.getCurrentNotebookId();
    if (currentNotebookId) {
      this.storeNotebookContext(currentNotebookId);
    }
  }

  /**
   * Get the current active notebook directly from the tracker
   * @param notebookPath Optional path to get a specific notebook instead of the active one
   * @returns Object with information about the current notebook or null if none
   */
  getCurrentNotebook(notebookPath?: string): {
    widget: any;
    path?: string;
    id?: string;
    kernel?: any;
  } | null {
    if (!this.notebookTracker) {
      return null;
    }

    // If notebookPath is provided, find that specific notebook
    let current = null;
    if (notebookPath) {
      this.notebookTracker.forEach(widget => {
        if (widget.context.path === notebookPath) {
          current = widget;
        }
      });
    } else {
      // Otherwise use the current active notebook
      current = this.notebookTracker.currentWidget;
    }

    if (!current) {
      return null;
    }

    const session = current.sessionContext.session;
    const kernelConnection = session?.kernel;

    return {
      widget: current,
      path: current.sessionContext.path,
      id: current.id,
      kernel: kernelConnection || undefined
    };
  }

  /**
   * Refresh available tools from MCP server
   */
  async refreshRemoteTools(): Promise<any[]> {
    if (!this.client) {
      throw new Error('MCP client not initialized');
    }

    try {
      const capabilities = (await this.client.listTools()) as any;
      console.log('Available MCP tools:', capabilities);

      this.tools = [];
      for (const tool of capabilities.tools) {
        if (tool.name === 'notebook-read_notebook_summary') continue;
        this.tools.push({
          name: tool.name,
          description: tool.description,
          input_schema: tool.inputSchema
        });
      }

      console.log(`Updated ${this.tools.length} tools from MCP server.`);
      return this.tools;
    } catch (error) {
      console.error('Failed to update tools:', error);
      throw error;
    }
  }

  /**
   * Get available tools
   */
  getTools(): any[] {
    return this.tools;
  }

  getAskModeTools(): any[] {
    const askModeTools = [
      'notebook-get_cell_info',
      'notebook-read_cells',
      'web-search_dataset',
      'filesystem-list_datasets',
      'filesystem-read_dataset',
      'notebook-wait_user_reply'
    ];

    return this.tools.filter(tool => askModeTools.includes(tool.name));
  }

  /**
   * Fetch the latest kernel and notebook information using provider functions
   * @returns A promise that resolves when info is updated
   */
  private async refreshDynamicInfo(): Promise<void> {
    try {
      // First try to get information directly from the notebook tracker
      if (this.notebookTracker && this.notebookTracker.currentWidget) {
        this.handleNotebookChanged();
      }

      // Then try using the provider functions if available
      if (this.kernelInfoProvider) {
        const latestKernelInfo = await this.kernelInfoProvider();
        if (latestKernelInfo) {
          this.kernelInfo = latestKernelInfo;
          console.log('Kernel info dynamically updated:', this.kernelInfo);
        }
      }

      if (this.notebookInfoProvider) {
        const latestNotebookInfo = await this.notebookInfoProvider();
        if (latestNotebookInfo) {
          this.notebookInfo = latestNotebookInfo;
          console.log('Notebook info dynamically updated:', this.notebookInfo);
        }
      }
    } catch (error) {
      console.error('Error refreshing dynamic info:', error);
    }
  }

  /**
   * Check if a tool can be handled locally by NotebookTools, FilesystemTools, or WebTools
   * @param toolName Name of the tool to check
   * @returns True if the tool can be handled locally
   */
  private canHandleToolLocally(toolName: string): boolean {
    return (
      (this.notebookTools !== null || this.filesystemTools !== null) &&
      toolName in this.toolMappings
    );
  }

  /**
   * Execute a tool locally using NotebookTools, FilesystemTools, or WebTools
   * @param toolName Name of the tool to execute
   * @param args Arguments to pass to the tool
   * @returns Result of the tool execution
   */
  private async executeLocalTool(toolName: string, args: any): Promise<any> {
    const methodName = this.toolMappings[toolName];
    console.log(`Executing local tool "${methodName}" with args:`, args);

    try {
      // Determine which tool service to use based on the tool name
      if (toolName.startsWith('filesystem-')) {
        if (!this.filesystemTools) {
          throw new Error('FilesystemTools not initialized');
        }

        // Call the corresponding method on filesystemTools
        const result = await (this.filesystemTools as any)[methodName](args);
        console.log(`Local filesystem tool "${methodName}" returned:`, result);
        return result;
      } else if (toolName.startsWith('web-')) {
        if (!this.notebookTools) {
          throw new Error('NotebookTools not initialized');
        }

        // Call the corresponding method on notebookTools (which has webTools)
        const result = await (this.notebookTools as any)[methodName](args);
        console.log(`Local web tool "${methodName}" returned:`, result);
        return result;
      } else {
        if (!this.notebookTools) {
          throw new Error('NotebookTools not initialized');
        }

        // For tools that operate on notebook cells, ensure we pass the notebook_path
        // to maintain the correct notebook context
        const notebookPath = args.notebook_path || null;

        // Call the corresponding method on notebookTools
        const result = await (this.notebookTools as any)[methodName](args);
        console.log(`Local notebook tool "${methodName}" returned:`, result);
        return result;
      }
    } catch (error) {
      console.error(`Error executing local tool "${methodName}":`, error);
      throw error;
    }
  }

  /**
   * Execute a tool call
   */
  async executeTool(
    toolCall: IToolCall,
    maxRetries = 3, // This is for tool execution retries, not connection retries
    includeContextInfo = true
  ): Promise<any> {
    // Before refreshing info, capture the notebook ID from the tool arguments
    // or use the current notebook ID from AppStateService
    const notebookId =
      toolCall.input?.notebook_id || AppStateService.getCurrentNotebookId();

    // If the tool specifies a notebook ID different from current, switch context
    const currentNotebookId = AppStateService.getCurrentNotebookId();
    if (notebookId && notebookId !== currentNotebookId) {
      this.setCurrentNotebookId(notebookId);
    }

    // Refresh kernel and notebook info before executing the tool
    await this.refreshDynamicInfo();

    const { name: toolName, input: toolArgs, id: toolId } = toolCall;

    // Check if we can handle this tool locally with NotebookTools or FilesystemTools
    if (this.canHandleToolLocally(toolName)) {
      try {
        console.log(`Executing tool ${toolName} locally with args:`, toolArgs);

        // Prepare arguments, optionally including context info
        const toolArguments = { ...toolArgs };

        // Add kernel and notebook information to arguments if requested
        if (includeContextInfo) {
          // Add kernel information
          if (this.kernelInfo.name) {
            toolArguments.kernel_name = this.kernelInfo.name;
          }
          if (this.kernelInfo.id) {
            toolArguments.kernel_id = this.kernelInfo.id;
          }

          // Add notebook information
          // Use the provided notebook ID or current notebook ID
          const contextNotebookId =
            toolArguments.notebook_id || AppStateService.getCurrentNotebookId();
          if (contextNotebookId) {
            toolArguments.notebook_id = contextNotebookId;
          }
          // Keep notebook_path for backward compatibility with tools that still expect it
          if (toolArguments.notebook_path) {
            // Keep existing notebook_path if provided
          } else if (this.notebookInfo.path) {
            toolArguments.notebook_path = this.notebookInfo.path;
          }
          if (this.notebookInfo.id) {
            toolArguments.notebook_id = this.notebookInfo.id;
          }
        }

        // For add_cell/edit_cell/remove_cells, we don't want to show diff view by default
        // The NotebookDiffManager will handle showing diffs later
        if (
          (toolName === 'notebook-add_cell' ||
            toolName === 'notebook-edit_cell') &&
          toolArguments.show_diff === undefined
        ) {
          toolArguments.show_diff = false;
        }

        // Execute the tool using our local implementation
        const result = await this.executeLocalTool(toolName, toolArguments);

        console.log(`Local tool ${toolName} returned:`, result);

        // Format the result as a string
        const resultContent =
          typeof result === 'object' ? JSON.stringify(result) : String(result);

        // Return proper tool result format for Claude
        return {
          type: 'tool_result',
          tool_use_id: toolId,
          content: resultContent
        };
      } catch (error) {
        console.error(`Local tool execution failed:`, error);

        // Return error as tool result
        return {
          type: 'tool_result',
          tool_use_id: toolId,
          content: `Error: ${error instanceof Error ? error.message : String(error)}`
        };
      }
    }

    // For non-local tools, use the MCP client
    let currentRemoteRetries = 0; // Use a distinct variable for remote tool call retries
    while (currentRemoteRetries <= maxRetries) {
      try {
        if (!this.isInitialized()) {
          console.warn(
            '[ToolService] MCP client not connected. Attempting to re-establish connection...'
          );
          await this.initialize(); // Attempt to initialize/reconnect
          if (!this.client || !this.isConnected) {
            throw new Error('MCP client could not establish connection.');
          }
        }

        console.log(`Executing remote tool ${toolName} with args:`, toolArgs);

        // Prepare arguments, optionally including context info
        const toolArguments = { ...toolArgs };

        // Add kernel and notebook information to arguments if requested
        if (includeContextInfo) {
          // Add kernel information
          if (this.kernelInfo.name) {
            toolArguments.kernel_name = this.kernelInfo.name;
          }
          if (this.kernelInfo.id) {
            toolArguments.kernel_id = this.kernelInfo.id;
          }

          // Add notebook information
          if (this.notebookInfo.path) {
            toolArguments.notebook_path = this.notebookInfo.path;
          }
          if (this.notebookInfo.id) {
            toolArguments.notebook_id = this.notebookInfo.id;
          }

          console.log('Including context info in tool call:', {
            kernel: this.kernelInfo,
            notebook: this.notebookInfo
          });
        }

        console.log('Tool arguments:', toolArguments);

        // Call the tool
        const result = (await this.client!.callTool({
          name: toolName,
          arguments: toolArguments
        })) as any;

        console.log(`Tool ${toolName} returned:`, result);

        const cleanedResult = [];
        if (result && result.content) {
          for (const content of result.content) {
            try {
              const cleaned = JSON.parse(content.text);
              cleanedResult.push({
                ...content,
                text: JSON.stringify(cleaned, null, 2)
              });
            } catch (e) {
              cleanedResult.push(content);
              console.error(e);
            }
          }
        }

        // Return proper tool result format for Claude
        return {
          type: 'tool_result',
          tool_use_id: toolId,
          content: cleanedResult
        };
      } catch (error) {
        console.error(
          `Remote tool execution failed (attempt ${currentRemoteRetries}/${maxRetries}):`,
          error
        );

        currentRemoteRetries++;
        if (currentRemoteRetries > maxRetries) {
          console.error(
            `Max remote tool execution retries reached for tool ${toolName}.`
          );
          return {
            type: 'tool_result',
            tool_use_id: toolId,
            content: `Error: ${error instanceof Error ? error.message : String(error)}`
          };
        }

        // Wait before retry
        await new Promise(resolve =>
          setTimeout(resolve, 1000 * currentRemoteRetries)
        );
      }
    }

    // This should never happen (while loop ensures it), but TypeScript needs a return
    throw new Error('Tool execution failed after all retries');
  }

  /**
   * Set the notebook context manager
   * @param contextManager The notebook context manager instance
   */
  public setContextManager(contextManager: any): void {
    this.notebookContextManager = contextManager;
    console.log('Notebook context manager set in ToolService');
  }

  /**
   * Get access to the notebook context manager
   * @returns The notebook context manager or null if not initialized
   */
  public getContextManager(): any {
    return this.notebookContextManager || null;
  }
}
