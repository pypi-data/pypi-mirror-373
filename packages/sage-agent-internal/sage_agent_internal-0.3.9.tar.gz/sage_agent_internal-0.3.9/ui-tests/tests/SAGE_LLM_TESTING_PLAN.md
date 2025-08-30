# Sage LLM State Testing Plan

## Overview
This document outlines the comprehensive testing strategy for all LLM interaction states in the Sage Agent. The tests will capture screenshots at each state and validate UI components to ensure proper functionality across all interaction scenarios.

## Test States Overview

### 1. Idle States
- **None**: Empty chat interface, no interactions
- **No diff but finished chat**: Chat completed without code diffs
- **Reloaded page chat**: Page refreshed with existing chat history
- **Create new chat**: Fresh chat session initiated

### 2. Diff Approval States

#### Single Diff States:
- **Approval**: Single file diff awaiting user approval
- **Accepted**: User accepted single diff
- **Rejected**: User rejected single diff  
- **Run**: Single diff being executed

#### Multi Diff States:
- **Approval**: Multiple file diffs awaiting user approval
- **Accepted**: User accepted multi-file diffs
- **Rejected**: User rejected multi-file diffs
- **Run**: Multi-file diffs being executed

### 3. Interaction States
- **Context picker open**: File/context selection interface displayed
- **Run cell request**: Cell execution in progress
- **Generating States**: LLM generating response
- **Running tool call**: Tool/function execution
- **Waiting for user reply**: LLM awaiting user input

### 4. Generating States
- **Generating**: LLM actively generating response
- **Running tool call**: Tool execution with loading indicators
- **Waiting for user reply**: Paused state awaiting user interaction

## Test Implementation Strategy

### Setup Requirements
1. **Environment Configuration**
   - Configuration via `tests/config.ts` file with API keys and model settings
   - Automated API key injection via settings UI
   - Playwright browser automation

2. **Screenshot Management**
   - Organized folder structure: `screenshots/states/[category]/[state]/`
   - Full-page screenshots for comprehensive state capture
   - Timestamped filenames for test run identification

3. **State Triggering**
   - Specific prompts designed to trigger each state
   - Automated UI interactions to navigate through states
   - Validation of state transitions

### Test Structure

#### Core Test File: `sage_llm_test.spec.ts`
- Main orchestrator for all state tests
- Handles environment setup and teardown
- Manages screenshot capture and organization

#### Test Categories:
1. **Idle State Tests** (`idle_states.spec.ts`)
2. **Diff Approval Tests** (`diff_approval.spec.ts`)  
3. **Interaction State Tests** (`interaction_states.spec.ts`)
4. **Generation State Tests** (`generation_states.spec.ts`)

### Prompts for State Triggering

#### Single-line Diffs
```
"Please fix this Python syntax error: print('hello world'"
```

#### Multiple Edits (Single File)
```
"Refactor this function to be more readable and add error handling"
```

#### Multi-file Diffs
```
"Create a new React component with TypeScript interfaces and CSS styling"
```

#### Context Picker
```
"Analyze the current codebase structure and suggest improvements"
```

#### Tool Calls
```
"Check the current git status and create a new branch"
```

#### Long Generation
```
"Write a comprehensive documentation for this entire project including setup, usage, and API reference"
```

### Screenshot Organization
```
screenshots/
├── states/
│   ├── idle/
│   │   ├── none/
│   │   ├── finished_no_diff/
│   │   ├── reloaded_page/
│   │   └── new_chat/
│   ├── diff_approval/
│   │   ├── single/
│   │   │   ├── approval/
│   │   │   ├── accepted/
│   │   │   ├── rejected/
│   │   │   └── run/
│   │   └── multi/
│   │       ├── approval/
│   │       ├── accepted/
│   │       ├── rejected/
│   │       └── run/
│   ├── interaction/
│   │   ├── context_picker/
│   │   ├── run_cell/
│   │   └── generating/
│   └── generation/
│       ├── generating/
│       ├── tool_call/
│       └── waiting_reply/
└── test_runs/
    └── [timestamp]/
        └── [copied from states/]
```

### Validation Strategy

#### Component Visibility Tests
- Chat container presence and visibility
- Input field accessibility
- Send button state validation
- Loading indicators during generation
- Diff approval UI elements
- Error states and messages

#### State Transition Validation
- Proper state changes after user actions
- Loading states during async operations
- Error recovery mechanisms
- UI responsiveness during long operations

#### Screenshot Comparison
- Visual regression testing capabilities
- Baseline screenshot establishment
- Automated difference detection
- Manual review flags for significant changes

### Environment Setup

#### Required Configuration
```typescript
// tests/config.ts file
const CONFIG = {
  SAGE_API_KEY: 'your_api_key_here',
  CLAUDE_MODEL_URL: 'https://sage.alpinex.ai:8760',
  CLAUDE_MODEL_ID: 'claude-sonnet-4-20250514',
  DATABASE_URL: 'your_database_url_here'
};
```

#### API Key Injection Strategy
1. Load configuration from tests/config.ts at test startup
2. Navigate to Settings UI programmatically
3. Inject API key via form automation
4. Validate successful configuration
5. Proceed with state testing

### Execution Flow

#### Pre-Test Setup
1. Launch JupyterLab with Sage extension
2. Wait for full application load
3. Configure API settings automatically
4. Create clean chat environment
5. Initialize screenshot directories

#### Test Execution
1. Execute state-specific prompts
2. Wait for state transitions
3. Capture full-page screenshots
4. Validate component states
5. Record test metrics and timing

#### Post-Test Cleanup
1. Archive screenshots with timestamps
2. Generate test report with state coverage
3. Clean up temporary files
4. Reset application state for next run

### Success Criteria

#### Functional Validation
- All states successfully triggered
- UI components behave as expected
- No crashes or errors during state transitions
- Proper error handling for failed operations

#### Visual Validation
- Screenshots capture complete UI state
- All relevant UI elements visible
- Consistent styling across states
- Loading indicators work properly

#### Performance Validation
- State transitions complete within reasonable timeframes
- No memory leaks during extended testing
- Responsive UI during long operations
- Proper cleanup after test completion

## Implementation Notes

### Technical Considerations
- Use Playwright's built-in waiting mechanisms
- Implement robust error handling for flaky operations
- Add retry logic for network-dependent operations
- Maintain state isolation between tests

### Maintenance Strategy
- Regular baseline screenshot updates
- Prompt refinement based on model updates
- UI selector updates for component changes
- Documentation updates for new states

### Future Enhancements
- Automated state coverage reporting
- Integration with CI/CD pipeline
- Performance benchmarking across states
- Cross-browser compatibility testing
