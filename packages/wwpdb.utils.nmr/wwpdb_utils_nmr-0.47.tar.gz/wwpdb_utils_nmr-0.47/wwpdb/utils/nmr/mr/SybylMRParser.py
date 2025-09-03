# Generated from SybylMRParser.g4 by ANTLR 4.13.0
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
        4,1,15,33,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,1,0,5,0,10,8,0,10,0,12,
        0,13,9,0,1,0,1,0,1,1,1,1,1,1,1,1,1,1,4,1,22,8,1,11,1,12,1,23,1,2,
        1,2,1,2,1,2,1,2,1,3,1,3,1,3,0,0,4,0,2,4,6,0,1,1,0,5,7,30,0,11,1,
        0,0,0,2,16,1,0,0,0,4,25,1,0,0,0,6,30,1,0,0,0,8,10,3,2,1,0,9,8,1,
        0,0,0,10,13,1,0,0,0,11,9,1,0,0,0,11,12,1,0,0,0,12,14,1,0,0,0,13,
        11,1,0,0,0,14,15,5,0,0,1,15,1,1,0,0,0,16,17,5,1,0,0,17,18,5,2,0,
        0,18,19,5,3,0,0,19,21,5,4,0,0,20,22,3,4,2,0,21,20,1,0,0,0,22,23,
        1,0,0,0,23,21,1,0,0,0,23,24,1,0,0,0,24,3,1,0,0,0,25,26,5,11,0,0,
        26,27,5,11,0,0,27,28,3,6,3,0,28,29,3,6,3,0,29,5,1,0,0,0,30,31,7,
        0,0,0,31,7,1,0,0,0,2,11,23
    ]

class SybylMRParser ( Parser ):

    grammarFileName = "SybylMRParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'ATOM1'", "'ATOM2'", "'LOWER'", "'UPPER'" ]

    symbolicNames = [ "<INVALID>", "Atom1", "Atom2", "Lower", "Upper", "Integer", 
                      "Float", "Float_DecimalComma", "SHARP_COMMENT", "EXCLM_COMMENT", 
                      "SMCLN_COMMENT", "Atom_selection", "SPACE", "ENCLOSE_COMMENT", 
                      "SECTION_COMMENT", "LINE_COMMENT" ]

    RULE_sybyl_mr = 0
    RULE_distance_restraints = 1
    RULE_distance_restraint = 2
    RULE_number = 3

    ruleNames =  [ "sybyl_mr", "distance_restraints", "distance_restraint", 
                   "number" ]

    EOF = Token.EOF
    Atom1=1
    Atom2=2
    Lower=3
    Upper=4
    Integer=5
    Float=6
    Float_DecimalComma=7
    SHARP_COMMENT=8
    EXCLM_COMMENT=9
    SMCLN_COMMENT=10
    Atom_selection=11
    SPACE=12
    ENCLOSE_COMMENT=13
    SECTION_COMMENT=14
    LINE_COMMENT=15

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.0")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class Sybyl_mrContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(SybylMRParser.EOF, 0)

        def distance_restraints(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(SybylMRParser.Distance_restraintsContext)
            else:
                return self.getTypedRuleContext(SybylMRParser.Distance_restraintsContext,i)


        def getRuleIndex(self):
            return SybylMRParser.RULE_sybyl_mr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSybyl_mr" ):
                listener.enterSybyl_mr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSybyl_mr" ):
                listener.exitSybyl_mr(self)




    def sybyl_mr(self):

        localctx = SybylMRParser.Sybyl_mrContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_sybyl_mr)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 11
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==1:
                self.state = 8
                self.distance_restraints()
                self.state = 13
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 14
            self.match(SybylMRParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Distance_restraintsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Atom1(self):
            return self.getToken(SybylMRParser.Atom1, 0)

        def Atom2(self):
            return self.getToken(SybylMRParser.Atom2, 0)

        def Lower(self):
            return self.getToken(SybylMRParser.Lower, 0)

        def Upper(self):
            return self.getToken(SybylMRParser.Upper, 0)

        def distance_restraint(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(SybylMRParser.Distance_restraintContext)
            else:
                return self.getTypedRuleContext(SybylMRParser.Distance_restraintContext,i)


        def getRuleIndex(self):
            return SybylMRParser.RULE_distance_restraints

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDistance_restraints" ):
                listener.enterDistance_restraints(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDistance_restraints" ):
                listener.exitDistance_restraints(self)




    def distance_restraints(self):

        localctx = SybylMRParser.Distance_restraintsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_distance_restraints)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 16
            self.match(SybylMRParser.Atom1)
            self.state = 17
            self.match(SybylMRParser.Atom2)
            self.state = 18
            self.match(SybylMRParser.Lower)
            self.state = 19
            self.match(SybylMRParser.Upper)
            self.state = 21 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 20
                self.distance_restraint()
                self.state = 23 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==11):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Distance_restraintContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Atom_selection(self, i:int=None):
            if i is None:
                return self.getTokens(SybylMRParser.Atom_selection)
            else:
                return self.getToken(SybylMRParser.Atom_selection, i)

        def number(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(SybylMRParser.NumberContext)
            else:
                return self.getTypedRuleContext(SybylMRParser.NumberContext,i)


        def getRuleIndex(self):
            return SybylMRParser.RULE_distance_restraint

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDistance_restraint" ):
                listener.enterDistance_restraint(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDistance_restraint" ):
                listener.exitDistance_restraint(self)




    def distance_restraint(self):

        localctx = SybylMRParser.Distance_restraintContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_distance_restraint)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 25
            self.match(SybylMRParser.Atom_selection)
            self.state = 26
            self.match(SybylMRParser.Atom_selection)
            self.state = 27
            self.number()
            self.state = 28
            self.number()
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
            return self.getToken(SybylMRParser.Float, 0)

        def Float_DecimalComma(self):
            return self.getToken(SybylMRParser.Float_DecimalComma, 0)

        def Integer(self):
            return self.getToken(SybylMRParser.Integer, 0)

        def getRuleIndex(self):
            return SybylMRParser.RULE_number

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNumber" ):
                listener.enterNumber(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNumber" ):
                listener.exitNumber(self)




    def number(self):

        localctx = SybylMRParser.NumberContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_number)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 30
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 224) != 0)):
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





