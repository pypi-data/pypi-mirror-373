import { AppStateService } from '../AppState';

/**
 * Tools for interacting with database systems via Python kernel execution
 */
export class DatabaseTools {
  constructor() {
    // No initialization needed
  }

  /**
   * Creates a temporary kernel session for database operations
   * @returns Promise with kernel connection and cleanup function
   */
  private async createTemporaryKernel(): Promise<{
    kernel: any;
    cleanup: () => void;
  }> {
    try {
      console.log('[DatabaseTools] Creating temporary kernel session...');

      const serviceManager = AppStateService.getServiceManager();
      if (!serviceManager) {
        throw new Error('Service manager not available');
      }

      // Create a new session for this operation
      const sessionManager = serviceManager.sessions;
      const kernelspecManager = serviceManager.kernelspecs;

      // Get the default Python kernel spec
      await kernelspecManager.refreshSpecs();
      const specs = kernelspecManager.specs;

      // Find a Python kernel spec (prefer python3, fallback to python)
      let kernelName = 'python3';
      if (!specs?.kernelspecs[kernelName]) {
        kernelName = 'python';
        if (!specs?.kernelspecs[kernelName]) {
          // Use the default kernel if no python kernel is found
          kernelName = specs?.default || 'python3';
        }
      }

      console.log(`[DatabaseTools] Using kernel spec: ${kernelName}`);

      // Create a new session with a unique name
      const sessionId = `database-temp-${Date.now()}-${Math.random().toString(36).substring(7)}`;
      const session = await sessionManager.startNew({
        name: sessionId,
        path: `temp/${sessionId}`,
        type: 'file',
        kernel: {
          name: kernelName
        }
      });

      console.log(`[DatabaseTools] Created temporary session: ${session.id}`);

      // Wait for kernel to be ready
      if (session.kernel) {
        // Wait a moment for the kernel to initialize
        await new Promise(resolve => setTimeout(resolve, 2000));
      }

      console.log('[DatabaseTools] Temporary kernel is ready');

      // Set up the database URL in the temporary kernel if available
      const appState = AppStateService.getState();
      const databaseUrl = appState.settings.databaseUrl;

      if (databaseUrl) {
        console.log('[DatabaseTools] Setting DB_URL in temporary kernel');
        const setupCode = `
import os
os.environ['DB_URL'] = '${databaseUrl.replace(/'/g, "\\'")}'
print("[DatabaseTools] DB_URL environment variable set in temporary kernel")
        `;

        // Execute the setup code silently
        session.kernel?.requestExecute({ code: setupCode, silent: true });
      }

      // Return kernel and cleanup function
      return {
        kernel: session.kernel,
        cleanup: () => {
          console.log(
            `[DatabaseTools] Cleaning up temporary session: ${session.id}`
          );
          sessionManager.shutdown(session.id).catch(error => {
            console.warn(
              `[DatabaseTools] Error shutting down session ${session.id}:`,
              error
            );
          });
        }
      };
    } catch (error) {
      console.error('[DatabaseTools] Error creating temporary kernel:', error);
      throw error;
    }
  }

  /**
   * Get database metadata as a formatted text string by executing SQL in the kernel
   * @param dbUrl PostgreSQL connection string (optional, will use kernel environment if not provided)
   * @returns Promise<string> Formatted database metadata text
   */
  async getDatabaseMetadataAsText(dbUrl?: string): Promise<string> {
    try {
      console.log(
        '[DatabaseTools] Fetching database schema info via temporary kernel...'
      );

      // Create a temporary kernel for this operation
      const { kernel, cleanup } = await this.createTemporaryKernel();

      if (!kernel) {
        return 'Error: Failed to create temporary kernel for database query';
      }

      // Python code to get database schema information
      const pythonCode = `
import os
import json
import subprocess
import sys

# Function to install packages if they don't exist
def install_package(package_name):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"[DatabaseTools] Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[DatabaseTools] Failed to install {package_name}: {str(e)}")
        return False

# Check if required modules are available, install if missing
missing_packages = []
try:
    import sqlalchemy
except ImportError:
    print("[DatabaseTools] sqlalchemy not found, attempting to install...")
    if install_package("sqlalchemy"):
        try:
            import sqlalchemy
            print("[DatabaseTools] sqlalchemy successfully imported after installation")
        except ImportError as e:
            missing_packages.append(f"sqlalchemy: {str(e)}")
    else:
        missing_packages.append("sqlalchemy: installation failed")

try:
    import psycopg2
except ImportError:
    print("[DatabaseTools] psycopg2 not found, attempting to install psycopg2-binary...")
    if install_package("psycopg2-binary"):
        try:
            import psycopg2
            print("[DatabaseTools] psycopg2 successfully imported after installation")
        except ImportError as e:
            missing_packages.append(f"psycopg2: {str(e)}")
    else:
        missing_packages.append("psycopg2: installation failed")

# If any packages are still missing after installation attempts, exit with error
if missing_packages:
    print(json.dumps({"error": f"Required modules could not be installed: {', '.join(missing_packages)}"}))
    exit()

try:
    # Use provided dbUrl or get from environment
    db_url = ${dbUrl ? `'${dbUrl.replace(/'/g, "\\'")}'` : "os.environ.get('DB_URL')"}
    
    if not db_url:
        print(json.dumps({"error": "No database URL provided and DB_URL environment variable not set"}))
    else:
        from sqlalchemy import create_engine, text
        
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            # Get all tables from public and custom schemas (excluding system schemas)
            tables_query = """
                SELECT table_schema, table_name 
                FROM information_schema.tables 
                WHERE table_type = 'BASE TABLE' 
                AND table_schema NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                ORDER BY table_schema, table_name
                LIMIT 50;
            """
            
            tables_result = conn.execute(text(tables_query))
            tables = [dict(row._mapping) for row in tables_result]
            
            if not tables:
                print(json.dumps({"result": "Database connected successfully, but no tables found."}))
            else:
                # Start building markdown formatted output
                markdown_output = f"# Database Schema\\n\\nFound **{len(tables)}** table(s)\\n\\n"
                
                # Get detailed information for each table
                for table in tables:
                    table_schema = table['table_schema']
                    table_name = table['table_name']
                    full_table_name = f"{table_schema}.{table_name}"
                    
                    # Get columns
                    columns_query = """
                        SELECT 
                            column_name, 
                            data_type, 
                            is_nullable, 
                            column_default,
                            character_maximum_length,
                            numeric_precision,
                            numeric_scale
                        FROM information_schema.columns 
                        WHERE table_schema = :schema AND table_name = :table
                        ORDER BY ordinal_position
                        LIMIT 30;
                    """
                    
                    columns_result = conn.execute(text(columns_query), 
                                                {"schema": table_schema, "table": table_name})
                    columns = [dict(row._mapping) for row in columns_result]
                    
                    # Get primary keys
                    pk_query = """
                        SELECT kcu.column_name
                        FROM information_schema.table_constraints tc
                        JOIN information_schema.key_column_usage kcu 
                            ON tc.constraint_name = kcu.constraint_name
                        WHERE tc.constraint_type = 'PRIMARY KEY' 
                            AND tc.table_schema = :schema 
                            AND tc.table_name = :table
                        ORDER BY kcu.ordinal_position;
                    """
                    
                    pk_result = conn.execute(text(pk_query), 
                                           {"schema": table_schema, "table": table_name})
                    primary_keys = [row[0] for row in pk_result]
                    
                    # Get foreign keys
                    fk_query = """
                        SELECT 
                            kcu.column_name,
                            ccu.table_schema AS foreign_table_schema,
                            ccu.table_name AS foreign_table_name,
                            ccu.column_name AS foreign_column_name
                        FROM information_schema.table_constraints tc
                        JOIN information_schema.key_column_usage kcu 
                            ON tc.constraint_name = kcu.constraint_name
                        JOIN information_schema.constraint_column_usage ccu 
                            ON ccu.constraint_name = tc.constraint_name
                        WHERE tc.constraint_type = 'FOREIGN KEY' 
                            AND tc.table_schema = :schema 
                            AND tc.table_name = :table
                        ORDER BY kcu.ordinal_position;
                    """
                    
                    fk_result = conn.execute(text(fk_query), 
                                           {"schema": table_schema, "table": table_name})
                    foreign_keys = [dict(row._mapping) for row in fk_result]
                    
                    # Get indices
                    index_query = """
                        SELECT 
                            indexname,
                            indexdef
                        FROM pg_indexes
                        WHERE schemaname = :schema 
                            AND tablename = :table
                            AND indexname NOT LIKE '%_pkey'
                        ORDER BY indexname;
                    """
                    
                    index_result = conn.execute(text(index_query), 
                                              {"schema": table_schema, "table": table_name})
                    indices = [dict(row._mapping) for row in index_result]
                    
                    # Build table section
                    markdown_output += f"## {full_table_name}\\n\\n"
                    
                    # Columns section
                    markdown_output += f"### Columns ({len(columns)})\\n\\n"
                    for col in columns:
                        col_name = col['column_name']
                        data_type = col['data_type']
                        
                        # Format data type with precision/scale
                        if col['character_maximum_length']:
                            data_type += f"({col['character_maximum_length']})"
                        elif col['numeric_precision'] and col['numeric_scale'] is not None:
                            data_type += f"({col['numeric_precision']},{col['numeric_scale']})"
                        elif col['numeric_precision']:
                            data_type += f"({col['numeric_precision']})"
                        
                        # Add constraints
                        constraints = []
                        if col['is_nullable'] == 'NO':
                            constraints.append("NOT NULL")
                        if col['column_default']:
                            constraints.append(f"DEFAULT {col['column_default']}")
                        if col_name in primary_keys:
                            constraints.append("PRIMARY KEY")
                        
                        constraint_text = f" ({', '.join(constraints)})" if constraints else ""
                        
                        markdown_output += f"- **{col_name}**: {data_type}{constraint_text}\\n"
                    
                    # Primary keys section
                    if primary_keys:
                        markdown_output += f"\\n### Primary Keys\\n\\n"
                        markdown_output += f"- {', '.join([f'**{pk}**' for pk in primary_keys])}\\n"
                    
                    # Foreign keys section
                    if foreign_keys:
                        markdown_output += f"\\n### Foreign Keys\\n\\n"
                        for fk in foreign_keys:
                            markdown_output += f"- **{fk['column_name']}** → {fk['foreign_table_schema']}.{fk['foreign_table_name']}({fk['foreign_column_name']})\\n"
                    
                    # Indices section
                    if indices:
                        markdown_output += f"\\n### Indices\\n\\n"
                        for idx in indices:
                            markdown_output += f"- **{idx['indexname']}**: {idx['indexdef']}\\n"
                    
                    markdown_output += "\\n---\\n\\n"
                
                print(json.dumps({"result": markdown_output.strip()}))
                
except Exception as e:
    print(json.dumps({"error": f"Error connecting to database: {str(e)}"}))
`;

      return new Promise(resolve => {
        let output = '';

        // Set up message handler to capture output
        const onIOPubMessage = (msg: any) => {
          if (
            msg.header.msg_type === 'stream' &&
            msg.content.name === 'stdout'
          ) {
            output += msg.content.text;
          } else if (msg.header.msg_type === 'execute_result') {
            if (msg.content.data && msg.content.data['text/plain']) {
              output += msg.content.data['text/plain'];
            }
          }
        };

        // Execute the Python code
        const future = kernel.requestExecute({
          code: pythonCode,
          silent: true
        });

        // Listen for messages
        future.onIOPub = onIOPubMessage;

        future.done
          .then(() => {
            try {
              // Parse the JSON output from Python
              const result = JSON.parse(output.trim());

              if (result.error) {
                console.error('[DatabaseTools] Database error:', result.error);
                resolve(result.error);
              } else {
                console.log(
                  '[DatabaseTools] Database schema info retrieved successfully'
                );
                // Replace unprocessed newlines with real newlines
                const processedResult = result.result.split('\\n').join('\n');
                resolve(processedResult);
              }
            } catch (parseError) {
              console.error(
                '[DatabaseTools] Error parsing kernel output:',
                parseError
              );
              // console.error('[DatabaseTools] Raw output:', output)
              resolve(`Error parsing database query result: ${output}`);
            } finally {
              // Clean up the temporary kernel
              cleanup();
            }
          })
          .catch((error: any) => {
            console.error('[DatabaseTools] Kernel execution error:', error);
            // Clean up the temporary kernel on error
            cleanup();
            resolve(
              `Error executing database query in kernel: ${error.message}`
            );
          });
      });
    } catch (error) {
      console.error(
        '[DatabaseTools] Error getting database schema info:',
        error
      );
      return `Error getting database schema info: ${error instanceof Error ? error.message : String(error)}`;
    }
  }

  /**
   * Get database metadata as structured JSON
   * @param dbUrl PostgreSQL connection string (optional, will use kernel environment if not provided)
   * @returns Promise<string> JSON string with database metadata
   */
  async getDatabaseMetadata(dbUrl?: string): Promise<string> {
    try {
      const textResult = await this.getDatabaseMetadataAsText(dbUrl);

      if (textResult.startsWith('Error:')) {
        return JSON.stringify({
          error: textResult
        });
      }

      return JSON.stringify({
        schema_info: textResult,
        db_url_configured: !!dbUrl || !!process.env.DB_URL
      });
    } catch (error) {
      console.error('[DatabaseTools] Error getting database metadata:', error);
      return JSON.stringify({
        error: `Failed to get database metadata: ${error instanceof Error ? error.message : String(error)}`
      });
    }
  }

  /**
   * Execute a read-only SQL query in the Python kernel
   * @param query SQL query to execute
   * @param dbUrl Optional database URL (will use kernel environment if not provided)
   * @returns Promise<string> JSON string with query results
   */
  async executeQuery(query: string, dbUrl?: string): Promise<string> {
    try {
      console.log(
        '[DatabaseTools] Executing SQL query via temporary kernel...'
      );

      // Create a temporary kernel for this operation
      const { kernel, cleanup } = await this.createTemporaryKernel();

      if (!kernel) {
        return JSON.stringify({
          error: 'Failed to create temporary kernel for database query'
        });
      }

      // Basic validation for read-only queries
      const normalizedQuery = query.trim().toUpperCase();
      if (
        !normalizedQuery.startsWith('SELECT') &&
        !normalizedQuery.startsWith('WITH')
      ) {
        return JSON.stringify({
          error: 'Only SELECT or WITH statements are allowed for read queries.'
        });
      }

      // Python code to execute the SQL query
      const pythonCode = `
import os
import json
import subprocess
import sys

# Function to install packages if they don't exist
def install_package(package_name):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"[DatabaseTools] Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[DatabaseTools] Failed to install {package_name}: {str(e)}")
        return False

# Check if required modules are available, install if missing
missing_packages = []
try:
    import sqlalchemy
except ImportError:
    print("[DatabaseTools] sqlalchemy not found, attempting to install...")
    if install_package("sqlalchemy"):
        try:
            import sqlalchemy
            print("[DatabaseTools] sqlalchemy successfully imported after installation")
        except ImportError as e:
            missing_packages.append(f"sqlalchemy: {str(e)}")
    else:
        missing_packages.append("sqlalchemy: installation failed")

try:
    import psycopg2
except ImportError:
    print("[DatabaseTools] psycopg2 not found, attempting to install psycopg2-binary...")
    if install_package("psycopg2-binary"):
        try:
            import psycopg2
            print("[DatabaseTools] psycopg2 successfully imported after installation")
        except ImportError as e:
            missing_packages.append(f"psycopg2: {str(e)}")
    else:
        missing_packages.append("psycopg2: installation failed")

# If any packages are still missing after installation attempts, exit with error
if missing_packages:
    print(json.dumps({"error": f"Required modules could not be installed: {', '.join(missing_packages)}"}))
    exit()

try:
    # Use provided dbUrl or get from environment
    db_url = ${dbUrl ? `'${dbUrl.replace(/'/g, "\\'")}'` : "os.environ.get('DB_URL')"}
    
    if not db_url:
        print(json.dumps({"error": "No database URL provided and DB_URL environment variable not set"}))
    else:
        from sqlalchemy import create_engine, text
        
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            query = """${query.replace(/"/g, '\\"').replace(/\n/g, '\\n')}"""
            result = conn.execute(text(query))
            
            # Convert result to list of dictionaries
            rows = [dict(row._mapping) for row in result]
            
            print(json.dumps({"result": rows}))
            
except Exception as e:
    print(json.dumps({"error": f"Database query failed: {str(e)}"}))
`;

      return new Promise(resolve => {
        let output = '';

        // Set up message handler to capture output
        const onIOPubMessage = (msg: any) => {
          if (
            msg.header.msg_type === 'stream' &&
            msg.content.name === 'stdout'
          ) {
            output += msg.content.text;
          } else if (msg.header.msg_type === 'execute_result') {
            if (msg.content.data && msg.content.data['text/plain']) {
              output += msg.content.data['text/plain'];
            }
          }
        };

        // Execute the Python code
        const future = kernel.requestExecute({
          code: pythonCode,
          silent: true
        });

        // Listen for messages
        future.onIOPub = onIOPubMessage;

        future.done
          .then(() => {
            try {
              // Parse the JSON output from Python
              const result = JSON.parse(output.trim());
              resolve(JSON.stringify(result));
            } catch (parseError) {
              console.error(
                '[DatabaseTools] Error parsing kernel output:',
                parseError
              );
              console.error('[DatabaseTools] Raw output:', output);
              resolve(
                JSON.stringify({
                  error: `Error parsing database query result: ${output}`
                })
              );
            } finally {
              // Clean up the temporary kernel
              cleanup();
            }
          })
          .catch((error: any) => {
            console.error('[DatabaseTools] Kernel execution error:', error);
            // Clean up the temporary kernel on error
            cleanup();
            resolve(
              JSON.stringify({
                error: `Error executing database query in kernel: ${error.message}`
              })
            );
          });
      });
    } catch (error) {
      console.error('[DatabaseTools] Error executing SQL query:', error);
      return JSON.stringify({
        error: `Failed to execute SQL query: ${error instanceof Error ? error.message : String(error)}`
      });
    }
  }
}
