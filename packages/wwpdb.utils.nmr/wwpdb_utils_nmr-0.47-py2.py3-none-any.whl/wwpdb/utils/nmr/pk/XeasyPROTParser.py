# Generated from XeasyPROTParser.g4 by ANTLR 4.13.0
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
        0,12,0,12,1,0,5,0,16,8,0,10,0,12,0,19,9,0,1,0,1,0,1,1,1,1,1,1,1,
        1,1,1,1,1,3,1,29,8,1,1,2,1,2,1,2,0,0,3,0,2,4,0,2,1,1,8,8,2,0,1,1,
        6,6,33,0,7,1,0,0,0,2,22,1,0,0,0,4,30,1,0,0,0,6,8,5,8,0,0,7,6,1,0,
        0,0,7,8,1,0,0,0,8,10,1,0,0,0,9,11,3,2,1,0,10,9,1,0,0,0,11,12,1,0,
        0,0,12,10,1,0,0,0,12,13,1,0,0,0,13,17,1,0,0,0,14,16,5,8,0,0,15,14,
        1,0,0,0,16,19,1,0,0,0,17,15,1,0,0,0,17,18,1,0,0,0,18,20,1,0,0,0,
        19,17,1,0,0,0,20,21,5,0,0,1,21,1,1,0,0,0,22,23,5,1,0,0,23,24,5,2,
        0,0,24,25,5,2,0,0,25,26,5,6,0,0,26,28,3,4,2,0,27,29,7,0,0,0,28,27,
        1,0,0,0,28,29,1,0,0,0,29,3,1,0,0,0,30,31,7,1,0,0,31,5,1,0,0,0,4,
        7,12,17,28
    ]

class XeasyPROTParser ( Parser ):

    grammarFileName = "XeasyPROTParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [  ]

    symbolicNames = [ "<INVALID>", "Integer", "Float", "SHARP_COMMENT", 
                      "EXCLM_COMMENT", "SMCLN_COMMENT", "Simple_name", "SPACE", 
                      "RETURN", "ENCLOSE_COMMENT", "SECTION_COMMENT", "LINE_COMMENT" ]

    RULE_xeasy_prot = 0
    RULE_prot = 1
    RULE_residue = 2

    ruleNames =  [ "xeasy_prot", "prot", "residue" ]

    EOF = Token.EOF
    Integer=1
    Float=2
    SHARP_COMMENT=3
    EXCLM_COMMENT=4
    SMCLN_COMMENT=5
    Simple_name=6
    SPACE=7
    RETURN=8
    ENCLOSE_COMMENT=9
    SECTION_COMMENT=10
    LINE_COMMENT=11

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.0")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class Xeasy_protContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(XeasyPROTParser.EOF, 0)

        def RETURN(self, i:int=None):
            if i is None:
                return self.getTokens(XeasyPROTParser.RETURN)
            else:
                return self.getToken(XeasyPROTParser.RETURN, i)

        def prot(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(XeasyPROTParser.ProtContext)
            else:
                return self.getTypedRuleContext(XeasyPROTParser.ProtContext,i)


        def getRuleIndex(self):
            return XeasyPROTParser.RULE_xeasy_prot

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterXeasy_prot" ):
                listener.enterXeasy_prot(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitXeasy_prot" ):
                listener.exitXeasy_prot(self)




    def xeasy_prot(self):

        localctx = XeasyPROTParser.Xeasy_protContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_xeasy_prot)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 7
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==8:
                self.state = 6
                self.match(XeasyPROTParser.RETURN)


            self.state = 10 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 9
                self.prot()
                self.state = 12 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==1):
                    break

            self.state = 17
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==8:
                self.state = 14
                self.match(XeasyPROTParser.RETURN)
                self.state = 19
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 20
            self.match(XeasyPROTParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ProtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Integer(self):
            return self.getToken(XeasyPROTParser.Integer, 0)

        def Float(self, i:int=None):
            if i is None:
                return self.getTokens(XeasyPROTParser.Float)
            else:
                return self.getToken(XeasyPROTParser.Float, i)

        def Simple_name(self):
            return self.getToken(XeasyPROTParser.Simple_name, 0)

        def residue(self):
            return self.getTypedRuleContext(XeasyPROTParser.ResidueContext,0)


        def RETURN(self):
            return self.getToken(XeasyPROTParser.RETURN, 0)

        def EOF(self):
            return self.getToken(XeasyPROTParser.EOF, 0)

        def getRuleIndex(self):
            return XeasyPROTParser.RULE_prot

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterProt" ):
                listener.enterProt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitProt" ):
                listener.exitProt(self)




    def prot(self):

        localctx = XeasyPROTParser.ProtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_prot)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 22
            self.match(XeasyPROTParser.Integer)
            self.state = 23
            self.match(XeasyPROTParser.Float)
            self.state = 24
            self.match(XeasyPROTParser.Float)
            self.state = 25
            self.match(XeasyPROTParser.Simple_name)
            self.state = 26
            self.residue()
            self.state = 28
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,3,self._ctx)
            if la_ == 1:
                self.state = 27
                _la = self._input.LA(1)
                if not(_la==-1 or _la==8):
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


    class ResidueContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Integer(self):
            return self.getToken(XeasyPROTParser.Integer, 0)

        def Simple_name(self):
            return self.getToken(XeasyPROTParser.Simple_name, 0)

        def getRuleIndex(self):
            return XeasyPROTParser.RULE_residue

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterResidue" ):
                listener.enterResidue(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitResidue" ):
                listener.exitResidue(self)




    def residue(self):

        localctx = XeasyPROTParser.ResidueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_residue)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 30
            _la = self._input.LA(1)
            if not(_la==1 or _la==6):
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





