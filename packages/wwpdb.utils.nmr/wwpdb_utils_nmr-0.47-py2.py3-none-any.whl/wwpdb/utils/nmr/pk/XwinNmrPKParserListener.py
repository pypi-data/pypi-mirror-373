##
# File: XwinNmrPKParserListener.py
# Date: 05-Dec-2024
#
# Updates:
""" ParserLister class for XWINNMR PK files.
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
    from wwpdb.utils.nmr.pk.XwinNmrPKParser import XwinNmrPKParser
    from wwpdb.utils.nmr.pk.BasePKParserListener import BasePKParserListener
    from wwpdb.utils.nmr.mr.ParserListenerUtil import (REPRESENTATIVE_MODEL_ID,
                                                       REPRESENTATIVE_ALT_ID,
                                                       getPkRow)
    from wwpdb.utils.nmr.ChemCompUtil import ChemCompUtil
    from wwpdb.utils.nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from wwpdb.utils.nmr.nef.NEFTranslator import NEFTranslator
except ImportError:
    from nmr.io.CifReader import CifReader
    from nmr.pk.XwinNmrPKParser import XwinNmrPKParser
    from nmr.pk.BasePKParserListener import BasePKParserListener
    from nmr.mr.ParserListenerUtil import (REPRESENTATIVE_MODEL_ID,
                                           REPRESENTATIVE_ALT_ID,
                                           getPkRow)
    from nmr.ChemCompUtil import ChemCompUtil
    from nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from nmr.nef.NEFTranslator import NEFTranslator


# This class defines a complete listener for a parse tree produced by XwinNmrPKParser.
class XwinNmrPKParserListener(ParseTreeListener, BasePKParserListener):

    __spectrum_names = None

    __f1_ppm_col = -1
    __f2_ppm_col = -1
    __f3_ppm_col = -1
    __f4_ppm_col = -1
    __intensity_col = -1
    __volume_col = -1

    def __init__(self, verbose: bool = True, log: IO = sys.stdout,
                 representativeModelId: int = REPRESENTATIVE_MODEL_ID,
                 representativeAltId: str = REPRESENTATIVE_ALT_ID,
                 mrAtomNameMapping: Optional[List[dict]] = None,
                 cR: Optional[CifReader] = None, caC: Optional[dict] = None, ccU: Optional[ChemCompUtil] = None,
                 csStat: Optional[BMRBChemShiftStat] = None, nefT: Optional[NEFTranslator] = None,
                 reasons: Optional[dict] = None):
        super().__init__(verbose, log, representativeModelId, representativeAltId,
                         mrAtomNameMapping, cR, caC, ccU, csStat, nefT, reasons)

        self.file_type = 'nm-pea-xwi'
        self.software_name = 'XWINNMR'

    # Enter a parse tree produced by XwinNmrPKParser#xwinnmr_pk.
    def enterXwinnmr_pk(self, ctx: XwinNmrPKParser.Xwinnmr_pkContext):  # pylint: disable=unused-argument
        self.__spectrum_names = {}

        self.enter()

    # Exit a parse tree produced by XwinNmrPKParser#xwinnmr_pk.
    def exitXwinnmr_pk(self, ctx: XwinNmrPKParser.Xwinnmr_pkContext):  # pylint: disable=unused-argument
        self.exit(self.__spectrum_names if len(self.__spectrum_names) > 0 else None)

    # Enter a parse tree produced by XwinNmrPKParser#comment.
    def enterComment(self, ctx: XwinNmrPKParser.CommentContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by XwinNmrPKParser#comment.
    def exitComment(self, ctx: XwinNmrPKParser.CommentContext):
        comment = []
        for col in range(20):
            if ctx.Any_name(col):
                text = str(ctx.Any_name(col))
                if text.startswith('NAME='):
                    self.spectrum_name = text[5:-1]
                comment.append(text)
            else:
                break

        self.__f1_ppm_col = -1
        self.__f2_ppm_col = -1
        self.__f3_ppm_col = -1
        self.__f4_ppm_col = -1
        self.__intensity_col = -1
        self.__volume_col = -1

        if 'F1[ppm]' in comment:
            self.__f1_ppm_col = comment.index('F1[ppm]')
        if 'F2[ppm]' in comment:
            self.__f2_ppm_col = comment.index('F2[ppm]')
        if 'F3[ppm]' in comment and self.num_of_dim >= 3:
            self.__f3_ppm_col = comment.index('F3[ppm]')
        if 'F4[ppm]' in comment and self.num_of_dim >= 4:
            self.__f4_ppm_col = comment.index('F4[ppm]')
        if 'Intensity' in comment:
            self.__intensity_col = comment.index('Intensity')
        if 'Volume' in comment:
            self.__volume_col = comment.index('Volume')

    # Enter a parse tree produced by XwinNmrPKParser#dimension.
    def enterDimension(self, ctx: XwinNmrPKParser.DimensionContext):
        if ctx.Integer_ND():
            self.num_of_dim = int(str(ctx.Integer_ND()))
            self.initSpectralDim()

            if self.spectrum_name is not None:
                if self.num_of_dim not in self.__spectrum_names:
                    self.__spectrum_names[self.num_of_dim] = {}
                if self.cur_list_id not in self.__spectrum_names[self.num_of_dim]:
                    self.__spectrum_names[self.num_of_dim][self.cur_list_id] = self.spectrum_name

    # Exit a parse tree produced by XwinNmrPKParser#dimension.
    def exitDimension(self, ctx: XwinNmrPKParser.DimensionContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by XwinNmrPKParser#peak_2d.
    def enterPeak_2d(self, ctx: XwinNmrPKParser.Peak_2dContext):  # pylint: disable=unused-argument
        self.peaks2D += 1

    # Exit a parse tree produced by XwinNmrPKParser#peak_2d.
    def exitPeak_2d(self, ctx: XwinNmrPKParser.Peak_2dContext):

        if -1 in (self.__f1_ppm_col, self.__f2_ppm_col)\
           or (self.__intensity_col == -1 and self.__volume_col == -1):
            self.peaks2D -= 1
            return

        index = int(str(ctx.Integer()))

        if ctx.Float(self.__f1_ppm_col):
            f1_ppm = float(str(ctx.Float(self.__f1_ppm_col)))
        else:
            self.peaks2D -= 1
            return

        if ctx.Float(self.__f2_ppm_col):
            f2_ppm = float(str(ctx.Float(self.__f2_ppm_col)))
        else:
            self.peaks2D -= 1
            return

        intensity = None
        if self.__intensity_col != -1 and ctx.Float(self.__intensity_col):
            intensity = float(str(ctx.Float(self.__intensity_col)))

        volume = None
        if self.__volume_col != -1 and ctx.Float(self.__volume_col):
            volume = float(str(ctx.Float(self.__volume_col)))

        annotation = None
        if ctx.Annotation(0):
            if self.__hasCoord:
                annotation = []
                i = 0
                while ctx.Annotation(i):
                    annotation.append(str(ctx.Annotation(i)))
                    i += 1
                annotation = ' '.join(annotation)

        dstFunc = self.validatePeak2D(index, f1_ppm, f2_ppm, None, None, None, None,
                                      None, None, None, None, intensity, None, volume, None)

        if dstFunc is None:
            self.peaks2D -= 1
            return

        cur_spectral_dim = self.spectral_dim[self.num_of_dim][self.cur_list_id]

        cur_spectral_dim[1]['freq_hint'].append(f1_ppm)
        cur_spectral_dim[2]['freq_hint'].append(f2_ppm)

        if self.debug:
            print(f"subtype={self.cur_subtype} id={self.peaks2D} (index={index}) {dstFunc}")

        if self.createSfDict__:
            sf = self.getSf()

            if sf is not None:
                sf['id'] = index
                sf['index_id'] += 1

                row = getPkRow(self.cur_subtype, sf['id'], sf['index_id'],
                               sf['list_id'], self.entryId, dstFunc,
                               None, None, None,
                               details=annotation)
                sf['loop'].add_data(row)

    # Enter a parse tree produced by XwinNmrPKParser#peak_3d.
    def enterPeak_3d(self, ctx: XwinNmrPKParser.Peak_3dContext):  # pylint: disable=unused-argument
        self.peaks3D += 1

    # Exit a parse tree produced by XwinNmrPKParser#peak_3d.
    def exitPeak_3d(self, ctx: XwinNmrPKParser.Peak_3dContext):

        if -1 in (self.__f1_ppm_col, self.__f2_ppm_col, self.__f3_ppm_col)\
           or (self.__intensity_col == -1 and self.__volume_col == -1):
            self.peaks3D -= 1
            return

        index = int(str(ctx.Integer()))

        if ctx.Float(self.__f1_ppm_col):
            f1_ppm = float(str(ctx.Float(self.__f1_ppm_col)))
        else:
            self.peaks3D -= 1
            return

        if ctx.Float(self.__f2_ppm_col):
            f2_ppm = float(str(ctx.Float(self.__f2_ppm_col)))
        else:
            self.peaks3D -= 1
            return

        if ctx.Float(self.__f3_ppm_col):
            f3_ppm = float(str(ctx.Float(self.__f3_ppm_col)))
        else:
            self.peaks3D -= 1
            return

        intensity = None
        if self.__intensity_col != -1 and ctx.Float(self.__intensity_col):
            intensity = float(str(ctx.Float(self.__intensity_col)))

        volume = None
        if self.__volume_col != -1 and ctx.Float(self.__volume_col):
            volume = float(str(ctx.Float(self.__volume_col)))

        annotation = None
        if ctx.Annotation(0):
            if self.__hasCoord:
                annotation = []
                i = 0
                while ctx.Annotation(i):
                    annotation.append(str(ctx.Annotation(i)))
                    i += 1
                annotation = ' '.join(annotation)

        dstFunc = self.validatePeak3D(index, f1_ppm, f2_ppm, f3_ppm, None, None, None, None, None, None,
                                      None, None, None, None, None, None, intensity, None, volume, None)

        if dstFunc is None:
            self.peaks3D -= 1
            return

        cur_spectral_dim = self.spectral_dim[self.num_of_dim][self.cur_list_id]

        cur_spectral_dim[1]['freq_hint'].append(f1_ppm)
        cur_spectral_dim[2]['freq_hint'].append(f2_ppm)
        cur_spectral_dim[3]['freq_hint'].append(f3_ppm)

        if self.debug:
            print(f"subtype={self.cur_subtype} id={self.peaks3D} (index={index}) {dstFunc}")

        if self.createSfDict__:
            sf = self.getSf()

            if sf is not None:
                sf['id'] = index
                sf['index_id'] += 1

                row = getPkRow(self.cur_subtype, sf['id'], sf['index_id'],
                               sf['list_id'], self.entryId, dstFunc,
                               None, None, None,
                               details=annotation)
                sf['loop'].add_data(row)

    # Enter a parse tree produced by XwinNmrPKParser#peak_4d.
    def enterPeak_4d(self, ctx: XwinNmrPKParser.Peak_4dContext):  # pylint: disable=unused-argument
        self.peaks4D += 1

    # Exit a parse tree produced by XwinNmrPKParser#peak_4d.
    def exitPeak_4d(self, ctx: XwinNmrPKParser.Peak_4dContext):

        if -1 in (self.__f1_ppm_col, self.__f2_ppm_col, self.__f3_ppm_col, self.__f4_ppm_col)\
           or (self.__intensity_col == -1 and self.__volume_col == -1):
            self.peaks4D -= 1
            return

        index = int(str(ctx.Integer()))

        if ctx.Float(self.__f1_ppm_col):
            f1_ppm = float(str(ctx.Float(self.__f1_ppm_col)))
        else:
            self.peaks4D -= 1
            return

        if ctx.Float(self.__f2_ppm_col):
            f2_ppm = float(str(ctx.Float(self.__f2_ppm_col)))
        else:
            self.peaks4D -= 1
            return

        if ctx.Float(self.__f3_ppm_col):
            f3_ppm = float(str(ctx.Float(self.__f3_ppm_col)))
        else:
            self.peaks4D -= 1
            return

        if ctx.Float(self.__f4_ppm_col):
            f4_ppm = float(str(ctx.Float(self.__f4_ppm_col)))
        else:
            self.peaks4D -= 1
            return

        intensity = None
        if self.__intensity_col != -1 and ctx.Float(self.__intensity_col):
            intensity = float(str(ctx.Float(self.__intensity_col)))

        volume = None
        if self.__volume_col != -1 and ctx.Float(self.__volume_col):
            volume = float(str(ctx.Float(self.__volume_col)))

        annotation = None
        if ctx.Annotation(0):
            if self.__hasCoord:
                annotation = []
                i = 0
                while ctx.Annotation(i):
                    annotation.append(str(ctx.Annotation(i)))
                    i += 1
                annotation = ' '.join(annotation)

        dstFunc = self.validatePeak4D(index, f1_ppm, f2_ppm, f3_ppm, f4_ppm, None, None, None, None, None, None, None, None,
                                      None, None, None, None, None, None, None, None, intensity, None, volume, None)

        if dstFunc is None:
            self.peaks4D -= 1
            return

        cur_spectral_dim = self.spectral_dim[self.num_of_dim][self.cur_list_id]

        cur_spectral_dim[1]['freq_hint'].append(f1_ppm)
        cur_spectral_dim[2]['freq_hint'].append(f2_ppm)
        cur_spectral_dim[3]['freq_hint'].append(f3_ppm)
        cur_spectral_dim[4]['freq_hint'].append(f4_ppm)

        if self.debug:
            print(f"subtype={self.cur_subtype} id={self.peaks4D} (index={index}) {dstFunc}")

        if self.createSfDict__:
            sf = self.getSf()

            if sf is not None:
                sf['id'] = index
                sf['index_id'] += 1

                row = getPkRow(self.cur_subtype, sf['id'], sf['index_id'],
                               sf['list_id'], self.entryId, dstFunc,
                               None, None, None,
                               details=annotation)
                sf['loop'].add_data(row)


# del XwinNmrPKParser
