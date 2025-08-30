/**
 * Test configuration for Sage LLM tests
 *
 * IMPORTANT: UPDATE THESE VALUES
 * Before running these tests, you MUST:
 * 1. Set your API key in SAGE_API_KEY below (replace 'your-api-key-here')
 * 2. Ensure the model URL and ID are correct for your setup
 * 3. Have JupyterLab running with the Sage extension installed
 *
 * No .env file is needed - all configuration is done in this file.
 */

export interface TestPromptsConfig {
  SIMPLE_QUERY: string[];
  SINGLE_DIFF: string[];
  MULTI_DIFF: string[];
  SP_ANALYSIS: string[];
}

export interface Config {
  // ⚠️ REQUIRED: Set your API key here before running tests
  SAGE_API_KEY: string;
  CLAUDE_MODEL_URL: string;
  CLAUDE_MODEL_ID: string;
  DATABASE_URL: string;
  SCREENSHOT_DIR: string;
  TEST_TIMEOUT: number;
  API_SETUP_TIMEOUT: number;
  TEST_PROMPTS: TestPromptsConfig;
}

const CONFIG: Config = {
  // ⚠️ REQUIRED: Replace 'your-api-key-here' with your actual API key
  SAGE_API_KEY: '',
  CLAUDE_MODEL_URL: 'https://sage.alpinex.ai:8760',
  CLAUDE_MODEL_ID: 'claude-sonnet-4-20250514',
  DATABASE_URL: '',
  SCREENSHOT_DIR: './screenshots',
  TEST_TIMEOUT: 30000,
  API_SETUP_TIMEOUT: 10000,
  TEST_PROMPTS: {
    // Simple prompts that don't generate diffs
    SIMPLE_QUERY: ['What is the current time?'],

    // Prompts that generate single file diffs
    SINGLE_DIFF: [
      'Add a cell that prints Hello World',
      'Edit it to instead print Hello Sage AI'
    ],

    // Prompts that generate multi-file diffs
    MULTI_DIFF: [
      'add three new cells that print hello world 3 times each. Run the last cell. You have to call the add cell tool 3 times.',
      'Modify cell 3 to print "Hello Sage AI" instead of "Hello World"'
    ],

    // Long generation prompts
    SP_ANALYSIS: [
      'What happens if you bought s&p500 during 5%+ stock market crashes everytime (with respect to 7day MA) + some DCA? compare this with a simple monthly DCA strategy where we just buy at the beginning of the month vs we either buy during a 5% correction or buy once every 12months (i.e. assuming no correction happened during that period). Make simple assumptions such as investing $1000 per month etc and also figure out if this strategy can or a variant of this could outperform simple DCA strategy. Ask for confirmation after plan creation\n'
    ]
  }
};

export default CONFIG;
