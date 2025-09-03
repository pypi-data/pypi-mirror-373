"""Prompt engineering module for the Gnosari framework.

This module contains all prompt-related functionality including:
- System prompt generation for orchestrator and specialized agents
- Tool prompt definitions and utilities
- Prompt constants for team runner
"""

from .tool_prompts import get_tools_definition

# Prompt building functions
from .prompts import (
    build_orchestrator_system_prompt,
    build_specialized_agent_system_prompt
)

# Prompt constants for team runner
from .prompts import (
    TOOL_EXECUTION_RESULT_PROMPT,
    TOOL_EXECUTION_ERROR_PROMPT,
    TOOL_NOT_AVAILABLE_PROMPT,
    CONTINUE_PROCESSING_PROMPT,
    ORCHESTRATION_PLANNING_PROMPT,
    FEEDBACK_LOOP_PROMPT
)

__all__ = [
    # Tool prompt utilities
    "get_tools_definition",
    
    # Prompt building functions
    "build_orchestrator_system_prompt",
    "build_specialized_agent_system_prompt",
    
    # Prompt constants
    "TOOL_EXECUTION_RESULT_PROMPT",
    "TOOL_EXECUTION_ERROR_PROMPT", 
    "TOOL_NOT_AVAILABLE_PROMPT",
    "CONTINUE_PROCESSING_PROMPT",
    "ORCHESTRATION_PLANNING_PROMPT",
    "FEEDBACK_LOOP_PROMPT"
]
