##
# File: CharmmMRParserListener.py
# Date: 21-Sep-2022
#
# Updates:
""" ParserLister class for CHARMM MR files.
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
import copy
import numpy
import collections

from antlr4 import ParseTreeListener
from rmsd.calculate_rmsd import (int_atom, ELEMENT_WEIGHTS)  # noqa: F401 pylint: disable=no-name-in-module, import-error
from operator import itemgetter
from typing import IO, List, Tuple, Optional

from wwpdb.utils.align.alignlib import PairwiseAlign  # pylint: disable=no-name-in-module

try:
    from wwpdb.utils.nmr.io.CifReader import (CifReader,
                                              SYMBOLS_ELEMENT)
    from wwpdb.utils.nmr.mr.CharmmMRParser import CharmmMRParser
    from wwpdb.utils.nmr.mr.ParserListenerUtil import (toRegEx,
                                                       toNefEx,
                                                       coordAssemblyChecker,
                                                       extendCoordChainsForExactNoes,
                                                       translateToStdResName,
                                                       translateToStdAtomName,
                                                       isIdenticalRestraint,
                                                       hasInterChainRestraint,
                                                       isAmbigAtomSelection,
                                                       getAltProtonIdInBondConstraint,
                                                       guessCompIdFromAtomId,
                                                       guessCompIdFromAtomIdWoLimit,
                                                       getTypeOfDihedralRestraint,
                                                       fixBackboneAtomsOfDihedralRestraint,
                                                       isLikePheOrTyr,
                                                       isCyclicPolymer,
                                                       getStructConnPtnr,
                                                       getWatsonCrickPtnr,
                                                       getRestraintName,
                                                       contentSubtypeOf,
                                                       incListIdCounter,
                                                       decListIdCounter,
                                                       getReadableFactor,
                                                       getSaveframe,
                                                       getLoop,
                                                       getRow,
                                                       getStarAtom,
                                                       resetCombinationId,
                                                       resetMemberId,
                                                       getDistConstraintType,
                                                       getPotentialType,
                                                       REPRESENTATIVE_MODEL_ID,
                                                       REPRESENTATIVE_ALT_ID,
                                                       MAX_PREF_LABEL_SCHEME_COUNT,
                                                       MIN_EXT_SEQ_FOR_ATOM_SEL_ERR,
                                                       THRESHHOLD_FOR_CIRCULAR_SHIFT,
                                                       PLANE_LIKE_LOWER_LIMIT,
                                                       PLANE_LIKE_UPPER_LIMIT,
                                                       DIST_RESTRAINT_RANGE,
                                                       DIST_RESTRAINT_ERROR,
                                                       ANGLE_RESTRAINT_RANGE,
                                                       ANGLE_RESTRAINT_ERROR,
                                                       DIST_AMBIG_LOW,
                                                       DIST_AMBIG_UP,
                                                       DIST_AMBIG_MED,
                                                       DIST_AMBIG_UNCERT,
                                                       CARTN_DATA_ITEMS,
                                                       AUTH_ATOM_DATA_ITEMS,
                                                       ATOM_NAME_DATA_ITEMS,
                                                       AUTH_ATOM_CARTN_DATA_ITEMS,
                                                       PTNR1_AUTH_ATOM_DATA_ITEMS,
                                                       PTNR2_AUTH_ATOM_DATA_ITEMS)
    from wwpdb.utils.nmr.ChemCompUtil import ChemCompUtil
    from wwpdb.utils.nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from wwpdb.utils.nmr.nef.NEFTranslator import (NEFTranslator,
                                                   PARAMAGNETIC_ELEMENTS)
    from wwpdb.utils.nmr.AlignUtil import (LEN_LARGE_ASYM_ID,
                                           LARGE_ASYM_ID,
                                           monDict3,
                                           emptyValue,
                                           protonBeginCode,
                                           pseProBeginCode,
                                           aminoProtonCode,
                                           carboxylCode,
                                           jcoupBbPairCode,
                                           zincIonCode,
                                           calciumIonCode,
                                           updatePolySeqRst,
                                           updatePolySeqRstAmbig,
                                           mergePolySeqRstAmbig,
                                           sortPolySeqRst,
                                           updateSeqAtmRst,
                                           alignPolymerSequence,
                                           assignPolymerSequence,
                                           trimSequenceAlignment,
                                           retrieveAtomIdentFromMRMap,
                                           retrieveAtomIdFromMRMap,
                                           retrieveRemappedSeqId,
                                           splitPolySeqRstForMultimers,
                                           splitPolySeqRstForExactNoes,
                                           retrieveRemappedChainId,
                                           splitPolySeqRstForNonPoly,
                                           retrieveRemappedNonPoly,
                                           splitPolySeqRstForBranched,
                                           retrieveOriginalSeqIdFromMRMap)
    from wwpdb.utils.nmr.CifToNmrStar import (get_first_sf_tag,
                                              set_sf_tag)
    from wwpdb.utils.nmr.NmrVrptUtility import (to_np_array,
                                                distance,
                                                dist_error,
                                                angle_target_values,
                                                dihedral_angle,
                                                angle_error)
except ImportError:
    from nmr.io.CifReader import (CifReader,
                                  SYMBOLS_ELEMENT)
    from nmr.mr.CharmmMRParser import CharmmMRParser
    from nmr.mr.ParserListenerUtil import (toRegEx,
                                           toNefEx,
                                           coordAssemblyChecker,
                                           extendCoordChainsForExactNoes,
                                           translateToStdResName,
                                           translateToStdAtomName,
                                           isIdenticalRestraint,
                                           hasInterChainRestraint,
                                           isAmbigAtomSelection,
                                           getAltProtonIdInBondConstraint,
                                           guessCompIdFromAtomId,
                                           guessCompIdFromAtomIdWoLimit,
                                           getTypeOfDihedralRestraint,
                                           fixBackboneAtomsOfDihedralRestraint,
                                           isLikePheOrTyr,
                                           getRestraintName,
                                           isCyclicPolymer,
                                           getStructConnPtnr,
                                           getWatsonCrickPtnr,
                                           contentSubtypeOf,
                                           incListIdCounter,
                                           decListIdCounter,
                                           getReadableFactor,
                                           getSaveframe,
                                           getLoop,
                                           getRow,
                                           getStarAtom,
                                           resetCombinationId,
                                           resetMemberId,
                                           getDistConstraintType,
                                           getPotentialType,
                                           REPRESENTATIVE_MODEL_ID,
                                           REPRESENTATIVE_ALT_ID,
                                           MAX_PREF_LABEL_SCHEME_COUNT,
                                           MIN_EXT_SEQ_FOR_ATOM_SEL_ERR,
                                           THRESHHOLD_FOR_CIRCULAR_SHIFT,
                                           PLANE_LIKE_LOWER_LIMIT,
                                           PLANE_LIKE_UPPER_LIMIT,
                                           DIST_RESTRAINT_RANGE,
                                           DIST_RESTRAINT_ERROR,
                                           ANGLE_RESTRAINT_RANGE,
                                           ANGLE_RESTRAINT_ERROR,
                                           DIST_AMBIG_LOW,
                                           DIST_AMBIG_UP,
                                           DIST_AMBIG_MED,
                                           DIST_AMBIG_UNCERT,
                                           CARTN_DATA_ITEMS,
                                           AUTH_ATOM_DATA_ITEMS,
                                           ATOM_NAME_DATA_ITEMS,
                                           AUTH_ATOM_CARTN_DATA_ITEMS,
                                           PTNR1_AUTH_ATOM_DATA_ITEMS,
                                           PTNR2_AUTH_ATOM_DATA_ITEMS)
    from nmr.ChemCompUtil import ChemCompUtil
    from nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from nmr.nef.NEFTranslator import (NEFTranslator,
                                       PARAMAGNETIC_ELEMENTS)
    from nmr.AlignUtil import (LEN_LARGE_ASYM_ID,
                               LARGE_ASYM_ID,
                               monDict3,
                               emptyValue,
                               protonBeginCode,
                               pseProBeginCode,
                               aminoProtonCode,
                               carboxylCode,
                               jcoupBbPairCode,
                               zincIonCode,
                               calciumIonCode,
                               updatePolySeqRst,
                               updatePolySeqRstAmbig,
                               mergePolySeqRstAmbig,
                               sortPolySeqRst,
                               updateSeqAtmRst,
                               alignPolymerSequence,
                               assignPolymerSequence,
                               trimSequenceAlignment,
                               retrieveAtomIdentFromMRMap,
                               retrieveAtomIdFromMRMap,
                               retrieveRemappedSeqId,
                               splitPolySeqRstForMultimers,
                               splitPolySeqRstForExactNoes,
                               retrieveRemappedChainId,
                               splitPolySeqRstForNonPoly,
                               retrieveRemappedNonPoly,
                               splitPolySeqRstForBranched,
                               retrieveOriginalSeqIdFromMRMap)
    from nmr.CifToNmrStar import (get_first_sf_tag,
                                  set_sf_tag)
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


# This class defines a complete listener for a parse tree produced by CharmmMRParser.
class CharmmMRParserListener(ParseTreeListener):

    __file_type = 'nm-res-cha'

    __verbose = None
    __lfh = None
    __debug = False
    __internal = False
    __sel_expr_debug = False

    __nmr_vs_model = None

    __createSfDict = False
    __omitDistLimitOutlier = True
    __allowZeroUpperLimit = False
    __correctCircularShift = True

    # @see: https://bmrb.io/ref_info/atom_nom.tbl
    # @see: https://bmrb.io/macro/files/xplor_to_iupac.Nov140620
    # whether to trust the ref_info or the macro for atom nomenclature of ASN/GLN amino group
    __trust_bmrb_ref_info = True

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

    # CharmmCRDParserListener.getAtomNumberDict()
    __atomNumberDict = None

    # reasons for re-parsing request from the previous trial
    __reasons = None

    # CIF reader
    __cR = None
    __hasCoord = False

    # experimental method
    __exptlMethod = ''
    # whether solid-state NMR is applied to symmetric samples such as fibrils
    __symmetric = 'no'

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
    __atomIdSetPerChain = None

    __offsetHolder = None
    __effSeqIdSet = None

    __representativeModelId = REPRESENTATIVE_MODEL_ID
    __representativeAltId = REPRESENTATIVE_ALT_ID
    __hasPolySeq = False
    __hasNonPoly = False
    __hasBranched = False
    __hasNonPolySeq = False
    __preferAuthSeq = True
    __gapInAuthSeq = False
    __extendAuthSeq = False
    __complexSeqScheme = False

    __entityAssembly = None
    __polyPeptide = False
    __polyDeoxyribonucleotide = False
    __polyRibonucleotide = False

    __uniqAtomIdToSeqKey = None

    # large model
    __largeModel = False
    __representativeAsymId = 'A'

    # polymer sequence of MR file
    __polySeqRst = None
    __polySeqRstValid = None
    __polySeqRstFailed = None
    __polySeqRstFailedAmbig = None
    __seqAtmRstFailed = None

    __seqAlign = None
    __chainAssign = None

    # current restraint subtype
    __cur_subtype = ''
    __cur_subtype_altered = False
    __cur_auth_atom_id = ''

    # last comment
    lastComment = None

    # vector statement
    __cur_vector_mode = ''
    __cur_vector_atom_prop_type = ''

    # evaluate statement
    __cur_symbol_name = ''
    __cur_vflc_op_code = ''

    # union expression
    __cur_union_expr = False
    __con_union_expr = False
    __top_union_expr = False

    depth = 0

    stackSelections = None  # stack of selection
    stackTerms = None  # stack of term
    stackFactors = None  # stack of factor
    stackVflc = None  # stack of Vflc

    factor = None
    unionFactor = None

    # distance
    noeAverage = 'r-6'
    squareExponent = 1.0
    rSwitch = None
    scale = 1.0
    kMin = 0.0
    kMax = 0.0
    rMin = 0.0
    rMax = None
    fMax = None
    # tCon = 0.0
    rExp = -1.0 / 6.0

    # dihedral angle
    force = None
    min = None
    width = None
    period = 0

    # generic statements
    classification = None
    coefficients = None

    # collection of atom selection
    atomSelectionSet = []

    # collection of number selection
    numberSelection = []

    # collection of number selection in factor
    numberFSelection = []

    # evaluate
    evaluate = {}

    __f = __g = None
    warningMessage = None

    # record failed chain id for segment_id assignment
    __failure_chain_ids = []

    reasonsForReParsing = {}

    __cachedDictForAtomIdList = {}
    __cachedDictForFactor = {}

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

    # last edited pynmrstar saveframe
    __lastSfDict = {}

    def __init__(self, verbose: bool = True, log: IO = sys.stdout,
                 representativeModelId: int = REPRESENTATIVE_MODEL_ID,
                 representativeAltId: str = REPRESENTATIVE_ALT_ID,
                 mrAtomNameMapping: Optional[List[dict]] = None,
                 cR: Optional[CifReader] = None, caC: Optional[dict] = None, ccU: Optional[ChemCompUtil] = None,
                 csStat: Optional[BMRBChemShiftStat] = None, nefT: Optional[NEFTranslator] = None,
                 atomNumberDict: Optional[dict] = None, reasons: Optional[dict] = None):
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
            self.__entityAssembly = ret['entity_assembly']

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

        self.__atomIdSetPerChain = {}
        if self.__hasCoord and len(self.__polySeq) > 1:  # 7d3v
            for ps in self.__polySeq:
                chainId = ps['auth_chain_id']
                if chainId not in self.__atomIdSetPerChain:
                    self.__atomIdSetPerChain[chainId] = set()
            if self.__hasNonPoly:
                for np in self.__nonPoly:
                    chainId = np['auth_chain_id']
                    if chainId not in self.__atomIdSetPerChain:
                        self.__atomIdSetPerChain[chainId] = set()
            if self.__hasBranched:
                for br in self.__branched:
                    chainId = br['auth_chain_id']
                    if chainId not in self.__atomIdSetPerChain:
                        self.__atomIdSetPerChain[chainId] = set()
            for k, v in self.__coordAtomSite.items():
                self.__atomIdSetPerChain[k[0]] |= set(v['atom_id'])

        if self.__hasPolySeq:
            self.__gapInAuthSeq = any(ps for ps in self.__polySeq if 'gap_in_auth_seq' in ps and ps['gap_in_auth_seq'])

            self.__complexSeqScheme = False
            if len(self.__polySeq) > 1 and not all('identical_chain_id' in ps for ps in self.__polySeq):
                self.__complexSeqScheme = True
                for ps in self.__polySeq:
                    if ps['auth_seq_id'][0] == ps['seq_id'] or ps['auth_seq_id'][-1] == ps['seq_id'][-1]\
                       or ('gap_in_auth_seq' in ps and ps['gap_in_auth_seq']):  # 2kyg
                        self.__complexSeqScheme = False
                        break

            for entity in self.__entityAssembly:
                if 'entity_poly_type' in entity:
                    poly_type = entity['entity_poly_type']
                    if poly_type.startswith('polypeptide'):
                        self.__polyPeptide = True
                    elif poly_type == 'polydeoxyribonucleotide':
                        self.__polyDeoxyribonucleotide = True
                    elif poly_type == 'polyribonucleotide':
                        self.__polyRibonucleotide = True

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

        self.__largeModel = self.__hasPolySeq and len(self.__polySeq) > LEN_LARGE_ASYM_ID
        if self.__largeModel:
            self.__representativeAsymId = next(c for c in LARGE_ASYM_ID if any(ps for ps in self.__polySeq if ps['auth_chain_id'] == c))

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

        if self.__altPolySeq is not None:
            self.__effSeqIdSet = set()
            for ps in self.__polySeq:
                self.__effSeqIdSet |= set(ps['auth_seq_id'])
                self.__effSeqIdSet |= set(ps['seq_id'])
            if self.__hasNonPolySeq:
                for np in self.__nonPolySeq:
                    self.__effSeqIdSet |= set(np['auth_seq_id'])
                    self.__effSeqIdSet |= set(np['seq_id'])

        # reasons for re-parsing request from the previous trial
        self.__reasons = reasons
        self.__preferLabelSeqCount = 0

        self.reasonsForReParsing = {}  # reset to prevent interference from the previous run

        if atomNumberDict is not None:
            self.__atomNumberDict = atomNumberDict

        self.__cachedDictForAtomIdList = {}
        self.__cachedDictForFactor = {}

        self.distRestraints = 0      # CHARMM: Distance restraints
        self.dihedRestraints = 0     # CHARMM: Dihedral angle restraints
        self.geoRestraints = 0       # CHARMM: Harmonic coordinate/NCS restraints

        self.dist_comment_pat = re.compile('.*:'
                                           r'([A-Za-z]+)(\d+):(\S+)-'
                                           r'([A-Za-z]+)(\d+):(\S+).*')
        self.dist_comment_pat2 = re.compile('.*:'
                                            r'([A-Z]+):([A-Za-z]+)(\d+):(\S+)-'
                                            r'([A-Z]+):([A-Za-z]+)(\d+):(\S+).*')

        self.dihed_comment_pat = re.compile('.*:'
                                            r'([A-Za-z]+)(\d+):(\S+)-'
                                            r'([A-Za-z]+)(\d+):(\S+)-'
                                            r'([A-Za-z]+)(\d+):(\S+)-'
                                            r'([A-Za-z]+)(\d+):(\S+).*')

        self.sfDict = {}

    def setDebugMode(self, debug: bool):
        self.__debug = debug

    def setInternalMode(self, internal: bool):
        self.__internal = internal

    def setNmrChainAssignments(self, nmr_vs_model: Optional[List[dict]]):
        self.__nmr_vs_model = nmr_vs_model

    def createSfDict(self, createSfDict: bool):
        self.__createSfDict = createSfDict

    def setOriginaFileName(self, originalFileName: str):
        self.__originalFileName = originalFileName

    def setListIdCounter(self, listIdCounter: dict):
        self.__listIdCounter = listIdCounter

    def setEntryId(self, entryId: str):
        self.__entryId = entryId

    # Enter a parse tree produced by CharmmMRParser#charmm_mr.
    def enterCharmm_mr(self, ctx: CharmmMRParser.Charmm_mrContext):  # pylint: disable=unused-argument
        self.__polySeqRst = []
        self.__polySeqRstValid = []
        self.__polySeqRstFailed = []
        self.__polySeqRstFailedAmbig = []
        self.__seqAtmRstFailed = []
        self.__f = []
        self.__g = []

    # Exit a parse tree produced by CharmmMRParser#charmm_mr.
    def exitCharmm_mr(self, ctx: CharmmMRParser.Charmm_mrContext):  # pylint: disable=unused-argument

        def set_label_seq_scheme():
            if 'label_seq_scheme' not in self.reasonsForReParsing:
                self.reasonsForReParsing['label_seq_scheme'] = {}
            if self.distRestraints > 0:
                self.reasonsForReParsing['label_seq_scheme']['dist'] = True
            if self.dihedRestraints > 0:
                self.reasonsForReParsing['label_seq_scheme']['dihed'] = True
            if self.geoRestraints > 0:
                self.reasonsForReParsing['label_seq_scheme']['geo'] = True
            if 'local_seq_scheme' in self.reasonsForReParsing:
                del self.reasonsForReParsing['local_seq_scheme']

        def chain_id_remap_with_offset(trust_cur_chain_assign=True):
            refChainIds, ovwChainIds = [], []
            chainIdRemap = {}
            if trust_cur_chain_assign:
                for ca in self.__chainAssign:
                    if ca['conflict'] > 0:
                        continue
                    ref_chain_id = ca['ref_chain_id']
                    test_chain_id = ca['test_chain_id']

                    if ref_chain_id in refChainIds:
                        continue

                    sa = next((sa for sa in self.__seqAlign
                               if sa['ref_chain_id'] == ref_chain_id
                               and sa['test_chain_id'] == test_chain_id), None)

                    if sa is None:
                        continue

                    if any(seq_id in chainIdRemap for seq_id in sa['test_seq_id']):
                        continue

                    ps = next(ps for ps in self.__polySeq if ps['auth_chain_id'] == ref_chain_id)
                    has_gap_in_auth_seq = 'gap_in_auth_seq' in ps and ps['gap_in_auth_seq']

                    label_seq_scheme = False
                    _ps = next((_ps for _ps in self.__polySeqRstValid if _ps['chain_id'] == ref_chain_id), None)
                    if _ps is not None and all(seq_id in ps['seq_id'] for seq_id in _ps['seq_id']):
                        label_seq_scheme = True  # 2m3o

                    rev_seq_id_mapping = {}
                    if 'ref_auth_seq_id' in sa and sa['ref_auth_seq_id'] == sa['test_seq_id'] and not label_seq_scheme:
                        pass  # 6f0y
                    else:
                        for ref_seq_id, test_seq_id in zip(sa['ref_seq_id'], sa['test_seq_id']):
                            if test_seq_id is not None:
                                rev_seq_id_mapping[test_seq_id] = ref_seq_id

                    if has_gap_in_auth_seq:
                        for seq_id, auth_seq_id in zip(ps['seq_id'], ps['auth_seq_id']):
                            if auth_seq_id in emptyValue:
                                continue
                            if auth_seq_id in rev_seq_id_mapping:
                                test_seq_id = rev_seq_id_mapping[auth_seq_id]
                                chainIdRemap[test_seq_id] = {'chain_id': ref_chain_id, 'seq_id': auth_seq_id}
                            elif seq_id not in chainIdRemap:
                                chainIdRemap[seq_id] = {'chain_id': ref_chain_id, 'seq_id': auth_seq_id}
                    else:
                        for auth_seq_id in ps['auth_seq_id']:
                            if auth_seq_id in emptyValue:
                                continue
                            if auth_seq_id in rev_seq_id_mapping:
                                test_seq_id = rev_seq_id_mapping[auth_seq_id]
                                chainIdRemap[test_seq_id] = {'chain_id': ref_chain_id, 'seq_id': auth_seq_id}
                            elif auth_seq_id not in chainIdRemap:
                                chainIdRemap[auth_seq_id] = {'chain_id': ref_chain_id, 'seq_id': auth_seq_id}

                    refChainIds.append(ref_chain_id)

            score = {1: 8, 2: 6, 3: 4, 4: 2, 5: 1, 6: 1, 7: 1}

            for ps in self.__polySeq:
                chainId = ps['auth_chain_id']
                if chainId in refChainIds:
                    continue
                has_gap_in_auth_seq = 'gap_in_auth_seq' in ps and ps['gap_in_auth_seq']
                seq_id_name = 'seq_id' if has_gap_in_auth_seq else 'auth_seq_id'

                chainIds = [chainId]
                if 'identical_chain_id' in ps:
                    chainIds.extend(ps['identical_chain_id'])

                offsets = []
                if trust_cur_chain_assign:
                    for item in self.__polySeqRstFailed:
                        if item['chain_id'] in chainIds:
                            for seqId, compId in zip(item['seq_id'], item['comp_id']):
                                offsets.extend([_seqId - seqId for _seqId, _compId in zip(ps[seq_id_name], ps['comp_id']) if _compId == compId])
                    for item in self.__polySeqRstFailedAmbig:
                        if item['chain_id'] in chainIds:
                            for seqId, compIds in zip(item['seq_id'], item['comp_ids']):
                                offsets.extend([_seqId - seqId for _seqId, _compId in zip(ps[seq_id_name], ps['comp_id']) if _compId in compIds])

                if len(offsets) == 0:
                    # predict sequence offset purely from __seqAtmRstFailed (2l12)
                    for item in self.__seqAtmRstFailed:
                        if item['chain_id'] not in chainIds:
                            continue
                        for seqId, atomIds in zip(item['seq_id'], item['atom_id']):
                            if seqId in chainIdRemap:
                                continue
                            compIds = guessCompIdFromAtomIdWoLimit(atomIds, [ps], self.__nefT)
                            lenCompIds = len(compIds)
                            if lenCompIds < 5:
                                for _seqId, _compId in zip(ps[seq_id_name], ps['comp_id']):
                                    if _compId in compIds:
                                        offsets.extend([_seqId - seqId] * score[lenCompIds])
                            else:
                                for _seqId, _compId in zip(ps[seq_id_name], ps['comp_id']):
                                    if _compId in compIds:
                                        offsets.append(_seqId - seqId)

                    if len(offsets) == 0:
                        continue

                common_offsets = collections.Counter(offsets).most_common()
                offsets = [offset for offset, count in common_offsets if count == common_offsets[0][1]]

                item = next((item for item in self.__seqAtmRstFailed if item['chain_id'] in chainIds), None)
                if item is None:
                    continue

                _matched = 0
                _offsets = []
                for offset in offsets:
                    valid = True
                    matched = 0
                    for item in self.__seqAtmRstFailed:
                        if item['chain_id'] not in chainIds:
                            continue
                        for _seqId, _atomIds in zip(item['seq_id'], item['atom_id']):
                            if _seqId in chainIdRemap:
                                continue
                            _compIds = guessCompIdFromAtomIdWoLimit(_atomIds, [ps], self.__nefT)
                            if _seqId + offset in ps[seq_id_name]:
                                compId = ps['comp_id'][ps[seq_id_name].index(_seqId + offset)]
                                if compId in _compIds:
                                    matched += 1
                                elif compId not in monDict3 or len(_compIds) == 0:  # 6f0y
                                    continue
                                else:
                                    valid = False
                                    break
                            else:
                                matched -= 1
                    if valid:
                        if matched > _matched:
                            _matched = matched
                            _offsets = [offset]
                        elif matched == _matched:
                            _offsets.append(offset)

                if len(_offsets) == 1:
                    _offset = _offsets[0]

                elif len(_offsets) == 0 or len(offsets) > 4:  # 2ymj, 2js1
                    continue

                else:  # 2n3a
                    _matched = -10000
                    _offset = None
                    for offset in _offsets:
                        matched = 0
                        for item in self.__seqAtmRstFailed:
                            if item['chain_id'] not in chainIds:
                                continue
                            for _seqId, _atomIds in zip(item['seq_id'], item['atom_id']):
                                _compIds = guessCompIdFromAtomIdWoLimit(_atomIds, [ps], self.__nefT)
                                if _seqId + offset in ps[seq_id_name]:
                                    idx = ps[seq_id_name].index(_seqId + offset)
                                    compId = ps['comp_id'][idx]
                                    if compId in _compIds:
                                        matched += 100
                                        if all(abs(offset_) > 950 for offset_ in _offsets):  # 6e5n
                                            matched -= abs((offset % 100) - 100) % 100
                                        elif ps['auth_seq_id'][idx] not in emptyValue:
                                            matched -= abs(offset - (ps['auth_seq_id'][idx] - ps['seq_id'][idx]))
                                else:
                                    matched -= 100
                            if matched > _matched:
                                _matched, _offset = matched, offset
                    if _offset is None:
                        _offset = _offsets[0]

                if has_gap_in_auth_seq:

                    if len(refChainIds) == 0:  # 2kny
                        continue

                    for seq_id, auth_seq_id in zip(ps['seq_id'], ps['auth_seq_id']):
                        if auth_seq_id in emptyValue:
                            continue
                        if seq_id - _offset in chainIdRemap:
                            _chainId = chainIdRemap[seq_id - _offset]['chain_id']
                            if _chainId not in ovwChainIds:
                                ovwChainIds.append(_chainId)
                        chainIdRemap[seq_id - _offset] = {'chain_id': chainId, 'seq_id': auth_seq_id}
                else:
                    for auth_seq_id in ps['auth_seq_id']:
                        if auth_seq_id in emptyValue:
                            continue
                        if auth_seq_id - _offset in chainIdRemap:
                            _chainId = chainIdRemap[auth_seq_id - _offset]['chain_id']
                            if _chainId not in ovwChainIds:
                                ovwChainIds.append(_chainId)
                        chainIdRemap[auth_seq_id - _offset] = {'chain_id': chainId, 'seq_id': auth_seq_id}

                if 'label_seq_offset' in self.reasonsForReParsing:
                    del self.reasonsForReParsing['label_seq_offset']
                if 'local_seq_scheme' in self.reasonsForReParsing:
                    del self.reasonsForReParsing['local_seq_scheme']
                self.reasonsForReParsing['chain_id_remap'] = chainIdRemap

                if 'inhibit_label_seq_scheme' in self.reasonsForReParsing:
                    if chainId in self.reasonsForReParsing['inhibit_label_seq_scheme']:
                        del self.reasonsForReParsing['inhibit_label_seq_scheme'][chainId]
                    if len(self.reasonsForReParsing['inhibit_label_seq_scheme']) == 0:
                        del self.reasonsForReParsing['inhibit_label_seq_scheme']

            # try to handle chain_id remapping conflicts (2knh)
            for chainId in ovwChainIds:
                ps = next(ps for ps in self.__polySeq if ps['auth_chain_id'] == chainId)
                has_gap_in_auth_seq = 'gap_in_auth_seq' in ps and ps['gap_in_auth_seq']
                seq_id_name = 'seq_id' if has_gap_in_auth_seq else 'auth_seq_id'

                offsets = []
                for item in self.__polySeqRstFailedAmbig:
                    if item['chain_id'] == chainId:
                        for seqId, compIds in zip(item['seq_id'], item['comp_ids']):
                            if seqId in chainIdRemap:
                                continue
                            offsets.extend([_seqId - seqId for _seqId, _compId in zip(ps[seq_id_name], ps['comp_id']) if _compId in compIds])

                if len(offsets) == 0:
                    continue

                common_offsets = collections.Counter(offsets).most_common()
                offsets = [offset for offset, count in common_offsets if count == common_offsets[0][1]]

                item = next((item for item in self.__seqAtmRstFailed if item['chain_id'] == chainId), None)
                if item is None:
                    continue

                _matched = 0
                _offset = None

                for item in self.__seqAtmRstFailed:
                    if item['chain_id'] != chainId:
                        continue
                    for offset in offsets:
                        valid = True
                        matched = 0
                        for _seqId, _atomIds in zip(item['seq_id'], item['atom_id']):
                            if _seqId in chainIdRemap:
                                continue
                            _compIds = guessCompIdFromAtomIdWoLimit(_atomIds, [ps], self.__nefT)
                            if _seqId + offset in ps[seq_id_name]:
                                if ps['comp_id'][ps[seq_id_name].index(_seqId + offset)] in _compIds:
                                    matched += 1
                                else:
                                    valid = False
                                    break
                        if valid:
                            if matched > _matched:
                                _matched, _offset = matched, offset

                if _offset is None:
                    continue

                if has_gap_in_auth_seq:
                    for seq_id, auth_seq_id in zip(ps['seq_id'], ps['auth_seq_id']):
                        if auth_seq_id in emptyValue:
                            continue
                        chainIdRemap[seq_id - _offset] = {'chain_id': chainId, 'seq_id': auth_seq_id}
                else:
                    for auth_seq_id in ps['auth_seq_id']:
                        if auth_seq_id in emptyValue:
                            continue
                        chainIdRemap[auth_seq_id - _offset] = {'chain_id': chainId, 'seq_id': auth_seq_id}

                self.reasonsForReParsing['chain_id_remap'] = chainIdRemap

                if 'inhibit_label_seq_scheme' in self.reasonsForReParsing:
                    if chainId in self.reasonsForReParsing['inhibit_label_seq_scheme']:
                        del self.reasonsForReParsing['inhibit_label_seq_scheme'][chainId]
                    if len(self.reasonsForReParsing['inhibit_label_seq_scheme']) == 0:
                        del self.reasonsForReParsing['inhibit_label_seq_scheme']

        def chain_id_split_with_offset(failed_seq_ids):
            refChainIds = []
            chainIdRemap = {}
            for ca in self.__chainAssign:
                if ca['conflict'] > 0:
                    continue
                ref_chain_id = ca['ref_chain_id']
                test_chain_id = ca['test_chain_id']

                if ref_chain_id in refChainIds:
                    continue

                sa = next((sa for sa in self.__seqAlign
                           if sa['ref_chain_id'] == ref_chain_id
                           and sa['test_chain_id'] == test_chain_id), None)

                if sa is None:
                    continue

                if any(seq_id in chainIdRemap for seq_id in sa['test_seq_id']):
                    continue

                ps = next(ps for ps in self.__polySeq if ps['auth_chain_id'] == ref_chain_id)
                has_gap_in_auth_seq = 'gap_in_auth_seq' in ps and ps['gap_in_auth_seq']

                label_seq_scheme = False
                _ps = next((_ps for _ps in self.__polySeqRstValid if _ps['chain_id'] == ref_chain_id), None)
                if _ps is not None and all(seq_id in ps['seq_id'] for seq_id in _ps['seq_id']):
                    label_seq_scheme = True  # 2m3o

                rev_seq_id_mapping = {}
                if 'ref_auth_seq_id' in sa and sa['ref_auth_seq_id'] == sa['test_seq_id'] and not label_seq_scheme:
                    pass  # 6f0y
                else:
                    for ref_seq_id, test_seq_id in zip(sa['ref_seq_id'], sa['test_seq_id']):
                        if test_seq_id is not None:
                            rev_seq_id_mapping[test_seq_id] = ref_seq_id

                if has_gap_in_auth_seq:
                    for seq_id, auth_seq_id in zip(ps['seq_id'], ps['auth_seq_id']):
                        if auth_seq_id in emptyValue:
                            continue
                        if auth_seq_id in rev_seq_id_mapping:
                            test_seq_id = rev_seq_id_mapping[auth_seq_id]
                            chainIdRemap[test_seq_id] = {'chain_id': ref_chain_id, 'seq_id': auth_seq_id}
                        elif seq_id not in chainIdRemap:
                            chainIdRemap[seq_id] = {'chain_id': ref_chain_id, 'seq_id': auth_seq_id}
                else:
                    for auth_seq_id in ps['auth_seq_id']:
                        if auth_seq_id in emptyValue:
                            continue
                        if auth_seq_id in rev_seq_id_mapping:
                            test_seq_id = rev_seq_id_mapping[auth_seq_id]
                            chainIdRemap[test_seq_id] = {'chain_id': ref_chain_id, 'seq_id': auth_seq_id}
                        elif auth_seq_id not in chainIdRemap:
                            chainIdRemap[auth_seq_id] = {'chain_id': ref_chain_id, 'seq_id': auth_seq_id}

                refChainIds.append(ref_chain_id)

            for ps in self.__polySeq:
                chainId = ps['auth_chain_id']
                if chainId in refChainIds:
                    continue

                has_gap_in_auth_seq = 'gap_in_auth_seq' in ps and ps['gap_in_auth_seq']
                seq_id_name = 'seq_id' if has_gap_in_auth_seq else 'auth_seq_id'

                len_seq_id = len(ps['seq_id'])

                src_seq_ids = failed_seq_ids[:len_seq_id]
                failed_seq_ids = failed_seq_ids[len_seq_id:]

                offset = ps[seq_id_name][0] - src_seq_ids[0]

                if has_gap_in_auth_seq:
                    for seq_id, auth_seq_id in zip(ps['seq_id'], ps['auth_seq_id']):
                        if auth_seq_id in emptyValue:
                            continue
                        chainIdRemap[seq_id - offset] = {'chain_id': chainId, 'seq_id': auth_seq_id}
                else:
                    for auth_seq_id in ps['auth_seq_id']:
                        if auth_seq_id in emptyValue:
                            continue
                        chainIdRemap[auth_seq_id - offset] = {'chain_id': chainId, 'seq_id': auth_seq_id}

                self.reasonsForReParsing['chain_id_remap'] = chainIdRemap

                if 'inhibit_label_seq_scheme' in self.reasonsForReParsing:
                    if chainId in self.reasonsForReParsing['inhibit_label_seq_scheme']:
                        del self.reasonsForReParsing['inhibit_label_seq_scheme'][chainId]
                    if len(self.reasonsForReParsing['inhibit_label_seq_scheme']) == 0:
                        del self.reasonsForReParsing['inhibit_label_seq_scheme']

            self.reasonsForReParsing['chain_id_remap'] = chainIdRemap

        try:

            pro_hn_atom_not_found_pattern = re.compile(r"^\[Atom not found\] \[Check the \d+th row of [^,]+s.*\] (\S+):(\d+):PRO:[Hh][Nn]? is not present in the coordinates\.$")
            pro_hn_anomalous_data_pattern = re.compile(r"^\[Anomalous data\] \[Check the \d+th row of [^,]+s.*\] (\S+):(\d+):PRO:[Hh][Nn]? is not present in the coordinates\.$")
            gly_hb_atom_not_found_pattern = re.compile(r"^\[Atom not found\] \[Check the \d+th row of [^,]+s.*\] (\S+):(\d+):GLY:[Hh][Bb]\S* is not present in the coordinates\.$")
            any_atom_not_found_pattern = re.compile(r"^\[Atom not found\] \[Check the \d+th row of [^,]+s.*\] (\S+):(\d+):\S+:(\S+) is not present in the coordinates\.$")
            pro_hn_atom_not_found_warnings = [f for f in self.__f if pro_hn_atom_not_found_pattern.match(f) or pro_hn_anomalous_data_pattern.match(f)]
            gly_hb_atom_not_found_warnings = [f for f in self.__f if gly_hb_atom_not_found_pattern.match(f)]
            any_atom_not_found_warnings = [f for f in self.__f if any_atom_not_found_pattern.match(f)]

            if 'segment_id_mismatch' in self.reasonsForReParsing\
               and (len(self.reasonsForReParsing['segment_id_mismatch']) == 0
                    or (len(self.reasonsForReParsing['segment_id_mismatch']) < len(self.__atomIdSetPerChain)
                        and all(all(score < 0 for score in stat.values()) and len(set(stat.values())) == 1
                                for stat in self.reasonsForReParsing['segment_id_match_stats'].values()))):  # 2lzs
                del self.reasonsForReParsing['segment_id_mismatch']
                del self.reasonsForReParsing['segment_id_match_stats']
                del self.reasonsForReParsing['segment_id_poly_type_stats']

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

                        chain_id_mapping = {}

                        for ca in self.__chainAssign:
                            ref_chain_id = ca['ref_chain_id']
                            test_chain_id = ca['test_chain_id']

                            if ref_chain_id != test_chain_id:
                                chain_id_mapping[test_chain_id] = ref_chain_id

                        if len(chain_id_mapping) == len(self.__polySeq):

                            if not any('identical_chain_id' in ps for ps in self.__polySeq if ps['auth_chain_id'] in chain_id_mapping):
                                for ps in self.__polySeqRst:
                                    if ps['chain_id'] in chain_id_mapping:
                                        ps['chain_id'] = chain_id_mapping[ps['chain_id']]

                                self.__seqAlign, _ = alignPolymerSequence(self.__pA, self.__polySeq, self.__polySeqRst,
                                                                          resolvedMultimer=self.__reasons is not None)
                                self.__chainAssign, _ = assignPolymerSequence(self.__pA, self.__ccU, self.__file_type, self.__polySeq, self.__polySeqRst, self.__seqAlign)

                            elif len(self.__chainAssign) > len(self.__polySeqRst) and len(self.__polySeqRstFailed) > 0:
                                mergePolySeqRstAmbig(self.__polySeqRstFailed, self.__polySeqRstFailedAmbig)
                                sortPolySeqRst(self.__polySeqRstFailed)

                                overlap = False
                                for _ps in self.__polySeqRstFailed:
                                    ps = next((ps for ps in self.__polySeqRst if ps['chain_id'] == _ps['chain_id']), None)
                                    if ps is not None and any(_seq_id in ps['seq_id'] for _seq_id in _ps['seq_id']):
                                        overlap = True
                                        break

                                if not overlap:  # 2lfr
                                    seqAlignFailed, _ = alignPolymerSequence(self.__pA, self.__polySeq, self.__polySeqRstFailed)

                                    if all(sa['matched'] > 0 and sa['conflict'] == 0 for sa in seqAlignFailed):
                                        chain_id_remap_with_offset()  # 2l01

                    elif len(self.__polySeq) > len(self.__polySeqRst) > 0 and all('identical_chain_id' in ps for ps in self.__polySeq):

                        chain_id_mapping = {}

                        for ca in self.__chainAssign:
                            ref_chain_id = ca['ref_chain_id']
                            test_chain_id = ca['test_chain_id']

                            if ref_chain_id != test_chain_id:
                                chain_id_mapping[test_chain_id] = ref_chain_id

                        if len(chain_id_mapping) == len(self.__polySeqRst) and len(self.__chainAssign) > len(self.__polySeqRst):
                            if len(self.__polySeqRstFailed) > 0:
                                mergePolySeqRstAmbig(self.__polySeqRstFailed, self.__polySeqRstFailedAmbig)
                                sortPolySeqRst(self.__polySeqRstFailed)

                                overlap = False
                                for _ps in self.__polySeqRstFailed:
                                    ps = next((ps for ps in self.__polySeqRst if ps['chain_id'] == _ps['chain_id']), None)
                                    if ps is not None and any(_seq_id in ps['seq_id'] for _seq_id in _ps['seq_id']):
                                        overlap = True
                                        break

                                if not overlap:  # 2lfr
                                    seqAlignFailed, _ = alignPolymerSequence(self.__pA, self.__polySeq, self.__polySeqRstFailed)

                                    if all(sa['matched'] > 0 and sa['conflict'] == 0 for sa in seqAlignFailed):
                                        chain_id_remap_with_offset()

                            elif len(self.__seqAtmRstFailed) > 0:
                                chain_id_remap_with_offset()  # 2n9b

                    trimSequenceAlignment(self.__seqAlign, self.__chainAssign)

                    if self.__reasons is None\
                       and any(f for f in self.__f if '[Anomalous data]' in f)\
                       and 'segment_id_mismatch' not in self.reasonsForReParsing\
                       and (self.distRestraints > 0 or len(self.__polySeq) == 1 or all('identical_chain_id' in ps for ps in self.__polySeq)):
                        set_label_seq_scheme()

                    if self.__reasons is None\
                       and (any(f for f in self.__f if '[Atom not found]' in f or '[Anomalous data]' in f or '[Sequence mismatch]' in f)
                            or any(f for f in self.__f if '[Insufficient atom selection]' in f)):

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

                            # extend restraint polymer sequence from single match (2joa)
                            if len(seqAlignFailed) == 0 and len(self.__polySeqRstFailed) > 0 and len(self.__polySeqRstFailedAmbig) > 0:
                                for ps in self.__polySeqRstFailed:
                                    chainId = ps['chain_id']
                                    _ps = next((_ps for _ps in self.__polySeqRstFailedAmbig if _ps['chain_id'] == chainId), None)
                                    if _ps is None:
                                        continue
                                    _matched = 0
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

                                seqAlignValid = None
                                if len(self.__polySeqRstValid) > 0:
                                    sortPolySeqRst(self.__polySeqRstValid)
                                    seqAlignValid, _ = alignPolymerSequence(self.__pA, self.__polySeq, self.__polySeqRstValid)

                                if seqAlignValid is not None and len(seqAlignValid) == 0 and len(seqAlignFailed) == 0:
                                    if 'local_seq_scheme' in self.reasonsForReParsing:
                                        del self.reasonsForReParsing['local_seq_scheme']
                                    if 'label_seq_scheme' in self.reasonsForReParsing:
                                        del self.reasonsForReParsing['label_seq_scheme']
                                    if len(pro_hn_atom_not_found_warnings) + len(gly_hb_atom_not_found_warnings) > 0:
                                        self.__seqAtmRstFailed = []
                                        for f in any_atom_not_found_warnings:
                                            g = any_atom_not_found_pattern.search(f).groups()
                                            updateSeqAtmRst(self.__seqAtmRstFailed, g[0], int(g[1]), [g[2]])
                                        chain_id_remap_with_offset(False)  # 5xs1

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

                                    ref_seq_id_mapping = {}
                                    if seqAlignValid is not None:
                                        sa_ref = next((sa for sa in seqAlignValid
                                                       if sa['ref_chain_id'] == ref_chain_id
                                                       and sa['test_chain_id'] == test_chain_id), None)

                                        if sa_ref is not None:
                                            for ref_auth_seq_id, mid_code, test_seq_id in zip(sa_ref['ref_auth_seq_id'] if 'ref_auth_seq_id' in sa_ref else sa_ref['ref_seq_id'],
                                                                                              sa_ref['mid_code'], sa_ref['test_seq_id']):
                                                if mid_code == '|' and test_seq_id is not None:
                                                    ref_seq_id_mapping[test_seq_id] = ref_auth_seq_id

                                    if len(seq_id_mapping) > 1:
                                        for k, v in seq_id_mapping.items():
                                            offset = v - k
                                            break

                                        if len(ref_seq_id_mapping) > 1:
                                            for k, v in ref_seq_id_mapping.items():
                                                ref_offset = v - k
                                                break

                                            if offset != ref_offset:
                                                continue

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

                                if len(chainAssignFailed) == 0\
                                   or (len(self.__polySeq) == 1 and 'label_seq_scheme' not in self.reasonsForReParsing
                                       and 'gap_in_auth_seq' in self.__polySeq[0] and self.__polySeq[0]['gap_in_auth_seq']):  # 6mv3
                                    valid_auth_seq = valid_label_seq = True
                                    for _ps in self.__polySeqRstFailed:
                                        test_chain_id = _ps['chain_id']
                                        try:
                                            ps = next(ps for ps in self.__polySeq if ps['auth_chain_id'] == test_chain_id)
                                            for test_seq_id, test_comp_id in zip(_ps['seq_id'], _ps['comp_id']):
                                                if test_seq_id not in ps['seq_id']:
                                                    valid_label_seq = False
                                                elif test_comp_id not in emptyValue and test_comp_id != ps['comp_id'][ps['seq_id'].index(test_seq_id)]:
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
                                    else:
                                        chain_id_remap_with_offset()

                                elif len(self.__chainAssign) > 0 and len(self.__polySeqRstFailed) == 1 and len(self.__seqAtmRstFailed) > 0\
                                        and all('identical_chain_id' in ps for ps in self.__polySeq)\
                                        and 'global_auth_sequence_offset' in self.reasonsForReParsing\
                                        and len(set(self.reasonsForReParsing['global_auth_sequence_offset'].values())) == 1:
                                    if len(self.__polySeqRstFailed[0]['seq_id']) == len(self.__polySeq[0]['seq_id']) * (len(self.__polySeq) - 1):
                                        chain_id_split_with_offset(self.__polySeqRstFailed[0]['seq_id'])  # 6ge1

                        elif len(self.__seqAtmRstFailed) > 0\
                                and 'label_seq_scheme' not in self.reasonsForReParsing\
                                and 'label_seq_offset' in self.reasonsForReParsing:
                            chainIdRemap = {}
                            valid = True
                            for item in self.__seqAtmRstFailed:
                                chainId = item['chain_id']
                                ps = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == chainId), None)
                                if ps is None:
                                    continue
                                if chainId in self.reasonsForReParsing['label_seq_offset']:
                                    for auth_seq_id in ps['auth_seq_id']:
                                        if auth_seq_id in chainIdRemap:
                                            valid = False
                                            break
                                        chainIdRemap[auth_seq_id] = {'chain_id': chainId, 'seq_id': auth_seq_id}
                                    if len(pro_hn_atom_not_found_warnings) + len(gly_hb_atom_not_found_warnings) == 0:
                                        continue
                                if all(seqId in ps['seq_id'] and seqId not in ps['auth_seq_id'] for seqId in item['seq_id']):
                                    for seqId, atoms in zip(item['seq_id'], item['atom_id']):
                                        compId = ps['comp_id'][ps['seq_id'].index(seqId)]
                                        for atom in atoms:
                                            _, _, details = self.__nefT.get_valid_star_atom_in_xplor(compId, atom, leave_unmatched=True)
                                            if details is not None:
                                                valid = False
                                                break
                                    if valid:
                                        for seq_id, auth_seq_id in zip(ps['seq_id'], ps['auth_seq_id']):
                                            if seq_id in chainIdRemap:
                                                valid = False
                                                break
                                            chainIdRemap[seq_id] = {'chain_id': chainId, 'seq_id': auth_seq_id}
                            if valid:
                                del self.reasonsForReParsing['label_seq_offset']
                                if 'local_seq_scheme' in self.reasonsForReParsing:
                                    del self.reasonsForReParsing['local_seq_scheme']
                                self.reasonsForReParsing['chain_id_remap'] = chainIdRemap

                        # try to find valid sequence offset from failed ambiguous assignments (2js1)
                        elif len(self.__chainAssign) > 0 and len(self.__seqAtmRstFailed) > 0\
                                and len(self.__polySeq) > 1:  # 2n3a, 6e5n
                            # and 'local_seq_scheme' in self.reasonsForReParsing:  # and 'label_seq_scheme' in self.reasonsForReParsing: (2lxs)
                            chain_id_remap_with_offset()

                    # DAOTHER-9063
                    if self.__reasons is None and 'np_seq_id_remap' in self.reasonsForReParsing:

                        seqIdRemap = []

                        for test_chain_id, np_seq_id_mapping in self.reasonsForReParsing['np_seq_id_remap'].items():
                            _np_seq_id_mapping = {k: v for k, v in np_seq_id_mapping.items() if v is not None}
                            if len(_np_seq_id_mapping) == 0:
                                continue
                            _np_seq_id_mapping_ = {v: k for k, v in np_seq_id_mapping.items() if v is not None}
                            if len(_np_seq_id_mapping) != len(_np_seq_id_mapping_):
                                continue
                            seqIdRemap.append({'chain_id': test_chain_id, 'seq_id_dict': _np_seq_id_mapping})

                        if len(seqIdRemap) == 0:
                            del self.reasonsForReParsing['np_seq_id_remap']
                        else:
                            self.reasonsForReParsing['np_seq_id_remap'] = seqIdRemap

                    # attempt to resolve case where there is no valid restraint, but only insufficient atom selection errors
                    # due to arbitrary shift of sequence number that does not match with any coordinate sequence schemes (2lzs)
                    mergePolySeqRstAmbig(self.__polySeqRstFailed, self.__polySeqRstFailedAmbig)
                    if self.__reasons is None and len(self.__polySeqRst) == 0 and len(self.__polySeqRstFailed) > 0\
                       and any(f for f in self.__f if '[Insufficient atom selection]' in f):
                        sortPolySeqRst(self.__polySeqRstFailed)

                        seqAlignFailed, _ = alignPolymerSequence(self.__pA, self.__polySeq, self.__polySeqRstFailed)

                        # extend restraint polymer sequence from single match (2joa)
                        if len(seqAlignFailed) == 0 and len(self.__polySeqRstFailed) > 0 and len(self.__polySeqRstFailedAmbig) > 0:
                            for ps in self.__polySeqRstFailed:
                                chainId = ps['chain_id']
                                _ps = next((_ps for _ps in self.__polySeqRstFailedAmbig if _ps['chain_id'] == chainId), None)
                                if _ps is None:
                                    continue
                                _matched = 0
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

                            seqIdRemap = []

                            cyclicPolymer = {}

                            for ca in chainAssignFailed:
                                ref_chain_id = ca['ref_chain_id']
                                test_chain_id = ca['test_chain_id']

                                sa = next(sa for sa in seqAlignFailed
                                          if sa['ref_chain_id'] == ref_chain_id
                                          and sa['test_chain_id'] == test_chain_id)

                                poly_seq_model = next(ps for ps in self.__polySeq
                                                      if ps['auth_chain_id'] == ref_chain_id)
                                poly_seq_rst = next(ps for ps in self.__polySeqRstFailed
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

                            if len(seqIdRemap) > 0:
                                if 'seq_id_remap' not in self.reasonsForReParsing:
                                    self.reasonsForReParsing['seq_id_remap'] = seqIdRemap

                            if any(ps for ps in self.__polySeq if 'identical_chain_id' in ps):
                                polySeqRst, chainIdMapping = splitPolySeqRstForMultimers(self.__pA, self.__polySeq, self.__polySeqRstFailed, chainAssignFailed)

                                if polySeqRst is not None and (not self.__hasNonPoly or len(self.__polySeq) // len(self.__nonPoly) in (1, 2)):
                                    self.__polySeqRst = polySeqRst
                                    if 'chain_id_remap' not in self.reasonsForReParsing:
                                        self.reasonsForReParsing['chain_id_remap'] = chainIdMapping

                            if len(self.__polySeq) == 1 and len(self.__polySeqRstFailed) == 1:
                                polySeqRst, chainIdMapping, modelChainIdExt =\
                                    splitPolySeqRstForExactNoes(self.__pA, self.__polySeq, self.__polySeqRstFailed, chainAssignFailed)

                                if polySeqRst is not None:
                                    self.__polySeqRst = polySeqRst
                                    if 'chain_id_clone' not in self.reasonsForReParsing:
                                        self.reasonsForReParsing['chain_id_clone'] = chainIdMapping
                                    if 'model_chain_id_ext' not in self.reasonsForReParsing:
                                        self.reasonsForReParsing['model_chain_id_ext'] = modelChainIdExt

                            if self.__hasNonPoly:
                                polySeqRst, nonPolyMapping = splitPolySeqRstForNonPoly(self.__ccU, self.__nonPoly, self.__polySeqRstFailed,
                                                                                       seqAlignFailed, chainAssignFailed)

                                if polySeqRst is not None:
                                    self.__polySeqRst = polySeqRst
                                    if 'non_poly_remap' not in self.reasonsForReParsing:
                                        self.reasonsForReParsing['non_poly_remap'] = nonPolyMapping

                            if self.__hasBranched:
                                polySeqRst, branchedMapping = splitPolySeqRstForBranched(self.__pA, self.__polySeq, self.__branched, self.__polySeqRstFailed,
                                                                                         chainAssignFailed)

                                if polySeqRst is not None:
                                    self.__polySeqRst = polySeqRst
                                    if 'branched_remap' not in self.reasonsForReParsing:
                                        self.reasonsForReParsing['branched_remap'] = branchedMapping

            insuff_dist_atom_sel_warnings = [f for f in self.__f if '[Insufficient atom selection]' in f and 'distance restraints' in f]

            if 'alt_global_sequence_offset' in self.reasonsForReParsing:
                if len(insuff_dist_atom_sel_warnings) < 20\
                   or not any(f for f in self.__f if '[Insufficient atom selection]' in f)\
                   or len(self.reasonsForReParsing) > 1:
                    del self.reasonsForReParsing['alt_global_sequence_offset']
                else:
                    globalSequenceOffset = copy.copy(self.reasonsForReParsing['alt_global_sequence_offset'])
                    for k, v in globalSequenceOffset.items():
                        len_v = 0 if v is None else len(v)
                        if len_v != 1:
                            del self.reasonsForReParsing['alt_global_sequence_offset'][k]
                        else:
                            self.reasonsForReParsing['alt_global_sequence_offset'][k] = list(v)[0]
                    if len(self.reasonsForReParsing['alt_global_sequence_offset']) == 0:
                        del self.reasonsForReParsing['alt_global_sequence_offset']

            if 'local_seq_scheme' in self.reasonsForReParsing:
                if 'non_poly_remap' in self.reasonsForReParsing or 'branched_remap' in self.reasonsForReParsing\
                   or 'np_seq_id_remap' in self.reasonsForReParsing:
                    del self.reasonsForReParsing['local_seq_scheme']
                if 'seq_id_remap' in self.reasonsForReParsing:
                    del self.reasonsForReParsing['seq_id_remap']

            if 'local_seq_scheme' in self.reasonsForReParsing:
                if 'label_seq_offset' in self.reasonsForReParsing:
                    del self.reasonsForReParsing['local_seq_scheme']
                elif len(self.reasonsForReParsing['local_seq_scheme']) == 1:
                    for k, v in self.reasonsForReParsing['local_seq_scheme'].items():
                        if k[0] == 'dist' and not v\
                           and k[1] > 1\
                           and len(insuff_dist_atom_sel_warnings) == 1\
                           and any(f'Check the {k[1]}th row of distance restraints' for f in insuff_dist_atom_sel_warnings):
                            set_label_seq_scheme()  # 2lif

            if 'seq_id_remap' in self.reasonsForReParsing and 'non_poly_remap' in self.reasonsForReParsing:
                if self.__reasons is None and not any(f for f in self.__f if '[Sequence mismatch]' in f):
                    del self.reasonsForReParsing['seq_id_remap']

            if 'np_seq_id_remap' in self.reasonsForReParsing and 'non_poly_remap' in self.reasonsForReParsing:
                effective = False
                for np_remap in self.reasonsForReParsing['np_seq_id_remap']:
                    chainId = np_remap['chain_id']
                    seqIdDict = np_remap['seq_id_dict']
                    for compId, _seqIdDict in self.reasonsForReParsing['non_poly_remap'].items():
                        for _seqId in _seqIdDict:
                            if _seqId in seqIdDict.values():
                                _seqId_ = next(k for k, v in seqIdDict.items() if v == _seqId)
                                if _seqId_ != _seqId:
                                    effective = True
                                    break
                if not effective:
                    del self.reasonsForReParsing['np_seq_id_remap']

            if len(self.__polySeqRstValid) > 0:
                sortPolySeqRst(self.__polySeqRstValid)

            label_seq_scheme = 'label_seq_scheme' in self.reasonsForReParsing\
                and all(t for t in self.reasonsForReParsing['label_seq_scheme'].values())
            local_to_label_seq_scheme = False  # 2lp4

            assert_auth_seq_scheme = 'global_auth_sequence_offset' in self.reasonsForReParsing and not label_seq_scheme

            if 'global_sequence_offset' in self.reasonsForReParsing:
                globalSequenceOffset = copy.copy(self.reasonsForReParsing['global_sequence_offset'])
                for k, v in globalSequenceOffset.items():
                    if v is None:
                        del self.reasonsForReParsing['global_sequence_offset'][k]  # 2l12
                        if not label_seq_scheme\
                           and 'global_auth_sequence_offset' not in self.reasonsForReParsing\
                           and 'segment_id_mismatch' not in self.reasonsForReParsing:  # 2n2w, 2b87, 2mf6 (excl label_seq_scheme)
                            if 'uninterpretable_chain_id' not in self.reasonsForReParsing:
                                self.reasonsForReParsing['uninterpretable_chain_id'] = {}
                            self.reasonsForReParsing['uninterpretable_chain_id'][k] = True  # 2lqc
                if len(self.reasonsForReParsing['global_sequence_offset']) == 0:
                    del self.reasonsForReParsing['global_sequence_offset']

            if 'global_sequence_offset' in self.reasonsForReParsing:
                globalSequenceOffset = copy.copy(self.reasonsForReParsing['global_sequence_offset'])
                has_label_seq_scheme_pred = False
                for k, v in globalSequenceOffset.items():
                    len_v = 0 if v is None else len(v)
                    if len_v != 1:
                        ps = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == k), None)
                        if ps is not None:
                            try:
                                offset = ps['auth_seq_id'][0] - ps['seq_id'][0]
                                if offset == ps['auth_seq_id'][-1] - ps['seq_id'][-1] and offset in v:
                                    has_label_seq_scheme_pred = True
                            except TypeError:
                                pass
                        del self.reasonsForReParsing['global_sequence_offset'][k]
                    else:
                        self.reasonsForReParsing['global_sequence_offset'][k] = list(v)[0]
                    if len(self.reasonsForReParsing['global_sequence_offset']) == 0:
                        del self.reasonsForReParsing['global_sequence_offset']
                        if len_v > 2:
                            if 'label_seq_scheme' in self.reasonsForReParsing and not has_label_seq_scheme_pred:
                                del self.reasonsForReParsing['label_seq_scheme']
                            if 'seq_id_remap' in self.reasonsForReParsing:
                                del self.reasonsForReParsing['seq_id_remap']

            seqIdRemapForRemaining = []
            if 'global_sequence_offset' in self.reasonsForReParsing:
                if 'local_seq_scheme' in self.reasonsForReParsing:
                    del self.reasonsForReParsing['local_seq_scheme']
                if 'label_seq_offset' in self.reasonsForReParsing:
                    del self.reasonsForReParsing['label_seq_offset']
                if 'label_seq_scheme' in self.reasonsForReParsing:
                    if 'global_auth_sequence_offset' not in self.reasonsForReParsing:
                        self.reasonsForReParsing['global_auth_sequence_offset'] = self.reasonsForReParsing['global_sequence_offset']
                        del self.reasonsForReParsing['global_sequence_offset']
                    no_gap = True
                    for ps in self.__polySeq:
                        chainId = ps['auth_chain_id']
                        if chainId not in self.reasonsForReParsing['global_auth_sequence_offset']:
                            if 'gap_in_auth_seq' in ps and ps['gap_in_auth_seq']:
                                offset = next(seq_id - auth_seq_id for seq_id, auth_seq_id in zip(ps['seq_id'], ps['auth_seq_id']))
                                if any(abs(seq_id - auth_seq_id - offset) > 20 for seq_id, auth_seq_id in zip(ps['seq_id'], ps['auth_seq_id'])):
                                    failed_ps = next((failed_ps for failed_ps in self.__polySeqRstFailed if failed_ps['chain_id'] == chainId), None)
                                    if failed_ps is None:
                                        continue
                                    if any(seq_id in ps['seq_id'] and seq_id not in ps['auth_seq_id'] for seq_id in failed_ps['seq_id']):
                                        seqIdRemapForRemaining.append({'chain_id': chainId, 'seq_id_dict': dict(zip(ps['seq_id'], ps['auth_seq_id']))})
                            elif any(seq_id in ps['seq_id'] and seq_id not in ps['auth_seq_id'] for seq_id in ps['seq_id']):
                                safe = True
                                for _ps in self.__polySeq:
                                    if _ps['auth_chain_id'] in self.reasonsForReParsing['global_auth_sequence_offset']:
                                        if any(seq_id in ps['seq_id'] and seq_id in _ps['auth_seq_id'] for seq_id in ps['seq_id']):
                                            safe = False
                                            break
                                if safe:
                                    seqIdRemapForRemaining.append({'chain_id': chainId, 'seq_id_dict': dict(zip(ps['seq_id'], ps['auth_seq_id']))})
                            elif 'gap_in_auth_seq' in ps and ps['gap_in_auth_seq']:
                                _ps = next((_ps for _ps in self.__polySeqRstFailed if _ps['chain_id'] == chainId), None)
                                if _ps is None or not all(_seq_id in ps['seq_id'] for _seq_id, _comp_id in zip(_ps['seq_id'], _ps['comp_id']) if _comp_id not in emptyValue):
                                    del self.reasonsForReParsing['global_auth_sequence_offset'][chainId]
                                    if len(self.reasonsForReParsing['global_auth_sequence_offset']) == 0:
                                        del self.reasonsForReParsing['global_auth_sequence_offset']
                                    no_gap = False
                    if no_gap:
                        del self.reasonsForReParsing['label_seq_scheme']
                if 'inhibit_label_seq_scheme' in self.reasonsForReParsing:
                    del self.reasonsForReParsing['inhibit_label_seq_scheme']
                if 'seq_id_remap' in self.reasonsForReParsing:
                    del self.reasonsForReParsing['seq_id_remap']

            if 'global_auth_sequence_offset' in self.reasonsForReParsing:
                if 'local_seq_scheme' in self.reasonsForReParsing:
                    del self.reasonsForReParsing['local_seq_scheme']
                if 'label_seq_scheme' in self.reasonsForReParsing:
                    no_gap = True
                    for ps in self.__polySeq:
                        chainId = ps['auth_chain_id']
                        if chainId not in self.reasonsForReParsing['global_auth_sequence_offset']:
                            if 'gap_in_auth_seq' in ps and ps['gap_in_auth_seq']:
                                offset = next(seq_id - auth_seq_id for seq_id, auth_seq_id in zip(ps['seq_id'], ps['auth_seq_id']))
                                if any(abs(seq_id - auth_seq_id - offset) > 20 for seq_id, auth_seq_id in zip(ps['seq_id'], ps['auth_seq_id'])):
                                    failed_ps = next((failed_ps for failed_ps in self.__polySeqRstFailed if failed_ps['chain_id'] == chainId), None)
                                    if failed_ps is None:
                                        continue
                                    if any(seq_id in ps['seq_id'] and seq_id not in ps['auth_seq_id'] for seq_id in failed_ps['seq_id']):
                                        seqIdRemapForRemaining.append({'chain_id': chainId, 'seq_id_dict': dict(zip(ps['seq_id'], ps['auth_seq_id']))})
                            elif any(seq_id in ps['seq_id'] and seq_id not in ps['auth_seq_id'] for seq_id in ps['seq_id']):
                                safe = True
                                for _ps in self.__polySeq:
                                    if _ps['auth_chain_id'] in self.reasonsForReParsing['global_auth_sequence_offset']:
                                        if any(seq_id in ps['seq_id'] and seq_id in _ps['auth_seq_id'] for seq_id in ps['seq_id']):
                                            safe = False
                                            break
                                if safe:
                                    seqIdRemapForRemaining.append({'chain_id': chainId, 'seq_id_dict': dict(zip(ps['seq_id'], ps['auth_seq_id']))})
                        elif 'gap_in_auth_seq' in ps and ps['gap_in_auth_seq']:
                            _ps = next((_ps for _ps in self.__polySeqRstFailed if _ps['chain_id'] == chainId), None)
                            if _ps is None or not all(_seq_id in ps['seq_id'] for _seq_id, _comp_id in zip(_ps['seq_id'], _ps['comp_id']) if _comp_id not in emptyValue):
                                del self.reasonsForReParsing['global_auth_sequence_offset'][chainId]
                                if len(self.reasonsForReParsing['global_auth_sequence_offset']) == 0:
                                    del self.reasonsForReParsing['global_auth_sequence_offset']
                                no_gap = False
                    if no_gap:
                        del self.reasonsForReParsing['label_seq_scheme']
                if 'label_seq_offset' in self.reasonsForReParsing:
                    del self.reasonsForReParsing['label_seq_offset']
                if 'inhibit_label_seq_scheme' in self.reasonsForReParsing:
                    del self.reasonsForReParsing['inhibit_label_seq_scheme']
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
                            subst_label_seq_scheme = ps['seq_id'] == ps['auth_seq_id']  # 2n2w
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
                                if label_seq_scheme or subst_label_seq_scheme or 'local_seq_scheme' in self.reasonsForReParsing:
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
                                        if len(_chainIds) > 1:
                                            overlap = False
                                            for _chainId in _chainIds:
                                                if _chainId == chainId:
                                                    continue
                                                _ps = next(_ps for _ps in self.__polySeq if _ps['auth_chain_id'] == _chainId)
                                                if auth_seq_id in ps['auth_seq_id']:
                                                    overlap = True
                                                    break
                                            if overlap:  # 2law
                                                continue
                                        chainIdRemap[auth_seq_id] = {'chain_id': chainId, 'seq_id': auth_seq_id}
                        if valid:
                            if 'global_sequence_offset' in self.reasonsForReParsing:
                                del self.reasonsForReParsing['global_sequence_offset']
                            del self.reasonsForReParsing['global_auth_sequence_offset']
                            self.reasonsForReParsing['chain_id_remap'] = chainIdRemap

            if len(seqIdRemapForRemaining) > 0:
                self.reasonsForReParsing['seq_id_remap'] = seqIdRemapForRemaining

            insuff_dist_atom_sel_in_1st_row_warnings = [f for f in insuff_dist_atom_sel_warnings if 'Check the 1th row of distance restraints' in f]
            invalid_dist_atom_sel_in_1st_row = any(f for f in self.__f if 'Check the 1th row of distance restraints' in f
                                                   and ('[Atom not found]' in f or '[Hydrogen not instantiated]' in f or '[Coordinate issue]' in f))

            if 'local_seq_scheme' in self.reasonsForReParsing\
               and (len(self.reasonsForReParsing) == 1 or len(insuff_dist_atom_sel_warnings) == len(self.__f)  # 2ljb
                    or 'label_seq_scheme' in self.reasonsForReParsing):  # 2joa
                mergePolySeqRstAmbig(self.__polySeqRstFailed, self.__polySeqRstFailedAmbig)
                sortPolySeqRst(self.__polySeqRstFailed)

                valid = True
                if len(self.__polySeqRstFailed) > 0 and 'label_seq_scheme' not in self.reasonsForReParsing:  # 6qeu
                    for _ps in self.__polySeqRstFailed:
                        ps = next((ps for ps in self.__polySeqRstValid if ps['chain_id'] == _ps['chain_id']), None)
                        if ps is None:
                            break
                        if len([compId for compId in ps['comp_id'] if compId not in emptyValue]) > len(_ps['comp_id']) * 2:
                            valid = False
                            break
                if len(self.__polySeqRstFailed) > 0:
                    self.reasonsForReParsing['extend_seq_scheme'] = self.__polySeqRstFailed
                if valid:
                    if len(insuff_dist_atom_sel_in_1st_row_warnings) > 0 and not invalid_dist_atom_sel_in_1st_row:
                        if 'label_seq_scheme' not in self.reasonsForReParsing:
                            self.reasonsForReParsing['label_seq_scheme'] = {}
                        self.reasonsForReParsing['label_seq_scheme']['dist'] = True
                        set_label_seq_scheme()
                        local_to_label_seq_scheme = True  # 2ljb, 2lp4
                    else:
                        del self.reasonsForReParsing['local_seq_scheme']
                else:  # 2ld3
                    if 'inhibit_label_seq_scheme' not in self.reasonsForReParsing:
                        self.reasonsForReParsing['inhibit_label_seq_scheme'] = {}
                    set_label_seq_scheme()
                    for ps in self.__polySeqRstValid:
                        chainId = ps['chain_id']
                        if 'label_seq_scheme' in self.reasonsForReParsing:
                            self.reasonsForReParsing['inhibit_label_seq_scheme'][chainId] = self.reasonsForReParsing['label_seq_scheme']
                    if 'local_seq_scheme' in self.reasonsForReParsing:
                        del self.reasonsForReParsing['local_seq_scheme']
                    if 'label_seq_scheme' in self.reasonsForReParsing:
                        del self.reasonsForReParsing['label_seq_scheme']

            if 'label_seq_scheme' in self.reasonsForReParsing and 'extend_seq_scheme' in self.reasonsForReParsing:  # 2mbv
                for _ps in self.reasonsForReParsing['extend_seq_scheme']:
                    ps = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == _ps['chain_id']), None)
                    if ps is None:
                        continue
                    if all(seqId in ps['seq_id'] for seqId in _ps['seq_id']):
                        self.reasonsForReParsing['extend_seq_scheme'].remove(_ps)
                if len(self.reasonsForReParsing['extend_seq_scheme']) == 0:
                    del self.reasonsForReParsing['extend_seq_scheme']

            if self.hasAnyRestraints():

                if len(self.__f) == 0\
                   and 'label_seq_scheme' in self.reasonsForReParsing:
                    del self.reasonsForReParsing['label_seq_scheme']
                    if 'local_seq_scheme' in self.reasonsForReParsing:
                        del self.reasonsForReParsing['local_seq_scheme']

                elif all('[Anomalous data]' in f for f in self.__f)\
                        and all('distance' in f for f in self.__f)\
                        and 'label_seq_scheme' in self.reasonsForReParsing:
                    del self.reasonsForReParsing['label_seq_scheme']
                    if 'local_seq_scheme' in self.reasonsForReParsing:
                        del self.reasonsForReParsing['local_seq_scheme']
                    __f = copy.deepcopy(self.__f)
                    self.__f = []
                    for f in __f:
                        self.__f.append(re.sub(r'\[Anomalous data\]', '[Atom not found]', f, 1))

                elif all('[Anomalous data]' in f for f in self.__f):
                    pass

                elif not any(f for f in self.__f if '[Atom not found]' in f or '[Anomalous data]' in f)\
                        and 'non_poly_remap' not in self.reasonsForReParsing\
                        and 'branch_remap' not in self.reasonsForReParsing:

                    # ad hoc sequence scheme switching of distance restraints should be inherited
                    if len(insuff_dist_atom_sel_in_1st_row_warnings) > 0 and not invalid_dist_atom_sel_in_1st_row\
                       and (len(self.reasonsForReParsing) == 0 or (len(self.reasonsForReParsing) == 1 and 'label_seq_scheme' in self.reasonsForReParsing))\
                       and (any(f for f in insuff_dist_atom_sel_in_1st_row_warnings if '_distance_' in f)
                            or (len(insuff_dist_atom_sel_warnings) == 1 and any(f for f in insuff_dist_atom_sel_in_1st_row_warnings if 'None' in f))):
                        if 'label_seq_scheme' not in self.reasonsForReParsing:
                            self.reasonsForReParsing['label_seq_scheme'] = {}
                        self.reasonsForReParsing['label_seq_scheme']['dist'] = True
                        set_label_seq_scheme()

                    elif len(self.reasonsForReParsing) > 0 and self.distRestraints > 0\
                            and 'global_auth_sequence_offset' not in self.reasonsForReParsing\
                            and len(insuff_dist_atom_sel_in_1st_row_warnings) == 0\
                            and not all('[Insufficient atom selection]' in f and 'distance restraints' in f for f in self.__f):
                        if any('[Insufficient atom selection]' in f and 'distance restraints' not in f for f in self.__f):
                            if 'label_seq_scheme' not in self.reasonsForReParsing:
                                self.reasonsForReParsing['label_seq_scheme'] = {}
                            self.reasonsForReParsing['label_seq_scheme']['dist'] = True
                            set_label_seq_scheme()
                        elif 'np_seq_id_remap' not in self.reasonsForReParsing and 'non_poly_remap' not in self.reasonsForReParsing:  # 2lml
                            if 'assert_label_seq_scheme' not in self.reasonsForReParsing:  # 2m0k
                                self.reasonsForReParsing = {}

                    if any(f for f in self.__f if '[Sequence mismatch]' in f):
                        __f = copy.copy(self.__f)
                        for f in __f:
                            if '[Sequence mismatch]' in f:
                                self.__f.remove(f)

                elif not assert_auth_seq_scheme:  # 2n0s
                    if 'label_seq_offset' in self.reasonsForReParsing and len(insuff_dist_atom_sel_in_1st_row_warnings) > 0 and not invalid_dist_atom_sel_in_1st_row\
                       and (any(f for f in insuff_dist_atom_sel_in_1st_row_warnings if '_distance_' in f)
                            or (len(insuff_dist_atom_sel_warnings) >= 1 and any(f for f in insuff_dist_atom_sel_in_1st_row_warnings if 'None' in f))):
                        if len(pro_hn_atom_not_found_warnings) + len(gly_hb_atom_not_found_warnings) > 0:
                            for chain_id in self.reasonsForReParsing['label_seq_offset']:
                                pro_seq_ids, gly_seq_ids = set(), set()
                                for f in pro_hn_atom_not_found_warnings:
                                    g = pro_hn_atom_not_found_pattern.search(f).groups()
                                    if g[0] != chain_id:
                                        continue
                                    pro_seq_ids.add(int(g[1]))
                                for f in gly_hb_atom_not_found_warnings:
                                    g = gly_hb_atom_not_found_pattern.search(f).groups()
                                    if g[0] != chain_id:
                                        continue
                                    gly_seq_ids.add(int(g[1]))
                                if len(pro_seq_ids) + len(gly_seq_ids) == 0:
                                    continue
                                ps = next((ps for ps in self.__polySeq if ps['chain_id'] == chain_id), None)
                                if ps is not None and ps['comp_id'][0] == 'ACE':
                                    self.reasonsForReParsing['label_seq_offset'][chain_id] = 1
                        if 'label_seq_scheme' not in self.reasonsForReParsing:
                            self.reasonsForReParsing['label_seq_scheme'] = {}
                        self.reasonsForReParsing['label_seq_scheme']['dist'] = True
                        set_label_seq_scheme()

                    elif ('non_poly_remap' in self.reasonsForReParsing or 'branch_remap' in self.reasonsForReParsing)\
                            and 'global_sequence_offset' not in self.reasonsForReParsing\
                            and 'global_auth_sequence_offset' not in self.reasonsForReParsing\
                            and 'segment_id_mismatch' not in self.reasonsForReParsing:
                        if self.distRestraints > 0 or len(self.__polySeq) == 1 or all('identical_chain_id' in ps for ps in self.__polySeq):
                            if 'label_seq_scheme' not in self.reasonsForReParsing:
                                self.reasonsForReParsing['label_seq_scheme'] = {}
                            self.reasonsForReParsing['label_seq_scheme']['dist'] = True
                            set_label_seq_scheme()

            elif self.__reasons is None and len(self.reasonsForReParsing) == 0 and all('[Insufficient atom selection]' in f for f in self.__f):
                set_label_seq_scheme()

            if self.__reasons is None and self.__complexSeqScheme and 'inhibit_label_seq_scheme_stats' in self.reasonsForReParsing:
                if 'label_seq_scheme' not in self.reasonsForReParsing:
                    del self.reasonsForReParsing['inhibit_label_seq_scheme_stats']
                else:
                    positive = negative = 0  # 2n1a
                    for ps in self.__polySeq:
                        if ps['auth_chain_id'] in self.reasonsForReParsing['inhibit_label_seq_scheme_stats']:
                            if self.reasonsForReParsing['inhibit_label_seq_scheme_stats'][ps['auth_chain_id']] / len(ps['seq_id']) < 1.0:  # 2ruk
                                negative += 1
                                del self.reasonsForReParsing['inhibit_label_seq_scheme_stats'][ps['auth_chain_id']]
                            else:
                                positive += 1
                    if len(self.reasonsForReParsing['inhibit_label_seq_scheme_stats']) == 0 or positive * negative == 0:
                        del self.reasonsForReParsing['inhibit_label_seq_scheme_stats']

            if 'segment_id_mismatch' in self.reasonsForReParsing:
                if 'np_seq_id_remap' not in self.reasonsForReParsing and 'non_poly_remap' not in self.reasonsForReParsing\
                   and not local_to_label_seq_scheme\
                   and 'inhibit_label_seq_scheme' not in self.reasonsForReParsing:  # 2ljb, 2lp4, 1qkg, 2lkm
                    if 'local_seq_scheme' in self.reasonsForReParsing:
                        del self.reasonsForReParsing['local_seq_scheme']
                    if 'label_seq_scheme' in self.reasonsForReParsing:
                        del self.reasonsForReParsing['label_seq_scheme']
                    if 'label_seq_offset' in self.reasonsForReParsing:
                        del self.reasonsForReParsing['label_seq_offset']

                for chainId, _chainId in self.reasonsForReParsing['segment_id_mismatch'].items():
                    uniq = True
                    for k, v in self.reasonsForReParsing['segment_id_mismatch'].items():
                        if k == chainId:
                            continue
                        if v == _chainId:
                            uniq = False
                            break
                    if not uniq:
                        ps = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == _chainId and 'identical_auth_chain_id' in ps), None)
                        if ps is not None:
                            dst_chain_id_set = [_chainId]
                            dst_chain_id_set.extend(ps['identical_auth_chain_id'])
                            dst_chain_id_set.sort()
                            src_chain_id_set = [chainId]
                            for k, v in self.reasonsForReParsing['segment_id_mismatch'].items():
                                if k == chainId or v not in dst_chain_id_set:
                                    continue
                                src_chain_id_set.append(k)
                            src_chain_id_set.sort()
                            for src_chain_id, dst_chain_id in zip(src_chain_id_set, dst_chain_id_set):
                                self.reasonsForReParsing['segment_id_mismatch'][src_chain_id] = dst_chain_id

                if 'inhibit_label_seq_scheme' in self.reasonsForReParsing\
                   and len(self.reasonsForReParsing['inhibit_label_seq_scheme']) == len(set(filter(None, self.reasonsForReParsing['segment_id_mismatch'].values())))\
                   and all(chainId in self.reasonsForReParsing['segment_id_mismatch'].values()
                           for chainId in self.reasonsForReParsing['inhibit_label_seq_scheme']):  # 2ljc, 1qkg
                    if 'local_seq_scheme' in self.reasonsForReParsing:
                        del self.reasonsForReParsing['local_seq_scheme']
                    if 'label_seq_scheme' in self.reasonsForReParsing:
                        del self.reasonsForReParsing['label_seq_scheme']
                    if 'label_seq_offset' in self.reasonsForReParsing:
                        del self.reasonsForReParsing['label_seq_offset']

                if (label_seq_scheme and 'inhibit_label_seq_scheme' not in self.reasonsForReParsing)\
                   or ('np_seq_id_remap' in self.reasonsForReParsing or 'non_poly_remap' in self.reasonsForReParsing):  # 6f0y, 2lkm, 2mnz
                    for chain_id in self.reasonsForReParsing['segment_id_mismatch'].values():
                        ps = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == chain_id), None)
                        if ps is None:
                            continue
                        if 'gap_in_auth_seq' in ps and ps['gap_in_auth_seq']:
                            offset = next(seq_id - auth_seq_id for seq_id, auth_seq_id in zip(ps['seq_id'], ps['auth_seq_id']))
                            if any(abs(seq_id - auth_seq_id - offset) > 20 for seq_id, auth_seq_id in zip(ps['seq_id'], ps['auth_seq_id'])):
                                failed_ps = next((failed_ps for failed_ps in self.__polySeqRstFailed if failed_ps['chain_id'] == ps['auth_chain_id']), None)
                                if failed_ps is None:
                                    continue
                                if any(seq_id in ps['seq_id'] and seq_id not in ps['auth_seq_id'] for seq_id in failed_ps['seq_id']):
                                    seqIdRemapForRemaining.append({'chain_id': ps['auth_chain_id'], 'seq_id_dict': dict(zip(ps['seq_id'], ps['auth_seq_id']))})
                        elif any(seq_id in ps['seq_id'] and seq_id not in ps['auth_seq_id'] for seq_id in ps['seq_id']):
                            safe = True
                            for _ps in self.__polySeq:
                                if _ps['auth_chain_id'] != ps['auth_chain_id']:
                                    if any(seq_id in ps['seq_id'] and seq_id in _ps['auth_seq_id'] for seq_id in ps['seq_id']):
                                        safe = False
                                        break
                            if 'np_seq_id_remap' in self.reasonsForReParsing or 'non_poly_remap' in self.reasonsForReParsing:
                                for _np in self.__nonPolySeq:
                                    if _np['auth_chain_id'] == chain_id:
                                        safe = False  # 2lba
                                        break
                            if safe:
                                seqIdRemapForRemaining.append({'chain_id': ps['auth_chain_id'], 'seq_id_dict': dict(zip(ps['seq_id'], ps['auth_seq_id']))})

                    if len(seqIdRemapForRemaining) > 0:
                        self.reasonsForReParsing['seq_id_remap'] = seqIdRemapForRemaining

                if 'chain_id_remap' in self.reasonsForReParsing:
                    stat_chain_ids = set()
                    for v in self.reasonsForReParsing['segment_id_match_stats'].values():
                        for _k, _v in v.items():
                            if _v > 0:
                                stat_chain_ids.add(_k)
                    map_chain_ids = set()
                    for v in self.reasonsForReParsing['chain_id_remap'].values():
                        map_chain_ids.add(v['chain_id'])
                    if stat_chain_ids == map_chain_ids:
                        # del self.reasonsForReParsing['segment_id_mismatch'] 6f0y
                        del self.reasonsForReParsing['segment_id_match_stats']
                        del self.reasonsForReParsing['segment_id_poly_type_stats']
                        if 'global_auth_sequence_offset' in self.reasonsForReParsing:
                            del self.reasonsForReParsing['global_auth_sequence_offset']

                if len(self.__f) == 0 and len(self.reasonsForReParsing) > 0:
                    if 'assert_label_seq_scheme' not in self.reasonsForReParsing:
                        self.reasonsForReParsing = {}

            elif 'chain_id_remap' in self.reasonsForReParsing:
                if 'seq_id_remap' in self.reasonsForReParsing:
                    del self.reasonsForReParsing['seq_id_remap']  # 6ijv

                if 'global_auth_sequence_offset' in self.reasonsForReParsing:
                    del self.reasonsForReParsing['global_auth_sequence_offset']  # 2lzs

                if len(self.__f) == 0 and len(self.reasonsForReParsing) > 0:
                    if 'assert_label_seq_scheme' not in self.reasonsForReParsing:
                        self.reasonsForReParsing = {}

            if len(self.reasonsForReParsing) == 0 and self.__reasons is None\
               and any('[Insufficient atom selection]' in f and 'Macromolecules page' in f for f in self.__f):
                __f = copy.deepcopy(self.__f)
                self.__f = []
                for f in __f:
                    if '[Insufficient atom selection]' in f and 'Macromolecules page' in f:
                        self.__f.append(f.replace('[Insufficient atom selection]', '[Sequence mismatch warning]'))  # 2laz
                    else:
                        self.__f.append(f)

        finally:
            self.warningMessage = sorted(list(set(self.__f)), key=self.__f.index)

    # Enter a parse tree produced by CharmmMRParser#comment.
    def enterComment(self, ctx: CharmmMRParser.CommentContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by CharmmMRParser#comment.
    def exitComment(self, ctx: CharmmMRParser.CommentContext):
        comment = []
        for col in range(20):
            if ctx.Any_name(col):
                text = str(ctx.Any_name(col))
                if text[0] in ('#', '!'):
                    break
                comment.append(str(ctx.Any_name(col)))
            else:
                break
        self.lastComment = None if len(comment) == 0 else ' '.join(comment)

    # Enter a parse tree produced by CharmmMRParser#distance_restraint.
    def enterDistance_restraint(self, ctx: CharmmMRParser.Distance_restraintContext):  # pylint: disable=unused-argument
        self.__cur_subtype_altered = self.__cur_subtype != 'dist' and len(self.__cur_subtype) > 0
        self.__cur_subtype = 'dist'

        if self.__cur_subtype_altered and not self.__preferAuthSeq:
            self.__preferAuthSeq = True
            self.__authSeqId = 'auth_seq_id'

        self.noeAverage = 'r-6'  # default averaging method
        self.squareExponent = 1.0
        self.rSwitch = None
        self.scale = 1.0
        self.kMin = 0.0
        self.kMax = 0.0
        self.rMin = 0.0
        self.rMax = None
        self.fMax = None
        # self.tCon = 0.0
        self.rExp = -1.0 / 6.0

        if self.__createSfDict:
            self.__addSf()

    # Exit a parse tree produced by CharmmMRParser#distance_restraint.
    def exitDistance_restraint(self, ctx: CharmmMRParser.Distance_restraintContext):  # pylint: disable=unused-argument

        try:

            target_value = None
            lower_limit = self.rMin
            upper_limit = self.rMax
            lower_linear_limit = None
            upper_linear_limit = None

            if self.fMax is not None and self.fMax > 0.0 and self.kMax > 0.0:
                upper_linear_limit = self.rMax + self.fMax / self.kMax
            if self.rSwitch is not None:
                upper_linear_limit = self.rMax + self.rSwitch

            if not self.__hasPolySeq and not self.__hasNonPolySeq:
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

            dstFunc = self.validateDistanceRange(self.scale, self.squareExponent if self.rSwitch is not None else 1.0,
                                                 target_value, lower_limit, upper_limit,
                                                 lower_linear_limit, upper_linear_limit)

            if dstFunc is None:
                return

            if 0 in (len(self.atomSelectionSet[0]), len(self.atomSelectionSet[1])):
                if len(self.__g) > 0:
                    self.__f.extend(self.__g)
                return

            memberId = memberLogicCode = '.'
            if self.__createSfDict:
                sf = self.__getSf(constraintType=getDistConstraintType(self.atomSelectionSet, dstFunc,
                                                                       self.__csStat, self.__originalFileName),
                                  potentialType=getPotentialType(self.__file_type, self.__cur_subtype, dstFunc))
                sf['id'] += 1
                memberLogicCode = 'OR' if len(self.atomSelectionSet[0]) * len(self.atomSelectionSet[1]) > 1 else '.'
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
                    print(f"subtype={self.__cur_subtype} (NOE) id={self.distRestraints} "
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

            if self.__createSfDict and sf is not None and isinstance(memberId, int) and memberId == 1:
                sf['loop'].data[-1] = resetMemberId(self.__cur_subtype, sf['loop'].data[-1])

        finally:
            self.numberSelection.clear()

            if self.__createSfDict:
                self.__trimSfWoLp()

    # Enter a parse tree produced by CharmmMRParser#point_distance_restraint.
    def enterPoint_distance_restraint(self, ctx: CharmmMRParser.Point_distance_restraintContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'geo'

    # Exit a parse tree produced by CharmmMRParser#point_distance_restraint.
    def exitPoint_distance_restraint(self, ctx: CharmmMRParser.Point_distance_restraintContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by CharmmMRParser#dihedral_angle_restraint.
    def enterDihedral_angle_restraint(self, ctx: CharmmMRParser.Dihedral_angle_restraintContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'dihed'

        if self.__createSfDict:
            self.__addSf()

    # Exit a parse tree produced by CharmmMRParser#dihedral_angle_restraint.
    def exitDihedral_angle_restraint(self, ctx: CharmmMRParser.Dihedral_angle_restraintContext):  # pylint: disable=unused-argument

        try:

            target_value = self.min
            lower_limit = None
            upper_limit = None
            lower_linear_limit = None
            upper_linear_limit = None

            dstFunc = self.validateAngleRange(1.0, {'force': self.force, 'period': self.period},
                                              target_value, lower_limit, upper_limit,
                                              lower_linear_limit, upper_linear_limit)

            if dstFunc is None:
                return

            if not self.__hasPolySeq and not self.__hasNonPolySeq:
                return

            if len(self.atomSelectionSet) != 4:
                return

            try:
                compId = self.atomSelectionSet[0][0]['comp_id']
                peptide, nucleotide, carbohydrate = self.__csStat.getTypeOfCompId(compId)
            except IndexError:
                if not self.areUniqueCoordAtoms('a dihedral angle (DIHE)'):
                    if len(self.__g) > 0:
                        self.__f.extend(self.__g)
                return

            len_f = len(self.__f)
            self.areUniqueCoordAtoms('a dihedral angle (DIHE)',
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
                    print(f"subtype={self.__cur_subtype} (DIHE) id={self.dihedRestraints} angleName={angleName} "
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
                                 atom1, atom2, atom3, atom4)
                    sf['loop'].add_data(row)

            if self.__createSfDict and sf is not None and isinstance(combinationId, int) and combinationId == 1:
                sf['loop'].data[-1] = resetCombinationId(self.__cur_subtype, sf['loop'].data[-1])

        finally:
            self.numberSelection.clear()

            if self.__createSfDict:
                self.__trimSfWoLp()

    # Enter a parse tree produced by CharmmMRParser#harmonic_restraint.
    def enterHarmonic_restraint(self, ctx: CharmmMRParser.Harmonic_restraintContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'geo'

    # Exit a parse tree produced by CharmmMRParser#harmonic_restraint.
    def exitHarmonic_restraint(self, ctx: CharmmMRParser.Harmonic_restraintContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by CharmmMRParser#manipulate_internal_coordinate.
    def enterManipulate_internal_coordinate(self, ctx: CharmmMRParser.Manipulate_internal_coordinateContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'geo'

    # Exit a parse tree produced by CharmmMRParser#manipulate_internal_coordinate.
    def exitManipulate_internal_coordinate(self, ctx: CharmmMRParser.Manipulate_internal_coordinateContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by CharmmMRParser#droplet_potential.
    def enterDroplet_potential(self, ctx: CharmmMRParser.Droplet_potentialContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by CharmmMRParser#droplet_potential.
    def exitDroplet_potential(self, ctx: CharmmMRParser.Droplet_potentialContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by CharmmMRParser#fix_atom_constraint.
    def enterFix_atom_constraint(self, ctx: CharmmMRParser.Fix_atom_constraintContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'geo'

    # Exit a parse tree produced by CharmmMRParser#fix_atom_constraint.
    def exitFix_atom_constraint(self, ctx: CharmmMRParser.Fix_atom_constraintContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by CharmmMRParser#center_of_mass_constraint.
    def enterCenter_of_mass_constraint(self, ctx: CharmmMRParser.Center_of_mass_constraintContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'geo'

    # Exit a parse tree produced by CharmmMRParser#center_of_mass_constraint.
    def exitCenter_of_mass_constraint(self, ctx: CharmmMRParser.Center_of_mass_constraintContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by CharmmMRParser#fix_bond_or_angle_constraint.
    def enterFix_bond_or_angle_constraint(self, ctx: CharmmMRParser.Fix_bond_or_angle_constraintContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'geo'

    # Exit a parse tree produced by CharmmMRParser#fix_bond_or_angle_constraint.
    def exitFix_bond_or_angle_constraint(self, ctx: CharmmMRParser.Fix_bond_or_angle_constraintContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by CharmmMRParser#restrained_distance.
    def enterRestrained_distance(self, ctx: CharmmMRParser.Restrained_distanceContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'geo'

    # Exit a parse tree produced by CharmmMRParser#restrained_distance.
    def exitRestrained_distance(self, ctx: CharmmMRParser.Restrained_distanceContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by CharmmMRParser#external_force.
    def enterExternal_force(self, ctx: CharmmMRParser.External_forceContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'geo'

    # Exit a parse tree produced by CharmmMRParser#external_force.
    def exitExternal_force(self, ctx: CharmmMRParser.External_forceContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by CharmmMRParser#rmsd_restraint.
    def enterRmsd_restraint(self, ctx: CharmmMRParser.Rmsd_restraintContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'geo'

    # Exit a parse tree produced by CharmmMRParser#rmsd_restraint.
    def exitRmsd_restraint(self, ctx: CharmmMRParser.Rmsd_restraintContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by CharmmMRParser#gyration_restraint.
    def enterGyration_restraint(self, ctx: CharmmMRParser.Gyration_restraintContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'geo'

    # Exit a parse tree produced by CharmmMRParser#gyration_restraint.
    def exitGyration_restraint(self, ctx: CharmmMRParser.Gyration_restraintContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by CharmmMRParser#distance_matrix_restraint.
    def enterDistance_matrix_restraint(self, ctx: CharmmMRParser.Distance_matrix_restraintContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'geo'

    # Exit a parse tree produced by CharmmMRParser#distance_matrix_restraint.
    def exitDistance_matrix_restraint(self, ctx: CharmmMRParser.Distance_matrix_restraintContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by CharmmMRParser#noe_statement.
    def enterNoe_statement(self, ctx: CharmmMRParser.Noe_statementContext):
        if ctx.MinDist():
            self.noeAverage = 'min'

        elif ctx.SumR():
            self.noeAverage = 'sum'

        elif ctx.SExp():
            self.squareExponent = self.getNumber_s(ctx.number_s(0))
            if isinstance(self.squareExponent, str):
                if self.squareExponent in self.evaluate:
                    self.squareExponent = self.evaluate[self.squareExponent]
                else:
                    self.__f.append("[Unsupported data] "
                                    f"The symbol {self.squareExponent!r} in the 'NOE' statement is not defined so that set the default value.")
                    self.squareExponent = 1.0
            if self.squareExponent is None or self.squareExponent <= 0.0:
                self.__f.append("[Invalid data] "
                                "The exponent value of square-well or soft-square function "
                                f"'NOE {str(ctx.SExp())} {self.squareExponent} END' must be a positive value.")

        elif ctx.RSwi():
            self.rSwitch = self.getNumber_s(ctx.number_s(0))
            if isinstance(self.rSwitch, str):
                if self.rSwitch in self.evaluate:
                    self.rSwitch = self.evaluate[self.rSwitch]
                else:
                    self.__f.append("[Unsupported data] "
                                    f"The symbol {self.rSwitch!r} in the 'NOE' statement is not defined so that set the default value.")
                    self.rSwitch = 1.0
            if self.rSwitch is None or self.rSwitch < 0.0:
                self.__f.append("[Invalid data] "
                                "The smoothing parameter of soft-square function "
                                f"'NOE {str(ctx.RSwi())} {self.rSwitch} END' must not be a negative value.")

        elif ctx.Scale():
            self.scale = self.getNumber_s(ctx.number_s(0))
            if isinstance(self.scale, str):
                if self.scale in self.evaluate:
                    self.scale = self.evaluate[self.scale]
                else:
                    self.__f.append("[Unsupported data] "
                                    f"The symbol {self.scale!r} in the 'NOE' statement is not defined so that set the default value.")
                    self.scale = 1.0
            if self.scale is None or self.scale == 0.0:
                self.__f.append("[Range value warning] "
                                f"The scale value 'NOE {str(ctx.Scale())} {self.scale} END' should be a positive value.")
            elif self.scale < 0.0:
                self.__f.append("[Invalid data] "
                                f"The scale value 'NOE {str(ctx.Scale())} {self.scale} END' must not be a negative value.")

        elif ctx.KMin():
            self.kMin = self.getNumber_s(ctx.number_s(0))
            if isinstance(self.kMin, str):
                if self.kMin in self.evaluate:
                    self.kMin = self.evaluate[self.kMin]
                else:
                    self.__f.append("[Unsupported data] "
                                    f"The symbol {self.kMin!r} in the 'NOE' statement is not defined so that set the default value.")
                    self.kMin = 0.0
            if self.kMin is None or self.kMin < 0.0:
                self.__f.append("[Invalid data] "
                                "The kinetic parameter of soft-square function "
                                f"'NOE {str(ctx.KMin())} {self.kMin} END' must not be a negative value.")

        elif ctx.KMax():
            self.kMax = self.getNumber_s(ctx.number_s(0))
            if isinstance(self.kMax, str):
                if self.kMax in self.evaluate:
                    self.kMax = self.evaluate[self.kMax]
                else:
                    self.__f.append("[Unsupported data] "
                                    f"The symbol {self.kMax!r} in the 'NOE' statement is not defined so that set the default value.")
                    self.kMax = 0.0
            if self.kMax is None or self.kMax < 0.0:
                self.__f.append("[Invalid data] "
                                "The kinetic parameter of soft-square function "
                                f"'NOE {str(ctx.KMax())} {self.kMax} END' must not be a negative value.")

        elif ctx.RMin():
            self.rMin = self.getNumber_s(ctx.number_s(0))
            if isinstance(self.rMin, str):
                if self.rMin in self.evaluate:
                    self.rMin = self.evaluate[self.rMin]
                else:
                    self.__f.append("[Unsupported data] "
                                    f"The symbol {self.rMin!r} in the 'NOE' statement is not defined so that set the default value.")
                    self.rMin = 0.0
            if self.rMin is None or self.rMin < 0.0:
                self.__f.append("[Invalid data] "
                                "The lower limit of distance restraint "
                                f"'NOE {str(ctx.RMin())} {self.rMin} END' must not be a negative value.")

        elif ctx.RMax():
            self.rMax = self.getNumber_s(ctx.number_s(0))
            if isinstance(self.rMax, str):
                if self.rMax in self.evaluate:
                    self.rMax = self.evaluate[self.rMax]
                else:
                    self.__f.append("[Unsupported data] "
                                    f"The symbol {self.rMax!r} in the 'NOE' statement is not defined so that set the default value.")
                    self.rMax = None
            if self.rMax is not None and self.rMax < 0.0:
                self.__f.append("[Invalid data] "
                                "The upper limit of distance restraint "
                                f"'NOE {str(ctx.RMax())} {self.rMax} END' must not be a negative value.")

        elif ctx.FMax():
            self.fMax = self.getNumber_s(ctx.number_s(0))
            if isinstance(self.fMax, str):
                if self.fMax in self.evaluate:
                    self.fMax = self.evaluate[self.fMax]
                else:
                    self.__f.append("[Unsupported data] "
                                    f"The symbol {self.fMax!r} in the 'NOE' statement is not defined so that set the default value.")
                    self.fMax = None
            if self.fMax is not None and self.fMax < 0.0:
                self.__f.append("[Invalid data] "
                                "The kinetic parameter of smoothing function "
                                f"'NOE {str(ctx.FMax())} {self.fMax} END' must not be a negative value.")

        elif ctx.RExp():
            self.rExp = self.getNumber_s(ctx.number_s(0))
            if isinstance(self.rExp, str):
                if self.rExp in self.evaluate:
                    self.rExp = self.evaluate[self.rExp]
                else:
                    self.__f.append("[Unsupported data] "
                                    f"The symbol {self.rExp!r} in the 'NOE' statement is not defined so that set the default value.")
                    self.rExp = -1.0 / 6.0
            if abs(self.rExp + 1.0 / 6.0) < 0.001 or abs(self.rExp - 6.0) < 0.001:
                self.noeAverage = 'r-6'
            elif abs(self.rExp - 3.0) < 0.001:
                self.noeAverage = 'r-3'
            elif abs(self.rExp - 1.0) < 0.001:
                self.noeAverage = 'center'

        elif ctx.Reset():
            self.noeAverage = 'r-6'
            self.squareExponent = 1.0
            self.rSwitch = None
            self.scale = 1.0
            self.kMin = 0.0
            self.kMax = 0.0
            self.rMin = 0.0
            self.rMax = None
            self.fMax = None
            # self.tCon = 0.0
            self.rExp = -1.0 / 6.0

    # Exit a parse tree produced by CharmmMRParser#noe_statement.
    def exitNoe_statement(self, ctx: CharmmMRParser.Noe_statementContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by CharmmMRParser#noe_assign.
    def enterNoe_assign(self, ctx: CharmmMRParser.Noe_assignContext):  # pylint: disable=unused-argument
        self.distRestraints += 1

        self.atomSelectionSet.clear()
        self.__g.clear()

    # Exit a parse tree produced by CharmmMRParser#noe_assign.
    def exitNoe_assign(self, ctx: CharmmMRParser.Noe_assignContext):  # pylint: disable=unused-argument
        pass

    def validateDistanceRange(self, weight: float, squareExponent: float, target_value: Optional[float],
                              lower_limit: Optional[float], upper_limit: Optional[float],
                              lower_linear_limit: Optional[float], upper_linear_limit: Optional[float]) -> Optional[dict]:
        """ Validate distance value range.
        """

        validRange = True
        dstFunc = {'weight': weight, 'average': self.noeAverage, 'exponent_over_upper_limit': squareExponent}

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
                                    f"The target value='{target_value}' is omitted because it is not within range {DIST_RESTRAINT_ERROR}.")
                    target_value = None
                else:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                    f"The target value='{target_value}' must be within range {DIST_RESTRAINT_ERROR}.")

        if lower_limit is not None:
            if DIST_ERROR_MIN <= lower_limit < DIST_ERROR_MAX:
                dstFunc['lower_limit'] = f"{lower_limit:.3f}" if lower_limit > 0.0 else "0.0"
            else:
                if lower_limit <= DIST_ERROR_MIN and self.__omitDistLimitOutlier:
                    self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                    f"The lower limit value='{lower_limit:.3f}' is omitted because it is not within range {DIST_RESTRAINT_ERROR}.")
                    lower_limit = None
                else:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                    f"The lower limit value='{lower_limit:.3f}' must be within range {DIST_RESTRAINT_ERROR}.")

        if upper_limit is not None:
            if DIST_ERROR_MIN < upper_limit <= DIST_ERROR_MAX or (upper_limit == 0.0 and self.__allowZeroUpperLimit):
                dstFunc['upper_limit'] = f"{upper_limit:.3f}" if upper_limit > 0.0 else "0.0"
            else:
                if (upper_limit <= DIST_ERROR_MIN or upper_limit > DIST_ERROR_MAX) and self.__omitDistLimitOutlier:
                    self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                    f"The upper limit value='{upper_limit:.3f}' is omitted because it is not within range {DIST_RESTRAINT_ERROR}.")
                    upper_limit = None
                else:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                    f"The upper limit value='{upper_limit:.3f}' must be within range {DIST_RESTRAINT_ERROR}.")

        if lower_linear_limit is not None:
            if DIST_ERROR_MIN <= lower_linear_limit < DIST_ERROR_MAX:
                dstFunc['lower_linear_limit'] = f"{lower_linear_limit:.3f}" if lower_linear_limit > 0.0 else "0.0"
            else:
                if lower_linear_limit <= DIST_ERROR_MIN and self.__omitDistLimitOutlier:
                    self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                    f"The lower linear limit value='{lower_linear_limit:.3f}' is omitted because it is not within range {DIST_RESTRAINT_ERROR}.")
                    lower_linear_limit = None
                else:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                    f"The lower linear limit value='{lower_linear_limit:.3f}' must be within range {DIST_RESTRAINT_ERROR}.")

        if upper_linear_limit is not None:
            if DIST_ERROR_MIN < upper_linear_limit <= DIST_ERROR_MAX or (upper_linear_limit == 0.0 and self.__allowZeroUpperLimit):
                dstFunc['upper_linear_limit'] = f"{upper_linear_limit:.3f}" if upper_linear_limit > 0.0 else "0.0"
            else:
                if (upper_linear_limit <= DIST_ERROR_MIN or upper_linear_limit > DIST_ERROR_MAX) and self.__omitDistLimitOutlier:
                    self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                    f"The upper linear limit value='{upper_linear_limit:.3f}' is omitted because it is not within range {DIST_RESTRAINT_ERROR}.")
                    upper_linear_limit = None
                else:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                    f"The upper linear limit value='{upper_linear_limit:.3f}' must be within range {DIST_RESTRAINT_ERROR}.")

        if target_value is not None:

            if lower_limit is not None:
                if lower_limit > target_value:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                    f"The lower limit value='{lower_limit:.3f}' must be less than the target value '{target_value}'. "
                                    "It indicates that a negative value was unexpectedly set: "
                                    f"d={target_value}, dminus={self.numberSelection[1]}, dplus={self.numberSelection[2]}.")

            if lower_linear_limit is not None:
                if lower_linear_limit > target_value:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                    f"The lower linear limit value='{lower_linear_limit:.3f}' must be less than the target value '{target_value}'. "
                                    "It indicates that a negative value was unexpectedly set: "
                                    f"d={target_value}, dminus={self.numberSelection[1]}, dplus={self.numberSelection[2]}.")

            if upper_limit is not None:
                if upper_limit < target_value:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                    f"The upper limit value='{upper_limit:.3f}' must be greater than the target value '{target_value}'. "
                                    "It indicates that a negative value was unexpectedly set: "
                                    f"d={target_value}, dminus={self.numberSelection[1]}, dplus={self.numberSelection[2]}.")

            if upper_linear_limit is not None:
                if upper_linear_limit < target_value:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                    f"The upper linear limit value='{upper_linear_limit:.3f}' must be greater than the target value '{target_value}'. "
                                    "It indicates that a negative value was unexpectedly set: "
                                    f"d={target_value}, dminus={self.numberSelection[1]}, dplus={self.numberSelection[2]}.")

        else:

            if None not in (lower_limit, upper_limit):
                if lower_limit > upper_limit:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                    f"The lower limit value='{lower_limit:.3f}' must be less than the upper limit value '{upper_limit:.3f}'.")
            if None not in (lower_linear_limit, upper_limit):
                if lower_linear_limit > upper_limit:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                    f"The lower linear limit value='{lower_linear_limit:.3f}' must be less than the upper limit value '{upper_limit:.3f}'.")

            if None not in (lower_limit, upper_linear_limit):
                if lower_limit > upper_linear_limit:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                    f"The lower limit value='{lower_limit:.3f}' must be less than the upper limit value '{upper_linear_limit:.3f}'.")

            if None not in (lower_linear_limit, upper_linear_limit):
                if lower_linear_limit > upper_linear_limit:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                    f"The lower linear limit value='{lower_linear_limit:.3f}' must be less than the upper limit value '{upper_linear_limit:.3f}'.")

            if None not in (lower_limit, lower_linear_limit):
                if lower_linear_limit > lower_limit:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                    f"The lower linear limit value='{lower_linear_limit:.3f}' must be less than the lower limit value '{lower_limit:.3f}'.")

            if None not in (upper_limit, upper_linear_limit):
                if upper_limit > upper_linear_limit:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                    f"The upper limit value='{upper_limit:.3f}' must be less than the upper linear limit value '{upper_linear_limit:.3f}'.")

        if not validRange:
            return None

        if target_value is not None:
            if DIST_RANGE_MIN <= target_value <= DIST_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                f"The target value='{target_value}' should be within range {DIST_RESTRAINT_RANGE}.")

        if lower_limit is not None:
            if DIST_RANGE_MIN <= lower_limit <= DIST_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                f"The lower limit value='{lower_limit:.3f}' should be within range {DIST_RESTRAINT_RANGE}.")

        if upper_limit is not None:
            if DIST_RANGE_MIN <= upper_limit <= DIST_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                f"The upper limit value='{upper_limit:.3f}' should be within range {DIST_RESTRAINT_RANGE}.")

        if lower_linear_limit is not None:
            if DIST_RANGE_MIN <= lower_linear_limit <= DIST_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                f"The lower linear limit value='{lower_linear_limit:.3f}' should be within range {DIST_RESTRAINT_RANGE}.")

        if upper_linear_limit is not None:
            if DIST_RANGE_MIN <= upper_linear_limit <= DIST_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                f"The upper linear limit value='{upper_linear_limit:.3f}' should be within range {DIST_RESTRAINT_RANGE}.")

        if target_value is None and lower_limit is None and upper_limit is None and lower_linear_limit is None and upper_linear_limit is None:
            return None

        return dstFunc

    # Enter a parse tree produced by CharmmMRParser#pnoe_statement.
    def enterPnoe_statement(self, ctx: CharmmMRParser.Pnoe_statementContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by CharmmMRParser#pnoe_statement.
    def exitPnoe_statement(self, ctx: CharmmMRParser.Pnoe_statementContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by CharmmMRParser#pnoe_assign.
    def enterPnoe_assign(self, ctx: CharmmMRParser.Pnoe_assignContext):  # pylint: disable=unused-argument
        self.geoRestraints += 1

        self.atomSelectionSet.clear()
        self.__g.clear()

    # Exit a parse tree produced by CharmmMRParser#pnoe_assign.
    def exitPnoe_assign(self, ctx: CharmmMRParser.Pnoe_assignContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by CharmmMRParser#dihedral_statement.
    def enterDihedral_statement(self, ctx: CharmmMRParser.Dihedral_statementContext):  # pylint: disable=unused-argument
        if ctx.Force():
            self.force = float(str(ctx.Force()))

        elif ctx.Min():
            self.min = float(str(ctx.Min()))

        elif ctx.Width():
            self.width = float(str(ctx.Width()))

        elif ctx.Period():
            self.period = int(str(ctx.Period()))

    # Exit a parse tree produced by CharmmMRParser#dihedral_statement.
    def exitDihedral_statement(self, ctx: CharmmMRParser.Dihedral_statementContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by CharmmMRParser#dihedral_assign.
    def enterDihedral_assign(self, ctx: CharmmMRParser.Dihedral_assignContext):  # pylint: disable=unused-argument
        self.dihedRestraints += 1

        self.atomSelectionSet.clear()
        self.__g.clear()

    # Exit a parse tree produced by CharmmMRParser#dihedral_assign.
    def exitDihedral_assign(self, ctx: CharmmMRParser.Dihedral_assignContext):  # pylint: disable=unused-argument
        if ctx.selection(0):
            pass

        elif ctx.ByNumber():
            if self.__atomNumberDict is None:
                self.__f.append(f"[Unsupported data] {self.__getCurrentRestraint()}"
                                "The 'bynumber' clause has no effect "
                                "because CHARMM CRD file is not provided.")
            else:
                for col in range(4):
                    ai = int(str(ctx.Integer(col)))
                    if ai in self.__atomNumberDict:
                        atomSelection = [copy.copy(self.__atomNumberDict[ai])]
                        self.atomSelectionSet.append(atomSelection)
                    else:
                        self.__f.append(f"[Missing data] {self.__getCurrentRestraint()}"
                                        f"'{ai}' is not defined in the CHARMM CRD file.")

        elif ctx.Simple_name(0) and ctx.Integer(0):
            if ctx.Simple_name(4):
                for col in range(4):
                    self.factor = {'chain_id': [str(ctx.Simple_name(col * 2))],
                                   'seq_id': [int(str(ctx.Integer(col)))],
                                   'atom_id': [str(ctx.Simple_name(col * 2 + 1))]}
                    self.factor = self.__consumeFactor_expressions(self.factor, 'atom-spec', True)
                    atomSelection = self.factor['atom_selection'] if 'atom_selection' in self.factor else []
                    self.atomSelectionSet.append(atomSelection)
            else:
                for col in range(4):
                    self.factor = {'seq_id': [int(str(ctx.Integer(col)))],
                                   'atom_id': [str(ctx.Simple_name(col))]}
                    atomSelection = self.factor['atom_selection'] if 'atom_selection' in self.factor else []
                    self.atomSelectionSet.append(atomSelection)

    def validateAngleRange(self, weight: float, misc_dict: dict, target_value: Optional[float],
                           lower_limit: Optional[float], upper_limit: Optional[float],
                           lower_linear_limit: Optional[float] = None, upper_linear_limit: Optional[float] = None) -> Optional[dict]:
        """ Validate angle value range.
        """

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

        if isinstance(misc_dict, dict):
            for k, v in misc_dict.items():
                dstFunc[k] = v

        if target_value is not None:
            if ANGLE_ERROR_MIN < target_value < ANGLE_ERROR_MAX:
                dstFunc['target_value'] = f"{target_value}"
            else:
                validRange = False
                self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                f"The target value='{target_value}' must be within range {ANGLE_RESTRAINT_ERROR}.")

        if lower_limit is not None:
            if ANGLE_ERROR_MIN <= lower_limit < ANGLE_ERROR_MAX:
                dstFunc['lower_limit'] = f"{lower_limit:.3f}"
            else:
                validRange = False
                self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                f"The lower limit value='{lower_limit:.3f}' must be within range {ANGLE_RESTRAINT_ERROR}.")

        if upper_limit is not None:
            if ANGLE_ERROR_MIN < upper_limit <= ANGLE_ERROR_MAX:
                dstFunc['upper_limit'] = f"{upper_limit:.3f}"
            else:
                validRange = False
                self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                f"The upper limit value='{upper_limit:.3f}' must be within range {ANGLE_RESTRAINT_ERROR}.")

        if lower_linear_limit is not None:
            if ANGLE_ERROR_MIN <= lower_linear_limit < ANGLE_ERROR_MAX:
                dstFunc['lower_linear_limit'] = f"{lower_linear_limit:.3f}"
            else:
                validRange = False
                self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                f"The lower linear limit value='{lower_linear_limit:.3f}' must be within range {ANGLE_RESTRAINT_ERROR}.")

        if upper_linear_limit is not None:
            if ANGLE_ERROR_MIN < upper_linear_limit <= ANGLE_ERROR_MAX:
                dstFunc['upper_linear_limit'] = f"{upper_linear_limit:.3f}"
            else:
                validRange = False
                self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                f"The upper linear limit value='{upper_linear_limit:.3f}' must be within range {ANGLE_RESTRAINT_ERROR}.")

        if None not in (lower_limit, lower_linear_limit):
            if lower_linear_limit > lower_limit:
                validRange = False
                self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                f"The lower linear limit value='{lower_linear_limit:.3f}' must be less than the lower limit value '{lower_limit:.3f}'.")

        if None not in (upper_limit, upper_linear_limit):
            if upper_limit > upper_linear_limit:
                validRange = False
                self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                f"The upper limit value='{upper_limit:.3f}' must be less than the upper linear limit value '{upper_linear_limit:.3f}'.")

        if not validRange:
            return None

        if target_value is not None:
            if ANGLE_RANGE_MIN <= target_value <= ANGLE_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                f"The target value='{target_value}' should be within range {ANGLE_RESTRAINT_RANGE}.")

        if lower_limit is not None:
            if ANGLE_RANGE_MIN <= lower_limit <= ANGLE_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                f"The lower limit value='{lower_limit:.3f}' should be within range {ANGLE_RESTRAINT_RANGE}.")

        if upper_limit is not None:
            if ANGLE_RANGE_MIN <= upper_limit <= ANGLE_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                f"The upper limit value='{upper_limit:.3f}' should be within range {ANGLE_RESTRAINT_RANGE}.")

        if lower_linear_limit is not None:
            if ANGLE_RANGE_MIN <= lower_linear_limit <= ANGLE_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                f"The lower linear limit value='{lower_linear_limit:.3f}' should be within range {ANGLE_RESTRAINT_RANGE}.")

        if upper_linear_limit is not None:
            if ANGLE_RANGE_MIN <= upper_linear_limit <= ANGLE_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                f"The upper linear limit value='{upper_linear_limit:.3f}' should be within range {ANGLE_RESTRAINT_RANGE}.")

        if target_value is None and lower_limit is None and upper_limit is None and lower_linear_limit is None and upper_linear_limit is None:
            return None

        if None not in (upper_limit, lower_limit)\
           and (PLANE_LIKE_LOWER_LIMIT <= lower_limit < 0.0 < upper_limit <= PLANE_LIKE_UPPER_LIMIT
                or PLANE_LIKE_LOWER_LIMIT <= lower_limit - 180.0 < 0.0 < upper_limit - 180.0 <= PLANE_LIKE_UPPER_LIMIT
                or PLANE_LIKE_LOWER_LIMIT <= lower_limit - 360.0 < 0.0 < upper_limit - 360.0 <= PLANE_LIKE_UPPER_LIMIT):
            dstFunc['plane_like'] = True

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

    # Enter a parse tree produced by CharmmMRParser#harmonic_statement.
    def enterHarmonic_statement(self, ctx: CharmmMRParser.Harmonic_statementContext):  # pylint: disable=unused-argument
        self.geoRestraints += 1

        self.atomSelectionSet.clear()
        self.__g.clear()

    # Exit a parse tree produced by CharmmMRParser#harmonic_statement.
    def exitHarmonic_statement(self, ctx: CharmmMRParser.Harmonic_statementContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by CharmmMRParser#absolute_spec.
    def enterAbsolute_spec(self, ctx: CharmmMRParser.Absolute_specContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by CharmmMRParser#absolute_spec.
    def exitAbsolute_spec(self, ctx: CharmmMRParser.Absolute_specContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by CharmmMRParser#force_const_spec.
    def enterForce_const_spec(self, ctx: CharmmMRParser.Force_const_specContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by CharmmMRParser#force_const_spec.
    def exitForce_const_spec(self, ctx: CharmmMRParser.Force_const_specContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by CharmmMRParser#bestfit_spec.
    def enterBestfit_spec(self, ctx: CharmmMRParser.Bestfit_specContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by CharmmMRParser#bestfit_spec.
    def exitBestfit_spec(self, ctx: CharmmMRParser.Bestfit_specContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by CharmmMRParser#coordinate_spec.
    def enterCoordinate_spec(self, ctx: CharmmMRParser.Coordinate_specContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by CharmmMRParser#coordinate_spec.
    def exitCoordinate_spec(self, ctx: CharmmMRParser.Coordinate_specContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by CharmmMRParser#ic_statement.
    def enterIc_statement(self, ctx: CharmmMRParser.Ic_statementContext):  # pylint: disable=unused-argument
        self.geoRestraints += 1

        self.atomSelectionSet.clear()
        self.__g.clear()

    # Exit a parse tree produced by CharmmMRParser#ic_statement.
    def exitIc_statement(self, ctx: CharmmMRParser.Ic_statementContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by CharmmMRParser#droplet_statement.
    def enterDroplet_statement(self, ctx: CharmmMRParser.Droplet_statementContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by CharmmMRParser#droplet_statement.
    def exitDroplet_statement(self, ctx: CharmmMRParser.Droplet_statementContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by CharmmMRParser#fix_atom_statement.
    def enterFix_atom_statement(self, ctx: CharmmMRParser.Fix_atom_statementContext):  # pylint: disable=unused-argument
        self.geoRestraints += 1

        self.atomSelectionSet.clear()
        self.__g.clear()

    # Exit a parse tree produced by CharmmMRParser#fix_atom_statement.
    def exitFix_atom_statement(self, ctx: CharmmMRParser.Fix_atom_statementContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by CharmmMRParser#center_of_mass_statement.
    def enterCenter_of_mass_statement(self, ctx: CharmmMRParser.Center_of_mass_statementContext):  # pylint: disable=unused-argument
        self.geoRestraints += 1

        self.atomSelectionSet.clear()
        self.__g.clear()

    # Exit a parse tree produced by CharmmMRParser#center_of_mass_statement.
    def exitCenter_of_mass_statement(self, ctx: CharmmMRParser.Center_of_mass_statementContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by CharmmMRParser#fix_bond_or_angle_statement.
    def enterFix_bond_or_angle_statement(self, ctx: CharmmMRParser.Fix_bond_or_angle_statementContext):  # pylint: disable=unused-argument
        self.geoRestraints += 1

        self.atomSelectionSet.clear()
        self.__g.clear()

    # Exit a parse tree produced by CharmmMRParser#fix_bond_or_angle_statement.
    def exitFix_bond_or_angle_statement(self, ctx: CharmmMRParser.Fix_bond_or_angle_statementContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by CharmmMRParser#shake_opt.
    def enterShake_opt(self, ctx: CharmmMRParser.Shake_optContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by CharmmMRParser#shake_opt.
    def exitShake_opt(self, ctx: CharmmMRParser.Shake_optContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by CharmmMRParser#fast_opt.
    def enterFast_opt(self, ctx: CharmmMRParser.Fast_optContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by CharmmMRParser#fast_opt.
    def exitFast_opt(self, ctx: CharmmMRParser.Fast_optContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by CharmmMRParser#restrained_distance_statement.
    def enterRestrained_distance_statement(self, ctx: CharmmMRParser.Restrained_distance_statementContext):  # pylint: disable=unused-argument
        self.geoRestraints += 1

        self.atomSelectionSet.clear()
        self.__g.clear()

    # Exit a parse tree produced by CharmmMRParser#restrained_distance_statement.
    def exitRestrained_distance_statement(self, ctx: CharmmMRParser.Restrained_distance_statementContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by CharmmMRParser#external_force_statement.
    def enterExternal_force_statement(self, ctx: CharmmMRParser.External_force_statementContext):  # pylint: disable=unused-argument
        self.geoRestraints += 1

        self.atomSelectionSet.clear()
        self.__g.clear()

    # Exit a parse tree produced by CharmmMRParser#external_force_statement.
    def exitExternal_force_statement(self, ctx: CharmmMRParser.External_force_statementContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by CharmmMRParser#rmsd_statement.
    def enterRmsd_statement(self, ctx: CharmmMRParser.Rmsd_statementContext):  # pylint: disable=unused-argument
        self.geoRestraints += 1

        self.atomSelectionSet.clear()
        self.__g.clear()

    # Exit a parse tree produced by CharmmMRParser#rmsd_statement.
    def exitRmsd_statement(self, ctx: CharmmMRParser.Rmsd_statementContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by CharmmMRParser#rmsd_orient_spec.
    def enterRmsd_orient_spec(self, ctx: CharmmMRParser.Rmsd_orient_specContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by CharmmMRParser#rmsd_orient_spec.
    def exitRmsd_orient_spec(self, ctx: CharmmMRParser.Rmsd_orient_specContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by CharmmMRParser#rmsd_force_const_spec.
    def enterRmsd_force_const_spec(self, ctx: CharmmMRParser.Rmsd_force_const_specContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by CharmmMRParser#rmsd_force_const_spec.
    def exitRmsd_force_const_spec(self, ctx: CharmmMRParser.Rmsd_force_const_specContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by CharmmMRParser#rmsd_coordinate_spec.
    def enterRmsd_coordinate_spec(self, ctx: CharmmMRParser.Rmsd_coordinate_specContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by CharmmMRParser#rmsd_coordinate_spec.
    def exitRmsd_coordinate_spec(self, ctx: CharmmMRParser.Rmsd_coordinate_specContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by CharmmMRParser#gyration_statement.
    def enterGyration_statement(self, ctx: CharmmMRParser.Gyration_statementContext):  # pylint: disable=unused-argument
        self.geoRestraints += 1

        self.atomSelectionSet.clear()
        self.__g.clear()

    # Exit a parse tree produced by CharmmMRParser#gyration_statement.
    def exitGyration_statement(self, ctx: CharmmMRParser.Gyration_statementContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by CharmmMRParser#distance_matrix_statement.
    def enterDistance_matrix_statement(self, ctx: CharmmMRParser.Distance_matrix_statementContext):  # pylint: disable=unused-argument
        self.geoRestraints += 1

        self.atomSelectionSet.clear()
        self.__g.clear()

    # Exit a parse tree produced by CharmmMRParser#distance_matrix_statement.
    def exitDistance_matrix_statement(self, ctx: CharmmMRParser.Distance_matrix_statementContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by CharmmMRParser#selection.
    def enterSelection(self, ctx: CharmmMRParser.SelectionContext):  # pylint: disable=unused-argument
        if self.__sel_expr_debug:
            print("  " * self.depth + "enter_selection")

        if self.depth == 0:
            self.stackSelections = []
            self.stackTerms = []
            self.factor = {}

    # Exit a parse tree produced by CharmmMRParser#selection.
    def exitSelection(self, ctx: CharmmMRParser.SelectionContext):  # pylint: disable=unused-argument
        if self.__sel_expr_debug:
            print("  " * self.depth + "exit_selection")

        if 'or' in self.stackSelections:
            top_union_exprs = self.stackSelections.count('or')

            unionSelections = []
            unionSelections.append(None)
            unionId = 0

            for _selection in self.stackSelections:

                if _selection is None:
                    continue

                if isinstance(_selection, str) and _selection == 'or':

                    if unionId == top_union_exprs - 1:
                        break

                    unionSelections.append(None)
                    unionId += 1

                    continue

                if unionSelections[unionId] is None:
                    unionSelections[unionId] = []

                unionSelections[unionId].append(_selection)

            self.stackSelections.clear()

            unionAtomSelection = []

            for stackSelections in unionSelections:

                if stackSelections is None:
                    continue

                if 'and' not in stackSelections:

                    atomSelection = stackSelections.pop() if stackSelections else []

                    while stackSelections:
                        _selection = stackSelections.pop()
                        if _selection is not None:
                            atomSelection = self.__intersectionAtom_selections(_selection, atomSelection)

                else:

                    blockSelections = []
                    blockSelections.append(None)
                    blockId = 0

                    for _selection in stackSelections:

                        if _selection is None:
                            continue

                        if isinstance(_selection, str) and _selection == 'and':
                            blockSelections.append(None)
                            blockId += 1
                            continue

                        if blockSelections[blockId] is None:
                            blockSelections[blockId] = _selection

                        else:
                            for _atom in _selection:
                                if _atom not in blockSelections[blockId]:
                                    blockSelections[blockId].append(_atom)

                    stackSelections.clear()

                    atomSelection = blockSelections.pop()

                    while blockSelections:
                        atomSelection = self.__intersectionAtom_selections(blockSelections.pop(), atomSelection)

                if len(atomSelection) > 0:
                    unionAtomSelection.extend(atomSelection)

            atomSelection = unionAtomSelection

            if '*' in atomSelection:
                atomSelection.remove('*')

            if self.__createSfDict:
                atomSelection = sorted(atomSelection, key=itemgetter('chain_id', 'seq_id', 'atom_id'))

            if self.__sel_expr_debug:
                print("  " * self.depth + f"atom selection: {atomSelection}")

            self.atomSelectionSet.append(atomSelection)

            return

        if 'and' not in self.stackSelections:

            atomSelection = self.stackSelections.pop() if self.stackSelections else []

            while self.stackSelections:
                _selection = self.stackSelections.pop()
                if _selection is not None:
                    if self.__con_union_expr:
                        for _atom in _selection:
                            if _atom not in atomSelection:
                                atomSelection.append(_atom)
                    else:
                        atomSelection = self.__intersectionAtom_selections(_selection, atomSelection)

        else:

            blockSelections = []
            blockSelections.append(None)
            blockId = 0

            for _selection in self.stackSelections:

                if _selection is None:
                    continue

                if isinstance(_selection, str) and _selection == 'and':
                    blockSelections.append(None)
                    blockId += 1
                    continue

                if blockSelections[blockId] is None:
                    blockSelections[blockId] = _selection

                else:
                    for _atom in _selection:
                        if _atom not in blockSelections[blockId]:
                            blockSelections[blockId].append(_atom)

            self.stackSelections.clear()

            atomSelection = blockSelections.pop()

            while blockSelections:
                atomSelection = self.__intersectionAtom_selections(blockSelections.pop(), atomSelection)

        while self.stackSelections:
            _selection = self.stackSelections.pop()
            if _selection is not None:
                for _atom in _selection:
                    if _atom not in atomSelection:
                        atomSelection.append(_atom)

        if '*' in atomSelection:
            atomSelection.remove('*')

        if self.__createSfDict:
            atomSelection = sorted(atomSelection, key=itemgetter('chain_id', 'seq_id', 'atom_id'))

        if self.__sel_expr_debug:
            print("  " * self.depth + f"atom selection: {atomSelection}")

        self.atomSelectionSet.append(atomSelection)

    # Enter a parse tree produced by CharmmMRParser#selection_expression.
    def enterSelection_expression(self, ctx: CharmmMRParser.Selection_expressionContext):
        self.__cur_union_expr = self.__con_union_expr = bool(ctx.Or_op(0))
        if self.depth == 0:
            self.__top_union_expr = self.__cur_union_expr

        if self.depth > 0 and self.__cur_union_expr:
            self.unionFactor = {}

        if self.__sel_expr_debug:
            print("  " * self.depth + f"enter_sel_expr, union: {self.__cur_union_expr}")

        if self.depth > 0 and len(self.factor) > 0:
            if 'atom_selection' not in self.factor:
                self.consumeFactor_expressions(cifCheck=True)
            if 'atom_selection' in self.factor:
                self.stackSelections.append(self.factor['atom_selection'])
                self.stackSelections.append('and')  # intersection

        self.depth += 1

    # Exit a parse tree produced by CharmmMRParser#selection_expression.
    def exitSelection_expression(self, ctx: CharmmMRParser.Selection_expressionContext):  # pylint: disable=unused-argument
        self.depth -= 1
        if self.__sel_expr_debug:
            print("  " * self.depth + "exit_sel_expr")

        _atomSelection = []
        while self.stackTerms:
            _term = self.stackTerms.pop()
            if _term is not None:
                _atomSelection.extend(_term)

        atomSelection = [dict(s) for s in set(frozenset(atom.items())
                                              for atom in _atomSelection
                                              if isinstance(atom, dict))] if len(_atomSelection) > 1 else _atomSelection

        if len(atomSelection) > 0:
            if self.depth == 0 and not self.__top_union_expr:
                self.stackSelections.append(atomSelection)
            elif self.depth > 0 and self.__top_union_expr and not self.__cur_union_expr:
                if len(self.stackSelections) > 0 and isinstance(self.stackSelections[-1], str):
                    self.stackSelections.append(atomSelection)
            else:
                self.stackSelections.append(atomSelection)

        if self.depth == 0 or not self.__top_union_expr:
            self.factor = {}

        if self.__cur_union_expr:
            self.__cur_union_expr = False
        if self.__con_union_expr and self.depth == 0:
            self.__con_union_expr = False
            self.unionFactor = None

    # Enter a parse tree produced by CharmmMRParser#term.
    def enterTerm(self, ctx: CharmmMRParser.TermContext):
        if self.__sel_expr_debug:
            print("  " * self.depth + f"enter_term, intersection: {bool(ctx.And_op(0))}")

        self.stackFactors = []
        self.factor = {}

        self.depth += 1

    # Exit a parse tree produced by CharmmMRParser#term.
    def exitTerm(self, ctx: CharmmMRParser.TermContext):  # pylint: disable=unused-argument
        self.depth -= 1
        if self.__sel_expr_debug:
            print("  " * self.depth + "exit_term")

        if self.depth == 1 and self.__top_union_expr:

            if self.stackFactors:
                while self.stackFactors:
                    _factor = self.__consumeFactor_expressions(self.stackFactors.pop(), cifCheck=True)
                    self.factor = self.__intersectionFactor_expressions(self.factor,
                                                                        None if 'atom_selection' not in _factor
                                                                        or isinstance(_factor['atom_selection'], str)
                                                                        else _factor['atom_selection'])
            else:
                self.factor = self.__consumeFactor_expressions(self.factor, cifCheck=True)

            if 'atom_selection' in self.factor:
                self.stackTerms.append(self.factor['atom_selection'])

            _atomSelection = []
            while self.stackTerms:
                _term = self.stackTerms.pop()
                if _term is not None and not isinstance(_term, str):
                    _atomSelection.extend(_term)

            atomSelection = [dict(s) for s in set(frozenset(atom.items())
                                                  for atom in _atomSelection
                                                  if isinstance(atom, dict))] if len(_atomSelection) > 1 else _atomSelection

            if len(atomSelection) > 0:
                self.stackSelections.append(atomSelection)

            self.stackSelections.append('or')  # union

            self.stackTerms = []
            self.stackFactors = []
            self.factor = {}

            return

        if self.depth == 1 or not self.__top_union_expr:
            while self.stackFactors:
                _factor = self.__consumeFactor_expressions(self.stackFactors.pop(), cifCheck=True)
                self.factor = self.__intersectionFactor_expressions(self.factor, _factor.get('atom_selection'))

        if self.unionFactor is not None and len(self.unionFactor) > 0:
            if 'atom_selection' not in self.unionFactor:
                self.unionFactor = self.__consumeFactor_expressions(self.unionFactor, cifCheck=True)
            if 'atom_selection' in self.unionFactor:
                _atomSelection = self.unionFactor['atom_selection']
                del self.unionFactor['atom_selection']
                __factor = self.__consumeFactor_expressions(self.unionFactor, cifCheck=True)
                if 'atom_selection' in __factor:
                    for _atom in __factor['atom_selection']:
                        if _atom not in _atomSelection:
                            _atomSelection.append(_atom)
                if len(_atomSelection) > 0:
                    self.factor['atom_selection'] = _atomSelection
            self.unionFactor = None

        if 'atom_selection' in self.factor and not isinstance(self.factor['atom_selection'], str):
            self.stackTerms.append(self.factor['atom_selection'])

    def consumeFactor_expressions(self, clauseName: str = 'atom selection expression', cifCheck: bool = True):
        """ Consume factor expressions as atom selection if possible.
        """

        if self.stackFactors:
            self.stackFactors.pop()

        self.factor = self.__consumeFactor_expressions(self.factor, clauseName, cifCheck)

    def __consumeFactor_expressions(self, _factor: dict, clauseName: str = 'atom selection expression', cifCheck: bool = True, trial: int = 1) -> dict:
        """ Consume factor expressions as atom selection if possible.
        """

        if not self.__hasPolySeq and not self.__hasNonPolySeq:
            return _factor

        if not self.__hasCoord:
            cifCheck = False

        if 'atom_num' in _factor and 'atom_id' not in _factor:
            g = None
            if self.lastComment is not None:
                if self.__cur_subtype == 'dist':
                    if self.dist_comment_pat.match(self.lastComment):
                        g = self.dist_comment_pat.search(self.lastComment).groups()
                        offset = len(self.atomSelectionSet) * 3
                        # _factor['comp_id'] = [g[offset]]
                        _factor['seq_id'] = [int(g[offset + 1])]
                        _factor['atom_id'] = [g[offset + 2]]
                        _factor['chain_id'] = [ps['auth_chain_id'] for ps in self.__polySeq if _factor['seq_id'][0] in ps['seq_id']]
                        if self.__hasNonPolySeq:
                            for np in self.__nonPolySeq:
                                _chainId = np['auth_chain_id']
                                if _chainId not in _factor['chain_id'] and _factor['seq_id'][0] in np['seq_id']:
                                    _factor['chain_id'].append(_chainId)
                        if len(_factor['chain_id']) == 0:
                            del _factor['chain_id']
                    elif self.dist_comment_pat2.match(self.lastComment):
                        g = self.dist_comment_pat2.search(self.lastComment).groups()
                        offset = len(self.atomSelectionSet) * 4
                        _factor['chain_id'] = [g[offset]]
                        # _factor['comp_id'] = [g[offset + 1]]
                        _factor['seq_id'] = [int(g[offset + 2])]
                        _factor['atom_id'] = [g[offset + 3]]
                elif self.__cur_subtype == 'dihed':
                    if self.dihed_comment_pat.match(self.lastComment):
                        g = self.dihed_comment_pat.search(self.lastComment).groups()
                        offset = len(self.atomSelectionSet) * 3
                        # _factor['comp_id'] = [g[offset]]
                        _factor['seq_id'] = [int(g[offset + 1])]
                        _factor['atom_id'] = [g[offset + 2]]
                        _factor['chain_id'] = [ps['auth_chain_id'] for ps in self.__polySeq if _factor['seq_id'][0] in ps['seq_id']]
                        if self.__hasNonPolySeq:
                            for np in self.__nonPolySeq:
                                _chainId = np['auth_chain_id']
                                if _chainId not in _factor['chain_id'] and _factor['seq_id'][0] in np['seq_id']:
                                    _factor['chain_id'].append(_chainId)
                        if len(_factor['chain_id']) == 0:
                            del _factor['chain_id']
            if g is None:
                _factor['atom_id'] = [None]
                if 'chain_id' in _factor:
                    del _factor['chain_id']
                if 'seq_id' in _factor:
                    del _factor['seq_id']

                self.__f.append(f"[Unsupported data] {self.__getCurrentRestraint()}"
                                "The 'bynumber' clause has no effect "
                                "because CHARMM CRD file is not provided.")

                return _factor

        if ('atom_id' in _factor and _factor['atom_id'][0] is None)\
           or ('atom_selection' in _factor and (_factor['atom_selection'] is None or len(_factor['atom_selection']) == 0)):
            return {'atom_selection': []}

        if not any(key for key in _factor if not (key == 'atom_selection' or key.startswith('auth'))):
            return _factor

        if 'alt_chain_id' in _factor:
            len_factor = len(_factor)

            if len_factor == 2 and 'chain_id' in _factor and len(_factor['chain_id']) == 0:
                if self.__largeModel:
                    _factor['chain_id'] = [self.__representativeAsymId]
                else:
                    _factor['atom_selection'] = ['*']
                    del _factor['chain_id']
                    return _factor

            elif len_factor == 1:
                _factor['atom_selection'] = ['*']
                return _factor

            self.__failure_chain_ids.clear()

        self.__retrieveLocalSeqScheme()

        if 'atom_id' in _factor and len(_factor['atom_id']) == 1:
            self.__cur_auth_atom_id = _factor['atom_id'][0]
        elif 'atom_ids' in _factor and len(_factor['atom_ids']) == 1:
            self.__cur_auth_atom_id = _factor['atom_ids'][0]
        else:
            self.__cur_auth_atom_id = ''

        ambigAtomSelect = False
        if 'atom_id' not in _factor and 'atom_ids' not in _factor\
           and 'type_symbol' not in _factor and 'type_symbols' not in _factor:
            _factor['atom_not_specified'] = True
            if 'atom_selection' not in _factor:
                ambigAtomSelect = True

        elif 'chain_id' not in _factor and 'seq_id' not in _factor and 'seq_ids' not in _factor:
            if 'atom_selection' not in _factor:
                ambigAtomSelect = True

        if 'seq_id' not in _factor and 'seq_ids' not in _factor:
            _factor['seq_not_specified'] = True

        key = str(_factor)
        if key in self.__cachedDictForFactor:
            return copy.deepcopy(self.__cachedDictForFactor[key])

        unambig = self.__cur_subtype != 'dist'

        len_warn_msg = len(self.__f)

        chain_not_specified = np_chain_not_specified = 'alt_chain_id' not in _factor
        if 'chain_id' not in _factor or len(_factor['chain_id']) == 0:
            if self.__largeModel:
                _factor['chain_id'] = [self.__representativeAsymId]
            else:
                _factor['chain_id'] = [ps['auth_chain_id'] for ps in self.__polySeq]
                if self.__hasNonPolySeq:
                    for np in self.__nonPolySeq:
                        _chainId = np['auth_chain_id']
                        if _chainId not in _factor['chain_id']:
                            _factor['chain_id'].append(_chainId)
                if len(_factor['chain_id']) == 1:
                    chain_not_specified = False
        elif len(_factor['chain_id']) == 1:
            if chain_not_specified and any(ps for ps in self.__polySeq if ps['auth_chain_id'] == _factor['chain_id'][0]):
                _factor['auth_chain_id'] = _factor['chain_id']
                chain_not_specified = False
            if self.__hasNonPolySeq and np_chain_not_specified:
                if any(np for np in self.__nonPolySeq if np['auth_chain_id'] == _factor['chain_id'][0]):
                    _factor['auth_chain_id'] = _factor['chain_id']
                    np_chain_not_specified = False
                elif not chain_not_specified and any(np for np in self.__nonPolySeq if np['chain_id'] == _factor['chain_id'][0]):
                    _factor['auth_chain_id'] = _factor['chain_id']
                    np_chain_not_specified = False

        if self.__complexSeqScheme and self.__reasons is not None and 'inhibit_label_seq_scheme_stats' in self.__reasons\
           and not chain_not_specified and _factor['chain_id'][0] in self.__reasons['inhibit_label_seq_scheme_stats']:
            self.__preferAuthSeq = True

        if 'seq_id' not in _factor and 'seq_ids' not in _factor:
            if 'comp_ids' in _factor and len(_factor['comp_ids']) > 0\
               and ('comp_id' not in _factor or len(_factor['comp_id']) == 0):
                lenCompIds = len(_factor['comp_ids'])
                _compIdSelect = set()
                for chainId in _factor['chain_id']:
                    ps = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == chainId), None)
                    if ps is not None:
                        for realSeqId in ps['auth_seq_id']:
                            if realSeqId is None:
                                continue
                            idx = ps['auth_seq_id'].index(realSeqId)
                            realCompId = ps['comp_id'][idx]
                            origCompId = ps['auth_comp_id'][idx]
                            if (lenCompIds == 1
                                and (re.match(toRegEx(translateToStdResName(_factor['comp_ids'][0], realCompId, self.__ccU)), realCompId)
                                     or re.match(toRegEx(translateToStdResName(_factor['comp_ids'][0], realCompId, self.__ccU)), origCompId)))\
                               or (lenCompIds == 2
                                   and (translateToStdResName(_factor['comp_ids'][0], realCompId, self.__ccU) <= realCompId
                                        <= translateToStdResName(_factor['comp_ids'][1], realCompId, self.__ccU)
                                        or translateToStdResName(_factor['comp_ids'][0], realCompId, self.__ccU) <= origCompId
                                        <= translateToStdResName(_factor['comp_ids'][1], realCompId, self.__ccU))):
                                _compIdSelect.add(realCompId)
                if self.__hasNonPolySeq:
                    for chainId in _factor['chain_id']:
                        npList = [np for np in self.__nonPolySeq if np['auth_chain_id'] == chainId]
                        for np in npList:
                            for realSeqId in np['auth_seq_id']:
                                if realSeqId is None:
                                    continue
                                idx = np['auth_seq_id'].index(realSeqId)
                                realCompId = self.getRealCompId(np['comp_id'][idx])
                                origCompId = np['auth_comp_id'][idx]
                                if (lenCompIds == 1
                                    and (re.match(toRegEx(translateToStdResName(_factor['comp_ids'][0], realCompId, self.__ccU)), realCompId)
                                         or re.match(toRegEx(translateToStdResName(_factor['comp_ids'][0], realCompId, self.__ccU)), origCompId)))\
                                   or (lenCompIds == 2
                                       and (translateToStdResName(_factor['comp_ids'][0], realCompId, self.__ccU) <= realCompId
                                            <= translateToStdResName(_factor['comp_ids'][1], realCompId, self.__ccU)
                                            or translateToStdResName(_factor['comp_ids'][0], realCompId, self.__ccU) <= origCompId
                                            <= translateToStdResName(_factor['comp_ids'][1], realCompId, self.__ccU))):
                                    _compIdSelect.add(realCompId)
                _factor['comp_id'] = list(_compIdSelect)
                del _factor['comp_ids']

        if 'seq_ids' in _factor and len(_factor['seq_ids']) > 0\
           and ('seq_id' not in _factor or len(_factor['seq_id']) == 0):
            seqId = _factor['seq_ids'][0]
            _seqId = toRegEx(seqId)
            seqIds = []
            for chainId in _factor['chain_id']:
                ps = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == chainId), None)
                if ps is not None:
                    found = False
                    for realSeqId in ps['auth_seq_id']:
                        if realSeqId is None:
                            continue
                        if 'comp_id' in _factor and len(_factor['comp_id']) > 0:
                            idx = ps['auth_seq_id'].index(realSeqId)
                            realCompId = ps['comp_id'][idx]
                            origCompId = ps['auth_comp_id'][idx]
                            _compIdList = [translateToStdResName(_compId, realCompId, self.__ccU) for _compId in _factor['comp_id']]
                            if realCompId not in _compIdList and origCompId not in _compIdList:
                                continue
                            if set(_factor['comp_id']) != set(_compIdList):
                                _factor['alt_comp_id'] = _factor['comp_id']
                                _factor['comp_id'] = _compIdList
                        if re.match(_seqId, str(realSeqId)):
                            seqIds.append(realSeqId)
                            found = True
                    if not found:
                        for realSeqId in ps['auth_seq_id']:
                            if realSeqId is None:
                                continue
                            if 'comp_id' in _factor and len(_factor['comp_id']) > 0:
                                idx = ps['auth_seq_id'].index(realSeqId)
                                realCompId = ps['comp_id'][idx]
                                origCompId = ps['auth_comp_id'][idx]
                                _compIdList = [translateToStdResName(_compId, realCompId, self.__ccU) for _compId in _factor['comp_id']]
                                if realCompId not in _compIdList and origCompId not in _compIdList:
                                    continue
                                if set(_factor['comp_id']) != set(_compIdList):
                                    _factor['alt_comp_id'] = _factor['comp_id']
                                    _factor['comp_id'] = _compIdList
                            seqKey = (chainId, realSeqId)
                            if seqKey in self.__authToLabelSeq:
                                _, realSeqId = self.__authToLabelSeq[seqKey]
                                if re.match(_seqId, str(realSeqId)):
                                    seqIds.append(realSeqId)
            if self.__hasNonPolySeq:
                for chainId in _factor['chain_id']:
                    npList = [np for np in self.__nonPolySeq if np['auth_chain_id'] == chainId]
                    for np in npList:
                        found = False
                        for realSeqId in np['auth_seq_id']:
                            if realSeqId is None:
                                continue
                            if 'comp_id' in _factor and len(_factor['comp_id']) > 0:
                                idx = np['auth_seq_id'].index(realSeqId)
                                realCompId = self.getRealCompId(np['comp_id'][idx])
                                origCompId = np['auth_comp_id'][idx]
                                _compIdList = [translateToStdResName(_compId, realCompId, self.__ccU) for _compId in _factor['comp_id']]
                                if realCompId not in _compIdList and origCompId not in _compIdList:
                                    continue
                                if set(_factor['comp_id']) != set(_compIdList):
                                    _factor['alt_comp_id'] = _factor['comp_id']
                                    _factor['comp_id'] = _compIdList
                            if re.match(_seqId, str(realSeqId)):
                                seqIds.append(realSeqId)
                                found = True
                        if not found:
                            for realSeqId in np['auth_seq_id']:
                                if realSeqId is None:
                                    continue
                                if 'comp_id' in _factor and len(_factor['comp_id']) > 0:
                                    idx = np['auth_seq_id'].index(realSeqId)
                                    realCompId = self.getRealCompId(np['comp_id'][idx])
                                    origCompId = np['auth_comp_id'][idx]
                                    _compIdList = [translateToStdResName(_compId, realCompId, self.__ccU) for _compId in _factor['comp_id']]
                                    if realCompId not in _compIdList and origCompId not in _compIdList:
                                        continue
                                    if set(_factor['comp_id']) != set(_compIdList):
                                        _factor['alt_comp_id'] = _factor['comp_id']
                                        _factor['comp_id'] = _compIdList
                                seqKey = (chainId, realSeqId)
                                if seqKey in self.__authToLabelSeq:
                                    _, realSeqId = self.__authToLabelSeq[seqKey]
                                    if re.match(_seqId, str(realSeqId)):
                                        seqIds.append(realSeqId)
            _factor['seq_id'] = list(set(seqIds))
            del _factor['seq_ids']

        if 'seq_id' not in _factor or len(_factor['seq_id']) == 0:
            seqIds = []
            for chainId in _factor['chain_id']:
                ps = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == chainId), None)
                if ps is not None:
                    for realSeqId in ps['auth_seq_id']:
                        if realSeqId is None:
                            continue
                        if 'comp_id' in _factor and len(_factor['comp_id']) > 0:
                            idx = ps['auth_seq_id'].index(realSeqId)
                            realCompId = ps['comp_id'][idx]
                            origCompId = ps['auth_comp_id'][idx]
                            _compIdList = [translateToStdResName(_compId, realCompId, self.__ccU) for _compId in _factor['comp_id']]
                            if realCompId not in _compIdList and origCompId not in _compIdList:
                                continue
                            if set(_factor['comp_id']) != set(_compIdList):
                                _factor['alt_comp_id'] = _factor['comp_id']
                                _factor['comp_id'] = _compIdList
                        seqIds.append(realSeqId)
            if self.__hasNonPolySeq:
                for chainId in _factor['chain_id']:
                    npList = [np for np in self.__nonPolySeq if np['auth_chain_id'] == chainId]
                    for np in npList:
                        for realSeqId in np['auth_seq_id']:
                            if realSeqId is None:
                                continue
                            if 'comp_id' in _factor and len(_factor['comp_id']) > 0:
                                idx = np['auth_seq_id'].index(realSeqId)
                                realCompId = self.getRealCompId(np['comp_id'][idx])
                                origCompId = np['auth_comp_id'][idx]
                                _compIdList = [translateToStdResName(_compId, realCompId, self.__ccU) for _compId in _factor['comp_id']]
                                if realCompId not in _compIdList and origCompId not in _compIdList:
                                    continue
                                if set(_factor['comp_id']) != set(_compIdList):
                                    _factor['alt_comp_id'] = _factor['comp_id']
                                    _factor['comp_id'] = _compIdList
                            seqIds.append(realSeqId)
            _factor['seq_id'] = list(set(seqIds))

            if len(_factor['seq_id']) > 0 and 'comp_id' in _factor and 'seq_not_specified' in _factor:  # 2lr1
                del _factor['seq_not_specified']  # 2krf

        if 'atom_id' not in _factor and 'atom_ids' not in _factor:
            if 'type_symbols' in _factor and len(_factor['type_symbols']) > 0\
               and ('type_symbol' not in _factor or len(_factor['type_symbol']) == 0):
                lenTypeSymbols = len(_factor['type_symbols'])
                _typeSymbolSelect = set()
                _compIdSelect = set()
                for chainId in _factor['chain_id']:
                    ps = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == chainId), None)
                    if ps is not None:
                        _compIdSelect |= set(ps['comp_id'])
                if self.__hasNonPolySeq:
                    for chainId in _factor['chain_id']:
                        npList = [np for np in self.__nonPolySeq if np['auth_chain_id'] == chainId]
                        for np in npList:
                            _compIdSelect |= set(np['comp_id'])
                for compId in _compIdSelect:
                    if self.__ccU.updateChemCompDict(compId):
                        for cca in self.__ccU.lastAtomList:
                            realTypeSymbol = cca[self.__ccU.ccaTypeSymbol]
                            if (lenTypeSymbols == 1 and re.match(toRegEx(_factor['type_symbols'][0]), realTypeSymbol))\
                               or (lenTypeSymbols == 2 and _factor['type_symbols'][0] <= realTypeSymbol <= _factor['type_symbols'][1]):
                                _typeSymbolSelect.add(realTypeSymbol)
                _factor['type_symbol'] = list(_typeSymbolSelect)
                if len(_factor['type_symbol']) == 0:
                    _factor['atom_id'] = [None]
                del _factor['type_symbols']

            if 'type_symbol' in _factor:
                _atomIdSelect = set()
                _compIdSelect = set()
                for chainId in _factor['chain_id']:
                    ps = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == chainId), None)
                    if ps is not None:
                        _compIdSelect |= set(ps['comp_id'])
                if self.__hasNonPolySeq:
                    for chainId in _factor['chain_id']:
                        npList = [np for np in self.__nonPolySeq if np['auth_chain_id'] == chainId]
                        for np in npList:
                            _compIdSelect |= set(np['comp_id'])
                for compId in _compIdSelect:
                    if self.__ccU.updateChemCompDict(compId):
                        for cca in self.__ccU.lastAtomList:
                            if cca[self.__ccU.ccaTypeSymbol] in _factor['type_symbol']\
                               and cca[self.__ccU.ccaLeavingAtomFlag] != 'Y':
                                _atomIdSelect.add(cca[self.__ccU.ccaAtomId])

                _factor['atom_id'] = list(_atomIdSelect)
                if len(_factor['atom_id']) == 0:
                    _factor['atom_id'] = [None]

        def get_real_seq_id(ps, real_seq_id):
            chain_id = ps['auth_chain_id']
            _seq_ids = _factor['seq_id']
            _seq_id = _seq_ids[0]

            if not self.__preferAuthSeq:
                if 'label_seq_offset' in self.__reasons\
                   and chain_id in self.__reasons['label_seq_offset']:
                    offset = self.__reasons['label_seq_offset'][chain_id]
                    if _seq_id + offset in ps['seq_id']:
                        return ps['auth_seq_id'][ps['seq_id'].index(_seq_id + offset)]
                elif _seq_id in ps['seq_id']:
                    return ps['auth_seq_id'][ps['seq_id'].index(_seq_id)]
                if 'chain_id_remap' in self.__reasons\
                        and _seq_id in self.__reasons['chain_id_remap']\
                        and chain_id == self.__reasons['chain_id_remap'][_seq_id]['chain_id']:
                    return real_seq_id
                if 'seq_id_remap' in self.__reasons:
                    _, _real_seq_id = retrieveRemappedSeqId(self.__reasons['seq_id_remap'], chain_id, _seq_id)
                    if _real_seq_id == real_seq_id:
                        return real_seq_id
                return None

            if 'global_auth_sequence_offset' in self.__reasons\
               and chain_id in self.__reasons['global_auth_sequence_offset']:
                offset = self.__reasons['global_auth_sequence_offset'][chain_id]
                if real_seq_id in [seq_id + offset for seq_id in _seq_ids]:
                    return real_seq_id
                if isinstance(offset, dict):
                    if real_seq_id in offset:
                        offset = offset[real_seq_id]
                    else:
                        for shift in range(1, 100):
                            if real_seq_id + shift in offset:
                                offset = offset[real_seq_id + shift]
                                break
                            if real_seq_id - shift in offset:
                                offset = offset[real_seq_id - shift]
                                break
                        if isinstance(offset, dict):
                            return None
                if real_seq_id + offset in ps['auth_seq_id']:
                    return real_seq_id + offset
                if offset != 0 and 'gap_in_auth_seq' in ps and ps['gap_in_auth_seq']:
                    for shift in range(1, 100):
                        if real_seq_id + shift + offset in ps['auth_seq_id']:
                            idx = ps['auth_seq_id'].index(real_seq_id + shift + offset) - shift
                            if 0 <= idx < len(ps['auth_seq_id']):
                                return ps['auth_seq_id'][idx]
                        if real_seq_id - shift + offset in ps['auth_seq_id']:
                            idx = ps['auth_seq_id'].index(real_seq_id - shift + offset) + shift
                            if 0 <= idx < len(ps['auth_seq_id']):
                                return ps['auth_seq_id'][idx]

            elif 'global_sequence_offset' in self.__reasons\
                    and chain_id in self.__reasons['global_sequence_offset']:
                offset = self.__reasons['global_sequence_offset'][chain_id]
                if real_seq_id in [seq_id + offset for seq_id in _seq_ids]:
                    return real_seq_id

            elif 'chain_id_remap' in self.__reasons\
                    and _seq_id in self.__reasons['chain_id_remap']\
                    and chain_id == self.__reasons['chain_id_remap'][_seq_id]['chain_id']:
                return real_seq_id

            elif 'seq_id_remap' in self.__reasons:
                _, _real_seq_id = retrieveRemappedSeqId(self.__reasons['seq_id_remap'], chain_id, _seq_id)
                if _real_seq_id == real_seq_id:
                    return real_seq_id

            return None

        def is_real_nucleic_atom_id(real_atom_id, test_atom_id, src_atom_id, candidates):
            if ("'" in test_atom_id and "'" in real_atom_id)\
               or ("'" not in test_atom_id and "'" not in real_atom_id):
                pass

            else:
                if len(test_atom_id) > 1 and test_atom_id[1] != src_atom_id[1]:
                    if "'" in real_atom_id:
                        return False

                else:
                    min_len = min(len(src_atom_id), 2)
                    if real_atom_id.startswith(src_atom_id[:min_len]):
                        if ("'" in src_atom_id and "'" in real_atom_id)\
                           or ("'" not in src_atom_id and "'" not in real_atom_id):
                            pass
                        elif len(candidates) == 1 or (all("'" in a for a in candidates) or all("'" not in a for a in candidates)):
                            pass  # 2lzv
                        else:
                            return False

            if len([_atom_id_ for _atom_id_ in candidates
                    if ("'" in _atom_id_ and "'" in real_atom_id)
                    or ("'" not in _atom_id_ and "'" not in real_atom_id)]) < 2:
                return len(candidates) == 1 or (all("'" in a for a in candidates) or all("'" not in a for a in candidates))  # 2lzv

            return True

        if 'atom_ids' in _factor and len(_factor['atom_ids']) > 0\
           and ('atom_id' not in _factor or len(_factor['atom_id']) == 0):
            lenAtomIds = len(_factor['atom_ids'])
            _compIdSelect = set()
            for chainId in _factor['chain_id']:
                ps = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == chainId), None)
                if ps is not None:
                    for realSeqId in ps['auth_seq_id']:
                        if realSeqId is None:
                            continue
                        if 'seq_id' in _factor and len(_factor['seq_id']) > 0:
                            if self.getOrigSeqId(ps, realSeqId) not in _factor['seq_id']:
                                if self.__reasons is None:
                                    continue
                                realSeqId = get_real_seq_id(ps, realSeqId)
                                if realSeqId is None:
                                    continue
                        idx = ps['auth_seq_id'].index(realSeqId)
                        realCompId = ps['comp_id'][idx]
                        if 'comp_id' in _factor and len(_factor['comp_id']) > 0:
                            origCompId = ps['auth_comp_id'][idx]
                            _compIdList = [translateToStdResName(_compId, realCompId, self.__ccU) for _compId in _factor['comp_id']]
                            if realCompId not in _compIdList and origCompId not in _compIdList:
                                continue
                            if set(_factor['comp_id']) != set(_compIdList):
                                _factor['alt_comp_id'] = _factor['comp_id']
                                _factor['comp_id'] = _compIdList
                        _compIdSelect.add(realCompId)

            if len(_compIdSelect) == 0 and self.__reasons is None:
                for chainId in _factor['chain_id']:
                    ps = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == chainId), None)
                    if ps is not None:
                        for realSeqId in ps['auth_seq_id']:
                            if realSeqId is None:
                                continue
                            idx = ps['auth_seq_id'].index(realSeqId)
                            realCompId = ps['comp_id'][idx]
                            if realCompId in ('ACE', 'NH2'):
                                continue
                            if 'comp_id' in _factor and len(_factor['comp_id']) > 0:
                                origCompId = ps['auth_comp_id'][idx]
                                _compIdList = [translateToStdResName(_compId, realCompId, self.__ccU) for _compId in _factor['comp_id']]
                                if realCompId not in _compIdList and origCompId not in _compIdList:
                                    continue
                                if set(_factor['comp_id']) != set(_compIdList):
                                    _factor['alt_comp_id'] = _factor['comp_id']
                                    _factor['comp_id'] = _compIdList
                            _compIdSelect.add(realCompId)

                        wcPtnrChainIds = getWatsonCrickPtnr(self.__cR, chainId)
                        if wcPtnrChainIds is not None:
                            for wcChainId in wcPtnrChainIds:
                                if wcChainId in _factor['chain_id']:
                                    continue
                                wc = next((wc for wc in self.__polySeq if wc['auth_chain_id'] == wcChainId), None)
                                if wc is not None:
                                    for realSeqId in wc['auth_seq_id']:
                                        if realSeqId is None:
                                            continue
                                        if 'seq_id' in _factor and len(_factor['seq_id']) > 0:
                                            if self.getOrigSeqId(wc, realSeqId) not in _factor['seq_id']:
                                                if self.__reasons is None:
                                                    continue
                                                realSeqId = get_real_seq_id(wc, realSeqId)
                                                if realSeqId is None:
                                                    continue
                                        idx = wc['auth_seq_id'].index(realSeqId)
                                        realCompId = wc['comp_id'][idx]
                                        if 'comp_id' in _factor and len(_factor['comp_id']) > 0:
                                            origCompId = wc['auth_comp_id'][idx]
                                            _compIdList = [translateToStdResName(_compId, realCompId, self.__ccU) for _compId in _factor['comp_id']]
                                            if realCompId not in _compIdList and origCompId not in _compIdList:
                                                continue
                                            if set(_factor['comp_id']) != set(_compIdList):
                                                _factor['alt_comp_id'] = _factor['comp_id']
                                                _factor['comp_id'] = _compIdList
                                        _compIdSelect.add(realCompId)
                                        _factor['chain_id'].append(wcChainId)
                                        if chainId in _factor['chain_id']:
                                            _factor['chain_id'].remove(chainId)

            if self.__hasNonPolySeq:
                for chainId in _factor['chain_id']:
                    npList = [np for np in self.__nonPolySeq if np['auth_chain_id'] == chainId]
                    for np in npList:
                        for realSeqId in np['auth_seq_id']:
                            if realSeqId is None:
                                continue
                            if 'seq_id' in _factor and len(_factor['seq_id']) > 0:
                                if self.getOrigSeqId(np, realSeqId, False) not in _factor['seq_id']:
                                    ptnr = getStructConnPtnr(self.__cR, chainId, realSeqId)
                                    if ptnr is None:
                                        continue
                            idx = np['auth_seq_id'].index(realSeqId)
                            realCompId = self.getRealCompId(np['comp_id'][idx])
                            if 'comp_id' in _factor and len(_factor['comp_id']) > 0:
                                origCompId = np['auth_comp_id'][idx]
                                _compIdList = [translateToStdResName(_compId, realCompId, self.__ccU) for _compId in _factor['comp_id']]
                                if realCompId not in _compIdList and origCompId not in _compIdList:
                                    continue
                                if set(_factor['comp_id']) != set(_compIdList):
                                    _factor['alt_comp_id'] = _factor['comp_id']
                                    _factor['comp_id'] = _compIdList
                            _compIdSelect.add(realCompId)

            _atomIdSelect = set()
            for compId in _compIdSelect:
                if self.__ccU.updateChemCompDict(compId):
                    nucleotide = self.__csStat.getTypeOfCompId(compId)[1]
                    refAtomIdList = [cca[self.__ccU.ccaAtomId] for cca in self.__ccU.lastAtomList]
                    tmpAtomId = _factor['atom_ids'][0].upper()
                    if lenAtomIds == 1:
                        atomId = _atomId = translateToStdAtomName(tmpAtomId, compId, refAtomIdList, ccU=self.__ccU, unambig=unambig)
                        if atomId[-1] in ('%', '*', '#'):
                            if atomId[0] == 'H' and len(atomId) > 2:
                                if atomId[1] != 'M':
                                    _atomId = 'Q' + atomId[1:-1]
                                else:
                                    _atomId = atomId[1:-1]
                            elif atomId[0] in ('Q', 'M'):
                                _atomId = atomId[:-1]
                        atomIds, _, details = self.__nefT.get_valid_star_atom(compId, _atomId, leave_unmatched=True)
                        if details is not None:
                            atomIds, _, details = self.__nefT.get_valid_star_atom_in_xplor(compId, _atomId, leave_unmatched=True)
                        if details is not None and atomId[-1] in ('%', '*', '#'):
                            _atomIds, _, _details = self.__nefT.get_valid_star_atom_in_xplor(compId, atomId[:-1], leave_unmatched=True)
                            if _details is None and len(_atomIds) > 0:  # 5z4f: GLU:HG1# -> GLU:HG3
                                if nucleotide and atomId[0] in protonBeginCode and len(atomId) > 1 and len(_atomIds[0]) > 1\
                                   and atomId[1].isdigit() and _atomIds[0][1].isdigit() and atomId[1] != _atomIds[0][0]:
                                    pass  # 2lzv
                                else:
                                    atomId = _atomId = _atomIds[0]
                                    atomIds, details = _atomIds, _details
                        _atomId = toNefEx(toRegEx(atomId))
                        if _atomId.endswith('.') and details is None:
                            _atomId += '$'  # HT# -> H. should match with H1/2/3 and not with HA2/3 (5iew)
                        elif _atomId.endswith('.*') and details is not None:  # remove excess wild card code e.g. LYS:HB1* -> LYS:HB3 (5kqj)
                            _atomIds, _, _details = self.__nefT.get_valid_star_atom_in_xplor(compId, _atomId[:-2], leave_unmatched=True)
                            if len(_atomIds) > 0 and _details is None:
                                _atomId = _atomIds[0]
                                atomIds, details = _atomIds, _details
                    elif lenAtomIds == 2:
                        atomId1 = translateToStdAtomName(tmpAtomId, compId, refAtomIdList, ccU=self.__ccU, unambig=unambig)
                        atomId2 = translateToStdAtomName(_factor['atom_ids'][1], compId, refAtomIdList, ccU=self.__ccU, unambig=unambig)
                    _atomIds = [cca[self.__ccU.ccaAtomId] for cca in self.__ccU.lastAtomList if cca[self.__ccU.ccaLeavingAtomFlag] != 'Y']
                    if lenAtomIds == 1 and nucleotide:
                        _matchedAtomIds = [_atomId_ for _atomId_ in _atomIds if re.match(_atomId, _atomId_)]
                    matched = False
                    for realAtomId in _atomIds:
                        if lenAtomIds == 1:
                            if re.match(_atomId, realAtomId):
                                if nucleotide and not is_real_nucleic_atom_id(realAtomId, atomId, tmpAtomId, _matchedAtomIds):
                                    continue
                                _atomIdSelect.add(realAtomId)
                                _factor['alt_atom_id'] = _factor['atom_ids'][0]
                                matched = True
                            elif details is None:
                                if len(atomIds) == 1 and not re.match(toNefEx(toRegEx(tmpAtomId)), atomIds[0]):  # len(atomIds) == 1 to allow map HR# to H[DE][12]
                                    continue
                                _atomIdSelect |= set(atomIds)
                                _factor['alt_atom_id'] = _factor['atom_ids'][0]
                                matched = True
                        elif lenAtomIds == 2:
                            if (atomId1 < atomId2 and atomId1 <= realAtomId <= atomId2)\
                               or (atomId1 > atomId2 and atomId2 <= realAtomId <= atomId1):
                                _atomIdSelect.add(realAtomId)
                    if lenAtomIds == 1 and not matched:
                        for chainId in _factor['chain_id']:
                            ps = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == chainId), None)
                            if ps is not None:
                                for realSeqId, realCompId in zip(ps['auth_seq_id'], ps['comp_id']):
                                    if realSeqId is None or realCompId != compId:
                                        continue
                                    if 'seq_id' in _factor and len(_factor['seq_id']) > 0:
                                        if self.getOrigSeqId(ps, realSeqId) not in _factor['seq_id']:
                                            if self.__reasons is None:
                                                continue
                                            realSeqId = get_real_seq_id(ps, realSeqId)
                                            if realSeqId is None:
                                                continue
                                        _, coordAtomSite = self.getCoordAtomSiteOf(chainId, realSeqId, cifCheck=cifCheck)
                                        if coordAtomSite is not None:
                                            __atomId = toNefEx(toRegEx(tmpAtomId))
                                            for realAtomId in coordAtomSite['atom_id']:
                                                if re.match(_atomId, realAtomId) or re.match(__atomId, realAtomId):
                                                    if nucleotide and not is_real_nucleic_atom_id(realAtomId, atomId, tmpAtomId, _matchedAtomIds):
                                                        continue
                                                    _atomIdSelect.add(realAtomId)
                                                    _factor['alt_atom_id'] = _factor['atom_ids'][0]
                            if self.__hasNonPolySeq:
                                np = next((np for np in self.__nonPolySeq if np['auth_chain_id'] == chainId), None)
                                if np is not None:
                                    for realSeqId, realCompId in zip(np['auth_seq_id'], np['comp_id']):
                                        if realSeqId is None or realCompId != compId:
                                            continue
                                        if 'seq_id' in _factor and len(_factor['seq_id']) > 0:
                                            ptnr = None
                                            if self.getOrigSeqId(np, realSeqId, False) not in _factor['seq_id']:
                                                ptnr = getStructConnPtnr(self.__cR, chainId, realSeqId, realCompId)
                                                if ptnr is None:
                                                    continue
                                            _, coordAtomSite = self.getCoordAtomSiteOf(chainId, realSeqId, cifCheck=cifCheck)
                                            if coordAtomSite is not None:
                                                __atomId = toNefEx(toRegEx(tmpAtomId))
                                                for realAtomId in coordAtomSite['atom_id']:
                                                    if re.match(_atomId, realAtomId) or re.match(__atomId, realAtomId):
                                                        if nucleotide and not is_real_nucleic_atom_id(realAtomId, atomId, tmpAtomId, _matchedAtomIds):
                                                            continue
                                                        _atomIdSelect.add(realAtomId)
                                                        _factor['alt_atom_id'] = _factor['atom_ids'][0]
                                                        if ptnr is not None:
                                                            _factor['seq_id'] = [realSeqId]

            _factor['atom_id'] = list(_atomIdSelect)

            if len(_compIdSelect) > 0 and len(_atomIdSelect) == 0 and self.__mrAtomNameMapping is not None:
                tmpAtomId = 'Q' + _factor['atom_ids'][0][1:-1].upper()
                for chainId in _factor['chain_id']:
                    ps = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == chainId), None)
                    if ps is not None:
                        for realSeqId in ps['auth_seq_id']:
                            if realSeqId is None:
                                continue
                            if 'seq_id' in _factor and len(_factor['seq_id']) > 0:
                                if self.getOrigSeqId(ps, realSeqId) not in _factor['seq_id']:
                                    if self.__reasons is None:
                                        continue
                                    realSeqId = get_real_seq_id(ps, realSeqId)
                                    if realSeqId is None:
                                        continue
                            idx = ps['auth_seq_id'].index(realSeqId)
                            realCompId = ps['comp_id'][idx]
                            if realCompId not in monDict3 and realCompId in _compIdSelect:
                                _, coordAtomSite = self.getCoordAtomSiteOf(chainId, realSeqId, cifCheck=cifCheck)
                                atomId = retrieveAtomIdFromMRMap(self.__ccU, self.__mrAtomNameMapping, realSeqId, realCompId, tmpAtomId, coordAtomSite, ignoreSeqId=True)
                                atomIds, _, details = self.__nefT.get_valid_star_atom(realCompId, atomId, leave_unmatched=True)
                                if details is None:
                                    _atomIdSelect |= set(atomIds)
                                    _factor['alt_atom_id'] = _factor['atom_ids'][0]
                    if self.__hasNonPolySeq:
                        np = next((np for np in self.__nonPolySeq if np['auth_chain_id'] == chainId), None)
                        if np is not None:
                            for realSeqId, realCompId in zip(np['auth_seq_id'], np['comp_id']):
                                if realSeqId is None:
                                    continue
                                if 'seq_id' in _factor and len(_factor['seq_id']) > 0:
                                    ptnr = None
                                    if self.getOrigSeqId(np, realSeqId, False) not in _factor['seq_id']:
                                        ptnr = getStructConnPtnr(self.__cR, chainId, realSeqId, realCompId)
                                        if ptnr is None:
                                            continue
                                    _, coordAtomSite = self.getCoordAtomSiteOf(chainId, realSeqId, cifCheck=cifCheck)
                                    atomId = retrieveAtomIdFromMRMap(self.__ccU, self.__mrAtomNameMapping, realSeqId, realCompId, tmpAtomId, coordAtomSite, ignoreSeqId=True)
                                    atomIds, _, details = self.__nefT.get_valid_star_atom(realCompId, atomId, leave_unmatched=True)
                                    if details is None:
                                        _atomIdSelect |= set(atomIds)
                                        _factor['alt_atom_id'] = _factor['atom_ids'][0]
                                        if ptnr is not None:
                                            _factor['seq_id'] = [realSeqId]

                _factor['atom_id'] = list(_atomIdSelect)

            if len(_factor['atom_id']) == 0:
                if self.__reasons is None:
                    self.__preferAuthSeq = not self.__preferAuthSeq

                _compIdSelect = set()
                for chainId in _factor['chain_id']:
                    ps = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == chainId), None)
                    if ps is not None:
                        for realSeqId in ps['auth_seq_id']:
                            if realSeqId is None:
                                continue
                            if 'seq_id' in _factor and len(_factor['seq_id']) > 0:
                                _seqId = self.getOrigSeqId(ps, realSeqId)
                                if self.__reasons is None and not self.__preferAuthSeq:
                                    _seqKey = (chainId, _seqId)
                                    if _seqKey in self.__authToLabelSeq:
                                        _seqId = self.__authToLabelSeq[_seqKey][1]
                                if _seqId not in _factor['seq_id']:
                                    if self.__reasons is None:
                                        continue
                                    realSeqId = get_real_seq_id(ps, realSeqId)
                                    if realSeqId is None:
                                        continue
                            idx = ps['auth_seq_id'].index(realSeqId)
                            realCompId = ps['comp_id'][idx]
                            if 'comp_id' in _factor and len(_factor['comp_id']) > 0:
                                origCompId = ps['auth_comp_id'][idx]
                                _compIdList = [translateToStdResName(_compId, realCompId, self.__ccU) for _compId in _factor['comp_id']]
                                if realCompId not in _compIdList and origCompId not in _compIdList:
                                    continue
                                if set(_factor['comp_id']) != set(_compIdList):
                                    _factor['alt_comp_id'] = _factor['comp_id']
                                    _factor['comp_id'] = _compIdList
                            _compIdSelect.add(realCompId)
                if self.__hasNonPolySeq:
                    for chainId in _factor['chain_id']:
                        npList = [np for np in self.__nonPolySeq if np['auth_chain_id'] == chainId]
                        for np in npList:
                            for realSeqId in np['auth_seq_id']:
                                if realSeqId is None:
                                    continue
                                if 'seq_id' in _factor and len(_factor['seq_id']) > 0:
                                    _seqId = self.getOrigSeqId(np, realSeqId, False)
                                    if not self.__preferAuthSeq and not np_chain_not_specified:
                                        if self.__reasons is None:
                                            _seqKey = (chainId, _seqId)
                                            if _seqKey in self.__authToLabelSeq:
                                                _seqId = self.__authToLabelSeq[_seqKey][1]
                                        elif 'alt_auth_seq_id' in np and np['alt_auth_seq_id'][np['auth_seq_id'].index(_seqId)] in _factor['seq_id']:
                                            _seqId = np['alt_auth_seq_id'][np['auth_seq_id'].index(_seqId)]
                                    if _seqId not in _factor['seq_id']:
                                        if self.__reasons is not None and (self.__preferAuthSeq or _seqId != realSeqId) and realSeqId in np['auth_seq_id']:
                                            pass
                                        else:
                                            ptnr = getStructConnPtnr(self.__cR, chainId, realSeqId)
                                            if ptnr is None:
                                                continue
                                idx = np['auth_seq_id'].index(realSeqId)
                                realCompId = self.getRealCompId(np['comp_id'][idx])
                                if 'comp_id' in _factor and len(_factor['comp_id']) > 0:
                                    origCompId = np['auth_comp_id'][idx]
                                    _compIdList = [translateToStdResName(_compId, realCompId, self.__ccU) for _compId in _factor['comp_id']]
                                    if realCompId not in _compIdList and origCompId not in _compIdList:
                                        continue
                                    if set(_factor['comp_id']) != set(_compIdList):
                                        _factor['alt_comp_id'] = _factor['comp_id']
                                        _factor['comp_id'] = _compIdList
                                _compIdSelect.add(realCompId)

                _atomIdSelect = set()
                for compId in _compIdSelect:
                    if self.__ccU.updateChemCompDict(compId):
                        nucleotide = self.__csStat.getTypeOfCompId(compId)[1]
                        refAtomIdList = [cca[self.__ccU.ccaAtomId] for cca in self.__ccU.lastAtomList]
                        tmpAtomId = _factor['atom_ids'][0].upper()
                        if lenAtomIds == 1:
                            atomId = _atomId = translateToStdAtomName(tmpAtomId, compId, refAtomIdList, ccU=self.__ccU, unambig=unambig)
                            if atomId[-1] in ('%', '*', '#'):
                                if atomId[0] == 'H' and len(atomId) > 2:
                                    if atomId[1] != 'M':
                                        _atomId = 'Q' + atomId[1:-1]
                                    else:
                                        _atomId = atomId[1:-1]
                                elif atomId[0] in ('Q', 'M'):
                                    _atomId = atomId[:-1]
                            atomIds, _, details = self.__nefT.get_valid_star_atom(compId, _atomId, leave_unmatched=True)
                            if details is not None:
                                atomIds, _, details = self.__nefT.get_valid_star_atom_in_xplor(compId, _atomId, leave_unmatched=True)
                            _atomId = toNefEx(toRegEx(atomId))
                        elif lenAtomIds == 2:
                            atomId1 = translateToStdAtomName(tmpAtomId, compId, refAtomIdList, ccU=self.__ccU, unambig=unambig)
                            atomId2 = translateToStdAtomName(_factor['atom_ids'][1], compId, refAtomIdList, ccU=self.__ccU, unambig=unambig)
                        _atomIds = [cca[self.__ccU.ccaAtomId] for cca in self.__ccU.lastAtomList if cca[self.__ccU.ccaLeavingAtomFlag] != 'Y']
                        if lenAtomIds == 1 and nucleotide:
                            _matchedAtomIds = [_atomId_ for _atomId_ in _atomIds if re.match(_atomId, _atomId_)]
                        for realAtomId in _atomIds:
                            if lenAtomIds == 1:
                                if re.match(_atomId, realAtomId):
                                    if nucleotide and not is_real_nucleic_atom_id(realAtomId, atomId, tmpAtomId, _matchedAtomIds):
                                        continue
                                    _atomIdSelect.add(realAtomId)
                                    _factor['alt_atom_id'] = _factor['atom_ids'][0]
                                elif details is None:
                                    if len(atomIds) == 1 and not re.match(toNefEx(toRegEx(tmpAtomId)), atomIds[0]):
                                        continue
                                    _atomIdSelect |= set(atomIds)
                                    _factor['alt_atom_id'] = _factor['atom_ids'][0]
                            elif lenAtomIds == 2:
                                if (atomId1 < atomId2 and atomId1 <= realAtomId <= atomId2)\
                                   or (atomId1 > atomId2 and atomId2 <= realAtomId <= atomId1):
                                    _atomIdSelect.add(realAtomId)

                _factor['atom_id'] = list(_atomIdSelect)

                if self.__reasons is None:
                    self.__preferAuthSeq = not self.__preferAuthSeq

                if len(_atomIdSelect) > 0:
                    if len(self.atomSelectionSet) > 0:
                        self.__setLocalSeqScheme()
                else:
                    if not self.__internal or all(compId in monDict3 for compId in _compIdSelect):
                        _factor['atom_id'] = [None]
                    _factor['alt_atom_id'] = _factor['atom_ids'][0]
            # del _factor['atom_ids']

        if 'atom_id' not in _factor or len(_factor['atom_id']) == 0:
            _compIdSelect = set()
            _repNstdResidueInstance = {}
            _nonPolyCompIdSelect = []
            for chainId in _factor['chain_id']:
                ps = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == chainId), None)
                if ps is not None:
                    for realSeqId in ps['auth_seq_id']:
                        if realSeqId is None:
                            continue
                        if 'seq_id' in _factor and len(_factor['seq_id']) > 0:
                            if self.getOrigSeqId(ps, realSeqId) not in _factor['seq_id']:
                                if self.__reasons is None:
                                    continue
                                realSeqId = get_real_seq_id(ps, realSeqId)
                                if realSeqId is None:
                                    continue
                        idx = ps['auth_seq_id'].index(realSeqId)
                        realCompId = ps['comp_id'][idx]
                        if 'comp_id' in _factor and len(_factor['comp_id']) > 0:
                            origCompId = ps['auth_comp_id'][idx]
                            _compIdList = [translateToStdResName(_compId, realCompId, self.__ccU) for _compId in _factor['comp_id']]
                            if realCompId not in _compIdList and origCompId not in _compIdList:
                                continue
                            if set(_factor['comp_id']) != set(_compIdList):
                                _factor['alt_comp_id'] = _factor['comp_id']
                                _factor['comp_id'] = _compIdList
                        _compIdSelect.add(realCompId)
                        if realCompId not in monDict3:
                            _repNstdResidueInstance[realCompId] = (chainId, realSeqId)
            if self.__hasNonPolySeq:
                for chainId in _factor['chain_id']:
                    npList = [np for np in self.__nonPolySeq if np['auth_chain_id'] == chainId]
                    for np in npList:
                        for realSeqId in np['auth_seq_id']:
                            if realSeqId is None:
                                continue
                            if 'seq_id' in _factor and len(_factor['seq_id']) > 0:
                                if self.getOrigSeqId(np, realSeqId, False) not in _factor['seq_id']:
                                    if _factor['seq_id'][0] not in np['seq_id']:
                                        continue
                                    realSeqId = np['auth_seq_id'][np['seq_id'].index(_factor['seq_id'][0])]
                            idx = np['auth_seq_id'].index(realSeqId)
                            realCompId = self.getRealCompId(np['comp_id'][idx])
                            if 'comp_id' in _factor and len(_factor['comp_id']) > 0:
                                origCompId = np['auth_comp_id'][idx]
                                _compIdList = [translateToStdResName(_compId, realCompId, self.__ccU) for _compId in _factor['comp_id']]
                                if realCompId not in _compIdList and origCompId not in _compIdList:
                                    continue
                                if set(_factor['comp_id']) != set(_compIdList):
                                    _factor['alt_comp_id'] = _factor['comp_id']
                                    _factor['comp_id'] = _compIdList
                            _nonPolyCompIdSelect.append({'chain_id': chainId,
                                                         'seq_id': realSeqId,
                                                         'comp_id': realCompId})

            _atomIdSelect = set()
            for compId in _compIdSelect:
                if self.__ccU.updateChemCompDict(compId):
                    for cca in self.__ccU.lastAtomList:
                        if cca[self.__ccU.ccaLeavingAtomFlag] != 'Y':
                            realAtomId = cca[self.__ccU.ccaAtomId]
                            _atomIdSelect.add(realAtomId)
                    if compId in _repNstdResidueInstance:
                        chainId, seqId = _repNstdResidueInstance[compId]
                        _, coordAtomSite = self.getCoordAtomSiteOf(chainId, seqId, cifCheck=cifCheck)
                        if coordAtomSite is not None:
                            _atomIdSelect |= set(coordAtomSite['atom_id'])  # D_1300057999

            for nonPolyCompId in _nonPolyCompIdSelect:
                _, coordAtomSite = self.getCoordAtomSiteOf(nonPolyCompId['chain_id'], nonPolyCompId['seq_id'], cifCheck=cifCheck)
                if coordAtomSite is not None:
                    if coordAtomSite['comp_id'] == nonPolyCompId['comp_id']:
                        for realAtomId in coordAtomSite['atom_id']:
                            _atomIdSelect.add(realAtomId)
                    else:
                        compId = nonPolyCompId['comp_id']
                        if self.__ccU.updateChemCompDict(compId):
                            for cca in self.__ccU.lastAtomList:
                                if cca[self.__ccU.ccaLeavingAtomFlag] != 'Y':
                                    realAtomId = cca[self.__ccU.ccaAtomId]
                                    _atomIdSelect.add(realAtomId)
                else:
                    for np in self.__nonPolySeq:
                        if nonPolyCompId['seq_id'] == np['auth_seq_id'][0]:
                            _, coordAtomSite = self.getCoordAtomSiteOf(nonPolyCompId['chain_id'], np['seq_id'][0], cifCheck=cifCheck)
                            if coordAtomSite is not None:
                                if coordAtomSite['comp_id'] == nonPolyCompId['comp_id']:
                                    for realAtomId in coordAtomSite['atom_id']:
                                        _atomIdSelect.add(realAtomId)
                                else:
                                    compId = nonPolyCompId['comp_id']
                                    if self.__ccU.updateChemCompDict(compId):
                                        for cca in self.__ccU.lastAtomList:
                                            if cca[self.__ccU.ccaLeavingAtomFlag] != 'Y':
                                                realAtomId = cca[self.__ccU.ccaAtomId]
                                                _atomIdSelect.add(realAtomId)

            _factor['atom_id'] = list(_atomIdSelect)

            if len(_factor['atom_id']) == 0:
                if self.__reasons is None:
                    self.__preferAuthSeq = not self.__preferAuthSeq

                _compIdSelect = set()
                _repNstdResidueInstance = {}
                _nonPolyCompIdSelect = []
                for chainId in _factor['chain_id']:
                    ps = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == chainId), None)
                    if ps is not None:
                        for realSeqId in ps['auth_seq_id']:
                            if realSeqId is None:
                                continue
                            if 'seq_id' in _factor and len(_factor['seq_id']) > 0:
                                _seqId = self.getOrigSeqId(ps, realSeqId)
                                if self.__reasons is None and not self.__preferAuthSeq:
                                    _seqKey = (chainId, _seqId)
                                    if _seqKey in self.__authToLabelSeq:
                                        _seqId = self.__authToLabelSeq[_seqKey][1]
                                if _seqId not in _factor['seq_id']:
                                    if self.__reasons is None:
                                        continue
                                    realSeqId = get_real_seq_id(ps, realSeqId)
                                    if realSeqId is None:
                                        continue
                            idx = ps['auth_seq_id'].index(realSeqId)
                            realCompId = ps['comp_id'][idx]
                            if 'comp_id' in _factor and len(_factor['comp_id']) > 0:
                                origCompId = ps['auth_comp_id'][idx]
                                _compIdList = [translateToStdResName(_compId, realCompId, self.__ccU) for _compId in _factor['comp_id']]
                                if realCompId not in _compIdList and origCompId not in _compIdList:
                                    continue
                                if set(_factor['comp_id']) != set(_compIdList):
                                    _factor['alt_comp_id'] = _factor['comp_id']
                                    _factor['comp_id'] = _compIdList
                            _compIdSelect.add(realCompId)
                            if realCompId not in monDict3:
                                _repNstdResidueInstance[realCompId] = (chainId, realSeqId)
                if self.__hasNonPolySeq:
                    for chainId in _factor['chain_id']:
                        npList = [np for np in self.__nonPolySeq if np['auth_chain_id'] == chainId]
                        for np in npList:
                            for realSeqId in np['auth_seq_id']:
                                if realSeqId is None:
                                    continue
                                if 'seq_id' in _factor and len(_factor['seq_id']) > 0:
                                    _seqId = self.getOrigSeqId(np, realSeqId, False)
                                    if not self.__preferAuthSeq and not np_chain_not_specified:
                                        if self.__reasons is None:
                                            _seqKey = (chainId, _seqId)
                                            if _seqKey in self.__authToLabelSeq:
                                                _seqId = self.__authToLabelSeq[_seqKey][1]
                                        elif 'alt_auth_seq_id' in np and np['alt_auth_seq_id'][np['auth_seq_id'].index(_seqId)] in _factor['seq_id']:
                                            _seqId = np['alt_auth_seq_id'][np['auth_seq_id'].index(_seqId)]
                                    if _seqId not in _factor['seq_id']:
                                        if self.__reasons is not None and (self.__preferAuthSeq or _seqId != realSeqId) and realSeqId in np['auth_seq_id']:
                                            pass
                                        else:
                                            ptnr = getStructConnPtnr(self.__cR, chainId, realSeqId)
                                            if ptnr is None:
                                                continue
                                idx = np['auth_seq_id'].index(realSeqId)
                                realCompId = self.getRealCompId(np['comp_id'][idx])
                                if 'comp_id' in _factor and len(_factor['comp_id']) > 0:
                                    origCompId = np['auth_comp_id'][idx]
                                    _compIdList = [translateToStdResName(_compId, realCompId, self.__ccU) for _compId in _factor['comp_id']]
                                    if realCompId not in _compIdList and origCompId not in _compIdList:
                                        continue
                                    if set(_factor['comp_id']) != set(_compIdList):
                                        _factor['alt_comp_id'] = _factor['comp_id']
                                        _factor['comp_id'] = _compIdList
                                _nonPolyCompIdSelect.append({'chain_id': chainId,
                                                             'seq_id': realSeqId,
                                                             'comp_id': realCompId})

                _atomIdSelect = set()
                for compId in _compIdSelect:
                    if self.__ccU.updateChemCompDict(compId):
                        for cca in self.__ccU.lastAtomList:
                            if cca[self.__ccU.ccaLeavingAtomFlag] != 'Y':
                                realAtomId = cca[self.__ccU.ccaAtomId]
                                _atomIdSelect.add(realAtomId)
                        if compId in _repNstdResidueInstance:
                            chainId, seqId = _repNstdResidueInstance[compId]
                            _, coordAtomSite = self.getCoordAtomSiteOf(chainId, seqId, cifCheck=cifCheck)
                            if coordAtomSite is not None:
                                _atomIdSelect |= set(coordAtomSite['atom_id'])  # D_1300057999

                for nonPolyCompId in _nonPolyCompIdSelect:
                    _, coordAtomSite = self.getCoordAtomSiteOf(nonPolyCompId['chain_id'], nonPolyCompId['seq_id'], cifCheck=cifCheck)
                    if coordAtomSite is not None:
                        if coordAtomSite['comp_id'] == nonPolyCompId['comp_id']:
                            for realAtomId in coordAtomSite['atom_id']:
                                _atomIdSelect.add(realAtomId)
                        else:
                            compId = nonPolyCompId['comp_id']
                            if self.__ccU.updateChemCompDict(compId):
                                for cca in self.__ccU.lastAtomList:
                                    if cca[self.__ccU.ccaLeavingAtomFlag] != 'Y':
                                        realAtomId = cca[self.__ccU.ccaAtomId]
                                        _atomIdSelect.add(realAtomId)
                    else:
                        for np in self.__nonPolySeq:
                            if nonPolyCompId['seq_id'] == np['auth_seq_id'][0]:
                                _, coordAtomSite = self.getCoordAtomSiteOf(nonPolyCompId['chain_id'], np['seq_id'][0], cifCheck=cifCheck)
                                if coordAtomSite is not None:
                                    if coordAtomSite['comp_id'] == nonPolyCompId['comp_id']:
                                        for realAtomId in coordAtomSite['atom_id']:
                                            _atomIdSelect.add(realAtomId)
                                    else:
                                        compId = nonPolyCompId['comp_id']
                                        if self.__ccU.updateChemCompDict(compId):
                                            for cca in self.__ccU.lastAtomList:
                                                if cca[self.__ccU.ccaLeavingAtomFlag] != 'Y':
                                                    realAtomId = cca[self.__ccU.ccaAtomId]
                                                    _atomIdSelect.add(realAtomId)

                _factor['atom_id'] = list(_atomIdSelect)

                if self.__reasons is None:
                    self.__preferAuthSeq = not self.__preferAuthSeq

                if len(_factor['atom_id']) > 0:
                    if len(self.atomSelectionSet) > 0:
                        self.__setLocalSeqScheme()
                else:
                    _factor['atom_id'] = [None]

        if 'comp_id' in _factor and len(_factor['comp_id']) > 0:
            for chainId in _factor['chain_id']:
                ps = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == chainId), None)
                if ps is not None:
                    for realSeqId in ps['auth_seq_id']:
                        if realSeqId is None:
                            continue
                        if 'seq_id' in _factor and len(_factor['seq_id']) > 0:
                            if self.getOrigSeqId(ps, realSeqId) not in _factor['seq_id']:
                                if self.__reasons is None:
                                    continue
                                realSeqId = get_real_seq_id(ps, realSeqId)
                                if realSeqId is None:
                                    continue
                        idx = ps['auth_seq_id'].index(realSeqId)
                        realCompId = ps['comp_id'][idx]
                        origCompId = ps['auth_comp_id'][idx]
                        _compIdList = [translateToStdResName(_compId, realCompId, self.__ccU) for _compId in _factor['comp_id']]
                        if realCompId not in _compIdList and origCompId not in _compIdList:
                            continue
                        if set(_factor['comp_id']) != set(_compIdList):
                            _factor['alt_comp_id'] = _factor['comp_id']
                            _factor['comp_id'] = _compIdList
            if self.__hasNonPolySeq:
                for chainId in _factor['chain_id']:
                    npList = [np for np in self.__nonPolySeq if np['auth_chain_id'] == chainId]
                    for np in npList:
                        for realSeqId in np['auth_seq_id']:
                            if realSeqId is None:
                                continue
                            if 'seq_id' in _factor and len(_factor['seq_id']) > 0:
                                if self.getOrigSeqId(np, realSeqId, False) not in _factor['seq_id']:
                                    if _factor['seq_id'][0] not in np['seq_id']:
                                        continue
                                    realSeqId = np['auth_seq_id'][np['seq_id'].index(_factor['seq_id'][0])]
                            idx = np['auth_seq_id'].index(realSeqId)
                            realCompId = self.getRealCompId(np['comp_id'][idx])
                            origCompId = np['auth_comp_id'][idx]
                            _compIdList = [translateToStdResName(_compId, realCompId, self.__ccU) for _compId in _factor['comp_id']]
                            if realCompId not in _compIdList and origCompId not in _compIdList:
                                continue
                            if set(_factor['comp_id']) != set(_compIdList):
                                _factor['alt_comp_id'] = _factor['comp_id']
                                _factor['comp_id'] = _compIdList

        if self.__reasons is not None and 'np_atom_id_remap' in self.__reasons\
           and len(_factor['atom_id']) == 1 and _factor['atom_id'][0] is not None:
            _atomId = _factor['atom_id'][0].upper()
            if _atomId in self.__reasons['np_atom_id_remap']:
                _seqKey = self.__reasons['np_atom_id_remap'][_atomId]
                _factor['chain_id'] = [_seqKey[0]]
                _factor['seq_id'] = [_seqKey[1]]

        _atomSelection = []

        len_f = len(self.__f)

        foundCompId = False
        if _factor['atom_id'][0] is not None:
            foundCompId = self.__consumeFactor_expressions__(_factor, cifCheck, _atomSelection,
                                                             isPolySeq=True, isChainSpecified=True)
            if self.__hasNonPolySeq:
                foundCompId |= self.__consumeFactor_expressions__(_factor, cifCheck, _atomSelection,
                                                                  isPolySeq=False, isChainSpecified=True,
                                                                  altPolySeq=self.__nonPolySeq, resolved=foundCompId)

            if not foundCompId and len(_factor['chain_id']) == 1 and len(self.__polySeq) > 1\
               and 'global_sequence_offset' not in self.reasonsForReParsing\
               and (self.__reasons is None or 'global_sequence_offset' not in self.__reasons):
                foundCompId |= self.__consumeFactor_expressions__(_factor, cifCheck, _atomSelection,
                                                                  isPolySeq=True, isChainSpecified=False)
                if self.__hasNonPolySeq:
                    self.__consumeFactor_expressions__(_factor, cifCheck, _atomSelection,
                                                       isPolySeq=False, isChainSpecified=False,
                                                       altPolySeq=self.__nonPolySeq, resolved=foundCompId)

        atom_not_found_error = len(self.__f) > len_f and any('[Atom not found]' in f or 'Hydrogen not instantiated' in f for f in self.__f[len_f:])

        if self.__reasons is None and self.__preferAuthSeq and not atom_not_found_error and self.__complexSeqScheme\
           and not chain_not_specified and 'seq_not_specified' not in _factor:
            if guessCompIdFromAtomId(_factor['atom_id'], self.__polySeq, self.__nefT) is not None:
                if 'inhibit_label_seq_scheme_stats' not in self.reasonsForReParsing:
                    self.reasonsForReParsing['inhibit_label_seq_scheme_stats'] = {}
                chainId = _factor['chain_id'][0]
                if chainId not in self.reasonsForReParsing['inhibit_label_seq_scheme_stats']:
                    self.reasonsForReParsing['inhibit_label_seq_scheme_stats'][chainId] = 0
                self.reasonsForReParsing['inhibit_label_seq_scheme_stats'][chainId] += 1

        if 'segment_id' in _factor:
            del _factor['segment_id']
        if 'atom_ids' in _factor:
            del _factor['atom_ids']
        if 'atom_not_specified' in _factor:
            del _factor['atom_not_specified']
        if 'seq_not_specified' in _factor:
            del _factor['seq_not_specified']

        atomSelection = [dict(s) for s in set(frozenset(atom.items())
                                              for atom in _atomSelection
                                              if isinstance(atom, dict))]

        valid = len(self.__f) == len_warn_msg

        if 'alt_chain_id' in _factor:
            for _atom in atomSelection:
                self.updateSegmentIdDict(_factor, _atom['chain_id'], _atom['is_poly'], valid)

        if 'atom_selection' not in _factor:
            _factor['atom_selection'] = atomSelection
        else:
            _factor['atom_selection'] = self.__intersectionAtom_selections(_factor['atom_selection'], atomSelection)

        _atomId = _factor['atom_id'][0].upper() if _factor['atom_id'][0] is not None else None

        def has_identical_chain_id(chain_id):
            try:
                next(ps for ps in self.__polySeq if ps['auth_chain_id'] == chain_id and 'identical_chain_id' in ps)
                return True
            except StopIteration:
                pass
            return False

        def update_np_atom_id_remap():
            if len(_factor['chain_id']) == 1 and len(_factor['seq_id']) == 1:
                if 'np_seq_id_remap' not in self.reasonsForReParsing:
                    self.reasonsForReParsing['np_seq_id_remap'] = {}
                chainId = _factor['chain_id'][0]
                srcSeqId = _factor['seq_id'][0]
                dstSeqId = self.__uniqAtomIdToSeqKey[_atomId][1]
                if chainId not in self.reasonsForReParsing['np_seq_id_remap']:
                    self.reasonsForReParsing['np_seq_id_remap'][chainId] = {}
                if srcSeqId in self.reasonsForReParsing['np_seq_id_remap'][chainId]:
                    if self.reasonsForReParsing['np_seq_id_remap'][chainId][srcSeqId] is not None:
                        if self.reasonsForReParsing['np_seq_id_remap'][chainId][srcSeqId] != dstSeqId:
                            self.reasonsForReParsing['np_seq_id_remap'][chainId][srcSeqId] = None
            else:
                if 'np_atom_id_remap' not in self.reasonsForReParsing:
                    self.reasonsForReParsing['np_atom_id_remap'] = {}
                if _atomId not in self.reasonsForReParsing['np_atom_id_remap']:
                    self.reasonsForReParsing['np_atom_id_remap'][_atomId] = self.__uniqAtomIdToSeqKey[_atomId]

        if len(_factor['atom_selection']) == 0:
            __factor = copy.copy(_factor)
            del __factor['atom_selection']
            if _atomId is None and 'alt_atom_id' not in _factor:
                if self.__cur_subtype != 'plane' and cifCheck and not self.__cur_union_expr:
                    if len(_factor['seq_id']) == 1 and 'alt_atom_id' in _factor and _factor['alt_atom_id'][0] is not None and 'comp_id' not in _factor:
                        for chainId in _factor['chain_id']:
                            updateSeqAtmRst(self.__seqAtmRstFailed, chainId, _factor['seq_id'][0], [_factor['alt_atom_id']])
                            if has_identical_chain_id(chainId):
                                break

            else:
                error_type = "Insufficient atom selection" if 'atom_num' not in __factor else 'Atom not found'
                if self.__cur_subtype != 'plane':
                    if cifCheck:
                        if self.__cur_union_expr or (self.__top_union_expr and ambigAtomSelect):  # 2mws, 2krf
                            self.__g.append(f"[Insufficient atom selection] {self.__getCurrentRestraint()}"
                                            f"The {clauseName} has no effect for a factor {getReadableFactor(__factor)}.")
                            if self.__uniqAtomIdToSeqKey is not None and len(_factor['atom_id']) == 1 and _atomId in self.__uniqAtomIdToSeqKey:
                                update_np_atom_id_remap()

                        else:
                            # self.__f.append(f"[{error_type}] {self.__getCurrentRestraint()}"
                            #                 f"The {clauseName} has no effect for a factor {getReadableFactor(__factor)}.")
                            if 'alt_chain_id' in _factor:  # 2mnz
                                for chainId in _factor['chain_id']:
                                    self.updateSegmentIdDict(_factor, chainId, None, False)
                            if foundCompId and len(_factor['atom_id']) == 1 and 'comp_id' not in _factor:
                                compIds = guessCompIdFromAtomId(_factor['atom_id'], self.__polySeq, self.__nefT)
                                if compIds is not None:
                                    foundCompId = False  # 2l5y
                            if not foundCompId:
                                # DAOTHER-9063
                                ligands = 0
                                npChainIds = set()
                                if self.__hasNonPoly and self.__cur_subtype == 'dist':
                                    for np in self.__nonPoly:
                                        ligands += len(np['seq_id'])
                                        npChainIds.add(np['auth_chain_id'])  # 2lqc
                                if ligands == 1:
                                    npChainIds.clear()  # 2ljc
                                if (len(_factor['chain_id']) == 1 or _factor['chain_id'][0] in npChainIds) and len(_factor['seq_id']) == 1:

                                    def update_np_seq_id_remap_request(np, ligands):
                                        if 'np_seq_id_remap' not in self.reasonsForReParsing:
                                            self.reasonsForReParsing['np_seq_id_remap'] = {}
                                        chainId = _factor['chain_id'][0]
                                        srcSeqId = _factor['seq_id'][0]
                                        dstSeqId = np['seq_id'][0]
                                        if chainId not in self.reasonsForReParsing['np_seq_id_remap']:
                                            self.reasonsForReParsing['np_seq_id_remap'][chainId] = {}
                                        if srcSeqId in self.reasonsForReParsing['np_seq_id_remap'][chainId]:
                                            if self.reasonsForReParsing['np_seq_id_remap'][chainId][srcSeqId] is not None:
                                                if self.reasonsForReParsing['np_seq_id_remap'][chainId][srcSeqId] != dstSeqId:
                                                    self.reasonsForReParsing['np_seq_id_remap'][chainId][srcSeqId] = None
                                                    ligands = 0
                                            else:
                                                ligands = 0
                                        else:
                                            self.reasonsForReParsing['np_seq_id_remap'][chainId][srcSeqId] = dstSeqId
                                        return ligands

                                    def upsert_np_seq_id_remap_request(np):
                                        if 'np_seq_id_remap' not in self.reasonsForReParsing:
                                            self.reasonsForReParsing['np_seq_id_remap'] = {}
                                        chainId = _factor['chain_id'][0]
                                        srcSeqId = _factor['seq_id'][0]
                                        dstSeqId = np['seq_id'][0]
                                        if chainId not in self.reasonsForReParsing['np_seq_id_remap']:
                                            self.reasonsForReParsing['np_seq_id_remap'][chainId] = {}
                                        if srcSeqId in self.reasonsForReParsing['np_seq_id_remap'][chainId]:
                                            if self.reasonsForReParsing['np_seq_id_remap'][chainId][srcSeqId] != dstSeqId:
                                                keys = list(self.reasonsForReParsing['np_seq_id_remap'][chainId].keys())
                                                vals = list(self.reasonsForReParsing['np_seq_id_remap'][chainId].values())
                                                if keys != sorted(keys) or vals != sorted(vals) or len(set(keys)) != len(set(vals)):
                                                    self.reasonsForReParsing['np_seq_id_remap'][chainId][srcSeqId] = dstSeqId
                                        else:
                                            self.reasonsForReParsing['np_seq_id_remap'][chainId][srcSeqId] = dstSeqId

                                    if ligands == 1:
                                        for np in self.__nonPoly:
                                            _, _coordAtomSite = self.getCoordAtomSiteOf(np['auth_chain_id'], np['seq_id'][0], cifCheck=cifCheck)
                                            if _coordAtomSite is not None and len(_factor['atom_id']) == 1\
                                               and _atomId is not None\
                                               and (_atomId in _coordAtomSite['atom_id']
                                                    or (len(_atomId) == 4 and ((_atomId[-2] == '+' and _atomId[-1].isdigit())
                                                                               or (_atomId[-1] == '+' and _atomId[-2].isdigit()))
                                                        and _atomId[:2] in _coordAtomSite['atom_id'])
                                                    or (len(_atomId) == 3 and (_atomId[-1].isdigit() or _atomId[-1] in ('+', '-'))
                                                        and _atomId[:2] in _coordAtomSite['atom_id'])
                                                    or (_atomId == 'X' and ('UNK' in _coordAtomSite['atom_id'] or 'UNX' in _coordAtomSite['atom_id']))):
                                                ligands = update_np_seq_id_remap_request(self.__nonPoly[0], ligands)
                                            else:
                                                ligands = 0

                                    elif ligands > 1 and len(_factor['atom_id']) == 1\
                                            and _atomId is not None\
                                            and (_atomId in SYMBOLS_ELEMENT  # 2n3r
                                                 or (len(_atomId) == 4 and ((_atomId[-2] == '+' and _atomId[-1].isdigit())
                                                                            or (_atomId[-1] == '+' and _atomId[-2].isdigit()))
                                                     and _atomId[:2] in SYMBOLS_ELEMENT)  # 6kg9, 2ma7
                                                 or (len(_atomId) == 3 and (_atomId[-1].isdigit() or _atomId[-1] in ('+', '-'))
                                                     and _atomId[:2] in SYMBOLS_ELEMENT)  # 2m28, 2mco
                                                 or _atomId == 'X'):  # 2mjq, 2mjr, 2mjs, 2mjt
                                        if _atomId != 'X':
                                            elemName = _atomId[:2]
                                            elemCount = 0
                                            refElemSeqIds = []
                                            for np in self.__nonPoly:
                                                if np['comp_id'][0] == elemName:
                                                    elemCount += 1
                                                    refElemSeqIds.append(np['seq_id'][0])
                                            if elemCount == 1:
                                                for np in self.__nonPoly:
                                                    if np['comp_id'][0] == elemName:
                                                        ligands = update_np_seq_id_remap_request(np, ligands)
                                                        break
                                            elif elemCount > 1:
                                                try:
                                                    elemSeqId = int(_factor['seq_id'][0])
                                                    found = False
                                                    for np in self.__nonPoly:
                                                        if np['comp_id'][0] == elemName and (elemSeqId in np['seq_id'] or elemSeqId in np['auth_seq_id']):
                                                            ligands = update_np_seq_id_remap_request(np, ligands)
                                                            found = True
                                                            break
                                                    if not found:
                                                        if 'alt_chain_id' in _factor:
                                                            elemChainId = _factor['alt_chain_id']
                                                            if elemName in elemChainId and len(elemChainId) > len(elemName) and elemChainId[len(elemName):].isdigit():
                                                                elemChainOrder = int(elemChainId[len(elemName):])
                                                                if 1 <= elemChainOrder <= len(refElemSeqIds):
                                                                    np_idx = 1
                                                                    for np in self.__nonPoly:
                                                                        if np['comp_id'][0] == elemName:
                                                                            if elemChainOrder == np_idx:
                                                                                ligands = update_np_seq_id_remap_request(np, ligands)
                                                                                found = True
                                                                                break
                                                                            np_idx += 1
                                                                else:  # 2lqc
                                                                    for elemSeqId in refElemSeqIds:
                                                                        for np in self.__nonPoly:
                                                                            if np['comp_id'][0] == elemName and elemSeqId in np['seq_id']:
                                                                                upsert_np_seq_id_remap_request(np)
                                                                    found = True
                                                        if not found:
                                                            if 1 <= elemSeqId <= len(refElemSeqIds):
                                                                elemSeqId = refElemSeqIds[elemSeqId - 1]
                                                                for np in self.__nonPoly:
                                                                    if np['comp_id'][0] == elemName and elemSeqId in np['seq_id']:
                                                                        ligands = update_np_seq_id_remap_request(np, ligands)
                                                            else:  # 2lqc
                                                                for elemSeqId in refElemSeqIds:
                                                                    for np in self.__nonPoly:
                                                                        if np['comp_id'][0] == elemName and elemSeqId in np['seq_id']:
                                                                            upsert_np_seq_id_remap_request(np)
                                                except ValueError:
                                                    pass
                                        else:
                                            for np in self.__nonPoly:
                                                _, _coordAtomSite = self.getCoordAtomSiteOf(np['auth_chain_id'], np['seq_id'][0], cifCheck=cifCheck)
                                                if 'UNK' in _coordAtomSite['atom_id']:  # 2mjq, 2mjr, 2mjs
                                                    ligands = update_np_seq_id_remap_request(np, ligands)
                                                    break
                                                if 'UNX' in _coordAtomSite['atom_id']:  # 2mjt
                                                    ligands = update_np_seq_id_remap_request(np, ligands)
                                                    break

                                    elif self.__uniqAtomIdToSeqKey is not None and len(_factor['atom_id']) == 1 and _atomId in self.__uniqAtomIdToSeqKey:
                                        update_np_atom_id_remap()
                                        ligands = 1

                                if len(_factor['seq_id']) == 1:
                                    if len(_factor['atom_id']) == 1 and 'comp_id' not in _factor:
                                        compIds = guessCompIdFromAtomId(_factor['atom_id'], self.__polySeq, self.__nefT)
                                        if compIds is not None:
                                            for chainId in _factor['chain_id']:
                                                if len(compIds) == 1:
                                                    updatePolySeqRst(self.__polySeqRstFailed, chainId, _factor['seq_id'][0], compIds[0])
                                                else:
                                                    updatePolySeqRstAmbig(self.__polySeqRstFailedAmbig, chainId, _factor['seq_id'][0], compIds)
                                                if has_identical_chain_id(chainId):
                                                    break
                                        for chainId in _factor['chain_id']:
                                            updateSeqAtmRst(self.__seqAtmRstFailed, chainId, _factor['seq_id'][0], _factor['atom_id'])
                                            if has_identical_chain_id(chainId):
                                                break

                                if ligands == 0\
                                   and (len(self.__polySeq) == 1 or all('identical_chain_id' in ps for ps in self.__polySeq) or not chain_not_specified):
                                    if _atomId is not None and _atomId.startswith('X')\
                                       and _atomId not in SYMBOLS_ELEMENT:
                                        pass  # 8bxj
                                    elif self.__reasons is not None and 'segment_id_mismatch' in self.__reasons:
                                        pass  # 6f0y
                                    # 2knf, 2ma9
                                    elif _atomId is None\
                                            or (_atomId not in aminoProtonCode and _atomId not in carboxylCode and _atomId not in jcoupBbPairCode)\
                                            or self.__gapInAuthSeq:  # 2kyg
                                        if self.__reasons is None:
                                            self.__preferAuthSeq = not self.__preferAuthSeq
                                            # self.__authSeqId = 'auth_seq_id' if self.__preferAuthSeq else 'label_seq_id'
                                            self.__setLocalSeqScheme()
                                            # ad hoc sequence scheme switching is possible for the first restraint, otherwise the entire restraints should be re-parsed
                                            if trial < 3 and 'Check the 1th row of' in self.__getCurrentRestraint()\
                                               and self.__cur_subtype != 'dist':
                                                # skip ad hoc sequence scheme switching should be inherited to the other restraints
                                                del _factor['atom_selection']
                                                return self.__consumeFactor_expressions(_factor, clauseName, cifCheck, trial + 1)
                                        if not self.__preferAuthSeq and self.__reasons is None\
                                           and (self.__cur_subtype != 'dist' or 'Check the 2th row of' in self.__getCurrentRestraint()):  # 6nk9
                                            if 'label_seq_scheme' not in self.reasonsForReParsing:
                                                self.reasonsForReParsing['label_seq_scheme'] = {}
                                            self.reasonsForReParsing['label_seq_scheme'][self.__cur_subtype] = True

                            if not atom_not_found_error:
                                if _atomId is not None and _atomId.startsnwith('X')\
                                   and _atomId not in SYMBOLS_ELEMENT:  # 8bxj
                                    self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                                    f"The {clauseName} has no effect for a factor {getReadableFactor(__factor)}.")
                                else:
                                    no_ext_seq = True
                                    unobs_seq = False
                                    if len(_factor['chain_id']) == 1 and len(_factor['seq_id']) == 1:
                                        _chainId = _factor['chain_id'][0]
                                        _seqId = _factor['seq_id'][0]
                                        ps = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == _chainId), None)
                                        no_nonpoly = not self.__hasNonPolySeq\
                                            or not any(_seqId in np['auth_seq_id'] for np in self.__nonPolySeq if np['auth_chain_id'] == _chainId)  # 2mco
                                        if ps is not None and _seqId not in ps['auth_seq_id'] and no_nonpoly:
                                            if self.__nmr_vs_model is not None and not ('gap_in_auth_seq' in ps and ps['gap_in_auth_seq']):
                                                nmr_offset = ps['seq_id'][0] - ps['auth_seq_id'][0]  # 2lzn
                                                if self.__reasons is not None and 'global_auth_sequence_offset' in self.__reasons\
                                                   and _chainId in self.__reasons['global_auth_sequence_offset']:
                                                    nmr_offset += self.__reasons['global_auth_sequence_offset'][_chainId]
                                                elif self.__reasons is not None and 'auth_sequence_offset' in self.__reasons\
                                                        and _chainId in self.__reasons['auth_sequence_offset']:
                                                    nmr_offset += self.__reasons['auth_sequence_offset'][_chainId]
                                                elif self.__reasons is not None and 'label_sequence_offset' in self.__reasons\
                                                        and _chainId in self.__reasons['label_sequence_offset']:
                                                    nmr_offset += self.__reasons['label_sequence_offset'][_chainId]
                                                item = next((item for item in self.__nmr_vs_model
                                                             if item['test_auth_chain_id' if 'test_auth_chain_id' in item else 'test_chain_id'] == _chainId), None)
                                                if item is not None and item['conflict'] == 0 and item['unmapped'] > 0 and 'unmapped_sequence' in item:
                                                    refCompId = next((u['ref_comp_id'] for u in item['unmapped_sequence']
                                                                      if 'ref_seq_id' in u and u['ref_seq_id'] == _seqId + nmr_offset), None)
                                                    if refCompId is not None:
                                                        hint = f" The residue '{_seqId}:{refCompId}' is not present in polymer sequence "\
                                                            f"of chain {_chainId} of the coordinates. "\
                                                            "Please update the sequence in the Macromolecules page."
                                                        if self.__reasons is not None:
                                                            self.__f.append(f"[Sequence mismatch warning] {self.__getCurrentRestraint()}"
                                                                            f"The {clauseName} has no effect for a factor {getReadableFactor(__factor)}.{hint}")
                                                        no_ext_seq = False  # 2ls7
                                            if no_ext_seq:
                                                auth_seq_id_list = list(filter(None, ps['auth_seq_id']))
                                                if len(auth_seq_id_list) > 0:
                                                    min_auth_seq_id = min(auth_seq_id_list)
                                                    max_auth_seq_id = max(auth_seq_id_list)
                                                    if (_seqId < min_auth_seq_id and min_auth_seq_id - _seqId <= MIN_EXT_SEQ_FOR_ATOM_SEL_ERR)\
                                                       or (_seqId > max_auth_seq_id and _seqId - max_auth_seq_id <= MIN_EXT_SEQ_FOR_ATOM_SEL_ERR):
                                                        hint = f" The residue '{_seqId}' is not present in polymer sequence "\
                                                            f"of chain {_chainId} of the coordinates. "\
                                                            "Please update the sequence in the Macromolecules page."
                                                        if self.__reasons is not None:
                                                            self.__f.append(f"[Sequence mismatch warning] {self.__getCurrentRestraint()}"
                                                                            f"The {clauseName} has no effect for a factor {getReadableFactor(__factor)}.{hint}")
                                                        no_ext_seq = False  # 2law
                                        _seqKey = (_chainId, _seqId)
                                        if _seqKey in self.__coordUnobsRes:
                                            unobs_seq = True  # 2n25
                                        if _seqKey in self.__coordUnobsAtom and 'atom_id' in _factor:
                                            _atomIds = self.getAtomIdList(_factor, self.__coordUnobsAtom[_seqKey]['comp_id'], _factor['atom_id'][0])
                                            if _atomIds[0] in self.__coordUnobsAtom[_seqKey]['atom_ids']:
                                                unobs_seq = True
                                    elif len(_factor['chain_id']) > 1 and len(_factor['seq_id']) == 1:
                                        _chainId_ = []
                                        _seqId = _factor['seq_id'][0]
                                        for _chainId in _factor['chain_id']:
                                            ps = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == _chainId), None)
                                            no_nonpoly = not self.__hasNonPolySeq\
                                                or not any(_seqId in np['auth_seq_id'] for np in self.__nonPolySeq if np['auth_chain_id'] == _chainId)
                                            if ps is not None and _seqId not in ps['auth_seq_id'] and no_nonpoly:
                                                auth_seq_id_list = list(filter(None, ps['auth_seq_id']))
                                                if len(auth_seq_id_list) > 0:
                                                    min_auth_seq_id = min(auth_seq_id_list)
                                                    max_auth_seq_id = max(auth_seq_id_list)
                                                    if (_seqId < min_auth_seq_id and min_auth_seq_id - _seqId <= MIN_EXT_SEQ_FOR_ATOM_SEL_ERR)\
                                                       or (_seqId > max_auth_seq_id and _seqId - max_auth_seq_id <= MIN_EXT_SEQ_FOR_ATOM_SEL_ERR):
                                                        _chainId_.append(_chainId)
                                        if len(_chainId_) == 1:
                                            _chainId = _chainId_[0]
                                            ps = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == _chainId), None)
                                            if ps is not None and _seqId not in ps['auth_seq_id']:
                                                auth_seq_id_list = list(filter(None, ps['auth_seq_id']))
                                                if len(auth_seq_id_list) > 0:
                                                    min_auth_seq_id = min(auth_seq_id_list)
                                                    max_auth_seq_id = max(auth_seq_id_list)
                                                    if (_seqId < min_auth_seq_id and min_auth_seq_id - _seqId <= MIN_EXT_SEQ_FOR_ATOM_SEL_ERR)\
                                                       or (_seqId > max_auth_seq_id and _seqId - max_auth_seq_id <= MIN_EXT_SEQ_FOR_ATOM_SEL_ERR):
                                                        hint = f" The residue '{_seqId}' is not present in polymer sequence "\
                                                            f"of chain {_chainId} of the coordinates. "\
                                                            "Please update the sequence in the Macromolecules page."
                                                        if self.__reasons is not None:
                                                            self.__f.append(f"[Sequence mismatch warning] {self.__getCurrentRestraint()}"
                                                                            f"The {clauseName} has no effect for a factor {getReadableFactor(__factor)}.{hint}")
                                                        no_ext_seq = False  # 2mps
                                            _seqKey = (_chainId, _seqId)
                                            if _seqKey in self.__coordUnobsRes:
                                                unobs_seq = True  # 2n25
                                            if _seqKey in self.__coordUnobsAtom and 'atom_id' in _factor:
                                                _atomIds = self.getAtomIdList(_factor, self.__coordUnobsAtom[_seqKey]['comp_id'], _factor['atom_id'][0])
                                                if _atomIds[0] in self.__coordUnobsAtom[_seqKey]['atom_ids']:
                                                    unobs_seq = True
                                    if (no_ext_seq or self.__reasons is None) and not unobs_seq:
                                        if no_ext_seq:  # 2laz
                                            hint = " Please make sure that the values in 'segidentifier', 'residue', and 'name' clauses of the restraint file match "\
                                                "the auth_asym_id, auth_seq_id, and auth_atom_id values of the coordinates, respectively. "\
                                                "Alternatively, try to upload the genuine coordinate file generated by structure determination software without editing."
                                        self.__f.append(f"[Insufficient atom selection] {self.__getCurrentRestraint()}"
                                                        f"The {clauseName} has no effect for a factor {getReadableFactor(__factor)}.{hint}")
                    else:
                        self.__g.append(f"[{error_type}] {self.__getCurrentRestraint()}"
                                        f"The {clauseName} has no effect for a factor {getReadableFactor(__factor)}. "
                                        "Please update the sequence in the Macromolecules page.")
                else:
                    if 'atom_id' not in _factor or ('H5T' not in _factor['atom_id'] and 'H3T' not in _factor['atom_id']
                                                    and 'HOP2' not in _factor['atom_id'] and "HO3'" not in _factor['atom_id']
                                                    and "O2'" not in _factor['atom_id']):
                        if not atom_not_found_error:
                            hint = f" Please verify that the planarity restraints match with the residue {_factor['comp_id'][0]!r}"\
                                if 'comp_id' in _factor and len(_factor['comp_id']) == 1 else ''
                            self.__f.append(f"[Insufficient atom selection] {self.__getCurrentRestraint()}"
                                            f"The {clauseName} has no effect for a factor {getReadableFactor(__factor)}.{hint}")

        elif len(_factor['chain_id']) == 1 and len(_factor['seq_id']) == 1 and len(_factor['atom_id']) == 1 and 'comp_id' not in _factor:
            compIds = guessCompIdFromAtomId(_factor['atom_id'], self.__polySeq, self.__nefT)
            if compIds is not None:
                if len(compIds) == 1:
                    updatePolySeqRst(self.__polySeqRstValid, _factor['chain_id'][0], _factor['seq_id'][0], compIds[0])

        if 'chain_id' in _factor:
            del _factor['chain_id']
        if 'comp_id' in _factor:
            del _factor['comp_id']
        if 'seq_id' in _factor:
            del _factor['seq_id']
        if 'type_symbol' in _factor:
            del _factor['type_symbol']
        if 'atom_id' in _factor:
            del _factor['atom_id']
        if 'alt_chain_id' in _factor:
            del _factor['alt_chain_id']
        if 'alt_atom_id' in _factor:
            del _factor['alt_atom_id']

        if ambigAtomSelect or valid:
            self.__cachedDictForFactor[key] = copy.deepcopy(_factor)

        return _factor

    def __consumeFactor_expressions__(self, _factor: dict, cifCheck: bool, _atomSelection: List[dict],
                                      isPolySeq: bool = True, isChainSpecified: bool = True,
                                      altPolySeq: Optional[List[dict]] = None, resolved: bool = False) -> bool:
        atomSpecified = True
        if 'atom_not_specified' in _factor:
            atomSpecified = not _factor['atom_not_specified']
        seqSpecified = True
        if 'seq_not_specified' in _factor:
            seqSpecified = not _factor['seq_not_specified']
        foundCompId = False

        if self.__reasons is not None and 'segment_id_poly_type_stats' in self.__reasons\
           and 'segment_id' in _factor and _factor['segment_id'] in self.__reasons['segment_id_poly_type_stats']:
            stats = self.__reasons['segment_id_poly_type_stats'][_factor['segment_id']]
            if isPolySeq and stats['polymer'] < stats['non-poly']:
                return False
            if not isPolySeq and 'np_seq_id_remap' not in self.__reasons:
                if stats['polymer'] > 10 * stats['non-poly']:
                    return False
                if stats['polymer'] >= stats['non-poly']\
                   and 'np_seq_id_remap' not in self.__reasons and 'non_poly_remap' not in self.__reasons:
                    return False

        chainIds = (_factor['chain_id'] if isChainSpecified else [ps['auth_chain_id'] for ps in (self.__polySeq if isPolySeq else altPolySeq)])

        for chainId in chainIds:

            if self.__reasons is not None:

                if 'label_seq_scheme' in self.__reasons\
                   and self.__reasons['label_seq_scheme'] is not None\
                   and self.__cur_subtype in self.__reasons['label_seq_scheme']\
                   and self.__reasons['label_seq_scheme'][self.__cur_subtype]\
                   and 'inhibit_label_seq_scheme' in self.__reasons and chainId in self.__reasons['inhibit_label_seq_scheme']\
                   and self.__cur_subtype in self.__reasons['inhibit_label_seq_scheme'][chainId]\
                   and self.__reasons['inhibit_label_seq_scheme'][chainId][self.__cur_subtype]\
                   and 'segment_id_mismatch' not in self.__reasons:
                    continue

                if 'uninterpretable_chain_id' in self.__reasons\
                   and chainId in self.__reasons['uninterpretable_chain_id']\
                   and self.__cur_subtype != 'dist'\
                   and 'chain_id_remap' not in self.__reasons:  # 2n2w
                    continue  # 2lqc

            psList = [ps for ps in (self.__polySeq if isPolySeq else altPolySeq) if ps['auth_chain_id'] == chainId]

            if len(psList) == 0:
                if isChainSpecified:
                    _chainIds = [ps['auth_chain_id'] for ps in (self.__polySeq if isPolySeq else altPolySeq)]
                    if self.__hasBranched:
                        _chainIds.extend([br['auth_chain_id'] for br in self.__branched])
                    if all(_chainId not in _chainIds for _chainId in chainIds)\
                       and chainId in [ps['chain_id'] for ps in (self.__polySeq if isPolySeq else altPolySeq)]:
                        psList = [ps for ps in (self.__polySeq if isPolySeq else altPolySeq) if ps['chain_id'] == chainId]
                    if len(psList) == 0:
                        continue
                    if 'auth_chain_id' in _factor:
                        _authChainIds = []
                        for _chainId in _factor['auth_chain_id']:
                            _authChainId = next((ps['auth_chain_id'] for ps in (self.__polySeq if isPolySeq else altPolySeq) if ps['chain_id'] == _chainId), _chainId)
                            if _chainId == chainId:
                                chainId = _authChainId
                            _authChainIds.append(_authChainId)
                        _factor['auth_chain_id'] = _authChainIds
                else:
                    continue

            prefAltAuthSeqId = False

            for ps in psList:

                for seqId in _factor['seq_id']:

                    if seqId is None:
                        continue

                    _seqId_ = seqId
                    seqId, _compId_, extSeqScheme = self.getRealSeqId(ps, seqId, isPolySeq)

                    if seqId is None:
                        continue

                    _seqId = seqId
                    if self.__reasons is not None:
                        if 'branched_remap' in self.__reasons and seqId in self.__reasons['branched_remap']:
                            fixedChainId, seqId = retrieveRemappedChainId(self.__reasons['branched_remap'], seqId)
                            if fixedChainId != chainId:
                                continue
                        if 'np_seq_id_remap' in self.__reasons:
                            if isPolySeq:
                                if 'segment_id' in _factor and 'segment_id_mismatch' in self.__reasons\
                                   and chainId in self.__reasons['segment_id_mismatch'].values()\
                                   and 'segment_id_poly_type_stats' in self.__reasons\
                                   and _factor['segment_id'] in self.__reasons['segment_id_poly_type_stats']\
                                   and stats['polymer'] <= stats['non-poly']:  # 2mtk
                                    _, __seqId = retrieveRemappedSeqId(self.__reasons['np_seq_id_remap'], chainId, seqId)
                                    if __seqId is not None and __seqId != seqId and list(self.__reasons['segment_id_mismatch'].values()).count(chainId) > 1:
                                        continue  # 2lkd
                            else:
                                _, seqId = retrieveRemappedSeqId(self.__reasons['np_seq_id_remap'], chainId, seqId)
                                if seqId is not None:
                                    if _seqId_ != seqId and len(_atomSelection) > 0:
                                        continue
                                    _seqId_ = seqId
                        elif 'chain_id_remap' in self.__reasons and seqId in self.__reasons['chain_id_remap']:
                            fixedChainId, seqId = retrieveRemappedChainId(self.__reasons['chain_id_remap'], seqId)
                            if fixedChainId != chainId:
                                continue
                        elif 'chain_id_clone' in self.__reasons and seqId in self.__reasons['chain_id_clone']:
                            fixedChainId, seqId = retrieveRemappedChainId(self.__reasons['chain_id_clone'], seqId)
                            if fixedChainId != chainId and isPolySeq:
                                continue
                        elif 'seq_id_remap' in self.__reasons:
                            _, seqId = retrieveRemappedSeqId(self.__reasons['seq_id_remap'], chainId, seqId)
                        if seqId is None:
                            seqId = _seqId

                    if ps is not None and seqId in ps['auth_seq_id']:
                        compId = ps['comp_id'][ps['auth_seq_id'].index(seqId)]
                    elif _compId_ is not None and self.__reasons is not None and 'extend_seq_scheme' in self.__reasons:
                        compId = _compId_
                    elif 'gap_in_auth_seq' in ps and ps['gap_in_auth_seq'] and seqId is not None:
                        compId = None
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
                                    idx = ps['auth_seq_id'].index(_seqId_) - _seqId_ - seqId
                                    try:
                                        seqId = ps['auth_seq_id'][idx]
                                        compId = ps['comp_id'][idx]
                                    except IndexError:
                                        pass
                    else:
                        compId = None

                    if not isPolySeq:
                        if compId is None:
                            if 'alt_auth_seq_id' in ps and seqId in ps['alt_auth_seq_id']:
                                idx = ps['alt_auth_seq_id'].index(seqId)
                                seqId = ps['seq_id'][idx]
                                compId = ps['comp_id'][idx]
                                prefAltAuthSeqId = True
                            elif seqId in ps['seq_id']:
                                idx = ps['seq_id'].index(seqId)
                                compId = ps['comp_id'][idx]
                                _seqId_ = ps['auth_seq_id'][idx]
                        elif prefAltAuthSeqId:
                            continue

                    if None in (self.__authToInsCode, _compId_) or len(self.__authToInsCode) == 0:
                        seqKey, coordAtomSite = self.getCoordAtomSiteOf(chainId, seqId, compId, cifCheck=cifCheck)
                    else:
                        compId = _compId_
                        seqKey, coordAtomSite = self.getCoordAtomSiteOf(chainId, seqId, _compId_, cifCheck=cifCheck)

                    if compId is None and seqKey in self.__authToLabelSeq:
                        _, seqId = self.__authToLabelSeq[seqKey]
                        if ps is not None and seqId in ps['auth_seq_id']:
                            compId = ps['comp_id'][ps['auth_seq_id'].index(seqId)]
                            seqKey, coordAtomSite = self.getCoordAtomSiteOf(chainId, seqId, cifCheck=cifCheck)

                    if compId is None and coordAtomSite is not None and ps is not None and seqKey[1] in ps['auth_seq_id']:
                        compId = ps['comp_id'][ps['auth_seq_id'].index(seqKey[1])]

                    if coordAtomSite is None and not isPolySeq:
                        try:
                            idx = ps['auth_seq_id'].index(seqId)
                            seqId = ps['seq_id'][idx]
                            compId = ps['comp_id'][idx]
                            seqKey, coordAtomSite = self.getCoordAtomSiteOf(chainId, seqId, cifCheck=cifCheck)
                        except ValueError:  # 2yhh (branched)
                            try:
                                idx = ps['seq_id'].index(seqId)
                                seqId = ps['auth_seq_id'][idx]
                                compId = ps['comp_id'][idx]
                                seqKey, coordAtomSite = self.getCoordAtomSiteOf(chainId, seqId, cifCheck=cifCheck)
                            except ValueError:
                                pass

                    atomId = _factor['atom_id'][0].upper()

                    if self.__hasNonPoly:
                        if isPolySeq and len(atomId) == 4\
                           and atomId[:2] in SYMBOLS_ELEMENT\
                           and atomId[2:] in ('+1', '+2', '+3', '1+', '2+', '3+'):
                            elemName = atomId[:2]
                            elemCount = 0
                            for np in self.__nonPoly:
                                if np['comp_id'][0] == elemName:
                                    elemCount += 1
                            if elemCount > 0:
                                continue

                        elif not isPolySeq and len(atomId) >= 2\
                                and (atomId in SYMBOLS_ELEMENT
                                     or (len(atomId) == 4 and atomId[:2] in SYMBOLS_ELEMENT
                                         and atomId[2:] in ('+1', '+2', '+3', '1+', '2+', '3+'))):
                            elemName = atomId[:2]
                            elemCount = 0
                            for np in self.__nonPoly:
                                if np['comp_id'][0] == elemName:
                                    elemCount += 1
                            if elemCount == 1 and elemName in ps['comp_id']\
                               and self.__cur_subtype == 'dist':
                                compId = elemName
                                seqId = ps['auth_seq_id'][0]
                                seqKey, coordAtomSite = self.getCoordAtomSiteOf(chainId, seqId, compId, cifCheck=cifCheck)

                    if compId is None:
                        """ cancel the following code because comp_id prediction conflicts with extended sequence (7zjy)
                        if isPolySeq and isChainSpecified and self.__reasons is None and self.__preferAuthSeq:
                            self.__preferAuthSeq = False
                            seqId, _compId_, _ = self.getRealSeqId(ps, seqId, isPolySeq)
                            if self.__csStat.peptideLike(_compId_):
                                compIds = guessCompIdFromAtomId(_factor['atom_id'], self.__polySeq, self.__nefT)
                                if compIds is not None and _compId_ in compIds:
                                    if 'label_seq_scheme' not in self.reasonsForReParsing:
                                        self.reasonsForReParsing['label_seq_scheme'] = {}
                                    self.reasonsForReParsing['label_seq_scheme'][self.__cur_subtype] = True
                            self.__preferAuthSeq = True
                        """
                        if isPolySeq and seqSpecified and atomSpecified\
                           and self.__reasons is None and self.__preferAuthSeq and self.__altPolySeq is not None:
                            if seqId in self.__effSeqIdSet:
                                continue
                            __ps = next((__ps for __ps in self.__altPolySeq if __ps['auth_chain_id'] == chainId), None)  # 2mg5
                            if __ps is None or seqId not in __ps['auth_seq_id']:
                                continue
                            try:
                                __seqId = ps['auth_seq_id'][__ps['auth_seq_id'].index(seqId)]
                                if seqId == __seqId:
                                    continue
                                _, __coordAtomSite = self.getCoordAtomSiteOf(chainId, __seqId, cifCheck=cifCheck)
                                if __coordAtomSite is None:
                                    continue
                                __compId = __coordAtomSite['comp_id']
                                __atomSiteAtomId = __coordAtomSite['atom_id']

                                offsets = set()

                                for atomId in _factor['atom_id']:
                                    atomId = atomId.upper()
                                    if __compId not in monDict3 and self.__mrAtomNameMapping is not None:
                                        authCompId = ps['auth_comp_id'][ps['auth_seq_id'].index(__seqId)]
                                        atomId = retrieveAtomIdFromMRMap(self.__ccU, self.__mrAtomNameMapping, __seqId, authCompId, atomId, __coordAtomSite)
                                    __atomIds = self.getAtomIdList(_factor, __compId, atomId)
                                    if __atomIds[0] in __atomSiteAtomId:
                                        offsets.add(__seqId - seqId)

                                if len(offsets) > 0:
                                    if 'alt_global_sequence_offset' not in self.reasonsForReParsing:
                                        self.reasonsForReParsing['alt_global_sequence_offset'] = {}
                                    if chainId in self.reasonsForReParsing['alt_global_sequence_offset']:
                                        if self.reasonsForReParsing['alt_global_sequence_offset'][chainId] is None:
                                            continue
                                        self.reasonsForReParsing['alt_global_sequence_offset'][chainId] &= offsets
                                        if len(self.reasonsForReParsing['alt_global_sequence_offset'][chainId]) == 0:
                                            self.reasonsForReParsing['alt_global_sequence_offset'][chainId] = None
                                            continue
                                        continue
                                    self.reasonsForReParsing['alt_global_sequence_offset'][chainId] = offsets
                            except IndexError:
                                pass
                        continue

                    if self.__reasons is not None:
                        if 'non_poly_remap' in self.__reasons and compId in self.__reasons['non_poly_remap']\
                           and _factor['seq_id'][0] in self.__reasons['non_poly_remap'][compId]:
                            fixedChainId, seqId = retrieveRemappedNonPoly(self.__reasons['non_poly_remap'], ps, chainId, _factor['seq_id'][0], compId)
                            if fixedChainId != chainId:
                                continue
                            if not isPolySeq and len(_atomSelection) > 0:
                                continue

                    _seqId = seqId
                    if self.__reasons is None and not isPolySeq and 'alt_auth_seq_id' in ps and seqId not in ps['auth_seq_id'] and seqId in ps['alt_auth_seq_id']:
                        try:
                            seqId = next(_seqId_ for _seqId_, _altSeqId_ in zip(ps['auth_seq_id'], ps['alt_auth_seq_id']) if _altSeqId_ == seqId)
                        except StopIteration:
                            pass
                        seqKey, coordAtomSite = self.getCoordAtomSiteOf(chainId, seqId, cifCheck=cifCheck)

                    if not isPolySeq and isChainSpecified and self.doesNonPolySeqIdMatchWithPolySeqUnobs(_factor['chain_id'][0], _seqId_):
                        if coordAtomSite is None or atomId not in coordAtomSite['atom_id']:
                            continue

                    if not isPolySeq:
                        replacedBy = self.getRealCompId(compId)
                        if replacedBy != compId:
                            compId = replacedBy
                            _coordAtomSite = copy.deepcopy(coordAtomSite)
                            _coordAtomSite['comp_id'] = compId
                            _coordAtomSite['atom_id'] = [cca[self.__ccU.ccaAtomId] for cca in self.__ccU.lastAtomList if cca[self.__ccU.ccaLeavingAtomFlag] != 'Y']
                            _coordAtomSite['alt_atom_id'] = [cca[self.__ccU.ccaAltAtomId] for cca in self.__ccU.lastAtomList if cca[self.__ccU.ccaLeavingAtomFlag] != 'Y']
                            _coordAtomSite['type_symbol'] = [cca[self.__ccU.ccaTypeSymbol] for cca in self.__ccU.lastAtomList if cca[self.__ccU.ccaLeavingAtomFlag] != 'Y']
                            _coordAtomSite['alt_comp_id'] = [coordAtomSite['alt_comp_id'][0]] * len(_coordAtomSite['atom_id'])
                            coordAtomSite = _coordAtomSite

                    foundCompId = True

                    updatePolySeqRst(self.__polySeqRst, chainId, seqId, compId)

                    atomSiteAtomId = None if coordAtomSite is None else coordAtomSite['atom_id']

                    if atomSiteAtomId is not None and isPolySeq and self.__csStat.peptideLike(compId)\
                       and not any(_atomId in atomSiteAtomId for _atomId in _factor['atom_id'])\
                       and all(_atomId in ('H1', 'H2', 'HN1', 'HN2', 'NT') for _atomId in _factor['atom_id']):
                        _seqKey, _coordAtomSite = self.getCoordAtomSiteOf(chainId, seqId + 1, cifCheck=cifCheck)
                        if _coordAtomSite is not None and _coordAtomSite['comp_id'] == 'NH2':
                            compId = 'NH2'
                            seqId = seqId + 1
                            seqKey = _seqKey
                            coordAtomSite = _coordAtomSite
                            atomSiteAtomId = _coordAtomSite['atom_id']
                        elif 'split_comp_id' in coordAtomSite and 'NH2' in coordAtomSite['split_comp_id']:
                            _seqKey, _coordAtomSite = self.getCoordAtomSiteOf(chainId, seqId, 'NH2', cifCheck=cifCheck)
                            if _coordAtomSite is not None and _coordAtomSite['comp_id'] == 'NH2':
                                compId = 'NH2'
                                seqKey = _seqKey
                                coordAtomSite = _coordAtomSite
                                atomSiteAtomId = _coordAtomSite['atom_id']

                    if self.__hasNonPoly and compId == 'CYS':

                        if atomId in zincIonCode:
                            znCount = 0
                            znSeqId = None
                            for np in self.__nonPoly:
                                if np['comp_id'][0] == 'ZN':
                                    znSeqId = np['auth_seq_id'][0]
                                    znCount += 1
                            if znCount > 0:
                                if znCount == 1:
                                    _seqKey, _coordAtomSite = self.getCoordAtomSiteOf(chainId, znSeqId, 'ZN', cifCheck=cifCheck)
                                    if _coordAtomSite is not None and _coordAtomSite['comp_id'] == 'ZN':
                                        compId = 'ZN'
                                        seqId = znSeqId
                                        seqKey = _seqKey
                                        coordAtomSite = _coordAtomSite
                                        atomSiteAtomId = _coordAtomSite['atom_id']

                        if atomId in calciumIonCode:
                            caCount = 0
                            caSeqId = None
                            for np in self.__nonPoly:
                                if np['comp_id'][0] == 'CA':
                                    caSeqId = np['auth_seq_id'][0]
                                    caCount += 1
                            if caCount > 0:
                                if caCount == 1:
                                    _seqKey, _coordAtomSite = self.getCoordAtomSiteOf(chainId, caSeqId, 'CA', cifCheck=cifCheck)
                                    if _coordAtomSite is not None and _coordAtomSite['comp_id'] == 'CA':
                                        compId = 'CA'
                                        seqId = caSeqId
                                        seqKey = _seqKey
                                        coordAtomSite = _coordAtomSite
                                        atomSiteAtomId = _coordAtomSite['atom_id']

                    auth_seq_id_list = list(filter(None, ps['auth_seq_id']))

                    for atomId in _factor['atom_id']:
                        origAtomId = _factor['atom_id'] if 'alt_atom_id' not in _factor else _factor['alt_atom_id']
                        """
                        if isinstance(origAtomId, str) and origAtomId.startswith('HT') and coordAtomSite is not None and origAtomId not in atomSiteAtomId:
                            if seqId == 1 or (chainId, seqId - 1) in self.__coordUnobsRes or seqId == min(auth_seq_id_list):
                                continue
                        """
                        atomId = atomId.upper()

                        if not isPolySeq and compId in PARAMAGNETIC_ELEMENTS:
                            if compId not in atomId:
                                continue
                            if compId != atomId:
                                atomId = compId

                        if self.__mrAtomNameMapping is not None:
                            # 6u24: split during annotation
                            if isPolySeq and compId in monDict3 and 'alt_comp_id' in ps and self.__hasNonPolySeq:
                                if _seqId in ps['auth_seq_id']:
                                    authCompId = ps['alt_comp_id'][ps['auth_seq_id'].index(_seqId)]
                                else:
                                    authCompId = ps['alt_comp_id'][ps['auth_seq_id'].index(_seqId_)]
                                if authCompId not in monDict3:
                                    __seqId__, __compId__, __atomId__ = retrieveAtomIdentFromMRMap(self.__ccU, self.__mrAtomNameMapping, _seqId,
                                                                                                   authCompId, atomId, ignoreSeqId=True)
                                    split = 0
                                    for np in self.__nonPolySeq:
                                        if __compId__ in np['comp_id']:
                                            split += 1
                                    if split == 1:
                                        for np in self.__nonPolySeq:
                                            if __compId__ in np['comp_id']:
                                                _factor['chain_id'] = [np['auth_chain_id']]
                                                _factor['seq_id'] = [__seqId__]
                                                _factor['atom_id'] = [__atomId__]
                                        continue

                            if compId not in monDict3\
                               and ((_seqId in ps['auth_seq_id'] or _seqId_ in ps['auth_seq_id'])
                                    or ('alt_auth_seq_id' in ps
                                        and (_seqId in ps['alt_auth_seq_id'] or _seqId_ in ps['alt_auth_seq_id']))):
                                if _seqId in ps['auth_seq_id']:
                                    authCompId = ps['auth_comp_id'][ps['auth_seq_id'].index(_seqId)]
                                elif _seqId_ in ps['auth_seq_id']:
                                    authCompId = ps['auth_comp_id'][ps['auth_seq_id'].index(_seqId_)]
                                elif _seqId in ps['alt_auth_seq_id']:
                                    authCompId = ps['auth_comp_id'][ps['alt_auth_seq_id'].index(_seqId)]
                                else:
                                    authCompId = ps['auth_comp_id'][ps['alt_auth_seq_id'].index(_seqId_)]
                                atomId = retrieveAtomIdFromMRMap(self.__ccU, self.__mrAtomNameMapping, _seqId, authCompId, atomId, coordAtomSite)
                                if coordAtomSite is not None and atomId not in atomSiteAtomId:
                                    if self.__reasons is not None and 'branched_remap' in self.__reasons:
                                        _seqId_ = retrieveOriginalSeqIdFromMRMap(self.__reasons['branched_remap'], chainId, seqId)
                                        if _seqId_ != seqId:
                                            _, _, atomId = retrieveAtomIdentFromMRMap(self.__ccU, self.__mrAtomNameMapping, _seqId_, authCompId, atomId, compId, coordAtomSite)
                                    elif seqId != _seqId:
                                        atomId = retrieveAtomIdFromMRMap(self.__ccU, self.__mrAtomNameMapping, seqId, authCompId, atomId, coordAtomSite)

                        atomIds = self.getAtomIdList(_factor, compId, atomId)

                        if atomSiteAtomId is not None:
                            if not any(_atomId in atomSiteAtomId for _atomId in atomIds):
                                atomId = translateToStdAtomName(atomId, compId, atomSiteAtomId, self.__ccU, False)
                            elif atomId[0] not in pseProBeginCode and not all(_atomId in atomSiteAtomId for _atomId in atomIds):
                                atomIds = [_atomId for _atomId in atomIds if _atomId in atomSiteAtomId]

                        # @see: https://bmrb.io/ref_info/atom_nom.tbl
                        if self.__trust_bmrb_ref_info:
                            pass

                        # @see: https://bmrb.io/macro/files/xplor_to_iupac.Nov140620
                        else:
                            if compId == 'ASN':
                                if atomId == 'HD21':
                                    _atomId = atomId[:-1] + '2'
                                    if self.__nefT.validate_comp_atom(compId, _atomId):
                                        atomIds = self.__nefT.get_valid_star_atom(compId, _atomId)[0]
                                elif atomId == 'HD22':
                                    _atomId = atomId[:-1] + '1'
                                    if self.__nefT.validate_comp_atom(compId, _atomId):
                                        atomIds = self.__nefT.get_valid_star_atom(compId, _atomId)[0]
                            elif compId == 'GLN':
                                if atomId == 'HE21':
                                    _atomId = atomId[:-1] + '2'
                                    if self.__nefT.validate_comp_atom(compId, _atomId):
                                        atomIds = self.__nefT.get_valid_star_atom(compId, _atomId)[0]
                                elif atomId == 'HE22':
                                    _atomId = atomId[:-1] + '1'
                                    if self.__nefT.validate_comp_atom(compId, _atomId):
                                        atomIds = self.__nefT.get_valid_star_atom(compId, _atomId)[0]

                        if coordAtomSite is not None\
                           and not any(_atomId for _atomId in atomIds if _atomId in atomSiteAtomId):
                            if atomId in atomSiteAtomId:
                                atomIds = [atomId]
                            elif 'alt_atom_id' in _factor:
                                _atomId_ = toNefEx(toRegEx(_factor['alt_atom_id']))
                                _atomIds_ = [_atomId for _atomId in atomSiteAtomId if re.match(_atomId_, _atomId)]
                                if len(_atomIds_) > 0:
                                    atomIds = _atomIds_
                            elif seqId == 1 and atomId == 'H1' and self.__csStat.peptideLike(compId) and 'H' in atomSiteAtomId:
                                atomIds = ['H']

                        if atomId.startswith('CEN'):
                            peptide, nucleotide, carbohydrate = self.__csStat.getTypeOfCompId(compId)
                            atomIds = self.__csStat.getCentroidAtoms(compId, False, peptide, nucleotide, carbohydrate)

                        for _atomId in atomIds:
                            ccdCheck = not cifCheck

                            if cifCheck:
                                _atom = None
                                if coordAtomSite is not None:
                                    if _atomId in atomSiteAtomId:
                                        _atom = {}
                                        _atom['comp_id'] = coordAtomSite['comp_id']
                                        _atom['type_symbol'] = coordAtomSite['type_symbol'][atomSiteAtomId.index(_atomId)]
                                    elif _atomId in ('HN1', 'HN2', 'HN3') and ((_atomId[-1] + 'HN') in atomSiteAtomId
                                                                               or ('H' + _atomId[-1]) in atomSiteAtomId):
                                        _atomId = _atomId[-1] + 'HN' if _atomId[-1] + 'HN' in atomSiteAtomId else 'H' + _atomId[-1]
                                        _atom = {}
                                        _atom['comp_id'] = coordAtomSite['comp_id']
                                        _atom['type_symbol'] = coordAtomSite['type_symbol'][atomSiteAtomId.index(_atomId)]
                                    elif 'alt_atom_id' in coordAtomSite and _atomId in coordAtomSite['alt_atom_id']:
                                        _atom = {}
                                        _atom['comp_id'] = coordAtomSite['comp_id']
                                        _atom['type_symbol'] = coordAtomSite['type_symbol'][coordAtomSite['alt_atom_id'].index(_atomId)]
                                        self.__authAtomId = 'auth_atom_id'
                                    elif self.__preferAuthSeq and atomSpecified:
                                        may_exist = False
                                        if self.__ccU.updateChemCompDict(compId):
                                            cca = next((cca for cca in self.__ccU.lastAtomList if cca[self.__ccU.ccaAtomId] == _atomId), None)
                                            if cca is not None and cca[self.__ccU.ccaLeavingAtomFlag] != 'Y':
                                                may_exist = True
                                        _seqKey, _coordAtomSite = self.getCoordAtomSiteOf(chainId, seqId, cifCheck=cifCheck, asis=False)
                                        if _coordAtomSite is not None and not may_exist:
                                            _compId = _coordAtomSite['comp_id']
                                            _atomId = self.getAtomIdList(_factor, _compId, atomId)[0]
                                            if _atomId in _coordAtomSite['atom_id']:
                                                if self.__cur_subtype != 'dist':
                                                    if 'label_seq_scheme' not in self.reasonsForReParsing:
                                                        self.reasonsForReParsing['label_seq_scheme'] = {}
                                                    self.reasonsForReParsing['label_seq_scheme'][self.__cur_subtype] = True
                                                else:
                                                    # _atom = {}
                                                    # _atom['comp_id'] = _compId
                                                    # _atom['type_symbol'] = _coordAtomSite['type_symbol'][_coordAtomSite['atom_id'].index(_atomId)]
                                                    if self.__ccU.updateChemCompDict(compId):
                                                        cca = next((cca for cca in self.__ccU.lastAtomList if cca[self.__ccU.ccaAtomId] == _atomId), None)
                                                        if cca is None or (cca is not None and cca[self.__ccU.ccaLeavingAtomFlag] == 'Y'):
                                                            if 'label_seq_scheme' not in self.reasonsForReParsing:
                                                                self.reasonsForReParsing['label_seq_scheme'] = {}
                                                            if self.__cur_subtype not in self.reasonsForReParsing['label_seq_scheme']:
                                                                self.reasonsForReParsing['label_seq_scheme'][self.__cur_subtype] = True
                                            elif _atomId in ('HN1', 'HN2', 'HN3') and ((_atomId[-1] + 'HN') in _coordAtomSite['atom_id']
                                                                                       or ('H' + _atomId[-1]) in _coordAtomSite['atom_id']):
                                                _atomId = _atomId[-1] + 'HN' if _atomId[-1] + 'HN' in _coordAtomSite['atom_id'] else 'H' + _atomId[-1]
                                                if self.__cur_subtype != 'dist':
                                                    if 'label_seq_scheme' not in self.reasonsForReParsing:
                                                        self.reasonsForReParsing['label_seq_scheme'] = {}
                                                    self.reasonsForReParsing['label_seq_scheme'][self.__cur_subtype] = True
                                                else:
                                                    _atom = {}
                                                    _atom['comp_id'] = _compId
                                                    _atom['type_symbol'] = _coordAtomSite['type_symbol'][_coordAtomSite['atom_id'].index(_atomId)]
                                                    if self.__ccU.updateChemCompDict(compId):
                                                        cca = next((cca for cca in self.__ccU.lastAtomList if cca[self.__ccU.ccaAtomId] == _atomId), None)
                                                        if cca is None or (cca is not None and cca[self.__ccU.ccaLeavingAtomFlag] == 'Y'):
                                                            if 'label_seq_scheme' not in self.reasonsForReParsing:
                                                                self.reasonsForReParsing['label_seq_scheme'] = {}
                                                            if self.__cur_subtype not in self.reasonsForReParsing['label_seq_scheme']:
                                                                self.reasonsForReParsing['label_seq_scheme'][self.__cur_subtype] = True
                                            elif 'alt_atom_id' in _coordAtomSite and _atomId in _coordAtomSite['alt_atom_id']:
                                                if self.__cur_subtype != 'dist':
                                                    if 'label_seq_scheme' not in self.reasonsForReParsing:
                                                        self.reasonsForReParsing['label_seq_scheme'] = {}
                                                    self.reasonsForReParsing['label_seq_scheme'][self.__cur_subtype] = True
                                                else:
                                                    _atom = {}
                                                    _atom['comp_id'] = _compId
                                                    _atom['type_symbol'] = _coordAtomSite['type_symbol'][_coordAtomSite['alt_atom_id'].index(_atomId)]
                                                    if self.__ccU.updateChemCompDict(compId):
                                                        cca = next((cca for cca in self.__ccU.lastAtomList if cca[self.__ccU.ccaAtomId] == _atomId), None)
                                                        if cca is None or (cca is not None and cca[self.__ccU.ccaLeavingAtomFlag] == 'Y'):
                                                            if 'label_seq_scheme' not in self.reasonsForReParsing:
                                                                self.reasonsForReParsing['label_seq_scheme'] = {}
                                                            if self.__cur_subtype not in self.reasonsForReParsing['label_seq_scheme']:
                                                                self.reasonsForReParsing['label_seq_scheme'][self.__cur_subtype] = True
                                    elif _seqId_ in ps['auth_seq_id'] and atomSpecified\
                                            and (self.__reasons is None or 'label_seq_scheme' not in self.__reasons
                                                 or self.__reasons['label_seq_scheme'] is None
                                                 or self.__cur_subtype not in self.__reasons['label_seq_scheme']
                                                 or not self.__reasons['label_seq_scheme'][self.__cur_subtype]):
                                        self.__preferAuthSeq = True
                                        _seqKey, _coordAtomSite = self.getCoordAtomSiteOf(chainId, _seqId_, cifCheck=cifCheck)
                                        if _coordAtomSite is not None:
                                            _compId = _coordAtomSite['comp_id']
                                            _atomId = self.getAtomIdList(_factor, _compId, atomId)[0]
                                            if _atomId in _coordAtomSite['atom_id']:
                                                _atom = {}
                                                _atom['comp_id'] = _compId
                                                _atom['type_symbol'] = _coordAtomSite['type_symbol'][_coordAtomSite['atom_id'].index(_atomId)]
                                                self.__authSeqId = 'auth_seq_id'
                                            elif _atomId in ('HN1', 'HN2', 'HN3') and ((_atomId[-1] + 'HN') in _coordAtomSite['atom_id']
                                                                                       or ('H' + _atomId[-1]) in _coordAtomSite['atom_id']):
                                                _atomId = _atomId[-1] + 'HN' if _atomId[-1] + 'HN' in _coordAtomSite['atom_id'] else 'H' + _atomId[-1]
                                                _atom = {}
                                                _atom['comp_id'] = _compId
                                                _atom['type_symbol'] = _coordAtomSite['type_symbol'][_coordAtomSite['atom_id'].index(_atomId)]
                                                self.__authSeqId = 'auth_seq_id'
                                            elif 'alt_atom_id' in _coordAtomSite and _atomId in _coordAtomSite['alt_atom_id']:
                                                _atom = {}
                                                _atom['comp_id'] = _compId
                                                _atom['type_symbol'] = _coordAtomSite['type_symbol'][_coordAtomSite['alt_atom_id'].index(_atomId)]
                                                self.__authSeqId = 'auth_seq_id'
                                                self.__authAtomId = 'auth_atom_id'
                                            elif not self.__extendAuthSeq:
                                                self.__preferAuthSeq = False
                                        elif not self.__extendAuthSeq:
                                            self.__preferAuthSeq = False

                                elif self.__preferAuthSeq and atomSpecified:
                                    if len(self.atomSelectionSet) == 0:
                                        may_exist = False
                                        if self.__ccU.updateChemCompDict(compId):
                                            cca = next((cca for cca in self.__ccU.lastAtomList if cca[self.__ccU.ccaAtomId] == _atomId), None)
                                            if cca is not None and cca[self.__ccU.ccaLeavingAtomFlag] != 'Y':
                                                may_exist = True
                                        _seqKey, _coordAtomSite = self.getCoordAtomSiteOf(chainId, seqId, cifCheck=cifCheck, asis=False)
                                        if _coordAtomSite is not None and not may_exist:
                                            _compId = _coordAtomSite['comp_id']
                                            _atomId = self.getAtomIdList(_factor, _compId, atomId)[0]
                                            if _atomId in _coordAtomSite['atom_id']:
                                                # _atom = {}
                                                # _atom['comp_id'] = _compId
                                                # _atom['type_symbol'] = _coordAtomSite['type_symbol'][_coordAtomSite['atom_id'].index(_atomId)]
                                                if self.__ccU.updateChemCompDict(compId):
                                                    cca = next((cca for cca in self.__ccU.lastAtomList if cca[self.__ccU.ccaAtomId] == _atomId), None)
                                                    if cca is None or (cca is not None and cca[self.__ccU.ccaLeavingAtomFlag] == 'Y'):
                                                        if 'label_seq_scheme' not in self.reasonsForReParsing:
                                                            self.reasonsForReParsing['label_seq_scheme'] = {}
                                                        if self.__cur_subtype not in self.reasonsForReParsing['label_seq_scheme']:
                                                            self.reasonsForReParsing['label_seq_scheme'][self.__cur_subtype] = True
                                            elif _atomId in ('HN1', 'HN2', 'HN3') and ((_atomId[-1] + 'HN') in _coordAtomSite['atom_id']
                                                                                       or ('H' + _atomId[-1]) in _coordAtomSite['atom_id']):
                                                _atomId = _atomId[-1] + 'HN' if _atomId[-1] + 'HN' in _coordAtomSite['atom_id'] else 'H' + _atomId[-1]
                                                _atom = {}
                                                _atom['comp_id'] = _compId
                                                _atom['type_symbol'] = _coordAtomSite['type_symbol'][_coordAtomSite['atom_id'].index(_atomId)]
                                                if self.__ccU.updateChemCompDict(compId):
                                                    cca = next((cca for cca in self.__ccU.lastAtomList if cca[self.__ccU.ccaAtomId] == _atomId), None)
                                                    if cca is None or (cca is not None and cca[self.__ccU.ccaLeavingAtomFlag] == 'Y'):
                                                        if 'label_seq_scheme' not in self.reasonsForReParsing:
                                                            self.reasonsForReParsing['label_seq_scheme'] = {}
                                                        if self.__cur_subtype not in self.reasonsForReParsing['label_seq_scheme']:
                                                            self.reasonsForReParsing['label_seq_scheme'][self.__cur_subtype] = True
                                            elif 'alt_atom_id' in _coordAtomSite and _atomId in _coordAtomSite['alt_atom_id']:
                                                _atom = {}
                                                _atom['comp_id'] = _compId
                                                _atom['type_symbol'] = _coordAtomSite['type_symbol'][_coordAtomSite['alt_atom_id'].index(_atomId)]
                                                if self.__ccU.updateChemCompDict(compId):
                                                    cca = next((cca for cca in self.__ccU.lastAtomList if cca[self.__ccU.ccaAtomId] == _atomId), None)
                                                    if cca is None or (cca is not None and cca[self.__ccU.ccaLeavingAtomFlag] == 'Y'):
                                                        if 'label_seq_scheme' not in self.reasonsForReParsing:
                                                            self.reasonsForReParsing['label_seq_scheme'] = {}
                                                        if self.__cur_subtype not in self.reasonsForReParsing['label_seq_scheme']:
                                                            self.reasonsForReParsing['label_seq_scheme'][self.__cur_subtype] = True
                                elif _seqId_ in ps['auth_seq_id'] and atomSpecified:
                                    if len(self.atomSelectionSet) == 0\
                                       and (self.__reasons is None or 'label_seq_scheme' not in self.__reasons
                                            or self.__reasons['label_seq_scheme'] is None
                                            or self.__cur_subtype not in self.__reasons['label_seq_scheme']
                                            or not self.__reasons['label_seq_scheme'][self.__cur_subtype]):
                                        self.__preferAuthSeq = True
                                        _seqKey, _coordAtomSite = self.getCoordAtomSiteOf(chainId, _seqId_, cifCheck=cifCheck)
                                        if _coordAtomSite is not None:
                                            _compId = _coordAtomSite['comp_id']
                                            _atomId = self.getAtomIdList(_factor, _compId, atomId)[0]
                                            if _atomId in _coordAtomSite['atom_id']:
                                                _atom = {}
                                                _atom['comp_id'] = _compId
                                                _atom['type_symbol'] = _coordAtomSite['type_symbol'][_coordAtomSite['atom_id'].index(_atomId)]
                                                self.__authSeqId = 'auth_seq_id'
                                                seqKey = _seqKey
                                                chainId, seqId = seqKey
                                                if len(self.atomSelectionSet) > 0:
                                                    self.__setLocalSeqScheme()
                                            elif _atomId in ('HN1', 'HN2', 'HN3') and ((_atomId[-1] + 'HN') in _coordAtomSite['atom_id']
                                                                                       or ('H' + _atomId[-1]) in _coordAtomSite['atom_id']):
                                                _atomId = _atomId[-1] + 'HN' if _atomId[-1] + 'HN' in _coordAtomSite['atom_id'] else 'H' + _atomId[-1]
                                                _atom = {}
                                                _atom['comp_id'] = _compId
                                                _atom['type_symbol'] = _coordAtomSite['type_symbol'][_coordAtomSite['atom_id'].index(_atomId)]
                                                self.__authSeqId = 'auth_seq_id'
                                                seqKey = _seqKey
                                                chainId, seqId = seqKey
                                                if len(self.atomSelectionSet) > 0:
                                                    self.__setLocalSeqScheme()
                                            elif 'alt_atom_id' in _coordAtomSite and _atomId in _coordAtomSite['alt_atom_id']:
                                                _atom = {}
                                                _atom['comp_id'] = _compId
                                                _atom['type_symbol'] = _coordAtomSite['type_symbol'][_coordAtomSite['alt_atom_id'].index(_atomId)]
                                                self.__authSeqId = 'auth_seq_id'
                                                self.__authAtomId = 'auth_atom_id'
                                                seqKey = _seqKey
                                                chainId, seqId = seqKey
                                                if len(self.atomSelectionSet) > 0:
                                                    self.__setLocalSeqScheme()
                                            elif not self.__extendAuthSeq:
                                                self.__preferAuthSeq = False
                                        elif not self.__extendAuthSeq:
                                            self.__preferAuthSeq = False

                                if _atom is not None:
                                    _compIdList = None if 'comp_id' not in _factor else [translateToStdResName(_compId, ccU=self.__ccU) for _compId in _factor['comp_id']]
                                    if ('comp_id' not in _factor or _atom['comp_id'] in _compIdList)\
                                       and ('type_symbol' not in _factor or _atom['type_symbol'] in _factor['type_symbol']):
                                        selection = {'chain_id': chainId, 'seq_id': seqId, 'comp_id': _atom['comp_id'], 'atom_id': _atomId, 'is_poly': isPolySeq}
                                        if len(self.__cur_auth_atom_id) > 0:
                                            selection['auth_atom_id'] = self.__cur_auth_atom_id
                                        if not atomSpecified or not seqSpecified:
                                            if self.__ccU.updateChemCompDict(compId):
                                                cca = next((cca for cca in self.__ccU.lastAtomList if cca[self.__ccU.ccaAtomId] == _atomId), None)
                                                if cca is None or (cca is not None and cca[self.__ccU.ccaLeavingAtomFlag] == 'Y'):
                                                    if atomSiteAtomId is None or _atomId not in atomSiteAtomId:
                                                        continue
                                        _atomSelection.append(selection)
                                else:
                                    ccdCheck = True

                            if (len(_factor['chain_id']) > 1 or len(_factor['seq_id']) > 1 or not isPolySeq) and not atomSpecified:
                                continue

                            if isPolySeq and 'ambig_auth_seq_id' in ps and _seqId in ps['ambig_auth_seq_id']:
                                continue

                            if not isPolySeq and 'alt_auth_seq_id' in ps and _seqId in ps['auth_seq_id'] and _seqId not in ps['alt_auth_seq_id']:
                                continue

                            if isinstance(origAtomId, str) and origAtomId.startswith('*'):
                                continue

                            origAtomId0 = origAtomId[0] if isinstance(origAtomId, list) else origAtomId

                            if isPolySeq and len(_factor['chain_id']) > 1 and self.__con_union_expr:  # D_1300057999: verify if another polymer can take over in union expression
                                hasAltPolymer = False
                                for chainId1, chainId2 in itertools.combinations(_factor['chain_id'], 2):
                                    ps1 = next((ps for ps in (self.__polySeq if isPolySeq else altPolySeq) if ps['auth_chain_id'] == chainId1), None)
                                    if ps1 is not None:
                                        if 'identical_auth_chain_id' in ps1 and chainId2 in ps1['identical_auth_chain_id']:
                                            continue
                                    ps2 = next((ps for ps in (self.__polySeq if isPolySeq else altPolySeq) if ps['auth_chain_id'] == chainId2), None)
                                    if ps2 is not None and ps1['comp_id'] != ps2['comp_id']:
                                        hasAltPolymer = True
                                        break
                                if hasAltPolymer:
                                    hasAltPolymer = False
                                    for chainId2 in _factor['chain_id']:
                                        if chainId2 == chainId:
                                            continue
                                        ps2 = next((ps for ps in (self.__polySeq if isPolySeq else altPolySeq) if ps['auth_chain_id'] == chainId2), None)
                                        if ps2 is None or ('identical_auth_chain_id' in ps2 and chainId in ps2['identical_auth_chain_id']):
                                            continue
                                        if seqId in ps2['auth_seq_id']:
                                            _, _coordAtomSite = self.getCoordAtomSiteOf(chainId2, seqId, cifCheck=cifCheck)
                                            if _coordAtomSite is not None:
                                                _atomSiteAtomId = _coordAtomSite['atom_id']
                                                if origAtomId0 in _atomSiteAtomId:
                                                    hasAltPolymer = True
                                                    break
                                                _compId = ps2['comp_id'][ps2['auth_seq_id'].index(seqId)]
                                                _origAtomId0 = translateToStdAtomName(origAtomId0, _compId, _atomSiteAtomId, self.__ccU, False)
                                                __origAtomId0, _, details = self.__nefT.get_valid_star_atom(_compId, _origAtomId0, leave_unmatched=True)
                                                if details is None and __origAtomId0[0] in _atomSiteAtomId:
                                                    hasAltPolymer = True
                                                    break
                                    if hasAltPolymer:
                                        continue

                            if ccdCheck and compId is not None:
                                _compIdList = None if 'comp_id' not in _factor else [translateToStdResName(_compId, ccU=self.__ccU) for _compId in _factor['comp_id']]
                                if self.__ccU.updateChemCompDict(compId) and ('comp_id' not in _factor or compId in _compIdList):
                                    if len(origAtomId) > 1:
                                        typeSymbols = set()
                                        for _atomId_ in origAtomId:
                                            typeSymbol = next((cca[self.__ccU.ccaTypeSymbol] for cca in self.__ccU.lastAtomList if cca[self.__ccU.ccaAtomId] == _atomId_), None)
                                            if typeSymbol is not None:
                                                typeSymbols.add(typeSymbol)
                                                if len(typeSymbols) > 1:
                                                    break
                                        if len(typeSymbols) > 1:
                                            continue
                                    cca = next((cca for cca in self.__ccU.lastAtomList if cca[self.__ccU.ccaAtomId] == _atomId), None)
                                    if cca is not None and cca[self.__ccU.ccaLeavingAtomFlag] == 'Y' and (not atomSpecified or not seqSpecified):
                                        continue
                                    if cca is not None and ('type_symbol' not in _factor or cca[self.__ccU.ccaTypeSymbol] in _factor['type_symbol']):
                                        selection = {'chain_id': chainId, 'seq_id': seqId, 'comp_id': compId, 'atom_id': _atomId, 'is_poly': isPolySeq}
                                        if len(self.__cur_auth_atom_id) > 0:
                                            selection['auth_atom_id'] = self.__cur_auth_atom_id
                                        if _atomId.startswith('HOP') and isinstance(origAtomId, str) and '*' in origAtomId:
                                            continue
                                        if not seqSpecified:
                                            continue
                                        _atomSelection.append(selection)
                                        if cifCheck and seqKey not in self.__coordUnobsRes and self.__ccU.lastChemCompDict['_chem_comp.pdbx_release_status'] == 'REL':
                                            if self.__cur_subtype != 'plane' and coordAtomSite is not None:
                                                checked = False
                                                if seqId == 1 or (chainId, seqId - 1) in self.__coordUnobsRes or seqId == min(auth_seq_id_list):
                                                    if coordAtomSite is not None and ((_atomId in aminoProtonCode and 'H1' in atomSiteAtomId)
                                                                                      or _atomId == 'P' or _atomId.startswith('HOP')):
                                                        checked = True
                                                if _atomId[0] in protonBeginCode:
                                                    bondedTo = self.__ccU.getBondedAtoms(compId, _atomId)
                                                    if len(bondedTo) > 0 and bondedTo[0][0] != 'P':
                                                        if coordAtomSite is not None and bondedTo[0] in atomSiteAtomId:
                                                            if cca[self.__ccU.ccaLeavingAtomFlag] != 'Y'\
                                                               or (self.__csStat.peptideLike(compId)
                                                                   and cca[self.__ccU.ccaNTerminalAtomFlag] == 'N'
                                                                   and cca[self.__ccU.ccaCTerminalAtomFlag] == 'N'):
                                                                checked = True
                                                                if len(origAtomId) == 1:
                                                                    _atomSelection[-1]['hydrogen_not_instantiated'] = True
                                                                    self.__f.append(f"[Hydrogen not instantiated] {self.__getCurrentRestraint()}"
                                                                                    f"{chainId}:{seqId}:{compId}:{origAtomId0} is not properly instantiated in the coordinates. "
                                                                                    "Please re-upload the model file.")
                                                        elif bondedTo[0][0] == 'O':
                                                            checked = True
                                                if seqId == max(auth_seq_id_list) or (chainId, seqId + 1) in self.__coordUnobsRes and self.__csStat.peptideLike(compId):
                                                    if coordAtomSite is not None and _atomId in carboxylCode\
                                                       and not isCyclicPolymer(self.__cR, self.__polySeq, chainId, self.__representativeModelId,
                                                                               self.__representativeAltId, self.__modelNumName):
                                                        self.__f.append(f"[Coordinate issue] {self.__getCurrentRestraint()}"
                                                                        f"{chainId}:{seqId}:{compId}:{origAtomId0} is not properly instantiated in the coordinates. "
                                                                        "Please re-upload the model file.")
                                                        checked = True

                                                if not checked and not self.__cur_union_expr:
                                                    if chainId in LARGE_ASYM_ID:
                                                        if isPolySeq and not self.__preferAuthSeq\
                                                           and ('label_seq_offset' not in self.reasonsForReParsing
                                                                or chainId not in self.reasonsForReParsing['label_seq_offset']):
                                                            if self.__csStat.peptideLike(compId) and origAtomId0.startswith('HT'):
                                                                pass
                                                            else:
                                                                if 'label_seq_offset' not in self.reasonsForReParsing:
                                                                    self.reasonsForReParsing['label_seq_offset'] = {}
                                                                offset = self.getLabelSeqOffsetDueToUnobs(ps)
                                                                self.reasonsForReParsing['label_seq_offset'][chainId] = offset
                                                                if offset != 0:
                                                                    if 'label_seq_scheme' not in self.reasonsForReParsing:
                                                                        self.reasonsForReParsing['label_seq_scheme'] = {}
                                                                    if self.__cur_subtype not in self.reasonsForReParsing['label_seq_scheme']:
                                                                        self.reasonsForReParsing['label_seq_scheme'][self.__cur_subtype] = True
                                                        if len(self.__polySeq) == 1\
                                                           and (seqId < 1
                                                                or (compId == 'ACE' and seqId == min(self.__polySeq[0]['auth_seq_id']) - 1)
                                                                or (compId == 'NH2' and seqId == max(self.__polySeq[0]['auth_seq_id']) + 1)):
                                                            self.__f.append(f"[Atom not found] {self.__getCurrentRestraint()}"
                                                                            f"{chainId}:{seqId}:{compId}:{origAtomId0} is not present in the coordinates. "
                                                                            f"The residue number '{seqId}' is not present in polymer sequence "
                                                                            f"of chain {chainId} of the coordinates. "
                                                                            "Please update the sequence in the Macromolecules page.")
                                                            if 'alt_chain_id' in _factor:
                                                                self.__failure_chain_ids.append(chainId)
                                                        else:
                                                            if len(chainIds) > 1 and isPolySeq and not self.__extendAuthSeq:
                                                                __preferAuthSeq = self.__preferAuthSeq
                                                                self.__preferAuthSeq = False
                                                                for __chainId in chainIds:
                                                                    if __chainId == chainId:
                                                                        continue
                                                                    __psList = [__ps for __ps in (self.__polySeq if isPolySeq else altPolySeq)
                                                                                if __ps['auth_chain_id'] == __chainId]
                                                                    if len(__psList) == 0:
                                                                        continue
                                                                    for __ps in __psList:
                                                                        __seqId = self.getRealSeqId(__ps, seqId, isPolySeq)[0]
                                                                        _, __coordAtomSite = self.getCoordAtomSiteOf(__chainId, __seqId, cifCheck=cifCheck)
                                                                        if __coordAtomSite is not None\
                                                                           and ((seqId in ps['auth_seq_id'] and ps['seq_id'][ps['auth_seq_id'].index(seqId)] != seqId)  # 2lr1, 2lqc
                                                                                or seqId != __seqId):  # 1qkg
                                                                            __compId = __coordAtomSite['comp_id']
                                                                            __atomIds = self.getAtomIdList(_factor, __compId, atomId)
                                                                            if compId != __compId and __atomIds[0] in __coordAtomSite['atom_id']:
                                                                                if 'label_seq_scheme' not in self.reasonsForReParsing:
                                                                                    self.reasonsForReParsing['label_seq_scheme'] = {}
                                                                                if self.__cur_subtype not in self.reasonsForReParsing['label_seq_scheme']:
                                                                                    self.reasonsForReParsing['label_seq_scheme'][self.__cur_subtype] = True
                                                                                if isChainSpecified:
                                                                                    if 'inhibit_label_seq_scheme' not in self.reasonsForReParsing:
                                                                                        self.reasonsForReParsing['inhibit_label_seq_scheme'] = {}
                                                                                    if chainId not in self.reasonsForReParsing['inhibit_label_seq_scheme']:
                                                                                        self.reasonsForReParsing['inhibit_label_seq_scheme'][chainId] = {}
                                                                                    self.reasonsForReParsing['inhibit_label_seq_scheme'][chainId][self.__cur_subtype] = True
                                                                                break
                                                                self.__preferAuthSeq = __preferAuthSeq
                                                            if isPolySeq and not isChainSpecified and seqSpecified and len(_factor['chain_id']) == 1\
                                                               and _factor['chain_id'][0] != chainId and compId in monDict3:
                                                                continue
                                                            if self.__csStat.peptideLike(compId) and origAtomId0.startswith('HT'):
                                                                _atomSelection.remove(selection)
                                                                continue
                                                            if self.__cur_subtype == 'dihed' and _atomId == 'P' and self.__csStat.getTypeOfCompId(compId)[1]:
                                                                continue
                                                            warn_title = 'Anomalous data' if self.__preferAuthSeq and compId == 'PRO' and origAtomId0 in aminoProtonCode\
                                                                and (seqId != 1 and (chainId, seqId - 1) not in self.__coordUnobsRes and seqId != min(auth_seq_id_list))\
                                                                else 'Atom not found'
                                                            if seqKey in self.__coordUnobsAtom\
                                                               and (_atomId in self.__coordUnobsAtom[seqKey]['atom_ids']
                                                                    or (_atomId[0] in protonBeginCode
                                                                        and any(bondedTo for bondedTo in self.__ccU.getBondedAtoms(compId, _atomId, exclProton=True)
                                                                                if bondedTo in self.__coordUnobsAtom[seqKey]['atom_ids']))):
                                                                warn_title = 'Coordinate issue'
                                                            if (compId == 'ASP' and _atomId == 'HD1') or (compId == 'GLU' and _atomId == 'HE1'):
                                                                warn_title = 'Hydrogen not instantiated'
                                                            self.__f.append(f"[{warn_title}] {self.__getCurrentRestraint()}"
                                                                            f"{chainId}:{seqId}:{compId}:{origAtomId0} is not present in the coordinates.")
                                                            if warn_title in ('Coordinate issue', 'Hydrogen not instantiated'):
                                                                _atomSelection.append(selection)
                                                                continue
                                                            if 'alt_chain_id' in _factor:
                                                                self.__failure_chain_ids.append(chainId)
                                    elif cca is None and 'type_symbol' not in _factor and 'atom_ids' not in _factor:
                                        if seqId == 1 or (chainId, seqId - 1) in self.__coordUnobsRes or seqId == min(auth_seq_id_list):
                                            if coordAtomSite is not None and ((_atomId in aminoProtonCode and 'H1' in atomSiteAtomId)
                                                                              or _atomId == 'P' or _atomId.startswith('HOP')):
                                                continue
                                        if cifCheck and self.__cur_subtype != 'plane'\
                                           and 'seq_id' in _factor and len(_factor['seq_id']) == 1\
                                           and (self.__reasons is None or 'non_poly_remap' not in self.__reasons)\
                                           and not self.__cur_union_expr:
                                            if chainId in LARGE_ASYM_ID:
                                                if len(self.__polySeq) == 1\
                                                   and (seqId < 1
                                                        or (compId == 'ACE' and seqId == min(self.__polySeq[0]['auth_seq_id']) - 1)
                                                        or (compId == 'NH2' and seqId == max(self.__polySeq[0]['auth_seq_id']) + 1)):
                                                    self.__f.append(f"[Atom not found] {self.__getCurrentRestraint()}"
                                                                    f"{chainId}:{seqId}:{compId}:{origAtomId0} is not present in the coordinates. "
                                                                    f"The residue number '{seqId}' is not present in polymer sequence "
                                                                    f"of chain {chainId} of the coordinates. "
                                                                    "Please update the sequence in the Macromolecules page.")
                                                    if 'alt_chain_id' in _factor:
                                                        self.__failure_chain_ids.append(chainId)
                                                elif seqSpecified:
                                                    if resolved and altPolySeq is not None:
                                                        continue
                                                    if len(chainIds) > 1 and isPolySeq and not self.__extendAuthSeq:
                                                        __preferAuthSeq = self.__preferAuthSeq
                                                        self.__preferAuthSeq = False
                                                        for __chainId in chainIds:
                                                            if __chainId == chainId:
                                                                continue
                                                            __psList = [__ps for __ps in (self.__polySeq if isPolySeq else altPolySeq)
                                                                        if __ps['auth_chain_id'] == __chainId]
                                                            if len(__psList) == 0:
                                                                continue
                                                            for __ps in __psList:
                                                                __seqId = self.getRealSeqId(__ps, seqId, isPolySeq)[0]
                                                                _, __coordAtomSite = self.getCoordAtomSiteOf(__chainId, __seqId, cifCheck=cifCheck)
                                                                if __coordAtomSite is not None\
                                                                   and ((seqId in ps['auth_seq_id'] and ps['seq_id'][ps['auth_seq_id'].index(seqId)] != seqId)  # 2lr1, 2lqc
                                                                        or seqId != __seqId):  # 1qkg
                                                                    __compId = __coordAtomSite['comp_id']
                                                                    __atomIds = self.getAtomIdList(_factor, __compId, atomId)
                                                                    if compId != __compId and __atomIds[0] in __coordAtomSite['atom_id']\
                                                                       and self.__csStat.getTypeOfCompId(compId) == self.__csStat.getTypeOfCompId(__compId):  # 2ld5
                                                                        if 'label_seq_scheme' not in self.reasonsForReParsing:
                                                                            self.reasonsForReParsing['label_seq_scheme'] = {}
                                                                        if self.__cur_subtype not in self.reasonsForReParsing['label_seq_scheme']:
                                                                            self.reasonsForReParsing['label_seq_scheme'][self.__cur_subtype] = True
                                                                            if 'segment_id' in _factor and 'assert_label_scheme_scheme' not in self.reasonsForReParsing:
                                                                                self.reasonsForReParsing['assert_label_seq_scheme'] = True  # 2m0k
                                                                        if isChainSpecified:
                                                                            if 'inhibit_label_seq_scheme' not in self.reasonsForReParsing:
                                                                                self.reasonsForReParsing['inhibit_label_seq_scheme'] = {}
                                                                            if chainId not in self.reasonsForReParsing['inhibit_label_seq_scheme']:
                                                                                self.reasonsForReParsing['inhibit_label_seq_scheme'][chainId] = {}
                                                                            self.reasonsForReParsing['inhibit_label_seq_scheme'][chainId][self.__cur_subtype] = True
                                                                        break
                                                        self.__preferAuthSeq = __preferAuthSeq
                                                    if isPolySeq and not isChainSpecified and seqSpecified and len(_factor['chain_id']) == 1\
                                                       and _factor['chain_id'][0] != chainId and compId in monDict3:
                                                        continue
                                                    # 2mgt
                                                    if self.__hasNonPoly and len(_factor['seq_id']) == 1 and len(_factor['atom_id']) == 1:
                                                        if self.__uniqAtomIdToSeqKey is not None and _atomId in self.__uniqAtomIdToSeqKey:  # 7jk8
                                                            if 'np_atom_id_remap' not in self.reasonsForReParsing:
                                                                self.reasonsForReParsing['np_atom_id_remap'] = {}
                                                            if _atomId not in self.reasonsForReParsing['np_atom_id_remap']:
                                                                self.reasonsForReParsing['np_atom_id_remap'][_atomId] = self.__uniqAtomIdToSeqKey[_atomId]
                                                        _coordAtomSite = None
                                                        ligands = 0
                                                        for np in self.__nonPoly:
                                                            if np['auth_chain_id'] == chainId and atomId == np['comp_id'][0]:
                                                                ligands += len(np['seq_id'])
                                                        if ligands == 0:
                                                            for np in self.__nonPoly:
                                                                if 'alt_comp_id' in np and np['auth_chain_id'] == chainId and atomId == np['alt_comp_id'][0]:
                                                                    ligands += len(np['seq_id'])
                                                        if ligands == 0:
                                                            for np in self.__nonPoly:
                                                                _, _coordAtomSite = self.getCoordAtomSiteOf(np['auth_chain_id'], np['seq_id'][0], cifCheck=cifCheck)
                                                                if _coordAtomSite is not None and atomId in _coordAtomSite['atom_id']:
                                                                    ligands += len(np['seq_id'])
                                                        if ligands == 1:
                                                            checked = False
                                                            if 'np_seq_id_remap' not in self.reasonsForReParsing:
                                                                self.reasonsForReParsing['np_seq_id_remap'] = {}
                                                            srcSeqId = _factor['seq_id'][0]
                                                            for np in self.__nonPoly:
                                                                if atomId == np['comp_id'][0]\
                                                                   or ('alt_comp_id' in np and atomId == np['alt_comp_id'][0]):
                                                                    dstSeqId = np['seq_id'][0]
                                                                    if chainId not in self.reasonsForReParsing['np_seq_id_remap']:
                                                                        self.reasonsForReParsing['np_seq_id_remap'][chainId] = {}
                                                                    if srcSeqId in self.reasonsForReParsing['np_seq_id_remap'][chainId]:
                                                                        if self.reasonsForReParsing['np_seq_id_remap'][chainId][srcSeqId] is not None:
                                                                            if self.reasonsForReParsing['np_seq_id_remap'][chainId][srcSeqId] != dstSeqId:
                                                                                self.reasonsForReParsing['np_seq_id_remap'][chainId][srcSeqId] = None
                                                                            else:
                                                                                checked = True
                                                                    else:
                                                                        self.reasonsForReParsing['np_seq_id_remap'][chainId][srcSeqId] = dstSeqId
                                                                        checked = True
                                                            for np in self.__nonPoly:
                                                                if _coordAtomSite is not None and atomId in _coordAtomSite['atom_id']:
                                                                    dstSeqId = np['seq_id'][0]
                                                                    if chainId not in self.reasonsForReParsing['np_seq_id_remap']:
                                                                        self.reasonsForReParsing['np_seq_id_remap'][chainId] = {}
                                                                    if srcSeqId in self.reasonsForReParsing['np_seq_id_remap'][chainId]:
                                                                        if self.reasonsForReParsing['np_seq_id_remap'][chainId][srcSeqId] is not None:
                                                                            if self.reasonsForReParsing['np_seq_id_remap'][chainId][srcSeqId] != dstSeqId:
                                                                                self.reasonsForReParsing['np_seq_id_remap'][chainId][srcSeqId] = None
                                                                            else:
                                                                                checked = True
                                                                    else:
                                                                        self.reasonsForReParsing['np_seq_id_remap'][chainId][srcSeqId] = dstSeqId
                                                                        checked = True
                                                            if checked and isPolySeq and (self.__reasons is None
                                                                                          or (self.__reasons is not None and 'np_seq_id_remap' in self.__reasons)):
                                                                continue
                                                        # 2n3r
                                                        elif ligands > 1 and isPolySeq and self.__reasons is not None and 'np_seq_id_remap' in self.__reasons\
                                                                and retrieveRemappedSeqId(self.__reasons['np_seq_id_remap'], chainId, seqId)[0] is not None:
                                                            continue
                                                    if extSeqScheme:
                                                        self.__f.append(f"[Sequence mismatch warning] {self.__getCurrentRestraint()}"
                                                                        f"The residue '{seqId}:{compId}' is not present in polymer sequence "
                                                                        f"of chain {chainId} of the coordinates. "
                                                                        "Please update the sequence in the Macromolecules page.")
                                                        if 'expected_comp_id' not in _factor:
                                                            _factor['expected_comp_id'] = [compId]
                                                        if compId not in _factor['expected_comp_id']:
                                                            _factor['expected_comp_id'].append(compId)
                                                        continue
                                                    if self.__csStat.peptideLike(compId) and origAtomId0.startswith('HT'):
                                                        continue
                                                    if self.__cur_subtype == 'dihed' and _atomId == 'P' and self.__csStat.getTypeOfCompId(compId)[1]:
                                                        continue
                                                    warn_title = 'Anomalous data' if self.__preferAuthSeq and compId == 'PRO' and origAtomId0 in aminoProtonCode\
                                                        and (seqId != 1 and (chainId, seqId - 1) not in self.__coordUnobsRes and seqId != min(auth_seq_id_list))\
                                                        else 'Atom not found'
                                                    if seqKey in self.__coordUnobsAtom\
                                                       and (_atomId in self.__coordUnobsAtom[seqKey]['atom_ids']
                                                            or (_atomId[0] in protonBeginCode
                                                                and any(bondedTo for bondedTo in self.__ccU.getBondedAtoms(compId, _atomId, exclProton=True)
                                                                        if bondedTo in self.__coordUnobsAtom[seqKey]['atom_ids']))):
                                                        warn_title = 'Coordinate issue'
                                                    if (compId == 'ASP' and _atomId == 'HD1') or (compId == 'GLU' and _atomId == 'HE1'):
                                                        warn_title = 'Hydrogen not instantiated'
                                                    self.__f.append(f"[{warn_title}] {self.__getCurrentRestraint()}"
                                                                    f"{chainId}:{seqId}:{compId}:{origAtomId0} is not present in the coordinates.")
                                                    if warn_title in ('Coordinate issue', 'Hydrogen not instantiated'):
                                                        continue
                                                    if self.__cur_subtype == 'dist' and isPolySeq and isChainSpecified and compId in monDict3 and self.__csStat.peptideLike(compId):
                                                        self.checkDistSequenceOffset(chainId, seqId, compId, origAtomId0)
                                                    if 'alt_chain_id' in _factor:
                                                        self.__failure_chain_ids.append(chainId)

        return foundCompId

    def getRealCompId(self, compId: str) -> str:
        if self.__ccU.updateChemCompDict(compId, False):
            if self.__ccU.lastChemCompDict['_chem_comp.pdbx_release_status'] == 'OBS' and '_chem_comp.pdbx_replaced_by' in self.__ccU.lastChemCompDict:
                replacedBy = self.__ccU.lastChemCompDict['_chem_comp.pdbx_replaced_by']
                if replacedBy not in emptyValue and self.__ccU.updateChemCompDict(replacedBy):
                    return replacedBy
        return compId

    def getOrigSeqId(self, ps: dict, seqId: int, isPolySeq: bool = True) -> Optional[int]:
        offset = 0
        if not self.__preferAuthSeq:
            chainId = ps['chain_id']
            if isPolySeq and self.__reasons is not None and 'label_seq_offset' in self.__reasons\
               and chainId in self.__reasons['label_seq_offset']:
                offset = self.__reasons['label_seq_offset'][chainId]
            if isPolySeq and self.__reasons is not None and 'global_sequence_offset' in self.__reasons\
               and ps['auth_chain_id'] in self.__reasons['global_sequence_offset']:
                offset = self.__reasons['global_sequence_offset'][ps['auth_chain_id']]
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
                        if isinstance(offset, dict):
                            return None
                if seqId + offset in ps['auth_seq_id']:
                    return seqId + offset
                if offset != 0 and 'gap_in_auth_seq' in ps and ps['gap_in_auth_seq']:
                    for shift in range(1, 100):
                        if seqId + shift + offset in ps['auth_seq_id']:
                            idx = ps['auth_seq_id'].index(seqId + shift + offset) - shift
                            if 0 <= idx < len(ps['auth_seq_id']):
                                return ps['auth_seq_id'][idx]
                        if seqId - shift + offset in ps['auth_seq_id']:
                            idx = ps['auth_seq_id'].index(seqId - shift + offset) + shift
                            if 0 <= idx < len(ps['auth_seq_id']):
                                return ps['auth_seq_id'][idx]
            seqKey = (ps['chain_id' if isPolySeq else 'auth_chain_id'], seqId + offset)
            if seqKey in self.__labelToAuthSeq:
                _, _seqId = self.__labelToAuthSeq[seqKey]
                return _seqId
            if seqKey[1] in ps['seq_id']:
                return ps['auth_seq_id'][ps['seq_id'].index(seqKey[1])]
        else:
            if isPolySeq and self.__reasons is not None and 'global_sequence_offset' in self.__reasons\
               and ps['auth_chain_id'] in self.__reasons['global_sequence_offset']:
                offset = self.__reasons['global_sequence_offset'][ps['auth_chain_id']]
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
                        if isinstance(offset, dict):
                            return None
        if seqId + offset in ps['auth_seq_id']:
            return seqId + offset
        if offset != 0 and 'gap_in_auth_seq' in ps and ps['gap_in_auth_seq']:
            for shift in range(1, 100):
                if seqId + shift + offset in ps['auth_seq_id']:
                    idx = ps['auth_seq_id'].index(seqId + shift + offset) - shift
                    if 0 <= idx < len(ps['auth_seq_id']):
                        return ps['auth_seq_id'][idx]
                if seqId - shift + offset in ps['auth_seq_id']:
                    idx = ps['auth_seq_id'].index(seqId - shift + offset) + shift
                    if 0 <= idx < len(ps['auth_seq_id']):
                        return ps['auth_seq_id'][idx]
        return seqId

    def getRealSeqId(self, ps: dict, seqId: int, isPolySeq: bool = True) -> Tuple[Optional[int], Optional[str], bool]:
        offset = 0
        preferLabelSeq = False
        if self.__reasons is not None and 'segment_id_mismatch' in self.__reasons and 'segment_id_match_stats' in self.__reasons:
            for k, v in self.__reasons['segment_id_mismatch'].items():
                if v == ps['auth_chain_id'] and 'identical_auth_chain_id' not in ps:  # prevent unexpected sequence scheme switch (6l8v)
                    if k in self.__reasons['segment_id_match_stats']:
                        if v in self.__reasons['segment_id_match_stats'][k] and self.__reasons['segment_id_match_stats'][k][v] == 0:
                            # no hope for auth sequence scheme (2mnz)
                            preferLabelSeq = True
                            break
        inhibitLabelSeq = self.__reasons is not None and 'inhibit_label_seq_scheme' in self.__reasons\
            and ps['auth_chain_id'] in self.__reasons['inhibit_label_seq_scheme']
        if (not self.__preferAuthSeq or preferLabelSeq) and not inhibitLabelSeq:
            chainId = ps['chain_id']
            if isPolySeq and self.__reasons is not None and 'label_seq_offset' in self.__reasons\
               and chainId in self.__reasons['label_seq_offset']:
                offset = self.__reasons['label_seq_offset'][chainId]
            if isPolySeq and self.__reasons is not None and 'global_sequence_offset' in self.__reasons\
               and ps['auth_chain_id'] in self.__reasons['global_sequence_offset']:
                offset = self.__reasons['global_sequence_offset'][ps['auth_chain_id']]
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
                        if isinstance(offset, dict):
                            return None, None, False
                if seqId + offset in ps['auth_seq_id']:
                    return seqId + offset, ps['comp_id'][ps['auth_seq_id'].index(seqId + offset)], False
                if offset != 0 and 'gap_in_auth_seq' in ps and ps['gap_in_auth_seq']:
                    for shift in range(1, 100):
                        if seqId + shift + offset in ps['auth_seq_id']:
                            idx = ps['auth_seq_id'].index(seqId + shift + offset) - shift
                            if 0 <= idx < len(ps['auth_seq_id']):
                                return ps['auth_seq_id'][idx], ps['comp_id'][idx], False
                        if seqId - shift + offset in ps['auth_seq_id']:
                            idx = ps['auth_seq_id'].index(seqId - shift + offset) + shift
                            if 0 <= idx < len(ps['auth_seq_id']):
                                return ps['auth_seq_id'][idx], ps['comp_id'][idx], False
            seqKey = (ps['chain_id' if isPolySeq else 'auth_chain_id'], seqId + offset)
            if seqKey in self.__labelToAuthSeq:
                _, _seqId = self.__labelToAuthSeq[seqKey]
                if _seqId in ps['auth_seq_id']:
                    return _seqId, ps['comp_id'][ps['seq_id'].index(seqId + offset)
                                                 if seqId + offset in ps['seq_id']
                                                 else ps['auth_seq_id'].index(_seqId)], False
                if seqKey[1] in ps['seq_id']:  # resolve conflict between label/auth sequence schemes of polymer/non-polymer (2l90)
                    idx = ps['seq_id'].index(seqKey[1])
                    return ps['auth_seq_id'][idx], ps['comp_id'][idx], False
        else:
            if isPolySeq and self.__reasons is not None and 'global_sequence_offset' in self.__reasons\
               and ps['auth_chain_id'] in self.__reasons['global_sequence_offset']:
                offset = self.__reasons['global_sequence_offset'][ps['auth_chain_id']]
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
                        if isinstance(offset, dict):
                            return None, None, False
        if seqId + offset in ps['auth_seq_id']:
            return seqId + offset, ps['comp_id'][ps['auth_seq_id'].index(seqId + offset)], False
        if self.__reasons is not None and 'extend_seq_scheme' in self.__reasons:
            _ps = next((_ps for _ps in self.__reasons['extend_seq_scheme'] if _ps['chain_id'] == ps['auth_chain_id']), None)
            if _ps is not None:
                if seqId + offset in _ps['seq_id']:
                    return seqId + offset, _ps['comp_id'][_ps['seq_id'].index(seqId + offset)], True
        if offset != 0 and 'gap_in_auth_seq' in ps and ps['gap_in_auth_seq']:
            for shift in range(1, 100):
                if seqId + shift + offset in ps['auth_seq_id']:
                    idx = ps['auth_seq_id'].index(seqId + shift + offset) - shift
                    if 0 <= idx < len(ps['auth_seq_id']):
                        return ps['auth_seq_id'][idx], ps['comp_id'][idx], False
                if seqId - shift + offset in ps['auth_seq_id']:
                    idx = ps['auth_seq_id'].index(seqId - shift + offset) + shift
                    if 0 <= idx < len(ps['auth_seq_id']):
                        return ps['auth_seq_id'][idx], ps['comp_id'][idx], False
        return seqId, None, False

    def getRealChainId(self, chainId: str) -> str:
        if self.__reasons is not None and 'segment_id_mismatch' in self.__reasons and chainId in self.__reasons['segment_id_mismatch']:
            _chainId = self.__reasons['segment_id_mismatch'][chainId]
            if _chainId is not None:
                chainId = _chainId
        return chainId

    def updateSegmentIdDict(self, factor: dict, chainId: str, isPolymer: Optional[bool], valid: bool):
        if self.__reasons is not None or 'alt_chain_id' not in factor\
           or len(self.reasonsForReParsing) == 0 or 'segment_id_mismatch' not in self.reasonsForReParsing:
            return
        altChainId = factor['alt_chain_id']
        if altChainId not in self.reasonsForReParsing['segment_id_mismatch']:
            return
        if 'atom_id' in factor and len(factor['atom_id']) == 1 and self.__polyPeptide:  # 7lgi
            atomId = factor['atom_id'][0]
            if atomId in aminoProtonCode or atomId in carboxylCode or atomId in jcoupBbPairCode:
                if self.__polyDeoxyribonucleotide or self.__polyRibonucleotide or self.__hasBranched:  # 2n8a, 4b1q (branched)
                    return
                if self.__cur_subtype == 'dist' and not valid:
                    return  # D_1300057999
        if chainId not in self.reasonsForReParsing['segment_id_match_stats'][altChainId]:
            self.reasonsForReParsing['segment_id_match_stats'][altChainId][chainId] = 0
            self.reasonsForReParsing['segment_id_poly_type_stats'][altChainId]['polymer'] = 0
            self.reasonsForReParsing['segment_id_poly_type_stats'][altChainId]['non-polymer'] = 0
        checked = False
        if not valid and chainId not in self.__failure_chain_ids and chainId in self.__atomIdSetPerChain:
            if 'atom_id' in factor:
                for atomId in factor['atom_id']:
                    if atomId in self.__atomIdSetPerChain[chainId]:
                        checked = True  # 7d3v
                        break
        if valid or checked:
            self.reasonsForReParsing['segment_id_match_stats'][altChainId][chainId] += 1
            if isPolymer is not None:
                if isPolymer:
                    self.reasonsForReParsing['segment_id_poly_type_stats'][altChainId]['polymer'] += 1
                else:
                    self.reasonsForReParsing['segment_id_poly_type_stats'][altChainId]['non-poly'] += 1
        else:
            for _chainId in factor['chain_id']:
                if _chainId in self.__failure_chain_ids or not checked:
                    if _chainId not in self.reasonsForReParsing['segment_id_match_stats'][altChainId]:
                        self.reasonsForReParsing['segment_id_match_stats'][altChainId][_chainId] = 0
                        self.reasonsForReParsing['segment_id_poly_type_stats'][altChainId]['polymer'] = 0
                        self.reasonsForReParsing['segment_id_poly_type_stats'][altChainId]['non-poly'] = 0
                    self.reasonsForReParsing['segment_id_match_stats'][altChainId][_chainId] -= 1
                    if isPolymer is not None:
                        if isPolymer:
                            self.reasonsForReParsing['segment_id_poly_type_stats'][altChainId]['polymer'] -= 1
                        else:
                            self.reasonsForReParsing['segment_id_poly_type_stats'][altChainId]['non-poly'] -= 1
        # try to avoid multiple segment_id assignments
        for k, _stats in self.reasonsForReParsing['segment_id_match_stats'].items():
            if k == altChainId:
                continue
            if chainId in _stats:
                _stats[chainId] -= 1
        stats = self.reasonsForReParsing['segment_id_match_stats'][altChainId]
        _chainId = max(stats, key=lambda key: stats[key])[0]
        _score = stats[_chainId]
        if _score > 0 or len(stats) == 1:  # 2mtk
            self.reasonsForReParsing['segment_id_mismatch'][altChainId] = _chainId
        elif _score < 0:
            __chainId = min(stats, key=lambda key: stats[key])[0]
            __score = stats[__chainId]
            if _score == __score and _chainId != __chainId and altChainId in self.reasonsForReParsing['segment_id_mismatch']:  # 2la5
                del self.reasonsForReParsing['segment_id_mismatch'][altChainId]  # 2lzs

    def getCoordAtomSiteOf(self, chainId: str, seqId: int, compId: Optional[str] = None, cifCheck: bool = True, asis: bool = True
                           ) -> Tuple[Tuple[str, int], Optional[dict]]:
        seqKey = (chainId, seqId)
        if asis:
            if cifCheck and compId is not None:
                _seqKey = (chainId, seqId, compId)
                if _seqKey in self.__coordAtomSite:
                    return seqKey, self.__coordAtomSite[_seqKey]
                if cifCheck and seqKey in self.__coordAtomSite:
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
            return seqKey, self.__coordAtomSite[seqKey] if cifCheck and seqKey in self.__coordAtomSite else None
        if seqKey in self.__labelToAuthSeq:
            seqKey = self.__labelToAuthSeq[seqKey]
            if cifCheck and compId is not None:
                _seqKey = (seqKey[0], seqKey[1], compId)
                if _seqKey in self.__coordAtomSite:
                    return seqKey, self.__coordAtomSite[_seqKey]
            return seqKey, self.__coordAtomSite[seqKey] if cifCheck and seqKey in self.__coordAtomSite else None
        return seqKey, None

    def getAtomIdList(self, factor: dict, compId: str, atomId: str) -> List[str]:
        key = (compId, atomId, 'alt_atom_id' in factor)
        if key in self.__cachedDictForAtomIdList:
            return copy.copy(self.__cachedDictForAtomIdList[key])
        atomIds, _, details = self.__nefT.get_valid_star_atom_in_xplor(compId, atomId, leave_unmatched=True)
        if self.__cur_subtype not in ('dist', 'geo') and len(atomIds) > 1:
            if self.__cur_subtype == 'dihed' and len(atomIds) == 2 and self.__ccU.hasIntervenedAtom(compId, atomIds[0], atomIds[1]):
                return atomIds
            return [atomId]
        if details is not None and len(atomId) > 1 and not atomId[-1].isalpha()\
           and 'alt_atom_id' in factor and factor['alt_atom_id'][-1] not in ('%', '*', '#') and self.__cur_subtype == 'dist':
            atomIds, _, details = self.__nefT.get_valid_star_atom_in_xplor(compId, atomId[:-1], leave_unmatched=True)
            if atomId[-1].isdigit() and int(atomId[-1]) <= len(atomIds):
                atomIds = [atomIds[int(atomId[-1]) - 1]]

        if details is not None or atomId.endswith('"'):
            _atomId = toNefEx(translateToStdAtomName(atomId, compId, ccU=self.__ccU, unambig=False))
            if _atomId != atomId:
                atomIds = self.__nefT.get_valid_star_atom_in_xplor(compId, _atomId)[0]
        self.__cachedDictForAtomIdList[key] = atomIds
        return atomIds

    def getLabelSeqOffsetDueToUnobs(self, ps: dict) -> int:
        authChainId = ps['auth_chain_id']
        for labelSeqId, authSeqId in zip(ps['seq_id'], ps['auth_seq_id']):
            seqKey = (authChainId, authSeqId)
            if seqKey not in self.__coordUnobsRes:
                return labelSeqId - 1
        return max(list(filter(None, ps['seq_id']))) - 1

    def doesNonPolySeqIdMatchWithPolySeqUnobs(self, chainId: str, seqId: int) -> bool:
        _ps_ = next((_ps_ for _ps_ in self.__polySeq if _ps_['auth_chain_id'] == chainId), None)
        if _ps_ is not None:
            _chainId_ = _ps_['chain_id']
            _seqKey_ = (_chainId_, seqId)
            if _seqKey_ in self.__labelToAuthSeq:
                if self.__labelToAuthSeq[_seqKey_] != _seqKey_:
                    if self.__labelToAuthSeq[_seqKey_] in self.__coordUnobsRes:
                        return True
                else:
                    seq_id_list = list(filter(None, _ps_['seq_id']))
                    max_label_seq_id = max(seq_id_list)
                    _seqId_ = seqId + 1
                    while _seqId_ <= max_label_seq_id:
                        if _seqId_ in _ps_['seq_id']:
                            _seqKey_ = (_chainId_, _seqId_)
                            if _seqKey_ in self.__labelToAuthSeq and self.__labelToAuthSeq[_seqKey_] != _seqKey_:
                                break
                        _seqId_ += 1
                    if _seqId_ not in _ps_['seq_id']:
                        min_label_seq_id = min(seq_id_list)
                        _seqId_ = seqId - 1
                        while _seqId_ >= min_label_seq_id:
                            if _seqId_ in _ps_['seq_id']:
                                _seqKey_ = (_chainId_, _seqId_)
                                if _seqKey_ in self.__labelToAuthSeq and self.__labelToAuthSeq[_seqKey_] != _seqKey_:
                                    break
                            _seqId_ -= 1
                    if _seqId_ in _ps_['seq_id']:
                        _seqKey_ = (_chainId_, _seqId_)
                        if _seqKey_ in self.__labelToAuthSeq and self.__labelToAuthSeq[_seqKey_] != _seqKey_:
                            __chainId__, __seqId__ = self.__labelToAuthSeq[_seqKey_]
                            __seqKey__ = (__chainId__, __seqId__ - (_seqId_ - seqId))
                            if __seqKey__ in self.__coordUnobsRes:
                                return True
        return False

    def checkDistSequenceOffset(self, chainId: str, seqId: int, compId: str, origAtomId: str) -> bool:
        """ Try to find sequence offset.
        """

        if not self.__hasPolySeq or self.__cur_subtype != 'dist':
            return False

        ps = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == chainId), None)

        if ps is None:
            return False

        compIds = ps['comp_id']
        candidates = []

        for _compId in set(compIds):
            if compId == _compId:
                continue
            _atomId, _, details = self.__nefT.get_valid_star_atom_in_xplor(_compId, origAtomId)
            if len(_atomId) > 0 and details is None:
                candidates.append(_compId)

        if len(candidates) != 1:
            return False

        compId = candidates[0]

        idx_list = [idx for idx, _compId in enumerate(compIds) if _compId == compId]

        offsets = set(ps['auth_seq_id'][idx] - seqId for idx in idx_list)

        if 'global_sequence_offset' not in self.reasonsForReParsing:
            self.reasonsForReParsing['global_sequence_offset'] = {}
        if chainId in self.reasonsForReParsing['global_sequence_offset']:
            if self.reasonsForReParsing['global_sequence_offset'][chainId] is None:
                return False
            self.reasonsForReParsing['global_sequence_offset'][chainId] &= offsets
            if len(self.reasonsForReParsing['global_sequence_offset'][chainId]) == 0:
                self.reasonsForReParsing['global_sequence_offset'][chainId] = None
                return False
            return True

        self.reasonsForReParsing['global_sequence_offset'][chainId] = offsets

        return True

    def intersectionFactor_expressions(self, atomSelection: Optional[List[dict]] = None):
        self.consumeFactor_expressions(cifCheck=False)

        self.factor = self.__intersectionFactor_expressions(self.factor, atomSelection)

    def __intersectionFactor_expressions(self, _factor: dict, atomSelection: Optional[List[dict]] = None) -> dict:  # pylint: disable=no-self-use
        if 'atom_selection' not in _factor:
            _factor['atom_selection'] = atomSelection
            return _factor

        if atomSelection is None or len(atomSelection) == 0:
            _factor['atom_selection'] = []

        elif isinstance(atomSelection[0], str) and atomSelection[0] == '*':
            return _factor

        factor_has_is_poly = factor_has_auth_atom_id = atomsel_has_is_poly = atomsel_has_auth_atom_id = None
        if len(_factor['atom_selection']) > 0:
            factor_has_is_poly = 'is_poly' in _factor['atom_selection'][0]
            factor_has_auth_atom_id = 'auth_atom_id' in _factor['atom_selection'][0]
        if atomSelection is not None and len(atomSelection) > 0:
            atomsel_has_is_poly = 'is_poly' in atomSelection[0]
            atomsel_has_auth_atom_id = 'auth_atom_id' in atomSelection[0]

        refAtomSelection = _factor['atom_selection']
        if factor_has_is_poly != atomsel_has_is_poly or factor_has_auth_atom_id != atomsel_has_auth_atom_id:
            refAtomSelection = copy.deepcopy(_factor['atom_selection'])
            if factor_has_is_poly != atomsel_has_is_poly:
                if factor_has_is_poly:
                    for _atom in refAtomSelection:
                        try:
                            del _atom['is_poly']
                        except KeyError:
                            pass
                if atomsel_has_is_poly:
                    for _atom in atomSelection:
                        try:
                            del _atom['is_poly']
                        except KeyError:
                            pass
            if factor_has_auth_atom_id != atomsel_has_auth_atom_id:
                if factor_has_auth_atom_id:
                    for _atom in refAtomSelection:
                        try:
                            del _atom['auth_atom_id']
                        except KeyError:
                            pass
                if atomsel_has_auth_atom_id:
                    for _atom in atomSelection:
                        try:
                            del _atom['auth_atom_id']
                        except KeyError:
                            pass

        _atomSelection = []
        for _atom, _atom_ in zip(refAtomSelection, _factor['atom_selection']):
            if isinstance(_atom, str) and _atom == '*':
                _factor['atom_selection'] = atomSelection
                return _factor
            if _atom in atomSelection:
                _atomSelection.append(_atom_)
            elif 'hydrogen_not_instantiated' in _atom and _atom['hydrogen_not_instantiated']:
                chain_id = _atom['chain_id']
                seq_id = _atom['seq_id']
                if any(_atom2 for _atom2 in atomSelection if _atom2['chain_id'] == chain_id and _atom2['seq_id'] == seq_id):
                    _atomSelection.append(_atom_)

        _factor['atom_selection'] = _atomSelection

        return _factor

    def __intersectionAtom_selections(self, _selection1: List[dict], _selection2: List[dict]) -> List[dict]:  # pylint: disable=no-self-use
        if None in (_selection1, _selection2) or 0 in (len(_selection1), len(_selection2)):
            return []

        if isinstance(_selection2[0], str) and _selection2[0] == '*':
            return _selection1

        hasAuthSeqId1 = any(_atom for _atom in _selection1 if 'auth_atom_id' in _atom)
        hasAuthSeqId2 = any(_atom for _atom in _selection2 if 'auth_atom_id' in _atom)

        _atomSelection = []

        if not hasAuthSeqId1 and not hasAuthSeqId2:
            for _atom in _selection1:
                if isinstance(_atom, str) and _atom == '*':
                    return _selection2
                if _atom in _selection2:
                    _atomSelection.append(_atom)
                elif 'hydrogen_not_instantiated' in _atom and _atom['hydrogen_not_instantiated']:
                    chain_id = _atom['chain_id']
                    seq_id = _atom['seq_id']
                    if any(_atom2 for _atom2 in _selection2 if _atom2['chain_id'] == chain_id and _atom2['seq_id'] == seq_id):
                        _atomSelection.append(_atom)

        elif hasAuthSeqId1 and not hasAuthSeqId2:
            __selection1 = copy.deepcopy(_selection1)
            for _atom in __selection1:
                if 'auth_atom_id' in _atom:
                    _atom.pop('auth_atom_id')
            for idx, _atom in enumerate(__selection1):
                if isinstance(_atom, str) and _atom == '*':
                    return _selection2
                if _atom in _selection2:
                    _atomSelection.append(_selection1[idx])
                elif 'hydrogen_not_instantiated' in _atom and _atom['hydrogen_not_instantiated']:
                    chain_id = _atom['chain_id']
                    seq_id = _atom['seq_id']
                    if any(_atom2 for _atom2 in _selection2 if _atom2['chain_id'] == chain_id and _atom2['seq_id'] == seq_id):
                        _atomSelection.append(_selection1[idx])

        elif not hasAuthSeqId1 and hasAuthSeqId2:
            __selection2 = copy.deepcopy(_selection2)
            for idx, _atom in enumerate(__selection2):
                if 'auth_atom_id' in _atom:
                    _atom.pop('auth_atom_id')
            for idx, _atom in enumerate(__selection2):
                if isinstance(_atom, str) and _atom == '*':
                    return _selection1
                if _atom in _selection1:
                    _atomSelection.append(_selection2[idx])
                elif 'hydrogen_not_instantiated' in _atom and _atom['hydrogen_not_instantiated']:
                    chain_id = _atom['chain_id']
                    seq_id = _atom['seq_id']
                    if any(_atom1 for _atom1 in _selection1 if _atom1['chain_id'] == chain_id and _atom1['seq_id'] == seq_id):
                        _atomSelection.append(_selection2[idx])

        else:
            __selection1 = copy.deepcopy(_selection1)
            for _atom in __selection1:
                if 'auth_atom_id' in _atom:
                    _atom.pop('auth_atom_id')
            __selection2 = copy.deepcopy(_selection2)
            for _atom in __selection2:
                if 'auth_atom_id' in _atom:
                    _atom.pop('auth_atom_id')
            for idx, _atom in enumerate(__selection1):
                if isinstance(_atom, str) and _atom == '*':
                    return _selection2
                if _atom in __selection2:
                    _atomSelection.append(_selection1[idx])
                elif 'hydrogen_not_instantiated' in _atom and _atom['hydrogen_not_instantiated']:
                    chain_id = _atom['chain_id']
                    seq_id = _atom['seq_id']
                    if any(_atom2 for _atom2 in __selection2 if _atom2['chain_id'] == chain_id and _atom2['seq_id'] == seq_id):
                        _atomSelection.append(_selection1[idx])

        return _atomSelection

    # Enter a parse tree produced by CharmmMRParser#factor.
    def enterFactor(self, ctx: CharmmMRParser.FactorContext):
        if self.__sel_expr_debug:
            print("  " * self.depth + f"enter_factor, concatenation: {bool(ctx.factor())}")

        if ctx.Not_op():
            if len(self.factor) > 0:
                self.factor = self.__consumeFactor_expressions(self.factor, cifCheck=True)
                if 'atom_selection' in self.factor:
                    self.stackFactors.append(self.factor)
                self.factor = {}

        self.depth += 1

    # Exit a parse tree produced by CharmmMRParser#factor.
    def exitFactor(self, ctx: CharmmMRParser.FactorContext):
        self.depth -= 1
        if self.__sel_expr_debug:
            print("  " * self.depth + "exit_factor")

        try:

            # concatenation
            if ctx.factor() and self.stackSelections:
                if self.__con_union_expr and not self.__cur_union_expr and ctx.Not_op():
                    if len(self.stackFactors) > 0:
                        self.stackFactors.pop()
                        self.factor['atom_selection'] = self.stackSelections[-1]
                        self.stackSelections.append('and')  # intersection

                elif not self.__top_union_expr:
                    if len(self.stackFactors) > 0:
                        self.stackFactors.pop()
                        self.factor = {'atom_selection': self.stackSelections.pop()}

            if ctx.All() or ctx.Initial():
                clauseName = 'all' if ctx.All() else 'initial'
                if self.__sel_expr_debug:
                    print("  " * self.depth + f"--> {clauseName}")
                if not self.__hasCoord:
                    return
                try:

                    atomSelection =\
                        self.__cR.getDictListWithFilter('atom_site',
                                                        AUTH_ATOM_DATA_ITEMS,
                                                        [{'name': self.__modelNumName, 'type': 'int',
                                                          'value': self.__representativeModelId},
                                                         {'name': 'label_alt_id', 'type': 'enum',
                                                          'enum': (self.__representativeAltId,)}
                                                         ])

                    self.intersectionFactor_expressions(atomSelection)

                    if len(self.factor['atom_selection']) == 0:
                        self.factor['atom_id'] = [None]
                        self.__f.append(f"[Insufficient atom selection] {self.__getCurrentRestraint()}"
                                        f"The {clauseName!r} clause has no effect.")

                    else:
                        if 'chain_id' in self.factor:
                            del self.factor['chain_id']
                        if 'comp_id' in self.factor:
                            del self.factor['comp_id']
                        if 'seq_id' in self.factor:
                            del self.factor['seq_id']
                        if 'type_symbol' in self.factor:
                            del self.factor['type_symbol']
                        if 'atom_id' in self.factor:
                            del self.factor['atom_id']
                        if 'comp_ids' in self.factor:
                            del self.factor['comp_ids']
                        if 'seq_ids' in self.factor:
                            del self.factor['seq_ids']
                        if 'type_symbols' in self.factor:
                            del self.factor['type_symbols']
                        if 'atom_ids' in self.factor:
                            del self.factor['atom_ids']
                        if 'alt_chain_id' in self.factor:
                            del self.factor['alt_chain_id']
                        if 'alt_atom_id' in self.factor:
                            del self.factor['alt_atom_id']

                except Exception as e:
                    if self.__verbose:
                        self.__lfh.write(f"+{self.__class_name__}.exitFactor() ++ Error  - {str(e)}")

            elif ctx.Around():
                clauseName = 'around'
                if self.__sel_expr_debug:
                    print("  " * self.depth + f"--> {clauseName}")
                if not self.__hasCoord:
                    return
                if len(self.numberFSelection) == 0 or None in self.numberFSelection:
                    return
                around = self.numberFSelection[0]
                _atomSelection = []

                self.consumeFactor_expressions(f"atom selection expression before the {clauseName!r} clause")

                if 'atom_selection' in self.factor:

                    for _atom in self.factor['atom_selection']:

                        try:

                            _origin =\
                                self.__cR.getDictListWithFilter('atom_site',
                                                                CARTN_DATA_ITEMS,
                                                                [{'name': self.__authAsymId, 'type': 'str', 'value': _atom['chain_id']},
                                                                 {'name': self.__authSeqId, 'type': 'int', 'value': _atom['seq_id']},
                                                                 {'name': self.__authAtomId, 'type': 'str', 'value': _atom['atom_id']},
                                                                 {'name': self.__modelNumName, 'type': 'int',
                                                                  'value': self.__representativeModelId},
                                                                 {'name': 'label_alt_id', 'type': 'enum',
                                                                  'enum': (self.__representativeAltId,)}
                                                                 ])

                            if len(_origin) != 1:
                                continue

                            origin = to_np_array(_origin[0])

                            _neighbor =\
                                self.__cR.getDictListWithFilter('atom_site',
                                                                AUTH_ATOM_CARTN_DATA_ITEMS,
                                                                [{'name': 'Cartn_x', 'type': 'range-float',
                                                                  'range': {'min_exclusive': (origin[0] - around),
                                                                            'max_exclusive': (origin[0] + around)}},
                                                                 {'name': 'Cartn_y', 'type': 'range-float',
                                                                  'range': {'min_exclusive': (origin[1] - around),
                                                                            'max_exclusive': (origin[1] + around)}},
                                                                 {'name': 'Cartn_z', 'type': 'range-float',
                                                                  'range': {'min_exclusive': (origin[2] - around),
                                                                            'max_exclusive': (origin[2] + around)}},
                                                                 {'name': self.__modelNumName, 'type': 'int',
                                                                  'value': self.__representativeModelId},
                                                                 {'name': 'label_alt_id', 'type': 'enum',
                                                                  'enum': (self.__representativeAltId,)}
                                                                 ])

                            if len(_neighbor) == 0:
                                continue

                            neighbor = [atom for atom in _neighbor if distance(to_np_array(atom), origin) < around]

                            for atom in neighbor:
                                del atom['x']
                                del atom['y']
                                del atom['z']
                                _atomSelection.append(atom)

                        except Exception as e:
                            if self.__verbose:
                                self.__lfh.write(f"+{self.__class_name__}.exitFactor() ++ Error  - {str(e)}")

                    if len(self.factor['atom_selection']) > 0:
                        self.factor['atom_selection'] = [dict(s) for s in set(frozenset(atom.items())
                                                                              for atom in _atomSelection
                                                                              if isinstance(atom, dict))]

                        if len(self.factor['atom_selection']) == 0:
                            self.factor['atom_id'] = [None]
                            self.__f.append(f"[Insufficient atom selection] {self.__getCurrentRestraint()}"
                                            f"The {clauseName!r} clause has no effect.")

            elif ctx.Atom():
                if self.__sel_expr_debug:
                    print("  " * self.depth + "--> atom")
                if not self.__hasPolySeq and not self.__hasNonPolySeq:
                    return

                simpleNameIndex = simpleNamesIndex = 0  # these indices are necessary to deal with mixing case of 'Simple_name' and 'Simple_names'
                if ctx.Simple_name(0):
                    chainId = str(ctx.Simple_name(0))
                    self.factor['chain_id'] = [ps['auth_chain_id'] for ps in self.__polySeq
                                               if ps['auth_chain_id'] == self.getRealChainId(chainId)]
                    if self.__hasNonPolySeq:
                        for np in self.__nonPolySeq:
                            _chainId = np['auth_chain_id']
                            if _chainId == self.getRealChainId(chainId) and _chainId not in self.factor['chain_id']:
                                self.factor['chain_id'].append(_chainId)
                    if len(self.factor['chain_id']) > 0:
                        simpleNameIndex += 1

                if simpleNameIndex == 0 and ctx.Simple_names(0):
                    chainId = str(ctx.Simple_names(0))
                    if self.__reasons is not None and 'segment_id_mismatch' in self.__reasons and chainId in self.__reasons['segment_id_mismatch']\
                       and self.__reasons['segment_id_mismatch'][chainId] in self.__reasons['segment_id_match_stats'][chainId]:
                        _chainId = self.__reasons['segment_id_mismatch'][chainId]
                        _stats = self.__reasons['segment_id_match_stats'][chainId]
                        self.factor['chain_id'] = sorted([k for k, v in _stats.items() if v == _stats[_chainId]])
                        self.factor['alt_chain_id'] = chainId
                    else:
                        _chainId = toRegEx(chainId)
                        self.factor['chain_id'] = [ps['auth_chain_id'] for ps in self.__polySeq
                                                   if re.match(_chainId, ps['auth_chain_id'])]
                        if self.__hasNonPolySeq:
                            for np in self.__nonPolySeq:
                                __chainId = np['auth_chain_id']
                                if re.match(_chainId, __chainId) and __chainId not in self.factor['chain_id']:
                                    self.factor['chain_id'].append(__chainId)
                    simpleNamesIndex += 1

                if len(self.factor['chain_id']) == 0:
                    if len(self.__polySeq) == 1 and not self.__hasBranched and not self.__hasNonPoly:
                        self.factor['chain_id'] = self.__polySeq[0]['chain_id']
                        self.factor['auth_chain_id'] = chainId
                    elif self.__reasons is not None:
                        self.factor['atom_id'] = [None]
                        if 'segment_id_mismatch' in self.__reasons\
                           and (chainId not in self.__reasons['segment_id_mismatch']
                                or self.__reasons['segment_id_mismatch'][chainId] is not None):
                            self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                            "Couldn't specify segment name "
                                            f"'{chainId}' the coordinates.")  # do not use 'chainId!r' expression, '%' code throws ValueError
                    else:
                        if 'segment_id_mismatch' not in self.reasonsForReParsing:
                            self.reasonsForReParsing['segment_id_mismatch'] = {}
                            self.reasonsForReParsing['segment_id_match_stats'] = {}
                            self.reasonsForReParsing['segment_id_poly_type_stats'] = {}
                        if chainId not in self.reasonsForReParsing['segment_id_mismatch']:
                            self.reasonsForReParsing['segment_id_mismatch'][chainId] = None
                            self.reasonsForReParsing['segment_id_match_stats'][chainId] = {}
                            self.reasonsForReParsing['segment_id_poly_type_stats'][chainId] = {'polymer': 0, 'non-poly': 0}
                        self.factor['alt_chain_id'] = chainId

                if ctx.Integer(0):
                    self.factor['seq_id'] = [int(str(ctx.Integer(0)))]

                if ctx.Integers():
                    seqId = str(ctx.Integers())
                    _seqId = toRegEx(seqId)
                    _seqIdSelect = set()
                    for chainId in self.factor['chain_id']:
                        ps = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == chainId), None)
                        if ps is not None:
                            found = False
                            for realSeqId in ps['auth_seq_id']:
                                if realSeqId is None:
                                    continue
                                realSeqId = self.getRealSeqId(ps, realSeqId)[0]
                                if re.match(_seqId, str(realSeqId)):
                                    _seqIdSelect.add(realSeqId)
                                    found = True
                            if not found:
                                for realSeqId in ps['auth_seq_id']:
                                    if realSeqId is None:
                                        continue
                                    realSeqId = self.getRealSeqId(ps, realSeqId)[0]
                                    seqKey = (chainId, realSeqId)
                                    if seqKey in self.__authToLabelSeq:
                                        _, realSeqId = self.__authToLabelSeq[seqKey]
                                        if re.match(_seqId, str(realSeqId)):
                                            _seqIdSelect.add(realSeqId)
                    if self.__hasNonPolySeq:
                        for chainId in self.factor['chain_id']:
                            npList = [np for np in self.__nonPolySeq if np['auth_chain_id'] == chainId]
                            for np in npList:
                                found = False
                                for realSeqId in np['auth_seq_id']:
                                    if realSeqId is None:
                                        continue
                                    realSeqId = self.getRealSeqId(np, realSeqId, False)[0]
                                    if re.match(_seqId, str(realSeqId)):
                                        _seqIdSelect.add(realSeqId)
                                        found = True
                                if not found:
                                    for realSeqId in np['auth_seq_id']:
                                        if realSeqId is None:
                                            continue
                                        realSeqId = self.getRealSeqId(np, realSeqId, False)[0]
                                        seqKey = (chainId, realSeqId)
                                        if seqKey in self.__authToLabelSeq:
                                            _, realSeqId = self.__authToLabelSeq[seqKey]
                                            if re.match(_seqId, str(realSeqId)):
                                                _seqIdSelect.add(realSeqId)
                    self.factor['seq_id'] = list(_seqIdSelect)

                _atomIdSelect = set()
                if ctx.Simple_name(simpleNameIndex):
                    atomId = str(ctx.Simple_name(simpleNameIndex))
                    for chainId in self.factor['chain_id']:
                        ps = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == chainId), None)
                        if ps is None:
                            continue
                        for seqId in self.factor['seq_id']:
                            if seqId in ps['auth_seq_id']:
                                seqId, compId, _ = self.getRealSeqId(ps, seqId)
                                # compId = ps['comp_id'][ps['auth_seq_id'].index(seqId)]
                                if self.__ccU.updateChemCompDict(compId):
                                    if any(cca for cca in self.__ccU.lastAtomList if cca[self.__ccU.ccaAtomId] == atomId):
                                        _atomIdSelect.add(atomId)
                    if self.__hasNonPolySeq:
                        for chainId in self.factor['chain_id']:
                            npList = [np for np in self.__nonPolySeq if np['auth_chain_id'] == chainId]
                            for np in npList:
                                for seqId in self.factor['seq_id']:
                                    if seqId in np['auth_seq_id']:
                                        seqId, compId, _ = self.getRealSeqId(np, seqId, False)
                                        # compId = np['comp_id'][np['auth_seq_id'].index(seqId)]
                                        if self.__ccU.updateChemCompDict(compId):
                                            if any(cca for cca in self.__ccU.lastAtomList if cca[self.__ccU.ccaAtomId] == atomId):
                                                _atomIdSelect.add(atomId)

                elif ctx.Simple_names(simpleNamesIndex):
                    atomId = translateToStdAtomName(str(ctx.Simple_names(simpleNamesIndex)),
                                                    None if 'comp_id' not in self.factor else self.factor['comp_id'][0],
                                                    ccU=self.__ccU)
                    _atomId = toRegEx(atomId)
                    for chainId in self.factor['chain_id']:
                        ps = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == chainId), None)
                        if ps is None:
                            continue
                        for seqId in self.factor['seq_id']:
                            if seqId in ps['auth_seq_id']:
                                seqId, compId, _ = self.getRealSeqId(ps, seqId)
                                # compId = ps['comp_id'][ps['auth_seq_id'].index(seqId)]
                                if self.__ccU.updateChemCompDict(compId):
                                    for cca in self.__ccU.lastAtomList:
                                        if cca[self.__ccU.ccaLeavingAtomFlag] != 'Y':
                                            realAtomId = cca[self.__ccU.ccaAtomId]
                                            if re.match(_atomId, realAtomId):
                                                _atomIdSelect.add(realAtomId)
                    if self.__hasNonPolySeq:
                        for chainId in self.factor['chain_id']:
                            npList = [np for np in self.__nonPolySeq if np['auth_chain_id'] == chainId]
                            for np in npList:
                                for seqId in self.factor['seq_id']:
                                    if seqId in np['auth_seq_id']:
                                        seqId, compId, _ = self.getRealSeqId(np, seqId, False)
                                        # compId = np['comp_id'][np['auth_seq_id'].index(seqId)]
                                        if self.__ccU.updateChemCompDict(compId):
                                            for cca in self.__ccU.lastAtomList:
                                                if cca[self.__ccU.ccaLeavingAtomFlag] != 'Y':
                                                    realAtomId = cca[self.__ccU.ccaAtomId]
                                                    if re.match(_atomId, realAtomId):
                                                        _atomIdSelect.add(realAtomId)

                self.factor['atom_id'] = list(_atomIdSelect)

                self.consumeFactor_expressions("'atom' clause", False)

            elif ctx.Property():
                if self.__sel_expr_debug:
                    print("  " * self.depth + "--> property")
                if not self.__hasCoord:
                    return
                absolute = bool(ctx.Abs())
                _attr_prop = str(ctx.Attr_properties())
                attr_prop = _attr_prop.lower()
                opCode = str(ctx.Comparison_ops()).lower()
                if len(self.numberFSelection) == 0 or None in self.numberFSelection:
                    return
                attr_value = self.numberFSelection[0]

                validProp = True

                if attr_prop.startswith('xcom')\
                        or attr_prop.startswith('ycom')\
                        or attr_prop.startswith('zcom')\
                        or attr_prop.startswith('wcom')\
                        or attr_prop.startswith('wmai'):  # XCOMP, YCOMP, ZCOMP, WCOMP, WMAI
                    self.factor['atom_id'] = [None]
                    self.__f.append(f"[Unsupported data] {self.__getCurrentRestraint()}"
                                    f"The attribute property {_attr_prop!r} "
                                    "requires a comparison coordinate set.")
                    validProp = False

                elif attr_prop.startswith('char'):  # CAHRGE
                    valueType = {'name': 'pdbx_formal_charge'}
                    if opCode in ('.eq.', '.ae.'):
                        valueType['type'] = 'int' if not absolute else 'abs-int'
                        valueType['value'] = attr_value
                    elif opCode == '.lt.':
                        valueType['type'] = 'range-int' if not absolute else 'range-abs-int'
                        valueType['range'] = {'max_exclusive': attr_value}
                    elif opCode == '.gt.':
                        valueType['type'] = 'range-int' if not absolute else 'range-abs-int'
                        valueType['range'] = {'min_exclusive': attr_value}
                    elif opCode == '.le.':
                        valueType['type'] = 'range-int' if not absolute else 'range-abs-int'
                        valueType['range'] = {'max_inclusive': attr_value}
                    elif opCode == '.gt.':
                        valueType['type'] = 'range-int' if not absolute else 'range-abs-int'
                        valueType['range'] = {'min_inclusive': attr_value}
                    elif opCode == '.ne.':
                        valueType['type'] = 'range-int' if not absolute else 'range-abs-int'
                        valueType['range'] = {'not_equal_to': attr_value}
                    atomSelection =\
                        self.__cR.getDictListWithFilter('atom_site',
                                                        AUTH_ATOM_DATA_ITEMS,
                                                        [valueType,
                                                         {'name': self.__modelNumName, 'type': 'int',
                                                          'value': self.__representativeModelId},
                                                         {'name': 'label_alt_id', 'type': 'enum',
                                                          'enum': (self.__representativeAltId,)}
                                                         ])

                    self.intersectionFactor_expressions(atomSelection)

                elif attr_prop in ('dx', 'dy', 'dz'):
                    self.factor['atom_id'] = [None]
                    self.__f.append(f"[Unsupported data] {self.__getCurrentRestraint()}"
                                    f"The attribute property {_attr_prop!r} "
                                    "related to atomic force of each atom is not possessed in the static coordinate file.")
                    validProp = False

                elif attr_prop.startswith('fbet'):  # FBETA
                    self.factor['atom_id'] = [None]
                    self.__f.append(f"[Unsupported data] {self.__getCurrentRestraint()}"
                                    f"The attribute property {_attr_prop!r} "
                                    "related to the Langevin dynamics (nonzero friction coefficient) is not possessed in the static coordinate file.")
                    validProp = False

                elif attr_prop == 'mass':
                    _typeSymbolSelect = set()
                    atomTypes = self.__cR.getDictList('atom_type')
                    if len(atomTypes) > 0 and 'symbol' in atomTypes[0]:
                        for atomType in atomTypes:
                            typeSymbol = atomType['symbol']
                            atomicNumber = int_atom(typeSymbol)
                            atomicWeight = ELEMENT_WEIGHTS[atomicNumber]

                            if (opCode == '.eq.' and atomicWeight == attr_value)\
                               or (opCode == '.lt.' and atomicWeight < attr_value)\
                               or (opCode == '.gt.' and atomicWeight > attr_value)\
                               or (opCode == '.le.' and atomicWeight <= attr_value)\
                               or (opCode == '.ge.' and atomicWeight >= attr_value)\
                               or (opCode == '.ne.' and atomicWeight != attr_value)\
                               or (opCode == '.ae.' and abs(atomicWeight - attr_value) < 0.001):
                                _typeSymbolSelect.add(typeSymbol)

                    atomSelection =\
                        self.__cR.getDictListWithFilter('atom_site',
                                                        AUTH_ATOM_DATA_ITEMS,
                                                        [{'name': 'type_symbol', 'type': 'enum',
                                                          'enum': _typeSymbolSelect},
                                                         {'name': self.__modelNumName, 'type': 'int',
                                                          'value': self.__representativeModelId},
                                                         {'name': 'label_alt_id', 'type': 'enum',
                                                          'enum': (self.__representativeAltId,)}
                                                         ])

                    self.intersectionFactor_expressions(atomSelection)

                elif attr_prop in ('xref', 'yref', 'zref'):
                    self.factor['atom_id'] = [None]
                    self.__f.append(f"[Unsupported data] {self.__getCurrentRestraint()}"
                                    f"The attribute property {_attr_prop!r} "
                                    "requires a reference coordinate set.")
                    validProp = False

                elif attr_prop in ('vx', 'vy', 'vz'):
                    self.factor['atom_id'] = [None]
                    self.__f.append(f"[Unsupported data] {self.__getCurrentRestraint()}"
                                    f"The attribute property {_attr_prop!r} "
                                    "related to current velocities of each atom is not possessed in the static coordinate file.")
                    validProp = False

                elif attr_prop in ('x', 'y', 'z'):
                    valueType = {'name': f"Cartn_{attr_prop}"}
                    if opCode == '.eq.':
                        valueType['type'] = 'float' if not absolute else 'abs-float'
                        valueType['value'] = attr_value
                    elif opCode == '.lt.':
                        valueType['type'] = 'range-float' if not absolute else 'range-abs-float'
                        valueType['range'] = {'max_exclusive': attr_value}
                    elif opCode == '.gt.':
                        valueType['type'] = 'range-float' if not absolute else 'range-abs-float'
                        valueType['range'] = {'min_exclusive': attr_value}
                    elif opCode == '.le.':
                        valueType['type'] = 'range-float' if not absolute else 'range-abs-float'
                        valueType['range'] = {'max_inclusive': attr_value}
                    elif opCode == '.ge.':
                        valueType['type'] = 'range-float' if not absolute else 'range-abs-float'
                        valueType['range'] = {'min_inclusive': attr_value}
                    elif opCode == '.ne.':
                        valueType['type'] = 'range-float' if not absolute else 'range-abs-float'
                        valueType['range'] = {'not_equal_to': attr_value}
                    elif opCode == '.ae.':
                        valueType['type'] = 'range-float' if not absolute else 'range-abs-float'
                        valueType['range'] = {'min_inclusive': attr_value - 0.001, 'max_inclusive': attr_value + 0.001}
                    atomSelection =\
                        self.__cR.getDictListWithFilter('atom_site',
                                                        AUTH_ATOM_DATA_ITEMS,
                                                        [valueType,
                                                         {'name': self.__modelNumName, 'type': 'int',
                                                          'value': self.__representativeModelId},
                                                         {'name': 'label_alt_id', 'type': 'enum',
                                                          'enum': (self.__representativeAltId,)}
                                                         ])

                    self.intersectionFactor_expressions(atomSelection)

                elif attr_prop.startswith('sca') or attr_prop in ('zero', 'one'):
                    self.factor['atom_id'] = [None]
                    self.__f.append(f"[Unsupported data] {self.__getCurrentRestraint()}"
                                    f"The '{_attr_prop}' clause has no effect "
                                    "because the internal vector statement is not set.")
                    validProp = False

                elif attr_prop.startswith('econ') or attr_prop.startswith('epco') or attr_prop.startswith('cons')\
                        or attr_prop.startswith('igno') or attr_prop.startswith('aspv') or attr_prop.startswith('vdws')\
                        or attr_prop.startswith('alph') or attr_prop.startswith('effe') or attr_prop.startswith('radi')\
                        or attr_prop.startswith('rsca') or attr_prop.startswith('fdco')\
                        or attr_prop in ('move', 'type', 'fdim', 'fdep'):
                    self.factor['atom_id'] = [None]
                    self.__f.append(f"[Unsupported data] {self.__getCurrentRestraint()}"
                                    f"The attribute property {_attr_prop!r} "
                                    "related to software specific parameters of each atom is not possessed in the static coordinate file.")
                    validProp = False

                if validProp and len(self.factor['atom_selection']) == 0:
                    self.factor['atom_id'] = [None]
                    _absolute = ' abs' if absolute else ''
                    self.__f.append(f"[Insufficient atom selection] {self.__getCurrentRestraint()}"
                                    f"The 'attribute' clause ('{_attr_prop}{_absolute} {opCode} {attr_value}') has no effect.")

            elif ctx.Bonded():
                if self.__sel_expr_debug:
                    print("  " * self.depth + "--> bonded")
                if not self.__hasCoord:
                    return
                if 'atom_selection' in self.factor and len(self.factor['atom_selection']) > 0:
                    _atomSelection = []

                    for _atom in self.factor['atom_selection']:
                        chainId = _atom['chain_id']
                        compId = _atom['comp_id']
                        seqId = _atom['seq_id']
                        atomId = _atom['atom_id']

                        _, coordAtomSite = self.getCoordAtomSiteOf(chainId, seqId)

                        # intra
                        if self.__ccU.updateChemCompDict(compId):
                            leavingAtomIds = [cca[self.__ccU.ccaAtomId] for cca in self.__ccU.lastAtomList if cca[self.__ccU.ccaLeavingAtomFlag] == 'Y']

                            _atomIdSelect = set()
                            for ccb in self.__ccU.lastBonds:
                                if ccb[self.__ccU.ccbAtomId1] == atomId:
                                    _atomIdSelect.add(ccb[self.__ccU.ccbAtomId2])
                                elif ccb[self.__ccU.ccbAtomId2] == atomId:
                                    _atomIdSelect.add(ccb[self.__ccU.ccbAtomId1])

                            hasLeaavindAtomId = False

                            for _atomId in _atomIdSelect:

                                if _atomId in leavingAtomIds:
                                    hasLeaavindAtomId = True
                                    continue

                                _atom = None
                                if coordAtomSite is not None:
                                    if _atomId in coordAtomSite['atom_id']:
                                        _atom = {}
                                        _atom['comp_id'] = coordAtomSite['comp_id']
                                    elif _atomId in ('HN1', 'HN2', 'HN3') and ((_atomId[-1] + 'HN') in coordAtomSite['atom_id']
                                                                               or ('H' + _atomId[-1] in coordAtomSite['atom_id'])):
                                        _atom = {}
                                        _atom['comp_id'] = coordAtomSite['comp_id']
                                    elif 'alt_atom_id' in coordAtomSite and _atomId in coordAtomSite['alt_atom_id']:
                                        _atom = {}
                                        _atom['comp_id'] = coordAtomSite['comp_id']

                                if _atom is not None and _atom['comp_id'] == compId:
                                    _atomSelection.append({'chain_id': chainId, 'seq_id': seqId, 'comp_id': compId, 'atom_id': _atomId})

                                else:
                                    ps = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == chainId), None)
                                    if ps is not None and seqId in ps['auth_seq_id'] and ps['comp_id'][ps['auth_seq_id'].index(seqId)] == compId:
                                        seqId = self.getRealSeqId(ps, seqId)[0]
                                        if any(cca for cca in self.__ccU.lastAtomList if cca[self.__ccU.ccaAtomId] == _atomId):
                                            _atomSelection.append({'chain_id': chainId, 'seq_id': seqId, 'comp_id': compId, 'atom_id': _atomId})
                                    if self.__hasNonPolySeq:
                                        npList = [np for np in self.__nonPolySeq if np['auth_chain_id'] == chainId]
                                        for np in npList:
                                            if seqId in np['auth_seq_id'] and np['comp_id'][np['auth_seq_id'].index(seqId)] == compId:
                                                seqId = self.getRealSeqId(np, seqId, False)[0]
                                                if any(cca for cca in self.__ccU.lastAtomList if cca[self.__ccU.ccaAtomId] == _atomId):
                                                    _atomSelection.append({'chain_id': chainId, 'seq_id': seqId, 'comp_id': compId, 'atom_id': _atomId})

                            # sequential
                            if hasLeaavindAtomId:
                                _origin =\
                                    self.__cR.getDictListWithFilter('atom_site',
                                                                    CARTN_DATA_ITEMS,
                                                                    [{'name': self.__authAsymId, 'type': 'str', 'value': chainId},
                                                                     {'name': self.__authSeqId, 'type': 'int', 'value': seqId},
                                                                     {'name': self.__authAtomId, 'type': 'str', 'value': atomId},
                                                                     {'name': self.__modelNumName, 'type': 'int',
                                                                      'value': self.__representativeModelId},
                                                                     {'name': 'label_alt_id', 'type': 'enum',
                                                                      'enum': (self.__representativeAltId,)}
                                                                     ])

                                if len(_origin) == 1:
                                    origin = to_np_array(_origin[0])

                                    ps = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == chainId), None)
                                    if ps is not None:
                                        for _seqId in [seqId - 1, seqId + 1]:
                                            if _seqId in ps['auth_seq_id']:
                                                _seqId, _compId, _ = self.getRealSeqId(ps, _seqId)
                                                # _compId = ps['comp_id'][ps['auth_seq_id'].index(_seqId)]
                                                if self.__ccU.updateChemCompDict(_compId):
                                                    leavingAtomIds = [cca[self.__ccU.ccaAtomId] for cca in self.__ccU.lastAtomList if cca[self.__ccU.ccaLeavingAtomFlag] == 'Y']

                                                    _atomIdSelect = set()
                                                    for ccb in self.__ccU.lastBonds:
                                                        if ccb[self.__ccU.ccbAtomId1] in leavingAtomIds:
                                                            _atomId = ccb[self.__ccU.ccbAtomId2]
                                                            if _atomId not in leavingAtomIds:
                                                                _atomIdSelect.add(_atomId)
                                                        if ccb[self.__ccU.ccbAtomId2] in leavingAtomIds:
                                                            _atomId = ccb[self.__ccU.ccbAtomId1]
                                                            if _atomId not in leavingAtomIds:
                                                                _atomIdSelect.add(_atomId)

                                                    for _atomId in _atomIdSelect:
                                                        _neighbor =\
                                                            self.__cR.getDictListWithFilter('atom_site',
                                                                                            CARTN_DATA_ITEMS,
                                                                                            [{'name': self.__authAsymId, 'type': 'str', 'value': chainId},
                                                                                             {'name': self.__authSeqId, 'type': 'int', 'value': _seqId},
                                                                                             {'name': self.__authAtomId, 'type': 'str', 'value': _atomId},
                                                                                             {'name': self.__modelNumName, 'type': 'int',
                                                                                              'value': self.__representativeModelId},
                                                                                             {'name': 'label_alt_id', 'type': 'enum',
                                                                                              'enum': (self.__representativeAltId,)}
                                                                                             ])

                                                        if len(_neighbor) != 1:
                                                            continue

                                                        if distance(to_np_array(_neighbor[0]), origin) < 2.5:
                                                            _atomSelection.append({'chain_id': chainId, 'seq_id': _seqId, 'comp_id': _compId, 'atom_id': _atomId})

                                    if self.__hasNonPolySeq:
                                        npList = [np for np in self.__nonPolySeq if np['auth_chain_id'] == chainId]
                                        for np in npList:
                                            for _seqId in [seqId - 1, seqId + 1]:
                                                if _seqId in np['auth_seq_id']:
                                                    _seqId, _compId, _ = self.getRealSeqId(np, _seqId, False)
                                                    # _compId = np['comp_id'][np['auth_seq_id'].index(_seqId)]
                                                    if self.__ccU.updateChemCompDict(_compId):
                                                        leavingAtomIds = [cca[self.__ccU.ccaAtomId] for cca in self.__ccU.lastAtomList if cca[self.__ccU.ccaLeavingAtomFlag] == 'Y']

                                                        _atomIdSelect = set()
                                                        for ccb in self.__ccU.lastBonds:
                                                            if ccb[self.__ccU.ccbAtomId1] in leavingAtomIds:
                                                                _atomId = ccb[self.__ccU.ccbAtomId2]
                                                                if _atomId not in leavingAtomIds:
                                                                    _atomIdSelect.add(_atomId)
                                                            if ccb[self.__ccU.ccbAtomId2] in leavingAtomIds:
                                                                _atomId = ccb[self.__ccU.ccbAtomId1]
                                                                if _atomId not in leavingAtomIds:
                                                                    _atomIdSelect.add(_atomId)

                                                        for _atomId in _atomIdSelect:
                                                            _neighbor =\
                                                                self.__cR.getDictListWithFilter('atom_site',
                                                                                                CARTN_DATA_ITEMS,
                                                                                                [{'name': self.__authAsymId, 'type': 'str', 'value': chainId},
                                                                                                 {'name': self.__authSeqId, 'type': 'int', 'value': _seqId},
                                                                                                 {'name': self.__authAtomId, 'type': 'str', 'value': _atomId},
                                                                                                 {'name': self.__modelNumName, 'type': 'int',
                                                                                                  'value': self.__representativeModelId},
                                                                                                 {'name': 'label_alt_id', 'type': 'enum',
                                                                                                  'enum': (self.__representativeAltId,)}
                                                                                                 ])

                                                            if len(_neighbor) != 1:
                                                                continue

                                                            if distance(to_np_array(_neighbor[0]), origin) < 2.5:
                                                                _atomSelection.append({'chain_id': chainId, 'seq_id': _seqId, 'comp_id': _compId, 'atom_id': _atomId})

                        # struct_conn category
                        _atom = self.__cR.getDictListWithFilter('struct_conn',
                                                                PTNR1_AUTH_ATOM_DATA_ITEMS,
                                                                [{'name': 'ptnr2_auth_asym_id', 'type': 'str', 'value': chainId},
                                                                 {'name': 'ptnr2_auth_seq_id', 'type': 'int', 'value': seqId},
                                                                 {'name': 'ptnr2_label_atom_id', 'type': 'str', 'value': atomId},
                                                                 {'name': self.__modelNumName, 'type': 'int',
                                                                  'value': self.__representativeModelId}
                                                                 ])

                        if len(_atom) == 1:
                            _atomSelection.append(_atom[0])

                        _atom = self.__cR.getDictListWithFilter('struct_conn',
                                                                PTNR2_AUTH_ATOM_DATA_ITEMS,
                                                                [{'name': 'ptnr1_auth_asym_id', 'type': 'str', 'value': chainId},
                                                                 {'name': 'ptnr1_auth_seq_id', 'type': 'int', 'value': seqId},
                                                                 {'name': 'ptnr1_label_atom_id', 'type': 'str', 'value': atomId},
                                                                 {'name': self.__modelNumName, 'type': 'int',
                                                                  'value': self.__representativeModelId}
                                                                 ])

                        if len(_atom) == 1:
                            _atomSelection.append(_atom[0])

                    self.factor['atom_selection'] = [dict(s) for s in set(frozenset(atom.items())
                                                                          for atom in _atomSelection
                                                                          if isinstance(atom, dict))]

                    if len(self.factor['atom_selection']) == 0:
                        self.factor['atom_id'] = [None]
                        self.__f.append(f"[Insufficient atom selection] {self.__getCurrentRestraint()}"
                                        "The 'bondedto' clause has no effect.")

                else:
                    self.factor['atom_id'] = [None]
                    self.__f.append(f"[Insufficient atom selection] {self.__getCurrentRestraint()}"
                                    "The 'bondedto' clause has no effect because no atom is selected.")

            elif ctx.ByGroup():
                if self.__sel_expr_debug:
                    print("  " * self.depth + "--> bygroup")
                if not self.__hasCoord:
                    return
                if 'atom_selection' in self.factor and len(self.factor['atom_selection']) > 0:
                    _atomSelection = []

                    for _atom in self.factor['atom_selection']:
                        chainId = _atom['chain_id']
                        compId = _atom['comp_id']
                        seqId = _atom['seq_id']
                        atomId = _atom['atom_id']

                        _atomSelection.append(_atom)  # self atom

                        if self.__ccU.updateChemCompDict(compId):
                            _bondedAtomIdSelect = set()
                            for ccb in self.__ccU.lastBonds:
                                if ccb[self.__ccU.ccbAtomId1] == atomId:
                                    _bondedAtomIdSelect.add(ccb[self.__ccU.ccbAtomId2])
                                elif ccb[self.__ccU.ccbAtomId2] == atomId:
                                    _bondedAtomIdSelect.add(ccb[self.__ccU.ccbAtomId1])

                            _nonBondedAtomIdSelect = set()
                            for _atomId in _bondedAtomIdSelect:
                                for ccb in self.__ccU.lastBonds:
                                    if ccb[self.__ccU.ccbAtomId1] == _atomId:
                                        _nonBondedAtomIdSelect.add(ccb[self.__ccU.ccbAtomId2])
                                    elif ccb[self.__ccU.ccbAtomId2] == _atomId:
                                        _nonBondedAtomIdSelect.add(ccb[self.__ccU.ccbAtomId1])

                            if atomId in _nonBondedAtomIdSelect:
                                _nonBondedAtomIdSelect.remove(atomId)

                            for _atomId in _bondedAtomIdSelect:
                                if _atomId in _nonBondedAtomIdSelect:
                                    _nonBondedAtomIdSelect.remove(_atomId)

                            if len(_nonBondedAtomIdSelect) > 0:
                                _origin =\
                                    self.__cR.getDictListWithFilter('atom_site',
                                                                    CARTN_DATA_ITEMS,
                                                                    [{'name': self.__authAsymId, 'type': 'str', 'value': chainId},
                                                                     {'name': self.__authSeqId, 'type': 'int', 'value': seqId},
                                                                     {'name': self.__authAtomId, 'type': 'str', 'value': atomId},
                                                                     {'name': self.__modelNumName, 'type': 'int',
                                                                      'value': self.__representativeModelId},
                                                                     {'name': 'label_alt_id', 'type': 'enum',
                                                                      'enum': (self.__representativeAltId,)}
                                                                     ])

                                if len(_origin) == 1:
                                    origin = to_np_array(_origin[0])

                                    for _atomId in _nonBondedAtomIdSelect:
                                        _neighbor =\
                                            self.__cR.getDictListWithFilter('atom_site',
                                                                            CARTN_DATA_ITEMS,
                                                                            [{'name': self.__authAsymId, 'type': 'str', 'value': chainId},
                                                                             {'name': self.__authSeqId, 'type': 'int', 'value': seqId},
                                                                             {'name': self.__authAtomId, 'type': 'str', 'value': _atomId},
                                                                             {'name': self.__modelNumName, 'type': 'int',
                                                                              'value': self.__representativeModelId},
                                                                             {'name': 'label_alt_id', 'type': 'enum',
                                                                              'enum': (self.__representativeAltId,)}
                                                                             ])

                                        if len(_neighbor) != 1:
                                            continue

                                        if distance(to_np_array(_neighbor[0]), origin) < 2.0:
                                            _atomSelection.append({'chain_id': chainId, 'seq_id': seqId, 'comp_id': compId, 'atom_id': _atomId})

                                else:
                                    cca = next((cca for cca in self.__ccU.lastAtomList if cca[self.__ccU.ccaAtomId] == atomId), None)
                                    if cca is not None:
                                        _origin = {'x': float(cca[self.__ccU.ccaCartnX]), 'y': float(cca[self.__ccU.ccaCartnY]), 'z': float(cca[self.__ccU.ccaCartnZ])}
                                        origin = to_np_array(_origin)

                                        for _atomId in _nonBondedAtomIdSelect:
                                            _cca = next((_cca for _cca in self.__ccU.lastAtomList if _cca[self.__ccU.ccaAtomId] == _atomId), None)
                                            if _cca is not None:
                                                _neighbor = {'x': float(_cca[self.__ccU.ccaCartnX]), 'y': float(_cca[self.__ccU.ccaCartnY]), 'z': float(_cca[self.__ccU.ccaCartnZ])}

                                                if distance(to_np_array(_neighbor), origin) < 2.0:
                                                    _atomSelection.append({'chain_id': chainId, 'seq_id': seqId, 'comp_id': compId, 'atom_id': _atomId})

                    atomSelection = [dict(s) for s in set(frozenset(atom.items())
                                                          for atom in _atomSelection
                                                          if isinstance(atom, dict))]

                    if len(atomSelection) <= len(self.factor['atom_selection']):
                        self.factor['atom_id'] = [None]
                        self.__f.append(f"[Insufficient atom selection] {self.__getCurrentRestraint()}"
                                        "The 'bygroup' clause has no effect.")

                    self.factor['atom_selection'] = atomSelection

                else:
                    self.factor['atom_id'] = [None]
                    self.__f.append(f"[Insufficient atom selection] {self.__getCurrentRestraint()}"
                                    "The 'bygroup' clause has no effect because no atom is selected.")

            elif ctx.ByRes():
                if self.__sel_expr_debug:
                    print("  " * self.depth + "--> byres")
                if not self.__hasCoord:
                    return
                if 'atom_selection' in self.factor and len(self.factor['atom_selection']) > 0:
                    _atomSelection = []

                    _sequenceSelect = set()

                    for _atom in self.factor['atom_selection']:
                        chainId = _atom['chain_id']
                        seqId = _atom['seq_id']

                        _sequenceSelect.add((chainId, seqId))

                    for (chainId, seqId) in _sequenceSelect:
                        _atom = next(_atom for _atom in self.factor['atom_selection'] if _atom['chain_id'] == chainId and _atom['seq_id'] == seqId)
                        compId = _atom['comp_id']

                        _atomByRes =\
                            self.__cR.getDictListWithFilter('atom_site',
                                                            ATOM_NAME_DATA_ITEMS,
                                                            [{'name': self.__authAsymId, 'type': 'str', 'value': chainId},
                                                             {'name': self.__authSeqId, 'type': 'int', 'value': seqId},
                                                             {'name': self.__modelNumName, 'type': 'int',
                                                              'value': self.__representativeModelId},
                                                             {'name': 'label_alt_id', 'type': 'enum',
                                                              'enum': (self.__representativeAltId,)}
                                                             ])

                        if len(_atomByRes) > 0 and _atomByRes[0]['comp_id'] == compId:
                            for _atom in _atomByRes:
                                _atomSelection.append({'chain_id': chainId, 'seq_id': seqId, 'comp_id': _atom['comp_id'], 'atom_id': _atom['atom_id']})

                        else:
                            ps = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == chainId), None)
                            if ps is not None and seqId in ps['auth_seq_id'] and ps['comp_id'][ps['auth_seq_id'].index(seqId)] == compId:
                                seqId = self.getRealSeqId(ps, seqId)[0]
                                if self.__ccU.updateChemCompDict(compId):
                                    atomIds = [cca[self.__ccU.ccaAtomId] for cca in self.__ccU.lastAtomList if cca[self.__ccU.ccaLeavingAtomFlag] != 'Y']
                                    for atomId in atomIds:
                                        _atomSelection.append({'chain_id': chainId, 'seq_id': seqId, 'comp_id': compId, 'atom_id': atomId})
                            if self.__hasNonPolySeq:
                                npList = [np for np in self.__nonPolySeq if np['auth_chain_id'] == chainId]
                                for np in npList:
                                    if seqId in np['auth_seq_id'] and np['comp_id'][np['auth_seq_id'].index(seqId)] == compId:
                                        seqId = self.getRealSeqId(np, seqId, False)[0]
                                        if self.__ccU.updateChemCompDict(compId):
                                            atomIds = [cca[self.__ccU.ccaAtomId] for cca in self.__ccU.lastAtomList if cca[self.__ccU.ccaLeavingAtomFlag] != 'Y']
                                            for atomId in atomIds:
                                                _atomSelection.append({'chain_id': chainId, 'seq_id': seqId, 'comp_id': compId, 'atom_id': atomId})

                    self.factor['atom_selection'] = [dict(s) for s in set(frozenset(atom.items())
                                                                          for atom in _atomSelection
                                                                          if isinstance(atom, dict))]

                    if len(self.factor['atom_selection']) == 0:
                        self.factor['atom_id'] = [None]
                        self.__f.append(f"[Insufficient atom selection] {self.__getCurrentRestraint()}"
                                        "The 'byres' clause has no effect.")

                else:
                    self.factor['atom_id'] = [None]
                    self.__f.append(f"[Insufficient atom selection] {self.__getCurrentRestraint()}"
                                    "The 'byres' clause has no effect because no atom is selected.")

            elif ctx.Chemical():
                if self.__sel_expr_debug:
                    print("  " * self.depth + "--> chemical")
                if ctx.Colon():  # range expression
                    self.factor['type_symbols'] = [str(ctx.Simple_name(0)).upper(), str(ctx.Simple_name(1)).upper()]

                elif ctx.Simple_name(0):
                    self.factor['type_symbol'] = [str(ctx.Simple_name(0)).upper()]

                elif ctx.Simple_names(0):
                    self.factor['type_symbols'] = [str(ctx.Simple_names(0)).upper()]

                elif ctx.Symbol_name():
                    symbol_name = str(ctx.Symbol_name())
                    if symbol_name in self.evaluate:
                        val = self.evaluate[symbol_name]
                        if isinstance(val, list):
                            self.factor['type_symbol'] = [v.upper() for v in val]
                        else:
                            self.factor['type_symbol'] = [val.upper()]
                    else:
                        self.__f.append(f"[Unsupported data] {self.__getCurrentRestraint()}"
                                        f"The symbol {symbol_name!r} is not defined.")

                self.consumeFactor_expressions("'chemical' clause", False)

            elif ctx.Hydrogen():
                if self.__sel_expr_debug:
                    print("  " * self.depth + "--> hydrogen")
                if not self.__hasCoord:
                    return
                _typeSymbolSelect = set()
                atomTypes = self.__cR.getDictList('atom_type')
                if len(atomTypes) > 0 and 'symbol' in atomTypes[0]:
                    for atomType in atomTypes:
                        typeSymbol = atomType['symbol']
                        atomicNumber = int_atom(typeSymbol)
                        atomicWeight = ELEMENT_WEIGHTS[atomicNumber]
                        if atomicWeight < 3.5:
                            _typeSymbolSelect.add(typeSymbol)

                self.factor['type_symbol'] = list(_typeSymbolSelect)

                self.consumeFactor_expressions("'hydrogen' clause", False)

            elif ctx.NONE():
                if self.__sel_expr_debug:
                    print("  " * self.depth + "--> none")
                self.factor['atom_selection'] = []

            elif ctx.Not_op():
                if self.__sel_expr_debug:
                    print("  " * self.depth + "--> not")
                if not self.__hasCoord:
                    return

                if 'atom_selection' in self.factor and ('atom_id' in self.factor or 'atom_ids' in self.factor):
                    _refAtomSelection = self.factor['atom_selection']
                    del self.factor['atom_selection']
                    if self.stackFactors:
                        self.stackFactors.pop()
                    self.factor = self.__consumeFactor_expressions(self.factor, cifCheck=True)
                    if 'atom_selection' in self.factor:
                        self.factor['atom_selection'] = [atom for atom in _refAtomSelection
                                                         if isinstance(atom, dict)
                                                         and not any(_atom for _atom in self.factor['atom_selection']
                                                                     if _atom['chain_id'] == atom['chain_id']
                                                                     and _atom['seq_id'] == atom['seq_id']
                                                                     and _atom['atom_id'] == atom['atom_id'])]
                    else:
                        self.factor['atom_selection'] = _refAtomSelection
                    if len(self.factor['atom_selection']) == 0:
                        self.factor['atom_id'] = [None]
                        self.__f.append(f"[Insufficient atom selection] {self.__getCurrentRestraint()}"
                                        "The 'not' clause has no effect.")

                elif 'atom_selection' not in self.factor:
                    self.factor = self.__consumeFactor_expressions(self.factor, cifCheck=True)

                    if 'atom_selection' in self.factor:
                        _refAtomSelection = copy.deepcopy(self.factor['atom_selection'])
                        for atom in _refAtomSelection:
                            if 'is_poly' in atom:
                                del atom['is_poly']
                            if 'auth_atom_id' in atom:
                                del atom['auth_atom_id']

                        try:

                            _atomSelection =\
                                self.__cR.getDictListWithFilter('atom_site',
                                                                AUTH_ATOM_DATA_ITEMS,
                                                                [{'name': self.__modelNumName, 'type': 'int',
                                                                  'value': self.__representativeModelId},
                                                                 {'name': 'label_alt_id', 'type': 'enum',
                                                                  'enum': (self.__representativeAltId,)}
                                                                 ])

                        except Exception as e:
                            if self.__verbose:
                                self.__lfh.write(f"+{self.__class_name__}.exitFactor() ++ Error  - {str(e)}")

                        self.factor['atom_selection'] = [atom for atom in _atomSelection if atom not in _refAtomSelection]

                        if len(self.factor['atom_selection']) == 0:
                            self.factor['atom_id'] = [None]
                            self.__f.append(f"[Insufficient atom selection] {self.__getCurrentRestraint()}"
                                            "The 'not' clause has no effect.")

                    else:
                        self.factor['atom_id'] = [None]
                        self.__f.append(f"[Insufficient atom selection] {self.__getCurrentRestraint()}"
                                        "The 'not' clause has no effect.")

                else:

                    try:

                        _atomSelection =\
                            self.__cR.getDictListWithFilter('atom_site',
                                                            AUTH_ATOM_DATA_ITEMS,
                                                            [{'name': self.__modelNumName, 'type': 'int',
                                                              'value': self.__representativeModelId},
                                                             {'name': 'label_alt_id', 'type': 'enum',
                                                              'enum': (self.__representativeAltId,)}
                                                             ])

                    except Exception as e:
                        if self.__verbose:
                            self.__lfh.write(f"+{self.__class_name__}.exitFactor() ++ Error  - {str(e)}")

                    _refAtomSelection = copy.deepcopy(self.factor['atom_selection'])
                    for atom in _refAtomSelection:
                        if 'is_poly' in atom:
                            del atom['is_poly']
                        if 'auth_atom_id' in atom:
                            del atom['auth_atom_id']

                    _refAtomSelection = [atom for atom in _refAtomSelection if atom in _atomSelection]

                    self.factor['atom_selection'] = [atom for atom in _atomSelection if atom not in _refAtomSelection]

                    if len(self.factor['atom_selection']) == 0:
                        self.factor['atom_id'] = [None]
                        self.__f.append(f"[Insufficient atom selection] {self.__getCurrentRestraint()}"
                                        "The 'not' clause has no effect.")

            elif ctx.Point():
                if self.__sel_expr_debug:
                    print("  " * self.depth + "--> point")
                if not self.__hasCoord:
                    return
                vector3D = [self.numberFSelection[0], self.numberFSelection[1], self.numberFSelection[2]]
                cut = self.numberFSelection[3]

                atomSelection = []

                try:

                    _neighbor =\
                        self.__cR.getDictListWithFilter('atom_site',
                                                        AUTH_ATOM_CARTN_DATA_ITEMS,
                                                        [{'name': 'Cartn_x', 'type': 'range-float',
                                                          'range': {'min_exclusive': (vector3D[0] - cut),
                                                                    'max_exclusive': (vector3D[0] + cut)}},
                                                         {'name': 'Cartn_y', 'type': 'range-float',
                                                          'range': {'min_exclusive': (vector3D[1] - cut),
                                                                    'max_exclusive': (vector3D[1] + cut)}},
                                                         {'name': 'Cartn_z', 'type': 'range-float',
                                                          'range': {'min_exclusive': (vector3D[2] - cut),
                                                                    'max_exclusive': (vector3D[2] + cut)}},
                                                         {'name': self.__modelNumName, 'type': 'int',
                                                          'value': self.__representativeModelId},
                                                         {'name': 'label_alt_id', 'type': 'enum',
                                                          'enum': (self.__representativeAltId,)}
                                                         ])

                    if len(_neighbor) > 0:
                        neighbor = [atom for atom in _neighbor if distance(to_np_array(atom), vector3D) < cut]

                        for atom in neighbor:
                            del atom['x']
                            del atom['y']
                            del atom['z']
                            atomSelection.append(atom)

                except Exception as e:
                    if self.__verbose:
                        self.__lfh.write(f"+{self.__class_name__}.exitFactor() ++ Error  - {str(e)}")

                self.factor['atom_selection'] = atomSelection

                if len(self.factor['atom_selection']) == 0:
                    self.factor['atom_id'] = [None]
                    self.__f.append(f"[Insufficient atom selection] {self.__getCurrentRestraint()}"
                                    "The 'cut' clause has no effect.")

            elif ctx.Lone():
                if self.__sel_expr_debug:
                    print("  " * self.depth + "--> lone")
                self.factor['atom_id'] = [None]
                self.__f.append(f"[Unsupported data] {self.__getCurrentRestraint()}"
                                "The 'lone' clause has no effect "
                                "because the internal atom selection is fragile in the restraint file.")

            elif ctx.Previous():
                if self.__sel_expr_debug:
                    print("  " * self.depth + "--> previous")
                self.factor['atom_id'] = [None]
                self.__f.append(f"[Unsupported data] {self.__getCurrentRestraint()}"
                                "The 'previous' clause has no effect "
                                "because the internal atom selection is fragile in the restraint file.")

            elif ctx.User():
                if self.__sel_expr_debug:
                    print("  " * self.depth + "--> user")
                self.factor['atom_id'] = [None]
                self.__f.append(f"[Unsupported data] {self.__getCurrentRestraint()}"
                                "The 'user' clause has no effect "
                                "because the internal atom selection is fragile in the restraint file.")

            elif ctx.Recall():
                if self.__sel_expr_debug:
                    print("  " * self.depth + "--> recall")
                self.factor['atom_id'] = [None]
                self.__f.append(f"[Unsupported data] {self.__getCurrentRestraint()}"
                                "The 'recall' clause has no effect "
                                "because the internal atom selection is fragile in the restraint file.")

            elif ctx.IGroup():
                if self.__sel_expr_debug:
                    print("  " * self.depth + "--> igroup")
                self.factor['atom_id'] = [None]
                self.__f.append(f"[Unsupported data] {self.__getCurrentRestraint()}"
                                "The 'igroup' clause has no effect "
                                "because the internal atom selection is fragile in the restraint file.")

            elif ctx.Subset():
                if self.__sel_expr_debug:
                    print("  " * self.depth + "--> subset")
                self.factor['atom_id'] = [None]
                self.__f.append(f"[Unsupported data] {self.__getCurrentRestraint()}"
                                "The 'subset' clause has no effect "
                                "because the internal atom selection is fragile in the restraint file.")

            elif ctx.ByNumber():
                if self.__sel_expr_debug:
                    print("  " * self.depth + "--> bynumber")

                if ctx.Colon():  # range expression
                    self.factor['atom_num'] = list(range(int(str(ctx.Integer(0))), int(str(ctx.Integer(0))) + 1))

                elif ctx.Integer(0):
                    self.factor['atom_num'] = [int(str(ctx.Integer(0)))]

                elif ctx.Integers():
                    self.factor['atom_nums'] = [str(ctx.Integers())]

                elif ctx.Symbol_name():
                    symbol_name = str(ctx.Symbol_name())
                    if symbol_name in self.evaluate:
                        val = self.evaluate[symbol_name]
                        if isinstance(val, list):
                            self.factor['atom_num'] = [v if isinstance(v, int) else int(v) for v in val]
                        else:
                            self.factor['atom_num'] = [val if isinstance(val, int) else int(val)]
                    else:
                        self.__f.append(f"[Unsupported data] {self.__getCurrentRestraint()}"
                                        f"The symbol {symbol_name!r} is not defined.")

                if 'atom_num' in self.factor and self.__atomNumberDict is not None:
                    for ai in self.factor['atom_num']:
                        if ai in self.__atomNumberDict:
                            _factor = copy.copy(self.__atomNumberDict[ai])
                            if 'chain_id' not in self.factor:
                                self.factor['chain_id'] = []
                            if _factor['chain_id'] not in self.factor['chain_id']:
                                self.factor['chain_id'].append(_factor['chain_id'])
                            if 'seq_id' not in self.factor:
                                self.factor['seq_id'] = []
                            if _factor['seq_id'] not in self.factor['seq_id']:
                                self.factor['seq_id'].append(_factor['seq_id'])
                            if 'comp_id' not in self.factor:
                                self.factor['comp_id'] = []
                            if _factor['comp_id'] not in self.factor['comp_id']:
                                self.factor['comp_id'].append(_factor['comp_id'])
                            if 'atom_id' not in self.factor:
                                self.factor['atom_id'] = []
                            if _factor['atom_id'] not in self.factor['atom_id']:
                                self.factor['atom_id'].append(_factor['atom_id'])
                            self.factor['atom_num'].remove(ai)
                            if len(self.factor['atom_num']) == 0:
                                del self.factor['atom_num']
                        else:
                            self.__f.append(f"[Missing data] {self.__getCurrentRestraint()}"
                                            f"'{ai}' is not defined in the CHARMM CRD file.")

            elif ctx.IRes():
                if self.__sel_expr_debug:
                    print("  " * self.depth + "--> ires")

                if ctx.Colon():  # range expression
                    self.factor['seq_id'] = list(range(int(str(ctx.Integer(0))), int(str(ctx.Integer(0))) + 1))

                elif ctx.Integer(0):
                    self.factor['seq_id'] = [int(str(ctx.Integer(0)))]

                elif ctx.Integers():
                    self.factor['seq_ids'] = [str(ctx.Integers())]

                elif ctx.Symbol_name():
                    symbol_name = str(ctx.Symbol_name())
                    if symbol_name in self.evaluate:
                        val = self.evaluate[symbol_name]
                        if isinstance(val, list):
                            self.factor['seq_id'] = [v if isinstance(v, int) else int(v) for v in val]
                        else:
                            self.factor['seq_id'] = [val if isinstance(val, int) else int(val)]
                    else:
                        self.__f.append(f"[Unsupported data] {self.__getCurrentRestraint()}"
                                        f"The symbol {symbol_name!r} is not defined.")

            elif ctx.Residue():
                if self.__sel_expr_debug:
                    print("  " * self.depth + "--> residue")

                eval_factor = False
                __factor = None
                if 'seq_id' in self.factor or 'seq_ids' in self.factor:
                    __factor = copy.copy(self.factor)
                    self.consumeFactor_expressions("'residue' clause", False)
                    eval_factor = True

                if not eval_factor and 'atom_selection' in self.factor:
                    self.factor = {}

                if ctx.Colon():  # range expression
                    self.factor['seq_id'] = list(range(int(str(ctx.Integer(0))), int(str(ctx.Integer(0))) + 1))

                elif ctx.Integer(0):
                    self.factor['seq_id'] = [int(str(ctx.Integer(0)))]

                elif ctx.Integers():
                    self.factor['seq_ids'] = [str(ctx.Integers())]

                elif ctx.Symbol_name():
                    symbol_name = str(ctx.Symbol_name())
                    if symbol_name in self.evaluate:
                        val = self.evaluate[symbol_name]
                        if isinstance(val, list):
                            self.factor['seq_id'] = [v if isinstance(v, int) else int(v) for v in val]
                        else:
                            self.factor['seq_id'] = [val if isinstance(val, int) else int(val)]
                    else:
                        self.__f.append(f"[Unsupported data] {self.__getCurrentRestraint()}"
                                        f"The symbol {symbol_name!r} is not defined.")

                if eval_factor and 'atom_selection' in self.factor:
                    if len(self.factor['atom_selection']) == 0:
                        _factor = copy.copy(self.factor)
                        if 'atom_selection' in __factor:
                            del __factor['atom_selection']
                        del _factor['atom_selection']
                        self.__f.append(f"[Insufficient atom selection] {self.__getCurrentRestraint()}"
                                        f"The 'residue' clause has no effect for a conjunction of factor {getReadableFactor(__factor)} "
                                        f"and {getReadableFactor(_factor)}.")

            elif ctx.Resname():
                if self.__sel_expr_debug:
                    print("  " * self.depth + "--> resname")

                eval_factor = False
                if 'comp_id' in self.factor or 'comp_ids' in self.factor:
                    __factor = copy.copy(self.factor)
                    self.consumeFactor_expressions("'resname' clause", False)
                    eval_factor = True

                if not eval_factor and 'atom_selection' in self.factor:
                    self.factor = {}

                if ctx.Colon():  # range expression
                    self.factor['comp_ids'] = [str(ctx.Simple_name(0)).upper(), str(ctx.Simple_name(1)).upper()]

                elif ctx.Simple_name(0):
                    self.factor['comp_id'] = [str(ctx.Simple_name(0)).upper()]

                elif ctx.Simple_names(0):
                    self.factor['comp_ids'] = [str(ctx.Simple_names(0)).upper()]

                elif ctx.Symbol_name():
                    symbol_name = str(ctx.Symbol_name())
                    if symbol_name in self.evaluate:
                        val = self.evaluate[symbol_name]
                        if isinstance(val, list):
                            self.factor['comp_id'] = [v.upper() for v in val]
                        else:
                            self.factor['comp_id'] = [val.upper()]
                    else:
                        self.__f.append(f"[Unsupported data] {self.__getCurrentRestraint()}"
                                        f"The symbol {symbol_name!r} is not defined.")

                if eval_factor and 'atom_selection' in self.factor:
                    if len(self.factor['atom_selection']) == 0:
                        _factor = copy.copy(self.factor)
                        if 'atom_selection' in __factor:
                            del __factor['atom_selection']
                        del _factor['atom_selection']
                        self.__f.append(f"[Insufficient atom selection] {self.__getCurrentRestraint()}"
                                        f"The 'resname' clause has no effect for a conjunction of factor {getReadableFactor(__factor)} "
                                        f"and {getReadableFactor(_factor)}.")

            elif ctx.ISeg():
                if self.__sel_expr_debug:
                    print("  " * self.depth + "--> iseg")

                if ctx.Colon():  # range expression
                    self.factor['chain_id'] = [str(id) for id in range(int(str(ctx.Integer(0))), int(str(ctx.Integer(0))) + 1)]

                elif ctx.Integer(0):
                    self.factor['chain_id'] = [str(ctx.Integer(0))]

                elif ctx.Integers():
                    self.factor['chain_ids'] = [str(ctx.Integers())]

                elif ctx.Symbol_name():
                    symbol_name = str(ctx.Symbol_name())
                    if symbol_name in self.evaluate:
                        val = self.evaluate[symbol_name]
                        if isinstance(val, list):
                            self.factor['chain_id'] = [str(v) if isinstance(v, int) else int(v) for v in val]
                        else:
                            self.factor['chain_id'] = [str(val) if isinstance(val, int) else int(val)]
                    else:
                        self.__f.append(f"[Unsupported data] {self.__getCurrentRestraint()}"
                                        f"The symbol {symbol_name!r} is not defined.")

            elif ctx.SegIdentifier():
                if self.__sel_expr_debug:
                    print("  " * self.depth + "--> segidentifier")
                if not self.__hasPolySeq and not self.__hasNonPolySeq:
                    return

                eval_factor = False
                if 'chain_id' in self.factor:
                    __factor = copy.copy(self.factor)
                    self.consumeFactor_expressions("'segidentifier' clause", False)
                    eval_factor = True

                if not eval_factor and 'atom_selection' in self.factor:
                    self.factor = {}

                if ctx.Colon():  # range expression
                    if ctx.Simple_name(0):
                        begChainId = str(ctx.Simple_name(0))
                    elif ctx.Double_quote_string(0):
                        begChainId = str(ctx.Double_quote_string(0)).strip('"').strip()
                        if len(begChainId) == 0:
                            return
                    if ctx.Simple_name(1):
                        endChainId = str(ctx.Simple_name(1))
                    elif ctx.Double_quote_string(1):
                        endChainId = str(ctx.Double_quote_string(1)).strip('"').strip()
                        if len(endChainId) == 0:
                            return
                    self.factor['chain_id'] = [ps['auth_chain_id'] for ps in self.__polySeq
                                               if begChainId <= ps['auth_chain_id'] <= endChainId]
                    if self.__hasNonPolySeq:
                        for np in self.__nonPolySeq:
                            _chainId = np['auth_chain_id']
                            if begChainId <= _chainId <= endChainId and _chainId not in self.factor['chain_id']:
                                self.factor['chain_id'].append(_chainId)

                    if len(self.factor['chain_id']) == 0:
                        if len(self.__polySeq) == 1:
                            self.factor['chain_id'] = self.__polySeq[0]['auth_chain_id']
                            self.factor['auth_chain_id'] = [begChainId, endChainId]
                        elif self.__reasons is not None:
                            self.factor['atom_id'] = [None]
                            if 'segment_id_mismatch' in self.__reasons\
                               and (chainId not in self.__reasons['segment_id_mismatch']
                                    or self.__reasons['segment_id_mismatch'][chainId] is not None):
                                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                                "Couldn't specify segment name "
                                                f"{begChainId:!r}:{endChainId:!r} in the coordinates.")

                else:
                    if ctx.Simple_name(0) or ctx.Double_quote_string(0):
                        if ctx.Simple_name(0):
                            chainId = str(ctx.Simple_name(0))
                        elif ctx.Double_quote_string(0):
                            chainId = str(ctx.Double_quote_string(0)).strip('"').strip()
                            if len(chainId) == 0:
                                return
                        self.factor['chain_id'] = [ps['auth_chain_id'] for ps in self.__polySeq
                                                   if ps['auth_chain_id'] == self.getRealChainId(chainId)]
                        if self.__hasNonPolySeq:
                            for np in self.__nonPolySeq:
                                _chainId = np['auth_chain_id']
                                if _chainId == self.getRealChainId(chainId) and _chainId not in self.factor['chain_id']:
                                    self.factor['chain_id'].append(_chainId)
                        self.factor['segment_id'] = chainId
                        if self.factor['chain_id'] != [chainId]:
                            self.factor['alt_chain_id'] = chainId
                    if ctx.Simple_names(0):
                        chainId = str(ctx.Simple_names(0))
                        if self.__reasons is not None and 'segment_id_mismatch' in self.__reasons and chainId in self.__reasons['segment_id_mismatch']\
                           and self.__reasons['segment_id_mismatch'][chainId] in self.__reasons['segment_id_match_stats'][chainId]:
                            _chainId = self.__reasons['segment_id_mismatch'][chainId]
                            _stats = self.__reasons['segment_id_match_stats'][chainId]
                            self.factor['chain_id'] = sorted([k for k, v in _stats.items() if v == _stats[_chainId]])
                            self.factor['alt_chain_id'] = chainId
                        else:
                            _chainId = toRegEx(chainId)
                            self.factor['chain_id'] = [ps['auth_chain_id'] for ps in self.__polySeq
                                                       if re.match(_chainId, ps['auth_chain_id'])]
                            if self.__hasNonPolySeq:
                                for np in self.__nonPolySeq:
                                    __chainId = np['auth_chain_id']
                                    if re.match(_chainId, __chainId) and __chainId not in self.factor['chain_id']:
                                        self.factor['chain_id'].append(__chainId)
                    if ctx.Symbol_name():
                        symbol_name = chainId = str(ctx.Symbol_name())
                        if symbol_name in self.evaluate:
                            val = self.evaluate[symbol_name]
                            if isinstance(val, list):
                                self.factor['chain_id'] = val
                                self.factor['segment_id'] = val
                            else:
                                self.factor['chain_id'] = [val]
                        else:
                            self.__f.append(f"[Unsupported data] {self.__getCurrentRestraint()}"
                                            f"The symbol {symbol_name!r} is not defined.")
                    if len(self.factor['chain_id']) == 0:
                        if len(self.__polySeq) == 1 and not self.__hasBranched and not self.__hasNonPoly:
                            self.factor['chain_id'] = self.__polySeq[0]['auth_chain_id']
                            self.factor['auth_chain_id'] = chainId
                        elif self.__reasons is not None:
                            self.factor['atom_id'] = [None]
                            if 'segment_id_mismatch' in self.__reasons\
                               and (chainId not in self.__reasons['segment_id_mismatch']
                                    or self.__reasons['segment_id_mismatch'][chainId] is not None):
                                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                                "Couldn't specify segment name "
                                                f"'{chainId}' in the coordinates.")  # do not use 'chainId!r' expression, '%' code throws ValueError
                        else:
                            if 'segment_id_mismatch' not in self.reasonsForReParsing:
                                self.reasonsForReParsing['segment_id_mismatch'] = {}
                                self.reasonsForReParsing['segment_id_match_stats'] = {}
                                self.reasonsForReParsing['segment_id_poly_type_stats'] = {}
                            if chainId not in self.reasonsForReParsing['segment_id_mismatch']:
                                self.reasonsForReParsing['segment_id_mismatch'][chainId] = None
                                self.reasonsForReParsing['segment_id_match_stats'][chainId] = {}
                                self.reasonsForReParsing['segment_id_poly_type_stats'][chainId] = {'polymer': 0, 'non-poly': 0}
                            self.factor['alt_chain_id'] = chainId

                if eval_factor and 'atom_selection' in self.factor:
                    if len(self.factor['atom_selection']) == 0:
                        _factor = copy.copy(self.factor)
                        if 'atom_selection' in __factor:
                            del __factor['atom_selection']
                        del _factor['atom_selection']
                        self.__f.append(f"[Insufficient atom selection] {self.__getCurrentRestraint()}"
                                        f"The 'segidentifier' clause has no effect for a conjunction of factor {getReadableFactor(__factor)} "
                                        f"and {getReadableFactor(_factor)}.")

            if self.depth > 0 and self.__cur_union_expr:
                self.unionFactor = self.factor
            else:
                self.stackFactors.append(self.factor)

        finally:
            self.numberFSelection.clear()

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

    # Enter a parse tree produced by CharmmMRParser#number.
    def enterNumber(self, ctx: CharmmMRParser.NumberContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by CharmmMRParser#number.
    def exitNumber(self, ctx: CharmmMRParser.NumberContext):
        if ctx.Real():
            self.numberSelection.append(float(str(ctx.Real())))

        elif ctx.Integer():
            self.numberSelection.append(float(str(ctx.Integer())))

        elif ctx.Symbol_name():
            symbol_name = str(ctx.Symbol_name())
            if symbol_name in self.evaluate:
                self.numberSelection.append(float(self.evaluate[symbol_name]))
            else:
                self.__f.append(f"[Unsupported data] {self.__getCurrentRestraint()}"
                                f"The symbol {symbol_name!r} is not defined.")
                self.numberSelection.append(None)

        else:
            self.numberSelection.append(None)

    # Enter a parse tree produced by CharmmMRParser#number_f.
    def enterNumber_f(self, ctx: CharmmMRParser.Number_fContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by CharmmMRParser#number_f.
    def exitNumber_f(self, ctx: CharmmMRParser.Number_fContext):
        if ctx.Real():
            self.numberFSelection.append(float(str(ctx.Real())))

        elif ctx.Integer():
            self.numberFSelection.append(float(str(ctx.Integer())))

        else:
            self.numberFSelection.append(None)

    # Enter a parse tree produced by CharmmMRParser#number_s.
    def enterNumber_s(self, ctx: CharmmMRParser.Number_sContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by CharmmMRParser#number_s.
    def exitNumber_s(self, ctx: CharmmMRParser.Number_sContext):  # pylint: disable=unused-argument
        pass

    def getNumber_s(self, ctx: CharmmMRParser.Number_sContext):  # pylint: disable=no-self-use
        if ctx is None:
            return None

        if ctx.Real():
            return float(str(ctx.Real()))

        if ctx.Integer():
            return float(str(ctx.Integer()))

        if ctx.Symbol_name():
            return str(ctx.Symbol_name())

        return None

    # Enter a parse tree produced by CharmmMRParser#set_statement.
    def enterSet_statement(self, ctx: CharmmMRParser.Set_statementContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by CharmmMRParser#set_statement.
    def exitSet_statement(self, ctx: CharmmMRParser.Set_statementContext):
        if ctx.Simple_name_VE(0):

            if ctx.Real_VE():
                self.evaluate[str(ctx.Simple_name_VE(0))] = float(str(ctx.Real_VE()))

            elif ctx.Integer_VE():
                self.evaluate[str(ctx.Simple_name_VE(0))] = int(str(ctx.Integer_VE()))

            elif ctx.Simple_name_VE(1):
                self.evaluate[str(ctx.Simple_name_VE(0))] = str(ctx.Simple_name_VE(1))

    def __getCurrentRestraint(self) -> str:
        if self.__cur_subtype == 'dist':
            return f"[Check the {self.distRestraints}th row of distance restraints, {self.__def_err_sf_framecode}] "
        if self.__cur_subtype == 'dihed':
            return f"[Check the {self.dihedRestraints}th row of dihedral angle restraints, {self.__def_err_sf_framecode}] "
        if self.__cur_subtype == 'geo':
            return f"[Check the {self.geoRestraints}th row of harmonic coordinate/NCS restraints, {self.__def_err_sf_framecode}] "
        return ''

    def __setLocalSeqScheme(self):
        if 'local_seq_scheme' not in self.reasonsForReParsing:
            self.reasonsForReParsing['local_seq_scheme'] = {}
        if self.__cur_subtype == 'dist':
            self.reasonsForReParsing['local_seq_scheme'][(self.__cur_subtype, self.distRestraints)] = self.__preferAuthSeq
        elif self.__cur_subtype == 'dihed':
            self.reasonsForReParsing['local_seq_scheme'][(self.__cur_subtype, self.dihedRestraints)] = self.__preferAuthSeq
        elif self.__cur_subtype == 'geo':
            self.reasonsForReParsing['local_seq_scheme'][(self.__cur_subtype, self.geoRestraints)] = self.__preferAuthSeq
        if not self.__preferAuthSeq:
            self.__preferLabelSeqCount += 1
            if self.__preferLabelSeqCount > MAX_PREF_LABEL_SCHEME_COUNT:
                if 'label_seq_scheme' not in self.reasonsForReParsing:
                    self.reasonsForReParsing['label_seq_scheme'] = {}
                self.reasonsForReParsing['label_seq_scheme'][self.__cur_subtype] = True

    def __retrieveLocalSeqScheme(self):
        if self.__reasons is None\
           or ('label_seq_scheme' not in self.__reasons
               and 'local_seq_scheme' not in self.__reasons
               and 'extend_seq_scheme' not in self.__reasons):
            #    and 'inhibit_label_seq_scheme' not in self.__reasons):
            return
        if 'extend_seq_scheme' in self.__reasons:
            self.__extendAuthSeq = True
            if 'label_seq_scheme' not in self.__reasons:  # 2joa
                self.__preferAuthSeq = True
                self.__authSeqId = 'label_seq_id'
            return
        if 'label_seq_scheme' in self.__reasons and self.__reasons['label_seq_scheme']:  # \
            # and 'segment_id_mismatch' not in self.__reasons:
            if self.__cur_subtype in self.__reasons['label_seq_scheme']\
               and self.__reasons['label_seq_scheme'][self.__cur_subtype]:
                self.__preferAuthSeq = False
                self.__authSeqId = 'label_seq_id'
                return
            if self.__cur_subtype != 'dist' and 'dist' in self.__reasons['label_seq_scheme']\
               and self.__reasons['label_seq_scheme']['dist']:
                self.__preferAuthSeq = False
                self.__authSeqId = 'label_seq_id'
                return
        if 'local_seq_scheme' not in self.__reasons:
            return
        if self.__cur_subtype == 'dist':
            key = (self.__cur_subtype, self.distRestraints)
        elif self.__cur_subtype == 'dihed':
            key = (self.__cur_subtype, self.dihedRestraints)
        elif self.__cur_subtype == 'geo':
            key = (self.__cur_subtype, self.geoRestraints)
        else:
            return

        if key in self.__reasons['local_seq_scheme']:
            self.__preferAuthSeq = self.__reasons['local_seq_scheme'][key]

    def __addSf(self, constraintType: Optional[str] = None, potentialType: Optional[str] = None):
        content_subtype = contentSubtypeOf(self.__cur_subtype)

        if content_subtype is None:
            return

        self.__listIdCounter = incListIdCounter(self.__cur_subtype, self.__listIdCounter)

        key = (self.__cur_subtype, constraintType, potentialType, None, None)

        if key in self.sfDict:
            if len(self.sfDict[key]) > 0:
                decListIdCounter(self.__cur_subtype, self.__listIdCounter)
                return
        else:
            self.sfDict[key] = []

        list_id = self.__listIdCounter[content_subtype]

        restraint_name = getRestraintName(self.__cur_subtype)

        sf_framecode = 'CHARMM_' + restraint_name.replace(' ', '_') + f'_{list_id}'

        sf = getSaveframe(self.__cur_subtype, sf_framecode, list_id, self.__entryId, self.__originalFileName,
                          constraintType=constraintType, potentialType=potentialType)

        lp = getLoop(self.__cur_subtype, hasInsCode=self.__authToInsCode is not None)
        if not isinstance(lp, dict):
            sf.add_loop(lp)

        _restraint_name = restraint_name.split()

        item = {'file_type': self.__file_type, 'saveframe': sf, 'loop': lp, 'list_id': list_id,
                'id': 0, 'index_id': 0,
                'constraint_type': ' '.join(_restraint_name[:-1]),
                'sf_framecode': sf_framecode}

        if self.__cur_subtype == 'dist':
            item['constraint_subsubtype'] = 'simple'
            if constraintType is None:
                item['NOE_dist_averaging_method'] = self.noeAverage
            elif 'ROE' in constraintType:
                item['ROE_dist_averaging_method'] = self.noeAverage

        self.__lastSfDict[self.__cur_subtype] = item

        self.sfDict[key].append(item)

    def __getSf(self, constraintType: Optional[str] = None, potentialType: Optional[str] = None) -> dict:
        key = (self.__cur_subtype, constraintType, potentialType, None, None)

        if key not in self.sfDict:
            replaced = False
            if potentialType is not None:
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
            if not replaced:
                self.__addSf(constraintType=constraintType, potentialType=potentialType)

        self.__cur_constraint_type = constraintType

        _key = next((_key for _key in self.sfDict if _key[0] == 'dist' and _key[1] is None), key) if self.__cur_subtype == 'dist' else key
        self.__def_err_sf_framecode = self.sfDict[_key][-1]['sf_framecode']

        sf = self.sfDict[key][-1]

        if self.classification not in emptyValue and 'classification' not in sf:
            if get_first_sf_tag(sf['saveframe'], 'Details') in emptyValue:
                set_sf_tag(sf['saveframe'], 'Details', self.classification)
                sf['classification'] = self.classification

        return sf

    def __trimSfWoLp(self):
        if self.__cur_subtype not in self.__lastSfDict:
            return
        if self.__lastSfDict[self.__cur_subtype]['index_id'] > 0:
            return
        for k, v in self.sfDict.items():
            for item in reversed(v):
                if item == self.__lastSfDict:
                    v.remove(item)
                    if len(v) == 0:
                        del self.sfDict[k]
                    self.__listIdCounter = decListIdCounter(k[0], self.__listIdCounter)
                    return

    def getContentSubtype(self) -> dict:
        """ Return content subtype of CHARMM MR file.
        """

        contentSubtype = {'dist_restraint': self.distRestraints,
                          'dihed_restraint': self.dihedRestraints,
                          'geo_restraint': self.geoRestraints
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
        """ Return polymer sequence of CHARMM MR file.
        """

        return None if self.__polySeqRst is None or len(self.__polySeqRst) == 0 else self.__polySeqRst

    def getSequenceAlignment(self) -> Optional[List[dict]]:
        """ Return sequence alignment between coordinates and CHARMM MR.
        """

        return None if self.__seqAlign is None or len(self.__seqAlign) == 0 else self.__seqAlign

    def getChainAssignment(self) -> Optional[List[dict]]:
        """ Return chain assignment between coordinates and CHARMM MR.
        """

        return None if self.__chainAssign is None or len(self.__chainAssign) == 0 else self.__chainAssign

    def getReasonsForReparsing(self) -> Optional[dict]:
        """ Return reasons for re-parsing CHARMM MR file.
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

# del CharmmMRParser
