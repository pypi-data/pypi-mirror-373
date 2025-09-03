##
# File: SparkyPKParserListener.py
# Date: 04-Dec-2024
#
# Updates:
""" ParserLister class for SPARKY PK files.
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
    from wwpdb.utils.nmr.io.CifReader import CifReader
    from wwpdb.utils.nmr.pk.SparkyPKParser import SparkyPKParser
    from wwpdb.utils.nmr.pk.BasePKParserListener import BasePKParserListener
    from wwpdb.utils.nmr.mr.ParserListenerUtil import (REPRESENTATIVE_MODEL_ID,
                                                       REPRESENTATIVE_ALT_ID,
                                                       getPkRow)
    from wwpdb.utils.nmr.ChemCompUtil import ChemCompUtil
    from wwpdb.utils.nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from wwpdb.utils.nmr.nef.NEFTranslator import NEFTranslator
except ImportError:
    from nmr.io.CifReader import CifReader
    from nmr.pk.SparkyPKParser import SparkyPKParser
    from nmr.pk.BasePKParserListener import BasePKParserListener
    from nmr.mr.ParserListenerUtil import (REPRESENTATIVE_MODEL_ID,
                                           REPRESENTATIVE_ALT_ID,
                                           getPkRow)
    from nmr.ChemCompUtil import ChemCompUtil
    from nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from nmr.nef.NEFTranslator import NEFTranslator


# This class defines a complete listener for a parse tree produced by SparkyPKParser.
class SparkyPKParserListener(ParseTreeListener, BasePKParserListener):

    __has_hz = False
    __has_dev = False
    __has_height = False
    __has_volume = False
    __has_rms = False
    __has_dummy_height = False
    __has_s_n = False
    __has_lw_hz = False
    __has_note = False

    __has_real_vol = False
    __real_vol = None

    __noteSelection = []

    def __init__(self, verbose: bool = True, log: IO = sys.stdout,
                 representativeModelId: int = REPRESENTATIVE_MODEL_ID,
                 representativeAltId: str = REPRESENTATIVE_ALT_ID,
                 mrAtomNameMapping: Optional[List[dict]] = None,
                 cR: Optional[CifReader] = None, caC: Optional[dict] = None, ccU: Optional[ChemCompUtil] = None,
                 csStat: Optional[BMRBChemShiftStat] = None, nefT: Optional[NEFTranslator] = None,
                 reasons: Optional[dict] = None):
        super().__init__(verbose, log, representativeModelId, representativeAltId,
                         mrAtomNameMapping, cR, caC, ccU, csStat, nefT, reasons)

        self.file_type = 'nm-pea-spa'
        self.software_name = 'SPARKY'

        if reasons is not None and 'has_real_vol' in reasons:
            self.__has_real_vol = True

    # Enter a parse tree produced by SparkyPKParser#sparky_pk.
    def enterSparky_pk(self, ctx: SparkyPKParser.Sparky_pkContext):  # pylint: disable=unused-argument
        self.enter()

    # Exit a parse tree produced by SparkyPKParser#sparky_pk.
    def exitSparky_pk(self, ctx: SparkyPKParser.Sparky_pkContext):  # pylint: disable=unused-argument
        self.exit()

    # Enter a parse tree produced by SparkyPKParser#data_label.
    def enterData_label(self, ctx: SparkyPKParser.Data_labelContext):
        if ctx.W2_LA():
            self.num_of_dim = max(self.num_of_dim, 2)
        if ctx.W3_LA():
            self.num_of_dim = max(self.num_of_dim, 3)
        if ctx.W4_LA():
            self.num_of_dim = max(self.num_of_dim, 4)

        self.__has_hz = False
        if ctx.W2_Hz_LA():
            self.__has_hz = True

        self.__has_dev = False
        if ctx.Dev_w2_LA():
            self.__has_dev = True

        self.__has_height = False
        if ctx.Height_LA():
            self.__has_height = True

        self.__has_volume = False
        if ctx.Volume_LA():
            self.__has_volume = True

        self.__has_rms = False
        if ctx.Dummy_Rms_LA():
            self.__has_rms = True

        self.__has_dummy_height = False
        if ctx.Dummy_H_LA():
            self.__has_dummy_height = True

        self.__has_s_n = False
        if ctx.S_N_LA():
            self.__has_s_n = True

        self.__has_lw_hz = False
        if ctx.Lw2_Hz_LA():
            self.__has_lw_hz = True

        self.__has_note = False
        if ctx.Note_LA():
            self.__has_note = True

        self.initSpectralDim()

    # Exit a parse tree produced by SparkyPKParser#data_label.
    def exitData_label(self, ctx: SparkyPKParser.Data_labelContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by SparkyPKParser#data_label_wo_assign.
    def enterData_label_wo_assign(self, ctx: SparkyPKParser.Data_label_wo_assignContext):
        if ctx.W2_LA():
            self.num_of_dim = max(self.num_of_dim, 2)
        if ctx.W3_LA():
            self.num_of_dim = max(self.num_of_dim, 3)
        if ctx.W4_LA():
            self.num_of_dim = max(self.num_of_dim, 4)

        self.__has_hz = False
        if ctx.W2_Hz_LA():
            self.__has_hz = True

        self.__has_dev = False
        if ctx.Dev_w2_LA():
            self.__has_dev = True

        self.__has_height = False
        if ctx.Height_LA():
            self.__has_height = True

        self.__has_volume = False
        if ctx.Volume_LA():
            self.__has_volume = True

        self.__has_rms = False
        if ctx.Dummy_Rms_LA():
            self.__has_rms = True

        self.__has_dummy_height = False
        if ctx.Dummy_H_LA():
            self.__has_dummy_height = True

        self.__has_s_n = False
        if ctx.S_N_LA():
            self.__has_s_n = True

        self.__has_lw_hz = False
        if ctx.Lw2_Hz_LA():
            self.__has_lw_hz = True

        self.__has_note = False
        if ctx.Note_LA():
            self.__has_note = True

        self.initSpectralDim()

    # Exit a parse tree produced by SparkyPKParser#data_label_wo_assign.
    def exitData_label_wo_assign(self, ctx: SparkyPKParser.Data_label_wo_assignContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by SparkyPKParser#peak_2d.
    def enterPeak_2d(self, ctx: SparkyPKParser.Peak_2dContext):  # pylint: disable=unused-argument
        if self.cur_subtype != 'peak2d':
            self.num_of_dim = 2
            self.initSpectralDim()

        self.peaks2D += 1

        self.atomSelectionSets.clear()
        self.asIsSets.clear()

    # Exit a parse tree produced by SparkyPKParser#peak_2d.
    def exitPeak_2d(self, ctx: SparkyPKParser.Peak_2dContext):

        try:

            if len(self.numberSelection) == 0:
                self.peaks2D -= 1
                return

            index = self.peaks2D

            ass = _ass_ = str(ctx.Assignment_2d_ex())
            if '?' in ass:
                ass = None
            if _ass_ == 'A1H-H' and not self.isFirstResidueAla:
                ass = _ass_ = None
            if _ass_ in ('?-?', None) and self.__has_note and len(self.__noteSelection) > 0:
                _ass_ = ' '.join(self.__noteSelection)

            x_ppm = float(str(ctx.Float(0)))
            y_ppm = float(str(ctx.Float(1)))

            offset = 0

            x_hz = y_hz = None
            if self.__has_hz:
                if len(self.numberSelection) > offset:
                    x_hz = self.numberSelection[offset]
                    offset += 1
                if len(self.numberSelection) > offset:
                    y_hz = self.numberSelection[offset]
                    offset += 1

            x_dev = y_dev = None
            if self.__has_dev:
                if len(self.numberSelection) > offset:
                    x_dev = self.numberSelection[offset]
                    offset += 1
                if len(self.numberSelection) > offset:
                    y_dev = self.numberSelection[offset]
                    offset += 1

            found_volume = False
            if self.__has_volume and self.__has_real_vol\
               and any(self.originalNumberSelection[_offset] == self.__real_vol for _offset in range(offset, len(self.originalNumberSelection))):
                found_volume = True

            if self.__has_dummy_height and found_volume:
                if not self.__has_height and len(self.originalNumberSelection) > offset:
                    height = self.originalNumberSelection[offset]
                    if height in ("0", "1"):
                        height = None
                offset += 1

            height = volume = None
            if self.__has_height and len(self.originalNumberSelection) > offset:
                height = self.originalNumberSelection[offset]
                offset += 1
            if self.__has_volume and len(self.originalNumberSelection) > offset:
                if self.__has_real_vol:
                    volume = self.__real_vol
                    if volume == self.originalNumberSelection[offset]:
                        offset += 1
                else:
                    volume = self.originalNumberSelection[offset]
                    offset += 1

            if self.__has_rms and found_volume:
                offset += 1

            if self.__has_s_n:
                offset += 1

            x_lw_hz = y_lw_hz = None
            if self.__has_lw_hz:
                if len(self.numberSelection) > offset:
                    x_lw_hz = self.numberSelection[offset]
                    offset += 1
                if len(self.numberSelection) > offset:
                    y_lw_hz = self.numberSelection[offset]
                    offset += 1

            if not self.hasPolySeq and not self.hasNonPolySeq:
                return

            if None in (x_ppm, y_ppm):
                self.peaks2D -= 1
                return

            dstFunc = self.validatePeak2D(index, x_ppm, y_ppm, x_dev, y_dev, None, None,
                                          x_hz, y_hz, x_lw_hz, y_lw_hz, height, None, volume, None)

            if dstFunc is None:
                self.peaks2D -= 1
                return

            cur_spectral_dim = self.spectral_dim[self.num_of_dim][self.cur_list_id]

            cur_spectral_dim[1]['freq_hint'].append(x_ppm)
            cur_spectral_dim[2]['freq_hint'].append(y_ppm)

            has_assignments = has_multiple_assignments = False
            asis1 = asis2 = None

            if ass is not None:
                assignments = []
                hint = None
                for _ass in ass.split('-'):
                    assignments.append(self.extractPeakAssignment(1, _ass, index, hint=hint))
                    hint = assignments[-1] if assignments[-1] is not None else None

                has_assignments, has_multiple_assignments, asis1, asis2 =\
                    self.checkAssignments2D(index, assignments, dstFunc)

                if not has_assignments and any(a[0]['comp_id'] == 'ARG' and a[0]['atom_id'] == 'NH' for a in assignments if a is not None):
                    _ass_ = ass.replace('NH', 'HN')
                    assignments = []
                    hint = None
                    for _ass in _ass_.split('-'):
                        assignments.append(self.extractPeakAssignment(1, _ass, index, hint=hint))
                        hint = assignments[-1] if assignments[-1] is not None else None

                    has_assignments, has_multiple_assignments, asis1, asis2 =\
                        self.checkAssignments2D(index, assignments, dstFunc)

            self.addAssignedPkRow2D(index, dstFunc, has_assignments, has_multiple_assignments,
                                    asis1, asis2,
                                    f'{ass} -> ',
                                    None if (has_assignments and not has_multiple_assignments)
                                    or _ass_ in ('?-?', None) else _ass_)

        finally:
            self.numberSelection.clear()
            self.originalNumberSelection.clear()
            self.__real_vol = None
            self.__noteSelection.clear()

    # Enter a parse tree produced by SparkyPKParser#peak_3d.
    def enterPeak_3d(self, ctx: SparkyPKParser.Peak_3dContext):  # pylint: disable=unused-argument
        if self.cur_subtype != 'peak3d':
            self.num_of_dim = 3
            self.initSpectralDim()

        self.peaks3D += 1

        self.atomSelectionSets.clear()
        self.asIsSets.clear()

    # Exit a parse tree produced by SparkyPKParser#peak_3d.
    def exitPeak_3d(self, ctx: SparkyPKParser.Peak_3dContext):

        try:

            if len(self.numberSelection) == 0:
                self.peaks3D -= 1
                return

            index = self.peaks3D

            ass = _ass_ = str(ctx.Assignment_3d_ex())
            if '?' in ass:
                ass = None
            if _ass_ == 'A1H-H-H' and not self.isFirstResidueAla:
                ass = _ass_ = None
            if _ass_ in ('?-?-?', None) and self.__has_note and len(self.__noteSelection) > 0:
                _ass_ = ' '.join(self.__noteSelection)

            x_ppm = float(str(ctx.Float(0)))
            y_ppm = float(str(ctx.Float(1)))
            z_ppm = float(str(ctx.Float(2)))

            offset = 0

            x_hz = y_hz = z_hz = None
            if self.__has_hz:
                if len(self.numberSelection) > offset:
                    x_hz = self.numberSelection[offset]
                    offset += 1
                if len(self.numberSelection) > offset:
                    y_hz = self.numberSelection[offset]
                    offset += 1
                if len(self.numberSelection) > offset:
                    z_hz = self.numberSelection[offset]
                    offset += 1

            x_dev = y_dev = z_dev = None
            if self.__has_dev:
                if len(self.numberSelection) > offset:
                    x_dev = self.numberSelection[offset]
                    offset += 1
                if len(self.numberSelection) > offset:
                    y_dev = self.numberSelection[offset]
                    offset += 1
                if len(self.numberSelection) > offset:
                    z_dev = self.numberSelection[offset]
                    offset += 1

            found_volume = False
            if self.__has_volume and self.__has_real_vol\
               and any(self.originalNumberSelection[_offset] == self.__real_vol for _offset in range(offset, len(self.originalNumberSelection))):
                found_volume = True

            if self.__has_dummy_height and found_volume:
                if not self.__has_height and len(self.originalNumberSelection) > offset:
                    height = self.originalNumberSelection[offset]
                    if height in ("0", "1"):
                        height = None
                offset += 1

            height = volume = None
            if self.__has_height and len(self.originalNumberSelection) > offset:
                height = self.originalNumberSelection[offset]
                offset += 1
            if self.__has_volume and len(self.originalNumberSelection) > offset:
                if self.__has_real_vol:
                    volume = self.__real_vol
                    if volume == self.originalNumberSelection[offset]:
                        offset += 1
                else:
                    volume = self.originalNumberSelection[offset]
                    offset += 1

            if self.__has_rms and found_volume:
                offset += 1

            if self.__has_s_n:
                offset += 1

            x_lw_hz = y_lw_hz = z_lw_hz = None
            if self.__has_lw_hz:
                if len(self.numberSelection) > offset:
                    x_lw_hz = self.numberSelection[offset]
                    offset += 1
                if len(self.numberSelection) > offset:
                    y_lw_hz = self.numberSelection[offset]
                    offset += 1
                if len(self.numberSelection) > offset:
                    z_lw_hz = self.numberSelection[offset]
                    offset += 1

            if not self.hasPolySeq and not self.hasNonPolySeq:
                return

            if None in (x_ppm, y_ppm, z_ppm):
                self.peaks3D -= 1
                return

            dstFunc = self.validatePeak3D(index, x_ppm, y_ppm, z_ppm, x_dev, y_dev, z_dev, None, None, None,
                                          x_hz, y_hz, z_hz, x_lw_hz, y_lw_hz, z_lw_hz, height, None, volume, None)

            if dstFunc is None:
                self.peaks3D -= 1
                return

            cur_spectral_dim = self.spectral_dim[self.num_of_dim][self.cur_list_id]

            cur_spectral_dim[1]['freq_hint'].append(x_ppm)
            cur_spectral_dim[2]['freq_hint'].append(y_ppm)
            cur_spectral_dim[3]['freq_hint'].append(z_ppm)

            has_assignments = has_multiple_assignments = False
            asis1 = asis2 = asis3 = None

            if ass is not None:
                assignments = []
                hint = None
                for _ass in ass.split('-'):
                    assignments.append(self.extractPeakAssignment(1, _ass, index, hint=hint))
                    hint = assignments[-1] if assignments[-1] is not None else None

                has_assignments, has_multiple_assignments, asis1, asis2, asis3 =\
                    self.checkAssignments3D(index, assignments, dstFunc)

                if not has_assignments and any(a[0]['comp_id'] == 'ARG' and a[0]['atom_id'] == 'NH' for a in assignments if a is not None):
                    _ass_ = ass.replace('NH', 'HN')
                    assignments = []
                    hint = None
                    for _ass in _ass_.split('-'):
                        assignments.append(self.extractPeakAssignment(1, _ass, index, hint=hint))
                        hint = assignments[-1] if assignments[-1] is not None else None

                    has_assignments, has_multiple_assignments, asis1, asis2, asis3 =\
                        self.checkAssignments3D(index, assignments, dstFunc)

            self.addAssignedPkRow3D(index, dstFunc, has_assignments, has_multiple_assignments,
                                    asis1, asis2, asis3,
                                    f'{ass} -> ',
                                    None if (has_assignments and not has_multiple_assignments)
                                    or _ass_ in ('?-?-?', None) else _ass_)

        finally:
            self.numberSelection.clear()
            self.originalNumberSelection.clear()
            self.__real_vol = None
            self.__noteSelection.clear()

    # Enter a parse tree produced by SparkyPKParser#peak_4d.
    def enterPeak_4d(self, ctx: SparkyPKParser.Peak_4dContext):  # pylint: disable=unused-argument
        if self.cur_subtype != 'peak4d':
            self.num_of_dim = 4
            self.initSpectralDim()

        self.peaks4D += 1

        self.atomSelectionSets.clear()
        self.asIsSets.clear()

    # Exit a parse tree produced by SparkyPKParser#peak_4d.
    def exitPeak_4d(self, ctx: SparkyPKParser.Peak_4dContext):

        try:

            if len(self.numberSelection) == 0:
                self.peaks4D -= 1
                return

            index = self.peaks4D

            ass = _ass_ = str(ctx.Assignment_4d_ex())
            if '?' in ass:
                ass = None
            if _ass_ == 'A1H-H-H-H' and not self.isFirstResidueAla:
                ass = _ass_ = None
            if _ass_ in ('?-?-?-?', None) and self.__has_note and len(self.__noteSelection) > 0:
                _ass_ = ' '.join(self.__noteSelection)

            x_ppm = float(str(ctx.Float(0)))
            y_ppm = float(str(ctx.Float(1)))
            z_ppm = float(str(ctx.Float(2)))
            a_ppm = float(str(ctx.Float(3)))

            offset = 0

            x_hz = y_hz = z_hz = a_hz = None
            if self.__has_hz:
                if len(self.numberSelection) > offset:
                    x_hz = self.numberSelection[offset]
                    offset += 1
                if len(self.numberSelection) > offset:
                    y_hz = self.numberSelection[offset]
                    offset += 1
                if len(self.numberSelection) > offset:
                    z_hz = self.numberSelection[offset]
                    offset += 1
                if len(self.numberSelection) > offset:
                    a_hz = self.numberSelection[offset]
                    offset += 1

            x_dev = y_dev = z_dev = a_dev = None
            if self.__has_dev:
                if len(self.numberSelection) > offset:
                    x_dev = self.numberSelection[offset]
                    offset += 1
                if len(self.numberSelection) > offset:
                    y_dev = self.numberSelection[offset]
                    offset += 1
                if len(self.numberSelection) > offset:
                    z_dev = self.numberSelection[offset]
                    offset += 1
                if len(self.numberSelection) > offset:
                    a_dev = self.numberSelection[offset]
                    offset += 1

            found_volume = False
            if self.__has_volume and self.__has_real_vol\
               and any(self.originalNumberSelection[_offset] == self.__real_vol for _offset in range(offset, len(self.originalNumberSelection))):
                found_volume = True

            if self.__has_dummy_height and found_volume:
                if not self.__has_height and len(self.originalNumberSelection) > offset:
                    height = self.originalNumberSelection[offset]
                    if height in ("0", "1"):
                        height = None
                offset += 1

            height = volume = None
            if self.__has_height and len(self.originalNumberSelection) > offset:
                height = self.originalNumberSelection[offset]
                offset += 1
            if self.__has_volume and len(self.originalNumberSelection) > offset:
                if self.__has_real_vol:
                    volume = self.__real_vol
                    if volume == self.originalNumberSelection[offset]:
                        offset += 1
                else:
                    volume = self.originalNumberSelection[offset]
                    offset += 1

            if self.__has_rms and found_volume:
                offset += 1

            if self.__has_s_n:
                offset += 1

            x_lw_hz = y_lw_hz = z_lw_hz = a_lw_hz = None
            if self.__has_lw_hz:
                if len(self.numberSelection) > offset:
                    x_lw_hz = self.numberSelection[offset]
                    offset += 1
                if len(self.numberSelection) > offset:
                    y_lw_hz = self.numberSelection[offset]
                    offset += 1
                if len(self.numberSelection) > offset:
                    z_lw_hz = self.numberSelection[offset]
                    offset += 1
                if len(self.numberSelection) > offset:
                    a_lw_hz = self.numberSelection[offset]
                    offset += 1

            if not self.hasPolySeq and not self.hasNonPolySeq:
                return

            if None in (x_ppm, y_ppm, z_ppm, a_ppm):
                self.peaks4D -= 1
                return

            dstFunc = self.validatePeak4D(index, x_ppm, y_ppm, z_ppm, a_ppm, x_dev, y_dev, z_dev, a_dev, None, None, None, None,
                                          x_hz, y_hz, z_hz, a_hz, x_lw_hz, y_lw_hz, z_lw_hz, a_lw_hz, height, None, volume, None)

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

            if ass is not None:
                assignments = []
                hint = None
                for _ass in ass.split('-'):
                    assignments.append(self.extractPeakAssignment(1, _ass, index, hint=hint))
                    hint = assignments[-1] if assignments[-1] is not None else None

                has_assignments, has_multiple_assignments, asis1, asis2, asis3, asis4 =\
                    self.checkAssignments4D(index, assignments, dstFunc)

                if not has_assignments and any(a[0]['comp_id'] == 'ARG' and a[0]['atom_id'] == 'NH' for a in assignments if a is not None):
                    _ass_ = ass.replace('NH', 'HN')
                    assignments = []
                    hint = None
                    for _ass in _ass_.split('-'):
                        assignments.append(self.extractPeakAssignment(1, _ass, index, hint=hint))
                        hint = assignments[-1] if assignments[-1] is not None else None

                    has_assignments, has_multiple_assignments, asis1, asis2, asis3, asis4 =\
                        self.checkAssignments4D(index, assignments, dstFunc)

            self.addAssignedPkRow4D(index, dstFunc, has_assignments, has_multiple_assignments,
                                    asis1, asis2, asis3, asis4,
                                    f'{ass} -> ',
                                    None if (has_assignments and not has_multiple_assignments)
                                    or _ass_ in ('?-?-?-?', None) else _ass_)

        finally:
            self.numberSelection.clear()
            self.originalNumberSelection.clear()
            self.__real_vol = None
            self.__noteSelection.clear()

    # Enter a parse tree produced by SparkyPKParser#peak_wo_assign.
    def enterPeak_wo_assign(self, ctx: SparkyPKParser.Peak_wo_assignContext):  # pylint: disable=unused-argument
        if self.num_of_dim == 2:
            self.peaks2D += 1
        elif self.num_of_dim == 3:
            self.peaks3D += 1
        elif self.num_of_dim == 4:
            self.peaks4D += 1

    # Exit a parse tree produced by SparkyPKParser#peak_wo_assign.
    def exitPeak_wo_assign(self, ctx: SparkyPKParser.Peak_wo_assignContext):  # pylint: disable=unused-argument

        try:

            if len(self.numberSelection) == 0:
                if self.num_of_dim == 2:
                    self.peaks2D -= 1
                elif self.num_of_dim == 3:
                    self.peaks3D -= 1
                elif self.num_of_dim == 4:
                    self.peaks4D -= 1
                return

            note = None
            if self.__has_note and len(self.__noteSelection) > 0:
                note = ' '.join(self.__noteSelection)

            offset = self.num_of_dim

            if self.num_of_dim == 2:

                try:

                    index = self.peaks2D
                    x_ppm = self.numberSelection[0]
                    y_ppm = self.numberSelection[1]

                    x_hz = y_hz = None
                    if self.__has_hz:
                        if len(self.numberSelection) > offset:
                            x_hz = self.numberSelection[offset]
                            offset += 1
                        if len(self.numberSelection) > offset:
                            y_hz = self.numberSelection[offset]
                            offset += 1

                    x_dev = y_dev = None
                    if self.__has_dev:
                        if len(self.numberSelection) > offset:
                            x_dev = self.numberSelection[offset]
                            offset += 1
                        if len(self.numberSelection) > offset:
                            y_dev = self.numberSelection[offset]
                            offset += 1

                    found_volume = False
                    if self.__has_volume and self.__has_real_vol\
                       and any(self.originalNumberSelection[_offset] == self.__real_vol for _offset in range(offset, len(self.originalNumberSelection))):
                        found_volume = True

                    if self.__has_dummy_height and found_volume:
                        if not self.__has_height and len(self.originalNumberSelection) > offset:
                            height = self.originalNumberSelection[offset]
                            if height in ("0", "1"):
                                height = None
                        offset += 1

                    height = volume = None
                    if self.__has_height and len(self.originalNumberSelection) > offset:
                        height = self.originalNumberSelection[offset]
                        offset += 1
                    if self.__has_volume and len(self.originalNumberSelection) > offset:
                        if self.__has_real_vol:
                            volume = self.__real_vol
                            if volume == self.originalNumberSelection[offset]:
                                offset += 1
                        else:
                            volume = self.originalNumberSelection[offset]
                            offset += 1

                    if self.__has_rms and found_volume:
                        offset += 1

                    if self.__has_s_n:
                        offset += 1

                    x_lw_hz = y_lw_hz = None
                    if self.__has_lw_hz:
                        if len(self.numberSelection) > offset:
                            x_lw_hz = self.numberSelection[offset]
                            offset += 1
                        if len(self.numberSelection) > offset:
                            y_lw_hz = self.numberSelection[offset]
                            offset += 1

                    if not self.hasPolySeq and not self.hasNonPolySeq:
                        return

                    if None in (x_ppm, y_ppm):
                        self.peaks2D -= 1
                        return

                    dstFunc = self.validatePeak2D(index, x_ppm, y_ppm, x_dev, y_dev, None, None,
                                                  x_hz, y_hz, x_lw_hz, y_lw_hz, height, None, volume, None)

                    if dstFunc is None:
                        self.peaks2D -= 1
                        return

                    cur_spectral_dim = self.spectral_dim[self.num_of_dim][self.cur_list_id]

                    cur_spectral_dim[1]['freq_hint'].append(x_ppm)
                    cur_spectral_dim[2]['freq_hint'].append(y_ppm)

                    if self.debug:
                        print(f"subtype={self.cur_subtype} id={self.peaks2D} (index={index}) {dstFunc}")

                    if self.createSfDict__:
                        sf = self.getSf()

                        if sf is not None:
                            sf['id'] = index
                            sf['index_id'] += 1

                            row = getPkRow(self.cur_subtype, sf['id'], sf['index_id'],
                                           sf['list_id'], self.entryId, dstFunc,
                                           None, None, None, details=note)
                            sf['loop'].add_data(row)

                except IndexError:
                    self.peaks2D -= 1
                    return

            elif self.num_of_dim == 3:

                try:

                    index = self.peaks3D
                    x_ppm = self.numberSelection[0]
                    y_ppm = self.numberSelection[1]
                    z_ppm = self.numberSelection[2]

                    x_hz = y_hz = z_hz = None
                    if self.__has_hz:
                        if len(self.numberSelection) > offset:
                            x_hz = self.numberSelection[offset]
                            offset += 1
                        if len(self.numberSelection) > offset:
                            y_hz = self.numberSelection[offset]
                            offset += 1
                        if len(self.numberSelection) > offset:
                            z_hz = self.numberSelection[offset]
                            offset += 1

                    x_dev = y_dev = z_dev = None
                    if self.__has_dev:
                        if len(self.numberSelection) > offset:
                            x_dev = self.numberSelection[offset]
                            offset += 1
                        if len(self.numberSelection) > offset:
                            y_dev = self.numberSelection[offset]
                            offset += 1
                        if len(self.numberSelection) > offset:
                            z_dev = self.numberSelection[offset]
                            offset += 1

                    found_volume = False
                    if self.__has_volume and self.__has_real_vol\
                       and any(self.originalNumberSelection[_offset] == self.__real_vol for _offset in range(offset, len(self.originalNumberSelection))):
                        found_volume = True

                    if self.__has_dummy_height and found_volume:
                        if not self.__has_height and len(self.originalNumberSelection) > offset:
                            height = self.originalNumberSelection[offset]
                            if height in ("0", "1"):
                                height = None
                        offset += 1

                    height = volume = None
                    if self.__has_height and len(self.originalNumberSelection) > offset:
                        height = self.originalNumberSelection[offset]
                        offset += 1
                    if self.__has_volume and len(self.originalNumberSelection) > offset:
                        if self.__has_real_vol:
                            volume = self.__real_vol
                            if volume == self.originalNumberSelection[offset]:
                                offset += 1
                        else:
                            volume = self.originalNumberSelection[offset]
                            offset += 1

                    if self.__has_rms and found_volume:
                        offset += 1

                    if self.__has_s_n:
                        offset += 1

                    x_lw_hz = y_lw_hz = z_lw_hz = None
                    if self.__has_lw_hz:
                        if len(self.numberSelection) > offset:
                            x_lw_hz = self.numberSelection[offset]
                            offset += 1
                        if len(self.numberSelection) > offset:
                            y_lw_hz = self.numberSelection[offset]
                            offset += 1
                        if len(self.numberSelection) > offset:
                            z_lw_hz = self.numberSelection[offset]
                            offset += 1

                    if not self.hasPolySeq and not self.hasNonPolySeq:
                        return

                    if None in (x_ppm, y_ppm, z_ppm):
                        self.peaks3D -= 1
                        return

                    dstFunc = self.validatePeak3D(index, x_ppm, y_ppm, z_ppm, x_dev, y_dev, z_dev, None, None, None,
                                                  x_hz, y_hz, z_hz, x_lw_hz, y_lw_hz, z_lw_hz, height, None, volume, None)

                    if dstFunc is None:
                        self.peaks3D -= 1
                        return

                    cur_spectral_dim = self.spectral_dim[self.num_of_dim][self.cur_list_id]

                    cur_spectral_dim[1]['freq_hint'].append(x_ppm)
                    cur_spectral_dim[2]['freq_hint'].append(y_ppm)
                    cur_spectral_dim[3]['freq_hint'].append(z_ppm)

                    if self.debug:
                        print(f"subtype={self.cur_subtype} id={self.peaks3D} (index={index}) {dstFunc}")

                    if self.createSfDict__:
                        sf = self.getSf()

                        if sf is not None:
                            sf['id'] = index
                            sf['index_id'] += 1

                            row = getPkRow(self.cur_subtype, sf['id'], sf['index_id'],
                                           sf['list_id'], self.entryId, dstFunc,
                                           None, None, None, details=note)
                            sf['loop'].add_data(row)

                except IndexError:
                    self.peaks3D -= 1
                    return

            elif self.num_of_dim == 4:

                try:

                    index = self.peaks4D
                    x_ppm = self.numberSelection[0]
                    y_ppm = self.numberSelection[1]
                    z_ppm = self.numberSelection[2]
                    a_ppm = self.numberSelection[3]

                    x_hz = y_hz = z_hz = a_hz = None
                    if self.__has_hz:
                        if len(self.numberSelection) > offset:
                            x_hz = self.numberSelection[offset]
                            offset += 1
                        if len(self.numberSelection) > offset:
                            y_hz = self.numberSelection[offset]
                            offset += 1
                        if len(self.numberSelection) > offset:
                            z_hz = self.numberSelection[offset]
                            offset += 1
                        if len(self.numberSelection) > offset:
                            a_hz = self.numberSelection[offset]
                            offset += 1

                    x_dev = y_dev = z_dev = a_dev = None
                    if self.__has_dev:
                        if len(self.numberSelection) > offset:
                            x_dev = self.numberSelection[offset]
                            offset += 1
                        if len(self.numberSelection) > offset:
                            y_dev = self.numberSelection[offset]
                            offset += 1
                        if len(self.numberSelection) > offset:
                            z_dev = self.numberSelection[offset]
                            offset += 1
                        if len(self.numberSelection) > offset:
                            a_dev = self.numberSelection[offset]
                            offset += 1

                    found_volume = False
                    if self.__has_volume and self.__has_real_vol\
                       and any(self.originalNumberSelection[_offset] == self.__real_vol for _offset in range(offset, len(self.originalNumberSelection))):
                        found_volume = True

                    if self.__has_dummy_height and found_volume:
                        if not self.__has_height and len(self.originalNumberSelection) > offset:
                            height = self.originalNumberSelection[offset]
                            if height in ("0", "1"):
                                height = None
                        offset += 1

                    height = volume = None
                    if self.__has_height and len(self.originalNumberSelection) > offset:
                        height = self.originalNumberSelection[offset]
                        offset += 1
                    if self.__has_volume and len(self.originalNumberSelection) > offset:
                        if self.__has_real_vol:
                            volume = self.__real_vol
                            if volume == self.originalNumberSelection[offset]:
                                offset += 1
                        else:
                            volume = self.originalNumberSelection[offset]
                            offset += 1

                    if self.__has_rms and found_volume:
                        offset += 1

                    if self.__has_s_n:
                        offset += 1

                    x_lw_hz = y_lw_hz = z_lw_hz = a_lw_hz = None
                    if self.__has_lw_hz:
                        if len(self.numberSelection) > offset:
                            x_lw_hz = self.numberSelection[offset]
                            offset += 1
                        if len(self.numberSelection) > offset:
                            y_lw_hz = self.numberSelection[offset]
                            offset += 1
                        if len(self.numberSelection) > offset:
                            z_lw_hz = self.numberSelection[offset]
                            offset += 1
                        if len(self.numberSelection) > offset:
                            a_lw_hz = self.numberSelection[offset]
                            offset += 1

                    if not self.hasPolySeq and not self.hasNonPolySeq:
                        return

                    if None in (x_ppm, y_ppm, z_ppm, a_ppm):
                        self.peaks4D -= 1
                        return

                    dstFunc = self.validatePeak4D(index, x_ppm, y_ppm, z_ppm, a_ppm, x_dev, y_dev, z_dev, a_dev, None, None, None, None,
                                                  x_hz, y_hz, z_hz, a_hz, x_lw_hz, y_lw_hz, z_lw_hz, a_lw_hz, height, None, volume, None)

                    if dstFunc is None:
                        self.peaks4D -= 1
                        return

                    cur_spectral_dim = self.spectral_dim[self.num_of_dim][self.cur_list_id]

                    cur_spectral_dim[1]['freq_hint'].append(x_ppm)
                    cur_spectral_dim[2]['freq_hint'].append(y_ppm)
                    cur_spectral_dim[3]['freq_hint'].append(z_ppm)
                    cur_spectral_dim[4]['freq_hint'].append(a_ppm)

                    if self.debug:
                        print(f"subtype={self.cur_subtype} id={self.peaks4D} (index={index}) {dstFunc}")

                    if self.createSfDict__:
                        sf = self.getSf()

                        if sf is not None:
                            sf['id'] = index
                            sf['index_id'] += 1

                            row = getPkRow(self.cur_subtype, sf['id'], sf['index_id'],
                                           sf['list_id'], self.entryId, dstFunc,
                                           None, None, None, details=note)
                            sf['loop'].add_data(row)

                except IndexError:
                    self.peaks4D -= 1
                    return

        finally:
            self.numberSelection.clear()
            self.originalNumberSelection.clear()
            self.__real_vol = None
            self.__noteSelection.clear()

    # Enter a parse tree produced by SparkyPKParser#number.
    def enterNumber(self, ctx: SparkyPKParser.NumberContext):

        try:

            if ctx.Float():
                value = str(ctx.Float())
                self.numberSelection.append(float(value))
                self.originalNumberSelection.append(value)

            elif ctx.Real():
                value = str(ctx.Real())
                self.numberSelection.append(float(value))
                self.originalNumberSelection.append(value)

            elif ctx.Real_vol():
                self.__has_real_vol = True
                if self.reasons is None and 'has_real_vol' not in self.reasonsForReParsing:
                    self.reasonsForReParsing['has_real_vol'] = True
                value = str(ctx.Real_vol())
                if ' ' in value:
                    value = value.split()[0]
                    self.__real_vol = value
                self.numberSelection.append(float(value))
                self.originalNumberSelection.append(value)

            else:
                value = str(ctx.Integer())
                self.numberSelection.append(int(value))
                self.originalNumberSelection.append(value)

        except ValueError:
            self.numberSelection.append(None)
            self.originalNumberSelection.append(None)

    # Exit a parse tree produced by SparkyPKParser#number.
    def exitNumber(self, ctx: SparkyPKParser.NumberContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by SparkyPKParser#note.
    def enterNote(self, ctx: SparkyPKParser.NoteContext):
        if ctx.Simple_name():
            self.__noteSelection.append(str(ctx.Simple_name()))

        elif ctx.Float():
            self.__noteSelection.append(str(ctx.Float()))

        elif ctx.Integer():
            self.__noteSelection.append(str(ctx.Integer()))

        elif ctx.Note_2d_ex():
            self.__noteSelection.append(str(ctx.Note_2d_ex()))

        elif ctx.Note_3d_ex():
            self.__noteSelection.append(str(ctx.Note_3d_ex()))

        elif ctx.Note_4d_ex():
            self.__noteSelection.append(str(ctx.Note_4d_ex()))

    # Exit a parse tree produced by SparkyPKParser#note.
    def exitNote(self, ctx: SparkyPKParser.NoteContext):  # pylint: disable=unused-argument
        pass


# del SparkyPKParser
