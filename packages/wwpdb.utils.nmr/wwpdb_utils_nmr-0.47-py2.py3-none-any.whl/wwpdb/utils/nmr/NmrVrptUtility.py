##
# File: NmrVrptUtility.py
# Date: 19-Apr-2023
#
# Updates:
# 19-Jul-2023  M. Yokochi - add trustPdbxAuthAtomName() for OneDep validation package (DAOTHER-8705)
# 19-Jul-2023  M. Yokochi - fix distance/dihedral angle/RDC averaging when lower/upper bounds are different in a restraint (DAOTER-8705)
# 18-Dec-2023  M. Yokochi - retrieve non-leaving hydrogens independent of MolProbity (DAOTHER-8945)
# 20-Dec-2023  M. Yokochi - add support for case 'Member_logic_code' value equals 'AND'
# 21-Feb-2024  M. Yokochi - add support for discontinuous model_id (NMR restraint remediation, 2n6j)
# 28-Feb-2024  M. Yokochi - collect atom_ids dictionary for both auth_atom_id and pdbx_auth_atom_name tags
#                           to prevent MISSING ATOM IN MODEL KeyError in restraintsanalysis.py (DAOTHER-9200)
##
""" Wrapper class for NMR restraint analysis.
    @author: Masashi Yokochi
    @note: This class is alternative implementation of wwpdb.apps.validation.src.RestraintValidation.BMRBRestraintsAnalysis
"""
__docformat__ = "restructuredtext en"
__author__ = "Masashi Yokochi, Kumaran Baskaran"
__email__ = "yokochi@protein.osaka-u.ac.jp, baskaran@uchc.edu"
__license__ = "Apache License 2.0"
__version__ = "v1.2"

import os
import sys
import gzip
import tempfile
import time
import pickle
import copy
import numpy as np

from operator import itemgetter
from typing import Any, IO, List, Tuple, Optional

from mmcif.io.IoAdapterPy import IoAdapterPy

try:
    from wwpdb.utils.nmr.io.CifReader import (CifReader,
                                              LEN_MAJOR_ASYM_ID,
                                              calculate_uninstanced_coord,
                                              to_np_array)
    from wwpdb.utils.nmr.mr.ParserListenerUtil import (REPRESENTATIVE_MODEL_ID,
                                                       REPRESENTATIVE_ALT_ID,
                                                       DIST_RESTRAINT_ERROR,
                                                       ANGLE_RESTRAINT_ERROR,
                                                       RDC_RESTRAINT_ERROR,
                                                       coordAssemblyChecker,
                                                       getDistConstraintType)
    from wwpdb.utils.nmr.AlignUtil import (LARGE_ASYM_ID,
                                           emptyValue,
                                           monDict3,
                                           protonBeginCode)
    from wwpdb.utils.nmr.ChemCompUtil import ChemCompUtil
    from wwpdb.utils.nmr.BMRBChemShiftStat import BMRBChemShiftStat
except ImportError:
    from nmr.io.CifReader import (CifReader,
                                  LEN_MAJOR_ASYM_ID,
                                  calculate_uninstanced_coord,
                                  to_np_array)
    from nmr.mr.ParserListenerUtil import (REPRESENTATIVE_MODEL_ID,
                                           REPRESENTATIVE_ALT_ID,
                                           DIST_RESTRAINT_ERROR,
                                           ANGLE_RESTRAINT_ERROR,
                                           RDC_RESTRAINT_ERROR,
                                           coordAssemblyChecker,
                                           getDistConstraintType)
    from nmr.AlignUtil import (LARGE_ASYM_ID,
                               emptyValue,
                               monDict3,
                               protonBeginCode)
    from nmr.ChemCompUtil import ChemCompUtil
    from nmr.BMRBChemShiftStat import BMRBChemShiftStat


NMR_VTF_DIST_VIOL_CUTOFF = 0.1
NMR_VTF_DIHED_VIOL_CUTOFF = 1.0
NMR_VTF_RDC_VIOL_CUTOFF = 1.0  # to be decided

NMR_VTF_DIST_ERR_BINS = (0.1, 0.2, 0.5)
NMR_VTF_DIHED_ERR_BINS = (1.0, 10.0, 20.0)
NMR_VTF_RDC_ERR_BINS = (1.0, 2.0, 5.0)  # to be decided

DIST_ERROR_MAX = DIST_RESTRAINT_ERROR['max_exclusive']
ANGLE_ERROR_MAX = ANGLE_RESTRAINT_ERROR['max_exclusive']
RDC_ERROR_MAX = RDC_RESTRAINT_ERROR['max_exclusive']


def uncompress_gzip_file(inPath: str, outPath: str):
    """ Uncompress a given gzip file.
    """

    with gzip.open(inPath, mode='rt') as ifh, open(outPath, 'w') as ofh:
        for line in ifh:
            ofh.write(line)


def compress_as_gzip_file(inPath: str, outPath: str):
    """ Compress a given file as a gzip file.
    """

    with open(inPath, mode='r') as ifh, gzip.open(outPath, 'wt') as ofh:
        for line in ifh:
            ofh.write(line)


def load_from_pickle(file_name: str, default: Any = None) -> Any:
    """ Load object from pickle file.
    """

    if os.path.exists(file_name):

        try:

            with open(file_name, 'rb') as ifh:
                obj = pickle.load(ifh)
                return obj if obj is not None else default

        except Exception:
            try:
                os.remove(file_name)
            except OSError:
                pass

    return default


def write_as_pickle(obj: Any, file_name: str):
    """ Write a given object as pickle file.
    """

    if obj is not None:

        with open(file_name, 'wb') as ofh:
            pickle.dump(obj, ofh)


def distance(p0: list, p1: list) -> float:
    """ Return distance between two points.
    """

    return np.linalg.norm(p0 - p1)


def to_unit_vector(a: list) -> list:
    """ Return unit vector of a given vector.
    """

    return a / np.linalg.norm(a)


def dihedral_angle(p0: list, p1: list, p2: list, p3: list) -> float:
    """ Return dihedral angle from a series of four points.
    """

    b0 = -1.0 * (p1 - p0)
    b1 = p2 - p1
    b2 = p3 - p2

    # normalize b1 so that it does not influence magnitude of vector
    # rejections that come next
    b1 = to_unit_vector(b1)

    # vector rejections
    # v = projection of b0 onto plane perpendicular to b1
    #   = b0 minus component that aligns with b1
    # w = projection of b2 onto plane perpendicular to b1
    #   = b2 minus component that aligns with b1
    v = b0 - np.dot(b0, b1) * b1
    w = b2 - np.dot(b2, b1) * b1

    # angle between v and w in a plane is the torsion angle
    # v and w may not be normalized but that's fine since tan is y/x
    x = np.dot(v, w)
    y = np.dot(np.cross(b1, v), w)

    return np.degrees(np.arctan2(y, x))


def dist_inv_6_summed(r_list: List[float]) -> float:
    """ Return r^−6-summed distance for a given list of distances for ambiguous restraints as recommended by NMR VTF.
        Reference:
          Calculation of Protein Structures with Ambiguous Distance Restraints. Automated Assignment of
          Ambiguous NOE Crosspeaks and Disulphide Connectivities.
          Michael Nilges.
          J. Mol. Biol. (1995) 245, 645–660.
          DOI: 10.1006/jmbi.1994.0053
        @author: Kumaran Baskaran
        @see: wwpdb.apps.validation.src.RestraintValidation.BMRBRestraintsAnalysis.r6sum
    """

    if len(r_list) == 1:
        return r_list[0]

    return sum(r ** (-6.0) for r in r_list) ** (-1.0 / 6.0)


def dist_target_values(target_value: Optional[float], target_value_uncertainty: Optional[float],
                       lower_limit: Optional[float], upper_limit: Optional[float],
                       lower_linear_limit: Optional[float], upper_linear_limit: Optional[float]
                       ) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """ Return estimated distance target value, lower_bound, upper_bound.
        @author: Masashi Yokochi
    """

    lower_bound, upper_bound = lower_limit, upper_limit

    if lower_bound is None and upper_bound is None and lower_linear_limit is None and upper_linear_limit is None:
        if target_value is None:
            return None, lower_bound, upper_bound
        if target_value is not None:
            if target_value_uncertainty is not None:
                lower_bound = target_value - target_value_uncertainty
                upper_bound = target_value + target_value_uncertainty
            else:
                lower_bound = upper_bound = target_value

    if lower_bound is None and lower_linear_limit is not None:
        lower_bound = lower_linear_limit
    if upper_bound is None and upper_linear_limit is not None:
        upper_bound = upper_linear_limit

    if lower_bound is not None:
        lower_bound = max(lower_bound, 0.0)
    if upper_bound is not None:
        upper_bound = max(upper_bound, 0.0)

    if target_value is None:
        if None not in (lower_bound, upper_bound):
            target_value = (lower_bound + upper_bound) / 2.0
        elif lower_bound is not None:
            target_value = lower_bound
        elif upper_bound is not None:
            target_value = upper_bound

    return target_value, lower_bound, upper_bound


def dist_error(lower_bound: Optional[float], upper_bound: Optional[float], dist: Optional[float]) -> float:
    """ Return distance outlier for given lower_bound and upper_bound.
        @author: Masashi Yokochi
    """

    error = 0.0

    try:

        if None not in (lower_bound, upper_bound):
            if lower_bound <= dist <= upper_bound:
                pass
            elif dist > upper_bound:
                error = abs(dist - upper_bound)
            else:
                error = abs(dist - lower_bound)

        elif upper_bound is not None:
            if dist <= upper_bound:
                pass
            elif dist > upper_bound:
                error = abs(dist - upper_bound)

        elif lower_bound is not None:
            if lower_bound <= dist:
                pass
            else:
                error = abs(dist - lower_bound)

    except TypeError:
        pass

    return error


def angle_target_values(target_value: Optional[float], target_value_uncertainty: Optional[float],
                        lower_limit: Optional[float], upper_limit: Optional[float],
                        lower_linear_limit: Optional[float], upper_linear_limit: Optional[float]
                        ) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """ Return estimated angle target value, lower_bound, upper_bound.
        @author: Masashi Yokochi
        @note: support for the case target_value is not set, but upper/lower_limit and upper/lower_linear_limit are set
                       (i.e. AMBER restraint format, decide target_value by testing anti-clockwise and clockwise mean),
               support for the case target_value is not set, but upper/lower_limit are set
                       (i.e. CYANA restraint format, decide target_value by comparing lower_limit and upper_limit values),
               support for the case upper/lower_linear_limit are set, but missing upper/lower_limit
                       (i.e. XPLOR-NIH/CNS exponent parameter (ed) equals 1)
    """

    lower_bound, upper_bound = lower_limit, upper_limit

    if lower_bound is None and upper_bound is None and lower_linear_limit is None and upper_linear_limit is None:

        if target_value is None:
            return None, lower_bound, upper_bound

        if target_value_uncertainty is not None:
            lower_bound = target_value - target_value_uncertainty
            upper_bound = target_value + target_value_uncertainty
        else:
            lower_bound = upper_bound = target_value

    if lower_bound is None and lower_linear_limit is not None:
        lower_bound = lower_linear_limit
    if upper_bound is None and upper_linear_limit is not None:
        upper_bound = upper_linear_limit

    if target_value is None:  # target values are not always filled (e.g. AMBER/CYANA dihedral angle restraints)
        has_valid_lower_linear_limit = lower_bound is not None and lower_linear_limit is not None and lower_bound != lower_linear_limit
        has_valid_upper_linear_limit = upper_bound is not None and upper_linear_limit is not None and upper_bound != upper_linear_limit

        try:

            target_value_aclock = (lower_bound + upper_bound) / 2.0
            target_value_clock = target_value_aclock + 180.0
            if target_value_clock >= 360.0:
                target_value_clock -= 360.0

            if has_valid_lower_linear_limit or has_valid_upper_linear_limit:  # decide target value from upper/lower_limit and upper/lower_linear_limit (AMBER)
                target_value_vote_aclock = target_value_vote_clock = 0

                if has_valid_lower_linear_limit:
                    if angle_diff(lower_bound, target_value_aclock) < angle_diff(lower_linear_limit, target_value_aclock):
                        target_value_vote_aclock += 1
                    elif angle_diff(lower_bound, target_value_clock) < angle_diff(lower_linear_limit, target_value_clock):
                        target_value_vote_clock += 1
                if has_valid_upper_linear_limit:
                    if angle_diff(upper_bound, target_value_aclock) < angle_diff(upper_linear_limit, target_value_aclock):
                        target_value_vote_aclock += 1
                    elif angle_diff(upper_bound, target_value_clock) < angle_diff(upper_linear_limit, target_value_clock):
                        target_value_vote_clock += 1

                if target_value_vote_aclock + target_value_vote_clock == 0 or target_value_vote_aclock * target_value_vote_clock != 0:
                    if angle_diff(upper_bound, target_value_aclock) > angle_diff(upper_bound, target_value_clock)\
                       and angle_diff(lower_bound, target_value_aclock) > angle_diff(lower_bound, target_value_clock):
                        return target_value_aclock, lower_bound, upper_bound
                    if angle_diff(upper_bound, target_value_clock) > angle_diff(upper_bound, target_value_aclock)\
                       and angle_diff(lower_bound, target_value_clock) > angle_diff(lower_bound, target_value_aclock):
                        return target_value_clock, lower_bound, upper_bound
                    return None, lower_bound, upper_bound

                target_value = target_value_aclock if target_value_vote_aclock > target_value_vote_clock else target_value_clock

            else:  # estimate target value by comparing lower_limit and upper_limit value, CYANA)
                target_value = target_value_aclock if lower_bound <= upper_bound else target_value_clock

        except TypeError:
            return None, lower_bound, upper_bound

    return target_value, lower_bound, upper_bound


def angle_diff(x: float, y: float) -> float:
    """ Return normalized angular difference.
        @author: Kumaran Baskaran
        @see: wwpdb.apps.validation.src.RestraintValidation.BMRBRestraintsAnalysis.angle_diff.ac
    """

    if x < 0.0:
        x += 360.0
    if y < 0.0:
        y += 360.0

    a, b = sorted([x, y])

    d = b - a
    if d > 180.0:
        d = 360.0 - d

    return d


def angle_error(lower_bound: Optional[float], upper_bound: Optional[float], target_value: Optional[float], angle: float) -> float:
    """ Return angle outlier for given lower_bound, upper_bound, and target_value.
        @author: Kumaran Baskaran
        @see: wwpdb.apps.validation.src.RestraintValidation.BMRBRestraintsAnalysis.angle_diff
    """

    def check_angle_range_overlap(x, y, c, g, t: float = 0.5):
        """ Return whether angular range formed by (x, c) and (c, y) matches to a given range (g) with tolerance (t).
            @author: Kumaran Baskaran
            @see: wwpdb.apps.validation.src.RestraintValidation.BMRBRestraintsAnalysis.angle_diff.check_ac
        """

        l = angle_diff(x, c)  # noqa: E741
        r = angle_diff(y, c)

        return abs(g - (l + r)) < t

    try:

        ld = angle_diff(lower_bound, target_value)
        rd = angle_diff(upper_bound, target_value)

        if check_angle_range_overlap(lower_bound, target_value, angle, ld, 0.5)\
           or check_angle_range_overlap(upper_bound, target_value, angle, rd, 0.5):
            return 0.0

    except TypeError:
        return 0.0

    return min(angle_diff(upper_bound, angle), angle_diff(lower_bound, angle))


def rdc_target_values(target_value: Optional[float], target_value_uncertainty: Optional[float],
                      value: Optional[float], value_uncertainty: Optional[float],
                      lower_limit: Optional[float], upper_limit: Optional[float],
                      lower_linear_limit: Optional[float], upper_linear_limit: Optional[float]
                      ) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """ Return estimated RDC target value, lower_bound, upper_bound.
        @author: Masashi Yokochi
    """

    lower_bound, upper_bound = lower_limit, upper_limit

    if lower_bound is None and upper_bound is None and lower_linear_limit is None and upper_linear_limit is None:
        if target_value is None and value is None:
            return None, lower_bound, upper_bound
        if target_value is not None:
            if target_value_uncertainty is not None:
                lower_bound = target_value - target_value_uncertainty
                upper_bound = target_value + target_value_uncertainty
            else:
                lower_bound = upper_bound = target_value
        else:
            target_value = value
            target_value_uncertainty = value_uncertainty
            if target_value_uncertainty is not None:
                lower_bound = target_value - target_value_uncertainty
                upper_bound = target_value + target_value_uncertainty
            else:
                lower_bound = upper_bound = target_value

    if lower_bound is None and lower_linear_limit is not None:
        lower_bound = lower_linear_limit
    if upper_bound is None and upper_linear_limit is not None:
        upper_bound = upper_linear_limit

    if target_value is None:
        if None not in (lower_bound, upper_bound):
            target_value = (lower_bound + upper_bound) / 2.0
        elif lower_bound is not None:
            target_value = lower_bound
        elif upper_bound is not None:
            target_value = upper_bound

    return target_value, lower_bound, upper_bound


def rdc_error(lower_bound: Optional[float], upper_bound: Optional[float], rdc: float) -> float:
    """ Return RDC outlier for given lower_bound and upper_bound.
        @author: Masashi Yokochi
    """

    error = 0.0

    try:

        if None not in (lower_bound, upper_bound):
            if lower_bound <= rdc <= upper_bound:
                pass
            elif rdc > upper_bound:
                error = abs(rdc - upper_bound)
            else:
                error = abs(rdc - lower_bound)

        elif upper_bound is not None:
            if rdc <= upper_bound:
                pass
            elif rdc > upper_bound:
                error = abs(rdc - upper_bound)

        elif lower_bound is not None:
            if lower_bound <= rdc:
                pass
            else:
                error = abs(rdc - lower_bound)

    except TypeError:
        pass

    return error


def get_violated_model_ids(viol_per_model: List[dict]) -> List[int]:
    return [m for m, err in viol_per_model.items() if err is not None and err > 0.0]


def get_violation_statistics_for_each_bin(beg_err_bin: Optional[float], end_err_bin: Optional[float],
                                          total_models: int, eff_model_ids: List[int], viol_dict: dict
                                          ) -> Tuple[Optional[float], Optional[float], Optional[int],
                                                     Optional[float], Optional[float], Optional[int], Optional[float]]:
    viol_stat_per_model = []

    all_err_list = []
    for m in eff_model_ids:
        err_list = []

        for viol_per_model in viol_dict.values():
            err = viol_per_model[m]

            if err is None or err == 0.0:
                continue

            if (end_err_bin is None and beg_err_bin < err)\
               or beg_err_bin < err <= end_err_bin\
               or (beg_err_bin is None and err < end_err_bin):
                err_list.append(err)
                all_err_list.append(err)

        if len(err_list) == 0:
            viol_stat = [None, None, None]
        else:
            viol_stat = [round(min(err_list), 2),
                         round(max(err_list), 2),
                         len(err_list)]

        viol_stat_per_model.append(viol_stat)

    if len(all_err_list) == 0:
        viol_stat_all_model = [None, None, None, None]
    else:
        viol_stat_all_model = [round(min(all_err_list), 2),
                               round(max(all_err_list), 2),
                               len(all_err_list),
                               round(float(len(all_err_list)) / float(total_models), 1)]

    return viol_stat_all_model, viol_stat_per_model


class NmrVrptUtility:
    """ Wrapper class for NMR restraint analysis.
    """

    def __init__(self, verbose: bool = False, log: IO = sys.stderr,
                 cR: Optional[CifReader] = None, caC: Optional[dict] = None, ccU: Optional[ChemCompUtil] = None,
                 csStat: Optional[BMRBChemShiftStat] = None):
        self.__class_name__ = self.__class__.__name__
        self.__version__ = __version__

        self.__verbose = verbose
        self.__lfh = log

        self.__debug = False
        self.__trust_pdbx_auth_atom_name = False
        self.__use_cache = cR is not None and caC is not None

        # auxiliary input resource
        self.__inputParamDict = {}

        # auxiliary output resource
        self.__outputParamDict = {}

        # sub-directory name for cache file
        self.__sub_dir_name_for_cache = 'utils_nmr'

        # CIF file path
        self.__cifPath = None

        # NMR data file path
        self.__nmrDataPath = None

        # current working directory
        self.__dirPath = None

        # directory for cache files
        self.__cacheDirPath = None

        # hash code of the coordinate file
        self.__cifHashCode = None

        # hash code of the NMR data file
        self.__nmrDataHashCode = None

        # cache file name for results
        self.__resultsCacheName = None

        # CIF reader
        self.__cR = cR

        # NMR data reader
        self.__rR = None

        # CCD accessing utility
        self.__ccU = ChemCompUtil(verbose, log) if ccU is None else ccU

        # BMRB chemical shift statistics
        self.__csStat = BMRBChemShiftStat(verbose, log, self.__ccU) if csStat is None else csStat

        # ParserListerUtil.coordAssemblyChecker()
        self.__caC = caC

        # representative model id
        self.__representative_model_id = REPRESENTATIVE_MODEL_ID
        # representative_alt_id
        self.__representative_alt_id = REPRESENTATIVE_ALT_ID
        # total number of models
        self.__total_models = 0
        # list of effective model_id
        self.__eff_model_ids = None

        # atom id list for each model_id and atom key (auth_asym_id, auth_seq_id, auth_comp_id, auth_atom_id, PDB_ins_code)
        self.__atomIdList = None
        # coordinates for each model_id and atom key
        self.__coordinates = None

        # distance restraints for each restraint key (list_id, restraint_id)
        self.__distRestDict = None
        # distance restraints for each restraint key (list_id, restraint_id, tuple(combination_id, member_id))
        self.__distRestDictWithCombKey = None
        # distance restraint keys for each sequence key (auth_asym_id, auth_seq_id, auth_comp_id)
        self.__distRestSeqDict = None

        # dihedral angle restraints for each restraint key (list_id, restraint_id)
        self.__dihedRestDict = None
        # dihedral angle restraints for each restraint key (list_id, restraint_id, tuple(combination_id))
        self.__dihedRestDictWithCombKey = None
        # dihedral angle restraint keys for each sequence key (auth_asym_id, auth_seq_id, auth_comp_id)
        self.__dihedRestSeqDict = None

        # RDC restraints for each restraint key (list_id, restraint_id)
        self.__rdcRestDict = None
        # RDC restraints for each restraint key (list_id, restraint_id, tuple(combination_id))
        self.__rdcRestDictWithCombKey = None
        # RDC restraint keys for each sequence key (auth_asym_id, auth_seq_id, auth_comp_id)
        self.__rdcRestSeqDict = None

        # distance restraint violations for each restraint key
        self.__distRestViolDict = None
        # list of restraint key of unmapped distance restraints
        self.__distRestUnmapped = None
        # combination keys (Combination_ID/Mmember_ID) of violated distance restraints for each restraint key
        self.__distRestViolCombKeyDict = None

        # dihedral angle restraint violations for each restraint key
        self.__dihedRestViolDict = None
        # list of restraint key of unmapped dihedral angle restraints
        self.__dihedRestUnmapped = None
        # combination key (Combination_ID) of violated dihedral angle restraints for each restraint key
        self.__dihedRestViolCombKeyDict = None

        # RDC restraint violations for each restraint key
        self.__rdcRestViolDict = None
        # list of restraint key of unmapped RDC restraints
        self.__rdcRestUnmapped = None
        # combination key (Combination_ID) of violated RDC restraints for each restraint key
        self.__rdcRestViolCombKeyDict = None

        # summarized restraint analysis results
        self.__results = None

        # whether the previous results have been retrieved
        self.__has_prev_results = False

        # list of known workflow operations
        self.__workFlowOps = ('nmr-restraint-validation',)

        __checkTasks = [self.__parseCoordinate,
                        self.__parseNmrData,
                        self.__checkPreviousResultsIfAvailable,
                        self.__retrieveCoordAssemblyChecker,
                        self.__extractCoordAtomSite,
                        self.__extractGenDistConstraint,
                        self.__extractTorsionAngleConstraint,
                        self.__extractRdcConstraint,
                        self.__calculateDistanceRestraintViolations,
                        self.__calculateDihedralAngleRestraintViolations,
                        self.__calculateRdcRestraintViolations,
                        self.__summarizeCommonResults,
                        self.__summarizeDistanceRestraintAnalysis,
                        self.__summarizeDihedralAngleRestraintAnalysis,
                        self.__summarizeRdcRestraintAnalysis,
                        self.__outputResultsAsPickleFileIfPossible]

        # dictionary of processing tasks of each workflow operation
        self.__procTasksDict = {'nmr-restraint-validation': __checkTasks}

    def setVerbose(self, verbose: bool):
        """ Set verbose mode.
        """

        self.__verbose = verbose

    def setDebugMode(self, debug: bool):
        """ Set debug mode.
        """

        self.__debug = debug

    def trustPdbxAuthAtomName(self, trust_pdbx_auth_atom_name: bool):
        """ Whether to trust _atom_site.pdbx_auth_atom_name rather than _atom_site.auth_atom_id.
            @note: Set True for OneDep validation package.
        """

        self.__trust_pdbx_auth_atom_name = trust_pdbx_auth_atom_name

    def useCache(self, use_cache: bool):
        """ Use cache file(s) of the previous run.
            Do not enable this for generation of wwPDB validation report because of no performance improvement.
        """

        self.__use_cache = use_cache

    def getResults(self) -> Optional[dict]:
        """ Return NMR restraint analysis result.
        """

        return self.__results

    def addInput(self, name: Optional[str] = None, value: Any = None, type: str = 'file'):  # pylint: disable=redefined-builtin
        """ Add a named input and value to the dictionary of input parameters.
        """

        try:

            if type == 'param':
                self.__inputParamDict[name] = value
            elif type == 'file':
                self.__inputParamDict[name] = os.path.abspath(value)
            else:
                raise ValueError(f"+{self.__class_name__}.addInput() ++ Error  - Unknown input type {type}.")

        except Exception as e:
            raise ValueError(f"+{self.__class_name__}.addInput() ++ Error  - " + str(e))

    def addOutput(self, name: Optional[str] = None, value: Any = None, type: str = 'file'):  # pylint: disable=redefined-builtin
        """ Add a named input and value to the dictionary of output parameters.
        """

        try:

            if type == 'param':
                self.__outputParamDict[name] = value
            elif type == 'file':
                self.__outputParamDict[name] = os.path.abspath(value)
                if name == 'result_pickle_file_path':
                    self.__use_cache = True
            else:
                raise ValueError(f"+{self.__class_name__}.addOutput() ++ Error  - Unknown output type {type}.")

        except Exception as e:
            raise ValueError(f"+{self.__class_name__}.addOutput() ++ Error  - " + str(e))

    def op(self, op: str) -> Optional[dict]:
        """ Perform a series of tasks for a given workflow operation.
        """

        if self.__verbose:
            self.__lfh.write(f"+{self.__class_name__}.op() starting op {op}, use_cache {self.__use_cache}\n")

        if op not in self.__workFlowOps:
            raise KeyError(f"+{self.__class_name__}.op() ++ Error  - Unknown workflow operation {op}.")

        if op in self.__procTasksDict:

            for task in self.__procTasksDict[op]:

                if self.__verbose:
                    self.__lfh.write(f"+{self.__class_name__}.op() starting op {op} - task {task.__name__}\n")

                start_time = time.time()

                if not task():
                    break

                if self.__debug and self.__verbose:
                    end_time = time.time()
                    if end_time - start_time > 1.0:
                        self.__lfh.write(f"op: {op}, task: {task.__name__}, elapsed time: {end_time - start_time:.1f} sec\n")

        return self.__results

    def __parseCoordinate(self) -> bool:
        """ Parse coordinates.
        """

        if self.__cR is not None:

            self.__cifPath = self.__cR.getFilePath()

            if self.__use_cache:

                if self.__dirPath is None:
                    self.__dirPath = os.path.dirname(self.__cifPath)

                self.__sub_dir_name_for_cache = self.__cR.__sub_dir_name_for_cache  # pylint: disable=protected-access

                self.__cacheDirPath = os.path.join(self.__dirPath, self.__sub_dir_name_for_cache)

                if not os.path.isdir(self.__cacheDirPath):
                    os.makedirs(self.__cacheDirPath)

                self.__cifHashCode = self.__cR.getHashCode()

            return True

        if not self.__checkCoordInputSource():

            if 'coordinate_file_path' in self.__inputParamDict:

                err = f"No such {self.__inputParamDict['coordinate_file_path']!r} file."

                if self.__verbose:
                    self.__lfh.write(f"+{self.__class_name__}.__parseCoordinate() ++ Error  - {err}\n")

            return False

        file_name = os.path.basename(self.__cifPath)

        try:

            if self.__cifPath is None:

                err = f"{file_name!r} is invalid PDBx/mmCIF file."

                if self.__verbose:
                    self.__lfh.write(f"+{self.__class_name__}.__parseCoordinate() ++ Error  - {err}\n")

                return False

            self.__total_models = 0
            self.__eff_model_ids = []

            ensemble = self.__cR.getDictList('pdbx_nmr_ensemble')

            if len(ensemble) > 0 and 'conformers_submitted_total_number' in ensemble[0]:

                try:
                    self.__total_models = int(ensemble[0]['conformers_submitted_total_number'])
                except ValueError:
                    pass

            if len(ensemble) == 0 or self.__total_models == 0:

                ensemble = self.__cR.getDictList('rcsb_nmr_ensemble')

                if len(ensemble) > 0 and 'conformers_submitted_total_number' in ensemble[0]:

                    try:
                        self.__total_models = int(ensemble[0]['conformers_submitted_total_number'])
                    except ValueError:
                        pass

                else:

                    try:

                        model_num_name = 'pdbx_PDB_model_num' if self.__cR.hasItem('atom_site', 'pdbx_PDB_model_num') else 'ndb_model'

                        model_ids = self.__cR.getDictListWithFilter('atom_site',
                                                                    [{'name': model_num_name, 'type': 'int', 'alt_name': 'model_id'}
                                                                     ])

                        if len(model_ids) > 0:
                            model_ids = set(c['model_id'] for c in model_ids)

                            self.__representative_model_id = min(model_ids)
                            self.__total_models = len(model_ids)
                            self.__eff_model_ids = sorted(model_ids)

                    except Exception as e:

                        if self.__verbose:
                            self.__lfh.write(f"+{self.__class_name__}.__parseCoordinate() ++ Error  - {str(e)}\n")

            if len(ensemble) > 0 and 'representative_conformer' in ensemble[0]:

                try:

                    rep_model_id = int(ensemble[0]['representative_conformer'])

                    if 1 <= rep_model_id <= self.__total_models:
                        self.__representative_model_id = rep_model_id

                except ValueError:
                    pass

            if len(self.__eff_model_ids) == 0:

                try:

                    model_num_name = 'pdbx_PDB_model_num' if self.__cR.hasItem('atom_site', 'pdbx_PDB_model_num') else 'ndb_model'

                    model_ids = self.__cR.getDictListWithFilter('atom_site',
                                                                [{'name': model_num_name, 'type': 'int', 'alt_name': 'model_id'}
                                                                 ])

                    if len(model_ids) > 0:
                        model_ids = set(c['model_id'] for c in model_ids)

                        self.__total_models = len(model_ids)
                        self.__eff_model_ids = sorted(model_ids)

                except Exception as e:

                    if self.__verbose:
                        self.__lfh.write(f"+{self.__class_name__}.__parseCoordinate() ++ Error  - {str(e)}\n")

            if self.__cR.hasItem('atom_site', 'label_alt_id'):
                alt_ids = self.__cR.getDictListWithFilter('atom_site',
                                                          [{'name': 'label_alt_id', 'type': 'str'}
                                                           ])

                if len(alt_ids) > 0:
                    for a in alt_ids:
                        if a['label_alt_id'] not in emptyValue:
                            self.__representative_alt_id = a['label_alt_id']
                            break

            return True

        except Exception:
            return False

    def __checkCoordInputSource(self) -> bool:
        """ Check input source of the coordinates.
        """

        if self.__cifPath is not None:
            return True

        if 'coordinate_file_path' in self.__inputParamDict:

            fPath = self.__inputParamDict['coordinate_file_path']

            if fPath.endswith('.gz'):

                _fPath = os.path.splitext(fPath)[0]

                if not os.path.exists(_fPath):

                    try:

                        uncompress_gzip_file(fPath, _fPath)

                    except Exception as e:

                        if self.__verbose:
                            self.__lfh.write(f"+{self.__class_name__}.__checkCoordInputSource() ++ Error  - {str(e)}\n")

                        return False

                fPath = _fPath

            try:

                if self.__use_cache:

                    if self.__dirPath is None:
                        self.__dirPath = os.path.dirname(fPath)

                    self.__cacheDirPath = os.path.join(self.__dirPath, self.__sub_dir_name_for_cache)

                    if not os.path.isdir(self.__cacheDirPath):
                        os.makedirs(self.__cacheDirPath)

                self.__cR = CifReader(self.__verbose, self.__lfh,
                                      use_cache=self.__use_cache,
                                      sub_dir_name_for_cache=self.__sub_dir_name_for_cache)

                if self.__cR.parse(fPath):
                    self.__cifPath = fPath
                    if self.__use_cache:
                        self.__cifHashCode = self.__cR.getHashCode()
                    return True

            except Exception:
                pass

        if 'coord_cif_reader_object' in self.__inputParamDict:

            self.__cR = self.__inputParamDict['coord_cif_reader_object']

            self.__cifPath = self.__cR.getFilePath()

            if self.__use_cache:

                if self.__dirPath is None:
                    self.__dirPath = os.path.dirname(self.__cifPath)

                self.__sub_dir_name_for_cache = self.__cR.__sub_dir_name_for_cache  # pylint: disable=protected-access

                self.__cacheDirPath = os.path.join(self.__dirPath, self.__sub_dir_name_for_cache)

                if not os.path.isdir(self.__cacheDirPath):
                    os.makedirs(self.__cacheDirPath)

                self.__cifHashCode = self.__cR.getHashCode()

            return True

        return False

    def __parseNmrData(self) -> bool:
        """ Parse NMR data.
        """

        if not self.__checkNmrDataInputSource():

            if 'nmr_cif_file_path' in self.__inputParamDict:

                err = f"No such {self.__inputParamDict['nmr_cif_file_path']!r} file."

                if self.__verbose:
                    self.__lfh.write(f"+{self.__class_name__}.__parseNmrData() ++ Error  - {err}\n")

            return False

        return True

    def __checkNmrDataInputSource(self) -> bool:
        """ Check input source of NMR data.
        """

        if self.__nmrDataPath is not None:
            return True

        if 'nmr_cif_file_path' in self.__inputParamDict:

            fPath = self.__inputParamDict['nmr_cif_file_path']

            if fPath.endswith('.gz'):

                _fPath = os.path.splitext(fPath)[0]

                if not os.path.exists(_fPath):

                    try:

                        uncompress_gzip_file(fPath, _fPath)

                    except Exception as e:

                        if self.__verbose:
                            self.__lfh.write(f"+{self.__class_name__}.__checkNmrDataInputSource() ++ Error  - {str(e)}\n")

                        return False

                fPath = _fPath

            try:

                self.__rR = CifReader(self.__verbose, self.__lfh,
                                      use_cache=False)

                if self.__rR.parse(fPath):
                    self.__nmrDataPath = fPath
                    if self.__use_cache:
                        self.__nmrDataHashCode = self.__rR.getHashCode()
                    return True

            except Exception:
                pass

        if 'nmr_cif_reader_object' in self.__inputParamDict:

            self.__rR = self.__inputParamDict['nmr_cif_reader_object']

            self.__nmrDataPath = self.__rR.getFilePath()

            if self.__use_cache:
                self.__nmrDataHashCode = self.__rR.getHashCode()

            return True

        def get_tempfile_name(suffix: str = ''):
            return os.path.join(tempfile.gettempdir(), f"{next(tempfile._get_candidate_names())}{suffix}")  # pylint: disable=protected-access

        if 'nmr_str_file_path' in self.__inputParamDict:

            fPath = self.__inputParamDict['nmr_str_file_path']

            _fPath = get_tempfile_name('.str2cif')

            try:

                myIo = IoAdapterPy(False, self.__lfh)
                containerList = myIo.readFile(fPath)

                if containerList is not None and len(containerList) > 1:

                    if self.__verbose:
                        self.__lfh.write(f"Input container list is {[(c.getName(), c.getType()) for c in containerList]!r}\n")

                    for c in containerList:
                        c.setType('data')

                    myIo.writeFile(_fPath, containerList=containerList[1:])

                    self.__rR = CifReader(self.__verbose, self.__lfh,
                                          use_cache=False)

                    if self.__rR.parse(_fPath, self.__dirPath):
                        self.__nmrDataPath = fPath
                        if self.__use_cache:
                            self.__nmrDataHashCode = self.__rR.getHashCode()
                        return True

            except Exception as e:
                self.__lfh.write(f"+{self.__class_name__}.__checkNmrDataInputSource() ++ Error  - {str(e)}\n")
            finally:
                try:
                    if os.path.exists(_fPath):
                        os.remove(_fPath)
                except OSError:
                    pass

        if 'pynmrstar_object' in self.__inputParamDict:

            master_entry = self.__inputParamDict['pynmrstar_object']

            _fPath = get_tempfile_name('.str')
            __fPath = _fPath + '.str2cif'

            try:

                master_entry.write_to_file(_fPath, show_comments=False, skip_empty_loops=True, skip_empty_tags=False)

                myIo = IoAdapterPy(False, self.__lfh)
                containerList = myIo.readFile(_fPath)

                if containerList is not None and len(containerList) > 1:

                    if self.__verbose:
                        self.__lfh.write(f"Input container list is {[(c.getName(), c.getType()) for c in containerList]!r}\n")

                    for c in containerList:
                        c.setType('data')

                    myIo.writeFile(__fPath, containerList=containerList[1:])

                    self.__rR = CifReader(self.__verbose, self.__lfh,
                                          use_cache=False)

                    if self.__rR.parse(__fPath, self.__dirPath):
                        self.__nmrDataPath = _fPath
                        if self.__use_cache:
                            self.__nmrDataHashCode = self.__rR.getHashCode()
                        return True

            except Exception as e:
                self.__lfh.write(f"+{self.__class_name__}.__checkNmrDataInputSource() ++ Error  - {str(e)}\n")
            finally:
                try:
                    if os.path.exists(_fPath):
                        os.remove(_fPath)
                    if os.path.exists(__fPath):
                        os.remove(__fPath)
                except OSError:
                    pass

        return False

    def __checkPreviousResultsIfAvailable(self) -> bool:
        """ Retrieve the previous results using the identical data sources, if available.
        """

        if None not in (self.__cifHashCode, self.__nmrDataHashCode):
            self.__resultsCacheName = f"{self.__cifHashCode}_{self.__nmrDataHashCode}_vrpt_results.pkl"
            cache_path = os.path.join(self.__cacheDirPath, self.__resultsCacheName)

            if self.__debug:
                if os.path.exists(cache_path):
                    os.remove(cache_path)

            self.__results = load_from_pickle(cache_path)
            self.__has_prev_results = self.__results is not None

        return True

    def __retrieveCoordAssemblyChecker(self) -> bool:
        """ Wrapper function for ParserListenerUtil.coordAssemblyChecker.
        """

        if self.__has_prev_results:
            return True

        if self.__caC is not None:
            return True

        if self.__use_cache:

            cache_path = None
            if self.__cifHashCode is not None:
                cache_path = os.path.join(self.__cacheDirPath, f"{self.__cifHashCode}_asm_chk.pkl")

                self.__caC = load_from_pickle(cache_path)

                if self.__caC is not None:
                    return True

            self.__caC = coordAssemblyChecker(self.__verbose, self.__lfh,
                                              self.__representative_model_id,
                                              self.__representative_alt_id,
                                              self.__cR, self.__ccU, None, None)

            if self.__caC is not None and cache_path:
                write_as_pickle(self.__caC, cache_path)

        else:
            self.__caC = coordAssemblyChecker(self.__verbose, self.__lfh,
                                              self.__representative_model_id,
                                              self.__representative_alt_id,
                                              self.__cR, self.__ccU, None, None, False)

        return True

    def __extractCoordAtomSite(self) -> bool:
        """ Extract atom_site of coordinate file.
            @author: Masashi Yokochi
            @note: Derived from wwpdb.apps.validation.src.RestraintValidation.BMRBRestraintsAnalysis.get_coordinates,
                   written by Kumaran Baskaran
            @change: class method, use of wwpdb.utils.nmr.io.CifReader, use PDB_ins_code for atom identification, performance optimization
        """

        if self.__has_prev_results:
            return True

        if self.__cifPath is None:
            return False

        vrpt_atom_id_cache_path = vrpt_atom_site_cache_path = None

        if self.__cifHashCode is not None:
            vrpt_atom_id_cache_path = os.path.join(self.__cacheDirPath, f"{self.__cifHashCode}_vrpt_atom_id.pkl")
            self.__atomIdList = load_from_pickle(vrpt_atom_id_cache_path)

            vrpt_atom_site_cache_path = os.path.join(self.__cacheDirPath, f"{self.__cifHashCode}_vrpt_atom_site.pkl")
            self.__coordinates = load_from_pickle(vrpt_atom_site_cache_path)

            if None not in (self.__atomIdList, self.__coordinates):
                return True

        _auth_atom_id = 'pdbx_auth_atom_name'\
            if self.__trust_pdbx_auth_atom_name and self.__cR.hasItem('atom_site', 'pdbx_auth_atom_name')\
            else 'auth_atom_id'

        data_items = [{'name': 'auth_asym_id', 'type': 'str'},
                      {'name': 'auth_seq_id', 'type': 'int'},
                      {'name': 'auth_comp_id', 'type': 'str'},
                      {'name': _auth_atom_id, 'type': 'str', 'alt_name': 'auth_atom_id'},
                      {'name': 'label_asym_id', 'type': 'str'},
                      {'name': 'label_seq_id', 'type': 'int'},
                      {'name': 'label_comp_id', 'type': 'str'},
                      {'name': 'label_atom_id', 'type': 'str'},
                      {'name': 'label_entity_id', 'type': 'int'},
                      {'name': 'label_alt_id', 'type': 'str', 'default': '.'},
                      {'name': 'pdbx_PDB_ins_code', 'type': 'str', 'default': '?'},
                      {'name': 'Cartn_x', 'type': 'float', 'alt_name': 'x'},
                      {'name': 'Cartn_y', 'type': 'float', 'alt_name': 'y'},
                      {'name': 'Cartn_z', 'type': 'float', 'alt_name': 'z'}
                      ]

        # DAOTHER-8705, 8817
        if _auth_atom_id == 'pdbx_auth_atom_name':
            data_items.append({'name': 'auth_atom_id', 'type': 'str', 'alt_name': 'alt_auth_atom_id'})
            data_items.append({'name': 'pdbx_auth_comp_id', 'type': 'str', 'alt_name': 'alt_auth_comp_id'})

        _filter_items = []  # {'name': 'label_alt_id', 'type': 'enum', 'enum': (self.__representativeAltId,)}]

        if len(self.__caC['polymer_sequence']) >= LEN_MAJOR_ASYM_ID:
            _filter_items.append({'name': 'auth_asym_id', 'type': 'enum', 'enum': LARGE_ASYM_ID,
                                  'fetch_first_match': True})  # to process large assembly avoiding forced timeout

        self.__atomIdList = {}
        self.__coordinates = {}

        atom_name_unchecked = comp_name_unchecked = True
        _auth_atom_id_ = 'auth_atom_id'

        try:

            for model_id in self.__eff_model_ids:
                filter_items = copy.copy(_filter_items)
                filter_items.append({'name': 'pdbx_PDB_model_num', 'type': 'int',
                                     'value': model_id})

                coord = self.__cR.getDictListWithFilter('atom_site', data_items, filter_items)

                # DAOTHER-8705
                if atom_name_unchecked:
                    atom_name_unchecked = False
                    if _auth_atom_id == 'pdbx_auth_atom_name':
                        for c in coord:
                            if None not in (c['auth_atom_id'], c['alt_auth_atom_id'])\
                               and c['auth_atom_id'][0].isdigit() and c['alt_auth_atom_id'][0] == 'H':
                                _auth_atom_id_ = 'alt_auth_atom_id'
                                break

                # DAOTHER-8817
                if comp_name_unchecked:
                    comp_name_unchecked = False
                    if _auth_atom_id == 'pdbx_auth_atom_name':
                        for c in coord:
                            if c['auth_comp_id'] is not None and c['auth_comp_id'] not in monDict3\
                               and c['alt_auth_comp_id'] is not None and c['auth_comp_id'] != c['alt_auth_comp_id']:
                                _auth_atom_id_ = 'alt_auth_atom_id'
                                break

                atom_id_list_per_model, coordinates_per_model = {}, {}

                for c in coord:
                    atom_key = (c['auth_asym_id'], c['auth_seq_id'], c['auth_comp_id'],
                                c[_auth_atom_id_], c['pdbx_PDB_ins_code'])

                    # tokens = ("ent_", "said_", "resname_", "seq_", "resnum_", "altcode_", "icode_", "chain_")

                    atom_id_list_per_model[atom_key] =\
                        (c['label_entity_id'], c['label_asym_id'], c['label_comp_id'], c['label_seq_id'],
                         c['auth_seq_id'], c['label_alt_id'], c['pdbx_PDB_ins_code'], c['auth_asym_id'])

                    coordinates_per_model[atom_key] = to_np_array(c)

                    # DAOTHER-9200 for wwpdb.apps.validation.src.wrapper.restraintsanalysis.generate_formated_output (MISSING ATOM IN MODEL KeyError)
                    if _auth_atom_id == 'pdbx_auth_atom_name' and c['auth_atom_id'] != c['alt_auth_atom_id']:
                        _atom_key = (c['auth_asym_id'], c['auth_seq_id'], c['auth_comp_id'],
                                     c['alt_auth_atom_id'], c['pdbx_PDB_ins_code'])

                        atom_id_list_per_model[_atom_key] =\
                            (c['label_entity_id'], c['label_asym_id'], c['label_comp_id'], c['label_seq_id'],
                             c['auth_seq_id'], c['label_alt_id'], c['pdbx_PDB_ins_code'], c['auth_asym_id'])

                        coordinates_per_model[_atom_key] = to_np_array(c)

                self.__atomIdList[model_id] = atom_id_list_per_model
                self.__coordinates[model_id] = coordinates_per_model

            if self.__cifHashCode is not None:
                write_as_pickle(self.__atomIdList, vrpt_atom_id_cache_path)
                write_as_pickle(self.__coordinates, vrpt_atom_site_cache_path)

            return True

        except Exception as e:
            self.__lfh.write(f"Exception occurred while processing {os.path.basename(self.__cifPath)} and {os.path.basename(self.__nmrDataPath)}\n")
            self.__lfh.write(f"+{self.__class_name__}.__extractCoordAtomSite() ++ Error  - {str(e)}\n")

            self.__atomIdList = self.__coordinates = None

        return False

    def __extractGenDistConstraint(self) -> bool:
        """ Extract Gen_dist_constraint category of NMR data file.
            @author: Masashi Yokochi
            @note: Derived from wwpdb.apps.validation.src.RestraintValidation.BMRBRestraintsAnalysis.get_restraints2,
                   written by Kumaran Baskaran
            @change: class method, use of wwpdb.utils.nmr.io.CifReader, improve readability of restraints,
                     support combinational restraints (_Gen_dist_constraint.Combination_ID, Member_ID)
                     define bond types for deselenide bond and metal coordination (sebond, metal)
        """

        if self.__has_prev_results:
            return True

        if self.__nmrDataPath is None:
            return False

        self.__distRestDict = {}
        self.__distRestSeqDict = {}

        lp_category = 'Gen_dist_constraint'
        sf_category = 'Gen_dist_constraint_list'

        try:

            skipped = False

            for datablock_name in self.__rR.getDataBlockNameList():

                if not self.__rR.hasCategory(lp_category, datablock_name):
                    continue

                sf_tag = self.__rR.getDictList(sf_category)

                list_id = int(sf_tag[0]['ID'])

                data_items = [{'name': 'ID', 'type': 'int', 'alt_name': 'id'},
                              {'name': 'Entity_assembly_ID_1', 'type': 'str', 'alt_name': 'entity_asm_id_1'},
                              {'name': 'Auth_asym_ID_1', 'type': 'str', 'alt_name': 'auth_asym_id_1'},
                              {'name': 'Auth_seq_ID_1', 'type': 'int', 'alt_name': 'auth_seq_id_1'},
                              {'name': 'Comp_ID_1', 'type': 'str', 'alt_name': 'comp_id_1'},
                              {'name': 'Atom_ID_1', 'type': 'str', 'alt_name': 'atom_id_1'},
                              {'name': 'Entity_assembly_ID_2', 'type': 'str', 'alt_name': 'entity_asm_id_2'},
                              {'name': 'Auth_asym_ID_2', 'type': 'str', 'alt_name': 'auth_asym_id_2'},
                              {'name': 'Auth_seq_ID_2', 'type': 'int', 'alt_name': 'auth_seq_id_2'},
                              {'name': 'Comp_ID_2', 'type': 'str', 'alt_name': 'comp_id_2'},
                              {'name': 'Atom_ID_2', 'type': 'str', 'alt_name': 'atom_id_2'},
                              {'name': 'Distance_lower_bound_val', 'type': 'float', 'alt_name': 'lower_limit'},
                              {'name': 'Distance_upper_bound_val', 'type': 'float', 'alt_name': 'upper_limit'}
                              ]

                tags = self.__rR.getAttributeList(lp_category)

                has_combination_id = 'Combination_ID' in tags
                has_member_logic_code = 'Member_logic_code' in tags
                has_member_id = 'Member_ID' in tags
                has_pdb_ins_code_1 = 'PDB_ins_code_1' in tags
                has_pdb_ins_code_2 = 'PDB_ins_code_2' in tags
                has_target_val = 'Target_val' in tags
                has_target_val_uncertainty = 'Target_val_uncertainty' in tags
                has_lower_linear_limit = 'Lower_linear_limit' in tags
                has_upper_linear_limit = 'Upper_linear_limit' in tags

                if has_combination_id:
                    data_items.append({'name': 'Combination_ID', 'type': 'int', 'alt_name': 'combination_id'})
                if has_member_logic_code:
                    data_items.append({'name': 'Member_logic_code', 'type': 'enum', 'alt_name': 'member_logic_code',
                                       'enum': ('OR', 'AND')})
                if has_member_id:
                    data_items.append({'name': 'Member_ID', 'type': 'int', 'alt_name': 'member_id'})
                if has_pdb_ins_code_1:
                    data_items.append({'name': 'PDB_ins_code_1', 'type': 'str', 'alt_name': 'ins_code_1', 'default': '?'})
                if has_pdb_ins_code_2:
                    data_items.append({'name': 'PDB_ins_code_2', 'type': 'str', 'alt_name': 'ins_code_2', 'default': '?'})
                if has_target_val:
                    data_items.append({'name': 'Target_val', 'type': 'float', 'alt_name': 'target_value'})
                if has_target_val_uncertainty:
                    data_items.append({'name': 'Target_val_uncertainty', 'type': 'abs-float', 'alt_name': 'target_value_uncertainty'})
                if has_lower_linear_limit:
                    data_items.append({'name': 'Lower_linear_limit', 'type': 'float', 'alt_name': 'lower_linear_limit'})
                if has_upper_linear_limit:
                    data_items.append({'name': 'Upper_linear_limit', 'type': 'float', 'alt_name': 'upper_linear_limit'})

                filter_items = [{'name': 'Gen_dist_constraint_list_ID', 'type': 'int', 'value': list_id}]

                rest = self.__rR.getDictListWithFilter(lp_category,
                                                       data_items,
                                                       filter_items)

                for r in rest:
                    rest_key = (list_id, r['id'])

                    if rest_key not in self.__distRestDict:
                        self.__distRestDict[rest_key] = []

                    auth_asym_id_1 = r['auth_asym_id_1']
                    auth_asym_id_2 = r['auth_asym_id_2']
                    auth_seq_id_1 = r['auth_seq_id_1']
                    auth_seq_id_2 = r['auth_seq_id_2']
                    comp_id_1 = r['comp_id_1']
                    comp_id_2 = r['comp_id_2']
                    atom_id_1 = r['atom_id_1']
                    atom_id_2 = r['atom_id_2']
                    ins_code_1 = r.get('ins_code_1', '?')
                    ins_code_2 = r.get('ins_code_2', '?')
                    target_value = r.get('target_value')
                    target_value_uncertainty = r.get('target_value_uncertainty')
                    lower_limit = r['lower_limit']
                    upper_limit = r['upper_limit']
                    lower_linear_limit = r.get('lower_linear_limit')
                    upper_linear_limit = r.get('upper_linear_limit')

                    if None in (atom_id_1, atom_id_2)\
                       or not isinstance(auth_seq_id_1, int) or not isinstance(auth_seq_id_2, int):
                        if 'HOH' not in (comp_id_1, comp_id_2):
                            self.__lfh.write(f"+{self.__class_name__}.__extractGenDistConstraint() ++ Error  - distance restraint {rest_key} {r} is not interpretable, "
                                             f"{os.path.basename(self.__nmrDataPath)}.\n")
                        skipped = True
                        continue

                    offset = abs(auth_seq_id_1 - auth_seq_id_2)

                    if r['entity_asm_id_1'] != r['entity_asm_id_2']:
                        distance_type = 'interchain'
                    elif offset == 0:
                        distance_type = 'intraresidue'
                    elif offset == 1:
                        distance_type = 'sequential'
                    elif 1 < offset < 5:
                        distance_type = 'medium'
                    else:
                        distance_type = 'long'

                    bb_atoms_1 = self.__csStat.getBackBoneAtoms(comp_id_1)
                    bb_atoms_2 = self.__csStat.getBackBoneAtoms(comp_id_2)

                    if atom_id_1 in bb_atoms_1 and atom_id_2 in bb_atoms_2:
                        distance_sub_type = 'backbone-backbone'
                    elif atom_id_1 in bb_atoms_1 or atom_id_2 in bb_atoms_2:
                        distance_sub_type = 'backbone-sidechain'
                    else:
                        distance_sub_type = 'sidechain-sidechain'

                    target_value, lower_bound, upper_bound =\
                        dist_target_values(target_value, target_value_uncertainty,
                                           lower_limit, upper_limit, lower_linear_limit, upper_linear_limit)

                    if target_value is None:
                        self.__lfh.write(f"+{self.__class_name__}.__extractGenDistConstraint() ++ Error  - distance restraint {rest_key} {r} is not interpretable, "
                                         f"{os.path.basename(self.__nmrDataPath)}.\n")
                        skipped = True
                        continue

                    atom_sels = [[{'chain_id': auth_asym_id_1,
                                   'seq_id': auth_seq_id_1,
                                   'comp_id': comp_id_1,
                                   'atom_id': atom_id_1}],
                                 [{'chain_id': auth_asym_id_2,
                                   'seq_id': auth_seq_id_2,
                                   'comp_id': comp_id_2,
                                   'atom_id': atom_id_2}]]

                    dst_func = {'lower_limit': str(lower_bound) if lower_bound is not None else None,
                                'upper_limit': str(upper_bound) if upper_bound is not None else None}

                    const_type = getDistConstraintType(atom_sels, dst_func, self.__csStat)

                    if const_type == 'hydrogen bond':
                        bond_flag = 'hbond'
                    elif const_type == 'disulfide bond':
                        bond_flag = 'sbond'
                    elif const_type == 'diselenide bond':
                        bond_flag = 'sebond'
                    elif const_type == 'metal coordination':
                        bond_flag = 'metal'
                    else:
                        bond_flag = None

                    or_member = r.get('member_logic_code') != 'AND'

                    self.__distRestDict[rest_key].append({'atom_key_1': (auth_asym_id_1, auth_seq_id_1, comp_id_1,
                                                                         atom_id_1, ins_code_1),
                                                          'atom_key_2': (auth_asym_id_2, auth_seq_id_2, comp_id_2,
                                                                         atom_id_2, ins_code_2),
                                                          'combination_id': r.get('combination_id'),
                                                          'member_id': r.get('member_id'),
                                                          'or_member': or_member,
                                                          'distance_type': distance_type,
                                                          'distance_sub_type': distance_sub_type,
                                                          'bond_flag': bond_flag,
                                                          'lower_bound': lower_bound,
                                                          'upper_bound': upper_bound,
                                                          'target_value': target_value})

                    seq_key_1 = (auth_asym_id_1, auth_seq_id_1, comp_id_1)
                    seq_key_2 = (auth_asym_id_2, auth_seq_id_2, comp_id_2)

                    seq_keys = set([seq_key_1, seq_key_2])

                    for seq_key in seq_keys:
                        if seq_key not in self.__distRestSeqDict:
                            self.__distRestSeqDict[seq_key] = []
                        self.__distRestSeqDict[seq_key].append(rest_key)

            if skipped:
                __distRestDict__ = copy.copy(self.__distRestDict)
                for k, v in __distRestDict__.items():
                    if len(v) == 0:
                        del self.__distRestDict[k]

            for v in self.__distRestSeqDict.values():
                v = list(set(v))

            if len(self.__distRestDict) == 0:
                self.__distRestDict = self.__distRestSeqDict = None

            return True

        except Exception as e:
            self.__lfh.write(f"Exception occurred while processing {os.path.basename(self.__cifPath)} and {os.path.basename(self.__nmrDataPath)}\n")
            self.__lfh.write(f"+{self.__class_name__}.__extractGenDistConstraint() ++ Error  - {str(e)}\n")

            self.__distRestDict = self.__distRestSeqDict = None

        return False

    def __extractTorsionAngleConstraint(self) -> bool:
        """ Extract Torsion_angle_constraint category of NMR data file.
            @author: Masashi Yokochi
            @note: Derived from wwpdb.apps.validation.src.RestraintValidation.BMRBRestraintsAnalysis.get_restraints2,
                   written by Kumaran Baskaran
            @change: class method, use of wwpdb.utils.nmr.io.CifReader, improve readability of restraints,
                     support combinational restraints (_Torsion_angle_constraint.Combination_ID),
                     support for the case target_value is not set, but upper/lower_limit and upper/lower_linear_limit are set
                             (i.e. AMBER restraint format, decide target_value by testing anti-clockwise and clockwise mean),
                     support for the case target_value is not set, but upper/lower_limit are set
                             (i.e. CYANA restraint format, decide target_value by comparing lower_limit and upper_limit values),
                     support for the case upper/lower_linear_limit are set, but missing upper/lower_limit
                             (i.e. XPLOR-NIH/CNS exponent parameter (ed) equals 1)
        """

        if self.__has_prev_results:
            return True

        if self.__nmrDataPath is None:
            return False

        self.__dihedRestDict = {}
        self.__dihedRestSeqDict = {}

        lp_category = 'Torsion_angle_constraint'
        sf_category = 'Torsion_angle_constraint_list'

        try:

            skipped = False

            for datablock_name in self.__rR.getDataBlockNameList():

                if not self.__rR.hasCategory(lp_category, datablock_name):
                    continue

                sf_tag = self.__rR.getDictList(sf_category)

                list_id = int(sf_tag[0]['ID'])

                data_items = [{'name': 'ID', 'type': 'int', 'alt_name': 'id'},
                              {'name': 'Auth_asym_ID_1', 'type': 'str', 'alt_name': 'auth_asym_id_1'},
                              {'name': 'Auth_seq_ID_1', 'type': 'int', 'alt_name': 'auth_seq_id_1'},
                              {'name': 'Comp_ID_1', 'type': 'str', 'alt_name': 'comp_id_1'},
                              {'name': 'Atom_ID_1', 'type': 'str', 'alt_name': 'atom_id_1'},
                              {'name': 'Auth_asym_ID_2', 'type': 'str', 'alt_name': 'auth_asym_id_2'},
                              {'name': 'Auth_seq_ID_2', 'type': 'int', 'alt_name': 'auth_seq_id_2'},
                              {'name': 'Comp_ID_2', 'type': 'str', 'alt_name': 'comp_id_2'},
                              {'name': 'Atom_ID_2', 'type': 'str', 'alt_name': 'atom_id_2'},
                              {'name': 'Auth_asym_ID_3', 'type': 'str', 'alt_name': 'auth_asym_id_3'},
                              {'name': 'Auth_seq_ID_3', 'type': 'int', 'alt_name': 'auth_seq_id_3'},
                              {'name': 'Comp_ID_3', 'type': 'str', 'alt_name': 'comp_id_3'},
                              {'name': 'Atom_ID_3', 'type': 'str', 'alt_name': 'atom_id_3'},
                              {'name': 'Auth_asym_ID_4', 'type': 'str', 'alt_name': 'auth_asym_id_4'},
                              {'name': 'Auth_seq_ID_4', 'type': 'int', 'alt_name': 'auth_seq_id_4'},
                              {'name': 'Comp_ID_4', 'type': 'str', 'alt_name': 'comp_id_4'},
                              {'name': 'Atom_ID_4', 'type': 'str', 'alt_name': 'atom_id_4'},
                              {'name': 'Angle_lower_bound_val', 'type': 'float', 'alt_name': 'lower_limit'},
                              {'name': 'Angle_upper_bound_val', 'type': 'float', 'alt_name': 'upper_limit'},
                              {'name': 'Angle_target_val', 'type': 'float', 'alt_name': 'target_value'}
                              ]

                tags = self.__rR.getAttributeList(lp_category)

                has_torsion_angle_name = 'Torsion_angle_name' in tags
                has_combination_id = 'Combination_ID' in tags
                has_pdb_ins_code_1 = 'PDB_ins_code_1' in tags
                has_pdb_ins_code_2 = 'PDB_ins_code_2' in tags
                has_pdb_ins_code_3 = 'PDB_ins_code_3' in tags
                has_pdb_ins_code_4 = 'PDB_ins_code_4' in tags
                has_lower_linear_limit = 'Angle_lower_linear_limit' in tags
                has_upper_linear_limit = 'Angle_upper_linear_limit' in tags
                has_target_val_err = 'Angle_target_val_err' in tags

                if has_torsion_angle_name:
                    data_items.append({'name': 'Torsion_angle_name', 'type': 'str', 'alt_name': 'angle_type', 'default': 'UNNAMED'})
                if has_combination_id:
                    data_items.append({'name': 'Combination_ID', 'type': 'int', 'alt_name': 'combination_id'})
                if has_pdb_ins_code_1:
                    data_items.append({'name': 'PDB_ins_code_1', 'type': 'str', 'alt_name': 'ins_code_1', 'default': '?'})
                if has_pdb_ins_code_2:
                    data_items.append({'name': 'PDB_ins_code_2', 'type': 'str', 'alt_name': 'ins_code_2', 'default': '?'})
                if has_pdb_ins_code_3:
                    data_items.append({'name': 'PDB_ins_code_3', 'type': 'str', 'alt_name': 'ins_code_3', 'default': '?'})
                if has_pdb_ins_code_4:
                    data_items.append({'name': 'PDB_ins_code_4', 'type': 'str', 'alt_name': 'ins_code_4', 'default': '?'})
                if has_lower_linear_limit:
                    data_items.append({'name': 'Angle_lower_linear_limit', 'type': 'float', 'alt_name': 'lower_linear_limit'})
                if has_upper_linear_limit:
                    data_items.append({'name': 'Angle_upper_linear_limit', 'type': 'float', 'alt_name': 'upper_linear_limit'})
                if has_target_val_err:
                    data_items.append({'name': 'Angle_target_val_err', 'type': 'abs-float', 'alt_name': 'target_value_uncertainty'})

                filter_items = [{'name': 'Torsion_angle_constraint_list_ID', 'type': 'int', 'value': list_id}]

                rest = self.__rR.getDictListWithFilter(lp_category,
                                                       data_items,
                                                       filter_items)

                for r in rest:
                    rest_key = (list_id, r['id'])

                    if rest_key not in self.__dihedRestDict:
                        self.__dihedRestDict[rest_key] = []

                    angle_type = r.get('angle_type', 'UNNAMED')
                    auth_asym_id_1 = r['auth_asym_id_1']
                    auth_asym_id_2 = r['auth_asym_id_2']
                    auth_asym_id_3 = r['auth_asym_id_3']
                    auth_asym_id_4 = r['auth_asym_id_4']
                    auth_seq_id_1 = r['auth_seq_id_1']
                    auth_seq_id_2 = r['auth_seq_id_2']
                    auth_seq_id_3 = r['auth_seq_id_3']
                    auth_seq_id_4 = r['auth_seq_id_4']
                    comp_id_1 = r['comp_id_1']
                    comp_id_2 = r['comp_id_2']
                    comp_id_3 = r['comp_id_3']
                    comp_id_4 = r['comp_id_4']
                    atom_id_1 = r['atom_id_1']
                    atom_id_2 = r['atom_id_2']
                    atom_id_3 = r['atom_id_3']
                    atom_id_4 = r['atom_id_4']
                    ins_code_1 = r.get('ins_code_1', '?')
                    ins_code_2 = r.get('ins_code_2', '?')
                    ins_code_3 = r.get('ins_code_3', '?')
                    ins_code_4 = r.get('ins_code_4', '?')

                    if None in (atom_id_1, atom_id_2, atom_id_3, atom_id_4)\
                       or not isinstance(auth_seq_id_1, int) or not isinstance(auth_seq_id_2, int)\
                       or not isinstance(auth_seq_id_3, int) or not isinstance(auth_seq_id_4, int):
                        if angle_type not in ('PPA', 'UNNAMED'):
                            self.__lfh.write(f"+{self.__class_name__}.__extractTorsionAngleConstraint() ++ Error  - dihedral angle restraint {rest_key} {r} is not interpretable, "
                                             f"{os.path.basename(self.__nmrDataPath)}.\n")
                        skipped = True
                        continue

                    lower_limit = r['lower_limit']
                    upper_limit = r['upper_limit']
                    target_value = r['target_value']
                    lower_linear_limit = r.get('lower_linear_limit')
                    upper_linear_limit = r.get('upper_linear_limit')
                    target_value_uncertainty = r.get('target_value_uncertainty')

                    target_value, lower_bound, upper_bound =\
                        angle_target_values(target_value, target_value_uncertainty,
                                            lower_limit, upper_limit, lower_linear_limit, upper_linear_limit)

                    if target_value is None:
                        self.__lfh.write(f"+{self.__class_name__}.__extractTorsionAngleConstraint() ++ Error  - dihedral angle restraint {rest_key} {r} is not interpretable, "
                                         f"{os.path.basename(self.__nmrDataPath)}.\n")
                        skipped = True
                        continue

                    self.__dihedRestDict[rest_key].append({'atom_key_1': (auth_asym_id_1, auth_seq_id_1, comp_id_1,
                                                                          atom_id_1, ins_code_1),
                                                           'atom_key_2': (auth_asym_id_2, auth_seq_id_2, comp_id_2,
                                                                          atom_id_2, ins_code_2),
                                                           'atom_key_3': (auth_asym_id_3, auth_seq_id_3, comp_id_3,
                                                                          atom_id_3, ins_code_3),
                                                           'atom_key_4': (auth_asym_id_4, auth_seq_id_4, comp_id_4,
                                                                          atom_id_4, ins_code_4),
                                                           'combination_id': r.get('combination_id'),
                                                           'angle_type': angle_type,
                                                           'lower_bound': lower_bound,
                                                           'upper_bound': upper_bound,
                                                           'target_value': target_value})

                    seq_key_1 = (auth_asym_id_1, auth_seq_id_1, comp_id_1)
                    seq_key_2 = (auth_asym_id_2, auth_seq_id_2, comp_id_2)
                    seq_key_3 = (auth_asym_id_3, auth_seq_id_3, comp_id_3)
                    seq_key_4 = (auth_asym_id_4, auth_seq_id_4, comp_id_4)

                    seq_keys = set([seq_key_1, seq_key_2, seq_key_3, seq_key_4])

                    for seq_key in seq_keys:
                        if seq_key not in self.__dihedRestSeqDict:
                            self.__dihedRestSeqDict[seq_key] = []
                        self.__dihedRestSeqDict[seq_key].append(rest_key)

            if skipped:
                __dihedRestDict__ = copy.copy(self.__dihedRestDict)
                for k, v in __dihedRestDict__.items():
                    if len(v) == 0:
                        del self.__dihedRestDict[k]

            for v in self.__dihedRestSeqDict.values():
                v = list(set(v))

            if len(self.__dihedRestDict) == 0:
                self.__dihedRestDict = self.__dihedRestSeqDict = None

            return True

        except Exception as e:
            self.__lfh.write(f"Exception occurred while processing {os.path.basename(self.__cifPath)} and {os.path.basename(self.__nmrDataPath)}\n")
            self.__lfh.write(f"+{self.__class_name__}.__extractTorsionAngleConstraint() ++ Error  - {str(e)}\n")

            self.__dihedRestDict = self.__dihedRestSeqDict = None

        return False

    def __extractRdcConstraint(self) -> bool:
        """ Extract RDC_constraint category of NMR data file.
        """

        if self.__has_prev_results:
            return True

        if self.__nmrDataPath is None:
            return False

        self.__rdcRestDict = {}
        self.__rdcRestSeqDict = {}

        lp_category = 'RDC_constraint'
        sf_category = 'RDC_constraint_list'

        try:

            skipped = False

            for datablock_name in self.__rR.getDataBlockNameList():

                if not self.__rR.hasCategory(lp_category, datablock_name):
                    continue

                sf_tag = self.__rR.getDictList(sf_category)

                list_id = int(sf_tag[0]['ID'])

                try:
                    rdc_type = sf_tag[0]['Details']  # e.g. RDC_HNC, RDC_NH, RDC_CN_i_1, RDC_CAHA, RDC_HNHA, RDC_HNHA_i_1, RDC_CAC, RDC_CAN, RDC_HH, RDC_CC, RDC_other
                    if rdc_type in (None, '', '.', '?', 'null'):
                        rdc_type = 'UNNAMED'
                except KeyError:
                    rdc_type = 'UNNAMED'

                data_items = [{'name': 'ID', 'type': 'int', 'alt_name': 'id'},
                              {'name': 'Auth_asym_ID_1', 'type': 'str', 'alt_name': 'auth_asym_id_1'},
                              {'name': 'Auth_seq_ID_1', 'type': 'int', 'alt_name': 'auth_seq_id_1'},
                              {'name': 'Comp_ID_1', 'type': 'str', 'alt_name': 'comp_id_1'},
                              {'name': 'Atom_ID_1', 'type': 'str', 'alt_name': 'atom_id_1'},
                              {'name': 'Auth_asym_ID_2', 'type': 'str', 'alt_name': 'auth_asym_id_2'},
                              {'name': 'Auth_seq_ID_2', 'type': 'int', 'alt_name': 'auth_seq_id_2'},
                              {'name': 'Comp_ID_2', 'type': 'str', 'alt_name': 'comp_id_2'},
                              {'name': 'Atom_ID_2', 'type': 'str', 'alt_name': 'atom_id_2'},
                              {'name': 'Target_value', 'type': 'float', 'alt_name': 'target_value'},
                              ]

                tags = self.__rR.getAttributeList(lp_category)

                has_combination_id = 'Combination_ID' in tags
                has_pdb_ins_code_1 = 'PDB_ins_code_1' in tags
                has_pdb_ins_code_2 = 'PDB_ins_code_2' in tags
                has_val = 'RDC_val' in tags
                has_val_err = 'RDC_val_err' in tags
                has_lower_bound = 'RDC_lower_bound' in tags
                has_upper_bound = 'RDC_upper_bound' in tags
                has_lower_linear_limit = 'RDC_lower_linear_limit' in tags
                has_upper_linear_limit = 'RDC_upper_linear_limit' in tags
                has_target_val_uncertainty = 'Target_value_uncertainty' in tags

                if has_combination_id:
                    data_items.append({'name': 'Combination_ID', 'type': 'int', 'alt_name': 'combination_id'})
                if has_pdb_ins_code_1:
                    data_items.append({'name': 'PDB_ins_code_1', 'type': 'str', 'alt_name': 'ins_code_1', 'default': '?'})
                if has_pdb_ins_code_2:
                    data_items.append({'name': 'PDB_ins_code_2', 'type': 'str', 'alt_name': 'ins_code_2', 'default': '?'})
                if has_val:
                    data_items.append({'name': 'RDC_val', 'type': 'float', 'alt_name': 'value'})
                if has_val_err:
                    data_items.append({'name': 'RDC_val_err', 'type': 'abs-float', 'alt_name': 'value_uncertainty'})
                if has_lower_bound:
                    data_items.append({'name': 'RDC_lower_bound', 'type': 'float', 'alt_name': 'lower_limit'})
                if has_upper_bound:
                    data_items.append({'name': 'RDC_upper_bound', 'type': 'float', 'alt_name': 'upper_limit'})
                if has_lower_linear_limit:
                    data_items.append({'name': 'RDC_lower_linear_limit', 'type': 'float', 'alt_name': 'lower_linear_limit'})
                if has_upper_linear_limit:
                    data_items.append({'name': 'RDC_upper_linear_limit', 'type': 'float', 'alt_name': 'upper_linear_limit'})
                if has_target_val_uncertainty:
                    data_items.append({'name': 'Target_value_uncertainty', 'type': 'abs-float', 'alt_name': 'target_value_uncertainty'})

                filter_items = [{'name': 'RDC_constraint_list_ID', 'type': 'int', 'value': list_id}]

                rest = self.__rR.getDictListWithFilter(lp_category,
                                                       data_items,
                                                       filter_items)

                for r in rest:
                    rest_key = (list_id, r['id'])

                    if rest_key not in self.__rdcRestDict:
                        self.__rdcRestDict[rest_key] = []

                    auth_asym_id_1 = r['auth_asym_id_1']
                    auth_asym_id_2 = r['auth_asym_id_2']
                    auth_seq_id_1 = r['auth_seq_id_1']
                    auth_seq_id_2 = r['auth_seq_id_2']
                    comp_id_1 = r['comp_id_1']
                    comp_id_2 = r['comp_id_2']
                    atom_id_1 = r['atom_id_1']
                    atom_id_2 = r['atom_id_2']
                    ins_code_1 = r.get('ins_code_1', '?')
                    ins_code_2 = r.get('ins_code_2', '?')

                    if None in (atom_id_1, atom_id_2)\
                       or not isinstance(auth_seq_id_1, int) or not isinstance(auth_seq_id_2, int):
                        self.__lfh.write(f"+{self.__class_name__}.__extractRdcConstraint() ++ Error  - RDC restraint {rest_key} {r} is not interpretable, "
                                         f"{os.path.basename(self.__nmrDataPath)}.\n")
                        skipped = True
                        continue

                    target_value = r['target_value']
                    target_value_uncertainty = r.get('target_value_uncertainty')
                    value = r.get('value')
                    value_uncertainty = r.get('value_uncertainty')
                    lower_limit = r.get('lower_limit')
                    upper_limit = r.get('upper_limit')
                    lower_linear_limit = r.get('lower_linear_limit')
                    upper_linear_limit = r.get('upper_linear_limit')

                    target_value, lower_bound, upper_bound =\
                        rdc_target_values(target_value, target_value_uncertainty, value, value_uncertainty,
                                          lower_limit, upper_limit, lower_linear_limit, upper_linear_limit)

                    if target_value is None:
                        self.__lfh.write(f"+{self.__class_name__}.__extractRdcConstraint() ++ Error  - RDC restraint {rest_key} {r} is not interpretable, "
                                         f"{os.path.basename(self.__nmrDataPath)}.\n")
                        skipped = True
                        continue

                    self.__rdcRestDict[rest_key].append({'atom_key_1': (auth_asym_id_1, auth_seq_id_1, comp_id_1,
                                                                        atom_id_1, ins_code_1),
                                                         'atom_key_2': (auth_asym_id_2, auth_seq_id_2, comp_id_2,
                                                                        atom_id_2, ins_code_2),
                                                         'combination_id': r.get('combination_id'),
                                                         'rdc_type': rdc_type,
                                                         'lower_bound': lower_bound,
                                                         'upper_bound': upper_bound,
                                                         'target_value': target_value})

                    seq_key_1 = (auth_asym_id_1, auth_seq_id_1, comp_id_1)
                    seq_key_2 = (auth_asym_id_2, auth_seq_id_2, comp_id_2)

                    seq_keys = set([seq_key_1, seq_key_2])

                    for seq_key in seq_keys:
                        if seq_key not in self.__rdcRestSeqDict:
                            self.__rdcRestSeqDict[seq_key] = []
                        self.__rdcRestSeqDict[seq_key].append(rest_key)

            if skipped:
                __rdcRestDict__ = copy.copy(self.__rdcRestDict)
                for k, v in __rdcRestDict__.items():
                    if len(v) == 0:
                        del self.__rdcRestDict[k]

            for v in self.__rdcRestSeqDict.values():
                v = list(set(v))

            if len(self.__rdcRestDict) == 0:
                self.__rdcRestDict = self.__rdcRestSeqDict = None

            return True

        except Exception as e:
            self.__lfh.write(f"Exception occurred while processing {os.path.basename(self.__cifPath)} and {os.path.basename(self.__nmrDataPath)}\n")
            self.__lfh.write(f"+{self.__class_name__}.__extractRdcConstraint() ++ Error  - {str(e)}\n")

            self.__rdcRestDict = self.__rdcRestSeqDict = None

        return False

    def __calculateDistanceRestraintViolations(self) -> bool:
        """ Calculate distance restraint violations.
            @author: Masashi Yokochi
            @note: Derived from wwpdb.apps.validation.src.RestraintValidation.BMRBRestraintsAnalysis.calculate_distance_violations,
                   written by Kumaran Baskaran
            @change: class method,
                     support combinational restraints (_Gen_dist_constraint.Combination_ID, Member_ID)
        """

        if self.__distRestDict is None or self.__has_prev_results:
            return True

        if self.__coordinates is None:
            return False

        self.__distRestDictWithCombKey = {}

        self.__distRestViolDict = {}
        self.__distRestViolCombKeyDict = {}
        self.__distRestUnmapped = []

        try:

            def get_uninstanced_hydrogen_coord(model_id, atom_key):

                if atom_key in self.__coordinates[model_id]:
                    return None

                auth_asym_id, auth_seq_id, comp_id, atom_id, ins_code = atom_key

                if atom_id[0] not in protonBeginCode:
                    return None

                if not self.__ccU.updateChemCompDict(comp_id):
                    return None

                if self.__ccU.lastChemCompDict['_chem_comp.pdbx_release_status'] != 'REL':
                    return None

                cca = next((cca for cca in self.__ccU.lastAtomList if cca[self.__ccU.ccaAtomId] == atom_id), None)

                if cca is None:
                    return None

                bonded_to = self.__ccU.getBondedAtoms(comp_id, atom_id)

                if len(bonded_to) == 0:
                    return None

                ref_atom_id = bonded_to[0]

                _atom_key = (auth_asym_id, auth_seq_id, comp_id, ref_atom_id, ins_code)

                if _atom_key not in self.__coordinates[model_id]:
                    return None

                if not (cca[self.__ccU.ccaLeavingAtomFlag] != 'Y'
                        or (self.__csStat.peptideLike(comp_id)
                            and cca[self.__ccU.ccaNTerminalAtomFlag] == 'N'
                            and cca[self.__ccU.ccaCTerminalAtomFlag] == 'N')):
                    return None

                neighbor_to = self.__ccU.getBondedAtoms(comp_id, ref_atom_id, exclProton=True)

                if len(neighbor_to) == 0:
                    return None

                if len(neighbor_to) < 2:
                    for _ref_atom_id in neighbor_to:
                        _neighbor_to = self.__ccU.getBondedAtoms(comp_id, _ref_atom_id, exclProton=True)
                        for __ref_atom_id in _neighbor_to:
                            if __ref_atom_id not in neighbor_to:
                                neighbor_to.append(__ref_atom_id)
                                break
                        if len(neighbor_to) >= 2:
                            break

                if len(neighbor_to) < 2:
                    return None

                ref_atom_ids = [ref_atom_id]
                ref_atoms_xyz = [self.__coordinates[model_id][_atom_key]]

                for _ref_atom_id in neighbor_to:
                    __atom_key = (auth_asym_id, auth_seq_id, comp_id, _ref_atom_id, ins_code)
                    if __atom_key in self.__coordinates[model_id]:
                        ref_atom_ids.append(_ref_atom_id)
                        ref_atoms_xyz.append(self.__coordinates[model_id][__atom_key])

                src_ccd_xyz = np.asarray([float(cca[self.__ccU.ccaCartnX]),
                                          float(cca[self.__ccU.ccaCartnY]),
                                          float(cca[self.__ccU.ccaCartnZ])], dtype=float)

                ccd_atoms_xyz = []
                for _ref_atom_id in ref_atom_ids:
                    _cca = next((_cca for _cca in self.__ccU.lastAtomList if _cca[self.__ccU.ccaAtomId] == _ref_atom_id), None)
                    if _cca is not None:
                        ccd_atoms_xyz.append(np.asarray([float(_cca[self.__ccU.ccaCartnX]),
                                                         float(_cca[self.__ccU.ccaCartnY]),
                                                         float(_cca[self.__ccU.ccaCartnZ])], dtype=float))

                if len(ref_atoms_xyz) != len(ccd_atoms_xyz):
                    return None

                dst_ccd_xyz, rmsd = calculate_uninstanced_coord(np.asarray(ccd_atoms_xyz),
                                                                np.asarray(ref_atoms_xyz),
                                                                np.asarray([src_ccd_xyz]))

                if rmsd > 0.1:
                    return None

                return dst_ccd_xyz[0]

            def calc_dist_rest_viol(rest_key, restraints):

                error_per_model = {}

                for model_id in self.__coordinates:

                    dist_list_set = {}

                    for r in restraints:
                        atom_key_1 = r['atom_key_1']
                        atom_key_2 = r['atom_key_2']
                        lower_bound = r['lower_bound']
                        upper_bound = r['upper_bound']

                        bound_key = (lower_bound, upper_bound, 'or' if r['or_member'] else r['member_id'])

                        if bound_key not in dist_list_set:
                            dist_list_set[bound_key] = []

                        atom_present = True

                        try:
                            pos_1 = self.__coordinates[model_id][atom_key_1]
                        except KeyError:
                            pos_1 = get_uninstanced_hydrogen_coord(model_id, atom_key_1)
                            if pos_1 is None:
                                if self.__verbose:
                                    self.__lfh.write(f"Atom (auth_asym_id: {atom_key_1[0]}, auth_seq_id: {atom_key_1[1]}, "
                                                     f"comp_id: {atom_key_1[2]}, atom_id: {atom_key_1[3]}) "
                                                     f"not found in the coordinates for distance restraint {rest_key}.\n")
                                atom_present = False

                        try:
                            pos_2 = self.__coordinates[model_id][atom_key_2]
                        except KeyError:
                            pos_2 = get_uninstanced_hydrogen_coord(model_id, atom_key_2)
                            if pos_2 is None:
                                if self.__verbose:
                                    self.__lfh.write(f"Atom (auth_asym_id: {atom_key_2[0]}, auth_seq_id: {atom_key_2[1]}, "
                                                     f"comp_id: {atom_key_2[2]}, atom_id: {atom_key_2[3]}) "
                                                     f"not found in the coordinates for distance restraint {rest_key}.\n")
                                atom_present = False

                        if atom_present:

                            d = distance(pos_1, pos_2)
                            if d == 0.0:
                                self.__lfh.write(f"+{self.__class_name__}.__calculateDistanceRestraintViolations() ++ Error  - "
                                                 "distance restraint {rest_key} {r} does not make sense, "
                                                 f"{os.path.basename(self.__nmrDataPath)}.\n")
                            dist_list_set[bound_key].append(d)
                        else:
                            self.__distRestUnmapped.append(rest_key)

                    error = None

                    if len(dist_list_set) > 0:

                        for bound_key, dist_list in dist_list_set.items():

                            if len(dist_list) == 0:
                                continue

                            lower_bound, upper_bound, _ = bound_key
                            avr_d = dist_inv_6_summed(dist_list)

                            _error = dist_error(lower_bound, upper_bound, avr_d)

                            if error is None or error > _error:
                                error = _error

                    error_per_model[model_id] = error

                return error_per_model

            def fill_smaller_error_for_each_model(error_per_model, min_error_per_model,
                                                  combination_id, member_id, min_comb_key_per_model):
                for model_id in self.__eff_model_ids:
                    error = error_per_model[model_id]

                    if error is not None and error < min_error_per_model[model_id]:
                        min_error_per_model[model_id] = error
                        min_comb_key_per_model[model_id]['combination_id'] = combination_id
                        min_comb_key_per_model[model_id]['member_id'] = member_id

            def get_viol_per_model(min_error_per_model, min_comb_key_per_model):
                viol_per_model, comb_key_per_model = {}, {}

                for model_id in self.__eff_model_ids:
                    error = min_error_per_model[model_id]
                    comb_key = min_comb_key_per_model[model_id]

                    if NMR_VTF_DIST_VIOL_CUTOFF < error < DIST_ERROR_MAX:
                        viol_per_model[model_id] = round(error, 2)
                        comb_key_per_model[model_id] = (comb_key['combination_id'], comb_key['member_id'])
                    else:
                        viol_per_model[model_id] = None
                        comb_key_per_model[model_id] = None

                return viol_per_model, comb_key_per_model

            for rest_key, restraints in self.__distRestDict.items():

                has_combination_id = any(r for r in restraints if r['combination_id'] is not None)
                has_member_id = any(r for r in restraints if r['member_id'] is not None)

                self.__distRestDictWithCombKey[rest_key] = {}

                min_error_per_model = {model_id: DIST_ERROR_MAX for model_id in self.__eff_model_ids}
                min_comb_key_per_model = {model_id: {'combination_id': None, 'member_id': None}
                                          for model_id in self.__eff_model_ids}

                if not has_combination_id and not has_member_id:
                    error_per_model = calc_dist_rest_viol(rest_key, restraints)

                    fill_smaller_error_for_each_model(error_per_model, min_error_per_model,
                                                      None, None, min_comb_key_per_model)

                    self.__distRestDictWithCombKey[rest_key][(None, None)] = restraints

                elif not has_combination_id and has_member_id:
                    member_ids = set(r['member_id'] for r in restraints)

                    for member_id in member_ids:
                        _restraints = [r for r in restraints if r['member_id'] == member_id]

                        _error_per_model = calc_dist_rest_viol(rest_key, _restraints)

                        fill_smaller_error_for_each_model(_error_per_model, min_error_per_model,
                                                          None, member_id, min_comb_key_per_model)

                        self.__distRestDictWithCombKey[rest_key][(None, member_id)] = _restraints

                elif has_combination_id and not has_member_id:
                    combination_ids = set(r['combination_id'] for r in restraints)

                    for combination_id in combination_ids:
                        _restraints = [r for r in restraints if r['combination_id'] == combination_id]

                        _error_per_model = calc_dist_rest_viol(rest_key, _restraints)

                        fill_smaller_error_for_each_model(_error_per_model, min_error_per_model,
                                                          combination_id, None, min_comb_key_per_model)

                        self.__distRestDictWithCombKey[rest_key][(combination_id, None)] = _restraints

                else:
                    combination_ids = set(r['combination_id'] for r in restraints)
                    member_ids = set(r['member_id'] for r in restraints)

                    for combination_id in combination_ids:

                        for member_id in member_ids:
                            _restraints = [r for r in restraints
                                           if r['combination_id'] == combination_id
                                           and r['member_id'] == member_id]

                            _error_per_model = calc_dist_rest_viol(rest_key, _restraints)

                            fill_smaller_error_for_each_model(_error_per_model, min_error_per_model,
                                                              combination_id, member_id,
                                                              min_comb_key_per_model)

                            self.__distRestDictWithCombKey[rest_key][(combination_id, member_id)] = _restraints

                self.__distRestViolDict[rest_key], self.__distRestViolCombKeyDict[rest_key] =\
                    get_viol_per_model(min_error_per_model, min_comb_key_per_model)

            self.__distRestUnmapped = list(set(self.__distRestUnmapped))

            return True

        except Exception as e:
            self.__lfh.write(f"Exception occurred while processing {os.path.basename(self.__cifPath)} and {os.path.basename(self.__nmrDataPath)}\n")
            self.__lfh.write(f"+{self.__class_name__}.__calculateDistanceRestraintViolations() ++ Error  - {str(e)}\n")

            self.__distRestViolDict = self.__distRestUnmapped = None

        return False

    def __calculateDihedralAngleRestraintViolations(self) -> bool:
        """ Calculate dihedral angle restraint violations.
            @author: Masashi Yokochi
            @note: Derived from wwpdb.apps.validation.src.RestraintValidation.BMRBRestraintsAnalysis.calculate_angle_violations,
                   written by Kumaran Baskaran
            @change: class method,
                     support combinational restraints (_Torsion_angle_constraint.Combination_ID)
        """

        if self.__dihedRestDict is None or self.__has_prev_results:
            return True

        if self.__coordinates is None:
            return False

        self.__dihedRestDictWithCombKey = {}

        self.__dihedRestViolDict = {}
        self.__dihedRestViolCombKeyDict = {}
        self.__dihedRestUnmapped = []

        try:

            def calc_dihed_rest_viol(rest_key, restraints):

                error_per_model = {}

                for model_id in self.__coordinates:

                    angle_list_set = {}

                    for r in restraints:
                        atom_key_1 = r['atom_key_1']
                        atom_key_2 = r['atom_key_2']
                        atom_key_3 = r['atom_key_3']
                        atom_key_4 = r['atom_key_4']
                        lower_bound = r['lower_bound']
                        upper_bound = r['upper_bound']
                        target_value = r['target_value']

                        bound_key = (lower_bound, upper_bound, target_value)

                        if bound_key not in angle_list_set:
                            angle_list_set[bound_key] = []

                        atom_present = True

                        try:
                            pos_1 = self.__coordinates[model_id][atom_key_1]
                        except KeyError:
                            if self.__verbose:
                                self.__lfh.write(f"Atom (auth_asym_id: {atom_key_1[0]}, auth_seq_id: {atom_key_1[1]}, "
                                                 f"comp_id: {atom_key_1[2]}, atom_id: {atom_key_1[3]}) "
                                                 f"not found in the coordinates for dihedral angle restraint {rest_key}.\n")
                            atom_present = False

                        try:
                            pos_2 = self.__coordinates[model_id][atom_key_2]
                        except KeyError:
                            if self.__verbose:
                                self.__lfh.write(f"Atom (auth_asym_id: {atom_key_2[0]}, auth_seq_id: {atom_key_2[1]}, "
                                                 f"comp_id: {atom_key_2[2]}, atom_id: {atom_key_2[3]}) "
                                                 f"not found in the coordinates for dihedral angle restraint {rest_key}.\n")
                            atom_present = False

                        try:
                            pos_3 = self.__coordinates[model_id][atom_key_3]
                        except KeyError:
                            if self.__verbose:
                                self.__lfh.write(f"Atom (auth_asym_id: {atom_key_3[0]}, auth_seq_id: {atom_key_3[1]}, "
                                                 f"comp_id: {atom_key_3[2]}, atom_id: {atom_key_3[3]}) "
                                                 f"not found in the coordinates for dihedral angle restraint {rest_key}.\n")
                            atom_present = False

                        try:
                            pos_4 = self.__coordinates[model_id][atom_key_4]
                        except KeyError:
                            if self.__verbose:
                                self.__lfh.write(f"Atom (auth_asym_id: {atom_key_4[0]}, auth_seq_id: {atom_key_4[1]}, "
                                                 f"comp_id: {atom_key_4[2]}, atom_id: {atom_key_4[3]}) "
                                                 f"not found in the coordinates for dihedral angle restraint {rest_key}.\n")
                            atom_present = False

                        if atom_present:
                            a = dihedral_angle(pos_1, pos_2, pos_3, pos_4) + 180.0
                            angle_list_set[bound_key].append(a)
                        else:
                            self.__dihedRestUnmapped.append(rest_key)

                    error = None

                    if len(angle_list_set) > 0:

                        for bound_key, angle_list in angle_list_set.items():

                            if len(angle_list) == 0:
                                continue

                            lower_bound, upper_bound, target_value = bound_key
                            avr_a = np.mean(np.array(angle_list)) - 180.0

                            _error = angle_error(lower_bound, upper_bound, target_value, avr_a)

                            if error is None or error > _error:
                                error = _error

                    error_per_model[model_id] = error

                return error_per_model

            def fill_smaller_error_for_each_model(error_per_model, min_error_per_model,
                                                  combination_id, min_comb_key_per_model):
                for model_id in self.__eff_model_ids:
                    error = error_per_model[model_id]

                    if error is not None and error < min_error_per_model[model_id]:
                        min_error_per_model[model_id] = error
                        min_comb_key_per_model[model_id]['combination_id'] = combination_id

            def get_viol_per_model(min_error_per_model, min_comb_key_per_model):
                viol_per_model, comb_key_per_model = {}, {}

                for model_id in self.__eff_model_ids:
                    error = min_error_per_model[model_id]
                    comb_key = min_comb_key_per_model[model_id]

                    if NMR_VTF_DIHED_VIOL_CUTOFF < error < ANGLE_ERROR_MAX:
                        viol_per_model[model_id] = round(error, 2)
                        comb_key_per_model[model_id] = (comb_key['combination_id'],)
                    else:
                        viol_per_model[model_id] = None
                        comb_key_per_model[model_id] = None

                return viol_per_model, comb_key_per_model

            for rest_key, restraints in self.__dihedRestDict.items():

                has_combination_id = any(r for r in restraints if r['combination_id'] is not None)

                self.__dihedRestDictWithCombKey[rest_key] = {}

                min_error_per_model = {model_id: ANGLE_ERROR_MAX for model_id in self.__eff_model_ids}
                min_comb_key_per_model = {model_id: {'combination_id': None}
                                          for model_id in self.__eff_model_ids}

                if not has_combination_id:
                    error_per_model = calc_dihed_rest_viol(rest_key, restraints)

                    fill_smaller_error_for_each_model(error_per_model, min_error_per_model,
                                                      None, min_comb_key_per_model)

                    self.__dihedRestDictWithCombKey[rest_key][(None,)] = restraints

                else:
                    combination_ids = set(r['combination_id'] for r in restraints)

                    for combination_id in combination_ids:
                        _restraints = [r for r in restraints if r['combination_id'] == combination_id]

                        _error_per_model = calc_dihed_rest_viol(rest_key, _restraints)

                        fill_smaller_error_for_each_model(_error_per_model, min_error_per_model,
                                                          combination_id, min_comb_key_per_model)

                        self.__dihedRestDictWithCombKey[rest_key][(combination_id,)] = _restraints

                self.__dihedRestViolDict[rest_key], self.__dihedRestViolCombKeyDict[rest_key] =\
                    get_viol_per_model(min_error_per_model, min_comb_key_per_model)

            self.__dihedRestUnmapped = list(set(self.__dihedRestUnmapped))

            return True

        except Exception as e:
            self.__lfh.write(f"Exception occurred while processing {os.path.basename(self.__cifPath)} and {os.path.basename(self.__nmrDataPath)}\n")
            self.__lfh.write(f"+{self.__class_name__}.__calculateDihedralAngleRestraintViolations() ++ Error  - {str(e)}\n")

            self.__dihedRestViolDict = self.__dihedRestUnmapped = None

        return False

    def __calculateRdcRestraintViolations(self) -> bool:
        """ Calculate RDC restraint violations.
            @author: Masashi Yokochi
        """

        if self.__rdcRestDict is None or self.__has_prev_results:
            return True

        if self.__coordinates is None:
            return False

        return True  # TODO  pylint: disable=fixme

        self.__rdcRestDictWithCombKey = {}  # pylint: disable='unreachable'

        self.__rdcRestViolDict = {}
        self.__rdcRestViolCombKeyDict = {}
        self.__rdcRestUnmapped = []

        try:

            def calc_rdc_rest_viol(rest_key, restraints):

                error_per_model = {}

                for model_id in self.__coordinates:

                    rdc_list_set = {}

                    for r in restraints:
                        atom_key_1 = r['atom_key_1']
                        atom_key_2 = r['atom_key_2']
                        lower_bound = r['lower_bound']
                        upper_bound = r['upper_bound']

                        bound_key = (lower_bound, upper_bound)

                        if bound_key not in rdc_list_set:
                            rdc_list_set[bound_key] = []

                        atom_present = True

                        try:
                            pos_1 = self.__coordinates[model_id][atom_key_1]  # noqa: F841, pylint: disable='unused-variable'
                        except KeyError:
                            if self.__verbose:
                                self.__lfh.write(f"Atom (auth_asym_id: {atom_key_1[0]}, auth_seq_id: {atom_key_1[1]}, "
                                                 f"comp_id: {atom_key_1[2]}, atom_id: {atom_key_1[3]}) "
                                                 f"not found in the coordinates for RDC restraint {rest_key}.\n")
                            atom_present = False

                        try:
                            pos_2 = self.__coordinates[model_id][atom_key_2]  # noqa: F841, pylint: disable='unused-variable'
                        except KeyError:
                            if self.__verbose:
                                self.__lfh.write(f"Atom (auth_asym_id: {atom_key_2[0]}, auth_seq_id: {atom_key_2[1]}, "
                                                 f"comp_id: {atom_key_2[2]}, atom_id: {atom_key_2[3]}) "
                                                 f"not found in the coordinates for RDC restraint {rest_key}.\n")
                            atom_present = False

                        if atom_present:
                            # """ TODO: rdc() should return calculated RDC value for a given vector using the RDC alignment tensor of rest_key[0]
                            # r = rdc(rest_key[0], pos_1, pos_2)
                            # rdc_list_set[bound_key].append(r)
                            # """
                            pass
                        else:
                            self.__rdcRestUnmapped.append(rest_key)

                    error = None

                    if len(rdc_list_set) > 0:

                        for bound_key, rdc_list in rdc_list_set.items():

                            if len(rdc_list) == 0:
                                continue

                            lower_bound, upper_bound = bound_key
                            avr_r = np.mean(np.array(rdc_list))

                            _error = rdc_error(lower_bound, upper_bound, avr_r)

                            if error is None or error > _error:
                                error = _error

                    error_per_model[model_id] = error

                return error_per_model

            def fill_smaller_error_for_each_model(error_per_model, min_error_per_model,
                                                  combination_id, min_comb_key_per_model):
                for model_id in self.__eff_model_ids:
                    error = error_per_model[model_id]

                    if error is not None and error < min_error_per_model[model_id]:
                        min_error_per_model[model_id] = error
                        min_comb_key_per_model[model_id]['combination_id'] = combination_id

            def get_viol_per_model(min_error_per_model, min_comb_key_per_model):
                viol_per_model, comb_key_per_model = {}, {}

                for model_id in self.__eff_model_ids:
                    error = min_error_per_model[model_id]
                    comb_key = min_comb_key_per_model[model_id]

                    if NMR_VTF_RDC_VIOL_CUTOFF < error < RDC_ERROR_MAX:
                        viol_per_model[model_id] = round(error, 2)
                        comb_key_per_model[model_id] = (comb_key['combination_id'],)
                    else:
                        viol_per_model[model_id] = None
                        comb_key_per_model[model_id] = None

                return viol_per_model, comb_key_per_model

            for rest_key, restraints in self.__rdcRestDict.items():

                has_combination_id = any(r for r in restraints if r['combination_id'] is not None)

                self.__rdcRestDictWithCombKey[rest_key] = {}

                min_error_per_model = {model_id: RDC_ERROR_MAX for model_id in self.__eff_model_ids}
                min_comb_key_per_model = {model_id: {'combination_id': None}
                                          for model_id in self.__eff_model_ids}

                if not has_combination_id:
                    error_per_model = calc_rdc_rest_viol(rest_key, restraints)

                    fill_smaller_error_for_each_model(error_per_model, min_error_per_model,
                                                      None, min_comb_key_per_model)

                    self.__rdcRestDictWithCombKey[rest_key][(None,)] = restraints

                else:
                    combination_ids = set(r['combination_id'] for r in restraints)

                    for combination_id in combination_ids:
                        _restraints = [r for r in restraints if r['combination_id'] == combination_id]

                        _error_per_model = calc_rdc_rest_viol(rest_key, _restraints)

                        fill_smaller_error_for_each_model(_error_per_model, min_error_per_model,
                                                          combination_id, min_comb_key_per_model)

                        self.__rdcRestDictWithCombKey[rest_key][(combination_id,)] = _restraints

                self.__rdcRestViolDict[rest_key], self.__rdcRestViolCombKeyDict[rest_key] =\
                    get_viol_per_model(min_error_per_model, min_comb_key_per_model)

            self.__rdcRestUnmapped = list(set(self.__rdcRestUnmapped))

            return True

        except Exception as e:
            self.__lfh.write(f"Exception occurred while processing {os.path.basename(self.__cifPath)} and {os.path.basename(self.__nmrDataPath)}\n")
            self.__lfh.write(f"+{self.__class_name__}.__calculateRdcRestraintViolations() ++ Error  - {str(e)}\n")

            self.__rdcRestViolDict = self.__rdcRestUnmapped = None

        return False

    def __summarizeCommonResults(self) -> bool:
        """ Summarize common results.
        """

        if self.__has_prev_results:
            return True

        self.__results = {'total_models': self.__total_models, 'eff_model_ids': self.__eff_model_ids,
                          'atom_ids': self.__atomIdList, 'key_lists': {}}

        for datablock_name in self.__rR.getDataBlockNameList():

            if not self.__rR.hasCategory('Chem_comp_assembly', datablock_name):
                continue

            self.__results['seq_length'] = self.__rR.getRowLength('Chem_comp_assembly')

            break

        return True

    def __summarizeDistanceRestraintAnalysis(self) -> bool:
        """ Summarize distance restraint analysis results.
            @author: Masashi Yokochi
            @note: Derived from wwpdb.apps.validation.src.RestraintValidation.BMRBRestraintsAnalysis.generate_output,
                   written by Kumaran Baskaran
            @change: class method, improve readability of restraints, support combinational restraints, performance optimization
        """

        if self.__has_prev_results:
            return True

        try:

            self.__results['distance'] = self.__distRestViolDict is not None and len(self.__distRestViolDict) > 0

            if not self.__results['distance']:
                return True

            self.__results['dist_seq_dict'] = self.__distRestSeqDict
            self.__results['unmapped_dist'] = self.__distRestUnmapped

            any_type = 'total'

            distance_type = ('intraresidue', 'sequential', 'medium', 'long', 'interchain', any_type)
            distance_sub_type = ('backbone-backbone', 'backbone-sidechain', 'sidechain-sidechain')
            bond_flag = ('hbond', 'sbond', 'sebond', 'metal', None)

            self.__results['key_lists']['distance_type'] = distance_type
            self.__results['key_lists']['distance_sub_type'] = distance_sub_type
            self.__results['key_lists']['bond_flag'] = bond_flag

            distance_summary, distance_violation = {}, {}

            consistent_distance_violation, distance_violations_vs_models, distance_violations_in_models =\
                {}, {}, {}

            for m in self.__eff_model_ids:
                distance_violations_in_models[m] = {}

                for t in distance_type:
                    distance_summary[t] = {}
                    distance_violation[t] = {}
                    consistent_distance_violation[t] = {}
                    distance_violations_vs_models[t] = {}
                    distance_violations_in_models[m][t] = {}

                    for s in distance_sub_type:
                        distance_summary[t][s] = {}
                        distance_violation[t][s] = {}
                        consistent_distance_violation[t][s] = {}
                        distance_violations_vs_models[t][s] = {}
                        distance_violations_in_models[m][t][s] = {}

                        for b in bond_flag:
                            distance_summary[t][s][b] = 0
                            distance_violation[t][s][b] = 0
                            consistent_distance_violation[t][s][b] = 0
                            distance_violations_vs_models[t][s][b] = [0] * (self.__total_models + 1)
                            distance_violations_in_models[m][t][s][b] = []

            for rest_key, restraints in self.__distRestDict.items():
                r = restraints[0]

                t = r['distance_type']
                s = r['distance_sub_type']
                b = r['bond_flag']

                distance_summary[t][s][b] += 1
                distance_summary[any_type][s][b] += 1

                len_vm = len(get_violated_model_ids(self.__distRestViolDict[rest_key]))

                if len_vm > 0:
                    distance_violation[t][s][b] += 1
                    distance_violation[any_type][s][b] += 1

                if len_vm == self.__total_models:
                    consistent_distance_violation[t][s][b] += 1
                    consistent_distance_violation[any_type][s][b] += 1

                distance_violations_vs_models[t][s][b][len_vm] += 1
                distance_violations_vs_models[any_type][s][b][len_vm] += 1

            self.__results['distance_summary'] = distance_summary
            self.__results['distance_violation'] = distance_violation
            self.__results['consistent_distance_violation'] = consistent_distance_violation
            self.__results['distance_violations_vs_models'] = distance_violations_vs_models

            for rest_key, viol_per_model in self.__distRestViolDict.items():
                for m in self.__eff_model_ids:
                    err = viol_per_model[m]

                    if err is None or err == 0.0:
                        continue

                    comb_key = self.__distRestViolCombKeyDict[rest_key][m]

                    if comb_key is None:
                        continue

                    r = self.__distRestDictWithCombKey[rest_key][comb_key][0]
                    t = r['distance_type']
                    s = r['distance_sub_type']
                    b = r['bond_flag']

                    distance_violations_in_models[m][t][s][b].append(err)
                    distance_violations_in_models[m][any_type][s][b].append(err)

            self.__results['distance_violations_in_models'] = distance_violations_in_models

            dist_range = []

            residual_distance_violation = {}
            for idx, beg_err_bin in enumerate(NMR_VTF_DIST_ERR_BINS):
                if idx == len(NMR_VTF_DIST_ERR_BINS) - 1:
                    end_err_bin = None
                    dist_err_range = f">{beg_err_bin}"
                else:
                    end_err_bin = NMR_VTF_DIST_ERR_BINS[idx + 1]
                    dist_err_range = f"{beg_err_bin}-{end_err_bin}"

                dist_range.append(dist_err_range)
                residual_distance_violation[dist_err_range] =\
                    get_violation_statistics_for_each_bin(beg_err_bin, end_err_bin,
                                                          self.__total_models,
                                                          self.__eff_model_ids,
                                                          self.__distRestViolDict)

            self.__results['key_lists']['dist_range'] = dist_range
            self.__results['residual_distance_violation'] = residual_distance_violation

            most_violated_distance = []
            for rest_key, viol_per_model in self.__distRestViolDict.items():
                vm = get_violated_model_ids(viol_per_model)

                if len(vm) > 1:
                    e = np.array([err for err in viol_per_model.values() if err is not None and err > 0.0])

                    comb_keys = []
                    for _m in set(vm):
                        comb_key = self.__distRestViolCombKeyDict[rest_key][_m]

                        if comb_key is None:
                            continue

                        if comb_key not in comb_keys:
                            comb_keys.append(comb_key)

                    for comb_key in comb_keys:
                        for r in self.__distRestDictWithCombKey[rest_key][comb_key]:
                            most_violated_distance.append([rest_key,
                                                           r['atom_key_1'],
                                                           r['atom_key_2'],
                                                           r['distance_type'],
                                                           r['distance_sub_type'],
                                                           r['bond_flag'],
                                                           len(vm),
                                                           vm,
                                                           np.min(e),
                                                           np.max(e),
                                                           np.mean(e),
                                                           np.std(e),
                                                           np.median(e)])

            self.__results['most_violated_distance'] =\
                sorted(most_violated_distance, reverse=True, key=itemgetter(6, 10))

            all_distance_violations = []
            for rest_key, viol_per_model in self.__distRestViolDict.items():
                for m in self.__eff_model_ids:
                    err = viol_per_model[m]

                    if err is None or err == 0.0:
                        continue

                    comb_key = self.__distRestViolCombKeyDict[rest_key][m]

                    if comb_key is None:
                        continue

                    for r in self.__distRestDictWithCombKey[rest_key][comb_key]:
                        all_distance_violations.append([rest_key,
                                                        r['atom_key_1'],
                                                        r['atom_key_2'],
                                                        m,
                                                        r['distance_type'],
                                                        r['distance_sub_type'],
                                                        r['bond_flag'],
                                                        err])

            self.__results['all_distance_violations'] =\
                sorted(all_distance_violations, reverse=True, key=itemgetter(7, 0))

            dist_violation_seq = {}
            for seq_key, rest_keys in self.__distRestSeqDict.items():
                for m in self.__eff_model_ids:
                    _seq_key = (seq_key[0], seq_key[1], seq_key[2], m)

                    if _seq_key not in dist_violation_seq:
                        dist_violation_seq[_seq_key] = []

                    for rest_key in rest_keys:
                        err = self.__distRestViolDict[rest_key][m]

                        if err is None or err == 0.0:
                            continue

                        comb_key = self.__distRestViolCombKeyDict[rest_key][m]

                        if comb_key is None:
                            continue

                        atom_ids = set()
                        distance_type = None

                        for r in self.__distRestDictWithCombKey[rest_key][comb_key]:
                            seq_key_1 = (r['atom_key_1'][0], r['atom_key_1'][1], r['atom_key_1'][2])
                            seq_key_2 = (r['atom_key_2'][0], r['atom_key_2'][1], r['atom_key_2'][2])

                            if seq_key not in (seq_key_1, seq_key_2):
                                if self.__verbose and comb_key[0] is None and comb_key[1] is None:
                                    self.__lfh.write(f"Nothing matches with sequence, {seq_key_1}, {seq_key_2}, {seq_key}\n")
                                continue

                            if seq_key_1 == seq_key_2:
                                atom_ids.add(r['atom_key_1'][3])
                                atom_ids.add(r['atom_key_2'][3])
                            elif seq_key_1 == seq_key:
                                atom_ids.add(r['atom_key_1'][3])
                            else:
                                atom_ids.add(r['atom_key_2'][3])

                            if distance_type is None:
                                distance_type = r['distance_type']
                                distance_sub_type = r['distance_sub_type']
                                bond_flag = r['bond_flag']

                        dist_violation_seq[_seq_key].append([rest_key[0],
                                                             rest_key[1],
                                                             sorted(list(atom_ids)),
                                                             distance_type,
                                                             distance_sub_type,
                                                             bond_flag,
                                                             err])

            self.__results['dist_violation_seq'] = dist_violation_seq

            return True

        except Exception as e:
            self.__lfh.write(f"Exception occurred while processing {os.path.basename(self.__cifPath)} and {os.path.basename(self.__nmrDataPath)}\n")
            self.__lfh.write(f"+{self.__class_name__}.__summarizeDistanceRestraintAnalysis() ++ Error  - {str(e)}\n")

        return False

    def __summarizeDihedralAngleRestraintAnalysis(self) -> bool:
        """ Summarize dihedral angle restraint analysis results.
            @author: Masashi Yokochi
            @note: Derived from wwpdb.apps.validation.src.RestraintValidation.BMRBRestraintsAnalysis.generate_output,
                   written by Kumaran Baskaran
            @change: class method, improve readability of restraints, support combinational restraints, performance optimization
        """

        if self.__has_prev_results:
            return True

        try:

            self.__results['angle'] = self.__dihedRestViolDict is not None and len(self.__dihedRestViolDict) > 0
            self.__results['error_message_angle'] = None

            if not self.__results['angle']:
                return True

            self.__results['angle_seq_dict'] = self.__dihedRestSeqDict
            self.__results['unmapped_angle'] = self.__dihedRestUnmapped

            any_type = 'Total'

            try:
                angle_type_set = set()
                for r_list in self.__dihedRestDict.values():
                    for r in r_list:
                        angle_type_set.add(r['angle_type'])
                angle_type = list(angle_type_set) + [any_type]
            except IndexError:
                self.__lfh.write(f"Dihedral angle analysis failed due to data error in the dihedral angle restraints. {self.__dihedRestDict.values()}\n")
                self.__results['error_message_angle'] = 'Dihedral angle analysis failed due to data error in the dihedral angle restraints, possibly missing target value'
                self.__results['angle'] = False
                return True

            self.__results['key_lists']['angle_type'] = angle_type

            angle_summary, angle_violation = {}, {}

            consistent_angle_violation, angle_violations_vs_models, angle_violations_in_models =\
                {}, {}, {}

            for m in self.__eff_model_ids:
                angle_violations_in_models[m] = {}

                for t in angle_type:
                    angle_summary[t] = 0
                    angle_violation[t] = 0
                    consistent_angle_violation[t] = 0
                    angle_violations_vs_models[t] = [0] * (self.__total_models + 1)
                    angle_violations_in_models[m][t] = []

            for rest_key, restraints in self.__dihedRestDict.items():
                r = restraints[0]

                t = r['angle_type']

                angle_summary[t] += 1
                angle_summary[any_type] += 1

                len_vm = len(get_violated_model_ids(self.__dihedRestViolDict[rest_key]))

                if len_vm > 0:
                    angle_violation[t] += 1
                    angle_violation[any_type] += 1

                if len_vm == self.__total_models:
                    consistent_angle_violation[t] += 1
                    consistent_angle_violation[any_type] += 1

                angle_violations_vs_models[t][len_vm] += 1
                angle_violations_vs_models[any_type][len_vm] += 1

            self.__results['angle_summary'] = angle_summary
            self.__results['angle_violation'] = angle_violation
            self.__results['consistent_angle_violation'] = consistent_angle_violation
            self.__results['angle_violations_vs_models'] = angle_violations_vs_models

            for rest_key, viol_per_model in self.__dihedRestViolDict.items():
                for m in self.__eff_model_ids:
                    err = viol_per_model[m]

                    if err is None or err == 0.0:
                        continue

                    comb_key = self.__dihedRestViolCombKeyDict[rest_key][m]

                    if comb_key is None:
                        continue

                    r = self.__dihedRestDictWithCombKey[rest_key][comb_key][0]

                    t = r['angle_type']

                    angle_violations_in_models[m][t].append(err)
                    angle_violations_in_models[m][any_type].append(err)

            self.__results['angle_violations_in_models'] = angle_violations_in_models

            angle_range = []

            residual_angle_violation = {}
            for idx, beg_err_bin in enumerate(NMR_VTF_DIHED_ERR_BINS):
                if idx == len(NMR_VTF_DIHED_ERR_BINS) - 1:
                    end_err_bin = None
                    dihed_err_range = f">{beg_err_bin}"
                else:
                    end_err_bin = NMR_VTF_DIHED_ERR_BINS[idx + 1]
                    dihed_err_range = f"{beg_err_bin}-{end_err_bin}"

                angle_range.append(dihed_err_range)
                residual_angle_violation[dihed_err_range] =\
                    get_violation_statistics_for_each_bin(beg_err_bin, end_err_bin,
                                                          self.__total_models,
                                                          self.__eff_model_ids,
                                                          self.__dihedRestViolDict)

            self.__results['key_lists']['angle_range'] = angle_range
            self.__results['residual_angle_violation'] = residual_angle_violation

            most_violated_angle = []
            for rest_key, viol_per_model in self.__dihedRestViolDict.items():
                vm = get_violated_model_ids(viol_per_model)

                if len(vm) > 1:
                    e = np.array([err for err in viol_per_model.values() if err is not None and err > 0.0])

                    comb_keys = []
                    for _m in set(vm):
                        comb_key = self.__dihedRestViolCombKeyDict[rest_key][_m]

                        if comb_key is None:
                            continue

                        if comb_key not in comb_keys:
                            comb_keys.append(comb_key)

                    for comb_key in comb_keys:
                        for r in self.__dihedRestDictWithCombKey[rest_key][comb_key]:
                            most_violated_angle.append([rest_key,
                                                        r['atom_key_1'],
                                                        r['atom_key_2'],
                                                        r['atom_key_3'],
                                                        r['atom_key_4'],
                                                        r['angle_type'],
                                                        len(vm),
                                                        vm,
                                                        np.min(e),
                                                        np.max(e),
                                                        np.mean(e),
                                                        np.std(e),
                                                        np.median(e)])

            self.__results['most_violated_angle'] =\
                sorted(most_violated_angle, reverse=True, key=itemgetter(6, 10))

            all_angle_violations = []
            for rest_key, viol_per_model in self.__dihedRestViolDict.items():
                for m in self.__eff_model_ids:
                    err = viol_per_model[m]

                    if err is None or err == 0.0:
                        continue

                    comb_key = self.__dihedRestViolCombKeyDict[rest_key][m]

                    if comb_key is None:
                        continue

                    for r in self.__dihedRestDictWithCombKey[rest_key][comb_key]:
                        all_angle_violations.append([rest_key,
                                                    r['atom_key_1'],
                                                    r['atom_key_2'],
                                                    r['atom_key_3'],
                                                    r['atom_key_4'],
                                                    m,
                                                    r['angle_type'],
                                                    err])

            self.__results['all_angle_violations'] =\
                sorted(all_angle_violations, reverse=True, key=itemgetter(7, 0))

            angle_violation_seq = {}
            for seq_key, rest_keys in self.__dihedRestSeqDict.items():
                for m in self.__eff_model_ids:
                    _seq_key = (seq_key[0], seq_key[1], seq_key[2], m)

                    if _seq_key not in angle_violation_seq:
                        angle_violation_seq[_seq_key] = []

                    for rest_key in rest_keys:
                        err = self.__dihedRestViolDict[rest_key][m]

                        if err is None or err == 0.0:
                            continue

                        comb_key = self.__dihedRestViolCombKeyDict[rest_key][m]

                        if comb_key is None:
                            continue

                        atom_ids_1, atom_ids_2, atom_ids_3, atom_ids_4 = [], [], [], []
                        angle_type = None

                        for r in self.__dihedRestDictWithCombKey[rest_key][comb_key]:
                            seq_key_1 = (r['atom_key_1'][0], r['atom_key_1'][1], r['atom_key_1'][2])
                            if seq_key_1 == seq_key:
                                atom_ids_1.append(r['atom_key_1'][3])
                            seq_key_2 = (r['atom_key_2'][0], r['atom_key_2'][1], r['atom_key_2'][2])
                            if seq_key_2 == seq_key:
                                atom_ids_2.append(r['atom_key_2'][3])
                            seq_key_3 = (r['atom_key_3'][0], r['atom_key_3'][1], r['atom_key_3'][2])
                            if seq_key_3 == seq_key:
                                atom_ids_3.append(r['atom_key_3'][3])
                            seq_key_4 = (r['atom_key_4'][0], r['atom_key_4'][1], r['atom_key_4'][2])
                            if seq_key_4 == seq_key:
                                atom_ids_4.append(r['atom_key_4'][3])

                            if angle_type is None:
                                angle_type = r['angle_type']

                        atom_ids = list(set(atom_ids_1))
                        atom_ids.extend(list(set(atom_ids_2)))
                        atom_ids.extend(list(set(atom_ids_3)))
                        atom_ids.extend(list(set(atom_ids_4)))

                        angle_violation_seq[_seq_key].append([rest_key[0],
                                                              rest_key[1],
                                                              atom_ids,
                                                              angle_type,
                                                              err])

            self.__results['angle_violation_seq'] = angle_violation_seq

            return True

        except Exception as e:
            self.__lfh.write(f"Exception occurred while processing {os.path.basename(self.__cifPath)} and {os.path.basename(self.__nmrDataPath)}\n")
            self.__lfh.write(f"+{self.__class_name__}.__summarizeDihedralAngleRestraintAnalysis() ++ Error  - {str(e)}\n")

        return False

    def __summarizeRdcRestraintAnalysis(self) -> bool:
        """ Summarize RDC restraint analysis results.
            @author: Masashi Yokochi
        """

        if self.__has_prev_results:
            return True

        try:

            self.__results['rdc'] = self.__rdcRestViolDict is not None and len(self.__rdcRestViolDict) > 0
            self.__results['error_message_rdc'] = None

            if not self.__results['rdc']:
                return True

            self.__results['rdc_seq_dict'] = self.__rdcRestSeqDict
            self.__results['unmapped_rdc'] = self.__rdcRestUnmapped

            any_type = 'Total'

            try:
                rdc_type_set = set()
                for r_list in self.__rdcRestDict.values():
                    for r in r_list:
                        rdc_type_set.add(r['rdc_type'])
                rdc_type = list(rdc_type_set) + [any_type]
            except IndexError:
                self.__lfh.write(f"RDC analysis failed due to data error in the RDC restraints. {self.__rdcRestDict.values()}\n")
                self.__results['error_message_rdc'] = 'RDC analysis failed due to data error in the RDC angle restraints'
                self.__results['rdc'] = False
                return True

            self.__results['key_lists']['rdc_type'] = rdc_type

            rdc_summary, rdc_violation = {}, {}

            consistent_rdc_violation, rdc_violations_vs_models, rdc_violations_in_models =\
                {}, {}, {}

            for m in self.__eff_model_ids:
                rdc_violations_in_models[m] = {}

                for t in rdc_type:
                    rdc_summary[t] = 0
                    rdc_violation[t] = 0
                    consistent_rdc_violation[t] = 0
                    rdc_violations_vs_models[t] = [0] * (self.__total_models + 1)
                    rdc_violations_in_models[m][t] = []

            for rest_key, restraints in self.__rdcRestDict.items():
                r = restraints[0]

                t = r['rdc_type']

                rdc_summary[t] += 1
                rdc_summary[any_type] += 1

                len_vm = len(get_violated_model_ids(self.__rdcRestViolDict[rest_key]))

                if len_vm > 0:
                    rdc_violation[t] += 1
                    rdc_violation[any_type] += 1

                if len_vm == self.__total_models:
                    consistent_rdc_violation[t] += 1
                    consistent_rdc_violation[any_type] += 1

                rdc_violations_vs_models[t][len_vm] += 1
                rdc_violations_vs_models[any_type][len_vm] += 1

            self.__results['rdc_summary'] = rdc_summary
            self.__results['rdc_violation'] = rdc_violation
            self.__results['consistent_rdc_violation'] = consistent_rdc_violation
            self.__results['rdc_violations_vs_models'] = rdc_violations_vs_models

            for rest_key, viol_per_model in self.__rdcRestViolDict.items():
                for m in self.__eff_model_ids:
                    err = viol_per_model[m]

                    if err is None or err == 0.0:
                        continue

                    comb_key = self.__rdcRestViolCombKeyDict[rest_key][m]

                    if comb_key is None:
                        continue

                    r = self.__rdcRestDictWithCombKey[rest_key][comb_key][0]

                    t = r['rdc_type']

                    rdc_violations_in_models[m][t].append(err)
                    rdc_violations_in_models[m][any_type].append(err)

            self.__results['rdc_violations_in_models'] = rdc_violations_in_models

            rdc_range = []

            residual_rdc_violation = {}
            for idx, beg_err_bin in enumerate(NMR_VTF_RDC_ERR_BINS):
                if idx == len(NMR_VTF_RDC_ERR_BINS) - 1:
                    end_err_bin = None
                    rdc_err_range = f">{beg_err_bin}"
                else:
                    end_err_bin = NMR_VTF_RDC_ERR_BINS[idx + 1]
                    rdc_err_range = f"{beg_err_bin}-{end_err_bin}"

                rdc_range.append(rdc_err_range)
                residual_rdc_violation[rdc_err_range] =\
                    get_violation_statistics_for_each_bin(beg_err_bin, end_err_bin,
                                                          self.__total_models,
                                                          self.__eff_model_ids,
                                                          self.__rdcRestViolDict)

            self.__results['key_lists']['rdc_range'] = rdc_range
            self.__results['residual_rdc_violation'] = residual_rdc_violation

            most_violated_rdc = []
            for rest_key, viol_per_model in self.__rdcRestViolDict.items():
                vm = get_violated_model_ids(viol_per_model)

                if len(vm) > 1:
                    e = np.array([err for err in viol_per_model.values() if err is not None and err > 0.0])

                    comb_keys = []
                    for _m in set(vm):
                        comb_key = self.__rdcRestViolCombKeyDict[rest_key][_m]

                        if comb_key is None:
                            continue

                        if comb_key not in comb_keys:
                            comb_keys.append(comb_key)

                    for comb_key in comb_keys:
                        for r in self.__rdcRestDictWithCombKey[rest_key][comb_key]:
                            most_violated_rdc.append([rest_key,
                                                      r['atom_key_1'],
                                                      r['atom_key_2'],
                                                      r['rdc_type'],
                                                      len(vm),
                                                      vm,
                                                      np.min(e),
                                                      np.max(e),
                                                      np.mean(e),
                                                      np.std(e),
                                                      np.median(e)])

            self.__results['most_violated_rdc'] =\
                sorted(most_violated_rdc, reverse=True, key=itemgetter(4, 8))

            all_rdc_violations = []
            for rest_key, viol_per_model in self.__rdcRestViolDict.items():
                for m in self.__eff_model_ids:
                    err = viol_per_model[m]

                    if err is None or err == 0.0:
                        continue

                    comb_key = self.__rdcRestViolCombKeyDict[rest_key][m]

                    if comb_key is None:
                        continue

                    for r in self.__rdcRestDictWithCombKey[rest_key][comb_key]:
                        all_rdc_violations.append([rest_key,
                                                  r['atom_key_1'],
                                                  r['atom_key_2'],
                                                  m,
                                                  r['rdc_type'],
                                                  err])

            self.__results['all_rdc_violations'] =\
                sorted(all_rdc_violations, reverse=True, key=itemgetter(5, 0))

            rdc_violation_seq = {}
            for seq_key, rest_keys in self.__rdcRestSeqDict.items():
                for m in self.__eff_model_ids:
                    _seq_key = (seq_key[0], seq_key[1], seq_key[2], m)

                    if _seq_key not in rdc_violation_seq:
                        rdc_violation_seq[_seq_key] = []

                    for rest_key in rest_keys:
                        err = self.__rdcRestViolDict[rest_key][m]

                        if err is None or err == 0.0:
                            continue

                        comb_key = self.__rdcRestViolCombKeyDict[rest_key][m]

                        if comb_key is None:
                            continue

                        atom_ids_1, atom_ids_2 = [], []
                        rdc_type = None

                        for r in self.__rdcRestDictWithCombKey[rest_key][comb_key]:
                            seq_key_1 = (r['atom_key_1'][0], r['atom_key_1'][1], r['atom_key_1'][2])
                            if seq_key_1 == seq_key:
                                atom_ids_1.append(r['atom_key_1'][3])
                            seq_key_2 = (r['atom_key_2'][0], r['atom_key_2'][1], r['atom_key_2'][2])
                            if seq_key_2 == seq_key:
                                atom_ids_2.append(r['atom_key_2'][3])

                            if rdc_type is None:
                                rdc_type = r['rdc_type']

                        atom_ids = list(set(atom_ids_1))
                        atom_ids.extend(list(set(atom_ids_2)))

                        rdc_violation_seq[_seq_key].append([rest_key[0],
                                                            rest_key[1],
                                                            atom_ids,
                                                            rdc_type,
                                                            err])

            self.__results['rdc_violation_seq'] = rdc_violation_seq

            return True

        except Exception as e:
            self.__lfh.write(f"Exception occurred while processing {os.path.basename(self.__cifPath)} and {os.path.basename(self.__nmrDataPath)}\n")
            self.__lfh.write(f"+{self.__class_name__}.__summarizeRdcRestraintAnalysis() ++ Error  - {str(e)}\n")

        return False

    def __outputResultsAsPickleFileIfPossible(self) -> bool:
        """ Output results if 'result_pickle_file_path' was set in output parameter.
        """

        if self.__use_cache:

            cache_path = None
            if self.__resultsCacheName is not None:
                cache_path = os.path.join(self.__cacheDirPath, self.__resultsCacheName)

                if not os.path.exists(cache_path):
                    write_as_pickle(self.__results, cache_path)

            if 'result_pickle_file_path' in self.__outputParamDict:
                pickle_file = self.__outputParamDict['result_pickle_file_path']

                if cache_path is None:
                    write_as_pickle(self.__results, pickle_file)
                    return True

                try:

                    if os.path.exists(pickle_file):
                        os.remove(pickle_file)

                    os.symlink(cache_path, pickle_file)

                except OSError:
                    pass

        elif 'result_pickle_file_path' in self.__outputParamDict:
            pickle_file = self.__outputParamDict['result_pickle_file_path']

            write_as_pickle(self.__results, pickle_file)

        return True
