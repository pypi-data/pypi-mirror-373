##
# File: AlignUtil.py
# Date: 18-Feb-2022
#
# Updates:
""" Utilities for pairwise alignment.
    @author: Masashi Yokochi
"""
__docformat__ = "restructuredtext en"
__author__ = "Masashi Yokochi"
__email__ = "yokochi@protein.osaka-u.ac.jp"
__license__ = "Apache License 2.0"
__version__ = "1.0.0"

import sys
import os
import copy
import json
import re
import io

from itertools import zip_longest
from typing import List, Tuple, Optional


# criterion for low sequence coverage
LOW_SEQ_COVERAGE = 0.3


# criterion for minimum sequence coverage when conflict occurs (NMR conventional deposition)
MIN_SEQ_COVERAGE_W_CONFLICT = 0.95


# empty value
emptyValue = (None, '', '.', '?', 'null', 'None')


# true value
trueValue = ('true', 't', 'yes', 'y', '1')


# taken from wwpdb.utils.align.SequenceReferenceData.py
monDict3 = {'ALA': 'A',
            'ARG': 'R',
            'ASN': 'N',
            'ASP': 'D',
            'ASX': 'B',
            'CYS': 'C',
            'GLN': 'Q',
            'GLU': 'E',
            'GLX': 'Z',
            'GLY': 'G',
            'HIS': 'H',
            'ILE': 'I',
            'LEU': 'L',
            'LYS': 'K',
            'MET': 'M',
            'PHE': 'F',
            'PRO': 'P',
            'SER': 'S',
            'THR': 'T',
            'TRP': 'W',
            'TYR': 'Y',
            'VAL': 'V',
            'DA': 'A',
            'DC': 'C',
            'DG': 'G',
            'DT': 'T',
            'DU': 'U',
            'DI': 'I',
            'A': 'A',
            'C': 'C',
            'G': 'G',
            'I': 'I',
            'T': 'T',
            'U': 'U'
            }

protonBeginCode = ('H', '1', '2', '3')
pseProBeginCode = ('H', 'Q', 'M', '1', '2', '3')
aminoProtonCode = ('H', 'HN', 'H1', 'H2', 'H3', 'HT1', 'HT2', 'HT3', 'H1*', 'H2*', 'H3*', 'HT', 'HT%', 'HT*', 'HT#')
carboxylCode = ('C', 'O', 'O1', 'O2', 'OT1', 'OT2', 'OXT', 'HXT')
jcoupBbPairCode = ('N', 'H', 'CA', 'C')
rdcBbPairCode = ('N', 'H', 'CA')
zincIonCode = ('ZN', 'ME', 'Z1', 'Z2')
calciumIonCode = ('CA2', 'CA2+', 'CA+2', 'ME')
unknownResidue = ('UNK', 'DN', 'N')

dnrParentCode = ('DC', 'CYT', 'DC5', 'DC3')
chParentCode = ('C', 'RCYT', 'C5', 'C3')

LARGE_ASYM_ID = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z')
LEN_LARGE_ASYM_ID = len(LARGE_ASYM_ID)

# maximum number of magnetically identifiable chain IDs
MAX_MAG_IDENT_ASYM_ID = 2


def hasLargeInnerSeqGap(polySeq: dict, seqIdName: str = 'seq_id') -> bool:
    """ Return whether large gap in a sequence.
    """

    _s = polySeq[seqIdName]

    for idx, seqId in enumerate(_s):
        if idx > 0 and None not in (seqId, _s[idx - 1]) and seqId - _s[idx - 1] > 20:
            return True

    return False


def hasLargeSeqGap(polySeq1: dict, polySeq2: dict,
                   seqIdName1: str = 'seq_id', seqIdName2: str = 'seq_id') -> bool:
    """ Return whether large gap in combined sequence of polySeq1 and polySeq2.
    """

    if None not in polySeq1[seqIdName1] and None not in polySeq2[seqIdName2]:
        _s = sorted(set(polySeq1[seqIdName1]) | set(polySeq2[seqIdName2]))
    elif None not in polySeq1[seqIdName1]:
        seqIds = [seqId for seqId in polySeq2[seqIdName2] if seqId is not None]
        _s = sorted(set(polySeq1[seqIdName1]) | set(seqIds))
    elif None not in polySeq2[seqIdName2]:
        seqIds = [seqId for seqId in polySeq1[seqIdName1] if seqId is not None]
        _s = sorted(set(seqIds) | set(polySeq2[seqIdName2]))
    else:
        seqId1s = [seqId for seqId in polySeq1[seqIdName1] if seqId is not None]
        seqId2s = [seqId for seqId in polySeq2[seqIdName2] if seqId is not None]
        _s = sorted(set(seqId1s) | set(seqId2s))

    for idx, seqId in enumerate(_s):
        if idx > 0 and None not in (seqId, _s[idx - 1]) and seqId - _s[idx - 1] > 20:
            return True

    return False


def fillInnerBlankCompId(polySeq: dict, seqIdName: str = 'seq_id') -> List[dict]:
    """ Fill inner blanked comp_ID.
    """

    if None not in polySeq[seqIdName]:
        _s = list(range(polySeq[seqIdName][0], polySeq[seqIdName][-1] + 1))
    else:
        seqIds = [seqId for seqId in polySeq[seqIdName] if seqId is not None]
        _s = list(range(seqIds[0], seqIds[-1] + 1))

    has_auth_comp_id = 'auth_comp_id' in polySeq

    _c = []
    if has_auth_comp_id:
        _a_c = []

    for seqId in _s:
        if seqId in polySeq[seqIdName]:
            idx = polySeq[seqIdName].index(seqId)
            if idx < len(polySeq['comp_id']):
                _c.append(polySeq['comp_id'][idx])
                if has_auth_comp_id:
                    _a_c.append(polySeq['auth_comp_id'][idx])
            else:
                _c.append('.')
                if has_auth_comp_id:
                    _a_c.append('.')
        else:
            _c.append('.')
            if has_auth_comp_id:
                _a_c.append('.')

    ps = {'chain_id': polySeq['chain_id'], 'seq_id': _s, 'comp_id': _c}
    if has_auth_comp_id:
        ps['auth_comp_id'] = _a_c
    if 'gap_in_auth_seq' in polySeq:
        ps['gap_in_auth_seq'] = polySeq['gap_in_auth_seq']

    return ps


def fillBlankCompId(polySeq1: dict, polySeq2: dict,
                    seqIdName1: str = 'seq_id', seqIdName2: str = 'seq_id') -> List[dict]:
    """ Fill blanked comp_ID in polySeq2 against polySeq1.
    """

    if seqIdName1 == seqIdName2:
        if None not in polySeq1[seqIdName1] and None not in polySeq2[seqIdName2]:
            _s = sorted(set(polySeq1[seqIdName1]) | set(polySeq2[seqIdName2]))
        elif None not in polySeq1[seqIdName1]:
            seqIds = [seqId for seqId in polySeq2[seqIdName2] if seqId is not None]
            _s = sorted(set(polySeq1[seqIdName1]) | set(seqIds))
        elif None not in polySeq2[seqIdName2]:
            seqIds = [seqId for seqId in polySeq1[seqIdName1] if seqId is not None]
            _s = sorted(set(seqIds) | set(polySeq2[seqIdName2]))
        else:
            seqId1s = [seqId for seqId in polySeq1[seqIdName1] if seqId is not None]
            seqId2s = [seqId for seqId in polySeq2[seqIdName2] if seqId is not None]
            _s = sorted(set(seqId1s) | set(seqId2s))
    else:
        if None not in polySeq2[seqIdName2]:
            _s = polySeq2[seqIdName2]
        else:
            _s = [seqId for seqId in polySeq2[seqIdName2] if seqId is not None]

    has_auth_comp_id = 'auth_comp_id' in polySeq2

    _c = []
    if has_auth_comp_id:
        _a_c = []

    for seqId in _s:
        if seqId in polySeq2[seqIdName2]:
            idx = polySeq2[seqIdName2].index(seqId)
            if idx < len(polySeq2['comp_id']):
                _c.append(polySeq2['comp_id'][idx])
                if has_auth_comp_id:
                    _a_c.append(polySeq2['auth_comp_id'][idx])
            else:
                _c.append('.')
                if has_auth_comp_id:
                    _a_c.append('.')
        else:
            _c.append('.')
            if has_auth_comp_id:
                _a_c.append('.')

    ps = {'chain_id': polySeq2['chain_id'], seqIdName2: _s, 'comp_id': _c}
    if has_auth_comp_id:
        ps['auth_comp_id'] = _a_c
    if seqIdName2 == 'auth_seq_id':
        ps['seq_id'] = polySeq2['seq_id']
    if seqIdName2 == 'seq_id' and 'auth_seq_id' in polySeq2:
        ps['auth_seq_id'] = polySeq2['auth_seq_id']
    if 'gap_in_auth_seq' in polySeq2:
        ps['gap_in_auth_seq'] = polySeq2['gap_in_auth_seq']

    return ps


def fillBlankCompIdWithOffset(polySeq: dict, offset: int, seqIdName: str = 'seq_id', compIdName: str = 'comp_id') -> List[dict]:
    """ Fill blanked comp_ID with offset.
    """

    if None not in polySeq[seqIdName]:
        _s = list(range(polySeq[seqIdName][0] - offset, polySeq[seqIdName][-1] + 1))
    else:
        seqIds = [seqId for seqId in polySeq[seqIdName] if seqId is not None]
        _s = list(range(seqIds[0] - offset, seqIds[-1] + 1))

    has_auth_comp_id = 'auth_comp_id' in polySeq

    _c = []
    if has_auth_comp_id:
        _a_c = []

    for seqId in _s:
        if seqId in polySeq[seqIdName]:
            idx = polySeq[seqIdName].index(seqId)
            if idx < len(polySeq['comp_id']):
                _c.append(polySeq[compIdName][idx])
                if has_auth_comp_id:
                    _a_c.append(polySeq['auth_comp_id'][idx])
            else:
                _c.append('.')
                if has_auth_comp_id:
                    _a_c.append('.')
        else:
            _c.append('.')
            if has_auth_comp_id:
                _a_c.append('.')

    ps = {'chain_id': polySeq['chain_id'], 'seq_id': _s, 'comp_id': _c}
    if has_auth_comp_id:
        ps['auth_comp_id'] = _a_c
    if 'gap_in_auth_seq' in polySeq:
        ps['gap_in_auth_seq'] = polySeq['gap_in_auth_seq']

    return ps


def beautifyPolySeq(polySeq1: dict, polySeq2: dict,
                    seqIdName1: str = 'seq_id', seqIdName2: str = 'seq_id') -> Tuple[List[dict], List[dict]]:
    """ Truncate negative seq_IDs and insert spacing between the large gap.
    """

    _polySeq1 = fillBlankCompId(polySeq2, polySeq1, seqIdName2, seqIdName1)  # pylint: disable=arguments-out-of-order
    _polySeq2 = fillBlankCompId(polySeq1, polySeq2, seqIdName1, seqIdName2)  # pylint: disable=arguments-out-of-order

    if _polySeq1[seqIdName1] != _polySeq2[seqIdName2]:
        return _polySeq1, _polySeq2

    has_auth_comp_id1 = 'auth_comp_id' in polySeq1
    has_auth_comp_id2 = 'auth_comp_id' in polySeq2

    _s = [seqId for seqId in _polySeq1[seqIdName1] if seqId is not None and seqId > 0]
    _c1 = [compId for seqId, compId
           in zip(_polySeq1[seqIdName1], _polySeq1['comp_id']) if seqId is not None and seqId > 0]
    if has_auth_comp_id1:
        _a_c1 = [authCompId for seqId, authCompId
                 in zip(_polySeq1[seqIdName1], _polySeq1['auth_comp_id']) if seqId is not None and seqId > 0]
        if _a_c1 in emptyValue:
            _a_c1 = _c1
    _c2 = [compId for seqId, compId
           in zip(_polySeq1[seqIdName1], _polySeq2['comp_id']) if seqId is not None and seqId > 0]
    if has_auth_comp_id2:
        _a_c2 = [authCompId for seqId, authCompId
                 in zip(_polySeq2[seqIdName1], _polySeq2['auth_comp_id']) if seqId is not None and seqId > 0]
        if _a_c2 in emptyValue:
            _a_c2 = _c2

    gapS, gapP = [], []

    lenSpacer = 5  # DAOTHER-7465, issue #2

    for idx, seqId in enumerate(_s):
        if idx > 0 and seqId - _s[idx - 1] > 20:
            prevSeqId = _s[idx - 1]
            for sp in range(1, lenSpacer + 1):
                gapS.append(prevSeqId + sp)
                gapS.append(seqId - sp)
            gapP.append(idx)

    if len(gapS) == 0:
        ps1 = {'chain_id': _polySeq1['chain_id'], 'seq_id': _s, 'comp_id': _c1}
        ps2 = {'chain_id': _polySeq2['chain_id'], 'seq_id': _s, 'comp_id': _c2}

        if has_auth_comp_id1:
            ps1['auth_comp_id'] = _a_c1
        if has_auth_comp_id2:
            ps2['auth_comp_id'] = _a_c2
        if 'gap_in_auth_seq' in polySeq1:
            ps1['gap_in_auth_seq'] = polySeq1['gap_in_auth_seq']
        if 'gap_in_auth_seq' in polySeq2:
            ps2['gap_in_auth_seq'] = polySeq2['gap_in_auth_seq']

        return ps1, ps2

    _s.extend(gapS)
    _s.sort()

    for p in reversed(gapP):
        for sp in range(1, lenSpacer + 1):
            _c1.insert(p, '.')
            _c2.insert(p, '.')
            if has_auth_comp_id1:
                _a_c1.insert(p, '.')
            if has_auth_comp_id2:
                _a_c2.insert(p, '.')

    ps1 = {'chain_id': _polySeq1['chain_id'], 'seq_id': _s, 'comp_id': _c1}
    ps2 = {'chain_id': _polySeq2['chain_id'], 'seq_id': _s, 'comp_id': _c2}

    if has_auth_comp_id1:
        ps1['auth_comp_id'] = _a_c1
    if has_auth_comp_id2:
        ps2['auth_comp_id'] = _a_c2
    if 'gap_in_auth_seq' in polySeq1:
        ps1['gap_in_auth_seq'] = polySeq1['gap_in_auth_seq']
    if 'gap_in_auth_seq' in polySeq2:
        ps2['gap_in_auth_seq'] = polySeq2['gap_in_auth_seq']

    return ps1, ps2


def getMiddleCode(compIdCode1: str, compIdCode2: str) -> str:
    """ Return array of middle code of sequence alignment.
    """

    f = []

    for idx, compId in enumerate(compIdCode1):
        f.append('|' if idx < len(compIdCode2) and compId == compIdCode2[idx] and compId != '.' else ' ')

    return ''.join(f)


def getGaugeCode(seqIdList: List[int], offset: int = 0) -> str:
    """ Return gauge code for a give sequence.
    """

    if offset > 0:
        _seqIdList = list(range(1, offset + 1))
        for idx, seqId in enumerate(seqIdList):
            if idx < offset:
                continue
            _seqIdList.append(seqId)
        seqIdList = _seqIdList

    lenSeqId = len([seqId for seqId in seqIdList if seqId is not None])
    lenCode = 0

    chars = []

    for seqId in seqIdList:

        if seqId is None:
            chars.append('-')
            continue

        if seqId >= 0 and seqId % 10 == 0 and lenCode == 0:

            code = str(seqId)
            lenCode = len(code)

            for p in range(lenCode):
                chars.append(code[p])

        if lenCode > 0:
            lenCode -= 1
        else:
            chars.append('-')

    lenChars = len(chars)

    for idx, seqId in enumerate(seqIdList):

        if seqId is None or seqId % 10 != 0:
            continue

        code = str(seqId)
        lenCode = len(code)

        if idx - lenCode > 0:
            for p in range(lenCode):
                if idx + p - lenCode + 1 >= 0 and idx + p < lenChars:
                    chars[idx + p - lenCode + 1] = chars[idx + p]
                    chars[idx + p] = '-'

    if offset > 0:
        for p in range(offset):
            chars[p] = '-'

    gaugeCode = ''.join(chars)

    if lenSeqId == len(seqIdList):
        return gaugeCode[:lenSeqId]

    _lenSeqId = len(seqIdList)

    offset = 0
    lastSeqId = None
    for idx, seqId in enumerate(seqIdList):

        if seqId is None:

            # 5n8m: nmr restraint remediation
            _offset = 1
            nextSeqId = None
            while True:
                if idx + _offset >= _lenSeqId:
                    break
                nextSeqId = seqIdList[idx + _offset]
                if nextSeqId is not None:
                    break
                _offset += 1

            if None in (lastSeqId, nextSeqId) or nextSeqId > lastSeqId + 1:
                p = idx + offset
                gaugeCode = gaugeCode[0:p] + ' ' + gaugeCode[p:]
                offset += 1
        else:
            lastSeqId = seqId

    return gaugeCode[:_lenSeqId]


def getScoreOfSeqAlign(myAlign: list) -> Tuple[int, int, int, int, int]:
    """ Return score of sequence alignment.
    """

    length = len(myAlign)

    aligned = [True] * length

    for p in range(length):
        myPr = myAlign[p]
        myPr0 = str(myPr[0])
        myPr1 = str(myPr[1])
        if myPr0 == '.' or myPr1 == '.':
            aligned[p] = False
        elif myPr0 != myPr1:
            pass
        else:
            break

    notAligned = True

    matched = unmapped = conflict = offset1 = offset2 = 0

    for p in range(length):
        myPr = myAlign[p]
        myPr0 = str(myPr[0])
        myPr1 = str(myPr[1])
        if myPr0 == '.' or myPr1 == '.':
            if notAligned and not aligned[p]:
                if myPr0 == '.' and myPr1 != '.'\
                   and offset2 == 0:  # DAOTHER-7421
                    offset1 += 1
                if myPr0 != '.' and myPr1 == '.'\
                   and offset1 == 0:  # DAOTHER-7421
                    offset2 += 1
                if myPr0 == '.' and myPr1 == '.':  # DAOTHER-7465
                    if offset2 == 0:
                        offset1 += 1
                    if offset1 == 0:
                        offset2 += 1
            unmapped += 1
        elif myPr0 != myPr1:
            conflict += 1
        else:
            notAligned = False
            matched += 1

    return matched, unmapped, conflict, offset1, offset2


def getOneLetterCodeCan(compId: str) -> str:
    """ Convert comp_ID to canonical one-letter code.
    """

    compId = compId.upper()

    if compId in monDict3:
        return monDict3[compId]

    if compId in emptyValue:
        return '.'

    return 'X'


def getOneLetterCode(compId: str) -> str:
    """ Convert comp_ID to one-letter code.
    """

    compId = compId.upper()

    if compId in monDict3:
        return monDict3[compId]

    if compId in emptyValue:
        return '.'

    return f'({compId})'


def getOneLetterCodeCanSequence(compIdList: List[str]) -> str:
    """ Convert array of comp_IDs to canonical one-letter code sequence.
    """

    return ''.join([getOneLetterCodeCan(compId) for compId in compIdList])


def getOneLetterCodeSequence(compIdList: List[str]) -> str:
    """ Convert array of comp_IDs to one-letter code sequence.
    """

    return ''.join([getOneLetterCode(compId) for compId in compIdList])


def letterToDigit(code: str, minDigit: int = 0) -> int:
    """ Return digit from a given chain code.
    """

    alphabet = 'abcdefghijklmnopqrstuvwxyz'

    unit = 1
    digit = 0

    if code is None:
        return minDigit

    for char in ''.join(reversed(code.lower())):

        if char.isdigit():
            digit += unit * int(char)
        elif char.isalpha():
            digit += unit * (alphabet.index(char) + 1)
        else:
            continue

        unit *= 27

    return digit if digit > minDigit else minDigit


def indexToLetter(index: int) -> str:
    """ Return chain code from a given index (0 based).
    """

    if index < 0:
        return '.'

    if index > 19683:
        index = index % 19683

    if index < 27:
        return str(chr(65 + index))

    if index < 729:
        return str(chr(64 + (index // 27)))\
            + str(chr(65 + (index % 27)))

    return str(chr(64 + (index // 729)))\
        + str(chr(64 + ((index % 729) // 27)))\
        + str(chr(65 + (index % 27)))


def getRestraintFormatName(fileType: str, ambig: bool = False) -> str:
    """ Return restraint format name.
    """

    if fileType == 'nmr-star':
        return 'NMR-STAR data'

    if fileType == 'nm-aux-amb':
        return 'AMBER topology'
    if fileType == 'nm-aux-cha':
        return 'CHARMM topology'
    if fileType == 'nm-aux-gro':
        return 'GROMACS topology'

    if fileType == 'nm-res-amb':
        return 'AMBER restraint'
    if fileType == 'nm-res-ari':
        return 'ARIA restraint'
    if fileType == 'nm-res-bio':
        return 'BIOSYM restraint'
    if fileType == 'nm-res-cha':
        return 'CHARMM restraint'
    if fileType == 'nm-res-cns':
        return 'CNS/XPLOR-NIH restraint' if ambig else 'CNS restraint'
    if fileType == 'nm-res-cya':
        return 'CYANA restraint'
    if fileType == 'nm-res-dyn':
        return 'DYNAMO/PALES/TALOS restraint'
    if fileType == 'nm-res-gro':
        return 'GROMACS restraint'
    if fileType == 'nm-res-isd':
        return 'ISD restraint'
    if fileType == 'nm-res-noa':
        return 'CYANA NOE assignment'
    if fileType == 'nm-res-mr':
        return 'MR data'
    if fileType == 'nm-res-ros':
        return 'ROSETTA restraint'
    if fileType == 'nm-res-sch':
        return 'SCHRODINGER/ASL restraint'
    if fileType == 'nm-res-syb':
        return 'SYBYL restraint'
    if fileType == 'nm-res-xpl':
        return 'XPLOR-NIH/CNS restraint' if ambig else 'XPLOR-NIH restraint'

    if fileType == 'nm-aux-xea':
        return 'XEASY PROT assignment'

    if fileType == 'nm-pea-ari':
        return 'ARIA spectral peak list'
    if fileType == 'nm-pea-ccp':
        return 'CCPN spectral peak list'
    if fileType == 'nm-pea-oli':
        return 'OLIVIA spectral peak list'
    if fileType == 'nm-pea-pip':
        return 'NMRPIPE spectral peak list'
    if fileType == 'nm-pea-pon':
        return 'PONDEROSA spectral peak list'
    if fileType in ('nm-pea-spa', 'nm-pea-sps'):
        return 'SPARKY spectral peak list'
    if fileType == 'nm-pea-top':
        return 'TOPSPIN spectral peak list'
    if fileType == 'nm-pea-vie':
        return 'NMRVIEW spectral peak list'
    if fileType == 'nm-pea-vnm':
        return 'VNMR spectral peak list'
    if fileType == 'nm-pea-xea':
        return 'XEASY spectral peak list'
    if fileType == 'nm-pea-xwi':
        return 'XWINNMR spectral peak list'
    if fileType == 'nm-pea-any':
        return 'other spectral peak list'

    return 'other restraint'


def getRestraintFormatNames(fileTypes: str, ambig: bool = False) -> str:
    """ Return restraint format name.
    """

    if len(fileTypes) == 0:
        return None

    if isinstance(fileTypes, str):
        return getRestraintFormatName(fileTypes, ambig)

    nameList = [getRestraintFormatName(fileType, ambig) for fileType in set(fileTypes)]

    return ', or '.join(nameList)


def getChemShiftFormatName(fileType: str) -> str:
    """ Return chemical shift format name.
    """

    if fileType == 'nmr-star':
        return 'NMR-STAR data'

    if fileType == 'nef':
        return 'NEF data'

    if fileType in ('nm-aux-xea', 'nm-shi-xea'):
        return 'XEASY PROT assignment'

    if fileType == 'nm-shi-ari':
        return 'ARIA chemical shift assignment'

    if fileType == 'nm-shi-bar':
        return 'Bare CSV/TSV chemical shift assignment'

    if fileType == 'nm-shi-gar':
        return 'GARRET chemical shift assignment'

    if fileType == 'nm-shi-npi':
        return 'NMRPIPE chemical shift assignment'

    if fileType == 'nm-shi-oli':
        return 'OLIVIA chemical shift assignment'

    if fileType == 'nm-shi-pip':
        return 'PIPP chemical shift assignment'

    if fileType == 'nm-shi-ppm':
        return 'PPM chemical shift assignment'

    if fileType == 'nm-shi-st2':
        return 'NMR-STAR V2.1 chemical shift assignment'

    return 'other chemical shift assignment'


def getChemShiftFormatNames(fileTypes: str) -> str:
    """ Return chemical shift format name.
    """

    if len(fileTypes) == 0:
        return None

    if isinstance(fileTypes, str):
        return getChemShiftFormatName(fileTypes)

    nameList = [getRestraintFormatName(fileType) for fileType in set(fileTypes)]

    return ', or '.join(nameList)


def updatePolySeqRst(polySeqRst: List[dict], chainId: str, seqId: int, compId: str, authCompId: Optional[str] = None):
    """ Update polymer sequence of the current MR file.
    """

    if seqId is None or compId in emptyValue:
        return

    if authCompId is None:
        for ps in polySeqRst:
            if 'auth_comp_id' not in ps:
                ps['auth_comp_id'] = copy.deepcopy(ps['comp_id'])

    ps = next((ps for ps in polySeqRst if ps['chain_id'] == chainId), None)
    if ps is None:
        polySeqRst.append({'chain_id': chainId, 'seq_id': [], 'comp_id': [], 'auth_comp_id': []})
        ps = polySeqRst[-1]

    if seqId not in ps['seq_id']:
        ps['seq_id'].append(seqId)
        ps['comp_id'].append(compId)
        ps['auth_comp_id'].append(compId if authCompId in emptyValue else authCompId)


def revertPolySeqRst(polySeqRst: List[dict], chainId: str, seqId: int, authCompId: str):
    """ Revert polymer sequence of the current MR file.
    """

    if seqId is None or authCompId in emptyValue:
        return

    ps = next((ps for ps in polySeqRst if ps['chain_id'] == chainId), None)
    if ps is None:
        polySeqRst.append({'chain_id': chainId, 'seq_id': [], 'comp_id': [], 'auth_comp_id': []})
        ps = polySeqRst[-1]

    if seqId in ps['seq_id']:
        idx = ps['seq_id'].index(seqId)
        ps['comp_id'][idx] = '.'
        ps['auth_comp_id'][idx] = authCompId
    else:
        ps['seq_id'].append(seqId)
        ps['comp_id'].append('.')
        ps['auth_comp_id'].append(authCompId)


def updatePolySeqRstAmbig(polySeqRstAmb: List[dict], chainId: str, seqId: int, compIds: List[str]):
    """ Update polymer sequence of the current MR file.
    """

    if seqId is None or len(compIds) == 0:
        return

    ps = next((ps for ps in polySeqRstAmb if ps['chain_id'] == chainId), None)
    if ps is None:
        polySeqRstAmb.append({'chain_id': chainId, 'seq_id': [], 'comp_ids': []})
        ps = polySeqRstAmb[-1]

    _compIds = set(compIds)

    if seqId not in ps['seq_id']:
        ps['seq_id'].append(seqId)
        ps['comp_ids'].append(_compIds)
    else:
        ps['comp_ids'][ps['seq_id'].index(seqId)] &= _compIds


def mergePolySeqRstAmbig(polySeqRst: List[dict], polySeqRstAmb: List[dict]):
    """ Merge polymer sequence and ambiguous polymer sequence of the curent MR file.
    """

    if len(polySeqRstAmb) == 0:
        return

    for _ps in polySeqRstAmb:
        chainId = _ps['chain_id']

        ps = next((ps for ps in polySeqRst if ps['chain_id'] == chainId), None)

        if ps is not None:
            continue

        __ps = copy.copy(_ps)

        for idx, (seqId, compIds) in enumerate(zip(__ps['seq_id'], __ps['comp_ids'])):
            if len(compIds) == 1:
                updatePolySeqRst(polySeqRst, chainId, seqId, list(compIds)[0])
                del _ps['seq_id'][idx]
                del _ps['comp_ids'][idx]

    for ps in polySeqRst:
        chainId = ps['chain_id']

        _ps = next((_ps for _ps in polySeqRstAmb if _ps['chain_id'] == chainId), None)

        if _ps is None:
            continue

        __ps = copy.copy(_ps)

        for idx, (seqId, compIds) in enumerate(zip(__ps['seq_id'], __ps['comp_ids'])):
            if len(compIds) == 1:
                updatePolySeqRst(polySeqRst, chainId, seqId, list(compIds)[0])
                del _ps['seq_id'][idx]
                del _ps['comp_ids'][idx]


def updatePolySeqRstFromAtomSelectionSet(polySeqRst: List[dict], atomSelectionSet: List[List[dict]]):
    """ Update polymer sequence of the current MR file.
    """

    if len(atomSelectionSet) == 0:
        return

    for atomSelection in atomSelectionSet:
        if len(atomSelection) == 0:
            continue
        for atom in atomSelection:
            chainId = atom['chain_id']
            seqId = atom['seq_id']
            compId = atom.get('comp_id', '.')

            if seqId is None or compId in emptyValue:
                continue

            updatePolySeqRst(polySeqRst, chainId, seqId, compId)


def sortPolySeqRst(polySeqRst: List[dict], nonPolyRemap: Optional[dict] = None):
    """ Sort polymer sequence of the current MR file by sequence number.
    """

    if polySeqRst is None:
        return

    if nonPolyRemap is None:

        for ps in polySeqRst:
            if None not in ps['seq_id']:
                minSeqId = min(ps['seq_id'])
                maxSeqId = max(ps['seq_id'])
            else:
                seqIds = [seqId for seqId in ps['seq_id'] if seqId is not None]
                minSeqId = min(seqIds)
                maxSeqId = max(seqIds)

            _seqIds = list(range(minSeqId, maxSeqId + 1))
            _compIds = ["."] * (maxSeqId - minSeqId + 1)
            _authCompIds = ["."] * (maxSeqId - minSeqId + 1)

            idx = 0
            for seqId in ps['seq_id']:
                if seqId is not None and seqId in _seqIds:
                    _idx = _seqIds.index(seqId)
                    _compIds[_idx] = ps['comp_id'][idx]
                    _authCompIds[_idx] = ps['auth_comp_id'][idx] if 'auth_comp_id' in ps else _compIds[_idx]
                    if _authCompIds[_idx] in emptyValue:
                        _authCompIds[_idx] = _compIds[_idx]
                    idx += 1

            ps['seq_id'] = _seqIds
            ps['comp_id'] = _compIds
            ps['auth_comp_id'] = _authCompIds

    else:

        remapList = []

        for compId, compIdMap in nonPolyRemap.items():
            for seqIdMap in compIdMap.values():
                remapList.append({'chain_id': seqIdMap['chain_id'],
                                  'seq_id': seqIdMap['seq_id'],
                                  'comp_id': compId})

        for pos, ps in enumerate(polySeqRst):
            seqIds = [seqId for seqId in ps['seq_id']
                      if not any(item for item in remapList if item['chain_id'] == ps['chain_id'] and item['seq_id'] == seqId)]

            if len(seqIds) == 0:
                continue

            minSeqId = min(seqIds)
            maxSeqId = max(seqIds)

            _seqIds = list(range(minSeqId, maxSeqId + 1))
            _compIds = ["."] * (maxSeqId - minSeqId + 1)
            _authCompIds = ["."] * (maxSeqId - minSeqId + 1)

            for idx, seqId in enumerate(ps['seq_id']):
                if minSeqId <= seqId <= maxSeqId:
                    _idx = _seqIds.index(seqId)
                    _compIds[_idx] = ps['comp_id'][idx]
                    _authCompIds[_idx] = ps['auth_comp_id'][idx] if 'auth_comp_id' in ps else _compIds[_idx]
                    if _authCompIds[_idx] in emptyValue:
                        _authCompIds[_idx] = _compIds[_idx]

            _endSeqIds, _endCompIds, _endAuthCompIds = [], [], []
            _begSeqIds, _begCompIds, _begAuthCompIds = [], [], []

            for item in remapList:
                if item['chain_id'] != ps['chain_id']:
                    continue
                seqId = item['seq_id']
                compId = item['comp_id']
                if seqId in ps['seq_id']:
                    authCompId = ps['auth_comp_id'][ps['seq_id'].index(seqId)]
                else:
                    authCompId = next(item['comp_id'] for item in remapList
                                      if item['chain_id'] == ps['chain_id'] and item['seq_id'] == seqId)
                if authCompId in emptyValue:
                    authCompId = compId
                if seqId > maxSeqId:
                    _endSeqIds.append(seqId)
                    _endCompIds.append(compId)
                    _endAuthCompIds.append(authCompId)
                elif seqId < minSeqId:
                    _begSeqIds.append(seqId)
                    _begCompIds.append(compId)
                    _begAuthCompIds.append(authCompId)

            if len(_begSeqIds) > 0:
                _begSeqIds.extend(_seqIds)
                _begCompIds.extend(_compIds)
                _begAuthCompIds.extend(_authCompIds)
                _seqIds = _begSeqIds
                _compIds = _begCompIds
                _authCompIds = _begAuthCompIds

            if len(_endSeqIds) > 0:
                _seqIds.extend(_endSeqIds)
                _compIds.extend(_endCompIds)
                _authCompIds.extend(_endAuthCompIds)

            ps['seq_id'] = _seqIds
            ps['comp_id'] = _compIds
            ps['auth_comp_id'] = _authCompIds

            if hasLargeInnerSeqGap(ps):
                polySeqRst[pos] = fillInnerBlankCompId(ps)


def syncCompIdOfPolySeqRst(polySeqRst: List[dict], compIdMap: dict):
    """ Synchronize residue names of polymer sequence of the current MR file.
    """

    if None in (polySeqRst, compIdMap) or 0 in (len(polySeqRst), len(compIdMap)):
        return

    for ps in polySeqRst:
        for idx, compId in enumerate(ps['comp_id']):
            if compId in compIdMap:
                ps['comp_id'][idx] = compIdMap[compId]


def stripPolySeqRst(polySeqRst: List[dict]):
    """ Strip polymer sequence of the current MR file.
    """

    if polySeqRst is None:
        return

    for ps in polySeqRst:
        seq_ids = copy.copy(ps['seq_id'])
        comp_ids = copy.copy(ps['comp_id'])

        has_auth_comp_id = 'auth_comp_id' in ps

        if has_auth_comp_id:
            auth_comp_ids = copy.copy(ps['auth_comp_id'])

        idx = 0
        while idx < len(seq_ids):
            if comp_ids[idx] != '.':
                break
            idx += 1

        if idx != 0:
            seq_ids = seq_ids[idx - 1:]
            comp_ids = comp_ids[idx - 1:]

            if has_auth_comp_id:
                auth_comp_ids = auth_comp_ids[idx - 1:]

        len_seq_ids = len(seq_ids)
        idx = len_seq_ids - 1
        while idx >= 0:
            if comp_ids[idx] != '.':
                break
            idx -= 1

        if idx != len_seq_ids - 1:
            seq_ids = seq_ids[:idx + 1]
            comp_ids = comp_ids[:idx + 1]

            if has_auth_comp_id:
                auth_comp_ids = auth_comp_ids[:idx + 1]

        if len(ps['seq_id']) != len(seq_ids):
            ps['seq_id'] = seq_ids
            ps['comp_id'] = comp_ids

            if has_auth_comp_id:
                ps['auth_comp_id'] = auth_comp_ids


def updateSeqAtmRst(seqAtmRst: List[dict], chainId: str, seqId: int, atoms: List[str]):
    """ Update sequence with atom names of the current MR file.
    """

    if seqId is None:
        return

    item = next((item for item in seqAtmRst if item['chain_id'] == chainId), None)
    if item is None:
        seqAtmRst.append({'chain_id': chainId, 'seq_id': [], 'atom_id': []})
        item = seqAtmRst[-1]

    if seqId not in item['seq_id']:
        item['seq_id'].append(seqId)
        item['atom_id'].append(atoms)
        return

    idx = item['seq_id'].index(seqId)
    for atom in atoms:
        if atom not in item['atom_id'][idx]:
            item['atom_id'][idx].append(atom)


def alignPolymerSequence(pA, polySeqModel: List[dict], polySeqRst: List[dict],
                         conservative: bool = True, resolvedMultimer: bool = False) -> Tuple[List[dict], List[dict]]:
    """ Align polymer sequence of the coordinates and restraints.
    """

    seqAlign, compIdMapping = [], []

    if None in (pA, polySeqModel, polySeqRst):
        return seqAlign, compIdMapping

    tabooList, inhibitList = [], []

    hasMultimer = False

    truncated = None

    _polySeqRst = copy.deepcopy(polySeqRst)

    for i1, ps1 in enumerate(polySeqModel):
        chain_id_name = 'auth_chain_id' if 'auth_chain_id' in ps1 else 'chain_id'
        chain_id = ps1[chain_id_name]

        if i1 >= LEN_LARGE_ASYM_ID:
            continue

        len_ident_chain_id = 0 if 'identical_chain_id' not in ps1 else len(ps1['identical_chain_id'])

        seq_id_name = 'auth_seq_id' if 'auth_seq_id' in ps1 else 'seq_id'

        for i2, ps2 in enumerate(_polySeqRst):
            chain_id2 = ps2['chain_id']

            if i2 >= LEN_LARGE_ASYM_ID:
                continue

            not_decided_ps2_comp_id = any(c2 for c2 in ps2['comp_id'] if c2.endswith('?'))  # AMBER/GROMACS topology
            if not_decided_ps2_comp_id:
                ps2['comp_id'] = [c2[:-1] if c2.endswith('?') else c2 for c2 in ps2['comp_id']]
                if len(ps1['comp_id']) == len(ps2['comp_id']):
                    if not any(cmp2 not in cmp1 for cmp1, cmp2 in zip(ps1['comp_id'], ps2['comp_id'])):
                        ps2['comp_id'] = copy.copy(ps1['comp_id'])

            pA.setReferenceSequence(ps1['comp_id'], 'REF' + chain_id)
            pA.addTestSequence(ps2['comp_id'], chain_id)
            pA.doAlign()

            myAlign = pA.getAlignment(chain_id)

            length = len(myAlign)

            if length == 0:
                tabooList.append({chain_id, chain_id2})
                continue

            _matched, unmapped, conflict, offset_1, offset_2 = getScoreOfSeqAlign(myAlign)

            prefer_ps1_alt_comp_id = prefer_ps2_auth_comp_id = False

            if _matched > 0 and conflict > 0 and not_decided_ps2_comp_id and 'auth_comp_id' in ps2:
                pA.setReferenceSequence(ps1['comp_id'], 'REF' + chain_id)
                pA.addTestSequence(ps2['auth_comp_id'], chain_id)
                pA.doAlign()

                _myAlign = pA.getAlignment(chain_id)

                _length = len(_myAlign)

                if _length > 0:
                    __matched, _unmapped, _conflict, _offset_1, _offset_2 = getScoreOfSeqAlign(_myAlign)

                    if __matched > _matched and _conflict == 0:  # DAOTHER-9511: auth_comp_id does match with the coordinates sequence
                        not_decided_ps2_comp_id = False
                        polySeqRst[i2]['comp_id'] = ps2['auth_comp_id']
                        myAlign = copy.deepcopy(_myAlign)
                        length, _matched, unmapped, conflict, offset_1, offset_2 =\
                            _length, __matched, _unmapped, _conflict, _offset_1, _offset_2
                        prefer_ps2_auth_comp_id = True

            elif _matched > 0 and conflict > 0 and 'alt_comp_id' in ps1 and conservative:
                pA.setReferenceSequence(ps1['alt_comp_id'], 'REF' + chain_id)
                pA.addTestSequence(ps2['comp_id'], chain_id)
                pA.doAlign()

                _myAlign = pA.getAlignment(chain_id)

                _length = len(_myAlign)

                if _length > 0:
                    __matched, _unmapped, _conflict, _offset_1, _offset_2 = getScoreOfSeqAlign(_myAlign)

                    if __matched > _matched and _conflict == 0:  # DAOTHER-9511: auth_comp_id does match with the coordinates sequence
                        if any(comp_id in emptyValue for comp_id in ps2['comp_id']):
                            valid_comp_ids = set()  # 2mze: ensure that comp_id_mapping has no side effect
                            comp_id_mapping = {}
                            for comp_id, alt_comp_id in zip(ps1['comp_id'], ps1['alt_comp_id']):
                                if comp_id == alt_comp_id:
                                    valid_comp_ids.add(alt_comp_id)
                                    continue
                                comp_id_mapping[alt_comp_id] = comp_id
                            polySeqRst[i2]['comp_id'] = [comp_id_mapping[comp_id]
                                                         if comp_id in comp_id_mapping and comp_id not in valid_comp_ids else comp_id
                                                         for comp_id in ps2['comp_id']]
                        elif len(polySeqRst[i2]['comp_id']) == len(ps1['comp_id']):
                            polySeqRst[i2]['comp_id'] = ps1['comp_id']
                        else:
                            idx1 = idx2 = 0
                            for i in range(length):
                                myPr = myAlign[i]
                                myPr0 = str(myPr[0])
                                myPr1 = str(myPr[1])
                                if myPr1 != '.':
                                    if myPr0 != '.':
                                        polySeqRst[i2]['comp_id'][idx2] = ps1['comp_id'][idx1]
                                    idx2 += 1
                                if myPr0 != '.':
                                    idx1 += 1
                        myAlign = copy.deepcopy(_myAlign)
                        length, _matched, unmapped, conflict, offset_1, offset_2 =\
                            _length, __matched, _unmapped, _conflict, _offset_1, _offset_2
                        prefer_ps1_alt_comp_id = True

            if length == unmapped + conflict or _matched <= conflict + (1 if length > 1 else 0):
                inhibitList.append({chain_id, chain_id2})
                continue

            if not_decided_ps2_comp_id:  # AMBER/GROMACS topology
                idx2 = 0
                for i in range(length):
                    myPr = myAlign[i]
                    myPr0 = str(myPr[0])
                    myPr1 = str(myPr[1])
                    if myPr1 != '.':
                        while idx2 < len(ps2['seq_id']):
                            if ps2['comp_id'][idx2] == myPr1:
                                ps2_seq_id = ps2['seq_id'][idx2]
                                ps2_auth_comp_id = ps2['auth_comp_id'][idx2]
                                compIdMapping.append({'chain_id': chain_id2, 'seq_id': ps2_seq_id,
                                                      'comp_id': myPr0, 'auth_comp_id': ps2_auth_comp_id})
                                idx2 += 1
                                break

            _ps1 = ps1 if offset_1 == 0 else fillBlankCompIdWithOffset(ps1, offset_1, seqIdName=seq_id_name,
                                                                       compIdName='alt_comp_id' if prefer_ps1_alt_comp_id else 'comp_id')
            _ps2 = ps2 if offset_2 == 0 else fillBlankCompIdWithOffset(ps2, offset_2, compIdName='auth_comp_id' if prefer_ps2_auth_comp_id else 'comp_id')

            if conflict == 0:
                if hasLargeInnerSeqGap(_ps2) and not hasLargeInnerSeqGap(_ps1):
                    _ps2 = fillInnerBlankCompId(_ps2)

            has_auth_seq_id1 = 'auth_seq_id' in _ps1
            has_auth_seq_id2 = 'auth_seq_id' in _ps2
            has_auth_comp_id1 = 'auth_comp_id' in _ps1
            has_auth_comp_id2 = 'auth_comp_id' in _ps2
            _seq_id_name = 'auth_seq_id' if has_auth_seq_id1 else 'seq_id'

            if 'gap_in_auth_seq' in ps1 and ps1['gap_in_auth_seq']:

                for p in range(len(ps1[seq_id_name]) - 1):
                    s_p = ps1[seq_id_name][p]
                    s_q = ps1[seq_id_name][p + 1]
                    if None in (s_p, s_q) or s_p not in ps2['seq_id'] or s_q not in ps2['seq_id']:
                        continue
                    if s_p + 1 != s_q:
                        beg = ps2['seq_id'].index(s_p)
                        end = ps2['seq_id'].index(s_q)
                        comp_ids = ps2['comp_id'][beg + 1:end]
                        if not any(comp_id for comp_id in comp_ids if comp_id != '.'):
                            ps2['seq_id'] = ps2['seq_id'][:beg + 1] + ps2['seq_id'][end:]
                            ps2['comp_id'] = ps2['comp_id'][:beg + 1] + ps2['comp_id'][end:]
                            if 'auth_comp_id' in ps2:
                                ps2['auth_comp_id'] = ps2['auth_comp_id'][:beg + 1] + ps2['auth_comp_id'][end:]
                            ps2['gap_in_auth_seq'] = True
                        beg = _ps2['seq_id'].index(s_p)
                        end = _ps2['seq_id'].index(s_q)
                        comp_ids = _ps2['comp_id'][beg + 1:end]
                        if not any(comp_id for comp_id in comp_ids if comp_id != '.'):
                            _ps2['seq_id'] = _ps2['seq_id'][:beg + 1] + _ps2['seq_id'][end:]
                            _ps2['comp_id'] = _ps2['comp_id'][:beg + 1] + _ps2['comp_id'][end:]
                            if 'auth_comp_id' in _ps2:
                                _ps2['auth_comp_id'] = _ps2['auth_comp_id'][:beg + 1] + _ps2['auth_comp_id'][end:]
                            _ps2['gap_in_auth_seq'] = True

            if conflict > 0 and hasLargeSeqGap(_ps1, _ps2, seqIdName1=_seq_id_name):
                __ps1, __ps2 = beautifyPolySeq(_ps1, _ps2, seqIdName1=_seq_id_name)

                if 'gap_in_auth_seq' in ps1 and ps1['gap_in_auth_seq']:

                    for p in range(len(ps1[seq_id_name]) - 1):
                        s_p = ps1[seq_id_name][p]
                        s_q = ps1[seq_id_name][p + 1]
                        if None in (s_p, s_q) or s_p not in __ps2['seq_id'] or s_q not in __ps2['seq_id']:
                            continue
                        if s_p + 1 != s_q:
                            beg = __ps2['seq_id'].index(s_p)
                            end = __ps2['seq_id'].index(s_q)
                            comp_ids = __ps2['comp_id'][beg + 1:end]
                            if not any(comp_id for comp_id in comp_ids if comp_id != '.'):
                                __ps2['seq_id'] = __ps2['seq_id'][:beg + 1] + __ps2['seq_id'][end:]
                                __ps2['comp_id'] = __ps2['comp_id'][:beg + 1] + __ps2['comp_id'][end:]
                                if 'auth_comp_id' in __ps2:
                                    __ps2['auth_comp_id'] = __ps2['auth_comp_id'][:beg + 1] + __ps2['auth_comp_id'][end:]
                                __ps2['gap_in_auth_seq'] = True

                _ps1_ = __ps1
                _ps2_ = __ps2

                pA.setReferenceSequence(_ps1_['alt_comp_id' if prefer_ps1_alt_comp_id else 'comp_id'], 'REF' + chain_id)
                pA.addTestSequence(_ps2_['auth_comp_id' if prefer_ps2_auth_comp_id else 'comp_id'], chain_id)
                pA.doAlign()

                myAlign = pA.getAlignment(chain_id)

                length = len(myAlign)

                _matched, unmapped, _conflict, _offset_1, _offset_2 = getScoreOfSeqAlign(myAlign)

                if _conflict == 0 and len(__ps2['comp_id']) - len(ps2['comp_id']) == conflict:
                    conflict = 0
                    offset_1 = _offset_1
                    offset_2 = _offset_2
                    _ps1 = __ps1
                    _ps2 = __ps2

            if conflict == 0 and _matched > 0 and unmapped > 0 and 'gap_in_auth_seq' in ps1 and ps1['gap_in_auth_seq']:
                for p in range(len(ps1[seq_id_name]) - 1):
                    s_p = ps1[seq_id_name][p]
                    s_q = ps1[seq_id_name][p + 1]
                    if None in (s_p, s_q) or s_p not in ps2['seq_id'] or s_q not in ps2['seq_id']:
                        continue
                    if s_p + 1 != s_q:
                        idx1 = idx2 = 0
                        beg = -1
                        for i in range(length):
                            myPr = myAlign[i]
                            myPr0 = str(myPr[0])
                            myPr1 = str(myPr[1])
                            if idx1 < len(ps1[seq_id_name]):
                                if ps1[seq_id_name][idx1] == s_p:
                                    beg = idx2
                            if myPr0 != '.':
                                while idx1 < len(_ps1['seq_id']):
                                    if _ps1['comp_id'][idx1] == myPr0:
                                        idx1 += 1
                                        break
                                    idx1 += 1
                            if myPr1 != '.':
                                while idx2 < len(_ps2['seq_id']):
                                    if _ps2['comp_id'][idx2] == myPr1:
                                        idx2 += 1
                                        break
                                    idx2 += 1
                        if beg >= 0 and beg + 1 < len(_ps2['seq_id']) and _ps2['seq_id'][beg] == s_p and _ps2['seq_id'][beg + 1] == s_p + 1:
                            beg = ps2['seq_id'].index(s_p)
                            end = ps2['seq_id'].index(s_q)
                            comp_ids = ps2['comp_id'][beg + 1:end]
                            if not any(comp_id for comp_id in comp_ids if comp_id != '.'):
                                truncated = (s_p, s_q)
                                break

            if conflict > len_ident_chain_id // 5 and not hasLargeSeqGap(_ps1, _ps2, seqIdName1=_seq_id_name):
                tabooList.append({chain_id, chain_id2})

            ref_length = len(ps1[seq_id_name])
            comp_id_name1 = 'alt_comp_id' if prefer_ps1_alt_comp_id and 'alt_comp_id' in _ps1 else 'comp_id'
            comp_id_name2 = 'auth_comp_id' if prefer_ps2_auth_comp_id and 'auth_comp_id' in _ps2 else 'comp_id'

            ref_code = getOneLetterCodeCanSequence(_ps1[comp_id_name1])
            test_code = getOneLetterCodeCanSequence(_ps2[comp_id_name2])
            mid_code = getMiddleCode(ref_code, test_code)
            ref_gauge_code = getGaugeCode(_ps1['seq_id'])
            test_gauge_code = getGaugeCode(_ps2['seq_id'])

            if conflict == 0\
               and any((__s1, __s2) for (__s1, __s2, __c1, __c2)
                       in zip(_ps1['seq_id'], _ps2['seq_id'], _ps1[comp_id_name1], _ps2[comp_id_name2])
                       if __c1 != '.' and __c2 != '.' and __c1 != __c2):
                seq_id1, seq_id2 = [], []
                if has_auth_seq_id1:
                    auth_seq_id1 = []
                if has_auth_seq_id2:
                    auth_seq_id2 = []
                comp_id1, comp_id2 = [], []
                if has_auth_comp_id1:
                    auth_comp_id1 = []
                if has_auth_comp_id2:
                    auth_comp_id2 = []
                idx1 = idx2 = 0
                for i in range(length):
                    myPr = myAlign[i]
                    myPr0 = str(myPr[0])
                    myPr1 = str(myPr[1])
                    if myPr0 != '.':
                        while idx1 < len(_ps1['seq_id']):
                            if _ps1[comp_id_name1][idx1] == myPr0:
                                seq_id1.append(_ps1['seq_id'][idx1])
                                if has_auth_seq_id1:
                                    auth_seq_id1.append(_ps1['auth_seq_id'][idx1])
                                comp_id1.append(myPr0)
                                if has_auth_comp_id1:
                                    auth_comp_id1.append(_ps1['auth_comp_id'][idx1])
                                idx1 += 1
                                break
                            idx1 += 1
                    elif idx1 < len(_ps1['seq_id']):
                        seq_id1.append(None)
                        if has_auth_seq_id1:
                            auth_seq_id1.append(None)
                        comp_id1.append('.')
                        if has_auth_comp_id1:
                            auth_comp_id1.append('.')
                    if myPr1 != '.':
                        while idx2 < len(_ps2['seq_id']):
                            if _ps2[comp_id_name2][idx2] == myPr1:
                                seq_id2.append(_ps2['seq_id'][idx2])
                                if has_auth_seq_id2:
                                    auth_seq_id2.append(_ps2['auth_seq_id'][idx2])
                                comp_id2.append(myPr1)
                                if has_auth_comp_id2:
                                    auth_comp_id2.append(_ps2['auth_comp_id'][idx2])
                                idx2 += 1
                                break
                            idx2 += 1
                    elif idx2 < len(_ps2['seq_id']):
                        seq_id2.append(None)
                        if has_auth_seq_id2:
                            auth_seq_id2.append(None)
                        comp_id2.append('.')
                        if has_auth_comp_id2:
                            auth_comp_id2.append('.')

                # handle improper position of open-gap introduced by PairwiseAlign()
                # 5ydy:         123456                123456
                # model PRGGGGNRQPPPPYPLTA    PRGGGGNRQPPPPYPLTA
                #       ||    ||||| |||||| vs ||    ||| |||||||
                # cs    PR....NRQPP.PYPLTA    PR....NRQ.PPPYPLTA
                #               123456                1 2356
                length = len(seq_id1)
                _seq_id1_ = copy.deepcopy(seq_id1)
                for idx1, _seq_id1 in enumerate(_seq_id1_):
                    if _seq_id1 is None and 1 < idx1 < length - 2\
                       and None not in (seq_id1[idx1 - 1], seq_id1[idx1 + 1])\
                       and seq_id1[idx1 + 1] - seq_id1[idx1 - 1] == 1:
                        for _idx1 in range(idx1 + 1, length - 1):
                            if None not in (seq_id1[_idx1], seq_id1[_idx1 + 1])\
                               and seq_id1[_idx1 + 1] - seq_id1[_idx1] == 2:
                                seq_id1.insert(_idx1 + 1, None)
                                seq_id1.pop(idx1)
                                comp_id1.insert(_idx1 + 1, '.')
                                comp_id1.pop(idx1)
                                if has_auth_seq_id1:
                                    auth_comp_id1.insert(_idx1 + 1, '.')
                                    auth_comp_id1.pop(idx1)

                length = len(seq_id2)
                _seq_id2_ = copy.deepcopy(seq_id2)
                for idx2, _seq_id2 in enumerate(_seq_id2_):
                    if _seq_id2 is None and 1 < idx2 < length - 2\
                       and None not in (seq_id2[idx2 - 1], seq_id2[idx2 + 1])\
                       and seq_id2[idx2 + 1] - seq_id2[idx2 - 1] == 1:
                        for _idx2 in range(idx2 + 1, length - 1):
                            if None not in (seq_id2[_idx2], seq_id2[_idx2 + 1])\
                               and seq_id2[_idx2 + 1] - seq_id2[_idx2] == 2:
                                seq_id2.insert(_idx2 + 1, None)
                                seq_id2.pop(idx2)
                                comp_id2.insert(_idx2 + 1, '.')
                                comp_id2.pop(idx2)
                                if has_auth_seq_id2:
                                    auth_comp_id2.insert(_idx2 + 1, '.')
                                    auth_comp_id2.pop(idx2)

                ref_code = getOneLetterCodeCanSequence(comp_id1)
                test_code = getOneLetterCodeCanSequence(comp_id2)
                mid_code = getMiddleCode(ref_code, test_code)
                ref_gauge_code = getGaugeCode(seq_id1, offset_1)
                test_gauge_code = getGaugeCode(seq_id2, offset_2)
                if ' ' in ref_gauge_code:
                    for p, g in enumerate(ref_gauge_code):
                        if g == ' ':
                            ref_code = ref_code[0:p] + '-' + ref_code[p + 1:]
                if ' ' in test_gauge_code:
                    for p, g in enumerate(test_gauge_code):
                        if g == ' ':
                            test_code = test_code[0:p] + '-' + test_code[p + 1:]
                # 5n8m: nmr restraint remediation
                _ps1['seq_id'] = seq_id1
                _ps2['seq_id'] = seq_id2
                if has_auth_seq_id1:
                    _ps1['auth_seq_id'] = auth_seq_id1
                if has_auth_seq_id2:
                    _ps2['auth_seq_id'] = auth_seq_id2
                if not prefer_ps1_alt_comp_id:
                    _ps1['comp_id'] = comp_id1
                else:
                    _ps1['comp_id'] = [comp_id for seq_id, comp_id in zip(_ps1['seq_id'], _ps1['comp_id']) if seq_id in seq_id1]
                if not prefer_ps2_auth_comp_id:
                    _ps2['comp_id'] = comp_id2
                else:
                    _ps2['comp_id'] = [comp_id for seq_id, comp_id in zip(_ps2['seq_id'], _ps2['comp_id']) if seq_id in seq_id2]
                if has_auth_comp_id1:
                    _ps1['auth_comp_id'] = auth_comp_id1
                if has_auth_comp_id2:
                    _ps2['auth_comp_id'] = auth_comp_id2

            matched = mid_code.count('|')

            seq_align = {'ref_chain_id': chain_id, 'test_chain_id': chain_id2, 'length': ref_length,
                         'matched': matched, 'conflict': conflict, 'unmapped': unmapped,
                         'sequence_coverage': float(f"{float(length - (unmapped + conflict)) / ref_length:.3f}"),
                         'ref_seq_id': _ps1['seq_id'], 'test_seq_id': _ps2['seq_id'],
                         'ref_gauge_code': ref_gauge_code, 'ref_code': ref_code, 'mid_code': mid_code,
                         'test_code': test_code, 'test_gauge_code': test_gauge_code}

            if 'auth_seq_id' in _ps1:
                seq_align['ref_auth_seq_id'] = _ps1['auth_seq_id']

            if 'identical_auth_chain_id' in ps1:
                hasMultimer = True

            seqAlign.append(seq_align)

    if truncated is not None:
        s_p, s_q = truncated

        for ps in polySeqRst:

            if s_p not in ps['seq_id'] or s_q not in ps['seq_id']:
                continue

            beg = ps['seq_id'].index(s_p)
            end = ps['seq_id'].index(s_q)
            comp_ids = ps['comp_id'][beg + 1:end]

            if not any(comp_id for comp_id in comp_ids if comp_id != '.'):
                ps['seq_id'] = ps['seq_id'][:beg + 1] + ps['seq_id'][end:]
                ps['comp_id'] = ps['comp_id'][:beg + 1] + ps['comp_id'][end:]
                if 'auth_comp_id' in ps:
                    ps['auth_comp_id'] = ps['auth_comp_id'][:beg + 1] + ps['auth_comp_id'][end:]
                ps['gap_in_auth_seq'] = True

        return alignPolymerSequence(pA, polySeqModel, polySeqRst, conservative, resolvedMultimer)

    if len(tabooList) > 0:
        _seqAlign = copy.copy(seqAlign)
        for sa in _seqAlign:
            if {sa['ref_chain_id'], sa['test_chain_id']} in tabooList:
                seqAlign.remove(sa)

    if len(inhibitList) > 0 and conservative:
        _seqAlign = copy.copy(seqAlign)
        for sa in _seqAlign:
            if {sa['ref_chain_id'], sa['test_chain_id']} in inhibitList:
                seqAlign.remove(sa)

    if hasMultimer and resolvedMultimer:
        _seqAlign = copy.copy(seqAlign)
        seqAlign = []
        for sa in _seqAlign:
            ref_chain_id = sa['ref_chain_id']
            test_chain_id = sa['test_chain_id']
            ps = next(ps for ps in polySeqModel if ps['auth_chain_id'] == ref_chain_id)
            if 'identical_auth_chain_id' not in ps or ref_chain_id == test_chain_id:
                seqAlign.append(sa)

    return seqAlign, compIdMapping


def alignPolymerSequenceWithConflicts(pA, polySeqModel: List[dict], polySeqRst: List[dict],
                                      conflictTh: int = 1) -> Tuple[List[dict], List[dict]]:
    """ Align polymer sequence of the coordinates and restraints allowing minor conflicts.
    """

    seqAlign, compIdMapping = [], []

    if None in (pA, polySeqModel, polySeqRst):
        return seqAlign, compIdMapping

    truncated = None

    for i1, ps1 in enumerate(polySeqModel):
        chain_id_name = 'auth_chain_id' if 'auth_chain_id' in ps1 else 'chain_id'
        chain_id = ps1[chain_id_name]

        if i1 >= LEN_LARGE_ASYM_ID:
            continue

        seq_id_name = 'auth_seq_id' if 'auth_seq_id' in ps1 else 'seq_id'

        for i2, ps2 in enumerate(polySeqRst):
            chain_id2 = ps2['chain_id']

            if i2 >= LEN_LARGE_ASYM_ID:
                continue

            not_decided_ps2_comp_id = any(c2 for c2 in ps2['comp_id'] if c2.endswith('?'))  # AMBER/GROMACS topology
            if not_decided_ps2_comp_id:
                ps2 = copy.deepcopy(ps2)
                ps2['comp_id'] = [c2[:-1] if c2.endswith('?') else c2 for c2 in ps2['comp_id']]
                if len(ps1['comp_id']) == len(ps2['comp_id']):
                    if not any(cmp2 not in cmp1 for cmp1, cmp2 in zip(ps1['comp_id'], ps2['comp_id'])):
                        ps2['comp_id'] = copy.copy(ps1['comp_id'])

            pA.setReferenceSequence(ps1['comp_id'], 'REF' + chain_id)
            pA.addTestSequence(ps2['comp_id'], chain_id)
            pA.doAlign()

            myAlign = pA.getAlignment(chain_id)

            length = len(myAlign)

            if length == 0:
                continue

            _matched, unmapped, conflict, offset_1, offset_2 = getScoreOfSeqAlign(myAlign)

            if length == unmapped + conflict or _matched <= conflict + (1 if length > 1 else 0) - conflictTh:
                continue

            if not_decided_ps2_comp_id:  # AMBER/GROMACS topology
                idx2 = 0
                for i in range(length):
                    myPr = myAlign[i]
                    myPr0 = str(myPr[0])
                    myPr1 = str(myPr[1])
                    if myPr1 != '.':
                        while idx2 < len(ps2['seq_id']):
                            if ps2['comp_id'][idx2] == myPr1:
                                ps2_seq_id = ps2['seq_id'][idx2]
                                ps2_auth_comp_id = ps2['auth_comp_id'][idx2]
                                compIdMapping.append({'chain_id': chain_id2, 'seq_id': ps2_seq_id,
                                                      'comp_id': myPr0, 'auth_comp_id': ps2_auth_comp_id})
                                idx2 += 1
                                break

            _ps1 = ps1 if offset_1 == 0 else fillBlankCompIdWithOffset(ps1, offset_1, seqIdName=seq_id_name)
            _ps2 = ps2 if offset_2 == 0 else fillBlankCompIdWithOffset(ps2, offset_2)

            if conflict == 0:
                if hasLargeInnerSeqGap(_ps2) and not hasLargeInnerSeqGap(_ps1):
                    _ps2 = fillInnerBlankCompId(_ps2)

            has_auth_seq_id1 = 'auth_seq_id' in _ps1
            has_auth_seq_id2 = 'auth_seq_id' in _ps2
            has_auth_comp_id1 = 'auth_comp_id' in _ps1
            has_auth_comp_id2 = 'auth_comp_id' in _ps2
            _seq_id_name = 'auth_seq_id' if has_auth_seq_id1 else 'seq_id'

            if 'gap_in_auth_seq' in ps1 and ps1['gap_in_auth_seq']:

                for p in range(len(ps1[seq_id_name]) - 1):
                    s_p = ps1[seq_id_name][p]
                    s_q = ps1[seq_id_name][p + 1]
                    if None in (s_p, s_q) or s_p not in ps2['seq_id'] or s_q not in ps2['seq_id']:
                        continue
                    if s_p + 1 != s_q:
                        beg = ps2['seq_id'].index(s_p)
                        end = ps2['seq_id'].index(s_q)
                        comp_ids = ps2['comp_id'][beg + 1:end]
                        if not any(comp_id for comp_id in comp_ids if comp_id != '.'):
                            ps2['seq_id'] = ps2['seq_id'][:beg + 1] + ps2['seq_id'][end:]
                            ps2['comp_id'] = ps2['comp_id'][:beg + 1] + ps2['comp_id'][end:]
                            if 'auth_comp_id' in ps2:
                                ps2['auth_comp_id'] = ps2['auth_comp_id'][:beg + 1] + ps2['auth_comp_id'][end:]
                            ps2['gap_in_auth_seq'] = True
                        beg = _ps2['seq_id'].index(s_p)
                        end = _ps2['seq_id'].index(s_q)
                        comp_ids = _ps2['comp_id'][beg + 1:end]
                        if not any(comp_id for comp_id in comp_ids if comp_id != '.'):
                            _ps2['seq_id'] = _ps2['seq_id'][:beg + 1] + _ps2['seq_id'][end:]
                            _ps2['comp_id'] = _ps2['comp_id'][:beg + 1] + _ps2['comp_id'][end:]
                            if 'auth_comp_id' in _ps2:
                                _ps2['auth_comp_id'] = _ps2['auth_comp_id'][:beg + 1] + _ps2['auth_comp_id'][end:]
                            _ps2['gap_in_auth_seq'] = True

            if conflict > 0 and hasLargeSeqGap(_ps1, _ps2, seqIdName1=_seq_id_name):
                __ps1, __ps2 = beautifyPolySeq(_ps1, _ps2, seqIdName1=_seq_id_name)

                if 'gap_in_auth_seq' in ps1 and ps1['gap_in_auth_seq']:

                    for p in range(len(ps1[seq_id_name]) - 1):
                        s_p = ps1[seq_id_name][p]
                        s_q = ps1[seq_id_name][p + 1]
                        if None in (s_p, s_q) or s_p not in __ps2['seq_id'] or s_q not in __ps2['seq_id']:
                            continue
                        if s_p + 1 != s_q:
                            beg = __ps2['seq_id'].index(s_p)
                            end = __ps2['seq_id'].index(s_q)
                            comp_ids = __ps2['comp_id'][beg + 1:end]
                            if not any(comp_id for comp_id in comp_ids if comp_id != '.'):
                                __ps2['seq_id'] = __ps2['seq_id'][:beg + 1] + __ps2['seq_id'][end:]
                                __ps2['comp_id'] = __ps2['comp_id'][:beg + 1] + __ps2['comp_id'][end:]
                                if 'auth_comp_id' in __ps2:
                                    __ps2['auth_comp_id'] = __ps2['auth_comp_id'][:beg + 1] + __ps2['auth_comp_id'][end:]
                                __ps2['gap_in_auth_seq'] = True

                _ps1_ = __ps1
                _ps2_ = __ps2

                pA.setReferenceSequence(_ps1_['comp_id'], 'REF' + chain_id)
                pA.addTestSequence(_ps2_['comp_id'], chain_id)
                pA.doAlign()

                myAlign = pA.getAlignment(chain_id)

                length = len(myAlign)

                _matched, unmapped, _conflict, _offset_1, _offset_2 = getScoreOfSeqAlign(myAlign)

                if _conflict == 0 and len(__ps2['comp_id']) - len(ps2['comp_id']) == conflict:
                    conflict = 0
                    offset_1 = _offset_1
                    offset_2 = _offset_2
                    _ps1 = __ps1
                    _ps2 = __ps2

            if conflict == 0 and _matched > 0 and unmapped > 0 and 'gap_in_auth_seq' in ps1 and ps1['gap_in_auth_seq']:
                for p in range(len(ps1[seq_id_name]) - 1):
                    s_p = ps1[seq_id_name][p]
                    s_q = ps1[seq_id_name][p + 1]
                    if None in (s_p, s_q) or s_p not in ps2['seq_id'] or s_q not in ps2['seq_id']:
                        continue
                    if s_p + 1 != s_q:
                        idx1 = idx2 = 0
                        beg = -1
                        for i in range(length):
                            myPr = myAlign[i]
                            myPr0 = str(myPr[0])
                            myPr1 = str(myPr[1])
                            if idx1 < len(ps1[seq_id_name]):
                                if ps1[seq_id_name][idx1] == s_p:
                                    beg = idx2
                            if myPr0 != '.':
                                while idx1 < len(_ps1['seq_id']):
                                    if _ps1['comp_id'][idx1] == myPr0:
                                        idx1 += 1
                                        break
                                    idx1 += 1
                            if myPr1 != '.':
                                while idx2 < len(_ps2['seq_id']):
                                    if _ps2['comp_id'][idx2] == myPr1:
                                        idx2 += 1
                                        break
                                    idx2 += 1
                        if beg >= 0 and beg + 1 < len(_ps2['seq_id']) and _ps2['seq_id'][beg] == s_p and _ps2['seq_id'][beg + 1] == s_p + 1:
                            beg = ps2['seq_id'].index(s_p)
                            end = ps2['seq_id'].index(s_q)
                            comp_ids = ps2['comp_id'][beg + 1:end]
                            if not any(comp_id for comp_id in comp_ids if comp_id != '.'):
                                truncated = (s_p, s_q)
                                break

            if conflict > conflictTh:
                continue

            ref_length = len(ps1[seq_id_name])

            ref_code = getOneLetterCodeCanSequence(_ps1['comp_id'])
            test_code = getOneLetterCodeCanSequence(_ps2['comp_id'])
            mid_code = getMiddleCode(ref_code, test_code)
            ref_gauge_code = getGaugeCode(_ps1['seq_id'])
            test_gauge_code = getGaugeCode(_ps2['seq_id'])

            if any((__s1, __s2) for (__s1, __s2, __c1, __c2)
                   in zip(_ps1['seq_id'], _ps2['seq_id'], _ps1['comp_id'], _ps2['comp_id'])
                   if __c1 != '.' and __c2 != '.' and __c1 != __c2):
                seq_id1, seq_id2 = [], []
                if has_auth_seq_id1:
                    auth_seq_id1 = []
                if has_auth_seq_id2:
                    auth_seq_id2 = []
                comp_id1, comp_id2 = [], []
                if has_auth_comp_id1:
                    auth_comp_id1 = []
                if has_auth_comp_id2:
                    auth_comp_id2 = []
                idx1 = idx2 = 0
                for i in range(length):
                    myPr = myAlign[i]
                    myPr0 = str(myPr[0])
                    myPr1 = str(myPr[1])
                    if myPr0 != '.':
                        while idx1 < len(_ps1['seq_id']):
                            if _ps1['comp_id'][idx1] == myPr0:
                                seq_id1.append(_ps1['seq_id'][idx1])
                                if has_auth_seq_id1:
                                    auth_seq_id1.append(_ps1['auth_seq_id'][idx1])
                                if has_auth_comp_id1:
                                    auth_comp_id1.append(_ps1['auth_comp_id'][idx1])
                                comp_id1.append(myPr0)
                                idx1 += 1
                                break
                            idx1 += 1
                    elif idx1 < len(_ps1['seq_id']):
                        seq_id1.append(None)
                        if has_auth_seq_id1:
                            auth_seq_id1.append(None)
                        comp_id1.append('.')
                        if has_auth_comp_id1:
                            auth_comp_id1.append('.')
                    if myPr1 != '.':
                        while idx2 < len(_ps2['seq_id']):
                            if _ps2['comp_id'][idx2] == myPr1:
                                seq_id2.append(_ps2['seq_id'][idx2])
                                if has_auth_seq_id2:
                                    auth_seq_id2.append(_ps2['auth_seq_id'][idx2])
                                comp_id2.append(myPr1)
                                if has_auth_comp_id2:
                                    auth_comp_id2.append(_ps2['auth_comp_id'][idx2])
                                idx2 += 1
                                break
                            idx2 += 1
                    elif idx2 < len(_ps2['seq_id']):
                        seq_id2.append(None)
                        if has_auth_seq_id2:
                            auth_seq_id2.append(None)
                        comp_id2.append('.')
                        if has_auth_comp_id2:
                            auth_comp_id2.append('.')
                ref_code = getOneLetterCodeCanSequence(comp_id1)
                test_code = getOneLetterCodeCanSequence(comp_id2)
                mid_code = getMiddleCode(ref_code, test_code)
                ref_gauge_code = getGaugeCode(seq_id1, offset_1)
                test_gauge_code = getGaugeCode(seq_id2, offset_2)
                if ' ' in ref_gauge_code:
                    for p, g in enumerate(ref_gauge_code):
                        if g == ' ':
                            ref_code = ref_code[0:p] + '-' + ref_code[p + 1:]
                if ' ' in test_gauge_code:
                    for p, g in enumerate(test_gauge_code):
                        if g == ' ':
                            test_code = test_code[0:p] + '-' + test_code[p + 1:]
                # 5n8m: nmr restraint remediation
                _ps1['seq_id'] = seq_id1
                _ps2['seq_id'] = seq_id2
                if has_auth_seq_id1:
                    _ps1['auth_seq_id'] = auth_seq_id1
                if has_auth_seq_id2:
                    _ps2['auth_seq_id'] = auth_seq_id2
                _ps1['comp_id'] = comp_id1
                _ps2['comp_id'] = comp_id2
                if has_auth_comp_id1:
                    _ps1['auth_comp_id'] = auth_comp_id1
                if has_auth_comp_id2:
                    _ps2['auth_comp_id'] = auth_comp_id2

            matched = mid_code.count('|')

            seq_align = {'ref_chain_id': chain_id, 'test_chain_id': chain_id2, 'length': ref_length,
                         'matched': matched, 'conflict': conflict, 'unmapped': unmapped,
                         'sequence_coverage': float(f"{float(length - (unmapped + conflict)) / ref_length:.3f}"),
                         'ref_seq_id': _ps1['seq_id'], 'test_seq_id': _ps2['seq_id'],
                         'ref_gauge_code': ref_gauge_code, 'ref_code': ref_code, 'mid_code': mid_code,
                         'test_code': test_code, 'test_gauge_code': test_gauge_code}

            if has_auth_seq_id1:
                seq_align['ref_auth_seq_id'] = _ps1['auth_seq_id']

            seqAlign.append(seq_align)

    if truncated is not None:
        s_p, s_q = truncated

        for ps in polySeqRst:

            if s_p not in ps['seq_id'] or s_q not in ps['seq_id']:
                continue

            beg = ps['seq_id'].index(s_p)
            end = ps['seq_id'].index(s_q)
            comp_ids = ps['comp_id'][beg + 1:end]

            if not any(comp_id for comp_id in comp_ids if comp_id != '.'):
                ps['seq_id'] = ps['seq_id'][:beg + 1] + ps['seq_id'][end:]
                ps['comp_id'] = ps['comp_id'][:beg + 1] + ps['comp_id'][end:]
                if 'auth_comp_id' in ps:
                    ps['auth_comp_id'] = ps['auth_comp_id'][:beg + 1] + ps['auth_comp_id'][end:]
                ps['gap_in_auth_seq'] = True

        return alignPolymerSequenceWithConflicts(pA, polySeqModel, polySeqRst, conflictTh=conflictTh)

    return seqAlign, compIdMapping


def assignPolymerSequence(pA, ccU, fileType: str, polySeqModel: List[dict], polySeqRst: List[dict], seqAlign: List[dict]
                          ) -> Tuple[Optional[List[dict]], List[str]]:
    """ Assign polymer sequences of restraints.
    """

    if None in (pA, polySeqModel, polySeqRst, seqAlign):
        return None, []

    warnings = []

    mrFormatName = getRestraintFormatName(fileType)
    _a_mr_format_name = 'the ' + mrFormatName

    mr_chains = len(polySeqRst) if len(polySeqRst) < LEN_LARGE_ASYM_ID else LEN_LARGE_ASYM_ID

    mat, indices = [], []

    for i1, ps1 in enumerate(polySeqModel):
        chain_id_name = 'auth_chain_id' if 'auth_chain_id' in ps1 else 'chain_id'
        chain_id = ps1[chain_id_name]

        if i1 >= LEN_LARGE_ASYM_ID:
            continue

        seq_id_name = 'auth_seq_id' if 'auth_seq_id' in ps1 else 'seq_id'

        cost = [0 for i in range(mr_chains)]

        for i2, ps2 in enumerate(polySeqRst):
            chain_id2 = ps2['chain_id']

            if i2 >= LEN_LARGE_ASYM_ID:
                continue

            result = next((seq_align for seq_align in seqAlign
                           if seq_align['ref_chain_id'] == chain_id
                           and seq_align['test_chain_id'] == chain_id2), None)

            if result is not None:
                cost[polySeqRst.index(ps2)] = result['unmapped'] + result['conflict'] - result['length']
                if result['length'] >= len(ps1[seq_id_name]) - result['unmapped']:
                    indices.append((polySeqModel.index(ps1), polySeqRst.index(ps2)))

        mat.append(cost)

    chainAssign = []

    for row, col in indices:

        if mat[row][col] >= 0:

            has_row = has_col = False
            for _row, _col in indices:
                if mat[_row][_col] < 0:
                    if _row == row:
                        has_row = True
                    if _col == col:
                        has_col = True

            if has_row and has_col:
                continue

            _cif_chains = []
            for _row, _col in indices:
                if col == _col:
                    _cif_chains.append(polySeqModel[_row][chain_id_name])

            if len(_cif_chains) > 1:
                chain_id2 = polySeqRst[col]['chain_id']

                warnings.append(f"[Concatenated sequence] The chain ID {chain_id2!r} of the sequences in {_a_mr_format_name} file "
                                f"will be re-assigned to the chain IDs {_cif_chains} in the coordinates during biocuration.")

        chain_id = polySeqModel[row][chain_id_name]
        chain_id2 = polySeqRst[col]['chain_id']

        result = next(seq_align for seq_align in seqAlign
                      if seq_align['ref_chain_id'] == chain_id and seq_align['test_chain_id'] == chain_id2)

        if result['matched'] == 0:
            continue

        if not fileType.startswith('nm-aux') and result['conflict'] > 0\
           and result['sequence_coverage'] < LOW_SEQ_COVERAGE < float(result['conflict']) / float(result['matched']):
            continue

        ca = {'ref_chain_id': chain_id, 'test_chain_id': chain_id2, 'length': result['length'],
              'matched': result['matched'], 'conflict': result['conflict'], 'unmapped': result['unmapped'],
              'sequence_coverage': result['sequence_coverage']}

        ps1 = next(ps1 for ps1 in polySeqModel if ps1[chain_id_name] == chain_id)
        ps2 = next(ps2 for ps2 in polySeqRst if ps2['chain_id'] == chain_id2)

        pA.setReferenceSequence(ps1['comp_id'], 'REF' + chain_id)
        pA.addTestSequence(ps2['comp_id'], chain_id)
        pA.doAlign()

        myAlign = pA.getAlignment(chain_id)

        length = len(myAlign)

        _matched, unmapped, conflict, offset_1, offset_2 = getScoreOfSeqAlign(myAlign)

        _ps1 = ps1 if offset_1 == 0 else fillBlankCompIdWithOffset(ps1, offset_1, seqIdName=seq_id_name)
        _ps2 = ps2 if offset_2 == 0 else fillBlankCompIdWithOffset(ps2, offset_2)

        if conflict == 0:
            if hasLargeInnerSeqGap(_ps2) and not hasLargeInnerSeqGap(_ps1):
                _ps2 = fillInnerBlankCompId(_ps2)

        _seq_id_name = 'auth_seq_id' if 'auth_seq_id' in _ps1 else 'seq_id'

        if conflict > 0 and hasLargeSeqGap(_ps1, _ps2, seqIdName1=_seq_id_name):
            __ps1, __ps2 = beautifyPolySeq(_ps1, _ps2, seqIdName1=_seq_id_name)
            _ps1 = __ps1
            _ps2 = __ps2

            pA.setReferenceSequence(_ps1['comp_id'], 'REF' + chain_id)
            pA.addTestSequence(_ps2['comp_id'], chain_id)
            pA.doAlign()

            myAlign = pA.getAlignment(chain_id)

            length = len(myAlign)

            _matched, unmapped, _conflict, _, _ = getScoreOfSeqAlign(myAlign)

            if _conflict == 0 and len(__ps2['comp_id']) - len(ps2['comp_id']) == conflict:
                result['conflict'] = 0
                ps2 = __ps2

        if result['unmapped'] > 0 or result['conflict'] > 0:

            aligned = [True] * length
            seq_id1, seq_id2 = [], []

            j = 0
            for i in range(length):
                if str(myAlign[i][0]) != '.' and j < len(ps1[seq_id_name]):
                    seq_id1.append(ps1[seq_id_name][j])
                    j += 1
                else:
                    seq_id1.append(None)

            j = 0
            for i in range(length):
                if str(myAlign[i][1]) != '.' and j < len(ps2['seq_id']):
                    seq_id2.append(ps2['seq_id'][j])
                    j += 1
                else:
                    seq_id2.append(None)

            for i in range(length):
                myPr = myAlign[i]
                myPr0 = str(myPr[0])
                myPr1 = str(myPr[1])
                if myPr0 == '.' or myPr1 == '.':
                    aligned[i] = False
                elif myPr0 != myPr1:
                    pass
                else:
                    break

            for i in reversed(range(length)):
                myPr = myAlign[i]
                myPr0 = str(myPr[0])
                myPr1 = str(myPr[1])
                if myPr0 == '.' or myPr1 == '.':
                    aligned[i] = False
                elif myPr0 != myPr1:
                    pass
                else:
                    break

            _conflicts = 0

            for i in range(length):
                myPr = myAlign[i]
                if myPr[0] == myPr[1]:
                    continue

                cif_comp_id = str(myPr[0])
                mr_comp_id = str(myPr[1])

                if mr_comp_id == '.' and cif_comp_id != '.':
                    pass

                elif mr_comp_id != cif_comp_id and aligned[i]:
                    _conflicts += 1

            if fileType.startswith('nm-aux') and _conflicts > ca['unmapped'] and ca['sequence_coverage'] < MIN_SEQ_COVERAGE_W_CONFLICT:
                continue

            if _conflicts + offset_1 > _matched and ca['sequence_coverage'] < LOW_SEQ_COVERAGE:  # DAOTHER-7825 (2lyw)
                continue

            unmapped, conflict = [], []

            for i in range(length):
                myPr = myAlign[i]
                if myPr[0] == myPr[1]:
                    continue

                cif_comp_id = str(myPr[0])
                mr_comp_id = str(myPr[1])

                if mr_comp_id == '.' and cif_comp_id != '.':

                    unmapped.append({'ref_seq_id': seq_id1[i], 'ref_comp_id': cif_comp_id})

                elif mr_comp_id != cif_comp_id and aligned[i]:

                    comp_ids = [comp_id for seq_id, comp_id in zip(ps1[_seq_id_name], ps1['comp_id']) if seq_id == seq_id1[i]]

                    if mr_comp_id in comp_ids:
                        continue

                    conflict.append({'ref_seq_id': seq_id1[i], 'ref_comp_id': cif_comp_id,
                                     'test_seq_id': seq_id2[i], 'test_comp_id': mr_comp_id})

                    cif_seq_code = f"{chain_id}:{seq_id1[i]}:{cif_comp_id}"
                    if cif_comp_id == '.':
                        cif_seq_code += ', insertion error'
                    mr_seq_code = f"{chain_id2}:{seq_id2[i]}:{mr_comp_id}"
                    if mr_comp_id == '.':
                        mr_seq_code += ', insertion error'

                    if cif_comp_id != '.':

                        if not ccU.updateChemCompDict(cif_comp_id):
                            continue

                        if ccU.lastChemCompDict['_chem_comp.pdbx_release_status'] != 'REL':
                            continue

                        if getOneLetterCodeCan(cif_comp_id) == 'X':
                            continue

                    warnings.append(f"[Sequence mismatch] Sequence alignment error between the coordinate ({cif_seq_code}) "
                                    f"and {_a_mr_format_name} data ({mr_seq_code}). "
                                    "Please verify the two sequences and re-upload the correct file(s) if required.")

            if len(unmapped) > 0:
                ca['unmapped_sequence'] = unmapped

            if len(conflict) > 0:
                ca['conflict_sequence'] = conflict
                ca['conflict'] = len(conflict)
                ca['unmapped'] = ca['unmapped'] - len(conflict)
                if ca['unmapped'] < 0:
                    ca['conflict'] -= ca['unmapped']
                    ca['unmapped'] = 0

                result['conflict'] = ca['conflict']
                result['unmapped'] = ca['unmapped']

        chainAssign.append(ca)

    if len(chainAssign) > 0 and len(polySeqModel) > 1:

        if any(ps for ps in polySeqModel if 'identical_auth_chain_id' in ps):

            _chainAssign = copy.copy(chainAssign)

            for ca in _chainAssign:

                if ca['conflict'] > 0:
                    continue

                chain_id = ca['ref_chain_id']

                try:
                    identity = next(ps['identical_auth_chain_id'] for ps in polySeqModel
                                    if ps['auth_chain_id'] == chain_id and 'identical_auth_chain_id' in ps)

                    for chain_id in identity:

                        if not any(_ca for _ca in chainAssign if _ca['ref_chain_id'] == chain_id):
                            _ca = copy.copy(ca)
                            _ca['ref_chain_id'] = chain_id
                            chainAssign.append(_ca)

                            sa = next(sa for sa in seqAlign if sa['ref_chain_id'] == ca['ref_chain_id'])
                            _sa = copy.copy(sa)
                            _sa['ref_chain_id'] = chain_id
                            seqAlign.append(_sa)

                except StopIteration:
                    pass

    return chainAssign, warnings


def trimSequenceAlignment(seqAlign: List[dict], chainAssign: List[dict]):
    """ Trim ineffective sequence alignments.
    """

    if None in (seqAlign, chainAssign):
        return

    ineffSeqAlignIdx = list(range(len(seqAlign) - 1, -1, -1))

    for ca in chainAssign:
        ref_chain_id = ca['ref_chain_id']
        test_chain_id = ca['test_chain_id']

        effSeqAlignIdx = next((idx for idx, seq_align in enumerate(seqAlign)
                              if seq_align['ref_chain_id'] == ref_chain_id
                              and seq_align['test_chain_id'] == test_chain_id), None)

        if effSeqAlignIdx is not None and effSeqAlignIdx in ineffSeqAlignIdx:
            ineffSeqAlignIdx.remove(effSeqAlignIdx)

    if len(ineffSeqAlignIdx) > 0:
        for idx in ineffSeqAlignIdx:
            del seqAlign[idx]


def retrieveAtomIdentFromMRMap(ccU, mrAtomNameMapping: List[dict], seqId: int, compId: str, atomId: str,
                               cifCompId: Optional[str] = None, coordAtomSite: Optional[dict] = None,
                               ignoreSeqId: bool = False) -> Tuple[int, str, str]:
    """ Retrieve atom identifiers from atom name mapping of public MR file.
    """

    if atomId.endswith('"'):
        atomId = atomId[:-1] + "''"
    lenAtomId = len(atomId)

    elemName = atomId[0]

    mapping = [item for item in mrAtomNameMapping
               if (item['original_seq_id'] == seqId or ignoreSeqId)
               and (compId in (item['original_comp_id'], item['auth_comp_id'])
                    or cifCompId is not None and cifCompId == item['auth_comp_id'])]

    if len(mapping) == 0:
        return seqId, compId, atomId

    if atomId.startswith('QQ') and lenAtomId > 2 and atomId not in ('QQR', 'QQM'):
        item = next((item for item in mapping
                     if item['original_atom_id'] in ('H' + atomId[2:] + '22',
                                                     '2H' + atomId[2:] + '2')), None)
        if item is not None:
            _branch = [c for c in ccU.getMethylAtoms(compId if cifCompId is None else cifCompId) if c[0] == 'C']
            if len(_branch) > 1:
                __branch = [cca[ccU.ccaAtomId] for cca in ccU.lastAtomList
                            if cca[ccU.ccaTypeSymbol] in ('C', 'N')
                            and cca[ccU.ccaLeavingAtomFlag] == 'N']
                total = 0
                for k in __branch:
                    c = ccU.getBondedAtoms(compId if cifCompId is None else cifCompId, k, exclProton=True)
                    if len([b for b in _branch if b in c]) == 2:
                        total += 1
                if total == 1:
                    return item['auth_seq_id'], item['auth_comp_id'], 'QQM'

    if atomId.startswith('QQ') and atomId not in ('QQR', 'QQM'):
        _branch = [c for c in ccU.getMethylAtoms(compId if cifCompId is None else cifCompId) if c[0] == 'C']
        if len(_branch) > 1:
            __branch = [cca[ccU.ccaAtomId] for cca in ccU.lastAtomList
                        if cca[ccU.ccaTypeSymbol] in ('C', 'N')
                        and cca[ccU.ccaLeavingAtomFlag] == 'N']
            total = 0
            for k in __branch:
                c = ccU.getBondedAtoms(compId if cifCompId is None else cifCompId, k, exclProton=True)
                if len([b for b in _branch if b in c]) == 2:
                    total += 1
            if total == 1:
                return seqId, compId, 'QQM'

    if elemName in ('Q', 'M'):

        item = next((item for item in mapping
                     if item['original_atom_id'] in ('H' + atomId[1:] + '2', '2H' + atomId[1:])), None)

        if item is not None:

            if coordAtomSite is not None and item['auth_atom_id'] not in coordAtomSite['atom_id']:
                return seqId, compId, atomId

            authAtomId = item['auth_atom_id'][:-1] + '%' if item['auth_atom_id'][0].isalpha() else '%' + item['auth_atom_id'][1:]

            if not authAtomId.startswith('%'):
                methyl = ccU.getMethylAtoms(item['auth_comp_id'])
                if item['auth_atom_id'] in methyl:
                    authAtomId = 'M' + authAtomId[1:-1]

            return item['auth_seq_id'], item['auth_comp_id'], authAtomId

        if lenAtomId > 1:

            item = next((item for item in mapping
                         if item['original_atom_id'] == '2H' + atomId[1:]), None)

            if item is not None:

                if coordAtomSite is not None and item['auth_atom_id'] not in coordAtomSite['atom_id']:
                    return seqId, compId, atomId

                authAtomId = item['auth_atom_id'][:-1] + '%' if item['auth_atom_id'][0].isalpha() else '%' + item['auth_atom_id'][1:]

                if not authAtomId.startswith('%'):
                    methyl = ccU.getMethylAtoms(item['auth_comp_id'])
                    if item['auth_atom_id'] in methyl:
                        authAtomId = 'M' + authAtomId[1:-1]

                return item['auth_seq_id'], item['auth_comp_id'], authAtomId

            if atomId[1] == 'H' and lenAtomId > 2:

                item = next((item for item in mapping if item['original_atom_id'] == atomId[1:] + '2'), None)

                if item is not None:

                    if coordAtomSite is not None and item['auth_atom_id'] not in coordAtomSite['atom_id']:
                        return seqId, compId, atomId

                    authAtomId = item['auth_atom_id'][:lenAtomId] + '%'
                    methyl = ccU.getMethylAtoms(item['auth_comp_id'])
                    if item['auth_atom_id'] in methyl:
                        authAtomId = 'M' + authAtomId[1:-1]

                    return item['auth_seq_id'], item['auth_comp_id'], authAtomId

    if elemName == 'H' and atomId[-1] in ('1', '2', '3'):

        item = next((item for item in mapping
                     if item['original_atom_id'] == atomId), None)

        if item is None:

            _atomId = atomId[-1] + atomId[:-1]

            item = next((item for item in mapping
                         if item['original_atom_id'] == _atomId), None)

            if item is not None:

                if coordAtomSite is not None and item['auth_atom_id'] not in coordAtomSite['atom_id']:
                    return seqId, compId, atomId

                return item['auth_seq_id'], item['auth_comp_id'], item['auth_atom_id']

            if atomId[-1] == '1':
                _atomId = '3' + atomId[:-1]

                item = next((item for item in mapping
                             if item['original_atom_id'] == _atomId), None)

                if item is not None:

                    if coordAtomSite is not None and item['auth_atom_id'] not in coordAtomSite['atom_id']:
                        return seqId, compId, atomId

                    return item['auth_seq_id'], item['auth_comp_id'], item['auth_atom_id']

    if elemName == 'H' and atomId.endswith('A'):

        item = next((item for item in mapping
                     if item['original_atom_id'] == atomId[:-1]), None)

        if item is not None:

            _atomId_ = item['auth_atom_id']

            if coordAtomSite is not None and _atomId_ not in coordAtomSite['atom_id']:

                total = 0
                for _atomId in coordAtomSite['atom_id']:
                    if _atomId.startswith(_atomId_):
                        total += 1

                if total == 1:
                    return item['auth_seq_id'], item['auth_comp_id'], \
                        next(_atomId for _atomId in coordAtomSite['atom_id'] if _atomId.startswith(_atomId_))

                return seqId, compId, atomId

            return item['auth_seq_id'], item['auth_comp_id'], _atomId_

    if elemName == 'H' or (elemName in ('1', '2', '3') and lenAtomId > 1 and atomId[1] == 'H'):

        item = next((item for item in mapping
                     if item['original_atom_id'] == atomId), None)

        if item is None:
            item = next((item for item in mapping
                         if item['original_atom_id'] == atomId[1:] + atomId[0]), None)

        if item is not None:

            _atomId_ = item['auth_atom_id']

            if coordAtomSite is not None and _atomId_ not in coordAtomSite['atom_id']:

                total = 0
                for _atomId in coordAtomSite['atom_id']:
                    if _atomId.startswith(_atomId_):
                        total += 1

                if total == 1:
                    return item['auth_seq_id'], item['auth_comp_id'], \
                        next(_atomId for _atomId in coordAtomSite['atom_id'] if _atomId.startswith(_atomId_))

                return seqId, compId, atomId

            return item['auth_seq_id'], item['auth_comp_id'], _atomId_

        if coordAtomSite is not None and atomId not in coordAtomSite['atom_id']:

            total = 0
            for _atomId in coordAtomSite['atom_id']:
                if _atomId.startswith(atomId):
                    total += 1

            if total == 1:
                return mapping[0]['auth_seq_id'], mapping[0]['auth_comp_id'], \
                    next(_atomId for _atomId in coordAtomSite['atom_id'] if _atomId.startswith(atomId))

        item = next((item for item in mapping
                     if item['original_atom_id'] == atomId + '2'), None)

        if item is not None and item['auth_atom_id'][-1] == '2':
            return item['auth_seq_id'], item['auth_comp_id'], item['auth_atom_id'][:-1] + '%'

        item = next((item for item in mapping
                     if item['original_atom_id'] == '2' + atomId), None)

        if item is not None and item['auth_atom_id'][-1] == '2':
            return item['auth_seq_id'], item['auth_comp_id'], item['auth_atom_id'][:-1] + '%'

        return seqId, compId, atomId

    if elemName not in protonBeginCode:

        item = next((item for item in mapping
                     if item['original_atom_id'] == atomId), None)

        if item is not None:
            return item['auth_seq_id'], item['auth_comp_id'], item['auth_atom_id']

        if coordAtomSite is not None and atomId in coordAtomSite['atom_id']:
            return seqId, compId, atomId

    _atomId = 'H' + atomId[1:]

    item = next((item for item in mapping
                 if item['original_atom_id'] == _atomId), None)

    if item is not None:

        _atomId_ = elemName + item['auth_atom_id'][1:]

        if coordAtomSite is not None:

            for hvyAtomId in ccU.getBondedAtoms(cifCompId, item['auth_atom_id'], exclProton=True):

                if hvyAtomId in coordAtomSite['atom_id']:
                    return item['auth_seq_id'], item['auth_comp_id'], hvyAtomId

            if _atomId not in coordAtomSite['atom_id']:

                total = 0
                for __atomId in coordAtomSite['atom_id']:
                    if __atomId.startswith(_atomId_):
                        total += 1

                if total == 1:
                    _atomId = next(_atomId for _atomId in coordAtomSite['atom_id'] if _atomId.startswith(_atomId_))
                    return item['auth_seq_id'], item['auth_comp_id'], _atomId

                return seqId, compId, atomId

        return item['auth_seq_id'], item['auth_comp_id'], _atomId_

    _atomId = 'H' + atomId[1:] + '2'

    item = next((item for item in mapping
                 if item['original_atom_id'] == _atomId), None)

    if item is not None:

        _atomId_ = elemName + item['auth_atom_id'][1:-1]

        if coordAtomSite is not None:

            for hvyAtomId in ccU.getBondedAtoms(cifCompId, item['auth_atom_id'], exclProton=True):

                if hvyAtomId in coordAtomSite['atom_id']:
                    return item['auth_seq_id'], item['auth_comp_id'], hvyAtomId

            if _atomId not in coordAtomSite['atom_id']:

                total = 0
                for __atomId in coordAtomSite['atom_id']:
                    if __atomId.startswith(_atomId_):
                        total += 1

                if total == 1:
                    _atomId = next(_atomId for _atomId in coordAtomSite['atom_id'] if _atomId.startswith(_atomId_))
                    return item['auth_seq_id'], item['auth_comp_id'], _atomId

                return seqId, compId, atomId

        return item['auth_seq_id'], item['auth_comp_id'], _atomId_

    if atomId[-1] in ('1', '2'):

        order = int(atomId[-1]) - 1
        _atomId = 'H' + atomId[1:-1]

        item = next((item for item in mapping
                     if item['original_atom_id'] == _atomId), None)

        if item is not None:

            _atomId_ = elemName + item['auth_atom_id'][1:]

            if coordAtomSite is not None:
                candidate = sorted(__atomId for __atomId in coordAtomSite['atom_id'] if __atomId.startswith(_atomId_))

                if order < len(candidate):
                    return item['auth_seq_id'], item['auth_comp_id'], candidate[order]

        elif coordAtomSite is not None and atomId not in coordAtomSite['atom_id']:

            _atomId_ = atomId[:-1]

            candidate = sorted(__atomId for __atomId in coordAtomSite['atom_id'] if __atomId.startswith(_atomId_))

            if order < len(candidate):
                if item is not None:
                    return item['auth_seq_id'], item['auth_comp_id'], candidate[order]

                return seqId, compId, candidate[order]

    if lenAtomId == 1:

        if coordAtomSite is not None and atomId not in coordAtomSite['atom_id']:

            total = 0
            for __atomId in coordAtomSite['atom_id']:
                if __atomId.startswith(atomId):
                    total += 1

            if total == 1:
                _atomId = next(_atomId for _atomId in coordAtomSite['atom_id'] if _atomId.startswith(atomId))
                if item is not None:
                    return item['auth_seq_id'], item['auth_comp_id'], _atomId

                return seqId, compId, _atomId

    return seqId, compId, atomId


def retrieveAtomIdFromMRMap(ccU, mrAtomNameMapping: List[dict], cifSeqId: int, cifCompId: str, atomId: str,
                            coordAtomSite: Optional[dict] = None, ignoreSeqId: bool = False) -> str:
    """ Retrieve atom_id from atom name mapping of public MR file.
    """

    if atomId.endswith('"'):
        atomId = atomId[:-1] + "''"
    lenAtomId = len(atomId)

    elemName = atomId[0]

    mapping = [item for item in mrAtomNameMapping
               if (item['auth_seq_id'] == cifSeqId or ignoreSeqId)
               and cifCompId in (item['auth_comp_id'], item['original_comp_id'])]

    if len(mapping) == 0:
        return atomId

    if any(item for item in mapping
           if item['original_atom_id'] is not None
           and len(item['original_atom_id']) > 1
           and item['original_atom_id'][0].isdigit()
           and item['original_atom_id'][1] == 'H'):
        _mapping = copy.deepcopy(mapping)
        for item in mapping:
            if item['original_atom_id'] is not None\
               and len(item['original_atom_id']) > 1\
               and item['original_atom_id'][0].isdigit()\
               and item['original_atom_id'][1] == 'H':
                _item = copy.copy(item)
                _item['original_atom_id'] = item['original_atom_id'][1:] + item['original_atom_id'][0]
                _mapping.append(_item)
        mapping = _mapping

    if atomId.startswith('QQ') and lenAtomId > 2 and atomId not in ('QQR', 'QQM'):
        item = next((item for item in mapping
                     if item['original_atom_id'] in ('H' + atomId[2:] + '22',
                                                     '2H' + atomId[2:] + '2')), None)
        if item is not None:
            _branch = [c for c in ccU.getMethylAtoms(cifCompId) if c[0] == 'C']
            if len(_branch) > 1:
                __branch = [cca[ccU.ccaAtomId] for cca in ccU.lastAtomList
                            if cca[ccU.ccaTypeSymbol] in ('C', 'N')
                            and cca[ccU.ccaLeavingAtomFlag] == 'N']
                total = 0
                for k in __branch:
                    c = ccU.getBondedAtoms(cifCompId, k, exclProton=True)
                    if len([b for b in _branch if b in c]) == 2:
                        total += 1
                if total == 1:
                    return 'QQM'

    if elemName in ('Q', 'M'):

        item = next((item for item in mapping
                     if item['original_atom_id'] in ('H' + atomId[1:] + '2', '2H' + atomId[1:])), None)

        if item is not None:

            if coordAtomSite is not None and item['auth_atom_id'] not in coordAtomSite['atom_id']:
                return atomId

            authAtomId = item['auth_atom_id'][:-1] + '%' if item['auth_atom_id'][0].isalpha() else '%' + item['auth_atom_id'][1:]

            if not authAtomId.startswith('%'):
                methyl = ccU.getMethylAtoms(item['auth_comp_id'])
                if item['auth_atom_id'] in methyl:
                    authAtomId = 'M' + authAtomId[1:-1]

            return authAtomId

        if lenAtomId > 1:

            item = next((item for item in mapping
                         if item['original_atom_id'] == '2H' + atomId[1:]), None)

            if item is not None:

                if coordAtomSite is not None and item['auth_atom_id'] not in coordAtomSite['atom_id']:
                    return atomId

                authAtomId = item['auth_atom_id'][:-1] + '%' if item['auth_atom_id'][0].isalpha() else '%' + item['auth_atom_id'][1:]

                if not authAtomId.startswith('%'):
                    methyl = ccU.getMethylAtoms(item['auth_comp_id'])
                    if item['auth_atom_id'] in methyl:
                        authAtomId = 'M' + authAtomId[1:-1]

                return authAtomId

            if atomId[1] == 'H' and lenAtomId > 2:

                item = next((item for item in mapping if item['original_atom_id'] == atomId[1:] + '2'), None)

                if item is not None:

                    if coordAtomSite is not None and item['auth_atom_id'] not in coordAtomSite['atom_id']:
                        return atomId

                    authAtomId = item['auth_atom_id'][:lenAtomId] + '%'

                    methyl = ccU.getMethylAtoms(item['auth_comp_id'])
                    if item['auth_atom_id'] in methyl:
                        authAtomId = 'M' + authAtomId[1:-1]

                    return authAtomId

    if elemName == 'H' and atomId[-1] in ('1', '2', '3'):

        item = next((item for item in mapping
                     if item['original_atom_id'] == atomId), None)

        if item is None:

            _atomId = atomId[-1] + atomId[:-1]

            item = next((item for item in mapping
                         if item['original_atom_id'] == _atomId), None)

            if item is not None:

                if coordAtomSite is not None and item['auth_atom_id'] not in coordAtomSite['atom_id']:
                    return atomId

                return item['auth_atom_id']

            if atomId[-1] == '1':
                _atomId = '3' + atomId[:-1]

                item = next((item for item in mapping
                             if item['original_atom_id'] == _atomId), None)

                if item is not None:

                    if coordAtomSite is not None and item['auth_atom_id'] not in coordAtomSite['atom_id']:
                        return atomId

                    return item['auth_atom_id']

    if elemName == 'H' and atomId.endswith('A'):

        item = next((item for item in mapping
                     if item['original_atom_id'] == atomId[:-1]), None)

        if item is not None:

            _atomId_ = item['auth_atom_id']

            if coordAtomSite is not None and _atomId_ not in coordAtomSite['atom_id']:

                total = 0
                for _atomId in coordAtomSite['atom_id']:
                    if _atomId.startswith(_atomId_):
                        total += 1

                if total == 1:
                    return next(_atomId for _atomId in coordAtomSite['atom_id'] if _atomId.startswith(_atomId_))

                return atomId

            return _atomId_

    if elemName == 'H' or (elemName in ('1', '2', '3') and lenAtomId > 1 and atomId[1] == 'H'):

        item = next((item for item in mapping
                     if item['original_atom_id'] == atomId), None)

        if item is None:
            item = next((item for item in mapping
                         if item['original_atom_id'] == atomId[1:] + atomId[0]), None)

        if item is not None:

            _atomId_ = item['auth_atom_id']

            if coordAtomSite is not None and _atomId_ not in coordAtomSite['atom_id']:

                total = 0
                for _atomId in coordAtomSite['atom_id']:
                    if _atomId.startswith(_atomId_):
                        total += 1

                if total == 1:
                    return next(_atomId for _atomId in coordAtomSite['atom_id'] if _atomId.startswith(_atomId_))

                return atomId

            return _atomId_

        if coordAtomSite is not None and atomId not in coordAtomSite['atom_id']:

            total = 0
            for _atomId in coordAtomSite['atom_id']:
                if _atomId.startswith(atomId):
                    total += 1

            if total == 1:
                return next(_atomId for _atomId in coordAtomSite['atom_id'] if _atomId.startswith(atomId))

        item = next((item for item in mapping
                     if item['original_atom_id'] == atomId + '2'), None)

        if item is not None and item['auth_atom_id'][-1] == '2':
            return item['auth_atom_id'][:-1] + '%'

        item = next((item for item in mapping
                     if item['original_atom_id'] == '2' + atomId), None)

        if item is not None and item['auth_atom_id'][-1] == '2':
            return item['auth_atom_id'][:-1] + '%'

        return atomId

    if elemName not in protonBeginCode:

        item = next((item for item in mapping
                     if item['original_atom_id'] == atomId), None)

        if item is not None:
            return item['auth_atom_id']

        if coordAtomSite is not None and atomId in coordAtomSite['atom_id']:
            return atomId

    _atomId = 'H' + atomId[1:]

    item = next((item for item in mapping
                 if item['original_atom_id'] == _atomId), None)

    if item is not None:
        _atomId_ = elemName + item['auth_atom_id'][1:]

        if coordAtomSite is not None:

            for hvyAtomId in ccU.getBondedAtoms(cifCompId, item['auth_atom_id'], exclProton=True):

                if hvyAtomId in coordAtomSite['atom_id']:
                    return hvyAtomId

            if _atomId_ not in coordAtomSite['atom_id']:

                total = 0
                for __atomId in coordAtomSite['atom_id']:
                    if __atomId.startswith(_atomId_):
                        total += 1

                    if total == 1:
                        return next(_atomId for _atomId in coordAtomSite['atom_id'] if _atomId.startswith(_atomId_))

                return atomId

        return _atomId_

    _atomId = 'H' + atomId[1:] + '2'

    item = next((item for item in mapping
                 if item['original_atom_id'] == _atomId), None)

    if item is not None:
        _atomId_ = elemName + item['auth_atom_id'][1:-1]

        if coordAtomSite is not None:

            for hvyAtomId in ccU.getBondedAtoms(cifCompId, item['auth_atom_id'], exclProton=True):

                if hvyAtomId in coordAtomSite['atom_id']:
                    return hvyAtomId

            if _atomId not in coordAtomSite['atom_id']:

                total = 0
                for __atomId in coordAtomSite['atom_id']:
                    if __atomId.startswith(_atomId_):
                        total += 1

                    if total == 1:
                        return next(_atomId for _atomId in coordAtomSite['atom_id'] if _atomId.startswith(_atomId_))

                return atomId

        return _atomId_

    if atomId[-1] in ('1', '2'):

        order = int(atomId[-1]) - 1
        _atomId = 'H' + atomId[1:-1]

        item = next((item for item in mapping
                     if item['original_atom_id'] == _atomId), None)

        if item is not None:

            _atomId_ = elemName + item['auth_atom_id'][1:]

            if coordAtomSite is not None:
                candidate = sorted(__atomId for __atomId in coordAtomSite['atom_id'] if __atomId.startswith(_atomId_))

                if order < len(candidate):
                    return candidate[order]

        elif coordAtomSite is not None and atomId not in coordAtomSite['atom_id']:

            _atomId_ = atomId[:-1]

            candidate = sorted(__atomId for __atomId in coordAtomSite['atom_id'] if __atomId.startswith(_atomId_))

            if order < len(candidate):
                return candidate[order]

    if lenAtomId == 1:

        if coordAtomSite is not None and atomId not in coordAtomSite['atom_id']:

            total = 0
            for __atomId in coordAtomSite['atom_id']:
                if __atomId.startswith(atomId):
                    total += 1

            if total == 1:
                _atomId = next(_atomId for _atomId in coordAtomSite['atom_id'] if _atomId.startswith(atomId))
                return _atomId

    return atomId


def retrieveRemappedSeqId(seqIdRemap: List[dict], chainId: str, seqId: int, compId: Optional[str] = None
                          ) -> Tuple[Optional[str], Optional[int]]:
    """ Retrieve seq_id from mapping dictionary based on sequence alignments.
    """

    try:

        if compId is None:

            if chainId is None:
                remap = next(remap for remap in seqIdRemap
                             if seqId in remap['seq_id_dict'])
            else:
                remap = next(remap for remap in seqIdRemap
                             if seqId in remap['seq_id_dict'] and remap['chain_id'] == chainId)

        else:

            if chainId is None:
                remap = next(remap for remap in seqIdRemap
                             if seqId in remap['seq_id_dict'] and compId in remap['comp_id_set'])
            else:
                remap = next(remap for remap in seqIdRemap
                             if seqId in remap['seq_id_dict'] and remap['chain_id'] == chainId and compId in remap['comp_id_set'])

        return remap['chain_id'], remap['seq_id_dict'][seqId]

    except StopIteration:
        return None, None


def retrieveRemappedSeqIdAndCompId(seqIdRemap: List[dict], chainId: str, seqId: int, compId: Optional[str] = None
                                   ) -> Tuple[Optional[str], Optional[int], Optional[str]]:
    """ Retrieve seq_id from mapping dictionary based on sequence alignments.
    """

    try:

        if compId is None:

            if chainId is None:
                remap = next(remap for remap in seqIdRemap
                             if seqId in remap['seq_id_dict'] and seqId in remap['comp_id_dict'])
            else:
                remap = next(remap for remap in seqIdRemap
                             if seqId in remap['seq_id_dict'] and seqId in remap['comp_id_dict']
                             and remap['chain_id'] == chainId)

        else:

            if chainId is None:
                remap = next(remap for remap in seqIdRemap
                             if seqId in remap['seq_id_dict'] and seqId in remap['comp_id_dict']
                             and compId in remap['comp_id_dict'].values())
            else:
                remap = next(remap for remap in seqIdRemap
                             if seqId in remap['seq_id_dict'] and seqId in remap['comp_id_dict']
                             and remap['chain_id'] == chainId and compId in remap['comp_id_dict'].values())

        return remap['chain_id'], remap['seq_id_dict'][seqId], remap['comp_id_dict'][seqId]

    except StopIteration:
        return None, None, None


def splitPolySeqRstForMultimers(pA, polySeqModel: List[dict], polySeqRst: List[dict], chainAssign: List[dict]
                                ) -> Tuple[Optional[List[dict]], Optional[List[dict]]]:
    """ Split polymer sequence of the current MR file for multimers.
    """

    if None in (polySeqModel, polySeqRst, chainAssign):
        return None, None

    target_chain_ids = {}
    for ca in chainAssign:
        if ca['conflict'] == 0 and ca['unmapped'] > 0:
            ref_chain_id = ca['ref_chain_id']
            test_chain_id = ca['test_chain_id']
            if test_chain_id not in target_chain_ids:
                target_chain_ids[test_chain_id] = []
            target_chain_ids[test_chain_id].append(ref_chain_id)
        elif ca['conflict'] > 0 and ca['unmapped'] > 0:
            ref_chain_id = ca['ref_chain_id']
            ref_ps = next(ps for ps in polySeqModel if ps['auth_chain_id'] == ref_chain_id)
            len_ident_chain_id = 0 if 'identical_chain_id' not in ref_ps else len(ref_ps['identical_chain_id'])
            if ca['conflict'] <= len_ident_chain_id // 5:
                test_chain_id = ca['test_chain_id']
                if test_chain_id not in target_chain_ids:
                    target_chain_ids[test_chain_id] = []
                target_chain_ids[test_chain_id].append(ref_chain_id)

    if len(target_chain_ids) == 0:
        return None, None

    split = False

    _polySeqRst = copy.copy(polySeqRst)
    _chainIdMapping = {}

    for test_chain_id, ref_chain_ids in target_chain_ids.items():

        total_gaps = len(ref_chain_ids) - 1

        if total_gaps == 0:
            continue

        len_ref_ps = []

        for ref_chain_id in ref_chain_ids:
            ref_ps = next(ps for ps in polySeqModel if ps['auth_chain_id'] == ref_chain_id)
            len_ref_ps.append(len(ref_ps['seq_id']))

        sum_len_ref_ps = sum(len_ref_ps)

        test_ps = next(ps for ps in _polySeqRst if ps['chain_id'] == test_chain_id)
        len_test_ps = len(test_ps['seq_id'])

        if sum_len_ref_ps < len_test_ps or len_test_ps > sum_len_ref_ps / len(ref_chain_ids):
            half_gap = (len_test_ps - sum_len_ref_ps) // (total_gaps * 2) if sum_len_ref_ps < len_test_ps else 0

            _test_ps = copy.copy(test_ps)

            _polySeqRst.remove(test_ps)

            offset = 0

            for idx, ref_chain_id in enumerate(ref_chain_ids):
                ref_ps = next(ps for ps in polySeqModel if ps['auth_chain_id'] == ref_chain_id)
                half_len_ref_ps = len(ref_ps['seq_id']) // 2

                beg = offset
                end = offset + len(ref_ps['seq_id'])

                if len_test_ps - end < half_len_ref_ps or idx == total_gaps:
                    end = len_test_ps

                if beg >= len(_test_ps['seq_id']):
                    break

                while True:
                    try:
                        if _test_ps['comp_id'][beg] != '.':
                            break
                    except IndexError:
                        return None, None
                    beg += 1
                    if beg == end:
                        return None, None

                end = beg + len(ref_ps['seq_id']) + half_gap

                if len_test_ps - end < half_len_ref_ps or idx == total_gaps:
                    end = len_test_ps

                while True:
                    try:
                        if _test_ps['comp_id'][end - 1] != '.':
                            break
                    except IndexError:
                        return None, None
                    end -= 1
                    if end == beg:
                        return None, None

                _test_ps_ = {'chain_id': ref_chain_id,
                             'seq_id': _test_ps['seq_id'][beg:end],
                             'comp_id': _test_ps['comp_id'][beg:end]}

                pA.setReferenceSequence(ref_ps['comp_id'], 'REF' + ref_chain_id)
                pA.addTestSequence(_test_ps_['comp_id'], ref_chain_id)
                pA.doAlign()

                myAlign = pA.getAlignment(ref_chain_id)

                length = len(myAlign)

                if length == 0:
                    return None, None

                _polySeqRst.append(_test_ps_)

                ref_seq_ids, test_seq_ids = [], []
                idx1 = idx2 = 0
                for i in range(length):
                    myPr = myAlign[i]
                    myPr0 = str(myPr[0])
                    myPr1 = str(myPr[1])
                    if myPr0 != '.':
                        while idx1 < len(ref_ps['auth_seq_id']):
                            if ref_ps['comp_id'][idx1] == myPr0:
                                ref_seq_ids.append(ref_ps['auth_seq_id'][idx1])
                                idx1 += 1
                                break
                            idx1 += 1
                    else:
                        ref_seq_ids.append(None)
                    if myPr1 != '.':
                        while idx2 < len(_test_ps_['seq_id']):
                            if _test_ps_['comp_id'][idx2] == myPr1:
                                test_seq_ids.append(_test_ps_['seq_id'][idx2])
                                idx2 += 1
                                break
                            idx2 += 1
                    else:
                        test_seq_ids.append(None)

                offset_in_chain = next((test_seq_id - ref_seq_id for ref_seq_id, test_seq_id
                                        in zip(ref_seq_ids, test_seq_ids)
                                        if ref_seq_id is not None and test_seq_id is not None), None)
                for ref_seq_id, test_seq_id in zip(ref_seq_ids, test_seq_ids):
                    if ref_seq_id is not None:
                        if test_seq_id is not None:
                            offset_in_chain = test_seq_id - ref_seq_id
                            _chainIdMapping[test_seq_id] = {'chain_id': ref_chain_id,
                                                            'seq_id': ref_seq_id}
                        elif offset_in_chain is not None:
                            test_seq_id = ref_seq_id + offset_in_chain
                            _chainIdMapping[test_seq_id] = {'chain_id': ref_chain_id,
                                                            'seq_id': ref_seq_id}

                split = True

                offset = end + half_gap

    if not split:
        return None, None

    return _polySeqRst, _chainIdMapping


def splitPolySeqRstForExactNoes(pA, polySeqModel: List[dict], polySeqRst: List[dict], chainAssign: List[dict]
                                ) -> Tuple[Optional[List[dict]], Optional[dict], Optional[dict]]:
    """ Split polymer sequence of the current MR file for eNOEs-guided multiple conformers.
    """

    if None in (polySeqModel, polySeqRst, chainAssign):
        return None, None, None

    target_chain_ids = {}
    for ca in chainAssign:
        if ca['conflict'] == 0 and ca['unmapped'] > 0:
            ref_chain_id = ca['ref_chain_id']
            test_chain_id = ca['test_chain_id']
            if test_chain_id not in target_chain_ids:
                target_chain_ids[test_chain_id] = []
            target_chain_ids[test_chain_id].append(ref_chain_id)

    if len(target_chain_ids) == 0:
        return None, None, None

    split = False

    _polySeqRst = copy.copy(polySeqRst)
    _chainIdMapping, _modelChainIdExt = {}, {}

    for test_chain_id, ref_chain_ids in target_chain_ids.items():

        total_gaps = len(ref_chain_ids) - 1

        if total_gaps != 0:
            continue

        ref_chain_id = ref_chain_ids[0]

        ref_ps = next(ps for ps in polySeqModel if ps['auth_chain_id' if 'auth_chain_id' in ps else 'chain_id'] == ref_chain_id)
        len_ref_ps = len(ref_ps['seq_id'])

        test_ps = next(ps for ps in _polySeqRst if ps['chain_id'] == test_chain_id)
        len_test_ps = len(test_ps['seq_id'])

        if 'gap_in_auth_seq' in ref_ps and ref_ps['gap_in_auth_seq']:
            continue

        if len_ref_ps * 1.5 < len_test_ps:

            total_gaps = len_test_ps // len_ref_ps - 1
            if total_gaps == 0:
                total_gaps = 1

            half_gap = (len_test_ps - len_ref_ps * (total_gaps + 1)) // (total_gaps * 2) if len_ref_ps < len_test_ps else 0
            half_gap = max(half_gap, 0)

            _test_ps = copy.copy(test_ps)

            _polySeqRst.remove(test_ps)

            offset = 0

            for idx in range(total_gaps + 1):
                half_len_ref_ps = len_ref_ps // 2

                beg = offset
                end = offset + len_ref_ps

                if len_test_ps - end < half_len_ref_ps or idx == total_gaps:
                    end = len_test_ps

                if beg >= len(_test_ps['seq_id']):
                    break

                while True:
                    try:
                        if _test_ps['comp_id'][beg] != '.':
                            break
                    except IndexError:
                        return None, None, None
                    beg += 1
                    if beg == end:
                        return None, None, None

                end = beg + len(ref_ps['seq_id']) + half_gap

                if len_test_ps - end < half_len_ref_ps or idx == total_gaps:
                    end = len_test_ps

                if idx == 0 and half_gap == 0:

                    pA.setReferenceSequence(ref_ps['comp_id'], 'REF' + ref_chain_id)
                    pA.addTestSequence(test_ps['comp_id'], ref_chain_id)
                    pA.doAlign()

                    myAlign = pA.getAlignment(ref_chain_id)

                    length = len(myAlign)

                    if length == 0:
                        return None, None, None

                    _, _, conflict, _, _ = getScoreOfSeqAlign(myAlign)

                    if conflict > 0:
                        return None, None, None

                    ref_seq_ids, test_seq_ids = [], []
                    idx1 = idx2 = 0
                    for i in range(length):
                        myPr = myAlign[i]
                        myPr0 = str(myPr[0])
                        myPr1 = str(myPr[1])
                        if myPr0 != '.':
                            while idx1 < len(ref_ps['auth_seq_id']):
                                if ref_ps['comp_id'][idx1] == myPr0:
                                    ref_seq_ids.append(ref_ps['auth_seq_id'][idx1])
                                    idx1 += 1
                                    break
                                idx1 += 1
                        else:
                            ref_seq_ids.append(None)
                        if myPr1 != '.':
                            while idx2 < len(test_ps['seq_id']):
                                if test_ps['comp_id'][idx2] == myPr1:
                                    test_seq_ids.append(test_ps['seq_id'][idx2])
                                    idx2 += 1
                                    break
                                idx2 += 1
                        else:
                            test_seq_ids.append(None)

                    _test_seq_id = test_ps['seq_id'][0]
                    for ref_seq_id, test_seq_id in zip(ref_seq_ids, test_seq_ids):
                        if None not in (ref_seq_id, test_seq_id):
                            _test_seq_id = test_seq_id

                    end = test_ps['seq_id'].index(_test_seq_id) + 1

                while True:
                    try:
                        if _test_ps['comp_id'][end - 1] != '.':
                            break
                    except IndexError:
                        return None, None, None
                    end -= 1
                    if end == beg:
                        return None, None, None

                _ref_chain_id = ref_chain_id + (str(idx + 1) if idx > 0 else '')

                _test_ps_ = {'chain_id': _ref_chain_id,
                             'seq_id': _test_ps['seq_id'][beg:end],
                             'comp_id': _test_ps['comp_id'][beg:end]}

                pA.setReferenceSequence(ref_ps['comp_id'], 'REF' + _ref_chain_id)
                pA.addTestSequence(_test_ps_['comp_id'], _ref_chain_id)
                pA.doAlign()

                myAlign = pA.getAlignment(_ref_chain_id)

                length = len(myAlign)

                if length == 0:
                    return None, None, None

                _, _, conflict, _, _ = getScoreOfSeqAlign(myAlign)

                if conflict > 0:
                    return None, None, None

                _polySeqRst.append(_test_ps_)

                ref_seq_ids, test_seq_ids = [], []
                idx1 = idx2 = 0
                for i in range(length):
                    myPr = myAlign[i]
                    myPr0 = str(myPr[0])
                    myPr1 = str(myPr[1])
                    if myPr0 != '.':
                        while idx1 < len(ref_ps['auth_seq_id']):
                            if ref_ps['comp_id'][idx1] == myPr0:
                                ref_seq_ids.append(ref_ps['auth_seq_id'][idx1])
                                idx1 += 1
                                break
                            idx1 += 1
                    else:
                        ref_seq_ids.append(None)
                    if myPr1 != '.':
                        while idx2 < len(_test_ps_['seq_id']):
                            if _test_ps_['comp_id'][idx2] == myPr1:
                                test_seq_ids.append(_test_ps_['seq_id'][idx2])
                                idx2 += 1
                                break
                            idx2 += 1
                    else:
                        test_seq_ids.append(None)

                offset_in_chain = next((test_seq_id - ref_seq_id for ref_seq_id, test_seq_id
                                        in zip(ref_seq_ids, test_seq_ids)
                                        if ref_seq_id is not None and test_seq_id is not None), None)
                for ref_seq_id, test_seq_id in zip(ref_seq_ids, test_seq_ids):
                    if ref_seq_id is not None:
                        if test_seq_id is not None:
                            offset_in_chain = test_seq_id - ref_seq_id
                            _chainIdMapping[test_seq_id] = {'chain_id': _ref_chain_id,
                                                            'seq_id': ref_seq_id}
                        elif offset_in_chain is not None:
                            test_seq_id = ref_seq_id + offset_in_chain
                            _chainIdMapping[test_seq_id] = {'chain_id': _ref_chain_id,
                                                            'seq_id': ref_seq_id}

                if idx > 0:
                    if ref_chain_id not in _modelChainIdExt:
                        _modelChainIdExt[ref_chain_id] = []
                    _modelChainIdExt[ref_chain_id].append(_ref_chain_id)

                split = True

                offset = end + half_gap

    if not split:
        return None, None, None

    return _polySeqRst, _chainIdMapping, _modelChainIdExt


def retrieveRemappedChainId(chainIdRemap: dict, seqId: int) -> Tuple[Optional[str], Optional[int]]:
    """ Retrieve chain_id and seq_id from mapping dictionary based on sequence alignments.
    """

    if seqId not in chainIdRemap:
        return None, None

    remap = chainIdRemap[seqId]

    return remap['chain_id'], remap['seq_id']


def retrieveOriginalSeqIdFromMRMap(chainIdRemap: dict, chainId: str, seqId: int) -> int:
    """ Retrieve the original seq_id from mapping dictionary based on sequence alignments.
    """

    return next((_seqId for _seqId, remap in chainIdRemap.items()
                 if remap['chain_id'] == chainId and remap['seq_id'] == seqId), seqId)


def splitPolySeqRstForNonPoly(ccU, nonPolyModel: List[dict], polySeqRst: List[dict], seqAlign: List[dict], chainAssign: List[dict]
                              ) -> Tuple[Optional[List[dict]], Optional[dict]]:
    """ Split polymer sequence of the current MR file for non-polymer.
    """

    if None in (polySeqRst, nonPolyModel, seqAlign, chainAssign):
        return None, None

    comp_ids = set()
    for np in nonPolyModel:
        for ref_comp_id in np['comp_id']:
            comp_ids.add(ref_comp_id)

    if len(comp_ids) == 0:
        return None, None

    alt_ref_comp_id_dict = {}

    for ref_comp_id in comp_ids:
        if not ccU.updateChemCompDict(ref_comp_id):
            continue

        parent_comp_id = ccU.lastChemCompDict.get('_chem_comp.mon_nstd_parent_comp_id', '?')

        if parent_comp_id not in emptyValue:
            alt_ref_comp_id_dict[parent_comp_id] = ref_comp_id

    comp_ids.clear()

    target_comp_ids = []

    for ca in chainAssign:
        if ca['conflict'] == 0 and ca['unmapped'] > 0:
            ref_chain_id = ca['ref_chain_id']
            test_chain_id = ca['test_chain_id']
            test_ps = next((ps for ps in polySeqRst if ps['chain_id'] == test_chain_id), None)
            if test_ps is None or 'auth_comp_id' not in test_ps:
                continue
            sa = next(sa for sa in seqAlign if sa['ref_chain_id'] == ref_chain_id and sa['test_chain_id'] == test_chain_id)

            for test_seq_id, mid_code in zip_longest(sa['test_seq_id'], sa['mid_code']):
                if test_seq_id in test_ps['seq_id'] and mid_code != '|':
                    test_comp_id, test_auth_comp_id = next((comp_id, auth_comp_id)
                                                           for seq_id, comp_id, auth_comp_id
                                                           in zip(test_ps['seq_id'], test_ps['comp_id'], test_ps['auth_comp_id'])
                                                           if seq_id == test_seq_id)
                    if getOneLetterCodeCan(test_auth_comp_id) == 'X':
                        _test_auth_comp_id = alt_ref_comp_id_dict.get(test_comp_id, test_auth_comp_id)
                        candidate = []
                        for np in nonPolyModel:
                            _ref_chain_id = np['auth_chain_id']
                            seq_id_name = 'auth_seq_id' if 'auth_seq_id' in np else 'seq_id'

                            if _test_auth_comp_id in np['comp_id']:
                                for ref_seq_id, ref_comp_id in zip(np[seq_id_name], np['comp_id']):
                                    if _test_auth_comp_id == ref_comp_id:
                                        candidate.append({'chain_id': _ref_chain_id, 'seq_id': ref_seq_id})

                        if len(candidate) > 0:
                            comp_ids.add(test_auth_comp_id)
                            target_comp_ids.append({'chain_id': test_chain_id,
                                                    'seq_id': test_seq_id,
                                                    'comp_id': test_auth_comp_id,
                                                    'candidate': candidate
                                                    })

    if len(comp_ids) == 0:
        return None, None

    split = False

    _polySeqRst = copy.copy(polySeqRst)
    _nonPolyMapping = {}

    for comp_id in comp_ids:
        _nonPolyMapping[comp_id] = {}

        targets = [target for target in target_comp_ids if target['comp_id'] == comp_id]

        candidates = []
        for target in targets:
            for candidate in target['candidate']:
                if candidate not in candidates:
                    candidates.append(candidate)
            del target['candidate']

        for target, candidate in zip_longest(targets, candidates):

            if None in (target, candidate):
                break

            test_chain_id = target['chain_id']
            test_seq_id = target['seq_id']

            test_ps = next(ps for ps in _polySeqRst if ps['chain_id'] == test_chain_id)

            if test_seq_id in test_ps['seq_id']:

                idx = test_ps['seq_id'].index(test_seq_id)

                del test_ps['seq_id'][idx]
                del test_ps['comp_id'][idx]

                _nonPolyMapping[comp_id][test_seq_id] = {'chain_id': candidate['chain_id'],
                                                         'seq_id': candidate['seq_id'],
                                                         'original_chain_id': test_chain_id}

        if len(_nonPolyMapping[comp_id]) == sum(np['comp_id'].count(comp_id) for np in nonPolyModel):
            split = True
        else:
            del _nonPolyMapping[comp_id]

    if not split:
        return None, None

    stripPolySeqRst(_polySeqRst)

    return _polySeqRst, _nonPolyMapping


def retrieveRemappedNonPoly(nonPolyRemap: dict, nonPoly: Optional[dict], chainId: Optional[str], seqId: int, compId: str) -> Tuple[Optional[str], Optional[int]]:
    """ Retrieve seq_id from mapping dictionary based on sequence alignments.
    """

    if compId not in nonPolyRemap or seqId not in nonPolyRemap[compId]:
        return None, None

    remap = nonPolyRemap[compId][seqId]

    if chainId is None or chainId in (remap['chain_id'], remap['original_chain_id']):
        if nonPoly is not None and compId in nonPoly['comp_id'] and chainId == nonPoly['auth_chain_id']:
            return nonPoly['auth_chain_id'], remap['seq_id']
        return remap['chain_id'], remap['seq_id']

    return None, None


def splitPolySeqRstForBranched(pA, polySeqModel: List[dict], branchedModel: List[dict], polySeqRst: List[dict], chainAssign: List[dict]
                               ) -> Tuple[Optional[List[dict]], Optional[dict]]:
    """ Split polymer sequence of the current MR file for branched polymer.
    """

    if None in (polySeqRst, polySeqModel, branchedModel, chainAssign):
        return None, None

    target_chain_ids = {}
    for ca in chainAssign:
        if ca['conflict'] == 0 and ca['unmapped'] > 0:
            ref_chain_id = ca['ref_chain_id']
            test_chain_id = ca['test_chain_id']

            test_ps = next((ps for ps in polySeqRst if ps['chain_id'] == test_chain_id), None)
            if test_ps is None:
                continue

            for br in branchedModel:
                b_ref_chain_id = br['auth_chain_id']

                pA.setReferenceSequence(br['comp_id'], 'REF' + b_ref_chain_id)
                pA.addTestSequence(test_ps['comp_id'], b_ref_chain_id)
                pA.doAlign()

                myAlign = pA.getAlignment(b_ref_chain_id)

                length = len(myAlign)

                if length == 0:
                    continue

                matched, _, conflict, _, _ = getScoreOfSeqAlign(myAlign)

                if matched == 0 or conflict > 0:
                    continue

                if test_chain_id not in target_chain_ids:
                    target_chain_ids[test_chain_id] = []
                target_chain_ids[test_chain_id].append((ref_chain_id, b_ref_chain_id))

    if len(target_chain_ids) == 0:
        return None, None

    split = False

    _polySeqRst = copy.copy(polySeqRst)
    _branchedMapping = {}

    for test_chain_id, ref_chain_ids in target_chain_ids.items():

        if len(ref_chain_ids) == 0:
            continue

        test_ps = next(ps for ps in _polySeqRst if ps['chain_id'] == test_chain_id)
        _test_ps = copy.copy(test_ps)

        _split = False

        p = b_p = 0

        _ref_chain_ids = []
        for ref_chain_id in ref_chain_ids:
            if ref_chain_id[0] not in _ref_chain_ids:
                _ref_chain_ids.append(ref_chain_id[0])

        _b_ref_chain_ids = []
        for ref_chain_id in ref_chain_ids:
            if ref_chain_id[1] not in _ref_chain_ids:
                _b_ref_chain_ids.append(ref_chain_id[1])

        while True:

            ref_chain_id = _ref_chain_ids[p] if p < len(_ref_chain_ids) else None
            myAlign = None
            length = matched = conflict = 0

            if ref_chain_id is not None:

                ref_ps = next(ps for ps in polySeqModel if ps['auth_chain_id'] == ref_chain_id)

                pA.setReferenceSequence(ref_ps['comp_id'], 'REF' + ref_chain_id)
                pA.addTestSequence(_test_ps['comp_id'], ref_chain_id)
                pA.doAlign()

                myAlign = pA.getAlignment(ref_chain_id)

                length = len(myAlign)

                if length > 0:
                    matched, _, conflict, _, _ = getScoreOfSeqAlign(myAlign)

            b_ref_chain_id = _b_ref_chain_ids[b_p]if b_p < len(_b_ref_chain_ids) else None
            myAlignB = None
            b_length = b_matched = b_conflict = 0

            if b_ref_chain_id is not None:

                ref_br = next(br for br in branchedModel if br['auth_chain_id'] == b_ref_chain_id)

                pA.setReferenceSequence(ref_br['comp_id'], 'REF' + b_ref_chain_id)
                pA.addTestSequence(_test_ps['comp_id'], b_ref_chain_id)
                pA.doAlign()

                myAlignB = pA.getAlignment(b_ref_chain_id)

                b_length = len(myAlignB)

                if b_length > 0:
                    b_matched, _, b_conflict, _, _ = getScoreOfSeqAlign(myAlignB)

            if length + b_length == 0 or matched + b_matched == 0 or conflict > 0 or b_conflict > 0:
                break

            if not _split:
                _polySeqRst.remove(test_ps)
                _split = True

            ref_seq_ids, test_seq_ids = [], []
            idx1 = idx2 = 0

            b_ref_seq_ids, b_test_seq_ids = [], []
            b_idx1 = b_idx2 = 0

            if matched > 0:

                for i in range(length):
                    myPr = myAlign[i]
                    myPr0 = str(myPr[0])
                    myPr1 = str(myPr[1])
                    if myPr0 != '.':
                        while idx1 < len(ref_ps['auth_seq_id']):
                            if ref_ps['comp_id'][idx1] == myPr0:
                                ref_seq_ids.append(ref_ps['auth_seq_id'][idx1])
                                idx1 += 1
                                break
                            idx1 += 1
                    else:
                        ref_seq_ids.append(None)
                    if myPr1 != '.':
                        while idx2 < len(_test_ps['seq_id']):
                            if _test_ps['comp_id'][idx2] == myPr1:
                                test_seq_ids.append(_test_ps['seq_id'][idx2])
                                idx2 += 1
                                break
                            idx2 += 1
                    else:
                        test_seq_ids.append(None)

            if b_matched > 0:

                for i in range(b_length):
                    myPr = myAlignB[i]
                    myPr0 = str(myPr[0])
                    myPr1 = str(myPr[1])
                    if myPr0 != '.':
                        while b_idx1 < len(ref_br['auth_seq_id']):
                            if ref_br['comp_id'][b_idx1] == myPr0:
                                b_ref_seq_ids.append(ref_br['seq_id'][b_idx1])
                                b_idx1 += 1
                                break
                            b_idx1 += 1
                    else:
                        b_ref_seq_ids.append(None)
                    if myPr1 != '.':
                        while b_idx2 < len(_test_ps['seq_id']):
                            if _test_ps['comp_id'][b_idx2] == myPr1:
                                b_test_seq_ids.append(_test_ps['seq_id'][b_idx2])
                                b_idx2 += 1
                                break
                            b_idx2 += 1
                    else:
                        b_test_seq_ids.append(None)

            if matched > 0 and b_matched > 0:

                if idx2 < b_idx2:

                    first_seq_id = next(test_seq_id for test_seq_id in test_seq_ids if test_seq_id is not None)
                    last_seq_id = next(test_seq_id for test_seq_id in reversed(test_seq_ids) if test_seq_id is not None)

                    beg = _test_ps['seq_id'].index(first_seq_id)
                    end = _test_ps['seq_id'].index(last_seq_id)

                    _test_ps_ = {'chain_id': ref_chain_id,
                                 'seq_id': _test_ps['seq_id'][beg:end],
                                 'comp_id': _test_ps['comp_id'][beg:end]}

                    _polySeqRst.append(_test_ps_)

                    _test_ps['seq_id'] = _test_ps['seq_id'][end:]
                    _test_ps['comp_id'] = _test_ps['comp_id'][end:]

                    p += 1

                else:

                    last_seq_id = next(test_seq_id for test_seq_id in reversed(b_test_seq_ids) if test_seq_id is not None)

                    end = _test_ps['seq_id'].index(last_seq_id)

                    offset_in_chain = next((test_seq_id - ref_seq_id for ref_seq_id, test_seq_id
                                            in zip(b_ref_seq_ids, b_test_seq_ids)
                                            if ref_seq_id is not None and test_seq_id is not None), None)

                    for ref_seq_id, test_seq_id in zip(b_ref_seq_ids, b_test_seq_ids):
                        if ref_seq_id is not None:
                            if test_seq_id is not None:
                                offset_in_chain = test_seq_id - ref_seq_id
                                _branchedMapping[test_seq_id] = {'chain_id': b_ref_chain_id,
                                                                 'seq_id': ref_seq_id}
                            elif offset_in_chain is not None:
                                test_seq_id = ref_seq_id + offset_in_chain
                                _branchedMapping[test_seq_id] = {'chain_id': b_ref_chain_id,
                                                                 'seq_id': ref_seq_id}

                    _test_ps['seq_id'] = _test_ps['seq_id'][end:]
                    _test_ps['comp_id'] = _test_ps['comp_id'][end:]

                    b_p += 1

            elif matched > 0:

                first_seq_id = next(test_seq_id for test_seq_id in test_seq_ids if test_seq_id is not None)
                last_seq_id = next(test_seq_id for test_seq_id in reversed(test_seq_ids) if test_seq_id is not None)

                beg = _test_ps['seq_id'].index(first_seq_id)
                end = _test_ps['seq_id'].index(last_seq_id)

                _test_ps_ = {'chain_id': ref_chain_id,
                             'seq_id': _test_ps['seq_id'][beg:end],
                             'comp_id': _test_ps['comp_id'][beg:end]}

                _polySeqRst.append(_test_ps_)

                _test_ps['seq_id'] = _test_ps['seq_id'][end:]
                _test_ps['comp_id'] = _test_ps['comp_id'][end:]

                p += 1

            else:

                last_seq_id = next(test_seq_id for test_seq_id in reversed(b_test_seq_ids) if test_seq_id is not None)

                end = _test_ps['seq_id'].index(last_seq_id)

                for ref_seq_id, test_seq_id in zip(b_ref_seq_ids, b_test_seq_ids):
                    if ref_seq_id is not None:
                        if test_seq_id is not None:
                            offset_in_chain = test_seq_id - ref_seq_id
                            _branchedMapping[test_seq_id] = {'chain_id': b_ref_chain_id,
                                                             'seq_id': ref_seq_id}
                        elif offset_in_chain is not None:
                            test_seq_id = ref_seq_id + offset_in_chain
                            _branchedMapping[test_seq_id] = {'chain_id': b_ref_chain_id,
                                                             'seq_id': ref_seq_id}

                _test_ps['seq_id'] = _test_ps['seq_id'][end:]
                _test_ps['comp_id'] = _test_ps['comp_id'][end:]

                b_p += 1

            split = True

    if not split:
        return None, None

    return _polySeqRst, _branchedMapping


def retrieveAtomNameMappingFromRevisions(cR, dir_path: str, extended_pdb_id: str, history: dict,
                                         rep_model_id: int, rep_alt_id: str) -> Optional[List[dict]]:
    """ Retrieve atom name mapping from revision history and PDB Versioned Archive.
    """

    try:
        import requests  # pylint: disable=import-outside-toplevel
    except ImportError:
        return None

    try:
        from wwpdb.utils.nmr.io.CifReader import CifReader  # pylint: disable=import-outside-toplevel
        from wwpdb.utils.nmr.NmrVrptUtility import (uncompress_gzip_file,  # pylint: disable=import-outside-toplevel
                                                    load_from_pickle,
                                                    write_as_pickle)
    except ImportError:
        from nmr.io.CifReader import CifReader  # pylint: disable=import-outside-toplevel
        from nmr.NmrVrptUtility import (uncompress_gzip_file,  # pylint: disable=import-outside-toplevel
                                        load_from_pickle,
                                        write_as_pickle)

    first = min(history)
    last = max(history)

    pkl_path = os.path.join(dir_path, f'atom_name_mapping_{last}_{history[last]}_{first}_{history[first]}.pkl')

    if os.path.exists(pkl_path):
        return load_from_pickle(pkl_path)

    for rev in range(first, last):
        if rev not in history:
            continue

        cif_gz_file = f'{extended_pdb_id}_xyz_v{rev}-{history[rev]}.cif.gz'
        loc_cif_gz_path = os.path.join(dir_path, cif_gz_file)
        loc_cif_path = loc_cif_gz_path[:-3]

        try:
            if not os.path.exists(loc_cif_gz_path):
                url = f'https://data.pdbj.org/pdb_versioned/data/entries/{extended_pdb_id[9:11]}/{extended_pdb_id}/{cif_gz_file}'
                print(f'Downloading {url} -> {loc_cif_gz_path} ...')
                r = requests.get(url, timeout=5.0)
                with open(loc_cif_gz_path, 'wb') as f:
                    f.write(r.content)
                if os.path.exists(loc_cif_path):
                    os.remove(loc_cif_path)
            if not os.path.exists(loc_cif_path):
                uncompress_gzip_file(loc_cif_gz_path, loc_cif_path)
        except Exception as e:
            print(str(e))
            return None

    nstd_residues = [d['id'] for d in cR.getDictList('chem_comp') if d['id'] not in emptyValue and d['id'] not in monDict3]

    if len(nstd_residues) == 0:
        return None

    coord = cR.getDictListWithFilter('atom_site',
                                     [{'name': 'auth_seq_id', 'type': 'int', 'alt_name': 'seq_id'},
                                      {'name': 'label_comp_id', 'type': 'starts-with-alnum', 'alt_name': 'comp_id'},
                                      {'name': 'label_atom_id', 'type': 'starts-with-alnum', 'alt_name': 'atom_id'},
                                      {'name': 'Cartn_x', 'type': 'float', 'alt_name': 'x'},
                                      {'name': 'Cartn_y', 'type': 'float', 'alt_name': 'y'},
                                      {'name': 'Cartn_z', 'type': 'float', 'alt_name': 'z'}
                                      ],
                                     [{'name': 'auth_comp_id', 'type': 'enum', 'enum': nstd_residues},
                                      {'name': 'pdbx_PDB_model_num', 'type': 'int', 'value': rep_model_id},
                                      {'name': 'label_alt_id', 'type': 'enum', 'enum': (rep_alt_id,)}
                                      ])

    if len(coord) == 0:
        return None

    atom_name_mapping = []

    for rev in range(first, last):
        if rev not in history:
            continue

        cif_file = f'{extended_pdb_id}_xyz_v{rev}-{history[rev]}.cif'
        loc_cif_path = os.path.join(dir_path, cif_file)

        if not os.path.exists(loc_cif_path):
            continue

        cR_prev = CifReader(False, sys.stdout, use_cache=False)
        cR_prev.parse(loc_cif_path)

        nstd_residues_prev = [d['id'] for d in cR_prev.getDictList('chem_comp') if d['id'] not in emptyValue and d['id'] not in monDict3]

        if len(nstd_residues_prev) == 0:
            continue

        coord_prev = cR_prev.getDictListWithFilter('atom_site',
                                                   [{'name': 'auth_seq_id', 'type': 'int', 'alt_name': 'seq_id'},
                                                    {'name': 'label_comp_id', 'type': 'starts-with-alnum', 'alt_name': 'comp_id'},
                                                    {'name': 'label_atom_id', 'type': 'starts-with-alnum', 'alt_name': 'atom_id'},
                                                    {'name': 'Cartn_x', 'type': 'float', 'alt_name': 'x'},
                                                    {'name': 'Cartn_y', 'type': 'float', 'alt_name': 'y'},
                                                    {'name': 'Cartn_z', 'type': 'float', 'alt_name': 'z'}
                                                    ],
                                                   [{'name': 'auth_comp_id', 'type': 'enum', 'enum': nstd_residues_prev},
                                                    {'name': 'pdbx_PDB_model_num', 'type': 'int', 'value': rep_model_id},
                                                    {'name': 'label_alt_id', 'type': 'enum', 'enum': (rep_alt_id,)}
                                                    ])

        for c in coord:
            c_prev = next((c_prev for c_prev in coord_prev if c_prev['x'] == c['x'] and c_prev['y'] == c['y'] and c_prev['z'] == c['z']), None)

            if c_prev is None:
                continue

            if c['seq_id'] != c_prev['seq_id']\
               or c['comp_id'] != c_prev['comp_id']\
               or c['atom_id'] != c_prev['atom_id']:
                atom_map = {'auth_atom_id': c['atom_id'],
                            'auth_comp_id': c['comp_id'],
                            'auth_seq_id': c['seq_id'],
                            'original_atom_id': c_prev['atom_id'],
                            'original_comp_id': c_prev['comp_id'],
                            'original_seq_id': c_prev['seq_id']}
                if atom_map not in atom_name_mapping:
                    atom_name_mapping.append(atom_map)

    if len(atom_name_mapping) == 0:
        atom_name_mapping = None

    write_as_pickle(atom_name_mapping, pkl_path)

    return atom_name_mapping


def retrieveAtomNameMappingFromInternal(cR, dir_path: str, history: dict, cif_path: str,
                                        rep_model_id: int, rep_alt_id: str) -> Optional[List[dict]]:
    """ Retrieve atom name mapping from the original uploaded coordinate file.
    """

    try:
        from wwpdb.utils.nmr.io.CifReader import CifReader  # pylint: disable=import-outside-toplevel
        from wwpdb.utils.nmr.NmrVrptUtility import (load_from_pickle,  # pylint: disable=import-outside-toplevel
                                                    write_as_pickle)
    except ImportError:
        from nmr.io.CifReader import CifReader  # pylint: disable=import-outside-toplevel
        from nmr.NmrVrptUtility import (load_from_pickle,  # pylint: disable=import-outside-toplevel
                                        write_as_pickle)

    if not os.path.exists(cif_path):
        return None

    last = max(history)

    pkl_path = os.path.join(dir_path, f'atom_name_mapping_{last}_{history[last]}_internal.pkl')

    if os.path.exists(pkl_path):
        return load_from_pickle(pkl_path)

    nstd_residues = [d['id'] for d in cR.getDictList('chem_comp') if d['id'] not in emptyValue and d['id'] not in monDict3]

    if len(nstd_residues) == 0:
        return None

    coord = cR.getDictListWithFilter('atom_site',
                                     [{'name': 'auth_seq_id', 'type': 'int', 'alt_name': 'seq_id'},
                                      {'name': 'label_comp_id', 'type': 'starts-with-alnum', 'alt_name': 'comp_id'},
                                      {'name': 'label_atom_id', 'type': 'starts-with-alnum', 'alt_name': 'atom_id'},
                                      {'name': 'Cartn_x', 'type': 'float', 'alt_name': 'x'},
                                      {'name': 'Cartn_y', 'type': 'float', 'alt_name': 'y'},
                                      {'name': 'Cartn_z', 'type': 'float', 'alt_name': 'z'}
                                      ],
                                     [{'name': 'auth_comp_id', 'type': 'enum', 'enum': nstd_residues},
                                      {'name': 'pdbx_PDB_model_num', 'type': 'int', 'value': rep_model_id},
                                      {'name': 'label_alt_id', 'type': 'enum', 'enum': (rep_alt_id,)}
                                      ])

    if len(coord) == 0:
        return None

    atom_name_mapping = []

    cR_prev = CifReader(False, sys.stdout, use_cache=False)
    cR_prev.parse(cif_path)

    nstd_residues_prev = [d['id'] for d in cR_prev.getDictList('chem_comp') if d['id'] not in emptyValue and d['id'] not in monDict3]

    if len(nstd_residues_prev) == 0:
        return None

    auth_comp_id = 'auth_comp_id' if cR_prev.hasItem('atom_site', 'auth_comp_id') else 'label_comp_id'

    coord_prev = cR_prev.getDictListWithFilter('atom_site',
                                               [{'name': 'auth_seq_id', 'type': 'int', 'alt_name': 'seq_id'},
                                                {'name': 'label_comp_id', 'type': 'starts-with-alnum', 'alt_name': 'comp_id'},
                                                {'name': 'label_atom_id', 'type': 'starts-with-alnum', 'alt_name': 'atom_id'},
                                                {'name': 'Cartn_x', 'type': 'float', 'alt_name': 'x'},
                                                {'name': 'Cartn_y', 'type': 'float', 'alt_name': 'y'},
                                                {'name': 'Cartn_z', 'type': 'float', 'alt_name': 'z'}
                                                ],
                                               [{'name': auth_comp_id, 'type': 'enum', 'enum': nstd_residues_prev},
                                                {'name': 'pdbx_PDB_model_num', 'type': 'int', 'value': rep_model_id},
                                                {'name': 'label_alt_id', 'type': 'enum', 'enum': (rep_alt_id,)}
                                                ])

    for c in coord:
        c_prev = next((c_prev for c_prev in coord_prev if c_prev['x'] == c['x'] and c_prev['y'] == c['y'] and c_prev['z'] == c['z']), None)

        if c_prev is None:
            continue

        if c['seq_id'] != c_prev['seq_id']\
           or c['comp_id'] != c_prev['comp_id']\
           or c['atom_id'] != c_prev['atom_id']:
            atom_map = {'auth_atom_id': c['atom_id'],
                        'auth_comp_id': c['comp_id'],
                        'auth_seq_id': c['seq_id'],
                        'original_atom_id': c_prev['atom_id'],
                        'original_comp_id': c_prev['comp_id'],
                        'original_seq_id': c_prev['seq_id']}
            if atom_map not in atom_name_mapping:
                atom_name_mapping.append(atom_map)

    if cR_prev.hasItem('atom_site', 'pdbx_auth_atom_name'):
        coord_prev = cR_prev.getDictListWithFilter('atom_site',
                                                   [{'name': 'auth_seq_id', 'type': 'int', 'alt_name': 'seq_id'},
                                                    {'name': 'label_comp_id', 'type': 'starts-with-alnum', 'alt_name': 'comp_id'},
                                                    {'name': 'label_atom_id', 'type': 'starts-with-alnum', 'alt_name': 'atom_id'},
                                                    {'name': 'pdbx_auth_atom_name', 'type': 'starts-with-alnum', 'alt_name': 'alt_atom_id'}
                                                    ],
                                                   [{'name': auth_comp_id, 'type': 'enum', 'enum': nstd_residues_prev},
                                                    {'name': 'pdbx_PDB_model_num', 'type': 'int', 'value': rep_model_id},
                                                    {'name': 'label_alt_id', 'type': 'enum', 'enum': (rep_alt_id,)}
                                                    ])

        for c in coord:
            c_prev = next((c_prev for c_prev in coord_prev if c['comp_id'] == c_prev['comp_id'] and c['atom_id'] == c_prev['atom_id']
                           and c['atom_id'] != c_prev['alt_atom_id'] and 'done' not in c_prev), None)

            if c_prev is None or c_prev['alt_atom_id'] is None:
                continue

            atom_map = {'auth_atom_id': c['atom_id'],
                        'auth_comp_id': c['comp_id'],
                        'auth_seq_id': c['seq_id'],
                        'original_atom_id': c_prev['alt_atom_id'],
                        'original_comp_id': c_prev['comp_id'],
                        'original_seq_id': c_prev['seq_id']}

            if atom_map not in atom_name_mapping:
                atom_name_mapping.append(atom_map)

            c_prev['done'] = True

    if len(atom_name_mapping) == 0:
        atom_name_mapping = None

    write_as_pickle(atom_name_mapping, pkl_path)

    return atom_name_mapping


def getPrettyJson(data: dict) -> str:
    """ Return pretty JSON string.
    """

    def getPrettyChunk(chunk):

        # string
        chunk_ = re.sub(r'",\s+', '", ', chunk)
        # number
        chunk__ = re.sub(r'(\d),\s+', r'\1, ', chunk_)
        # null, true, false
        chunk___ = re.sub(r'(null|true|false),\s+', r'\1, ', chunk__)

        return re.sub(r'(\s+)\[\s+([\S ]+)\s+\](,?)\n', r'\1[\2]\3\n', chunk___)

    lines = json.dumps(data, indent=2).split('\n')

    is_tag, chunk = [], []

    with io.StringIO() as f:

        for line in lines:

            if '": ' in line:

                if f.tell() > 0:
                    is_tag.append(False)
                    chunk.append(f.getvalue())

                    f.truncate(0)
                    f.seek(0)

                is_tag.append(True)
                chunk.append(line)

            else:
                f.write(line + '\n')

        if f.tell() > 0:
            is_tag.append(False)
            chunk.append(f.getvalue())

            f.truncate(0)
            f.seek(0)

        for _is_tag, _chunk in zip(is_tag, chunk):
            f.write((_chunk + '\n') if _is_tag else getPrettyChunk(_chunk))

        return f.getvalue()
