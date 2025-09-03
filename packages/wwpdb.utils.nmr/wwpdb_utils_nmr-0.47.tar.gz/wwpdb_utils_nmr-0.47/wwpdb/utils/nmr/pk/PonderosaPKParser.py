# Generated from PonderosaPKParser.g4 by ANTLR 4.13.0
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
        4,1,21,99,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,1,0,3,0,18,8,0,1,0,1,0,1,0,1,0,5,0,24,8,0,10,0,12,0,27,
        9,0,1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,4,1,40,8,1,11,1,
        12,1,41,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,3,1,3,1,3,1,3,1,3,1,3,1,3,
        1,3,1,3,4,3,60,8,3,11,3,12,3,61,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,
        1,4,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,4,5,82,8,5,11,5,12,5,83,
        1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,7,1,7,1,7,0,0,8,0,
        2,4,6,8,10,12,14,0,2,1,1,11,11,1,0,4,5,98,0,17,1,0,0,0,2,30,1,0,
        0,0,4,43,1,0,0,0,6,50,1,0,0,0,8,63,1,0,0,0,10,72,1,0,0,0,12,85,1,
        0,0,0,14,96,1,0,0,0,16,18,5,11,0,0,17,16,1,0,0,0,17,18,1,0,0,0,18,
        25,1,0,0,0,19,24,3,2,1,0,20,24,3,6,3,0,21,24,3,10,5,0,22,24,5,11,
        0,0,23,19,1,0,0,0,23,20,1,0,0,0,23,21,1,0,0,0,23,22,1,0,0,0,24,27,
        1,0,0,0,25,23,1,0,0,0,25,26,1,0,0,0,26,28,1,0,0,0,27,25,1,0,0,0,
        28,29,5,0,0,1,29,1,1,0,0,0,30,31,5,1,0,0,31,32,5,14,0,0,32,33,5,
        15,0,0,33,34,5,17,0,0,34,35,5,2,0,0,35,36,5,18,0,0,36,37,5,19,0,
        0,37,39,5,21,0,0,38,40,3,4,2,0,39,38,1,0,0,0,40,41,1,0,0,0,41,39,
        1,0,0,0,41,42,1,0,0,0,42,3,1,0,0,0,43,44,5,4,0,0,44,45,5,4,0,0,45,
        46,3,14,7,0,46,47,5,9,0,0,47,48,5,9,0,0,48,49,7,0,0,0,49,5,1,0,0,
        0,50,51,5,1,0,0,51,52,5,14,0,0,52,53,5,15,0,0,53,54,5,17,0,0,54,
        55,5,2,0,0,55,56,5,18,0,0,56,57,5,19,0,0,57,59,5,21,0,0,58,60,3,
        8,4,0,59,58,1,0,0,0,60,61,1,0,0,0,61,59,1,0,0,0,61,62,1,0,0,0,62,
        7,1,0,0,0,63,64,5,4,0,0,64,65,5,4,0,0,65,66,5,4,0,0,66,67,3,14,7,
        0,67,68,5,9,0,0,68,69,5,9,0,0,69,70,5,9,0,0,70,71,7,0,0,0,71,9,1,
        0,0,0,72,73,5,1,0,0,73,74,5,14,0,0,74,75,5,15,0,0,75,76,5,17,0,0,
        76,77,5,2,0,0,77,78,5,18,0,0,78,79,5,19,0,0,79,81,5,21,0,0,80,82,
        3,12,6,0,81,80,1,0,0,0,82,83,1,0,0,0,83,81,1,0,0,0,83,84,1,0,0,0,
        84,11,1,0,0,0,85,86,5,4,0,0,86,87,5,4,0,0,87,88,5,4,0,0,88,89,5,
        4,0,0,89,90,3,14,7,0,90,91,5,9,0,0,91,92,5,9,0,0,92,93,5,9,0,0,93,
        94,5,9,0,0,94,95,7,0,0,0,95,13,1,0,0,0,96,97,7,1,0,0,97,15,1,0,0,
        0,6,17,23,25,41,61,83
    ]

class PonderosaPKParser ( Parser ):

    grammarFileName = "PonderosaPKParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'NOESYTYPE'", "'AXISORDER'" ]

    symbolicNames = [ "<INVALID>", "Noesy_type", "Axis_order", "Integer", 
                      "Float", "Real", "SHARP_COMMENT", "EXCLM_COMMENT", 
                      "SMCLN_COMMENT", "Simple_name", "SPACE", "RETURN", 
                      "SECTION_COMMENT", "LINE_COMMENT", "Integer_NT", "Simple_name_NT", 
                      "SPACE_NT", "RETURN_NT", "Integer_AO", "Simple_name_AO", 
                      "SPACE_AO", "RETURN_AO" ]

    RULE_ponderosa_pk = 0
    RULE_peak_list_2d = 1
    RULE_peak_2d = 2
    RULE_peak_list_3d = 3
    RULE_peak_3d = 4
    RULE_peak_list_4d = 5
    RULE_peak_4d = 6
    RULE_number = 7

    ruleNames =  [ "ponderosa_pk", "peak_list_2d", "peak_2d", "peak_list_3d", 
                   "peak_3d", "peak_list_4d", "peak_4d", "number" ]

    EOF = Token.EOF
    Noesy_type=1
    Axis_order=2
    Integer=3
    Float=4
    Real=5
    SHARP_COMMENT=6
    EXCLM_COMMENT=7
    SMCLN_COMMENT=8
    Simple_name=9
    SPACE=10
    RETURN=11
    SECTION_COMMENT=12
    LINE_COMMENT=13
    Integer_NT=14
    Simple_name_NT=15
    SPACE_NT=16
    RETURN_NT=17
    Integer_AO=18
    Simple_name_AO=19
    SPACE_AO=20
    RETURN_AO=21

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.0")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class Ponderosa_pkContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(PonderosaPKParser.EOF, 0)

        def RETURN(self, i:int=None):
            if i is None:
                return self.getTokens(PonderosaPKParser.RETURN)
            else:
                return self.getToken(PonderosaPKParser.RETURN, i)

        def peak_list_2d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PonderosaPKParser.Peak_list_2dContext)
            else:
                return self.getTypedRuleContext(PonderosaPKParser.Peak_list_2dContext,i)


        def peak_list_3d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PonderosaPKParser.Peak_list_3dContext)
            else:
                return self.getTypedRuleContext(PonderosaPKParser.Peak_list_3dContext,i)


        def peak_list_4d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PonderosaPKParser.Peak_list_4dContext)
            else:
                return self.getTypedRuleContext(PonderosaPKParser.Peak_list_4dContext,i)


        def getRuleIndex(self):
            return PonderosaPKParser.RULE_ponderosa_pk

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPonderosa_pk" ):
                listener.enterPonderosa_pk(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPonderosa_pk" ):
                listener.exitPonderosa_pk(self)




    def ponderosa_pk(self):

        localctx = PonderosaPKParser.Ponderosa_pkContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_ponderosa_pk)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 17
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,0,self._ctx)
            if la_ == 1:
                self.state = 16
                self.match(PonderosaPKParser.RETURN)


            self.state = 25
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==1 or _la==11:
                self.state = 23
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,1,self._ctx)
                if la_ == 1:
                    self.state = 19
                    self.peak_list_2d()
                    pass

                elif la_ == 2:
                    self.state = 20
                    self.peak_list_3d()
                    pass

                elif la_ == 3:
                    self.state = 21
                    self.peak_list_4d()
                    pass

                elif la_ == 4:
                    self.state = 22
                    self.match(PonderosaPKParser.RETURN)
                    pass


                self.state = 27
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 28
            self.match(PonderosaPKParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Peak_list_2dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Noesy_type(self):
            return self.getToken(PonderosaPKParser.Noesy_type, 0)

        def Integer_NT(self):
            return self.getToken(PonderosaPKParser.Integer_NT, 0)

        def Simple_name_NT(self):
            return self.getToken(PonderosaPKParser.Simple_name_NT, 0)

        def RETURN_NT(self):
            return self.getToken(PonderosaPKParser.RETURN_NT, 0)

        def Axis_order(self):
            return self.getToken(PonderosaPKParser.Axis_order, 0)

        def Integer_AO(self):
            return self.getToken(PonderosaPKParser.Integer_AO, 0)

        def Simple_name_AO(self):
            return self.getToken(PonderosaPKParser.Simple_name_AO, 0)

        def RETURN_AO(self):
            return self.getToken(PonderosaPKParser.RETURN_AO, 0)

        def peak_2d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PonderosaPKParser.Peak_2dContext)
            else:
                return self.getTypedRuleContext(PonderosaPKParser.Peak_2dContext,i)


        def getRuleIndex(self):
            return PonderosaPKParser.RULE_peak_list_2d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPeak_list_2d" ):
                listener.enterPeak_list_2d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPeak_list_2d" ):
                listener.exitPeak_list_2d(self)




    def peak_list_2d(self):

        localctx = PonderosaPKParser.Peak_list_2dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_peak_list_2d)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 30
            self.match(PonderosaPKParser.Noesy_type)
            self.state = 31
            self.match(PonderosaPKParser.Integer_NT)
            self.state = 32
            self.match(PonderosaPKParser.Simple_name_NT)
            self.state = 33
            self.match(PonderosaPKParser.RETURN_NT)
            self.state = 34
            self.match(PonderosaPKParser.Axis_order)
            self.state = 35
            self.match(PonderosaPKParser.Integer_AO)
            self.state = 36
            self.match(PonderosaPKParser.Simple_name_AO)
            self.state = 37
            self.match(PonderosaPKParser.RETURN_AO)
            self.state = 39 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 38
                self.peak_2d()
                self.state = 41 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==4):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Peak_2dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Float(self, i:int=None):
            if i is None:
                return self.getTokens(PonderosaPKParser.Float)
            else:
                return self.getToken(PonderosaPKParser.Float, i)

        def number(self):
            return self.getTypedRuleContext(PonderosaPKParser.NumberContext,0)


        def Simple_name(self, i:int=None):
            if i is None:
                return self.getTokens(PonderosaPKParser.Simple_name)
            else:
                return self.getToken(PonderosaPKParser.Simple_name, i)

        def RETURN(self):
            return self.getToken(PonderosaPKParser.RETURN, 0)

        def EOF(self):
            return self.getToken(PonderosaPKParser.EOF, 0)

        def getRuleIndex(self):
            return PonderosaPKParser.RULE_peak_2d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPeak_2d" ):
                listener.enterPeak_2d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPeak_2d" ):
                listener.exitPeak_2d(self)




    def peak_2d(self):

        localctx = PonderosaPKParser.Peak_2dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_peak_2d)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 43
            self.match(PonderosaPKParser.Float)
            self.state = 44
            self.match(PonderosaPKParser.Float)
            self.state = 45
            self.number()
            self.state = 46
            self.match(PonderosaPKParser.Simple_name)
            self.state = 47
            self.match(PonderosaPKParser.Simple_name)
            self.state = 48
            _la = self._input.LA(1)
            if not(_la==-1 or _la==11):
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


    class Peak_list_3dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Noesy_type(self):
            return self.getToken(PonderosaPKParser.Noesy_type, 0)

        def Integer_NT(self):
            return self.getToken(PonderosaPKParser.Integer_NT, 0)

        def Simple_name_NT(self):
            return self.getToken(PonderosaPKParser.Simple_name_NT, 0)

        def RETURN_NT(self):
            return self.getToken(PonderosaPKParser.RETURN_NT, 0)

        def Axis_order(self):
            return self.getToken(PonderosaPKParser.Axis_order, 0)

        def Integer_AO(self):
            return self.getToken(PonderosaPKParser.Integer_AO, 0)

        def Simple_name_AO(self):
            return self.getToken(PonderosaPKParser.Simple_name_AO, 0)

        def RETURN_AO(self):
            return self.getToken(PonderosaPKParser.RETURN_AO, 0)

        def peak_3d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PonderosaPKParser.Peak_3dContext)
            else:
                return self.getTypedRuleContext(PonderosaPKParser.Peak_3dContext,i)


        def getRuleIndex(self):
            return PonderosaPKParser.RULE_peak_list_3d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPeak_list_3d" ):
                listener.enterPeak_list_3d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPeak_list_3d" ):
                listener.exitPeak_list_3d(self)




    def peak_list_3d(self):

        localctx = PonderosaPKParser.Peak_list_3dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_peak_list_3d)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 50
            self.match(PonderosaPKParser.Noesy_type)
            self.state = 51
            self.match(PonderosaPKParser.Integer_NT)
            self.state = 52
            self.match(PonderosaPKParser.Simple_name_NT)
            self.state = 53
            self.match(PonderosaPKParser.RETURN_NT)
            self.state = 54
            self.match(PonderosaPKParser.Axis_order)
            self.state = 55
            self.match(PonderosaPKParser.Integer_AO)
            self.state = 56
            self.match(PonderosaPKParser.Simple_name_AO)
            self.state = 57
            self.match(PonderosaPKParser.RETURN_AO)
            self.state = 59 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 58
                self.peak_3d()
                self.state = 61 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==4):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Peak_3dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Float(self, i:int=None):
            if i is None:
                return self.getTokens(PonderosaPKParser.Float)
            else:
                return self.getToken(PonderosaPKParser.Float, i)

        def number(self):
            return self.getTypedRuleContext(PonderosaPKParser.NumberContext,0)


        def Simple_name(self, i:int=None):
            if i is None:
                return self.getTokens(PonderosaPKParser.Simple_name)
            else:
                return self.getToken(PonderosaPKParser.Simple_name, i)

        def RETURN(self):
            return self.getToken(PonderosaPKParser.RETURN, 0)

        def EOF(self):
            return self.getToken(PonderosaPKParser.EOF, 0)

        def getRuleIndex(self):
            return PonderosaPKParser.RULE_peak_3d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPeak_3d" ):
                listener.enterPeak_3d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPeak_3d" ):
                listener.exitPeak_3d(self)




    def peak_3d(self):

        localctx = PonderosaPKParser.Peak_3dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_peak_3d)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 63
            self.match(PonderosaPKParser.Float)
            self.state = 64
            self.match(PonderosaPKParser.Float)
            self.state = 65
            self.match(PonderosaPKParser.Float)
            self.state = 66
            self.number()
            self.state = 67
            self.match(PonderosaPKParser.Simple_name)
            self.state = 68
            self.match(PonderosaPKParser.Simple_name)
            self.state = 69
            self.match(PonderosaPKParser.Simple_name)
            self.state = 70
            _la = self._input.LA(1)
            if not(_la==-1 or _la==11):
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


    class Peak_list_4dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Noesy_type(self):
            return self.getToken(PonderosaPKParser.Noesy_type, 0)

        def Integer_NT(self):
            return self.getToken(PonderosaPKParser.Integer_NT, 0)

        def Simple_name_NT(self):
            return self.getToken(PonderosaPKParser.Simple_name_NT, 0)

        def RETURN_NT(self):
            return self.getToken(PonderosaPKParser.RETURN_NT, 0)

        def Axis_order(self):
            return self.getToken(PonderosaPKParser.Axis_order, 0)

        def Integer_AO(self):
            return self.getToken(PonderosaPKParser.Integer_AO, 0)

        def Simple_name_AO(self):
            return self.getToken(PonderosaPKParser.Simple_name_AO, 0)

        def RETURN_AO(self):
            return self.getToken(PonderosaPKParser.RETURN_AO, 0)

        def peak_4d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PonderosaPKParser.Peak_4dContext)
            else:
                return self.getTypedRuleContext(PonderosaPKParser.Peak_4dContext,i)


        def getRuleIndex(self):
            return PonderosaPKParser.RULE_peak_list_4d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPeak_list_4d" ):
                listener.enterPeak_list_4d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPeak_list_4d" ):
                listener.exitPeak_list_4d(self)




    def peak_list_4d(self):

        localctx = PonderosaPKParser.Peak_list_4dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_peak_list_4d)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 72
            self.match(PonderosaPKParser.Noesy_type)
            self.state = 73
            self.match(PonderosaPKParser.Integer_NT)
            self.state = 74
            self.match(PonderosaPKParser.Simple_name_NT)
            self.state = 75
            self.match(PonderosaPKParser.RETURN_NT)
            self.state = 76
            self.match(PonderosaPKParser.Axis_order)
            self.state = 77
            self.match(PonderosaPKParser.Integer_AO)
            self.state = 78
            self.match(PonderosaPKParser.Simple_name_AO)
            self.state = 79
            self.match(PonderosaPKParser.RETURN_AO)
            self.state = 81 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 80
                self.peak_4d()
                self.state = 83 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==4):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Peak_4dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Float(self, i:int=None):
            if i is None:
                return self.getTokens(PonderosaPKParser.Float)
            else:
                return self.getToken(PonderosaPKParser.Float, i)

        def number(self):
            return self.getTypedRuleContext(PonderosaPKParser.NumberContext,0)


        def Simple_name(self, i:int=None):
            if i is None:
                return self.getTokens(PonderosaPKParser.Simple_name)
            else:
                return self.getToken(PonderosaPKParser.Simple_name, i)

        def RETURN(self):
            return self.getToken(PonderosaPKParser.RETURN, 0)

        def EOF(self):
            return self.getToken(PonderosaPKParser.EOF, 0)

        def getRuleIndex(self):
            return PonderosaPKParser.RULE_peak_4d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPeak_4d" ):
                listener.enterPeak_4d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPeak_4d" ):
                listener.exitPeak_4d(self)




    def peak_4d(self):

        localctx = PonderosaPKParser.Peak_4dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_peak_4d)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 85
            self.match(PonderosaPKParser.Float)
            self.state = 86
            self.match(PonderosaPKParser.Float)
            self.state = 87
            self.match(PonderosaPKParser.Float)
            self.state = 88
            self.match(PonderosaPKParser.Float)
            self.state = 89
            self.number()
            self.state = 90
            self.match(PonderosaPKParser.Simple_name)
            self.state = 91
            self.match(PonderosaPKParser.Simple_name)
            self.state = 92
            self.match(PonderosaPKParser.Simple_name)
            self.state = 93
            self.match(PonderosaPKParser.Simple_name)
            self.state = 94
            _la = self._input.LA(1)
            if not(_la==-1 or _la==11):
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
            return self.getToken(PonderosaPKParser.Float, 0)

        def Real(self):
            return self.getToken(PonderosaPKParser.Real, 0)

        def getRuleIndex(self):
            return PonderosaPKParser.RULE_number

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNumber" ):
                listener.enterNumber(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNumber" ):
                listener.exitNumber(self)




    def number(self):

        localctx = PonderosaPKParser.NumberContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_number)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 96
            _la = self._input.LA(1)
            if not(_la==4 or _la==5):
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





