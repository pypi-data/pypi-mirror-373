##
# CnsMRReader.py
#
# Update:
##
""" A collection of classes for parsing CNS MR files.
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
    from wwpdb.utils.nmr.mr.CnsMRLexer import CnsMRLexer
    from wwpdb.utils.nmr.mr.CnsMRParser import CnsMRParser
    from wwpdb.utils.nmr.mr.CnsMRParserListener import CnsMRParserListener
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
    from nmr.mr.CnsMRLexer import CnsMRLexer
    from nmr.mr.CnsMRParser import CnsMRParser
    from nmr.mr.CnsMRParserListener import CnsMRParserListener
    from nmr.mr.ParserListenerUtil import (coordAssemblyChecker,
                                           retrieveOriginalFileName,
                                           MAX_ERROR_REPORT,
                                           REPRESENTATIVE_MODEL_ID,
                                           REPRESENTATIVE_ALT_ID)
    from nmr.io.CifReader import CifReader
    from nmr.ChemCompUtil import ChemCompUtil
    from nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from nmr.nef.NEFTranslator import NEFTranslator


class CnsMRReader:
    """ Accessor methods for parsing CNS MR files.
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
              ) -> Tuple[Optional[CnsMRParserListener], Optional[ParserErrorListener], Optional[LexerErrorListener]]:
        """ Parse CNS MR file.
            @return: CnsMRParserListener for success or None otherwise, ParserErrorListener, LexerErrorListener.
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

            lexer = CnsMRLexer(input)
            lexer.removeErrorListeners()

            lexer_error_listener = LexerErrorListener(mrFilePath, maxErrorReport=self.__maxLexerErrorReport)
            lexer.addErrorListener(lexer_error_listener)

            messageList = lexer_error_listener.getMessageList()

            if messageList is not None and self.__verbose:
                for description in messageList:
                    self.__lfh.write(f"[Syntax error] line {description['line_number']}:{description['column_position']} {description['message']}\n")
                    if 'input' in description:
                        self.__lfh.write(f"{description['input']}\n")
                        self.__lfh.write(f"{description['marker']}\n")

            stream = CommonTokenStream(lexer)
            parser = CnsMRParser(stream)
            if not isFilePath or self.__sll_pred:
                parser._interp.predictionMode = PredictionMode.SLL  # pylint: disable=protected-access
            parser.removeErrorListeners()
            parser_error_listener = ParserErrorListener(mrFilePath, maxErrorReport=self.__maxParserErrorReport)
            parser.addErrorListener(parser_error_listener)
            tree = parser.cns_mr()

            walker = ParseTreeWalker()
            listener = CnsMRParserListener(self.__verbose, self.__lfh,
                                           self.__representativeModelId,
                                           self.__representativeAltId,
                                           self.__mrAtomNameMapping,
                                           self.__cR, self.__caC,
                                           self.__ccU, self.__csStat, self.__nefT,
                                           self.__reasons)
            listener.setDebugMode(self.__debug)
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
    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/8voi/bmr31139/work/data/D_1000280655_mr-upload_P1.cns.V2',
                     '../../tests-nmr/mock-data-remediation/8voi/8voi.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7n7d/distance.xplor-corrected',
                     '../../tests-nmr/mock-data-remediation/7n7d/7n7d.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7jk8/DistanceRe.tbl-corrected',
                     '../../tests-nmr/mock-data-remediation/7jk8/7jk8.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6uyi/noe-Tenary_110119forP.tbl',
                     '../../tests-nmr/mock-data-remediation/6uyi/6uyi.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6uyi/noe-Tenary_110119forP.tbl',
                 '../../tests-nmr/mock-data-remediation/6uyi/6uyi.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6qtf/bmr34363/work/data/D_1292100432_nmr-peaks-upload_P1.dat.V1',
                     '../../tests-nmr/mock-data-remediation/6qtf/6qtf.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6o22/D_1000239495_mr_P1.cns.V1-corrected',
                     '../../tests-nmr/mock-data-remediation/6o22/6o22.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6nk9/AcaTx1_distance-constraints.tbl',
                     '../../tests-nmr/mock-data-remediation/6nk9/6nk9.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6nk9/AcaTx1_distance-constraints.tbl',
                 '../../tests-nmr/mock-data-remediation/6nk9/6nk9.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6mv3/D_1000236393_mr_P1.cns.V1',
                     '../../tests-nmr/mock-data-remediation/6mv3/6mv3.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6mv3/D_1000236393_mr_P1.cns.V1',
                 '../../tests-nmr/mock-data-remediation/6mv3/6mv3.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6ijv/N1_QC_mr.str-corrected',
                     '../../tests-nmr/mock-data-remediation/6ijv/6ijv.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6ijv/N1_QC_mr.str-corrected',
                 '../../tests-nmr/mock-data-remediation/6ijv/6ijv.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6ge1/noe_nonex_int.tbl',
                     '../../tests-nmr/mock-data-remediation/6ge1/6ge1.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6ge1/noe_nonex_int.tbl',
                 '../../tests-nmr/mock-data-remediation/6ge1/6ge1.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6e5n/NOEs.tbl',
                     '../../tests-nmr/mock-data-remediation/6e5n/6e5n.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6e5n/NOEs.tbl',
                 '../../tests-nmr/mock-data-remediation/6e5n/6e5n.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6ccx/NKC_run17_unambig.tbl-corrected',
                     '../../tests-nmr/mock-data-remediation/6ccx/6ccx.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6c00/cdif1restraints',
                     '../../tests-nmr/mock-data-remediation/6c00/6c00.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/5zld/N1_NEW.mr-corrected',
                     '../../tests-nmr/mock-data-remediation/5zld/5zld.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/5xs1/5xs1-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/5xs1/5xs1.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/5xs1/5xs1-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/5xs1/5xs1.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2yhh/2yhh-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2yhh/2yhh.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2m98/2m98-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2m98/2m98.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2krf/2krf-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2krf/2krf.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2n9b/2n9b-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2n9b/2n9b.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2n9b/2n9b-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2n9b/2n9b.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2n4r/2n4r-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2n4r/2n4r.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2n3a/2n3a-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2n3a/2n3a.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2n3a/2n3a-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2n3a/2n3a.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2n0s/2n0s-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2n0s/2n0s.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2n0s/2n0s-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2n0s/2n0s.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2l01/2l01-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2l01/2l01.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2l01/2l01-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2l01/2l01.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2mzx/2mzx-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2mzx/2mzx.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2mzx/2mzx-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2mzx/2mzx.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2mws/2mws-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2mws/2mws.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2miy/2miy-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2miy/2miy.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2mf6/2mf6-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2mf6/2mf6.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2mf6/2mf6-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2mf6/2mf6.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2mco/2mco-corrected-div_src.mr',
                     '../../tests-nmr/mock-data-remediation/2mco/2mco.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2mco/2mco-corrected-div_src.mr',
                 '../../tests-nmr/mock-data-remediation/2mco/2mco.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2ld5/2ld5-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2ld5/2ld5.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2mps/2mps-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2mps/2mps.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2m3o/2m3o-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2m3o/2m3o.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2m3o/2m3o-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2m3o/2m3o.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2mg5/2mg5-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2mg5/2mg5.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2mg5/2mg5-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2mg5/2mg5.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2m3o/2m3o-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2m3o/2m3o.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2m3o/2m3o-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2m3o/2m3o.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2m0k/2m0k-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2m0k/2m0k.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2lb9/2lb9-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2lb9/2lb9.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lb9/2lb9-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2lb9/2lb9.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2lzv/2lzv-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2lzv/2lzv.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/4asw/4asw-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/4asw/4asw.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2lxs/2lxs-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2lxs/2lxs.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lxs/2lxs-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2lxs/2lxs.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2lxp/2lxp-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2lxp/2lxp.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2lw3/2lw3-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2lw3/2lw3.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lw3/2lw3-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2lw3/2lw3.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7fba/7fba-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/7fba/7fba.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2mcj/2mcj-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2mcj/2mcj.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2lr1/2lr1-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2lr1/2lr1.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2lqc/2lqc-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2lqc/2lqc.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lqc/2lqc-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2lqc/2lqc.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2lns/2lns-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2lns/2lns.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2lml/2lml-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2lml/2lml.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2lm9/2lm9-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2lm9/2lm9.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lm9/2lm9-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2lm9/2lm9.cif')

    reasons_ = {'segment_id_mismatch': {'G2': 'A', 'GDP': 'A'},
                'segment_id_match_stats': {'G2': {'A': 5122}, 'GDP': {'A': -146}},
                'segment_id_poly_type_stats': {'G2': {'polymer': 5101, 'non-poly': 40, 'non-polymer': 0}, 'GDP': {'polymer': 11, 'non-poly': 0, 'non-polymer': 0}},
                'np_seq_id_remap': [{'chain_id': 'A', 'seq_id_dict': {1: 179}}],
                'non_poly_remap': {'GDP': {179: {'chain_id': 'A', 'seq_id': 179, 'original_chain_id': 'A'}}}}
    reader = CnsMRReader(True, reasons=reasons_)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lkd/2lkd-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2lkd/2lkd.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2lif/2lif-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2lif/2lif.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2lgm/2lgm-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2lgm/2lgm.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2lba/2lba-trimmed-div_dst.mr',
                     '../../tests-nmr/mock-data-remediation/2lba/2lba.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2l12/2l12-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2l12/2l12.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2l12/2l12-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2l12/2l12.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2knh/2knh-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2knh/2knh.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2knh/2knh-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2knh/2knh.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2js1/2js1-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2js1/2js1.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2js1/2js1-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2js1/2js1.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2mbz/2mbz-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2mbz/2mbz.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6tf4/vcrfah_ctd.restraints-corrected',
                     '../../tests-nmr/mock-data-remediation/6tf4/6tf4.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6tf4/vcrfah_ctd.restraints-corrected',
                 '../../tests-nmr/mock-data-remediation/6tf4/6tf4.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2mbv/2mbv-corrected-div_dst.mr',
                     '../../tests-nmr/mock-data-remediation/2mbv/2mbv.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2mbv/2mbv-corrected-div_dst.mr',
                 '../../tests-nmr/mock-data-remediation/2mbv/2mbv.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2ld3/2ld3-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2ld3/2ld3.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2ld3/2ld3-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2ld3/2ld3.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2jw1/2jw1-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2jw1/2jw1.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2jw1/2jw1-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2jw1/2jw1.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2joa/2joa-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2joa/2joa.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2joa/2joa-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2joa/2joa.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2ymj/2ymj-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2ymj/2ymj.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2ymj/2ymj-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2ymj/2ymj.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/1qkg/1qkg-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/1qkg/1qkg.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/1qkg/1qkg-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/1qkg/1qkg.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7d3v/A3A2plus2_noe_all.tbl',
                     '../../tests-nmr/mock-data-remediation/7d3v/7d3v.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/7d3v/A3A2plus2_noe_all.tbl',
                 '../../tests-nmr/mock-data-remediation/7d3v/7d3v.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2ljb/2ljb-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2ljb/2ljb.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2ljb/2ljb-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2ljb/2ljb.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2lkm/2lkm-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2lkm/2lkm.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lkm/2lkm-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2lkm/2lkm.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6f0y/noe_all.tbl',
                     '../../tests-nmr/mock-data-remediation/6f0y/6f0y.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6f0y/noe_all.tbl',
                 '../../tests-nmr/mock-data-remediation/6f0y/6f0y.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2mly/2mly-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2mly/2mly.cif')
    print(reader_listener.getReasonsForReparsing())

    reasons_ = {'global_sequence_offset': {'B': -115},
                'global_auth_sequence_offset': {'B': -115},
                'seq_id_remap': [{'chain_id': 'A', 'seq_id_dict': {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10,
                                                                   11: 11, 12: 12, 13: 13, 14: 14, 15: 15, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20,
                                                                   21: 21, 22: 22, 23: 23, 24: 24, 25: 25, 26: 26, 27: 310, 28: 311, 29: 312, 30: 313,
                                                                   31: 314, 32: 315, 33: 326, 34: 327, 35: 328, 36: 329, 37: 330, 38: 331, 39: 332, 40: 333,
                                                                   41: 334, 42: 335, 43: 336, 44: 337, 45: 338, 46: 339, 47: 340, 48: 341, 49: 342, 50: 343,
                                                                   51: 344, 52: 345, 53: 346, 54: 347, 55: 348, 56: 349, 57: 350, 58: 351, 59: 352, 60: 353,
                                                                   61: 354, 62: 355, 63: 356, 64: 357, 65: 358, 66: 359, 67: 360, 68: 361, 69: 362, 70: 363,
                                                                   71: 364, 72: 365, 73: 366, 74: 367, 75: 368, 76: 369, 77: 370, 78: 371, 79: 372, 80: 373,
                                                                   81: 392, 82: 393, 83: 502, 84: 503, 85: 504, 86: 505, 87: 506, 88: 507, 89: 508, 90: 509,
                                                                   91: 510, 92: 511, 93: 512, 94: 513, 95: 514, 96: 515, 97: 516, 98: 517, 99: 518, 100: 519,
                                                                   101: 520, 102: 521, 103: 522, 104: 523, 105: 524, 106: 525, 107: 526, 108: 527, 109: 528, 110: 529,
                                                                   111: 530, 112: 531, 113: 532, 114: 548, 115: 549}}]}
    reader = CnsMRReader(True, reasons=reasons_)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6feh/03_CAL_RDCs_XPLOR_281217.tbl-corrected',
                 '../../tests-nmr/mock-data-remediation/6feh/6feh.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/5z4f/txn38_complex_noe.tbl',
                     '../../tests-nmr/mock-data-remediation/5z4f/5z4f.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2ruk/2ruk-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2ruk/2ruk.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2ruk/2ruk-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2ruk/2ruk.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2mtk/2mtk-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2mtk/2mtk.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2mtk/2mtk-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2mtk/2mtk.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6fe6/noe_all.tbl',
                     '../../tests-nmr/mock-data-remediation/6fe6/6fe6.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2ma9/2ma9-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2ma9/2ma9.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2n7l/2n7l-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2n7l/2n7l.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2n7l/2n7l-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2n7l/2n7l.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2ky8/2ky8-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2ky8/2ky8.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/8bxj/D_1292127161_mr_P1.cns.V1',
                     '../../tests-nmr/mock-data-remediation/8bxj/8bxj.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6kg9/ca.tbl',
                     '../../tests-nmr/mock-data-remediation/6kg9/6kg9.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6kg9/ca.tbl',
                 '../../tests-nmr/mock-data-remediation/6kg9/6kg9.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6w4e/KRASGTPdimer_restraints.tbl-corrected',
                     '../../tests-nmr/mock-data-remediation/6w4e/6w4e.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6mxq/TL1_Dihedral_Restraints.tbl-corrected',
                 '../../tests-nmr/mock-data-remediation/6mxq/6mxq.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6l8v/D_1300013940_mr_P2.xplor-nih.V3-corrected',
                     '../../tests-nmr/mock-data-remediation/6l8v/6l8v.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6l8v/D_1300013940_mr_P2.xplor-nih.V3-corrected',
                 '../../tests-nmr/mock-data-remediation/6l8v/6l8v.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2jnh/2jnh-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2jnh/2jnh.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/5mnw/cns_run30.tbl',
                     '../../tests-nmr/mock-data-remediation/5mnw/5mnw.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/5mnw/cns_run30.tbl',
                 '../../tests-nmr/mock-data-remediation/5mnw/5mnw.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2l5e/2l5e-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2l5e/2l5e.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2rqz/2rqz-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2rqz/2rqz.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2kyi/2kyi-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2kyi/2kyi.cif')
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2kyi/2kyi-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2kyi/2kyi.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2jpi/2jpi-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2jpi/2jpi.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/7lgi/7lgi-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/7lgi/7lgi.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2nbj/2nbj-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2nbj/2nbj.cif')
    print(reader_listener.getReasonsForReparsing())

    reasons_ = {'global_auth_sequence_offset': {'A': 21}}
    reader = CnsMRReader(True, reasons=reasons_)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lpe/2lpe-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2lpe/2lpe.cif')

    reasons_ = {'global_sequence_offset': {'A': 1}, 'global_auth_sequence_offset': {'A': 153}}
    reader = CnsMRReader(True, reasons=reasons_)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2k31/2k31-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2k31/2k31.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/5twi/5twi-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/5twi/5twi.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2mo5/2mo5-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2mo5/2mo5.cif')

    reasons_ = {'segment_id_mismatch': {'PHD': 'A', 'H3K': 'B'},
                'segment_id_match_stats': {'PHD': {'A': 1425}, 'H3K': {'A': -1424, 'B': 32}},
                'segment_id_poly_type_stats': {'PHD': {'polymer': 1457, 'non-poly': 0, 'non-polymer': 0}, 'H3K': {'polymer': 0, 'non-poly': 0, 'non-polymer': 0}},
                'non_poly_remap': {'ZN': {401: {'chain_id': 'A', 'seq_id': 361, 'original_chain_id': 'A'},
                                          402: {'chain_id': 'A', 'seq_id': 362, 'original_chain_id': 'A'}}},
                'seq_id_remap': [{'chain_id': 'A', 'seq_id_dict': {1: 306, 2: 307, 3: 308, 4: 309, 5: 310, 6: 311, 7: 312, 8: 313, 9: 314, 10: 315,
                                                                   11: 316, 12: 317, 13: 318, 14: 319, 15: 320, 16: 321, 17: 322, 18: 323, 19: 324, 20: 325,
                                                                   21: 326, 22: 327, 23: 328, 24: 329, 25: 330, 26: 331, 27: 332, 28: 333, 29: 334, 30: 335,
                                                                   31: 336, 32: 337, 33: 338, 34: 339, 35: 340, 36: 341, 37: 342, 38: 343, 39: 344, 40: 345,
                                                                   41: 346, 42: 347, 43: 348, 44: 349, 45: 350, 46: 351, 47: 352, 48: 353, 49: 354, 50: 355,
                                                                   51: 356, 52: 357, 53: 358, 54: 359, 55: 360}},
                                 {'chain_id': 'B', 'seq_id_dict': {1: 363, 2: 364, 3: 365, 4: 366, 5: 367, 6: 368, 7: 369, 8: 370, 9: 371, 10: 372}}]}
    reader = CnsMRReader(True, reasons=reasons_)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2mnz/2mnz-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2mnz/2mnz.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/4apd/4apd-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/4apd/4apd.cif')
    print(reader_listener.getReasonsForReparsing())

    mrAtomNameMapping_ = [{'auth_atom_id': 'HC1', 'auth_comp_id': 'MEA', 'auth_seq_id': 3, 'original_atom_id': 'HI1', 'original_comp_id': 'NHE', 'original_seq_id': 2},
                          {'auth_atom_id': 'HC2', 'auth_comp_id': 'MEA', 'auth_seq_id': 3, 'original_atom_id': 'HI2', 'original_comp_id': 'NHE', 'original_seq_id': 2},
                          {'auth_atom_id': 'HC3', 'auth_comp_id': 'MEA', 'auth_seq_id': 3, 'original_atom_id': 'HI3', 'original_comp_id': 'NHE', 'original_seq_id': 2},
                          {'auth_atom_id': 'HA', 'auth_comp_id': 'MEA', 'auth_seq_id': 3, 'original_atom_id': 'HA', 'original_comp_id': 'NHE', 'original_seq_id': 2},
                          {'auth_atom_id': 'HB1', 'auth_comp_id': 'MEA', 'auth_seq_id': 3, 'original_atom_id': 'HB1', 'original_comp_id': 'NHE', 'original_seq_id': 2},
                          {'auth_atom_id': 'HB2', 'auth_comp_id': 'MEA', 'auth_seq_id': 3, 'original_atom_id': 'HB2', 'original_comp_id': 'NHE', 'original_seq_id': 2},
                          {'auth_atom_id': 'HD1', 'auth_comp_id': 'MEA', 'auth_seq_id': 3, 'original_atom_id': 'HD1', 'original_comp_id': 'NHE', 'original_seq_id': 2},
                          {'auth_atom_id': 'HE1', 'auth_comp_id': 'MEA', 'auth_seq_id': 3, 'original_atom_id': 'HE1', 'original_comp_id': 'NHE', 'original_seq_id': 2},
                          {'auth_atom_id': 'HZ', 'auth_comp_id': 'MEA', 'auth_seq_id': 3, 'original_atom_id': 'HZ', 'original_comp_id': 'NHE', 'original_seq_id': 2},
                          {'auth_atom_id': 'HE2', 'auth_comp_id': 'MEA', 'auth_seq_id': 3, 'original_atom_id': 'HE2', 'original_comp_id': 'NHE', 'original_seq_id': 2},
                          {'auth_atom_id': 'HD2', 'auth_comp_id': 'MEA', 'auth_seq_id': 3, 'original_atom_id': 'HD2', 'original_comp_id': 'NHE', 'original_seq_id': 2},
                          {'auth_atom_id': 'H', 'auth_comp_id': 'ITZ', 'auth_seq_id': 7, 'original_atom_id': 'HN', 'original_comp_id': 'ITZ', 'original_seq_id': 6},
                          {'auth_atom_id': 'HA', 'auth_comp_id': 'ITZ', 'auth_seq_id': 7, 'original_atom_id': 'HA', 'original_comp_id': 'ITZ', 'original_seq_id': 6},
                          {'auth_atom_id': 'HB', 'auth_comp_id': 'ITZ', 'auth_seq_id': 7, 'original_atom_id': 'HB', 'original_comp_id': 'ITZ', 'original_seq_id': 6},
                          {'auth_atom_id': 'HG12', 'auth_comp_id': 'ITZ', 'auth_seq_id': 7, 'original_atom_id': 'HG12', 'original_comp_id': 'ITZ', 'original_seq_id': 6},
                          {'auth_atom_id': 'HG11', 'auth_comp_id': 'ITZ', 'auth_seq_id': 7, 'original_atom_id': 'HG11', 'original_comp_id': 'ITZ', 'original_seq_id': 6},
                          {'auth_atom_id': 'HG23', 'auth_comp_id': 'ITZ', 'auth_seq_id': 7, 'original_atom_id': 'HG23', 'original_comp_id': 'ITZ', 'original_seq_id': 6},
                          {'auth_atom_id': 'HG21', 'auth_comp_id': 'ITZ', 'auth_seq_id': 7, 'original_atom_id': 'HG21', 'original_comp_id': 'ITZ', 'original_seq_id': 6},
                          {'auth_atom_id': 'HG22', 'auth_comp_id': 'ITZ', 'auth_seq_id': 7, 'original_atom_id': 'HG22', 'original_comp_id': 'ITZ', 'original_seq_id': 6},
                          {'auth_atom_id': 'HD11', 'auth_comp_id': 'ITZ', 'auth_seq_id': 7, 'original_atom_id': 'HD11', 'original_comp_id': 'ITZ', 'original_seq_id': 6},
                          {'auth_atom_id': 'HD12', 'auth_comp_id': 'ITZ', 'auth_seq_id': 7, 'original_atom_id': 'HD12', 'original_comp_id': 'ITZ', 'original_seq_id': 6},
                          {'auth_atom_id': 'HD13', 'auth_comp_id': 'ITZ', 'auth_seq_id': 7, 'original_atom_id': 'HD13', 'original_comp_id': 'ITZ', 'original_seq_id': 6},
                          {'auth_atom_id': 'HQ', 'auth_comp_id': 'ITZ', 'auth_seq_id': 7, 'original_atom_id': 'HQ', 'original_comp_id': 'ITZ', 'original_seq_id': 6}]
    reader = CnsMRReader(True, mrAtomNameMapping=mrAtomNameMapping_)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7l98/NOEtable_compound10.tbl',
                     '../../tests-nmr/mock-data-remediation/7l98/7l98.cif')
    print(reader_listener.getReasonsForReparsing())

    mrAtomNameMapping_ = [{'auth_atom_id': 'H8', 'auth_comp_id': '4FU', 'auth_seq_id': 6, 'original_atom_id': 'HAM', 'original_comp_id': '4FU', 'original_seq_id': 6},
                          {'auth_atom_id': 'H9', 'auth_comp_id': '4FU', 'auth_seq_id': 6, 'original_atom_id': 'HAI', 'original_comp_id': '4FU', 'original_seq_id': 6},
                          {'auth_atom_id': 'HAI', 'auth_comp_id': '4FU', 'auth_seq_id': 6, 'original_atom_id': 'HAJ', 'original_comp_id': '4FU', 'original_seq_id': 6},
                          {'auth_atom_id': 'H112', 'auth_comp_id': '4FU', 'auth_seq_id': 6, 'original_atom_id': 'HAE', 'original_comp_id': '4FU', 'original_seq_id': 6},
                          {'auth_atom_id': 'H111', 'auth_comp_id': '4FU', 'auth_seq_id': 6, 'original_atom_id': 'HAF', 'original_comp_id': '4FU', 'original_seq_id': 6},
                          {'auth_atom_id': 'HAG', 'auth_comp_id': '4FU', 'auth_seq_id': 6, 'original_atom_id': 'HAG', 'original_comp_id': '4FU', 'original_seq_id': 6},
                          {'auth_atom_id': 'H12', 'auth_comp_id': '4FU', 'auth_seq_id': 6, 'original_atom_id': 'HAH', 'original_comp_id': '4FU', 'original_seq_id': 6},
                          {'auth_atom_id': 'HAL', 'auth_comp_id': '4FU', 'auth_seq_id': 6, 'original_atom_id': 'HAL', 'original_comp_id': '4FU', 'original_seq_id': 6},
                          {'auth_atom_id': 'HAK', 'auth_comp_id': '4FU', 'auth_seq_id': 6, 'original_atom_id': 'HAK', 'original_comp_id': '4FU', 'original_seq_id': 6},
                          {'auth_atom_id': 'H14', 'auth_comp_id': '4FU', 'auth_seq_id': 6, 'original_atom_id': 'HAN', 'original_comp_id': '4FU', 'original_seq_id': 6},
                          {'auth_atom_id': 'HAC', 'auth_comp_id': '4G6', 'auth_seq_id': 24, 'original_atom_id': 'HAC', 'original_comp_id': '4G6', 'original_seq_id': 24},
                          {'auth_atom_id': 'HAB', 'auth_comp_id': '4G6', 'auth_seq_id': 24, 'original_atom_id': 'HAB', 'original_comp_id': '4G6', 'original_seq_id': 24},
                          {'auth_atom_id': 'HAA', 'auth_comp_id': '4G6', 'auth_seq_id': 24, 'original_atom_id': 'HAA', 'original_comp_id': '4G6', 'original_seq_id': 24},
                          {'auth_atom_id': 'HAF', 'auth_comp_id': '4G6', 'auth_seq_id': 24, 'original_atom_id': 'HAF', 'original_comp_id': '4G6', 'original_seq_id': 24},
                          {'auth_atom_id': 'HAD', 'auth_comp_id': '4G6', 'auth_seq_id': 24, 'original_atom_id': 'HAD', 'original_comp_id': '4G6', 'original_seq_id': 24},
                          {'auth_atom_id': 'HAE', 'auth_comp_id': '4G6', 'auth_seq_id': 24, 'original_atom_id': 'HAE', 'original_comp_id': '4G6', 'original_seq_id': 24},
                          {'auth_atom_id': 'HAL', 'auth_comp_id': '4G6', 'auth_seq_id': 24, 'original_atom_id': 'HAL', 'original_comp_id': '4G6', 'original_seq_id': 24},
                          {'auth_atom_id': 'HAH', 'auth_comp_id': '4G6', 'auth_seq_id': 24, 'original_atom_id': 'HAH', 'original_comp_id': '4G6', 'original_seq_id': 24},
                          {'auth_atom_id': 'HAG', 'auth_comp_id': '4G6', 'auth_seq_id': 24, 'original_atom_id': 'HAG', 'original_comp_id': '4G6', 'original_seq_id': 24},
                          {'auth_atom_id': 'H', 'auth_comp_id': '4G6', 'auth_seq_id': 24, 'original_atom_id': 'H', 'original_comp_id': '4G6', 'original_seq_id': 24},
                          {'auth_atom_id': 'H1', 'auth_comp_id': 'ACE', 'auth_seq_id': 30, 'original_atom_id': 'HA2', 'original_comp_id': 'ACE', 'original_seq_id': 30},
                          {'auth_atom_id': 'H2', 'auth_comp_id': 'ACE', 'auth_seq_id': 30, 'original_atom_id': 'HA3', 'original_comp_id': 'ACE', 'original_seq_id': 30},
                          {'auth_atom_id': 'H3', 'auth_comp_id': 'ACE', 'auth_seq_id': 30, 'original_atom_id': 'HA1', 'original_comp_id': 'ACE', 'original_seq_id': 30}]
    reader = CnsMRReader(True, mrAtomNameMapping=mrAtomNameMapping_)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2nbl/2nbl-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2nbl/2nbl.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7uv1/noe.tbl',
                     '../../tests-nmr/mock-data-remediation/7uv1/7uv1.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6d37/6d37-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/6d37/6d37.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-daother-9437/D_1000284098_mr_P2.cns.V3',
                     '../../tests-nmr/mock-data-daother-9437/D_800689_model_P1.cif.V3')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-daother-9063/4_mercaptophenol_a3c_NOE_restaints.txt.revised',
                     '../../tests-nmr/mock-data-daother-9063/D_800642_model_P1.cif.V15')
    print(reader_listener.getReasonsForReparsing())

    reasons_ = {'label_seq_scheme': {'dist': True}, 'label_seq_offset': {'A': 9}}
    reader = CnsMRReader(True, reasons=reasons_)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6mie/NOE.tbl-corrected',
                 '../../tests-nmr/mock-data-remediation/6mie/6mie.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7f7x/pUbrl-UBA-NOE.tab-corrected',
                     '../../tests-nmr/mock-data-remediation/7f7x/7f7x.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7f7x/f1f_cnoe.tab-corrected',
                     '../../tests-nmr/mock-data-remediation/7f7x/7f7x.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2n1o/2n1o-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2n1o/2n1o.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2lai/2lai-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2lai/2lai.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/5jyv/c13noe-square_cika.tbl-corrected',
                     '../../tests-nmr/mock-data-remediation/5jyv/5jyv.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/5jyv/c13noe-square_cika.tbl-corrected',
                 '../../tests-nmr/mock-data-remediation/5jyv/5jyv.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2rsy/2rsy-corrected-div_dst-div_dst.mr',
                     '../../tests-nmr/mock-data-remediation/2rsy/2rsy.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2mgs/2mgs-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2mgs/2mgs.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2maj/2maj-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2maj/2maj.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2m0m/2m0m-corrected-div_dst.mr',
                     '../../tests-nmr/mock-data-remediation/2m0m/2m0m.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2lxm/2lxm-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2lxm/2lxm.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2lhz/2lhz-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2lhz/2lhz.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2le9/2le9-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2le9/2le9.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2le9/2le9-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2le9/2le9.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2kid/2kid-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2kid/2kid.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2kid/2kid-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2kid/2kid.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2kyg/2kyg-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2kyg/2kyg.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2kyg/2kyg-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2kyg/2kyg.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6bho/CN-NOE_gaf6012g4lit.tbl-corrected',
                     '../../tests-nmr/mock-data-remediation/6bho/6bho.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6bho/CN-NOE_gaf6012g4lit.tbl-corrected',
                 '../../tests-nmr/mock-data-remediation/6bho/6bho.cif')

    reasons_ = {'segment_id_mismatch': {'B': 'A'},
                'segment_id_match_stats': {'B': {'A': -104}},
                'segment_id_poly_type_stats': {'B': {'polymer': 0, 'non-poly': 0, 'non-polymer': 0}},
                'np_seq_id_remap': [{'chain_id': 'A', 'seq_id_dict': {1: 201}}]}
    reader = CnsMRReader(True, reasons=reasons_)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6nbn/bmr30550/work/data/D_1000238162_mr-upload_P1.cns.V1',
                 '../../tests-nmr/mock-data-remediation/6nbn/6nbn.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2lck/2lck-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2lck/2lck.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2lla/2lla-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2lla/2lla.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lla/2lla-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2lla/2lla.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-daother-10105/D_1000295697_mr-upload_P1.cns.V1',
                     '../../tests-nmr/mock-data-daother-10105/D_1000295697_model_P1.cif.V6')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2lpe/2lpe-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2lpe/2lpe.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lpe/2lpe-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2lpe/2lpe.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2mj5/2mj5-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2mj5/2mj5.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2mj5/2mj5-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2mj5/2mj5.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2mnz/2mnz-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2mnz/2mnz.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2mnz/2mnz-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2mnz/2mnz.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2rt5/2rt5-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2rt5/2rt5.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2rt5/2rt5-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2rt5/2rt5.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2k3c/2k3c-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2k3c/2k3c.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2k3c/2k3c-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2k3c/2k3c.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6feg/03_NOEs_unambig.tbl',
                     '../../tests-nmr/mock-data-remediation/6feg/6feg.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6feg/03_NOEs_unambig.tbl',
                 '../../tests-nmr/mock-data-remediation/6feg/6feg.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6qeu/disu.tbl',
                     '../../tests-nmr/mock-data-remediation/6qeu/6qeu.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7nf9/Clamp_NOEs.tbl',
                     '../../tests-nmr/mock-data-remediation/7nf9/7nf9.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7zjy/unambig.tbl',
                     '../../tests-nmr/mock-data-remediation/7zjy/7zjy.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/7zjy/unambig.tbl',
                 '../../tests-nmr/mock-data-remediation/7zjy/7zjy.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7qgv/NMR_restraints_Update.tbl-corrected',
                     '../../tests-nmr/mock-data-remediation/7qgv/7qgv.cif')
    assert reader_listener.getReasonsForReparsing() is None

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-D_1300057999/sc-ec.tbl',
                     '../../tests-nmr/mock-data-D_1300057999/D_800813_model_P1.cif.V3')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-D_1300057999/sc-ec.tbl',
                 '../../tests-nmr/mock-data-D_1300057999/D_800813_model_P1.cif.V3')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/5kp0/cterm_ab_noe.tbl-corrected',
                     '../../tests-nmr/mock-data-remediation/5kp0/5kp0.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6xmn/6xmn-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/6xmn/6xmn.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6xmn/6xmn-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/6xmn/6xmn.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2k3c/2k3c-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2k3c/2k3c.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2k3c/2k3c-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2k3c/2k3c.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2rvb/2rvb-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2rvb/2rvb.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7qlf/noes.tbl',
                     '../../tests-nmr/mock-data-remediation/7qlf/7qlf.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2l8i/2l8i-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2l8i/2l8i.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7t1p/7t1p-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/7t1p/7t1p.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2nbl/2nbl-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2nbl/2nbl.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2mlx/2mlx-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2mlx/2mlx.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6ggz/unambig.tbl',
                     '../../tests-nmr/mock-data-remediation/6ggz/6ggz.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-daother-8751/2nd_case/D_1292132188_mr-upload_P1.cns.V1',
                     '../../tests-nmr/mock-data-daother-8751/2nd_case/D_800600_model_P1.cif.V3')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2kid/2kid-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2kid/2kid.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2kid/2kid-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2kid/2kid.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2n1o/2n1o-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2n1o/2n1o.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2n2w/2n2w-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2n2w/2n2w.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2n2w/2n2w-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2n2w/2n2w.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7cwh/Rack_noe_all.tbl',
                     '../../tests-nmr/mock-data-remediation/7cwh/7cwh.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2l11/2l11-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2l11/2l11.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2n3r/2n3r-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2n3r/2n3r.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2n3r/2n3r-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2n3r/2n3r.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2lfr/2lfr-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2lfr/2lfr.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lfr/2lfr-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2lfr/2lfr.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2n30/2n30-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2n30/2n30.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/5xv8/170307_UVSSA-TFIIHp62.tbl-corrected',
                     '../../tests-nmr/mock-data-remediation/5xv8/5xv8.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2lwn/2lwn-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2lwn/2lwn.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lwn/2lwn-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2lwn/2lwn.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6cc9/NOE_cmpd2_run30_ambig.tbl',
                     '../../tests-nmr/mock-data-remediation/6cc9/6cc9.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2lp4/2lp4-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2lp4/2lp4.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lp4/2lp4-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2lp4/2lp4.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2k7v/2k7v-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2k7v/2k7v.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2k7v/2k7v-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2k7v/2k7v.cif')
    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2ms7/2ms7-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2ms7/2ms7.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2lpe/2lpe-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2lpe/2lpe.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lpe/2lpe-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2lpe/2lpe.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2mrp/2mrp-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2mrp/2mrp.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2mrp/2mrp-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2mrp/2mrp.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6zbi/allNOEs.tbl',
                     '../../tests-nmr/mock-data-remediation/6zbi/6zbi.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6zbi/allNOEs.tbl',
                 '../../tests-nmr/mock-data-remediation/6zbi/6zbi.cif')

    reader = CnsMRReader(True, reasons={'global_auth_sequence_offset': {'B': 35}})
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7f7x/f1f_cnoe.tab-corrected',
                     '../../tests-nmr/mock-data-remediation/7f7x/7f7x.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7f7x/pUbrl-UBA-NOE.tab-corrected',
                     '../../tests-nmr/mock-data-remediation/7f7x/7f7x.cif')
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/7f7x/pUbrl-UBA-NOE.tab-corrected',
                 '../../tests-nmr/mock-data-remediation/7f7x/7f7x.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lbu/2lbu-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2lbu/2lbu.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2n4n/2n4n-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2n4n/2n4n.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2lwe/2lwe-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2lwe/2lwe.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6ttc/ambig.tbl',
                     '../../tests-nmr/mock-data-remediation/6ttc/6ttc.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/4cyk/4cyk-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/4cyk/4cyk.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6vl2/restraint_file-corrected',
                     '../../tests-nmr/mock-data-remediation/6vl2/6vl2.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2ljc/2ljc-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2ljc/2ljc.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2ljc/2ljc-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2ljc/2ljc.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/5y95/5y95-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/5y95/5y95.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7mqu/ambig.tbl',
                     '../../tests-nmr/mock-data-remediation/7mqu/7mqu.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2l5y/test.mr',
                     '../../tests-nmr/mock-data-remediation/2l5y/2l5y.cif')
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2l5y/test.mr',
                 '../../tests-nmr/mock-data-remediation/2l5y/2l5y.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lsz/2lsz-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2lsz/2lsz.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/7dvm/7dvm-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/7dvm/7dvm.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2k9e/2k9e-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2k9e/2k9e.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/8ht7/dihe_f.tbl-corrected',
                 '../../tests-nmr/mock-data-remediation/8ht7/8ht7.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2mgt/2mgt-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2mgt/2mgt.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2mgt/2mgt-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2mgt/2mgt.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/5kmz/5kmz-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/5kmz/5kmz.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/7yhh/all.tbl',
                 '../../tests-nmr/mock-data-remediation/7yhh/7yhh.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2mhm/2mhm-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2mhm/2mhm.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6pts/run6_unambig.tbl-corrected',
                 '../../tests-nmr/mock-data-remediation/6pts/6pts.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6feg/03_NOEs_ambig.tbl',
                     '../../tests-nmr/mock-data-remediation/6feg/6feg.cif')
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6feg/03_NOEs_ambig.tbl',
                 '../../tests-nmr/mock-data-remediation/6feg/6feg.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6gpi/distance_res.tbl-corrected',
                     '../../tests-nmr/mock-data-remediation/6gpi/6gpi.cif')
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6gpi/distance_res.tbl-corrected',
                 '../../tests-nmr/mock-data-remediation/6gpi/6gpi.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-daother-9063/4_mercaptophenol_a3c_NOE_restaints.txt',
                     '../../tests-nmr/mock-data-daother-9063/D_800642_model_P1.cif.V15')
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-daother-9063/4_mercaptophenol_a3c_NOE_restaints.txt',
                 '../../tests-nmr/mock-data-daother-9063/D_800642_model_P1.cif.V15')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2k4l/2k4l-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2k4l/2k4l.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2mlb/test.mr',
                 '../../tests-nmr/mock-data-remediation/2mlb/2mlb.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2ltq/2ltq-corrected-div_src.mr',
                 '../../tests-nmr/mock-data-remediation/2ltq/2ltq.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-combine-at-upload/bmr36473/data/D_1300028046_mr-upload_P2.cns.V1',
                 '../../tests-nmr/mock-data-combine-at-upload/bmr36473/data/D_1300028046_model-annotate_P1.cif.V2')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-daother-7969/dna2_used.tbl',
                 '../../tests-nmr/mock-data-daother-7969/D_800478_model_P1.cif.V3')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6ijw/D_1300008256_mr_P1.cyana.V1-corrected',
                 '../../tests-nmr/mock-data-remediation/6ijw/6ijw.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6uck/noe.tbl-corrected',
                 '../../tests-nmr/mock-data-remediation/6uck/6uck.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2m10/2m10-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2m10/2m10.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/1iio/1iio-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/1iio/1iio.cif')
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/1iio/1iio-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/1iio/1iio.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2jrl/2jrl-corrected-div_dst-div_src.mr',
                 '../../tests-nmr/mock-data-remediation/2jrl/2jrl.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2b87/2b87-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2b87/2b87.cif')
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2b87/2b87-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2b87/2b87.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lhz/2lhz-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2lhz/2lhz.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6th8/hbond_patches.tbl',
                 '../../tests-nmr/mock-data-remediation/6th8/6th8.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/4by9/4by9-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/4by9/4by9.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-daother-7690/D_1300022442_mr-upload_P1.cns.V1',
                 '../../tests-nmr/mock-data-daother-7690/D_1300022442_model-annotate_P1.cif.V1')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-daother-7690/D_1300019843_mr-upload_P1.cns.V1',
                 '../../tests-nmr/mock-data-daother-7690/D_1300019843_model-annotate_P1.cif.V1')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-pdbstat/D_1000243168_mr-upload_P8.xplor-nih.V1',
                 '../../tests-nmr/mock-data-pdbstat/6pvr.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-pdbstat/D_1000243168_mr-upload_P2.xplor-nih.V1',
                 '../../tests-nmr/mock-data-pdbstat/6pvr.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-pdbstat/atom_sel_expr_example.txt',
                 '../../tests-nmr/mock-data-pdbstat/6pvr.cif')
