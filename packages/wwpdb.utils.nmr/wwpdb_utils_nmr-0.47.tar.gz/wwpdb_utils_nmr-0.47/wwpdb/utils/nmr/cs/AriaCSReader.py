##
# AriaCSReader.py
#
# Update:
##
""" A collection of classes for parsing ARIA CS files.
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
    from wwpdb.utils.nmr.pk.XMLLexer import XMLLexer
    from wwpdb.utils.nmr.pk.XMLParser import XMLParser
    from wwpdb.utils.nmr.cs.AriaCSParserListener import AriaCSParserListener
    from wwpdb.utils.nmr.mr.ParserListenerUtil import MAX_ERROR_REPORT
    from wwpdb.utils.nmr.ChemCompUtil import ChemCompUtil
    from wwpdb.utils.nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from wwpdb.utils.nmr.nef.NEFTranslator import NEFTranslator
except ImportError:
    from nmr.mr.LexerErrorListener import LexerErrorListener
    from nmr.mr.ParserErrorListener import ParserErrorListener
    from nmr.pk.XMLLexer import XMLLexer
    from nmr.pk.XMLParser import XMLParser
    from nmr.cs.AriaCSParserListener import AriaCSParserListener
    from nmr.mr.ParserListenerUtil import MAX_ERROR_REPORT
    from nmr.ChemCompUtil import ChemCompUtil
    from nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from nmr.nef.NEFTranslator import NEFTranslator


class AriaCSReader:
    """ Accessor methods for parsing ARIA CS files.
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
              ) -> Tuple[Optional[AriaCSParserListener], Optional[ParserErrorListener], Optional[LexerErrorListener]]:
        """ Parse ARIA CS file.
            @return: AriaCSParserListener for success or None otherwise, ParserErrorListener, LexerErrorListener.
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

            lexer = XMLLexer(input)
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
            parser = XMLParser(stream)
            # try with simpler/faster SLL prediction mode
            # parser._interp.predictionMode = PredictionMode.SLL  # pylint: disable=protected-access
            parser.removeErrorListeners()
            parser_error_listener = ParserErrorListener(csFilePath, maxErrorReport=self.__maxParserErrorReport, ignoreCodicError=True)
            parser.addErrorListener(parser_error_listener)
            tree = parser.document()

            walker = ParseTreeWalker()
            listener = AriaCSParserListener(self.__verbose, self.__lfh,
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
                     'seq_id': list(range(1, 120)),
                     'comp_id': ['SER', 'ALA', 'LYS', 'ASP', 'ILE', 'LYS', 'ASP', 'GLU', 'LYS', 'ILE', 'GLN', 'GLN', 'TYR', 'ARG', 'LYS', 'THR', 'LEU', 'THR', 'LYS', 'ILE',
                                 'VAL', 'LYS', 'ILE', 'LYS', 'THR', 'ALA', 'ILE', 'PHE', 'HIS', 'GLU', 'THR', 'VAL', 'LYS', 'VAL', 'THR', 'CYS', 'SER', 'LYS', 'ASP', 'GLY',
                                 'LYS', 'MET', 'LEU', 'GLU', 'TRP', 'TYR', 'LYS', 'GLY', 'LYS', 'ASN', 'ASP', 'SER', 'ASP', 'GLY', 'LYS', 'LYS', 'LYS', 'PRO', 'ILE', 'GLY',
                                 'SER', 'PHE', 'PRO', 'LEU', 'ASN', 'LYS', 'ILE', 'THR', 'SER', 'ILE', 'ARG', 'THR', 'LYS', 'VAL', 'ASP', 'ASN', 'LEU', 'LYS', 'SER', 'LEU',
                                 'GLU', 'ILE', 'SER', 'VAL', 'SER', 'SER', 'VAL', 'HIS', 'ILE', 'SER', 'THR', 'TYR', 'LEU', 'PHE', 'THR', 'PHE', 'LYS', 'THR', 'ARG', 'GLU',
                                 'GLU', 'ARG', 'GLU', 'SER', 'TRP', 'GLN', 'ASN', 'ASN', 'LEU', 'GLU', 'SER', 'PHE', 'ARG', 'LYS', 'ILE', 'MET', 'SER', 'MET', 'LYS']
                     }]
    entity_assembly = {'1': {'entity_id': 1, 'auth_asym_id': 'A'}}
    reader = AriaCSReader(False, polySeq=nmr_poly_seq, entityAssembly=entity_assembly)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6f24/bmr34202/work/data/D_1200007358_nmr-peaks-upload_P1.dat.V1')
    print(reader_listener.getReasonsForReparsing())
    reader = AriaCSReader(True, polySeq=nmr_poly_seq, entityAssembly=entity_assembly, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6f24/bmr34202/work/data/D_1200007358_nmr-peaks-upload_P1.dat.V1')
