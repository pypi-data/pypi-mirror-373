# Varphi Development Kit

A Python framework for creating compilers that target the Varphi language - a domain-specific language for describing Turing machine transition rules.

## Overview

Varphi is a minimalist language designed to represent Turing machine programs using simple transition rules. The Varphi Development Kit provides a flexible compiler framework that allows you to build custom compilers to transform Varphi programs into any target format.

## Installation

```bash
pip install varphi-devkit
```

**Requirements:**
- Python ≥ 3.10

## Varphi Language Syntax

Varphi programs consist of transition rules with the following syntax:

```
STATE TAPE_CHARACTER STATE TAPE_CHARACTER HEAD_DIRECTION
```

Where:
- **STATE**: Current/target state (format: `q` followed by alphanumeric characters, e.g., `q0`, `q_start`, `q1_accept`)
- **TAPE_CHARACTER**: Tape symbol (`0` for blank, `1` for marked)
- **HEAD_DIRECTION**: Head movement (`L` for left, `R` for right)

### Example Varphi Program

```varphi
// Simple addition-by-one program
q0 1 q0 1 R
q0 0 qHalt 1 R
```

### Language Features

- **Comments**: Single-line (`//`) and multi-line (`/* */`) comments are supported
- **Whitespace**: Flexible whitespace handling (spaces, tabs, newlines)
- **States**: Flexible state naming with `q` prefix

## Core Architecture

The framework is built around these key components:

### Data Model

- **`VarphiTapeCharacter`**: Enum for tape symbols (`BLANK="0"`, `TALLY="1"`)
- **`VarphiHeadDirection`**: Enum for head movement (`LEFT="L"`, `RIGHT="R"`)
- **`VarphiLine`**: Dataclass representing a transition rule with fields:
  - `if_state`: Current state
  - `if_character`: Current tape character
  - `then_state`: Next state  
  - `then_character`: Character to write
  - `then_direction`: Direction to move

### Compiler Framework

- **`VarphiCompiler`**: Abstract base class for implementing custom compilers
- **`compile_varphi()`**: Function to parse and compile Varphi programs
- **`VarphiSyntaxError`**: Exception for syntax errors

## Usage

### Creating a Custom Compiler

To create a Varphi compiler, subclass `VarphiCompiler` and implement three methods:

```python
from varphi_devkit import VarphiCompiler, VarphiLine, compile_varphi

class MyCompiler(VarphiCompiler):
    def __init__(self):
        # Initialize your compiler's state
        self.output = []
    
    def handle_line(self, line: VarphiLine):
        # Process each transition rule
        self.output.append(f"Transition: {line.if_state} -> {line.then_state}")
    
    def generate_compiled_program(self) -> str:
        # Return the final compiled output
        return "\n".join(self.output)

# Use your compiler
program = """
q0 0 q1 1 R
q1 1 q_halt 0 L
"""

compiler = MyCompiler()
result = compile_varphi(program, compiler)
print(result)
```

## Example Toy Compilers

The framework's test suite includes several [example compilers](/tests/toy_compilers) that demonstrate different use cases.

## Error Handling

The framework provides comprehensive syntax error reporting out of the box:

```python
from varphi_devkit import VarphiSyntaxError, compile_varphi
from your_compiler import YourCompiler

try:
    result = compile_varphi("invalid syntax here", YourCompiler())
except VarphiSyntaxError as e:
    print(f"Syntax error at line {e.line}, column {e.column}: {e.message}")
```

## API Reference

### Core Functions

#### `compile_varphi(program: str, compiler: VarphiCompiler) -> str`

Parses and compiles a Varphi program using the provided compiler.

- **Parameters:**
  - `program`: Varphi source code as a string
  - `compiler`: VarphiCompiler instance to process the program
- **Returns:** Compiled program output from the compiler
- **Raises:** `VarphiSyntaxError` for invalid syntax

### Abstract Base Class

#### `VarphiCompiler`

Abstract base class for implementing custom Varphi compilers.

**Abstract Methods:**
- `__init__(self) -> None`: Initialize compiler state
- `handle_line(self, line: VarphiLine) -> None`: Process a transition rule (line in the Varphi program)
- `generate_compiled_program(self) -> str`: Return final compiled output

### Data Classes

#### `VarphiLine`

Represents a single transition rule with attributes:
- `if_state: str` - Current state
- `if_character: VarphiTapeCharacter` - Current tape character
- `then_state: str` - Next state
- `then_character: VarphiTapeCharacter` - Character to write
- `then_direction: VarphiHeadDirection` - Head movement direction

#### `VarphiTapeCharacter`

Enum for tape characters:
- `BLANK = "0"` - Empty tape cell
- `TALLY = "1"` - Marked tape cell

#### `VarphiHeadDirection`

Enum for head movement:
- `LEFT = "L"` - Move head left
- `RIGHT = "R"` - Move head right

### Exceptions

#### `VarphiSyntaxError`

Exception raised for syntax errors in Varphi programs.

**Attributes:**
- `message: str` - Error description
- `line: int` - Line number where error occurred
- `column: int` - Column position of error

## License

This project is available under the BSD-3-Clause License (see [LICENSE](LICENSE)).
