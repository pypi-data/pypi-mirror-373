##
# File: NmrStar2CSParserListener.py
# Date: 11-Apr-2025
#
# Updates:
""" ParserLister class for NMR-STAR V2.1 CS files.
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
    from wwpdb.utils.nmr.cs.NmrStar2CSParser import NmrStar2CSParser
    from wwpdb.utils.nmr.cs.BaseCSParserListener import BaseCSParserListener
    from wwpdb.utils.nmr.AlignUtil import (emptyValue, monDict3)
    from wwpdb.utils.nmr.ChemCompUtil import ChemCompUtil
    from wwpdb.utils.nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from wwpdb.utils.nmr.nef.NEFTranslator import NEFTranslator
except ImportError:
    from nmr.cs.NmrStar2CSParser import NmrStar2CSParser
    from nmr.cs.BaseCSParserListener import BaseCSParserListener
    from nmr.AlignUtil import (emptyValue, monDict3)
    from nmr.ChemCompUtil import ChemCompUtil
    from nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from nmr.nef.NEFTranslator import NEFTranslator


# This class defines a complete listener for a parse tree produced by NmrStar2CSParser.
class NmrStar2CSParserListener(ParseTreeListener, BaseCSParserListener):

    __first_seq_id = None
    __current_seq_ids = None
    __current_comp_ids = None

    __tag_order = None

    def __init__(self, verbose: bool = True, log: IO = sys.stdout,
                 polySeq: List[dict] = None, entityAssembly: Optional[dict] = None,
                 ccU: Optional[ChemCompUtil] = None, csStat: Optional[BMRBChemShiftStat] = None, nefT: Optional[NEFTranslator] = None,
                 reasons: Optional[dict] = None):
        super().__init__(verbose, log, polySeq, entityAssembly, ccU, csStat, nefT, reasons)

        self.file_type = 'nm-shi-st2'

    # Enter a parse tree produced by NmrStar2CSParser#nmrstar2_cs.
    def enterNmrstar2_cs(self, ctx: NmrStar2CSParser.Nmrstar2_csContext):  # pylint: disable=unused-argument
        self.enter()

    # Exit a parse tree produced by NmrStar2CSParser#nmrstar2_cs.
    def exitNmrstar2_cs(self, ctx: NmrStar2CSParser.Nmrstar2_csContext):  # pylint: disable=unused-argument
        self.exit()

    # Enter a parse tree produced by NmrStar2CSParser#seq_loop.
    def enterSeq_loop(self, ctx: NmrStar2CSParser.Seq_loopContext):  # pylint: disable=unused-argument
        self.__first_seq_id = None
        self.__current_seq_ids = []
        self.__current_comp_ids = []

    # Exit a parse tree produced by NmrStar2CSParser#seq_loop.
    def exitSeq_loop(self, ctx: NmrStar2CSParser.Seq_loopContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by NmrStar2CSParser#seq_tags.
    def enterSeq_tags(self, ctx: NmrStar2CSParser.Seq_tagsContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by NmrStar2CSParser#seq_tags.
    def exitSeq_tags(self, ctx: NmrStar2CSParser.Seq_tagsContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by NmrStar2CSParser#seq_data.
    def enterSeq_data(self, ctx: NmrStar2CSParser.Seq_dataContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by NmrStar2CSParser#seq_data.
    def exitSeq_data(self, ctx: NmrStar2CSParser.Seq_dataContext):  # pylint: disable=unused-argument
        for any in self.anySelection:
            if any is None:
                continue
            if isinstance(any, int):
                self.__current_seq_ids.append(any)
            elif isinstance(any, str):
                self.__current_comp_ids.append(any)
        self.anySelection.clear()

        if self.__first_seq_id is None and len(self.__current_seq_ids) > 0:
            self.__first_seq_id = self.__current_seq_ids[0]

    # Enter a parse tree produced by NmrStar2CSParser#cs_loop.
    def enterCs_loop(self, ctx: NmrStar2CSParser.Cs_loopContext):  # pylint: disable=unused-argument

        if not self.hasPolySeq and self.__first_seq_id is not None:
            self.hasPolySeq = True

            self.polySeq = [{'chain_id': '1', 'seq_id': self.__current_seq_ids, 'comp_id': self.__current_comp_ids}]
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

        self.cur_list_id = max(self.cur_list_id, 0)
        self.cur_list_id += 1

        self.chemShifts = 0
        self.offset = {}

        self.cur_subtype = 'chem_shift'

        self.__tag_order = []

    # Exit a parse tree produced by NmrStar2CSParser#cs_loop.
    def exitCs_loop(self, ctx: NmrStar2CSParser.Cs_loopContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by NmrStar2CSParser#cs_tags.
    def enterCs_tags(self, ctx: NmrStar2CSParser.Cs_tagsContext):
        if ctx.Atom_shift_assign_ID():
            self.__tag_order.append('index')
        elif ctx.Residue_author_seq_code():
            self.__tag_order.append('author_sequence_code')
        elif ctx.Residue_seq_code():
            self.__tag_order.append('sequence_code')
        elif ctx.Residue_label():
            self.__tag_order.append('residue_name')
        elif ctx.Atom_name():
            self.__tag_order.append('atom_name')
        elif ctx.Atom_type():
            self.__tag_order.append('element')
        elif ctx.Chem_shift_value():
            self.__tag_order.append('value')
        elif ctx.Chem_shift_value_error():
            self.__tag_order.append('value_uncertainty')
        elif ctx.Chem_shift_ambiguity_code():
            self.__tag_order.append('ambiguity_code')
        else:
            self.__tag_order.append('unknown')

    # Exit a parse tree produced by NmrStar2CSParser#cs_tags.
    def exitCs_tags(self, ctx: NmrStar2CSParser.Cs_tagsContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by NmrStar2CSParser#cs_data.
    def enterCs_data(self, ctx: NmrStar2CSParser.Cs_dataContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by NmrStar2CSParser#cs_data.
    def exitCs_data(self, ctx: NmrStar2CSParser.Cs_dataContext):  # pylint: disable=unused-argument

        def concat_assignment(seq, comp, atom):
            L = f'{str(seq)}:'
            if comp is not None:
                L += comp + ':'
            L += atom
            return L

        try:

            len_tag = len(self.__tag_order)
            len_any = len(self.anySelection)

            if len_tag > len_any:
                return

            if 'sequence_code' not in self.__tag_order or 'atom_name' not in self.__tag_order or 'value' not in self.__tag_order:
                return

            if not self.hasPolySeq:
                return

            if 'index' in self.__tag_order:
                index = self.anySelection[self.__tag_order.index('index')]
            else:
                index = self.chemShifts + 1

            seq_id = comp_id = atom_id = value = value_uncertainty = ambig_code = None

            for idx in range(len_any):
                if idx < len_tag:
                    tag = self.__tag_order[idx]
                    if tag == 'sequence_code':
                        if isinstance(self.anySelection[idx], int):
                            seq_id = self.anySelection[idx]
                    elif tag == 'residue_name':
                        if isinstance(self.anySelection[idx], str):
                            comp_id = self.anySelection[idx]
                    elif tag == 'atom_name':
                        if isinstance(self.anySelection[idx], str):
                            atom_id = self.anySelection[idx]
                    elif tag == 'value':
                        value = self.anySelection[idx]
                        if isinstance(value, float):
                            if self.validateCsValue(index, value, None) is None:
                                return
                        elif isinstance(value, int):
                            value = float(value)
                            if self.validateCsValue(index, value, None) is None:
                                return
                    elif tag == 'value_uncertainty':
                        value_uncetainty = self.anySelection[idx]
                        if not isinstance(value_uncertainty, float) and not isinstance(value_uncertainty, int):
                            value_uncertainty = None
                    elif tag == 'ambig_code':
                        ambig_code = self.anySelection[idx]
                        if not isinstance(value_uncetainty, int):
                            ambig_code = None

            if None in (seq_id, atom_id):
                return

            _seq_id = seq_id
            auth_seq_id_map = {}

            self.atomSelectionSets.clear()

            dstFunc = self.validateCsValue(index, value, value_uncertainty)

            if dstFunc is None:
                return

            if self.__first_seq_id is not None:
                self.predictSequenceNumberOffsetByFirstResidue(None, self.__first_seq_id, None)
            else:
                self.predictSequenceNumberOffsetByFirstResidue(None, _seq_id, comp_id)

            if None in self.offset:
                seq_id = _seq_id + self.offset[None]
                auth_seq_id_map[seq_id] = _seq_id

            L = concat_assignment(seq_id, comp_id, atom_id)

            assignment = self.extractAssignment(1, L, index, with_compid=comp_id)

            if assignment is None:
                return

            has_assignments, has_multiple_assignments = self.checkAssignment(index, assignment)

            self.addCsRow(index, dstFunc, has_assignments, has_multiple_assignments, auth_seq_id_map,
                          f'{L} -> ', default_ambig_code=ambig_code)

            self.chemShifts += 1

        finally:
            self.anySelection.clear()

    # Enter a parse tree produced by NmrStar2CSParser#any.
    def enterAny(self, ctx: NmrStar2CSParser.AnyContext):

        try:

            if ctx.Float():
                value = str(ctx.Float())
                self.anySelection.append(float(value))

            elif ctx.Integer():
                value = str(ctx.Integer())
                self.anySelection.append(int(value))

            elif ctx.Simple_name():
                self.anySelection.append(str(ctx.Simple_name()))

            elif ctx.Double_quote_string():
                self.anySelection.append(str(ctx.Double_quote_string()).strip('"'))

            else:
                self.anySelection.append(str(ctx.Single_quote_string()).strip("'"))

        except ValueError:
            self.anySelection.append(None)

    # Exit a parse tree produced by NmrStar2CSParser#any.
    def exitAny(self, ctx: NmrStar2CSParser.AnyContext):  # pylint: disable=unused-argument
        pass


# del NmrStar2CSParser
