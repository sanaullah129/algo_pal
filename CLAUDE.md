# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commonly Used Commands
1. **Setup**:
   - `pip install -r requirements.txt` - Install all dependencies
   - `python -m pytest` - Run test suite

2. **Running the Application**:
   - `python main.py` - Start the FastAPI server
   - `uvicorn main:app --reload` - Development mode with auto-reload

3. **Agent Workflows**:
   - `python agents/dsa_agent.py` - Execute DSA processing agent
   - `python prompts/dsa_system_prompt.py` - Load system prompts for DSA

4. **Environment Configuration**:
   - Set environment variables: `export AZURE_OPENAI_API_KEY=...`
   - Configuration files: `core/env.py`, `core/config.py`

## High-Level Architecture
The codebase follows a modular architecture with clear separation of concerns:

### Core Layer (`core/`)
- `config.py`: Centralized configuration, API client setup (Azure OpenAI)
- `env.py`: Environment variable management and validation
- `middleware.py`: Request logging and error handling middleware for FastAPI

### Agent Layer (`agents/`)
- `dsa_agent.py`: LangGraph-based stateful agent for DSA problem solving with conversation memory

### Prompt Layer (`prompts/`)
- `dsa_system_prompt.py`: Contains DSA-specific system prompts and templates for LLM interaction

### API Layer (`main.py`)
- FastAPI application with streaming support and Azure OpenAI integration
- `SessionManager`: Handles conversation state and history
- `generate_dsa_response()`: Orchestrates LLM calls for DSA problem solving

### Key Design Patterns
- **Layered Architecture**: Separation between configuration, middleware, agents, and API
- **Stateful Conversations**: LangGraph-based workflow for managing multi-turn DSA discussions
- **Structured Responses**: Consistent response format with complexity analysis and code samples
- **Azure OpenAI Integration**: Production-ready LLM client with proper error handling
- **Asynchronous Processing**: Streaming support for long-running LLM responses

This modular structure enables independent development of each layer while maintaining clear interfaces and consistent behavior across the application.