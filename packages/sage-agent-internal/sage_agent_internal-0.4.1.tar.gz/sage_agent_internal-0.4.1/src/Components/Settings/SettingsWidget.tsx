import * as React from 'react';
import { Widget } from '@lumino/widgets';
import { ReactWidget } from '@jupyterlab/ui-components';
import { ISignal, Signal } from '@lumino/signaling';
import { ToolService } from '../../Services/ToolService';
import { CodebaseManager } from '../../CodebaseManager';
import { AppStateService } from '../../AppState';
import { CachingService, SETTING_KEYS } from '../../utils/caching';
import { KernelUtils } from '../../utils/kernelUtils';
import { DatabaseMetadataCache } from '../../Services/DatabaseMetadataCache';

/**
 * Interface for the Settings state
 */
export interface ISettingsState {
  isVisible: boolean;
  sageTokenMode: boolean;
  tabAutocompleteEnabled: boolean;
  claudeApiKey: string;
  claudeModelId: string;
  claudeModelUrl: string;
  databaseUrl: string;
}

/**
 * React component for displaying Settings content
 */
function SettingsContent({
  isVisible,
  sageTokenMode,
  tabAutocompleteEnabled,
  claudeApiKey,
  claudeModelId,
  claudeModelUrl,
  databaseUrl,
  onTokenModeChange,
  onTabAutocompleteChange,
  onClaudeApiKeyChange,
  onClaudeModelIdChange,
  onClaudeModelUrlChange,
  onDatabaseUrlChange,
  toolService
}: {
  isVisible: boolean;
  sageTokenMode: boolean;
  tabAutocompleteEnabled: boolean;
  claudeApiKey: string;
  claudeModelId: string;
  claudeModelUrl: string;
  databaseUrl: string;
  onTokenModeChange: (enabled: boolean) => void;
  onTabAutocompleteChange: (enabled: boolean) => void;
  onClaudeApiKeyChange: (value: string) => void;
  onClaudeModelIdChange: (value: string) => void;
  onClaudeModelUrlChange: (value: string) => void;
  onDatabaseUrlChange: (value: string) => void;
  toolService: ToolService;
}): JSX.Element | null {
  const [codebaseManager, setCodebaseManager] =
    React.useState<CodebaseManager | null>(null);
  const codebaseContainerRef = React.useRef<HTMLDivElement>(null);
  const [isApiKeyFocused, setIsApiKeyFocused] = React.useState<boolean>(false);
  const [isDatabaseUrlFocused, setIsDatabaseUrlFocused] =
    React.useState<boolean>(false);

  // Database cache state
  const [cacheStatus, setCacheStatus] = React.useState<{
    isCached: boolean;
    lastUpdated: number | null;
    isExpired: boolean;
  }>({ isCached: false, lastUpdated: null, isExpired: false });
  const [isRefreshing, setIsRefreshing] = React.useState<boolean>(false);

  // Get database cache instance
  const databaseCache = React.useMemo(
    () => DatabaseMetadataCache.getInstance(),
    []
  );

  // Update cache status periodically
  React.useEffect(() => {
    const updateCacheStatus = () => {
      setCacheStatus(databaseCache.getCacheStatus());
    };

    // Initial update
    updateCacheStatus();

    // Subscribe to cache updates
    const subscription = databaseCache.metadata$.subscribe(() => {
      updateCacheStatus();
    });

    // Update status every second to show accurate time
    const interval = setInterval(updateCacheStatus, 1000);

    return () => {
      subscription.unsubscribe();
      clearInterval(interval);
    };
  }, [databaseCache]);

  // Handle database metadata refresh
  const handleRefreshMetadata = async () => {
    if (!databaseUrl || databaseUrl.trim() === '' || isRefreshing) {
      return;
    }

    setIsRefreshing(true);
    try {
      await databaseCache.refreshMetadata(databaseUrl);
    } catch (error) {
      console.error(
        '[SettingsWidget] Failed to refresh database metadata:',
        error
      );
    } finally {
      setIsRefreshing(false);
    }
  };

  // Format last updated time
  const formatLastUpdated = (timestamp: number | null): string => {
    if (!timestamp) return 'Never';

    const now = Date.now();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / 60000);
    const seconds = Math.floor((diff % 60000) / 1000);

    if (minutes > 0) {
      return `${minutes}m ${seconds}s ago`;
    } else {
      return `${seconds}s ago`;
    }
  };

  // Initialize codebase manager when toolService is available
  React.useEffect(() => {
    if (toolService && codebaseContainerRef.current && !codebaseManager) {
      const manager = new CodebaseManager(toolService);
      setCodebaseManager(manager);
      codebaseContainerRef.current.appendChild(manager.getElement());
    }
  }, [toolService, codebaseManager]);

  // Cleanup codebase manager on unmount
  React.useEffect(() => {
    return () => {
      if (codebaseManager && codebaseContainerRef.current) {
        const element = codebaseManager.getElement();
        if (element.parentNode) {
          element.parentNode.removeChild(element);
        }
      }
    };
  }, [codebaseManager]);

  if (!isVisible) {
    return null;
  }

  const handleTokenModeChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    onTokenModeChange(event.target.checked);
  };

  const handleTabAutocompleteChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    onTabAutocompleteChange(event.target.checked);
  };

  return (
    <div className="sage-ai-settings-container">
      <h2 className="sage-ai-settings-title">Sage Settings</h2>

      {/* Codebase Manager Container */}
      <div ref={codebaseContainerRef} />

      {/* Claude API Configuration */}
      <div className="sage-ai-config-section">
        <h3 className="sage-ai-config-title">API Configuration</h3>

        <div className="sage-ai-field-container">
          <label className="sage-ai-field-label">Sage API Key:</label>
          <input
            type={isApiKeyFocused ? 'text' : 'password'}
            value={claudeApiKey}
            onChange={e => onClaudeApiKeyChange(e.target.value)}
            onFocus={() => setIsApiKeyFocused(true)}
            onBlur={() => setIsApiKeyFocused(false)}
            placeholder="Enter your Sage API key"
            className="sage-ai-field-input"
          />
        </div>

        <div className="sage-ai-field-container">
          <label className="sage-ai-field-label">Sage Model ID:</label>
          <input
            type="text"
            value={claudeModelId}
            onChange={e => onClaudeModelIdChange(e.target.value)}
            placeholder="claude-sonnet-4-20250514"
            className="sage-ai-field-input"
          />
        </div>

        <div className="sage-ai-field-container">
          <label className="sage-ai-field-label">Sage Model URL:</label>
          <input
            type="text"
            value={claudeModelUrl}
            onChange={e => onClaudeModelUrlChange(e.target.value)}
            placeholder="https://sage.alpinex.ai:8760"
            className="sage-ai-field-input"
          />
        </div>
      </div>

      {/* Database Configuration */}
      <div className="sage-ai-config-section">
        <h3 className="sage-ai-config-title">Database Configuration</h3>

        <div className="sage-ai-field-container">
          <label className="sage-ai-field-label">Database URL:</label>
          <div className="sage-ai-database-input-container">
            <input
              type={isDatabaseUrlFocused ? 'text' : 'password'}
              value={databaseUrl}
              onChange={e => onDatabaseUrlChange(e.target.value)}
              onFocus={() => setIsDatabaseUrlFocused(true)}
              onBlur={() => setIsDatabaseUrlFocused(false)}
              placeholder="Enter your database URL"
              className="sage-ai-field-input sage-ai-database-input"
            />
            <button
              onClick={handleRefreshMetadata}
              disabled={
                !databaseUrl || databaseUrl.trim() === '' || isRefreshing
              }
              className="sage-ai-refresh-button"
              title="Refresh database metadata cache"
            >
              {isRefreshing ? (
                <div className="sage-ai-db-metadata-spinner">
                  <div className="sage-ai-db-spinner-ring"></div>
                  <div className="sage-ai-db-spinner-pulse"></div>
                </div>
              ) : (
                '↻'
              )}
            </button>
          </div>

          {/* Cache Status */}
          <div className="sage-ai-cache-status">
            <span
              className={`sage-ai-cache-indicator ${cacheStatus.isCached ? (cacheStatus.isExpired ? 'expired' : 'cached') : 'not-cached'}`}
            >
              {cacheStatus.isCached
                ? cacheStatus.isExpired
                  ? '⚠️'
                  : '✓'
                : '○'}
            </span>
            <span className="sage-ai-cache-text">
              {cacheStatus.isCached
                ? `Metadata cached (${formatLastUpdated(cacheStatus.lastUpdated)})${cacheStatus.isExpired ? ' - Expired' : ''}`
                : 'No metadata cached'}
            </span>
          </div>
        </div>
      </div>

      {/* Sage Token Mode Checkbox */}
      <div className="sage-token-mode-container">
        <label className="sage-token-mode-label">
          <input
            type="checkbox"
            checked={sageTokenMode}
            onChange={handleTokenModeChange}
            className="sage-token-mode-checkbox"
          />
          <span>Sage Token Debug Mode</span>
        </label>
      </div>

      {/* Tab Autocomplete Checkbox */}
      <div className="sage-tab-autocomplete-container">
        <label className="sage-tab-autocomplete-label">
          <input
            type="checkbox"
            checked={tabAutocompleteEnabled}
            onChange={handleTabAutocompleteChange}
            className="sage-tab-autocomplete-checkbox"
          />
          <span>Enable Tab Autocomplete</span>
        </label>
      </div>
    </div>
  );
}

/**
 * React-based Widget that contains the settings for Sage AI
 */
export class SettingsWidget extends ReactWidget {
  private toolService: ToolService;
  private _state: ISettingsState;
  private _stateChanged = new Signal<this, ISettingsState>(this);
  public static SAGE_TOKEN_MODE: boolean = false;
  private static readonly SAGE_TOKEN_MODE_KEY = 'sage-ai-token-mode';
  private static readonly CLAUDE_API_KEY_KEY = 'sage-ai-claude-api-key';
  private static readonly CLAUDE_MODEL_ID_KEY = 'sage-ai-claude-model-id';
  private static readonly CLAUDE_MODEL_URL_KEY = 'sage-ai-claude-model-url';
  private static readonly DATABASE_URL_KEY = 'sage-ai-database-url';

  constructor(toolService: ToolService) {
    super();

    this.id = 'sage-ai-settings';
    this.title.label = 'Settings';
    this.title.closable = false;
    this.addClass('sage-ai-settings');

    this.toolService = toolService;

    // Initialize state with defaults, then load async
    this._state = {
      isVisible: true,
      sageTokenMode: false,
      tabAutocompleteEnabled: true,
      claudeApiKey: '',
      claudeModelId: 'claude-sonnet-4-20250514',
      claudeModelUrl: 'https://sage.alpinex.ai:8760',
      databaseUrl: ''
    };

    // Load settings asynchronously
    this.initializeSettings();
  }

  /**
   * Initialize settings from storage
   */
  private async initializeSettings(): Promise<void> {
    try {
      // Load cached settings from settings registry and update AppState
      await this.loadAndSyncSettings();

      // Get updated state from AppState
      const appSettings = AppStateService.getClaudeSettings();
      await this.loadTokenModeSetting(); // This sets SettingsWidget.SAGE_TOKEN_MODE
      await this.loadTabAutocompleteSetting(); // Load tab autocomplete setting
      const tokenMode = SettingsWidget.SAGE_TOKEN_MODE;

      // Update AppState with token mode and tab autocomplete
      AppStateService.updateSettings({ tokenMode });
      AppStateService.updateClaudeSettings({ 
        tabAutocompleteEnabled: this._state.tabAutocompleteEnabled 
      });

      // Update state
      this._state = {
        isVisible: true,
        sageTokenMode: tokenMode,
        tabAutocompleteEnabled: this._state.tabAutocompleteEnabled,
        claudeApiKey: appSettings.claudeApiKey,
        claudeModelId: appSettings.claudeModelId,
        claudeModelUrl: appSettings.claudeModelUrl,
        databaseUrl: appSettings.databaseUrl
      };

      this.update();
    } catch (error) {
      console.error('Failed to initialize settings:', error);
    }
  }

  /**
   * Get the signal that fires when state changes
   */
  public get stateChanged(): ISignal<this, ISettingsState> {
    return this._stateChanged;
  }

  /**
   * Render the React component
   */
  render(): JSX.Element {
    return (
      <SettingsContent
        isVisible={this._state.isVisible}
        sageTokenMode={this._state.sageTokenMode}
        tabAutocompleteEnabled={this._state.tabAutocompleteEnabled}
        claudeApiKey={this._state.claudeApiKey}
        claudeModelId={this._state.claudeModelId}
        claudeModelUrl={this._state.claudeModelUrl}
        databaseUrl={this._state.databaseUrl}
        onTokenModeChange={this.handleTokenModeChange.bind(this)}
        onTabAutocompleteChange={this.handleTabAutocompleteChange.bind(this)}
        onClaudeApiKeyChange={this.handleClaudeApiKeyChange.bind(this)}
        onClaudeModelIdChange={this.handleClaudeModelIdChange.bind(this)}
        onClaudeModelUrlChange={this.handleClaudeModelUrlChange.bind(this)}
        onDatabaseUrlChange={this.handleDatabaseUrlChange.bind(this)}
        toolService={this.toolService}
      />
    );
  }

  /**
   * Load the Sage Token Mode setting from settings registry
   */
  private async loadTokenModeSetting(): Promise<void> {
    const cached = await CachingService.getBooleanSetting(
      SETTING_KEYS.SAGE_TOKEN_MODE,
      false
    );
    SettingsWidget.SAGE_TOKEN_MODE = cached;
  }

  /**
   * Save the Sage Token Mode setting to settings registry
   */
  private async saveTokenModeSetting(value: boolean): Promise<void> {
    await CachingService.setBooleanSetting(SETTING_KEYS.SAGE_TOKEN_MODE, value);
  }

  /**
   * Load the Tab Autocomplete setting from settings registry
   */
  private async loadTabAutocompleteSetting(): Promise<void> {
    const cached = await CachingService.getBooleanSetting(
      SETTING_KEYS.TAB_AUTOCOMPLETE_ENABLED,
      true
    );
    this._state = { ...this._state, tabAutocompleteEnabled: cached };
  }

  /**
   * Save the Tab Autocomplete setting to settings registry
   */
  private async saveTabAutocompleteSetting(value: boolean): Promise<void> {
    await CachingService.setBooleanSetting(SETTING_KEYS.TAB_AUTOCOMPLETE_ENABLED, value);
  }

  /**
   * Generic method to load a setting from settings registry
   */
  private async loadSetting(
    key: string,
    defaultValue: string
  ): Promise<string> {
    return await CachingService.getStringSetting(key, defaultValue);
  }

  /**
   * Generic method to save a setting to settings registry
   */
  private async saveSetting(key: string, value: string): Promise<void> {
    await CachingService.setStringSetting(key, value);
  }

  /**
   * Load settings from settings registry and sync with AppState
   */
  private async loadAndSyncSettings(): Promise<void> {
    let claudeApiKey = await this.loadSetting(SETTING_KEYS.CLAUDE_API_KEY, '');

    // Try to load API key from optional_env.json only if not already set in settings registry
    if (!claudeApiKey || claudeApiKey.trim() === '') {
      try {
        const optionalEnv = require('../../Config/optional_env.json');
        if (optionalEnv.api_key) {
          claudeApiKey = optionalEnv.api_key;
          // Cache the API key from optional_env.json to the settings registry
          console.log(
            '[SettingsWidget] Caching API key from optional_env.json to settings registry'
          );
          await this.saveSetting(SETTING_KEYS.CLAUDE_API_KEY, claudeApiKey);
        }
      } catch (error) {
        console.log('No optional_env.json found or error loading it:', error);
      }
    } else {
      console.log(
        '[SettingsWidget] API key already exists in settings registry, not loading from optional_env.json'
      );
    }

    const claudeModelId = await this.loadSetting(
      SETTING_KEYS.CLAUDE_MODEL_ID,
      'claude-sonnet-4-20250514'
    );
    const claudeModelUrl = await this.loadSetting(
      SETTING_KEYS.CLAUDE_MODEL_URL,
      'https://sage.alpinex.ai:8760'
    );
    const databaseUrl = await this.loadSetting(SETTING_KEYS.DATABASE_URL, '');

    // Update AppState with loaded settings
    AppStateService.updateClaudeSettings({
      claudeApiKey,
      claudeModelId,
      claudeModelUrl,
      databaseUrl
    });

    // Set DB_URL environment variable in kernel if configured
    console.log('[SettingsWidget] Database URL from settings:', databaseUrl);
    if (databaseUrl && databaseUrl.trim() !== '') {
      console.log(
        '[SettingsWidget] Setting DB_URL in kernel during settings load'
      );
      // Use retry mechanism since kernel might not be ready yet
      KernelUtils.setDbUrlInKernelWithRetry(databaseUrl);
    } else {
      console.log(
        '[SettingsWidget] No database URL configured, skipping DB_URL setup'
      );
    }
  }

  /**
   * Handle token mode change
   */
  private async handleTokenModeChange(enabled: boolean): Promise<void> {
    SettingsWidget.SAGE_TOKEN_MODE = enabled;
    await this.saveTokenModeSetting(enabled);

    // Update AppState
    AppStateService.updateSettings({ tokenMode: enabled });

    // Update state
    this._state = {
      ...this._state,
      sageTokenMode: enabled
    };

    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Handle tab autocomplete change
   */
  private async handleTabAutocompleteChange(enabled: boolean): Promise<void> {
    await this.saveTabAutocompleteSetting(enabled);

    // Update AppState
    AppStateService.updateClaudeSettings({ tabAutocompleteEnabled: enabled });

    this._state = {
      ...this._state,
      tabAutocompleteEnabled: enabled
    };

    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Handle Claude API key change
   */
  private async handleClaudeApiKeyChange(value: string): Promise<void> {
    await this.saveSetting(SETTING_KEYS.CLAUDE_API_KEY, value);

    // Update AppState
    AppStateService.updateClaudeSettings({ claudeApiKey: value });

    this._state = {
      ...this._state,
      claudeApiKey: value
    };

    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Handle Claude model ID change
   */
  private async handleClaudeModelIdChange(value: string): Promise<void> {
    await this.saveSetting(SETTING_KEYS.CLAUDE_MODEL_ID, value);

    // Update AppState
    AppStateService.updateClaudeSettings({ claudeModelId: value });

    this._state = {
      ...this._state,
      claudeModelId: value
    };

    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Handle Claude model URL change
   */
  private async handleClaudeModelUrlChange(value: string): Promise<void> {
    await this.saveSetting(SETTING_KEYS.CLAUDE_MODEL_URL, value);

    // Update AppState
    AppStateService.updateClaudeSettings({ claudeModelUrl: value });

    this._state = {
      ...this._state,
      claudeModelUrl: value
    };

    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Handle database URL change
   */
  private async handleDatabaseUrlChange(value: string): Promise<void> {
    await this.saveSetting(SETTING_KEYS.DATABASE_URL, value);

    // Update AppState
    AppStateService.updateClaudeSettings({ databaseUrl: value });

    // Set DB_URL environment variable in the current kernel
    KernelUtils.setDbUrlInKernel(value);

    // Clear metadata cache if database URL is empty
    if (!value || value.trim() === '') {
      console.log(
        '[SettingsWidget] Database URL cleared, clearing metadata cache'
      );
      const databaseCache = DatabaseMetadataCache.getInstance();
      databaseCache.clearCache();
    }

    this._state = {
      ...this._state,
      databaseUrl: value
    };

    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Show the settings widget
   */
  public show(): void {
    this._state = {
      ...this._state,
      isVisible: true
    };
    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Hide the settings widget
   */
  public hide(): void {
    this._state = {
      ...this._state,
      isVisible: false
    };
    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Get the current state
   */
  public getState(): ISettingsState {
    return { ...this._state };
  }

  /**
   * Check if the widget is currently visible
   */
  public getIsVisible(): boolean {
    return this._state.isVisible;
  }

  /**
   * Get the current Claude API key
   */
  public getClaudeApiKey(): string {
    return this._state.claudeApiKey;
  }

  /**
   * Get the current Claude model ID
   */
  public getClaudeModelId(): string {
    return this._state.claudeModelId;
  }

  /**
   * Get the current Claude model URL
   */
  public getClaudeModelUrl(): string {
    return this._state.claudeModelUrl;
  }

  /**
   * Get the current database URL
   */
  public getDatabaseUrl(): string {
    return this._state.databaseUrl;
  }

  /**
   * Get the current tab autocomplete setting
   */
  public getTabAutocompleteEnabled(): boolean {
    return this._state.tabAutocompleteEnabled;
  }

  /**
   * Get all Claude settings as an object
   */
  public getClaudeSettings(): {
    apiKey: string;
    modelId: string;
    modelUrl: string;
  } {
    return {
      apiKey: this._state.claudeApiKey,
      modelId: this._state.claudeModelId,
      modelUrl: this._state.claudeModelUrl
    };
  }

  /**
   * Get the widget for adding to layout (for backwards compatibility)
   */
  public getWidget(): Widget {
    return this;
  }
}
