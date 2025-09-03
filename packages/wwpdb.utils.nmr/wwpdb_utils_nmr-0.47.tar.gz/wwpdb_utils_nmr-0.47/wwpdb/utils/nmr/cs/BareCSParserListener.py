##
# File: BareCSParserListener.py
# Date: 08-Apr-2025
#
# Updates:
""" ParserLister class for Bare WSV/TSV/CSV CS files.
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
    from wwpdb.utils.nmr.cs.BareCSParser import BareCSParser
    from wwpdb.utils.nmr.cs.BaseCSParserListener import (BaseCSParserListener,
                                                         CHEM_SHIFT_HALF_SPIN_NUCLEUS)
    from wwpdb.utils.nmr.ChemCompUtil import ChemCompUtil
    from wwpdb.utils.nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from wwpdb.utils.nmr.nef.NEFTranslator import NEFTranslator
except ImportError:
    from nmr.cs.BareCSParser import BareCSParser
    from nmr.cs.BaseCSParserListener import (BaseCSParserListener,
                                             CHEM_SHIFT_HALF_SPIN_NUCLEUS)
    from nmr.ChemCompUtil import ChemCompUtil
    from nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from nmr.nef.NEFTranslator import NEFTranslator


# This class defines a complete listener for a parse tree produced by BareCSParser.
class BareCSParserListener(ParseTreeListener, BaseCSParserListener):

    __col_name = None
    __col_order = None

    def __init__(self, verbose: bool = True, log: IO = sys.stdout,
                 polySeq: List[dict] = None, entityAssembly: Optional[dict] = None,
                 ccU: Optional[ChemCompUtil] = None, csStat: Optional[BMRBChemShiftStat] = None, nefT: Optional[NEFTranslator] = None,
                 reasons: Optional[dict] = None):
        super().__init__(verbose, log, polySeq, entityAssembly, ccU, csStat, nefT, reasons)

        self.file_type = 'nm-shi-bar'

    # Enter a parse tree produced by BareCSParser#bare_cs.
    def enterBare_cs(self, ctx: BareCSParser.Bare_csContext):  # pylint: disable=unused-argument
        self.enter()

    # Exit a parse tree produced by BareCSParser#bare_cs.
    def exitBare_cs(self, ctx: BareCSParser.Bare_csContext):  # pylint: disable=unused-argument
        self.exit()

    # Enter a parse tree produced by BareCSParser#cs_raw_format.
    def enterCs_raw_format(self, ctx: BareCSParser.Cs_raw_formatContext):

        def is_half_spin_nuclei(atom_id: str) -> bool:
            """ Return whether nuclei of a given atom_id has a spin 1/2.
                @return: True for spin 1/2 nuclei, False otherwise
            """

            return any(nucl for nucl in CHEM_SHIFT_HALF_SPIN_NUCLEUS if atom_id.startswith(nucl))

        atom_like_names = self.csStat.getAtomLikeNameSet(1)
        cs_atom_like_names = list(filter(is_half_spin_nuclei, atom_like_names))
        cs_atom_like_names.extend(['HN', 'CO'])

        self.software_name = None

        self.__col_name = []
        self.__col_order = []

        def register_column_info(col_name):
            self.__col_name.append(col_name)
            if col_name in cs_atom_like_names or col_name.endswith('#') or col_name.endswith('#'):
                self.__col_order.append('atom_name_instance')
            elif col_name.startswith('Q') or col_name.startswith('M') and 'H' + col_name[1:].replace('%', '2').replace('#', '2') in cs_atom_like_names:
                self.__col_order.append('atom_name_instance')
            elif (col_name.endswith('%') or col_name.endswith('#')) and col_name[:-1] + '2' in cs_atom_like_names:
                self.__col_order.append('atom_name_instance')
            elif 'RES' in col_name or 'SEQ' in col_name or 'COMP' in col_name or 'GROUP' in col_name or 'LABEL' in col_name:
                if 'COMP_ID' in col_name or 'NAME' in col_name or 'TYPE' in col_name or 'GROUP' in col_name or 'LABEL' in col_name:
                    self.__col_order.append('residue_name')
                else:
                    self.__col_order.append('sequence_code')
            elif 'CHAIN' in col_name or 'ASYM' in col_name or 'ENTITY' in col_name:
                self.__col_order.append('chain_code')
            elif 'ATOM' in col_name and 'TYPE' not in col_name and 'ISOTOPE' not in col_name and 'NUM' not in col_name:
                self.__col_order.append('atom_name')
            elif 'ASS' in col_name and 'ASSIGNMENTS' not in col_name:
                self.__col_order.append('assignment')
            elif 'ID' in col_name or 'NUM' in col_name or 'INDEX' in col_name:
                self.__col_order.append('index')
            elif ('SHIFT' in col_name or 'VAL' in col_name) and 'ERR' not in col_name and 'UNCERT' not in col_name:
                self.__col_order.append('value')
            elif 'ERR' in col_name or 'UNCERT' in col_name or 'DEV' in col_name:
                self.__col_order.append('value_uncertainty')
            elif ('ATOM' in col_name and 'TYPE' in col_name) or 'ELEM' in col_name or 'NUC' in col_name:
                self.__col_order.append('element')
            elif 'ISOTOPE' in col_name:
                self.__col_order.append('isotope_number')
            elif 'COMMENT' in col_name or 'DETAIL' in col_name or 'MEMO' in col_name:
                self.__col_order.append('details')
            elif 'OCC' in col_name:
                self.__col_order.append('occupancy')
            elif 'MERIT' in col_name:
                self.__col_order.append('figure_of_merit')
            elif 'AMBIG' in col_name:
                if 'SET' not in col_name:
                    self.__col_order.append('ambiguity_code')
                else:
                    self.__col_order.append('ambiguity_set_id')
            else:
                self.__col_order.append('unknown')

        if ctx.Simple_name(0):
            i = 0
            while ctx.Simple_name(i):
                register_column_info(str(ctx.Simple_name(i)).upper())
                i += 1

        elif ctx.Double_quote_string(0):
            i = 0
            while ctx.Double_quote_string(i):
                register_column_info(str(ctx.Double_quote_string(i)).strip('"').upper())
                i += 1

        sparky_resonance_columns = ('GROUP', 'ATOM', 'NUC', 'SHIFT', 'SDEV')
        if all(col_name in self.__col_name for col_name in sparky_resonance_columns):
            self.software_name = 'SPARKY'

        self.cur_list_id = max(self.cur_list_id, 0)
        self.cur_list_id += 1

        self.cur_line_num = 0

        self.chemShifts = 0
        self.offset = {}

    # Exit a parse tree produced by BareCSParser#cs_raw_format.
    def exitCs_raw_format(self, ctx: BareCSParser.Cs_raw_formatContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by BareCSParser#cs_raw_list.
    def enterCs_raw_list(self, ctx: BareCSParser.Cs_raw_listContext):  # pylint: disable=unused-argument
        self.cur_subtype = 'chem_shift'
        self.cur_line_num += 1

    # Exit a parse tree produced by BareCSParser#cs_raw_list.
    def exitCs_raw_list(self, ctx: BareCSParser.Cs_raw_listContext):  # pylint: disable=unused-argument

        def concat_assignment(chain, seq, comp, atom):
            L = ''
            if chain is not None:
                L = chain + ':'
            if seq is not None:
                L += str(seq) + ':'
            if comp is not None:
                L += comp + ':'
            L += atom
            return L

        try:

            len_ord = len(self.__col_order)
            len_any = len(self.anySelection)

            if len_ord > len_any:
                return

            if self.chemShifts == 0 and len_ord + 1 == len_any:
                if 'sequence_code' not in self.__col_order:
                    self.__col_order.insert(0, 'sequence_code')
                elif 'atom_name_instance' not in self.__col_order and 'assignment' not in self.__col_order:
                    self.__col_order.insert(0, 'assignment')
                elif 'index' not in self.__col_order:
                    self.__col_order.insert(0, 'index')
                else:
                    self.__col_order.insert(0, 'unknown')
                self.__col_name.insert(0, 'N/A')
                len_ord += 1

            if not ((('sequence_code' in self.__col_order or 'residue_name' in self.__col_order) and 'atom_name_instance' in self.__col_order)
                    or ('value' in self.__col_order and ((('sequence_code' in self.__col_order or 'residue_name' in self.__col_order) and 'atom_name' in self.__col_order)
                                                         or ('assignment' in self.__col_order and 'atom_name' not in self.__col_order)))):
                return

            if not self.hasPolySeq:
                return

            if ('sequence_code' in self.__col_order or 'residue_name' in self.__col_order) and 'atom_name_instance' in self.__col_order:

                chain_id = seq_id = comp_id = None
                atom_ids, values, details = [], [], []

                for idx in range(len_any):
                    if idx < len_ord:
                        order = self.__col_order[idx]
                        if order == 'chain_code':
                            if isinstance(self.anySelection[idx], str):
                                chain_id = self.anySelection[idx]
                            elif isinstance(self.anySelection[idx], int):
                                chain_id = str(self.anySelection[idx])
                        elif order == 'sequence_code':
                            if isinstance(self.anySelection[idx], int):
                                seq_id = self.anySelection[idx]
                            elif isinstance(self.anySelection[idx], str):
                                comp_id = self.anySelection[idx]
                        elif order == 'residue_name':
                            if isinstance(self.anySelection[idx], str):
                                comp_id = self.anySelection[idx]
                            elif isinstance(self.anySelection[idx], int):
                                seq_id = self.anySelection[idx]
                        elif order == 'atom_name_instance':
                            if isinstance(self.anySelection[idx], float):
                                value = self.anySelection[idx]
                                if self.validateCsValue(self.cur_list_id, value, None) is not None:
                                    atom_ids.append(self.__col_name[idx])
                                    values.append(value)
                            elif isinstance(self.anySelection[idx], int):
                                value = float(self.anySelection[idx])
                                if self.validateCsValue(self.cur_list_id, value, None) is not None:
                                    atom_ids.append(self.__col_name[idx])
                                    values.append(value)
                        elif order == 'details':
                            details.append(self.anySelection[idx] if isinstance(self.anySelection[idx], str) else str(self.anySelection[idx]))
                    elif self.__col_order[len_ord - 1] == 'details':
                        details.append(self.anySelection[idx] if isinstance(self.anySelection[idx], str) else str(self.anySelection[idx]))

                if len(details) == 0:
                    details = None
                else:
                    details = ' '.join(details)

                if seq_id is None or len(atom_ids) == 0:
                    return

                _seq_id = seq_id
                auth_seq_id_map = {}

                for atom_id, value in zip(atom_ids, values):
                    self.atomSelectionSets.clear()

                    dstFunc = self.validateCsValue(self.cur_line_num, value, None)

                    if dstFunc is None:
                        continue

                    self.predictSequenceNumberOffsetByFirstResidue(chain_id, _seq_id, comp_id)

                    if chain_id in self.offset:
                        seq_id = _seq_id + self.offset[chain_id]
                        auth_seq_id_map[seq_id] = _seq_id

                    L = concat_assignment(chain_id, seq_id, comp_id, atom_id)

                    assignment = self.extractAssignment(1, L, self.cur_line_num, chain_id, comp_id)

                    if assignment is None:
                        continue

                    has_assignments, has_multiple_assignments = self.checkAssignment(self.cur_line_num, assignment)

                    self.addCsRow(self.cur_line_num, dstFunc, has_assignments, has_multiple_assignments, auth_seq_id_map,
                                  f'{L} -> ', details)

                    self.chemShifts += 1

            elif ('sequence_code' in self.__col_order or 'residue_name' in self.__col_order) and 'atom_name' in self.__col_order:

                chain_id = seq_id = comp_id = None
                atom_ids, values, value_uncertainties, occupancies, figure_of_merits, details = [], [], [], [], [], []

                for idx in range(len_any):
                    if idx < len_ord:
                        order = self.__col_order[idx]
                        if order == 'chain_code':
                            if isinstance(self.anySelection[idx], str):
                                chain_id = self.anySelection[idx]
                            elif isinstance(self.anySelection[idx], int):
                                chain_id = str(self.anySelection[idx])
                        elif order == 'sequence_code':
                            if isinstance(self.anySelection[idx], int):
                                seq_id = self.anySelection[idx]
                            elif isinstance(self.anySelection[idx], str):
                                comp_id = self.anySelection[idx]
                        elif order == 'residue_name':
                            if isinstance(self.anySelection[idx], str):
                                comp_id = self.anySelection[idx]
                            elif isinstance(self.anySelection[idx], int):
                                seq_id = self.anySelection[idx]
                        elif order == 'atom_name':
                            if isinstance(self.anySelection[idx], str):
                                atom_ids.append(self.anySelection[idx])
                        elif order == 'value':
                            value = self.anySelection[idx]
                            if isinstance(value, float):
                                if self.validateCsValue(self.cur_list_id, value, None) is not None:
                                    values.append(self.anySelection[idx])
                                elif len(atom_ids) > len(values):
                                    del atom_ids[-1]
                            elif isinstance(value, int):
                                value = float(value)
                                if self.validateCsValue(self.cur_list_id, value, None) is not None:
                                    values.append(self.anySelection[idx])
                                elif len(atom_ids) > len(values):
                                    del atom_ids[-1]
                            elif len(atom_ids) > len(values):
                                del atom_ids[-1]
                        elif order == 'value_uncertainty':
                            if len(values) - 1 == len(value_uncertainties):
                                value_uncertainty = self.anySelection[idx]
                                if isinstance(value_uncertainty, float):
                                    value_uncertainties.append(value_uncertainty)
                                else:
                                    value_uncertainties.append(None)
                        elif order == 'occupancy':
                            if len(values) - 1 == len(occupancies):
                                occupancy = self.anySelection[idx]
                                if isinstance(occupancy, float):
                                    occupancies.append(occupancy)
                                else:
                                    occupancies.append(None)
                        elif order == 'figure_of_merit':
                            if len(values) - 1 == len(figure_of_merits):
                                figure_of_merit = self.anySelection[idx]
                                if isinstance(figure_of_merit, float):
                                    figure_of_merits.append(figure_of_merit)
                                else:
                                    figure_of_merits.append(None)
                        elif order == 'details':
                            details.append(self.anySelection[idx] if isinstance(self.anySelection[idx], str) else str(self.anySelection[idx]))
                    elif self.__col_order[len_ord - 1] == 'details':
                        details.append(self.anySelection[idx] if isinstance(self.anySelection[idx], str) else str(self.anySelection[idx]))

                if len(details) == 0:
                    details = None
                else:
                    details = ' '.join(details)

                if seq_id is None or len(atom_ids) == 0:
                    return

                _seq_id = seq_id
                auth_seq_id_map = {}

                for atom_id, value, value_uncertainty, occupancy, figure_of_merit in zip(atom_ids, values, value_uncertainties, occupancies, figure_of_merits):
                    self.atomSelectionSets.clear()

                    dstFunc = self.validateCsValue(self.cur_line_num, value, value_uncertainty, occupancy, figure_of_merit)

                    if dstFunc is None:
                        continue

                    self.predictSequenceNumberOffsetByFirstResidue(chain_id, _seq_id, comp_id)

                    if chain_id in self.offset:
                        seq_id = _seq_id + self.offset[chain_id]
                        auth_seq_id_map[seq_id] = _seq_id

                    L = concat_assignment(chain_id, seq_id, comp_id, atom_id)

                    assignment = self.extractAssignment(1, L, self.cur_line_num, chain_id, comp_id)

                    if assignment is None:
                        continue

                    has_assignments, has_multiple_assignments = self.checkAssignment(self.cur_line_num, assignment)

                    self.addCsRow(self.cur_line_num, dstFunc, has_assignments, has_multiple_assignments, auth_seq_id_map,
                                  f'{L} -> ', details)

                    self.chemShifts += 1

            else:

                chain_id = None
                assignments, values, value_uncertainties, occupancies, figure_of_merits, details = [], [], [], [], [], []

                for idx in range(len_any):
                    if idx < len_ord:
                        order = self.__col_order[idx]
                        if order == 'chain_code':
                            if isinstance(self.anySelection[idx], str):
                                chain_id = self.anySelection[idx]
                            elif isinstance(self.anySelection[idx], int):
                                chain_id = str(self.anySelection[idx])
                        elif order == 'assignment':
                            if isinstance(self.anySelection[idx], str):
                                assignments.append(self.anySelection[idx])
                        elif order == 'value':
                            value = self.anySelection[idx]
                            if isinstance(value, float):
                                if self.validateCsValue(self.cur_list_id, value, None) is not None:
                                    values.append(self.anySelection[idx])
                                elif len(atom_ids) > len(values):
                                    del atom_ids[-1]
                            elif isinstance(value, int):
                                value = float(value)
                                if self.validateCsValue(self.cur_list_id, value, None) is not None:
                                    values.append(self.anySelection[idx])
                                elif len(atom_ids) > len(values):
                                    del atom_ids[-1]
                            elif len(atom_ids) > len(values):
                                del atom_ids[-1]
                        elif order == 'value_uncertainty':
                            if len(values) - 1 == len(value_uncertainties):
                                value_uncertainty = self.anySelection[idx]
                                if isinstance(value_uncertainty, float):
                                    value_uncertainties.append(value_uncertainty)
                                else:
                                    value_uncertainties.append(None)
                        elif order == 'occupancy':
                            if len(values) - 1 == len(occupancies):
                                occupancy = self.anySelection[idx]
                                if isinstance(occupancy, float):
                                    occupancies.append(occupancy)
                                else:
                                    occupancies.append(None)
                        elif order == 'figure_of_merit':
                            if len(values) - 1 == len(figure_of_merits):
                                figure_of_merit = self.anySelection[idx]
                                if isinstance(figure_of_merit, float):
                                    figure_of_merits.append(figure_of_merit)
                                else:
                                    figure_of_merits.append(None)
                        elif order == 'details':
                            details.append(self.anySelection[idx] if isinstance(self.anySelection[idx], str) else str(self.anySelection[idx]))
                    elif self.__col_order[len_ord - 1] == 'details':
                        details.append(self.anySelection[idx] if isinstance(self.anySelection[idx], str) else str(self.anySelection[idx]))

                if len(details) == 0:
                    details = None
                else:
                    details = ' '.join(details)

                if len(assignments) == 0:
                    return

                for L, value, value_uncertainty, occupancy, figure_of_merit in zip(assignments, values, value_uncertainties, occupancies, figure_of_merits):
                    self.atomSelectionSets.clear()

                    dstFunc = self.validateCsValue(self.cur_line_num, value, value_uncertainty, occupancy, figure_of_merit)

                    if dstFunc is None:
                        continue

                    if chain_id is not None:
                        L = f'{chain_id}:{L}'

                    assignment = self.extractAssignment(1, L, self.cur_line_num, chain_id)

                    if assignment is None:
                        continue

                    has_assignments, has_multiple_assignments = self.checkAssignment(self.cur_line_num, assignment)

                    self.addCsRow(self.cur_line_num, dstFunc, has_assignments, has_multiple_assignments, {},
                                  f'{L} -> ', details)

                    self.chemShifts += 1

        finally:
            self.anySelection.clear()

    # Enter a parse tree produced by BareCSParser#any.
    def enterAny(self, ctx: BareCSParser.AnyContext):

        try:

            if ctx.Float():
                value = str(ctx.Float())
                self.anySelection.append(float(value))

            elif ctx.Integer():
                value = str(ctx.Integer())
                self.anySelection.append(int(value))

            elif ctx.Simple_name():
                self.anySelection.append(str(ctx.Simple_name()))

            elif ctx.Double_quote_float():
                value = str(ctx.Double_quote_float()).strip('"')
                self.anySelection.append(float(value))

            elif ctx.Double_quote_integer():
                value = str(ctx.Double_quote_integer()).strip('"')
                self.anySelection.append(int(value))

            else:
                self.anySelection.append(str(ctx.Double_quote_string()).strip('"'))

        except ValueError:
            self.anySelection.append(None)

    # Exit a parse tree produced by BareCSParser#any.
    def exitAny(self, ctx: BareCSParser.AnyContext):  # pylint: disable=unused-argument
        pass


# del BareCSParser
