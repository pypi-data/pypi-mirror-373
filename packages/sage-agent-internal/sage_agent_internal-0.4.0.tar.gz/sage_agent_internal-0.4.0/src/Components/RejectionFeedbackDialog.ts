/**
 * Dialog component for gathering feedback when a user rejects cell execution
 */
export class RejectionFeedbackDialog {
  /**
   * Show a dialog to collect feedback about why the cell execution was rejected
   */
  public async showDialog(): Promise<string> {
    // Create a modal dialog for feedback
    const modal = document.createElement('div');
    modal.className = 'sage-ai-modal';

    const dialog = document.createElement('div');
    dialog.className = 'sage-ai-dialog';

    const title = document.createElement('h3');
    title.textContent = 'Cell Execution Rejected';
    title.className = 'sage-ai-dialog-title';

    const label = document.createElement('label');
    label.textContent =
      'Could you explain why you rejected the code execution? This will help improve the next attempt:';
    label.className = 'sage-ai-dialog-label';

    const textarea = document.createElement('textarea');
    textarea.className = 'sage-ai-dialog-textarea';

    const buttonContainer = document.createElement('div');
    buttonContainer.className = 'sage-ai-dialog-button-container';

    const submitButton = document.createElement('button');
    submitButton.textContent = 'Submit';
    submitButton.className = 'sage-ai-dialog-submit-button';

    buttonContainer.appendChild(submitButton);
    dialog.appendChild(title);
    dialog.appendChild(label);
    dialog.appendChild(textarea);
    dialog.appendChild(buttonContainer);
    modal.appendChild(dialog);

    document.body.appendChild(modal);

    return new Promise<string>(resolve => {
      submitButton.addEventListener('click', () => {
        const rejectionReason = textarea.value.trim();
        document.body.removeChild(modal);
        resolve(rejectionReason);
      });
    });
  }
}
