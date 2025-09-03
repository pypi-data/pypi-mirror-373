##
# File: XeasyPKParserListener.py
# Date: 04-Dec-2024
#
# Updates:
""" ParserLister class for XEASY PK files.
    @author: Masashi Yokochi
"""
__docformat__ = "restructuredtext en"
__author__ = "Masashi Yokochi"
__email__ = "yokochi@protein.osaka-u.ac.jp"
__license__ = "Apache License 2.0"
__version__ = "1.0.0"

import sys
import re
import copy

from antlr4 import ParseTreeListener
from typing import IO, List, Optional

try:
    from wwpdb.utils.nmr.io.CifReader import CifReader
    from wwpdb.utils.nmr.pk.XeasyPKParser import XeasyPKParser
    from wwpdb.utils.nmr.pk.BasePKParserListener import (BasePKParserListener,
                                                         PEAK_ASSIGNMENT_SEPARATOR_PAT)
    from wwpdb.utils.nmr.mr.ParserListenerUtil import (ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS,
                                                       REPRESENTATIVE_MODEL_ID,
                                                       REPRESENTATIVE_ALT_ID)
    from wwpdb.utils.nmr.ChemCompUtil import ChemCompUtil
    from wwpdb.utils.nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from wwpdb.utils.nmr.nef.NEFTranslator import NEFTranslator
    from wwpdb.utils.nmr.AlignUtil import emptyValue
except ImportError:
    from nmr.io.CifReader import CifReader
    from nmr.pk.XeasyPKParser import XeasyPKParser
    from nmr.pk.BasePKParserListener import (BasePKParserListener,
                                             PEAK_ASSIGNMENT_SEPARATOR_PAT)
    from nmr.mr.ParserListenerUtil import (ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS,
                                           REPRESENTATIVE_MODEL_ID,
                                           REPRESENTATIVE_ALT_ID)
    from nmr.ChemCompUtil import ChemCompUtil
    from nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from nmr.nef.NEFTranslator import NEFTranslator
    from nmr.AlignUtil import emptyValue


# This class defines a complete listener for a parse tree produced by XeasyPKParser.
class XeasyPKParserListener(ParseTreeListener, BasePKParserListener):

    __index = None
    __labels = None
    __axis_order = None
    __atomNumberDict = None
    __last_comment = None
    __comment_offset = None
    __g = None

    def __init__(self, verbose: bool = True, log: IO = sys.stdout,
                 representativeModelId: int = REPRESENTATIVE_MODEL_ID,
                 representativeAltId: str = REPRESENTATIVE_ALT_ID,
                 mrAtomNameMapping: Optional[List[dict]] = None,
                 cR: Optional[CifReader] = None, caC: Optional[dict] = None, ccU: Optional[ChemCompUtil] = None,
                 csStat: Optional[BMRBChemShiftStat] = None, nefT: Optional[NEFTranslator] = None,
                 atomNumberDict: Optional[dict] = None, reasons: Optional[dict] = None):
        super().__init__(verbose, log, representativeModelId, representativeAltId,
                         mrAtomNameMapping, cR, caC, ccU, csStat, nefT, reasons)

        self.file_type = 'nm-pea-xea'
        self.software_name = 'XEASY'

        self.__atomNumberDict = atomNumberDict

    # Enter a parse tree produced by XeasyPKParser#xeasy_pk.
    def enterXeasy_pk(self, ctx: XeasyPKParser.Xeasy_pkContext):  # pylint: disable=unused-argument
        self.enter()
        self.__g = []

    # Exit a parse tree produced by XeasyPKParser#xeasy_pk.
    def exitXeasy_pk(self, ctx: XeasyPKParser.Xeasy_pkContext):  # pylint: disable=unused-argument
        self.exit()

    # Enter a parse tree produced by XeasyPKParser#dimension.
    def enterDimension(self, ctx: XeasyPKParser.DimensionContext):
        if ctx.Integer_ND():
            self.num_of_dim = int(str(ctx.Integer_ND()))
            self.acq_dim_id = 1
        self.__index = None
        self.__labels = {}
        self.__axis_order = {}

    # Exit a parse tree produced by XeasyPKParser#dimension.
    def exitDimension(self, ctx: XeasyPKParser.DimensionContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by XeasyPKParser#peak.
    def enterPeak(self, ctx: XeasyPKParser.PeakContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by XeasyPKParser#peak.
    def exitPeak(self, ctx: XeasyPKParser.PeakContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by XeasyPKParser#format.
    def enterFormat(self, ctx: XeasyPKParser.FormatContext):
        if ctx.Simple_name_FO():
            if self.num_of_dim == -1:
                val = str(ctx.Simple_name_FO())
                if '2D' in val:
                    self.num_of_dim = 2
                if '3D' in val:
                    self.num_of_dim = 3
                if '4D' in val:
                    self.num_of_dim = 4

    # Exit a parse tree produced by XeasyPKParser#format.
    def exitFormat(self, ctx: XeasyPKParser.FormatContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by XeasyPKParser#iname.
    def enterIname(self, ctx: XeasyPKParser.InameContext):
        if ctx.Integer_IN():
            _dim_id = int(str(ctx.Integer_IN()))
            self.num_of_dim = max(self.num_of_dim, _dim_id)
        if ctx.Simple_name_IN():
            _axis_code = str(ctx.Simple_name_IN())
            if _axis_code not in emptyValue:
                self.__labels[_dim_id] = _axis_code

    # Exit a parse tree produced by XeasyPKParser#iname.
    def exitIname(self, ctx: XeasyPKParser.InameContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by XeasyPKParser#cyana_format.
    def enterCyana_format(self, ctx: XeasyPKParser.Cyana_formatContext):
        if ctx.Simple_name_CY():
            _axis_codes = str(ctx.Simple_name_CY())
            if self.num_of_dim == -1:
                self.num_of_dim = max(self.num_of_dim, len(_axis_codes))

            for _dim_id, _axis_code in enumerate(_axis_codes, start=1):
                if _dim_id not in self.__labels:
                    if _axis_code not in emptyValue:
                        self.__labels[_dim_id] = _axis_code
                if _dim_id not in self.__axis_order:
                    if _axis_code not in emptyValue:
                        self.__axis_order[_dim_id] = _axis_code

    # Exit a parse tree produced by XeasyPKParser#cyana_format.
    def exitCyana_format(self, ctx: XeasyPKParser.Cyana_formatContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by XeasyPKParser#spectrum.
    def enterSpectrum(self, ctx: XeasyPKParser.SpectrumContext):
        _dim_id = 0
        if ctx.Simple_name_SP(_dim_id):
            _dim_id += 1
            while ctx.Simple_name_SP(_dim_id):
                self.num_of_dim = max(self.num_of_dim, _dim_id)
                if _dim_id not in self.__labels:
                    _axis_code = str(ctx.Simple_name_SP(_dim_id))
                    if _axis_code not in emptyValue:
                        self.__labels[_dim_id] = _axis_code
                _dim_id += 1

    # Exit a parse tree produced by XeasyPKParser#spectrum.
    def exitSpectrum(self, ctx: XeasyPKParser.SpectrumContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by XeasyPKParser#tolerance.
    def enterTolerance(self, ctx: XeasyPKParser.ToleranceContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by XeasyPKParser#tolerance.
    def exitTolerance(self, ctx: XeasyPKParser.ToleranceContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by XeasyPKParser#peak_list_2d.
    def enterPeak_list_2d(self, ctx: XeasyPKParser.Peak_list_2dContext):  # pylint: disable=unused-argument
        self.num_of_dim = 2
        self.initSpectralDim()
        self.fillSpectralDimWithLabels()

    # Exit a parse tree produced by XeasyPKParser#peak_list_2d.
    def exitPeak_list_2d(self, ctx: XeasyPKParser.Peak_list_2dContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by XeasyPKParser#peak_2d.
    def enterPeak_2d(self, ctx: XeasyPKParser.Peak_2dContext):  # pylint: disable=unused-argument
        self.peaks2D += 1

        self.atomSelectionSets.clear()
        self.asIsSets.clear()

        self.__index = int(str(ctx.Integer(0)))
        self.__last_comment = None
        self.__comment_offset = 0
        self.__g.clear()

        self.no_extra_comment = True

    # Exit a parse tree produced by XeasyPKParser#peak_2d.
    def exitPeak_2d(self, ctx: XeasyPKParser.Peak_2dContext):

        try:

            if 0 in (len(self.positionSelection), len(self.numberSelection)):
                self.peaks2D -= 1
                return

            index = int(str(ctx.Integer(0)))
            x_ppm = self.positionSelection[0]
            y_ppm = self.positionSelection[1]
            # color_code = int(str(ctx.Integer(1)))
            # spectrum_type = str(ctx.Simple_name(0))
            vol = self.originalNumberSelection[0]
            vol_err = self.originalNumberSelection[1]
            # integral_method = str(ctx.Simple_name(1))
            # type = str(ctx.type_code())

            if len(self.assignmentSelection) > self.num_of_dim or ctx.assign(self.num_of_dim):
                if self.createSfDict__ and self.use_peak_row_format:
                    sf = self.getSf()
                    sf['peak_row_format'] = self.use_peak_row_format = False

            if not self.hasPolySeq and not self.hasNonPolySeq:
                return

            if None in (x_ppm, y_ppm):
                self.peaks2D -= 1
                return

            dstFunc = self.validatePeak2D(index, x_ppm, y_ppm, None, None, None, None,
                                          None, None, None, None, None, None, vol, vol_err)

            if dstFunc is None:
                self.peaks2D -= 1
                return

            cur_spectral_dim = self.spectral_dim[self.num_of_dim][self.cur_list_id]

            cur_spectral_dim[1]['freq_hint'].append(x_ppm)
            cur_spectral_dim[2]['freq_hint'].append(y_ppm)

            has_assignments = has_multiple_assignments = False
            asis1 = asis2 = None

            if len(self.assignmentSelection) >= self.num_of_dim:
                assignments = [None] * self.num_of_dim
                for idx, assignment in enumerate(self.assignmentSelection):
                    if isinstance(assignment, dict):
                        if assignments[idx % self.num_of_dim] is None:
                            assignments[idx % self.num_of_dim] = []
                        assignments[idx % self.num_of_dim].append(assignment)
                    elif assignment is not None:
                        ext = self.extractPeakAssignment(1, assignment, index)
                        if ext is not None:
                            if assignments[idx % self.num_of_dim] is None:
                                assignments[idx % self.num_of_dim] = []
                            for a in ext:
                                assignments[idx % self.num_of_dim].append(a)

                has_assignments, has_multiple_assignments, asis1, asis2 =\
                    self.checkAssignments2D(index, assignments, dstFunc)

            self.addAssignedPkRow2D(index, dstFunc, has_assignments, has_multiple_assignments,
                                    asis1, asis2, '', None)

        finally:
            self.positionSelection.clear()
            self.numberSelection.clear()
            self.originalNumberSelection.clear()
            self.assignmentSelection.clear()

    # Enter a parse tree produced by XeasyPKParser#peak_list_3d.
    def enterPeak_list_3d(self, ctx: XeasyPKParser.Peak_list_3dContext):  # pylint: disable=unused-argument
        self.num_of_dim = 3
        self.initSpectralDim()
        self.fillSpectralDimWithLabels()

    # Exit a parse tree produced by XeasyPKParser#peak_list_3d.
    def exitPeak_list_3d(self, ctx: XeasyPKParser.Peak_list_3dContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by XeasyPKParser#peak_3d.
    def enterPeak_3d(self, ctx: XeasyPKParser.Peak_3dContext):  # pylint: disable=unused-argument
        self.peaks3D += 1

        self.atomSelectionSets.clear()
        self.asIsSets.clear()

        self.__index = int(str(ctx.Integer(0)))
        self.__last_comment = None
        self.__comment_offset = 0
        self.__g.clear()

        self.no_extra_comment = True

    # Exit a parse tree produced by XeasyPKParser#peak_3d.
    def exitPeak_3d(self, ctx: XeasyPKParser.Peak_3dContext):

        try:

            if 0 in (len(self.positionSelection), len(self.numberSelection)):
                self.peaks3D -= 1
                return

            index = int(str(ctx.Integer(0)))
            x_ppm = self.positionSelection[0]
            y_ppm = self.positionSelection[1]
            z_ppm = self.positionSelection[2]
            # color_code = int(str(ctx.Integer(1)))
            # spectrum_type = str(ctx.Simple_name(0))
            vol = self.originalNumberSelection[0]
            vol_err = self.originalNumberSelection[1]
            # integral_method = str(ctx.Simple_name(1))
            # type = str(ctx.type_code())

            if len(self.assignmentSelection) > self.num_of_dim or ctx.assign(self.num_of_dim):
                if self.createSfDict__ and self.use_peak_row_format:
                    sf = self.getSf()
                    sf['peak_row_format'] = self.use_peak_row_format = False

            if not self.hasPolySeq and not self.hasNonPolySeq:
                return

            if None in (x_ppm, y_ppm, z_ppm):
                self.peaks3D -= 1
                return

            dstFunc = self.validatePeak3D(index, x_ppm, y_ppm, z_ppm, None, None, None, None, None, None,
                                          None, None, None, None, None, None, None, None, vol, vol_err)

            if dstFunc is None:
                self.peaks3D -= 1
                return

            cur_spectral_dim = self.spectral_dim[self.num_of_dim][self.cur_list_id]

            cur_spectral_dim[1]['freq_hint'].append(x_ppm)
            cur_spectral_dim[2]['freq_hint'].append(y_ppm)
            cur_spectral_dim[3]['freq_hint'].append(z_ppm)

            has_assignments = has_multiple_assignments = False
            asis1 = asis2 = asis3 = None

            if len(self.assignmentSelection) >= self.num_of_dim:
                assignments = [None] * self.num_of_dim
                for idx, assignment in enumerate(self.assignmentSelection):
                    if isinstance(assignment, dict):
                        if assignments[idx % self.num_of_dim] is None:
                            assignments[idx % self.num_of_dim] = []
                        assignments[idx % self.num_of_dim].append(assignment)
                    elif assignment is not None:
                        ext = self.extractPeakAssignment(1, assignment, index)
                        if ext is not None:
                            if assignments[idx % self.num_of_dim] is None:
                                assignments[idx % self.num_of_dim] = []
                            for a in ext:
                                assignments[idx % self.num_of_dim].append(a)

                has_assignments, has_multiple_assignments, asis1, asis2, asis3 =\
                    self.checkAssignments3D(index, assignments, dstFunc)

            self.addAssignedPkRow3D(index, dstFunc, has_assignments, has_multiple_assignments,
                                    asis1, asis2, asis3, '', None)

        finally:
            self.positionSelection.clear()
            self.numberSelection.clear()
            self.originalNumberSelection.clear()
            self.assignmentSelection.clear()

    # Enter a parse tree produced by XeasyPKParser#peak_list_4d.
    def enterPeak_list_4d(self, ctx: XeasyPKParser.Peak_list_4dContext):  # pylint: disable=unused-argument
        self.num_of_dim = 4
        self.initSpectralDim()
        self.fillSpectralDimWithLabels()

    # Exit a parse tree produced by XeasyPKParser#peak_list_4d.
    def exitPeak_list_4d(self, ctx: XeasyPKParser.Peak_list_4dContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by XeasyPKParser#peak_4d.
    def enterPeak_4d(self, ctx: XeasyPKParser.Peak_4dContext):  # pylint: disable=unused-argument
        self.peaks4D += 1

        self.atomSelectionSets.clear()
        self.asIsSets.clear()

        self.__index = int(str(ctx.Integer(0)))
        self.__last_comment = None
        self.__comment_offset = 0
        self.__g.clear()

        self.no_extra_comment = True

    # Exit a parse tree produced by XeasyPKParser#peak_4d.
    def exitPeak_4d(self, ctx: XeasyPKParser.Peak_4dContext):

        try:

            if 0 in (len(self.positionSelection), len(self.numberSelection)):
                self.peaks4D -= 1
                return

            index = int(str(ctx.Integer(0)))
            x_ppm = self.positionSelection[0]
            y_ppm = self.positionSelection[1]
            z_ppm = self.positionSelection[2]
            a_ppm = self.positionSelection[3]
            # color_code = int(str(ctx.Integer(1)))
            # spectrum_type = str(ctx.Simple_name(0))
            vol = self.originalNumberSelection[0]
            vol_err = self.originalNumberSelection[1]
            # integral_method = str(ctx.Simple_name(1))
            # type = str(ctx.type_code())

            if len(self.assignmentSelection) > self.num_of_dim or ctx.assign(self.num_of_dim):
                if self.createSfDict__ and self.use_peak_row_format:
                    sf = self.getSf()
                    sf['peak_row_format'] = self.use_peak_row_format = False

            if not self.hasPolySeq and not self.hasNonPolySeq:
                return

            if None in (x_ppm, y_ppm, z_ppm, a_ppm):
                self.peaks4D -= 1
                return

            dstFunc = self.validatePeak4D(index, x_ppm, y_ppm, z_ppm, a_ppm, None, None, None, None, None, None, None, None,
                                          None, None, None, None, None, None, None, None, None, None, vol, vol_err)

            if dstFunc is None:
                self.peaks4D -= 1
                return

            cur_spectral_dim = self.spectral_dim[self.num_of_dim][self.cur_list_id]

            cur_spectral_dim[1]['freq_hint'].append(x_ppm)
            cur_spectral_dim[2]['freq_hint'].append(y_ppm)
            cur_spectral_dim[3]['freq_hint'].append(z_ppm)
            cur_spectral_dim[4]['freq_hint'].append(a_ppm)

            has_assignments = has_multiple_assignments = False
            asis1 = asis2 = asis3 = asis4 = None

            if len(self.assignmentSelection) >= self.num_of_dim:
                assignments = [None] * self.num_of_dim
                for idx, assignment in enumerate(self.assignmentSelection):
                    if isinstance(assignment, dict):
                        if assignments[idx % self.num_of_dim] is None:
                            assignments[idx % self.num_of_dim] = []
                        assignments[idx % self.num_of_dim].append(assignment)
                    elif assignment is not None:
                        ext = self.extractPeakAssignment(1, assignment, index)
                        if ext is not None:
                            if assignments[idx % self.num_of_dim] is None:
                                assignments[idx % self.num_of_dim] = []
                            for a in ext:
                                assignments[idx % self.num_of_dim].append(a)

                has_assignments, has_multiple_assignments, asis1, asis2, asis3, asis4 =\
                    self.checkAssignments4D(index, assignments, dstFunc)

            self.addAssignedPkRow4D(index, dstFunc, has_assignments, has_multiple_assignments,
                                    asis1, asis2, asis3, asis4, '', None)

        finally:
            self.positionSelection.clear()
            self.numberSelection.clear()
            self.originalNumberSelection.clear()
            self.assignmentSelection.clear()

    # Enter a parse tree produced by XeasyPKParser#position.
    def enterPosition(self, ctx: XeasyPKParser.PositionContext):

        try:

            if ctx.Float():
                value = str(ctx.Float())
                self.positionSelection.append(float(value))

            elif ctx.Integer():
                value = str(ctx.Integer())
                self.positionSelection.append(float(value))

            else:
                self.positionSelection.append(None)

        except ValueError:
            self.positionSelection.append(None)

    # Exit a parse tree produced by XeasyPKParser#position.
    def exitPosition(self, ctx: XeasyPKParser.PositionContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by XeasyPKParser#number.
    def enterNumber(self, ctx: XeasyPKParser.NumberContext):  # pylint: disable=unused-argument

        try:

            if ctx.Float():
                value = str(ctx.Float())
                self.numberSelection.append(float(value))
                self.originalNumberSelection.append(value)

            elif ctx.Real():
                value = str(ctx.Real())
                self.numberSelection.append(float(value))
                self.originalNumberSelection.append(value)

            elif ctx.Integer():
                value = str(ctx.Integer())
                self.numberSelection.append(int(value))
                self.originalNumberSelection.append(value)

            else:
                self.numberSelection.append(None)
                self.originalNumberSelection.append(None)

        except ValueError:
            self.numberSelection.append(None)
            self.originalNumberSelection.append(None)

    # Exit a parse tree produced by XeasyPKParser#number.
    def exitNumber(self, ctx: XeasyPKParser.NumberContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by XeasyPKParser#type_code.
    def enterType_code(self, ctx: XeasyPKParser.Type_codeContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by XeasyPKParser#type_code.
    def exitType_code(self, ctx: XeasyPKParser.Type_codeContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by XeasyPKParser#assign.
    def enterAssign(self, ctx: XeasyPKParser.AssignContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by XeasyPKParser#assign.
    def exitAssign(self, ctx: XeasyPKParser.AssignContext):
        index = self.__index
        if ctx.Simple_name() and ctx.Integer():
            self.assignmentSelection.append(f'{str(ctx.Integer())} {str(ctx.Simple_name())}')
        elif ctx.Simple_name():
            assignment = self.extractPeakAssignment(1, str(ctx.Simple_name()), index)
            if assignment is None:
                self.assignmentSelection.append(None)
            else:
                factor = assignment[0]
                self.assignmentSelection.append(factor)
        else:
            if ctx.Integer() is None:
                self.assignmentSelection.append(None)
            else:
                ai = int(str(ctx.Integer()))
                if ai == 0 or self.__atomNumberDict is None or ai not in self.__atomNumberDict:
                    self.assignmentSelection.append(None)
                    if ai == 0:
                        pass
                    elif self.__atomNumberDict is None:
                        self.__g.append(f"[Missing data] {self.getCurrentRestraint(n=index)}"
                                        "Failed to recognize XEASY atom numbers in the spectral peak list file "
                                        "because XEASY PROT file is not available.")
                    elif ai not in self.__atomNumberDict:
                        self.__g.append(f"[Missing data] {self.getCurrentRestraint(n=index)}"
                                        f"'{ai})' is not defined in the XEASY PROT file.")
                else:
                    _factor = copy.copy(self.__atomNumberDict[ai])
                    _factor['atom_id'] = _factor['auth_atom_id']
                    del _factor['auth_atom_id']
                    self.assignmentSelection.append(_factor)

    # Enter a parse tree produced by XeasyPKParser#comment.
    def enterComment(self, ctx: XeasyPKParser.CommentContext):  # pylint: disable=unused-argument
        self.no_extra_comment = False

    # Exit a parse tree produced by XeasyPKParser#comment.
    def exitComment(self, ctx: XeasyPKParser.CommentContext):
        comment = []
        for col in range(20):
            if ctx.Any_name(col):
                text = str(ctx.Any_name(col))
                if text[0] in ('#', '!'):
                    break
                if text[0] in ('>', '<'):
                    continue
                comment.append(str(ctx.Any_name(col)))
            else:
                break
        self.__last_comment = None if len(comment) == 0 else ' '.join(comment)

        if self.__last_comment is None:
            return

        __last_comment = self.__last_comment if isinstance(self.__last_comment, str) else str(self.__last_comment)

        has_split = False

        if '/' in __last_comment:
            for last_comment in __last_comment.split('/'):
                if len(PEAK_ASSIGNMENT_SEPARATOR_PAT.sub(' ', last_comment).split()) >= self.num_of_dim:
                    assignments = self.extractPeakAssignment(self.num_of_dim, last_comment,
                                                             self.__index - 1 if isinstance(self.__index, int) else 1)
                    if assignments is not None and self.__atomNumberDict is None:
                        if self.ass_expr_debug:
                            print(f'{last_comment!r} -> {assignments}')
                        if isinstance(self.__comment_offset, int):
                            for idx, factor in enumerate(assignments, start=self.__comment_offset):
                                if idx >= len(self.assignmentSelection):
                                    self.assignmentSelection.append(factor)
                                elif self.assignmentSelection[idx] is None:
                                    self.assignmentSelection[idx] = factor
                    self.__comment_offset = len(self.assignmentSelection)
                    has_split = True

        if not has_split and '|' in __last_comment:
            for last_comment in __last_comment.split('|'):
                if len(PEAK_ASSIGNMENT_SEPARATOR_PAT.sub(' ', last_comment).split()) >= self.num_of_dim:
                    assignments = self.extractPeakAssignment(self.num_of_dim, last_comment,
                                                             self.__index - 1 if isinstance(self.__index, int) else 1)
                    if assignments is not None and self.__atomNumberDict is None:
                        if self.ass_expr_debug:
                            print(f'{last_comment!r} -> {assignments}')
                        if isinstance(self.__comment_offset, int):
                            for idx, factor in enumerate(assignments, start=self.__comment_offset):
                                if idx >= len(self.assignmentSelection):
                                    self.assignmentSelection.append(factor)
                                elif self.assignmentSelection[idx] is None:
                                    self.assignmentSelection[idx] = factor
                    self.__comment_offset = len(self.assignmentSelection)
                    has_split = True

        if not has_split and ',' in __last_comment:
            for last_comment in __last_comment.split(','):
                if len(PEAK_ASSIGNMENT_SEPARATOR_PAT.sub(' ', last_comment).split()) >= self.num_of_dim:
                    assignments = self.extractPeakAssignment(self.num_of_dim, last_comment,
                                                             self.__index - 1 if isinstance(self.__index, int) else 1)
                    if assignments is not None and self.__atomNumberDict is None:
                        if self.ass_expr_debug:
                            print(f'{last_comment!r} -> {assignments}')
                        if isinstance(self.__comment_offset, int):
                            for idx, factor in enumerate(assignments, start=self.__comment_offset):
                                if idx >= len(self.assignmentSelection):
                                    self.assignmentSelection.append(factor)
                                elif self.assignmentSelection[idx] is None:
                                    self.assignmentSelection[idx] = factor
                    self.__comment_offset = len(self.assignmentSelection)
                    has_split = True

        if not has_split:
            assignments = self.extractPeakAssignment(self.num_of_dim, __last_comment,
                                                     self.__index - 1 if isinstance(self.__index, int) else 1)
            if assignments is not None and self.__atomNumberDict is None:
                if self.ass_expr_debug:
                    print(f'{__last_comment!r} -> {assignments}')
                if isinstance(self.__comment_offset, int):
                    for idx, factor in enumerate(assignments, start=self.__comment_offset):
                        if idx >= len(self.assignmentSelection):
                            self.assignmentSelection.append(factor)
                        elif self.assignmentSelection[idx] is None:
                            self.assignmentSelection[idx] = factor
                self.__comment_offset = len(self.assignmentSelection)

        self.__last_comment = None
        self.__g.clear()

    def fillSpectralDimWithLabels(self):
        if self.__labels is None or len(self.__labels) == 0:
            return

        for _dim_id, _axis_code in self.__labels.items():

            try:
                cur_spectral_dim = self.spectral_dim[self.num_of_dim][self.cur_list_id][_dim_id]
            except KeyError:
                continue

            cur_spectral_dim['axis_code'] = _axis_code

            digits = re.findall(r'\d+', _axis_code)
            for digit in digits:
                num = int(digit)
                nuc = next((k for k, v in ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS.items() if num == v[0]), None)
                if nuc is not None:
                    cur_spectral_dim['atom_type'] = nuc
                    cur_spectral_dim['atom_isotope_number'] = num
                    break
            if cur_spectral_dim['atom_type'] is None:
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

        if self.__axis_order is None or len(self.__axis_order) == 0:
            return

        for _dim_id, _axis_order in self.__axis_order.items():

            try:
                cur_spectral_dim = self.spectral_dim[self.num_of_dim][self.cur_list_id][_dim_id]
            except KeyError:
                continue

            cur_spectral_dim['axis_order'] = _axis_order


# del XeasyPKParser
