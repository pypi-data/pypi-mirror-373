##
# File: BaseCSParserListener.py
# Date: 08-Apr-2025
#
# Updates:
""" ParserLister base class for any chemical shift file.
    @author: Masashi Yokochi
"""
__docformat__ = "restructuredtext en"
__author__ = "Masashi Yokochi"
__email__ = "yokochi@protein.osaka-u.ac.jp"
__license__ = "Apache License 2.0"
__version__ = "1.0.0"

import sys
import re
import copy
import collections

from typing import IO, List, Tuple, Union, Optional

from wwpdb.utils.align.alignlib import PairwiseAlign  # pylint: disable=no-name-in-module

try:
    from wwpdb.utils.nmr.io.CifReader import SYMBOLS_ELEMENT
    from wwpdb.utils.nmr.mr.ParserListenerUtil import (translateToStdResName,
                                                       translateToStdAtomName,
                                                       backTranslateFromStdResName,
                                                       guessCompIdFromAtomId,
                                                       getRestraintName,
                                                       contentSubtypeOf,
                                                       incListIdCounter,
                                                       decListIdCounter,
                                                       getSaveframe,
                                                       getLoop,
                                                       getCsRow,
                                                       MAX_PREF_LABEL_SCHEME_COUNT,
                                                       MAX_ALLOWED_EXT_SEQ,
                                                       UNREAL_AUTH_SEQ_NUM,
                                                       CS_RESTRAINT_RANGE,
                                                       CS_RESTRAINT_ERROR,
                                                       WEIGHT_RANGE)
    from wwpdb.utils.nmr.ChemCompUtil import ChemCompUtil
    from wwpdb.utils.nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from wwpdb.utils.nmr.nef.NEFTranslator import NEFTranslator
    from wwpdb.utils.nmr.AlignUtil import (LARGE_ASYM_ID,
                                           monDict3,
                                           emptyValue,
                                           protonBeginCode,
                                           pseProBeginCode,
                                           zincIonCode,
                                           calciumIonCode,
                                           getOneLetterCode,
                                           updatePolySeqRst,
                                           revertPolySeqRst,
                                           sortPolySeqRst,
                                           syncCompIdOfPolySeqRst,
                                           alignPolymerSequence,
                                           alignPolymerSequenceWithConflicts,
                                           assignPolymerSequence,
                                           trimSequenceAlignment,
                                           updatePolySeqRstAmbig,
                                           retrieveRemappedSeqId,
                                           retrieveRemappedSeqIdAndCompId,
                                           splitPolySeqRstForExactNoes,
                                           retrieveRemappedChainId,
                                           retrieveRemappedNonPoly)
except ImportError:
    from nmr.io.CifReader import SYMBOLS_ELEMENT
    from nmr.mr.ParserListenerUtil import (translateToStdResName,
                                           translateToStdAtomName,
                                           backTranslateFromStdResName,
                                           guessCompIdFromAtomId,
                                           getRestraintName,
                                           contentSubtypeOf,
                                           incListIdCounter,
                                           decListIdCounter,
                                           getSaveframe,
                                           getLoop,
                                           getCsRow,
                                           MAX_PREF_LABEL_SCHEME_COUNT,
                                           MAX_ALLOWED_EXT_SEQ,
                                           UNREAL_AUTH_SEQ_NUM,
                                           CS_RESTRAINT_RANGE,
                                           CS_RESTRAINT_ERROR,
                                           WEIGHT_RANGE)
    from nmr.ChemCompUtil import ChemCompUtil
    from nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from nmr.nef.NEFTranslator import NEFTranslator
    from nmr.AlignUtil import (LARGE_ASYM_ID,
                               monDict3,
                               emptyValue,
                               protonBeginCode,
                               pseProBeginCode,
                               zincIonCode,
                               calciumIonCode,
                               getOneLetterCode,
                               updatePolySeqRst,
                               revertPolySeqRst,
                               sortPolySeqRst,
                               syncCompIdOfPolySeqRst,
                               alignPolymerSequence,
                               alignPolymerSequenceWithConflicts,
                               assignPolymerSequence,
                               trimSequenceAlignment,
                               updatePolySeqRstAmbig,
                               retrieveRemappedSeqId,
                               retrieveRemappedSeqIdAndCompId,
                               splitPolySeqRstForExactNoes,
                               retrieveRemappedChainId,
                               retrieveRemappedNonPoly)


CS_RANGE_MIN = CS_RESTRAINT_RANGE['min_inclusive']
CS_RANGE_MAX = CS_RESTRAINT_RANGE['max_inclusive']

CS_ERROR_MIN = CS_RESTRAINT_ERROR['min_exclusive']
CS_ERROR_MAX = CS_RESTRAINT_ERROR['max_exclusive']

WEIGHT_RANGE_MIN = WEIGHT_RANGE['min_inclusive']
WEIGHT_RANGE_MAX = WEIGHT_RANGE['max_inclusive']

CHEM_SHIFT_ASSIGNMENT_SEPARATOR_PAT = re.compile(r'[^0-9A-Za-z\'\"]+')
CHEM_SHIFT_ASSIGNMENT_RESID_PAT = re.compile(r'[0-9]+')
CHEM_SHIFT_HALF_SPIN_NUCLEUS = ('H', 'Q', 'M', 'C', 'N', 'P', 'F')


class BaseCSParserListener():

    file_type = None
    software_name = None

    debug = False
    ass_expr_debug = False

    createSfDict__ = False

    # CCD accessing utility
    ccU = None

    # BMRB chemical shift statistics
    csStat = None

    # NEFTranslator
    nefT = None

    # Pairwise align
    pA = None

    # reasons for re-parsing request from the previous trial
    reasons = None

    # data item names for auth_asym_id, auth_seq_id, auth_atom_id in 'atom_site' category
    __authSeqId = None

    polySeq = None
    entityAssembly = None  # key=Entity_assembly_ID (str), value=dictionary of 'entity_id' (int) and 'auth_asym_id' (str)
    labelToAuthSeq = None
    authToLabelSeq = None

    chainIdSet = None
    compIdSet = None
    cyanaCompIdSet = None
    polyPeptide = False
    polyDeoxyribonucleotide = False
    polyRibonucleotide = False

    __shiftNonPosSeq = None
    __defaultSegId = None
    __defaultSegId__ = None

    hasPolySeq = False

    # chain number dictionary
    chainNumberDict = None

    # polymer sequence of MR file
    polySeqCs = None
    polySeqCsFailed = None
    polySeqCsFailedAmbig = None
    compIdMap = None
    __preferAuthSeq = True
    __extendAuthSeq = False

    seqAlign = None
    chainAssign = None

    # current subtype
    cur_subtype = ''
    cur_list_id = -1
    cur_line_num = -1
    offset = None

    # whether to allow extended sequence temporary
    __allow_ext_seq = False

    # whether current assignment derived not from unreliable extra comment
    no_extra_comment = False

    # collection of atom selection set for multiple assignments
    atomSelectionSets = []

    # collection of atom selection
    atomSelectionSet = []

    # collection of any selection
    anySelection = []

    f = None
    warningMessage = None

    reasonsForReParsing = {}

    # original source MR file name
    __originalFileName = '.'

    # list id counter
    __listIdCounter = {}

    # reserved list ids for NMR data remediation Phase 2
    __reservedListIds = {}

    # entry ID
    entryId = '.'

    # dictionary of pynmrstar saveframes
    sfDict = {}

    # default saveframe name for error handling
    __def_err_sf_framecode = None

    __cachedDictForStarAtom = {}

    def __init__(self, verbose: bool = True, log: IO = sys.stdout,
                 polySeq: List[dict] = None, entityAssembly: Optional[dict] = None,
                 ccU: Optional[ChemCompUtil] = None, csStat: Optional[BMRBChemShiftStat] = None, nefT: Optional[NEFTranslator] = None,
                 reasons: Optional[dict] = None):

        self.polySeq = polySeq
        self.entityAssembly = entityAssembly

        # CCD accessing utility
        self.ccU = ChemCompUtil(verbose, log) if ccU is None else ccU

        self.hasPolySeq = self.polySeq is not None and len(self.polySeq) > 0

        if self.hasPolySeq:
            self.__labelToAuthSeq = {}
            for ps in self.polySeq:
                chainId = ps['chain_id']
                authChainId = ps['auth_chain_id' if 'auth_chain_id' in ps else 'chain_id']
                if 'auth_seq_id' not in ps:
                    for seqId in ps['seq_id']:
                        self.__labelToAuthSeq[(chainId, seqId)] = (authChainId, seqId)
                else:
                    for seqId, authSeqId in zip(ps['seq_id'], ps['auth_seq_id']):
                        self.__labelToAuthSeq[(chainId, seqId)] = (authChainId, authSeqId)
            self.authToLabelSeq = {v: k for k, v in self.__labelToAuthSeq.items()}

            self.chainIdSet = set(ps['chain_id'] for ps in self.polySeq)
            self.compIdSet = set()
            self.cyanaCompIdSet = set()

            def is_data(array: list) -> bool:
                return not any(d in emptyValue for d in array)

            for ps in self.polySeq:
                self.compIdSet.update(set(filter(is_data, ps['comp_id'])))

            for compId in self.compIdSet:
                self.cyanaCompIdSet |= backTranslateFromStdResName(compId)

            for compId in self.compIdSet:
                if compId in monDict3:
                    if len(compId) == 3:
                        self.polyPeptide = True
                    elif len(compId) == 2 and compId.startswith('D'):
                        self.polyDeoxyribonucleotide = True
                    elif len(compId) == 1:
                        self.polyRibonucleotide = True

        # BMRB chemical shift statistics
        self.csStat = BMRBChemShiftStat(verbose, log, self.ccU) if csStat is None else csStat

        # NEFTranslator
        self.nefT = NEFTranslator(verbose, log, self.ccU, self.csStat) if nefT is None else nefT

        # Pairwise align
        if self.hasPolySeq:
            self.pA = PairwiseAlign()
            self.pA.setVerbose(verbose)

        # reasons for re-parsing request from the previous trial
        self.reasons = reasons
        self.__preferAuthSeqCount = 0
        self.__preferLabelSeqCount = 0

        self.reasonsForReParsing = {}  # reset to prevent interference from the previous run

        self.chemShifts = 0

        self.sfDict = {}

        self.__cachedDictForStarAtom = {}

    def setDebugMode(self, debug: bool):
        self.debug = debug

    def createSfDict(self, createSfDict: bool):
        self.createSfDict__ = createSfDict

    def setOriginaFileName(self, originalFileName: str):
        self.__originalFileName = originalFileName

    def setListIdCounter(self, listIdCounter: dict):
        self.__listIdCounter = listIdCounter

    def setReservedListIds(self, reservedListIds: dict):
        self.__reservedListIds = reservedListIds

    def setEntryId(self, entryId: str):
        self.entryId = entryId

    def enter(self):
        self.polySeqCs = []
        self.polySeqCsFailed = []
        self.polySeqCsFailedAmbig = []
        self.compIdMap = {}
        self.f = []

    def exit(self):

        try:

            if self.hasPolySeq and self.polySeqCs is not None:
                sortPolySeqRst(self.polySeqCs,
                               None if self.reasons is None else self.reasons.get('non_poly_remap'))

                self.seqAlign, _ = alignPolymerSequence(self.pA, self.polySeq, self.polySeqCs,
                                                        resolvedMultimer=self.reasons is not None)
                self.chainAssign, message = assignPolymerSequence(self.pA, self.ccU, self.file_type, self.polySeq, self.polySeqCs, self.seqAlign)

                if len(self.seqAlign) == 0:
                    for c in range(1, 5):
                        self.seqAlign, _ = alignPolymerSequenceWithConflicts(self.pA, self.polySeq, self.polySeqCs, c)
                        if len(self.seqAlign) > 0:
                            self.chainAssign, message = assignPolymerSequence(self.pA, self.ccU, self.file_type, self.polySeq, self.polySeqCs, self.seqAlign)
                            break

                if len(message) > 0:
                    self.f.extend(message)

                if self.chainAssign is not None:

                    if len(self.polySeq) == len(self.polySeqCs):

                        chain_mapping = {}

                        for ca in self.chainAssign:
                            ref_chain_id = ca['ref_chain_id']
                            test_chain_id = ca['test_chain_id']

                            if ref_chain_id != test_chain_id:
                                chain_mapping[test_chain_id] = ref_chain_id

                        if len(chain_mapping) == len(self.polySeq):

                            for ps in self.polySeqCs:
                                if ps['chain_id'] in chain_mapping:
                                    ps['chain_id'] = chain_mapping[ps['chain_id']]

                            self.seqAlign, _ = alignPolymerSequence(self.pA, self.polySeq, self.polySeqCs,
                                                                    resolvedMultimer=self.reasons is not None)
                            self.chainAssign, _ = assignPolymerSequence(self.pA, self.ccU, self.file_type, self.polySeq, self.polySeqCs, self.seqAlign)

                    trimSequenceAlignment(self.seqAlign, self.chainAssign)

                    if self.reasons is None and any(f for f in self.f
                                                    if '[Atom not found]' in f or '[Sequence mismatch]' in f or '[Invalid atom nomenclature]' in f):

                        seqIdRemap = []

                        for ca in self.chainAssign:
                            ref_chain_id = ca['ref_chain_id']
                            test_chain_id = ca['test_chain_id']

                            sa = next(sa for sa in self.seqAlign
                                      if sa['ref_chain_id'] == ref_chain_id
                                      and sa['test_chain_id'] == test_chain_id)

                            poly_seq_model = next(ps for ps in self.polySeq
                                                  if ps['auth_chain_id' if 'auth_chain_id' in ps else 'chain_id'] == ref_chain_id)
                            poly_seq_rst = next(ps for ps in self.polySeqCs
                                                if ps['chain_id'] == test_chain_id)

                            seq_id_mapping = {}
                            offset = None
                            for ref_seq_id, mid_code, test_seq_id in zip(sa['ref_seq_id'], sa['mid_code'], sa['test_seq_id']):
                                if test_seq_id is None:
                                    continue
                                if mid_code == '|':
                                    try:
                                        seq_id_mapping[test_seq_id] =\
                                            next(auth_seq_id for auth_seq_id, seq_id
                                                 in zip(poly_seq_model['auth_seq_id' if 'auth_seq_id' in poly_seq_model else 'seq_id'], poly_seq_model['seq_id'])
                                                 if seq_id == ref_seq_id and isinstance(auth_seq_id, int))
                                        if offset is None:
                                            offset = seq_id_mapping[test_seq_id] - test_seq_id
                                    except StopIteration:
                                        pass
                                elif mid_code == ' ' and test_seq_id in poly_seq_rst['seq_id']:
                                    idx = poly_seq_rst['seq_id'].index(test_seq_id)
                                    if poly_seq_rst['comp_id'][idx] == '.' and poly_seq_rst['auth_comp_id'][idx] not in emptyValue:
                                        seq_id_mapping[test_seq_id] =\
                                            next(auth_seq_id for auth_seq_id, seq_id
                                                 in zip(poly_seq_model['auth_seq_id' if 'auth_seq_id' in poly_seq_model else 'seq_id'], poly_seq_model['seq_id'])
                                                 if seq_id == ref_seq_id and isinstance(auth_seq_id, int))

                            if offset is not None and all(v - k == offset for k, v in seq_id_mapping.items()):
                                test_seq_id_list = list(seq_id_mapping.keys())
                                min_test_seq_id = min(test_seq_id_list)
                                max_test_seq_id = max(test_seq_id_list)
                                for test_seq_id in range(min_test_seq_id + 1, max_test_seq_id):
                                    if test_seq_id not in seq_id_mapping:
                                        seq_id_mapping[test_seq_id] = test_seq_id + offset

                            if any(k for k, v in seq_id_mapping.items() if k != v)\
                               and not any(k for k, v in seq_id_mapping.items()
                                           if v in poly_seq_model['seq_id']
                                           and k == poly_seq_model['auth_seq_id' if 'auth_seq_id' in poly_seq_model else 'seq_id'][poly_seq_model['seq_id'].index(v)]):
                                offsets = [v - k for k, v in seq_id_mapping.items()]
                                offsets = collections.Counter(offsets).most_common()
                                if len(offsets) == 1:
                                    offset = offsets[0][0]
                                    seq_id_mapping = {ref_seq_id - offset: ref_seq_id for ref_seq_id
                                                      in poly_seq_model['auth_seq_id' if 'auth_seq_id' in poly_seq_model else 'seq_id']}
                                item = {'chain_id': test_chain_id, 'seq_id_dict': seq_id_mapping}
                                if item not in seqIdRemap:
                                    seqIdRemap.append(item)

                        if len(seqIdRemap) > 0:
                            if 'seq_id_remap' not in self.reasonsForReParsing:
                                self.reasonsForReParsing['seq_id_remap'] = seqIdRemap

                        if len(self.polySeq) == 1 and len(self.polySeqCs) == 1:
                            polySeqCs, chainIdMapping, _ =\
                                splitPolySeqRstForExactNoes(self.pA, self.polySeq, self.polySeqCs, self.chainAssign)

                            if polySeqCs is not None:
                                self.polySeqCs = polySeqCs
                                if 'chain_id_clone' not in self.reasonsForReParsing:
                                    self.reasonsForReParsing['chain_id_clone'] = chainIdMapping

                        if len(self.polySeqCsFailed) > 0:
                            sortPolySeqRst(self.polySeqCsFailed)
                            if not any(f for f in self.f if '[Sequence mismatch]' in f):  # 2n6y
                                syncCompIdOfPolySeqRst(self.polySeqCsFailed, self.compIdMap)  # 2mx9

                            seqAlignFailed, _ = alignPolymerSequence(self.pA, self.polySeq, self.polySeqCsFailed)
                            chainAssignFailed, _ = assignPolymerSequence(self.pA, self.ccU, self.file_type,
                                                                         self.polySeq, self.polySeqCsFailed, seqAlignFailed)

                            if chainAssignFailed is not None:
                                seqIdRemapFailed = []

                                uniq_ps = not any('identical_chain_id' in ps for ps in self.polySeq)

                                for ca in chainAssignFailed:
                                    if ca['conflict'] > 0:
                                        continue
                                    ref_chain_id = ca['ref_chain_id']
                                    test_chain_id = ca['test_chain_id']

                                    sa = next((sa for sa in seqAlignFailed
                                               if sa['ref_chain_id'] == ref_chain_id
                                               and sa['test_chain_id'] == test_chain_id), None)

                                    if sa is None:
                                        continue

                                    poly_seq_model = next(ps for ps in self.polySeq
                                                          if ps['auth_chain_id' if 'auth_chain_id' in ps else 'chain_id'] == ref_chain_id)

                                    seq_id_mapping = {}
                                    for ref_seq_id, mid_code, test_seq_id in zip(sa['ref_seq_id'], sa['mid_code'], sa['test_seq_id']):
                                        if test_seq_id is None:
                                            continue
                                        if mid_code == '|':
                                            try:
                                                seq_id_mapping[test_seq_id] =\
                                                    next(auth_seq_id for auth_seq_id, seq_id
                                                         in zip(poly_seq_model['auth_seq_id' if 'auth_seq_id' in poly_seq_model else 'seq_id'], poly_seq_model['seq_id'])
                                                         if seq_id == ref_seq_id and isinstance(auth_seq_id, int))
                                            except StopIteration:
                                                if uniq_ps:
                                                    seq_id_mapping[test_seq_id] = ref_seq_id

                                    offset = None
                                    offsets = [v - k for k, v in seq_id_mapping.items()]
                                    if len(offsets) > 0 and ('gap_in_auth_seq' not in poly_seq_model or not poly_seq_model['gap_in_auth_seq']):
                                        offsets = collections.Counter(offsets).most_common()
                                        if len(offsets) > 1:
                                            offset = offsets[0][0]
                                            for k, v in seq_id_mapping.items():
                                                if v - k != offset:
                                                    seq_id_mapping[k] = k + offset

                                    if uniq_ps and offset is not None and len(seq_id_mapping) > 0\
                                       and ('gap_in_auth_seq' not in poly_seq_model or not poly_seq_model['gap_in_auth_seq']):
                                        for ref_seq_id, mid_code, test_seq_id, ref_code, test_code in zip(sa['ref_seq_id'], sa['mid_code'], sa['test_seq_id'],
                                                                                                          sa['ref_code'], sa['test_code']):
                                            if test_seq_id is None:
                                                continue
                                            if mid_code == '|' and test_seq_id not in seq_id_mapping:
                                                seq_id_mapping[test_seq_id] = test_seq_id + offset
                                            elif ref_code != '.' and test_code == '.':
                                                seq_id_mapping[test_seq_id] = test_seq_id + offset

                                    if any(k for k, v in seq_id_mapping.items() if k != v)\
                                       and not any(k for k, v in seq_id_mapping.items()
                                                   if v in poly_seq_model['seq_id']
                                                   and k == poly_seq_model['auth_seq_id' if 'auth_seq_id' in poly_seq_model else 'seq_id'][poly_seq_model['seq_id'].index(v)]):
                                        offsets = [v - k for k, v in seq_id_mapping.items()]
                                        offsets = collections.Counter(offsets).most_common()
                                        if len(offsets) == 1:
                                            offset = offsets[0][0]
                                            seq_id_mapping = {ref_seq_id - offset: ref_seq_id for ref_seq_id
                                                              in poly_seq_model['auth_seq_id' if 'auth_seq_id' in poly_seq_model else 'seq_id']}
                                        item = {'chain_id': ref_chain_id, 'seq_id_dict': seq_id_mapping, 'comp_id_set': list(set(poly_seq_model['comp_id']))}
                                        if item not in seqIdRemapFailed:
                                            seqIdRemapFailed.append(item)

                                if len(seqIdRemapFailed) > 0:
                                    if 'chain_seq_id_remap' not in self.reasonsForReParsing:
                                        seqIdRemap = self.reasonsForReParsing['seq_id_remap'] if 'seq_id_remap' in self.reasonsForReParsing else []
                                        if len(seqIdRemap) != len(seqIdRemapFailed)\
                                           or seqIdRemap[0]['chain_id'] != seqIdRemapFailed[0]['chain_id']\
                                           or not all(src_seq_id in seqIdRemap[0] for src_seq_id in seqIdRemapFailed[0]):
                                            self.reasonsForReParsing['chain_seq_id_remap'] = seqIdRemapFailed

                                else:
                                    for ps in self.polySeqCsFailed:
                                        for ca in self.chainAssign:
                                            ref_chain_id = ca['ref_chain_id']
                                            test_chain_id = ca['test_chain_id']

                                            if test_chain_id != ps['chain_id']:
                                                continue

                                            sa = next(sa for sa in self.seqAlign
                                                      if sa['ref_chain_id'] == ref_chain_id
                                                      and sa['test_chain_id'] == test_chain_id)

                                            if len(sa['test_seq_id']) != len(sa['ref_seq_id']):
                                                continue

                                            poly_seq_model = next(ps for ps in self.polySeq
                                                                  if ps['auth_chain_id' if 'auth_chain_id' in ps else 'chain_id'] == ref_chain_id)

                                            seq_id_mapping, comp_id_mapping = {}, {}

                                            for seq_id, comp_id in zip(ps['seq_id'], ps['comp_id']):
                                                if seq_id in sa['test_seq_id']:
                                                    idx = sa['test_seq_id'].index(seq_id)
                                                    auth_seq_id = sa['ref_seq_id'][idx]
                                                    seq_id_mapping[seq_id] = auth_seq_id
                                                    comp_id_mapping[seq_id] = comp_id
                                            if any(k for k, v in seq_id_mapping.items() if k != v)\
                                               or ('label_seq_scheme' not in self.reasonsForReParsing
                                                   and all(v not in poly_seq_model['auth_seq_id' if 'auth_seq_id' in poly_seq_model else 'seq_id']
                                                           for v in seq_id_mapping.values())):
                                                seqIdRemapFailed.append({'chain_id': ref_chain_id, 'seq_id_dict': seq_id_mapping,
                                                                         'comp_id_dict': comp_id_mapping})

                                    if len(seqIdRemapFailed) > 0:
                                        if 'ext_chain_seq_id_remap' not in self.reasonsForReParsing:
                                            seqIdRemap = self.reasonsForReParsing['seq_id_remap'] if 'seq_id_remap' in self.reasonsForReParsing else []
                                            if len(seqIdRemap) != len(seqIdRemapFailed)\
                                               or seqIdRemap[0]['chain_id'] != seqIdRemapFailed[0]['chain_id']\
                                               or not all(src_seq_id in seqIdRemap[0] for src_seq_id in seqIdRemapFailed[0]):
                                                self.reasonsForReParsing['ext_chain_seq_id_remap'] = seqIdRemapFailed

        finally:
            self.warningMessage = sorted(list(set(self.f)), key=self.f.index)

    def validateCsValue(self, index: int, pos: float, pos_unc: Optional[float],
                        occupancy: Optional[float] = None,
                        figure_of_merit: Optional[Union[float, int]] = None) -> Optional[dict]:

        validRange = True
        dstFunc = {}

        if CS_ERROR_MIN < pos < CS_ERROR_MAX:
            dstFunc['position'] = str(pos)
        else:
            validRange = False
            self.f.append(f"[Range value error] {self.getCurrentAssignment(n=index)}"
                          f"The position='{pos}' must be within range {CS_RESTRAINT_ERROR}.")

        if not validRange:
            return None

        if CS_RANGE_MIN <= pos <= CS_RANGE_MAX:
            pass
        else:
            self.f.append(f"[Range value warning] {self.getCurrentAssignment(n=index)}"
                          f"The position='{pos}' should be within range {CS_RESTRAINT_RANGE}.")

        if pos_unc is not None and pos_unc != 0.0:
            dstFunc['position_uncertainty'] = str(pos_unc)

        if occupancy is not None:
            if WEIGHT_RANGE_MIN <= occupancy <= WEIGHT_RANGE_MAX:
                dstFunc['occupancy'] = str(occupancy)
            else:
                self.f.append(f"[Range value warning] {self.getCurrentAssignment(n=index)}"
                              f"The occupancy='{occupancy}' should be within range {WEIGHT_RANGE}.")

        if figure_of_merit is not None:
            if WEIGHT_RANGE_MIN <= figure_of_merit <= WEIGHT_RANGE_MAX:
                dstFunc['figure_of_merit'] = str(figure_of_merit)
            else:
                self.f.append(f"[Range value warning] {self.getCurrentAssignment(n=index)}"
                              f"The figure_of_merit='{figure_of_merit}' should be within range {WEIGHT_RANGE}.")

        if self.chemShifts == 0:
            self.__defaultSegId = None
            if self.reasons is not None and 'default_seg_id' in self.reasons:
                try:
                    self.__defaultSegId = self.reasons['default_seg_id'][self.cur_list_id]
                except KeyError:
                    pass

        return dstFunc

    def predictSequenceNumberOffsetByFirstResidue(self, chain_id: Optional[str], seq_id: int, comp_id: Optional[str]):
        if self.reasons is not None or self.polySeq is None:
            return

        if chain_id is not None and any(ps for ps in self.polySeq if ps['auth_chain_id' if 'auth_chain_id' in ps else 'chain_id']):

            if chain_id in self.offset:
                return

            ps = next(ps for ps in self.polySeq if ps['auth_chain_id' if 'auth_chain_id' in ps else 'chain_id'])
            seq_ids = ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id']
            min_seq_id = seq_ids[0]
            max_seq_id = seq_ids[-1]

            if seq_id < min_seq_id or seq_id > max_seq_id:
                offset = min_seq_id - seq_id

                if comp_id is not None:
                    _seq_id = seq_id + offset
                    if _seq_id in seq_ids and comp_id == ps['comp_id'][seq_ids.index(_seq_id)]:
                        self.offset[chain_id] = offset
                        return

                    for shift in range(1, 10):
                        _seq_id = seq_id + offset + shift
                        if _seq_id in seq_ids and comp_id == ps['comp_id'][seq_ids.index(_seq_id)]:
                            self.offset[chain_id] = offset + shift
                            return

                self.offset[chain_id] = offset

            return

        if None in self.offset:
            return

        min_seq_id = 1000
        max_seq_id = -1000
        for ps in self.polySeq:
            min_seq_id = min(min_seq_id, ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id'][0])
            max_seq_id = max(max_seq_id, ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id'][-1])

        if seq_id < min_seq_id or seq_id > max_seq_id:
            offset = min_seq_id - seq_id

            if comp_id is not None:
                for ps in self.polySeq:
                    seq_ids = ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id']
                    min_seq_id = seq_ids[0]
                    offset = min_seq_id - seq_id

                    _seq_id = seq_id + offset
                    if _seq_id in seq_ids and comp_id == ps['comp_id'][seq_ids.index(_seq_id)]:
                        self.offset[None] = offset
                        return

                for shift in range(1, 10):
                    for ps in self.polySeq:
                        seq_ids = ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id']
                        min_seq_id = seq_ids[0]
                        offset = min_seq_id - seq_id

                        _seq_id = seq_id + offset + shift
                        if _seq_id in seq_ids and comp_id == ps['comp_id'][seq_ids.index(_seq_id)]:
                            self.offset[None] = offset + shift
                            return

            self.offset[None] = offset

    def checkAssignment(self, index: int, assignment: List[dict]) -> Tuple[bool, bool, Optional[bool]]:
        has_assignments = has_multiple_assignments = False

        if assignment is not None:

            self.retrieveLocalSeqScheme()

            try:

                hasChainId = assignment[0]['chain_id'] is not None
                hasCompId = assignment[0]['comp_id'] is not None

                has_multiple_assignments = len(assignment) > 1

                for a in assignment:

                    self.atomSelectionSet.clear()

                    if hasChainId and hasCompId:
                        chainAssign, _ = self.assignCoordPolymerSequenceWithChainId(a['chain_id'], a['seq_id'], a['comp_id'], a['atom_id'], index)

                    elif hasChainId:
                        chainAssign = self.assignCoordPolymerSequenceWithChainIdWithoutCompId(a['chain_id'], a['seq_id'], a['atom_id'], index)

                    elif hasCompId:
                        chainAssign, _ = self.assignCoordPolymerSequence(a['chain_id'], a['seq_id'], a['comp_id'], a['atom_id'], index)

                    else:
                        chainAssign = self.assignCoordPolymerSequenceWithoutCompId(a['seq_id'], a['atom_id'], index)

                    if len(chainAssign) > 0:
                        self.selectCoordAtoms(chainAssign, a['seq_id'], a['comp_id'], a['atom_id'], index)

                        if len(self.atomSelectionSet) == 1:
                            has_assignments = True
                            self.atomSelectionSets.append(copy.deepcopy(self.atomSelectionSet))
                        else:
                            has_assignments = False
                            break

            except (KeyError, TypeError):
                pass

        return has_assignments, has_multiple_assignments

    def addCsRow(self, index: int, dstFunc: dict, has_assignments: bool, has_multiple_assignments: bool, auth_seq_id_map: dict,
                 debug_label: Optional[str], details: Optional[str] = None, default_ambig_code: Optional[int] = None):

        if self.debug:
            if not has_assignments:
                print(f"subtype={self.cur_subtype} id={self.chemShifts + 1} (index={index}) "
                      f"{debug_label}None None {dstFunc}")
            for idx, atomSelectionSet in enumerate(self.atomSelectionSets, start=1):
                if has_multiple_assignments:
                    print(f"subtype={self.cur_subtype} id={self.chemShifts + 1} (index={index}) combination_id={idx} "
                          f"{debug_label}{atomSelectionSet[0]} {dstFunc}")
                else:
                    print(f"subtype={self.cur_subtype} id={self.chemShifts + 1} (index={index}) "
                          f"{debug_label}{atomSelectionSet[0]} {dstFunc}")

        if self.createSfDict__:
            sf = self.getSf()

            if sf is not None:
                sf['id'] = index
                sf['index_id'] += 1
                ambig_code = default_ambig_code
                if has_assignments and not has_multiple_assignments and default_ambig_code is None:
                    atom = self.atomSelectionSet[0][0]
                    if len(self.atomSelectionSet[0]) > 1:
                        ambig_code = self.csStat.getMaxAmbigCodeWoSetId(atom['comp_id'], atom['atom_id'])
                        if ambig_code == 0:
                            ambig_code = None
                else:
                    atom = None
                    return

                if len(auth_seq_id_map) > 0 and atom['seq_id'] in auth_seq_id_map:
                    atom['auth_seq_id'] = auth_seq_id_map[atom['seq_id']]

                row = getCsRow(self.cur_subtype, sf['index_id'], sf['list_id'], self.entryId,
                               dstFunc, self.entityAssembly,
                               atom, ambig_code=ambig_code, details=details)
                sf['loop'].add_data(row)

    def extractAssignment(self, numOfDim: int, string: str, src_index: int,
                          with_segid: Optional[str] = None, with_compid: Optional[str] = None,
                          hint: Optional[List[dict]] = None) -> Optional[List[dict]]:
        """ Extract assignment from a given string.
        """

        if numOfDim not in (1, 2, 3, 4) or string is None:
            return None

        _str_ = CHEM_SHIFT_ASSIGNMENT_SEPARATOR_PAT.sub(' ', string).split()
        _str = CHEM_SHIFT_ASSIGNMENT_SEPARATOR_PAT.sub(' ', string.upper()).split()
        lenStr = len(_str)

        segIdLike, resIdLike, resNameLike, atomNameLike, _atomNameLike, __atomNameLike, ___atomNameLike, atomNameLike_ =\
            [False] * lenStr, [False] * lenStr, [False] * lenStr, [False] * lenStr, [False] * lenStr, [False] * lenStr, [False] * lenStr, [False] * lenStr

        segIdSpan, resIdSpan, resNameSpan, atomNameSpan, _atomNameSpan, __atomNameSpan, ___atomNameSpan, siblingAtomName =\
            [None] * lenStr, [None] * lenStr, [None] * lenStr, [None] * lenStr, [None] * lenStr, [None] * lenStr, [None] * lenStr, [None] * lenStr

        if self.chainIdSet is None:
            self.chainIdSet = set()
        if self.compIdSet is None:
            self.compIdSet = set(monDict3.keys())

        oneLetterCodeSet = []
        extMonDict3 = {}
        if self.polyPeptide and not self.polyDeoxyribonucleotide and not self.polyRibonucleotide:
            oneLetterCodeSet = [getOneLetterCode(compId) for compId in self.compIdSet if len(compId) == 3]
            extMonDict3 = {compId: getOneLetterCode(compId) for compId in self.compIdSet if len(compId) == 3}
        elif not self.polyPeptide and self.polyDeoxyribonucleotide and not self.polyRibonucleotide:
            oneLetterCodeSet = [getOneLetterCode(compId) for compId in self.compIdSet if len(compId) == 2]
            extMonDict3 = {compId: getOneLetterCode(compId) for compId in self.compIdSet if len(compId) == 2}
        elif not self.polyPeptide and not self.polyDeoxyribonucleotide and self.polyRibonucleotide:
            oneLetterCodeSet = [getOneLetterCode(compId) for compId in self.compIdSet if len(compId) == 1]
            extMonDict3 = {compId: getOneLetterCode(compId) for compId in self.compIdSet if len(compId) == 1}

        for np in self.polySeq:
            if len(np['seq_id']) != 1:
                continue
            if np['comp_id'][0][0].isalpha() and np['comp_id'][0][0] not in oneLetterCodeSet:
                oneLetterCodeSet.append(np['comp_id'][0][0])
                extMonDict3[np['comp_id'][0]] = np['comp_id'][0][0]
            if 'auth_comp_id' in np and np['auth_comp_id'][0][0].isalpha() and np['auth_comp_id'][0][0] not in oneLetterCodeSet:
                oneLetterCodeSet.append(np['auth_comp_id'][0][0])
                extMonDict3[np['comp_id'][0]] = np['auth_comp_id'][0][0]
            if 'alt_comp_id' in np and np['alt_comp_id'][0][0].isalpha() and np['alt_comp_id'][0][0] not in oneLetterCodeSet:
                oneLetterCodeSet.append(np['alt_comp_id'][0][0])
                extMonDict3[np['comp_id'][0]] = np['alt_comp_id'][0][0]

        hasOneLetterCodeSet = len(oneLetterCodeSet) > 0
        useOneLetterCodeSet = forceOneLetterCodeSet = self.polyRibonucleotide and not self.polyPeptide and not self.polyDeoxyribonucleotide
        ligCompId = ligAtomId = None
        _ligSeqId = _ligCompId = _ligAtomId = None

        for idx, term in enumerate(_str):
            for segId in self.chainIdSet:
                if term.startswith(segId) and (with_segid is None or term.startswith(with_segid)):
                    segIdLike[idx] = True
                    segIdSpan[idx] = (0, len(segId))
                    break

            resIdTest = CHEM_SHIFT_ASSIGNMENT_RESID_PAT.search(term)
            if resIdTest:
                if term[0] == 'D' and len(term) == 3 and term[-1] in ('5', '3') and translateToStdResName(term, ccU=self.ccU) in self.compIdSet:
                    pass
                else:
                    resIdLike[idx] = True
                    resIdSpan[idx] = resIdTest.span()

            minIndex = len(term)

            for compId in self.compIdSet:
                if compId in term:
                    resNameLike[idx] = True
                    index = term.index(compId)
                    if index < minIndex:
                        resNameSpan[idx] = (index, index + len(compId))
                        minIndex = index

            if not resNameLike[idx] and self.cyanaCompIdSet is not None:
                for compId in self.cyanaCompIdSet:
                    if compId in term:
                        resNameLike[idx] = True
                        index = term.index(compId)
                        if index < minIndex:
                            resNameSpan[idx] = (index, index + len(compId))
                            minIndex = index

            if hasOneLetterCodeSet and not useOneLetterCodeSet and resNameLike[idx] and len(term[resNameSpan[idx][0]:resNameSpan[idx][1]]) > 1:
                hasOneLetterCodeSet = False

            if with_compid is not None and len(with_compid) > 1:
                hasOneLetterCodeSet = False

            if not resNameLike[idx] and hasOneLetterCodeSet:
                if not any(compId in term for compId in monDict3 if len(compId) == 3):
                    for compId in oneLetterCodeSet:
                        if compId in term:
                            resNameLike[idx] = True
                            index = term.index(compId)
                            if index < minIndex:
                                resNameSpan[idx] = (index, index + len(compId))
                                minIndex = index
                elif resIdLike[idx] and self.hasPolySeq:
                    _compId = next(compId for compId in monDict3 if len(compId) == 3 and compId in term)
                    resId = int(term[resIdSpan[idx][0]:resIdSpan[idx][1]])
                    for ps in self.polySeq:
                        _, _, compId = self.getRealChainSeqId(ps, resId, None)
                        if len(compId) == 3 and compId in monDict3 and _compId[0:2] == compId[0:2]:
                            resNameLike[idx] = True
                            index = term.index(_compId)
                            resNameSpan[idx] = (index, index + len(compId))
                            term = _str[idx] = term.replace(_compId, compId)
                            break

            if resNameLike[idx]:
                compId = term[resNameSpan[idx][0]:resNameSpan[idx][1]]
                if compId in self.compIdSet and compId not in monDict3:
                    ligCompId = compId

                if len(compId) == 1:
                    _ligCompId = next((k for k, v in extMonDict3.items() if v == compId and k not in monDict3), None)

                    if resIdLike[idx] and self.hasPolySeq:
                        resId = int(term[resIdSpan[idx][0]:resIdSpan[idx][1]])
                        for ps in self.polySeq:
                            _, _, _compId = self.getRealChainSeqId(ps, resId, None)
                            if _compId is not None and _compId not in monDict3:
                                resNameLike[idx] = False
                                break
                    if resNameLike[idx]:
                        index = resNameSpan[idx][1]
                        if index < len(term):
                            if term[index].isdigit() or term[index] in CHEM_SHIFT_HALF_SPIN_NUCLEUS or term[index] in pseProBeginCode:
                                pass
                            else:
                                resNameLike[idx] = False

            if ligCompId is not None and ligCompId != term:
                _, _, details = self.nefT.get_valid_star_atom_in_xplor(ligCompId, term, leave_unmatched=True)
                if details is None or term[0] in CHEM_SHIFT_HALF_SPIN_NUCLEUS:
                    atomNameLike[idx] = True
                    atomNameSpan[idx] = (0, len(term) + 1)
                    ligAtomId = term

            if _ligCompId is not None and resNameLike[idx] and len(term[resNameSpan[idx][1]:]) > 0:
                _, _, details = self.nefT.get_valid_star_atom_in_xplor(_ligCompId, term[resNameSpan[idx][1]:], leave_unmatched=True)
                if details is None or term[resNameSpan[idx][1]] in CHEM_SHIFT_HALF_SPIN_NUCLEUS:
                    atomNameLike[idx] = True
                    atomNameSpan[idx] = (resNameSpan[idx][1], len(term) + 1)
                    _ligAtomId = term[resNameSpan[idx][1]:len(term) + 1]
                    for np in self.polySeq:
                        if np['comp_id'][0] == _ligCompId:
                            _ligSeqId = np['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id'][0]

            if resIdLike[idx] and resIdSpan[idx][1] + 1 <= len(term) and _str_[idx][resIdSpan[idx][1]].islower() and _str[idx][resIdSpan[idx][1]].isupper():
                if resIdSpan[idx][1] + 1 < len(term) and any(_str_[idx][resIdSpan[idx][1] + 1].startswith(elem) for elem in CHEM_SHIFT_HALF_SPIN_NUCLEUS):
                    term = _str[idx] = term[0:resIdSpan[idx][1]] + term[resIdSpan[idx][1] + 1:]
                elif resIdSpan[idx][1] + 1 == len(term):
                    term = _str[idx] = term[0:resIdSpan[idx][1]]

            for elem in reversed(CHEM_SHIFT_HALF_SPIN_NUCLEUS) if 'NH' in term else CHEM_SHIFT_HALF_SPIN_NUCLEUS:
                if len(elem) == 1 and ligAtomId is None and _ligAtomId is None:
                    if elem in term:

                        # handle ambiguous assigned peak '(14Trp/11Trp)Hh2' seen in 6r28/bmr34380/work/data/D_1292101294_nmr-peaks-upload_P1.dat.V1
                        if idx > 0 and not resNameLike[idx] and any(resIdLike[_idx] and resNameLike[_idx] and not atomNameLike[_idx]
                                                                    for _idx in range(idx)):
                            _index = term.index(elem)
                            _atomId = term[_index:len(term)]
                            for _idx in range(idx):
                                if resIdLike[_idx] and resNameLike[_idx] and not atomNameLike[_idx]:
                                    _compId = _str[_idx][resNameSpan[_idx][0]:resNameSpan[_idx][1]]
                                    if len(_compId) == 1 and hasOneLetterCodeSet:
                                        _compId = next(k for k, v in extMonDict3.items() if k in self.compIdSet and v == _compId)
                                        _, _, details = self.nefT.get_valid_star_atom_in_xplor(_compId, _atomId, leave_unmatched=True)
                                        if details is None:
                                            atomNameLike[idx] = atomNameLike_[_idx] = useOneLetterCodeSet = True
                                            atomNameSpan[idx] = (_index, len(term))
                                            if siblingAtomName[_idx] is None:
                                                siblingAtomName[_idx] = []
                                            if _atomId not in siblingAtomName[_idx]:
                                                siblingAtomName[_idx].append(_atomId)
                                            break
                                    if (with_compid is not None and _atomId.startswith(with_compid)) or _atomId.startswith('MET'):
                                        continue
                                    _atomId = translateToStdAtomName(_atomId, _compId, ccU=self.ccU)
                                    _, _, details = self.nefT.get_valid_star_atom_in_xplor(_compId, _atomId, leave_unmatched=True)
                                    if details is None:
                                        atomNameLike[idx] = atomNameLike_[_idx] = True
                                        atomNameSpan[idx] = (_index, len(term))
                                        if siblingAtomName[_idx] is None:
                                            siblingAtomName[_idx] = []
                                        if _atomId not in siblingAtomName[_idx]:
                                            siblingAtomName[_idx].append(_atomId)
                                        break
                            if atomNameLike[idx]:
                                break

                        # prevent to split HH2 -> res_name:'HIS', atom_name:'H2'
                        if resNameLike[idx] and resNameSpan[idx][1] - resNameSpan[idx][0] == 1 and resNameSpan[idx][1] == term.rindex(elem)\
                           and term[resNameSpan[idx][0]] in CHEM_SHIFT_HALF_SPIN_NUCLEUS:
                            _index = term.index(elem)
                            _atomId = term[_index:len(term)]
                            for compId in self.compIdSet:
                                _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, _atomId, leave_unmatched=True)
                                if details is None:
                                    atomNameLike[idx] = True
                                    atomNameSpan[idx] = (_index, len(term))
                                    resNameLike[idx] = False
                                    break
                            if atomNameLike[idx]:
                                break

                        # resolve concatenation of residue number and XPLOR-NIH atom nomenclature of proton, D1391HB -> res_id:139, res_name:'ASP', atom_name:'1HB'
                        # seen in 8e1d/bmr31038/work/data/D_1000267621_nmr-peaks-upload_P6.dat.V1
                        if self.hasPolySeq and resIdLike[idx] and resNameLike[idx] and resIdSpan[idx][1] == term.rindex(elem) and elem == 'H'\
                           and term[resIdSpan[idx][1] - 1] in ('1', '2', '3') and resIdSpan[idx][1] - resIdSpan[idx][0] > 3:
                            _resId = int(term[resIdSpan[idx][0]:resIdSpan[idx][1]])
                            _compId = term[resNameSpan[idx][0]:resNameSpan[idx][1]]
                            if len(_compId) == 1 and hasOneLetterCodeSet:
                                _compId = next((k for k, v in extMonDict3.items() if k in self.compIdSet and v == _compId), _compId)
                            valid = False
                            for ps in self.polySeq:
                                _, _, _compId_ = self.getRealChainSeqId(ps, _resId, None)
                                if _compId is not None and _compId == _compId_:
                                    valid = True
                                    break
                            if not valid:
                                _resId = int(term[resIdSpan[idx][0]:resIdSpan[idx][1] - 1])
                                for ps in self.polySeq:
                                    _, _, _compId_ = self.getRealChainSeqId(ps, _resId, None)
                                    if _compId is not None and _compId == _compId_:
                                        valid = True
                                        break
                                if valid:
                                    _index = term.rindex(elem)
                                    _atomId = term[_index:len(term)] + term[resIdSpan[idx][1] - 1]
                                    _, _, details = self.nefT.get_valid_star_atom_in_xplor(_compId, _atomId, leave_unmatched=True)
                                    if details is None:
                                        atomNameLike[idx] = True
                                        atomNameSpan[idx] = (_index - 1, len(term))
                                        resIdSpan[idx] = (resIdSpan[idx][0], resIdSpan[idx][1] - 1)
                                        break
                        index = term.rindex(elem)
                        atomId = term[index:len(term)]
                        if index - 1 >= 0 and term[index - 1] in CHEM_SHIFT_HALF_SPIN_NUCLEUS:
                            if resNameLike[idx] and compId[-1] in CHEM_SHIFT_HALF_SPIN_NUCLEUS and index == resNameSpan[idx][1]:
                                pass
                            else:
                                continue
                        if atomId[0] in ('Q', 'M') and index + 1 < len(term) and term[index + 1].isdigit():
                            if resNameLike[idx] and resNameSpan[idx][0] == index:
                                continue
                            if self.csStat.peptideLike(compId):
                                ligand = False
                                if resIdLike[idx] and self.reasons is not None:
                                    resId = int(term[resIdSpan[idx][0]:resIdSpan[idx][1]])
                                    if 'non_poly_remap' in self.reasons\
                                       and compId in self.reasons['non_poly_remap']\
                                       and resId in self.reasons['non_poly_remap'][compId]:
                                        ligand = True
                                if not ligand:
                                    continue
                        if ((with_compid is not None and atomId.startswith(with_compid)) or atomId.startswith('MET'))\
                           and ((index + 3 < len(term) and term[index + 3].isdigit() or (index + 4 < len(term) and term[index + 4].isdigit()))):
                            continue
                        if resNameLike[idx] and len(compId) > 1 and compId[-1] == elem and index + 1 == resNameSpan[idx][1]:
                            continue
                        if resNameLike[idx]:
                            compId = term[resNameSpan[idx][0]:resNameSpan[idx][1]]
                            if len(compId) == 1 and hasOneLetterCodeSet and not forceOneLetterCodeSet:
                                compId = next(k for k, v in extMonDict3.items() if k in self.compIdSet and v == compId)
                                _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, atomId, leave_unmatched=True)
                                if details is None:
                                    atomNameLike[idx] = useOneLetterCodeSet = True
                                    atomNameSpan[idx] = (index, len(term))
                                    if resNameSpan[idx][0] == atomNameSpan[idx][0]:
                                        resNameLike[idx] = False
                                    break
                                if with_compid is not None and (atomId.startswith(with_compid) or (atomId in with_compid and index < resNameSpan[idx][1])):
                                    continue
                                _atomId = translateToStdAtomName(atomId, compId, ccU=self.ccU)
                                _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, _atomId, leave_unmatched=True)
                                if details is None:
                                    atomNameLike[idx] = True
                                    atomNameSpan[idx] = (index, len(term))
                                    if resNameSpan[idx][0] == atomNameSpan[idx][0]:
                                        resNameLike[idx] = False
                                    break
                        for compId in self.compIdSet:
                            _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, atomId, leave_unmatched=True)
                            if details is None:
                                atomNameLike[idx] = True
                                atomNameSpan[idx] = (index, len(term))
                                break
                            if with_compid is not None and atomId.startswith(with_compid):
                                continue
                            _atomId = translateToStdAtomName(atomId, compId, ccU=self.ccU)
                            _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, _atomId, leave_unmatched=True)
                            if details is None:
                                atomNameLike[idx] = True
                                atomNameSpan[idx] = (index, len(term))
                                break
                        if atomNameLike[idx]:
                            break

            if atomNameLike[idx]:
                _term = term[0:atomNameSpan[idx][0]]
                for elem in reversed(CHEM_SHIFT_HALF_SPIN_NUCLEUS) if 'NH' in _term else CHEM_SHIFT_HALF_SPIN_NUCLEUS:
                    if len(elem) == 1 and ligAtomId is None and _ligAtomId is None:
                        if elem in _term:
                            index = _term.rindex(elem)
                            atomId = _term[index:len(_term)]
                            if index - 1 >= 0 and _term[index - 1] in CHEM_SHIFT_HALF_SPIN_NUCLEUS:
                                if resNameLike[idx] and compId[-1] in CHEM_SHIFT_HALF_SPIN_NUCLEUS and index == resNameSpan[idx][1]:
                                    pass
                                else:
                                    continue
                            if atomId[0] in ('Q', 'M') and index + 1 < len(_term) and _term[index + 1].isdigit():
                                continue
                            if ((with_compid is not None and atomId.startswith(with_compid)) or atomId.startswith('MET'))\
                               and ((index + 3 < len(_term) and _term[index + 3].isdigit() or (index + 4 < len(_term) and _term[index + 4].isdigit()))):
                                continue
                            if resNameLike[idx] and len(compId) > 1 and compId[-1] == elem and index + 1 == resNameSpan[idx][1]:
                                continue
                            if len(_term) == atomNameSpan[idx][0]:
                                continue
                            if resNameLike[idx]:
                                compId = term[resNameSpan[idx][0]:resNameSpan[idx][1]]
                                if len(compId) == 1 and hasOneLetterCodeSet:
                                    compId = next(k for k, v in extMonDict3.items() if k in self.compIdSet and v == compId)
                                    _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, atomId, leave_unmatched=True)
                                    if details is None:
                                        _atomNameLike[idx] = useOneLetterCodeSet = True
                                        _atomNameSpan[idx] = (index, len(_term))
                                        if resNameSpan[idx][0] == _atomNameSpan[idx][0]:
                                            resNameLike[idx] = False
                                        break
                                    if with_compid is not None and (atomId.startswith(with_compid) or (atomId in with_compid and index < resNameSpan[idx][1])):
                                        continue
                                    _atomId = translateToStdAtomName(atomId, compId, ccU=self.ccU)
                                    _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, _atomId, leave_unmatched=True)
                                    if details is None:
                                        _atomNameLike[idx] = True
                                        _atomNameSpan[idx] = (index, len(_term))
                                        if resNameSpan[idx][0] == _atomNameSpan[idx][0]:
                                            resNameLike[idx] = False
                                        break
                            for compId in self.compIdSet:
                                _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, atomId, leave_unmatched=True)
                                if details is None:
                                    _atomNameLike[idx] = True
                                    _atomNameSpan[idx] = (index, len(_term))
                                    break
                                if with_compid is not None and atomId.startswith(with_compid):
                                    continue
                                _atomId = translateToStdAtomName(atomId, compId, ccU=self.ccU)
                                _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, _atomId, leave_unmatched=True)
                                if details is None:
                                    _atomNameLike[idx] = True
                                    _atomNameSpan[idx] = (index, len(_term))
                                    break
                            if _atomNameLike[idx]:
                                break

            if numOfDim >= 3 and _atomNameLike[idx]:
                __term = term[0:_atomNameSpan[idx][0]]
                for elem in reversed(CHEM_SHIFT_HALF_SPIN_NUCLEUS) if 'NH' in __term else CHEM_SHIFT_HALF_SPIN_NUCLEUS:
                    if len(elem) == 1 and ligAtomId is None and _ligAtomId is None:
                        if elem in __term:
                            index = __term.rindex(elem)
                            atomId = __term[index:len(__term)]
                            if index - 1 >= 0 and __term[index - 1] in CHEM_SHIFT_HALF_SPIN_NUCLEUS:
                                if resNameLike[idx] and compId[-1] in CHEM_SHIFT_HALF_SPIN_NUCLEUS and index == resNameSpan[idx][1]:
                                    pass
                                else:
                                    continue
                            if atomId[0] in ('Q', 'M') and index + 1 < len(__term) and __term[index + 1].isdigit():
                                continue
                            if ((with_compid is not None and atomId.startswith(with_compid)) or atomId.startswith('MET'))\
                               and ((index + 3 < len(__term) and __term[index + 3].isdigit() or (index + 4 < len(__term) and __term[index + 4].isdigit()))):
                                continue
                            if resNameLike[idx] and len(compId) > 1 and compId[-1] == elem and index + 1 == resNameSpan[idx][1]:
                                continue
                            if len(__term) == _atomNameSpan[idx][0]:
                                continue
                            if resNameLike[idx]:
                                compId = term[resNameSpan[idx][0]:resNameSpan[idx][1]]
                                if len(compId) == 1 and hasOneLetterCodeSet:
                                    compId = next(k for k, v in extMonDict3.items() if k in self.compIdSet and v == compId)
                                    _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, atomId, leave_unmatched=True)
                                    if details is None:
                                        __atomNameLike[idx] = useOneLetterCodeSet = True
                                        __atomNameSpan[idx] = (index, len(__term))
                                        if resNameSpan[idx][0] == __atomNameSpan[idx][0]:
                                            resNameLike[idx] = False
                                        break
                                    if with_compid is not None and atomId.startswith(with_compid):
                                        continue
                                    _atomId = translateToStdAtomName(atomId, compId, ccU=self.ccU)
                                    _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, _atomId, leave_unmatched=True)
                                    if details is None:
                                        __atomNameLike[idx] = True
                                        __atomNameSpan[idx] = (index, len(__term))
                                        if resNameSpan[idx][0] == __atomNameSpan[idx][0]:
                                            resNameLike[idx] = False
                                        break
                            for compId in self.compIdSet:
                                _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, atomId, leave_unmatched=True)
                                if details is None:
                                    __atomNameLike[idx] = True
                                    __atomNameSpan[idx] = (index, len(__term))
                                    break
                                if with_compid is not None and atomId.startswith(with_compid):
                                    continue
                                _atomId = translateToStdAtomName(atomId, compId, ccU=self.ccU)
                                _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, _atomId, leave_unmatched=True)
                                if details is None:
                                    __atomNameLike[idx] = True
                                    __atomNameSpan[idx] = (index, len(__term))
                                    break
                            if __atomNameLike[idx]:
                                break

            if numOfDim >= 4 and __atomNameLike[idx]:
                ___term = term[0:__atomNameSpan[idx][0]]
                for elem in reversed(CHEM_SHIFT_HALF_SPIN_NUCLEUS) if 'NH' in ___term else CHEM_SHIFT_HALF_SPIN_NUCLEUS:
                    if len(elem) == 1 and ligAtomId is None and _ligAtomId is None:
                        if elem in ___term:
                            index = ___term.rindex(elem)
                            atomId = ___term[index:len(___term)]
                            if index - 1 >= 0 and ___term[index - 1] in CHEM_SHIFT_HALF_SPIN_NUCLEUS:
                                if resNameLike[idx] and compId[-1] in CHEM_SHIFT_HALF_SPIN_NUCLEUS and index == resNameSpan[idx][1]:
                                    pass
                                else:
                                    continue
                            if atomId[0] in ('Q', 'M') and index + 1 < len(___term) and ___term[index + 1].isdigit():
                                continue
                            if ((with_compid is not None and atomId.startswith(with_compid)) or atomId.startswith('MET'))\
                               and ((index + 3 < len(___term) and ___term[index + 3].isdigit() or (index + 4 < len(___term) and ___term[index + 4].isdigit()))):
                                continue
                            if resNameLike[idx] and len(compId) > 1 and compId[-1] == elem and index + 1 == resNameSpan[idx][1]:
                                continue
                            if len(___term) == __atomNameSpan[idx][0]:
                                continue
                            if resNameLike[idx]:
                                compId = term[resNameSpan[idx][0]:resNameSpan[idx][1]]
                                if len(compId) == 1 and hasOneLetterCodeSet:
                                    compId = next(k for k, v in extMonDict3.items() if k in self.compIdSet and v == compId)
                                    _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, atomId, leave_unmatched=True)
                                    if details is None:
                                        ___atomNameLike[idx] = useOneLetterCodeSet = True
                                        ___atomNameSpan[idx] = (index, len(___term))
                                        if resNameSpan[idx][0] == ___atomNameSpan[idx][0]:
                                            resNameLike[idx] = False
                                        break
                                    if with_compid is not None and atomId.startswith(with_compid):
                                        continue
                                    _atomId = translateToStdAtomName(atomId, compId, ccU=self.ccU)
                                    _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, _atomId, leave_unmatched=True)
                                    if details is None:
                                        ___atomNameLike[idx] = True
                                        ___atomNameSpan[idx] = (index, len(___term))
                                        if resNameSpan[idx][0] == ___atomNameSpan[idx][0]:
                                            resNameLike[idx] = False
                                        break
                            for compId in self.compIdSet:
                                _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, atomId, leave_unmatched=True)
                                if details is None:
                                    ___atomNameLike[idx] = True
                                    ___atomNameSpan[idx] = (index, len(___term))
                                    break
                                if with_compid is not None and atomId.startswith(with_compid):
                                    continue
                                _atomId = translateToStdAtomName(atomId, compId, ccU=self.ccU)
                                _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, _atomId, leave_unmatched=True)
                                if details is None:
                                    ___atomNameLike[idx] = True
                                    ___atomNameSpan[idx] = (index, len(___term))
                                    break
                            if ___atomNameLike[idx]:
                                break

            if _atomNameLike[idx] and atomNameLike[idx]:
                concat = False
                if _atomNameSpan[idx][1] == atomNameSpan[idx][0]:
                    atomId = term[_atomNameSpan[idx][0]:atomNameSpan[idx][1]]
                    if resNameLike[idx]:
                        compId = term[resNameSpan[idx][0]:resNameSpan[idx][1]]
                        resId = term[resIdSpan[idx][0]:resIdSpan[idx][1]] if resIdLike[idx] else '.'
                        if len(compId) == 1 and hasOneLetterCodeSet:
                            compId = next(k for k, v in extMonDict3.items() if k in self.compIdSet and v == compId)
                            _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, atomId, leave_unmatched=True)
                            if details is None:
                                _atomNameLike[idx] = False
                                atomNameSpan[idx] = (_atomNameSpan[idx][0], atomNameSpan[idx][1])
                                if resNameSpan[idx][0] == atomNameSpan[idx][0]:
                                    resNameLike[idx] = False
                                concat = True
                            else:
                                _atomId = translateToStdAtomName(atomId, compId, ccU=self.ccU)
                                _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, _atomId, leave_unmatched=True)
                                if details is None:
                                    _atomNameLike[idx] = False
                                    atomNameSpan[idx] = (_atomNameSpan[idx][0], atomNameSpan[idx][1])
                                    if resNameSpan[idx][0] == atomNameSpan[idx][0]:
                                        resNameLike[idx] = False
                                    concat = True
                            if details is not None and numOfDim == 1:
                                _atomNameLike[idx] = False
                                for shift in range(_atomNameSpan[idx][0], atomNameSpan[idx][1]):
                                    _atomId = term[_atomNameSpan[idx][0] + shift:atomNameSpan[idx][1]]
                                    if len(_atomId) == 0:
                                        break
                                    if _atomId[0] == resId[0]:
                                        continue
                                    _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, _atomId, leave_unmatched=True)
                                    if details is None:
                                        _atomNameSpan[idx] = (_atomNameSpan[idx][0] + shift, len(_atomId))
                                        atomNameSpan[idx] = (_atomNameSpan[idx][0], atomNameSpan[idx][1])
                                        concat = True
                                        break
                                    __atomId = translateToStdAtomName(_atomId, compId, ccU=self.ccU)
                                    _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, __atomId, leave_unmatched=True)
                                    if details is None:
                                        _atomNameSpan[idx] = (_atomNameSpan[idx][0] + shift, len(_atomId))
                                        atomNameSpan[idx] = (_atomNameSpan[idx][0], atomNameSpan[idx][1])
                                        concat = True
                                        break
                        else:
                            _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, atomId, leave_unmatched=True)
                            if details is None:
                                _atomNameLike[idx] = False
                                atomNameSpan[idx] = (_atomNameSpan[idx][0], atomNameSpan[idx][1])
                                concat = True
                            else:
                                _atomId = translateToStdAtomName(atomId, compId, ccU=self.ccU)
                                _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, _atomId, leave_unmatched=True)
                                if details is None:
                                    _atomNameLike[idx] = False
                                    atomNameSpan[idx] = (_atomNameSpan[idx][0], atomNameSpan[idx][1])
                                    concat = True
                            if details is not None and numOfDim == 1:
                                _atomNameLike[idx] = False
                                for shift in range(_atomNameSpan[idx][0], atomNameSpan[idx][1]):
                                    _atomId = term[_atomNameSpan[idx][0] + shift:atomNameSpan[idx][1]]
                                    if len(_atomId) == 0:
                                        break
                                    if _atomId[0] == resId[0]:
                                        continue
                                    _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, _atomId, leave_unmatched=True)
                                    if details is None:
                                        _atomNameSpan[idx] = (_atomNameSpan[idx][0] + shift, len(_atomId))
                                        atomNameSpan[idx] = (_atomNameSpan[idx][0], atomNameSpan[idx][1])
                                        concat = True
                                        break
                                    __atomId = translateToStdAtomName(_atomId, compId, ccU=self.ccU)
                                    _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, __atomId, leave_unmatched=True)
                                    if details is None:
                                        _atomNameSpan[idx] = (_atomNameSpan[idx][0] + shift, len(_atomId))
                                        atomNameSpan[idx] = (_atomNameSpan[idx][0], atomNameSpan[idx][1])
                                        concat = True
                                        break
                    if not concat:
                        for compId in self.compIdSet:
                            _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, atomId, leave_unmatched=True)
                            if details is None:
                                _atomNameLike[idx] = False
                                atomNameSpan[idx] = (_atomNameSpan[idx][0], atomNameSpan[idx][1])
                                break
                            _atomId = translateToStdAtomName(atomId, compId, ccU=self.ccU)
                            _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, _atomId, leave_unmatched=True)
                            if details is None:
                                _atomNameLike[idx] = False
                                atomNameSpan[idx] = (_atomNameSpan[idx][0], atomNameSpan[idx][1])
                                break

            if __atomNameLike[idx] and _atomNameLike[idx] and atomNameLike[idx]:
                concat = False
                if __atomNameSpan[idx][1] == _atomNameSpan[idx][0] and _atomNameSpan[idx][1] == atomNameSpan[idx][0]:
                    atomId = term[__atomNameSpan[idx][0]:atomNameSpan[idx][1]]
                    if resNameLike[idx]:
                        compId = term[resNameSpan[idx][0]:resNameSpan[idx][1]]
                        if len(compId) == 1 and hasOneLetterCodeSet:
                            compId = next(k for k, v in extMonDict3.items() if k in self.compIdSet and v == compId)
                            _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, atomId, leave_unmatched=True)
                            if details is None:
                                __atomNameLike[idx] = _atomNameLike[idx] = False
                                atomNameSpan[idx] = (__atomNameSpan[idx][0], atomNameSpan[idx][1])
                                if resNameSpan[idx][0] == atomNameSpan[idx][0]:
                                    resNameLike[idx] = False
                                concat = True
                            else:
                                _atomId = translateToStdAtomName(atomId, compId, ccU=self.ccU)
                                _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, _atomId, leave_unmatched=True)
                                if details is None:
                                    __atomNameLike[idx] = _atomNameLike[idx] = False
                                    atomNameSpan[idx] = (__atomNameSpan[idx][0], atomNameSpan[idx][1])
                                    if resNameSpan[idx][0] == atomNameSpan[idx][0]:
                                        resNameLike[idx] = False
                                    concat = True

                    if not concat:
                        for compId in self.compIdSet:
                            _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, atomId, leave_unmatched=True)
                            if details is None:
                                __atomNameLike[idx] = _atomNameLike[idx] = False
                                atomNameSpan[idx] = (__atomNameSpan[idx][0], atomNameSpan[idx][1])
                                break
                            _atomId = translateToStdAtomName(atomId, compId, ccU=self.ccU)
                            _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, _atomId, leave_unmatched=True)
                            if details is None:
                                __atomNameLike[idx] = _atomNameLike[idx] = False
                                atomNameSpan[idx] = (__atomNameSpan[idx][0], atomNameSpan[idx][1])
                                break

            if ___atomNameLike[idx] and __atomNameLike[idx] and _atomNameLike[idx] and atomNameLike[idx]:
                concat = False
                if ___atomNameSpan[idx][1] == __atomNameSpan[idx][0] and __atomNameSpan[idx][1] == _atomNameSpan[idx][0]\
                   and _atomNameSpan[idx][1] == atomNameSpan[idx][0]:
                    atomId = term[___atomNameSpan[idx][0]:atomNameSpan[idx][1]]
                    if resNameLike[idx]:
                        compId = term[resNameSpan[idx][0]:resNameSpan[idx][1]]
                        if len(compId) == 1 and hasOneLetterCodeSet:
                            compId = next(k for k, v in extMonDict3.items() if k in self.compIdSet and v == compId)
                            _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, atomId, leave_unmatched=True)
                            if details is None:
                                ___atomNameLike[idx] = __atomNameLike[idx] = _atomNameLike[idx] = False
                                atomNameSpan[idx] = (___atomNameSpan[idx][0], atomNameSpan[idx][1])
                                if resNameSpan[idx][0] == atomNameSpan[idx][0]:
                                    resNameLike[idx] = False
                                concat = True
                            else:
                                _atomId = translateToStdAtomName(atomId, compId, ccU=self.ccU)
                                _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, _atomId, leave_unmatched=True)
                                if details is None:
                                    ___atomNameLike[idx] = __atomNameLike[idx] = _atomNameLike[idx] = False
                                    atomNameSpan[idx] = (___atomNameSpan[idx][0], atomNameSpan[idx][1])
                                    if resNameSpan[idx][0] == atomNameSpan[idx][0]:
                                        resNameLike[idx] = False
                                    concat = True
                    if not concat:
                        for compId in self.compIdSet:
                            _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, atomId, leave_unmatched=True)
                            if details is None:
                                ___atomNameLike[idx] = __atomNameLike[idx] = _atomNameLike[idx] = False
                                atomNameSpan[idx] = (___atomNameSpan[idx][0], atomNameSpan[idx][1])
                                break
                            _atomId = translateToStdAtomName(atomId, compId, ccU=self.ccU)
                            _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, _atomId, leave_unmatched=True)
                            if details is None:
                                ___atomNameLike[idx] = __atomNameLike[idx] = _atomNameLike[idx] = False
                                atomNameSpan[idx] = (___atomNameSpan[idx][0], atomNameSpan[idx][1])
                                break

            if __atomNameLike[idx] and _atomNameLike[idx]:
                concat = False
                if __atomNameSpan[idx][1] == _atomNameSpan[idx][0]:
                    atomId = term[__atomNameSpan[idx][0]:_atomNameSpan[idx][1]]
                    if resNameLike[idx]:
                        compId = term[resNameSpan[idx][0]:resNameSpan[idx][1]]
                        if len(compId) == 1 and hasOneLetterCodeSet:
                            compId = next(k for k, v in extMonDict3.items() if k in self.compIdSet and v == compId)
                            _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, atomId, leave_unmatched=True)
                            if details is None:
                                __atomNameLike[idx] = False
                                _atomNameSpan[idx] = (__atomNameSpan[idx][0], _atomNameSpan[idx][1])
                                if resNameSpan[idx][0] == _atomNameSpan[idx][0]:
                                    resNameLike[idx] = False
                                concat = True
                            else:
                                _atomId = translateToStdAtomName(atomId, compId, ccU=self.ccU)
                                _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, _atomId, leave_unmatched=True)
                                if details is None:
                                    __atomNameLike[idx] = False
                                    _atomNameSpan[idx] = (__atomNameSpan[idx][0], _atomNameSpan[idx][1])
                                    if resNameSpan[idx][0] == _atomNameSpan[idx][0]:
                                        resNameLike[idx] = False
                                    concat = True
                    if not concat:
                        for compId in self.compIdSet:
                            _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, atomId, leave_unmatched=True)
                            if details is None:
                                __atomNameLike[idx] = False
                                _atomNameSpan[idx] = (__atomNameSpan[idx][0], _atomNameSpan[idx][1])
                                break
                            _atomId = translateToStdAtomName(atomId, compId, ccU=self.ccU)
                            _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, _atomId, leave_unmatched=True)
                            if details is None:
                                __atomNameLike[idx] = False
                                _atomNameSpan[idx] = (__atomNameSpan[idx][0], _atomNameSpan[idx][1])
                                break

            if ___atomNameLike[idx] and __atomNameLike[idx] and _atomNameLike[idx]:
                concat = False
                if ___atomNameSpan[idx][1] == __atomNameSpan[idx][0] and __atomNameSpan[idx][1] == _atomNameSpan[idx][0]:
                    atomId = term[___atomNameSpan[idx][0]:_atomNameSpan[idx][1]]
                    if resNameLike[idx]:
                        compId = term[resNameSpan[idx][0]:resNameSpan[idx][1]]
                        if len(compId) == 1 and hasOneLetterCodeSet:
                            compId = next(k for k, v in extMonDict3.items() if k in self.compIdSet and v == compId)
                            _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, atomId, leave_unmatched=True)
                            if details is None:
                                ___atomNameLike[idx] = __atomNameLike[idx] = False
                                _atomNameSpan[idx] = (___atomNameSpan[idx][0], _atomNameSpan[idx][1])
                                if resNameSpan[idx][0] == _atomNameSpan[idx][0]:
                                    resNameLike[idx] = False
                                concat = True
                            else:
                                _atomId = translateToStdAtomName(atomId, compId, ccU=self.ccU)
                                _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, _atomId, leave_unmatched=True)
                                if details is None:
                                    ___atomNameLike[idx] = __atomNameLike[idx] = False
                                    _atomNameSpan[idx] = (___atomNameSpan[idx][0], _atomNameSpan[idx][1])
                                    if resNameSpan[idx][0] == _atomNameSpan[idx][0]:
                                        resNameLike[idx] = False
                                    concat = True
                    if not concat:
                        for compId in self.compIdSet:
                            _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, atomId, leave_unmatched=True)
                            if details is None:
                                ___atomNameLike[idx] = __atomNameLike[idx] = False
                                _atomNameSpan[idx] = (___atomNameSpan[idx][0], _atomNameSpan[idx][1])
                                break
                            _atomId = translateToStdAtomName(atomId, compId, ccU=self.ccU)
                            _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, _atomId, leave_unmatched=True)
                            if details is None:
                                ___atomNameLike[idx] = __atomNameLike[idx] = False
                                _atomNameSpan[idx] = (___atomNameSpan[idx][0], _atomNameSpan[idx][1])
                                break

            if ___atomNameLike[idx] and __atomNameLike[idx]:
                concat = False
                if ___atomNameSpan[idx][1] == __atomNameSpan[idx][0]:
                    atomId = term[___atomNameSpan[idx][0]:__atomNameSpan[idx][1]]
                    if resNameLike[idx]:
                        compId = term[resNameSpan[idx][0]:resNameSpan[idx][1]]
                        if len(compId) == 1 and hasOneLetterCodeSet:
                            compId = next(k for k, v in extMonDict3.items() if k in self.compIdSet and v == compId)
                            _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, atomId, leave_unmatched=True)
                            if details is None:
                                ___atomNameLike[idx] = False
                                __atomNameSpan[idx] = (___atomNameSpan[idx][0], __atomNameSpan[idx][1])
                                if resNameSpan[idx][0] == __atomNameSpan[idx][0]:
                                    resNameLike[idx] = False
                                concat = True
                            else:
                                _atomId = translateToStdAtomName(atomId, compId, ccU=self.ccU)
                                _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, _atomId, leave_unmatched=True)
                                if details is None:
                                    ___atomNameLike[idx] = False
                                    __atomNameSpan[idx] = (___atomNameSpan[idx][0], __atomNameSpan[idx][1])
                                    if resNameSpan[idx][0] == __atomNameSpan[idx][0]:
                                        resNameLike[idx] = False
                                    concat = True
                    if not concat:
                        for compId in self.compIdSet:
                            _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, atomId, leave_unmatched=True)
                            if details is None:
                                ___atomNameLike[idx] = False
                                __atomNameSpan[idx] = (___atomNameSpan[idx][0], __atomNameSpan[idx][1])
                                break
                            _atomId = translateToStdAtomName(atomId, compId, ccU=self.ccU)
                            _, _, details = self.nefT.get_valid_star_atom_in_xplor(compId, _atomId, leave_unmatched=True)
                            if details is None:
                                ___atomNameLike[idx] = False
                                __atomNameSpan[idx] = (___atomNameSpan[idx][0], __atomNameSpan[idx][1])
                                break

            if self.ass_expr_debug:
                print(f'{idx} {term!r} segid:{segIdLike[idx]} {term[segIdSpan[idx][0]:segIdSpan[idx][1]] if segIdLike[idx] else ""}, '
                      f'resid:{resIdLike[idx]} {term[resIdSpan[idx][0]:resIdSpan[idx][1]] if resIdLike[idx] else ""}, '
                      f'resname:{resNameLike[idx]} {term[resNameSpan[idx][0]:resNameSpan[idx][1]] if resNameLike[idx] else ""}, '
                      f'atomname:{atomNameLike[idx]} {term[atomNameSpan[idx][0]:atomNameSpan[idx][1]] if atomNameLike[idx] else ""}, '
                      f'_atomname:{_atomNameLike[idx]} {term[_atomNameSpan[idx][0]:_atomNameSpan[idx][1]] if _atomNameLike[idx] else ""}, '
                      f'__atomname:{__atomNameLike[idx]} {term[__atomNameSpan[idx][0]:__atomNameSpan[idx][1]] if __atomNameLike[idx] else ""}, '
                      f'___atomname:{___atomNameLike[idx]} {term[___atomNameSpan[idx][0]:___atomNameSpan[idx][1]] if ___atomNameLike[idx] else ""}')

        atomNameCount = 0
        for idx in range(lenStr):
            if atomNameLike[idx]:
                atomNameCount += 1
            if _atomNameLike[idx]:
                atomNameCount += 1
            if __atomNameLike[idx]:
                atomNameCount += 1
            if ___atomNameLike[idx]:
                atomNameCount += 1

        if atomNameCount < numOfDim:
            return None

        if atomNameCount > numOfDim > 1:
            atomNameCount = 0
            ignoreBefore = False
            for idx in range(lenStr - 1, 0, -1):
                if ignoreBefore:
                    atomNameLike[idx] = _atomNameLike[idx] = __atomNameLike[idx] = ___atomNameLike[idx] = False
                else:
                    if atomNameLike[idx]:
                        atomNameCount += 1
                    if _atomNameLike[idx]:
                        atomNameCount += 1
                    if __atomNameLike[idx]:
                        atomNameCount += 1
                    if ___atomNameLike[idx]:
                        atomNameCount += 1
                    if atomNameCount >= numOfDim:
                        ignoreBefore = True

        hasResName = hasResId = False
        for idx in range(lenStr):
            if ___atomNameLike[idx]:
                if resNameLike[idx]:
                    if not hasResName and resNameSpan[idx][0] < ___atomNameSpan[idx][0] and resNameSpan[idx][1] >= ___atomNameSpan[idx][1]:
                        ___atomNameLike[idx] = False
                    elif resNameSpan[idx][1] > ___atomNameSpan[idx][0]:
                        term = _str[idx]
                        if not hasResId and resNameSpan[idx][1] - resNameSpan[idx][0] == 3\
                           and term[resNameSpan[idx][0]:resNameSpan[idx][1]] == term[___atomNameSpan[idx][0]:___atomNameSpan[idx][1]]\
                           and any(_idx for _idx in range(idx + 1, lenStr) if __atomNameLike[_idx] or _atomNameLike[_idx] or atomNameLike[_idx]):
                            ___atomNameLike[idx] = False
                        else:
                            resNameLike[idx] = False
                if resIdLike[idx]:
                    if resIdSpan[idx][1] > ___atomNameSpan[idx][0]:
                        resIdLike[idx] = False
                if segIdLike[idx]:
                    if segIdSpan[idx][1] > ___atomNameSpan[idx][0]:
                        segIdLike[idx] = False

            elif __atomNameLike[idx]:
                if resNameLike[idx]:
                    if not hasResName and resNameSpan[idx][0] < __atomNameSpan[idx][0] and resNameSpan[idx][1] >= __atomNameSpan[idx][1]:
                        __atomNameLike[idx] = False
                    elif resNameSpan[idx][1] > __atomNameSpan[idx][0]:
                        term = _str[idx]
                        if not hasResId and resNameSpan[idx][1] - resNameSpan[idx][0] == 3\
                           and term[resNameSpan[idx][0]:resNameSpan[idx][1]] == term[__atomNameSpan[idx][0]:__atomNameSpan[idx][1]]\
                           and any(_idx for _idx in range(idx + 1, lenStr) if _atomNameLike[_idx] or atomNameLike[_idx]):
                            __atomNameLike[idx] = False
                        else:
                            resNameLike[idx] = False
                if resIdLike[idx]:
                    if resIdSpan[idx][1] > __atomNameSpan[idx][0]:
                        resIdLike[idx] = False
                if segIdLike[idx]:
                    if segIdSpan[idx][1] > __atomNameSpan[idx][0]:
                        segIdLike[idx] = False

            elif _atomNameLike[idx]:
                if resNameLike[idx]:
                    if not hasResName and resNameSpan[idx][0] < _atomNameSpan[idx][0] and resNameSpan[idx][1] >= _atomNameSpan[idx][1]:
                        _atomNameLike[idx] = False
                    elif resNameSpan[idx][1] > _atomNameSpan[idx][0]:
                        term = _str[idx]
                        if not hasResId and resNameSpan[idx][1] - resNameSpan[idx][0] == 3\
                           and term[resNameSpan[idx][0]:resNameSpan[idx][1]] == term[_atomNameSpan[idx][0]:_atomNameSpan[idx][1]]\
                           and any(_idx for _idx in range(idx + 1, lenStr) if atomNameLike[_idx]):
                            _atomNameLike[idx] = False
                        else:
                            resNameLike[idx] = False
                if resIdLike[idx]:
                    if resIdSpan[idx][1] > _atomNameSpan[idx][0]:
                        resIdLike[idx] = False
                if segIdLike[idx]:
                    if segIdSpan[idx][1] > _atomNameSpan[idx][0]:
                        segIdLike[idx] = False

            elif atomNameLike[idx]:
                if resNameLike[idx]:
                    if not hasResName and resNameSpan[idx][0] < atomNameSpan[idx][0] and resNameSpan[idx][1] >= atomNameSpan[idx][1]:
                        atomNameLike[idx] = False
                    elif resNameSpan[idx][1] > atomNameSpan[idx][0]:
                        term = _str[idx]
                        if not hasResId and resNameSpan[idx][1] - resNameSpan[idx][0] == 3\
                           and term[resNameSpan[idx][0]:resNameSpan[idx][1]] == term[atomNameSpan[idx][0]:atomNameSpan[idx][1]]\
                           and any(_idx for _idx in range(idx + 1, lenStr) if atomNameLike[_idx]):
                            atomNameLike[idx] = False
                        else:
                            if forceOneLetterCodeSet and resIdLike[idx] and len(atomNameLike) > idx + 1 and atomNameLike[idx + 1]:
                                atomNameLike[idx] = False
                            else:
                                resNameLike[idx] = False
                if resIdLike[idx]:
                    if resIdSpan[idx][1] > atomNameSpan[idx][0]:
                        if forceOneLetterCodeSet and resNameLike[idx]:
                            pass
                        else:
                            resIdLike[idx] = False
                if segIdLike[idx]:
                    if segIdSpan[idx][1] > atomNameSpan[idx][0]:
                        segIdLike[idx] = False

            if resNameLike[idx]:
                hasResName = True
                if segIdLike[idx]:
                    if segIdSpan[idx][1] > resNameSpan[idx][0]:
                        if numOfDim > 1 or not any(resNameLike[_idx] for _idx in range(idx + 1, lenStr))\
                           or (resIdLike[idx] and segIdSpan[idx][1] == resIdSpan[idx][0]):
                            _resName = _str[idx][resNameSpan[idx][0]:resNameSpan[idx][1]]
                            _resId = next((int(_str[_idx][resIdSpan[_idx][0]:resIdSpan[_idx][1]]) for _idx in range(idx + 1, lenStr) if resIdLike[_idx]), None)
                            _atomName = next((_str[_idx][atomNameSpan[_idx][0]:atomNameSpan[_idx][1]] for _idx in range(idx + 1, lenStr) if atomNameLike[_idx]), None)
                            checked = True
                            if _resId is not None and _atomName is not None and len(_resName) == 1 and len(self.polySeq) > 1:
                                for ps in self.polySeq:
                                    _, _, _compId_ = self.getRealChainSeqId(ps, _resId, None)
                                    if _resName == ps['auth_chain_id'] and _compId_ in monDict3 and _resName != monDict3[_compId_]:
                                        checked = False
                                        break
                            if checked:
                                segIdLike[idx] = False
                            else:
                                resNameLike[idx] = False
                        else:
                            if not hasResId and resNameSpan[idx][1] - resNameSpan[idx][0] == 3\
                               and term[resNameSpan[idx][0]:resNameSpan[idx][1]] == term[atomNameSpan[idx][0]:atomNameSpan[idx][1]]\
                               and any(_idx for _idx in range(idx + 1, lenStr) if atomNameLike[_idx]):
                                atomNameLike[idx] = False
                            else:
                                resNameLike[idx] = False

            if resIdLike[idx]:
                hasResId = True
                if atomNameLike[idx]:
                    if resIdSpan[idx][1] > atomNameSpan[idx][0]:
                        resIdLike[idx] = False

            if self.ass_expr_debug:
                print(f' -> {idx} segid:{segIdLike[idx]}, resid:{resIdLike[idx]}, resname:{resNameLike[idx]}, '
                      f'atomname:{atomNameLike[idx]}, _atomname:{_atomNameLike[idx]}, __atomname:{__atomNameLike[idx]}, ___atomname:{___atomNameLike[idx]}')

        resIdCount = 0
        for idx in range(lenStr):
            if resIdLike[idx]:
                resIdCount += 1

        _resId = [h['seq_id'] for h in hint] if hint is not None else None
        if resIdCount == 0:
            if _resId is None and _ligAtomId is None:
                return None

        _resNameDict = [{h['auth_seq_id']: h['comp_id']} for h in hint] if hint is not None else None

        resIdLater = resIdCount == numOfDim
        if resIdLater:
            atomNameCount = 0
            for idx in range(lenStr):
                if atomNameLike[idx]:
                    atomNameCount += 1
            resIdLater = atomNameCount == numOfDim
            if resIdLater:
                anyResId = False
                for idx in range(lenStr):
                    if resIdLike[idx]:
                        anyResId = True
                    if atomNameLike[idx]:
                        if anyResId:
                            resIdLater = False
                        break

        if self.ass_expr_debug:
            print(f'num_of_dim: {numOfDim}, resid_count: {resIdCount}, resid_later:{resIdLater}')

        def is_valid_chain_assign(chain_assign, res_name):
            return len(chain_assign) > 0 and ((res_name in extMonDict3 and any(a for a in chain_assign if a[2] == res_name)) or res_name not in extMonDict3)

        ret = []

        segId = resId = resName = atomName = _segId_ = _resId_ = authResId = None
        dimId = 1
        for idx, term in enumerate(_str):
            if segIdLike[idx]:
                segId = term[segIdSpan[idx][0]:segIdSpan[idx][1]]
                if _segId_ is not None and segId != _segId_:
                    resId = resName = None
                _segId_ = segId
            if resIdLike[idx]:
                resId = authResId = int(term[resIdSpan[idx][0]:resIdSpan[idx][1]])
                if _resId_ is not None and resId != _resId_:
                    resName = None
                _resId_ = resId
            if resNameLike[idx]:
                resName = term[resNameSpan[idx][0]:resNameSpan[idx][1]]
                if len(resName) == 1 and hasOneLetterCodeSet:
                    resName = next(k for k, v in extMonDict3.items() if k in self.compIdSet and v == resName)
            elif _resNameDict is not None and resName is None and len(ret) < len(_resNameDict)\
                    and _resId is not None and len(ret) < len(_resId) and _resId[len(ret)] in _resNameDict[len(ret)]\
                    and (authResId is None or authResId == _resId[len(ret)]):
                resName = _resNameDict[len(ret)][_resId[len(ret)]]
            if ___atomNameLike[idx]:
                if resIdLater:
                    for _idx, _term in enumerate(_str):
                        if _idx > idx and resIdLike[_idx]:
                            resId = int(_term[resIdSpan[_idx][0]:resIdSpan[_idx][1]])
                            segId = resName = None
                            break
                if resId is None:
                    if _resId is None or len(ret) >= len(_resId):
                        return None
                    resId = _resId[len(ret)]
                atomName = term[___atomNameSpan[idx][0]:___atomNameSpan[idx][1]]
                if self.hasPolySeq:
                    if segId is None and resName is None:
                        chainAssign = self.assignCoordPolymerSequenceWithChainIdWithoutCompId(self.__defaultSegId, resId, atomName, src_index)
                        if len(chainAssign) > 0:
                            if self.__defaultSegId is None:
                                idx = next((chainAssign.index(a) for a in chainAssign if a[1] == resId), -1)
                            else:
                                idx = next((chainAssign.index(a) for a in chainAssign if a[0] == self.__defaultSegId and a[1] == resId), -1)
                                if idx == -1:
                                    idx = next((chainAssign.index(a) for a in chainAssign if a[1] == resId), -1)
                            if idx != -1:
                                # if self.__defaultSegId is None:
                                self.__defaultSegId = chainAssign[idx][0]
                            else:
                                idx = 0
                            segId, _, resName, _ = chainAssign[idx]
                        else:
                            chainAssign = self.assignCoordPolymerSequenceWithoutCompId(resId, atomName, src_index)
                            if len(chainAssign) > 0:
                                if self.__defaultSegId is None:
                                    idx = next((chainAssign.index(a) for a in chainAssign if a[1] == resId), -1)
                                else:
                                    idx = next((chainAssign.index(a) for a in chainAssign if a[0] == self.__defaultSegId and a[1] == resId), -1)
                                    if idx == -1:
                                        idx = next((chainAssign.index(a) for a in chainAssign if a[1] == resId), -1)
                                if idx != -1:
                                    # if self.__defaultSegId is None:
                                    # self.__defaultSegId = chainAssign[idx][0]
                                    pass
                                else:
                                    idx = 0
                                segId, _, resName, _ = chainAssign[idx]
                    elif segId is None:
                        chainAssign, _ = self.assignCoordPolymerSequence(self.__defaultSegId,
                                                                         resId, resName, atomName, src_index)
                        is_valid = is_valid_chain_assign(chainAssign, resName)
                        if not is_valid:
                            if self.__defaultSegId != self.__defaultSegId__:
                                __preferAuthSeq = self.__preferAuthSeq
                                self.__preferAuthSeq = not __preferAuthSeq
                                chainAssign, _ = self.assignCoordPolymerSequenceWithChainId(self.__defaultSegId__,
                                                                                            resId, resName, atomName, src_index)
                                is_valid = is_valid_chain_assign(chainAssign, resName)
                                self.__preferAuthSeq = __preferAuthSeq
                        if is_valid:
                            idx = next((chainAssign.index(a) for a in chainAssign if a[2] == resName), -1)
                            if idx != -1:
                                # if self.__defaultSegId is None:
                                self.__defaultSegId = chainAssign[idx][0]
                            else:
                                idx = 0
                            segId = chainAssign[idx][0]
                        else:
                            chainAssign, _ = self.assignCoordPolymerSequence(None,
                                                                             resId, resName, atomName, src_index)
                            if is_valid_chain_assign(chainAssign, resName):
                                idx = next((chainAssign.index(a) for a in chainAssign if a[2] == resName), -1)
                                if idx != -1:
                                    # if self.__defaultSegId is None:
                                    self.__defaultSegId = chainAssign[idx][0]
                                    if self.reasons is None:
                                        if 'default_seg_id' not in self.reasonsForReParsing:
                                            self.reasonsForReParsing['default_seg_id'] = {}
                                        if self.cur_list_id not in self.reasonsForReParsing['default_seg_id']:
                                            self.reasonsForReParsing['default_seg_id'][self.cur_list_id] = self.__defaultSegId
                                else:
                                    idx = 0
                                segId = chainAssign[idx][0]
                    elif resName is None:
                        chainAssign = self.assignCoordPolymerSequenceWithChainIdWithoutCompId(segId, resId, atomName, src_index)
                        if len(chainAssign) > 0:
                            idx = next((chainAssign.index(a) for a in chainAssign if a[1] == resId), 0)
                            resName = chainAssign[idx][2]
                    _, _, details = self.nefT.get_valid_star_atom_in_xplor(resName, atomName, leave_unmatched=True)
                    if details is not None:
                        atomName = translateToStdAtomName(atomName, resName, ccU=self.ccU)
                    ret.append({'dim_id': dimId, 'chain_id': segId, 'seq_id': resId, 'auth_seq_id': authResId, 'comp_id': resName, 'atom_id': atomName})
                else:
                    ass = {'dim': dimId, 'atom_id': atomName}
                    if segId is not None:
                        ass['chain_id'] = segId
                    if resId is not None:
                        ass['seq_id'] = resId
                    if resName is not None:
                        ass['comp_id'] = resName
                    ret.append(ass)
                dimId += 1
            if __atomNameLike[idx]:
                if resIdLater:
                    for _idx, _term in enumerate(_str):
                        if _idx > idx and resIdLike[_idx]:
                            resId = int(_term[resIdSpan[_idx][0]:resIdSpan[_idx][1]])
                            segId = resName = None
                            break
                if resId is None:
                    if _resId is None or len(ret) >= len(_resId):
                        return None
                    resId = _resId[len(ret)]
                atomName = term[__atomNameSpan[idx][0]:__atomNameSpan[idx][1]]
                if self.hasPolySeq:
                    if segId is None and resName is None:
                        chainAssign = self.assignCoordPolymerSequenceWithChainIdWithoutCompId(self.__defaultSegId, resId, atomName, src_index)
                        if len(chainAssign) > 0:
                            if self.__defaultSegId is None:
                                idx = next((chainAssign.index(a) for a in chainAssign if a[1] == resId), -1)
                            else:
                                idx = next((chainAssign.index(a) for a in chainAssign if a[0] == self.__defaultSegId and a[1] == resId), -1)
                                if idx == -1:
                                    idx = next((chainAssign.index(a) for a in chainAssign if a[1] == resId), -1)
                            if idx != -1:
                                # if self.__defaultSegId is None:
                                self.__defaultSegId = chainAssign[idx][0]
                            else:
                                idx = 0
                            segId, _, resName, _ = chainAssign[idx]
                        else:
                            chainAssign = self.assignCoordPolymerSequenceWithoutCompId(resId, atomName, src_index)
                            if len(chainAssign) > 0:
                                if self.__defaultSegId is None:
                                    idx = next((chainAssign.index(a) for a in chainAssign if a[1] == resId), -1)
                                else:
                                    idx = next((chainAssign.index(a) for a in chainAssign if a[0] == self.__defaultSegId and a[1] == resId), -1)
                                    if idx == -1:
                                        idx = next((chainAssign.index(a) for a in chainAssign if a[1] == resId), -1)
                                if idx != -1:
                                    # if self.__defaultSegId is None:
                                    # self.__defaultSegId = chainAssign[idx][0]
                                    pass
                                else:
                                    idx = 0
                                segId, _, resName, _ = chainAssign[idx]
                    elif segId is None:
                        chainAssign, _ = self.assignCoordPolymerSequence(self.__defaultSegId,
                                                                         resId, resName, atomName, src_index)
                        is_valid = is_valid_chain_assign(chainAssign, resName)
                        if not is_valid:
                            if self.__defaultSegId != self.__defaultSegId__:
                                __preferAuthSeq = self.__preferAuthSeq
                                self.__preferAuthSeq = not __preferAuthSeq
                                chainAssign, _ = self.assignCoordPolymerSequenceWithChainId(self.__defaultSegId__,
                                                                                            resId, resName, atomName, src_index)
                                is_valid = is_valid_chain_assign(chainAssign, resName)
                                self.__preferAuthSeq = __preferAuthSeq
                        if is_valid:
                            idx = next((chainAssign.index(a) for a in chainAssign if a[2] == resName), -1)
                            if idx != -1:
                                # if self.__defaultSegId is None:
                                self.__defaultSegId = chainAssign[idx][0]
                            else:
                                idx = 0
                            segId = chainAssign[idx][0]
                        else:
                            chainAssign, _ = self.assignCoordPolymerSequence(None,
                                                                             resId, resName, atomName, src_index)
                            if is_valid_chain_assign(chainAssign, resName):
                                idx = next((chainAssign.index(a) for a in chainAssign if a[2] == resName), -1)
                                if idx != -1:
                                    # if self.__defaultSegId is None:
                                    self.__defaultSegId = chainAssign[idx][0]
                                    if self.reasons is None:
                                        if 'default_seg_id' not in self.reasonsForReParsing:
                                            self.reasonsForReParsing['default_seg_id'] = {}
                                        if self.cur_list_id not in self.reasonsForReParsing['default_seg_id']:
                                            self.reasonsForReParsing['default_seg_id'][self.cur_list_id] = self.__defaultSegId
                                else:
                                    idx = 0
                                segId = chainAssign[idx][0]
                    elif resName is None:
                        chainAssign = self.assignCoordPolymerSequenceWithChainIdWithoutCompId(segId, resId, atomName, src_index)
                        if len(chainAssign) > 0:
                            idx = next((chainAssign.index(a) for a in chainAssign if a[1] == resId), 0)
                            resName = chainAssign[idx][2]
                    _, _, details = self.nefT.get_valid_star_atom_in_xplor(resName, atomName, leave_unmatched=True)
                    if details is not None:
                        atomName = translateToStdAtomName(atomName, resName, ccU=self.ccU)
                    ret.append({'dim_id': dimId, 'chain_id': segId, 'seq_id': resId, 'auth_seq_id': authResId, 'comp_id': resName, 'atom_id': atomName})
                else:
                    ass = {'dim': dimId, 'atom_id': atomName}
                    if segId is not None:
                        ass['chain_id'] = segId
                    if resId is not None:
                        ass['seq_id'] = resId
                    if resName is not None:
                        ass['comp_id'] = resName
                    ret.append(ass)
                dimId += 1
            if _atomNameLike[idx]:
                if resIdLater:
                    for _idx, _term in enumerate(_str):
                        if _idx > idx and resIdLike[_idx]:
                            resId = int(_term[resIdSpan[_idx][0]:resIdSpan[_idx][1]])
                            segId = resName = None
                            break
                if resId is None:
                    if _resId is None or len(ret) >= len(_resId):
                        return None
                    resId = _resId[len(ret)]
                atomName = term[_atomNameSpan[idx][0]:_atomNameSpan[idx][1]]
                if self.hasPolySeq:
                    if segId is None and resName is None:
                        chainAssign = self.assignCoordPolymerSequenceWithChainIdWithoutCompId(self.__defaultSegId, resId, atomName, src_index)
                        if len(chainAssign) > 0:
                            if self.__defaultSegId is None:
                                idx = next((chainAssign.index(a) for a in chainAssign if a[1] == resId), -1)
                            else:
                                idx = next((chainAssign.index(a) for a in chainAssign if a[0] == self.__defaultSegId and a[1] == resId), -1)
                                if idx == -1:
                                    idx = next((chainAssign.index(a) for a in chainAssign if a[1] == resId), -1)
                            if idx != -1:
                                # if self.__defaultSegId is None:
                                self.__defaultSegId = chainAssign[idx][0]
                            else:
                                idx = 0
                            segId, _, resName, _ = chainAssign[idx]
                        else:
                            chainAssign = self.assignCoordPolymerSequenceWithoutCompId(resId, atomName, src_index)
                            if len(chainAssign) > 0:
                                if self.__defaultSegId is None:
                                    idx = next((chainAssign.index(a) for a in chainAssign if a[1] == resId), -1)
                                else:
                                    idx = next((chainAssign.index(a) for a in chainAssign if a[0] == self.__defaultSegId and a[1] == resId), -1)
                                    if idx == -1:
                                        idx = next((chainAssign.index(a) for a in chainAssign if a[1] == resId), -1)
                                if idx != -1:
                                    # if self.__defaultSegId is None:
                                    # self.__defaultSegId = chainAssign[idx][0]
                                    pass
                                else:
                                    idx = 0
                                segId, _, resName, _ = chainAssign[idx]
                    elif segId is None:
                        chainAssign, _ = self.assignCoordPolymerSequence(self.__defaultSegId,
                                                                         resId, resName, atomName, src_index)
                        is_valid = is_valid_chain_assign(chainAssign, resName)
                        if not is_valid:
                            if self.__defaultSegId != self.__defaultSegId__:
                                __preferAuthSeq = self.__preferAuthSeq
                                self.__preferAuthSeq = not __preferAuthSeq
                                chainAssign, _ = self.assignCoordPolymerSequenceWithChainId(self.__defaultSegId__,
                                                                                            resId, resName, atomName, src_index)
                                is_valid = is_valid_chain_assign(chainAssign, resName)
                                self.__preferAuthSeq = __preferAuthSeq
                        if is_valid:
                            idx = next((chainAssign.index(a) for a in chainAssign if a[2] == resName), -1)
                            if idx != -1:
                                # if self.__defaultSegId is None:
                                self.__defaultSegId = chainAssign[idx][0]
                            else:
                                idx = 0
                            segId = chainAssign[idx][0]
                        else:
                            chainAssign, _ = self.assignCoordPolymerSequence(None,
                                                                             resId, resName, atomName, src_index)
                            if is_valid_chain_assign(chainAssign, resName):
                                idx = next((chainAssign.index(a) for a in chainAssign if a[2] == resName), -1)
                                if idx != -1:
                                    # if self.__defaultSegId is None:
                                    self.__defaultSegId = chainAssign[idx][0]
                                    if self.reasons is None:
                                        if 'default_seg_id' not in self.reasonsForReParsing:
                                            self.reasonsForReParsing['default_seg_id'] = {}
                                        if self.cur_list_id not in self.reasonsForReParsing['default_seg_id']:
                                            self.reasonsForReParsing['default_seg_id'][self.cur_list_id] = self.__defaultSegId
                                else:
                                    idx = 0
                                segId = chainAssign[idx][0]
                    elif resName is None:
                        chainAssign = self.assignCoordPolymerSequenceWithChainIdWithoutCompId(segId, resId, atomName, src_index)
                        if len(chainAssign) > 0:
                            idx = next((chainAssign.index(a) for a in chainAssign if a[1] == resId), 0)
                            resName = chainAssign[idx][2]
                    _, _, details = self.nefT.get_valid_star_atom_in_xplor(resName, atomName, leave_unmatched=True)
                    if details is not None:
                        atomName = translateToStdAtomName(atomName, resName, ccU=self.ccU)
                    ret.append({'dim_id': dimId, 'chain_id': segId, 'seq_id': resId, 'auth_seq_id': authResId, 'comp_id': resName, 'atom_id': atomName})
                else:
                    ass = {'dim': dimId, 'atom_id': atomName}
                    if segId is not None:
                        ass['chain_id'] = segId
                    if resId is not None:
                        ass['seq_id'] = resId
                    if resName is not None:
                        ass['comp_id'] = resName
                    ret.append(ass)
                dimId += 1
            if atomNameLike[idx]:
                if resIdLater:
                    for _idx, _term in enumerate(_str):
                        if _idx > idx and resIdLike[_idx]:
                            resId = int(_term[resIdSpan[_idx][0]:resIdSpan[_idx][1]])
                            segId = resName = None
                            break
                if resId is None and _ligAtomId is None:
                    if _resId is None or len(ret) >= len(_resId):
                        return None
                    resId = _resId[len(ret)]
                if _ligAtomId is not None:
                    resId = _ligSeqId
                atomName = term[atomNameSpan[idx][0]:atomNameSpan[idx][1]]
                if self.hasPolySeq:
                    if segId is None and resName is None:
                        chainAssign = self.assignCoordPolymerSequenceWithChainIdWithoutCompId(self.__defaultSegId, resId, atomName, src_index)
                        if len(chainAssign) > 0:
                            if self.__defaultSegId is None:
                                idx = next((chainAssign.index(a) for a in chainAssign if a[1] == resId), -1)
                            else:
                                idx = next((chainAssign.index(a) for a in chainAssign if a[0] == self.__defaultSegId and a[1] == resId), -1)
                                if idx == -1:
                                    idx = next((chainAssign.index(a) for a in chainAssign if a[1] == resId), -1)
                            if idx != -1:
                                # if self.__defaultSegId is None:
                                self.__defaultSegId = chainAssign[idx][0]
                            else:
                                idx = 0
                            segId, _, resName, _ = chainAssign[idx]
                        else:
                            chainAssign = self.assignCoordPolymerSequenceWithoutCompId(resId, atomName, src_index)
                            if len(chainAssign) > 0:
                                if self.__defaultSegId is None:
                                    idx = next((chainAssign.index(a) for a in chainAssign if a[1] == resId), -1)
                                else:
                                    idx = next((chainAssign.index(a) for a in chainAssign if a[0] == self.__defaultSegId and a[1] == resId), -1)
                                    if idx == -1:
                                        idx = next((chainAssign.index(a) for a in chainAssign if a[1] == resId), -1)
                                if idx != -1:
                                    # if self.__defaultSegId is None:
                                    # self.__defaultSegId = chainAssign[idx][0]
                                    pass
                                else:
                                    idx = 0
                                segId, _, resName, _ = chainAssign[idx]
                    elif segId is None:
                        chainAssign, _ = self.assignCoordPolymerSequence(self.__defaultSegId,
                                                                         resId, resName, atomName, src_index)
                        is_valid = is_valid_chain_assign(chainAssign, resName)
                        if not is_valid:
                            if self.__defaultSegId != self.__defaultSegId__:
                                __preferAuthSeq = self.__preferAuthSeq
                                self.__preferAuthSeq = not __preferAuthSeq
                                chainAssign, _ = self.assignCoordPolymerSequenceWithChainId(self.__defaultSegId__,
                                                                                            resId, resName, atomName, src_index)
                                is_valid = is_valid_chain_assign(chainAssign, resName)
                                self.__preferAuthSeq = __preferAuthSeq
                        if is_valid:
                            idx = next((chainAssign.index(a) for a in chainAssign if a[2] == resName), -1)
                            if idx != -1:
                                # if self.__defaultSegId is None:
                                self.__defaultSegId = chainAssign[idx][0]
                            else:
                                idx = 0
                            segId = chainAssign[idx][0]
                        else:
                            chainAssign, _ = self.assignCoordPolymerSequence(None,
                                                                             resId, resName, atomName, src_index)
                            if is_valid_chain_assign(chainAssign, resName):
                                idx = next((chainAssign.index(a) for a in chainAssign if a[2] == resName), -1)
                                if idx != -1:
                                    # if self.__defaultSegId is None:
                                    self.__defaultSegId = chainAssign[idx][0]
                                    if self.reasons is None:
                                        if 'default_seg_id' not in self.reasonsForReParsing:
                                            self.reasonsForReParsing['default_seg_id'] = {}
                                        if self.cur_list_id not in self.reasonsForReParsing['default_seg_id']:
                                            self.reasonsForReParsing['default_seg_id'][self.cur_list_id] = self.__defaultSegId
                                else:
                                    idx = 0
                                segId = chainAssign[idx][0]
                    elif resName is None:
                        chainAssign = self.assignCoordPolymerSequenceWithChainIdWithoutCompId(segId, resId, atomName, src_index)
                        if len(chainAssign) > 0:
                            idx = next((chainAssign.index(a) for a in chainAssign if a[1] == resId), 0)
                            resName = chainAssign[idx][2]
                    _, _, details = self.nefT.get_valid_star_atom_in_xplor(resName, atomName, leave_unmatched=True)
                    if details is not None:
                        atomName = translateToStdAtomName(atomName, resName, ccU=self.ccU)
                    ret.append({'dim_id': dimId, 'chain_id': segId, 'seq_id': resId, 'auth_seq_id': authResId, 'comp_id': resName, 'atom_id': atomName})
                else:
                    ass = {'dim': dimId, 'atom_id': atomName}
                    if segId is not None:
                        ass['chain_id'] = segId
                    if resId is not None:
                        ass['seq_id'] = resId
                    if resName is not None:
                        ass['comp_id'] = resName
                    ret.append(ass)
                dimId += 1
            elif atomNameLike_[idx] and siblingAtomName[idx] is not None:
                if resIdLater:
                    for _idx, _term in enumerate(_str):
                        if _idx > idx and resIdLike[_idx]:
                            resId = int(_term[resIdSpan[_idx][0]:resIdSpan[_idx][1]])
                            segId = resName = None
                            break
                if resId is None:
                    if _resId is None or len(ret) >= len(_resId):
                        return None
                    resId = _resId[len(ret)]
                for atomName in siblingAtomName[idx]:
                    if self.hasPolySeq:
                        if segId is None and resName is None:
                            chainAssign = self.assignCoordPolymerSequenceWithChainIdWithoutCompId(self.__defaultSegId, resId, atomName, src_index)
                            if len(chainAssign) > 0:
                                if self.__defaultSegId is None:
                                    idx = next((chainAssign.index(a) for a in chainAssign if a[1] == resId), -1)
                                else:
                                    idx = next((chainAssign.index(a) for a in chainAssign if a[0] == self.__defaultSegId and a[1] == resId), -1)
                                    if idx == -1:
                                        idx = next((chainAssign.index(a) for a in chainAssign if a[1] == resId), -1)
                                if idx != -1:
                                    # if self.__defaultSegId is None:
                                    self.__defaultSegId = chainAssign[idx][0]
                                else:
                                    idx = 0
                                segId, _, resName, _ = chainAssign[idx]
                            else:
                                chainAssign = self.assignCoordPolymerSequenceWithoutCompId(resId, atomName, src_index)
                                if len(chainAssign) > 0:
                                    if self.__defaultSegId is None:
                                        idx = next((chainAssign.index(a) for a in chainAssign if a[1] == resId), -1)
                                    else:
                                        idx = next((chainAssign.index(a) for a in chainAssign if a[0] == self.__defaultSegId and a[1] == resId), -1)
                                        if idx == -1:
                                            idx = next((chainAssign.index(a) for a in chainAssign if a[1] == resId), -1)
                                    if idx != -1:
                                        # if self.__defaultSegId is None:
                                        # self.__defaultSegId = chainAssign[idx][0]
                                        pass
                                    else:
                                        idx = 0
                                    segId, _, resName, _ = chainAssign[idx]
                        elif segId is None:
                            chainAssign, _ = self.assignCoordPolymerSequence(self.__defaultSegId,
                                                                             resId, resName, atomName, src_index)
                            is_valid = is_valid_chain_assign(chainAssign, resName)
                            if not is_valid:
                                if self.__defaultSegId != self.__defaultSegId__:
                                    __preferAuthSeq = self.__preferAuthSeq
                                    self.__preferAuthSeq = not __preferAuthSeq
                                    chainAssign, _ = self.assignCoordPolymerSequenceWithChainId(self.__defaultSegId__,
                                                                                                resId, resName, atomName, src_index)
                                    is_valid = is_valid_chain_assign(chainAssign, resName)
                                    self.__preferAuthSeq = __preferAuthSeq
                            if is_valid:
                                idx = next((chainAssign.index(a) for a in chainAssign if a[2] == resName), -1)
                                if idx != -1:
                                    # if self.__defaultSegId is None:
                                    self.__defaultSegId = chainAssign[idx][0]
                                else:
                                    idx = 0
                                segId = chainAssign[idx][0]
                            else:
                                chainAssign, _ = self.assignCoordPolymerSequence(None,
                                                                                 resId, resName, atomName, src_index)
                                if is_valid_chain_assign(chainAssign, resName):
                                    idx = next((chainAssign.index(a) for a in chainAssign if a[2] == resName), -1)
                                    if idx != -1:
                                        # if self.__defaultSegId is None:
                                        self.__defaultSegId = chainAssign[idx][0]
                                        if self.reasons is None:
                                            if 'default_seg_id' not in self.reasonsForReParsing:
                                                self.reasonsForReParsing['default_seg_id'] = {}
                                            if self.cur_list_id not in self.reasonsForReParsing['default_seg_id']:
                                                self.reasonsForReParsing['default_seg_id'][self.cur_list_id] = self.__defaultSegId
                                    else:
                                        idx = 0
                                    segId = chainAssign[idx][0]
                        elif resName is None:
                            chainAssign = self.assignCoordPolymerSequenceWithChainIdWithoutCompId(segId, resId, atomName, src_index)
                            if len(chainAssign) > 0:
                                idx = next((chainAssign.index(a) for a in chainAssign if a[1] == resId), 0)
                                resName = chainAssign[idx][2]
                        _, _, details = self.nefT.get_valid_star_atom_in_xplor(resName, atomName, leave_unmatched=True)
                        if details is not None:
                            atomName = translateToStdAtomName(atomName, resName, ccU=self.ccU)
                        ret.append({'dim_id': dimId, 'chain_id': segId, 'seq_id': resId, 'auth_seq_id': authResId, 'comp_id': resName, 'atom_id': atomName})
                    else:
                        ass = {'dim': dimId, 'atom_id': atomName}
                        if segId is not None:
                            ass['chain_id'] = segId
                        if resId is not None:
                            ass['seq_id'] = resId
                        if resName is not None:
                            ass['comp_id'] = resName
                        ret.append(ass)
                    dimId += 1

        return ret if len(ret) > 0 else None

    def getRealChainSeqId(self, ps: dict, seqId: int, compId: Optional[str], isPolySeq: bool = True) -> Tuple[str, int, Optional[str]]:
        if compId is not None:
            compId = _compId = translateToStdResName(compId, ccU=self.ccU)
            if len(_compId) == 2 and _compId.startswith('D'):
                _compId = compId[1]
        if not self.__preferAuthSeq:
            seqKey = (ps['auth_chain_id' if 'auth_chain_id' in ps else 'chain_id'], seqId)
            if seqKey in self.__labelToAuthSeq:
                _chainId, _seqId = self.__labelToAuthSeq[seqKey]
                if _seqId in ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id']:
                    return _chainId, _seqId, ps['comp_id'][ps['seq_id'].index(seqId)]
                if seqKey[1] in ps['seq_id']:  # resolve conflict between label/auth sequence schemes of polymer/non-polymer (2l90)
                    idx = ps['seq_id'].index(seqKey[1])
                    return _chainId, ps['auth_seq_id'][idx], ps['comp_id'][idx]
        if seqId in ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id']:
            if compId is None:
                return ps['auth_chain_id' if 'auth_chain_id' in ps else 'chain_id'], seqId, ps['comp_id'][ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id'].index(seqId)]
            for idx in [_idx for _idx, _seqId in enumerate(ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id']) if _seqId == seqId]:
                if 'alt_comp_id' in ps and idx < len(ps['alt_comp_id']):
                    if compId in (ps['comp_id'][idx], ps['auth_comp_id' if 'auth_comp_id' in ps else 'comp_id'][idx], ps['alt_comp_id'][idx]):
                        return ps['auth_chain_id' if 'auth_chain_id' in ps else 'chain_id'], seqId, ps['comp_id'][idx]
                    if compId != _compId and _compId in (ps['comp_id'][idx], ps['auth_comp_id' if 'auth_comp_id' in ps else 'comp_id'][idx], ps['alt_comp_id'][idx]):
                        return ps['auth_chain_id' if 'auth_chain_id' in ps else 'chain_id'], seqId, ps['comp_id'][idx]
                if compId in (ps['comp_id'][idx], ps['auth_comp_id' if 'auth_comp_id' in ps else 'comp_id'][idx])\
                   or (isPolySeq and seqId == 1
                       and ((compId.endswith('-N') and all(c in ps['comp_id'][idx] for c in compId.split('-')[0]))
                            or (ps['comp_id'][idx] == 'PCA' and 'P' == compId[0] and ('GL' in compId or 'N' in compId)))):
                    return ps['auth_chain_id' if 'auth_chain_id' in ps else 'chain_id'], seqId, ps['comp_id'][idx]
                if compId != _compId and _compId in (ps['comp_id'][idx], ps['auth_comp_id' if 'auth_comp_id' in ps else 'comp_id'][idx]):
                    return ps['auth_chain_id' if 'auth_chain_id' in ps else 'chain_id'], seqId, ps['comp_id'][idx]
        if self.reasons is not None and 'extend_seq_scheme' in self.reasons:
            _ps = next((_ps for _ps in self.reasons['extend_seq_scheme'] if _ps['chain_id'] == ps['auth_chain_id' if 'auth_chain_id' in ps else 'chain_id']), None)
            if _ps is not None:
                if seqId in _ps['seq_id']:
                    return ps['auth_chain_id' if 'auth_chain_id' in ps else 'chain_id'], seqId, _ps['comp_id'][_ps['seq_id'].index(seqId)]
        return ps['auth_chain_id' if 'auth_chain_id' in ps else 'chain_id'], seqId, None

    def translateToStdResNameWrapper(self, seqId: int, compId: str, preferNonPoly: bool = False) -> str:
        _compId = compId
        refCompId = None
        for ps in self.polySeq:
            if preferNonPoly:
                continue
            _, _, refCompId = self.getRealChainSeqId(ps, seqId, _compId)
            if refCompId is not None:
                compId = translateToStdResName(_compId, refCompId=refCompId, ccU=self.ccU)
                if compId != _compId and compId in monDict3 and _compId in monDict3:
                    continue
                break
        if refCompId is None:
            compId = translateToStdResName(_compId, ccU=self.ccU)
        return compId

    def assignCoordPolymerSequence(self, refChainId: str, seqId: int, compId: str, atomId: str, index: int
                                   ) -> Tuple[List[Tuple[str, int, str, bool]], bool]:
        """ Assign polymer sequences of the coordinates.
        """

        _refChainId = refChainId

        chainAssign = set()
        asis = False

        _seqId = seqId
        _compId = compId

        fixedChainId = fixedSeqId = fixedCompId = None

        preferNonPoly = False

        self.__allow_ext_seq = False

        compId = self.translateToStdResNameWrapper(_seqId, _compId, preferNonPoly)

        if self.reasons is not None:
            if 'non_poly_remap' in self.reasons and _compId in self.reasons['non_poly_remap']\
               and seqId in self.reasons['non_poly_remap'][_compId]:
                fixedChainId, fixedSeqId = retrieveRemappedNonPoly(self.reasons['non_poly_remap'], None, refChainId, seqId, _compId)
                refChainId = fixedChainId
                preferNonPoly = True
            if 'branched_remap' in self.reasons and seqId in self.reasons['branched_remap']:
                fixedChainId, fixedSeqId = retrieveRemappedChainId(self.reasons['branched_remap'], seqId)
                refChainId = fixedChainId
                preferNonPoly = True
            if not preferNonPoly:
                if 'chain_id_remap' in self.reasons and seqId in self.reasons['chain_id_remap']:
                    fixedChainId, fixedSeqId = retrieveRemappedChainId(self.reasons['chain_id_remap'], seqId)
                    refChainId = fixedChainId
                elif 'chain_id_clone' in self.reasons and seqId in self.reasons['chain_id_clone']:
                    fixedChainId, fixedSeqId = retrieveRemappedChainId(self.reasons['chain_id_clone'], seqId)
                    refChainId = fixedChainId
                elif 'seq_id_remap' in self.reasons\
                        or 'chain_seq_id_remap' in self.reasons\
                        or 'ext_chain_seq_id_remap' in self.reasons:
                    if 'ext_chain_seq_id_remap' in self.reasons:
                        fixedChainId, fixedSeqId, fixedCompId =\
                            retrieveRemappedSeqIdAndCompId(self.reasons['ext_chain_seq_id_remap'], refChainId, seqId,
                                                           compId if compId in monDict3 else None)
                        self.__allow_ext_seq = fixedCompId is not None
                        if fixedSeqId is not None:
                            refChainId = fixedChainId
                    if fixedSeqId is None and 'chain_seq_id_remap' in self.reasons:
                        fixedChainId, fixedSeqId = retrieveRemappedSeqId(self.reasons['chain_seq_id_remap'], refChainId, seqId,
                                                                         compId if compId in monDict3 else None)
                        if fixedSeqId is not None:
                            refChainId = fixedChainId
                    if fixedSeqId is None and 'seq_id_remap' in self.reasons:
                        _, fixedSeqId = retrieveRemappedSeqId(self.reasons['seq_id_remap'], refChainId, seqId)
            if fixedSeqId is not None:
                _seqId = fixedSeqId

        updatePolySeqRst(self.polySeqCs, self.polySeq[0]['chain_id'] if refChainId is None else refChainId, _seqId, compId, _compId)

        types = self.csStat.getTypeOfCompId(compId)
        if all(not t for t in types) or compId in ('MTS', 'ORI'):
            types = None
        elif compId != _compId:
            if types != self.csStat.getTypeOfCompId(_compId):
                types = None

        def comp_id_unmatched_with(ps, cif_comp_id):
            if 'alt_comp_id' in ps and self.csStat.peptideLike(cif_comp_id) and compId.startswith('D') and len(compId) >= 3\
               and self.ccU.lastChemCompDict['_chem_comp.type'].upper() == 'D-PEPTIDE LINKING':
                revertPolySeqRst(self.polySeqCs, ps['chain_id'] if fixedChainId is None else fixedChainId, _seqId, compId)

            if types is None or ('alt_comp_id' in ps and _compId in ps['alt_comp_id']):
                return False
            if compId not in monDict3 and cif_comp_id not in monDict3:
                return False
            return types != self.csStat.getTypeOfCompId(cif_comp_id)

        if refChainId is not None or refChainId != _refChainId:
            if any(ps for ps in self.polySeq if ps['auth_chain_id' if 'auth_chain_id' in ps else 'chain_id'] == _refChainId):
                fixedChainId = _refChainId

        for ps in self.polySeq:
            if preferNonPoly:
                continue
            chainId, seqId, cifCompId = self.getRealChainSeqId(ps, _seqId, compId)
            if fixedChainId is None and refChainId is not None and refChainId != chainId and refChainId in self.chainNumberDict:
                if chainId != self.chainNumberDict[refChainId]:
                    continue
            if self.reasons is not None:
                if fixedChainId is not None:
                    if fixedChainId != chainId:
                        continue
                    if fixedSeqId is not None:
                        seqId = fixedSeqId
                elif fixedSeqId is not None:
                    seqId = fixedSeqId
            if seqId <= 0 and self.__shiftNonPosSeq is not None and chainId in self.__shiftNonPosSeq:
                seqId -= 1
            if seqId in ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id'] or fixedCompId is not None:
                if fixedCompId is not None:
                    cifCompId = origCompId = fixedCompId
                else:
                    if cifCompId is not None:
                        idx = next((_idx for _idx, (_seqId_, _cifCompId_) in enumerate(zip(ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id'], ps['comp_id']))
                                    if _seqId_ == seqId and _cifCompId_ == cifCompId), ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id'].index(seqId))
                    else:
                        idx = ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id'].index(seqId)
                    cifCompId = ps['comp_id'][idx]
                    origCompId = ps['auth_comp_id' if 'auth_comp_id' in ps else 'comp_id'][idx]
                    if comp_id_unmatched_with(ps, cifCompId):
                        continue
                if cifCompId != compId:
                    if (self.__shiftNonPosSeq is None or chainId not in self.__shiftNonPosSeq)\
                       and seqId <= 0 and seqId - 1 in ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id']\
                       and compId == ps['comp_id'][ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id'].index(seqId - 1)]:
                        seqId -= 1
                        if self.__shiftNonPosSeq is None:
                            self.__shiftNonPosSeq = {}
                        self.__shiftNonPosSeq[chainId] = True
                    compIds = [_compId for _seqId, _compId in zip(ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id'], ps['comp_id']) if _seqId == seqId]
                    if compId in compIds:
                        cifCompId = compId
                        origCompId = next(origCompId for _seqId, _compId, origCompId in zip(ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id'],
                                                                                            ps['comp_id'],
                                                                                            ps['auth_comp_id' if 'auth_comp_id' in ps else 'comp_id'])
                                          if _seqId == seqId and _compId == compId)
                if compId in (cifCompId, origCompId, 'MTS', 'ORI'):
                    if len(self.nefT.get_valid_star_atom(cifCompId, atomId)[0]) > 0:
                        chainAssign.add((chainId, seqId, cifCompId, True))
                        if refChainId is not None and refChainId != chainId and refChainId not in self.chainNumberDict:
                            self.chainNumberDict[refChainId] = chainId
                else:
                    _atomId, _, details = self.nefT.get_valid_star_atom(cifCompId, atomId)
                    if len(_atomId) > 0 and (details is None or _compId not in monDict3):
                        chainAssign.add((chainId, seqId, cifCompId, True))
                        if refChainId is not None and refChainId != chainId and refChainId not in self.chainNumberDict:
                            self.chainNumberDict[refChainId] = chainId

            elif 'gap_in_auth_seq' in ps and ps['gap_in_auth_seq']:
                auth_seq_id_list = list(filter(None, ps['auth_seq_id']))
                if len(auth_seq_id_list) > 0:
                    min_auth_seq_id = min(auth_seq_id_list)
                    max_auth_seq_id = max(auth_seq_id_list)
                    if min_auth_seq_id <= seqId <= max_auth_seq_id:
                        _seqId_ = seqId + 1
                        while _seqId_ <= max_auth_seq_id:
                            if _seqId_ in ps['auth_seq_id']:
                                break
                            _seqId_ += 1
                        if _seqId_ not in ps['auth_seq_id']:
                            _seqId_ = seqId - 1
                            while _seqId_ >= min_auth_seq_id:
                                if _seqId_ in ps['auth_seq_id']:
                                    break
                                _seqId_ -= 1
                        if _seqId_ in ps['auth_seq_id']:
                            idx = ps['auth_seq_id'].index(_seqId_) - (_seqId_ - seqId)
                            try:
                                seqId_ = ps['auth_seq_id'][idx]
                                cifCompId = ps['comp_id'][idx]
                                origCompId = ps['auth_comp_id'][idx]
                                if comp_id_unmatched_with(ps, cifCompId):
                                    continue
                                if cifCompId != compId:
                                    compIds = [_compId for _seqId, _compId in zip(ps['auth_seq_id'], ps['comp_id']) if _seqId == seqId]
                                    if compId in compIds:
                                        cifCompId = compId
                                        origCompId = next(origCompId for _seqId, _compId, origCompId in zip(ps['auth_seq_id'], ps['comp_id'], ps['auth_comp_id'])
                                                          if _seqId == seqId and _compId == compId)
                                if compId in (cifCompId, origCompId, 'MTS', 'ORI'):
                                    if len(self.nefT.get_valid_star_atom(cifCompId, atomId)[0]) > 0:
                                        chainAssign.add((chainId, seqId_, cifCompId, True))
                                        if refChainId is not None and refChainId != chainId and refChainId not in self.chainNumberDict:
                                            self.chainNumberDict[refChainId] = chainId
                                else:
                                    _atomId, _, details = self.nefT.get_valid_star_atom(cifCompId, atomId)
                                    if len(_atomId) > 0 and (details is None or _compId not in monDict3):
                                        chainAssign.add((chainId, seqId_, cifCompId, True))
                                        if refChainId is not None and refChainId != chainId and refChainId not in self.chainNumberDict:
                                            self.chainNumberDict[refChainId] = chainId
                            except IndexError:
                                pass

        if len(chainAssign) == 0:
            for ps in self.polySeq:
                if preferNonPoly:
                    continue
                chainId = ps['chain_id']
                if refChainId is not None and refChainId != chainId and refChainId in self.chainNumberDict:
                    if chainId != self.chainNumberDict[refChainId]:
                        continue
                if fixedChainId is not None and fixedChainId != chainId:
                    continue
                seqKey = (chainId, _seqId)
                if seqKey in self.authToLabelSeq:
                    _, seqId = self.authToLabelSeq[seqKey]
                    if seqId in ps['seq_id']:
                        idx = ps['seq_id'].index(seqId)
                        cifCompId = ps['comp_id'][idx]
                        origCompId = ps['auth_comp_id' if 'auth_comp_id' in ps else 'comp_id'][idx]
                        if comp_id_unmatched_with(ps, cifCompId):
                            continue
                        if cifCompId != compId:
                            compIds = [_compId for _seqId, _compId in zip(ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id'], ps['comp_id']) if _seqId == seqId]
                            if compId in compIds:
                                cifCompId = compId
                                origCompId = next(origCompId for _seqId, _compId, origCompId in zip(ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id'],
                                                                                                    ps['comp_id'],
                                                                                                    ps['auth_comp_id' if 'auth_comp_id' in ps else 'comp_id'])
                                                  if _seqId == seqId and _compId == compId)
                        if compId in (cifCompId, origCompId, 'MTS', 'ORI'):
                            if len(self.nefT.get_valid_star_atom(cifCompId, atomId)[0]) > 0:
                                chainAssign.add((ps['auth_chain_id' if 'auth_chain_id' in ps else 'chain_id'], _seqId, cifCompId, True))
                                if refChainId is not None and refChainId != chainId and refChainId not in self.chainNumberDict:
                                    self.chainNumberDict[refChainId] = chainId
                        else:
                            _atomId, _, details = self.nefT.get_valid_star_atom(cifCompId, atomId)
                            if len(_atomId) > 0 and (details is None or _compId not in monDict3):
                                chainAssign.add((ps['auth_chain_id' if 'auth_chain_id' in ps else 'chain_id'], _seqId, cifCompId, True))
                                if refChainId is not None and refChainId != chainId and refChainId not in self.chainNumberDict:
                                    self.chainNumberDict[refChainId] = chainId

        if len(chainAssign) == 0 and (self.__preferAuthSeqCount - self.__preferLabelSeqCount < MAX_PREF_LABEL_SCHEME_COUNT or len(self.polySeq) > 1):
            for ps in self.polySeq:
                if preferNonPoly:
                    continue
                chainId = ps['chain_id']
                if refChainId is not None and refChainId != chainId and refChainId in self.chainNumberDict:
                    if chainId != self.chainNumberDict[refChainId]:
                        continue
                if fixedChainId is not None and fixedChainId != chainId:
                    continue
                seqKey = (chainId, _seqId)
                if seqKey in self.__labelToAuthSeq:
                    _, seqId = self.__labelToAuthSeq[seqKey]
                    if seqId in ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id']:
                        idx = ps['seq_id'].index(_seqId)
                        cifCompId = ps['comp_id'][idx]
                        origCompId = ps['auth_comp_id' if 'auth_comp_id' in ps else 'comp_id'][idx]
                        if comp_id_unmatched_with(ps, cifCompId):
                            continue
                        if cifCompId != compId:
                            compIds = [_compId for _seqId, _compId in zip(ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id'], ps['comp_id']) if _seqId == seqId]
                            if compId in compIds:
                                cifCompId = compId
                                origCompId = next(origCompId for _seqId, _compId, origCompId in zip(ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id'],
                                                                                                    ps['comp_id'],
                                                                                                    ps['auth_comp_id' if 'auth_comp_id' in ps else 'comp_id'])
                                                  if _seqId == seqId and _compId == compId)
                        if compId in (cifCompId, origCompId, 'MTS', 'ORI'):
                            if len(self.nefT.get_valid_star_atom(cifCompId, atomId)[0]) > 0:
                                chainAssign.add((ps['auth_chain_id' if 'auth_chain_id' in ps else 'chain_id'], seqId, cifCompId, True))
                                if compId in (cifCompId, origCompId):
                                    self.__authSeqId = 'label_seq_id'
                                    self.__setLocalSeqScheme()
                                    if refChainId is not None and refChainId != chainId and refChainId not in self.chainNumberDict:
                                        self.chainNumberDict[refChainId] = chainId
                        else:
                            _atomId, _, details = self.nefT.get_valid_star_atom(cifCompId, atomId)
                            if len(_atomId) > 0 and (details is None or _compId not in monDict3):
                                chainAssign.add((ps['auth_chain_id' if 'auth_chain_id' in ps else 'chain_id'], seqId, cifCompId, True))
                                self.__authSeqId = 'label_seq_id'
                                self.__setLocalSeqScheme()
                                if refChainId is not None and refChainId != chainId and refChainId not in self.chainNumberDict:
                                    self.chainNumberDict[refChainId] = chainId

        if len(chainAssign) == 0:
            auth_seq_id_list = list(filter(None, self.polySeq[0]['auth_seq_id']))
            min_auth_seq_id = max_auth_seq_id = UNREAL_AUTH_SEQ_NUM
            if len(auth_seq_id_list) > 0:
                min_auth_seq_id = min(auth_seq_id_list)
                max_auth_seq_id = max(auth_seq_id_list)
            if len(self.polySeq) == 1\
               and (seqId < 1
                    or (compId == 'ACE' and seqId == min_auth_seq_id - 1)
                    or (compId == 'NH2' and seqId == max_auth_seq_id + 1)
                    or (compId in monDict3 and self.__preferAuthSeqCount - self.__preferLabelSeqCount >= MAX_PREF_LABEL_SCHEME_COUNT)):
                refChainId = self.polySeq[0]['auth_chain_id' if 'auth_chain_id' in self.polySeq[0] else 'chain_id']
                if (compId == 'ACE' and seqId == min_auth_seq_id - 1)\
                   or (compId == 'NH2' and seqId == max_auth_seq_id + 1)\
                   or (compId in monDict3 and self.__preferAuthSeqCount - self.__preferLabelSeqCount >= MAX_PREF_LABEL_SCHEME_COUNT
                       and (min_auth_seq_id - MAX_ALLOWED_EXT_SEQ <= seqId < min_auth_seq_id
                            or max_auth_seq_id < seqId <= max_auth_seq_id + MAX_ALLOWED_EXT_SEQ)):
                    self.f.append(f"[Sequence mismatch warning] {self.getCurrentAssignment(n=index)}"
                                  f"The residue '{_seqId}:{_compId}' is not present in polymer sequence "
                                  f"of chain {refChainId} of the coordinates. "
                                  "Please update the sequence in the Macromolecules page.")
                    chainAssign.add((refChainId, _seqId, compId, True))
                    asis = True
                elif compId in monDict3 and self.__preferAuthSeqCount - self.__preferLabelSeqCount >= MAX_PREF_LABEL_SCHEME_COUNT:
                    self.f.append(f"[Sequence mismatch warning] {self.getCurrentAssignment(n=index)}"
                                  f"The residue '{_seqId}:{_compId}' is not present in polymer sequence "
                                  f"of chain {refChainId} of the coordinates. "
                                  "Please update the sequence in the Macromolecules page.")
                elif self.no_extra_comment:
                    self.f.append(f"[Atom not found] {self.getCurrentAssignment(n=index)}"
                                  f"{_seqId}:{_compId}:{atomId} is not present in the coordinates. "
                                  f"The residue number '{_seqId}' is not present in polymer sequence "
                                  f"of chain {refChainId} of the coordinates. "
                                  "Please update the sequence in the Macromolecules page.")
            else:
                ext_seq = False
                if (compId in monDict3 or compId in ('ACE', 'NH2')) and self.__preferAuthSeqCount - self.__preferLabelSeqCount >= MAX_PREF_LABEL_SCHEME_COUNT:
                    refChainIds = []
                    _auth_seq_id_list = auth_seq_id_list
                    for idx, ps in enumerate(self.polySeq):
                        if idx > 0:
                            auth_seq_id_list = list(filter(None, ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id']))
                            _auth_seq_id_list.extend(auth_seq_id_list)
                        if len(auth_seq_id_list) > 0:
                            if idx > 0:
                                min_auth_seq_id = min(auth_seq_id_list)
                                max_auth_seq_id = max(auth_seq_id_list)
                            if min_auth_seq_id - MAX_ALLOWED_EXT_SEQ <= seqId < min_auth_seq_id\
                               and (compId in monDict3 or (compId == 'ACE' and seqId == min_auth_seq_id - 1)):
                                refChainIds.append(ps['auth_chain_id' if 'auth_chain_id' in ps else 'chain_id'])
                                ext_seq = True
                            if max_auth_seq_id < seqId <= max_auth_seq_id + MAX_ALLOWED_EXT_SEQ\
                               and (compId in monDict3 or (compId == 'NH2' and seqId == max_auth_seq_id + 1)):
                                refChainIds.append(ps['auth_chain_id' if 'auth_chain_id' in ps else 'chain_id'])
                                ext_seq = True
                    if ext_seq and seqId in _auth_seq_id_list:
                        ext_seq = False
                if ext_seq:
                    refChainId = refChainIds[0] if len(refChainIds) == 1 else refChainIds
                    self.f.append(f"[Sequence mismatch warning] {self.getCurrentAssignment(n=index)}"
                                  f"The residue '{_seqId}:{_compId}' is not present in polymer sequence "
                                  f"of chain {refChainId} of the coordinates. "
                                  "Please update the sequence in the Macromolecules page.")
                    if isinstance(refChainId, str):
                        chainAssign.add((refChainId, _seqId, compId, True))
                    else:
                        for _refChainId in refChainIds:
                            chainAssign.add((_refChainId, _seqId, compId, True))
                    asis = True
                elif self.no_extra_comment:
                    self.f.append(f"[Atom not found] {self.getCurrentAssignment(n=index)}"
                                  f"{_seqId}:{_compId}:{atomId} is not present in the coordinates.")
                updatePolySeqRst(self.polySeqCsFailed, self.polySeq[0]['chain_id'] if refChainId is None else refChainId, _seqId, compId, _compId)

        elif any(ca for ca in chainAssign if ca[0] == refChainId) and any(ca for ca in chainAssign if ca[0] != refChainId):
            _chainAssign = copy.copy(chainAssign)
            for _ca in _chainAssign:
                if _ca[0] != refChainId:
                    chainAssign.remove(_ca)

        return list(chainAssign), asis

    def assignCoordPolymerSequenceWithChainId(self, refChainId: str, seqId: int, compId: str, atomId: str, index: int
                                              ) -> Tuple[List[Tuple[str, int, str, bool]], bool]:
        """ Assign polymer sequences of the coordinates.
        """

        _refChainId = refChainId

        chainAssign = set()
        asis = False
        _seqId = seqId
        _compId = compId

        fixedChainId = fixedSeqId = fixedCompId = None

        preferNonPoly = False

        compId = self.translateToStdResNameWrapper(_seqId, _compId, preferNonPoly)

        self.__allow_ext_seq = False

        if self.reasons is not None:
            if 'unambig_atom_id_remap' in self.reasons and _compId in self.reasons['unambig_atom_id_remap']\
               and atomId in self.reasons['unambig_atom_id_remap'][_compId]:
                atomId = self.reasons['unambig_atom_id_remap'][_compId][atomId][0]  # select representative one
            if 'non_poly_remap' in self.reasons and _compId in self.reasons['non_poly_remap']\
               and seqId in self.reasons['non_poly_remap'][_compId]:
                fixedChainId, fixedSeqId = retrieveRemappedNonPoly(self.reasons['non_poly_remap'], None, str(refChainId), seqId, _compId)
                refChainId = fixedChainId
                preferNonPoly = True
            if 'branched_remap' in self.reasons and seqId in self.reasons['branched_remap']:
                fixedChainId, fixedSeqId = retrieveRemappedChainId(self.reasons['branched_remap'], seqId)
                refChainId = fixedChainId
                preferNonPoly = True
            if not preferNonPoly:
                if 'chain_id_remap' in self.reasons and seqId in self.reasons['chain_id_remap']:
                    fixedChainId, fixedSeqId = retrieveRemappedChainId(self.reasons['chain_id_remap'], seqId)
                    refChainId = fixedChainId
                elif 'chain_id_clone' in self.reasons and seqId in self.reasons['chain_id_clone']:
                    fixedChainId, fixedSeqId = retrieveRemappedChainId(self.reasons['chain_id_clone'], seqId)
                    refChainId = fixedChainId
                elif 'seq_id_remap' in self.reasons\
                        or 'chain_seq_id_remap' in self.reasons\
                        or 'ext_chain_seq_id_remap' in self.reasons:
                    if 'ext_chain_seq_id_remap' in self.reasons:
                        fixedChainId, fixedSeqId, fixedCompId =\
                            retrieveRemappedSeqIdAndCompId(self.reasons['ext_chain_seq_id_remap'], str(refChainId), seqId,
                                                           compId if compId in monDict3 else None)
                        self.__allow_ext_seq = fixedCompId is not None
                        if fixedSeqId is not None:
                            refChainId = fixedChainId
                    if fixedSeqId is None and 'chain_seq_id_remap' in self.reasons:
                        fixedChainId, fixedSeqId = retrieveRemappedSeqId(self.reasons['chain_seq_id_remap'], str(refChainId), seqId,
                                                                         compId if compId in monDict3 else None)
                        if fixedSeqId is not None:
                            refChainId = fixedChainId
                    if fixedSeqId is None and 'seq_id_remap' in self.reasons:
                        _, fixedSeqId = retrieveRemappedSeqId(self.reasons['seq_id_remap'], str(refChainId), seqId)
            if fixedSeqId is not None:
                _seqId = fixedSeqId

        updatePolySeqRst(self.polySeqCs, str(refChainId), _seqId, compId, _compId)

        types = self.csStat.getTypeOfCompId(compId)
        if all(not t for t in types) or compId in ('MTS', 'ORI'):
            types = None
        elif compId != _compId:
            if types != self.csStat.getTypeOfCompId(_compId):
                types = None

        def comp_id_unmatched_with(ps, cif_comp_id):
            if 'alt_comp_id' in ps and self.csStat.peptideLike(cif_comp_id) and compId.startswith('D') and len(compId) >= 3\
               and self.ccU.lastChemCompDict['_chem_comp.type'].upper() == 'D-PEPTIDE LINKING':
                revertPolySeqRst(self.polySeqCs, str(refChainId), _seqId, compId)

            if types is None or ('alt_comp_id' in ps and _compId in ps['alt_comp_id']):
                return False
            if compId not in monDict3 and cif_comp_id not in monDict3:
                return False
            return types != self.csStat.getTypeOfCompId(cif_comp_id)

        if refChainId is not None or refChainId != _refChainId:
            if any(ps for ps in self.polySeq if ps['auth_chain_id' if 'auth_chain_id' in ps else 'chain_id'] == _refChainId):
                fixedChainId = _refChainId

        for ps in self.polySeq:
            if preferNonPoly:
                continue
            chainId, seqId, cifCompId = self.getRealChainSeqId(ps, _seqId, compId)
            if fixedChainId is None and refChainId is not None and refChainId != chainId and refChainId in self.chainNumberDict:
                if chainId != self.chainNumberDict[refChainId]:
                    continue
            if self.reasons is not None:
                if fixedChainId is not None:
                    if fixedChainId != chainId:
                        continue
                    if fixedSeqId is not None:
                        seqId = fixedSeqId
                elif fixedSeqId is not None:
                    seqId = fixedSeqId
            if seqId <= 0 and self.__shiftNonPosSeq is not None and chainId in self.__shiftNonPosSeq:
                seqId -= 1
            if seqId in ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id'] or fixedCompId is not None:
                if fixedCompId is not None:
                    cifCompId = origCompId = fixedCompId
                else:
                    if cifCompId is not None:
                        idx = next((_idx for _idx, (_seqId_, _cifCompId_) in enumerate(zip(ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id'], ps['comp_id']))
                                    if _seqId_ == seqId and _cifCompId_ == cifCompId), ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id'].index(seqId))
                    else:
                        idx = ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id'].index(seqId)
                    cifCompId = ps['comp_id'][idx]
                    origCompId = ps['auth_comp_id' if 'auth_comp_id' in ps else 'comp_id'][idx]
                    if comp_id_unmatched_with(ps, cifCompId):
                        continue
                if cifCompId != compId:
                    if (self.__shiftNonPosSeq is None or chainId not in self.__shiftNonPosSeq)\
                       and seqId <= 0 and seqId - 1 in ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id']\
                       and compId == ps['comp_id'][ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id'].index(seqId - 1)]:
                        seqId -= 1
                        if self.__shiftNonPosSeq is None:
                            self.__shiftNonPosSeq = {}
                        self.__shiftNonPosSeq[chainId] = True
                    compIds = [_compId for _seqId, _compId in zip(ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id'], ps['comp_id']) if _seqId == seqId]
                    if compId in compIds:
                        cifCompId = compId
                        origCompId = next(origCompId for _seqId, _compId, origCompId in zip(ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id'],
                                                                                            ps['comp_id'],
                                                                                            ps['auth_comp_id' if 'auth_comp_id' in ps else 'comp_id'])
                                          if _seqId == seqId and _compId == compId)
                if compId in (cifCompId, origCompId, 'MTS', 'ORI'):
                    if len(self.nefT.get_valid_star_atom(cifCompId, atomId)[0]) > 0:
                        chainAssign.add((chainId, seqId, cifCompId, True))
                        if refChainId is not None and refChainId != chainId and refChainId not in self.chainNumberDict:
                            self.chainNumberDict[refChainId] = chainId
                else:
                    _atomId, _, details = self.nefT.get_valid_star_atom(cifCompId, atomId)
                    if len(_atomId) > 0 and (details is None or _compId not in monDict3):
                        chainAssign.add((chainId, seqId, cifCompId, True))
                        if refChainId is not None and refChainId != chainId and refChainId not in self.chainNumberDict:
                            self.chainNumberDict[refChainId] = chainId

            elif 'gap_in_auth_seq' in ps and ps['gap_in_auth_seq']:
                auth_seq_id_list = list(filter(None, ps['auth_seq_id']))
                if len(auth_seq_id_list) > 0:
                    min_auth_seq_id = min(auth_seq_id_list)
                    max_auth_seq_id = max(auth_seq_id_list)
                    if min_auth_seq_id <= seqId <= max_auth_seq_id:
                        _seqId_ = seqId + 1
                        while _seqId_ <= max_auth_seq_id:
                            if _seqId_ in ps['auth_seq_id']:
                                break
                            _seqId_ += 1
                        if _seqId_ not in ps['auth_seq_id']:
                            _seqId_ = seqId - 1
                            while _seqId_ >= min_auth_seq_id:
                                if _seqId_ in ps['auth_seq_id']:
                                    break
                                _seqId_ -= 1
                        if _seqId_ in ps['auth_seq_id']:
                            idx = ps['auth_seq_id'].index(_seqId_) - (_seqId_ - seqId)
                            try:
                                seqId_ = ps['auth_seq_id'][idx]
                                cifCompId = ps['comp_id'][idx]
                                origCompId = ps['auth_comp_id'][idx]
                                if comp_id_unmatched_with(ps, cifCompId):
                                    continue
                                if cifCompId != compId:
                                    compIds = [_compId for _seqId, _compId in zip(ps['auth_seq_id'], ps['comp_id']) if _seqId == seqId]
                                    if compId in compIds:
                                        cifCompId = compId
                                        origCompId = next(origCompId for _seqId, _compId, origCompId in zip(ps['auth_seq_id'], ps['comp_id'], ps['auth_comp_id'])
                                                          if _seqId == seqId and _compId == compId)
                                if compId in (cifCompId, origCompId, 'MTS', 'ORI'):
                                    if len(self.nefT.get_valid_star_atom(cifCompId, atomId)[0]) > 0:
                                        chainAssign.add((chainId, seqId_, cifCompId, True))
                                    else:
                                        _atomId, _, details = self.nefT.get_valid_star_atom(cifCompId, atomId)
                                        if len(_atomId) > 0 and (details is None or _compId not in monDict3):
                                            chainAssign.add((chainId, seqId_, cifCompId, True))
                            except IndexError:
                                pass

        if len(chainAssign) == 0:
            for ps in self.polySeq:
                if preferNonPoly:
                    continue
                chainId = ps['chain_id']
                if refChainId is not None and refChainId != chainId and refChainId in self.chainNumberDict:
                    if chainId != self.chainNumberDict[refChainId]:
                        continue
                if fixedChainId is not None and fixedChainId != chainId:
                    continue
                seqKey = (chainId, _seqId)
                if seqKey in self.authToLabelSeq:
                    _, seqId = self.authToLabelSeq[seqKey]
                    if seqId in ps['seq_id']:
                        idx = ps['seq_id'].index(seqId)
                        cifCompId = ps['comp_id'][idx]
                        origCompId = ps['auth_comp_id' if 'auth_comp_id' in ps else 'comp_id'][idx]
                        if comp_id_unmatched_with(ps, cifCompId):
                            continue
                        if cifCompId != compId:
                            compIds = [_compId for _seqId, _compId in zip(ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id'], ps['comp_id']) if _seqId == seqId]
                            if compId in compIds:
                                cifCompId = compId
                                origCompId = next(origCompId for _seqId, _compId, origCompId in zip(ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id'],
                                                                                                    ps['comp_id'],
                                                                                                    ps['auth_comp_id' if 'auth_comp_id' in ps else 'comp_id'])
                                                  if _seqId == seqId and _compId == compId)
                        if compId in (cifCompId, origCompId, 'MTS', 'ORI'):
                            if len(self.nefT.get_valid_star_atom(cifCompId, atomId)[0]) > 0:
                                chainAssign.add((ps['auth_chain_id' if 'auth_chain_id' in ps else 'chain_id'], _seqId, cifCompId, True))
                                if refChainId is not None and refChainId != chainId and refChainId not in self.chainNumberDict:
                                    self.chainNumberDict[refChainId] = chainId
                        else:
                            _atomId, _, details = self.nefT.get_valid_star_atom(cifCompId, atomId)
                            if len(_atomId) > 0 and (details is None or _compId not in monDict3):
                                chainAssign.add((ps['auth_chain_id' if 'auth_chain_id' in ps else 'chain_id'], _seqId, cifCompId, True))
                                if refChainId is not None and refChainId != chainId and refChainId not in self.chainNumberDict:
                                    self.chainNumberDict[refChainId] = chainId

        if len(chainAssign) == 0 and (self.__preferAuthSeqCount - self.__preferLabelSeqCount < MAX_PREF_LABEL_SCHEME_COUNT or len(self.polySeq) > 1):
            for ps in self.polySeq:
                if preferNonPoly:
                    continue
                chainId = ps['chain_id']
                if refChainId is not None and refChainId != chainId and refChainId in self.chainNumberDict:
                    if chainId != self.chainNumberDict[refChainId]:
                        continue
                if fixedChainId is not None and fixedChainId != chainId:
                    continue
                seqKey = (chainId, _seqId)
                if seqKey in self.__labelToAuthSeq:
                    _, seqId = self.__labelToAuthSeq[seqKey]
                    if seqId in ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id']:
                        idx = ps['seq_id'].index(_seqId)
                        cifCompId = ps['comp_id'][idx]
                        origCompId = ps['auth_comp_id' if 'auth_comp_id' in ps else 'comp_id'][idx]
                        if comp_id_unmatched_with(ps, cifCompId):
                            continue
                        if cifCompId != compId:
                            compIds = [_compId for _seqId, _compId in zip(ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id'], ps['comp_id']) if _seqId == seqId]
                            if compId in compIds:
                                cifCompId = compId
                                origCompId = next(origCompId for _seqId, _compId, origCompId in zip(ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id'],
                                                                                                    ps['comp_id'],
                                                                                                    ps['auth_comp_id' if 'auth_comp_id' in ps else 'comp_id'])
                                                  if _seqId == seqId and _compId == compId)
                        if compId in (cifCompId, origCompId, 'MTS', 'ORI'):
                            if len(self.nefT.get_valid_star_atom(cifCompId, atomId)[0]) > 0:
                                chainAssign.add((ps['auth_chain_id' if 'auth_chain_id' in ps else 'chain_id'], seqId, cifCompId, True))
                                if compId in (cifCompId, origCompId):
                                    self.__authSeqId = 'label_seq_id'
                                    self.__setLocalSeqScheme()
                                    if refChainId is not None and refChainId != chainId and refChainId not in self.chainNumberDict:
                                        self.chainNumberDict[refChainId] = chainId
                        else:
                            _atomId, _, details = self.nefT.get_valid_star_atom(cifCompId, atomId)
                            if len(_atomId) > 0 and (details is None or _compId not in monDict3):
                                chainAssign.add((ps['auth_chain_id' if 'auth_chain_id' in ps else 'chain_id'], seqId, cifCompId, True))
                                self.__authSeqId = 'label_seq_id'
                                self.__setLocalSeqScheme()
                                if refChainId is not None and refChainId != chainId and refChainId not in self.chainNumberDict:
                                    self.chainNumberDict[refChainId] = chainId

        if len(chainAssign) == 0:
            auth_seq_id_list = list(filter(None, self.polySeq[0]['auth_seq_id']))
            min_auth_seq_id = max_auth_seq_id = UNREAL_AUTH_SEQ_NUM
            if len(auth_seq_id_list) > 0:
                min_auth_seq_id = min(auth_seq_id_list)
                max_auth_seq_id = max(auth_seq_id_list)
            if len(self.polySeq) == 1\
               and (seqId < 1
                    or (compId == 'ACE' and seqId == min_auth_seq_id - 1)
                    or (compId == 'NH2' and seqId == max_auth_seq_id + 1)
                    or (compId in monDict3 and self.__preferAuthSeqCount - self.__preferLabelSeqCount >= MAX_PREF_LABEL_SCHEME_COUNT)):
                refChainId = self.polySeq[0]['auth_chain_id' if 'auth_chain_id' in self.polySeq[0] else 'chain_id']
                if (compId == 'ACE' and seqId == min_auth_seq_id - 1)\
                   or (compId == 'NH2' and seqId == max_auth_seq_id + 1)\
                   or (compId in monDict3 and self.__preferAuthSeqCount - self.__preferLabelSeqCount >= MAX_PREF_LABEL_SCHEME_COUNT
                       and (min_auth_seq_id - MAX_ALLOWED_EXT_SEQ <= seqId < min_auth_seq_id
                            or max_auth_seq_id < seqId <= max_auth_seq_id + MAX_ALLOWED_EXT_SEQ)):
                    self.f.append(f"[Sequence mismatch warning] {self.getCurrentAssignment(n=index)}"
                                  f"The residue '{_seqId}:{_compId}' is not present in polymer sequence "
                                  f"of chain {refChainId} of the coordinates. "
                                  "Please update the sequence in the Macromolecules page.")
                    chainAssign.add((refChainId, _seqId, compId, True))
                    asis = True
                elif compId in monDict3 and self.__preferAuthSeqCount - self.__preferLabelSeqCount >= MAX_PREF_LABEL_SCHEME_COUNT:
                    self.f.append(f"[Sequence mismatch warning] {self.getCurrentAssignment(n=index)}"
                                  f"The residue '{_seqId}:{_compId}' is not present in polymer sequence "
                                  f"of chain {refChainId} of the coordinates. "
                                  "Please update the sequence in the Macromolecules page.")
                elif self.no_extra_comment:
                    self.f.append(f"[Atom not found] {self.getCurrentAssignment(n=index)}"
                                  f"{_seqId}:{_compId}:{atomId} is not present in the coordinates. "
                                  f"The residue number '{_seqId}' is not present in polymer sequence "
                                  f"of chain {refChainId} of the coordinates. "
                                  "Please update the sequence in the Macromolecules page.")
            else:
                ext_seq = False
                if (compId in monDict3 or compId in ('ACE', 'NH2')) and self.__preferAuthSeqCount - self.__preferLabelSeqCount >= MAX_PREF_LABEL_SCHEME_COUNT:
                    refChainIds = []
                    _auth_seq_id_list = auth_seq_id_list
                    for idx, ps in enumerate(self.polySeq):
                        if idx > 0:
                            auth_seq_id_list = list(filter(None, ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id']))
                            _auth_seq_id_list.extend(auth_seq_id_list)
                        if len(auth_seq_id_list) > 0:
                            if idx > 0:
                                min_auth_seq_id = min(auth_seq_id_list)
                                max_auth_seq_id = max(auth_seq_id_list)
                            if min_auth_seq_id - MAX_ALLOWED_EXT_SEQ <= seqId < min_auth_seq_id\
                               and (compId in monDict3 or (compId == 'ACE' and seqId == min_auth_seq_id - 1)):
                                refChainIds.append(ps['auth_chain_id' if 'auth_chain_id' in ps else 'chain_id'])
                                ext_seq = True
                            if max_auth_seq_id < seqId <= max_auth_seq_id + MAX_ALLOWED_EXT_SEQ\
                               and (compId in monDict3 or (compId == 'NH2' and seqId == max_auth_seq_id + 1)):
                                refChainIds.append(ps['auth_chain_id' if 'auth_chain_id' in ps else 'chain_id'])
                                ext_seq = True
                    if ext_seq and seqId in _auth_seq_id_list:
                        ext_seq = False
                if ext_seq:
                    refChainId = refChainIds[0] if len(refChainIds) == 1 else refChainIds
                    self.f.append(f"[Sequence mismatch warning] {self.getCurrentAssignment(n=index)}"
                                  f"The residue '{_seqId}:{_compId}' is not present in polymer sequence "
                                  f"of chain {refChainId} of the coordinates. "
                                  "Please update the sequence in the Macromolecules page.")
                    if isinstance(refChainId, str):
                        chainAssign.add((refChainId, _seqId, compId, True))
                    else:
                        for _refChainId in refChainIds:
                            chainAssign.add((_refChainId, _seqId, compId, True))
                    asis = True
                elif self.no_extra_comment:
                    self.f.append(f"[Atom not found] {self.getCurrentAssignment(n=index)}"
                                  f"{_seqId}:{_compId}:{atomId} is not present in the coordinates.")
                updatePolySeqRst(self.polySeqCsFailed, str(refChainId), _seqId, compId, _compId)

        elif any(ca for ca in chainAssign if ca[0] == refChainId) and any(ca for ca in chainAssign if ca[0] != refChainId):
            _chainAssign = copy.copy(chainAssign)
            for _ca in _chainAssign:
                if _ca[0] != refChainId:
                    chainAssign.remove(_ca)

        return list(chainAssign), asis

    def assignCoordPolymerSequenceWithoutCompId(self, seqId: int, atomId: str, index: int
                                                ) -> List[Tuple[str, int, str, bool]]:
        """ Assign polymer sequences of the coordinates.
        """

        chainAssign = set()
        _seqId = seqId

        fixedChainId = fixedSeqId = fixedCompId = None

        self.__allow_ext_seq = False

        if self.reasons is not None:
            if 'branched_remap' in self.reasons and seqId in self.reasons['branched_remap']:
                fixedChainId, fixedSeqId = retrieveRemappedChainId(self.reasons['branched_remap'], seqId)
            if 'chain_id_remap' in self.reasons and seqId in self.reasons['chain_id_remap']:
                fixedChainId, fixedSeqId = retrieveRemappedChainId(self.reasons['chain_id_remap'], seqId)
            elif 'chain_id_clone' in self.reasons and seqId in self.reasons['chain_id_clone']:
                fixedChainId, fixedSeqId = retrieveRemappedChainId(self.reasons['chain_id_clone'], seqId)
            if fixedSeqId is not None:
                seqId = _seqId = fixedSeqId

        for ps in self.polySeq:
            chainId, seqId, cifCompId = self.getRealChainSeqId(ps, _seqId, None)
            if self.reasons is not None:
                if 'seq_id_remap' not in self.reasons\
                   and 'chain_seq_id_remap' not in self.reasons\
                   and 'ext_chain_seq_id_remap' not in self.reasons:
                    if fixedChainId is not None and fixedChainId != chainId:
                        continue
                else:
                    if 'ext_chain_seq_id_remap' in self.reasons:
                        fixedChainId, fixedSeqId, fixedCompId =\
                            retrieveRemappedSeqIdAndCompId(self.reasons['ext_chain_seq_id_remap'], chainId, seqId)
                        if fixedChainId is not None and fixedChainId != chainId:
                            continue
                        if fixedSeqId is not None:
                            self.__allow_ext_seq = fixedCompId is not None
                            seqId = _seqId = fixedSeqId
                    if fixedSeqId is None and 'chain_seq_id_remap' in self.reasons:
                        fixedChainId, fixedSeqId = retrieveRemappedSeqId(self.reasons['chain_seq_id_remap'], chainId, seqId)
                        if fixedChainId is not None and fixedChainId != chainId:
                            continue
                        if fixedSeqId is not None:
                            seqId = _seqId = fixedSeqId
                    if fixedSeqId is None and 'seq_id_remap' in self.reasons:
                        _, fixedSeqId = retrieveRemappedSeqId(self.reasons['seq_id_remap'], chainId, seqId)
                        if fixedSeqId is not None:
                            seqId = _seqId = fixedSeqId
            if seqId in ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id'] or fixedCompId is not None:
                if fixedCompId is not None:
                    cifCompId = fixedCompId
                else:
                    if cifCompId is not None:
                        idx = next((_idx for _idx, (_seqId_, _cifCompId_) in enumerate(zip(ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id'], ps['comp_id']))
                                    if _seqId_ == seqId and _cifCompId_ == cifCompId), ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id'].index(seqId))
                    else:
                        idx = ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id'].index(seqId)
                    cifCompId = ps['comp_id'][idx]
                if self.reasons is not None:
                    if 'non_poly_remap' in self.reasons and cifCompId in self.reasons['non_poly_remap']\
                       and seqId in self.reasons['non_poly_remap'][cifCompId]:
                        fixedChainId, fixedSeqId = retrieveRemappedNonPoly(self.reasons['non_poly_remap'], None, chainId, seqId, cifCompId)
                        if fixedSeqId is not None:
                            seqId = _seqId = fixedSeqId
                        if (fixedChainId is not None and fixedChainId != chainId) or seqId not in ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id']:
                            continue
                updatePolySeqRst(self.polySeqCs, chainId, _seqId, cifCompId)
                if atomId is None or len(self.nefT.get_valid_star_atom(cifCompId, atomId)[0]) > 0:
                    chainAssign.add((chainId, seqId, cifCompId, True))
            elif 'gap_in_auth_seq' in ps and ps['gap_in_auth_seq']:
                auth_seq_id_list = list(filter(None, ps['auth_seq_id']))
                if len(auth_seq_id_list) > 0:
                    min_auth_seq_id = min(auth_seq_id_list)
                    max_auth_seq_id = max(auth_seq_id_list)
                    if min_auth_seq_id <= seqId <= max_auth_seq_id:
                        _seqId_ = seqId + 1
                        while _seqId_ <= max_auth_seq_id:
                            if _seqId_ in ps['auth_seq_id']:
                                break
                            _seqId_ += 1
                        if _seqId_ not in ps['auth_seq_id']:
                            _seqId_ = seqId - 1
                            while _seqId_ >= min_auth_seq_id:
                                if _seqId_ in ps['auth_seq_id']:
                                    break
                                _seqId_ -= 1
                        if _seqId_ in ps['auth_seq_id']:
                            idx = ps['auth_seq_id'].index(_seqId_) - (_seqId_ - seqId)
                            try:
                                seqId_ = ps['auth_seq_id'][idx]
                                cifCompId = ps['comp_id'][idx]
                                updatePolySeqRst(self.polySeqCs, chainId, _seqId, cifCompId)
                                if atomId is None or len(self.nefT.get_valid_star_atom(cifCompId, atomId)[0]) > 0:
                                    chainAssign.add((chainId, seqId_, cifCompId, True))
                            except IndexError:
                                pass

        if len(chainAssign) == 0:
            for ps in self.polySeq:
                chainId = ps['chain_id']
                if fixedChainId is not None and fixedChainId != chainId:
                    continue
                seqKey = (chainId, _seqId)
                if seqKey in self.authToLabelSeq:
                    _, seqId = self.authToLabelSeq[seqKey]
                    if seqId in ps['seq_id']:
                        cifCompId = ps['comp_id'][ps['seq_id'].index(seqId)]
                        updatePolySeqRst(self.polySeqCs, chainId, _seqId, cifCompId)
                        if atomId is None or len(self.nefT.get_valid_star_atom(cifCompId, atomId)[0]) > 0:
                            chainAssign.add((ps['auth_chain_id' if 'auth_chain_id' in ps else 'chain_id'], _seqId, cifCompId, True))

        if len(chainAssign) == 0 and (self.__preferAuthSeqCount - self.__preferLabelSeqCount < MAX_PREF_LABEL_SCHEME_COUNT or len(self.polySeq) > 1):
            for ps in self.polySeq:
                chainId = ps['chain_id']
                if fixedChainId is not None and fixedChainId != chainId:
                    continue
                seqKey = (chainId, _seqId)
                if seqKey in self.__labelToAuthSeq:
                    _, seqId = self.__labelToAuthSeq[seqKey]
                    if seqId in ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id']:
                        cifCompId = ps['comp_id'][ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id'].index(seqId)]
                        updatePolySeqRst(self.polySeqCs, chainId, seqId, cifCompId)
                        if atomId is None or len(self.nefT.get_valid_star_atom(cifCompId, atomId)[0]) > 0:
                            chainAssign.add((ps['auth_chain_id' if 'auth_chain_id' in ps else 'chain_id'], seqId, cifCompId, True))
                            self.__authSeqId = 'label_seq_id'
                            self.__setLocalSeqScheme()

        if len(chainAssign) == 0:
            if atomId is not None and (('-' in atomId and ':' in atomId) or '.' in atomId):
                if self.no_extra_comment:
                    self.f.append(f"[Atom not found] {self.getCurrentAssignment(n=index)}"
                                  f"{_seqId}:?:{atomId} is not present in the coordinates.")
            elif atomId is not None:
                if len(self.polySeq) == 1 and seqId < 1:
                    refChainId = self.polySeq[0]['auth_chain_id' if 'auth_chain_id' in self.polySeq[0] else 'chain_id']
                    if self.no_extra_comment:
                        self.f.append(f"[Atom not found] {self.getCurrentAssignment(n=index)}"
                                      f"{_seqId}:?:{atomId} is not present in the coordinates. "
                                      f"The residue number '{_seqId}' is not present in polymer sequence "
                                      f"of chain {refChainId} of the coordinates. "
                                      "Please update the sequence in the Macromolecules page.")
                else:
                    if self.no_extra_comment:
                        self.f.append(f"[Atom not found] {self.getCurrentAssignment(n=index)}"
                                      f"{_seqId}:{atomId} is not present in the coordinates.")
                    compIds = guessCompIdFromAtomId([atomId], self.polySeq, self.nefT)
                    if compIds is not None:
                        chainId = fixedChainId
                        if chainId is None and len(self.polySeq) == 1:
                            chainId = self.polySeq[0]['chain_id']
                        if chainId is not None:
                            if len(compIds) == 1:
                                updatePolySeqRst(self.polySeqCsFailed, chainId, seqId, compIds[0])
                            else:
                                updatePolySeqRstAmbig(self.polySeqCsFailedAmbig, chainId, seqId, compIds)

        return list(chainAssign)

    def assignCoordPolymerSequenceWithChainIdWithoutCompId(self, fixedChainId: str, seqId: int, atomId: str, index: int
                                                           ) -> List[Tuple[str, int, str, bool]]:
        """ Assign polymer sequences of the coordinates.
        """

        chainAssign = set()
        _seqId = seqId

        fixedSeqId = fixedCompId = None

        self.__allow_ext_seq = False

        if self.reasons is not None:
            if 'branched_remap' in self.reasons and seqId in self.reasons['branched_remap']:
                fixedChainId, fixedSeqId = retrieveRemappedChainId(self.reasons['branched_remap'], seqId)
            if 'chain_id_remap' in self.reasons and seqId in self.reasons['chain_id_remap']:
                fixedChainId, fixedSeqId = retrieveRemappedChainId(self.reasons['chain_id_remap'], seqId)
            elif 'chain_id_clone' in self.reasons and seqId in self.reasons['chain_id_clone']:
                fixedChainId, fixedSeqId = retrieveRemappedChainId(self.reasons['chain_id_clone'], seqId)
            if fixedSeqId is not None:
                seqId = _seqId = fixedSeqId

        for ps in self.polySeq:
            chainId, seqId, cifCompId = self.getRealChainSeqId(ps, _seqId, None)
            if chainId != fixedChainId:
                continue
            if self.reasons is not None:
                if 'seq_id_remap' not in self.reasons\
                   and 'chain_seq_id_remap' not in self.reasons\
                   and 'ext_chain_seq_id_remap' not in self.reasons:
                    if fixedChainId is not None and fixedChainId != chainId:
                        continue
                else:
                    if 'ext_chain_seq_id_remap' in self.reasons:
                        fixedChainId, fixedSeqId, fixedCompId =\
                            retrieveRemappedSeqIdAndCompId(self.reasons['ext_chain_seq_id_remap'], chainId, seqId)
                        if fixedChainId is not None and fixedChainId != chainId:
                            continue
                        if fixedSeqId is not None:
                            self.__allow_ext_seq = fixedCompId is not None
                            seqId = _seqId = fixedSeqId
                    if fixedSeqId is None and 'chain_seq_id_remap' in self.reasons:
                        fixedChainId, fixedSeqId = retrieveRemappedSeqId(self.reasons['chain_seq_id_remap'], chainId, seqId)
                        if fixedChainId is not None and fixedChainId != chainId:
                            continue
                        if fixedSeqId is not None:
                            seqId = _seqId = fixedSeqId
                    if fixedSeqId is None and 'seq_id_remap' in self.reasons:
                        _, fixedSeqId = retrieveRemappedSeqId(self.reasons['seq_id_remap'], chainId, seqId)
                        if fixedSeqId is not None:
                            seqId = _seqId = fixedSeqId
            if seqId in ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id'] or fixedCompId is not None:
                if fixedCompId is not None:
                    cifCompId = fixedCompId
                else:
                    if cifCompId is not None:
                        idx = next((_idx for _idx, (_seqId_, _cifCompId_) in enumerate(zip(ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id'], ps['comp_id']))
                                    if _seqId_ == seqId and _cifCompId_ == cifCompId), ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id'].index(seqId))
                    else:
                        idx = ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id'].index(seqId)
                    cifCompId = ps['comp_id'][idx]
                if self.reasons is not None:
                    if 'non_poly_remap' in self.reasons and cifCompId in self.reasons['non_poly_remap']\
                       and seqId in self.reasons['non_poly_remap'][cifCompId]:
                        fixedChainId, fixedSeqId = retrieveRemappedNonPoly(self.reasons['non_poly_remap'], None, chainId, seqId, cifCompId)
                        if fixedSeqId is not None:
                            seqId = _seqId = fixedSeqId
                        if (fixedChainId is not None and fixedChainId != chainId) or seqId not in ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id']:
                            continue
                updatePolySeqRst(self.polySeqCs, fixedChainId, _seqId, cifCompId)
                if len(self.nefT.get_valid_star_atom(cifCompId, atomId)[0]) > 0:
                    chainAssign.add((chainId, seqId, cifCompId, True))
            elif 'gap_in_auth_seq' in ps and ps['gap_in_auth_seq']:
                auth_seq_id_list = list(filter(None, ps['auth_seq_id']))
                if len(auth_seq_id_list) > 0:
                    min_auth_seq_id = min(auth_seq_id_list)
                    max_auth_seq_id = max(auth_seq_id_list)
                    if min_auth_seq_id <= seqId <= max_auth_seq_id:
                        _seqId_ = seqId + 1
                        while _seqId_ <= max_auth_seq_id:
                            if _seqId_ in ps['auth_seq_id']:
                                break
                            _seqId_ += 1
                        if _seqId_ not in ps['auth_seq_id']:
                            _seqId_ = seqId - 1
                            while _seqId_ >= min_auth_seq_id:
                                if _seqId_ in ps['auth_seq_id']:
                                    break
                                _seqId_ -= 1
                        if _seqId_ in ps['auth_seq_id']:
                            idx = ps['auth_seq_id'].index(_seqId_) - (_seqId_ - seqId)
                            try:
                                seqId_ = ps['auth_seq_id'][idx]
                                cifCompId = ps['comp_id'][idx]
                                updatePolySeqRst(self.polySeqCs, fixedChainId, _seqId, cifCompId)
                                if len(self.nefT.get_valid_star_atom(cifCompId, atomId)[0]) > 0:
                                    chainAssign.add((chainId, seqId_, cifCompId, True))
                            except IndexError:
                                pass

        if len(chainAssign) == 0:
            for ps in self.polySeq:
                chainId = ps['chain_id']
                if chainId != fixedChainId:
                    continue
                seqKey = (chainId, _seqId)
                if seqKey in self.authToLabelSeq:
                    _, seqId = self.authToLabelSeq[seqKey]
                    if seqId in ps['seq_id']:
                        cifCompId = ps['comp_id'][ps['seq_id'].index(seqId)]
                        updatePolySeqRst(self.polySeqCs, fixedChainId, _seqId, cifCompId)
                        if len(self.nefT.get_valid_star_atom(cifCompId, atomId)[0]) > 0:
                            chainAssign.add((ps['auth_chain_id' if 'auth_chain_id' in ps else 'chain_id'], _seqId, cifCompId, True))

        if len(chainAssign) == 0 and (self.__preferAuthSeqCount - self.__preferLabelSeqCount < MAX_PREF_LABEL_SCHEME_COUNT or len(self.polySeq) > 1):
            for ps in self.polySeq:
                chainId = ps['chain_id']
                if chainId != fixedChainId:
                    continue
                seqKey = (chainId, _seqId)
                if seqKey in self.__labelToAuthSeq:
                    _, seqId = self.__labelToAuthSeq[seqKey]
                    if seqId in ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id']:
                        cifCompId = ps['comp_id'][ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id'].index(seqId)]
                        updatePolySeqRst(self.polySeqCs, fixedChainId, seqId, cifCompId)
                        if len(self.nefT.get_valid_star_atom(cifCompId, atomId)[0]) > 0:
                            chainAssign.add((ps['auth_chain_id' if 'auth_chain_id' in ps else 'chain_id'], seqId, cifCompId, True))
                            self.__authSeqId = 'label_seq_id'
                            self.__setLocalSeqScheme()

        if len(chainAssign) == 0:
            if (('-' in atomId and ':' in atomId) or '.' in atomId):
                if self.no_extra_comment:
                    self.f.append(f"[Atom not found] {self.getCurrentAssignment(n=index)}"
                                  f"{fixedChainId}:{_seqId}:?:{atomId} is not present in the coordinates.")
            else:
                if len(self.polySeq) == 1 and seqId < 1:
                    refChainId = self.polySeq[0]['auth_chain_id' if 'auth_chain_id' in self.polySeq[0] else 'chain_id']
                    if self.no_extra_comment:
                        self.f.append(f"[Atom not found] {self.getCurrentAssignment(n=index)}"
                                      f"{_seqId}:?:{atomId} is not present in the coordinates. "
                                      f"The residue number '{_seqId}' is not present in polymer sequence "
                                      f"of chain {refChainId} of the coordinates. "
                                      "Please update the sequence in the Macromolecules page.")
                else:
                    if self.no_extra_comment:
                        self.f.append(f"[Atom not found] {self.getCurrentAssignment(n=index)}"
                                      f"{fixedChainId}:{_seqId}:{atomId} is not present in the coordinates.")
                    compIds = guessCompIdFromAtomId([atomId], self.polySeq, self.nefT)
                    if compIds is not None:
                        if len(compIds) == 1:
                            updatePolySeqRst(self.polySeqCsFailed, fixedChainId, seqId, compIds[0])
                        else:
                            updatePolySeqRstAmbig(self.polySeqCsFailedAmbig, fixedChainId, seqId, compIds)

        return list(chainAssign)

    def selectCoordAtoms(self, chainAssign: List[Tuple[str, int, str, bool]], seqId: int, compId: str, atomId: str,
                         index: int, allowAmbig: bool = True, offset: int = 0):
        """ Select atoms of the coordinates.
        """

        atomSelection = []

        authAtomId = atomId

        __compId = compId
        __atomId = atomId

        compId = self.translateToStdResNameWrapper(seqId, __compId)

        for chainId, cifSeqId, cifCompId, isPolySeq in chainAssign:

            if offset != 0:
                cifSeqId += offset
                cifCompId = compId

            _, coordAtomSite = self.getCoordAtomSiteOf(chainId, cifSeqId, cifCompId, asis=self.__preferAuthSeq)

            _atomId = []
            if not isPolySeq and atomId[0] in ('Q', 'M') and coordAtomSite is not None:
                key = (chainId, cifSeqId, compId, atomId)
                if key in self.__cachedDictForStarAtom:
                    _atomId = copy.deepcopy(self.__cachedDictForStarAtom[key])
            if len(_atomId) > 1:
                details = None
            else:
                _atomId, _, details = self.nefT.get_valid_star_atom_in_xplor(cifCompId, atomId, leave_unmatched=True)
                if details is not None:
                    if atomId != __atomId:
                        _atomId, _, details = self.nefT.get_valid_star_atom_in_xplor(cifCompId, __atomId, leave_unmatched=True)
                    elif len(atomId) > 1 and not atomId[-1].isalpha() and (atomId[0] in pseProBeginCode or atomId[0] in ('C', 'N', 'P', 'F')):
                        _atomId, _, details = self.nefT.get_valid_star_atom_in_xplor(cifCompId, atomId[:-1], leave_unmatched=True)
                        if atomId[-1].isdigit() and int(atomId[-1]) <= len(_atomId):
                            _atomId = [_atomId[int(atomId[-1]) - 1]]

            if details is not None or atomId.endswith('"'):
                _atomId_ = translateToStdAtomName(atomId, cifCompId, ccU=self.ccU)
                if _atomId_ != atomId:
                    if atomId.startswith('HT') and len(_atomId_) == 2:
                        _atomId_ = 'H'
                    __atomId__ = self.nefT.get_valid_star_atom_in_xplor(cifCompId, _atomId_)[0]
                    if coordAtomSite is not None:
                        if any(_atomId_ for _atomId_ in __atomId__ if _atomId_ in coordAtomSite['atom_id']):
                            _atomId = __atomId__
                        elif __atomId__[0][0] in protonBeginCode:
                            __bondedTo = self.ccU.getBondedAtoms(cifCompId, __atomId__[0])
                            if len(__bondedTo) > 0 and __bondedTo[0] in coordAtomSite['atom_id']:
                                _atomId = __atomId__
                elif coordAtomSite is not None:
                    _atomId = []
            # _atomId = self.nefT.get_valid_star_atom(cifCompId, atomId)[0]

            if coordAtomSite is not None\
               and not any(_atomId_ for _atomId_ in _atomId if _atomId_ in coordAtomSite['atom_id']):
                if atomId in coordAtomSite['atom_id']:
                    _atomId = [atomId]
                elif seqId == 1 and atomId == 'H1' and self.csStat.peptideLike(compId) and 'H' in coordAtomSite['atom_id']:
                    _atomId = ['H']

            if coordAtomSite is not None:
                atomSiteAtomId = coordAtomSite['atom_id']
                if len(_atomId) == 0 and __atomId in zincIonCode and 'ZN' in atomSiteAtomId:
                    compId = atomId = 'ZN'
                    _atomId = [atomId]
                elif len(_atomId) == 0 and __atomId in calciumIonCode and 'CA' in atomSiteAtomId:
                    compId = atomId = 'CA'
                    _atomId = [atomId]
                elif not any(_atomId_ in atomSiteAtomId for _atomId_ in _atomId):
                    pass
                elif atomId[0] not in pseProBeginCode and not all(_atomId in atomSiteAtomId for _atomId in _atomId):
                    _atomId = [_atomId_ for _atomId_ in _atomId if _atomId_ in atomSiteAtomId]

            lenAtomId = len(_atomId)
            if self.reasons is not None and compId != cifCompId and __compId == cifCompId:
                compId = cifCompId
            if compId != cifCompId and compId in monDict3 and cifCompId in monDict3:
                multiChain = insCode = False
                if len(chainAssign) > 0:
                    chainIds = [ca[0] for ca in chainAssign]
                    multiChain = len(collections.Counter(chainIds).most_common()) > 1
                ps = next((ps for ps in self.polySeq if ps['auth_chain_id' if 'auth_chain_id' in ps else 'chain_id'] == chainId), None)
                if ps is not None:
                    compIds = [_compId for _seqId, _compId in zip(ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id'], ps['comp_id']) if _seqId == cifSeqId]
                    if compId in compIds:
                        insCode = True
                        cifCompId = compId
                if not multiChain and not insCode:
                    if self.__preferAuthSeq:
                        _seqKey, _coordAtomSite = self.getCoordAtomSiteOf(chainId, cifSeqId, cifCompId, asis=False)
                        if _coordAtomSite is not None and _coordAtomSite['comp_id'] == compId:
                            if lenAtomId > 0 and _atomId[0] in _coordAtomSite['atom_id']:
                                self.__authSeqId = 'label_seq_id'
                                self.__setLocalSeqScheme()
                                continue
                    self.f.append(f"[Sequence mismatch] {self.getCurrentAssignment(n=index)}"
                                  f"Residue name {__compId!r} of the chemical shift does not match with {chainId}:{cifSeqId}:{cifCompId} of the coordinates.")
                    continue

            if compId != cifCompId and cifCompId in monDict3 and not isPolySeq:
                continue

            if lenAtomId == 0 and not isPolySeq and cifCompId in SYMBOLS_ELEMENT:
                _atomId = [cifCompId]
                lenAtomId = 1

            if lenAtomId == 0:
                if compId != cifCompId and any(item for item in chainAssign if item[2] == compId):
                    continue
                if seqId == 1 and isPolySeq and cifCompId == 'ACE' and cifCompId != compId and offset == 0:
                    self.selectCoordAtoms(chainAssign, seqId, compId, atomId, index, allowAmbig, offset=1)
                    return
                self.f.append(f"[Invalid atom nomenclature] {self.getCurrentAssignment(n=index)}"
                              f"{seqId}:{__compId}:{__atomId} is invalid atom nomenclature.")
                continue
            if lenAtomId > 1 and not allowAmbig:
                self.f.append(f"[Invalid atom selection] {self.getCurrentAssignment(n=index)}"
                              f"Ambiguous atom selection '{seqId}:{__compId}:{__atomId}' is not allowed as a angle restraint.")
                continue

            if __compId != cifCompId and __compId not in self.compIdMap:
                self.compIdMap[__compId] = cifCompId

            for cifAtomId in _atomId:

                if authAtomId in ('H', 'HN') and cifAtomId in ('HN1', 'HN2', 'HNA') and self.csStat.peptideLike(cifCompId)\
                   and coordAtomSite is not None and cifAtomId not in coordAtomSite['atom_id']:
                    if cifAtomId in ('HN2', 'HNA'):
                        if 'H2' not in coordAtomSite['atom_id']:
                            continue
                        cifAtomId = 'H2'
                    if cifAtomId == 'HN1' and 'H' in coordAtomSite['atom_id']:
                        cifAtomId = 'H'

                atomSelection.append({'chain_id': chainId, 'seq_id': cifSeqId, 'comp_id': cifCompId,
                                      'atom_id': cifAtomId, 'auth_seq_id': seqId, 'auth_atom_id': authAtomId})

                self.testCoordAtomIdConsistency(chainId, cifSeqId, cifCompId, cifAtomId, coordAtomSite, index)

        if len(atomSelection) > 0:
            self.atomSelectionSet.append(atomSelection)

    def testCoordAtomIdConsistency(self, chainId: str, seqId: int, compId: str, atomId: str,
                                   coordAtomSite: Optional[dict], index: int) -> Tuple[str, bool]:
        asis = False
        if not self.hasPolySeq:
            return atomId, asis

        found = False

        if coordAtomSite is not None:
            if atomId in coordAtomSite['atom_id']:
                found = True
            elif atomId in ('HN1', 'HN2', 'HN3') and ((atomId[-1] + 'HN') in coordAtomSite['atom_id']
                                                      or ('H' + atomId[-1]) in coordAtomSite['atom_id']):
                atomId = atomId[-1] + 'HN' if atomId[-1] + 'HN' in coordAtomSite['atom_id'] else 'H' + atomId[-1]
                found = True
            elif 'alt_atom_id' in coordAtomSite and atomId in coordAtomSite['alt_atom_id']:
                found = True
                # self.__authAtomId = 'auth_atom_id'

            elif self.__preferAuthSeq:
                _seqKey, _coordAtomSite = self.getCoordAtomSiteOf(chainId, seqId, compId, asis=False)
                if _coordAtomSite is not None and _coordAtomSite['comp_id'] == compId and not self.__extendAuthSeq:
                    if atomId in _coordAtomSite['atom_id']:
                        found = True
                        self.__preferAuthSeq = False
                        self.__authSeqId = 'label_seq_id'
                        # seqKey = _seqKey
                        self.__setLocalSeqScheme()
                    elif atomId in ('HN1', 'HN2', 'HN3') and ((atomId[-1] + 'HN') in _coordAtomSite['atom_id']
                                                              or ('H' + atomId[-1]) in _coordAtomSite['atom_id']):
                        atomId = atomId[-1] + 'HN' if atomId[-1] + 'HN' in _coordAtomSite['atom_id'] else 'H' + atomId[-1]
                        found = True
                        self.__preferAuthSeq = False
                        self.__authSeqId = 'label_seq_id'
                        # seqKey = _seqKey
                        self.__setLocalSeqScheme()
                    elif 'alt_atom_id' in _coordAtomSite and atomId in _coordAtomSite['alt_atom_id']:
                        found = True
                        self.__preferAuthSeq = False
                        self.__authSeqId = 'label_seq_id'
                        # self.__authAtomId = 'auth_atom_id'
                        # seqKey = _seqKey
                        self.__setLocalSeqScheme()

            else:
                self.__preferAuthSeq = True
                _seqKey, _coordAtomSite = self.getCoordAtomSiteOf(chainId, seqId, compId)
                if _coordAtomSite is not None and _coordAtomSite['comp_id'] == compId:
                    if atomId in _coordAtomSite['atom_id']:
                        found = True
                        self.__authSeqId = 'auth_seq_id'
                        # seqKey = _seqKey
                        self.__setLocalSeqScheme()
                    elif atomId in ('HN1', 'HN2', 'HN3') and ((atomId[-1] + 'HN') in _coordAtomSite['atom_id']
                                                              or ('H' + atomId[-1]) in _coordAtomSite['atom_id']):
                        atomId = atomId[-1] + 'HN' if atomId[-1] + 'HN' in _coordAtomSite['atom_id'] else 'H' + atomId[-1]
                        found = True
                        self.__authSeqId = 'auth_seq_id'
                        # seqKey = _seqKey
                        self.__setLocalSeqScheme()
                    elif 'alt_atom_id' in _coordAtomSite and atomId in _coordAtomSite['alt_atom_id']:
                        found = True
                        self.__authSeqId = 'auth_seq_id'
                        # self.__authAtomId = 'auth_atom_id'
                        # seqKey = _seqKey
                        self.__setLocalSeqScheme()
                    elif not self.__extendAuthSeq:
                        self.__preferAuthSeq = False
                elif not self.__extendAuthSeq:
                    self.__preferAuthSeq = False

        elif self.__preferAuthSeq:
            _seqKey, _coordAtomSite = self.getCoordAtomSiteOf(chainId, seqId, compId, asis=False)
            if _coordAtomSite is not None and _coordAtomSite['comp_id'] == compId and not self.__extendAuthSeq:
                if atomId in _coordAtomSite['atom_id']:
                    found = True
                    self.__preferAuthSeq = False
                    self.__authSeqId = 'label_seq_id'
                    # seqKey = _seqKey
                    self.__setLocalSeqScheme()
                elif atomId in ('HN1', 'HN2', 'HN3') and ((atomId[-1] + 'HN') in _coordAtomSite['atom_id']
                                                          or ('H' + atomId[-1]) in _coordAtomSite['atom_id']):
                    atomId = atomId[-1] + 'HN' if atomId[-1] + 'HN' in _coordAtomSite['atom_id'] else 'H' + atomId[-1]
                    found = True
                    self.__preferAuthSeq = False
                    self.__authSeqId = 'label_seq_id'
                    # seqKey = _seqKey
                    self.__setLocalSeqScheme()
                elif 'alt_atom_id' in _coordAtomSite and atomId in _coordAtomSite['alt_atom_id']:
                    found = True
                    self.__preferAuthSeq = False
                    self.__authSeqId = 'label_seq_id'
                    # self.__authAtomId = 'auth_atom_id'
                    # seqKey = _seqKey
                    self.__setLocalSeqScheme()

        elif not self.__preferAuthSeq:
            self.__preferAuthSeq = True
            _seqKey, _coordAtomSite = self.getCoordAtomSiteOf(chainId, seqId, compId)
            if _coordAtomSite is not None and _coordAtomSite['comp_id'] == compId:
                if atomId in _coordAtomSite['atom_id']:
                    found = True
                    self.__authSeqId = 'auth_seq_id'
                    # seqKey = _seqKey
                    self.__setLocalSeqScheme()
                elif atomId in ('HN1', 'HN2', 'HN3') and ((atomId[-1] + 'HN') in _coordAtomSite['atom_id']
                                                          or ('H' + atomId[-1]) in _coordAtomSite['atom_id']):
                    atomId = atomId[-1] + 'HN' if atomId[-1] + 'HN' in _coordAtomSite['atom_id'] else 'H' + atomId[-1]
                    found = True
                    self.__authSeqId = 'auth_seq_id'
                    # seqKey = _seqKey
                    self.__setLocalSeqScheme()
                elif 'alt_atom_id' in _coordAtomSite and atomId in _coordAtomSite['alt_atom_id']:
                    found = True
                    self.__authSeqId = 'auth_seq_id'
                    # self.__authAtomId = 'auth_atom_id'
                    # seqKey = _seqKey
                    self.__setLocalSeqScheme()
                elif not self.__extendAuthSeq:
                    self.__preferAuthSeq = False
            elif not self.__extendAuthSeq:
                self.__preferAuthSeq = False

        if found:
            if self.__preferAuthSeq:
                self.__preferAuthSeqCount += 1
            return atomId, asis

        if chainId in self.chainNumberDict.values():

            if self.__preferAuthSeq:
                _seqKey, _coordAtomSite = self.getCoordAtomSiteOf(chainId, seqId, compId, asis=False)
                if _coordAtomSite is not None and _coordAtomSite['comp_id'] == compId and not self.__extendAuthSeq:
                    if atomId in _coordAtomSite['atom_id']:
                        found = True
                        self.__preferAuthSeq = False
                        self.__authSeqId = 'label_seq_id'
                        # seqKey = _seqKey
                        self.__setLocalSeqScheme()
                    elif atomId in ('HN1', 'HN2', 'HN3') and ((atomId[-1] + 'HN') in _coordAtomSite['atom_id']
                                                              or ('H' + atomId[-1]) in _coordAtomSite['atom_id']):
                        atomId = atomId[-1] + 'HN' if atomId[-1] + 'HN' in _coordAtomSite['atom_id'] else 'H' + atomId[-1]
                        found = True
                        self.__preferAuthSeq = False
                        self.__authSeqId = 'label_seq_id'
                        # seqKey = _seqKey
                        self.__setLocalSeqScheme()
                    elif 'alt_atom_id' in _coordAtomSite and atomId in _coordAtomSite['alt_atom_id']:
                        found = True
                        self.__preferAuthSeq = False
                        self.__authSeqId = 'label_seq_id'
                        # self.__authAtomId = 'auth_atom_id'
                        # seqKey = _seqKey
                        self.__setLocalSeqScheme()
            elif not self.__preferAuthSeq:
                self.__preferAuthSeq = True
                _seqKey, _coordAtomSite = self.getCoordAtomSiteOf(chainId, seqId, compId)
                if _coordAtomSite is not None and _coordAtomSite['comp_id'] == compId:
                    if atomId in _coordAtomSite['atom_id']:
                        found = True
                        self.__authSeqId = 'auth_seq_id'
                        # seqKey = _seqKey
                        self.__setLocalSeqScheme()
                    elif atomId in ('HN1', 'HN2', 'HN3') and ((atomId[-1] + 'HN') in _coordAtomSite['atom_id']
                                                              or ('H' + atomId[-1]) in _coordAtomSite['atom_id']):
                        atomId = atomId[-1] + 'HN' if atomId[-1] + 'HN' in _coordAtomSite['atom_id'] else 'H' + atomId[-1]
                        found = True
                        self.__authSeqId = 'auth_seq_id'
                        # seqKey = _seqKey
                        self.__setLocalSeqScheme()
                    elif 'alt_atom_id' in _coordAtomSite and atomId in _coordAtomSite['alt_atom_id']:
                        found = True
                        self.__authSeqId = 'auth_seq_id'
                        # self.__authAtomId = 'auth_atom_id'
                        # seqKey = _seqKey
                        self.__setLocalSeqScheme()
                    elif not self.__extendAuthSeq:
                        self.__preferAuthSeq = False
                elif not self.__extendAuthSeq:
                    self.__preferAuthSeq = False

            if found:
                if self.__preferAuthSeq:
                    self.__preferAuthSeqCount += 1
                return atomId, asis

        if self.ccU.updateChemCompDict(compId):
            cca = next((cca for cca in self.ccU.lastAtomList if cca[self.ccU.ccaAtomId] == atomId), None)
            if cca is not None and self.ccU.lastChemCompDict['_chem_comp.pdbx_release_status'] == 'REL':
                ps = next((ps for ps in self.polySeq if ps['auth_chain_id' if 'auth_chain_id' in ps else 'chain_id'] == chainId), None)
                auth_seq_id_list = list(filter(None, ps['auth_seq_id' if 'auth_seq_id' in ps else 'seq_id'])) if ps is not None else None
                min_auth_seq_id = max_auth_seq_id = UNREAL_AUTH_SEQ_NUM
                if auth_seq_id_list is not None and len(auth_seq_id_list) > 0:
                    min_auth_seq_id = min(auth_seq_id_list)
                    max_auth_seq_id = max(auth_seq_id_list)
                if atomId[0] in protonBeginCode:
                    bondedTo = self.ccU.getBondedAtoms(compId, atomId)
                    if len(bondedTo) > 0 and bondedTo[0][0] != 'P':
                        if coordAtomSite is not None and bondedTo[0] in coordAtomSite['atom_id']:
                            if cca[self.ccU.ccaLeavingAtomFlag] != 'Y'\
                               or (self.csStat.peptideLike(compId)
                                   and cca[self.ccU.ccaNTerminalAtomFlag] == 'N'
                                   and cca[self.ccU.ccaCTerminalAtomFlag] == 'N'):
                                self.f.append(f"[Hydrogen not instantiated] {self.getCurrentAssignment(n=index)}"
                                              f"{chainId}:{seqId}:{compId}:{atomId} is not properly instantiated in the coordinates. "
                                              "Please re-upload the model file.")
                                return atomId, asis
                        if bondedTo[0][0] == 'O':
                            return 'Ignorable hydroxyl group', asis

                ext_seq = False
                if auth_seq_id_list is not None and len(auth_seq_id_list) > 0:
                    if (compId == 'ACE' and seqId == min_auth_seq_id - 1)\
                       or (compId == 'NH2' and seqId == max_auth_seq_id + 1)\
                       or (compId in monDict3 and self.__preferAuthSeqCount - self.__preferLabelSeqCount >= MAX_PREF_LABEL_SCHEME_COUNT
                           and (min_auth_seq_id - MAX_ALLOWED_EXT_SEQ <= seqId < min_auth_seq_id
                                or max_auth_seq_id < seqId <= max_auth_seq_id + MAX_ALLOWED_EXT_SEQ)):
                        ext_seq = True
                if chainId in LARGE_ASYM_ID:
                    if ext_seq:
                        return atomId, asis
                    if self.__allow_ext_seq:
                        self.f.append(f"[Sequence mismatch warning] {self.getCurrentAssignment(n=index)}"
                                      f"The residue '{chainId}:{seqId}:{compId}' is not present in polymer sequence "
                                      f"of chain {chainId} of the coordinates. "
                                      "Please update the sequence in the Macromolecules page.")
                        asis = True
                    else:
                        if self.no_extra_comment:
                            self.f.append(f"[Atom not found] {self.getCurrentAssignment(n=index)}"
                                          f"{chainId}:{seqId}:{compId}:{atomId} is not present in the coordinates.")
                        updatePolySeqRst(self.polySeqCsFailed, chainId, seqId, compId)
        return atomId, asis

    def getCoordAtomSiteOf(self, chainId: str, seqId: int, compId: Optional[str] = None, cifCheck: bool = True, asis: bool = True
                           ) -> Tuple[Tuple[str, int], Optional[dict]]:

        def get_dummy_coord_atom_site(comp_id):
            if self.ccU.updateChemCompDict(comp_id):
                atom_id_list = [cca[self.ccU.ccaAtomId] for cca in self.ccU.lastAtomList if self.ccU.ccaLeavingAtomFlag != 'Y']
                return {'atom_id': atom_id_list} if len(atom_id_list) > 0 else None
            return None

        seqKey = (chainId, seqId)
        if cifCheck:
            preferAuthSeq = self.__preferAuthSeq if asis else not self.__preferAuthSeq
            if preferAuthSeq:
                ps = next((ps for ps in self.polySeq if 'auth_chain_id' in ps and ps['auth_chain_id'] == chainId), None)
                if ps is None:
                    ps = next((ps for ps in self.polySeq if ps['chain_id'] == chainId), None)
                if ps is None:
                    return seqKey, None
                if 'auth_seq_id' in ps:
                    if seqId in ps['auth_seq_id']:
                        _compId = ps['comp_id'][ps['auth_seq_id'].index(seqId)]
                        if compId is None or compId == _compId:
                            return seqKey, get_dummy_coord_atom_site(_compId)
                elif seqId in ps['seq_id']:
                    _compId = ps['comp_id'][ps['seq_id'].index(seqId)]
                    if compId is None or compId == _compId:
                        return seqKey, get_dummy_coord_atom_site(_compId)
            else:
                ps = next((ps for ps in self.polySeq if ps['chain_id'] == chainId), None)
                if ps is None:
                    return seqKey, None
                if seqId in ps['seq_id']:
                    _compId = ps['comp_id'][ps['seq_id'].index(seqId)]
                    if compId is None or compId == _compId:
                        return seqKey, get_dummy_coord_atom_site(compId)
        return seqKey, None

    def getCurrentAssignment(self, n: int) -> str:
        if self.cur_subtype == 'chem_shift':
            return f"[Check the {self.chemShifts + 1}th row of assigned chemical shifts (list_id={self.cur_list_id}, index={n}), {self.__def_err_sf_framecode}] "
        return ''

    def __setLocalSeqScheme(self):
        if 'local_seq_scheme' not in self.reasonsForReParsing:
            self.reasonsForReParsing['local_seq_scheme'] = {}
        preferAuthSeq = self.__authSeqId == 'auth_seq_id'
        if self.cur_subtype == 'chem_shift':
            self.reasonsForReParsing['local_seq_scheme'][(self.cur_subtype, self.cur_list_id, self.chemShifts)] = preferAuthSeq
        if not preferAuthSeq:
            self.__preferLabelSeqCount += 1
            if self.__preferLabelSeqCount > MAX_PREF_LABEL_SCHEME_COUNT:
                self.reasonsForReParsing['label_seq_scheme'] = True

    def retrieveLocalSeqScheme(self):
        if self.reasons is None\
           or ('label_seq_scheme' not in self.reasons
               and 'local_seq_scheme' not in self.reasons
               and 'extend_seq_scheme' not in self.reasons):
            return
        if 'extend_seq_scheme' in self.reasons:
            self.__preferAuthSeq = self.__extendAuthSeq = True
            return
        if 'label_seq_scheme' in self.reasons and self.reasons['label_seq_scheme']:
            self.__preferAuthSeq = False
            # self.__authSeqId = 'label_seq_id'
            return
        if self.cur_subtype == 'chem_shift':
            key = (self.cur_subtype, self.cur_list_id, self.chemShifts)
        else:
            return

        if key in self.reasons['local_seq_scheme']:
            self.__preferAuthSeq = self.reasons['local_seq_scheme'][key]

    def __addSf(self):
        content_subtype = contentSubtypeOf(self.cur_subtype)

        if content_subtype is None:
            return

        self.__listIdCounter = incListIdCounter(self.cur_subtype, self.__listIdCounter, reservedListIds=self.__reservedListIds)

        key = (self.cur_subtype, self.cur_list_id)

        if key in self.sfDict:
            if len(self.sfDict[key]) > 0:
                decListIdCounter(self.cur_subtype, self.__listIdCounter, reservedListIds=self.__reservedListIds)
                return
        else:
            self.sfDict[key] = []

        list_id = self.__listIdCounter[content_subtype]

        restraint_name = getRestraintName(self.cur_subtype)

        sf_framecode = (f'{self.software_name}_' if self.software_name is not None else '') + restraint_name.replace(' ', '_') + f'_{list_id}'

        sf = getSaveframe(self.cur_subtype, sf_framecode, list_id, self.entryId, self.__originalFileName)

        lp = getLoop(self.cur_subtype)

        item = {'file_type': self.file_type, 'saveframe': sf, 'loop': lp, 'list_id': list_id,
                'id': 0, 'index_id': 0,
                'sf_framecode': sf_framecode}

        self.sfDict[key].append(item)

    def getSf(self) -> dict:
        key = (self.cur_subtype, self.cur_list_id)

        if key not in self.sfDict:
            self.__addSf()

        cur_sf = self.sfDict[key][-1]

        self.__def_err_sf_framecode = cur_sf['sf_framecode']

        return cur_sf

    def getContentSubtype(self) -> dict:
        """ Return content subtype of CS file.
        """

        n = self.cur_list_id

        return {'chem_shift': n} if n > 0 else {}

    def getPolymerSequence(self) -> Optional[List[dict]]:
        """ Return polymer sequence of CS file.
        """

        return None if self.polySeqCs is None or len(self.polySeqCs) == 0 else self.polySeqCs

    def getSequenceAlignment(self) -> Optional[List[dict]]:
        """ Return sequence alignment between (coordinates or nmr_data) and CS.
        """

        return None if self.seqAlign is None or len(self.seqAlign) == 0 else self.seqAlign

    def getChainAssignment(self) -> Optional[List[dict]]:
        """ Return chain assignment between (coordinates or nmr_data) and CS.
        """

        return None if self.chainAssign is None or len(self.chainAssign) == 0 else self.chainAssign

    def getReasonsForReparsing(self) -> Optional[dict]:
        """ Return reasons for re-parsing CS file.
        """

        return None if len(self.reasonsForReParsing) == 0 else self.reasonsForReParsing

    def getSfDict(self) -> Tuple[dict, Optional[dict]]:
        """ Return a dictionary of pynmrstar saveframes.
        """

        if len(self.sfDict) == 0:
            return self.__listIdCounter, None
        ign_keys = []
        for k, v in self.sfDict.items():
            for item in reversed(v):
                if item['index_id'] == 0:
                    v.remove(item)
                    if len(v) == 0:
                        ign_keys.append(k)
                    self.__listIdCounter = decListIdCounter(k[0], self.__listIdCounter, reservedListIds=self.__reservedListIds)
        for k in ign_keys:
            del self.sfDict[k]
        return self.__listIdCounter, None if len(self.sfDict) == 0 else self.sfDict
