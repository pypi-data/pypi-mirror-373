# Generated from PpmCSParser.g4 by ANTLR 4.13.0
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,11,33,2,0,7,0,2,1,7,1,2,2,7,2,1,0,3,0,8,8,0,1,0,4,0,11,8,0,11,
        0,12,0,12,1,0,5,0,16,8,0,10,0,12,0,19,9,0,1,0,1,0,1,1,1,1,1,1,3,
        1,26,8,1,1,1,3,1,29,8,1,1,2,1,2,1,2,0,0,3,0,2,4,0,3,1,0,5,7,1,1,
        9,9,2,0,1,2,7,7,34,0,7,1,0,0,0,2,22,1,0,0,0,4,30,1,0,0,0,6,8,5,9,
        0,0,7,6,1,0,0,0,7,8,1,0,0,0,8,10,1,0,0,0,9,11,3,2,1,0,10,9,1,0,0,
        0,11,12,1,0,0,0,12,10,1,0,0,0,12,13,1,0,0,0,13,17,1,0,0,0,14,16,
        5,9,0,0,15,14,1,0,0,0,16,19,1,0,0,0,17,15,1,0,0,0,17,18,1,0,0,0,
        18,20,1,0,0,0,19,17,1,0,0,0,20,21,5,0,0,1,21,1,1,0,0,0,22,23,7,0,
        0,0,23,25,3,4,2,0,24,26,5,1,0,0,25,24,1,0,0,0,25,26,1,0,0,0,26,28,
        1,0,0,0,27,29,7,1,0,0,28,27,1,0,0,0,28,29,1,0,0,0,29,3,1,0,0,0,30,
        31,7,2,0,0,31,5,1,0,0,0,5,7,12,17,25,28
    ]

class PpmCSParser ( Parser ):

    grammarFileName = "PpmCSParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [  ]

    symbolicNames = [ "<INVALID>", "Integer", "Float", "SHARP_COMMENT", 
                      "EXCLM_COMMENT", "Atom_selection_2d_ex", "Atom_selection_3d_ex", 
                      "Simple_name", "SPACE", "RETURN", "SECTION_COMMENT", 
                      "LINE_COMMENT" ]

    RULE_ppm_cs = 0
    RULE_ppm_list = 1
    RULE_number = 2

    ruleNames =  [ "ppm_cs", "ppm_list", "number" ]

    EOF = Token.EOF
    Integer=1
    Float=2
    SHARP_COMMENT=3
    EXCLM_COMMENT=4
    Atom_selection_2d_ex=5
    Atom_selection_3d_ex=6
    Simple_name=7
    SPACE=8
    RETURN=9
    SECTION_COMMENT=10
    LINE_COMMENT=11

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.0")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class Ppm_csContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(PpmCSParser.EOF, 0)

        def RETURN(self, i:int=None):
            if i is None:
                return self.getTokens(PpmCSParser.RETURN)
            else:
                return self.getToken(PpmCSParser.RETURN, i)

        def ppm_list(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PpmCSParser.Ppm_listContext)
            else:
                return self.getTypedRuleContext(PpmCSParser.Ppm_listContext,i)


        def getRuleIndex(self):
            return PpmCSParser.RULE_ppm_cs

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPpm_cs" ):
                listener.enterPpm_cs(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPpm_cs" ):
                listener.exitPpm_cs(self)




    def ppm_cs(self):

        localctx = PpmCSParser.Ppm_csContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_ppm_cs)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 7
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==9:
                self.state = 6
                self.match(PpmCSParser.RETURN)


            self.state = 10 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 9
                self.ppm_list()
                self.state = 12 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & 224) != 0)):
                    break

            self.state = 17
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==9:
                self.state = 14
                self.match(PpmCSParser.RETURN)
                self.state = 19
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 20
            self.match(PpmCSParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Ppm_listContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def number(self):
            return self.getTypedRuleContext(PpmCSParser.NumberContext,0)


        def Simple_name(self):
            return self.getToken(PpmCSParser.Simple_name, 0)

        def Atom_selection_2d_ex(self):
            return self.getToken(PpmCSParser.Atom_selection_2d_ex, 0)

        def Atom_selection_3d_ex(self):
            return self.getToken(PpmCSParser.Atom_selection_3d_ex, 0)

        def Integer(self):
            return self.getToken(PpmCSParser.Integer, 0)

        def RETURN(self):
            return self.getToken(PpmCSParser.RETURN, 0)

        def EOF(self):
            return self.getToken(PpmCSParser.EOF, 0)

        def getRuleIndex(self):
            return PpmCSParser.RULE_ppm_list

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPpm_list" ):
                listener.enterPpm_list(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPpm_list" ):
                listener.exitPpm_list(self)




    def ppm_list(self):

        localctx = PpmCSParser.Ppm_listContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_ppm_list)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 22
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 224) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 23
            self.number()
            self.state = 25
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1:
                self.state = 24
                self.match(PpmCSParser.Integer)


            self.state = 28
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,4,self._ctx)
            if la_ == 1:
                self.state = 27
                _la = self._input.LA(1)
                if not(_la==-1 or _la==9):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class NumberContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Float(self):
            return self.getToken(PpmCSParser.Float, 0)

        def Integer(self):
            return self.getToken(PpmCSParser.Integer, 0)

        def Simple_name(self):
            return self.getToken(PpmCSParser.Simple_name, 0)

        def getRuleIndex(self):
            return PpmCSParser.RULE_number

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNumber" ):
                listener.enterNumber(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNumber" ):
                listener.exitNumber(self)




    def number(self):

        localctx = PpmCSParser.NumberContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_number)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 30
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 134) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





