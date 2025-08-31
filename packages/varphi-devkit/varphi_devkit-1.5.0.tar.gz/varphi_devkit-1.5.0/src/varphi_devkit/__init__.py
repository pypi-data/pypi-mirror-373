"""
Varphi Development Kit

A Python toolkit for working with the Varphi language - a domain-specific
language for describing Turing machine transition rules.

Main Components:

Model Classes:
- VarphiTapeCharacter: Represents tape characters (0 for blank, 1 for tally)
- VarphiHeadDirection: Represents head movement (L for left, R for right)  
- VarphiLine: Represents a complete transition rule

Compilation:
- VarphiCompiler: Abstract base class for implementing Varphi compilers
- compile: Function to compile Varphi programs using a given compiler

Error Handling:
- VarphiSyntaxError: Exception raised for syntax errors in Varphi code
"""

from .model import VarphiTapeCharacter, VarphiHeadDirection, VarphiLine
from .compilation import VarphiCompiler, compile_varphi
from .syntax.error_listener import VarphiSyntaxError

__all__ = [
    "VarphiTapeCharacter",
    "VarphiHeadDirection", 
    "VarphiLine",
    "VarphiCompiler",
    "compile_varphi",
    "VarphiSyntaxError",
]
