import { ToolService } from './Services/ToolService';
import { CachingService, SETTING_KEYS } from './utils/caching';

interface Codebase {
  id: string;
  name: string;
  path: string;
  instructions: string;
}

/**
 * Component for managing codebases for AI search
 */
export class CodebaseManager {
  private element: HTMLElement;
  private toolService: ToolService;
  private codebases: Codebase[] = [];
  private isInitialized: boolean = false;

  // UI elements
  private codebaseListElement!: HTMLElement; // Added definite assignment assertion
  private addForm!: HTMLFormElement; // Added definite assignment assertion

  constructor(toolService: ToolService) {
    this.toolService = toolService;
    this.element = this.createUI();
    this.loadCodebases();
  }

  /**
   * Get the DOM element for this component
   */
  public getElement(): HTMLElement {
    return this.element;
  }

  /**
   * Create the UI for codebase management
   */
  private createUI(): HTMLElement {
    const container = document.createElement('div');
    container.className = 'sage-ai-codebase-manager';

    // This feature is not maintained yet
    // Softly hide it for now
    container.style.display = 'none';

    // Create section title
    const title = document.createElement('h3');
    title.textContent = 'Codebase Search';
    title.className = 'sage-ai-section-title';

    // Create description
    const description = document.createElement('p');
    description.textContent =
      'Manage codebases that the AI can search through and reference.';
    description.className = 'sage-ai-section-description';

    // Create form for adding new repos
    this.addForm = this.createAddForm();

    // Create codebase list
    this.codebaseListElement = document.createElement('div');
    this.codebaseListElement.className = 'sage-ai-codebase-list';

    // Create empty state
    const emptyState = document.createElement('div');
    emptyState.className = 'sage-ai-empty-state';
    emptyState.textContent =
      'No codebases added yet. Add a codebase to enable AI code search.';
    this.codebaseListElement.appendChild(emptyState);

    // Assemble the container
    container.appendChild(title);
    container.appendChild(description);
    container.appendChild(this.addForm);
    container.appendChild(this.codebaseListElement);

    // Add a stylesheet link to the document head
    // Styles are bundled via the JupyterLab extension (style/index.css). Avoid injecting links.

    return container;
  }

  /**
   * Create the form for adding new repositories
   */
  private createAddForm(): HTMLFormElement {
    const form = document.createElement('form');
    form.className = 'sage-ai-add-repo-form';

    // Path input
    const pathGroup = document.createElement('div');
    pathGroup.className = 'sage-ai-form-group';

    const pathLabel = document.createElement('label');
    pathLabel.textContent = 'Repository Path:';
    pathLabel.htmlFor = 'repo-path';

    const pathInput = document.createElement('input');
    pathInput.type = 'text';
    pathInput.id = 'repo-path';
    pathInput.placeholder = '/path/to/codebase';
    pathInput.className = 'sage-ai-input';

    pathGroup.appendChild(pathLabel);
    pathGroup.appendChild(pathInput);

    // Name input
    const nameGroup = document.createElement('div');
    nameGroup.className = 'sage-ai-form-group';

    const nameLabel = document.createElement('label');
    nameLabel.textContent = 'Name (optional):';
    nameLabel.htmlFor = 'repo-name';

    const nameInput = document.createElement('input');
    nameInput.type = 'text';
    nameInput.id = 'repo-name';
    nameInput.placeholder = 'e.g., My Project';
    nameInput.className = 'sage-ai-input';

    nameGroup.appendChild(nameLabel);
    nameGroup.appendChild(nameInput);

    // Instructions input
    const instructionsGroup = document.createElement('div');
    instructionsGroup.className = 'sage-ai-form-group';

    const instructionsLabel = document.createElement('label');
    instructionsLabel.textContent = 'Instructions (optional):';
    instructionsLabel.htmlFor = 'repo-instructions';

    const instructionsTextarea = document.createElement('textarea');
    instructionsTextarea.id = 'repo-instructions';
    instructionsTextarea.placeholder =
      'e.g., Import the bot class like this: from twitter_bots.crypto_sherpa import CryptoSherpa';
    instructionsTextarea.className = 'sage-ai-textarea';
    instructionsTextarea.rows = 3;

    instructionsGroup.appendChild(instructionsLabel);
    instructionsGroup.appendChild(instructionsTextarea);

    // Submit button
    const submitBtn = document.createElement('button');
    submitBtn.type = 'submit';
    submitBtn.className = 'sage-ai-button sage-ai-primary-button';
    submitBtn.textContent = 'Add Repository';

    // Assemble form
    form.appendChild(pathGroup);
    form.appendChild(nameGroup);
    form.appendChild(instructionsGroup);
    form.appendChild(submitBtn);

    // Form submission handler
    form.addEventListener('submit', event => {
      event.preventDefault();
      this.addRepository(
        pathInput.value.trim(),
        nameInput.value.trim(),
        instructionsTextarea.value.trim()
      );

      // Clear the form
      pathInput.value = '';
      nameInput.value = '';
      instructionsTextarea.value = '';
    });

    return form;
  }

  /**
   * Load saved codebases from settings registry
   */
  private async loadCodebases(): Promise<void> {
    try {
      const storedCodebases = await CachingService.getObjectSetting<Codebase[]>(
        SETTING_KEYS.CODEBASES,
        []
      );

      this.codebases = storedCodebases || [];

      console.log('Loaded codebases from settings registry:', this.codebases);

      // Update the UI with the loaded repositories
      this.renderCodebaseList();
    } catch (error) {
      console.error('Failed to load codebases:', error);
      this.codebases = [];
      this.renderCodebaseList();
    }
  }

  /**
   * Save codebases to settings registry
   */
  private async saveCodebasesToStorage(): Promise<void> {
    try {
      await CachingService.setObjectSetting(
        SETTING_KEYS.CODEBASES,
        this.codebases
      );
      console.log('Saved codebases to settings registry');
    } catch (error) {
      console.error('Failed to save codebases to settings registry:', error);
    }
  }

  /**
   * Add a new repository
   */
  private async addRepository(
    path: string,
    name: string,
    instructions: string
  ): Promise<void> {
    if (!path) {
      alert('Repository path is required');
      return;
    }

    // Generate a unique ID (using path as ID)
    const id = path;

    try {
      // TODO: Remove MCP backend dependency - for now just add to local list
      const codebase: Codebase = {
        id,
        path,
        name: name || path.split('/').pop() || path,
        instructions
      };

      // Add to our list
      this.codebases.push(codebase);

      // Save to settings registry
      await this.saveCodebasesToStorage();

      this.renderCodebaseList();

      // TODO: Implement local codebase management without backend
      console.log(
        'Repository added locally (backend integration disabled):',
        codebase
      );
    } catch (error) {
      console.error('Failed to add repository:', error);
      alert(
        `Failed to add repository: ${error instanceof Error ? error.message : 'Unknown error'}`
      );
    }
  }

  /**
   * Reload a repository
   */
  private async reloadRepository(id: string): Promise<void> {
    const codebase = this.codebases.find(repo => repo.id === id);
    if (!codebase) return;

    try {
      // TODO: Remove MCP backend dependency - for now just log the action
      console.log(
        'Repository reload requested (backend integration disabled):',
        codebase.path
      );

      // Update the UI
      this.renderCodebaseList();
    } catch (error) {
      console.error('Failed to reload repository:', error);
      alert(
        `Failed to reload repository: ${error instanceof Error ? error.message : 'Unknown error'}`
      );

      // Reset UI
      this.renderCodebaseList();
    }
  }

  /**
   * Remove a repository
   */
  private async removeRepository(id: string): Promise<void> {
    const codebase = this.codebases.find(repo => repo.id === id);
    if (!codebase) return;

    if (
      !confirm(
        'Are you sure you want to remove this repository? This action cannot be undone.'
      )
    ) {
      return;
    }

    try {
      // TODO: Remove MCP backend dependency - remove from local list only
      this.codebases = this.codebases.filter(cb => cb.id !== id);

      // Save to settings registry
      await this.saveCodebasesToStorage();

      console.log(
        'Repository removed locally (backend integration disabled):',
        codebase.path
      );

      // Update the UI
      this.renderCodebaseList();

      // Show success message
      alert(`Repository at ${codebase.path} removed locally.`);
    } catch (error) {
      console.error('Failed to remove repository:', error);
      alert(
        `Failed to remove repository: ${error instanceof Error ? error.message : 'Unknown error'}`
      );
    }
  }

  /**
   * Edit repository instructions
   */
  private editInstructions(id: string): void {
    const codebase = this.codebases.find(repo => repo.id === id);
    if (!codebase) return;

    // Get the current instructions
    const currentInstructions = codebase.instructions || '';

    // Prompt for new instructions
    const newInstructions = prompt(
      'Edit instructions for this codebase:',
      currentInstructions
    );

    // If canceled or unchanged, do nothing
    if (newInstructions === null || newInstructions === currentInstructions)
      return;

    // Update the codebase
    codebase.instructions = newInstructions;

    // Update the UI
    this.renderCodebaseList();
  }

  /**
   * Render the list of codebases
   */
  private renderCodebaseList(): void {
    // Clear current list
    this.codebaseListElement.innerHTML = '';

    if (this.codebases.length === 0) {
      const emptyState = document.createElement('div');
      emptyState.className = 'sage-ai-empty-state';
      emptyState.textContent =
        'No codebases added yet. Add a codebase to enable AI code search.';
      this.codebaseListElement.appendChild(emptyState);
      return;
    }

    // Create elements for each codebase
    this.codebases.forEach(codebase => {
      const item = document.createElement('div');
      item.className = 'sage-ai-codebase-item';

      const header = document.createElement('div');
      header.className = 'sage-ai-codebase-header';

      const title = document.createElement('h4');
      title.className = 'sage-ai-codebase-title';
      title.textContent = codebase.name;

      const actions = document.createElement('div');
      actions.className = 'sage-ai-codebase-actions';

      // Reload button
      const reloadBtn = document.createElement('button');
      reloadBtn.className = 'sage-ai-action-button';
      reloadBtn.textContent = 'Reload';
      reloadBtn.addEventListener('click', () =>
        this.reloadRepository(codebase.id)
      );

      // Edit instructions button
      const editBtn = document.createElement('button');
      editBtn.className = 'sage-ai-action-button';
      editBtn.textContent = 'Edit Instructions';
      editBtn.addEventListener('click', () =>
        this.editInstructions(codebase.id)
      );

      // Remove button
      const removeBtn = document.createElement('button');
      removeBtn.className = 'sage-ai-action-button sage-ai-danger-button';
      removeBtn.textContent = 'Remove';
      removeBtn.addEventListener('click', () =>
        this.removeRepository(codebase.id)
      );

      actions.appendChild(reloadBtn);
      actions.appendChild(editBtn);
      actions.appendChild(removeBtn);

      header.appendChild(title);
      header.appendChild(actions);

      // Path
      const path = document.createElement('div');
      path.className = 'sage-ai-codebase-path';
      path.textContent = codebase.path;

      // Instructions (if any)
      let instructions;
      if (codebase.instructions) {
        instructions = document.createElement('div');
        instructions.className = 'sage-ai-codebase-instructions';
        instructions.textContent = codebase.instructions;
      }

      // Assemble the item
      item.appendChild(header);
      item.appendChild(path);
      if (instructions) {
        item.appendChild(instructions);
      }

      this.codebaseListElement.appendChild(item);
    });
  }
}
