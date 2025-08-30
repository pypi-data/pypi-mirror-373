import { Widget } from '@lumino/widgets';

export interface NewChatDisplayCallbacks {
  onPromptSelected: (prompt: string) => void;
  onRemoveDisplay: () => void;
}

export interface NewChatDisplayOptions {
  callbacks: NewChatDisplayCallbacks;
  recommendedPrompts: string[];
}

/**
 * Widget displayed when there are no messages in the current chat
 */
export class NewChatDisplayWidget extends Widget {
  private callbacks: NewChatDisplayCallbacks;
  private recommendedPrompts: string[];

  constructor(
    callbacks: NewChatDisplayCallbacks,
    recommendedPrompts: string[]
  ) {
    super();
    this.callbacks = callbacks;
    this.recommendedPrompts = recommendedPrompts;
    this.addClass('sage-ai-new-chat-display');
    this.node.style.height = '100%';
    this.buildContent();
  }

  private buildContent(): void {
    // Create the main container
    const container = document.createElement('div');
    container.className = 'sage-ai-new-chat-container';

    // Create title section
    const titleSection = document.createElement('div');
    titleSection.className = 'sage-ai-new-chat-title-section';

    const newChatTitle = document.createElement('h2');
    newChatTitle.className = 'sage-ai-new-chat-title';
    newChatTitle.textContent = 'New Chat';

    const helpText = document.createElement('p');
    helpText.className = 'sage-ai-new-chat-help';
    helpText.textContent = 'How can I help you?';

    titleSection.appendChild(newChatTitle);
    titleSection.appendChild(helpText);

    // Create prompts section
    const promptsSection = document.createElement('div');
    promptsSection.className = 'sage-ai-new-chat-prompts-section';

    // Create prompt buttons
    const promptsList = document.createElement('div');
    promptsList.className = 'sage-ai-new-chat-prompts-list';

    this.recommendedPrompts.forEach((prompt: string) => {
      const button = document.createElement('button');
      button.className = 'sage-ai-new-chat-prompt-button';
      button.textContent = prompt;
      button.addEventListener('click', () => {
        this.callbacks.onPromptSelected(prompt);
        this.callbacks.onRemoveDisplay();
      });
      promptsList.appendChild(button);
    });

    promptsSection.appendChild(promptsList);

    // Add all sections to container
    container.appendChild(titleSection);
    container.appendChild(promptsSection);

    // Set the container as the widget's node
    this.node.appendChild(container);
  }
}
