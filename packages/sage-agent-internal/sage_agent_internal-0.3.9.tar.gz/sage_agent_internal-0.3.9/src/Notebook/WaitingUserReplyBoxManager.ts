import { AppStateService } from '../AppState';

export class WaitingUserReplyBoxManager {
  private container: HTMLElement | null = null;
  private waitingReplyBox: HTMLElement | null = null;
  private continueButton: HTMLElement | null = null;
  private promptButtons: HTMLElement[] = [];
  private onContinueCallback: (() => void) | null = null;
  private onPromptCallback: ((prompt: string) => void) | null = null;

  public initialize(container: HTMLElement): void {
    console.log('[WaitingUserReplyBoxManager] initialize() called');
    if (this.waitingReplyBox) {
      console.log(
        '[WaitingUserReplyBoxManager] Already initialized, returning early'
      );
      return;
    }

    this.container = container;
    console.log('[WaitingUserReplyBoxManager] Container set:', container);

    // Create the waiting reply box
    this.waitingReplyBox = document.createElement('div');
    this.waitingReplyBox.className = 'sage-ai-waiting-reply-container';

    const text = document.createElement('div');
    text.className = 'sage-ai-waiting-reply-text';
    text.textContent = 'Sage will continue working after you reply';

    this.waitingReplyBox.appendChild(text);

    // Create three prompt buttons
    const defaultPrompts = ['Continue'];

    const buttonsContainer = document.createElement('div');
    buttonsContainer.className = 'sage-ai-prompt-buttons-container';
    buttonsContainer.style.display = 'flex';
    buttonsContainer.style.flexDirection = 'column';
    buttonsContainer.style.gap = '8px';
    buttonsContainer.style.marginTop = '12px';

    defaultPrompts.forEach((prompt, index) => {
      const button = document.createElement('button');
      button.className = 'sage-ai-prompt-button';
      button.textContent = prompt;
      button.style.display = 'none';

      button.addEventListener('click', () => {
        console.log(
          `[WaitingUserReplyBoxManager] Prompt button ${index + 1} clicked:`,
          prompt
        );
        if (this.onPromptCallback) {
          console.log('[WaitingUserReplyBoxManager] Calling prompt callback');
          this.onPromptCallback(prompt);
        } else {
          console.warn('[WaitingUserReplyBoxManager] No prompt callback set');
        }
        this.hidePromptButtons();
      });

      this.promptButtons.push(button);
      buttonsContainer.appendChild(button);
    });

    this.waitingReplyBox.appendChild(buttonsContainer);

    // Create the continue button (initially hidden)
    this.continueButton = document.createElement('button');
    this.continueButton.className = 'sage-ai-continue-button';
    this.continueButton.textContent = 'Continue';
    this.continueButton.style.display = 'none';

    this.continueButton.addEventListener('click', () => {
      console.log('[WaitingUserReplyBoxManager] Continue button clicked');
      if (this.onContinueCallback) {
        console.log('[WaitingUserReplyBoxManager] Calling continue callback');
        this.onContinueCallback();
      } else {
        console.warn('[WaitingUserReplyBoxManager] No continue callback set');
      }
      this.hideContinueButton();
    });

    this.waitingReplyBox.appendChild(this.continueButton);

    this.hide();

    // Add to the container
    this.container.appendChild(this.waitingReplyBox);
    console.log(
      '[WaitingUserReplyBoxManager] Waiting reply box added to container'
    );
    console.log('[WaitingUserReplyBoxManager] Initialization complete');
  }

  public hide(): void {
    if (this.waitingReplyBox) {
      this.waitingReplyBox.style.display = 'none';
    }
  }

  public show(recommendedPrompts?: string[]): void {
    console.log('[WaitingUserReplyBoxManager] show() called');
    if (this.waitingReplyBox) {
      console.log(
        '[WaitingUserReplyBoxManager] Setting waiting reply box display to block'
      );
      this.waitingReplyBox.style.display = 'block';

      // Update prompt buttons with recommended prompts if provided
      if (recommendedPrompts && recommendedPrompts.length > 0) {
        this.updatePromptButtons(recommendedPrompts);
      }

      // Check if we should show the continue button
      this.checkAndShowContinueButton();
    } else {
      console.warn(
        '[WaitingUserReplyBoxManager] waitingReplyBox is null in show()'
      );
    }
  }

  public setContinueCallback(callback: () => void): void {
    console.log('[WaitingUserReplyBoxManager] Setting continue callback');
    this.onContinueCallback = callback;
  }

  public setPromptCallback(callback: (prompt: string) => void): void {
    console.log('[WaitingUserReplyBoxManager] Setting prompt callback');
    this.onPromptCallback = callback;
  }

  private checkAndShowContinueButton(): void {
    console.log(
      '[WaitingUserReplyBoxManager] checkAndShowContinueButton() called'
    );

    // Get the current thread from chat history manager
    const chatContainer = AppStateService.getState().chatContainer;
    console.log('[WaitingUserReplyBoxManager] chatContainer:', chatContainer);
    if (!chatContainer) {
      console.warn('[WaitingUserReplyBoxManager] No chatContainer found');
      return;
    }

    const currentThread =
      chatContainer.chatWidget.chatHistoryManager.getCurrentThread();
    console.log('[WaitingUserReplyBoxManager] currentThread:', currentThread);
    if (!currentThread) {
      console.warn('[WaitingUserReplyBoxManager] No currentThread found');
      return;
    }

    console.log(
      '[WaitingUserReplyBoxManager] continueButtonShown status:',
      currentThread.continueButtonShown
    );

    // Show prompt buttons only if they haven't been shown in this thread before
    if (!currentThread.continueButtonShown) {
      console.log(
        '[WaitingUserReplyBoxManager] Showing prompt buttons for the first time in this thread'
      );
      this.showPromptButtons();

      // Mark that continue button has been shown for this thread
      currentThread.continueButtonShown = true;

      // Update the thread in storage
      chatContainer.chatWidget.chatHistoryManager.updateCurrentThreadMessages(
        currentThread.messages,
        currentThread.contexts
      );
    } else {
      console.log(
        '[WaitingUserReplyBoxManager] Prompt buttons already shown in this thread, not showing again'
      );
    }
  }

  private showContinueButton(): void {
    console.log('[WaitingUserReplyBoxManager] showContinueButton() called');
    if (this.continueButton) {
      console.log(
        '[WaitingUserReplyBoxManager] Setting continue button display to inline-block'
      );
      this.continueButton.style.display = 'inline-block';
    } else {
      console.warn(
        '[WaitingUserReplyBoxManager] continueButton is null in showContinueButton()'
      );
    }
  }

  private hideContinueButton(): void {
    console.log('[WaitingUserReplyBoxManager] hideContinueButton() called');
    if (this.continueButton) {
      console.log(
        '[WaitingUserReplyBoxManager] Setting continue button display to none'
      );
      this.continueButton.style.display = 'none';
    } else {
      console.warn(
        '[WaitingUserReplyBoxManager] continueButton is null in hideContinueButton()'
      );
    }
  }

  private showPromptButtons(): void {
    console.log('[WaitingUserReplyBoxManager] showPromptButtons() called');
    this.promptButtons.forEach((button, index) => {
      if (button) {
        console.log(
          `[WaitingUserReplyBoxManager] Setting prompt button ${index + 1} display to block`
        );
        button.style.display = 'block';
      } else {
        console.warn(
          `[WaitingUserReplyBoxManager] promptButton ${index + 1} is null in showPromptButtons()`
        );
      }
    });
  }

  private hidePromptButtons(): void {
    console.log('[WaitingUserReplyBoxManager] hidePromptButtons() called');
    this.promptButtons.forEach((button, index) => {
      if (button) {
        console.log(
          `[WaitingUserReplyBoxManager] Setting prompt button ${index + 1} display to none`
        );
        button.style.display = 'none';
      } else {
        console.warn(
          `[WaitingUserReplyBoxManager] promptButton ${index + 1} is null in hidePromptButtons()`
        );
      }
    });
  }

  /**
   * Update the prompt buttons with new recommended prompts
   * @param recommendedPrompts List of recommended prompts to display
   */
  private updatePromptButtons(recommendedPrompts: string[]): void {
    console.log(
      '[WaitingUserReplyBoxManager] updatePromptButtons() called with prompts:',
      recommendedPrompts
    );

    // Update button text and make sure we have enough buttons
    const maxPrompts = Math.min(
      recommendedPrompts.length,
      this.promptButtons.length
    );

    for (let i = 0; i < this.promptButtons.length; i++) {
      const button = this.promptButtons[i];
      if (button) {
        if (i < maxPrompts) {
          // Update button text and make it visible
          button.textContent = recommendedPrompts[i];
          button.style.display = 'block';
          console.log(
            `[WaitingUserReplyBoxManager] Updated prompt button ${i + 1} to: "${recommendedPrompts[i]}"`
          );
        } else {
          // Hide extra buttons
          button.style.display = 'none';
        }
      }
    }
  }
}
