import { BehaviorSubject } from 'rxjs';
import { DatabaseTools } from '../BackendTools/DatabaseTools';
import { AppStateService } from '../AppState';
import { StateDBCachingService } from '../utils/stateDBCaching';
import { CachingService, SETTING_KEYS } from '../utils/caching';

export interface DatabaseMetadata {
  schema: string;
  lastUpdated: number;
  url: string;
}

/**
 * Service for caching database metadata to avoid refetching on every message
 */
export class DatabaseMetadataCache {
  private static instance: DatabaseMetadataCache | null = null;
  private cache: DatabaseMetadata | null = null;
  private refreshTimer: NodeJS.Timeout | null = null;
  private readonly CACHE_DURATION_MS = 15 * 60 * 1000; // 15 minutes
  private readonly CACHE_KEY = 'database-metadata';

  // Observable for cache updates
  private metadataSubject = new BehaviorSubject<DatabaseMetadata | null>(null);
  public metadata$ = this.metadataSubject.asObservable();

  private constructor() {
    this.loadCacheFromStateDB();
    this.startAutoRefresh();
  }

  public static getInstance(): DatabaseMetadataCache {
    if (!DatabaseMetadataCache.instance) {
      DatabaseMetadataCache.instance = new DatabaseMetadataCache();
    }
    return DatabaseMetadataCache.instance;
  }

  /**
   * Get database URL from settings with comprehensive fallback strategy
   * This method tries multiple sources to ensure we get the database URL even during initialization
   */
  private async getDatabaseUrl(): Promise<string> {
    try {
      // Method 1: Try to get from settings registry directly (most reliable)
      if (CachingService.isAvailable()) {
        try {
          const url = await CachingService.getStringSetting(SETTING_KEYS.DATABASE_URL, '');
          if (url && url.trim() !== '') {
            console.log('[DatabaseMetadataCache] Retrieved database URL from settings registry:', url.length > 50 ? url.substring(0, 50) + '...' : url);
            return url;
          }
        } catch (settingsError) {
          console.warn('[DatabaseMetadataCache] Failed to get database URL from settings registry:', settingsError);
        }
      } else {
        console.log('[DatabaseMetadataCache] Settings registry not available, trying AppState');
      }
      
      // Method 2: Try to get from AppState settings
      try {
        const appStateUrl = AppStateService.getState().settings.databaseUrl;
        if (appStateUrl && appStateUrl.trim() !== '') {
          console.log('[DatabaseMetadataCache] Retrieved database URL from AppState:', appStateUrl.length > 50 ? appStateUrl.substring(0, 50) + '...' : appStateUrl);
          return appStateUrl;
        }
      } catch (appStateError) {
        console.warn('[DatabaseMetadataCache] Failed to get database URL from AppState:', appStateError);
      }
      
      // Method 3: Try to get settings registry directly from AppState and load manually
      try {
        const settingsRegistry = AppStateService.getSettingsRegistry();
        if (settingsRegistry) {
          const settings = await settingsRegistry.load('sage-agent-internal:plugin');
          const databaseUrl = settings.get('databaseUrl').composite as string;
          if (databaseUrl && databaseUrl.trim() !== '') {
            console.log('[DatabaseMetadataCache] Retrieved database URL from direct settings registry access:', databaseUrl.length > 50 ? databaseUrl.substring(0, 50) + '...' : databaseUrl);
            return databaseUrl;
          }
        }
      } catch (directSettingsError) {
        console.warn('[DatabaseMetadataCache] Failed to get database URL from direct settings access:', directSettingsError);
      }
      
      console.log('[DatabaseMetadataCache] No database URL found from any source');
      return '';
    } catch (error) {
      console.error('[DatabaseMetadataCache] Unexpected error getting database URL:', error);
      return '';
    }
  }

  /**
   * Get cached metadata or fetch if needed
   */
  public async getMetadata(): Promise<string | null> {
    const currentUrl = await this.getDatabaseUrl();

    if (!currentUrl || currentUrl.trim() === '') {
      return null;
    }

    // Check if cache is valid
    if (this.isCacheValid(currentUrl)) {
      console.log('[DatabaseMetadataCache] Using cached metadata');
      return this.cache!.schema;
    }

    // Fetch new metadata
    return await this.refreshMetadata(currentUrl);
  }

  /**
   * Get only cached metadata without attempting to refresh
   */
  public async getCachedMetadata(): Promise<string | null> {
    const currentUrl = await this.getDatabaseUrl();

    if (!currentUrl || currentUrl.trim() === '') {
      return null;
    }

    // Only return if cache is valid, never refresh
    if (this.isCacheValid(currentUrl)) {
      console.log('[DatabaseMetadataCache] Using cached metadata (no refresh)');
      return this.cache!.schema;
    }

    console.log('[DatabaseMetadataCache] No valid cached metadata available');
    return null;
  }

  /**
   * Check if a kernel is available for database operations
   */
  private async isKernelAvailable(): Promise<boolean> {
    try {
      const toolService = AppStateService.getToolService();
      const currentNotebook = toolService?.getCurrentNotebook();
      const kernel = currentNotebook?.kernel;
      
      if (!kernel) {
        console.log('[DatabaseMetadataCache] No kernel available');
        return false;
      }
      
      // Check if kernel is ready
      if (kernel.status !== 'idle' && kernel.status !== 'busy') {
        console.log('[DatabaseMetadataCache] Kernel not ready, status:', kernel.status);
        return false;
      }
      
      console.log('[DatabaseMetadataCache] Kernel is available and ready');
      return true;
    } catch (error) {
      console.warn('[DatabaseMetadataCache] Error checking kernel availability:', error);
      return false;
    }
  }

  /**
   * Wait for kernel to become available with timeout
   */
  private async waitForKernel(maxWaitMs: number = 30000): Promise<boolean> {
    const startTime = Date.now();
    const checkInterval = 1000; // Check every 1 second
    
    console.log('[DatabaseMetadataCache] Waiting for kernel to become available...');
    
    while (Date.now() - startTime < maxWaitMs) {
      if (await this.isKernelAvailable()) {
        console.log('[DatabaseMetadataCache] Kernel is now available');
        return true;
      }
      
      // Wait before next check
      await new Promise(resolve => setTimeout(resolve, checkInterval));
    }
    
    console.warn('[DatabaseMetadataCache] Timeout waiting for kernel to become available');
    return false;
  }

  /**
   * Force refresh the metadata
   */
  public async refreshMetadata(url?: string): Promise<string | null> {
    const databaseUrl = url || await this.getDatabaseUrl();

    if (!databaseUrl || databaseUrl.trim() === '') {
      this.clearCache();
      return null;
    }

    console.log('[DatabaseMetadataCache] Fetching fresh database metadata...');

    // Check if kernel is available before attempting to fetch metadata
    const kernelAvailable = await this.isKernelAvailable();
    if (!kernelAvailable) {
      console.log('[DatabaseMetadataCache] Kernel not available, waiting...');
      const kernelReady = await this.waitForKernel(15000); // Wait up to 15 seconds
      
      if (!kernelReady) {
        const errorMsg = 'Kernel not available after waiting - database metadata fetch skipped';
        console.warn('[DatabaseMetadataCache]', errorMsg);
        // Don't clear cache in this case, just return null and try again later
        return null;
      }
    }

    try {
      const databaseTools = new DatabaseTools();
      const schemaText =
        await databaseTools.getDatabaseMetadataAsText(databaseUrl);

      if (schemaText && !schemaText.startsWith('Error:')) {
        this.cache = {
          schema: schemaText,
          lastUpdated: Date.now(),
          url: databaseUrl
        };

        this.metadataSubject.next(this.cache);
        await this.saveCacheToStateDB();
        console.log(
          '[DatabaseMetadataCache] Database metadata cached successfully'
        );
        return schemaText;
      } else {
        console.warn(
          '[DatabaseMetadataCache] Failed to fetch database metadata:',
          schemaText
        );
        this.clearCache();
        return null;
      }
    } catch (error) {
      console.error(
        '[DatabaseMetadataCache] Error fetching database metadata:',
        error
      );
      
      // If it's a kernel-related error, don't clear cache - just try again later
      const errorString = error?.toString() || '';
      if (errorString.includes('kernel') || errorString.includes('No kernel available')) {
        console.log('[DatabaseMetadataCache] Kernel-related error, will retry later');
        return null;
      }
      
      this.clearCache();
      return null;
    }
  }

  /**
   * Check if current cache is valid
   */
  private isCacheValid(currentUrl: string): boolean {
    if (!this.cache) {
      return false;
    }

    // Check if URL changed
    if (this.cache.url !== currentUrl) {
      return false;
    }

    // Check if cache expired
    const now = Date.now();
    const cacheAge = now - this.cache.lastUpdated;
    return cacheAge < this.CACHE_DURATION_MS;
  }

  /**
   * Clear the cache
   */
  public clearCache(): void {
    this.cache = null;
    this.metadataSubject.next(null);
    this.clearCacheFromStateDB();
    console.log('[DatabaseMetadataCache] Cache cleared');
  }

  /**
   * Load cache from StateDB on initialization
   */
  private async loadCacheFromStateDB(): Promise<void> {
    try {
      const cachedData =
        await StateDBCachingService.getObjectValue<DatabaseMetadata | null>(
          this.CACHE_KEY,
          null
        );

      if (cachedData) {
        this.cache = cachedData;
        this.metadataSubject.next(this.cache);
        console.log('[DatabaseMetadataCache] Loaded cache from StateDB');
      }
    } catch (error) {
      console.error(
        '[DatabaseMetadataCache] Failed to load cache from StateDB:',
        error
      );
    }
  }

  /**
   * Save cache to StateDB
   */
  private async saveCacheToStateDB(): Promise<void> {
    if (!this.cache) return;

    try {
      await StateDBCachingService.setObjectValue(this.CACHE_KEY, this.cache);
    } catch (error) {
      console.error(
        '[DatabaseMetadataCache] Failed to save cache to StateDB:',
        error
      );
    }
  }

  /**
   * Clear cache from StateDB
   */
  private async clearCacheFromStateDB(): Promise<void> {
    try {
      await StateDBCachingService.removeValue(this.CACHE_KEY);
    } catch (error) {
      console.error(
        '[DatabaseMetadataCache] Failed to clear cache from StateDB:',
        error
      );
    }
  }

  /**
   * Start auto-refresh timer
   */
  private startAutoRefresh(): void {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
    }

    this.refreshTimer = setInterval(async () => {
      try {
        const currentUrl = await this.getDatabaseUrl();
        if (currentUrl && currentUrl.trim() !== '' && this.cache) {
          // Only attempt auto-refresh if kernel is available
          const kernelAvailable = await this.isKernelAvailable();
          if (kernelAvailable) {
            console.log(
              '[DatabaseMetadataCache] Auto-refreshing database metadata...'
            );
            await this.refreshMetadata(currentUrl);
          } else {
            console.log(
              '[DatabaseMetadataCache] Skipping auto-refresh - kernel not available'
            );
          }
        }
      } catch (error) {
        console.warn('[DatabaseMetadataCache] Auto-refresh failed:', error);
      }
    }, this.CACHE_DURATION_MS);
  }

  /**
   * Stop auto-refresh timer
   */
  public stopAutoRefresh(): void {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
      this.refreshTimer = null;
    }
  }

  /**
   * Initialize cache on startup (async, non-blocking) with retry mechanism
   */
  public async initializeOnStartup(): Promise<void> {
    console.log('[DatabaseMetadataCache] Starting initialization...');
    
    // Wait a bit for settings and notebooks to load (non-blocking)
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    try {
      const databaseUrl = await this.getDatabaseUrl();
      console.log('[DatabaseMetadataCache] Retrieved database URL during initialization:', databaseUrl ? 'configured' : 'not configured');
      
      if (databaseUrl && databaseUrl.trim() !== '') {
        console.log('[DatabaseMetadataCache] Database URL is configured, attempting to fetch metadata...');
        
        // Check if kernel is available before initial attempt
        const kernelAvailable = await this.isKernelAvailable();
        if (!kernelAvailable) {
          console.log('[DatabaseMetadataCache] Kernel not available during initialization, scheduling retry...');
          
          // Schedule retries with increasing delays
          this.scheduleRetryWithBackoff(databaseUrl, 1);
        } else {
          // Kernel is available, try to fetch metadata
          this.refreshMetadata(databaseUrl).catch(error => {
            console.warn(
              '[DatabaseMetadataCache] Startup initialization failed:',
              error
            );
            
            // Schedule retry on failure
            this.scheduleRetryWithBackoff(databaseUrl, 1);
          });
        }
      } else {
        console.log('[DatabaseMetadataCache] No database URL configured, skipping initialization');
        
        // Set up a delayed retry in case settings load later
        setTimeout(async () => {
          console.log('[DatabaseMetadataCache] Checking for database URL after delay...');
          try {
            const delayedUrl = await this.getDatabaseUrl();
            if (delayedUrl && delayedUrl.trim() !== '') {
              console.log('[DatabaseMetadataCache] Database URL found after delay, initializing...');
              const kernelReady = await this.waitForKernel(10000);
              if (kernelReady) {
                await this.refreshMetadata(delayedUrl);
              } else {
                this.scheduleRetryWithBackoff(delayedUrl, 1);
              }
            }
          } catch (delayedError) {
            console.warn('[DatabaseMetadataCache] Delayed initialization check failed:', delayedError);
          }
        }, 15000); // Check again after 15 seconds
      }
    } catch (error) {
      console.error('[DatabaseMetadataCache] Error during initialization:', error);
    }
  }

  /**
   * Schedule a retry with exponential backoff
   */
  private scheduleRetryWithBackoff(databaseUrl: string, attempt: number, maxAttempts: number = 5): void {
    if (attempt > maxAttempts) {
      console.warn('[DatabaseMetadataCache] Max retry attempts reached, giving up');
      return;
    }
    
    const delay = Math.min(5000 * Math.pow(2, attempt - 1), 60000); // Exponential backoff, max 1 minute
    console.log(`[DatabaseMetadataCache] Scheduling retry attempt ${attempt} in ${delay}ms`);
    
    setTimeout(async () => {
      console.log(`[DatabaseMetadataCache] Retry attempt ${attempt} starting...`);
      
      try {
        // Check for updated database URL
        const currentUrl = await this.getDatabaseUrl();
        const urlToUse = currentUrl && currentUrl.trim() !== '' ? currentUrl : databaseUrl;
        
        if (!urlToUse || urlToUse.trim() === '') {
          console.log('[DatabaseMetadataCache] No database URL available for retry');
          return;
        }
        
        // Wait for kernel to be available
        const kernelReady = await this.waitForKernel(20000); // Wait up to 20 seconds for retry
        if (!kernelReady) {
          console.log('[DatabaseMetadataCache] Kernel still not ready, scheduling next retry...');
          this.scheduleRetryWithBackoff(urlToUse, attempt + 1, maxAttempts);
          return;
        }
        
        // Try to fetch metadata
        const result = await this.refreshMetadata(urlToUse);
        if (result) {
          console.log('[DatabaseMetadataCache] Retry successful!');
        } else {
          console.log('[DatabaseMetadataCache] Retry failed, scheduling next attempt...');
          this.scheduleRetryWithBackoff(urlToUse, attempt + 1, maxAttempts);
        }
      } catch (retryError) {
        console.warn(`[DatabaseMetadataCache] Retry attempt ${attempt} failed:`, retryError);
        this.scheduleRetryWithBackoff(databaseUrl, attempt + 1, maxAttempts);
      }
    }, delay);
  }

  /**
   * Get cache status for UI display
   */
  public getCacheStatus(): {
    isCached: boolean;
    lastUpdated: number | null;
    isExpired: boolean;
  } {
    if (!this.cache) {
      return { isCached: false, lastUpdated: null, isExpired: false };
    }

    const now = Date.now();
    const cacheAge = now - this.cache.lastUpdated;
    const isExpired = cacheAge >= this.CACHE_DURATION_MS;

    return {
      isCached: true,
      lastUpdated: this.cache.lastUpdated,
      isExpired
    };
  }

  /**
   * Handle settings change events - reinitialize if database URL changed
   */
  public async onSettingsChanged(): Promise<void> {
    console.log('[DatabaseMetadataCache] Settings changed, checking database URL...');
    try {
      const currentUrl = await this.getDatabaseUrl();
      
      // Check if URL changed from cached version
      if (this.cache && this.cache.url !== currentUrl) {
        console.log('[DatabaseMetadataCache] Database URL changed, clearing cache and reinitializing...');
        this.clearCache();
        
        if (currentUrl && currentUrl.trim() !== '') {
          // Check kernel availability before refreshing
          const kernelAvailable = await this.isKernelAvailable();
          if (kernelAvailable) {
            // Refresh with new URL
            this.refreshMetadata(currentUrl).catch(error => {
              console.warn('[DatabaseMetadataCache] Failed to refresh after settings change:', error);
            });
          } else {
            console.log('[DatabaseMetadataCache] Kernel not available after settings change, scheduling retry...');
            this.scheduleRetryWithBackoff(currentUrl, 1);
          }
        }
      } else if (!this.cache && currentUrl && currentUrl.trim() !== '') {
        console.log('[DatabaseMetadataCache] Database URL configured but no cache, initializing...');
        // No cache but URL is configured - initialize
        const kernelAvailable = await this.isKernelAvailable();
        if (kernelAvailable) {
          this.refreshMetadata(currentUrl).catch(error => {
            console.warn('[DatabaseMetadataCache] Failed to initialize after settings change:', error);
          });
        } else {
          console.log('[DatabaseMetadataCache] Kernel not available for initialization, scheduling retry...');
          this.scheduleRetryWithBackoff(currentUrl, 1);
        }
      }
    } catch (error) {
      console.error('[DatabaseMetadataCache] Error handling settings change:', error);
    }
  }

  /**
   * Trigger initialization when kernel becomes available
   * This can be called from external systems when they detect kernel readiness
   */
  public async onKernelReady(): Promise<void> {
    console.log('[DatabaseMetadataCache] Kernel ready event received, checking for pending initialization...');
    
    try {
      const databaseUrl = await this.getDatabaseUrl();
      
      if (databaseUrl && databaseUrl.trim() !== '') {
        // If we don't have cached metadata or it's expired, try to refresh
        if (!this.cache || !this.isCacheValid(databaseUrl)) {
          console.log('[DatabaseMetadataCache] Attempting to refresh metadata now that kernel is ready...');
          await this.refreshMetadata(databaseUrl);
        } else {
          console.log('[DatabaseMetadataCache] Cache is valid, no refresh needed');
        }
      } else {
        console.log('[DatabaseMetadataCache] No database URL configured, skipping kernel ready handler');
      }
    } catch (error) {
      console.error('[DatabaseMetadataCache] Error handling kernel ready event:', error);
    }
  }

  /**
   * Clean up resources
   */
  public dispose(): void {
    this.stopAutoRefresh();
    this.clearCache();
  }
}
