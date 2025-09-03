# Generated from CharmmCRDParser.g4 by ANTLR 4.13.0
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
        4,1,14,45,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,1,0,1,0,5,0,11,8,0,10,
        0,12,0,14,9,0,1,0,1,0,1,1,1,1,5,1,20,8,1,10,1,12,1,23,9,1,1,1,1,
        1,1,2,1,2,1,2,4,2,30,8,2,11,2,12,2,31,1,3,1,3,1,3,1,3,1,3,1,3,1,
        3,1,3,1,3,1,3,1,3,1,3,0,0,4,0,2,4,6,0,1,1,1,14,14,44,0,12,1,0,0,
        0,2,17,1,0,0,0,4,26,1,0,0,0,6,33,1,0,0,0,8,11,3,2,1,0,9,11,3,4,2,
        0,10,8,1,0,0,0,10,9,1,0,0,0,11,14,1,0,0,0,12,10,1,0,0,0,12,13,1,
        0,0,0,13,15,1,0,0,0,14,12,1,0,0,0,15,16,5,0,0,1,16,1,1,0,0,0,17,
        21,5,4,0,0,18,20,5,12,0,0,19,18,1,0,0,0,20,23,1,0,0,0,21,19,1,0,
        0,0,21,22,1,0,0,0,22,24,1,0,0,0,23,21,1,0,0,0,24,25,7,0,0,0,25,3,
        1,0,0,0,26,27,5,1,0,0,27,29,5,5,0,0,28,30,3,6,3,0,29,28,1,0,0,0,
        30,31,1,0,0,0,31,29,1,0,0,0,31,32,1,0,0,0,32,5,1,0,0,0,33,34,5,1,
        0,0,34,35,5,1,0,0,35,36,5,6,0,0,36,37,5,6,0,0,37,38,5,2,0,0,38,39,
        5,2,0,0,39,40,5,2,0,0,40,41,5,6,0,0,41,42,5,1,0,0,42,43,5,2,0,0,
        43,7,1,0,0,0,4,10,12,21,31
    ]

class CharmmCRDParser ( Parser ):

    grammarFileName = "CharmmCRDParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "'EXT'" ]

    symbolicNames = [ "<INVALID>", "Integer", "Float", "Double_quote_string", 
                      "COMMENT", "Ext", "Simple_name", "SPACE", "CONTINUE", 
                      "ENCLOSE_COMMENT", "SECTION_COMMENT", "LINE_COMMENT", 
                      "Any_name", "SPACE_CM", "RETURN_CM" ]

    RULE_charmm_crd = 0
    RULE_comment = 1
    RULE_coordinates = 2
    RULE_atom_coordinate = 3

    ruleNames =  [ "charmm_crd", "comment", "coordinates", "atom_coordinate" ]

    EOF = Token.EOF
    Integer=1
    Float=2
    Double_quote_string=3
    COMMENT=4
    Ext=5
    Simple_name=6
    SPACE=7
    CONTINUE=8
    ENCLOSE_COMMENT=9
    SECTION_COMMENT=10
    LINE_COMMENT=11
    Any_name=12
    SPACE_CM=13
    RETURN_CM=14

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.0")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class Charmm_crdContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(CharmmCRDParser.EOF, 0)

        def comment(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(CharmmCRDParser.CommentContext)
            else:
                return self.getTypedRuleContext(CharmmCRDParser.CommentContext,i)


        def coordinates(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(CharmmCRDParser.CoordinatesContext)
            else:
                return self.getTypedRuleContext(CharmmCRDParser.CoordinatesContext,i)


        def getRuleIndex(self):
            return CharmmCRDParser.RULE_charmm_crd

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCharmm_crd" ):
                listener.enterCharmm_crd(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCharmm_crd" ):
                listener.exitCharmm_crd(self)




    def charmm_crd(self):

        localctx = CharmmCRDParser.Charmm_crdContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_charmm_crd)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 12
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==1 or _la==4:
                self.state = 10
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [4]:
                    self.state = 8
                    self.comment()
                    pass
                elif token in [1]:
                    self.state = 9
                    self.coordinates()
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 14
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 15
            self.match(CharmmCRDParser.EOF)
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
            return self.getToken(CharmmCRDParser.COMMENT, 0)

        def RETURN_CM(self):
            return self.getToken(CharmmCRDParser.RETURN_CM, 0)

        def EOF(self):
            return self.getToken(CharmmCRDParser.EOF, 0)

        def Any_name(self, i:int=None):
            if i is None:
                return self.getTokens(CharmmCRDParser.Any_name)
            else:
                return self.getToken(CharmmCRDParser.Any_name, i)

        def getRuleIndex(self):
            return CharmmCRDParser.RULE_comment

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterComment" ):
                listener.enterComment(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitComment" ):
                listener.exitComment(self)




    def comment(self):

        localctx = CharmmCRDParser.CommentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_comment)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 17
            self.match(CharmmCRDParser.COMMENT)
            self.state = 21
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==12:
                self.state = 18
                self.match(CharmmCRDParser.Any_name)
                self.state = 23
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 24
            _la = self._input.LA(1)
            if not(_la==-1 or _la==14):
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


    class CoordinatesContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Integer(self):
            return self.getToken(CharmmCRDParser.Integer, 0)

        def Ext(self):
            return self.getToken(CharmmCRDParser.Ext, 0)

        def atom_coordinate(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(CharmmCRDParser.Atom_coordinateContext)
            else:
                return self.getTypedRuleContext(CharmmCRDParser.Atom_coordinateContext,i)


        def getRuleIndex(self):
            return CharmmCRDParser.RULE_coordinates

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCoordinates" ):
                listener.enterCoordinates(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCoordinates" ):
                listener.exitCoordinates(self)




    def coordinates(self):

        localctx = CharmmCRDParser.CoordinatesContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_coordinates)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 26
            self.match(CharmmCRDParser.Integer)
            self.state = 27
            self.match(CharmmCRDParser.Ext)
            self.state = 29 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 28
                    self.atom_coordinate()

                else:
                    raise NoViableAltException(self)
                self.state = 31 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,3,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Atom_coordinateContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Integer(self, i:int=None):
            if i is None:
                return self.getTokens(CharmmCRDParser.Integer)
            else:
                return self.getToken(CharmmCRDParser.Integer, i)

        def Simple_name(self, i:int=None):
            if i is None:
                return self.getTokens(CharmmCRDParser.Simple_name)
            else:
                return self.getToken(CharmmCRDParser.Simple_name, i)

        def Float(self, i:int=None):
            if i is None:
                return self.getTokens(CharmmCRDParser.Float)
            else:
                return self.getToken(CharmmCRDParser.Float, i)

        def getRuleIndex(self):
            return CharmmCRDParser.RULE_atom_coordinate

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAtom_coordinate" ):
                listener.enterAtom_coordinate(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAtom_coordinate" ):
                listener.exitAtom_coordinate(self)




    def atom_coordinate(self):

        localctx = CharmmCRDParser.Atom_coordinateContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_atom_coordinate)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 33
            self.match(CharmmCRDParser.Integer)
            self.state = 34
            self.match(CharmmCRDParser.Integer)
            self.state = 35
            self.match(CharmmCRDParser.Simple_name)
            self.state = 36
            self.match(CharmmCRDParser.Simple_name)
            self.state = 37
            self.match(CharmmCRDParser.Float)
            self.state = 38
            self.match(CharmmCRDParser.Float)
            self.state = 39
            self.match(CharmmCRDParser.Float)
            self.state = 40
            self.match(CharmmCRDParser.Simple_name)
            self.state = 41
            self.match(CharmmCRDParser.Integer)
            self.state = 42
            self.match(CharmmCRDParser.Float)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





