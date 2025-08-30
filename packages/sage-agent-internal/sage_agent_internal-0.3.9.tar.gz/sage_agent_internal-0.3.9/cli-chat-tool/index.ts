import 'dotenv/config'; // Load .env file
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import {
  type ChatSession,
  type FunctionDeclaration,
  type FunctionDeclarationSchema,
  type GenerateContentResponse,
  GoogleGenerativeAI,
   HarmCategory, HarmBlockThreshold,
  Tool,
  SchemaType,
} from "@google/generative-ai";
import assert from "node:assert";
import readline from "node:readline/promises"; // Use readline/promises for async input

function isEmptyObject(obj: object) {
  return Object.keys(obj).length === 0;
}

// Use SchemaType for the mapping
const typeStringMapping: { [key: string]: SchemaType } = {
  number: SchemaType.NUMBER,
  string: SchemaType.STRING,
  boolean: SchemaType.BOOLEAN,
  object: SchemaType.OBJECT,
  array: SchemaType.ARRAY,
  integer: SchemaType.INTEGER,
};

/**
 * Recursively transforms an object or array by replacing string values
 * associated with a 'type' key with corresponding enum values from SchemaType.
 * Creates a deep clone to avoid modifying the original object.
 *
 * @param data - The input data (object, array, or primitive) to transform.
 * @returns The transformed data with 'type' strings replaced by SchemaType enum values.
 */
function transformTypes<T>(data: T): T {
  if (typeof data !== "object" || data === null) {
    return data;
  }

  if (Array.isArray(data)) {
    return data.map((item) => transformTypes(item)) as T;
  }

  // Handle Objects
  const newData: { [key: string]: any } = {};
  for (const key in data) {
    if (Object.prototype.hasOwnProperty.call(data, key)) {
      const value = data[key];
      if (key === "type" && typeof value === "string" && typeStringMapping[value]) {
        // Use the mapping which now uses the SchemaType enum
        newData[key] = typeStringMapping[value];
      } else {
        newData[key] = transformTypes(value);
      }
    }
  }
  return newData as T;
}

async function handleAiResp(
  { response, chat, mcpClients }: {
    response: GenerateContentResponse;
    chat: ChatSession;
    mcpClients: [Client];
  },
) {
  // Check for safety ratings and blocked prompts
  if (response.promptFeedback?.blockReason) {
      console.error(`Prompt blocked due to: ${response.promptFeedback.blockReason}`);
      // Handle the blocked prompt appropriately, e.g., inform the user, retry with modifications
      // You might want to inspect response.promptFeedback.safetyRatings for more details
      return; // Stop processing this response
  }

  for (const candidate of response?.candidates ?? []) {
     // Check if the candidate was blocked
    if (candidate.finishReason === "SAFETY") {
      console.warn("Response candidate blocked due to safety concerns.");
      // Optionally inspect candidate.safetyRatings
      continue; // Move to the next candidate
    }
     if (candidate.finishReason === "RECITATION") {
      console.warn("Response candidate blocked due to potential recitation.");
      // Optionally inspect candidate.safetyRatings
      continue; // Move to the next candidate
    }
    if (candidate.finishReason === "OTHER") {
      console.warn(`Response candidate finished due to an unspecified reason: ${candidate.finishReason}`);
      continue;
    }

    for (const part of candidate.content?.parts ?? []) {
      if (part.text) {
          console.log("AI:", part.text);
      }
      if (part.functionCall) {
        console.log("AI requesting tool call:", part.functionCall.name, JSON.stringify(part.functionCall.args));
        const name = part.functionCall.name;
        assert(name, "Function call name is missing");
        let foundTool = false;

        // Check if the tool exists on the single client
         try {
           const toolListResponse = await mcpClients[0].listTools() as any;
           const availableTools: {name: string}[] = toolListResponse?.tools ?? [];
           if (availableTools.some(tool => tool.name === name)) {
              foundTool = true;
           }
         } catch (error) {
             console.error(`Error listing tools for client jupyterClient:`, error);
         }
        

        if (!foundTool) {
            console.error(`Error: Tool '${name}' not found in the connected MCP client (jupyterClient).`);
             const errorResponse = await chat.sendMessage([
                 { functionResponse: { name, response: { error: `Tool ${name} not found` } } }
             ]);
             await handleAiResp({ response: errorResponse.response, chat, mcpClients }); 
            continue; 
        }

         try {
             console.log(`Calling tool '${name}' on client jupyterClient...`);
             const toolArgs = (part.functionCall.args ?? {}) as Record<string, unknown>; 
             const result = await mcpClients[0].callTool({
               name,
               arguments: toolArgs, 
             }) as any; 

             console.log(`Tool '${name}' result:`, JSON.stringify(result, null, 2));

             if (result?.content) {
                const chatResp = await chat.sendMessage([
                    { functionResponse: { name, response: result } }
                ]);
               await handleAiResp({ response: chatResp.response, chat, mcpClients }); 
             } else {
                  console.warn(`Tool '${name}' did not return content.`);
                  const noContentResp = await chat.sendMessage([
                       { functionResponse: { name, response: { message: "Tool executed but returned no content." } } }
                  ]);
                  await handleAiResp({ response: noContentResp.response, chat, mcpClients }); 
             }
         } catch (error) {
             console.error(`Error calling tool '${name}':`, error);
             const errorResponse = await chat.sendMessage([
                 { functionResponse: { name, response: { error: `Failed to execute tool ${name}: ${error instanceof Error ? error.message : String(error)}` } } }
             ]);
              await handleAiResp({ response: errorResponse.response, chat, mcpClients }); 
         }
      }
    }
  }
}

async function mcpToolsToGeminiFunctionDeclarations(mcpClient: Client): Promise<FunctionDeclaration[]> {
  let allFnDecls: FunctionDeclaration[] = [];
  const clientName = "jupyterClient"; // Use the known name
  try {
    const listToolsResponse = await mcpClient.listTools() as any;
    const tools = listToolsResponse?.tools ?? [];
    console.log(`Processing tools for client: ${clientName}`);

     // Process tools from the single client
    const fnDecls = tools.map((tool: any) => {
      let schema = structuredClone(tool.inputSchema || { type: "object", properties: {} });
      if (!schema.properties) { schema.properties = {}; }
      if (!schema.type) { schema.type = 'object'; }
      else if (schema.type !== 'object') { schema.type = 'object'; }
      schema = transformTypes(schema);
      delete schema.$schema;
      if (schema.properties && typeof schema.properties === 'object') {
        for (const [_key, val] of Object.entries(schema.properties as Record<string, any>)) {
          if (val && typeof val === 'object' && !('type' in val)) {
            Object.assign(val, { type: SchemaType.STRING }); 
          }
        }
      } else {
         schema.properties = {};
      }
     const fnDecl: FunctionDeclaration = {
       name: tool.name,
       description: tool.description || `Execute the ${tool.name} tool.`,
     };
     if (schema.properties && !isEmptyObject(schema.properties)) {
       fnDecl.parameters = schema as FunctionDeclarationSchema;
     }
     return fnDecl;
    }).filter((decl: FunctionDeclaration | undefined | null): decl is FunctionDeclaration => !!decl);

    allFnDecls = allFnDecls.concat(fnDecls);

  } catch (error) {
       console.error(`Error processing tools for client ${clientName}:`, error);
  }
  return allFnDecls;
}

// Helper function to filter process.env
function getFilteredEnv(): Record<string, string> {
    const filteredEnv: Record<string, string> = {};
    for (const key in process.env) {
        if (Object.prototype.hasOwnProperty.call(process.env, key)) {
            const value = process.env[key];
            if (value !== undefined) {
                filteredEnv[key] = value;
            }
        }
    }
    return filteredEnv;
}

// Main execution wrapped in an async IIFE (Immediately Invoked Function Expression)
(async () => {
  // --- Environment Variable Setup ---
  const API_KEY = process.env.API_KEY;
  const MODEL_ID = process.env.MODEL_ID || "gemini-1.5-flash-latest"; // Default model

  if (!API_KEY) {
    console.error("Error: API_KEY environment variable not set.");
    process.exit(1);
  }

  const filteredEnv = getFilteredEnv();

  // --- MCP Client Setup ---
  // Configure transport1 for the uv command
  const transport1 = new StdioClientTransport({
    command: "uv", 
    args: [
      "--directory",
      // TODO: Consider making this path configurable via .env or argument?
      "/Users/adibhasan/sage-book/jupyter-mcp-server", 
      "run",
      "--frozen",
      "python",
      "-m",
      "src.server.simple_server",
      "--stdio"
    ],
    env: filteredEnv, 
  });

  // Keep only mcpClient1
  const mcpClient1 = new Client({ name: "jupyterClient", version: "1.0.0" });

  try {
    console.log("Connecting to MCP client..."); // Updated log message
    // Connect only mcpClient1
    await mcpClient1.connect(transport1);
    console.log("MCP client connected.");
  } catch (error) {
     console.error("Failed to connect to MCP client:", error); // Updated log message
     // Attempt to close the potentially open connection
     await mcpClient1.close(); 
     process.exit(1);
  }

  // Array contains only the one client
  const mcpClients: [Client] = [mcpClient1]; 

  // --- Gemini Client Setup ---
  console.log("Initializing Gemini client...");
  const genAI = new GoogleGenerativeAI(API_KEY);

  // Fetch and prepare tool declarations for the single client
  let functionDeclarations: FunctionDeclaration[] = [];
  try {
       console.log("Fetching tool definitions from MCP client..."); // Updated log
       // Pass only the single client to the updated function
      functionDeclarations = await mcpToolsToGeminiFunctionDeclarations(mcpClient1); 
      if (functionDeclarations.length === 0) {
         console.warn("Warning: No tools were successfully processed from the MCP client. Proceeding without tools.");
      } else {
         console.log(`Successfully processed ${functionDeclarations.length} tool declarations.`);
      }
  } catch (error) {
      console.error("Error processing MCP tools for Gemini:", error);
      console.warn("Proceeding without tools due to processing error.");
  }

  const tools: Tool[] = functionDeclarations.length > 0 ? [{ functionDeclarations }] : [];

  const model = genAI.getGenerativeModel({
       model: MODEL_ID,
       tools: tools,
       // Optional: Configure safety settings
       safetySettings: [
            { category: HarmCategory.HARM_CATEGORY_HARASSMENT, threshold: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE },
            { category: HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE },
            { category: HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE },
            { category: HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE },
       ]
  });

  const chat = model.startChat({
    // Optional: Add initial history if needed
    // history: [
    //   { role: "user", parts: [{ text: "Initial user message" }] },
    //   { role: "model", parts: [{ text: "Initial model response" }] },
    // ],
    // generationConfig: { // Optional: Add generation config if needed
    //   maxOutputTokens: 100,
    // }
  });

  console.log(`Chat started with model: ${MODEL_ID}`);
  console.log("Welcome to AI REPL. Type ':exit' to quit.");

  // --- Chat Loop ---
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  try {
      while (true) {
        const userInput = await rl.question("You: ");
        if (!userInput) continue;
        if (userInput.toLowerCase() === ":exit") break;

        try {
          const result = await chat.sendMessage(userInput);
          await handleAiResp({ response: result.response, chat, mcpClients }); 
        } catch (error) {
           console.error("Error sending message or handling response:", error);
        }
      }
  } finally {
      rl.close();
      console.log("Closing MCP connection..."); // Updated log
      await mcpClient1.close(); 
      console.log("Connection closed. Exiting.");
  }

})(); // End of async IIFE 