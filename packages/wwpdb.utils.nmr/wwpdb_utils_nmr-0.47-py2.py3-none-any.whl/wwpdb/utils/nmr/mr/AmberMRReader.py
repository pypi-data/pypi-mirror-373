##
# AmberMRReader.py
#
# Update:
##
""" A collection of classes for parsing AMBER MR files.
"""
__docformat__ = "restructuredtext en"
__author__ = "Masashi Yokochi"
__email__ = "yokochi@protein.osaka-u.ac.jp"
__license__ = "Apache License 2.0"
__version__ = "1.0.0"

import sys
import os
import copy

from antlr4 import InputStream, CommonTokenStream, ParseTreeWalker, PredictionMode
from typing import IO, List, Tuple, Optional

try:
    from wwpdb.utils.nmr.mr.LexerErrorListener import LexerErrorListener
    from wwpdb.utils.nmr.mr.ParserErrorListener import ParserErrorListener
    from wwpdb.utils.nmr.mr.AmberMRLexer import AmberMRLexer
    from wwpdb.utils.nmr.mr.AmberMRParser import AmberMRParser
    from wwpdb.utils.nmr.mr.AmberMRParserListener import AmberMRParserListener
    from wwpdb.utils.nmr.mr.AmberPTReader import AmberPTReader
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
    from nmr.mr.AmberMRLexer import AmberMRLexer
    from nmr.mr.AmberMRParser import AmberMRParser
    from nmr.mr.AmberMRParserListener import AmberMRParserListener
    from nmr.mr.AmberPTReader import AmberPTReader
    from nmr.mr.ParserListenerUtil import (coordAssemblyChecker,
                                           retrieveOriginalFileName,
                                           MAX_ERROR_REPORT,
                                           REPRESENTATIVE_MODEL_ID,
                                           REPRESENTATIVE_ALT_ID)
    from nmr.io.CifReader import CifReader
    from nmr.ChemCompUtil import ChemCompUtil
    from nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from nmr.nef.NEFTranslator import NEFTranslator


class AmberMRReader:
    """ Accessor methods for parsing AMBER MR files.
    """

    def __init__(self, verbose: bool = True, log: IO = sys.stdout,
                 representativeModelId: int = REPRESENTATIVE_MODEL_ID,
                 representativeAltId: str = REPRESENTATIVE_ALT_ID,
                 mrAtomNameMapping: Optional[List[dict]] = None,
                 cR: Optional[CifReader] = None, caC: Optional[dict] = None, ccU: Optional[ChemCompUtil] = None,
                 csStat: Optional[BMRBChemShiftStat] = None, nefT: Optional[NEFTranslator] = None,
                 atomNumberDict: Optional[dict] = None, auxAtomNumberDict: Optional[dict] = None,
                 reasons: Optional[dict] = None):
        self.__class_name__ = self.__class__.__name__
        self.__version__ = __version__

        self.__verbose = verbose
        self.__lfh = log
        self.__debug = False

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

        # AmberPTParserListener.getAtomNumberDict()
        self.__atomNumberDict = atomNumberDict
        self.__auxAtomNumberDict = auxAtomNumberDict

        # reasons for re-parsing request from the previous trial
        self.__reasons = self.__reasons__ = reasons

    def setDebugMode(self, debug: bool):
        self.__debug = debug

    def setLexerMaxErrorReport(self, maxErrReport: int):
        self.__maxLexerErrorReport = maxErrReport

    def setParserMaxErrorReport(self, maxErrReport: int):
        self.__maxParserErrorReport = maxErrReport

    def getReasons(self) -> Optional[dict]:
        return self.__reasons

    def parse(self, mrFilePath: str, cifFilePath: Optional[str] = None, ptFilePath: Optional[str] = None, isFilePath: bool = True,
              createSfDict: bool = False, originalFileName: Optional[str] = None,
              listIdCounter: Optional[dict] = None, entryId: Optional[str] = None
              ) -> Tuple[Optional[AmberMRParserListener], Optional[ParserErrorListener], Optional[LexerErrorListener]]:
        """ Parse AMBER MR file.
            @return: AmberMRParserListener for success or None otherwise, ParserErrorListener, LexerErrorListener.
        """

        ifh = None

        try:

            if isFilePath:
                mrString = None

                if not os.access(mrFilePath, os.R_OK):
                    if self.__verbose:
                        self.__lfh.write(f"+{self.__class_name__}.parse() {mrFilePath} is not accessible.\n")
                    return None, None, None

            else:
                mrFilePath, mrString = None, mrFilePath

                if mrString is None or len(mrString) == 0:
                    if self.__verbose:
                        self.__lfh.write(f"+{self.__class_name__}.parse() Empty string.\n")
                    return None, None, None

            if cifFilePath is not None:
                if not os.access(cifFilePath, os.R_OK):
                    if self.__verbose:
                        self.__lfh.write(f"+{self.__class_name__}.parse() {cifFilePath} is not accessible.\n")
                    return None, None, None

                if self.__cR is None:
                    self.__cR = CifReader(self.__verbose, self.__lfh)
                    if not self.__cR.parse(cifFilePath):
                        return None, None, None

            if ptFilePath is not None and self.__atomNumberDict is None:
                ptR = AmberPTReader(self.__verbose, self.__lfh,
                                    self.__representativeModelId,
                                    self.__representativeAltId,
                                    self.__mrAtomNameMapping,
                                    self.__cR, self.__caC,
                                    self.__ccU, self.__csStat, self.__nefT)
                ptPL, _, _ = ptR.parse(ptFilePath, cifFilePath)
                if ptPL is not None:
                    self.__atomNumberDict = ptPL.getAtomNumberDict()

            while True:

                if isFilePath:
                    ifh = open(mrFilePath, 'r', encoding='utf-8', errors='ignore')  # pylint: disable=consider-using-with
                    input = InputStream(ifh.read())
                else:
                    input = InputStream(mrString)

                lexer = AmberMRLexer(input)
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
                parser = AmberMRParser(stream)
                # try with simpler/faster SLL prediction mode
                parser._interp.predictionMode = PredictionMode.SLL  # pylint: disable=protected-access
                parser.removeErrorListeners()
                parser_error_listener = ParserErrorListener(mrFilePath, maxErrorReport=self.__maxParserErrorReport)
                parser.addErrorListener(parser_error_listener)
                tree = parser.amber_mr()

                walker = ParseTreeWalker()
                listener = AmberMRParserListener(self.__verbose, self.__lfh,
                                                 self.__representativeModelId,
                                                 self.__representativeAltId,
                                                 self.__mrAtomNameMapping,
                                                 self.__cR, self.__caC,
                                                 self.__ccU, self.__csStat, self.__nefT,
                                                 self.__atomNumberDict, self.__reasons)
                listener.setDebugMode(self.__debug)
                listener.createSfDict(createSfDict)
                if createSfDict:
                    listener.setOriginaFileName(originalFileName if originalFileName is not None else retrieveOriginalFileName(mrFilePath))
                    if listIdCounter is not None:
                        listener.setListIdCounter(copy.copy(listIdCounter))
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

                if self.__atomNumberDict is not None:
                    if self.__verbose and self.__debug:
                        if isFilePath:
                            self.__lfh.write(f"+{self.__class_name__}.parse() ++ Info  - {listener.getContentSubtype()}\n")
                    break

                reasons = self.__reasons = listener.getReasonsForReparsing()

                if reasons is not None:

                    listener.getSfDict()  # rewind listIdCounter (6neb)

                    if listener.warningMessage is None\
                       or len(listener.warningMessage) == 0\
                       or not any(f for f in listener.warningMessage
                                  if '[Atom not found]' in f or '[Sequence mismatch]' in f or '[Invalid data]' in f):
                        sanderAtomNumberDict = listener.getSanderAtomNumberDict()
                        if sanderAtomNumberDict is not None and len(sanderAtomNumberDict) > 0:
                            self.__atomNumberDict = sanderAtomNumberDict
                            if self.__auxAtomNumberDict is not None and len(self.__auxAtomNumberDict) > 0:
                                for k, v in self.__auxAtomNumberDict.items():
                                    if k not in self.__atomNumberDict:
                                        self.__atomNumberDict[k] = v

                    if isFilePath and ifh is not None:
                        ifh.close()

                    if isFilePath:
                        ifh = open(mrFilePath, 'r', encoding='utf-8', errors='ignore')  # pylint: disable=consider-using-with
                        input = InputStream(ifh.read())
                    else:
                        input = InputStream(mrString)

                    lexer = AmberMRLexer(input)
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
                    parser = AmberMRParser(stream)
                    # try with simpler/faster SLL prediction mode
                    parser._interp.predictionMode = PredictionMode.SLL  # pylint: disable=protected-access
                    parser.removeErrorListeners()
                    parser_error_listener = ParserErrorListener(mrFilePath, maxErrorReport=self.__maxParserErrorReport)
                    parser.addErrorListener(parser_error_listener)
                    tree = parser.amber_mr()
                    walker = ParseTreeWalker()
                    listener = AmberMRParserListener(self.__verbose, self.__lfh,
                                                     self.__representativeModelId,
                                                     self.__representativeAltId,
                                                     self.__mrAtomNameMapping,
                                                     self.__cR, self.__caC,
                                                     self.__ccU, self.__csStat, self.__nefT,
                                                     self.__atomNumberDict
                                                     if 'global_sequence_offset' not in reasons
                                                     and 'chain_seq_id_remap' not in reasons
                                                     and 'use_alt_poly_seq' not in reasons else None,
                                                     reasons
                                                     if self.__reasons__ is None
                                                     or 'global_sequence_offset' in self.__reasons__
                                                     or 'chain_seq_id_remap' in self.__reasons__
                                                     or 'use_alt_poly_seq' in self.__reasons__ else self.__reasons__)
                    listener.setDebugMode(self.__debug)
                    listener.createSfDict(createSfDict)
                    if createSfDict:
                        if originalFileName is not None:
                            listener.setOriginaFileName(originalFileName)
                        if listIdCounter is not None:
                            listener.setListIdCounter(copy.copy(listIdCounter))
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

                sanderAtomNumberDict = listener.getSanderAtomNumberDict()
                if sanderAtomNumberDict is not None and len(sanderAtomNumberDict) > 0:
                    self.__atomNumberDict = sanderAtomNumberDict
                    if self.__auxAtomNumberDict is not None and len(self.__auxAtomNumberDict) > 0:
                        for k, v in self.__auxAtomNumberDict.items():
                            if k not in self.__atomNumberDict:
                                self.__atomNumberDict[k] = v
                else:
                    break

                if isFilePath and ifh is not None:
                    ifh.close()

            return listener, parser_error_listener, lexer_error_listener

        except IOError as e:
            if self.__verbose:
                self.__lfh.write(f"+{self.__class_name__}.parse() ++ Error  - {str(e)}\n")
            return None, None, None
        finally:
            if isFilePath and ifh is not None:
                ifh.close()


if __name__ == "__main__":
    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/5o4d/ang.rst',
                 '../../tests-nmr/mock-data-remediation/5o4d/5o4d.cif',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6but/final.rst',
                 '../../tests-nmr/mock-data-remediation/6but/6but.cif',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/5n14/CL112_RST.all',
                 '../../tests-nmr/mock-data-remediation/5n14/5n14.cif',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/5m4w/planarity_1.txt-corrected',
                 '../../tests-nmr/mock-data-remediation/5m4w/5m4w.cif',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2mxj/2mxj-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2mxj/2mxj.cif',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2mki/2mki-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2mki/2mki.cif',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2n96/2n96-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2n96/2n96.cif',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2kxn/2kxn-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2kxn/2kxn.cif',
                 None)

    reasons_ = {'auth_seq_scheme': {'A': True}}
    reader = AmberMRReader(True, reasons=reasons_)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/7kbv/dihedral.amber-corrected',
                 '../../tests-nmr/mock-data-remediation/7kbv/7kbv.cif',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lec/2lec-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2lec/2lec.cif',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/7z9l/all.rst',
                 '../../tests-nmr/mock-data-remediation/7z9l/7z9l.cif',
                 '../../tests-nmr/mock-data-remediation/7z9l/ok1.top')

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2miw/2miw-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2miw/2miw.cif',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2kg1/2kg1-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2kg1/2kg1.cif',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lto/2lto-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2lto/2lto.cif',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6e83/ang.rst',
                 '../../tests-nmr/mock-data-remediation/6e83/6e83.cif',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6e83/dist.rst',
                 '../../tests-nmr/mock-data-remediation/6e83/6e83.cif',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6g99/man_noe2.rst',
                 '../../tests-nmr/mock-data-remediation/6g99/6g99.cif',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2n3o/2n3o-corrected-div_src.mr',
                 '../../tests-nmr/mock-data-remediation/2n3o/2n3o.cif',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/7nwj/CEP164_191201.rst',
                 '../../tests-nmr/mock-data-remediation/7nwj/7nwj.cif',
                 None)

    _reasons_ = {'auth_seq_scheme': {'B': True, 'A': True},
                 'global_sequence_offset': {'B': 252}}

    reader = AmberMRReader(True, reasons=_reasons_)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6gbm/hbonds.rst',
                 '../../tests-nmr/mock-data-remediation/6gbm/6gbm.cif',
                 None)

    reader = AmberMRReader(True, reasons=_reasons_)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6gbm/aco.rst',
                 '../../tests-nmr/mock-data-remediation/6gbm/6gbm.cif',
                 None)

    reader = AmberMRReader(True, reasons=_reasons_)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6gbm/chir.rst',
                 '../../tests-nmr/mock-data-remediation/6gbm/6gbm.cif',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6gbm/ac.rst',
                 '../../tests-nmr/mock-data-remediation/6gbm/6gbm.cif',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2mke/2mke-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2mke/2mke.cif',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2rv1/2rv1-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2rv1/2rv1.cif',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lql/2lql-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2lql/2lql.cif',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2mz1/2mz1-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2mz1/2mz1.cif',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lww/2lww-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2lww/2lww.cif',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/5n8m/RST.prot-dist',
                 '../../tests-nmr/mock-data-remediation/5n8m/5n8m.cif',
                 '../../tests-nmr/mock-data-remediation/5n8m/prmtop')

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-daother-8841/all_restraints_bp_030923-GglJOrl2.rst',
                 '../../tests-nmr/mock-data-daother-8841/D_800609_model_P1.cif.V4',
                 '../../tests-nmr/mock-data-daother-8841/complex_neutral-ziVR0Q9n.prmtop')

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-daother-8828/D_1292133069_mr-upload_P1.amber.V1',
                 '../../tests-nmr/mock-data-daother-8828/D_800607_model_P1.cif.V3',
                 '../../tests-nmr/mock-data-daother-8828/D_1292133069_mr-upload_P1.dat.V1')

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2kwq/2kwq-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2kwq/2kwq.cif',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6sdw/RST_34_test',
                 '../../tests-nmr/mock-data-remediation/6sdw/6sdw.cif',
                 '../../tests-nmr/mock-data-remediation/6sdw/prmtop_34')

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/7n7e/dihedral.amber',
                 '../../tests-nmr/mock-data-remediation/7n7e/7n7e.cif',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/7n7e/distance.amber-corrected',
                 '../../tests-nmr/mock-data-remediation/7n7e/7n7e.cif',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2llj/2llj-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2llj/2llj.cif',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/5oe1/pa8_wat2.rest',
                 '../../tests-nmr/mock-data-remediation/5oe1/5oe1.cif',
                 '../../tests-nmr/mock-data-remediation/5oe1/pa8_wat2.prmtop')

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2jsn/2jsn-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2jsn/2jsn.cif',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2m1g/test_dihed.mr',
                 '../../tests-nmr/mock-data-remediation/2m1g/2m1g.cif',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6zx7/bcl2ex.RST',
                 '../../tests-nmr/mock-data-remediation/6zx7/6zx7.cif',
                 '../../tests-nmr/mock-data-remediation/6zx7/bcl2ex.prmtop')

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2mko/test_plane.mr',
                 '../../tests-nmr/mock-data-remediation/2mko/2mko.cif',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/7qb3/RST.pcs-corrected',
                 '../../tests-nmr/mock-data-remediation/7qb3/7qb3.cif',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6f4z/RST_Hbond',
                 '../../tests-nmr/mock-data-remediation/6f4z/6f4z.cif',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6alu/dd09_RST',
                 '../../tests-nmr/mock-data-remediation/6alu/6alu.cif',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6i4o/all.rest',
                 '../../tests-nmr/mock-data-remediation/6i4o/6i4o.cif',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/5n8m/RST-2-tensors.dip',
                 '../../tests-nmr/mock-data-remediation/5n8m/5n8m.cif',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lar/2lar-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2lar/2lar.cif',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-daother-7690/D_1300018283_mr-upload_P1.dat.V1',
                 '../../tests-nmr/mock-data-daother-7690/D_1300018283_model-release_P1.cif.V3',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-daother-7690/D_1300020743_mr-upload_P1.amber.V1',
                 '../../tests-nmr/mock-data-daother-7690/D_1300020743_model-release_P1.cif.V2',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-daother-7690/D_1300028390_mr-upload_P1.amber.V1',
                 '../../tests-nmr/mock-data-daother-7690/D_1300028390_model-annotate_P1.cif.V2',
                 '../../tests-nmr/mock-data-daother-7690/D_1300028390_mr-upload_P1.dat.V1')

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-daother-7690/D_1300028390_mr-upload_P1.amber.V1',
                 '../../tests-nmr/mock-data-daother-7690/D_1300028390_model-annotate_P1.cif.V2',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-daother-7421/amber_rdc.test',
                 '../../tests-nmr/mock-data-daother-7421/D_800450_model_P1.cif.V1',
                 '../../tests-nmr/mock-data-daother-7421/D_1292118884_mr-upload_P1.dat.V1')

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-daother-7421/D_1292118884_mr-upload_P1.amber.V1',
                 '../../tests-nmr/mock-data-daother-7421/D_800450_model_P1.cif.V1',
                 None)

    reader = AmberMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-daother-7421/D_1292118884_mr-upload_P1.amber.V1',
                 '../../tests-nmr/mock-data-daother-7421/D_800450_model_P1.cif.V1',
                 '../../tests-nmr/mock-data-daother-7421/D_1292118884_mr-upload_P1.dat.V1')
