##
# File: NmrPipePKParserListener.py
# Date: 03-Dec-2024
#
# Updates:
""" ParserLister class for NMRPIPE PK files.
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
import math

from antlr4 import ParseTreeListener
from typing import IO, List, Optional

try:
    from wwpdb.utils.nmr.io.CifReader import CifReader
    from wwpdb.utils.nmr.pk.NmrPipePKParser import NmrPipePKParser
    from wwpdb.utils.nmr.pk.BasePKParserListener import BasePKParserListener
    from wwpdb.utils.nmr.mr.ParserListenerUtil import (ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS,
                                                       REPRESENTATIVE_MODEL_ID,
                                                       REPRESENTATIVE_ALT_ID,
                                                       SPECTRAL_DIM_TEMPLATE,
                                                       getMaxEffDigits,
                                                       roundString)
    from wwpdb.utils.nmr.ChemCompUtil import ChemCompUtil
    from wwpdb.utils.nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from wwpdb.utils.nmr.nef.NEFTranslator import NEFTranslator
    from wwpdb.utils.nmr.AlignUtil import emptyValue
except ImportError:
    from nmr.io.CifReader import CifReader
    from nmr.pk.NmrPipePKParser import NmrPipePKParser
    from nmr.pk.BasePKParserListener import BasePKParserListener
    from nmr.mr.ParserListenerUtil import (ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS,
                                           REPRESENTATIVE_MODEL_ID,
                                           REPRESENTATIVE_ALT_ID,
                                           SPECTRAL_DIM_TEMPLATE,
                                           getMaxEffDigits,
                                           roundString)
    from nmr.ChemCompUtil import ChemCompUtil
    from nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from nmr.nef.NEFTranslator import NEFTranslator
    from nmr.AlignUtil import emptyValue


# This class defines a complete listener for a parse tree produced by NmrPipePKParser.
class NmrPipePKParserListener(ParseTreeListener, BasePKParserListener):

    def __init__(self, verbose: bool = True, log: IO = sys.stdout,
                 representativeModelId: int = REPRESENTATIVE_MODEL_ID,
                 representativeAltId: str = REPRESENTATIVE_ALT_ID,
                 mrAtomNameMapping: Optional[List[dict]] = None,
                 cR: Optional[CifReader] = None, caC: Optional[dict] = None, ccU: Optional[ChemCompUtil] = None,
                 csStat: Optional[BMRBChemShiftStat] = None, nefT: Optional[NEFTranslator] = None,
                 reasons: Optional[dict] = None):
        super().__init__(verbose, log, representativeModelId, representativeAltId,
                         mrAtomNameMapping, cR, caC, ccU, csStat, nefT, reasons)

        self.file_type = 'nm-pea-pip'
        self.software_name = 'NMRPIPE'

    # Enter a parse tree produced by NmrPipePKParser#nmrpipe_pk.
    def enterNmrpipe_pk(self, ctx: NmrPipePKParser.Nmrpipe_pkContext):  # pylint: disable=unused-argument
        self.enter()

    # Exit a parse tree produced by NmrPipePKParser#dynamo_mr.
    def exitNmrpipe_pk(self, ctx: NmrPipePKParser.Nmrpipe_pkContext):  # pylint: disable=unused-argument
        self.exit()

    # Enter a parse tree produced by NmrPipePKParser#data_label.
    def enterData_label(self, ctx: NmrPipePKParser.Data_labelContext):

        def set_spectral_dim(_dim_id):
            self.num_of_dim = max(self.num_of_dim, _dim_id)
            if _dim_id not in self.cur_spectral_dim:
                cur_spectral_dim = copy.copy(SPECTRAL_DIM_TEMPLATE)
            else:
                cur_spectral_dim = self.cur_spectral_dim[_dim_id]

            if ctx.Simple_name_DA():
                cur_spectral_dim['axis_code'] = axis_code = str(ctx.Simple_name_DA())
                if axis_code not in emptyValue:
                    digits = re.findall(r'\d+', axis_code)
                    for digit in digits:
                        num = int(digit)
                        nuc = next((k for k, v in ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS.items() if num == v[0]), None)
                        if nuc is not None:
                            cur_spectral_dim['atom_type'] = nuc
                            cur_spectral_dim['atom_isotope_number'] = num
                            break
                    if cur_spectral_dim['atom_type'] is None:
                        for a in axis_code:
                            a = a.upper()
                            if a in ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS:
                                cur_spectral_dim['atom_type'] = a
                                cur_spectral_dim['atom_isotope_number'] = ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS[a][0]
                                break

            truncated = False
            first_point = last_point = None
            if ctx.Integer_DA(0) and ctx.Integer_DA(1):
                first_point = int(str(ctx.Integer_DA(0)))
                last_point = int(str(ctx.Integer_DA(1)))

                truncated |= first_point != 1
                log2_last_point = math.log2(float(last_point))
                round_log2_last_point = int(log2_last_point)
                truncated |= log2_last_point - round_log2_last_point > 0.001

            isotope_number = cur_spectral_dim['atom_isotope_number']

            cur_spectral_dim['acquisition'] = 'yes' if _dim_id == self.acq_dim_id\
                and (isotope_number == 1 or (isotope_number == 13 and self.exptlMethod == 'SOLID-STATE NMR')) else 'no'

            if _dim_id == 1 and cur_spectral_dim['acquisition'] == 'no':
                self.acq_dim_id = self.num_of_dim

            cur_spectral_dim['under_sampling_type'] = 'not observed' if cur_spectral_dim['acquisition'] == 'yes' else 'aliased'

            if ctx.Ppm_value_DA(0) and ctx.Ppm_value_DA(1):
                row = [str(ctx.Ppm_value_DA(0)).replace('ppm', ''),
                       str(ctx.Ppm_value_DA(1)).replace('ppm', '')]

                max_eff_digits = getMaxEffDigits(row)

                first_ppm = float(row[0])
                last_ppm = float(row[1])
                cur_spectral_dim['value_first_point'] = first_ppm
                cur_spectral_dim['center_frequency_offset'] = float(roundString(str((first_ppm + last_ppm) / 2.0),
                                                                                max_eff_digits))

                if truncated and isotope_number in (1, 13, 15):
                    _last_point = int(pow(2.0, round_log2_last_point + 1.0))
                    scale = float(_last_point) / float(last_point - first_point - 1)
                    center = first_ppm - (first_ppm - last_ppm) * scale / 2

                    if isotope_number == 1:
                        if not 4 < center < 6:
                            __last_point = _last_point + _last_point / 2
                            _scale = float(__last_point) / float(last_point - first_point - 1)
                            center = first_ppm - (first_ppm - last_ppm) * _scale / 2
                            if 4 < center < 6:
                                scale = _scale
                            else:
                                __last_point = _last_point + _last_point
                                _scale = float(__last_point) / float(last_point - first_point - 1)
                                center = first_ppm - (first_ppm - last_ppm) * _scale / 2
                                if 4 < center < 6:
                                    scale = _scale

                    cur_spectral_dim['sweep_width'] = float(roundString(str((first_ppm - last_ppm) * scale),
                                                                        max_eff_digits))
                else:
                    cur_spectral_dim['sweep_width'] = float(roundString(str(first_ppm - last_ppm),
                                                                        max_eff_digits))

                cur_spectral_dim['sweep_width_units'] = 'ppm'

            self.cur_spectral_dim[_dim_id] = cur_spectral_dim

        if ctx.X_axis_DA():
            set_spectral_dim(1)
        elif ctx.Y_axis_DA():
            set_spectral_dim(2)
        elif ctx.Z_axis_DA():
            set_spectral_dim(3)
        elif ctx.A_axis_DA():
            set_spectral_dim(4)

    # Exit a parse tree produced by NmrPipePKParser#data_label.
    def exitData_label(self, ctx: NmrPipePKParser.Data_labelContext):  # pylint: disable=unused-argument
        if self.num_of_dim > 2 and self.exptlMethod != 'SOLID-STATE NMR':
            for _dim_id in range(2, self.num_of_dim + 1):
                cur_spectral_dim = self.cur_spectral_dim[_dim_id]
                if cur_spectral_dim['atom_isotope_number'] != 13:
                    continue
                if cur_spectral_dim['center_frequency_offset'] > 100.0:
                    continue
                if cur_spectral_dim['sweep_width'] < 50.0:
                    cur_spectral_dim['under_sampling_type'] = 'folded'

    # Enter a parse tree produced by NmrPipePKParser#peak_list_2d.
    def enterPeak_list_2d(self, ctx: NmrPipePKParser.Peak_list_2dContext):
        self.initSpectralDim()

        self.null_value = str(ctx.Null_value()) if ctx.Null_value() else None
        self.null_string = str(ctx.Null_string()) if ctx.Null_string() else None
        self.software_name = 'NMRPIPE'

    # Exit a parse tree produced by NmrPipePKParser#peak_list_2d.
    def exitPeak_list_2d(self, ctx: NmrPipePKParser.Peak_list_2dContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by NmrPipePKParser#peak_2d.
    def enterPeak_2d(self, ctx: NmrPipePKParser.Peak_2dContext):  # pylint: disable=unused-argument
        self.peaks2D += 1

        self.atomSelectionSets.clear()
        self.asIsSets.clear()

    # Exit a parse tree produced by NmrPipePKParser#peak_2d.
    def exitPeak_2d(self, ctx: NmrPipePKParser.Peak_2dContext):

        try:

            if len(self.numberSelection) == 0:
                self.peaks2D -= 1
                return

            try:

                index = int(str(ctx.Integer(0)))
                # x_axis = self.numberSelection[0]
                # y_axis = self.numberSelection[1]
                # dx = self.numberSelection[2]
                # dy = self.numberSelection[3]
                x_ppm = self.numberSelection[4]
                y_ppm = self.numberSelection[5]
                x_hz = self.numberSelection[6]
                y_hz = self.numberSelection[7]
                # xw = self.numberSelection[8]
                # yw = self.numberSelection[9]
                xw_hz = self.numberSelection[10]
                yw_hz = self.numberSelection[11]
                # x1 = int(str(ctx.Integer(1)))
                # x3 = int(str(ctx.Integer(2)))
                # y1 = int(str(ctx.Integer(3)))
                # y3 = int(str(ctx.Integer(4)))
                height = self.originalNumberSelection[12]
                dheight = self.originalNumberSelection[13]
                vol = self.originalNumberSelection[14]
                # pchi2 = self.originalNumberSelection[15]
                # type = int(str(ctx.Integer(5)))

            except IndexError:
                self.peaks2D -= 1
                return

            if ctx.Any_name():
                ass = str(ctx.Any_name())
                if ass in emptyValue or (self.null_string is not None and ass == self.null_string):
                    ass = None
            else:
                ass = None
            # clustid = int(str(ctx.Integer(6)))
            # memcnt = int(str(ctx.Integer(7)))

            if not self.hasPolySeq and not self.hasNonPolySeq:
                return

            if None in (x_ppm, y_ppm):  # or type != 1:
                self.peaks2D -= 1
                return

            dstFunc = self.validatePeak2D(index, x_ppm, y_ppm, None, None, None, None,
                                          x_hz, y_hz, xw_hz, yw_hz, height, dheight, vol, None)

            if dstFunc is None:
                self.peaks2D -= 1
                return

            if self.num_of_dim != 2:
                self.num_of_dim = 2
                self.initSpectralDim()

            cur_spectral_dim = self.spectral_dim[self.num_of_dim][self.cur_list_id]

            cur_spectral_dim[1]['freq_hint'].append(x_ppm)
            cur_spectral_dim[2]['freq_hint'].append(y_ppm)

            if x_ppm is not None and x_hz is not None and cur_spectral_dim[1]['spectrometer_frequency'] is None\
               and isinstance(cur_spectral_dim[1]['value_first_point'], float):
                cur_spectral_dim[1]['obs_freq_hint'].append(float(roundString(str(x_hz / (cur_spectral_dim[1]['value_first_point'] - x_ppm)),
                                                                              getMaxEffDigits([str(x_ppm), str(x_hz)]))))
            if y_ppm is not None and y_hz is not None and cur_spectral_dim[2]['spectrometer_frequency'] is None\
               and isinstance(cur_spectral_dim[2]['value_first_point'], float):
                cur_spectral_dim[2]['obs_freq_hint'].append(float(roundString(str(y_hz / (cur_spectral_dim[2]['value_first_point'] - y_ppm)),
                                                                              getMaxEffDigits([str(y_ppm), str(y_hz)]))))

            has_assignments = has_multiple_assignments = False
            asis1 = asis2 = None

            if ass is not None:
                assignments = []
                if len(ass.split('-')) == self.num_of_dim:
                    hint = None
                    for _ass in ass.split('-'):
                        assignments.append(self.extractPeakAssignment(1, _ass, index, hint=hint))
                        hint = assignments[-1] if assignments[-1] is not None else None
                elif len(ass.split(':')) == self.num_of_dim:
                    hint = None
                    for _ass in ass.split(':'):
                        assignments.append(self.extractPeakAssignment(1, _ass, index, hint=hint))
                        hint = assignments[-1] if assignments[-1] is not None else None
                elif len(ass.split(';')) == self.num_of_dim:
                    hint = None
                    for _ass in ass.split(';'):
                        assignments.append(self.extractPeakAssignment(1, _ass, index, hint=hint))
                        hint = assignments[-1] if assignments[-1] is not None else None
                elif len(ass.split(',')) == self.num_of_dim:
                    hint = None
                    for _ass in ass.split(','):
                        assignments.append(self.extractPeakAssignment(1, _ass, index, hint=hint))
                        hint = assignments[-1] if assignments[-1] is not None else None
                else:
                    assignments = [None] * self.num_of_dim
                    _assignments = self.extractPeakAssignment(self.num_of_dim, ass, index)
                    if _assignments is not None and len(_assignments) == self.num_of_dim:
                        for idx in range(self.num_of_dim):
                            assignments[idx] = [_assignments[idx]]  # pylint: disable=unsubscriptable-object

                has_assignments, has_multiple_assignments, asis1, asis2 =\
                    self.checkAssignments2D(index, assignments, dstFunc)

            self.addAssignedPkRow2D(index, dstFunc, has_assignments, has_multiple_assignments,
                                    asis1, asis2,
                                    f'{ass} -> ',
                                    None if has_assignments and not has_multiple_assignments else ass)

        finally:
            self.numberSelection.clear()
            self.originalNumberSelection.clear()

    # Enter a parse tree produced by NmrPipePKParser#peak_list_3d.
    def enterPeak_list_3d(self, ctx: NmrPipePKParser.Peak_list_3dContext):
        self.initSpectralDim()

        self.null_value = str(ctx.Null_value()) if ctx.Null_value() else None
        self.null_string = str(ctx.Null_string()) if ctx.Null_string() else None
        self.software_name = 'NMRPIPE'

    # Exit a parse tree produced by NmrPipePKParser#peak_list_3d.
    def exitPeak_list_3d(self, ctx: NmrPipePKParser.Peak_list_3dContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by NmrPipePKParser#peak_3d.
    def enterPeak_3d(self, ctx: NmrPipePKParser.Peak_3dContext):  # pylint: disable=unused-argument
        self.peaks3D += 1

        self.atomSelectionSets.clear()
        self.asIsSets.clear()

    # Exit a parse tree produced by NmrPipePKParser#peak_3d.
    def exitPeak_3d(self, ctx: NmrPipePKParser.Peak_3dContext):

        try:

            if len(self.numberSelection) == 0:
                self.peaks3D -= 1
                return

            try:

                index = int(str(ctx.Integer(0)))
                # x_axis = self.numberSelection[0]
                # y_axis = self.numberSelection[1]
                # z_axis = self.numberSelection[2]
                # dx = self.numberSelection[3]
                # dy = self.numberSelection[4]
                # dz = self.numberSelection[5]
                x_ppm = self.numberSelection[6]
                y_ppm = self.numberSelection[7]
                z_ppm = self.numberSelection[8]
                x_hz = self.numberSelection[9]
                y_hz = self.numberSelection[10]
                z_hz = self.numberSelection[11]
                # xw = self.numberSelection[12]
                # yw = self.numberSelection[13]
                # zw = self.numberSelection[14]
                xw_hz = self.numberSelection[15]
                yw_hz = self.numberSelection[16]
                zw_hz = self.numberSelection[17]
                # x1 = int(str(ctx.Integer(1)))
                # x3 = int(str(ctx.Integer(2)))
                # y1 = int(str(ctx.Integer(3)))
                # y3 = int(str(ctx.Integer(4)))
                # z1 = int(str(ctx.Integer(5)))
                # z3 = int(str(ctx.Integer(6)))
                height = self.originalNumberSelection[18]
                dheight = self.originalNumberSelection[19]
                vol = self.originalNumberSelection[20]
                # pchi2 = self.originalNumberSelection[21]
                # type = int(str(ctx.Integer(7)))

            except IndexError:
                self.peaks3D -= 1
                return

            if ctx.Any_name():
                ass = str(ctx.Any_name())
                if ass in emptyValue or (self.null_string is not None and ass == self.null_string):
                    ass = None
            else:
                ass = None
            # clustid = int(str(ctx.Integer(8)))
            # memcnt = int(str(ctx.Integer(9)))

            if not self.hasPolySeq and not self.hasNonPolySeq:
                return

            if None in (x_ppm, y_ppm, z_ppm):  # or type != 1:
                self.peaks3D -= 1
                return

            dstFunc = self.validatePeak3D(index, x_ppm, y_ppm, z_ppm, None, None, None, None, None, None,
                                          x_hz, y_hz, z_hz, xw_hz, yw_hz, zw_hz, height, dheight, vol, None)

            if dstFunc is None:
                self.peaks3D -= 1
                return

            if self.num_of_dim != 3:
                self.num_of_dim = 3
                self.initSpectralDim()

            cur_spectral_dim = self.spectral_dim[self.num_of_dim][self.cur_list_id]

            cur_spectral_dim[1]['freq_hint'].append(x_ppm)
            cur_spectral_dim[2]['freq_hint'].append(y_ppm)
            cur_spectral_dim[3]['freq_hint'].append(z_ppm)

            if x_ppm is not None and x_hz is not None and cur_spectral_dim[1]['spectrometer_frequency'] is None\
               and isinstance(cur_spectral_dim[1]['value_first_point'], float):
                cur_spectral_dim[1]['obs_freq_hint'].append(float(roundString(str(x_hz / (cur_spectral_dim[1]['value_first_point'] - x_ppm)),
                                                                              getMaxEffDigits([str(x_ppm), str(x_hz)]))))
            if y_ppm is not None and y_hz is not None and cur_spectral_dim[2]['spectrometer_frequency'] is None\
               and isinstance(cur_spectral_dim[2]['value_first_point'], float):
                cur_spectral_dim[2]['obs_freq_hint'].append(float(roundString(str(y_hz / (cur_spectral_dim[2]['value_first_point'] - y_ppm)),
                                                                              getMaxEffDigits([str(y_ppm), str(y_hz)]))))
            if z_ppm is not None and z_hz is not None and cur_spectral_dim[3]['spectrometer_frequency'] is None\
               and isinstance(cur_spectral_dim[3]['value_first_point'], float):
                cur_spectral_dim[3]['obs_freq_hint'].append(float(roundString(str(z_hz / (cur_spectral_dim[3]['value_first_point'] - z_ppm)),
                                                                              getMaxEffDigits([str(z_ppm), str(z_hz)]))))

            has_assignments = has_multiple_assignments = False
            asis1 = asis2 = asis3 = None

            if ass is not None:
                assignments = []
                if len(ass.split('-')) == self.num_of_dim:
                    hint = None
                    for _ass in ass.split('-'):
                        assignments.append(self.extractPeakAssignment(1, _ass, index, hint=hint))
                        hint = assignments[-1] if assignments[-1] is not None else None
                elif len(ass.split(':')) == self.num_of_dim:
                    hint = None
                    for _ass in ass.split(':'):
                        assignments.append(self.extractPeakAssignment(1, _ass, index, hint=hint))
                        hint = assignments[-1] if assignments[-1] is not None else None
                elif len(ass.split(';')) == self.num_of_dim:
                    hint = None
                    for _ass in ass.split(';'):
                        assignments.append(self.extractPeakAssignment(1, _ass, index, hint=hint))
                        hint = assignments[-1] if assignments[-1] is not None else None
                elif len(ass.split(',')) == self.num_of_dim:
                    hint = None
                    for _ass in ass.split(','):
                        assignments.append(self.extractPeakAssignment(1, _ass, index, hint=hint))
                        hint = assignments[-1] if assignments[-1] is not None else None
                else:
                    assignments = [None] * self.num_of_dim
                    _assignments = self.extractPeakAssignment(self.num_of_dim, ass, index)
                    if _assignments is not None and len(_assignments) == self.num_of_dim:
                        for idx in range(self.num_of_dim):
                            assignments[idx] = [_assignments[idx]]  # pylint: disable=unsubscriptable-object

                has_assignments, has_multiple_assignments, asis1, asis2, asis3 =\
                    self.checkAssignments3D(index, assignments, dstFunc)

            self.addAssignedPkRow3D(index, dstFunc, has_assignments, has_multiple_assignments,
                                    asis1, asis2, asis3,
                                    f'{ass} -> ',
                                    None if has_assignments and not has_multiple_assignments else ass)

        finally:
            self.numberSelection.clear()
            self.originalNumberSelection.clear()

    # Enter a parse tree produced by NmrPipePKParser#peak_list_4d.
    def enterPeak_list_4d(self, ctx: NmrPipePKParser.Peak_list_4dContext):
        self.initSpectralDim()

        self.null_value = str(ctx.Null_value()) if ctx.Null_value() else None
        self.null_string = str(ctx.Null_string()) if ctx.Null_string() else None
        self.software_name = 'NMRPIPE'

    # Exit a parse tree produced by NmrPipePKParser#peak_list_4d.
    def exitPeak_list_4d(self, ctx: NmrPipePKParser.Peak_list_4dContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by NmrPipePKParser#peak_4d.
    def enterPeak_4d(self, ctx: NmrPipePKParser.Peak_4dContext):  # pylint: disable=unused-argument
        self.peaks4D += 1

        self.atomSelectionSets.clear()
        self.asIsSets.clear()

    # Exit a parse tree produced by NmrPipePKParser#peak_4d.
    def exitPeak_4d(self, ctx: NmrPipePKParser.Peak_4dContext):

        try:

            if len(self.numberSelection) == 0:
                self.peaks4D -= 1
                return

            try:

                index = int(str(ctx.Integer(0)))
                # x_axis = self.numberSelection[0]
                # y_axis = self.numberSelection[1]
                # z_axis = self.numberSelection[2]
                # a_axis = self.numberSelection[3]
                # dx = self.numberSelection[4]
                # dy = self.numberSelection[5]
                # dz = self.numberSelection[6]
                # da = self.numberSelection[7]
                x_ppm = self.numberSelection[8]
                y_ppm = self.numberSelection[9]
                z_ppm = self.numberSelection[10]
                a_ppm = self.numberSelection[11]
                x_hz = self.numberSelection[12]
                y_hz = self.numberSelection[13]
                z_hz = self.numberSelection[14]
                a_hz = self.numberSelection[15]
                # xw = self.numberSelection[16]
                # yw = self.numberSelection[17]
                # zw = self.numberSelection[18]
                # aw = self.numberSelection[19]
                xw_hz = self.numberSelection[20]
                yw_hz = self.numberSelection[21]
                zw_hz = self.numberSelection[22]
                aw_hz = self.numberSelection[23]
                # x1 = int(str(ctx.Integer(1)))
                # x3 = int(str(ctx.Integer(2)))
                # y1 = int(str(ctx.Integer(3)))
                # y3 = int(str(ctx.Integer(4)))
                # z1 = int(str(ctx.Integer(5)))
                # z3 = int(str(ctx.Integer(6)))
                # a1 = int(str(ctx.Integer(7)))
                # a3 = int(str(ctx.Integer(8)))
                height = self.originalNumberSelection[24]
                dheight = self.originalNumberSelection[25]
                vol = self.originalNumberSelection[26]
                # pchi2 = self.originalNumberSelection[27]
                # type = int(str(ctx.Integer(9)))

            except IndexError:
                self.peaks4D -= 1
                return

            if ctx.Any_name():
                ass = str(ctx.Any_name())
                if ass in emptyValue or (self.null_string is not None and ass == self.null_string):
                    ass = None
            else:
                ass = None
            # clustid = int(str(ctx.Integer(10)))
            # memcnt = int(str(ctx.Integer(11)))

            if not self.hasPolySeq and not self.hasNonPolySeq:
                return

            if None in (x_ppm, y_ppm, z_ppm, a_ppm):  # or type != 1:
                self.peaks4D -= 1
                return

            dstFunc = self.validatePeak4D(index, x_ppm, y_ppm, z_ppm, a_ppm, None, None, None, None, None, None, None, None,
                                          x_hz, y_hz, z_hz, a_hz, xw_hz, yw_hz, zw_hz, aw_hz, height, dheight, vol, None)

            if dstFunc is None:
                self.peaks4D -= 1
                return

            if self.num_of_dim != 4:
                self.num_of_dim = 4
                self.initSpectralDim()

            cur_spectral_dim = self.spectral_dim[self.num_of_dim][self.cur_list_id]

            cur_spectral_dim[1]['freq_hint'].append(x_ppm)
            cur_spectral_dim[2]['freq_hint'].append(y_ppm)
            cur_spectral_dim[3]['freq_hint'].append(z_ppm)
            cur_spectral_dim[4]['freq_hint'].append(a_ppm)

            if x_ppm is not None and x_hz is not None and cur_spectral_dim[1]['spectrometer_frequency'] is None\
               and isinstance(cur_spectral_dim[1]['value_first_point'], float):
                cur_spectral_dim[1]['obs_freq_hint'].append(float(roundString(str(x_hz / (cur_spectral_dim[1]['value_first_point'] - x_ppm)),
                                                                              getMaxEffDigits([str(x_ppm), str(x_hz)]))))
            if y_ppm is not None and y_hz is not None and cur_spectral_dim[2]['spectrometer_frequency'] is None\
               and isinstance(cur_spectral_dim[2]['value_first_point'], float):
                cur_spectral_dim[2]['obs_freq_hint'].append(float(roundString(str(y_hz / (cur_spectral_dim[2]['value_first_point'] - y_ppm)),
                                                                              getMaxEffDigits([str(y_ppm), str(y_hz)]))))
            if z_ppm is not None and z_hz is not None and cur_spectral_dim[3]['spectrometer_frequency'] is None\
               and isinstance(cur_spectral_dim[3]['value_first_point'], float):
                cur_spectral_dim[3]['obs_freq_hint'].append(float(roundString(str(z_hz / (cur_spectral_dim[3]['value_first_point'] - z_ppm)),
                                                                              getMaxEffDigits([str(z_ppm), str(z_hz)]))))
            if a_ppm is not None and a_hz is not None and cur_spectral_dim[4]['spectrometer_frequency'] is None\
               and isinstance(cur_spectral_dim[4]['value_first_point'], float):
                cur_spectral_dim[4]['obs_freq_hint'].append(float(roundString(str(a_hz / (cur_spectral_dim[4]['value_first_point'] - a_ppm)),
                                                                              getMaxEffDigits([str(a_ppm), str(a_hz)]))))

            has_assignments = has_multiple_assignments = False
            asis1 = asis2 = asis3 = asis4 = None

            if ass is not None:
                assignments = []
                if len(ass.split('-')) == self.num_of_dim:
                    hint = None
                    for _ass in ass.split('-'):
                        assignments.append(self.extractPeakAssignment(1, _ass, index, hint=hint))
                        hint = assignments[-1] if assignments[-1] is not None else None
                elif len(ass.split(':')) == self.num_of_dim:
                    hint = None
                    for _ass in ass.split(':'):
                        assignments.append(self.extractPeakAssignment(1, _ass, index, hint=hint))
                        hint = assignments[-1] if assignments[-1] is not None else None
                elif len(ass.split(';')) == self.num_of_dim:
                    hint = None
                    for _ass in ass.split(';'):
                        assignments.append(self.extractPeakAssignment(1, _ass, index, hint=hint))
                        hint = assignments[-1] if assignments[-1] is not None else None
                elif len(ass.split(',')) == self.num_of_dim:
                    hint = None
                    for _ass in ass.split(','):
                        assignments.append(self.extractPeakAssignment(1, _ass, index, hint=hint))
                        hint = assignments[-1] if assignments[-1] is not None else None
                else:
                    assignments = [None] * self.num_of_dim
                    _assignments = self.extractPeakAssignment(self.num_of_dim, ass, index)
                    if _assignments is not None and len(_assignments) == self.num_of_dim:
                        for idx in range(self.num_of_dim):
                            assignments[idx] = [_assignments[idx]]  # pylint: disable=unsubscriptable-object

                has_assignments, has_multiple_assignments, asis1, asis2, asis3, asis4 =\
                    self.checkAssignments4D(index, assignments, dstFunc)

            self.addAssignedPkRow4D(index, dstFunc, has_assignments, has_multiple_assignments,
                                    asis1, asis2, asis3, asis4,
                                    f'{ass} -> ',
                                    None if has_assignments and not has_multiple_assignments else ass)

        finally:
            self.numberSelection.clear()
            self.originalNumberSelection.clear()

    # Enter a parse tree produced by NmrPipePKParser#pipp_label.
    def enterPipp_label(self, ctx: NmrPipePKParser.Pipp_labelContext):
        if ctx.Dim_count_DA():
            self.num_of_dim = int(str(ctx.Integer_DA()))

    # Exit a parse tree produced by NmrPipePKParser#pipp_label.
    def exitPipp_label(self, ctx: NmrPipePKParser.Pipp_labelContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by NmrPipePKParser#pipp_axis.
    def enterPipp_axis(self, ctx: NmrPipePKParser.Pipp_axisContext):

        def set_spectral_dim(_dim_id):
            if _dim_id not in self.cur_spectral_dim:
                cur_spectral_dim = copy.copy(SPECTRAL_DIM_TEMPLATE)
            else:
                cur_spectral_dim = self.cur_spectral_dim[_dim_id]

            sw = str(ctx.Float_DA(0))
            sf = str(ctx.Float_DA(1))
            first_value_point = str(ctx.Float_DA(2))

            max_eff_digits = getMaxEffDigits([sf, first_value_point])

            sw = float(sw)
            sf = float(sf)
            first_ppm = float(roundString(str(float(first_value_point) / sf), max_eff_digits))
            last_ppm = float(roundString(str(first_ppm - sw / sf), max_eff_digits))
            center_ppm = (first_ppm + last_ppm) / 2.0

            cur_spectral_dim['spectrometer_frequency'] = sf
            cur_spectral_dim['sweep_width'] = sw
            cur_spectral_dim['sweep_width_units'] = 'Hz'
            cur_spectral_dim['value_first_point'] = first_ppm
            cur_spectral_dim['center_frequency_offset'] = float(roundString(str(center_ppm), max_eff_digits))

            self.cur_spectral_dim[_dim_id] = cur_spectral_dim

        if ctx.X_axis_DA():
            set_spectral_dim(1)
        elif ctx.Y_axis_DA():
            set_spectral_dim(2)
        elif ctx.Z_axis_DA():
            set_spectral_dim(3)
        elif ctx.A_axis_DA():
            set_spectral_dim(4)

    # Exit a parse tree produced by NmrPipePKParser#pipp_axis.
    def exitPipp_axis(self, ctx: NmrPipePKParser.Pipp_axisContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by NmrPipePKParser#pipp_peak_list_2d.
    def enterPipp_peak_list_2d(self, ctx: NmrPipePKParser.Pipp_peak_list_2dContext):  # pylint: disable=unused-argument
        if self.num_of_dim != 2:
            self.num_of_dim = 2
        self.initSpectralDim()
        self.software_name = 'PIPP'

    # Exit a parse tree produced by NmrPipePKParser#pipp_peak_list_2d.
    def exitPipp_peak_list_2d(self, ctx: NmrPipePKParser.Pipp_peak_list_2dContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by NmrPipePKParser#pipp_peak_2d.
    def enterPipp_peak_2d(self, ctx: NmrPipePKParser.Pipp_peak_2dContext):  # pylint: disable=unused-argument
        self.peaks2D += 1

        self.atomSelectionSets.clear()
        self.asIsSets.clear()

    # Exit a parse tree produced by NmrPipePKParser#pipp_peak_2d.
    def exitPipp_peak_2d(self, ctx: NmrPipePKParser.Pipp_peak_2dContext):

        try:

            if len(self.numberSelection) == 0:
                self.peaks2D -= 1
                return

            try:

                index = int(str(ctx.Integer()))
                x_ppm = self.numberSelection[0]
                y_ppm = self.numberSelection[1]
                height = self.originalNumberSelection[2]

            except IndexError:
                self.peaks2D -= 1
                return

            if len(self.originalNumberSelection) > 3:
                ass1 = self.originalNumberSelection[3]
                if ass1 in emptyValue:
                    ass1 = None
            else:
                ass1 = None

            if len(self.originalNumberSelection) > 4:
                ass2 = self.originalNumberSelection[4]
                if ass2 in emptyValue:
                    ass2 = None
            else:
                ass2 = None

            if not self.hasPolySeq and not self.hasNonPolySeq:
                return

            if None in (x_ppm, y_ppm):
                self.peaks2D -= 1
                return

            dstFunc = self.validatePeak2D(index, x_ppm, y_ppm, None, None, None, None,
                                          None, None, None, None, height, None, None, None)

            if dstFunc is None:
                self.peaks2D -= 1
                return

            if self.num_of_dim != 2:
                self.num_of_dim = 2
                self.initSpectralDim()

            cur_spectral_dim = self.spectral_dim[self.num_of_dim][self.cur_list_id]

            cur_spectral_dim[1]['freq_hint'].append(x_ppm)
            cur_spectral_dim[2]['freq_hint'].append(y_ppm)

            has_assignments = has_multiple_assignments = False
            asis1 = asis2 = None

            ass = None
            if ass1 is not None and ass2 is not None:
                ass = f'{ass1}, {ass2}'
            elif ass1 is not None:
                ass = ass1
            elif ass2 is not None:
                ass = ass2

            if ass is not None:
                assignments = []
                if len(ass.split('-')) == self.num_of_dim:
                    hint = None
                    for _ass in ass.split('-'):
                        assignments.append(self.extractPeakAssignment(1, _ass, index, hint=hint))
                        hint = assignments[-1] if assignments[-1] is not None else None
                elif len(ass.split(':')) == self.num_of_dim:
                    hint = None
                    for _ass in ass.split(':'):
                        assignments.append(self.extractPeakAssignment(1, _ass, index, hint=hint))
                        hint = assignments[-1] if assignments[-1] is not None else None
                elif len(ass.split(';')) == self.num_of_dim:
                    hint = None
                    for _ass in ass.split(';'):
                        assignments.append(self.extractPeakAssignment(1, _ass, index, hint=hint))
                        hint = assignments[-1] if assignments[-1] is not None else None
                elif len(ass.split(',')) == self.num_of_dim:
                    hint = None
                    for _ass in ass.split(','):
                        assignments.append(self.extractPeakAssignment(1, _ass, index, hint=hint))
                        hint = assignments[-1] if assignments[-1] is not None else None
                else:
                    assignments = [None] * self.num_of_dim
                    _assignments = self.extractPeakAssignment(self.num_of_dim, ass, index)
                    if _assignments is not None and len(_assignments) == self.num_of_dim:
                        for idx in range(self.num_of_dim):
                            assignments[idx] = [_assignments[idx]]  # pylint: disable=unsubscriptable-object

                has_assignments, has_multiple_assignments, asis1, asis2 =\
                    self.checkAssignments2D(index, assignments, dstFunc)

            self.addAssignedPkRow2D(index, dstFunc, has_assignments, has_multiple_assignments,
                                    asis1, asis2,
                                    f'{ass} -> ',
                                    None if has_assignments and not has_multiple_assignments else ass)

        finally:
            self.numberSelection.clear()
            self.originalNumberSelection.clear()

    # Enter a parse tree produced by NmrPipePKParser#pipp_peak_list_3d.
    def enterPipp_peak_list_3d(self, ctx: NmrPipePKParser.Pipp_peak_list_3dContext):  # pylint: disable=unused-argument
        if self.num_of_dim != 3:
            self.num_of_dim = 3
        self.initSpectralDim()
        self.software_name = 'PIPP'

    # Exit a parse tree produced by NmrPipePKParser#pipp_peak_list_3d.
    def exitPipp_peak_list_3d(self, ctx: NmrPipePKParser.Pipp_peak_list_3dContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by NmrPipePKParser#pipp_peak_3d.
    def enterPipp_peak_3d(self, ctx: NmrPipePKParser.Pipp_peak_3dContext):  # pylint: disable=unused-argument
        self.peaks3D += 1

        self.atomSelectionSets.clear()
        self.asIsSets.clear()

    # Exit a parse tree produced by NmrPipePKParser#pipp_peak_3d.
    def exitPipp_peak_3d(self, ctx: NmrPipePKParser.Pipp_peak_3dContext):

        try:

            if len(self.numberSelection) == 0:
                self.peaks3D -= 1
                return

            try:

                index = int(str(ctx.Integer(0)))
                x_ppm = self.numberSelection[0]
                y_ppm = self.numberSelection[1]
                z_ppm = self.numberSelection[2]
                height = self.originalNumberSelection[3]

            except IndexError:
                self.peaks3D -= 1
                return

            if len(self.originalNumberSelection) > 4:
                ass1 = self.originalNumberSelection[4]
                if ass1 in emptyValue:
                    ass1 = None
            else:
                ass1 = None

            if len(self.originalNumberSelection) > 5:
                ass2 = self.originalNumberSelection[5]
                if ass2 in emptyValue:
                    ass2 = None
            else:
                ass2 = None

            if not self.hasPolySeq and not self.hasNonPolySeq:
                return

            if None in (x_ppm, y_ppm, z_ppm):
                self.peaks3D -= 1
                return

            dstFunc = self.validatePeak3D(index, x_ppm, y_ppm, z_ppm, None, None, None, None, None, None,
                                          None, None, None, None, None, None, height, None, None, None)

            if dstFunc is None:
                self.peaks3D -= 1
                return

            if self.num_of_dim != 3:
                self.num_of_dim = 3
                self.initSpectralDim()

            cur_spectral_dim = self.spectral_dim[self.num_of_dim][self.cur_list_id]

            cur_spectral_dim[1]['freq_hint'].append(x_ppm)
            cur_spectral_dim[2]['freq_hint'].append(y_ppm)
            cur_spectral_dim[3]['freq_hint'].append(z_ppm)

            has_assignments = has_multiple_assignments = False
            asis1 = asis2 = asis3 = None

            ass = None
            if ass1 is not None and ass2 is not None:
                ass = f'{ass1}, {ass2}'
            elif ass1 is not None:
                ass = ass1
            elif ass2 is not None:
                ass = ass2

            if ass is not None and self.reasons is not None and 'onebond_resolved' in self.reasons:

                if self.extractPeakAssignment(2, ass1, index) is not None:
                    onebondOrder = 0
                else:
                    onebondOrder = 1

                assignments = []
                if len(ass.split('-')) == self.num_of_dim:
                    hint = None
                    for _ass in ass.split('-'):
                        assignments.append(self.extractPeakAssignment(1, _ass, index, hint=hint))
                        hint = assignments[-1] if assignments[-1] is not None else None
                elif len(ass.split(':')) == self.num_of_dim:
                    hint = None
                    for _ass in ass.split(':'):
                        assignments.append(self.extractPeakAssignment(1, _ass, index, hint=hint))
                        hint = assignments[-1] if assignments[-1] is not None else None
                elif len(ass.split(';')) == self.num_of_dim:
                    hint = None
                    for _ass in ass.split(';'):
                        assignments.append(self.extractPeakAssignment(1, _ass, index, hint=hint))
                        hint = assignments[-1] if assignments[-1] is not None else None
                elif len(ass.split(',')) == self.num_of_dim:
                    hint = None
                    for _ass in ass.split(','):
                        assignments.append(self.extractPeakAssignment(1, _ass, index, hint=hint))
                        hint = assignments[-1] if assignments[-1] is not None else None
                else:
                    assignments = [None] * self.num_of_dim
                    _assignments = self.extractPeakAssignment(self.num_of_dim, ass, index)
                    if _assignments is not None and len(_assignments) == self.num_of_dim:
                        for idx in range(self.num_of_dim):
                            assignments[idx] = [_assignments[idx]]  # pylint: disable=unsubscriptable-object

                has_assignments, has_multiple_assignments, asis1, asis2, asis3 =\
                    self.checkAssignments3D(index, assignments, dstFunc, onebondOrder)

            self.addAssignedPkRow3D(index, dstFunc, has_assignments, has_multiple_assignments,
                                    asis1, asis2, asis3,
                                    f'{ass} -> ',
                                    None if has_assignments and not has_multiple_assignments else ass)

        finally:
            self.numberSelection.clear()
            self.originalNumberSelection.clear()

    # Enter a parse tree produced by NmrPipePKParser#pipp_peak_list_4d.
    def enterPipp_peak_list_4d(self, ctx: NmrPipePKParser.Pipp_peak_list_4dContext):  # pylint: disable=unused-argument
        if self.num_of_dim != 4:
            self.num_of_dim = 4
        self.initSpectralDim()
        self.software_name = 'PIPP'

    # Exit a parse tree produced by NmrPipePKParser#pipp_peak_list_4d.
    def exitPipp_peak_list_4d(self, ctx: NmrPipePKParser.Pipp_peak_list_4dContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by NmrPipePKParser#pipp_peak_4d.
    def enterPipp_peak_4d(self, ctx: NmrPipePKParser.Pipp_peak_4dContext):  # pylint: disable=unused-argument
        self.peaks4D += 1

        self.atomSelectionSets.clear()
        self.asIsSets.clear()

    # Exit a parse tree produced by NmrPipePKParser#pipp_peak_4d.
    def exitPipp_peak_4d(self, ctx: NmrPipePKParser.Pipp_peak_4dContext):

        try:

            if len(self.numberSelection) == 0:
                self.peaks4D -= 1
                return

            try:

                index = int(str(ctx.Integer(0)))
                x_ppm = self.numberSelection[0]
                y_ppm = self.numberSelection[1]
                z_ppm = self.numberSelection[2]
                a_ppm = self.numberSelection[3]
                height = self.originalNumberSelection[4]

            except IndexError:
                self.peaks4D -= 1
                return

            if len(self.originalNumberSelection) > 5:
                ass1 = self.originalNumberSelection[5]
                if ass1 in emptyValue:
                    ass1 = None
            else:
                ass1 = None

            if len(self.originalNumberSelection) > 6:
                ass2 = self.originalNumberSelection[6]
                if ass2 in emptyValue:
                    ass2 = None
            else:
                ass2 = None

            if not self.hasPolySeq and not self.hasNonPolySeq:
                return

            if None in (x_ppm, y_ppm, z_ppm, a_ppm):
                self.peaks4D -= 1
                return

            dstFunc = self.validatePeak4D(index, x_ppm, y_ppm, z_ppm, a_ppm, None, None, None, None, None, None, None, None,
                                          None, None, None, None, None, None, None, None, height, None, None, None)

            if dstFunc is None:
                self.peaks4D -= 1
                return

            if self.num_of_dim != 4:
                self.num_of_dim = 4
                self.initSpectralDim()

            cur_spectral_dim = self.spectral_dim[self.num_of_dim][self.cur_list_id]

            cur_spectral_dim[1]['freq_hint'].append(x_ppm)
            cur_spectral_dim[2]['freq_hint'].append(y_ppm)
            cur_spectral_dim[3]['freq_hint'].append(z_ppm)
            cur_spectral_dim[4]['freq_hint'].append(a_ppm)

            has_assignments = has_multiple_assignments = False
            asis1 = asis2 = asis3 = asis4 = None

            ass = None
            if ass1 is not None and ass2 is not None:
                ass = f'{ass1}, {ass2}'
            elif ass1 is not None:
                ass = ass1
            elif ass2 is not None:
                ass = ass2

            if ass is not None and self.reasons is not None and 'onebond_resolved' in self.reasons:
                assignments = []
                if len(ass.split('-')) == self.num_of_dim:
                    hint = None
                    for _ass in ass.split('-'):
                        assignments.append(self.extractPeakAssignment(1, _ass, index, hint=hint))
                        hint = assignments[-1] if assignments[-1] is not None else None
                elif len(ass.split(':')) == self.num_of_dim:
                    hint = None
                    for _ass in ass.split(':'):
                        assignments.append(self.extractPeakAssignment(1, _ass, index, hint=hint))
                        hint = assignments[-1] if assignments[-1] is not None else None
                elif len(ass.split(';')) == self.num_of_dim:
                    hint = None
                    for _ass in ass.split(';'):
                        assignments.append(self.extractPeakAssignment(1, _ass, index, hint=hint))
                        hint = assignments[-1] if assignments[-1] is not None else None
                elif len(ass.split(',')) == self.num_of_dim:
                    hint = None
                    for _ass in ass.split(','):
                        assignments.append(self.extractPeakAssignment(1, _ass, index, hint=hint))
                        hint = assignments[-1] if assignments[-1] is not None else None
                else:
                    assignments = [None] * self.num_of_dim
                    _assignments = self.extractPeakAssignment(self.num_of_dim, ass, index)
                    if _assignments is not None and len(_assignments) == self.num_of_dim:
                        for idx in range(self.num_of_dim):
                            assignments[idx] = [_assignments[idx]]  # pylint: disable=unsubscriptable-object

                has_assignments, has_multiple_assignments, asis1, asis2, asis3, asis4 =\
                    self.checkAssignments4D(index, assignments, dstFunc)

            self.addAssignedPkRow4D(index, dstFunc, has_assignments, has_multiple_assignments,
                                    asis1, asis2, asis3, asis4,
                                    f'{ass} -> ',
                                    None if has_assignments and not has_multiple_assignments else ass)

        finally:
            self.numberSelection.clear()
            self.originalNumberSelection.clear()

    def enterNumber(self, ctx: NmrPipePKParser.NumberContext):  # pylint: disable=unused-argument

        try:

            if ctx.Integer():
                value = str(ctx.Integer())
                if self.null_value is not None and value == self.null_value:
                    self.numberSelection.append(None)
                    self.originalNumberSelection.append(None)
                else:
                    self.numberSelection.append(int(value))
                    self.originalNumberSelection.append(value)

            elif ctx.Float():
                value = str(ctx.Float())
                if self.null_value is not None and value == self.null_value:
                    self.numberSelection.append(None)
                    self.originalNumberSelection.append(None)
                else:
                    self.numberSelection.append(float(value))
                    self.originalNumberSelection.append(value)

            elif ctx.Real():
                value = str(ctx.Real())
                if self.null_value is not None and value == self.null_value:
                    self.numberSelection.append(None)
                    self.originalNumberSelection.append(None)
                else:
                    self.numberSelection.append(float(value))
                    self.originalNumberSelection.append(value)

            else:
                self.numberSelection.append(None)
                self.originalNumberSelection.append(str(ctx.Any_name()))

        except ValueError:
            self.numberSelection.append(None)
            self.originalNumberSelection.append(None)

    # Exit a parse tree produced by NmrPipePKParser#number.
    def exitNumber(self, ctx: NmrPipePKParser.NumberContext):  # pylint: disable=unused-argument
        pass


# del NmrPipePKParser
