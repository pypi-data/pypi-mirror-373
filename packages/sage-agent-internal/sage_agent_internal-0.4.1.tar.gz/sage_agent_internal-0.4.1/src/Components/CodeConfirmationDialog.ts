import { AppStateService } from '../AppState';
import { ChatMessages } from '../Chat/ChatMessages';

/**
 * A component for displaying a code execution confirmation dialog
 */
export class CodeConfirmationDialog {
  private chatHistory: HTMLDivElement;
  private messageComponent: ChatMessages;
  private confirmationContainer: HTMLDivElement | null = null;
  private isShowing: boolean = false;

  // Add properties to support external control
  private currentResolver: ((value: boolean) => void) | null = null;
  private currentKeyboardHandler: ((event: KeyboardEvent) => void) | null =
    null;

  constructor(chatHistory: HTMLDivElement, messageComponent: ChatMessages) {
    this.chatHistory = chatHistory;
    this.messageComponent = messageComponent;
  }

  /**
   * Externally trigger approval of the current confirmation dialog
   * This can be called from LLMStateDisplay buttons
   */
  public triggerApproval(): void {
    if (this.isShowing && this.currentResolver) {
      this.executeApproval();
    }
  }

  /**
   * Externally trigger rejection of the current confirmation dialog
   * This can be called from LLMStateDisplay buttons
   */
  public triggerRejection(): void {
    if (this.isShowing && this.currentResolver) {
      this.executeRejection();
    }
  }

  /**
   * Execute the approval logic
   */
  private executeApproval(): void {
    if (this.confirmationContainer) {
      this.chatHistory.removeChild(this.confirmationContainer);
      this.confirmationContainer = null;
    }
    if (this.currentResolver) {
      this.currentResolver(true);
    }
    this.cleanup();
  }

  /**
   * Execute the rejection logic
   */
  private executeRejection(): void {
    if (this.confirmationContainer) {
      this.chatHistory.removeChild(this.confirmationContainer);
      this.confirmationContainer = null;
    }
    if (this.currentResolver) {
      this.currentResolver(false);
    }
    this.cleanup();
  }

  /**
   * Clean up the current confirmation state
   */
  private cleanup(): void {
    this.isShowing = false;
    this.currentResolver = null;
    if (this.currentKeyboardHandler) {
      document.removeEventListener('keydown', this.currentKeyboardHandler);
      this.currentKeyboardHandler = null;
    }
  }

  /**
   * Show a confirmation dialog for code execution
   * @param cellId The cell id to be executed
   * @param isProcessingStopped Whether the processing has been stopped
   * @returns A promise that resolves to true if execution is approved, false otherwise
   */
  public async showConfirmation(
    cellId?: string,
    isProcessingStopped?: boolean
  ): Promise<boolean> {
    // If processing has been stopped, don't show the dialog and return false
    if (isProcessingStopped) {
      return false;
    }

    this.isShowing = true;

    return new Promise<boolean>(resolve => {
      // Store the resolver for external control
      this.currentResolver = resolve;

      // Create an inline confirmation message in the chat
      this.confirmationContainer = document.createElement('div');
      this.confirmationContainer.className = 'sage-ai-code-confirmation';

      const codeIcon = `<svg width="14px" height="14px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path fill-rule="evenodd" clip-rule="evenodd" d="M4.5 6L5.25 5.25H18.75L19.5 6V18L18.75 18.75H5.25L4.5 18V6ZM6 6.75V17.25H18V6.75H6ZM10.1894 12L7.71973 9.5303L8.78039 8.46964L12.3107 12L8.78039 15.5303L7.71973 14.4696L10.1894 12ZM12 15.75H15.75V14.25H12V15.75Z" fill="var(--jp-ui-font-color0)"></path> </g></svg>`;

      // Add heading
      const heading = document.createElement('span');
      heading.style.fontSize = 'var(--jp-ui-font-size1)';
      heading.style.color = 'var(--jp-ui-font-color1)';
      heading.style.fontWeight = '500';
      heading.style.display = 'flex';
      heading.style.alignItems = 'center';
      heading.style.gap = '4px';

      heading.innerHTML = `${codeIcon} Sage is trying to run ${cellId || 'cell'}`;
      heading.className = 'sage-ai-code-confirmation-heading';
      this.confirmationContainer.appendChild(heading);

      const buttonContainer = document.createElement('div');
      buttonContainer.className = 'sage-ai-confirmation-button-container';

      const cancelButton = document.createElement('button');
      cancelButton.textContent = 'Reject';
      cancelButton.className = 'sage-ai-reject-button';

      const confirmButton = document.createElement('button');
      // Detect platform for modifier key
      const isMac = /Mac|iPod|iPhone|iPad/.test(navigator.platform);
      // Unicode icons for Cmd, Ctrl, and Enter
      const cmdIcon = '\u2318'; // ⌘
      const ctrlIcon = '\u2303'; // ⌃
      const enterIcon = '\u23CE'; // ⏎

      // Compose label: [Cmd|Ctrl] + Enter
      let modifierIcon = isMac ? cmdIcon : ctrlIcon;

      // Create a span for the button label
      const labelSpan = document.createElement('span');
      labelSpan.style.display = 'flex';
      labelSpan.style.alignItems = 'center';

      // Add modifier icon/text
      const modSpan = document.createElement('span');
      modSpan.style.display = 'inline-flex';
      modSpan.style.alignItems = 'center';
      modSpan.style.fontFamily = 'monospace';
      modSpan.style.fontWeight = 'bold';
      modSpan.style.marginLeft = '4px';
      modSpan.style.marginRight = '2px';
      modSpan.textContent = modifierIcon;

      // Add enter icon/text
      const enterSpan = document.createElement('span');
      enterSpan.style.display = 'inline-flex';
      enterSpan.style.alignItems = 'center';
      enterSpan.style.fontFamily = 'monospace';
      enterSpan.style.fontWeight = 'bold';
      enterSpan.textContent = enterIcon;

      // Add "Run" label
      const runSpan = document.createElement('span');
      runSpan.style.fontSize = 'var(--jp-ui-font-size1)';
      runSpan.textContent = 'Run';

      // Compose the label: [Run] [Cmd/Ctrl icon + text] + [Enter icon + text]
      labelSpan.appendChild(runSpan);
      labelSpan.appendChild(modSpan);
      labelSpan.appendChild(enterSpan);

      confirmButton.appendChild(labelSpan);
      confirmButton.className = 'sage-ai-confirm-button';

      buttonContainer.appendChild(cancelButton);
      buttonContainer.appendChild(confirmButton);

      const bottomContainer = document.createElement('div');
      bottomContainer.className = 'sage-ai-confirmation-bottom-container';
      bottomContainer.appendChild(buttonContainer);

      this.confirmationContainer.appendChild(bottomContainer);

      // Add the confirmation container to the chat history
      this.chatHistory.appendChild(this.confirmationContainer);

      this.messageComponent.handleScroll();

      // Keyboard event handler for the entire document
      const keyboardHandler = (event: KeyboardEvent) => {
        // Check for Cmd+Enter (macOS) or Ctrl+Enter (Windows/Linux)
        if (event.key === 'Enter' && (event.metaKey || event.ctrlKey)) {
          event.preventDefault();
          this.executeApproval();
        }
      };

      // Store reference to keyboard handler for cleanup
      this.currentKeyboardHandler = keyboardHandler;

      // Add keyboard event listener
      document.addEventListener('keydown', keyboardHandler);

      // Set up button event handlers
      confirmButton.addEventListener('click', () => {
        this.executeApproval();
      });

      cancelButton.addEventListener('click', () => {
        this.executeRejection();
      });
    });
  }

  /**
   * Check if the confirmation dialog is currently showing
   */
  public isDialogShowing(): boolean {
    return this.isShowing;
  }
}
