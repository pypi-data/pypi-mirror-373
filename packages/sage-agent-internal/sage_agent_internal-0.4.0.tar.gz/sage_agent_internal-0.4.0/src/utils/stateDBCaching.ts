import { IStateDB } from '@jupyterlab/statedb';
import { PartialJSONValue } from '@lumino/coreutils';

/**
 * Utility class for managing chat-specific data through JupyterLab's IStateDB
 * instead of ISettingsRegistry. This provides better performance and isolation
 * for chat history data which can be large and frequently updated.
 */
export class StateDBCachingService {
  private static stateDB: IStateDB | null = null;
  private static readonly NAMESPACE = 'sage-agent-internal';

  /**
   * Initialize the state DB caching service
   */
  public static initialize(stateDB: IStateDB | null): void {
    StateDBCachingService.stateDB = stateDB;
  }

  /**
   * Get a value from the state database
   * @param key The setting key
   * @param defaultValue The default value if setting doesn't exist
   * @returns The setting value or default
   */
  public static async getValue<T>(key: string, defaultValue: T): Promise<T> {
    if (!StateDBCachingService.stateDB) {
      console.warn(
        '[StateDBCachingService] State DB not initialized, using default value'
      );
      return defaultValue;
    }

    try {
      const fullKey = `${StateDBCachingService.NAMESPACE}:${key}`;
      const value = await StateDBCachingService.stateDB.fetch(fullKey);
      return value !== undefined ? (value as T) : defaultValue;
    } catch (error) {
      console.warn(
        `[StateDBCachingService] Failed to get value '${key}':`,
        error
      );
      return defaultValue;
    }
  }

  /**
   * Set a value in the state database
   * @param key The setting key
   * @param value The value to set
   */
  public static async setValue(
    key: string,
    value: PartialJSONValue
  ): Promise<void> {
    if (!StateDBCachingService.stateDB) {
      console.warn(
        '[StateDBCachingService] State DB not initialized, cannot set value'
      );
      return;
    }

    try {
      const fullKey = `${StateDBCachingService.NAMESPACE}:${key}`;
      await StateDBCachingService.stateDB.save(fullKey, value);
    } catch (error) {
      console.error(
        `[StateDBCachingService] Failed to set value '${key}':`,
        error
      );
    }
  }

  /**
   * Remove a value from the state database
   * @param key The setting key to remove
   */
  public static async removeValue(key: string): Promise<void> {
    if (!StateDBCachingService.stateDB) {
      console.warn(
        '[StateDBCachingService] State DB not initialized, cannot remove value'
      );
      return;
    }

    try {
      const fullKey = `${StateDBCachingService.NAMESPACE}:${key}`;
      await StateDBCachingService.stateDB.remove(fullKey);
    } catch (error) {
      console.error(
        `[StateDBCachingService] Failed to remove value '${key}':`,
        error
      );
    }
  }

  /**
   * Get an object value (for complex data like arrays, objects)
   */
  public static async getObjectValue<T>(
    key: string,
    defaultValue: T
  ): Promise<T> {
    return StateDBCachingService.getValue(key, defaultValue);
  }

  /**
   * Set an object value (for complex data like arrays, objects)
   */
  public static async setObjectValue<T>(key: string, value: T): Promise<void> {
    return StateDBCachingService.setValue(key, value as PartialJSONValue);
  }

  /**
   * Check if the state DB is available
   */
  public static isAvailable(): boolean {
    return StateDBCachingService.stateDB !== null;
  }

  /**
   * List all keys in the namespace (for debugging purposes)
   */
  public static async listKeys(): Promise<string[]> {
    if (!StateDBCachingService.stateDB) {
      return [];
    }

    try {
      const allKeys = await StateDBCachingService.stateDB.list(
        StateDBCachingService.NAMESPACE
      );
      return allKeys.ids.map(id =>
        id.replace(`${StateDBCachingService.NAMESPACE}:`, '')
      );
    } catch (error) {
      console.error('[StateDBCachingService] Failed to list keys:', error);
      return [];
    }
  }
}

// State DB key constants for chat-related data
export const STATE_DB_KEYS = {
  // Chat settings
  CHAT_HISTORIES: 'chatHistories',
  // Error logging
  ERROR_LOGS: 'errorLogs',
  // Snippets
  SNIPPETS: 'snippets',
  // Inserted snippets
  INSERTED_SNIPPETS: 'insertedSnippets'
} as const;
