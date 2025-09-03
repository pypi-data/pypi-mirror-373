import { Contents } from '@jupyterlab/services';
import { AppStateService } from '../AppState';

/**
 * Tools for interacting with the filesystem directly
 */
export class FilesystemTools {
  private dataDir: string = 'data';

  constructor() {
    // No longer need to pass contentManager as parameter
  }

  /**
   * List datasets in the data directory
   * @param args Arguments (unused for list_datasets but needed for consistency)
   * @returns JSON string with list of files and their metadata
   */
  async list_datasets(args?: any): Promise<string> {
    try {
      // Ensure data directory exists
      await this.ensureDataDirectory();

      // List contents of the data directory
      const contents = await AppStateService.getContentManager().get(
        this.dataDir
      );

      if (contents.type !== 'directory') {
        throw new Error('Data path is not a directory');
      }

      const files = contents.content
        .filter((item: Contents.IModel) => item.type === 'file')
        .map((item: Contents.IModel) => ({
          name: item.name,
          path: item.path,
          size: item.size || 0,
          modified: item.last_modified
            ? new Date(item.last_modified).getTime() / 1000
            : 0
        }));

      return JSON.stringify(files);
    } catch (error) {
      console.error('Error listing datasets:', error);

      return JSON.stringify({
        error: `Failed to list datasets: ${error instanceof Error ? error.message : String(error)}`
      });
    }
  }

  /**
   * Read a dataset file
   * @param args Configuration options
   * @param args.filepath Path to the file to read
   * @param args.start Starting line number (0-indexed)
   * @param args.end Ending line number (0-indexed)
   * @returns JSON string with file contents or error
   */
  async read_dataset(args: {
    filepath: string;
    start?: number;
    end?: number;
  }): Promise<string> {
    try {
      const { filepath, start = 0, end = 10 } = args;

      // Ensure filepath is within data directory
      const safePath = this.getSafeFilePath(filepath);

      // Read the file
      const fileModel = await AppStateService.getContentManager().get(safePath);

      if (fileModel.type !== 'file') {
        throw new Error('Path is not a file');
      }

      const content = fileModel.content as string;
      const lines = content.split('\n');

      // Validate line range
      const safeStart = Math.max(0, start);
      const safeEnd = Math.min(safeStart + 10, Math.min(end, lines.length));

      const selectedLines = lines.slice(safeStart, safeEnd);

      return JSON.stringify({
        content: selectedLines,
        start: safeStart,
        end: safeEnd,
        path: safePath,
        total_lines: lines.length
      });
    } catch (error) {
      console.error('Error reading dataset:', error);

      return JSON.stringify({
        error: `Failed to read dataset: ${error instanceof Error ? error.message : String(error)}`
      });
    }
  }

  /**
   * Delete a dataset file
   * @param args Configuration options
   * @param args.filepath Path to the file to delete
   * @returns JSON string with success or error message
   */
  async delete_dataset(args: { filepath: string }): Promise<string> {
    try {
      const { filepath } = args;

      // Ensure filepath is within data directory
      const safePath = this.getSafeFilePath(filepath);

      // Delete the file
      await AppStateService.getContentManager().delete(safePath);

      return JSON.stringify({
        success: true,
        path: safePath,
        message: 'File deleted successfully'
      });
    } catch (error) {
      console.error('Error deleting dataset:', error);

      return JSON.stringify({
        error: `Failed to delete dataset: ${error instanceof Error ? error.message : String(error)}`
      });
    }
  }

  /**
   * Upload/save a dataset file
   * @param args Configuration options
   * @param args.filepath Path where to save the file
   * @param args.content Content to save
   * @returns JSON string with success or error message
   */
  async save_dataset(args: {
    filepath: string;
    content: string;
  }): Promise<string> {
    try {
      const { filepath, content } = args;

      // Ensure filepath is within data directory
      const safePath = this.getSafeFilePath(filepath);

      // Save the file
      await AppStateService.getContentManager().save(safePath, {
        type: 'file',
        format: 'text',
        content: content
      });

      return JSON.stringify({
        success: true,
        path: safePath,
        message: 'File saved successfully'
      });
    } catch (error) {
      console.error('Error saving dataset:', error);

      return JSON.stringify({
        error: `Failed to save dataset: ${error instanceof Error ? error.message : String(error)}`
      });
    }
  }

  /**
   * Ensure the data directory exists
   * @private
   */
  private async ensureDataDirectory(): Promise<void> {
    try {
      await AppStateService.getContentManager().get(this.dataDir);
    } catch (error) {
      // Directory doesn't exist, create it
      console.log(`Creating data directory: ${this.dataDir}`);
      await AppStateService.getContentManager()
        .newUntitled({
          type: 'directory',
          path: ''
        })
        .then(model => {
          return AppStateService.getContentManager().rename(
            model.path,
            this.dataDir
          );
        });
    }
  }

  /**
   * Ensure the file path is safe and within the data directory
   * @param filepath The file path to validate
   * @returns Safe file path
   * @private
   */
  private getSafeFilePath(filepath: string): string {
    // Remove any path traversal attempts
    const cleanPath = filepath.replace(/\.\./g, '').replace(/^\/+/, '');

    // If the path already starts with data directory, use it as is
    if (cleanPath.startsWith(this.dataDir + '/')) {
      return cleanPath;
    }

    // Otherwise, prepend the data directory
    return `${this.dataDir}/${cleanPath}`;
  }
}
