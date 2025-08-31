import { AppStateService } from '../AppState';
import { extractNotebookVariables, filterKernelVariablesByNotebook } from './VariableExtractor';

/**
 * Interface for kernel variable information
 */
export interface KernelVariableInfo {
  type: string;
  value?: any;
  size?: number;
  shape?: number[];
  columns?: string[];
  dtypes?: Record<string, string>;
  dtype?: string;
  first_rows?: any;
  preview?: any;
  truncated?: boolean;
  multi_level_columns?: boolean;
  column_levels?: number;
  length?: number;
  repr?: string;
  module?: string;
  error?: string;
}

/**
 * Result of kernel variables extraction
 */
export interface KernelVariablesResult {
  [variableName: string]: KernelVariableInfo;
}

/**
 * Utility functions for extracting and processing kernel variables
 */
export class KernelPreviewUtils {
  /**
   * Gets detailed information about all variables in the current kernel
   * @returns Promise resolving to kernel variables information, or null if no kernel
   */
  static async getKernelVariables(): Promise<KernelVariablesResult | null> {
    try {
      const toolService = AppStateService.getToolService();
      const kernel = toolService?.getCurrentNotebook()?.kernel;

      console.log('[KernelPreviewUtils] Getting kernel variables...');

      if (!kernel) {
        console.warn('[KernelPreviewUtils] No kernel available');
        return null;
      }

      const cells = AppStateService.getState().notebookTools?.read_cells();
      
      // Extract variables from notebook cells
      const notebookVariables = extractNotebookVariables(
        cells?.cells || []
      );
      
      console.log('[KernelPreviewUtils] Found notebook variables:', Array.from(notebookVariables));

      return new Promise<KernelVariablesResult | null>(resolve => {
        // Python code to get a comprehensive preview of the kernel state
        const code = `
import json
import sys
import math
from types import ModuleType, FunctionType, BuiltinFunctionType, BuiltinMethodType

# Try to import common libraries but don't fail if they're not available
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

def is_serializable(obj):
    """Check if an object can be JSON serialized"""
    try:
        json.dumps(obj)
        return True
    except (TypeError, ValueError, OverflowError):
        return False

def safe_json_value(obj):
    """Convert an object to a JSON-safe value, handling NaN, inf, etc."""
    import math
    
    if obj is None:
        return None
    elif isinstance(obj, float):
        if math.isnan(obj):
            return None  # Convert NaN to null
        elif math.isinf(obj):
            return "Infinity" if obj > 0 else "-Infinity"
        else:
            return obj
    elif isinstance(obj, (int, str, bool)):
        return obj
    elif isinstance(obj, (list, tuple)):
        return [safe_json_value(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: safe_json_value(v) for k, v in obj.items()}
    else:
        return str(obj)

def get_preview_info(obj, max_items=5):
    """Get preview information for an object"""
    try:
        obj_type = type(obj).__name__
        
        # Handle basic types
        if obj_type in ['int', 'float', 'str', 'bool', 'NoneType']:
            value = safe_json_value(obj)
            # Truncate very long strings
            if obj_type == 'str' and len(str(obj)) > 200:
                value = str(obj)[:200] + "..."
            return {"type": obj_type, "value": value, "size": len(str(obj)) if obj_type == 'str' else None}
        
        # Handle collections
        elif obj_type in ['list', 'tuple']:
            size = len(obj)
            # Get preview of first few items, ensuring they're serializable
            preview_items = []
            for i, item in enumerate(obj[:max_items]):
                try:
                    safe_item = safe_json_value(item)
                    if safe_item is not None or item is None:
                        preview_items.append(safe_item)
                    else:
                        preview_items.append(f"<{type(item).__name__} object>")
                except Exception:
                    preview_items.append("<unreadable object>")
            return {"type": obj_type, "size": size, "preview": preview_items, "truncated": size > max_items}
        
        elif obj_type == 'dict':
            size = len(obj)
            # Get preview of first few items, ensuring keys and values are serializable
            preview_dict = {}
            for i, (key, value) in enumerate(list(obj.items())[:max_items]):
                try:
                    # Convert key to string if not serializable
                    safe_key = str(key) if not is_serializable(key) else key
                    # Convert value using safe_json_value
                    safe_value = safe_json_value(value)
                    preview_dict[safe_key] = safe_value
                except Exception:
                    preview_dict[str(key)] = "<unreadable object>"
            return {"type": obj_type, "size": size, "preview": preview_dict, "truncated": size > max_items}
        
        elif obj_type == 'set':
            size = len(obj)
            # Convert set items to list, ensuring they're serializable
            preview_items = []
            for i, item in enumerate(list(obj)[:max_items]):
                try:
                    safe_item = safe_json_value(item)
                    if safe_item is not None or item is None:
                        preview_items.append(safe_item)
                    else:
                        preview_items.append(f"<{type(item).__name__} object>")
                except Exception:
                    preview_items.append("<unreadable object>")
            return {"type": obj_type, "size": size, "preview": preview_items, "truncated": size > max_items}
        
        # Handle special objects with class and module info
        elif hasattr(obj, '__class__') and hasattr(obj.__class__, '__module__'):
            # For pandas DataFrames
            if obj_type == 'DataFrame' and HAS_PANDAS:
                try:
                    result = {
                        "type": obj_type, 
                        "shape": list(obj.shape),  # Convert to list for JSON serialization
                        "columns": [str(col) for col in list(obj.columns)[:max_items]], 
                        "dtypes": {str(k): str(v) for k, v in dict(list(obj.dtypes.items())[:max_items]).items()}
                    }
                    
                    # Handle multi-level columns (like from yfinance)
                    if hasattr(obj.columns, 'nlevels') and obj.columns.nlevels > 1:
                        result["multi_level_columns"] = True
                        result["column_levels"] = obj.columns.nlevels
                        # Get a sample of the multi-level column structure
                        result["columns"] = [str(col) for col in obj.columns[:max_items]]
                    
                    # Get first 2 rows as preview
                    try:
                        first_rows = obj.head(2).to_dict('records')
                        # Ensure all values in rows are serializable and handle NaN
                        safe_rows = []
                        for row in first_rows:
                            safe_row = {}
                            for k, v in row.items():
                                try:
                                    safe_row[str(k)] = safe_json_value(v)
                                except Exception:
                                    safe_row[str(k)] = "<unreadable value>"
                            safe_rows.append(safe_row)
                        result["first_rows"] = safe_rows
                    except Exception as e:
                        # If to_dict fails, try a simpler approach
                        try:
                            result["first_rows"] = str(obj.head(2))[:500]
                        except Exception:
                            result["first_rows"] = "Unable to preview rows"
                    
                    return result
                except Exception as e:
                    return {"type": obj_type, "shape": list(getattr(obj, 'shape', []))}
            
            # For numpy arrays
            elif obj_type == 'ndarray' and HAS_NUMPY:
                try:
                    return {
                        "type": obj_type, 
                        "shape": list(obj.shape), 
                        "dtype": str(obj.dtype),
                        "size": int(obj.size)
                    }
                except Exception:
                    return {"type": obj_type, "shape": "unknown"}
            
            # For other objects with classes, try to get useful info
            else:
                try:
                    info = {"type": obj_type}
                    
                    # Try to get module info
                    if hasattr(obj.__class__, '__module__'):
                        info["module"] = str(obj.__class__.__module__)
                    
                    # Try to get length if available
                    if hasattr(obj, '__len__'):
                        try:
                            info["length"] = len(obj)
                        except Exception:
                            pass
                    
                    # Try to get a brief string representation
                    try:
                        repr_str = repr(obj)[:100]
                        if len(repr_str) < len(repr(obj)):
                            repr_str += "..."
                        info["repr"] = repr_str
                    except Exception:
                        info["repr"] = f"<{obj_type} object>"
                    
                    return info
                except Exception:
                    return {"type": obj_type, "module": "unknown"}
        
        # Fallback for other types
        else:
            try:
                return {"type": obj_type, "repr": str(obj)[:100]}
            except Exception:
                return {"type": obj_type, "repr": f"<{obj_type} object>"}
                
    except Exception as e:
        return {"type": "unknown", "error": str(e)[:100]}

# Main execution
try:
    # Create a snapshot of globals to avoid "dictionary changed size during iteration"
    globals_dict = globals()
    globals_snapshot = dict(globals_dict)
    
    # Get all variables from the snapshot, excluding private ones and modules
    kernel_preview = {}
    
    # Comprehensive list of names to exclude
    excluded_names = {
        'In', 'Out', 'get_ipython', 'exit', 'quit', 'json', 'sys', 
        'get_preview_info', 'globals_snapshot', 'kernel_preview',
        'HAS_NUMPY', 'HAS_PANDAS', 'excluded_names', 'tables', 'local_vars', 
        'constraints', 'fk', 'globals_dict', 'is_serializable', 'data',
        # Additional built-in names that might appear
        '__name__', '__doc__', '__package__', '__loader__', '__spec__',
        '__builtin__', '__builtins__', '_', '__', '___'
    }
    
    # Add numpy and pandas to excluded if they exist
    if HAS_NUMPY:
        excluded_names.add('np')
    if HAS_PANDAS:
        excluded_names.add('pd')
    
    # Process each variable in the globals snapshot
    for name, obj in globals_snapshot.items():
        try:
            # Skip private variables, built-ins, modules, and functions
            if (name.startswith('_') or 
                isinstance(obj, (ModuleType, FunctionType, BuiltinFunctionType, BuiltinMethodType)) or 
                name in excluded_names or
                callable(obj)):  # Skip any callable objects
                continue
            
            # Get type information
            obj_type = type(obj).__name__
            
            # Include various types but be more selective
            if obj_type in ['int', 'float', 'complex', 'str', 'bool', 'list', 'tuple', 'dict', 'set']:
                # For strings, only include if they're not too long or seem like user data
                if obj_type == 'str':
                    if len(obj) > 1000:  # Skip very long strings
                        continue
                kernel_preview[name] = get_preview_info(obj)
            elif obj_type == 'ndarray' and HAS_NUMPY:
                kernel_preview[name] = get_preview_info(obj)
            elif obj_type == 'DataFrame' and HAS_PANDAS:
                kernel_preview[name] = get_preview_info(obj)
            elif obj_type == 'Series' and HAS_PANDAS:
                kernel_preview[name] = get_preview_info(obj)
            # Skip everything else to avoid clutter
            
        except Exception as e:
            # If we can't process this variable, skip it silently
            continue
    
    # Output the result
    if kernel_preview:
        print(json.dumps(kernel_preview, indent=2, default=str))
    else:
        print(json.dumps({"message": "No user-defined variables found in kernel"}, indent=2))
    
except Exception as e:
    # If everything fails, output a detailed error message
    error_info = {
        "error": f"Kernel preview failed: {str(e)}", 
        "error_type": type(e).__name__,
        "globals_keys_count": len(globals().keys()) if 'globals' in dir() else 0
    }
    print(json.dumps(error_info, indent=2, default=str))
        `;

        let buffer = '';

        // Execute the Python code
        const future = kernel.requestExecute({
          code,
          silent: true
        });

        // Capture output
        future.onIOPub = (msg: any) => {
          const msgType = msg.header.msg_type;
          if (msgType === 'stream' && msg.content.name === 'stdout') {
            buffer += msg.content.text;
          } else if (msgType === 'error') {
            console.error(
              '[KernelPreviewUtils] Kernel execution error:',
              msg.content
            );
          }
        };

        // When execution is complete
        future.done
          .then(() => {
            try {
              if (buffer.trim()) {
                const kernelData = JSON.parse(buffer.trim());
                
                // Filter kernel variables to only include those that exist in the notebook
                const filteredKernelData = filterKernelVariablesByNotebook(
                  kernelData,
                  notebookVariables
                );

                console.log('[KernelPreviewUtils] Filtered kernel variables:', Object.keys(filteredKernelData));
                resolve(filteredKernelData);
              } else {
                resolve(null);
              }
            } catch (error) {
              console.error(
                '[KernelPreviewUtils] Error parsing kernel variables:',
                error
              );
              console.error('[KernelPreviewUtils] Raw buffer:', buffer);
              resolve(null);
            }
          })
          .catch((error: any) => {
            console.error(
              '[KernelPreviewUtils] Kernel execution error:',
              error
            );
            resolve(null);
          });
      });
    } catch (error) {
      console.error(
        '[KernelPreviewUtils] Error in getKernelVariables:',
        error
      );
      return null;
    }
  }

  /**
   * Gets a formatted string preview of all variables in the current kernel
   * @returns Promise resolving to formatted preview string, or null if no kernel
   */
  static async getKernelPreview(): Promise<string | null> {
    const kernelVariables = await this.getKernelVariables();
    
    if (!kernelVariables) {
      return null;
    }

    // Format the preview nicely with proper newlines
    let preview = '=== KERNEL VARIABLES AND OBJECTS ===\n\n';

    const entries = Object.entries(kernelVariables);
    if (entries.length === 0) {
      preview += 'No user-defined variables from notebook found in kernel.\n';
      return preview;
    }

    entries.forEach(([name, info]: [string, KernelVariableInfo]) => {
      // Add spacing before each variable
      preview += `\n• Variable: ${name}\n`;
      preview += `  Type: ${info.type || 'unknown'}\n`;

      if (info.size !== undefined && info.size !== null) {
        preview += `  Size: ${info.size}\n`;
      }

      if (info.shape) {
        preview += `  Shape: ${JSON.stringify(info.shape)}\n`;
      }

      if (info.columns) {
        if (info.multi_level_columns) {
          preview += `  Multi-level Columns (${info.column_levels} levels): ${JSON.stringify(info.columns)}\n`;
        } else {
          preview += `  Columns: ${JSON.stringify(info.columns)}\n`;
        }
      }

      if (info.dtype) {
        preview += `  Data Type: ${info.dtype}\n`;
      }

      if (info.dtypes) {
        preview += `  Column Types: ${info.dtypes}\n`;
      }

      if (info.first_rows) {
        preview += `  First 2 Rows:\n`;
        if (typeof info.first_rows === 'string') {
          preview += `    ${info.first_rows}\n`;
        } else {
          preview += `    ${JSON.stringify(info.first_rows, null, 4)}\n`;
        }
      }

      if (info.value !== undefined) {
        preview += `  Value: ${JSON.stringify(info.value)}\n`;
      } else if (info.preview !== undefined) {
        preview += `  Preview: ${JSON.stringify(info.preview)}\n`;
        if (info.truncated) {
          preview += `  [truncated - showing first ${info.preview.length || 5} items]\n`;
        }
      } else if (info.repr) {
        preview += `  Repr: ${info.repr}\n`;
      }

      if (info.module) {
        preview += `  Module: ${info.module}\n`;
      }

      if (info.error) {
        preview += `  Error: ${info.error}\n`;
      }

      // Add spacing after each variable
      preview += '\n';
    });

    preview += '=== END KERNEL PREVIEW ===';
    return preview;
  }

  /**
   * Gets a limited kernel preview for use in AnthropicMessageCreator
   * Limited to last 10 cells context and 10,000 characters maximum
   * @returns Promise resolving to formatted preview string, or null if no kernel
   */
  static async getLimitedKernelPreview(): Promise<string | null> {
    try {
      const toolService = AppStateService.getToolService();
      const kernel = toolService?.getCurrentNotebook()?.kernel;

      console.log('[KernelPreviewUtils] Getting limited kernel variables (last 10 cells)...');

      if (!kernel) {
        console.warn('[KernelPreviewUtils] No kernel available');
        return null;
      }

      const cells = AppStateService.getState().notebookTools?.read_cells();
      
      // Extract variables from notebook cells - limit to last 10 cells only if content > 10k chars
      const notebookVariables = extractNotebookVariables(
        cells?.cells || [], 
        10 // Only consider last 10 cells if total content > 10,000 characters
      );
      
      console.log('[KernelPreviewUtils] Found notebook variables (conditional last 10 cells):', Array.from(notebookVariables));

      const kernelVariables = await new Promise<KernelVariablesResult | null>(resolve => {
        // Use the same Python code to get kernel variables
        const code = `
import json
import sys
import math
from types import ModuleType, FunctionType, BuiltinFunctionType, BuiltinMethodType

# Try to import common libraries but don't fail if they're not available
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

def is_serializable(obj):
    """Check if an object can be JSON serialized"""
    try:
        json.dumps(obj)
        return True
    except (TypeError, ValueError, OverflowError):
        return False

def safe_json_value(obj):
    """Convert an object to a JSON-safe value, handling NaN, inf, etc."""
    import math
    
    if obj is None:
        return None
    elif isinstance(obj, float):
        if math.isnan(obj):
            return None  # Convert NaN to null
        elif math.isinf(obj):
            return "Infinity" if obj > 0 else "-Infinity"
        else:
            return obj
    elif isinstance(obj, (int, str, bool)):
        return obj
    elif isinstance(obj, (list, tuple)):
        return [safe_json_value(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: safe_json_value(v) for k, v in obj.items()}
    else:
        return str(obj)

def get_preview_info(obj, max_items=3):  # Reduced max_items for limited version
    """Get preview information for an object"""
    try:
        obj_type = type(obj).__name__
        
        # Handle basic types
        if obj_type in ['int', 'float', 'str', 'bool', 'NoneType']:
            value = safe_json_value(obj)
            # Truncate very long strings more aggressively
            if obj_type == 'str' and len(str(obj)) > 100:  # Reduced from 200
                value = str(obj)[:100] + "..."
            return {"type": obj_type, "value": value, "size": len(str(obj)) if obj_type == 'str' else None}
        
        # Handle collections - more aggressive truncation
        elif obj_type in ['list', 'tuple']:
            size = len(obj)
            preview_items = []
            for i, item in enumerate(obj[:max_items]):
                try:
                    safe_item = safe_json_value(item)
                    if safe_item is not None or item is None:
                        preview_items.append(safe_item)
                    else:
                        preview_items.append(f"<{type(item).__name__} object>")
                except Exception:
                    preview_items.append("<unreadable object>")
            return {"type": obj_type, "size": size, "preview": preview_items, "truncated": size > max_items}
        
        elif obj_type == 'dict':
            size = len(obj)
            preview_dict = {}
            for i, (key, value) in enumerate(list(obj.items())[:max_items]):
                try:
                    safe_key = str(key) if not is_serializable(key) else key
                    safe_value = safe_json_value(value)
                    preview_dict[safe_key] = safe_value
                except Exception:
                    preview_dict[str(key)] = "<unreadable object>"
            return {"type": obj_type, "size": size, "preview": preview_dict, "truncated": size > max_items}
        
        elif obj_type == 'set':
            size = len(obj)
            preview_items = []
            for i, item in enumerate(list(obj)[:max_items]):
                try:
                    safe_item = safe_json_value(item)
                    if safe_item is not None or item is None:
                        preview_items.append(safe_item)
                    else:
                        preview_items.append(f"<{type(item).__name__} object>")
                except Exception:
                    preview_items.append("<unreadable object>")
            return {"type": obj_type, "size": size, "preview": preview_items, "truncated": size > max_items}
        
        # Handle DataFrames with more truncation
        elif obj_type == 'DataFrame' and HAS_PANDAS:
            try:
                result = {
                    "type": obj_type, 
                    "shape": list(obj.shape),
                    "columns": [str(col) for col in list(obj.columns)[:max_items]], 
                    "dtypes": {str(k): str(v) for k, v in dict(list(obj.dtypes.items())[:max_items]).items()}
                }
                
                if hasattr(obj.columns, 'nlevels') and obj.columns.nlevels > 1:
                    result["multi_level_columns"] = True
                    result["column_levels"] = obj.columns.nlevels
                    result["columns"] = [str(col) for col in obj.columns[:max_items]]
                
                # Only get first row for limited version
                try:
                    first_rows = obj.head(1).to_dict('records')
                    safe_rows = []
                    for row in first_rows:
                        safe_row = {}
                        for k, v in row.items():
                            try:
                                safe_row[str(k)] = safe_json_value(v)
                            except Exception:
                                safe_row[str(k)] = "<unreadable value>"
                        safe_rows.append(safe_row)
                    result["first_rows"] = safe_rows
                except Exception:
                    result["first_rows"] = "Unable to preview rows"
                
                return result
            except Exception:
                return {"type": obj_type, "shape": list(getattr(obj, 'shape', []))}
        
        # For numpy arrays
        elif obj_type == 'ndarray' and HAS_NUMPY:
            try:
                return {
                    "type": obj_type, 
                    "shape": list(obj.shape), 
                    "dtype": str(obj.dtype),
                    "size": int(obj.size)
                }
            except Exception:
                return {"type": obj_type, "shape": "unknown"}
        
        # For other objects - more minimal info
        else:
            try:
                info = {"type": obj_type}
                
                if hasattr(obj.__class__, '__module__'):
                    info["module"] = str(obj.__class__.__module__)
                
                if hasattr(obj, '__len__'):
                    try:
                        info["length"] = len(obj)
                    except Exception:
                        pass
                
                # Shorter repr for limited version
                try:
                    repr_str = repr(obj)[:50]  # Reduced from 100
                    if len(repr_str) < len(repr(obj)):
                        repr_str += "..."
                    info["repr"] = repr_str
                except Exception:
                    info["repr"] = f"<{obj_type} object>"
                
                return info
            except Exception:
                return {"type": obj_type, "module": "unknown"}
                
    except Exception as e:
        return {"type": "unknown", "error": str(e)[:50]}  # Reduced error message length

# Main execution - same logic but with reduced output
try:
    globals_dict = globals()
    globals_snapshot = dict(globals_dict)
    
    kernel_preview = {}
    
    excluded_names = {
        'In', 'Out', 'get_ipython', 'exit', 'quit', 'json', 'sys', 
        'get_preview_info', 'globals_snapshot', 'kernel_preview',
        'HAS_NUMPY', 'HAS_PANDAS', 'excluded_names', 'tables', 'local_vars', 
        'constraints', 'fk', 'globals_dict', 'is_serializable', 'data',
        '__name__', '__doc__', '__package__', '__loader__', '__spec__',
        '__builtin__', '__builtins__', '_', '__', '___'
    }
    
    if HAS_NUMPY:
        excluded_names.add('np')
    if HAS_PANDAS:
        excluded_names.add('pd')
    
    for name, obj in globals_snapshot.items():
        try:
            if (name.startswith('_') or 
                isinstance(obj, (ModuleType, FunctionType, BuiltinFunctionType, BuiltinMethodType)) or 
                name in excluded_names or
                callable(obj)):
                continue
            
            obj_type = type(obj).__name__
            
            if obj_type in ['int', 'float', 'complex', 'str', 'bool', 'list', 'tuple', 'dict', 'set']:
                if obj_type == 'str':
                    if len(obj) > 500:  # More aggressive string filtering for limited version
                        continue
                kernel_preview[name] = get_preview_info(obj)
            elif obj_type == 'ndarray' and HAS_NUMPY:
                kernel_preview[name] = get_preview_info(obj)
            elif obj_type == 'DataFrame' and HAS_PANDAS:
                kernel_preview[name] = get_preview_info(obj)
            elif obj_type == 'Series' and HAS_PANDAS:
                kernel_preview[name] = get_preview_info(obj)
            
        except Exception:
            continue
    
    if kernel_preview:
        print(json.dumps(kernel_preview, indent=2, default=str))
    else:
        print(json.dumps({"message": "No user-defined variables found in kernel"}, indent=2))
    
except Exception as e:
    error_info = {
        "error": f"Kernel preview failed: {str(e)}", 
        "error_type": type(e).__name__,
        "globals_keys_count": len(globals().keys()) if 'globals' in dir() else 0
    }
    print(json.dumps(error_info, indent=2, default=str))
        `;

        let buffer = '';

        const future = kernel.requestExecute({
          code,
          silent: true
        });

        future.onIOPub = (msg: any) => {
          const msgType = msg.header.msg_type;
          if (msgType === 'stream' && msg.content.name === 'stdout') {
            buffer += msg.content.text;
          } else if (msgType === 'error') {
            console.error(
              '[KernelPreviewUtils] Kernel execution error:',
              msg.content
            );
          }
        };

        future.done
          .then(() => {
            try {
              if (buffer.trim()) {
                const kernelData = JSON.parse(buffer.trim());
                
                const filteredKernelData = filterKernelVariablesByNotebook(
                  kernelData,
                  notebookVariables
                );

                console.log('[KernelPreviewUtils] Limited filtered kernel variables:', Object.keys(filteredKernelData));
                resolve(filteredKernelData);
              } else {
                resolve(null);
              }
            } catch (error) {
              console.error(
                '[KernelPreviewUtils] Error parsing limited kernel variables:',
                error
              );
              resolve(null);
            }
          })
          .catch((error: any) => {
            console.error(
              '[KernelPreviewUtils] Limited kernel execution error:',
              error
            );
            resolve(null);
          });
      });

      if (!kernelVariables) {
        return null;
      }

      // Format the preview with character limit
      let preview = '=== KERNEL VARIABLES AND OBJECTS ===\n\n';
      const maxCharacters = 10000;

      const entries = Object.entries(kernelVariables);
      if (entries.length === 0) {
        preview += 'No user-defined variables from notebook found in kernel.\n';
        return preview;
      }

      for (const [name, info] of entries) {
        const variableSection = this.formatVariableInfo(name, info);
        
        // Check if adding this variable would exceed the character limit
        if (preview.length + variableSection.length > maxCharacters - 100) { // Leave some room for ending
          preview += `\n[Output truncated - showing first ${preview.split('• Variable:').length - 1} variables out of ${entries.length} total]\n`;
          break;
        }
        
        preview += variableSection;
      }

      preview += '=== END KERNEL PREVIEW ===';
      
      // Final check - if still too long, truncate more aggressively
      if (preview.length > maxCharacters) {
        preview = preview.substring(0, maxCharacters - 50) + '\n\n[Output truncated at 10,000 characters]\n=== END KERNEL PREVIEW ===';
      }
      
      return preview;
    } catch (error) {
      console.error('[KernelPreviewUtils] Error in getLimitedKernelPreview:', error);
      return null;
    }
  }

  /**
   * Helper method to format variable information
   */
  private static formatVariableInfo(name: string, info: KernelVariableInfo): string {
    let section = `\n• Variable: ${name}\n`;
    section += `  Type: ${info.type || 'unknown'}\n`;

    if (info.size !== undefined && info.size !== null) {
      section += `  Size: ${info.size}\n`;
    }

    if (info.shape) {
      section += `  Shape: ${JSON.stringify(info.shape)}\n`;
    }

    if (info.columns) {
      if (info.multi_level_columns) {
        section += `  Multi-level Columns (${info.column_levels} levels): ${JSON.stringify(info.columns)}\n`;
      } else {
        section += `  Columns: ${JSON.stringify(info.columns)}\n`;
      }
    }

    if (info.dtype) {
      section += `  Data Type: ${info.dtype}\n`;
    }

    if (info.dtypes) {
      section += `  Column Types: ${JSON.stringify(info.dtypes).substring(0, 200)}${JSON.stringify(info.dtypes).length > 200 ? '...' : ''}\n`;
    }

    if (info.first_rows) {
      section += `  First Row:\n`;
      if (typeof info.first_rows === 'string') {
        section += `    ${info.first_rows.substring(0, 300)}${info.first_rows.length > 300 ? '...' : ''}\n`;
      } else {
        const rowStr = JSON.stringify(info.first_rows, null, 2);
        section += `    ${rowStr.substring(0, 300)}${rowStr.length > 300 ? '...' : ''}\n`;
      }
    }

    if (info.value !== undefined) {
      const valueStr = JSON.stringify(info.value);
      section += `  Value: ${valueStr.substring(0, 200)}${valueStr.length > 200 ? '...' : ''}\n`;
    } else if (info.preview !== undefined) {
      const previewStr = JSON.stringify(info.preview);
      section += `  Preview: ${previewStr.substring(0, 200)}${previewStr.length > 200 ? '...' : ''}\n`;
      if (info.truncated) {
        section += `  [truncated - showing first ${Array.isArray(info.preview) ? info.preview.length : 3} items]\n`;
      }
    } else if (info.repr) {
      section += `  Repr: ${info.repr}\n`;
    }

    if (info.module && info.module !== 'builtins') {
      section += `  Module: ${info.module}\n`;
    }

    if (info.error) {
      section += `  Error: ${info.error}\n`;
    }

    section += '\n';
    return section;
  }
}
