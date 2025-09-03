"""
Articom Skills SDK
==================

This SDK provides the core components for building skills for the Articom Agentic Marketplace.

Key components:
- ArticomSkill: A decorator to define a skill and its metadata.
- Tool: A decorator to define a tool (function) within a skill.
- ArticomCLI: A command-line interface helper (used internally by the CLI).
"""

from .skill import ArticomSkill, Tool
from .cli import ArticomCLI

__all__ = ["ArticomSkill", "Tool", "ArticomCLI"]
