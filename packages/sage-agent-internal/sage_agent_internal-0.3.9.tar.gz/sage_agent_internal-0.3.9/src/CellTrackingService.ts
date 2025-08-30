import { ICellTrackingMetadata } from './types';
import { NotebookTools } from './Notebook/NotebookTools';
import { INotebookTracker } from '@jupyterlab/notebook';
import { Cell } from '@jupyterlab/cells';

/**
 * Service for tracking cells across notebook reloads
 */
export class CellTrackingService {
  private notebookTools: NotebookTools;
  private notebookTracker: INotebookTracker;

  constructor(notebookTools: NotebookTools, notebookTracker: INotebookTracker) {
    this.notebookTools = notebookTools;
    this.notebookTracker = notebookTracker;

    // Initialize tracking for existing cells when the service starts
    this.initializeExistingCells();

    // Set up change listener on the notebook tracker
    this.notebookTracker.currentChanged.connect(() => {
      this.initializeExistingCells();
    });
  }

  /**
   * Initialize tracking metadata for all existing cells that don't have it
   */
  public initializeExistingCells(): void {
    const notebook = this.notebookTracker.currentWidget?.content;
    if (!notebook) return;

    const cells = notebook.widgets;

    for (let i = 0; i < cells.length; i++) {
      const cell = cells[i];
      this.ensureCellHasTrackingMetadata(cell, 'user');
    }
  }

  /**
   * Helper to get the next available cell number for cell IDs
   */
  private getNextCellNumber(): number {
    const notebook = this.notebookTracker.currentWidget?.content;
    if (!notebook) return 1;
    const cells = notebook.widgets;
    let maxNum = 0;
    for (let i = 0; i < cells.length; i++) {
      const metadata: any = cells[i].model.sharedModel.getMetadata() || {};
      const trackingId = metadata.cell_tracker?.trackingId;
      if (trackingId && /^cell_(\d+)$/.test(trackingId)) {
        const num = parseInt(trackingId.split('_')[1], 10);
        if (num > maxNum) maxNum = num;
      }
    }
    return maxNum + 1;
  }

  /**
   * Ensure a cell has tracking metadata, add it if not present
   * @param cell The cell to check/update
   * @param origin The origin of the cell if metadata is being created
   * @returns The tracking ID
   */
  public ensureCellHasTrackingMetadata(
    cell: Cell,
    origin: 'user' | 'ai' | 'system' = 'user'
  ): string {
    const metadata: any = cell.model.sharedModel.getMetadata() || {};

    // Check if cell_tracker metadata already exists
    if (metadata.cell_tracker && metadata.cell_tracker.trackingId) {
      // Update the last modified timestamp
      metadata.cell_tracker.lastModified = new Date().toISOString();
      cell.model.sharedModel.setMetadata(metadata);
      return metadata.cell_tracker.trackingId;
    }

    // Assign a numerical cell ID
    const trackingId = `cell_${this.getNextCellNumber()}`;
    const trackingMetadata: ICellTrackingMetadata = {
      trackingId,
      createdAt: new Date().toISOString(),
      lastModified: new Date().toISOString(),
      origin: origin,
      summary: ''
    };

    // Add metadata to the cell
    metadata.cell_tracker = trackingMetadata;
    cell.model.sharedModel.setMetadata(metadata);

    return trackingMetadata.trackingId;
  }

  /**
   * Find a cell by its tracking ID
   * @param trackingId The tracking ID to search for
   * @returns The cell if found, or null if not found
   */
  public findCellByTrackingId(
    trackingId: string
  ): { cell: Cell; index: number } | null {
    const notebook = this.notebookTracker.currentWidget?.content;
    if (!notebook) return null;

    const cells = notebook.widgets;
    for (let i = 0; i < cells.length; i++) {
      const cell = cells[i];
      const metadata: any = cell.model.sharedModel.getMetadata() || {};

      if (
        metadata.cell_tracker &&
        metadata.cell_tracker.trackingId === trackingId
      ) {
        return { cell, index: i };
      }
    }

    return null;
  }

  /**
   * Get the tracking metadata for a cell
   * @param cell The cell to get metadata for
   * @returns The tracking metadata or null if not found
   */
  public getCellTrackingMetadata(cell: Cell): ICellTrackingMetadata | null {
    const metadata: any = cell.model.sharedModel.getMetadata() || {};
    return metadata.cell_tracker || null;
  }

  /**
   * Set the origin of a cell
   * @param cell The cell to update
   * @param origin The new origin value
   */
  public setCellOrigin(cell: Cell, origin: 'user' | 'ai' | 'system'): void {
    this.ensureCellHasTrackingMetadata(cell);
    const metadata: any = cell.model.sharedModel.getMetadata() || {};

    if (metadata.cell_tracker) {
      metadata.cell_tracker.origin = origin;
      metadata.cell_tracker.lastModified = new Date().toISOString();
      cell.model.sharedModel.setMetadata(metadata);
    }
  }

  /**
   * Get all tracking IDs in the current notebook
   * @returns Array of tracking IDs
   */
  public getAllTrackingIds(): string[] {
    const notebook = this.notebookTracker.currentWidget?.content;
    if (!notebook) return [];

    const cells = notebook.widgets;
    const ids: string[] = [];

    for (let i = 0; i < cells.length; i++) {
      const cell = cells[i];
      const metadata: any = cell.model.sharedModel.getMetadata() || {};

      if (metadata.cell_tracker && metadata.cell_tracker.trackingId) {
        ids.push(metadata.cell_tracker.trackingId);
      }
    }

    return ids;
  }
}
