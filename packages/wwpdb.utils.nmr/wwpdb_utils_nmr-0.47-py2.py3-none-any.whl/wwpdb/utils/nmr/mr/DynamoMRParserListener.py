##
# File: DynamoMRParserListener.py
# Date: 17-Jun-2022
#
# Updates:
""" ParserLister class for DYNAMO/PALES/TALOS MR files.
    @author: Masashi Yokochi
"""
__docformat__ = "restructuredtext en"
__author__ = "Masashi Yokochi"
__email__ = "yokochi@protein.osaka-u.ac.jp"
__license__ = "Apache License 2.0"
__version__ = "1.0.0"

import sys
import re
import itertools
import numpy
import copy
import collections

from antlr4 import ParseTreeListener
from typing import IO, List, Tuple, Optional

from wwpdb.utils.align.alignlib import PairwiseAlign  # pylint: disable=no-name-in-module

try:
    from wwpdb.utils.nmr.io.CifReader import (CifReader,
                                              SYMBOLS_ELEMENT)
    from wwpdb.utils.nmr.mr.DynamoMRParser import DynamoMRParser
    from wwpdb.utils.nmr.mr.ParserListenerUtil import (coordAssemblyChecker,
                                                       extendCoordChainsForExactNoes,
                                                       isIdenticalRestraint,
                                                       isLongRangeRestraint,
                                                       hasIntraChainRestraint,
                                                       hasInterChainRestraint,
                                                       isAmbigAtomSelection,
                                                       getAltProtonIdInBondConstraint,
                                                       getTypeOfDihedralRestraint,
                                                       fixBackboneAtomsOfDihedralRestraint,
                                                       isLikePheOrTyr,
                                                       getRdcCode,
                                                       translateToStdResName,
                                                       translateToStdAtomName,
                                                       translateToLigandName,
                                                       isCyclicPolymer,
                                                       isStructConn,
                                                       getStructConnPtnrAtom,
                                                       getMetalCoordOf,
                                                       getRestraintName,
                                                       contentSubtypeOf,
                                                       incListIdCounter,
                                                       decListIdCounter,
                                                       getSaveframe,
                                                       getLoop,
                                                       getRow,
                                                       getStarAtom,
                                                       resetCombinationId,
                                                       resetMemberId,
                                                       getDistConstraintType,
                                                       getPotentialType,
                                                       ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS,
                                                       REPRESENTATIVE_MODEL_ID,
                                                       REPRESENTATIVE_ALT_ID,
                                                       MAX_PREF_LABEL_SCHEME_COUNT,
                                                       MAX_ALLOWED_EXT_SEQ,
                                                       UNREAL_AUTH_SEQ_NUM,
                                                       THRESHHOLD_FOR_CIRCULAR_SHIFT,
                                                       PLANE_LIKE_LOWER_LIMIT,
                                                       PLANE_LIKE_UPPER_LIMIT,
                                                       DIST_RESTRAINT_RANGE,
                                                       DIST_RESTRAINT_ERROR,
                                                       ANGLE_RESTRAINT_RANGE,
                                                       ANGLE_RESTRAINT_ERROR,
                                                       RDC_RESTRAINT_RANGE,
                                                       RDC_RESTRAINT_ERROR,
                                                       DIST_AMBIG_LOW,
                                                       DIST_AMBIG_UP,
                                                       DIST_AMBIG_MED,
                                                       DIST_AMBIG_UNCERT,
                                                       CARTN_DATA_ITEMS,
                                                       KNOWN_ANGLE_ATOM_NAMES,
                                                       KNOWN_ANGLE_SEQ_OFFSET,
                                                       HEME_LIKE_RES_NAMES)
    from wwpdb.utils.nmr.ChemCompUtil import ChemCompUtil
    from wwpdb.utils.nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from wwpdb.utils.nmr.nef.NEFTranslator import NEFTranslator
    from wwpdb.utils.nmr.AlignUtil import (LARGE_ASYM_ID,
                                           monDict3,
                                           emptyValue,
                                           protonBeginCode,
                                           pseProBeginCode,
                                           aminoProtonCode,
                                           carboxylCode,
                                           zincIonCode,
                                           calciumIonCode,
                                           rdcBbPairCode,
                                           updatePolySeqRst,
                                           revertPolySeqRst,
                                           sortPolySeqRst,
                                           syncCompIdOfPolySeqRst,
                                           alignPolymerSequence,
                                           assignPolymerSequence,
                                           trimSequenceAlignment,
                                           retrieveAtomIdentFromMRMap,
                                           retrieveAtomIdFromMRMap,
                                           retrieveRemappedSeqId,
                                           retrieveRemappedSeqIdAndCompId,
                                           splitPolySeqRstForMultimers,
                                           splitPolySeqRstForExactNoes,
                                           retrieveRemappedChainId,
                                           splitPolySeqRstForNonPoly,
                                           retrieveRemappedNonPoly,
                                           splitPolySeqRstForBranched,
                                           retrieveOriginalSeqIdFromMRMap)
    from wwpdb.utils.nmr.NmrVrptUtility import (to_np_array,
                                                distance,
                                                dist_error,
                                                angle_target_values,
                                                dihedral_angle,
                                                angle_error)
except ImportError:
    from nmr.io.CifReader import (CifReader,
                                  SYMBOLS_ELEMENT)
    from nmr.mr.DynamoMRParser import DynamoMRParser
    from nmr.mr.ParserListenerUtil import (coordAssemblyChecker,
                                           extendCoordChainsForExactNoes,
                                           isIdenticalRestraint,
                                           isLongRangeRestraint,
                                           hasIntraChainRestraint,
                                           hasInterChainRestraint,
                                           isAmbigAtomSelection,
                                           getAltProtonIdInBondConstraint,
                                           getTypeOfDihedralRestraint,
                                           fixBackboneAtomsOfDihedralRestraint,
                                           isLikePheOrTyr,
                                           getRdcCode,
                                           translateToStdResName,
                                           translateToStdAtomName,
                                           translateToLigandName,
                                           isCyclicPolymer,
                                           isStructConn,
                                           getStructConnPtnrAtom,
                                           getMetalCoordOf,
                                           getRestraintName,
                                           contentSubtypeOf,
                                           incListIdCounter,
                                           decListIdCounter,
                                           getSaveframe,
                                           getLoop,
                                           getRow,
                                           getStarAtom,
                                           resetCombinationId,
                                           resetMemberId,
                                           getDistConstraintType,
                                           getPotentialType,
                                           ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS,
                                           REPRESENTATIVE_MODEL_ID,
                                           REPRESENTATIVE_ALT_ID,
                                           MAX_PREF_LABEL_SCHEME_COUNT,
                                           MAX_ALLOWED_EXT_SEQ,
                                           UNREAL_AUTH_SEQ_NUM,
                                           THRESHHOLD_FOR_CIRCULAR_SHIFT,
                                           PLANE_LIKE_LOWER_LIMIT,
                                           PLANE_LIKE_UPPER_LIMIT,
                                           DIST_RESTRAINT_RANGE,
                                           DIST_RESTRAINT_ERROR,
                                           ANGLE_RESTRAINT_RANGE,
                                           ANGLE_RESTRAINT_ERROR,
                                           RDC_RESTRAINT_RANGE,
                                           RDC_RESTRAINT_ERROR,
                                           DIST_AMBIG_LOW,
                                           DIST_AMBIG_UP,
                                           DIST_AMBIG_MED,
                                           DIST_AMBIG_UNCERT,
                                           CARTN_DATA_ITEMS,
                                           KNOWN_ANGLE_ATOM_NAMES,
                                           KNOWN_ANGLE_SEQ_OFFSET,
                                           HEME_LIKE_RES_NAMES)
    from nmr.ChemCompUtil import ChemCompUtil
    from nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from nmr.nef.NEFTranslator import NEFTranslator
    from nmr.AlignUtil import (LARGE_ASYM_ID,
                               monDict3,
                               emptyValue,
                               protonBeginCode,
                               pseProBeginCode,
                               aminoProtonCode,
                               carboxylCode,
                               rdcBbPairCode,
                               zincIonCode,
                               calciumIonCode,
                               updatePolySeqRst,
                               revertPolySeqRst,
                               sortPolySeqRst,
                               syncCompIdOfPolySeqRst,
                               alignPolymerSequence,
                               assignPolymerSequence,
                               trimSequenceAlignment,
                               retrieveAtomIdentFromMRMap,
                               retrieveAtomIdFromMRMap,
                               retrieveRemappedSeqId,
                               retrieveRemappedSeqIdAndCompId,
                               splitPolySeqRstForMultimers,
                               splitPolySeqRstForExactNoes,
                               retrieveRemappedChainId,
                               splitPolySeqRstForNonPoly,
                               retrieveRemappedNonPoly,
                               splitPolySeqRstForBranched,
                               retrieveOriginalSeqIdFromMRMap)
    from nmr.NmrVrptUtility import (to_np_array,
                                    distance,
                                    dist_error,
                                    angle_target_values,
                                    dihedral_angle,
                                    angle_error)


DIST_RANGE_MIN = DIST_RESTRAINT_RANGE['min_inclusive']
DIST_RANGE_MAX = DIST_RESTRAINT_RANGE['max_inclusive']

DIST_ERROR_MIN = DIST_RESTRAINT_ERROR['min_exclusive']
DIST_ERROR_MAX = DIST_RESTRAINT_ERROR['max_exclusive']


ANGLE_RANGE_MIN = ANGLE_RESTRAINT_RANGE['min_inclusive']
ANGLE_RANGE_MAX = ANGLE_RESTRAINT_RANGE['max_inclusive']

ANGLE_ERROR_MIN = ANGLE_RESTRAINT_ERROR['min_exclusive']
ANGLE_ERROR_MAX = ANGLE_RESTRAINT_ERROR['max_exclusive']


RDC_RANGE_MIN = RDC_RESTRAINT_RANGE['min_inclusive']
RDC_RANGE_MAX = RDC_RESTRAINT_RANGE['max_inclusive']

RDC_ERROR_MIN = RDC_RESTRAINT_ERROR['min_exclusive']
RDC_ERROR_MAX = RDC_RESTRAINT_ERROR['max_exclusive']


TALOS_PREDICTION_CLASSES = ('Strong', 'Good', 'Generous', 'Warn', 'Bad', 'Dyn', 'New', 'None')
TALOS_PREDICTION_MIN_CLASSES = ('Strong', 'Good')


# This class defines a complete listener for a parse tree produced by DynamoMRParser.
class DynamoMRParserListener(ParseTreeListener):

    __file_type = 'nm-res-dyn'

    __verbose = None
    __lfh = None
    __debug = False

    __createSfDict = False
    __omitDistLimitOutlier = True
    __allowZeroUpperLimit = False
    __correctCircularShift = True

    # atom name mapping of public MR file between the archive coordinates and submitted ones
    __mrAtomNameMapping = None

    # CCD accessing utility
    __ccU = None

    # BMRB chemical shift statistics
    __csStat = None

    # NEFTranslator
    __nefT = None

    # Pairwise align
    __pA = None

    # reasons for re-parsing request from the previous trial
    __reasons = None

    # CIF reader
    __cR = None
    __hasCoord = False

    # data item name for model ID in 'atom_site' category
    __modelNumName = None

    # data item names for auth_asym_id, auth_seq_id, auth_atom_id in 'atom_site' category
    __authAsymId = None
    __authSeqId = None
    __authAtomId = None

    # coordinates information generated by ParserListenerUtil.coordAssemblyChecker()
    __polySeq = None
    __altPolySeq = None
    __nonPoly = None
    __branched = None
    __nonPolySeq = None
    __coordAtomSite = None
    __coordUnobsRes = None
    __coordUnobsAtom = None
    __labelToAuthSeq = None
    __authToLabelSeq = None
    __authToStarSeq = None
    __authToOrigSeq = None
    __authToInsCode = None
    __modResidue = None
    __splitLigand = None

    __uniqAtomIdToSeqKey = None

    __offsetHolder = None
    __shiftNonPosSeq = None

    __representativeModelId = REPRESENTATIVE_MODEL_ID
    __representativeAltId = REPRESENTATIVE_ALT_ID
    __hasPolySeq = False
    __hasNonPoly = False
    __hasBranched = False
    __hasNonPolySeq = False
    __preferAuthSeq = True
    __gapInAuthSeq = False
    __extendAuthSeq = False

    # chain number dictionary
    __chainNumberDict = None

    # extended residue key
    __extResKey = None

    # polymer sequence of MR file
    __polySeqRst = None
    __polySeqRstFailed = None
    __compIdMap = None

    __seqAlign = None
    __chainAssign = None

    # current restraint subtype
    __cur_subtype = ''

    __first_resid = 1
    __cur_sequence = ''
    __open_sequence = False
    __has_sequence = False
    __has_seq_align_err = False

    # whether to allow extended sequence temporary
    __allow_ext_seq = False

    # collection of atom selection
    atomSelectionSet = []

    # collection of auxiliary atom selection
    auxAtomSelectionSet = []

    # collection of number selection
    numberSelection = []

    __f = None
    warningMessage = None

    reasonsForReParsing = {}

    # original source MR file name
    __originalFileName = '.'

    # list id counter
    __listIdCounter = {}

    # entry ID
    __entryId = '.'

    # dictionary of pynmrstar saveframes
    sfDict = {}

    # current constraint type
    __cur_constraint_type = None

    # default saveframe name for error handling
    __def_err_sf_framecode = None

    __cachedDictForStarAtom = {}

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

        self.__representativeModelId = representativeModelId
        self.__representativeAltId = representativeAltId
        self.__mrAtomNameMapping = None if mrAtomNameMapping is None or len(mrAtomNameMapping) == 0 else mrAtomNameMapping

        self.__cR = cR
        self.__hasCoord = cR is not None

        # CCD accessing utility
        self.__ccU = ChemCompUtil(verbose, log) if ccU is None else ccU

        if self.__hasCoord:
            ret = coordAssemblyChecker(verbose, log, representativeModelId, representativeAltId,
                                       cR, self.__ccU, caC)
            self.__modelNumName = ret['model_num_name']
            self.__authAsymId = ret['auth_asym_id']
            self.__authSeqId = ret['auth_seq_id']
            self.__authAtomId = ret['auth_atom_id']
            self.__polySeq = ret['polymer_sequence']
            self.__altPolySeq = ret['alt_polymer_sequence']
            self.__nonPoly = ret['non_polymer']
            self.__branched = ret['branched']
            self.__coordAtomSite = ret['coord_atom_site']
            self.__coordUnobsRes = ret['coord_unobs_res']
            self.__coordUnobsAtom = ret['coord_unobs_atom'] if 'coord_unobs_atom' in ret else {}
            self.__labelToAuthSeq = ret['label_to_auth_seq']
            self.__authToLabelSeq = ret['auth_to_label_seq']
            self.__authToStarSeq = ret['auth_to_star_seq']
            self.__authToOrigSeq = ret['auth_to_orig_seq']
            self.__authToInsCode = ret['auth_to_ins_code']
            self.__modResidue = ret['mod_residue']
            self.__splitLigand = ret['split_ligand']

        self.__offsetHolder = {}

        self.__hasPolySeq = self.__polySeq is not None and len(self.__polySeq) > 0
        self.__hasNonPoly = self.__nonPoly is not None and len(self.__nonPoly) > 0
        self.__hasBranched = self.__branched is not None and len(self.__branched) > 0
        if self.__hasNonPoly or self.__hasBranched:
            self.__hasNonPolySeq = True
            if self.__hasNonPoly and self.__hasBranched:
                self.__nonPolySeq = self.__nonPoly
                self.__nonPolySeq.extend(self.__branched)
            elif self.__hasNonPoly:
                self.__nonPolySeq = self.__nonPoly
            else:
                self.__nonPolySeq = self.__branched

        if self.__hasPolySeq:
            self.__gapInAuthSeq = any(ps for ps in self.__polySeq if 'gap_in_auth_seq' in ps and ps['gap_in_auth_seq'])

        if self.__hasNonPoly:
            atom_list = []
            for v in self.__coordAtomSite.values():
                atom_list.extend(v['atom_id'])
            common_atom_list = collections.Counter(atom_list).most_common()
            uniq_atom_ids = [atom_id for atom_id, count in common_atom_list if count == 1]
            if len(uniq_atom_ids) > 0:
                self.__uniqAtomIdToSeqKey = {}
                for k, v in self.__coordAtomSite.items():
                    if any(np for np in self.__nonPoly if np['comp_id'][0] == v['comp_id']):
                        for atom_id in v['atom_id']:
                            if atom_id in uniq_atom_ids:
                                self.__uniqAtomIdToSeqKey[atom_id] = k

        # BMRB chemical shift statistics
        self.__csStat = BMRBChemShiftStat(verbose, log, self.__ccU) if csStat is None else csStat

        # NEFTranslator
        self.__nefT = NEFTranslator(verbose, log, self.__ccU, self.__csStat) if nefT is None else nefT

        # Pairwise align
        if self.__hasPolySeq:
            self.__pA = PairwiseAlign()
            self.__pA.setVerbose(verbose)

        if reasons is not None and 'model_chain_id_ext' in reasons:
            self.__polySeq, self.__altPolySeq, self.__coordAtomSite, self.__coordUnobsRes, \
                self.__labelToAuthSeq, self.__authToLabelSeq, self.__authToStarSeq, self.__authToOrigSeq =\
                extendCoordChainsForExactNoes(reasons['model_chain_id_ext'],
                                              self.__polySeq, self.__altPolySeq,
                                              self.__coordAtomSite, self.__coordUnobsRes,
                                              self.__authToLabelSeq, self.__authToStarSeq, self.__authToOrigSeq)

        # reasons for re-parsing request from the previous trial
        self.__reasons = reasons
        self.__preferAuthSeqCount = 0
        self.__preferLabelSeqCount = 0

        self.reasonsForReParsing = {}  # reset to prevent interference from the previous run

        self.distRestraints = 0      # DYNAMO: Distance restraints
        self.dihedRestraints = 0     # DYNAMO/TALOS: Torsion angle restraints
        self.rdcRestraints = 0       # DYNAMO/PALES: Residual dipolar coupling restraints
        self.jcoupRestraints = 0     # DYNAMO: Scalar coupling constant restraints

        self.sfDict = {}

        self.__cachedDictForStarAtom = {}

    def setDebugMode(self, debug: bool):
        self.__debug = debug

    def createSfDict(self, createSfDict: bool):
        self.__createSfDict = createSfDict

    def setOriginaFileName(self, originalFileName: str):
        self.__originalFileName = originalFileName

    def setListIdCounter(self, listIdCounter: dict):
        self.__listIdCounter = listIdCounter

    def setEntryId(self, entryId: str):
        self.__entryId = entryId

    # Enter a parse tree produced by DynamoMRParser#dynamo_mr.
    def enterDynamo_mr(self, ctx: DynamoMRParser.Dynamo_mrContext):  # pylint: disable=unused-argument
        self.__chainNumberDict = {}
        self.__extResKey = []
        self.__polySeqRst = []
        self.__polySeqRstFailed = []
        self.__compIdMap = {}
        self.__f = []

    # Exit a parse tree produced by DynamoMRParser#dynamo_mr.
    def exitDynamo_mr(self, ctx: DynamoMRParser.Dynamo_mrContext):  # pylint: disable=unused-argument

        try:

            if self.__hasPolySeq and self.__polySeqRst is not None:
                sortPolySeqRst(self.__polySeqRst,
                               None if self.__reasons is None else self.__reasons.get('non_poly_remap'))

                self.__seqAlign, _ = alignPolymerSequence(self.__pA, self.__polySeq, self.__polySeqRst,
                                                          resolvedMultimer=self.__reasons is not None)
                self.__chainAssign, message = assignPolymerSequence(self.__pA, self.__ccU, self.__file_type, self.__polySeq, self.__polySeqRst, self.__seqAlign)

                if len(message) > 0:
                    self.__f.extend(message)

                if self.__chainAssign is not None:

                    if len(self.__polySeq) == len(self.__polySeqRst):

                        chain_mapping = {}

                        for ca in self.__chainAssign:
                            ref_chain_id = ca['ref_chain_id']
                            test_chain_id = ca['test_chain_id']

                            if ref_chain_id != test_chain_id:
                                chain_mapping[test_chain_id] = ref_chain_id

                        if len(chain_mapping) == len(self.__polySeq):

                            for ps in self.__polySeqRst:
                                if ps['chain_id'] in chain_mapping:
                                    ps['chain_id'] = chain_mapping[ps['chain_id']]

                            self.__seqAlign, _ = alignPolymerSequence(self.__pA, self.__polySeq, self.__polySeqRst,
                                                                      resolvedMultimer=self.__reasons is not None)
                            self.__chainAssign, _ = assignPolymerSequence(self.__pA, self.__ccU, self.__file_type, self.__polySeq, self.__polySeqRst, self.__seqAlign)

                    trimSequenceAlignment(self.__seqAlign, self.__chainAssign)

                    if self.__reasons is None and any(f for f in self.__f
                                                      if '[Atom not found]' in f or '[Sequence mismatch]' in f):

                        seqIdRemap = []

                        cyclicPolymer = {}

                        for ca in self.__chainAssign:
                            ref_chain_id = ca['ref_chain_id']
                            test_chain_id = ca['test_chain_id']

                            sa = next(sa for sa in self.__seqAlign
                                      if sa['ref_chain_id'] == ref_chain_id
                                      and sa['test_chain_id'] == test_chain_id)

                            poly_seq_model = next(ps for ps in self.__polySeq
                                                  if ps['auth_chain_id'] == ref_chain_id)
                            poly_seq_rst = next(ps for ps in self.__polySeqRst
                                                if ps['chain_id'] == test_chain_id)

                            seq_id_mapping = {}
                            offset = None
                            for ref_seq_id, mid_code, test_seq_id in zip(sa['ref_seq_id'], sa['mid_code'], sa['test_seq_id']):
                                if test_seq_id is None:
                                    continue
                                if mid_code == '|':
                                    try:
                                        seq_id_mapping[test_seq_id] = next(auth_seq_id for auth_seq_id, seq_id
                                                                           in zip(poly_seq_model['auth_seq_id'], poly_seq_model['seq_id'])
                                                                           if seq_id == ref_seq_id and isinstance(auth_seq_id, int))
                                        if offset is None:
                                            offset = seq_id_mapping[test_seq_id] - test_seq_id
                                    except StopIteration:
                                        pass
                                elif mid_code == ' ' and test_seq_id in poly_seq_rst['seq_id']:
                                    idx = poly_seq_rst['seq_id'].index(test_seq_id)
                                    if poly_seq_rst['comp_id'][idx] == '.' and poly_seq_rst['auth_comp_id'][idx] not in emptyValue:
                                        seq_id_mapping[test_seq_id] = next(auth_seq_id for auth_seq_id, seq_id
                                                                           in zip(poly_seq_model['auth_seq_id'], poly_seq_model['seq_id'])
                                                                           if seq_id == ref_seq_id and isinstance(auth_seq_id, int))

                            if offset is not None and all(v - k == offset for k, v in seq_id_mapping.items()):
                                test_seq_id_list = list(seq_id_mapping.keys())
                                min_test_seq_id = min(test_seq_id_list)
                                max_test_seq_id = max(test_seq_id_list)
                                for test_seq_id in range(min_test_seq_id + 1, max_test_seq_id):
                                    if test_seq_id not in seq_id_mapping:
                                        seq_id_mapping[test_seq_id] = test_seq_id + offset

                            if ref_chain_id not in cyclicPolymer:
                                cyclicPolymer[ref_chain_id] =\
                                    isCyclicPolymer(self.__cR, self.__polySeq, ref_chain_id,
                                                    self.__representativeModelId, self.__representativeAltId, self.__modelNumName)

                            if cyclicPolymer[ref_chain_id]:

                                poly_seq_model = next(ps for ps in self.__polySeq
                                                      if ps['auth_chain_id'] == ref_chain_id)

                                offset = None
                                for seq_id, comp_id in zip(poly_seq_rst['seq_id'], poly_seq_rst['comp_id']):
                                    if seq_id is not None and seq_id not in seq_id_mapping:
                                        _seq_id = next((_seq_id for _seq_id, _comp_id in zip(poly_seq_model['seq_id'], poly_seq_model['comp_id'])
                                                        if _seq_id not in seq_id_mapping.values() and _comp_id == comp_id), None)
                                        if _seq_id is not None:
                                            offset = seq_id - _seq_id
                                            break

                                if offset is not None:
                                    for seq_id in poly_seq_rst['seq_id']:
                                        if seq_id is not None and seq_id not in seq_id_mapping:
                                            seq_id_mapping[seq_id] = seq_id - offset

                            if any(k for k, v in seq_id_mapping.items() if k != v)\
                               and not any(k for k, v in seq_id_mapping.items()
                                           if v in poly_seq_model['seq_id']
                                           and k == poly_seq_model['auth_seq_id'][poly_seq_model['seq_id'].index(v)]):
                                seqIdRemap.append({'chain_id': test_chain_id, 'seq_id_dict': seq_id_mapping})

                        if len(seqIdRemap) > 0:
                            if 'seq_id_remap' not in self.reasonsForReParsing:
                                self.reasonsForReParsing['seq_id_remap'] = seqIdRemap

                        if any(ps for ps in self.__polySeq if 'identical_chain_id' in ps):
                            polySeqRst, chainIdMapping = splitPolySeqRstForMultimers(self.__pA, self.__polySeq, self.__polySeqRst, self.__chainAssign)

                            if polySeqRst is not None and (not self.__hasNonPoly or len(self.__polySeq) // len(self.__nonPoly) in (1, 2)):
                                self.__polySeqRst = polySeqRst
                                if 'chain_id_remap' not in self.reasonsForReParsing:
                                    self.reasonsForReParsing['chain_id_remap'] = chainIdMapping

                        if len(self.__polySeq) == 1 and len(self.__polySeqRst) == 1:
                            polySeqRst, chainIdMapping, modelChainIdExt =\
                                splitPolySeqRstForExactNoes(self.__pA, self.__polySeq, self.__polySeqRst, self.__chainAssign)

                            if polySeqRst is not None:
                                self.__polySeqRst = polySeqRst
                                if 'chain_id_clone' not in self.reasonsForReParsing:
                                    self.reasonsForReParsing['chain_id_clone'] = chainIdMapping
                                if 'model_chain_id_ext' not in self.reasonsForReParsing:
                                    self.reasonsForReParsing['model_chain_id_ext'] = modelChainIdExt

                        if self.__hasNonPoly:
                            polySeqRst, nonPolyMapping = splitPolySeqRstForNonPoly(self.__ccU, self.__nonPoly, self.__polySeqRst,
                                                                                   self.__seqAlign, self.__chainAssign)

                            if polySeqRst is not None:
                                self.__polySeqRst = polySeqRst
                                if 'non_poly_remap' not in self.reasonsForReParsing:
                                    self.reasonsForReParsing['non_poly_remap'] = nonPolyMapping
                                else:
                                    for k, v in nonPolyMapping.items():
                                        if k not in self.reasonsForReParsing['non_poly_remap']:
                                            self.reasonsForReParsing['non_poly_remap'][k] = v
                                        else:
                                            for k2, v2 in v.items():
                                                if k2 not in self.reasonsForReParsing['non_poly_remap'][k]:
                                                    self.reasonsForReParsing['non_poly_remap'][k][k2] = v2

                        if self.__hasBranched:
                            polySeqRst, branchedMapping = splitPolySeqRstForBranched(self.__pA, self.__polySeq, self.__branched, self.__polySeqRst,
                                                                                     self.__chainAssign)

                            if polySeqRst is not None:
                                self.__polySeqRst = polySeqRst
                                if 'branched_remap' not in self.reasonsForReParsing:
                                    self.reasonsForReParsing['branched_remap'] = branchedMapping

                        if len(self.__polySeqRstFailed) > 0:
                            sortPolySeqRst(self.__polySeqRstFailed)
                            if not any(f for f in self.__f if '[Sequence mismatch]' in f):  # 2n6y
                                syncCompIdOfPolySeqRst(self.__polySeqRstFailed, self.__compIdMap)  # 2mx9

                            seqAlignFailed, _ = alignPolymerSequence(self.__pA, self.__polySeq, self.__polySeqRstFailed)
                            chainAssignFailed, _ = assignPolymerSequence(self.__pA, self.__ccU, self.__file_type,
                                                                         self.__polySeq, self.__polySeqRstFailed, seqAlignFailed)

                            if chainAssignFailed is not None:
                                seqIdRemapFailed = []

                                uniq_ps = not any('identical_chain_id' in ps for ps in self.__polySeq)

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

                                    poly_seq_model = next(ps for ps in self.__polySeq
                                                          if ps['auth_chain_id'] == ref_chain_id)

                                    seq_id_mapping = {}
                                    for ref_seq_id, mid_code, test_seq_id in zip(sa['ref_seq_id'], sa['mid_code'], sa['test_seq_id']):
                                        if test_seq_id is None:
                                            continue
                                        if mid_code == '|':
                                            try:
                                                seq_id_mapping[test_seq_id] = next(auth_seq_id for auth_seq_id, seq_id
                                                                                   in zip(poly_seq_model['auth_seq_id'], poly_seq_model['seq_id'])
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
                                                   and k == poly_seq_model['auth_seq_id'][poly_seq_model['seq_id'].index(v)]):
                                        seqIdRemapFailed.append({'chain_id': ref_chain_id, 'seq_id_dict': seq_id_mapping,
                                                                 'comp_id_set': list(set(poly_seq_model['comp_id']))})

                                if len(seqIdRemapFailed) > 0:
                                    if 'chain_seq_id_remap' not in self.reasonsForReParsing:
                                        seqIdRemap = self.reasonsForReParsing['seq_id_remap'] if 'seq_id_remap' in self.reasonsForReParsing else []
                                        if len(seqIdRemap) != len(seqIdRemapFailed)\
                                           or seqIdRemap[0]['chain_id'] != seqIdRemapFailed[0]['chain_id']\
                                           or not all(src_seq_id in seqIdRemap[0] for src_seq_id in seqIdRemapFailed[0]):
                                            self.reasonsForReParsing['chain_seq_id_remap'] = seqIdRemapFailed

                                else:
                                    for ps in self.__polySeqRstFailed:
                                        for ca in self.__chainAssign:
                                            ref_chain_id = ca['ref_chain_id']
                                            test_chain_id = ca['test_chain_id']

                                            if test_chain_id != ps['chain_id']:
                                                continue

                                            sa = next(sa for sa in self.__seqAlign
                                                      if sa['ref_chain_id'] == ref_chain_id
                                                      and sa['test_chain_id'] == test_chain_id)

                                            if len(sa['test_seq_id']) != len(sa['ref_seq_id']):
                                                continue

                                            poly_seq_model = next(ps for ps in self.__polySeq
                                                                  if ps['auth_chain_id'] == ref_chain_id)

                                            seq_id_mapping, comp_id_mapping = {}, {}

                                            for seq_id, comp_id in zip(ps['seq_id'], ps['comp_id']):
                                                if seq_id in sa['test_seq_id']:
                                                    idx = sa['test_seq_id'].index(seq_id)
                                                    auth_seq_id = sa['ref_seq_id'][idx]
                                                    seq_id_mapping[seq_id] = auth_seq_id
                                                    comp_id_mapping[seq_id] = comp_id
                                            if any(k for k, v in seq_id_mapping.items() if k != v)\
                                               or ('label_seq_scheme' not in self.reasonsForReParsing
                                                   and all(v not in poly_seq_model['auth_seq_id'] for v in seq_id_mapping.values())):
                                                seqIdRemapFailed.append({'chain_id': ref_chain_id, 'seq_id_dict': seq_id_mapping,
                                                                         'comp_id_dict': comp_id_mapping})

                                    if len(seqIdRemapFailed) > 0:
                                        if 'ext_chain_seq_id_remap' not in self.reasonsForReParsing:
                                            seqIdRemap = self.reasonsForReParsing['seq_id_remap'] if 'seq_id_remap' in self.reasonsForReParsing else []
                                            if len(seqIdRemap) != len(seqIdRemapFailed)\
                                               or seqIdRemap[0]['chain_id'] != seqIdRemapFailed[0]['chain_id']\
                                               or not all(src_seq_id in seqIdRemap[0] for src_seq_id in seqIdRemapFailed[0]):
                                                self.reasonsForReParsing['ext_chain_seq_id_remap'] = seqIdRemapFailed

            if 'local_seq_scheme' in self.reasonsForReParsing:
                if 'non_poly_remap' in self.reasonsForReParsing or 'branched_remap' in self.reasonsForReParsing:
                    del self.reasonsForReParsing['local_seq_scheme']
                elif 'seq_id_remap' in self.reasonsForReParsing:
                    del self.reasonsForReParsing['local_seq_scheme']
                elif 'chain_seq_id_remap' in self.reasonsForReParsing:
                    del self.reasonsForReParsing['local_seq_scheme']
                elif 'ext_chain_seq_id_remap' in self.reasonsForReParsing:
                    del self.reasonsForReParsing['local_seq_scheme']

            if 'local_seq_scheme' in self.reasonsForReParsing and len(self.reasonsForReParsing) == 1:
                sortPolySeqRst(self.__polySeqRstFailed)
                if len(self.__polySeqRstFailed) > 0:
                    self.reasonsForReParsing['extend_seq_scheme'] = self.__polySeqRstFailed
                del self.reasonsForReParsing['local_seq_scheme']
        finally:
            self.warningMessage = sorted(list(set(self.__f)), key=self.__f.index)

    # Enter a parse tree produced by DynamoMRParser#sequence.
    def enterSequence(self, ctx: DynamoMRParser.SequenceContext):
        if self.__has_sequence and not self.__open_sequence:
            self.__first_resid = 1
            self.__cur_sequence = ''

        if ctx.First_resid():
            self.__first_resid = int(str(ctx.Integer_DA()))

        if ctx.Sequence():
            if self.__hasCoord:
                i = 0
                while ctx.One_letter_code(i):
                    self.__cur_sequence += str(ctx.One_letter_code(i))
                    i += 1

        self.__open_sequence = True

    # Exit a parse tree produced by DynamoMRParser#sequence.
    def exitSequence(self, ctx: DynamoMRParser.SequenceContext):  # pylint: disable=unused-argument
        pass

    def closeSequqnce(self):
        self.__has_seq_align_err = False

        if not self.__open_sequence:
            return

        self.__has_sequence = len(self.__cur_sequence) > 0

        self.__open_sequence = False

    # Enter a parse tree produced by DynamoMRParser#distance_restraints.
    def enterDistance_restraints(self, ctx: DynamoMRParser.Distance_restraintsContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'dist'

        self.closeSequqnce()

    # Exit a parse tree produced by DynamoMRParser#distance_restraints.
    def exitDistance_restraints(self, ctx: DynamoMRParser.Distance_restraintsContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by DynamoMRParser#distance_restraint.
    def enterDistance_restraint(self, ctx: DynamoMRParser.Distance_restraintContext):  # pylint: disable=unused-argument
        self.distRestraints += 1

        self.atomSelectionSet.clear()

    # Exit a parse tree produced by DynamoMRParser#distance_restraint.
    def exitDistance_restraint(self, ctx: DynamoMRParser.Distance_restraintContext):

        try:

            index = int(str(ctx.Integer(0)))
            group = int(str(ctx.Integer(1)))

            seqId1 = int(str(ctx.Integer(2)))
            compId1 = str(ctx.Simple_name(0)).upper()
            atomId1 = str(ctx.Simple_name(1)).upper()
            seqId2 = int(str(ctx.Integer(3)))
            compId2 = str(ctx.Simple_name(2)).upper()
            atomId2 = str(ctx.Simple_name(3)).upper()

            target_value = None
            lower_limit = None
            upper_limit = None

            if len(self.numberSelection) == 0 or None in self.numberSelection:
                return

            lower_limit = self.numberSelection[0]
            upper_limit = self.numberSelection[1]
            # fource_const = self.numberSelection[2]
            weight = self.numberSelection[3]
            scale = self.numberSelection[4]

            if weight < 0.0:
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint(n=index, g=group)}"
                                f"The relative weight value of '{weight}' must not be a negative value.")
                return
            if weight == 0.0:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint(n=index, g=group)}"
                                f"The relative weight value of '{weight}' should be a positive value.")

            if scale < 0.0:
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint(n=index, g=group)}"
                                f"The relative scale value of '{scale}' must not be a negative value.")
                return
            if scale == 0.0:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint(n=index, g=group)}"
                                f"The relative scale value of '{scale}' should be a positive value.")

            if not self.__hasPolySeq and not self.__hasNonPolySeq:
                return

            self.__retrieveLocalSeqScheme()

            chainAssign1, asis1 = self.assignCoordPolymerSequence(None, seqId1, compId1, atomId1, index, group)
            chainAssign2, asis2 = self.assignCoordPolymerSequence(None, seqId2, compId2, atomId2, index, group)

            if 0 in (len(chainAssign1), len(chainAssign2)):
                return

            self.selectCoordAtoms(chainAssign1, seqId1, compId1, atomId1, True, index, group)
            self.selectCoordAtoms(chainAssign2, seqId2, compId2, atomId2, True, index, group)

            if len(self.atomSelectionSet) < 2:
                return

            self.__allowZeroUpperLimit = False
            if self.__reasons is not None and 'model_chain_id_ext' in self.__reasons\
               and len(self.atomSelectionSet[0]) > 0\
               and len(self.atomSelectionSet[0]) == len(self.atomSelectionSet[1]):
                chain_id_1 = self.atomSelectionSet[0][0]['chain_id']
                seq_id_1 = self.atomSelectionSet[0][0]['seq_id']
                atom_id_1 = self.atomSelectionSet[0][0]['atom_id']

                chain_id_2 = self.atomSelectionSet[1][0]['chain_id']
                seq_id_2 = self.atomSelectionSet[1][0]['seq_id']
                atom_id_2 = self.atomSelectionSet[1][0]['atom_id']

                if chain_id_1 != chain_id_2 and seq_id_1 == seq_id_2 and atom_id_1 == atom_id_2\
                   and ((chain_id_1 in self.__reasons['model_chain_id_ext'] and chain_id_2 in self.__reasons['model_chain_id_ext'][chain_id_1])
                        or (chain_id_2 in self.__reasons['model_chain_id_ext'] and chain_id_1 in self.__reasons['model_chain_id_ext'][chain_id_2])):
                    self.__allowZeroUpperLimit = True
            self.__allowZeroUpperLimit |= hasInterChainRestraint(self.atomSelectionSet)

            dstFunc = self.validateDistanceRange(index, group, weight, scale, target_value, lower_limit, upper_limit, self.__omitDistLimitOutlier)

            if dstFunc is None:
                return

            if self.__createSfDict:
                sf = self.__getSf(constraintType=getDistConstraintType(self.atomSelectionSet, dstFunc,
                                                                       self.__csStat, self.__originalFileName),
                                  potentialType=getPotentialType(self.__file_type, self.__cur_subtype, dstFunc),
                                  softwareName='DYNAMO')
                sf['id'] += 1
                memberLogicCode = 'OR' if len(self.atomSelectionSet[0]) * len(self.atomSelectionSet[1]) > 1 else '.'

            has_intra_chain, rep_chain_id_set = hasIntraChainRestraint(self.atomSelectionSet)

            memberId = '.'
            if self.__createSfDict:
                if memberLogicCode == 'OR' and has_intra_chain and len(rep_chain_id_set) == 1:
                    memberLogicCode = '.'

                if memberLogicCode == 'OR':
                    if len(self.atomSelectionSet[0]) * len(self.atomSelectionSet[1]) > 1\
                       and (isAmbigAtomSelection(self.atomSelectionSet[0], self.__csStat)
                            or isAmbigAtomSelection(self.atomSelectionSet[1], self.__csStat)):
                        memberId = 0
                        _atom1 = _atom2 = None

            for atom1, atom2 in itertools.product(self.atomSelectionSet[0],
                                                  self.atomSelectionSet[1]):
                atoms = [atom1, atom2]
                if isIdenticalRestraint(atoms, self.__nefT):
                    continue
                if self.__createSfDict and isinstance(memberId, int):
                    star_atom1 = getStarAtom(self.__authToStarSeq, self.__authToOrigSeq, self.__offsetHolder, copy.copy(atom1))
                    star_atom2 = getStarAtom(self.__authToStarSeq, self.__authToOrigSeq, self.__offsetHolder, copy.copy(atom2))
                    if None in (star_atom1, star_atom2) or isIdenticalRestraint([star_atom1, star_atom2], self.__nefT):
                        continue
                if has_intra_chain and (atom1['chain_id'] != atom2['chain_id'] or atom1['chain_id'] not in rep_chain_id_set):
                    continue
                if self.__createSfDict and memberLogicCode == '.':
                    altAtomId1, altAtomId2 = getAltProtonIdInBondConstraint(atoms, self.__csStat)
                    if altAtomId1 is not None or altAtomId2 is not None:
                        atom1, atom2 =\
                            self.selectRealisticBondConstraint(atom1, atom2,
                                                               altAtomId1, altAtomId2,
                                                               dstFunc)
                if self.__debug:
                    print(f"subtype={self.__cur_subtype} id={self.distRestraints} (index={index}, group={group}) "
                          f"atom1={atom1} atom2={atom2} {dstFunc}")
                if self.__createSfDict and sf is not None:
                    if isinstance(memberId, int):
                        if _atom1 is None or isAmbigAtomSelection([_atom1, atom1], self.__csStat)\
                           or isAmbigAtomSelection([_atom2, atom2], self.__csStat):
                            memberId += 1
                            _atom1, _atom2 = atom1, atom2
                    sf['index_id'] += 1
                    row = getRow(self.__cur_subtype, sf['id'], sf['index_id'],
                                 '.', memberId, memberLogicCode,
                                 sf['list_id'], self.__entryId, dstFunc,
                                 self.__authToStarSeq, self.__authToOrigSeq, self.__authToInsCode, self.__offsetHolder,
                                 atom1, atom2, asis1=asis1, asis2=asis2)
                    sf['loop'].add_data(row)

                    if sf['constraint_subsubtype'] == 'ambi':
                        continue

                    if self.__cur_constraint_type is not None and self.__cur_constraint_type.startswith('ambiguous'):
                        sf['constraint_subsubtype'] = 'ambi'

                    if memberLogicCode == 'OR'\
                       and (isAmbigAtomSelection(self.atomSelectionSet[0], self.__csStat)
                            or isAmbigAtomSelection(self.atomSelectionSet[1], self.__csStat)):
                        sf['constraint_subsubtype'] = 'ambi'

                    if 'upper_limit' in dstFunc and dstFunc['upper_limit'] is not None:
                        upperLimit = float(dstFunc['upper_limit'])
                        if upperLimit <= DIST_AMBIG_LOW or upperLimit >= DIST_AMBIG_UP:
                            sf['constraint_subsubtype'] = 'ambi'

            if self.__createSfDict and sf is not None and isinstance(memberId, int) and memberId == 1:
                sf['loop'].data[-1] = resetMemberId(self.__cur_subtype, sf['loop'].data[-1])

        except ValueError:
            self.distRestraints -= 1

        finally:
            self.numberSelection.clear()

    # Enter a parse tree produced by DynamoMRParser#distance_restraints_sw_segid.
    def enterDistance_restraints_sw_segid(self, ctx: DynamoMRParser.Distance_restraints_sw_segidContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'dist'

        self.closeSequqnce()

    # Exit a parse tree produced by DynamoMRParser#distance_restraints_sw_segid.
    def exitDistance_restraints_sw_segid(self, ctx: DynamoMRParser.Distance_restraints_sw_segidContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by DynamoMRParser#distance_restraint_sw_segid.
    def enterDistance_restraint_sw_segid(self, ctx: DynamoMRParser.Distance_restraint_sw_segidContext):  # pylint: disable=unused-argument
        self.distRestraints += 1

        self.atomSelectionSet.clear()

    # Exit a parse tree produced by DynamoMRParser#distance_restraint_sw_segid.
    def exitDistance_restraint_sw_segid(self, ctx: DynamoMRParser.Distance_restraint_sw_segidContext):

        try:

            index = int(str(ctx.Integer(0)))
            group = int(str(ctx.Integer(1)))

            chainId1 = str(ctx.Simple_name(0))
            seqId1 = int(str(ctx.Integer(2)))
            compId1 = str(ctx.Simple_name(1)).upper()
            atomId1 = str(ctx.Simple_name(2)).upper()
            chainId2 = str(ctx.Simple_name(3))
            seqId2 = int(str(ctx.Integer(3)))
            compId2 = str(ctx.Simple_name(4)).upper()
            atomId2 = str(ctx.Simple_name(5)).upper()

            target_value = None
            lower_limit = None
            upper_limit = None

            if len(self.numberSelection) == 0 or None in self.numberSelection:
                return

            lower_limit = self.numberSelection[0]
            upper_limit = self.numberSelection[1]
            # fource_const = self.numberSelection[2]
            weight = self.numberSelection[3]
            scale = self.numberSelection[4]

            if weight < 0.0:
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint(n=index, g=group)}"
                                f"The relative weight value of '{weight}' must not be a negative value.")
                return
            if weight == 0.0:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint(n=index, g=group)}"
                                f"The relative weight value of '{weight}' should be a positive value.")

            if scale < 0.0:
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint(n=index, g=group)}"
                                f"The relative scale value of '{scale}' must not be a negative value.")
                return
            if scale == 0.0:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint(n=index, g=group)}"
                                f"The relative scale value of '{scale}' should be a positive value.")

            if not self.__hasPolySeq and not self.__hasNonPolySeq:
                return

            self.__retrieveLocalSeqScheme()

            chainAssign1, asis1 = self.assignCoordPolymerSequence(chainId1, seqId1, compId1, atomId1, index, group)
            chainAssign2, asis2 = self.assignCoordPolymerSequence(chainId2, seqId2, compId2, atomId2, index, group)

            if 0 in (len(chainAssign1), len(chainAssign2)):
                return

            self.selectCoordAtoms(chainAssign1, seqId1, compId1, atomId1, True, index, group)
            self.selectCoordAtoms(chainAssign2, seqId2, compId2, atomId2, True, index, group)

            if len(self.atomSelectionSet) < 2:
                return

            self.__allowZeroUpperLimit = False
            if self.__reasons is not None and 'model_chain_id_ext' in self.__reasons\
               and len(self.atomSelectionSet[0]) > 0\
               and len(self.atomSelectionSet[0]) == len(self.atomSelectionSet[1]):
                chain_id_1 = self.atomSelectionSet[0][0]['chain_id']
                seq_id_1 = self.atomSelectionSet[0][0]['seq_id']
                atom_id_1 = self.atomSelectionSet[0][0]['atom_id']

                chain_id_2 = self.atomSelectionSet[1][0]['chain_id']
                seq_id_2 = self.atomSelectionSet[1][0]['seq_id']
                atom_id_2 = self.atomSelectionSet[1][0]['atom_id']

                if chain_id_1 != chain_id_2 and seq_id_1 == seq_id_2 and atom_id_1 == atom_id_2\
                   and ((chain_id_1 in self.__reasons['model_chain_id_ext'] and chain_id_2 in self.__reasons['model_chain_id_ext'][chain_id_1])
                        or (chain_id_2 in self.__reasons['model_chain_id_ext'] and chain_id_1 in self.__reasons['model_chain_id_ext'][chain_id_2])):
                    self.__allowZeroUpperLimit = True
            self.__allowZeroUpperLimit |= hasInterChainRestraint(self.atomSelectionSet)

            dstFunc = self.validateDistanceRange(index, group, weight, scale, target_value, lower_limit, upper_limit, self.__omitDistLimitOutlier)

            if dstFunc is None:
                return

            memberId = '.'
            if self.__createSfDict:
                sf = self.__getSf(constraintType=getDistConstraintType(self.atomSelectionSet, dstFunc,
                                                                       self.__csStat, self.__originalFileName),
                                  potentialType=getPotentialType(self.__file_type, self.__cur_subtype, dstFunc),
                                  softwareName='DYNAMO')
                sf['id'] += 1
                memberLogicCode = 'OR' if len(self.atomSelectionSet[0]) * len(self.atomSelectionSet[1]) > 1 else '.'

                if memberLogicCode == 'OR':
                    if len(self.atomSelectionSet[0]) * len(self.atomSelectionSet[1]) > 1\
                       and (isAmbigAtomSelection(self.atomSelectionSet[0], self.__csStat)
                            or isAmbigAtomSelection(self.atomSelectionSet[1], self.__csStat)):
                        memberId = 0
                        _atom1 = _atom2 = None

            for atom1, atom2 in itertools.product(self.atomSelectionSet[0],
                                                  self.atomSelectionSet[1]):
                atoms = [atom1, atom2]
                if isIdenticalRestraint(atoms, self.__nefT):
                    continue
                if self.__createSfDict and isinstance(memberId, int):
                    star_atom1 = getStarAtom(self.__authToStarSeq, self.__authToOrigSeq, self.__offsetHolder, copy.copy(atom1))
                    star_atom2 = getStarAtom(self.__authToStarSeq, self.__authToOrigSeq, self.__offsetHolder, copy.copy(atom2))
                    if None in (star_atom1, star_atom2) or isIdenticalRestraint([star_atom1, star_atom2], self.__nefT):
                        continue
                if self.__createSfDict and memberLogicCode == '.':
                    altAtomId1, altAtomId2 = getAltProtonIdInBondConstraint(atoms, self.__csStat)
                    if altAtomId1 is not None or altAtomId2 is not None:
                        atom1, atom2 =\
                            self.selectRealisticBondConstraint(atom1, atom2,
                                                               altAtomId1, altAtomId2,
                                                               dstFunc)
                if self.__debug:
                    print(f"subtype={self.__cur_subtype} id={self.distRestraints} (index={index}, group={group}) "
                          f"atom1={atom1} atom2={atom2} {dstFunc}")
                if self.__createSfDict and sf is not None:
                    if isinstance(memberId, int):
                        if _atom1 is None or isAmbigAtomSelection([_atom1, atom1], self.__csStat)\
                           or isAmbigAtomSelection([_atom2, atom2], self.__csStat):
                            memberId += 1
                            _atom1, _atom2 = atom1, atom2
                    sf['index_id'] += 1
                    row = getRow(self.__cur_subtype, sf['id'], sf['index_id'],
                                 '.', memberId, memberLogicCode,
                                 sf['list_id'], self.__entryId, dstFunc,
                                 self.__authToStarSeq, self.__authToOrigSeq, self.__authToInsCode, self.__offsetHolder,
                                 atom1, atom2, asis1=asis1, asis2=asis2)
                    sf['loop'].add_data(row)

                    if sf['constraint_subsubtype'] == 'ambi':
                        continue

                    if self.__cur_constraint_type is not None and self.__cur_constraint_type.startswith('ambiguous'):
                        sf['constraint_subsubtype'] = 'ambi'

                    if memberLogicCode == 'OR'\
                       and (isAmbigAtomSelection(self.atomSelectionSet[0], self.__csStat)
                            or isAmbigAtomSelection(self.atomSelectionSet[1], self.__csStat)):
                        sf['constraint_subsubtype'] = 'ambi'

                    if 'upper_limit' in dstFunc and dstFunc['upper_limit'] is not None:
                        upperLimit = float(dstFunc['upper_limit'])
                        if upperLimit <= DIST_AMBIG_LOW or upperLimit >= DIST_AMBIG_UP:
                            sf['constraint_subsubtype'] = 'ambi'

            if self.__createSfDict and sf is not None and isinstance(memberId, int) and memberId == 1:
                sf['loop'].data[-1] = resetMemberId(self.__cur_subtype, sf['loop'].data[-1])

        except ValueError:
            self.distRestraints -= 1

        finally:
            self.numberSelection.clear()

    # Enter a parse tree produced by DynamoMRParser#distance_restraints_ew_segid.
    def enterDistance_restraints_ew_segid(self, ctx: DynamoMRParser.Distance_restraints_ew_segidContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'dist'

        self.closeSequqnce()

    # Exit a parse tree produced by DynamoMRParser#distance_restraints_ew_segid.
    def exitDistance_restraints_ew_segid(self, ctx: DynamoMRParser.Distance_restraints_ew_segidContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by DynamoMRParser#distance_restraint_ew_segid.
    def enterDistance_restraint_ew_segid(self, ctx: DynamoMRParser.Distance_restraint_ew_segidContext):  # pylint: disable=unused-argument
        self.distRestraints += 1

        self.atomSelectionSet.clear()

    # Exit a parse tree produced by DynamoMRParser#distance_restraint_ew_segid.
    def exitDistance_restraint_ew_segid(self, ctx: DynamoMRParser.Distance_restraint_ew_segidContext):

        try:

            index = int(str(ctx.Integer(0)))
            group = int(str(ctx.Integer(1)))

            seqId1 = int(str(ctx.Integer(2)))
            compId1 = str(ctx.Simple_name(0)).upper()
            atomId1 = str(ctx.Simple_name(1)).upper()
            chainId1 = str(ctx.Simple_name(2))
            chainId2 = str(ctx.Simple_name(5))
            seqId2 = int(str(ctx.Integer(3)))
            compId2 = str(ctx.Simple_name(3)).upper()
            atomId2 = str(ctx.Simple_name(4)).upper()
            chainId2 = str(ctx.Simple_name(5))

            target_value = None
            lower_limit = None
            upper_limit = None

            if len(self.numberSelection) == 0 or None in self.numberSelection:
                return

            lower_limit = self.numberSelection[0]
            upper_limit = self.numberSelection[1]
            # fource_const = self.numberSelection[2]
            weight = self.numberSelection[3]
            scale = self.numberSelection[4]

            if weight < 0.0:
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint(n=index, g=group)}"
                                f"The relative weight value of '{weight}' must not be a negative value.")
                return
            if weight == 0.0:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint(n=index, g=group)}"
                                f"The relative weight value of '{weight}' should be a positive value.")

            if scale < 0.0:
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint(n=index, g=group)}"
                                f"The relative scale value of '{scale}' must not be a negative value.")
                return
            if scale == 0.0:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint(n=index, g=group)}"
                                f"The relative scale value of '{scale}' should be a positive value.")

            if not self.__hasPolySeq and not self.__hasNonPolySeq:
                return

            self.__retrieveLocalSeqScheme()

            chainAssign1, asis1 = self.assignCoordPolymerSequence(chainId1, seqId1, compId1, atomId1, index, group)
            chainAssign2, asis2 = self.assignCoordPolymerSequence(chainId2, seqId2, compId2, atomId2, index, group)

            if 0 in (len(chainAssign1), len(chainAssign2)):
                return

            self.selectCoordAtoms(chainAssign1, seqId1, compId1, atomId1, True, index, group)
            self.selectCoordAtoms(chainAssign2, seqId2, compId2, atomId2, True, index, group)

            if len(self.atomSelectionSet) < 2:
                return

            self.__allowZeroUpperLimit = False
            if self.__reasons is not None and 'model_chain_id_ext' in self.__reasons\
               and len(self.atomSelectionSet[0]) > 0\
               and len(self.atomSelectionSet[0]) == len(self.atomSelectionSet[1]):
                chain_id_1 = self.atomSelectionSet[0][0]['chain_id']
                seq_id_1 = self.atomSelectionSet[0][0]['seq_id']
                atom_id_1 = self.atomSelectionSet[0][0]['atom_id']

                chain_id_2 = self.atomSelectionSet[1][0]['chain_id']
                seq_id_2 = self.atomSelectionSet[1][0]['seq_id']
                atom_id_2 = self.atomSelectionSet[1][0]['atom_id']

                if chain_id_1 != chain_id_2 and seq_id_1 == seq_id_2 and atom_id_1 == atom_id_2\
                   and ((chain_id_1 in self.__reasons['model_chain_id_ext'] and chain_id_2 in self.__reasons['model_chain_id_ext'][chain_id_1])
                        or (chain_id_2 in self.__reasons['model_chain_id_ext'] and chain_id_1 in self.__reasons['model_chain_id_ext'][chain_id_2])):
                    self.__allowZeroUpperLimit = True
            self.__allowZeroUpperLimit |= hasInterChainRestraint(self.atomSelectionSet)

            dstFunc = self.validateDistanceRange(index, group, weight, scale, target_value, lower_limit, upper_limit, self.__omitDistLimitOutlier)

            if dstFunc is None:
                return

            memberId = '.'
            if self.__createSfDict:
                sf = self.__getSf(constraintType=getDistConstraintType(self.atomSelectionSet, dstFunc,
                                                                       self.__csStat, self.__originalFileName),
                                  potentialType=getPotentialType(self.__file_type, self.__cur_subtype, dstFunc),
                                  softwareName='DYNAMO')
                sf['id'] += 1
                memberLogicCode = 'OR' if len(self.atomSelectionSet[0]) * len(self.atomSelectionSet[1]) > 1 else '.'

                if memberLogicCode == 'OR':
                    if len(self.atomSelectionSet[0]) * len(self.atomSelectionSet[1]) > 1\
                       and (isAmbigAtomSelection(self.atomSelectionSet[0], self.__csStat)
                            or isAmbigAtomSelection(self.atomSelectionSet[1], self.__csStat)):
                        memberId = 0
                        _atom1 = _atom2 = None

            for atom1, atom2 in itertools.product(self.atomSelectionSet[0],
                                                  self.atomSelectionSet[1]):
                atoms = [atom1, atom2]
                if isIdenticalRestraint(atoms, self.__nefT):
                    continue
                if self.__createSfDict and isinstance(memberId, int):
                    star_atom1 = getStarAtom(self.__authToStarSeq, self.__authToOrigSeq, self.__offsetHolder, copy.copy(atom1))
                    star_atom2 = getStarAtom(self.__authToStarSeq, self.__authToOrigSeq, self.__offsetHolder, copy.copy(atom2))
                    if None in (star_atom1, star_atom2) or isIdenticalRestraint([star_atom1, star_atom2], self.__nefT):
                        continue
                if self.__createSfDict and memberLogicCode == '.':
                    altAtomId1, altAtomId2 = getAltProtonIdInBondConstraint(atoms, self.__csStat)
                    if altAtomId1 is not None or altAtomId2 is not None:
                        atom1, atom2 =\
                            self.selectRealisticBondConstraint(atom1, atom2,
                                                               altAtomId1, altAtomId2,
                                                               dstFunc)
                if self.__debug:
                    print(f"subtype={self.__cur_subtype} id={self.distRestraints} (index={index}, group={group}) "
                          f"atom1={atom1} atom2={atom2} {dstFunc}")
                if self.__createSfDict and sf is not None:
                    if isinstance(memberId, int):
                        if _atom1 is None or isAmbigAtomSelection([_atom1, atom1], self.__csStat)\
                           or isAmbigAtomSelection([_atom2, atom2], self.__csStat):
                            memberId += 1
                            _atom1, _atom2 = atom1, atom2
                    sf['index_id'] += 1
                    row = getRow(self.__cur_subtype, sf['id'], sf['index_id'],
                                 '.', memberId, memberLogicCode,
                                 sf['list_id'], self.__entryId, dstFunc,
                                 self.__authToStarSeq, self.__authToOrigSeq, self.__authToInsCode, self.__offsetHolder,
                                 atom1, atom2, asis1=asis1, asis2=asis2)
                    sf['loop'].add_data(row)

                    if sf['constraint_subsubtype'] == 'ambi':
                        continue

                    if self.__cur_constraint_type is not None and self.__cur_constraint_type.startswith('ambiguous'):
                        sf['constraint_subsubtype'] = 'ambi'

                    if memberLogicCode == 'OR'\
                       and (isAmbigAtomSelection(self.atomSelectionSet[0], self.__csStat)
                            or isAmbigAtomSelection(self.atomSelectionSet[1], self.__csStat)):
                        sf['constraint_subsubtype'] = 'ambi'
                    if 'upper_limit' in dstFunc and dstFunc['upper_limit'] is not None:
                        upperLimit = float(dstFunc['upper_limit'])
                        if upperLimit <= DIST_AMBIG_LOW or upperLimit >= DIST_AMBIG_UP:
                            sf['constraint_subsubtype'] = 'ambi'

            if self.__createSfDict and sf is not None and isinstance(memberId, int) and memberId == 1:
                sf['loop'].data[-1] = resetMemberId(self.__cur_subtype, sf['loop'].data[-1])

        except ValueError:
            self.distRestraints -= 1

        finally:
            self.numberSelection.clear()

    def validateDistanceRange(self, index: int, group: int, weight: float, scale: float, target_value: Optional[float],
                              lower_limit: Optional[float], upper_limit: Optional[float], omit_dist_limit_outlier: bool) -> Optional[dict]:
        """ Validate distance value range.
        """

        validRange = True
        dstFunc = {'weight': weight, 'scale': scale}

        if None not in (target_value, upper_limit, lower_limit)\
           and abs(target_value - lower_limit) <= DIST_AMBIG_UNCERT\
           and abs(target_value - upper_limit) <= DIST_AMBIG_UNCERT:
            if target_value >= DIST_AMBIG_MED:
                lower_limit = None
            elif target_value <= DIST_AMBIG_LOW:
                upper_limit = None

        if target_value is not None:
            if DIST_ERROR_MIN < target_value < DIST_ERROR_MAX or (target_value == 0.0 and self.__allowZeroUpperLimit):
                dstFunc['target_value'] = f"{target_value:.3f}" if target_value > 0.0 else "0.0"
            else:
                if target_value <= DIST_ERROR_MIN and omit_dist_limit_outlier:
                    self.__f.append(f"[Range value warning] {self.__getCurrentRestraint(n=index, g=group)}"
                                    f"The target value='{target_value:.3f}' is omitted because it is not within range {DIST_RESTRAINT_ERROR}.")
                    target_value = None
                else:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint(n=index, g=group)}"
                                    f"The target value='{target_value:.3f}' must be within range {DIST_RESTRAINT_ERROR}.")

        if lower_limit is not None:
            if DIST_ERROR_MIN <= lower_limit < DIST_ERROR_MAX:
                dstFunc['lower_limit'] = f"{lower_limit:.3f}" if lower_limit > 0.0 else "0.0"
            else:
                if lower_limit <= DIST_ERROR_MIN and omit_dist_limit_outlier:
                    self.__f.append(f"[Range value warning] {self.__getCurrentRestraint(n=index, g=group)}"
                                    f"The lower limit value='{lower_limit:.3f}' is omitted because it is not within range {DIST_RESTRAINT_ERROR}.")
                    lower_limit = None
                else:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint(n=index, g=group)}"
                                    f"The lower limit value='{lower_limit:.3f}' must be within range {DIST_RESTRAINT_ERROR}.")

        if upper_limit is not None:
            if DIST_ERROR_MIN < upper_limit <= DIST_ERROR_MAX or (upper_limit == 0.0 and self.__allowZeroUpperLimit):
                dstFunc['upper_limit'] = f"{upper_limit:.3f}" if upper_limit > 0.0 else "0.0"
            else:
                if (upper_limit <= DIST_ERROR_MIN or upper_limit > DIST_ERROR_MAX) and omit_dist_limit_outlier:
                    self.__f.append(f"[Range value warning] {self.__getCurrentRestraint(n=index,g=group)}"
                                    f"The upper limit value='{upper_limit:.3f}' is omitted because it is not within range {DIST_RESTRAINT_ERROR}.")
                    upper_limit = None
                else:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint(n=index, g=group)}"
                                    f"The upper limit value='{upper_limit:.3f}' must be within range {DIST_RESTRAINT_ERROR}.")

        if target_value is not None:

            if lower_limit is not None:
                if lower_limit > target_value:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint(n=index, g=group)}"
                                    f"The lower limit value='{lower_limit:.3f}' must be less than the target value '{target_value:.3f}'.")

            if upper_limit is not None:
                if upper_limit < target_value:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint(n=index, g=group)}"
                                    f"The upper limit value='{upper_limit:.3f}' must be greater than the target value '{target_value:.3f}'.")

        else:

            if None not in (lower_limit, upper_limit):
                if lower_limit > upper_limit:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint(n=index, g=group)}"
                                    f"The lower limit value='{lower_limit:.3f}' must be less than the upper limit value '{upper_limit:.3f}'.")

        if not validRange:
            return None

        if target_value is not None:
            if DIST_RANGE_MIN <= target_value <= DIST_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint(n=index, g=group)}"
                                f"The target value='{target_value:.3f}' should be within range {DIST_RESTRAINT_RANGE}.")

        if lower_limit is not None:
            if DIST_RANGE_MIN <= lower_limit <= DIST_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint(n=index, g=group)}"
                                f"The lower limit value='{lower_limit:.3f}' should be within range {DIST_RESTRAINT_RANGE}.")

        if upper_limit is not None:
            if DIST_RANGE_MIN <= upper_limit <= DIST_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint(n=index, g=group)}"
                                f"The upper limit value='{upper_limit:.3f}' should be within range {DIST_RESTRAINT_RANGE}.")

        if target_value is None and lower_limit is None and upper_limit is None:
            return None

        return dstFunc

    def getRealChainSeqId(self, ps: dict, seqId: int, compId: str, isPolySeq: bool = True) -> Tuple[str, int, Optional[str]]:
        compId = _compId = translateToStdResName(compId, ccU=self.__ccU)
        if len(_compId) == 2 and _compId.startswith('D'):
            _compId = compId[1]
        if not self.__preferAuthSeq:
            seqKey = (ps['auth_chain_id'], seqId)
            if seqKey in self.__labelToAuthSeq:
                _chainId, _seqId = self.__labelToAuthSeq[seqKey]
                if _seqId in ps['auth_seq_id']:
                    return _chainId, _seqId, ps['comp_id'][ps['seq_id'].index(seqId)]
                if seqKey[1] in ps['seq_id']:  # resolve conflict between label/auth sequence schemes of polymer/non-polymer (2l90)
                    idx = ps['seq_id'].index(seqKey[1])
                    return _chainId, ps['auth_seq_id'][idx], ps['comp_id'][idx]
        if seqId in ps['auth_seq_id']:
            for idx in [_idx for _idx, _seqId in enumerate(ps['auth_seq_id']) if _seqId == seqId]:
                if 'alt_comp_id' in ps and idx < len(ps['alt_comp_id']):
                    if compId in (ps['comp_id'][idx], ps['auth_comp_id'][idx], ps['alt_comp_id'][idx], 'MTS', 'ORI'):
                        return ps['auth_chain_id'], seqId, ps['comp_id'][idx]
                    if compId != _compId and _compId in (ps['comp_id'][idx], ps['auth_comp_id'][idx], ps['alt_comp_id'][idx], 'MTS', 'ORI'):
                        return ps['auth_chain_id'], seqId, ps['comp_id'][idx]
                if compId in (ps['comp_id'][idx], ps['auth_comp_id'][idx], 'MTS', 'ORI')\
                   or (isPolySeq and seqId == 1
                       and ((compId.endswith('-N') and all(c in ps['comp_id'][idx] for c in compId.split('-')[0]))
                            or (ps['comp_id'][idx] == 'PCA' and 'P' == compId[0] and ('GL' in compId or 'N' in compId)))):
                    return ps['auth_chain_id'], seqId, ps['comp_id'][idx]
                if compId != _compId and _compId in (ps['comp_id'][idx], ps['auth_comp_id'][idx], 'MTS', 'ORI'):
                    return ps['auth_chain_id'], seqId, ps['comp_id'][idx]
        if self.__reasons is not None and 'extend_seq_scheme' in self.__reasons:
            _ps = next((_ps for _ps in self.__reasons['extend_seq_scheme'] if _ps['chain_id'] == ps['auth_chain_id']), None)
            if _ps is not None:
                if seqId in _ps['seq_id']:
                    return ps['auth_chain_id'], seqId, _ps['comp_id'][_ps['seq_id'].index(seqId)]
        return ps['auth_chain_id'], seqId, None

    def translateToStdResNameWrapper(self, seqId: int, compId: str, preferNonPoly: bool = False) -> str:
        _compId = compId
        refCompId = None
        for ps in self.__polySeq:
            if preferNonPoly:
                continue
            _, _, refCompId = self.getRealChainSeqId(ps, seqId, _compId)
            if refCompId is not None:
                compId = translateToStdResName(_compId, refCompId=refCompId, ccU=self.__ccU)
                if compId != _compId and compId in monDict3 and _compId in monDict3:
                    continue
                break
        if refCompId is None and self.__hasNonPolySeq:
            for np in self.__nonPolySeq:
                _, _, refCompId = self.getRealChainSeqId(np, seqId, _compId, False)
                if refCompId is not None:
                    compId = translateToStdResName(_compId, refCompId=refCompId, ccU=self.__ccU)
                    break
        if refCompId is None:
            compId = translateToStdResName(_compId, ccU=self.__ccU)
        return compId

    def assignCoordPolymerSequence(self, refChainId: str, seqId: int, compId: str, atomId: str,
                                   index: Optional[int] = None, group: Optional[int] = None) -> Tuple[List[Tuple[str, int, str, bool]], bool]:
        """ Assign polymer sequences of the coordinates.
        """

        if self.__has_sequence and self.__reasons is None:
            if self.__first_resid <= seqId < self.__first_resid + len(self.__cur_sequence):
                oneLetterCode = self.__cur_sequence[seqId - self.__first_resid].upper()

                _compId = next(k for k, v in monDict3.items() if v == oneLetterCode)

                if _compId != translateToStdResName(compId, ccU=self.__ccU) and _compId != 'X':
                    self.__f.append(f"[Sequence mismatch warning] {self.__getCurrentRestraint()}"
                                    f"Sequence alignment error between the sequence ({seqId}:{_compId}) "
                                    f"and data ({seqId}:{compId}). "
                                    "Please verify the consistency between the internally defined sequence and restraints and re-upload the restraint file(s).")
                    self.__has_seq_align_err = True
                    return []

        _refChainId = refChainId

        chainAssign = set()
        asis = preferNonPoly = False

        _seqId = seqId
        _compId = compId

        fixedChainId = fixedSeqId = fixedCompId = None

        self.__allow_ext_seq = False

        if self.__hasNonPoly:

            resolved = False

            for np in self.__nonPoly:
                if 'alt_comp_id' in np and 'alt_auth_seq_id' in np\
                   and compId in np['alt_comp_id'] and seqId in np['alt_auth_seq_id']:
                    npCompId = np['comp_id'][0]
                    npSeqId = np['auth_seq_id'][0]
                    for ps in self.__polySeq:
                        if 'ambig_auth_seq_id' in ps and seqId in ps['ambig_auth_seq_id']:
                            psCompId = ps['comp_id'][ps['auth_seq_id'].index(seqId)]
                            _atomId, _, details = self.__nefT.get_valid_star_atom_in_xplor(psCompId, atomId, leave_unmatched=True)
                            if details is None:
                                _, _coordAtomSite = self.getCoordAtomSiteOf(ps['auth_chain_id'], seqId, psCompId, cifCheck=self.__hasCoord)
                                if _coordAtomSite is not None and all(_atomId_ in _coordAtomSite['atom_id'] for _atomId_ in _atomId):
                                    compId = _compId = psCompId
                                    resolved = True
                                    break
                            _, _coordAtomSite = self.getCoordAtomSiteOf(np['auth_chain_id'], npSeqId, npCompId, cifCheck=self.__hasCoord)
                            if self.__mrAtomNameMapping is not None:
                                atomId = retrieveAtomIdFromMRMap(self.__ccU, self.__mrAtomNameMapping, npSeqId, npCompId, atomId, _coordAtomSite)
                            _atomId, _, details = self.__nefT.get_valid_star_atom_in_xplor(npCompId, atomId, leave_unmatched=True)
                            if details is None:
                                if _coordAtomSite is not None and all(_atomId_ in _coordAtomSite['atom_id'] for _atomId_ in _atomId):
                                    compId = _compId = npCompId
                                    seqId = _seqId = npSeqId
                                    preferNonPoly = resolved = True
                                    break

            if not resolved and compId in ('CYSZ', 'CYZ', 'CYS', 'ION', 'ZN1', 'ZN2')\
               and atomId in zincIonCode:
                znCount = 0
                znSeqId = None
                for np in self.__nonPoly:
                    if np['comp_id'][0] == 'ZN':
                        znSeqId = np['auth_seq_id'][0]
                        znCount += 1
                if znCount > 0:
                    compId = _compId = 'ZN'
                    if znCount == 1:
                        seqId = _seqId = znSeqId
                        atomId = 'ZN'
                        resolved = True
                    preferNonPoly = True

            if not resolved and compId in ('CYS', 'CYSC', 'CYC', 'CCA', 'CYO', 'ION', 'CA1', 'CA2')\
               and atomId in calciumIonCode:
                caCount = 0
                caSeqId = None
                for np in self.__nonPoly:
                    if np['comp_id'][0] == 'CA':
                        caSeqId = np['auth_seq_id'][0]
                        caCount += 1
                if caCount > 0:
                    compId = _compId = 'CA'
                    if caCount == 1:
                        seqId = _seqId = caSeqId
                        atomId = 'CA'
                        resolved = True
                    preferNonPoly = True

            if not resolved and len(atomId) > 1 and atomId in SYMBOLS_ELEMENT:
                elemCount = 0
                for np in self.__nonPoly:
                    if np['comp_id'][0] == atomId:
                        elemCount += 1
                if elemCount > 0:
                    _, elemSeqId = getMetalCoordOf(self.__cR, seqId, compId, atomId)
                    if elemSeqId is not None:
                        seqId = _seqId = elemSeqId
                        compId = _compId = atomId
                        preferNonPoly = resolved = True
                    elif elemCount == 1:
                        for np in self.__nonPoly:
                            if np['comp_id'][0] == atomId:
                                seqId = _seqId = np['auth_seq_id'][0]
                                compId = _compId = atomId
                                preferNonPoly = resolved = True

            if not resolved and len(compId) > 1 and compId in SYMBOLS_ELEMENT:
                elemCount = 0
                for np in self.__nonPoly:
                    if np['comp_id'][0] == compId:
                        elemCount += 1
                if elemCount > 0:
                    _, elemSeqId = getMetalCoordOf(self.__cR, seqId, compId, compId)
                    if elemSeqId is not None:
                        seqId = _seqId = elemSeqId
                        atomId = _compId = compId
                        preferNonPoly = True
                    elif elemCount == 1:
                        for np in self.__nonPoly:
                            if np['comp_id'][0] == compId:
                                seqId = _seqId = np['auth_seq_id'][0]
                                atomId = _compId = compId
                                preferNonPoly = True

        if self.__splitLigand is not None and len(self.__splitLigand):
            found = False
            for (_, _seqId_, _compId_), ligList in self.__splitLigand.items():
                if _seqId_ != seqId or _compId_ != compId:
                    continue
                for idx, lig in enumerate(ligList):
                    _atomId = atomId
                    if self.__mrAtomNameMapping is not None and compId not in monDict3:
                        _, _, _atomId = retrieveAtomIdentFromMRMap(self.__ccU, self.__mrAtomNameMapping, seqId, compId, atomId)

                    if _atomId in lig['atom_ids']:
                        seqId = _seqId = lig['auth_seq_id']
                        compId = _compId = lig['comp_id']
                        atomId = _atomId
                        preferNonPoly = idx > 0
                        found = True
                        break
                if found:
                    break

        if self.__mrAtomNameMapping is not None and compId not in monDict3:
            seqId, compId, _ = retrieveAtomIdentFromMRMap(self.__ccU, self.__mrAtomNameMapping, seqId, compId, atomId)

        compId = self.translateToStdResNameWrapper(_seqId, _compId, preferNonPoly)

        if len(self.__modResidue) > 0:
            modRes = next((modRes for modRes in self.__modResidue
                           if modRes['auth_comp_id'] == compId
                           and (compId != _compId or seqId in (modRes['auth_seq_id'], modRes['seq_id']))), None)
            if modRes is not None:
                compId = modRes['comp_id']

        if self.__reasons is not None:
            if 'non_poly_remap' in self.__reasons and _compId in self.__reasons['non_poly_remap']\
               and seqId in self.__reasons['non_poly_remap'][_compId]:
                fixedChainId, fixedSeqId = retrieveRemappedNonPoly(self.__reasons['non_poly_remap'], None, refChainId, seqId, _compId)
                refChainId = fixedChainId
                preferNonPoly = True
            if 'branched_remap' in self.__reasons and seqId in self.__reasons['branched_remap']:
                fixedChainId, fixedSeqId = retrieveRemappedChainId(self.__reasons['branched_remap'], seqId)
                refChainId = fixedChainId
                preferNonPoly = True
            if not preferNonPoly:
                if 'chain_id_remap' in self.__reasons and seqId in self.__reasons['chain_id_remap']:
                    fixedChainId, fixedSeqId = retrieveRemappedChainId(self.__reasons['chain_id_remap'], seqId)
                    refChainId = fixedChainId
                elif 'chain_id_clone' in self.__reasons and seqId in self.__reasons['chain_id_clone']:
                    fixedChainId, fixedSeqId = retrieveRemappedChainId(self.__reasons['chain_id_clone'], seqId)
                    refChainId = fixedChainId
                elif 'seq_id_remap' in self.__reasons\
                        or 'chain_seq_id_remap' in self.__reasons\
                        or 'ext_chain_seq_id_remap' in self.__reasons:
                    if 'ext_chain_seq_id_remap' in self.__reasons:
                        fixedChainId, fixedSeqId, fixedCompId =\
                            retrieveRemappedSeqIdAndCompId(self.__reasons['ext_chain_seq_id_remap'], refChainId, seqId,
                                                           compId if compId in monDict3 else None)
                        self.__allow_ext_seq = fixedCompId is not None
                        if fixedSeqId is not None:
                            refChainId = fixedChainId
                    if fixedSeqId is None and 'chain_seq_id_remap' in self.__reasons:
                        fixedChainId, fixedSeqId = retrieveRemappedSeqId(self.__reasons['chain_seq_id_remap'], refChainId, seqId,
                                                                         compId if compId in monDict3 else None)
                        if fixedSeqId is not None:
                            refChainId = fixedChainId
                    if fixedSeqId is None and 'seq_id_remap' in self.__reasons:
                        _, fixedSeqId = retrieveRemappedSeqId(self.__reasons['seq_id_remap'], refChainId, seqId)
            if fixedSeqId is not None:
                _seqId = fixedSeqId

        updatePolySeqRst(self.__polySeqRst, self.__polySeq[0]['chain_id'] if refChainId is None else refChainId, _seqId, compId, _compId)

        types = self.__csStat.getTypeOfCompId(compId)
        if all(not t for t in types) or compId in ('MTS', 'ORI'):
            types = None
        elif compId != _compId:
            if types != self.__csStat.getTypeOfCompId(_compId):
                types = None

        def comp_id_unmatched_with(ps, cif_comp_id):
            if 'alt_comp_id' in ps and self.__csStat.peptideLike(cif_comp_id) and compId.startswith('D') and len(compId) >= 3\
               and self.__ccU.lastChemCompDict['_chem_comp.type'].upper() == 'D-PEPTIDE LINKING':
                revertPolySeqRst(self.__polySeqRst, ps['chain_id'] if fixedChainId is None else fixedChainId, _seqId, compId)

            if types is None or ('alt_comp_id' in ps and _compId in ps['alt_comp_id']):
                return False
            if compId not in monDict3 and cif_comp_id not in monDict3:
                return False
            return types != self.__csStat.getTypeOfCompId(cif_comp_id)

        def comp_id_in_polymer(np):
            return (_seqId == 1
                    and ((compId.endswith('-N') and all(c in np['comp_id'][0] for c in compId.split('-')[0]))
                         or (np['comp_id'][0] == 'PCA' and 'P' == compId[0] and ('GL' in compId or 'N' in compId))))\
                or (compId in monDict3
                    and any(compId in ps['comp_id'] for ps in self.__polySeq)
                    and compId not in np['comp_id'])

        if refChainId is not None or refChainId != _refChainId:
            if any(ps for ps in self.__polySeq if ps['auth_chain_id'] == _refChainId):
                fixedChainId = _refChainId
            elif self.__hasNonPolySeq:
                if any(np for np in self.__nonPolySeq if np['auth_chain_id'] == _refChainId):
                    fixedChainId = _refChainId

        for ps in self.__polySeq:
            if preferNonPoly:
                continue
            chainId, seqId, cifCompId = self.getRealChainSeqId(ps, _seqId, compId)
            if fixedChainId is None and refChainId is not None and refChainId != chainId and refChainId in self.__chainNumberDict:
                if chainId != self.__chainNumberDict[refChainId]:
                    continue
            if self.__reasons is not None:
                if fixedChainId is not None:
                    if fixedChainId != chainId:
                        continue
                    if fixedSeqId is not None:
                        seqId = fixedSeqId
                elif fixedSeqId is not None:
                    seqId = fixedSeqId
            if seqId <= 0 and self.__shiftNonPosSeq is not None and chainId in self.__shiftNonPosSeq:
                seqId -= 1
            if seqId in ps['auth_seq_id'] or fixedCompId is not None:
                if fixedCompId is not None:
                    cifCompId = origCompId = fixedCompId
                else:
                    if cifCompId is not None:
                        idx = next((_idx for _idx, (_seqId_, _cifCompId_) in enumerate(zip(ps['auth_seq_id'], ps['comp_id']))
                                    if _seqId_ == seqId and _cifCompId_ == cifCompId), ps['auth_seq_id'].index(seqId))
                    else:
                        idx = ps['auth_seq_id'].index(seqId) if seqId in ps['auth_seq_id'] else ps['seq_id'].index(seqId)
                    cifCompId = ps['comp_id'][idx]
                    origCompId = ps['auth_comp_id'][idx]
                    if comp_id_unmatched_with(ps, cifCompId):
                        continue
                if cifCompId != compId:
                    if (self.__shiftNonPosSeq is None or chainId not in self.__shiftNonPosSeq)\
                       and seqId <= 0 and seqId - 1 in ps['auth_seq_id']\
                       and compId == ps['comp_id'][ps['auth_seq_id'].index(seqId - 1)]:
                        seqId -= 1
                        if self.__shiftNonPosSeq is None:
                            self.__shiftNonPosSeq = {}
                        self.__shiftNonPosSeq[chainId] = True
                    compIds = [_compId for _seqId, _compId in zip(ps['auth_seq_id'], ps['comp_id']) if _seqId == seqId]
                    if compId in compIds:
                        cifCompId = compId
                        origCompId = next(origCompId for _seqId, _compId, origCompId in zip(ps['auth_seq_id'], ps['comp_id'], ps['auth_comp_id'])
                                          if _seqId == seqId and _compId == compId)
                if self.__mrAtomNameMapping is not None and origCompId not in monDict3:
                    _, coordAtomSite = self.getCoordAtomSiteOf(chainId, seqId, cifCompId, cifCheck=self.__hasCoord)
                    atomId = retrieveAtomIdFromMRMap(self.__ccU, self.__mrAtomNameMapping, seqId, origCompId, atomId, coordAtomSite)
                if compId in (cifCompId, origCompId, 'MTS', 'ORI'):
                    if len(self.__nefT.get_valid_star_atom(cifCompId, atomId)[0]) > 0:
                        chainAssign.add((chainId, seqId, cifCompId, True))
                        if refChainId is not None and refChainId != chainId and refChainId not in self.__chainNumberDict:
                            self.__chainNumberDict[refChainId] = chainId
                else:
                    _atomId, _, details = self.__nefT.get_valid_star_atom(cifCompId, atomId)
                    if len(_atomId) > 0 and (details is None or _compId not in monDict3):
                        chainAssign.add((chainId, seqId, cifCompId, True))
                        if refChainId is not None and refChainId != chainId and refChainId not in self.__chainNumberDict:
                            self.__chainNumberDict[refChainId] = chainId

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
                                if self.__mrAtomNameMapping is not None and origCompId not in monDict3:
                                    _, coordAtomSite = self.getCoordAtomSiteOf(chainId, seqId_, cifCompId, cifCheck=self.__hasCoord)
                                    atomId = retrieveAtomIdFromMRMap(self.__ccU, self.__mrAtomNameMapping, seqId, origCompId, atomId, coordAtomSite)
                                if compId in (cifCompId, origCompId, 'MTS', 'ORI'):
                                    if len(self.__nefT.get_valid_star_atom(cifCompId, atomId)[0]) > 0:
                                        chainAssign.add((chainId, seqId_, cifCompId, True))
                                        if refChainId is not None and refChainId != chainId and refChainId not in self.__chainNumberDict:
                                            self.__chainNumberDict[refChainId] = chainId
                                else:
                                    _atomId, _, details = self.__nefT.get_valid_star_atom(cifCompId, atomId)
                                    if len(_atomId) > 0 and (details is None or _compId not in monDict3):
                                        chainAssign.add((chainId, seqId_, cifCompId, True))
                                        if refChainId is not None and refChainId != chainId and refChainId not in self.__chainNumberDict:
                                            self.__chainNumberDict[refChainId] = chainId
                            except IndexError:
                                pass

        if self.__hasNonPolySeq:
            ligands = 0
            if self.__hasNonPoly:
                for np in self.__nonPoly:
                    ligands += np['comp_id'].count(_compId)
                if ligands == 0:
                    for np in self.__nonPoly:
                        ligands += np['comp_id'].count(compId)
                    if ligands == 1:
                        _compId = compId
                if ligands == 0:
                    for np in self.__nonPoly:
                        if 'alt_comp_id' in np:
                            ligands += np['alt_comp_id'].count(_compId)
                if ligands == 0:
                    for np in self.__nonPoly:
                        if 'alt_comp_id' in np:
                            ligands += np['alt_comp_id'].count(compId)
                    if ligands == 1:
                        _compId = compId
                if ligands == 0 and len(chainAssign) == 0:
                    __compId = None
                    for np in self.__nonPoly:
                        for ligand in np['comp_id']:
                            __compId = translateToLigandName(_compId, ligand, self.__ccU)
                            if __compId == ligand:
                                ligands += 1
                    if ligands == 1:
                        compId = _compId = __compId
                    elif len(self.__nonPoly) == 1 and self.__ccU.updateChemCompDict(_compId, False):
                        if self.__ccU.lastChemCompDict['_chem_comp.pdbx_release_status'] == 'OBS':
                            compId = _compId = self.__nonPoly[0]['comp_id'][0]
                            ligands = 1
                        elif _compId == 'ION':
                            if self.__nonPoly[0]['comp_id'][0] in SYMBOLS_ELEMENT:
                                compId = _compId = self.__nonPoly[0]['comp_id'][0]
                                ligands = 1
                if self.__reasons is None and self.__uniqAtomIdToSeqKey is not None and atomId in self.__uniqAtomIdToSeqKey:
                    seqKey = self.__uniqAtomIdToSeqKey[atomId]
                    if _seqId != seqKey[1]:
                        if 'non_poly_remap' not in self.reasonsForReParsing:
                            self.reasonsForReParsing['non_poly_remap'] = {}
                        if _compId not in self.reasonsForReParsing['non_poly_remap']:
                            self.reasonsForReParsing['non_poly_remap'][_compId] = {}
                        if _seqId not in self.reasonsForReParsing['non_poly_remap'][_compId]:
                            self.reasonsForReParsing['non_poly_remap'][_compId][_seqId] =\
                                {'chain_id': seqKey[0],
                                 'seq_id': seqKey[1],
                                 'original_chain_id': refChainId}
            for np in self.__nonPolySeq:
                chainId, seqId, cifCompId = self.getRealChainSeqId(np, _seqId, compId, False)
                if fixedChainId is None and refChainId is not None and refChainId != chainId and refChainId in self.__chainNumberDict:
                    if chainId != self.__chainNumberDict[refChainId]:
                        continue
                if self.__reasons is not None:
                    if fixedChainId is not None:
                        if fixedChainId != chainId:
                            continue
                        if fixedSeqId is not None:
                            seqId = fixedSeqId
                    elif fixedSeqId is not None:
                        seqId = fixedSeqId
                if comp_id_in_polymer(np):
                    continue
                if 'alt_auth_seq_id' in np and seqId not in np['auth_seq_id'] and seqId in np['alt_auth_seq_id']:
                    try:
                        seqId = next(_seqId_ for _seqId_, _altSeqId_ in zip(np['auth_seq_id'], np['alt_auth_seq_id']) if _altSeqId_ == seqId)
                    except StopIteration:
                        pass
                if seqId in np['auth_seq_id']\
                   or (ligands == 1 and (_compId in np['comp_id'] or ('alt_comp_id' in np and _compId in np['alt_comp_id']))):
                    if ligands == 1 and cifCompId is None:
                        cifCompId = _compId
                    idx = -1
                    try:
                        if cifCompId is not None:
                            idx = next(_idx for _idx, (_seqId_, _cifCompId_) in enumerate(zip(np['auth_seq_id'], np['comp_id']))
                                       if (_seqId_ == seqId or ligands == 1) and _cifCompId_ == cifCompId)
                            if ligands == 1:
                                seqId = np['auth_seq_id'][idx]
                    except StopIteration:
                        pass
                    if idx == -1:
                        idx = np['auth_seq_id'].index(seqId) if seqId in np['auth_seq_id']\
                            else np['seq_id'].index(seqId) if seqId in np['seq_id'] else 0
                    cifCompId = np['comp_id'][idx]
                    origCompId = np['auth_comp_id'][idx]
                    seqId = np['auth_seq_id'][idx]
                    if cifCompId in ('ZN', 'CA') and atomId[0] in protonBeginCode:  # 2loa
                        continue
                    if self.__mrAtomNameMapping is not None and origCompId not in monDict3:
                        _, coordAtomSite = self.getCoordAtomSiteOf(chainId, seqId, cifCompId, cifCheck=self.__hasCoord)
                        atomId = retrieveAtomIdFromMRMap(self.__ccU, self.__mrAtomNameMapping, _seqId, origCompId, atomId, coordAtomSite)
                    if compId in (cifCompId, origCompId, 'MTS', 'ORI'):
                        if len(self.__nefT.get_valid_star_atom(cifCompId, atomId)[0]) > 0:
                            if (ligands == 1 or cifCompId in HEME_LIKE_RES_NAMES) and any(a[3] for a in chainAssign):
                                chainAssign.clear()
                            chainAssign.add((chainId, seqId, cifCompId, False))
                            if refChainId is not None and refChainId != chainId and refChainId not in self.__chainNumberDict:
                                self.__chainNumberDict[refChainId] = chainId
                    else:
                        _atomId, _, details = self.__nefT.get_valid_star_atom(cifCompId, atomId)
                        if len(_atomId) > 0 and (details is None or _compId not in monDict3):
                            if (ligands == 1 or cifCompId in HEME_LIKE_RES_NAMES) and any(a[3] for a in chainAssign):
                                chainAssign.clear()
                            chainAssign.add((chainId, seqId, cifCompId, False))
                            if refChainId is not None and refChainId != chainId and refChainId not in self.__chainNumberDict:
                                self.__chainNumberDict[refChainId] = chainId

        if len(chainAssign) == 0:
            for ps in self.__polySeq:
                if preferNonPoly:
                    continue
                chainId = ps['chain_id']
                if refChainId is not None and refChainId != chainId and refChainId in self.__chainNumberDict:
                    if chainId != self.__chainNumberDict[refChainId]:
                        continue
                if fixedChainId is not None and fixedChainId != chainId:
                    continue
                seqKey = (chainId, _seqId)
                if seqKey in self.__authToLabelSeq:
                    _, seqId = self.__authToLabelSeq[seqKey]
                    if seqId in ps['seq_id']:
                        idx = ps['seq_id'].index(seqId)
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
                        if self.__mrAtomNameMapping is not None and origCompId not in monDict3:
                            _, coordAtomSite = self.getCoordAtomSiteOf(chainId, _seqId, cifCompId, cifCheck=self.__hasCoord)
                            atomId = retrieveAtomIdFromMRMap(self.__ccU, self.__mrAtomNameMapping, seqId, origCompId, atomId, coordAtomSite)
                        if compId in (cifCompId, origCompId, 'MTS', 'ORI'):
                            if len(self.__nefT.get_valid_star_atom(cifCompId, atomId)[0]) > 0:
                                chainAssign.add((ps['auth_chain_id'], _seqId, cifCompId, True))
                                if refChainId is not None and refChainId != chainId and refChainId not in self.__chainNumberDict:
                                    self.__chainNumberDict[refChainId] = chainId
                        else:
                            _atomId, _, details = self.__nefT.get_valid_star_atom(cifCompId, atomId)
                            if len(_atomId) > 0 and (details is None or _compId not in monDict3):
                                chainAssign.add((ps['auth_chain_id'], _seqId, cifCompId, True))
                                if refChainId is not None and refChainId != chainId and refChainId not in self.__chainNumberDict:
                                    self.__chainNumberDict[refChainId] = chainId

            if self.__hasNonPolySeq:
                for np in self.__nonPolySeq:
                    chainId = np['auth_chain_id']
                    if refChainId is not None and refChainId != chainId and refChainId in self.__chainNumberDict:
                        if chainId != self.__chainNumberDict[refChainId]:
                            continue
                    if fixedChainId is not None and fixedChainId != chainId:
                        continue
                    if comp_id_in_polymer(np):
                        continue
                    seqKey = (chainId, _seqId)
                    if seqKey in self.__authToLabelSeq:
                        _, seqId = self.__authToLabelSeq[seqKey]
                        if seqId in np['seq_id']:
                            idx = np['seq_id'].index(seqId)
                            cifCompId = np['comp_id'][idx]
                            origCompId = np['auth_comp_id'][idx]
                            if self.__mrAtomNameMapping is not None and origCompId not in monDict3:
                                _, coordAtomSite = self.getCoordAtomSiteOf(chainId, _seqId, cifCompId, cifCheck=self.__hasCoord)
                                atomId = retrieveAtomIdFromMRMap(self.__ccU, self.__mrAtomNameMapping, seqId, origCompId, atomId, coordAtomSite)
                            if compId in (cifCompId, origCompId, 'MTS', 'ORI'):
                                if len(self.__nefT.get_valid_star_atom(cifCompId, atomId)[0]) > 0:
                                    chainAssign.add((np['auth_chain_id'], _seqId, cifCompId, False))
                                    if refChainId is not None and refChainId != chainId and refChainId not in self.__chainNumberDict:
                                        self.__chainNumberDict[refChainId] = chainId
                            else:
                                _atomId, _, details = self.__nefT.get_valid_star_atom(cifCompId, atomId)
                                if len(_atomId) > 0 and (details is None or _compId not in monDict3):
                                    chainAssign.add((np['auth_chain_id'], _seqId, cifCompId, False))
                                    if refChainId is not None and refChainId != chainId and refChainId not in self.__chainNumberDict:
                                        self.__chainNumberDict[refChainId] = chainId

        if len(chainAssign) == 0 and self.__altPolySeq is not None:
            for ps in self.__altPolySeq:
                if preferNonPoly:
                    continue
                chainId = ps['auth_chain_id']
                if refChainId is not None and refChainId != chainId and refChainId in self.__chainNumberDict:
                    if chainId != self.__chainNumberDict[refChainId]:
                        continue
                if fixedChainId is not None and fixedChainId != chainId:
                    continue
                if _seqId in ps['auth_seq_id']:
                    cifCompId = ps['comp_id'][ps['auth_seq_id'].index(_seqId)]
                    if comp_id_unmatched_with(ps, cifCompId):
                        continue
                    if cifCompId != compId:
                        if cifCompId in monDict3 and compId in monDict3:
                            continue
                        compIds = [_compId for _seqId, _compId in zip(ps['auth_seq_id'], ps['comp_id']) if _seqId == seqId]
                        if compId in compIds:
                            cifCompId = compId
                    chainAssign.add((chainId, _seqId, cifCompId, True))
                    if refChainId is not None and refChainId != chainId and refChainId not in self.__chainNumberDict:
                        self.__chainNumberDict[refChainId] = chainId

        if len(chainAssign) == 0 and (self.__preferAuthSeqCount - self.__preferLabelSeqCount < MAX_PREF_LABEL_SCHEME_COUNT or len(self.__polySeq) > 1):
            for ps in self.__polySeq:
                if preferNonPoly:
                    continue
                chainId = ps['chain_id']
                if refChainId is not None and refChainId != chainId and refChainId in self.__chainNumberDict:
                    if chainId != self.__chainNumberDict[refChainId]:
                        continue
                if fixedChainId is not None and fixedChainId != chainId:
                    continue
                seqKey = (chainId, _seqId)
                if seqKey in self.__labelToAuthSeq:
                    _, seqId = self.__labelToAuthSeq[seqKey]
                    if seqId in ps['auth_seq_id']:
                        idx = ps['seq_id'].index(_seqId)
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
                        if self.__mrAtomNameMapping is not None and origCompId not in monDict3:
                            _, coordAtomSite = self.getCoordAtomSiteOf(chainId, seqId, cifCompId, cifCheck=self.__hasCoord)
                            atomId = retrieveAtomIdFromMRMap(self.__ccU, self.__mrAtomNameMapping, seqId, origCompId, atomId, coordAtomSite)
                        if compId in (cifCompId, origCompId, 'MTS', 'ORI'):
                            if len(self.__nefT.get_valid_star_atom(cifCompId, atomId)[0]) > 0:
                                chainAssign.add((ps['auth_chain_id'], seqId, cifCompId, True))
                                if compId in (cifCompId, origCompId):
                                    self.__authSeqId = 'label_seq_id'
                                    self.__setLocalSeqScheme()
                                    if refChainId is not None and refChainId != chainId and refChainId not in self.__chainNumberDict:
                                        self.__chainNumberDict[refChainId] = chainId
                        else:
                            _atomId, _, details = self.__nefT.get_valid_star_atom(cifCompId, atomId)
                            if len(_atomId) > 0 and (details is None or _compId not in monDict3):
                                chainAssign.add((ps['auth_chain_id'], seqId, cifCompId, True))
                                self.__authSeqId = 'label_seq_id'
                                self.__setLocalSeqScheme()
                                if refChainId is not None and refChainId != chainId and refChainId not in self.__chainNumberDict:
                                    self.__chainNumberDict[refChainId] = chainId

        if len(chainAssign) == 0:
            if seqId == 1 or (refChainId, seqId - 1) in self.__coordUnobsRes:
                if atomId in aminoProtonCode and atomId != 'H1':
                    return self.assignCoordPolymerSequence(refChainId, seqId, compId, 'H1')
            auth_seq_id_list = list(filter(None, self.__polySeq[0]['auth_seq_id']))
            min_auth_seq_id = max_auth_seq_id = UNREAL_AUTH_SEQ_NUM
            if len(auth_seq_id_list) > 0:
                min_auth_seq_id = min(auth_seq_id_list)
                max_auth_seq_id = max(auth_seq_id_list)
            if len(self.__polySeq) == 1\
               and (seqId < 1
                    or (compId == 'ACE' and seqId == min_auth_seq_id - 1)
                    or (compId == 'NH2' and seqId == max_auth_seq_id + 1)
                    or (compId in monDict3 and self.__preferAuthSeqCount - self.__preferLabelSeqCount >= MAX_PREF_LABEL_SCHEME_COUNT)):
                refChainId = self.__polySeq[0]['auth_chain_id']
                if (compId == 'ACE' and seqId == min_auth_seq_id - 1)\
                   or (compId == 'NH2' and seqId == max_auth_seq_id + 1)\
                   or (compId in monDict3 and self.__preferAuthSeqCount - self.__preferLabelSeqCount >= MAX_PREF_LABEL_SCHEME_COUNT
                       and (min_auth_seq_id - MAX_ALLOWED_EXT_SEQ <= seqId < min_auth_seq_id
                            or max_auth_seq_id < seqId <= max_auth_seq_id + MAX_ALLOWED_EXT_SEQ)):
                    self.__f.append(f"[Sequence mismatch warning] {self.__getCurrentRestraint()}"
                                    f"The residue '{_seqId}:{_compId}' is not present in polymer sequence "
                                    f"of chain {refChainId} of the coordinates. "
                                    "Please update the sequence in the Macromolecules page.")
                    resKey = (_seqId, _compId)
                    if resKey not in self.__extResKey:
                        self.__extResKey.append(resKey)
                    chainAssign.add((refChainId, _seqId, compId, True))
                    asis = True
                elif compId in monDict3 and self.__preferAuthSeqCount - self.__preferLabelSeqCount >= MAX_PREF_LABEL_SCHEME_COUNT:
                    self.__f.append(f"[Sequence mismatch warning] {self.__getCurrentRestraint()}"
                                    f"The residue '{_seqId}:{_compId}' is not present in polymer sequence "
                                    f"of chain {refChainId} of the coordinates. "
                                    "Please update the sequence in the Macromolecules page.")
                    resKey = (_seqId, _compId)
                    if resKey not in self.__extResKey:
                        self.__extResKey.append(resKey)
                else:
                    self.__f.append(f"[Atom not found] {self.__getCurrentRestraint()}"
                                    f"{_seqId}:{_compId}:{atomId} is not present in the coordinates. "
                                    f"The residue number '{_seqId}' is not present in polymer sequence "
                                    f"of chain {refChainId} of the coordinates. "
                                    "Please update the sequence in the Macromolecules page.")
            else:
                ext_seq = False
                if (compId in monDict3 or compId in ('ACE', 'NH2')) and (self.__preferAuthSeqCount - self.__preferLabelSeqCount >= MAX_PREF_LABEL_SCHEME_COUNT
                                                                         or len(atomId) == 1):
                    refChainIds = []
                    _auth_seq_id_list = auth_seq_id_list
                    for idx, ps in enumerate(self.__polySeq):
                        if idx > 0:
                            auth_seq_id_list = list(filter(None, ps['auth_seq_id']))
                            _auth_seq_id_list.extend(auth_seq_id_list)
                        if len(auth_seq_id_list) > 0:
                            if idx > 0:
                                min_auth_seq_id = min(auth_seq_id_list)
                                max_auth_seq_id = max(auth_seq_id_list)
                            if min_auth_seq_id - MAX_ALLOWED_EXT_SEQ <= seqId < min_auth_seq_id\
                               and (compId in monDict3 or (compId == 'ACE' and seqId == min_auth_seq_id - 1)):
                                refChainIds.append(ps['auth_chain_id'])
                                ext_seq = True
                            elif max_auth_seq_id < seqId <= max_auth_seq_id + MAX_ALLOWED_EXT_SEQ\
                                    and (compId in monDict3 or (compId == 'NH2' and seqId == max_auth_seq_id + 1)):
                                refChainIds.append(ps['auth_chain_id'])
                                ext_seq = True
                            elif self.__reasons is None and compId in monDict3 and atomId == 'H' and seqId < min_auth_seq_id\
                                    and self.__preferAuthSeqCount - self.__preferLabelSeqCount < MAX_PREF_LABEL_SCHEME_COUNT:
                                refChainIds.append(ps['auth_chain_id'])
                                ext_seq = True
                    if ext_seq and seqId in _auth_seq_id_list:
                        ext_seq = False
                if ext_seq:
                    refChainId = refChainIds[0] if len(refChainIds) == 1 else refChainIds
                    self.__f.append(f"[Sequence mismatch warning] {self.__getCurrentRestraint()}"
                                    f"The residue '{_seqId}:{_compId}' is not present in polymer sequence "
                                    f"of chain {refChainId} of the coordinates. "
                                    "Please update the sequence in the Macromolecules page.")
                    resKey = (_seqId, _compId)
                    if resKey not in self.__extResKey:
                        self.__extResKey.append(resKey)
                    if isinstance(refChainId, str):
                        chainAssign.add((refChainId, _seqId, compId, True))
                    else:
                        for _refChainId in refChainIds:
                            chainAssign.add((_refChainId, _seqId, compId, True))
                    asis = True
                else:
                    self.__f.append(f"[Atom not found] {self.__getCurrentRestraint(n=index, g=group)}"
                                    f"{_seqId}:{_compId}:{atomId} is not present in the coordinates.")
                updatePolySeqRst(self.__polySeqRstFailed, self.__polySeq[0]['chain_id'] if refChainId is None else refChainId, _seqId, compId, _compId)

        elif any(ca for ca in chainAssign if ca[0] == refChainId) and any(ca for ca in chainAssign if ca[0] != refChainId):
            _chainAssign = copy.copy(chainAssign)
            for _ca in _chainAssign:
                if _ca[0] != refChainId:
                    chainAssign.remove(_ca)

        return list(chainAssign), asis

    def selectCoordAtoms(self, chainAssign: List[Tuple[str, int, str, bool]], seqId: int, compId: str, atomId: str,
                         allowAmbig: bool = True, index: Optional[int] = None, group: Optional[int] = None, offset: int = 0):
        """ Select atoms of the coordinates.
        """

        atomSelection = []

        authAtomId = atomId

        __compId = compId
        __atomId = atomId

        if self.__mrAtomNameMapping is not None and compId not in monDict3:
            __atomId = retrieveAtomIdFromMRMap(self.__ccU, self.__mrAtomNameMapping, seqId, compId, atomId)

        compId = self.translateToStdResNameWrapper(seqId, __compId)

        for chainId, cifSeqId, cifCompId, isPolySeq in chainAssign:

            if offset != 0:
                cifSeqId += offset
                cifCompId = compId

            seqKey, coordAtomSite = self.getCoordAtomSiteOf(chainId, cifSeqId, cifCompId, asis=self.__preferAuthSeq)

            if self.__cur_subtype == 'dist' and __compId is not None\
               and (__compId.startswith('MTS') or __compId.startswith('ORI')) and cifCompId != __compId:
                if __atomId[0] in ('O', 'N'):

                    if cifCompId == 'CYS':
                        atomId = 'SG'
                    elif cifCompId == 'SER':
                        atomId = 'OG'
                    elif cifCompId == 'GLU':
                        atomId = 'OE2'
                    elif cifCompId == 'ASP':
                        atomId = 'OD2'
                    elif cifCompId == 'GLN':
                        atomId = 'NE2'
                    elif cifCompId == 'ASN':
                        atomId = 'ND2'
                    elif cifCompId == 'LYS':
                        atomId = 'NZ'
                    elif cifCompId == 'THR':
                        atomId = 'OG1'
                    elif compId == 'HIS':
                        atomId = 'NE2'
                    elif compId == 'R1A':
                        atomId = 'O1'

                elif self.__csStat.peptideLike(cifCompId):
                    atomId = 'CA'

            if self.__mrAtomNameMapping is not None and cifCompId not in monDict3:
                __atomId = retrieveAtomIdFromMRMap(self.__ccU, self.__mrAtomNameMapping, cifSeqId, cifCompId, atomId, coordAtomSite)
                if atomId != __atomId and coordAtomSite is not None\
                   and (__atomId in coordAtomSite['atom_id'] or (__atomId.endswith('%') and __atomId[:-1] + '2' in coordAtomSite['atom_id'])):
                    atomId = __atomId
                elif self.__reasons is not None and 'branched_remap' in self.__reasons:
                    _seqId = retrieveOriginalSeqIdFromMRMap(self.__reasons['branched_remap'], chainId, cifSeqId)
                    if _seqId != cifSeqId:
                        _, _, atomId = retrieveAtomIdentFromMRMap(self.__ccU, self.__mrAtomNameMapping, _seqId, cifCompId, atomId, None, coordAtomSite)

            _atomId = []
            if not isPolySeq and atomId[0] in ('Q', 'M') and coordAtomSite is not None:
                key = (chainId, cifSeqId, compId, atomId)
                if key in self.__cachedDictForStarAtom:
                    _atomId = copy.deepcopy(self.__cachedDictForStarAtom[key])
                else:
                    pattern = re.compile(fr'H{atomId[1:]}\d+') if compId in monDict3 else re.compile(fr'H{atomId[1:]}\S?$')
                    atomIdList = [a for a in coordAtomSite['atom_id'] if re.search(pattern, a) and a[-1] in ('1', '2', '3')]
                    if len(atomIdList) > 1:
                        hvyAtomIdList = [a for a in coordAtomSite['atom_id'] if a[0] in ('C', 'N')]
                        hvyAtomId = None
                        for canHvyAtomId in hvyAtomIdList:
                            if isStructConn(self.__cR, chainId, cifSeqId, canHvyAtomId, chainId, cifSeqId, atomIdList[0],
                                            representativeModelId=self.__representativeModelId, representativeAltId=self.__representativeAltId,
                                            modelNumName=self.__modelNumName):
                                hvyAtomId = canHvyAtomId
                                break
                        if hvyAtomId is not None:
                            for _atomId_ in atomIdList:
                                if isStructConn(self.__cR, chainId, cifSeqId, hvyAtomId, chainId, cifSeqId, _atomId_,
                                                representativeModelId=self.__representativeModelId, representativeAltId=self.__representativeAltId,
                                                modelNumName=self.__modelNumName):
                                    _atomId.append(_atomId_)
                    if len(_atomId) > 1:
                        self.__cachedDictForStarAtom[key] = copy.deepcopy(_atomId)
            if len(_atomId) > 1:
                details = None
            else:
                _atomId, _, details = self.__nefT.get_valid_star_atom_in_xplor(cifCompId, atomId, leave_unmatched=True)
                if details is not None:
                    if atomId != __atomId:
                        _atomId, _, details = self.__nefT.get_valid_star_atom_in_xplor(cifCompId, __atomId, leave_unmatched=True)
                    elif len(atomId) > 1 and not atomId[-1].isalpha() and (atomId[0] in pseProBeginCode or atomId[0] in ('C', 'N', 'P', 'F')):
                        _atomId, _, details = self.__nefT.get_valid_star_atom_in_xplor(cifCompId, atomId[:-1], leave_unmatched=True)
                        if atomId[-1].isdigit() and int(atomId[-1]) <= len(_atomId):
                            _atomId = [_atomId[int(atomId[-1]) - 1]]

            if details is not None or atomId.endswith('"'):
                _atomId_ = translateToStdAtomName(atomId, cifCompId, ccU=self.__ccU, unambig=self.__cur_subtype != 'dist')
                if _atomId_ != atomId:
                    if atomId.startswith('HT') and len(_atomId_) == 2:
                        _atomId_ = 'H'
                    __atomId__ = self.__nefT.get_valid_star_atom_in_xplor(cifCompId, _atomId_)[0]
                    if coordAtomSite is not None:
                        if any(_atomId_ for _atomId_ in __atomId__ if _atomId_ in coordAtomSite['atom_id']):
                            _atomId = __atomId__
                        elif __atomId__[0][0] in protonBeginCode:
                            __bondedTo = self.__ccU.getBondedAtoms(cifCompId, __atomId__[0])
                            if len(__bondedTo) > 0 and __bondedTo[0] in coordAtomSite['atom_id']:
                                _atomId = __atomId__
                elif coordAtomSite is not None:
                    _atomId = []
            # _atomId = self.__nefT.get_valid_star_atom(cifCompId, atomId)[0]

            if coordAtomSite is not None\
               and not any(_atomId_ for _atomId_ in _atomId if _atomId_ in coordAtomSite['atom_id']):
                if atomId in coordAtomSite['atom_id']:
                    _atomId = [atomId]
                elif seqId == 1 and atomId == 'H1' and self.__csStat.peptideLike(compId) and 'H' in coordAtomSite['atom_id']:
                    _atomId = ['H']

            if coordAtomSite is None and not isPolySeq and self.__hasNonPolySeq:
                try:
                    for np in self.__nonPolySeq:
                        if np['auth_chain_id'] == chainId and cifSeqId in np['auth_seq_id']:
                            cifSeqId = np['seq_id'][np['auth_seq_id'].index(cifSeqId)]
                            seqKey, coordAtomSite = self.getCoordAtomSiteOf(chainId, cifSeqId, cifCompId)
                            if coordAtomSite is not None:
                                break
                except ValueError:
                    pass

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
            if self.__reasons is not None and compId != cifCompId and __compId == cifCompId:
                compId = cifCompId
            if compId != cifCompId and compId in monDict3 and cifCompId in monDict3:
                multiChain = insCode = False
                if len(chainAssign) > 0:
                    chainIds = [ca[0] for ca in chainAssign]
                    multiChain = len(collections.Counter(chainIds).most_common()) > 1
                ps = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == chainId), None)
                if ps is not None:
                    compIds = [_compId for _seqId, _compId in zip(ps['auth_seq_id'], ps['comp_id']) if _seqId == cifSeqId]
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
                    self.__f.append(f"[Sequence mismatch] {self.__getCurrentRestraint()}"
                                    f"Residue name {__compId!r} of the restraint does not match with {chainId}:{cifSeqId}:{cifCompId} of the coordinates.")
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
                    self.selectCoordAtoms(chainAssign, seqId, compId, atomId, allowAmbig, index, group, offset=1)
                    return
                self.__f.append(f"[Invalid atom nomenclature] {self.__getCurrentRestraint(n=index, g=group)}"
                                f"{seqId}:{__compId}:{__atomId} is invalid atom nomenclature.")
                continue
            if lenAtomId > 1 and not allowAmbig:
                self.__f.append(f"[Invalid atom selection] {self.__getCurrentRestraint(n=index, g=group)}"
                                f"Ambiguous atom selection '{seqId}:{__compId}:{__atomId}' is not allowed as a angle restraint.")
                continue

            if __compId != cifCompId and __compId not in self.__compIdMap:
                self.__compIdMap[__compId] = cifCompId

            for cifAtomId in _atomId:

                if seqKey in self.__coordUnobsRes and cifCompId in monDict3 and self.__reasons is not None and 'non_poly_remap' in self.__reasons:
                    if self.__ccU.updateChemCompDict(cifCompId):
                        try:
                            next(cca for cca in self.__ccU.lastAtomList
                                 if cca[self.__ccU.ccaAtomId] == cifAtomId and cca[self.__ccU.ccaLeavingAtomFlag] != 'Y')
                        except StopIteration:
                            continue
                        try:
                            if len(authAtomId) > len(cifAtomId):
                                next(cca for cca in self.__ccU.lastAtomList
                                     if cca[self.__ccU.ccaAtomId] == authAtomId and cca[self.__ccU.ccaLeavingAtomFlag] != 'Y')
                        except StopIteration:
                            break

                if authAtomId in ('H', 'HN') and cifAtomId in ('HN1', 'HN2', 'HNA') and self.__csStat.peptideLike(cifCompId)\
                   and coordAtomSite is not None and cifAtomId not in coordAtomSite['atom_id']:
                    if cifAtomId in ('HN2', 'HNA'):
                        if 'H2' not in coordAtomSite['atom_id']:
                            continue
                        cifAtomId = 'H2'
                    if cifAtomId == 'HN1' and 'H' in coordAtomSite['atom_id']:
                        cifAtomId = 'H'

                atomSelection.append({'chain_id': chainId, 'seq_id': cifSeqId, 'comp_id': cifCompId,
                                      'atom_id': cifAtomId, 'auth_atom_id': authAtomId})

                self.testCoordAtomIdConsistency(chainId, cifSeqId, cifCompId, cifAtomId, seqKey, coordAtomSite, index, group)

        if len(atomSelection) > 0:
            self.atomSelectionSet.append(atomSelection)

    def selectAuxCoordAtoms(self, chainAssign: List[Tuple[str, int, str, bool]], seqId: int, compId: str, atomId: str,
                            allowAmbig: bool = True, index: Optional[int] = None, group: Optional[int] = None):
        """ Select auxiliary atoms of the coordinates.
        """

        atomSelection = []

        for chainId, cifSeqId, cifCompId, isPolySeq in chainAssign:
            seqKey, coordAtomSite = self.getCoordAtomSiteOf(chainId, cifSeqId, cifCompId)

            _atomId, _, details = self.__nefT.get_valid_star_atom_in_xplor(cifCompId, atomId, leave_unmatched=True)
            if details is not None and len(atomId) > 1 and not atomId[-1].isalpha():
                _atomId, _, details = self.__nefT.get_valid_star_atom_in_xplor(cifCompId, atomId[:-1], leave_unmatched=True)
                if atomId[-1].isdigit() and int(atomId[-1]) <= len(_atomId):
                    _atomId = [_atomId[int(atomId[-1]) - 1]]

            if details is not None or atomId.endswith('"'):
                _atomId_ = translateToStdAtomName(atomId, cifCompId, ccU=self.__ccU, unambig=False)
                if _atomId_ != atomId:
                    if atomId.startswith('HT') and len(_atomId_) == 2:
                        _atomId_ = 'H'
                    __atomId = self.__nefT.get_valid_star_atom_in_xplor(cifCompId, _atomId_)[0]
                    if coordAtomSite is not None:
                        if any(_atomId_ for _atomId_ in __atomId if _atomId_ in coordAtomSite['atom_id']):
                            _atomId = __atomId
                        elif __atomId[0][0] in protonBeginCode:
                            __bondedTo = self.__ccU.getBondedAtoms(cifCompId, __atomId[0])
                            if len(__bondedTo) > 0 and __bondedTo[0] in coordAtomSite['atom_id']:
                                _atomId = __atomId
                elif coordAtomSite is not None:
                    _atomId = []
            # _atomId = self.__nefT.get_valid_star_atom(cifCompId, atomId)[0]

            if coordAtomSite is not None\
               and not any(_atomId_ for _atomId_ in _atomId if _atomId_ in coordAtomSite['atom_id'])\
               and atomId in coordAtomSite['atom_id']:
                _atomId = [atomId]

            if coordAtomSite is None and not isPolySeq:
                try:
                    for np in self.__nonPoly:
                        if np['auth_chain_id'] == chainId and cifSeqId in np['auth_seq_id']:
                            cifSeqId = np['seq_id'][np['auth_seq_id'].index(cifSeqId)]
                            seqKey, coordAtomSite = self.getCoordAtomSiteOf(chainId, cifSeqId, cifCompId)
                            if coordAtomSite is not None:
                                break
                except ValueError:
                    pass

            lenAtomId = len(_atomId)
            if lenAtomId == 0:
                self.__f.append(f"[Invalid atom nomenclature] {self.__getCurrentRestraint(n=index, g=group)}"
                                f"{seqId}:{compId}:{atomId} is invalid atom nomenclature.")
                continue
            if lenAtomId > 1 and not allowAmbig:
                self.__f.append(f"[Invalid atom selection] {self.__getCurrentRestraint(n=index, g=group)}"
                                f"Ambiguous atom selection '{seqId}:{compId}:{atomId}' is not allowed as a angle restraint.")
                continue

            for cifAtomId in _atomId:
                atomSelection.append({'chain_id': chainId, 'seq_id': cifSeqId, 'comp_id': cifCompId, 'atom_id': cifAtomId})

                _cifAtomId, asis = self.testCoordAtomIdConsistency(chainId, cifSeqId, cifCompId, cifAtomId, seqKey, coordAtomSite, index, group)
                if asis:
                    atomSelection[-1]['asis'] = True
                if cifAtomId != _cifAtomId:
                    atomSelection[-1]['atom_id'] = _cifAtomId
                    if _cifAtomId.startswith('Ignorable'):
                        atomSelection.pop()

        if len(atomSelection) > 0:
            self.auxAtomSelectionSet.append(atomSelection)

    def testCoordAtomIdConsistency(self, chainId: str, seqId: int, compId: str, atomId: str,
                                   seqKey: Tuple[str, int], coordAtomSite: Optional[dict],
                                   index: Optional[int] = None, group: Optional[int] = None) -> Tuple[str, bool]:
        asis = False
        if not self.__hasCoord:
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
                        seqKey = _seqKey
                        self.__setLocalSeqScheme()
                    elif atomId in ('HN1', 'HN2', 'HN3') and ((atomId[-1] + 'HN') in _coordAtomSite['atom_id']
                                                              or ('H' + atomId[-1]) in _coordAtomSite['atom_id']):
                        atomId = atomId[-1] + 'HN' if atomId[-1] + 'HN' in _coordAtomSite['atom_id'] else 'H' + atomId[-1]
                        found = True
                        self.__preferAuthSeq = False
                        self.__authSeqId = 'label_seq_id'
                        seqKey = _seqKey
                        self.__setLocalSeqScheme()
                    elif 'alt_atom_id' in _coordAtomSite and atomId in _coordAtomSite['alt_atom_id']:
                        found = True
                        self.__preferAuthSeq = False
                        self.__authSeqId = 'label_seq_id'
                        # self.__authAtomId = 'auth_atom_id'
                        seqKey = _seqKey
                        self.__setLocalSeqScheme()

            else:
                self.__preferAuthSeq = True
                _seqKey, _coordAtomSite = self.getCoordAtomSiteOf(chainId, seqId, compId)
                if _coordAtomSite is not None and _coordAtomSite['comp_id'] == compId:
                    if atomId in _coordAtomSite['atom_id']:
                        found = True
                        self.__authSeqId = 'auth_seq_id'
                        seqKey = _seqKey
                        self.__setLocalSeqScheme()
                    elif atomId in ('HN1', 'HN2', 'HN3') and ((atomId[-1] + 'HN') in _coordAtomSite['atom_id']
                                                              or ('H' + atomId[-1]) in _coordAtomSite['atom_id']):
                        atomId = atomId[-1] + 'HN' if atomId[-1] + 'HN' in _coordAtomSite['atom_id'] else 'H' + atomId[-1]
                        found = True
                        self.__authSeqId = 'auth_seq_id'
                        seqKey = _seqKey
                        self.__setLocalSeqScheme()
                    elif 'alt_atom_id' in _coordAtomSite and atomId in _coordAtomSite['alt_atom_id']:
                        found = True
                        self.__authSeqId = 'auth_seq_id'
                        # self.__authAtomId = 'auth_atom_id'
                        seqKey = _seqKey
                        self.__setLocalSeqScheme()
                    elif not self.__extendAuthSeq:
                        self.__preferAuthSeq = False
                elif not self.__extendAuthSeq:
                    self.__preferAuthSeq = False

        elif self.__preferAuthSeq and seqKey not in self.__coordUnobsRes:
            _seqKey, _coordAtomSite = self.getCoordAtomSiteOf(chainId, seqId, compId, asis=False)
            if _coordAtomSite is not None and _coordAtomSite['comp_id'] == compId and not self.__extendAuthSeq:
                if atomId in _coordAtomSite['atom_id']:
                    found = True
                    self.__preferAuthSeq = False
                    self.__authSeqId = 'label_seq_id'
                    seqKey = _seqKey
                    self.__setLocalSeqScheme()
                elif atomId in ('HN1', 'HN2', 'HN3') and ((atomId[-1] + 'HN') in _coordAtomSite['atom_id']
                                                          or ('H' + atomId[-1]) in _coordAtomSite['atom_id']):
                    atomId = atomId[-1] + 'HN' if atomId[-1] + 'HN' in _coordAtomSite['atom_id'] else 'H' + atomId[-1]
                    found = True
                    self.__preferAuthSeq = False
                    self.__authSeqId = 'label_seq_id'
                    seqKey = _seqKey
                    self.__setLocalSeqScheme()
                elif 'alt_atom_id' in _coordAtomSite and atomId in _coordAtomSite['alt_atom_id']:
                    found = True
                    self.__preferAuthSeq = False
                    self.__authSeqId = 'label_seq_id'
                    # self.__authAtomId = 'auth_atom_id'
                    seqKey = _seqKey
                    self.__setLocalSeqScheme()

        elif not self.__preferAuthSeq:
            self.__preferAuthSeq = True
            _seqKey, _coordAtomSite = self.getCoordAtomSiteOf(chainId, seqId, compId)
            if _coordAtomSite is not None and _coordAtomSite['comp_id'] == compId:
                if atomId in _coordAtomSite['atom_id']:
                    found = True
                    self.__authSeqId = 'auth_seq_id'
                    seqKey = _seqKey
                    self.__setLocalSeqScheme()
                elif atomId in ('HN1', 'HN2', 'HN3') and ((atomId[-1] + 'HN') in _coordAtomSite['atom_id']
                                                          or ('H' + atomId[-1]) in _coordAtomSite['atom_id']):
                    atomId = atomId[-1] + 'HN' if atomId[-1] + 'HN' in _coordAtomSite['atom_id'] else 'H' + atomId[-1]
                    found = True
                    self.__authSeqId = 'auth_seq_id'
                    seqKey = _seqKey
                    self.__setLocalSeqScheme()
                elif 'alt_atom_id' in _coordAtomSite and atomId in _coordAtomSite['alt_atom_id']:
                    found = True
                    self.__authSeqId = 'auth_seq_id'
                    # self.__authAtomId = 'auth_atom_id'
                    seqKey = _seqKey
                    self.__setLocalSeqScheme()
                elif not self.__extendAuthSeq:
                    self.__preferAuthSeq = False
            elif not self.__extendAuthSeq:
                self.__preferAuthSeq = False

        if found:
            if self.__preferAuthSeq:
                self.__preferAuthSeqCount += 1
            return atomId, asis

        if chainId in self.__chainNumberDict.values():

            if self.__preferAuthSeq and seqKey not in self.__coordUnobsRes:
                _seqKey, _coordAtomSite = self.getCoordAtomSiteOf(chainId, seqId, compId, asis=False)
                if _coordAtomSite is not None and _coordAtomSite['comp_id'] == compId and not self.__extendAuthSeq:
                    if atomId in _coordAtomSite['atom_id']:
                        found = True
                        self.__preferAuthSeq = False
                        self.__authSeqId = 'label_seq_id'
                        seqKey = _seqKey
                        self.__setLocalSeqScheme()
                    elif atomId in ('HN1', 'HN2', 'HN3') and ((atomId[-1] + 'HN') in _coordAtomSite['atom_id']
                                                              or ('H' + atomId[-1]) in _coordAtomSite['atom_id']):
                        atomId = atomId[-1] + 'HN' if atomId[-1] + 'HN' in _coordAtomSite['atom_id'] else 'H' + atomId[-1]
                        found = True
                        self.__preferAuthSeq = False
                        self.__authSeqId = 'label_seq_id'
                        seqKey = _seqKey
                        self.__setLocalSeqScheme()
                    elif 'alt_atom_id' in _coordAtomSite and atomId in _coordAtomSite['alt_atom_id']:
                        found = True
                        self.__preferAuthSeq = False
                        self.__authSeqId = 'label_seq_id'
                        # self.__authAtomId = 'auth_atom_id'
                        seqKey = _seqKey
                        self.__setLocalSeqScheme()
            elif not self.__preferAuthSeq:
                self.__preferAuthSeq = True
                _seqKey, _coordAtomSite = self.getCoordAtomSiteOf(chainId, seqId, compId)
                if _coordAtomSite is not None and _coordAtomSite['comp_id'] == compId:
                    if atomId in _coordAtomSite['atom_id']:
                        found = True
                        self.__authSeqId = 'auth_seq_id'
                        seqKey = _seqKey
                        self.__setLocalSeqScheme()
                    elif atomId in ('HN1', 'HN2', 'HN3') and ((atomId[-1] + 'HN') in _coordAtomSite['atom_id']
                                                              or ('H' + atomId[-1]) in _coordAtomSite['atom_id']):
                        atomId = atomId[-1] + 'HN' if atomId[-1] + 'HN' in _coordAtomSite['atom_id'] else 'H' + atomId[-1]
                        found = True
                        self.__authSeqId = 'auth_seq_id'
                        seqKey = _seqKey
                        self.__setLocalSeqScheme()
                    elif 'alt_atom_id' in _coordAtomSite and atomId in _coordAtomSite['alt_atom_id']:
                        found = True
                        self.__authSeqId = 'auth_seq_id'
                        # self.__authAtomId = 'auth_atom_id'
                        seqKey = _seqKey
                        self.__setLocalSeqScheme()
                    elif not self.__extendAuthSeq:
                        self.__preferAuthSeq = False
                elif not self.__extendAuthSeq:
                    self.__preferAuthSeq = False

            if found:
                if self.__preferAuthSeq:
                    self.__preferAuthSeqCount += 1
                return atomId, asis

        if self.__ccU.updateChemCompDict(compId):
            cca = next((cca for cca in self.__ccU.lastAtomList if cca[self.__ccU.ccaAtomId] == atomId), None)
            if cca is not None and seqKey not in self.__coordUnobsRes and self.__ccU.lastChemCompDict['_chem_comp.pdbx_release_status'] == 'REL':
                checked = False
                ps = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == chainId), None)
                auth_seq_id_list = list(filter(None, ps['auth_seq_id'])) if ps is not None else None
                min_auth_seq_id = max_auth_seq_id = UNREAL_AUTH_SEQ_NUM
                if auth_seq_id_list is not None and len(auth_seq_id_list) > 0:
                    min_auth_seq_id = min(auth_seq_id_list)
                    max_auth_seq_id = max(auth_seq_id_list)
                if seqId == 1 or (chainId, seqId - 1) in self.__coordUnobsRes\
                   or seqId == min_auth_seq_id:
                    if atomId in aminoProtonCode and atomId != 'H1':
                        return self.testCoordAtomIdConsistency(chainId, seqId, compId, 'H1', seqKey, coordAtomSite)
                    if atomId in aminoProtonCode or atomId == 'P' or atomId.startswith('HOP'):
                        checked = True
                if not checked:
                    if atomId[0] in protonBeginCode:
                        bondedTo = self.__ccU.getBondedAtoms(compId, atomId)
                        if len(bondedTo) > 0 and bondedTo[0][0] != 'P':
                            if coordAtomSite is not None and bondedTo[0] in coordAtomSite['atom_id']:
                                if cca[self.__ccU.ccaLeavingAtomFlag] != 'Y'\
                                   or (self.__csStat.peptideLike(compId)
                                       and cca[self.__ccU.ccaNTerminalAtomFlag] == 'N'
                                       and cca[self.__ccU.ccaCTerminalAtomFlag] == 'N'):
                                    self.__f.append(f"[Hydrogen not instantiated] {self.__getCurrentRestraint(n=index, g=group)}"
                                                    f"{chainId}:{seqId}:{compId}:{atomId} is not properly instantiated in the coordinates. "
                                                    "Please re-upload the model file.")
                                    return atomId, asis
                            if bondedTo[0][0] == 'O':
                                return 'Ignorable hydroxyl group', asis
                    if seqId == max_auth_seq_id\
                       or (chainId, seqId + 1) in self.__coordUnobsRes and self.__csStat.peptideLike(compId):
                        if coordAtomSite is not None and atomId in carboxylCode\
                           and not isCyclicPolymer(self.__cR, self.__polySeq, chainId, self.__representativeModelId, self.__representativeAltId, self.__modelNumName):
                            self.__f.append(f"[Coordinate issue] {self.__getCurrentRestraint()}"
                                            f"{chainId}:{seqId}:{compId}:{atomId} is not properly instantiated in the coordinates. "
                                            "Please re-upload the model file.")
                            return atomId, asis

                    ext_seq = False
                    if auth_seq_id_list is not None and len(auth_seq_id_list) > 0:
                        if (compId == 'ACE' and seqId == min_auth_seq_id - 1)\
                           or (compId == 'NH2' and seqId == max_auth_seq_id + 1)\
                           or (compId in monDict3 and self.__preferAuthSeqCount - self.__preferLabelSeqCount >= MAX_PREF_LABEL_SCHEME_COUNT
                               and (min_auth_seq_id - MAX_ALLOWED_EXT_SEQ <= seqId < min_auth_seq_id
                                    or max_auth_seq_id < seqId <= max_auth_seq_id + MAX_ALLOWED_EXT_SEQ)):
                            ext_seq = True
                        elif self.__reasons is None and compId in monDict3 and atomId == 'H' and seqId < min_auth_seq_id\
                                and self.__preferAuthSeqCount - self.__preferLabelSeqCount < MAX_PREF_LABEL_SCHEME_COUNT:
                            ext_seq = True
                    if chainId in LARGE_ASYM_ID:
                        if ext_seq:
                            return atomId, asis
                        if self.__allow_ext_seq:
                            self.__f.append(f"[Sequence mismatch warning] {self.__getCurrentRestraint()}"
                                            f"The residue '{chainId}:{seqId}:{compId}' is not present in polymer sequence "
                                            f"of chain {chainId} of the coordinates. "
                                            "Please update the sequence in the Macromolecules page.")
                            asis = True
                        else:
                            if seqKey in self.__coordUnobsAtom\
                               and (atomId in self.__coordUnobsAtom[seqKey]['atom_ids']
                                    or (atomId[0] in protonBeginCode
                                        and any(bondedTo for bondedTo in self.__ccU.getBondedAtoms(compId, atomId, exclProton=True)
                                                if bondedTo in self.__coordUnobsAtom[seqKey]['atom_ids']))):
                                self.__f.append(f"[Coordinate issue] {self.__getCurrentRestraint()}"
                                                f"{chainId}:{seqId}:{compId}:{atomId} is not present in the coordinates.")
                                return atomId, asis
                            if (compId == 'ASP' and atomId == 'HD1') or (compId == 'GLU' and atomId == 'HE1'):
                                self.__f.append(f"[Hydrogen not instantiated] {self.__getCurrentRestraint()}"
                                                f"{chainId}:{seqId}:{compId}:{atomId} is not present in the coordinates.")
                                return atomId, asis
                            self.__f.append(f"[Atom not found] {self.__getCurrentRestraint(n=index, g=group)}"
                                            f"{chainId}:{seqId}:{compId}:{atomId} is not present in the coordinates.")
                            updatePolySeqRst(self.__polySeqRstFailed, chainId, seqId, compId)
        return atomId, asis

    def selectRealisticBondConstraint(self, atom1: str, atom2: str, alt_atom_id1: str, alt_atom_id2: str, dst_func: dict
                                      ) -> Tuple[str, str]:
        """ Return realistic bond constraint taking into account the current coordinates.
        """

        if not self.__hasCoord:
            return atom1, atom2

        try:

            _p1 =\
                self.__cR.getDictListWithFilter('atom_site',
                                                CARTN_DATA_ITEMS,
                                                [{'name': self.__authAsymId, 'type': 'str', 'value': atom1['chain_id']},
                                                 {'name': self.__authSeqId, 'type': 'int', 'value': atom1['seq_id']},
                                                 {'name': self.__authAtomId, 'type': 'str', 'value': atom1['atom_id']},
                                                 {'name': self.__modelNumName, 'type': 'int',
                                                  'value': self.__representativeModelId},
                                                 {'name': 'label_alt_id', 'type': 'enum',
                                                  'enum': (self.__representativeAltId,)}
                                                 ])

            if len(_p1) != 1:
                return atom1, atom2

            p1 = to_np_array(_p1[0])

            _p2 =\
                self.__cR.getDictListWithFilter('atom_site',
                                                CARTN_DATA_ITEMS,
                                                [{'name': self.__authAsymId, 'type': 'str', 'value': atom2['chain_id']},
                                                 {'name': self.__authSeqId, 'type': 'int', 'value': atom2['seq_id']},
                                                 {'name': self.__authAtomId, 'type': 'str', 'value': atom2['atom_id']},
                                                 {'name': self.__modelNumName, 'type': 'int',
                                                  'value': self.__representativeModelId},
                                                 {'name': 'label_alt_id', 'type': 'enum',
                                                  'enum': (self.__representativeAltId,)}
                                                 ])

            if len(_p2) != 1:
                return atom1, atom2

            p2 = to_np_array(_p2[0])

            d_org = distance(p1, p2)

            lower_limit = dst_func.get('lower_limit')
            if lower_limit is not None:
                lower_limit = float(lower_limit)
            upper_limit = dst_func.get('upper_limit')
            if upper_limit is not None:
                upper_limit = float(upper_limit)

            if alt_atom_id1 is not None:

                _p1 =\
                    self.__cR.getDictListWithFilter('atom_site',
                                                    CARTN_DATA_ITEMS,
                                                    [{'name': self.__authAsymId, 'type': 'str', 'value': atom1['chain_id']},
                                                     {'name': self.__authSeqId, 'type': 'int', 'value': atom1['seq_id']},
                                                     {'name': self.__authAtomId, 'type': 'str', 'value': alt_atom_id1},
                                                     {'name': self.__modelNumName, 'type': 'int',
                                                      'value': self.__representativeModelId},
                                                     {'name': 'label_alt_id', 'type': 'enum',
                                                      'enum': (self.__representativeAltId,)}
                                                     ])

                if len(_p1) != 1:
                    return atom1, atom2

                p1_alt = to_np_array(_p1[0])

                d_alt = distance(p1_alt, p2)

                if dist_error(lower_limit, upper_limit, d_org) > dist_error(lower_limit, upper_limit, d_alt):
                    if 'auth_atom_id' not in atom1:
                        atom1['auth_atom_id'] = atom1['atom_id']
                    atom1['atom_id'] = alt_atom_id1

            elif alt_atom_id2 is not None:

                _p2 =\
                    self.__cR.getDictListWithFilter('atom_site',
                                                    CARTN_DATA_ITEMS,
                                                    [{'name': self.__authAsymId, 'type': 'str', 'value': atom2['chain_id']},
                                                     {'name': self.__authSeqId, 'type': 'int', 'value': atom2['seq_id']},
                                                     {'name': self.__authAtomId, 'type': 'str', 'value': alt_atom_id2},
                                                     {'name': self.__modelNumName, 'type': 'int',
                                                      'value': self.__representativeModelId},
                                                     {'name': 'label_alt_id', 'type': 'enum',
                                                      'enum': (self.__representativeAltId,)}
                                                     ])

                if len(_p2) != 1:
                    return atom1, atom2

                p2_alt = to_np_array(_p2[0])

                d_alt = distance(p1, p2_alt)

                if dist_error(lower_limit, upper_limit, d_org) > dist_error(lower_limit, upper_limit, d_alt):
                    if 'auth_atom_id' not in atom2:
                        atom2['auth_atom_id'] = atom2['atom_id']
                    atom2['atom_id'] = alt_atom_id2

        except Exception as e:
            if self.__verbose:
                self.__lfh.write(f"+{self.__class_name__}.selectRealisticBondConstraint() ++ Error  - {str(e)}")

        return atom1, atom2

    def selectRealisticChi2AngleConstraint(self, atom1: str, atom2: str, atom3: str, atom4: str, dst_func: dict
                                           ) -> dict:
        """ Return realistic chi2 angle constraint taking into account the current coordinates.
        """

        if not self.__hasCoord:
            return dst_func

        try:

            _p1 =\
                self.__cR.getDictListWithFilter('atom_site',
                                                CARTN_DATA_ITEMS,
                                                [{'name': self.__authAsymId, 'type': 'str', 'value': atom1['chain_id']},
                                                 {'name': self.__authSeqId, 'type': 'int', 'value': atom1['seq_id']},
                                                 {'name': self.__authAtomId, 'type': 'str', 'value': atom1['atom_id']},
                                                 {'name': self.__modelNumName, 'type': 'int',
                                                  'value': self.__representativeModelId},
                                                 {'name': 'label_alt_id', 'type': 'enum',
                                                  'enum': (self.__representativeAltId,)}
                                                 ])

            if len(_p1) != 1:
                return dst_func

            p1 = to_np_array(_p1[0])

            _p2 =\
                self.__cR.getDictListWithFilter('atom_site',
                                                CARTN_DATA_ITEMS,
                                                [{'name': self.__authAsymId, 'type': 'str', 'value': atom2['chain_id']},
                                                 {'name': self.__authSeqId, 'type': 'int', 'value': atom2['seq_id']},
                                                 {'name': self.__authAtomId, 'type': 'str', 'value': atom2['atom_id']},
                                                 {'name': self.__modelNumName, 'type': 'int',
                                                  'value': self.__representativeModelId},
                                                 {'name': 'label_alt_id', 'type': 'enum',
                                                  'enum': (self.__representativeAltId,)}
                                                 ])

            if len(_p2) != 1:
                return dst_func

            p2 = to_np_array(_p2[0])

            _p3 =\
                self.__cR.getDictListWithFilter('atom_site',
                                                CARTN_DATA_ITEMS,
                                                [{'name': self.__authAsymId, 'type': 'str', 'value': atom3['chain_id']},
                                                 {'name': self.__authSeqId, 'type': 'int', 'value': atom3['seq_id']},
                                                 {'name': self.__authAtomId, 'type': 'str', 'value': atom3['atom_id']},
                                                 {'name': self.__modelNumName, 'type': 'int',
                                                  'value': self.__representativeModelId},
                                                 {'name': 'label_alt_id', 'type': 'enum',
                                                  'enum': (self.__representativeAltId,)}
                                                 ])

            if len(_p3) != 1:
                return dst_func

            p3 = to_np_array(_p3[0])

            _p4 =\
                self.__cR.getDictListWithFilter('atom_site',
                                                CARTN_DATA_ITEMS,
                                                [{'name': self.__authAsymId, 'type': 'str', 'value': atom4['chain_id']},
                                                 {'name': self.__authSeqId, 'type': 'int', 'value': atom4['seq_id']},
                                                 {'name': self.__authAtomId, 'type': 'str', 'value': 'CD1'},
                                                 {'name': self.__modelNumName, 'type': 'int',
                                                  'value': self.__representativeModelId},
                                                 {'name': 'label_alt_id', 'type': 'enum',
                                                  'enum': (self.__representativeAltId,)}
                                                 ])

            if len(_p4) != 1:
                return dst_func

            p4 = to_np_array(_p4[0])

            chi2 = dihedral_angle(p1, p2, p3, p4)

            _p4 =\
                self.__cR.getDictListWithFilter('atom_site',
                                                CARTN_DATA_ITEMS,
                                                [{'name': self.__authAsymId, 'type': 'str', 'value': atom4['chain_id']},
                                                 {'name': self.__authSeqId, 'type': 'int', 'value': atom4['seq_id']},
                                                 {'name': self.__authAtomId, 'type': 'str', 'value': 'CD2'},
                                                 {'name': self.__modelNumName, 'type': 'int',
                                                  'value': self.__representativeModelId},
                                                 {'name': 'label_alt_id', 'type': 'enum',
                                                  'enum': (self.__representativeAltId,)}
                                                 ])

            if len(_p4) != 1:
                return dst_func

            alt_p4 = to_np_array(_p4[0])

            alt_chi2 = dihedral_angle(p1, p2, p3, alt_p4)

            target_value = dst_func.get('target_value')
            if target_value is not None:
                target_value = float(target_value)
            target_value_uncertainty = dst_func.get('target_value_uncertainty')
            if target_value_uncertainty is not None:
                target_value_uncertainty = float(target_value_uncertainty)

            lower_limit = dst_func.get('lower_limit')
            if lower_limit is not None:
                lower_limit = float(lower_limit)
            upper_limit = dst_func.get('upper_limit')
            if upper_limit is not None:
                upper_limit = float(upper_limit)

            lower_linear_limit = dst_func.get('lower_linear_limit')
            if lower_linear_limit is not None:
                lower_linear_limit = float(lower_linear_limit)
            upper_linear_limit = dst_func.get('upper_linear_limit')
            if upper_linear_limit is not None:
                upper_linear_limit = float(upper_linear_limit)

            target_value, lower_bound, upper_bound =\
                angle_target_values(target_value, target_value_uncertainty,
                                    lower_limit, upper_limit,
                                    lower_linear_limit, upper_linear_limit)

            if target_value is None:
                return dst_func

            if angle_error(lower_bound, upper_bound, target_value, chi2) > angle_error(lower_bound, upper_bound, target_value, alt_chi2):
                target_value = dst_func.get('target_value')
                if target_value is not None:
                    target_value = float(target_value) + 180.0
                lower_limit = dst_func.get('lower_limit')
                if lower_limit is not None:
                    lower_limit = float(lower_limit) + 180.0
                upper_limit = dst_func.get('upper_limit')
                if upper_limit is not None:
                    upper_limit = float(upper_limit) + 180.0

                if lower_linear_limit is not None:
                    lower_linear_limit += 180.0
                if upper_linear_limit is not None:
                    upper_linear_limit += 180.0

                _array = numpy.array([target_value, lower_limit, upper_limit, lower_linear_limit, upper_linear_limit],
                                     dtype=float)

                shift = 0.0
                if self.__correctCircularShift:
                    if numpy.nanmin(_array) >= THRESHHOLD_FOR_CIRCULAR_SHIFT:
                        shift = -(numpy.nanmax(_array) // 360) * 360
                    elif numpy.nanmax(_array) <= -THRESHHOLD_FOR_CIRCULAR_SHIFT:
                        shift = -(numpy.nanmin(_array) // 360) * 360
                if target_value is not None:
                    dst_func['target_value'] = str(target_value + shift)
                if lower_limit is not None:
                    dst_func['lower_limit'] = str(lower_limit + shift)
                if upper_limit is not None:
                    dst_func['upper_limit'] = str(upper_limit + shift)
                if lower_linear_limit is not None:
                    dst_func['lower_linear_limit'] = str(lower_linear_limit + shift)
                if upper_linear_limit is not None:
                    dst_func['upper_linear_limit'] = str(upper_linear_limit + shift)

        except Exception as e:
            if self.__verbose:
                self.__lfh.write(f"+{self.__class_name__}.selectRealisticChi2AngleConstraint() ++ Error  - {str(e)}")

        return dst_func

    def getCoordAtomSiteOf(self, chainId: str, seqId: int, compId: Optional[str] = None, cifCheck: bool = True, asis: bool = True
                           ) -> Tuple[Tuple[str, int], Optional[dict]]:
        seqKey = (chainId, seqId)
        if cifCheck:
            preferAuthSeq = self.__preferAuthSeq if asis else not self.__preferAuthSeq
            if preferAuthSeq:
                if compId is not None:
                    _seqKey = (chainId, seqId, compId)
                    if _seqKey in self.__coordAtomSite:
                        return seqKey, self.__coordAtomSite[_seqKey]
                if seqKey in self.__coordAtomSite:
                    if compId is None:
                        return seqKey, self.__coordAtomSite[seqKey]
                    _compId = self.__coordAtomSite[seqKey]['comp_id']
                    if compId == _compId:
                        return seqKey, self.__coordAtomSite[seqKey]
                    if self.__hasNonPoly:
                        npList = [np for np in self.__nonPoly if np['auth_chain_id'] == chainId]
                        for np in npList:
                            if np['comp_id'][0] == compId and np['auth_seq_id'][0] == seqId:
                                _seqKey = (chainId, np['seq_id'][0])
                                if _seqKey in self.__coordAtomSite and self.__coordAtomSite[_seqKey]['comp_id'] == compId:
                                    return _seqKey, self.__coordAtomSite[_seqKey]
                    return seqKey, self.__coordAtomSite[seqKey]
            else:
                if seqKey in self.__labelToAuthSeq:
                    seqKey = self.__labelToAuthSeq[seqKey]
                    if cifCheck and compId is not None:
                        _seqKey = (seqKey[0], seqKey[1], compId)
                        if _seqKey in self.__coordAtomSite:
                            return seqKey, self.__coordAtomSite[_seqKey]
                    if seqKey in self.__coordAtomSite:
                        return seqKey, self.__coordAtomSite[seqKey]
        return seqKey, None

    # Enter a parse tree produced by DynamoMRParser#torsion_angle_restraints.
    def enterTorsion_angle_restraints(self, ctx: DynamoMRParser.Torsion_angle_restraintsContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'dihed'

        self.closeSequqnce()

    # Exit a parse tree produced by DynamoMRParser#torsion_angle_restraints.
    def exitTorsion_angle_restraints(self, ctx: DynamoMRParser.Torsion_angle_restraintsContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by DynamoMRParser#torsion_angle_restraint.
    def enterTorsion_angle_restraint(self, ctx: DynamoMRParser.Torsion_angle_restraintContext):  # pylint: disable=unused-argument
        self.dihedRestraints += 1

        self.atomSelectionSet.clear()

    # Exit a parse tree produced by DynamoMRParser#torsion_angle_restraint.
    def exitTorsion_angle_restraint(self, ctx: DynamoMRParser.Torsion_angle_restraintContext):

        try:

            index = int(str(ctx.Integer(0)))

            seqId1 = int(str(ctx.Integer(1)))
            compId1 = str(ctx.Simple_name(0)).upper()
            atomId1 = str(ctx.Simple_name(1)).upper()
            seqId2 = int(str(ctx.Integer(2)))
            compId2 = str(ctx.Simple_name(2)).upper()
            atomId2 = str(ctx.Simple_name(3)).upper()
            seqId3 = int(str(ctx.Integer(3)))
            compId3 = str(ctx.Simple_name(4)).upper()
            atomId3 = str(ctx.Simple_name(5)).upper()
            seqId4 = int(str(ctx.Integer(4)))
            compId4 = str(ctx.Simple_name(6)).upper()
            atomId4 = str(ctx.Simple_name(7)).upper()

            if len(self.numberSelection) == 0 or None in self.numberSelection:
                return

            target_value = None
            lower_limit = self.numberSelection[0]
            upper_limit = self.numberSelection[1]
            # fource_const = self.numberSelection[2]

            dstFunc = self.validateAngleRange(index, 1.0, target_value, lower_limit, upper_limit)

            if dstFunc is None:
                return

            if not self.__hasPolySeq and not self.__hasNonPolySeq:
                return

            self.__retrieveLocalSeqScheme()

            chainAssign1, asis1 = self.assignCoordPolymerSequence(None, seqId1, compId1, atomId1, index)
            chainAssign2, asis2 = self.assignCoordPolymerSequence(None, seqId2, compId2, atomId2, index)
            chainAssign3, asis3 = self.assignCoordPolymerSequence(None, seqId3, compId3, atomId3, index)
            chainAssign4, asis4 = self.assignCoordPolymerSequence(None, seqId4, compId4, atomId4, index)

            if 0 in (len(chainAssign1), len(chainAssign2), len(chainAssign3), len(chainAssign4)):
                return

            self.selectCoordAtoms(chainAssign1, seqId1, compId1, atomId1, False)
            self.selectCoordAtoms(chainAssign2, seqId2, compId2, atomId2, False)
            self.selectCoordAtoms(chainAssign3, seqId3, compId3, atomId3, False)
            self.selectCoordAtoms(chainAssign4, seqId4, compId4, atomId4, False)

            if len(self.atomSelectionSet) < 4:
                return

            try:
                compId = self.atomSelectionSet[0][0]['comp_id']
                peptide, nucleotide, carbohydrate = self.__csStat.getTypeOfCompId(compId)
            except IndexError:
                self.areUniqueCoordAtoms('a torsion angle')
                return

            len_f = len(self.__f)
            self.areUniqueCoordAtoms('a torsion angle',
                                     allow_ambig=True, allow_ambig_warn_title='Ambiguous dihedral angle')
            combinationId = '.' if len_f == len(self.__f) else 0

            atomSelTotal = sum(len(s) for s in self.atomSelectionSet)

            if isinstance(combinationId, int):
                fixedAngleName = '.'
                for atom1, atom2, atom3, atom4 in itertools.product(self.atomSelectionSet[0],
                                                                    self.atomSelectionSet[1],
                                                                    self.atomSelectionSet[2],
                                                                    self.atomSelectionSet[3]):
                    atoms = [atom1, atom2, atom3, atom4]
                    angleName = getTypeOfDihedralRestraint(peptide, nucleotide, carbohydrate,
                                                           atoms,
                                                           'plane_like' in dstFunc,
                                                           self.__cR, self.__ccU,
                                                           self.__representativeModelId, self.__representativeAltId, self.__modelNumName)

                    if angleName is not None and angleName.startswith('pseudo'):
                        angleName, atom2, atom3, err = fixBackboneAtomsOfDihedralRestraint(angleName,
                                                                                           atoms,
                                                                                           self.__getCurrentRestraint(n=index))
                        self.__f.append(err)

                    if angleName in emptyValue and atomSelTotal != 4:
                        continue

                    fixedAngleName = angleName
                    break

            sf = None
            if self.__createSfDict:
                sf = self.__getSf(constraintType='backbone chemical shifts',
                                  potentialType=getPotentialType(self.__file_type, self.__cur_subtype, dstFunc),
                                  softwareName='DYNAMO/TALOS')

            first_item = True

            for atom1, atom2, atom3, atom4 in itertools.product(self.atomSelectionSet[0],
                                                                self.atomSelectionSet[1],
                                                                self.atomSelectionSet[2],
                                                                self.atomSelectionSet[3]):
                atoms = [atom1, atom2, atom3, atom4]
                angleName = getTypeOfDihedralRestraint(peptide, nucleotide, carbohydrate,
                                                       atoms,
                                                       'plane_like' in dstFunc,
                                                       self.__cR, self.__ccU,
                                                       self.__representativeModelId, self.__representativeAltId, self.__modelNumName)

                if angleName is not None and angleName.startswith('pseudo'):
                    angleName, atom2, atom3, err = fixBackboneAtomsOfDihedralRestraint(angleName,
                                                                                       atoms,
                                                                                       self.__getCurrentRestraint(n=index))
                    self.__f.append(err)

                if angleName in emptyValue and atomSelTotal != 4:
                    continue

                if isinstance(combinationId, int):
                    if angleName != fixedAngleName:
                        continue
                    combinationId += 1
                if peptide and angleName == 'CHI2' and atom4['atom_id'] == 'CD1' and isLikePheOrTyr(atom2['comp_id'], self.__ccU):
                    dstFunc = self.selectRealisticChi2AngleConstraint(atom1, atom2, atom3, atom4,
                                                                      dstFunc)
                if self.__debug:
                    print(f"subtype={self.__cur_subtype} id={self.dihedRestraints} (index={index}) angleName={angleName} "
                          f"atom1={atom1} atom2={atom2} atom3={atom3} atom4={atom4} {dstFunc}")
                if self.__createSfDict and sf is not None:
                    if first_item:
                        sf['id'] += 1
                        first_item = False
                    sf['index_id'] += 1
                    row = getRow(self.__cur_subtype, sf['id'], sf['index_id'],
                                 combinationId, None, angleName,
                                 sf['list_id'], self.__entryId, dstFunc,
                                 self.__authToStarSeq, self.__authToOrigSeq, self.__authToInsCode, self.__offsetHolder,
                                 atom1, atom2, atom3, atom4, asis1=asis1, asis2=asis2, asis3=asis3, asis4=asis4)
                    sf['loop'].add_data(row)

            if self.__createSfDict and sf is not None and isinstance(combinationId, int) and combinationId == 1:
                sf['loop'].data[-1] = resetCombinationId(self.__cur_subtype, sf['loop'].data[-1])

        except ValueError:
            self.dihedRestraints -= 1

        finally:
            self.numberSelection.clear()

    # Enter a parse tree produced by DynamoMRParser#torsion_angle_restraints_sw_segid.
    def enterTorsion_angle_restraints_sw_segid(self, ctx: DynamoMRParser.Torsion_angle_restraints_sw_segidContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'dihed'

        self.closeSequqnce()

    # Exit a parse tree produced by DynamoMRParser#torsion_angle_restraints_sw_segid.
    def exitTorsion_angle_restraints_sw_segid(self, ctx: DynamoMRParser.Torsion_angle_restraints_sw_segidContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by DynamoMRParser#torsion_angle_restraint_sw_segid.
    def enterTorsion_angle_restraint_sw_segid(self, ctx: DynamoMRParser.Torsion_angle_restraint_sw_segidContext):  # pylint: disable=unused-argument
        self.dihedRestraints += 1

        self.atomSelectionSet.clear()

    # Exit a parse tree produced by DynamoMRParser#torsion_angle_restraint_sw_segid.
    def exitTorsion_angle_restraint_sw_segid(self, ctx: DynamoMRParser.Torsion_angle_restraint_sw_segidContext):

        try:

            index = int(str(ctx.Integer(0)))

            chainId1 = str(ctx.Simple_name(0))
            seqId1 = int(str(ctx.Integer(1)))
            compId1 = str(ctx.Simple_name(1)).upper()
            atomId1 = str(ctx.Simple_name(2)).upper()
            chainId2 = str(ctx.Simple_name(3))
            seqId2 = int(str(ctx.Integer(2)))
            compId2 = str(ctx.Simple_name(4)).upper()
            atomId2 = str(ctx.Simple_name(5)).upper()
            chainId3 = str(ctx.Simple_name(6))
            seqId3 = int(str(ctx.Integer(3)))
            compId3 = str(ctx.Simple_name(7)).upper()
            atomId3 = str(ctx.Simple_name(8)).upper()
            chainId4 = str(ctx.Simple_name(9))
            seqId4 = int(str(ctx.Integer(4)))
            compId4 = str(ctx.Simple_name(10)).upper()
            atomId4 = str(ctx.Simple_name(11)).upper()

            if len(self.numberSelection) == 0 or None in self.numberSelection:
                return

            target_value = None
            lower_limit = self.numberSelection[0]
            upper_limit = self.numberSelection[1]
            # fource_const = self.numberSelection[2]

            dstFunc = self.validateAngleRange(None, 1.0, target_value, lower_limit, upper_limit)

            if dstFunc is None:
                return

            if not self.__hasPolySeq and not self.__hasNonPolySeq:
                return

            self.__retrieveLocalSeqScheme()

            chainAssign1, asis1 = self.assignCoordPolymerSequence(chainId1, seqId1, compId1, atomId1, index)
            chainAssign2, asis2 = self.assignCoordPolymerSequence(chainId2, seqId2, compId2, atomId2, index)
            chainAssign3, asis3 = self.assignCoordPolymerSequence(chainId3, seqId3, compId3, atomId3, index)
            chainAssign4, asis4 = self.assignCoordPolymerSequence(chainId4, seqId4, compId4, atomId4, index)

            if 0 in (len(chainAssign1), len(chainAssign2), len(chainAssign3), len(chainAssign4)):
                return

            self.selectCoordAtoms(chainAssign1, seqId1, compId1, atomId1, False)
            self.selectCoordAtoms(chainAssign2, seqId2, compId2, atomId2, False)
            self.selectCoordAtoms(chainAssign3, seqId3, compId3, atomId3, False)
            self.selectCoordAtoms(chainAssign4, seqId4, compId4, atomId4, False)

            if len(self.atomSelectionSet) < 4:
                return

            try:
                compId = self.atomSelectionSet[0][0]['comp_id']
                peptide, nucleotide, carbohydrate = self.__csStat.getTypeOfCompId(compId)
            except IndexError:
                self.areUniqueCoordAtoms('a torsion angle')
                return

            len_f = len(self.__f)
            self.areUniqueCoordAtoms('a torsion angle',
                                     allow_ambig=True, allow_ambig_warn_title='Ambiguous dihedral angle')
            combinationId = '.' if len_f == len(self.__f) else 0

            atomSelTotal = sum(len(s) for s in self.atomSelectionSet)

            if isinstance(combinationId, int):
                fixedAngleName = '.'
                for atom1, atom2, atom3, atom4 in itertools.product(self.atomSelectionSet[0],
                                                                    self.atomSelectionSet[1],
                                                                    self.atomSelectionSet[2],
                                                                    self.atomSelectionSet[3]):
                    atoms = [atom1, atom2, atom3, atom4]
                    angleName = getTypeOfDihedralRestraint(peptide, nucleotide, carbohydrate,
                                                           atoms,
                                                           'plane_like' in dstFunc,
                                                           self.__cR, self.__ccU,
                                                           self.__representativeModelId, self.__representativeAltId, self.__modelNumName)

                    if angleName is not None and angleName.startswith('pseudo'):
                        angleName, atom2, atom3, err = fixBackboneAtomsOfDihedralRestraint(angleName,
                                                                                           atoms,
                                                                                           self.__getCurrentRestraint(n=index))
                        self.__f.append(err)

                    if angleName in emptyValue and atomSelTotal != 4:
                        continue

                    fixedAngleName = angleName
                    break

            sf = None
            if self.__createSfDict:
                sf = self.__getSf(constraintType='backbone chemical shifts',
                                  potentialType=getPotentialType(self.__file_type, self.__cur_subtype, dstFunc),
                                  softwareName='DYNAMO/TALOS')

            first_item = True

            for atom1, atom2, atom3, atom4 in itertools.product(self.atomSelectionSet[0],
                                                                self.atomSelectionSet[1],
                                                                self.atomSelectionSet[2],
                                                                self.atomSelectionSet[3]):
                atoms = [atom1, atom2, atom3, atom4]
                angleName = getTypeOfDihedralRestraint(peptide, nucleotide, carbohydrate,
                                                       atoms,
                                                       'plane_like' in dstFunc,
                                                       self.__cR, self.__ccU,
                                                       self.__representativeModelId, self.__representativeAltId, self.__modelNumName)

                if angleName is not None and angleName.startswith('pseudo'):
                    angleName, atom2, atom3, err = fixBackboneAtomsOfDihedralRestraint(angleName,
                                                                                       atoms,
                                                                                       self.__getCurrentRestraint(n=index))
                    self.__f.append(err)

                if angleName in emptyValue and atomSelTotal != 4:
                    continue

                if isinstance(combinationId, int):
                    if angleName != fixedAngleName:
                        continue
                    combinationId += 1
                if peptide and angleName == 'CHI2' and atom4['atom_id'] == 'CD1' and isLikePheOrTyr(atom2['comp_id'], self.__ccU):
                    dstFunc = self.selectRealisticChi2AngleConstraint(atom1, atom2, atom3, atom4,
                                                                      dstFunc)
                if self.__debug:
                    print(f"subtype={self.__cur_subtype} id={self.dihedRestraints} (index={index}) angleName={angleName} "
                          f"atom1={atom1} atom2={atom2} atom3={atom3} atom4={atom4} {dstFunc}")
                if self.__createSfDict and sf is not None:
                    if first_item:
                        sf['id'] += 1
                        first_item = False
                    sf['index_id'] += 1
                    row = getRow(self.__cur_subtype, sf['id'], sf['index_id'],
                                 combinationId, None, angleName,
                                 sf['list_id'], self.__entryId, dstFunc,
                                 self.__authToStarSeq, self.__authToOrigSeq, self.__authToInsCode, self.__offsetHolder,
                                 atom1, atom2, atom3, atom4, asis1=asis1, asis2=asis2, asis3=asis3, asis4=asis4)
                    sf['loop'].add_data(row)

            if self.__createSfDict and sf is not None and isinstance(combinationId, int) and combinationId == 1:
                sf['loop'].data[-1] = resetCombinationId(self.__cur_subtype, sf['loop'].data[-1])

        except ValueError:
            self.dihedRestraints -= 1

        finally:
            self.numberSelection.clear()

    # Enter a parse tree produced by DynamoMRParser#torsion_angle_restraints_ew_segid.
    def enterTorsion_angle_restraints_ew_segid(self, ctx: DynamoMRParser.Torsion_angle_restraints_ew_segidContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'dihed'

        self.closeSequqnce()

    # Exit a parse tree produced by DynamoMRParser#torsion_angle_restraints_ew_segid.
    def exitTorsion_angle_restraints_ew_segid(self, ctx: DynamoMRParser.Torsion_angle_restraints_ew_segidContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by DynamoMRParser#torsion_angle_restraint_ew_segid.
    def enterTorsion_angle_restraint_ew_segid(self, ctx: DynamoMRParser.Torsion_angle_restraint_ew_segidContext):  # pylint: disable=unused-argument
        self.dihedRestraints += 1

        self.atomSelectionSet.clear()

    # Exit a parse tree produced by DynamoMRParser#torsion_angle_restraint_ew_segid.
    def exitTorsion_angle_restraint_ew_segid(self, ctx: DynamoMRParser.Torsion_angle_restraint_ew_segidContext):

        try:

            index = int(str(ctx.Integer(0)))

            seqId1 = int(str(ctx.Integer(1)))
            compId1 = str(ctx.Simple_name(0)).upper()
            atomId1 = str(ctx.Simple_name(1)).upper()
            chainId1 = str(ctx.Simple_name(2))
            seqId2 = int(str(ctx.Integer(2)))
            compId2 = str(ctx.Simple_name(3)).upper()
            atomId2 = str(ctx.Simple_name(4)).upper()
            chainId2 = str(ctx.Simple_name(5))
            seqId3 = int(str(ctx.Integer(3)))
            compId3 = str(ctx.Simple_name(6)).upper()
            atomId3 = str(ctx.Simple_name(7)).upper()
            chainId3 = str(ctx.Simple_name(8))
            seqId4 = int(str(ctx.Integer(4)))
            compId4 = str(ctx.Simple_name(9)).upper()
            atomId4 = str(ctx.Simple_name(10)).upper()
            chainId4 = str(ctx.Simple_name(11))

            if len(self.numberSelection) == 0 or None in self.numberSelection:
                return

            target_value = None
            lower_limit = self.numberSelection[0]
            upper_limit = self.numberSelection[1]
            # fource_const = self.numberSelection[2]

            dstFunc = self.validateAngleRange(None, 1.0, target_value, lower_limit, upper_limit)

            if dstFunc is None:
                return

            if not self.__hasPolySeq and not self.__hasNonPolySeq:
                return

            self.__retrieveLocalSeqScheme()

            chainAssign1, asis1 = self.assignCoordPolymerSequence(chainId1, seqId1, compId1, atomId1, index)
            chainAssign2, asis2 = self.assignCoordPolymerSequence(chainId2, seqId2, compId2, atomId2, index)
            chainAssign3, asis3 = self.assignCoordPolymerSequence(chainId3, seqId3, compId3, atomId3, index)
            chainAssign4, asis4 = self.assignCoordPolymerSequence(chainId4, seqId4, compId4, atomId4, index)

            if 0 in (len(chainAssign1), len(chainAssign2), len(chainAssign3), len(chainAssign4)):
                return

            self.selectCoordAtoms(chainAssign1, seqId1, compId1, atomId1, False)
            self.selectCoordAtoms(chainAssign2, seqId2, compId2, atomId2, False)
            self.selectCoordAtoms(chainAssign3, seqId3, compId3, atomId3, False)
            self.selectCoordAtoms(chainAssign4, seqId4, compId4, atomId4, False)

            if len(self.atomSelectionSet) < 4:
                return

            try:
                compId = self.atomSelectionSet[0][0]['comp_id']
                peptide, nucleotide, carbohydrate = self.__csStat.getTypeOfCompId(compId)
            except IndexError:
                self.areUniqueCoordAtoms('a torsion angle')
                return

            len_f = len(self.__f)
            self.areUniqueCoordAtoms('a torsion angle',
                                     allow_ambig=True, allow_ambig_warn_title='Ambiguous dihedral angle')
            combinationId = '.' if len_f == len(self.__f) else 0

            atomSelTotal = sum(len(s) for s in self.atomSelectionSet)

            if isinstance(combinationId, int):
                fixedAngleName = '.'
                for atom1, atom2, atom3, atom4 in itertools.product(self.atomSelectionSet[0],
                                                                    self.atomSelectionSet[1],
                                                                    self.atomSelectionSet[2],
                                                                    self.atomSelectionSet[3]):
                    atoms = [atom1, atom2, atom3, atom4]
                    angleName = getTypeOfDihedralRestraint(peptide, nucleotide, carbohydrate,
                                                           atoms,
                                                           'plane_like' in dstFunc,
                                                           self.__cR, self.__ccU,
                                                           self.__representativeModelId, self.__representativeAltId, self.__modelNumName)

                    if angleName is not None and angleName.startswith('pseudo'):
                        angleName, atom2, atom3, err = fixBackboneAtomsOfDihedralRestraint(angleName,
                                                                                           atoms,
                                                                                           self.__getCurrentRestraint(n=index))
                        self.__f.append(err)

                    if angleName in emptyValue and atomSelTotal != 4:
                        continue

                    fixedAngleName = angleName
                    break

            sf = None
            if self.__createSfDict:
                sf = self.__getSf(constraintType='backbone chemical shifts',
                                  potentialType=getPotentialType(self.__file_type, self.__cur_subtype, dstFunc),
                                  softwareName='DYNAMO/TALOS')

            first_item = True

            for atom1, atom2, atom3, atom4 in itertools.product(self.atomSelectionSet[0],
                                                                self.atomSelectionSet[1],
                                                                self.atomSelectionSet[2],
                                                                self.atomSelectionSet[3]):
                atoms = [atom1, atom2, atom3, atom4]
                angleName = getTypeOfDihedralRestraint(peptide, nucleotide, carbohydrate,
                                                       atoms,
                                                       'plane_like' in dstFunc,
                                                       self.__cR, self.__ccU,
                                                       self.__representativeModelId, self.__representativeAltId, self.__modelNumName)

                if angleName is not None and angleName.startswith('pseudo'):
                    angleName, atom2, atom3, err = fixBackboneAtomsOfDihedralRestraint(angleName,
                                                                                       atoms,
                                                                                       self.__getCurrentRestraint(n=index))
                    self.__f.append(err)

                if angleName in emptyValue and atomSelTotal != 4:
                    continue

                if isinstance(combinationId, int):
                    if angleName != fixedAngleName:
                        continue
                    combinationId += 1
                if peptide and angleName == 'CHI2' and atom4['atom_id'] == 'CD1' and isLikePheOrTyr(atom2['comp_id'], self.__ccU):
                    dstFunc = self.selectRealisticChi2AngleConstraint(atom1, atom2, atom3, atom4,
                                                                      dstFunc)
                if self.__debug:
                    print(f"subtype={self.__cur_subtype} id={self.dihedRestraints} (index={index}) angleName={angleName} "
                          f"atom1={atom1} atom2={atom2} atom3={atom3} atom4={atom4} {dstFunc}")
                if self.__createSfDict and sf is not None:
                    if first_item:
                        sf['id'] += 1
                        first_item = False
                    sf['index_id'] += 1
                    row = getRow(self.__cur_subtype, sf['id'], sf['index_id'],
                                 combinationId, None, angleName,
                                 sf['list_id'], self.__entryId, dstFunc,
                                 self.__authToStarSeq, self.__authToOrigSeq, self.__authToInsCode, self.__offsetHolder,
                                 atom1, atom2, atom3, atom4, asis1=asis1, asis2=asis2, asis3=asis3, asis4=asis4)
                    sf['loop'].add_data(row)

            if self.__createSfDict and sf is not None and isinstance(combinationId, int) and combinationId == 1:
                sf['loop'].data[-1] = resetCombinationId(self.__cur_subtype, sf['loop'].data[-1])

        except ValueError:
            self.dihedRestraints -= 1

        finally:
            self.numberSelection.clear()

    def validateAngleRange(self, index: int, weight: float, target_value: Optional[float],
                           lower_limit: Optional[float], upper_limit: Optional[float]) -> Optional[dict]:
        """ Validate angle value range.
        """

        validRange = True
        dstFunc = {'weight': weight}

        if self.__correctCircularShift:
            _array = numpy.array([target_value, lower_limit, upper_limit],
                                 dtype=float)

            shift = None
            if numpy.nanmin(_array) >= THRESHHOLD_FOR_CIRCULAR_SHIFT:
                shift = -(numpy.nanmax(_array) // 360) * 360
            elif numpy.nanmax(_array) <= -THRESHHOLD_FOR_CIRCULAR_SHIFT:
                shift = -(numpy.nanmin(_array) // 360) * 360
            if shift is not None:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint(n=index)}"
                                "The target/limit values for an angle restraint have been circularly shifted "
                                f"to fit within range {ANGLE_RESTRAINT_ERROR}.")
                if target_value is not None:
                    target_value += shift
                if lower_limit is not None:
                    lower_limit += shift
                if upper_limit is not None:
                    upper_limit += shift

        if target_value is not None:
            if ANGLE_ERROR_MIN < target_value < ANGLE_ERROR_MAX:
                dstFunc['target_value'] = f"{target_value}"
            else:
                validRange = False
                self.__f.append(f"[Range value error] {self.__getCurrentRestraint(n=index)}"
                                f"The target value='{target_value}' must be within range {ANGLE_RESTRAINT_ERROR}.")

        if lower_limit is not None:
            if ANGLE_ERROR_MIN <= lower_limit < ANGLE_ERROR_MAX:
                dstFunc['lower_limit'] = f"{lower_limit:.3f}"
            else:
                validRange = False
                self.__f.append(f"[Range value error] {self.__getCurrentRestraint(n=index)}"
                                f"The lower limit value='{lower_limit:.3f}' must be within range {ANGLE_RESTRAINT_ERROR}.")

        if upper_limit is not None:
            if ANGLE_ERROR_MIN < upper_limit <= ANGLE_ERROR_MAX:
                dstFunc['upper_limit'] = f"{upper_limit:.3f}"
            else:
                validRange = False
                self.__f.append(f"[Range value error] {self.__getCurrentRestraint(n=index)}"
                                f"The upper limit value='{upper_limit:.3f}' must be within range {ANGLE_RESTRAINT_ERROR}.")

        if not validRange:
            return None

        if target_value is not None:
            if ANGLE_RANGE_MIN <= target_value <= ANGLE_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint(n=index)}"
                                f"The target value='{target_value}' should be within range {ANGLE_RESTRAINT_RANGE}.")

        if lower_limit is not None:
            if ANGLE_RANGE_MIN <= lower_limit <= ANGLE_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint(n=index)}"
                                f"The lower limit value='{lower_limit:.3f}' should be within range {ANGLE_RESTRAINT_RANGE}.")

        if upper_limit is not None:
            if ANGLE_RANGE_MIN <= upper_limit <= ANGLE_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint(n=index)}"
                                f"The upper limit value='{upper_limit:.3f}' should be within range {ANGLE_RESTRAINT_RANGE}.")

        if target_value is None and lower_limit is None and upper_limit is None:
            return None

        if None not in (upper_limit, lower_limit)\
           and (PLANE_LIKE_LOWER_LIMIT <= lower_limit < 0.0 < upper_limit <= PLANE_LIKE_UPPER_LIMIT
                or PLANE_LIKE_LOWER_LIMIT <= lower_limit - 180.0 < 0.0 < upper_limit - 180.0 <= PLANE_LIKE_UPPER_LIMIT
                or PLANE_LIKE_LOWER_LIMIT <= lower_limit - 360.0 < 0.0 < upper_limit - 360.0 <= PLANE_LIKE_UPPER_LIMIT):
            dstFunc['plane_like'] = True

        return dstFunc

    # Enter a parse tree produced by DynamoMRParser#rdc_restraints.
    def enterRdc_restraints(self, ctx: DynamoMRParser.Rdc_restraintsContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'rdc'

        self.closeSequqnce()

    # Exit a parse tree produced by DynamoMRParser#rdc_restraints.
    def exitRdc_restraints(self, ctx: DynamoMRParser.Rdc_restraintsContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by DynamoMRParser#rdc_restraint.
    def enterRdc_restraint(self, ctx: DynamoMRParser.Rdc_restraintContext):  # pylint: disable=unused-argument
        self.rdcRestraints += 1

        self.atomSelectionSet.clear()

    # Exit a parse tree produced by DynamoMRParser#rdc_restraint.
    def exitRdc_restraint(self, ctx: DynamoMRParser.Rdc_restraintContext):

        try:

            seqId1 = int(str(ctx.Integer(0)))
            compId1 = str(ctx.Simple_name(0)).upper()
            atomId1 = str(ctx.Simple_name(1)).upper()
            seqId2 = int(str(ctx.Integer(1)))
            compId2 = str(ctx.Simple_name(2)).upper()
            atomId2 = str(ctx.Simple_name(3)).upper()

            if len(self.numberSelection) == 0 or None in self.numberSelection:
                return

            target = self.numberSelection[0]
            error = abs(self.numberSelection[1])
            weight = self.numberSelection[2]

            if weight < 0.0:
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                f"The relative weight value of '{weight}' must not be a negative value.")
                return
            if weight == 0.0:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                f"The relative weight value of '{weight}' should be a positive value.")

            target_value = target
            lower_limit = target - error
            upper_limit = target + error

            dstFunc = self.validateRdcRange(weight, target_value, lower_limit, upper_limit)

            if dstFunc is None:
                return

            if not self.__hasPolySeq and not self.__hasNonPolySeq:
                return

            diffSeqId = seqId1 - seqId2

            self.__retrieveLocalSeqScheme()

            chainAssign1, asis1 = self.assignCoordPolymerSequence(None, seqId1, compId1, atomId1)
            chainAssign2, asis2 = self.assignCoordPolymerSequence(None, seqId2, compId2, atomId2)

            if 0 in (len(chainAssign1), len(chainAssign2)):
                return

            self.selectCoordAtoms(chainAssign1, seqId1, compId1, atomId1)
            self.selectCoordAtoms(chainAssign2, seqId2, compId2, atomId2)

            if len(self.atomSelectionSet) < 2:
                return
            """
            if not self.areUniqueCoordAtoms('an RDC'):
                return
            """
            try:
                chain_id_1 = self.atomSelectionSet[0][0]['chain_id']
                seq_id_1 = self.atomSelectionSet[0][0]['seq_id']
                comp_id_1 = self.atomSelectionSet[0][0]['comp_id']
                atom_id_1 = self.atomSelectionSet[0][0]['atom_id']

                chain_id_2 = self.atomSelectionSet[1][0]['chain_id']
                seq_id_2 = self.atomSelectionSet[1][0]['seq_id']
                comp_id_2 = self.atomSelectionSet[1][0]['comp_id']
                atom_id_2 = self.atomSelectionSet[1][0]['atom_id']
            except IndexError:
                self.areUniqueCoordAtoms('an RDC')
                return

            if self.__has_seq_align_err and seq_id_1 - seq_id_2 != diffSeqId:
                return

            if (atom_id_1[0] not in ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS) or (atom_id_2[0] not in ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS):
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                "Non-magnetic susceptible spin appears in RDC vector; "
                                f"({chain_id_1}:{seq_id_1}:{comp_id_1}:{atom_id_1}, "
                                f"{chain_id_2}:{seq_id_2}:{comp_id_2}:{atom_id_2}).")
                return

            if chain_id_1 != chain_id_2:
                ps1 = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == chain_id_1 and 'identical_auth_chain_id' in ps), None)
                ps2 = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == chain_id_2 and 'identical_auth_chain_id' in ps), None)
                if ps1 is None and ps2 is None:
                    self.__f.append(f"[Anomalous RDC vector] {self.__getCurrentRestraint()}"
                                    "Found inter-chain RDC vector; "
                                    f"({chain_id_1}:{seq_id_1}:{comp_id_1}:{atom_id_1}, {chain_id_2}:{seq_id_2}:{comp_id_2}:{atom_id_2}).")
                    return

            elif abs(seq_id_1 - seq_id_2) > 1:
                ps1 = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == chain_id_1 and 'gap_in_auth_seq' in ps and ps['gap_in_auth_seq']), None)
                if ps1 is None:
                    self.__f.append(f"[Anomalous RDC vector] {self.__getCurrentRestraint()}"
                                    "Found inter-residue RDC vector; "
                                    f"({chain_id_1}:{seq_id_1}:{comp_id_1}:{atom_id_1}, {chain_id_2}:{seq_id_2}:{comp_id_2}:{atom_id_2}).")
                    return

            elif abs(seq_id_1 - seq_id_2) == 1:

                if self.__csStat.peptideLike(comp_id_1) and self.__csStat.peptideLike(comp_id_2) and\
                        ((seq_id_1 < seq_id_2 and atom_id_1 == 'C' and atom_id_2 in rdcBbPairCode)
                         or (seq_id_1 > seq_id_2 and atom_id_1 in rdcBbPairCode and atom_id_2 == 'C')
                         or (seq_id_1 < seq_id_2 and atom_id_1.startswith('HA') and atom_id_2 == 'H')
                         or (seq_id_1 > seq_id_2 and atom_id_1 == 'H' and atom_id_2.startswith('HA'))):
                    pass

                else:
                    self.__f.append(f"[Anomalous RDC vector] {self.__getCurrentRestraint()}"
                                    "Found inter-residue RDC vector; "
                                    f"({chain_id_1}:{seq_id_1}:{comp_id_1}:{atom_id_1}, {chain_id_2}:{seq_id_2}:{comp_id_2}:{atom_id_2}).")
                    return

            elif atom_id_1 == atom_id_2:
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                "Found zero RDC vector; "
                                f"({chain_id_1}:{seq_id_1}:{comp_id_1}:{atom_id_1}, {chain_id_2}:{seq_id_2}:{comp_id_2}:{atom_id_2}).")
                return

            elif self.__ccU.updateChemCompDict(comp_id_1):  # matches with comp_id in CCD

                if not self.__ccU.hasBond(comp_id_1, atom_id_1, atom_id_2):

                    if self.__nefT.validate_comp_atom(comp_id_1, atom_id_1) and self.__nefT.validate_comp_atom(comp_id_2, atom_id_2):
                        self.__f.append(f"[Anomalous RDC vector] {self.__getCurrentRestraint()}"
                                        "Found an RDC vector over multiple covalent bonds; "
                                        f"({chain_id_1}:{seq_id_1}:{comp_id_1}:{atom_id_1}, {chain_id_2}:{seq_id_2}:{comp_id_2}:{atom_id_2}).")

            combinationId = '.'
            if self.__createSfDict:
                sf = self.__getSf(potentialType=getPotentialType(self.__file_type, self.__cur_subtype, dstFunc),
                                  rdcCode=getRdcCode([self.atomSelectionSet[0][0], self.atomSelectionSet[1][0]]),
                                  softwareName='DYNAMO/PALES')
                sf['id'] += 1
                if len(self.atomSelectionSet[0]) > 1 or len(self.atomSelectionSet[1]) > 1:
                    combinationId = 0

            for atom1, atom2 in itertools.product(self.atomSelectionSet[0],
                                                  self.atomSelectionSet[1]):
                atoms = [atom1, atom2]
                if isIdenticalRestraint(atoms, self.__nefT):
                    continue
                if isLongRangeRestraint(atoms, self.__polySeq if self.__gapInAuthSeq else None):
                    continue
                if isinstance(combinationId, int):
                    combinationId += 1
                if self.__debug:
                    print(f"subtype={self.__cur_subtype} id={self.rdcRestraints} "
                          f"atom1={atom1} atom2={atom2} {dstFunc}")
                if self.__createSfDict and sf is not None:
                    sf['index_id'] += 1
                    row = getRow(self.__cur_subtype, sf['id'], sf['index_id'],
                                 combinationId, None, None,
                                 sf['list_id'], self.__entryId, dstFunc,
                                 self.__authToStarSeq, self.__authToOrigSeq, self.__authToInsCode, self.__offsetHolder,
                                 atom1, atom2, asis1=asis1, asis2=asis2)
                    sf['loop'].add_data(row)

            if self.__createSfDict and sf is not None and isinstance(combinationId, int) and combinationId == 1:
                sf['loop'].data[-1] = resetCombinationId(self.__cur_subtype, sf['loop'].data[-1])

        except ValueError:
            self.rdcRestraints -= 1

        finally:
            self.numberSelection.clear()

    # Enter a parse tree produced by DynamoMRParser#rdc_restraints_sw_segid.
    def enterRdc_restraints_sw_segid(self, ctx: DynamoMRParser.Rdc_restraints_sw_segidContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'rdc'

        self.closeSequqnce()

    # Exit a parse tree produced by DynamoMRParser#rdc_restraints_sw_segid.
    def exitRdc_restraints_sw_segid(self, ctx: DynamoMRParser.Rdc_restraints_sw_segidContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by DynamoMRParser#rdc_restraint_sw_segid.
    def enterRdc_restraint_sw_segid(self, ctx: DynamoMRParser.Rdc_restraint_sw_segidContext):  # pylint: disable=unused-argument
        self.rdcRestraints += 1

        self.atomSelectionSet.clear()

    # Exit a parse tree produced by DynamoMRParser#rdc_restraint_sw_segid.
    def exitRdc_restraint_sw_segid(self, ctx: DynamoMRParser.Rdc_restraint_sw_segidContext):

        try:

            chainId1 = str(ctx.Simple_name(0))
            seqId1 = int(str(ctx.Integer(0)))
            compId1 = str(ctx.Simple_name(1)).upper()
            atomId1 = str(ctx.Simple_name(2)).upper()
            chainId2 = str(ctx.Simple_name(3))
            seqId2 = int(str(ctx.Integer(1)))
            compId2 = str(ctx.Simple_name(4)).upper()
            atomId2 = str(ctx.Simple_name(5)).upper()

            if len(self.numberSelection) == 0 or None in self.numberSelection:
                return

            target = self.numberSelection[0]
            error = abs(self.numberSelection[1])
            weight = self.numberSelection[2]

            if weight < 0.0:
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                f"The relative weight value of '{weight}' must not be a negative value.")
                return
            if weight == 0.0:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                f"The relative weight value of '{weight}' should be a positive value.")

            target_value = target
            lower_limit = target - error
            upper_limit = target + error

            dstFunc = self.validateRdcRange(weight, target_value, lower_limit, upper_limit)

            if dstFunc is None:
                return

            if not self.__hasPolySeq and not self.__hasNonPolySeq:
                return

            diffSeqId = seqId1 - seqId2

            self.__retrieveLocalSeqScheme()

            chainAssign1, asis1 = self.assignCoordPolymerSequence(chainId1, seqId1, compId1, atomId1)
            chainAssign2, asis2 = self.assignCoordPolymerSequence(chainId2, seqId2, compId2, atomId2)

            if 0 in (len(chainAssign1), len(chainAssign2)):
                return

            self.selectCoordAtoms(chainAssign1, seqId1, compId1, atomId1)
            self.selectCoordAtoms(chainAssign2, seqId2, compId2, atomId2)

            if len(self.atomSelectionSet) < 2:
                return
            """
            if not self.areUniqueCoordAtoms('an RDC'):
                return
            """
            try:
                chain_id_1 = self.atomSelectionSet[0][0]['chain_id']
                seq_id_1 = self.atomSelectionSet[0][0]['seq_id']
                comp_id_1 = self.atomSelectionSet[0][0]['comp_id']
                atom_id_1 = self.atomSelectionSet[0][0]['atom_id']

                chain_id_2 = self.atomSelectionSet[1][0]['chain_id']
                seq_id_2 = self.atomSelectionSet[1][0]['seq_id']
                comp_id_2 = self.atomSelectionSet[1][0]['comp_id']
                atom_id_2 = self.atomSelectionSet[1][0]['atom_id']
            except IndexError:
                self.areUniqueCoordAtoms('an RDC')
                return

            if self.__has_seq_align_err and seq_id_1 - seq_id_2 != diffSeqId:
                return

            if (atom_id_1[0] not in ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS) or (atom_id_2[0] not in ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS):
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                "Non-magnetic susceptible spin appears in RDC vector; "
                                f"({chain_id_1}:{seq_id_1}:{comp_id_1}:{atom_id_1}, "
                                f"{chain_id_2}:{seq_id_2}:{comp_id_2}:{atom_id_2}).")
                return

            if chain_id_1 != chain_id_2:
                ps1 = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == chain_id_1 and 'identical_auth_chain_id' in ps), None)
                ps2 = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == chain_id_2 and 'identical_auth_chain_id' in ps), None)
                if ps1 is None and ps2 is None:
                    self.__f.append(f"[Anomalous RDC vector] {self.__getCurrentRestraint()}"
                                    "Found inter-chain RDC vector; "
                                    f"({chain_id_1}:{seq_id_1}:{comp_id_1}:{atom_id_1}, {chain_id_2}:{seq_id_2}:{comp_id_2}:{atom_id_2}).")
                    return

            elif abs(seq_id_1 - seq_id_2) > 1:
                ps1 = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == chain_id_1 and 'gap_in_auth_seq' in ps and ps['gap_in_auth_seq']), None)
                if ps1 is None:
                    self.__f.append(f"[Anomalous RDC vector] {self.__getCurrentRestraint()}"
                                    "Found inter-residue RDC vector; "
                                    f"({chain_id_1}:{seq_id_1}:{comp_id_1}:{atom_id_1}, {chain_id_2}:{seq_id_2}:{comp_id_2}:{atom_id_2}).")
                    return

            elif abs(seq_id_1 - seq_id_2) == 1:

                if self.__csStat.peptideLike(comp_id_1) and self.__csStat.peptideLike(comp_id_2) and\
                        ((seq_id_1 < seq_id_2 and atom_id_1 == 'C' and atom_id_2 in rdcBbPairCode)
                         or (seq_id_1 > seq_id_2 and atom_id_1 in rdcBbPairCode and atom_id_2 == 'C')
                         or (seq_id_1 < seq_id_2 and atom_id_1.startswith('HA') and atom_id_2 == 'H')
                         or (seq_id_1 > seq_id_2 and atom_id_1 == 'H' and atom_id_2.startswith('HA'))):
                    pass

                else:
                    self.__f.append(f"[Anomalous RDC vector] {self.__getCurrentRestraint()}"
                                    "Found inter-residue RDC vector; "
                                    f"({chain_id_1}:{seq_id_1}:{comp_id_1}:{atom_id_1}, {chain_id_2}:{seq_id_2}:{comp_id_2}:{atom_id_2}).")
                    return

            elif atom_id_1 == atom_id_2:
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                "Found zero RDC vector; "
                                f"({chain_id_1}:{seq_id_1}:{comp_id_1}:{atom_id_1}, {chain_id_2}:{seq_id_2}:{comp_id_2}:{atom_id_2}).")
                return

            elif self.__ccU.updateChemCompDict(comp_id_1):  # matches with comp_id in CCD

                if not self.__ccU.hasBond(comp_id_1, atom_id_1, atom_id_2):

                    if self.__nefT.validate_comp_atom(comp_id_1, atom_id_1) and self.__nefT.validate_comp_atom(comp_id_2, atom_id_2):
                        self.__f.append(f"[Anomalous RDC vector] {self.__getCurrentRestraint()}"
                                        "Found an RDC vector over multiple covalent bonds; "
                                        f"({chain_id_1}:{seq_id_1}:{comp_id_1}:{atom_id_1}, {chain_id_2}:{seq_id_2}:{comp_id_2}:{atom_id_2}).")

            combinationId = '.'
            if self.__createSfDict:
                sf = self.__getSf(potentialType=getPotentialType(self.__file_type, self.__cur_subtype, dstFunc),
                                  rdcCode=getRdcCode([self.atomSelectionSet[0][0], self.atomSelectionSet[1][0]]),
                                  softwareName='DYNAMO/PALES')
                sf['id'] += 1
                if len(self.atomSelectionSet[0]) > 1 or len(self.atomSelectionSet[1]) > 1:
                    combinationId = 0

            for atom1, atom2 in itertools.product(self.atomSelectionSet[0],
                                                  self.atomSelectionSet[1]):
                atoms = [atom1, atom2]
                if isIdenticalRestraint(atoms, self.__nefT):
                    continue
                if isLongRangeRestraint(atoms, self.__polySeq if self.__gapInAuthSeq else None):
                    continue
                if isinstance(combinationId, int):
                    combinationId += 1
                if self.__debug:
                    print(f"subtype={self.__cur_subtype} id={self.rdcRestraints} "
                          f"atom1={atom1} atom2={atom2} {dstFunc}")
                if self.__createSfDict and sf is not None:
                    sf['index_id'] += 1
                    row = getRow(self.__cur_subtype, sf['id'], sf['index_id'],
                                 combinationId, None, None,
                                 sf['list_id'], self.__entryId, dstFunc,
                                 self.__authToStarSeq, self.__authToOrigSeq, self.__authToInsCode, self.__offsetHolder,
                                 atom1, atom2, asis1=asis1, asis2=asis2)
                    sf['loop'].add_data(row)

            if self.__createSfDict and sf is not None and isinstance(combinationId, int) and combinationId == 1:
                sf['loop'].data[-1] = resetCombinationId(self.__cur_subtype, sf['loop'].data[-1])

        except ValueError:
            self.rdcRestraints -= 1

        finally:
            self.numberSelection.clear()

    # Enter a parse tree produced by DynamoMRParser#rdc_restraints_ew_segid.
    def enterRdc_restraints_ew_segid(self, ctx: DynamoMRParser.Rdc_restraints_ew_segidContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'rdc'

        self.closeSequqnce()

    # Exit a parse tree produced by DynamoMRParser#rdc_restraints_ew_segid.
    def exitRdc_restraints_ew_segid(self, ctx: DynamoMRParser.Rdc_restraints_ew_segidContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by DynamoMRParser#rdc_restraint_ew_segid.
    def enterRdc_restraint_ew_segid(self, ctx: DynamoMRParser.Rdc_restraint_ew_segidContext):  # pylint: disable=unused-argument
        self.rdcRestraints += 1

        self.atomSelectionSet.clear()

    # Exit a parse tree produced by DynamoMRParser#rdc_restraint_ew_segid.
    def exitRdc_restraint_ew_segid(self, ctx: DynamoMRParser.Rdc_restraint_ew_segidContext):

        try:

            seqId1 = int(str(ctx.Integer(0)))
            compId1 = str(ctx.Simple_name(0)).upper()
            atomId1 = str(ctx.Simple_name(1)).upper()
            chainId1 = str(ctx.Simple_name(2))
            seqId2 = int(str(ctx.Integer(1)))
            compId2 = str(ctx.Simple_name(3)).upper()
            atomId2 = str(ctx.Simple_name(4)).upper()
            chainId2 = str(ctx.Simple_name(5))

            if len(self.numberSelection) == 0 or None in self.numberSelection:
                return

            target = self.numberSelection[0]
            error = abs(self.numberSelection[1])
            weight = self.numberSelection[2]

            if weight < 0.0:
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                f"The relative weight value of '{weight}' must not be a negative value.")
                return
            if weight == 0.0:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                f"The relative weight value of '{weight}' should be a positive value.")

            target_value = target
            lower_limit = target - error
            upper_limit = target + error

            dstFunc = self.validateRdcRange(weight, target_value, lower_limit, upper_limit)

            if dstFunc is None:
                return

            if not self.__hasPolySeq and not self.__hasNonPolySeq:
                return

            diffSeqId = seqId1 - seqId2

            self.__retrieveLocalSeqScheme()

            chainAssign1, asis1 = self.assignCoordPolymerSequence(chainId1, seqId1, compId1, atomId1)
            chainAssign2, asis2 = self.assignCoordPolymerSequence(chainId2, seqId2, compId2, atomId2)

            if 0 in (len(chainAssign1), len(chainAssign2)):
                return

            self.selectCoordAtoms(chainAssign1, seqId1, compId1, atomId1)
            self.selectCoordAtoms(chainAssign2, seqId2, compId2, atomId2)

            if len(self.atomSelectionSet) < 2:
                return
            """
            if not self.areUniqueCoordAtoms('an RDC'):
                return
            """
            try:
                chain_id_1 = self.atomSelectionSet[0][0]['chain_id']
                seq_id_1 = self.atomSelectionSet[0][0]['seq_id']
                comp_id_1 = self.atomSelectionSet[0][0]['comp_id']
                atom_id_1 = self.atomSelectionSet[0][0]['atom_id']

                chain_id_2 = self.atomSelectionSet[1][0]['chain_id']
                seq_id_2 = self.atomSelectionSet[1][0]['seq_id']
                comp_id_2 = self.atomSelectionSet[1][0]['comp_id']
                atom_id_2 = self.atomSelectionSet[1][0]['atom_id']
            except IndexError:
                self.areUniqueCoordAtoms('an RDC')
                return

            if self.__has_seq_align_err and seq_id_1 - seq_id_2 != diffSeqId:
                return

            if (atom_id_1[0] not in ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS) or (atom_id_2[0] not in ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS):
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                "Non-magnetic susceptible spin appears in RDC vector; "
                                f"({chain_id_1}:{seq_id_1}:{comp_id_1}:{atom_id_1}, "
                                f"{chain_id_2}:{seq_id_2}:{comp_id_2}:{atom_id_2}).")
                return

            if chain_id_1 != chain_id_2:
                ps1 = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == chain_id_1 and 'identical_auth_chain_id' in ps), None)
                ps2 = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == chain_id_2 and 'identical_auth_chain_id' in ps), None)
                if ps1 is None and ps2 is None:
                    self.__f.append(f"[Anomalous RDC vector] {self.__getCurrentRestraint()}"
                                    "Found inter-chain RDC vector; "
                                    f"({chain_id_1}:{seq_id_1}:{comp_id_1}:{atom_id_1}, {chain_id_2}:{seq_id_2}:{comp_id_2}:{atom_id_2}).")
                    return

            elif abs(seq_id_1 - seq_id_2) > 1:
                ps1 = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == chain_id_1 and 'gap_in_auth_seq' in ps and ps['gap_in_auth_seq']), None)
                if ps1 is None:
                    self.__f.append(f"[Anomalous RDC vector] {self.__getCurrentRestraint()}"
                                    "Found inter-residue RDC vector; "
                                    f"({chain_id_1}:{seq_id_1}:{comp_id_1}:{atom_id_1}, {chain_id_2}:{seq_id_2}:{comp_id_2}:{atom_id_2}).")
                    return

            elif abs(seq_id_1 - seq_id_2) == 1:

                if self.__csStat.peptideLike(comp_id_1) and self.__csStat.peptideLike(comp_id_2) and\
                        ((seq_id_1 < seq_id_2 and atom_id_1 == 'C' and atom_id_2 in rdcBbPairCode)
                         or (seq_id_1 > seq_id_2 and atom_id_1 in rdcBbPairCode and atom_id_2 == 'C')
                         or (seq_id_1 < seq_id_2 and atom_id_1.startswith('HA') and atom_id_2 == 'H')
                         or (seq_id_1 > seq_id_2 and atom_id_1 == 'H' and atom_id_2.startswith('HA'))):
                    pass

                else:
                    self.__f.append(f"[Anomalous RDC vector] {self.__getCurrentRestraint()}"
                                    "Found inter-residue RDC vector; "
                                    f"({chain_id_1}:{seq_id_1}:{comp_id_1}:{atom_id_1}, {chain_id_2}:{seq_id_2}:{comp_id_2}:{atom_id_2}).")
                    return

            elif atom_id_1 == atom_id_2:
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                "Found zero RDC vector; "
                                f"({chain_id_1}:{seq_id_1}:{comp_id_1}:{atom_id_1}, {chain_id_2}:{seq_id_2}:{comp_id_2}:{atom_id_2}).")
                return

            elif self.__ccU.updateChemCompDict(comp_id_1):  # matches with comp_id in CCD

                if not self.__ccU.hasBond(comp_id_1, atom_id_1, atom_id_2):

                    if self.__nefT.validate_comp_atom(comp_id_1, atom_id_1) and self.__nefT.validate_comp_atom(comp_id_2, atom_id_2):
                        self.__f.append(f"[Anomalous RDC vector] {self.__getCurrentRestraint()}"
                                        "Found an RDC vector over multiple covalent bonds; "
                                        f"({chain_id_1}:{seq_id_1}:{comp_id_1}:{atom_id_1}, {chain_id_2}:{seq_id_2}:{comp_id_2}:{atom_id_2}).")

            combinationId = '.'
            if self.__createSfDict:
                sf = self.__getSf(potentialType=getPotentialType(self.__file_type, self.__cur_subtype, dstFunc),
                                  rdcCode=getRdcCode([self.atomSelectionSet[0][0], self.atomSelectionSet[1][0]]),
                                  softwareName='DYNAMO/PALES')
                sf['id'] += 1
                if len(self.atomSelectionSet[0]) > 1 or len(self.atomSelectionSet[1]) > 1:
                    combinationId = 0

            for atom1, atom2 in itertools.product(self.atomSelectionSet[0],
                                                  self.atomSelectionSet[1]):
                atoms = [atom1, atom2]
                if isIdenticalRestraint(atoms, self.__nefT):
                    continue
                if isLongRangeRestraint(atoms, self.__polySeq if self.__gapInAuthSeq else None):
                    continue
                if isinstance(combinationId, int):
                    combinationId += 1
                if self.__debug:
                    print(f"subtype={self.__cur_subtype} id={self.rdcRestraints} "
                          f"atom1={atom1} atom2={atom2} {dstFunc}")
                if self.__createSfDict and sf is not None:
                    sf['index_id'] += 1
                    row = getRow(self.__cur_subtype, sf['id'], sf['index_id'],
                                 combinationId, None, None,
                                 sf['list_id'], self.__entryId, dstFunc,
                                 self.__authToStarSeq, self.__authToOrigSeq, self.__authToInsCode, self.__offsetHolder,
                                 atom1, atom2, asis1=asis1, asis2=asis2)
                    sf['loop'].add_data(row)

            if self.__createSfDict and sf is not None and isinstance(combinationId, int) and combinationId == 1:
                sf['loop'].data[-1] = resetCombinationId(self.__cur_subtype, sf['loop'].data[-1])

        except ValueError:
            self.rdcRestraints -= 1

        finally:
            self.numberSelection.clear()

    # Enter a parse tree produced by DynamoMRParser#pales_meta_outputs.
    def enterPales_meta_outputs(self, ctx: DynamoMRParser.Pales_meta_outputsContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by DynamoMRParser#pales_meta_outputs.
    def exitPales_meta_outputs(self, ctx: DynamoMRParser.Pales_meta_outputsContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by DynamoMRParser#pales_rdc_outputs.
    def enterPales_rdc_outputs(self, ctx: DynamoMRParser.Pales_rdc_outputsContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'rdc'

        self.closeSequqnce()

    # Exit a parse tree produced by DynamoMRParser#pales_rdc_outputs.
    def exitPales_rdc_outputs(self, ctx: DynamoMRParser.Pales_rdc_outputsContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by DynamoMRParser#pales_rdc_output.
    def enterPales_rdc_output(self, ctx: DynamoMRParser.Pales_rdc_outputContext):  # pylint: disable=unused-argument
        self.rdcRestraints += 1

        self.atomSelectionSet.clear()

    # Exit a parse tree produced by DynamoMRParser#pales_rdc_output.
    def exitPales_rdc_output(self, ctx: DynamoMRParser.Pales_rdc_outputContext):

        try:

            seqId1 = int(str(ctx.Integer(0)))
            compId1 = str(ctx.Simple_name(0)).upper()
            atomId1 = str(ctx.Simple_name(1)).upper()
            seqId2 = int(str(ctx.Integer(1)))
            compId2 = str(ctx.Simple_name(2)).upper()
            atomId2 = str(ctx.Simple_name(3)).upper()

            if len(self.numberSelection) == 0 or None in self.numberSelection:
                return

            # di
            target = self.numberSelection[1]  # d_obs
            # d (calc)
            # d_diff
            error = abs(self.numberSelection[4])
            weight = self.numberSelection[5]

            if weight < 0.0:
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                f"The relative weight value of '{weight}' must not be a negative value.")
                return
            if weight == 0.0:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                f"The relative weight value of '{weight}' should be a positive value.")

            target_value = target
            lower_limit = target - error
            upper_limit = target + error

            dstFunc = self.validateRdcRange(weight, target_value, lower_limit, upper_limit)

            if dstFunc is None:
                return

            if not self.__hasPolySeq and not self.__hasNonPolySeq:
                return

            diffSeqId = seqId1 - seqId2

            self.__retrieveLocalSeqScheme()

            chainAssign1, asis1 = self.assignCoordPolymerSequence(None, seqId1, compId1, atomId1)
            chainAssign2, asis2 = self.assignCoordPolymerSequence(None, seqId2, compId2, atomId2)

            if 0 in (len(chainAssign1), len(chainAssign2)):
                return

            self.selectCoordAtoms(chainAssign1, seqId1, compId1, atomId1)
            self.selectCoordAtoms(chainAssign2, seqId2, compId2, atomId2)

            if len(self.atomSelectionSet) < 2:
                return
            """
            if not self.areUniqueCoordAtoms('an RDC'):
                return
            """
            try:
                chain_id_1 = self.atomSelectionSet[0][0]['chain_id']
                seq_id_1 = self.atomSelectionSet[0][0]['seq_id']
                comp_id_1 = self.atomSelectionSet[0][0]['comp_id']
                atom_id_1 = self.atomSelectionSet[0][0]['atom_id']

                chain_id_2 = self.atomSelectionSet[1][0]['chain_id']
                seq_id_2 = self.atomSelectionSet[1][0]['seq_id']
                comp_id_2 = self.atomSelectionSet[1][0]['comp_id']
                atom_id_2 = self.atomSelectionSet[1][0]['atom_id']
            except IndexError:
                self.areUniqueCoordAtoms('an RDC')
                return

            if self.__has_seq_align_err and seq_id_1 - seq_id_2 != diffSeqId:
                return

            if (atom_id_1[0] not in ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS) or (atom_id_2[0] not in ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS):
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                "Non-magnetic susceptible spin appears in RDC vector; "
                                f"({chain_id_1}:{seq_id_1}:{comp_id_1}:{atom_id_1}, "
                                f"{chain_id_2}:{seq_id_2}:{comp_id_2}:{atom_id_2}).")
                return

            if chain_id_1 != chain_id_2:
                ps1 = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == chain_id_1 and 'identical_auth_chain_id' in ps), None)
                ps2 = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == chain_id_2 and 'identical_auth_chain_id' in ps), None)
                if ps1 is None and ps2 is None:
                    self.__f.append(f"[Anomalous RDC vector] {self.__getCurrentRestraint()}"
                                    "Found inter-chain RDC vector; "
                                    f"({chain_id_1}:{seq_id_1}:{comp_id_1}:{atom_id_1}, {chain_id_2}:{seq_id_2}:{comp_id_2}:{atom_id_2}).")
                    return

            elif abs(seq_id_1 - seq_id_2) > 1:
                ps1 = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == chain_id_1 and 'gap_in_auth_seq' in ps and ps['gap_in_auth_seq']), None)
                if ps1 is None:
                    self.__f.append(f"[Anomalous RDC vector] {self.__getCurrentRestraint()}"
                                    "Found inter-residue RDC vector; "
                                    f"({chain_id_1}:{seq_id_1}:{comp_id_1}:{atom_id_1}, {chain_id_2}:{seq_id_2}:{comp_id_2}:{atom_id_2}).")
                    return

            elif abs(seq_id_1 - seq_id_2) == 1:

                if self.__csStat.peptideLike(comp_id_1) and self.__csStat.peptideLike(comp_id_2) and\
                        ((seq_id_1 < seq_id_2 and atom_id_1 == 'C' and atom_id_2 in rdcBbPairCode)
                         or (seq_id_1 > seq_id_2 and atom_id_1 in rdcBbPairCode and atom_id_2 == 'C')
                         or (seq_id_1 < seq_id_2 and atom_id_1.startswith('HA') and atom_id_2 == 'H')
                         or (seq_id_1 > seq_id_2 and atom_id_1 == 'H' and atom_id_2.startswith('HA'))):
                    pass

                else:
                    self.__f.append(f"[Anomalous RDC vector] {self.__getCurrentRestraint()}"
                                    "Found inter-residue RDC vector; "
                                    f"({chain_id_1}:{seq_id_1}:{comp_id_1}:{atom_id_1}, {chain_id_2}:{seq_id_2}:{comp_id_2}:{atom_id_2}).")
                    return

            elif atom_id_1 == atom_id_2:
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                "Found zero RDC vector; "
                                f"({chain_id_1}:{seq_id_1}:{comp_id_1}:{atom_id_1}, {chain_id_2}:{seq_id_2}:{comp_id_2}:{atom_id_2}).")
                return

            elif self.__ccU.updateChemCompDict(comp_id_1):  # matches with comp_id in CCD

                if not self.__ccU.hasBond(comp_id_1, atom_id_1, atom_id_2):

                    if self.__nefT.validate_comp_atom(comp_id_1, atom_id_1) and self.__nefT.validate_comp_atom(comp_id_2, atom_id_2):
                        self.__f.append(f"[Anomalous RDC vector] {self.__getCurrentRestraint()}"
                                        "Found an RDC vector over multiple covalent bonds; "
                                        f"({chain_id_1}:{seq_id_1}:{comp_id_1}:{atom_id_1}, {chain_id_2}:{seq_id_2}:{comp_id_2}:{atom_id_2}).")

            combinationId = '.'
            if self.__createSfDict:
                sf = self.__getSf(potentialType=getPotentialType(self.__file_type, self.__cur_subtype, dstFunc),
                                  rdcCode=getRdcCode([self.atomSelectionSet[0][0], self.atomSelectionSet[1][0]]),
                                  softwareName='PALES')
                sf['id'] += 1
                if len(self.atomSelectionSet[0]) > 1 or len(self.atomSelectionSet[1]) > 1:
                    combinationId = 0

            for atom1, atom2 in itertools.product(self.atomSelectionSet[0],
                                                  self.atomSelectionSet[1]):
                atoms = [atom1, atom2]
                if isIdenticalRestraint(atoms, self.__nefT):
                    continue
                if isLongRangeRestraint(atoms, self.__polySeq if self.__gapInAuthSeq else None):
                    continue
                if isinstance(combinationId, int):
                    combinationId += 1
                if self.__debug:
                    print(f"subtype={self.__cur_subtype} id={self.rdcRestraints} "
                          f"atom1={atom1} atom2={atom2} {dstFunc}")
                if self.__createSfDict and sf is not None:
                    sf['index_id'] += 1
                    row = getRow(self.__cur_subtype, sf['id'], sf['index_id'],
                                 combinationId, None, None,
                                 sf['list_id'], self.__entryId, dstFunc,
                                 self.__authToStarSeq, self.__authToOrigSeq, self.__authToInsCode, self.__offsetHolder,
                                 atom1, atom2, asis1=asis1, asis2=asis2)
                    sf['loop'].add_data(row)

            if self.__createSfDict and sf is not None and isinstance(combinationId, int) and combinationId == 1:
                sf['loop'].data[-1] = resetCombinationId(self.__cur_subtype, sf['loop'].data[-1])

        except ValueError:
            self.rdcRestraints -= 1

        finally:
            self.numberSelection.clear()

    def validateRdcRange(self, weight: float, target_value: Optional[float],
                         lower_limit: Optional[float], upper_limit: Optional[float]) -> Optional[dict]:
        """ Validate RDC value range.
        """

        validRange = True
        dstFunc = {'weight': weight}

        if target_value is not None:
            if RDC_ERROR_MIN < target_value < RDC_ERROR_MAX:
                dstFunc['target_value'] = f"{target_value}"
            else:
                validRange = False
                self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                f"The target value='{target_value}' must be within range {RDC_RESTRAINT_ERROR}.")

        if lower_limit is not None:
            if RDC_ERROR_MIN <= lower_limit < RDC_ERROR_MAX:
                dstFunc['lower_limit'] = f"{lower_limit:.6f}"
            else:
                validRange = False
                self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                f"The lower limit value='{lower_limit:.6f}' must be within range {RDC_RESTRAINT_ERROR}.")

        if upper_limit is not None:
            if RDC_ERROR_MIN < upper_limit <= RDC_ERROR_MAX:
                dstFunc['upper_limit'] = f"{upper_limit:.6f}"
            else:
                validRange = False
                self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                f"The upper limit value='{upper_limit:.6f}' must be within range {RDC_RESTRAINT_ERROR}.")

        if target_value is not None:

            if lower_limit is not None:
                if lower_limit > target_value:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                    f"The lower limit value='{lower_limit:.6f}' must be less than the target value '{target_value}'.")

            if upper_limit is not None:
                if upper_limit < target_value:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                    f"The upper limit value='{upper_limit:.6f}' must be greater than the target value '{target_value}'.")

        if not validRange:
            return None

        if target_value is not None:
            if RDC_RANGE_MIN <= target_value <= RDC_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                f"The target value='{target_value}' should be within range {RDC_RESTRAINT_RANGE}.")

        if lower_limit is not None:
            if RDC_RANGE_MIN <= lower_limit <= RDC_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                f"The lower limit value='{lower_limit:.6f}' should be within range {RDC_RESTRAINT_RANGE}.")

        if upper_limit is not None:
            if RDC_RANGE_MIN <= upper_limit <= RDC_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                f"The upper limit value='{upper_limit:.6f}' should be within range {RDC_RESTRAINT_RANGE}.")

        if target_value is None and lower_limit is None and upper_limit is None:
            return None

        return dstFunc

    def areUniqueCoordAtoms(self, subtype_name: str, allow_ambig: bool = False, allow_ambig_warn_title: str = '') -> bool:
        """ Check whether atom selection sets are uniquely assigned.
        """

        for _atomSelectionSet in self.atomSelectionSet:
            _lenAtomSelectionSet = len(_atomSelectionSet)

            if _lenAtomSelectionSet == 0:
                return False  # raised error already

            if _lenAtomSelectionSet == 1:
                continue

            for (atom1, atom2) in itertools.combinations(_atomSelectionSet, 2):
                if atom1['chain_id'] != atom2['chain_id']:
                    continue
                if atom1['seq_id'] != atom2['seq_id']:
                    continue
                if allow_ambig:
                    self.__f.append(f"[{allow_ambig_warn_title}] {self.__getCurrentRestraint()}"
                                    f"Ambiguous atom selection '{atom1['chain_id']}:{atom1['seq_id']}:{atom1['comp_id']}:{atom1['atom_id']} or "
                                    f"{atom2['atom_id']}' found in {subtype_name} restraint.")
                    continue
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                f"Ambiguous atom selection '{atom1['chain_id']}:{atom1['seq_id']}:{atom1['comp_id']}:{atom1['atom_id']} or "
                                f"{atom2['atom_id']}' is not allowed as {subtype_name} restraint.")
                return False

        return True

    # Enter a parse tree produced by DynamoMRParser#coupling_restraints.
    def enterCoupling_restraints(self, ctx: DynamoMRParser.Coupling_restraintsContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'jcoup'

        self.closeSequqnce()

    # Exit a parse tree produced by DynamoMRParser#coupling_restraints.
    def exitCoupling_restraints(self, ctx: DynamoMRParser.Coupling_restraintsContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by DynamoMRParser#coupling_restraint.
    def enterCoupling_restraint(self, ctx: DynamoMRParser.Coupling_restraintContext):  # pylint: disable=unused-argument
        self.jcoupRestraints += 1

        self.atomSelectionSet.clear()

    # Exit a parse tree produced by DynamoMRParser#coupling_restraint.
    def exitCoupling_restraint(self, ctx: DynamoMRParser.Coupling_restraintContext):

        try:

            index = int(str(ctx.Integer(0)))

            seqId1 = int(str(ctx.Integer(1)))
            compId1 = str(ctx.Simple_name(0)).upper()
            atomId1 = str(ctx.Simple_name(1)).upper()
            seqId2 = int(str(ctx.Integer(2)))
            compId2 = str(ctx.Simple_name(2)).upper()
            atomId2 = str(ctx.Simple_name(3)).upper()
            seqId3 = int(str(ctx.Integer(3)))
            compId3 = str(ctx.Simple_name(4)).upper()
            atomId3 = str(ctx.Simple_name(5)).upper()
            seqId4 = int(str(ctx.Integer(4)))
            compId4 = str(ctx.Simple_name(6)).upper()
            atomId4 = str(ctx.Simple_name(7)).upper()

            if len(self.numberSelection) == 0 or None in self.numberSelection:
                return

            A = self.numberSelection[0]
            B = self.numberSelection[1]
            C = self.numberSelection[2]
            phase = self.numberSelection[3]
            target_value = self.numberSelection[4]
            lower_limit = upper_limit = None
            # fource_const = self.numberSelection[5]

            dstFunc = self.validateCoupRange(index, 1.0, target_value, lower_limit, upper_limit)

            if dstFunc is None:
                return

            if not self.__hasPolySeq and not self.__hasNonPolySeq:
                return

            self.__retrieveLocalSeqScheme()

            chainAssign1, asis1 = self.assignCoordPolymerSequence(None, seqId1, compId1, atomId1, index)
            chainAssign2, asis2 = self.assignCoordPolymerSequence(None, seqId2, compId2, atomId2, index)
            chainAssign3, asis3 = self.assignCoordPolymerSequence(None, seqId3, compId3, atomId3, index)
            chainAssign4, asis4 = self.assignCoordPolymerSequence(None, seqId4, compId4, atomId4, index)

            if 0 in (len(chainAssign1), len(chainAssign2), len(chainAssign3), len(chainAssign4)):
                return

            self.selectCoordAtoms(chainAssign1, seqId1, compId1, atomId1, False)
            self.selectCoordAtoms(chainAssign2, seqId2, compId2, atomId2, False)
            self.selectCoordAtoms(chainAssign3, seqId3, compId3, atomId3, False)
            self.selectCoordAtoms(chainAssign4, seqId4, compId4, atomId4, False)

            if len(self.atomSelectionSet) < 4:
                return

            if not self.areUniqueCoordAtoms('a scalar coupling'):
                return

            sf = None
            if self.__createSfDict:
                sf = self.__getSf(constraintType='backbone chemical shifts',
                                  potentialType=getPotentialType(self.__file_type, self.__cur_subtype, dstFunc),
                                  softwareName='DYNAMO')

            compId = self.atomSelectionSet[0][0]['comp_id']
            peptide, nucleotide, carbohydrate = self.__csStat.getTypeOfCompId(compId)

            first_item = True

            atomSelTotal = sum(len(s) for s in self.atomSelectionSet)

            for atom1, atom2, atom3, atom4 in itertools.product(self.atomSelectionSet[0],
                                                                self.atomSelectionSet[1],
                                                                self.atomSelectionSet[2],
                                                                self.atomSelectionSet[3]):
                atoms = [atom1, atom2, atom3, atom4]
                angleName = getTypeOfDihedralRestraint(peptide, nucleotide, carbohydrate,
                                                       atoms,
                                                       'plane_like' in dstFunc,
                                                       self.__cR, self.__ccU,
                                                       self.__representativeModelId, self.__representativeAltId, self.__modelNumName)

                if angleName is not None and angleName.startswith('pseudo'):
                    angleName, atom2, atom3, err = fixBackboneAtomsOfDihedralRestraint(angleName,
                                                                                       atoms,
                                                                                       self.__getCurrentRestraint(n=index))
                    self.__f.append(err)

                if angleName in emptyValue and atomSelTotal != 4:
                    continue

                if angleName == 'PHI':
                    self.auxAtomSelectionSet.clear()
                    self.selectAuxCoordAtoms(chainAssign2, seqId2, compId2, 'H', False)
                    self.selectAuxCoordAtoms(chainAssign2, seqId2, compId2, 'N', False)
                    self.selectAuxCoordAtoms(chainAssign3, seqId3, compId3, 'CA', False)
                    self.selectAuxCoordAtoms(chainAssign3, seqId3, compId3, 'HA', False)
                if self.__debug:
                    if angleName == 'PHI':
                        if len(self.auxAtomSelectionSet) == 2:
                            print(f"subtype={self.__cur_subtype} id={self.jcoupRestraints} (index={index}) angleName={angleName} "
                                  f"A={A} B={B} C={C} phase={phase} "
                                  f"atom1={self.auxAtomSelectionSet[0][0]} atom2={self.auxAtomSelectionSet[1][0]} "
                                  f"atom1={self.auxAtomSelectionSet[2][0]} atom2={self.auxAtomSelectionSet[3][0]} {dstFunc}")
                    else:
                        print(f"subtype={self.__cur_subtype} id={self.jcoupRestraints} (index={index}) angleName={angleName} "
                              f"A={A} B={B} C={C} phase={phase} "
                              f"atom1={atom1} atom2={atom2} atom3={atom3} atom4={atom4} {dstFunc}")
                if self.__createSfDict and sf is not None:
                    if first_item:
                        sf['id'] += 1
                        first_item = False
                    if angleName == 'PHI':
                        if len(self.auxAtomSelectionSet) == 4:
                            sf['index_id'] += 1
                            row = getRow(self.__cur_subtype, sf['id'], sf['index_id'],
                                         '.', None, None,
                                         sf['list_id'], self.__entryId, dstFunc,
                                         self.__authToStarSeq, self.__authToOrigSeq, self.__authToInsCode, self.__offsetHolder,
                                         self.auxAtomSelectionSet[0][0], self.auxAtomSelectionSet[1][0],
                                         self.auxAtomSelectionSet[2][0], self.auxAtomSelectionSet[3][0])
                            sf['loop'].add_data(row)
                    else:
                        sf['index_id'] += 1
                        row = getRow(self.__cur_subtype, sf['id'], sf['index_id'],
                                     '.', None, None,
                                     sf['list_id'], self.__entryId, dstFunc,
                                     self.__authToStarSeq, self.__authToOrigSeq, self.__authToInsCode, self.__offsetHolder,
                                     atom1, atom2, atom3, atom4, asis1=asis1, asis2=asis2, asis3=asis3, asis4=asis4)
                        sf['loop'].add_data(row)

        except ValueError:
            self.jcoupRestraints -= 1

        finally:
            self.numberSelection.clear()

    # Enter a parse tree produced by DynamoMRParser#coupling_restraints_sw_segid.
    def enterCoupling_restraints_sw_segid(self, ctx: DynamoMRParser.Coupling_restraints_sw_segidContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'jcoup'

        self.closeSequqnce()

    # Exit a parse tree produced by DynamoMRParser#coupling_restraints_sw_segid.
    def exitCoupling_restraints_sw_segid(self, ctx: DynamoMRParser.Coupling_restraints_sw_segidContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by DynamoMRParser#coupling_restraint_sw_segid.
    def enterCoupling_restraint_sw_segid(self, ctx: DynamoMRParser.Coupling_restraint_sw_segidContext):  # pylint: disable=unused-argument
        self.jcoupRestraints += 1

        self.atomSelectionSet.clear()

    # Exit a parse tree produced by DynamoMRParser#coupling_restraint_sw_segid.
    def exitCoupling_restraint_sw_segid(self, ctx: DynamoMRParser.Coupling_restraint_sw_segidContext):

        try:

            index = int(str(ctx.Integer(0)))

            chainId1 = str(ctx.Simple_name(0))
            seqId1 = int(str(ctx.Integer(1)))
            compId1 = str(ctx.Simple_name(1)).upper()
            atomId1 = str(ctx.Simple_name(2)).upper()
            chainId2 = str(ctx.Simple_name(3))
            seqId2 = int(str(ctx.Integer(2)))
            compId2 = str(ctx.Simple_name(4)).upper()
            atomId2 = str(ctx.Simple_name(5)).upper()
            chainId3 = str(ctx.Simple_name(6))
            seqId3 = int(str(ctx.Integer(3)))
            compId3 = str(ctx.Simple_name(7)).upper()
            atomId3 = str(ctx.Simple_name(8)).upper()
            chainId4 = str(ctx.Simple_name(9))
            seqId4 = int(str(ctx.Integer(4)))
            compId4 = str(ctx.Simple_name(10)).upper()
            atomId4 = str(ctx.Simple_name(11)).upper()

            if len(self.numberSelection) == 0 or None in self.numberSelection:
                return

            A = self.numberSelection[0]
            B = self.numberSelection[1]
            C = self.numberSelection[2]
            phase = self.numberSelection[3]
            target_value = self.numberSelection[4]
            lower_limit = upper_limit = None
            # fource_const = self.numberSelection[5]

            dstFunc = self.validateCoupRange(index, 1.0, target_value, lower_limit, upper_limit)

            if dstFunc is None:
                return

            if not self.__hasPolySeq and not self.__hasNonPolySeq:
                return

            self.__retrieveLocalSeqScheme()

            chainAssign1, asis1 = self.assignCoordPolymerSequence(chainId1, seqId1, compId1, atomId1, index)
            chainAssign2, asis2 = self.assignCoordPolymerSequence(chainId2, seqId2, compId2, atomId2, index)
            chainAssign3, asis3 = self.assignCoordPolymerSequence(chainId3, seqId3, compId3, atomId3, index)
            chainAssign4, asis4 = self.assignCoordPolymerSequence(chainId4, seqId4, compId4, atomId4, index)

            if 0 in (len(chainAssign1), len(chainAssign2), len(chainAssign3), len(chainAssign4)):
                return

            self.selectCoordAtoms(chainAssign1, seqId1, compId1, atomId1, False)
            self.selectCoordAtoms(chainAssign2, seqId2, compId2, atomId2, False)
            self.selectCoordAtoms(chainAssign3, seqId3, compId3, atomId3, False)
            self.selectCoordAtoms(chainAssign4, seqId4, compId4, atomId4, False)

            if len(self.atomSelectionSet) < 4:
                return

            if not self.areUniqueCoordAtoms('a scalar coupling'):
                return

            sf = None
            if self.__createSfDict:
                sf = self.__getSf(constraintType='backbone chemical shifts',
                                  potentialType=getPotentialType(self.__file_type, self.__cur_subtype, dstFunc),
                                  softwareName='DYNAMO')

            compId = self.atomSelectionSet[0][0]['comp_id']
            peptide, nucleotide, carbohydrate = self.__csStat.getTypeOfCompId(compId)

            first_item = True

            atomSelTotal = sum(len(s) for s in self.atomSelectionSet)

            for atom1, atom2, atom3, atom4 in itertools.product(self.atomSelectionSet[0],
                                                                self.atomSelectionSet[1],
                                                                self.atomSelectionSet[2],
                                                                self.atomSelectionSet[3]):
                atoms = [atom1, atom2, atom3, atom4]
                angleName = getTypeOfDihedralRestraint(peptide, nucleotide, carbohydrate,
                                                       atoms,
                                                       'plane_like' in dstFunc,
                                                       self.__cR, self.__ccU,
                                                       self.__representativeModelId, self.__representativeAltId, self.__modelNumName)

                if angleName is not None and angleName.startswith('pseudo'):
                    angleName, atom2, atom3, err = fixBackboneAtomsOfDihedralRestraint(angleName,
                                                                                       atoms,
                                                                                       self.__getCurrentRestraint(n=index))
                    self.__f.append(err)

                if angleName in emptyValue and atomSelTotal != 4:
                    continue

                if angleName == 'PHI':
                    self.auxAtomSelectionSet.clear()
                    self.selectAuxCoordAtoms(chainAssign2, seqId2, compId2, 'H', False)
                    self.selectAuxCoordAtoms(chainAssign2, seqId2, compId2, 'N', False)
                    self.selectAuxCoordAtoms(chainAssign3, seqId3, compId3, 'CA', False)
                    self.selectAuxCoordAtoms(chainAssign3, seqId3, compId3, 'HA', False)
                if self.__debug:
                    if angleName == 'PHI':
                        if len(self.auxAtomSelectionSet) == 2:
                            print(f"subtype={self.__cur_subtype} id={self.jcoupRestraints} (index={index}) angleName={angleName} "
                                  f"A={A} B={B} C={C} phase={phase} "
                                  f"atom1={self.auxAtomSelectionSet[0][0]} atom2={self.auxAtomSelectionSet[1][0]} "
                                  f"atom1={self.auxAtomSelectionSet[2][0]} atom2={self.auxAtomSelectionSet[3][0]} {dstFunc}")
                    else:
                        print(f"subtype={self.__cur_subtype} id={self.jcoupRestraints} (index={index}) angleName={angleName} "
                              f"A={A} B={B} C={C} phase={phase} "
                              f"atom1={atom1} atom2={atom2} atom3={atom3} atom4={atom4} {dstFunc}")
                if self.__createSfDict and sf is not None:
                    if first_item:
                        sf['id'] += 1
                        first_item = False
                    if angleName == 'PHI':
                        if len(self.auxAtomSelectionSet) == 4:
                            sf['index_id'] += 1
                            row = getRow(self.__cur_subtype, sf['id'], sf['index_id'],
                                         '.', None, None,
                                         sf['list_id'], self.__entryId, dstFunc,
                                         self.__authToStarSeq, self.__authToOrigSeq, self.__authToInsCode, self.__offsetHolder,
                                         self.auxAtomSelectionSet[0][0], self.auxAtomSelectionSet[1][0],
                                         self.auxAtomSelectionSet[2][0], self.auxAtomSelectionSet[3][0])
                            sf['loop'].add_data(row)
                    else:
                        sf['index_id'] += 1
                        row = getRow(self.__cur_subtype, sf['id'], sf['index_id'],
                                     '.', None, None,
                                     sf['list_id'], self.__entryId, dstFunc,
                                     self.__authToStarSeq, self.__authToOrigSeq, self.__authToInsCode, self.__offsetHolder,
                                     atom1, atom2, atom3, atom4, asis1=asis1, asis2=asis2, asis3=asis3, asis4=asis4)
                        sf['loop'].add_data(row)

        except ValueError:
            self.jcoupRestraints -= 1

        finally:
            self.numberSelection.clear()

    # Enter a parse tree produced by DynamoMRParser#coupling_restraints_ew_segid.
    def enterCoupling_restraints_ew_segid(self, ctx: DynamoMRParser.Coupling_restraints_ew_segidContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'jcoup'

        self.closeSequqnce()

    # Exit a parse tree produced by DynamoMRParser#coupling_restraints_ew_segid.
    def exitCoupling_restraints_ew_segid(self, ctx: DynamoMRParser.Coupling_restraints_ew_segidContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by DynamoMRParser#coupling_restraint_ew_segid.
    def enterCoupling_restraint_ew_segid(self, ctx: DynamoMRParser.Coupling_restraint_ew_segidContext):  # pylint: disable=unused-argument
        self.jcoupRestraints += 1

        self.atomSelectionSet.clear()

    # Exit a parse tree produced by DynamoMRParser#coupling_restraint_ew_segid.
    def exitCoupling_restraint_ew_segid(self, ctx: DynamoMRParser.Coupling_restraint_ew_segidContext):

        try:

            index = int(str(ctx.Integer(0)))

            seqId1 = int(str(ctx.Integer(1)))
            compId1 = str(ctx.Simple_name(0)).upper()
            atomId1 = str(ctx.Simple_name(1)).upper()
            chainId1 = str(ctx.Simple_name(2))
            seqId2 = int(str(ctx.Integer(2)))
            compId2 = str(ctx.Simple_name(3)).upper()
            atomId2 = str(ctx.Simple_name(4)).upper()
            chainId2 = str(ctx.Simple_name(5))
            seqId3 = int(str(ctx.Integer(3)))
            compId3 = str(ctx.Simple_name(6)).upper()
            atomId3 = str(ctx.Simple_name(7)).upper()
            chainId3 = str(ctx.Simple_name(8))
            seqId4 = int(str(ctx.Integer(4)))
            compId4 = str(ctx.Simple_name(9)).upper()
            atomId4 = str(ctx.Simple_name(10)).upper()
            chainId4 = str(ctx.Simple_name(11))

            if len(self.numberSelection) == 0 or None in self.numberSelection:
                return

            A = self.numberSelection[0]
            B = self.numberSelection[1]
            C = self.numberSelection[2]
            phase = self.numberSelection[3]
            target_value = self.numberSelection[4]
            lower_limit = upper_limit = None
            # fource_const = self.numberSelection[5]

            dstFunc = self.validateCoupRange(index, 1.0, target_value, lower_limit, upper_limit)

            if dstFunc is None:
                return

            if not self.__hasPolySeq and not self.__hasNonPolySeq:
                return

            self.__retrieveLocalSeqScheme()

            chainAssign1, asis1 = self.assignCoordPolymerSequence(chainId1, seqId1, compId1, atomId1, index)
            chainAssign2, asis2 = self.assignCoordPolymerSequence(chainId2, seqId2, compId2, atomId2, index)
            chainAssign3, asis3 = self.assignCoordPolymerSequence(chainId3, seqId3, compId3, atomId3, index)
            chainAssign4, asis4 = self.assignCoordPolymerSequence(chainId4, seqId4, compId4, atomId4, index)

            if 0 in (len(chainAssign1), len(chainAssign2), len(chainAssign3), len(chainAssign4)):
                return

            self.selectCoordAtoms(chainAssign1, seqId1, compId1, atomId1, False)
            self.selectCoordAtoms(chainAssign2, seqId2, compId2, atomId2, False)
            self.selectCoordAtoms(chainAssign3, seqId3, compId3, atomId3, False)
            self.selectCoordAtoms(chainAssign4, seqId4, compId4, atomId4, False)

            if len(self.atomSelectionSet) < 4:
                return

            if not self.areUniqueCoordAtoms('a scalar coupling'):
                return

            sf = None
            if self.__createSfDict:
                sf = self.__getSf(constraintType='backbone chemical shifts',
                                  potentialType=getPotentialType(self.__file_type, self.__cur_subtype, dstFunc),
                                  softwareName='DYNAMO')

            compId = self.atomSelectionSet[0][0]['comp_id']
            peptide, nucleotide, carbohydrate = self.__csStat.getTypeOfCompId(compId)

            first_item = True

            atomSelTotal = sum(len(s) for s in self.atomSelectionSet)

            for atom1, atom2, atom3, atom4 in itertools.product(self.atomSelectionSet[0],
                                                                self.atomSelectionSet[1],
                                                                self.atomSelectionSet[2],
                                                                self.atomSelectionSet[3]):
                atoms = [atom1, atom2, atom3, atom4]
                angleName = getTypeOfDihedralRestraint(peptide, nucleotide, carbohydrate,
                                                       atoms,
                                                       'plane_like' in dstFunc,
                                                       self.__cR, self.__ccU,
                                                       self.__representativeModelId, self.__representativeAltId, self.__modelNumName)

                if angleName is not None and angleName.startswith('pseudo'):
                    angleName, atom2, atom3, err = fixBackboneAtomsOfDihedralRestraint(angleName,
                                                                                       atoms,
                                                                                       self.__getCurrentRestraint(n=index))
                    self.__f.append(err)

                if angleName in emptyValue and atomSelTotal != 4:
                    continue

                if angleName == 'PHI':
                    self.auxAtomSelectionSet.clear()
                    self.selectAuxCoordAtoms(chainAssign2, seqId2, compId2, 'H', False)
                    self.selectAuxCoordAtoms(chainAssign2, seqId2, compId2, 'N', False)
                    self.selectAuxCoordAtoms(chainAssign3, seqId3, compId3, 'CA', False)
                    self.selectAuxCoordAtoms(chainAssign3, seqId3, compId3, 'HA', False)
                if self.__debug:
                    if angleName == 'PHI':
                        if len(self.auxAtomSelectionSet) == 2:
                            print(f"subtype={self.__cur_subtype} id={self.jcoupRestraints} (index={index}) angleName={angleName} "
                                  f"A={A} B={B} C={C} phase={phase} "
                                  f"atom1={self.auxAtomSelectionSet[0][0]} atom2={self.auxAtomSelectionSet[1][0]} "
                                  f"atom1={self.auxAtomSelectionSet[2][0]} atom2={self.auxAtomSelectionSet[3][0]} {dstFunc}")
                    else:
                        print(f"subtype={self.__cur_subtype} id={self.jcoupRestraints} (index={index}) angleName={angleName} "
                              f"A={A} B={B} C={C} phase={phase} "
                              f"atom1={atom1} atom2={atom2} atom3={atom3} atom4={atom4} {dstFunc}")
                if self.__createSfDict and sf is not None:
                    if first_item:
                        sf['id'] += 1
                        first_item = False
                    if angleName == 'PHI':
                        if len(self.auxAtomSelectionSet) == 4:
                            sf['index_id'] += 1
                            row = getRow(self.__cur_subtype, sf['id'], sf['index_id'],
                                         '.', None, None,
                                         sf['list_id'], self.__entryId, dstFunc,
                                         self.__authToStarSeq, self.__authToOrigSeq, self.__authToInsCode, self.__offsetHolder,
                                         self.auxAtomSelectionSet[0][0], self.auxAtomSelectionSet[1][0],
                                         self.auxAtomSelectionSet[2][0], self.auxAtomSelectionSet[3][0])
                            sf['loop'].add_data(row)
                    else:
                        sf['index_id'] += 1
                        row = getRow(self.__cur_subtype, sf['id'], sf['index_id'],
                                     '.', None, None,
                                     sf['list_id'], self.__entryId, dstFunc,
                                     self.__authToStarSeq, self.__authToOrigSeq, self.__authToInsCode, self.__offsetHolder,
                                     atom1, atom2, atom3, atom4, asis1=asis1, asis2=asis2, asis3=asis3, asis4=asis4)
                        sf['loop'].add_data(row)

        except ValueError:
            self.jcoupRestraints -= 1

        finally:
            self.numberSelection.clear()

    def validateCoupRange(self, index: int, weight: float, target_value: Optional[float],
                          lower_limit: Optional[float], upper_limit: Optional[float]) -> Optional[dict]:
        """ Validate scalar J-coupling value range.
        """

        validRange = True
        dstFunc = {'weight': weight}

        if target_value is not None:
            if RDC_ERROR_MIN < target_value < RDC_ERROR_MAX:
                dstFunc['target_value'] = f"{target_value}"
            else:
                validRange = False
                self.__f.append(f"[Range value error] {self.__getCurrentRestraint(n=index)}"
                                f"The target value='{target_value}' must be within range {RDC_RESTRAINT_ERROR}.")

        if lower_limit is not None:
            if RDC_ERROR_MIN <= lower_limit < RDC_ERROR_MAX:
                dstFunc['lower_limit'] = f"{lower_limit:.6f}"
            else:
                validRange = False
                self.__f.append(f"[Range value error] {self.__getCurrentRestraint(n=index)}"
                                f"The lower limit value='{lower_limit:.6f}' must be within range {RDC_RESTRAINT_ERROR}.")

        if upper_limit is not None:
            if RDC_ERROR_MIN < upper_limit <= RDC_ERROR_MAX:
                dstFunc['upper_limit'] = f"{upper_limit:.6f}"
            else:
                validRange = False
                self.__f.append(f"[Range value error] {self.__getCurrentRestraint(n=index)}"
                                f"The upper limit value='{upper_limit:.6f}' must be within range {RDC_RESTRAINT_ERROR}.")

        if target_value is not None:

            if lower_limit is not None:
                if lower_limit > target_value:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint(n=index)}"
                                    f"The lower limit value='{lower_limit:.6f}' must be less than the target value '{target_value}'.")

            if upper_limit is not None:
                if upper_limit < target_value:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint(n=index)}"
                                    f"The upper limit value='{upper_limit:.6f}' must be greater than the target value '{target_value}'.")

        if not validRange:
            return None

        if target_value is not None:
            if RDC_RANGE_MIN <= target_value <= RDC_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint(n=index)}"
                                f"The target value='{target_value}' should be within range {RDC_RESTRAINT_RANGE}.")

        if lower_limit is not None:
            if RDC_RANGE_MIN <= lower_limit <= RDC_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint(n=index)}"
                                f"The lower limit value='{lower_limit:.6f}' should be within range {RDC_RESTRAINT_RANGE}.")

        if upper_limit is not None:
            if RDC_RANGE_MIN <= upper_limit <= RDC_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint(n=index)}"
                                f"The upper limit value='{upper_limit:.6f}' should be within range {RDC_RESTRAINT_RANGE}.")

        if target_value is None and lower_limit is None and upper_limit is None:
            return None

        return dstFunc

    # Enter a parse tree produced by DynamoMRParser#talos_restraints.
    def enterTalos_restraints(self, ctx: DynamoMRParser.Talos_restraintsContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'dihed'

        self.closeSequqnce()

    # Exit a parse tree produced by DynamoMRParser#talos_restraints.
    def exitTalos_restraints(self, ctx: DynamoMRParser.Talos_restraintsContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by DynamoMRParser#talos_restraint.
    def enterTalos_restraint(self, ctx: DynamoMRParser.Talos_restraintContext):  # pylint: disable=unused-argument
        self.dihedRestraints += 1

        self.atomSelectionSet.clear()

    # Exit a parse tree produced by DynamoMRParser#talos_restraint.
    def exitTalos_restraint(self, ctx: DynamoMRParser.Talos_restraintContext):

        try:

            seqId = int(str(ctx.Integer(0)))
            compId = str(ctx.Simple_name(0)).upper()

            if compId not in monDict3.values() and compId not in monDict3:
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                f"Found unknown residue name {compId!r}.")
                return

            if len(compId) >= 3:
                pass
            else:
                compId = next(k for k, v in monDict3.items() if v == compId and len(k) == 3)

            if len(self.numberSelection) == 0 or None in self.numberSelection:
                return

            # phi
            phi_target_value = self.numberSelection[0]
            psi_target_value = self.numberSelection[1]

            delta_phi_value = self.numberSelection[2]
            delta_psi_value = self.numberSelection[3]

            # dist = self.numberSelection[4]
            # s2 = self.numberSelection[5]

            # count = int(str(ctx.Integer(1)))
            # cs_count = int(str(ctx.Integer(2)))

            _class = str(ctx.Simple_name(1))

            if _class not in TALOS_PREDICTION_CLASSES:
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                f"The class name {_class!r} should be one of {TALOS_PREDICTION_CLASSES}.")
                return

            if _class not in TALOS_PREDICTION_MIN_CLASSES:  # ignore suspicious predictions
                return

            if not self.__hasPolySeq and not self.__hasNonPolySeq:
                return

            for angleName in ('PHI', 'PSI'):
                atomNames = KNOWN_ANGLE_ATOM_NAMES[angleName]
                seqOffset = KNOWN_ANGLE_SEQ_OFFSET[angleName]

                if angleName == 'PHI':
                    target_value = phi_target_value
                    if delta_phi_value > 0.0:
                        lower_limit = phi_target_value - delta_phi_value
                        upper_limit = phi_target_value + delta_phi_value
                    else:
                        lower_limit = upper_limit = None
                else:
                    target_value = psi_target_value
                    if delta_psi_value > 0.0:
                        lower_limit = psi_target_value - delta_psi_value
                        upper_limit = psi_target_value + delta_psi_value
                    else:
                        lower_limit = upper_limit = None

                dstFunc = self.validateAngleRange(None, 1.0, target_value, lower_limit, upper_limit)

                if dstFunc is None:
                    return

                atomId = next(name for name, offset in zip(atomNames, seqOffset) if offset == 0)

                if not isinstance(atomId, str):
                    self.__ccU.updateChemCompDict(compId)
                    atomId = next((cca[self.__ccU.ccaAtomId] for cca in self.__ccU.lastAtomList if atomId.match(cca[self.__ccU.ccaAtomId])), None)
                    if atomId is None:
                        resKey = (seqId, compId)
                        if resKey not in self.__extResKey:
                            self.__f.append(f"[Atom not found] {self.__getCurrentRestraint()}"
                                            f"{seqId}:{compId} is not present in the coordinates.")
                        return

                self.__retrieveLocalSeqScheme()

                chainAssign, _ = self.assignCoordPolymerSequence(None, seqId, compId, atomId)

                if len(chainAssign) == 0:
                    resKey = (seqId, compId)
                    if resKey not in self.__extResKey:
                        self.__f.append(f"[Atom not found] {self.__getCurrentRestraint()}"
                                        f"{seqId}:{compId} is not present in the coordinates.")
                    return

                for chainId, cifSeqId, cifCompId, _ in chainAssign:
                    ps = next(ps for ps in self.__polySeq if ps['auth_chain_id'] == chainId)

                    for ord, (atomId, offset) in enumerate(zip(atomNames, seqOffset)):

                        atomSelection = []

                        _cifSeqId = cifSeqId + offset
                        _cifCompId = cifCompId if offset == 0 else (ps['comp_id'][ps['auth_seq_id'].index(_cifSeqId)]
                                                                    if _cifSeqId in ps['auth_seq_id'] else None)

                        if _cifCompId is None and offset != 0 and 'gap_in_auth_seq' in ps and ps['gap_in_auth_seq']:
                            idx = ps['auth_seq_id'].index(cifSeqId)
                            try:
                                _cifSeqId = ps['auth_seq_id'][idx + offset]
                                _cifCompId = ps['comp_id'][idx + offset]
                            except IndexError:
                                pass

                        if _cifCompId is None:
                            try:
                                _cifCompId = ps['comp_id'][ps['auth_seq_id'].index(cifSeqId) + offset]
                            except IndexError:
                                pass
                            if _cifCompId is None and not self.__allow_ext_seq:
                                self.__f.append(f"[Sequence mismatch warning] {self.__getCurrentRestraint()}"
                                                f"The residue number '{seqId+offset}' is not present in polymer sequence "
                                                f"of chain {chainId} of the coordinates. "
                                                "Please update the sequence in the Macromolecules page.")
                                return
                                # _cifCompId = '.'
                            cifAtomId = atomId

                        else:
                            self.__ccU.updateChemCompDict(_cifCompId)

                            cifAtomId = next((cca[self.__ccU.ccaAtomId] for cca in self.__ccU.lastAtomList
                                              if cca[self.__ccU.ccaAtomId] == atomId), None)
                            if cifAtomId is None:
                                if ord == 0:
                                    _cifSeqId += seqOffset[ord + 1] - offset
                                    ptnr = getStructConnPtnrAtom(self.__cR, chainId, _cifSeqId, atomNames[ord + 1])
                                    if ptnr is not None and atomId[0] == ptnr['atom_id'][0]:
                                        cifAtomId = ptnr['atom_id']
                                elif ord == 3:
                                    _cifSeqId += seqOffset[ord - 1] - offset
                                    ptnr = getStructConnPtnrAtom(self.__cR, chainId, _cifSeqId, atomNames[ord - 1])
                                    if ptnr is not None and atomId[0] == ptnr['atom_id'][0]:
                                        cifAtomId = ptnr['atom_id']

                            if cifAtomId is None:
                                if _cifCompId is None and not self.__allow_ext_seq:
                                    self.__f.append(f"[Sequence mismatch warning] {self.__getCurrentRestraint()}"
                                                    f"The residue number '{seqId+offset}' is not present in polymer sequence "
                                                    f"of chain {chainId} of the coordinates. "
                                                    "Please update the sequence in the Macromolecules page.")
                                else:
                                    self.__f.append(f"[Atom not found] {self.__getCurrentRestraint()}"
                                                    f"{seqId+offset}:{compId}:{atomId} is not present in the coordinates.")
                                return

                        atomSelection.append({'chain_id': chainId, 'seq_id': _cifSeqId, 'comp_id': _cifCompId, 'atom_id': cifAtomId})

                        if len(atomSelection) > 0:
                            self.atomSelectionSet.append(atomSelection)

                    if len(self.atomSelectionSet) < 4:
                        return

                    try:
                        self.atomSelectionSet[0][0]['comp_id']
                    except IndexError:
                        self.areUniqueCoordAtoms('a torsion angle (TALOS)')
                        return

                    len_f = len(self.__f)
                    self.areUniqueCoordAtoms('a torsion angle (TALOS)',
                                             allow_ambig=True, allow_ambig_warn_title='Ambiguous dihedral angle')
                    combinationId = '.' if len_f == len(self.__f) else 0

                    atomSelTotal = sum(len(s) for s in self.atomSelectionSet)

                    if isinstance(combinationId, int):
                        fixedAngleName = '.'
                        for atom1, atom2, atom3, atom4 in itertools.product(self.atomSelectionSet[0],
                                                                            self.atomSelectionSet[1],
                                                                            self.atomSelectionSet[2],
                                                                            self.atomSelectionSet[3]):
                            atoms = [atom1, atom2, atom3, atom4]
                            _angleName = getTypeOfDihedralRestraint(True, False, False,
                                                                    atoms,
                                                                    'plane_like' in dstFunc)

                            if _angleName is not None and _angleName.startswith('pseudo'):
                                _angleName, atom2, atom3, err = fixBackboneAtomsOfDihedralRestraint(_angleName,
                                                                                                    atoms,
                                                                                                    self.__getCurrentRestraint())
                                self.__f.append(err)

                            if _angleName in emptyValue and atomSelTotal != 4:
                                continue

                            fixedAngleName = _angleName
                            break

                    if self.__createSfDict:
                        sf = self.__getSf(constraintType='backbone chemical shifts',
                                          potentialType=getPotentialType(self.__file_type, self.__cur_subtype, dstFunc),
                                          softwareName='TALOS')
                        sf['id'] += 1

                    for atom1, atom2, atom3, atom4 in itertools.product(self.atomSelectionSet[0],
                                                                        self.atomSelectionSet[1],
                                                                        self.atomSelectionSet[2],
                                                                        self.atomSelectionSet[3]):
                        atoms = [atom1, atom2, atom3, atom4]
                        if isLongRangeRestraint(atoms, self.__polySeq if self.__gapInAuthSeq else None):
                            continue
                        _angleName = getTypeOfDihedralRestraint(True, False, False,
                                                                atoms,
                                                                'plane_like' in dstFunc)

                        if _angleName is not None and _angleName.startswith('pseudo'):
                            _angleName, atom2, atom3, err = fixBackboneAtomsOfDihedralRestraint(_angleName,
                                                                                                atoms,
                                                                                                self.__getCurrentRestraint())
                            self.__f.append(err)

                        if _angleName in emptyValue and atomSelection != 4:
                            continue

                        if isinstance(combinationId, int):
                            if _angleName != fixedAngleName:
                                continue
                            combinationId += 1
                        if self.__debug:
                            print(f"subtype={self.__cur_subtype} id={self.dihedRestraints} angleName={angleName} className={_class} "
                                  f"atom1={atom1} atom2={atom2} atom3={atom3} atom4={atom4} {dstFunc}")
                        if self.__createSfDict and sf is not None:
                            sf['index_id'] += 1
                            row = getRow(self.__cur_subtype, sf['id'], sf['index_id'],
                                         combinationId, None, angleName,
                                         sf['list_id'], self.__entryId, dstFunc,
                                         self.__authToStarSeq, self.__authToOrigSeq, self.__authToInsCode, self.__offsetHolder,
                                         atom1, atom2, atom3, atom4)
                            sf['loop'].add_data(row)

                    if self.__createSfDict and sf is not None and isinstance(combinationId, int) and combinationId == 1:
                        sf['loop'].data[-1] = resetCombinationId(self.__cur_subtype, sf['loop'].data[-1])

                    self.atomSelectionSet.clear()

        except ValueError:
            self.dihedRestraints -= 1

        finally:
            self.numberSelection.clear()

    # Enter a parse tree produced by DynamoMRParser#talos_restraints_wo_s2.
    def enterTalos_restraints_wo_s2(self, ctx: DynamoMRParser.Talos_restraints_wo_s2Context):  # pylint: disable=unused-argument
        self.__cur_subtype = 'dihed'

        self.closeSequqnce()

    # Exit a parse tree produced by DynamoMRParser#talos_restraints_wo_s2.
    def exitTalos_restraints_wo_s2(self, ctx: DynamoMRParser.Talos_restraints_wo_s2Context):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by DynamoMRParser#talos_restraint_wo_s2.
    def enterTalos_restraint_wo_s2(self, ctx: DynamoMRParser.Talos_restraint_wo_s2Context):  # pylint: disable=unused-argument
        self.dihedRestraints += 1

        self.atomSelectionSet.clear()

    # Exit a parse tree produced by DynamoMRParser#talos_restraint_wo_s2.
    def exitTalos_restraint_wo_s2(self, ctx: DynamoMRParser.Talos_restraint_wo_s2Context):

        try:

            seqId = int(str(ctx.Integer(0)))
            compId = str(ctx.Simple_name(0)).upper()

            if compId not in monDict3.values() and compId not in monDict3:
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                f"Found unknown residue name {compId!r}.")
                return

            if len(compId) >= 3:
                pass
            else:
                compId = next(k for k, v in monDict3.items() if v == compId and len(k) == 3)

            if len(self.numberSelection) == 0 or None in self.numberSelection:
                return

            # phi
            phi_target_value = self.numberSelection[0]
            psi_target_value = self.numberSelection[1]

            delta_phi_value = self.numberSelection[2]
            delta_psi_value = self.numberSelection[3]

            # dist = self.numberSelection[4]

            # count = int(str(ctx.Integer(1)))

            _class = str(ctx.Simple_name(1))

            if _class not in TALOS_PREDICTION_CLASSES:
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                f"The class name {_class!r} should be one of {TALOS_PREDICTION_CLASSES}.")
                return

            if _class not in TALOS_PREDICTION_MIN_CLASSES:  # ignore suspicious predictions
                return

            if not self.__hasPolySeq and not self.__hasNonPolySeq:
                return

            for angleName in ('PHI', 'PSI'):
                atomNames = KNOWN_ANGLE_ATOM_NAMES[angleName]
                seqOffset = KNOWN_ANGLE_SEQ_OFFSET[angleName]

                if angleName == 'PHI':
                    target_value = phi_target_value
                    if delta_phi_value > 0.0:
                        lower_limit = phi_target_value - delta_phi_value
                        upper_limit = phi_target_value + delta_phi_value
                    else:
                        lower_limit = upper_limit = None
                else:
                    target_value = psi_target_value
                    if delta_psi_value > 0.0:
                        lower_limit = psi_target_value - delta_psi_value
                        upper_limit = psi_target_value + delta_psi_value
                    else:
                        lower_limit = upper_limit = None

                dstFunc = self.validateAngleRange(None, 1.0, target_value, lower_limit, upper_limit)

                if dstFunc is None:
                    return

                atomId = next(name for name, offset in zip(atomNames, seqOffset) if offset == 0)

                if not isinstance(atomId, str):
                    self.__ccU.updateChemCompDict(compId)
                    atomId = next((cca[self.__ccU.ccaAtomId] for cca in self.__ccU.lastAtomList if atomId.match(cca[self.__ccU.ccaAtomId])), None)
                    if atomId is None:
                        resKey = (seqId, compId)
                        if resKey not in self.__extResKey:
                            self.__f.append(f"[Atom not found] {self.__getCurrentRestraint()}"
                                            f"{seqId}:{compId} is not present in the coordinates.")
                        return

                self.__retrieveLocalSeqScheme()

                chainAssign, _ = self.assignCoordPolymerSequence(None, seqId, compId, atomId)

                if len(chainAssign) == 0:
                    resKey = (seqId, compId)
                    if resKey not in self.__extResKey:
                        self.__f.append(f"[Atom not found] {self.__getCurrentRestraint()}"
                                        f"{seqId}:{compId} is not present in the coordinates.")
                    return

                for chainId, cifSeqId, cifCompId, _ in chainAssign:
                    ps = next(ps for ps in self.__polySeq if ps['auth_chain_id'] == chainId)

                    for atomId, offset in zip(atomNames, seqOffset):

                        atomSelection = []

                        _cifSeqId = cifSeqId + offset
                        _cifCompId = cifCompId if offset == 0 else (ps['comp_id'][ps['auth_seq_id'].index(_cifSeqId)]
                                                                    if _cifSeqId in ps['auth_seq_id'] else None)

                        if _cifCompId is None and offset != 0 and 'gap_in_auth_seq' in ps and ps['gap_in_auth_seq']:
                            idx = ps['auth_seq_id'].index(cifSeqId)
                            try:
                                _cifSeqId = ps['auth_seq_id'][idx + offset]
                                _cifCompId = ps['comp_id'][idx + offset]
                            except IndexError:
                                pass

                        if _cifCompId is None:
                            try:
                                _cifCompId = ps['comp_id'][ps['auth_seq_id'].index(cifSeqId) + offset]
                            except IndexError:
                                pass
                            if _cifCompId is None and not self.__allow_ext_seq:
                                self.__f.append(f"[Sequence mismatch warning] {self.__getCurrentRestraint()}"
                                                f"The residue number '{seqId+offset}' is not present in polymer sequence "
                                                f"of chain {chainId} of the coordinates. "
                                                "Please update the sequence in the Macromolecules page.")
                                return
                                # _cifCompId = '.'
                            cifAtomId = atomId

                        else:
                            self.__ccU.updateChemCompDict(_cifCompId)

                            cifAtomId = next((cca[self.__ccU.ccaAtomId] for cca in self.__ccU.lastAtomList
                                              if cca[self.__ccU.ccaAtomId] == atomId), None)

                            if cifAtomId is None:
                                if _cifCompId is None and not self.__allow_ext_seq:
                                    self.__f.append(f"[Sequence mismatch warning] {self.__getCurrentRestraint()}"
                                                    f"The residue number '{seqId+offset}' is not present in polymer sequence "
                                                    f"of chain {chainId} of the coordinates. "
                                                    "Please update the sequence in the Macromolecules page.")
                                else:
                                    self.__f.append(f"[Atom not found] {self.__getCurrentRestraint()}"
                                                    f"{seqId+offset}:{compId}:{atomId} is not present in the coordinates.")
                                return

                        atomSelection.append({'chain_id': chainId, 'seq_id': _cifSeqId, 'comp_id': _cifCompId, 'atom_id': cifAtomId})

                        if len(atomSelection) > 0:
                            self.atomSelectionSet.append(atomSelection)

                    if len(self.atomSelectionSet) < 4:
                        return

                    try:
                        self.atomSelectionSet[0][0]['comp_id']
                    except IndexError:
                        self.areUniqueCoordAtoms('a torsion angle (TALOS)')
                        return

                    len_f = len(self.__f)
                    self.areUniqueCoordAtoms('a torsion angle (TALOS)',
                                             allow_ambig=True, allow_ambig_warn_title='Ambiguous dihedral angle')
                    combinationId = '.' if len_f == len(self.__f) else 0

                    atomSelTotal = sum(len(s) for s in self.atomSelectionSet)

                    if isinstance(combinationId, int):
                        fixedAngleName = '.'
                        for atom1, atom2, atom3, atom4 in itertools.product(self.atomSelectionSet[0],
                                                                            self.atomSelectionSet[1],
                                                                            self.atomSelectionSet[2],
                                                                            self.atomSelectionSet[3]):
                            atoms = [atom1, atom2, atom3, atom4]
                            _angleName = getTypeOfDihedralRestraint(True, False, False,
                                                                    atoms,
                                                                    'plane_like' in dstFunc)

                            if _angleName is not None and _angleName.startswith('pseudo'):
                                _angleName, atom2, atom3, err = fixBackboneAtomsOfDihedralRestraint(_angleName,
                                                                                                    atoms,
                                                                                                    self.__getCurrentRestraint())
                                self.__f.append(err)

                            if _angleName in emptyValue and atomSelTotal != 4:
                                continue

                            fixedAngleName = _angleName
                            break

                    if self.__createSfDict:
                        sf = self.__getSf(constraintType='backbone chemical shifts',
                                          potentialType=getPotentialType(self.__file_type, self.__cur_subtype, dstFunc),
                                          softwareName='TALOS')
                        sf['id'] += 1

                    for atom1, atom2, atom3, atom4 in itertools.product(self.atomSelectionSet[0],
                                                                        self.atomSelectionSet[1],
                                                                        self.atomSelectionSet[2],
                                                                        self.atomSelectionSet[3]):
                        atoms = [atom1, atom2, atom3, atom4]
                        if isLongRangeRestraint(atoms, self.__polySeq if self.__gapInAuthSeq else None):
                            continue
                        _angleName = getTypeOfDihedralRestraint(True, False, False,
                                                                atoms,
                                                                'plane_like' in dstFunc)

                        if _angleName is not None and _angleName.startswith('pseudo'):
                            _angleName, atom2, atom3, err = fixBackboneAtomsOfDihedralRestraint(_angleName,
                                                                                                atoms,
                                                                                                self.__getCurrentRestraint())
                            self.__f.append(err)

                        if _angleName in emptyValue and atomSelTotal != 4:
                            continue

                        if isinstance(combinationId, int):
                            if _angleName != fixedAngleName:
                                continue
                            combinationId += 1
                        if self.__debug:
                            print(f"subtype={self.__cur_subtype} id={self.dihedRestraints} angleName={angleName} className={_class} "
                                  f"atom1={atom1} atom2={atom2} atom3={atom3} atom4={atom4} {dstFunc}")
                        if self.__createSfDict and sf is not None:
                            sf['index_id'] += 1
                            row = getRow(self.__cur_subtype, sf['id'], sf['index_id'],
                                         combinationId, None, angleName,
                                         sf['list_id'], self.__entryId, dstFunc,
                                         self.__authToStarSeq, self.__authToOrigSeq, self.__authToInsCode, self.__offsetHolder,
                                         atom1, atom2, atom3, atom4)
                            sf['loop'].add_data(row)

                    if self.__createSfDict and sf is not None and isinstance(combinationId, int) and combinationId == 1:
                        sf['loop'].data[-1] = resetCombinationId(self.__cur_subtype, sf['loop'].data[-1])

                    self.atomSelectionSet.clear()

        except ValueError:
            self.dihedRestraints -= 1

        finally:
            self.numberSelection.clear()

    # Enter a parse tree produced by DynamoMRParser#number.
    def enterNumber(self, ctx: DynamoMRParser.NumberContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by DynamoMRParser#number.
    def exitNumber(self, ctx: DynamoMRParser.NumberContext):
        if ctx.Float():
            self.numberSelection.append(float(str(ctx.Float())))

        elif ctx.Float_DecimalComma():
            self.numberSelection.append(float(str(ctx.Float_DecimalComma()).replace(',', '.', 1)))

        elif ctx.Integer():
            self.numberSelection.append(float(str(ctx.Integer())))

        else:
            self.numberSelection.append(None)

    def __getCurrentRestraint(self, n: Optional[int] = None, g: Optional[int] = None) -> str:
        if self.__cur_subtype == 'dist':
            if None in (n, g):
                return f"[Check the {self.distRestraints}th row of distance restraints, {self.__def_err_sf_framecode}] "
            return f"[Check the {self.distRestraints}th row of distance restraints (index={n} group={g}), {self.__def_err_sf_framecode}] "
        if self.__cur_subtype == 'dihed':
            if n is None:
                return f"[Check the {self.dihedRestraints}th row of torsion angle restraints, {self.__def_err_sf_framecode}] "
            return f"[Check the {self.dihedRestraints}th row of torsion angle restraints (index={n}), {self.__def_err_sf_framecode}] "
        if self.__cur_subtype == 'rdc':
            return f"[Check the {self.rdcRestraints}th row of residual dipolar coupling restraints, {self.__def_err_sf_framecode}] "
        if self.__cur_subtype == 'jcoup':
            if n is None:
                return f"[Check the {self.jcoupRestraints}th row of scalar coupling constant restraints, {self.__def_err_sf_framecode}] "
            return f"[Check the {self.jcoupRestraints}th row of scalar coupling constant restraints (index={n}), {self.__def_err_sf_framecode}] "
        return ''

    def __setLocalSeqScheme(self):
        if 'local_seq_scheme' not in self.reasonsForReParsing:
            self.reasonsForReParsing['local_seq_scheme'] = {}
        preferAuthSeq = self.__authSeqId == 'auth_seq_id'
        if self.__cur_subtype == 'dist':
            self.reasonsForReParsing['local_seq_scheme'][(self.__cur_subtype, self.distRestraints)] = preferAuthSeq
        elif self.__cur_subtype == 'dihed':
            self.reasonsForReParsing['local_seq_scheme'][(self.__cur_subtype, self.dihedRestraints)] = preferAuthSeq
        elif self.__cur_subtype == 'rdc':
            self.reasonsForReParsing['local_seq_scheme'][(self.__cur_subtype, self.rdcRestraints)] = preferAuthSeq
        elif self.__cur_subtype == 'jcoup':
            self.reasonsForReParsing['local_seq_scheme'][(self.__cur_subtype, self.jcoupRestraints)] = preferAuthSeq
        if not preferAuthSeq:
            self.__preferLabelSeqCount += 1
            if self.__preferLabelSeqCount > MAX_PREF_LABEL_SCHEME_COUNT:
                self.reasonsForReParsing['label_seq_scheme'] = True

    def __retrieveLocalSeqScheme(self):
        if self.__reasons is None\
           or ('label_seq_scheme' not in self.__reasons
               and 'local_seq_scheme' not in self.__reasons
               and 'extend_seq_scheme' not in self.__reasons):
            return
        if 'extend_seq_scheme' in self.__reasons:
            self.__preferAuthSeq = self.__extendAuthSeq = True
            return
        if 'label_seq_scheme' in self.__reasons and self.__reasons['label_seq_scheme']:
            self.__preferAuthSeq = False
            # self.__authSeqId = 'label_seq_id'
            return
        if self.__cur_subtype == 'dist':
            key = (self.__cur_subtype, self.distRestraints)
        elif self.__cur_subtype == 'dihed':
            key = (self.__cur_subtype, self.dihedRestraints)
        elif self.__cur_subtype == 'rdc':
            key = (self.__cur_subtype, self.rdcRestraints)
        elif self.__cur_subtype == 'jcoup':
            key = (self.__cur_subtype, self.jcoupRestraints)
        else:
            return

        if key in self.__reasons['local_seq_scheme']:
            self.__preferAuthSeq = self.__reasons['local_seq_scheme'][key]

    def __addSf(self, constraintType: Optional[str] = None, potentialType: Optional[str] = None,
                rdcCode: Optional[str] = None, softwareName: Optional[str] = None):
        content_subtype = contentSubtypeOf(self.__cur_subtype)

        if content_subtype is None:
            return

        self.__listIdCounter = incListIdCounter(self.__cur_subtype, self.__listIdCounter)

        key = (self.__cur_subtype, constraintType, potentialType, rdcCode, None)

        if key in self.sfDict:
            if len(self.sfDict[key]) > 0:
                decListIdCounter(self.__cur_subtype, self.__listIdCounter)
                return
        else:
            self.sfDict[key] = []

        list_id = self.__listIdCounter[content_subtype]

        restraint_name = getRestraintName(self.__cur_subtype)

        sf_framecode = ('DYNAMO/PALES/TALOS' if softwareName is None else softwareName) + '_' + restraint_name.replace(' ', '_') + f'_{list_id}'

        sf = getSaveframe(self.__cur_subtype, sf_framecode, list_id, self.__entryId, self.__originalFileName,
                          constraintType=constraintType, potentialType=potentialType, rdcCode=rdcCode)

        not_valid = True

        lp = getLoop(self.__cur_subtype, hasInsCode=self.__authToInsCode is not None)
        if not isinstance(lp, dict):
            sf.add_loop(lp)
            not_valid = False

        _restraint_name = restraint_name.split()

        item = {'file_type': self.__file_type, 'saveframe': sf, 'loop': lp, 'list_id': list_id,
                'id': 0, 'index_id': 0,
                'constraint_type': ' '.join(_restraint_name[:-1]),
                'sf_framecode': sf_framecode}

        if not_valid:
            item['tags'] = []

        if self.__cur_subtype == 'dist':
            item['constraint_subsubtype'] = 'simple'

        self.sfDict[key].append(item)

    def __getSf(self, constraintType: Optional[str] = None, potentialType: Optional[str] = None,
                rdcCode: Optional[str] = None, softwareName: Optional[str] = None) -> dict:
        key = (self.__cur_subtype, constraintType, potentialType, rdcCode, None)

        if key not in self.sfDict:
            replaced = False
            if potentialType is not None or rdcCode is not None:
                old_key = (self.__cur_subtype, constraintType, None, None, None)
                if old_key in self.sfDict:
                    replaced = True
                    self.sfDict[key] = [self.sfDict[old_key].pop(-1)]
                    if len(self.sfDict[old_key]) == 0:
                        del self.sfDict[old_key]
                    sf = self.sfDict[key][-1]['saveframe']
                    idx = next((idx for idx, t in enumerate(sf.tags) if t[0] == 'Potential_type'), -1)
                    if idx != -1:
                        sf.tags[idx][1] = potentialType
                    else:
                        sf.add_tag('Potential_type', potentialType)
                    if rdcCode is not None:
                        idx = next((idx for idx, t in enumerate(sf.tags) if t[0] == 'Details'), -1)
                        if idx != -1:
                            sf.tags[idx][1] = rdcCode
                        else:
                            sf.add_tag('Details', rdcCode)
            if not replaced:
                self.__addSf(constraintType=constraintType, potentialType=potentialType, rdcCode=rdcCode,
                             softwareName=softwareName)

        self.__cur_constraint_type = constraintType

        _key = next((_key for _key in self.sfDict if _key[0] == 'dist' and _key[1] is None), key) if self.__cur_subtype == 'dist' else key
        self.__def_err_sf_framecode = self.sfDict[_key][-1]['sf_framecode']

        return self.sfDict[key][-1]

    def getContentSubtype(self) -> dict:
        """ Return content subtype of DYNAMO/PALES/TALOS MR file.
        """

        contentSubtype = {'dist_restraint': self.distRestraints,
                          'dihed_restraint': self.dihedRestraints,
                          'rdc_restraint': self.rdcRestraints,
                          'jcoup_restraint': self.jcoupRestraints
                          }

        return {k: 1 for k, v in contentSubtype.items() if v > 0}

    def getPolymerSequence(self) -> Optional[List[dict]]:
        """ Return polymer sequence of DYNAMO/PALES/TALOS MR file.
        """

        return None if self.__polySeqRst is None or len(self.__polySeqRst) == 0 else self.__polySeqRst

    def getSequenceAlignment(self) -> Optional[List[dict]]:
        """ Return sequence alignment between coordinates and DYNAMO/PALES/TALOS MR.
        """

        return None if self.__seqAlign is None or len(self.__seqAlign) == 0 else self.__seqAlign

    def getChainAssignment(self) -> Optional[List[dict]]:
        """ Return chain assignment between coordinates and DYNAMO/PALES/TALOS MR.
        """

        return None if self.__chainAssign is None or len(self.__chainAssign) == 0 else self.__chainAssign

    def getReasonsForReparsing(self) -> Optional[dict]:
        """ Return reasons for re-parsing DYNAMO/PALES/TALOS MR file.
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
                    self.__listIdCounter = decListIdCounter(k[0], self.__listIdCounter)
        for k in ign_keys:
            del self.sfDict[k]
        return self.__listIdCounter, None if len(self.sfDict) == 0 else self.sfDict

# del DynamoMRParser
