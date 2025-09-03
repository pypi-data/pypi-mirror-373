# Generated from IsdMRParser.g4 by ANTLR 4.13.0
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
        4,1,11,24,2,0,7,0,2,1,7,1,2,2,7,2,1,0,5,0,8,8,0,10,0,12,0,11,9,0,
        1,0,1,0,1,1,1,1,4,1,17,8,1,11,1,12,1,18,1,2,1,2,1,2,1,2,0,0,3,0,
        2,4,0,0,22,0,9,1,0,0,0,2,14,1,0,0,0,4,20,1,0,0,0,6,8,3,2,1,0,7,6,
        1,0,0,0,8,11,1,0,0,0,9,7,1,0,0,0,9,10,1,0,0,0,10,12,1,0,0,0,11,9,
        1,0,0,0,12,13,5,0,0,1,13,1,1,0,0,0,14,16,5,1,0,0,15,17,3,4,2,0,16,
        15,1,0,0,0,17,18,1,0,0,0,18,16,1,0,0,0,18,19,1,0,0,0,19,3,1,0,0,
        0,20,21,5,7,0,0,21,22,5,7,0,0,22,5,1,0,0,0,2,9,18
    ]

class IsdMRParser ( Parser ):

    grammarFileName = "IsdMRParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [  ]

    symbolicNames = [ "<INVALID>", "Distance", "Integer", "Float", "SHARP_COMMENT", 
                      "EXCLM_COMMENT", "SMCLN_COMMENT", "Atom_selection", 
                      "SPACE", "ENCLOSE_COMMENT", "SECTION_COMMENT", "LINE_COMMENT" ]

    RULE_isd_mr = 0
    RULE_distance_restraints = 1
    RULE_distance_restraint = 2

    ruleNames =  [ "isd_mr", "distance_restraints", "distance_restraint" ]

    EOF = Token.EOF
    Distance=1
    Integer=2
    Float=3
    SHARP_COMMENT=4
    EXCLM_COMMENT=5
    SMCLN_COMMENT=6
    Atom_selection=7
    SPACE=8
    ENCLOSE_COMMENT=9
    SECTION_COMMENT=10
    LINE_COMMENT=11

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.0")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class Isd_mrContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(IsdMRParser.EOF, 0)

        def distance_restraints(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(IsdMRParser.Distance_restraintsContext)
            else:
                return self.getTypedRuleContext(IsdMRParser.Distance_restraintsContext,i)


        def getRuleIndex(self):
            return IsdMRParser.RULE_isd_mr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIsd_mr" ):
                listener.enterIsd_mr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIsd_mr" ):
                listener.exitIsd_mr(self)




    def isd_mr(self):

        localctx = IsdMRParser.Isd_mrContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_isd_mr)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 9
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==1:
                self.state = 6
                self.distance_restraints()
                self.state = 11
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 12
            self.match(IsdMRParser.EOF)
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

        def Distance(self):
            return self.getToken(IsdMRParser.Distance, 0)

        def distance_restraint(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(IsdMRParser.Distance_restraintContext)
            else:
                return self.getTypedRuleContext(IsdMRParser.Distance_restraintContext,i)


        def getRuleIndex(self):
            return IsdMRParser.RULE_distance_restraints

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDistance_restraints" ):
                listener.enterDistance_restraints(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDistance_restraints" ):
                listener.exitDistance_restraints(self)




    def distance_restraints(self):

        localctx = IsdMRParser.Distance_restraintsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_distance_restraints)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 14
            self.match(IsdMRParser.Distance)
            self.state = 16 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 15
                self.distance_restraint()
                self.state = 18 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==7):
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
                return self.getTokens(IsdMRParser.Atom_selection)
            else:
                return self.getToken(IsdMRParser.Atom_selection, i)

        def getRuleIndex(self):
            return IsdMRParser.RULE_distance_restraint

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDistance_restraint" ):
                listener.enterDistance_restraint(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDistance_restraint" ):
                listener.exitDistance_restraint(self)




    def distance_restraint(self):

        localctx = IsdMRParser.Distance_restraintContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_distance_restraint)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 20
            self.match(IsdMRParser.Atom_selection)
            self.state = 21
            self.match(IsdMRParser.Atom_selection)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





