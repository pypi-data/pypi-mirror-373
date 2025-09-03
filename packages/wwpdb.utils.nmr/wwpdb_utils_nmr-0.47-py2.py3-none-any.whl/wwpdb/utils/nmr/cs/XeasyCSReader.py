##
# XeasyCSReader.py
#
# Update:
##
""" A collection of classes for parsing XEASY CS (aka. PROT) files.
"""
__docformat__ = "restructuredtext en"
__author__ = "Masashi Yokochi"
__email__ = "yokochi@protein.osaka-u.ac.jp"
__license__ = "Apache License 2.0"
__version__ = "1.0.0"

import sys
import os

from antlr4 import InputStream, CommonTokenStream, ParseTreeWalker
from typing import IO, List, Tuple, Optional

try:
    from wwpdb.utils.nmr.mr.LexerErrorListener import LexerErrorListener
    from wwpdb.utils.nmr.mr.ParserErrorListener import ParserErrorListener
    from wwpdb.utils.nmr.pk.XeasyPROTLexer import XeasyPROTLexer
    from wwpdb.utils.nmr.pk.XeasyPROTParser import XeasyPROTParser
    from wwpdb.utils.nmr.cs.XeasyCSParserListener import XeasyCSParserListener
    from wwpdb.utils.nmr.mr.ParserListenerUtil import MAX_ERROR_REPORT
    from wwpdb.utils.nmr.ChemCompUtil import ChemCompUtil
    from wwpdb.utils.nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from wwpdb.utils.nmr.nef.NEFTranslator import NEFTranslator
except ImportError:
    from nmr.mr.LexerErrorListener import LexerErrorListener
    from nmr.mr.ParserErrorListener import ParserErrorListener
    from nmr.pk.XeasyPROTLexer import XeasyPROTLexer
    from nmr.pk.XeasyPROTParser import XeasyPROTParser
    from nmr.cs.XeasyCSParserListener import XeasyCSParserListener
    from nmr.mr.ParserListenerUtil import MAX_ERROR_REPORT
    from nmr.ChemCompUtil import ChemCompUtil
    from nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from nmr.nef.NEFTranslator import NEFTranslator


class XeasyCSReader:
    """ Accessor methods for parsing XEASY CS (aka. PROT) files.
    """

    def __init__(self, verbose: bool = True, log: IO = sys.stdout,
                 polySeq: List[dict] = None, entityAssembly: Optional[dict] = None,
                 ccU: Optional[ChemCompUtil] = None, csStat: Optional[BMRBChemShiftStat] = None, nefT: Optional[NEFTranslator] = None,
                 reasons: Optional[dict] = None):
        self.__class_name__ = self.__class__.__name__
        self.__version__ = __version__

        self.__verbose = verbose
        self.__lfh = log
        self.__debug = False

        self.__maxLexerErrorReport = MAX_ERROR_REPORT
        self.__maxParserErrorReport = MAX_ERROR_REPORT

        self.__polySeq = polySeq
        self.__entityAssembly = entityAssembly  # key=Entity_assembly_ID (str), value=dictionary of 'entity_id' (int) and 'auth_asym_id' (str)

        # CCD accessing utility
        self.__ccU = ChemCompUtil(verbose, log) if ccU is None else ccU

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

    def setLexerMaxErrorReport(self, maxErrReport: int):
        self.__maxLexerErrorReport = maxErrReport

    def setParserMaxErrorReport(self, maxErrReport: int):
        self.__maxParserErrorReport = maxErrReport

    def parse(self, csFilePath: str, isFilePath: bool = True,
              createSfDict: bool = False, originalFileName: Optional[str] = None, listIdCounter: Optional[dict] = None,
              reservedListIds: Optional[dict] = None, entryId: Optional[str] = None
              ) -> Tuple[Optional[XeasyCSParserListener], Optional[ParserErrorListener], Optional[LexerErrorListener]]:
        """ Parse XEASY CS file.
            @return: XeasyCSParserListener for success or None otherwise, ParserErrorListener, LexerErrorListener.
        """

        ifh = None

        try:

            if isFilePath:
                csString = None

                if not os.access(csFilePath, os.R_OK):
                    if self.__verbose:
                        self.__lfh.write(f"+{self.__class_name__}.parse() {csFilePath} is not accessible.\n")
                    return None, None, None

                ifh = open(csFilePath, 'r', encoding='utf-8', errors='ignore')  # pylint: disable=consider-using-with
                input = InputStream(ifh.read())

            else:
                csFilePath, csString = None, csFilePath

                if csString is None or len(csString) == 0:
                    if self.__verbose:
                        self.__lfh.write(f"+{self.__class_name__}.parse() Empty string.\n")
                    return None, None, None

                input = InputStream(csString)

            lexer = XeasyPROTLexer(input)
            lexer.removeErrorListeners()

            lexer_error_listener = LexerErrorListener(csFilePath, maxErrorReport=self.__maxLexerErrorReport, ignoreCodicError=True)
            lexer.addErrorListener(lexer_error_listener)

            messageList = lexer_error_listener.getMessageList()

            if messageList is not None and self.__verbose:
                for description in messageList:
                    self.__lfh.write(f"[Syntax error] line {description['line_number']}:{description['column_position']} {description['message']}\n")
                    if 'input' in description:
                        self.__lfh.write(f"{description['input']}\n")
                        self.__lfh.write(f"{description['marker']}\n")

            stream = CommonTokenStream(lexer)
            parser = XeasyPROTParser(stream)
            # try with simpler/faster SLL prediction mode
            # parser._interp.predictionMode = PredictionMode.SLL  # pylint: disable=protected-access
            parser.removeErrorListeners()
            parser_error_listener = ParserErrorListener(csFilePath, maxErrorReport=self.__maxParserErrorReport, ignoreCodicError=True)
            parser.addErrorListener(parser_error_listener)
            tree = parser.xeasy_prot()

            walker = ParseTreeWalker()
            listener = XeasyCSParserListener(self.__verbose, self.__lfh,
                                             self.__polySeq, self.__entityAssembly,
                                             self.__ccU, self.__csStat, self.__nefT,
                                             self.__reasons)
            listener.setDebugMode(self.__debug)
            listener.createSfDict(createSfDict)
            if createSfDict:
                if originalFileName is not None:
                    listener.setOriginaFileName(originalFileName)
                if listIdCounter is not None:
                    listener.setListIdCounter(listIdCounter)
                if reservedListIds is not None:
                    listener.setReservedListIds(reservedListIds)
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
    nmr_poly_seq = [{'chain_id': '1',
                     'seq_id': list(range(1, 82)),
                     'comp_id': ['ALA', 'MET', 'GLY', 'ASN', 'LYS', 'ILE', 'TYR', 'VAL', 'GLY', 'GLY', 'LEU', 'PRO', 'THR', 'CYS', 'LEU', 'ASN', 'GLN', 'ASP', 'GLN', 'VAL',
                                 'LYS', 'GLU', 'LEU', 'LEU', 'GLN', 'SER', 'PHE', 'GLY', 'GLU', 'LEU', 'LYS', 'GLY', 'LEU', 'ASN', 'LEU', 'VAL', 'MET', 'ASP', 'THR', 'ASN',
                                 'THR', 'ASN', 'LEU', 'ASN', 'LYS', 'GLY', 'PHE', 'ALA', 'PHE', 'PHE', 'GLU', 'TYR', 'CYS', 'ASP', 'PRO', 'SER', 'VAL', 'THR', 'ASP', 'HIS',
                                 'ALA', 'ILE', 'ALA', 'GLY', 'LEU', 'HIS', 'GLY', 'MET', 'LEU', 'LEU', 'GLY', 'ASP', 'ARG', 'ARG', 'LEU', 'VAL', 'VAL', 'GLN', 'ARG', 'SER',
                                 'ILE']
                     }]
    entity_assembly = {'1': {'entity_id': 1, 'auth_asym_id': '.'}}
    reader = XeasyCSReader(True, polySeq=nmr_poly_seq, entityAssembly=entity_assembly)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7aaf/bmr34555/work/data/D_1292111069_nmr-peaks-upload_P2.dat.V1')
    assert reader_listener.getReasonsForReparsing() is None
