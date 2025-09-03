# Generated from XwinNmrPKParser.g4 by ANTLR 4.13.0
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
        4,1,15,111,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,1,0,3,
        0,14,8,0,1,0,1,0,1,0,4,0,19,8,0,11,0,12,0,20,1,0,4,0,24,8,0,11,0,
        12,0,25,1,0,4,0,29,8,0,11,0,12,0,30,1,0,5,0,34,8,0,10,0,12,0,37,
        9,0,1,0,1,0,1,1,1,1,5,1,43,8,1,10,1,12,1,46,9,1,1,1,1,1,1,2,1,2,
        1,2,1,2,1,3,1,3,1,3,1,3,1,3,1,3,1,3,3,3,61,8,3,1,3,5,3,64,8,3,10,
        3,12,3,67,9,3,1,3,1,3,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,3,4,80,
        8,4,1,4,5,4,83,8,4,10,4,12,4,86,9,4,1,4,1,4,1,5,1,5,1,5,1,5,1,5,
        1,5,1,5,1,5,1,5,1,5,1,5,3,5,101,8,5,1,5,5,5,104,8,5,10,5,12,5,107,
        9,5,1,5,1,5,1,5,0,0,6,0,2,4,6,8,10,0,2,1,1,15,15,1,1,6,6,121,0,13,
        1,0,0,0,2,40,1,0,0,0,4,49,1,0,0,0,6,53,1,0,0,0,8,70,1,0,0,0,10,89,
        1,0,0,0,12,14,5,6,0,0,13,12,1,0,0,0,13,14,1,0,0,0,14,35,1,0,0,0,
        15,34,3,2,1,0,16,34,3,4,2,0,17,19,3,6,3,0,18,17,1,0,0,0,19,20,1,
        0,0,0,20,18,1,0,0,0,20,21,1,0,0,0,21,34,1,0,0,0,22,24,3,8,4,0,23,
        22,1,0,0,0,24,25,1,0,0,0,25,23,1,0,0,0,25,26,1,0,0,0,26,34,1,0,0,
        0,27,29,3,10,5,0,28,27,1,0,0,0,29,30,1,0,0,0,30,28,1,0,0,0,30,31,
        1,0,0,0,31,34,1,0,0,0,32,34,5,6,0,0,33,15,1,0,0,0,33,16,1,0,0,0,
        33,18,1,0,0,0,33,23,1,0,0,0,33,28,1,0,0,0,33,32,1,0,0,0,34,37,1,
        0,0,0,35,33,1,0,0,0,35,36,1,0,0,0,36,38,1,0,0,0,37,35,1,0,0,0,38,
        39,5,0,0,1,39,1,1,0,0,0,40,44,5,4,0,0,41,43,5,13,0,0,42,41,1,0,0,
        0,43,46,1,0,0,0,44,42,1,0,0,0,44,45,1,0,0,0,45,47,1,0,0,0,46,44,
        1,0,0,0,47,48,7,0,0,0,48,3,1,0,0,0,49,50,5,1,0,0,50,51,5,10,0,0,
        51,52,5,12,0,0,52,5,1,0,0,0,53,54,5,2,0,0,54,55,5,3,0,0,55,56,5,
        3,0,0,56,57,5,3,0,0,57,58,5,3,0,0,58,60,5,3,0,0,59,61,5,3,0,0,60,
        59,1,0,0,0,60,61,1,0,0,0,61,65,1,0,0,0,62,64,5,9,0,0,63,62,1,0,0,
        0,64,67,1,0,0,0,65,63,1,0,0,0,65,66,1,0,0,0,66,68,1,0,0,0,67,65,
        1,0,0,0,68,69,7,1,0,0,69,7,1,0,0,0,70,71,5,2,0,0,71,72,5,3,0,0,72,
        73,5,3,0,0,73,74,5,3,0,0,74,75,5,3,0,0,75,76,5,3,0,0,76,77,5,3,0,
        0,77,79,5,3,0,0,78,80,5,3,0,0,79,78,1,0,0,0,79,80,1,0,0,0,80,84,
        1,0,0,0,81,83,5,9,0,0,82,81,1,0,0,0,83,86,1,0,0,0,84,82,1,0,0,0,
        84,85,1,0,0,0,85,87,1,0,0,0,86,84,1,0,0,0,87,88,7,1,0,0,88,9,1,0,
        0,0,89,90,5,2,0,0,90,91,5,3,0,0,91,92,5,3,0,0,92,93,5,3,0,0,93,94,
        5,3,0,0,94,95,5,3,0,0,95,96,5,3,0,0,96,97,5,3,0,0,97,98,5,3,0,0,
        98,100,5,3,0,0,99,101,5,3,0,0,100,99,1,0,0,0,100,101,1,0,0,0,101,
        105,1,0,0,0,102,104,5,9,0,0,103,102,1,0,0,0,104,107,1,0,0,0,105,
        103,1,0,0,0,105,106,1,0,0,0,106,108,1,0,0,0,107,105,1,0,0,0,108,
        109,7,1,0,0,109,11,1,0,0,0,13,13,20,25,30,33,35,44,60,65,79,84,100,
        105
    ]

class XwinNmrPKParser ( Parser ):

    grammarFileName = "XwinNmrPKParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'# PEAKLIST_DIMENSION'" ]

    symbolicNames = [ "<INVALID>", "Num_of_dim", "Integer", "Float", "COMMENT", 
                      "SPACE", "RETURN", "SECTION_COMMENT", "LINE_COMMENT", 
                      "Annotation", "Integer_ND", "SPACE_ND", "RETURN_ND", 
                      "Any_name", "SPACE_CM", "RETURN_CM" ]

    RULE_xwinnmr_pk = 0
    RULE_comment = 1
    RULE_dimension = 2
    RULE_peak_2d = 3
    RULE_peak_3d = 4
    RULE_peak_4d = 5

    ruleNames =  [ "xwinnmr_pk", "comment", "dimension", "peak_2d", "peak_3d", 
                   "peak_4d" ]

    EOF = Token.EOF
    Num_of_dim=1
    Integer=2
    Float=3
    COMMENT=4
    SPACE=5
    RETURN=6
    SECTION_COMMENT=7
    LINE_COMMENT=8
    Annotation=9
    Integer_ND=10
    SPACE_ND=11
    RETURN_ND=12
    Any_name=13
    SPACE_CM=14
    RETURN_CM=15

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.0")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class Xwinnmr_pkContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(XwinNmrPKParser.EOF, 0)

        def RETURN(self, i:int=None):
            if i is None:
                return self.getTokens(XwinNmrPKParser.RETURN)
            else:
                return self.getToken(XwinNmrPKParser.RETURN, i)

        def comment(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(XwinNmrPKParser.CommentContext)
            else:
                return self.getTypedRuleContext(XwinNmrPKParser.CommentContext,i)


        def dimension(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(XwinNmrPKParser.DimensionContext)
            else:
                return self.getTypedRuleContext(XwinNmrPKParser.DimensionContext,i)


        def peak_2d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(XwinNmrPKParser.Peak_2dContext)
            else:
                return self.getTypedRuleContext(XwinNmrPKParser.Peak_2dContext,i)


        def peak_3d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(XwinNmrPKParser.Peak_3dContext)
            else:
                return self.getTypedRuleContext(XwinNmrPKParser.Peak_3dContext,i)


        def peak_4d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(XwinNmrPKParser.Peak_4dContext)
            else:
                return self.getTypedRuleContext(XwinNmrPKParser.Peak_4dContext,i)


        def getRuleIndex(self):
            return XwinNmrPKParser.RULE_xwinnmr_pk

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterXwinnmr_pk" ):
                listener.enterXwinnmr_pk(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitXwinnmr_pk" ):
                listener.exitXwinnmr_pk(self)




    def xwinnmr_pk(self):

        localctx = XwinNmrPKParser.Xwinnmr_pkContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_xwinnmr_pk)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 13
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,0,self._ctx)
            if la_ == 1:
                self.state = 12
                self.match(XwinNmrPKParser.RETURN)


            self.state = 35
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 86) != 0):
                self.state = 33
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,4,self._ctx)
                if la_ == 1:
                    self.state = 15
                    self.comment()
                    pass

                elif la_ == 2:
                    self.state = 16
                    self.dimension()
                    pass

                elif la_ == 3:
                    self.state = 18 
                    self._errHandler.sync(self)
                    _alt = 1
                    while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                        if _alt == 1:
                            self.state = 17
                            self.peak_2d()

                        else:
                            raise NoViableAltException(self)
                        self.state = 20 
                        self._errHandler.sync(self)
                        _alt = self._interp.adaptivePredict(self._input,1,self._ctx)

                    pass

                elif la_ == 4:
                    self.state = 23 
                    self._errHandler.sync(self)
                    _alt = 1
                    while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                        if _alt == 1:
                            self.state = 22
                            self.peak_3d()

                        else:
                            raise NoViableAltException(self)
                        self.state = 25 
                        self._errHandler.sync(self)
                        _alt = self._interp.adaptivePredict(self._input,2,self._ctx)

                    pass

                elif la_ == 5:
                    self.state = 28 
                    self._errHandler.sync(self)
                    _alt = 1
                    while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                        if _alt == 1:
                            self.state = 27
                            self.peak_4d()

                        else:
                            raise NoViableAltException(self)
                        self.state = 30 
                        self._errHandler.sync(self)
                        _alt = self._interp.adaptivePredict(self._input,3,self._ctx)

                    pass

                elif la_ == 6:
                    self.state = 32
                    self.match(XwinNmrPKParser.RETURN)
                    pass


                self.state = 37
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 38
            self.match(XwinNmrPKParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CommentContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def COMMENT(self):
            return self.getToken(XwinNmrPKParser.COMMENT, 0)

        def RETURN_CM(self):
            return self.getToken(XwinNmrPKParser.RETURN_CM, 0)

        def EOF(self):
            return self.getToken(XwinNmrPKParser.EOF, 0)

        def Any_name(self, i:int=None):
            if i is None:
                return self.getTokens(XwinNmrPKParser.Any_name)
            else:
                return self.getToken(XwinNmrPKParser.Any_name, i)

        def getRuleIndex(self):
            return XwinNmrPKParser.RULE_comment

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterComment" ):
                listener.enterComment(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitComment" ):
                listener.exitComment(self)




    def comment(self):

        localctx = XwinNmrPKParser.CommentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_comment)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 40
            self.match(XwinNmrPKParser.COMMENT)
            self.state = 44
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==13:
                self.state = 41
                self.match(XwinNmrPKParser.Any_name)
                self.state = 46
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 47
            _la = self._input.LA(1)
            if not(_la==-1 or _la==15):
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


    class DimensionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Num_of_dim(self):
            return self.getToken(XwinNmrPKParser.Num_of_dim, 0)

        def Integer_ND(self):
            return self.getToken(XwinNmrPKParser.Integer_ND, 0)

        def RETURN_ND(self):
            return self.getToken(XwinNmrPKParser.RETURN_ND, 0)

        def getRuleIndex(self):
            return XwinNmrPKParser.RULE_dimension

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDimension" ):
                listener.enterDimension(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDimension" ):
                listener.exitDimension(self)




    def dimension(self):

        localctx = XwinNmrPKParser.DimensionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_dimension)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 49
            self.match(XwinNmrPKParser.Num_of_dim)
            self.state = 50
            self.match(XwinNmrPKParser.Integer_ND)
            self.state = 51
            self.match(XwinNmrPKParser.RETURN_ND)
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

        def Integer(self):
            return self.getToken(XwinNmrPKParser.Integer, 0)

        def Float(self, i:int=None):
            if i is None:
                return self.getTokens(XwinNmrPKParser.Float)
            else:
                return self.getToken(XwinNmrPKParser.Float, i)

        def RETURN(self):
            return self.getToken(XwinNmrPKParser.RETURN, 0)

        def EOF(self):
            return self.getToken(XwinNmrPKParser.EOF, 0)

        def Annotation(self, i:int=None):
            if i is None:
                return self.getTokens(XwinNmrPKParser.Annotation)
            else:
                return self.getToken(XwinNmrPKParser.Annotation, i)

        def getRuleIndex(self):
            return XwinNmrPKParser.RULE_peak_2d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPeak_2d" ):
                listener.enterPeak_2d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPeak_2d" ):
                listener.exitPeak_2d(self)




    def peak_2d(self):

        localctx = XwinNmrPKParser.Peak_2dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_peak_2d)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 53
            self.match(XwinNmrPKParser.Integer)
            self.state = 54
            self.match(XwinNmrPKParser.Float)
            self.state = 55
            self.match(XwinNmrPKParser.Float)
            self.state = 56
            self.match(XwinNmrPKParser.Float)
            self.state = 57
            self.match(XwinNmrPKParser.Float)
            self.state = 58
            self.match(XwinNmrPKParser.Float)
            self.state = 60
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==3:
                self.state = 59
                self.match(XwinNmrPKParser.Float)


            self.state = 65
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==9:
                self.state = 62
                self.match(XwinNmrPKParser.Annotation)
                self.state = 67
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 68
            _la = self._input.LA(1)
            if not(_la==-1 or _la==6):
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


    class Peak_3dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Integer(self):
            return self.getToken(XwinNmrPKParser.Integer, 0)

        def Float(self, i:int=None):
            if i is None:
                return self.getTokens(XwinNmrPKParser.Float)
            else:
                return self.getToken(XwinNmrPKParser.Float, i)

        def RETURN(self):
            return self.getToken(XwinNmrPKParser.RETURN, 0)

        def EOF(self):
            return self.getToken(XwinNmrPKParser.EOF, 0)

        def Annotation(self, i:int=None):
            if i is None:
                return self.getTokens(XwinNmrPKParser.Annotation)
            else:
                return self.getToken(XwinNmrPKParser.Annotation, i)

        def getRuleIndex(self):
            return XwinNmrPKParser.RULE_peak_3d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPeak_3d" ):
                listener.enterPeak_3d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPeak_3d" ):
                listener.exitPeak_3d(self)




    def peak_3d(self):

        localctx = XwinNmrPKParser.Peak_3dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_peak_3d)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 70
            self.match(XwinNmrPKParser.Integer)
            self.state = 71
            self.match(XwinNmrPKParser.Float)
            self.state = 72
            self.match(XwinNmrPKParser.Float)
            self.state = 73
            self.match(XwinNmrPKParser.Float)
            self.state = 74
            self.match(XwinNmrPKParser.Float)
            self.state = 75
            self.match(XwinNmrPKParser.Float)
            self.state = 76
            self.match(XwinNmrPKParser.Float)
            self.state = 77
            self.match(XwinNmrPKParser.Float)
            self.state = 79
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==3:
                self.state = 78
                self.match(XwinNmrPKParser.Float)


            self.state = 84
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==9:
                self.state = 81
                self.match(XwinNmrPKParser.Annotation)
                self.state = 86
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 87
            _la = self._input.LA(1)
            if not(_la==-1 or _la==6):
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


    class Peak_4dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Integer(self):
            return self.getToken(XwinNmrPKParser.Integer, 0)

        def Float(self, i:int=None):
            if i is None:
                return self.getTokens(XwinNmrPKParser.Float)
            else:
                return self.getToken(XwinNmrPKParser.Float, i)

        def RETURN(self):
            return self.getToken(XwinNmrPKParser.RETURN, 0)

        def EOF(self):
            return self.getToken(XwinNmrPKParser.EOF, 0)

        def Annotation(self, i:int=None):
            if i is None:
                return self.getTokens(XwinNmrPKParser.Annotation)
            else:
                return self.getToken(XwinNmrPKParser.Annotation, i)

        def getRuleIndex(self):
            return XwinNmrPKParser.RULE_peak_4d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPeak_4d" ):
                listener.enterPeak_4d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPeak_4d" ):
                listener.exitPeak_4d(self)




    def peak_4d(self):

        localctx = XwinNmrPKParser.Peak_4dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_peak_4d)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 89
            self.match(XwinNmrPKParser.Integer)
            self.state = 90
            self.match(XwinNmrPKParser.Float)
            self.state = 91
            self.match(XwinNmrPKParser.Float)
            self.state = 92
            self.match(XwinNmrPKParser.Float)
            self.state = 93
            self.match(XwinNmrPKParser.Float)
            self.state = 94
            self.match(XwinNmrPKParser.Float)
            self.state = 95
            self.match(XwinNmrPKParser.Float)
            self.state = 96
            self.match(XwinNmrPKParser.Float)
            self.state = 97
            self.match(XwinNmrPKParser.Float)
            self.state = 98
            self.match(XwinNmrPKParser.Float)
            self.state = 100
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==3:
                self.state = 99
                self.match(XwinNmrPKParser.Float)


            self.state = 105
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==9:
                self.state = 102
                self.match(XwinNmrPKParser.Annotation)
                self.state = 107
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 108
            _la = self._input.LA(1)
            if not(_la==-1 or _la==6):
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





