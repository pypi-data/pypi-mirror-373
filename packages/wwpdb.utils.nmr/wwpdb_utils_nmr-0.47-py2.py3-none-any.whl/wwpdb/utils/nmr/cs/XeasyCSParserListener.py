##
# File: XeasyCSParserListener.py
# Date: 10-Apr-2025
#
# Updates:
""" ParserLister class for XEASY CS (aka. PROT) files.
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
    from wwpdb.utils.nmr.pk.XeasyPROTParser import XeasyPROTParser
    from wwpdb.utils.nmr.cs.BaseCSParserListener import BaseCSParserListener
    from wwpdb.utils.nmr.ChemCompUtil import ChemCompUtil
    from wwpdb.utils.nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from wwpdb.utils.nmr.nef.NEFTranslator import NEFTranslator
except ImportError:
    from nmr.pk.XeasyPROTParser import XeasyPROTParser
    from nmr.cs.BaseCSParserListener import BaseCSParserListener
    from nmr.ChemCompUtil import ChemCompUtil
    from nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from nmr.nef.NEFTranslator import NEFTranslator


# This class defines a complete listener for a parse tree produced by XeasyCSParser.
class XeasyCSParserListener(ParseTreeListener, BaseCSParserListener):

    # residue
    __cur_residue = None

    __auth_seq_id_map = None

    def __init__(self, verbose: bool = True, log: IO = sys.stdout,
                 polySeq: List[dict] = None, entityAssembly: Optional[dict] = None,
                 ccU: Optional[ChemCompUtil] = None, csStat: Optional[BMRBChemShiftStat] = None, nefT: Optional[NEFTranslator] = None,
                 reasons: Optional[dict] = None):
        super().__init__(verbose, log, polySeq, entityAssembly, ccU, csStat, nefT, reasons)

        self.file_type = 'nm-aux-xea'
        self.software_name = 'XEASY'

    # Enter a parse tree produced by XeasyPROTParser#xeasy_prot.
    def enterXeasy_prot(self, ctx: XeasyPROTParser.Xeasy_protContext):  # pylint: disable=unused-argument
        self.enter()

        self.cur_subtype = 'chem_shift'

        self.cur_list_id = max(self.cur_list_id, 0)
        self.cur_list_id += 1

        self.chemShifts = 0
        self.offset = {}

        self.__auth_seq_id_map = {}

    # Exit a parse tree produced by XeasyPROTParser#xeasy_prot.
    def exitXeasy_prot(self, ctx: XeasyPROTParser.Xeasy_protContext):  # pylint: disable=unused-argument
        self.exit()

    # Enter a parse tree produced by XeasyPROTParser#prot.
    def enterProt(self, ctx: XeasyPROTParser.ProtContext):  # pylint: disable=unused-argument
        self.chemShifts += 1

    # Exit a parse tree produced by XeasyPROTParser#prot.
    def exitProt(self, ctx: XeasyPROTParser.ProtContext):

        if not self.hasPolySeq:
            return

        try:

            index = int(str(ctx.Integer()))
            shift = float(str(ctx.Float(0)))
            shift_error = float(str(ctx.Float(1)))
            atomId = str(ctx.Simple_name())
            L = f'{self.__cur_residue} {atomId}'

            self.atomSelectionSets.clear()

            dstFunc = self.validateCsValue(index, shift, shift_error)

            if dstFunc is None:
                self.chemShifts -= 1
                return

            assignment = self.extractAssignment(1, L, index)

            if assignment is None:
                self.chemShifts -= 1
                return

            has_assignments, has_multiple_assignments = self.checkAssignment(index, assignment)

            self.addCsRow(index, dstFunc, has_assignments, has_multiple_assignments, self.__auth_seq_id_map,
                          f'{L} -> ')

        except (ValueError, TypeError):
            self.chemShifts -= 1

    # Enter a parse tree produced by XeasyPROTParser#residue.
    def enterResidue(self, ctx: XeasyPROTParser.ResidueContext):
        if ctx.Integer():
            self.__cur_residue = str(ctx.Integer())

            residue = int(self.__cur_residue)

            if self.chemShifts == 1 and self.hasPolySeq:
                self.predictSequenceNumberOffsetByFirstResidue(None, residue, None)

            if None in self.offset:
                _residue = residue
                residue += self.offset[None]
                self.__cur_residue = str(residue)
                self.__auth_seq_id_map[_residue] = residue

        else:
            self.__cur_residue = str(ctx.Simple_name())

    # Exit a parse tree produced by XeasyPROTParser#residue.
    def exitResidue(self, ctx: XeasyPROTParser.ResidueContext):  # pylint: disable=unused-argument
        pass


# del XeasyCSParser
