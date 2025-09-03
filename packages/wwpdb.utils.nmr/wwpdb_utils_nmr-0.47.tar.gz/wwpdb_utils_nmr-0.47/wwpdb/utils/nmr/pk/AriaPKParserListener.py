##
# File: AriaPKParserListener.py
# Date: 05-Dec-2024
#
# Updates:
""" ParserLister class for ARIA PK files.
    @author: Masashi Yokochi
    @see: https://aria-test.pasteur.fr/documentation/input-format/version-2.1/spectrum
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
    from wwpdb.utils.nmr.io.CifReader import CifReader
    from wwpdb.utils.nmr.pk.XMLParser import XMLParser
    from wwpdb.utils.nmr.pk.BasePKParserListener import BasePKParserListener
    from wwpdb.utils.nmr.mr.ParserListenerUtil import (REPRESENTATIVE_MODEL_ID,
                                                       REPRESENTATIVE_ALT_ID)
    from wwpdb.utils.nmr.ChemCompUtil import ChemCompUtil
    from wwpdb.utils.nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from wwpdb.utils.nmr.nef.NEFTranslator import NEFTranslator
except ImportError:
    from nmr.io.CifReader import CifReader
    from nmr.pk.XMLParser import XMLParser
    from nmr.pk.BasePKParserListener import BasePKParserListener
    from nmr.mr.ParserListenerUtil import (REPRESENTATIVE_MODEL_ID,
                                           REPRESENTATIVE_ALT_ID)
    from nmr.ChemCompUtil import ChemCompUtil
    from nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from nmr.nef.NEFTranslator import NEFTranslator


# This class defines a complete listener for a parse tree produced by XMLParser.
class AriaPKParserListener(ParseTreeListener, BasePKParserListener):

    __cur_path = None

    __spectrum_names = None

    __index = None
    __proton1_ppm = None
    __proton1_ppm_error = None
    __proton1_ass = None
    __proton1_atoms = None
    __proton2_ppm = None
    __proton2_ppm_error = None
    __proton2_ass = None
    __proton2_atoms = None
    __hetero1_ppm = None
    __hetero1_ppm_error = None
    __hetero1_ass = None
    __hetero1_atoms = None
    __hetero2_ppm = None
    __hetero2_ppm_error = None
    __hetero2_ass = None
    __hetero2_atoms = None
    __intensity = None
    __intensity_error = None
    __volume = None
    __volume_error = None

    __proton1_active = False
    __proton2_active = False
    __hetero1_active = False
    __hetero2_active = False

    def __init__(self, verbose: bool = True, log: IO = sys.stdout,
                 representativeModelId: int = REPRESENTATIVE_MODEL_ID,
                 representativeAltId: str = REPRESENTATIVE_ALT_ID,
                 mrAtomNameMapping: Optional[List[dict]] = None,
                 cR: Optional[CifReader] = None, caC: Optional[dict] = None, ccU: Optional[ChemCompUtil] = None,
                 csStat: Optional[BMRBChemShiftStat] = None, nefT: Optional[NEFTranslator] = None,
                 reasons: Optional[dict] = None):
        super().__init__(verbose, log, representativeModelId, representativeAltId,
                         mrAtomNameMapping, cR, caC, ccU, csStat, nefT, reasons)

        self.file_type = 'nm-pea-ari'
        self.software_name = 'ARIA'

    # Enter a parse tree produced by XMLParser#document.
    def enterDocument(self, ctx: XMLParser.DocumentContext):  # pylint: disable=unused-argument
        self.__cur_path = ''
        self.__spectrum_names = {}

        self.enter()

    # Exit a parse tree produced by XMLParser#document.
    def exitDocument(self, ctx: XMLParser.DocumentContext):  # pylint: disable=unused-argument
        self.exit(self.__spectrum_names if len(self.__spectrum_names) > 0 else None)

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

        if self.__cur_path == '/spectrum':
            self.num_of_dim = -1
            self.spectrum_name = None

        elif self.__cur_path == '/spectrum/peak':
            self.__volume = None
            self.__volume_error = None
            self.__intensity = None
            self.__intensity_error = None

        elif self.__cur_path == '/spectrum/peak/proton1':
            self.__proton1_ppm = None
            self.__proton1_ppm_error = None
            self.__proton1_atoms = None

        elif self.__cur_path == '/spectrum/peak/proton2':
            self.__proton2_ppm = None
            self.__proton2_ppm_error = None
            self.__proton2_atoms = None

        elif self.__cur_path == '/spectrum/peak/hetero1':
            self.__hetero1_ppm = None
            self.__hetero1_ppm_error = None
            self.__hetero1_atoms = None

        elif self.__cur_path == '/spectrum/peak/hetero2':
            self.__hetero2_ppm = None
            self.__hetero2_ppm_error = None
            self.__hetero2_atoms = None

        elif self.__cur_path == '/spectrum/peak/proton1/assignment':
            self.__proton1_atoms = []

        elif self.__cur_path == '/spectrum/peak/proton2/assignment':
            self.__proton2_atoms = []

        elif self.__cur_path == '/spectrum/peak/hetero1/assignment':
            self.__hetero1_atoms = []

        elif self.__cur_path == '/spectrum/peak/hetero2/assignment':
            self.__hetero2_atoms = []

        elif self.__cur_path == '/spectrum/peak/proton1/assignment/atom':
            self.__proton1_ass = {}

        elif self.__cur_path == '/spectrum/peak/proton2/assignment/atom':
            self.__proton2_ass = {}

        elif self.__cur_path == '/spectrum/peak/hetero1/assignment/atom':
            self.__hetero1_ass = {}

        elif self.__cur_path == '/spectrum/peak/hetero2/assignment/atom':
            self.__hetero2_ass = {}

    # Exit a parse tree produced by XMLParser#element.
    def exitElement(self, ctx: XMLParser.ElementContext):  # pylint: disable=unused-argument

        if self.__cur_path == '/spectrum':
            self.num_of_dim = -1
            self.__proton1_active, self.__proton2_active, self.__hetero1_active, self.__hetero2_active =\
                False, False, False, False

        elif self.__cur_path == '/spectrum/peak':
            if self.num_of_dim == -1:
                self.num_of_dim = 0
                if self.__proton1_ppm is not None:
                    self.num_of_dim += 1
                    self.__proton1_active = True
                if self.__proton2_ppm is not None:
                    self.num_of_dim += 1
                    self.__proton2_active = True
                if self.__hetero1_ppm is not None:
                    self.num_of_dim += 1
                    self.__hetero1_active = True
                if self.__hetero2_ppm is not None:
                    self.num_of_dim += 1
                    self.__hetero2_active = True
                self.initSpectralDim()
                if self.num_of_dim not in self.__spectrum_names:
                    self.__spectrum_names[self.num_of_dim] = {}
                if self.cur_list_id not in self.__spectrum_names[self.num_of_dim]:
                    self.__spectrum_names[self.num_of_dim][self.cur_list_id] = self.spectrum_name

            index = self.__index

            ppm = [None] * self.num_of_dim
            ppm_error = [None] * self.num_of_dim
            assignments = [None] * self.num_of_dim

            idx = 0
            if self.__proton1_active:
                ppm[idx] = self.__proton1_ppm
                ppm_error[idx] = self.__proton1_ppm_error
                if self.__proton1_atoms is not None:
                    assignments[idx] = self.__proton1_atoms
                    if len(self.__proton1_atoms) > 1:
                        if self.createSfDict__ and self.use_peak_row_format:
                            sf = self.getSf()
                            sf['peak_row_format'] = self.use_peak_row_format = False
                idx += 1
            if self.__proton2_active:
                ppm[idx] = self.__proton2_ppm
                ppm_error[idx] = self.__proton2_ppm_error
                if self.__proton2_atoms is not None:
                    assignments[idx] = self.__proton2_atoms
                    if len(self.__proton2_atoms) > 1:
                        if self.createSfDict__ and self.use_peak_row_format:
                            sf = self.getSf()
                            sf['peak_row_format'] = self.use_peak_row_format = False
                idx += 1
            if self.__hetero1_active:
                ppm[idx] = self.__hetero1_ppm
                ppm_error[idx] = self.__hetero1_ppm_error
                if self.__hetero1_atoms is not None:
                    assignments[idx] = self.__hetero1_atoms
                    if len(self.__hetero1_atoms) > 1:
                        if self.createSfDict__ and self.use_peak_row_format:
                            sf = self.getSf()
                            sf['peak_row_format'] = self.use_peak_row_format = False
                idx += 1
            if self.__hetero2_active:
                ppm[idx] = self.__hetero2_ppm
                ppm_error[idx] = self.__hetero2_ppm_error
                if self.__hetero2_atoms is not None:
                    assignments[idx] = self.__hetero2_atoms
                    if len(self.__hetero2_atoms) > 1:
                        if self.createSfDict__ and self.use_peak_row_format:
                            sf = self.getSf()
                            sf['peak_row_format'] = self.use_peak_row_format = False

            if not all(a is not None and len(a) >= 1 and 'seq_id' in a[0] and 'atom_id' in a[0] for a in assignments):
                assignments = [None] * self.num_of_dim

            if self.num_of_dim == 2:
                self.peaks2D += 1

                if None in (ppm[0], ppm[1])\
                   or (self.__intensity is None and self.__volume is None):
                    self.peaks2D -= 1
                    return

                dstFunc = self.validatePeak2D(index, ppm[0], ppm[1],
                                              ppm_error[0], ppm_error[1],
                                              None, None, None, None, None, None,
                                              self.__intensity, self.__intensity_error, self.__volume, self.__volume_error)

                if dstFunc is None:
                    self.peaks2D -= 1
                    return

                cur_spectral_dim = self.spectral_dim[self.num_of_dim][self.cur_list_id]

                cur_spectral_dim[1]['freq_hint'].append(ppm[0])
                cur_spectral_dim[2]['freq_hint'].append(ppm[1])

                has_assignments, has_multiple_assignments, asis1, asis2 =\
                    self.checkAssignments2D(index, assignments, dstFunc)

                self.addAssignedPkRow2D(index, dstFunc, has_assignments, has_multiple_assignments,
                                        asis1, asis2,
                                        '', None)

            elif self.num_of_dim == 3:
                self.peaks3D += 1

                if None in (ppm[0], ppm[1], ppm[2])\
                   or (self.__intensity is None and self.__volume is None):
                    self.peaks3D -= 1
                    return

                dstFunc = self.validatePeak3D(index, ppm[0], ppm[1], ppm[2],
                                              ppm_error[0], ppm_error[1], ppm_error[2],
                                              None, None, None, None, None, None, None, None, None,
                                              self.__intensity, self.__intensity_error, self.__volume, self.__volume_error)

                if dstFunc is None:
                    self.peaks3D -= 1
                    return

                cur_spectral_dim = self.spectral_dim[self.num_of_dim][self.cur_list_id]

                cur_spectral_dim[1]['freq_hint'].append(ppm[0])
                cur_spectral_dim[2]['freq_hint'].append(ppm[1])
                cur_spectral_dim[3]['freq_hint'].append(ppm[2])

                has_assignments, has_multiple_assignments, asis1, asis2, asis3 =\
                    self.checkAssignments3D(index, assignments, dstFunc)

                self.addAssignedPkRow3D(index, dstFunc, has_assignments, has_multiple_assignments,
                                        asis1, asis2, asis3,
                                        '', None)

            elif self.num_of_dim == 4:
                self.peaks4D += 1

                if None in (ppm[0], ppm[1], ppm[2], ppm[3])\
                   or (self.__intensity is None and self.__volume is None):
                    self.peaks4D -= 1
                    return

                dstFunc = self.validatePeak4D(index, ppm[0], ppm[1], ppm[2], ppm[3],
                                              ppm_error[0], ppm_error[1], ppm_error[2], ppm_error[3],
                                              None, None, None, None, None, None, None, None, None, None, None, None,
                                              self.__intensity, self.__intensity_error, self.__volume, self.__volume_error)

                if dstFunc is None:
                    self.peaks4D -= 1
                    return

                cur_spectral_dim = self.spectral_dim[self.num_of_dim][self.cur_list_id]

                cur_spectral_dim[1]['freq_hint'].append(ppm[0])
                cur_spectral_dim[2]['freq_hint'].append(ppm[1])
                cur_spectral_dim[3]['freq_hint'].append(ppm[2])
                cur_spectral_dim[4]['freq_hint'].append(ppm[3])

                has_assignments, has_multiple_assignments, asis1, asis2, asis3, asis4 =\
                    self.checkAssignments4D(index, assignments, dstFunc)

                self.addAssignedPkRow4D(index, dstFunc, has_assignments, has_multiple_assignments,
                                        asis1, asis2, asis3, asis4,
                                        '', None)

        elif self.__cur_path == '/spectrum/peak/proton1/assignment/atom':
            if len(self.__proton1_ass) > 0:
                self.__proton1_atoms.append(self.__proton1_ass)

        elif self.__cur_path == '/spectrum/peak/proton2/assignment/atom':
            if len(self.__proton2_ass) > 0:
                self.__proton2_atoms.append(self.__proton2_ass)

        elif self.__cur_path == '/spectrum/peak/hetero1/assignment/atom':
            if len(self.__hetero1_ass) > 0:
                self.__hetero1_atoms.append(self.__hetero1_ass)

        elif self.__cur_path == '/spectrum/peak/hetero2/assignment/atom':
            if len(self.__hetero2_ass) > 0:
                self.__hetero2_atoms.append(self.__hetero2_ass)

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

            if self.__cur_path == '/spectrum':

                if name == 'name':
                    self.spectrum_name = string

            elif self.__cur_path == '/spectrum/peak':

                if name == 'number':
                    self.__index = int(string)

            elif self.__cur_path == '/spectrum/peak/volume':

                if name == 'value':
                    self.__volume = string

                elif name == 'error' and len(string) > 0:
                    self.__volume_error = string

            elif self.__cur_path == '/spectrum/peak/intensity':

                if name == 'value':
                    self.__intensity = string

                elif name == 'error' and len(string) > 0:
                    self.__intensity_error = string

            elif self.__cur_path == '/spectrum/peak/proton1/shift' and len(string) > 0:

                if string == self.__volume:
                    self.__volume = None

                if string == self.__intensity:
                    self.__intensity = None

                if name == 'value':
                    self.__proton1_ppm = float(string)

                elif name == 'error':
                    self.__proton1_ppm_error = float(string)

            elif self.__cur_path == '/spectrum/peak/proton2/shift' and len(string) > 0:

                if string == self.__volume:
                    self.__volume = None

                if string == self.__intensity:
                    self.__intensity = None

                if name == 'value':
                    self.__proton2_ppm = float(string)

                elif name == 'error':
                    self.__proton2_ppm_error = float(string)

            elif self.__cur_path == '/spectrum/peak/hetero1/shift' and len(string) > 0:

                if string == self.__volume:
                    self.__volume = None

                if string == self.__intensity:
                    self.__intensity = None

                if name == 'value':
                    self.__hetero1_ppm = float(string)

                elif name == 'error':
                    self.__hetero1_ppm_error = float(string)

            elif self.__cur_path == '/spectrum/peak/hetero2/shift' and len(string) > 0:

                if string == self.__volume:
                    self.__volume = None

                if string == self.__intensity:
                    self.__intensity = None

                if name == 'value':
                    self.__hetero2_ppm = float(string)

                elif name == 'error':
                    self.__hetero2_ppm_error = float(string)

            elif self.__cur_path == '/spectrum/peak/proton1/assignment/atom' and len(string) > 0:

                if name == 'segid':
                    self.__proton1_ass['chain_id'] = string

                elif name == 'residue':
                    self.__proton1_ass['seq_id'] = string

                elif name == 'name':
                    self.__proton1_ass['atom_id'] = string

            elif self.__cur_path == '/spectrum/peak/proton2/assignment/atom' and len(string) > 0:

                if name == 'segid':
                    self.__proton2_ass['chain_id'] = string

                elif name == 'residue':
                    self.__proton2_ass['seq_id'] = string

                elif name == 'name':
                    self.__proton2_ass['atom_id'] = string

            elif self.__cur_path == '/spectrum/peak/hetero1/assignment/atom' and len(string) > 0:

                if name == 'segid':
                    self.__hetero1_ass['chain_id'] = string

                elif name == 'residue':
                    self.__hetero1_ass['seq_id'] = string

                elif name == 'name':
                    self.__hetero1_ass['atom_id'] = string

            elif self.__cur_path == '/spectrum/peak/hetero2/assignment/atom' and len(string) > 0:

                if name == 'segid':
                    self.__hetero2_ass['chain_id'] = string

                elif name == 'residue':
                    self.__hetero2_ass['seq_id'] = string

                elif name == 'name':
                    self.__hetero2_ass['atom_id'] = string

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
