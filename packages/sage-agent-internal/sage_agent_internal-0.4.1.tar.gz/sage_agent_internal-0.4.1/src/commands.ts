import { JupyterFrontEnd } from '@jupyterlab/application';
import { ICommandPalette } from '@jupyterlab/apputils';
import { AppStateService } from './AppState';
import { StateDBCachingService, STATE_DB_KEYS } from './utils/stateDBCaching';
import { inlineDiffService } from './Notebook/InlineDiffService';

/**
 * Register all commands for the sage-ai extension
 */
export function registerCommands(
  app: JupyterFrontEnd,
  palette: ICommandPalette
): void {
  // Register test notebook command
  registerTestNotebookCommand(app, palette);

  // Register test add with diff command
  registerTestAddWithDiffCommand(app, palette);

  // Register test edit with diff command
  registerTestEditWithDiffCommand(app, palette);

  // Register test multiple diffs command
  registerTestMultipleDiffsCommand(app, palette);

  // Register test tracking persistence command
  registerTestTrackingPersistenceCommand(app, palette);

  // Register tracking report command
  registerTrackingReportCommand(app, palette);

  // Register fix tracking IDs command
  registerFixTrackingIDsCommand(app, palette);

  // Register export error logs command
  registerExportErrorLogsCommand(app, palette);

  // Register clear error logs command
  registerClearErrorLogsCommand(app, palette);
}

/**
 * Register the test notebook command
 */
function registerTestNotebookCommand(
  app: JupyterFrontEnd,
  palette: ICommandPalette
): void {
  const testNotebookCommand: string = 'sage-ai:test-notebook';

  app.commands.addCommand(testNotebookCommand, {
    label: 'Test Notebook',
    execute: async () => {
      const notebookTools = AppStateService.getNotebookTools();

      // Test our NotebookTools class by adding a cell with tracking
      const trackingId = notebookTools.add_cell({
        cell_type: 'code',
        source:
          '# This is a test cell created by NotebookTools\nprint("Hello from Sage AI!")\nimport time\ntime.sleep(1)\nprint("Cell with stable tracking ID!")',
        summary: 'Test cell created with tracking ID',
        position: null // Append to the end
      });

      // Add a second cell with tracking ID
      const trackingId2 = notebookTools.add_cell({
        cell_type: 'markdown',
        source:
          '# This is a test markdown cell\n\nWith stable tracking ID!\n\n* List item 1\n* List item 2',
        summary: 'Test markdown cell created with tracking ID',
        position: null // Append to the end
      });

      // Show all cells info with their tracking IDs
      console.log('Cell tracking ID 1:', trackingId);
      console.log('Cell tracking ID 2:', trackingId2);

      // Wait 2 seconds then find cells by tracking ID
      setTimeout(() => {
        const cell1 = notebookTools.findCellByAnyId(trackingId);
        const cell2 = notebookTools.findCellByAnyId(trackingId2);

        console.log('Found cell 1 by tracking ID:', cell1 ? 'Yes' : 'No');
        console.log('Found cell 2 by tracking ID:', cell2 ? 'Yes' : 'No');

        // Update cell content to demonstrate persistence
        if (cell1) {
          notebookTools.edit_cell({
            cell_id: trackingId,
            new_source:
              '# Updated cell content\nprint("This cell was found by tracking ID!")\nimport time\ntime.sleep(1)\nprint("Success!")',
            summary: 'Updated test cell',
            is_tracking_id: true
          });
        }
      }, 2000);
    }
  });

  // Add the test notebook command to the command palette
  palette.addItem({ command: testNotebookCommand, category: 'AI Tools' });
}

/**
 * Register the test add with diff command
 */
function registerTestAddWithDiffCommand(
  app: JupyterFrontEnd,
  palette: ICommandPalette
): void {
  const testAddWithDiffCommand: string = 'sage-ai:test-add-with-diff';

  app.commands.addCommand(testAddWithDiffCommand, {
    label: 'Test Add Cell With Diff',
    execute: async () => {
      const notebookTools = AppStateService.getNotebookTools();
      const diffManager = AppStateService.getNotebookDiffManager();
      const notebooks = AppStateService.getNotebookTracker();

      // Step 1: Add a new cell with tracking ID
      const trackingId = notebookTools.add_cell({
        cell_type: 'code',
        source:
          '# Test cell with diff view\nprint("This cell demonstrates diff view")\nfor i in range(5):\n    print(f"Count: {i}")',
        summary: 'Test cell with diff view',
        position: null
      });

      // Step 2: Find the added cell by tracking ID
      const cellInfo = notebookTools.findCellByAnyId(trackingId);
      if (!cellInfo) {
        console.error('Could not find the newly added cell by tracking ID');
        return;
      }

      // Get current notebook path
      const notebookPath = notebooks.currentWidget?.context.path || null;

      // Step 3: Track the diff in the diff manager with notebook path
      diffManager.trackAddCell(
        trackingId,
        cellInfo.cell.model.sharedModel.getSource(),
        'Test cell with diff view',
        notebookPath
      );

      // Step 4: Display the diff view
      console.log('Displaying diff view...');
      const diffResult = notebookTools.display_diff(
        cellInfo.cell,
        '', // Original content (empty for new cell)
        cellInfo.cell.model.sharedModel.getSource(),
        'add'
      );

      // Store the updated cell ID and update the mapping in diff manager
      const updatedCellId = diffResult.cellId;
      console.log(
        `Original tracking ID: ${trackingId}, Updated cell ID: ${updatedCellId}`
      );
      diffManager.updateCellIdMapping(trackingId, updatedCellId, notebookPath);

      // Step 5: Show approval dialog using the notebook widget for proper positioning
      const activeNotebook = notebooks.currentWidget;

      // Get unique_id from notebook metadata to use as notebook ID
      let notebookUniqueId: string | null = null;
      if (activeNotebook) {
        try {
          const contentManager = AppStateService.getContentManager();
          const nbFile = await contentManager?.get(activeNotebook.context.path);
          if (nbFile?.content?.metadata?.sage_ai?.unique_id) {
            notebookUniqueId = nbFile.content.metadata.sage_ai.unique_id;
          }
        } catch (error) {
          console.warn('Could not get notebook metadata in commands:', error);
        }
      }

      const result = await diffManager.showApprovalDialog(
        activeNotebook ? activeNotebook.node : document.body,
        false, // Use standard dialog mode for notebook context
        false, // Not a run context
        notebookUniqueId ||
          (activeNotebook ? activeNotebook.context.path : null) // Pass the unique_id as notebook ID
      );
      console.log('Diff approval result:', result);

      // Step 7: Demonstrate finding the cell by tracking ID after diff approval
      setTimeout(() => {
        const updatedCellInfo = notebookTools.findCellByAnyId(
          trackingId,
          notebookPath
        );
        console.log(
          'Found cell after diff approval:',
          updatedCellInfo ? 'Yes' : 'No'
        );
      }, 1000);
    }
  });

  // Add the test add with diff command to the command palette
  palette.addItem({ command: testAddWithDiffCommand, category: 'AI Tools' });
}

/**
 * Register the test edit with diff command
 */
function registerTestEditWithDiffCommand(
  app: JupyterFrontEnd,
  palette: ICommandPalette
): void {
  const testEditWithDiffCommand: string = 'sage-ai:test-edit-with-diff';

  app.commands.addCommand(testEditWithDiffCommand, {
    label: 'Test Edit Cell With Diff',
    execute: async () => {
      const notebookTools = AppStateService.getNotebookTools();
      const diffManager = AppStateService.getNotebookDiffManager();
      const notebooks = AppStateService.getNotebookTracker();

      // Step 1: Add a new cell with tracking ID
      console.log('Step 1: Adding new cell...');
      const trackingId = notebookTools.add_cell({
        cell_type: 'code',
        source:
          '# Original cell content\nprint("This is the original content")\nvalue = 42',
        summary: 'Original test cell',
        position: null
      });

      // Get original content
      const originalContent =
        '# Original cell content\nprint("This is the original content")\nvalue = 42';

      // Step 2: Wait 2 seconds before editing to ensure cell is rendered
      setTimeout(() => {
        console.log('Step 2: Editing cell after 2 seconds...');

        // Step 3: Edit the cell using tracking ID
        const newContent =
          '# Modified cell content\nprint("This content has been modified!")\nvalue = 42\nprint(f"The value is {value}")\n\n# Added a new comment';

        const editSuccess = notebookTools.edit_cell({
          cell_id: trackingId,
          new_source: newContent,
          summary: 'Modified test cell',
          is_tracking_id: true // Indicate we're using a tracking ID
        });

        if (!editSuccess) {
          console.error('Could not edit the cell with tracking ID');
          return;
        }

        // Get current notebook path
        const notebookPath = notebooks.currentWidget?.context.path || null;

        // Step 4: Track the diff in the manager using tracking ID and notebook path
        diffManager.trackEditCell(
          trackingId,
          originalContent,
          newContent,
          'Modified test cell',
          notebookPath
        );

        // Step 5: Wait 2 seconds before showing diff
        setTimeout(async () => {
          console.log('Step 3: Showing diff after edit...');

          // Step 7: Show approval dialog
          const result = await diffManager.showApprovalDialog(
            document.body,
            false, // Standard dialog mode
            false, // Not a run context
            notebooks.currentWidget?.context.path || null // Pass the current notebook path
          );
          console.log('Diff approval result:', result);

          // Step 8: Apply approved diffs and handle rejected ones
          await diffManager.applyApprovedDiffs();
          await diffManager.handleRejectedDiffs();

          // Step 9: Find the cell again by tracking ID after approval
          setTimeout(() => {
            const finalCellInfo = notebookTools.findCellByAnyId(
              trackingId,
              notebookPath
            );
            console.log(
              'Found cell after diff approval:',
              finalCellInfo ? 'Yes' : 'No'
            );
          }, 2000);
        }, 2000);
      }, 2000);
    }
  });

  // Add the test edit with diff command to the command palette
  palette.addItem({ command: testEditWithDiffCommand, category: 'AI Tools' });
}

/**
 * Register the test multiple diffs command
 */
function registerTestMultipleDiffsCommand(
  app: JupyterFrontEnd,
  palette: ICommandPalette
): void {
  const testMultipleDiffsCommand: string = 'sage-ai:test-multiple-diffs';

  app.commands.addCommand(testMultipleDiffsCommand, {
    label: 'Test Multiple Diffs',
    execute: async () => {
      const notebookTools = AppStateService.getNotebookTools();
      const diffManager = AppStateService.getNotebookDiffManager();
      const notebooks = AppStateService.getNotebookTracker();

      console.log('Running multiple diffs test with tracking IDs...');

      // Step 1: Add multiple cells with different content and get tracking IDs
      const trackingIds: any = [];

      // Add first cell (code)
      const trackingId1 = notebookTools.add_cell({
        cell_type: 'code',
        source: '# First cell\nx = 10\ny = 20\nprint(f"Sum: {x + y}")',
        summary: 'First test cell',
        position: null
      });
      trackingIds.push(trackingId1);
      console.log(`Added cell 1 with tracking ID: ${trackingId1}`);

      // Add second cell (markdown)
      const trackingId2 = notebookTools.add_cell({
        cell_type: 'markdown',
        source:
          '# Second Cell\nThis is a markdown cell for testing multiple diffs.',
        summary: 'Second test cell',
        position: null
      });
      trackingIds.push(trackingId2);
      console.log(`Added cell 2 with tracking ID: ${trackingId2}`);

      // Add third cell (code)
      const trackingId3 = notebookTools.add_cell({
        cell_type: 'code',
        source:
          '# Third cell\nimport matplotlib.pyplot as plt\nplt.figure(figsize=(8, 6))\nplt.plot([1, 2, 3, 4])\nplt.title("Test Plot")',
        summary: 'Third test cell',
        position: null
      });
      trackingIds.push(trackingId3);
      console.log(`Added cell 3 with tracking ID: ${trackingId3}`);

      // Wait to ensure cells are properly created and rendered
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Step 2: Prepare new content for the cells
      const newContents = [
        '# First cell - MODIFIED\nx = 10\ny = 20\nz = 30\nprint(f"Sum: {x + y + z}")', // Modified code
        '# Second Cell - MODIFIED\nThis is a **modified** markdown cell for testing multiple diffs.\n\n- Item 1\n- Item 2', // Modified markdown
        '# Third cell - MODIFIED\nimport matplotlib.pyplot as plt\nimport numpy as np\nx = np.linspace(0, 10, 100)\nplt.figure(figsize=(10, 8))\nplt.plot(x, np.sin(x))\nplt.title("Modified Plot")' // Modified code with plot
      ];

      // Step 3: Track all the diffs but find and display each cell individually
      for (let i = 0; i < trackingIds.length; i++) {
        const trackingId = trackingIds[i];
        // Find the cell by tracking ID
        const cellInfo = notebookTools.findCellByAnyId(trackingId);
        if (!cellInfo) {
          console.error(`Could not find cell with tracking ID ${trackingId}`);
          continue;
        }

        // Get original content
        const originalContent = cellInfo.cell.model.sharedModel.getSource();

        // Get current notebook path
        const notebookPath = notebooks.currentWidget?.context.path || null;

        // Track the diff using tracking ID and notebook path
        diffManager.trackEditCell(
          trackingId,
          originalContent,
          newContents[i],
          `Modified test cell ${i + 1}`,
          notebookPath
        );

        // Display the diff
        console.log(
          `Displaying diff for cell ${i + 1} with tracking ID ${trackingId}...`
        );
      }

      // Step 4: Show approval dialog
      const activeNotebook = notebooks.currentWidget;
      const result = await diffManager.showApprovalDialog(
        activeNotebook ? activeNotebook.node : document.body,
        false, // Use standard dialog mode
        false, // Not a run context
        activeNotebook ? activeNotebook.context.path : null // Pass the notebook path
      );
      console.log('Multiple diffs approval result:', result);

      // Step 5: Apply approved diffs and handle rejected ones
      // await diffManager.applyApprovedDiffs();
      // await diffManager.handleRejectedDiffs();

      // Step 6: Verify all cells can still be found by tracking ID
      setTimeout(() => {
        for (let i = 0; i < trackingIds.length; i++) {
          const trackingId = trackingIds[i];
          const cellInfo = notebookTools.findCellByAnyId(trackingId);
          console.log(
            `Found cell ${i + 1} after diff approval: ${cellInfo ? 'Yes' : 'No'}`
          );
        }
      }, 1000);
    }
  });

  // Add the test multiple diffs command to the command palette
  palette.addItem({
    command: testMultipleDiffsCommand,
    category: 'AI Tools'
  });
}

/**
 * Register the test tracking persistence command
 */
function registerTestTrackingPersistenceCommand(
  app: JupyterFrontEnd,
  palette: ICommandPalette
): void {
  const testTrackingPersistenceCommand: string =
    'sage-ai:test-tracking-persistence';

  app.commands.addCommand(testTrackingPersistenceCommand, {
    label: 'Test Tracking ID Persistence',
    execute: async () => {
      const notebookTools = AppStateService.getNotebookTools();
      const cellTrackingService = AppStateService.getCellTrackingService();

      console.log('Testing tracking ID persistence...');

      // Get all existing tracking IDs
      const allTrackingIds = cellTrackingService.getAllTrackingIds();
      console.log(`Found ${allTrackingIds.length} cells with tracking IDs`);
      console.log('Tracking IDs:', allTrackingIds);

      // Initialize tracking for any cells without tracking IDs
      cellTrackingService.initializeExistingCells();

      // Get updated list of tracking IDs
      const updatedTrackingIds = cellTrackingService.getAllTrackingIds();
      console.log(
        `Now have ${updatedTrackingIds.length} cells with tracking IDs`
      );

      // Add a new cell and then find it by tracking ID
      const newTrackingId = notebookTools.add_cell({
        cell_type: 'markdown',
        source:
          '# Persistence Test\n\nThis cell tests tracking ID persistence across notebook operations.',
        summary: 'Persistence test cell',
        position: null
      });

      console.log(`Added new cell with tracking ID: ${newTrackingId}`);

      // Find the cell right away
      const immediateFind = notebookTools.findCellByAnyId(newTrackingId);
      console.log('Found cell immediately:', immediateFind ? 'Yes' : 'No');

      // Wait and then find it again
      setTimeout(() => {
        const laterFind = notebookTools.findCellByAnyId(newTrackingId);
        console.log('Found cell after delay:', laterFind ? 'Yes' : 'No');

        if (laterFind) {
          // Edit the cell to show persistence
          notebookTools.edit_cell({
            cell_id: newTrackingId,
            new_source:
              '# Persistence Test - UPDATED\n\nThis cell was successfully found by its tracking ID after a delay!',
            summary: 'Updated persistence test cell',
            is_tracking_id: true
          });

          console.log('Cell updated successfully through tracking ID');
        }
      }, 2000);
    }
  });

  // Add the tracking persistence test to the command palette
  palette.addItem({
    command: testTrackingPersistenceCommand,
    category: 'AI Tools'
  });
}

/**
 * Register the tracking report command
 */
function registerTrackingReportCommand(
  app: JupyterFrontEnd,
  palette: ICommandPalette
): void {
  const trackingReportCommand: string = 'sage-ai:tracking-id-report';

  app.commands.addCommand(trackingReportCommand, {
    label: 'Show Cell Tracking ID Report',
    execute: () => {
      const trackingIDUtility = AppStateService.getTrackingIDUtility();
      const report = trackingIDUtility.getTrackingIDReport();
      console.log('Cell Tracking ID Report:');
      console.table(report);
    }
  });

  // Add this command to the command palette
  palette.addItem({ command: trackingReportCommand, category: 'AI Tools' });
}

/**
 * Register the fix tracking IDs command
 */
function registerFixTrackingIDsCommand(
  app: JupyterFrontEnd,
  palette: ICommandPalette
): void {
  const fixTrackingIDsCommand: string = 'sage-ai:fix-tracking-ids';

  app.commands.addCommand(fixTrackingIDsCommand, {
    label: 'Fix Cell Tracking IDs',
    execute: () => {
      const trackingIDUtility = AppStateService.getTrackingIDUtility();
      const fixedCount = trackingIDUtility.fixTrackingIDs();
      console.log(`Fixed tracking IDs for ${fixedCount} cells`);
    }
  });

  // Add this command to the command palette
  palette.addItem({ command: fixTrackingIDsCommand, category: 'AI Tools' });
}

/**
 * Register the export error logs command
 */
function registerExportErrorLogsCommand(
  app: JupyterFrontEnd,
  palette: ICommandPalette
): void {
  const exportErrorLogsCommand: string = 'sage-ai:export-error-logs';

  app.commands.addCommand(exportErrorLogsCommand, {
    label: 'Export Error Logs to File',
    execute: async () => {
      try {
        // Get error logs from stateDB
        const errorLogs = await StateDBCachingService.getValue(
          STATE_DB_KEYS.ERROR_LOGS,
          ''
        );

        if (!errorLogs.trim()) {
          console.log('No error logs found to export');
          return;
        }

        // Get content manager to save the file
        const contentManager = AppStateService.getContentManager();

        // Save the error logs to error_dump.txt
        await contentManager.save('./error_dump.txt', {
          type: 'file',
          format: 'text',
          content: errorLogs
        });

        console.log('Error logs exported successfully to error_dump.txt');
      } catch (error) {
        console.error('Failed to export error logs:', error);
      }
    }
  });

  // Add this command to the command palette
  palette.addItem({ command: exportErrorLogsCommand, category: 'AI Tools' });
}

/**
 * Register the clear error logs command
 */
function registerClearErrorLogsCommand(
  app: JupyterFrontEnd,
  palette: ICommandPalette
): void {
  const clearErrorLogsCommand: string = 'sage-ai:clear-error-logs';

  app.commands.addCommand(clearErrorLogsCommand, {
    label: 'Clear Error Logs',
    execute: async () => {
      try {
        // Clear error logs from stateDB
        await StateDBCachingService.setValue(STATE_DB_KEYS.ERROR_LOGS, '');
        console.log('Error logs cleared successfully');
      } catch (error) {
        console.error('Failed to clear error logs:', error);
      }
    }
  });

  // Add this command to the command palette
  palette.addItem({ command: clearErrorLogsCommand, category: 'AI Tools' });
}
