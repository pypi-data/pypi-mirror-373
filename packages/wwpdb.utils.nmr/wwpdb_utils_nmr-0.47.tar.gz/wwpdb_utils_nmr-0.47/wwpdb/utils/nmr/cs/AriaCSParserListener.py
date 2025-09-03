##
# File: AriaCSParserListener.py
# Date: 10-Apr-2025
#
# Updates:
""" ParserLister class for ARIA CS files.
    @author: Masashi Yokochi
    @see: https://aria-test.pasteur.fr/documentation/input-format/version-2.1/chemical_shift_list
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
    from wwpdb.utils.nmr.pk.XMLParser import XMLParser
    from wwpdb.utils.nmr.cs.BaseCSParserListener import BaseCSParserListener
    from wwpdb.utils.nmr.ChemCompUtil import ChemCompUtil
    from wwpdb.utils.nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from wwpdb.utils.nmr.nef.NEFTranslator import NEFTranslator
except ImportError:
    from nmr.pk.XMLParser import XMLParser
    from nmr.cs.BaseCSParserListener import BaseCSParserListener
    from nmr.ChemCompUtil import ChemCompUtil
    from nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from nmr.nef.NEFTranslator import NEFTranslator


# This class defines a complete listener for a parse tree produced by XMLParser.
class AriaCSParserListener(ParseTreeListener, BaseCSParserListener):

    __cur_path = None

    __method = None

    __spin_system = None
    # __averaging_method = None

    __atom = None
    __segid = None
    __residue = None
    __name = None

    __chemical_shift = None
    __value = None
    __error = None

    def __init__(self, verbose: bool = True, log: IO = sys.stdout,
                 polySeq: List[dict] = None, entityAssembly: Optional[dict] = None,
                 ccU: Optional[ChemCompUtil] = None, csStat: Optional[BMRBChemShiftStat] = None, nefT: Optional[NEFTranslator] = None,
                 reasons: Optional[dict] = None):
        super().__init__(verbose, log, polySeq, entityAssembly, ccU, csStat, nefT, reasons)

        self.file_type = 'nm-shi-ari'
        self.software_name = 'ARIA'

    # Enter a parse tree produced by XMLParser#document.
    def enterDocument(self, ctx: XMLParser.DocumentContext):  # pylint: disable=unused-argument
        self.__cur_path = ''

        self.enter()

    # Exit a parse tree produced by XMLParser#document.
    def exitDocument(self, ctx: XMLParser.DocumentContext):  # pylint: disable=unused-argument
        self.exit()

    # Enter a parse tree produced by XMLParser#prolog.
    def enterProlog(self, ctx: XMLParser.PrologContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by XMLParser#prolog.
    def exitProlog(self, ctx: XMLParser.PrologContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by XMLParser#content.
    def enterContent(self, ctx: XMLParser.ContentContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by XMLParser#content.
    def exitContent(self, ctx: XMLParser.ContentContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by XMLParser#element.
    def enterElement(self, ctx: XMLParser.ElementContext):
        self.__cur_path += '/' + str(ctx.Name(0))

        if self.__cur_path == '/chemical_shift_list':
            self.cur_subtype = 'chem_shift'

            self.cur_list_id = max(self.cur_list_id, 0)
            self.cur_list_id += 1

            self.chemShifts = 0
            self.offset = {}

        elif self.__cur_path == '/chemical_shift_list/shift_assignment':
            self.__spin_system = []

        elif self.__cur_path == '/chemical_shift_list/shift_assignment/spin_system':
            self.__atom = []
            self.__chemical_shift = []

        elif self.__cur_path == '/chemical_shift_list/shift_assignment/spin_system/atom':
            self.__segid = None
            self.__residue = None
            self.__name = None

        elif self.__cur_path == '/chemical_shift_list/shift_assignment/spin_system/chemical_shift':
            self.__value = None
            self.__error = None

    # Exit a parse tree produced by XMLParser#element.
    def exitElement(self, ctx: XMLParser.ElementContext):  # pylint: disable=unused-argument

        try:

            if self.__cur_path == '/chemical_shift_list':
                pass

            elif self.__cur_path == '/chemical_shift_list/shift_assignment':

                def concat_assignment(a):
                    chain_id = a['segid']
                    if chain_id is not None:
                        L = f"{chain_id}:{str(a['residue'])}:{a['name']}"
                    else:
                        L = f"{str(a['residue'])}:{a['name']}"
                    return chain_id, L

                try:

                    if len(self.__spin_system) == 0:
                        return

                    auth_seq_id_map = {}

                    index = self.chemShifts + 1

                    if self.__method == 'EQUIVALENT':

                        spin_system = self.__spin_system[0]

                        chemical_shift = spin_system['chemical_shift'][0]

                        value = chemical_shift['value']
                        error = chemical_shift['error']

                        dstFunc = self.validateCsValue(index, value, error)

                        if dstFunc is None:
                            return

                        auth_seq_id_map.clear()

                        for atom in spin_system['atom']:
                            self.atomSelectionSets.clear()

                            self.predictSequenceNumberOffsetByFirstResidue(None, atom['residue'], None)
                            if None in self.offset:
                                _residue = atom['residue']
                                atom['residue'] += self.offset[None]
                                auth_seq_id_map[_residue] = atom['residue']

                            chain_id, L = concat_assignment(atom)

                            assignment = self.extractAssignment(1, L, index, chain_id)

                            if assignment is None:
                                continue

                            _atom = assignment[0]  # pylint: disable=unsubscriptable-object
                            ambig_code = self.csStat.getMaxAmbigCodeWoSetId(_atom['comp_id'], _atom['atom_id'])
                            if ambig_code == 0:
                                ambig_code = None

                            has_assignments, has_multiple_assignments = self.checkAssignment(index, assignment)

                            self.addCsRow(index, dstFunc, has_assignments, has_multiple_assignments, auth_seq_id_map,
                                          f'{L} -> ', None, ambig_code)

                            self.chemShifts += 1

                    elif self.__method == 'FLOATING':

                        segids = set()
                        residues = set()
                        for spin_system in self.__spin_system:
                            for atom in spin_system['atom']:
                                if atom['segid'] is not None:
                                    segids.add(atom['segid'])
                                residues.add(atom['residue'])
                        if len(segids) > 1:
                            max_ambig_code = 6
                        elif len(residues) > 1:
                            max_ambig_code = 5
                        else:
                            max_ambig_code_in_res = 0
                            for spin_system in self.__spin_system:
                                for atom in spin_system['atom']:

                                    self.predictSequenceNumberOffsetByFirstResidue(None, atom['residue'], None)
                                    if None in self.offset:
                                        atom['residue'] += self.offset[None]

                                    chain_id, L = concat_assignment(atom)

                                    assignment = self.extractAssignment(1, L, index, chain_id)

                                    if assignment is None:
                                        continue

                                    _atom = assignment[0]  # pylint: disable=unsubscriptable-object
                                    ambig_code = self.csStat.getMaxAmbigCodeWoSetId(_atom['comp_id'], _atom['atom_id'])
                                    max_ambig_code_in_res = max(max_ambig_code_in_res, ambig_code)
                            if max_ambig_code_in_res > 1:
                                max_ambig_code = max_ambig_code_in_res
                            else:
                                max_ambig_code = 4

                        for idx, spin_system in enumerate(self.__spin_system):

                            if idx < len(spin_system['chemical_shift']):
                                chemical_shift = spin_system['chemical_shift'][idx]
                            else:
                                chemical_shift = spin_system['chemical_shift'][0]

                            value = chemical_shift['value']
                            error = chemical_shift['error']

                            dstFunc = self.validateCsValue(index, value, error)

                            if dstFunc is None:
                                continue

                            auth_seq_id_map.clear()

                            for atom in spin_system['atom']:
                                self.atomSelectionSets.clear()

                                self.predictSequenceNumberOffsetByFirstResidue(None, atom['residue'], None)
                                if None in self.offset:
                                    _residue = atom['residue']
                                    atom['residue'] += self.offset[None]
                                    auth_seq_id_map[_residue] = atom['residue']

                                chain_id, L = concat_assignment(atom)

                                assignment = self.extractAssignment(1, L, index, chain_id)

                                if assignment is None:
                                    continue

                                has_assignments, has_multiple_assignments = self.checkAssignment(index, assignment)

                                self.addCsRow(index, dstFunc, has_assignments, has_multiple_assignments, auth_seq_id_map,
                                              f'{L} -> ', None, max_ambig_code)

                                self.chemShifts += 1

                    else:  # "STEREO_SPECIFIC"

                        spin_system = self.__spin_system[0]

                        chemical_shift = spin_system['chemical_shift'][0]

                        value = chemical_shift['value']
                        error = chemical_shift['error']

                        dstFunc = self.validateCsValue(index, value, error)

                        if dstFunc is None:
                            return

                        auth_seq_id_map.clear()

                        atom = spin_system['atom'][0]

                        self.atomSelectionSets.clear()

                        self.predictSequenceNumberOffsetByFirstResidue(None, atom['residue'], None)
                        if None in self.offset:
                            _residue = atom['residue']
                            atom['residue'] += self.offset[None]
                            auth_seq_id_map[_residue] = atom['residue']

                        chain_id, L = concat_assignment(atom)

                        assignment = self.extractAssignment(1, L, index, chain_id)

                        if assignment is None:
                            return

                        has_assignments, has_multiple_assignments = self.checkAssignment(index, assignment)

                        self.addCsRow(index, dstFunc, has_assignments, has_multiple_assignments, auth_seq_id_map,
                                      f'{L} -> ')

                        self.chemShifts += 1

                finally:
                    self.__method = None

            elif self.__cur_path == '/chemical_shift_list/shift_assignment/spin_system':
                if len(self.__atom) > 0 and len(self.__chemical_shift) > 0:
                    self.__spin_system.append({'atom': self.__atom, 'chemical_shift': self.__chemical_shift})

            elif self.__cur_path == '/chemical_shift_list/shift_assignment/spin_system/atom':
                if self.__residue is not None and self.__name is not None:
                    self.__atom.append({'segid': self.__segid, 'residue': self.__residue, 'name': self.__name})

            elif self.__cur_path == '/chemical_shift_list/shift_assignment/spin_system/chemical_shift':
                if self.__value is not None:
                    self.__chemical_shift.append({'value': self.__value, 'error': self.__error})

        finally:
            self.__cur_path = self.__cur_path[:-(1 + len(str(ctx.Name(0))))]

    # Enter a parse tree produced by XMLParser#reference.
    def enterReference(self, ctx: XMLParser.ReferenceContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by XMLParser#reference.
    def exitReference(self, ctx: XMLParser.ReferenceContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by XMLParser#attribute.
    def enterAttribute(self, ctx: XMLParser.AttributeContext):

        if ctx.Name() and ctx.STRING():
            name = str(ctx.Name())
            string = str(ctx.STRING())[1:-1].strip()

            if self.__cur_path == '/chemical_shift_list':
                pass

            elif self.__cur_path == '/chemical_shift_list/shift_assignment':

                if name == 'method':
                    self.__method = string

            elif self.__cur_path == '/chemical_shift_list/shift_assignment/spin_system':
                pass
                # if name == 'averaging_method':
                #     self.__averaging_method = string

            elif self.__cur_path == '/chemical_shift_list/shift_assignment/spin_system/atom':

                if name == 'segid' and len(string) > 0:
                    self.__segid = string

                elif name == 'residue' and string.isdigit():
                    self.__residue = int(string)

                elif name == 'name' and len(string) > 0:
                    self.__name = string

            elif self.__cur_path == '/chemical_shift_list/shift_assignment/spin_system/chemical_shift':

                if name == 'value' and len(string) > 0:
                    try:
                        self.__value = float(string)
                    except ValueError:
                        pass

                elif name == 'error' and len(string) > 0:
                    try:
                        self.__error = float(string)
                    except ValueError:
                        pass

    # Exit a parse tree produced by XMLParser#attribute.
    def exitAttribute(self, ctx: XMLParser.AttributeContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by XMLParser#chardata.
    def enterChardata(self, ctx: XMLParser.ChardataContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by XMLParser#chardata.
    def exitChardata(self, ctx: XMLParser.ChardataContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by XMLParser#misc.
    def enterMisc(self, ctx: XMLParser.MiscContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by XMLParser#misc.
    def exitMisc(self, ctx: XMLParser.MiscContext):  # pylint: disable=unused-argument
        pass
