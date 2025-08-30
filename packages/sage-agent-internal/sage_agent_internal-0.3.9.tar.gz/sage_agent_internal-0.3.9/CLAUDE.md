# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

Sage Agent is a JupyterLab extension that provides AI-powered assistance for data analysis and notebook development. It integrates LLM capabilities directly into Jupyter notebooks with chat interface, code generation, and notebook manipulation tools.

## Development Commands

### Build and Development
- `jlpm build` - Build the extension for development (includes source maps)
- `jlpm build:prod` - Build for production (optimized, no source maps)
- `jlpm watch` - Watch source files and rebuild automatically
- `jlpm watch:src` - Watch TypeScript source files only
- `jlpm watch:labextension` - Watch labextension files only

### Development Setup
- `pip install -e "."` - Install package in development mode
- `jupyter labextension develop . --overwrite` - Link development version with JupyterLab
- `jupyter lab` - Run JupyterLab with the extension

### Testing and Quality
- `jlpm test` - Run Jest tests with coverage
- `jlpm lint` - Run all linters (stylelint, prettier, eslint) with fixes
- `jlpm lint:check` - Check code quality without fixes
- `jlpm eslint` - Run ESLint with fixes
- `jlpm prettier` - Format code with Prettier

### Clean Commands
- `jlpm clean` - Clean compiled TypeScript files
- `jlpm clean:all` - Clean all generated files (lib, labextension, cache)

## Architecture Overview

### Core Architecture Pattern
The extension follows a centralized state management pattern using **AppStateService** as the single source of truth for all application state. This service manages:

- Core services (ToolService, NotebookTracker, etc.)
- UI containers (ChatContainer, SettingsContainer)
- Notebook state and tracking
- Configuration and settings

### Key Architectural Components

**Plugin System (src/plugin.ts:46-750)**
- Main JupyterLab plugin entry point
- Initializes all services in dependency order
- Sets up event handlers for notebook changes
- Registers commands and UI components

**State Management (src/AppState.ts)**
- Centralized state using RxJS BehaviorSubject
- Event-driven architecture for notebook changes
- Service initialization and dependency injection
- Settings and configuration management

**Chat System (src/Chat/)**
- ConversationService: Manages chat interactions with LLMs
- ChatInputManager: Handles user input and context
- ActionHistory: Tracks user actions for context
- RichTextChatInput: Advanced input component with markdown support

**Notebook Management (src/Notebook/)**
- NotebookTools: Core notebook manipulation utilities
- NotebookDiffManager: Handles code diff display and approval
- NotebookContextManager: Manages cell context for chat
- InlineDiffService: Provides inline diff visualization

**Services (src/Services/)**
- ToolService: Orchestrates all notebook tools and operations
- AnthropicService: Handles Claude API integration
- ConfigService: Manages extension configuration
- DatabaseMetadataCache: Caches database metadata for tools

### Tool System Architecture

The extension provides structured tools for LLM interaction defined in `src/Config/tools.json`:

**Notebook Tools:**
- `notebook-edit_plan` - Manages notebook planning workflow
- `notebook-read_cells` - Reads specific notebook cells  
- `notebook-add_cell` - Creates new cells with tracking
- `notebook-edit_cell` - Modifies existing cell content
- `notebook-run_cell` - Executes code cells
- `notebook-remove_cells` - Deletes specified cells
- `notebook-wait_user_reply` - UI component for user interaction

**Data Tools:**
- `filesystem-read_dataset` - Reads dataset files from data directory
- `web-search_dataset` - Searches ticker/financial data with fuzzy matching

### Configuration System

**Model Configuration (src/Config/models.json)**
- Different models for different interaction modes
- Tool blacklists per model to optimize performance
- Supports Claude Sonnet 4 and Haiku models

**Prompt System (src/Config/prompts/)**
- Specialized system prompts for different modes
- `claude_system_prompt.md` - Main data science assistant prompt
- Mode-specific prompts for ask, edit, and fast modes

## Important Development Patterns

### Service Initialization Order
1. Core services (ToolService, NotebookTracker, NotebookTools)
2. Managers (PlanStateDisplay, WaitingUserReplyBoxManager)  
3. Additional services (ActionHistory, CellTrackingService)
4. UI containers (ChatContainer, SettingsContainer)

### Notebook Unique ID System
- Each notebook gets a unique `sage_ai.unique_id` in metadata
- Used for tracking chat histories and state across renames
- Fallback to path-based tracking for compatibility

### Context Management
- Cells can be added/removed from chat context
- Visual highlighting shows which cells are in context
- Context preserved across notebook operations

### Diff Approval Workflow
- Code changes shown as diffs before execution
- User approval required for cell modifications
- Inline diff visualization with syntax highlighting

## Key File Locations

### Source Structure
- `src/plugin.ts` - Main plugin entry point and initialization
- `src/AppState.ts` - Centralized state management
- `src/Config/` - Configuration files (tools, models, prompts)
- `src/Services/` - Core business logic services
- `src/Notebook/` - Notebook-specific functionality
- `src/Chat/` - Chat interface and conversation management
- `src/Components/` - Reusable UI components

### Build Outputs
- `lib/` - Compiled TypeScript output
- `sage_agent_internal/labextension/` - JupyterLab extension package
- `style/` - CSS stylesheets and icons

## Testing Strategy

- Jest for unit tests (`__tests__/` and `ui-tests/`)
- Playwright for integration tests
- Test configuration in `jest.config.js`
- Coverage reporting enabled

## Extension Development Notes

### JupyterLab Integration
- Requires JupyterLab >= 4.0.0
- Uses JupyterLab's plugin system for initialization
- Integrates with notebook tracker and command palette
- Supports JupyterLab theming system

### Database Integration
- PGLite integration for local database operations
- Database URL management through kernel environment
- Metadata caching for performance optimization

### Theme Support
- Automatic dark theme application on first load
- Diff visualization adapts to JupyterLab theme
- CSS custom properties for theme consistency