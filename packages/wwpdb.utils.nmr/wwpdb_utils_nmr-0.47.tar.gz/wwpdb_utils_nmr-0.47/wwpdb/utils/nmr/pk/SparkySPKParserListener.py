##
# File: SparkySPKParserListener.py
# Date: 28-Mar-2025
#
# Updates:
""" ParserLister class for SPARKY SPK files.
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
    from wwpdb.utils.nmr.pk.SparkySPKParser import SparkySPKParser
    from wwpdb.utils.nmr.pk.BasePKParserListener import BasePKParserListener
    from wwpdb.utils.nmr.mr.ParserListenerUtil import (REPRESENTATIVE_MODEL_ID,
                                                       REPRESENTATIVE_ALT_ID,
                                                       getPkRow)
    from wwpdb.utils.nmr.ChemCompUtil import ChemCompUtil
    from wwpdb.utils.nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from wwpdb.utils.nmr.nef.NEFTranslator import NEFTranslator
except ImportError:
    from nmr.io.CifReader import CifReader
    from nmr.pk.SparkySPKParser import SparkySPKParser
    from nmr.pk.BasePKParserListener import BasePKParserListener
    from nmr.mr.ParserListenerUtil import (REPRESENTATIVE_MODEL_ID,
                                           REPRESENTATIVE_ALT_ID,
                                           getPkRow)
    from nmr.ChemCompUtil import ChemCompUtil
    from nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from nmr.nef.NEFTranslator import NEFTranslator


# This class defines a complete listener for a parse tree produced by SparkySPKParser.
class SparkySPKParserListener(ParseTreeListener, BasePKParserListener):

    __spectrum_names = None

    __cur_spectrum_name = None
    __cur_id = None
    __cur_height = None
    __cur_lw = None
    __cur_integral = None
    __cur_rs = None

    def __init__(self, verbose: bool = True, log: IO = sys.stdout,
                 representativeModelId: int = REPRESENTATIVE_MODEL_ID,
                 representativeAltId: str = REPRESENTATIVE_ALT_ID,
                 mrAtomNameMapping: Optional[List[dict]] = None,
                 cR: Optional[CifReader] = None, caC: Optional[dict] = None, ccU: Optional[ChemCompUtil] = None,
                 csStat: Optional[BMRBChemShiftStat] = None, nefT: Optional[NEFTranslator] = None,
                 reasons: Optional[dict] = None):
        super().__init__(verbose, log, representativeModelId, representativeAltId,
                         mrAtomNameMapping, cR, caC, ccU, csStat, nefT, reasons)

        self.file_type = 'nm-pea-sps'
        self.software_name = 'SPARKY'

    # Enter a parse tree produced by SparkySPKParser#sparky_spk.
    def enterSparky_spk(self, ctx: SparkySPKParser.Sparky_spkContext):  # pylint: disable=unused-argument
        self.__spectrum_names = {}

        self.enter()

    # Exit a parse tree produced by SparkySPKParser#sparky_spk.
    def exitSparky_spk(self, ctx: SparkySPKParser.Sparky_spkContext):  # pylint: disable=unused-argument
        self.exit(self.__spectrum_names if len(self.__spectrum_names) > 0 else None)

    # Enter a parse tree produced by SparkySPKParser#user_block.
    def enterUser_block(self, ctx: SparkySPKParser.User_blockContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by SparkySPKParser#user_block.
    def exitUser_block(self, ctx: SparkySPKParser.User_blockContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by SparkySPKParser#user_statement.
    def enterUser_statement(self, ctx: SparkySPKParser.User_statementContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by SparkySPKParser#user_statement.
    def exitUser_statement(self, ctx: SparkySPKParser.User_statementContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by SparkySPKParser#spectrum_block.
    def enterSpectrum_block(self, ctx: SparkySPKParser.Spectrum_blockContext):  # pylint: disable=unused-argument
        self.__cur_spectrum_name = []

    # Exit a parse tree produced by SparkySPKParser#spectrum_block.
    def exitSpectrum_block(self, ctx: SparkySPKParser.Spectrum_blockContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by SparkySPKParser#spectrum_statement.
    def enterSpectrum_statement(self, ctx: SparkySPKParser.Spectrum_statementContext):
        if ctx.Dimension():
            self.num_of_dim = int(str(ctx.Integer_SP(0)))
            self.spectrum_name = ' '.join(self.__cur_spectrum_name)
            self.initSpectralDim()
            if self.num_of_dim not in self.__spectrum_names:
                self.__spectrum_names[self.num_of_dim] = {}
            if self.cur_list_id not in self.__spectrum_names[self.num_of_dim]:
                self.__spectrum_names[self.num_of_dim][self.cur_list_id] = self.spectrum_name

    # Exit a parse tree produced by SparkySPKParser#spectrum_statement.
    def exitSpectrum_statement(self, ctx: SparkySPKParser.Spectrum_statementContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by SparkySPKParser#spectrum_name.
    def enterSpectrum_name(self, ctx: SparkySPKParser.Spectrum_nameContext):
        if ctx.Integer_SP():
            self.__cur_spectrum_name.append(str(ctx.Integer_SP()))
        elif ctx.Float_SP():
            self.__cur_spectrum_name.append(str(ctx.Float_SP()))
        elif ctx.Simple_name_SP():
            self.__cur_spectrum_name.append(str(ctx.Simple_name_SP()))
        elif ctx.Any_name_SP():
            self.__cur_spectrum_name.append(str(ctx.Any_name_SP()))

    # Exit a parse tree produced by SparkySPKParser#spectrum_name.
    def exitSpectrum_name(self, ctx: SparkySPKParser.Spectrum_nameContext):
        pass

    # Enter a parse tree produced by SparkySPKParser#attached_data.
    def enterAttached_data(self, ctx: SparkySPKParser.Attached_dataContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by SparkySPKParser#attached_data.
    def exitAttached_data(self, ctx: SparkySPKParser.Attached_dataContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by SparkySPKParser#attached_data_statement.
    def enterAttached_data_statement(self, ctx: SparkySPKParser.Attached_data_statementContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by SparkySPKParser#attached_data_statement.
    def exitAttached_data_statement(self, ctx: SparkySPKParser.Attached_data_statementContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by SparkySPKParser#view.
    def enterView(self, ctx: SparkySPKParser.ViewContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by SparkySPKParser#view.
    def exitView(self, ctx: SparkySPKParser.ViewContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by SparkySPKParser#view_statement.
    def enterView_statement(self, ctx: SparkySPKParser.View_statementContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by SparkySPKParser#view_statement.
    def exitView_statement(self, ctx: SparkySPKParser.View_statementContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by SparkySPKParser#view_name.
    def enterView_name(self, ctx: SparkySPKParser.View_nameContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by SparkySPKParser#view_name.
    def exitView_name(self, ctx: SparkySPKParser.View_nameContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by SparkySPKParser#view_number.
    def enterView_number(self, ctx: SparkySPKParser.View_numberContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by SparkySPKParser#view_number.
    def exitView_number(self, ctx: SparkySPKParser.View_numberContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by SparkySPKParser#params.
    def enterParams(self, ctx: SparkySPKParser.ParamsContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by SparkySPKParser#params.
    def exitParams(self, ctx: SparkySPKParser.ParamsContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by SparkySPKParser#params_statement.
    def enterParams_statement(self, ctx: SparkySPKParser.Params_statementContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by SparkySPKParser#params_statement.
    def exitParams_statement(self, ctx: SparkySPKParser.Params_statementContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by SparkySPKParser#ornament.
    def enterOrnament(self, ctx: SparkySPKParser.OrnamentContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by SparkySPKParser#ornament.
    def exitOrnament(self, ctx: SparkySPKParser.OrnamentContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by SparkySPKParser#ornament_statement.
    def enterOrnament_statement(self, ctx: SparkySPKParser.Ornament_statementContext):
        if ctx.Type_OR() and ctx.Peak():
            if self.num_of_dim == 2:
                self.peaks2D += 1
            elif self.num_of_dim == 3:
                self.peaks3D += 1
            elif self.num_of_dim == 4:
                self.peaks4D += 1
            self.atomSelectionSets.clear()
            self.asIsSets.clear()
            self.__cur_id = None
            self.__cur_height = None
            self.__cur_lw = None
            self.__cur_integral = None
            self.__cur_rs = None

        elif ctx.Id():
            self.__cur_id = int(str(ctx.Integer_OR(0)))

        elif ctx.Height():
            self.__cur_height = str(ctx.Float_OR(0))
            if float(self.__cur_height) == 0.0 and ctx.Float_OR(1):
                self.__cur_height = str(ctx.Float_OR(1))

        elif ctx.Line_width():
            self.__cur_lw = [float(str(ctx.Float_OR(col))) for col in range(self.num_of_dim)]

        elif ctx.Integral():
            self.__cur_integral = str(ctx.Real_OR())

        elif ctx.Rs():
            self.__cur_rs = [str(ctx.Rs_ex(col)).strip('|') for col in range(self.num_of_dim)]

    # Exit a parse tree produced by SparkySPKParser#ornament_statement.
    def exitOrnament_statement(self, ctx: SparkySPKParser.Ornament_statementContext):
        pass

    # Enter a parse tree produced by SparkySPKParser#ornament_position.
    def enterOrnament_position(self, ctx: SparkySPKParser.Ornament_positionContext):

        try:

            if ctx.Float_OR():
                value = str(ctx.Float_OR())
                self.positionSelection.append(float(value))

            elif ctx.Integer_OR():
                value = str(ctx.Integer_OR())
                self.positionSelection.append(float(value))

            else:
                self.positionSelection.append(None)

        except ValueError:
            self.positionSelection.append(None)

    # Exit a parse tree produced by SparkySPKParser#ornament_position.
    def exitOrnament_position(self, ctx: SparkySPKParser.Ornament_positionContext):
        pass

    # Enter a parse tree produced by SparkySPKParser#label.
    def enterLabel(self, ctx: SparkySPKParser.LabelContext):  # pylint: disable=unused-argument

        if self.__cur_rs is not None:
            if all(len(rs.replace('|', '')) == 0 for rs in self.__cur_rs):
                self.__cur_rs = None
            else:
                for idx, rs in enumerate(self.__cur_rs):
                    if '?' in rs:
                        self.__cur_rs[idx] = '?'
                if not self.isFirstResidueAla:
                    for idx, rs in enumerate(self.__cur_rs):
                        if rs == 'A1|H':
                            self.__cur_rs[idx] = '?'

        if self.__cur_rs is not None:
            if self.num_of_dim == 2:
                self.exit_Peak_2d()
            elif self.num_of_dim == 3:
                self.exit_Peak_3d()
            elif self.num_of_dim == 4:
                self.exit_Peak_4d()

        else:
            if self.num_of_dim == 2:
                self.exit_Peak_wo_assign_2d()
            elif self.num_of_dim == 3:
                self.exit_Peak_wo_assign_3d()
            elif self.num_of_dim == 4:
                self.exit_Peak_wo_assign_4d()

    # Exit a parse tree produced by SparkySPKParser#label.
    def exitLabel(self, ctx: SparkySPKParser.LabelContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by SparkySPKParser#label_statement.
    def enterLabel_statement(self, ctx: SparkySPKParser.Label_statementContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by SparkySPKParser#label_statement.
    def exitLabel_statement(self, ctx: SparkySPKParser.Label_statementContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by SparkySPKParser#label_position.
    def enterLabel_position(self, ctx: SparkySPKParser.Label_positionContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by SparkySPKParser#label_position.
    def exitLabel_position(self, ctx: SparkySPKParser.Label_positionContext):  # pylint: disable=unused-argument
        pass

    def exit_Peak_2d(self):

        try:

            if len(self.positionSelection) == 0:
                self.peaks2D -= 1
                return

            index = self.__cur_id if self.__cur_id is not None else self.peaks2D

            x_ppm, y_ppm = self.positionSelection[0], self.positionSelection[1]

            x_lw_hz = y_lw_hz = None
            if self.__cur_lw is not None:
                x_lw_hz, y_lw_hz = self.__cur_lw[0], self.__cur_lw[1]

            height, volume = self.__cur_height, self.__cur_integral

            ass = '-'.join(self.__cur_rs)

            if not self.hasPolySeq and not self.hasNonPolySeq:
                return

            if None in (x_ppm, y_ppm):
                self.peaks2D -= 1
                return

            dstFunc = self.validatePeak2D(index, x_ppm, y_ppm, None, None, None, None,
                                          None, None, x_lw_hz, y_lw_hz, height, None, volume, None)

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
                                    or ass == '?-?' else ass)

        finally:
            self.positionSelection.clear()

    def exit_Peak_3d(self):

        try:

            if len(self.positionSelection) == 0:
                self.peaks3D -= 1
                return

            index = self.__cur_id if self.__cur_id is not None else self.peaks3D

            x_ppm, y_ppm, z_ppm = self.positionSelection[0], self.positionSelection[1], self.positionSelection[2]

            x_lw_hz = y_lw_hz = z_lw_hz = None
            if self.__cur_lw is not None:
                x_lw_hz, y_lw_hz, z_lw_hz = self.__cur_lw[0], self.__cur_lw[1], self.__cur_lw[2]

            height, volume = self.__cur_height, self.__cur_integral

            ass = '-'.join(self.__cur_rs)

            if not self.hasPolySeq and not self.hasNonPolySeq:
                return

            if None in (x_ppm, y_ppm, z_ppm):
                self.peaks3D -= 1
                return

            dstFunc = self.validatePeak3D(index, x_ppm, y_ppm, z_ppm, None, None, None, None, None, None,
                                          None, None, None, x_lw_hz, y_lw_hz, z_lw_hz, height, None, volume, None)

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
                                    or ass == '?-?-?' else ass)

        finally:
            self.positionSelection.clear()

    def exit_Peak_4d(self):

        try:

            if len(self.positionSelection) == 0:
                self.peaks4D -= 1
                return

            index = self.__cur_id if self.__cur_id is not None else self.peaks3D

            x_ppm, y_ppm, z_ppm, a_ppm = self.positionSelection[0], self.positionSelection[1], self.positionSelection[2], self.positionSelection[3]

            x_lw_hz = y_lw_hz = z_lw_hz = a_lw_hz = None
            if self.__cur_lw is not None:
                x_lw_hz, y_lw_hz, z_lw_hz, a_lw_hz = self.__cur_lw[0], self.__cur_lw[1], self.__cur_lw[2], self.__cur_lw[3]

            height, volume = self.__cur_height, self.__cur_integral

            ass = '-'.join(self.__cur_rs)

            if not self.hasPolySeq and not self.hasNonPolySeq:
                return

            if None in (x_ppm, y_ppm, z_ppm, a_ppm):
                self.peaks4D -= 1
                return

            dstFunc = self.validatePeak4D(index, x_ppm, y_ppm, z_ppm, a_ppm, None, None, None, None, None, None, None, None,
                                          None, None, None, None, x_lw_hz, y_lw_hz, z_lw_hz, a_lw_hz, height, None, volume, None)

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
                                    or ass == '?-?-?-?' else ass)

        finally:
            self.positionSelection.clear()

    def exit_Peak_wo_assign_2d(self):

        try:

            if len(self.positionSelection) == 0:
                self.peaks2D -= 1
                return

            index = self.__cur_id if self.__cur_id is not None else self.peaks2D

            x_ppm, y_ppm = self.positionSelection[0], self.positionSelection[1]

            x_lw_hz = y_lw_hz = None
            if self.__cur_lw is not None:
                x_lw_hz, y_lw_hz = self.__cur_lw[0], self.__cur_lw[1]

            height, volume = self.__cur_height, self.__cur_integral

            if not self.hasPolySeq and not self.hasNonPolySeq:
                return

            if None in (x_ppm, y_ppm):
                self.peaks2D -= 1
                return

            dstFunc = self.validatePeak2D(index, x_ppm, y_ppm, None, None, None, None,
                                          None, None, x_lw_hz, y_lw_hz, height, None, volume, None)

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
                                   None, None, None)
                    sf['loop'].add_data(row)

        finally:
            self.positionSelection.clear()

    def exit_Peak_wo_assign_3d(self):

        try:

            if len(self.positionSelection) == 0:
                self.peaks3D -= 1
                return

            index = self.__cur_id if self.__cur_id is not None else self.peaks3D

            x_ppm, y_ppm, z_ppm = self.positionSelection[0], self.positionSelection[1], self.positionSelection[2]

            x_lw_hz = y_lw_hz = z_lw_hz = None
            if self.__cur_lw is not None:
                x_lw_hz, y_lw_hz, z_lw_hz = self.__cur_lw[0], self.__cur_lw[1], self.__cur_lw[2]

            height, volume = self.__cur_height, self.__cur_integral

            if not self.hasPolySeq and not self.hasNonPolySeq:
                return

            if None in (x_ppm, y_ppm, z_ppm):
                self.peaks3D -= 1
                return

            dstFunc = self.validatePeak3D(index, x_ppm, y_ppm, z_ppm, None, None, None, None, None, None,
                                          None, None, None, x_lw_hz, y_lw_hz, z_lw_hz, height, None, volume, None)

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
                                   None, None, None)
                    sf['loop'].add_data(row)

        finally:
            self.positionSelection.clear()

    def exit_Peak_wo_assign_4d(self):

        try:

            if len(self.positionSelection) == 0:
                self.peaks4D -= 1
                return

            index = self.__cur_id if self.__cur_id is not None else self.peaks4D

            x_ppm, y_ppm, z_ppm, a_ppm = self.positionSelection[0], self.positionSelection[1], self.positionSelection[2], self.positionSelection[3]

            x_lw_hz = y_lw_hz = z_lw_hz = a_lw_hz = None
            if self.__cur_lw is not None:
                x_lw_hz, y_lw_hz, z_lw_hz, a_lw_hz = self.__cur_lw[0], self.__cur_lw[1], self.__cur_lw[2], self.__cur_lw[3]

            height, volume = self.__cur_height, self.__cur_integral

            if not self.hasPolySeq and not self.hasNonPolySeq:
                return

            if None in (x_ppm, y_ppm, z_ppm, a_ppm):
                self.peaks4D -= 1
                return

            dstFunc = self.validatePeak4D(index, x_ppm, y_ppm, z_ppm, a_ppm, None, None, None, None, None, None, None, None,
                                          None, None, None, None, x_lw_hz, y_lw_hz, z_lw_hz, a_lw_hz, height, None, volume, None)

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
                                   None, None, None)
                    sf['loop'].add_data(row)

        finally:
            self.positionSelection.clear()


# del SparkySPKParser
