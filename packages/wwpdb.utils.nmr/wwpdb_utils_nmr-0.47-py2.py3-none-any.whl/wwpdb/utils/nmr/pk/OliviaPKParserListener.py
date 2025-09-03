##
# File: OliviaPKParserListener.py
# Date: 22-Aug-2025
#
# Updates:
""" ParserLister class for OLIVIA PK files.
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
    from wwpdb.utils.nmr.pk.OliviaPKParser import OliviaPKParser
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
    from nmr.pk.OliviaPKParser import OliviaPKParser
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


# This class defines a complete listener for a parse tree produced by OliviaPKParser.
class OliviaPKParserListener(ParseTreeListener, BasePKParserListener):

    __spectrum_names = None

    __transposed = False
    __hz_unit = False

    __strings = None
    __integers = None
    __memo = None

    def __init__(self, verbose: bool = True, log: IO = sys.stdout,
                 representativeModelId: int = REPRESENTATIVE_MODEL_ID,
                 representativeAltId: str = REPRESENTATIVE_ALT_ID,
                 mrAtomNameMapping: Optional[List[dict]] = None,
                 cR: Optional[CifReader] = None, caC: Optional[dict] = None, ccU: Optional[ChemCompUtil] = None,
                 csStat: Optional[BMRBChemShiftStat] = None, nefT: Optional[NEFTranslator] = None,
                 reasons: Optional[dict] = None):
        super().__init__(verbose, log, representativeModelId, representativeAltId,
                         mrAtomNameMapping, cR, caC, ccU, csStat, nefT, reasons)

        self.file_type = 'nm-pea-oli'
        self.software_name = 'Olivia'

    # Enter a parse tree produced by OliviaPKParser#nmrpipe_pk.
    def enterOlivia_pk(self, ctx: OliviaPKParser.Olivia_pkContext):  # pylint: disable=unused-argument
        self.__spectrum_names = {}

        self.enter()

    # Exit a parse tree produced by OliviaPKParser#dynamo_mr.
    def exitOlivia_pk(self, ctx: OliviaPKParser.Olivia_pkContext):  # pylint: disable=unused-argument
        self.exit(self.__spectrum_names if len(self.__spectrum_names) > 0 else None)

    # Enter a parse tree produced by OliviaPKParser#comment.
    def enterComment(self, ctx: OliviaPKParser.CommentContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by OliviaPKParser#comment.
    def exitComment(self, ctx: OliviaPKParser.CommentContext):
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
        last_comment = None if len(comment) == 0 else ' '.join(comment)

        if last_comment is None or ':' not in last_comment:  # pylint: disable=unsupported-membership-test
            return

        remark = last_comment.split(':')

        key = remark[0].strip()
        value = remark[1].strip()

        if key == 'Dimension':
            if value == '2':
                self.num_of_dim = 2
            elif value == '3':
                self.num_of_dim = 3
            elif value == '4':
                self.num_of_dim = 4

        elif key == 'Experiment':
            self.spectrum_name = value

        elif key == 'Axis Label':
            labels = [_label[:_label.index('(')] for _label in value.split(',')]

            for _dim_id, _axis_code in enumerate(labels, start=1):
                if _dim_id not in self.cur_spectral_dim:
                    cur_spectral_dim = copy.copy(SPECTRAL_DIM_TEMPLATE)
                else:
                    cur_spectral_dim = self.cur_spectral_dim[_dim_id]

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

                self.cur_spectral_dim[_dim_id] = cur_spectral_dim

        elif key == 'Obs. Freq.':
            value = value[:value.index('[')].strip()
            obs_freq = [float(_obs_freq[:_obs_freq.index('(')]) for _obs_freq in value.split(',')]

            for _dim_id, _obs_freq in enumerate(obs_freq, start=1):
                if _dim_id not in self.cur_spectral_dim:
                    cur_spectral_dim = copy.copy(SPECTRAL_DIM_TEMPLATE)
                else:
                    cur_spectral_dim = self.cur_spectral_dim[_dim_id]

                cur_spectral_dim['spectrometer_frequency'] = _obs_freq

                self.cur_spectral_dim[_dim_id] = cur_spectral_dim

        elif key == 'Spec.Center':
            value = value[:value.index('[')].strip()
            spec_center = [float(_obs_freq[:_obs_freq.index('(')]) for _obs_freq in value.split(',')]

            for _dim_id, _spec_center in enumerate(spec_center, start=1):
                if _dim_id not in self.cur_spectral_dim:
                    cur_spectral_dim = copy.copy(SPECTRAL_DIM_TEMPLATE)
                else:
                    cur_spectral_dim = self.cur_spectral_dim[_dim_id]

                cur_spectral_dim['center_frequency_offset'] = _spec_center

                self.cur_spectral_dim[_dim_id] = cur_spectral_dim

        elif key == 'Orig.Freq.':
            value = value[:value.index('[')].strip()
            orig_freq = [float(_obs_freq[:_obs_freq.index('(')]) for _obs_freq in value.split(',')]

            for _dim_id, _orig_freq in enumerate(orig_freq, start=1):
                if _dim_id not in self.cur_spectral_dim:
                    cur_spectral_dim = copy.copy(SPECTRAL_DIM_TEMPLATE)
                else:
                    cur_spectral_dim = self.cur_spectral_dim[_dim_id]

                max_eff_digits = getMaxEffDigits([str(f) for f in orig_freq])

                if 'specrometer_frequency' in cur_spectral_dim:
                    cur_spectral_dim['center_frequency_offset'] = float(roundString(str(orig_freq / cur_spectral_dim['spectrometer_frequency']),
                                                                                    max_eff_digits))

                self.cur_spectral_dim[_dim_id] = cur_spectral_dim

        elif key == 'Spec.Width':
            value = value[:value.index('[')].strip()
            spec_width = [float(_obs_freq[:_obs_freq.index('(')]) for _obs_freq in value.split(',')]

            for _dim_id, _spec_width in enumerate(spec_width, start=1):
                if _dim_id not in self.cur_spectral_dim:
                    cur_spectral_dim = copy.copy(SPECTRAL_DIM_TEMPLATE)
                else:
                    cur_spectral_dim = self.cur_spectral_dim[_dim_id]

                cur_spectral_dim['sweep_width'] = _spec_width

                self.cur_spectral_dim[_dim_id] = cur_spectral_dim

        elif key == 'Orig.Width':
            value = value[:value.index('[')].strip()
            spec_width = [float(_obs_freq[:_obs_freq.index('(')]) for _obs_freq in value.split(',')]

            for _dim_id, _spec_width in enumerate(spec_width, start=1):
                if _dim_id not in self.cur_spectral_dim:
                    cur_spectral_dim = copy.copy(SPECTRAL_DIM_TEMPLATE)
                else:
                    cur_spectral_dim = self.cur_spectral_dim[_dim_id]

                cur_spectral_dim['sweep_width'] = _spec_width

                self.cur_spectral_dim[_dim_id] = cur_spectral_dim

    def enterIdx_peak_list_2d(self, ctx: OliviaPKParser.Idx_peak_list_2dContext):  # pylint: disable=unused-argument
        if self.num_of_dim != 2:
            self.num_of_dim = 2
        self.initSpectralDim()
        if self.num_of_dim not in self.__spectrum_names:
            self.__spectrum_names[self.num_of_dim] = {}
        if self.cur_list_id not in self.__spectrum_names[self.num_of_dim]:
            self.__spectrum_names[self.num_of_dim][self.cur_list_id] = self.spectrum_name

        self.__strings = []
        self.__integers = []

    # Exit a parse tree produced by OliviaPKParser#idx_peak_list_2d.
    def exitIdx_peak_list_2d(self, ctx: OliviaPKParser.Idx_peak_list_2dContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by OliviaPKParser#idx_peak_2d.
    def enterIdx_peak_2d(self, ctx: OliviaPKParser.Idx_peak_2dContext):  # pylint: disable=unused-argument
        self.peaks2D += 1

        self.atomSelectionSets.clear()
        self.asIsSets.clear()
        self.spectrum_name = None

    # Exit a parse tree produced by OliviaPKParser#idx_peak_2d.
    def exitIdx_peak_2d(self, ctx: OliviaPKParser.Idx_peak_2dContext):
        self.__exit_peak_2d(int(str(ctx.Integer(0))))

    def __exit_peak_2d(self, index):

        try:

            if len(self.numberSelection) == 0:
                self.peaks2D -= 1
                return

            try:

                cur_spectral_dim = self.spectral_dim[self.num_of_dim][self.cur_list_id]

                if self.__hz_unit:
                    if self.__transposed:
                        x_hz = self.numberSelection[1]
                        y_hz = self.numberSelection[0]
                    else:
                        x_hz = self.numberSelection[0]
                        y_hz = self.numberSelection[1]
                    x_ppm = y_ppm = None
                    max_eff_digits = getMaxEffDigits([str(x_hz), str(y_hz)])
                    if 'spectrometer_frequency' in cur_spectral_dim[1]:
                        x_ppm = float(roundString(str(x_hz / cur_spectral_dim[1]['spectrometer_frequency']),
                                                  max_eff_digits))
                    if 'spectrometer_frequency' in cur_spectral_dim[2]:
                        y_ppm = float(roundString(str(y_hz / cur_spectral_dim[2]['spectrometer_frequency']),
                                                  max_eff_digits))
                else:
                    if self.__transposed:
                        x_ppm = self.numberSelection[1]
                        y_ppm = self.numberSelection[0]
                    else:
                        x_ppm = self.numberSelection[0]
                        y_ppm = self.numberSelection[1]
                    x_hz = y_hz = None
                height = self.originalNumberSelection[2]
                vol = self.originalNumberSelection[3]
                vol_err = self.originalNumberSelection[4]

                assignments = [None] * self.num_of_dim

                for idx in range(self.num_of_dim):
                    chain_id = self.__strings[3 * idx]
                    comp_id = self.__strings[3 * idx + 1]
                    atom_id = self.__strings[3 * idx + 2]
                    seq_id = self.__integers[idx]
                    if chain_id is None or comp_id is None or atom_id is None or seq_id is None:
                        continue
                    assignments[idx] = [{'chain_id': chain_id, 'seq_id': seq_id, 'comp_id': comp_id, 'atom_id': atom_id}]

                if not all(a is not None and len(a) >= 1 and 'seq_id' in a[0] and 'atom_id' in a[0] for a in assignments):  # pylint: disable=unsubscriptable-object
                    assignments = [None] * self.num_of_dim

            except IndexError:
                self.peaks2D -= 1
                return

            if not self.hasPolySeq and not self.hasNonPolySeq:
                return

            if None in (x_ppm, y_ppm):
                self.peaks2D -= 1
                return

            dstFunc = self.validatePeak2D(index, x_ppm, y_ppm, None, None, None, None,
                                          x_hz, y_hz, None, None, height, None, vol, vol_err)

            if dstFunc is None:
                self.peaks2D -= 1
                return

            cur_spectral_dim[1]['freq_hint'].append(x_ppm)
            cur_spectral_dim[2]['freq_hint'].append(y_ppm)

            has_assignments, has_multiple_assignments, asis1, asis2 =\
                self.checkAssignments2D(index, assignments, dstFunc)

            self.addAssignedPkRow2D(index, dstFunc, has_assignments, has_multiple_assignments,
                                    asis1, asis2,
                                    '', self.__memo)

        finally:
            self.numberSelection.clear()
            self.originalNumberSelection.clear()
            self.__strings.clear()
            self.__integers.clear()

    # Enter a parse tree produced by OliviaPKParser#idx_peak_list_3d.
    def enterIdx_peak_list_3d(self, ctx: OliviaPKParser.Idx_peak_list_3dContext):  # pylint: disable=unused-argument
        if self.num_of_dim != 3:
            self.num_of_dim = 3
        self.initSpectralDim()
        if self.num_of_dim not in self.__spectrum_names:
            self.__spectrum_names[self.num_of_dim] = {}
        if self.cur_list_id not in self.__spectrum_names[self.num_of_dim]:
            self.__spectrum_names[self.num_of_dim][self.cur_list_id] = self.spectrum_name

        self.__strings = []
        self.__integers = []

    # Exit a parse tree produced by OliviaPKParser#idx_peak_list_3d.
    def exitIdx_peak_list_3d(self, ctx: OliviaPKParser.Idx_peak_list_3dContext):  # pylint: disable=unused-argument
        if self.exptlMethod != 'SOLID-STATE NMR':
            for _dim_id in range(2, self.num_of_dim + 1):
                cur_spectral_dim = self.cur_spectral_dim[_dim_id]
                if cur_spectral_dim['atom_isotope_number'] != 13:
                    continue
                if cur_spectral_dim['center_frequency_offset'] > 100.0:
                    continue
                if cur_spectral_dim['sweep_width'] < 50.0:
                    cur_spectral_dim['under_sampling_type'] = 'folded'

    # Enter a parse tree produced by OliviaPKParser#idx_peak_3d.
    def enterIdx_peak_3d(self, ctx: OliviaPKParser.Idx_peak_3dContext):  # pylint: disable=unused-argument
        self.peaks3D += 1

        self.atomSelectionSets.clear()
        self.asIsSets.clear()
        self.spectrum_name = None

    # Exit a parse tree produced by OliviaPKParser#idx_peak_3d.
    def exitIdx_peak_3d(self, ctx: OliviaPKParser.Idx_peak_3dContext):
        self.__exit_peak_3d(int(str(ctx.Integer(0))))

    def __exit_peak_3d(self, index):

        try:

            if len(self.numberSelection) == 0:
                self.peaks3D -= 1
                return

            try:

                cur_spectral_dim = self.spectral_dim[self.num_of_dim][self.cur_list_id]

                if self.__hz_unit:
                    if self.__transposed:
                        x_hz = self.numberSelection[2]
                        y_hz = self.numberSelection[1]
                        z_hz = self.numberSelection[0]
                    else:
                        x_hz = self.numberSelection[0]
                        y_hz = self.numberSelection[1]
                        z_hz = self.numberSelection[2]
                    x_ppm = y_ppm = z_ppm = None
                    max_eff_digits = getMaxEffDigits([str(x_hz), str(y_hz), str(z_hz)])
                    if 'spectrometer_frequency' in cur_spectral_dim[1]:
                        x_ppm = float(roundString(str(x_hz / cur_spectral_dim[1]['spectrometer_frequency']),
                                                  max_eff_digits))
                    if 'spectrometer_frequency' in cur_spectral_dim[2]:
                        y_ppm = float(roundString(str(y_hz / cur_spectral_dim[2]['spectrometer_frequency']),
                                                  max_eff_digits))
                    if 'spectrometer_frequency' in cur_spectral_dim[3]:
                        z_ppm = float(roundString(str(z_hz / cur_spectral_dim[3]['spectrometer_frequency']),
                                                  max_eff_digits))
                else:
                    if self.__transposed:
                        x_ppm = self.numberSelection[2]
                        y_ppm = self.numberSelection[1]
                        z_ppm = self.numberSelection[0]
                    else:
                        x_ppm = self.numberSelection[0]
                        y_ppm = self.numberSelection[1]
                        z_ppm = self.numberSelection[2]
                    x_hz = y_hz = z_hz = None
                height = self.originalNumberSelection[3]
                vol = self.originalNumberSelection[4]
                vol_err = self.originalNumberSelection[5]

                assignments = [None] * self.num_of_dim

                for idx in range(self.num_of_dim):
                    chain_id = self.__strings[3 * idx]
                    comp_id = self.__strings[3 * idx + 1]
                    atom_id = self.__strings[3 * idx + 2]
                    seq_id = self.__integers[idx]
                    if chain_id is None or comp_id is None or atom_id is None or seq_id is None:
                        continue
                    assignments[idx] = [{'chain_id': chain_id, 'seq_id': seq_id, 'comp_id': comp_id, 'atom_id': atom_id}]

                if not all(a is not None and len(a) >= 1 and 'seq_id' in a[0] and 'atom_id' in a[0] for a in assignments):  # pylint: disable=unsubscriptable-object
                    assignments = [None] * self.num_of_dim

            except IndexError:
                self.peaks3D -= 1
                return

            if not self.hasPolySeq and not self.hasNonPolySeq:
                return

            if None in (x_ppm, y_ppm, z_ppm):
                self.peaks3D -= 1
                return

            dstFunc = self.validatePeak3D(index, x_ppm, y_ppm, z_ppm, None, None, None, None, None, None,
                                          x_hz, y_hz, z_hz, None, None, None, height, None, vol, vol_err)

            if dstFunc is None:
                self.peaks3D -= 1
                return

            cur_spectral_dim[1]['freq_hint'].append(x_ppm)
            cur_spectral_dim[2]['freq_hint'].append(y_ppm)
            cur_spectral_dim[3]['freq_hint'].append(z_ppm)

            has_assignments, has_multiple_assignments, asis1, asis2, asis3 =\
                self.checkAssignments3D(index, assignments, dstFunc)

            self.addAssignedPkRow3D(index, dstFunc, has_assignments, has_multiple_assignments,
                                    asis1, asis2, asis3,
                                    '', self.__memo)

        finally:
            self.numberSelection.clear()
            self.originalNumberSelection.clear()
            self.__strings.clear()
            self.__integers.clear()

    # Enter a parse tree produced by OliviaPKParser#idx_peak_list_4d.
    def enterIdx_peak_list_4d(self, ctx: OliviaPKParser.Idx_peak_list_4dContext):  # pylint: disable=unused-argument
        if self.num_of_dim != 4:
            self.num_of_dim = 4
        self.initSpectralDim()
        if self.num_of_dim not in self.__spectrum_names:
            self.__spectrum_names[self.num_of_dim] = {}
        if self.cur_list_id not in self.__spectrum_names[self.num_of_dim]:
            self.__spectrum_names[self.num_of_dim][self.cur_list_id] = self.spectrum_name

        self.__strings = []
        self.__integers = []

    # Exit a parse tree produced by OliviaPKParser#idx_peak_list_4d.
    def exitIdx_peak_list_4d(self, ctx: OliviaPKParser.Idx_peak_list_4dContext):  # pylint: disable=unused-argument
        if self.exptlMethod != 'SOLID-STATE NMR':
            for _dim_id in range(2, self.num_of_dim + 1):
                cur_spectral_dim = self.cur_spectral_dim[_dim_id]
                if cur_spectral_dim['atom_isotope_number'] != 13:
                    continue
                if cur_spectral_dim['center_frequency_offset'] > 100.0:
                    continue
                if cur_spectral_dim['sweep_width'] < 50.0:
                    cur_spectral_dim['under_sampling_type'] = 'folded'

    # Enter a parse tree produced by OliviaPKParser#idx_peak_4d.
    def enterIdx_peak_4d(self, ctx: OliviaPKParser.Idx_peak_4dContext):  # pylint: disable=unused-argument
        self.peaks4D += 1

        self.atomSelectionSets.clear()
        self.asIsSets.clear()
        self.spectrum_name = None

    # Exit a parse tree produced by OliviaPKParser#idx_peak_4d.
    def exitIdx_peak_4d(self, ctx: OliviaPKParser.Idx_peak_4dContext):
        self.__exit_peak_4d(int(str(ctx.Integer(0))))

    def __exit_peak_4d(self, index):

        try:

            if len(self.numberSelection) == 0:
                self.peaks4D -= 1
                return

            try:

                cur_spectral_dim = self.spectral_dim[self.num_of_dim][self.cur_list_id]

                if self.__hz_unit:
                    if self.__transposed:
                        x_hz = self.numberSelection[3]
                        y_hz = self.numberSelection[2]
                        z_hz = self.numberSelection[1]
                        a_hz = self.numberSelection[0]
                    else:
                        x_hz = self.numberSelection[0]
                        y_hz = self.numberSelection[1]
                        z_hz = self.numberSelection[2]
                        a_hz = self.numberSelection[3]
                    x_ppm = y_ppm = z_ppm = a_ppm = None
                    max_eff_digits = getMaxEffDigits([str(x_hz), str(y_hz), str(z_hz), str(a_hz)])
                    if 'spectrometer_frequency' in cur_spectral_dim[1]:
                        x_ppm = float(roundString(str(x_hz / cur_spectral_dim[1]['spectrometer_frequency']),
                                                  max_eff_digits))
                    if 'spectrometer_frequency' in cur_spectral_dim[2]:
                        y_ppm = float(roundString(str(y_hz / cur_spectral_dim[2]['spectrometer_frequency']),
                                                  max_eff_digits))
                    if 'spectrometer_frequency' in cur_spectral_dim[3]:
                        z_ppm = float(roundString(str(z_hz / cur_spectral_dim[3]['spectrometer_frequency']),
                                                  max_eff_digits))
                    if 'spectrometer_frequency' in cur_spectral_dim[4]:
                        a_ppm = float(roundString(str(a_hz / cur_spectral_dim[4]['spectrometer_frequency']),
                                                  max_eff_digits))
                else:
                    if self.__transposed:
                        x_ppm = self.numberSelection[3]
                        y_ppm = self.numberSelection[2]
                        z_ppm = self.numberSelection[1]
                        a_ppm = self.numberSelection[0]
                    else:
                        x_ppm = self.numberSelection[0]
                        y_ppm = self.numberSelection[1]
                        z_ppm = self.numberSelection[2]
                        a_ppm = self.numberSelection[3]
                    x_hz = y_hz = z_hz = a_hz = None
                height = self.originalNumberSelection[4]
                vol = self.originalNumberSelection[5]
                vol_err = self.originalNumberSelection[6]

                assignments = [None] * self.num_of_dim

                for idx in range(self.num_of_dim):
                    chain_id = self.__strings[3 * idx]
                    comp_id = self.__strings[3 * idx + 1]
                    atom_id = self.__strings[3 * idx + 2]
                    seq_id = self.__integers[idx]
                    if chain_id is None or comp_id is None or atom_id is None or seq_id is None:
                        continue
                    assignments[idx] = [{'chain_id': chain_id, 'seq_id': seq_id, 'comp_id': comp_id, 'atom_id': atom_id}]

                if not all(a is not None and len(a) >= 1 and 'seq_id' in a[0] and 'atom_id' in a[0] for a in assignments):  # pylint: disable=unsubscriptable-object
                    assignments = [None] * self.num_of_dim

            except IndexError:
                self.peaks4D -= 1
                return

            if not self.hasPolySeq and not self.hasNonPolySeq:
                return

            if None in (x_ppm, y_ppm, z_ppm, a_ppm):
                self.peaks4D -= 1
                return

            dstFunc = self.validatePeak4D(index, x_ppm, y_ppm, z_ppm, a_ppm, None, None, None, None, None, None, None, None,
                                          x_hz, y_hz, z_hz, a_hz, None, None, None, None, height, None, vol, vol_err)

            if dstFunc is None:
                self.peaks4D -= 1
                return

            cur_spectral_dim[1]['freq_hint'].append(x_ppm)
            cur_spectral_dim[2]['freq_hint'].append(y_ppm)
            cur_spectral_dim[3]['freq_hint'].append(z_ppm)
            cur_spectral_dim[4]['freq_hint'].append(a_ppm)

            has_assignments, has_multiple_assignments, asis1, asis2, asis3, asis4 =\
                self.checkAssignments4D(index, assignments, dstFunc)

            self.addAssignedPkRow4D(index, dstFunc, has_assignments, has_multiple_assignments,
                                    asis1, asis2, asis3, asis4,
                                    '', self.__memo)

        finally:
            self.numberSelection.clear()
            self.originalNumberSelection.clear()
            self.__strings.clear()
            self.__integers.clear()

    # Enter a parse tree produced by OliviaPKParser#ass_peak_list_2d.
    def enterAss_peak_list_2d(self, ctx: OliviaPKParser.Ass_peak_list_2dContext):  # pylint: disable=unused-argument
        if self.num_of_dim != 2:
            self.num_of_dim = 2
        self.initSpectralDim()
        if self.num_of_dim not in self.__spectrum_names:
            self.__spectrum_names[self.num_of_dim] = {}
        if self.cur_list_id not in self.__spectrum_names[self.num_of_dim]:
            self.__spectrum_names[self.num_of_dim][self.cur_list_id] = self.spectrum_name

        self.__strings = []
        self.__integers = []

    # Exit a parse tree produced by OliviaPKParser#ass_peak_list_2d.
    def exitAss_peak_list_2d(self, ctx: OliviaPKParser.Ass_peak_list_2dContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by OliviaPKParser#ass_peak_2d.
    def enterAss_peak_2d(self, ctx: OliviaPKParser.Ass_peak_2dContext):  # pylint: disable=unused-argument
        self.peaks2D += 1

        self.atomSelectionSets.clear()
        self.asIsSets.clear()
        self.spectrum_name = None

    # Exit a parse tree produced by OliviaPKParser#ass_peak_2d.
    def exitAss_peak_2d(self, ctx: OliviaPKParser.Ass_peak_2dContext):
        self.__exit_peak_2d(int(str(ctx.Integer(0))))

    # Enter a parse tree produced by OliviaPKParser#ass_peak_list_3d.
    def enterAss_peak_list_3d(self, ctx: OliviaPKParser.Ass_peak_list_3dContext):  # pylint: disable=unused-argument
        if self.num_of_dim != 3:
            self.num_of_dim = 3
        self.initSpectralDim()
        if self.num_of_dim not in self.__spectrum_names:
            self.__spectrum_names[self.num_of_dim] = {}
        if self.cur_list_id not in self.__spectrum_names[self.num_of_dim]:
            self.__spectrum_names[self.num_of_dim][self.cur_list_id] = self.spectrum_name

        self.__strings = []
        self.__integers = []

    # Exit a parse tree produced by OliviaPKParser#ass_peak_list_3d.
    def exitAss_peak_list_3d(self, ctx: OliviaPKParser.Ass_peak_list_3dContext):  # pylint: disable=unused-argument
        if self.exptlMethod != 'SOLID-STATE NMR':
            for _dim_id in range(2, self.num_of_dim + 1):
                cur_spectral_dim = self.cur_spectral_dim[_dim_id]
                if cur_spectral_dim['atom_isotope_number'] != 13:
                    continue
                if cur_spectral_dim['center_frequency_offset'] > 100.0:
                    continue
                if cur_spectral_dim['sweep_width'] < 50.0:
                    cur_spectral_dim['under_sampling_type'] = 'folded'

    # Enter a parse tree produced by OliviaPKParser#ass_peak_3d.
    def enterAss_peak_3d(self, ctx: OliviaPKParser.Ass_peak_3dContext):  # pylint: disable=unused-argument
        self.peaks3D += 1

        self.atomSelectionSets.clear()
        self.asIsSets.clear()
        self.spectrum_name = None

    # Exit a parse tree produced by OliviaPKParser#ass_peak_3d.
    def exitAss_peak_3d(self, ctx: OliviaPKParser.Ass_peak_3dContext):
        self.__exit_peak_3d(int(str(ctx.Integer(0))))

    # Enter a parse tree produced by OliviaPKParser#ass_peak_list_4d.
    def enterAss_peak_list_4d(self, ctx: OliviaPKParser.Ass_peak_list_4dContext):  # pylint: disable=unused-argument
        if self.num_of_dim != 4:
            self.num_of_dim = 4
        self.initSpectralDim()
        if self.num_of_dim not in self.__spectrum_names:
            self.__spectrum_names[self.num_of_dim] = {}
        if self.cur_list_id not in self.__spectrum_names[self.num_of_dim]:
            self.__spectrum_names[self.num_of_dim][self.cur_list_id] = self.spectrum_name

        self.__strings = []
        self.__integers = []

    # Exit a parse tree produced by OliviaPKParser#ass_peak_list_4d.
    def exitAss_peak_list_4d(self, ctx: OliviaPKParser.Ass_peak_list_4dContext):  # pylint: disable=unused-argument
        if self.exptlMethod != 'SOLID-STATE NMR':
            for _dim_id in range(2, self.num_of_dim + 1):
                cur_spectral_dim = self.cur_spectral_dim[_dim_id]
                if cur_spectral_dim['atom_isotope_number'] != 13:
                    continue
                if cur_spectral_dim['center_frequency_offset'] > 100.0:
                    continue
                if cur_spectral_dim['sweep_width'] < 50.0:
                    cur_spectral_dim['under_sampling_type'] = 'folded'

    # Enter a parse tree produced by OliviaPKParser#ass_peak_4d.
    def enterAss_peak_4d(self, ctx: OliviaPKParser.Ass_peak_4dContext):  # pylint: disable=unused-argument
        self.peaks4D += 1

        self.atomSelectionSets.clear()
        self.asIsSets.clear()
        self.spectrum_name = None

    # Exit a parse tree produced by OliviaPKParser#ass_peak_4d.
    def exitAss_peak_4d(self, ctx: OliviaPKParser.Ass_peak_4dContext):
        self.__exit_peak_4d(int(str(ctx.Integer(0))))

    # Enter a parse tree produced by OliviaPKParser#def_2d_axis_order_ppm.
    def enterDef_2d_axis_order_ppm(self, ctx: OliviaPKParser.Def_2d_axis_order_ppmContext):  # pylint: disable=unused-argument
        self.__transposed = False
        self.__hz_unit = False

    # Exit a parse tree produced by OliviaPKParser#def_2d_axis_order_ppm.
    def exitDef_2d_axis_order_ppm(self, ctx: OliviaPKParser.Def_2d_axis_order_ppmContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by OliviaPKParser#tp_2d_axis_order_ppm.
    def enterTp_2d_axis_order_ppm(self, ctx: OliviaPKParser.Tp_2d_axis_order_ppmContext):  # pylint: disable=unused-argument
        self.__transposed = True
        self.__hz_unit = False

    # Exit a parse tree produced by OliviaPKParser#tp_2d_axis_order_ppm.
    def exitTp_2d_axis_order_ppm(self, ctx: OliviaPKParser.Tp_2d_axis_order_ppmContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by OliviaPKParser#def_2d_axis_order_hz.
    def enterDef_2d_axis_order_hz(self, ctx: OliviaPKParser.Def_2d_axis_order_hzContext):  # pylint: disable=unused-argument
        self.__transposed = False
        self.__hz_unit = True

    # Exit a parse tree produced by OliviaPKParser#def_2d_axis_order_hz.
    def exitDef_2d_axis_order_hz(self, ctx: OliviaPKParser.Def_2d_axis_order_hzContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by OliviaPKParser#tp_2d_axis_order_hz.
    def enterTp_2d_axis_order_hz(self, ctx: OliviaPKParser.Tp_2d_axis_order_hzContext):  # pylint: disable=unused-argument
        self.__transposed = True
        self.__hz_unit = True

    # Exit a parse tree produced by OliviaPKParser#tp_2d_axis_order_hz.
    def exitTp_2d_axis_order_hz(self, ctx: OliviaPKParser.Tp_2d_axis_order_hzContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by OliviaPKParser#def_3d_axis_order_ppm.
    def enterDef_3d_axis_order_ppm(self, ctx: OliviaPKParser.Def_3d_axis_order_ppmContext):  # pylint: disable=unused-argument
        self.__transposed = False
        self.__hz_unit = False

    # Exit a parse tree produced by OliviaPKParser#def_3d_axis_order_ppm.
    def exitDef_3d_axis_order_ppm(self, ctx: OliviaPKParser.Def_3d_axis_order_ppmContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by OliviaPKParser#tp_3d_axis_order_ppm.
    def enterTp_3d_axis_order_ppm(self, ctx: OliviaPKParser.Tp_3d_axis_order_ppmContext):  # pylint: disable=unused-argument
        self.__transposed = True
        self.__hz_unit = False

    # Exit a parse tree produced by OliviaPKParser#tp_3d_axis_order_ppm.
    def exitTp_3d_axis_order_ppm(self, ctx: OliviaPKParser.Tp_3d_axis_order_ppmContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by OliviaPKParser#def_3d_axis_order_hz.
    def enterDef_3d_axis_order_hz(self, ctx: OliviaPKParser.Def_3d_axis_order_hzContext):  # pylint: disable=unused-argument
        self.__transposed = False
        self.__hz_unit = True

    # Exit a parse tree produced by OliviaPKParser#def_3d_axis_order_hz.
    def exitDef_3d_axis_order_hz(self, ctx: OliviaPKParser.Def_3d_axis_order_hzContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by OliviaPKParser#tp_3d_axis_order_hz.
    def enterTp_3d_axis_order_hz(self, ctx: OliviaPKParser.Tp_3d_axis_order_hzContext):  # pylint: disable=unused-argument
        self.__transposed = True
        self.__hz_unit = True

    # Exit a parse tree produced by OliviaPKParser#tp_3d_axis_order_hz.
    def exitTp_3d_axis_order_hz(self, ctx: OliviaPKParser.Tp_3d_axis_order_hzContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by OliviaPKParser#def_4d_axis_order_ppm.
    def enterDef_4d_axis_order_ppm(self, ctx: OliviaPKParser.Def_4d_axis_order_ppmContext):  # pylint: disable=unused-argument
        self.__transposed = False
        self.__hz_unit = False

    # Exit a parse tree produced by OliviaPKParser#def_4d_axis_order_ppm.
    def exitDef_4d_axis_order_ppm(self, ctx: OliviaPKParser.Def_4d_axis_order_ppmContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by OliviaPKParser#tp_4d_axis_order_ppm.
    def enterTp_4d_axis_order_ppm(self, ctx: OliviaPKParser.Tp_4d_axis_order_ppmContext):  # pylint: disable=unused-argument
        self.__transposed = True
        self.__hz_unit = False

    # Exit a parse tree produced by OliviaPKParser#tp_4d_axis_order_ppm.
    def exitTp_4d_axis_order_ppm(self, ctx: OliviaPKParser.Tp_4d_axis_order_ppmContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by OliviaPKParser#def_4d_axis_order_hz.
    def enterDef_4d_axis_order_hz(self, ctx: OliviaPKParser.Def_4d_axis_order_hzContext):  # pylint: disable=unused-argument
        self.__transposed = False
        self.__hz_unit = True

    # Exit a parse tree produced by OliviaPKParser#def_4d_axis_order_hz.
    def exitDef_4d_axis_order_hz(self, ctx: OliviaPKParser.Def_4d_axis_order_hzContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by OliviaPKParser#tp_4d_axis_order_hz.
    def enterTp_4d_axis_order_hz(self, ctx: OliviaPKParser.Tp_4d_axis_order_hzContext):  # pylint: disable=unused-argument
        self.__transposed = True
        self.__hz_unit = True

    # Exit a parse tree produced by OliviaPKParser#tp_4d_axis_order_hz.
    def exitTp_4d_axis_order_hz(self, ctx: OliviaPKParser.Tp_4d_axis_order_hzContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by OliviaPKParser#string.
    def enterString(self, ctx: OliviaPKParser.StringContext):
        if ctx.Simple_name():
            self.__strings.append(str(ctx.Simple_name()))
        else:
            self.__strings.append(None)

    # Exit a parse tree produced by OliviaPKParser#string.
    def exitString(self, ctx: OliviaPKParser.StringContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by OliviaPKParser#integer.
    def enterInteger(self, ctx: OliviaPKParser.IntegerContext):
        if ctx.Integer():
            self.__integers.append(int(str(ctx.Integer())))
        else:
            self.__integers.append(None)

    # Exit a parse tree produced by OliviaPKParser#integer.
    def exitInteger(self, ctx: OliviaPKParser.IntegerContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by OliviaPKParser#number.
    def enterNumber(self, ctx: OliviaPKParser.NumberContext):  # pylint: disable=unused-argument

        try:

            if ctx.Integer():
                value = str(ctx.Integer())
                self.numberSelection.append(int(value))
                self.originalNumberSelection.append(value)

            elif ctx.Float():
                value = str(ctx.Float())
                self.numberSelection.append(float(value))
                self.originalNumberSelection.append(value)

            elif ctx.Real():
                value = str(ctx.Real())
                self.numberSelection.append(float(value))
                self.originalNumberSelection.append(value)

            else:
                self.numberSelection.append(None)
                self.originalNumberSelection.append(str(ctx.Any_name()))

        except ValueError:
            self.numberSelection.append(None)
            self.originalNumberSelection.append(None)

    # Exit a parse tree produced by OliviaPKParser#number.
    def exitNumber(self, ctx: OliviaPKParser.NumberContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by OliviaPKParser#memo.
    def enterMemo(self, ctx: OliviaPKParser.MemoContext):
        if ctx.Double_quote_string():
            self.__memo = str(ctx.Double_quote_string()).strip('"')
            if len(self.__memo) == 0:
                self.__memo = None
        elif ctx.Single_quote_string():
            self.__memo = str(ctx.Single_quote_string()).strip("'")
            if len(self.__memo) == 0:
                self.__memo = None
        else:
            self.__memo = str(ctx.Simple_name())
            if self.__memo in emptyValue:
                self.__memo = None

    # Exit a parse tree produced by OliviaPKParser#memo.
    def exitMemo(self, ctx: OliviaPKParser.MemoContext):  # pylint: disable=unused-argument
        pass


# del OliviaPKParser
