##
# CyanaMRReader.py
#
# Update:
##
""" A collection of classes for parsing CYANA MR files.
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
    from wwpdb.utils.nmr.mr.CyanaMRLexer import CyanaMRLexer
    from wwpdb.utils.nmr.mr.CyanaMRParser import CyanaMRParser
    from wwpdb.utils.nmr.mr.CyanaMRParserListener import CyanaMRParserListener
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
    from nmr.mr.CyanaMRLexer import CyanaMRLexer
    from nmr.mr.CyanaMRParser import CyanaMRParser
    from nmr.mr.CyanaMRParserListener import CyanaMRParserListener
    from nmr.mr.ParserListenerUtil import (coordAssemblyChecker,
                                           retrieveOriginalFileName,
                                           MAX_ERROR_REPORT,
                                           REPRESENTATIVE_MODEL_ID,
                                           REPRESENTATIVE_ALT_ID)
    from nmr.io.CifReader import CifReader
    from nmr.ChemCompUtil import ChemCompUtil
    from nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from nmr.nef.NEFTranslator import NEFTranslator


class CyanaMRReader:
    """ Accessor methods for parsing CYANA MR files.
    """

    def __init__(self, verbose: bool = True, log: IO = sys.stdout,
                 representativeModelId: int = REPRESENTATIVE_MODEL_ID,
                 representativeAltId: str = REPRESENTATIVE_ALT_ID,
                 mrAtomNameMapping: Optional[List[dict]] = None,
                 cR: Optional[CifReader] = None, caC: Optional[dict] = None, ccU: Optional[ChemCompUtil] = None,
                 csStat: Optional[BMRBChemShiftStat] = None, nefT: Optional[NEFTranslator] = None,
                 reasons: Optional[dict] = None, upl_or_lol: Optional[str] = None, file_ext: Optional[str] = None):
        self.__class_name__ = self.__class__.__name__
        self.__version__ = __version__

        self.__verbose = verbose
        self.__lfh = log
        self.__debug = False
        self.__remediate = False
        self.__sll_pred = False

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

        self.__upl_or_lol = upl_or_lol

        self.__file_ext = file_ext

    def setDebugMode(self, debug: bool):
        self.__debug = debug

    def setRemediateMode(self, remediate: bool):
        self.__remediate = remediate

    def setLexerMaxErrorReport(self, maxErrReport: int):
        self.__maxLexerErrorReport = maxErrReport

    def setParserMaxErrorReport(self, maxErrReport: int):
        self.__maxParserErrorReport = maxErrReport

    def setSllPredMode(self, sll_pred: bool):
        self.__sll_pred = sll_pred

    def parse(self, mrFilePath: str, cifFilePath: Optional[str] = None, isFilePath: bool = True,
              createSfDict: bool = False, originalFileName: Optional[str] = None, listIdCounter: Optional[dict] = None, entryId: Optional[str] = None
              ) -> Tuple[Optional[CyanaMRParserListener], Optional[ParserErrorListener], Optional[LexerErrorListener]]:
        """ Parse CYANA MR file.
            @return: CyanaMRParserListener for success or None otherwise, ParserErrorListener, LexerErrorListener.
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

            lexer = CyanaMRLexer(input)
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
            parser = CyanaMRParser(stream)
            if not isFilePath or self.__sll_pred:
                parser._interp.predictionMode = PredictionMode.SLL  # pylint: disable=protected-access
            parser.removeErrorListeners()
            parser_error_listener = ParserErrorListener(mrFilePath, maxErrorReport=self.__maxParserErrorReport)
            parser.addErrorListener(parser_error_listener)
            tree = parser.cyana_mr()

            walker = ParseTreeWalker()
            listener = CyanaMRParserListener(self.__verbose, self.__lfh,
                                             self.__representativeModelId,
                                             self.__representativeAltId,
                                             self.__mrAtomNameMapping,
                                             self.__cR, self.__caC,
                                             self.__ccU, self.__csStat, self.__nefT,
                                             self.__reasons, self.__upl_or_lol, self.__file_ext)
            listener.setDebugMode(self.__debug)
            listener.setRemediateMode(self.__remediate)
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
    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2lum/2lum-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2lum/2lum.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CyanaMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2rsy/2rsy-corrected-div_dst-div_src.mr',
                     '../../tests-nmr/mock-data-remediation/2rsy/2rsy.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CyanaMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/8rhm/bmr34888/work/data/D_1292134954_mr-upload_P1.cyana.V3',
                     '../../tests-nmr/mock-data-remediation/8rhm/8rhm.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CyanaMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/8rhm/bmr34888/work/data/D_1292134954_mr-upload_P1.cyana.V3',
                 '../../tests-nmr/mock-data-remediation/8rhm/8rhm.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/8vrc/bmr31140/work/data/D_1000281082_mr-upload_P1.cyana.V3',
                     '../../tests-nmr/mock-data-remediation/8vrc/8vrc.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/9fsi/bmr34922/work/data/D_1292139585_mr-upload_P1.cyana.V2',
                     '../../tests-nmr/mock-data-remediation/9fsi/9fsi.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/9ceq/bmr31181/work/data/D_1000285213_mr-upload_P4.cyana.V1',
                     '../../tests-nmr/mock-data-remediation/9ceq/9ceq.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-daother-10230/D_1300048971_mr-upload_P2.cyana.V2',
                     '../../tests-nmr/mock-data-daother-10230/D_800848_model_P1.cif.V3')

    reasons_ = {'non_poly_remap': {'SAH': {76: {'chain_id': 'A', 'seq_id': 101, 'original_chain_id': None}}}}
    reader = CyanaMRReader(True, reasons=reasons_)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6hag/aroG.upl',
                     '../../tests-nmr/mock-data-remediation/6hag/6hag.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2mze/2mze-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2mze/2mze.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-D_1300055931/0306REST.txt',
                 '../../tests-nmr/mock-data-D_1300055931/D_800803_model_P1.cif.V6')

    __mrAtomNameMapping__ = [{'auth_atom_id': 'H4', 'auth_comp_id': 'NGH', 'auth_seq_id': 253, 'original_atom_id': 'HP3', 'original_comp_id': 'NGH', 'original_seq_id': 253},
                             {'auth_atom_id': 'H5', 'auth_comp_id': 'NGH', 'auth_seq_id': 253, 'original_atom_id': 'HP2', 'original_comp_id': 'NGH', 'original_seq_id': 253},
                             {'auth_atom_id': 'H1', 'auth_comp_id': 'NGH', 'auth_seq_id': 253, 'original_atom_id': 'HP6', 'original_comp_id': 'NGH', 'original_seq_id': 253},
                             {'auth_atom_id': 'H2', 'auth_comp_id': 'NGH', 'auth_seq_id': 253, 'original_atom_id': 'HP5', 'original_comp_id': 'NGH', 'original_seq_id': 253},
                             {'auth_atom_id': 'H12', 'auth_comp_id': 'NGH', 'auth_seq_id': 253, 'original_atom_id': 'HG', 'original_comp_id': 'NGH', 'original_seq_id': 253},
                             {'auth_atom_id': 'HN1', 'auth_comp_id': 'NGH', 'auth_seq_id': 253, 'original_atom_id': 'HNA', 'original_comp_id': 'NGH', 'original_seq_id': 253},
                             {'auth_atom_id': 'H71', 'auth_comp_id': 'NGH', 'auth_seq_id': 253, 'original_atom_id': 'HM3', 'original_comp_id': 'NGH', 'original_seq_id': 253},
                             {'auth_atom_id': 'H72', 'auth_comp_id': 'NGH', 'auth_seq_id': 253, 'original_atom_id': 'HM1', 'original_comp_id': 'NGH', 'original_seq_id': 253},
                             {'auth_atom_id': 'H73', 'auth_comp_id': 'NGH', 'auth_seq_id': 253, 'original_atom_id': 'HM2', 'original_comp_id': 'NGH', 'original_seq_id': 253},
                             {'auth_atom_id': 'H91', 'auth_comp_id': 'NGH', 'auth_seq_id': 253, 'original_atom_id': 'HB2', 'original_comp_id': 'NGH', 'original_seq_id': 253},
                             {'auth_atom_id': 'H92', 'auth_comp_id': 'NGH', 'auth_seq_id': 253, 'original_atom_id': 'HB3', 'original_comp_id': 'NGH', 'original_seq_id': 253},
                             {'auth_atom_id': 'H101', 'auth_comp_id': 'NGH', 'auth_seq_id': 253, 'original_atom_id': 'HA1', 'original_comp_id': 'NGH', 'original_seq_id': 253},
                             {'auth_atom_id': 'H102', 'auth_comp_id': 'NGH', 'auth_seq_id': 253, 'original_atom_id': 'HA2', 'original_comp_id': 'NGH', 'original_seq_id': 253},
                             {'auth_atom_id': 'H131', 'auth_comp_id': 'NGH', 'auth_seq_id': 253, 'original_atom_id': 'HD11', 'original_comp_id': 'NGH', 'original_seq_id': 253},
                             {'auth_atom_id': 'H132', 'auth_comp_id': 'NGH', 'auth_seq_id': 253, 'original_atom_id': 'HD12', 'original_comp_id': 'NGH', 'original_seq_id': 253},
                             {'auth_atom_id': 'H133', 'auth_comp_id': 'NGH', 'auth_seq_id': 253, 'original_atom_id': 'HD13', 'original_comp_id': 'NGH', 'original_seq_id': 253},
                             {'auth_atom_id': 'H141', 'auth_comp_id': 'NGH', 'auth_seq_id': 253, 'original_atom_id': 'HD21', 'original_comp_id': 'NGH', 'original_seq_id': 253},
                             {'auth_atom_id': 'H142', 'auth_comp_id': 'NGH', 'auth_seq_id': 253, 'original_atom_id': 'HD22', 'original_comp_id': 'NGH', 'original_seq_id': 253},
                             {'auth_atom_id': 'H143', 'auth_comp_id': 'NGH', 'auth_seq_id': 253, 'original_atom_id': 'HD23', 'original_comp_id': 'NGH', 'original_seq_id': 253}
                             ]
    reader = CyanaMRReader(True, mrAtomNameMapping=__mrAtomNameMapping__)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2jnp/test.mr',
                 '../../tests-nmr/mock-data-remediation/2jnp/2jnp.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2n3y/2n3y-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2n3y/2n3y.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2n06/2n06-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2n06/2n06.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CyanaMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2n06/2n06-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2n06/2n06.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2max/2max-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2max/2max.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CyanaMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2max/2max-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2max/2max.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7qde/7qde-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/7qde/7qde.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7nmb/cToxR_nOe_nur_upl_190221.upl',
                     '../../tests-nmr/mock-data-remediation/7nmb/7nmb.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-daother-8946/2nd/D_1000288502_mr-upload_P1.cyana.V1',
                     '../../tests-nmr/mock-data-daother-8946/2nd/D_800740_model_P1.cif.V3')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2mv8/2mv8-corrected.mr.1',
                     '../../tests-nmr/mock-data-remediation/2mv8/2mv8.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2mv8/2mv8-corrected.mr.2',
                     '../../tests-nmr/mock-data-remediation/2mv8/2mv8.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7zex/D_1292113916_mr_P2.cyana.V1',
                     '../../tests-nmr/mock-data-remediation/7zex/7zex.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7zew/protein_renumb.upl',
                     '../../tests-nmr/mock-data-remediation/7zew/7zew.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7zew/protein_renumb.aco',
                     '../../tests-nmr/mock-data-remediation/7zew/7zew.cif')

    reader = CyanaMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7dfe/TuSp2-RP-Cut.upl_2.txt',
                     '../../tests-nmr/mock-data-remediation/7dfe/7dfe.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CyanaMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/7dfe/TuSp2-RP-Cut.upl_2.txt',
                 '../../tests-nmr/mock-data-remediation/7dfe/7dfe.cif')

    reader = CyanaMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2rol/2rol-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2rol/2rol.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CyanaMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2rol/2rol-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2rol/2rol.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/5lfh/P29_upl.txt',
                     '../../tests-nmr/mock-data-remediation/5lfh/5lfh.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CyanaMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/5lfh/P29_upl.txt',
                 '../../tests-nmr/mock-data-remediation/5lfh/5lfh.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6zpr/final.upl',
                     '../../tests-nmr/mock-data-remediation/6zpr/6zpr.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2mhx/2mhx-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2mhx/2mhx.cif')

    reader = CyanaMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2mx9/2mx9-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2mx9/2mx9.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CyanaMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2mx9/2mx9-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2mx9/2mx9.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2bl6/2bl6-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2bl6/2bl6.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CyanaMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2bl6/2bl6-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2bl6/2bl6.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/5nip/DepositExpConstCC9.upl',
                     '../../tests-nmr/mock-data-remediation/5nip/5nip.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CyanaMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/5nip/DepositExpConstCC9.upl',
                 '../../tests-nmr/mock-data-remediation/5nip/5nip.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2k1m/2k1m-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2k1m/2k1m.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2mqq/2mqq-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2mqq/2mqq.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/5ue5/2_dp8_dihre.aco-corrected',
                     '../../tests-nmr/mock-data-remediation/5ue5/5ue5.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7elj/7col_sub.dist-corrected',
                     '../../tests-nmr/mock-data-remediation/7elj/7elj.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2myn/test.mr',
                     '../../tests-nmr/mock-data-remediation/2myn/2myn.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2n1g/test.mr',  # 2n1g-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2n1g/2n1g.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CyanaMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2n5e/2n5e-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2n5e/2n5e.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/8hga/pep_upl.upl-corrected',
                 '../../tests-nmr/mock-data-remediation/8hga/8hga.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6wa5/FIV-myr_minus-NOS.upl',
                 '../../tests-nmr/mock-data-remediation/6wa5/6wa5.cif')

    reader = CyanaMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2mxu/2mxu-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2mxu/2mxu.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CyanaMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2mxu/2mxu-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2mxu/2mxu.cif')

    reasons_ = {'chain_seq_id_remap': [{'chain_id': 'B',
                                        'seq_id_dict': {1200: 1120, 1201: 1121, 1202: 1122, 1203: 1123, 1204: 1124, 1205: 1125, 1206: 1126,
                                                        1207: 1127, 1208: 1128, 1209: 1129, 1210: 1130, 1211: 1131, 1212: 1132, 1213: 1133},
                                        'comp_id_set': ['THR', 'ALA', 'GLU', 'LEU', 'PRO', 'ASN', 'GLY', 'LYS', 'SER', 'ARG', 'ASP', 'GLN', 'VAL', 'PHE']}]}

    reader = CyanaMRReader(True, reasons=reasons_)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/8fg1/DADspinlinks.upl',
                 '../../tests-nmr/mock-data-remediation/8fg1/8fg1.cif')

    reader = CyanaMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6aau/m62a_restraints.txt-corrected',
                     '../../tests-nmr/mock-data-remediation/6aau/6aau.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CyanaMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6aau/m62a_restraints.txt-corrected',
                 '../../tests-nmr/mock-data-remediation/6aau/6aau.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6gvt/hybrid-structure-hbonds-restraints-cyana.rstr',
                 '../../tests-nmr/mock-data-remediation/6gvt/6gvt.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2mnh/2mnh-trimmed-div_dst.mr',
                     '../../tests-nmr/mock-data-remediation/2mnh/2mnh.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6xeh/cya.rdc',
                     '../../tests-nmr/mock-data-remediation/6xeh/6xeh.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7csq/ddtd.upl.txt-corrected',
                     '../../tests-nmr/mock-data-remediation/7csq/7csq.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/7ubg/TT-A-constraints-all.txt-corrected',
                 '../../tests-nmr/mock-data-remediation/7ubg/7ubg.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2rsd/2rsd-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2rsd/2rsd.cif')
    reader = CyanaMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2rsd/2rsd-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2rsd/2rsd.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6fw4/final.upl',
                 '../../tests-nmr/mock-data-remediation/6fw4/6fw4.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2n6y/2n6y-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2n6y/2n6y.cif')
    reader = CyanaMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2n6y/2n6y-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2n6y/2n6y.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2l8r/2l8r-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2l8r/2l8r.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2n63/2n63-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2n63/2n63.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7nt7/final.aco',
                     '../../tests-nmr/mock-data-remediation/7nt7/7nt7.cif')
    reader = CyanaMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/7nt7/final.aco',
                 '../../tests-nmr/mock-data-remediation/7nt7/7nt7.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6dm7/dG4CG4.cco',
                 '../../tests-nmr/mock-data-remediation/6dm7/6dm7.cif')

    reader = CyanaMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2lnh/2lnh-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2lnh/2lnh.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CyanaMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lnh/2lnh-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2lnh/2lnh.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2m0m/2m0m-corrected-div_src.mr',
                     '../../tests-nmr/mock-data-remediation/2m0m/2m0m.cif')
    reader = CyanaMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2m0m/2m0m-corrected-div_src.mr',
                 '../../tests-nmr/mock-data-remediation/2m0m/2m0m.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2nam/2nam-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2nam/2nam.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-daother-8191/D_1292126851_mr_P1.cyana.V7',
                 '../../tests-nmr/mock-data-daother-8191/D_800640_model_P1.cif.V3')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/7r0r/10_ORI_LOL.lol',
                 '../../tests-nmr/mock-data-remediation/7r0r/7r0r.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6drg/Cycle7_Cyana_With_GW_Constraints.upl',
                     '../../tests-nmr/mock-data-remediation/6drg/6drg.cif')
    reader = CyanaMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6drg/Cycle7_Cyana_With_GW_Constraints.upl',
                 '../../tests-nmr/mock-data-remediation/6drg/6drg.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-daother-8945/D_1000278694_mr-upload_P1.cyana.V4',
                 '../../tests-nmr/mock-data-daother-8945/D_800635_model_P1.cif.V4')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/5z5q/1103_4.8_BMRB.upl',
                 '../../tests-nmr/mock-data-remediation/5z5q/5z5q.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lk5/test.mr',
                 '../../tests-nmr/mock-data-remediation/2lk5/2lk5.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2m6i/2m6i-corrected-div_dst-div_dst-div_dst-div_dst.mr',
                 '../../tests-nmr/mock-data-remediation/2m6i/2m6i.cif')

    reader = CyanaMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2lrr/2lrr-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2lrr/2lrr.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CyanaMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lrr/2lrr-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2lrr/2lrr.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2kym/2kym-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2kym/2kym.cif')

    reader = CyanaMRReader(True, file_ext='upv')
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/5mcs/omcf_omcf320R.upv',
                 '../../tests-nmr/mock-data-remediation/5mcs/5mcs.cif', originalFileName='omcf_omcf320R.upv')

    reader = CyanaMRReader(True, file_ext='upl')
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/5ue2/pro_csp_28dec16.upl',
                 '../../tests-nmr/mock-data-remediation/5ue2/5ue2.cif', originalFileName='pro_csp_28dec16.upl')

    reader = CyanaMRReader(True, file_ext='upl')
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/5ue2/pro_mutations_28dec16.upl',
                 '../../tests-nmr/mock-data-remediation/5ue2/5ue2.cif', originalFileName='pro_mutations_28dec16.upl')

    reader = CyanaMRReader(True, file_ext='upl')
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/5ue2/methyl_NOEs.upl',
                 '../../tests-nmr/mock-data-remediation/5ue2/5ue2.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/5ue2/2_dp8_dihre.aco-corrected',
                 '../../tests-nmr/mock-data-remediation/5ue2/5ue2.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2rrn/2rrn-trimmed-div_src.mr',
                 '../../tests-nmr/mock-data-remediation/2rrn/2rrn.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6cgh/deposit.rdc',
                 '../../tests-nmr/mock-data-remediation/6cgh/6cgh.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2m5b/2m5b-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2m5b/2m5b.cif')

    reader = CyanaMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ = reader.parse('../../tests-nmr/mock-data-remediation/5ue2/pro_protect_28dec16.upl',
                                         '../../tests-nmr/mock-data-remediation/5ue2/5ue2.cif')
    reader = CyanaMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/5ue2/pro_protect_28dec16.upl',
                 '../../tests-nmr/mock-data-remediation/5ue2/5ue2.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lxn/test.mr',
                 '../../tests-nmr/mock-data-remediation/2lxn/2lxn.cif')

    reader = CyanaMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7sa5/D_1000259911_mr_P4.cyana.V1',
                     '../../tests-nmr/mock-data-remediation/7sa5/7sa5.cif')
    reader = CyanaMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/7sa5/D_1000259911_mr_P4.cyana.V1',
                 '../../tests-nmr/mock-data-remediation/7sa5/7sa5.cif')

    reader = CyanaMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2lum/2lum-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2lum/2lum.cif')
    reader = CyanaMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lum/2lum-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2lum/2lum.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/7en4/deposit.rdc',
                 '../../tests-nmr/mock-data-remediation/7en4/7en4.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/5knw/hbond_nmrstar.txt-corrected',
                 '../../tests-nmr/mock-data-remediation/5knw/5knw.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2mls/2mls-corrected-div_dst-div_dst.mr',
                 '../../tests-nmr/mock-data-remediation/2mls/2mls.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/7f7n/dis.upl_map',
                 '../../tests-nmr/mock-data-remediation/7f7n/7f7n.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2jrl/2jrl-corrected-div_src.mr',
                 '../../tests-nmr/mock-data-remediation/2jrl/2jrl.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2m5v/test_concat.mr',
                 '../../tests-nmr/mock-data-remediation/2m5v/2m5v.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2llp/test_multichain_noe.mr',
                 '../../tests-nmr/mock-data-remediation/2llp/2llp.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/5ujn/K27_both_RDC_for_armor_b72_edited.txt-corrected',
                 '../../tests-nmr/mock-data-remediation/5ujn/5ujn.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6kh9/18hrs_revised_4.dist.upl-corrected',
                 '../../tests-nmr/mock-data-remediation/6kh9/6kh9.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lj5/2lj5-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2lj5/2lj5.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2mk3/rdc_test.mr',
                 '../../tests-nmr/mock-data-remediation/2mk3/2mk3.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/7acb/7acb-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/7acb/7acb.cif')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-daother-7690/D_1300028390_mr-upload_P1.cyana.V1',
                 '../../tests-nmr/mock-data-daother-7690/D_1300028390_model-annotate_P1.cif.V2')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-daother-7690/D_1300022821_mr-upload_P2.cyana.V1',
                 '../../tests-nmr/mock-data-daother-7690/D_1300022821_model-annotate_P1.cif.V1')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-daother-7690/D_1300024364_mr-upload_P1.cyana.V2',
                 '../../tests-nmr/mock-data-daother-7690/D_1300024364_model-release_P1.cif.V1')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-daother-6830/2nd_test/cyana_rdc_restraints_exmaple',
                 '../../tests-nmr/mock-data-daother-6830/2nd_test/D_800411_model_P1.cif.V1')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-daother-6830/2nd_test/cyana_dihed_restraints_exmaple',
                 '../../tests-nmr/mock-data-daother-6830/2nd_test/D_800411_model_P1.cif.V1')

    reader = CyanaMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-daother-5829/D_1000249951_mr-upload_P1.cyana.V1',
                 '../../tests-nmr/mock-data-daother-5829/D_800467_model_P1.cif.V3')
