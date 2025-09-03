##
# File: PpmCSParserListener.py
# Date: 11-Apr-2025
#
# Updates:
""" ParserLister class for PPM CS files.
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
    from wwpdb.utils.nmr.cs.PpmCSParser import PpmCSParser
    from wwpdb.utils.nmr.cs.BaseCSParserListener import BaseCSParserListener
    from wwpdb.utils.nmr.ChemCompUtil import ChemCompUtil
    from wwpdb.utils.nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from wwpdb.utils.nmr.nef.NEFTranslator import NEFTranslator
except ImportError:
    from nmr.cs.PpmCSParser import PpmCSParser
    from nmr.cs.BaseCSParserListener import BaseCSParserListener
    from nmr.ChemCompUtil import ChemCompUtil
    from nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from nmr.nef.NEFTranslator import NEFTranslator


# This class defines a complete listener for a parse tree produced by PpmCSParser.
class PpmCSParserListener(ParseTreeListener, BaseCSParserListener):

    __number = None

    def __init__(self, verbose: bool = True, log: IO = sys.stdout,
                 polySeq: List[dict] = None, entityAssembly: Optional[dict] = None,
                 ccU: Optional[ChemCompUtil] = None, csStat: Optional[BMRBChemShiftStat] = None, nefT: Optional[NEFTranslator] = None,
                 reasons: Optional[dict] = None):
        super().__init__(verbose, log, polySeq, entityAssembly, ccU, csStat, nefT, reasons)

        self.file_type = 'nm-shi-ppm'

    # Enter a parse tree produced by PpmCSParser#ppm_cs.
    def enterPpm_cs(self, ctx: PpmCSParser.Ppm_csContext):  # pylint: disable=unused-argument
        self.enter()

        self.cur_list_id = max(self.cur_list_id, 0)
        self.cur_list_id += 1

        self.cur_line_num = 0

        self.chemShifts = 0
        self.offset = {}

    # Exit a parse tree produced by PpmCSParser#ppm_cs.
    def exitPpm_cs(self, ctx: PpmCSParser.Ppm_csContext):  # pylint: disable=unused-argument
        self.exit()

    # Enter a parse tree produced by PpmCSParser#ppm_list.
    def enterPpm_list(self, ctx: PpmCSParser.Ppm_listContext):  # pylint: disable=unused-argument
        self.cur_subtype = 'chem_shift'
        self.cur_line_num += 1

    # Exit a parse tree produced by PpmCSParser#ppm_list.
    def exitPpm_list(self, ctx: PpmCSParser.Ppm_listContext):

        chain_id = None

        if ctx.Simple_name():
            L = str(ctx.Simple_name())
        elif ctx.Atom_selection_2d_ex():
            L = str(ctx.Atom_selection_2d_ex())
        else:
            L = str(ctx.Atom_selection_3d_ex())
            chain_id = L.split(':', maxsplit=1)[0]

        value = self.__number

        if value is None:
            return

        self.atomSelectionSets.clear()

        dstFunc = self.validateCsValue(self.cur_line_num, value, None)

        if dstFunc is None:
            return

        assignment = self.extractAssignment(1, L, self.cur_line_num, chain_id)

        if assignment is None:
            return

        has_assignments, has_multiple_assignments = self.checkAssignment(self.cur_line_num, assignment)

        self.addCsRow(self.cur_line_num, dstFunc, has_assignments, has_multiple_assignments, {}, f'{L} -> ')

        self.chemShifts += 1

    # Enter a parse tree produced by PpmCSParser#number.
    def enterNumber(self, ctx: PpmCSParser.NumberContext):

        try:

            if ctx.Float():
                self.__number = float(str(ctx.Float()))

            elif ctx.Integer():
                self.__number = float(str(ctx.Integer()))

            else:
                self.__number = None

        except ValueError:
            self.__number = None

    # Exit a parse tree produced by PpmCSParser#number.
    def exitNumber(self, ctx: PpmCSParser.NumberContext):  # pylint: disable=unused-argument
        pass


# del PpmCSParser
