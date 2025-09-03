import { AppStateService } from '../AppState';
import { CheckpointManager } from '../Services/CheckpointManager';
import { ICheckpoint, CheckpointRestorationOption } from '../types';

/**
 * Modal dialog for checkpoint restoration
 */
export class CheckpointRestorationModal {
  private modalElement: HTMLElement | null = null;
  private onRestoreCallback:
    | ((option: CheckpointRestorationOption) => void)
    | null = null;
  private onCancelCallback: (() => void) | null = null;

  /**
   * Show the restoration modal
   */
  public show(
    checkpoint: ICheckpoint,
    onRestore: (option: CheckpointRestorationOption) => void,
    onCancel: () => void
  ): void {
    this.onRestoreCallback = onRestore;
    this.onCancelCallback = onCancel;

    this.createModal(checkpoint);
    this.attachEventListeners();

    // Show modal
    document.body.appendChild(this.modalElement!);
    this.modalElement!.classList.add('visible');

    console.log(
      '[CheckpointRestorationModal] Modal shown for checkpoint:',
      checkpoint.id
    );
  }

  /**
   * Hide the modal
   */
  public hide(): void {
    if (this.modalElement) {
      this.modalElement.classList.remove('visible');
      setTimeout(() => {
        if (this.modalElement && this.modalElement.parentNode) {
          this.modalElement.parentNode.removeChild(this.modalElement);
        }
        this.modalElement = null;
      }, 200); // Wait for animation
    }
  }

  /**
   * Create the modal HTML structure
   */
  private createModal(checkpoint: ICheckpoint): void {
    this.modalElement = document.createElement('div');
    this.modalElement.className = 'sage-ai-checkpoint-modal';

    // Add CSS styles
    this.addStyles();

    console.log(
      '[CheckpointRestorationModal] Undoing all actions from checkpoint chain'
    );

    // Find the previous checkpoint by id
    const allNotebookCheckpoints =
      CheckpointManager.getInstance().getCheckpoints();

    // Helper to recursively collect all checkpoints from oldest to newest
    const collectCheckpoints = (
      cp: ICheckpoint,
      allCheckpoints: ICheckpoint[] = []
    ): ICheckpoint[] => {
      if (cp.nextCheckpointId) {
        const next = allNotebookCheckpoints.find(
          c => c.id === cp.nextCheckpointId
        );
        if (next) {
          collectCheckpoints(next, allCheckpoints);
        }
      }
      allCheckpoints.push(cp);
      return allCheckpoints;
    };

    // Collect all checkpoints from oldest to the current one (inclusive)
    const checkpointsToUndo = collectCheckpoints(checkpoint, []);

    // Collect all actions in order (oldest checkpoint first)
    const allActions: any[] = [];
    for (const cp of checkpointsToUndo) {
      if (cp.actionHistory && cp.actionHistory.length > 0) {
        allActions.push(...cp.actionHistory);
      }
    }

    console.log(
      '[CheckpointRestorationModal] Total actions to undo from all checkpoints:',
      allActions.length
    );

    if (allActions.length === 0) {
      this.modalElement.innerHTML = `
      <div class="sage-ai-checkpoint-modal-overlay"></div>
      <div class="sage-ai-checkpoint-modal-content">
        <div class="sage-ai-checkpoint-modal-header">
          <h3>Submit from a previous message?</h3>
          <button class="sage-ai-checkpoint-modal-close" type="button">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 4L4 12M4 4L12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>
        
        <div class="sage-ai-checkpoint-modal-body">
          <p>Submitting from a previous message will clear the next messages.</p>
          <p>You can't revert this change.</p>
        </div>

        <div class="sage-ai-checkpoint-modal-footer">
          <button class="sage-ai-checkpoint-btn sage-ai-checkpoint-btn-cancel" type="button">
            Cancel
          </button>
          <button class="sage-ai-checkpoint-btn sage-ai-checkpoint-btn-continue-run" type="button" data-option="continue_and_run_all_cells">
            Continue
          </button>
        </div>
      </div>
    `;
      return;
    }

    this.modalElement.innerHTML = `
      <div class="sage-ai-checkpoint-modal-overlay"></div>
      <div class="sage-ai-checkpoint-modal-content">
        <div class="sage-ai-checkpoint-modal-header">
          <h3>Submit from a previous message?</h3>
          <button class="sage-ai-checkpoint-modal-close" type="button">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 4L4 12M4 4L12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>
        
        <div class="sage-ai-checkpoint-modal-body">
          <p>Submitting from a previous message will revert all actions after this message and clear the messages.</p>
          <p>Run all cells to keep the kernel state consistent.</p>
          <p>You can't revert this change.</p>
        </div>
        
        <div class="sage-ai-checkpoint-modal-footer">
          <button class="sage-ai-checkpoint-btn sage-ai-checkpoint-btn-cancel" type="button">
            Cancel
          </button>
          <button class="sage-ai-checkpoint-btn sage-ai-checkpoint-btn-continue" type="button" data-option="continue_without_running">
            Revert without Running
          </button>
          <button class="sage-ai-checkpoint-btn sage-ai-checkpoint-btn-continue-run" type="button" data-option="continue_and_run_all_cells">
            Revert and Run All Cells
          </button>
        </div>
      </div>
    `;
  }

  /**
   * Add CSS styles for the modal
   */
  private addStyles(): void {
    if (document.getElementById('sage-ai-checkpoint-modal-styles')) {
      return; // Styles already added
    }

    const style = document.createElement('style');
    style.id = 'sage-ai-checkpoint-modal-styles';
    style.textContent = `
      .sage-ai-checkpoint-modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0;
        visibility: hidden;
        transition: opacity 0.2s ease, visibility 0.2s ease;
      }

      .sage-ai-checkpoint-modal.visible {
        opacity: 1;
        visibility: visible;
      }

      .sage-ai-checkpoint-modal-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(2px);
      }

      .sage-ai-checkpoint-modal-content {
        position: relative;
        background: var(--jp-layout-color1);
        border-radius: 8px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        max-width: 500px;
        width: 90%;
        max-height: 80vh;
        overflow: hidden;
        transform: scale(0.95);
        transition: transform 0.2s ease;
      }

      .sage-ai-checkpoint-modal.visible .sage-ai-checkpoint-modal-content {
        transform: scale(1);
      }

      .sage-ai-checkpoint-modal-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px 20px 12px;
      }

      .sage-ai-checkpoint-modal-header h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
        color: var(--jp-ui-font-color1);
      }

      .sage-ai-checkpoint-modal-close {
        background: none;
        border: none;
        padding: 4px;
        cursor: pointer;
        color: var(--jp-ui-font-color2);
        border-radius: 4px;
        transition: background-color 0.2s ease;
      }

      .sage-ai-checkpoint-modal-close:hover {
        background-color: var(--jp-layout-color2);
      }

      .sage-ai-checkpoint-modal-body {
        padding: 0 20px;
      }

      .sage-ai-checkpoint-modal-body p {
        margin: 0;
        color: var(--jp-ui-font-color2);
        line-height: 1.5;
      }

      .sage-ai-checkpoint-preview {
        background: var(--jp-layout-color2);
        border: 1px solid var(--jp-border-color2);
        border-radius: 6px;
        padding: 12px;
      }

      .sage-ai-checkpoint-preview-label {
        font-size: 12px;
        font-weight: 600;
        color: var(--jp-ui-font-color2);
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }

      .sage-ai-checkpoint-preview-content {
        color: var(--jp-ui-font-color1);
        font-size: 14px;
        line-height: 1.4;
        word-break: break-word;
      }

      .sage-ai-checkpoint-modal-footer {
        display: flex;
        gap: 12px;
        padding: 12px 20px 16px;
        justify-content: flex-end;
      }

      .sage-ai-checkpoint-btn {
        padding: 8px 16px;
        border: 1px solid var(--jp-border-color1);
        border-radius: 4px;
        font-size: 12px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
        background: var(--jp-layout-color1);
        color: var(--jp-ui-font-color1);
      }

      .sage-ai-checkpoint-btn:hover {
        background: var(--jp-layout-color2);
      }

      .sage-ai-checkpoint-btn-cancel {
        margin-right: 0;
        border: 0;
      }

      .sage-ai-checkpoint-btn-continue {
      }

      .sage-ai-checkpoint-btn-continue:hover {
      }

      .sage-ai-checkpoint-btn-continue-run {
        background: var(--jp-brand-color1);
        color: var(--jp-ui-inverse-font-color1);
        border-color: var(--jp-brand-color1);
      }

      .sage-ai-checkpoint-btn-continue-run:hover {
        background: var(--jp-brand-color2);
        border-color: var(--jp-brand-color2);
      }
    `;

    document.head.appendChild(style);
  }

  /**
   * Attach event listeners to the modal
   */
  private attachEventListeners(): void {
    if (!this.modalElement) return;

    // Close button
    const closeBtn = this.modalElement.querySelector(
      '.sage-ai-checkpoint-modal-close'
    );
    closeBtn?.addEventListener('click', () => {
      this.handleCancel();
    });

    // Overlay click
    const overlay = this.modalElement.querySelector(
      '.sage-ai-checkpoint-modal-overlay'
    );
    overlay?.addEventListener('click', () => {
      this.handleCancel();
    });

    // Cancel button
    const cancelBtn = this.modalElement.querySelector(
      '.sage-ai-checkpoint-btn-cancel'
    );
    cancelBtn?.addEventListener('click', () => {
      this.handleCancel();
    });

    // Continue buttons
    const continueBtns = this.modalElement.querySelectorAll(
      '.sage-ai-checkpoint-btn-continue, .sage-ai-checkpoint-btn-continue-run'
    );
    continueBtns.forEach(btn => {
      btn.addEventListener('click', e => {
        const target = e.target as HTMLElement;
        const option = target.getAttribute(
          'data-option'
        ) as CheckpointRestorationOption;
        this.handleRestore(option);
      });
    });

    // Escape key
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        this.handleCancel();
      }
    };
    document.addEventListener('keydown', handleKeyDown);

    // Store the handler so we can remove it later
    (this.modalElement as any)._keyDownHandler = handleKeyDown;
  }

  /**
   * Handle cancel action
   */
  private handleCancel(): void {
    this.hide();
    if (this.onCancelCallback) {
      this.onCancelCallback();
    }
  }

  /**
   * Handle restore action
   */
  private handleRestore(option: CheckpointRestorationOption): void {
    this.hide();
    if (this.onRestoreCallback) {
      this.onRestoreCallback(option);
    }
  }

  /**
   * Escape HTML to prevent XSS
   */
  private escapeHtml(text: string): string {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
}
