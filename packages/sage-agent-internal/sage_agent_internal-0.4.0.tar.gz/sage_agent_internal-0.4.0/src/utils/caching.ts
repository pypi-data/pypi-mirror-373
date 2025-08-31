import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { PartialJSONValue } from '@lumino/coreutils';

/**
 * Utility class for managing settings through JupyterLab's settings registry
 * instead of localStorage. This provides a centralized way to handle all
 * application settings with proper persistence.
 */
export class CachingService {
  private static settingsRegistry: ISettingRegistry | null = null;
  private static readonly PLUGIN_ID = 'sage-agent-internal:plugin';

  /**
   * Initialize the caching service with the settings registry
   */
  public static initialize(settingsRegistry: ISettingRegistry | null): void {
    CachingService.settingsRegistry = settingsRegistry;
  }

  /**
   * Get a setting value from the registry
   * @param key The setting key
   * @param defaultValue The default value if setting doesn't exist
   * @returns The setting value or default
   */
  public static async getSetting<T>(key: string, defaultValue: T): Promise<T> {
    if (!CachingService.settingsRegistry) {
      console.warn(
        '[CachingService] Settings registry not initialized, using default value'
      );
      return defaultValue;
    }

    try {
      const settings = await CachingService.settingsRegistry.load(
        CachingService.PLUGIN_ID
      );
      const value = settings.get(key).composite as T;
      return value !== undefined ? value : defaultValue;
    } catch (error) {
      console.warn(`[CachingService] Failed to get setting '${key}':`, error);
      return defaultValue;
    }
  }

  /**
   * Set a setting value in the registry
   * @param key The setting key
   * @param value The value to set
   */
  public static async setSetting(
    key: string,
    value: PartialJSONValue
  ): Promise<void> {
    if (!CachingService.settingsRegistry) {
      console.warn(
        '[CachingService] Settings registry not initialized, cannot set setting'
      );
      return;
    }

    try {
      const settings = await CachingService.settingsRegistry.load(
        CachingService.PLUGIN_ID
      );
      await settings.set(key, value);
      await settings.save(settings.raw);
    } catch (error) {
      console.error(`[CachingService] Failed to set setting '${key}':`, error);
    }
  }

  /**
   * Remove a setting from the registry
   * @param key The setting key to remove
   */
  public static async removeSetting(key: string): Promise<void> {
    if (!CachingService.settingsRegistry) {
      console.warn(
        '[CachingService] Settings registry not initialized, cannot remove setting'
      );
      return;
    }

    try {
      const settings = await CachingService.settingsRegistry.load(
        CachingService.PLUGIN_ID
      );
      await settings.remove(key);
      await settings.save(settings.raw);
    } catch (error) {
      console.error(
        `[CachingService] Failed to remove setting '${key}':`,
        error
      );
    }
  }

  /**
   * Get a boolean setting
   */
  public static async getBooleanSetting(
    key: string,
    defaultValue: boolean = false
  ): Promise<boolean> {
    return CachingService.getSetting(key, defaultValue);
  }

  /**
   * Set a boolean setting
   */
  public static async setBooleanSetting(
    key: string,
    value: boolean
  ): Promise<void> {
    return CachingService.setSetting(key, value);
  }

  /**
   * Get a string setting
   */
  public static async getStringSetting(
    key: string,
    defaultValue: string = ''
  ): Promise<string> {
    return CachingService.getSetting(key, defaultValue);
  }

  /**
   * Set a string setting
   */
  public static async setStringSetting(
    key: string,
    value: string
  ): Promise<void> {
    return CachingService.setSetting(key, value);
  }

  /**
   * Get an object setting (for complex data like arrays, objects)
   */
  public static async getObjectSetting<T>(
    key: string,
    defaultValue: T
  ): Promise<T> {
    return CachingService.getSetting(key, defaultValue);
  }

  /**
   * Set an object setting (for complex data like arrays, objects)
   */
  public static async setObjectSetting<T>(
    key: string,
    value: T
  ): Promise<void> {
    return CachingService.setSetting(key, value as PartialJSONValue);
  }

  /**
   * Check if the settings registry is available
   */
  public static isAvailable(): boolean {
    return CachingService.settingsRegistry !== null;
  }

  /**
   * Get all settings for debugging purposes
   */
  public static async getAllSettings(): Promise<Record<string, any>> {
    if (!CachingService.settingsRegistry) {
      return {};
    }

    try {
      const settings = await CachingService.settingsRegistry.load(
        CachingService.PLUGIN_ID
      );
      return settings.composite as Record<string, any>;
    } catch (error) {
      console.error('[CachingService] Failed to get all settings:', error);
      return {};
    }
  }
}

// Setting key constants
export const SETTING_KEYS = {
  // Theme settings
  DARK_THEME_APPLIED: 'darkThemeApplied',

  // Update banner settings
  UPDATE_DECLINED_VERSION: 'updateDeclinedVersion',

  // Chat settings
  CHAT_HISTORIES: 'chatHistories',

  // Codebase settings
  CODEBASES: 'codebases',

  // User preferences
  SAGE_TOKEN_MODE: 'sageTokenMode',
  TAB_AUTOCOMPLETE_ENABLED: 'tabAutocompleteEnabled',
  CLAUDE_API_KEY: 'claudeApiKey',
  CLAUDE_MODEL_ID: 'claudeModelId',
  CLAUDE_MODEL_URL: 'claudeModelUrl',
  DATABASE_URL: 'databaseUrl'
} as const;
