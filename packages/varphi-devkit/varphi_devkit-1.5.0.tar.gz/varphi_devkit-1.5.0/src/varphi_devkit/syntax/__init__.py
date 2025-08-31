"""
Varphi Syntax Module

This module provides syntax analysis components for the Varphi language.

Components:
- VarphiLexer: Tokenizes Varphi source code
- VarphiParser: Parses tokens into parse tree
- VarphiListener: Provides callback interface for parse tree traversal
- VarphiSyntaxError: Exception for syntax errors
- VarphiSyntaxErrorListener: Error handler for parsing
"""

# Error handling components
from .error_listener import VarphiSyntaxError, VarphiSyntaxErrorListener

# ANTLR generated components
from .antlr.VarphiLexer import VarphiLexer
from .antlr.VarphiParser import VarphiParser
from .antlr.VarphiListener import VarphiListener

__all__ = [
    "VarphiSyntaxError",
    "VarphiSyntaxErrorListener", 
    "VarphiLexer",
    "VarphiParser", 
    "VarphiListener",
]
