# Generated from src/varphi_devkit/syntax/Varphi.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .VarphiParser import VarphiParser
else:
    from VarphiParser import VarphiParser

# This class defines a complete listener for a parse tree produced by VarphiParser.
class VarphiListener(ParseTreeListener):

    # Enter a parse tree produced by VarphiParser#program.
    def enterProgram(self, ctx:VarphiParser.ProgramContext):
        pass

    # Exit a parse tree produced by VarphiParser#program.
    def exitProgram(self, ctx:VarphiParser.ProgramContext):
        pass


    # Enter a parse tree produced by VarphiParser#line.
    def enterLine(self, ctx:VarphiParser.LineContext):
        pass

    # Exit a parse tree produced by VarphiParser#line.
    def exitLine(self, ctx:VarphiParser.LineContext):
        pass



del VarphiParser