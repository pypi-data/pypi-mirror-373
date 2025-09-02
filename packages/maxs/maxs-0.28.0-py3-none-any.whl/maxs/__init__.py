"""maxs - a minimalist strands agent.

A rock-solid, binary-ready AI agent that uses local models via Ollama.
Designed for extreme simplicity and reliability.
"""

__version__ = "0.1.3"
__author__ = "maxs"
__description__ = "minimalist strands agent"

from .main import create_agent, main

__all__ = ["main", "create_agent", "__version__"]
