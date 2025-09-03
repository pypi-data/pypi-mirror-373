/**
 * Main entry point for the sage-agent-internal extension
 */

// Export components
export * from './types';
export * from './Components/chatbox';
export * from './Notebook/NotebookDiffManager';

import 'bootstrap/dist/css/bootstrap.min.css';

// Import and re-export plugin
import { plugin } from './plugin';

export default plugin;
