##
# File: PonderosaPKParserListener.py
# Date: 18-Feb-2025
#
# Updates:
""" ParserLister class for PONDEROSA PK files.
    @author: Masashi Yokochi
"""
__docformat__ = "restructuredtext en"
__author__ = "Masashi Yokochi"
__email__ = "yokochi@protein.osaka-u.ac.jp"
__license__ = "Apache License 2.0"
__version__ = "1.0.0"

import sys
import copy

from antlr4 import ParseTreeListener
from typing import IO, List, Optional

try:
    from wwpdb.utils.nmr.io.CifReader import CifReader
    from wwpdb.utils.nmr.pk.PonderosaPKParser import PonderosaPKParser
    from wwpdb.utils.nmr.pk.BasePKParserListener import BasePKParserListener
    from wwpdb.utils.nmr.mr.ParserListenerUtil import (REPRESENTATIVE_MODEL_ID,
                                                       REPRESENTATIVE_ALT_ID,
                                                       SPECTRAL_DIM_TEMPLATE,
                                                       ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS)
    from wwpdb.utils.nmr.ChemCompUtil import ChemCompUtil
    from wwpdb.utils.nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from wwpdb.utils.nmr.nef.NEFTranslator import NEFTranslator
    from wwpdb.utils.nmr.AlignUtil import emptyValue
except ImportError:
    from nmr.io.CifReader import CifReader
    from nmr.pk.PonderosaPKParser import PonderosaPKParser
    from nmr.pk.BasePKParserListener import BasePKParserListener
    from nmr.mr.ParserListenerUtil import (REPRESENTATIVE_MODEL_ID,
                                           REPRESENTATIVE_ALT_ID,
                                           SPECTRAL_DIM_TEMPLATE,
                                           ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS)
    from nmr.ChemCompUtil import ChemCompUtil
    from nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from nmr.nef.NEFTranslator import NEFTranslator
    from nmr.AlignUtil import emptyValue


# This class defines a complete listener for a parse tree produced by PonderosaPKParser.
class PonderosaPKParserListener(ParseTreeListener, BasePKParserListener):

    __spectrum_names = None

    def __init__(self, verbose: bool = True, log: IO = sys.stdout,
                 representativeModelId: int = REPRESENTATIVE_MODEL_ID,
                 representativeAltId: str = REPRESENTATIVE_ALT_ID,
                 mrAtomNameMapping: Optional[List[dict]] = None,
                 cR: Optional[CifReader] = None, caC: Optional[dict] = None, ccU: Optional[ChemCompUtil] = None,
                 csStat: Optional[BMRBChemShiftStat] = None, nefT: Optional[NEFTranslator] = None,
                 reasons: Optional[dict] = None):
        super().__init__(verbose, log, representativeModelId, representativeAltId,
                         mrAtomNameMapping, cR, caC, ccU, csStat, nefT, reasons)

        self.file_type = 'nm-pea-pon'
        self.software_name = 'PONDEROSA'

    # Enter a parse tree produced by PonderosaPKParser#ponderosa_pk.
    def enterPonderosa_pk(self, ctx: PonderosaPKParser.Ponderosa_pkContext):  # pylint: disable=unused-argument
        self.__spectrum_names = {}

        self.enter()

    # Exit a parse tree produced by PonderosaPKParser#ponderosa_pk.
    def exitPonderosa_pk(self, ctx: PonderosaPKParser.Ponderosa_pkContext):  # pylint: disable=unused-argument
        self.exit(self.__spectrum_names if len(self.__spectrum_names) > 0 else None)

    # Enter a parse tree produced by PonderosaPKParser#peak_list_2d.
    def enterPeak_list_2d(self, ctx: PonderosaPKParser.Peak_list_2dContext):
        self.num_of_dim = 2

        axis_order = str(ctx.Simple_name_AO())

        if len(axis_order) == self.num_of_dim:

            for _dim_id, _axis_code in enumerate(axis_order, start=1):
                if _dim_id not in self.cur_spectral_dim:
                    cur_spectral_dim = copy.copy(SPECTRAL_DIM_TEMPLATE)
                else:
                    cur_spectral_dim = self.cur_spectral_dim[_dim_id]

                cur_spectral_dim['axis_code'] = cur_spectral_dim['axis_order'] = _axis_code

                for a in _axis_code:
                    a = a.upper()
                    if a in ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS:
                        cur_spectral_dim['atom_type'] = a
                        cur_spectral_dim['atom_isotope_number'] = ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS[a][0]
                        break

                isotope_number = cur_spectral_dim['atom_isotope_number']

                cur_spectral_dim['acquisition'] = 'yes' if _dim_id == self.acq_dim_id\
                    and (isotope_number == 1 or (isotope_number == 13 and self.exptlMethod == 'SOLID-STATE NMR')) else 'no'

                if _dim_id == 1 and cur_spectral_dim['acquisition'] == 'no':
                    self.acq_dim_id = self.num_of_dim

                cur_spectral_dim['under_sampling_type'] = 'not observed' if cur_spectral_dim['acquisition'] == 'yes' else 'aliased'

                self.cur_spectral_dim[_dim_id] = cur_spectral_dim

        self.initSpectralDim()

        if self.num_of_dim not in self.__spectrum_names:
            self.__spectrum_names[self.num_of_dim] = {}
        if self.cur_list_id not in self.__spectrum_names[self.num_of_dim]:
            self.__spectrum_names[self.num_of_dim][self.cur_list_id] = str(ctx.Simple_name_NT())

    # Exit a parse tree produced by PonderosaPKParser#peak_list_2d.
    def exitPeak_list_2d(self, ctx: PonderosaPKParser.Peak_list_2dContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by PonderosaPKParser#peak_2d.
    def enterPeak_2d(self, ctx: PonderosaPKParser.Peak_2dContext):  # pylint: disable=unused-argument
        self.peaks2D += 1

        self.atomSelectionSets.clear()
        self.asIsSets.clear()

    # Exit a parse tree produced by PonderosaPKParser#peak_2d.
    def exitPeak_2d(self, ctx: PonderosaPKParser.Peak_2dContext):

        try:

            if len(self.numberSelection) == 0:
                self.peaks2D -= 1
                return

            index = self.peaks2D

            try:

                P1 = float(str(ctx.Float(0)))
                P2 = float(str(ctx.Float(1)))

            except ValueError:
                self.peaks2D -= 1
                return

            comment = volume = None
            height = self.originalNumberSelection[0]

            L1 = str(ctx.Simple_name(0))
            L2 = str(ctx.Simple_name(1))

            if L1 in emptyValue:
                L1 = None
            if L2 in emptyValue:
                L2 = None

            if not self.hasPolySeq and not self.hasNonPolySeq:
                return

            if None in (P1, P2):
                self.peaks2D -= 1
                return

            dstFunc = self.validatePeak2D(index, P1, P2, None, None, None, None,
                                          None, None, None, None, height, None, volume, None)

            if dstFunc is None:
                self.peaks2D -= 1
                return

            cur_spectral_dim = self.spectral_dim[self.num_of_dim][self.cur_list_id]

            cur_spectral_dim[1]['freq_hint'].append(P1)
            cur_spectral_dim[2]['freq_hint'].append(P2)

            has_assignments = has_multiple_assignments = False
            asis1 = asis2 = None

            if None not in (L1, L2):
                assignments = [None] * self.num_of_dim
                if L1 is not None:
                    ext = self.extractPeakAssignment(1, L1, index)
                    if ext is not None:
                        status, _L1 = self.testAssignment(1, ext, L1)
                        if status:
                            assignments[0] = ext
                        elif _L1 is not None:
                            if comment is None:
                                comment = f'{cur_spectral_dim[1]["axis_code"]}:{L1} -> {_L1}'
                            ext = self.extractPeakAssignment(1, _L1, index)
                            if ext is not None:
                                assignments[0] = ext
                if L2 is not None:
                    ext = self.extractPeakAssignment(1, L2, index)
                    if ext is not None:
                        status, _L2 = self.testAssignment(2, ext, L2)
                        if status:
                            assignments[1] = ext
                        elif _L2 is not None:
                            if comment is None:
                                comment = f'{cur_spectral_dim[2]["axis_code"]}:{L2} -> {_L2}'
                            ext = self.extractPeakAssignment(1, _L2, index)
                            if ext is not None:
                                assignments[1] = ext

                has_assignments, has_multiple_assignments, asis1, asis2 =\
                    self.checkAssignments2D(index, assignments, dstFunc)

            self.addAssignedPkRow2D(index, dstFunc, has_assignments, has_multiple_assignments,
                                    asis1, asis2,
                                    f'{L1} {L2} -> ',
                                    comment if comment is not None or None in (L1, L2) or (has_assignments and not has_multiple_assignments)
                                    else f'{L1} {L2}')

        finally:
            self.numberSelection.clear()
            self.originalNumberSelection.clear()

    # Enter a parse tree produced by PonderosaPKParser#peak_list_3d.
    def enterPeak_list_3d(self, ctx: PonderosaPKParser.Peak_list_3dContext):
        self.num_of_dim = 3

        axis_order = str(ctx.Simple_name_AO())

        if len(axis_order) == self.num_of_dim:

            for _dim_id, _axis_code in enumerate(axis_order, start=1):
                if _dim_id not in self.cur_spectral_dim:
                    cur_spectral_dim = copy.copy(SPECTRAL_DIM_TEMPLATE)
                else:
                    cur_spectral_dim = self.cur_spectral_dim[_dim_id]

                cur_spectral_dim['axis_code'] = cur_spectral_dim['axis_order'] = _axis_code

                for a in _axis_code:
                    a = a.upper()
                    if a in ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS:
                        cur_spectral_dim['atom_type'] = a
                        cur_spectral_dim['atom_isotope_number'] = ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS[a][0]
                        break

                isotope_number = cur_spectral_dim['atom_isotope_number']

                cur_spectral_dim['acquisition'] = 'yes' if _dim_id == self.acq_dim_id\
                    and (isotope_number == 1 or (isotope_number == 13 and self.exptlMethod == 'SOLID-STATE NMR')) else 'no'

                if _dim_id == 1 and cur_spectral_dim['acquisition'] == 'no':
                    self.acq_dim_id = self.num_of_dim

                cur_spectral_dim['under_sampling_type'] = 'not observed' if cur_spectral_dim['acquisition'] == 'yes' else 'aliased'

                self.cur_spectral_dim[_dim_id] = cur_spectral_dim

        self.initSpectralDim()

        if self.num_of_dim not in self.__spectrum_names:
            self.__spectrum_names[self.num_of_dim] = {}
        if self.cur_list_id not in self.__spectrum_names[self.num_of_dim]:
            self.__spectrum_names[self.num_of_dim][self.cur_list_id] = str(ctx.Simple_name_NT())

    # Exit a parse tree produced by PonderosaPKParser#peak_list_3d.
    def exitPeak_list_3d(self, ctx: PonderosaPKParser.Peak_list_3dContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by PonderosaPKParser#peak_3d.
    def enterPeak_3d(self, ctx: PonderosaPKParser.Peak_3dContext):  # pylint: disable=unused-argument
        self.peaks3D += 1

        self.atomSelectionSets.clear()
        self.asIsSets.clear()

    # Exit a parse tree produced by PonderosaPKParser#peak_3d.
    def exitPeak_3d(self, ctx: PonderosaPKParser.Peak_3dContext):

        try:

            if len(self.numberSelection) == 0:
                self.peaks3D -= 1
                return

            index = self.peaks3D

            try:

                P1 = float(str(ctx.Float(0)))
                P2 = float(str(ctx.Float(1)))
                P3 = float(str(ctx.Float(2)))

            except ValueError:
                self.peaks3D -= 1
                return

            comment = volume = None
            height = self.originalNumberSelection[0]

            L1 = str(ctx.Simple_name(0))
            L2 = str(ctx.Simple_name(1))
            L3 = str(ctx.Simple_name(2))

            if L1 in emptyValue:
                L1 = None
            if L2 in emptyValue:
                L2 = None
            if L3 in emptyValue:
                L3 = None

            if not self.hasPolySeq and not self.hasNonPolySeq:
                return

            if None in (P1, P2, P3):
                self.peaks3D -= 1
                return

            dstFunc = self.validatePeak3D(index, P1, P2, P3, None, None, None, None, None, None,
                                          None, None, None, None, None, None, height, None, volume, None)

            if dstFunc is None:
                self.peaks3D -= 1
                return

            cur_spectral_dim = self.spectral_dim[self.num_of_dim][self.cur_list_id]

            cur_spectral_dim[1]['freq_hint'].append(P1)
            cur_spectral_dim[2]['freq_hint'].append(P2)
            cur_spectral_dim[3]['freq_hint'].append(P3)

            has_assignments = has_multiple_assignments = False
            asis1 = asis2 = asis3 = None

            if None not in (L1, L2, L3):
                assignments = [None] * self.num_of_dim
                if L1 is not None:
                    ext = self.extractPeakAssignment(1, L1, index)
                    if ext is not None:
                        status, _L1 = self.testAssignment(1, ext, L1)
                        if status:
                            assignments[0] = ext
                        elif _L1 is not None:
                            if comment is None:
                                comment = f'{cur_spectral_dim[1]["axis_code"]}:{L1} -> {_L1}'
                            ext = self.extractPeakAssignment(1, _L1, index)
                            if ext is not None:
                                assignments[0] = ext
                if L2 is not None:
                    ext = self.extractPeakAssignment(1, L2, index)
                    if ext is not None:
                        status, _L2 = self.testAssignment(2, ext, L2)
                        if status:
                            assignments[1] = ext
                        elif _L2 is not None:
                            if comment is None:
                                comment = f'{cur_spectral_dim[2]["axis_code"]}:{L2} -> {_L2}'
                            ext = self.extractPeakAssignment(1, _L2, index)
                            if ext is not None:
                                assignments[1] = ext
                if L3 is not None:
                    ext = self.extractPeakAssignment(1, L3, index)
                    if ext is not None:
                        status, _L3 = self.testAssignment(3, ext, L3)
                        if status:
                            assignments[2] = ext
                        elif _L3 is not None:
                            if comment is None:
                                comment = f'{cur_spectral_dim[3]["axis_code"]}:{L3} -> {_L3}'
                            ext = self.extractPeakAssignment(1, _L3, index)
                            if ext is not None:
                                assignments[2] = ext

                has_assignments, has_multiple_assignments, asis1, asis2, asis3 =\
                    self.checkAssignments3D(index, assignments, dstFunc)

            self.addAssignedPkRow3D(index, dstFunc, has_assignments, has_multiple_assignments,
                                    asis1, asis2, asis3,
                                    f'{L1} {L2} {L3} -> ',
                                    comment if comment is not None or None in (L1, L2, L3) or (has_assignments and not has_multiple_assignments)
                                    else f'{L1} {L2} {L3}')

        finally:
            self.numberSelection.clear()
            self.originalNumberSelection.clear()

    # Enter a parse tree produced by PonderosaPKParser#peak_list_4d.
    def enterPeak_list_4d(self, ctx: PonderosaPKParser.Peak_list_4dContext):
        self.num_of_dim = 4

        axis_order = str(ctx.Simple_name_AO())

        if len(axis_order) == self.num_of_dim:

            for _dim_id, _axis_code in enumerate(axis_order, start=1):
                if _dim_id not in self.cur_spectral_dim:
                    cur_spectral_dim = copy.copy(SPECTRAL_DIM_TEMPLATE)
                else:
                    cur_spectral_dim = self.cur_spectral_dim[_dim_id]

                cur_spectral_dim['axis_code'] = cur_spectral_dim['axis_order'] = _axis_code

                for a in _axis_code:
                    a = a.upper()
                    if a in ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS:
                        cur_spectral_dim['atom_type'] = a
                        cur_spectral_dim['atom_isotope_number'] = ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS[a][0]
                        break

                isotope_number = cur_spectral_dim['atom_isotope_number']

                cur_spectral_dim['acquisition'] = 'yes' if _dim_id == self.acq_dim_id\
                    and (isotope_number == 1 or (isotope_number == 13 and self.exptlMethod == 'SOLID-STATE NMR')) else 'no'

                if _dim_id == 1 and cur_spectral_dim['acquisition'] == 'no':
                    self.acq_dim_id = self.num_of_dim

                cur_spectral_dim['under_sampling_type'] = 'not observed' if cur_spectral_dim['acquisition'] == 'yes' else 'aliased'

                self.cur_spectral_dim[_dim_id] = cur_spectral_dim

        self.initSpectralDim()

        if self.num_of_dim not in self.__spectrum_names:
            self.__spectrum_names[self.num_of_dim] = {}
        if self.cur_list_id not in self.__spectrum_names[self.num_of_dim]:
            self.__spectrum_names[self.num_of_dim][self.cur_list_id] = str(ctx.Simple_name_NT())

    # Exit a parse tree produced by PonderosaPKParser#peak_list_4d.
    def exitPeak_list_4d(self, ctx: PonderosaPKParser.Peak_list_4dContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by PonderosaPKParser#peak_4d.
    def enterPeak_4d(self, ctx: PonderosaPKParser.Peak_4dContext):  # pylint: disable=unused-argument
        self.peaks4D += 1

        self.atomSelectionSets.clear()
        self.asIsSets.clear()

    # Exit a parse tree produced by PonderosaPKParser#peak_4d.
    def exitPeak_4d(self, ctx: PonderosaPKParser.Peak_4dContext):

        try:

            if len(self.numberSelection) == 0:
                self.peaks4D -= 1
                return

            index = self.peaks4D

            try:

                P1 = float(str(ctx.Float(0)))
                P2 = float(str(ctx.Float(1)))
                P3 = float(str(ctx.Float(2)))
                P4 = float(str(ctx.Float(3)))

            except ValueError:
                self.peaks4D -= 1
                return

            comment = volume = None
            height = self.originalNumberSelection[0]

            L1 = str(ctx.Simple_name(0))
            L2 = str(ctx.Simple_name(1))
            L3 = str(ctx.Simple_name(2))
            L4 = str(ctx.Simple_name(3))

            if L1 in emptyValue:
                L1 = None
            if L2 in emptyValue:
                L2 = None
            if L3 in emptyValue:
                L3 = None
            if L4 in emptyValue:
                L4 = None

            if not self.hasPolySeq and not self.hasNonPolySeq:
                return

            if None in (P1, P2, P3, P4):
                self.peaks4D -= 1
                return

            dstFunc = self.validatePeak4D(index, P1, P2, P3, P4, None, None, None, None, None, None, None, None,
                                          None, None, None, None, None, None, None, None, height, None, volume, None)

            if dstFunc is None:
                self.peaks4D -= 1
                return

            cur_spectral_dim = self.spectral_dim[self.num_of_dim][self.cur_list_id]

            cur_spectral_dim[1]['freq_hint'].append(P1)
            cur_spectral_dim[2]['freq_hint'].append(P2)
            cur_spectral_dim[3]['freq_hint'].append(P3)
            cur_spectral_dim[4]['freq_hint'].append(P4)

            has_assignments = has_multiple_assignments = False
            asis1 = asis2 = asis3 = asis4 = None

            if None not in (L1, L2, L3, L4):
                assignments = [None] * self.num_of_dim
                if L1 is not None:
                    ext = self.extractPeakAssignment(1, L1, index)
                    if ext is not None:
                        status, _L1 = self.testAssignment(1, ext, L1)
                        if status:
                            assignments[0] = ext
                        elif _L1 is not None:
                            if comment is None:
                                comment = f'{cur_spectral_dim[1]["axis_code"]}:{L1} -> {_L1}'
                            ext = self.extractPeakAssignment(1, _L1, index)
                            if ext is not None:
                                assignments[0] = ext
                if L2 is not None:
                    ext = self.extractPeakAssignment(1, L2, index)
                    if ext is not None:
                        status, _L2 = self.testAssignment(2, ext, L2)
                        if status:
                            assignments[1] = ext
                        elif _L2 is not None:
                            if comment is None:
                                comment = f'{cur_spectral_dim[2]["axis_code"]}:{L2} -> {_L2}'
                            ext = self.extractPeakAssignment(1, _L2, index)
                            if ext is not None:
                                assignments[1] = ext
                if L3 is not None:
                    ext = self.extractPeakAssignment(1, L3, index)
                    if ext is not None:
                        status, _L3 = self.testAssignment(3, ext, L3)
                        if status:
                            assignments[2] = ext
                        elif _L3 is not None:
                            if comment is None:
                                comment = f'{cur_spectral_dim[3]["axis_code"]}:{L3} -> {_L3}'
                            ext = self.extractPeakAssignment(1, _L3, index)
                            if ext is not None:
                                assignments[2] = ext
                if L4 is not None:
                    ext = self.extractPeakAssignment(1, L4, index)
                    if ext is not None:
                        status, _L4 = self.testAssignment(4, ext, L4)
                        if status:
                            assignments[3] = ext
                        elif _L4 is not None:
                            if comment is None:
                                comment = f'{cur_spectral_dim[4]["axis_code"]}:{L4} -> {_L4}'
                            ext = self.extractPeakAssignment(1, _L4, index)
                            if ext is not None:
                                assignments[3] = ext

                has_assignments, has_multiple_assignments, asis1, asis2, asis3, asis4 =\
                    self.checkAssignments4D(index, assignments, dstFunc)

            self.addAssignedPkRow4D(index, dstFunc, has_assignments, has_multiple_assignments,
                                    asis1, asis2, asis3, asis4,
                                    f'{L1} {L2} {L3} {L4} -> ',
                                    comment if comment is not None or None in (L1, L2, L3, L4) or (has_assignments and not has_multiple_assignments)
                                    else f'{L1} {L2} {L3} {L4}')

        finally:
            self.numberSelection.clear()
            self.originalNumberSelection.clear()

    # Enter a parse tree produced by PonderosaPKParser#number.
    def enterNumber(self, ctx: PonderosaPKParser.NumberContext):

        try:

            if ctx.Float():
                value = str(ctx.Float())
                self.numberSelection.append(float(value))
                self.originalNumberSelection.append(value)

            else:
                value = str(ctx.Real())
                self.numberSelection.append(float(value))
                self.originalNumberSelection.append(value)

        except ValueError:
            self.numberSelection.append(None)
            self.originalNumberSelection.append(None)

    # Exit a parse tree produced by PonderosaPKParser#number.
    def exitNumber(self, ctx: PonderosaPKParser.NumberContext):  # pylint: disable=unused-argument
        pass


# del PonderosaPKParser
