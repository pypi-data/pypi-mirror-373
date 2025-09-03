##
# File: GromacsMRParserListener.py
# Date: 02-June-2022
#
# Updates:
""" ParserLister class for GROMACS MR files.
    @author: Masashi Yokochi
"""
__docformat__ = "restructuredtext en"
__author__ = "Masashi Yokochi"
__email__ = "yokochi@protein.osaka-u.ac.jp"
__license__ = "Apache License 2.0"
__version__ = "1.0.0"

import sys
import copy
import itertools
import numpy

from antlr4 import ParseTreeListener
from typing import IO, List, Tuple, Optional

from wwpdb.utils.align.alignlib import PairwiseAlign  # pylint: disable=no-name-in-module

try:
    from wwpdb.utils.nmr.io.CifReader import CifReader
    from wwpdb.utils.nmr.mr.GromacsMRParser import GromacsMRParser
    from wwpdb.utils.nmr.mr.ParserListenerUtil import (coordAssemblyChecker,
                                                       isIdenticalRestraint,
                                                       isLongRangeRestraint,
                                                       isAmbigAtomSelection,
                                                       getAltProtonIdInBondConstraint,
                                                       getTypeOfDihedralRestraint,
                                                       fixBackboneAtomsOfDihedralRestraint,
                                                       isLikePheOrTyr,
                                                       getRdcCode,
                                                       getRestraintName,
                                                       contentSubtypeOf,
                                                       incListIdCounter,
                                                       decListIdCounter,
                                                       getSaveframe,
                                                       getLoop,
                                                       getRow,
                                                       getStarAtom,
                                                       resetMemberId,
                                                       getDistConstraintType,
                                                       getPotentialType,
                                                       ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS,
                                                       REPRESENTATIVE_MODEL_ID,
                                                       REPRESENTATIVE_ALT_ID,
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
                                                       CARTN_DATA_ITEMS)
    from wwpdb.utils.nmr.ChemCompUtil import ChemCompUtil
    from wwpdb.utils.nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from wwpdb.utils.nmr.nef.NEFTranslator import NEFTranslator
    from wwpdb.utils.nmr.AlignUtil import (emptyValue,
                                           rdcBbPairCode,
                                           updatePolySeqRstFromAtomSelectionSet,
                                           sortPolySeqRst,
                                           alignPolymerSequence,
                                           assignPolymerSequence,
                                           trimSequenceAlignment)
    from wwpdb.utils.nmr.NmrVrptUtility import (to_np_array,
                                                distance,
                                                dist_error,
                                                angle_target_values,
                                                dihedral_angle,
                                                angle_error)
except ImportError:
    from nmr.io.CifReader import CifReader
    from nmr.mr.GromacsMRParser import GromacsMRParser
    from nmr.mr.ParserListenerUtil import (coordAssemblyChecker,
                                           isIdenticalRestraint,
                                           isLongRangeRestraint,
                                           isAmbigAtomSelection,
                                           getAltProtonIdInBondConstraint,
                                           getTypeOfDihedralRestraint,
                                           fixBackboneAtomsOfDihedralRestraint,
                                           isLikePheOrTyr,
                                           getRdcCode,
                                           getRestraintName,
                                           contentSubtypeOf,
                                           incListIdCounter,
                                           decListIdCounter,
                                           getSaveframe,
                                           getLoop,
                                           getRow,
                                           getStarAtom,
                                           resetMemberId,
                                           getDistConstraintType,
                                           getPotentialType,
                                           ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS,
                                           REPRESENTATIVE_MODEL_ID,
                                           REPRESENTATIVE_ALT_ID,
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
                                           CARTN_DATA_ITEMS)
    from nmr.ChemCompUtil import ChemCompUtil
    from nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from nmr.nef.NEFTranslator import NEFTranslator
    from nmr.AlignUtil import (emptyValue,
                               rdcBbPairCode,
                               updatePolySeqRstFromAtomSelectionSet,
                               sortPolySeqRst,
                               alignPolymerSequence,
                               assignPolymerSequence,
                               trimSequenceAlignment)
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


# This class defines a complete listener for a parse tree produced by GromacsMRParser.
class GromacsMRParserListener(ParseTreeListener):

    __file_type = 'nm-res-gro'

    __verbose = None
    __lfh = None
    __debug = False

    __createSfDict = False
    __omitDistLimitOutlier = True
    __correctCircularShift = True

    # atom name mapping of public MR file between the archive coordinates and submitted ones
    # __mrAtomNameMapping = None

    # CCD accessing utility
    __ccU = None

    # BMRB chemical shift statistics
    __csStat = None

    # NEFTranslator
    __nefT = None

    # Pairwise align
    __pA = None

    # GromacsPTParserListener.getAtomNumberDict()
    __atomNumberDict = None

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
    # __altPolySeq = None
    __nonPoly = None
    __branched = None
    # __coordAtomSite = None
    # __coordUnobsRes = None
    # __labelToAuthSeq = None
    # __authToLabelSeq = None
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

    # polymer sequence of MR file
    __polySeqRst = None

    __seqAlign = None
    __chainAssign = None

    # current restraint subtype
    __cur_subtype = ''

    # collection of atom selection
    atomSelectionSet = []

    # collection of number selection
    numberSelection = []

    __f = None
    warningMessage = None

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

    def __init__(self, verbose: bool = True, log: IO = sys.stdout,
                 representativeModelId: int = REPRESENTATIVE_MODEL_ID,
                 representativeAltId: str = REPRESENTATIVE_ALT_ID,
                 mrAtomNameMapping: Optional[List[dict]] = None,  # pylint: disable=unused-argument
                 cR: Optional[CifReader] = None, caC: Optional[dict] = None, ccU: Optional[ChemCompUtil] = None,
                 csStat: Optional[BMRBChemShiftStat] = None, nefT: Optional[NEFTranslator] = None,
                 atomNumberDict: Optional[dict] = None):
        self.__class_name__ = self.__class__.__name__
        self.__version__ = __version__

        self.__verbose = verbose
        self.__lfh = log

        self.__representativeModelId = representativeModelId
        self.__representativeAltId = representativeAltId
        # self.__mrAtomNameMapping = None if mrAtomNameMapping is None or len(mrAtomNameMapping) == 0 else mrAtomNameMapping

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
            # self.__altPolySeq = ret['alt_polymer_sequence']
            # self.__coordAtomSite = ret['coord_atom_site']
            # self.__coordUnobsRes = ret['coord_unobs_res']
            # self.__labelToAuthSeq = ret['label_to_auth_seq']
            # self.__authToLabelSeq = ret['auth_to_label_seq']
            self.__authToStarSeq = ret['auth_to_star_seq']
            self.__authToOrigSeq = ret['auth_to_orig_seq']
            self.__authToInsCode = ret['auth_to_ins_code']

        self.__offsetHolder = {}

        self.__hasPolySeq = self.__polySeq is not None and len(self.__polySeq) > 0
        self.__hasNonPoly = self.__nonPoly is not None and len(self.__nonPoly) > 0
        self.__hasBranched = self.__branched is not None and len(self.__branched) > 0
        if self.__hasNonPoly or self.__hasBranched:
            self.__hasNonPolySeq = True

        if self.__hasPolySeq:
            self.__gapInAuthSeq = any(ps for ps in self.__polySeq if 'gap_in_auth_seq' in ps and ps['gap_in_auth_seq'])

        # BMRB chemical shift statistics
        self.__csStat = BMRBChemShiftStat(verbose, log, self.__ccU) if csStat is None else csStat

        # NEFTranslator
        self.__nefT = NEFTranslator(verbose, log, self.__ccU, self.__csStat) if nefT is None else nefT

        # Pairwise align
        if self.__hasPolySeq:
            self.__pA = PairwiseAlign()
            self.__pA.setVerbose(verbose)

        self.__atomNumberDict = atomNumberDict

        self.distRestraints = 0      # GROMACS: Distance restraints
        self.angRestraints = 0       # GROMACS: Angle restraints
        self.dihedRestraints = 0     # GROMACS: Dihedral angle restraints
        self.rdcRestraints = 0       # GROMACS: Residual dipolar coupling restraints
        self.geoRestraints = 0       # GROMACS: Coordinate geometry restraints

        self.sfDict = {}

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

    # Enter a parse tree produced by GromacsMRParser#gromacs_mr.
    def enterGromacs_mr(self, ctx: GromacsMRParser.Gromacs_mrContext):  # pylint: disable=unused-argument
        self.__polySeqRst = []
        self.__f = []

    # Exit a parse tree produced by GromacsMRParser#gromacs_mr.
    def exitGromacs_mr(self, ctx: GromacsMRParser.Gromacs_mrContext):  # pylint: disable=unused-argument

        try:

            if self.__hasPolySeq and self.__polySeqRst is not None:
                sortPolySeqRst(self.__polySeqRst)

                self.__seqAlign, _ = alignPolymerSequence(self.__pA, self.__polySeq, self.__polySeqRst)
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

                            self.__seqAlign, _ = alignPolymerSequence(self.__pA, self.__polySeq, self.__polySeqRst)
                            self.__chainAssign, _ = assignPolymerSequence(self.__pA, self.__ccU, self.__file_type, self.__polySeq, self.__polySeqRst, self.__seqAlign)

                    trimSequenceAlignment(self.__seqAlign, self.__chainAssign)

        finally:
            self.warningMessage = sorted(list(set(self.__f)), key=self.__f.index)

    # Enter a parse tree produced by GromacsMRParser#distance_restraints.
    def enterDistance_restraints(self, ctx: GromacsMRParser.Distance_restraintsContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'dist'

    # Exit a parse tree produced by GromacsMRParser#distance_restraints.
    def exitDistance_restraints(self, ctx: GromacsMRParser.Distance_restraintsContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by GromacsMRParser#distance_restraint.
    def enterDistance_restraint(self, ctx: GromacsMRParser.Distance_restraintContext):  # pylint: disable=unused-argument
        self.distRestraints += 1

        self.atomSelectionSet.clear()

    # Exit a parse tree produced by GromacsMRParser#distance_restraint.
    def exitDistance_restraint(self, ctx: GromacsMRParser.Distance_restraintContext):

        def get_eff_digits(val):
            eff_digits = 0
            if '.' in val and val[-1] == '0':
                period = val.index('.')
                last = len(val) - 1
                while val[last] == '0':
                    last -= 1
                eff_digits = last - period
            return max(eff_digits, 0)

        try:

            if len(self.numberSelection) == 0 or None in self.numberSelection:
                return

            ai = int(str(ctx.Integer(0)))
            aj = int(str(ctx.Integer(1)))
            funct = int(str(ctx.Integer(2)))
            index = int(str(ctx.Integer(3)))

            lower_limit = self.numberSelection[0]
            upper_limit = self.numberSelection[1]
            upper_linear_limit = self.numberSelection[2]
            weight = self.numberSelection[3]

            if lower_limit is not None:
                eff_digits = get_eff_digits(str(lower_limit))
                lower_limit = round(lower_limit * 10.0, eff_digits)
            if upper_limit is not None:
                eff_digits = get_eff_digits(str(upper_limit))
                upper_limit = round(upper_limit * 10.0, eff_digits)
            if upper_linear_limit is not None:
                eff_digits = get_eff_digits(str(upper_linear_limit))
                upper_linear_limit = round(upper_linear_limit * 10.0, eff_digits)

            if funct != 1:
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint(n=index)}"
                                f"Unknown function type '{funct}' is set.")
                return

            if weight < 0.0:
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint(n=index)}"
                                f"The relative weight value of '{weight}' must not be a negative value.")
                return
            if weight == 0.0:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint(n=index)}"
                                f"The relative weight value of '{weight}' should be a positive value.")

            dstFunc = self.validateDistanceRange(index, weight, lower_limit, upper_limit, upper_linear_limit, self.__omitDistLimitOutlier)

            if dstFunc is None:
                return

            if not self.__hasPolySeq and not self.__hasNonPolySeq:
                return

            if self.__atomNumberDict is None:
                self.__f.append(f"[Missing data] {self.__getCurrentRestraint(n=index)}"
                                "Failed to recognize GROMACS atom numbers in the restraint file "
                                "because GROMACS parameter/topology file is not available.")
                return

            atomSelection = []

            if ai in self.__atomNumberDict:
                atomSelection.append(copy.copy(self.__atomNumberDict[ai]))
                self.atomSelectionSet.append(atomSelection)
            else:
                self.__f.append(f"[Missing data] {self.__getCurrentRestraint(n=index)}"
                                f"'ai={ai}' is not defined in the GROMACS parameter/topology file.")

            atomSelection = []

            if aj in self.__atomNumberDict:
                atomSelection.append(copy.copy(self.__atomNumberDict[aj]))
                self.atomSelectionSet.append(atomSelection)
            else:
                self.__f.append(f"[Missing data] {self.__getCurrentRestraint(n=index)}"
                                f"'aj={aj}' is not defined in the GROMACS parameter/topology file.")

            if len(self.atomSelectionSet) < 2:
                return

            memberId = '.'
            if self.__createSfDict:
                sf = self.__getSf(constraintType=getDistConstraintType(self.atomSelectionSet, dstFunc,
                                                                       self.__csStat, self.__originalFileName),
                                  potentialType=getPotentialType(self.__file_type, self.__cur_subtype, dstFunc))
                sf['id'] += 1
                memberLogicCode = 'OR' if len(self.atomSelectionSet[0]) * len(self.atomSelectionSet[1]) > 1 else '.'

                if memberLogicCode == 'OR':
                    if len(self.atomSelectionSet[0]) * len(self.atomSelectionSet[1]) > 1\
                       and (isAmbigAtomSelection(self.atomSelectionSet[0], self.__csStat)
                            or isAmbigAtomSelection(self.atomSelectionSet[1], self.__csStat)):
                        memberId = 0
                        _atom1 = _atom2 = None

            updatePolySeqRstFromAtomSelectionSet(self.__polySeqRst, self.atomSelectionSet)

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
                    print(f"subtype={self.__cur_subtype} id={self.distRestraints} (index={index}) "
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

        except ValueError:
            self.distRestraints -= 1

        finally:
            self.numberSelection.clear()

    def validateDistanceRange(self, index: int, weight: float,
                              lower_limit: Optional[float], upper_limit: Optional[float],
                              upper_linear_limit: Optional[float], omit_dist_limit_outlier: bool) -> Optional[dict]:
        """ Validate distance value range.
        """

        validRange = True
        dstFunc = {'weight': weight}

        if lower_limit is not None:
            if DIST_ERROR_MIN <= lower_limit < DIST_ERROR_MAX:
                dstFunc['lower_limit'] = f"{lower_limit}"
            else:
                if lower_limit <= DIST_ERROR_MIN and omit_dist_limit_outlier:
                    self.__f.append(f"[Range value warning] {self.__getCurrentRestraint(n=index)}"
                                    f"The lower limit value='{lower_limit}' is omitted because it is not within range {DIST_RESTRAINT_ERROR}.")
                    lower_limit = None
                else:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint(n=index)}"
                                    f"The lower limit value='{lower_limit}' must be within range {DIST_RESTRAINT_ERROR}.")

        if upper_limit is not None:
            if DIST_ERROR_MIN < upper_limit <= DIST_ERROR_MAX:
                dstFunc['upper_limit'] = f"{upper_limit}"
            else:
                if (upper_limit <= DIST_ERROR_MIN or upper_limit > DIST_ERROR_MAX) and omit_dist_limit_outlier:
                    self.__f.append(f"[Range value warning] {self.__getCurrentRestraint(n=index)}"
                                    f"The upper limit value='{upper_limit}' is omitted because it is not within range {DIST_RESTRAINT_ERROR}.")
                    upper_limit = None
                else:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint(n=index)}"
                                    f"The upper limit value='{upper_limit}' must be within range {DIST_RESTRAINT_ERROR}.")

        if upper_linear_limit is not None:
            if DIST_ERROR_MIN < upper_linear_limit <= DIST_ERROR_MAX:
                dstFunc['upper_linear_limit'] = f"{upper_linear_limit}"
            else:
                if (upper_linear_limit <= DIST_ERROR_MIN or upper_linear_limit > DIST_ERROR_MAX) and omit_dist_limit_outlier:
                    self.__f.append(f"[Range value warning] {self.__getCurrentRestraint(n=index)}"
                                    f"The upper linear limit value='{upper_linear_limit}' is omitted because it is not within range {DIST_RESTRAINT_ERROR}.")
                    upper_linear_limit = None
                else:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint(n=index)}"
                                    f"The upper linear limit value='{upper_linear_limit}' must be within range {DIST_RESTRAINT_ERROR}.")

        if None not in (upper_limit, upper_linear_limit):
            if upper_limit > upper_linear_limit:
                validRange = False
                self.__f.append(f"[Range value error] {self.__getCurrentRestraint(n=index)}"
                                f"The upper limit value='{upper_limit}' must be less than the upper linear limit value '{upper_linear_limit}'.")

        if not validRange:
            return None

        if lower_limit is not None:
            if DIST_RANGE_MIN <= lower_limit <= DIST_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint(n=index)}"
                                f"The lower limit value='{lower_limit}' should be within range {DIST_RESTRAINT_RANGE}.")

        if upper_limit is not None:
            if DIST_RANGE_MIN <= upper_limit <= DIST_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint(n=index)}"
                                f"The upper limit value='{upper_limit}' should be within range {DIST_RESTRAINT_RANGE}.")

        if upper_linear_limit is not None:
            if DIST_RANGE_MIN <= upper_linear_limit <= DIST_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint(n=index)}"
                                f"The upper linear limit value='{upper_linear_limit}' should be within range {DIST_RESTRAINT_RANGE}.")

        if lower_limit is None and upper_limit is None and upper_linear_limit is None:
            return None

        return dstFunc

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

    # Enter a parse tree produced by GromacsMRParser#dihedral_restraints.
    def enterDihedral_restraints(self, ctx: GromacsMRParser.Dihedral_restraintsContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'dihed'

    # Exit a parse tree produced by GromacsMRParser#dihedral_restraints.
    def exitDihedral_restraints(self, ctx: GromacsMRParser.Dihedral_restraintsContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by GromacsMRParser#dihedral_restraint.
    def enterDihedral_restraint(self, ctx: GromacsMRParser.Dihedral_restraintContext):  # pylint: disable=unused-argument
        self.dihedRestraints += 1

        self.atomSelectionSet.clear()

    # Exit a parse tree produced by GromacsMRParser#dihedral_restraint.
    def exitDihedral_restraint(self, ctx: GromacsMRParser.Dihedral_restraintContext):  # pylint: disable=unused-argument

        try:

            if len(self.numberSelection) == 0 or None in self.numberSelection:
                return

            ai = int(str(ctx.Integer(0)))
            aj = int(str(ctx.Integer(1)))
            ak = int(str(ctx.Integer(2)))
            al = int(str(ctx.Integer(3)))
            funct = int(str(ctx.Integer(4)))

            target_value = self.numberSelection[0]
            delta = self.numberSelection[1]
            weight = self.numberSelection[2]

            if delta > 0.0:
                lower_limit = target_value - delta
                upper_limit = target_value + delta
            else:
                lower_limit = upper_limit = None

            if funct != 1:
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                f"Unknown function type '{funct}' is set.")
                return

            if weight < 0.0:
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                f"The relative weight value of '{weight}' must not be a negative value.")
                return
            if weight == 0.0:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                f"The relative weight value of '{weight}' should be a positive value.")

            dstFunc = self.validateAngleRange(weight, target_value, lower_limit, upper_limit)

            if dstFunc is None:
                return

            if not self.__hasPolySeq and not self.__hasNonPolySeq:
                return

            if self.__atomNumberDict is None:
                self.__f.append(f"[Missing data] {self.__getCurrentRestraint()}"
                                "Failed to recognize GROMACS atom numbers in the restraint file "
                                "because GROMACS parameter/topology file is not available.")
                return

            atomSelection = []

            if ai in self.__atomNumberDict:
                atomSelection.append(copy.copy(self.__atomNumberDict[ai]))
                self.atomSelectionSet.append(atomSelection)
            else:
                self.__f.append(f"[Missing data] {self.__getCurrentRestraint()}"
                                f"'ai={ai}' is not defined in the GROMACS parameter/topology file.")

            atomSelection = []

            if aj in self.__atomNumberDict:
                atomSelection.append(copy.copy(self.__atomNumberDict[aj]))
                self.atomSelectionSet.append(atomSelection)
            else:
                self.__f.append(f"[Missing data] {self.__getCurrentRestraint()}"
                                f"'aj={aj}' is not defined in the GROMACS parameter/topology file.")

            atomSelection = []

            if ak in self.__atomNumberDict:
                atomSelection.append(copy.copy(self.__atomNumberDict[ak]))
                self.atomSelectionSet.append(atomSelection)
            else:
                self.__f.append(f"[Missing data] {self.__getCurrentRestraint()}"
                                f"'ak={ak}' is not defined in the GROMACS parameter/topology file.")

            atomSelection = []

            if al in self.__atomNumberDict:
                atomSelection.append(copy.copy(self.__atomNumberDict[al]))
                self.atomSelectionSet.append(atomSelection)
            else:
                self.__f.append(f"[Missing data] {self.__getCurrentRestraint()}"
                                f"'al={al}' is not defined in the GROMACS parameter/topology file.")

            if len(self.atomSelectionSet) < 4:
                return

            sf = None
            if self.__createSfDict:
                sf = self.__getSf(potentialType=getPotentialType(self.__file_type, self.__cur_subtype, dstFunc))

            updatePolySeqRstFromAtomSelectionSet(self.__polySeqRst, self.atomSelectionSet)

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
                                                                                       self.__getCurrentRestraint())
                    self.__f.append(err)

                if angleName in emptyValue and atomSelTotal != 4:
                    continue

                if peptide and angleName == 'CHI2' and atom4['atom_id'] == 'CD1' and isLikePheOrTyr(atom2['comp_id'], self.__ccU):
                    dstFunc = self.selectRealisticChi2AngleConstraint(atom1, atom2, atom3, atom4,
                                                                      dstFunc)
                if self.__debug:
                    print(f"subtype={self.__cur_subtype} id={self.dihedRestraints} angleName={angleName} "
                          f"atom1={atom1} atom2={atom2} atom3={atom3} atom4={atom4} {dstFunc}")
                if self.__createSfDict and sf is not None:
                    if first_item:
                        sf['id'] += 1
                        first_item = False
                    sf['index_id'] += 1
                    row = getRow(self.__cur_subtype, sf['id'], sf['index_id'],
                                 '.', None, angleName,
                                 sf['list_id'], self.__entryId, dstFunc,
                                 self.__authToStarSeq, self.__authToOrigSeq, self.__authToInsCode, self.__offsetHolder,
                                 atom1, atom2, atom3, atom4)
                    sf['loop'].add_data(row)

        except ValueError:
            self.dihedRestraints -= 1

        finally:
            self.numberSelection.clear()

    def validateAngleRange(self, weight: float, target_value: Optional[float],
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
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
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
                self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                f"The target value='{target_value}' must be within range {ANGLE_RESTRAINT_ERROR}.")

        if lower_limit is not None:
            if ANGLE_ERROR_MIN <= lower_limit < ANGLE_ERROR_MAX:
                dstFunc['lower_limit'] = f"{lower_limit}"
            else:
                validRange = False
                self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                f"The lower limit value='{lower_limit}' must be within range {ANGLE_RESTRAINT_ERROR}.")

        if upper_limit is not None:
            if ANGLE_ERROR_MIN < upper_limit <= ANGLE_ERROR_MAX:
                dstFunc['upper_limit'] = f"{upper_limit}"
            else:
                validRange = False
                self.__f.append(f"[Range value error] {self.__getCurrentRestraint()}"
                                f"The upper limit value='{upper_limit}' must be within range {ANGLE_RESTRAINT_ERROR}.")

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
                                f"The lower limit value='{lower_limit}' should be within range {ANGLE_RESTRAINT_RANGE}.")

        if upper_limit is not None:
            if ANGLE_RANGE_MIN <= upper_limit <= ANGLE_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint()}"
                                f"The upper limit value='{upper_limit}' should be within range {ANGLE_RESTRAINT_RANGE}.")

        if target_value is None and lower_limit is None and upper_limit is None:
            return None

        if None not in (upper_limit, lower_limit)\
           and (PLANE_LIKE_LOWER_LIMIT <= lower_limit < 0.0 < upper_limit <= PLANE_LIKE_UPPER_LIMIT
                or PLANE_LIKE_LOWER_LIMIT <= lower_limit - 180.0 < 0.0 < upper_limit - 180.0 <= PLANE_LIKE_UPPER_LIMIT
                or PLANE_LIKE_LOWER_LIMIT <= lower_limit - 360.0 < 0.0 < upper_limit - 360.0 <= PLANE_LIKE_UPPER_LIMIT):
            dstFunc['plane_like'] = True

        return dstFunc

    # Enter a parse tree produced by GromacsMRParser#orientation_restraints.
    def enterOrientation_restraints(self, ctx: GromacsMRParser.Orientation_restraintsContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'rdc'

    # Exit a parse tree produced by GromacsMRParser#orientation_restraints.
    def exitOrientation_restraints(self, ctx: GromacsMRParser.Orientation_restraintsContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by GromacsMRParser#orientation_restraint.
    def enterOrientation_restraint(self, ctx: GromacsMRParser.Orientation_restraintContext):  # pylint: disable=unused-argument
        self.rdcRestraints += 1

        self.atomSelectionSet.clear()

    # Exit a parse tree produced by GromacsMRParser#orientation_restraint.
    def exitOrientation_restraint(self, ctx: GromacsMRParser.Orientation_restraintContext):

        try:

            if len(self.numberSelection) == 0 or None in self.numberSelection:
                return

            ai = int(str(ctx.Integer(0)))
            aj = int(str(ctx.Integer(1)))
            funct = int(str(ctx.Integer(2)))
            exp = int(str(ctx.Integer(3)))
            index = int(str(ctx.Integer(4)))

            alpha = self.numberSelection[0]
            # const = self.numberSelection[1]
            target_value = self.numberSelection[2]
            weight = self.numberSelection[3]

            if ai == aj:
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint(dataset=exp, n=index)}"
                                f"Found zero RDC vector; (ai={ai}, aj={aj}).")
                return

            if funct != 1:
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint(dataset=exp, n=index)}"
                                f"Unknown function type '{funct}' is set.")
                return

            if alpha != 3.0:
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint(dataset=exp, n=index)}"
                                f"The 'alpha={alpha}' must be 3.0 for RDC restraints.")
                return

            if weight < 0.0:
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint(dataset=exp, n=index)}"
                                f"The relative weight value of '{weight}' must not be a negative value.")
                return
            if weight == 0.0:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint(dataset=exp, n=index)}"
                                f"The relative weight value of '{weight}' should be a positive value.")

            dstFunc = self.validateRdcRange(weight, exp, index, target_value, None, None)

            if dstFunc is None:
                return

            if not self.__hasPolySeq and not self.__hasNonPolySeq:
                return

            if self.__atomNumberDict is None:
                self.__f.append(f"[Missing data] {self.__getCurrentRestraint(dataset=exp, n=index)}"
                                "Failed to recognize GROMACS atom numbers in the restraint file "
                                "because GROMACS parameter/topology file is not available.")
                return

            atomSelection = []

            if ai in self.__atomNumberDict:
                atomSelection.append(copy.copy(self.__atomNumberDict[ai]))
                self.atomSelectionSet.append(atomSelection)
            else:
                self.__f.append(f"[Missing data] {self.__getCurrentRestraint(dataset=exp, n=index)}"
                                f"'ai={ai}' is not defined in the GROMACS parameter/topology file.")

            atomSelection = []

            if aj in self.__atomNumberDict:
                atomSelection.append(copy.copy(self.__atomNumberDict[aj]))
                self.atomSelectionSet.append(atomSelection)
            else:
                self.__f.append(f"[Missing data] {self.__getCurrentRestraint(dataset=exp, n=index)}"
                                f"'aj={aj}' is not defined in the GROMACS parameter/topology file.")

            if len(self.atomSelectionSet) < 2:
                return

            chain_id_1 = self.atomSelectionSet[0][0]['chain_id']
            seq_id_1 = self.atomSelectionSet[0][0]['seq_id']
            comp_id_1 = self.atomSelectionSet[0][0]['comp_id']
            atom_id_1 = self.atomSelectionSet[0][0].get('atom_id', None)
            if atom_id_1 is None:
                atom_id_1 = self.atomSelectionSet[0][0]['atom_id'] = self.atomSelectionSet[0][0]['auth_atom_id']

            chain_id_2 = self.atomSelectionSet[1][0]['chain_id']
            seq_id_2 = self.atomSelectionSet[1][0]['seq_id']
            comp_id_2 = self.atomSelectionSet[1][0]['comp_id']
            atom_id_2 = self.atomSelectionSet[1][0].get('atom_id', None)
            if atom_id_2 is None:
                atom_id_2 = self.atomSelectionSet[1][0]['atom_id'] = self.atomSelectionSet[1][0]['auth_atom_id']

            if (atom_id_1[0] not in ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS) or (atom_id_2[0] not in ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS):
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint(dataset=exp, n=index)}"
                                "Non-magnetic susceptible spin appears in RDC vector; "
                                f"({chain_id_1}:{seq_id_1}:{comp_id_1}:{atom_id_1}, "
                                f"{chain_id_2}:{seq_id_2}:{comp_id_2}:{atom_id_2}).")
                return

            if chain_id_1 != chain_id_2:
                ps1 = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == chain_id_1 and 'identical_auth_chain_id' in ps), None)
                ps2 = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == chain_id_2 and 'identical_auth_chain_id' in ps), None)
                if ps1 is None and ps2 is None:
                    self.__f.append(f"[Anomalous RDC vector] {self.__getCurrentRestraint(dataset=exp, n=index)}"
                                    "Found inter-chain RDC vector; "
                                    f"({chain_id_1}:{seq_id_1}:{comp_id_1}:{atom_id_1}, {chain_id_2}:{seq_id_2}:{comp_id_2}:{atom_id_2}).")
                    return

            elif abs(seq_id_1 - seq_id_2) > 1:
                ps1 = next((ps for ps in self.__polySeq if ps['auth_chain_id'] == chain_id_1 and 'gap_in_auth_seq' in ps and ps['gap_in_auth_seq']), None)
                if ps1 is None:
                    self.__f.append(f"[Anomalous RDC vector] {self.__getCurrentRestraint(dataset=exp, n=index)}"
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
                    self.__f.append(f"[Anomalous RDC vector] {self.__getCurrentRestraint(dataset=exp, n=index)}"
                                    "Found inter-residue RDC vector; "
                                    f"({chain_id_1}:{seq_id_1}:{comp_id_1}:{atom_id_1}, {chain_id_2}:{seq_id_2}:{comp_id_2}:{atom_id_2}).")
                    return

            elif atom_id_1 == atom_id_2:
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint(dataset=exp, n=index)}"
                                "Found zero RDC vector; "
                                f"({chain_id_1}:{seq_id_1}:{comp_id_1}:{atom_id_1}, {chain_id_2}:{seq_id_2}:{comp_id_2}:{atom_id_2}).")
                return

            elif self.__ccU.updateChemCompDict(comp_id_1):  # matches with comp_id in CCD

                if not self.__ccU.hasBond(comp_id_1, atom_id_1, atom_id_2):

                    if self.__nefT.validate_comp_atom(comp_id_1, atom_id_1) and self.__nefT.validate_comp_atom(comp_id_2, atom_id_2):
                        self.__f.append(f"[Anomalous RDC vector] {self.__getCurrentRestraint(dataset=exp, n=index)}"
                                        "Found an RDC vector over multiple covalent bonds; "
                                        f"({chain_id_1}:{seq_id_1}:{comp_id_1}:{atom_id_1}, {chain_id_2}:{seq_id_2}:{comp_id_2}:{atom_id_2}).")

            if self.__createSfDict:
                sf = self.__getSf(potentialType=getPotentialType(self.__file_type, self.__cur_subtype, dstFunc),
                                  rdcCode=getRdcCode([self.atomSelectionSet[0][0], self.atomSelectionSet[1][0]]))
                sf['id'] += 1

            updatePolySeqRstFromAtomSelectionSet(self.__polySeqRst, self.atomSelectionSet)

            for atom1, atom2 in itertools.product(self.atomSelectionSet[0],
                                                  self.atomSelectionSet[1]):
                atoms = [atom1, atom2]
                if isIdenticalRestraint(atoms, self.__nefT):
                    continue
                if isLongRangeRestraint(atoms, self.__polySeq if self.__gapInAuthSeq else None):
                    continue
                if self.__debug:
                    print(f"subtype={self.__cur_subtype} id={self.rdcRestraints} exp={exp} index={index} "
                          f"atom1={atom1} atom2={atom2} {dstFunc}")
                if self.__createSfDict and sf is not None:
                    sf['index_id'] += 1
                    row = getRow(self.__cur_subtype, sf['id'], sf['index_id'],
                                 '.', None, None,
                                 sf['list_id'], self.__entryId, dstFunc,
                                 self.__authToStarSeq, self.__authToOrigSeq, self.__authToInsCode, self.__offsetHolder,
                                 atom1, atom2)
                    sf['loop'].add_data(row)

        except ValueError:
            self.rdcRestraints -= 1

        finally:
            self.numberSelection.clear()

    def validateRdcRange(self, exp: int, index: int, weight: float, target_value: Optional[float],
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
                self.__f.append(f"[Range value error] {self.__getCurrentRestraint(dataset=exp, n=index)}"
                                f"The target value='{target_value}' must be within range {RDC_RESTRAINT_ERROR}.")

        if lower_limit is not None:
            if RDC_ERROR_MIN <= lower_limit < RDC_ERROR_MAX:
                dstFunc['lower_limit'] = f"{lower_limit:.6f}"
            else:
                validRange = False
                self.__f.append(f"[Range value error] {self.__getCurrentRestraint(dataset=exp, n=index)}"
                                f"The lower limit value='{lower_limit:.6f}' must be within range {RDC_RESTRAINT_ERROR}.")

        if upper_limit is not None:
            if RDC_ERROR_MIN < upper_limit <= RDC_ERROR_MAX:
                dstFunc['upper_limit'] = f"{upper_limit:.6f}"
            else:
                validRange = False
                self.__f.append(f"[Range value error] {self.__getCurrentRestraint(dataset=exp, n=index)}"
                                f"The upper limit value='{upper_limit:.6f}' must be within range {RDC_RESTRAINT_ERROR}.")

        if target_value is not None:

            if lower_limit is not None:
                if lower_limit > target_value:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint(dataset=exp, n=index)}"
                                    f"The lower limit value='{lower_limit:.6f}' must be less than the target value '{target_value}'.")

            if upper_limit is not None:
                if upper_limit < target_value:
                    validRange = False
                    self.__f.append(f"[Range value error] {self.__getCurrentRestraint(dataset=exp, n=index)}"
                                    f"The upper limit value='{upper_limit:.6f}' must be greater than the target value '{target_value}'.")

        if not validRange:
            return None

        if target_value is not None:
            if RDC_RANGE_MIN <= target_value <= RDC_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint(dataset=exp, n=index)}"
                                f"The target value='{target_value}' should be within range {RDC_RESTRAINT_RANGE}.")

        if lower_limit is not None:
            if RDC_RANGE_MIN <= lower_limit <= RDC_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint(dataset=exp, n=index)}"
                                f"The lower limit value='{lower_limit:.6f}' should be within range {RDC_RESTRAINT_RANGE}.")

        if upper_limit is not None:
            if RDC_RANGE_MIN <= upper_limit <= RDC_RANGE_MAX:
                pass
            else:
                self.__f.append(f"[Range value warning] {self.__getCurrentRestraint(dataset=exp, n=index)}"
                                f"The upper limit value='{upper_limit:.6f}' should be within range {RDC_RESTRAINT_RANGE}.")

        if target_value is None and lower_limit is None and upper_limit is None:
            return None

        return dstFunc

    # Enter a parse tree produced by GromacsMRParser#angle_restraints.
    def enterAngle_restraints(self, ctx: GromacsMRParser.Angle_restraintsContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'ang'

    # Exit a parse tree produced by GromacsMRParser#angle_restraints.
    def exitAngle_restraints(self, ctx: GromacsMRParser.Angle_restraintsContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by GromacsMRParser#angle_restraint.
    def enterAngle_restraint(self, ctx: GromacsMRParser.Angle_restraintContext):  # pylint: disable=unused-argument
        self.angRestraints += 1

        self.atomSelectionSet.clear()

    # Exit a parse tree produced by GromacsMRParser#angle_restraint.
    def exitAngle_restraint(self, ctx: GromacsMRParser.Angle_restraintContext):  # pylint: disable=unused-argument

        try:

            if len(self.numberSelection) == 0 or None in self.numberSelection:
                return

            ai = int(str(ctx.Integer(0)))
            aj = int(str(ctx.Integer(1)))
            ak = int(str(ctx.Integer(2)))
            al = int(str(ctx.Integer(3)))
            funct = int(str(ctx.Integer(4)))
            mult = int(str(ctx.Integer(5)))

            target_value = self.numberSelection[0]
            delta = self.numberSelection[1]
            weight = 1.0

            if delta > 0.0:
                lower_limit = target_value - delta
                upper_limit = target_value + delta
            else:
                lower_limit = upper_limit = None

            len_atom_sorts = len(set(ai, aj, ak, al))

            if len_atom_sorts < 3 or ai == aj or ak == al:
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                f"Found zero angle vector; (ai={ai}, aj={aj}) - (ak={ak}, al={al}).")
                return

            if funct != 1:
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                f"Unknown function type '{funct}' is set.")
                return

            if mult <= 0:
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                f"The multiplicity of angle restraint '{mult}' must be a positive integer.")
                return

            dstFunc = self.validateAngleRange(weight, target_value, lower_limit, upper_limit)

            if dstFunc is None:
                return

            if not self.__hasPolySeq and not self.__hasNonPolySeq:
                return

            if self.__atomNumberDict is None:
                self.__f.append(f"[Missing data] {self.__getCurrentRestraint()}"
                                "Failed to recognize GROMACS atom numbers in the restraint file "
                                "because GROMACS parameter/topology file is not available.")
                return

            atomSelection = []

            if ai in self.__atomNumberDict:
                atomSelection.append(copy.copy(self.__atomNumberDict[ai]))
                self.atomSelectionSet.append(atomSelection)
            else:
                self.__f.append(f"[Missing data] {self.__getCurrentRestraint()}"
                                f"'ai={ai}' is not defined in the GROMACS parameter/topology file.")

            atomSelection = []

            if aj in self.__atomNumberDict:
                atomSelection.append(copy.copy(self.__atomNumberDict[aj]))
                self.atomSelectionSet.append(atomSelection)
            else:
                self.__f.append(f"[Missing data] {self.__getCurrentRestraint()}"
                                f"'aj={aj}' is not defined in the GROMACS parameter/topology file.")

            atomSelection = []

            if ak in self.__atomNumberDict:
                atomSelection.append(copy.copy(self.__atomNumberDict[ak]))
                self.atomSelectionSet.append(atomSelection)
            else:
                self.__f.append(f"[Missing data] {self.__getCurrentRestraint()}"
                                f"'ak={ak}' is not defined in the GROMACS parameter/topology file.")

            atomSelection = []

            if al in self.__atomNumberDict:
                atomSelection.append(copy.copy(self.__atomNumberDict[al]))
                self.atomSelectionSet.append(atomSelection)
            else:
                self.__f.append(f"[Missing data] {self.__getCurrentRestraint()}"
                                f"'al={al}' is not defined in the GROMACS parameter/topology file.")

            if len(self.atomSelectionSet) < 4:
                return

            if self.__createSfDict:
                sf = self.__getSf('angle restraint' if len_atom_sorts == 3 else 'angle restraint (intervector projection angle)')
                sf['id'] += 1
                if len(sf['loop']['tags']) == 0:
                    if len_atom_sorts == 3:
                        sf['loop']['tags'] = ['index_id', 'id',
                                              'auth_asym_id_1', 'auth_seq_id_1', 'auth_comp_id_1', 'auth_atom_id_1',
                                              'auth_asym_id_2', 'auth_seq_id_2', 'auth_comp_id_2', 'auth_atom_id_2',
                                              'auth_asym_id_3', 'auth_seq_id_3', 'auth_comp_id_3', 'auth_atom_id_3',
                                              'target_value', 'target_value_uncertainty',
                                              'lower_linear_limit', 'lower_limit', 'upper_limit', 'upper_linear_limit',
                                              'multiplicity',
                                              'list_id']
                    else:
                        sf['loop']['tags'] = ['index_id', 'id',
                                              'auth_asym_id_1', 'auth_seq_id_1', 'auth_comp_id_1', 'auth_atom_id_1',
                                              'auth_asym_id_2', 'auth_seq_id_2', 'auth_comp_id_2', 'auth_atom_id_2',
                                              'auth_asym_id_3', 'auth_seq_id_3', 'auth_comp_id_3', 'auth_atom_id_3',
                                              'auth_asym_id_4', 'auth_seq_id_4', 'auth_comp_id_4', 'auth_atom_id_4',
                                              'target_value', 'target_value_uncertainty',
                                              'lower_linear_limit', 'lower_limit', 'upper_limit', 'upper_linear_limit',
                                              'multiplicity',
                                              'list_id']

            updatePolySeqRstFromAtomSelectionSet(self.__polySeqRst, self.atomSelectionSet)

            if len_atom_sorts == 3:
                if ai in (ak, al):
                    if ai == ak:
                        atom_order = [1, 0, 3]
                    else:
                        atom_order = [1, 0, 2]
                else:
                    if aj == ak:
                        atom_order = [0, 1, 3]
                    else:
                        atom_order = [0, 1, 2]

                for atom1, atom2, atom3 in itertools.product(self.atomSelectionSet[atom_order[0]],
                                                             self.atomSelectionSet[atom_order[1]],
                                                             self.atomSelectionSet[atom_order[2]]):
                    if isLongRangeRestraint([atom1, atom2, atom3], self.__polySeq if self.__gapInAuthSeq else None):
                        continue
                    if self.__debug:
                        print(f"subtype={self.__cur_subtype} id={self.angRestraints} mult={mult} "
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
                                                   mult,
                                                   sf['list_id']])

            else:

                for atom1, atom2, atom3, atom4 in itertools.product(self.atomSelectionSet[0],
                                                                    self.atomSelectionSet[1],
                                                                    self.atomSelectionSet[2],
                                                                    self.atomSelectionSet[3]):
                    if isLongRangeRestraint([atom1, atom2, atom3, atom4], self.__polySeq if self.__gapInAuthSeq else None):
                        continue
                    if self.__debug:
                        print(f"subtype={self.__cur_subtype} id={self.angRestraints} mult={mult} "
                              f"atom1={atom1} atom2={atom2} atom3={atom3} atom4={atom4} {dstFunc}")
                    if self.__createSfDict and sf is not None:
                        sf['index_id'] += 1
                        sf['loop']['data'].append([sf['index_id'], sf['id'],
                                                   atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id'],
                                                   atom2['chain_id'], atom2['seq_id'], atom2['comp_id'], atom2['atom_id'],
                                                   atom3['chain_id'], atom3['seq_id'], atom3['comp_id'], atom3['atom_id'],
                                                   atom4['chain_id'], atom4['seq_id'], atom4['comp_id'], atom4['atom_id'],
                                                   dstFunc.get('target_value'), None,
                                                   dstFunc.get('lower_linear_limit'),
                                                   dstFunc.get('lower_limit'),
                                                   dstFunc.get('upper_limit'),
                                                   dstFunc.get('upper_linear_limit'),
                                                   mult,
                                                   sf['list_id']])

        except ValueError:
            self.angRestraints -= 1

        finally:
            self.numberSelection.clear()

    # Enter a parse tree produced by GromacsMRParser#angle_restraints_z.
    def enterAngle_restraints_z(self, ctx: GromacsMRParser.Angle_restraints_zContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'ang'

    # Exit a parse tree produced by GromacsMRParser#angle_restraints_z.
    def exitAngle_restraints_z(self, ctx: GromacsMRParser.Angle_restraints_zContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by GromacsMRParser#angle_restraint_z.
    def enterAngle_restraint_z(self, ctx: GromacsMRParser.Angle_restraint_zContext):  # pylint: disable=unused-argument
        self.angRestraints += 1

        self.atomSelectionSet.clear()

    # Exit a parse tree produced by GromacsMRParser#angle_restraint_z.
    def exitAngle_restraint_z(self, ctx: GromacsMRParser.Angle_restraint_zContext):

        try:

            if len(self.numberSelection) == 0 or None in self.numberSelection:
                return

            ai = int(str(ctx.Integer(0)))
            aj = int(str(ctx.Integer(1)))
            funct = int(str(ctx.Integer(2)))
            mult = int(str(ctx.Integer(3)))

            target_value = self.numberSelection[0]
            delta = self.numberSelection[1]
            weight = 1.0

            if delta > 0.0:
                lower_limit = target_value - delta
                upper_limit = target_value + delta
            else:
                lower_limit = upper_limit = None

            if ai == aj:
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                f"Found zero angle vector; (ai={ai}, aj={aj}).")
                return

            if funct != 1:
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                f"Unknown function type '{funct}' is set.")
                return

            if mult <= 0:
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                f"The multiplicity of angle restraint '{mult}' must be a positive integer.")
                return

            dstFunc = self.validateAngleRange(weight, target_value, lower_limit, upper_limit)

            if dstFunc is None:
                return

            if not self.__hasPolySeq and not self.__hasNonPolySeq:
                return

            if self.__atomNumberDict is None:
                self.__f.append(f"[Missing data] {self.__getCurrentRestraint()}"
                                "Failed to recognize GROMACS atom numbers in the restraint file "
                                "because GROMACS parameter/topology file is not available.")
                return

            atomSelection = []

            if ai in self.__atomNumberDict:
                atomSelection.append(copy.copy(self.__atomNumberDict[ai]))
                self.atomSelectionSet.append(atomSelection)
            else:
                self.__f.append(f"[Missing data] {self.__getCurrentRestraint()}"
                                f"'ai={ai}' is not defined in the GROMACS parameter/topology file.")

            atomSelection = []

            if aj in self.__atomNumberDict:
                atomSelection.append(copy.copy(self.__atomNumberDict[aj]))
                self.atomSelectionSet.append(atomSelection)
            else:
                self.__f.append(f"[Missing data] {self.__getCurrentRestraint()}"
                                f"'aj={aj}' is not defined in the GROMACS parameter/topology file.")

            if len(self.atomSelectionSet) < 2:
                return

            if self.__createSfDict:
                sf = self.__getSf('angle restraint (intervector projection angle with z-axis)')
                sf['id'] += 1
                if len(sf['loop']['tags']) == 0:
                    sf['loop']['tags'] = ['index_id', 'id',
                                          'auth_asym_id_1', 'auth_seq_id_1', 'auth_comp_id_1', 'auth_atom_id_1',
                                          'auth_asym_id_2', 'auth_seq_id_2', 'auth_comp_id_2', 'auth_atom_id_2',
                                          'target_value', 'target_value_uncertainty',
                                          'lower_linear_limit', 'lower_limit', 'upper_limit', 'upper_linear_limit',
                                          'multiplicity',
                                          'list_id']

            updatePolySeqRstFromAtomSelectionSet(self.__polySeqRst, self.atomSelectionSet)

            for atom1, atom2 in itertools.product(self.atomSelectionSet[0],
                                                  self.atomSelectionSet[1]):
                atoms = [atom1, atom2]
                if isIdenticalRestraint(atoms, self.__nefT):
                    continue
                if isLongRangeRestraint(atoms, self.__polySeq if self.__gapInAuthSeq else None):
                    continue
                if self.__debug:
                    print(f"subtype={self.__cur_subtype} id={self.angRestraints} mult={mult} "
                          f"atom1={atom1} atom2={atom2} z-axis {dstFunc}")
                if self.__createSfDict and sf is not None:
                    sf['index_id'] += 1
                    sf['loop']['data'].append([sf['index_id'], sf['id'],
                                               atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id'],
                                               atom2['chain_id'], atom2['seq_id'], atom2['comp_id'], atom2['atom_id'],
                                               dstFunc.get('target_value'), None,
                                               dstFunc.get('lower_linear_limit'),
                                               dstFunc.get('lower_limit'),
                                               dstFunc.get('upper_limit'),
                                               dstFunc.get('upper_linear_limit'),
                                               mult,
                                               sf['list_id']])

        except ValueError:
            self.angRestraints -= 1

        finally:
            self.numberSelection.clear()

    # Enter a parse tree produced by GromacsMRParser#position_restraints.
    def enterPosition_restraints(self, ctx: GromacsMRParser.Position_restraintsContext):  # pylint: disable=unused-argument
        self.__cur_subtype = 'geo'

    # Exit a parse tree produced by GromacsMRParser#position_restraints.
    def exitPosition_restraints(self, ctx: GromacsMRParser.Position_restraintsContext):  # pylint: disable=unused-argument
        pass

    # Enter a parse tree produced by GromacsMRParser#position_restraint.
    def enterPosition_restraint(self, ctx: GromacsMRParser.Position_restraintContext):  # pylint: disable=unused-argument
        self.geoRestraints += 1

        self.atomSelectionSet.clear()

    # Exit a parse tree produced by GromacsMRParser#position_restraint.
    def exitPosition_restraint(self, ctx: GromacsMRParser.Position_restraintContext):

        try:

            if len(self.numberSelection) == 0 or None in self.numberSelection:
                return

            ai = int(str(ctx.Integer(0)))
            funct = int(str(ctx.Integer(1)))

            a = self.numberSelection[0]
            b = self.numberSelection[1]
            c = self.numberSelection[2]

            if funct not in (1, 2):
                self.__f.append(f"[Invalid data] {self.__getCurrentRestraint()}"
                                f"Unknown function type '{funct}' is set.")
                return

            if not self.__hasPolySeq and not self.__hasNonPolySeq:
                return

            if self.__atomNumberDict is None:
                self.__f.append(f"[Missing data] {self.__getCurrentRestraint()}"
                                "Failed to recognize GROMACS atom numbers in the restraint file "
                                "because GROMACS parameter/topology file is not available.")
                return

            atomSelection = []

            if ai in self.__atomNumberDict:
                atomSelection.append(copy.copy(self.__atomNumberDict[ai]))
                self.atomSelectionSet.append(atomSelection)
            else:
                self.__f.append(f"[Missing data] {self.__getCurrentRestraint()}"
                                f"'ai={ai}' is not defined in the GROMACS parameter/topology file.")

            if len(self.atomSelectionSet) < 1:
                return

            if self.__createSfDict:
                sf = self.__getSf('harmonic coordinate restraint, GROMACS position restraint')
                sf['id'] += 1
                if len(sf['loop']['tags']) == 0:
                    if funct == 1:
                        sf['loop']['tags'] = ['index_id', 'id',
                                              'auth_asym_id', 'auth_seq_id', 'auth_comp_id', 'auth_atom_id',
                                              'kx', 'ky', 'kz',
                                              'list_id']
                    else:
                        sf['loop']['tags'] = ['index_id', 'id',
                                              'auth_asym_id', 'auth_seq_id', 'auth_comp_id', 'auth_atom_id',
                                              'g', 'r', 'k',
                                              'list_id']

            updatePolySeqRstFromAtomSelectionSet(self.__polySeqRst, self.atomSelectionSet)

            for atom1 in self.atomSelectionSet[0]:
                if self.__debug:
                    if funct == 1:
                        print(f"subtype={self.__cur_subtype} id={self.geoRestraints} "
                              f"atom={atom1} (kx, ky, kz)=({a}, {b}, {c})")
                    else:
                        print(f"subtype={self.__cur_subtype} id={self.geoRestraints} "
                              f"atom={atom1} (g, r, k)=({a}, {b}, {c})")
                if self.__createSfDict and sf is not None:
                    sf['index_id'] += 1
                    sf['loop']['data'].append([sf['index_id'], sf['id'],
                                               atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id'],
                                               a, b, c,
                                               sf['list_id']])

        except ValueError:
            self.geoRestraints -= 1

        finally:
            self.numberSelection.clear()

    # Enter a parse tree produced by GromacsMRParser#number.
    def enterNumber(self, ctx: GromacsMRParser.NumberContext):  # pylint: disable=unused-argument
        pass

    # Exit a parse tree produced by GromacsMRParser#number.
    def exitNumber(self, ctx: GromacsMRParser.NumberContext):
        if ctx.Float():
            self.numberSelection.append(float(str(ctx.Float())))

        elif ctx.Integer():
            self.numberSelection.append(float(str(ctx.Integer())))

        else:
            self.numberSelection.append(None)

    def __getCurrentRestraint(self, dataset: Optional[int] = None, n: Optional[int] = None) -> str:
        if self.__cur_subtype == 'dist':
            if n is None:
                return f"[Check the {self.distRestraints}th row of distance restraints, {self.__def_err_sf_framecode}] "
            return f"[Check the {self.distRestraints}th row of distance restraints (index={n}), {self.__def_err_sf_framecode}] "
        if self.__cur_subtype == 'ang':
            return f"[Check the {self.angRestraints}th row of angle restraints, {self.__def_err_sf_framecode}] "
        if self.__cur_subtype == 'dihed':
            return f"[Check the {self.dihedRestraints}th row of dihedral angle restraints, {self.__def_err_sf_framecode}] "
        if self.__cur_subtype == 'rdc':
            if dataset is None:
                return f"[Check the {n}th row of residual dipolar coupling restraints, {self.__def_err_sf_framecode}] "
            return f"[Check the {n}th row of residual dipolar coupling restraints (exp={dataset}), {self.__def_err_sf_framecode}] "
        if self.__cur_subtype == 'geo':
            return f"[Check the {self.geoRestraints}th row of coordinate geometry restraints, {self.__def_err_sf_framecode}] "
        return ''

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

        sf_framecode = 'GROMACS_' + restraint_name.replace(' ', '_') + f'_{list_id}'

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
        """ Return content subtype of GROMACS MR file.
        """

        contentSubtype = {'dist_restraint': self.distRestraints,
                          'ang_restraint': self.angRestraints,
                          'dihed_restraint': self.dihedRestraints,
                          'rdc_restraint': self.rdcRestraints,
                          'geo_restraint': self.geoRestraints
                          }

        return {k: 1 for k, v in contentSubtype.items() if v > 0}

    def getPolymerSequence(self) -> Optional[List[dict]]:
        """ Return polymer sequence of GROMACS MR file.
        """

        return None if self.__polySeqRst is None or len(self.__polySeqRst) == 0 else self.__polySeqRst

    def getSequenceAlignment(self) -> Optional[List[dict]]:
        """ Return sequence alignment between coordinates and GROMACS MR.
        """

        return None if self.__seqAlign is None or len(self.__seqAlign) == 0 else self.__seqAlign

    def getChainAssignment(self) -> Optional[List[dict]]:
        """ Return chain assignment between coordinates and GROMACS MR.
        """

        return None if self.__chainAssign is None or len(self.__chainAssign) == 0 else self.__chainAssign

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

# del GromacsMRParser
