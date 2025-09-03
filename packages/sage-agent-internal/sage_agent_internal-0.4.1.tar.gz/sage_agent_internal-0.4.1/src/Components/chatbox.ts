import { ChatMessages } from '../Chat/ChatMessages';
import { ConversationService } from '../Chat/ConversationService';
import { PanelLayout, Widget } from '@lumino/widgets';
import { ConfigService } from '../Config/ConfigService';
import { IChatService } from '../Services/IChatService';
import { ServiceFactory, ServiceProvider } from '../Services/ServiceFactory';
import { ChatHistoryManager, IChatThread } from '../Chat/ChatHistoryManager';
import { ThreadManager } from '../ThreadManager';
import { ChatInputManager } from '../Chat/ChatInputManager';
import { RichTextChatInput } from '../Chat/RichTextChatInput';
import { ChatUIHelper } from '../Chat/ChatUIHelper';
import { AnthropicService } from '../Services/AnthropicService';
import { AppStateService } from '../AppState';
import { ChatboxContext } from './ChatboxContext';
import { NewChatDisplayWidget } from './NewChatDisplayWidget';
import { LLMStateDisplay } from './LLMStateDisplay/LLMStateDisplay';
import {
  AGENT_MODE_ICON,
  AGENT_MODE_SHINY_ICON,
  ASK_ICON,
  HANDS_ON_MODE_ICON,
  OPEN_MODE_SELECTOR_ICON,
  SEND_ICON
} from './icons';
import { PlanStateDisplay } from './PlanStateDisplay';
import { MoreOptionsDisplay } from './MoreOptionsDisplay';
import { UpdateBannerWidget } from './UpdateBanner/UpdateBannerWidget';
import { Subscription } from 'rxjs';
import { ActionHistory } from '../Chat/ActionHistory';

// Recommended prompts for new chat display
const RECOMMENDED_PROMPTS: string[] = [
  // 'Analyze the data in my notebook'
  // 'Create a visualization from my data',
  // 'Help me clean and preprocess this dataset',
  // 'Build a machine learning model',
  // 'Explain this code and suggest improvements'
];

/**
 * ChatBoxWidget: A widget for interacting with AI services via a chat interface
 */
export class ChatBoxWidget extends Widget {
  private chatHistory: HTMLDivElement;
  private chatInput: RichTextChatInput;
  private sendButton: HTMLButtonElement;
  private newChatButton: HTMLButtonElement;
  private undoButton: HTMLButtonElement;
  public autorunCheckbox: HTMLInputElement;
  private lastNotebookId: string | null = null;

  private threadSelectorButton: HTMLButtonElement;
  private modeSelector: HTMLDivElement;
  private threadNameDisplay: HTMLSpanElement;
  private modeSelectorDropdown: HTMLDivElement;
  private modeSelectorOptions: Map<string, HTMLDivElement> = new Map();
  private modeName: 'agent' | 'ask' | 'fast' = 'agent';

  // Widget management
  private historyWidget: Widget | null = null;
  private newChatDisplayWidget: NewChatDisplayWidget | null = null;
  public llmStateDisplay: LLMStateDisplay;
  private planStateDisplay: PlanStateDisplay;
  private moreOptionsDisplay: MoreOptionsDisplay;
  private updateBanner: UpdateBannerWidget | null = null;
  private scrollDownButton: HTMLButtonElement;

  // Chat services
  public messageComponent: ChatMessages;
  private chatService: IChatService;
  public conversationService: ConversationService;
  private currentServiceProvider: ServiceProvider = ServiceProvider.ANTHROPIC;
  public chatHistoryManager: ChatHistoryManager;

  // Helper classes
  public threadManager: ThreadManager;
  public inputManager: ChatInputManager;
  private uiHelper: ChatUIHelper;
  private contextHandler: ChatboxContext;

  // Observer cleanup
  private resizeObserver?: ResizeObserver;
  private mutationObserver?: MutationObserver;
  private llmStateConnection?: any;
  private planStateConnection?: any;
  private appStateSubscription?: Subscription;
  private lastClaudeSettings?: {
    claudeApiKey: string;
    claudeModelId: string;
    claudeModelUrl: string;
  };

  constructor(actionHistory: ActionHistory) {
    super();
    this.id = 'sage-ai-chat';
    this.title.label = 'AI Chat';
    this.title.closable = true;
    this.addClass('sage-ai-chatbox');

    // Initialize the chat history manager
    this.chatHistoryManager = new ChatHistoryManager();

    // Initialize services
    this.chatService = ServiceFactory.createService(
      this.currentServiceProvider
    );

    AppStateService.setChatService(this.chatService);

    // Create layout for the chat box
    const layout = new PanelLayout();
    this.layout = layout;

    // Create toolbar
    const toolbar = document.createElement('div');
    toolbar.className = 'sage-ai-toolbar';

    // Create thread selector button
    this.threadSelectorButton = document.createElement('button');
    this.threadSelectorButton.className =
      'sage-ai-icon-button-md sage-ai-thread-selector-button';

    // Add chat icon SVG
    this.threadSelectorButton.innerHTML = `
     <svg width="20" height="21" viewBox="0 0 20 21" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M2.5 10.5H17.5M2.5 5.5H17.5M2.5 15.5H17.5" stroke="#949494" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    `;
    this.threadSelectorButton.title = 'Select conversation thread';

    toolbar.appendChild(this.threadSelectorButton);

    // Create thread name display
    this.threadNameDisplay = document.createElement('span');
    this.threadNameDisplay.className = 'sage-ai-thread-name';
    this.threadNameDisplay.textContent =
      this.chatHistoryManager.getCurrentThread()?.name || 'New Chat';
    toolbar.appendChild(this.threadNameDisplay);

    // Create autorun checkbox container
    const checkboxContainer = document.createElement('div');
    checkboxContainer.className =
      'sage-ai-checkbox-container sage-ai-autorun-toggle sage-ai-control-base';

    this.autorunCheckbox = document.createElement('input');
    this.autorunCheckbox.id = 'sage-ai-autorun';
    this.autorunCheckbox.type = 'checkbox';
    this.autorunCheckbox.className = 'sage-ai-checkbox sage-ai-toggle-input';
    this.autorunCheckbox.title = 'Automatically run code without confirmation';

    const checkboxLabel = document.createElement('label');
    checkboxLabel.htmlFor = 'sage-ai-autorun';
    checkboxLabel.className = 'sage-ai-checkbox-label sage-ai-toggle-label';
    checkboxLabel.innerHTML = `
      <span class="sage-ai-toggle-switch"></span>
      Auto Run
    `;
    checkboxLabel.title = 'Automatically run code without confirmation';

    checkboxContainer.appendChild(this.autorunCheckbox);
    checkboxContainer.appendChild(checkboxLabel);

    // Create new chat button (previously reset button)
    this.newChatButton = document.createElement('button');
    this.newChatButton.className = 'sage-ai-reset-button sage-ai-control-base';
    this.newChatButton.innerHTML = `
      <svg width="16" height="17" viewBox="0 0 16 17" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M3.3335 8.49992H12.6668M8.00016 3.83325V13.1666" stroke="var(--jp-ui-font-color0)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    `;
    this.newChatButton.title = 'Start a new chat';
    this.newChatButton.addEventListener('click', () => this.createNewChat());

    // Create undo button
    this.undoButton = document.createElement('button');
    this.undoButton.className = 'sage-ai-undo-button sage-ai-control-base';
    this.undoButton.innerHTML = `
      <svg width="16" height="17" viewBox="0 0 16 17" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M5.99984 9.83341L2.6665 6.50008M2.6665 6.50008L5.99984 3.16675M2.6665 6.50008H9.6665C10.148 6.50008 10.6248 6.59492 11.0697 6.77919C11.5145 6.96346 11.9187 7.23354 12.2592 7.57402C12.5997 7.9145 12.8698 8.31871 13.0541 8.76357C13.2383 9.20844 13.3332 9.68523 13.3332 10.1667C13.3332 10.6483 13.2383 11.1251 13.0541 11.5699C12.8698 12.0148 12.5997 12.419 12.2592 12.7595C11.9187 13.1 11.5145 13.37 11.0697 13.5543C10.6248 13.7386 10.148 13.8334 9.6665 13.8334H7.33317" stroke="var(--jp-ui-font-color0)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    `;
    this.undoButton.disabled = true;
    this.undoButton.title = 'No action to undo';
    this.undoButton.addEventListener('click', () => this.undoLastAction());

    // Create a button to show more options
    const moreOptionsButton = document.createElement('button');
    moreOptionsButton.className =
      'sage-ai-more-options-button sage-ai-icon-button-md';
    moreOptionsButton.innerHTML = `
      <svg width="18" height="19" viewBox="0 0 18 19" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M9 10.25C9.41421 10.25 9.75 9.91421 9.75 9.5C9.75 9.08579 9.41421 8.75 9 8.75C8.58579 8.75 8.25 9.08579 8.25 9.5C8.25 9.91421 8.58579 10.25 9 10.25Z" stroke="var(--jp-ui-font-color0)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M14.25 10.25C14.6642 10.25 15 9.91421 15 9.5C15 9.08579 14.6642 8.75 14.25 8.75C13.8358 8.75 13.5 9.08579 13.5 9.5C13.5 9.91421 13.8358 10.25 14.25 10.25Z" stroke="var(--jp-ui-font-color0)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M3.75 10.25C4.16421 10.25 4.5 9.91421 4.5 9.5C4.5 9.08579 4.16421 8.75 3.75 8.75C3.33579 8.75 3 9.08579 3 9.5C3 9.91421 3.33579 10.25 3.75 10.25Z" stroke="var(--jp-ui-font-color0)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    `;
    moreOptionsButton.title = 'More options';
    moreOptionsButton.addEventListener('click', () => this.showMoreOptions());

    // Add buttons to toolbar
    toolbar.appendChild(checkboxContainer);
    // toolbar.appendChild(this.undoButton);
    toolbar.appendChild(this.newChatButton);
    toolbar.appendChild(moreOptionsButton);

    // Create chat history container
    const historyContainer = document.createElement('div');
    historyContainer.className = 'sage-ai-history-container';
    this.chatHistory = document.createElement('div');
    this.chatHistory.className = 'sage-ai-chat-history';
    this.chatHistory.setAttribute('data-is-scrolled-to-bottom', 'true');
    historyContainer.appendChild(this.chatHistory);

    this.scrollDownButton = document.createElement('button');
    this.scrollDownButton.className = 'sage-ai-scroll-down-button hidden';
    this.scrollDownButton.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M8 10.25L12.5 5.75L13.25 6.5L8 11.75L2.75 6.5L3.5 5.75L8 10.25Z" fill="var(--jp-ui-font-color1" />
      </svg>
    `;
    this.scrollDownButton.addEventListener('click', () => {
      this.messageComponent.scrollToBottom();
      this.hideScrollDownButton();
    });
    historyContainer.appendChild(this.scrollDownButton);

    const chatHistoryResizeObserver = new ResizeObserver(() =>
      this.handleChatHistoryResize()
    );
    chatHistoryResizeObserver.observe(this.chatHistory);

    let userScrolled = false;
    let userScrollTimeout: NodeJS.Timeout | null = null;

    // Mark user-initiated scroll
    ['wheel', 'touchstart', 'keydown'].forEach(eventType => {
      window.addEventListener(eventType, () => {
        userScrolled = true;

        userScrollTimeout && clearTimeout(userScrollTimeout);
        userScrollTimeout = setTimeout(() => {
          userScrolled = false;
        }, 1000); // reset after 1s
      });
    });
    this.chatHistory.addEventListener('scroll', () => {
      // As the chat-history height change, we need to check if the user is scrolling
      // or the chat-history is being resized
      if (userScrolled) {
        const isScrolledToBottom = this.updateScrollAttribute();

        if (isScrolledToBottom) {
          this.hideScrollDownButton();
        } else {
          this.showScrollDownButton();
        }
      }
    });

    // Create the initial history widget
    this.historyWidget = new Widget({ node: historyContainer });

    // Initialize LLM state display
    this.llmStateDisplay = new LLMStateDisplay();

    this.planStateDisplay = AppStateService.getPlanStateDisplay();

    // Initialize more options display
    this.moreOptionsDisplay = new MoreOptionsDisplay({
      onRenameChat: () => this.handleRenameChat(),
      onDeleteChat: () => this.handleDeleteChat()
    });

    // Initialize message component with the chat history manager
    this.messageComponent = new ChatMessages(
      this.chatHistory,
      this.chatHistoryManager,
      AppStateService.getNotebookTools(),
      () => this.handleDisplayScrollDownButton()
    );

    // Create input container with text input and send button
    const inputContainer = document.createElement('div');
    inputContainer.className = 'sage-ai-input-container';
    inputContainer.style.position = 'relative'; // Add relative positioning

    // Create inner chatbox wrapper for the focused styling
    const chatboxWrapper = document.createElement('div');
    chatboxWrapper.className = 'sage-ai-chatbox-wrapper';

    // Create context row (first row)
    const contextRow = document.createElement('div');
    contextRow.className = 'sage-ai-context-row';

    // Create "Add Context" button with @ icon
    const addContextButton = document.createElement('button');

    const atIcon = document.createElement('span');
    atIcon.className = 'sage-ai-at-icon';
    atIcon.innerHTML =
      '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="13" viewBox="0 0 12 13" fill="none">\n' +
      '  <g clip-path="url(#clip0_590_6942)">\n' +
      '    <path d="M8.00001 4.5V7C8.00001 7.39783 8.15804 7.77936 8.43935 8.06066C8.72065 8.34197 9.10218 8.5 9.50001 8.5C9.89783 8.5 10.2794 8.34197 10.5607 8.06066C10.842 7.77936 11 7.39783 11 7V6.5C11 5.37366 10.6197 4.2803 9.92071 3.39709C9.22172 2.51387 8.24499 1.89254 7.14877 1.63376C6.05255 1.37498 4.90107 1.49391 3.88089 1.97128C2.86071 2.44865 2.03159 3.2565 1.52787 4.26394C1.02415 5.27137 0.875344 6.41937 1.10556 7.52194C1.33577 8.62452 1.93151 9.61706 2.79627 10.3388C3.66102 11.0605 4.74413 11.4691 5.87009 11.4983C6.99606 11.5276 8.09893 11.1758 9.00001 10.5M8 6.5C8 7.60457 7.10457 8.5 6 8.5C4.89543 8.5 4 7.60457 4 6.5C4 5.39543 4.89543 4.5 6 4.5C7.10457 4.5 8 5.39543 8 6.5Z" stroke="#949494" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>\n' +
      '  </g>\n' +
      '  <defs>\n' +
      '    <clipPath id="clip0_590_6942">\n' +
      '      <rect width="12" height="12" fill="white" transform="translate(0 0.5)"/>\n' +
      '    </clipPath>\n' +
      '  </defs>\n' +
      '</svg>';

    const contextText = document.createElement('p');
    contextText.className = 'sage-ai-context-text';
    contextText.textContent = 'Add Context';

    addContextButton.className = 'sage-ai-add-context-button';
    addContextButton.appendChild(atIcon);
    addContextButton.appendChild(contextText);
    addContextButton.title = 'Add context';
    addContextButton.type = 'button';

    // Add click handler for the Add Context button
    addContextButton.addEventListener('click', e => {
      e.preventDefault();
      e.stopPropagation();
      // Focus the input and trigger mention dropdown by inserting @
      this.chatInput.focus();
      const currentText = this.chatInput.getPlainText();
      const cursorPosition = this.chatInput.getSelectionStart();
      const newText =
        currentText.slice(0, cursorPosition) +
        '@' +
        currentText.slice(cursorPosition);
      this.chatInput.setPlainText(newText);
      // Set cursor position after the @
      setTimeout(() => {
        this.chatInput.setSelectionRange(
          cursorPosition + 1,
          cursorPosition + 1
        );
        // Trigger input event to activate mention dropdown
        const inputEvent = new Event('input', { bubbles: true });
        this.chatInput.getInputElement().dispatchEvent(inputEvent);
      }, 0);
    });

    // Create context display container
    const contextDisplay = document.createElement('div');
    contextDisplay.className = 'sage-ai-context-display-inline';

    contextRow.appendChild(addContextButton);
    contextRow.appendChild(contextDisplay);

    // Create input row (second row)
    const inputRow = document.createElement('div');
    inputRow.className = 'sage-ai-input-row';

    // Replace input with rich text input
    this.chatInput = new RichTextChatInput(
      'What would you like me to generate or analyze?'
    );

    // Handle keydown events for submission
    this.chatInput.addEventListener('keydown', (event: Event) => {
      const keyEvent = event as KeyboardEvent;
      // Submit on Enter (without shift for newlines)
      if (
        keyEvent.key === 'Enter' &&
        !keyEvent.shiftKey &&
        this.chatInput.getPlainText().trim() !== '' &&
        !this.inputManager.getIsProcessingMessage()
      ) {
        keyEvent.preventDefault(); // Prevent newline
        this.inputManager.sendMessage();
      }
    });

    this.sendButton = document.createElement('button');
    SEND_ICON.render(this.sendButton);
    this.sendButton.className = 'sage-ai-send-button disabled';
    this.sendButton.style.position = 'absolute'; // Set absolute positioning
    this.sendButton.style.bottom = '12px'; // Position at bottom
    this.sendButton.style.right = '12px'; // Position at right
    this.sendButton.addEventListener('click', () => {
      if (this.inputManager.getIsProcessingMessage()) {
        this.cancelMessage();
      } else if (this.chatInput.getPlainText().trim() !== '') {
        this.inputManager.sendMessage();
      }
    });

    // Update send button state based on input content
    const updateSendButtonState = () => {
      const hasContent = this.chatInput.getPlainText().trim() !== '';
      if (this.inputManager.getIsProcessingMessage()) {
        this.sendButton.classList.add('enabled');
        this.sendButton.classList.remove('disabled');
        this.sendButton.disabled = false;
      } else if (hasContent) {
        this.sendButton.classList.add('enabled');
        this.sendButton.classList.remove('disabled');
        this.sendButton.disabled = false;
      } else {
        this.sendButton.classList.remove('enabled');
        this.sendButton.classList.add('disabled');
        this.sendButton.disabled = true;
      }
    };

    // Initial state - disabled since input starts empty
    this.sendButton.disabled = true;

    // Listen for input changes to update button state
    this.chatInput.addEventListener('input', updateSendButtonState);
    this.chatInput.addEventListener('keyup', updateSendButtonState);
    this.chatInput.addEventListener('paste', () => {
      // Use setTimeout to ensure paste content is processed
      setTimeout(updateSendButtonState, 0);
    });

    // Create mode selector
    this.modeSelector = document.createElement('div');
    this.modeSelector.className = 'sage-ai-mode-selector';
    this.modeSelector.title = 'Select chat mode';

    // Create dropdown container
    this.modeSelectorDropdown = document.createElement('div');
    this.modeSelectorDropdown.className = 'sage-ai-mode-dropdown hidden';

    // Create content wrapper for flexbox layout
    const dropdownContent = document.createElement('div');
    dropdownContent.className = 'sage-ai-mode-dropdown-content';

    // Create options
    const agentOption = this.createOption(
      'agent',
      'Agent',
      AGENT_MODE_ICON.svgstr,
      'Prepare datasets. Build models. Test ideas.'
    );
    const askOption = this.createOption(
      'ask',
      'Ask',
      ASK_ICON.svgstr,
      'Ask Sage about your notebook or your data.'
    );
    const handsOnOption = this.createOption(
      'fast',
      'Hands-on',
      HANDS_ON_MODE_ICON.svgstr,
      'Manually decide what gets added to the context.'
    );

    dropdownContent.appendChild(agentOption);
    dropdownContent.appendChild(askOption);
    dropdownContent.appendChild(handsOnOption);
    this.modeSelectorDropdown.appendChild(dropdownContent);

    // Set initial display (Agent selected by default)
    this.updateModeSelectorDisplay('agent');

    // Add click handler to toggle dropdown
    this.modeSelector.addEventListener('click', e => {
      e.stopPropagation();
      if (this.modeSelector.getAttribute('data-is-disabled') === 'true') {
        return;
      }
      this.toggleModeDropdown();
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', () => {
      this.closeModeDropdown();
    });

    // Assemble the input structure
    inputRow.appendChild(this.chatInput.getElement());
    inputRow.appendChild(this.sendButton);
    inputRow.appendChild(this.modeSelector);

    chatboxWrapper.appendChild(contextRow);
    chatboxWrapper.appendChild(inputRow);
    inputContainer.appendChild(chatboxWrapper);
    // Note: modeSelectorDropdown will be appended to body when opened

    const newPromptCTA = document.createElement('div');
    newPromptCTA.className = 'sage-ai-new-prompt-cta';
    const text = document.createElement('p');
    text.textContent = 'Want to start a new prompt?';
    const chatCTA = document.createElement('a');
    chatCTA.textContent = 'Create a New Chat';
    chatCTA.onclick = () => {
      this.createNewChat();
      return false; // Prevent default link behavior
    };
    newPromptCTA.appendChild(text);
    newPromptCTA.appendChild(chatCTA);
    this.hideNewChatCta();

    this.newChatDisplayWidget = new NewChatDisplayWidget(
      {
        onPromptSelected: prompt => {
          this.inputManager.setInputValue(prompt);
          this.inputManager.sendMessage();
          this.showHistoryWidget();
        },
        onRemoveDisplay: () => {
          this.showHistoryWidget();
        }
      },
      RECOMMENDED_PROMPTS
    );

    // Initialize UpdateBanner
    const extensions = AppStateService.getExtensions();
    if (extensions) {
      this.updateBanner = new UpdateBannerWidget(extensions);
      // Show banner on first launch
      this.updateBanner.showBanner();
    }

    // Add components to the layout
    layout.addWidget(new Widget({ node: toolbar }));
    layout.addWidget(this.historyWidget);
    layout.addWidget(this.newChatDisplayWidget);

    document.body.appendChild(
      this.updateBanner?.node || document.createElement('div')
    );

    this.showHistoryWidget();
    this.updateBanner?.checkForUpdates();

    const inputContainerWidget = new Widget({ node: inputContainer });

    // Create wrapper for state displays with fixed positioning and flexbox
    const stateDisplayContainer = document.createElement('div');
    stateDisplayContainer.className = 'sage-ai-state-display-container';
    stateDisplayContainer.style.position = 'fixed';
    stateDisplayContainer.style.bottom = '0';
    stateDisplayContainer.style.left = '0';
    stateDisplayContainer.style.right = '0';
    stateDisplayContainer.style.pointerEvents = 'none'; // Allow clicks to pass through
    stateDisplayContainer.style.zIndex = '1';
    stateDisplayContainer.style.display = 'flex';
    stateDisplayContainer.style.flexDirection = 'column';
    stateDisplayContainer.style.alignItems = 'stretch';

    // Widget nodes will get their styles from CSS classes
    const planStateNode = this.planStateDisplay.getWidget().node;
    const llmStateNode = this.llmStateDisplay.getWidget().node;

    // Create spacer for input container height
    const inputSpacer = document.createElement('div');
    inputSpacer.className = 'sage-ai-input-spacer';
    inputSpacer.style.order = '3'; // Input spacer appears last
    inputSpacer.style.flexShrink = '0';

    // Function to update container positioning based on input container height
    const updateWrapperPositions = () => {
      const inputHeight = inputContainer.offsetHeight;
      const isNewPromptCTAHidden = newPromptCTA.style.display === 'none';
      // 29px is the height of the new prompt CTA when it is visible
      // being 17px of height and 12px of padding
      const newPromptCTAHeight = isNewPromptCTAHidden ? 29 : 0;

      // Update the spacer height to match input container + some spacing
      inputSpacer.style.height = `${inputHeight - newPromptCTAHeight + 16}px`;

      // Use requestAnimationFrame to ensure DOM updates are complete before calculating heights
      requestAnimationFrame(() => {
        setTimeout(() => {
          // Calculate dynamic padding for history container
          let totalStateHeight = 0;

          // Check if LLM state display is hidden
          const isLLMHidden =
            this.llmStateDisplay.node.classList.contains('hidden');

          // Add LLM state height if visible
          if (!isLLMHidden && this.llmStateDisplay.node.offsetHeight > 0) {
            totalStateHeight += this.llmStateDisplay.node.offsetHeight - 10;
          }

          // Add plan state height if visible
          if (
            this.planStateDisplay.getIsVisible() &&
            this.planStateDisplay.node.offsetHeight > 0
          ) {
            totalStateHeight += this.planStateDisplay.node.offsetHeight - 20;
          }

          if (totalStateHeight > 0) {
            totalStateHeight += 10;
          }

          const historyContainer = this.chatHistory.parentElement;
          if (historyContainer) {
            historyContainer.style.paddingBottom = `${totalStateHeight}px`;
          }

          const scrollDownButton = <HTMLButtonElement>(
            historyContainer?.querySelector('.sage-ai-scroll-down-button')
          );
          if (scrollDownButton) {
            const bottom = totalStateHeight ? totalStateHeight - 6 : 0;
            scrollDownButton.style.bottom = `${bottom}px`;
          }

          this.handleDisplayScrollDownButton();
        }, 200); // Additional delay to ensure transitions/animations complete
      });
    };

    // Store the positioning function for later use
    (this as any).updateStateDisplayPositions = updateWrapperPositions;

    // // Connect to state change signals instead of overriding methods
    // this.llmStateConnection = this.llmStateDisplay.stateChanged.connect(() => {
    //   setTimeout(updateWrapperPositions, 100);
    // });

    this.planStateConnection = this.planStateDisplay.stateChanged.connect(
      () => {
        setTimeout(updateWrapperPositions, 100);
      }
    );

    // Initial positioning
    setTimeout(updateWrapperPositions, 100); // Increased timeout to ensure DOM is rendered

    // Update positioning when window resizes or layout changes
    this.resizeObserver = new ResizeObserver(updateWrapperPositions);
    this.resizeObserver.observe(inputContainer);

    // Add MutationObserver to watch for content changes in state displays
    this.mutationObserver = new MutationObserver(() => {
      setTimeout(updateWrapperPositions, 100); // Increased delay to ensure DOM updates complete
    });

    // Observe both state displays for changes (mainly for expanded content size changes)
    this.mutationObserver.observe(this.llmStateDisplay.node, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['class'] // Focus on class changes like 'hidden'
    });

    this.mutationObserver.observe(this.planStateDisplay.node, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['class'] // Focus on class changes and content size changes
    });

    // Add widgets directly to container in order: plan state, LLM state, input spacer
    stateDisplayContainer.appendChild(planStateNode);
    stateDisplayContainer.appendChild(llmStateNode);
    stateDisplayContainer.appendChild(inputSpacer);

    // Add the container to the layout
    layout.addWidget(inputContainerWidget);
    layout.addWidget(new Widget({ node: stateDisplayContainer }));
    layout.addWidget(new Widget({ node: newPromptCTA }));
    layout.addWidget(this.moreOptionsDisplay);

    // Initialize helper classes
    this.threadManager = new ThreadManager(
      this.chatHistoryManager,
      this.messageComponent,
      this.chatService,
      this.threadNameDisplay,
      this.node
    );

    this.inputManager = new ChatInputManager(
      this.chatInput,
      this.chatHistoryManager,
      inputContainer,
      AppStateService.getContentManager(),
      AppStateService.getToolService(),
      context => {
        // Handle context selection - add to ChatMessages
        this.messageComponent.addMentionContext(context);
        this.contextHandler.updateContextDisplay();
        console.log('Context added:', context);
      },
      contextId => {
        // Handle context removal - remove from ChatMessages
        this.messageComponent.removeMentionContext(contextId);
        this.contextHandler.updateContextDisplay();
        console.log(`Context removed: ${contextId}`);
      },
      () => this.createNewChat() // Handle reset chat
    );

    this.uiHelper = new ChatUIHelper(
      this.chatHistory,
      this.messageComponent,
      this.llmStateDisplay
    );

    // Initialize context handler early so it can be used in other components
    this.contextHandler = new ChatboxContext(
      this.messageComponent,
      this.inputManager,
      this.node
    );

    // Initialize the conversation service with the diffManager
    this.conversationService = new ConversationService(
      this.chatService,
      AppStateService.getToolService(),
      AppStateService.getContentManager(),
      this.messageComponent,
      this.chatHistory,
      actionHistory,
      {
        updateLoadingIndicator: (text?: string) =>
          this.updateLoadingIndicator(text),
        removeLoadingIndicator: () => this.removeLoadingIndicator(),
        hideLoadingIndicator: () => this.llmStateDisplay.hide()
      }
    );

    // Set the diff manager in the conversation service if available
    const diffManager = AppStateService.getState().notebookDiffManager;
    if (diffManager) {
      this.conversationService.setDiffManager(diffManager);
    }

    // Set up event handlers
    this.setupEventHandlers();

    // Initialize services
    void this.initializeServices();

    // Subscribe to AppState changes to re-initialize services when Claude settings change
    this.subscribeToAppStateChanges();

    // Set dependencies in input manager for sendMessage and revertAndSend
    this.inputManager.setDependencies({
      chatService: this.chatService,
      conversationService: this.conversationService,
      messageComponent: this.messageComponent,
      uiHelper: this.uiHelper,
      contextHandler: this.contextHandler,
      sendButton: this.sendButton,
      modeSelector: this.modeSelector,
      updateUndoButtonState: () => this.updateUndoButtonState(),
      cancelMessage: () => this.cancelMessage(),
      onMessageSent: () => this.showHistoryWidget()
    });

    // Set up polling to update undo button state
    setInterval(() => this.updateUndoButtonState(), 1000);

    // Initialize managers

    const waitingUserReplyBoxManager =
      AppStateService.getWaitingUserReplyBoxManager();
    waitingUserReplyBoxManager.initialize(this.chatHistory);

    // Set up the continue callback to send "Continue" message
    waitingUserReplyBoxManager.setContinueCallback(() => {
      this.sendContinueMessage();
    });

    // Set up the prompt callback to send custom prompt messages
    waitingUserReplyBoxManager.setPromptCallback((prompt: string) => {
      this.sendPromptMessage(prompt);
    });

    // Initialize context display after everything is set up
    this.contextHandler.updateContextDisplay();

    if (this.messageComponent.getMessageHistory().length === 0)
      this.showNewChatDisplay();
  }

  private handleDisplayScrollDownButton(): void {
    if (this.isScrolledToBottom()) {
      this.hideScrollDownButton();
    } else {
      this.showScrollDownButton();
    }
  }

  private showScrollDownButton(): void {
    this.scrollDownButton.classList.remove('hidden');
  }

  private hideScrollDownButton(): void {
    this.scrollDownButton.classList.add('hidden');
  }

  private handleChatHistoryResize(): void {
    if (this.isScrolledToBottom()) {
      this.scrollChatHistoryToBottom();
    } else {
      this.handleDisplayScrollDownButton();
    }
  }

  public scrollChatHistoryToBottom(): void {
    this.chatHistory.scrollTop = this.chatHistory.scrollHeight;
  }

  private updateScrollAttribute(): boolean {
    const scrollTop = this.chatHistory.scrollTop;
    const scrollHeight = this.chatHistory.scrollHeight;
    const isScrolledToBottom =
      Math.ceil(scrollTop + this.chatHistory.clientHeight) >= scrollHeight;

    this.chatHistory.setAttribute(
      'data-is-scrolled-to-bottom',
      isScrolledToBottom.toString()
    );

    return isScrolledToBottom;
  }

  private isScrolledToBottom(): boolean {
    return (
      this.chatHistory.getAttribute('data-is-scrolled-to-bottom') === 'true'
    );
  }

  /**
   * Create a custom option element for the mode selector dropdown
   * @param value The value of the option
   * @param text The display text
   * @param iconSvg The SVG icon string
   * @returns The HTML div element representing the option
   */
  private createOption(
    value: string,
    text: string,
    iconSvg: string,
    description: string
  ): HTMLDivElement {
    const option = document.createElement('div');
    option.className = 'sage-ai-mode-option';
    option.setAttribute('data-value', value);

    const iconContainer = document.createElement('div');
    iconContainer.className = 'sage-ai-mode-option-icon';
    iconContainer.innerHTML = iconSvg;

    const textElement = document.createElement('div');
    textElement.innerHTML = `
      <p class="sage-ai-mode-option-title">
      ${text}
       </p>
       <p class="sage-ai-mode-option-description">
      ${description}
       </p>
    `;
    textElement.className = 'sage-ai-mode-option-text';

    option.appendChild(iconContainer);
    option.appendChild(textElement);

    // Store reference for easy access
    this.modeSelectorOptions.set(value, option);

    // Add click handler
    option.addEventListener('click', e => {
      e.stopPropagation();
      this.selectMode(value);
    });

    return option;
  }

  /**
   * Update the mode selector display to show the selected mode
   * @param mode The selected mode ('agent' or 'ask')
   */
  private updateModeSelectorDisplay(mode: string): void {
    const selectedOption = this.modeSelectorOptions.get(mode);
    if (selectedOption) {
      // Clear current display
      this.modeSelector.innerHTML = '';

      // Create a display option without description
      const displayOption = document.createElement('div');
      displayOption.className = 'sage-ai-mode-display';

      const iconContainer = document.createElement('div');
      iconContainer.className = 'sage-ai-mode-option-icon';
      iconContainer.innerHTML = AGENT_MODE_SHINY_ICON.svgstr;
      displayOption.appendChild(iconContainer);

      // Create text element with only the title (no description)
      const originalText = selectedOption.querySelector(
        '.sage-ai-mode-option-text'
      );
      if (originalText) {
        const titleElement = originalText.querySelector(
          '.sage-ai-mode-option-title'
        );
        if (titleElement) {
          const textElement = document.createElement('div');
          textElement.className = 'sage-ai-mode-option-text';
          textElement.innerHTML = titleElement.innerHTML;
          displayOption.appendChild(textElement);
        }
      }

      // Add dropdown arrow
      const arrow = document.createElement('div');
      arrow.className = 'sage-ai-mode-selector-arrow';
      OPEN_MODE_SELECTOR_ICON.render(arrow);

      this.modeSelector.appendChild(displayOption);
      this.modeSelector.appendChild(arrow);
    }
  }

  /**
   * Toggle the visibility of the mode dropdown
   */
  private toggleModeDropdown(): void {
    if (this.modeSelectorDropdown.classList.contains('hidden')) {
      this.openModeDropdown();
    } else {
      this.closeModeDropdown();
    }
  }

  /**
   * Open the mode dropdown
   */
  private openModeDropdown(): void {
    // Add opening class to mode selector
    this.modeSelector.classList.add('open');

    // Position the dropdown above the selector
    const rect = this.modeSelector.getBoundingClientRect();
    this.modeSelectorDropdown.style.position = 'absolute';
    this.modeSelectorDropdown.style.bottom = `${window.innerHeight - rect.top + 8}px`;
    this.modeSelectorDropdown.style.left = `${rect.left}px`;
    this.modeSelectorDropdown.style.minWidth = `${rect.width}px`;

    // Append to body to ensure it appears above other elements
    document.body.appendChild(this.modeSelectorDropdown);

    // Remove hidden class and add visible class with slight delay for animation
    this.modeSelectorDropdown.classList.remove('hidden');
    this.modeSelectorDropdown.classList.add('opening');

    // Use requestAnimationFrame to ensure the element is rendered before adding visible class
    requestAnimationFrame(() => {
      this.modeSelectorDropdown.classList.add('visible');
    });

    // Clean up animation class after animation completes
    setTimeout(() => {
      this.modeSelectorDropdown.classList.remove('opening');
    }, 300);
  }

  /**
   * Close the mode dropdown
   */
  private closeModeDropdown(): void {
    // Remove open class from mode selector
    this.modeSelector.classList.remove('open');

    // Add closing animation
    this.modeSelectorDropdown.classList.add('closing');
    this.modeSelectorDropdown.classList.remove('visible');

    // Remove from DOM after animation completes
    setTimeout(() => {
      this.modeSelectorDropdown.classList.add('hidden');
      this.modeSelectorDropdown.classList.remove('closing');

      // Remove from body if it was appended there
      if (this.modeSelectorDropdown.parentNode === document.body) {
        document.body.removeChild(this.modeSelectorDropdown);
      }
    }, 200);
  }

  /**
   * Select a mode and update the UI
   * @param mode The mode to select ('agent' or 'ask')
   */
  private selectMode(mode: string): void {
    this.modeName = mode as 'agent' | 'ask' | 'fast';
    this.inputManager.setModeName(this.modeName);

    // Handle fast mode when "fast" (Hands-on) mode is selected
    if (this.chatService instanceof AnthropicService) {
      const isFastMode = mode === 'fast';
      // Display appropriate system message
      if (isFastMode) {
        const toolBlacklist = (
          this.chatService as AnthropicService
        ).getToolBlacklist();
        this.messageComponent.addSystemMessage(
          `Hands-on mode enabled. Using optimized prompt and limiting certain tools: ${toolBlacklist.join(', ')}`
        );
      }
    }

    this.updateModeSelectorDisplay(mode);
    this.closeModeDropdown();

    const displayName =
      mode === 'agent' ? 'Agent' : mode === 'ask' ? 'Ask' : 'Hands-on';
    this.messageComponent.addSystemMessage(`Mode switched to: ${displayName}`);
  }

  public updateNotebookId(newId: string): void {
    AppStateService.setCurrentNotebookId(newId);
    this.threadManager.updateNotebookId(newId);
    this.conversationService.updateNotebookId(newId);
  }

  // Backward compatibility method
  public updateNotebookPath(newPath: string): void {
    this.updateNotebookId(newPath);
  }

  /**
   * Setup event handlers
   */
  private setupEventHandlers(): void {
    // Add click event to open left side banner
    this.threadSelectorButton.addEventListener('click', () => {
      this.threadManager.openBanner();
    });

    // Add event listener to autorun checkbox to update the conversation service
    this.autorunCheckbox.addEventListener('change', () => {
      this.conversationService.setAutoRun(this.autorunCheckbox.checked);

      // Display a system message to confirm the change
      if (this.autorunCheckbox.checked) {
        this.messageComponent.addSystemMessage(
          'Auto-run mode enabled. Code will execute automatically without confirmation.'
        );
      } else {
        this.messageComponent.addSystemMessage(
          'Auto-run mode disabled. You will be prompted for code execution.'
        );
      }
    });
  }

  /**
   * Initialize all services
   */
  private async initializeServices(): Promise<void> {
    try {
      // Get configuration from server
      AppStateService.setConfig(await ConfigService.getConfig());

      // Initialize chat service with config from server
      const initialized = await this.chatService.initialize();
      console.log('Chat service initialized:', initialized);

      if (initialized) {
        const modelName = this.chatService.getModelName();
        // this.messageComponent.addSystemMessage(
        //   `✅ Configuration loaded successfully. Using model: ${modelName}`
        // );
      } else {
        // this.messageComponent.addSystemMessage(
        //   '⚠️ Failed to initialize with API key from config. Please check the server.'
        // );
      }

      // Initialize tool service
      const toolService = AppStateService.getToolService();
      await toolService.initialize();
      console.log('Connected to MCP server successfully.');
      console.log(
        `Loaded ${toolService.getTools().length} tools from MCP server.`
      );

      // Initialize plan generation service
      const { PlanGenerationService } = await import(
        '../Services/PlanGenerationService'
      );
      await PlanGenerationService.initialize();
      console.log('Plan generation service initialized.');
    } catch (error) {
      console.error('Failed to connect to MCP server:', error);
      this.messageComponent.addSystemMessage(
        '❌ Failed to connect to MCP server. Some features may not work.'
      );
    }
  }

  /**
   * Update the notebook ID and load its chat history
   * @param notebookId ID of the notebook
   */
  public async setNotebookId(notebookId: string | undefined): Promise<void> {
    if (!notebookId) {
      AppStateService.setCurrentNotebookId(null);
      this.threadManager.setNotebookId(null);
      return;
    }

    if (this.lastNotebookId === notebookId) return;

    this.lastNotebookId = notebookId;

    AppStateService.setCurrentNotebookId(notebookId);

    // Update the thread manager with the current notebook ID
    this.threadManager.setNotebookId(notebookId);

    // Show appropriate widget based on whether there are messages
    await this.showNewChatDisplayOrHistory();

    // Update conversation service with the current notebook ID
    this.conversationService.setNotebookId(notebookId);

    await this.restoreLastThreadForNotebook(notebookId);

    // Refresh user message history when switching notebooks
    this.inputManager.loadUserMessageHistory();

    // Update context cells indicator when switching notebooks
    const contextManager = AppStateService.getState().notebookContextManager;
    if (contextManager) {
      const contextCells = contextManager.getContextCells(notebookId);
      this.contextHandler.updateContextCellsIndicator(contextCells.length);
    }
  }

  /**
   * Try to restore the last selected thread for a notebook
   * @param notebookId ID of the notebook
   */
  private async restoreLastThreadForNotebook(
    notebookId: string
  ): Promise<void> {
    try {
      // Get the last valid thread for this notebook
      const lastThread =
        await this.threadManager.getLastValidThreadForNotebook(notebookId);

      if (lastThread && lastThread.messages.length > 0) {
        // Found a valid last thread, load it
        console.log(
          `[ChatBoxWidget] Restoring last thread: ${lastThread.name} for notebook ${notebookId}`
        );

        await this.showHistoryWidgetFromThread(lastThread);
        return;
      } else {
        // No valid last thread found, show new chat or history based on available content
        console.log(
          `[ChatBoxWidget] No valid last thread found for notebook ${notebookId}, showing default view`
        );
        await this.createNewChat();
        this.showNewChatDisplay();
        return;
      }
    } catch (error) {
      console.warn(
        `[ChatBoxWidget] Failed to restore last thread for notebook ${notebookId}:`,
        error
      );
      // Fallback to default behavior
      await this.showNewChatDisplayOrHistory();
    }
  }

  /**
   * Create a new chat thread
   */
  private async createNewChat(): Promise<void> {
    // Hide the waiting reply box when user cancels
    AppStateService.getWaitingUserReplyBoxManager().hide();

    // Only proceed if we have an active notebook
    const currentNotebookId = AppStateService.getCurrentNotebookId();
    if (!currentNotebookId) {
      this.messageComponent.addSystemMessage('Please open a notebook first.');
      return;
    }

    // Cancel any ongoing request - make sure to update the UI state as well
    if (this.inputManager.getIsProcessingMessage()) {
      this.cancelMessage();
    } else {
      // Even if not visibly processing, cancel any pending requests
      this.chatService.cancelRequest();
    }

    // Create a new thread
    const newThread = await this.threadManager.createNewThread();

    if (newThread) {
      // Clear action history
      this.conversationService.clearActionHistory();
      this.updateUndoButtonState();
      this.contextHandler.updateContextDisplay();

      // Switch to new chat display since there are no messages
      this.showNewChatDisplay();
      this.llmStateDisplay.hide();

      // Also hide DiffNavigationWidget when creating new chat
      const diffNavigationWidget =
        AppStateService.getDiffNavigationWidgetSafe();
      if (diffNavigationWidget) {
        diffNavigationWidget.hidePendingDiffs();
      }
    }
  }

  /**
   * Update the state of the undo button based on available actions
   */
  private updateUndoButtonState(): void {
    if (this.conversationService.canUndo()) {
      const actionDesc = this.conversationService.getLastActionDescription();
      this.undoButton.disabled = false;
      this.undoButton.title = `Undo: ${actionDesc}`;
    } else {
      this.undoButton.disabled = true;
      this.undoButton.title = 'No action to undo';
    }
  }

  /**
   * Undo the last action
   */
  private async undoLastAction(): Promise<void> {
    if (!this.conversationService.canUndo()) {
      return;
    }

    // Disable the button during undo
    this.undoButton.disabled = true;
    this.undoButton.title = 'Undoing...';

    try {
      // Perform the undo operation
      await this.conversationService.undoLastAction();
    } catch (error) {
      console.error('Error during undo:', error);
      this.messageComponent.addErrorMessage(
        `Error during undo: ${error instanceof Error ? error.message : 'Unknown error'}`
      );
    } finally {
      // Update the button state after undo completes
      this.updateUndoButtonState();
    }
  }

  /**
   * Cancel the current message processing
   */
  public cancelMessage(): void {
    if (!this.inputManager.getIsProcessingMessage()) {
      return;
    }

    console.log('Cancelling message...');
    console.log(this.inputManager.getIsProcessingMessage());

    // Cancel the request in the chatService
    this.chatService.cancelRequest();

    // Update state immediately to prevent any further processing
    this.inputManager.setIsProcessingMessage(false);

    // Remove loading indicator
    this.uiHelper.removeLoadingIndicator();

    // this.messageComponent.addSystemMessage('Request cancelled by user.');
    this.messageComponent.removeLoadingText();
    this.uiHelper.updateSendButton(this.sendButton, false);
    this.sendButton.classList.add('disabled');
    this.sendButton.classList.remove('enabled');
    this.sendButton.disabled = true;
    AppStateService.getPlanStateDisplay().setLoading(false);
    this.uiHelper.updateAgentModeElement(this.modeSelector, false);

    const modeIcon = document.createElement('div');
    AGENT_MODE_SHINY_ICON.render(modeIcon);

    // Check if there are pending diffs and show approval dialog if needed
    const diffManager = AppStateService.getState().notebookDiffManager;
    if (
      diffManager &&
      diffManager.hasPendingDiffs() &&
      !diffManager.isDialogOpen()
    ) {
      // Show pending diffs in LLMStateDisplay
      if (this.llmStateDisplay) {
        const currentNotebookId = AppStateService.getCurrentNotebookId();
        this.llmStateDisplay.showPendingDiffs(currentNotebookId);

        // Also show diffs in DiffNavigationWidget for synchronized display
        const diffNavigationWidget =
          AppStateService.getDiffNavigationWidgetSafe();
        if (diffNavigationWidget) {
          diffNavigationWidget.showPendingDiffs(currentNotebookId);
        }
      }

      // Use setTimeout to ensure UI updates before showing the dialog
      setTimeout(async () => {
        const currentNotebookId = AppStateService.getCurrentNotebookId();
        await diffManager?.showCancellationApprovalDialog(
          this.chatHistory,
          currentNotebookId // Pass the notebook ID
        );
      }, 100);
    } else {
      this.llmStateDisplay.show();
      this.llmStateDisplay.hide();
    }
  }

  protected onAfterShow(): void {
    this.inputManager.focus();
  }

  /**
   * Update the loading indicator - exposed for the conversation service to use
   */
  public updateLoadingIndicator(text: string = 'Generating...'): void {
    this.uiHelper.updateLoadingIndicator(text);
  }

  /**
   * Remove the loading indicator - exposed for the conversation service to use
   */
  public removeLoadingIndicator(): void {
    this.uiHelper.removeLoadingIndicator();
  }

  /**
   * Handle a cell being added to context
   * @param notebookPath Path of the notebook containing the cell
   * @param cellId ID of the cell added to context
   */
  public onCellAddedToContext(notebookPath: string): void {
    this.contextHandler.onCellAddedToContext(notebookPath);
  }

  /**
   * Handle a cell being removed from context
   * @param notebookPath Path of the notebook containing the cell
   * @param cellId ID of the cell removed from context
   */
  public onCellRemovedFromContext(notebookPath: string): void {
    this.contextHandler.onCellRemovedFromContext(notebookPath);
  }

  /**
   * Show new chat display or history based on current thread state
   */
  public async showNewChatDisplayOrHistory(): Promise<void> {
    const currentThread = this.chatHistoryManager.getCurrentThread();
    const hasMessages = currentThread && currentThread.messages.length > 0;

    if (hasMessages) {
      await this.showHistoryWidgetFromThread(currentThread);
    } else {
      this.showNewChatDisplay();
    }
  }

  public showNewChatCta(): void {
    const newPromptCTA = <HTMLDivElement>(
      this.node.querySelector('.sage-ai-new-prompt-cta')
    );
    if (newPromptCTA) {
      newPromptCTA.style.display = 'flex';
    }
  }

  public hideNewChatCta(): void {
    const newPromptCTA = <HTMLDivElement>(
      this.node.querySelector('.sage-ai-new-prompt-cta')
    );
    if (newPromptCTA) {
      newPromptCTA.style.display = 'none';
    }
  }

  /**
   * Show the new chat display widget
   */
  public showNewChatDisplay(): void {
    if (this.messageComponent.getMessageHistory().length > 0) return;
    if (this.newChatDisplayWidget) {
      this.newChatDisplayWidget.node.style.display = 'flex';
    }
    if (this.historyWidget) {
      this.historyWidget.node.style.display = 'none';
    }

    this.hideNewChatCta();
  }

  /**
   * Show the history widget
   */
  public showHistoryWidget(): void {
    if (this.newChatDisplayWidget) {
      this.newChatDisplayWidget.node.style.display = 'none';
    }
    if (this.historyWidget) {
      this.historyWidget.node.style.display = 'block';
    }
    this.showNewChatCta();
  }

  public async showHistoryWidgetFromThread(thread: IChatThread): Promise<void> {
    await this.threadManager.selectThread(thread.id);
    this.showHistoryWidget();
  }

  /**
   * Show the more options popover
   */
  private showMoreOptions(): void {
    const moreOptionsButton = this.node.querySelector(
      '.sage-ai-more-options-button'
    ) as HTMLButtonElement;
    if (moreOptionsButton && this.moreOptionsDisplay) {
      this.moreOptionsDisplay.showPopover(moreOptionsButton);
    }
  }

  /**
   * Handle rename chat action
   */
  private async handleRenameChat(): Promise<void> {
    const currentThread = this.chatHistoryManager.getCurrentThread();
    if (!currentThread) {
      this.messageComponent.addSystemMessage('No active chat to rename.');
      return;
    }

    const newName = prompt('Enter new chat name:', currentThread.name);
    if (newName && newName.trim() !== '' && newName !== currentThread.name) {
      const success = this.chatHistoryManager.renameCurrentThread(
        newName.trim()
      );
      if (success) {
        this.threadNameDisplay.textContent = newName.trim();
        this.messageComponent.addSystemMessage(
          `Chat renamed to: ${newName.trim()}`
        );
      } else {
        this.messageComponent.addSystemMessage('Failed to rename chat.');
      }
    }
  }

  /**
   * Handle delete chat action
   */
  private async handleDeleteChat(): Promise<void> {
    const currentThread = this.chatHistoryManager.getCurrentThread();
    if (!currentThread) {
      this.messageComponent.addSystemMessage('No active chat to delete.');
      return;
    }

    const confirmDelete = confirm(
      `Are you sure you want to delete the chat "${currentThread.name}"? This action cannot be undone.`
    );
    if (confirmDelete) {
      const deletedThreadName = currentThread.name;
      const success = this.chatHistoryManager.deleteThread(currentThread.id);
      if (success) {
        this.messageComponent.addSystemMessage(
          `Chat "${deletedThreadName}" has been deleted.`
        );

        // Update thread name display for the new current thread
        const newCurrentThread = this.chatHistoryManager.getCurrentThread();
        if (newCurrentThread) {
          this.threadNameDisplay.textContent = newCurrentThread.name;
          await this.messageComponent.loadFromThread(newCurrentThread);
          if (newCurrentThread.messages.length > 0) {
            this.showHistoryWidget();
          } else {
            this.showNewChatDisplay();
          }
        } else {
          this.showNewChatDisplay();
        }
      } else {
        this.messageComponent.addSystemMessage('Failed to delete chat.');
      }
    }
  }

  /**
   * Subscribe to AppState changes to re-initialize services when Claude settings change
   */
  private subscribeToAppStateChanges(): void {
    // Store initial Claude settings to compare against
    const initialClaudeSettings = AppStateService.getClaudeSettings();
    this.lastClaudeSettings = {
      claudeApiKey: initialClaudeSettings.claudeApiKey,
      claudeModelId: initialClaudeSettings.claudeModelId,
      claudeModelUrl: initialClaudeSettings.claudeModelUrl
    };

    this.appStateSubscription = AppStateService.changes.subscribe(state => {
      // Check if Claude settings have changed
      const currentClaudeSettings = {
        claudeApiKey: state.settings.claudeApiKey,
        claudeModelId: state.settings.claudeModelId,
        claudeModelUrl: state.settings.claudeModelUrl
      };

      const hasChanged =
        !this.lastClaudeSettings ||
        this.lastClaudeSettings.claudeApiKey !==
          currentClaudeSettings.claudeApiKey ||
        this.lastClaudeSettings.claudeModelId !==
          currentClaudeSettings.claudeModelId ||
        this.lastClaudeSettings.claudeModelUrl !==
          currentClaudeSettings.claudeModelUrl;

      if (hasChanged) {
        console.log(
          'Claude settings changed, re-initializing chat service...',
          {
            previous: this.lastClaudeSettings,
            current: currentClaudeSettings
          }
        );

        this.lastClaudeSettings = currentClaudeSettings;
        this.reinitializeChatService();
      }
    });
  }

  /**
   * Re-initialize the chat service with updated settings
   */
  private async reinitializeChatService(): Promise<void> {
    try {
      console.log(
        'Re-initializing chat service with updated Claude settings...'
      );

      // Re-initialize the chat service (it will automatically pick up new settings from AppState)
      const initialized = await this.chatService.initialize();
      console.log('Chat service re-initialized:', initialized);

      if (initialized) {
        const modelName = this.chatService.getModelName();
        // this.messageComponent.addSystemMessage(
        //   `✅ Settings updated successfully. Using model: ${modelName}`
        // );
      } else {
        this.messageComponent.addSystemMessage(
          '⚠️ Failed to re-initialize with updated settings. Please check your API key.'
        );
      }
    } catch (error) {
      console.error('Failed to re-initialize chat service:', error);
      this.messageComponent.addSystemMessage(
        '⚠️ Error updating settings. Please try again.'
      );
    }
  }

  /**
   * Send a "Continue" message when the continue button is pressed
   */
  public sendContinueMessage(): void {
    // Set the input value to "Continue"
    this.inputManager.setInputValue('Continue');

    // Send the message
    this.inputManager.sendMessage();

    // Hide the waiting reply box since user has responded
    this.messageComponent.hideWaitingReplyBox();
  }

  public sendPromptMessage(prompt: string): void {
    // Set the input value to the selected prompt
    this.inputManager.setInputValue(prompt);

    // Send the message
    this.inputManager.sendMessage();

    // Hide the waiting reply box since user has responded
    this.messageComponent.hideWaitingReplyBox();
  }

  /**
   * Gets the message component for external access
   */
  public getMessageComponent(): ChatMessages {
    return this.messageComponent;
  }

  public dispose(): void {
    this.resizeObserver?.disconnect();
    this.mutationObserver?.disconnect();
    this.llmStateConnection?.dispose();
    this.planStateConnection?.dispose();
    this.moreOptionsDisplay?.dispose();
    this.updateBanner?.dispose();
    this.appStateSubscription?.unsubscribe();
    super.dispose();
  }
}
