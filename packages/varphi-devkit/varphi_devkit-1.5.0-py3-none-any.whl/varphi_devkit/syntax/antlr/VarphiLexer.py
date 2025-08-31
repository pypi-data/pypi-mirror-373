# Generated from src/varphi_devkit/syntax/Varphi.g4 by ANTLR 4.13.2
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
    from typing import TextIO
else:
    from typing.io import TextIO


def serializedATN():
    return [
        4,0,6,75,6,-1,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,
        6,7,6,2,7,7,7,2,8,7,8,2,9,7,9,1,0,1,0,1,1,1,1,1,2,1,2,1,3,1,3,1,
        4,1,4,4,4,32,8,4,11,4,12,4,33,1,5,1,5,3,5,38,8,5,1,6,1,6,3,6,42,
        8,6,1,7,1,7,1,7,1,7,5,7,48,8,7,10,7,12,7,51,9,7,1,7,1,7,1,8,1,8,
        1,8,1,8,5,8,59,8,8,10,8,12,8,62,9,8,1,8,1,8,1,8,1,8,1,8,1,9,4,9,
        70,8,9,11,9,12,9,71,1,9,1,9,1,60,0,10,1,0,3,0,5,0,7,0,9,1,11,2,13,
        3,15,4,17,5,19,6,1,0,3,4,0,48,57,65,90,95,95,97,122,2,0,10,10,13,
        13,3,0,9,10,13,13,32,32,76,0,9,1,0,0,0,0,11,1,0,0,0,0,13,1,0,0,0,
        0,15,1,0,0,0,0,17,1,0,0,0,0,19,1,0,0,0,1,21,1,0,0,0,3,23,1,0,0,0,
        5,25,1,0,0,0,7,27,1,0,0,0,9,29,1,0,0,0,11,37,1,0,0,0,13,41,1,0,0,
        0,15,43,1,0,0,0,17,54,1,0,0,0,19,69,1,0,0,0,21,22,5,76,0,0,22,2,
        1,0,0,0,23,24,5,82,0,0,24,4,1,0,0,0,25,26,5,49,0,0,26,6,1,0,0,0,
        27,28,5,48,0,0,28,8,1,0,0,0,29,31,5,113,0,0,30,32,7,0,0,0,31,30,
        1,0,0,0,32,33,1,0,0,0,33,31,1,0,0,0,33,34,1,0,0,0,34,10,1,0,0,0,
        35,38,3,5,2,0,36,38,3,7,3,0,37,35,1,0,0,0,37,36,1,0,0,0,38,12,1,
        0,0,0,39,42,3,1,0,0,40,42,3,3,1,0,41,39,1,0,0,0,41,40,1,0,0,0,42,
        14,1,0,0,0,43,44,5,47,0,0,44,45,5,47,0,0,45,49,1,0,0,0,46,48,8,1,
        0,0,47,46,1,0,0,0,48,51,1,0,0,0,49,47,1,0,0,0,49,50,1,0,0,0,50,52,
        1,0,0,0,51,49,1,0,0,0,52,53,6,7,0,0,53,16,1,0,0,0,54,55,5,47,0,0,
        55,56,5,42,0,0,56,60,1,0,0,0,57,59,9,0,0,0,58,57,1,0,0,0,59,62,1,
        0,0,0,60,61,1,0,0,0,60,58,1,0,0,0,61,63,1,0,0,0,62,60,1,0,0,0,63,
        64,5,42,0,0,64,65,5,47,0,0,65,66,1,0,0,0,66,67,6,8,0,0,67,18,1,0,
        0,0,68,70,7,2,0,0,69,68,1,0,0,0,70,71,1,0,0,0,71,69,1,0,0,0,71,72,
        1,0,0,0,72,73,1,0,0,0,73,74,6,9,0,0,74,20,1,0,0,0,7,0,33,37,41,49,
        60,71,1,6,0,0
    ]

class VarphiLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    STATE = 1
    TAPE_CHARACTER = 2
    HEAD_DIRECTION = 3
    COMMENT = 4
    MULTI_COMMENT = 5
    WHITESPACE = 6

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
 ]

    symbolicNames = [ "<INVALID>",
            "STATE", "TAPE_CHARACTER", "HEAD_DIRECTION", "COMMENT", "MULTI_COMMENT", 
            "WHITESPACE" ]

    ruleNames = [ "LEFT", "RIGHT", "TALLY", "BLANK", "STATE", "TAPE_CHARACTER", 
                  "HEAD_DIRECTION", "COMMENT", "MULTI_COMMENT", "WHITESPACE" ]

    grammarFileName = "Varphi.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


