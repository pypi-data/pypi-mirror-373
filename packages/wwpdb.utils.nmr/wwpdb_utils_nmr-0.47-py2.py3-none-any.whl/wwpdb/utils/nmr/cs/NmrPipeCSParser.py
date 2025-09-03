# Generated from NmrPipeCSParser.g4 by ANTLR 4.13.0
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
        4,1,40,131,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,1,0,1,0,1,0,1,0,5,0,23,8,0,10,0,12,0,26,9,0,1,
        0,1,0,1,1,1,1,1,1,1,1,1,1,1,1,4,1,36,8,1,11,1,12,1,37,1,1,1,1,1,
        1,1,1,1,1,1,1,5,1,46,8,1,10,1,12,1,49,9,1,1,1,1,1,1,1,1,1,3,1,55,
        8,1,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,4,2,70,8,
        2,11,2,12,2,71,1,3,1,3,1,3,1,3,1,3,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,
        4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,4,4,94,8,4,11,4,12,4,95,1,5,1,5,1,
        5,1,5,1,5,1,5,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,
        6,1,6,1,6,4,6,119,8,6,11,6,12,6,120,1,7,1,7,1,7,1,7,1,7,1,7,1,8,
        1,8,1,8,0,0,9,0,2,4,6,8,10,12,14,16,0,1,1,0,4,6,134,0,24,1,0,0,0,
        2,29,1,0,0,0,4,56,1,0,0,0,6,73,1,0,0,0,8,78,1,0,0,0,10,97,1,0,0,
        0,12,103,1,0,0,0,14,122,1,0,0,0,16,128,1,0,0,0,18,23,3,2,1,0,19,
        23,3,4,2,0,20,23,3,8,4,0,21,23,3,12,6,0,22,18,1,0,0,0,22,19,1,0,
        0,0,22,20,1,0,0,0,22,21,1,0,0,0,23,26,1,0,0,0,24,22,1,0,0,0,24,25,
        1,0,0,0,25,27,1,0,0,0,26,24,1,0,0,0,27,28,5,0,0,1,28,1,1,0,0,0,29,
        54,5,1,0,0,30,31,5,15,0,0,31,32,5,20,0,0,32,55,5,23,0,0,33,35,5,
        16,0,0,34,36,5,25,0,0,35,34,1,0,0,0,36,37,1,0,0,0,37,35,1,0,0,0,
        37,38,1,0,0,0,38,39,1,0,0,0,39,55,5,27,0,0,40,41,5,17,0,0,41,42,
        5,21,0,0,42,55,5,23,0,0,43,47,5,18,0,0,44,46,5,21,0,0,45,44,1,0,
        0,0,46,49,1,0,0,0,47,45,1,0,0,0,47,48,1,0,0,0,48,50,1,0,0,0,49,47,
        1,0,0,0,50,55,5,23,0,0,51,52,5,19,0,0,52,53,5,20,0,0,53,55,5,23,
        0,0,54,30,1,0,0,0,54,33,1,0,0,0,54,40,1,0,0,0,54,43,1,0,0,0,54,51,
        1,0,0,0,55,3,1,0,0,0,56,57,5,2,0,0,57,58,5,30,0,0,58,59,5,31,0,0,
        59,60,5,32,0,0,60,61,5,33,0,0,61,62,5,35,0,0,62,63,5,3,0,0,63,64,
        5,37,0,0,64,65,5,37,0,0,65,66,5,37,0,0,66,67,5,37,0,0,67,69,5,39,
        0,0,68,70,3,6,3,0,69,68,1,0,0,0,70,71,1,0,0,0,71,69,1,0,0,0,71,72,
        1,0,0,0,72,5,1,0,0,0,73,74,5,4,0,0,74,75,5,10,0,0,75,76,5,10,0,0,
        76,77,3,16,8,0,77,7,1,0,0,0,78,79,5,2,0,0,79,80,5,29,0,0,80,81,5,
        30,0,0,81,82,5,31,0,0,82,83,5,32,0,0,83,84,5,33,0,0,84,85,5,35,0,
        0,85,86,5,3,0,0,86,87,5,37,0,0,87,88,5,37,0,0,88,89,5,37,0,0,89,
        90,5,37,0,0,90,91,5,37,0,0,91,93,5,39,0,0,92,94,3,10,5,0,93,92,1,
        0,0,0,94,95,1,0,0,0,95,93,1,0,0,0,95,96,1,0,0,0,96,9,1,0,0,0,97,
        98,5,10,0,0,98,99,5,4,0,0,99,100,5,10,0,0,100,101,5,10,0,0,101,102,
        3,16,8,0,102,11,1,0,0,0,103,104,5,2,0,0,104,105,5,30,0,0,105,106,
        5,31,0,0,106,107,5,32,0,0,107,108,5,29,0,0,108,109,5,33,0,0,109,
        110,5,35,0,0,110,111,5,3,0,0,111,112,5,37,0,0,112,113,5,37,0,0,113,
        114,5,37,0,0,114,115,5,37,0,0,115,116,5,37,0,0,116,118,5,39,0,0,
        117,119,3,14,7,0,118,117,1,0,0,0,119,120,1,0,0,0,120,118,1,0,0,0,
        120,121,1,0,0,0,121,13,1,0,0,0,122,123,5,4,0,0,123,124,5,10,0,0,
        124,125,5,10,0,0,125,126,5,10,0,0,126,127,3,16,8,0,127,15,1,0,0,
        0,128,129,7,0,0,0,129,17,1,0,0,0,8,22,24,37,47,54,71,95,120
    ]

class NmrPipeCSParser ( Parser ):

    grammarFileName = "NmrPipeCSParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'DATA'", "'VARS'", "'FORMAT'", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "'FIRST_RESID'", "'SEQUENCE'", 
                     "'DB_NAME'", "'TAB_NAME'", "'TAB_ID'", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "'SEGNAME'", "'RESID'", "'RESNAME'", "'ATOMNAME'", 
                     "'SHIFT'" ]

    symbolicNames = [ "<INVALID>", "Data", "Vars", "Format", "Integer", 
                      "Float", "Float_DecimalComma", "SHARP_COMMENT", "EXCLM_COMMENT", 
                      "SMCLN_COMMENT", "Simple_name", "SPACE", "ENCLOSE_COMMENT", 
                      "SECTION_COMMENT", "LINE_COMMENT", "First_resid", 
                      "Sequence", "Db_name", "Tab_name", "Tab_id", "Integer_DA", 
                      "Simple_name_DA", "SPACE_DA", "RETURN_DA", "LINE_COMMENT_DA", 
                      "One_letter_code", "SPACE_SQ", "RETURN_SQ", "LINE_COMMENT_SQ", 
                      "Segname", "Resid", "Resname", "Atomname", "Shift", 
                      "SPACE_VA", "RETURN_VA", "LINE_COMMENT_VA", "Format_code", 
                      "SPACE_FO", "RETURN_FO", "LINE_COMMENT_FO" ]

    RULE_nmrpipe_cs = 0
    RULE_sequence = 1
    RULE_chemical_shifts = 2
    RULE_chemical_shift = 3
    RULE_chemical_shifts_sw_segid = 4
    RULE_chemical_shift_sw_segid = 5
    RULE_chemical_shifts_ew_segid = 6
    RULE_chemical_shift_ew_segid = 7
    RULE_number = 8

    ruleNames =  [ "nmrpipe_cs", "sequence", "chemical_shifts", "chemical_shift", 
                   "chemical_shifts_sw_segid", "chemical_shift_sw_segid", 
                   "chemical_shifts_ew_segid", "chemical_shift_ew_segid", 
                   "number" ]

    EOF = Token.EOF
    Data=1
    Vars=2
    Format=3
    Integer=4
    Float=5
    Float_DecimalComma=6
    SHARP_COMMENT=7
    EXCLM_COMMENT=8
    SMCLN_COMMENT=9
    Simple_name=10
    SPACE=11
    ENCLOSE_COMMENT=12
    SECTION_COMMENT=13
    LINE_COMMENT=14
    First_resid=15
    Sequence=16
    Db_name=17
    Tab_name=18
    Tab_id=19
    Integer_DA=20
    Simple_name_DA=21
    SPACE_DA=22
    RETURN_DA=23
    LINE_COMMENT_DA=24
    One_letter_code=25
    SPACE_SQ=26
    RETURN_SQ=27
    LINE_COMMENT_SQ=28
    Segname=29
    Resid=30
    Resname=31
    Atomname=32
    Shift=33
    SPACE_VA=34
    RETURN_VA=35
    LINE_COMMENT_VA=36
    Format_code=37
    SPACE_FO=38
    RETURN_FO=39
    LINE_COMMENT_FO=40

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.0")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class Nmrpipe_csContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(NmrPipeCSParser.EOF, 0)

        def sequence(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NmrPipeCSParser.SequenceContext)
            else:
                return self.getTypedRuleContext(NmrPipeCSParser.SequenceContext,i)


        def chemical_shifts(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NmrPipeCSParser.Chemical_shiftsContext)
            else:
                return self.getTypedRuleContext(NmrPipeCSParser.Chemical_shiftsContext,i)


        def chemical_shifts_sw_segid(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NmrPipeCSParser.Chemical_shifts_sw_segidContext)
            else:
                return self.getTypedRuleContext(NmrPipeCSParser.Chemical_shifts_sw_segidContext,i)


        def chemical_shifts_ew_segid(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NmrPipeCSParser.Chemical_shifts_ew_segidContext)
            else:
                return self.getTypedRuleContext(NmrPipeCSParser.Chemical_shifts_ew_segidContext,i)


        def getRuleIndex(self):
            return NmrPipeCSParser.RULE_nmrpipe_cs

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNmrpipe_cs" ):
                listener.enterNmrpipe_cs(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNmrpipe_cs" ):
                listener.exitNmrpipe_cs(self)




    def nmrpipe_cs(self):

        localctx = NmrPipeCSParser.Nmrpipe_csContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_nmrpipe_cs)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 24
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==1 or _la==2:
                self.state = 22
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,0,self._ctx)
                if la_ == 1:
                    self.state = 18
                    self.sequence()
                    pass

                elif la_ == 2:
                    self.state = 19
                    self.chemical_shifts()
                    pass

                elif la_ == 3:
                    self.state = 20
                    self.chemical_shifts_sw_segid()
                    pass

                elif la_ == 4:
                    self.state = 21
                    self.chemical_shifts_ew_segid()
                    pass


                self.state = 26
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 27
            self.match(NmrPipeCSParser.EOF)
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

        def Data(self):
            return self.getToken(NmrPipeCSParser.Data, 0)

        def First_resid(self):
            return self.getToken(NmrPipeCSParser.First_resid, 0)

        def Integer_DA(self):
            return self.getToken(NmrPipeCSParser.Integer_DA, 0)

        def RETURN_DA(self):
            return self.getToken(NmrPipeCSParser.RETURN_DA, 0)

        def Sequence(self):
            return self.getToken(NmrPipeCSParser.Sequence, 0)

        def RETURN_SQ(self):
            return self.getToken(NmrPipeCSParser.RETURN_SQ, 0)

        def Db_name(self):
            return self.getToken(NmrPipeCSParser.Db_name, 0)

        def Simple_name_DA(self, i:int=None):
            if i is None:
                return self.getTokens(NmrPipeCSParser.Simple_name_DA)
            else:
                return self.getToken(NmrPipeCSParser.Simple_name_DA, i)

        def Tab_name(self):
            return self.getToken(NmrPipeCSParser.Tab_name, 0)

        def Tab_id(self):
            return self.getToken(NmrPipeCSParser.Tab_id, 0)

        def One_letter_code(self, i:int=None):
            if i is None:
                return self.getTokens(NmrPipeCSParser.One_letter_code)
            else:
                return self.getToken(NmrPipeCSParser.One_letter_code, i)

        def getRuleIndex(self):
            return NmrPipeCSParser.RULE_sequence

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSequence" ):
                listener.enterSequence(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSequence" ):
                listener.exitSequence(self)




    def sequence(self):

        localctx = NmrPipeCSParser.SequenceContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_sequence)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 29
            self.match(NmrPipeCSParser.Data)
            self.state = 54
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [15]:
                self.state = 30
                self.match(NmrPipeCSParser.First_resid)
                self.state = 31
                self.match(NmrPipeCSParser.Integer_DA)
                self.state = 32
                self.match(NmrPipeCSParser.RETURN_DA)
                pass
            elif token in [16]:
                self.state = 33
                self.match(NmrPipeCSParser.Sequence)
                self.state = 35 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 34
                    self.match(NmrPipeCSParser.One_letter_code)
                    self.state = 37 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==25):
                        break

                self.state = 39
                self.match(NmrPipeCSParser.RETURN_SQ)
                pass
            elif token in [17]:
                self.state = 40
                self.match(NmrPipeCSParser.Db_name)
                self.state = 41
                self.match(NmrPipeCSParser.Simple_name_DA)
                self.state = 42
                self.match(NmrPipeCSParser.RETURN_DA)
                pass
            elif token in [18]:
                self.state = 43
                self.match(NmrPipeCSParser.Tab_name)
                self.state = 47
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==21:
                    self.state = 44
                    self.match(NmrPipeCSParser.Simple_name_DA)
                    self.state = 49
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 50
                self.match(NmrPipeCSParser.RETURN_DA)
                pass
            elif token in [19]:
                self.state = 51
                self.match(NmrPipeCSParser.Tab_id)
                self.state = 52
                self.match(NmrPipeCSParser.Integer_DA)
                self.state = 53
                self.match(NmrPipeCSParser.RETURN_DA)
                pass
            else:
                raise NoViableAltException(self)

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

        def Vars(self):
            return self.getToken(NmrPipeCSParser.Vars, 0)

        def Resid(self):
            return self.getToken(NmrPipeCSParser.Resid, 0)

        def Resname(self):
            return self.getToken(NmrPipeCSParser.Resname, 0)

        def Atomname(self):
            return self.getToken(NmrPipeCSParser.Atomname, 0)

        def Shift(self):
            return self.getToken(NmrPipeCSParser.Shift, 0)

        def RETURN_VA(self):
            return self.getToken(NmrPipeCSParser.RETURN_VA, 0)

        def Format(self):
            return self.getToken(NmrPipeCSParser.Format, 0)

        def Format_code(self, i:int=None):
            if i is None:
                return self.getTokens(NmrPipeCSParser.Format_code)
            else:
                return self.getToken(NmrPipeCSParser.Format_code, i)

        def RETURN_FO(self):
            return self.getToken(NmrPipeCSParser.RETURN_FO, 0)

        def chemical_shift(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NmrPipeCSParser.Chemical_shiftContext)
            else:
                return self.getTypedRuleContext(NmrPipeCSParser.Chemical_shiftContext,i)


        def getRuleIndex(self):
            return NmrPipeCSParser.RULE_chemical_shifts

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterChemical_shifts" ):
                listener.enterChemical_shifts(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitChemical_shifts" ):
                listener.exitChemical_shifts(self)




    def chemical_shifts(self):

        localctx = NmrPipeCSParser.Chemical_shiftsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_chemical_shifts)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 56
            self.match(NmrPipeCSParser.Vars)
            self.state = 57
            self.match(NmrPipeCSParser.Resid)
            self.state = 58
            self.match(NmrPipeCSParser.Resname)
            self.state = 59
            self.match(NmrPipeCSParser.Atomname)
            self.state = 60
            self.match(NmrPipeCSParser.Shift)
            self.state = 61
            self.match(NmrPipeCSParser.RETURN_VA)
            self.state = 62
            self.match(NmrPipeCSParser.Format)
            self.state = 63
            self.match(NmrPipeCSParser.Format_code)
            self.state = 64
            self.match(NmrPipeCSParser.Format_code)
            self.state = 65
            self.match(NmrPipeCSParser.Format_code)
            self.state = 66
            self.match(NmrPipeCSParser.Format_code)
            self.state = 67
            self.match(NmrPipeCSParser.RETURN_FO)
            self.state = 69 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 68
                self.chemical_shift()
                self.state = 71 
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


    class Chemical_shiftContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Integer(self):
            return self.getToken(NmrPipeCSParser.Integer, 0)

        def Simple_name(self, i:int=None):
            if i is None:
                return self.getTokens(NmrPipeCSParser.Simple_name)
            else:
                return self.getToken(NmrPipeCSParser.Simple_name, i)

        def number(self):
            return self.getTypedRuleContext(NmrPipeCSParser.NumberContext,0)


        def getRuleIndex(self):
            return NmrPipeCSParser.RULE_chemical_shift

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterChemical_shift" ):
                listener.enterChemical_shift(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitChemical_shift" ):
                listener.exitChemical_shift(self)




    def chemical_shift(self):

        localctx = NmrPipeCSParser.Chemical_shiftContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_chemical_shift)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 73
            self.match(NmrPipeCSParser.Integer)
            self.state = 74
            self.match(NmrPipeCSParser.Simple_name)
            self.state = 75
            self.match(NmrPipeCSParser.Simple_name)
            self.state = 76
            self.number()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Chemical_shifts_sw_segidContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Vars(self):
            return self.getToken(NmrPipeCSParser.Vars, 0)

        def Segname(self):
            return self.getToken(NmrPipeCSParser.Segname, 0)

        def Resid(self):
            return self.getToken(NmrPipeCSParser.Resid, 0)

        def Resname(self):
            return self.getToken(NmrPipeCSParser.Resname, 0)

        def Atomname(self):
            return self.getToken(NmrPipeCSParser.Atomname, 0)

        def Shift(self):
            return self.getToken(NmrPipeCSParser.Shift, 0)

        def RETURN_VA(self):
            return self.getToken(NmrPipeCSParser.RETURN_VA, 0)

        def Format(self):
            return self.getToken(NmrPipeCSParser.Format, 0)

        def Format_code(self, i:int=None):
            if i is None:
                return self.getTokens(NmrPipeCSParser.Format_code)
            else:
                return self.getToken(NmrPipeCSParser.Format_code, i)

        def RETURN_FO(self):
            return self.getToken(NmrPipeCSParser.RETURN_FO, 0)

        def chemical_shift_sw_segid(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NmrPipeCSParser.Chemical_shift_sw_segidContext)
            else:
                return self.getTypedRuleContext(NmrPipeCSParser.Chemical_shift_sw_segidContext,i)


        def getRuleIndex(self):
            return NmrPipeCSParser.RULE_chemical_shifts_sw_segid

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterChemical_shifts_sw_segid" ):
                listener.enterChemical_shifts_sw_segid(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitChemical_shifts_sw_segid" ):
                listener.exitChemical_shifts_sw_segid(self)




    def chemical_shifts_sw_segid(self):

        localctx = NmrPipeCSParser.Chemical_shifts_sw_segidContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_chemical_shifts_sw_segid)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 78
            self.match(NmrPipeCSParser.Vars)
            self.state = 79
            self.match(NmrPipeCSParser.Segname)
            self.state = 80
            self.match(NmrPipeCSParser.Resid)
            self.state = 81
            self.match(NmrPipeCSParser.Resname)
            self.state = 82
            self.match(NmrPipeCSParser.Atomname)
            self.state = 83
            self.match(NmrPipeCSParser.Shift)
            self.state = 84
            self.match(NmrPipeCSParser.RETURN_VA)
            self.state = 85
            self.match(NmrPipeCSParser.Format)
            self.state = 86
            self.match(NmrPipeCSParser.Format_code)
            self.state = 87
            self.match(NmrPipeCSParser.Format_code)
            self.state = 88
            self.match(NmrPipeCSParser.Format_code)
            self.state = 89
            self.match(NmrPipeCSParser.Format_code)
            self.state = 90
            self.match(NmrPipeCSParser.Format_code)
            self.state = 91
            self.match(NmrPipeCSParser.RETURN_FO)
            self.state = 93 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 92
                self.chemical_shift_sw_segid()
                self.state = 95 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==10):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Chemical_shift_sw_segidContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Simple_name(self, i:int=None):
            if i is None:
                return self.getTokens(NmrPipeCSParser.Simple_name)
            else:
                return self.getToken(NmrPipeCSParser.Simple_name, i)

        def Integer(self):
            return self.getToken(NmrPipeCSParser.Integer, 0)

        def number(self):
            return self.getTypedRuleContext(NmrPipeCSParser.NumberContext,0)


        def getRuleIndex(self):
            return NmrPipeCSParser.RULE_chemical_shift_sw_segid

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterChemical_shift_sw_segid" ):
                listener.enterChemical_shift_sw_segid(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitChemical_shift_sw_segid" ):
                listener.exitChemical_shift_sw_segid(self)




    def chemical_shift_sw_segid(self):

        localctx = NmrPipeCSParser.Chemical_shift_sw_segidContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_chemical_shift_sw_segid)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 97
            self.match(NmrPipeCSParser.Simple_name)
            self.state = 98
            self.match(NmrPipeCSParser.Integer)
            self.state = 99
            self.match(NmrPipeCSParser.Simple_name)
            self.state = 100
            self.match(NmrPipeCSParser.Simple_name)
            self.state = 101
            self.number()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Chemical_shifts_ew_segidContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Vars(self):
            return self.getToken(NmrPipeCSParser.Vars, 0)

        def Resid(self):
            return self.getToken(NmrPipeCSParser.Resid, 0)

        def Resname(self):
            return self.getToken(NmrPipeCSParser.Resname, 0)

        def Atomname(self):
            return self.getToken(NmrPipeCSParser.Atomname, 0)

        def Segname(self):
            return self.getToken(NmrPipeCSParser.Segname, 0)

        def Shift(self):
            return self.getToken(NmrPipeCSParser.Shift, 0)

        def RETURN_VA(self):
            return self.getToken(NmrPipeCSParser.RETURN_VA, 0)

        def Format(self):
            return self.getToken(NmrPipeCSParser.Format, 0)

        def Format_code(self, i:int=None):
            if i is None:
                return self.getTokens(NmrPipeCSParser.Format_code)
            else:
                return self.getToken(NmrPipeCSParser.Format_code, i)

        def RETURN_FO(self):
            return self.getToken(NmrPipeCSParser.RETURN_FO, 0)

        def chemical_shift_ew_segid(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NmrPipeCSParser.Chemical_shift_ew_segidContext)
            else:
                return self.getTypedRuleContext(NmrPipeCSParser.Chemical_shift_ew_segidContext,i)


        def getRuleIndex(self):
            return NmrPipeCSParser.RULE_chemical_shifts_ew_segid

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterChemical_shifts_ew_segid" ):
                listener.enterChemical_shifts_ew_segid(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitChemical_shifts_ew_segid" ):
                listener.exitChemical_shifts_ew_segid(self)




    def chemical_shifts_ew_segid(self):

        localctx = NmrPipeCSParser.Chemical_shifts_ew_segidContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_chemical_shifts_ew_segid)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 103
            self.match(NmrPipeCSParser.Vars)
            self.state = 104
            self.match(NmrPipeCSParser.Resid)
            self.state = 105
            self.match(NmrPipeCSParser.Resname)
            self.state = 106
            self.match(NmrPipeCSParser.Atomname)
            self.state = 107
            self.match(NmrPipeCSParser.Segname)
            self.state = 108
            self.match(NmrPipeCSParser.Shift)
            self.state = 109
            self.match(NmrPipeCSParser.RETURN_VA)
            self.state = 110
            self.match(NmrPipeCSParser.Format)
            self.state = 111
            self.match(NmrPipeCSParser.Format_code)
            self.state = 112
            self.match(NmrPipeCSParser.Format_code)
            self.state = 113
            self.match(NmrPipeCSParser.Format_code)
            self.state = 114
            self.match(NmrPipeCSParser.Format_code)
            self.state = 115
            self.match(NmrPipeCSParser.Format_code)
            self.state = 116
            self.match(NmrPipeCSParser.RETURN_FO)
            self.state = 118 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 117
                self.chemical_shift_ew_segid()
                self.state = 120 
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


    class Chemical_shift_ew_segidContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Integer(self):
            return self.getToken(NmrPipeCSParser.Integer, 0)

        def Simple_name(self, i:int=None):
            if i is None:
                return self.getTokens(NmrPipeCSParser.Simple_name)
            else:
                return self.getToken(NmrPipeCSParser.Simple_name, i)

        def number(self):
            return self.getTypedRuleContext(NmrPipeCSParser.NumberContext,0)


        def getRuleIndex(self):
            return NmrPipeCSParser.RULE_chemical_shift_ew_segid

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterChemical_shift_ew_segid" ):
                listener.enterChemical_shift_ew_segid(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitChemical_shift_ew_segid" ):
                listener.exitChemical_shift_ew_segid(self)




    def chemical_shift_ew_segid(self):

        localctx = NmrPipeCSParser.Chemical_shift_ew_segidContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_chemical_shift_ew_segid)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 122
            self.match(NmrPipeCSParser.Integer)
            self.state = 123
            self.match(NmrPipeCSParser.Simple_name)
            self.state = 124
            self.match(NmrPipeCSParser.Simple_name)
            self.state = 125
            self.match(NmrPipeCSParser.Simple_name)
            self.state = 126
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
            return self.getToken(NmrPipeCSParser.Float, 0)

        def Float_DecimalComma(self):
            return self.getToken(NmrPipeCSParser.Float_DecimalComma, 0)

        def Integer(self):
            return self.getToken(NmrPipeCSParser.Integer, 0)

        def getRuleIndex(self):
            return NmrPipeCSParser.RULE_number

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNumber" ):
                listener.enterNumber(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNumber" ):
                listener.exitNumber(self)




    def number(self):

        localctx = NmrPipeCSParser.NumberContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_number)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 128
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 112) != 0)):
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





