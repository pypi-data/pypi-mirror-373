import { Widget } from '@lumino/widgets';
import { Message } from '@lumino/messaging';
import { JupyterFrontEnd } from '@jupyterlab/application';
import { INotebookTracker, NotebookPanel, NotebookActions } from '@jupyterlab/notebook';
import { CodeCell } from '@jupyterlab/cells';

/**
 * A floating input widget for Pantheon commands
 */
export class FloatingInputWidget extends Widget {
  private _notebookTracker: INotebookTracker;
  private _inputElement!: HTMLTextAreaElement;
  private _outputElement!: HTMLDivElement;
  private _statusOutputElement!: HTMLDivElement;
  private _sendButton!: HTMLButtonElement;
  private _toggleButton!: HTMLButtonElement;
  private _statusToggleButton!: HTMLButtonElement;
  private _isExpanded: boolean = false;
  private _isStatusExpanded: boolean = false;
  private _history: string[] = [];
  private _historyIndex: number = -1;
  private _commandHistory: string[] = [];
  private _parentLayout: any = null; // Store reference to parent layout
  private _currentQueryHandler: ((input: string) => Promise<void>) | null = null;

  constructor(app: JupyterFrontEnd, notebookTracker: INotebookTracker) {
    super();
    this._notebookTracker = notebookTracker;
    
    this.id = 'pantheon-floating-input';
    this.title.label = 'Pantheon Assistant';
    this.title.closable = false; // Make it non-closable so it stays visible
    
    // Add CSS classes
    this.addClass('pantheon-floating-widget');
    
    // Set initial styling to ensure visibility (increased height for output area)
    this.node.style.cssText = `
      height: 350px;
      min-height: 350px;
      background: var(--jp-layout-color1, #ffffff);
      border: 1px solid var(--jp-border-color2, #e0e0e0);
      display: flex;
      flex-direction: column;
      box-sizing: border-box;
      transform-origin: bottom;
      transition: height 0.3s ease, transform 0.3s ease, margin-top 0.3s ease;
      overflow: hidden;
      position: relative;
    `;
    
    // Create the widget content
    this._createContent();
  }

  /**
   * Create the widget content
   */
  private _createContent(): void {
    console.log('Creating Pantheon widget content...');
    
    const container = document.createElement('div');
    container.className = 'pantheon-container';
    container.style.cssText = `
      display: flex;
      flex-direction: column-reverse;
      height: 100%;
      padding: 8px;
      background: inherit;
      transition: height 0.3s ease, transform 0.3s ease;
      justify-content: flex-start;
    `;
    
    // Create header
    const header = document.createElement('div');
    header.className = 'pantheon-header';
    header.style.cssText = `
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 4px 8px;
      border-bottom: 1px solid var(--jp-border-color2, #e0e0e0);
      margin-bottom: 8px;
      background: var(--jp-layout-color2, #f5f5f5);
    `;
    
    const title = document.createElement('span');
    title.className = 'pantheon-title';
    title.textContent = ' Pantheon Assistant';
    title.style.cssText = `
      font-weight: 600;
      color: var(--jp-ui-font-color0, #000);
      font-size: 14px;
    `;
    
    this._toggleButton = document.createElement('button');
    this._toggleButton.className = 'pantheon-toggle-btn';
    this._toggleButton.innerHTML = '▲';
    this._toggleButton.title = 'Expand widget';
    this._toggleButton.style.cssText = `
      background: none;
      border: none;
      color: var(--jp-ui-font-color2, #666);
      cursor: pointer;
      padding: 4px 8px;
      font-size: 12px;
    `;
    this._toggleButton.onclick = () => this._toggleExpanded();
    
    header.appendChild(title);
    header.appendChild(this._toggleButton);
    
    // Create output area (above input)
    const outputContainer = document.createElement('div');
    outputContainer.className = 'pantheon-output-container';
    outputContainer.style.cssText = `
      display: flex;
      flex-direction: column;
      max-height: 200px;
      min-height: 100px;
      border: 1px solid var(--jp-border-color2, #e0e0e0);
      border-radius: 4px;
      background: var(--jp-layout-color0, #fff);
      margin-bottom: 8px;
      overflow-y: auto;
    `;
    
    this._outputElement = document.createElement('div');
    this._outputElement.className = 'pantheon-output';
    this._outputElement.style.cssText = `
      padding: 8px;
      font-family: var(--jp-code-font-family, monospace);
      font-size: 12px;
      line-height: 1.4;
      color: var(--jp-ui-font-color1, #000);
      white-space: pre-wrap;
      overflow-wrap: break-word;
    `;
    this._outputElement.innerHTML = `<span style="color: var(--jp-ui-font-color2, #666);"> Pantheon Assistant Ready
Type a message or use commands like:
• /help - Show available commands
• /status - Show session status
• /history - Show command history
• /clear - Clear this output

Ready for your queries!</span>`;
    
    outputContainer.appendChild(this._outputElement);

    // Create status output area
    const statusSection = document.createElement('div');
    statusSection.className = 'pantheon-status-section';
    statusSection.style.cssText = `
      margin-bottom: 8px;
    `;

    const statusHeader = document.createElement('div');
    statusHeader.className = 'pantheon-status-header';
    statusHeader.style.cssText = `
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 4px 8px;
      border: 1px solid var(--jp-border-color2, #e0e0e0);
      border-radius: 4px 4px 0 0;
      background: var(--jp-layout-color2, #f5f5f5);
      font-size: 12px;
      font-weight: 500;
    `;

    const statusTitle = document.createElement('span');
    statusTitle.textContent = '📊 Execution Status';
    statusTitle.style.color = 'var(--jp-ui-font-color1, #000)';

    this._statusToggleButton = document.createElement('button');
    this._statusToggleButton.className = 'pantheon-status-toggle-btn';
    this._statusToggleButton.innerHTML = '▲';
    this._statusToggleButton.title = 'Show execution status';
    this._statusToggleButton.style.cssText = `
      background: none;
      border: none;
      color: var(--jp-ui-font-color2, #666);
      cursor: pointer;
      padding: 2px 6px;
      font-size: 10px;
    `;
    this._statusToggleButton.onclick = () => this._toggleStatusExpanded();

    statusHeader.appendChild(statusTitle);
    statusHeader.appendChild(this._statusToggleButton);

    const statusOutputContainer = document.createElement('div');
    statusOutputContainer.className = 'pantheon-status-output-container';
    statusOutputContainer.style.cssText = `
      max-height: 120px;
      border: 1px solid var(--jp-border-color2, #e0e0e0);
      border-top: none;
      border-radius: 0 0 4px 4px;
      background: var(--jp-layout-color0, #fff);
      overflow-y: auto;
      display: none;
    `;

    this._statusOutputElement = document.createElement('div');
    this._statusOutputElement.className = 'pantheon-status-output';
    this._statusOutputElement.style.cssText = `
      padding: 8px;
      font-family: var(--jp-code-font-family, monospace);
      font-size: 11px;
      line-height: 1.3;
      color: var(--jp-ui-font-color2, #666);
      white-space: pre-wrap;
      overflow-wrap: break-word;
    `;
    this._statusOutputElement.innerHTML = `<span style="color: var(--jp-ui-font-color3, #999);">Status messages will appear here...</span>`;

    statusOutputContainer.appendChild(this._statusOutputElement);
    statusSection.appendChild(statusHeader);
    statusSection.appendChild(statusOutputContainer);

    // Create input area
    const inputContainer = document.createElement('div');
    inputContainer.className = 'pantheon-input-container';
    inputContainer.style.cssText = `
      display: flex;
      flex-direction: column;
      gap: 8px;
    `;
    
    this._inputElement = document.createElement('textarea');
    this._inputElement.className = 'pantheon-input';
    this._inputElement.placeholder = 'Ask Pantheon to generate code...';
    this._inputElement.rows = 3;
    this._inputElement.style.cssText = `
      flex: 1;
      padding: 8px;
      border: 1px solid var(--jp-border-color2, #e0e0e0);
      border-radius: 4px;
      background: var(--jp-layout-color0, #fff);
      color: var(--jp-ui-font-color1, #000);
      font-family: var(--jp-code-font-family, monospace);
      font-size: 13px;
      resize: vertical;
      min-height: 60px;
      max-height: 150px;
      outline: none;
    `;
    
    // Add keyboard shortcuts
    this._inputElement.addEventListener('keydown', (event) => {
      if (event.key === 'Enter') {
        if (event.ctrlKey || event.metaKey) {
          event.preventDefault();
          this._sendQuery();
        } else {
          // Enter key just adds a new line, don't send query
          // Users need to click Generate button or use Ctrl+Enter
        }
      } else if (event.key === 'ArrowUp' && event.ctrlKey) {
        event.preventDefault();
        this._navigateHistory(-1);
      } else if (event.key === 'ArrowDown' && event.ctrlKey) {
        event.preventDefault();
        this._navigateHistory(1);
      }
    });
    
    // Create button container
    const buttonContainer = document.createElement('div');
    buttonContainer.className = 'pantheon-button-container';
    buttonContainer.style.cssText = `
      display: flex;
      gap: 8px;
      justify-content: flex-end;
    `;
    
    this._sendButton = document.createElement('button');
    this._sendButton.className = 'pantheon-send-btn';
    this._sendButton.textContent = 'Generate';
    this._sendButton.style.cssText = `
      padding: 6px 16px;
      border-radius: 4px;
      border: none;
      font-size: 13px;
      font-weight: 500;
      cursor: pointer;
      background: var(--jp-brand-color1, #2196F3);
      color: white;
    `;
    this._sendButton.onclick = () => this._sendQuery();
    
    const clearButton = document.createElement('button');
    clearButton.className = 'pantheon-clear-btn';
    clearButton.textContent = 'Clear';
    clearButton.style.cssText = `
      padding: 6px 16px;
      border-radius: 4px;
      border: 1px solid var(--jp-border-color2, #e0e0e0);
      font-size: 13px;
      font-weight: 500;
      cursor: pointer;
      background: var(--jp-layout-color2, #f5f5f5);
      color: var(--jp-ui-font-color1, #000);
    `;
    clearButton.onclick = () => this._clearInput();
    
    buttonContainer.appendChild(clearButton);
    buttonContainer.appendChild(this._sendButton);
    
    // Assemble the widget
    inputContainer.appendChild(this._inputElement);
    inputContainer.appendChild(buttonContainer);
    
    // Add status bar
    const statusBar = document.createElement('div');
    statusBar.className = 'pantheon-status';
    statusBar.style.cssText = `
      padding: 4px 8px;
      border-top: 1px solid var(--jp-border-color2, #e0e0e0);
      margin-top: 8px;
      font-size: 12px;
      color: var(--jp-ui-font-color2, #666);
      background: var(--jp-layout-color2, #f5f5f5);
    `;
    statusBar.innerHTML = '<span class="pantheon-status-text">Ready</span>';
    
    // Add elements in reverse order due to column-reverse
    // This ensures header appears at bottom, content expands upward
    container.appendChild(statusBar);
    container.appendChild(inputContainer);
    container.appendChild(statusSection);
    container.appendChild(outputContainer);
    container.appendChild(header);
    
    this.node.appendChild(container);
    
    // Initialize as collapsed state
    setTimeout(() => {
      this._initializeCollapsedState();
    }, 100);
    
    console.log('Pantheon widget content created and added to DOM');
  }

  /**
   * Set parent layout reference (called from index.ts when added to layout)
   */
  public setParentLayout(layout: any): void {
    this._parentLayout = layout;
  }

  /**
   * Send the query to Pantheon
   */
  private async _sendQuery(): Promise<void> {
    const query = this._inputElement.value.trim();
    if (!query) {
      return;
    }
    
    // Check if we have a special handler (e.g., for error responses)
    if (this._currentQueryHandler) {
      await this._currentQueryHandler(query);
      this._clearInput();
      return;
    }
    
    // Add to history
    this._history.push(query);
    this._historyIndex = this._history.length;
    this._commandHistory.push(query);
    
    // Show input in output
    this._appendToOutput(`> ${query}`, 'user-input');
    
    // Check if it's a slash command
    if (query.startsWith('/')) {
      await this._handleSlashCommand(query);
      this._clearInput();
      return;
    }
    
    // Update status
    this._updateStatus('Processing with Pantheon AI...', 'processing');
    
    // Get the current notebook
    const notebook = this._notebookTracker.currentWidget;
    if (!notebook) {
      this._appendToOutput('❌ No active notebook found', 'error');
      this._updateStatus('Ready', 'ready');
      return;
    }
    
    try {
      // Get notebook path for session management
      const notebookPath = notebook.context.path || 'default';
      
      // Call Pantheon backend API
      const response = await this._callPantheonAPI(query, notebookPath);
      
      if (response.success) {
        // Show response info
        this._appendToOutput(`✅ Code generated from Pantheon AI`, 'success');
        
        // Parse raw response to extract markdown and code blocks in order
        const blocks = this._parseResponseIntoBlocks(response);
        
        if (blocks.length > 0) {
          this._appendToStatusOutput(`📝 Inserting ${blocks.length} block(s) into notebook...`, 'status');
          
          try {
            // Insert each block (markdown or code)
            for (let i = 0; i < blocks.length; i++) {
              const block = blocks[i];
              
              if (block.type === 'markdown') {
                // Insert markdown cell
                const mdIndex = this._insertMarkdownIntoNotebook(notebook, block.content);
                this._appendToStatusOutput(`📄 Markdown inserted into cell ${mdIndex + 1}`, 'success');
              } else if (block.type === 'code') {
                this._appendToStatusOutput(`▶️ Inserting code block ${i + 1}:`, 'status');
                
                // Insert code into a new cell
                const cellIndex = this._insertCodeIntoNotebook(notebook, block.content);
                this._appendToStatusOutput(`✅ Code inserted into cell ${cellIndex + 1}`, 'success');
                
                // Execute the cell immediately
                this._appendToStatusOutput(`🚀 Executing cell ${cellIndex + 1}...`, 'status');
                const result = await this._executeCellInNotebook(notebook, cellIndex);
                
                if (result.hasError) {
                  this._appendToStatusOutput(`❌ Error in cell ${cellIndex + 1}: ${result.output}`, 'error');
                  
                  // Try to fix the error automatically
                  const shouldTryFix = await this._handleCellError(notebook, cellIndex, block.content, result.output, i + 1);
                  
                  if (!shouldTryFix) {
                    this._appendToStatusOutput(`⏹️ Execution stopped due to unresolvable error`, 'error');
                    break;
                  }
                } else {
                  this._appendToStatusOutput(`✅ Cell ${cellIndex + 1} executed successfully`, 'success');
                  if (result.output && result.output.trim()) {
                    this._appendToOutput(`📊 Output: ${result.output.slice(0, 200)}${result.output.length > 200 ? '...' : ''}`, 'output');
                  }
                }
              }
            }
            
            this._appendToOutput(`🏁 All code blocks processed!`, 'success');
          } catch (error) {
            this._appendToOutput(`❌ Error processing code blocks: ${error}`, 'error');
          }
        } else {
          this._appendToOutput(`ℹ️ No code blocks to execute`, 'system');
        }
        
        // Clear input after successful processing
        this._clearInput();
        this._updateStatus('Processing complete', 'success');
        
        // Reset status after 3 seconds
        setTimeout(() => {
          this._updateStatus('Ready', 'ready');
        }, 3000);
      } else {
        throw new Error(response.error || 'Unknown error from Pantheon API');
      }
      
    } catch (error) {
      console.error('Error processing query:', error);
      const errorMessage = error instanceof Error ? error.message : String(error);
      
      // Show error in output area
      this._appendToOutput(`❌ Error: ${errorMessage}`, 'error');
      this._showMessage(`Error: ${errorMessage}`, 'error');
      this._updateStatus('Error', 'error');
      
      // Reset status after 5 seconds for errors
      setTimeout(() => {
        this._updateStatus('Ready', 'ready');
      }, 5000);
    }
  }
  
  /**
   * Notebook-based execution loop - insert code in cells, then execute via notebook
   */
  private async _notebookExecutionLoop(originalQuery: string, initialResponse: any, notebook: any): Promise<void> {
    try {
      await this._ensureKernelReady(notebook);
    } catch (error) {
      this._appendToOutput(`❌ Failed to prepare kernel: ${error}`, 'error');
      this._updateStatus('Kernel error', 'error');
      return;
    }

    this._appendToOutput(`🚀 Auto-executing code for: "${originalQuery}"`, 'system');
    
    let currentResponse = initialResponse;
    let iterationCount = 0;
    const maxIterations = 3;
    const insertedCellIndexes: number[] = []; // Track inserted cells
    
    while (iterationCount < maxIterations) {
      iterationCount++;
      this._appendToOutput(`🔄 Iteration ${iterationCount}`, 'system');
      
      if (!currentResponse.code_blocks || currentResponse.code_blocks.length === 0) {
        this._appendToOutput(`✅ No more code to execute`, 'success');
        break;
      }
      
      // Execute all code blocks that were already inserted in the notebook
      const executionResults = [];
      const currentIndex = notebook.content.activeCellIndex;
      
      // Find the cells that contain our generated code
      let cellIndex = currentIndex + 1; // Start from the cell after current
      
      for (let i = 0; i < currentResponse.code_blocks.length; i++) {
        const code = currentResponse.code_blocks[i];
        this._appendToOutput(`▶️ Executing code block ${i + 1} in cell ${cellIndex + 1}:`, 'system');
        
        // Find or create the cell with this code
        let targetCell = null;
        let targetIndex = cellIndex;
        
        // Check if we need to find the right cell
        for (let j = cellIndex; j < notebook.content.model.cells.length; j++) {
          const cell = notebook.content.model.cells.get(j);
          if (cell && cell.source === code.trim()) {
            targetCell = cell;
            targetIndex = j;
            break;
          }
        }
        
        if (!targetCell) {
          // Insert the code as a new cell if not found
          notebook.model?.sharedModel.insertCell(cellIndex, {
            cell_type: 'code',
            source: code.trim()
          });
          targetIndex = cellIndex;
          insertedCellIndexes.push(cellIndex);
          cellIndex++;
        }
        
        // Execute the cell and get results
        const result = await this._executeCellAtIndex(notebook, targetIndex);
        executionResults.push(result);
        
        if (result.hasError) {
          this._appendToOutput(`❌ Error in block ${i + 1}:\n${result.output}`, 'error');
          
          // Send error back to agent for analysis and fix
          const fixQuery = `The code execution failed with error: ${result.output}\n\nOriginal code:\n${code}\n\nPlease analyze the error and provide a fixed version.`;
          
          try {
            this._appendToOutput(`🔧 Asking agent to fix the error...`, 'system');
            const fixResponse = await this._callPantheonAPI(fixQuery, 'error_fix');
            
            if (fixResponse.success) {
              // Display the full agent response for error fixes
              if (fixResponse.raw_response) {
                this._appendToOutput(fixResponse.raw_response, 'output');
              } else if (fixResponse.explanation) {
                this._appendToOutput(`💡 Agent analysis: ${fixResponse.explanation}`, 'system');
              }
              currentResponse = fixResponse;
              break; // Exit code block loop to retry with fixed code
            }
          } catch (error) {
            this._appendToOutput(`❌ Failed to get fix from agent: ${error}`, 'error');
            return;
          }
        } else {
          if (result.output && result.output.trim()) {
            this._appendToOutput(`📊 Block ${i + 1} Output:\n${result.output}`, 'output');
          } else {
            this._appendToOutput(`✅ Block ${i + 1} executed successfully`, 'success');
          }
        }
        
        cellIndex++;
      }
      
      // If all blocks executed successfully, check if agent wants to continue
      const allSuccessful = executionResults.every(r => !r.hasError);
      if (allSuccessful) {
        const outputSummary = executionResults.map((r, i) => `Block ${i + 1}: ${r.output || 'No output'}`).join('\n');
        
        const continueQuery = `The code executed successfully with these results:\n${outputSummary}\n\nOriginal request was: "${originalQuery}"\n\nIs the task complete, or do you need to generate additional code to fully satisfy the request?`;
        
        try {
          this._appendToOutput(`🤔 Checking if task is complete...`, 'system');
          const continueResponse = await this._callPantheonAPI(continueQuery, 'continuation_check');
          
          if (continueResponse.success && continueResponse.code_blocks && continueResponse.code_blocks.length > 0) {
            // Display the full agent response in output panel (like bio commands do)
            if (continueResponse.raw_response) {
              this._appendToOutput(continueResponse.raw_response, 'output');
            } else if (continueResponse.explanation) {
              this._appendToOutput(`📋 Agent suggests additional steps: ${continueResponse.explanation}`, 'system');
            }
            currentResponse = continueResponse;
            // Continue with next iteration
          } else {
            this._appendToOutput(`✅ Task completed successfully!`, 'success');
            this._updateStatus('Execution complete!', 'success');
            break;
          }
        } catch (error) {
          this._appendToOutput(`❌ Failed to check continuation: ${error}`, 'error');
          break;
        }
      }
    }
    
    if (iterationCount >= maxIterations) {
      this._appendToOutput(`⚠️ Reached maximum iterations (${maxIterations}). Stopping execution loop.`, 'error');
      this._updateStatus('Max iterations reached', 'error');
    }
  }

  /**
   * Legacy intelligent execution loop - kept for fallback
   */
  private async _intelligentExecutionLoop(originalQuery: string, initialResponse: any): Promise<void> {
    const currentNotebook = this._notebookTracker.currentWidget;
    if (!currentNotebook) {
      this._appendToOutput(`❌ No active notebook found.`, 'error');
      return;
    }

    try {
      // Ensure kernel is ready before starting execution loop
      await this._ensureKernelReady(currentNotebook);
    } catch (error) {
      this._appendToOutput(`❌ Failed to prepare kernel: ${error}`, 'error');
      return;
    }
    this._appendToOutput(`🚀 Auto-executing code for: "${originalQuery}"`, 'system');
    
    let currentResponse = initialResponse;
    let iterationCount = 0;
    const maxIterations = 3;
    
    while (iterationCount < maxIterations) {
      iterationCount++;
      this._appendToOutput(`🔄 Iteration ${iterationCount}`, 'system');
      
      if (!currentResponse.code_blocks || currentResponse.code_blocks.length === 0) {
        this._appendToOutput(`✅ No more code to execute`, 'success');
        break;
      }
      
      // Execute all code blocks in current response
      const executionResults = [];
      for (let i = 0; i < currentResponse.code_blocks.length; i++) {
        const code = currentResponse.code_blocks[i];
        this._appendToOutput(`▶️ Executing code block ${i + 1}:`, 'system');
        
        const result = await this._executeCodeBlock(code);
        executionResults.push(result);
        
        if (result.hasError) {
          this._appendToOutput(`❌ Error in block ${i + 1}:\n${result.output}`, 'error');
          
          // Send error back to agent for analysis and fix
          const fixQuery = `The code execution failed with error: ${result.output}\n\nOriginal code:\n${code}\n\nPlease analyze the error and provide a fixed version.`;
          
          try {
            this._appendToOutput(`🔧 Asking agent to fix the error...`, 'system');
            const fixResponse = await this._callPantheonAPI(fixQuery, 'error_fix');
            
            if (fixResponse.success) {
              // Display the full agent response for error fixes
              if (fixResponse.raw_response) {
                this._appendToOutput(fixResponse.raw_response, 'output');
              } else if (fixResponse.explanation) {
                this._appendToOutput(`💡 Agent analysis: ${fixResponse.explanation}`, 'system');
              }
              currentResponse = fixResponse;
              break; // Exit code block loop to retry with fixed code
            }
          } catch (error) {
            this._appendToOutput(`❌ Failed to get fix from agent: ${error}`, 'error');
            return;
          }
        } else {
          if (result.output.trim()) {
            this._appendToOutput(`📊 Block ${i + 1} Output:\n${result.output}`, 'output');
          } else {
            this._appendToOutput(`✅ Block ${i + 1} executed successfully (no output)`, 'success');
          }
        }
      }
      
      // If all blocks executed successfully, check if agent wants to continue
      const allSuccessful = executionResults.every(r => !r.hasError);
      if (allSuccessful) {
        const outputSummary = executionResults.map((r, i) => `Block ${i + 1}: ${r.output || 'No output'}`).join('\n');
        
        const continueQuery = `The code executed successfully with these results:\n${outputSummary}\n\nOriginal request was: "${originalQuery}"\n\nIs the task complete, or do you need to generate additional code to fully satisfy the request?`;
        
        try {
          this._appendToOutput(`🤔 Checking if task is complete...`, 'system');
          const continueResponse = await this._callPantheonAPI(continueQuery, 'continuation_check');
          
          if (continueResponse.success && continueResponse.code_blocks && continueResponse.code_blocks.length > 0) {
            this._appendToOutput(`📋 Agent suggests additional steps: ${continueResponse.explanation}`, 'system');
            currentResponse = continueResponse;
          } else {
            this._appendToOutput(`✅ Task completed successfully!`, 'success');
            this._updateStatus('Execution complete!', 'success');
            break;
          }
        } catch (error) {
          this._appendToOutput(`❌ Failed to check continuation: ${error}`, 'error');
          break;
        }
      }
    }
    
    if (iterationCount >= maxIterations) {
      this._appendToOutput(`⚠️ Reached maximum iterations (${maxIterations}). Stopping execution loop.`, 'error');
      this._updateStatus('Max iterations reached', 'error');
    }
  }

  /**
   * Execute a single code block and return results
   */
  private async _executeCodeBlock(code: string): Promise<{output: string, hasError: boolean, hasStreaming?: boolean, streamingResults?: Array<{output: string, hasError: boolean, timestamp: number}>}> {
    const currentNotebook = this._notebookTracker.currentWidget;
    if (!currentNotebook) {
      return { output: 'No active notebook found', hasError: true };
    }
    
    try {
      // Ensure kernel is ready before execution
      await this._ensureKernelReady(currentNotebook);
      
      const kernel = currentNotebook.sessionContext.session?.kernel;
      if (!kernel) {
        return { output: 'Kernel not available after preparation', hasError: true };
      }
      
      const future = kernel.requestExecute({
        code: code,
        silent: false,
        store_history: true
      });
      
      let output = '';
      let hasError = false;
      let executionCount = 0;
      
      // Handle all types of kernel messages with real-time streaming support
      let lastUpdateTime = Date.now();
      const streamingResults: Array<{output: string, hasError: boolean, timestamp: number}> = [];
      
      future.onIOPub = (msg: any) => {
        const msgType = msg.header.msg_type;
        
        switch (msgType) {
          case 'stream':
            if (msg.content.text) {
              output += msg.content.text;
              
              // For long-running processes, collect streaming outputs and show progress
              const now = Date.now();
              const text = msg.content.text;
              
              // Check if this looks like training/progress output
              const isProgressUpdate = text.includes('%') || 
                                     text.toLowerCase().includes('epoch') ||
                                     text.toLowerCase().includes('step') ||
                                     text.toLowerCase().includes('progress') ||
                                     text.toLowerCase().includes('loss') ||
                                     text.toLowerCase().includes('acc') ||
                                     /\d+\/\d+/.test(text) ||  // Progress like "100/1000"
                                     /\[\s*[=>\-]*\s*\]/.test(text); // Progress bars
              
              // Update streaming results more frequently for training processes
              if (now - lastUpdateTime > (isProgressUpdate ? 1000 : 3000)) {
                streamingResults.push({
                  output: output,
                  hasError: hasError,
                  timestamp: now
                });
                lastUpdateTime = now;
                
                // Show progress in status for long-running tasks
                if (isProgressUpdate) {
                  const cleanText = text.replace(/\r/g, '').trim().split('\n').pop() || text;
                  this._appendToStatusOutput(`📊 ${cleanText.slice(0, 100)}`, 'status');
                }
              }
            }
            break;
            
          case 'execute_result':
            executionCount = msg.content.execution_count;
            if (msg.content.data) {
              // Handle different output formats
              if (msg.content.data['text/plain']) {
                output += msg.content.data['text/plain'];
              } else if (msg.content.data['text/html']) {
                output += `[HTML Output: ${msg.content.data['text/html'].slice(0, 100)}...]`;
              } else if (msg.content.data['image/png']) {
                output += '[PNG Image Generated]';
              }
            }
            break;
            
          case 'display_data':
            if (msg.content.data) {
              if (msg.content.data['text/plain']) {
                output += msg.content.data['text/plain'];
              } else if (msg.content.data['image/png']) {
                output += '[Display: PNG Image]';
              }
            }
            break;
            
          case 'error':
            hasError = true;
            const errorOutput = [];
            if (msg.content.ename) {
              errorOutput.push(`${msg.content.ename}: ${msg.content.evalue}`);
            }
            if (msg.content.traceback && msg.content.traceback.length > 0) {
              // Clean up ANSI escape codes from traceback
              const cleanTraceback = msg.content.traceback.map((line: string) => 
                line.replace(/\u001b\[[0-9;]*m/g, '')
              );
              errorOutput.push(...cleanTraceback);
            }
            output += errorOutput.join('\n');
            break;
            
          case 'status':
            // Kernel status changes (busy/idle)
            break;
            
          default:
            console.log(`Unhandled message type: ${msgType}`, msg);
        }
      };
      
      // Wait for execution to complete with adaptive timeout
      const executionPromise = future.done;
      
      // Check if this is likely a long-running training task
      const isLongRunningTask = code.toLowerCase().includes('fit(') || 
                               code.toLowerCase().includes('train') ||
                               code.toLowerCase().includes('epoch') ||
                               code.toLowerCase().includes('model.compile') ||
                               code.toLowerCase().includes('neural') ||
                               code.toLowerCase().includes('deep') ||
                               code.toLowerCase().includes('learning') ||
                               streamingResults.length > 5; // Has been streaming for a while
      
      const timeoutDuration = isLongRunningTask ? 1800000 : 120000; // 30 min vs 2 min
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error(`Execution timeout (${isLongRunningTask ? '30min' : '2min'})`)), timeoutDuration);
      });
      
      try {
        await Promise.race([executionPromise, timeoutPromise]);
      } catch (error) {
        // If timeout, try to interrupt the kernel
        if (error instanceof Error && error.message.includes('timeout')) {
          console.log('Execution timed out, attempting to interrupt kernel...');
          try {
            await kernel.interrupt();
          } catch (interruptError) {
            console.error('Failed to interrupt kernel:', interruptError);
          }
        }
        throw error;
      }
      
      // Clean up output
      output = output.trim();
      
      // Add streaming results info for long-running tasks
      const finalOutput = output || `[Execution completed${executionCount ? ` (${executionCount})` : ''}]`;
      const hasStreaming = streamingResults.length > 0;
      
      return { 
        output: finalOutput,
        hasError,
        hasStreaming,
        streamingResults: hasStreaming ? streamingResults : undefined
      };
      
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      return { 
        output: `Execution error: ${errorMsg}`, 
        hasError: true 
      };
    }
  }

  /**
   * Get CSRF token from page
   */
  private _getCSRFToken(): string {
    // Try to get CSRF token from various sources
    const tokenMeta = document.querySelector('meta[name="_xsrf"]');
    if (tokenMeta) {
      return (tokenMeta as HTMLMetaElement).content;
    }
    
    // Try from cookie
    const cookies = document.cookie.split(';');
    for (const cookie of cookies) {
      const [name, value] = cookie.trim().split('=');
      if (name === '_xsrf') {
        return decodeURIComponent(value);
      }
    }
    
    // Try from window
    if ((window as any)._xsrf) {
      return (window as any)._xsrf;
    }
    
    return '';
  }

  /**
   * Handle cell execution errors with intelligent retry logic
   */
  private async _handleCellError(
    notebook: NotebookPanel, 
    cellIndex: number, 
    originalCode: string, 
    errorOutput: string,
    blockNumber: number
  ): Promise<boolean> {
    try {
      this._appendToStatusOutput(`🔧 Attempting to fix error in cell ${cellIndex + 1}...`, 'status');
      
      // Prepare error context for agent
      const errorContext = `The following code block (block ${blockNumber}) failed with an error:

**Original Code:**
\`\`\`python
${originalCode}
\`\`\`

**Error Output:**
\`\`\`
${errorOutput}
\`\`\`

Please analyze the error and provide a corrected version of the code. If the error is due to missing dependencies or data files, please provide installation instructions or alternative approaches. Respond with only the fixed code block.`;

      // Get notebook path
      const notebookPath = notebook.context.path;
      
      // Call Pantheon API to get fixed code
      this._appendToStatusOutput(`🤖 Asking Pantheon agent to fix the error...`, 'status');
      const response = await this._callPantheonAPI(errorContext, notebookPath);
      
      if (response.success && response.code_blocks && response.code_blocks.length > 0) {
        const fixedCode = response.code_blocks[0].code;
        
        if (fixedCode && fixedCode.trim() !== originalCode.trim()) {
          this._appendToStatusOutput(`✨ Agent provided a fix. Updating cell ${cellIndex + 1}...`, 'success');
          
          // Update the cell with fixed code
          this._updateCellContent(notebook, cellIndex, fixedCode);
          
          // Execute the fixed cell
          this._appendToStatusOutput(`🔄 Re-executing fixed cell ${cellIndex + 1}...`, 'status');
          const retryResult = await this._executeCellInNotebook(notebook, cellIndex);
          
          if (retryResult.hasError) {
            this._appendToStatusOutput(`❌ Fixed code still has errors: ${retryResult.output}`, 'error');
            
            // Ask user for guidance on how to fix the persisting error
            return await this._askUserForFixGuidance(notebook, cellIndex, fixedCode, retryResult.output);
          } else {
            this._appendToStatusOutput(`✅ Cell ${cellIndex + 1} fixed and executed successfully!`, 'success');
            if (retryResult.output && retryResult.output.trim()) {
              this._appendToOutput(`📊 Fixed Output: ${retryResult.output.slice(0, 200)}${retryResult.output.length > 200 ? '...' : ''}`, 'output');
            }
            return true; // Continue with next blocks
          }
        } else {
          this._appendToStatusOutput(`🤷 Agent couldn't provide a meaningful fix`, 'error');
          return await this._askUserForFixGuidance(notebook, cellIndex, originalCode, errorOutput);
        }
      } else {
        this._appendToStatusOutput(`❌ Failed to get fix from agent: ${response.error || 'No response'}`, 'error');
        return await this._askUserForFixGuidance(notebook, cellIndex, originalCode, errorOutput);
      }
    } catch (error) {
      this._appendToStatusOutput(`❌ Error while trying to fix cell: ${error}`, 'error');
      return await this._askUserForFixGuidance(notebook, cellIndex, originalCode, errorOutput);
    }
  }

  /**
   * Ask user for guidance on how to fix the error
   */
  private async _askUserForFixGuidance(
    notebook: NotebookPanel, 
    cellIndex: number, 
    originalCode: string, 
    errorOutput: string
  ): Promise<boolean> {
    return new Promise((resolve) => {
      // Enable input and change state to waiting for user response
      this._updateStatus('Waiting for your guidance...', 'error');
      this._inputElement.disabled = false;
      this._inputElement.placeholder = 'Describe how to fix this error, or type "continue"/"stop"...';
      
      // Show error in output
      this._appendToOutput(`⚠️ Cell execution failed. Error details:`, 'error');
      this._appendToOutput(`${errorOutput.slice(0, 500)}${errorOutput.length > 500 ? '...' : ''}`, 'error');
      this._appendToOutput(`💬 How should I fix this?`, 'system');
      this._appendToOutput(`• Describe the solution (e.g., "use pandas instead of numpy")`, 'system');
      this._appendToOutput(`• Type "continue" to skip and proceed with remaining code`, 'system');
      this._appendToOutput(`• Type "stop" to halt execution`, 'system');
      
      // Store current handler and replace with error response handler
      const originalHandler = this._currentQueryHandler;
      
      this._currentQueryHandler = async (input: string) => {
        const command = input.toLowerCase().trim();
        
        // First, always show the user's input as part of the conversation
        this._appendToOutput(`> ${input}`, 'user-input');
        
        if (command === 'continue') {
          this._appendToOutput(`➡️ Continuing with remaining code blocks...`, 'success');
          this._resetInputState();
          this._currentQueryHandler = originalHandler;
          resolve(true);
        } else if (command === 'stop') {
          this._appendToOutput(`⏹️ Execution stopped by user`, 'error');
          this._resetInputState();
          this._currentQueryHandler = originalHandler;
          resolve(false);
        } else {
          // User provided custom fix instructions
          this._appendToOutput(`🤖 Analyzing your suggestion and generating fixed code...`, 'system');
          this._resetInputState();
          this._currentQueryHandler = originalHandler;
          
          // Try to fix based on user guidance
          const fixSuccess = await this._tryUserGuidedFix(notebook, cellIndex, originalCode, errorOutput, input);
          resolve(fixSuccess);
        }
      };
      
      // Focus input for immediate user interaction
      this._inputElement.focus();
    });
  }

  /**
   * Try to fix the code based on user's guidance
   */
  private async _tryUserGuidedFix(
    notebook: NotebookPanel, 
    cellIndex: number, 
    originalCode: string, 
    errorOutput: string,
    userGuidance: string
  ): Promise<boolean> {
    try {
      // Prepare enhanced error context with user guidance
      const guidedFixContext = `The following code failed with an error:

**Original Code:**
\`\`\`python
${originalCode}
\`\`\`

**Error Output:**
\`\`\`
${errorOutput}
\`\`\`

**User's Fix Guidance:**
"${userGuidance}"

Please analyze the error and the user's guidance, then provide a corrected version of the code that addresses both the error and incorporates the user's suggestions. Respond with only the fixed Python code block.`;

      // Get notebook path
      const notebookPath = notebook.context.path;
      
      // Call Pantheon API to get user-guided fix
      this._appendToStatusOutput(`🤖 Generating fix based on your guidance...`, 'status');
      const response = await this._callPantheonAPI(guidedFixContext, notebookPath);
      
      if (response.success && response.code_blocks && response.code_blocks.length > 0) {
        const fixedCode = response.code_blocks[0].code;
        
        if (fixedCode && fixedCode.trim() !== originalCode.trim()) {
          this._appendToStatusOutput(`✨ Generated fix based on your guidance. Updating cell ${cellIndex + 1}...`, 'success');
          
          // Update the cell with user-guided fix
          this._updateCellContent(notebook, cellIndex, fixedCode);
          
          // Execute the fixed cell
          this._appendToStatusOutput(`🔄 Re-executing user-guided fix for cell ${cellIndex + 1}...`, 'status');
          const retryResult = await this._executeCellInNotebook(notebook, cellIndex);
          
          if (retryResult.hasError) {
            this._appendToStatusOutput(`❌ User-guided fix still has errors: ${retryResult.output}`, 'error');
            
            // Ask user for more guidance or to continue
            return await this._askUserForFixGuidance(notebook, cellIndex, fixedCode, retryResult.output);
          } else {
            this._appendToStatusOutput(`✅ Cell ${cellIndex + 1} fixed with your guidance and executed successfully!`, 'success');
            if (retryResult.output && retryResult.output.trim()) {
              this._appendToOutput(`📊 Fixed Output: ${retryResult.output.slice(0, 200)}${retryResult.output.length > 200 ? '...' : ''}`, 'output');
            }
            return true; // Continue with next blocks
          }
        } else {
          this._appendToOutput(`🤷 Could not generate a meaningful fix from your guidance. Please try a different approach.`, 'error');
          return await this._askUserForFixGuidance(notebook, cellIndex, originalCode, errorOutput);
        }
      } else {
        this._appendToOutput(`❌ Failed to generate fix: ${response.error || 'No response'}`, 'error');
        return await this._askUserForFixGuidance(notebook, cellIndex, originalCode, errorOutput);
      }
    } catch (error) {
      this._appendToOutput(`❌ Error while generating user-guided fix: ${error}`, 'error');
      return await this._askUserForFixGuidance(notebook, cellIndex, originalCode, errorOutput);
    }
  }

  /**
   * Reset input state
   */
  private _resetInputState(): void {
    this._inputElement.disabled = false;
    this._inputElement.placeholder = 'Ask me anything about your code...';
    this._updateStatus('Ready', 'ready');
  }

  /**
   * Update cell content with new code
   */
  private _updateCellContent(notebook: NotebookPanel, cellIndex: number, newCode: string): void {
    const cell = notebook.content.widgets[cellIndex];
    if (cell && cell.model.type === 'code') {
      const codeCell = cell as CodeCell;
      codeCell.model.sharedModel.setSource(newCode);
    }
  }

  // Context management for incremental updates
  private _lastContextHash: string = '';
  private _lastCellHashes: Map<number, string> = new Map();
  private _conversationCount: number = 0;
  private _lastSentCells: Set<number> = new Set();

  /**
   * Calculate hash for a cell based on source and outputs
   */
  private _calculateCellHash(cellInfo: any): string {
    const source = cellInfo.source || '';
    const outputsStr = JSON.stringify(cellInfo.outputs || []);
    const executionCount = cellInfo.executionCount || 0;
    const combinedStr = `${source}|${outputsStr}|${executionCount}`;
    
    // Simple hash function
    let hash = 0;
    for (let i = 0; i < combinedStr.length; i++) {
      const char = combinedStr.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return hash.toString();
  }

  /**
   * Detect changes in notebook context and return incremental update info
   */
  private _detectContextChanges(context: any): any {
    const cells = context.cells || [];
    const changedCells: any[] = [];
    const newCells: any[] = [];
    const currentCellHashes = new Map<number, string>();
    const isFirstConversation = this._conversationCount === 0;
    
    console.log(`🔍 Detecting changes. First conversation: ${isFirstConversation}, Previous cells: ${this._lastCellHashes.size}`);
    
    // Check each cell for changes
    for (const cell of cells) {
      const cellIndex = cell.index;
      const cellHash = this._calculateCellHash(cell);
      currentCellHashes.set(cellIndex, cellHash);
      
      const previousHash = this._lastCellHashes.get(cellIndex);
      
      if (isFirstConversation || !this._lastSentCells.has(cellIndex)) {
        // First conversation or new cell - include all
        newCells.push({...cell, changeType: 'new'});
        console.log(`📝 New cell ${cellIndex} (first: ${isFirstConversation})`);
      } else if (previousHash !== cellHash) {
        // Cell has changed
        changedCells.push({...cell, changeType: 'modified'});
        console.log(`✏️ Modified cell ${cellIndex} (${previousHash?.slice(0,8)} -> ${cellHash.slice(0,8)})`);
      } else {
        console.log(`✅ Unchanged cell ${cellIndex}`);
      }
    }
    
    // Update state
    this._lastCellHashes = currentCellHashes;
    this._lastSentCells = new Set(cells.map((c: any) => c.index));
    
    return {
      isFirstConversation,
      hasChanges: isFirstConversation || changedCells.length > 0 || newCells.length > 0,
      changedCells,
      newCells,
      totalCells: cells.length,
      currentCellIndex: context.currentCellIndex,
      hasOutputs: context.hasOutputs
    };
  }

  /**
   * Collect raw notebook context for agent analysis with incremental updates
   */
  private _collectNotebookContext(notebook: any, maxCells: number = 50): any {
    console.log('🔥 CONTEXT COLLECTION START v0.2.0 - INCREMENTAL UPDATES 🔥');
    
    try {
      // Validate notebook input
      if (!notebook) {
        console.log('❌ No notebook provided');
        return {
          totalCells: 0,
          currentCellIndex: -1,
          cells: [],
          message: "No notebook available"
        };
      }

      // Initialize context
      const context: any = {
        cells: [],
        totalCells: 0,
        currentCellIndex: -1,
        hasOutputs: false,
        message: "Raw notebook content for agent analysis"
      };

      // Try to get current cell index safely
      try {
        context.currentCellIndex = notebook.content?.activeCellIndex || -1;
      } catch (e) {
        console.log('Warning: Could not get active cell index');
      }

      // Get cells with multiple fallback methods
      let cells = null;
      
      // Method 1: Standard access
      try {
        if (notebook.content?.model?.cells) {
          cells = notebook.content.model.cells;
          console.log(`Found ${cells.length || 0} cells via content.model.cells`);
        }
      } catch (e) {
        console.log('Method 1 failed:', (e as Error).message);
      }
      
      // Method 2: Alternative access
      if (!cells) {
        try {
          if (notebook.model?.cells) {
            cells = notebook.model.cells;
            console.log(`Found ${cells.length || 0} cells via model.cells`);
          }
        } catch (e) {
          console.log('Method 2 failed:', (e as Error).message);
        }
      }

      // If no cells found, return empty context
      if (!cells) {
        console.log('❌ No cells found in notebook');
        return context;
      }

      // Get total count safely
      context.totalCells = cells.length || 0;
      console.log(`Processing ${context.totalCells} cells`);

      // Limit cells to process
      const cellsToProcess = Math.min(context.totalCells, maxCells);
      
      // Process each cell
      for (let i = 0; i < cellsToProcess; i++) {
        try {
          const cell = cells.get ? cells.get(i) : cells[i];
          if (!cell) {
            console.log(`Cell ${i} is null, skipping`);
            continue;
          }

          // Extract basic cell info
          const cellInfo: any = {
            index: i,
            type: cell.type || 'unknown',
            isActive: i === context.currentCellIndex
          };

          // Get cell source safely
          let source = '';
          console.log(`Cell ${i} debug:`, {
            hasSource: !!cell.source,
            sourceType: typeof cell.source,
            hasModel: !!cell.model,
            modelKeys: cell.model ? Object.keys(cell.model) : [],
            hasSharedModel: !!cell.sharedModel,
            sharedModelKeys: cell.sharedModel ? Object.keys(cell.sharedModel) : []
          });
          
          if (cell.source) {
            source = cell.source;
          } else if (cell.model?.source?.text) {
            source = cell.model.source.text;
          } else if (cell.model?.value?.text) {
            source = cell.model.value.text;
          } else if (cell.sharedModel?.source) {
            source = cell.sharedModel.source;
          } else if (cell.model?.sharedModel?.source) {
            source = cell.model.sharedModel.source;
          }
          cellInfo.source = source;

          // Get execution info for code cells
          if (cell.type === 'code') {
            // Execution count
            const executionCount = cell.executionCount || cell.model?.executionCount;
            if (executionCount !== null && executionCount !== undefined) {
              cellInfo.executionCount = executionCount;
            }

            // Outputs - get raw content for agent analysis
            try {
              const outputs = cell.outputs || cell.model?.outputs;
              if (outputs && outputs.length > 0) {
                context.hasOutputs = true;
                cellInfo.hasOutputs = true;
                cellInfo.outputCount = outputs.length;
                
                // Include ALL outputs with FULL content - no truncation
                cellInfo.outputs = [];
                
                for (let j = 0; j < outputs.length; j++) {
                  const output = outputs.get ? outputs.get(j) : outputs[j];
                  if (output) {
                    const outputInfo: any = { 
                      type: output.type,
                      index: j 
                    };
                    
                    // Include FULL text content - no truncation
                    if (output.text) {
                      outputInfo.text = typeof output.text === 'string' ? 
                        output.text : String(output.text);
                    }
                    
                    // Include full data content if available
                    if (output.data) {
                      outputInfo.hasData = true;
                      outputInfo.data = output.data;
                    }
                    
                    // Include full error content if available
                    if (output.traceback) {
                      outputInfo.hasError = true;
                      outputInfo.traceback = output.traceback;
                    }
                    
                    cellInfo.outputs.push(outputInfo);
                  }
                }
              }
            } catch (outputError) {
              console.log(`Error processing outputs for cell ${i}:`, (outputError as Error).message);
            }
          }

          context.cells.push(cellInfo);
          
        } catch (cellError) {
          console.log(`Error processing cell ${i}:`, (cellError as Error).message);
          // Continue processing other cells
        }
      }

      console.log(`✅ Context collected: ${context.cells.length} cells processed`);
      
      // Detect changes and create incremental update info
      const changeInfo = this._detectContextChanges(context);
      
      // Create optimized context based on changes
      let optimizedContext;
      if (changeInfo.isFirstConversation) {
        // First conversation - send full context
        optimizedContext = {
          ...context,
          updateType: 'full',
          isFirstConversation: true,
          message: "Full notebook context for initial analysis"
        };
        console.log(`📤 Sending FULL context (first conversation): ${context.cells.length} cells`);
      } else if (changeInfo.hasChanges) {
        // Only send changed/new cells
        const updatedCells = [...changeInfo.newCells, ...changeInfo.changedCells];
        optimizedContext = {
          updateType: 'incremental',
          isFirstConversation: false,
          totalCells: changeInfo.totalCells,
          currentCellIndex: changeInfo.currentCellIndex,
          hasOutputs: changeInfo.hasOutputs,
          cells: updatedCells,
          changedCellsCount: changeInfo.changedCells.length,
          newCellsCount: changeInfo.newCells.length,
          message: `Incremental update: ${changeInfo.changedCells.length} modified, ${changeInfo.newCells.length} new cells`
        };
        console.log(`📤 Sending INCREMENTAL context: ${updatedCells.length} cells (${changeInfo.changedCells.length} modified, ${changeInfo.newCells.length} new)`);
      } else {
        // No changes - minimal context
        optimizedContext = {
          updateType: 'none',
          isFirstConversation: false,
          totalCells: changeInfo.totalCells,
          currentCellIndex: changeInfo.currentCellIndex,
          hasOutputs: changeInfo.hasOutputs,
          cells: [],
          message: "No changes in notebook context since last interaction"
        };
        console.log(`📤 Sending NO CHANGES context - same as previous state`);
      }
      
      // Increment conversation counter
      this._conversationCount++;
      
      return optimizedContext;
      
    } catch (error) {
      console.error('❌ Error in context collection:', (error as Error).message);
      return {
        totalCells: 0,
        currentCellIndex: -1,
        cells: [],
        message: `Error collecting context: ${(error as Error).message}`
      };
    }
  }

  /**
   * Analyze notebook context to identify patterns and provide insights
   */
  private _analyzeNotebookContext(context: any): any {
    const analysis: any = {
      dataScience: false,
      webDevelopment: false,
      machineLearning: false,
      bioinformatics: false,
      visualizations: false,
      dataLoaded: false,
      hasDataFrames: false,
      hasPlots: false,
      hasErrors: false,
      suggestedLibraries: [],
      codePatterns: []
    };

    const imports = context.imports || [];
    const variables = context.variables || [];
    const functions = context.functions || [];
    const cells = context.cells || [];

    // Analyze imports to identify domain
    const importText = imports.join(' ').toLowerCase();
    
    if (importText.includes('pandas') || importText.includes('numpy') || importText.includes('scipy')) {
      analysis.dataScience = true;
      analysis.hasDataFrames = variables.some((v: string) => v.includes('df') || v.includes('data'));
    }
    
    if (importText.includes('sklearn') || importText.includes('tensorflow') || importText.includes('torch') || importText.includes('keras')) {
      analysis.machineLearning = true;
    }
    
    if (importText.includes('matplotlib') || importText.includes('seaborn') || importText.includes('plotly')) {
      analysis.visualizations = true;
      analysis.hasPlots = true;
    }
    
    if (importText.includes('bio') || importText.includes('scanpy') || importText.includes('anndata')) {
      analysis.bioinformatics = true;
    }
    
    if (importText.includes('flask') || importText.includes('django') || importText.includes('fastapi')) {
      analysis.webDevelopment = true;
    }

    // Check for data loading patterns
    const allCellSources = cells.map((c: any) => c.source?.toLowerCase() || '').join(' ');
    analysis.dataLoaded = allCellSources.includes('read_csv') || 
                         allCellSources.includes('load_data') || 
                         allCellSources.includes('pd.read');

    // Check for errors
    analysis.hasErrors = cells.some((c: any) => c.outputType === 'error');

    // Suggest relevant libraries based on context
    if (analysis.dataScience && !importText.includes('matplotlib')) {
      analysis.suggestedLibraries.push('matplotlib for plotting');
    }
    if (analysis.dataScience && !importText.includes('seaborn')) {
      analysis.suggestedLibraries.push('seaborn for statistical visualization');
    }
    if (analysis.machineLearning && !importText.includes('sklearn')) {
      analysis.suggestedLibraries.push('scikit-learn for machine learning');
    }

    // Identify code patterns
    if (variables.some((v: string) => v.toLowerCase().includes('model'))) {
      analysis.codePatterns.push('ML model development');
    }
    if (functions.some((f: string) => f.toLowerCase().includes('plot'))) {
      analysis.codePatterns.push('Custom plotting functions');
    }
    if (variables.some((v: string) => v.toLowerCase().includes('test'))) {
      analysis.codePatterns.push('Testing/validation workflow');
    }

    return analysis;
  }

  /**
   * Call integrated Pantheon API (single-process architecture)
   */
  private async _callPantheonAPI(query: string, notebookPath: string): Promise<any> {
    // Use JupyterLab's integrated Pantheon service (no external server needed)
    // Get the base URL from the current location
    const baseUrl = window.location.origin + window.location.pathname.replace(/\/lab.*/, '');
    const url = `${baseUrl}/pantheon/query`;
    
    // Get CSRF token for security
    const csrfToken = this._getCSRFToken();
    
    try {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };
      
      // Add CSRF token for security
      if (csrfToken) {
        headers['X-XSRFToken'] = csrfToken;
      }
      
      // Get workspace path from current notebook
      const notebook = this._notebookTracker.currentWidget;
      const workspacePath = notebook?.context.path ? 
        notebook.context.path.split('/').slice(0, -1).join('/') : undefined;
      
      // Collect notebook context
      const notebookContext = notebook ? this._collectNotebookContext(notebook) : null;
      
      console.log(`Calling integrated Pantheon API: ${query}`);
      if (notebookContext) {
        console.log(`📊 Notebook context: ${notebookContext.totalCells} cells, ${notebookContext.cells.length} processed, outputs: ${notebookContext.hasOutputs}`);
      }
      
      // Check if this is a complex query that needs progress tracking
      const isComplexQuery = query.toLowerCase().includes('pbmc') || 
                            query.toLowerCase().includes('analysis') ||
                            query.toLowerCase().includes('clustering') ||
                            query.length > 200;
      
      if (isComplexQuery) {
        // Show initial status
        this._appendToStatusOutput('🚀 Sending query to Pantheon agent...', 'status');
        
        // Start progress tracking
        let progressTimer: any = null;
        let elapsed = 0;
        
        progressTimer = setInterval(() => {
          elapsed += 5;
          this._appendToStatusOutput(`⏳ Processing... (${elapsed}s elapsed)`, 'status');
        }, 5000); // Update every 5 seconds
        
        try {
          const response = await fetch(url, {
            method: 'POST',
            headers,
            credentials: 'same-origin',
            body: JSON.stringify({
              query,
              notebook_path: notebookPath,
              workspace_path: workspacePath,
              notebook_context: notebookContext,
              _xsrf: csrfToken
            })
          });
          
          // Clear progress timer
          if (progressTimer) {
            clearInterval(progressTimer);
          }
          
          if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
          }
          
          // Read the response text first to handle chunked responses
          const responseText = await response.text();
          
          // Remove any keepalive spaces at the beginning
          const cleanedText = responseText.trim();
          
          // Try to parse as JSON
          const result = JSON.parse(cleanedText);
          
          this._appendToStatusOutput(`✅ Response received after ${elapsed}s`, 'success');
          console.log(`Integrated API response:`, result);
          
          return result;
        } finally {
          // Always clear the timer
          if (progressTimer) {
            clearInterval(progressTimer);
          }
        }
      } else {
        // Simple query - no progress tracking needed
        const response = await fetch(url, {
          method: 'POST',
          headers,
          credentials: 'same-origin',
          body: JSON.stringify({
            query,
            notebook_path: notebookPath,
            workspace_path: workspacePath,
            notebook_context: notebookContext,
            _xsrf: csrfToken
          })
        });
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        console.log(`Integrated API response:`, result);
        
        return result;
      }
      
    } catch (error) {
      console.error(`Integrated Pantheon API error:`, error);
      throw error;
    }
  }
  
  /**
   * Insert Pantheon response into notebook
   */
  private async _insertPantheonResponse(notebook: any, query: string, response: any): Promise<void> {
    const currentIndex = notebook.content.activeCellIndex;
    let insertIndex = currentIndex + 1;
    
    // Add explanation if available
    if (response.explanation && response.explanation.trim()) {
      notebook.model?.sharedModel.insertCell(insertIndex, {
        cell_type: 'markdown',
        source: `##  Pantheon Response\n\n**Query:** ${query}\n\n${response.explanation}`
      });
      insertIndex++;
    }
    
    // Add code blocks
    if (response.code_blocks && response.code_blocks.length > 0) {
      for (const codeBlock of response.code_blocks) {
        if (codeBlock.trim()) {
          // Insert code cell
          notebook.model?.sharedModel.insertCell(insertIndex, {
            cell_type: 'code', 
            source: codeBlock.trim()
          });
          insertIndex++;
          
          // Note: Execution will be handled by the execution loop, not here
        }
      }
    } else {
      // If no code blocks, insert a placeholder
      notebook.model?.sharedModel.insertCell(insertIndex, {
        cell_type: 'markdown',
        source: `*No executable code was generated for this query.*`
      });
    }
  }
  
  /**
   * Execute a cell at the given index using proper JupyterLab API
   */
  private async _executeCellAtIndex(notebook: any, index: number): Promise<{output: string, hasError: boolean}> {
    try {
      // Ensure kernel is available and ready
      await this._ensureKernelReady(notebook);
      
      // Set active cell to the one we want to execute
      notebook.content.activeCellIndex = index;
      
      const cell = notebook.content.activeCell;
      if (!cell) {
        return { output: 'Cell not found', hasError: true };
      }
      
      // Clear previous outputs
      cell.model.outputs.clear();
      
      // Execute using the kernel directly but wait for cell outputs
      const kernel = notebook.sessionContext.session?.kernel;
      if (!kernel) {
        return { output: 'Kernel not available', hasError: true };
      }
      
      let output = '';
      let hasError = false;
      
      // Double-check kernel is still available right before execution
      if (!kernel || kernel.isDisposed) {
        return { output: 'Kernel became unavailable before execution', hasError: true };
      }
      
      // Execute the code using kernel
      const future = kernel.requestExecute({
        code: cell.model.source,
        silent: false,
        store_history: true
      });
      
      // Listen for execution results and update cell outputs with streaming support
      let lastStreamUpdateTime = Date.now();
      const cellStreamingResults: Array<{output: string, hasError: boolean, timestamp: number}> = [];
      
      future.onIOPub = (msg: any) => {
        const msgType = msg.header.msg_type;
        
        switch (msgType) {
          case 'stream':
            if (msg.content.text) {
              output += msg.content.text;
              // Also add to cell outputs
              cell.model.outputs.add({
                output_type: 'stream',
                name: msg.content.name,
                text: msg.content.text
              });
              
              // Track streaming for training/long-running processes
              const now = Date.now();
              const text = msg.content.text;
              const isProgressUpdate = text.includes('%') || 
                                     text.toLowerCase().includes('epoch') ||
                                     text.toLowerCase().includes('step') ||
                                     text.toLowerCase().includes('loss') ||
                                     /\d+\/\d+/.test(text) ||
                                     /\[\s*[=>\-]*\s*\]/.test(text);
              
              if (now - lastStreamUpdateTime > (isProgressUpdate ? 1000 : 3000)) {
                cellStreamingResults.push({
                  output: output,
                  hasError: hasError,
                  timestamp: now
                });
                lastStreamUpdateTime = now;
              }
            }
            break;
            
          case 'execute_result':
            if (msg.content.data) {
              // Add to cell outputs
              cell.model.outputs.add({
                output_type: 'execute_result',
                execution_count: msg.content.execution_count,
                data: msg.content.data,
                metadata: msg.content.metadata || {}
              });
              
              // Extract text for our output
              if (msg.content.data['text/plain']) {
                output += msg.content.data['text/plain'];
              }
            }
            break;
            
          case 'display_data':
            if (msg.content.data) {
              // Add to cell outputs
              cell.model.outputs.add({
                output_type: 'display_data',
                data: msg.content.data,
                metadata: msg.content.metadata || {}
              });
              
              // Extract text for our output
              if (msg.content.data['text/plain']) {
                output += msg.content.data['text/plain'];
              } else if (msg.content.data['image/png']) {
                output += '[PNG Image Generated]';
              }
            }
            break;
            
          case 'error':
            hasError = true;
            const ename = msg.content.ename || 'Error';
            const evalue = msg.content.evalue || 'Unknown error occurred';
            const errorOutput = `${ename}: ${evalue}`;
            output += errorOutput;
            
            // Add to cell outputs
            cell.model.outputs.add({
              output_type: 'error',
              ename: ename,
              evalue: evalue,
              traceback: msg.content.traceback || []
            });
            
            if (msg.content.traceback && msg.content.traceback.length > 0) {
              // Clean up ANSI codes and add traceback
              const cleanTraceback = msg.content.traceback.map((line: string) => 
                typeof line === 'string' ? line.replace(/\u001b\[[0-9;]*m/g, '') : String(line)
              );
              output += '\n' + cleanTraceback.join('\n');
            }
            break;
        }
      };
      
      // Wait for execution to complete with error handling and adaptive timeout
      try {
        // Check for long-running tasks based on cell content
        const cellCode = cell.model.value.text.toLowerCase();
        const isLongTask = cellCode.includes('fit(') || 
                          cellCode.includes('train') ||
                          cellCode.includes('neural') ||
                          cellStreamingResults.length > 3;
        
        const executionPromise = future.done;
        const timeoutDuration = isLongTask ? 1800000 : 120000; // 30 min vs 2 min
        const timeoutPromise = new Promise((_, reject) => {
          setTimeout(() => reject(new Error(`Execution timeout (${isLongTask ? '30min' : '2min'})`)), timeoutDuration);
        });
        
        await Promise.race([executionPromise, timeoutPromise]);
      } catch (execError) {
        hasError = true;
        output += `Execution error: ${execError}`;
        this._appendToOutput(`⚠️ Execution failed: ${execError}`, 'error');
      }
      
      output = output.trim();
      this._appendToStatusOutput(`✅ Cell ${index + 1} executed: ${output || '[No output]'}`, hasError ? 'error' : 'success');
      
      return { output: output || '[Execution completed]', hasError };
      
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      console.warn('Could not execute cell:', error);
      this._appendToStatusOutput(`❌ Failed to execute cell ${index + 1}: ${errorMsg}`, 'error');
      return { output: `Execution failed: ${errorMsg}`, hasError: true };
    }
  }

  /**
   * Ensure kernel is ready and available with better error handling
   */
  private async _ensureKernelReady(notebook: any): Promise<void> {
    const sessionContext = notebook.sessionContext;
    const maxRetries = 3;
    let retryCount = 0;
    
    while (retryCount < maxRetries) {
      try {
        this._appendToStatusOutput(`🔄 Checking kernel status (attempt ${retryCount + 1})...`, 'status');
        
        // First, try to initialize session context if needed
        if (!sessionContext.isReady) {
          this._appendToStatusOutput('⚡ Initializing session context...', 'status');
          await sessionContext.initialize();
          await sessionContext.ready;
        }
        
        // Check if we have a valid session and kernel
        if (!sessionContext.session || !sessionContext.session.kernel) {
          this._appendToStatusOutput('🚀 Starting new kernel...', 'status');
          
          // Start a new kernel session
          await sessionContext.startKernel();
          await sessionContext.ready;
          
          // Wait a bit for kernel to fully initialize
          await new Promise(resolve => setTimeout(resolve, 2000));
        }
        
        // Verify kernel is working
        const kernel = sessionContext.session?.kernel;
        if (!kernel || kernel.isDisposed) {
          this._appendToOutput(`⚠️ Kernel not available, restarting (attempt ${retryCount + 1})...`, 'system');
          await sessionContext.restartKernel();
          await sessionContext.ready;
          await new Promise(resolve => setTimeout(resolve, 2000));
        }
        
        // Final check - test kernel with simple command
        const finalKernel = sessionContext.session?.kernel;
        if (finalKernel && !finalKernel.isDisposed) {
          try {
            this._appendToStatusOutput('🧪 Testing kernel responsiveness...', 'status');
            const testFuture = finalKernel.requestExecute({
              code: '1+1',
              silent: true,
              store_history: false
            });
            
            // Wait for test execution with timeout
            await Promise.race([
              testFuture.done,
              new Promise((_, reject) => 
                setTimeout(() => reject(new Error('Kernel test timeout')), 30000)  // 30 seconds for kernel test
              )
            ]);
            
            this._appendToStatusOutput('✅ Kernel ready and responsive!', 'success');
            return; // Success!
            
          } catch (testError) {
            this._appendToOutput(`⚠️ Kernel test failed: ${testError}`, 'system');
            retryCount++;
            continue;
          }
        }
        
        retryCount++;
        
      } catch (error) {
        this._appendToOutput(`❌ Kernel setup error (attempt ${retryCount + 1}): ${error}`, 'error');
        retryCount++;
        
        // Wait before retry
        await new Promise(resolve => setTimeout(resolve, 2000));
      }
    }
    
    throw new Error(`❌ Failed to get working kernel after ${maxRetries} attempts. Please restart the notebook kernel manually.`);
  }

  /**
   * Clear the input field
   */
  private _clearInput(): void {
    this._inputElement.value = '';
    this._inputElement.focus();
  }

  /**
   * Initialize widget in collapsed state
   */
  private _initializeCollapsedState(): void {
    const collapsedHeight = 40;
    
    // Remove widget from parent layout to free up space
    if (this._parentLayout && this._parentLayout.removeWidget) {
      this._parentLayout.removeWidget(this);
    }
    
    // Create floating header
    let floatingHeader = document.querySelector('.pantheon-floating-header') as HTMLElement;
    if (!floatingHeader) {
      floatingHeader = document.createElement('div');
      floatingHeader.className = 'pantheon-floating-header';
      document.body.appendChild(floatingHeader);
    }
    
    // Style the floating header
    floatingHeader.innerHTML = `
      <span style="font-weight: 600; color: var(--jp-ui-font-color0, #000); font-size: 14px;">🤖 Pantheon Assistant</span>
      <button class="floating-toggle-btn" style="background: none; border: none; color: var(--jp-ui-font-color2, #666); cursor: pointer; padding: 4px 8px; font-size: 12px;">▲</button>
    `;
    
    floatingHeader.style.cssText = `
      position: fixed;
      bottom: 10px;
      right: 10px;
      width: 280px;
      height: ${collapsedHeight}px;
      background: var(--jp-layout-color1, #ffffff);
      backdrop-filter: blur(4px);
      border: 1px solid var(--jp-border-color2, #e0e0e0);
      border-radius: 8px;
      box-shadow: 0 4px 12px var(--jp-shadow-penumbra-color, rgba(0,0,0,0.15));
      z-index: 9999;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 4px 8px;
      opacity: 0.95;
    `;
    
    // Add click handler to floating button
    const floatingToggleBtn = floatingHeader.querySelector('.floating-toggle-btn') as HTMLButtonElement;
    if (floatingToggleBtn) {
      floatingToggleBtn.onclick = () => {
        // Toggle the state and trigger expand
        this._isExpanded = false; // Set to false so _toggleExpanded will make it true
        this._toggleExpanded();
      };
    }
    
    // Update toggle button
    this._toggleButton.innerHTML = '▲';
    this._toggleButton.title = 'Expand widget';
    
    console.log('Pantheon widget initialized in collapsed state');
  }

  /**
   * Toggle expanded/collapsed state with bottom-up animation
   */
  private _toggleExpanded(): void {
    this._isExpanded = !this._isExpanded;
    const container = this.node.querySelector('.pantheon-container') as HTMLElement;
    const header = this.node.querySelector('.pantheon-header') as HTMLElement;
    const inputContainer = this.node.querySelector('.pantheon-input-container') as HTMLElement;
    const outputContainer = this.node.querySelector('.pantheon-output-container') as HTMLElement;
    const statusSection = this.node.querySelector('.pantheon-status-section') as HTMLElement;
    const statusBar = this.node.querySelector('.pantheon-status') as HTMLElement;
    
    if (this._isExpanded) {
      // Expanding - add widget back to layout and remove floating header
      
      // Remove floating header if it exists
      const floatingHeader = document.querySelector('.pantheon-floating-header');
      if (floatingHeader) {
        floatingHeader.remove();
      }
      
      // Add widget back to parent layout
      if (this._parentLayout && this._parentLayout.addWidget) {
        this._parentLayout.addWidget(this);
      }
      
      // Show the original widget
      this.node.style.display = 'flex'; // Show the widget
      this.node.style.height = '350px';
      this.node.style.marginTop = '0px';
      this.node.style.position = 'relative'; // Reset to relative positioning
      this.node.style.bottom = 'auto'; // Reset bottom
      this.node.style.right = 'auto'; // Reset right
      this.node.style.left = 'auto'; // Reset left
      this.node.style.width = 'auto'; // Reset width
      this.node.style.background = 'var(--jp-layout-color1, #ffffff)'; // Solid background
      this.node.style.backdropFilter = 'none'; // Remove blur
      this.node.style.border = '1px solid var(--jp-border-color2, #e0e0e0)'; // Original border
      this.node.style.borderRadius = '0'; // Remove rounded corners
      this.node.style.boxShadow = 'none'; // Remove shadow
      this.node.style.zIndex = 'auto'; // Reset z-index
      this.node.style.overflow = 'hidden'; // Reset overflow
      this.node.style.padding = '0'; // Container padding handled by inner container
      
      // Reset header to original style
      const header = this.node.querySelector('.pantheon-header') as HTMLElement;
      if (header) {
        header.style.position = 'relative';
        header.style.bottom = 'auto';
        header.style.right = 'auto';
        header.style.width = 'auto';
        header.style.height = 'auto';
        header.style.background = 'var(--jp-layout-color2, #f5f5f5)';
        header.style.backdropFilter = 'none';
        header.style.border = 'none';
        header.style.borderRadius = '0';
        header.style.boxShadow = 'none';
        header.style.zIndex = 'auto';
      }
      
      // Show all content with smooth transition
      setTimeout(() => {
        inputContainer.style.display = 'flex';
        outputContainer.style.display = 'flex';
        statusSection.style.display = 'block';
        statusBar.style.display = 'block';
        
        // Add fade-in effect
        inputContainer.style.opacity = '1';
        outputContainer.style.opacity = '1';
        statusSection.style.opacity = '1';
        statusBar.style.opacity = '1';
      }, 50);
      
      this._toggleButton.innerHTML = '▼';
      this._toggleButton.title = 'Collapse widget';
    } else {
      // Collapsing - remove widget from layout and show floating header
      const collapsedHeight = 40;
      
      // Remove widget from parent layout to free up space
      if (this._parentLayout && this._parentLayout.removeWidget) {
        this._parentLayout.removeWidget(this);
      }
      
      // Create or update floating header
      let floatingHeader = document.querySelector('.pantheon-floating-header') as HTMLElement;
      if (!floatingHeader) {
        floatingHeader = document.createElement('div');
        floatingHeader.className = 'pantheon-floating-header';
        document.body.appendChild(floatingHeader);
      }
      
      // Style the floating header
      floatingHeader.innerHTML = `
        <span style="font-weight: 600; color: var(--jp-ui-font-color0, #000); font-size: 14px;">🤖 Pantheon Assistant</span>
        <button class="floating-toggle-btn" style="background: none; border: none; color: var(--jp-ui-font-color2, #666); cursor: pointer; padding: 4px 8px; font-size: 12px;">▲</button>
      `;
      
      floatingHeader.style.cssText = `
        position: fixed;
        bottom: 10px;
        right: 10px;
        width: 280px;
        height: ${collapsedHeight}px;
        background: var(--jp-layout-color1, #ffffff);
        backdrop-filter: blur(4px);
        border: 1px solid var(--jp-border-color2, #e0e0e0);
        border-radius: 8px;
        box-shadow: 0 4px 12px var(--jp-shadow-penumbra-color, rgba(0,0,0,0.15));
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 4px 8px;
        opacity: 0.95;
      `;
      
      // Add click handler to floating button
      const floatingToggleBtn = floatingHeader.querySelector('.floating-toggle-btn') as HTMLButtonElement;
      if (floatingToggleBtn) {
        floatingToggleBtn.onclick = () => {
          // Toggle the state and trigger expand
          this._isExpanded = false; // Set to false so _toggleExpanded will make it true
          this._toggleExpanded();
        };
      }
      
      this._toggleButton.innerHTML = '▲';
      this._toggleButton.title = 'Expand widget';
    }
    
    // Add transition effects to content elements
    [inputContainer, outputContainer, statusSection, statusBar].forEach(element => {
      if (element) {
        element.style.transition = 'opacity 0.2s ease';
      }
    });
  }

  /**
   * Toggle status output window
   */
  private _toggleStatusExpanded(): void {
    this._isStatusExpanded = !this._isStatusExpanded;
    const statusOutputContainer = this.node.querySelector('.pantheon-status-output-container') as HTMLElement;
    
    if (this._isStatusExpanded) {
      statusOutputContainer.style.display = 'block';
      this._statusToggleButton.innerHTML = '▼';
      this._statusToggleButton.title = 'Hide execution status';
    } else {
      statusOutputContainer.style.display = 'none';
      this._statusToggleButton.innerHTML = '▲';
      this._statusToggleButton.title = 'Show execution status';
    }
  }

  /**
   * Navigate through query history
   */
  private _navigateHistory(direction: number): void {
    const newIndex = this._historyIndex + direction;
    if (newIndex >= 0 && newIndex < this._history.length) {
      this._historyIndex = newIndex;
      this._inputElement.value = this._history[this._historyIndex];
    } else if (newIndex >= this._history.length) {
      this._historyIndex = this._history.length;
      this._inputElement.value = '';
    }
  }

  /**
   * Update status bar
   */
  private _updateStatus(text: string, state: 'ready' | 'processing' | 'success' | 'error'): void {
    const statusText = this.node.querySelector('.pantheon-status-text');
    if (statusText) {
      statusText.textContent = text;
      statusText.className = `pantheon-status-text pantheon-status-${state}`;
    }
  }

  /**
   * Show a temporary message
   */
  private _showMessage(message: string, type: 'info' | 'error' | 'success'): void {
    console.log(`[Pantheon ${type}]:`, message);
    // TODO: Implement toast notification
  }

  /**
   * Handle widget activation
   */
  protected onActivateRequest(msg: Message): void {
    if (this._inputElement) {
      this._inputElement.focus();
    }
  }

  /**
   * Append text to the main output area (Agent interactions only)
   */
  private _appendToOutput(text: string, type: 'user-input' | 'system' | 'error' | 'success' | 'output' = 'system'): void {
    const timestamp = new Date().toLocaleTimeString();
    const colorMap = {
      'user-input': 'var(--jp-brand-color1, #2196F3)',
      'system': 'var(--jp-ui-font-color1, #000)',
      'error': '#d32f2f',
      'success': '#2e7d32',
      'output': '#666666'
    };
    
    const color = colorMap[type];
    const prefix = type === 'user-input' ? '' : `[${timestamp}] `;
    
    this._outputElement.innerHTML += `<div style="color: ${color}; margin: 2px 0;">${prefix}${text}</div>`;
    this._outputElement.scrollTop = this._outputElement.scrollHeight;
  }

  /**
   * Append text to the status output area (Notebook execution status only)
   */
  private _appendToStatusOutput(text: string, type: 'status' | 'error' | 'success' = 'status'): void {
    const timestamp = new Date().toLocaleTimeString();
    const colorMap = {
      'status': 'var(--jp-ui-font-color2, #666)',
      'error': '#d32f2f',
      'success': '#2e7d32'
    };
    
    const color = colorMap[type];
    const prefix = `[${timestamp}] `;
    
    this._statusOutputElement.innerHTML += `<div style="color: ${color}; margin: 1px 0; font-size: 10px;">${prefix}${text}</div>`;
    this._statusOutputElement.scrollTop = this._statusOutputElement.scrollHeight;
  }

  /**
   * Handle slash commands
   */
  private async _handleSlashCommand(command: string): Promise<void> {
    const parts = command.split(' ');
    const cmd = parts[0];
    const args = parts.slice(1);

    switch (cmd) {
      case '/help':
        this._showHelp();
        break;
      case '/status':
        this._showStatus();
        break;
      case '/history':
        this._showHistory();
        break;
      case '/clear':
        this._clearOutput();
        break;
      case '/model':
        await this._handleModelCommand(args);
        break;
      case '/api-key':
        await this._handleApiKeyCommand(args);
        break;
      case '/bio':
        await this._handleBioCommand(args);
        break;
      default:
        this._appendToOutput(`❌ Unknown command: ${cmd}. Type /help for available commands.`, 'error');
    }
  }

  private _showHelp(): void {
    const helpText = `
📋 PANTHEON NOTEBOOK ASSISTANT COMMANDS

🔧 BASIC COMMANDS:
• /help     - Show this help
• /status   - Show session status  
• /history  - Show command history
• /clear    - Clear output window
• /model    - Model management
• /api-key  - API key management
• /bio      - Bioinformatics analysis tools

🧬 BIO COMMANDS:
• /bio list             - List all available bio tools
• /bio atac init        - Initialize ATAC-seq analysis
• /bio scrna init       - Initialize scRNA-seq analysis  
• /bio GeneAgent TP53   - Gene analysis with AI
• /bio dock init        - Molecular docking analysis
• /bio spatial init     - Spatial transcriptomics

💡 USAGE:
• Type natural language to generate code
• Commands start with / 
• Use ↑/↓ to navigate history
• Press Ctrl+Enter to send, Enter for new line

🚀 Ready to assist with your data analysis!`;
    
    this._appendToOutput(helpText, 'system');
  }

  private _showStatus(): void {
    const notebook = this._notebookTracker.currentWidget;
    const notebookName = notebook ? notebook.context.path : 'No notebook';
    const historyCount = this._commandHistory.length;
    
    const statusText = `
📊 SESSION STATUS:
• Active notebook: ${notebookName}
• Commands executed: ${historyCount}
• History size: ${this._history.length}
• Widget state: ${this._isExpanded ? 'Expanded' : 'Collapsed'}
• Time: ${new Date().toLocaleString()}`;
    
    this._appendToOutput(statusText, 'system');
  }

  private _showHistory(): void {
    if (this._commandHistory.length === 0) {
      this._appendToOutput('📝 No command history yet.', 'system');
      return;
    }
    
    let historyText = `\n📝 COMMAND HISTORY (${this._commandHistory.length} commands):\n`;
    this._commandHistory.slice(-10).forEach((cmd, index) => {
      historyText += `${index + 1}. ${cmd}\n`;
    });
    
    this._appendToOutput(historyText, 'system');
  }

  private _clearOutput(): void {
    this._outputElement.innerHTML = `<span style="color: var(--jp-ui-font-color2, #666);"> Output cleared. Ready for new commands!</span>`;
    this._appendToOutput('✅ Output cleared', 'success');
  }

  private async _handleModelCommand(args: string[]): Promise<void> {
    try {
      if (args.length === 0 || args[0] === 'list') {
        // Get model list
        const response = await this._callModelAPI('GET', { action: 'list' });
        if (response.success) {
          this._appendToOutput(response.result, 'system');
        } else {
          this._appendToOutput(`❌ Failed to get model list: ${response.error}`, 'error');
        }
      } else if (args[0] === 'current') {
        // Get current model
        const response = await this._callModelAPI('GET', { action: 'current' });
        if (response.success) {
          this._appendToOutput(response.result, 'system');
        } else {
          this._appendToOutput(`❌ Failed to get current model: ${response.error}`, 'error');
        }
      } else {
        // Switch to new model
        const newModel = args[0];
        this._appendToOutput(`🔄 Switching to model: ${newModel}...`, 'system');
        
        const response = await this._callModelAPI('POST', { model: newModel });
        if (response.success) {
          this._appendToOutput(response.result, 'success');
          this._updateStatus('Model switched', 'success');
          
          // Clear status after 3 seconds
          setTimeout(() => {
            this._updateStatus('Ready', 'ready');
          }, 3000);
        } else {
          this._appendToOutput(`❌ Failed to switch model: ${response.error}`, 'error');
        }
      }
    } catch (error) {
      this._appendToOutput(`❌ Model command error: ${error}`, 'error');
    }
  }

  private async _handleApiKeyCommand(args: string[]): Promise<void> {
    try {
      if (args.length === 0 || args[0] === 'list') {
        // Get API key status
        const response = await this._callApiKeyAPI('GET', { action: 'list' });
        if (response.success) {
          this._appendToOutput(response.result, 'system');
        } else {
          this._appendToOutput(`❌ Failed to get API key status: ${response.error}`, 'error');
        }
      } else if (args[0] === 'status') {
        // Get detailed API key status
        const response = await this._callApiKeyAPI('GET', { action: 'status' });
        if (response.success) {
          this._appendToOutput(response.result, 'system');
        } else {
          this._appendToOutput(`❌ Failed to get API key status: ${response.error}`, 'error');
        }
      } else if (args.length >= 2) {
        // Set API key: /api-key <provider> <key> [--local]
        const provider = args[0];
        let apiKey = '';
        let saveGlobal = true;
        
        // Parse arguments to handle --local flag
        for (let i = 1; i < args.length; i++) {
          if (args[i] === '--local') {
            saveGlobal = false;
          } else {
            // Join remaining args as the API key (in case it contains spaces)
            apiKey += args[i];
            if (i < args.length - 1 && args[i + 1] !== '--local') {
              apiKey += ' ';
            }
          }
        }
        
        if (!apiKey.trim()) {
          this._appendToOutput(`❌ Please provide an API key: /api-key ${provider} <your-key> [--local]`, 'error');
          return;
        }
        
        this._appendToOutput(`🔐 Setting ${provider} API key...`, 'system');
        
        const response = await this._callApiKeyAPI('POST', {
          provider,
          api_key: apiKey.trim(),
          save_global: saveGlobal
        });
        
        if (response.success) {
          this._appendToOutput(response.result, 'success');
          this._updateStatus('API key updated', 'success');
          
          // Clear status after 3 seconds
          setTimeout(() => {
            this._updateStatus('Ready', 'ready');
          }, 3000);
        } else {
          this._appendToOutput(`❌ Failed to set API key: ${response.error}`, 'error');
        }
      } else {
        this._appendToOutput(`❌ Invalid usage. Examples:
• /api-key list - Show API key status
• /api-key status - Show detailed status
• /api-key openai sk-proj-xxx - Set OpenAI key globally
• /api-key anthropic sk-ant-xxx --local - Set Anthropic key locally`, 'error');
      }
    } catch (error) {
      this._appendToOutput(`❌ API key command error: ${error}`, 'error');
    }
  }

  /**
   * Call model management API
   */
  private async _callModelAPI(method: 'GET' | 'POST', data?: any): Promise<any> {
    const baseUrl = window.location.origin + window.location.pathname.replace(/\/lab.*/, '');
    const url = method === 'GET' ? 
      `${baseUrl}/pantheon/model${data?.action ? `?action=${data.action}` : ''}` : 
      `${baseUrl}/pantheon/model`;
    
    const csrfToken = this._getCSRFToken();
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    
    if (csrfToken) {
      headers['X-XSRFToken'] = csrfToken;
    }
    
    const requestOptions: RequestInit = {
      method,
      headers,
      credentials: 'same-origin'
    };
    
    if (method === 'POST' && data) {
      requestOptions.body = JSON.stringify({
        ...data,
        _xsrf: csrfToken
      });
    }
    
    try {
      const response = await fetch(url, requestOptions);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Model API error:', error);
      throw error;
    }
  }

  /**
   * Call API key management API
   */
  private async _callApiKeyAPI(method: 'GET' | 'POST', data?: any): Promise<any> {
    const baseUrl = window.location.origin + window.location.pathname.replace(/\/lab.*/, '');
    const url = method === 'GET' ? 
      `${baseUrl}/pantheon/api-key${data?.action ? `?action=${data.action}` : ''}` : 
      `${baseUrl}/pantheon/api-key`;
    
    const csrfToken = this._getCSRFToken();
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    
    if (csrfToken) {
      headers['X-XSRFToken'] = csrfToken;
    }
    
    const requestOptions: RequestInit = {
      method,
      headers,
      credentials: 'same-origin'
    };
    
    if (method === 'POST' && data) {
      requestOptions.body = JSON.stringify({
        ...data,
        _xsrf: csrfToken
      });
    }
    
    try {
      const response = await fetch(url, requestOptions);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API Key API error:', error);
      throw error;
    }
  }

  /**
   * Handle bio command
   */
  private async _handleBioCommand(args: string[]): Promise<void> {
    try {
      // Reconstruct the full bio command
      const bioCommand = `/bio ${args.join(' ')}`;
      
      // Show bio command is being processed
      this._appendToOutput(`🧬 Processing bio command: ${bioCommand}`, 'system');
      this._updateStatus('Processing bio analysis...', 'processing');
      
      // Send bio command directly to server
      const response = await this._queryServer(bioCommand);
      
      if (response.success) {
        // Display the complete agent response first (like normal queries)
        if (response.raw_response) {
          this._appendToOutput(response.raw_response, 'output');
        } else if (response.explanation) {
          this._appendToOutput(response.explanation, 'output');
        }
        
        // Use the same iterative execution as normal queries
        const notebook = this._notebookTracker.currentWidget;
        if (notebook) {
          // If no code_blocks, try to parse from raw_response
          if (!response.code_blocks || response.code_blocks.length === 0) {
            const blocks = this._parseResponseIntoBlocks(response);
            const codeBlocks = blocks.filter(block => block.type === 'code').map(block => ({
              language: 'python',
              code: block.content
            }));
            response.code_blocks = codeBlocks;
          }
          
          if (response.code_blocks && response.code_blocks.length > 0) {
            this._appendToOutput(`🧬 Starting bio analysis with iterative execution...`, 'system');
            // Use the notebook execution loop for iterative execution
            await this._notebookExecutionLoop(bioCommand, response, notebook);
          } else {
            this._appendToOutput(`✅ Bio command completed (no code to execute)`, 'success');
          }
        } else if (!notebook) {
          // If no notebook, just show the code in output
          if (response.code_blocks && response.code_blocks.length > 0) {
            for (const block of response.code_blocks) {
              this._appendToOutput(`\`\`\`${block.language || 'python'}\n${block.code}\n\`\`\``, 'output');
            }
          }
          this._updateStatus('Bio analysis completed (no notebook)', 'success');
        } else {
          // No code blocks, just the response was shown
          this._updateStatus('Bio analysis completed', 'success');
        }
        
        // Clear status after 3 seconds
        setTimeout(() => {
          this._updateStatus('Ready', 'ready');
        }, 3000);
      } else {
        this._appendToOutput(`❌ Bio command failed: ${response.error}`, 'error');
        this._updateStatus('Bio command failed', 'error');
        
        // Clear status after 3 seconds
        setTimeout(() => {
          this._updateStatus('Ready', 'ready');
        }, 3000);
      }
      
    } catch (error) {
      this._appendToOutput(`❌ Bio command error: ${error}`, 'error');
      console.error('Bio command error:', error);
      
      this._updateStatus('Bio command error', 'error');
      
      // Clear status after 3 seconds
      setTimeout(() => {
        this._updateStatus('Ready', 'ready');
      }, 3000);
    }
  }

  /**
   * Query server directly
   */
  private async _queryServer(query: string): Promise<any> {
    const baseUrl = window.location.origin + window.location.pathname.replace(/\/lab.*/, '');
    const url = `${baseUrl}/pantheon/query`;
    
    const notebook = this._notebookTracker.currentWidget;
    if (!notebook) {
      throw new Error('No active notebook found');
    }
    
    const csrfToken = this._getCSRFToken();
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    
    if (csrfToken) {
      headers['X-XSRFToken'] = csrfToken;
    }
    
    const notebookPath = notebook.context.path;
    const workspacePath = notebook.context.path.includes('/') ? 
      notebook.context.path.split('/').slice(0, -1).join('/') : undefined;
    
    const response = await fetch(url, {
      method: 'POST',
      headers,
      credentials: 'same-origin',
      body: JSON.stringify({
        query,
        notebook_path: notebookPath,
        workspace_path: workspacePath,
        _xsrf: csrfToken
      })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  }

  /**
   * Handle widget close
   */
  protected onCloseRequest(msg: Message): void {
    super.onCloseRequest(msg);
    this.dispose();
  }

  /**
   * Simplified code execution - just execute blocks without complex loops
   */
  private async _executeCodeBlocksSimply(codeBlocks: string[], notebook: any): Promise<void> {
    if (!codeBlocks || codeBlocks.length === 0) {
      this._appendToOutput('✅ No code to execute', 'success');
      return;
    }

    this._appendToStatusOutput(`🚀 Executing ${codeBlocks.length} code block(s)...`, 'status');
    
    try {
      await this._ensureKernelReady(notebook);
    } catch (error) {
      this._appendToOutput(`❌ Failed to prepare kernel: ${error}`, 'error');
      return;
    }

    // Execute each code block sequentially
    for (let i = 0; i < codeBlocks.length; i++) {
      const code = codeBlocks[i];
      this._appendToStatusOutput(`▶️ Executing code block ${i + 1}/${codeBlocks.length}:`, 'status');
      this._appendToOutput(`\`\`\`python\n${code}\n\`\`\``, 'system');
      
      try {
        // Insert code into a new cell in the notebook
        const cellIndex = this._insertCodeIntoNotebook(notebook, code);
        this._appendToStatusOutput(`📝 Code inserted into cell ${cellIndex + 1}`, 'success');
        
        // Execute the cell in the notebook (this will show output in the notebook)
        const result = await this._executeCellInNotebook(notebook, cellIndex);
        
        if (result.hasError) {
          this._appendToStatusOutput(`❌ Error in cell ${cellIndex + 1}:\n${result.output}`, 'error');
          break; // Stop execution on first error
        } else {
          if (result.output && result.output.trim()) {
            this._appendToStatusOutput(`✅ Cell ${cellIndex + 1} executed successfully with output`, 'success');
          } else {
            this._appendToStatusOutput(`✅ Cell ${cellIndex + 1} executed successfully (no output)`, 'success');
          }
        }
      } catch (error) {
        this._appendToOutput(`❌ Execution error in block ${i + 1}: ${error}`, 'error');
        break; // Stop execution on error
      }
      
      // Small delay between executions to avoid overwhelming the kernel
      if (i < codeBlocks.length - 1) {
        await new Promise(resolve => setTimeout(resolve, 100));
      }
    }
    
    this._appendToOutput('🏁 Code execution completed', 'success');
    this._updateStatus('Execution complete', 'success');
  }

  /**
   * Parse response into ordered blocks of markdown and code
   */
  private _parseResponseIntoBlocks(response: any): Array<{type: string, content: string}> {
    const blocks: Array<{type: string, content: string}> = [];
    
    // Check if we have structured code_blocks (guaranteed complete)
    const hasCodeBlocks = response.code_blocks && response.code_blocks.length > 0;
    const hasExplanation = response.explanation && response.explanation.trim();
    
    if (hasCodeBlocks) {
      // Case 1: We have code blocks, use them for complete code but still parse raw_response for proper ordering
      const rawContent = response.raw_response || '';
      
      if (rawContent && !rawContent.includes('(response truncated)')) {
        // If raw_response is complete, use it for proper ordering
        const codeBlockRegex = /```(?:python)?\n([\s\S]*?)\n```/g;
        let lastIndex = 0;
        let match;
        let codeBlockIndex = 0;
        
        while ((match = codeBlockRegex.exec(rawContent)) !== null) {
          // Add markdown before this code block
          const markdownContent = rawContent.substring(lastIndex, match.index).trim();
          if (markdownContent) {
            blocks.push({ type: 'markdown', content: markdownContent });
          }
          
          // Use the complete code from code_blocks instead of potentially truncated raw content
          if (codeBlockIndex < response.code_blocks.length) {
            const codeBlock = response.code_blocks[codeBlockIndex];
            const codeContent = typeof codeBlock === 'string' ? codeBlock.trim() : codeBlock.code?.trim();
            if (codeContent) {
              blocks.push({ type: 'code', content: codeContent });
            }
            codeBlockIndex++;
          }
          
          lastIndex = match.index + match[0].length;
        }
        
        // Add any remaining markdown after the last code block
        const remainingMarkdown = rawContent.substring(lastIndex).trim();
        if (remainingMarkdown) {
          blocks.push({ type: 'markdown', content: remainingMarkdown });
        }
      } else {
        // Fallback: raw_response truncated, use explanation + code_blocks
        if (hasExplanation) {
          blocks.push({ type: 'markdown', content: response.explanation.trim() });
        }
        
        for (const codeBlock of response.code_blocks) {
          const codeContent = typeof codeBlock === 'string' ? codeBlock.trim() : codeBlock.code?.trim();
          if (codeContent) {
            blocks.push({ type: 'code', content: codeContent });
          }
        }
      }
    } else if (hasExplanation) {
      // Case 2: No code blocks, just explanation (text-only response)
      blocks.push({ type: 'markdown', content: response.explanation.trim() });
    } else {
      // Case 3: Parse raw_response as fallback
      const rawContent = response.raw_response || '';
      
      if (rawContent) {
        const codeBlockRegex = /```(?:python)?\n([\s\S]*?)\n```/g;
        let lastIndex = 0;
        let match;
        
        while ((match = codeBlockRegex.exec(rawContent)) !== null) {
          // Add markdown before this code block
          const markdownContent = rawContent.substring(lastIndex, match.index).trim();
          if (markdownContent) {
            blocks.push({ type: 'markdown', content: markdownContent });
          }
          
          // Add the code block
          const codeContent = match[1].trim();
          if (codeContent) {
            blocks.push({ type: 'code', content: codeContent });
          }
          
          lastIndex = match.index + match[0].length;
        }
        
        // Add any remaining markdown after the last code block
        const remainingMarkdown = rawContent.substring(lastIndex).trim();
        if (remainingMarkdown && !remainingMarkdown.includes('(response truncated)')) {
          blocks.push({ type: 'markdown', content: remainingMarkdown });
        }
      }
    }
    
    return blocks;
  }
  
  /**
   * Insert markdown into a new notebook cell and return the cell index
   */
  private _insertMarkdownIntoNotebook(notebook: any, markdown: string): number {
    const notebookPanel = notebook.content;
    const model = notebookPanel.model;
    const currentIndex = notebookPanel.activeCellIndex;
    
    if (!model) {
      throw new Error('Notebook model not available');
    }
    
    // Use the shared model to insert cell directly
    const insertIndex = currentIndex + 1;
    
    // Insert markdown cell using shared model
    model.sharedModel.insertCell(insertIndex, {
      cell_type: 'markdown',
      source: markdown,
      metadata: {}
    });
    
    // Update active cell to the newly inserted cell
    notebookPanel.activeCellIndex = insertIndex;
    
    return insertIndex;
  }
  
  /**
   * Insert code into a new notebook cell and return the cell index
   */
  private _insertCodeIntoNotebook(notebook: any, code: string): number {
    const notebookPanel = notebook.content;
    const model = notebookPanel.model;
    const currentIndex = notebookPanel.activeCellIndex;
    
    if (!model) {
      throw new Error('Notebook model not available');
    }
    
    // Use the shared model to insert cell directly
    const insertIndex = currentIndex + 1;
    
    // Insert cell using shared model
    model.sharedModel.insertCell(insertIndex, {
      cell_type: 'code',
      source: code,
      metadata: {}
    });
    
    // Make the new cell active
    notebookPanel.activeCellIndex = insertIndex;
    
    return insertIndex;
  }

  /**
   * Execute a cell in the notebook using proper JupyterLab execution mechanism
   */
  private async _executeCellInNotebook(notebook: any, cellIndex: number): Promise<{output: string, hasError: boolean}> {
    try {
      // Set the active cell to the one we want to execute
      notebook.content.activeCellIndex = cellIndex;
      const cell = notebook.content.activeCell;
      
      if (!cell) {
        return { output: 'Cell not found', hasError: true };
      }

      this._appendToStatusOutput(`🔧 Preparing to execute cell ${cellIndex + 1}...`, 'status');
      
      // Ensure kernel is ready
      await this._ensureKernelReady(notebook);
      
      // Clear previous outputs
      cell.model.outputs.clear();
      
      // Use the NotebookActions to execute the cell properly
      this._appendToStatusOutput(`▶️ Executing cell ${cellIndex + 1} with NotebookActions...`, 'status');
      const { NotebookActions } = await import('@jupyterlab/notebook');
      
      // Execute the cell using JupyterLab's NotebookActions
      const promise = NotebookActions.run(notebook.content, notebook.sessionContext);
      
      // Wait for execution with appropriate timeout for data processing and imports
      await Promise.race([
        promise,
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Cell execution timeout')), 180000)  // 3 minutes for heavy imports/processing
        )
      ]);
      
      // Wait a bit more for outputs to be processed
      this._appendToStatusOutput(`⏳ Waiting for execution results...`, 'status');
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      let output = '';
      let hasError = false;
      
      // Collect outputs from the cell
      const outputs = cell.model.outputs;
      this._appendToStatusOutput(`📊 Found ${outputs.length} output(s) from cell`, 'status');
      
      for (let i = 0; i < outputs.length; i++) {
        const outputData = outputs.get(i);
        
        if (outputData.type === 'stream') {
          output += outputData.text;
        } else if (outputData.type === 'execute_result' || outputData.type === 'display_data') {
          if (outputData.data && outputData.data['text/plain']) {
            output += outputData.data['text/plain'];
          } else if (outputData.data && outputData.data['image/png']) {
            output += '[PNG Image Generated]';
          }
        } else if (outputData.type === 'error') {
          hasError = true;
          const ename = outputData.ename || 'Error';
          const evalue = outputData.evalue || 'Unknown error occurred';
          output += `${ename}: ${evalue}`;
          if (outputData.traceback && outputData.traceback.length > 0) {
            const cleanTraceback = outputData.traceback.map((line: any) => 
              typeof line === 'string' ? line.replace(/\u001b\[[0-9;]*m/g, '') : String(line)
            );
            output += '\n' + cleanTraceback.join('\n');
          }
        }
      }
      
      const finalOutput = output.trim() || '[No output]';
      this._appendToStatusOutput(`✅ Cell execution complete. Output: ${finalOutput.slice(0, 100)}${finalOutput.length > 100 ? '...' : ''}`, hasError ? 'error' : 'success');
      
      return { output: finalOutput, hasError };
      
    } catch (error) {
      this._appendToStatusOutput(`❌ Cell execution failed: ${error}`, 'error');
      return { output: `Execution error: ${error}`, hasError: true };
    }
  }
}