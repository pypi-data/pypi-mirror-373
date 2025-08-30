import * as React from 'react';
import { SnippetListProps } from './types';
import { ISnippet, AppStateService } from '../../AppState';
import { INSERT_ICON } from '../../Chat/ChatContextMenu/icons';

/**
 * Component for displaying the list of snippets
 */
export function SnippetList({
  snippets,
  onView,
  onDelete,
  onCreateNew
}: SnippetListProps): JSX.Element {
  const [selectedSnippet, setSelectedSnippet] = React.useState<ISnippet | null>(
    null
  );
  const [openMenuId, setOpenMenuId] = React.useState<string | null>(null);
  const [insertedSnippets, setInsertedSnippets] = React.useState<string[]>([]);

  // Load inserted snippets on mount
  React.useEffect(() => {
    const loadInsertedSnippets = () => {
      const currentState = AppStateService.getState();
      setInsertedSnippets(currentState.insertedSnippets);
    };

    // Load initial state
    loadInsertedSnippets();

    // Subscribe to app state changes
    const subscription =
      AppStateService.changes.subscribe(loadInsertedSnippets);

    return () => subscription.unsubscribe();
  }, []);

  // Update selectedSnippet when snippets change (to reflect updates)
  React.useEffect(() => {
    if (selectedSnippet) {
      const updatedSnippet = snippets.find(
        snippet => snippet.id === selectedSnippet.id
      );
      if (
        updatedSnippet &&
        (updatedSnippet.title !== selectedSnippet.title ||
          updatedSnippet.content !== selectedSnippet.content ||
          updatedSnippet.description !== selectedSnippet.description)
      ) {
        setSelectedSnippet(updatedSnippet);
      } else if (!updatedSnippet) {
        // Snippet was deleted
        setSelectedSnippet(null);
      }
    }
  }, [snippets, selectedSnippet]);

  // Close context menu when clicking outside
  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Element;
      if (
        !target.closest('.sage-ai-snippet-context-menu') &&
        !target.closest('.sage-ai-snippet-menu-btn')
      ) {
        setOpenMenuId(null);
      }
    };

    document.addEventListener('click', handleClickOutside);
    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  }, []);

  const handleSnippetClick = (snippet: ISnippet) => {
    setSelectedSnippet(selectedSnippet?.id === snippet.id ? null : snippet);
  };

  const handleContextMenu = (e: React.MouseEvent, snippetId: string) => {
    e.stopPropagation();
    setOpenMenuId(openMenuId === snippetId ? null : snippetId);
  };

  const handleEdit = (e: React.MouseEvent, snippet: ISnippet) => {
    e.stopPropagation();
    setOpenMenuId(null);
    onView(snippet); // This will trigger edit mode in the parent
  };

  const handleDelete = (e: React.MouseEvent, snippetId: string) => {
    e.stopPropagation();
    setOpenMenuId(null);
    onDelete(snippetId);
  };

  const handleInsert = async (snippet: ISnippet) => {
    try {
      const isInserted = insertedSnippets.includes(snippet.id);

      if (isInserted) {
        // Remove snippet from inserted snippets list in AppState
        await AppStateService.removeInsertedSnippet(snippet.id);
        console.log('Snippet removed from context');
      } else {
        // Add snippet to inserted snippets list in AppState
        await AppStateService.addInsertedSnippet(snippet.id);

        // Copy content to clipboard for immediate use
        navigator.clipboard
          .writeText(snippet.content)
          .then(() => {
            console.log(
              'Snippet content copied to clipboard and added to context'
            );
          })
          .catch(err => {
            console.error('Failed to copy snippet content:', err);
          });
      }
    } catch (error) {
      console.error('Failed to update snippet in inserted list:', error);
    }
  };

  return (
    <div className="sage-ai-snippet-list">
      <div className="sage-ai-snippet-list-container">
        {snippets.length === 0 ? (
          <div className="sage-ai-snippet-empty">
            <p>No rules created yet.</p>
            <p>Click the + button to create your first snippet.</p>
          </div>
        ) : (
          <div className="sage-ai-snippet-items">
            {snippets.map(snippet => (
              <div key={snippet.id} className="sage-ai-snippet-item-container">
                <div
                  className={`sage-ai-snippet-item ${selectedSnippet?.id === snippet.id ? 'selected' : ''}`}
                  onClick={() => handleSnippetClick(snippet)}
                >
                  <div className="sage-ai-snippet-item-header">
                    <div className="sage-ai-snippet-title-container">
                      <h5>{snippet.title}</h5>
                      {insertedSnippets.includes(snippet.id) && (
                        <svg
                          className="sage-ai-snippet-checkmark"
                          width="16"
                          height="16"
                          viewBox="0 0 24 24"
                          fill="none"
                        >
                          <path
                            d="M20 6L9 17l-5-5"
                            stroke="currentColor"
                            strokeWidth="2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                          />
                        </svg>
                      )}
                    </div>
                    <div className="sage-ai-snippet-item-actions">
                      <button
                        className="sage-ai-snippet-menu-btn"
                        onClick={e => handleContextMenu(e, snippet.id)}
                        title="More options"
                      >
                        ⋯
                      </button>
                      {openMenuId === snippet.id && (
                        <div className="sage-ai-snippet-context-menu">
                          <button
                            onClick={e => handleEdit(e, snippet)}
                            className="sage-ai-snippet-menu-item"
                          >
                            Edit
                          </button>
                          <button
                            onClick={e => handleDelete(e, snippet.id)}
                            className="sage-ai-snippet-menu-item delete"
                          >
                            Delete
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {selectedSnippet && (
        <div className="sage-ai-snippet-viewer-inline">
          {/* First Row: Snippet Preview | Insert | Edit Icon | Close Icon */}
          <div className="sage-ai-snippet-viewer-toolbar">
            <span className="sage-ai-snippet-preview-label">
              Snippet Preview
            </span>
            <div className="sage-ai-snippet-viewer-actions">
              <button
                className={`sage-ai-snippet-insert-btn ${
                  insertedSnippets.includes(selectedSnippet.id)
                    ? 'sage-ai-snippet-remove-state'
                    : ''
                }`}
                onClick={() => handleInsert(selectedSnippet)}
                title={
                  insertedSnippets.includes(selectedSnippet.id)
                    ? 'Remove from context'
                    : 'Add to LLM Context'
                }
              >
                {insertedSnippets.includes(selectedSnippet.id)
                  ? 'Remove'
                  : 'Insert'}
                <div className="insert-icon-container">
                  <INSERT_ICON.react />
                </div>
              </button>
              <button
                className="sage-ai-snippet-edit-btn"
                onClick={e => handleEdit(e, selectedSnippet)}
                title="Edit snippet"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <path
                    d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                  <path
                    d="m18.5 2.5 3 3L12 15l-4 1 1-4 9.5-9.5z"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </button>
              <button
                className="sage-ai-snippet-close-btn"
                onClick={() => setSelectedSnippet(null)}
                title="Close preview"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <path
                    d="M18 6L6 18M6 6l12 12"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </button>
            </div>
          </div>

          {/* Second Row: Title */}
          <div className="sage-ai-snippet-viewer-title-row">
            <span className="sage-ai-snippet-title-label">Title:</span>
            <span className="sage-ai-snippet-title-text">
              {selectedSnippet.title}
            </span>
          </div>

          {selectedSnippet.description && (
            <p className={'sage-ai-snippet-description'}>
              {selectedSnippet.description}
            </p>
          )}

          {/* Third Row: Snippet Content */}
          <div className="sage-ai-snippet-code-block">
            <pre className="sage-ai-snippet-code-content">
              <code>{selectedSnippet.content}</code>
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
