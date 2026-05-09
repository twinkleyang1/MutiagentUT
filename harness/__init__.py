"""
Harness Module

Coordinates the UT generation process by managing state and providing prompts.
"""

from .state_manager import StateManager
from .coordinator import HarnessCoordinator

__all__ = ['StateManager', 'HarnessCoordinator']