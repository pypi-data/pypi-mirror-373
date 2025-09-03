##
# File: RosettaMRParserListener.py
# Date: 04-Mar-2022
#
# Updates:
""" ParserLister class for ROSETTA MR files.
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
import itertools
import numpy
import collections

from antlr4 import ParseTreeListener
from typing import IO, List, Tuple, Optional

from wwpdb.utils.align.alignlib import PairwiseAlign  # pylint: disable=no-name-in-module

try:
    from wwpdb.utils.nmr.io.CifReader import CifReader
    from wwpdb.utils.nmr.mr.RosettaMRParser import RosettaMRParser
    from wwpdb.utils.nmr.mr.ParserListenerUtil import (coordAssemblyChecker,
                                                       extendCoordChainsForExactNoes,
                                                       isIdenticalRestraint,
                                                       isLongRangeRestraint,
                                                       hasIntraChainRestraint,
                                                       hasInterChainRestraint,
                                                       isAmbigAtomSelection,
                                                       getAltProtonIdInBondConstraint,
                                                       guessCompIdFromAtomId,
                                                       getTypeOfDihedralRestraint,
                                                       fixBackboneAtomsOfDihedralRestraint,
                                                       isLikePheOrTyr,
                                                       getRdcCode,
                                                       translateToStdAtomName,
                                                       isCyclicPolymer,
                                                       isStructConn,
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
                                                       getDstFuncForSsBond,
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
                                                       CARTN_DATA_ITEMS)
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
                                           rdcBbPairCode,
                                           zincIonCode,
                                           calciumIonCode,
                                           updatePolySeqRst,
                                           updatePolySeqRstAmbig,
                                           mergePolySeqRstAmbig,
                                           sortPolySeqRst,
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
    from nmr.io.CifReader import CifReader
    from nmr.mr.RosettaMRParser import RosettaMRParser
    from nmr.mr.ParserListenerUtil import (coordAssemblyChecker,
                                           extendCoordChainsForExactNoes,
                                           isIdenticalRestraint,
                                           isLongRangeRestraint,
                                           hasIntraChainRestraint,
                                           hasInterChainRestraint,
                                           isAmbigAtomSelection,
                                           getAltProtonIdInBondConstraint,
                                           guessCompIdFromAtomId,
                                           getTypeOfDihedralRestraint,
                                           fixBackboneAtomsOfDihedralRestraint,
                                           isLikePheOrTyr,
                                           getRdcCode,
                                           translateToStdAtomName,
                                           isCyclicPolymer,
                                           isStructConn,
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
                                           getDstFuncForSsBond,
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
                                           CARTN_DATA_ITEMS)
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
                               updatePolySeqRstAmbig,
                               mergePolySeqRstAmbig,
                               sortPolySeqRst,
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


# This class defines a complete listener for a parse tree produced by RosettaMRParser.
class RosettaMRParserListener(ParseTreeListener):

    __file_type = 'nm-res-ros'

    __verbose = None
    __lfh = None
    __debug = False
    __remediate = False

    __createSfDict = True
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

    __offsetHolder = None

    __representativeModelId = REPRESENTATIVE_MODEL_ID
    __representativeAltId = REPRESENTATIVE_ALT_ID
    __hasPolySeq = False
    __hasNonPoly = False
    __hasBranched = False
    __hasNonPolySeq = False
    __preferAuthSeq = True
    __gapInAuthSeq = False
    __extendAuthSeq = False

    # polymer sequence of MR file
    __polySeqRst = None
    __polySeqRstFailed = None
    __polySeqRstFailedAmbig = None

    __uniqAtomIdToSeqKey = None

    __seqAlign = None
    __chainAssign = None

    # current restraint subtype
    __cur_subtype = ''
    __cur_comment_inlined = False

    # whether to allow extended sequence temporary
    __allow_ext_seq = False

    # stack of function
    stackFuncs = []

    # collection of atom selection
    atomSelectionSet = []

    # collection of number selection
    numberSelection = []

    # collection of number selection in function
    numberFSelection = []

    # collection of atom selection in comment
    atomSelectionInComment = []

    # current nested restraint type
    __is_first_nest = False
    __is_any_nest = False
    __nest_combination_id = -1
    __nest_member_id = -1
    stackNest = []

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

        self.distRestraints = 0      # ROSETTA: Distance restraints
        self.angRestraints = 0       # ROSETTA: Angle restraints
        self.dihedRestraints = 0     # ROSETTA: Dihedral angle restraints
        self.rdcRestraints = 0       # ROSETTA: Residual dipolar coupling restraints
        self.geoRestraints = 0       # ROSETTA: Coordinate geometry restraints
        self.ssbondRestraints = 0    # ROSETTA: Disulfide bond geometry restraints

        self.concat_resnum_chain_pat = re.compile(r'^(\d+)(\S+)$')

        self.__dist_lb_greater_than_ub = False
        self.__dist_ub_always_positive = True

        self.__atom_sel_comment_pattern = re.compile(r'([A-Za-z]+)(\d+)(\S+)$')

        self.sfDict = {}

        self.__cachedDictForStarAtom = {}

    def setDebugMode(self, debug: bool):
        self.__debug = debug

    def setRemediateMode(self, remediate: bool):
        self.__remediate = remediate

    def createSfDict(self, createSfDict: bool):
        self.__createSfDict = createSfDict

    def setOriginaFileName(self, originalFileName: str):
        self.__originalFileName = originalFileName

    def setListIdCounter(self, listIdCounter: dict):
        self.__listIdCounter = listIdCounter

    def setEntryId(self, entryId: str):
        self.__entryId = entryId

    # Enter a parse tree produced by RosettaMRParser#rosetta_mr.
    def enterRosetta_mr(self, ctx: RosettaMRParser.Rosetta_mrContext):  # pylint: disable=unused-argument
        self.__polySeqRst = []
        self.__polySeqRstFailed = []
        self.__polySeqRstFailedAmbig = []
        self.__f = []

    # Exit a parse tree produced by RosettaMRParser#rosetta_mr.
    def exitRosetta_mr(self, ctx: RosettaMRParser.Rosetta_mrContext):  # pylint: disable=unused-argument

        def set_label_seq_scheme():
            if 'label_seq_scheme' not in self.reasonsForReParsing:
                self.reasonsForReParsing['label_seq_scheme'] = {}
            if self.distRestraints > 0:
                self.reasonsForReParsing['label_seq_scheme']['dist'] = True
            if self.angRestraints > 0:
                self.reasonsForReParsing['label_seq_scheme']['ang'] = True
            if self.dihedRestraints > 0:
                self.reasonsForReParsing['label_seq_scheme']['dihed'] = True
            if self.rdcRestraints > 0:
                self.reasonsForReParsing['label_seq_scheme']['rdc'] = True
            if self.geoRestraints > 0:
                self.reasonsForReParsing['label_seq_scheme']['geo'] = True
            if self.ssbondRestraints > 0:
                self.reasonsForReParsing['label_seq_scheme']['ssbond'] = True
            if 'local_seq_scheme' in self.reasonsForReParsing:
                del self.reasonsForReParsing['local_seq_scheme']

        try:

            _seqIdRemap = []

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

                    if self.__reasons is None\
                       and any(f for f in self.__f if '[Anomalous data]' in f):
                        set_label_seq_scheme()

                    if self.__reasons is None and any(f for f in self.__f
                                                      if '[Atom not found]' in f or 'Invalid atom nomenclature' in f):

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
                            for ref_seq_id, mid_code, test_seq_id in zip(sa['ref_seq_id'], sa['mid_code'], sa['test_seq_id']):
                                if mid_code == '|' and test_seq_id is not None:
                                    try:
                                        seq_id_mapping[test_seq_id] = next(auth_seq_id for auth_seq_id, seq_id
                                                                           in zip(poly_seq_model['auth_seq_id'], poly_seq_model['seq_id'])
                                                                           if seq_id == ref_seq_id and isinstance(auth_seq_id, int))
                                    except StopIteration:
                                        pass

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
                            else:
                                _seqIdRemap.append({'chain_id': test_chain_id, 'seq_id_dict': seq_id_mapping})

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

                        mergePolySeqRstAmbig(self.__polySeqRstFailed, self.__polySeqRstFailedAmbig)
                        if len(self.__polySeqRstFailed) > 0:
                            sortPolySeqRst(self.__polySeqRstFailed)

                            seqAlignFailed, _ = alignPolymerSequence(self.__pA, self.__polySeq, self.__polySeqRstFailed)

                            for sa in seqAlignFailed:
                                if sa['conflict'] == 0:
                                    chainId = sa['test_chain_id']
                                    _ps = next((_ps for _ps in self.__polySeqRstFailedAmbig if _ps['chain_id'] == chainId), None)
                                    if _ps is None:
                                        continue
                                    _matched = sa['matched']
                                    for seqId, compIds in zip(_ps['seq_id'], _ps['comp_ids']):
                                        _compId = None
                                        for compId in list(compIds):
                                            _polySeqRstFailed = copy.deepcopy(self.__polySeqRstFailed)
                                            updatePolySeqRst(_polySeqRstFailed, chainId, seqId, compId)
                                            sortPolySeqRst(_polySeqRstFailed)
                                            _seqAlignFailed, _ = alignPolymerSequence(self.__pA, self.__polySeq, _polySeqRstFailed)
                                            _sa = next((_sa for _sa in _seqAlignFailed if _sa['test_chain_id'] == chainId), None)
                                            if _sa is None or _sa['conflict'] > 0:
                                                continue
                                            if _sa['matched'] > _matched:
                                                _matched = _sa['matched']
                                                _compId = compId
                                        if _compId is not None:
                                            updatePolySeqRst(self.__polySeqRstFailed, chainId, seqId, _compId)
                                            sortPolySeqRst(self.__polySeqRstFailed)

                            seqAlignFailed, _ = alignPolymerSequence(self.__pA, self.__polySeq, self.__polySeqRstFailed)
                            chainAssignFailed, _ = assignPolymerSequence(self.__pA, self.__ccU, self.__file_type,
                                                                         self.__polySeq, self.__polySeqRstFailed, seqAlignFailed)

                            if chainAssignFailed is not None:

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
                                    for ref_auth_seq_id, mid_code, test_seq_id in zip(sa['ref_auth_seq_id'] if 'ref_auth_seq_id' in sa else sa['ref_seq_id'],
                                                                                      sa['mid_code'], sa['test_seq_id']):
                                        if mid_code == '|' and test_seq_id is not None:
                                            seq_id_mapping[test_seq_id] = ref_auth_seq_id

                                    if len(seq_id_mapping) > 1:
                                        for k, v in seq_id_mapping.items():
                                            offset = v - k
                                            break

                                        if any(k for k, v in seq_id_mapping.items() if k != v):
                                            if not any(v - k != offset for k, v in seq_id_mapping.items()):
                                                if 'global_auth_sequence_offset' not in self.reasonsForReParsing:
                                                    self.reasonsForReParsing['global_auth_sequence_offset'] = {}
                                                self.reasonsForReParsing['global_auth_sequence_offset'][ref_chain_id] = offset
                                            else:
                                                offsets = [v - k for k, v in seq_id_mapping.items()]
                                                common_offsets = collections.Counter(offsets).most_common()
                                                if common_offsets[0][1] > 1 and common_offsets[0][1] > common_offsets[1][1]\
                                                   and abs(common_offsets[0][0] - common_offsets[1][0]) == 1:
                                                    offset = common_offsets[0][0]
                                                    if 'global_auth_sequence_offset' not in self.reasonsForReParsing:
                                                        self.reasonsForReParsing['global_auth_sequence_offset'] = {}
                                                    self.reasonsForReParsing['global_auth_sequence_offset'][ref_chain_id] = offset
                                                else:
                                                    seq_id_mapping = {}
                                                    for ref_seq_id, mid_code, test_seq_id in zip(sa['ref_seq_id'], sa['mid_code'], sa['test_seq_id']):
                                                        if mid_code == '|' and test_seq_id is not None:
                                                            seq_id_mapping[test_seq_id] = ref_seq_id

                                                    for k, v in seq_id_mapping.items():
                                                        offset = v - k
                                                        break

                                                    if offset != 0 and not any(v - k != offset for k, v in seq_id_mapping.items()):
                                                        offsets = {}
                                                        for ref_auth_seq_id, auth_seq_id in zip(sa['ref_auth_seq_id'], sa['ref_seq_id']):
                                                            offsets[auth_seq_id - offset] = ref_auth_seq_id - auth_seq_id
                                                        if 'global_auth_sequence_offset' not in self.reasonsForReParsing:
                                                            self.reasonsForReParsing['global_auth_sequence_offset'] = {}
                                                        self.reasonsForReParsing['global_auth_sequence_offset'][ref_chain_id] = offsets

                                if len(chainAssignFailed) == 0:
                                    valid_auth_seq = valid_label_seq = True
                                    for _ps in self.__polySeqRstFailed:
                                        test_chain_id = _ps['chain_id']
                                        try:
                                            ps = next(ps for ps in self.__polySeq if ps['auth_chain_id'] == test_chain_id)
                                            for test_seq_id, test_comp_id in zip(_ps['seq_id'], _ps['comp_id']):
                                                if test_seq_id not in ps['seq_id']:
                                                    valid_label_seq = False
                                                elif test_comp_id != ps['comp_id'][ps['seq_id'].index(test_seq_id)]:
                                                    valid_label_seq = False
                                                if test_seq_id not in ps['auth_seq_id']:
                                                    valid_auth_seq = False
                                                elif test_comp_id != ps['comp_id'][ps['auth_seq_id'].index(test_seq_id)]:
                                                    valid_auth_seq = False
                                                if not valid_auth_seq and not valid_label_seq:
                                                    break
                                        except StopIteration:
                                            valid_auth_seq = valid_label_seq = False
                                            break
                                    if not valid_auth_seq and valid_label_seq:
                                        set_label_seq_scheme()

                                seqIdRemapFailed = []

                                uniq_ps = not any('identical_chain_id' in ps for ps in self.__polySeq)

                                for ca in chainAssignFailed:
                                    if ca['conflict'] > 0:
                                        continue
                                    ref_chain_id = ca['ref_chain_id']
                                    test_chain_id = ca['test_chain_id']
                                    sa = next(sa for sa in seqAlignFailed
                                              if sa['ref_chain_id'] == ref_chain_id
                                              and sa['test_chain_id'] == test_chain_id)

                                    poly_seq_model = next(ps for ps in self.__polySeq
                                                          if ps['auth_chain_id'] == ref_chain_id)

                                    seq_id_mapping = {}
                                    for ref_seq_id, mid_code, test_seq_id in zip(sa['ref_seq_id'], sa['mid_code'], sa['test_seq_id']):
                                        if mid_code == '|' and test_seq_id is not None:
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

            label_seq_scheme = 'label_seq_scheme' in self.reasonsForReParsing\
                and all(t for t in self.reasonsForReParsing['label_seq_scheme'].values())

            seqIdRemapForRemaining = []
            if 'global_auth_sequence_offset' in self.reasonsForReParsing:
                if 'local_seq_scheme' in self.reasonsForReParsing:
                    del self.reasonsForReParsing['local_seq_scheme']
                if 'label_seq_scheme' in self.reasonsForReParsing:
                    del self.reasonsForReParsing['label_seq_scheme']
                    for ps in self.__polySeq:
                        if ps['auth_chain_id'] not in self.reasonsForReParsing['global_auth_sequence_offset']:
                            if 'gap_in_auth_seq' in ps and ps['gap_in_auth_seq']:
                                offset = next(seq_id - auth_seq_id for seq_id, auth_seq_id in zip(ps['seq_id'], ps['auth_seq_id']))
                                if any(abs(seq_id - auth_seq_id - offset) > 20 for seq_id, auth_seq_id in zip(ps['seq_id'], ps['auth_seq_id'])):
                                    failed_ps = next((failed_ps for failed_ps in self.__polySeqRstFailed if failed_ps['chain_id'] == ps['auth_chain_id']), None)
                                    if failed_ps is None:
                                        continue
                                    if any(seq_id in ps['seq_id'] and seq_id not in ps['auth_seq_id'] for seq_id in failed_ps['seq_id']):
                                        seqIdRemapForRemaining.append({'chain_id': ps['auth_chain_id'], 'seq_id_dict': dict(zip(ps['seq_id'], ps['auth_seq_id']))})
                            elif any(seq_id in ps['seq_id'] and seq_id not in ps['auth_seq_id'] for seq_id in ps['seq_id']):
                                seqIdRemapForRemaining.append({'chain_id': ps['auth_chain_id'], 'seq_id_dict': dict(zip(ps['seq_id'], ps['auth_seq_id']))})
                if 'seq_id_remap' in self.reasonsForReParsing:
                    del self.reasonsForReParsing['seq_id_remap']
                if len(_seqIdRemap) > 0 and 'chain_id_remap' not in self.reasonsForReParsing:
                    _chainIds = [d['chain_id'] for d in _seqIdRemap]
                    chainIds = [k for k, v in self.reasonsForReParsing['global_auth_sequence_offset'].items() if v is not None]
                    if any(_c in chainIds for _c in _chainIds) and len(chainIds) < len(_chainIds):
                        chainIdRemap = {}
                        valid = True
                        for d in _seqIdRemap:
                            chainId = d['chain_id']
                            ps = next(ps for ps in self.__polySeq if ps['auth_chain_id'] == chainId)
                            if 'gap_in_auth_seq' in ps and ps['gap_in_auth_seq']:
                                valid = False
                                break
                            if chainId in chainIds:
                                offset = next(v for k, v in self.reasonsForReParsing['global_auth_sequence_offset'].items() if k == chainId and v is not None)
                                for auth_seq_id in ps['auth_seq_id']:
                                    if auth_seq_id - offset in chainIdRemap:
                                        valid = False
                                        break
                                    chainIdRemap[auth_seq_id - offset] = {'chain_id': chainId, 'seq_id': auth_seq_id}
                            else:
                                if label_seq_scheme:
                                    for seq_id, auth_seq_id in zip(ps['seq_id'], ps['auth_seq_id']):
                                        if seq_id in chainIdRemap:
                                            valid = False
                                            break
                                        chainIdRemap[seq_id] = {'chain_id': chainId, 'seq_id': auth_seq_id}
                                else:
                                    for auth_seq_id in ps['auth_seq_id']:
                                        if auth_seq_id in chainIdRemap:
                                            valid = False
                                            break
                                        chainIdRemap[auth_seq_id] = {'chain_id': chainId, 'seq_id': auth_seq_id}
                        if valid:
                            del self.reasonsForReParsing['global_auth_sequence_offset']
                            self.reasonsForReParsing['chain_id_remap'] = chainIdRemap

            if len(seqIdRemapForRemaining) > 0:
                self.reasonsForReParsing['seq_id_remap'] = seqIdRemapForRemaining

            if 'local_seq_scheme' in self.reasonsForReParsing and len(self.reasonsForReParsing) == 1:
                mergePolySeqRstAmbig(self.__polySeqRstFailed, self.__polySeqRstFailedAmbig)
                sortPolySeqRst(self.__polySeqRstFailed)
                if len(self.__polySeqRstFailed) > 0:
                    self.reasonsForReParsing['extend_seq_scheme'] = self.__polySeqRstFailed
                del self.reasonsForReParsing['local_seq_scheme']

            if self.__remediate:
                if self.__dist_lb_greater_than_ub and self.__dist_ub_always_positive:
                    if 'dist_unusual_order' not in self.reasonsForReParsing:
                        self.reasonsForReParsing['dist_unusual_order'] = True

            if self.hasAnyRestraints():

                if all('[Anomalous data]' in f for f in self.__f)\
                   and all('distance' in f for f in self.__f)\
                   and 'label_seq_scheme' in self.reasonsForReParsing:
                    del self.reasonsForReParsing['label_seq_scheme']
                    __f = copy.deepcopy(self.__f)
                    self.__f = []
                    for f in __f:
                        self.__f.append(re.sub(r'\[Anomalous data\]', '[Atom not found]', f, 1))

                elif all('[Anomalous data]' in f for f in self.__f):
                    pass

                elif not any(f for f in self.__f if '[Atom not found]' in f or '[Anomalous data]' in f)\
                        and 'non_poly_remap' not in self.reasonsForReParsing\
                        and 'branch_remap' not in self.reasonsForReParsing:

                    if len(self.reasonsForReParsing) > 0:
                        self.reasonsForReParsing = {}

        finally:
            self.warningMessage = sorted(list(set(self.__f)), key=self.__f.index)

    # Enter a parse tree produced by RosettaMRParser#comment.
    def enterComment(self, ctx: RosettaMRParser.CommentContext):
        if not self.__cur_comment_inlined:
            return

        if ctx.Atom_pair_selection(0):
            for atomSel in str(ctx.Atom_pair_selection(0)).split('-'):
                if self.__atom_sel_comment_pattern.match(atomSel):
                    g = self.__atom_sel_comment_pattern.search(atomSel).groups()
                    self.atomSelectionInComment.append({'comp_id': g[0], 'seq_id': int(g[1]), 'atom_id': g[2]})

        if ctx.Atom_selection(0):
            for idx in range(2):
                if ctx.Atom_selection(idx):
                    atomSel = str(ctx.Atom_selection(idx))
                    if self.__atom_sel_comment_pattern.match(atomSel):
                        g = self.__atom_sel_comment_pattern.search(atomSel).groups()
                        self.atomSelectionInComment.append({'comp_id': g[0], 'seq_id': int(g[1]), 'atom_id': g[2]})
                else:
                    self.atomSelectionInComment.clear()
                    break

    # Exit a parse tree produced by RosettaMRParser#comment.
    def exitComment(self, ctx: RosettaMRParser.CommentContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by RosettaMRParser#atom_pair_restraints.
    def enterAtom_pair_restraints(self, ctx: RosettaMRParser.Atom_pair_restraintsContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'dist'

        self.__cur_comment_inlined = True

    # Exit a parse tree produced by RosettaMRParser#atom_pair_restraints.
    def exitAtom_pair_restraints(self, ctx: RosettaMRParser.Atom_pair_restraintsContext):  # pylint: disable=unused-argument
        self.__cur_comment_inlined = False

    # Enter a parse tree produced by RosettaMRParser#atom_pair_restraint.
    def enterAtom_pair_restraint(self, ctx: RosettaMRParser.Atom_pair_restraintContext):  # pylint: disable=unused-argument
        self.distRestraints += 1

        self.stackFuncs.clear()
        self.atomSelectionSet.clear()

    # Exit a parse tree produced by RosettaMRParser#atom_pair_restraint.
    def exitAtom_pair_restraint(self, ctx: RosettaMRParser.Atom_pair_restraintContext):

        try:

            seqId1 = int(str(ctx.Integer(0)))
            atomId1 = str(ctx.Simple_name(0)).upper()
            seqId2 = int(str(ctx.Integer(1)))
            atomId2 = str(ctx.Simple_name(1)).upper()

            if len(self.atomSelectionInComment) == 2:
                matched = True
                for atomSel in self.atomSelectionInComment:
                    if atomSel['atom_id'] not in (atomId1, atomId2):
                        matched = False
                        break
                if matched:
                    for idx, atomSel in enumerate(self.atomSelectionInComment):
                        if idx == 0:
                            seqId1 = atomSel['seq_id']
                            atomId1 = atomSel['atom_id']
                        else:
                            seqId2 = atomSel['seq_id']
                            atomId2 = atomSel['atom_id']

            if not self.__hasPolySeq and not self.__hasNonPolySeq:
                return

            self.__retrieveLocalSeqScheme()

            chainAssign1 = self.assignCoordPolymerSequence(seqId1, atomId1)
            chainAssign2 = self.assignCoordPolymerSequence(seqId2, atomId2)

            if 0 in (len(chainAssign1), len(chainAssign2)):
                return

            self.selectCoordAtoms(chainAssign1, seqId1, atomId1)
            self.selectCoordAtoms(chainAssign2, seqId2, atomId2)

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

            dstFunc = self.validateDistanceRange(1.0)

            if dstFunc is None:
                return

            isNested = len(self.stackNest) > 0
            isMulti = isNested and self.stackNest[-1]['type'] == 'multi'

            if self.__createSfDict:
                sf = self.__getSf(constraintType=getDistConstraintType(self.atomSelectionSet, dstFunc,
                                                                       self.__csStat, self.__originalFileName),
                                  potentialType=getPotentialType(self.__file_type, self.__cur_subtype, dstFunc))
                if not isNested or self.__is_first_nest:
                    sf['id'] += 1
                memberLogicCode = 'OR' if len(self.atomSelectionSet[0]) * len(self.atomSelectionSet[1]) > 1 or isNested else '.'

            if isNested:
                if self.__debug:
                    print(f"NESTED: {self.stackNest}")

            has_intra_chain, rep_chain_id_set = hasIntraChainRestraint(self.atomSelectionSet)

            combinationId = '.'
            if isNested and self.__nest_combination_id > 0:
                combinationId = self.__nest_combination_id

            memberId = '.'
            if self.__createSfDict:
                if memberLogicCode == 'OR' and has_intra_chain and len(rep_chain_id_set) == 1 and not isNested:
                    if not self.atomSelectionSet[0][0]['auth_atom_id'].upper().startswith('CEN')\
                       and not self.atomSelectionSet[1][0]['auth_atom_id'].upper().startswith('CEN'):
                        memberLogicCode = '.'

                if memberLogicCode == 'OR':
                    if isNested:
                        memberId = self.__nest_member_id
                        _atom1 = _atom2 = None
                    elif len(self.atomSelectionSet[0]) * len(self.atomSelectionSet[1]) > 1\
                            and (isAmbigAtomSelection(self.atomSelectionSet[0], self.__csStat)
                                 or isAmbigAtomSelection(self.atomSelectionSet[1], self.__csStat)):
                        memberId = 0
                        _atom1 = _atom2 = None

                combinationId = '.'
                if isNested and self.__nest_combination_id > 0:
                    combinationId = self.__nest_combination_id

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
                    print(f"subtype={self.__cur_subtype} id={self.distRestraints} "
                          f"atom1={atom1} atom2={atom2} {dstFunc}")
                if self.__createSfDict and sf is not None:
                    if isinstance(memberId, int):
                        if isNested:
                            memberId += 1
                            self.__nest_member_id = memberId
                            _atom1, _atom2 = atom1, atom2
                        elif _atom1 is None or isAmbigAtomSelection([_atom1, atom1], self.__csStat)\
                                or isAmbigAtomSelection([_atom2, atom2], self.__csStat):
                            memberId += 1
                            _atom1, _atom2 = atom1, atom2
                    sf['index_id'] += 1
                    row = getRow(self.__cur_subtype, sf['id'], sf['index_id'],
                                 combinationId, memberId, 'AND' if isMulti else memberLogicCode,
                                 sf['list_id'], self.__entryId, dstFunc,
                                 self.__authToStarSeq, self.__authToOrigSeq, self.__authToInsCode, self.__offsetHolder,
                                 atom1, atom2)
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

            if self.__createSfDict and sf is not None:
                if isinstance(memberId, int) and memberId == 1:
                    sf['loop'].data[-1] = resetMemberId(self.__cur_subtype, sf['loop'].data[-1])
                    memberId = '.'
                if isinstance(memberId, str) and isinstance(combinationId, int) and combinationId == 1:
                    sf['loop'].data[-1] = resetCombinationId(self.__cur_subtype, sf['loop'].data[-1])

        finally:
            self.atomSelectionInComment.clear()

    def validateDistanceRange(self, weight: float) -> Optional[dict]:
        """ Validate distance value range.
        """

        target_value = None
        lower_limit = None
        upper_limit = None
        lower_linear_limit = None
        upper_linear_limit = None

        firstFunc = None
        srcFunc = None

        level = 0
        while self.stackFuncs:
            func = self.stackFuncs.pop()
            if func is not None:
                if firstFunc is None:
                    firstFunc = copy.copy(func)
                if func['name'] in ('SCALARWEIGHTEDFUNC', 'SUMFUNC'):
                    continue
                if 'func_types' in firstFunc:
                    firstFunc['func_types'].append(func['name'])
                if srcFunc is None:
                    srcFunc = copy.copy(func)
                if 'target_value' in func:
                    target_value = func['target_value']
                    del srcFunc['target_value']
                if 'lower_limit' in func:
                    lower_limit = func['lower_limit']
                    del srcFunc['lower_limit']
                if 'upper_limit' in func:
                    upper_limit = func['upper_limit']
                    del srcFunc['upper_limit']
                if 'lower_linear_limit' in func:
                    lower_linear_limit = func['lower_linear_limit']
                    del srcFunc['lower_linear_limit']
                if 'upper_linear_limit' in func:
                    upper_linear_limit = func['upper_linear_limit']
                    del srcFunc['upper_linear_limit']
                level += 1

        if srcFunc is None:  # errors are already caught
            return None

        if level > 1:
            self.__f.append(f"[Unsupported data] {self.__getCurrentRestraint()}"
                            f"Too complex constraint function {firstFunc} can not be converted to NEF/NMR-STAR data.")
            return None

        if target_value is None and lower_limit is None and upper_limit is None\
           and lower_linear_limit is None and upper_linear_limit is None:
            self.__f.append(f"[Unsupported data] {self.__getCurrentRestraint()}"
                            f"The constraint function {srcFunc} can not be converted to NEF/NMR-STAR data.")
            return None

        validRange = True
        dstFunc = {'weight': weight}

        if None not in (target_value, upper_limit, lower_limit)\
           and abs(target_value - lower_limit) <= DIST_AMBIG_UNCERT\
           and abs(target_value - upper_limit) <= DIST_AMBIG_UNCERT:
            if target_value >= DIST_AMBIG_MED:
                lower_limit = lower_linear_limit = None
            elif target_value <= DIST_AMBIG_LOW:
                upper_limit = upper_linear_limit = None

        if target_value is not None:
            if DIST_ERROR_MIN < target_value < DIST_ERROR_MAX or (target_value == 0.0 and self.__allowZeroUpperLimit):
                dstFunc['target_value'] = f"{target_value}" if target_value > 0.0 else "0.0"
            else:
                if target_value <= DIST_ERROR_MIN and self.__omitDistLimitOutlier:
                    self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                    f"{srcFunc}, the target value='{target_value}' is omitted because it is not within range {DIST_RESTRAINT_ERROR}.")
                    target_value = None
                else:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                    f"{srcFunc}, the target value='{target_value}' must be within range {DIST_RESTRAINT_ERROR}.")

        if lower_limit is not None:
            if DIST_ERROR_MIN <= lower_limit < DIST_ERROR_MAX:
                dstFunc['lower_limit'] = f"{lower_limit:.6f}" if lower_limit > 0.0 else "0.0"
            else:
                if lower_limit <= DIST_ERROR_MIN and self.__omitDistLimitOutlier:
                    self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                    f"{srcFunc}, the lower limit value='{lower_limit}' is omitted because it is not within range {DIST_RESTRAINT_ERROR}.")
                    lower_limit = None
                else:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                    f"{srcFunc}, the lower limit value='{lower_limit}' must be within range {DIST_RESTRAINT_ERROR}.")

        if upper_limit is not None:
            if DIST_ERROR_MIN < upper_limit <= DIST_ERROR_MAX or (upper_limit == 0.0 and self.__allowZeroUpperLimit):
                dstFunc['upper_limit'] = f"{upper_limit:.6f}" if upper_limit > 0.0 else "0.0"
            else:
                if (upper_limit <= DIST_ERROR_MIN or upper_limit > DIST_ERROR_MAX) and self.__omitDistLimitOutlier:
                    self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                    f"{srcFunc}, the upper limit value='{upper_limit}' is omitted because it is not within range {DIST_RESTRAINT_ERROR}.")
                    upper_limit = None
                else:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                    f"{srcFunc}, the upper limit value='{upper_limit}' must be within range {DIST_RESTRAINT_ERROR}.")

        if lower_linear_limit is not None:
            if DIST_ERROR_MIN <= lower_linear_limit < DIST_ERROR_MAX:
                dstFunc['lower_linear_limit'] = f"{lower_linear_limit:.6f}" if lower_linear_limit > 0.0 else "0.0"
            else:
                if lower_linear_limit <= DIST_ERROR_MIN and self.__omitDistLimitOutlier:
                    self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                    f"{srcFunc}, the lower linear limit value='{lower_linear_limit}' is omitted because it is not within range {DIST_RESTRAINT_ERROR}.")
                    lower_linear_limit = None
                else:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                    f"{srcFunc}, the lower linear limit value='{lower_linear_limit}' must be within range {DIST_RESTRAINT_ERROR}.")

        if upper_linear_limit is not None:
            if DIST_ERROR_MIN < upper_linear_limit <= DIST_ERROR_MAX or (upper_linear_limit == 0.0 and self.__allowZeroUpperLimit):
                dstFunc['upper_linear_limit'] = f"{upper_linear_limit:.6f}" if upper_linear_limit > 0.0 else "0.0"
            else:
                if (upper_linear_limit <= DIST_ERROR_MIN or upper_linear_limit > DIST_ERROR_MAX) and self.__omitDistLimitOutlier:
                    self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                    f"The upper linear limit value='{upper_linear_limit}' is omitted because it is not within range {DIST_RESTRAINT_ERROR}.")
                    upper_linear_limit = None
                else:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                    f"{srcFunc}, the upper linear limit value='{upper_linear_limit}' must be within range {DIST_RESTRAINT_ERROR}.")

        if target_value is not None:

            if lower_limit is not None:
                if lower_limit > target_value:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                    f"{srcFunc}, the lower limit value='{lower_limit}' must be less than the target value '{target_value}'.")

            if lower_linear_limit is not None:
                if lower_linear_limit > target_value:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                    f"{srcFunc}, the lower linear limit value='{lower_linear_limit}' must be less than the target value '{target_value}'.")

            if upper_limit is not None:
                if upper_limit < target_value:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                    f"{srcFunc}, the upper limit value='{upper_limit}' must be greater than the target value '{target_value}'.")

            if upper_linear_limit is not None:
                if upper_linear_limit < target_value:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                    f"{srcFunc}, the upper linear limit value='{upper_linear_limit}' must be greater than the target value '{target_value}'.")

        else:

            if None not in (lower_limit, upper_limit):
                if lower_limit > upper_limit:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                    f"{srcFunc}, the lower limit value='{lower_limit}' must be less than the upper limit value '{upper_limit}'.")

            if None not in (lower_linear_limit, upper_limit):
                if lower_linear_limit > upper_limit:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                    f"{srcFunc}, the lower linear limit value='{lower_linear_limit}' must be less than the upper limit value '{upper_limit}'.")

            if None not in (lower_limit, upper_linear_limit):
                if lower_limit > upper_linear_limit:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                    f"{srcFunc}, the lower limit value='{lower_limit}' must be less than the upper limit value '{upper_linear_limit}'.")

            if None not in (lower_linear_limit, upper_linear_limit):
                if lower_linear_limit > upper_linear_limit:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                    f"{srcFunc}, the lower linear limit value='{lower_linear_limit}' must be less than the upper limit value '{upper_linear_limit}'.")

            if None not in (lower_limit, lower_linear_limit):
                if lower_linear_limit > lower_limit:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                    f"{srcFunc}, the lower linear limit value='{lower_linear_limit}' must be less than the lower limit value '{lower_limit}'.")

            if None not in (upper_limit, upper_linear_limit):
                if upper_limit > upper_linear_limit:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                    f"{srcFunc}, the upper limit value='{upper_limit}' must be less than the upper linear limit value '{upper_linear_limit}'.")

        if not validRange:
            return None

        if target_value is not None:
            if DIST_RANGE_MIN <= target_value <= DIST_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                f"{srcFunc}, the target value='{target_value}' should be within range {DIST_RESTRAINT_RANGE}.")

        if lower_limit is not None:
            if DIST_RANGE_MIN <= lower_limit <= DIST_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                f"{srcFunc}, the lower limit value='{lower_limit}' should be within range {DIST_RESTRAINT_RANGE}.")

        if upper_limit is not None:
            if DIST_RANGE_MIN <= upper_limit <= DIST_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                f"{srcFunc}, the upper limit value='{upper_limit}' should be within range {DIST_RESTRAINT_RANGE}.")

        if lower_linear_limit is not None:
            if DIST_RANGE_MIN <= lower_linear_limit <= DIST_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                f"{srcFunc}, the lower linear limit value='{lower_linear_limit}' should be within range {DIST_RESTRAINT_RANGE}.")

        if upper_linear_limit is not None:
            if DIST_RANGE_MIN <= upper_linear_limit <= DIST_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                f"{srcFunc}, the upper linear limit value='{upper_linear_limit}' should be within range {DIST_RESTRAINT_RANGE}.")

        if target_value is None and lower_limit is None and upper_limit is None and lower_linear_limit is None and upper_linear_limit is None:
            return None

        return dstFunc

    def getRealChainSeqId(self, ps: dict, seqId: int, isPolySeq: bool = True) -> Tuple[str, int, Optional[str]]:
        offset = 0
        if not self.__preferAuthSeq:
            if isPolySeq and self.__reasons is not None and 'global_auth_sequence_offset' in self.__reasons\
               and ps['auth_chain_id'] in self.__reasons['global_auth_sequence_offset']:
                offset = self.__reasons['global_auth_sequence_offset'][ps['auth_chain_id']]
                if isinstance(offset, dict):
                    if seqId in offset:
                        offset = offset[seqId]
                    else:
                        for shift in range(1, 100):
                            if seqId + shift in offset:
                                offset = offset[seqId + shift]
                                break
                            if seqId - shift in offset:
                                offset = offset[seqId - shift]
                                break
                if seqId + offset in ps['auth_seq_id']:
                    return ps['auth_chain_id'], seqId + offset, ps['comp_id'][ps['auth_seq_id'].index(seqId + offset)]
            seqKey = (ps['auth_chain_id'], seqId)
            if seqKey in self.__labelToAuthSeq:
                _chainId, _seqId = self.__labelToAuthSeq[seqKey]
                if _seqId in ps['auth_seq_id']:
                    return _chainId, _seqId, ps['comp_id'][ps['auth_seq_id'].index(_seqId)]
                if seqKey[1] in ps['seq_id']:  # resolve conflict between label/auth sequence schemes of polymer/non-polymer (2l90)
                    idx = ps['seq_id'].index(seqKey[1])
                    return _chainId, ps['auth_seq_id'][idx], ps['comp_id'][idx]
        else:
            if isPolySeq and self.__reasons is not None and 'global_auth_sequence_offset' in self.__reasons\
               and ps['auth_chain_id'] in self.__reasons['global_auth_sequence_offset']:
                offset = self.__reasons['global_auth_sequence_offset'][ps['auth_chain_id']]
                if isinstance(offset, dict):
                    if seqId in offset:
                        offset = offset[seqId]
                    else:
                        for shift in range(1, 100):
                            if seqId + shift in offset:
                                offset = offset[seqId + shift]
                                break
                            if seqId - shift in offset:
                                offset = offset[seqId - shift]
                                break
        if seqId + offset in ps['auth_seq_id']:
            return ps['auth_chain_id'], seqId + offset, ps['comp_id'][ps['auth_seq_id'].index(seqId + offset)]
        if self.__reasons is not None and 'extend_seq_scheme' in self.__reasons:
            _ps = next((_ps for _ps in self.__reasons['extend_seq_scheme'] if _ps['chain_id'] == ps['auth_chain_id']), None)
            if _ps is not None:
                if seqId + offset in _ps['seq_id']:
                    return ps['auth_chain_id'], seqId + offset, _ps['comp_id'][_ps['seq_id'].index(seqId + offset)]
        return ps['auth_chain_id'], seqId, None

    def assignCoordPolymerSequence(self, seqId: int, atomId: Optional[str] = None, fixedChainId: Optional[str] = None
                                   ) -> List[Tuple[str, int, str, bool]]:
        """ Assign polymer sequences of the coordinates.
        """

        chainAssign = set()
        _seqId = seqId

        fixedSeqId = fixedCompId = None

        self.__allow_ext_seq = False

        if self.__reasons is not None:
            if 'branched_remap' in self.__reasons and seqId in self.__reasons['branched_remap']:
                fixedChainId, fixedSeqId = retrieveRemappedChainId(self.__reasons['branched_remap'], seqId)
            if 'chain_id_remap' in self.__reasons and seqId in self.__reasons['chain_id_remap']:
                fixedChainId, fixedSeqId = retrieveRemappedChainId(self.__reasons['chain_id_remap'], seqId)
            elif 'chain_id_clone' in self.__reasons and seqId in self.__reasons['chain_id_clone']:
                fixedChainId, fixedSeqId = retrieveRemappedChainId(self.__reasons['chain_id_clone'], seqId)
            if fixedSeqId is not None:
                seqId = _seqId = fixedSeqId

        for ps in self.__polySeq:
            chainId, seqId, fixedCompId = self.getRealChainSeqId(ps, _seqId)
            if self.__reasons is not None:
                if 'seq_id_remap' not in self.__reasons\
                   and 'chain_seq_id_remap' not in self.__reasons\
                   and 'ext_chain_seq_id_remap' not in self.__reasons:
                    if fixedChainId is not None and fixedChainId != chainId:
                        continue
                elif 'global_auth_sequence_offset' not in self.__reasons:
                    if 'ext_chain_seq_id_remap' in self.__reasons:
                        fixedChainId, fixedSeqId, fixedCompId =\
                            retrieveRemappedSeqIdAndCompId(self.__reasons['ext_chain_seq_id_remap'], chainId, seqId)
                        if fixedChainId is not None and fixedChainId != chainId:
                            continue
                        if fixedSeqId is not None:
                            self.__allow_ext_seq = fixedCompId is not None
                            seqId = _seqId = fixedSeqId
                    if fixedSeqId is None and 'chain_seq_id_remap' in self.__reasons:
                        fixedChainId, fixedSeqId = retrieveRemappedSeqId(self.__reasons['chain_seq_id_remap'], chainId, seqId)
                        if fixedChainId is not None and fixedChainId != chainId:
                            continue
                        if fixedSeqId is not None:
                            seqId = _seqId = fixedSeqId
                    if fixedSeqId is None and 'seq_id_remap' in self.__reasons:
                        _, fixedSeqId = retrieveRemappedSeqId(self.__reasons['seq_id_remap'], chainId, seqId)
                        if fixedSeqId is not None:
                            seqId = _seqId = fixedSeqId
            if fixedChainId is not None and chainId != fixedChainId:
                continue
            if seqId in ps['auth_seq_id'] or fixedCompId is not None:
                if fixedCompId is not None:
                    cifCompId = fixedCompId
                else:
                    idx = ps['auth_seq_id'].index(seqId)
                    cifCompId = ps['comp_id'][idx]
                if self.__reasons is not None:
                    if 'non_poly_remap' in self.__reasons and cifCompId in self.__reasons['non_poly_remap']\
                       and seqId in self.__reasons['non_poly_remap'][cifCompId]:
                        fixedChainId, fixedSeqId = retrieveRemappedNonPoly(self.__reasons['non_poly_remap'], None, chainId, seqId, cifCompId)
                        if fixedSeqId is not None:
                            seqId = _seqId = fixedSeqId
                        if (fixedChainId is not None and fixedChainId != chainId) or seqId not in ps['auth_seq_id']:
                            continue
                updatePolySeqRst(self.__polySeqRst, chainId, _seqId, cifCompId)
                if atomId is not None and cifCompId not in monDict3 and self.__mrAtomNameMapping:
                    _, coordAtomSite = self.getCoordAtomSiteOf(chainId, seqId, cifCheck=self.__hasCoord)
                    origCompId = ps['auth_comp_id'][idx]
                    atomId = retrieveAtomIdFromMRMap(self.__ccU, self.__mrAtomNameMapping, seqId, origCompId, atomId, coordAtomSite)
                if atomId is None\
                   or (atomId is not None and len(self.__nefT.get_valid_star_atom(cifCompId, atomId)[0]) > 0):
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
                                updatePolySeqRst(self.__polySeqRst, chainId, _seqId, cifCompId)
                                if atomId is not None and cifCompId not in monDict3 and self.__mrAtomNameMapping:
                                    _, coordAtomSite = self.getCoordAtomSiteOf(chainId, seqId_, cifCheck=self.__hasCoord)
                                    origCompId = ps['auth_comp_id'][idx]
                                    atomId = retrieveAtomIdFromMRMap(self.__ccU, self.__mrAtomNameMapping, seqId, origCompId, atomId, coordAtomSite)
                                if atomId is None\
                                   or (atomId is not None and len(self.__nefT.get_valid_star_atom(cifCompId, atomId)[0]) > 0):
                                    chainAssign.add((chainId, seqId_, cifCompId, True))
                            except IndexError:
                                pass

        if self.__hasNonPolySeq:
            if self.__hasNonPoly:
                for np in self.__nonPoly:
                    chainId, seqId, fixedCompId = self.getRealChainSeqId(np, _seqId, False)
                    if seqId in np['auth_seq_id'] or fixedCompId is not None:
                        if fixedCompId is not None:
                            cifCompId = fixedCompId
                        else:
                            idx = np['auth_seq_id'].index(seqId)
                            cifCompId = np['comp_id'][idx]
                        if self.__reasons is not None:
                            if 'non_poly_remap' in self.__reasons and cifCompId in self.__reasons['non_poly_remap']\
                               and seqId in self.__reasons['non_poly_remap'][cifCompId]:
                                fixedChainId, fixedSeqId = retrieveRemappedNonPoly(self.__reasons['non_poly_remap'], None, chainId, seqId, cifCompId)
                                if fixedSeqId is not None:
                                    seqId = _seqId = fixedSeqId
                        elif self.__uniqAtomIdToSeqKey is not None and atomId in self.__uniqAtomIdToSeqKey:
                            seqKey = self.__uniqAtomIdToSeqKey[atomId]
                            if _seqId != seqKey[1] and seqKey in self.__coordAtomSite:
                                if 'non_poly_remap' not in self.reasonsForReParsing:
                                    self.reasonsForReParsing['non_poly_remap'] = {}
                                if cifCompId not in self.reasonsForReParsing['non_poly_remap']:
                                    self.reasonsForReParsing['non_poly_remap'][cifCompId] = {}
                                if _seqId not in self.reasonsForReParsing['non_poly_remap'][cifCompId]:
                                    self.reasonsForReParsing['non_poly_remap'][cifCompId][_seqId] =\
                                        {'chain_id': seqKey[0],
                                         'seq_id': seqKey[1],
                                         'original_chain_id': None}
            for np in self.__nonPolySeq:
                chainId, seqId, _ = self.getRealChainSeqId(np, _seqId, False)
                if self.__reasons is not None:
                    if 'seq_id_remap' not in self.__reasons and 'chain_seq_id_remap' not in self.__reasons:
                        if fixedChainId is not None and fixedChainId != chainId:
                            continue
                    else:
                        if 'chain_seq_id_remap' in self.__reasons:
                            fixedChainId, fixedSeqId = retrieveRemappedSeqId(self.__reasons['chain_seq_id_remap'], chainId, seqId)
                            if fixedChainId is not None and fixedChainId != chainId:
                                continue
                            if fixedSeqId is not None:
                                seqId = _seqId = fixedSeqId
                        if fixedSeqId is None and 'seq_id_remap' in self.__reasons:
                            _, fixedSeqId = retrieveRemappedSeqId(self.__reasons['seq_id_remap'], chainId, seqId)
                            if fixedSeqId is not None:
                                seqId = _seqId = fixedSeqId
                if seqId in np['auth_seq_id']:
                    idx = np['auth_seq_id'].index(seqId)
                    cifCompId = np['comp_id'][idx]
                    updatePolySeqRst(self.__polySeqRst, chainId, _seqId, cifCompId)
                    if atomId is not None and cifCompId not in monDict3 and self.__mrAtomNameMapping:
                        _, coordAtomSite = self.getCoordAtomSiteOf(chainId, seqId, cifCheck=self.__hasCoord)
                        origCompId = np['auth_comp_id'][idx]
                        atomId = retrieveAtomIdFromMRMap(self.__ccU, self.__mrAtomNameMapping, seqId, origCompId, atomId, coordAtomSite)
                    if 'alt_auth_seq_id' in np and seqId in np['auth_seq_id'] and seqId not in np['alt_auth_seq_id']:
                        try:
                            seqId = next(_altSeqId for _seqId, _altSeqId in zip(np['auth_seq_id'], np['alt_auth_seq_id']) if _seqId == seqId)
                        except StopIteration:
                            pass
                    if atomId is None\
                       or (atomId is not None and len(self.__nefT.get_valid_star_atom(cifCompId, atomId)[0]) > 0):
                        chainAssign.add((chainId, seqId, cifCompId, False))

        if len(chainAssign) == 0:
            for ps in self.__polySeq:
                chainId = ps['chain_id']
                if fixedChainId is not None and chainId != fixedChainId:
                    continue
                seqKey = (chainId, _seqId)
                if seqKey in self.__authToLabelSeq:
                    _, seqId = self.__authToLabelSeq[seqKey]
                    if seqId in ps['seq_id']:
                        idx = ps['seq_id'].index(seqId)
                        cifCompId = ps['comp_id'][idx]
                        updatePolySeqRst(self.__polySeqRst, chainId, _seqId, cifCompId)
                        if atomId is not None and cifCompId not in monDict3 and self.__mrAtomNameMapping:
                            _, coordAtomSite = self.getCoordAtomSiteOf(chainId, _seqId, cifCheck=self.__hasCoord)
                            origCompId = ps['auth_comp_id'][idx]
                            atomId = retrieveAtomIdFromMRMap(self.__ccU, self.__mrAtomNameMapping, seqId, origCompId, atomId, coordAtomSite)
                        if atomId is None\
                           or (atomId is not None and len(self.__nefT.get_valid_star_atom(cifCompId, atomId)[0]) > 0):
                            chainAssign.add((ps['auth_chain_id'], _seqId, cifCompId, True))

            if self.__hasNonPolySeq:
                for np in self.__nonPolySeq:
                    chainId = np['auth_chain_id']
                    if fixedChainId is not None and chainId != fixedChainId:
                        continue
                    seqKey = (chainId, _seqId)
                    if seqKey in self.__authToLabelSeq:
                        _, seqId = self.__authToLabelSeq[seqKey]
                        if seqId in np['seq_id']:
                            idx = np['seq_id'].index(seqId)
                            cifCompId = np['comp_id'][idx]
                            updatePolySeqRst(self.__polySeqRst, chainId, _seqId, cifCompId)
                            if atomId is not None and cifCompId not in monDict3 and self.__mrAtomNameMapping:
                                _, coordAtomSite = self.getCoordAtomSiteOf(chainId, _seqId, cifCheck=self.__hasCoord)
                                origCompId = np['auth_comp_id'][idx]
                                atomId = retrieveAtomIdFromMRMap(self.__ccU, self.__mrAtomNameMapping, seqId, origCompId, atomId, coordAtomSite)
                            if atomId is None\
                               or (atomId is not None and len(self.__nefT.get_valid_star_atom(cifCompId, atomId)[0]) > 0):
                                chainAssign.add((np['auth_chain_id'], _seqId, cifCompId, False))

        if len(chainAssign) == 0 and self.__altPolySeq is not None:
            for ps in self.__altPolySeq:
                chainId = ps['auth_chain_id']
                if fixedChainId is not None and chainId != fixedChainId:
                    continue
                if _seqId in ps['auth_seq_id']:
                    cifCompId = ps['comp_id'][ps['auth_seq_id'].index(_seqId)]
                    updatePolySeqRst(self.__polySeqRst, chainId, _seqId, cifCompId)
                    chainAssign.add((chainId, _seqId, cifCompId, True))

        if len(chainAssign) == 0 and (self.__preferAuthSeqCount - self.__preferLabelSeqCount < MAX_PREF_LABEL_SCHEME_COUNT or len(self.__polySeq) > 1):
            for ps in self.__polySeq:
                chainId = ps['chain_id']
                if fixedChainId is not None and chainId != fixedChainId:
                    continue
                seqKey = (chainId, _seqId)
                if seqKey in self.__labelToAuthSeq:
                    _, seqId = self.__labelToAuthSeq[seqKey]
                    if seqId in ps['auth_seq_id']:
                        idx = ps['seq_id'].index(_seqId)
                        cifCompId = ps['comp_id'][idx]
                        updatePolySeqRst(self.__polySeqRst, chainId, seqId, cifCompId)
                        if atomId is not None and cifCompId not in monDict3 and self.__mrAtomNameMapping:
                            _, coordAtomSite = self.getCoordAtomSiteOf(chainId, seqId, cifCheck=self.__hasCoord)
                            origCompId = ps['auth_comp_id'][idx]
                            atomId = retrieveAtomIdFromMRMap(self.__ccU, self.__mrAtomNameMapping, seqId, origCompId, atomId, coordAtomSite)
                        if atomId is None\
                           or (atomId is not None and len(self.__nefT.get_valid_star_atom(cifCompId, atomId)[0]) > 0):
                            chainAssign.add((ps['auth_chain_id'], seqId, cifCompId, True))
                            self.__authSeqId = 'label_seq_id'
                            self.__setLocalSeqScheme()

        if len(chainAssign) == 0:
            if atomId is not None:
                if seqId == 1 or (chainId if fixedChainId is None else fixedChainId, seqId - 1) in self.__coordUnobsRes:
                    if atomId in aminoProtonCode and atomId != 'H1':
                        return self.assignCoordPolymerSequence(seqId, 'H1', fixedChainId)
                if len(self.__polySeq) == 1 and seqId < 1:
                    refChainId = self.__polySeq[0]['auth_chain_id']
                    self.__f.append(f"[Atom not found] {self.__getCurrentRestraint()}"
                                    f"{_seqId}:?:{atomId} is not present in the coordinates. "
                                    f"The residue number '{_seqId}' is not present in polymer sequence "
                                    f"of chain {refChainId} of the coordinates. "
                                    "Please update the sequence in the Macromolecules page.")
                else:
                    ext_seq = False
                    if self.__reasons is None and (self.__preferAuthSeqCount - self.__preferLabelSeqCount >= MAX_PREF_LABEL_SCHEME_COUNT or atomId == 'H'):
                        auth_seq_id_list = list(filter(None, self.__polySeq[0]['auth_seq_id']))
                        min_auth_seq_id = max_auth_seq_id = UNREAL_AUTH_SEQ_NUM
                        if len(auth_seq_id_list) > 0:
                            min_auth_seq_id = min(auth_seq_id_list)
                            max_auth_seq_id = max(auth_seq_id_list)
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
                                if (seqId < min_auth_seq_id or seqId > max_auth_seq_id)\
                                   and self.__preferAuthSeqCount - self.__preferLabelSeqCount >= MAX_PREF_LABEL_SCHEME_COUNT:
                                    refChainIds.append(ps['auth_chain_id'])
                                    ext_seq = True
                        if ext_seq and seqId in _auth_seq_id_list:
                            ext_seq = False
                    if ext_seq:
                        refChainId = refChainIds[0] if len(refChainIds) == 1 else refChainIds
                        self.__f.append(f"[Sequence mismatch warning] {self.__getCurrentRestraint()}"
                                        f"The residue '{_seqId}' is not present in polymer sequence "
                                        f"of chain {refChainId} of the coordinates. "
                                        "Please update the sequence in the Macromolecules page.")
                    else:
                        self.__f.append(f"[Atom not found] {self.__getCurrentRestraint()}"
                                        f"{_seqId}:{atomId} is not present in the coordinates.")
                        compIds = guessCompIdFromAtomId([atomId], self.__polySeq, self.__nefT)
                        if compIds is not None:
                            chainId = fixedChainId
                            if chainId is None and len(self.__polySeq) == 1:
                                chainId = self.__polySeq[0]['chain_id']
                            if chainId is not None:
                                if len(compIds) == 1:
                                    updatePolySeqRst(self.__polySeqRstFailed, chainId, seqId, compIds[0])
                                else:
                                    updatePolySeqRstAmbig(self.__polySeqRstFailedAmbig, chainId, seqId, compIds)

            else:
                if len(self.__polySeq) == 1 and seqId < 1:
                    refChainId = self.__polySeq[0]['auth_chain_id']
                    self.__f.append(f"[Atom not found] {self.__getCurrentRestraint()}"
                                    f"The residue number '{_seqId}' is not present in polymer sequence "
                                    f"of chain {refChainId} of the coordinates. "
                                    "Please update the sequence in the Macromolecules page.")
                else:
                    self.__f.append(f"[Atom not found] {self.__getCurrentRestraint()}"
                                    f"The residue number '{_seqId}' is not present in the coordinates.")

        return list(chainAssign)

    def selectCoordAtoms(self, chainAssign: List[Tuple[str, int, str, bool]], seqId: int, atomId: str,
                         allowAmbig: bool = True, subtype_name: Optional[str] = None):
        """ Select atoms of the coordinates.
        """

        atomSelection = []

        authAtomId = atomId

        for chainId, cifSeqId, cifCompId, isPolySeq in chainAssign:

            seqKey, coordAtomSite = self.getCoordAtomSiteOf(chainId, cifSeqId, asis=self.__preferAuthSeq)

            if self.__mrAtomNameMapping is not None and cifCompId not in monDict3:
                _atomId_ = retrieveAtomIdFromMRMap(self.__ccU, self.__mrAtomNameMapping, cifSeqId, cifCompId, atomId, coordAtomSite)
                if atomId != _atomId_ and coordAtomSite is not None\
                   and (_atomId_ in coordAtomSite['atom_id'] or (_atomId_.endswith('%') and _atomId_[:-1] + '2' in coordAtomSite['atom_id'])):
                    atomId = _atomId_
                elif self.__reasons is not None and 'branched_remap' in self.__reasons:
                    _seqId = retrieveOriginalSeqIdFromMRMap(self.__reasons['branched_remap'], chainId, cifSeqId)
                    if _seqId != cifSeqId:
                        _, _, atomId = retrieveAtomIdentFromMRMap(self.__ccU, self.__mrAtomNameMapping, _seqId, cifCompId, atomId, None, coordAtomSite)

            _atomId = []
            if not isPolySeq and atomId[0] in ('Q', 'M') and coordAtomSite is not None:
                key = (chainId, cifSeqId, cifCompId, atomId)
                if key in self.__cachedDictForStarAtom:
                    _atomId = copy.deepcopy(self.__cachedDictForStarAtom[key])
                else:
                    pattern = re.compile(fr'H{atomId[1:]}\d+') if cifCompId in monDict3 else re.compile(fr'H{atomId[1:]}\S?$')
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
                if details is not None and len(atomId) > 1 and not atomId[-1].isalpha():
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
                elif seqId == 1 and atomId == 'H1' and self.__csStat.peptideLike(cifCompId) and 'H' in coordAtomSite['atom_id']:
                    _atomId = ['H']

            if authAtomId.upper().startswith('CEN') and len(_atomId) == 0:
                peptide, nucleotide, carbohydrate = self.__csStat.getTypeOfCompId(cifCompId)
                _atomId = self.__csStat.getCentroidAtoms(cifCompId, False, peptide, nucleotide, carbohydrate)

            if coordAtomSite is None and not isPolySeq and self.__hasNonPolySeq:
                try:
                    for np in self.__nonPolySeq:
                        if np['auth_chain_id'] == chainId and cifSeqId in np['auth_seq_id']:
                            cifSeqId = np['seq_id'][np['auth_seq_id'].index(cifSeqId)]
                            seqKey, coordAtomSite = self.getCoordAtomSiteOf(chainId, cifSeqId)
                            if coordAtomSite is not None:
                                break
                except ValueError:
                    pass

            if coordAtomSite is not None:
                atomSiteAtomId = coordAtomSite['atom_id']
                if len(_atomId) == 0 and authAtomId in zincIonCode and 'ZN' in atomSiteAtomId:
                    atomId = 'ZN'
                    _atomId = [atomId]
                elif len(_atomId) == 0 and authAtomId in calciumIonCode and 'CA' in atomSiteAtomId:
                    atomId = 'CA'
                    _atomId = [atomId]
                elif not any(_atomId_ in atomSiteAtomId for _atomId_ in _atomId):
                    pass
                elif atomId[0] not in pseProBeginCode and not all(_atomId in atomSiteAtomId for _atomId in _atomId):
                    _atomId = [_atomId_ for _atomId_ in _atomId if _atomId_ in atomSiteAtomId]

            lenAtomId = len(_atomId)
            if lenAtomId == 0:
                self.__f.append(f"[Invalid atom nomenclature] {self.__getCurrentRestraint()}"
                                f"{seqId}:{authAtomId} is invalid atom nomenclature.")
                compIds = guessCompIdFromAtomId([authAtomId], self.__polySeq, self.__nefT)
                if compIds is not None:
                    if len(compIds) == 1:
                        updatePolySeqRst(self.__polySeqRstFailed, chainId, seqId, compIds[0])
                    else:
                        updatePolySeqRstAmbig(self.__polySeqRstFailedAmbig, chainId, seqId, compIds)
                continue
            if lenAtomId > 1 and not allowAmbig:
                self.__f.append(f"[Invalid atom selection] {self.__getCurrentRestraint()}"
                                f"Ambiguous atom selection '{seqId}:{authAtomId}' is not allowed as {subtype_name} restraint.")
                continue

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

                _cifAtomId, asis = self.testCoordAtomIdConsistency(chainId, cifSeqId, cifCompId, cifAtomId, seqKey, coordAtomSite)
                if asis:
                    atomSelection[-1]['asis'] = True
                if cifAtomId != _cifAtomId:
                    atomSelection[-1]['atom_id'] = _cifAtomId

        if len(atomSelection) > 0:
            self.atomSelectionSet.append(atomSelection)

    def selectCoordResidues(self, chainAssign: List[Tuple[str, int, str, bool]], seqId: int):
        """ Select residues of the coordinates.
        """

        atomSelection = []

        for chainId, cifSeqId, cifCompId, _ in chainAssign:
            if cifSeqId == seqId:
                atomSelection.append({'chain_id': chainId, 'seq_id': cifSeqId, 'comp_id': cifCompId})

        if len(atomSelection) > 0:
            self.atomSelectionSet.append(atomSelection)

    def testCoordAtomIdConsistency(self, chainId: str, seqId: int, compId: str, atomId: str,
                                   seqKey: Tuple[str, int], coordAtomSite: Optional[dict]) -> Tuple[str, bool]:
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
                self.__authAtomId = 'auth_atom_id'

            elif self.__preferAuthSeq:
                _seqKey, _coordAtomSite = self.getCoordAtomSiteOf(chainId, seqId, asis=False)
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
                        self.__authAtomId = 'auth_atom_id'
                        seqKey = _seqKey
                        self.__setLocalSeqScheme()

            else:
                self.__preferAuthSeq = True
                _seqKey, _coordAtomSite = self.getCoordAtomSiteOf(chainId, seqId)
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
                        self.__authAtomId = 'auth_atom_id'
                        seqKey = _seqKey
                        self.__setLocalSeqScheme()
                    elif not self.__extendAuthSeq:
                        self.__preferAuthSeq = False
                elif not self.__extendAuthSeq:
                    self.__preferAuthSeq = False

        elif self.__preferAuthSeq and seqKey not in self.__coordUnobsRes:
            _seqKey, _coordAtomSite = self.getCoordAtomSiteOf(chainId, seqId, asis=False)
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
                    self.__authAtomId = 'auth_atom_id'
                    seqKey = _seqKey
                    self.__setLocalSeqScheme()

        elif not self.__preferAuthSeq:
            self.__preferAuthSeq = True
            _seqKey, _coordAtomSite = self.getCoordAtomSiteOf(chainId, seqId)
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
                    self.__authAtomId = 'auth_atom_id'
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

        if self.__preferAuthSeq and seqKey not in self.__coordUnobsRes:
            _seqKey, _coordAtomSite = self.getCoordAtomSiteOf(chainId, seqId, asis=False)
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
                    self.__authAtomId = 'auth_atom_id'
                    seqKey = _seqKey
                    self.__setLocalSeqScheme()

        elif not self.__preferAuthSeq:
            self.__preferAuthSeq = True
            _seqKey, _coordAtomSite = self.getCoordAtomSiteOf(chainId, seqId)
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
                    self.__authAtomId = 'auth_atom_id'
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
                                    self.__f.append(f"[Hydrogen not instantiated] {self.__getCurrentRestraint()}"
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
                                            f"The residue '{seqId}:{compId}' is not present in polymer sequence "
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
                            warn_title = 'Anomalous data' if self.__preferAuthSeq and compId == 'PRO' else 'Atom not found'
                            self.__f.append(f"[{warn_title}] {self.__getCurrentRestraint()}"
                                            f"{chainId}:{seqId}:{compId}:{atomId} is not present in the coordinates.")
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

    def getCoordAtomSiteOf(self, chainId: str, seqId: int, cifCheck: bool = True, asis: bool = True
                           ) -> Tuple[Tuple[str, int], Optional[dict]]:
        seqKey = (chainId, seqId)
        coordAtomSite = None
        if cifCheck:
            preferAuthSeq = self.__preferAuthSeq if asis else not self.__preferAuthSeq
            if preferAuthSeq:
                if seqKey in self.__coordAtomSite:
                    coordAtomSite = self.__coordAtomSite[seqKey]
            else:
                if seqKey in self.__labelToAuthSeq:
                    seqKey = self.__labelToAuthSeq[seqKey]
                    if seqKey in self.__coordAtomSite:
                        coordAtomSite = self.__coordAtomSite[seqKey]
        return seqKey, coordAtomSite

    # Enter a parse tree produced by RosettaMRParser#angle_restraints.
    def enterAngle_restraints(self, ctx: RosettaMRParser.Angle_restraintsContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'ang'

    # Exit a parse tree produced by RosettaMRParser#angle_restraints.
    def exitAngle_restraints(self, ctx: RosettaMRParser.Angle_restraintsContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by RosettaMRParser#angle_restraint.
    def enterAngle_restraint(self, ctx: RosettaMRParser.Angle_restraintContext):  # pylint: disable=unused-argument
        self.angRestraints += 1

        self.stackFuncs.clear()
        self.atomSelectionSet.clear()

    # Exit a parse tree produced by RosettaMRParser#angle_restraint.
    def exitAngle_restraint(self, ctx: RosettaMRParser.Angle_restraintContext):
        seqId1 = int(str(ctx.Integer(0)))
        atomId1 = str(ctx.Simple_name(0)).upper()
        seqId2 = int(str(ctx.Integer(1)))
        atomId2 = str(ctx.Simple_name(1)).upper()
        seqId3 = int(str(ctx.Integer(2)))
        atomId3 = str(ctx.Simple_name(2)).upper()

        dstFunc = self.validateAngleRange(1.0)

        if dstFunc is None:
            return

        if not self.__hasPolySeq and not self.__hasNonPolySeq:
            return

        self.__retrieveLocalSeqScheme()

        chainAssign1 = self.assignCoordPolymerSequence(seqId1, atomId1)
        chainAssign2 = self.assignCoordPolymerSequence(seqId2, atomId2)
        chainAssign3 = self.assignCoordPolymerSequence(seqId3, atomId3)

        if 0 in (len(chainAssign1), len(chainAssign2), len(chainAssign3)):
            return

        self.selectCoordAtoms(chainAssign1, seqId1, atomId1, False, 'an angle')
        self.selectCoordAtoms(chainAssign2, seqId2, atomId2, False, 'an angle')
        self.selectCoordAtoms(chainAssign3, seqId3, atomId3, False, 'an angle')

        if len(self.atomSelectionSet) < 3:
            return

        if not self.areUniqueCoordAtoms('an angle'):
            return

        isNested = len(self.stackNest) > 0

        if self.__createSfDict:
            sf = self.__getSf('angle restraint')
            if not isNested or self.__is_first_nest:
                sf['id'] += 1
            if len(sf['loop']['tags']) == 0:
                sf['loop']['tags'] = ['index_id', 'id',
                                      'auth_asym_id_1', 'auth_seq_id_1', 'auth_comp_id_1', 'auth_atom_id_1',
                                      'auth_asym_id_2', 'auth_seq_id_2', 'auth_comp_id_2', 'auth_atom_id_2',
                                      'auth_asym_id_3', 'auth_seq_id_3', 'auth_comp_id_3', 'auth_atom_id_3',
                                      'target_value', 'target_value_uncertainty',
                                      'lower_linear_limit', 'lower_limit', 'upper_limit', 'upper_linear_limit',
                                      'list_id']

        if isNested:
            if self.__debug:
                print(f"NESTED: {self.stackNest}")

        for atom1, atom2, atom3 in itertools.product(self.atomSelectionSet[0],
                                                     self.atomSelectionSet[1],
                                                     self.atomSelectionSet[2]):
            if isLongRangeRestraint([atom1, atom2, atom3], self.__polySeq if self.__gapInAuthSeq else None):
                continue
            if self.__debug:
                print(f"subtype={self.__cur_subtype} id={self.angRestraints} "
                      f"atom1={atom1} atom2={atom2} atom3={atom3} {dstFunc}")
            if self.__createSfDict and sf is not None:
                sf['index_id'] += 1
                sf['loop']['data'].append([sf['index_id'], sf['id'],
                                           atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id'],
                                           atom2['chain_id'], atom2['seq_id'], atom2['comp_id'], atom2['atom_id'],
                                           atom3['chain_id'], atom3['seq_id'], atom3['comp_id'], atom3['atom_id'],
                                           dstFunc.get('target_value'), None,
                                           dstFunc.get('lower_linear_limit'),
                                           dstFunc.get('lower_limit'),
                                           dstFunc.get('upper_limit'),
                                           dstFunc.get('upper_linear_limit'),
                                           sf['list_id']])

    def validateAngleRange(self, weight: float) -> Optional[dict]:
        """ Validate angle value range.
        """

        target_value = None
        lower_limit = None
        upper_limit = None
        lower_linear_limit = None
        upper_linear_limit = None

        firstFunc = None
        srcFunc = None

        level = 0
        while self.stackFuncs:
            func = self.stackFuncs.pop()
            if func is not None:
                if firstFunc is None:
                    firstFunc = copy.copy(func)
                if func['name'] in ('SCALARWEIGHTEDFUNC', 'SUMFUNC'):
                    continue
                if 'func_types' in firstFunc:
                    firstFunc['func_types'].append(func['name'])
                if srcFunc is None:
                    srcFunc = copy.copy(func)
                if 'target_value' in func:
                    target_value = func['target_value']
                    del srcFunc['target_value']
                if 'lower_limit' in func:
                    lower_limit = func['lower_limit']
                    del srcFunc['lower_limit']
                if 'upper_limit' in func:
                    upper_limit = func['upper_limit']
                    del srcFunc['upper_limit']
                if 'lower_linear_limit' in func:
                    lower_linear_limit = func['lower_linear_limit']
                    del srcFunc['lower_linear_limit']
                if 'upper_linear_limit' in func:
                    upper_linear_limit = func['upper_linear_limit']
                    del srcFunc['upper_linear_limit']
                level += 1

        if srcFunc is None:  # errors are already caught
            return None

        if level > 1:
            self.__f.append(f"[Unsupported data] {self.__getCurrentRestraint()}"
                            f"Too complex constraint function {firstFunc} can not be converted to NEF/NMR-STAR data.")
            return None

        if target_value is None and lower_limit is None and upper_limit is None\
           and lower_linear_limit is None and upper_linear_limit is None:
            self.__f.append(f"[Unsupported data] {self.__getCurrentRestraint()}"
                            f"The constraint function {srcFunc} can not be converted to NEF/NMR-STAR data.")
            return None

        validRange = True
        dstFunc = {'weight': weight}

        if self.__correctCircularShift:
            _array = numpy.array([target_value, lower_limit, upper_limit, lower_linear_limit, upper_linear_limit],
                                 dtype=float)

            shift = None
            if numpy.nanmin(_array) >= THRESHHOLD_FOR_CIRCULAR_SHIFT:
                shift = -(numpy.nanmax(_array) // 360) * 360
            elif numpy.nanmax(_array) <= -THRESHHOLD_FOR_CIRCULAR_SHIFT:
                shift = -(numpy.nanmin(_array) // 360) * 360
            if shift is not None:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                "The target/limit values for an angle restraint have been circularly shifted "
                                f"to fit within range {ANGLE_RESTRAINT_ERROR}.")
                if target_value is not None:
                    target_value += shift
                if lower_limit is not None:
                    lower_limit += shift
                if upper_limit is not None:
                    upper_limit += shift
                if lower_linear_limit is not None:
                    upper_linear_limit += shift
                if upper_linear_limit is not None:
                    upper_linear_limit += shift

        if target_value is not None:
            if ANGLE_ERROR_MIN < target_value < ANGLE_ERROR_MAX:
                dstFunc['target_value'] = f"{target_value}"
            else:
                validRange = False
                self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                f"{srcFunc}, the target value='{target_value}' must be within range {ANGLE_RESTRAINT_ERROR}.")

        if lower_limit is not None:
            if ANGLE_ERROR_MIN <= lower_limit < ANGLE_ERROR_MAX:
                dstFunc['lower_limit'] = f"{lower_limit:.6f}"
            else:
                validRange = False
                self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                f"{srcFunc}, the lower limit value='{lower_limit}' must be within range {ANGLE_RESTRAINT_ERROR}.")

        if upper_limit is not None:
            if ANGLE_ERROR_MIN < upper_limit <= ANGLE_ERROR_MAX:
                dstFunc['upper_limit'] = f"{upper_limit:.6f}"
            else:
                validRange = False
                self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                f"{srcFunc}, the upper limit value='{upper_limit}' must be within range {ANGLE_RESTRAINT_ERROR}.")

        if lower_linear_limit is not None:
            if ANGLE_ERROR_MIN <= lower_linear_limit < ANGLE_ERROR_MAX:
                dstFunc['lower_linear_limit'] = f"{lower_linear_limit:.6f}"
            else:
                validRange = False
                self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                f"{srcFunc}, the lower linear limit value='{lower_linear_limit}' must be within range {ANGLE_RESTRAINT_ERROR}.")

        if upper_linear_limit is not None:
            if ANGLE_ERROR_MIN < upper_linear_limit <= ANGLE_ERROR_MAX:
                dstFunc['upper_linear_limit'] = f"{upper_linear_limit:.6f}"
            else:
                validRange = False
                self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                f"{srcFunc}, the upper linear limit value='{upper_linear_limit}' must be within range {ANGLE_RESTRAINT_ERROR}.")

        if None not in (lower_limit, lower_linear_limit):
            if lower_linear_limit > lower_limit:
                validRange = False
                self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                f"{srcFunc}, the lower linear limit value='{lower_linear_limit}' must be less than the lower limit value '{lower_limit}'.")

        if None not in (upper_limit, upper_linear_limit):
            if upper_limit > upper_linear_limit:
                validRange = False
                self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                f"{srcFunc}, the upper limit value='{upper_limit}' must be less than the upper linear limit value '{upper_linear_limit}'.")

        if not validRange:
            return None

        if target_value is not None:
            if ANGLE_RANGE_MIN <= target_value <= ANGLE_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                f"{srcFunc}, the target value='{target_value}' should be within range {ANGLE_RESTRAINT_RANGE}.")

        if lower_limit is not None:
            if ANGLE_RANGE_MIN <= lower_limit <= ANGLE_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                f"{srcFunc}, the lower limit value='{lower_limit}' should be within range {ANGLE_RESTRAINT_RANGE}.")

        if upper_limit is not None:
            if ANGLE_RANGE_MIN <= upper_limit <= ANGLE_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                f"{srcFunc}, the upper limit value='{upper_limit}' should be within range {ANGLE_RESTRAINT_RANGE}.")

        if lower_linear_limit is not None:
            if ANGLE_RANGE_MIN <= lower_linear_limit <= ANGLE_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                f"{srcFunc}, the lower linear limit value='{lower_linear_limit}' should be within range {ANGLE_RESTRAINT_RANGE}.")

        if upper_linear_limit is not None:
            if ANGLE_RANGE_MIN <= upper_linear_limit <= ANGLE_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                f"{srcFunc}, the upper linear limit value='{upper_linear_limit}' should be within range {ANGLE_RESTRAINT_RANGE}.")

        if target_value is None and lower_limit is None and upper_limit is None and lower_linear_limit is None and upper_linear_limit is None:
            return None

        if None not in (upper_limit, lower_limit)\
           and (PLANE_LIKE_LOWER_LIMIT <= lower_limit < 0.0 < upper_limit <= PLANE_LIKE_UPPER_LIMIT
                or PLANE_LIKE_LOWER_LIMIT <= lower_limit - 180.0 < 0.0 < upper_limit - 180.0 <= PLANE_LIKE_UPPER_LIMIT
                or PLANE_LIKE_LOWER_LIMIT <= lower_limit - 360.0 < 0.0 < upper_limit - 360.0 <= PLANE_LIKE_UPPER_LIMIT):
            dstFunc['plane_like'] = True

        return dstFunc

    # Enter a parse tree produced by RosettaMRParser#dihedral_restraints.
    def enterDihedral_restraints(self, ctx: RosettaMRParser.Dihedral_restraintsContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'dihed'

    # Exit a parse tree produced by RosettaMRParser#dihedral_restraints.
    def exitDihedral_restraints(self, ctx: RosettaMRParser.Dihedral_restraintsContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by RosettaMRParser#dihedral_restraint.
    def enterDihedral_restraint(self, ctx: RosettaMRParser.Dihedral_restraintContext):  # pylint: disable=unused-argument
        self.dihedRestraints += 1

        self.stackFuncs.clear()
        self.atomSelectionSet.clear()

    # Exit a parse tree produced by RosettaMRParser#dihedral_restraint.
    def exitDihedral_restraint(self, ctx: RosettaMRParser.Dihedral_restraintContext):
        seqId1 = int(str(ctx.Integer(0)))
        atomId1 = str(ctx.Simple_name(0)).upper()
        seqId2 = int(str(ctx.Integer(1)))
        atomId2 = str(ctx.Simple_name(1)).upper()
        seqId3 = int(str(ctx.Integer(2)))
        atomId3 = str(ctx.Simple_name(2)).upper()
        seqId4 = int(str(ctx.Integer(3)))
        atomId4 = str(ctx.Simple_name(3)).upper()

        dstFunc = self.validateAngleRange(1.0)

        if dstFunc is None:
            return

        if not self.__hasPolySeq and not self.__hasNonPolySeq:
            return

        self.__retrieveLocalSeqScheme()

        chainAssign1 = self.assignCoordPolymerSequence(seqId1, atomId1)
        chainAssign2 = self.assignCoordPolymerSequence(seqId2, atomId2)
        chainAssign3 = self.assignCoordPolymerSequence(seqId3, atomId3)
        chainAssign4 = self.assignCoordPolymerSequence(seqId4, atomId4)

        if 0 in (len(chainAssign1), len(chainAssign2), len(chainAssign3), len(chainAssign4)):
            return

        self.selectCoordAtoms(chainAssign1, seqId1, atomId1, False, 'a dihedral angle')
        self.selectCoordAtoms(chainAssign2, seqId2, atomId2, False, 'a dihedral angle')
        self.selectCoordAtoms(chainAssign3, seqId3, atomId3, False, 'a dihedral angle')
        self.selectCoordAtoms(chainAssign4, seqId4, atomId4, False, 'a dihedral angle')

        if len(self.atomSelectionSet) < 4:
            return

        try:
            compId = self.atomSelectionSet[0][0]['comp_id']
            peptide, nucleotide, carbohydrate = self.__csStat.getTypeOfCompId(compId)
        except IndexError:
            self.areUniqueCoordAtoms('a dihedral angle')
            return

        len_f = len(self.__f)
        self.areUniqueCoordAtoms('a dihedral angle',
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
                                                                                       self.__getCurrentRestraint())
                    self.__f.append(err)

                if angleName in emptyValue and atomSelTotal != 4:
                    continue

                fixedAngleName = angleName
                break

        sf = None
        if self.__createSfDict:
            sf = self.__getSf(potentialType=getPotentialType(self.__file_type, self.__cur_subtype, dstFunc))

        isNested = len(self.stackNest) > 0

        if isNested:
            if self.__debug:
                print(f"NESTED: {self.stackNest}")

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
                                                                                   self.__getCurrentRestraint())
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
                print(f"subtype={self.__cur_subtype} id={self.dihedRestraints} angleName={angleName} "
                      f"atom1={atom1} atom2={atom2} atom3={atom3} atom4={atom4} {dstFunc}")
            if self.__createSfDict and sf is not None:
                if first_item and (not isNested or self.__is_first_nest):
                    sf['id'] += 1
                    first_item = False
                sf['index_id'] += 1
                row = getRow(self.__cur_subtype, sf['id'], sf['index_id'],
                             combinationId, None, angleName,
                             sf['list_id'], self.__entryId, dstFunc,
                             self.__authToStarSeq, self.__authToOrigSeq, self.__authToInsCode, self.__offsetHolder,
                             atom1, atom2, atom3, atom4)
                sf['loop'].add_data(row)

        if self.__createSfDict and sf is not None and isinstance(combinationId, int) and combinationId == 1:
            sf['loop'].data[-1] = resetCombinationId(self.__cur_subtype, sf['loop'].data[-1])

    # Enter a parse tree produced by RosettaMRParser#dihedral_pair_restraints.
    def enterDihedral_pair_restraints(self, ctx: RosettaMRParser.Dihedral_pair_restraintsContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'dihed'

    # Exit a parse tree produced by RosettaMRParser#dihedral_pair_restraints.
    def exitDihedral_pair_restraints(self, ctx: RosettaMRParser.Dihedral_pair_restraintsContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by RosettaMRParser#dihedral_pair_restraint.
    def enterDihedral_pair_restraint(self, ctx: RosettaMRParser.Dihedral_pair_restraintContext):  # pylint: disable=unused-argument
        self.dihedRestraints += 1

        self.stackFuncs.clear()
        self.atomSelectionSet.clear()

    # Exit a parse tree produced by RosettaMRParser#dihedral_pair_restraint.
    def exitDihedral_pair_restraint(self, ctx: RosettaMRParser.Dihedral_pair_restraintContext):
        seqId1 = int(str(ctx.Integer(0)))
        atomId1 = str(ctx.Simple_name(0)).upper()
        seqId2 = int(str(ctx.Integer(1)))
        atomId2 = str(ctx.Simple_name(1)).upper()
        seqId3 = int(str(ctx.Integer(2)))
        atomId3 = str(ctx.Simple_name(2)).upper()
        seqId4 = int(str(ctx.Integer(3)))
        atomId4 = str(ctx.Simple_name(3)).upper()

        seqId5 = int(str(ctx.Integer(4)))
        atomId5 = str(ctx.Simple_name(4)).upper()
        seqId6 = int(str(ctx.Integer(5)))
        atomId6 = str(ctx.Simple_name(5)).upper()
        seqId7 = int(str(ctx.Integer(6)))
        atomId7 = str(ctx.Simple_name(6)).upper()
        seqId8 = int(str(ctx.Integer(7)))
        atomId8 = str(ctx.Simple_name(7)).upper()

        dstFunc = self.validateAngleRange(1.0)

        if dstFunc is None:
            return

        if not self.__hasPolySeq and not self.__hasNonPolySeq:
            return

        self.__retrieveLocalSeqScheme()

        chainAssign1 = self.assignCoordPolymerSequence(seqId1, atomId1)
        chainAssign2 = self.assignCoordPolymerSequence(seqId2, atomId2)
        chainAssign3 = self.assignCoordPolymerSequence(seqId3, atomId3)
        chainAssign4 = self.assignCoordPolymerSequence(seqId4, atomId4)
        chainAssign5 = self.assignCoordPolymerSequence(seqId5, atomId5)
        chainAssign6 = self.assignCoordPolymerSequence(seqId6, atomId6)
        chainAssign7 = self.assignCoordPolymerSequence(seqId7, atomId7)
        chainAssign8 = self.assignCoordPolymerSequence(seqId8, atomId8)

        if 0 in (len(chainAssign1), len(chainAssign2), len(chainAssign3), len(chainAssign4),
                 len(chainAssign5), len(chainAssign6), len(chainAssign7), len(chainAssign8)):
            return

        self.selectCoordAtoms(chainAssign1, seqId1, atomId1, False, 'a dihedral angle pair')
        self.selectCoordAtoms(chainAssign2, seqId2, atomId2, False, 'a dihedral angle pair')
        self.selectCoordAtoms(chainAssign3, seqId3, atomId3, False, 'a dihedral angle pair')
        self.selectCoordAtoms(chainAssign4, seqId4, atomId4, False, 'a dihedral angle pair')
        self.selectCoordAtoms(chainAssign5, seqId5, atomId5, False, 'a dihedral angle pair')
        self.selectCoordAtoms(chainAssign6, seqId6, atomId6, False, 'a dihedral angle pair')
        self.selectCoordAtoms(chainAssign7, seqId7, atomId7, False, 'a dihedral angle pair')
        self.selectCoordAtoms(chainAssign8, seqId8, atomId8, False, 'a dihedral angle pair')

        if len(self.atomSelectionSet) < 8:
            return

        if not self.areUniqueCoordAtoms('a dihedral angle pair'):
            return

        sf = None
        if self.__createSfDict:
            sf = self.__getSf(potentialType=getPotentialType(self.__file_type, self.__cur_subtype, dstFunc))

        compId = self.atomSelectionSet[0][0]['comp_id']
        peptide, nucleotide, carbohydrate = self.__csStat.getTypeOfCompId(compId)

        isNested = len(self.stackNest) > 0

        if isNested:
            if self.__debug:
                print(f"NESTED: {self.stackNest}")

        first_item = True

        atomSelTotal = sum(len(s) for s in self.atomSelectionSet[0:4])

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
                                                                                   self.__getCurrentRestraint())
                self.__f.append(err)

            if angleName in emptyValue and atomSelTotal != 4:
                continue

            if peptide and angleName == 'CHI2' and atom4['atom_id'] == 'CD1' and isLikePheOrTyr(atom2['comp_id'], self.__ccU):
                dstFunc = self.selectRealisticChi2AngleConstraint(atom1, atom2, atom3, atom4,
                                                                  dstFunc)
            if self.__debug:
                print(f"subtype={self.__cur_subtype} id={self.dihedRestraints} angleName={angleName} "
                      f"atom1={atom1} atom2={atom2} atom3={atom3} atom4={atom4}")
            if self.__createSfDict and sf is not None:
                if first_item and (not isNested or self.__is_first_nest):
                    sf['id'] += 1
                    first_item = False
                sf['index_id'] += 1
                row = getRow(self.__cur_subtype, sf['id'], sf['index_id'],
                             1, None, angleName,
                             sf['list_id'], self.__entryId, dstFunc,
                             self.__authToStarSeq, self.__authToOrigSeq, self.__authToInsCode, self.__offsetHolder,
                             atom1, atom2, atom3, atom4)
                sf['loop'].add_data(row)

        compId = self.atomSelectionSet[4][0]['comp_id']
        peptide, nucleotide, carbohydrate = self.__csStat.getTypeOfCompId(compId)

        atomSelTotal = sum(len(s) for s in self.atomSelectionSet[4:8])

        for atom1, atom2, atom3, atom4 in itertools.product(self.atomSelectionSet[4],
                                                            self.atomSelectionSet[5],
                                                            self.atomSelectionSet[6],
                                                            self.atomSelectionSet[7]):
            atoms = [atom1, atom2, atom3, atom4]
            angleName = getTypeOfDihedralRestraint(peptide, nucleotide, carbohydrate,
                                                   atoms,
                                                   'plane_like' in dstFunc,
                                                   self.__cR, self.__ccU,
                                                   self.__representativeModelId, self.__representativeAltId, self.__modelNumName)

            if angleName is not None and angleName.startswith('pseudo'):
                angleName, atom2, atom3, err = fixBackboneAtomsOfDihedralRestraint(angleName,
                                                                                   atoms,
                                                                                   self.__getCurrentRestraint())
                self.__f.append(err)

            if angleName in emptyValue and atomSelTotal != 4:
                continue

            if peptide and angleName == 'CHI2' and atom4['atom_id'] == 'CD1' and isLikePheOrTyr(atom2['comp_id'], self.__ccU):
                dstFunc = self.selectRealisticChi2AngleConstraint(atom1, atom2, atom3, atom4,
                                                                  dstFunc)
            if self.__debug:
                print(f"subtype={self.__cur_subtype} id={self.dihedRestraints} angleName={angleName} "
                      f"atom5={atom1} atom6={atom2} atom7={atom3} atom8={atom4} {dstFunc}")
            if self.__createSfDict and sf is not None:
                if first_item:
                    sf['id'] += 1
                    first_item = False
                sf['index_id'] += 1
                row = getRow(self.__cur_subtype, sf['id'], sf['index_id'],
                             2, None, angleName,
                             sf['list_id'], self.__entryId, dstFunc,
                             self.__authToStarSeq, self.__authToOrigSeq, self.__authToInsCode, self.__offsetHolder,
                             atom1, atom2, atom3, atom4)
                sf['loop'].add_data(row)

    # Enter a parse tree produced by RosettaMRParser#coordinate_restraints.
    def enterCoordinate_restraints(self, ctx: RosettaMRParser.Coordinate_restraintsContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'geo'

    # Exit a parse tree produced by RosettaMRParser#coordinate_restraints.
    def exitCoordinate_restraints(self, ctx: RosettaMRParser.Coordinate_restraintsContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by RosettaMRParser#coordinate_restraint.
    def enterCoordinate_restraint(self, ctx: RosettaMRParser.Coordinate_restraintContext):  # pylint: disable=unused-argument
        self.geoRestraints += 1

        self.stackFuncs.clear()
        self.atomSelectionSet.clear()

    # Exit a parse tree produced by RosettaMRParser#coordinate_restraint.
    def exitCoordinate_restraint(self, ctx: RosettaMRParser.Coordinate_restraintContext):

        try:

            atomId1 = str(ctx.Simple_name(0)).upper()
            _seqId1 = str(ctx.Simple_name(1)).upper()
            atomId2 = str(ctx.Simple_name(2)).upper()
            _seqId2 = str(ctx.Simple_name(3)).upper()

            if len(self.numberSelection) == 0 or None in self.numberSelection:
                return

            cartX = self.numberSelection[0]
            cartY = self.numberSelection[1]
            cartZ = self.numberSelection[2]

            if _seqId1.isdecimal():
                seqId1 = int(_seqId1)
                fixedChainId1 = None
            else:
                g = self.concat_resnum_chain_pat.search(_seqId1).groups()
                seqId1 = int(g[0])
                fixedChainId1 = g[1]

            if _seqId2.isdecimal():
                seqId2 = int(_seqId2)
                fixedChainId2 = None
            else:
                g = self.concat_resnum_chain_pat.search(_seqId2).groups()
                seqId2 = int(g[0])
                fixedChainId2 = g[1]

            if not self.__hasPolySeq and not self.__hasNonPolySeq:
                return

            self.__retrieveLocalSeqScheme()

            chainAssign1 = self.assignCoordPolymerSequence(seqId1, atomId1, fixedChainId1)
            chainAssign2 = self.assignCoordPolymerSequence(seqId2, atomId2, fixedChainId2)

            if 0 in (len(chainAssign1), len(chainAssign2)):
                return

            self.selectCoordAtoms(chainAssign1, seqId1, atomId1)
            self.selectCoordAtoms(chainAssign2, seqId2, atomId2, False, 'a coordinate')  # refAtom

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

            dstFunc = self.validateDistanceRange(1.0)

            if dstFunc is None:
                return

            isNested = len(self.stackNest) > 0

            if self.__createSfDict:
                sf = self.__getSf('harmonic coordinate restraint, ROSETTA CoordinateConstraint')
                if not isNested or self.__is_first_nest:
                    sf['id'] += 1
                if len(sf['loop']['tags']) == 0:
                    sf['loop']['tags'] = ['index_id', 'id',
                                          'auth_asym_id', 'auth_seq_id', 'auth_comp_id', 'auth_atom_id',
                                          'ref_auth_asym_id', 'ref_auth_seq_id', 'ref_auth_comp_id', 'ref_auth_atom_id',
                                          'cart_x', 'cart_y', 'cart_z',
                                          'list_id']

            if isNested:
                if self.__debug:
                    print(f"NESTED: {self.stackNest}")

            has_intra_chain, rep_chain_id_set = hasIntraChainRestraint(self.atomSelectionSet)

            for atom1, atom2 in itertools.product(self.atomSelectionSet[0],
                                                  self.atomSelectionSet[1]):
                if isIdenticalRestraint([atom1, atom2], self.__nefT):
                    continue
                if has_intra_chain and (atom1['chain_id'] != atom2['chain_id'] or atom1['chain_id'] not in rep_chain_id_set):
                    continue
                if self.__debug:
                    print(f"subtype={self.__cur_subtype} (Coordinate) id={self.geoRestraints} "
                          f"atom={atom1} refAtom={atom2} coord=({cartX}, {cartY}, {cartZ}) {dstFunc}")
                if self.__createSfDict and sf is not None:
                    sf['index_id'] += 1
                    sf['loop']['data'].append([sf['index_id'], sf['id'],
                                               atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id'],
                                               atom2['chain_id'], atom2['seq_id'], atom2['comp_id'], atom2['atom_id'],
                                               cartX, cartY, cartZ,
                                               sf['list_id']])

        except ValueError:
            self.geoRestraints -= 1

        finally:
            self.numberSelection.clear()

    # Enter a parse tree produced by RosettaMRParser#local_coordinate_restraints.
    def enterLocal_coordinate_restraints(self, ctx: RosettaMRParser.Local_coordinate_restraintsContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'geo'

    # Exit a parse tree produced by RosettaMRParser#local_coordinate_restraints.
    def exitLocal_coordinate_restraints(self, ctx: RosettaMRParser.Local_coordinate_restraintsContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by RosettaMRParser#local_coordinate_restraint.
    def enterLocal_coordinate_restraint(self, ctx: RosettaMRParser.Local_coordinate_restraintContext):  # pylint: disable=unused-argument
        self.geoRestraints += 1

        self.stackFuncs.clear()
        self.atomSelectionSet.clear()

    # Exit a parse tree produced by RosettaMRParser#local_coordinate_restraint.
    def exitLocal_coordinate_restraint(self, ctx: RosettaMRParser.Local_coordinate_restraintContext):

        try:

            seqId1 = int(str(ctx.Integer(0)))
            atomId1 = str(ctx.Simple_name(0)).upper()
            seqId234 = int(str(ctx.Integer(1)))
            atomId2 = str(ctx.Simple_name(1)).upper()
            atomId3 = str(ctx.Simple_name(2)).upper()
            atomId4 = str(ctx.Simple_name(3)).upper()

            if len(self.numberSelection) == 0 or None in self.numberSelection:
                return

            cartX = self.numberSelection[0]
            cartY = self.numberSelection[1]
            cartZ = self.numberSelection[2]

            dstFunc = self.validateDistanceRange(1.0)

            if dstFunc is None:
                return

            if not self.__hasPolySeq and not self.__hasNonPolySeq:
                return

            self.__retrieveLocalSeqScheme()

            chainAssign1 = self.assignCoordPolymerSequence(seqId1, atomId1)
            chainAssign2 = self.assignCoordPolymerSequence(seqId234, atomId2)
            chainAssign3 = self.assignCoordPolymerSequence(seqId234, atomId3)
            chainAssign4 = self.assignCoordPolymerSequence(seqId234, atomId4)

            if 0 in (len(chainAssign1), len(chainAssign2), len(chainAssign3), len(chainAssign4)):
                return

            self.selectCoordAtoms(chainAssign1, seqId1, atomId1)
            self.selectCoordAtoms(chainAssign2, seqId234, atomId2, False, 'a local coordinate')  # originAtom1
            self.selectCoordAtoms(chainAssign3, seqId234, atomId3, False, 'a local coordinate')  # originAtom2
            self.selectCoordAtoms(chainAssign4, seqId234, atomId4, False, 'a local coordiante')  # originAtom3

            if len(self.atomSelectionSet) < 4:
                return

            isNested = len(self.stackNest) > 0

            if self.__createSfDict:
                sf = self.__getSf('local harmonic coordinate restraint, ROSETTA LocalCoordinateConstraint')
                if not isNested or self.__is_first_nest:
                    sf['id'] += 1
                if len(sf['loop']['tags']) == 0:
                    sf['loop']['tags'] = ['index_id', 'id',
                                          'auth_asym_id', 'auth_seq_id', 'auth_comp_id', 'auth_atom_id',
                                          'origin_auth_asym_id_1', 'origin_auth_seq_id_1', 'origin_auth_comp_id_1', 'origin_auth_atom_id_1',
                                          'origin_auth_asym_id_2', 'origin_auth_seq_id_2', 'origin_auth_comp_id_2', 'origin_auth_atom_id_2',
                                          'origin_auth_asym_id_3', 'origin_auth_seq_id_3', 'origin_auth_comp_id_3', 'origin_auth_atom_id_3',
                                          'local_cart_x', 'local_cart_y', 'local_cart_z',
                                          'list_id']

            if isNested:
                if self.__debug:
                    print(f"NESTED: {self.stackNest}")

            for atom1, atom2, atom3, atom4 in itertools.product(self.atomSelectionSet[0],
                                                                self.atomSelectionSet[1],
                                                                self.atomSelectionSet[2],
                                                                self.atomSelectionSet[3]):
                if self.__debug:
                    print(f"subtype={self.__cur_subtype} (LocalCoordinate) id={self.geoRestraints} "
                          f"atom={atom1} originAtom1={atom2} originAtom2={atom3} originAtom3={atom4} "
                          f"localCoord=({cartX}, {cartY}, {cartZ}) {dstFunc}")
                if self.__createSfDict and sf is not None:
                    sf['index_id'] += 1
                    sf['loop']['data'].append([sf['index_id'], sf['id'],
                                               atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id'],
                                               atom2['chain_id'], atom2['seq_id'], atom2['comp_id'], atom2['atom_id'],
                                               atom3['chain_id'], atom3['seq_id'], atom3['comp_id'], atom3['atom_id'],
                                               atom4['chain_id'], atom4['seq_id'], atom4['comp_id'], atom4['atom_id'],
                                               cartX, cartY, cartZ,
                                               sf['list_id']])

        except ValueError:
            self.geoRestraints -= 1

        finally:
            self.numberSelection.clear()

    # Enter a parse tree produced by RosettaMRParser#site_restraints.
    def enterSite_restraints(self, ctx: RosettaMRParser.Site_restraintsContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'geo'

    # Exit a parse tree produced by RosettaMRParser#site_restraints.
    def exitSite_restraints(self, ctx: RosettaMRParser.Site_restraintsContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by RosettaMRParser#site_restraint.
    def enterSite_restraint(self, ctx: RosettaMRParser.Site_restraintContext):  # pylint: disable=unused-argument
        self.geoRestraints += 1

        self.stackFuncs.clear()
        self.atomSelectionSet.clear()

    # Exit a parse tree produced by RosettaMRParser#site_restraint.
    def exitSite_restraint(self, ctx: RosettaMRParser.Site_restraintContext):
        seqId1 = int(str(ctx.Integer()))
        atomId1 = str(ctx.Simple_name(0)).upper()
        opposingChainId = str(ctx.Simple_name(1)).upper()

        dstFunc = self.validateDistanceRange(1.0)

        if dstFunc is None:
            return

        if not self.__hasPolySeq and not self.__hasNonPolySeq:
            return

        self.__retrieveLocalSeqScheme()

        chainAssign1 = self.assignCoordPolymerSequence(seqId1, atomId1)

        if len(chainAssign1) == 0:
            return

        self.selectCoordAtoms(chainAssign1, seqId1, atomId1)

        if len(self.atomSelectionSet) < 1:
            return

        if not self.__preferAuthSeq:
            ps = next((ps for ps in self.__polySeq if ps['chain_id'] == opposingChainId), None)
        else:
            ps = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == opposingChainId), None)

        if ps is None:
            self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                            f"The opposing chain {opposingChainId!r} is not found in the coordinates.")
            return

        for atom1 in self.atomSelectionSet[0]:
            chainId = atom1['chain_id']
            if chainId == opposingChainId:
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                f"The selected atom {chainId}:{atom1['seq_id']}:{atom1['comp_id']}:{atom1['atom_id']} "
                                f"must not in the opposing chain {opposingChainId!r}.")
                return

        isNested = len(self.stackNest) > 0

        if self.__createSfDict:
            sf = self.__getSf('ambiguous site restraint (atom to other chain), ROSETTA SiteConstraint')
            if not isNested or self.__is_first_nest:
                sf['id'] += 1
            if len(sf['loop']['tags']) == 0:
                sf['loop']['tags'] = ['index_id', 'id',
                                      'auth_asym_id', 'auth_seq_id', 'auth_comp_id', 'auth_atom_id',
                                      'opposing_auth_asym_id',
                                      'target_value', 'target_value_uncertainty',
                                      'lower_linear_limit', 'lower_limit', 'upper_limit', 'upper_linear_limit',
                                      'list_id']

        if isNested:
            if self.__debug:
                print(f"NESTED: {self.stackNest}")

        for atom1 in self.atomSelectionSet[0]:
            if self.__debug:
                print(f"subtype={self.__cur_subtype} (Site) id={self.geoRestraints} "
                      f"atom={atom1} opposingChainId={opposingChainId} {dstFunc}")
            if self.__createSfDict and sf is not None:
                sf['index_id'] += 1
                sf['loop']['data'].append([sf['index_id'], sf['id'],
                                           atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id'],
                                           opposingChainId,
                                           dstFunc.get('target_value'), None,
                                           dstFunc.get('lower_linear_limit'),
                                           dstFunc.get('lower_limit'),
                                           dstFunc.get('upper_limit'),
                                           dstFunc.get('upper_linear_limit'),
                                           sf['list_id']])

    # Enter a parse tree produced by RosettaMRParser#site_residues_restraints.
    def enterSite_residues_restraints(self, ctx: RosettaMRParser.Site_residues_restraintsContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'geo'

    # Exit a parse tree produced by RosettaMRParser#site_residues_restraints.
    def exitSite_residues_restraints(self, ctx: RosettaMRParser.Site_residues_restraintsContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by RosettaMRParser#site_residues_restraint.
    def enterSite_residues_restraint(self, ctx: RosettaMRParser.Site_residues_restraintContext):  # pylint: disable=unused-argument
        self.geoRestraints += 1

        self.stackFuncs.clear()
        self.atomSelectionSet.clear()

    # Exit a parse tree produced by RosettaMRParser#site_residues_restraint.
    def exitSite_residues_restraint(self, ctx: RosettaMRParser.Site_residues_restraintContext):
        seqId1 = int(str(ctx.Integer(0)))
        atomId1 = str(ctx.Simple_name()).upper()
        seqId2 = int(str(ctx.Integer(1)))
        seqId3 = int(str(ctx.Integer(2)))

        dstFunc = self.validateDistanceRange(1.0)

        if dstFunc is None:
            return

        if not self.__hasPolySeq and not self.__hasNonPolySeq:
            return

        self.__retrieveLocalSeqScheme()

        chainAssign1 = self.assignCoordPolymerSequence(seqId1, atomId1)

        if len(chainAssign1) == 0:
            return

        self.selectCoordAtoms(chainAssign1, seqId1, atomId1)

        if len(self.atomSelectionSet) < 1:
            return

        chainAssign2 = self.assignCoordPolymerSequence(seqId2)
        chainAssign3 = self.assignCoordPolymerSequence(seqId3)

        if 0 in (len(chainAssign2), len(chainAssign3)):
            return

        self.selectCoordResidues(chainAssign2, seqId2)
        self.selectCoordResidues(chainAssign3, seqId3)

        if len(self.atomSelectionSet) < 3:
            return

        isNested = len(self.stackNest) > 0

        if self.__createSfDict:
            sf = self.__getSf('ambiguous site restraint (atom to other residue), ROSETTA SiteConstraintResidues')
            if not isNested or self.__is_first_nest:
                sf['id'] += 1
            if len(sf['loop']['tags']) == 0:
                sf['loop']['tags'] = ['index_id', 'id',
                                      'auth_asym_id', 'auth_seq_id', 'auth_comp_id', 'auth_atom_id',
                                      'interacting_auth_asym_id_1', 'interacting_auth_seq_id_1', 'interacting_auth_comp_id_1',
                                      'interacting_auth_asym_id_2', 'interacting_auth_seq_id_2', 'interacting_auth_comp_id_2',
                                      'target_value', 'target_value_uncertainty',
                                      'lower_linear_limit', 'lower_limit', 'upper_limit', 'upper_linear_limit',
                                      'list_id']

        if isNested:
            if self.__debug:
                print(f"NESTED: {self.stackNest}")

        for atom1, res2, res3 in itertools.product(self.atomSelectionSet[0],
                                                   self.atomSelectionSet[1],
                                                   self.atomSelectionSet[2]):
            if self.__debug:
                print(f"subtype={self.__cur_subtype} (Site-Residue) id={self.geoRestraints} "
                      f"atom1={atom1} residue2={res2} residue3={res3} {dstFunc}")
            if self.__createSfDict and sf is not None:
                sf['index_id'] += 1
                sf['loop']['data'].append([sf['index_id'], sf['id'],
                                           atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id'],
                                           res2['chain_id'], res2['seq_id'], res2['comp_id'],
                                           res3['chain_id'], res3['seq_id'], res3['comp_id'],
                                           dstFunc.get('target_value'), None,
                                           dstFunc.get('lower_linear_limit'),
                                           dstFunc.get('lower_limit'),
                                           dstFunc.get('upper_limit'),
                                           dstFunc.get('upper_linear_limit'),
                                           sf['list_id']])

    # Enter a parse tree produced by RosettaMRParser#min_residue_atomic_distance_restraints.
    def enterMin_residue_atomic_distance_restraints(self, ctx: RosettaMRParser.Min_residue_atomic_distance_restraintsContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'geo'

    # Exit a parse tree produced by RosettaMRParser#min_residue_atomic_distance_restraints.
    def exitMin_residue_atomic_distance_restraints(self, ctx: RosettaMRParser.Min_residue_atomic_distance_restraintsContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by RosettaMRParser#min_residue_atomic_distance_restraint.
    def enterMin_residue_atomic_distance_restraint(self, ctx: RosettaMRParser.Min_residue_atomic_distance_restraintContext):  # pylint: disable=unused-argument
        self.geoRestraints += 1

        self.stackFuncs.clear()
        self.atomSelectionSet.clear()

    # Exit a parse tree produced by RosettaMRParser#min_residue_atomic_distance_restraint.
    def exitMin_residue_atomic_distance_restraint(self, ctx: RosettaMRParser.Min_residue_atomic_distance_restraintContext):

        try:

            seqId1 = int(str(ctx.Integer(0)))
            seqId2 = int(str(ctx.Integer(1)))

            if len(self.numberSelection) == 0 or None in self.numberSelection:
                return

            target_value = self.numberSelection[0]

            if not self.__hasPolySeq and not self.__hasNonPolySeq:
                return

            self.__retrieveLocalSeqScheme()

            chainAssign1 = self.assignCoordPolymerSequence(seqId1)
            chainAssign2 = self.assignCoordPolymerSequence(seqId2)

            if 0 in (len(chainAssign1), len(chainAssign2)):
                return

            self.selectCoordResidues(chainAssign1, seqId1)
            self.selectCoordResidues(chainAssign2, seqId2)

            if len(self.atomSelectionSet) < 2:
                return

            dstFunc = {}
            validRange = True

            if DIST_ERROR_MIN < target_value < DIST_ERROR_MAX:
                dstFunc['target_value'] = f"{target_value}"
            else:
                validRange = False
                self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                f"The target value='{target_value}' must be within range {DIST_RESTRAINT_ERROR}.")

            if not validRange:
                return

            if DIST_RANGE_MIN <= target_value <= DIST_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                f"The target value='{target_value}' should be within range {DIST_RESTRAINT_RANGE}.")

            isNested = len(self.stackNest) > 0

            if self.__createSfDict:
                sf = self.__getSf('ambiguous site restraint (residue to other residue), ROSETTA MinResidueAtomicDistance')
                if not isNested or self.__is_first_nest:
                    sf['id'] += 1
                if len(sf['loop']['tags']) == 0:
                    sf['loop']['tags'] = ['index_id', 'id',
                                          'interacting_auth_asym_id_1', 'interacting_auth_seq_id_1', 'interacting_auth_comp_id_1',
                                          'interacting_auth_asym_id_2', 'interacting_auth_seq_id_2', 'interacting_auth_comp_id_2',
                                          'target_value', 'target_value_uncertainty',
                                          'lower_linear_limit', 'lower_limit', 'upper_limit', 'upper_linear_limit',
                                          'list_id']

            if isNested:
                if self.__debug:
                    print(f"NESTED: {self.stackNest}")

            for res1, res2 in itertools.product(self.atomSelectionSet[0],
                                                self.atomSelectionSet[1]):
                if self.__debug:
                    print(f"subtype={self.__cur_subtype} (MinResidueAtomicDistance) id={self.geoRestraints} "
                          f"resudue1={res1} residue2={res2} {dstFunc}")
                if self.__createSfDict and sf is not None:
                    sf['index_id'] += 1
                    sf['loop']['data'].append([sf['index_id'], sf['id'],
                                               res1['chain_id'], res1['seq_id'], res1['comp_id'],
                                               res2['chain_id'], res2['seq_id'], res2['comp_id'],
                                               dstFunc.get('target_value'), None,
                                               dstFunc.get('lower_linear_limit'),
                                               dstFunc.get('lower_limit'),
                                               dstFunc.get('upper_limit'),
                                               dstFunc.get('upper_linear_limit'),
                                               sf['list_id']])

        except ValueError:
            self.geoRestraints -= 1

        finally:
            self.numberSelection.clear()

    # Enter a parse tree produced by RosettaMRParser#big_bin_restraints.
    def enterBig_bin_restraints(self, ctx: RosettaMRParser.Big_bin_restraintsContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'geo'

    # Exit a parse tree produced by RosettaMRParser#big_bin_restraints.
    def exitBig_bin_restraints(self, ctx: RosettaMRParser.Big_bin_restraintsContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by RosettaMRParser#big_bin_restraint.
    def enterBig_bin_restraint(self, ctx: RosettaMRParser.Big_bin_restraintContext):  # pylint: disable=unused-argument
        self.geoRestraints += 1

        self.stackFuncs.clear()
        self.atomSelectionSet.clear()

    # Exit a parse tree produced by RosettaMRParser#big_bin_restraint.
    def exitBig_bin_restraint(self, ctx: RosettaMRParser.Big_bin_restraintContext):

        try:

            seqId = int(str(ctx.Simple_name()))
            binChar = str(ctx.Simple_name())

            if len(self.numberSelection) == 0 or None in self.numberSelection:
                return

            sDev = self.numberSelection[0]

            if not self.__hasPolySeq and not self.__hasNonPolySeq:
                return

            self.__retrieveLocalSeqScheme()

            chainAssign = self.assignCoordPolymerSequence(seqId)

            if len(chainAssign) == 0:
                return

            self.selectCoordResidues(chainAssign, seqId)

            if len(self.atomSelectionSet) < 1:
                return

            if binChar not in ('O', 'G', 'E', 'A', 'B'):
                self.__f.append(f"[Enum mismatch] {self.__getCurrentRestraint()}"
                                f"The BigBin identifier '{binChar}' must be one of {('O', 'G', 'E', 'A', 'B')}.")
                return

            dstFunc = {}
            validRange = True

            if DIST_ERROR_MIN < sDev < DIST_ERROR_MAX:
                dstFunc['standard_deviation'] = f"{sDev}"
            else:
                validRange = False
                self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                f"The 'sdev={sDev}' must be within range {DIST_RESTRAINT_ERROR}.")

            if not validRange:
                return

            if DIST_RANGE_MIN <= sDev <= DIST_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                f"The 'sdev={sDev}' should be within range {DIST_RESTRAINT_RANGE}.")

            isNested = len(self.stackNest) > 0

            if self.__createSfDict:
                sf = self.__getSf("dihedral angle restraint, ROSETTA BigBin "
                                  "('O' for cis-like OMEGA, 'G' for PHI,PSI in 100,100, 'E' for 100,-90, 'A' for -50,30, 'B' for 100,175)")
                if not isNested or self.__is_first_nest:
                    sf['id'] += 1
                if len(sf['loop']['tags']) == 0:
                    sf['loop']['tags'] = ['index_id', 'id',
                                          'auth_asym_id_1', 'auth_seq_id_1', 'auth_comp_id_1',
                                          'bin_code', 'standard_deviation',
                                          'list_id']

            if isNested:
                if self.__debug:
                    print(f"NESTED: {self.stackNest}")

            for res in self.atomSelectionSet[0]:
                if self.__debug:
                    print(f"subtype={self.__cur_subtype} (BigBin) id={self.geoRestraints} "
                          f"residue={res} binChar={binChar} {dstFunc}")
                if self.__createSfDict and sf is not None:
                    sf['index_id'] += 1
                    sf['loop']['data'].append([sf['index_id'], sf['id'],
                                               res['chain_id'], res['seq_id'], res['comp_id'],
                                               binChar, sDev,
                                               sf['list_id']])

        except ValueError:
            self.geoRestraints -= 1

        finally:
            self.numberSelection.clear()

    # Enter a parse tree produced by RosettaMRParser#nested_restraints.
    def enterNested_restraints(self, ctx: RosettaMRParser.Nested_restraintsContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by RosettaMRParser#nested_restraints.
    def exitNested_restraints(self, ctx: RosettaMRParser.Nested_restraintsContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by RosettaMRParser#nested_restraint.
    def enterNested_restraint(self, ctx: RosettaMRParser.Nested_restraintContext):
        if len(self.stackNest) == 0:
            self.__is_first_nest = True
            self.__is_any_nest = False
        if self.__is_any_nest:
            self.__is_first_nest = False
        if self.__is_first_nest:
            self.__nest_combination_id = 0

        n = 0
        while ctx.any_restraint(n):
            n += 1

        if n > 0:
            self.__nest_combination_id += 1
            self.__nest_member_id = 0

        cur_nest = {}

        if ctx.MultiConstraint():
            cur_nest['type'] = 'multi'
        elif ctx.AmbiguousConstraint():
            cur_nest['type'] = 'ambig'
        else:
            k = int(str(ctx.Integer()))
            cur_nest['type'] = f"{k}of{n}"

        n = 0
        while ctx.any_restraint(n):
            n += 1

        if n > 0:
            cur_nest['id'] = -1
            cur_nest['size'] = n

        self.stackNest.append(cur_nest)

    # Exit a parse tree produced by RosettaMRParser#nested_restraint.
    def exitNested_restraint(self, ctx: RosettaMRParser.Nested_restraintContext):  # pylint: disable=unused-argument
        self.stackNest.pop()

    # Enter a parse tree produced by RosettaMRParser#any_restraint.
    def enterAny_restraint(self, ctx: RosettaMRParser.Any_restraintContext):  # pylint: disable=unused-argument
        self.__is_any_nest = True
        cur_nest = self.stackNest[-1]
        cur_nest['id'] += 1

    # Exit a parse tree produced by RosettaMRParser#any_restraint.
    def exitAny_restraint(self, ctx: RosettaMRParser.Any_restraintContext):  # pylint: disable=unused-argument
        self.__is_first_nest = False

    # Enter a parse tree produced by RosettaMRParser#func_type_def.
    def enterFunc_type_def(self, ctx: RosettaMRParser.Func_type_defContext):
        if ctx.SCALARWEIGHTEDFUNC():  # weight func_type_def
            func = {}
            valid = True

            funcType = 'SCALARWEIGHTEDFUNC'
            weight = self.getNumber_f(ctx.number_f(0))

            func['name'] = funcType
            func['weight'] = weight

            if weight < 0.0:
                valid = False
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                f"{funcType} 'weight={weight}' must not be a negative value.")
            elif weight == 0.0:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                f"{funcType} 'weight={weight}' should be a positive value.")

            func['func_types'] = []

            if valid:
                self.stackFuncs.append(func)

        elif ctx.SUMFUNC():  # n_funcs Func_Type1 Func_Def1 [Func_Type2 Func_Def2 [...]]
            func = {}
            valid = True

            funcType = 'SUMFUNC'
            n_funcs = int(str(ctx.Integer()))

            func['name'] = funcType
            func['n_funcs'] = n_funcs

            if n_funcs <= 0:
                valid = False
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                f"{funcType} the number of functions 'n_funcs={n_funcs}' must be a positive value.")
            elif ctx.func_type_def(n_funcs - 1):
                pass
            else:
                valid = False
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                f"{funcType} requires {n_funcs} function definitions after the first 'n_funcs' value.")

            func['func_types'] = []

            if valid:
                self.stackFuncs.append(func)

    # Exit a parse tree produced by RosettaMRParser#func_type_def.
    def exitFunc_type_def(self, ctx: RosettaMRParser.Func_type_defContext):
        """
        (CIRCULARHARMONIC | HARMONIC | SIGMOID | SQUARE_WELL) Float Float |
        BOUNDED Float Float Float Float? Simple_name* |
        PERIODICBOUNDED Float Float Float Float Float? Simple_name* |
        OFFSETPERIODICBOUNDED Float Float Float Float Float Float? Simple_name* |
        (AMBERPERIODIC | CHARMMPERIODIC | FLAT_HARMONIC | TOPOUT) Float Float Float |
        (CIRCULARSIGMOIDAL | LINEAR_PENALTY) Float Float Float Float |
        CIRCULARSPLINE Float+ |
        GAUSSIANFUNC Float Float Simple_name (WEIGHT Float)? |
        SOGFUNC Integer (Float Float Float)+ |
        (MIXTUREFUNC | KARPLUS | SOEDINGFUNC) Float Float Float Float Float Float |
        CONSTANTFUNC Float |
        IDENTITY |
        SCALARWEIGHTEDFUNC Float func_type_def |
        SUMFUNC Integer func_type_def+ |
        SPLINE Simple_name (Float Float Float | NONE Float Float Float (Simple_name Float*)+) // histogram_file_path can not be evaluated
        FADE Float Float Float Float Float? |
        SQUARE_WELL2 Float Float Float DEGREES? |
        ETABLE Float Float Float* |
        USOG Integer (Float Float Float Float)+ |
        SOG Integer (Float Float Float Float Float Float)+;
        """

        fnum_offset = 0
        if len(self.stackFuncs) > 0 and self.stackFuncs[-1]['name'] == 'SCALARWEIGHTEDFUNC':
            fnum_offset = 1

        try:

            func = {}
            valid = True

            if len(self.numberFSelection) == 0 or None in self.numberFSelection:
                return

            if ctx.CIRCULARHARMONIC() or ctx.HARMONIC() or ctx.SIGMOID() or ctx.SQUARE_WELL():
                x0 = self.numberFSelection[fnum_offset]

                func['x0'] = x0

                if ctx.CIRCULARHARMONIC():  # x0 sd
                    funcType = 'CIRCULARHARMONIC'

                    sd = self.numberFSelection[fnum_offset + 1]

                    func['sd'] = sd

                    if sd <= 0.0:
                        valid = False
                        self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                        f"{funcType} standard deviation 'sd={sd}' must be a positive value.")

                    func['target_value'] = x0
                    func['lower_limit'] = x0 - sd
                    func['upper_limit'] = x0 + sd

                elif ctx.HARMONIC():  # x0 sd
                    funcType = 'HARMONIC'

                    sd = self.numberFSelection[fnum_offset + 1]

                    func['sd'] = sd

                    if sd <= 0.0:
                        valid = False
                        self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                        f"{funcType} standard deviation 'sd={sd}' must be a positive value.")

                    func['target_value'] = x0
                    func['lower_limit'] = x0 - sd
                    func['upper_limit'] = x0 + sd

                elif ctx.SIGMOID():  # x0 m
                    funcType = 'SIGMOID'

                    m = self.numberFSelection[fnum_offset + 1]

                    func['m'] = m

                    if m > 0.0:
                        func['upper_linear_limit'] = x0
                    else:
                        func['lower_lienar_limit'] = x0

                else:  # x0 depth
                    funcType = 'SQUARE_WELL'

                    depth = self.numberFSelection[fnum_offset + 1]

                    func['depth'] = depth

                    if depth > 0.0:
                        func['lower_linear_limit'] = x0
                    elif depth < 0.0:
                        func['upper_linear_limit'] = x0

                func['name'] = funcType

            elif ctx.BOUNDED():  # lb ub sd rswitch tag
                funcType = 'BOUNDED'
                lb = self.numberFSelection[fnum_offset]
                ub = self.numberFSelection[fnum_offset + 1]
                sd = self.numberFSelection[fnum_offset + 2]
                rswitch = 0.5

                func['name'] = funcType
                func['lb'] = lb
                func['ub'] = ub
                func['sd'] = sd

                if self.__remediate and self.__reasons is not None:
                    if self.__cur_subtype == 'dist' and 'dist_unusual_order' in self.__reasons:
                        target_value, dminus, dplus = lb, ub, sd
                        func['lb'] = target_value - dminus
                        func['ub'] = target_value + dplus
                        func['sd'] = (dminus + dplus) / 2.0

                if lb > ub:
                    valid = False
                    self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                    f"{funcType} lower boundary 'lb={lb}' must be less than or equal to upper boundary 'ub={ub}'.")
                    if self.__remediate:
                        if self.__cur_subtype == 'dist' and lb > sd:
                            self.__dist_lb_greater_than_ub = True
                if self.__remediate:
                    if self.__cur_subtype == 'dist' and (ub > lb or sd > lb):
                        self.__dist_ub_always_positive = False
                if sd <= 0.0:
                    valid = False
                    self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                    f"{funcType} standard deviation 'sd={sd}' must be a positive value.")

                if len(self.numberFSelection) > 4 + fnum_offset:  # DAOTHER-8932, tag must be numeric, otherwise rswitch will be ignored
                    rswitch = self.numberFSelection[fnum_offset + 3]

                    func['rswitch'] = rswitch

                    if rswitch < 0.0:
                        valid = False
                        self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                        f"{funcType} additional value for switching from the upper limit to the upper linear limit "
                                        f"'rswitch={rswitch}' must not be a negative value.")

                    func['tag'] = str(self.numberFSelection[fnum_offset + 4])

                func['lower_limit'] = lb
                func['upper_limit'] = ub

                if ub + rswitch < DIST_ERROR_MAX or self.__cur_subtype != 'dist':
                    func['upper_linear_limit'] = ub + rswitch
                if lb - rswitch >= DIST_ERROR_MIN or self.__cur_subtype != 'dist':
                    func['lower_linear_limit'] = lb - rswitch

            elif ctx.PERIODICBOUNDED():  # period lb ub sd rswitch tag
                funcType = 'PERIODICBOUNDED'

                period = self.numberFSelection[fnum_offset]
                lb = self.numberFSelection[fnum_offset + 1]
                ub = self.numberFSelection[fnum_offset + 2]
                sd = self.numberFSelection[fnum_offset + 3]
                rswitch = 0.5

                func['name'] = funcType
                func['period'] = period
                func['lb'] = lb
                func['ub'] = ub
                func['sd'] = sd

                if self.__remediate and self.__reasons is not None:
                    if self.__cur_subtype == 'dist' and 'dist_unusual_order' in self.__reasons:
                        target_value, dminus, dplus = lb, ub, sd
                        func['lb'] = target_value - dminus
                        func['ub'] = target_value + dplus
                        func['sd'] = (dminus + dplus) / 2.0

                if period < 0.0:
                    valid = False
                    self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                    f"{funcType} 'period={period}' must not be a negative value.")
                if lb > ub:
                    valid = False
                    self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                    f"{funcType} lower boundary 'lb={lb}' must be less than or equal to upper boundary 'ub={ub}'.")
                    if self.__remediate:
                        if self.__cur_subtype == 'dist' and lb > sd:
                            self.__dist_lb_greater_than_ub = True
                if self.__remediate:
                    if self.__cur_subtype == 'dist' and (ub > lb or sd > lb):
                        self.__dist_ub_always_positive = False
                if sd <= 0.0:
                    valid = False
                    self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                    f"{funcType} standard deviation 'sd={sd}' must be a positive value.")

                if len(self.numberFSelection) > 5 + fnum_offset:  # DAOTHER-8932, tag must be numeric, otherwise rswitch will be ignored
                    rswitch = self.numberFSelection[fnum_offset + 4]

                    func['rswitch'] = rswitch

                    if rswitch < 0.0:
                        valid = False
                        self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                        f"{funcType} additional value for switching from the upper limit to the upper linear limit "
                                        f"'rswitch={rswitch}' must not be a negative value.")

                    func['tag'] = str(self.numberFSelection[fnum_offset + 5])

                func['lower_limit'] = lb
                func['upper_limit'] = ub

                if ub + rswitch < DIST_ERROR_MAX or self.__cur_subtype != 'dist':
                    func['upper_linear_limit'] = ub + rswitch
                if lb - rswitch >= DIST_ERROR_MIN or self.__cur_subtype != 'dist':
                    func['lower_linear_limit'] = lb - rswitch

            elif ctx.OFFSETPERIODICBOUNDED():  # offset period lb ub sd rswitch tag
                funcType = 'OFFSETPERIODICBOUNDED'

                offset = self.numberFSelection[fnum_offset]
                period = self.numberFSelection[fnum_offset + 1]
                lb = self.numberFSelection[fnum_offset + 2]
                ub = self.numberFSelection[fnum_offset + 3]
                sd = self.numberFSelection[fnum_offset + 4]
                rswitch = 0.5

                func['name'] = funcType
                func['offset'] = offset
                func['period'] = period
                func['lb'] = lb
                func['ub'] = ub
                func['sd'] = sd

                if self.__remediate and self.__reasons is not None:
                    if self.__cur_subtype == 'dist' and 'dist_unusual_order' in self.__reasons:
                        target_value, dminus, dplus = lb, ub, sd
                        func['lb'] = target_value - dminus
                        func['ub'] = target_value + dplus
                        func['sd'] = (dminus + dplus) / 2.0

                if period < 0.0:
                    valid = False
                    self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                    f"{funcType} 'period={period}' must not be a negative value.")
                if lb > ub:
                    valid = False
                    self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                    f"{funcType} lower boundary 'lb={lb}' must be less than or equal to upper boundary 'ub={ub}'.")
                    if self.__remediate:
                        if self.__cur_subtype == 'dist' and lb > sd:
                            self.__dist_lb_greater_than_ub = True
                if self.__remediate:
                    if self.__cur_subtype == 'dist' and (ub > lb or sd > lb):
                        self.__dist_ub_always_positive = False
                if sd <= 0.0:
                    valid = False
                    self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                    f"{funcType} standard deviation 'sd={sd}' must be a positive value.")

                if len(self.numberFSelection) > 6 + fnum_offset:  # DAOTHER-8932, tag must be numeric, otherwise rswitch will be ignored
                    rswitch = self.numberFSelection[fnum_offset + 5]

                    func['rswitch'] = rswitch

                    if rswitch < 0.0:
                        valid = False
                        self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                        f"{funcType} additional value for switching from the upper limit to the upper linear limit "
                                        f"'rswitch={rswitch}' must not be a negative value.")

                    func['tag'] = str(self.numberFSelection[fnum_offset + 6])

                func['lower_limit'] = lb + offset
                func['upper_limit'] = ub + offset

                if ub + rswitch < DIST_ERROR_MAX or self.__cur_subtype != 'dist':
                    func['upper_linear_limit'] = ub + rswitch
                if lb - rswitch >= DIST_ERROR_MIN or self.__cur_subtype != 'dist':
                    func['lower_linear_limit'] = lb - rswitch

            elif ctx.AMBERPERIODIC() or ctx.CHARMMPERIODIC():  # x0 n_period k
                funcType = 'AMBERPERIODIC' if ctx.AMBERPERIODIC() else 'CHARMMPERIODIC'
                x0 = self.numberFSelection[fnum_offset]
                n_period = self.numberFSelection[fnum_offset + 1]
                k = self.numberFSelection[fnum_offset + 2]

                func['name'] = funcType
                func['x0'] = x0
                func['n_period'] = n_period
                func['k'] = k

                if period < 0.0:
                    valid = False
                    self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                    f"{funcType} periodicity 'n_period={n_period}' must not be a negative value.")

            elif ctx.FLAT_HARMONIC() or ctx.TOPOUT():
                funcType = 'FLAT_HARMONIC' if ctx.FLAT_HARMONIC() else 'TOPOUT'

                if ctx.FLAT_HARMONIC():  # x0 sd tol
                    x0 = self.numberFSelection[fnum_offset]
                    sd = self.numberFSelection[fnum_offset + 1]
                    tol = self.numberFSelection[fnum_offset + 2]

                    func['x0'] = x0
                    func['sd'] = sd
                    func['tol'] = tol

                    if sd <= 0.0:
                        valid = False
                        self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                        f"{funcType} standard deviation 'sd={sd}' must be a positive value.")
                    if tol < 0.0:
                        valid = False
                        self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                        f"{funcType} tolerance 'tol={tol}' must not be a negative value.")

                    func['target_value'] = x0
                    func['lower_limit'] = x0 - tol - sd
                    func['upper_limit'] = x0 + tol + sd

                else:  # weight x0 limit
                    weight = self.numberFSelection[fnum_offset]
                    x0 = self.numberFSelection[fnum_offset + 1]
                    limit = self.numberFSelection[fnum_offset + 2]

                    func['weight'] = weight
                    func['x0'] = x0
                    func['limit'] = limit

                    if weight < 0.0:
                        valid = False
                        self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                        f"{funcType} 'weight={weight}' must not be a negative value.")
                    elif weight == 0.0:
                        self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                        f"{funcType} 'weight={weight}' should be a positive value.")

                    if limit <= 0.0:
                        valid = False
                        self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                        f"{funcType} 'limit={limit}' must be a positive value.")

                    func['target_value'] = x0
                    func['lower_limit'] = x0 - limit
                    func['upper_limit'] = x0 + limit

                func['name'] = funcType

            elif ctx.CIRCULARSIGMOIDAL() or ctx.LINEAR_PENALTY():
                funcType = 'CIRCULARSIGMOIDAL' if ctx.CIRCULARSIGMOIDAL() else 'LINEAR_PENALTY'

                if ctx.CIRCULARSIGMOIDAL():  # xC m o1 o2
                    xC = self.numberFSelection[fnum_offset]
                    m = self.numberFSelection[fnum_offset + 1]
                    o1 = self.numberFSelection[fnum_offset + 2]
                    o2 = self.numberFSelection[fnum_offset + 3]

                    func['xC'] = xC
                    func['m'] = m
                    func['o1'] = o1
                    func['o2'] = o2

                    if m < 0.0:
                        valid = False
                        self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                        f"{funcType} periodicity 'm={m}' must not be a negative value.")

                else:  # x0 depth width slope
                    x0 = self.numberFSelection[fnum_offset]
                    depth = self.numberFSelection[fnum_offset + 1]
                    width = self.numberFSelection[fnum_offset + 2]
                    slope = self.numberFSelection[fnum_offset + 3]

                    func['x0'] = x0
                    func['depth'] = depth
                    func['width'] = width
                    func['slope'] = slope

                    if width < 0.0:
                        valid = False
                        self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                        f"{funcType} 'width={width}' must not be a negative value.")
                    if slope < 0.0:
                        valid = False
                        self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                        f"{funcType} 'slope={slope}' must not be a negative value.")

                    func['lower_linear_limit'] = x0 - width
                    func['upper_linear_limit'] = x0 + width

                func['name'] = funcType

            elif ctx.CIRCULARSPLINE():  # weight [36 energy values]
                funcType = 'CIRCULARSPLINE'
                weight = self.numberFSelection[fnum_offset]

                func['name'] = funcType
                func['weight'] = weight

                if weight < 0.0:
                    valid = False
                    self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                    f"{funcType} 'weight={weight}' must not be a negative value.")
                elif weight == 0.0:
                    self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                    f"{funcType} 'weight={weight}' should be a positive value.")

                if len(self.numberFSelection) > 36 + fnum_offset:
                    func['energy'] = []
                    for i in range(36):
                        func['energy'].append(self.numberFSelection[fnum_offset + i + 1])
                else:
                    valid = False
                    self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                    f"{funcType} requires consecutive 36 energy values, following the first weight value.")

            elif ctx.GAUSSIANFUNC():  # mean sd tag WEIGHT weight
                funcType = 'GAUSSIANFUNC'
                mean = self.numberFSelection[fnum_offset]
                sd = self.numberFSelection[fnum_offset + 1]

                func['name'] = funcType
                func['mean'] = mean
                func['sd'] = sd
                func['tag'] = str(ctx.Simple_name(0))

                if sd <= 0.0:
                    valid = False
                    self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                    f"{funcType} standard deviation 'sd={sd}' must be a positive value.")

                if ctx.WEIGHT():
                    weight = self.numberFSelection[fnum_offset + 2]

                    func['weight'] = weight

                    if weight < 0.0:
                        valid = False
                        self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                        f"{funcType} 'weight={weight}' must not be a negative value.")
                    elif weight == 0.0:
                        self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                        f"{funcType} 'weight={weight}' should be a positive value.")

                func['target_value'] = mean
                func['lower_limit'] = mean - sd
                func['upper_limit'] = mean + sd

            elif ctx.SOGFUNC():  # n_funcs [mean1 sdev1 weight1 [mean2 sdev2 weight2 [...]]]
                funcType = 'SOGFUNC'
                n_funcs = int(str(ctx.Integer()))

                func['name'] = funcType
                func['n_funcs'] = n_funcs

                if n_funcs <= 0:
                    valid = False
                    self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                    f"{funcType} the number of Gaussian functions 'n_funcs={n_funcs}' must be a positive value.")
                elif len(self.numberFSelection) > n_funcs * 3 - 1 + fnum_offset:
                    func['mean'] = []
                    func['sdev'] = []
                    func['weight'] = []
                    for n in range(n_funcs):
                        p = n * 3
                        mean = self.numberFSelection[fnum_offset + p]
                        sdev = self.numberFSelection[fnum_offset + p + 1]
                        weight = self.numberFSelection[fnum_offset + p + 2]

                        func['mean'].append(mean)
                        func['sdev'].append(sdev)
                        func['weight'].append(weight)

                        if n_funcs == 1:
                            func['target_value'] = mean
                            func['lower_limit'] = mean - sdev
                            func['upper_limit'] = mean + sdev

                        if sdev <= 0.0:
                            valid = False
                            self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                            f"{funcType} standard deviation 'sdev={sdev}' of {n+1}th function must be a positive value.")
                        if weight < 0.0:
                            valid = False
                            self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                            f"{funcType} 'weight={weight}' of {n+1}th function must not be a negative value.")
                        elif weight == 0.0:
                            self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                            f"{funcType} 'weight={weight}' of {n+1}th function should be a positive value.")

                else:
                    valid = False
                    self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                    f"{funcType} requires consecutive 3 parameters (mean, sdev, weight) for each Gaussian function after the first 'n_funcs' value.")

            elif ctx.MIXTUREFUNC() or ctx.KARPLUS() or ctx.SOEDINGFUNC():
                if ctx.MIXTUREFUNC():  # anchor gaussian_param exp_param mixture_param bg_mean bg_sd
                    funcType = 'MIXTUREFUNC'
                    anchor = self.numberFSelection[fnum_offset]
                    gaussian_param = self.numberFSelection[fnum_offset + 1]
                    exp_param = self.numberFSelection[fnum_offset + 2]
                    mixture_param = self.numberFSelection[fnum_offset + 3]
                    bg_mean = self.numberFSelection[fnum_offset + 4]
                    bg_sd = self.numberFSelection[fnum_offset + 5]

                    func['name'] = funcType
                    func['anchor'] = anchor
                    func['gaussian_param'] = gaussian_param
                    func['exp_param'] = exp_param
                    func['mixture_param'] = mixture_param
                    func['bg_mean'] = bg_mean
                    func['bg_sd'] = bg_sd

                    if gaussian_param <= 0.0:
                        valid = False
                        self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                        f"{funcType} standard deviation of a Gaussian distribution "
                                        f"'gaussian_param={gaussian_param}' must be a positive value.")
                    if exp_param <= 0.0:
                        valid = False
                        self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                        f"{funcType} rate at which the exponential distribution drops off "
                                        f"'exp_param={exp_param}' must be a positive value.")
                    if mixture_param <= 0.0:
                        valid = False
                        self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                        f"{funcType} mixture of the Gaussian and Exponential functions "
                                        f"'mixture_param={mixture_param}' that make up g(r) function must be a positive value.")
                    if bg_sd <= 0.0:
                        valid = False
                        self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                        f"{funcType} standard deviation 'bg_sd={bg_sd}' of h(r) function must be a positive value.")

                elif ctx.KARPLUS():  # A B C D x0 sd
                    funcType = 'KARPLUS'
                    A = self.numberFSelection[fnum_offset]
                    B = self.numberFSelection[fnum_offset + 1]
                    C = self.numberFSelection[fnum_offset + 2]
                    D = self.numberFSelection[fnum_offset + 3]
                    x0 = self.numberFSelection[fnum_offset + 4]
                    sd = self.numberFSelection[fnum_offset + 5]

                    func['A'] = A
                    func['B'] = B
                    func['C'] = C
                    func['D'] = D
                    func['x0'] = x0
                    func['sd'] = sd

                    if sd <= 0.0:
                        valid = False
                        self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                        f"{funcType} standard deviation 'sd={sd}' must be a positive value.")

                else:  # w1 mean1 sd1 w2 mean2 sd2
                    funcType = 'SOEDINGFUNC'
                    w1 = self.numberFSelection[fnum_offset]
                    mean1 = self.numberFSelection[fnum_offset + 1]
                    sd1 = self.numberFSelection[fnum_offset + 2]
                    w2 = self.numberFSelection[fnum_offset + 3]
                    mean2 = self.numberFSelection[fnum_offset + 4]
                    sd2 = self.numberFSelection[fnum_offset + 5]

                    func['w1'] = w1
                    func['mean1'] = mean1
                    func['sd1'] = sd1
                    func['w2'] = w2
                    func['mean2'] = mean2
                    func['sd2'] = sd2

                    if w1 < 0.0:
                        valid = False
                        self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                        f"{funcType} weight of the 1st Gaussian function 'w1={w1}' must not be a negative value.")
                    if w2 < 0.0:
                        valid = False
                        self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                        f"{funcType} weight of the 2nd Gaussian function 'w2={w2}' must not be a negative value.")
                    if sd1 <= 0.0:
                        valid = False
                        self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                        f"{funcType} standard deviation of the 1st Gaussian function 'sd1={sd1}' must be a positive value.")
                    if sd2 <= 0.0:
                        valid = False
                        self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                        f"{funcType} standard deviation of the 2nd Gaussian function 'sd2={sd2}' must be a positive value.")

            elif ctx.CONSTANTFUNC():  # return_val
                funcType = 'CONSTANTFUNC'
                return_val = self.numberFSelection[fnum_offset]

                func['name'] = funcType
                func['return_val'] = return_val

            elif ctx.IDENTITY():
                func['name'] = 'IDENTITY'

            elif ctx.SPLINE():  # description (NONE) experimental_value weight bin_size (x_axis val*)+
                funcType = 'SPLINE'
                description = str(ctx.Simple_name(0))
                experimental_value = self.numberFSelection[fnum_offset]
                weight = self.numberFSelection[fnum_offset + 1]
                bin_size = self.numberFSelection[fnum_offset + 2]

                func['name'] = funcType
                func['description'] = description
                func['experimental_value'] = experimental_value
                func['weight'] = weight
                func['bin_size'] = bin_size

                if weight < 0.0:
                    valid = False
                    self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                    f"{funcType} 'weight={weight}' must not be a negative value.")
                elif weight == 0.0:
                    self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                    f"{funcType} 'weight={weight}' should be a positive value.")

                if bin_size <= 0.0:
                    valid = False
                    self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                    f"{funcType} 'bin_size={bin_size}' must be a positive value.")

            elif ctx.FADE():  # lb ub d wd [ wo ]
                funcType = 'FADE'
                lb = self.numberFSelection[fnum_offset]
                ub = self.numberFSelection[fnum_offset + 1]
                d = self.numberFSelection[fnum_offset + 2]
                wd = self.numberFSelection[fnum_offset + 3]
                wo = 0.0

                func['name'] = funcType
                func['lb'] = lb
                func['ub'] = ub
                func['d'] = d  # fade zone
                func['wd'] = wd  # well depth

                if lb > ub:
                    valid = False
                    self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                    f"{funcType} lower boundary 'lb={lb}' must be less than or equal to upper boundary 'ub={ub}'.")

                if d < 0.0:
                    valid = False
                    self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                    f"{funcType} fade zone 'd={d}' must not be a negative value.")

                if len(self.numberFSelection) > 4 + fnum_offset:
                    wo = self.numberFSelection[fnum_offset + 4]

                    func['wo'] = wo  # well offset

            elif ctx.SQUARE_WELL2():  # x0 width depth [DEGREES]
                funcType = 'SQUARE_WELL2'
                x0 = self.numberFSelection[fnum_offset]
                width = self.numberFSelection[fnum_offset + 2]
                depth = self.numberFSelection[fnum_offset + 1]

                func['name'] = funcType
                func['x0'] = x0
                func['width'] = width
                func['depth'] = depth

                if weight < 0.0:
                    valid = False
                    self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                    f"{funcType} 'weight={weight}' must not be a negative value.")
                elif weight == 0.0:
                    self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                    f"{funcType} 'weight={weight}' should be a positive value.")

                if ctx.DEGREES():
                    func['unit'] = 'degrees'
                    func['lower_linear_limit'] = x0 - width
                    func['upper_linear_limit'] = x0 + width
                else:
                    func['unit'] = 'radians'
                    func['lower_linear_limit'] = numpy.degrees(x0 - width)
                    func['upper_linear_limit'] = numpy.degrees(x0 + width)

            elif ctx.ETABLE():  # min max [many numbers]
                funcType = 'ETABLE'
                _min = self.numberFSelection[fnum_offset]
                _max = self.numberFSelection[fnum_offset + 1]

                func['name'] = funcType
                func['min'] = _min
                func['max'] = _max

                if _min > _max:
                    valid = False
                    self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                    f"{funcType} 'min={_min}' must be less than or equal to 'max={_max}'.")

                if len(self.numberFSelection) > 2 + fnum_offset:
                    pass
                else:
                    valid = False
                    self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                    f"{funcType} requires parameters after the first 'min' and the second 'max' values.")

            elif ctx.USOG():  # num_gaussians mean1 sd1 mean2 sd2...
                funcType = 'USOG'
                num_gaussians = int(str(ctx.Integer()))

                func['name'] = funcType
                func['num_gaussians'] = num_gaussians

                if num_gaussians <= 0:
                    valid = False
                    self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                    f"{funcType} the number of Gaussian functions 'num_gaussians={num_gaussians}' must be a positive value.")
                elif len(self.numberFSelection) > num_gaussians * 2 - 1 + fnum_offset:
                    func['mean'] = []
                    func['sd'] = []
                    for n in range(num_gaussians):
                        p = n * 2
                        mean = self.numberFSelection[fnum_offset + p]
                        sd = self.numberFSelection[fnum_offset + p + 1]

                        func['mean'].append(mean)
                        func['sd'].append(sd)

                        if num_gaussians == 1:
                            func['target_value'] = mean
                            func['lower_limit'] = mean - sd
                            func['upper_limit'] = mean + sd

                        if sd <= 0.0:
                            valid = False
                            self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                            f"{funcType} standard deviation 'sd={sd}' of {n+1}th function must be a positive value.")
                else:
                    valid = False
                    self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                    f"{funcType} requires consecutive 2 parameters (mean, sd) for each Gaussian function after the first 'num_gaussians' value.")

            elif ctx.SOG():  # num_gaussians mean1 sd1 weight1 mean2 sd2 weight2...
                funcType = 'SOG'
                num_gaussians = int(str(ctx.Integer()))

                func['name'] = funcType
                func['num_gaussians'] = num_gaussians

                if num_gaussians <= 0:
                    valid = False
                    self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                    f"{funcType} the number of Gaussian functions 'num_gaussians={num_gaussians}' must be a positive value.")
                elif len(self.numberFSelection) > num_gaussians * 3 - 1 + fnum_offset:
                    func['mean'] = []
                    func['sd'] = []
                    func['weight'] = []
                    for n in range(num_gaussians):
                        p = n * 3
                        mean = self.numberFSelection[fnum_offset + p]
                        sd = self.numberFSelection[fnum_offset + p + 1]
                        weight = self.numberFSelection[fnum_offset + p + 2]

                        func['mean'].append(mean)
                        func['sd'].append(sd)
                        func['weight'].append(weight)

                        if num_gaussians == 1:
                            func['target_value'] = mean
                            func['lower_limit'] = mean - sd
                            func['upper_limit'] = mean + sd

                        if sd <= 0.0:
                            valid = False
                            self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                            f"{funcType} standard deviation 'sd={sd}' of {n+1}th function must be a positive value.")
                        if weight < 0.0:
                            valid = False
                            self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                            f"{funcType} 'weight={weight}' of {n+1}th function must not be a negative value.")
                        elif weight == 0.0:
                            self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                            f"{funcType} 'weight={weight}' of {n+1}th function should be a positive value.")
                else:
                    valid = False
                    self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                    f"{funcType} requires consecutive 3 parameters (mean, sd, weight) for each Gaussian function after the first 'num_gaussians' value.")

            if valid:
                self.stackFuncs.append(func)

        except ValueError:
            pass

        finally:
            self.numberFSelection.clear()

    # Enter a parse tree produced by RosettaMRParser#rdc_restraints.
    def enterRdc_restraints(self, ctx: RosettaMRParser.Rdc_restraintsContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'rdc'

    # Exit a parse tree produced by RosettaMRParser#rdc_restraints.
    def exitRdc_restraints(self, ctx: RosettaMRParser.Rdc_restraintsContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by RosettaMRParser#rdc_restraint.
    def enterRdc_restraint(self, ctx: RosettaMRParser.Rdc_restraintContext):  # pylint: disable=unused-argument
        self.rdcRestraints += 1

        self.atomSelectionSet.clear()

    # Exit a parse tree produced by RosettaMRParser#rdc_restraint.
    def exitRdc_restraint(self, ctx: RosettaMRParser.Rdc_restraintContext):

        try:

            seqId1 = int(str(ctx.Integer(0)))
            atomId1 = str(ctx.Simple_name(0)).upper()
            seqId2 = int(str(ctx.Integer(1)))
            atomId2 = str(ctx.Simple_name(1)).upper()

            if len(self.numberSelection) == 0 or None in self.numberSelection:
                return

            target_value = self.numberSelection[0]

            validRange = True
            dstFunc = {'weight': 1.0}

            if target_value is not None:
                if RDC_ERROR_MIN < target_value < RDC_ERROR_MAX:
                    dstFunc['target_value'] = f"{target_value}"
                else:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                    f"The target value='{target_value}' must be within range {RDC_RESTRAINT_ERROR}.")

            if not validRange:
                return

            if target_value is not None:
                if RDC_RANGE_MIN < target_value < RDC_RANGE_MAX:
                    pass
                else:
                    self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                    f"The target value='{target_value}' should be within range {RDC_RESTRAINT_RANGE}.")

            if not self.__hasPolySeq and not self.__hasNonPolySeq:
                return

            self.__retrieveLocalSeqScheme()

            chainAssign1 = self.assignCoordPolymerSequence(seqId1, atomId1)
            chainAssign2 = self.assignCoordPolymerSequence(seqId2, atomId2)

            if 0 in (len(chainAssign1), len(chainAssign2)):
                return

            self.selectCoordAtoms(chainAssign1, seqId1, atomId1, False, 'an RDC')
            self.selectCoordAtoms(chainAssign2, seqId2, atomId2, False, 'an RDC')

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
                                  rdcCode=getRdcCode([self.atomSelectionSet[0][0], self.atomSelectionSet[1][0]]))
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
                    print(f"subtype={self.__cur_subtype} (CS-ROSETTA: RDC) id={self.rdcRestraints} "
                          f"atom1={atom1} atom2={atom2} {dstFunc}")
                if self.__createSfDict and sf is not None:
                    sf['index_id'] += 1
                    row = getRow(self.__cur_subtype, sf['id'], sf['index_id'],
                                 combinationId, None, None,
                                 sf['list_id'], self.__entryId, dstFunc,
                                 self.__authToStarSeq, self.__authToOrigSeq, self.__authToInsCode, self.__offsetHolder,
                                 atom1, atom2)
                    sf['loop'].add_data(row)

            if self.__createSfDict and sf is not None and isinstance(combinationId, int) and combinationId == 1:
                sf['loop'].data[-1] = resetCombinationId(self.__cur_subtype, sf['loop'].data[-1])

        except (ValueError, IndexError):
            self.rdcRestraints -= 1

        finally:
            self.numberSelection.clear()

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

    # Enter a parse tree produced by RosettaMRParser#disulfide_bond_linkages.
    def enterDisulfide_bond_linkages(self, ctx: RosettaMRParser.Disulfide_bond_linkagesContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'ssbond'

    # Exit a parse tree produced by RosettaMRParser#disulfide_bond_linkages.
    def exitDisulfide_bond_linkages(self, ctx: RosettaMRParser.Disulfide_bond_linkagesContext):
        pass

    # Enter a parse tree produced by RosettaMRParser#disulfide_bond_linkage.
    def enterDisulfide_bond_linkage(self, ctx: RosettaMRParser.Disulfide_bond_linkageContext):  # pylint: disable=unused-argument
        self.ssbondRestraints += 1

        self.atomSelectionSet.clear()

    # Exit a parse tree produced by RosettaMRParser#disulfide_bond_linkage.
    def exitDisulfide_bond_linkage(self, ctx: RosettaMRParser.Disulfide_bond_linkageContext):

        try:

            try:
                seqId1 = int(str(ctx.Integer(0)))
                seqId2 = int(str(ctx.Integer(1)))
            except ValueError:
                self.ssbondRestraints -= 1
                return

            if not self.__hasPolySeq and not self.__hasNonPolySeq:
                return

            self.__retrieveLocalSeqScheme()

            chainAssign1 = self.assignCoordPolymerSequence(seqId1)
            chainAssign2 = self.assignCoordPolymerSequence(seqId2)

            if 0 in (len(chainAssign1), len(chainAssign2)):
                return

            self.selectCoordAtoms(chainAssign1, seqId1, 'SG')
            self.selectCoordAtoms(chainAssign2, seqId2, 'SG')

            if len(self.atomSelectionSet) < 2:
                return

            for atom1 in self.atomSelectionSet[0]:
                if atom1['comp_id'] != 'CYS':
                    self.__f.append(f"[Invalid atom selection] {self.__getCurrentRestraint()}"
                                    f"Failed to select a Cystein residue for disulfide bond between '{seqId1}' and '{seqId2}'.")
                    return

            for atom2 in self.atomSelectionSet[1]:
                if atom2['comp_id'] != 'CYS':
                    self.__f.append(f"[Invalid atom selection] {self.__getCurrentRestraint()}"
                                    f"Failed to select a Cystein residue for disulfide bond between '{seqId1}' and '{seqId2}'.")
                    return

            chain_id_1 = self.atomSelectionSet[0][0]['chain_id']
            seq_id_1 = self.atomSelectionSet[0][0]['seq_id']
            atom_id_1 = self.atomSelectionSet[0][0]['atom_id']

            chain_id_2 = self.atomSelectionSet[1][0]['chain_id']
            seq_id_2 = self.atomSelectionSet[1][0]['seq_id']
            atom_id_2 = self.atomSelectionSet[1][0]['atom_id']

            try:

                _head =\
                    self.__cR.getDictListWithFilter('atom_site',
                                                    CARTN_DATA_ITEMS,
                                                    [{'name': self.__authAsymId, 'type': 'str', 'value': chain_id_1},
                                                     {'name': self.__authSeqId, 'type': 'int', 'value': seq_id_1},
                                                     {'name': self.__authAtomId, 'type': 'str', 'value': atom_id_1},
                                                     {'name': self.__modelNumName, 'type': 'int',
                                                      'value': self.__representativeModelId},
                                                     {'name': 'label_alt_id', 'type': 'enum',
                                                      'enum': (self.__representativeAltId,)}
                                                     ])

                _tail =\
                    self.__cR.getDictListWithFilter('atom_site',
                                                    CARTN_DATA_ITEMS,
                                                    [{'name': self.__authAsymId, 'type': 'str', 'value': chain_id_2},
                                                     {'name': self.__authSeqId, 'type': 'int', 'value': seq_id_2},
                                                     {'name': self.__authAtomId, 'type': 'str', 'value': atom_id_2},
                                                     {'name': self.__modelNumName, 'type': 'int',
                                                      'value': self.__representativeModelId},
                                                     {'name': 'label_alt_id', 'type': 'enum',
                                                      'enum': (self.__representativeAltId,)}
                                                     ])

                if len(_head) == 1 and len(_tail) == 1:
                    dist = distance(to_np_array(_head[0]), to_np_array(_tail[0]))
                    if dist > 2.5:
                        self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                        f"The distance of the disulfide bond linkage ({chain_id_1}:{seq_id_1}:{atom_id_1} - "
                                        f"{chain_id_2}:{seq_id_2}:{atom_id_2}) is too far apart in the coordinates ({dist:.3f}Å).")

            except Exception as e:
                if self.__verbose:
                    self.__lfh.write(f"+{self.__class_name__}.exitDisulfide_bond_linkage() ++ Error  - {str(e)}")

            if self.__createSfDict:
                sf = self.__getSf()
                sf['id'] += 1
                memberLogicCode = 'OR' if len(self.atomSelectionSet[0]) * len(self.atomSelectionSet[1]) > 1 else '.'

            has_intra_chain, rep_chain_id_set = hasIntraChainRestraint(self.atomSelectionSet)

            if self.__createSfDict and memberLogicCode == 'OR' and has_intra_chain and len(rep_chain_id_set) == 1:
                memberLogicCode = '.'

            memberId = '.'
            if memberLogicCode == 'OR':
                if len(self.atomSelectionSet[0]) * len(self.atomSelectionSet[1]) > 1\
                   and (isAmbigAtomSelection(self.atomSelectionSet[0], self.__csStat)
                        or isAmbigAtomSelection(self.atomSelectionSet[1], self.__csStat)):
                    memberId = 0
                    _atom1 = _atom2 = None

            for atom1, atom2 in itertools.product(self.atomSelectionSet[0],
                                                  self.atomSelectionSet[1]):
                if isIdenticalRestraint([atom1, atom2], self.__nefT):
                    continue
                if self.__createSfDict and isinstance(memberId, int):
                    star_atom1 = getStarAtom(self.__authToStarSeq, self.__authToOrigSeq, self.__offsetHolder, copy.copy(atom1))
                    star_atom2 = getStarAtom(self.__authToStarSeq, self.__authToOrigSeq, self.__offsetHolder, copy.copy(atom2))
                    if None in (star_atom1, star_atom2) or isIdenticalRestraint([star_atom1, star_atom2], self.__nefT):
                        continue
                if has_intra_chain and (atom1['chain_id'] != atom2['chain_id'] or atom1['chain_id'] not in rep_chain_id_set):
                    continue
                if self.__debug:
                    print(f"subtype={self.__cur_subtype} (CS-ROSETTA: disulfide bond linkage) id={self.ssbondRestraints} "
                          f"atom1={atom1} atom2={atom2}")
                if self.__createSfDict and sf is not None:
                    if isinstance(memberId, int):
                        if _atom1 is None or isAmbigAtomSelection([_atom1, atom1], self.__csStat)\
                           or isAmbigAtomSelection([_atom2, atom2], self.__csStat):
                            memberId += 1
                            _atom1, _atom2 = atom1, atom2
                    sf['index_id'] += 1
                    row = getRow(self.__cur_subtype, sf['id'], sf['index_id'],
                                 '.', memberId, memberLogicCode,
                                 sf['list_id'], self.__entryId, getDstFuncForSsBond(atom1, atom2),
                                 self.__authToStarSeq, self.__authToOrigSeq, self.__authToInsCode, self.__offsetHolder,
                                 atom1, atom2)
                    sf['loop'].add_data(row)

        finally:
            self.atomSelectionSet.clear()

    # Enter a parse tree produced by RosettaMRParser#atom_pair_w_chain_restraints.
    def enterAtom_pair_w_chain_restraints(self, ctx: RosettaMRParser.Atom_pair_w_chain_restraintsContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'dist'

        self.__cur_comment_inlined = True

    # Exit a parse tree produced by RosettaMRParser#atom_pair_w_chain_restraints.
    def exitAtom_pair_w_chain_restraints(self, ctx: RosettaMRParser.Atom_pair_w_chain_restraintsContext):  # pylint: disable=unused-argument
        self.__cur_comment_inlined = False

    # Enter a parse tree produced by RosettaMRParser#atom_pair_w_chain_restraint.
    def enterAtom_pair_w_chain_restraint(self, ctx: RosettaMRParser.Atom_pair_w_chain_restraintContext):  # pylint: disable=unused-argument
        self.distRestraints += 1

        self.stackFuncs.clear()
        self.atomSelectionSet.clear()

    # Exit a parse tree produced by RosettaMRParser#atom_pair_w_chain_restraint.
    def exitAtom_pair_w_chain_restraint(self, ctx: RosettaMRParser.Atom_pair_w_chain_restraintContext):

        try:

            seqId1 = int(str(ctx.Integer(0)))
            atomId1 = str(ctx.Simple_name(0)).upper()
            chainId1 = str(ctx.Simple_name(1))
            seqId2 = int(str(ctx.Integer(1)))
            atomId2 = str(ctx.Simple_name(2)).upper()
            chainId2 = str(ctx.Simple_name(3))

            if len(self.atomSelectionInComment) == 2:
                matched = True
                for atomSel in self.atomSelectionInComment:
                    if atomSel['atom_id'] not in (atomId1, atomId2):
                        matched = False
                        break
                if matched:
                    for idx, atomSel in enumerate(self.atomSelectionInComment):
                        if idx == 0:
                            seqId1 = atomSel['seq_id']
                            atomId1 = atomSel['atom_id']
                        else:
                            seqId2 = atomSel['seq_id']
                            atomId2 = atomSel['atom_id']

            if not self.__hasPolySeq and not self.__hasNonPolySeq:
                return

            self.__retrieveLocalSeqScheme()

            chainAssign1 = self.assignCoordPolymerSequence(seqId1, atomId1, fixedChainId=chainId1)
            chainAssign2 = self.assignCoordPolymerSequence(seqId2, atomId2, fixedChainId=chainId2)

            if 0 in (len(chainAssign1), len(chainAssign2)):
                return

            self.selectCoordAtoms(chainAssign1, seqId1, atomId1)
            self.selectCoordAtoms(chainAssign2, seqId2, atomId2)

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

            dstFunc = self.validateDistanceRange(1.0)

            if dstFunc is None:
                return

            isNested = len(self.stackNest) > 0
            isMulti = isNested and self.stackNest[-1]['type'] == 'multi'

            if self.__createSfDict:
                sf = self.__getSf(constraintType=getDistConstraintType(self.atomSelectionSet, dstFunc,
                                                                       self.__csStat, self.__originalFileName),
                                  potentialType=getPotentialType(self.__file_type, self.__cur_subtype, dstFunc))
                if not isNested or self.__is_first_nest:
                    sf['id'] += 1
                memberLogicCode = 'OR' if len(self.atomSelectionSet[0]) * len(self.atomSelectionSet[1]) > 1 or isNested else '.'

            if isNested:
                if self.__debug:
                    print(f"NESTED: {self.stackNest}")

            has_intra_chain, rep_chain_id_set = hasIntraChainRestraint(self.atomSelectionSet)

            combinationId = '.'
            if isNested and self.__nest_combination_id > 0:
                combinationId = self.__nest_combination_id

            memberId = '.'
            if self.__createSfDict:
                if memberLogicCode == 'OR' and has_intra_chain and len(rep_chain_id_set) == 1 and not isNested:
                    if not self.atomSelectionSet[0][0]['auth_atom_id'].upper().startswith('CEN')\
                       and not self.atomSelectionSet[1][0]['auth_atom_id'].upper().startswith('CEN'):
                        memberLogicCode = '.'

                if memberLogicCode == 'OR':
                    if isNested:
                        memberId = self.__nest_member_id
                        _atom1 = _atom2 = None
                    elif len(self.atomSelectionSet[0]) * len(self.atomSelectionSet[1]) > 1\
                            and (isAmbigAtomSelection(self.atomSelectionSet[0], self.__csStat)
                                 or isAmbigAtomSelection(self.atomSelectionSet[1], self.__csStat)):
                        memberId = 0
                        _atom1 = _atom2 = None

                combinationId = '.'
                if isNested and self.__nest_combination_id > 0:
                    combinationId = self.__nest_combination_id

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
                    print(f"subtype={self.__cur_subtype} id={self.distRestraints} "
                          f"atom1={atom1} atom2={atom2} {dstFunc}")
                if self.__createSfDict and sf is not None:
                    if isinstance(memberId, int):
                        if isNested:
                            memberId += 1
                            self.__nest_member_id = memberId
                            _atom1, _atom2 = atom1, atom2
                        elif _atom1 is None or isAmbigAtomSelection([_atom1, atom1], self.__csStat)\
                                or isAmbigAtomSelection([_atom2, atom2], self.__csStat):
                            memberId += 1
                            _atom1, _atom2 = atom1, atom2
                    sf['index_id'] += 1
                    row = getRow(self.__cur_subtype, sf['id'], sf['index_id'],
                                 combinationId, memberId, 'AND' if isMulti else memberLogicCode,
                                 sf['list_id'], self.__entryId, dstFunc,
                                 self.__authToStarSeq, self.__authToOrigSeq, self.__authToInsCode, self.__offsetHolder,
                                 atom1, atom2)
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

            if self.__createSfDict and sf is not None:
                if isinstance(memberId, int) and memberId == 1:
                    sf['loop'].data[-1] = resetMemberId(self.__cur_subtype, sf['loop'].data[-1])
                    memberId = '.'
                if isinstance(memberId, str) and isinstance(combinationId, int) and combinationId == 1:
                    sf['loop'].data[-1] = resetCombinationId(self.__cur_subtype, sf['loop'].data[-1])

        finally:
            self.atomSelectionInComment.clear()

    # Enter a parse tree produced by RosettaMRParser#number.
    def enterNumber(self, ctx: RosettaMRParser.NumberContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by RosettaMRParser#number.
    def exitNumber(self, ctx: RosettaMRParser.NumberContext):
        if ctx.Float():
            self.numberSelection.append(float(str(ctx.Float())))

        elif ctx.Integer():
            self.numberSelection.append(float(str(ctx.Integer())))

        else:
            self.numberSelection.append(None)

    # Enter a parse tree produced by RosettaMRParser#number_f.
    def enterNumber_f(self, ctx: RosettaMRParser.Number_fContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by RosettaMRParser#number_f.
    def exitNumber_f(self, ctx: RosettaMRParser.Number_fContext):
        if ctx.Float():
            self.numberFSelection.append(float(str(ctx.Float())))

        elif ctx.Integer():
            self.numberFSelection.append(float(str(ctx.Integer())))

        else:
            self.numberFSelection.append(None)

    def getNumber_f(self, ctx: RosettaMRParser.Number_fContext):  # pylint: disable=no-self-use
        if ctx is None:
            return None

        if ctx.Float():
            return float(str(ctx.Float()))

        if ctx.Integer():
            return float(str(ctx.Integer()))

        return None

    def __getCurrentRestraint(self) -> str:
        if self.__cur_subtype == 'dist':
            return f"[Check the {self.distRestraints}th row of distance restraints, {self.__def_err_sf_framecode}] "
        if self.__cur_subtype == 'ang':
            return f"[Check the {self.angRestraints}th row of angle restraints, {self.__def_err_sf_framecode}] "
        if self.__cur_subtype == 'dihed':
            return f"[Check the {self.dihedRestraints}th row of dihedral angle restraints, {self.__def_err_sf_framecode}] "
        if self.__cur_subtype == 'rdc':
            return f"[Check the {self.rdcRestraints}th row of residual dipolar coupling restraints, {self.__def_err_sf_framecode}] "
        if self.__cur_subtype == 'geo':
            return f"[Check the {self.geoRestraints}th row of coordinate geometry restraints, {self.__def_err_sf_framecode}] "
        if self.__cur_subtype == 'ssbond':
            return f"[Check the {self.ssbondRestraints}th row of disulfide bond restraints, {self.__def_err_sf_framecode}] "
        return ''

    def __setLocalSeqScheme(self):
        if 'local_seq_scheme' not in self.reasonsForReParsing:
            self.reasonsForReParsing['local_seq_scheme'] = {}
        preferAuthSeq = self.__authSeqId == 'auth_seq_id'
        if self.__cur_subtype == 'dist':
            self.reasonsForReParsing['local_seq_scheme'][(self.__cur_subtype, self.distRestraints)] = preferAuthSeq
        elif self.__cur_subtype == 'ang':
            self.reasonsForReParsing['local_seq_scheme'][(self.__cur_subtype, self.angRestraints)] = preferAuthSeq
        elif self.__cur_subtype == 'dihed':
            self.reasonsForReParsing['local_seq_scheme'][(self.__cur_subtype, self.dihedRestraints)] = preferAuthSeq
        elif self.__cur_subtype == 'rdc':
            self.reasonsForReParsing['local_seq_scheme'][(self.__cur_subtype, self.rdcRestraints)] = preferAuthSeq
        elif self.__cur_subtype == 'geo':
            self.reasonsForReParsing['local_seq_scheme'][(self.__cur_subtype, self.geoRestraints)] = preferAuthSeq
        elif self.__cur_subtype == 'ssbond':
            self.reasonsForReParsing['local_seq_scheme'][(self.__cur_subtype, self.ssbondRestraints)] = preferAuthSeq
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
            self.__authSeqId = 'label_seq_id'
            return
        if self.__cur_subtype == 'dist':
            key = (self.__cur_subtype, self.distRestraints)
        elif self.__cur_subtype == 'ang':
            key = (self.__cur_subtype, self.angRestraints)
        elif self.__cur_subtype == 'dihed':
            key = (self.__cur_subtype, self.dihedRestraints)
        elif self.__cur_subtype == 'rdc':
            key = (self.__cur_subtype, self.rdcRestraints)
        elif self.__cur_subtype == 'geo':
            key = (self.__cur_subtype, self.geoRestraints)
        elif self.__cur_subtype == 'ssbond':
            key = (self.__cur_subtype, self.ssbondRestraints)
        else:
            return

        if key in self.__reasons['local_seq_scheme']:
            self.__preferAuthSeq = self.__reasons['local_seq_scheme'][key]

    def __addSf(self, constraintType: Optional[str] = None, potentialType: Optional[str] = None,
                rdcCode: Optional[str] = None):
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

        sf_framecode = 'ROSETTA_' + restraint_name.replace(' ', '_') + f'_{list_id}'

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
                rdcCode: Optional[str] = None) -> dict:
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
                self.__addSf(constraintType=constraintType, potentialType=potentialType, rdcCode=rdcCode)

        self.__cur_constraint_type = constraintType

        _key = next((_key for _key in self.sfDict if _key[0] == 'dist' and _key[1] is None), key) if self.__cur_subtype == 'dist' else key
        self.__def_err_sf_framecode = self.sfDict[_key][-1]['sf_framecode']

        return self.sfDict[key][-1]

    def getContentSubtype(self) -> dict:
        """ Return content subtype of ROSETTA MR file.
        """

        contentSubtype = {'dist_restraint': self.distRestraints,
                          'ang_restraint': self.angRestraints,
                          'dihed_restraint': self.dihedRestraints,
                          'rdc_restraint': self.rdcRestraints,
                          'geo_restraint': self.geoRestraints,
                          'ssbond_restraint': self.ssbondRestraints
                          }

        return {k: 1 for k, v in contentSubtype.items() if v > 0}

    def getEffectiveContentSubtype(self) -> dict:
        """ Return effective content subtype of ROSETTA MR file (excluding CS-ROSETTA).
        """

        contentSubtype = {'dist_restraint': self.distRestraints,
                          'ang_restraint': self.angRestraints,
                          'dihed_restraint': self.dihedRestraints
                          }

        return {k: 1 for k, v in contentSubtype.items() if v > 0}

    def hasAnyRestraints(self) -> bool:
        """ Return whether any restraint is parsed successfully.
        """

        if self.__createSfDict:
            if len(self.sfDict) == 0:
                return False
            for v in self.sfDict.values():
                for item in v:
                    if item['index_id'] > 0:
                        return True
            return False
        return len(self.getContentSubtype()) > 0

    def getPolymerSequence(self) -> Optional[List[dict]]:
        """ Return polymer sequence of ROSETTA MR file.
        """

        return None if self.__polySeqRst is None or len(self.__polySeqRst) == 0 else self.__polySeqRst

    def getSequenceAlignment(self) -> Optional[List[dict]]:
        """ Return sequence alignment between coordinates and ROSETTA MR.
        """

        return None if self.__seqAlign is None or len(self.__seqAlign) == 0 else self.__seqAlign

    def getChainAssignment(self) -> Optional[List[dict]]:
        """ Return chain assignment between coordinates and ROSETTA MR.
        """

        return None if self.__chainAssign is None or len(self.__chainAssign) == 0 else self.__chainAssign

    def getReasonsForReparsing(self) -> Optional[dict]:
        """ Return reasons for re-parsing ROSETTA MR file.
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

# del RosettaMRParser
