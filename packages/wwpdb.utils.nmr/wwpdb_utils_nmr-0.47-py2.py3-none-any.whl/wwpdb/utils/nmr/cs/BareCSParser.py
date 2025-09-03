# Generated from BareCSParser.g4 by ANTLR 4.13.0
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
        4,1,12,48,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,1,0,3,0,10,8,0,1,0,1,0,
        5,0,14,8,0,10,0,12,0,17,9,0,1,0,1,0,1,1,4,1,22,8,1,11,1,12,1,23,
        1,1,4,1,27,8,1,11,1,12,1,28,3,1,31,8,1,1,1,1,1,4,1,35,8,1,11,1,12,
        1,36,1,2,4,2,40,8,2,11,2,12,2,41,1,2,1,2,1,3,1,3,1,3,0,0,4,0,2,4,
        6,0,2,1,1,10,10,2,0,1,2,5,8,51,0,9,1,0,0,0,2,30,1,0,0,0,4,39,1,0,
        0,0,6,45,1,0,0,0,8,10,5,10,0,0,9,8,1,0,0,0,9,10,1,0,0,0,10,15,1,
        0,0,0,11,14,3,2,1,0,12,14,5,10,0,0,13,11,1,0,0,0,13,12,1,0,0,0,14,
        17,1,0,0,0,15,13,1,0,0,0,15,16,1,0,0,0,16,18,1,0,0,0,17,15,1,0,0,
        0,18,19,5,0,0,1,19,1,1,0,0,0,20,22,5,5,0,0,21,20,1,0,0,0,22,23,1,
        0,0,0,23,21,1,0,0,0,23,24,1,0,0,0,24,31,1,0,0,0,25,27,5,6,0,0,26,
        25,1,0,0,0,27,28,1,0,0,0,28,26,1,0,0,0,28,29,1,0,0,0,29,31,1,0,0,
        0,30,21,1,0,0,0,30,26,1,0,0,0,31,32,1,0,0,0,32,34,5,10,0,0,33,35,
        3,4,2,0,34,33,1,0,0,0,35,36,1,0,0,0,36,34,1,0,0,0,36,37,1,0,0,0,
        37,3,1,0,0,0,38,40,3,6,3,0,39,38,1,0,0,0,40,41,1,0,0,0,41,39,1,0,
        0,0,41,42,1,0,0,0,42,43,1,0,0,0,43,44,7,0,0,0,44,5,1,0,0,0,45,46,
        7,1,0,0,46,7,1,0,0,0,8,9,13,15,23,28,30,36,41
    ]

class BareCSParser ( Parser ):

    grammarFileName = "BareCSParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [  ]

    symbolicNames = [ "<INVALID>", "Integer", "Float", "SHARP_COMMENT", 
                      "EXCLM_COMMENT", "Simple_name", "Double_quote_string", 
                      "Double_quote_integer", "Double_quote_float", "SPACE", 
                      "RETURN", "SECTION_COMMENT", "LINE_COMMENT" ]

    RULE_bare_cs = 0
    RULE_cs_raw_format = 1
    RULE_cs_raw_list = 2
    RULE_any = 3

    ruleNames =  [ "bare_cs", "cs_raw_format", "cs_raw_list", "any" ]

    EOF = Token.EOF
    Integer=1
    Float=2
    SHARP_COMMENT=3
    EXCLM_COMMENT=4
    Simple_name=5
    Double_quote_string=6
    Double_quote_integer=7
    Double_quote_float=8
    SPACE=9
    RETURN=10
    SECTION_COMMENT=11
    LINE_COMMENT=12

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.0")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class Bare_csContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(BareCSParser.EOF, 0)

        def RETURN(self, i:int=None):
            if i is None:
                return self.getTokens(BareCSParser.RETURN)
            else:
                return self.getToken(BareCSParser.RETURN, i)

        def cs_raw_format(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BareCSParser.Cs_raw_formatContext)
            else:
                return self.getTypedRuleContext(BareCSParser.Cs_raw_formatContext,i)


        def getRuleIndex(self):
            return BareCSParser.RULE_bare_cs

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBare_cs" ):
                listener.enterBare_cs(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBare_cs" ):
                listener.exitBare_cs(self)




    def bare_cs(self):

        localctx = BareCSParser.Bare_csContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_bare_cs)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 9
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,0,self._ctx)
            if la_ == 1:
                self.state = 8
                self.match(BareCSParser.RETURN)


            self.state = 15
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 1120) != 0):
                self.state = 13
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [5, 6]:
                    self.state = 11
                    self.cs_raw_format()
                    pass
                elif token in [10]:
                    self.state = 12
                    self.match(BareCSParser.RETURN)
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 17
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 18
            self.match(BareCSParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Cs_raw_formatContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def RETURN(self):
            return self.getToken(BareCSParser.RETURN, 0)

        def cs_raw_list(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BareCSParser.Cs_raw_listContext)
            else:
                return self.getTypedRuleContext(BareCSParser.Cs_raw_listContext,i)


        def Simple_name(self, i:int=None):
            if i is None:
                return self.getTokens(BareCSParser.Simple_name)
            else:
                return self.getToken(BareCSParser.Simple_name, i)

        def Double_quote_string(self, i:int=None):
            if i is None:
                return self.getTokens(BareCSParser.Double_quote_string)
            else:
                return self.getToken(BareCSParser.Double_quote_string, i)

        def getRuleIndex(self):
            return BareCSParser.RULE_cs_raw_format

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCs_raw_format" ):
                listener.enterCs_raw_format(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCs_raw_format" ):
                listener.exitCs_raw_format(self)




    def cs_raw_format(self):

        localctx = BareCSParser.Cs_raw_formatContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_cs_raw_format)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 30
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [5]:
                self.state = 21 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 20
                    self.match(BareCSParser.Simple_name)
                    self.state = 23 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==5):
                        break

                pass
            elif token in [6]:
                self.state = 26 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 25
                    self.match(BareCSParser.Double_quote_string)
                    self.state = 28 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==6):
                        break

                pass
            else:
                raise NoViableAltException(self)

            self.state = 32
            self.match(BareCSParser.RETURN)
            self.state = 34 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 33
                    self.cs_raw_list()

                else:
                    raise NoViableAltException(self)
                self.state = 36 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,6,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Cs_raw_listContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def RETURN(self):
            return self.getToken(BareCSParser.RETURN, 0)

        def EOF(self):
            return self.getToken(BareCSParser.EOF, 0)

        def any_(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BareCSParser.AnyContext)
            else:
                return self.getTypedRuleContext(BareCSParser.AnyContext,i)


        def getRuleIndex(self):
            return BareCSParser.RULE_cs_raw_list

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCs_raw_list" ):
                listener.enterCs_raw_list(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCs_raw_list" ):
                listener.exitCs_raw_list(self)




    def cs_raw_list(self):

        localctx = BareCSParser.Cs_raw_listContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_cs_raw_list)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 39 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 38
                self.any_()
                self.state = 41 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & 486) != 0)):
                    break

            self.state = 43
            _la = self._input.LA(1)
            if not(_la==-1 or _la==10):
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


    class AnyContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Float(self):
            return self.getToken(BareCSParser.Float, 0)

        def Integer(self):
            return self.getToken(BareCSParser.Integer, 0)

        def Simple_name(self):
            return self.getToken(BareCSParser.Simple_name, 0)

        def Double_quote_float(self):
            return self.getToken(BareCSParser.Double_quote_float, 0)

        def Double_quote_integer(self):
            return self.getToken(BareCSParser.Double_quote_integer, 0)

        def Double_quote_string(self):
            return self.getToken(BareCSParser.Double_quote_string, 0)

        def getRuleIndex(self):
            return BareCSParser.RULE_any

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAny" ):
                listener.enterAny(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAny" ):
                listener.exitAny(self)




    def any_(self):

        localctx = BareCSParser.AnyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_any)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 45
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 486) != 0)):
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





