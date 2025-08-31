/**
 * Tab completion service for inline code suggestions
 */
export class TabCompletionService {
  private static _instance: TabCompletionService;
  private hasActiveCellFn: (() => boolean) | null = null;
  private currentRequestId: number = 0;

  public static getInstance(): TabCompletionService {
    if (!TabCompletionService._instance) {
      TabCompletionService._instance = new TabCompletionService();
    }
    return TabCompletionService._instance;
  }

  private constructor() {}

  public async initialize(): Promise<void> {
    console.log('[TabCompletionService] Initializing...');
  }

  public setActiveCellChecker(hasActiveCellFn: () => boolean): void {
    this.hasActiveCellFn = hasActiveCellFn;
  }

  public isReady(): boolean {
    return true;
  }

  public canSuggestSync(prefix: string, suffix: string): boolean {
    // First check if tab autocomplete is enabled
    const { AppStateService } = require('../AppState');
    const settings = AppStateService.getClaudeSettings();
    if (!settings.tabAutocompleteEnabled) {
      return false;
    }

    // Then check if there's an active cell - if not, don't suggest
    if (this.hasActiveCellFn && !this.hasActiveCellFn()) {
      // console.log('[TabCompletionService] No active cell, skipping suggestion');
      return false;
    }

    // Allow suggestions broadly; only block when clearly mid-identifier to reduce noise
    const prevChar = prefix.slice(-1);
    const nextChar = suffix.slice(0, 1);
    if (/\w/.test(prevChar) && /\w/.test(nextChar)) return false;
    return true;
  }

  private buildPrompt(
    prefix: string,
    suffix: string
  ): { system: string; user: string } {
    const system = [
      'You are a code completion assistant. Generate ONLY the code that should appear after the <cursor position>.',
      'CRITICAL: Output raw code only - no explanations, comments, or markdown.',
      'CRITICAL: Your output REPLACES everything after <cursor position>. The text after <cursor position> shows what will be OVERWRITTEN by your output.',
      'CRITICAL: Do NOT concatenate with existing text after cursor. Your output completely replaces the suffix text.',
      'CRITICAL: If cursor is at end of complete word/identifier followed by whitespace or newline, DO NOT suggest text that would create invalid syntax.',
      'Complete 1-10 tokens max. Output a few meaningful keywords. Do not make massive changes. If unsure or code is complete, output nothing.',
      '',
      'REPLACEMENT RULES:',
      '- Everything after <cursor position> gets DELETED and replaced with your output',
      '- If cursor is after "def funcname" and suffix starts with newline/whitespace, suggest function signature completion like "(args):"',
      '- If cursor is after complete identifier + space/newline, do NOT suggest unrelated code that would break syntax',
      '- When in doubt about syntax validity, output nothing',
      '',
      'EXAMPLES:',
      'Before: "def dfs<cursor position>\\n    visited = set()" → Output: "(graph, start, visited):\\n    if visited is None:" (replaces everything after cursor)',
      'Before: "if x > 0:<cursor position>" → Output: "\\n    return True"',
      'Before: "print(<cursor position>)" → Output: ""',
      'Before: "def func<cursor position>tion():" → Output: "():\\n    pass" (replaces "tion():")'
    ].join('\n');

    const user = prefix + '<cursor position>' + suffix;
    return { system, user };
  }

  public async getCompletion(
    prefix: string,
    suffix: string
  ): Promise<string | null> {
    // Generate a unique request ID to handle race conditions
    const requestId = ++this.currentRequestId;

    // console.log('[TabCompletionService] getCompletion called with:', {
    //   prefixLength: prefix.length,
    //   suffixLength: suffix.length,
    //   canSuggest: this.canSuggestSync(prefix, suffix),
    //   requestId
    // });

    try {
      if (!this.canSuggestSync(prefix, suffix)) {
        // console.log(
        //   '[TabCompletionService] canSuggestSync returned false, skipping'
        // );
        return null;
      }

      // Check if this request is still current before building prompt
      if (requestId !== this.currentRequestId) {
        // console.log('[TabCompletionService] Request superseded before prompt build');
        return null;
      }

      const { system, user } = this.buildPrompt(prefix, suffix);

      // console.log('[TabCompletionService] Built prompt:', {
      //   systemLength: system.length,
      //   userLength: user.length
      // });

      // Lazy import to avoid hard coupling
      const { ServiceFactory, ServiceProvider } = require('./ServiceFactory');
      const chatService = ServiceFactory.createService(
        ServiceProvider.ANTHROPIC
      );

      const initialized = await chatService.initialize();
      // console.log(
      //   '[TabCompletionService] Chat service initialized:',
      //   initialized
      // );
      if (!initialized) return null;

      // Check if this request is still current before sending
      if (requestId !== this.currentRequestId) {
        // console.log('[TabCompletionService] Request superseded before API call');
        return null;
      }

      // console.log('[TabCompletionService] Sending ephemeral message...');
      const text = await chatService.sendEphemeralMessage(
        user,
        system,
        'claude-3-5-haiku-latest',
        undefined,
        { maxTokens: 25, temperature: 0 }
      );

      // Final check if this request is still current after response
      if (requestId !== this.currentRequestId) {
        // console.log('[TabCompletionService] Request superseded after response');
        return null;
      }

      // console.log('[TabCompletionService] Raw response:', JSON.stringify(text));

      // Return raw output from the model - NO post-processing
      return text || null;
    } catch (err) {
      console.warn('[TabCompletionService] getCompletion error:', err);
      return null;
    }
  }
}
