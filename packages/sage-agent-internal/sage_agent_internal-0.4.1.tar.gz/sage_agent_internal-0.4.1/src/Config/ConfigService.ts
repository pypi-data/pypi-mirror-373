import { AppStateService } from '../AppState';

/**
 * Interface for model configuration data
 */
export interface IModelConfig {
  system_prompt: string;
  model_name: string;
  model_url: string;
  api_key: string;
  tool_blacklist?: string[];
}

/**
 * Combined configuration interface
 */
export interface IConfig {
  claude: IModelConfig;
  claude_ask_mode: IModelConfig;
  edit_selection: IModelConfig;
  edit_full_cell: IModelConfig;
  fast_mode: IModelConfig;
  active_model_type?: string;
}

/**
 * Service for managing local configuration data
 */
export class ConfigService {
  private static activeModelType: string = 'claude'; // Default to claude

  /**
   * Get the active model type
   */
  public static getActiveModelType(): string {
    return this.activeModelType;
  }

  /**
   * Set the active model type
   */
  public static setActiveModelType(modelType: string): void {
    this.activeModelType = modelType;
  }

  /**
   * Get model configurations from JSON file
   */
  private static getModelConfigurations(): Record<
    string,
    { model_name: string; tool_blacklist: string[] }
  > {
    return require('./models.json');
  }

  /**
   * Build configuration for a specific model type
   */
  private static async buildModelConfig(
    modelType: string,
    modelUrl: string,
    apiKey: string
  ): Promise<IModelConfig> {
    const modelConfigs = this.getModelConfigurations();
    const modelConfig = modelConfigs[modelType];

    if (!modelConfig) {
      throw new Error(`Unknown model type: ${modelType}`);
    }

    const system_prompt = require(
      `./prompts/${this.getPromptFileName(modelType)}.md`
    );

    return {
      system_prompt,
      model_name: modelConfig.model_name,
      model_url: modelUrl,
      api_key: apiKey,
      tool_blacklist: modelConfig.tool_blacklist || []
    };
  }

  /**
   * Get the prompt file name for a model type
   */
  private static getPromptFileName(modelType: string): string {
    switch (modelType) {
      case 'claude':
        return 'claude_system_prompt';
      case 'claude_ask_mode':
        return 'claude_system_prompt_ask_mode';
      case 'edit_selection':
        return 'claude_system_prompt_edit_selection';
      case 'edit_full_cell':
        return 'claude_system_prompt_edit_full_cell';
      case 'fast_mode':
        return 'claude_system_prompt_fast_mode';
      default:
        return 'claude_system_prompt';
    }
  }

  /**
   * Get the tab completion system prompt text
   */
  public static getTabCompletionPrompt(): string {
    try {
      const mod = require('./prompts/claude_system_prompt_tab_completion.md');
      if (typeof mod === 'string') return mod;
      if (mod && typeof mod.default === 'string') return mod.default;
      // Some bundlers may wrap as { default: <string> }
      return (
        String(mod ?? '').trim() ||
        'You are a code-only completion engine. Return only the next minimal continuation as raw text.'
      );
    } catch (e) {
      return 'You are a code completion engine. Return only short continuations.';
    }
  }

  /**
   * Get configuration with model settings
   */
  public static async getConfig(
    modelUrl: string = '',
    apiKey: string = ''
  ): Promise<IConfig> {
    try {
      // If no explicit parameters provided, get from AppState
      if (!modelUrl || !apiKey) {
        const claudeSettings = AppStateService.getClaudeSettings();
        modelUrl = modelUrl || claudeSettings.claudeModelUrl;
        apiKey = apiKey || claudeSettings.claudeApiKey;
      }

      const config: IConfig = {
        claude: await this.buildModelConfig('claude', modelUrl, apiKey),
        claude_ask_mode: await this.buildModelConfig(
          'claude_ask_mode',
          modelUrl,
          apiKey
        ),
        edit_selection: await this.buildModelConfig(
          'edit_selection',
          modelUrl,
          apiKey
        ),
        edit_full_cell: await this.buildModelConfig(
          'edit_full_cell',
          modelUrl,
          apiKey
        ),
        fast_mode: await this.buildModelConfig('fast_mode', modelUrl, apiKey),
        active_model_type: this.activeModelType
      };

      return config;
    } catch (error) {
      console.error('Error building configuration:', error);
      throw new Error(`Failed to build configuration: ${error}`);
    }
  }

  public static async getTools() {
    return require('./tools.json');
  }
}
