##
# File: OliviaCSParserListener.py
# Date: 22-Aug-2025
#
# Updates:
""" ParserLister class for OLIVIA CS files.
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
    from wwpdb.utils.nmr.cs.OliviaCSParser import OliviaCSParser
    from wwpdb.utils.nmr.cs.BaseCSParserListener import BaseCSParserListener
    from wwpdb.utils.nmr.AlignUtil import (emptyValue, monDict3)
    from wwpdb.utils.nmr.ChemCompUtil import ChemCompUtil
    from wwpdb.utils.nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from wwpdb.utils.nmr.nef.NEFTranslator import NEFTranslator
except ImportError:
    from nmr.cs.OliviaCSParser import OliviaCSParser
    from nmr.cs.BaseCSParserListener import BaseCSParserListener
    from nmr.AlignUtil import (emptyValue, monDict3)
    from nmr.ChemCompUtil import ChemCompUtil
    from nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from nmr.nef.NEFTranslator import NEFTranslator


# This class defines a complete listener for a parse tree produced by OliviaCSParser.
class OliviaCSParserListener(ParseTreeListener, BaseCSParserListener):

    __polySeq = None
    __entityAssembly = None

    def __init__(self, verbose: bool = True, log: IO = sys.stdout,
                 polySeq: List[dict] = None, entityAssembly: Optional[dict] = None,
                 ccU: Optional[ChemCompUtil] = None, csStat: Optional[BMRBChemShiftStat] = None, nefT: Optional[NEFTranslator] = None,
                 reasons: Optional[dict] = None):
        super().__init__(verbose, log, polySeq, entityAssembly, ccU, csStat, nefT, reasons)

        self.file_type = 'nm-shi-oli'
        self.software_name = 'Olivia'

    # Enter a parse tree produced by OliviaCSParser#olivia_cs.
    def enterOlivia_cs(self, ctx: OliviaCSParser.Olivia_csContext):  # pylint: disable=unused-argument
        self.enter()

    # Exit a parse tree produced by OliviaCSParser#olivia_cs.
    def exitOlivia_cs(self, ctx: OliviaCSParser.Olivia_csContext):  # pylint: disable=unused-argument
        self.exit()

    # Enter a parse tree produced by OliviaCSParser#sequence.
    def enterSequence(self, ctx: OliviaCSParser.SequenceContext):  # pylint: disable=unused-argument
        self.__polySeq = []
        self.__entityAssembly = {}
        self.offset = {}

    # Exit a parse tree produced by OliviaCSParser#sequence.
    def exitSequence(self, ctx: OliviaCSParser.SequenceContext):  # pylint: disable=unused-argument

        if not self.hasPolySeq:

            self.polySeq = self.__polySeq
            self.entityAssembly = self.__entityAssembly
            self.hasPolySeq = True

            self.labelToAuthSeq = {}
            for ps in self.polySeq:
                chainId = ps['chain_id']
                for seqId in ps['seq_id']:
                    self.labelToAuthSeq[(chainId, seqId)] = (chainId, seqId)
            self.authToLabelSeq = {v: k for k, v in self.labelToAuthSeq.items()}

            self.chainIdSet = set(ps['chain_id'] for ps in self.polySeq)
            self.compIdSet = set()

            def is_data(array: list) -> bool:
                return not any(d in emptyValue for d in array)

            for ps in self.polySeq:
                self.compIdSet.update(set(filter(is_data, ps['comp_id'])))

            for compId in self.compIdSet:
                if compId in monDict3:
                    if len(compId) == 3:
                        self.polyPeptide = True
                    elif len(compId) == 2 and compId.startswith('D'):
                        self.polyDeoxyribonucleotide = True
                    elif len(compId) == 1:
                        self.polyRibonucleotide = True

    # Enter a parse tree produced by OliviaCSParser#residue.
    def enterResidue(self, ctx: OliviaCSParser.ResidueContext):

        chain_id = str(ctx.Simple_name(0))
        comp_id = str(ctx.Simple_name(1))
        seq_id = int(str(ctx.Integer()))

        ps = next((ps for ps in self.__polySeq if ps['chain_id'] == chain_id), None)

        if ps is None:
            self.__polySeq.append({'chain_id': chain_id, 'seq_id': [], 'comp_id': []})
            ps = self.__polySeq[-1]
            entity_assembly_id = len(self.__polySeq)
            self.__entityAssembly[str(entity_assembly_id)] = {'entity_id': entity_assembly_id, 'auth_asym_id': chain_id}
            self.predictSequenceNumberOffsetByFirstResidue(chain_id, seq_id, comp_id)

        ps['seq_id'].append(seq_id)
        ps['comp_id'].append(comp_id)

    # Exit a parse tree produced by OliviaCSParser#residue.
    def exitResidue(self, ctx: OliviaCSParser.ResidueContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by OliviaCSParser#chemical_shifts.
    def enterChemical_shifts(self, ctx: OliviaCSParser.Chemical_shiftsContext):  # pylint: disable=unused-argument
        self.cur_list_id = max(self.cur_list_id, 0)
        self.cur_list_id += 1

        self.chemShifts = 0

        self.cur_subtype = 'chem_shift'

    # Exit a parse tree produced by OliviaCSParser#chemical_shifts.
    def exitChemical_shifts(self, ctx: OliviaCSParser.Chemical_shiftsContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by OliviaCSParser#chemical_shift.
    def enterChemical_shift(self, ctx: OliviaCSParser.Chemical_shiftContext):  # pylint: disable=unused-argument
        self.chemShifts += 1

    # Exit a parse tree produced by OliviaCSParser#chemical_shift.
    def exitChemical_shift(self, ctx: OliviaCSParser.Chemical_shiftContext):

        try:

            if len(self.anySelection) == 0:
                self.chemShifts -= 1
                return

            index = self.chemShifts
            chain_id = str(ctx.Simple_name(0))
            comp_id = str(ctx.Simple_name(1))
            atom_id = str(ctx.Simple_name(2))
            seq_id = int(str(ctx.Integer()))

            value = self.anySelection[0]
            val_err = self.anySelection[1]

            if value is None:
                self.chemShifts -= 1
                return

            if len(comp_id) == 1 and not self.polyRibonucleotide and not self.polyDeoxyribonucleotide and self.polyPeptide:
                comp_id = next((_comp_id for _comp_id in self.compIdSet if _comp_id in monDict3 and monDict3[_comp_id] == comp_id), comp_id)

            self.atomSelectionSets.clear()

            dstFunc = self.validateCsValue(index, value, val_err)

            if dstFunc is None:
                self.chemShifts -= 1
                return

            _seq_id = seq_id

            auth_seq_id_map = {}

            self.predictSequenceNumberOffsetByFirstResidue(chain_id, _seq_id, comp_id)

            if chain_id in self.offset:
                seq_id += self.offset[chain_id]
                auth_seq_id_map[seq_id] = _seq_id

            L = f'{chain_id}:{seq_id}:{comp_id}:{atom_id}'

            assignment = self.extractAssignment(1, L, index, chain_id, comp_id)

            if assignment is None:
                self.chemShifts -= 1
                return

            has_assignments, has_multiple_assignments = self.checkAssignment(index, assignment)

            self.addCsRow(index, dstFunc, has_assignments, has_multiple_assignments, auth_seq_id_map,
                          f'{L} -> ')

        finally:
            self.anySelection.clear()

    # Enter a parse tree produced by OliviaCSParser#number.
    def enterNumber(self, ctx: OliviaCSParser.NumberContext):
        if ctx.Float():
            self.anySelection.append(float(str(ctx.Float())))

        elif ctx.Real():
            self.anySelection.append(float(str(ctx.Real())))

        elif ctx.Integer():
            self.anySelection.append(float(str(ctx.Integer())))

        else:
            self.anySelection.append(None)

    # Exit a parse tree produced by OliviaCSParser#number.
    def exitNumber(self, ctx: OliviaCSParser.NumberContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by OliviaCSParser#comment.
    def enterComment(self, ctx: OliviaCSParser.CommentContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by OliviaCSParser#comment.
    def exitComment(self, ctx: OliviaCSParser.CommentContext):  # pylint: disable=unused-argument
        pass


# del OliviaCSParser
