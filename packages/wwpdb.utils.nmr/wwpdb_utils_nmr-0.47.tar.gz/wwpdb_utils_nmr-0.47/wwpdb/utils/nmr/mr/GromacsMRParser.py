# Generated from GromacsMRParser.g4 by ANTLR 4.13.0
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
        4,1,19,158,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,5,0,38,8,0,10,0,12,0,41,9,0,
        1,0,1,0,1,1,1,1,1,1,1,1,4,1,49,8,1,11,1,12,1,50,1,2,1,2,1,2,1,2,
        1,2,1,2,1,2,1,2,1,2,1,2,3,2,63,8,2,1,3,1,3,1,3,1,3,4,3,69,8,3,11,
        3,12,3,70,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,3,4,82,8,4,1,5,1,5,
        1,5,1,5,4,5,88,8,5,11,5,12,5,89,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,
        1,6,1,6,3,6,102,8,6,1,7,1,7,1,7,1,7,4,7,108,8,7,11,7,12,7,109,1,
        8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,3,8,121,8,8,1,9,1,9,1,9,1,9,4,
        9,127,8,9,11,9,12,9,128,1,10,1,10,1,10,1,10,1,10,1,10,1,10,3,10,
        138,8,10,1,11,1,11,1,11,1,11,4,11,144,8,11,11,11,12,11,145,1,12,
        1,12,1,12,1,12,1,12,1,12,3,12,154,8,12,1,13,1,13,1,13,0,0,14,0,2,
        4,6,8,10,12,14,16,18,20,22,24,26,0,1,1,0,10,11,162,0,39,1,0,0,0,
        2,44,1,0,0,0,4,52,1,0,0,0,6,64,1,0,0,0,8,72,1,0,0,0,10,83,1,0,0,
        0,12,91,1,0,0,0,14,103,1,0,0,0,16,111,1,0,0,0,18,122,1,0,0,0,20,
        130,1,0,0,0,22,139,1,0,0,0,24,147,1,0,0,0,26,155,1,0,0,0,28,38,3,
        2,1,0,29,38,3,6,3,0,30,38,3,10,5,0,31,38,3,14,7,0,32,38,3,18,9,0,
        33,38,3,22,11,0,34,35,5,1,0,0,35,36,5,9,0,0,36,38,5,2,0,0,37,28,
        1,0,0,0,37,29,1,0,0,0,37,30,1,0,0,0,37,31,1,0,0,0,37,32,1,0,0,0,
        37,33,1,0,0,0,37,34,1,0,0,0,38,41,1,0,0,0,39,37,1,0,0,0,39,40,1,
        0,0,0,40,42,1,0,0,0,41,39,1,0,0,0,42,43,5,0,0,1,43,1,1,0,0,0,44,
        45,5,1,0,0,45,46,5,3,0,0,46,48,5,2,0,0,47,49,3,4,2,0,48,47,1,0,0,
        0,49,50,1,0,0,0,50,48,1,0,0,0,50,51,1,0,0,0,51,3,1,0,0,0,52,53,5,
        10,0,0,53,54,5,10,0,0,54,55,5,10,0,0,55,56,5,10,0,0,56,57,5,10,0,
        0,57,58,3,26,13,0,58,59,3,26,13,0,59,60,3,26,13,0,60,62,3,26,13,
        0,61,63,5,15,0,0,62,61,1,0,0,0,62,63,1,0,0,0,63,5,1,0,0,0,64,65,
        5,1,0,0,65,66,5,4,0,0,66,68,5,2,0,0,67,69,3,8,4,0,68,67,1,0,0,0,
        69,70,1,0,0,0,70,68,1,0,0,0,70,71,1,0,0,0,71,7,1,0,0,0,72,73,5,10,
        0,0,73,74,5,10,0,0,74,75,5,10,0,0,75,76,5,10,0,0,76,77,5,10,0,0,
        77,78,3,26,13,0,78,79,3,26,13,0,79,81,3,26,13,0,80,82,5,15,0,0,81,
        80,1,0,0,0,81,82,1,0,0,0,82,9,1,0,0,0,83,84,5,1,0,0,84,85,5,5,0,
        0,85,87,5,2,0,0,86,88,3,12,6,0,87,86,1,0,0,0,88,89,1,0,0,0,89,87,
        1,0,0,0,89,90,1,0,0,0,90,11,1,0,0,0,91,92,5,10,0,0,92,93,5,10,0,
        0,93,94,5,10,0,0,94,95,5,10,0,0,95,96,5,10,0,0,96,97,3,26,13,0,97,
        98,3,26,13,0,98,99,3,26,13,0,99,101,3,26,13,0,100,102,5,15,0,0,101,
        100,1,0,0,0,101,102,1,0,0,0,102,13,1,0,0,0,103,104,5,1,0,0,104,105,
        5,6,0,0,105,107,5,2,0,0,106,108,3,16,8,0,107,106,1,0,0,0,108,109,
        1,0,0,0,109,107,1,0,0,0,109,110,1,0,0,0,110,15,1,0,0,0,111,112,5,
        10,0,0,112,113,5,10,0,0,113,114,5,10,0,0,114,115,5,10,0,0,115,116,
        5,10,0,0,116,117,3,26,13,0,117,118,3,26,13,0,118,120,5,10,0,0,119,
        121,5,15,0,0,120,119,1,0,0,0,120,121,1,0,0,0,121,17,1,0,0,0,122,
        123,5,1,0,0,123,124,5,7,0,0,124,126,5,2,0,0,125,127,3,20,10,0,126,
        125,1,0,0,0,127,128,1,0,0,0,128,126,1,0,0,0,128,129,1,0,0,0,129,
        19,1,0,0,0,130,131,5,10,0,0,131,132,5,10,0,0,132,133,5,10,0,0,133,
        134,3,26,13,0,134,135,3,26,13,0,135,137,5,10,0,0,136,138,5,15,0,
        0,137,136,1,0,0,0,137,138,1,0,0,0,138,21,1,0,0,0,139,140,5,1,0,0,
        140,141,5,8,0,0,141,143,5,2,0,0,142,144,3,24,12,0,143,142,1,0,0,
        0,144,145,1,0,0,0,145,143,1,0,0,0,145,146,1,0,0,0,146,23,1,0,0,0,
        147,148,5,10,0,0,148,149,5,10,0,0,149,150,3,26,13,0,150,151,3,26,
        13,0,151,153,3,26,13,0,152,154,5,15,0,0,153,152,1,0,0,0,153,154,
        1,0,0,0,154,25,1,0,0,0,155,156,7,0,0,0,156,27,1,0,0,0,14,37,39,50,
        62,70,81,89,101,109,120,128,137,145,153
    ]

class GromacsMRParser ( Parser ):

    grammarFileName = "GromacsMRParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'['", "']'", "'distance_restraints'", 
                     "'dihedral_restraints'", "'orientation_restraints'", 
                     "'angle_restraints'", "'angle_restraints_z'", "'position_restraints'" ]

    symbolicNames = [ "<INVALID>", "L_brkt", "R_brkt", "Distance_restraints", 
                      "Dihedral_restraints", "Orientation_restraints", "Angle_restraints", 
                      "Angle_restraints_z", "Position_restraints", "Intermolecular_interactions", 
                      "Integer", "Float", "SHARP_COMMENT", "EXCLM_COMMENT", 
                      "SMCLN_COMMENT", "Simple_name", "SPACE", "ENCLOSE_COMMENT", 
                      "SECTION_COMMENT", "LINE_COMMENT" ]

    RULE_gromacs_mr = 0
    RULE_distance_restraints = 1
    RULE_distance_restraint = 2
    RULE_dihedral_restraints = 3
    RULE_dihedral_restraint = 4
    RULE_orientation_restraints = 5
    RULE_orientation_restraint = 6
    RULE_angle_restraints = 7
    RULE_angle_restraint = 8
    RULE_angle_restraints_z = 9
    RULE_angle_restraint_z = 10
    RULE_position_restraints = 11
    RULE_position_restraint = 12
    RULE_number = 13

    ruleNames =  [ "gromacs_mr", "distance_restraints", "distance_restraint", 
                   "dihedral_restraints", "dihedral_restraint", "orientation_restraints", 
                   "orientation_restraint", "angle_restraints", "angle_restraint", 
                   "angle_restraints_z", "angle_restraint_z", "position_restraints", 
                   "position_restraint", "number" ]

    EOF = Token.EOF
    L_brkt=1
    R_brkt=2
    Distance_restraints=3
    Dihedral_restraints=4
    Orientation_restraints=5
    Angle_restraints=6
    Angle_restraints_z=7
    Position_restraints=8
    Intermolecular_interactions=9
    Integer=10
    Float=11
    SHARP_COMMENT=12
    EXCLM_COMMENT=13
    SMCLN_COMMENT=14
    Simple_name=15
    SPACE=16
    ENCLOSE_COMMENT=17
    SECTION_COMMENT=18
    LINE_COMMENT=19

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.0")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class Gromacs_mrContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(GromacsMRParser.EOF, 0)

        def distance_restraints(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(GromacsMRParser.Distance_restraintsContext)
            else:
                return self.getTypedRuleContext(GromacsMRParser.Distance_restraintsContext,i)


        def dihedral_restraints(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(GromacsMRParser.Dihedral_restraintsContext)
            else:
                return self.getTypedRuleContext(GromacsMRParser.Dihedral_restraintsContext,i)


        def orientation_restraints(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(GromacsMRParser.Orientation_restraintsContext)
            else:
                return self.getTypedRuleContext(GromacsMRParser.Orientation_restraintsContext,i)


        def angle_restraints(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(GromacsMRParser.Angle_restraintsContext)
            else:
                return self.getTypedRuleContext(GromacsMRParser.Angle_restraintsContext,i)


        def angle_restraints_z(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(GromacsMRParser.Angle_restraints_zContext)
            else:
                return self.getTypedRuleContext(GromacsMRParser.Angle_restraints_zContext,i)


        def position_restraints(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(GromacsMRParser.Position_restraintsContext)
            else:
                return self.getTypedRuleContext(GromacsMRParser.Position_restraintsContext,i)


        def L_brkt(self, i:int=None):
            if i is None:
                return self.getTokens(GromacsMRParser.L_brkt)
            else:
                return self.getToken(GromacsMRParser.L_brkt, i)

        def Intermolecular_interactions(self, i:int=None):
            if i is None:
                return self.getTokens(GromacsMRParser.Intermolecular_interactions)
            else:
                return self.getToken(GromacsMRParser.Intermolecular_interactions, i)

        def R_brkt(self, i:int=None):
            if i is None:
                return self.getTokens(GromacsMRParser.R_brkt)
            else:
                return self.getToken(GromacsMRParser.R_brkt, i)

        def getRuleIndex(self):
            return GromacsMRParser.RULE_gromacs_mr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterGromacs_mr" ):
                listener.enterGromacs_mr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitGromacs_mr" ):
                listener.exitGromacs_mr(self)




    def gromacs_mr(self):

        localctx = GromacsMRParser.Gromacs_mrContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_gromacs_mr)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 39
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==1:
                self.state = 37
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,0,self._ctx)
                if la_ == 1:
                    self.state = 28
                    self.distance_restraints()
                    pass

                elif la_ == 2:
                    self.state = 29
                    self.dihedral_restraints()
                    pass

                elif la_ == 3:
                    self.state = 30
                    self.orientation_restraints()
                    pass

                elif la_ == 4:
                    self.state = 31
                    self.angle_restraints()
                    pass

                elif la_ == 5:
                    self.state = 32
                    self.angle_restraints_z()
                    pass

                elif la_ == 6:
                    self.state = 33
                    self.position_restraints()
                    pass

                elif la_ == 7:
                    self.state = 34
                    self.match(GromacsMRParser.L_brkt)
                    self.state = 35
                    self.match(GromacsMRParser.Intermolecular_interactions)
                    self.state = 36
                    self.match(GromacsMRParser.R_brkt)
                    pass


                self.state = 41
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 42
            self.match(GromacsMRParser.EOF)
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

        def L_brkt(self):
            return self.getToken(GromacsMRParser.L_brkt, 0)

        def Distance_restraints(self):
            return self.getToken(GromacsMRParser.Distance_restraints, 0)

        def R_brkt(self):
            return self.getToken(GromacsMRParser.R_brkt, 0)

        def distance_restraint(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(GromacsMRParser.Distance_restraintContext)
            else:
                return self.getTypedRuleContext(GromacsMRParser.Distance_restraintContext,i)


        def getRuleIndex(self):
            return GromacsMRParser.RULE_distance_restraints

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDistance_restraints" ):
                listener.enterDistance_restraints(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDistance_restraints" ):
                listener.exitDistance_restraints(self)




    def distance_restraints(self):

        localctx = GromacsMRParser.Distance_restraintsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_distance_restraints)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 44
            self.match(GromacsMRParser.L_brkt)
            self.state = 45
            self.match(GromacsMRParser.Distance_restraints)
            self.state = 46
            self.match(GromacsMRParser.R_brkt)
            self.state = 48 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 47
                self.distance_restraint()
                self.state = 50 
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


    class Distance_restraintContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Integer(self, i:int=None):
            if i is None:
                return self.getTokens(GromacsMRParser.Integer)
            else:
                return self.getToken(GromacsMRParser.Integer, i)

        def number(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(GromacsMRParser.NumberContext)
            else:
                return self.getTypedRuleContext(GromacsMRParser.NumberContext,i)


        def Simple_name(self):
            return self.getToken(GromacsMRParser.Simple_name, 0)

        def getRuleIndex(self):
            return GromacsMRParser.RULE_distance_restraint

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDistance_restraint" ):
                listener.enterDistance_restraint(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDistance_restraint" ):
                listener.exitDistance_restraint(self)




    def distance_restraint(self):

        localctx = GromacsMRParser.Distance_restraintContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_distance_restraint)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 52
            self.match(GromacsMRParser.Integer)
            self.state = 53
            self.match(GromacsMRParser.Integer)
            self.state = 54
            self.match(GromacsMRParser.Integer)
            self.state = 55
            self.match(GromacsMRParser.Integer)
            self.state = 56
            self.match(GromacsMRParser.Integer)
            self.state = 57
            self.number()
            self.state = 58
            self.number()
            self.state = 59
            self.number()
            self.state = 60
            self.number()
            self.state = 62
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==15:
                self.state = 61
                self.match(GromacsMRParser.Simple_name)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Dihedral_restraintsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def L_brkt(self):
            return self.getToken(GromacsMRParser.L_brkt, 0)

        def Dihedral_restraints(self):
            return self.getToken(GromacsMRParser.Dihedral_restraints, 0)

        def R_brkt(self):
            return self.getToken(GromacsMRParser.R_brkt, 0)

        def dihedral_restraint(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(GromacsMRParser.Dihedral_restraintContext)
            else:
                return self.getTypedRuleContext(GromacsMRParser.Dihedral_restraintContext,i)


        def getRuleIndex(self):
            return GromacsMRParser.RULE_dihedral_restraints

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDihedral_restraints" ):
                listener.enterDihedral_restraints(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDihedral_restraints" ):
                listener.exitDihedral_restraints(self)




    def dihedral_restraints(self):

        localctx = GromacsMRParser.Dihedral_restraintsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_dihedral_restraints)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 64
            self.match(GromacsMRParser.L_brkt)
            self.state = 65
            self.match(GromacsMRParser.Dihedral_restraints)
            self.state = 66
            self.match(GromacsMRParser.R_brkt)
            self.state = 68 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 67
                self.dihedral_restraint()
                self.state = 70 
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


    class Dihedral_restraintContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Integer(self, i:int=None):
            if i is None:
                return self.getTokens(GromacsMRParser.Integer)
            else:
                return self.getToken(GromacsMRParser.Integer, i)

        def number(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(GromacsMRParser.NumberContext)
            else:
                return self.getTypedRuleContext(GromacsMRParser.NumberContext,i)


        def Simple_name(self):
            return self.getToken(GromacsMRParser.Simple_name, 0)

        def getRuleIndex(self):
            return GromacsMRParser.RULE_dihedral_restraint

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDihedral_restraint" ):
                listener.enterDihedral_restraint(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDihedral_restraint" ):
                listener.exitDihedral_restraint(self)




    def dihedral_restraint(self):

        localctx = GromacsMRParser.Dihedral_restraintContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_dihedral_restraint)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 72
            self.match(GromacsMRParser.Integer)
            self.state = 73
            self.match(GromacsMRParser.Integer)
            self.state = 74
            self.match(GromacsMRParser.Integer)
            self.state = 75
            self.match(GromacsMRParser.Integer)
            self.state = 76
            self.match(GromacsMRParser.Integer)
            self.state = 77
            self.number()
            self.state = 78
            self.number()
            self.state = 79
            self.number()
            self.state = 81
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==15:
                self.state = 80
                self.match(GromacsMRParser.Simple_name)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Orientation_restraintsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def L_brkt(self):
            return self.getToken(GromacsMRParser.L_brkt, 0)

        def Orientation_restraints(self):
            return self.getToken(GromacsMRParser.Orientation_restraints, 0)

        def R_brkt(self):
            return self.getToken(GromacsMRParser.R_brkt, 0)

        def orientation_restraint(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(GromacsMRParser.Orientation_restraintContext)
            else:
                return self.getTypedRuleContext(GromacsMRParser.Orientation_restraintContext,i)


        def getRuleIndex(self):
            return GromacsMRParser.RULE_orientation_restraints

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOrientation_restraints" ):
                listener.enterOrientation_restraints(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOrientation_restraints" ):
                listener.exitOrientation_restraints(self)




    def orientation_restraints(self):

        localctx = GromacsMRParser.Orientation_restraintsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_orientation_restraints)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 83
            self.match(GromacsMRParser.L_brkt)
            self.state = 84
            self.match(GromacsMRParser.Orientation_restraints)
            self.state = 85
            self.match(GromacsMRParser.R_brkt)
            self.state = 87 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 86
                self.orientation_restraint()
                self.state = 89 
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


    class Orientation_restraintContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Integer(self, i:int=None):
            if i is None:
                return self.getTokens(GromacsMRParser.Integer)
            else:
                return self.getToken(GromacsMRParser.Integer, i)

        def number(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(GromacsMRParser.NumberContext)
            else:
                return self.getTypedRuleContext(GromacsMRParser.NumberContext,i)


        def Simple_name(self):
            return self.getToken(GromacsMRParser.Simple_name, 0)

        def getRuleIndex(self):
            return GromacsMRParser.RULE_orientation_restraint

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOrientation_restraint" ):
                listener.enterOrientation_restraint(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOrientation_restraint" ):
                listener.exitOrientation_restraint(self)




    def orientation_restraint(self):

        localctx = GromacsMRParser.Orientation_restraintContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_orientation_restraint)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 91
            self.match(GromacsMRParser.Integer)
            self.state = 92
            self.match(GromacsMRParser.Integer)
            self.state = 93
            self.match(GromacsMRParser.Integer)
            self.state = 94
            self.match(GromacsMRParser.Integer)
            self.state = 95
            self.match(GromacsMRParser.Integer)
            self.state = 96
            self.number()
            self.state = 97
            self.number()
            self.state = 98
            self.number()
            self.state = 99
            self.number()
            self.state = 101
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==15:
                self.state = 100
                self.match(GromacsMRParser.Simple_name)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Angle_restraintsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def L_brkt(self):
            return self.getToken(GromacsMRParser.L_brkt, 0)

        def Angle_restraints(self):
            return self.getToken(GromacsMRParser.Angle_restraints, 0)

        def R_brkt(self):
            return self.getToken(GromacsMRParser.R_brkt, 0)

        def angle_restraint(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(GromacsMRParser.Angle_restraintContext)
            else:
                return self.getTypedRuleContext(GromacsMRParser.Angle_restraintContext,i)


        def getRuleIndex(self):
            return GromacsMRParser.RULE_angle_restraints

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAngle_restraints" ):
                listener.enterAngle_restraints(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAngle_restraints" ):
                listener.exitAngle_restraints(self)




    def angle_restraints(self):

        localctx = GromacsMRParser.Angle_restraintsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_angle_restraints)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 103
            self.match(GromacsMRParser.L_brkt)
            self.state = 104
            self.match(GromacsMRParser.Angle_restraints)
            self.state = 105
            self.match(GromacsMRParser.R_brkt)
            self.state = 107 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 106
                self.angle_restraint()
                self.state = 109 
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


    class Angle_restraintContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Integer(self, i:int=None):
            if i is None:
                return self.getTokens(GromacsMRParser.Integer)
            else:
                return self.getToken(GromacsMRParser.Integer, i)

        def number(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(GromacsMRParser.NumberContext)
            else:
                return self.getTypedRuleContext(GromacsMRParser.NumberContext,i)


        def Simple_name(self):
            return self.getToken(GromacsMRParser.Simple_name, 0)

        def getRuleIndex(self):
            return GromacsMRParser.RULE_angle_restraint

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAngle_restraint" ):
                listener.enterAngle_restraint(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAngle_restraint" ):
                listener.exitAngle_restraint(self)




    def angle_restraint(self):

        localctx = GromacsMRParser.Angle_restraintContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_angle_restraint)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 111
            self.match(GromacsMRParser.Integer)
            self.state = 112
            self.match(GromacsMRParser.Integer)
            self.state = 113
            self.match(GromacsMRParser.Integer)
            self.state = 114
            self.match(GromacsMRParser.Integer)
            self.state = 115
            self.match(GromacsMRParser.Integer)
            self.state = 116
            self.number()
            self.state = 117
            self.number()
            self.state = 118
            self.match(GromacsMRParser.Integer)
            self.state = 120
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==15:
                self.state = 119
                self.match(GromacsMRParser.Simple_name)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Angle_restraints_zContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def L_brkt(self):
            return self.getToken(GromacsMRParser.L_brkt, 0)

        def Angle_restraints_z(self):
            return self.getToken(GromacsMRParser.Angle_restraints_z, 0)

        def R_brkt(self):
            return self.getToken(GromacsMRParser.R_brkt, 0)

        def angle_restraint_z(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(GromacsMRParser.Angle_restraint_zContext)
            else:
                return self.getTypedRuleContext(GromacsMRParser.Angle_restraint_zContext,i)


        def getRuleIndex(self):
            return GromacsMRParser.RULE_angle_restraints_z

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAngle_restraints_z" ):
                listener.enterAngle_restraints_z(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAngle_restraints_z" ):
                listener.exitAngle_restraints_z(self)




    def angle_restraints_z(self):

        localctx = GromacsMRParser.Angle_restraints_zContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_angle_restraints_z)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 122
            self.match(GromacsMRParser.L_brkt)
            self.state = 123
            self.match(GromacsMRParser.Angle_restraints_z)
            self.state = 124
            self.match(GromacsMRParser.R_brkt)
            self.state = 126 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 125
                self.angle_restraint_z()
                self.state = 128 
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


    class Angle_restraint_zContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Integer(self, i:int=None):
            if i is None:
                return self.getTokens(GromacsMRParser.Integer)
            else:
                return self.getToken(GromacsMRParser.Integer, i)

        def number(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(GromacsMRParser.NumberContext)
            else:
                return self.getTypedRuleContext(GromacsMRParser.NumberContext,i)


        def Simple_name(self):
            return self.getToken(GromacsMRParser.Simple_name, 0)

        def getRuleIndex(self):
            return GromacsMRParser.RULE_angle_restraint_z

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAngle_restraint_z" ):
                listener.enterAngle_restraint_z(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAngle_restraint_z" ):
                listener.exitAngle_restraint_z(self)




    def angle_restraint_z(self):

        localctx = GromacsMRParser.Angle_restraint_zContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_angle_restraint_z)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 130
            self.match(GromacsMRParser.Integer)
            self.state = 131
            self.match(GromacsMRParser.Integer)
            self.state = 132
            self.match(GromacsMRParser.Integer)
            self.state = 133
            self.number()
            self.state = 134
            self.number()
            self.state = 135
            self.match(GromacsMRParser.Integer)
            self.state = 137
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==15:
                self.state = 136
                self.match(GromacsMRParser.Simple_name)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Position_restraintsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def L_brkt(self):
            return self.getToken(GromacsMRParser.L_brkt, 0)

        def Position_restraints(self):
            return self.getToken(GromacsMRParser.Position_restraints, 0)

        def R_brkt(self):
            return self.getToken(GromacsMRParser.R_brkt, 0)

        def position_restraint(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(GromacsMRParser.Position_restraintContext)
            else:
                return self.getTypedRuleContext(GromacsMRParser.Position_restraintContext,i)


        def getRuleIndex(self):
            return GromacsMRParser.RULE_position_restraints

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPosition_restraints" ):
                listener.enterPosition_restraints(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPosition_restraints" ):
                listener.exitPosition_restraints(self)




    def position_restraints(self):

        localctx = GromacsMRParser.Position_restraintsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_position_restraints)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 139
            self.match(GromacsMRParser.L_brkt)
            self.state = 140
            self.match(GromacsMRParser.Position_restraints)
            self.state = 141
            self.match(GromacsMRParser.R_brkt)
            self.state = 143 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 142
                self.position_restraint()
                self.state = 145 
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


    class Position_restraintContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Integer(self, i:int=None):
            if i is None:
                return self.getTokens(GromacsMRParser.Integer)
            else:
                return self.getToken(GromacsMRParser.Integer, i)

        def number(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(GromacsMRParser.NumberContext)
            else:
                return self.getTypedRuleContext(GromacsMRParser.NumberContext,i)


        def Simple_name(self):
            return self.getToken(GromacsMRParser.Simple_name, 0)

        def getRuleIndex(self):
            return GromacsMRParser.RULE_position_restraint

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPosition_restraint" ):
                listener.enterPosition_restraint(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPosition_restraint" ):
                listener.exitPosition_restraint(self)




    def position_restraint(self):

        localctx = GromacsMRParser.Position_restraintContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_position_restraint)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 147
            self.match(GromacsMRParser.Integer)
            self.state = 148
            self.match(GromacsMRParser.Integer)
            self.state = 149
            self.number()
            self.state = 150
            self.number()
            self.state = 151
            self.number()
            self.state = 153
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==15:
                self.state = 152
                self.match(GromacsMRParser.Simple_name)


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
            return self.getToken(GromacsMRParser.Float, 0)

        def Integer(self):
            return self.getToken(GromacsMRParser.Integer, 0)

        def getRuleIndex(self):
            return GromacsMRParser.RULE_number

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNumber" ):
                listener.enterNumber(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNumber" ):
                listener.exitNumber(self)




    def number(self):

        localctx = GromacsMRParser.NumberContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_number)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 155
            _la = self._input.LA(1)
            if not(_la==10 or _la==11):
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





