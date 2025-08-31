"""Data model for representing Varphi language programs.

This module provides the core data types for representing Varphi programs
(Turing machine descriptions) including tape characters, head directions,
and transition rules.

Classes:
    VarphiTapeCharacter: Enum for possible tape characters (0, 1).
    VarphiHeadDirection: Enum for head movement directions (L, R).
    VarphiLine: Dataclass representing a single transition rule.
"""

from enum import Enum
from dataclasses import dataclass

class VarphiTapeCharacter(Enum):
    """Represents the possible characters on a Turing machine tape.
    
    Attributes:
        BLANK: Represents a blank/empty tape cell (character '0').
        TALLY: Represents a marked tape cell (character '1').
    """
    BLANK = "0"
    TALLY = "1"


class VarphiHeadDirection(Enum):
    """Represents the possible head movement directions for the Turing machine head.
    
    Attributes:
        LEFT: Move the head one position to the left (character 'L').
        RIGHT: Move the head one position to the right (character 'R').
    """
    LEFT = "L"
    RIGHT = "R"


@dataclass
class VarphiLine:
    """Represents a single line (transition rule) in a Varphi program.
    
    Attributes:
        if_state: current state
        if_character: current tape character
        then_state: next state
        then_character: character to write
        then_direction: direction to move the head
        line_number_in_source: the corresponding line number in the original source Varphi program
    """
    if_state: str
    if_character: VarphiTapeCharacter
    then_state: str
    then_character: VarphiTapeCharacter
    then_direction: VarphiHeadDirection
    line_number_in_source: int
