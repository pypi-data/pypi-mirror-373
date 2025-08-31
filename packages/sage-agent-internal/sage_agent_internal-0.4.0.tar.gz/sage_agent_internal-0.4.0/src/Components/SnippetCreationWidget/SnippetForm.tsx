import * as React from 'react';
import { SnippetFormProps } from './types';

/**
 * Component for creating/editing snippets
 */
export function SnippetForm({
  title,
  description,
  content,
  isEditing,
  onSave,
  onClose,
  onTitleChange,
  onDescriptionChange,
  onContentChange
}: SnippetFormProps): JSX.Element {
  return (
    <div className="sage-ai-snippet-form">
      <div className="sage-ai-snippet-form-group">
        <label>Title</label>
        <input
          type="text"
          value={title}
          onChange={(e) => onTitleChange(e.target.value)}
          placeholder="Enter snippet title..."
          autoFocus
        />
      </div>
      
      <div className="sage-ai-snippet-form-group">
        <label>Description</label>
        <input
          type="text"
          value={description}
          onChange={(e) => onDescriptionChange(e.target.value)}
          placeholder="Brief description..."
        />
      </div>
      
      <div className="sage-ai-snippet-form-group">
        <label>Content</label>
        <textarea
          value={content}
          onChange={(e) => onContentChange(e.target.value)}
          placeholder="Your code, markdown, or text content..."
          rows={10}
        />
      </div>
      
      <div className="sage-ai-snippet-form-actions">
        <button
          className="sage-ai-snippet-save-btn"
          onClick={onSave}
          disabled={!title.trim() || !content.trim()}
        >
          {isEditing ? 'Update' : 'Save'}
        </button>
        <button
          className="sage-ai-snippet-cancel-btn"
          onClick={onClose}
        >
          Cancel
        </button>
      </div>
    </div>
  );
}
