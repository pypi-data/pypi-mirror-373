import { AppStateService } from '../AppState';
import { extractNotebookVariables, filterKernelVariablesByNotebook } from './VariableExtractor';
import { KernelPreviewUtils } from './kernelPreview';

/**
 * Utility functions for kernel operations
 */
export class KernelUtils {
  /**
   * Set DB_URL environment variable in the current kernel
   * @param databaseUrl The database URL to set, or null to use from AppState
   */
  static setDbUrlInKernel(databaseUrl?: string | null): void {
    try {
      // Get database URL from parameter or AppState
      const dbUrl =
        databaseUrl ?? AppStateService.getState().settings.databaseUrl;

      console.log(
        '[KernelUtils] Attempting to set DB_URL in kernel:',
        dbUrl ? 'configured' : 'not configured'
      );
      console.log('[KernelUtils] Database URL value:', dbUrl);

      const toolService = AppStateService.getToolService();
      const kernel = toolService?.getCurrentNotebook()?.kernel;

      if (!kernel) {
        console.warn('[KernelUtils] No kernel available to set DB_URL');
        return;
      }

      if (dbUrl && dbUrl.trim() !== '') {
        const code = `
import os
os.environ['DB_URL'] = '${dbUrl.replace(/'/g, "\\'")}'
print(f"[KernelUtils] DB_URL environment variable set: {os.environ.get('DB_URL', 'Not set')}")
        `;

        console.log(
          '[KernelUtils] Setting DB_URL environment variable in kernel. URL:',
          dbUrl.length > 50 ? dbUrl.substring(0, 50) + '...' : dbUrl
        );
        kernel.requestExecute({ code, silent: false });
      } else {
        // Remove DB_URL if empty
        const code = `
import os
if 'DB_URL' in os.environ:
    del os.environ['DB_URL']
    print("[KernelUtils] DB_URL environment variable removed")
else:
    print("[KernelUtils] DB_URL environment variable was not set")
        `;

        console.log(
          '[KernelUtils] Removing DB_URL environment variable from kernel'
        );
        kernel.requestExecute({ code, silent: false });
      }
    } catch (error) {
      console.error('[KernelUtils] Error setting DB_URL in kernel:', error);
    }
  }

  /**
   * Check current DB_URL in kernel
   */
  static checkDbUrlInKernel(): void {
    try {
      const toolService = AppStateService.getToolService();
      const kernel = toolService?.getCurrentNotebook()?.kernel;

      if (!kernel) {
        console.warn('[KernelUtils] No kernel available to check DB_URL');
        return;
      }

      const code = `
import os
db_url = os.environ.get('DB_URL')
print(f"[KernelUtils Check] Current DB_URL: {db_url}")
if db_url:
    print(f"[KernelUtils Check] DB_URL length: {len(db_url)}")
    print(f"[KernelUtils Check] DB_URL starts with: {db_url[:50]}...")
else:
    print("[KernelUtils Check] DB_URL is not set")
      `;

      console.log('[KernelUtils] Checking current DB_URL in kernel');
      kernel.requestExecute({ code, silent: false });
    } catch (error) {
      console.error('[KernelUtils] Error checking DB_URL in kernel:', error);
    }
  }

  /**
   * Debug AppState database URL
   */
  static debugAppStateDatabaseUrl(): void {
    try {
      const appState = AppStateService.getState();
      console.log('[KernelUtils] AppState settings:', appState.settings);
      console.log(
        '[KernelUtils] Database URL from AppState:',
        appState.settings.databaseUrl
      );
      console.log(
        '[KernelUtils] Database URL type:',
        typeof appState.settings.databaseUrl
      );
      console.log(
        '[KernelUtils] Database URL length:',
        appState.settings.databaseUrl?.length
      );
    } catch (error) {
      console.error('[KernelUtils] Error debugging AppState:', error);
    }
  }

  // Guard to prevent multiple simultaneous retry attempts
  private static isRetrying = false;

  /**
   * Set DB_URL with retry mechanism for when kernel is not ready
   * @param databaseUrl The database URL to set
   * @param maxRetries Maximum number of retry attempts
   * @param delay Delay between retries in ms
   */
  static async setDbUrlInKernelWithRetry(
    databaseUrl?: string | null,
    maxRetries: number = 3,
    delay: number = 1000
  ): Promise<void> {
    if (this.isRetrying) {
      console.log(
        '[KernelUtils] Already retrying DB_URL setup, skipping duplicate attempt'
      );
      return;
    }

    this.isRetrying = true;
    console.log('[KernelUtils] Starting DB_URL retry process...');
    this.debugAppStateDatabaseUrl();

    try {
      for (let i = 0; i < maxRetries; i++) {
        try {
          const toolService = AppStateService.getToolService();
          const kernel = toolService?.getCurrentNotebook()?.kernel;

          if (kernel) {
            console.log(
              `[KernelUtils] Kernel available on attempt ${i + 1}, setting DB_URL`
            );
            this.setDbUrlInKernel(databaseUrl);
            console.log(
              '[KernelUtils] DB_URL retry process completed successfully'
            );
            return;
          } else {
            console.log(
              `[KernelUtils] Kernel not ready, attempt ${i + 1}/${maxRetries}, waiting ${delay}ms...`
            );
            if (i < maxRetries - 1) {
              await new Promise(resolve => setTimeout(resolve, delay));
            }
          }
        } catch (error) {
          console.error(`[KernelUtils] Error on attempt ${i + 1}:`, error);
          if (i < maxRetries - 1) {
            await new Promise(resolve => setTimeout(resolve, delay));
          }
        }
      }

      console.warn(
        '[KernelUtils] Failed to set DB_URL after all retry attempts'
      );
    } finally {
      this.isRetrying = false;
    }
  }

  /**
   * Gets a preview of all variables, dicts, and objects in the current kernel
   */
  static async getKernelPreview(): Promise<string | null> {
    return KernelPreviewUtils.getKernelPreview();
  }
}
