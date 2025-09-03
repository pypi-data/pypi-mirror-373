# Generated from AriaMRParser.g4 by ANTLR 4.13.0
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
        4,1,36,78,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,1,0,5,0,18,8,0,10,0,12,0,21,9,0,1,0,1,0,1,1,4,1,26,8,1,
        11,1,12,1,27,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,
        1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,4,2,51,8,2,11,2,12,2,52,1,3,1,3,
        1,3,1,3,1,3,1,3,1,3,1,3,3,3,63,8,3,1,4,1,4,1,4,1,4,1,5,1,5,1,5,3,
        5,72,8,5,1,6,1,6,1,7,1,7,1,7,0,0,8,0,2,4,6,8,10,12,14,0,1,1,0,2,
        3,74,0,19,1,0,0,0,2,25,1,0,0,0,4,29,1,0,0,0,6,54,1,0,0,0,8,64,1,
        0,0,0,10,68,1,0,0,0,12,73,1,0,0,0,14,75,1,0,0,0,16,18,3,2,1,0,17,
        16,1,0,0,0,18,21,1,0,0,0,19,17,1,0,0,0,19,20,1,0,0,0,20,22,1,0,0,
        0,21,19,1,0,0,0,22,23,5,0,0,1,23,1,1,0,0,0,24,26,3,4,2,0,25,24,1,
        0,0,0,26,27,1,0,0,0,27,25,1,0,0,0,27,28,1,0,0,0,28,3,1,0,0,0,29,
        30,5,7,0,0,30,31,5,26,0,0,31,32,5,8,0,0,32,33,5,2,0,0,33,34,5,9,
        0,0,34,35,5,2,0,0,35,36,5,10,0,0,36,37,3,12,6,0,37,38,5,11,0,0,38,
        39,3,12,6,0,39,40,5,12,0,0,40,41,3,12,6,0,41,42,5,13,0,0,42,43,3,
        12,6,0,43,44,5,14,0,0,44,45,5,29,0,0,45,46,5,15,0,0,46,47,5,32,0,
        0,47,48,5,16,0,0,48,50,5,35,0,0,49,51,3,6,3,0,50,49,1,0,0,0,51,52,
        1,0,0,0,52,50,1,0,0,0,52,53,1,0,0,0,53,5,1,0,0,0,54,62,3,8,4,0,55,
        56,5,10,0,0,56,57,3,14,7,0,57,58,5,18,0,0,58,59,3,14,7,0,59,60,5,
        17,0,0,60,61,3,14,7,0,61,63,1,0,0,0,62,55,1,0,0,0,62,63,1,0,0,0,
        63,7,1,0,0,0,64,65,3,10,5,0,65,66,5,19,0,0,66,67,3,10,5,0,67,9,1,
        0,0,0,68,69,5,20,0,0,69,71,5,20,0,0,70,72,5,20,0,0,71,70,1,0,0,0,
        71,72,1,0,0,0,72,11,1,0,0,0,73,74,7,0,0,0,74,13,1,0,0,0,75,76,7,
        0,0,0,76,15,1,0,0,0,5,19,27,52,62,71
    ]

class AriaMRParser ( Parser ):

    grammarFileName = "AriaMRParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "','", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "'ref_spec:'", "'ref_peak:'", 
                     "'id:'", "'d:'", "'u:'", "'u_viol:'", "'%_viol:'", 
                     "'viol:'", "'reliable:'", "'a_type:'", "'weight:'", 
                     "'+/-'", "'-'" ]

    symbolicNames = [ "<INVALID>", "COMMA", "Integer", "Float", "SHARP_COMMENT", 
                      "EXCLM_COMMENT", "SMCLN_COMMENT", "RefSpec", "RefPeak", 
                      "Id", "D", "U", "UViol", "PViol", "Viol", "Reliable", 
                      "AType", "Weight", "PlusMinus", "Hyphen", "Simple_name", 
                      "SPACE", "ENCLOSE_COMMENT", "SECTION_COMMENT", "LINE_COMMENT", 
                      "SPACE_RS", "RefSpecName", "RETURN_RS", "SPACE_V", 
                      "ViolFlag", "RETURN_V", "SPACE_R", "ReliableFlag", 
                      "RETURN_R", "SPACE_A", "ATypeFlag", "RETURN_A" ]

    RULE_aria_mr = 0
    RULE_distance_restraints = 1
    RULE_distance_restraint = 2
    RULE_contribution = 3
    RULE_atom_pair = 4
    RULE_atom_selection = 5
    RULE_number = 6
    RULE_number_c = 7

    ruleNames =  [ "aria_mr", "distance_restraints", "distance_restraint", 
                   "contribution", "atom_pair", "atom_selection", "number", 
                   "number_c" ]

    EOF = Token.EOF
    COMMA=1
    Integer=2
    Float=3
    SHARP_COMMENT=4
    EXCLM_COMMENT=5
    SMCLN_COMMENT=6
    RefSpec=7
    RefPeak=8
    Id=9
    D=10
    U=11
    UViol=12
    PViol=13
    Viol=14
    Reliable=15
    AType=16
    Weight=17
    PlusMinus=18
    Hyphen=19
    Simple_name=20
    SPACE=21
    ENCLOSE_COMMENT=22
    SECTION_COMMENT=23
    LINE_COMMENT=24
    SPACE_RS=25
    RefSpecName=26
    RETURN_RS=27
    SPACE_V=28
    ViolFlag=29
    RETURN_V=30
    SPACE_R=31
    ReliableFlag=32
    RETURN_R=33
    SPACE_A=34
    ATypeFlag=35
    RETURN_A=36

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.0")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class Aria_mrContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(AriaMRParser.EOF, 0)

        def distance_restraints(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AriaMRParser.Distance_restraintsContext)
            else:
                return self.getTypedRuleContext(AriaMRParser.Distance_restraintsContext,i)


        def getRuleIndex(self):
            return AriaMRParser.RULE_aria_mr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAria_mr" ):
                listener.enterAria_mr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAria_mr" ):
                listener.exitAria_mr(self)




    def aria_mr(self):

        localctx = AriaMRParser.Aria_mrContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_aria_mr)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 19
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==7:
                self.state = 16
                self.distance_restraints()
                self.state = 21
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 22
            self.match(AriaMRParser.EOF)
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

        def distance_restraint(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AriaMRParser.Distance_restraintContext)
            else:
                return self.getTypedRuleContext(AriaMRParser.Distance_restraintContext,i)


        def getRuleIndex(self):
            return AriaMRParser.RULE_distance_restraints

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDistance_restraints" ):
                listener.enterDistance_restraints(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDistance_restraints" ):
                listener.exitDistance_restraints(self)




    def distance_restraints(self):

        localctx = AriaMRParser.Distance_restraintsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_distance_restraints)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 25 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 24
                    self.distance_restraint()

                else:
                    raise NoViableAltException(self)
                self.state = 27 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,1,self._ctx)

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

        def RefSpec(self):
            return self.getToken(AriaMRParser.RefSpec, 0)

        def RefSpecName(self):
            return self.getToken(AriaMRParser.RefSpecName, 0)

        def RefPeak(self):
            return self.getToken(AriaMRParser.RefPeak, 0)

        def Integer(self, i:int=None):
            if i is None:
                return self.getTokens(AriaMRParser.Integer)
            else:
                return self.getToken(AriaMRParser.Integer, i)

        def Id(self):
            return self.getToken(AriaMRParser.Id, 0)

        def D(self):
            return self.getToken(AriaMRParser.D, 0)

        def number(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AriaMRParser.NumberContext)
            else:
                return self.getTypedRuleContext(AriaMRParser.NumberContext,i)


        def U(self):
            return self.getToken(AriaMRParser.U, 0)

        def UViol(self):
            return self.getToken(AriaMRParser.UViol, 0)

        def PViol(self):
            return self.getToken(AriaMRParser.PViol, 0)

        def Viol(self):
            return self.getToken(AriaMRParser.Viol, 0)

        def ViolFlag(self):
            return self.getToken(AriaMRParser.ViolFlag, 0)

        def Reliable(self):
            return self.getToken(AriaMRParser.Reliable, 0)

        def ReliableFlag(self):
            return self.getToken(AriaMRParser.ReliableFlag, 0)

        def AType(self):
            return self.getToken(AriaMRParser.AType, 0)

        def ATypeFlag(self):
            return self.getToken(AriaMRParser.ATypeFlag, 0)

        def contribution(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AriaMRParser.ContributionContext)
            else:
                return self.getTypedRuleContext(AriaMRParser.ContributionContext,i)


        def getRuleIndex(self):
            return AriaMRParser.RULE_distance_restraint

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDistance_restraint" ):
                listener.enterDistance_restraint(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDistance_restraint" ):
                listener.exitDistance_restraint(self)




    def distance_restraint(self):

        localctx = AriaMRParser.Distance_restraintContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_distance_restraint)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 29
            self.match(AriaMRParser.RefSpec)
            self.state = 30
            self.match(AriaMRParser.RefSpecName)
            self.state = 31
            self.match(AriaMRParser.RefPeak)
            self.state = 32
            self.match(AriaMRParser.Integer)
            self.state = 33
            self.match(AriaMRParser.Id)
            self.state = 34
            self.match(AriaMRParser.Integer)
            self.state = 35
            self.match(AriaMRParser.D)
            self.state = 36
            self.number()
            self.state = 37
            self.match(AriaMRParser.U)
            self.state = 38
            self.number()
            self.state = 39
            self.match(AriaMRParser.UViol)
            self.state = 40
            self.number()
            self.state = 41
            self.match(AriaMRParser.PViol)
            self.state = 42
            self.number()
            self.state = 43
            self.match(AriaMRParser.Viol)
            self.state = 44
            self.match(AriaMRParser.ViolFlag)
            self.state = 45
            self.match(AriaMRParser.Reliable)
            self.state = 46
            self.match(AriaMRParser.ReliableFlag)
            self.state = 47
            self.match(AriaMRParser.AType)
            self.state = 48
            self.match(AriaMRParser.ATypeFlag)
            self.state = 50 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 49
                self.contribution()
                self.state = 52 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==20):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ContributionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def atom_pair(self):
            return self.getTypedRuleContext(AriaMRParser.Atom_pairContext,0)


        def D(self):
            return self.getToken(AriaMRParser.D, 0)

        def number_c(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AriaMRParser.Number_cContext)
            else:
                return self.getTypedRuleContext(AriaMRParser.Number_cContext,i)


        def PlusMinus(self):
            return self.getToken(AriaMRParser.PlusMinus, 0)

        def Weight(self):
            return self.getToken(AriaMRParser.Weight, 0)

        def getRuleIndex(self):
            return AriaMRParser.RULE_contribution

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterContribution" ):
                listener.enterContribution(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitContribution" ):
                listener.exitContribution(self)




    def contribution(self):

        localctx = AriaMRParser.ContributionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_contribution)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 54
            self.atom_pair()
            self.state = 62
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==10:
                self.state = 55
                self.match(AriaMRParser.D)
                self.state = 56
                self.number_c()
                self.state = 57
                self.match(AriaMRParser.PlusMinus)
                self.state = 58
                self.number_c()
                self.state = 59
                self.match(AriaMRParser.Weight)
                self.state = 60
                self.number_c()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Atom_pairContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def atom_selection(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AriaMRParser.Atom_selectionContext)
            else:
                return self.getTypedRuleContext(AriaMRParser.Atom_selectionContext,i)


        def Hyphen(self):
            return self.getToken(AriaMRParser.Hyphen, 0)

        def getRuleIndex(self):
            return AriaMRParser.RULE_atom_pair

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAtom_pair" ):
                listener.enterAtom_pair(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAtom_pair" ):
                listener.exitAtom_pair(self)




    def atom_pair(self):

        localctx = AriaMRParser.Atom_pairContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_atom_pair)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 64
            self.atom_selection()
            self.state = 65
            self.match(AriaMRParser.Hyphen)
            self.state = 66
            self.atom_selection()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Atom_selectionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Simple_name(self, i:int=None):
            if i is None:
                return self.getTokens(AriaMRParser.Simple_name)
            else:
                return self.getToken(AriaMRParser.Simple_name, i)

        def getRuleIndex(self):
            return AriaMRParser.RULE_atom_selection

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAtom_selection" ):
                listener.enterAtom_selection(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAtom_selection" ):
                listener.exitAtom_selection(self)




    def atom_selection(self):

        localctx = AriaMRParser.Atom_selectionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_atom_selection)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 68
            self.match(AriaMRParser.Simple_name)
            self.state = 69
            self.match(AriaMRParser.Simple_name)
            self.state = 71
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,4,self._ctx)
            if la_ == 1:
                self.state = 70
                self.match(AriaMRParser.Simple_name)


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
            return self.getToken(AriaMRParser.Float, 0)

        def Integer(self):
            return self.getToken(AriaMRParser.Integer, 0)

        def getRuleIndex(self):
            return AriaMRParser.RULE_number

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNumber" ):
                listener.enterNumber(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNumber" ):
                listener.exitNumber(self)




    def number(self):

        localctx = AriaMRParser.NumberContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_number)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 73
            _la = self._input.LA(1)
            if not(_la==2 or _la==3):
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


    class Number_cContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Float(self):
            return self.getToken(AriaMRParser.Float, 0)

        def Integer(self):
            return self.getToken(AriaMRParser.Integer, 0)

        def getRuleIndex(self):
            return AriaMRParser.RULE_number_c

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNumber_c" ):
                listener.enterNumber_c(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNumber_c" ):
                listener.exitNumber_c(self)




    def number_c(self):

        localctx = AriaMRParser.Number_cContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_number_c)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 75
            _la = self._input.LA(1)
            if not(_la==2 or _la==3):
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





