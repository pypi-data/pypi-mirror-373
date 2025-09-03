##
# File: GarretCSParserListener.py
# Date: 11-Apr-2025
#
# Updates:
""" ParserLister class for GARRET CS files.
    @author: Masashi Yokochi
"""
__docformat__ = "restructuredtext en"
__author__ = "Masashi Yokochi"
__email__ = "yokochi@protein.osaka-u.ac.jp"
__license__ = "Apache License 2.0"
__version__ = "1.0.0"

import sys

from antlr4 import ParseTreeListener
from typing import IO, List, Optional

try:
    from wwpdb.utils.nmr.cs.GarretCSParser import GarretCSParser
    from wwpdb.utils.nmr.cs.BaseCSParserListener import BaseCSParserListener
    from wwpdb.utils.nmr.ChemCompUtil import ChemCompUtil
    from wwpdb.utils.nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from wwpdb.utils.nmr.nef.NEFTranslator import NEFTranslator
except ImportError:
    from nmr.cs.GarretCSParser import GarretCSParser
    from nmr.cs.BaseCSParserListener import BaseCSParserListener
    from nmr.ChemCompUtil import ChemCompUtil
    from nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from nmr.nef.NEFTranslator import NEFTranslator


# This class defines a complete listener for a parse tree produced by GarretCSParser.
class GarretCSParserListener(ParseTreeListener, BaseCSParserListener):

    __seq_id = None
    __comp_id = None
    __number = None

    def __init__(self, verbose: bool = True, log: IO = sys.stdout,
                 polySeq: List[dict] = None, entityAssembly: Optional[dict] = None,
                 ccU: Optional[ChemCompUtil] = None, csStat: Optional[BMRBChemShiftStat] = None, nefT: Optional[NEFTranslator] = None,
                 reasons: Optional[dict] = None):
        super().__init__(verbose, log, polySeq, entityAssembly, ccU, csStat, nefT, reasons)

        self.file_type = 'nm-shi-gar'

    # Enter a parse tree produced by GarretCSParser#garret_cs.
    def enterGarret_cs(self, ctx: GarretCSParser.Garret_csContext):  # pylint: disable=unused-argument
        self.enter()

        self.cur_list_id = max(self.cur_list_id, 0)
        self.cur_list_id += 1

        self.cur_line_num = 0

        self.chemShifts = 0
        self.offset = {}

        self.cur_subtype = 'chem_shift'

    # Exit a parse tree produced by GarretCSParser#garret_cs.
    def exitGarret_cs(self, ctx: GarretCSParser.Garret_csContext):  # pylint: disable=unused-argument
        self.exit()

    # Enter a parse tree produced by GarretCSParser#residue_list.
    def enterResidue_list(self, ctx: GarretCSParser.Residue_listContext):
        if ctx.Integer():
            self.__seq_id = int(str(ctx.Integer()))
        if ctx.Simple_name():
            self.__comp_id = str(ctx.Simple_name())

    # Exit a parse tree produced by GarretCSParser#residue_list.
    def exitResidue_list(self, ctx: GarretCSParser.Residue_listContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by GarretCSParser#shift_list.
    def enterShift_list(self, ctx: GarretCSParser.Shift_listContext):  # pylint: disable=unused-argument
        self.cur_subtype = 'chem_shift'
        self.cur_line_num += 1

    # Exit a parse tree produced by GarretCSParser#shift_list.
    def exitShift_list(self, ctx: GarretCSParser.Shift_listContext):

        value = self.__number

        if value is None:
            return

        self.atomSelectionSets.clear()

        dstFunc = self.validateCsValue(self.cur_line_num, value, None)

        if dstFunc is None:
            return

        L = f'{self.__seq_id}:{self.__comp_id}:{str(ctx.Simple_name())}'

        assignment = self.extractAssignment(1, L, self.cur_line_num, with_compid=self.__comp_id)

        if assignment is None:
            return

        has_assignments, has_multiple_assignments = self.checkAssignment(self.cur_line_num, assignment)

        self.addCsRow(self.cur_line_num, dstFunc, has_assignments, has_multiple_assignments, {}, f'{L} -> ')

        self.chemShifts += 1

    # Enter a parse tree produced by GarretCSParser#number.
    def enterNumber(self, ctx: GarretCSParser.NumberContext):

        try:

            if ctx.Float():
                self.__number = float(str(ctx.Float()))

            elif ctx.Integer():
                self.__number = float(str(ctx.Integer()))

            else:
                self.__number = None

        except ValueError:
            self.__number = None

    # Exit a parse tree produced by GarretCSParser#number.
    def exitNumber(self, ctx: GarretCSParser.NumberContext):  # pylint: disable=unused-argument
        pass


# del GarretCSParser
