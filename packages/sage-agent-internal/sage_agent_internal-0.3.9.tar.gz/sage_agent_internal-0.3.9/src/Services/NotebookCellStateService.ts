import { StateDBCachingService } from '../utils/stateDBCaching';
import { AppStateService } from '../AppState';
import * as JsDiff from 'diff';

/**
 * Interface for cached cell state
 */
export interface ICachedCellState {
  id: string;
  trackingId?: string;
  type: string;
  content: string;
  execution_count?: number;
  index: number;
  outputs?: any[];
}

/**
 * Interface for notebook state cache
 */
export interface INotebookStateCache {
  notebookId: string;
  cells: ICachedCellState[];
  timestamp: number;
}

/**
 * Interface for cell change diff
 */
export interface ICellChangeDiff {
  cellId: string;
  trackingId?: string;
  type: 'added' | 'removed' | 'modified' | 'moved';
  oldContent?: string;
  newContent?: string;
  oldIndex?: number;
  newIndex?: number;
  diff?: string; // Human-readable diff
}

/**
 * Service for caching and tracking notebook cell state changes between messages
 */
export class NotebookCellStateService {
  private static readonly CACHE_KEY_PREFIX = 'notebook-cell-state';

  /**
   * Check if the notebook has any meaningful content (non-empty cells)
   */
  public static hasContent(notebookId?: string): boolean {
    const currentState =
      NotebookCellStateService.getCurrentNotebookState(notebookId);
    if (!currentState) {
      return false;
    }

    return currentState.some(cell => {
      const content = cell.content || '';
      return content.trim().length > 0;
    });
  }

  /**
   * Get the cache key for a specific notebook
   */
  private static getCacheKey(notebookId: string): string {
    return `${NotebookCellStateService.CACHE_KEY_PREFIX}:${notebookId}`;
  }

  /**
   * Get the current state of all cells in the active notebook
   */
  public static getCurrentNotebookState(
    notebookId?: string
  ): ICachedCellState[] | null {
    const currentNotebookId =
      notebookId || AppStateService.getCurrentNotebookId();
    if (!currentNotebookId) {
      console.warn(
        '[NotebookCellStateService] No current notebook ID available'
      );
      return null;
    }

    try {
      const notebookTools = AppStateService.getNotebookTools();
      const cellData = notebookTools.read_cells({
        notebook_path: currentNotebookId,
        include_outputs: true,
        include_metadata: true
      });

      if (!cellData || !cellData.cells) {
        return [];
      }

      return cellData.cells.map((cell, index) => ({
        id: cell.id,
        trackingId: cell.trackingId || cell.id, // Fallback to regular ID if no trackingId
        type: cell.type,
        content: cell.content || '', // Ensure content is never undefined
        execution_count: cell.execution_count,
        index: index,
        outputs: cell.outputs
      }));
    } catch (error) {
      console.error(
        '[NotebookCellStateService] Error getting current notebook state:',
        error
      );
      return null;
    }
  }

  /**
   * Cache the current notebook state
   */
  public static async cacheCurrentNotebookState(
    notebookId?: string
  ): Promise<void> {
    const currentNotebookId =
      notebookId || AppStateService.getCurrentNotebookId();
    if (!currentNotebookId) {
      console.warn(
        '[NotebookCellStateService] No current notebook ID available for caching'
      );
      return;
    }

    const cells =
      NotebookCellStateService.getCurrentNotebookState(currentNotebookId);
    if (cells === null) {
      console.warn(
        '[NotebookCellStateService] Could not get current notebook state for caching'
      );
      return;
    }

    await this.cacheNotebookState(currentNotebookId, cells);
  }

  public static async cacheNotebookState(
    notebookId: string,
    cells: ICachedCellState[]
  ): Promise<void> {
    // Only cache cells that have meaningful content to avoid false diffs
    const cellsWithContent = cells.filter(
      cell => cell.content && cell.content.trim().length > 0
    );

    const cacheData: INotebookStateCache = {
      notebookId: notebookId,
      cells: cellsWithContent,
      timestamp: Date.now()
    };

    try {
      const cacheKey = NotebookCellStateService.getCacheKey(notebookId);
      await StateDBCachingService.setObjectValue(cacheKey, cacheData);
      console.log(
        `[NotebookCellStateService] Cached state for notebook ${notebookId} with ${cellsWithContent.length} cells (filtered from ${cells.length} total)`
      );
    } catch (error) {
      console.error(
        '[NotebookCellStateService] Error caching notebook state:',
        error
      );
    }
  }

  /**
   * Get the cached notebook state
   */
  public static async getCachedNotebookState(
    notebookId?: string
  ): Promise<INotebookStateCache | null> {
    const currentNotebookId =
      notebookId || AppStateService.getCurrentNotebookId();
    if (!currentNotebookId) {
      console.warn(
        '[NotebookCellStateService] No current notebook ID available for getting cached state'
      );
      return null;
    }

    try {
      const cacheKey = NotebookCellStateService.getCacheKey(currentNotebookId);
      const cachedData =
        await StateDBCachingService.getObjectValue<INotebookStateCache | null>(
          cacheKey,
          null
        );
      return cachedData;
    } catch (error) {
      console.error(
        '[NotebookCellStateService] Error getting cached notebook state:',
        error
      );
      return null;
    }
  }

  /**
   * Compare current state with cached state and generate diffs
   */
  public static async detectChanges(
    notebookId?: string
  ): Promise<ICellChangeDiff[]> {
    const currentNotebookId =
      notebookId || AppStateService.getCurrentNotebookId();
    if (!currentNotebookId) {
      console.warn(
        '[NotebookCellStateService] No current notebook ID available for change detection'
      );
      return [];
    }

    // Early exit if notebook has no meaningful content
    if (!NotebookCellStateService.hasContent(currentNotebookId)) {
      console.log(
        '[NotebookCellStateService] Notebook has no meaningful content - no diffs to report'
      );
      return [];
    }

    const currentState =
      NotebookCellStateService.getCurrentNotebookState(currentNotebookId);
    const cachedData =
      await NotebookCellStateService.getCachedNotebookState(currentNotebookId);

    if (!currentState) {
      console.warn(
        '[NotebookCellStateService] Could not get current state for change detection'
      );
      return [];
    }

    // Filter out cells with no content to avoid false positives
    const currentCellsWithContent = currentState.filter(cell => {
      const content = cell.content || '';
      return content.trim().length > 0;
    });

    console.log(
      `[NotebookCellStateService] Current cells with content: ${currentCellsWithContent.length}`
    );

    if (!cachedData || !cachedData.cells) {
      console.log(
        '[NotebookCellStateService] No cached state found - caching current state without generating diffs'
      );
      // Cache current state but don't treat as changes since we have no baseline to compare against
      await NotebookCellStateService.cacheCurrentNotebookState(
        currentNotebookId
      );
      return [];
    }

    // Filter cached cells with content as well
    const cachedCellsWithContent = cachedData.cells.filter(cell => {
      const content = cell.content || '';
      return content.trim().length > 0;
    });

    console.log(
      `[NotebookCellStateService] Cached cells with content: ${cachedCellsWithContent.length}`
    );

    const changes: ICellChangeDiff[] = [];

    // Use trackingId as the primary key for comparison, fallback to regular id if no trackingId
    const cachedCellsByTrackingId = new Map<string, ICachedCellState>();
    const currentCellsByTrackingId = new Map<string, ICachedCellState>();

    // Build maps using trackingId as the key
    for (const cell of cachedCellsWithContent) {
      const key = cell.trackingId || cell.id;
      cachedCellsByTrackingId.set(key, cell);
    }

    for (const cell of currentCellsWithContent) {
      const key = cell.trackingId || cell.id;
      currentCellsByTrackingId.set(key, cell);
    }

    console.log(
      `[NotebookCellStateService] Cached cells by tracking ID: [${Array.from(cachedCellsByTrackingId.keys()).join(', ')}]`
    );
    console.log(
      `[NotebookCellStateService] Current cells by tracking ID: [${Array.from(currentCellsByTrackingId.keys()).join(', ')}]`
    );

    // Check for new or modified cells
    for (const currentCell of currentCellsWithContent) {
      const trackingKey = currentCell.trackingId || currentCell.id;
      const cachedCell = cachedCellsByTrackingId.get(trackingKey);

      if (!cachedCell) {
        // New cell - only add if it has meaningful content
        const content = currentCell.content || '';
        if (content.trim().length > 0) {
          console.log(
            `[NotebookCellStateService] Detected new cell: ${trackingKey}`
          );
          changes.push({
            cellId: currentCell.id,
            trackingId: currentCell.trackingId,
            type: 'added',
            newContent: currentCell.content,
            newIndex: currentCell.index,
            diff: `+ Added new ${currentCell.type} cell: ${currentCell.content.substring(0, 100)}${currentCell.content.length > 100 ? '...' : ''}`
          });
        }
      } else {
        // Check for actual content changes (ignore execution count and minor position changes)
        const currentContent = (currentCell.content || '').trim();
        const cachedContent = (cachedCell.content || '').trim();
        const contentChanged = cachedContent !== currentContent;
        const meaningfulPositionChange =
          Math.abs((cachedCell.index || 0) - (currentCell.index || 0)) > 1;

        if (contentChanged || meaningfulPositionChange) {
          console.log(
            `[NotebookCellStateService] Detected modified cell: ${trackingKey} (content changed: ${contentChanged}, position changed: ${meaningfulPositionChange})`
          );

          // Modified cell
          const textDiff = JsDiff.createPatch(
            `cell_${currentCell.trackingId || currentCell.id}`,
            cachedCell.content,
            currentCell.content,
            `Before (execution ${cachedCell.execution_count || 'none'})`,
            `After (execution ${currentCell.execution_count || 'none'})`
          );

          changes.push({
            cellId: currentCell.id,
            trackingId: currentCell.trackingId,
            type:
              meaningfulPositionChange && !contentChanged
                ? 'moved'
                : 'modified',
            oldContent: cachedCell.content,
            newContent: currentCell.content,
            oldIndex: cachedCell.index,
            newIndex: currentCell.index,
            diff: textDiff
          });
        }
      }
    }

    // Check for removed cells
    for (const cachedCell of cachedCellsWithContent) {
      const trackingKey = cachedCell.trackingId || cachedCell.id;
      if (!currentCellsByTrackingId.has(trackingKey)) {
        console.log(
          `[NotebookCellStateService] Detected removed cell: ${trackingKey}`
        );
        changes.push({
          cellId: cachedCell.id,
          trackingId: cachedCell.trackingId,
          type: 'removed',
          oldContent: cachedCell.content,
          oldIndex: cachedCell.index,
          diff: `- Removed ${cachedCell.type} cell: ${cachedCell.content.substring(0, 100)}${cachedCell.content.length > 100 ? '...' : ''}`
        });
      }
    }

    console.log(
      `[NotebookCellStateService] Total changes detected: ${changes.length}`
    );
    return changes;
  }

  /**
   * Generate XML-formatted diff for a cell change
   */
  private static generateXMLDiff(change: ICellChangeDiff): string {
    const cellRef = change.trackingId || change.cellId;
    let xmlDiff = `<diff - (${cellRef})>\n`;

    switch (change.type) {
      case 'added': {
        // For added cells, show each line as an addition
        const newLines = (change.newContent || '').split('\n');
        newLines.forEach((line, index) => {
          if (line.trim() || index < newLines.length - 1) {
            // Include empty lines except trailing ones
            xmlDiff += `    <diff - add - line ${index + 1}>\n`;
            xmlDiff += `        ${line}\n`;
            xmlDiff += `    </diff - add - line ${index + 1}>\n`;
          }
        });
        break;
      }

      case 'removed': {
        // For removed cells, show each line as a removal
        const oldLines = (change.oldContent || '').split('\n');
        oldLines.forEach((line, index) => {
          if (line.trim() || index < oldLines.length - 1) {
            // Include empty lines except trailing ones
            xmlDiff += `    <diff - remove - line ${index + 1}>\n`;
            xmlDiff += `        ${line}\n`;
            xmlDiff += `    </diff - remove - line ${index + 1}>\n`;
          }
        });
        break;
      }

      case 'modified':
      case 'moved': {
        // For modified cells, we'll show line-by-line differences
        const oldContent = change.oldContent || '';
        const newContent = change.newContent || '';

        const oldLines = oldContent.split('\n');
        const newLines = newContent.split('\n');

        // Use a simple line-by-line comparison
        const maxLines = Math.max(oldLines.length, newLines.length);

        for (let i = 0; i < maxLines; i++) {
          const oldLine = i < oldLines.length ? oldLines[i] : undefined;
          const newLine = i < newLines.length ? newLines[i] : undefined;
          const lineNum = i + 1;

          if (oldLine === undefined && newLine !== undefined) {
            // Line was added
            xmlDiff += `    <diff - add - line ${lineNum}>\n`;
            xmlDiff += `        ${newLine}\n`;
            xmlDiff += `    </diff - add - line ${lineNum}>\n`;
          } else if (oldLine !== undefined && newLine === undefined) {
            // Line was removed
            xmlDiff += `    <diff - remove - line ${lineNum}>\n`;
            xmlDiff += `        ${oldLine}\n`;
            xmlDiff += `    </diff - remove - line ${lineNum}>\n`;
          } else if (oldLine !== newLine) {
            // Line was modified - show both removed and added
            xmlDiff += `    <diff - edit - line ${lineNum}>\n`;
            xmlDiff += `        removed: ${oldLine}\n`;
            xmlDiff += `        added: ${newLine}\n`;
            xmlDiff += `    </diff - edit - line ${lineNum}>\n`;
          }
          // Skip unchanged lines to keep the diff focused
        }

        // If it's a moved cell, add position information
        if (change.type === 'moved') {
          xmlDiff += `    <diff - move>\n`;
          xmlDiff += `        from_position: ${change.oldIndex}\n`;
          xmlDiff += `        to_position: ${change.newIndex}\n`;
          xmlDiff += `    </diff - move>\n`;
        }
        break;
      }
    }

    xmlDiff += `</diff - (${cellRef})>\n`;
    return xmlDiff;
  }

  /**
   * Generate a human-readable summary of changes for the LLM
   */
  public static generateChangeSummaryMessage(
    changes: ICellChangeDiff[]
  ): string {
    if (changes.length === 0) {
      return '';
    }

    let summary = '\n\n=== NOTEBOOK CHANGES SINCE LAST MESSAGE ===\n\n';
    summary += `Detected ${changes.length} change(s) in the notebook:\n\n`;

    for (const change of changes) {
      summary += NotebookCellStateService.generateXMLDiff(change);
      summary += '\n';
    }

    summary += '=== END NOTEBOOK CHANGES ===\n\n';
    return summary;
  }

  /**
   * Initialize the service for a notebook - should be called when first opening/switching to a notebook
   * This ensures we have a proper baseline without treating initial content as diffs
   */
  public static async initializeForNotebook(
    notebookId?: string
  ): Promise<void> {
    const currentNotebookId =
      notebookId || AppStateService.getCurrentNotebookId();
    if (!currentNotebookId) {
      console.warn(
        '[NotebookCellStateService] No current notebook ID available for initialization'
      );
      return;
    }

    // Clear any existing cache for this notebook
    await NotebookCellStateService.clearCachedState(currentNotebookId);

    // Cache the current state as the baseline if there's meaningful content
    if (NotebookCellStateService.hasContent(currentNotebookId)) {
      await NotebookCellStateService.cacheCurrentNotebookState(
        currentNotebookId
      );
      console.log(
        `[NotebookCellStateService] Initialized baseline state for notebook ${currentNotebookId}`
      );
    } else {
      console.log(
        `[NotebookCellStateService] Notebook ${currentNotebookId} has no content - skipping baseline cache`
      );
    }
  }

  /**
   * Debug method to log current notebook state
   */
  public static debugCurrentState(notebookId?: string): void {
    const currentState =
      NotebookCellStateService.getCurrentNotebookState(notebookId);
    const currentNotebookId =
      notebookId || AppStateService.getCurrentNotebookId();

    console.log(
      `[NotebookCellStateService] DEBUG - Current state for notebook: ${currentNotebookId}`
    );

    if (!currentState) {
      console.log('  No current state available');
      return;
    }

    console.log(`  Total cells: ${currentState.length}`);

    currentState.forEach((cell, index) => {
      const content = cell.content || '';
      const contentPreview = content.slice(0, 50).replace(/\n/g, '\\n');
      console.log(
        `  Cell ${index}: id="${cell.id}", trackingId="${cell.trackingId}", type="${cell.type}", content="${contentPreview}${content.length > 50 ? '...' : ''}"`
      );
    });
  }

  /**
   * Clear cached state for a notebook (useful for cleanup)
   */
  public static async clearCachedState(notebookId?: string): Promise<void> {
    const currentNotebookId =
      notebookId || AppStateService.getCurrentNotebookId();
    if (!currentNotebookId) {
      console.warn(
        '[NotebookCellStateService] No current notebook ID available for clearing cache'
      );
      return;
    }

    try {
      const cacheKey = NotebookCellStateService.getCacheKey(currentNotebookId);
      await StateDBCachingService.removeValue(cacheKey);
      console.log(
        `[NotebookCellStateService] Cleared cached state for notebook ${currentNotebookId}`
      );
    } catch (error) {
      console.error(
        '[NotebookCellStateService] Error clearing cached state:',
        error
      );
    }
  }
}
