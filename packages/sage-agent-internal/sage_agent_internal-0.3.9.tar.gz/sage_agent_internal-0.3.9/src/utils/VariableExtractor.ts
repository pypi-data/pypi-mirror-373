/**
 * Extract variables from Python code using regex patterns
 * This is a simpler approach that doesn't require full AST parsing
 */
function extractVariablesFromCode(code: string): Set<string> {
  const variables = new Set<string>();
  
  // Split code into lines for processing
  const lines = code.split('\n');
  
  for (const line of lines) {
    const trimmedLine = line.trim();
    
    // Skip comments and empty lines
    if (!trimmedLine || trimmedLine.startsWith('#')) continue;
    
    // Assignment patterns
    const assignmentPatterns = [
      // Simple assignment: var = value
      /^([a-zA-Z_][a-zA-Z0-9_]*)\s*=/,
      // Multiple assignment: a, b = values
      /^([a-zA-Z_][a-zA-Z0-9_]*(?:\s*,\s*[a-zA-Z_][a-zA-Z0-9_]*)*)\s*=/,
      // For loop variables: for var in iterable
      /for\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+in\s/,
      // Function definitions: def func_name(
      /def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(/,
      // Class definitions: class ClassName
      /class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[:\(]/,
      // Import statements: import module as alias
      /import\s+[\w.]+\s+as\s+([a-zA-Z_][a-zA-Z0-9_]*)/,
      // From import: from module import name as alias
      /from\s+[\w.]+\s+import\s+[\w\s,]*\s+as\s+([a-zA-Z_][a-zA-Z0-9_]*)/,
      // From import: from module import name
      /from\s+[\w.]+\s+import\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\s*,\s*[a-zA-Z_][a-zA-Z0-9_]*)*)/,
      // Simple import: import module
      /^import\s+([a-zA-Z_][a-zA-Z0-9_]*)/
    ];
    
    for (const pattern of assignmentPatterns) {
      const match = trimmedLine.match(pattern);
      if (match) {
        const varNames = match[1];
        // Handle multiple variables (comma-separated)
        const names = varNames.split(',').map(name => name.trim());
        names.forEach(name => {
          if (name && !isBuiltinOrKeyword(name)) {
            variables.add(name);
          }
        });
        break; // Found a match, move to next line
      }
    }
  }
  
  return variables;
}

/**
 * Check if a name is a Python built-in or keyword
 */
function isBuiltinOrKeyword(name: string): boolean {
  const pythonBuiltins = new Set([
    // Python keywords
    'False', 'None', 'True', '__peg_parser__', 'and', 'as', 'assert', 'async', 'await',
    'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except', 'finally',
    'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal',
    'not', 'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield',
    
    // Common built-in functions and variables
    'abs', 'all', 'any', 'ascii', 'bin', 'bool', 'bytearray', 'bytes', 'callable',
    'chr', 'classmethod', 'compile', 'complex', 'delattr', 'dict', 'dir', 'divmod',
    'enumerate', 'eval', 'exec', 'filter', 'float', 'format', 'frozenset',
    'getattr', 'globals', 'hasattr', 'hash', 'help', 'hex', 'id', 'input', 'int',
    'isinstance', 'issubclass', 'iter', 'len', 'list', 'locals', 'map', 'max',
    'memoryview', 'min', 'next', 'object', 'oct', 'open', 'ord', 'pow', 'print',
    'property', 'range', 'repr', 'reversed', 'round', 'set', 'setattr', 'slice',
    'sorted', 'staticmethod', 'str', 'sum', 'super', 'tuple', 'type', 'vars', 'zip',
    
    // IPython/Jupyter specific
    'get_ipython', 'In', 'Out', '_', '__', '___', 'exit', 'quit',
    
    // Common module names that might be confused with variables
    'sys', 'os', 'json', 'math', 'datetime', 'time', 'random', 're',
    'numpy', 'np', 'pandas', 'pd', 'matplotlib', 'plt', 'seaborn', 'sns'
  ]);

  return pythonBuiltins.has(name) || name.startsWith('_');
}

/**
 * Extract variables from Python source code using regex patterns
 */
export function extractPythonVariables(code: string): Set<string> {
  return extractVariablesFromCode(code);
}

/**
 * Extract all variables from notebook cells
 */
export function extractNotebookVariables(cells: Array<{ type: string; content: string }>, lastNCells?: number): Set<string> {
  const allVariables = new Set<string>();

  // If lastNCells is specified, check if we need to limit based on content size
  let cellsToProcess = cells;
  
  if (lastNCells) {
    // First, calculate the total character count of all cells
    const totalCharacters = cells.reduce((total, cell) => {
      return total + (cell.type === 'code' ? cell.content.length : 0);
    }, 0);
    
    // Only limit to last N cells if total content is greater than 10,000 characters
    if (totalCharacters > 10000) {
      cellsToProcess = cells.slice(-lastNCells);
      console.log(`[VariableExtractor] Total content length (${totalCharacters}) > 10,000 chars, limiting to last ${lastNCells} cells`);
    } else {
      console.log(`[VariableExtractor] Total content length (${totalCharacters}) <= 10,000 chars, processing all cells`);
    }
  }

  for (const cell of cellsToProcess) {
    if (cell.type === 'code' && cell.content.trim()) {
      const cellVariables = extractPythonVariables(cell.content);
      cellVariables.forEach(variable => allVariables.add(variable));
    }
  }

  return allVariables;
}

/**
 * Filter kernel variables to only include those that exist in the notebook
 */
export function filterKernelVariablesByNotebook(
  kernelVariables: Record<string, any>,
  notebookVariables: Set<string>
): Record<string, any> {
  const filteredVariables: Record<string, any> = {};

  for (const [varName, varInfo] of Object.entries(kernelVariables)) {
    if (notebookVariables.has(varName)) {
      filteredVariables[varName] = varInfo;
    }
  }

  return filteredVariables;
}
