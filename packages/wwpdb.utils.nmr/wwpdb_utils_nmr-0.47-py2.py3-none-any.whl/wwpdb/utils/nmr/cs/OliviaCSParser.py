# Generated from OliviaCSParser.g4 by ANTLR 4.13.0
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
        4,1,42,103,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,1,0,3,0,16,8,0,1,0,1,0,1,0,1,0,5,0,22,8,0,10,0,12,0,25,9,0,1,0,
        1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,4,1,45,8,1,11,1,12,1,46,1,1,1,1,1,2,1,2,1,2,1,2,1,2,1,3,1,3,
        1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,
        1,3,1,3,1,3,1,3,4,3,78,8,3,11,3,12,3,79,1,3,1,3,1,4,1,4,1,4,1,4,
        1,4,1,4,1,4,1,4,1,5,1,5,1,6,1,6,5,6,96,8,6,10,6,12,6,99,9,6,1,6,
        1,6,1,6,0,0,7,0,2,4,6,8,10,12,0,3,1,0,24,26,1,0,19,21,1,0,7,9,103,
        0,15,1,0,0,0,2,28,1,0,0,0,4,50,1,0,0,0,6,55,1,0,0,0,8,83,1,0,0,0,
        10,91,1,0,0,0,12,93,1,0,0,0,14,16,5,15,0,0,15,14,1,0,0,0,15,16,1,
        0,0,0,16,23,1,0,0,0,17,22,3,12,6,0,18,22,3,2,1,0,19,22,3,6,3,0,20,
        22,5,15,0,0,21,17,1,0,0,0,21,18,1,0,0,0,21,19,1,0,0,0,21,20,1,0,
        0,0,22,25,1,0,0,0,23,21,1,0,0,0,23,24,1,0,0,0,24,26,1,0,0,0,25,23,
        1,0,0,0,26,27,5,0,0,1,27,1,1,0,0,0,28,29,5,1,0,0,29,30,5,18,0,0,
        30,31,5,23,0,0,31,32,5,2,0,0,32,33,7,0,0,0,33,34,5,28,0,0,34,35,
        5,3,0,0,35,36,5,29,0,0,36,37,5,30,0,0,37,38,5,31,0,0,38,39,5,36,
        0,0,39,40,5,37,0,0,40,41,5,37,0,0,41,42,5,37,0,0,42,44,5,39,0,0,
        43,45,3,4,2,0,44,43,1,0,0,0,45,46,1,0,0,0,46,44,1,0,0,0,46,47,1,
        0,0,0,47,48,1,0,0,0,48,49,5,4,0,0,49,3,1,0,0,0,50,51,5,13,0,0,51,
        52,5,13,0,0,52,53,5,7,0,0,53,54,5,15,0,0,54,5,1,0,0,0,55,56,5,1,
        0,0,56,57,7,1,0,0,57,58,5,23,0,0,58,59,5,2,0,0,59,60,7,0,0,0,60,
        61,5,28,0,0,61,62,5,3,0,0,62,63,5,29,0,0,63,64,5,30,0,0,64,65,5,
        31,0,0,65,66,5,32,0,0,66,67,5,33,0,0,67,68,5,34,0,0,68,69,5,36,0,
        0,69,70,5,37,0,0,70,71,5,37,0,0,71,72,5,37,0,0,72,73,5,37,0,0,73,
        74,5,37,0,0,74,75,5,37,0,0,75,77,5,39,0,0,76,78,3,8,4,0,77,76,1,
        0,0,0,78,79,1,0,0,0,79,77,1,0,0,0,79,80,1,0,0,0,80,81,1,0,0,0,81,
        82,5,4,0,0,82,7,1,0,0,0,83,84,5,13,0,0,84,85,5,13,0,0,85,86,5,7,
        0,0,86,87,5,13,0,0,87,88,3,10,5,0,88,89,3,10,5,0,89,90,5,15,0,0,
        90,9,1,0,0,0,91,92,7,2,0,0,92,11,1,0,0,0,93,97,5,10,0,0,94,96,5,
        40,0,0,95,94,1,0,0,0,96,99,1,0,0,0,97,95,1,0,0,0,97,98,1,0,0,0,98,
        100,1,0,0,0,99,97,1,0,0,0,100,101,5,42,0,0,101,13,1,0,0,0,6,15,21,
        23,46,79,97
    ]

class OliviaCSParser ( Parser ):

    grammarFileName = "OliviaCSParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'TYPEDEF'", "'SEPARATOR'", "'FORMAT\\n'", 
                     "'UNFORMAT'", "'EOF'", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "'REMARK'", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "'SEQUENCE'", "'ASS_TBL_H2O'", "'ASS_TBL_TRO'", 
                     "'ASS_TBL_D2O'", "<INVALID>", "<INVALID>", "'TAB'", 
                     "'COMMA'", "'SPACE'", "<INVALID>", "<INVALID>", "'CHAIN'", 
                     "'RESNAME'", "'SEQNUM'", "'ATOMNAME'", "'SHIFT'", "'STDDEV'" ]

    symbolicNames = [ "<INVALID>", "Typedef", "Separator", "Format", "Unformat", 
                      "Eof", "Null_string", "Integer", "Float", "Real", 
                      "COMMENT", "SHARP_COMMENT", "EXCLM_COMMENT", "Simple_name", 
                      "SPACE", "RETURN", "SECTION_COMMENT", "LINE_COMMENT", 
                      "Sequence", "Ass_tbl_h2o", "Ass_tbl_tro", "Ass_tbl_d2o", 
                      "SPACE_TD", "RETURN_TD", "Tab", "Comma", "Space", 
                      "SPACE_SE", "RETURN_SE", "Chain", "Resname", "Seqnum", 
                      "Atomname", "Shift", "Stddev", "SPACE_FO", "RETURN_FO", 
                      "Printf_string", "SPACE_PF", "RETURN_PF", "Any_name", 
                      "SPACE_CM", "RETURN_CM" ]

    RULE_olivia_cs = 0
    RULE_sequence = 1
    RULE_residue = 2
    RULE_chemical_shifts = 3
    RULE_chemical_shift = 4
    RULE_number = 5
    RULE_comment = 6

    ruleNames =  [ "olivia_cs", "sequence", "residue", "chemical_shifts", 
                   "chemical_shift", "number", "comment" ]

    EOF = Token.EOF
    Typedef=1
    Separator=2
    Format=3
    Unformat=4
    Eof=5
    Null_string=6
    Integer=7
    Float=8
    Real=9
    COMMENT=10
    SHARP_COMMENT=11
    EXCLM_COMMENT=12
    Simple_name=13
    SPACE=14
    RETURN=15
    SECTION_COMMENT=16
    LINE_COMMENT=17
    Sequence=18
    Ass_tbl_h2o=19
    Ass_tbl_tro=20
    Ass_tbl_d2o=21
    SPACE_TD=22
    RETURN_TD=23
    Tab=24
    Comma=25
    Space=26
    SPACE_SE=27
    RETURN_SE=28
    Chain=29
    Resname=30
    Seqnum=31
    Atomname=32
    Shift=33
    Stddev=34
    SPACE_FO=35
    RETURN_FO=36
    Printf_string=37
    SPACE_PF=38
    RETURN_PF=39
    Any_name=40
    SPACE_CM=41
    RETURN_CM=42

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.0")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class Olivia_csContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(OliviaCSParser.EOF, 0)

        def RETURN(self, i:int=None):
            if i is None:
                return self.getTokens(OliviaCSParser.RETURN)
            else:
                return self.getToken(OliviaCSParser.RETURN, i)

        def comment(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(OliviaCSParser.CommentContext)
            else:
                return self.getTypedRuleContext(OliviaCSParser.CommentContext,i)


        def sequence(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(OliviaCSParser.SequenceContext)
            else:
                return self.getTypedRuleContext(OliviaCSParser.SequenceContext,i)


        def chemical_shifts(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(OliviaCSParser.Chemical_shiftsContext)
            else:
                return self.getTypedRuleContext(OliviaCSParser.Chemical_shiftsContext,i)


        def getRuleIndex(self):
            return OliviaCSParser.RULE_olivia_cs

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOlivia_cs" ):
                listener.enterOlivia_cs(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOlivia_cs" ):
                listener.exitOlivia_cs(self)




    def olivia_cs(self):

        localctx = OliviaCSParser.Olivia_csContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_olivia_cs)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 15
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,0,self._ctx)
            if la_ == 1:
                self.state = 14
                self.match(OliviaCSParser.RETURN)


            self.state = 23
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 33794) != 0):
                self.state = 21
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,1,self._ctx)
                if la_ == 1:
                    self.state = 17
                    self.comment()
                    pass

                elif la_ == 2:
                    self.state = 18
                    self.sequence()
                    pass

                elif la_ == 3:
                    self.state = 19
                    self.chemical_shifts()
                    pass

                elif la_ == 4:
                    self.state = 20
                    self.match(OliviaCSParser.RETURN)
                    pass


                self.state = 25
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 26
            self.match(OliviaCSParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SequenceContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Typedef(self):
            return self.getToken(OliviaCSParser.Typedef, 0)

        def Sequence(self):
            return self.getToken(OliviaCSParser.Sequence, 0)

        def RETURN_TD(self):
            return self.getToken(OliviaCSParser.RETURN_TD, 0)

        def Separator(self):
            return self.getToken(OliviaCSParser.Separator, 0)

        def RETURN_SE(self):
            return self.getToken(OliviaCSParser.RETURN_SE, 0)

        def Format(self):
            return self.getToken(OliviaCSParser.Format, 0)

        def Chain(self):
            return self.getToken(OliviaCSParser.Chain, 0)

        def Resname(self):
            return self.getToken(OliviaCSParser.Resname, 0)

        def Seqnum(self):
            return self.getToken(OliviaCSParser.Seqnum, 0)

        def RETURN_FO(self):
            return self.getToken(OliviaCSParser.RETURN_FO, 0)

        def Printf_string(self, i:int=None):
            if i is None:
                return self.getTokens(OliviaCSParser.Printf_string)
            else:
                return self.getToken(OliviaCSParser.Printf_string, i)

        def RETURN_PF(self):
            return self.getToken(OliviaCSParser.RETURN_PF, 0)

        def Unformat(self):
            return self.getToken(OliviaCSParser.Unformat, 0)

        def Tab(self):
            return self.getToken(OliviaCSParser.Tab, 0)

        def Comma(self):
            return self.getToken(OliviaCSParser.Comma, 0)

        def Space(self):
            return self.getToken(OliviaCSParser.Space, 0)

        def residue(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(OliviaCSParser.ResidueContext)
            else:
                return self.getTypedRuleContext(OliviaCSParser.ResidueContext,i)


        def getRuleIndex(self):
            return OliviaCSParser.RULE_sequence

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSequence" ):
                listener.enterSequence(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSequence" ):
                listener.exitSequence(self)




    def sequence(self):

        localctx = OliviaCSParser.SequenceContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_sequence)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 28
            self.match(OliviaCSParser.Typedef)
            self.state = 29
            self.match(OliviaCSParser.Sequence)
            self.state = 30
            self.match(OliviaCSParser.RETURN_TD)
            self.state = 31
            self.match(OliviaCSParser.Separator)
            self.state = 32
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 117440512) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 33
            self.match(OliviaCSParser.RETURN_SE)
            self.state = 34
            self.match(OliviaCSParser.Format)
            self.state = 35
            self.match(OliviaCSParser.Chain)
            self.state = 36
            self.match(OliviaCSParser.Resname)
            self.state = 37
            self.match(OliviaCSParser.Seqnum)
            self.state = 38
            self.match(OliviaCSParser.RETURN_FO)
            self.state = 39
            self.match(OliviaCSParser.Printf_string)
            self.state = 40
            self.match(OliviaCSParser.Printf_string)
            self.state = 41
            self.match(OliviaCSParser.Printf_string)
            self.state = 42
            self.match(OliviaCSParser.RETURN_PF)
            self.state = 44 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 43
                self.residue()
                self.state = 46 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==13):
                    break

            self.state = 48
            self.match(OliviaCSParser.Unformat)
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

        def Simple_name(self, i:int=None):
            if i is None:
                return self.getTokens(OliviaCSParser.Simple_name)
            else:
                return self.getToken(OliviaCSParser.Simple_name, i)

        def Integer(self):
            return self.getToken(OliviaCSParser.Integer, 0)

        def RETURN(self):
            return self.getToken(OliviaCSParser.RETURN, 0)

        def getRuleIndex(self):
            return OliviaCSParser.RULE_residue

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterResidue" ):
                listener.enterResidue(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitResidue" ):
                listener.exitResidue(self)




    def residue(self):

        localctx = OliviaCSParser.ResidueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_residue)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 50
            self.match(OliviaCSParser.Simple_name)
            self.state = 51
            self.match(OliviaCSParser.Simple_name)
            self.state = 52
            self.match(OliviaCSParser.Integer)
            self.state = 53
            self.match(OliviaCSParser.RETURN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Chemical_shiftsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Typedef(self):
            return self.getToken(OliviaCSParser.Typedef, 0)

        def RETURN_TD(self):
            return self.getToken(OliviaCSParser.RETURN_TD, 0)

        def Separator(self):
            return self.getToken(OliviaCSParser.Separator, 0)

        def RETURN_SE(self):
            return self.getToken(OliviaCSParser.RETURN_SE, 0)

        def Format(self):
            return self.getToken(OliviaCSParser.Format, 0)

        def Chain(self):
            return self.getToken(OliviaCSParser.Chain, 0)

        def Resname(self):
            return self.getToken(OliviaCSParser.Resname, 0)

        def Seqnum(self):
            return self.getToken(OliviaCSParser.Seqnum, 0)

        def Atomname(self):
            return self.getToken(OliviaCSParser.Atomname, 0)

        def Shift(self):
            return self.getToken(OliviaCSParser.Shift, 0)

        def Stddev(self):
            return self.getToken(OliviaCSParser.Stddev, 0)

        def RETURN_FO(self):
            return self.getToken(OliviaCSParser.RETURN_FO, 0)

        def Printf_string(self, i:int=None):
            if i is None:
                return self.getTokens(OliviaCSParser.Printf_string)
            else:
                return self.getToken(OliviaCSParser.Printf_string, i)

        def RETURN_PF(self):
            return self.getToken(OliviaCSParser.RETURN_PF, 0)

        def Unformat(self):
            return self.getToken(OliviaCSParser.Unformat, 0)

        def Ass_tbl_h2o(self):
            return self.getToken(OliviaCSParser.Ass_tbl_h2o, 0)

        def Ass_tbl_tro(self):
            return self.getToken(OliviaCSParser.Ass_tbl_tro, 0)

        def Ass_tbl_d2o(self):
            return self.getToken(OliviaCSParser.Ass_tbl_d2o, 0)

        def Tab(self):
            return self.getToken(OliviaCSParser.Tab, 0)

        def Comma(self):
            return self.getToken(OliviaCSParser.Comma, 0)

        def Space(self):
            return self.getToken(OliviaCSParser.Space, 0)

        def chemical_shift(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(OliviaCSParser.Chemical_shiftContext)
            else:
                return self.getTypedRuleContext(OliviaCSParser.Chemical_shiftContext,i)


        def getRuleIndex(self):
            return OliviaCSParser.RULE_chemical_shifts

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterChemical_shifts" ):
                listener.enterChemical_shifts(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitChemical_shifts" ):
                listener.exitChemical_shifts(self)




    def chemical_shifts(self):

        localctx = OliviaCSParser.Chemical_shiftsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_chemical_shifts)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 55
            self.match(OliviaCSParser.Typedef)
            self.state = 56
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 3670016) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 57
            self.match(OliviaCSParser.RETURN_TD)
            self.state = 58
            self.match(OliviaCSParser.Separator)
            self.state = 59
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 117440512) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 60
            self.match(OliviaCSParser.RETURN_SE)
            self.state = 61
            self.match(OliviaCSParser.Format)
            self.state = 62
            self.match(OliviaCSParser.Chain)
            self.state = 63
            self.match(OliviaCSParser.Resname)
            self.state = 64
            self.match(OliviaCSParser.Seqnum)
            self.state = 65
            self.match(OliviaCSParser.Atomname)
            self.state = 66
            self.match(OliviaCSParser.Shift)
            self.state = 67
            self.match(OliviaCSParser.Stddev)
            self.state = 68
            self.match(OliviaCSParser.RETURN_FO)
            self.state = 69
            self.match(OliviaCSParser.Printf_string)
            self.state = 70
            self.match(OliviaCSParser.Printf_string)
            self.state = 71
            self.match(OliviaCSParser.Printf_string)
            self.state = 72
            self.match(OliviaCSParser.Printf_string)
            self.state = 73
            self.match(OliviaCSParser.Printf_string)
            self.state = 74
            self.match(OliviaCSParser.Printf_string)
            self.state = 75
            self.match(OliviaCSParser.RETURN_PF)
            self.state = 77 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 76
                self.chemical_shift()
                self.state = 79 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==13):
                    break

            self.state = 81
            self.match(OliviaCSParser.Unformat)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Chemical_shiftContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Simple_name(self, i:int=None):
            if i is None:
                return self.getTokens(OliviaCSParser.Simple_name)
            else:
                return self.getToken(OliviaCSParser.Simple_name, i)

        def Integer(self):
            return self.getToken(OliviaCSParser.Integer, 0)

        def number(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(OliviaCSParser.NumberContext)
            else:
                return self.getTypedRuleContext(OliviaCSParser.NumberContext,i)


        def RETURN(self):
            return self.getToken(OliviaCSParser.RETURN, 0)

        def getRuleIndex(self):
            return OliviaCSParser.RULE_chemical_shift

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterChemical_shift" ):
                listener.enterChemical_shift(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitChemical_shift" ):
                listener.exitChemical_shift(self)




    def chemical_shift(self):

        localctx = OliviaCSParser.Chemical_shiftContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_chemical_shift)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 83
            self.match(OliviaCSParser.Simple_name)
            self.state = 84
            self.match(OliviaCSParser.Simple_name)
            self.state = 85
            self.match(OliviaCSParser.Integer)
            self.state = 86
            self.match(OliviaCSParser.Simple_name)
            self.state = 87
            self.number()
            self.state = 88
            self.number()
            self.state = 89
            self.match(OliviaCSParser.RETURN)
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

        def Integer(self):
            return self.getToken(OliviaCSParser.Integer, 0)

        def Float(self):
            return self.getToken(OliviaCSParser.Float, 0)

        def Real(self):
            return self.getToken(OliviaCSParser.Real, 0)

        def getRuleIndex(self):
            return OliviaCSParser.RULE_number

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNumber" ):
                listener.enterNumber(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNumber" ):
                listener.exitNumber(self)




    def number(self):

        localctx = OliviaCSParser.NumberContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_number)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 91
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 896) != 0)):
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


    class CommentContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def COMMENT(self):
            return self.getToken(OliviaCSParser.COMMENT, 0)

        def RETURN_CM(self):
            return self.getToken(OliviaCSParser.RETURN_CM, 0)

        def Any_name(self, i:int=None):
            if i is None:
                return self.getTokens(OliviaCSParser.Any_name)
            else:
                return self.getToken(OliviaCSParser.Any_name, i)

        def getRuleIndex(self):
            return OliviaCSParser.RULE_comment

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterComment" ):
                listener.enterComment(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitComment" ):
                listener.exitComment(self)




    def comment(self):

        localctx = OliviaCSParser.CommentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_comment)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 93
            self.match(OliviaCSParser.COMMENT)
            self.state = 97
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==40:
                self.state = 94
                self.match(OliviaCSParser.Any_name)
                self.state = 99
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 100
            self.match(OliviaCSParser.RETURN_CM)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





