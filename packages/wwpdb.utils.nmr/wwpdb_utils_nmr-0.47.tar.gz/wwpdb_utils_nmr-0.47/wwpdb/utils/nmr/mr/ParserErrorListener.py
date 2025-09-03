##
# File: ParserErrorListner.py
# Date: 11-Feb-2022
#
# Updates:
""" Inheritance of ANTLR ErrorListener for Parser.
    @author: Masashi Yokochi
"""
__docformat__ = "restructuredtext en"
__author__ = "Masashi Yokochi"
__email__ = "yokochi@protein.osaka-u.ac.jp"
__license__ = "Apache License 2.0"
__version__ = "1.0.0"

import re

from antlr4.error.ErrorListener import ErrorListener
from typing import List, Optional

try:
    from wwpdb.utils.nmr.mr.ParserListenerUtil import (MAX_ERROR_REPORT,
                                                       MAX_ERR_LINENUM_REPORT)
except ImportError:
    from nmr.mr.ParserListenerUtil import (MAX_ERROR_REPORT,
                                           MAX_ERR_LINENUM_REPORT)


expecting_multiple_pattern = re.compile(r"(.*) expecting \{(.*)\}")
expecting_simple_pattern = re.compile(r"(.*) expecting (.*)")
substitution_pattern = re.compile(r"_(A[APR]|[BIQR][AP]|CM|[DE]A|FO?|HB|MP|PR|V[AS]|Lp)$")


class ParserErrorListener(ErrorListener):

    __messageList = None
    __errorLineNumber = None

    __filePath = None
    __inputString = None

    __maxErrorReport = MAX_ERROR_REPORT
    __errLineNumOverflowed = False

    __ignoreCodicError = False

    def __init__(self, filePath: str, inputString: Optional[str] = None,
                 maxErrorReport: int = MAX_ERROR_REPORT, ignoreCodicError: bool = False):

        self.__messageList = []
        self.__errorLineNumber = []

        self.__filePath = filePath

        if filePath is None and inputString is not None:
            self.__inputString = inputString.split('\n')
            if len(self.__inputString) == 0:
                self.__inputString = None

        self.__maxErrorReport = maxErrorReport
        self.__errLineNumOverflowed = False

        self.__ignoreCodicError = ignoreCodicError

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):

        if self.__errLineNumOverflowed:
            return

        if line not in self.__errorLineNumber:
            if len(self.__errorLineNumber) > MAX_ERR_LINENUM_REPORT:
                self.__errLineNumOverflowed = True
                return
            self.__errorLineNumber.append(line)

        if len(self.__messageList) >= self.__maxErrorReport:
            return

        _msg = msg.split("'")
        length = 1 if 'alternative' in msg or len(_msg) < 2 else len(_msg[1])

        if 'expecting' in msg:

            if 'expecting {' in msg:

                g = expecting_multiple_pattern.search(msg).groups()
                terms = g[1].split(', ')
                _terms = []
                for term in terms:
                    if term.startswith("'"):
                        _term = "'" + substitution_pattern.sub('', term.strip("'")) + "'"
                    else:
                        _term = substitution_pattern.sub('', term)
                    _terms.append(_term)

                msg = g[0] + ' expecting {' + ', '.join(_terms) + '}'

            else:

                g = expecting_simple_pattern.search(msg).groups()
                term = g[1]
                if term.startswith("'"):
                    _term = "'" + substitution_pattern.sub('', term.strip("'")) + "'"
                else:
                    _term = substitution_pattern.sub('', term)

                msg = g[0] + ' expecting ' + _term

        _dict = {'file_path': self.__filePath,
                 'line_number': line,
                 'column_position': column,
                 'message': msg,
                 'marker': " " * (column) + "^" * (length)}

        if self.__filePath is not None:
            _line = 1
            with open(self.__filePath, 'r', encoding='utf-8',
                      errors='ignore' if self.__ignoreCodicError else None) as ifh:
                for content in ifh:
                    if _line == line:
                        _dict['input'] = content.replace('\t', ' ')\
                            .replace('\r', ' ').replace('\n', ' ')\
                            .rstrip(' ')
                        break
                    _line += 1

        elif self.__inputString is not None:
            if line - 1 < len(self.__inputString):
                _dict['input'] = self.__inputString[line - 1].replace('\t', ' ')\
                    .replace('\r', ' ').replace('\n', ' ')\
                    .rstrip(' ')

        if 'at input' in _dict['message']:  # parser error
            try:
                p = _dict['message'].index('at input')
                _dict['message'] = _dict['message'][0:p] + 'at input:'
            except ValueError:
                pass

        self.__messageList.append(_dict)

    def reportAmbiguity(self, recognizer, dfa, startIndex, stopIndex, exact, ambigAlts, configs):
        pass

    def reportAttemptingFullContext(self, recognizer, dfa, startIndex, stopIndex, conflictingAlts, configs):
        pass

    def reportContextSensitivity(self, recognizer, dfa, startIndex, stopIndex, prediction, configs):
        pass

    def getMessageList(self) -> Optional[List[dict]]:
        return self.__messageList if len(self.__messageList) > 0 else None

    def getErrorLineNumber(self) -> Optional[List[int]]:
        return self.__errorLineNumber if len(self.__errorLineNumber) > 0 else None
