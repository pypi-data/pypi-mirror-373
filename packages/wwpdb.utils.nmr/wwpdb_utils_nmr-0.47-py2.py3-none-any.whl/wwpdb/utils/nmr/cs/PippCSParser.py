# Generated from PippCSParser.g4 by ANTLR 4.13.0
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
        4,1,28,92,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,1,0,3,0,16,8,0,1,0,1,0,5,0,20,8,0,10,0,12,0,23,9,0,1,0,1,0,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,3,1,34,8,1,1,1,4,1,37,8,1,11,1,12,1,38,1,
        2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,4,2,49,8,2,11,2,12,2,50,1,3,1,3,1,
        3,1,3,1,3,1,3,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,
        4,4,4,72,8,4,11,4,12,4,73,1,4,1,4,1,4,1,5,1,5,1,5,1,5,4,5,83,8,5,
        11,5,12,5,84,1,5,1,5,1,5,1,6,1,6,1,6,0,0,7,0,2,4,6,8,10,12,0,3,2,
        0,5,5,21,21,1,1,18,18,2,0,12,13,16,16,92,0,15,1,0,0,0,2,26,1,0,0,
        0,4,40,1,0,0,0,6,52,1,0,0,0,8,58,1,0,0,0,10,78,1,0,0,0,12,89,1,0,
        0,0,14,16,5,18,0,0,15,14,1,0,0,0,15,16,1,0,0,0,16,21,1,0,0,0,17,
        20,3,2,1,0,18,20,5,18,0,0,19,17,1,0,0,0,19,18,1,0,0,0,20,23,1,0,
        0,0,21,19,1,0,0,0,21,22,1,0,0,0,22,24,1,0,0,0,23,21,1,0,0,0,24,25,
        5,0,0,1,25,1,1,0,0,0,26,27,5,1,0,0,27,28,5,2,0,0,28,29,5,18,0,0,
        29,30,5,3,0,0,30,31,5,12,0,0,31,33,5,18,0,0,32,34,3,4,2,0,33,32,
        1,0,0,0,33,34,1,0,0,0,34,36,1,0,0,0,35,37,3,8,4,0,36,35,1,0,0,0,
        37,38,1,0,0,0,38,36,1,0,0,0,38,39,1,0,0,0,39,3,1,0,0,0,40,41,5,4,
        0,0,41,42,5,28,0,0,42,43,5,22,0,0,43,44,5,23,0,0,44,45,5,24,0,0,
        45,46,5,25,0,0,46,48,5,28,0,0,47,49,3,6,3,0,48,47,1,0,0,0,49,50,
        1,0,0,0,50,48,1,0,0,0,50,51,1,0,0,0,51,5,1,0,0,0,52,53,5,26,0,0,
        53,54,5,26,0,0,54,55,5,26,0,0,55,56,5,26,0,0,56,57,5,28,0,0,57,7,
        1,0,0,0,58,59,7,0,0,0,59,60,5,12,0,0,60,61,5,18,0,0,61,62,5,6,0,
        0,62,63,5,16,0,0,63,64,5,18,0,0,64,65,5,7,0,0,65,66,5,12,0,0,66,
        67,5,18,0,0,67,68,5,8,0,0,68,69,5,12,0,0,69,71,5,18,0,0,70,72,3,
        10,5,0,71,70,1,0,0,0,72,73,1,0,0,0,73,71,1,0,0,0,73,74,1,0,0,0,74,
        75,1,0,0,0,75,76,5,9,0,0,76,77,7,1,0,0,77,9,1,0,0,0,78,79,5,16,0,
        0,79,80,3,12,6,0,80,82,5,10,0,0,81,83,5,16,0,0,82,81,1,0,0,0,83,
        84,1,0,0,0,84,82,1,0,0,0,84,85,1,0,0,0,85,86,1,0,0,0,86,87,5,11,
        0,0,87,88,5,18,0,0,88,11,1,0,0,0,89,90,7,2,0,0,90,13,1,0,0,0,8,15,
        19,21,33,38,50,73,84
    ]

class PippCSParser ( Parser ):

    grammarFileName = "PippCSParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'SHIFT_FL_FRMT'", "'RES_SIAD'", "'FIRST_RES_IN_SEQ'", 
                     "'EXP_PEAK_PICK_TBL'", "<INVALID>", "'RES_TYPE'", "'SPIN_SYSTEM_ID'", 
                     "'HETEROGENEITY'", "'END_RES_DEF'", "'('", "')'", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "'Label'", "'Exp Par Fl'", "'Peak-Pick Fl'", 
                     "'#-Cross-Ref'" ]

    symbolicNames = [ "<INVALID>", "Shift_fl_frmt", "Res_siad", "First_res_in_seq", 
                      "Exp_peak_pick_tbl", "Res_ID", "Res_type", "Spin_system_ID", 
                      "Heterogeneity", "End_res_def", "L_paren", "R_paren", 
                      "Integer", "Float", "SHARP_COMMENT", "EXCLM_COMMENT", 
                      "Simple_name", "SPACE", "RETURN", "SECTION_COMMENT", 
                      "LINE_COMMENT", "Res_ID_", "Label", "Exp_par_fl", 
                      "Peak_pick_fl", "Cross_ref", "Simple_name_ET", "SPACE_ET", 
                      "RETURN_ET" ]

    RULE_pipp_cs = 0
    RULE_pipp_format = 1
    RULE_ext_peak_pick_tbl = 2
    RULE_ext_peak_pick_tbl_row = 3
    RULE_residue_list = 4
    RULE_shift_list = 5
    RULE_number = 6

    ruleNames =  [ "pipp_cs", "pipp_format", "ext_peak_pick_tbl", "ext_peak_pick_tbl_row", 
                   "residue_list", "shift_list", "number" ]

    EOF = Token.EOF
    Shift_fl_frmt=1
    Res_siad=2
    First_res_in_seq=3
    Exp_peak_pick_tbl=4
    Res_ID=5
    Res_type=6
    Spin_system_ID=7
    Heterogeneity=8
    End_res_def=9
    L_paren=10
    R_paren=11
    Integer=12
    Float=13
    SHARP_COMMENT=14
    EXCLM_COMMENT=15
    Simple_name=16
    SPACE=17
    RETURN=18
    SECTION_COMMENT=19
    LINE_COMMENT=20
    Res_ID_=21
    Label=22
    Exp_par_fl=23
    Peak_pick_fl=24
    Cross_ref=25
    Simple_name_ET=26
    SPACE_ET=27
    RETURN_ET=28

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.0")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class Pipp_csContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(PippCSParser.EOF, 0)

        def RETURN(self, i:int=None):
            if i is None:
                return self.getTokens(PippCSParser.RETURN)
            else:
                return self.getToken(PippCSParser.RETURN, i)

        def pipp_format(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PippCSParser.Pipp_formatContext)
            else:
                return self.getTypedRuleContext(PippCSParser.Pipp_formatContext,i)


        def getRuleIndex(self):
            return PippCSParser.RULE_pipp_cs

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPipp_cs" ):
                listener.enterPipp_cs(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPipp_cs" ):
                listener.exitPipp_cs(self)




    def pipp_cs(self):

        localctx = PippCSParser.Pipp_csContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_pipp_cs)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 15
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,0,self._ctx)
            if la_ == 1:
                self.state = 14
                self.match(PippCSParser.RETURN)


            self.state = 21
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==1 or _la==18:
                self.state = 19
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [1]:
                    self.state = 17
                    self.pipp_format()
                    pass
                elif token in [18]:
                    self.state = 18
                    self.match(PippCSParser.RETURN)
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 23
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 24
            self.match(PippCSParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Pipp_formatContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Shift_fl_frmt(self):
            return self.getToken(PippCSParser.Shift_fl_frmt, 0)

        def Res_siad(self):
            return self.getToken(PippCSParser.Res_siad, 0)

        def RETURN(self, i:int=None):
            if i is None:
                return self.getTokens(PippCSParser.RETURN)
            else:
                return self.getToken(PippCSParser.RETURN, i)

        def First_res_in_seq(self):
            return self.getToken(PippCSParser.First_res_in_seq, 0)

        def Integer(self):
            return self.getToken(PippCSParser.Integer, 0)

        def ext_peak_pick_tbl(self):
            return self.getTypedRuleContext(PippCSParser.Ext_peak_pick_tblContext,0)


        def residue_list(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PippCSParser.Residue_listContext)
            else:
                return self.getTypedRuleContext(PippCSParser.Residue_listContext,i)


        def getRuleIndex(self):
            return PippCSParser.RULE_pipp_format

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPipp_format" ):
                listener.enterPipp_format(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPipp_format" ):
                listener.exitPipp_format(self)




    def pipp_format(self):

        localctx = PippCSParser.Pipp_formatContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_pipp_format)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 26
            self.match(PippCSParser.Shift_fl_frmt)
            self.state = 27
            self.match(PippCSParser.Res_siad)
            self.state = 28
            self.match(PippCSParser.RETURN)
            self.state = 29
            self.match(PippCSParser.First_res_in_seq)
            self.state = 30
            self.match(PippCSParser.Integer)
            self.state = 31
            self.match(PippCSParser.RETURN)
            self.state = 33
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==4:
                self.state = 32
                self.ext_peak_pick_tbl()


            self.state = 36 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 35
                self.residue_list()
                self.state = 38 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==5 or _la==21):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Ext_peak_pick_tblContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Exp_peak_pick_tbl(self):
            return self.getToken(PippCSParser.Exp_peak_pick_tbl, 0)

        def RETURN_ET(self, i:int=None):
            if i is None:
                return self.getTokens(PippCSParser.RETURN_ET)
            else:
                return self.getToken(PippCSParser.RETURN_ET, i)

        def Label(self):
            return self.getToken(PippCSParser.Label, 0)

        def Exp_par_fl(self):
            return self.getToken(PippCSParser.Exp_par_fl, 0)

        def Peak_pick_fl(self):
            return self.getToken(PippCSParser.Peak_pick_fl, 0)

        def Cross_ref(self):
            return self.getToken(PippCSParser.Cross_ref, 0)

        def ext_peak_pick_tbl_row(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PippCSParser.Ext_peak_pick_tbl_rowContext)
            else:
                return self.getTypedRuleContext(PippCSParser.Ext_peak_pick_tbl_rowContext,i)


        def getRuleIndex(self):
            return PippCSParser.RULE_ext_peak_pick_tbl

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExt_peak_pick_tbl" ):
                listener.enterExt_peak_pick_tbl(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExt_peak_pick_tbl" ):
                listener.exitExt_peak_pick_tbl(self)




    def ext_peak_pick_tbl(self):

        localctx = PippCSParser.Ext_peak_pick_tblContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_ext_peak_pick_tbl)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 40
            self.match(PippCSParser.Exp_peak_pick_tbl)
            self.state = 41
            self.match(PippCSParser.RETURN_ET)
            self.state = 42
            self.match(PippCSParser.Label)
            self.state = 43
            self.match(PippCSParser.Exp_par_fl)
            self.state = 44
            self.match(PippCSParser.Peak_pick_fl)
            self.state = 45
            self.match(PippCSParser.Cross_ref)
            self.state = 46
            self.match(PippCSParser.RETURN_ET)
            self.state = 48 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 47
                self.ext_peak_pick_tbl_row()
                self.state = 50 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==26):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Ext_peak_pick_tbl_rowContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Simple_name_ET(self, i:int=None):
            if i is None:
                return self.getTokens(PippCSParser.Simple_name_ET)
            else:
                return self.getToken(PippCSParser.Simple_name_ET, i)

        def RETURN_ET(self):
            return self.getToken(PippCSParser.RETURN_ET, 0)

        def getRuleIndex(self):
            return PippCSParser.RULE_ext_peak_pick_tbl_row

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExt_peak_pick_tbl_row" ):
                listener.enterExt_peak_pick_tbl_row(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExt_peak_pick_tbl_row" ):
                listener.exitExt_peak_pick_tbl_row(self)




    def ext_peak_pick_tbl_row(self):

        localctx = PippCSParser.Ext_peak_pick_tbl_rowContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_ext_peak_pick_tbl_row)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 52
            self.match(PippCSParser.Simple_name_ET)
            self.state = 53
            self.match(PippCSParser.Simple_name_ET)
            self.state = 54
            self.match(PippCSParser.Simple_name_ET)
            self.state = 55
            self.match(PippCSParser.Simple_name_ET)
            self.state = 56
            self.match(PippCSParser.RETURN_ET)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Residue_listContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Integer(self, i:int=None):
            if i is None:
                return self.getTokens(PippCSParser.Integer)
            else:
                return self.getToken(PippCSParser.Integer, i)

        def RETURN(self, i:int=None):
            if i is None:
                return self.getTokens(PippCSParser.RETURN)
            else:
                return self.getToken(PippCSParser.RETURN, i)

        def Res_type(self):
            return self.getToken(PippCSParser.Res_type, 0)

        def Simple_name(self):
            return self.getToken(PippCSParser.Simple_name, 0)

        def Spin_system_ID(self):
            return self.getToken(PippCSParser.Spin_system_ID, 0)

        def Heterogeneity(self):
            return self.getToken(PippCSParser.Heterogeneity, 0)

        def End_res_def(self):
            return self.getToken(PippCSParser.End_res_def, 0)

        def Res_ID(self):
            return self.getToken(PippCSParser.Res_ID, 0)

        def Res_ID_(self):
            return self.getToken(PippCSParser.Res_ID_, 0)

        def EOF(self):
            return self.getToken(PippCSParser.EOF, 0)

        def shift_list(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PippCSParser.Shift_listContext)
            else:
                return self.getTypedRuleContext(PippCSParser.Shift_listContext,i)


        def getRuleIndex(self):
            return PippCSParser.RULE_residue_list

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterResidue_list" ):
                listener.enterResidue_list(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitResidue_list" ):
                listener.exitResidue_list(self)




    def residue_list(self):

        localctx = PippCSParser.Residue_listContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_residue_list)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 58
            _la = self._input.LA(1)
            if not(_la==5 or _la==21):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 59
            self.match(PippCSParser.Integer)
            self.state = 60
            self.match(PippCSParser.RETURN)
            self.state = 61
            self.match(PippCSParser.Res_type)
            self.state = 62
            self.match(PippCSParser.Simple_name)
            self.state = 63
            self.match(PippCSParser.RETURN)
            self.state = 64
            self.match(PippCSParser.Spin_system_ID)
            self.state = 65
            self.match(PippCSParser.Integer)
            self.state = 66
            self.match(PippCSParser.RETURN)
            self.state = 67
            self.match(PippCSParser.Heterogeneity)
            self.state = 68
            self.match(PippCSParser.Integer)
            self.state = 69
            self.match(PippCSParser.RETURN)
            self.state = 71 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 70
                self.shift_list()
                self.state = 73 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==16):
                    break

            self.state = 75
            self.match(PippCSParser.End_res_def)
            self.state = 76
            _la = self._input.LA(1)
            if not(_la==-1 or _la==18):
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


    class Shift_listContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Simple_name(self, i:int=None):
            if i is None:
                return self.getTokens(PippCSParser.Simple_name)
            else:
                return self.getToken(PippCSParser.Simple_name, i)

        def number(self):
            return self.getTypedRuleContext(PippCSParser.NumberContext,0)


        def L_paren(self):
            return self.getToken(PippCSParser.L_paren, 0)

        def R_paren(self):
            return self.getToken(PippCSParser.R_paren, 0)

        def RETURN(self):
            return self.getToken(PippCSParser.RETURN, 0)

        def getRuleIndex(self):
            return PippCSParser.RULE_shift_list

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterShift_list" ):
                listener.enterShift_list(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitShift_list" ):
                listener.exitShift_list(self)




    def shift_list(self):

        localctx = PippCSParser.Shift_listContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_shift_list)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 78
            self.match(PippCSParser.Simple_name)
            self.state = 79
            self.number()
            self.state = 80
            self.match(PippCSParser.L_paren)
            self.state = 82 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 81
                self.match(PippCSParser.Simple_name)
                self.state = 84 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==16):
                    break

            self.state = 86
            self.match(PippCSParser.R_paren)
            self.state = 87
            self.match(PippCSParser.RETURN)
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
            return self.getToken(PippCSParser.Float, 0)

        def Integer(self):
            return self.getToken(PippCSParser.Integer, 0)

        def Simple_name(self):
            return self.getToken(PippCSParser.Simple_name, 0)

        def getRuleIndex(self):
            return PippCSParser.RULE_number

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNumber" ):
                listener.enterNumber(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNumber" ):
                listener.exitNumber(self)




    def number(self):

        localctx = PippCSParser.NumberContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_number)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 89
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 77824) != 0)):
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





