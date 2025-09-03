##
# XplorMRReader.py
#
# Update:
##
""" A collection of classes for parsing XPLOR-NIH MR files.
"""
__docformat__ = "restructuredtext en"
__author__ = "Masashi Yokochi"
__email__ = "yokochi@protein.osaka-u.ac.jp"
__license__ = "Apache License 2.0"
__version__ = "1.0.0"

import sys
import os

from antlr4 import InputStream, CommonTokenStream, ParseTreeWalker, PredictionMode
from typing import IO, List, Tuple, Optional

try:
    from wwpdb.utils.nmr.mr.LexerErrorListener import LexerErrorListener
    from wwpdb.utils.nmr.mr.ParserErrorListener import ParserErrorListener
    from wwpdb.utils.nmr.mr.XplorMRLexer import XplorMRLexer
    from wwpdb.utils.nmr.mr.XplorMRParser import XplorMRParser
    from wwpdb.utils.nmr.mr.XplorMRParserListener import XplorMRParserListener
    from wwpdb.utils.nmr.mr.ParserListenerUtil import (coordAssemblyChecker,
                                                       retrieveOriginalFileName,
                                                       MAX_ERROR_REPORT,
                                                       REPRESENTATIVE_MODEL_ID,
                                                       REPRESENTATIVE_ALT_ID)
    from wwpdb.utils.nmr.io.CifReader import CifReader
    from wwpdb.utils.nmr.ChemCompUtil import ChemCompUtil
    from wwpdb.utils.nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from wwpdb.utils.nmr.nef.NEFTranslator import NEFTranslator
except ImportError:
    from nmr.mr.LexerErrorListener import LexerErrorListener
    from nmr.mr.ParserErrorListener import ParserErrorListener
    from nmr.mr.XplorMRLexer import XplorMRLexer
    from nmr.mr.XplorMRParser import XplorMRParser
    from nmr.mr.XplorMRParserListener import XplorMRParserListener
    from nmr.mr.ParserListenerUtil import (coordAssemblyChecker,
                                           retrieveOriginalFileName,
                                           MAX_ERROR_REPORT,
                                           REPRESENTATIVE_MODEL_ID,
                                           REPRESENTATIVE_ALT_ID)
    from nmr.io.CifReader import CifReader
    from nmr.ChemCompUtil import ChemCompUtil
    from nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from nmr.nef.NEFTranslator import NEFTranslator


class XplorMRReader:
    """ Accessor methods for parsing XPLOR-NIH MR files.
    """

    def __init__(self, verbose: bool = True, log: IO = sys.stdout,
                 representativeModelId: int = REPRESENTATIVE_MODEL_ID,
                 representativeAltId: str = REPRESENTATIVE_ALT_ID,
                 mrAtomNameMapping: Optional[List[dict]] = None,
                 cR: Optional[CifReader] = None, caC: Optional[dict] = None, ccU: Optional[ChemCompUtil] = None,
                 csStat: Optional[BMRBChemShiftStat] = None, nefT: Optional[NEFTranslator] = None,
                 reasons: Optional[dict] = None):
        self.__class_name__ = self.__class__.__name__
        self.__version__ = __version__

        self.__verbose = verbose
        self.__lfh = log
        self.__debug = False
        self.__remediate = False
        self.__internal = False
        self.__sll_pred = False

        self.__nmr_vs_model = None

        self.__maxLexerErrorReport = MAX_ERROR_REPORT
        self.__maxParserErrorReport = MAX_ERROR_REPORT

        self.__representativeModelId = representativeModelId
        self.__representativeAltId = representativeAltId
        self.__mrAtomNameMapping = mrAtomNameMapping

        # CCD accessing utility
        self.__ccU = ChemCompUtil(verbose, log) if ccU is None else ccU

        if cR is not None and caC is None:
            caC = coordAssemblyChecker(verbose, log, representativeModelId, representativeAltId,
                                       cR, self.__ccU, None, None, fullCheck=False)

        self.__cR = cR
        self.__caC = caC

        # BMRB chemical shift statistics
        self.__csStat = BMRBChemShiftStat(verbose, log, self.__ccU) if csStat is None else csStat

        # NEFTranslator
        self.__nefT = NEFTranslator(verbose, log, self.__ccU, self.__csStat) if nefT is None else nefT
        if nefT is None:
            self.__nefT.set_remediation_mode(True)

        # reasons for re-parsing request from the previous trial
        self.__reasons = reasons

    def setDebugMode(self, debug: bool):
        self.__debug = debug

    def setRemediateMode(self, remediate: bool):
        self.__remediate = remediate

    def setInternalMode(self, internal: bool):
        self.__internal = internal

    def setNmrChainAssignments(self, nmr_vs_model: Optional[List[dict]]):
        self.__nmr_vs_model = nmr_vs_model

    def setLexerMaxErrorReport(self, maxErrReport: int):
        self.__maxLexerErrorReport = maxErrReport

    def setParserMaxErrorReport(self, maxErrReport: int):
        self.__maxParserErrorReport = maxErrReport

    def setSllPredMode(self, sll_pred: bool):
        self.__sll_pred = sll_pred

    def parse(self, mrFilePath: str, cifFilePath: Optional[str] = None, isFilePath: bool = True,
              createSfDict: bool = False, originalFileName: Optional[str] = None, listIdCounter: Optional[dict] = None, entryId: Optional[str] = None
              ) -> Tuple[Optional[XplorMRParserListener], Optional[ParserErrorListener], Optional[LexerErrorListener]]:
        """ Parse XPLOR-NIH MR file.
            @return: XplorMRParserListener for success or None otherwise, ParserErrorListener, LexerErrorListener.
        """

        ifh = None

        try:

            if isFilePath:
                mrString = None

                if not os.access(mrFilePath, os.R_OK):
                    if self.__verbose:
                        self.__lfh.write(f"+{self.__class_name__}.parse() {mrFilePath} is not accessible.\n")
                    return None, None, None

                ifh = open(mrFilePath, 'r', encoding='utf-8', errors='ignore')  # pylint: disable=consider-using-with
                input = InputStream(ifh.read())

            else:
                mrFilePath, mrString = None, mrFilePath

                if mrString is None or len(mrString) == 0:
                    if self.__verbose:
                        self.__lfh.write(f"+{self.__class_name__}.parse() Empty string.\n")
                    return None, None, None

                input = InputStream(mrString)

            if cifFilePath is not None:
                if not os.access(cifFilePath, os.R_OK):
                    if self.__verbose:
                        self.__lfh.write(f"+{self.__class_name__}.parse() {cifFilePath} is not accessible.\n")
                    return None, None, None

                if self.__cR is None:
                    self.__cR = CifReader(self.__verbose, self.__lfh)
                    if not self.__cR.parse(cifFilePath):
                        return None, None, None

            lexer = XplorMRLexer(input)
            lexer.removeErrorListeners()

            lexer_error_listener = LexerErrorListener(mrFilePath, inputString=mrString, maxErrorReport=self.__maxLexerErrorReport)
            lexer.addErrorListener(lexer_error_listener)

            messageList = lexer_error_listener.getMessageList()

            if messageList is not None and self.__verbose:
                for description in messageList:
                    self.__lfh.write(f"[Syntax error] line {description['line_number']}:{description['column_position']} {description['message']}\n")
                    if 'input' in description:
                        self.__lfh.write(f"{description['input']}\n")
                        self.__lfh.write(f"{description['marker']}\n")

            stream = CommonTokenStream(lexer)
            parser = XplorMRParser(stream)
            if not isFilePath or self.__sll_pred:
                parser._interp.predictionMode = PredictionMode.SLL  # pylint: disable=protected-access
            parser.removeErrorListeners()
            parser_error_listener = ParserErrorListener(mrFilePath, inputString=mrString, maxErrorReport=self.__maxParserErrorReport)
            parser.addErrorListener(parser_error_listener)
            tree = parser.xplor_nih_mr()

            walker = ParseTreeWalker()
            listener = XplorMRParserListener(self.__verbose, self.__lfh,
                                             self.__representativeModelId,
                                             self.__representativeAltId,
                                             self.__mrAtomNameMapping,
                                             self.__cR, self.__caC,
                                             self.__ccU, self.__csStat, self.__nefT,
                                             self.__reasons)
            listener.setDebugMode(self.__debug)
            listener.setRemediateMode(self.__remediate)
            listener.setInternalMode(self.__internal)
            listener.setNmrChainAssignments(self.__nmr_vs_model)
            listener.createSfDict(createSfDict)
            if createSfDict:
                listener.setOriginaFileName(originalFileName if originalFileName is not None else retrieveOriginalFileName(mrFilePath))
                if listIdCounter is not None:
                    listener.setListIdCounter(listIdCounter)
                if entryId is not None:
                    listener.setEntryId(entryId)
            walker.walk(listener, tree)

            messageList = parser_error_listener.getMessageList()

            if messageList is not None and self.__verbose:
                for description in messageList:
                    self.__lfh.write(f"[Syntax error] line {description['line_number']}:{description['column_position']} {description['message']}\n")
                    if 'input' in description:
                        self.__lfh.write(f"{description['input']}\n")
                        self.__lfh.write(f"{description['marker']}\n")

            if self.__verbose and self.__debug:
                if listener.warningMessage is not None and len(listener.warningMessage) > 0:
                    self.__lfh.write(f"+{self.__class_name__}.parse() ++ Info  -\n" + '\n'.join(listener.warningMessage) + '\n')
                if isFilePath:
                    self.__lfh.write(f"+{self.__class_name__}.parse() ++ Info  - {listener.getContentSubtype()}\n")

            return listener, parser_error_listener, lexer_error_listener

        except IOError as e:
            if self.__verbose:
                self.__lfh.write(f"+{self.__class_name__}.parse() ++ Error  - {str(e)}\n")
            return None, None, None
        finally:
            if isFilePath and ifh is not None:
                ifh.close()


if __name__ == "__main__":
    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7cv3/bmr36374/work/data/D_1300018300_mr-upload_P5.xplor-nih.V2',
                     '../../tests-nmr/mock-data-remediation/7cv3/7cv3.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/9atn/bmr31041/work/data/D_1000260878_mr-upload_P1.xplor-nih.V2',
                     '../../tests-nmr/mock-data-remediation/9atn/9atn.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = XplorMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2mf8/2mf8-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2mf8/2mf8.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2ju4/2ju4-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2ju4/2ju4.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2mp0/2mp0-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2mp0/2mp0.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2lhy/2lhy-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2lhy/2lhy.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2lhk/2lhk-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2lhk/2lhk.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2laz/2laz-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2laz/2laz.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = XplorMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2law/2law-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2law/2law.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = XplorMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2law/2law-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2law/2law.cif')

    reader = XplorMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2joa/2joa-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2joa/2joa.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = XplorMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2joa/2joa-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2joa/2joa.cif')

    reader = XplorMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2ymj/2ymj-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2ymj/2ymj.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = XplorMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2ymj/2ymj-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2ymj/2ymj.cif')

    reader = XplorMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2n8a/2n8a-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2n8a/2n8a.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = XplorMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2n8a/2n8a-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2n8a/2n8a.cif')

    reader = XplorMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2ljb/2ljb-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2ljb/2ljb.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = XplorMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2ljb/2ljb-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2ljb/2ljb.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/4ch0/4ch0-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/4ch0/4ch0.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2lz3/2lz3-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2lz3/2lz3.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2m56/2m56-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2m56/2m56.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = XplorMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2m56/2m56-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2m56/2m56.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2rse/2rse-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2rse/2rse.cif')

    reasons_ = {'segment_id_mismatch': {'AN1': 'A', 'SSS': None, 'AN2': 'B', 'AN3': 'C', 'AN4': 'D', 'RI1': 'A'},
                'segment_id_match_stats': {'AN1': {'A': 99, 'B': 90, 'C': 90, 'D': 90},
                                           'SSS': {},
                                           'AN2': {'A': -149, 'B': -126, 'C': -126, 'D': -126},
                                           'AN3': {'D': -114, 'A': -137, 'C': -114, 'B': -114},
                                           'AN4': {'D': -110, 'A': -133, 'C': -110, 'B': -110},
                                           'RI1': {'C': -14, 'B': -14, 'A': -2, 'D': -14}},
                'segment_id_poly_type_stats': {'AN1': {'polymer': 1044, 'non-poly': 42, 'non-polymer': 0},
                                               'SSS': {'polymer': 0, 'non-poly': 0},
                                               'AN2': {'polymer': 216, 'non-poly': 7, 'non-polymer': 0},
                                               'AN3': {'polymer': 236, 'non-poly': 7, 'non-polymer': 0},
                                               'AN4': {'polymer': 236, 'non-poly': 7, 'non-polymer': 0},
                                               'RI1': {'polymer': 19, 'non-poly': 12, 'non-polymer': 0}},
                'label_seq_scheme': {'dist': True, 'rdc': True, 'dihed': True},
                'inhibit_label_seq_scheme': {'A': {'dist': True}, 'B': {'dist': True}, 'C': {'dist': True}, 'D': {'dist': True}},
                'non_poly_remap': {'RIM': {1: {'chain_id': 'A', 'seq_id': 1, 'original_chain_id': 'D'}}}}
    reader = XplorMRReader(True, reasons=reasons_)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2ljc/2ljc-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2ljc/2ljc.cif')

    reader = XplorMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2l90/2l90-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2l90/2l90.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = XplorMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2l90/2l90-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2l90/2l90.cif')

    reader = XplorMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2la5/2la5-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2la5/2la5.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = XplorMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2la5/2la5-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2la5/2la5.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/7k7f/HBond_HBDB_renumbered.tbl',
                 '../../tests-nmr/mock-data-remediation/7k7f/7k7f.cif')

    reasons__ = {}
    for c, o in zip(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'], [100, 200, 300, 400, 500, 600, 700, 800, 900]):
        for s in range(1, 56):
            reasons__[s + o] = {'chain_id': c, 'seq_id': s}
    reasons_ = {'chain_id_remap': reasons__}
    reader = XplorMRReader(True, reasons=reasons_)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lzs/2lzs-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2lzs/2lzs.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-D_1300043061/D_1300043061_mr-upload_P1.xplor-nih.V3',
                     '../../tests-nmr/mock-data-D_1300043061/D_800647_model_P1.cif.V4')

    reader = XplorMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2khx/2khx-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2khx/2khx.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = XplorMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2khx/2khx-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2khx/2khx.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2lax/2lax-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2lax/2lax.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = XplorMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2kid/2kid-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2kid/2kid.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = XplorMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2kid/2kid-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2kid/2kid.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6d53/wr_distILB.tbl',
                 '../../tests-nmr/mock-data-remediation/6d53/6d53.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6c8u/msi2_cacb.tbl-corrected',
                     '../../tests-nmr/mock-data-remediation/6c8u/6c8u.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7kbv/distance.xplor',
                     '../../tests-nmr/mock-data-remediation/7kbv/7kbv.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/7n7e/plane.tbl-corrected',
                 '../../tests-nmr/mock-data-remediation/7n7e/7n7e.cif')

    reader = XplorMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2l5y/2l5y-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2l5y/2l5y.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = XplorMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2l5y/2l5y-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2l5y/2l5y.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2khx/2khx-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2khx/2khx.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = XplorMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2khx/2khx-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2khx/2khx.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2nci/2nci-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2nci/2nci.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7wnr/D_1300027046_mr_P2.xplor-nih.V1-corrected',
                     '../../tests-nmr/mock-data-remediation/7wnr/7wnr.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7wnr/D_1300027046_mr_P1.xplor-nih.V1-corrected',
                     '../../tests-nmr/mock-data-remediation/7wnr/7wnr.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2knf/2knf-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2knf/2knf.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = XplorMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2knf/2knf-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2knf/2knf.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2nbj/2nbj-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2nbj/2nbj.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/5t1n/PCS_HN.tbl',
                 '../../tests-nmr/mock-data-remediation/5t1n/5t1n.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2m6z/2m6z-corrected.mr.1',
                     '../../tests-nmr/mock-data-remediation/2m6z/2m6z.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2mlz/2mlz-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2mlz/2mlz.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = XplorMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/4b1q/4b1q-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/4b1q/4b1q.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = XplorMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/4b1q/4b1q-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/4b1q/4b1q.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2kf4/2kf4-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2kf4/2kf4.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/1iym/1iym-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/1iym/1iym.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/5oay/cluster_noe2.tbl',
                     '../../tests-nmr/mock-data-remediation/5oay/5oay.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = XplorMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/5oay/cluster_noe2.tbl',
                 '../../tests-nmr/mock-data-remediation/5oay/5oay.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6uz4/AGL55_K2_NOE.tbl',
                     '../../tests-nmr/mock-data-remediation/6uz4/6uz4.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7t1o/noe.tbl-corrected',
                     '../../tests-nmr/mock-data-remediation/7t1o/7t1o.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2ll4/2ll4-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2ll4/2ll4.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/5j2w/TARpRAM_pf1.txt-corrected',
                     '../../tests-nmr/mock-data-remediation/5j2w/5j2w.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = XplorMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2rsy/2rsy-corrected-div_dst-div_dst.mr',
                     '../../tests-nmr/mock-data-remediation/2rsy/2rsy.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = XplorMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2mpg/2mpg-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2mpg/2mpg.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = XplorMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2mpg/2mpg-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2mpg/2mpg.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2kxa/2kxa-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2kxa/2kxa.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = XplorMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7t03/HB1_noe.tbl',
                     '../../tests-nmr/mock-data-remediation/7t03/7t03.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = XplorMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2lzs/2lzs-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2lzs/2lzs.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2m3t/test.mr',
                     '../../tests-nmr/mock-data-remediation/2m3t/2m3t.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/5j0m/TARpRAM_pf1.txt-corrected',
                     '../../tests-nmr/mock-data-remediation/5j0m/5j0m.cif')

    reader = XplorMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2n1e/2n1e-corrected-div_src.mr',
                     '../../tests-nmr/mock-data-remediation/2n1e/2n1e.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = XplorMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2n1e/2n1e-corrected-div_src.mr',
                 '../../tests-nmr/mock-data-remediation/2n1e/2n1e.cif')

    reader = XplorMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/5w3n/fus_CC_PITHIRDSCT.tbl',
                     '../../tests-nmr/mock-data-remediation/5w3n/5w3n.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = XplorMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/5w3n/fus_CC_PITHIRDSCT.tbl',
                 '../../tests-nmr/mock-data-remediation/5w3n/5w3n.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2mnh/2mnh-trimmed-div_src.mr',
                 '../../tests-nmr/mock-data-remediation/2mnh/2mnh.cif')

    reader = XplorMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7m3u/PDP-24_restraints.tbl',
                     '../../tests-nmr/mock-data-remediation/7m3u/7m3u.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2n7j/2n7j-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2n7j/2n7j.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2n05/2n05-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2n05/2n05.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/5ggm/dis.txt',
                 '../../tests-nmr/mock-data-remediation/5ggm/5ggm.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/5y95/5y95-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/5y95/5y95.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lai/2lai-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2lai/2lai.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2ruj/test.mr',
                 '../../tests-nmr/mock-data-remediation/2ruj/2ruj.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2mus/2mus-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2mus/2mus.cif')
    reader = XplorMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2mus/2mus-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2mus/2mus.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6qeu/disu.tbl',
                 '../../tests-nmr/mock-data-remediation/6qeu/6qeu.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/5kmz/TPK_restraints.txt',
                 '../../tests-nmr/mock-data-remediation/5kmz/5kmz.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6bvy/test.mr',
                 '../../tests-nmr/mock-data-remediation/6bvy/6bvy.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lck/2lck-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2lck/2lck.cif')

    reader = XplorMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2n1a/2n1a-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2n1a/2n1a.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = XplorMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2n1a/2n1a-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2n1a/2n1a.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2mjf/2mjf-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2mjf/2mjf.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2muk/2muk-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2muk/2muk.cif')

    reader = XplorMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2kny/2kny-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2kny/2kny.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = XplorMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2kny/2kny-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2kny/2kny.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2ltj/2ltj-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2ltj/2ltj.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2n24/2n24-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2n24/2n24.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6feg/03_NOEs_unambig.tbl',
                     '../../tests-nmr/mock-data-remediation/6feg/6feg.cif')
    reader = XplorMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6feg/03_NOEs_unambig.tbl',
                 '../../tests-nmr/mock-data-remediation/6feg/6feg.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6feg/01_Dihedral_XPLOR.tbl-corrected',
                     '../../tests-nmr/mock-data-remediation/6feg/6feg.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6feg/02_RDCs_XPLOR.tbl-corrected',
                     '../../tests-nmr/mock-data-remediation/6feg/6feg.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2mqi/2mqi-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2mqi/2mqi.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/7ui5/jna_coup_dimer_2.tbl-corrected',
                 '../../tests-nmr/mock-data-remediation/7ui5/7ui5.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2ml9/2ml9-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2ml9/2ml9.cif')

    reader = XplorMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/3zfj/3zfj-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/3zfj/3zfj.cif')
    reader = XplorMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/3zfj/3zfj-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/3zfj/3zfj.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2b87/2b87-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2b87/2b87.cif')
    reader = XplorMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2b87/2b87-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2b87/2b87.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2mj5/2mj5-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2mj5/2mj5.cif')
    reader = XplorMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2mj5/2mj5-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2mj5/2mj5.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/5jyv/DN-HN_ThCikA_gel_complex_complete.tbl',
                     '../../tests-nmr/mock-data-remediation/5jyv/5jyv.cif')
    reader = XplorMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/5jyv/DN-HN_ThCikA_gel_complex_complete.tbl',
                 '../../tests-nmr/mock-data-remediation/5jyv/5jyv.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/5jyv/c13noe-square_cika.tbl',
                     '../../tests-nmr/mock-data-remediation/5jyv/5jyv.cif')
    reader = XplorMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/5jyv/c13noe-square_cika.tbl',
                 '../../tests-nmr/mock-data-remediation/5jyv/5jyv.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-combine-at-upload/bmr21102/sms21102/AmBErg_CC_restraints_PAR12p6ms.tbl',
                 '../../tests-nmr/mock-data-combine-at-upload/bmr21102/sms21102/sms21102.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-combine-at-upload/bmr21100/sms21100/Ambig.tbl',
                 '../../tests-nmr/mock-data-combine-at-upload/bmr21100/sms21100/sms21100.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-daother-8580/newupload_2/D_1000274286_mr_P3.xplor-nih.V1',
                     '../../tests-nmr/mock-data-daother-8580/newupload_2/D_1000274286_model_P1.cif.V1')
    reader = XplorMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-daother-8580/newupload_2/D_1000274286_mr_P3.xplor-nih.V1',
                 '../../tests-nmr/mock-data-daother-8580/newupload_2/D_1000274286_model_P1.cif.V1')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2mjb/2mjb-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2mjb/2mjb.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2l94/2l94-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2l94/2l94.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/5t1o/PCS_HN_EIN.tbl-corrected',
                 '../../tests-nmr/mock-data-remediation/5t1o/5t1o.cif')

    reader = XplorMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2n8l/2n8l-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2n8l/2n8l.cif')
    reader = XplorMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2n8l/2n8l-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2n8l/2n8l.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6th8/allnoe.tbl-corrected',
                 '../../tests-nmr/mock-data-remediation/6th8/6th8.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2mjk/2mjk-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2mjk/2mjk.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6cch/6cch-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/6cch/6cch.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lrk/2lrk-corrected-div_src.mr',
                 '../../tests-nmr/mock-data-remediation/2lrk/2lrk.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2mk3/2mk3-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2mk3/2mk3.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/5xbo/Tb_UBA1_PCS_correct_50p.tbl-corrected',
                 '../../tests-nmr/mock-data-remediation/5xbo/5xbo.cif')

    reader = XplorMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2k31/2k31-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2k31/2k31.cif')

    reader = XplorMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2k31/2k31-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2k31/2k31.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lrk/2lrk-corrected-div_src.mr',
                 '../../tests-nmr/mock-data-remediation/2lrk/2lrk.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/1iio/1iio-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/1iio/1iio.cif')
    reader = XplorMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/1iio/1iio-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/1iio/1iio.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2m3g/2m3g-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2m3g/2m3g.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/7n7e/distance.xplor',
                 '../../tests-nmr/mock-data-remediation/7n7e/7n7e.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2ju5/2ju5-corrected-div_src.mr',
                     '../../tests-nmr/mock-data-remediation/2ju5/2ju5.cif')
    reader = XplorMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2ju5/2ju5-corrected-div_src.mr',
                 '../../tests-nmr/mock-data-remediation/2ju5/2ju5.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6x63/deposit_All_Unamb_MD_xplorFormat_fixNomen.txt',
                 '../../tests-nmr/mock-data-remediation/6x63/6x63.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2laj/2laj-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2laj/2laj.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/5kqj/ANT2_hbond_restraint.tbl',
                 '../../tests-nmr/mock-data-remediation/5kqj/5kqj.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2l1v/2l1v-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2l1v/2l1v.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2mcc/2mcc-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2mcc/2mcc.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6d53/dangleT.tbl-corrected',
                 '../../tests-nmr/mock-data-remediation/6d53/6d53.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2k2a/2k2a-corrected-div_src.mr',
                 '../../tests-nmr/mock-data-remediation/2k2a/2k2a.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/5w3n/fus_CC_RDC.tbl-corrected',
                 '../../tests-nmr/mock-data-remediation/5w3n/5w3n.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/5w3n/fus_CO_RDC.tbl-corrected',
                 '../../tests-nmr/mock-data-remediation/5w3n/5w3n.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6var/HBVe_sPRE.tab-corrected',
                 '../../tests-nmr/mock-data-remediation/6var/6var.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6l92/G4II_planarity.txt',
                 '../../tests-nmr/mock-data-remediation/6l92/6l92.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/5t1o/RDC_NPr.tbl-corrected',
                 '../../tests-nmr/mock-data-remediation/5t1o/5t1o.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6ud0/pcs_hn_dist_tm_tsg_tsap.tbl-corrected',
                 '../../tests-nmr/mock-data-remediation/6ud0/6ud0.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2l3b/cacb_shift.mr',
                 '../../tests-nmr/mock-data-remediation/2l3b/2l3b.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2kw8/2kw8-trimmed-div_dst-div_src.mr',
                 '../../tests-nmr/mock-data-remediation/2kw8/2kw8.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2bjc/test_no_eff.mr',
                 '../../tests-nmr/mock-data-remediation/2bjc/2bjc.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2bgo/2bgo-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2bgo/2bgo.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/5ks5/vean.test',
                 '../../tests-nmr/mock-data-remediation/5ks5/5ks5.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2bjc/test.mr',
                 '../../tests-nmr/mock-data-remediation/2bjc/2bjc.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/4by9/4by9-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/4by9/4by9.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-daother-7871/wsh2090_ambig_rev.tbl',
                 '../../tests-nmr/mock-data-daother-7871/D_800473_model_P1.cif.V3')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2n55/test.mr',
                 '../../tests-nmr/mock-data-remediation/2n55/2n55.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2m54/2m54-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2m54/2m54.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2n21/2n21-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2n21/2n21.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6p6c/pea-15erk2c13shifts_ded.tbl',
                 '../../tests-nmr/mock-data-remediation/6p6c/6p6c.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6jcd/submit-plane.tbl',
                 '../../tests-nmr/mock-data-remediation/6jcd/6jcd.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-daother-7690/D_1300020446_mr-upload_P5.xplor-nih.V1',
                 '../../tests-nmr/mock-data-daother-7690/D_1300020446_model-release_P1.cif.V2')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-daother-7690/D_1300020646_mr-upload_P1.xplor-nih.V2',
                 '../../tests-nmr/mock-data-daother-7690/D_1300020646_model-annotate_P1.cif.V2')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-pdbstat/D_1000243168_mr-upload_P8.xplor-nih.V1',
                 '../../tests-nmr/mock-data-pdbstat/6pvr.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-pdbstat/D_1000243168_mr-upload_P2.xplor-nih.V1',
                 '../../tests-nmr/mock-data-pdbstat/6pvr.cif')

    reader = XplorMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-pdbstat/atom_sel_expr_example.txt',
                 '../../tests-nmr/mock-data-pdbstat/6pvr.cif')
