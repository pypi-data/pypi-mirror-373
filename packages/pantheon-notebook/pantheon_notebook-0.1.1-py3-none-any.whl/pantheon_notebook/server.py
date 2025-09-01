"""Pantheon Notebook Server Extension - Integrated Agent Architecture"""

import asyncio
import json
import re
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import time
from jupyter_server.extension.application import ExtensionApp
from jupyter_server.base.handlers import JupyterHandler
from tornado import web
from tornado.websocket import WebSocketHandler

# Configure logging
logger = logging.getLogger(__name__)

# Add pantheon paths
pantheon_cli_path = Path(__file__).parent.parent.parent / "pantheon-cli"
pantheon_agents_path = Path(__file__).parent.parent.parent / "pantheon-agents"
pantheon_toolsets_path = Path(__file__).parent.parent.parent / "pantheon-toolsets" 

sys.path.insert(0, str(pantheon_cli_path))
sys.path.insert(0, str(pantheon_agents_path))
sys.path.insert(0, str(pantheon_toolsets_path))

try:
    from pantheon.agent import Agent
    from pantheon.toolsets.file_manager import FileManagerToolSet
    from pantheon.toolsets.notebook import NotebookToolSet
    from pantheon.toolsets.shell import ShellToolSet
    from pantheon.toolsets.file_editor import FileEditorToolSet
    from pantheon.toolsets.code_search import CodeSearchToolSet
    from pantheon.toolsets.todo import TodoToolSet
    from pantheon.toolsets.web import WebToolSet
    # Import API key manager and model manager for global config compatibility
    from pantheon_cli.cli.manager.api_key_manager import APIKeyManager
    from pantheon_cli.cli.manager.model_manager import ModelManager
    from pantheon_cli.repl.bio_handler import BioCommandHandler
    # Import the actual bio toolset manager
    from pantheon.toolsets.bio import BioToolsetManager
    PANTHEON_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import pantheon modules: {e}")
    PANTHEON_AVAILABLE = False


class PantheonAgentManager:
    """Manages integrated pantheon agent instances for notebooks"""
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.last_error: Optional[Dict[str, Any]] = None  # Store last error for better user feedback
        
        # Initialize API key manager and model manager like pantheon-cli does
        if PANTHEON_AVAILABLE:
            try:
                # Use same config paths as pantheon-cli
                local_config_path = Path.cwd() / ".pantheon_config.json"
                self.api_key_manager = APIKeyManager(local_config_path)
                self.model_manager = ModelManager(local_config_path, self.api_key_manager)
                # Initialize bio command handler
                from rich.console import Console
                self.bio_handler = BioCommandHandler(Console())
                # Sync API keys to environment variables
                self.api_key_manager.sync_environment_variables()
                print("✅ Loaded Pantheon API key, model and bio modules configuration")
            except Exception as e:
                print(f"Warning: Could not initialize managers: {e}")
                self.api_key_manager = None
                self.model_manager = None
                self.bio_handler = None
        else:
            self.api_key_manager = None
            self.model_manager = None
            self.bio_handler = None
    
    def get_or_create_agent(self, notebook_path: str, workspace_path: Optional[Path] = None, retry_count: int = 0) -> Optional[Agent]:
        """Get or create agent for a specific notebook with full toolset integration
        
        Args:
            notebook_path: Path to the notebook
            workspace_path: Optional workspace path
            retry_count: Number of retry attempts (internal use)
        """
        if not PANTHEON_AVAILABLE:
            return None
            
        # Check if agent exists and is healthy
        if notebook_path in self.agents:
            agent = self.agents[notebook_path]
            if self._is_agent_healthy(agent):
                return agent
            else:
                # Agent exists but unhealthy, remove it
                print(f"⚠️ Agent for {notebook_path} is unhealthy, recreating...")
                del self.agents[notebook_path]
                if notebook_path in self.sessions:
                    del self.sessions[notebook_path]
        
        # Create new agent
        if notebook_path not in self.agents:
            try:
                # Use workspace path or current directory
                if workspace_path is None:
                    workspace_path = Path.cwd()
                
                # Create agent with minimal toolset first for faster initialization
                # Use current model from model manager, fallback to gpt-4o-mini (more reliable)
                current_model = self.model_manager.current_model if self.model_manager else "gpt-4o-mini"
                print(f"🚀 Creating agent with model: {current_model}")
                start_time = time.time()
                
                agent = Agent(
                    name="PantheonNotebookAssistant",
                    model=current_model,
                    instructions=self._get_notebook_instructions()
                )
                
                print(f"✅ Agent created in {time.time() - start_time:.1f}s")
                
                # Set agent reference in model manager for model switching (like pantheon-cli)
                if self.model_manager:
                    self.model_manager.set_agent(agent)
                
                # Attach managers to agent for REPL access (like pantheon-cli)
                agent._model_manager = self.model_manager
                agent._api_key_manager = self.api_key_manager
                
                print("🔧 Adding essential toolsets...")
                toolset_start = time.time()
                
                # Add essential toolsets first (fast ones)
                file_editor = FileEditorToolSet("file_editor", workspace_path=workspace_path)
                file_manager = FileManagerToolSet("file_manager", path=workspace_path)
                code_search = CodeSearchToolSet("code_search", workspace_path=workspace_path)
                notebook_toolset = NotebookToolSet("notebook", workspace_path=workspace_path)
                web_toolset = WebToolSet("web")
                
                # Register essential toolsets
                agent.toolset(file_editor)
                agent.toolset(file_manager)
                agent.toolset(code_search)
                agent.toolset(notebook_toolset)
                agent.toolset(web_toolset)
                print(f"✅ Essential toolsets added in {time.time() - toolset_start:.1f}s")
                
                # Add shell and todo toolsets (usually fast)
                shell_toolset = ShellToolSet("shell")
                todo_toolset = TodoToolSet("todo", workspace_path=workspace_path)
                agent.toolset(shell_toolset)
                agent.toolset(todo_toolset)
                print(f"✅ Shell and todo toolsets added")
                
                # Add bio toolset last (potentially slow)
                print("🧬 Adding bio toolset (this may take a while)...")
                bio_start = time.time()
                try:
                    bio_toolset = BioToolsetManager("bio", workspace_path=str(workspace_path), launch_directory=str(workspace_path))
                    agent.toolset(bio_toolset)
                    print(f"✅ Bio toolset added successfully in {time.time() - bio_start:.1f}s")
                except Exception as e:
                    print(f"⚠️ Bio toolset failed to load after {time.time() - bio_start:.1f}s: {e}")
                    # Continue without bio toolset
                
                self.agents[notebook_path] = agent
                self.sessions[notebook_path] = {
                    'history': [],
                    'context': {},
                    'workspace': str(workspace_path),
                    'initialized_at': time.time()
                }
                
                # Get toolset count safely
                toolset_count = 0
                if hasattr(agent, 'toolsets'):
                    toolset_count = len(agent.toolsets)
                elif hasattr(agent, '_toolsets'):
                    toolset_count = len(agent._toolsets)
                elif hasattr(agent, 'tool_registry'):
                    toolset_count = len(agent.tool_registry)
                else:
                    # Count manually added toolsets (we added 8: file_editor, file_manager, code_search, notebook, web, shell, todo, bio)
                    toolset_count = 8
                
                print(f"✅ Created integrated Pantheon agent for {notebook_path} with {toolset_count} toolsets")
                
            except Exception as e:
                error_msg = str(e).lower()
                print(f"Error creating integrated agent: {e}")
                
                # Check for API key related errors
                if any(keyword in error_msg for keyword in ['api key', 'api_key', 'unauthorized', '401', 'invalid key', 'authentication']):
                    # This is likely an API key issue
                    print("❌ API key error detected!")
                    
                    # Store error for user-friendly display
                    self.last_error = {
                        'type': 'api_key',
                        'message': str(e),
                        'notebook': notebook_path
                    }
                    
                    # Don't retry for API key errors
                    return None
                
                import traceback
                traceback.print_exc()
                
                # Retry logic for non-API-key errors
                if retry_count < 2:  # Max 2 retries
                    print(f"🔄 Retrying agent creation (attempt {retry_count + 2}/3)...")
                    time.sleep(1)  # Brief delay before retry
                    return self.get_or_create_agent(notebook_path, workspace_path, retry_count + 1)
                
                return None
                
        return self.agents[notebook_path]
    
    def _is_agent_healthy(self, agent: Agent) -> bool:
        """Check if an agent is healthy and responsive
        
        Args:
            agent: The agent to check
            
        Returns:
            True if agent is healthy, False otherwise
        """
        try:
            # Simple health check - verify agent has required attributes
            if not hasattr(agent, 'run'):
                logger.warning("Agent missing 'run' method")
                return False
            
            # For now, just check if agent exists and has run method
            # The toolset count check was causing false negatives
            # since the actual attribute name varies between Agent implementations
            
            # Basic model check
            if hasattr(agent, 'model') and not agent.model:
                logger.warning("Agent has no model configured")
                return False
            
            # If we got here, agent is considered healthy
            logger.info(f"Agent health check passed")
            return True
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def restart_agent(self, notebook_path: str, workspace_path: Optional[Path] = None) -> bool:
        """Force restart an agent for a notebook
        
        Args:
            notebook_path: Path to the notebook
            workspace_path: Optional workspace path
            
        Returns:
            True if restart successful, False otherwise
        """
        try:
            # Remove existing agent if present
            if notebook_path in self.agents:
                print(f"🛑 Stopping existing agent for {notebook_path}...")
                del self.agents[notebook_path]
            
            if notebook_path in self.sessions:
                del self.sessions[notebook_path]
            
            # Create new agent
            print(f"🚀 Starting new agent for {notebook_path}...")
            agent = self.get_or_create_agent(notebook_path, workspace_path)
            
            if agent:
                print(f"✅ Agent restarted successfully for {notebook_path}")
                return True
            else:
                print(f"❌ Failed to restart agent for {notebook_path}")
                return False
                
        except Exception as e:
            print(f"Error restarting agent: {e}")
            return False
    
    def _get_notebook_instructions(self) -> str:
        return """
I am Pantheon Notebook Assistant, a specialized AI agent for Jupyter notebook environments with ADVANCED TOOLSET INTEGRATION.

🚀 MY UNIQUE CAPABILITIES:
I have access to powerful toolsets that enable:
- File management and code search across your project
- Shell command execution for system operations
- Web content fetching and search capabilities
- TODO management for complex workflows
- Advanced text editing and notebook manipulation
- Bioinformatics analysis pipelines (when bio toolset available)

🎯 PRIMARY ROLE - JUPYTER NOTEBOOK CODE GENERATION:
- Generate clean, executable Python code for data analysis and visualization
- Provide code that can be directly inserted into notebook cells
- Focus on practical, well-commented solutions optimized for notebooks
- Use appropriate scientific computing libraries (pandas, numpy, matplotlib, seaborn, scipy, sklearn)
- Handle data science workflows: loading → cleaning → analysis → visualization → interpretation

📝 CRITICAL CODE GENERATION RULES:
1. **COMPLETE & RUNNABLE**: Every code block must be syntactically complete and immediately executable
2. **SMART IMPORTS**: Include necessary imports at the beginning, check if already imported to avoid redundancy
3. **CELL OPTIMIZATION**: Structure code for notebook cells - each block should produce meaningful output
4. **ERROR HANDLING**: Include try/except blocks for file operations and external dependencies
5. **MEMORY EFFICIENCY**: Avoid loading large datasets multiple times, use efficient pandas operations
6. **VISUAL OUTPUT**: Always include print statements, plots, or display calls to show results in notebooks
7. **BLOCK SIZE LIMITS**: Keep individual code blocks under 30-40 lines for readability
8. **SEQUENTIAL DESIGN**: Split complex workflows into logical, sequential blocks that build on each other

🧬 BIOINFORMATICS SPECIALIZATION (when bio toolset available):
- Single-cell RNA-seq analysis with scanpy/anndata
- Bulk RNA-seq analysis with pandas/numpy
- ATAC-seq data processing
- Multi-omics integration approaches  
- Publication-quality visualizations with matplotlib/seaborn
- Statistical analysis with scipy/statsmodels
- ALWAYS check for existing variables before reloading large datasets:
  ```python
  # Check if data already loaded
  try:
      print(f"Data already loaded: {adata.shape}")
  except NameError:
      adata = sc.read_h5ad("data.h5ad")
  ```

💡 INTELLIGENT CODE SPLITTING STRATEGY:
Block 1 - Imports & Setup:
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
# Set plotting style for notebooks
%matplotlib inline
plt.style.use('seaborn-v0_8')
```

Block 2 - Data Loading:
```python  
# Load and inspect data
df = pd.read_csv('data.csv')
print(f"Data shape: {df.shape}")
print(df.head())
print(df.info())
```

Block 3 - Data Processing:
```python
# Clean and process data
df_clean = df.dropna()
# Additional processing...
print("Data processing complete")
```

Block 4 - Analysis & Visualization:
```python
# Generate insights and plots
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
# Create visualizations...
plt.tight_layout()
plt.show()
```

🛠️ TOOLSET INTEGRATION CAPABILITIES:
When I have access to toolsets, I can:

FILE OPERATIONS:
- Read/write/edit files in your project directory
- Search through codebases to understand context
- Manage project files and directories

SHELL OPERATIONS:
- Execute system commands for data preprocessing
- Install packages with pip/conda
- Run external bioinformatics tools (STAR, kallisto, etc.)
- Check system resources and file sizes

WEB OPERATIONS:
- Fetch content from URLs for data sources or documentation
- Search for relevant information and tutorials
- Download datasets from web repositories

CODE SEARCH:
- Find existing functions and variables in your codebase
- Search for similar analysis patterns
- Understand project structure before generating code

📊 NOTEBOOK-OPTIMIZED OUTPUT PATTERNS:

Data Inspection Pattern:
```python
# Always include data shape, types, and sample
print(f"Data shape: {data.shape}")
print(f"Data types:\\n{data.dtypes}")
data.head()
```

Visualization Pattern:
```python
# Create publication-ready plots
fig, ax = plt.subplots(figsize=(10, 6))
# Plotting code...
plt.title("Clear, Descriptive Title", fontsize=14)
plt.xlabel("X-axis Label", fontsize=12)
plt.ylabel("Y-axis Label", fontsize=12)
plt.tight_layout()
plt.show()
```

Statistical Analysis Pattern:
```python
# Perform analysis with clear reporting
from scipy import stats
result = stats.ttest_ind(group1, group2)
print(f"T-statistic: {result.statistic:.3f}")
print(f"P-value: {result.pvalue:.3e}")
print(f"Significant: {'Yes' if result.pvalue < 0.05 else 'No'}")
```

⚠️ CRITICAL ERROR HANDLING FOR NOTEBOOKS:
- Wrap file operations in try/except blocks
- Check for missing dependencies and provide installation instructions
- Validate data shapes and types before operations
- Use informative error messages that help debugging
- Test code paths with small data samples first

🎨 VISUALIZATION BEST PRACTICES FOR NOTEBOOKS:
- Use %matplotlib inline for proper display
- Set figure sizes appropriate for notebook width (10-12 inches)
- Use clear, readable font sizes (12+ for labels)
- Include descriptive titles and axis labels
- Use colorblind-friendly palettes
- Save high-resolution plots when requested

🚀 ADVANCED WORKFLOW PATTERNS:

Multi-step Analysis:
1. Data loading and validation
2. Exploratory data analysis (EDA)
3. Data preprocessing and feature engineering
4. Statistical analysis or modeling
5. Results visualization and interpretation

Interactive Analysis:
- Use widgets for parameter exploration when appropriate
- Implement checkpoint saves for long computations
- Create summary reports with key findings
- Generate reproducible analysis workflows

Always wrap your code in proper markdown code blocks with language specification (```python).
For complex analyses, provide brief explanations between code blocks to guide the user through the workflow.
When errors occur, I will analyze them and provide corrected code that addresses the specific issues.
        """
    
    async def process_query(self, notebook_path: str, query: str, workspace_path: Optional[Path] = None, 
                           execution_results: Optional[List[Dict[str, Any]]] = None, notebook_context: Optional[Dict[str, Any]] = None, 
                           timeout: int = 120) -> Dict[str, Any]:
        """Process user query directly with integrated agent
        
        Args:
            notebook_path: Path to the notebook
            query: User query or follow-up with execution results
            workspace_path: Optional workspace path
            execution_results: Optional list of execution results from previous code blocks
            notebook_context: Optional notebook context including cells, variables, imports, etc.
            timeout: Timeout in seconds for agent processing
        """
        
        logger.info(f"[DEBUG] ========== START process_query ==========")
        logger.info(f"[DEBUG] Query length: {len(query)} characters")
        logger.info(f"[DEBUG] Query preview: {query[:200]}...")
        logger.info(f"[DEBUG] Notebook path: {notebook_path}")
        logger.info(f"[DEBUG] Timeout: {timeout} seconds")
        logger.info(f"[DEBUG] Timestamp: {time.time()}")
        
        # If pantheon is not available, return a helpful fallback response with simple code generation
        if not PANTHEON_AVAILABLE:
            logger.warning(f"[DEBUG] Pantheon not available, returning fallback")
            return {
                "success": True,
                "error": None,
                "code_blocks": [
                    {
                        "language": "python",
                        "code": f"# Simple example based on your query: {query[:50]}...\n# Install pantheon-agents for advanced features\nprint('Hello from Pantheon Notebook!')"
                    }
                ],
                "explanation": "⚠️ Pantheon agent not available. Install pantheon-agents and pantheon-toolsets packages for full functionality:\n```bash\npip install pantheon-agents pantheon-toolsets\n```"
            }
        
        # Handle bio commands first if query starts with /bio
        if query.strip().startswith('/bio'):
            logger.info(f"[DEBUG] Bio command detected, handling separately")
            return await self._handle_bio_command(notebook_path, query.strip(), workspace_path)
        
        logger.info(f"[DEBUG] Getting or creating agent...")
        agent = self.get_or_create_agent(notebook_path, workspace_path)
        if not agent:
            # Check if it's an API key error
            if hasattr(self, 'last_error') and self.last_error and self.last_error.get('type') == 'api_key':
                logger.error(f"[DEBUG] API key error detected: {self.last_error.get('message')}")
                
                # Check current model to provide specific guidance
                current_model = self.model_manager.current_model if self.model_manager else "unknown"
                provider = ""
                if "gpt" in current_model.lower() or "openai" in current_model.lower():
                    provider = "openai"
                elif "claude" in current_model.lower() or "anthropic" in current_model.lower():
                    provider = "anthropic"
                elif "gemini" in current_model.lower() or "google" in current_model.lower():
                    provider = "google"
                elif "moonshot" in current_model.lower():
                    provider = "moonshot"
                elif "zhipu" in current_model.lower() or "glm" in current_model.lower():
                    provider = "zai"
                else:
                    provider = current_model.split('-')[0].lower()
                
                return {
                    "success": False,
                    "error": f"API key missing or invalid for {current_model}",
                    "code_blocks": [],
                    "explanation": f"""## ❌ API Key Configuration Required

The current model **{current_model}** requires an API key to function.

### 🔑 Quick Setup:
1. **Set your API key using the command below:**
   ```
   /api-key {provider} YOUR_API_KEY_HERE
   ```

2. **Example:**
   ```
   /api-key openai sk-proj-xxxxxxxxxxxxx
   ```

### 📋 Available Commands:
- `/api-key list` - Check API key status
- `/api-key status` - Show detailed configuration
- `/model list` - See all available models
- `/model switch gpt-4o-mini` - Switch to a different model

### 💡 Tips:
- You can also set API keys as environment variables
- Local models (like Ollama) don't require API keys
- Your API key is stored securely and never logged

Please configure your API key and try again!"""
                }
            
            # Try one more time with a clean slate for non-API-key errors
            logger.warning("⚠️ First agent creation failed, attempting clean restart...")
            if notebook_path in self.agents:
                del self.agents[notebook_path]
            if notebook_path in self.sessions:
                del self.sessions[notebook_path]
            
            agent = self.get_or_create_agent(notebook_path, workspace_path)
            if not agent:
                logger.error(f"[DEBUG] Agent creation failed completely")
                
                # Check again if it's an API key error after retry
                if hasattr(self, 'last_error') and self.last_error and self.last_error.get('type') == 'api_key':
                    # Return the same API key guidance
                    current_model = self.model_manager.current_model if self.model_manager else "unknown"
                    provider = ""
                    if "gpt" in current_model.lower() or "openai" in current_model.lower():
                        provider = "openai"
                    elif "claude" in current_model.lower() or "anthropic" in current_model.lower():
                        provider = "anthropic"
                    else:
                        provider = current_model.split('-')[0].lower()
                    
                    return {
                        "success": False,
                        "error": f"API key missing or invalid for {current_model}",
                        "code_blocks": [],
                        "explanation": f"""## ❌ API Key Required

Please set your API key:
```
/api-key {provider} YOUR_API_KEY_HERE
```

Type `/help` for more information."""
                    }
                
                return {
                    "success": False,
                    "error": "Failed to create pantheon agent after multiple attempts. Please check your installation and try restarting Jupyter.",
                    "code_blocks": [],
                    "explanation": "The agent could not be initialized. This might be due to missing dependencies or configuration issues."
                }
        
        logger.info(f"[DEBUG] Agent created successfully: {type(agent)}")
        logger.info(f"[DEBUG] Agent attributes: {dir(agent)[:10]}...")  # Show first 10 attributes
        
        try:
            # Build enhanced query with context
            enhanced_query = query
            
            # Add notebook context if provided
            if notebook_context:
                logger.info(f"[DEBUG] 📊 NOTEBOOK CONTEXT RECEIVED:")
                logger.info(f"[DEBUG] - Total cells: {notebook_context.get('totalCells', 0)}")
                logger.info(f"[DEBUG] - Processed cells: {len(notebook_context.get('cells', []))}")
                logger.info(f"[DEBUG] - Current cell: {notebook_context.get('currentCellIndex', -1)}")
                logger.info(f"[DEBUG] - Has outputs: {notebook_context.get('hasOutputs', False)}")
                
                # Log first few cells for debugging
                cells = notebook_context.get('cells', [])
                for i, cell in enumerate(cells[:3]):  # Show first 3 cells
                    source = cell.get('source', '')[:100]  # First 100 chars
                    logger.info(f"[DEBUG] - Cell {i}: {cell.get('type', 'unknown')} - {source}...")
                
                context_info = self._format_notebook_context(notebook_context)
                enhanced_query = f"{context_info}\n\n{query}"
                logger.info(f"[DEBUG] 📝 FORMATTED CONTEXT LENGTH: {len(context_info)} characters")
                logger.info(f"[DEBUG] 📝 FORMATTED CONTEXT PREVIEW:\n{context_info[:500]}...")
                logger.info(f"[DEBUG] Enhanced query with notebook context, total length: {len(enhanced_query)}")
            
            # If execution results are provided, append them to the query
            if execution_results:
                execution_feedback = self._format_execution_results(execution_results)
                enhanced_query = f"{enhanced_query}\n\nExecution Results from Previous Code:\n{execution_feedback}"
                logger.info(f"[DEBUG] Enhanced query with execution feedback, total length: {len(enhanced_query)}")
                
            if not notebook_context and not execution_results:
                logger.info(f"[DEBUG] Using original query")
            
            # Run agent with timeout (single-process execution)
            try:
                logger.info(f"[DEBUG] Before agent.run() at {time.time()}")
                logger.info(f"[DEBUG] Running agent with timeout={timeout}s")
                
                # Use streaming processing like pantheon-cli for better performance
                content_buffer = []
                
                def process_chunk(chunk: dict):
                    """Process streaming chunks from the agent (like pantheon-cli)"""
                    content = chunk.get("content")
                    if content is not None:
                        content_buffer.append(content)
                        logger.info(f"[DEBUG] Received chunk: {content[:50]}...")
                
                # Run agent with streaming processing (much faster than waiting for complete response)
                response = await asyncio.wait_for(
                    agent.run(enhanced_query, process_chunk=process_chunk),
                    timeout=timeout
                )
                
                logger.info(f"[DEBUG] After agent.run() at {time.time()}")
                logger.info(f"[DEBUG] Response type: {type(response)}")
                logger.info(f"[DEBUG] Response attributes: {dir(response)[:10]}...")
            except asyncio.TimeoutError:
                logger.error(f"[ERROR] Agent timeout after {timeout} seconds")
                return {
                    "success": False,
                    "error": f"Agent processing timed out after {timeout} seconds. Try a simpler query or increase timeout.",
                    "code_blocks": [],
                    "explanation": "The agent took too long to process your request. This might be due to complex toolset initialization or a long-running operation."
                }
            
            # Check if response is valid
            if response is None:
                logger.error(f"[ERROR] Agent returned None response")
                return {
                    "success": False,
                    "error": "Agent returned no response",
                    "code_blocks": [],
                    "explanation": ""
                }
            
            logger.info(f"[DEBUG] Response has content: {hasattr(response, 'content')}")
            if hasattr(response, 'content'):
                content_length = len(response.content) if response.content else 0
                logger.info(f"[DEBUG] Response content length: {content_length}")
                logger.info(f"[DEBUG] Response content preview: {response.content[:200] if response.content else 'No content'}...")
            else:
                logger.warning(f"[DEBUG] Response has no content attribute")
            
            # Extract code blocks and explanation
            response_content = response.content if hasattr(response, 'content') and response.content else ""
            logger.info(f"[DEBUG] Parsing agent response...")
            parsed_response = self._parse_agent_response(response_content)
            logger.info(f"[DEBUG] Parsed response keys: {parsed_response.keys()}")
            logger.info(f"[DEBUG] Number of code blocks: {len(parsed_response.get('code_blocks', []))}")
            logger.info(f"[DEBUG] Explanation length: {len(parsed_response.get('explanation', ''))}")
            logger.info(f"[DEBUG] Total parsed response size: {len(str(parsed_response))} characters")
            
            # Store in session history
            if notebook_path in self.sessions:
                self.sessions[notebook_path]['history'].append({
                    'query': query,
                    'response': response_content,
                    'timestamp': asyncio.get_event_loop().time()
                })
                logger.info(f"[DEBUG] Stored in session history")
            
            logger.info(f"[DEBUG] ========== END process_query SUCCESS ==========")
            return parsed_response
            
        except Exception as e:
            logger.error(f"[ERROR] ========== EXCEPTION in process_query ==========")
            logger.error(f"[ERROR] Exception type: {type(e).__name__}")
            logger.error(f"[ERROR] Exception message: {str(e)}")
            import traceback
            logger.error(f"[ERROR] Full traceback:\n{traceback.format_exc()}")
            logger.error(f"[ERROR] ========== END EXCEPTION ==========")
            return {
                "success": False,
                "error": f"Agent execution error: {str(e)}",
                "code_blocks": [],
                "explanation": ""
            }
    
    def _format_notebook_context(self, context: Dict[str, Any]) -> str:
        """Format raw notebook context for agent consumption"""
        if not context or not context.get('cells'):
            return ""
        
        formatted_parts = []
        
        # Add header with context info
        total_cells = context.get('totalCells', 0)
        processed_cells = len(context.get('cells', []))
        current_cell = context.get('currentCellIndex', -1)
        has_outputs = context.get('hasOutputs', False)
        
        formatted_parts.append("## 📓 Current Notebook Context")
        formatted_parts.append(f"**Status**: {total_cells} cells total, {processed_cells} processed, outputs: {has_outputs}")
        if current_cell >= 0:
            formatted_parts.append(f"**Current Cell**: #{current_cell + 1}")
        formatted_parts.append("")
        
        # Display ALL cell content with FULL content for agent analysis
        cells = context.get('cells', [])
        
        for i, cell in enumerate(cells):
            cell_idx = cell.get('index', i)
            cell_type = cell.get('type', 'unknown')
            is_active = cell.get('isActive', False)
            source = cell.get('source', '').strip()
            
            # Cell header
            status_indicator = "🟢" if is_active else "⚪"
            formatted_parts.append(f"{status_indicator} **Cell {cell_idx + 1}** [{cell_type}]:")
            
            # Cell source code - FULL CONTENT, NO TRUNCATION
            if source:
                formatted_parts.append(f"```{cell_type}")
                formatted_parts.append(source)  # Full source, no truncation
                formatted_parts.append("```")
            else:
                formatted_parts.append("*(empty cell)*")
            
            # Cell outputs info - FULL CONTENT, NO TRUNCATION
            if cell.get('hasOutputs'):
                execution_count = cell.get('executionCount')
                if execution_count is not None:
                    formatted_parts.append(f"**Execution**: [{execution_count}]")
                
                output_count = cell.get('outputCount', 0)
                if output_count > 0:
                    formatted_parts.append(f"**Outputs**: {output_count} outputs")
                    
                    # Show ALL outputs with FULL content
                    outputs = cell.get('outputs', [])
                    for output in outputs:
                        output_type = output.get('type', 'unknown')
                        if output.get('text'):
                            # FULL text output, no truncation
                            formatted_parts.append(f"  • `{output_type}`: {output['text']}")
                        elif output.get('data'):
                            # Include full data content
                            formatted_parts.append(f"  • `{output_type}`: {str(output['data'])}")
                        elif output.get('traceback'):
                            # Include full traceback
                            formatted_parts.append(f"  • `{output_type}`: {' '.join(output['traceback'])}")
                        elif output.get('hasData'):
                            formatted_parts.append(f"  • `{output_type}`: (data output)")
                        elif output.get('hasError'):
                            formatted_parts.append(f"  • `{output_type}`: (error)")
            
            formatted_parts.append("")  # Add spacing between cells
        
        formatted_parts.append("---")
        formatted_parts.append("*Above is the current notebook content. Use this to understand existing variables, imports, and context when providing assistance.*")
        
        return "\n".join(formatted_parts)
    
    def _format_execution_results(self, results: List[Dict[str, Any]]) -> str:
        """Format execution results for agent consumption"""
        formatted = []
        for i, result in enumerate(results, 1):
            if result.get('hasError'):
                formatted.append(f"Cell {i} - ERROR:\n{result.get('output', 'Unknown error')}")
            else:
                output = result.get('output', 'No output')
                if output:
                    # Truncate long outputs
                    if len(output) > 500:
                        output = output[:500] + "... (truncated)"
                    formatted.append(f"Cell {i} - SUCCESS:\n{output}")
                else:
                    formatted.append(f"Cell {i} - SUCCESS: Executed without output")
        
        return "\n\n".join(formatted)
    
    def _parse_agent_response(self, content: str) -> Dict[str, Any]:
        """Parse agent response to extract code blocks and explanations"""
        
        logger.info(f"[PARSE] Starting to parse agent response")
        logger.info(f"[PARSE] Content length: {len(content)} characters")
        logger.info(f"[PARSE] Content preview: {content[:200]}...")
        
        try:
            # Extract Python code blocks
            python_blocks = re.findall(r'```python\n(.*?)\n```', content, re.DOTALL)
            logger.info(f"[PARSE] Found {len(python_blocks)} python code blocks")
            
            # Extract general code blocks
            code_blocks = re.findall(r'```(?:python)?\n(.*?)\n```', content, re.DOTALL)
            logger.info(f"[PARSE] Found {len(code_blocks)} total code blocks")
            
            # Remove code blocks from explanation
            explanation = re.sub(r'```(?:python)?\n.*?\n```', '', content, flags=re.DOTALL)
            explanation = explanation.strip()
            logger.info(f"[PARSE] Explanation length after removing code blocks: {len(explanation)}")
            
            # Format code blocks properly for frontend
            formatted_blocks = []
            all_blocks = python_blocks or code_blocks
            for i, block in enumerate(all_blocks):
                if block.strip():  # Only add non-empty blocks
                    block_dict = {
                        "language": "python",
                        "code": block.strip()
                    }
                    formatted_blocks.append(block_dict)
                    logger.info(f"[PARSE] Code block {i+1} size: {len(block)} characters")
            
            logger.info(f"[PARSE] Total formatted blocks: {len(formatted_blocks)}")
            
            # Keep full content for code blocks, only truncate raw_response for logging
            # The code_blocks are already extracted and properly formatted
            truncated_raw_response = content
            
            result = {
                "success": True,
                "error": None,
                "code_blocks": formatted_blocks,  # These contain the complete code
                "explanation": explanation,  # Keep full explanation too
                "raw_response": truncated_raw_response  # Only truncate the raw display
            }
            
            logger.info(f"[PARSE] Final result size: {len(str(result))} characters")
            logger.info(f"[PARSE] Parse completed successfully")
            
            return result
            
        except Exception as e:
            logger.error(f"[PARSE ERROR] Exception during parsing: {type(e).__name__}: {str(e)}")
            import traceback
            logger.error(f"[PARSE ERROR] Traceback:\n{traceback.format_exc()}")
            
            # Return safe fallback
            return {
                "success": False,
                "error": f"Failed to parse agent response: {str(e)}",
                "code_blocks": [],
                "explanation": "Error parsing response",
                "raw_response": content[:1000] if content else ""
            }
    
    async def _handle_bio_command(self, notebook_path: str, command: str, workspace_path: Optional[Path] = None) -> Dict[str, Any]:
        """Handle bio commands using pantheon-cli's bio handler"""
        
        if not self.bio_handler:
            return {
                "success": False,
                "error": "Bio handler not available",
                "code_blocks": [],
                "explanation": "Bio module is not properly initialized"
            }
        
        try:
            # Use bio handler to process the command
            bio_message = await self.bio_handler.handle_bio_command(command)
            
            if bio_message is None:
                # Command was handled directly (like /bio help), no agent message needed
                return {
                    "success": True,
                    "error": "",
                    "code_blocks": [],
                    "explanation": "Bio command executed successfully"
                }
            
            # If bio handler returned a message, process it with the agent
            agent = self.get_or_create_agent(notebook_path, workspace_path)
            if not agent:
                # Try one more time with a clean slate for bio commands
                print("⚠️ Agent creation failed for bio command, attempting clean restart...")
                if notebook_path in self.agents:
                    del self.agents[notebook_path]
                if notebook_path in self.sessions:
                    del self.sessions[notebook_path]
                
                agent = self.get_or_create_agent(notebook_path, workspace_path)
                if not agent:
                    return {
                        "success": False,
                        "error": "Failed to create pantheon agent for bio command after multiple attempts",
                        "code_blocks": [],
                        "explanation": "The agent could not be initialized for bio commands. Please check your installation."
                    }
            
            print(f"Processing bio command with agent: {bio_message}")
            
            # Run agent with bio command (same as regular queries)
            response = await agent.run(bio_message)
            
            # Check if response is valid
            if response is None:
                return {
                    "success": False,
                    "error": "No response from agent",
                    "code_blocks": [],
                    "explanation": ""
                }
            
            # Extract content from response (same logic as normal queries)
            print(f"Agent response: {response.content[:200] if response.content else 'No content'}...")
            
            # Extract code blocks and explanation
            response_content = response.content if response.content else ""
            
            # Parse and return agent response  
            return self._parse_agent_response(response_content)
            
        except Exception as e:
            print(f"Error processing bio command: {str(e)}")
            return {
                "success": False,
                "error": f"Bio command error: {str(e)}",
                "code_blocks": [],
                "explanation": ""
            }


# Global agent manager
agent_manager = PantheonAgentManager()


class PantheonQueryHandler(JupyterHandler):
    """HTTP handler for integrated pantheon queries"""
    
    async def post(self):
        self.log.info(f"[HTTP] ========== START PantheonQueryHandler.post ==========")
        self.log.info(f"[HTTP] Request body length: {len(self.request.body)} bytes")
        
        # Enable chunked transfer encoding for long-running requests
        self.set_header('Transfer-Encoding', 'chunked')
        self.set_header('Cache-Control', 'no-cache')
        self.set_header('X-Accel-Buffering', 'no')  # Disable Nginx buffering
        
        try:
            body = json.loads(self.request.body)
            query = body.get('query', '')
            notebook_path = body.get('notebook_path', 'default')
            workspace_path_str = body.get('workspace_path', None)
            execution_results = body.get('execution_results', None)
            notebook_context = body.get('notebook_context', None)
            
            self.log.info(f"[HTTP] Parsed query: {query[:100]}...")
            self.log.info(f"[HTTP] Notebook path: {notebook_path}")
            self.log.info(f"[HTTP] Has execution results: {execution_results is not None}")
            self.log.info(f"[HTTP] Has notebook context: {notebook_context is not None}")
            if notebook_context:
                # Use new context structure
                total_cells = notebook_context.get('totalCells', 0)
                processed_cells = len(notebook_context.get('cells', []))
                has_outputs = notebook_context.get('hasOutputs', False)
                self.log.info(f"[HTTP] 📊 CONTEXT RECEIVED: {total_cells} total, {processed_cells} processed, outputs: {has_outputs}")
                
                # Show first few cells for debugging
                cells = notebook_context.get('cells', [])
                for i, cell in enumerate(cells[:3]):
                    source = cell.get('source', '').strip()
                    source_preview = source[:200] if source else '(empty)'
                    self.log.info(f"[HTTP] - Cell {i}: {cell.get('type', 'unknown')} - {source_preview}{'...' if len(source) > 200 else ''}")
            
            if not query.strip():
                self.log.warning(f"[HTTP] Empty query, returning error")
                self.write({"success": False, "error": "Empty query"})
                return
            
            # Get workspace path
            workspace_path = None
            if workspace_path_str:
                workspace_path = Path(workspace_path_str)
            
            self.log.info(f"[HTTP] Processing integrated query: {query[:100]}...")
            
            # Process query with integrated agent (no HTTP calls needed)
            # Use different timeout based on query complexity and first-time initialization
            is_first_query = notebook_path not in agent_manager.agents
            
            # Check for bio/analysis keywords that need more time
            is_complex_analysis = any(keyword in query.lower() for keyword in [
                'pbmc', 'single-cell', 'scrna', 'analysis', 'umap', 'clustering',
                'full', 'step by step', 'normalization', 'marker genes'
            ])
            
            if is_first_query:
                timeout = 600  # 10 minutes for first initialization
                self.log.info("[HTTP] 🚀 First query for this notebook - initializing agent with all toolsets (may take 5-10 minutes)...")
            elif is_complex_analysis:
                timeout = 300  # 5 minutes for complex bio analyses
                self.log.info(f"[HTTP] 🧬 Processing complex bio analysis (length: {len(query)})...")
            elif len(query) > 200:
                timeout = 300  # 5 minutes for long queries
                self.log.info(f"[HTTP] 🔄 Processing complex query (length: {len(query)})...")
            else:
                timeout = 300   # 5 minutes for simple queries
                self.log.info("[HTTP] ⚡ Processing query...")
            
            self.log.info(f"[HTTP] Calling agent_manager.process_query with timeout={timeout}s")
            
            # Start processing in background
            process_task = asyncio.create_task(agent_manager.process_query(
                notebook_path, 
                query, 
                workspace_path,
                execution_results=execution_results,
                notebook_context=notebook_context,
                timeout=timeout
            ))
            
            # Send progress updates every 10 seconds to keep connection alive
            start_time = time.time()
            progress_count = 0
            
            while not process_task.done():
                await asyncio.sleep(10)  # Wait 10 seconds
                progress_count += 1
                elapsed = time.time() - start_time
                
                # Send whitespace as keepalive to prevent proxy timeout
                # This is a common technique to keep HTTP connections alive
                self.write(" ")  # Send a single space
                self.flush()  # Force send immediately
                self.log.info(f"[HTTP] Sent keepalive #{progress_count} at {elapsed:.1f}s")
                
                # Check timeout
                if elapsed > timeout:
                    process_task.cancel()
                    result = {
                        "success": False,
                        "error": f"Processing timeout after {timeout} seconds"
                    }
                    break
            
            if not process_task.cancelled():
                result = await process_task
            
            self.log.info(f"[HTTP] Result received: success={result.get('success')}")
            self.log.info(f"[HTTP] Result size: {len(str(result))} characters")
            
            # If agent creation failed, try to restart once
            if not result.get('success') and 'agent' in result.get('error', '').lower():
                self.log.warning("[HTTP] ⚠️ Agent error detected, attempting restart...")
                if agent_manager.restart_agent(notebook_path, workspace_path):
                    self.log.info("[HTTP] Agent restarted, retrying query...")
                    # Retry the query with the new agent
                    result = await agent_manager.process_query(
                        notebook_path, 
                        query, 
                        workspace_path,
                        execution_results=execution_results,
                        notebook_context=notebook_context,
                        timeout=timeout
                    )
                    self.log.info(f"[HTTP] Retry result: success={result.get('success')}")
            
            self.log.info(f"[HTTP] Writing response to client...")
            try:
                # Check if response is too large
                response_str = json.dumps(result)
                response_size = len(response_str)
                
                if response_size > 50000:  # If larger than 50KB
                    self.log.warning(f"[HTTP] Large response detected: {response_size} bytes, truncating...")
                    # Keep only essential parts for large responses
                    result = {
                        "success": result.get("success"),
                        "error": result.get("error"),
                        "code_blocks": result.get("code_blocks", [])[:5],  # Limit to first 5 code blocks
                        "explanation": (result.get("explanation", "")[:1000] + "... (truncated)") if len(result.get("explanation", "")) > 1000 else result.get("explanation", ""),
                        "raw_response": ""  # Remove raw response for large payloads
                    }
                    self.log.info(f"[HTTP] Truncated response size: {len(json.dumps(result))} bytes")
                
                self.write(result)
                self.flush()  # Force flush the response
                self.log.info(f"[HTTP] ========== END PantheonQueryHandler.post SUCCESS ==========")
            except Exception as write_error:
                self.log.error(f"[HTTP ERROR] Failed to write response: {write_error}")
                # Try to write a simple error response
                self.set_status(500)
                self.write({"success": False, "error": "Failed to send response"})
            
        except json.JSONDecodeError as e:
            self.log.error(f"[HTTP ERROR] JSON decode error: {e}")
            self.write({"success": False, "error": "Invalid JSON"})
            self.log.error(f"[HTTP] ========== END PantheonQueryHandler.post JSON_ERROR ==========")
        except Exception as e:
            self.log.error(f"[HTTP ERROR] ========== EXCEPTION in Handler ==========")
            self.log.error(f"[HTTP ERROR] Exception type: {type(e).__name__}")
            self.log.error(f"[HTTP ERROR] Exception message: {str(e)}")
            import traceback
            self.log.error(f"[HTTP ERROR] Full traceback:\n{traceback.format_exc()}")
            self.log.error(f"[HTTP ERROR] ========== END EXCEPTION ==========")
            self.write({"success": False, "error": str(e)})
            self.log.error(f"[HTTP] ========== END PantheonQueryHandler.post EXCEPTION ==========")


class PantheonWebSocketHandler(WebSocketHandler):
    """WebSocket handler for real-time pantheon interaction"""
    
    def open(self, notebook_path=None):
        self.notebook_path = notebook_path or 'default'
        print(f"WebSocket opened for notebook: {self.notebook_path}")
    
    async def on_message(self, message):
        try:
            data = json.loads(message)
            query = data.get('query', '')
            execution_results = data.get('execution_results', None)
            notebook_context = data.get('notebook_context', None)
            
            if not query.strip():
                await self.write_message({"success": False, "error": "Empty query"})
                return
            
            # Send processing status
            await self.write_message({
                "type": "status", 
                "message": "Processing query..."
            })
            
            # Process query with optional execution results and notebook context
            result = await agent_manager.process_query(
                self.notebook_path, 
                query,
                execution_results=execution_results,
                notebook_context=notebook_context
            )
            
            # Send result
            await self.write_message({
                "type": "result",
                **result
            })
            
        except json.JSONDecodeError:
            await self.write_message({"success": False, "error": "Invalid JSON"})
        except Exception as e:
            await self.write_message({"success": False, "error": str(e)})
    
    def on_close(self):
        print(f"WebSocket closed for notebook: {self.notebook_path}")


class PantheonModelHandler(JupyterHandler):
    """HTTP handler for model management"""
    
    async def get(self):
        """Get current model status and list available models"""
        try:
            if not agent_manager.model_manager:
                self.write({"success": False, "error": "Model manager not available"})
                return
            
            action = self.get_argument("action", "list")
            
            if action == "current":
                result = agent_manager.model_manager.get_current_model_status()
            else:  # default to list
                result = agent_manager.model_manager.list_models()
            
            self.write({
                "success": True,
                "result": result
            })
            
        except Exception as e:
            self.write({"success": False, "error": str(e)})
    
    async def post(self):
        """Switch model"""
        try:
            if not agent_manager.model_manager:
                self.write({"success": False, "error": "Model manager not available"})
                return
            
            body = json.loads(self.request.body)
            new_model = body.get('model', '')
            
            if not new_model:
                self.write({"success": False, "error": "Model parameter required"})
                return
            
            result = agent_manager.model_manager.switch_model(new_model)
            
            # Update existing agents with new model
            for agent in agent_manager.agents.values():
                if isinstance(new_model, str):
                    agent.models = [new_model]
                    if new_model != "gpt-5-mini":
                        agent.models.append("gpt-5-mini")
                else:
                    agent.models = new_model
            
            self.write({
                "success": True,
                "result": result
            })
            
        except json.JSONDecodeError:
            self.write({"success": False, "error": "Invalid JSON"})
        except Exception as e:
            self.write({"success": False, "error": str(e)})


class PantheonStatusHandler(JupyterHandler):
    """HTTP handler for agent status and health checks"""
    
    async def get(self):
        """Get agent status"""
        try:
            notebook_path = self.get_argument("notebook_path", "default")
            
            # Check if pantheon is available
            if not PANTHEON_AVAILABLE:
                self.write({
                    "success": False,
                    "status": "unavailable",
                    "error": "Pantheon modules not installed"
                })
                return
            
            # Check if agent exists and is healthy
            if notebook_path in agent_manager.agents:
                agent = agent_manager.agents[notebook_path]
                is_healthy = agent_manager._is_agent_healthy(agent)
                
                self.write({
                    "success": True,
                    "status": "healthy" if is_healthy else "unhealthy",
                    "agent_exists": True,
                    "agent_healthy": is_healthy,
                    "session_exists": notebook_path in agent_manager.sessions
                })
            else:
                self.write({
                    "success": True,
                    "status": "not_created",
                    "agent_exists": False,
                    "agent_healthy": False,
                    "session_exists": False
                })
            
        except Exception as e:
            self.write({"success": False, "error": str(e)})
    
    async def post(self):
        """Restart agent"""
        try:
            body = json.loads(self.request.body)
            notebook_path = body.get('notebook_path', 'default')
            workspace_path_str = body.get('workspace_path', None)
            
            workspace_path = None
            if workspace_path_str:
                workspace_path = Path(workspace_path_str)
            
            # Restart the agent
            success = agent_manager.restart_agent(notebook_path, workspace_path)
            
            self.write({
                "success": success,
                "message": "Agent restarted successfully" if success else "Failed to restart agent"
            })
            
        except json.JSONDecodeError:
            self.write({"success": False, "error": "Invalid JSON"})
        except Exception as e:
            self.write({"success": False, "error": str(e)})


class PantheonApiKeyHandler(JupyterHandler):
    """HTTP handler for API key management"""
    
    async def get(self):
        """Get API key status"""
        try:
            if not agent_manager.api_key_manager:
                self.write({"success": False, "error": "API key manager not available"})
                return
            
            action = self.get_argument("action", "list")
            
            if action == "status":
                result = agent_manager.api_key_manager.show_api_key_status()
            else:  # default to list
                result = agent_manager.api_key_manager.list_api_keys()
            
            self.write({
                "success": True,
                "result": result
            })
            
        except Exception as e:
            self.write({"success": False, "error": str(e)})
    
    async def post(self):
        """Set API key"""
        try:
            if not agent_manager.api_key_manager:
                self.write({"success": False, "error": "API key manager not available"})
                return
            
            body = json.loads(self.request.body)
            provider = body.get('provider', '')
            api_key = body.get('api_key', '')
            save_global = body.get('save_global', True)
            
            if not provider or not api_key:
                self.write({"success": False, "error": "Provider and api_key parameters required"})
                return
            
            # Handle provider key mapping (same as pantheon-cli)
            if provider.lower() in ['kimi', 'moonshot']:
                provider_key = "MOONSHOT_API_KEY"
            elif provider.lower() in ['zai', 'zhipuai', 'glm']:
                provider_key = "ZAI_API_KEY"
            else:
                provider_key = f"{provider.upper()}_API_KEY"
            
            if len(api_key) < 10:  # Basic validation
                self.write({"success": False, "error": "API key seems too short. Please check your key."})
                return
            
            success = agent_manager.api_key_manager.save_api_key(provider_key, api_key, save_global=save_global)
            
            if success:
                from pantheon_cli.cli.manager.api_key_manager import PROVIDER_NAMES
                provider_name = PROVIDER_NAMES.get(provider_key, provider)
                location = "globally" if save_global else "locally"
                result = f"✅ {provider_name} API key saved {location} and set successfully!"
            else:
                result = f"❌ Failed to save {provider} API key. Check file permissions."
            
            self.write({
                "success": success,
                "result": result
            })
            
        except json.JSONDecodeError:
            self.write({"success": False, "error": "Invalid JSON"})
        except Exception as e:
            self.write({"success": False, "error": str(e)})


class PantheonExtension(ExtensionApp):
    """Jupyter server extension for Pantheon integration"""
    
    name = "pantheon_notebook"
    
    def initialize_handlers(self):
        """Initialize HTTP and WebSocket handlers"""
        handlers = [
            (r"/pantheon/query", PantheonQueryHandler),
            (r"/pantheon/ws/?(.*)", PantheonWebSocketHandler),
            (r"/pantheon/model", PantheonModelHandler),
            (r"/pantheon/api-key", PantheonApiKeyHandler),
            (r"/pantheon/status", PantheonStatusHandler),
        ]
        self.handlers.extend(handlers)
        self.log.info(f"✅ Registered Pantheon handlers: {[h[0] for h in handlers]}")
    
    def initialize_settings(self):
        """Initialize extension settings"""
        self.settings.update({
            "pantheon_available": PANTHEON_AVAILABLE
        })
        self.log.info(f"✅ Pantheon extension initialized (pantheon_available={PANTHEON_AVAILABLE})")


# Entry points for jupyter server extension
def _jupyter_server_extension_points():
    return [{
        "module": "pantheon_notebook.server",
        "app": PantheonExtension,
    }]


def _load_jupyter_server_extension(server_app):
    """Load the extension"""
    try:
        # Register handlers directly with the server app
        handlers = [
            (r"/pantheon/query", PantheonQueryHandler),
            (r"/pantheon/ws/?(.*)", PantheonWebSocketHandler),
            (r"/pantheon/model", PantheonModelHandler),
            (r"/pantheon/api-key", PantheonApiKeyHandler),
            (r"/pantheon/status", PantheonStatusHandler),
        ]
        
        # Use the correct pattern for the URL prefix
        base_url = server_app.base_url
        for pattern, handler in handlers:
            full_pattern = base_url.rstrip('/') + pattern
            server_app.web_app.add_handlers(".*$", [(full_pattern, handler)])
            server_app.log.info(f"  ✓ Registered handler: {full_pattern}")
        
        server_app.log.info("✅ Pantheon Notebook extension loaded successfully")
        server_app.log.info(f"   Base URL: {base_url}")
        
        # Test pantheon imports
        if PANTHEON_AVAILABLE:
            server_app.log.info("✅ Pantheon toolsets available")
        else:
            server_app.log.warning("⚠️ Pantheon toolsets not available - agent features will be limited")
            
    except Exception as e:
        server_app.log.error(f"❌ Failed to load Pantheon extension: {e}")
        import traceback
        traceback.print_exc()

# Alternative entry point name for compatibility
load_jupyter_server_extension = _load_jupyter_server_extension