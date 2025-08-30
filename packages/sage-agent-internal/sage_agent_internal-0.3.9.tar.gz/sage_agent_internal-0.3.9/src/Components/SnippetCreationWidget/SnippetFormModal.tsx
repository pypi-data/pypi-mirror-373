import * as React from 'react';
import { Modal, Button, Form } from 'react-bootstrap';
import { SnippetFormProps } from './types';

/**
 * Modal component for creating/editing snippets
 */
export function SnippetFormModal({
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
  // Handle form submission with Enter key
  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {
      if (title.trim() && content.trim()) {
        onSave();
      }
    }
  };

  return (
    <Modal
      show={true}
      onHide={onClose}
      size="lg"
      backdrop="static"
      keyboard={true}
      onKeyDown={handleKeyDown}
      dialogClassName="sage-ai-custom-snippet-modal"
    >
      <Modal.Header closeButton>
        <Modal.Title>
          {isEditing ? 'Edit Snippet' : 'Create New Snippet'}
        </Modal.Title>
      </Modal.Header>

      <Modal.Body>
        <Form>
          <Form.Group className="mb-3">
            <Form.Label>Title</Form.Label>
            <Form.Control
              type="text"
              value={title}
              onChange={e => onTitleChange(e.target.value)}
              placeholder="Enter rule title..."
              autoFocus
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Description</Form.Label>
            <Form.Control
              type="text"
              value={description}
              onChange={e => onDescriptionChange(e.target.value)}
              placeholder="Brief description..."
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Content</Form.Label>
            <Form.Control
              as="textarea"
              rows={10}
              value={content}
              onChange={e => onContentChange(e.target.value)}
              placeholder="Your code, markdown, or text content..."
            />
          </Form.Group>
        </Form>
      </Modal.Body>

      <Modal.Footer>
        <Button variant="secondary" onClick={onClose}>
          Cancel
        </Button>
        <Button
          variant="primary"
          onClick={onSave}
          disabled={!title.trim() || !content.trim()}
          title={`${isEditing ? 'Update' : 'Save'} snippet (Ctrl+Enter)`}
        >
          {isEditing ? 'Update' : 'Save'}
        </Button>
      </Modal.Footer>
    </Modal>
  );
}
