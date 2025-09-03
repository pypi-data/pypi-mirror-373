##
# File: NmrPipeCSParserListener.py
# Date: 11-Apr-2025
#
# Updates:
""" ParserLister class for NMRPIPE CS files.
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
    from wwpdb.utils.nmr.cs.NmrPipeCSParser import NmrPipeCSParser
    from wwpdb.utils.nmr.cs.BaseCSParserListener import BaseCSParserListener
    from wwpdb.utils.nmr.AlignUtil import (emptyValue, monDict3)
    from wwpdb.utils.nmr.ChemCompUtil import ChemCompUtil
    from wwpdb.utils.nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from wwpdb.utils.nmr.nef.NEFTranslator import NEFTranslator
except ImportError:
    from nmr.cs.NmrPipeCSParser import NmrPipeCSParser
    from nmr.cs.BaseCSParserListener import BaseCSParserListener
    from nmr.AlignUtil import (emptyValue, monDict3)
    from nmr.ChemCompUtil import ChemCompUtil
    from nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from nmr.nef.NEFTranslator import NEFTranslator


# This class defines a complete listener for a parse tree produced by NmrPipeCSParser.
class NmrPipeCSParserListener(ParseTreeListener, BaseCSParserListener):

    __first_resid = 1
    __cur_sequence = ''
    __open_sequence = False
    __has_sequence = False

    __number = None

    def __init__(self, verbose: bool = True, log: IO = sys.stdout,
                 polySeq: List[dict] = None, entityAssembly: Optional[dict] = None,
                 ccU: Optional[ChemCompUtil] = None, csStat: Optional[BMRBChemShiftStat] = None, nefT: Optional[NEFTranslator] = None,
                 reasons: Optional[dict] = None):
        super().__init__(verbose, log, polySeq, entityAssembly, ccU, csStat, nefT, reasons)

        self.file_type = 'nm-shi-npi'
        self.software_name = 'NMRPipe'

    # Enter a parse tree produced by NmrPipeCSParser#nmrpipe_cs.
    def enterNmrpipe_cs(self, ctx: NmrPipeCSParser.Nmrpipe_csContext):  # pylint: disable=unused-argument
        self.enter()

    # Exit a parse tree produced by NmrPipeCSParser#nmrpipe_cs.
    def exitNmrpipe_cs(self, ctx: NmrPipeCSParser.Nmrpipe_csContext):  # pylint: disable=unused-argument
        self.exit()

    # Enter a parse tree produced by NmrPipeCSParser#sequence.
    def enterSequence(self, ctx: NmrPipeCSParser.SequenceContext):
        if self.__has_sequence and not self.__open_sequence:
            self.__first_resid = 1
            self.__cur_sequence = ''

        if ctx.First_resid():
            self.__first_resid = int(str(ctx.Integer_DA()))

        if ctx.Sequence():
            i = 0
            while ctx.One_letter_code(i):
                self.__cur_sequence += str(ctx.One_letter_code(i))
                i += 1

        self.__open_sequence = True

        self.offset = {}

    # Exit a parse tree produced by NmrPipeCSParser#sequence.
    def exitSequence(self, ctx: NmrPipeCSParser.SequenceContext):  # pylint: disable=unused-argument
        pass

    def closeSequqnce(self):
        if not self.__open_sequence:
            return

        self.__has_sequence = len(self.__cur_sequence) > 0

        self.__open_sequence = False

        if self.__has_sequence and not self.hasPolySeq:
            self.hasPolySeq = True

            def get_comp_id(one_letter_code: str):
                return next((k for k, v in monDict3.items() if v == one_letter_code and len(k) == 3), one_letter_code)

            comp_ids = [get_comp_id(one_letter_code) for one_letter_code in self.__cur_sequence]
            seq_ids = list(range(self.__first_resid, self.__first_resid + len(comp_ids) + 1))

            self.polySeq = [{'chain_id': '1', 'seq_id': seq_ids, 'comp_id': comp_ids}]
            self.entityAssembly = {'1': {'entity_id': 1, 'auth_asym_id': '.'}}

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

    # Enter a parse tree produced by NmrPipeCSParser#chemical_shifts.
    def enterChemical_shifts(self, ctx: NmrPipeCSParser.Chemical_shiftsContext):  # pylint: disable=unused-argument
        self.cur_list_id = max(self.cur_list_id, 0)
        self.cur_list_id += 1

        self.chemShifts = 0

        self.cur_subtype = 'chem_shift'

        self.predictSequenceNumberOffsetByFirstResidue(None, self.__first_resid, None)

        self.closeSequqnce()

    # Exit a parse tree produced by NmrPipeCSParser#chemical_shifts.
    def exitChemical_shifts(self, ctx: NmrPipeCSParser.Chemical_shiftsContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by NmrPipeCSParser#chemical_shift.
    def enterChemical_shift(self, ctx: NmrPipeCSParser.Chemical_shiftContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by NmrPipeCSParser#chemical_shift.
    def exitChemical_shift(self, ctx: NmrPipeCSParser.Chemical_shiftContext):

        index = self.chemShifts + 1

        seq_id = int(str(ctx.Integer()))
        comp_id = str(ctx.Simple_name(0))
        atom_id = str(ctx.Simple_name(1))
        value = self.__number

        if value is None:
            return

        if len(comp_id) == 1 and not self.polyRibonucleotide and not self.polyDeoxyribonucleotide and self.polyPeptide:
            comp_id = next((_comp_id for _comp_id in self.compIdSet if _comp_id in monDict3 and monDict3[_comp_id] == comp_id), comp_id)

        self.atomSelectionSets.clear()

        dstFunc = self.validateCsValue(index, value, None)

        if dstFunc is None:
            return

        _seq_id = seq_id

        auth_seq_id_map = {}

        self.predictSequenceNumberOffsetByFirstResidue(None, _seq_id, comp_id)

        if None in self.offset:
            seq_id += self.offset[None]
            auth_seq_id_map[seq_id] = _seq_id

        L = f'{seq_id}:{comp_id}:{atom_id}'

        assignment = self.extractAssignment(1, L, index, with_compid=comp_id)

        if assignment is None:
            return

        has_assignments, has_multiple_assignments = self.checkAssignment(index, assignment)

        self.addCsRow(index, dstFunc, has_assignments, has_multiple_assignments, auth_seq_id_map,
                      f'{L} -> ')

        self.chemShifts += 1

    # Enter a parse tree produced by NmrPipeCSParser#chemical_shifts_sw_segid.
    def enterChemical_shifts_sw_segid(self, ctx: NmrPipeCSParser.Chemical_shifts_sw_segidContext):  # pylint: disable=unused-argument
        self.cur_list_id = max(self.cur_list_id, 0)
        self.cur_list_id += 1

        self.chemShifts = 0

        self.cur_subtype = 'chem_shift'

        self.predictSequenceNumberOffsetByFirstResidue(None, self.__first_resid, None)

        self.closeSequqnce()

    # Exit a parse tree produced by NmrPipeCSParser#chemical_shifts_sw_segid.
    def exitChemical_shifts_sw_segid(self, ctx: NmrPipeCSParser.Chemical_shifts_sw_segidContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by NmrPipeCSParser#chemical_shift_sw_segid.
    def enterChemical_shift_sw_segid(self, ctx: NmrPipeCSParser.Chemical_shift_sw_segidContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by NmrPipeCSParser#chemical_shift_sw_segid.
    def exitChemical_shift_sw_segid(self, ctx: NmrPipeCSParser.Chemical_shift_sw_segidContext):

        index = self.chemShifts + 1

        chain_id = str(ctx.Simple_name(0))
        seq_id = int(str(ctx.Integer()))
        comp_id = str(ctx.Simple_name(1))
        atom_id = str(ctx.Simple_name(2))
        value = self.__number

        if value is None:
            return

        if len(comp_id) == 1 and not self.polyRibonucleotide and not self.polyDeoxyribonucleotide and self.polyPeptide:
            comp_id = next((_comp_id for _comp_id in self.compIdSet if _comp_id in monDict3 and monDict3[_comp_id] == comp_id), comp_id)

        self.atomSelectionSets.clear()

        dstFunc = self.validateCsValue(index, value, None)

        if dstFunc is None:
            return

        _seq_id = seq_id

        auth_seq_id_map = {}

        self.predictSequenceNumberOffsetByFirstResidue(chain_id, _seq_id, comp_id)

        if chain_id in self.offset:
            seq_id = _seq_id + self.offset[chain_id]
            auth_seq_id_map[seq_id] = _seq_id

        L = f'{chain_id}:{seq_id}:{comp_id}:{atom_id}'

        assignment = self.extractAssignment(1, L, index, chain_id, comp_id)

        if assignment is None:
            return

        has_assignments, has_multiple_assignments = self.checkAssignment(index, assignment)

        self.addCsRow(index, dstFunc, has_assignments, has_multiple_assignments, auth_seq_id_map,
                      f'{L} -> ')

        self.chemShifts += 1

    # Enter a parse tree produced by NmrPipeCSParser#chemical_shifts_ew_segid.
    def enterChemical_shifts_ew_segid(self, ctx: NmrPipeCSParser.Chemical_shifts_ew_segidContext):  # pylint: disable=unused-argument
        self.cur_list_id = max(self.cur_list_id, 0)
        self.cur_list_id += 1

        self.chemShifts = 0

        self.cur_subtype = 'chem_shift'

        self.predictSequenceNumberOffsetByFirstResidue(None, self.__first_resid, None)

        self.closeSequqnce()

    # Exit a parse tree produced by NmrPipeCSParser#chemical_shifts_ew_segid.
    def exitChemical_shifts_ew_segid(self, ctx: NmrPipeCSParser.Chemical_shifts_ew_segidContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by NmrPipeCSParser#chemical_shift_ew_segid.
    def enterChemical_shift_ew_segid(self, ctx: NmrPipeCSParser.Chemical_shift_ew_segidContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by NmrPipeCSParser#chemical_shift_ew_segid.
    def exitChemical_shift_ew_segid(self, ctx: NmrPipeCSParser.Chemical_shift_ew_segidContext):

        index = self.chemShifts + 1

        seq_id = int(str(ctx.Integer()))
        comp_id = str(ctx.Simple_name(0))
        atom_id = str(ctx.Simple_name(1))
        chain_id = str(ctx.Simple_name(2))
        value = self.__number

        if value is None:
            return

        if len(comp_id) == 1 and not self.polyRibonucleotide and not self.polyDeoxyribonucleotide and self.polyPeptide:
            comp_id = next((_comp_id for _comp_id in self.compIdSet if _comp_id in monDict3 and monDict3[_comp_id] == comp_id), comp_id)

        self.atomSelectionSets.clear()

        dstFunc = self.validateCsValue(index, value, None)

        if dstFunc is None:
            return

        _seq_id = seq_id

        auth_seq_id_map = {}

        self.predictSequenceNumberOffsetByFirstResidue(chain_id, _seq_id, comp_id)

        if chain_id in self.offset:
            seq_id = _seq_id + self.offset[chain_id]
            auth_seq_id_map[seq_id] = _seq_id

        L = f'{chain_id}:{seq_id}:{comp_id}:{atom_id}'

        assignment = self.extractAssignment(1, L, index, chain_id, comp_id)

        if assignment is None:
            return

        has_assignments, has_multiple_assignments = self.checkAssignment(index, assignment)

        self.addCsRow(index, dstFunc, has_assignments, has_multiple_assignments, auth_seq_id_map,
                      f'{L} -> ')

        self.chemShifts += 1

    # Enter a parse tree produced by NmrPipeCSParser#number.
    def enterNumber(self, ctx: NmrPipeCSParser.NumberContext):
        if ctx.Float():
            self.__number = float(str(ctx.Float()))

        elif ctx.Float_DecimalComma():
            self.__number = float(str(ctx.Float_DecimalComma()).replace(',', '.', 1))

        elif ctx.Integer():
            self.__number = float(str(ctx.Integer()))

        else:
            self.__number = None

    # Exit a parse tree produced by NmrPipeCSParser#number.
    def exitNumber(self, ctx: NmrPipeCSParser.NumberContext):  # pylint: disable=unused-argument
        pass


# del NmrPipeCSParser
