import * as React from 'react';
import { ReactWidget } from '@jupyterlab/ui-components';
import { ISignal, Signal } from '@lumino/signaling';
import { AppStateService, ISnippet } from '../../AppState';
import { SNIPPETS_ICON } from '../../Chat/ChatContextMenu/icons';
import { ISnippetCreationState } from './types';
import { SnippetCreationContent } from './SnippetCreationContent';
import { v4 as uuidv4 } from 'uuid';

/**
 * Component for displaying content on the left side panel
 */
export class SnippetCreationWidget extends ReactWidget {
  private _state: ISnippetCreationState;
  private _stateChanged = new Signal<this, ISnippetCreationState>(this);

  constructor() {
    super();
    this._state = {
      isVisible: true,
      snippets: [],
      isCreating: false,
      editingSnippet: null,
      viewingSnippet: null, // Keep for compatibility but not used
      title: '',
      description: '',
      content: ''
    };
    this.addClass('sage-ai-snippet-creation-widget');
    this.id = 'sage-ai-snippet-creation';
    this.title.icon = SNIPPETS_ICON;
    this.title.closable = true;

    // Set the panel title to 'Rules'
    // this.title.label = 'Rules';

    // Set initial visibility state
    if (!this._state.isVisible) {
      this.addClass('hidden');
    }

    // Load snippets from cache
    this.loadSnippets();
  }

  /**
   * Get the signal that fires when state changes
   */
  public get stateChanged(): ISignal<this, ISnippetCreationState> {
    return this._stateChanged;
  }

  /**
   * Render the React component
   */
  render(): JSX.Element {
    return (
      <SnippetCreationContent
        state={this._state}
        onCreateNew={this.handleCreateNew.bind(this)}
        onSave={this.handleSave.bind(this)}
        onEdit={this.handleEdit.bind(this)}
        onView={this.handleView.bind(this)}
        onDelete={this.handleDelete.bind(this)}
        onClose={this.handleClose.bind(this)}
        onEnable={this.handleEnable.bind(this)}
        onTitleChange={this.handleTitleChange.bind(this)}
        onDescriptionChange={this.handleDescriptionChange.bind(this)}
        onContentChange={this.handleContentChange.bind(this)}
      />
    );
  }

  /**
   * Load snippets from AppStateService
   */
  private async loadSnippets(): Promise<void> {
    try {
      // Load snippets from StateDB through AppStateService
      await AppStateService.loadSnippets();
      const snippets = AppStateService.getSnippets();
      this._state = {
        ...this._state,
        snippets
      };
      this._stateChanged.emit(this._state);
      this.update();
    } catch (error) {
      console.error('[SnippetCreationWidget] Failed to load snippets:', error);
    }
  }

  /**
   * Generate a unique ID for a snippet
   */
  private generateSnippetId(): string {
    return AppStateService.generateSnippetId();
  }

  /**
   * Handle create new snippet
   */
  private handleCreateNew(): void {
    this._state = {
      ...this._state,
      isCreating: true,
      editingSnippet: null,
      viewingSnippet: null,
      title: '',
      description: '',
      content: ''
    };
    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Handle save snippet
   */
  private async handleSave(): Promise<void> {
    if (!this._state.title.trim() || !this._state.content.trim()) {
      return;
    }

    const now = new Date().toISOString();

    if (this._state.editingSnippet) {
      // Update existing snippet
      console.log(
        '[SnippetCreationWidget] Updating snippet with ID:',
        this._state.editingSnippet.id
      );
      console.log('[SnippetCreationWidget] New content:', {
        title: this._state.title.trim(),
        description: this._state.description.trim(),
        content: this._state.content.trim()
      });

      await AppStateService.updateSnippet(this._state.editingSnippet.id, {
        title: this._state.title.trim(),
        description: this._state.description.trim(),
        content: this._state.content.trim(),
        updatedAt: now
      });

      console.log('[SnippetCreationWidget] Snippet updated successfully');

      this._state = {
        ...this._state,
        snippets: AppStateService.getSnippets(),
        isCreating: false,
        editingSnippet: null,
        title: '',
        description: '',
        content: ''
      };
    } else {
      // Create new snippet
      console.log('[SnippetCreationWidget] Creating new snippet');
      const newSnippet: ISnippet = {
        id: this.generateSnippetId(),
        title: this._state.title.trim(),
        description: this._state.description.trim(),
        content: this._state.content.trim(),
        createdAt: now,
        updatedAt: now
      };

      await AppStateService.addSnippet(newSnippet);

      this._state = {
        ...this._state,
        snippets: AppStateService.getSnippets(),
        isCreating: false,
        title: '',
        description: '',
        content: ''
      };
    }

    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Handle edit snippet
   */
  private handleEdit(snippet: ISnippet): void {
    console.log('[SnippetCreationWidget] Editing snippet:', snippet);
    this._state = {
      ...this._state,
      isCreating: false,
      editingSnippet: snippet,
      title: snippet.title,
      description: snippet.description,
      content: snippet.content
    };
    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Handle view snippet (now same as edit for compatibility)
   */
  private handleView(snippet: ISnippet): void {
    this.handleEdit(snippet);
  }

  /**
   * Handle delete snippet
   */
  private async handleDelete(snippetId: string): Promise<void> {
    if (!confirm('Are you sure you want to delete this snippet?')) {
      return;
    }

    await AppStateService.removeSnippet(snippetId);

    this._state = {
      ...this._state,
      snippets: AppStateService.getSnippets(),
      editingSnippet: null
    };

    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Handle close form/viewer
   */
  private handleClose(): void {
    this._state = {
      ...this._state,
      isCreating: false,
      editingSnippet: null,
      title: '',
      description: '',
      content: ''
    };
    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Handle enable snippet (placeholder for future implementation)
   */
  private handleEnable(snippet: ISnippet): void {
    console.log('[SnippetCreationWidget] Enable snippet:', snippet.title);
    // TODO: Implement enable functionality
    // This would integrate with the chat context system
  }

  /**
   * Handle title change
   */
  private handleTitleChange(value: string): void {
    this._state = {
      ...this._state,
      title: value
    };
    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Handle description change
   */
  private handleDescriptionChange(value: string): void {
    this._state = {
      ...this._state,
      description: value
    };
    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Handle content change
   */
  private handleContentChange(value: string): void {
    this._state = {
      ...this._state,
      content: value
    };
    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Show the panel
   */
  public show(): void {
    this._state = {
      ...this._state,
      isVisible: true
    };
    this.removeClass('hidden');
    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Hide the panel
   */
  public hide(): void {
    this._state = {
      ...this._state,
      isVisible: false
    };
    this.addClass('hidden');
    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Check if the panel is currently visible
   */
  public getIsVisible(): boolean {
    return this._state.isVisible;
  }

  /**
   * Get the current state
   */
  public getState(): ISnippetCreationState {
    return { ...this._state };
  }

  /**
   * Get all snippets
   */
  public getSnippets(): ISnippet[] {
    return [...this._state.snippets];
  }

  /**
   * Handle close request when the widget is closed
   */
  protected onCloseRequest(): void {
    this.dispose();
  }

  /**
   * Dispose of the widget and clean up resources
   */
  dispose(): void {
    if (this.isDisposed) {
      return;
    }

    // Clear any state
    this._state = {
      isVisible: false,
      snippets: [],
      isCreating: false,
      editingSnippet: null,
      viewingSnippet: null,
      title: '',
      description: '',
      content: ''
    };

    // Apply hidden class since isVisible is false
    this.addClass('hidden');

    // Emit final state change
    this._stateChanged.emit(this._state);

    // Call parent dispose
    super.dispose();
  }
}
