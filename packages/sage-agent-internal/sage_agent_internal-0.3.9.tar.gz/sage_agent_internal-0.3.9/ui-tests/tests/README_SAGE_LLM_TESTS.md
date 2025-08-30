# Sage LLM State Testing

This directory contains comprehensive tests for all LLM interaction states in the Sage Agent extension.

## Quick Setup

### Windows:
```bash
.\setup-tests.bat
```

### Linux/Mac:
```bash
chmod +x setup-tests.sh
./setup-tests.sh
```

### Manual Setup:
1. Edit `tests/config.ts` and set your `SAGE_API_KEY`
2. Install dependencies: `npm install`
3. Create screenshots directory: `mkdir -p screenshots`

## Running Tests

1. **Start JupyterLab** (in one terminal):
   ```bash
   npm run start
   ```

2. **Run Tests** (in another terminal):
   ```bash
   npm test                    # Run all tests
   npm test sage_llm_test      # Run only LLM state tests
   ```

## Configuration

**IMPORTANT:** Before running tests, you must set your API key in one of these ways:

## Configuration

Edit `tests/config.ts` and set your API key:
```typescript
const CONFIG: Config = {
  SAGE_API_KEY: 'your-actual-api-key-here',  // Replace with your actual API key
  CLAUDE_MODEL_URL: 'https://sage.alpinex.ai:8760',
  CLAUDE_MODEL_ID: 'claude-sonnet-4-20250514',
  // ... other config
};
```

## Test Categories

### 🏠 Idle States
- Empty interface (no interactions)
- Finished chat without diffs
- Page reload with chat history
- New chat creation

### 🔄 Diff Approval States
- **Single File Diffs**: Approval → Accept/Reject → Execute
- **Multi-File Diffs**: Approval → Accept/Reject → Execute

### ⚡ Interaction States
- Context picker activation
- Cell execution requests
- Tool calls and function execution
- Waiting for user replies

### 🤖 Generation States
- Active LLM generation
- Tool execution with loading
- Long-running generation tracking

## Screenshots

All screenshots are automatically captured and organized in:
```
screenshots/
├── test_runs/
│   └── [timestamp]/         # Screenshots from each test run
└── states/                  # Organized by state category
    ├── idle/
    ├── diff_approval/
    ├── interaction/
    └── generation/
```

## Test Prompts

The tests use specific prompts designed to trigger different states:

- **Simple Query**: `"What is the current time?"` (no diffs)
- **Single Diff**: `"Please fix this Python syntax error: print('hello world'"` 
- **Multi-File Diff**: `"Create a new React component with TypeScript interfaces and CSS styling"`
- **Tool Call**: `"Check the current git status and list recent commits"`
- **Context Analysis**: `"Analyze the current codebase structure and suggest improvements"`
- **Long Generation**: `"Write comprehensive documentation for this entire project..."`

## Troubleshooting

### Common Issues:

1. **API Key Error**: Make sure `SAGE_API_KEY` is set correctly
2. **JupyterLab Not Starting**: Check if port 8888 is available
3. **Tests Timing Out**: Increase timeout values in config
4. **Screenshots Not Saving**: Check directory permissions

### Debug Mode:
Set `headless: false` in playwright config to see browser interactions.

## Test Development

To add new states or modify existing tests:

1. **Add new prompts** in the `TEST_PROMPTS` object
2. **Create new test cases** following the existing pattern
3. **Update selectors** if UI elements change
4. **Add new screenshot categories** as needed

## Performance Notes

- Tests run with visual browser by default (for debugging)
- Screenshots are full-page captures (may be large)
- Long generation tests may take several minutes
- Each test run creates a timestamped screenshot directory

## CI/CD Integration

For automated testing:
- Set `headless: true` in playwright config
- Use environment variables for sensitive data
- Archive screenshot artifacts for failed tests
