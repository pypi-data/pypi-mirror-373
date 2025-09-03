# Generated from NmrStar2CSParser.g4 by ANTLR 4.13.0
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
        4,1,23,84,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,1,0,3,0,18,8,0,1,0,1,0,1,0,5,0,23,8,0,10,0,12,0,26,9,0,
        1,0,1,0,1,1,1,1,1,1,4,1,33,8,1,11,1,12,1,34,1,1,4,1,38,8,1,11,1,
        12,1,39,1,1,1,1,3,1,44,8,1,1,2,1,2,1,2,1,3,4,3,50,8,3,11,3,12,3,
        51,1,3,1,3,1,4,1,4,1,4,4,4,59,8,4,11,4,12,4,60,1,4,4,4,64,8,4,11,
        4,12,4,65,1,4,1,4,3,4,70,8,4,1,5,1,5,1,5,1,6,4,6,76,8,6,11,6,12,
        6,77,1,6,1,6,1,7,1,7,1,7,0,0,8,0,2,4,6,8,10,12,14,0,4,1,1,21,21,
        1,0,3,4,1,0,3,11,2,0,12,13,17,19,87,0,17,1,0,0,0,2,29,1,0,0,0,4,
        45,1,0,0,0,6,49,1,0,0,0,8,55,1,0,0,0,10,71,1,0,0,0,12,75,1,0,0,0,
        14,81,1,0,0,0,16,18,5,21,0,0,17,16,1,0,0,0,17,18,1,0,0,0,18,24,1,
        0,0,0,19,23,3,2,1,0,20,23,3,8,4,0,21,23,5,21,0,0,22,19,1,0,0,0,22,
        20,1,0,0,0,22,21,1,0,0,0,23,26,1,0,0,0,24,22,1,0,0,0,24,25,1,0,0,
        0,25,27,1,0,0,0,26,24,1,0,0,0,27,28,5,0,0,1,28,1,1,0,0,0,29,30,5,
        1,0,0,30,32,5,21,0,0,31,33,3,4,2,0,32,31,1,0,0,0,33,34,1,0,0,0,34,
        32,1,0,0,0,34,35,1,0,0,0,35,37,1,0,0,0,36,38,3,6,3,0,37,36,1,0,0,
        0,38,39,1,0,0,0,39,37,1,0,0,0,39,40,1,0,0,0,40,41,1,0,0,0,41,43,
        5,2,0,0,42,44,7,0,0,0,43,42,1,0,0,0,43,44,1,0,0,0,44,3,1,0,0,0,45,
        46,7,1,0,0,46,47,5,21,0,0,47,5,1,0,0,0,48,50,3,14,7,0,49,48,1,0,
        0,0,50,51,1,0,0,0,51,49,1,0,0,0,51,52,1,0,0,0,52,53,1,0,0,0,53,54,
        5,21,0,0,54,7,1,0,0,0,55,56,5,1,0,0,56,58,5,21,0,0,57,59,3,10,5,
        0,58,57,1,0,0,0,59,60,1,0,0,0,60,58,1,0,0,0,60,61,1,0,0,0,61,63,
        1,0,0,0,62,64,3,12,6,0,63,62,1,0,0,0,64,65,1,0,0,0,65,63,1,0,0,0,
        65,66,1,0,0,0,66,67,1,0,0,0,67,69,5,2,0,0,68,70,7,0,0,0,69,68,1,
        0,0,0,69,70,1,0,0,0,70,9,1,0,0,0,71,72,7,2,0,0,72,73,5,21,0,0,73,
        11,1,0,0,0,74,76,3,14,7,0,75,74,1,0,0,0,76,77,1,0,0,0,77,75,1,0,
        0,0,77,78,1,0,0,0,78,79,1,0,0,0,79,80,5,21,0,0,80,13,1,0,0,0,81,
        82,7,3,0,0,82,15,1,0,0,0,11,17,22,24,34,39,43,51,60,65,69,77
    ]

class NmrStar2CSParser ( Parser ):

    grammarFileName = "NmrStar2CSParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'loop_'", "'stop_'", "'_Residue_seq_code'", 
                     "'_Residue_label'", "'_Atom_shift_assign_ID'", "'_Residue_author_seq_code'", 
                     "'_Atom_name'", "'_Atom_type'", "'_Chem_shift_value'", 
                     "'_Chem_shift_value_error'", "'_Chem_shift_ambiguity_code'" ]

    symbolicNames = [ "<INVALID>", "Loop", "Stop", "Residue_seq_code", "Residue_label", 
                      "Atom_shift_assign_ID", "Residue_author_seq_code", 
                      "Atom_name", "Atom_type", "Chem_shift_value", "Chem_shift_value_error", 
                      "Chem_shift_ambiguity_code", "Integer", "Float", "SHARP_COMMENT", 
                      "EXCLM_COMMENT", "SMCLN_COMMENT", "Simple_name", "Double_quote_string", 
                      "Single_quote_string", "SPACE", "RETURN", "SECTION_COMMENT", 
                      "LINE_COMMENT" ]

    RULE_nmrstar2_cs = 0
    RULE_seq_loop = 1
    RULE_seq_tags = 2
    RULE_seq_data = 3
    RULE_cs_loop = 4
    RULE_cs_tags = 5
    RULE_cs_data = 6
    RULE_any = 7

    ruleNames =  [ "nmrstar2_cs", "seq_loop", "seq_tags", "seq_data", "cs_loop", 
                   "cs_tags", "cs_data", "any" ]

    EOF = Token.EOF
    Loop=1
    Stop=2
    Residue_seq_code=3
    Residue_label=4
    Atom_shift_assign_ID=5
    Residue_author_seq_code=6
    Atom_name=7
    Atom_type=8
    Chem_shift_value=9
    Chem_shift_value_error=10
    Chem_shift_ambiguity_code=11
    Integer=12
    Float=13
    SHARP_COMMENT=14
    EXCLM_COMMENT=15
    SMCLN_COMMENT=16
    Simple_name=17
    Double_quote_string=18
    Single_quote_string=19
    SPACE=20
    RETURN=21
    SECTION_COMMENT=22
    LINE_COMMENT=23

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.0")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class Nmrstar2_csContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(NmrStar2CSParser.EOF, 0)

        def RETURN(self, i:int=None):
            if i is None:
                return self.getTokens(NmrStar2CSParser.RETURN)
            else:
                return self.getToken(NmrStar2CSParser.RETURN, i)

        def seq_loop(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NmrStar2CSParser.Seq_loopContext)
            else:
                return self.getTypedRuleContext(NmrStar2CSParser.Seq_loopContext,i)


        def cs_loop(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NmrStar2CSParser.Cs_loopContext)
            else:
                return self.getTypedRuleContext(NmrStar2CSParser.Cs_loopContext,i)


        def getRuleIndex(self):
            return NmrStar2CSParser.RULE_nmrstar2_cs

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNmrstar2_cs" ):
                listener.enterNmrstar2_cs(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNmrstar2_cs" ):
                listener.exitNmrstar2_cs(self)




    def nmrstar2_cs(self):

        localctx = NmrStar2CSParser.Nmrstar2_csContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_nmrstar2_cs)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 17
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,0,self._ctx)
            if la_ == 1:
                self.state = 16
                self.match(NmrStar2CSParser.RETURN)


            self.state = 24
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==1 or _la==21:
                self.state = 22
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,1,self._ctx)
                if la_ == 1:
                    self.state = 19
                    self.seq_loop()
                    pass

                elif la_ == 2:
                    self.state = 20
                    self.cs_loop()
                    pass

                elif la_ == 3:
                    self.state = 21
                    self.match(NmrStar2CSParser.RETURN)
                    pass


                self.state = 26
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 27
            self.match(NmrStar2CSParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Seq_loopContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Loop(self):
            return self.getToken(NmrStar2CSParser.Loop, 0)

        def RETURN(self, i:int=None):
            if i is None:
                return self.getTokens(NmrStar2CSParser.RETURN)
            else:
                return self.getToken(NmrStar2CSParser.RETURN, i)

        def Stop(self):
            return self.getToken(NmrStar2CSParser.Stop, 0)

        def seq_tags(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NmrStar2CSParser.Seq_tagsContext)
            else:
                return self.getTypedRuleContext(NmrStar2CSParser.Seq_tagsContext,i)


        def seq_data(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NmrStar2CSParser.Seq_dataContext)
            else:
                return self.getTypedRuleContext(NmrStar2CSParser.Seq_dataContext,i)


        def EOF(self):
            return self.getToken(NmrStar2CSParser.EOF, 0)

        def getRuleIndex(self):
            return NmrStar2CSParser.RULE_seq_loop

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSeq_loop" ):
                listener.enterSeq_loop(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSeq_loop" ):
                listener.exitSeq_loop(self)




    def seq_loop(self):

        localctx = NmrStar2CSParser.Seq_loopContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_seq_loop)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 29
            self.match(NmrStar2CSParser.Loop)
            self.state = 30
            self.match(NmrStar2CSParser.RETURN)
            self.state = 32 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 31
                self.seq_tags()
                self.state = 34 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==3 or _la==4):
                    break

            self.state = 37 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 36
                self.seq_data()
                self.state = 39 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & 929792) != 0)):
                    break

            self.state = 41
            self.match(NmrStar2CSParser.Stop)
            self.state = 43
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,5,self._ctx)
            if la_ == 1:
                self.state = 42
                _la = self._input.LA(1)
                if not(_la==-1 or _la==21):
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


    class Seq_tagsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def RETURN(self):
            return self.getToken(NmrStar2CSParser.RETURN, 0)

        def Residue_seq_code(self):
            return self.getToken(NmrStar2CSParser.Residue_seq_code, 0)

        def Residue_label(self):
            return self.getToken(NmrStar2CSParser.Residue_label, 0)

        def getRuleIndex(self):
            return NmrStar2CSParser.RULE_seq_tags

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSeq_tags" ):
                listener.enterSeq_tags(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSeq_tags" ):
                listener.exitSeq_tags(self)




    def seq_tags(self):

        localctx = NmrStar2CSParser.Seq_tagsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_seq_tags)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 45
            _la = self._input.LA(1)
            if not(_la==3 or _la==4):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 46
            self.match(NmrStar2CSParser.RETURN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Seq_dataContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def RETURN(self):
            return self.getToken(NmrStar2CSParser.RETURN, 0)

        def any_(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NmrStar2CSParser.AnyContext)
            else:
                return self.getTypedRuleContext(NmrStar2CSParser.AnyContext,i)


        def getRuleIndex(self):
            return NmrStar2CSParser.RULE_seq_data

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSeq_data" ):
                listener.enterSeq_data(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSeq_data" ):
                listener.exitSeq_data(self)




    def seq_data(self):

        localctx = NmrStar2CSParser.Seq_dataContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_seq_data)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 49 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 48
                self.any_()
                self.state = 51 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & 929792) != 0)):
                    break

            self.state = 53
            self.match(NmrStar2CSParser.RETURN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Cs_loopContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Loop(self):
            return self.getToken(NmrStar2CSParser.Loop, 0)

        def RETURN(self, i:int=None):
            if i is None:
                return self.getTokens(NmrStar2CSParser.RETURN)
            else:
                return self.getToken(NmrStar2CSParser.RETURN, i)

        def Stop(self):
            return self.getToken(NmrStar2CSParser.Stop, 0)

        def cs_tags(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NmrStar2CSParser.Cs_tagsContext)
            else:
                return self.getTypedRuleContext(NmrStar2CSParser.Cs_tagsContext,i)


        def cs_data(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NmrStar2CSParser.Cs_dataContext)
            else:
                return self.getTypedRuleContext(NmrStar2CSParser.Cs_dataContext,i)


        def EOF(self):
            return self.getToken(NmrStar2CSParser.EOF, 0)

        def getRuleIndex(self):
            return NmrStar2CSParser.RULE_cs_loop

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCs_loop" ):
                listener.enterCs_loop(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCs_loop" ):
                listener.exitCs_loop(self)




    def cs_loop(self):

        localctx = NmrStar2CSParser.Cs_loopContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_cs_loop)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 55
            self.match(NmrStar2CSParser.Loop)
            self.state = 56
            self.match(NmrStar2CSParser.RETURN)
            self.state = 58 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 57
                self.cs_tags()
                self.state = 60 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & 4088) != 0)):
                    break

            self.state = 63 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 62
                self.cs_data()
                self.state = 65 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & 929792) != 0)):
                    break

            self.state = 67
            self.match(NmrStar2CSParser.Stop)
            self.state = 69
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,9,self._ctx)
            if la_ == 1:
                self.state = 68
                _la = self._input.LA(1)
                if not(_la==-1 or _la==21):
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


    class Cs_tagsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def RETURN(self):
            return self.getToken(NmrStar2CSParser.RETURN, 0)

        def Atom_shift_assign_ID(self):
            return self.getToken(NmrStar2CSParser.Atom_shift_assign_ID, 0)

        def Residue_author_seq_code(self):
            return self.getToken(NmrStar2CSParser.Residue_author_seq_code, 0)

        def Residue_seq_code(self):
            return self.getToken(NmrStar2CSParser.Residue_seq_code, 0)

        def Residue_label(self):
            return self.getToken(NmrStar2CSParser.Residue_label, 0)

        def Atom_name(self):
            return self.getToken(NmrStar2CSParser.Atom_name, 0)

        def Atom_type(self):
            return self.getToken(NmrStar2CSParser.Atom_type, 0)

        def Chem_shift_value(self):
            return self.getToken(NmrStar2CSParser.Chem_shift_value, 0)

        def Chem_shift_value_error(self):
            return self.getToken(NmrStar2CSParser.Chem_shift_value_error, 0)

        def Chem_shift_ambiguity_code(self):
            return self.getToken(NmrStar2CSParser.Chem_shift_ambiguity_code, 0)

        def getRuleIndex(self):
            return NmrStar2CSParser.RULE_cs_tags

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCs_tags" ):
                listener.enterCs_tags(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCs_tags" ):
                listener.exitCs_tags(self)




    def cs_tags(self):

        localctx = NmrStar2CSParser.Cs_tagsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_cs_tags)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 71
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 4088) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 72
            self.match(NmrStar2CSParser.RETURN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Cs_dataContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def RETURN(self):
            return self.getToken(NmrStar2CSParser.RETURN, 0)

        def any_(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NmrStar2CSParser.AnyContext)
            else:
                return self.getTypedRuleContext(NmrStar2CSParser.AnyContext,i)


        def getRuleIndex(self):
            return NmrStar2CSParser.RULE_cs_data

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCs_data" ):
                listener.enterCs_data(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCs_data" ):
                listener.exitCs_data(self)




    def cs_data(self):

        localctx = NmrStar2CSParser.Cs_dataContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_cs_data)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 75 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 74
                self.any_()
                self.state = 77 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & 929792) != 0)):
                    break

            self.state = 79
            self.match(NmrStar2CSParser.RETURN)
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
            return self.getToken(NmrStar2CSParser.Float, 0)

        def Integer(self):
            return self.getToken(NmrStar2CSParser.Integer, 0)

        def Simple_name(self):
            return self.getToken(NmrStar2CSParser.Simple_name, 0)

        def Double_quote_string(self):
            return self.getToken(NmrStar2CSParser.Double_quote_string, 0)

        def Single_quote_string(self):
            return self.getToken(NmrStar2CSParser.Single_quote_string, 0)

        def getRuleIndex(self):
            return NmrStar2CSParser.RULE_any

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAny" ):
                listener.enterAny(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAny" ):
                listener.exitAny(self)




    def any_(self):

        localctx = NmrStar2CSParser.AnyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_any)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 81
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 929792) != 0)):
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





