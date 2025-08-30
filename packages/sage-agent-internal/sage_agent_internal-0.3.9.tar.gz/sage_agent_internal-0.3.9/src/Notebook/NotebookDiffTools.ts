// NotebookDiffTools.ts
/**
 * NotebookDiffTools - Utility class for showing diffs in JupyterLab cells.
 *
 * To install diff2html:
 *   yarn add diff2html
 *
 * In your extension, import these at the top of your code:
 *   import * as Diff2Html from 'diff2html';
 *   import 'diff2html/bundles/css/diff2html.min.css';
 *   import 'highlight.js/styles/github.css';  // For syntax highlighting in diffs
 *   import * as JsDiff from 'diff';
 *
 * This file integrates diff2html for the HTML diff view while keeping
 * all your original metadata, console-formatting, and cell-edit-mode logic.
 */
import { NotebookActions } from '@jupyterlab/notebook';
import { Cell } from '@jupyterlab/cells';
import { NotebookTools } from './NotebookTools';

import * as Diff2Html from 'diff2html'; // diff2html parser & HTML generator
import 'highlight.js/styles/github.css'; // highlight.js syntax highlighting for diffs
import 'diff2html/bundles/css/diff2html.min.css'; // diff2html styles
import * as JsDiff from 'diff';
import { ColorSchemeType } from 'diff2html/lib/types';
import { timeout } from '../utils';
import { Diff2HtmlUI } from 'diff2html/lib-esm/ui/js/diff2html-ui';
import { NotebookCellTools } from './NotebookCellTools';
import { inlineDiffService, MergeCallbacks } from './InlineDiffService';
import { AppStateService } from '../AppState';

export class NotebookDiffTools {
  private static themeObserver: MutationObserver | null = null;
  private static onThemeChangeCallbacks: (() => void)[] = [];

  /**
   * Detect JupyterLab's current theme and return appropriate diff2html color scheme
   * @returns ColorSchemeType.DARK for dark themes, ColorSchemeType.LIGHT for light themes
   */
  private static detectJupyterLabTheme(): ColorSchemeType {
    const isLightTheme = document.body.getAttribute('data-jp-theme-light');
    if (isLightTheme === 'false') {
      return ColorSchemeType.DARK;
    } else {
      return ColorSchemeType.LIGHT;
    }
  }

  /**
   * Set up theme change detection to automatically refresh diff displays
   * This method should be called once during initialization
   */
  public static initializeThemeDetection(): void {
    if (NotebookDiffTools.themeObserver) {
      return; // Already initialized
    }

    try {
      const targetElement = document.body;

      NotebookDiffTools.themeObserver = new MutationObserver(mutations => {
        let themeChanged = false;

        mutations.forEach(mutation => {
          if (mutation.type === 'attributes') {
            const attributeName = mutation.attributeName;
            if (
              attributeName === 'data-jp-theme-light' ||
              attributeName === 'data-jp-theme-name' ||
              attributeName === 'class'
            ) {
              themeChanged = true;
            }
          }
        });

        if (themeChanged) {
          console.log(
            'JupyterLab theme change detected, refreshing diff displays...'
          );
          NotebookDiffTools.onThemeChangeCallbacks.forEach(callback => {
            try {
              callback();
            } catch (error) {
              console.error('Error in theme change callback:', error);
            }
          });
        }
      });

      NotebookDiffTools.themeObserver.observe(targetElement, {
        attributes: true,
        attributeFilter: ['data-jp-theme-light', 'data-jp-theme-name', 'class']
      });

      console.log('Theme detection initialized for diff2html');
    } catch (error) {
      console.error('Failed to initialize theme detection:', error);
    }
  }

  /**
   * Register a callback to be called when the theme changes
   * @param callback Function to call when theme changes
   */
  public static onThemeChange(callback: () => void): void {
    NotebookDiffTools.onThemeChangeCallbacks.push(callback);
  }

  /**
   * Cleanup theme detection observer
   */
  public static cleanupThemeDetection(): void {
    if (NotebookDiffTools.themeObserver) {
      NotebookDiffTools.themeObserver.disconnect();
      NotebookDiffTools.themeObserver = null;
    }
    NotebookDiffTools.onThemeChangeCallbacks = [];
  }

  /**
   * Get the currently detected JupyterLab theme
   * @returns ColorSchemeType.DARK or ColorSchemeType.LIGHT
   */
  public static getCurrentTheme(): ColorSchemeType {
    return NotebookDiffTools.detectJupyterLabTheme();
  }

  /**
   * Check if the current theme is dark
   * @returns true if dark theme is detected, false otherwise
   */
  public static isDarkTheme(): boolean {
    return NotebookDiffTools.detectJupyterLabTheme() === ColorSchemeType.DARK;
  }

  /**
   * Calculate the difference between two strings line by line
   * @param oldText The original text
   * @param newText The new text
   * @returns An array of diff objects with line content and change type
   */
  public static calculateDiff(
    oldText: string,
    newText: string
  ): Array<{ line: string; type: 'added' | 'removed' | 'unchanged' }> {
    const oldLines = oldText.split('\n');
    const newLines = newText.split('\n');
    const result: Array<{
      line: string;
      type: 'added' | 'removed' | 'unchanged';
    }> = [];

    // Simple line-by-line diff
    let i = 0,
      j = 0;
    while (i < oldLines.length || j < newLines.length) {
      if (i >= oldLines.length) {
        result.push({ line: newLines[j], type: 'added' });
        j++;
      } else if (j >= newLines.length) {
        result.push({ line: oldLines[i], type: 'removed' });
        i++;
      } else if (oldLines[i] === newLines[j]) {
        result.push({ line: oldLines[i], type: 'unchanged' });
        i++;
        j++;
      } else {
        result.push({ line: oldLines[i], type: 'removed' });
        result.push({ line: newLines[j], type: 'added' });
        i++;
        j++;
      }
    }

    return result;
  }

  /**
   * Format diff results for console output with ANSI color codes
   * @param diff The diff result array
   * @returns Colored string representation of the diff
   */
  formatDiffForConsole(
    diff: Array<{ line: string; type: 'added' | 'removed' | 'unchanged' }>
  ): string {
    const RED = '\x1b[31m';
    const GREEN = '\x1b[32m';
    const RESET = '\x1b[0m';

    return diff
      .map(item => {
        if (item.type === 'added') {
          return `${GREEN}+ ${item.line}${RESET}`;
        } else if (item.type === 'removed') {
          return `${RED}- ${item.line}${RESET}`;
        } else {
          return `  ${item.line}`;
        }
      })
      .join('\n');
  }

  /**
   * Private helper: generate an HTML diff using jsdiff → unified diff → diff2html
   * @param oldText Raw original text
   * @param newText Raw new text
   * @param showAllLines Whether to show all lines or only the changed lines
   * @returns Fully formatted HTML diff snippet
   */
  static generateHtmlDiff(
    oldText: string,
    newText: string,
    showAllLines: boolean
  ): string {
    const allLinesArg = showAllLines ? ['', '', { context: Infinity }] : [];
    // Create a unified diff string with jsdiff
    const unifiedDiff = JsDiff.createTwoFilesPatch(
      'Original.py',
      'Modified.py',
      oldText,
      newText,
      ...(allLinesArg as [string, string, { context: number }])
    );

    // Detect current JupyterLab theme dynamically
    const colorScheme = NotebookDiffTools.detectJupyterLabTheme();

    // Parse into JSON diff structure
    const diffJson = Diff2Html.parse(unifiedDiff, {
      // Remove inputFormat as it's not in Diff2HtmlConfig
      outputFormat: 'line-by-line',
      matching: 'lines',
      colorScheme: colorScheme
    });

    // Set the language to python for all blocks
    // There's a bug in diff2html where the language is not set correctly
    // when the diff is generated with context = Infinity
    diffJson.forEach(block => {
      block.language = 'py';
    });

    const element = document.createElement('div');

    const diff2htmlUi = new Diff2HtmlUI(element, diffJson, {
      drawFileList: false,
      outputFormat: 'line-by-line',
      matching: 'lines',
      colorScheme: colorScheme,
      highlight: true
    });

    diff2htmlUi.highlightCode();
    diff2htmlUi.draw();

    // Render HTML
    return element.innerHTML;
  }

  /**
   * Display a diff in a cell using the InlineDiffService
   * @param notebookTools The notebook tools instance
   * @param cell The cell to display the diff in
   * @param oldText The original text content
   * @param newText The new text content
   * @param operation The operation being performed (add, edit, remove)
   * @returns Object containing the updated cell info (htmlDiff is empty string for compatibility)
   */
  display_diff(
    notebookTools: NotebookTools,
    cell: Cell,
    oldText: string,
    newText: string,
    operation: string
  ): { htmlDiff: string; cell: Cell; cellId: string } {
    try {
      const normalizedOld = notebookTools.normalizeContent(oldText);
      const normalizedNew = notebookTools.normalizeContent(newText);

      const nbWidget = notebookTools.getCurrentNotebook();
      if (!nbWidget?.notebook) {
        throw new Error('No active notebook found');
      }
      notebookTools.activateCell(cell);

      const originalCellType = cell.model.type;
      this.store_diff_metadata(
        cell,
        oldText,
        newText,
        operation,
        originalCellType
      );

      const updatedCell = notebookTools.getCurrentNotebook()?.notebook
        .activeCell as Cell;

      // Set up merge callbacks to handle accept/reject operations
      const mergeCallbacks: MergeCallbacks = {
        onApproveAll: (cellId: string) => {
          console.log(
            `[NotebookDiffTools] Diff all approved for cell ${cellId}`
          );
          AppStateService.getNotebookDiffManager().approveCellDiff(cellId);
        },
        onAllResolved: (cellId: string) => {
          console.log(
            `[NotebookDiffTools] Diff all resolved for cell ${cellId}`
          );
          AppStateService.getNotebookDiffManager().approveCellDiff(cellId);
        },
        onRejectAll: (cellId: string) => {
          console.log(
            `[NotebookDiffTools] Diff all rejected for cell ${cellId}`
          );
          AppStateService.getNotebookDiffManager().rejectCellDiff(cellId);
        }
      };

      // Use InlineDiffService to show the unified merge view
      inlineDiffService.showInlineDiff(
        updatedCell,
        normalizedOld,
        normalizedNew,
        mergeCallbacks
      );

      return {
        htmlDiff: '', // Empty string for compatibility - inline diff doesn't use HTML overlays
        cell: updatedCell,
        cellId: updatedCell.model.id
      };
    } catch (error) {
      console.error('Error displaying diff:', error);
      throw error;
    }
  }

  /**
   * Remove diff overlay from a cell
   * @param cell The cell to remove the diff overlay from
   */
  static removeDiffOverlay(cell: Cell): void {
    try {
      const editorArea = cell.node.getElementsByClassName(
        'jp-InputArea-editor'
      );
      const item = editorArea.item(0) as HTMLElement;

      if (item) {
        const overlay = item.querySelector('.jp-DiffOverlay');
        if (overlay) {
          overlay.remove();
        }
        item.style.removeProperty('min-height');
      }
    } catch (error) {
      console.error('Error removing diff overlay:', error);
    }
  }

  /**
   * Clean up diff metadata from a cell
   * @param cell The cell to clean up metadata from
   */
  private cleanupDiffMetadata(cell: Cell): void {
    try {
      const meta = cell.model.sharedModel.getMetadata() || {};
      const cleanedMeta = { ...meta };

      if (cleanedMeta.custom) {
        // Fix the spread operator issue by checking if custom is an object
        const customData: any =
          typeof cleanedMeta.custom === 'object' && cleanedMeta.custom
            ? { ...cleanedMeta.custom }
            : {};

        // Create a clean version without the diff property
        if (customData) {
          delete customData.diff;
          cleanedMeta.custom = customData;
        }
      }

      cell.model.sharedModel.setMetadata(cleanedMeta);
      console.log('Cleaned up diff metadata for cell:', cell.model.id);
    } catch (error) {
      console.error('Error cleaning up diff metadata:', error);
    }
  }

  /**
   * Store original and new content in cell metadata
   */
  store_diff_metadata(
    cell: Cell,
    oldText: string,
    newText: string,
    operation: string,
    originalCellType: string
  ): void {
    try {
      const currentMeta = cell.model.sharedModel.getMetadata() || {};
      const diffMeta = {
        originalContent: oldText,
        newContent: newText,
        operation,
        originalCellType,
        timestamp: new Date().toISOString()
      };
      const customData =
        typeof currentMeta.custom === 'object' && currentMeta.custom
          ? currentMeta.custom
          : {};
      const updatedMeta = {
        ...currentMeta,
        custom: {
          ...customData,
          diff: diffMeta
        }
      };
      cell.model.sharedModel.setMetadata(updatedMeta);
      console.log(
        'Cell metadata after storing diff:',
        cell.model.sharedModel.getMetadata()
      );
    } catch (error) {
      console.error('Error storing diff metadata:', error);
    }
  }

  /**
   * Apply or reject the diff using InlineDiffService chunk acceptance
   */
  apply_diff(
    notebookTools: NotebookTools,
    cell: Cell,
    accept: boolean
  ): { success: boolean; updatedCellId?: string } {
    try {
      console.log(
        'APPLYING DIFF ================================== APPLYING DIFF ============== APPYING DIFF'
      );
      const notebook = notebookTools.getCurrentNotebook()?.notebook;

      notebookTools.activateCell(cell);
      const active = notebookTools.getCurrentNotebook()?.notebook
        .activeCell as Cell;

      if (cell.model.type === 'markdown' && notebook) {
        const restoreScroll = NotebookCellTools.preventScrolling(notebook);

        void NotebookActions.runCells(notebook, [cell]);

        restoreScroll();
      }

      const meta = active.model.sharedModel.getMetadata() || {};
      const custom: any = meta.custom || {};
      const diffMeta = custom.diff as any;
      if (!diffMeta) {
        console.warn('No diff metadata found');
        return { success: false };
      }

      const {
        originalContent = '',
        newContent = '',
        operation = '',
        originalCellType = 'code'
      } = diffMeta;

      // Get the cell ID for the inline diff service
      const cellId = (
        active.model.sharedModel.getMetadata()?.cell_tracker as any
      )?.trackingId;

      if (accept) {
        if (operation !== 'remove' && cellId && inlineDiffService) {
          inlineDiffService.acceptAllChunks(cellId);
        }
      } else {
        if (operation === 'add') {
          active.model.sharedModel.setSource('');
        } else {
          active.model.sharedModel.setSource(originalContent);
        }

        if (cellId && inlineDiffService) {
          inlineDiffService.cleanupMergeView(cellId);
        }
      }

      // Restore cell type if changed
      const nb = notebookTools.getCurrentNotebook()?.notebook;
      let updatedId = active.model.id;
      if (nb && active.model.type !== originalCellType) {
        NotebookActions.changeCellType(nb, originalCellType);
        const nowActive = nb.activeCell;
        if (nowActive && nowActive.model.id !== updatedId) {
          updatedId = nowActive.model.id;
        }
      }

      // Clean up diff metadata using the helper method
      this.cleanupDiffMetadata(active);

      console.log(
        'Cell metadata after applying diff:',
        active.model.sharedModel.getMetadata()
      );

      return { success: true, updatedCellId: updatedId };
    } catch (error) {
      console.error('Error applying diff:', error);
      return { success: false };
    }
  }

  /**
   * Log diff to console, now using diff2html for HTML portion
   */
  logDiff(
    normalizeContent: (content: string) => string,
    oldText: string,
    newText: string,
    operation: string,
    cellId?: string
  ): void {
    const nOld = normalizeContent(oldText);
    const nNew = normalizeContent(newText);

    const diffArr =
      operation === 'add' && nOld === ''
        ? nNew.split('\n').map(line => ({ line, type: 'added' as const }))
        : NotebookDiffTools.calculateDiff(nOld, nNew);

    console.log(
      `--- DIFF for ${operation}${cellId ? ` on cell ${cellId}` : ''} ---`
    );
    console.log(this.formatDiffForConsole(diffArr));
    console.log('--- END DIFF ---');
  }
}
