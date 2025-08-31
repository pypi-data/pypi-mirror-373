"""Compilation infrastructure for Varphi language programs.

This module provides the compilation framework for translating Varphi programs 
(Turing machine descriptions) into target languages. Users implement custom 
compilers by subclassing VarphiCompiler and defining how individual transition 
rules should be processed.

Usage:
    1. Subclass VarphiCompiler and implement the abstract methods:
       - __init__(): Set up your compiler's initial state
       - handleLine(): Process each transition rule (VarphiLine)  
       - generate_compiled_program(): Return the final compiled output
    
    2. Use the compile() function with your compiler instance:
       compiled_output = compile(varphi_program_text, your_compiler_instance)

Classes:
    VarphiCompiler: Abstract base class for implementing custom compilers.

Functions:
    compile: Parses a Varphi program and compiles it using the provided compiler.
"""

from abc import ABC, abstractmethod

from antlr4 import InputStream, CommonTokenStream, ParseTreeWalker

from .syntax.antlr.VarphiLexer import VarphiLexer
from .syntax.antlr.VarphiParser import VarphiParser
from .syntax.antlr.VarphiListener import VarphiListener
from .syntax.error_listener import VarphiSyntaxErrorListener
from .model import VarphiTapeCharacter, VarphiHeadDirection, VarphiLine


class VarphiCompiler(VarphiListener, ABC):
    """Abstract base class for compiling Varphi programs into target languages.
    
    Subclasses must implement the abstract methods to define compilation behavior.
    Inherits from VarphiListener to receive ANTLR parse tree events.
    
    Abstract Methods:
        __init__: Initialize compiler state
        handleLine: Process a single transition rule
        generate_compiled_program: Return the final compiled output
    """
    @abstractmethod
    def __init__(self) -> None:
        """Initialize the compiler's state and data structures."""


    @abstractmethod
    def handle_line(self, line: VarphiLine) -> None:
        """Process a single transition rule (line in the Varphi program).
        
        Args:
            line: The VarphiLine object representing a transition rule
        """


    @abstractmethod
    def generate_compiled_program(self) -> str:
        """Generate and return the final compiled program as a string.
        
        Returns:
            The complete compiled program in the target language
        """


    def enterLine(self, ctx: VarphiParser.LineContext) -> None:
        """Parse ANTLR line context and delegate to handleLine.
        
        Args:
            ctx: The ANTLR parser context for the line rule
        """
        if_state = str(ctx.STATE(0).getText())
        tape_character = VarphiTapeCharacter(ctx.TAPE_CHARACTER(0).getText())
        then_state = str(ctx.STATE(1).getText())
        then_character = VarphiTapeCharacter(ctx.TAPE_CHARACTER(1).getText())
        then_direction = VarphiHeadDirection(ctx.HEAD_DIRECTION().getText())
        line_number_in_source = ctx.start.line
        line = VarphiLine(if_state,
                          tape_character,
                          then_state,
                          then_character,
                          then_direction,
                          line_number_in_source)
        self.handle_line(line)



def compile_varphi(program: str, compiler: VarphiCompiler) -> str:
    """Parse and compile a Varphi program using the provided compiler.
    
    Args:
        program: The Varphi program source code as a string
        compiler: A VarphiCompiler instance to process the program
        
    Returns:
        The compiled program output from the compiler
    """
    input_stream = InputStream(program)
    error_listener = VarphiSyntaxErrorListener(program)
    lexer = VarphiLexer(input_stream)
    lexer.removeErrorListeners()
    lexer.addErrorListener(error_listener)
    token_stream = CommonTokenStream(lexer)
    parser = VarphiParser(token_stream)
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener)
    parse_tree = parser.program()
    walker = ParseTreeWalker()
    walker.walk(compiler, parse_tree)
    return compiler.generate_compiled_program()
