##
# File: NEFTranslator.py
# Date:  02-May-2019  K. Baskaran
#
# Updates:
# 29-Jul-2019  M. Yokochi - support NEFTranslator v1.3.0 and integration into OneDep environment
# 28-Aug-2019  M. Yokochi - report all empty data error as UserWarning
# 11-Oct-2019  K. Baskaran & M. Yokochi - add functions to detect missing mandatory tag (v1.4.0)
# 05-Nov-2019  M. Yokochi - revise error messages for missing mandatory saveframe/loop tags
# 28-Nov-2019  M. Yokochi - implement bi-directional translation, which enables to convert NMR-STAR to NEF (v2.0.0)
# 29-Nov-2019  M. Yokochi - support index pointer from loop to their parent saveframe in NMR-STAR (v2.0.1)
# 11-Dec-2019  M. Yokochi - relax 'smaller-than' and 'larger-than' constraints, which include 'equal-to' constraint (v2.0.2)
# 05-Feb-2020  M. Yokochi - add 'circular-shift' to relax dihedral angle constraint range error (v2.0.3)
# 05-Feb-2020  M. Yokochi - convert 'HN' in amino acids to 'H' while NEF->NMR-STAR translation (v2.0.3)
# 05-Feb-2020  M. Yokochi - rescue NEF atom_id w/o wild card notation in methyl group (v2.0.3)
# 05-Feb-2020  M. Yokochi - relax NEF atom_id that ends with [xy] in methyne/methyl group (v2.0.3)
# 26-Feb-2020  M. Yokochi - additional support for abnormal NEF atom nomenclature, e.g. HDy% in ASN, HEy% in GLN, seen in CCPN_2mtv_docr.nef (v2.0.4)
# 04-Mar-2020  M. Yokochi - support 'default' of key items and 'default-from' of data items (v2.0.4)
# 05-Mar-2020  M. Yokochi - support alternative enumeration definition, 'enum-alt' (v2.0.5, DAOTHER-5485)
# 05-Mar-2020  M. Yokochi - bidirectional convert between restraint_origin (NEF) and Content_type (NMR-STAR) (v2.0.6, DAOTHER-5485)
# 06-Mar-2020  M. Yokochi - fix ambiguity_code mapping from NEF atom nomenclature (v2.0.7)
# 17-Mar-2020  M. Yokochi - fill default value for mandatory saveframe tag (v2.0.8, DAOTHER-5508)
# 18-Mar-2020  M. Yokochi - convert NEF atom nomenclature in dihedral angle/RDC restraint (v2.0.9)
# 18-Mar-2020  M. Yokochi - remove invalid NMR-STAR's Details tag in restraint (v2.0.9)
# 03-Apr-2020  M. Yokochi - remove dependency of lib/atomDict.json and lib/codeDict.json (v2.1.0)
# 03-Apr-2020  M. Yokochi - fill _Atom_chem_shift.Original_PDB_* items (v2.1.0)
# 03-Apr-2020  M. Yokochi - synchronize with coordinates' auth_asym_id and auth_seq_id for NEF deposition (v2.2.0)
# 06-Apr-2020  M. Yokochi - fix crash when sequence alignment is not available. (v2.2.1)
# 10-Apr-2020  M. Yokochi - fix crash in case of format issue (v2.2.2)
# 10-Apr-2020  M. Yokochi - fix typo in alternative enumeration definition (v2.2.2)
# 22-Apr-2020  M. Yokochi - convert comp_id in capital letters (v2.2.3, DAOTHER-5600)
# 22-Apr-2020  M. Yokochi - fix None type object is not iterable error (v2.2.4, DAOTHER-5602)
# 24-Apr-2020  M. Yokochi - fix type mismatch if 'default' value is set (v2.2.5, DAOTHER-5609)
# 24-Apr-2020  M. Yokochi - fix type mismatch if 'default-from' is 'self' (v2.2.5, DAOTHER-5609)
# 24-Apr-2020  M. Yokochi - revise error message in validate_file() (v2.2.6, DAOTHER-5611)
# 25-Apr-2020  M. Yokochi - add 'excl_missing_data' option of check_data() for NMR separated deposition (v2.2.7, DAOTHER-5611)
# 25-Apr-2020  M. Yokochi - fill default value if Entity_assembly_ID is blank (v2.2.8, DAOTHER-5611)
# 28-Apr-2020  M. Yokochi - do not throw ValueError for 'range-float' data type (v2.2.9, DAOTHER-5611)
# 28-Apr-2020  M. Yokochi - extract sequence from CS/MR loop with gap (v2.2.10, DAOTHER-5611)
# 29-Apr-2020  M. Yokochi - support diagnostic message of PyNMRSTAR v2.6.5.1 or later (v2.2.11, DAOTHER-5611)
# 30-Apr-2020  M. Yokochi - fix pseudo atom mapping in ligand (v2.2.12, DAOTHER-5611)
# 14-May-2020  M. Yokochi - revise error message for missing mandatory content (v2.2.13, DAOTHER-5681 and 5682)
# 06-Jun-2020  M. Yokochi - be compatible with pynmrstar v3 (v2.3.0, DAOTHER-5765)
# 19-Jun-2020  M. Yokochi - do not generate invalid restraints include self atom (v2.3.1)
# 26-Jun-2020  M. Yokochi - support bidirectional conversion between _nef_covalent_links and _Bond (v2.4.0)
# 30-Jun-2020  M. Yokochi - skip third party loops and items gracefully (v2.5.0, DAOTHER-5896)
# 30-Jun-2020  M. Yokochi - support bidirectional conversion between _nef_peak and _Peak_row_format (v2.5.0, DAOTHER-5896)
# 08-Jul-2020  M. Yokochi - add support for _Gen_dist_constraint.Distance_val, _RDC_constraint.RDC_val, and _RDC_constraint.RDC_val_err (v2.6.0, DAOTHER-5926)
# 17-Aug-2020  M. Yokochi - add support for residue variant (v2.7.0, DAOTHER-5906)
# 14-Sep-2020  M. Yokochi - add support for pseudo atom in NMR-STAR (v2.8.0, DAOTHER-6128)
# 17-Sep-2020  M. Yokochi - do not convert atom name between NEF and NMR-STAR, which ends with apostrophe (v2.8.0, DAOTHER-6128)
# 18-Sep-2020  M. Yokochi - bug fix release for negative sequence numbers (v2.8.1, DAOTHER-6128)
# 28-Sep-2020  M. Yokochi - fix chain_code mapping in NEF MR loops in case that there is no CS assignment (v2.8.2, DAOTHER-6128)
# 29-Sep-2020  M. Yokochi - sort numeric string in a list of chain_id while NMR-STAR to NEF conversion (v2.8.3, DAOTHER-6128)
# 06-Sep-2020  M. Yokochi - improve stability against the presence of undefined chain_id in loops (v2.8.4, DAOTHER-6128)
# 12-Oct-2020  M. Yokochi - add support for spectral peak conversion from NMR-STAR canonical loops to NEF (v2.9.0, DAOTHER-6128)
# 11-Nov-2020  M. Yokochi - fix crash while translation due to invalid seq_id (v2.9.1)
# 11-Nov-2020  M. Yokochi - append _nef_sequence.index even if _Chem_comp_assembly.NEF_index does not exist (v2.9.2, DAOTHER-6128)
# 19-Nov-2020  M. Yokochi - add support for HEM, HEB, HEC methyl groups (v2.9.3, DAOTHER-6366)
# 25-Jan-2021  M. Yokochi - add 'positive-int-as-str' value type to simplify code for Entity_assembly_ID, and chain_code (v2.9.4)
# 04-Feb-2021  M. Yokochi - support 3 letter chain code (v2.9.5, DAOTHER-5896, DAOTHER-6128, BMRB entry: 16812, PDB ID: 6kae)
# 10-Mar-2021  M. Yokochi - block NEF deposition missing '_nef_sequence' category and turn off salvage routine for the case (v2.9.6, DAOTHER-6694)
# 10-Mar-2021  M. Yokochi - add support for audit loop in NEF (v2.9.7, DAOTHER-6327)
# 25-Mar-2021  M. Yokochi - fix crash during NMR-STAR to NEF atom name conversion (v2.9.8, DAOTHER-6128,
#                           bmrb_id: 15879, pdb_id: 2k6r, comp_id: DNS, nef_atom_id: Hx%, Hy% point to [H11A, H12, H13],
#                           [H21, H22, H23], respectively, but SHOULD NOT to H10, H11, H[ABCDE][23])
# 14-May-2021  M. Yokochi - add support for PyNMRSTAR v3.1.1 (DAOTHER-6693)
# 14-May-2021  M. Yokochi - remove empty loop for Entity_deleted_atom category in NMR-STAR to NEF conversion (v2.10.0)
# 23-Jun-2021  M. Yokochi - fix error in handling lower/upper linear limits (v2.10.1, DAOTHER-6963)
# 28-Jun-2021  M. Yokochi - revise error message for sequence mismatch in a loop (v2.10.2, DAOTHER-7103)
# 29-Jun-2021  M. Yokochi - add support for PyNMRSTAR v3.2.0 (v2.10.3, DAOTHER-7107)
# 16-Sep-2021  M. Yokochi - report an empty loop case of CS/MR data as an error (v2.10.4, D_1292117503, DAOTHER-7318)
# 13-Oct-2021  M. Yokochi - code revision according to PEP8 using Pylint (v2.11.0, DAOTHER-7389, issue #5)
# 14-Oct-2021  M. Yokochi - remove unassigned chemical shifts, clear incompletely assigned spectral peaks (v2.11.1, DAOTHER-7389, issue #3)
# 19-Oct-2021  M. Yokochi - add NMR-STAR format normalizer for conventional CS deposition using a single file (v3.0.0, DAOTHER-7344, 7355, 7389 issue #4, 7407)
# 27-Oct-2021  M. Yokochi - utilize Auth_asym_ID* tag for chain_id if Entity_assembly_ID* is not available (v3.0.1, DAOTHER-7421)
# 28-Oct-2021  M. Yokochi - use simple dictionary for return messaging, instead of JSON dump/load (v3.0.2)
# 28-Oct-2021  M. Yokochi - resolve case-insensitive saveframe name collision for CIF (v3.0.3, DAOTHER-7389, issue #4)
# 16-Nov-2021  M. Yokochi - map alphabet code of Entity_assembly_ID to valid integer (v3.0.4, DAOTHER-7475)
# 13-Dec-2021  M. Yokochi - fill list id (e.g. Assigned_chem_shift_list_ID) using a given saveframe counter (parent_pointer) just in case (v3.0.5, DAOTHER-7465, issue #2)
# 15-Dec-2021  M. Yokochi - fix TypeError: unsupported operand type(s) for -: 'NoneType' and 'set' (v3.0.6, DAOTHER-7545)
# 22-Dec-2021  M. Yokochi - extend validate_file() for uploading NMR restraint files in NMR-STAR format (v3.0.7, DAOTHER-7545, issue #2)
# 02-Mar-2022  M. Yokochi - revise logging and overall code revision (v3.1.0)
# 12-Apr-2022  M. Yokochi - add get_valid_star_atom_in_xplor(), which translates XPLOR atom name to IUPAC one (v3.1.1, NMR restraint remediation, DAOTHER-7407)
# 13-Apr-2022  M. Yokochi - use auth_*_id scheme preferentially in combined format translation (v3.1.2, NMR restraint remediation)
# 02-May-2022  M. Yokochi - remediate inconsistent _Atom_chem_shift.Comp_index_ID tag values in reference to _Atom_chem_shift.Seq_ID (v3.1.3, NMR restraint remediation)
# 04-Jul-2022  M. Yokochi - add support for old XPLOR atom nomenclature, e.g. 1HB (v3.1.4, NMR restraint remediation)
# 01-Sep-2022  M. Yokochi - fix NEF atom name conversion for excess wild card (v3.1.5, NMR restraint remediation)
# 09-Sep-2022  M. Yokochi - add support for NEF atom name conversion starting with wild card, e.g. '%HN' (v3.2.0, NMR restraint remediation)
# 20-Oct-2022  M. Yokochi - allow missing distance restraints via allow_missing_dist_restraint(bool) (v3.2.1, DAOTHER-8088 1.b, 8108)
# 16-Dec-2022  M. Yokochi - remove deprecated functions with minor code revisions (v3.2.2)
# 27-Feb-2023  M. Yokochi - preserve author sequence scheme of the coordinates during NMR-STAR to NEF conversion (v3.2.3)
# 13-Mar-2023  M. Yokochi - preserve the original atom nomenclature of NMR restraints into Auth_atom_name_* data items (v3.4.0)
# 13-Sep-2023  M. Yokochi - fix/improve NEF atom nomenclature mapping (v3.5.0, DAOTHER-8817)
# 02-Oct-2023  M. Yokochi - do not reorganize _Gen_dist_constraint.ID (v3.5.1, DAOTHER-8855)
# 11-Jun-2024  M. Yokochi - add support for ligand remapping in annotation process (v3.6.0, DAOTHER-9286)
# 28-Jun-2024  M. Yokochi - do not evaluate value in case of ValueError exception (v3.6.1, DAOTHER-9520)
# 28-Jun-2024  M. Yokochi - throw error for key items with empty value (v3.6.2, DAOTHER-9520, 2nd case)
# 03-Jul-2024  M. Yokochi - convert protonated DC/C residue to valid DNR/CH respectively because of existence of H3/H3+ assignment (v3.6.3)
# 08-Aug-2024  M. Yokochi - remove deprecated function (star_data_to_nmrstar)
#                           remove dependency of CSV resource files (NEF_NMRSTAR_equivalence.csv, NEF_mandatory.csv, NMR-STAR_mandatory.csv) (v4.0.0)
# 08-Aug-2024  M. Yokochi - conform to the NEF specification 3.3 (sf_framecode must start with sf_category) and
#                           preserve the original NMR-STAR frame codes provided by author through bidirectional conversion (v4.0.0, DAOTHER-9623)
# 28-Nov-2024  M. Yokochi - drop support for old pynmrstar versions less than 3.2 (v4.1.0)
# 27-Dec-2024  M. Yokochi - change class path and visibility of class method (v4.1.1)
# 19-Feb-2025  M. Yokochi - try to extract sequence using Seq_ID_# tags if necessary (v4.2.0)
# 12-Mar-2025  M. Yokochi - allow to reset auth_seq_id of cs loop if necessary (v4.3.0, DAOTHER-9927)
# 09-Apr-2025  M. Yokochi - allow missing of chemical shift loop for standalone NMR data conversion service (v4.4.0, DAOTHER-9785)
# 23-May-2025  M. Yokochi - resolve pseudo atom name of non-standard residue based on local CCD derived from the coordinated (v4.5.0, DAOTHER-10105)
##
""" Bi-directional translator between NEF and NMR-STAR
    @author: Kumaran Baskaran, Masashi Yokochi
"""
__docformat__ = "restructuredtext en"
__author__ = "Masashi Yokochi, Kumaran Baskaran"
__email__ = "yokochi@protein.osaka-u.ac.jp, baskaran@uchc.edu"
__license__ = "Apache License 2.0"
__version__ = "4.7.0"

import sys
import os
import ntpath
import logging
import re
import io
# import csv
import itertools
import copy
import pynmrstar
import collections

from packaging import version
from operator import itemgetter
from typing import IO, List, Tuple, Union, Optional

from wwpdb.utils.align.alignlib import PairwiseAlign  # pylint: disable=no-name-in-module

try:
    from wwpdb.utils.nmr.AlignUtil import (LEN_LARGE_ASYM_ID,
                                           LOW_SEQ_COVERAGE,
                                           emptyValue,
                                           trueValue,
                                           monDict3,
                                           protonBeginCode,
                                           pseProBeginCode,
                                           aminoProtonCode,
                                           dnrParentCode,
                                           chParentCode,
                                           letterToDigit,
                                           indexToLetter,
                                           alignPolymerSequence,
                                           alignPolymerSequenceWithConflicts,
                                           assignPolymerSequence)
    from wwpdb.utils.nmr.ChemCompUtil import ChemCompUtil
    from wwpdb.utils.nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from wwpdb.utils.nmr.CifToNmrStar import (CifToNmrStar,
                                              get_first_sf_tag)
    from wwpdb.utils.nmr.mr.ParserListenerUtil import (ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS,
                                                       ALLOWED_AMBIGUITY_CODES,
                                                       translateToStdResName,
                                                       translateToStdAtomName,
                                                       isLikePheOrTyr)
except ImportError:
    from nmr.AlignUtil import (LEN_LARGE_ASYM_ID,
                               LOW_SEQ_COVERAGE,
                               emptyValue,
                               trueValue,
                               monDict3,
                               protonBeginCode,
                               pseProBeginCode,
                               aminoProtonCode,
                               dnrParentCode,
                               chParentCode,
                               letterToDigit,
                               indexToLetter,
                               alignPolymerSequence,
                               alignPolymerSequenceWithConflicts,
                               assignPolymerSequence)
    from nmr.ChemCompUtil import ChemCompUtil
    from nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from nmr.CifToNmrStar import (CifToNmrStar,
                                  get_first_sf_tag)
    from nmr.mr.ParserListenerUtil import (ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS,
                                           ALLOWED_AMBIGUITY_CODES,
                                           translateToStdResName,
                                           translateToStdAtomName,
                                           isLikePheOrTyr)


__package_name__ = 'wwpdb.utils.nmr'

__pynmrstar_v3_3_1__ = version.parse(pynmrstar.__version__) >= version.parse("3.3.1")

if __pynmrstar_v3_3_1__:
    logger = logging.getLogger('pynmrstar')
    logger.setLevel(logging.ERROR)
else:
    logging.getLogger().setLevel(logging.ERROR)  # set level for pynmrstar


# supported NEF dictionary version
NEF_VERSION = '1.1'

# supported NMR-STAR dictionary version
NMR_STAR_VERSION = '3.2.6.0'

# format name
NEF_FORMAT_NAME = 'nmr_exchange_format'

# NEF boolean values
NEF_BOOLEAN_VALUES = ('true', 'false')

# NMR-STAR boolean values
STAR_BOOLEAN_VALUES = ('yes', 'no')


# paramagnetic elements, except for Oxygen
PARAMAGNETIC_ELEMENTS = ('LI', 'NA', 'MG', 'AL', 'K', 'CA', 'SC', 'TI', 'V', 'MN', 'RB', 'SR',
                         'Y', 'ZR', 'NB', 'MO', 'TC', 'RU', 'RH', 'PD', 'SN', 'CS', 'BA', 'LA',
                         'CE', 'PR', 'ND', 'PM', 'SM', 'EU', 'GD', 'TB', 'DY', 'HO', 'ER', 'TM',
                         'YB', 'LU', 'HF', 'TA', 'W', 'RE', 'OS', 'IR', 'PT', 'FR', 'RA', 'AC')

# ferromagnetic elements
FERROMAGNETIC_ELEMENTS = ('CR', 'FE', 'CO', 'NI')

# lanthanoid elements
LANTHANOID_ELEMENTS = ('LA', 'CE', 'PR', 'ND', 'PM', 'SM', 'EU', 'GD', 'TB', 'DY', 'HO', 'ER', 'TM', 'YB', 'LU')

# non-metal elements
NON_METAL_ELEMENTS = ('H', 'C', 'N', 'O', 'P', 'S', 'SE')


# limit number of dimensions
MAX_DIM_NUM_OF_SPECTRA = 16

# maximum number of rows to perform explicit redundancy check
MAX_ROWS_TO_PERFORM_REDUNDANCY_CHECK = 20000


# maximum number of rows to perform index order check
MAX_ROWS_TO_PERFORM_INDEX_ORDER_CHECK = 10000


# data items in _Entity_deleted_atom category of NMR-STAR
ENTITY_DELETED_ATOM_ITEMS = ('ID', 'Entity_assembly_ID', 'Comp_index_ID', 'Comp_ID', 'Atom_ID',
                             'Auth_entity_assembly_ID', 'Auth_seq_ID', 'Auth_comp_ID', 'Auth_atom_ID', 'Assembly_ID')


# integer pattern
intPattern = re.compile(r'^([+-]?[1-9]\d*|0)$')

# bad pattern
badPattern = re.compile(r'.*[\!\$\&\(\)\=\~\^\\\|\`\@\{\}\[\]\;\:\<\>\,\/].*')

# separator pattern
sepPattern = re.compile(r'[\&\\\|\;\:\,\/]')


# alternative dictionary of constraint type
altDistanceConstraintType = {'nef': {'NOE': 'noe',
                                     'NOE build-up': 'noe_build_up',
                                     'noe build-up': 'noe_build_up',
                                     'NOE buildup': 'noe_build_up',
                                     'noe buildup': 'noe_build_up',
                                     'NOE build up': 'noe_build_up',
                                     'noe build up': 'noe_build_up',
                                     'noe not seen': 'noe_not_seen',
                                     'ROE': 'roe',
                                     'roe build-up': 'roe_build_up',
                                     'ROE buildup': 'roe_build_up',
                                     'roe buildup': 'roe_build_up',
                                     'ROE build up': 'roe_build_up',
                                     'roe build up': 'roe_build_up',
                                     'hydrogen bond': 'hbond',
                                     'Hbond': 'hbond',
                                     'HBond': 'hbond',
                                     'H-bond': 'hbond',
                                     'h-bond': 'hbond',
                                     'H-Bond': 'hbond',
                                     'Hydrogen bond': 'hbond',
                                     'disulfide bond': 'disulfide_bond',
                                     'Disulfide bond': 'disulfide_bond',
                                     'S-S bond': 'disulfide_bond',
                                     'SS bond': 'disulfide_bond',
                                     'SS-bond': 'disulfide_bond',
                                     'disulfide bridge': 'disulfide_bond',
                                     'Disulfide bridge': 'disulfide_bond',
                                     'paramagnetic relaxation': 'pre',
                                     'PRE': 'pre',
                                     'Paramagnetic relaxation': 'pre',
                                     'paramagnetic relaxation enhancement': 'pre',
                                     'Paramagnetic relaxation enhancement': 'pre',
                                     'general distance': 'undefined',
                                     'distance': 'undefined',
                                     'Mutation': 'mutation',
                                     'chemical shift perturbation': 'shift_perturbation',
                                     'shift perturbation': 'shift_perturbation',
                                     'chem shift perturbation': 'shift_perturbation',
                                     'CS perturbation': 'shift_perturbation',
                                     'csp': 'shift_perturbation',
                                     'CSP': 'shift_perturbation'
                                     },
                             'nmr-star': {'noe': 'NOE',
                                          'noe_build_up': 'NOE build-up',
                                          'noe build-up': 'NOE build-up',
                                          'NOE buildup': 'NOE build-up',
                                          'noe buildup': 'NOE build-up',
                                          'NOE build up': 'NOE build-up',
                                          'noe build up': 'NOE build-up',
                                          'noe_not_seen': 'NOE not seen',
                                          'noe not seen': 'NOE not seen',
                                          'roe': 'ROE',
                                          'roe_build_up': 'ROE build-up',
                                          'roe build-up': 'ROE build-up',
                                          'ROE buildup': 'ROE build-up',
                                          'roe buildup': 'ROE build-up',
                                          'ROE build up': 'ROE build-up',
                                          'roe build up': 'ROE build-up',
                                          'hbond': 'hydrogen bond',
                                          'Hbond': 'hydrogen bond',
                                          'HBond': 'hydrogen bond',
                                          'H-bond': 'hydrogen bond',
                                          'h-bond': 'hydrogen bond',
                                          'H-Bond': 'hydrogen bond',
                                          'Hydrogen bond': 'hydrogen bond',
                                          'disulfide_bond': 'disulfide bond',
                                          'Disulfide bond': 'disulfide bond',
                                          'S-S bond': 'disulfide bond',
                                          'SS bond': 'disulfide bond',
                                          'SS-bond': 'disulfide bond',
                                          'disulfide bridge': 'disulfide bond',
                                          'Disulfide bridge': 'disulfide bond',
                                          'PRE': 'paramagnetic relaxation',
                                          'pre': 'paramagnetic relaxation',
                                          'Paramagnetic relaxation': 'paramagnetic relaxation',
                                          'paramagnetic relaxation enhancement': 'paramagnetic relaxation',
                                          'Paramagnetic relaxation enhancement': 'paramagnetic relaxation',
                                          'Mutation': 'mutation',
                                          'unknown': 'general distance',
                                          'undefined': 'general distance',
                                          'shift_perturbation': 'chemical shift perturbation',
                                          'shift perturbation': 'chemical shift perturbation',
                                          'chem shift perturbation': 'chemical shift perturbation',
                                          'CS perturbation': 'chemical shift perturbation',
                                          'csp': 'chemical shift perturbation',
                                          'CSP': 'chemical shift perturbation'
                                          }
                             }


altDihedralAngleConstraintType = {'nef': {'J-couplings': 'jcoupling',
                                          'j-couplings': 'jcoupling',
                                          'J couplings': 'jcoupling',
                                          'j couplings': 'jcoupling',
                                          'Jcouplings': 'jcoupling',
                                          'jcouplings': 'jcoupling',
                                          'J-coupling': 'jcoupling',
                                          'j-coupling': 'jcoupling',
                                          'J coupling': 'jcoupling',
                                          'j coupling': 'jcoupling',
                                          'Jcoupling': 'jcoupling',
                                          'chemical shift': 'chemical_shift',
                                          'Chemical shift': 'chemical_shift',
                                          'Chemical_shift': 'chemical_shift',
                                          'chemical shifts': 'chemical_shift',
                                          'Chemical shifts': 'chemical_shift',
                                          'Chemical_shifts': 'chemical_shift',
                                          'backbone chemical shifts': 'chemical_shift',
                                          'Backbone chemical shifts': 'chemical_shift',
                                          'Mainchain chemical shifts': 'chemical_shift',
                                          'mainchain chemical shifts': 'chemical_shift',
                                          'Main chain chemical shifts': 'chemical_shift',
                                          'main chain chemical shifts': 'chemical_shift',
                                          'bb chemical shifts': 'chemical_shift',
                                          'BB chemical shifts': 'chemical_shift',
                                          'backbone chemical shift': 'chemical_shift',
                                          'Backbone chemical shift': 'chemical_shift',
                                          'Mainchain chemical shift': 'chemical_shift',
                                          'mainchain chemical shift': 'chemical_shift',
                                          'Main chain chemical shift': 'chemical_shift',
                                          'main chain chemical shift': 'chemical_shift',
                                          'bb chemical shift': 'chemical_shift',
                                          'BB chemical shift': 'chemical_shift',
                                          'backbone chem shifts': 'chemical_shift',
                                          'Backbone chem shifts': 'chemical_shift',
                                          'Mainchain chem shifts': 'chemical_shift',
                                          'mainchain chem shifts': 'chemical_shift',
                                          'Main chain chem shifts': 'chemical_shift',
                                          'main chain chem shifts': 'chemical_shift',
                                          'bb chem shifts': 'chemical_shift',
                                          'BB chem shifts': 'chemical_shift',
                                          'backbone chem shift': 'chemical_shift',
                                          'Backbone chem shift': 'chemical_shift',
                                          'Mainchain chem shift': 'chemical_shift',
                                          'mainchain chem shift': 'chemical_shift',
                                          'Main chain chem shift': 'chemical_shift',
                                          'main chain chem shift': 'chemical_shift',
                                          'bb chem shift': 'chemical_shift',
                                          'BB chem shift': 'chemical_shift',
                                          'backbone cs': 'chemical_shift',
                                          'Backbone cs': 'chemical_shift',
                                          'Mainchain cs': 'chemical_shift',
                                          'mainchain cs': 'chemical_shift',
                                          'Main chain cs': 'chemical_shift',
                                          'main chain cs': 'chemical_shift',
                                          'bb cs': 'chemical_shift',
                                          'BB cs': 'chemical_shift',
                                          'backbone CS': 'chemical_shift',
                                          'Backbone CS': 'chemical_shift',
                                          'Mainchain CS': 'chemical_shift',
                                          'mainchain CS': 'chemical_shift',
                                          'Main chain CS': 'chemical_shift',
                                          'main chain CS': 'chemical_shift',
                                          'bb CS': 'chemical_shift',
                                          'BB CS': 'chemical_shift',
                                          'TALOS': 'chemical_shift',
                                          'talos': 'chemical_shift',
                                          'TALOS+': 'chemical_shift',
                                          'talos+': 'chemical_shift',
                                          'TALOS-N': 'chemical_shift',
                                          'talos-n': 'chemical_shift'
                                          },
                                  'nmr-star': {'jcoupling': 'J-couplings',
                                               'Jcoupling': 'J-couplings',
                                               'jcouplings': 'J-couplings',
                                               'Jcouplings': 'J-couplings',
                                               'j-couplings': 'J-couplings',
                                               'J couplings': 'J-couplings',
                                               'j couplings': 'J-couplings',
                                               'J-coupling': 'J-couplings',
                                               'j-coupling': 'J-couplings',
                                               'J coupling': 'J-couplings',
                                               'j coupling': 'J-couplings',
                                               'chemical_shift': 'backbone chemical shifts',
                                               'Chemical_shift': 'backbone chemical shifts',
                                               'chemical_shifts': 'backbone chemical shifts',
                                               'Chemical_shifts': 'backbone chemical shifts',
                                               'chemical shift': 'backbone chemical shifts',
                                               'Chemical shift': 'backbone chemical shifts',
                                               'chemical shifts': 'backbone chemical shifts',
                                               'Chemical shifts': 'backbone chemical shifts',
                                               'Backbone chemical shifts': 'backbone chemical shifts',
                                               'Mainchain chemical shifts': 'backbone chemical shifts',
                                               'mainchain chemical shifts': 'backbone chemical shifts',
                                               'Main chain chemical shifts': 'backbone chemical shifts',
                                               'main chain chemical shifts': 'backbone chemical shifts',
                                               'bb chemical shifts': 'backbone chemical shifts',
                                               'BB chemical shifts': 'backbone chemical shifts',
                                               'backbone chemical shift': 'backbone chemical shifts',
                                               'Backbone chemical shift': 'backbone chemical shifts',
                                               'Mainchain chemical shift': 'backbone chemical shifts',
                                               'mainchain chemical shift': 'backbone chemical shifts',
                                               'Main chain chemical shift': 'backbone chemical shifts',
                                               'main chain chemical shift': 'backbone chemical shifts',
                                               'bb chemical shift': 'backbone chemical shifts',
                                               'BB chemical shift': 'backbone chemical shifts',
                                               'backbone chem shifts': 'backbone chemical shifts',
                                               'Backbone chem shifts': 'backbone chemical shifts',
                                               'Mainchain chem shifts': 'backbone chemical shifts',
                                               'mainchain chem shifts': 'backbone chemical shifts',
                                               'Main chain chem shifts': 'backbone chemical shifts',
                                               'main chain chem shifts': 'backbone chemical shifts',
                                               'bb chem shifts': 'backbone chemical shifts',
                                               'BB chem shifts': 'backbone chemical shifts',
                                               'backbone chem shift': 'backbone chemical shifts',
                                               'Backbone chem shift': 'backbone chemical shifts',
                                               'Mainchain chem shift': 'backbone chemical shifts',
                                               'mainchain chem shift': 'backbone chemical shifts',
                                               'Main chain chem shift': 'backbone chemical shifts',
                                               'main chain chem shift': 'backbone chemical shifts',
                                               'bb chem shift': 'backbone chemical shifts',
                                               'BB chem shift': 'backbone chemical shifts',
                                               'backbone cs': 'backbone chemical shifts',
                                               'Backbone cs': 'backbone chemical shifts',
                                               'Mainchain cs': 'backbone chemical shifts',
                                               'mainchain cs': 'backbone chemical shifts',
                                               'Main chain cs': 'backbone chemical shifts',
                                               'main chain cs': 'backbone chemical shifts',
                                               'bb cs': 'backbone chemical shifts',
                                               'BB cs': 'backbone chemical shifts',
                                               'backbone CS': 'backbone chemical shifts',
                                               'Backbone CS': 'backbone chemical shifts',
                                               'Mainchain CS': 'backbone chemical shifts',
                                               'mainchain CS': 'backbone chemical shifts',
                                               'Main chain CS': 'backbone chemical shifts',
                                               'main chain CS': 'backbone chemical shifts',
                                               'bb CS': 'backbone chemical shifts',
                                               'BB CS': 'backbone chemical shifts',
                                               'TALOS': 'backbone chemical shifts',
                                               'talos': 'backbone chemical shifts',
                                               'TALOS+': 'backbone chemical shifts',
                                               'talos+': 'backbone chemical shifts',
                                               'TALOS-N': 'backbone chemical shifts',
                                               'talos-n': 'backbone chemical shifts'
                                               }
                                  }


altRdcConstraintType = {'nef': {'RDC': 'measured',
                                'rdc': 'measured'
                                },
                        'nmr-star': {'rdc': 'RDC',
                                     'measured': 'RDC'
                                     }
                        }


def get_idx_msg(idx_tag_ids: List[int], tags: List[str], row: dict) -> str:
    """ Return description about current index.
        @author: Masashi Yokochi
        @return: description
    """

    try:

        f = []

        if len(idx_tag_ids) > 0:
            for _j in idx_tag_ids:
                f.append(tags[_j] + " " + str(row[tags[_j]]))

            return f"[Check row of {', '.join(f)}] "

        return ''

    except KeyError:
        return ''


def is_empty_loop(star_data: Union[pynmrstar.Entry, pynmrstar.Saveframe, pynmrstar.Loop], lp_category: str) -> bool:
    """ Return whether one of specified loops is empty loop.
        @return: True for empty loop exists, False otherwise
    """

    if isinstance(star_data, pynmrstar.Entry):
        loops = star_data.get_loops_by_category(lp_category)

        return any(len(loop) == 0 for loop in loops)

    if isinstance(star_data, pynmrstar.Saveframe):
        loop = star_data.get_loop(lp_category)

        return len(loop) == 0

    return len(star_data) == 0


def count_non_empty_loops(star_data: Union[pynmrstar.Entry, pynmrstar.Saveframe, pynmrstar.Loop], lp_category: str) -> int:
    """ Return the number of non-empty loops.
        @return: the number of non-empty loops.
    """

    if isinstance(star_data, pynmrstar.Entry):
        loops = star_data.get_loops_by_category(lp_category)

        return sum(len(loop) > 0 for loop in loops)

    if isinstance(star_data, pynmrstar.Saveframe):
        loop = star_data.get_loop(lp_category)

        return 0 if len(loop) == 0 else 1

    return 0 if len(star_data) == 0 else 1


def get_sf_tag_values_with_empty_loop(star_data: Union[pynmrstar.Entry, pynmrstar.Saveframe, pynmrstar.Loop], lp_category: str, sf_category: str) -> List[str]:
    """ Return list of saveframe tag values with empty loop.
        @return: list of saveframe tag values
    """

    sf_framecodes = []

    for sf in star_data.get_saveframes_by_category(sf_category):

        loop = sf.get_loop(lp_category)

        if len(loop) == 0:
            sf_framecodes.append(get_first_sf_tag(sf, 'sf_framecode'))

    return sf_framecodes


def is_empty(array: list) -> bool:
    """ Return whether the array contains empty data.
        @author: Masashi Yokochi
        @return: True for empty data in the array, False otherwise
    """

    return any(d in emptyValue for d in array)


def is_data(array: list) -> bool:
    """ Return whether the array consists of no empty data.
        @author: Masashi Yokochi
        @return: True for no empty data in the array, False for empty data
    """

    return not any(d in emptyValue for d in array)


def is_good_data(array: list) -> bool:
    """ Return whether the array consists of good pattern data (neither empty nor bad pattern).
        @author: Masashi Yokochi
        @return: True for good data in the array, False otherwise
    """

    return not any(d in emptyValue or (isinstance(d, str) and badPattern.match(d)) for d in array)


class NEFTranslator:
    """ Bi-directional translator between NEF and NMR-STAR
    """

    def __init__(self, verbose: bool = False, log: IO = sys.stderr,
                 ccU: Optional[ChemCompUtil] = None, csStat: Optional[BMRBChemShiftStat] = None,
                 c2S: Optional[CifToNmrStar] = None):
        self.__class_name__ = self.__class__.__name__
        self.__version__ = __version__

        self.__verbose = verbose
        self.__lfh = log

        # whether to enable remediation routine
        self.__remediation_mode = False
        # whether to allow sequence mismatch during annotation
        self.__annotation_mode = False
        # whether to allow to raise internal error
        self.__internal_mode = False
        # whether to allow to reset auth_seq_id of cs loop if necessary (DAOTHER-9927)
        self.__merge_rescue_mode = False
        # whether the initial sequence number starts from '1' in NEF file, otherwise preserves author sequence scheme of the coordinates
        self.__bmrb_only = False
        # whether allow missing distance restraints
        self.__allow_missing_dist_restraint = False
        # whether to skip missing_mandatory_content error for data conversion server (DAOTHER-9785)
        self.__allow_missing_chem_shift = False

        # libDirPath = os.path.dirname(__file__) + '/lib/'

        # self.tagMap = self.load_csv_data(libDirPath + 'NEF_NMRSTAR_equivalence.csv', transpose=True)
        self.sfCatMap = [('nef_nmr_meta_data', 'entry_information'),
                         ('nef_molecular_system', 'assembly'),
                         ('nef_chemical_shift_list', 'assigned_chemical_shifts'),
                         ('nef_distance_restraint_list', 'general_distance_constraints'),
                         ('nef_dihedral_restraint_list', 'torsion_angle_constraints'),
                         ('nef_rdc_restraint_list', 'RDC_constraints'),
                         ('nef_nmr_spectrum', 'spectral_peak_list'),
                         ('nef_peak_restraint_links', 'peak_constraint_links'),
                         ('nef_related_entries', 'Related_entries'),
                         ('nef_program_script', 'Software_applied_methods'),
                         ('nef_run_history', 'History'),
                         ('nef_sequence', 'Chem_comp_assembly'),
                         ('nef_covalent_links', 'Bond'),
                         ('nef_chemical_shift', 'Atom_chem_shift'),
                         ('nef_distance_restraint', 'Gen_dist_constraint'),
                         ('nef_dihedral_restraint', 'Torsion_angle_constraint'),
                         ('nef_rdc_restraint', 'RDC_constraint'),
                         ('nef_spectrum_dimension', 'Spectral_dim'),
                         ('nef_spectrum_dimension_transfer', 'Spectral_dim_transfer'),
                         ('nef_peak', 'Peak_row_format'),
                         ('nef_peak_restraint_link', 'Peak_constraint_link'),
                         ('audit', 'Audit')
                         ]

        # nef tag, nmr-star auth tag, nmr-star tag
        self.tagMap = [('_nef_program_script.program_name', '_Software_applied_methods.Software_name', '_Software_applied_methods.Software_name'),
                       ('_nef_program_script.script_name', '_Software_applied_methods.Script_name', '_Software_applied_methods.Script_name'),
                       ('_nef_program_script.script', '_Software_applied_methods.Script', '_Software_applied_methods.Script'),
                       ('_nef_run_history.run_number', '_History.Run_number', '_History.Run_number'),
                       ('_nef_run_history.program_name', '_History.Software_name', '_History.Software_name'),
                       ('_nef_run_history.program_version', '_History.Software_version', '_History.Software_version'),
                       ('_nef_run_history.script_name', '_History.Script_name', '_History.Script_name'),
                       ('_nef_run_history.script', '_History.Script', '_History.Script'),
                       ('_nef_nmr_meta_data.sf_category', '_Entry.Sf_category', '_Entry.Sf_category'),
                       ('_nef_nmr_meta_data.sf_framecode', '_Entry.Sf_framecode', '_Entry.Sf_framecode'),
                       ('_nef_nmr_meta_data.format_name', '_Entry.Source_data_format', '_Entry.Source_data_format'),
                       ('_nef_nmr_meta_data.format_version', '_Entry.Source_data_format_version', '_Entry.Source_data_format_version'),
                       ('_nef_nmr_meta_data.program_name', '_Entry.Generated_software_name', '_Entry.Generated_software_name'),
                       ('_nef_nmr_meta_data.program_version', '_Entry.Generated_software_version', '_Entry.Generated_software_version'),
                       ('_nef_nmr_meta_data.creation_date', '_Entry.Generated_date', '_Entry.Generated_date'),
                       ('_nef_nmr_meta_data.uuid', '_Entry.UUID', '_Entry.UUID'),
                       ('_nef_nmr_meta_data.coordinate_file_name', '_Entry.Related_coordinate_file_name', '_Entry.Related_coordinate_file_name'),
                       ('_nef_related_entries.database_name', '_Related_entries.Database_name', '_Related_entries.Database_name'),
                       ('_nef_related_entries.database_accession_code', '_Related_entries.Database_accession_code', '_Related_entries.Database_accession_code'),
                       ('_nef_molecular_system.sf_category', '_Assembly.Sf_category', '_Assembly.Sf_category'),
                       ('_nef_molecular_system.sf_framecode', '_Assembly.Sf_framecode', '_Assembly.Sf_framecode'),
                       ('_nef_sequence.index', '_Chem_comp_assembly.NEF_index', '_Chem_comp_assembly.NEF_index'),
                       ('_nef_sequence.chain_code', '_Chem_comp_assembly.Auth_asym_ID', '_Chem_comp_assembly.Entity_assembly_ID'),
                       ('_nef_sequence.sequence_code', '_Chem_comp_assembly.Auth_seq_ID', '_Chem_comp_assembly.Comp_index_ID'),
                       ('_nef_sequence.residue_name', '_Chem_comp_assembly.Auth_comp_ID', '_Chem_comp_assembly.Comp_ID'),
                       ('_nef_sequence.linking', '_Chem_comp_assembly.Sequence_linking', '_Chem_comp_assembly.Sequence_linking'),
                       ('_nef_sequence.residue_variant', '_Chem_comp_assembly.Auth_variant_ID', '_Chem_comp_assembly.Auth_variant_ID'),
                       ('_nef_sequence.cis_peptide', '_Chem_comp_assembly.Cis_residue', '_Chem_comp_assembly.Cis_residue'),
                       ('_nef_covalent_links.chain_code_1', '_Bond.Auth_asym_ID_1', '_Bond.Entity_assembly_ID_1'),
                       ('_nef_covalent_links.sequence_code_1', '_Bond.Auth_seq_ID_1', '_Bond.Comp_index_ID_1'),
                       ('_nef_covalent_links.residue_name_1', '_Bond.Auth_comp_ID_1', '_Bond.Comp_ID_1'),
                       ('_nef_covalent_links.atom_name_1', '_Bond.Auth_atom_ID_1', '_Bond.Atom_ID_1'),
                       ('_nef_covalent_links.chain_code_2', '_Bond.Auth_asym_ID_2', '_Bond.Entity_assembly_ID_2'),
                       ('_nef_covalent_links.sequence_code_2', '_Bond.Auth_seq_ID_2', '_Bond.Comp_index_ID_2'),
                       ('_nef_covalent_links.residue_name_2', '_Bond.Auth_comp_ID_2', '_Bond.Comp_ID_2'),
                       ('_nef_covalent_links.atom_name_2', '_Bond.Auth_atom_ID_2', '_Bond.Atom_ID_2'),
                       ('_nef_chemical_shift_list.sf_category', '_Assigned_chem_shift_list.Sf_category', '_Assigned_chem_shift_list.Sf_category'),
                       ('_nef_chemical_shift_list.sf_framecode', '_Assigned_chem_shift_list.Sf_framecode', '_Assigned_chem_shift_list.Sf_framecode'),
                       ('_nef_chemical_shift_list.atom_chemical_shift_units', '', ''),
                       ('_nef_chemical_shift.chain_code', '_Atom_chem_shift.Auth_asym_ID', '_Atom_chem_shift.Entity_assembly_ID'),
                       ('_nef_chemical_shift.sequence_code', '_Atom_chem_shift.Auth_seq_ID', '_Atom_chem_shift.Comp_index_ID'),
                       ('_nef_chemical_shift.residue_name', '_Atom_chem_shift.Auth_comp_ID', '_Atom_chem_shift.Comp_ID'),
                       ('_nef_chemical_shift.atom_name', '_Atom_chem_shift.Auth_atom_ID', '_Atom_chem_shift.Atom_ID'),
                       ('_nef_chemical_shift.element', '_Atom_chem_shift.Atom_type', '_Atom_chem_shift.Atom_type'),
                       ('_nef_chemical_shift.isotope_number', '_Atom_chem_shift.Atom_isotope_number', '_Atom_chem_shift.Atom_isotope_number'),
                       ('_nef_chemical_shift.value', '_Atom_chem_shift.Val', '_Atom_chem_shift.Val'),
                       ('_nef_chemical_shift.value_uncertainty', '_Atom_chem_shift.Val_err', '_Atom_chem_shift.Val_err'),
                       ('_nef_distance_restraint_list.sf_category', '_Gen_dist_constraint_list.Sf_category', '_Gen_dist_constraint_list.Sf_category'),
                       ('_nef_distance_restraint_list.sf_framecode', '_Gen_dist_constraint_list.Sf_framecode', '_Gen_dist_constraint_list.Sf_framecode'),
                       ('_nef_distance_restraint_list.potential_type', '_Gen_dist_constraint_list.Potential_type', '_Gen_dist_constraint_list.Potential_type'),
                       ('_nef_distance_restraint_list.restraint_origin', '_Gen_dist_constraint_list.Constraint_type', '_Gen_dist_constraint_list.Constraint_type'),
                       ('_nef_distance_restraint.index', '_Gen_dist_constraint.Index_ID', '_Gen_dist_constraint.Index_ID'),
                       ('_nef_distance_restraint.restraint_id', '_Gen_dist_constraint.ID', '_Gen_dist_constraint.ID'),
                       ('_nef_distance_restraint.restraint_combination_id', '_Gen_dist_constraint.Combination_ID', '_Gen_dist_constraint.Combination_ID'),
                       ('_nef_distance_restraint.chain_code_1', '_Gen_dist_constraint.Auth_asym_ID_1', '_Gen_dist_constraint.Entity_assembly_ID_1'),
                       ('_nef_distance_restraint.sequence_code_1', '_Gen_dist_constraint.Auth_seq_ID_1', '_Gen_dist_constraint.Comp_index_ID_1'),
                       ('_nef_distance_restraint.residue_name_1', '_Gen_dist_constraint.Auth_comp_ID_1', '_Gen_dist_constraint.Comp_ID_1'),
                       ('_nef_distance_restraint.atom_name_1', '_Gen_dist_constraint.Auth_atom_ID_1', '_Gen_dist_constraint.Atom_ID_1'),
                       ('_nef_distance_restraint.chain_code_2', '_Gen_dist_constraint.Auth_asym_ID_2', '_Gen_dist_constraint.Entity_assembly_ID_2'),
                       ('_nef_distance_restraint.sequence_code_2', '_Gen_dist_constraint.Auth_seq_ID_2', '_Gen_dist_constraint.Comp_index_ID_2'),
                       ('_nef_distance_restraint.residue_name_2', '_Gen_dist_constraint.Auth_comp_ID_2', '_Gen_dist_constraint.Comp_ID_2'),
                       ('_nef_distance_restraint.atom_name_2', '_Gen_dist_constraint.Auth_atom_ID_2', '_Gen_dist_constraint.Atom_ID_2'),
                       ('_nef_distance_restraint.weight', '_Gen_dist_constraint.Weight', '_Gen_dist_constraint.Weight'),
                       ('_nef_distance_restraint.target_value', '_Gen_dist_constraint.Target_val', '_Gen_dist_constraint.Target_val'),
                       ('_nef_distance_restraint.target_value_uncertainty', '_Gen_dist_constraint.Target_val_uncertainty', '_Gen_dist_constraint.Target_val_uncertainty'),
                       ('_nef_distance_restraint.lower_linear_limit', '_Gen_dist_constraint.Lower_linear_limit', '_Gen_dist_constraint.Lower_linear_limit'),
                       ('_nef_distance_restraint.lower_limit', '_Gen_dist_constraint.Distance_lower_bound_val', '_Gen_dist_constraint.Distance_lower_bound_val'),
                       ('_nef_distance_restraint.upper_limit', '_Gen_dist_constraint.Distance_upper_bound_val', '_Gen_dist_constraint.Distance_upper_bound_val'),
                       ('_nef_distance_restraint.upper_linear_limit', '_Gen_dist_constraint.Upper_linear_limit', '_Gen_dist_constraint.Upper_linear_limit'),
                       ('_nef_dihedral_restraint_list.sf_category', '_Torsion_angle_constraint_list.Sf_category', '_Torsion_angle_constraint_list.Sf_category'),
                       ('_nef_dihedral_restraint_list.sf_framecode', '_Torsion_angle_constraint_list.Sf_framecode', '_Torsion_angle_constraint_list.Sf_framecode'),
                       ('_nef_dihedral_restraint_list.potential_type', '_Torsion_angle_constraint_list.Potential_type', '_Torsion_angle_constraint_list.Potential_type'),
                       ('_nef_dihedral_restraint_list.restraint_origin', '_Torsion_angle_constraint_list.Constraint_type', '_Torsion_angle_constraint_list.Constraint_type'),
                       ('_nef_dihedral_restraint.index', '_Torsion_angle_constraint.Index_ID', '_Torsion_angle_constraint.Index_ID'),
                       ('_nef_dihedral_restraint.restraint_id', '_Torsion_angle_constraint.ID', '_Torsion_angle_constraint.ID'),
                       ('_nef_dihedral_restraint.restraint_combination_id', '_Torsion_angle_constraint.Combination_ID', '_Torsion_angle_constraint.Combination_ID'),
                       ('_nef_dihedral_restraint.chain_code_1', '_Torsion_angle_constraint.Auth_asym_ID_1', '_Torsion_angle_constraint.Entity_assembly_ID_1'),
                       ('_nef_dihedral_restraint.sequence_code_1', '_Torsion_angle_constraint.Auth_seq_ID_1', '_Torsion_angle_constraint.Comp_index_ID_1'),
                       ('_nef_dihedral_restraint.residue_name_1', '_Torsion_angle_constraint.Auth_comp_ID_1', '_Torsion_angle_constraint.Comp_ID_1'),
                       ('_nef_dihedral_restraint.atom_name_1', '_Torsion_angle_constraint.Auth_atom_ID_1', '_Torsion_angle_constraint.Atom_ID_1'),
                       ('_nef_dihedral_restraint.chain_code_2', '_Torsion_angle_constraint.Auth_asym_ID_2', '_Torsion_angle_constraint.Entity_assembly_ID_2'),
                       ('_nef_dihedral_restraint.sequence_code_2', '_Torsion_angle_constraint.Auth_seq_ID_2', '_Torsion_angle_constraint.Comp_index_ID_2'),
                       ('_nef_dihedral_restraint.residue_name_2', '_Torsion_angle_constraint.Auth_comp_ID_2', '_Torsion_angle_constraint.Comp_ID_2'),
                       ('_nef_dihedral_restraint.atom_name_2', '_Torsion_angle_constraint.Auth_atom_ID_2', '_Torsion_angle_constraint.Atom_ID_2'),
                       ('_nef_dihedral_restraint.chain_code_3', '_Torsion_angle_constraint.Auth_asym_ID_3', '_Torsion_angle_constraint.Entity_assembly_ID_3'),
                       ('_nef_dihedral_restraint.sequence_code_3', '_Torsion_angle_constraint.Auth_seq_ID_3', '_Torsion_angle_constraint.Comp_index_ID_3'),
                       ('_nef_dihedral_restraint.residue_name_3', '_Torsion_angle_constraint.Auth_comp_ID_3', '_Torsion_angle_constraint.Comp_ID_3'),
                       ('_nef_dihedral_restraint.atom_name_3', '_Torsion_angle_constraint.Auth_atom_ID_3', '_Torsion_angle_constraint.Atom_ID_3'),
                       ('_nef_dihedral_restraint.chain_code_4', '_Torsion_angle_constraint.Auth_asym_ID_4', '_Torsion_angle_constraint.Entity_assembly_ID_4'),
                       ('_nef_dihedral_restraint.sequence_code_4', '_Torsion_angle_constraint.Auth_seq_ID_4', '_Torsion_angle_constraint.Comp_index_ID_4'),
                       ('_nef_dihedral_restraint.residue_name_4', '_Torsion_angle_constraint.Auth_comp_ID_4', '_Torsion_angle_constraint.Comp_ID_4'),
                       ('_nef_dihedral_restraint.atom_name_4', '_Torsion_angle_constraint.Auth_atom_ID_4', '_Torsion_angle_constraint.Atom_ID_4'),
                       ('_nef_dihedral_restraint.weight', '_Torsion_angle_constraint.Weight', '_Torsion_angle_constraint.Weight'),
                       ('_nef_dihedral_restraint.target_value', '_Torsion_angle_constraint.Angle_target_val', '_Torsion_angle_constraint.Angle_target_val'),
                       ('_nef_dihedral_restraint.target_value_uncertainty', '_Torsion_angle_constraint.Angle_target_val_err', '_Torsion_angle_constraint.Angle_target_val_err'),
                       ('_nef_dihedral_restraint.lower_linear_limit', '_Torsion_angle_constraint.Angle_lower_linear_limit', '_Torsion_angle_constraint.Angle_lower_linear_limit'),
                       ('_nef_dihedral_restraint.lower_limit', '_Torsion_angle_constraint.Angle_lower_bound_val', '_Torsion_angle_constraint.Angle_lower_bound_val'),
                       ('_nef_dihedral_restraint.upper_limit', '_Torsion_angle_constraint.Angle_upper_bound_val', '_Torsion_angle_constraint.Angle_upper_bound_val'),
                       ('_nef_dihedral_restraint.upper_linear_limit', '_Torsion_angle_constraint.Angle_upper_linear_limit', '_Torsion_angle_constraint.Angle_upper_linear_limit'),
                       ('_nef_dihedral_restraint.name', '_Torsion_angle_constraint.Torsion_angle_name', '_Torsion_angle_constraint.Torsion_angle_name'),
                       ('_nef_rdc_restraint_list.sf_category', '_RDC_constraint_list.Sf_category', '_RDC_constraint_list.Sf_category'),
                       ('_nef_rdc_restraint_list.sf_framecode', '_RDC_constraint_list.Sf_framecode', '_RDC_constraint_list.Sf_framecode'),
                       ('_nef_rdc_restraint_list.potential_type', '_RDC_constraint_list.Potential_type', '_RDC_constraint_list.Potential_type'),
                       ('_nef_rdc_restraint_list.restraint_origin', '_RDC_constraint_list.Constraint_type', '_RDC_constraint_list.Constraint_type'),
                       ('_nef_rdc_restraint_list.tensor_magnitude', '_RDC_constraint_list.Tensor_magnitude', '_RDC_constraint_list.Tensor_magnitude'),
                       ('_nef_rdc_restraint_list.tensor_rhombicity', '_RDC_constraint_list.Tensor_rhombicity', '_RDC_constraint_list.Tensor_rhombicity'),
                       ('_nef_rdc_restraint_list.tensor_chain_code', '_RDC_constraint_list.Tensor_auth_asym_ID', '_RDC_constraint_list.Tensor_Entity_assembly_ID'),
                       ('_nef_rdc_restraint_list.tensor_sequence_code', '_RDC_constraint_list.Tensor_Auth_seq_ID', '_RDC_constraint_list.Tensor_seq_ID'),
                       ('_nef_rdc_restraint_list.tensor_residue_name', '_RDC_constraint_list.Tensor_auth_comp_ID', '_RDC_constraint_list.Tensor_comp_ID'),
                       ('_nef_rdc_restraint.index', '_RDC_constraint.Index_ID', '_RDC_constraint.Index_ID'),
                       ('_nef_rdc_restraint.restraint_id', '_RDC_constraint.ID', '_RDC_constraint.ID'),
                       ('_nef_rdc_restraint.restraint_combination_id', '_RDC_constraint.Combination_ID', '_RDC_constraint.Combination_ID'),
                       ('_nef_rdc_restraint.chain_code_1', '_RDC_constraint.Auth_asym_ID_1', '_RDC_constraint.Entity_assembly_ID_1'),
                       ('_nef_rdc_restraint.sequence_code_1', '_RDC_constraint.Auth_seq_ID_1', '_RDC_constraint.Comp_index_ID_1'),
                       ('_nef_rdc_restraint.residue_name_1', '_RDC_constraint.Auth_comp_ID_1', '_RDC_constraint.Comp_ID_1'),
                       ('_nef_rdc_restraint.atom_name_1', '_RDC_constraint.Auth_atom_ID_1', '_RDC_constraint.Atom_ID_1'),
                       ('_nef_rdc_restraint.chain_code_2', '_RDC_constraint.Auth_asym_ID_2', '_RDC_constraint.Entity_assembly_ID_2'),
                       ('_nef_rdc_restraint.sequence_code_2', '_RDC_constraint.Auth_seq_ID_2', '_RDC_constraint.Comp_index_ID_2'),
                       ('_nef_rdc_restraint.residue_name_2', '_RDC_constraint.Auth_comp_ID_2', '_RDC_constraint.Comp_ID_2'),
                       ('_nef_rdc_restraint.atom_name_2', '_RDC_constraint.Auth_atom_ID_2', '_RDC_constraint.Atom_ID_2'),
                       ('_nef_rdc_restraint.weight', '_RDC_constraint.Weight', '_RDC_constraint.Weight'),
                       ('_nef_rdc_restraint.target_value', '_RDC_constraint.Target_value', '_RDC_constraint.Target_value'),
                       ('_nef_rdc_restraint.target_value_uncertainty', '_RDC_constraint.Target_value_uncertainty', '_RDC_constraint.Target_value_uncertainty'),
                       ('_nef_rdc_restraint.lower_linear_limit', '_RDC_constraint.RDC_lower_linear_limit', '_RDC_constraint.RDC_lower_linear_limit'),
                       ('_nef_rdc_restraint.lower_limit', '_RDC_constraint.RDC_lower_bound', '_RDC_constraint.RDC_lower_bound'),
                       ('_nef_rdc_restraint.upper_limit', '_RDC_constraint.RDC_upper_bound', '_RDC_constraint.RDC_upper_bound'),
                       ('_nef_rdc_restraint.upper_linear_limit', '_RDC_constraint.RDC_upper_linear_limit', '_RDC_constraint.RDC_upper_linear_limit'),
                       ('_nef_rdc_restraint.scale', '_RDC_constraint.RDC_val_scale_factor', '_RDC_constraint.RDC_val_scale_factor'),
                       ('_nef_rdc_restraint.distance_dependent', '_RDC_constraint.RDC_distant_dependent', '_RDC_constraint.RDC_distant_dependent'),
                       ('_nef_nmr_spectrum.sf_category', '_Spectral_peak_list.Sf_category', '_Spectral_peak_list.Sf_category'),
                       ('_nef_nmr_spectrum.sf_framecode', '_Spectral_peak_list.Sf_framecode', '_Spectral_peak_list.Sf_framecode'),
                       ('_nef_nmr_spectrum.num_dimensions', '_Spectral_peak_list.Number_of_spectral_dimensions', '_Spectral_peak_list.Number_of_spectral_dimensions'),
                       ('_nef_nmr_spectrum.chemical_shift_list', '_Spectral_peak_list.Chemical_shift_list', '_Spectral_peak_list.Chemical_shift_list'),
                       ('_nef_nmr_spectrum.experiment_classification', '_Spectral_peak_list.Experiment_class', '_Spectral_peak_list.Experiment_class'),
                       ('_nef_nmr_spectrum.experiment_type', '_Spectral_peak_list.Experiment_type', '_Spectral_peak_list.Experiment_type'),
                       ('_nef_spectrum_dimension.dimension_id', '_Spectral_dim.ID', '_Spectral_dim.ID'),
                       ('_nef_spectrum_dimension.axis_unit', '_Spectral_dim.Sweep_width_units', '_Spectral_dim.Sweep_width_units'),
                       ('_nef_spectrum_dimension.axis_code', '_Spectral_dim.Axis_code', '_Spectral_dim.Axis_code'),
                       ('_nef_spectrum_dimension.spectrometer_frequency', '_Spectral_dim.Spectrometer_frequency', '_Spectral_dim.Spectrometer_frequency'),
                       ('_nef_spectrum_dimension.spectral_width', '_Spectral_dim.Sweep_width', '_Spectral_dim.Sweep_width'),
                       ('_nef_spectrum_dimension.value_first_point', '_Spectral_dim.Value_first_point', '_Spectral_dim.Value_first_point'),
                       ('_nef_spectrum_dimension.folding', '_Spectral_dim.Under_sampling_type', '_Spectral_dim.Under_sampling_type'),
                       ('_nef_spectrum_dimension.absolute_peak_positions', '_Spectral_dim.Absolute_peak_positions', '_Spectral_dim.Absolute_peak_positions'),
                       ('_nef_spectrum_dimension.is_acquisition', '_Spectral_dim.Acquisition', '_Spectral_dim.Acquisition'),
                       ('_nef_spectrum_dimension_transfer.dimension_1', '_Spectral_dim_transfer.Spectral_dim_ID_1', '_Spectral_dim_transfer.Spectral_dim_ID_1'),
                       ('_nef_spectrum_dimension_transfer.dimension_2', '_Spectral_dim_transfer.Spectral_dim_ID_2', '_Spectral_dim_transfer.Spectral_dim_ID_2'),
                       ('_nef_spectrum_dimension_transfer.transfer_type', '_Spectral_dim_transfer.Type', '_Spectral_dim_transfer.Type'),
                       ('_nef_spectrum_dimension_transfer.is_indirect', '_Spectral_dim_transfer.Indirect', '_Spectral_dim_transfer.Indirect'),
                       ('_nef_peak.index', '_Peak_row_format.Index_ID', '_Peak_row_format.Index_ID'),
                       ('_nef_peak.peak_id', '_Peak_row_format.ID', '_Peak_row_format.ID'),
                       ('_nef_peak.volume', '_Peak_row_format.Volume', '_Peak_row_format.Volume'),
                       ('_nef_peak.volume_uncertainty', '_Peak_row_format.Volume_uncertainty', '_Peak_row_format.Volume_uncertainty'),
                       ('_nef_peak.height', '_Peak_row_format.Height', '_Peak_row_format.Height'),
                       ('_nef_peak.height_uncertainty', '_Peak_row_format.Height_uncertainty', '_Peak_row_format.Height_uncertainty'),
                       ('_nef_peak.position_1', '_Peak_row_format.Position_1', '_Peak_row_format.Position_1'),
                       ('_nef_peak.position_uncertainty_1', '_Peak_row_format.Position_uncertainty_1', '_Peak_row_format.Position_uncertainty_1'),
                       ('_nef_peak.position_2', '_Peak_row_format.Position_2', '_Peak_row_format.Position_2'),
                       ('_nef_peak.position_uncertainty_2', '_Peak_row_format.Position_uncertainty_2', '_Peak_row_format.Position_uncertainty_2'),
                       ('_nef_peak.position_3', '_Peak_row_format.Position_3', '_Peak_row_format.Position_3'),
                       ('_nef_peak.position_uncertainty_3', '_Peak_row_format.Position_uncertainty_3', '_Peak_row_format.Position_uncertainty_3'),
                       ('_nef_peak.position_4', '_Peak_row_format.Position_4', '_Peak_row_format.Position_4'),
                       ('_nef_peak.position_uncertainty_4', '_Peak_row_format.Position_uncertainty_4', '_Peak_row_format.Position_uncertainty_4'),
                       ('_nef_peak.position_5', '_Peak_row_format.Position_5', '_Peak_row_format.Position_5'),
                       ('_nef_peak.position_uncertainty_5', '_Peak_row_format.Position_uncertainty_5', '_Peak_row_format.Position_uncertainty_5'),
                       ('_nef_peak.position_6', '_Peak_row_format.Position_6', '_Peak_row_format.Position_6'),
                       ('_nef_peak.position_uncertainty_6', '_Peak_row_format.Position_uncertainty_6', '_Peak_row_format.Position_uncertainty_6'),
                       ('_nef_peak.position_7', '_Peak_row_format.Position_7', '_Peak_row_format.Position_7'),
                       ('_nef_peak.position_uncertainty_7', '_Peak_row_format.Position_uncertainty_7', '_Peak_row_format.Position_uncertainty_7'),
                       ('_nef_peak.position_8', '_Peak_row_format.Position_8', '_Peak_row_format.Position_8'),
                       ('_nef_peak.position_uncertainty_8', '_Peak_row_format.Position_uncertainty_8', '_Peak_row_format.Position_uncertainty_8'),
                       ('_nef_peak.position_9', '_Peak_row_format.Position_9', '_Peak_row_format.Position_9'),
                       ('_nef_peak.position_uncertainty_9', '_Peak_row_format.Position_uncertainty_9', '_Peak_row_format.Position_uncertainty_9'),
                       ('_nef_peak.position_10', '_Peak_row_format.Position_10', '_Peak_row_format.Position_10'),
                       ('_nef_peak.position_uncertainty_10', '_Peak_row_format.Position_uncertainty_10', '_Peak_row_format.Position_uncertainty_10'),
                       ('_nef_peak.position_11', '_Peak_row_format.Position_11', '_Peak_row_format.Position_11'),
                       ('_nef_peak.position_uncertainty_11', '_Peak_row_format.Position_uncertainty_11', '_Peak_row_format.Position_uncertainty_11'),
                       ('_nef_peak.position_12', '_Peak_row_format.Position_12', '_Peak_row_format.Position_12'),
                       ('_nef_peak.position_uncertainty_12', '_Peak_row_format.Position_uncertainty_12', '_Peak_row_format.Position_uncertainty_12'),
                       ('_nef_peak.position_13', '_Peak_row_format.Position_13', '_Peak_row_format.Position_13'),
                       ('_nef_peak.position_uncertainty_13', '_Peak_row_format.Position_uncertainty_13', '_Peak_row_format.Position_uncertainty_13'),
                       ('_nef_peak.position_14', '_Peak_row_format.Position_14', '_Peak_row_format.Position_14'),
                       ('_nef_peak.position_uncertainty_14', '_Peak_row_format.Position_uncertainty_14', '_Peak_row_format.Position_uncertainty_14'),
                       ('_nef_peak.position_15', '_Peak_row_format.Position_15', '_Peak_row_format.Position_15'),
                       ('_nef_peak.position_uncertainty_15', '_Peak_row_format.Position_uncertainty_15', '_Peak_row_format.Position_uncertainty_15'),
                       ('_nef_peak.chain_code_1', '_Peak_row_format.Auth_asym_ID_1', '_Peak_row_format.Entity_assembly_ID_1'),
                       ('_nef_peak.sequence_code_1', '_Peak_row_format.Auth_seq_ID_1', '_Peak_row_format.Comp_index_ID_1'),
                       ('_nef_peak.residue_name_1', '_Peak_row_format.Auth_comp_ID_1', '_Peak_row_format.Comp_ID_1'),
                       ('_nef_peak.atom_name_1', '_Peak_row_format.Auth_atom_ID_1', '_Peak_row_format.Atom_ID_1'),
                       ('_nef_peak.chain_code_2', '_Peak_row_format.Auth_asym_ID_2', '_Peak_row_format.Entity_assembly_ID_2'),
                       ('_nef_peak.sequence_code_2', '_Peak_row_format.Auth_seq_ID_2', '_Peak_row_format.Comp_index_ID_2'),
                       ('_nef_peak.residue_name_2', '_Peak_row_format.Auth_comp_ID_2', '_Peak_row_format.Comp_ID_2'),
                       ('_nef_peak.atom_name_2', '_Peak_row_format.Auth_atom_ID_2', '_Peak_row_format.Atom_ID_2'),
                       ('_nef_peak.chain_code_3', '_Peak_row_format.Auth_asym_ID_3', '_Peak_row_format.Entity_assembly_ID_3'),
                       ('_nef_peak.sequence_code_3', '_Peak_row_format.Auth_seq_ID_3', '_Peak_row_format.Comp_index_ID_3'),
                       ('_nef_peak.residue_name_3', '_Peak_row_format.Auth_comp_ID_3', '_Peak_row_format.Comp_ID_3'),
                       ('_nef_peak.atom_name_3', '_Peak_row_format.Auth_atom_ID_3', '_Peak_row_format.Atom_ID_3'),
                       ('_nef_peak.chain_code_4', '_Peak_row_format.Auth_asym_ID_4', '_Peak_row_format.Entity_assembly_ID_4'),
                       ('_nef_peak.sequence_code_4', '_Peak_row_format.Auth_seq_ID_4', '_Peak_row_format.Comp_index_ID_4'),
                       ('_nef_peak.residue_name_4', '_Peak_row_format.Auth_comp_ID_4', '_Peak_row_format.Comp_ID_4'),
                       ('_nef_peak.atom_name_4', '_Peak_row_format.Auth_atom_ID_4', '_Peak_row_format.Atom_ID_4'),
                       ('_nef_peak.chain_code_5', '_Peak_row_format.Auth_asym_ID_5', '_Peak_row_format.Entity_assembly_ID_5'),
                       ('_nef_peak.sequence_code_5', '_Peak_row_format.Auth_seq_ID_5', '_Peak_row_format.Comp_index_ID_5'),
                       ('_nef_peak.residue_name_5', '_Peak_row_format.Auth_comp_ID_5', '_Peak_row_format.Comp_ID_5'),
                       ('_nef_peak.atom_name_5', '_Peak_row_format.Auth_atom_ID_5', '_Peak_row_format.Atom_ID_5'),
                       ('_nef_peak.chain_code_6', '_Peak_row_format.Auth_asym_ID_6', '_Peak_row_format.Entity_assembly_ID_6'),
                       ('_nef_peak.sequence_code_6', '_Peak_row_format.Auth_seq_ID_6', '_Peak_row_format.Comp_index_ID_6'),
                       ('_nef_peak.residue_name_6', '_Peak_row_format.Auth_comp_ID_6', '_Peak_row_format.Comp_ID_6'),
                       ('_nef_peak.atom_name_6', '_Peak_row_format.Auth_atom_ID_6', '_Peak_row_format.Atom_ID_6'),
                       ('_nef_peak.chain_code_7', '_Peak_row_format.Auth_asym_ID_7', '_Peak_row_format.Entity_assembly_ID_7'),
                       ('_nef_peak.sequence_code_7', '_Peak_row_format.Auth_seq_ID_7', '_Peak_row_format.Comp_index_ID_7'),
                       ('_nef_peak.residue_name_7', '_Peak_row_format.Auth_comp_ID_7', '_Peak_row_format.Comp_ID_7'),
                       ('_nef_peak.atom_name_7', '_Peak_row_format.Auth_atom_ID_7', '_Peak_row_format.Atom_ID_7'),
                       ('_nef_peak.chain_code_8', '_Peak_row_format.Auth_asym_ID_8', '_Peak_row_format.Entity_assembly_ID_8'),
                       ('_nef_peak.sequence_code_8', '_Peak_row_format.Auth_seq_ID_8', '_Peak_row_format.Comp_index_ID_8'),
                       ('_nef_peak.residue_name_8', '_Peak_row_format.Auth_comp_ID_8', '_Peak_row_format.Comp_ID_8'),
                       ('_nef_peak.atom_name_8', '_Peak_row_format.Auth_atom_ID_8', '_Peak_row_format.Atom_ID_8'),
                       ('_nef_peak.chain_code_9', '_Peak_row_format.Auth_asym_ID_9', '_Peak_row_format.Entity_assembly_ID_9'),
                       ('_nef_peak.sequence_code_9', '_Peak_row_format.Auth_seq_ID_9', '_Peak_row_format.Comp_index_ID_9'),
                       ('_nef_peak.residue_name_9', '_Peak_row_format.Auth_comp_ID_9', '_Peak_row_format.Comp_ID_9'),
                       ('_nef_peak.atom_name_9', '_Peak_row_format.Auth_atom_ID_9', '_Peak_row_format.Atom_ID_9'),
                       ('_nef_peak.chain_code_10', '_Peak_row_format.Auth_asym_ID_10', '_Peak_row_format.Entity_assembly_ID_10'),
                       ('_nef_peak.sequence_code_10', '_Peak_row_format.Auth_seq_ID_10', '_Peak_row_format.Comp_index_ID_10'),
                       ('_nef_peak.residue_name_10', '_Peak_row_format.Auth_comp_ID_10', '_Peak_row_format.Comp_ID_10'),
                       ('_nef_peak.atom_name_10', '_Peak_row_format.Auth_atom_ID_10', '_Peak_row_format.Atom_ID_10'),
                       ('_nef_peak.chain_code_11', '_Peak_row_format.Auth_asym_ID_11', '_Peak_row_format.Entity_assembly_ID_11'),
                       ('_nef_peak.sequence_code_11', '_Peak_row_format.Auth_seq_ID_11', '_Peak_row_format.Comp_index_ID_11'),
                       ('_nef_peak.residue_name_11', '_Peak_row_format.Auth_comp_ID_11', '_Peak_row_format.Comp_ID_11'),
                       ('_nef_peak.atom_name_11', '_Peak_row_format.Auth_atom_ID_11', '_Peak_row_format.Atom_ID_11'),
                       ('_nef_peak.chain_code_12', '_Peak_row_format.Auth_asym_ID_12', '_Peak_row_format.Entity_assembly_ID_12'),
                       ('_nef_peak.sequence_code_12', '_Peak_row_format.Auth_seq_ID_12', '_Peak_row_format.Comp_index_ID_12'),
                       ('_nef_peak.residue_name_12', '_Peak_row_format.Auth_comp_ID_12', '_Peak_row_format.Comp_ID_12'),
                       ('_nef_peak.atom_name_12', '_Peak_row_format.Auth_atom_ID_12', '_Peak_row_format.Atom_ID_12'),
                       ('_nef_peak.chain_code_13', '_Peak_row_format.Auth_asym_ID_13', '_Peak_row_format.Entity_assembly_ID_13'),
                       ('_nef_peak.sequence_code_13', '_Peak_row_format.Auth_seq_ID_13', '_Peak_row_format.Comp_index_ID_13'),
                       ('_nef_peak.residue_name_13', '_Peak_row_format.Auth_comp_ID_13', '_Peak_row_format.Comp_ID_13'),
                       ('_nef_peak.atom_name_13', '_Peak_row_format.Auth_atom_ID_13', '_Peak_row_format.Atom_ID_13'),
                       ('_nef_peak.chain_code_14', '_Peak_row_format.Auth_asym_ID_14', '_Peak_row_format.Entity_assembly_ID_14'),
                       ('_nef_peak.sequence_code_14', '_Peak_row_format.Auth_seq_ID_14', '_Peak_row_format.Comp_index_ID_14'),
                       ('_nef_peak.residue_name_14', '_Peak_row_format.Auth_comp_ID_14', '_Peak_row_format.Comp_ID_14'),
                       ('_nef_peak.atom_name_14', '_Peak_row_format.Auth_atom_ID_14', '_Peak_row_format.Atom_ID_14'),
                       ('_nef_peak.chain_code_15', '_Peak_row_format.Auth_asym_ID_15', '_Peak_row_format.Entity_assembly_ID_15'),
                       ('_nef_peak.sequence_code_15', '_Peak_row_format.Auth_seq_ID_15', '_Peak_row_format.Comp_index_ID_15'),
                       ('_nef_peak.residue_name_15', '_Peak_row_format.Auth_comp_ID_15', '_Peak_row_format.Comp_ID_15'),
                       ('_nef_peak.atom_name_15', '_Peak_row_format.Auth_atom_ID_15', '_Peak_row_format.Atom_ID_15'),
                       ('_nef_peak_restraint_links.sf_category', '_Peak_constraint_link_list.Sf_category', '_Peak_constraint_link_list.Sf_category'),
                       ('_nef_peak_restraint_links.sf_framecode', '_Peak_constraint_link_list.Sf_framecode', '_Peak_constraint_link_list.Sf_framecode'),
                       ('_nef_peak_restraint_link.nmr_spectrum_id',
                        '_Peak_constraint_link.Spectral_Peak_list_Sf_framecode', '_Peak_constraint_link.Spectral_Peak_list_Sf_framecode'),
                       ('_nef_peak_restraint_link.peak_id', '_Peak_constraint_link.Peak_ID', '_Peak_constraint_link.Peak_ID'),
                       ('_nef_peak_restraint_link.restraint_list_id', '_Peak_constraint_link.Constraint_Sf_framecode', '_Peak_constraint_link.Constraint_Sf_framecode'),
                       ('_nef_peak_restraint_link.restraint_id', '_Peak_constraint_link.Constraint_ID', '_Peak_constraint_link.Constraint_ID'),
                       ('_audit.revision_id', '_Audit.Revision_ID', '_Audit.Revision_ID'),  # add support for _audit loop in NEF (DAOTHER-6327)
                       ('_audit.creation_date', '_Audit.Creation_date', '_Audit.Creation_date'),
                       ('_audit.creation_method', '_Audit.Creation_method', '_Audit.Creation_method'),
                       ('_audit.update_record', '_Audit.Update_record', '_Audit.Update_record')
                       ]

        # self.nefMandatoryTag = self.load_csv_data(libDirPath + 'NEF_mandatory.csv')
        # """
        # self.nefMandatorySfCat = {'nef_nmr_meta_data': True,
        #                           'nef_related_entries': False,
        #                           'nef_program_script': False,
        #                           'nef_run_history': False,
        #                           'nef_molecular_system': True,
        #                           'nef_sequence': True,
        #                           'nef_covalent_links': False,
        #                           'nef_chemical_shift_list': True,
        #                           'nef_chemical_shift': True,
        #                           'nef_distance_restraint_list': False,
        #                           'nef_distance_restraint': False,
        #                           'nef_dihedral_restraint_list': False,
        #                           'nef_dihedral_restraint': False,
        #                           'nef_rdc_restraint_list': False,
        #                           'nef_rdc_restraint': False,
        #                           'nef_nmr_spectrum': False,
        #                           'nef_spectrum_dimension': True,
        #                           'nef_spectrum_dimension_transfer': True,
        #                           'nef_peak': False,
        #                           'nef_peak_restraint_links': False,
        #                           'nef_peak_restraint_link': False,
        #                           'audit': False
        #                           }
        # """
        self.nefMandatoryTag = {'_nef_nmr_meta_data.sf_category': True,
                                '_nef_nmr_meta_data.sf_framecode': True,
                                '_nef_nmr_meta_data.format_name': True,
                                '_nef_nmr_meta_data.format_version': True,
                                '_nef_nmr_meta_data.program_name': True,
                                '_nef_nmr_meta_data.program_version': True,
                                '_nef_nmr_meta_data.creation_date': True,
                                '_nef_nmr_meta_data.uuid': True,
                                '_nef_nmr_meta_data.coordinate_file_name': False,
                                '_nef_related_entries.database_name': True,
                                '_nef_related_entries.database_accession_code': True,
                                '_nef_program_script.program_name': True,
                                '_nef_program_script.script_name': False,
                                '_nef_program_script.script': False,
                                '_nef_run_history.run_number': True,
                                '_nef_run_history.program_name': True,
                                '_nef_run_history.program_version': False,
                                '_nef_run_history.script_name': False,
                                '_nef_run_history.script': False,
                                '_nef_molecular_system.sf_category': True,
                                '_nef_molecular_system.sf_framecode': True,
                                '_nef_sequence.index': True,
                                '_nef_sequence.chain_code': True,
                                '_nef_sequence.sequence_code': True,
                                '_nef_sequence.residue_name': True,
                                '_nef_sequence.linking': False,
                                '_nef_sequence.residue_variant': False,
                                '_nef_sequence.cis_peptide': False,
                                '_nef_covalent_links.chain_code_1': True,
                                '_nef_covalent_links.sequence_code_1': True,
                                '_nef_covalent_links.residue_name_1': True,
                                '_nef_covalent_links.atom_name_1': True,
                                '_nef_covalent_links.chain_code_2': True,
                                '_nef_covalent_links.sequence_code_2': True,
                                '_nef_covalent_links.residue_name_2': True,
                                '_nef_covalent_links.atom_name_2': True,
                                '_nef_chemical_shift_list.sf_category': True,
                                '_nef_chemical_shift_list.sf_framecode': True,
                                '_nef_chemical_shift.chain_code': True,
                                '_nef_chemical_shift.sequence_code': True,
                                '_nef_chemical_shift.residue_name': True,
                                '_nef_chemical_shift.atom_name': True,
                                '_nef_chemical_shift.value': True,
                                '_nef_chemical_shift.value_uncertainty': False,
                                '_nef_chemical_shift.element': False,
                                '_nef_chemical_shift.isotope_number': False,
                                '_nef_distance_restraint_list.sf_category': True,
                                '_nef_distance_restraint_list.sf_framecode': True,
                                '_nef_distance_restraint_list.potential_type': True,
                                '_nef_distance_restraint_list.restraint_origin': False,
                                '_nef_distance_restraint.index': True,
                                '_nef_distance_restraint.restraint_id': True,
                                '_nef_distance_restraint.restraint_combination_id': False,
                                '_nef_distance_restraint.chain_code_1': True,
                                '_nef_distance_restraint.sequence_code_1': True,
                                '_nef_distance_restraint.residue_name_1': True,
                                '_nef_distance_restraint.atom_name_1': True,
                                '_nef_distance_restraint.chain_code_2': True,
                                '_nef_distance_restraint.sequence_code_2': True,
                                '_nef_distance_restraint.residue_name_2': True,
                                '_nef_distance_restraint.atom_name_2': True,
                                '_nef_distance_restraint.weight': True,
                                '_nef_distance_restraint.target_value': False,
                                '_nef_distance_restraint.target_value_uncertainty': False,
                                '_nef_distance_restraint.lower_linear_limit': False,
                                '_nef_distance_restraint.lower_limit': False,
                                '_nef_distance_restraint.upper_limit': False,
                                '_nef_distance_restraint.upper_linear_limit': False,
                                '_nef_dihedral_restraint_list.sf_category': True,
                                '_nef_dihedral_restraint_list.sf_framecode': True,
                                '_nef_dihedral_restraint_list.potential_type': True,
                                '_nef_dihedral_restraint_list.restraint_origin': False,
                                '_nef_dihedral_restraint.index': True,
                                '_nef_dihedral_restraint.restraint_id': True,
                                '_nef_dihedral_restraint.restraint_combination_id': False,
                                '_nef_dihedral_restraint.chain_code_1': True,
                                '_nef_dihedral_restraint.sequence_code_1': True,
                                '_nef_dihedral_restraint.residue_name_1': True,
                                '_nef_dihedral_restraint.atom_name_1': True,
                                '_nef_dihedral_restraint.chain_code_2': True,
                                '_nef_dihedral_restraint.sequence_code_2': True,
                                '_nef_dihedral_restraint.residue_name_2': True,
                                '_nef_dihedral_restraint.atom_name_2': True,
                                '_nef_dihedral_restraint.chain_code_3': True,
                                '_nef_dihedral_restraint.sequence_code_3': True,
                                '_nef_dihedral_restraint.residue_name_3': True,
                                '_nef_dihedral_restraint.atom_name_3': True,
                                '_nef_dihedral_restraint.chain_code_4': True,
                                '_nef_dihedral_restraint.sequence_code_4': True,
                                '_nef_dihedral_restraint.residue_name_4': True,
                                '_nef_dihedral_restraint.atom_name_4': True,
                                '_nef_dihedral_restraint.weight': True,
                                '_nef_dihedral_restraint.target_value': False,
                                '_nef_dihedral_restraint.target_value_uncertainty': False,
                                '_nef_dihedral_restraint.lower_linear_limit': False,
                                '_nef_dihedral_restraint.lower_limit': False,
                                '_nef_dihedral_restraint.upper_limit': False,
                                '_nef_dihedral_restraint.upper_linear_limit': False,
                                '_nef_dihedral_restraint.name': False,
                                '_nef_rdc_restraint_list.sf_category': True,
                                '_nef_rdc_restraint_list.sf_framecode': True,
                                '_nef_rdc_restraint_list.potential_type': True,
                                '_nef_rdc_restraint_list.restraint_origin': False,
                                '_nef_rdc_restraint_list.tensor_magnitude': False,
                                '_nef_rdc_restraint_list.tensor_rhombicity': False,
                                '_nef_rdc_restraint_list.tensor_chain_code': False,
                                '_nef_rdc_restraint_list.tensor_sequence_code': False,
                                '_nef_rdc_restraint_list.tensor_residue_name': False,
                                '_nef_rdc_restraint.index': True,
                                '_nef_rdc_restraint.restraint_id': True,
                                '_nef_rdc_restraint.restraint_combination_id': False,
                                '_nef_rdc_restraint.chain_code_1': True,
                                '_nef_rdc_restraint.sequence_code_1': True,
                                '_nef_rdc_restraint.residue_name_1': True,
                                '_nef_rdc_restraint.atom_name_1': True,
                                '_nef_rdc_restraint.chain_code_2': True,
                                '_nef_rdc_restraint.sequence_code_2': True,
                                '_nef_rdc_restraint.residue_name_2': True,
                                '_nef_rdc_restraint.atom_name_2': True,
                                '_nef_rdc_restraint.weight': True,
                                '_nef_rdc_restraint.target_value': False,
                                '_nef_rdc_restraint.target_value_uncertainty': False,
                                '_nef_rdc_restraint.lower_linear_limit': False,
                                '_nef_rdc_restraint.lower_limit': False,
                                '_nef_rdc_restraint.upper_limit': False,
                                '_nef_rdc_restraint.upper_linear_limit': False,
                                '_nef_rdc_restraint.scale': False,
                                '_nef_rdc_restraint.distance_dependent': False,
                                '_nef_nmr_spectrum.sf_category': True,
                                '_nef_nmr_spectrum.sf_framecode': True,
                                '_nef_nmr_spectrum.num_dimensions': False,
                                '_nef_nmr_spectrum.chemical_shift_list': False,
                                '_nef_nmr_spectrum.experiment_classification': False,
                                '_nef_nmr_spectrum.experiment_type': False,
                                '_nef_spectrum_dimension.dimension_id': True,
                                '_nef_spectrum_dimension.axis_unit': True,
                                '_nef_spectrum_dimension.axis_code': True,
                                '_nef_spectrum_dimension.spectrometer_frequency': False,
                                '_nef_spectrum_dimension.spectral_width': False,
                                '_nef_spectrum_dimension.value_first_point': False,
                                '_nef_spectrum_dimension.folding': False,
                                '_nef_spectrum_dimension.absolute_peak_positions': False,
                                '_nef_spectrum_dimension.is_acquisition': False,
                                '_nef_spectrum_dimension_transfer.dimension_1': True,
                                '_nef_spectrum_dimension_transfer.dimension_2': True,
                                '_nef_spectrum_dimension_transfer.transfer_type': True,
                                '_nef_spectrum_dimension_transfer.is_indirect': False,
                                '_nef_peak.index': True,
                                '_nef_peak.peak_id': True,
                                '_nef_peak.volume': False,
                                '_nef_peak.volume_uncertainty': False,
                                '_nef_peak.height': False,
                                '_nef_peak.height_uncertainty': False,
                                '_nef_peak.position_1': False,
                                '_nef_peak.position_uncertainty_1': False,
                                '_nef_peak.position_2': False,
                                '_nef_peak.position_uncertainty_2': False,
                                '_nef_peak.position_3': False,
                                '_nef_peak.position_uncertainty_3': False,
                                '_nef_peak.position_4': False,
                                '_nef_peak.position_uncertainty_4': False,
                                '_nef_peak.position_5': False,
                                '_nef_peak.position_uncertainty_5': False,
                                '_nef_peak.position_6': False,
                                '_nef_peak.position_uncertainty_6': False,
                                '_nef_peak.position_7': False,
                                '_nef_peak.position_uncertainty_7': False,
                                '_nef_peak.position_8': False,
                                '_nef_peak.position_uncertainty_8': False,
                                '_nef_peak.position_9': False,
                                '_nef_peak.position_uncertainty_9': False,
                                '_nef_peak.position_10': False,
                                '_nef_peak.position_uncertainty_10': False,
                                '_nef_peak.position_11': False,
                                '_nef_peak.position_uncertainty_11': False,
                                '_nef_peak.position_12': False,
                                '_nef_peak.position_uncertainty_12': False,
                                '_nef_peak.position_13': False,
                                '_nef_peak.position_uncertainty_13': False,
                                '_nef_peak.position_14': False,
                                '_nef_peak.position_uncertainty_14': False,
                                '_nef_peak.position_15': False,
                                '_nef_peak.position_uncertainty_15': False,
                                '_nef_peak.chain_code_1': False,
                                '_nef_peak.sequence_code_1': False,
                                '_nef_peak.residue_name_1': False,
                                '_nef_peak.atom_name_1': False,
                                '_nef_peak.chain_code_2': False,
                                '_nef_peak.sequence_code_2': False,
                                '_nef_peak.residue_name_2': False,
                                '_nef_peak.atom_name_2': False,
                                '_nef_peak.chain_code_3': False,
                                '_nef_peak.sequence_code_3': False,
                                '_nef_peak.residue_name_3': False,
                                '_nef_peak.atom_name_3': False,
                                '_nef_peak.chain_code_4': False,
                                '_nef_peak.sequence_code_4': False,
                                '_nef_peak.residue_name_4': False,
                                '_nef_peak.atom_name_4': False,
                                '_nef_peak.chain_code_5': False,
                                '_nef_peak.sequence_code_5': False,
                                '_nef_peak.residue_name_5': False,
                                '_nef_peak.atom_name_5': False,
                                '_nef_peak.chain_code_6': False,
                                '_nef_peak.sequence_code_6': False,
                                '_nef_peak.residue_name_6': False,
                                '_nef_peak.atom_name_6': False,
                                '_nef_peak.chain_code_7': False,
                                '_nef_peak.sequence_code_7': False,
                                '_nef_peak.residue_name_7': False,
                                '_nef_peak.atom_name_7': False,
                                '_nef_peak.chain_code_8': False,
                                '_nef_peak.sequence_code_8': False,
                                '_nef_peak.residue_name_8': False,
                                '_nef_peak.atom_name_8': False,
                                '_nef_peak.chain_code_9': False,
                                '_nef_peak.sequence_code_9': False,
                                '_nef_peak.residue_name_9': False,
                                '_nef_peak.atom_name_9': False,
                                '_nef_peak.chain_code_10': False,
                                '_nef_peak.sequence_code_10': False,
                                '_nef_peak.residue_name_10': False,
                                '_nef_peak.atom_name_10': False,
                                '_nef_peak.chain_code_11': False,
                                '_nef_peak.sequence_code_11': False,
                                '_nef_peak.residue_name_11': False,
                                '_nef_peak.atom_name_11': False,
                                '_nef_peak.chain_code_12': False,
                                '_nef_peak.sequence_code_12': False,
                                '_nef_peak.residue_name_12': False,
                                '_nef_peak.atom_name_12': False,
                                '_nef_peak.chain_code_13': False,
                                '_nef_peak.sequence_code_13': False,
                                '_nef_peak.residue_name_13': False,
                                '_nef_peak.atom_name_13': False,
                                '_nef_peak.chain_code_14': False,
                                '_nef_peak.sequence_code_14': False,
                                '_nef_peak.residue_name_14': False,
                                '_nef_peak.atom_name_14': False,
                                '_nef_peak.chain_code_15': False,
                                '_nef_peak.sequence_code_15': False,
                                '_nef_peak.residue_name_15': False,
                                '_nef_peak.atom_name_15': False,
                                '_nef_peak_restraint_links.sf_category': True,
                                '_nef_peak_restraint_links.sf_framecode': True,
                                '_nef_peak_restraint_link.nmr_spectrum_id': True,
                                '_nef_peak_restraint_link.peak_id': True,
                                '_nef_peak_restraint_link.restraint_list_id': True,
                                '_nef_peak_restraint_link.restraint_id': True,
                                '_audit.revision_id': True,  # add support for _audit loop in NEF (DAOTHER-6327)
                                '_audit.creation_date': False,
                                '_audit.creation_method': False,
                                '_audit.update_record': False
                                }

        # self.starMandatoryTag = self.load_csv_data(libDirPath + 'NMR-STAR_mandatory.csv')
        # """
        # self.starMandatorySfCat = {'entry_information': True,
        #                            'Related_entries': False,
        #                            'Software_applied_methods': False,
        #                            'History': False,
        #                            'assembly': True,
        #                            'Chem_comp_assembly': True,
        #                            'Bond': False,
        #                            'assigned_chemical_shifts': True,
        #                            'Atom_chem_shift': True,
        #                            'general_distance_constraints': False,
        #                            'Gen_dist_constraint': False,
        #                            'torsion_angle_constraints': False,
        #                            'Torsion_angle_constraint': False,
        #                            'RDC_constraints': False,
        #                            'RDC_constraint': False,
        #                            'spectral_peak_list': False,
        #                            'Spectral_dim': True,
        #                            'Spectral_dim_transfer': True,
        #                            'Peak_row_format': False,
        #                            'peak_constraint_links': False,
        #                            'Peak_constraint_link': False,
        #                            'Audit': False
        #                            }
        # """
        self.starMandatoryTag = {'_Entry.Sf_category': True,
                                 '_Entry.Sf_framecode': True,
                                 '_Entry.Source_data_format': True,
                                 '_Entry.Source_data_format_version': True,
                                 '_Entry.Generated_software_name': True,
                                 '_Entry.Generated_software_version': True,
                                 '_Entry.Generated_date': True,
                                 '_Entry.UUID': True,
                                 '_Entry.Related_coordinate_file_name': False,
                                 '_Related_entries.Database_name': True,
                                 '_Related_entries.Database_accession_code': True,
                                 '_Software_applied_methods.Software_name': True,
                                 '_Software_applied_methods.Script_name': False,
                                 '_Software_applied_methods.Script': False,
                                 '_History.Run_number': True,
                                 '_History.Software_name': True,
                                 '_History.Software_version': False,
                                 '_History.Script_name': False,
                                 '_History.Script': False,
                                 '_Assembly.Sf_category': True,
                                 '_Assembly.Sf_framecode': True,
                                 '_Chem_comp_assembly.NEF_index': True,
                                 '_Chem_comp_assembly.Entity_assembly_ID': True,
                                 '_Chem_comp_assembly.Comp_index_ID': True,
                                 '_Chem_comp_assembly.Comp_ID': True,
                                 '_Chem_comp_assembly.Sequence_linking': False,
                                 '_Chem_comp_assembly.Auth_variant_ID': False,
                                 '_Chem_comp_assembly.Cis_residue': False,
                                 '_Bond.Entity_assembly_ID_1': True,
                                 '_Bond.Comp_index_ID_1': True,
                                 '_Bond.Comp_ID_1': True,
                                 '_Bond.Atom_ID_1': True,
                                 '_Bond.Entity_assembly_ID_2': True,
                                 '_Bond.Comp_index_ID_2': True,
                                 '_Bond.Comp_ID_2': True,
                                 '_Bond.Atom_ID_2': True,
                                 '_Assigned_chem_shift_list.Sf_category': True,
                                 '_Assigned_chem_shift_list.Sf_framecode': True,
                                 '_Atom_chem_shift.Entity_assembly_ID': True,
                                 '_Atom_chem_shift.Comp_index_ID': True,
                                 '_Atom_chem_shift.Comp_ID': True,
                                 '_Atom_chem_shift.Atom_ID': True,
                                 '_Atom_chem_shift.Val': True,
                                 '_Atom_chem_shift.Val_err': False,
                                 '_Atom_chem_shift.Atom_type': False,
                                 '_Atom_chem_shift.Atom_isotope_number': False,
                                 '_Gen_dist_constraint_list.Sf_category': True,
                                 '_Gen_dist_constraint_list.Sf_framecode': True,
                                 '_Gen_dist_constraint_list.Potential_type': True,
                                 '_Gen_dist_constraint_list.Constraint_type': False,
                                 '_Gen_dist_constraint.Index_ID': True,
                                 '_Gen_dist_constraint.ID': True,
                                 '_Gen_dist_constraint.Combination_ID': False,
                                 '_Gen_dist_constraint.Entity_assembly_ID_1': True,
                                 '_Gen_dist_constraint.Comp_index_ID_1': True,
                                 '_Gen_dist_constraint.Comp_ID_1': True,
                                 '_Gen_dist_constraint.Atom_ID_1': True,
                                 '_Gen_dist_constraint.Entity_assembly_ID_2': True,
                                 '_Gen_dist_constraint.Comp_index_ID_2': True,
                                 '_Gen_dist_constraint.Comp_ID_2': True,
                                 '_Gen_dist_constraint.Atom_ID_2': True,
                                 '_Gen_dist_constraint.Weight': True,
                                 '_Gen_dist_constraint.Target_val': False,
                                 '_Gen_dist_constraint.Target_val_uncertainty': False,
                                 '_Gen_dist_constraint.Lower_linear_limit': False,
                                 '_Gen_dist_constraint.Distance_lower_bound_val': False,
                                 '_Gen_dist_constraint.Distance_upper_bound_val': False,
                                 '_Gen_dist_constraint.Upper_linear_limit': False,
                                 '_Torsion_angle_constraint_list.Sf_category': True,
                                 '_Torsion_angle_constraint_list.Sf_framecode': True,
                                 '_Torsion_angle_constraint_list.Potential_type': True,
                                 '_Torsion_angle_constraint_list.Constraint_type': False,
                                 '_Torsion_angle_constraint.Index_ID': True,
                                 '_Torsion_angle_constraint.ID': True,
                                 '_Torsion_angle_constraint.Combination_ID': False,
                                 '_Torsion_angle_constraint.Entity_assembly_ID_1': True,
                                 '_Torsion_angle_constraint.Comp_index_ID_1': True,
                                 '_Torsion_angle_constraint.Comp_ID_1': True,
                                 '_Torsion_angle_constraint.Atom_ID_1': True,
                                 '_Torsion_angle_constraint.Entity_assembly_ID_2': True,
                                 '_Torsion_angle_constraint.Comp_index_ID_2': True,
                                 '_Torsion_angle_constraint.Comp_ID_2': True,
                                 '_Torsion_angle_constraint.Atom_ID_2': True,
                                 '_Torsion_angle_constraint.Entity_assembly_ID_3': True,
                                 '_Torsion_angle_constraint.Comp_index_ID_3': True,
                                 '_Torsion_angle_constraint.Comp_ID_3': True,
                                 '_Torsion_angle_constraint.Atom_ID_3': True,
                                 '_Torsion_angle_constraint.Entity_assembly_ID_4': True,
                                 '_Torsion_angle_constraint.Comp_index_ID_4': True,
                                 '_Torsion_angle_constraint.Comp_ID_4': True,
                                 '_Torsion_angle_constraint.Atom_ID_4': True,
                                 '_Torsion_angle_constraint.Weight': True,
                                 '_Torsion_angle_constraint.Angle_target_val': False,
                                 '_Torsion_angle_constraint.Angle_target_val_err': False,
                                 '_Torsion_angle_constraint.Angle_lower_linear_limit': False,
                                 '_Torsion_angle_constraint.Angle_lower_bound_val': False,
                                 '_Torsion_angle_constraint.Angle_upper_bound_val': False,
                                 '_Torsion_angle_constraint.Angle_upper_linear_limit': False,
                                 '_Torsion_angle_constraint.Torsion_angle_name': False,
                                 '_RDC_constraint_list.Sf_category': True,
                                 '_RDC_constraint_list.Sf_framecode': True,
                                 '_RDC_constraint_list.Potential_type': True,
                                 '_RDC_constraint_list.Constraint_type': False,
                                 '_RDC_constraint_list.Tensor_magnitude': False,
                                 '_RDC_constraint_list.Tensor_rhombicity': False,
                                 '_RDC_constraint_list.Tensor_Entity_assembly_ID': False,
                                 '_RDC_constraint_list.Tensor_seq_ID': False,
                                 '_RDC_constraint_list.Tensor_comp_ID': False,
                                 '_RDC_constraint.Index_ID': True,
                                 '_RDC_constraint.ID': True,
                                 '_RDC_constraint.Combination_ID': False,
                                 '_RDC_constraint.Entity_assembly_ID_1': True,
                                 '_RDC_constraint.Comp_index_ID_1': True,
                                 '_RDC_constraint.Comp_ID_1': True,
                                 '_RDC_constraint.Atom_ID_1': True,
                                 '_RDC_constraint.Entity_assembly_ID_2': True,
                                 '_RDC_constraint.Comp_index_ID_2': True,
                                 '_RDC_constraint.Comp_ID_2': True,
                                 '_RDC_constraint.Atom_ID_2': True,
                                 '_RDC_constraint.Weight': True,
                                 '_RDC_constraint.Target_value': False,
                                 '_RDC_constraint.Target_value_uncertainty': False,
                                 '_RDC_constraint.RDC_lower_linear_limit': False,
                                 '_RDC_constraint.RDC_lower_bound': False,
                                 '_RDC_constraint.RDC_upper_bound': False,
                                 '_RDC_constraint.RDC_upper_linear_limit': False,
                                 '_RDC_constraint.RDC_val_scale_factor': False,
                                 '_RDC_constraint.RDC_distant_dependent': False,
                                 '_Spectral_peak_list.Sf_category': True,
                                 '_Spectral_peak_list.Sf_framecode': True,
                                 '_Spectral_peak_list.Number_of_spectral_dimensions': False,
                                 '_Spectral_peak_list.Chemical_shift_list': False,
                                 '_Spectral_peak_list.Experiment_class': False,
                                 '_Spectral_peak_list.Experiment_type': False,
                                 '_Spectral_dim.ID': True,
                                 '_Spectral_dim.Sweep_width_units': True,
                                 '_Spectral_dim.Axis_code': False,
                                 '_Spectral_dim.Spectrometer_frequency': False,
                                 '_Spectral_dim.Sweep_width': False,
                                 '_Spectral_dim.Value_first_point': False,
                                 '_Spectral_dim.Under_sampling_type': False,
                                 '_Spectral_dim.Absolute_peak_positions': False,
                                 '_Spectral_dim.Acquisition': False,
                                 '_Spectral_dim_transfer.Spectral_dim_ID_1': True,
                                 '_Spectral_dim_transfer.Spectral_dim_ID_2': True,
                                 '_Spectral_dim_transfer.Type': True,
                                 '_Spectral_dim_transfer.Indirect': False,
                                 '_Peak_row_format.Index_ID': True,
                                 '_Peak_row_format.ID': True,
                                 '_Peak_row_format.Volume': False,
                                 '_Peak_row_format.Volume_uncertainty': False,
                                 '_Peak_row_format.Height': False,
                                 '_Peak_row_format.Height_uncertainty': False,
                                 '_Peak_row_format.Position_1': False,
                                 '_Peak_row_format.Position_uncertainty_1': False,
                                 '_Peak_row_format.Position_2': False,
                                 '_Peak_row_format.Position_uncertainty_2': False,
                                 '_Peak_row_format.Position_3': False,
                                 '_Peak_row_format.Position_uncertainty_3': False,
                                 '_Peak_row_format.Position_4': False,
                                 '_Peak_row_format.Position_uncertainty_4': False,
                                 '_Peak_row_format.Position_5': False,
                                 '_Peak_row_format.Position_uncertainty_5': False,
                                 '_Peak_row_format.Position_6': False,
                                 '_Peak_row_format.Position_uncertainty_6': False,
                                 '_Peak_row_format.Position_7': False,
                                 '_Peak_row_format.Position_uncertainty_7': False,
                                 '_Peak_row_format.Position_8': False,
                                 '_Peak_row_format.Position_uncertainty_8': False,
                                 '_Peak_row_format.Position_9': False,
                                 '_Peak_row_format.Position_uncertainty_9': False,
                                 '_Peak_row_format.Position_10': False,
                                 '_Peak_row_format.Position_uncertainty_10': False,
                                 '_Peak_row_format.Position_11': False,
                                 '_Peak_row_format.Position_uncertainty_11': False,
                                 '_Peak_row_format.Position_12': False,
                                 '_Peak_row_format.Position_uncertainty_12': False,
                                 '_Peak_row_format.Position_13': False,
                                 '_Peak_row_format.Position_uncertainty_13': False,
                                 '_Peak_row_format.Position_14': False,
                                 '_Peak_row_format.Position_uncertainty_14': False,
                                 '_Peak_row_format.Position_15': False,
                                 '_Peak_row_format.Position_uncertainty_15': False,
                                 '_Peak_row_format.Entity_assembly_ID_1': False,
                                 '_Peak_row_format.Comp_index_ID_1': False,
                                 '_Peak_row_format.Comp_ID_1': False,
                                 '_Peak_row_format.Atom_ID_1': False,
                                 '_Peak_row_format.Entity_assembly_ID_2': False,
                                 '_Peak_row_format.Comp_index_ID_2': False,
                                 '_Peak_row_format.Comp_ID_2': False,
                                 '_Peak_row_format.Atom_ID_2': False,
                                 '_Peak_row_format.Entity_assembly_ID_3': False,
                                 '_Peak_row_format.Comp_index_ID_3': False,
                                 '_Peak_row_format.Comp_ID_3': False,
                                 '_Peak_row_format.Atom_ID_3': False,
                                 '_Peak_row_format.Entity_assembly_ID_4': False,
                                 '_Peak_row_format.Comp_index_ID_4': False,
                                 '_Peak_row_format.Comp_ID_4': False,
                                 '_Peak_row_format.Atom_ID_4': False,
                                 '_Peak_row_format.Entity_assembly_ID_5': False,
                                 '_Peak_row_format.Comp_index_ID_5': False,
                                 '_Peak_row_format.Comp_ID_5': False,
                                 '_Peak_row_format.Atom_ID_5': False,
                                 '_Peak_row_format.Entity_assembly_ID_6': False,
                                 '_Peak_row_format.Comp_index_ID_6': False,
                                 '_Peak_row_format.Comp_ID_6': False,
                                 '_Peak_row_format.Atom_ID_6': False,
                                 '_Peak_row_format.Entity_assembly_ID_7': False,
                                 '_Peak_row_format.Comp_index_ID_7': False,
                                 '_Peak_row_format.Comp_ID_7': False,
                                 '_Peak_row_format.Atom_ID_7': False,
                                 '_Peak_row_format.Entity_assembly_ID_8': False,
                                 '_Peak_row_format.Comp_index_ID_8': False,
                                 '_Peak_row_format.Comp_ID_8': False,
                                 '_Peak_row_format.Atom_ID_8': False,
                                 '_Peak_row_format.Entity_assembly_ID_9': False,
                                 '_Peak_row_format.Comp_index_ID_9': False,
                                 '_Peak_row_format.Comp_ID_9': False,
                                 '_Peak_row_format.Atom_ID_9': False,
                                 '_Peak_row_format.Entity_assembly_ID_10': False,
                                 '_Peak_row_format.Comp_index_ID_10': False,
                                 '_Peak_row_format.Comp_ID_10': False,
                                 '_Peak_row_format.Atom_ID_10': False,
                                 '_Peak_row_format.Entity_assembly_ID_11': False,
                                 '_Peak_row_format.Comp_index_ID_11': False,
                                 '_Peak_row_format.Comp_ID_11': False,
                                 '_Peak_row_format.Atom_ID_11': False,
                                 '_Peak_row_format.Entity_assembly_ID_12': False,
                                 '_Peak_row_format.Comp_index_ID_12': False,
                                 '_Peak_row_format.Comp_ID_12': False,
                                 '_Peak_row_format.Atom_ID_12': False,
                                 '_Peak_row_format.Entity_assembly_ID_13': False,
                                 '_Peak_row_format.Comp_index_ID_13': False,
                                 '_Peak_row_format.Comp_ID_13': False,
                                 '_Peak_row_format.Atom_ID_13': False,
                                 '_Peak_row_format.Entity_assembly_ID_14': False,
                                 '_Peak_row_format.Comp_index_ID_14': False,
                                 '_Peak_row_format.Comp_ID_14': False,
                                 '_Peak_row_format.Atom_ID_14': False,
                                 '_Peak_row_format.Entity_assembly_ID_15': False,
                                 '_Peak_row_format.Comp_index_ID_15': False,
                                 '_Peak_row_format.Comp_ID_15': False,
                                 '_Peak_row_format.Atom_ID_15': False,
                                 '_Peak_constraint_link_list.Sf_category': True,
                                 '_Peak_constraint_link_list.Sf_framecode': True,
                                 '_Peak_constraint_link.Spectral_Peak_list_Sf_framecode': True,
                                 '_Peak_constraint_link.Peak_ID': True,
                                 '_Peak_constraint_link.Constraint_Sf_framecode': True,
                                 '_Peak_constraint_link.Constraint_ID': True,
                                 '_Audit.Revision_ID': True,  # add support for _audit loop in NEF (DAOTHER-6327)
                                 '_Audit.Creation_date': False,
                                 '_Audit.Creation_method': False,
                                 '_Audit.Update_record': False
                                 }

        # whether to replace zero by empty if 'void-zero' is set
        self.replace_zero_by_null_in_case = False
        # whether to insert _Atom_chem_shift.Original_PDB_* items
        self.insert_original_pdb_cs_items = True
        # whether to insert Auth_atom_name_* items
        self.insert_original_atom_name_items = True

        # temporary dictionaries used in translation
        self.authChainId = None
        self.authSeqMap = None
        self.selfSeqMap = None
        self.atomIdMap = None

        # DAOTHER-8817: construct pseudo CCD from the coordinates
        self.chemCompAtom = None
        self.chemCompBond = None
        self.chemCompTopo = None
        # DAOTHER-10105: coordinate derived atom name mapping from pdbx_auth_atom_name to auth_atom_id
        self.authAtomNameToId = None

        self.star2NefChainMapping = None
        self.star2CifChainMapping = None

        # Pairwise align
        self.__pA = PairwiseAlign()
        self.__pA.setVerbose(self.__verbose)

        # CCD accessing utility
        self.__ccU = ChemCompUtil(self.__verbose, self.__lfh) if ccU is None else ccU

        # BMRB chemical shift statistics
        self.__csStat = BMRBChemShiftStat(self.__verbose, self.__lfh) if csStat is None else csStat

        # CifToNmrStar
        self.__c2S = CifToNmrStar(self.__lfh) if c2S is None else c2S

        # readable item type
        self.readableItemType = {'str': 'a string',
                                 'bool': 'a boolean value',
                                 'int': 'an integer',
                                 'index-int': 'an unique positive integer',
                                 'positive-int': 'a positive integer',
                                 'positive-int-as-str': 'a positive integer',
                                 'pointer-index': 'an integer acting as a pointer to the parent item',
                                 'float': 'a floating point number',
                                 'positive-float': 'a positive floating point number',
                                 'range-float': 'a floating point number in a specific range',
                                 'enum': 'an enumeration value',
                                 'enum-int': 'an enumeration value restricted to integers'}

        self.__cachedDictForValidStarAtomInXplor = {}
        self.__cachedDictForValidStarAtom = {}
        self.__cachedDictForStarAtom = {}
        self.__cachedDictForNefAtom = {}

    def get_ccu(self):
        """ Get instance of ChemCompUtil.
        """

        return self.__ccU

    def set_remediation_mode(self, flag: bool):
        """ Set remediation mode.
        """

        self.__remediation_mode = flag

    def set_annotation_mode(self, flag: bool):
        """ Set annotation mode.
        """

        self.__annotation_mode = flag

    def set_internal_mode(self, flag: bool):
        """ Set internal mode.
        """

        self.__internal_mode = flag

    def set_merge_rescue_mode(self, flag: bool):
        """ Set merge-rescue mode.
        """

        self.__merge_rescue_mode = flag

    def set_bmrb_only_mode(self, flag: bool):
        """ Set BMRB-only mode.
        """

        self.__bmrb_only = flag

    def allow_missing_dist_restraint(self, flag: bool):
        """ Whether allow missing distance restraint.
        """

        self.__allow_missing_dist_restraint = flag

    def allow_missing_chem_shift(self, flag: bool):
        """ Whether allow missing assigned chemical shift.
        """

        self.__allow_missing_chem_shift = flag

    def set_chem_comp_dict(self, chem_comp_atom: dict, chem_comp_bond: dict, chem_comp_topo: dict, auth_atom_name_to_id: dict):
        """ Set chem_comp dictionary derived from ParserListerUtil.coordAssemblyChecker().
            DAOTHER-8817: construct pseudo CCD from the coordinates
            DAOTHER-10105: add auth_atom_name_to_id to resolve pseudo atom names
        """

        if isinstance(chem_comp_atom, dict):
            self.chemCompAtom = chem_comp_atom

        if isinstance(chem_comp_bond, dict):
            self.chemCompBond = chem_comp_bond

        if isinstance(chem_comp_topo, dict):
            self.chemCompTopo = chem_comp_topo

        if isinstance(auth_atom_name_to_id, dict):
            self.authAtomNameToId = auth_atom_name_to_id

    # def load_csv_data(self, csv_file, transpose=False):
    #     """ Load CSV data to list.
    #         @param cvs_file: input CSV file path
    #         @param transpose: transpose CSV data
    #         @return: list object
    #     """
    #
    #     data_map = []
    #
    #     try:
    #         data = []
    #
    #         with open(csv_file, 'r', encoding='utf-8') as file:
    #             csv_reader = csv.reader(file, delimiter=',')
    #
    #             for r in csv_reader:
    #                 if r[0][0] != '#':
    #                     data.append(r)
    #
    #         data_map = list(map(list, zip(*data))) if transpose else data
    #
    #     except Exception as e:
    #         self.__lfh.write(f"+{self.__class_name__}.load_csv_data() ++ Error  - {str(e)}\n")
    #
    #     return data_map

    def read_input_file(self, in_file: str) -> Tuple[bool, str, Union[pynmrstar.Entry, pynmrstar.Saveframe, pynmrstar.Loop]]:  # pylint: disable=no-self-use
        """ Read input NEF/NMR-STAR file.
            @param in_file: input NEF/NMR-STAR file path
            @return: status, one of {'Entry', 'Saveframe', 'Loop', error message}, data object
        """

        is_ok = True
        data_type = star_data = None

        try:

            star_data = pynmrstar.Entry.from_file(in_file)

        except Exception as e1:

            try:

                star_data = pynmrstar.Saveframe.from_file(in_file)

            except Exception as e2:

                try:

                    star_data = pynmrstar.Loop.from_file(in_file)

                except Exception as e3:

                    is_ok = False

                    if 'The Sf_framecode tag cannot be different from the saveframe name.' in str(e2):
                        data_type = str(e2)
                    elif "Invalid loop. Loops must start with the 'loop_' keyword." not in str(e3) and\
                         "Invalid token found in loop contents" not in str(e3) and\
                         "Illegal value: 'loop_'" not in str(e3):
                        data_type = str(e3)
                    else:
                        data_type = str(e1)

        if is_ok:
            data_type = 'Entry' if isinstance(star_data, pynmrstar.Entry)\
                else ('Saveframe' if isinstance(star_data, pynmrstar.Saveframe) else 'Loop')

        return is_ok, data_type, star_data

    def check_mandatory_tags(self, in_file: str, file_type: str) -> Tuple[List[str], List[str]]:
        """ Returns list of missing mandatory saveframe/loop tags of the input file.
            @change: detect missing mandatory saveframe tags in Saveframe/Loop data as well as Entry data by Masashi Yokochi
            @param in_file: input NEF/NMR-STAR file path
            @param file_type: input file type either 'nef' or 'nmr-star'
            @return: list of missing mandatory saveframe tags, list of missing mandatory loop tags
        """

        mandatoryTag = self.nefMandatoryTag if file_type == 'nef' else self.starMandatoryTag

        missing_sf_tags, missing_lp_tags = [], []

        try:
            star_data = pynmrstar.Entry.from_file(in_file)

            sf_list = [sf.category for sf in star_data.frame_list]

            for k, v in mandatoryTag.items():

                if v:

                    try:
                        tags = star_data.get_tags([k])
                        if len(tags[k]) == 0 and k[1:].split('.')[0] in sf_list:
                            missing_sf_tags.append(k)
                    except Exception:  # ValueError:
                        missing_lp_tags.append(k)

        except Exception:  # ValueError:

            try:
                star_data = pynmrstar.Saveframe.from_file(in_file)

                for k, v in mandatoryTag.items():

                    if v:

                        try:
                            tag = star_data.get_tag(k)
                            if len(tag) == 0 and k[1:].split('.')[0] == star_data.category:
                                missing_sf_tags.append(k)
                        except Exception:  # ValueError:
                            missing_lp_tags.append(k)

            except Exception:  # ValueError:

                try:
                    star_data = pynmrstar.Loop.from_file(in_file)

                    for k, v in mandatoryTag.items():

                        if k[1:].split('.')[0] == star_data.category and v:

                            try:
                                star_data.get_tag(k)
                            except Exception:  # ValueError:
                                missing_lp_tags.append(k)

                except Exception:  # ValueError:
                    pass

        return missing_sf_tags, missing_lp_tags

    def is_mandatory_tag(self, item: str, file_type: str) -> bool:
        """ Return whether a given tag is mandatory.
            @author: Masashi Yokochi
            @param item: item name
            @param file_type: input file type either 'nef' or 'nmr-star'
            @return: True for mandatory tag, False otherwise
        """

        mandatoryTag = self.nefMandatoryTag if file_type == 'nef' else self.starMandatoryTag

        if item not in mandatoryTag:
            return False

        return mandatoryTag[item]

    def validate_file(self, in_file: str, file_subtype: str = 'A', allow_empty: bool = False) -> Tuple[bool, dict]:
        """ Validate input NEF/NMR-STAR file.
            @param infile: input NEF/NMR-STAR file path
            @param file_subtype: should be 'A', 'S', 'R', or 'O'
                , where A for All in one file, S for chemical Shifts file, R for Restraints file, O for Other conventional restraint file
            @return: status, message
        """

        is_valid = True
        info, error = [], []

        file_type = 'unknown'

        err_template_for_missing_mandatory_loop = "The mandatory loop %r is missing. Deposition of %s is mandatory. Please re-upload the %s file."
        err_template_for_empty_mandatory_loop = "The mandatory loop %r is empty. Deposition of %s is mandatory. Please re-upload the %s file."
        err_template_for_empty_mandatory_loop_of_sf = "The mandatory loop %r in saveframe %r is empty. Deposition of %s is mandatory. Please re-upload the %s file."
        warn_template_for_empty_mandatory_loop = "The mandatory loop %r is empty. Please re-upload the %s file."
        warn_template_for_empty_mandatory_loop_of_sf = "The mandatory loop %r in saveframe %r is empty. Please re-upload the %s file."

        try:

            is_ok, data_type, star_data = self.read_input_file(in_file)

            if is_ok:

                minimal_lp_category_nef_a = ['_nef_chemical_shift', '_nef_distance_restraint']
                minimal_lp_category_nef_s = ['_nef_chemical_shift']
                minimal_lp_category_nef_r = ['_nef_distance_restraint']

                minimal_lp_category_star_a = ['_Atom_chem_shift', '_Gen_dist_constraint']
                minimal_lp_category_star_s = [] if self.__allow_missing_chem_shift else ['_Atom_chem_shift']
                minimal_lp_category_star_r = ['_Gen_dist_constraint']
                allowed_lp_category_star_o = ['_Gen_dist_constraint', '_Torsion_angle_constraint', '_RDC_constraint',
                                              '_Homonucl_NOE', '_J_three_bond_constraint', '_RDC',
                                              '_CS_anisotropy', '_Dipolar_coupling',
                                              '_CA_CB_constraint', '_H_chem_shift_constraint',
                                              '_Chem_shift_perturbation', '_Auto_relaxation',
                                              '_Heteronucl_NOE', '_T1', '_T2', '_T1rho', '_Order_param', '_PH_titr_result',
                                              '_Coupling_constant',
                                              '_Cross_correlation_D_CSA', '_Cross_correlation_DD',
                                              '_Other_data']
                if self.__internal_mode:
                    allowed_lp_category_star_o.extend(['_Peak_row_format', '_Peak_char'])

                minimal_sf_category_nef_a = ['nef_chemical_shift_list', 'nef_distance_restraint_list']
                minimal_sf_category_nef_s = ['nef_chemical_shift_list']
                minimal_sf_category_nef_r = ['nef_distance_restraint_list']

                minimal_sf_category_star_a = ['assigned_chemical_shifts', 'general_distance_constraints']
                minimal_sf_category_star_s = [] if self.__allow_missing_chem_shift else ['assigned_chemical_shifts']
                minimal_sf_category_star_r = ['general_distance_constraints']
                allowed_sf_category_star_o = ['general_distance_constraints', 'torsion_angle_constraints', 'RDC_constraints',
                                              'homonucl_NOEs', 'J_three_bond_constraints', 'RDCs',
                                              'chem_shift_anisotropy', 'dipolar_couplings',
                                              'CA_CB_chem_shift_constraints', 'H_chem_shift_constraints',
                                              'chem_shift_perturbation', 'auto_relaxation',
                                              'heteronucl_NOEs', 'heteronucl_T1_relaxation', 'heteronucl_T2_relaxation',
                                              'heteronucl_T1rho_relaxation', 'order_parameters', 'pH_titration',
                                              'coupling_constants',
                                              'dipole_CSA_cross_correlations', 'dipole_dipole_cross_correlations',
                                              'other_data_types']
                if self.__internal_mode:
                    allowed_sf_category_star_o.append('spectral_peak_list')

                if self.__allow_missing_dist_restraint:
                    minimal_lp_category_nef_a = ['_nef_chemical_shift']
                    minimal_lp_category_nef_r = ['']

                    minimal_lp_category_star_a = ['_Atom_chem_shift']
                    minimal_lp_category_star_r = []

                    minimal_sf_category_nef_a = ['nef_chemical_shift_list']
                    minimal_sf_category_nef_r = []

                    minimal_sf_category_star_a = ['assigned_chemical_shifts']
                    minimal_sf_category_star_r = []

                sf_list, lp_list = self.get_inventory_list(star_data)

                info.append(f"{len(sf_list)} saveframes and {len(lp_list)} loops found")

                nef_sf_list = [sf for sf in sf_list if sf is not None and 'nef' in sf]
                nef_lp_list = [lp for lp in lp_list if lp is not None and 'nef' in lp]

                info.append(f"{len(nef_sf_list)} saveframes and {len(nef_lp_list)} loops found with NEF prefix")

                if len(nef_sf_list) > 0 or len(nef_lp_list) > 0:

                    is_nef_file = True
                    info.append(f"{in_file} is a NEF file")
                    file_type = 'nef'

                else:

                    is_nef_file = False
                    info.append(f"{in_file} is an NMR-STAR file")
                    file_type = 'nmr-star'

                _file_type = file_type.upper()

                if is_nef_file:
                    if file_subtype == 'A':

                        for lp_category, sf_category in zip(minimal_lp_category_nef_a, minimal_sf_category_nef_a):
                            content_subtype = 'assigned chemical shifts' if 'shift' in lp_category else 'distance restraints'
                            if lp_category not in lp_list:
                                is_valid = allow_empty
                                error.append(err_template_for_missing_mandatory_loop
                                             % (lp_category, content_subtype, _file_type))
                            else:
                                if is_empty_loop(star_data, lp_category):
                                    is_valid = allow_empty
                                    if data_type == 'Loop':
                                        if count_non_empty_loops(star_data, lp_category) == 0:
                                            error.append(err_template_for_empty_mandatory_loop
                                                         % (lp_category, content_subtype, _file_type))
                                        else:
                                            error.append(warn_template_for_empty_mandatory_loop
                                                         % (lp_category, _file_type))
                                    else:
                                        sf_framecodes = get_sf_tag_values_with_empty_loop(star_data, lp_category, sf_category)
                                        if count_non_empty_loops(star_data, lp_category) == 0:
                                            if len(sf_framecodes) == 1:
                                                error.append(err_template_for_empty_mandatory_loop_of_sf
                                                             % (lp_category, sf_framecodes[0], content_subtype, _file_type))
                                            else:
                                                error.append(err_template_for_empty_mandatory_loop_of_sf
                                                             % (lp_category, sf_framecodes, content_subtype, _file_type))
                                        else:
                                            if len(sf_framecodes) == 1:
                                                error.append(warn_template_for_empty_mandatory_loop_of_sf
                                                             % (lp_category, sf_framecodes[0], _file_type))
                                            else:
                                                error.append(warn_template_for_empty_mandatory_loop_of_sf
                                                             % (lp_category, sf_framecodes, _file_type))

                    elif file_subtype == 'S':
                        content_subtype = 'assigned chemical shifts'

                        for lp_category, sf_category in zip(minimal_lp_category_nef_s, minimal_sf_category_nef_s):
                            if lp_category not in lp_list:
                                is_valid = allow_empty
                                error.append(err_template_for_missing_mandatory_loop
                                             % (lp_category, content_subtype, _file_type))
                            else:
                                if is_empty_loop(star_data, lp_category):
                                    is_valid = allow_empty
                                    if data_type == 'Loop':
                                        if count_non_empty_loops(star_data, lp_category) == 0:
                                            error.append(err_template_for_empty_mandatory_loop
                                                         % (lp_category, content_subtype, _file_type))
                                        else:
                                            error.append(warn_template_for_empty_mandatory_loop
                                                         % (lp_category, _file_type))
                                    else:
                                        sf_framecodes = get_sf_tag_values_with_empty_loop(star_data, lp_category, sf_category)
                                        if count_non_empty_loops(star_data, lp_category) == 0:
                                            if len(sf_framecodes) == 1:
                                                error.append(err_template_for_empty_mandatory_loop_of_sf
                                                             % (lp_category, sf_framecodes[0], content_subtype, _file_type))
                                            else:
                                                error.append(err_template_for_empty_mandatory_loop_of_sf
                                                             % (lp_category, sf_framecodes, content_subtype, _file_type))
                                        else:
                                            if len(sf_framecodes) == 1:
                                                error.append(warn_template_for_empty_mandatory_loop_of_sf
                                                             % (lp_category, sf_framecodes[0], _file_type))
                                            else:
                                                error.append(warn_template_for_empty_mandatory_loop_of_sf
                                                             % (lp_category, sf_framecodes, _file_type))

                    elif file_subtype == 'R':
                        content_subtype = 'distance restraints'

                        for lp_category, sf_category in zip(minimal_lp_category_nef_r, minimal_sf_category_nef_r):
                            if lp_category not in lp_list:
                                is_valid = allow_empty
                                error.append(err_template_for_missing_mandatory_loop
                                             % (lp_category, content_subtype, _file_type))
                            else:
                                if is_empty_loop(star_data, lp_category):
                                    is_valid = allow_empty
                                    if data_type == 'Loop':
                                        if count_non_empty_loops(star_data, lp_category) == 0:
                                            error.append(err_template_for_empty_mandatory_loop
                                                         % (lp_category, content_subtype, _file_type))
                                        else:
                                            error.append(warn_template_for_empty_mandatory_loop
                                                         % (lp_category, _file_type))
                                    else:
                                        sf_framecodes = get_sf_tag_values_with_empty_loop(star_data, lp_category, sf_category)
                                        if count_non_empty_loops(star_data, lp_category) == 0:
                                            if len(sf_framecodes) == 1:
                                                error.append(err_template_for_empty_mandatory_loop_of_sf
                                                             % (lp_category, sf_framecodes[0], content_subtype, _file_type))
                                            else:
                                                error.append(err_template_for_empty_mandatory_loop_of_sf
                                                             % (lp_category, sf_framecodes, content_subtype, _file_type))
                                        else:
                                            if len(sf_framecodes) == 1:
                                                error.append(warn_template_for_empty_mandatory_loop_of_sf
                                                             % (lp_category, sf_framecodes[0], _file_type))
                                            else:
                                                error.append(warn_template_for_empty_mandatory_loop_of_sf
                                                             % (lp_category, sf_framecodes, _file_type))

                    else:
                        is_valid = False
                        error.append("file_subtype flag should be one of {'A', 'S', 'R'}.")

                else:
                    if file_subtype == 'A':

                        for lp_category, sf_category in zip(minimal_lp_category_star_a, minimal_sf_category_star_a):
                            content_subtype = 'assigned chemical shifts' if 'shift' in lp_category else 'distance restraints'
                            if lp_category not in lp_list:
                                is_valid = allow_empty
                                error.append(err_template_for_missing_mandatory_loop
                                             % (lp_category, content_subtype, _file_type))
                            else:
                                if is_empty_loop(star_data, lp_category):
                                    is_valid = allow_empty
                                    if data_type == 'Loop':
                                        if count_non_empty_loops(star_data, lp_category) == 0:
                                            error.append(err_template_for_empty_mandatory_loop
                                                         % (lp_category, content_subtype, _file_type))
                                        else:
                                            error.append(warn_template_for_empty_mandatory_loop
                                                         % (lp_category, _file_type))
                                    else:
                                        sf_framecodes = get_sf_tag_values_with_empty_loop(star_data, lp_category, sf_category)
                                        if count_non_empty_loops(star_data, lp_category) == 0:
                                            if len(sf_framecodes) == 1:
                                                error.append(err_template_for_empty_mandatory_loop_of_sf
                                                             % (lp_category, sf_framecodes[0], content_subtype, _file_type))
                                            else:
                                                error.append(err_template_for_empty_mandatory_loop_of_sf
                                                             % (lp_category, sf_framecodes, content_subtype, _file_type))
                                        else:
                                            if len(sf_framecodes) == 1:
                                                error.append(warn_template_for_empty_mandatory_loop_of_sf
                                                             % (lp_category, sf_framecodes[0], _file_type))
                                            else:
                                                error.append(warn_template_for_empty_mandatory_loop_of_sf
                                                             % (lp_category, sf_framecodes, _file_type))

                    elif file_subtype == 'S':
                        content_subtype = 'assigned chemical shifts'

                        for lp_category, sf_category in zip(minimal_lp_category_star_s, minimal_sf_category_star_s):
                            if lp_category not in lp_list:
                                is_valid = allow_empty
                                error.append(err_template_for_missing_mandatory_loop
                                             % (lp_category, content_subtype, _file_type))
                            else:
                                if is_empty_loop(star_data, lp_category):
                                    is_valid = allow_empty
                                    if data_type == 'Loop':
                                        if count_non_empty_loops(star_data, lp_category) == 0:
                                            error.append(err_template_for_empty_mandatory_loop
                                                         % (lp_category, content_subtype, _file_type))
                                        else:
                                            error.append(warn_template_for_empty_mandatory_loop
                                                         % (lp_category, _file_type))
                                    else:
                                        sf_framecodes = get_sf_tag_values_with_empty_loop(star_data, lp_category, sf_category)
                                        if count_non_empty_loops(star_data, lp_category) == 0:
                                            if len(sf_framecodes) == 1:
                                                error.append(err_template_for_empty_mandatory_loop_of_sf
                                                             % (lp_category, sf_framecodes[0], content_subtype, _file_type))
                                            else:
                                                error.append(err_template_for_empty_mandatory_loop_of_sf
                                                             % (lp_category, sf_framecodes, content_subtype, _file_type))
                                        else:
                                            if len(sf_framecodes) == 1:
                                                error.append(warn_template_for_empty_mandatory_loop_of_sf
                                                             % (lp_category, sf_framecodes[0], _file_type))
                                            else:
                                                error.append(warn_template_for_empty_mandatory_loop_of_sf
                                                             % (lp_category, sf_framecodes, _file_type))

                    elif file_subtype == 'R':
                        content_subtype = 'distance restraints'

                        for lp_category, sf_category in zip(minimal_lp_category_star_r, minimal_sf_category_star_r):
                            if lp_category not in lp_list:
                                is_valid = allow_empty
                                error.append(err_template_for_missing_mandatory_loop
                                             % (lp_category, content_subtype, _file_type))
                            else:
                                if is_empty_loop(star_data, lp_category):
                                    is_valid = allow_empty
                                    if data_type == 'Loop':
                                        if count_non_empty_loops(star_data, lp_category) == 0:
                                            error.append(err_template_for_empty_mandatory_loop
                                                         % (lp_category, content_subtype, _file_type))
                                        else:
                                            error.append(warn_template_for_empty_mandatory_loop
                                                         % (lp_category, _file_type))
                                    else:
                                        sf_framecodes = get_sf_tag_values_with_empty_loop(star_data, lp_category, sf_category)
                                        if count_non_empty_loops(star_data, lp_category) == 0:
                                            if len(sf_framecodes) == 1:
                                                error.append(err_template_for_empty_mandatory_loop_of_sf
                                                             % (lp_category, sf_framecodes[0], content_subtype, _file_type))
                                            else:
                                                error.append(err_template_for_empty_mandatory_loop_of_sf
                                                             % (lp_category, sf_framecodes, content_subtype, _file_type))
                                        else:
                                            if len(sf_framecodes) == 1:
                                                error.append(warn_template_for_empty_mandatory_loop_of_sf
                                                             % (lp_category, sf_framecodes[0], _file_type))
                                            else:
                                                error.append(warn_template_for_empty_mandatory_loop_of_sf
                                                             % (lp_category, sf_framecodes, _file_type))

                    elif file_subtype == 'O':  # DAOTHER-7545, issue #2
                        is_valid = allow_empty
                        for lp_category in allowed_lp_category_star_o:
                            if lp_category in lp_list and not is_empty_loop(star_data, lp_category):
                                is_valid = True
                        if not is_valid:
                            error.append(f"One of the mandatory loops {allowed_lp_category_star_o} is missing. "
                                         f"Please re-upload the {_file_type} file.")
                        else:
                            for lp_category, sf_category in zip(allowed_lp_category_star_o, allowed_sf_category_star_o):
                                if lp_category in lp_list:
                                    if is_empty_loop(star_data, lp_category):
                                        is_valid = allow_empty
                                        if data_type == 'Loop':
                                            error.append(warn_template_for_empty_mandatory_loop
                                                         % (lp_category, _file_type))
                                        else:
                                            sf_framecodes = get_sf_tag_values_with_empty_loop(star_data, lp_category, sf_category)
                                            if len(sf_framecodes) == 1:
                                                error.append(warn_template_for_empty_mandatory_loop_of_sf
                                                             % (lp_category, sf_framecodes[0], _file_type))
                                            else:
                                                error.append(warn_template_for_empty_mandatory_loop_of_sf
                                                             % (lp_category, sf_framecodes, _file_type))

                    else:
                        is_valid = False
                        error.append("file_subtype flag should be {'A', 'S', 'R', 'O'}.")

            else:
                is_valid = False
                error.append(data_type)

        except Exception as e:
            is_valid = False
            error.append(str(e))

        return is_valid, {'info': info, 'error': error, 'file_type': file_type}

    def resolve_sf_names_for_cif(self, star_data: Union[pynmrstar.Entry, pynmrstar.Saveframe, pynmrstar.Loop]  # pylint: disable=no-self-use # DAOTHER-7389, issue #4
                                 ) -> Tuple[bool, List[str], dict]:  # DAOTHER-7389, issue #4
        """ Resolve saveframe names to prevent case-insensitive name collisions occur in CIF format.
            @return: status, list of correction messages, dictionary of saveframe name corrections
        """

        if not isinstance(star_data, pynmrstar.Entry):
            return True, [], {}

        original_names = [sf.name for sf in star_data.frame_list]

        while True:

            lower_names = [sf.name.lower() for sf in star_data.frame_list]
            dup_names = set(n for n in lower_names if lower_names.count(n) > 1)

            if len(dup_names) == 0:
                break

            for dup_name in dup_names:
                idx = 1
                for sf in star_data.frame_list:
                    if sf.name.lower() == dup_name:
                        sf.name = f"{sf.name}_{idx}"
                        idx += 1

        resolved_names = [sf.name for sf in star_data.frame_list]

        messages = []
        corrections = {}

        for original, resolved in zip(original_names, resolved_names):
            if original != resolved:
                messages.append(f"The saveframe name {original!r} has been renamed to {resolved!r} "
                                "in order to prevent case-insensitive name collisions occurring in CIF format.")
                corrections[original] = resolved

        return len(messages) == 0, messages, corrections

    def get_inventory_list(self, star_data: Union[pynmrstar.Entry, pynmrstar.Saveframe, pynmrstar.Loop]  # pylint: disable=no-self-use
                           ) -> Tuple[List[str], List[str]]:
        """ Return lists of saveframe category names and loop category names in an NEF/NMR-STAR file.
            @change: rename the original get_data_content() to get_inventory_list() by Masashi Yokochi
            @return: list of saveframe category names, list of loop category names
        """

        sf_list, lp_list = [], []

        if isinstance(star_data, pynmrstar.Entry):

            for sf in star_data.frame_list:
                sf_list.append(sf.category)

                for lp in sf:
                    lp_list.append(lp.category)

        elif isinstance(star_data, pynmrstar.Saveframe):

            for lp in star_data:
                lp_list.append(lp.category)

        elif star_data is not None:
            lp_list.append(star_data.category)

        return sf_list, lp_list

    def get_nef_seq(self, star_data: Union[pynmrstar.Entry, pynmrstar.Saveframe, pynmrstar.Loop],  # pylint: disable=no-self-use
                    lp_category: str = 'nef_chemical_shift', seq_id='sequence_code', comp_id='residue_name',
                    chain_id: str = 'chain_code', allow_empty: bool = False, allow_gap: bool = False, check_identity: bool = True
                    ) -> List[List[dict]]:
        """ Extract sequence from any given loops in an NEF file.
            @change: re-written by Masashi Yokochi
            @return: list of sequence information for each loop
        """

        if isinstance(star_data, pynmrstar.Entry):
            loops = star_data.get_loops_by_category(lp_category)
        elif isinstance(star_data, pynmrstar.Saveframe):
            loops = [star_data.get_loop(lp_category)]
        else:
            loops = [star_data]

        f = []  # user warnings

        data = []  # data of all loops

        tags = [seq_id, comp_id, chain_id]

        is_dist_lp = 'nef_distance_restraint' in lp_category
        is_dihed_lp = 'nef_dihedral_restraint' in lp_category
        is_target_lp = is_dist_lp or is_dihed_lp

        def skip_empty_value_error(lp, idx):
            if not is_target_lp:
                return False
            if is_dist_lp and 'residue_name_1' in lp.tags and 'residue_name_2' in lp.tags\
               and (lp.data[idx][lp.tags.index('residue_name_1')] == 'HOH'
                    or lp.data[idx][lp.tags.index('residue_name_2')] == 'HOH'):
                return True
            if is_dihed_lp and 'name' in lp.tags and lp.data[idx][lp.tags.index('name')] == 'PPA':
                return True
            return False

        for loop in loops:
            cmp_dict, seq_dict = {}, {}

            seq_data = []

            len_data = len(loop)

            if set(tags) & set(loop.tags) == set(tags):
                seq_data = loop.get_tag(tags)
                for row in seq_data:
                    if row[2] in emptyValue:
                        row[2] = 1
            else:
                _tags_exist = False
                for j in range(1, MAX_DIM_NUM_OF_SPECTRA):
                    _tags = [seq_id + '_' + str(j), comp_id + '_' + str(j), chain_id + '_' + str(j)]
                    if set(_tags) & set(loop.tags) == set(_tags):
                        _tags_exist = True
                        seq_data += loop.get_tag(_tags)

                if not _tags_exist:
                    missing_tags = list(set(tags) - set(loop.tags))
                    raise LookupError(f"Missing mandatory {missing_tags} loop tag(s).")

            if allow_empty:
                # seq_data = list(filter(is_data, seq_data))
                seq_data = list(filter(is_good_data, seq_data))  # DAOTHER-7389, issue #3
            else:
                for idx, row in enumerate(seq_data):
                    if is_empty(row) and idx < len_data:
                        if skip_empty_value_error(loop, idx):
                            continue
                        r = {}
                        for j, t in enumerate(loop.tags):
                            r[t] = loop.data[idx][j]
                        f.append("[Invalid data] Sequence must not be empty. "
                                 f"#_of_row {idx + 1}, data_of_row {r}.")

            if len(seq_data) == 0:
                continue

            for idx, row in enumerate(seq_data):
                try:
                    int(row[0])
                except (ValueError, TypeError):
                    if idx < len_data:
                        if skip_empty_value_error(loop, idx):
                            continue
                        r = {}
                        for j, t in enumerate(loop.tags):
                            r[t] = loop.data[idx][j]
                        f.append(f"[Invalid data] {seq_id} must be an integer. "
                                 f"#_of_row {idx + 1}, data_of_row {r}.")

            if len(f) > 0:
                raise UserWarning('\n'.join(sorted(list(set(f)), key=f.index)))

            try:

                chain_ids = sorted(set(row[2] for row in seq_data), key=lambda x: (len(x), x))
                offset_seq_ids = {row[2]: 0 for row in seq_data}
                for c in chain_ids:
                    min_seq_id = min(int(row[0]) for row in seq_data if row[2] == c)
                    if min_seq_id < 0:
                        offset_seq_ids[c] = min_seq_id * -1
                sorted_seq = sorted(set((row[2], int(row[0]) + offset_seq_ids[row[2]], row[1].upper()) for row in seq_data),
                                    key=itemgetter(0, 1))

                chk_dict = {(row[2], int(row[0])): row[1].upper() for row in seq_data}

                for row in seq_data:
                    chk_key = (row[2], int(row[0]))
                    if chk_dict[chk_key] != row[1].upper():
                        raise KeyError(f"{lp_category[1:]} loop contains different {comp_id} ({row[1]} and {chk_dict[chk_key]}) "
                                       f"with the same {chain_id} {row[2]}, {seq_id} {row[0]}.")

                for c in chain_ids:
                    cmp_dict[c] = [x[2] for x in sorted_seq if x[0] == c]
                    seq_dict[c] = [x[1] - offset_seq_ids[c] for x in sorted_seq if x[0] == c]

                asm = []  # assembly of a loop

                for c in chain_ids:
                    ent = {}  # entity

                    ent['chain_id'] = str(c)

                    if allow_gap:
                        ent['seq_id'] = []
                        ent['comp_id'] = []

                        _seq_id_ = None

                        for _seq_id, _comp_id in zip(seq_dict[c], cmp_dict[c]):

                            if _seq_id_ is not None and _seq_id_ + 1 != _seq_id and _seq_id_ + 20 > _seq_id:
                                for s in range(_seq_id_ + 1, _seq_id):
                                    ent['seq_id'].append(s)
                                    ent['comp_id'].append('.')
                            ent['seq_id'].append(_seq_id)
                            ent['comp_id'].append(_comp_id)

                            _seq_id_ = _seq_id

                    else:
                        ent['seq_id'] = seq_dict[c]
                        ent['comp_id'] = cmp_dict[c]

                    if len(chain_ids) > 1 and check_identity:
                        identity = []
                        for _c in chain_ids:
                            if _c == c:
                                continue
                            if seq_dict[_c] == seq_dict[c]:
                                if cmp_dict[_c] == cmp_dict[c]:
                                    identity.append(_c)
                            else:
                                common_seq_id = set(seq_dict[_c]) & set(seq_dict[c])
                                if len(common_seq_id) == 0:
                                    continue
                                if any(s for s in common_seq_id
                                       if s in seq_dict[_c] and s in seq_dict[c]
                                       and cmp_dict[_c][seq_dict[_c].index(s)] != cmp_dict[c][seq_dict[c].index(s)]):
                                    continue
                                if not any(s for s in common_seq_id
                                           if s in seq_dict[_c] and s in seq_dict[c]
                                           and cmp_dict[_c][seq_dict[_c].index(s)] == cmp_dict[c][seq_dict[c].index(s)]):
                                    continue
                                identity.append(_c)
                        if len(identity) > 0:
                            ent['identical_chain_id'] = identity

                    asm.append(ent)

                data.append(asm)

            except (ValueError, TypeError):
                pass

        if len(data) == 0:
            data.append([])

        return data

    def get_star_seq(self, star_data: Union[pynmrstar.Entry, pynmrstar.Saveframe, pynmrstar.Loop],
                     lp_category: str = 'Atom_chem_shift', seq_id: str = 'Comp_index_ID', comp_id: str = 'Comp_ID',  # pylint: disable=no-self-use
                     chain_id='Entity_assembly_ID', alt_seq_id='Seq_ID', alt_seq_id_offset=0, alt_chain_id='Auth_asym_ID',
                     allow_empty: bool = False, allow_gap: bool = False, check_identity: bool = True,
                     coord_assembly_checker: Optional[dict] = None) -> List[List[dict]]:
        """ Extract sequence from any given loops in an NMR-STAR file.
            @change: re-written by Masashi Yokochi
            @return: list of sequence information for each loop
        """

        if isinstance(star_data, pynmrstar.Entry):
            loops = star_data.get_loops_by_category(lp_category)
        elif isinstance(star_data, pynmrstar.Saveframe):
            loops = [star_data.get_loop(lp_category)]
        else:
            loops = [star_data]

        f = []  # user warnings

        def_chain_id = 'A' if self.__remediation_mode else '1'

        data = []  # data of all loops

        tags = [seq_id, comp_id, chain_id]
        tags_ = [seq_id, comp_id]
        tags__ = [seq_id, comp_id, alt_chain_id]  # DAOTHER-7421

        is_dist_lp = 'Gen_dist_constraint' in lp_category
        is_dihed_lp = 'Torsion_angle_constraint' in lp_category
        is_target_lp = is_dist_lp or is_dihed_lp

        def skip_empty_value_error(lp, idx):
            if not is_target_lp:
                return False
            if is_dist_lp and 'Auth_comp_ID_1' in lp.tags and 'Auth_comp_ID_2' in lp.tags\
               and (lp.data[idx][lp.tags.index('Auth_comp_ID_1')] == 'HOH'
                    or lp.data[idx][lp.tags.index('Auth_comp_ID_2')] == 'HOH'):
                return True
            if is_dihed_lp and 'Torsion_angle_name' in lp.tags and lp.data[idx][lp.tags.index('Torsion_angle_name')] == 'PPA':
                return True
            return False

        for loop in loops:
            cmp_dict, seq_dict, lig_to_chain_id = {}, {}, {}

            seq_data = []

            len_data = len(loop)

            has_auth_asym_id = False
            if lp_category == '_Atom_chem_shift' and self.__remediation_mode:
                alt_chain_id_set = set()
                if 'Auth_asym_ID' in loop.tags:
                    pre_tag = ['Auth_asym_ID']
                    pre_chain_data = loop.get_tag(pre_tag)
                    for row in pre_chain_data:
                        if row not in emptyValue:
                            alt_chain_id_set.add(row)
                has_auth_asym_id = len(alt_chain_id_set) > 0

                # fix wrong biocuration seen in 8ofc_cs.str
                if set(tags) & set(loop.tags) == set(tags):
                    pre_seq_data = loop.get_tag(tags)
                    if not isinstance(pre_seq_data[0][0], int):
                        if all(row[0] not in emptyValue and not row[0].isdigit()
                               and row[1] not in emptyValue and row[1].isdigit() for row in pre_seq_data):
                            col0 = loop.tags.index(tags[0])
                            col1 = loop.tags.index(tags[1])
                            for row in loop:
                                row[col0], row[col1] = row[col1], row[col0]

                if coord_assembly_checker is not None:
                    cif_np = coord_assembly_checker['non_polymer']
                    if cif_np is not None:
                        ligands = []
                        for np in cif_np:
                            ligands.extend(np['comp_id'])
                            if np['comp_id'] != np['auth_comp_id']:
                                ligands.extend(np['auth_comp_id'])
                        for _comp_id in set(ligands):
                            if ligands.count(_comp_id) == 1:
                                lig_to_chain_id[_comp_id] = next(np['auth_chain_id'] for np in cif_np if _comp_id in np['comp_id'] or _comp_id in np['auth_comp_id'])

                    if 'Auth_asym_ID' not in loop.tags and 'Entity_assembly_ID' not in loop.tags\
                       and len(coord_assembly_checker['polymer_sequence']) > 1\
                       and coord_assembly_checker['non_polymer'] is None:
                        for row in loop:
                            row.append(def_chain_id)
                        loop.add_tag('Entity_assembly_ID')

                # convert protonated DC -> DNR, protonated C -> CH
                if 'Atom_ID' in loop.tags and 'Auth_comp_ID' not in loop.tags\
                   and set(tags) & set(loop.tags) == set(tags):
                    pre_tags = copy.deepcopy(tags)
                    pre_tags.append('Atom_ID')
                    pre_seq_data = loop.get_tag(pre_tags)
                    has_dc_h3 = has_c_h3 = False
                    dnr_set = set()
                    ch_set = set()
                    for row in pre_seq_data:
                        if row[3] in ('H3', 'H3+'):
                            if row[1] in dnrParentCode:
                                has_dc_h3 = True
                                seq_key = (row[2], row[0])
                                dnr_set.add(seq_key)
                            elif row[1] in chParentCode:
                                has_c_h3 = True
                                seq_key = (row[2], row[0])
                                ch_set.add(seq_key)
                    comp_id_col = loop.tags.index('Comp_ID')
                    if has_dc_h3:
                        for idx, row in enumerate(pre_seq_data):
                            if row[1] in dnrParentCode:
                                seq_key = (row[2], row[0])
                                if seq_key in dnr_set:
                                    loop.data[idx][comp_id_col] = 'DNR'
                    if has_c_h3:
                        for idx, row in enumerate(pre_seq_data):
                            if row[1] in chParentCode:
                                seq_key = (row[2], row[0])
                                if seq_key in ch_set:
                                    loop.data[idx][comp_id_col] = 'CH'

                elif 'Atom_ID' in loop.tags and 'Auth_comp_ID' in loop.tags\
                        and set(tags) & set(loop.tags) == set(tags):
                    pre_tags = copy.deepcopy(tags)
                    pre_tags.append('Atom_ID')
                    pre_seq_data = loop.get_tag(pre_tags)
                    has_dc_h3 = has_c_h3 = False
                    dnr_set = set()
                    ch_set = set()
                    for row in pre_seq_data:
                        if row[3] in ('H3', 'H3+'):
                            if row[1] in dnrParentCode:
                                has_dc_h3 = True
                                seq_key = (row[2], row[0])
                                dnr_set.add(seq_key)
                            elif row[1] in chParentCode:
                                has_c_h3 = True
                                seq_key = (row[2], row[0])
                                ch_set.add(seq_key)
                    comp_id_col = loop.tags.index('Comp_ID')
                    auth_comp_id_col = loop.tags.index('Auth_comp_ID')
                    if has_dc_h3:
                        for idx, row in enumerate(pre_seq_data):
                            if row[1] in dnrParentCode:
                                seq_key = (row[2], row[0])
                                if seq_key in dnr_set:
                                    loop.data[idx][comp_id_col] = loop.data[idx][auth_comp_id_col] = 'DNR'
                    if has_c_h3:
                        for idx, row in enumerate(pre_seq_data):
                            if row[1] in chParentCode:
                                seq_key = (row[2], row[0])
                                if seq_key in ch_set:
                                    loop.data[idx][comp_id_col] = loop.data[idx][auth_comp_id_col] = 'CH'
                    pre_tags = ['Comp_ID', 'Auth_comp_ID']
                    pre_seq_data = loop.get_tag(pre_tags)
                    for idx, row in enumerate(pre_seq_data):
                        _comp_id, _auth_comp_id = row
                        if _comp_id not in emptyValue:
                            __comp_id = _comp_id.upper()
                            if __comp_id != _comp_id:
                                loop.data[idx][comp_id_col] = __comp_id
                        if _auth_comp_id not in emptyValue:
                            __auth_comp_id = _auth_comp_id.upper()
                            if __auth_comp_id != _auth_comp_id:
                                loop.data[idx][auth_comp_id_col] = __auth_comp_id

            if lp_category == '_Atom_chem_shift' and self.__remediation_mode and has_auth_asym_id\
               and set(tags) & set(loop.tags) == set(tags) and set(tags__) & set(loop.tags) == set(tags__):
                factor = max(len(alt_chain_id_set), 2)  # 2lnh
                if seq_id != alt_seq_id and alt_seq_id in loop.tags:
                    pre_tags = [seq_id, alt_seq_id]
                    pre_seq_data = loop.get_tag(pre_tags)
                    seq_id_set = set()
                    alt_seq_id_set = set()
                    for row in pre_seq_data:
                        seq_id_set.add(row[0])
                        alt_seq_id_set.add(row[1])
                    if 0 < len(seq_id_set) < len(alt_seq_id_set) // factor:  # 2kyb
                        seq_id_col = loop.tags.index('Comp_index_ID')
                        alt_seq_id_col = loop.tags.index('Seq_ID')
                        for r in loop.data:
                            r[seq_id_col] = r[alt_seq_id_col]

                    elif 'Auth_seq_ID' in loop.tags:
                        pre_tag = ['Auth_seq_ID']
                        pre_seq_data = loop.get_tag(pre_tag)
                        alt_seq_id_set = set()
                        for row in pre_seq_data:
                            alt_seq_id_set.add(row)
                        if 0 < len(seq_id_set) < len(alt_seq_id_set) // factor:  # 6wux, 2lnh
                            seq_id_col = loop.tags.index('Comp_index_ID')
                            alt_seq_id_col = loop.tags.index('Auth_seq_ID')
                            for r in loop.data:
                                r[seq_id_col] = r[alt_seq_id_col]

                if 'Entity_assembly_ID' in loop.tags and 'Auth_asym_ID' in loop.tags:
                    pre_tag = ['Entity_assembly_ID']
                    pre_chain_data = loop.get_tag(pre_tag)
                    chain_id_set = set()
                    for row in pre_chain_data:
                        if row not in emptyValue:
                            chain_id_set.add(row)

                    if coord_assembly_checker is not None:

                        def resolve_entity_assembly(_loop, _alt_chain_id_list, sync_seq):
                            if 'Auth_seq_ID' in _loop.tags:
                                comp_id_col = _loop.tags.index('Comp_ID')
                                pre_tags = [alt_chain_id, 'Auth_seq_ID', 'Comp_ID']
                                if 'Auth_comp_ID' in _loop.tags:
                                    pre_tags.append('Auth_comp_ID')
                                pre_seq_data = _loop.get_tag(pre_tags)
                                cif_ps = coord_assembly_checker['polymer_sequence']
                                cif_np = coord_assembly_checker['non_polymer']
                                nmr_ps = []
                                for c in _alt_chain_id_list:
                                    nmr_ps.append({'chain_id': c, 'seq_id': [], 'comp_id': []})
                                seq = set()

                                valid = True
                                for idx, row in enumerate(pre_seq_data):
                                    if row[0] in emptyValue or row[1] in emptyValue or row[2] in emptyValue:
                                        valid = False
                                        break
                                    try:
                                        _ref_comp_id = row[3] if len(row) > 3 else None
                                        ref_comp_id = row[2].upper()
                                        can_comp_id = translateToStdResName(ref_comp_id, refCompId=_ref_comp_id, ccU=self.__ccU)
                                        seq.add((row[0], int(row[1]), can_comp_id))
                                        if ref_comp_id != can_comp_id:  # 7zew, 7zex
                                            ref_comp_id_not_found, can_comp_id_found = True, False
                                            for ps in cif_ps:
                                                if can_comp_id in ps['comp_id']:
                                                    can_comp_id_found = True
                                                if ref_comp_id in ps['comp_id'] or ref_comp_id in ps['auth_comp_id']:
                                                    ref_comp_id_not_found = False
                                                    break
                                            if cif_np is not None and ref_comp_id_not_found:
                                                for np in cif_np:
                                                    if can_comp_id in np['comp_id']:
                                                        can_comp_id_found = True
                                                    if ref_comp_id in np['comp_id'] or ref_comp_id in np['auth_comp_id']:
                                                        ref_comp_id_not_found = False
                                                        break
                                            if ref_comp_id_not_found and can_comp_id_found:  # 6alt
                                                _loop.data[idx][comp_id_col] = can_comp_id
                                    except ValueError:
                                        valid = False
                                        break

                                if valid:
                                    sorted_seq = sorted(seq, key=itemgetter(0, 1))
                                    for row in sorted_seq:
                                        c = row[0]
                                        _nmr_ps = nmr_ps[_alt_chain_id_list.index(row[0])]
                                        _nmr_ps['seq_id'].append(row[1])
                                        _nmr_ps['comp_id'].append(row[2])
                                    # 2c34
                                    seq_align, _ = alignPolymerSequence(self.__pA, cif_ps, nmr_ps)
                                    chain_assign, _ = assignPolymerSequence(self.__pA, self.__ccU, 'nmr-star', cif_ps, nmr_ps, seq_align)
                                    for ca in chain_assign:
                                        if ca['matched'] == 0 or ca['conflict'] > 0:
                                            valid = False
                                            break

                                    if valid:
                                        chain_id_col = _loop.tags.index('Entity_assembly_ID')
                                        alt_chain_id_col = _loop.tags.index('Auth_asym_ID')
                                        auth_seq_id_col = _loop.tags.index('Auth_seq_ID')
                                        entity_id_col = _loop.tags.index('Entity_ID') if 'Entity_ID' in _loop.tags else -1
                                        seq_id_col = _loop.tags.index('Comp_index_ID') if 'Comp_index_ID' in _loop.tags else -1
                                        alt_seq_id_col = _loop.tags.index('Seq_ID') if 'Seq_ID' in _loop.tags else -1
                                        orig_chain_id_col = _loop.tags.index('Original_PDB_strand_ID') if 'Original_PDB_strand_ID' in _loop.tags else -1
                                        orig_seq_id_col = _loop.tags.index('Original_PDB_residue_no') if 'Original_PDB_residue_no' in _loop.tags else -1
                                        auth_to_star_seq = coord_assembly_checker['auth_to_star_seq']

                                        rev_seq, _offset = {}, {}
                                        _entity_assembly_id = _entity_id = None

                                        for ca in chain_assign:
                                            if ca['matched'] == 0 or ca['conflict'] > 0:
                                                continue
                                            _entity_assembly_id = _entity_id = None
                                            ref_chain_id = ca['ref_chain_id']
                                            test_chain_id = ca['test_chain_id']
                                            sa = next(sa for sa in seq_align
                                                      if sa['ref_chain_id'] == ref_chain_id
                                                      and sa['test_chain_id'] == test_chain_id)
                                            ps = next(ps for ps in cif_ps if ps['auth_chain_id'] == ref_chain_id)
                                            # if 'identical_auth_chain_id' in ps:
                                            #    continue
                                            for ref_seq_id, mid_code, test_seq_id in zip(sa['ref_seq_id'], sa['mid_code'], sa['test_seq_id']):
                                                if mid_code == '|' and test_seq_id is not None:
                                                    rev_seq_key = (test_chain_id, test_seq_id)
                                                    if rev_seq_key in rev_seq:
                                                        continue
                                                    try:
                                                        rev_seq[rev_seq_key] =\
                                                            (ps['auth_chain_id'],
                                                             next(auth_seq_id for auth_seq_id, _seq_id
                                                                  in zip(ps['auth_seq_id'], ps['seq_id'])
                                                                  if _seq_id == ref_seq_id and isinstance(auth_seq_id, int)))
                                                        if _entity_assembly_id is None:
                                                            auth_seq_id = rev_seq[rev_seq_key][1]
                                                            _rev_seq = rev_seq[rev_seq_key]
                                                            _k = (ps['auth_chain_id'], auth_seq_id, ps['comp_id'][ps['auth_seq_id'].index(auth_seq_id)])
                                                            if _k in auth_to_star_seq:
                                                                _entity_assembly_id, _offset_, _entity_id, _ = auth_to_star_seq[_k]
                                                                _offset_ -= auth_seq_id
                                                                _offset[_entity_assembly_id] = _offset_
                                                    except StopIteration:
                                                        rev_seq[rev_seq_key] = (ps['auth_chain_id'], ref_seq_id)
                                        if any(_offset_ for _offset_ in _offset.values() if _offset_ != 0):
                                            sync_seq = True
                                        for r in _loop.data:
                                            k = (r[alt_chain_id_col], int(r[auth_seq_id_col]))
                                            if k in rev_seq:
                                                _rev_seq = rev_seq[k]
                                                _k = (_rev_seq[0], _rev_seq[1], r[comp_id_col])
                                                if _k in auth_to_star_seq:
                                                    r[alt_chain_id_col], r[auth_seq_id_col] = _rev_seq[0], str(_rev_seq[1])
                                                    if orig_chain_id_col != -1:
                                                        r[orig_chain_id_col] = _rev_seq[0]
                                                    if orig_seq_id_col != -1:
                                                        r[orig_seq_id_col] = str(_rev_seq[1])
                                                    _entity_assembly_id, _seq_id, _entity_id, _ = auth_to_star_seq[_k]
                                                    r[chain_id_col] = str(_entity_assembly_id)
                                                    if entity_id_col != -1:
                                                        r[entity_id_col] = str(_entity_id)
                                                    if sync_seq:
                                                        if seq_id_col != -1:
                                                            r[seq_id_col] = str(_seq_id)
                                                        if alt_seq_id_col != -1:
                                                            r[alt_seq_id_col] = str(_seq_id)
                                                elif _entity_assembly_id in _offset:
                                                    _offset_ = _offset[_entity_assembly_id]
                                                    r[chain_id_col], r[entity_id_col] = str(_entity_assembly_id), str(_entity_id)
                                                    if sync_seq:
                                                        if int(r[seq_id_col]) - int(r[auth_seq_id_col]) == _offset_:
                                                            continue
                                                        if seq_id_col != -1:
                                                            r[seq_id_col] = str(int(r[auth_seq_id_col]) + _offset_)
                                                        if alt_seq_id_col != -1:
                                                            r[alt_seq_id_col] = str(int(r[auth_seq_id_col]) + _offset_)
                                            elif _entity_assembly_id in _offset:  # 2k7b
                                                _offset_ = _offset[_entity_assembly_id]
                                                r[chain_id_col], r[entity_id_col] = str(_entity_assembly_id), str(_entity_id)
                                                if sync_seq:
                                                    if int(r[seq_id_col]) - int(r[auth_seq_id_col]) == _offset_:
                                                        continue
                                                    if seq_id_col != -1:
                                                        r[seq_id_col] = str(int(r[auth_seq_id_col]) + _offset_)
                                                    if alt_seq_id_col != -1:
                                                        r[alt_seq_id_col] = str(int(r[auth_seq_id_col]) + _offset_)
                                    # 2ksi
                                    if cif_np is not None:
                                        seq_align, _ = alignPolymerSequence(self.__pA, cif_np, nmr_ps)
                                        chain_assign, _ = assignPolymerSequence(self.__pA, self.__ccU, 'nmr-star', cif_np, nmr_ps, seq_align)
                                        for ca in chain_assign:
                                            if ca['matched'] == 0 or ca['conflict'] > 0:
                                                valid = False
                                                break

                                        if valid:
                                            rev_seq = {}
                                            for ca in chain_assign:
                                                if ca['matched'] == 0 or ca['conflict'] > 0:
                                                    continue
                                                ref_chain_id = ca['ref_chain_id']
                                                test_chain_id = ca['test_chain_id']
                                                sa = next(sa for sa in seq_align
                                                          if sa['ref_chain_id'] == ref_chain_id
                                                          and sa['test_chain_id'] == test_chain_id)
                                                np = next(np for np in cif_np if np['auth_chain_id'] == ref_chain_id)
                                                for ref_seq_id, mid_code, test_seq_id in zip(sa['ref_seq_id'], sa['mid_code'], sa['test_seq_id']):
                                                    if mid_code == '|' and test_seq_id is not None:
                                                        rev_seq_key = (test_chain_id, test_seq_id)
                                                        if rev_seq_key in rev_seq:
                                                            continue
                                                        try:
                                                            rev_seq[rev_seq_key] =\
                                                                (np['auth_chain_id'],
                                                                 next(auth_seq_id for auth_seq_id, _seq_id
                                                                      in zip(np['auth_seq_id'], np['seq_id'])
                                                                      if _seq_id == ref_seq_id and isinstance(auth_seq_id, int)))
                                                        except StopIteration:
                                                            rev_seq[rev_seq_key] = (np['auth_chain_id'], ref_seq_id)
                                            chain_id_col = _loop.tags.index('Entity_assembly_ID')
                                            alt_chain_id_col = _loop.tags.index('Auth_asym_ID')
                                            auth_seq_id_col = _loop.tags.index('Auth_seq_ID')
                                            comp_id_col = _loop.tags.index('Comp_ID')
                                            entity_id_col = _loop.tags.index('Entity_ID') if 'Entity_ID' in _loop.tags else -1
                                            seq_id_col = _loop.tags.index('Comp_index_ID') if 'Comp_index_ID' in _loop.tags else -1
                                            alt_seq_id_col = _loop.tags.index('Seq_ID') if 'Seq_ID' in _loop.tags else -1
                                            auth_to_star_seq = coord_assembly_checker['auth_to_star_seq']
                                            for r in _loop.data:
                                                k = (r[alt_chain_id_col], int(r[auth_seq_id_col]))
                                                if k in rev_seq:
                                                    _rev_seq = rev_seq[k]
                                                    r[alt_chain_id_col], r[auth_seq_id_col] = _rev_seq[0], str(_rev_seq[1])
                                                    _k = (_rev_seq[0], _rev_seq[1], r[comp_id_col])
                                                    if _k in auth_to_star_seq:
                                                        _entity_assembly_id, _seq_id, _entity_id, _ = auth_to_star_seq[_k]
                                                        r[chain_id_col] = str(_entity_assembly_id)
                                                        if entity_id_col != -1:
                                                            r[entity_id_col] = str(_entity_id)
                                                        if sync_seq:
                                                            if seq_id_col != -1:
                                                                r[seq_id_col] = str(_seq_id)
                                                            if alt_seq_id_col != -1:
                                                                r[alt_seq_id_col] = str(_seq_id)

                        def refresh_entity_assembly(_loop, _alt_chain_id_list):
                            sync_seq = True
                            if 'Original_PDB_strand_ID' in _loop.tags:
                                _pre_tag = ['Auth_asym_ID', 'Original_PDB_strand_ID']
                                _pre_chain_data = _loop.get_tag(_pre_tag)
                                for _row in _pre_chain_data:
                                    if _row[0] != _row[1]:
                                        sync_seq = False
                                        break
                            else:
                                sync_seq = False
                            resolve_entity_assembly(_loop, _alt_chain_id_list, sync_seq)  # pylint: disable=cell-var-from-loop

                        def sync_entity_assembly_with_entity(_loop, _chain_id_set, _alt_chain_id_set):
                            if len(_chain_id_set) == 0 and 'Entity_ID' in _loop.tags:
                                _pre_tag = ['Entity_ID']
                                _pre_chain_data = _loop.get_tag(_pre_tag)
                                entity_id_set = set()
                                for _row in _pre_chain_data:
                                    if _row not in emptyValue:
                                        entity_id_set.add(_row)
                                if len(entity_id_set) > 0 and len(entity_id_set) == len(_alt_chain_id_set):
                                    chain_id_col = _loop.tags.index('Entity_assembly_ID')
                                    entity_id_col = _loop.tags.index('Entity_ID')
                                    for r in _loop.data:
                                        r[chain_id_col] = r[entity_id_col]
                                    return True
                            return False

                        valid = True
                        if self.__merge_rescue_mode and 'Auth_seq_ID' in loop.tags and 'Auth_comp_ID' in loop.tags and 'Details' in loop.tags:
                            pre_tags = ['Comp_index_ID', 'Comp_ID', 'Auth_seq_ID', 'Auth_comp_ID', 'Details']
                            pre_seq_data = loop.get_tag(pre_tags)
                            count = 0
                            for row in pre_seq_data:
                                if row[0] in emptyValue or row[2] in emptyValue or row[4] == 'UNMAPPED':
                                    count = 0
                                    break
                                _seq_id_ = int(row[0]) if isinstance(row[0], str) else row[0]
                                try:
                                    _auth_seq_id_ = int(row[2]) if isinstance(row[2], str) else row[2]
                                except ValueError:
                                    continue
                                if _seq_id_ == _auth_seq_id_ and row[1] not in emptyValue and row[3] not in emptyValue and row[1] != row[3]\
                                   and row[1] in monDict3 and row[3] not in monDict3:
                                    count += 1
                            if count > len(pre_seq_data) // 2:  # DAOTHER-9927: reset auth_seq_id and auth_comp_id derived from BMRB archive
                                auth_seq_id_col = loop.tags.index('Auth_seq_ID')
                                auth_comp_id_col = loop.tags.index('Auth_comp_ID')
                                for idx in range(len(loop)):
                                    loop.data[idx][auth_seq_id_col] = None
                                    loop.data[idx][auth_comp_id_col] = None
                                valid = False

                            elif 'Entry_ID' in loop.tags:
                                pre_tags = ['Comp_index_ID', 'Auth_asym_ID', 'Auth_seq_ID', 'Auth_comp_ID', 'Details', 'Entry_ID']
                                pre_seq_data = loop.get_tag(pre_tags)
                                count = 0
                                for row in pre_seq_data:
                                    if row[0] in emptyValue or row[2] in emptyValue or row[4] == 'UNMAPPED' or row[5] in emptyValue or not row[5].isdigit():
                                        count = 0
                                        break
                                    _seq_id_ = int(row[0]) if isinstance(row[0], str) else row[0]
                                    try:
                                        _auth_seq_id_ = int(row[2]) if isinstance(row[2], str) else row[2]
                                    except ValueError:
                                        continue
                                    if _seq_id_ != _auth_seq_id_ and row[3] in monDict3 and row[1] not in emptyValue and row[4] in emptyValue:
                                        _k = (row[1], _auth_seq_id_, row[3])
                                        if _k in coord_assembly_checker['auth_to_star_seq']:
                                            count += 1
                                if 0 < count < len(loop):  # DAOTHER-9927: reset auth_seq_id derived from BMRB archive
                                    auth_seq_id_col = loop.tags.index('Auth_seq_ID')
                                    pdb_seq_id_col = loop.tags.index('PDB_residue_no') if 'PDB_residue_no' in loop.tags else -1
                                    orig_seq_id_col = loop.tags.index('Original_PDB_residue_no') if 'Original_PDB_residue_no' in loop.tags else -1
                                    for idx, row in enumerate(loop):
                                        loop.data[idx][auth_seq_id_col] = None
                                        if pdb_seq_id_col != -1:
                                            loop.data[idx][pdb_seq_id_col] = None
                                        if orig_seq_id_col != -1:
                                            loop.data[idx][orig_seq_id_col] = None
                                    valid = False

                        if valid and len(alt_chain_id_set) > 0 and (len(chain_id_set) > LEN_LARGE_ASYM_ID or len(chain_id_set) == 0):
                            if 'UNMAPPED' in alt_chain_id_set:  # 2c34, 2ksi
                                resolve_entity_assembly(loop, list(alt_chain_id_set), True)

                            else:  # 2lpk, 2lnh
                                if not sync_entity_assembly_with_entity(loop, chain_id_set, alt_chain_id_set):  # 2rqz
                                    chain_id_col = loop.tags.index('Entity_assembly_ID')
                                    alt_chain_id_col = loop.tags.index('Auth_asym_ID')
                                    for r in loop.data:
                                        r[chain_id_col] = r[alt_chain_id_col]
                                    # if len(alt_chain_id_set) == 1:
                                    if len(chain_id_set) <= len(alt_chain_id_set):
                                        refresh_entity_assembly(loop, list(alt_chain_id_set))

                        elif not sync_entity_assembly_with_entity(loop, chain_id_set, alt_chain_id_set):  # 2kxc
                            if (len(alt_chain_id_set) == 1 and len(chain_id_set) == 1)\
                               or (len(alt_chain_id_set) > len(chain_id_set)):  # 5xv8, 2n7k
                                refresh_entity_assembly(loop, list(alt_chain_id_set))

                if 'Auth_asym_ID' in loop.tags and 'Auth_seq_ID' in loop.tags and coord_assembly_checker is not None:
                    pre_comp_data = loop.get_tag(['Auth_asym_ID', 'Auth_seq_ID', 'Comp_ID'])
                    comp_id_col = loop.tags.index('Comp_ID')
                    for idx, row in enumerate(pre_comp_data):
                        if row[2] in emptyValue:
                            continue
                        if len(row[2]) not in (1, 2, 3, 5):
                            ref_comp_id = None
                            cif_ps = coord_assembly_checker['polymer_sequence']
                            cif_np = coord_assembly_checker['non_polymer']
                            ps = next((ps for ps in cif_ps if ps['auth_chain_id'] == row[0]), None)
                            if ps is not None:
                                try:
                                    if int(row[1]) in ps['auth_seq_id']:
                                        ref_comp_id = ps['comp_id'][ps['auth_seq_id'].index(int(row[1]))]
                                except ValueError:
                                    pass
                            if cif_np is not None:
                                np = next((np for np in cif_np if np['auth_chain_id'] == row[0]), None)
                                if np is not None:
                                    try:
                                        if int(row[1]) in np['auth_seq_id']:
                                            ref_comp_id = np['comp_id'][np['auth_seq_id'].index(int(row[1]))]
                                    except ValueError:
                                        pass
                            loop.data[idx][comp_id_col] = translateToStdResName(row[2].upper(), refCompId=ref_comp_id, ccU=self.__ccU)

                    if 'Auth_comp_ID' in loop.tags:
                        pre_comp_data = loop.get_tag(['Auth_asym_ID', 'Auth_seq_ID', 'Auth_comp_ID'])
                        alt_chain_id_col = loop.tags.index('Auth_asym_ID')
                        auth_seq_id_col = loop.tags.index('Auth_seq_ID')
                        auth_comp_id_col = loop.tags.index('Auth_comp_ID')

                        def fill_ligand(_loop, idx, np):
                            try:
                                seq_key = (np['auth_chain_id'], np['auth_seq_id'][0], np['comp_id'][0])
                                if seq_key in coord_assembly_checker['auth_to_star_seq']:
                                    chain_id_col = _loop.tags.index('Entity_assembly_ID') if 'Entity_assembly_ID' in _loop.tags else -1
                                    seq_id_col = _loop.tags.index('Comp_index_ID') if 'Comp_index_ID' in _loop.tags else -1
                                    alt_seq_id_col = _loop.tags.index('Seq_ID') if 'Seq_ID' in _loop.tags else -1
                                    entity_id_col = _loop.tags.index('Entity_ID') if 'Entity_ID' in _loop.tags else -1

                                    _entity_assembly_id, _seq_id, _entity_id, _ = coord_assembly_checker['auth_to_star_seq'][seq_key]
                                    _row = _loop.data[idx]
                                    if chain_id_col != -1:
                                        _row[chain_id_col] = str(_entity_assembly_id)
                                    if seq_id_col != -1:
                                        _row[seq_id_col] = str(_seq_id)
                                    if alt_seq_id_col != -1:
                                        _row[alt_seq_id_col] = str(_seq_id)
                                    if entity_id_col != -1:
                                        _row[entity_id_col] = str(_entity_id)
                                    _row[alt_chain_id_col], _row[auth_seq_id_col], _row[comp_id_col], _row[auth_comp_id_col] =\
                                        seq_key[0], str(seq_key[1]), seq_key[2], seq_key[2]  # pylint: disable=cell-var-from-loop
                            except (KeyError, TypeError):
                                pass

                        for idx, row in enumerate(pre_comp_data):
                            if row[2] in emptyValue:
                                continue
                            auth_asym_id = row[0]
                            try:
                                auth_seq_id = int(row[1])
                            except (TypeError, ValueError):
                                continue
                            auth_comp_id = row[2].upper()
                            if len(auth_comp_id) not in (1, 2, 3, 5):
                                ref_comp_id = None
                                cif_ps = coord_assembly_checker['polymer_sequence']
                                cif_np = coord_assembly_checker['non_polymer']
                                ps = next((ps for ps in cif_ps if ps['auth_chain_id'] == auth_asym_id), None)
                                if ps is not None:
                                    if auth_asym_id in ps['auth_seq_id']:
                                        ref_comp_id = ps['comp_id'][ps['auth_seq_id'].index(auth_seq_id)]
                                if cif_np is not None:
                                    np = next((np for np in cif_np if np['auth_chain_id'] == auth_asym_id), None)
                                    if np is not None:
                                        if auth_seq_id in np['auth_seq_id']:
                                            ref_comp_id = np['comp_id'][np['auth_seq_id'].index(auth_seq_id)]
                                loop.data[idx][auth_comp_id_col] = translateToStdResName(auth_comp_id, refCompId=ref_comp_id, ccU=self.__ccU)
                            else:
                                cif_ps = coord_assembly_checker['polymer_sequence']
                                cif_np = coord_assembly_checker['non_polymer']
                                ps = next((ps for ps in cif_ps if ps['auth_chain_id'] == auth_asym_id), None)
                                if ps is not None and auth_comp_id in ps['comp_id']:
                                    pass
                                elif cif_np is not None:
                                    ligands = 0
                                    np = next((np for np in cif_np if np['auth_chain_id'] == auth_asym_id and auth_seq_id in np['auth_seq_id']), None)
                                    if np is not None:
                                        if auth_comp_id in np['comp_id']:
                                            ligands = 1
                                            fill_ligand(loop, idx, np)
                                    if ligands == 0:
                                        for np in cif_np:
                                            ligands += np['comp_id'].count(auth_comp_id)
                                        if ligands == 1:
                                            for np in cif_np:
                                                if auth_comp_id in np['comp_id']:
                                                    fill_ligand(loop, idx, np)
                                                    break
                                        elif ligands > 1:
                                            for np in cif_np:
                                                if auth_comp_id in np['comp_id'] and auth_seq_id in np['auth_seq_id']:
                                                    fill_ligand(loop, idx, np)
                                                    break
                                    if ligands == 0:
                                        for np in cif_np:
                                            if 'alt_comp_id' in np:
                                                ligands += np['alt_comp_id'].count(auth_comp_id)
                                        if ligands == 1:
                                            for np in cif_np:
                                                if 'alt_comp_id' in np and auth_comp_id in np['alt_comp_id']:
                                                    fill_ligand(loop, idx, np)
                                                    break
                                        elif ligands > 1:
                                            for np in cif_np:
                                                if 'alt_comp_id' in np and auth_comp_id in np['alt_comp_id'] and auth_seq_id in np['auth_seq_id']:
                                                    fill_ligand(loop, idx, np)
                                                    break

                seq_data = loop.get_tag(tags)
                if isinstance(seq_data[0][2], int):
                    for row in seq_data:
                        row[2] = str(row[2])
                has_valid_chain_id = True
                for row in seq_data:
                    if row[2] in emptyValue:
                        has_valid_chain_id = False
                        break
                if has_valid_chain_id:
                    wrong_chain_id_anno = True
                    for row in seq_data:
                        if row[0] != row[2]:
                            wrong_chain_id_anno = False
                            break
                    if not wrong_chain_id_anno:
                        wrong_chain_id_anno = True
                        offset = None
                        _seq_id_set = set()
                        for row in seq_data:
                            if not row[2].isdigit():
                                wrong_chain_id_anno = False
                                break
                            try:
                                _seq_id = int(row[0])
                                _chain_id = int(row[2])
                                _seq_id_set.add(_seq_id)
                                if offset is None:
                                    offset = _seq_id - _chain_id
                                    continue
                                if _seq_id - _chain_id != offset:
                                    wrong_chain_id_anno = False
                                    break
                            except ValueError:
                                continue
                        if len(_seq_id_set) < 2:
                            wrong_chain_id_anno = False
                    if wrong_chain_id_anno:
                        has_valid_chain_id = False
                if not has_valid_chain_id:
                    seq_data = loop.get_tag(tags__)
                    for row in seq_data:
                        if row[1] in lig_to_chain_id:
                            row[2] = lig_to_chain_id[row[1]]
                        else:
                            row[2] = def_chain_id if row[2] in emptyValue else str(row[2] if self.__remediation_mode else letterToDigit(row[2], 1))

            elif lp_category == '_Atom_chem_shift' and self.__remediation_mode\
                    and set(tags) & set(loop.tags) == set(tags)\
                    and coord_assembly_checker is not None and len(coord_assembly_checker['polymer_sequence']) > 1:
                factor = 2
                if seq_id != alt_seq_id and alt_seq_id in loop.tags:
                    pre_tags = [seq_id, alt_seq_id]
                    pre_seq_data = loop.get_tag(pre_tags)
                    seq_id_set = set()
                    alt_seq_id_set = set()
                    for row in pre_seq_data:
                        seq_id_set.add(row[0])
                        alt_seq_id_set.add(row[1])
                    if 0 < len(seq_id_set) < len(alt_seq_id_set) // factor:  # 2kyb
                        seq_id_col = loop.tags.index('Comp_index_ID')
                        alt_seq_id_col = loop.tags.index('Seq_ID')
                        for r in loop.data:
                            r[seq_id_col] = r[alt_seq_id_col]
                    elif 'Auth_seq_ID' in loop.tags:
                        pre_tag = ['Auth_seq_ID']
                        pre_seq_data = loop.get_tag(pre_tag)
                        alt_seq_id_set = set()
                        for row in pre_seq_data:
                            alt_seq_id_set.add(row)
                        if 0 < len(seq_id_set) < len(alt_seq_id_set) // factor:  # 6wux, 2lnh
                            seq_id_col = loop.tags.index('Comp_index_ID')
                            alt_seq_id_col = loop.tags.index('Auth_seq_ID')
                            for r in loop.data:
                                r[seq_id_col] = r[alt_seq_id_col]

                valid = True
                if self.__merge_rescue_mode and 'Auth_seq_ID' in loop.tags and 'Auth_comp_ID' in loop.tags and 'Details' in loop.tags:
                    pre_tags = ['Comp_index_ID', 'Comp_ID', 'Auth_seq_ID', 'Auth_comp_ID', 'Details']
                    pre_seq_data = loop.get_tag(pre_tags)
                    count = 0
                    for row in pre_seq_data:
                        if row[0] in emptyValue or row[2] in emptyValue or row[4] == 'UNMAPPED':
                            count = 0
                            break
                        _seq_id_ = int(row[0]) if isinstance(row[0], str) else row[0]
                        try:
                            _auth_seq_id_ = int(row[2]) if isinstance(row[2], str) else row[2]
                        except ValueError:
                            continue
                        if _seq_id_ == _auth_seq_id_ and row[1] not in emptyValue and row[3] not in emptyValue and row[1] != row[3]\
                           and row[1] in monDict3 and row[3] not in monDict3:
                            count += 1
                    if count > len(pre_seq_data) // 2:  # DAOTHER-9927: reset auth_seq_id and auth_comp_id derived from BMRB archive
                        auth_seq_id_col = loop.tags.index('Auth_seq_ID')
                        auth_comp_id_col = loop.tags.index('Auth_comp_ID')
                        for idx in range(len(loop)):
                            loop.data[idx][auth_seq_id_col] = None
                            loop.data[idx][auth_comp_id_col] = None
                        valid = False

                if valid:
                    pre_tag = ['Entity_assembly_ID']
                    pre_chain_data = loop.get_tag(pre_tag)
                    chain_id_set = set()
                    for row in pre_chain_data:
                        if row not in emptyValue:
                            chain_id_set.add(row)

                    if len(chain_id_set) == 1:
                        pre_tags = ['Comp_index_ID', 'Comp_ID']
                        pre_seq_data = loop.get_tag(pre_tags)
                        cif_ps = coord_assembly_checker['polymer_sequence']
                        alt_cif_ps = coord_assembly_checker['alt_polymer_sequence']
                        if sum(len(ps['seq_id']) for ps in cif_ps) < sum(len(ps['seq_id']) for ps in alt_cif_ps):
                            cif_ps = alt_cif_ps
                        cif_np = coord_assembly_checker['non_polymer']
                        nmr_chain_id = list(chain_id_set)[0]
                        nmr_ps = [{'chain_id': nmr_chain_id, 'seq_id': [], 'comp_id': []}]
                        seq = set()
                        valid = True
                        for row in pre_seq_data:
                            if row[0] in emptyValue or row[1] in emptyValue:
                                valid = False
                                break
                            try:
                                seq.add((nmr_chain_id, int(row[0]), row[1]))
                            except ValueError:
                                valid = False
                                break

                        if valid:
                            sorted_seq = sorted(seq, key=itemgetter(0, 1))
                            for row in sorted_seq:
                                _nmr_ps = nmr_ps[0]
                                _nmr_ps['seq_id'].append(row[1])
                                _nmr_ps['comp_id'].append(row[2])
                            # 2c34
                            seq_align, _ = alignPolymerSequence(self.__pA, cif_ps, nmr_ps)
                            if len(seq_align) > 0:
                                chain_assign, _ = assignPolymerSequence(self.__pA, self.__ccU, 'nmr-star', cif_ps, nmr_ps, seq_align)
                            else:
                                valid = False
                                for c in range(1, 5):
                                    seq_align, _ = alignPolymerSequenceWithConflicts(self.__pA, cif_ps, nmr_ps, c)
                                    if len(seq_align) > 0:
                                        chain_assign, _ = assignPolymerSequence(self.__pA, self.__ccU, 'nmr-star', cif_ps, nmr_ps, seq_align)
                                        valid = True
                                        break

                            if valid:

                                rev_seq = {}
                                ref_chain_id = test_chain_id = None
                                for ca in chain_assign:
                                    if ca['matched'] == 0:  # or (ca['conflict'] > 0 and ca['matched'] != ca['length']):
                                        continue
                                    ref_chain_id = ca['ref_chain_id']
                                    test_chain_id = ca['test_chain_id']
                                    sa = next(sa for sa in seq_align
                                              if sa['ref_chain_id'] == ref_chain_id
                                              and sa['test_chain_id'] == test_chain_id)
                                    ps = next(ps for ps in cif_ps if ps['auth_chain_id'] == ref_chain_id)
                                    for ref_seq_id, mid_code, test_seq_id in zip(sa['ref_seq_id'], sa['mid_code'], sa['test_seq_id']):
                                        if mid_code == '|' and test_seq_id is not None:
                                            rev_seq_key = (test_chain_id, test_seq_id)
                                            if rev_seq_key in rev_seq:
                                                continue
                                            try:
                                                rev_seq[rev_seq_key] =\
                                                    (ps['auth_chain_id'],
                                                     next(auth_seq_id for auth_seq_id, _seq_id
                                                          in zip(ps['auth_seq_id'], ps['seq_id'])
                                                          if _seq_id == ref_seq_id and isinstance(auth_seq_id, int)))
                                            except StopIteration:
                                                rev_seq[rev_seq_key] = (ps['auth_chain_id'], ref_seq_id)

                                    if test_chain_id is not None:
                                        chain_id_col = loop.tags.index('Entity_assembly_ID')
                                        comp_id_col = loop.tags.index('Comp_ID')
                                        alt_chain_id_col = loop.tags.index('Auth_asym_ID') if 'Auth_asym_ID' in loop.tags else -1
                                        auth_seq_id_col = loop.tags.index('Auth_seq_ID') if 'Auth_seq_ID' in loop.tags else -1
                                        entity_id_col = loop.tags.index('Entity_ID') if 'Entity_ID' in loop.tags else -1
                                        seq_id_col = loop.tags.index('Comp_index_ID') if 'Comp_index_ID' in loop.tags else -1
                                        alt_seq_id_col = loop.tags.index('Seq_ID') if 'Seq_ID' in loop.tags else -1
                                        auth_to_star_seq = coord_assembly_checker['auth_to_star_seq']
                                        _entity_assembly_id = _entity_id = None
                                        for r in loop.data:
                                            k = (test_chain_id, int(r[seq_id_col]))
                                            if k in rev_seq:
                                                _rev_seq = rev_seq[k]
                                                if alt_chain_id_col != -1:
                                                    r[alt_chain_id_col] = _rev_seq[0]
                                                if auth_seq_id_col != -1:
                                                    r[auth_seq_id_col] = str(_rev_seq[1])
                                                _k = (_rev_seq[0], _rev_seq[1], r[comp_id_col])
                                                if _k in auth_to_star_seq:
                                                    _entity_assembly_id, _seq_id, _entity_id, _ = auth_to_star_seq[_k]
                                                    r[chain_id_col] = str(_entity_assembly_id)
                                                    if seq_id_col != -1:
                                                        r[seq_id_col] = str(_seq_id)
                                                    if alt_seq_id_col != -1:
                                                        r[alt_seq_id_col] = str(_seq_id)
                                                    if entity_id_col != -1:
                                                        r[entity_id_col] = str(_entity_id)
                                                else:
                                                    _comp_id = next((_comp_id for _seq_id, _auth_seq_id, _comp_id, _auth_comp_id, _alt_comp_id
                                                                     in zip(ps['seq_id'], ps['auth_seq_id'], ps['comp_id'], ps['auth_comp_id'],
                                                                            ps['alt_comp_id'] if 'alt_comp_id' in ps else ps['auth_comp_id'])
                                                                     if _k[1] in (_seq_id, _auth_seq_id) and _k[2] in (_comp_id, _auth_comp_id, _alt_comp_id)), None)
                                                    if _comp_id is not None:
                                                        _k = (_rev_seq[0], _rev_seq[1], _comp_id)
                                                        if _k in auth_to_star_seq:
                                                            _entity_assembly_id, _seq_id, _entity_id, _ = auth_to_star_seq[_k]
                                                            r[chain_id_col] = str(_entity_assembly_id)
                                                            if seq_id_col != -1:
                                                                r[seq_id_col] = str(_seq_id)
                                                            if alt_seq_id_col != -1:
                                                                r[alt_seq_id_col] = str(_seq_id)
                                                            if entity_id_col != -1:
                                                                r[entity_id_col] = str(_entity_id)
                                                            if _comp_id not in monDict3:
                                                                r[comp_id_col] = _comp_id
                                            else:
                                                for c in range(1, 5):
                                                    k = (test_chain_id, int(r[seq_id_col]) + c)
                                                    if k in rev_seq:
                                                        r[chain_id_col] = str(_entity_assembly_id)
                                                        if entity_id_col != -1:
                                                            r[entity_id_col] = str(_entity_id)
                                                        break
                                                    k = (test_chain_id, int(r[seq_id_col]) - c)
                                                    if k in rev_seq:
                                                        r[chain_id_col] = str(_entity_assembly_id)
                                                        if entity_id_col != -1:
                                                            r[entity_id_col] = str(_entity_id)
                                                        break

                                    else:

                                        valid = False
                                        for c in range(1, 5):
                                            seq_align, _ = alignPolymerSequenceWithConflicts(self.__pA, cif_ps, nmr_ps, c)
                                            if len(seq_align) > 0:
                                                chain_assign, _ = assignPolymerSequence(self.__pA, self.__ccU, 'nmr-star', cif_ps, nmr_ps, seq_align)
                                                for ca in chain_assign:
                                                    if ca['matched'] > 0 and ca['conflict'] <= c and ca['sequence_coverage'] >= LOW_SEQ_COVERAGE:
                                                        valid = True
                                                        break
                                                break

                                        if valid:
                                            rev_seq = {}
                                            ref_chain_id = test_chain_id = None
                                            for ca in chain_assign:
                                                if ca['matched'] == 0 or ca['conflict'] > c or ca['sequence_coverage'] < LOW_SEQ_COVERAGE:
                                                    continue
                                                ref_chain_id = ca['ref_chain_id']
                                                test_chain_id = ca['test_chain_id']
                                                sa = next(sa for sa in seq_align
                                                          if sa['ref_chain_id'] == ref_chain_id
                                                          and sa['test_chain_id'] == test_chain_id)
                                                ps = next(ps for ps in cif_ps if ps['auth_chain_id'] == ref_chain_id)
                                                for ref_seq_id, mid_code, test_seq_id in zip(sa['ref_seq_id'], sa['mid_code'], sa['test_seq_id']):
                                                    if mid_code == '|' and test_seq_id is not None:
                                                        rev_seq_key = (test_chain_id, test_seq_id)
                                                        if rev_seq_key in rev_seq:
                                                            continue
                                                        try:
                                                            rev_seq[rev_seq_key] =\
                                                                (ps['auth_chain_id'],
                                                                 next(auth_seq_id for auth_seq_id, _seq_id
                                                                      in zip(ps['auth_seq_id'], ps['seq_id'])
                                                                      if _seq_id == ref_seq_id and isinstance(auth_seq_id, int)))
                                                        except StopIteration:
                                                            rev_seq[rev_seq_key] = (ps['auth_chain_id'], ref_seq_id)
                                                break
                                            if test_chain_id is not None:
                                                chain_id_col = loop.tags.index('Entity_assembly_ID')
                                                comp_id_col = loop.tags.index('Comp_ID')
                                                alt_chain_id_col = loop.tags.index('Auth_asym_ID') if 'Auth_asym_ID' in loop.tags else -1
                                                auth_seq_id_col = loop.tags.index('Auth_seq_ID') if 'Auth_seq_ID' in loop.tags else -1
                                                entity_id_col = loop.tags.index('Entity_ID') if 'Entity_ID' in loop.tags else -1
                                                seq_id_col = loop.tags.index('Comp_index_ID') if 'Comp_index_ID' in loop.tags else -1
                                                alt_seq_id_col = loop.tags.index('Seq_ID') if 'Seq_ID' in loop.tags else -1
                                                auth_to_star_seq = coord_assembly_checker['auth_to_star_seq']
                                                _offset = _entity_assembly_id = _entity_id = None
                                                for r in loop.data:
                                                    k = (test_chain_id, int(r[seq_id_col]))
                                                    if k in rev_seq:
                                                        _rev_seq = rev_seq[k]
                                                        if alt_chain_id_col != -1:
                                                            r[alt_chain_id_col] = _rev_seq[0]
                                                        if auth_seq_id_col != -1:
                                                            r[auth_seq_id_col] = str(_rev_seq[1])
                                                        _k = (_rev_seq[0], _rev_seq[1], r[comp_id_col])
                                                        if _k in auth_to_star_seq:
                                                            _entity_assembly_id, _seq_id, _entity_id, _ = auth_to_star_seq[_k]
                                                            _offset = _seq_id - int(r[seq_id_col])
                                                            break
                                                        _comp_id = next((_comp_id for _seq_id, _auth_seq_id, _comp_id, _auth_comp_id, _alt_comp_id
                                                                         in zip(ps['seq_id'], ps['auth_seq_id'], ps['comp_id'], ps['auth_comp_id'],
                                                                                ps['alt_comp_id'] if 'alt_comp_id' in ps else ps['auth_comp_id'])
                                                                         if _k[1] in (_seq_id, _auth_seq_id) and _k[2] in (_comp_id, _auth_comp_id, _alt_comp_id)), None)
                                                        if _comp_id is not None and _comp_id not in monDict3:
                                                            _k = (_rev_seq[0], _rev_seq[1], _comp_id)
                                                            if _k in auth_to_star_seq:
                                                                _entity_assembly_id, _seq_id, _entity_id, _ = auth_to_star_seq[_k]
                                                                _offset = _seq_id - int(r[seq_id_col])
                                                                break

                                                for r in loop.data:
                                                    k = (test_chain_id, int(r[seq_id_col]))
                                                    if k in rev_seq:
                                                        _rev_seq = rev_seq[k]
                                                        if alt_chain_id_col != -1:
                                                            r[alt_chain_id_col] = _rev_seq[0]
                                                        if auth_seq_id_col != -1:
                                                            r[auth_seq_id_col] = str(_rev_seq[1])
                                                        _k = (_rev_seq[0], _rev_seq[1], r[comp_id_col])
                                                        if _k in auth_to_star_seq:
                                                            _entity_assembly_id, _seq_id, _entity_id, _ = auth_to_star_seq[_k]
                                                            r[chain_id_col] = str(_entity_assembly_id)
                                                            if seq_id_col != -1:
                                                                r[seq_id_col] = str(_seq_id)
                                                            if alt_seq_id_col != -1:
                                                                r[alt_seq_id_col] = str(_seq_id)
                                                            if entity_id_col != -1:
                                                                r[entity_id_col] = str(_entity_id)
                                                        else:
                                                            _comp_id = next((_comp_id for _seq_id, _auth_seq_id, _comp_id, _auth_comp_id, _alt_comp_id
                                                                             in zip(ps['seq_id'], ps['auth_seq_id'], ps['comp_id'], ps['auth_comp_id'],
                                                                                    ps['alt_comp_id'] if 'alt_comp_id' in ps else ps['auth_comp_id'])
                                                                             if _k[1] in (_seq_id, _auth_seq_id) and _k[2] in (_comp_id, _auth_comp_id, _alt_comp_id)), None)
                                                            if _comp_id is not None:
                                                                _k = (_rev_seq[0], _rev_seq[1], _comp_id)
                                                                if _k in auth_to_star_seq:
                                                                    _entity_assembly_id, _seq_id, _entity_id, _ = auth_to_star_seq[_k]
                                                                    r[chain_id_col] = str(_entity_assembly_id)
                                                                    if seq_id_col != -1:
                                                                        r[seq_id_col] = str(_seq_id)
                                                                    if alt_seq_id_col != -1:
                                                                        r[alt_seq_id_col] = str(_seq_id)
                                                                    if entity_id_col != -1:
                                                                        r[entity_id_col] = str(_entity_id)
                                                                    if _comp_id not in monDict3:
                                                                        r[comp_id_col] = _comp_id

                                                    else:
                                                        r[chain_id_col] = str(_entity_assembly_id)
                                                        _seq_id = int(r[seq_id_col]) + _offset
                                                        if seq_id_col != -1:
                                                            r[seq_id_col] = str(_seq_id)
                                                        if alt_seq_id_col != -1:
                                                            r[alt_seq_id_col] = str(_seq_id)
                                                        if entity_id_col != -1:
                                                            r[entity_id_col] = str(_entity_id)

                                    if 'identical_chain_id' in ps:
                                        break

                seq_data = loop.get_tag(tags)

                has_valid_chain_id = True
                for row in seq_data:
                    if row[2] in emptyValue:
                        has_valid_chain_id = False
                        break
                if has_valid_chain_id:
                    wrong_chain_id_anno = True
                    for row in seq_data:
                        if row[0] != row[2]:
                            wrong_chain_id_anno = False
                            break
                    if not wrong_chain_id_anno:
                        wrong_chain_id_anno = True
                        offset = None
                        _seq_id_set = set()
                        for row in seq_data:
                            if not row[2].isdigit():
                                wrong_chain_id_anno = False
                                break
                            try:
                                _seq_id = int(row[0])
                                _chain_id = int(row[2])
                                _seq_id_set.add(_seq_id)
                                if offset is None:
                                    offset = _seq_id - _chain_id
                                    continue
                                if _seq_id - _chain_id != offset:
                                    wrong_chain_id_anno = False
                                    break
                            except ValueError:
                                continue
                        if len(_seq_id_set) < 2:
                            wrong_chain_id_anno = False
                    if wrong_chain_id_anno:
                        has_valid_chain_id = False
                if not has_valid_chain_id:
                    seq_data = loop.get_tag(tags__)
                    for row in seq_data:
                        if row[1] in lig_to_chain_id:
                            row[2] = lig_to_chain_id[row[1]]
                        else:
                            row[2] = def_chain_id if row[2] in emptyValue else str(row[2] if self.__remediation_mode else letterToDigit(row[2], 1))

            elif set(tags) & set(loop.tags) == set(tags):
                seq_data = loop.get_tag(tags)
                for row in seq_data:
                    if row[2] in emptyValue:
                        row[2] = def_chain_id if row[1] not in lig_to_chain_id else lig_to_chain_id[row[1]]
            elif set(tags__) & set(loop.tags) == set(tags__):  # DAOTHER-7421
                seq_data = loop.get_tag(tags__)
                for row in seq_data:
                    if row[1] in lig_to_chain_id:
                        row[2] = lig_to_chain_id[row[1]]
                    else:
                        row[2] = def_chain_id if row[2] in emptyValue else str(row[2] if self.__remediation_mode else letterToDigit(row[2], 1))
            elif set(tags_) & set(loop.tags) == set(tags_):  # No Entity_assembly_ID tag case
                seq_data = loop.get_tag(tags_)
                for row in seq_data:
                    row.append(def_chain_id if row[1] not in lig_to_chain_id else lig_to_chain_id[row[1]])
                comp_id_col = loop.tags.index('Comp_ID')
                for row in loop:
                    row.append(def_chain_id if row[comp_id_col] not in lig_to_chain_id else lig_to_chain_id[row[comp_id_col]])
                loop.add_tag(chain_id)
            else:
                _tags_exist = _normal_chain_tag = False
                for j in range(1, MAX_DIM_NUM_OF_SPECTRA):
                    _tags = [seq_id + '_' + str(j), comp_id + '_' + str(j), chain_id + '_' + str(j)]
                    _tags_ = [seq_id + '_' + str(j), comp_id + '_' + str(j)]
                    _tags__ = [seq_id + '_' + str(j), comp_id + '_' + str(j), alt_chain_id + '_' + str(j)]  # DAOTHER-7421

                    _alt_tags = [alt_seq_id + '_' + str(j), comp_id + '_' + str(j), chain_id + '_' + str(j)]
                    _alt_tags_ = [alt_seq_id + '_' + str(j), comp_id + '_' + str(j)]
                    _alt_tags__ = [alt_seq_id + '_' + str(j), comp_id + '_' + str(j), alt_chain_id + '_' + str(j)]  # DAOTHER-7421

                    if set(_tags) & set(loop.tags) == set(_tags):
                        _tags_exist = True
                        seq_data_ = loop.get_tag(_tags)
                        for row_ in seq_data_:
                            if alt_seq_id_offset != 0:
                                row_[0] += alt_seq_id_offset
                            if row_[2] in emptyValue:
                                row_[2] = def_chain_id if row_[1] not in lig_to_chain_id else lig_to_chain_id[row_[1]]
                        seq_data += seq_data_
                        _normal_chain_tag = True
                    elif set(_tags__) & set(loop.tags) == set(_tags__):  # DAOTHER-7421
                        _tags_exist = True
                        seq_data_ = loop.get_tag(_tags__)
                        for row_ in seq_data_:
                            if row_[1] in lig_to_chain_id:
                                row_[2] = lig_to_chain_id[row_[1]]
                            else:
                                row_[2] = def_chain_id if row_[2] in emptyValue else str(row_[2] if self.__remediation_mode else letterToDigit(row_[2], 1))
                        seq_data += seq_data_
                        if _normal_chain_tag:
                            raise LookupError(f"Missing mandatory {_tags[2]!r} loop tag.")
                    elif set(_tags_) & set(loop.tags) == set(_tags_):
                        _tags_exist = True
                        seq_data_ = loop.get_tag(_tags_)
                        for row_ in seq_data_:
                            row_.append(def_chain_id if row_[1] not in lig_to_chain_id else lig_to_chain_id[row_[1]])
                        seq_data += seq_data_

                    elif set(_alt_tags) & set(loop.tags) == set(_alt_tags):
                        _tags_exist = True
                        seq_data_ = loop.get_tag(_alt_tags)
                        for row_ in seq_data_:
                            if alt_seq_id_offset != 0:
                                row_[0] += alt_seq_id_offset
                            if row_[2] in emptyValue:
                                row_[2] = def_chain_id if row_[1] not in lig_to_chain_id else lig_to_chain_id[row_[1]]
                        seq_data += seq_data_
                        _normal_chain_tag = True
                    elif set(_alt_tags__) & set(loop.tags) == set(_alt_tags__):  # DAOTHER-7421
                        _tags_exist = True
                        seq_data_ = loop.get_tag(_alt_tags__)
                        for row_ in seq_data_:
                            if row_[1] in lig_to_chain_id:
                                row_[2] = lig_to_chain_id[row_[1]]
                            else:
                                row_[2] = def_chain_id if row_[2] in emptyValue else str(row_[2] if self.__remediation_mode else letterToDigit(row_[2], 1))
                        seq_data += seq_data_
                        if _normal_chain_tag:
                            raise LookupError(f"Missing mandatory {_alt_tags[2]!r} loop tag.")
                    elif set(_alt_tags_) & set(loop.tags) == set(_alt_tags_):
                        _tags_exist = True
                        seq_data_ = loop.get_tag(_alt_tags_)
                        for row_ in seq_data_:
                            row_.append(def_chain_id if row_[1] not in lig_to_chain_id else lig_to_chain_id[row_[1]])
                        seq_data += seq_data_

                if not _tags_exist:
                    if seq_id == 'Comp_index_ID' and 'Auth_asym_ID' in loop.tags and 'Auth_seq_ID' in loop.tags and 'Auth_comp_ID' in loop.tags:
                        return self.get_star_seq(star_data, lp_category, 'Auth_seq_ID', 'Auth_comp_ID', 'Auth_asym_ID',
                                                 alt_seq_id, alt_seq_id_offset, alt_chain_id, allow_empty, allow_gap, coord_assembly_checker)

                    # missing_tags = list(set(tags) - set(loop.tags))
                    # raise LookupError(f"Missing mandatory {missing_tags} loop tag(s).")

            if allow_empty:
                # seq_data = list(filter(is_data, seq_data))
                seq_data = list(filter(is_good_data, seq_data))  # DAOTHER-7389, issue #3
            else:
                for idx, row in enumerate(seq_data):
                    if is_empty(row) and idx < len_data:
                        if skip_empty_value_error(loop, idx):
                            continue
                        r = {}
                        for j, t in enumerate(loop.tags):
                            r[t] = loop.data[idx][j]
                        f.append("[Invalid data] Sequence must not be empty. "
                                 f"#_of_row {idx + 1}, data_of_row {r}.")

            if len(seq_data) == 0:
                continue

            for idx, row in enumerate(seq_data):
                try:
                    int(row[0])
                except (ValueError, TypeError):
                    if idx < len_data:
                        if skip_empty_value_error(loop, idx):
                            continue
                        r = {}
                        for j, t in enumerate(loop.tags):
                            r[t] = loop.data[idx][j]
                        f.append(f"[Invalid data] {seq_id} must be an integer. "
                                 f"#_of_row {idx + 1}, data_of_row {r}.")

            if len(f) > 0:
                if seq_id == 'Comp_index_ID' and 'Auth_asym_ID' in loop.tags and 'Auth_seq_ID' in loop.tags and 'Auth_comp_ID' in loop.tags:
                    return self.get_star_seq(star_data, lp_category, 'Auth_seq_ID', 'Auth_comp_ID', 'Auth_asym_ID',
                                             alt_seq_id, alt_seq_id_offset, alt_chain_id, allow_empty, allow_gap, coord_assembly_checker)

                raise UserWarning('\n'.join(sorted(list(set(f)), key=f.index)))

            try:

                chain_ids = sorted(set(row[2] for row in seq_data))
                offset_seq_ids = {row[2]: 0 for row in seq_data}
                for c in chain_ids:
                    min_seq_id = min(int(row[0]) for row in seq_data if row[2] == c)
                    if min_seq_id < 0:
                        offset_seq_ids[c] = min_seq_id * -1
                sorted_seq = sorted(set((row[2], int(row[0]) + offset_seq_ids[row[2]], row[1].upper()) for row in seq_data),
                                    key=itemgetter(0, 1))

                chk_dict = {(row[2], int(row[0])): row[1].upper() for row in seq_data}

                for row in seq_data:
                    chk_key = (row[2], int(row[0]))
                    if chk_dict[chk_key] != row[1].upper():

                        if seq_id != alt_seq_id and alt_seq_id in loop.tags:

                            seq_tags = [seq_id, alt_seq_id]
                            _seq_data = loop.get_tag(seq_tags)

                            offset = None

                            for _row in _seq_data:
                                try:
                                    offset = int(_row[0]) - int(_row[1])
                                    break
                                except ValueError:
                                    continue

                            if offset is not None:
                                return self.get_star_seq(star_data, lp_category, alt_seq_id, comp_id, chain_id,
                                                         alt_seq_id, offset, alt_chain_id, allow_empty, allow_gap, coord_assembly_checker)

                        raise KeyError(f"{lp_category[1:]} loop contains different {comp_id} ({row[1]} and {chk_dict[chk_key]}) "
                                       f"with the same {chain_id} {row[2]}, {seq_id} {row[0]}.")

                for c in chain_ids:
                    cmp_dict[c] = [x[2] for x in sorted_seq if x[0] == c]
                    seq_dict[c] = [x[1] - offset_seq_ids[c] for x in sorted_seq if x[0] == c]

                has_alt_comp_id = False
                if lp_category == '_Atom_chem_shift' and self.__remediation_mode\
                   and 'Entity_assembly_ID' in loop.tags and 'Comp_index_ID' in loop.tags\
                   and ('Auth_comp_ID' in loop.tags or 'Original_PDB_residue_name' in loop.tags):
                    comp_tags = ['Entity_assembly_ID', 'Comp_index_ID', 'Comp_ID']
                    if 'Auth_comp_ID' in loop.tags:
                        comp_tags.append('Auth_comp_ID')
                    if 'Original_PDB_residue_name' in loop.tags:
                        comp_tags.append('Original_PDB_residue_name')
                    comp_data = loop.get_tag(comp_tags)
                    if len(comp_data) > 0:
                        has_alt_comp_id = True

                asm = []  # assembly of a loop

                valid_gap_key, valid_spacer_key = [], []

                if coord_assembly_checker is not None:
                    cif_ps = coord_assembly_checker['polymer_sequence']
                    nmr_ps = []
                    for c in chain_ids:
                        nmr_ps.append({'chain_id': c, 'seq_id': seq_dict[c], 'comp_id': cmp_dict[c]})
                    seq_align, _ = alignPolymerSequence(self.__pA, cif_ps, nmr_ps)
                    chain_assign, _ = assignPolymerSequence(self.__pA, self.__ccU, 'nmr-star', cif_ps, nmr_ps, seq_align)

                    valid = False
                    for ca in chain_assign:
                        if ca['matched'] == 0 or ca['conflict'] > 0:
                            break
                        ref_chain_id = ca['ref_chain_id']
                        test_chain_id = ca['test_chain_id']
                        sa = next(sa for sa in seq_align
                                  if sa['ref_chain_id'] == ref_chain_id
                                  and sa['test_chain_id'] == test_chain_id)

                        _test_seq_id = None
                        for ref_seq_id, mid_code, test_seq_id in zip(sa['ref_seq_id'], sa['mid_code'], sa['test_seq_id']):
                            valid = _test_seq_id is not None and test_seq_id is not None and test_seq_id - _test_seq_id == 1
                            if mid_code == '|' and test_seq_id is not None:
                                if not valid and _test_seq_id is not None and test_seq_id - _test_seq_id != -1:
                                    for _test_seq_id_ in range(_test_seq_id + 1, test_seq_id):
                                        valid_gap_key.append((c, _test_seq_id_))
                                _test_seq_id = test_seq_id
                            else:
                                _test_seq_id = None

                        if 'ref_auth_seq_id' in sa\
                           and any(ref_auth_seq_id == test_seq_id
                                   for ref_auth_seq_id, mid_code, test_seq_id
                                   in zip(sa['ref_auth_seq_id'], sa['mid_code'], sa['test_seq_id'])
                                   if mid_code == '|' and test_seq_id is not None)\
                           and not all(ref_auth_seq_id == test_seq_id
                                       for ref_auth_seq_id, mid_code, test_seq_id
                                       in zip(sa['ref_auth_seq_id'], sa['mid_code'], sa['test_seq_id'])
                                       if mid_code == '|' and test_seq_id is not None)\
                           and 'unmapped_sequence' in ca:
                            unmapped_ref_seq_ids = [unmap['ref_seq_id'] for unmap in ca['unmapped_sequence']]
                            for ref_auth_seq_id, mid_code, test_seq_id in zip(sa['ref_auth_seq_id'], sa['mid_code'], sa['test_seq_id']):
                                if mid_code != '|' and test_seq_id is None:
                                    if ref_auth_seq_id in unmapped_ref_seq_ids:
                                        valid_spacer_key.append((c, ref_auth_seq_id))

                for c in chain_ids:
                    ent = {}  # entity

                    str_c = str(c)
                    ent['chain_id'] = str_c if str_c.isdigit() or self.__remediation_mode else str(letterToDigit(str_c, 1))

                    if allow_gap:
                        ent['seq_id'] = []
                        ent['comp_id'] = []
                        if has_alt_comp_id:
                            ent['alt_comp_id'] = []

                        _seq_id_ = None

                        for _seq_id, _comp_id in zip(seq_dict[c], cmp_dict[c]):

                            if _seq_id_ is not None and _seq_id_ + 1 != _seq_id:
                                if _seq_id_ + 20 > _seq_id:
                                    for s in range(_seq_id_ + 1, _seq_id):
                                        if (c, s) in valid_gap_key:
                                            continue
                                        ent['seq_id'].append(s)
                                        ent['comp_id'].append('.')
                                        if has_alt_comp_id:
                                            ent['alt_comp_id'].append('.')
                                if any((c, s) in valid_spacer_key for s in range(_seq_id_ + 1, _seq_id)):
                                    for s in range(_seq_id_ + 1, _seq_id):
                                        if s not in ent['seq_id']:
                                            ent['seq_id'].append(s)
                                            ent['comp_id'].append('.')
                                            if has_alt_comp_id:
                                                ent['alt_comp_id'].append('.')

                            ent['seq_id'].append(_seq_id)
                            ent['comp_id'].append(_comp_id)
                            if has_alt_comp_id:
                                try:
                                    r = next(r for r in comp_data if r[0] == c and r[1].isdigit() and int(r[1]) == _seq_id and r[2] == _comp_id)
                                    if len(r) == 5:
                                        if r[4] not in emptyValue:
                                            ent['alt_comp_id'].append(r[4])
                                        elif r[3] not in emptyValue:
                                            ent['alt_comp_id'].append(r[3])
                                        else:
                                            del ent['alt_comp_id']
                                            has_alt_comp_id = False
                                    else:
                                        if r[3] not in emptyValue:
                                            ent['alt_comp_id'].append(r[3])
                                        else:
                                            del ent['alt_comp_id']
                                            has_alt_comp_id = False
                                except StopIteration:
                                    del ent['alt_comp_id']
                                    has_alt_comp_id = False

                            _seq_id_ = _seq_id

                    else:
                        ent['seq_id'] = seq_dict[c]
                        ent['comp_id'] = cmp_dict[c]
                        if has_alt_comp_id:
                            for _seq_id, _comp_id in zip(seq_dict[c], cmp_dict[c]):
                                try:
                                    r = next(r for r in comp_data if r[0] == c and r[1].isdigit() and int(r[1]) == _seq_id and r[2] == _comp_id)
                                    if len(r) == 5:
                                        if r[4] not in emptyValue:
                                            ent['alt_comp_id'].append(r[4])
                                        elif r[3] not in emptyValue:
                                            ent['alt_comp_id'].append(r[3])
                                        else:
                                            del ent['alt_comp_id']
                                            has_alt_comp_id = False
                                    else:
                                        if r[3] not in emptyValue:
                                            ent['alt_comp_id'].append(r[3])
                                        else:
                                            del ent['alt_comp_id']
                                            has_alt_comp_id = False
                                except StopIteration:
                                    del ent['alt_comp_id']
                                    has_alt_comp_id = False

                    if len(chain_ids) > 1 and check_identity:
                        identity = []
                        for _c in chain_ids:
                            if _c == c:
                                continue
                            if seq_dict[_c] == seq_dict[c]:
                                if cmp_dict[_c] == cmp_dict[c]:
                                    _str_c = str(_c)
                                    identity.append(_str_c if _str_c.isdigit() or self.__remediation_mode else str(letterToDigit(_str_c, 1)))
                            else:
                                common_seq_id = set(seq_dict[_c]) & set(seq_dict[c])
                                if len(common_seq_id) == 0:
                                    continue
                                if any(s for s in common_seq_id
                                       if s in seq_dict[_c] and s in seq_dict[c]
                                       and cmp_dict[_c][seq_dict[_c].index(s)] != cmp_dict[c][seq_dict[c].index(s)]):
                                    continue
                                if not any(s for s in common_seq_id
                                           if s in seq_dict[_c] and s in seq_dict[c]
                                           and cmp_dict[_c][seq_dict[_c].index(s)] == cmp_dict[c][seq_dict[c].index(s)]):
                                    continue
                                _str_c = str(_c)
                                identity.append(_str_c if _str_c.isdigit() or self.__remediation_mode else str(letterToDigit(_str_c, 1)))
                        if len(identity) > 0:
                            ent['identical_chain_id'] = identity

                    asm.append(ent)

                data.append(asm)

            except (ValueError, TypeError):
                pass

        if len(data) == 0:
            data.append([])

        return data

    def get_star_auth_seq(self, star_data: Union[pynmrstar.Entry, pynmrstar.Saveframe, pynmrstar.Loop],  # pylint: disable=no-self-use
                          lp_category: str = 'Atom_chem_shift', aseq_id: str = 'Auth_seq_ID', acomp_id: str = 'Auth_comp_ID',
                          asym_id: str = 'Auth_asym_ID', seq_id: str = 'Comp_index_ID', chain_id: str = 'Entity_assembly_ID',
                          allow_empty: bool = True) -> List[List[dict]]:
        """ Extract author sequence from any given loops in an NMR-STAR file.
            @author: Masashi Yokochi
            @return: list of author sequence information for each loop
        """

        if isinstance(star_data, pynmrstar.Entry):
            loops = star_data.get_loops_by_category(lp_category)
        elif isinstance(star_data, pynmrstar.Saveframe):
            loops = [star_data.get_loop(lp_category)]
        else:
            loops = [star_data]

        f = []  # user warnings

        data = []  # data of all loops

        tags = [aseq_id, acomp_id, asym_id, seq_id, chain_id]
        tags_ = [aseq_id, acomp_id, seq_id, asym_id]

        is_dist_lp = 'Gen_dist_constraint' in lp_category
        is_dihed_lp = 'Torsion_angle_constraint' in lp_category
        is_target_lp = is_dist_lp or is_dihed_lp

        def skip_empty_value_error(lp, idx):
            if not is_target_lp:
                return False
            if is_dist_lp and 'Auth_comp_ID_1' in lp.tags and 'Auth_comp_ID_2' in lp.tags\
               and (lp.data[idx][lp.tags.index('Auth_comp_ID_1')] == 'HOH'
                    or lp.data[idx][lp.tags.index('Auth_comp_ID_2')] == 'HOH'):
                return True
            if is_dihed_lp and 'Torsion_angle_name' in lp.tags and lp.data[idx][lp.tags.index('Torsion_angle_name')] == 'PPA':
                return True
            return False

        seq_id_col = 3

        for loop in loops:
            seq_dict, acmp_dict, aseq_dict, asym_dict = {}, {}, {}, {}

            seq_data = []

            len_data = len(loop)

            if set(tags) & set(loop.tags) == set(tags):
                seq_data = loop.get_tag(tags)
            elif set(tags_) & set(loop.tags) == set(tags_):  # No Entity_assembly_ID tag case
                seq_data = loop.get_tag(tags_)
                for row in seq_data:
                    row.append('1')
                for row in loop:
                    row.append('1')
                loop.add_tag(chain_id)
                seq_id_col = 4
            else:
                _tags_exist = False
                for j in range(1, MAX_DIM_NUM_OF_SPECTRA):
                    _tags = [aseq_id + '_' + str(j), acomp_id + '_' + str(j), asym_id + '_' + str(j),
                             seq_id + '_' + str(j), chain_id + '_' + str(j)]
                    _tags_ = [aseq_id + '_' + str(j), acomp_id + '_' + str(j), asym_id + '_' + str(j), seq_id + '_' + str(j)]
                    if set(_tags) & set(loop.tags) == set(_tags):
                        _tags_exist = True
                        seq_data += loop.get_tag(_tags)
                    elif set(_tags_) & set(loop.tags) == set(_tags_):
                        _tags_exist = True
                        seq_data_ = loop.get_tag(_tags_)
                        for row_ in seq_data_:
                            row_.append('1')
                        seq_data += seq_data_

                if not _tags_exist:
                    missing_tags = list(set(tags) - set(loop.tags))
                    raise LookupError(f"Missing mandatory {missing_tags} loop tag(s).")

            if allow_empty:
                # seq_data = list(filter(is_data, seq_data))
                seq_data = list(filter(is_good_data, seq_data))  # DAOTHER-7389, issue #3
            else:
                for idx, row in enumerate(seq_data):
                    if is_empty(row) and idx < len_data:
                        if skip_empty_value_error(loop, idx):
                            continue
                        r = {}
                        for j, t in enumerate(loop.tags):
                            r[t] = loop.data[idx][j]
                        f.append("[Invalid data] Author sequence must not be empty. "
                                 f"#_of_row {idx + 1}, data_of_row {r}.")

            if len(seq_data) == 0:
                continue

            for idx, row in enumerate(seq_data):
                try:
                    int(row[seq_id_col])
                except (ValueError, TypeError):
                    if idx < len_data:
                        if skip_empty_value_error(loop, idx):
                            continue
                        r = {}
                        for j, t in enumerate(loop.tags):
                            r[t] = loop.data[idx][j]
                        f.append(f"[Invalid data] {seq_id} must be an integer. "
                                 f"#_of_row {idx + 1}, data_of_row {r}.")

            if len(f) > 0:
                raise UserWarning('\n'.join(sorted(list(set(f)), key=f.index)))

            try:

                chain_ids = sorted(set(row[4] for row in seq_data), key=lambda x: (len(x), x))
                offset_seq_ids = {row[4]: 0 for row in seq_data}
                for c in chain_ids:
                    min_seq_id = min(int(row[3]) for row in seq_data if row[4] == c)
                    if min_seq_id < 0:
                        offset_seq_ids[c] = min_seq_id * -1
                sorted_seq = sorted(set((row[4], int(row[3]) + offset_seq_ids[row[4]], row[2], row[0].strip(), row[1]) for row in seq_data),
                                    key=itemgetter(0, 1))

                chk_dict = {(row[4], int(row[3]), row[2], row[0].strip()): row[1] for row in seq_data}

                for row in seq_data:
                    chk_key = (row[4], int(row[3]), row[2], row[0].strip())
                    if chk_dict[chk_key] != row[1]:
                        raise KeyError(f"Author sequence must be unique. {chain_id} {row[4]}, {seq_id} {row[3]}, "
                                       f"{asym_id} {row[2]}, {aseq_id} {row[0]}, "
                                       f"{acomp_id} {row[1]} vs {chk_dict[chk_key]}.")

                for c in chain_ids:
                    acmp_dict[c] = [x[4] for x in sorted_seq if x[0] == c]
                    aseq_dict[c] = [x[3] for x in sorted_seq if x[0] == c]
                    asym_dict[c] = [x[2] for x in sorted_seq if x[0] == c]
                    seq_dict[c] = [x[1] - offset_seq_ids[c] for x in sorted_seq if x[0] == c]

                asm = []  # assembly of a loop

                for c in chain_ids:
                    ent = {}  # entity

                    ent['chain_id'] = str(c)
                    ent['seq_id'] = seq_dict[c]
                    ent['auth_asym_id'] = asym_dict[c]
                    ent['auth_seq_id'] = aseq_dict[c]
                    ent['auth_comp_id'] = acmp_dict[c]

                    asm.append(ent)

                data.append(asm)

            except (ValueError, TypeError):
                pass

        if len(data) == 0:
            data.append([])

        return data

    def get_nef_comp_atom_pair(self, star_data: Union[pynmrstar.Entry, pynmrstar.Saveframe, pynmrstar.Loop],
                               lp_category: str = 'nef_chemical_shift', comp_id: str = 'residue_name', atom_id: str = 'atom_name',
                               allow_empty: bool = False) -> List[List[dict]]:
        """ Wrapper function of get_comp_atom_pair() for an NEF file.
            @author: Masashi Yokochi
        """

        return self.get_comp_atom_pair(star_data, lp_category, comp_id, atom_id, allow_empty)

    def get_star_comp_atom_pair(self, star_data: Union[pynmrstar.Entry, pynmrstar.Saveframe, pynmrstar.Loop],
                                lp_category: str = 'Atom_chem_shift', comp_id: str = 'Comp_ID', atom_id: str = 'Atom_ID',
                                allow_empty: bool = False) -> List[List[dict]]:
        """ Wrapper function of get_comp_atom_pair() for an NMR-STAR file.
            @author: Masashi Yokochi
        """

        return self.get_comp_atom_pair(star_data, lp_category, comp_id, atom_id, allow_empty)

    def get_star_auth_comp_atom_pair(self, star_data: Union[pynmrstar.Entry, pynmrstar.Saveframe, pynmrstar.Loop],
                                     lp_category: str = 'Atom_chem_shift', comp_id: str = 'Auth_comp_ID', atom_id: str = 'Auth_atom_ID',
                                     allow_empty: bool = True) -> List[List[dict]]:
        """ Wrapper function of get_comp_atom_pair() for pairs of author comp_id and author atom_id in an NMR-STAR file.
            @author: Masashi Yokochi
        """

        return self.get_comp_atom_pair(star_data, lp_category, comp_id, atom_id, allow_empty)

    def get_comp_atom_pair(self, star_data: Union[pynmrstar.Entry, pynmrstar.Saveframe, pynmrstar.Loop],  # pylint: disable=no-self-use
                           lp_category: str, comp_id: str, atom_id: str, allow_empty: bool) -> List[List[dict]]:
        """ Extract unique pairs of comp_id and atom_id from any given loops in an NEF/NMR-STAR file.
            @author: Masashi Yokochi
            @return: list of unique pairs of comp_id and atom_id for each loop
        """

        if isinstance(star_data, pynmrstar.Entry):
            loops = star_data.get_loops_by_category(lp_category)
        elif isinstance(star_data, pynmrstar.Saveframe):
            loops = [star_data.get_loop(lp_category)]
        else:
            loops = [star_data]

        is_nef_dist_lp = 'nef_distance_restraint' in lp_category
        is_nef_dihed_lp = 'nef_dihedral_restraint' in lp_category
        is_star_dist_lp = 'Gen_dist_constraint' in lp_category
        is_star_dihed_lp = 'Torsion_angle_constraint' in lp_category
        is_target_lp = is_nef_dist_lp or is_nef_dihed_lp or is_star_dist_lp or is_star_dihed_lp

        def skip_empty_value_error(lp, idx):
            if not is_target_lp:
                return False
            if is_nef_dist_lp and 'residue_name_1' in lp.tags and 'residue_name_2' in lp.tags\
               and (lp.data[idx][lp.tags.index('residue_name_1')] == 'HOH'
                    or lp.data[idx][lp.tags.index('residue_name_2')] == 'HOH'):
                return True
            if is_nef_dihed_lp and 'name' in lp.tags and lp.data[idx][lp.tags.index('name')] == 'PPA':
                return True
            if is_star_dist_lp and 'Auth_comp_ID_1' in lp.tags and 'Auth_comp_ID_2' in lp.tags\
               and (lp.data[idx][lp.tags.index('Auth_comp_ID_1')] == 'HOH'
                    or lp.data[idx][lp.tags.index('Auth_comp_ID_2')] == 'HOH'):
                return True
            if is_star_dihed_lp and 'Torsion_angle_name' in lp.tags and lp.data[idx][lp.tags.index('Torsion_angle_name')] == 'PPA':
                return True
            return False

        f = []  # user warnings

        data = []  # data of all loops

        tags = [comp_id, atom_id]

        for loop in loops:
            atm_dict = {}

            pair_data = []

            len_data = len(loop)

            if set(tags) & set(loop.tags) == set(tags):
                pair_data = loop.get_tag(tags)
            else:
                _tags_exist = False
                for j in range(1, MAX_DIM_NUM_OF_SPECTRA):
                    _tags = [comp_id + '_' + str(j), atom_id + '_' + str(j)]
                    if set(_tags) & set(loop.tags) == set(_tags):
                        _tags_exist = True
                        pair_data += loop.get_tag(_tags)

                if not _tags_exist and lp_category != '_Peak_row_format':
                    missing_tags = list(set(tags) - set(loop.tags))
                    raise LookupError(f"Missing mandatory {missing_tags} loop tag(s).")

            if allow_empty:
                # pair_data = list(filter(is_data, pair_data))
                pair_data = list(filter(is_good_data, pair_data))  # DAOTHER-7389, issue #3
                if len(pair_data) == 0:
                    continue
            else:
                for idx, row in enumerate(pair_data):
                    if is_empty(row) and idx < len_data and not skip_empty_value_error(loop, idx):
                        r = {}
                        for j, t in enumerate(loop.tags):
                            r[t] = loop.data[idx][j]
                        f.append(f"[Invalid data] {comp_id} and {atom_id} must not be empty. "
                                 f"#_of_row {idx + 1}, data_of_row {r}.")

            if len(f) > 0:
                raise UserWarning('\n'.join(sorted(list(set(f)), key=f.index)))

            comps = sorted(set(row[0].upper() for row in pair_data if row[0] not in emptyValue))
            sorted_comp_atom = sorted(set((row[0].upper(), row[1]) for row in pair_data),
                                      key=itemgetter(0, 1))

            for c in comps:
                atm_dict[c] = [x[1] for x in sorted_comp_atom if x[0] == c]

            asm = []  # assembly of a loop

            for c in comps:
                ent = {}  # entity

                ent['comp_id'] = c
                ent['atom_id'] = atm_dict[c]

                asm.append(ent)

            data.append(asm)

        if len(data) == 0:
            data.append([])

        return data

    def get_nef_atom_type_from_cs_loop(self, star_data: Union[pynmrstar.Entry, pynmrstar.Saveframe, pynmrstar.Loop],
                                       lp_category: str = 'nef_chemical_shift', atom_type: str = 'element',
                                       isotope_number: str = 'isotope_number', atom_id: str = 'atom_name',
                                       allow_empty: bool = False) -> List[List[dict]]:
        """ Wrapper function of get_atom_type_from_cs_loop() for an NEF file.
            @author: Masashi Yokochi
        """

        return self.get_atom_type_from_cs_loop(star_data, lp_category, atom_type, isotope_number, atom_id, allow_empty)

    def get_star_atom_type_from_cs_loop(self, star_data: Union[pynmrstar.Entry, pynmrstar.Saveframe, pynmrstar.Loop],
                                        lp_category: str = 'Atom_chem_shift', atom_type: str = 'Atom_type',
                                        isotope_number: str = 'Atom_isotope_number', atom_id: str = 'Atom_ID',
                                        allow_empty: bool = False) -> List[List[dict]]:
        """ Wrapper function of get_atom_type_from_cs_loop() for an NMR-SAR file.
            @author: Masashi Yokochi
        """

        return self.get_atom_type_from_cs_loop(star_data, lp_category, atom_type, isotope_number, atom_id, allow_empty)

    def get_atom_type_from_cs_loop(self, star_data: Union[pynmrstar.Entry, pynmrstar.Saveframe, pynmrstar.Loop],  # pylint: disable=no-self-use,
                                   lp_category: str, atom_type: str, isotope_number: str, atom_id: str,
                                   allow_empty: bool) -> List[List[dict]]:
        """ Extract unique pairs of atom_type, isotope number, and atom_id from assigned chemical shifts in n NEF/NMR-SAR file.
            @author: Masashi Yokochi
            @return: list of unique pairs of atom_type, isotope number, and atom_id for each CS loop
        """

        if isinstance(star_data, pynmrstar.Entry):
            loops = star_data.get_loops_by_category(lp_category)
        elif isinstance(star_data, pynmrstar.Saveframe):
            loops = [star_data.get_loop(lp_category)]
        else:
            loops = [star_data]

        f = []  # user warnings

        data = []  # data of all loops

        tags = [atom_type, isotope_number, atom_id]

        for loop in loops:
            ist_dict, atm_dict = {}, {}

            a_type_data = []

            len_data = len(loop)

            if set(tags) & set(loop.tags) != set(tags):
                missing_tags = list(set(tags) - set(loop.tags))
                raise LookupError(f"Missing mandatory {missing_tags} loop tag(s).")

            a_type_data = loop.get_tag(tags)

            if allow_empty:
                # a_type_data = list(filter(is_data, a_type_data))
                a_type_data = list(filter(is_good_data, a_type_data))  # DAOTHER-7389, issue #3
                if len(a_type_data) == 0:
                    continue
            else:
                for idx, row in enumerate(a_type_data):
                    if is_empty(row) and idx < len_data:
                        r = {}
                        for j, t in enumerate(loop.tags):
                            r[t] = loop.data[idx][j]
                        f.append(f"[Invalid data] {atom_type}, {isotope_number}, and {atom_id} must not be empty. "
                                 f"#_of_row {idx + 1}, data_of_row {r}.")

            for idx, row in enumerate(a_type_data):
                try:
                    int(row[1])
                except (ValueError, TypeError):
                    if idx < len_data:
                        r = {}
                        for j, t in enumerate(loop.tags):
                            r[t] = loop.data[idx][j]
                        f.append(f"[Invalid data] {isotope_number} must be an integer. "
                                 f"#_of_row {idx + 1}, data_of_row {r}.")

            if len(f) > 0:
                raise UserWarning('\n'.join(sorted(list(set(f)), key=f.index)))

            try:

                a_types = sorted(set(row[0] for row in a_type_data))
                sorted_ist = sorted(set((row[0], int(row[1])) for row in a_type_data),
                                    key=itemgetter(0, 1))
                sorted_atm = sorted(set((row[0], row[2]) for row in a_type_data
                                        if not (row[2] in emptyValue or (isinstance(row[2], str) and badPattern.match(row[2])))),
                                    key=itemgetter(0, 1))  # DAOTHER-7389, issue #3

                for t in a_types:
                    ist_dict[t] = [x[1] for x in sorted_ist if x[0] == t]
                    atm_dict[t] = [x[1] for x in sorted_atm if x[0] == t]

                asm = []  # assembly of a loop

                for t in a_types:
                    ent = {}  # entity

                    ent['atom_type'] = t
                    ent['isotope_number'] = ist_dict[t]
                    ent['atom_id'] = atm_dict[t]

                    asm.append(ent)

                data.append(asm)

            except ValueError:
                pass

        if len(data) == 0:
            data.append([])

        return data

    def get_star_ambig_code_from_cs_loop(self, star_data: Union[pynmrstar.Entry, pynmrstar.Saveframe, pynmrstar.Loop],  # pylint: disable=no-self-use
                                         lp_category: str = 'Atom_chem_shift', comp_id: str = 'Comp_ID', atom_id: str = 'Atom_ID',
                                         ambig_code: str = 'Ambiguity_code', ambig_set_id: str = 'Ambiguity_set_ID') -> List[List[dict]]:
        """ Extract unique pairs of comp_id, atom_id, and ambiguity code from assigned chemical shifts in an NMR-SAR file.
            @author: Masashi Yokochi
            @return: list of unique pairs of comp_id, atom_id, and ambiguity code for each CS loop
        """

        if isinstance(star_data, pynmrstar.Entry):
            loops = star_data.get_loops_by_category(lp_category)
        elif isinstance(star_data, pynmrstar.Saveframe):
            loops = [star_data.get_loop(lp_category)]
        else:
            loops = [star_data]

        f = []  # user warnings

        data = []  # data of all loops

        tags = [comp_id, atom_id, ambig_code, ambig_set_id]

        for loop in loops:
            atm_dict = {}

            ambig_data = []

            len_data = len(loop)

            if set(tags) & set(loop.tags) != set(tags):
                missing_tags = list(set(tags) - set(loop.tags))
                raise LookupError(f"Missing mandatory {missing_tags} loop tag(s).")

            ambig_data = loop.get_tag(tags)

            if len(ambig_data) == 0:
                data.append(None)
                continue

            for idx, row in enumerate(ambig_data):
                # already checked elsewhere
                # if row[0] in emptyValue:
                #   raise ValueError(f"{comp_id} must not be empty.")
                # if row[1] in emptyValue:
                #    raise ValueError(f"{comp_id} must not be empty.")
                if row[2] not in emptyValue:

                    try:
                        code = int(row[2])
                    except ValueError:
                        if idx < len_data:
                            r = {}
                            for j, t in enumerate(loop.tags):
                                r[t] = loop.data[idx][j]
                            f.append(f"[Invalid data] {ambig_code} must be one of {ALLOWED_AMBIGUITY_CODES}. "
                                     f"#_of_row {idx + 1}, data_of_row {r}.")

                    if code not in ALLOWED_AMBIGUITY_CODES:
                        if idx < len_data:
                            r = {}
                            for j, t in enumerate(loop.tags):
                                r[t] = loop.data[idx][j]
                            f.append(f"[Invalid data] {ambig_code} must be one of {ALLOWED_AMBIGUITY_CODES}. "
                                     f"#_of_row {idx + 1}, data_of_row {r}.")

                    if code >= 4:
                        if row[3] in emptyValue and idx < len_data:
                            if code in (4, 5):
                                r = {}
                                for j, t in enumerate(loop.tags):
                                    r[t] = loop.data[idx][j]
                                f.append(f"[Invalid data] {ambig_set_id} must not be empty for {ambig_code} {code}. "
                                         f"#_of_row {idx + 1}, data_of_row {r}.")
                        else:
                            try:
                                int(row[3])
                            except (ValueError, TypeError):
                                if idx < len_data:
                                    r = {}
                                    for j, t in enumerate(loop.tags):
                                        r[t] = loop.data[idx][j]
                                    f.append(f"[Invalid data] {ambig_set_id} must be an integer. "
                                             f"#_of_row {idx + 1}, data_of_row {r}.")

                if row[3] not in emptyValue:

                    if row[2] in emptyValue or row[2] not in ('4', '5', '6', '9'):
                        if self.__remediation_mode:
                            loop.data[idx][loop.tags.index(ambig_set_id)] = '.'
                        else:
                            if idx < len_data:
                                r = {}
                                for j, t in enumerate(loop.tags):
                                    r[t] = loop.data[idx][j]
                                f.append(f"[Invalid data] {ambig_set_id} must be empty for {ambig_code} {row[2]}. "
                                         f"#_of_row {idx + 1}, data_of_row {r}.")

            if len(f) > 0:
                raise UserWarning('\n'.join(sorted(list(set(f)), key=f.index)))

            _ambig_data = [row for row in ambig_data
                           if not (row[0] in emptyValue or (isinstance(row[0], str) and badPattern.match(row[0])))
                           and not (row[1] in emptyValue or (isinstance(row[1], str) and badPattern.match(row[1])))]  # DAOTHER-7389, issue #3

            if len(_ambig_data) == 0:
                continue

            ambigs = sorted(set((row[0].upper(), row[2]) for row in _ambig_data),
                            key=itemgetter(0, 1))
            sorted_atm = sorted(set((row[0].upper(), row[2], row[1]) for row in _ambig_data),
                                key=itemgetter(0, 1, 2))

            for a in ambigs:
                atm_dict[a] = [x[2] for x in sorted_atm if x[0] == a[0] and x[1] == a[1]]

            asm = []  # assembly of a loop

            for a in ambigs:
                ent = {}  # entity

                ent['comp_id'] = a[0]
                ent['ambig_code'] = None if a[1] in emptyValue else int(a[1])
                ent['atom_id'] = atm_dict[a]

                asm.append(ent)

            data.append(asm)

        if len(data) == 0:
            data.append([])

        return data

    def get_index(self, star_data: Union[pynmrstar.Entry, pynmrstar.Saveframe, pynmrstar.Loop],  # pylint: disable=no-self-use
                  lp_category: str, index_id: str, row_limit: int = MAX_ROWS_TO_PERFORM_INDEX_ORDER_CHECK) -> List[List[int]]:
        """ Extract index_id from any given loops in an NEF/NMR-STAR file.
            @author: Masashi Yokochi
            @return: list of index for each loop
        """

        if isinstance(star_data, pynmrstar.Entry):
            loops = star_data.get_loops_by_category(lp_category)
        elif isinstance(star_data, pynmrstar.Saveframe):
            loops = [star_data.get_loop(lp_category)]
        else:
            loops = [star_data]

        f = []  # user warnings

        data = []  # data of all loops

        tags = [index_id]

        for loop in loops:
            index_data = []

            len_data = len(loop)

            if len_data > row_limit:
                raise UserWarning(f'[Too big loop] The total number of rows in a loop, {len_data}, exceeds the limit {row_limit}.')

            if set(tags) & set(loop.tags) == set(tags):
                index_data = loop.get_tag(tags)
            else:
                raise LookupError(f"Missing mandatory {index_id} loop tag.")

            for idx, i in enumerate(index_data):
                if i in emptyValue and idx < len_data:
                    r = {}
                    for j, t in enumerate(loop.tags):
                        r[t] = loop.data[idx][j]
                    f.append(f"[Invalid data] {index_id} must not be empty. "
                             f"#_of_row {idx + 1}, data_of_row {r}.")
                else:
                    try:
                        int(i)
                    except (ValueError, TypeError):
                        if idx < len_data:
                            r = {}
                            for j, t in enumerate(loop.tags):
                                r[t] = loop.data[idx][j]
                            f.append(f"[Invalid data] {index_id} must be an integer. "
                                     f"#_of_row {idx + 1}, data_of_row {r}.")

            if len(f) > 0:
                raise UserWarning('\n'.join(sorted(list(set(f)), key=f.index)))

            try:

                idxs = [int(row) for row in index_data]

                dup_idxs = [idx for idx in set(idxs) if idxs.count(idx) > 1]

                if len(dup_idxs) > 0:
                    raise KeyError(f"{index_id} must be unique in loop. {dup_idxs} are duplicated.")

                data.append(idxs)

            except ValueError:
                pass

        if len(data) == 0:
            data.append([])

        return data

    def check_data(self, star_data: Union[pynmrstar.Entry, pynmrstar.Saveframe, pynmrstar.Loop],
                   lp_category: str, key_items: List[dict], data_items: List[dict],
                   allowed_tags: Optional[List[str]] = None, disallowed_tags: Optional[List[str]] = None, parent_pointer: Optional[int] = None,
                   test_on_index: bool = False, enforce_non_zero: bool = False, enforce_sign: bool = False, enforce_range: bool = False,
                   enforce_enum: bool = False, enforce_allowed_tags: bool = False, excl_missing_data: bool = False) -> List[List[dict]]:
        """ Extract data with sanity check from any given loops in an NEF/NMR-STAR file.
            @author: Masashi Yokochi
            @return: list of extracted data for each loop
        """

        if isinstance(star_data, pynmrstar.Entry):
            loops = star_data.get_loops_by_category(lp_category)
        elif isinstance(star_data, pynmrstar.Saveframe):
            loops = [star_data.get_loop(lp_category)]
        else:
            loops = [star_data]

        is_nef_dist_lp = 'nef_distance_restraint' in lp_category
        is_nef_dihed_lp = 'nef_dihedral_restraint' in lp_category
        is_star_dist_lp = 'Gen_dist_constraint' in lp_category
        is_star_dihed_lp = 'Torsion_angle_constraint' in lp_category
        is_target_lp = is_nef_dist_lp or is_nef_dihed_lp or is_star_dist_lp or is_star_dihed_lp

        def skip_empty_value_error(lp, idx):
            if not is_target_lp:
                return False
            if is_nef_dist_lp and 'residue_name_1' in lp.tags and 'residue_name_2' in lp.tags\
               and (lp.data[idx][lp.tags.index('residue_name_1')] == 'HOH'
                    or lp.data[idx][lp.tags.index('residue_name_2')] == 'HOH'):
                return True
            if is_nef_dihed_lp and 'name' in lp.tags and lp.data[idx][lp.tags.index('name')] == 'PPA':
                return True
            if (is_nef_dist_lp or is_nef_dihed_lp) and 'restraint_combination_id' in lp.tags and lp.data[idx][lp.tags.index('restraint_combination_id')] in emptyValue:
                return True
            if is_star_dist_lp and 'Auth_comp_ID_1' in lp.tags and 'Auth_comp_ID_2' in lp.tags\
               and (lp.data[idx][lp.tags.index('Auth_comp_ID_1')] == 'HOH'
                    or lp.data[idx][lp.tags.index('Auth_comp_ID_2')] == 'HOH'):
                return True
            if is_star_dihed_lp and 'Torsion_angle_name' in lp.tags and lp.data[idx][lp.tags.index('Torsion_angle_name')] == 'PPA':
                return True
            if (is_star_dist_lp or is_star_dihed_lp) and 'Combination_ID' in lp.tags and lp.data[idx][lp.tags.index('Combination_ID')] in emptyValue:
                return True
            return False

        f, _f = [], []  # user warnings

        with io.StringIO() as idx_f, io.StringIO() as key_f, io.StringIO() as msg_f:

            data = []  # data of all loops

            item_types = ('str', 'bool', 'int', 'index-int', 'positive-int', 'positive-int-as-str', 'pointer-index',
                          'float', 'positive-float', 'range-float', 'enum', 'enum-int')

            for loop in loops:

                if is_target_lp:
                    if (is_nef_dist_lp or is_nef_dihed_lp) and 'restraint_combination_id' in loop.tags:
                        key_items = copy.deepcopy(key_items)
                        data_items = copy.deepcopy(data_items)
                        comb_item = next(item for item in data_items if item['name'] == 'restraint_combination_id')
                        key_items.insert(1, comb_item)
                        data_items.remove(comb_item)
                    elif (is_star_dist_lp or is_star_dihed_lp) and 'Combination_ID' in loop.tags:
                        key_items = copy.deepcopy(key_items)
                        data_items = copy.deepcopy(data_items)
                        comb_item = next(item for item in data_items if item['name'] == 'Combination_ID')
                        key_items.insert(1, comb_item)
                        data_items.remove(comb_item)

                key_names = [k['name'] for k in key_items]
                data_names = [d['name'] for d in data_items]
                mand_data_names = [d['name'] for d in data_items if d['mandatory']]
                _mand_data_names = [d['name'] for d in data_items if d['mandatory'] and 'default-from' in d]

                key_len = len(key_items)

                for k in key_items:
                    if k['type'] not in item_types:
                        raise TypeError(f"Type {k['type']} of data item {k['name']} must be one of {item_types}.")

                for d in data_items:
                    if d['type'] not in item_types:
                        raise TypeError(f"Type {d['type']} of data item {d['name']} must be one of {item_types}.")

                if allowed_tags is not None:

                    if len(key_names) > 0 and (set(key_names) | set(allowed_tags)) != set(allowed_tags):
                        raise LookupError(f"Key items {((set(key_names) | set(allowed_tags)) - set(allowed_tags))} must not exists.")

                    if len(data_names) > 0 and (set(data_names) | set(allowed_tags)) != set(allowed_tags):
                        raise LookupError(f"Data items {((set(data_names) | set(allowed_tags)) - set(allowed_tags))} must not exists.")

                    for d in data_items:
                        if 'group-mandatory' in d and d['group-mandatory']:
                            group = d['group']
                            if group['member-with'] is not None:
                                for mw in group['member-with']:
                                    if mw not in allowed_tags:
                                        raise ValueError(f"Member data item {mw} of {d['name']} must exists in allowed tags.")
                            if group['coexist-with'] is not None:
                                for cw in group['coexist-with']:
                                    if cw not in allowed_tags:
                                        raise ValueError(f"Coexisting data item {cw} of {d['name']} must exists in allowed tags.")

                _test_on_index = test_on_index
                if self.__remediation_mode and len(loop) > MAX_ROWS_TO_PERFORM_REDUNDANCY_CHECK:
                    _test_on_index = False

                if allowed_tags is not None:

                    if 'Details' in loop.tags and 'Details' not in allowed_tags:
                        loop.remove_tag('Details')

                    if loop.category == '_Assigned_peak_chem_shift' and 'Peak_contribution_ID' in loop.tags and 'Contribution_fractional_val' in allowed_tags:
                        col = loop.tags.index('Peak_contribution_ID')
                        loop.tags[col] = 'Contribution_fractional_val'

                    if loop.category == '_Atom_chem_shift' and 'NEF_atom_name' in loop.tags and 'PDB_atom_name' in allowed_tags:
                        col = loop.tags.index('NEF_atom_name')
                        loop.tags[col] = 'PDB_atom_name'

                    if loop.category == '_Bond' and 'Order' in loop.tags and 'Value_order' in allowed_tags:
                        col = loop.tags.index('Order')
                        loop.tags[col] = 'Value_order'

                    if loop.category == '_Spectral_dim':
                        if 'Encoded_source_dimension_ID' in loop.tags and 'Encoded_reduced_dimension_ID' in allowed_tags:
                            col = loop.tags.index('Encoded_source_dimension_ID')
                            loop.tags[col] = 'Encoded_reduced_dimension_ID'

                        if 'Folding_type' in loop.tags and 'Under_sampling_type' in allowed_tags:
                            col = loop.tags.index('Folding_type')
                            loop.tags[col] = 'Under_sampling_type'

                tag_data = []

                if len(key_names) > 0 and set(key_names) & set(loop.tags) != set(key_names):
                    missing_tags = list(set(key_names) - set(loop.tags))
                    for k in key_items:
                        if k['name'] in missing_tags:
                            if 'default-from' in k and k['default-from'] != 'self' and k['default-from'] in loop.tags:
                                from_col = loop.tags.index(k['default-from'])
                                for row in loop:
                                    ref = row[from_col]
                                    row.append(ref)
                                loop.add_tag(k['name'])
                            elif 'default' in k:
                                for row in loop:
                                    row.append(k['default'])
                                loop.add_tag(k['name'])
                            elif 'auto-increment' in k and k['auto-increment']:
                                for lv, row in enumerate(loop.data, start=1):
                                    row.append(lv)
                                loop.add_tag(k['name'])
                            else:
                                raise LookupError(f"Missing mandatory {missing_tags} loop tag(s).")

                if len(mand_data_names) > 0 and set(mand_data_names) & set(loop.tags) != set(mand_data_names):
                    missing_tags = list(set(mand_data_names) - set(loop.tags))
                    for k in key_items:
                        if k['name'] in missing_tags:
                            if 'default-from' in k and k['default-from'] != 'self' and k['default-from'] in loop.tags:
                                from_col = loop.tags.index(k['default-from'])
                                for row in loop:
                                    ref = row[from_col]
                                    row.append(ref)
                                loop.add_tag(k['name'])
                            elif 'default' in k:
                                for row in loop:
                                    row.append(k['default'])
                                loop.add_tag(k['name'])
                            elif 'auto-increment' in k and k['auto-increment']:
                                for lv, row in enumerate(loop.data, start=1):
                                    row.append(lv)
                                loop.add_tag(k['name'])
                            else:
                                raise LookupError(f"Missing mandatory {missing_tags} loop tag(s).")

                if len(_mand_data_names) > 0 and set(_mand_data_names) & set(loop.tags) != set(_mand_data_names):
                    missing_tags = list(set(_mand_data_names) - set(loop.tags))
                    for d in data_items:
                        if d['name'] in missing_tags:
                            if 'default-from' in d:
                                if d['type'] == 'index-int':
                                    for lv, row in enumerate(loop.data, start=1):
                                        row.append(lv)
                                    loop.add_tag(d['name'])
                                elif d['default-from'] != 'self' and d['default-from'] in loop.tags:
                                    from_col = loop.tags.index(d['default-from'])
                                    if d['name'] == 'element' or d['name'] == 'Atom_type':
                                        for row in loop:
                                            ref = row[from_col]
                                            if ref[0] in pseProBeginCode:
                                                row.append('H')
                                            else:
                                                row.append(ref[0])
                                        loop.add_tag(d['name'])
                                    elif d['name'] == 'isotope_number' or d['name'] == 'Atom_isotope_number':
                                        for row in loop:
                                            ref = row[from_col]
                                            if ref[0] in pseProBeginCode or ref[0] not in ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS:
                                                row.append(1)
                                            else:
                                                row.append(ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS[ref[0]][0])
                                        loop.add_tag(d['name'])
                                    elif 'Entity_assembly_ID' in d['name'] or d['name'] == 'Axis_code':
                                        for row in loop:
                                            ref = row[from_col]
                                            row.append(ref)
                                        loop.add_tag(d['name'])
                            elif 'auto-increment' in d and d['auto-increment']:
                                for lv, row in enumerate(loop.data, start=1):
                                    row.append(lv)
                                loop.add_tag(d['name'])

                if disallowed_tags is not None:
                    if len(set(loop.tags) & set(disallowed_tags)) > 0:
                        disallow_tags = list(set(loop.tags) & set(disallowed_tags))
                        raise LookupError(f"Disallowed {disallow_tags} loop tag(s) exists.")

                if enforce_allowed_tags and allowed_tags is not None:
                    extra_tags = (set(loop.tags) | set(allowed_tags)) - set(allowed_tags)
                    if len(extra_tags) > 0 and not self.__remediation_mode:
                        raise LookupError(f"Unauthorized {extra_tags} loop tag(s) must not exists.")  # DAOTHER-7545 only for NMR-STAR

                for d in data_items:
                    if 'group-mandatory' in d and d['group-mandatory']:
                        name = d['name']
                        group = d['group']
                        if name in loop.tags:
                            if group['coexist-with'] is not None:
                                for cw in group['coexist-with']:
                                    if cw not in loop.tags:
                                        set_cw = set(group['coexist-with'])
                                        set_cw.add(name)
                                        missing_tags = list(set_cw - set(loop.tags))
                                        raise LookupError(f"Missing mandatory {missing_tags} loop tag(s).")

                        elif group['member-with'] is not None:
                            has_member = False
                            for mw in group['member-with']:
                                if mw in loop.tags:
                                    has_member = True
                                    break
                            if not has_member and not all(mw.endswith('_max') or mw.endswith('_min') for mw in group['member-with']):
                                set_mw = set(group['member-with'])
                                set_mw.add(name)
                                missing_tags = list(set_mw - set(loop.tags))
                                raise LookupError(f"Missing mandatory {missing_tags} loop tag(s).")

                tags = [k['name'] for k in key_items]
                for data_name in set(data_names) & set(loop.tags):
                    tags.append(data_name)

                tag_len = len(tags)

                static_val = {}
                for name in tags:
                    static_val[name] = None

                idx_tag_ids = set()
                for j in range(tag_len):
                    name = tags[j]
                    if name in key_names:
                        for k in key_items:
                            if k['name'] == name and k['type'] == 'index-int':
                                idx_tag_ids.add(j)
                    else:
                        for d in data_items:
                            if d['name'] == name and d['type'] == 'index-int':
                                idx_tag_ids.add(j)

                relax_key_ids = set()
                for j in range(tag_len):
                    name = tags[j]
                    for d in data_items:
                        if d['name'] == name and 'relax-key-if-exist' in d and d['relax-key-if-exist']:
                            relax_key_ids.add(j)

                tag_data = loop.get_tag(tags)

                if _test_on_index:  # and len(idx_tag_ids) > 0 and len(tag_data) <= MAX_ROWS_TO_PERFORM_REDUNDANCY_CHECK:

                    for idx, idx_tag_id in enumerate(idx_tag_ids):

                        try:
                            idxs = [int(row[idx_tag_id]) for row in tag_data]

                            dup_idxs = [_idx for _idx in set(idxs) if idxs.count(_idx) > 1]

                            if len(dup_idxs) > 0:
                                raise KeyError(f"{tags[idx_tag_id]} must be unique in loop. {dup_idxs} are duplicated.")

                        except (ValueError, TypeError):
                            r = {}
                            for j, t in enumerate(loop.tags):
                                r[t] = loop.data[idx][j]
                            raise ValueError(f"{tags[idx_tag_id]} must be an integer. "
                                             f"#_of_row {idx + 1}, data_of_row {r}.")

                if not excl_missing_data:
                    for idx, row in enumerate(tag_data):
                        for j in range(tag_len):
                            if row[j] in emptyValue:
                                name = tags[j]
                                if name in key_names:
                                    k = key_items[key_names.index(name)]
                                    if not ('remove-bad-pattern' in k and k['remove-bad-pattern']) and 'default' not in k\
                                       and not skip_empty_value_error(loop, idx):
                                        r = {}
                                        for _j, _t in enumerate(loop.tags):
                                            r[_t] = loop.data[idx][_j]
                                        raise ValueError(f"{name} must not be empty. "
                                                         f"#_of_row {idx + 1}, data_of_row {r}.")

                                for d in data_items:
                                    if d['name'] == name and d['mandatory'] and 'default' not in d\
                                       and not ('remove-bad-pattern' in d and d['detele-bad-pattern'])\
                                       and not skip_empty_value_error(loop, idx):
                                        r = {}
                                        for _j, _t in enumerate(loop.tags):
                                            r[_t] = loop.data[idx][_j]
                                        raise ValueError(f"{name} must not be empty. "
                                                         f"#_of_row {idx + 1}, data_of_row {r}.")

                if _test_on_index and key_len > 0:
                    keys = set()

                    rechk = False

                    for row in tag_data:

                        if key_f.tell() > 0:
                            key_f.truncate(0)
                            key_f.seek(0)

                        for j in range(key_len):
                            key_f.write(f'{row[j]} ')

                        key = key_f.getvalue()

                        if key in keys:

                            relax_key = False

                            if len(relax_key_ids) > 0:
                                for j in relax_key_ids:
                                    if row[j] is not emptyValue:
                                        relax_key = True
                                        break

                            if relax_key:
                                rechk = True

                            else:

                                if msg_f.tell() > 0:
                                    msg_f.truncate(0)
                                    msg_f.seek(0)

                                for j in range(key_len):
                                    msg_f.write(f'{key_names[j]} {row[j]}, ')

                                pos = msg_f.tell() - 2
                                msg_f.truncate(pos)
                                msg_f.seek(pos)

                                idx_msg = ''

                                if idx_f.tell() > 0:
                                    idx_f.truncate(0)
                                    idx_f.seek(0)

                                if len(idx_tag_ids) > 0:
                                    for _j in idx_tag_ids:
                                        idx_f.write(f'{tags[_j]} ')

                                        for _row in tag_data:

                                            if key_f.tell() > 0:
                                                key_f.truncate(0)
                                                key_f.seek(0)

                                            for j in range(key_len):
                                                key_f.write(f'{_row[j]} ')

                                            _key = key_f.getvalue()

                                            if key == _key:
                                                idx_f.write(f'{_row[_j]} vs ')

                                        pos = idx_f.tell() - 4
                                        idx_f.truncate(pos)
                                        idx_f.seek(pos)

                                        idx_f.write(', ')

                                    pos = idx_f.tell() - 2
                                    idx_f.truncate(pos)
                                    idx_f.seek(pos)

                                    idx_msg = f"[Check rows of {idx_f.getvalue()}] "

                                f.append("[Multiple data] "
                                         f"{idx_msg}Duplicated rows having the following values {msg_f.getvalue()} exist in a loop.")

                        else:
                            keys.add(key)

                    if rechk:
                        keys = set()

                        for row in tag_data:

                            if key_f.tell() > 0:
                                key_f.truncate(0)
                                key_f.seek(0)

                            for j in range(key_len):
                                key_f.write(f'{row[j]} ')
                            for j in relax_key_ids:
                                key_f.write(f'{row[j]} ')

                            key = key_f.getvalue()

                            if key in keys:

                                if msg_f.tell() > 0:
                                    msg_f.truncate(0)
                                    msg_f.seek(0)

                                for j in range(key_len):
                                    msg_f.write(f'{key_names[j]} {row[j]}, ')
                                for j in relax_key_ids:
                                    if row[j] not in emptyValue:
                                        msg_f.write(f'{tags[j]} {row[j]}, ')

                                pos = msg_f.tell() - 2
                                msg_f.truncate(pos)
                                msg_f.seek(pos)

                                idx_msg = ''

                                if idx_f.tell() > 0:
                                    idx_f.truncate(0)
                                    idx_f.seek(0)

                                if len(idx_tag_ids) > 0:
                                    for _j in idx_tag_ids:
                                        idx_f.write(f'{tags[_j]} ')

                                        for _row in tag_data:

                                            if key_f.tell() > 0:
                                                key_f.truncate(0)
                                                key_f.seek(0)

                                            for j in range(key_len):
                                                key_f.write(f'{_row[j]} ')
                                            for j in relax_key_ids:
                                                key_f.write(f'{_row[j]} ')

                                            _key = key_f.getvalue()

                                            if key == _key:
                                                idx_f.write(f'{_row[_j]} vs ')

                                        pos = idx_f.tell() - 4
                                        idx_f.truncate(pos)
                                        idx_f.seek(pos)

                                        idx_f.write(', ')

                                    pos = idx_f.tell() - 2
                                    idx_f.truncate(pos)
                                    idx_f.seek(pos)

                                    idx_msg = f"[Check rows of {idx_f.getvalue()}] "

                                f.append("[Multiple data] "
                                         f"{idx_msg}Duplicated rows having the following values {msg_f.getvalue()} exist in a loop.")

                            else:
                                keys.add(key)

                if len(f) > 0:

                    for k in key_items:
                        if k['type'] == 'int' and 'default-from' in k and k['default-from'] in loop.tags:
                            to_idx = loop.tags.index(k['name'])
                            fr_idx = loop.tags.index(k['default-from'])

                            offset = None

                            for row in loop:
                                if row[to_idx] not in emptyValue and row[fr_idx] not in emptyValue:
                                    try:
                                        offset = int(row[to_idx]) - int(row[fr_idx])
                                        break
                                    except ValueError:
                                        continue

                            if offset is not None:

                                for idx, row in enumerate(loop.data):
                                    if row[to_idx] not in emptyValue and row[fr_idx] not in emptyValue:
                                        try:
                                            loop.data[idx][to_idx] = str(int(row[fr_idx]) + offset)
                                        except ValueError:
                                            continue

                    tag_data = loop.get_tag(tags)

                    if _test_on_index and key_len > 0:
                        keys = set()

                        rechk = False

                        for row in tag_data:

                            if key_f.tell() > 0:
                                key_f.truncate(0)
                                key_f.seek(0)

                            for j in range(key_len):
                                key_f.write(f'{row[j]} ')

                            key = key_f.getvalue()

                            if key in keys:

                                relax_key = False

                                if len(relax_key_ids) > 0:
                                    for j in relax_key_ids:
                                        if row[j] is not emptyValue:
                                            relax_key = True
                                            break

                                if relax_key:
                                    rechk = True

                                else:

                                    if msg_f.tell() > 0:
                                        msg_f.truncate(0)
                                        msg_f.seek(0)

                                    for j in range(key_len):
                                        msg_f.write(f'{key_names[j]} {row[j]}, ')

                                    pos = msg_f.tell() - 2
                                    msg_f.truncate(pos)
                                    msg_f.seek(pos)

                                    idx_msg = ''

                                    if idx_f.tell() > 0:
                                        idx_f.truncate(0)
                                        idx_f.seek(0)

                                    if len(idx_tag_ids) > 0:
                                        for _j in idx_tag_ids:
                                            idx_f.write(f'{tags[_j]} ')

                                            for _row in tag_data:

                                                if key_f.tell() > 0:
                                                    key_f.truncate(0)
                                                    key_f.seek(0)

                                                for j in range(key_len):
                                                    key_f.write(f'{_row[j]} ')

                                                _key = key_f.getvalue()

                                                if key == _key:
                                                    idx_f.write(f'{_row[_j]} vs ')

                                            pos = idx_f.tell() - 4
                                            idx_f.truncate(pos)
                                            idx_f.seek(pos)

                                            idx_f.write(', ')

                                        pos = idx_f.tell() - 2
                                        idx_f.truncate(pos)
                                        idx_f.seek(pos)

                                        idx_msg = f"[Check rows of {idx_f.getvalue()}] "

                                    _f.append("[Multiple data] "
                                              f"{idx_msg}Duplicated rows having the following values {msg_f.getvalue()} exist in a loop.")

                            else:
                                keys.add(key)

                        if rechk:
                            keys = set()

                            for row in tag_data:

                                if key_f.tell() > 0:
                                    key_f.truncate(0)
                                    key_f.seek(0)

                                for j in range(key_len):
                                    key_f.write(f'{row[j]} ')
                                for j in relax_key_ids:
                                    key_f.write(f'{row[j]} ')

                                key = key_f.getvalue()

                                if key in keys:

                                    if msg_f.tell() > 0:
                                        msg_f.truncate(0)
                                        msg_f.seek(0)

                                    for j in range(key_len):
                                        msg_f.write(f'{key_names[j]} {row[j]}, ')
                                    for j in relax_key_ids:
                                        if row[j] not in emptyValue:
                                            msg_f.write(f'{tags[j]} {row[j]}, ')

                                    pos = msg_f.tell() - 2
                                    msg_f.truncate(pos)
                                    msg_f.seek(pos)

                                    idx_msg = ''

                                    if idx_f.tell() > 0:
                                        idx_f.truncate(0)
                                        idx_f.seek(0)

                                    if len(idx_tag_ids) > 0:
                                        for _j in idx_tag_ids:
                                            idx_f.write(f'{tags[_j]} ')

                                            for _row in tag_data:

                                                if key_f.tell() > 0:
                                                    key_f.truncate(0)
                                                    key_f.seek(0)

                                                for j in range(key_len):
                                                    key_f.write(f'{_row[j]} ')
                                                for j in relax_key_ids:
                                                    key_f.write(f'{_row[j]} ')

                                                _key = key_f.getvalue()

                                                if key == _key:
                                                    idx_f.write(f'{_row[_j]} vs ')

                                            pos = idx_f.tell() - 4
                                            idx_f.truncate(pos)
                                            idx_f.seek(pos)

                                            idx_f.write(', ')

                                        pos = idx_f.tell() - 2
                                        idx_f.truncate(pos)
                                        idx_f.seek(pos)

                                        idx_msg = f"[Check rows of {idx_f.getvalue()}] "

                                    _f.append("[Multiple data] "
                                              f"{idx_msg}Duplicated rows having the following values {msg_f.getvalue()} exist in a loop.")

                                else:
                                    keys.add(key)

                    if len(_f) == 0:
                        f = []

                asm = []  # assembly of a loop

                for idx, row in enumerate(tag_data):
                    ent = {}  # entity

                    missing_mandatory_data = remove_bad_pattern = clear_bad_pattern = False

                    for j in range(tag_len):
                        name = tags[j]
                        val = row[j]
                        if j < key_len:
                            k = key_items[j]
                            type = k['type']  # pylint: disable=redefined-builtin
                            if val in emptyValue and 'default' in k and k['default'] in emptyValue:
                                ent[name] = k['default']
                            elif type == 'bool':
                                try:
                                    ent[name] = val.lower() in trueValue
                                except ValueError:
                                    if 'remove-bad-pattern' in k and k['remove-bad-pattern']:
                                        remove_bad_pattern = True
                                        continue
                                    if 'clear-bad-pattern' in k and k['clear-bad-pattern']:
                                        ent[name] = loop.data[idx][loop.tags.index(name)] = None
                                        clear_bad_pattern = True
                                        continue
                                    if excl_missing_data:
                                        missing_mandatory_data = True
                                        continue
                                    if skip_empty_value_error(loop, idx):
                                        continue
                                    raise ValueError(get_idx_msg(idx_tag_ids, tags, ent)
                                                     + f"{name} {val!r} must be {self.readableItemType[type]}.")

                            elif type == 'int':
                                try:
                                    ent[name] = int(val)
                                except (ValueError, TypeError):
                                    if 'default-from' in k and k['default-from'] == 'self':
                                        row[j] = ent[name] = letterToDigit(val)
                                    elif 'default-from' in k and k['default-from'] in tags:
                                        row[j] = ent[name] = letterToDigit(row[tags.index(k['default-from'])])
                                    elif 'default' in k:
                                        row[j] = ent[name] = int(k['default'])
                                    elif 'remove-bad-pattern' in k and k['remove-bad-pattern']:
                                        remove_bad_pattern = True
                                        continue
                                    elif 'clear-bad-pattern' in k and k['clear-bad-pattern']:
                                        ent[name] = loop.data[idx][loop.tags.index(name)] = None
                                        clear_bad_pattern = True
                                        continue
                                    elif excl_missing_data:
                                        missing_mandatory_data = True
                                        continue
                                    elif skip_empty_value_error(loop, idx):
                                        continue
                                    else:
                                        raise ValueError(get_idx_msg(idx_tag_ids, tags, ent)
                                                         + f"{name} {val!r} must be {self.readableItemType[type]}.")

                            elif type in ('index-int', 'positive-int', 'positive-int-as-str'):
                                try:
                                    ent[name] = int(val)
                                except (ValueError, TypeError):
                                    if 'default-from' in k and k['default-from'] == 'self':
                                        row[j] = ent[name] = letterToDigit(val, 1)
                                    elif 'default-from' in k and k['default-from'] in tags and row[tags.index(k['default-from'])] not in emptyValue:
                                        row[j] = ent[name] = letterToDigit(row[tags.index(k['default-from'])], 1)
                                        if ent[name] > 8 and not self.__remediation_mode and 'default' in k:
                                            row[j] = ent[name] = int(k['default'])
                                    elif 'default-from' in k and k['default-from'].startswith('Auth_asym_ID'):
                                        row[j] = ent[name] = letterToDigit(val, 1)
                                    elif 'default' in k:
                                        row[j] = ent[name] = int(k['default'])
                                    elif 'remove-bad-pattern' in k and k['remove-bad-pattern']:
                                        remove_bad_pattern = True
                                        continue
                                    elif 'clear-bad-pattern' in k and k['clear-bad-pattern']:
                                        ent[name] = loop.data[idx][loop.tags.index(name)] = None
                                        clear_bad_pattern = True
                                        continue
                                    elif excl_missing_data:
                                        missing_mandatory_data = True
                                        continue
                                    elif skip_empty_value_error(loop, idx):
                                        continue
                                    else:
                                        raise ValueError(get_idx_msg(idx_tag_ids, tags, ent)
                                                         + f"{name} {val!r} must be {self.readableItemType[type]}.")

                                if (type == 'index-int' and ent[name] <= 0)\
                                   or (type == 'positive-int' and (ent[name] < 0 or (ent[name] == 0 and 'enforce-non-zero' in k and k['enforce-non-zero']))):
                                    raise ValueError(get_idx_msg(idx_tag_ids, tags, ent)
                                                     + f"{name} {val!r} must be {self.readableItemType[type]}.")
                                if ent[name] == 0 and enforce_non_zero:
                                    if 'void-zero' in k:
                                        if self.replace_zero_by_null_in_case:
                                            loop.data[idx][loop.tags.index(name)] = None
                                        ent[name] = None
                                    else:
                                        f.append(f"[Zero value error] {get_idx_msg(idx_tag_ids, tags, ent)}"
                                                 f"{name} {val!r} should not be zero, "
                                                 f"as defined by {self.readableItemType[type]}.")
                                if type == 'positive-int-as-str':
                                    row[j] = ent[name] = str(ent[name])

                            elif type == 'pointer-index':
                                try:
                                    ent[name] = int(val)
                                except (ValueError, TypeError):
                                    if 'default-from' in k and k['default-from'] == 'self':
                                        row[j] = ent[name] = letterToDigit(val, 1)
                                    elif 'default-from' in k and k['default-from'] in tags:
                                        row[j] = ent[name] = letterToDigit(row[tags.index(k['default-from'])], 1)
                                    elif 'default-from' in k and k['default-from'] == 'parent' and parent_pointer is not None:
                                        row[j] = ent[name] = parent_pointer
                                    elif 'default' in k:
                                        row[j] = ent[name] = int(k['default'])
                                    elif 'remove-bad-pattern' in k and k['remove-bad-pattern']:
                                        remove_bad_pattern = True
                                        continue
                                    elif 'clear-bad-pattern' in k and k['clear-bad-pattern']:
                                        ent[name] = loop.data[idx][loop.tags.index(name)] = None
                                        clear_bad_pattern = True
                                        continue
                                    elif excl_missing_data:
                                        missing_mandatory_data = True
                                        continue
                                    elif skip_empty_value_error(loop, idx):
                                        continue
                                    else:
                                        raise ValueError(get_idx_msg(idx_tag_ids, tags, ent)
                                                         + f"{name} {val!r} must be {self.readableItemType[type]}.")

                                if ent[name] <= 0:
                                    raise ValueError(get_idx_msg(idx_tag_ids, tags, ent)
                                                     + f"{name} {val!r} must be {self.readableItemType[type]}.")
                                if static_val[name] is None:
                                    static_val[name] = val
                                elif val != static_val[name] and _test_on_index:
                                    raise ValueError(get_idx_msg(idx_tag_ids, tags, ent)
                                                     + f"{name} {val} vs {static_val[name]} must be {self.readableItemType[type]}.")
                            elif type == 'float':
                                try:
                                    ent[name] = float(val)
                                except (ValueError, TypeError):
                                    if 'remove-bad-pattern' in k and k['remove-bad-pattern']:
                                        remove_bad_pattern = True
                                        continue
                                    if 'clear-bad-pattern' in k and k['clear-bad-pattern']:
                                        ent[name] = loop.data[idx][loop.tags.index(name)] = None
                                        clear_bad_pattern = True
                                        continue
                                    if excl_missing_data:
                                        missing_mandatory_data = True
                                        continue
                                    if skip_empty_value_error(loop, idx):
                                        continue
                                    raise ValueError(get_idx_msg(idx_tag_ids, tags, ent)
                                                     + f"{name} {val!r} must be {self.readableItemType[type]}.")

                            elif type == 'positive-float':
                                try:
                                    ent[name] = float(val)
                                except (ValueError, TypeError):
                                    if 'remove-bad-pattern' in k and k['remove-bad-pattern']:
                                        remove_bad_pattern = True
                                        continue
                                    if 'clear-bad-pattern' in k and k['clear-bad-pattern']:
                                        ent[name] = loop.data[idx][loop.tags.index(name)] = None
                                        clear_bad_pattern = True
                                        continue
                                    if excl_missing_data:
                                        missing_mandatory_data = True
                                        continue
                                    if skip_empty_value_error(loop, idx):
                                        continue
                                    raise ValueError(get_idx_msg(idx_tag_ids, tags, ent)
                                                     + f"{name} {val!r} must be {self.readableItemType[type]}.")

                                if ent[name] < 0.0 or (ent[name] == 0.0 and 'enforce-non-zero' in k and k['enforce-non-zero']):
                                    raise ValueError(get_idx_msg(idx_tag_ids, tags, ent)
                                                     + f"{name} {val!r} must be {self.readableItemType[type]}.")
                                if ent[name] == 0.0 and enforce_non_zero:
                                    if 'void-zero' in k:
                                        if self.replace_zero_by_null_in_case:
                                            loop.data[idx][loop.tags.index(name)] = None
                                        ent[name] = None
                                    else:
                                        f.append(f"[Zero value error] {get_idx_msg(idx_tag_ids, tags, ent)}"
                                                 f"{name} {val!r} should not be zero, "
                                                 f"as defined by {self.readableItemType[type]}.")

                            elif type == 'range-float':
                                try:
                                    _range = k['range']
                                    ent[name] = float(val)
                                except KeyError:
                                    raise ValueError(f"Range of key item {name} is not defined")
                                except (ValueError, TypeError):
                                    if 'remove-bad-pattern' in k and k['remove-bad-pattern']:
                                        remove_bad_pattern = True
                                        continue
                                    if 'clear-bad-pattern' in k and k['clear-bad-pattern']:
                                        ent[name] = loop.data[idx][loop.tags.index(name)] = None
                                        clear_bad_pattern = True
                                        continue
                                    if excl_missing_data:
                                        missing_mandatory_data = True
                                        continue
                                    if skip_empty_value_error(loop, idx):
                                        continue
                                    if not enforce_range:
                                        ent[name] = None
                                        continue
                                    f.append(f"[Range value error] {get_idx_msg(idx_tag_ids, tags, ent)}"
                                             f"{name} {val!r} must be {self.readableItemType[type]}.")
                                    continue

                                if ('min_exclusive' in _range and _range['min_exclusive'] == 0.0 and ent[name] <= 0.0)\
                                   or ('min_inclusive' in _range and _range['min_inclusive'] == 0.0 and ent[name] < 0):
                                    if ent[name] < 0.0:
                                        if ('max_inclusive' in _range and abs(ent[name]) > _range['max_inclusive'])\
                                           or ('max_exclusive' in _range and abs(ent[name]) >= _range['max_exclusive'])\
                                           or ('enforce-sign' in k and k['enforce-sign']):
                                            if not enforce_range:
                                                ent[name] = None
                                            else:
                                                f.append(f"[Range value error] {get_idx_msg(idx_tag_ids, tags, ent)}"
                                                         f"{name} {val!r} must be within range {_range}.")
                                        elif enforce_sign:
                                            f.append(f"[Negative value error] {get_idx_msg(idx_tag_ids, tags, ent)}"
                                                     f"{name} {val!r} should not have "
                                                     f"negative value for {self.readableItemType[type]}, {_range}.")
                                    elif ent[name] == 0.0 and 'enforce-non-zero' in k and k['enforce-non-zero']:
                                        if not enforce_range:
                                            ent[name] = None
                                        else:
                                            f.append(f"[Range value error] {get_idx_msg(idx_tag_ids, tags, ent)}"
                                                     f"{name} {val!r} must be within range {_range}.")
                                    elif ent[name] == 0.0 and enforce_non_zero:
                                        if 'void-zero' in k:
                                            if self.replace_zero_by_null_in_case:
                                                loop.data[idx][loop.tags.index(name)] = None
                                            ent[name] = None
                                        else:
                                            f.append(f"[Zero value error] {get_idx_msg(idx_tag_ids, tags, ent)}"
                                                     f"{name} {val!r} should not be zero, "
                                                     f"as defined by {self.readableItemType[type]}, {_range}.")
                                elif ('min_exclusive' in _range and ent[name] <= _range['min_exclusive']) or\
                                     ('min_inclusive' in _range and ent[name] < _range['min_inclusive']) or\
                                     ('max_inclusive' in _range and ent[name] > _range['max_inclusive']) or\
                                     ('max_exclusive' in _range and ent[name] >= _range['max_exclusive']):
                                    if 'void-zero' in k and ent[name] == 0.0:
                                        if self.replace_zero_by_null_in_case:
                                            loop.data[idx][loop.tags.index(name)] = None
                                        ent[name] = None
                                    elif not enforce_range:
                                        ent[name] = None
                                    else:
                                        f.append(f"[Range value error] {get_idx_msg(idx_tag_ids, tags, ent)}"
                                                 f"{name} {val!r} must be within range {_range}.")
                            elif type == 'enum':
                                try:
                                    enum = k['enum']
                                    if val not in enum:
                                        if 'default' in k:
                                            val = k['default']
                                            row[j] = val
                                        if 'default-from' in k and k['default-from'] in tags:
                                            if row[tags.index(k['default-from'])][0].upper() in enum:
                                                val = row[tags.index(k['default-from'])][0].upper()
                                        elif 'enum-alt' in k and val in k['enum-alt']:
                                            val = k['enum-alt'][val]
                                            row[j] = val
                                        elif 'enforce-enum' in k and k['enforce-enum']:
                                            if excl_missing_data:
                                                missing_mandatory_data = True
                                                continue
                                            if 'remove-bad-pattern' in k and k['remove-bad-pattern']:
                                                remove_bad_pattern = True
                                                continue
                                            if 'clear-bad-pattern' in k and k['clear-bad-pattern']:
                                                ent[name] = loop.data[idx][loop.tags.index(name)] = None
                                                clear_bad_pattern = True
                                                continue
                                            if skip_empty_value_error(loop, idx):
                                                continue
                                            raise ValueError(get_idx_msg(idx_tag_ids, tags, ent)
                                                             + f"{name} {val!r} must be one of {enum}.")
                                        elif enforce_enum and name in mand_data_names:
                                            f.append(f"[Enumeration error] {get_idx_msg(idx_tag_ids, tags, ent)}"
                                                     f"{name} {val!r} should be one of {enum}.")
                                    ent[name] = val
                                except KeyError:
                                    raise ValueError(f"Enumeration of key item {name} is not defined")

                            elif type == 'enum-int':
                                try:
                                    enum = k['enum']
                                    if int(val) not in enum:
                                        if 'default' in k:
                                            val = str(k['default'])
                                        if 'default-from' in k and k['default-from'] in tags:
                                            if row[tags.index(k['default-from'])][0].upper() in ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS:
                                                val = ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS[row[tags.index(k['default-from'])][0].upper()][0]
                                        if 'enforce-enum' in k and k['enforce-enum']:
                                            raise ValueError(get_idx_msg(idx_tag_ids, tags, ent)
                                                             + f"{name} {val!r} must be one of {enum}.")
                                        if enforce_enum:
                                            f.append(f"[Enumeration error] {get_idx_msg(idx_tag_ids, tags, ent)}"
                                                     f"{name} {val!r} should be one of {enum}.")
                                    ent[name] = int(val)
                                except KeyError:
                                    raise ValueError(f"Enumeration of key item {name} is not defined")
                                except (ValueError, TypeError):
                                    if 'remove-bad-pattern' in k and k['remove-bad-pattern']:
                                        remove_bad_pattern = True
                                        continue
                                    if 'clear-bad-pattern' in k and k['clear-bad-pattern']:
                                        ent[name] = loop.data[idx][loop.tags.index(name)] = None
                                        clear_bad_pattern = True
                                        continue
                                    if excl_missing_data:
                                        missing_mandatory_data = True
                                        continue
                                    if skip_empty_value_error(loop, idx):
                                        continue
                                    raise ValueError(get_idx_msg(idx_tag_ids, tags, ent)
                                                     + f"{name} {val!r} must be {self.readableItemType[type]}.")

                            else:
                                if val in emptyValue:
                                    if 'default-from' in k and k['default-from'] == 'self':
                                        val = indexToLetter(letterToDigit(val, 1) - 1)
                                    elif 'default-from' in k and k['default-from'] in tags and row[tags.index(k['default-from'])] not in emptyValue:
                                        val = row[tags.index(k['default-from'])]
                                    elif 'default-from' in k and k['default-from'].startswith('Auth_asym_ID'):
                                        val = indexToLetter(letterToDigit(val, 1) - 1)
                                    elif 'default' in k:
                                        val = k['default']
                                    elif 'remove-bad-pattern' in k and k['remove-bad-pattern']:
                                        remove_bad_pattern = True
                                    elif excl_missing_data:
                                        missing_mandatory_data = True
                                        continue
                                    elif skip_empty_value_error(loop, idx):
                                        continue
                                    if 'uppercase' in k and k['uppercase']:
                                        val = val.upper()
                                    row[j] = ent[name] = val
                                if ('remove-bad-pattern' in k and k['remove-bad-pattern']) or ('clear-bad-pattern' in k and k['clear-bad-pattern']):
                                    if isinstance(val, str) and badPattern.match(val):
                                        if 'remove-bad-pattern' in k and k['remove-bad-pattern']:
                                            remove_bad_pattern = True
                                            continue
                                        if 'clear-bad-pattern' in k and k['clear-bad-pattern']:
                                            ent[name] = loop.data[idx][loop.tags.index(name)] = None
                                            clear_bad_pattern = True
                                            continue
                                if 'uppercase' in k and k['uppercase']:
                                    ent[name] = val.upper()
                                else:
                                    ent[name] = val if isinstance(val, str) else str(val)

                        else:
                            for d in data_items:
                                if d['name'] == name:
                                    type = d['type']
                                    if val in emptyValue and ('enum' in type or ('default-from' not in d and 'default' not in d)):
                                        if d['mandatory'] and excl_missing_data:
                                            missing_mandatory_data = True
                                            continue
                                        ent[name] = None
                                    elif type == 'bool':
                                        try:
                                            ent[name] = val.lower() in trueValue
                                        except ValueError:
                                            if 'remove-bad-pattern' in d and d['remove-bad-pattern']:
                                                if val in emptyValue:
                                                    ent[name] = None
                                                    continue
                                                remove_bad_pattern = True
                                                continue
                                            if 'clear-bad-pattern' in d and d['clear-bad-pattern']:
                                                if val in emptyValue:
                                                    ent[name] = None
                                                    continue
                                                ent[name] = loop.data[idx][loop.tags.index(name)] = None
                                                clear_bad_pattern = True
                                                continue
                                            if excl_missing_data:
                                                ent[name] = None
                                                continue
                                            if skip_empty_value_error(loop, idx):
                                                continue
                                            raise ValueError(get_idx_msg(idx_tag_ids, tags, ent)
                                                             + f"{name} {val!r} must be {self.readableItemType[type]}.")

                                    elif type == 'int':
                                        try:
                                            ent[name] = int(val)
                                        except (ValueError, TypeError):
                                            if 'default-from' in d and d['default-from'] == 'self':
                                                row[j] = ent[name] = letterToDigit(val)
                                            elif 'default-from' in d and d['default-from'] in tags:
                                                row[j] = ent[name] = letterToDigit(row[tags.index(d['default-from'])])
                                            elif 'default' in d:
                                                row[j] = ent[name] = int(d['default'])
                                            elif 'remove-bad-pattern' in d and d['remove-bad-pattern']:
                                                if val in emptyValue:
                                                    ent[name] = None
                                                    continue
                                                remove_bad_pattern = True
                                                continue
                                            elif 'clear-bad-pattern' in d and d['clear-bad-pattern']:
                                                if val in emptyValue:
                                                    ent[name] = None
                                                    continue
                                                ent[name] = loop.data[idx][loop.tags.index(name)] = None
                                                clear_bad_pattern = True
                                                continue
                                            elif excl_missing_data:
                                                ent[name] = None
                                                continue
                                            elif skip_empty_value_error(loop, idx):
                                                continue
                                            else:
                                                raise ValueError(get_idx_msg(idx_tag_ids, tags, ent)
                                                                 + f"{name} {val!r} must be {self.readableItemType[type]}.")

                                    elif type in ('index-int', 'positive-int', 'positive-int-as-str'):
                                        try:
                                            ent[name] = int(val)
                                        except (ValueError, TypeError):
                                            if 'default-from' in d and d['default-from'] == 'self':
                                                row[j] = ent[name] = letterToDigit(val, 1)
                                            elif 'default-from' in d and d['default-from'] in tags and row[tags.index(d['default-from'])] not in emptyValue:
                                                row[j] = ent[name] = letterToDigit(row[tags.index(d['default-from'])], 1)
                                                if ent[name] > 8 and not self.__remediation_mode and 'default' in d:
                                                    row[j] = ent[name] = int(d['default'])
                                            elif 'default-from' in d and d['default-from'].startswith('Auth_asym_ID'):
                                                row[j] = ent[name] = letterToDigit(val, 1)
                                            elif 'default' in d:
                                                row[j] = ent[name] = int(d['default'])
                                            elif 'remove-bad-pattern' in d and d['remove-bad-pattern']:
                                                if val in emptyValue:
                                                    ent[name] = None
                                                    continue
                                                remove_bad_pattern = True
                                                continue
                                            elif 'clear-bad-pattern' in d and d['clear-bad-pattern']:
                                                if val in emptyValue:
                                                    ent[name] = None
                                                    continue
                                                ent[name] = loop.data[idx][loop.tags.index(name)] = None
                                                clear_bad_pattern = True
                                                continue
                                            elif excl_missing_data:
                                                ent[name] = None
                                                continue
                                            elif skip_empty_value_error(loop, idx):
                                                continue
                                            else:
                                                raise ValueError(get_idx_msg(idx_tag_ids, tags, ent)
                                                                 + f"{name} {val!r} must be {self.readableItemType[type]}.")

                                        if (type == 'index-int' and ent[name] <= 0)\
                                           or (type == 'positive-int' and (ent[name] < 0 or (ent[name] == 0 and 'enforce-non-zero' in d and d['enforce-non-zero']))):
                                            raise ValueError(get_idx_msg(idx_tag_ids, tags, ent)
                                                             + f"{name} {val!r} must be {self.readableItemType[type]}.")
                                        if ent[name] == 0 and enforce_non_zero:
                                            if 'void-zero' in d:
                                                if self.replace_zero_by_null_in_case:
                                                    loop.data[idx][loop.tags.index(name)] = None
                                                ent[name] = None
                                            else:
                                                f.append(f"[Zero value error] {get_idx_msg(idx_tag_ids, tags, ent)}"
                                                         f"{name} {val!r} should not be zero, "
                                                         f"as defined by {self.readableItemType[type]}.")
                                        if type == 'positive-int-as-str':
                                            row[j] = ent[name] = str(ent[name])

                                    elif type == 'pointer-index':
                                        try:
                                            ent[name] = int(val)
                                        except (ValueError, TypeError):
                                            if 'default-from' in d and d['default-from'] == 'self':
                                                row[j] = ent[name] = letterToDigit(val, 1)
                                            elif 'default-from' in d and d['default-from'] in tags:
                                                row[j] = ent[name] = letterToDigit(row[tags.index(d['default-from'])], 1)
                                            elif 'default-from' in d and d['default-from'] == 'parent' and parent_pointer is not None:
                                                row[j] = ent[name] = parent_pointer
                                            elif 'default' in d:
                                                row[j] = ent[name] = int(d['default'])
                                            elif 'remove-bad-pattern' in d and d['remove-bad-pattern']:
                                                if val in emptyValue:
                                                    ent[name] = None
                                                    continue
                                                remove_bad_pattern = True
                                                continue
                                            elif 'clear-bad-pattern' in d and d['clear-bad-pattern']:
                                                if val in emptyValue:
                                                    ent[name] = None
                                                    continue
                                                ent[name] = loop.data[idx][loop.tags.index(name)] = None
                                                clear_bad_pattern = True
                                                continue
                                            elif excl_missing_data:
                                                ent[name] = None
                                                continue
                                            elif skip_empty_value_error(loop, idx):
                                                continue
                                            else:
                                                raise ValueError(get_idx_msg(idx_tag_ids, tags, ent)
                                                                 + f"{name} {val!r} must be {self.readableItemType[type]}.")

                                        if ent[name] <= 0:
                                            raise ValueError(get_idx_msg(idx_tag_ids, tags, ent)
                                                             + f"{name} {val!r} must be {self.readableItemType[type]}.")
                                        if static_val[name] is None:
                                            static_val[name] = val
                                        elif val != static_val[name] and _test_on_index:
                                            raise ValueError(get_idx_msg(idx_tag_ids, tags, ent)
                                                             + f"{name} {val} vs {static_val[name]} must be {self.readableItemType[type]}.")

                                    elif type == 'float':
                                        try:
                                            ent[name] = float(val)
                                        except (ValueError, TypeError):
                                            if 'remove-bad-pattern' in d and d['remove-bad-pattern']:
                                                if val in emptyValue:
                                                    ent[name] = None
                                                    continue
                                                remove_bad_pattern = True
                                                continue
                                            if 'clear-bad-pattern' in d and d['clear-bad-pattern']:
                                                if val in emptyValue:
                                                    ent[name] = None
                                                    continue
                                                ent[name] = loop.data[idx][loop.tags.index(name)] = None
                                                clear_bad_pattern = True
                                                continue
                                            if excl_missing_data:
                                                ent[name] = None
                                                continue
                                            if skip_empty_value_error(loop, idx):
                                                continue
                                            raise ValueError(get_idx_msg(idx_tag_ids, tags, ent)
                                                             + f"{name} {val!r} must be {self.readableItemType[type]}.")

                                    elif type == 'positive-float':
                                        try:
                                            ent[name] = float(val)
                                        except (ValueError, TypeError):
                                            if 'remove-bad-pattern' in d and d['remove-bad-pattern']:
                                                if val in emptyValue:
                                                    ent[name] = None
                                                    continue
                                                remove_bad_pattern = True
                                                continue
                                            if 'clear-bad-pattern' in d and d['clear-bad-pattern']:
                                                if val in emptyValue:
                                                    ent[name] = None
                                                    continue
                                                ent[name] = loop.data[idx][loop.tags.index(name)] = None
                                                clear_bad_pattern = True
                                                continue
                                            if excl_missing_data:
                                                ent[name] = None
                                                continue
                                            if skip_empty_value_error(loop, idx):
                                                continue
                                            raise ValueError(get_idx_msg(idx_tag_ids, tags, ent)
                                                             + f"{name} {val!r} must be {self.readableItemType[type]}.")
                                        if ent[name] < 0.0 or (ent[name] == 0.0 and 'enforce-non-zero' in d and d['enforce-non-zero']):
                                            raise ValueError(get_idx_msg(idx_tag_ids, tags, ent)
                                                             + f"{name} {val!r} must be {self.readableItemType[type]}.")
                                        if ent[name] == 0.0 and enforce_non_zero:
                                            if 'void-zero' in d:
                                                if self.replace_zero_by_null_in_case:
                                                    loop.data[idx][loop.tags.index(name)] = None
                                                ent[name] = None
                                            else:
                                                f.append(f"[Zero value error] {get_idx_msg(idx_tag_ids, tags, ent)}"
                                                         f"{name} {val!r} should not be zero, "
                                                         f"as defined by {self.readableItemType[type]}.")

                                    elif type == 'range-float':
                                        try:
                                            _range = d['range']
                                            ent[name] = float(val)
                                        except KeyError:
                                            raise ValueError(f"Range of data item {name} is not defined")
                                        except (ValueError, TypeError):
                                            if 'remove-bad-pattern' in d and d['remove-bad-pattern']:
                                                if val in emptyValue:
                                                    ent[name] = None
                                                    continue
                                                remove_bad_pattern = True
                                                continue
                                            if 'clear-bad-pattern' in d and d['clear-bad-pattern']:
                                                if val in emptyValue:
                                                    ent[name] = None
                                                    continue
                                                ent[name] = loop.data[idx][loop.tags.index(name)] = None
                                                clear_bad_pattern = True
                                                continue
                                            if excl_missing_data:
                                                ent[name] = None
                                                continue
                                            if not enforce_range:
                                                ent[name] = None
                                                continue
                                            if skip_empty_value_error(loop, idx):
                                                continue
                                            f.append(f"[Range value error] {get_idx_msg(idx_tag_ids, tags, ent)}"
                                                     f"{name} {val!r} must be {self.readableItemType[type]}.")
                                            continue

                                        if ('min_exclusive' in _range and _range['min_exclusive'] == 0.0 and ent[name] <= 0.0)\
                                           or ('min_inclusive' in _range and _range['min_inclusive'] == 0.0 and ent[name] < 0):
                                            if ent[name] < 0.0:
                                                if ('max_inclusive' in _range and abs(ent[name]) > _range['max_inclusive'])\
                                                   or ('max_exclusive' in _range and abs(ent[name]) >= _range['max_exclusive'])\
                                                   or ('enforce-sign' in d and d['enforce-sign']):
                                                    if not enforce_range:
                                                        ent[name] = None
                                                    else:
                                                        f.append(f"[Range value error] {get_idx_msg(idx_tag_ids, tags, ent)}"
                                                                 f"{name} {val!r} must be within range {_range}.")
                                                elif enforce_sign:
                                                    f.append(f"[Negative value error] {get_idx_msg(idx_tag_ids, tags, ent)}"
                                                             f"{name} {val!r} should not have "
                                                             f"negative value for {self.readableItemType[type]}, {_range}.")
                                            elif ent[name] == 0.0 and 'enforce-non-zero' in d and d['enforce-non-zero']:
                                                if not enforce_range:
                                                    ent[name] = None
                                                else:
                                                    f.append(f"[Range value error] {get_idx_msg(idx_tag_ids, tags, ent)}"
                                                             f"{name} {val!r} must be within range {_range}.")
                                            elif ent[name] == 0.0 and enforce_non_zero:
                                                if 'void-zero' in d:
                                                    if self.replace_zero_by_null_in_case:
                                                        loop.data[idx][loop.tags.index(name)] = None
                                                    ent[name] = None
                                                else:
                                                    f.append(f"[Zero value error] {get_idx_msg(idx_tag_ids, tags, ent)}"
                                                             f"{name} {val!r} should not be zero, "
                                                             f"as defined by {self.readableItemType[type]}, {_range}.")
                                            elif 'remove-bad-pattern' in d and d['remove-bad-pattern']:
                                                if val in emptyValue:
                                                    ent[name] = None
                                                    continue
                                                remove_bad_pattern = True
                                                continue
                                            elif 'clear-bad-pattern' in d and d['clear-bad-pattern']:
                                                if val in emptyValue:
                                                    ent[name] = None
                                                    continue
                                                ent[name] = loop.data[idx][loop.tags.index(name)] = None
                                                clear_bad_pattern = True
                                                continue
                                            elif skip_empty_value_error(loop, idx):
                                                continue
                                        elif ('min_exclusive' in _range and ent[name] <= _range['min_exclusive']) or\
                                             ('min_inclusive' in _range and ent[name] < _range['min_inclusive']) or\
                                             ('max_inclusive' in _range and ent[name] > _range['max_inclusive']) or\
                                             ('max_exclusive' in _range and ent[name] >= _range['max_exclusive']):
                                            if 'void-zero' in d and ent[name] == 0.0:
                                                if self.replace_zero_by_null_in_case:
                                                    loop.data[idx][loop.tags.index(name)] = None
                                                ent[name] = None
                                            elif not enforce_range:
                                                ent[name] = None
                                            elif 'remove-bad-pattern' in d and d['remove-bad-pattern']:
                                                if val in emptyValue:
                                                    ent[name] = None
                                                    continue
                                                remove_bad_pattern = True
                                                continue
                                            elif 'clear-bad-pattern' in d and d['clear-bad-pattern']:
                                                if val in emptyValue:
                                                    ent[name] = None
                                                    continue
                                                ent[name] = loop.data[idx][loop.tags.index(name)] = None
                                                clear_bad_pattern = True
                                                continue
                                            elif skip_empty_value_error(loop, idx):
                                                continue
                                            else:
                                                f.append(f"[Range value error] {get_idx_msg(idx_tag_ids, tags, ent)}"
                                                         f"{name} {val!r} must be within range {_range}.")

                                    elif type == 'enum':
                                        try:
                                            enum = d['enum']
                                            if val not in enum:
                                                if 'default' in d:
                                                    val = d['default']
                                                    row[j] = val
                                                elif 'default-from' in d and d['default-from'] in tags:
                                                    if row[tags.index(d['default-from'])][0].upper() in enum:
                                                        val = row[tags.index(d['default-from'])][0].upper()
                                                elif 'enum-alt' in d and val in d['enum-alt']:
                                                    val = d['enum-alt'][val]
                                                    row[j] = val
                                                elif 'enforce-enum' in d and d['enforce-enum']:
                                                    if excl_missing_data:
                                                        ent[name] = None
                                                        continue
                                                    raise ValueError(get_idx_msg(idx_tag_ids, tags, ent)
                                                                     + f"{name} {val!r} must be one of {enum}.")
                                                elif enforce_enum and name in mand_data_names:
                                                    f.append(f"[Enumeration error] {get_idx_msg(idx_tag_ids, tags, ent)}"
                                                             f"{name} {val!r} should be one of {enum}.")
                                                elif 'remove-bad-pattern' in d and d['remove-bad-pattern']:
                                                    if val in emptyValue:
                                                        ent[name] = None
                                                        continue
                                                    remove_bad_pattern = True
                                                    continue
                                                elif 'clear-bad-pattern' in d and d['clear-bad-pattern']:
                                                    if val in emptyValue:
                                                        ent[name] = None
                                                        continue
                                                    ent[name] = loop.data[idx][loop.tags.index(name)] = None
                                                    clear_bad_pattern = True
                                                    continue
                                                elif skip_empty_value_error(loop, idx):
                                                    continue
                                            ent[name] = val
                                        except KeyError:
                                            raise ValueError(f"Enumeration of data item {name} is not defined")

                                    elif type == 'enum-int':
                                        try:
                                            enum = d['enum']
                                            if int(val) not in enum:
                                                if 'default' in d:
                                                    val = str(d['default'])
                                                if 'default-from' in d and d['default-from'] in tags:
                                                    if row[tags.index(d['default-from'])][0].upper() in ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS:
                                                        val = ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS[row[tags.index(d['default-from'])][0].upper()][0]
                                                if 'enforce-enum' in d and d['enforce-enum']:
                                                    raise ValueError(get_idx_msg(idx_tag_ids, tags, ent)
                                                                     + f"{name} {val!r} must be one of {enum}.")
                                                if 'remove-bad-pattern' in d and d['remove-bad-pattern']:
                                                    if val in emptyValue:
                                                        ent[name] = None
                                                        continue
                                                    remove_bad_pattern = True
                                                    continue
                                                if 'clear-bad-pattern' in d and d['clear-bad-pattern']:
                                                    if val in emptyValue:
                                                        ent[name] = None
                                                        continue
                                                    ent[name] = loop.data[idx][loop.tags.index(name)] = None
                                                    clear_bad_pattern = True
                                                    continue
                                                if enforce_enum:
                                                    f.append(f"[Enumeration error] {get_idx_msg(idx_tag_ids, tags, ent)}"
                                                             f"{name} {val!r} should be one of {enum}.")
                                                    continue
                                                if skip_empty_value_error(loop, idx):
                                                    continue
                                            ent[name] = int(val)
                                        except KeyError:
                                            raise ValueError(f"Enumeration of data item {name} is not defined")
                                        except (ValueError, TypeError):
                                            if excl_missing_data:
                                                ent[name] = None
                                                continue
                                            raise ValueError(get_idx_msg(idx_tag_ids, tags, ent)
                                                             + f"{name} {val!r} must be {self.readableItemType[type]}.")

                                    else:
                                        if val in emptyValue:
                                            if 'default-from' in d and d['default-from'] == 'self':
                                                val = indexToLetter(letterToDigit(val, 1) - 1)
                                            elif 'default-from' in d and d['default-from'] in tags and row[tags.index(d['default-from'])] not in emptyValue:
                                                val = row[tags.index(d['default-from'])]
                                            elif 'default-from' in d and d['default-from'].startswith('Auth_asym_ID'):
                                                val = indexToLetter(letterToDigit(val, 1) - 1)
                                            elif 'default' in d:
                                                val = d['default']
                                            elif 'remove-bad-pattern' in d and d['remove-bad-pattern']:
                                                remove_bad_pattern = True
                                            elif excl_missing_data:
                                                missing_mandatory_data = True
                                                continue
                                            elif skip_empty_value_error(loop, idx):
                                                continue
                                            if 'uppercase' in d and d['uppercase']:
                                                val = val.upper()
                                            row[j] = ent[name] = val
                                        if ('remove-bad-pattern' in d and d['remove-bad-pattern']) or ('clear-bad-pattern' in d and d['clear-bad-pattern']):
                                            if isinstance(val, str) and badPattern.match(val):
                                                if 'remove-bad-pattern' in d and d['remove-bad-pattern']:
                                                    if val in emptyValue:
                                                        ent[name] = None
                                                        continue
                                                    remove_bad_pattern = True
                                                    continue
                                                if 'clear-bad-pattern' in d and d['clear-bad-pattern']:
                                                    if val in emptyValue:
                                                        ent[name] = None
                                                        continue
                                                    ent[name] = loop.data[idx][loop.tags.index(name)] = None
                                                    clear_bad_pattern = True
                                                    continue
                                        if 'uppercase' in d and d['uppercase']:
                                            ent[name] = val.upper()
                                        else:
                                            ent[name] = val if isinstance(val, str) else str(val)

                    for d in data_items:
                        if 'group-mandatory' in d and d['group-mandatory']:
                            name = d['name']
                            group = d['group']
                            if name in ent and ent[name] is not None:
                                if group['coexist-with'] is not None:
                                    for cw in group['coexist-with']:
                                        if cw not in ent or ent[cw] is None:
                                            raise ValueError(get_idx_msg(idx_tag_ids, tags, ent)
                                                             + f"One of data item {cw} must not be empty for a row having {name} {ent[name]!r}.")

                                if 'smaller-than' in group and group['smaller-than'] is not None:
                                    for st in group['smaller-than']:
                                        if st in ent and ent[st] is not None:
                                            if ent[name] < ent[st]:
                                                if 'circular-shift' in group:
                                                    ent[st] -= abs(group['circular-shift'])
                                                if ent[name] < ent[st]:
                                                    raise ValueError(get_idx_msg(idx_tag_ids, tags, ent)
                                                                     + f"Data item {name} {ent[name]!r} must be larger than {st} {ent[st]!r}.")

                                if 'larger-than' in group and group['larger-than'] is not None:
                                    for lt in group['larger-than']:
                                        if lt in ent and ent[lt] is not None:
                                            if ent[name] > ent[lt]:
                                                if 'circular-shift' in group:
                                                    ent[lt] += abs(group['circular-shift'])
                                                if ent[name] > ent[lt]:
                                                    raise ValueError(get_idx_msg(idx_tag_ids, tags, ent)
                                                                     + f"Data item {name} {ent[name]!r} must be smaller than {lt} {ent[lt]!r}.")

                                if 'not-equal-to' in group and group['not-equal-to'] is not None:
                                    for ne in group['not-equal-to']:
                                        if ne in ent and ent[ne] is not None:
                                            if ent[name] == ent[ne]:
                                                raise ValueError(get_idx_msg(idx_tag_ids, tags, ent)
                                                                 + f"Data item {name} {ent[name]!r} must not be equal to {ne} {ent[ne]!r}.")

                            elif group['member-with'] is not None:
                                has_member = not d['mandatory']
                                for mw in group['member-with']:
                                    if mw in ent and ent[mw] is not None:
                                        has_member = True
                                        break
                                if not has_member:
                                    member = set(group['member-with'])
                                    member.add(name)
                                    raise ValueError(get_idx_msg(idx_tag_ids, tags, ent)
                                                     + f"One of data items {member} must not be empty.")

                    if missing_mandatory_data:
                        continue

                    if remove_bad_pattern:
                        r = {}
                        for j, t in enumerate(loop.tags):
                            r[t] = loop.data[idx][j]
                        f.append(f"[Remove bad pattern] Found bad pattern. "
                                 f"#_of_row {idx + 1}, data_of_row {r}.")
                        continue  # should be removed from loop later

                    if clear_bad_pattern:
                        r = {}
                        for j, t in enumerate(loop.tags):
                            r[t] = loop.data[idx][j]
                        f.append(f"[Clear bad pattern] Found bad pattern. "
                                 f"#_of_row {idx + 1}, data_of_row {r}.")

                    asm.append(ent)

                data.append(asm)

            if len(f) > 0:
                raise UserWarning('\n'.join(sorted(list(set(f)), key=f.index)))

            if len(data) == 0:
                data.append([])

            return data

    def get_conflict_id(self, star_data: Union[pynmrstar.Entry, pynmrstar.Saveframe, pynmrstar.Loop],  # pylint: disable=no-self-use
                        lp_category: str, key_items: List[dict]) -> List[List[int]]:
        """ Return list of conflicted row IDs except for rows of the first occurrence.
            @author: Masashi Yokochi
            @return: list of row IDs in reverse order for each loop
        """

        if isinstance(star_data, pynmrstar.Entry):
            loops = star_data.get_loops_by_category(lp_category)
        elif isinstance(star_data, pynmrstar.Saveframe):
            loops = [star_data.get_loop(lp_category)]
        else:
            loops = [star_data]

        is_nef_dist_lp = 'nef_distance_restraint' in lp_category
        is_nef_dihed_lp = 'nef_dihedral_restraint' in lp_category
        is_star_dist_lp = 'Gen_dist_constraint' in lp_category
        is_star_dihed_lp = 'Torsion_angle_constraint' in lp_category
        is_target_lp = is_nef_dist_lp or is_nef_dihed_lp or is_star_dist_lp or is_star_dihed_lp

        data = []  # data of all loops

        with io.StringIO() as key_f:

            for loop in loops:

                if is_target_lp:
                    if (is_nef_dist_lp or is_nef_dihed_lp) and 'restraint_combination_id' in loop.tags:
                        key_items = copy.deepcopy(key_items)
                        key_items.insert(0, {'name': 'restraint_combination_id', 'type': 'positive-int', 'mandatory': False,
                                             'enforce-non-zero': True})
                    elif (is_star_dist_lp or is_star_dihed_lp) and 'Combination_ID' in loop.tags:
                        key_items = copy.deepcopy(key_items)
                        key_items.insert(0, {'name': 'Combination_ID', 'type': 'positive-int', 'mandatory': False,
                                             'enforce-non-zero': True})

                key_names = [k['name'] for k in key_items]
                uppercases = [('uppercase' in k and k['uppercase']) for k in key_items]

                key_len = len(key_items)

                if len(key_names) > 0 and set(key_names) & set(loop.tags) != set(key_names):
                    missing_tags = list(set(key_names) - set(loop.tags))
                    for k in key_items:
                        if k['name'] in missing_tags:
                            if 'default' in k:
                                for row in loop:
                                    row.append(k['default'])
                                loop.add_tag(k['name'])
                            else:
                                raise LookupError(f"Missing mandatory {missing_tags} loop tag(s).")

                len_loop = len(loop)

                keys = set()
                dup_ids = set()

                for idx, row in enumerate(loop.get_tag(key_names)):

                    if key_f.tell() > 0:
                        key_f.truncate(0)
                        key_f.seek(0)

                    for j in range(key_len):
                        key_f.write(f'{row[j].upper() if row[j] is not None and uppercases[j] else row[j]} ')

                    key = key_f.getvalue()

                    if key in keys and idx < len_loop:
                        dup_ids.add(idx)

                    else:
                        keys.add(key)

                data.append(sorted(dup_ids, reverse=True))

            return data

    def get_conflict_id_set(self, star_data: Union[pynmrstar.Entry, pynmrstar.Saveframe, pynmrstar.Loop],  # pylint: disable=no-self-use
                            lp_category: str, key_items: List[dict]) -> List[List[int]]:
        """ Return list of conflicted row ID sets.
            @author: Masashi Yokochi
            @return: list of row ID sets for each loop
        """

        if isinstance(star_data, pynmrstar.Entry):
            loops = star_data.get_loops_by_category(lp_category)
        elif isinstance(star_data, pynmrstar.Saveframe):
            loops = [star_data.get_loop(lp_category)]
        else:
            loops = [star_data]

        is_nef_dist_lp = 'nef_distance_restraint' in lp_category
        is_nef_dihed_lp = 'nef_dihedral_restraint' in lp_category
        is_star_dist_lp = 'Gen_dist_constraint' in lp_category
        is_star_dihed_lp = 'Torsion_angle_constraint' in lp_category
        is_target_lp = is_nef_dist_lp or is_nef_dihed_lp or is_star_dist_lp or is_star_dihed_lp

        data = []  # data of all loops

        with io.StringIO() as key_f:

            for loop in loops:

                if is_target_lp:
                    if (is_nef_dist_lp or is_nef_dihed_lp) and 'restraint_combination_id' in loop.tags:
                        key_items = copy.deepcopy(key_items)
                        key_items.insert(0, {'name': 'restraint_combination_id', 'type': 'positive-int', 'mandatory': False,
                                             'enforce-non-zero': True})
                    elif (is_star_dist_lp or is_star_dihed_lp) and 'Combination_ID' in loop.tags:
                        key_items = copy.deepcopy(key_items)
                        key_items.insert(0, {'name': 'Combination_ID', 'type': 'positive-int', 'mandatory': False,
                                             'enforce-non-zero': True})

                key_names = [k['name'] for k in key_items]
                uppercases = [('uppercase' in k and k['uppercase']) for k in key_items]

                key_len = len(key_items)

                if len(key_names) > 0 and set(key_names) & set(loop.tags) != set(key_names):
                    missing_tags = list(set(key_names) - set(loop.tags))
                    raise LookupError(f"Missing mandatory {missing_tags} loop tag(s).")

                len_loop = len(loop)

                tag_data = loop.get_tag(key_names)

                keys = set()
                dup_ids = set()

                for idx, row in enumerate(tag_data):

                    if key_f.tell() > 0:
                        key_f.truncate(0)
                        key_f.seek(0)

                    for j in range(key_len):
                        key_f.write(f'{row[j].upper() if row[j] is not None and uppercases[j] else row[j]} ')

                    key = key_f.getvalue()

                    if key in keys and idx < len_loop:
                        dup_ids.add(idx)

                    else:
                        keys.add(key)

                conflict_id = sorted(dup_ids, reverse=True)

                if len(conflict_id) == 0:
                    data.append(None)

                else:
                    conflict_id_set = []

                    for idx in conflict_id:

                        if key_f.tell() > 0:
                            key_f.truncate(0)
                            key_f.seek(0)

                        for j in range(key_len):
                            key_f.write(f'{tag_data[idx][j]} ')

                        key = key_f.getvalue()

                        id_set = [idx]

                        for m in range(idx):

                            if key_f.tell() > 0:
                                key_f.truncate(0)
                                key_f.seek(0)

                            for j in range(key_len):
                                key_f.write(f'{tag_data[m][j]} ')

                            _key = key_f.getvalue()

                            if key == _key and m < len_loop:
                                id_set.append(m)

                                if m in conflict_id:
                                    conflict_id.remove(m)

                        if len(id_set) > 1:
                            conflict_id_set.insert(0, sorted(id_set))

                    data.append(conflict_id_set)

            return data

    def get_conflict_atom_id(self, star_data: Union[pynmrstar.Entry, pynmrstar.Saveframe, pynmrstar.Loop],
                             file_type: str, lp_category: str, key_items: List[dict]) -> List[List[int]]:
        """ Return list of row IDs that include self atoms.
            @author: Masashi Yokochi
            @return: list of row IDs in reverse order for each loop
        """

        if isinstance(star_data, pynmrstar.Entry):
            loops = star_data.get_loops_by_category(lp_category)
        elif isinstance(star_data, pynmrstar.Saveframe):
            loops = [star_data.get_loop(lp_category)]
        else:
            loops = [star_data]

        is_nef_dist_lp = 'nef_distance_restraint' in lp_category
        is_nef_dihed_lp = 'nef_dihedral_restraint' in lp_category
        is_star_dist_lp = 'Gen_dist_constraint' in lp_category
        is_star_dihed_lp = 'Torsion_angle_constraint' in lp_category
        is_target_lp = is_nef_dist_lp or is_nef_dihed_lp or is_star_dist_lp or is_star_dihed_lp

        def skip_empty_value_error(lp, idx):
            if not is_target_lp:
                return False
            if is_nef_dist_lp and 'residue_name_1' in lp.tags and 'residue_name_2' in lp.tags\
               and (lp.data[idx][lp.tags.index('residue_name_1')] == 'HOH'
                    or lp.data[idx][lp.tags.index('residue_name_2')] == 'HOH'):
                return True
            if is_nef_dihed_lp and 'name' in lp.tags and lp.data[idx][lp.tags.index('name')] == 'PPA':
                return True
            if is_star_dist_lp and 'Auth_comp_ID_1' in lp.tags and 'Auth_comp_ID_2' in lp.tags\
               and (lp.data[idx][lp.tags.index('Auth_comp_ID_1')] == 'HOH'
                    or lp.data[idx][lp.tags.index('Auth_comp_ID_2')] == 'HOH'):
                return True
            if is_star_dihed_lp and 'Torsion_angle_name' in lp.tags and lp.data[idx][lp.tags.index('Torsion_angle_name')] == 'PPA':
                return True
            return False

        data = []  # data of all loops

        key_names = [k['name'] for k in key_items]

        for loop in loops:

            if len(key_names) > 0 and set(key_names) & set(loop.tags) != set(key_names):
                missing_tags = list(set(key_names) - set(loop.tags))
                for k in key_items:
                    if k['name'] in missing_tags:
                        if 'default' in k:
                            for row in loop:
                                row.append(k['default'])
                            loop.add_tag(k['name'])
                        else:
                            raise LookupError(f"Missing mandatory {missing_tags} loop tag(s).")

            len_loop = len(loop)

            atom_keys = self.get_atom_keys(loop.get_tag_names(), file_type)

            len_atom_keys = len(atom_keys)

            dup_ids = set()

            for idx, row in enumerate(loop.get_tag(key_names)):

                for j in range(0, len_atom_keys - 2):
                    atom_key_j = atom_keys[j]
                    chain_id_j = row[key_names.index(atom_key_j['chain_tag'])]
                    seq_id_j = row[key_names.index(atom_key_j['seq_tag'])]
                    atom_id_j = row[key_names.index(atom_key_j['atom_tag'])]

                    for k in range(j + 1, len_atom_keys - 1):
                        atom_key_k = atom_keys[k]
                        chain_id_k = row[key_names.index(atom_key_k['chain_tag'])]
                        seq_id_k = row[key_names.index(atom_key_k['seq_tag'])]
                        atom_id_k = row[key_names.index(atom_key_k['atom_tag'])]

                        if chain_id_j == chain_id_k and seq_id_j == seq_id_k and atom_id_j == atom_id_k and idx < len_loop\
                           and not skip_empty_value_error(loop, idx):
                            dup_ids.add(idx)
                            break

            data.append(sorted(dup_ids, reverse=True))

        return data

    def get_bad_pattern_id(self, star_data: Union[pynmrstar.Entry, pynmrstar.Saveframe, pynmrstar.Loop],  # pylint: disable=no-self-use
                           lp_category: str, key_items: List[dict], data_items: List[dict]) -> List[List[int]]:
        """ Return list of row IDs with bad patterns
            @author: Masashi Yokochi
            @return: list of row IDs in reverse order for each loop
        """

        if isinstance(star_data, pynmrstar.Entry):
            loops = star_data.get_loops_by_category(lp_category)
        elif isinstance(star_data, pynmrstar.Saveframe):
            loops = [star_data.get_loop(lp_category)]
        else:
            loops = [star_data]

        data = []  # data of all loops

        key_names = [k['name'] for k in key_items if 'remove-bad-pattern' in k and k['remove-bad-pattern']]
        data_names = [d['name'] for d in data_items if 'remove-bad-pattern' in d and d['remove-bad-pattern']]

        key_names.extend(data_names)

        key_types = [k['type'] for k in key_items if 'remove-bad-pattern' in k and k['remove-bad-pattern']]
        data_types = [d['type'] for d in data_items if 'remove-bad-pattern' in d and d['remove-bad-pattern']]

        key_types.extend(data_types)

        for loop in loops:

            len_loop = len(loop)

            bad_ids = set()

            for idx, row in enumerate(loop.get_tag(key_names)):

                if any(isinstance(dat, str) and badPattern.match(dat) for dat in row):
                    if idx < len_loop:
                        bad_ids.add(idx)
                else:
                    for col, dat in enumerate(row):
                        dat_type = key_types[col]
                        if dat_type == 'bool':
                            try:
                                bool(dat)
                            except ValueError:
                                if idx < len_loop:
                                    bad_ids.add(idx)
                        elif 'int' in dat_type or dat_type == 'pointer-index':
                            try:
                                int(dat)
                            except ValueError:
                                if idx < len_loop:
                                    bad_ids.add(idx)
                        elif 'float' in dat_type:
                            try:
                                float(dat)
                            except ValueError:
                                if idx < len_loop:
                                    bad_ids.add(idx)

            data.append(sorted(bad_ids, reverse=True))

        return data

    def check_sf_tag(self, star_data: pynmrstar.Saveframe, file_type: str, category: str, tag_items: List[dict], allowed_tags: List[str] = None,
                     enforce_non_zero: bool = False, enforce_sign: bool = False, enforce_range: bool = False, enforce_enum: bool = False) -> dict:
        """ Extract saveframe tags with sanity check.
            @author: Masashi Yokochi
            @return: list of extracted saveframe tags
        """

        item_types = ('str', 'bool', 'int', 'positive-int', 'positive-int-as-str',
                      'float', 'positive-float', 'range-float', 'enum', 'enum-int')

        tag_names = [t['name'] for t in tag_items]
        mand_tag_names = [t['name'] for t in tag_items if t['mandatory']]

        for t in tag_items:
            if t['type'] not in item_types:
                raise TypeError(f"Type {t['type']} of tag item {t['name']} must be one of {item_types}.")

        if allowed_tags is not None:

            if (set(tag_names) | set(allowed_tags)) != set(allowed_tags):
                raise LookupError(f"Saveframe tags {((set(tag_names) | set(allowed_tags)) - set(allowed_tags))} must not exists.")

            for t in tag_items:
                if 'group-mandatory' in t and t['group-mandatory']:
                    group = t['group']
                    if group['member-with'] is not None:
                        for mw in group['member-with']:
                            if mw not in allowed_tags:
                                raise ValueError(f"Member tag item {mw} of {t['name']} must exists in allowed tags.")
                    if group['coexist-with'] is not None:
                        for cw in group['coexist-with']:
                            if cw not in allowed_tags:
                                raise ValueError(f"Coexisting tag item {cw} of {t['name']} must exists in allowed tags.")

        sf_tags = {row[0]: row[1] for row in star_data.tags}

        if len(mand_tag_names) > 0 and set(mand_tag_names) & set(sf_tags.keys()) != set(mand_tag_names):
            missing_tags = list(set(mand_tag_names) - set(sf_tags.keys()))
            raise LookupError(f"Missing mandatory {missing_tags} saveframe tag(s).")

        for t in tag_items:
            if 'group-mandatory' in t and t['group-mandatory']:
                name = t['name']
                group = t['group']
                if name in sf_tags.keys():
                    if group['coexist-with'] is not None:
                        for cw in group['coexist-with']:
                            if cw not in sf_tags.keys():
                                set_cw = set(group['coexist-with'])
                                set_cw.add(name)
                                missing_tags = list(set_cw - set(sf_tags.keys()))
                                raise LookupError(f"Missing mandatory {missing_tags} saveframe tag(s).")

                elif group['member-with'] is not None:
                    has_member = False
                    for mw in group['member-with']:
                        if mw in sf_tags.keys():
                            has_member = True
                            break
                    if not has_member:
                        set_mw = set(group['member-with'])
                        set_mw.add(name)
                        missing_tags = list(set_mw - set(sf_tags.keys()))
                        raise LookupError(f"Missing mandatory {missing_tags} saveframe tag(s).")

        for name, val in sf_tags.items():
            if val in emptyValue:
                for t in tag_items:
                    if t['name'] == name and t['mandatory'] and 'default' not in t:
                        raise ValueError(f"{name} must not be empty.")

        f = []  # user warnings

        ent = {}  # entity

        for name, val in sf_tags.items():
            for t in tag_items:
                if t['name'] == name:
                    type = t['type']  # pylint: disable=redefined-builtin
                    if val in emptyValue and 'enum' not in type and 'default-from' not in t and 'default' not in t:
                        ent[name] = None
                    elif type == 'bool':
                        try:
                            ent[name] = val.lower() in trueValue
                        except ValueError:
                            raise ValueError(f"{name} {val!r} must be {self.readableItemType[type]}.")

                    elif type == 'int':
                        try:
                            ent[name] = int(val)
                        except (ValueError, TypeError):
                            if 'default-from' in t and t['default-from'] == 'self':
                                ent[name] = letterToDigit(val)
                            elif 'default-from' in t and t['default-from'] in sf_tags.keys():
                                ent[name] = letterToDigit(sf_tags[t['default-from']])
                            elif 'default' in t:
                                ent[name] = int(t['default'])
                            else:
                                raise ValueError(f"{name} {val!r} must be {self.readableItemType[type]}.")

                    elif type in ('positive-int', 'positive-int-as-str'):
                        try:
                            ent[name] = int(val)
                        except (ValueError, TypeError):
                            if 'default-from' in t and t['default-from'] == 'self':
                                ent[name] = letterToDigit(val, 1)
                            elif 'default-from' in t and t['default-from'] in sf_tags.keys() and sf_tags[t['default-from']] not in emptyValue:
                                ent[name] = letterToDigit(sf_tags[t['default-from']], 1)
                                if ent[name] > 8 and not self.__remediation_mode and 'default' in t:
                                    ent[name] = int(t['default'])
                            elif 'default-from' in t and t['default-from'].startswith('Auth_asym_ID'):
                                ent[name] = letterToDigit(val, 1)
                            elif 'default' in t:
                                ent[name] = int(t['default'])
                            else:
                                raise ValueError(f"{name} {val!r} must be {self.readableItemType[type]}.")
                        if ent[name] < 0 or (ent[name] == 0 and 'enforce-non-zero' in t and t['enforce-non-zero']):
                            raise ValueError(f"{name} {val!r} must be {self.readableItemType[type]}.")
                        if ent[name] == 0 and enforce_non_zero:
                            if 'void-zero' in t:
                                if self.replace_zero_by_null_in_case:
                                    star_data.tags[sf_tags.keys().index(name)][1] = None
                                ent[name] = None
                            else:
                                f.append(f"[Zero value error] {name} {val!r} should not be zero, "
                                         f"as defined by {self.readableItemType[type]}.")
                        if type == 'positive-int-as-str':
                            ent[name] = str(ent[name])

                    elif type == 'float':
                        try:
                            ent[name] = float(val)
                        except (ValueError, TypeError):
                            raise ValueError(f"{name} {val!r} must be {self.readableItemType[type]}.")

                    elif type == 'positive-float':
                        try:
                            ent[name] = float(val)
                        except (ValueError, TypeError):
                            raise ValueError(f"{name} {val!r} must be {self.readableItemType[type]}.")
                        if ent[name] < 0.0 or (ent[name] == 0.0 and 'enforce-non-zero' in t and t['enforce-non-zero']):
                            raise ValueError(f"{name} {val!r} must be {self.readableItemType[type]}.")
                        if ent[name] == 0.0 and enforce_non_zero:
                            if 'void-zero' in t:
                                if self.replace_zero_by_null_in_case:
                                    star_data.tags[sf_tags.keys().index(name)][1] = None
                                ent[name] = None
                            else:
                                f.append(f"[Zero value error] {name} {val!r} should not be zero, "
                                         f"as defined by {self.readableItemType[type]}.")

                    elif type == 'range-float':
                        try:
                            _range = t['range']
                            ent[name] = float(val)
                        except KeyError:
                            raise ValueError(f"Range of tag item {name} is not defined.")
                        except (ValueError, TypeError):
                            if not enforce_range:
                                ent[name] = None
                                continue
                            f.append(f"[Range value error] {name} {val!r} must be {self.readableItemType[type]}.")
                        if ('min_exclusive' in _range and _range['min_exclusive'] == 0.0 and ent[name] <= 0.0)\
                           or ('min_inclusive' in _range and _range['min_inclusive'] == 0.0 and ent[name] < 0):
                            if ent[name] < 0.0:
                                if ('max_inclusive' in _range and abs(ent[name]) > _range['max_inclusive'])\
                                   or ('max_exclusive' in _range and abs(ent[name]) >= _range['max_exclusive'])\
                                   or ('enforce-sign' in t and t['enforce-sign']):
                                    if not enforce_range:
                                        ent[name] = None
                                    else:
                                        f.append(f"[Range value error] {name} {val!r} must be within range {_range}.")
                                elif enforce_sign:
                                    f.append(f"[Negative value error] {name} {val!r} should not have "
                                             f"negative value for {self.readableItemType[type]}, {_range}.")
                            elif ent[name] == 0.0 and 'enforce-non-zero' in t and t['enforce-non-zero']:
                                if not enforce_range:
                                    ent[name] = None
                                else:
                                    f.append(f"[Range value error] {name} {val!r} must be within range {_range}.")
                            elif ent[name] == 0.0 and enforce_non_zero:
                                if 'void-zero' in t:
                                    if self.replace_zero_by_null_in_case:
                                        star_data.tags[sf_tags.keys().index(name)][1] = None
                                    ent[name] = None
                                else:
                                    f.append(f"[Zero value error] {name} {val!r} should not be zero, "
                                             f"as defined by {self.readableItemType[type]}, {_range}.")
                        elif ('min_exclusive' in _range and ent[name] <= _range['min_exclusive']) or\
                             ('min_inclusive' in _range and ent[name] < _range['min_inclusive']) or\
                             ('max_inclusive' in _range and ent[name] > _range['max_inclusive']) or\
                             ('max_exclusive' in _range and ent[name] >= _range['max_exclusive']):
                            if 'void-zero' in t and ent[name] == 0.0:
                                if self.replace_zero_by_null_in_case:
                                    star_data.tags[sf_tags.keys().index(name)][1] = None
                                ent[name] = None
                            elif not enforce_range:
                                ent[name] = None
                            else:
                                f.append(f"[Range value error] {name} {val} must be within range {_range}.")

                    elif type == 'enum':
                        if val in emptyValue:
                            val = '?'  # '.' raises internal error in NmrDpUtility
                        try:
                            enum = t['enum']
                            if val not in enum:
                                if 'enum-alt' in t and val in t['enum-alt']:
                                    tagNames = [_t[0] for _t in star_data.tags]
                                    itCol = tagNames.index(name)
                                    itName = '_' + category + '.' + t['name']
                                    if val == '?' and enforce_enum:
                                        if self.is_mandatory_tag(itName, file_type):
                                            f.append(f"[Enumeration error] The mandatory type {itName} {val!r} is missing "
                                                     f"and the type must be one of {enum}. {t['enum-alt'][val]} will be given "
                                                     f"unless you would like to fix the type and re-upload the {file_type.upper()} file.")
                                            val = t['enum-alt'][val]
                                            star_data.tags[itCol][1] = val
                                        else:
                                            f.append(f"[Enumeration error] {name} {val!r} should be one of {enum}. "
                                                     "The type may be filled with either 'undefined' or estimated value "
                                                     f"unless you would like to fix the type and re-upload the {file_type.upper()} file.")
                                    else:
                                        val = t['enum-alt'][val]
                                        star_data.tags[itCol][1] = val
                                elif 'enforce-enum' in t and t['enforce-enum']:
                                    raise ValueError(f"{name} {val!r} must be one of {enum}.")
                                elif enforce_enum and name in mand_tag_names:
                                    f.append(f"[Enumeration error] {name} {val!r} should be one of {enum}.")
                            ent[name] = None if val in emptyValue else val
                        except KeyError:
                            raise ValueError(f"Enumeration of tag item {name} is not defined.")

                    elif type == 'enum-int':
                        try:
                            enum = t['enum']
                            if int(val) not in enum:
                                if 'enforce-enum' in t and t['enforce-enum']:
                                    raise ValueError(f"{name} {val!r} must be one of {enum}.")
                                if enforce_enum:
                                    f.append(f"[Enumeration error] {name} {val!r} should be one of {enum}.")
                            ent[name] = int(val)
                        except KeyError:
                            raise ValueError(f"Enumeration of tag item {name} is not defined.")
                        except (ValueError, TypeError):
                            raise ValueError(f"{name} {val!r} must be {self.readableItemType[type]}.")
                    else:
                        ent[name] = val

            for t in tag_items:
                if 'group-mandatory' in t and t['group-mandatory']:
                    name = t['name']
                    group = t['group']
                    if name in ent and ent[name] is not None:
                        if group['coexist-with'] is not None:
                            for cw in group['coexist-with']:
                                if cw not in ent or ent[cw] is None:
                                    raise ValueError(f"One of tag item {cw} must not be empty due to {name} {ent[name]!r}.")

                        if 'smaller-than' in group and group['smaller-than'] is not None:
                            for st in group['smaller-than']:
                                if st in ent and ent[st] is not None:
                                    if ent[name] < ent[st]:
                                        if 'circular-shift' in group:
                                            ent[st] -= abs(group['circular-shift'])
                                        if ent[name] < ent[st]:
                                            raise ValueError(f"Tag item {name} {ent[name]!r} must be larger than {st} {ent[st]!r}.")

                        if 'larger-than' in group and group['larger-than'] is not None:
                            for lt in group['larger-than']:
                                if lt in ent and ent[lt] is not None:
                                    if ent[name] > ent[lt]:
                                        if 'circular-shift' in group:
                                            ent[lt] += abs(group['circular-shift'])
                                        if ent[name] > ent[lt]:
                                            raise ValueError(f"Tag item {name} {ent[name]!r} must be smaller than {lt} {ent[lt]!r}.")

                        if 'not-equal-to' in group and group['not-equal-to'] is not None:
                            for ne in group['not-equal-to']:
                                if ne in ent and ent[ne] is not None:
                                    if ent[name] == ent[ne]:
                                        raise ValueError(f"Tag item {name} {ent[name]!r} must not be equal to {ne} {ent[ne]!r}.")

                    elif group['member-with'] is not None:
                        has_member = not t['mandatory']
                        for mw in group['member-with']:
                            if mw in ent and ent[mw] is not None:
                                has_member = True
                                break
                        if not has_member:
                            member = set(group['member-with'])
                            member.add(name)
                            raise ValueError(f"One of tag items {member} must not be empty.")

        if len(f) > 0:
            raise UserWarning('\n'.join(sorted(list(set(f)), key=f.index)))

        return ent

    def validate_comp_atom(self, comp_id: str, atom_id: str) -> bool:
        """ Validate atom_id of comp_id.
            @change: support non-standard residue by Masashi Yokochi
            @return: True for valid atom_id of comp_id, False otherwise
        """

        if comp_id in emptyValue:
            return False

        comp_id = comp_id.upper()

        if self.__ccU.updateChemCompDict(comp_id):
            return atom_id in [a[self.__ccU.ccaAtomId] for a in self.__ccU.lastAtomList]

        return False

    def get_star_sf_cat(self, nef_sf_cat: str) -> Optional[str]:
        """ Return NMR-STAR saveframe category corresponding to NEF saveframe category.
            @author: Masashi Yokochi
            @return: NEF saveframe category
        """

        try:

            return next(row for row in self.sfCatMap if row[0] == nef_sf_cat)[1]

        except StopIteration:
            return None

    def get_nef_sf_cat(self, star_sf_cat: str) -> Optional[str]:
        """ Return NEF saveframe category corresponding to NMR-STAR saveframe category.
            @author: Masashi Yokochi
            @return: NMR-STAR saveframe category
        """

        try:

            return next(row for row in self.sfCatMap if row[1] == star_sf_cat)[0]

        except StopIteration:
            return None

    def get_star_tag(self, nef_tag: str) -> Tuple[Optional[str], Optional[str], Optional[int]]:
        """ Return NMR-STAR saveframe/loop tag corresponding to NEF tag.
            @change: rename the original get_nmrstar_tag() to get_star_tag() by Masashi Yokochi
            @return: NMR-STAR's author tag and data tag corresponding to a given NEF tag
        """

        try:

            row = next(row for row in self.tagMap if row[0] == nef_tag)

            return row[1], row[2], self.tagMap.index(row)  # author tag, data tag

        except StopIteration:
            return None, None, None

    def get_nef_tag(self, star_tag: str) -> Tuple[Optional[str], Optional[int]]:
        """ Return NEF saveframe/loop tag corresponding to NMR-STAR tag.
            @author: Masashi Yokochi
            @return: NEF data tag corresponding to a given NMR-STAR tag
        """

        try:

            row = next(row for row in self.tagMap if row[2] == star_tag)

            return row[0], self.tagMap.index(row)

        except StopIteration:  # None for NMR-STAR specific tag
            return None, None

    def get_star_auth_tag(self, star_tag: str) -> Tuple[Optional[str], Optional[int]]:
        """ Return NMR-STAR saveframe/loop author tag corresponding to NMR-STAR data tag.
            @return: NMR-STAR's author tag corresponding to a given NMR-STAR data tag
        """

        try:

            row = next(row for row in self.tagMap if row[2] == star_tag)

            return row[1], self.tagMap.index(row)  # author tag

        except ValueError:
            return None, None

    def get_star_loop_tags(self, nef_loop_tags: List[str]) -> List[str]:
        """ Return list of NMR-STAR loop tags corresponding to NEF loop tags.
            @change: rename the original get_nmrstar_loop_tags() to get_star_loop_tags() by Masashi Yokochi
            @return: list of NMR-STAR loop tags corresponding to given NEF loop tags
        """

        out_tag_w_ordinal = {}
        out_tag = []

        for tag in nef_loop_tags:

            auth_tag, data_tag, ordinal = self.get_star_tag(tag)

            if auth_tag is None:
                continue

            out_tag_w_ordinal[data_tag] = ordinal

            if auth_tag != data_tag:
                out_tag_w_ordinal[auth_tag] = ordinal + 100

        out_tag = [t[0] for t in sorted(out_tag_w_ordinal.items(), key=itemgetter(1))]

        lp_category = nef_loop_tags[0].split('.')[0]

        if lp_category == '_nef_sequence':
            out_tag.append('_Chem_comp_assembly.Assembly_ID')

        elif lp_category == '_nef_covalent_links':
            out_tag.insert(0, '_Bond.ID')
            out_tag.insert(1, '_Bond.Type')
            out_tag.insert(2, '_Bond.Value_order')
            out_tag.append('_Bond.Assembly_ID')

        elif lp_category == '_nef_chemical_shift':
            out_tag.insert(0, '_Atom_chem_shift.ID')
            out_tag.insert(9, '_Atom_chem_shift.Ambiguity_code')
            out_tag.insert(10, '_Atom_chem_shift.Ambiguity_set_ID')

            if self.insert_original_pdb_cs_items:
                out_tag.append('_Atom_chem_shift.Original_PDB_strand_ID')
                out_tag.append('_Atom_chem_shift.Original_PDB_residue_no')
                out_tag.append('_Atom_chem_shift.Original_PDB_residue_name')
                out_tag.append('_Atom_chem_shift.Original_PDB_atom_name')

            out_tag.append('_Atom_chem_shift.Details')
            out_tag.append('_Atom_chem_shift.Assigned_chem_shift_list_ID')

        elif lp_category == '_nef_distance_restraint':
            out_tag.append('_Gen_dist_constraint.Member_logic_code')
            out_tag.append('_Gen_dist_constraint.Gen_dist_constraint_list_ID')
            if self.insert_original_atom_name_items:
                out_tag.append('_Gen_dist_constraint.Auth_atom_name_1')
                out_tag.append('_Gen_dist_constraint.Auth_atom_name_2')

        elif lp_category == '_nef_dihedral_restraint':
            out_tag.append('_Torsion_angle_constraint.Torsion_angle_constraint_list_ID')
            if self.insert_original_atom_name_items:
                out_tag.append('_Torsion_angle_constraint.Auth_atom_name_1')
                out_tag.append('_Torsion_angle_constraint.Auth_atom_name_2')
                out_tag.append('_Torsion_angle_constraint.Auth_atom_name_3')
                out_tag.append('_Torsion_angle_constraint.Auth_atom_name_4')

        elif lp_category == '_nef_rdc_restraint':
            out_tag.append('_RDC_constraint.RDC_constraint_list_ID')
            if self.insert_original_atom_name_items:
                out_tag.append('_RDC_constraint.Auth_atom_name_1')
                out_tag.append('_RDC_constraint.Auth_atom_name_2')

        elif lp_category == '_nef_peak':
            out_tag.append('_Peak_row_format.Details')
            out_tag.append('_Peak_row_format.Spectral_peak_list_ID')

        elif lp_category == '_nef_spectrum_dimension':
            out_tag.append('_Spectral_dim.Spectral_peak_list_ID')

        elif lp_category == '_nef_spectrum_dimension_transfer':
            out_tag.append('_Spectral_dim_transfer.Spectral_peak_list_ID')

        return out_tag

    def get_nef_loop_tags(self, star_loop_tags: List[str]) -> List[str]:
        """ Return list of NEF loop tags corresponding to NMR-STAR loop tags.
            @author: Masashi Yokochi
            @return: list of NEF loop tags corresponding to given NMR-STAR loop tags
        """

        out_tag_w_ordinal = {}
        out_tag = []

        for tag in star_loop_tags:

            data_tag, ordinal = self.get_nef_tag(tag)

            if data_tag is not None:
                out_tag_w_ordinal[data_tag] = ordinal

        out_tag = [t[0] for t in sorted(out_tag_w_ordinal.items(), key=itemgetter(1))]

        if len(out_tag) > 0 and out_tag[0].startswith('_nef_sequence.') and '_nef_sequence.index' not in out_tag:
            out_tag.insert(0, '_nef_sequence.index')

        return out_tag

    def get_valid_star_atom_in_xplor_for_ligand_remap(self, comp_id: str, atom_id: str, coord_atom_site: dict
                                                      ) -> Tuple[List[str], Optional[int], Optional[str]]:
        """ Return lists of atom ID in IUPAC atom nomenclature for a given atom name in XPLOR atom nomenclature
            in reference to coordinates' alternative atom IDs.
            @author: Masashi Yokochi
            @return: list of instanced atom_id, ambiguity_code, and description
            @note: used only for annotation (DAOTHER-9286)
        """

        if comp_id in emptyValue or atom_id in emptyValue:
            return [], None, None

        methyl_only = atom_id[0] == 'M'
        # if comp_id == 'ACE' and atom_id.startswith('Q'):
        #     atom_id = 'H%'
        #     methyl_only = True

        atom_list = []
        ambiguity_code = details = None

        if '++' in atom_id:
            atom_id = re.sub(r'\+\+', '+', atom_id)

        if '#' in atom_id:
            atom_id = atom_id.replace('#', '%')

        if atom_id.endswith('%%'):
            atom_id = re.sub('%%', '%', atom_id)

        if atom_id[0] in ('1', '2', '3'):
            atom_list, ambiguity_code, details = self.get_valid_star_atom_for_ligand_remap(comp_id, atom_id, coord_atom_site, methyl_only)
            if details is None:
                return (atom_list, ambiguity_code, details)
            atom_id = atom_id[1:] + atom_id[0]
            if atom_id in self.__csStat.getMethylAtoms(comp_id):
                methyl_only = True

        len_atom_id = len(atom_id)

        if atom_id[0] in ('H', 'Q', 'M'):

            if atom_id[-1] == '+' and atom_id[1].isdigit() and len_atom_id > 2 and self.__ccU.updateChemCompDict(comp_id):
                if self.__ccU.lastChemCompDict['_chem_comp.type'] in ('DNA LINKING', 'RNA LINKING'):  # DAOTHER-9198
                    _atom_list, _ambiguity_code, _details = self.get_valid_star_atom_for_ligand_remap(comp_id, 'HN' + atom_id[1:-1], coord_atom_site, methyl_only)
                    if _details is None:
                        atom_list, ambiguity_code, details = _atom_list, _ambiguity_code, _details
                        return (atom_list, ambiguity_code, details)

        atom_list, ambiguity_code, details = self.get_valid_star_atom_for_ligand_remap(comp_id, atom_id, coord_atom_site, methyl_only)

        if details is not None and atom_id[-1] not in ('%', '*'):
            _atom_list, _ambiguity_code, _details = self.get_valid_star_atom_for_ligand_remap(comp_id, atom_id + '%', coord_atom_site, methyl_only)
            if _details is None:
                atom_list, ambiguity_code, details = _atom_list, _ambiguity_code, _details
            elif atom_id[0] in protonBeginCode or len_atom_id > 1:
                atom_list, ambiguity_code, details = self.get_valid_star_atom_for_ligand_remap(comp_id, atom_id + '*', coord_atom_site, methyl_only)
                if details is not None:
                    atom_list, ambiguity_code, details = self.get_valid_star_atom_for_ligand_remap(comp_id, atom_id, coord_atom_site, methyl_only)
                    # 2l8r, comp_id=APR, atom_id=Q5D -> ['H5R1', 'H5R2']
                    if details is not None and atom_id[0] in ('Q', 'M'):
                        protons = self.__ccU.getBondedAtoms(comp_id, 'C' + atom_id[1:], onlyProton=True)
                        resolved = False
                        len_protons = len(protons)
                        if len_protons in (1, 3):
                            atom_list, ambiguity_code, details = protons, 1, None
                            resolved = True
                        elif len_protons == 2:
                            atom_list, ambiguity_code, details = protons, 2, None
                            resolved = True
                        if not resolved:
                            protons = self.__ccU.getBondedAtoms(comp_id, 'N' + atom_id[1:], onlyProton=True)
                            len_protons = len(protons)
                            if len_protons in (1, 3):
                                atom_list, ambiguity_code, details = protons, 1, None
                            elif len_protons == 2:
                                atom_list, ambiguity_code, details = protons, 2, None
                        if atom_id.startswith('QQ') and self.__ccU.updateChemCompDict(comp_id):
                            root, _branch = [], []
                            _root = self.__ccU.getBondedAtoms(comp_id, 'C' + atom_id[2:], exclProton=True)
                            if len(_root) > 0:
                                _branch.append('C' + atom_id[2:])
                                root.extend(_root)
                            for e in '123ABC':
                                _root = self.__ccU.getBondedAtoms(comp_id, 'C' + atom_id[2:] + e, exclProton=True)
                                if len(_root) > 0:
                                    _branch.append('C' + atom_id[2:] + e)
                                    root.extend(_root)
                            _root = self.__ccU.getBondedAtoms(comp_id, 'N' + atom_id[2:], exclProton=True)
                            if len(_root) > 0:
                                _branch.append('N' + atom_id[2:])
                                root.extend(_root)
                            for e in '123ABC':
                                _root = self.__ccU.getBondedAtoms(comp_id, 'N' + atom_id[2:] + e, exclProton=True)
                                if len(_root) > 0:
                                    _branch.append('N' + atom_id[2:] + e)
                                    root.extend(_root)
                            protons = []
                            aliphatic = True
                            for k, v in collections.Counter(root).most_common():
                                if v != 2:
                                    continue
                                cca = next((cca for cca in self.__ccU.lastAtomList if cca[self.__ccU.ccaAtomId] == k and cca[self.__ccU.ccaLeavingAtomFlag] == 'N'), None)
                                if cca is not None:
                                    if cca[self.__ccU.ccaAromaticFlag] == 'Y':
                                        aliphatic = False
                                branch = [branch for branch in self.__ccU.getBondedAtoms(comp_id, k, exclProton=True) if branch in _branch]
                                if len(branch) == 2:
                                    for b in branch:
                                        protons.extend(self.__ccU.getBondedAtoms(comp_id, b, onlyProton=True))
                            len_protons = len(protons)
                            if len_protons in (4, 6):
                                atom_list, ambiguity_code, details = protons, 2 if aliphatic else 3, None
                                resolved = True
                    # 5lig, comp_id=6XM, atom_id=HA' -> ["HA1'", "HA2'"]
                    # c' should not be propagated: peak list (5z80. D_1300006579_nmr-peaks-upload_P2.dat.V5)
                    # c7' should be allowed: 6gpi, Dihedral_res.tbl
                    elif details is not None and atom_id.endswith("'") and not atom_id.endswith("''") and (atom_id[0] in protonBeginCode or atom_id[1].isdigit()):
                        _atom_list, _ambiguity_code, _details = self.get_valid_star_atom_for_ligand_remap(comp_id, atom_id[:-1] + "%'", coord_atom_site, methyl_only)
                        if _details is None:
                            atom_list, ambiguity_code, details = _atom_list, _ambiguity_code, _details

        return (atom_list, ambiguity_code, details)

    def get_valid_star_atom_for_ligand_remap(self, comp_id: str, atom_id: str, coord_atom_site: dict, methyl_only: bool = False
                                             ) -> Tuple[List[str], Optional[int], Optional[str]]:
        """ Return lists of atom ID, ambiguity_code, details in IUPAC atom nomenclature for a given conventional NMR atom name
            in reference to coordinates' alternative atom IDs.
            @author: Masashi Yokochi
            @return: list of instanced atom_id, ambiguity_code, and description
            @note: used only for annotation (DAOTHER-9286)
        """

        if comp_id in emptyValue or atom_id in emptyValue:
            return [], None, None

        nucleotide = self.__csStat.getTypeOfCompId(comp_id)[1]

        methyl_only |= atom_id[0] == 'M'

        atom_list = []
        ambiguity_code = details = None

        if '#' in atom_id:
            atom_id = atom_id.replace('#', '%')

        if atom_id.endswith('%%'):
            atom_id = re.sub('%%', '%', atom_id)

        if atom_id == 'HN' or atom_id.endswith('%') or atom_id.endswith('*'):
            atom_list, ambiguity_code, details = self.get_star_atom_for_ligand_remap(comp_id, atom_id, details, coord_atom_site, methyl_only)
            return (atom_list, ambiguity_code, details)

        len_atom_id = len(atom_id)

        if atom_id[0] in ('M', 'Q') or (isLikePheOrTyr(comp_id, self.__ccU) and atom_id in ('HR', 'HR%', 'HR*')):

            if atom_id.startswith('QQ'):
                atom_list, ambiguity_code, details = self.get_star_atom_for_ligand_remap(comp_id, 'H' + atom_id[2:] + ('%' if nucleotide else '*'),
                                                                                         details, coord_atom_site, methyl_only)
                if details is not None and comp_id not in monDict3 and self.__csStat.peptideLike(comp_id)\
                   and atom_id[2] in ('A', 'B', 'G', 'D', 'E', 'Z', 'H'):
                    grk_atoms = self.__ccU.getAtomsBasedOnGreekLetterSystem(comp_id, 'H' + atom_id[2])
                    if len(grk_atoms) > 0:
                        atom_list = []
                        details = None
                        for grk_atom in grk_atoms:
                            _atom_list, ambiguity_code, details = self.get_star_atom_for_ligand_remap(comp_id, grk_atom, details, coord_atom_site, methyl_only)
                            atom_list.extend(_atom_list)
                        if len(atom_list) >= 4:
                            return (atom_list, ambiguity_code, details)
                if len(atom_list) >= 4:
                    return (atom_list, ambiguity_code, details)

            if atom_id.startswith('HR') or atom_id.startswith('QR') or atom_id.startswith('QX'):
                qr_atoms = sorted(set(atom_id[:-1] + '%' for atom_id in self.__csStat.getAromaticAtoms(comp_id)
                                      if atom_id[0] in protonBeginCode and self.__csStat.getMaxAmbigCodeWoSetId(comp_id, atom_id) == 3))
                if len(qr_atoms) == 0:
                    return (atom_list, ambiguity_code, details)
                atom_list = []
                details = None
                for qr_atom in qr_atoms:
                    _atom_list, ambiguity_code, details = self.get_star_atom_for_ligand_remap(comp_id, qr_atom, details, coord_atom_site, methyl_only)
                    atom_list.extend(_atom_list)
                if len(atom_list) >= 4:
                    return (atom_list, ambiguity_code, details)

            if atom_id.startswith('Q') or atom_id.startswith('M'):
                min_len = 4 if atom_id.startswith('QQ') else 1  # ILE/LEU/THR:QB -> HB (2m6i), MG -> Magnesium (2n3r)
                if atom_id[-1].isalnum():
                    atom_list, ambiguity_code, details = self.get_star_atom_for_ligand_remap(comp_id, 'H' + atom_id[1:] + ('%' if nucleotide else '*'),
                                                                                             details, coord_atom_site, methyl_only)
                    if details is not None and comp_id not in monDict3 and self.__csStat.peptideLike(comp_id) and len_atom_id > 1\
                       and atom_id[1] in ('A', 'B', 'G', 'D', 'E', 'Z', 'H'):
                        grk_atoms = self.__ccU.getAtomsBasedOnGreekLetterSystem(comp_id, 'H' + atom_id[1])
                        if len(grk_atoms) > 0:
                            atom_list = []
                            details = None
                            for grk_atom in grk_atoms:
                                _atom_list, ambiguity_code, details = self.get_star_atom_for_ligand_remap(comp_id, grk_atom, details, coord_atom_site, methyl_only)
                                atom_list.extend(_atom_list)
                            if len(atom_list) >= min_len:
                                return (atom_list, ambiguity_code, details)
                    if details is None and len(atom_list) == 1:
                        atom_list = self.__ccU.getProtonsInSameGroup(comp_id, atom_list[0])
                    if len(atom_list) >= min_len:
                        return (atom_list, ambiguity_code, details)
                atom_list, ambiguity_code, details =\
                    self.get_star_atom_for_ligand_remap(comp_id, 'H' + atom_id[1:] + '*', details, coord_atom_site, methyl_only)
                if details is None and len(atom_list) == 1:
                    atom_list = self.__ccU.getProtonsInSameGroup(comp_id, atom_list[0])
                if len(atom_list) >= min_len:
                    return (atom_list, ambiguity_code, details)

        if len_atom_id > 2 and ((atom_id + '2' in self.__csStat.getAllAtoms(comp_id)) or (atom_id + '22' in self.__csStat.getAllAtoms(comp_id))):
            atom_list, ambiguity_code, details = self.get_star_atom_for_ligand_remap(comp_id, atom_id + '%', details, coord_atom_site, methyl_only)
            return (atom_list, ambiguity_code, details)

        atom_list, ambiguity_code, details = self.get_star_atom_for_ligand_remap(comp_id, atom_id, details, coord_atom_site, methyl_only)

        if details is not None and atom_id[-1] not in ('%', '*'):
            _atom_list, _ambiguity_code, _details = self.get_star_atom_for_ligand_remap(comp_id, atom_id + ('%' if nucleotide else '*'),
                                                                                        None, coord_atom_site, methyl_only)
            if _details is None:
                atom_list, ambiguity_code, details = _atom_list, _ambiguity_code, _details

        if details is not None and comp_id not in monDict3 and self.__csStat.peptideLike(comp_id) and atom_id[0] in ('H', 'C', 'N', 'O', 'P')\
           and len_atom_id > 1 and atom_id[1] in ('A', 'B', 'G', 'D', 'E', 'Z', 'H')\
           and (atom_id[0] != 'H' or (atom_id[0] == 'H' and atom_id[-1] not in ('%', '*') and not (atom_id[-1].isdigit() and atom_id[-2].isdigit()))):
            grk_atoms = self.__ccU.getAtomsBasedOnGreekLetterSystem(comp_id, atom_id)
            if len(grk_atoms) > 0:
                atom_list = []
                details = None
                for grk_atom in grk_atoms:
                    _atom_list, ambiguity_code, details = self.get_star_atom_for_ligand_remap(comp_id, grk_atom, details, coord_atom_site, methyl_only)
                    atom_list.extend(_atom_list)

        return (atom_list, ambiguity_code, details)

    def get_star_atom_for_ligand_remap(self, comp_id: str, nef_atom: str, details: str, coord_atom_site: dict, methyl_only: bool = False
                                       ) -> Tuple[List[str], Optional[int], Optional[str]]:
        """ Return list of instanced atom_id of a given NEF atom (including wildcard codes) and its ambiguity code.
            @change: support non-standard residue by Masashi Yokochi
            @return: list of instanced atom_id of a given NEF atom, ambiguity_code, and description
            @note: used only for annotation (DAOTHER-9286)
        """

        if comp_id in emptyValue:
            return [], None, None

        comp_id = comp_id.upper()
        is_std_comp_id = comp_id in monDict3

        atom_list, atoms, methyl_atoms = [], [], []
        ambiguity_code = 1

        alt_atom_conv_dict = dict(zip(coord_atom_site['atom_id'], coord_atom_site['alt_atom_id']))
        atom_conv_dict = dict(zip(coord_atom_site['alt_atom_id'], coord_atom_site['atom_id']))

        if self.__ccU.updateChemCompDict(comp_id) and self.__annotation_mode:
            cc_rel_status = self.__ccU.lastChemCompDict['_chem_comp.pdbx_release_status']

            if cc_rel_status == 'REL':
                methyl_atoms = self.__csStat.getMethylAtoms(comp_id)
                not_methyl = not methyl_only or nef_atom[0] not in protonBeginCode or len(methyl_atoms) == 0
                atoms = [a[self.__ccU.ccaAtomId] for a in self.__ccU.lastAtomList
                         if not_methyl or (not not_methyl and a[self.__ccU.ccaAtomId] in methyl_atoms)]
                alt_atom_dict = {a[self.__ccU.ccaAltAtomId]: a[self.__ccU.ccaAtomId] for a in self.__ccU.lastAtomList
                                 if not_methyl or (not not_methyl and a[self.__ccU.ccaAtomId] in methyl_atoms)
                                 and a[self.__ccU.ccaAltAtomId] != a[self.__ccU.ccaAtomId]}
                if nef_atom not in atoms and nef_atom in alt_atom_dict:
                    nef_atom = alt_atom_dict[nef_atom]

            # DAOTHER-8817
            elif self.chemCompAtom is not None and comp_id in self.chemCompAtom:
                atoms = copy.copy(self.chemCompAtom[comp_id])

                for v in self.chemCompBond[comp_id].values():
                    if len(v) == 3:
                        methyl_atoms.extend(v)

            else:
                methyl_atoms = self.__csStat.getMethylAtoms(comp_id)
                not_methyl = not methyl_only or nef_atom[0] not in protonBeginCode or len(methyl_atoms) == 0
                atoms = [a[self.__ccU.ccaAtomId] for a in self.__ccU.lastAtomList
                         if not_methyl or (not not_methyl and a[self.__ccU.ccaAtomId] in methyl_atoms)]

        else:

            if self.chemCompAtom is not None and comp_id in self.chemCompAtom:
                atoms = copy.copy(self.chemCompAtom[comp_id])

                for v in self.chemCompBond[comp_id].values():
                    if len(v) == 3:
                        methyl_atoms.extend(v)

        atoms = [alt_atom_conv_dict[atom] if atom in alt_atom_conv_dict else atom for atom in atoms if atom[0] == nef_atom[0]]
        methyl_atoms = [alt_atom_conv_dict[atom] if atom in alt_atom_conv_dict else atom for atom in methyl_atoms if atom[0] == nef_atom[0]]

        try:

            # DAOTHER-8817: guess ambiguity code from pseudo CCD
            def guess_ambiguity_code(atom_list):
                if self.chemCompBond is not None and comp_id in self.chemCompBond:
                    for k, v in self.chemCompBond[comp_id].items():
                        if atom_list[0] in v:
                            len_v = len(v)
                            if len_v == 2:
                                return 2  # methylene/amino
                            if len_v == 1:
                                if k[0] == 'C' and self.chemCompTopo is not None and comp_id in self.chemCompTopo\
                                   and any(len(tv) == 2 and tv[0][0] == 'C' and tv[1][0] == 'C'
                                           for tk, tv in self.chemCompTopo[comp_id].items() if tk == k):
                                    return 3  # aromatic opposite
                                return 1
                return None

            ref_atom = re.findall(r'([^ \t\r\n\f\v\(\)\{\}\[\]]+)([xyXY])([%*])$'
                                  r'|([^ \t\r\n\f\v\(\)\{\}\[\]]+)([%*])$|([^ \t\r\n\f\v\(\)\{\}\[\]]+)([xyXY]$)'
                                  r'|([%*])([^ \t\r\n\f\v\(\)\{\}\[\]]+)', nef_atom)[0]

            atm_set = [ref_atom.index(a) for a in ref_atom if a != '']

            pattern = None

            if atm_set == [0, 1, 2]:  # endswith [xyXY][%*]

                atom_type = ref_atom[0]
                xy_code = ref_atom[1].lower()

                len_atom_type = len(atom_type)

                pattern = re.compile(fr'{atom_type}\S\d+')

                alist2 = [a for a in atoms
                          if re.match(pattern, a) and a[len_atom_type].isdigit()]  # bmrb_id: 15879, pdb_id: 2k6r, comp_id: DNS

                xid = sorted(set(int(a[len_atom_type]) for a in alist2))

                # DAOTHER-8817: select proper atom groups
                xid_count = {}
                for _xid in xid:
                    xid_count[_xid] = len([a for a in alist2 if int(a[len_atom_type]) == _xid])
                _xid_count = next((k for k, v in collections.Counter(xid_count.values()).most_common() if v == 2), None)
                if _xid_count is None:
                    _xid_count = next((k for k, v in collections.Counter(xid_count.values()).most_common() if v == 1), None)
                xid = [k for k, v in xid_count.items() if v == _xid_count]

                if xy_code == 'x':
                    atom_list = [a for a in alist2 if int(a[len_atom_type]) == xid[0]]
                    if len(atom_list) > 3:  # bmrb_id: 15879, pdb_id: 2k6r, comp_id: DNS
                        atom_list[3:] = []

                else:
                    atom_list = [a for a in alist2 if int(a[len_atom_type]) == xid[1]]
                    if len(atom_list) > 3:  # bmrb_id: 15879, pdb_id: 2k6r, comp_id: DNS
                        atom_list[3:] = []

                ambiguity_code = self.__csStat.getMaxAmbigCodeWoSetId(comp_id, atom_list[0])

                # DAOTHER-8817: guess ambiguity code from pseudo CCD
                if ambiguity_code == 0:
                    ambiguity_code = min([len(xid), 2]) if atom_list[0] in methyl_atoms else guess_ambiguity_code(atom_list)

            elif atm_set == [3, 4]:  # endswith [%*] but neither [xyXY][%*]

                atom_type = _atom_type = ref_atom[3]
                wc_code = ref_atom[4]

                if atom_type[0] not in ('%', '*'):
                    # DAOTHER-8817: H\S*[xyXY]\S+[%*]
                    if atom_type[0] in protonBeginCode and ('X' in atom_type or 'Y' in atom_type or 'x' in atom_type or 'y' in atom_type):
                        _atom_type = atom_type.replace('X', '').replace('Y', '').replace('x', '').replace('y', '')
                        if wc_code == '%':
                            pattern = re.compile(fr'{_atom_type}\d+') if is_std_comp_id else re.compile(fr'{_atom_type}\S?$')
                        elif wc_code == '*':
                            pattern = re.compile(fr'{_atom_type}\S+')
                        elif self.__verbose:
                            self.__lfh.write(f"+{self.__class_name__}.get_star_atom_for_ligand_remap() ++ Error  - Invalid NEF atom nomenclature {nef_atom} found.\n")
                    elif wc_code == '%':
                        pattern = re.compile(fr'{atom_type}\d+') if is_std_comp_id else re.compile(fr'{atom_type}\S?$')
                    elif wc_code == '*':
                        pattern = re.compile(fr'{atom_type}\S+')
                    elif self.__verbose:
                        self.__lfh.write(f"+{self.__class_name__}.get_star_atom_for_ligand_remap() ++ Error  - Invalid NEF atom nomenclature {nef_atom} found.\n")
                else:
                    _wc_code = atom_type[0]
                    atom_type = atom_type[1:]

                    if _wc_code == '%':
                        if wc_code == '%':
                            pattern = re.compile(fr'\d+{atom_type}\d+') if is_std_comp_id else re.compile(fr'\S?{atom_type}\S?$')
                        elif wc_code == '*':
                            pattern = re.compile(fr'\d+{atom_type}\S+') if is_std_comp_id else re.compile(fr'\S?{atom_type}\S+$')
                        elif self.__verbose:
                            self.__lfh.write(f"+{self.__class_name__}.get_star_atom_for_ligand_remap() ++ Error  - Invalid NEF atom nomenclature {nef_atom} found.\n")
                    elif _wc_code == '*':
                        if wc_code == '%':
                            pattern = re.compile(fr'\S+{atom_type}\d+') if is_std_comp_id else re.compile(fr'\S+{atom_type}\S?$')
                        elif wc_code == '*':
                            pattern = re.compile(fr'\S+{atom_type}\S+')
                        elif self.__verbose:
                            self.__lfh.write(f"+{self.__class_name__}.get_star_atom_for_ligand_remap() ++ Error  - Invalid NEF atom nomenclature {nef_atom} found.\n")
                    elif self.__verbose:
                        self.__lfh.write(f"+{self.__class_name__}.get_star_atom_for_ligand_remap() ++ Error  - Invalid NEF atom nomenclature {nef_atom} found.\n")

                atom_list = [a for a in atoms if re.match(pattern, a) and nef_atom[0] in ('H', '1', '2', '3', a[0])]

                if not is_std_comp_id and self.__csStat.peptideLike(comp_id) and any(a in aminoProtonCode for a in atom_list)\
                   and any(a not in aminoProtonCode for a in atom_list):
                    atom_list = [a for a in atom_list if a not in aminoProtonCode]  # ACA:H21, H22, H2 (5nwu)

                if atom_type != _atom_type and self.chemCompBond is not None and comp_id in self.chemCompBond:
                    _atom_list = []
                    for a in atom_list:
                        for v in self.chemCompBond[comp_id].values():
                            if a in v and len(v) > 1:
                                _atom_list.extend(v)

                    if len(_atom_list) > 0:
                        atom_list = _atom_list

                ambiguity_code = 1 if atom_list[0] in methyl_atoms else self.__csStat.getMaxAmbigCodeWoSetId(comp_id, atom_list[0])

                # DAOTHER-8817: guess ambiguity code from pseudo CCD
                if ambiguity_code == 0:
                    ambiguity_code = guess_ambiguity_code(atom_list)

            elif atm_set == [5, 6]:  # endswith [xyXY]

                atom_type = ref_atom[5]
                xy_code = ref_atom[6].lower()

                pattern = re.compile(fr'{atom_type}[^\']+')

                atom_list = [a for a in atoms if re.match(pattern, a)]

                atom_list_len = len(atom_list)

                if atom_list_len != 2:
                    if atom_list_len > 2:
                        atom_list = []
                elif xy_code == 'y':
                    atom_list = atom_list[-1:]
                elif xy_code == 'x':
                    atom_list = atom_list[:1]
                elif self.__verbose:
                    self.__lfh.write(f"+{self.__class_name__}.get_star_atom_for_ligand_remap() ++ Error  - Invalid NEF atom nomenclature {nef_atom} found.\n")

                ambiguity_code = self.__csStat.getMaxAmbigCodeWoSetId(comp_id, atom_list[0])

                # DAOTHER-8817: guess ambiguity code from pseudo CCD
                if ambiguity_code == 0:
                    ambiguity_code = guess_ambiguity_code(atom_list)

            elif atm_set == [7, 8]:  # startswith [%*]

                atom_type = ref_atom[8]
                wc_code = ref_atom[7]

                if wc_code == '%':
                    pattern = re.compile(fr'\d+{atom_type}') if is_std_comp_id else re.compile(fr'\S?{atom_type}')
                elif wc_code == '*':
                    pattern = re.compile(fr'\S+{atom_type}')
                elif self.__verbose:
                    self.__lfh.write(f"+{self.__class_name__}.get_star_atom_for_ligand_remap() ++ Error  - Invalid NEF atom nomenclature {nef_atom} found.\n")

                atom_list = [a for a in atoms if re.match(pattern, a)]

                if not is_std_comp_id and self.__csStat.peptideLike(comp_id) and any(a in aminoProtonCode for a in atom_list)\
                   and any(a not in aminoProtonCode for a in atom_list):
                    atom_list = [a for a in atom_list if a not in aminoProtonCode]  # ACA:H21, H22, H2 (5nwu)

                ambiguity_code = 1 if atom_list[0] in methyl_atoms else self.__csStat.getMaxAmbigCodeWoSetId(comp_id, atom_list[0])

                # DAOTHER-8817: guess ambiguity code from pseudo CCD
                if ambiguity_code == 0:
                    ambiguity_code = guess_ambiguity_code(atom_list)

            elif self.__verbose:
                self.__lfh.write(f"+{self.__class_name__}.get_star_atom_for_ligand_remap() ++ Error  - Invalid NEF atom nomenclature {nef_atom} found.\n")

        except IndexError:
            pass

        if len(atom_list) == 0:

            if self.__csStat.peptideLike(comp_id):
                if nef_atom == 'HN':
                    atom_list, ambiguity_code, details = self.get_star_atom_for_ligand_remap(comp_id, 'H', None, coord_atom_site)
                    return (atom_list, ambiguity_code, details)
                if nef_atom == 'CO':
                    atom_list, ambiguity_code, details = self.get_star_atom_for_ligand_remap(comp_id, 'C', None, coord_atom_site)
                    return (atom_list, ambiguity_code, details)

            if self.__csStat.hasCompId(comp_id):

                if is_std_comp_id and not nef_atom.endswith('%') and not nef_atom.endswith('*') and nef_atom + '1' in methyl_atoms:
                    atom_list, ambiguity_code, details =\
                        self.get_star_atom_for_ligand_remap(comp_id, nef_atom + '%', None, coord_atom_site, methyl_only)
                    return (atom_list, ambiguity_code, details)

                if nef_atom[-1].lower() == 'x' or nef_atom[-1].lower() == 'y' and nef_atom[:-1] + '1' in methyl_atoms:
                    atom_list, ambiguity_code, details =\
                        self.get_star_atom_for_ligand_remap(comp_id, nef_atom[:-1] + '%', None, coord_atom_site, methyl_only)
                    return (atom_list, ambiguity_code, details)

                if ((is_std_comp_id and nef_atom[-1] == '%') or nef_atom[-1] == '*') and (nef_atom[:-1] + '1' not in methyl_atoms) and\
                   len(nef_atom) > 2 and (nef_atom[-2].lower() == 'x' or nef_atom[-2].lower() == 'y'):
                    atom_list, ambiguity_code, details =\
                        self.get_star_atom_for_ligand_remap(comp_id, nef_atom[:-2] + ('1' if nef_atom[-2].lower() == 'x' else '2') + '%', None,
                                                            coord_atom_site, methyl_only)
                    return (atom_list, ambiguity_code, details)

                if ((is_std_comp_id and nef_atom[-1] == '%') or nef_atom[-1] == '*') and nef_atom[:-1] in atoms:
                    atom_list, ambiguity_code, details =\
                        self.get_star_atom_for_ligand_remap(comp_id, nef_atom[:-1], None, coord_atom_site, methyl_only)
                    return (atom_list, ambiguity_code, details)

            if nef_atom in atoms:
                atom_list.append(nef_atom)

            else:  # DAOTHER-8817
                atom_list.append(nef_atom)
                ambiguity_code = None

        atom_list = [atom_conv_dict[atom] if atom in atom_conv_dict else atom for atom in atom_list]
        atom_list = sorted(atom_list)

        return (atom_list, ambiguity_code, details)

    def get_valid_star_atom_in_xplor(self, comp_id: str, atom_id: str, details: Optional[str] = None, leave_unmatched: bool = True
                                     ) -> Tuple[List[str], Optional[int], Optional[str]]:
        """ Return lists of atom ID, ambiguity_code, details in IUPAC atom nomenclature for a given atom name in XPLOR atom nomenclature.
            @author: Masashi Yokochi
            @return: list of instanced atom_id, ambiguity_code, and description
        """

        if comp_id in emptyValue or atom_id in emptyValue:
            return [], None, None

        methyl_only = atom_id[0] == 'M' or atom_id.startswith('HM') or atom_id.startswith('QM') or atom_id.startswith('QQM')
        # if comp_id == 'ACE' and atom_id.startswith('Q'):
        #     atom_id = 'H%'
        #     methyl_only = True

        key = (comp_id, atom_id, details, leave_unmatched, methyl_only)
        if key in self.__cachedDictForValidStarAtomInXplor:
            return copy.deepcopy(self.__cachedDictForValidStarAtomInXplor[key])

        atom_list = []
        ambiguity_code = details = None

        if sepPattern.search(atom_id):
            atom_ids = sepPattern.sub(' ', atom_id.strip()).split()
            _atom_list = []
            _ambiguity_code = 1
            valid = True
            for _atom_id in atom_ids:
                _atom_list_, _ambiguity_code_, _details = self.get_valid_star_atom_in_xplor(comp_id, _atom_id.strip(), details, leave_unmatched)
                if _details is not None:
                    valid = False
                    break
                _atom_list.extend(_atom_list_)
                _ambiguity_code = max(_ambiguity_code, _ambiguity_code_)
            if valid and len(_atom_list) > 0:
                _atom_list = sorted(set(_atom_list))
                if len(_atom_list) > 1 and _ambiguity_code < 2:
                    _ambiguity_code = 4
                atom_list, ambiguity_code = _atom_list, _ambiguity_code
                return (atom_list, ambiguity_code, details)

        try:

            # DAOTHER-10105: resolve pseudo atom name of non-standard residue
            if comp_id not in monDict3 and self.authAtomNameToId is not None and comp_id in self.authAtomNameToId\
               and not self.__annotation_mode:  # and atom_id[0] in ('Q', 'M'):
                _atom_id = atom_id
                if _atom_id[0] in ('Q', 'M'):
                    _atom_id = 'H' + atom_id[1:] + '*'
                coord_atom_site = {'atom_id': list(self.authAtomNameToId[comp_id].values()),
                                   'alt_atom_id': list(self.authAtomNameToId[comp_id].keys())}
                _atom_list, _ambiguity_code, _details = self.get_star_atom_for_ligand_remap(comp_id, _atom_id, details, coord_atom_site, methyl_only)
                if len(_atom_list) > 0 and _atom_list[0][-1] not in ('%', '*') and _atom_list[0] in coord_atom_site['atom_id']:
                    atom_list, ambiguity_code, details = _atom_list, _ambiguity_code, _details
                    return (atom_list, ambiguity_code, details)

            if '++' in atom_id:
                atom_id = re.sub(r'\+\+', '+', atom_id)

            if '#' in atom_id:
                atom_id = atom_id.replace('#', '%')

            if atom_id.endswith('%%'):
                atom_id = re.sub('%%', '%', atom_id)

            if atom_id[-1] in ('%', '*') and len(atom_id) > 2 and atom_id[-2] != "'" and self.__csStat.getTypeOfCompId(comp_id)[1]:
                atom_id = translateToStdAtomName(atom_id[:-1], refCompId=comp_id, ccU=self.__ccU) + atom_id[-1]

            if atom_id[0] in ('1', '2', '3'):
                atom_list, ambiguity_code, details = self.get_valid_star_atom(comp_id, atom_id, details, leave_unmatched, methyl_only)
                if details is None:
                    return (atom_list, ambiguity_code, details)
                atom_id = atom_id[1:] + atom_id[0]
                if atom_id in self.__csStat.getMethylAtoms(comp_id):
                    methyl_only = True

            len_atom_id = len(atom_id)

            if atom_id[0] in ('H', 'Q', 'M') and (self.__remediation_mode or atom_id[0] in ('H', 'M')):  # DAOTHER-8663, 8751

                if atom_id.endswith('1') and not self.validate_comp_atom(comp_id, atom_id):
                    _atom_id = atom_id[:-1] + '3'
                    if self.validate_comp_atom(comp_id, _atom_id):
                        atom_list, ambiguity_code, details = self.get_valid_star_atom(comp_id, _atom_id, details, leave_unmatched, methyl_only)
                        return (atom_list, ambiguity_code, details)

                if atom_id.endswith('1*') or atom_id.endswith('1%'):
                    _atom_id = atom_id[:-2] + '3' + atom_id[-1]
                    _atom_list, _ambiguity_code, _details = self.get_valid_star_atom(comp_id, _atom_id, None, True, methyl_only)
                    if _details is None:
                        if leave_unmatched:
                            atom_list, ambiguity_code, details = _atom_list, _ambiguity_code, _details
                            return (atom_list, ambiguity_code, details)
                        atom_list, ambiguity_code, details = self.get_valid_star_atom(comp_id, _atom_id, details, leave_unmatched, methyl_only)
                        return (atom_list, ambiguity_code, details)

                    _atom_list, _ambiguity_code, _details = self.get_valid_star_atom(comp_id, _atom_id[:-1], None, True, methyl_only)
                    if _details is None:
                        if leave_unmatched:
                            atom_list, ambiguity_code, details = _atom_list, _ambiguity_code, _details
                            return (atom_list, ambiguity_code, details)
                        atom_list, ambiguity_code, details = self.get_valid_star_atom(comp_id, _atom_id, details, leave_unmatched, methyl_only)
                        return (atom_list, ambiguity_code, details)

                if atom_id in ('HN', 'HN%', 'HN*') and not self.validate_comp_atom(comp_id, atom_id):
                    if self.validate_comp_atom(comp_id, 'HN3'):
                        _atom_list = self.__ccU.getProtonsInSameGroup(comp_id, 'HN3')
                        if len(_atom_list) == 3:
                            atom_list, ambiguity_code, details = _atom_list, 1, None
                            return (atom_list, ambiguity_code, details)

                if atom_id.startswith("HN'") and comp_id in ('DA', 'DT', 'DG', 'DC', 'DI', 'DU', 'DNR', 'A', 'T', 'G', 'C', 'U', 'CH'):
                    nh2 = self.__ccU.getRepAminoProtons(comp_id)
                    if len(nh2) == 1:
                        if atom_id.endswith("''"):
                            nh2 = self.__ccU.getNonRepAminoProtons(comp_id)
                            if self.validate_comp_atom(comp_id, nh2[0]):
                                atom_list, ambiguity_code, details = nh2[0], 1, None
                                return (atom_list, ambiguity_code, details)
                        elif self.validate_comp_atom(comp_id, nh2[0]):
                            atom_list, ambiguity_code, details = nh2[0], 1, None
                            return (atom_list, ambiguity_code, details)
                    elif atom_id == "HN'":
                        nh = self.__ccU.getImideProtons(comp_id)
                        if len(nh) == 1:
                            atom_list, ambiguity_code, details = nh[0], 1, None
                            return (atom_list, ambiguity_code, details)

                if atom_id == 'HY' and comp_id == 'ILE':  # 2l9i, AMBER
                    atom_list, ambiguity_code, details = ['HB', 'HG12', 'HG13'], 4, None
                    return (atom_list, ambiguity_code, details)

                if atom_id[-1] == '+' and atom_id[1].isdigit() and len_atom_id > 2 and self.__ccU.updateChemCompDict(comp_id):
                    if self.__ccU.lastChemCompDict['_chem_comp.type'] in ('DNA LINKING', 'RNA LINKING'):  # DAOTHER-9198
                        _atom_list, _ambiguity_code, _details = self.get_valid_star_atom(comp_id, 'HN' + atom_id[1:-1], None, leave_unmatched, methyl_only)
                        if _details is None:
                            atom_list, ambiguity_code, details = _atom_list, _ambiguity_code, _details
                            return (atom_list, ambiguity_code, details)

                if (atom_id.startswith('QH') or atom_id.startswith('MH')) and comp_id in monDict3\
                   and len_atom_id > 2 and not atom_id[2].isdigit():  # 6wqr LEU:QHD# -> LEU:HD#
                    _atom_list, _ambiguity_code, _details = self.get_valid_star_atom(comp_id, atom_id[1:], None, leave_unmatched, methyl_only)
                    if _details is None:
                        atom_list, ambiguity_code, details = _atom_list, _ambiguity_code, _details
                        return (atom_list, ambiguity_code, details)

            atom_list, ambiguity_code, details = self.get_valid_star_atom(comp_id, atom_id, details, leave_unmatched, methyl_only)

            if details is not None and atom_id[-1] not in ('%', '*'):
                _atom_list, _ambiguity_code, _details = self.get_valid_star_atom(comp_id, atom_id + '%', None, leave_unmatched, methyl_only)
                if _details is None:
                    atom_list, ambiguity_code, details = _atom_list, _ambiguity_code, _details
                elif atom_id[0] in protonBeginCode or len_atom_id > 1:
                    atom_list, ambiguity_code, details = self.get_valid_star_atom(comp_id, atom_id + '*', details, leave_unmatched, methyl_only)
                    if details is not None:
                        atom_list, ambiguity_code, details = self.get_valid_star_atom(comp_id, atom_id, details, leave_unmatched, methyl_only)
                        # 2l8r, comp_id=APR, atom_id=Q5D -> ['H5R1', 'H5R2']
                        if details is not None and atom_id[0] in ('Q', 'M'):

                            if atom_id.startswith('QQM'):  # 2n06, comp_id=CM8, atom_id=QQM -> ['HM2%', HM3%']
                                root, _branch = [], []
                                _root = self.__ccU.getBondedAtoms(comp_id, 'C' + atom_id[2:], exclProton=True)
                                if len(_root) > 0:
                                    _branch.append('C' + atom_id[2:])
                                    root.extend(_root)
                                for e in '1234ABCD':
                                    _root = self.__ccU.getBondedAtoms(comp_id, 'C' + atom_id[2:] + e, exclProton=True)
                                    if len(_root) > 0:
                                        _branch.append('C' + atom_id[2:] + e)
                                        root.extend(_root)
                                if len(_root) == 0 and len(_branch) == 0:
                                    _branch = [c for c in self.__ccU.getMethylAtoms(comp_id) if c[0] == 'C']  # 2jnp:QQM
                                if len(_root) == 0 and len(_branch) > 1:
                                    __branch = [cca[self.__ccU.ccaAtomId] for cca in self.__ccU.lastAtomList
                                                if cca[self.__ccU.ccaTypeSymbol] in ('C', 'N')
                                                and cca[self.__ccU.ccaLeavingAtomFlag] == 'N']
                                    if len(__branch) > 0:
                                        _atom_list = []
                                        for k in __branch:
                                            c = self.__ccU.getBondedAtoms(comp_id, k, exclProton=True)
                                            if any(b in c for b in _branch):
                                                protons = []
                                                for b in _branch:
                                                    if b in c:
                                                        protons.extend(self.__ccU.getBondedAtoms(comp_id, b, onlyProton=True))
                                                if len(protons) == 6:
                                                    _atom_list.extend(protons)
                                        if len(_atom_list) > 0:
                                            atom_list, ambiguity_code, details = _atom_list, 2, None
                                            return (atom_list, ambiguity_code, details)

                            protons = self.__ccU.getBondedAtoms(comp_id, 'C' + atom_id[1:], onlyProton=True)
                            resolved = False
                            len_protons = len(protons)
                            if len_protons in (1, 3):
                                atom_list, ambiguity_code, details = protons, 1, None
                                resolved = True
                            elif len_protons == 2:
                                atom_list, ambiguity_code, details = protons, 2, None
                                resolved = True
                            if not resolved:
                                protons = self.__ccU.getBondedAtoms(comp_id, 'N' + atom_id[1:], onlyProton=True)
                                len_protons = len(protons)
                                if len_protons in (1, 3):
                                    atom_list, ambiguity_code, details = protons, 1, None
                                elif len_protons == 2:
                                    atom_list, ambiguity_code, details = protons, 2, None
                            if atom_id.startswith('QQ') and self.__ccU.updateChemCompDict(comp_id):
                                root, _branch = [], []
                                _root = self.__ccU.getBondedAtoms(comp_id, 'C' + atom_id[2:], exclProton=True)
                                if len(_root) > 0:
                                    _branch.append('C' + atom_id[2:])
                                    root.extend(_root)
                                for e in '123ABC':
                                    _root = self.__ccU.getBondedAtoms(comp_id, 'C' + atom_id[2:] + e, exclProton=True)
                                    if len(_root) > 0:
                                        _branch.append('C' + atom_id[2:] + e)
                                        root.extend(_root)
                                _root = self.__ccU.getBondedAtoms(comp_id, 'N' + atom_id[2:], exclProton=True)
                                if len(_root) > 0:
                                    _branch.append('N' + atom_id[2:])
                                    root.extend(_root)
                                for e in '123ABC':
                                    _root = self.__ccU.getBondedAtoms(comp_id, 'N' + atom_id[2:] + e, exclProton=True)
                                    if len(_root) > 0:
                                        _branch.append('N' + atom_id[2:] + e)
                                        root.extend(_root)
                                protons = []
                                aliphatic = True
                                if len(root) > 0:
                                    aliphatic = True
                                    for k, v in collections.Counter(root).most_common():
                                        if v != 2:
                                            continue
                                        cca = next((cca for cca in self.__ccU.lastAtomList if cca[self.__ccU.ccaAtomId] == k and cca[self.__ccU.ccaLeavingAtomFlag] == 'N'), None)
                                        if cca is not None:
                                            if cca[self.__ccU.ccaAromaticFlag] == 'Y':
                                                aliphatic = False
                                        branch = [branch for branch in self.__ccU.getBondedAtoms(comp_id, k, exclProton=True) if branch in _branch]
                                        if len(branch) == 2:
                                            for b in branch:
                                                protons.extend(self.__ccU.getBondedAtoms(comp_id, b, onlyProton=True))
                                else:  # 2mlm
                                    for cca in self.__ccU.lastAtomList:
                                        if cca[self.__ccU.ccaTypeSymbol] in ('C', 'N'):
                                            _root = cca[self.__ccU.ccaAtomId]
                                            for proton in self.__ccU.getBondedAtoms(comp_id, _root, onlyProton=True):
                                                if proton.startswith('H' + atom_id[2:]):
                                                    root.append(_root)
                                                    break
                                    for k, v in collections.Counter(root).most_common():
                                        if v != 1:
                                            continue
                                        cca = next((cca for cca in self.__ccU.lastAtomList if cca[self.__ccU.ccaAtomId] == k and cca[self.__ccU.ccaLeavingAtomFlag] == 'N'), None)
                                        if cca is not None:
                                            if cca[self.__ccU.ccaAromaticFlag] == 'Y':
                                                aliphatic = False
                                            protons.extend(self.__ccU.getBondedAtoms(comp_id, k, onlyProton=True))
                                len_protons = len(protons)
                                if len_protons in (4, 6):
                                    atom_list, ambiguity_code, details = protons, 2 if aliphatic else 3, None
                                    resolved = True
                        # 5lig, comp_id=6XM, atom_id=HA' -> ["HA1'", "HA2'"]
                        # c' should not be propagated: peak list (5z80. D_1300006579_nmr-peaks-upload_P2.dat.V5)
                        # c7' should be allowed: 6gpi, Dihedral_res.tbl
                        elif details is not None and atom_id.endswith("'") and not atom_id.endswith("''") and (atom_id[0] in protonBeginCode or atom_id[1].isdigit()):
                            _atom_list, _ambiguity_code, _details = self.get_valid_star_atom(comp_id, atom_id[:-1] + "%'", None, leave_unmatched, methyl_only)
                            if _details is None:
                                atom_list, ambiguity_code, details = _atom_list, _ambiguity_code, _details

            return (atom_list, ambiguity_code, details)

        finally:
            _atom_list = copy.deepcopy(atom_list)
            self.__cachedDictForValidStarAtomInXplor[key] = (_atom_list, ambiguity_code, details)
            if leave_unmatched:
                key = (comp_id, atom_id, details, False, methyl_only)
                self.__cachedDictForValidStarAtomInXplor[key] = (_atom_list, ambiguity_code, details)

    def get_valid_star_atom(self, comp_id: str, atom_id: str, details: Optional[str] = None, leave_unmatched: bool = True, methyl_only: bool = False
                            ) -> Tuple[List[str], Optional[int], Optional[str]]:
        """ Return lists of atom ID, ambiguity_code, details in IUPAC atom nomenclature for a given conventional NMR atom name.
            @author: Masashi Yokochi
            @return: list of instanced atom_id, ambiguity_code, and description
        """

        if comp_id in emptyValue or atom_id in emptyValue:
            return [], None, None

        nucleotide = self.__csStat.getTypeOfCompId(comp_id)[1]

        methyl_only |= atom_id[0] == 'M' or atom_id.startswith('HM') or atom_id.startswith('QM') or atom_id.startswith('QQM')
        # if comp_id == 'ACE' and atom_id.startswith('Q'):
        #     atom_id = 'H%'
        #     methyl_only = True

        key = (comp_id, atom_id, details, leave_unmatched, methyl_only)
        if key in self.__cachedDictForValidStarAtom:
            return copy.deepcopy(self.__cachedDictForValidStarAtom[key])

        atom_list = []
        ambiguity_code = details = None

        try:

            # DAOTHER-10105: resolve pseudo atom name of non-standard residue
            if comp_id not in monDict3 and self.authAtomNameToId is not None and comp_id in self.authAtomNameToId\
               and not self.__annotation_mode:  # and atom_id[0] in ('Q', 'M'):
                _atom_id = atom_id
                if _atom_id[0] in ('Q', 'M'):
                    _atom_id = 'H' + atom_id[1:] + '*'
                coord_atom_site = {'atom_id': list(self.authAtomNameToId[comp_id].values()),
                                   'alt_atom_id': list(self.authAtomNameToId[comp_id].keys())}
                _atom_list, _ambiguity_code, _details = self.get_star_atom_for_ligand_remap(comp_id, _atom_id, details, coord_atom_site, methyl_only)
                if len(_atom_list) > 0 and _atom_list[0][-1] not in ('%', '*') and _atom_list[0] in coord_atom_site['atom_id']:
                    atom_list, ambiguity_code, details = _atom_list, _ambiguity_code, _details
                    return (atom_list, ambiguity_code, details)

            if '#' in atom_id:
                atom_id = atom_id.replace('#', '%')

            if atom_id.endswith('%%'):
                atom_id = atom_id.replace('%%', '%')

            if (atom_id == 'HN' or atom_id.endswith('%') or atom_id.endswith('*')) and not (isLikePheOrTyr(comp_id, self.__ccU) and atom_id in ('HR', 'HR%', 'HR*')):
                atom_list, ambiguity_code, details = self.get_star_atom(comp_id, atom_id, details, leave_unmatched, methyl_only)
                return (atom_list, ambiguity_code, details)

            len_atom_id = len(atom_id)

            if atom_id[0] == 'M' or ((atom_id[0] == 'Q'
                                      or (isLikePheOrTyr(comp_id, self.__ccU) and atom_id in ('HR', 'HR%', 'HR*'))) and self.__remediation_mode):  # DAOTHER-8663, 8751

                if atom_id.startswith('QQM'):  # 2n06, comp_id=CM8, atom_id=QQM -> ['HM2%', HM3%']
                    root, _branch = [], []
                    _root = self.__ccU.getBondedAtoms(comp_id, 'C' + atom_id[2:], exclProton=True)
                    if len(_root) > 0:
                        _branch.append('C' + atom_id[2:])
                        root.extend(_root)
                    for e in '1234ABCD':
                        _root = self.__ccU.getBondedAtoms(comp_id, 'C' + atom_id[2:] + e, exclProton=True)
                        if len(_root) > 0:
                            _branch.append('C' + atom_id[2:] + e)
                            root.extend(_root)
                    if len(_root) == 0 and len(_branch) == 0:
                        _branch = [c for c in self.__ccU.getMethylAtoms(comp_id) if c[0] == 'C']  # 2jnp:QQM
                    if len(_root) == 0 and len(_branch) > 1:
                        __branch = [cca[self.__ccU.ccaAtomId] for cca in self.__ccU.lastAtomList
                                    if cca[self.__ccU.ccaTypeSymbol] in ('C', 'N')
                                    and cca[self.__ccU.ccaLeavingAtomFlag] == 'N']
                        if len(__branch) > 0:
                            _atom_list = []
                            for k in __branch:
                                c = self.__ccU.getBondedAtoms(comp_id, k, exclProton=True)
                                if any(b in c for b in _branch):
                                    protons = []
                                    for b in _branch:
                                        if b in c:
                                            protons.extend(self.__ccU.getBondedAtoms(comp_id, b, onlyProton=True))
                                    if len(protons) == 6:
                                        _atom_list.extend(protons)
                            if len(_atom_list) > 0:
                                atom_list, ambiguity_code, details = _atom_list, 2, None
                                return (atom_list, ambiguity_code, details)

                if atom_id.startswith('QQ'):
                    atom_list, ambiguity_code, details = self.get_star_atom(comp_id, 'H' + atom_id[2:] + ('%' if nucleotide else '*'),
                                                                            details, leave_unmatched, methyl_only)
                    if details is not None and comp_id not in monDict3 and self.__csStat.peptideLike(comp_id)\
                       and atom_id[2] in ('A', 'B', 'G', 'D', 'E', 'Z', 'H'):
                        grk_atoms = self.__ccU.getAtomsBasedOnGreekLetterSystem(comp_id, 'H' + atom_id[2])
                        if len(grk_atoms) > 0:
                            atom_list = []
                            details = None
                            for grk_atom in grk_atoms:
                                _atom_list, ambiguity_code, details = self.get_star_atom(comp_id, grk_atom, details, leave_unmatched, methyl_only)
                                atom_list.extend(_atom_list)
                            if len(atom_list) >= 4:
                                return (atom_list, ambiguity_code, details)
                    if len(atom_list) >= 4:
                        return (atom_list, ambiguity_code, details)

                if atom_id.startswith('HR') or atom_id.startswith('QR') or atom_id.startswith('QX'):
                    qr_atoms = sorted(set(atom_id[:-1] + '%' for atom_id in self.__csStat.getAromaticAtoms(comp_id)
                                          if atom_id[0] in protonBeginCode and self.__csStat.getMaxAmbigCodeWoSetId(comp_id, atom_id) == 3))
                    if len(qr_atoms) == 0:
                        return (atom_list, ambiguity_code, details)
                    atom_list = []
                    details = None
                    for qr_atom in qr_atoms:
                        _atom_list, ambiguity_code, details = self.get_star_atom(comp_id, qr_atom, details, leave_unmatched, methyl_only)
                        atom_list.extend(_atom_list)
                    if len(atom_list) >= 4:
                        return (atom_list, ambiguity_code, details)

                if atom_id in ('QCD', 'QCE') and isLikePheOrTyr(comp_id, self.__ccU):  # 2js7 - peak list
                    atom_list, ambiguity_code, details = self.get_star_atom(comp_id, atom_id[1:] + '%', details, leave_unmatched, methyl_only)
                    if len(atom_list) > 1:
                        return (atom_list, ambiguity_code, details)

                if comp_id in monDict3 and atom_id.upper() == 'ME':
                    rep_methyl_protons = self.__csStat.getRepMethylProtons(comp_id)
                    if len(rep_methyl_protons) == 1:
                        atom_list, ambiguity_code, details = self.__csStat.getProtonsInSameGroup(comp_id, rep_methyl_protons[0]), 1, None
                        return (atom_list, ambiguity_code, details)

                if atom_id.startswith('Q') or atom_id.startswith('M'):
                    min_len = 4 if atom_id.startswith('QQ') else 1  # ILE/LEU/THR:QB -> HB (2m6i), MG -> Magnesium (2n3r)
                    if atom_id[-1].isalnum():
                        atom_list, ambiguity_code, details = self.get_star_atom(comp_id, 'H' + atom_id[1:] + ('%' if nucleotide else '*'),
                                                                                details, leave_unmatched, methyl_only)
                        if details is not None and comp_id not in monDict3 and self.__csStat.peptideLike(comp_id) and len_atom_id > 1\
                           and atom_id[1] in ('A', 'B', 'G', 'D', 'E', 'Z', 'H'):
                            grk_atoms = self.__ccU.getAtomsBasedOnGreekLetterSystem(comp_id, 'H' + atom_id[1])
                            if len(grk_atoms) > 0:
                                atom_list = []
                                details = None
                                for grk_atom in grk_atoms:
                                    _atom_list, ambiguity_code, details = self.get_star_atom(comp_id, grk_atom, details, leave_unmatched, methyl_only)
                                    atom_list.extend(_atom_list)
                                if len(atom_list) >= min_len:
                                    return (atom_list, ambiguity_code, details)
                        if details is None and len(atom_list) == 1:
                            atom_list = self.__ccU.getProtonsInSameGroup(comp_id, atom_list[0])
                        if len(atom_list) >= min_len:
                            return (atom_list, ambiguity_code, details)
                    if comp_id not in monDict3 and self.authAtomNameToId is not None and comp_id in self.authAtomNameToId\
                       and not self.__annotation_mode and atom_id in self.authAtomNameToId[comp_id].values():
                        pass  # Reconciled fix for DAOTHER-10105 and D-1300057999, 'MN' should not be mapped to 'HN%' because real 'MN' exists
                    else:
                        atom_list, ambiguity_code, details =\
                            self.get_star_atom(comp_id, 'H' + (atom_id[1:] if len(atom_id) < 3 else atom_id[1:-1]) + '*', details, leave_unmatched, methyl_only)
                        if details is None and len(atom_list) == 1:
                            atom_list = self.__ccU.getProtonsInSameGroup(comp_id, atom_list[0])
                        if len(atom_list) >= min_len:
                            return (atom_list, ambiguity_code, details)

            if len_atom_id > 2 and ((atom_id + '2' in self.__csStat.getAllAtoms(comp_id)) or (atom_id + '22' in self.__csStat.getAllAtoms(comp_id))):
                atom_list, ambiguity_code, details = self.get_star_atom(comp_id, atom_id + '%', details, leave_unmatched, methyl_only)
                return (atom_list, ambiguity_code, details)

            atom_list, ambiguity_code, details = self.get_star_atom(comp_id, atom_id, details, leave_unmatched, methyl_only)

            if details is not None and atom_id[-1] not in ('%', '*'):
                _atom_list, _ambiguity_code, _details = self.get_star_atom(comp_id, atom_id + '*', None, leave_unmatched, methyl_only)
                if _details is None:
                    atom_list, ambiguity_code, details = _atom_list, _ambiguity_code, _details

            if details is not None and comp_id not in monDict3 and self.__csStat.peptideLike(comp_id) and atom_id[0] in ('H', 'C', 'N', 'O', 'P')\
               and len_atom_id > 1 and atom_id[1] in ('A', 'B', 'G', 'D', 'E', 'Z', 'H')\
               and (atom_id[0] != 'H' or (atom_id[0] == 'H' and atom_id[-1] not in ('%', '*') and not (atom_id[-1].isdigit() and atom_id[-2].isdigit()))):
                grk_atoms = self.__ccU.getAtomsBasedOnGreekLetterSystem(comp_id, atom_id)
                if len(grk_atoms) > 0:
                    atom_list = []
                    for grk_atom in grk_atoms:
                        _atom_list, ambiguity_code, details = self.get_star_atom(comp_id, grk_atom, None, leave_unmatched, methyl_only)
                        atom_list.extend(_atom_list)

            if details is not None and self.__csStat.peptideLike(comp_id) and len_atom_id > 2 and atom_id[1] in ('A', 'B', 'G', 'D', 'E', 'Z', 'H'):
                if atom_id[2] in ('A', 'B'):
                    _details = None
                    for n in ['1', '2'] if atom_id[2] == 'A' else ['3', '2']:
                        _atom_id = atom_id[:2] + n + (atom_id[3:] if len_atom_id > 3 else '')
                        _atom_list, _ambiguity_code, _details = self.get_star_atom(comp_id, _atom_id, None, leave_unmatched, methyl_only)
                        if _details is None:
                            atom_list, ambiguity_code, details = _atom_list, _ambiguity_code, _details
                            break
                    if _details is not None:
                        _atom_id = atom_id[:2] + (atom_id[3:] if len_atom_id > 3 else '')
                        _atom_list, _ambiguity_code, _details = self.get_star_atom(comp_id, _atom_id, None, leave_unmatched, methyl_only)
                        if _details is None:
                            atom_list, ambiguity_code, details = _atom_list, _ambiguity_code, _details
                elif len_atom_id > 3 and atom_id[3] in ('A', 'B'):
                    for n in ['1', '2'] if atom_id[3] == 'A' else ['3', '2']:
                        _atom_id = atom_id[:3] + n + (atom_id[4:] if len_atom_id > 4 else '')
                        _atom_list, _ambiguity_code, _details = self.get_star_atom(comp_id, _atom_id, None, leave_unmatched, methyl_only)
                        if _details is None:
                            atom_list, ambiguity_code, details = _atom_list, _ambiguity_code, _details
                            break

            return (atom_list, ambiguity_code, details)

        finally:
            _atom_list = copy.deepcopy(atom_list)
            self.__cachedDictForValidStarAtom[key] = (_atom_list, ambiguity_code, details)
            if leave_unmatched:
                key = (comp_id, atom_id, details, False, methyl_only)
                self.__cachedDictForValidStarAtom[key] = (_atom_list, ambiguity_code, details)

    def get_star_atom(self, comp_id: str, nef_atom: str, details: Optional[str] = None, leave_unmatched: bool = True, methyl_only: bool = False
                      ) -> Tuple[List[str], Optional[int], Optional[str]]:
        """ Return list of instanced atom_id of a given NEF atom (including wildcard codes) and its ambiguity code.
            @change: support non-standard residue by Masashi Yokochi
            @change: rename the original get_nmrstar_atom() to get_star_atom() by Masashi Yokochi
            @return: list of instanced atom_id of a given NEF atom, ambiguity_code, and description
        """

        if comp_id in emptyValue:
            return [], None, None

        key = (comp_id, nef_atom, details, leave_unmatched, methyl_only)
        if key in self.__cachedDictForStarAtom:
            return copy.deepcopy(self.__cachedDictForStarAtom[key])

        comp_id = comp_id.upper()
        is_std_comp_id = comp_id in monDict3

        atom_list, atoms, methyl_atoms = [], [], []
        ambiguity_code = 1

        try:

            # DAOTHER-10105: resolve pseudo atom name of non-standard residue
            if not is_std_comp_id and self.authAtomNameToId is not None and comp_id in self.authAtomNameToId\
               and not self.__annotation_mode:  # and nef_atom[0] in ('%', '*'):
                coord_atom_site = {'atom_id': list(self.authAtomNameToId[comp_id].values()),
                                   'alt_atom_id': list(self.authAtomNameToId[comp_id].keys())}
                _atom_list, _ambiguity_code, _details = self.get_star_atom_for_ligand_remap(comp_id, nef_atom, details, coord_atom_site, methyl_only)
                if len(_atom_list) > 0 and _atom_list[0][-1] not in ('%', '*') and _atom_list[0] in coord_atom_site['atom_id']:
                    atom_list, ambiguity_code, details = _atom_list, _ambiguity_code, _details
                    return (atom_list, ambiguity_code, details)

            if self.__ccU.updateChemCompDict(comp_id):
                cc_rel_status = self.__ccU.lastChemCompDict['_chem_comp.pdbx_release_status']

                if cc_rel_status == 'REL':
                    methyl_atoms = self.__csStat.getMethylAtoms(comp_id)
                    not_methyl = not methyl_only or nef_atom[0] not in protonBeginCode or len(methyl_atoms) == 0
                    atoms = [a[self.__ccU.ccaAtomId] for a in self.__ccU.lastAtomList
                             if not_methyl or (not not_methyl and a[self.__ccU.ccaAtomId] in methyl_atoms)]
                    alt_atom_dict = {a[self.__ccU.ccaAltAtomId]: a[self.__ccU.ccaAtomId] for a in self.__ccU.lastAtomList
                                     if not_methyl or (not not_methyl and a[self.__ccU.ccaAtomId] in methyl_atoms)
                                     and a[self.__ccU.ccaAltAtomId] != a[self.__ccU.ccaAtomId]}
                    if nef_atom not in atoms and nef_atom in alt_atom_dict:
                        nef_atom = alt_atom_dict[nef_atom]

                # DAOTHER-8817
                elif self.chemCompAtom is not None and comp_id in self.chemCompAtom:
                    atoms = copy.copy(self.chemCompAtom[comp_id])

                    for v in self.chemCompBond[comp_id].values():
                        if len(v) == 3:
                            methyl_atoms.extend(v)

                else:
                    methyl_atoms = self.__csStat.getMethylAtoms(comp_id)
                    not_methyl = not methyl_only or nef_atom[0] not in protonBeginCode or len(methyl_atoms) == 0
                    atoms = [a[self.__ccU.ccaAtomId] for a in self.__ccU.lastAtomList
                             if not_methyl or (not not_methyl and a[self.__ccU.ccaAtomId] in methyl_atoms)]

            else:

                if self.chemCompAtom is not None and comp_id in self.chemCompAtom:
                    atoms = copy.copy(self.chemCompAtom[comp_id])

                    for v in self.chemCompBond[comp_id].values():
                        if len(v) == 3:
                            methyl_atoms.extend(v)

                if leave_unmatched:
                    details = f"Unknown non-standard residue {comp_id} found."
                elif self.__verbose:
                    self.__lfh.write(f"+{self.__class_name__}.get_star_atom() ++ Error  - Unknown non-standard residue {comp_id} found.\n")

            if self.__csStat.getTypeOfCompId(comp_id)[1]:
                if "'" in nef_atom:
                    atoms = [a for a in atoms if "'" in a]
                else:
                    _nef_atom = translateToStdAtomName(nef_atom, refCompId=comp_id, ccU=self.__ccU)
                    if len(_nef_atom) > 1 and len(nef_atom) > 1 and _nef_atom[1] != nef_atom[1]:
                        atoms = [a for a in atoms if "'" not in a]
                    else:
                        for min_len in range(min(len(nef_atom), 3), 2, -1):
                            if "'" not in nef_atom and any("'" not in a for a in atoms if a.startswith(nef_atom[:min_len])):
                                atoms = [a for a in atoms if "'" not in a]
                                break
                            if any("'" in a for a in atoms if a.startswith(nef_atom[:min_len])):
                                atoms = [a for a in atoms if "'" in a]
                                break
                            if any("'" not in a for a in atoms if a.startswith(nef_atom[:min_len])):
                                atoms = [a for a in atoms if "'" not in a]
                                break
                        else:
                            if not nef_atom.startswith('H2') and not nef_atom.startswith('H5'):  # 2l5d
                                if "'" not in nef_atom:
                                    if nef_atom[:2] not in ('H1', 'H3', 'H4')\
                                       or not any(a for a in atoms if "'" not in a and a.startswith(nef_atom[:2])):  # 2lzv
                                        atoms = [a for a in atoms if "'" not in a]
                                else:
                                    atoms = [a for a in atoms if "'" in a]

            try:

                # DAOTHER-8817: guess ambiguity code from pseudo CCD
                def guess_ambiguity_code(atom_list):
                    if self.chemCompBond is not None and comp_id in self.chemCompBond:
                        for k, v in self.chemCompBond[comp_id].items():
                            if atom_list[0] in v:
                                len_v = len(v)
                                if len_v == 2:
                                    return 2  # methylene/amino
                                if len_v == 1:
                                    if k[0] == 'C' and self.chemCompTopo is not None and comp_id in self.chemCompTopo\
                                       and any(len(tv) == 2 and tv[0][0] == 'C' and tv[1][0] == 'C'
                                               for tk, tv in self.chemCompTopo[comp_id].items() if tk == k):
                                        return 3  # aromatic opposite
                                    return 1
                    return None

                ref_atom = re.findall(r'([^ \t\r\n\f\v\(\)\{\}\[\]]+)([xyXY])([%*])$'
                                      r'|([^ \t\r\n\f\v\(\)\{\}\[\]]+)([%*])$|([^ \t\r\n\f\v\(\)\{\}\[\]]+)([xyXY]$)'
                                      r'|([%*])([^ \t\r\n\f\v\(\)\{\}\[\]]+)', nef_atom)[0]

                atm_set = [ref_atom.index(a) for a in ref_atom if a != '']

                pattern = None

                if atm_set == [0, 1, 2]:  # endswith [xyXY][%*]

                    atom_type = ref_atom[0]
                    xy_code = ref_atom[1].lower()

                    len_atom_type = len(atom_type)

                    pattern = re.compile(fr'{atom_type}\S\d+')

                    alist2 = [a for a in atoms
                              if re.match(pattern, a) and a[len_atom_type].isdigit()]  # bmrb_id: 15879, pdb_id: 2k6r, comp_id: DNS

                    xid = sorted(set(int(a[len_atom_type]) for a in alist2))

                    # DAOTHER-8817: select proper atom groups
                    xid_count = {}
                    for _xid in xid:
                        xid_count[_xid] = len([a for a in alist2 if int(a[len_atom_type]) == _xid])
                    _xid_count = next((k for k, v in collections.Counter(xid_count.values()).most_common() if v == 2), None)
                    if _xid_count is None:
                        _xid_count = next((k for k, v in collections.Counter(xid_count.values()).most_common() if v == 1), None)
                    xid = [k for k, v in xid_count.items() if v == _xid_count]

                    if xy_code == 'x':
                        atom_list = [a for a in alist2 if int(a[len_atom_type]) == xid[0]]
                        if len(atom_list) > 3:  # bmrb_id: 15879, pdb_id: 2k6r, comp_id: DNS
                            atom_list[3:] = []

                    else:
                        atom_list = [a for a in alist2 if int(a[len_atom_type]) == xid[1]]
                        if len(atom_list) > 3:  # bmrb_id: 15879, pdb_id: 2k6r, comp_id: DNS
                            atom_list[3:] = []

                    ambiguity_code = self.__csStat.getMaxAmbigCodeWoSetId(comp_id, atom_list[0])

                    # DAOTHER-8817: guess ambiguity code from pseudo CCD
                    if ambiguity_code == 0:
                        ambiguity_code = min([len(xid), 2]) if atom_list[0] in methyl_atoms else guess_ambiguity_code(atom_list)

                elif atm_set == [3, 4]:  # endswith [%*] but neither [xyXY][%*]

                    atom_type = _atom_type = ref_atom[3]
                    wc_code = ref_atom[4]

                    if atom_type[0] not in ('%', '*'):
                        # DAOTHER-8817: H\S*[xyXY]\S+[%*]
                        if atom_type[0] in protonBeginCode and ('X' in atom_type or 'Y' in atom_type or 'x' in atom_type or 'y' in atom_type):
                            _atom_type = atom_type.replace('X', '').replace('Y', '').replace('x', '').replace('y', '')
                            if wc_code == '%':
                                pattern = re.compile(fr'{_atom_type}\d+') if is_std_comp_id else re.compile(fr'{_atom_type}\S?$')
                            elif wc_code == '*':
                                pattern = re.compile(fr'{_atom_type}\S+')
                            elif self.__verbose:
                                self.__lfh.write(f"+{self.__class_name__}.get_star_atom() ++ Error  - Invalid NEF atom nomenclature {nef_atom} found.\n")
                        elif wc_code == '%':
                            pattern = re.compile(fr'{atom_type}\d+') if is_std_comp_id else re.compile(fr'{atom_type}\S?$')
                        elif wc_code == '*':
                            pattern = re.compile(fr'{atom_type}\S+')
                        elif self.__verbose:
                            self.__lfh.write(f"+{self.__class_name__}.get_star_atom() ++ Error  - Invalid NEF atom nomenclature {nef_atom} found.\n")
                    else:
                        _wc_code = atom_type[0]
                        atom_type = atom_type[1:]

                        if _wc_code == '%':
                            if wc_code == '%':
                                pattern = re.compile(fr'\d+{atom_type}\d+') if is_std_comp_id else re.compile(fr'\S?{atom_type}\S?$')
                            elif wc_code == '*':
                                pattern = re.compile(fr'\d+{atom_type}\S+') if is_std_comp_id else re.compile(fr'\S?{atom_type}\S+$')
                            elif self.__verbose:
                                self.__lfh.write(f"+{self.__class_name__}.get_star_atom() ++ Error  - Invalid NEF atom nomenclature {nef_atom} found.\n")
                        elif _wc_code == '*':
                            if wc_code == '%':
                                pattern = re.compile(fr'\S+{atom_type}\d+') if is_std_comp_id else re.compile(fr'\S+{atom_type}\S?$')
                            elif wc_code == '*':
                                pattern = re.compile(fr'\S+{atom_type}\S+')
                            elif self.__verbose:
                                self.__lfh.write(f"+{self.__class_name__}.get_star_atom() ++ Error  - Invalid NEF atom nomenclature {nef_atom} found.\n")
                        elif self.__verbose:
                            self.__lfh.write(f"+{self.__class_name__}.get_star_atom() ++ Error  - Invalid NEF atom nomenclature {nef_atom} found.\n")

                    atom_list = [a for a in atoms if re.match(pattern, a) and nef_atom[0] in ('H', '1', '2', '3', a[0])]

                    if not is_std_comp_id and self.__csStat.peptideLike(comp_id) and any(a in aminoProtonCode for a in atom_list)\
                       and any(a not in aminoProtonCode for a in atom_list):
                        atom_list = [a for a in atom_list if a not in aminoProtonCode]  # ACA:H21, H22, H2 (5nwu)

                    if atom_type != _atom_type and self.chemCompBond is not None and comp_id in self.chemCompBond:
                        _atom_list = []
                        for a in atom_list:
                            for v in self.chemCompBond[comp_id].values():
                                if a in v and len(v) > 1:
                                    _atom_list.extend(v)

                        if len(_atom_list) > 0:
                            atom_list = _atom_list

                    ambiguity_code = 1 if atom_list[0] in methyl_atoms else self.__csStat.getMaxAmbigCodeWoSetId(comp_id, atom_list[0])

                    # DAOTHER-8817: guess ambiguity code from pseudo CCD
                    if ambiguity_code == 0:
                        ambiguity_code = guess_ambiguity_code(atom_list)

                elif atm_set == [5, 6]:  # endswith [xyXY]

                    atom_type = ref_atom[5]
                    xy_code = ref_atom[6].lower()

                    pattern = re.compile(fr'{atom_type}[^\']+')

                    atom_list = [a for a in atoms if re.match(pattern, a)]

                    atom_list_len = len(atom_list)

                    if atom_list_len != 2:
                        if atom_list_len > 2:
                            atom_list = []
                    elif xy_code == 'y':
                        atom_list = atom_list[-1:]
                    elif xy_code == 'x':
                        atom_list = atom_list[:1]
                    elif self.__verbose:
                        self.__lfh.write(f"+{self.__class_name__}.get_star_atom() ++ Error  - Invalid NEF atom nomenclature {nef_atom} found.\n")

                    ambiguity_code = self.__csStat.getMaxAmbigCodeWoSetId(comp_id, atom_list[0])

                    # DAOTHER-8817: guess ambiguity code from pseudo CCD
                    if ambiguity_code == 0:
                        ambiguity_code = guess_ambiguity_code(atom_list)

                elif atm_set == [7, 8]:  # startswith [%*]

                    atom_type = ref_atom[8]
                    wc_code = ref_atom[7]

                    if wc_code == '%':
                        pattern = re.compile(fr'\d+{atom_type}') if is_std_comp_id else re.compile(fr'\S?{atom_type}')
                    elif wc_code == '*':
                        pattern = re.compile(fr'\S+{atom_type}')
                    elif self.__verbose:
                        self.__lfh.write(f"+{self.__class_name__}.get_star_atom() ++ Error  - Invalid NEF atom nomenclature {nef_atom} found.\n")

                    atom_list = [a for a in atoms if re.match(pattern, a)]

                    if not is_std_comp_id and self.__csStat.peptideLike(comp_id) and any(a in aminoProtonCode for a in atom_list)\
                       and any(a not in aminoProtonCode for a in atom_list):
                        atom_list = [a for a in atom_list if a not in aminoProtonCode]  # ACA:H21, H22, H2 (5nwu)

                    ambiguity_code = 1 if atom_list[0] in methyl_atoms else self.__csStat.getMaxAmbigCodeWoSetId(comp_id, atom_list[0])

                    # DAOTHER-8817: guess ambiguity code from pseudo CCD
                    if ambiguity_code == 0:
                        ambiguity_code = guess_ambiguity_code(atom_list)

                elif self.__verbose:
                    self.__lfh.write(f"+{self.__class_name__}.get_star_atom() ++ Error  - Invalid NEF atom nomenclature {nef_atom} found.\n")

            except IndexError:
                pass

            if len(atom_list) == 0:

                if self.__csStat.peptideLike(comp_id):
                    if nef_atom == 'HN':
                        atom_list, ambiguity_code, details = self.get_star_atom(comp_id, 'H', None,
                                                                                leave_unmatched)
                        return (atom_list, ambiguity_code, details)
                    if nef_atom == 'CO':
                        atom_list, ambiguity_code, details = self.get_star_atom(comp_id, 'C', None,
                                                                                leave_unmatched)
                        return (atom_list, ambiguity_code, details)

                if self.__csStat.hasCompId(comp_id):

                    if is_std_comp_id and not nef_atom.endswith('%') and not nef_atom.endswith('*') and nef_atom + '1' in methyl_atoms:
                        atom_list, ambiguity_code, details =\
                            self.get_star_atom(comp_id, nef_atom + '%', None,
                                               leave_unmatched, methyl_only)
                        return (atom_list, ambiguity_code, details)

                    if nef_atom[-1].lower() == 'x' or nef_atom[-1].lower() == 'y' and nef_atom[:-1] + '1' in methyl_atoms:
                        atom_list, ambiguity_code, details =\
                            self.get_star_atom(comp_id, nef_atom[:-1] + '%', None,
                                               leave_unmatched, methyl_only)
                        return (atom_list, ambiguity_code, details)

                    if ((is_std_comp_id and nef_atom[-1] == '%') or nef_atom[-1] == '*') and (nef_atom[:-1] + '1' not in methyl_atoms) and\
                       len(nef_atom) > 2 and (nef_atom[-2].lower() == 'x' or nef_atom[-2].lower() == 'y'):
                        atom_list, ambiguity_code, details =\
                            self.get_star_atom(comp_id, nef_atom[:-2] + ('1' if nef_atom[-2].lower() == 'x' else '2') + '%', None,
                                               leave_unmatched, methyl_only)
                        return (atom_list, ambiguity_code, details)

                    if ((is_std_comp_id and nef_atom[-1] == '%') or nef_atom[-1] == '*') and nef_atom[:-1] in atoms:
                        atom_list, ambiguity_code, details =\
                            self.get_star_atom(comp_id, nef_atom[:-1], None,
                                               leave_unmatched, methyl_only)
                        return (atom_list, ambiguity_code, details)

                if nef_atom in atoms:
                    atom_list.append(nef_atom)

                else:  # DAOTHER-8817
                    atom_list.append(nef_atom)
                    ambiguity_code = None
                    if leave_unmatched and details is None:
                        details = f"{nef_atom} is an invalid atom name as a residue {comp_id}."

            atom_list = sorted(atom_list)

            return (atom_list, ambiguity_code, details)

        finally:
            _atom_list = copy.deepcopy(atom_list)
            self.__cachedDictForStarAtom[key] = (_atom_list, ambiguity_code, details)
            if leave_unmatched:
                key = (comp_id, nef_atom, details, False, methyl_only)
                self.__cachedDictForStarAtom[key] = (_atom_list, ambiguity_code, details)

    def get_nef_atom(self, comp_id: str, star_atom_list: List[str], details: Optional[str] = None, leave_unmatched: bool = True
                     ) -> Tuple[List[str], Optional[str], Optional[dict]]:
        """ Return list of all instanced atom_id of given NMR-STAR atoms with ambiguity code and CS value in a given comp_id.
            @author: Masashi Yokochi
            @return: list of instanced atom_id of given NMR-STAR atoms, descriptions, and atom conversion dictionary for conversion of other loops
        """

        if comp_id in emptyValue:
            return [], None, None

        comp_id = comp_id.upper()

        key = (comp_id, str(star_atom_list), str(details), leave_unmatched)
        if key in self.__cachedDictForNefAtom:
            return copy.deepcopy(self.__cachedDictForNefAtom[key])

        atom_list, atoms = [], []
        atom_id_map = {}

        try:

            if self.__ccU.updateChemCompDict(comp_id):
                atoms = [a[self.__ccU.ccaAtomId] for a in self.__ccU.lastAtomList]

            methyl_atoms = self.__csStat.getMethylAtoms(comp_id)

            proc_atom_list = set()

            if details is None:
                details = {}

            try:

                for a in star_atom_list:

                    atom_id = a['atom_id']
                    _ambig_code = a['ambig_code']
                    _value = a['value']

                    if atom_id in proc_atom_list:
                        continue

                    if atom_id not in atoms:

                        _atom_id = None

                        if self.__csStat.peptideLike(comp_id):
                            if atom_id == 'HN':
                                _atom_id = 'H'
                            elif atom_id == 'CO':
                                _atom_id = 'C'
                        elif atom_id.startswith('QQ') and self.__remediation_mode:  # DAOTHER-8663
                            _atom_id = 'H' + atom_id[2:] + '*'
                        elif (atom_id in ('HR', 'HR%', 'HR*') or atom_id.startswith('QR') or atom_id.startswith('QX')) and self.__remediation_mode:  # DAOTHER-8663
                            qr_atoms = sorted(set(atom_id[:-1] + '%' for atom_id in self.__csStat.getAromaticAtoms(comp_id)
                                                  if atom_id[0] in protonBeginCode and self.__csStat.getMaxAmbigCodeWoSetId(comp_id, atom_id) == 3))
                            if len(qr_atoms) > 0:
                                for qr_atom in qr_atoms:
                                    _a = copy.copy(a)
                                    _a['atom_id'] = qr_atom
                                    star_atom_list.append(_a)
                                star_atom_list.remove(a)
                                atom_list, details, atom_id_map = self.get_nef_atom(comp_id, star_atom_list, details, leave_unmatched)
                                return (atom_list, details, atom_id_map)
                        elif atom_id.startswith('M') or (atom_id.startswith('Q') and self.__remediation_mode):  # DAOTHER-8663, 8751
                            if atom_id[-1].isalnum():
                                _atom_id = 'H' + atom_id[1:] + '%'
                            else:
                                _atom_id = 'H' + atom_id[1:-1] + '*'
                        elif atom_id + '2' in self.__csStat.getAllAtoms(comp_id):
                            _atom_id = atom_id + '%'

                        if _atom_id is None:

                            if leave_unmatched:
                                atom_list.append(atom_id)
                                if not self.__ccU.lastStatus:
                                    details[atom_id] = f"Unknown non-standard residue {comp_id} found."
                                else:
                                    details[atom_id] = f"{atom_id} is an invalid atom name as a residue {comp_id}."
                                atom_id_map[atom_id] = atom_id
                            elif self.__verbose:
                                if not self.__ccU.lastStatus:
                                    self.__lfh.write(f"+{self.__class_name__}.get_nef_atom() ++ Error  - Unknown non-standard residue {comp_id} found.\n")
                                else:
                                    self.__lfh.write(f"+{self.__class_name__}.get_nef_atom() ++ Error  - Invalid atom nomenclature {atom_id} found.\n")

                            continue

                        atom_id = _atom_id

                    if _ambig_code in emptyValue:
                        ambig_code = self.__csStat.getMaxAmbigCodeWoSetId(comp_id, atom_id)
                        if atom_id.endswith("'"):
                            ambig_code = 1
                    else:
                        ambig_code = int(_ambig_code)

                    if ambig_code not in ALLOWED_AMBIGUITY_CODES:

                        if leave_unmatched:
                            atom_list.append(atom_id)
                            details[atom_id] = f"{atom_id} has invalid ambiguity code {ambig_code}."
                            atom_id_map[atom_id] = atom_id
                        elif self.__verbose:
                            self.__lfh.write(f"+{self.__class_name__}.get_nef_atom() ++ Error  - Invalid ambiguity code {ambig_code} for atom_id {atom_id} found.\n")

                        continue

                    if ambig_code == 1:

                        if atom_id[0] in protonBeginCode and atom_id in methyl_atoms:

                            methyl_c, methyl_h_list = self.get_group(comp_id, atom_id)

                            if methyl_h_list is None:

                                if leave_unmatched:
                                    atom_list.append(atom_id)
                                    details[atom_id] = f"{atom_id} is an invalid atom name as a residue {comp_id}."
                                    atom_id_map[atom_id] = atom_id
                                elif self.__verbose:
                                    self.__lfh.write(f"+{self.__class_name__}.get_nef_atom() ++ Error  - Invalid atom nomenclature {atom_id} found.\n")

                            else:

                                has_methyl_proton = len([_a['atom_id'] for _a in star_atom_list
                                                         if _a['atom_id'] in methyl_h_list and (_a['value'] is None or _a['value'] == _value)]) == 3

                                if has_methyl_proton:

                                    name_len = [len(n) for n in methyl_h_list]
                                    max_len = max(name_len)
                                    min_len = min(name_len)

                                    if max_len == min_len or len(atom_id) == max_len:
                                        nef_atom = atom_id[:-1] + '%'
                                    else:  # For example, HEM HM[A-D]
                                        nef_atom = atom_id + '%'

                                    atom_list.append(nef_atom)
                                    details[nef_atom] = None
                                    for b in methyl_h_list:
                                        atom_id_map[b] = nef_atom
                                        proc_atom_list.add(b)

                                else:
                                    atom_list.append(atom_id)
                                    details[atom_id] = None
                                    atom_id_map[atom_id] = atom_id

                        else:
                            atom_list.append(atom_id)
                            details[atom_id] = None
                            atom_id_map[atom_id] = atom_id

                    elif ambig_code == 2:

                        if self.__csStat.getMaxAmbigCodeWoSetId(comp_id, atom_id) != 2:

                            if leave_unmatched:
                                atom_list.append(atom_id)
                                details[atom_id] = f"{atom_id} has invalid ambiguity code {ambig_code}."
                                atom_id_map[atom_id] = atom_id
                            elif self.__verbose:
                                self.__lfh.write(f"+{self.__class_name__}.get_nef_atom() ++ Error  - Invalid ambiguity code {ambig_code} for atom_id {atom_id} found.\n")

                        elif atom_id[0] in protonBeginCode:

                            if atom_id in methyl_atoms:

                                methyl_c, methyl_h_list = self.get_group(comp_id, atom_id)
                                _, methyl_h_list_2 = self.get_geminal_group(comp_id, methyl_c)

                                if methyl_h_list is None:

                                    if leave_unmatched:
                                        atom_list.append(atom_id)
                                        details[atom_id] = f"{atom_id} is an invalid atom name as a residue {comp_id}."
                                        atom_id_map[atom_id] = atom_id
                                    elif self.__verbose:
                                        self.__lfh.write(f"+{self.__class_name__}.get_nef_atom() ++ Error  - Invalid atom nomenclature {atom_id} found.\n")

                                else:

                                    has_methyl_proton = len([_a['atom_id'] for _a in star_atom_list
                                                             if _a['atom_id'] in methyl_h_list and (_a['value'] is None or _a['value'] == _value)]) == 3
                                    has_methyl_proton_2 = methyl_h_list_2 is not None and len([_a['atom_id'] for _a in star_atom_list
                                                                                               if _a['atom_id'] in methyl_h_list_2
                                                                                               and (_a['value'] is None or _a['value'] == _value)]) == 3

                                    nef_atom_prefix = 'x'
                                    nef_atom_prefix_2 = 'y'

                                    if has_methyl_proton and has_methyl_proton_2:

                                        methyl_proton_value = next((_a['value'] for _a in star_atom_list if _a['atom_id'] in methyl_h_list), None)
                                        methyl_proton_value_2 = next((_a['value'] for _a in star_atom_list if _a['atom_id'] in methyl_h_list_2), None)

                                        if None not in (methyl_proton_value, methyl_proton_value_2)\
                                           and float(methyl_proton_value_2) < float(methyl_proton_value):
                                            nef_atom_prefix = 'y'
                                            nef_atom_prefix_2 = 'x'

                                        nef_atom = methyl_h_list[0][:-2] + nef_atom_prefix + '%'

                                        atom_list.append(nef_atom)
                                        details[nef_atom] = None
                                        for b in methyl_h_list:
                                            atom_id_map[b] = nef_atom
                                            proc_atom_list.add(b)

                                        nef_atom_2 = methyl_h_list_2[0][:-2] + nef_atom_prefix_2 + '%'

                                        atom_list.append(nef_atom_2)
                                        details[nef_atom_2] = None
                                        for b in methyl_h_list_2:
                                            atom_id_map[b] = nef_atom_2
                                            proc_atom_list.add(b)

                                    elif has_methyl_proton:

                                        nef_atom_prefix = 'x' if methyl_h_list[0] < methyl_h_list_2[0] else 'y'
                                        nef_atom = methyl_h_list[0][:-2] + nef_atom_prefix + '%'

                                        atom_list.append(nef_atom)
                                        details[nef_atom] = None
                                        for b in methyl_h_list:
                                            atom_id_map[b] = nef_atom
                                            proc_atom_list.add(b)

                                    else:
                                        atom_list.append(atom_id)
                                        details[atom_id] = None
                                        atom_id_map[atom_id] = atom_id

                            else:

                                _, geminal_h_list = self.get_group(comp_id, atom_id)

                                if geminal_h_list is None:

                                    if leave_unmatched:
                                        atom_list.append(atom_id)
                                        details[atom_id] = f"{atom_id} is an invalid atom name as a residue {comp_id}."
                                        atom_id_map[atom_id] = atom_id
                                    elif self.__verbose:
                                        self.__lfh.write(f"+{self.__class_name__}.get_nef_atom() ++ Error  - Invalid atom nomenclature {atom_id} found.\n")

                                else:

                                    has_geminal_proton = len([_a['atom_id'] for _a in star_atom_list if _a['atom_id'] in geminal_h_list]) == 2

                                    nef_atom_prefix = 'x'
                                    nef_atom_prefix_2 = 'y'

                                    if atom_id.endswith("'"):

                                        atom_list.append(atom_id)
                                        details[atom_id] = None
                                        atom_id_map[atom_id] = atom_id

                                    elif has_geminal_proton:

                                        geminal_proton_value = next((_a['value'] for _a in star_atom_list if _a['atom_id'] == geminal_h_list[0]), None)
                                        geminal_proton_value_2 = next((_a['value'] for _a in star_atom_list if _a['atom_id'] == geminal_h_list[1]), None)

                                        if None not in (geminal_proton_value, geminal_proton_value_2)\
                                           and float(geminal_proton_value_2) < float(geminal_proton_value):
                                            nef_atom_prefix = 'y'
                                            nef_atom_prefix_2 = 'x'

                                        nef_atom = geminal_h_list[0][:-1] + nef_atom_prefix

                                        atom_list.append(nef_atom)
                                        details[nef_atom] = None
                                        atom_id_map[geminal_h_list[0]] = nef_atom

                                        nef_atom_2 = geminal_h_list[1][:-1] + nef_atom_prefix_2

                                        atom_list.append(nef_atom_2)
                                        details[nef_atom_2] = None
                                        atom_id_map[geminal_h_list[1]] = nef_atom_2

                                        for b in geminal_h_list:
                                            proc_atom_list.add(b)

                                    else:

                                        nef_atom_prefix = 'x' if (atom_id == geminal_h_list[0] and geminal_h_list[0] < geminal_h_list[1]) or\
                                                                 (atom_id == geminal_h_list[1] and geminal_h_list[1] < geminal_h_list[0]) else 'y'
                                        nef_atom = atom_id[:-1] + nef_atom_prefix

                                        atom_list.append(nef_atom)
                                        details[nef_atom] = None
                                        atom_id_map[atom_id] = nef_atom

                        else:

                            atom_id_2, _ = self.get_geminal_group(comp_id, atom_id)

                            if atom_id_2 is None:

                                if leave_unmatched:
                                    atom_list.append(atom_id)
                                    details[atom_id] = f"{atom_id} is an invalid atom name as a residue {comp_id}."
                                    atom_id_map[atom_id] = atom_id
                                elif self.__verbose:
                                    self.__lfh.write(f"+{self.__class_name__}.get_nef_atom() ++ Error  - Invalid atom nomenclature {atom_id} found.\n")

                            else:

                                has_atom_id_2 = len([_a['atom_id'] for _a in star_atom_list if _a['atom_id'] == atom_id_2]) == 1

                                nef_atom_prefix = 'x'
                                nef_atom_prefix_2 = 'y'

                                if has_atom_id_2:

                                    atom_id_value = next((_a['value'] for _a in star_atom_list if _a['atom_id'] == atom_id), None)
                                    atom_id_value_2 = next((_a['value'] for _a in star_atom_list if _a['atom_id'] == atom_id_2), None)

                                    if None not in (atom_id_value, atom_id_value_2)\
                                       and float(atom_id_value_2) < float(atom_id_value):
                                        nef_atom_prefix = 'y'
                                        nef_atom_prefix_2 = 'x'

                                    nef_atom = atom_id[:-1] + nef_atom_prefix

                                    atom_list.append(nef_atom)
                                    details[nef_atom] = None
                                    atom_id_map[atom_id] = nef_atom
                                    proc_atom_list.add(atom_id)

                                    nef_atom_2 = atom_id_2[:-1] + nef_atom_prefix_2

                                    atom_list.append(nef_atom_2)
                                    details[nef_atom_2] = None
                                    atom_id_map[atom_id_2] = nef_atom_2
                                    proc_atom_list.add(atom_id_2)

                                else:

                                    nef_atom_prefix = 'x' if atom_id < atom_id_2 else 'y'
                                    nef_atom = atom_id[:-1] + nef_atom_prefix

                                    atom_list.append(nef_atom)
                                    details[nef_atom] = None
                                    atom_id_map[atom_id] = nef_atom

                    elif ambig_code == 3:

                        if self.__csStat.getMaxAmbigCodeWoSetId(comp_id, atom_id) != 3:

                            if leave_unmatched:
                                atom_list.append(atom_id)
                                details[atom_id] = f"{atom_id} has invalid ambiguity code {ambig_code}."
                                atom_id_map[atom_id] = atom_id
                            elif self.__verbose:
                                self.__lfh.write(f"+{self.__class_name__}.get_nef_atom() ++ Error  - Invalid ambiguity code {ambig_code} for atom_id {atom_id} found.\n")

                        else:

                            atom_id_2 = self.__csStat.getGeminalAtom(comp_id, atom_id)

                            if atom_id_2 is None:

                                if leave_unmatched:
                                    atom_list.append(atom_id)
                                    details[atom_id] = f"{atom_id} is an invalid atom name as a residue {comp_id}."
                                    atom_id_map[atom_id] = atom_id
                                elif self.__verbose:
                                    self.__lfh.write(f"+{self.__class_name__}.get_nef_atom() ++ Error  - Invalid atom nomenclature {atom_id} found.\n")

                            else:

                                has_atom_id_2 = len([_a['atom_id'] for _a in star_atom_list if _a['atom_id'] == atom_id_2]) == 1

                                nef_atom_prefix = 'x'
                                nef_atom_prefix_2 = 'y'

                                if has_atom_id_2:

                                    atom_id_value = next((_a['value'] for _a in star_atom_list if _a['atom_id'] == atom_id), None)
                                    atom_id_value_2 = next((_a['value'] for _a in star_atom_list if _a['atom_id'] == atom_id_2), None)

                                    if None not in (atom_id_value, atom_id_value_2)\
                                       and float(atom_id_value_2) < float(atom_id_value):
                                        nef_atom_prefix = 'y'
                                        nef_atom_prefix_2 = 'x'

                                    nef_atom = atom_id[:-1] + nef_atom_prefix

                                    atom_list.append(nef_atom)
                                    details[nef_atom] = None
                                    atom_id_map[atom_id] = nef_atom
                                    proc_atom_list.add(atom_id)

                                    nef_atom_2 = atom_id_2[:-1] + nef_atom_prefix_2

                                    atom_list.append(nef_atom_2)
                                    details[nef_atom_2] = None
                                    atom_id_map[atom_id_2] = nef_atom_2
                                    proc_atom_list.add(atom_id_2)

                                else:

                                    nef_atom_prefix = 'x' if atom_id < atom_id_2 else 'y'
                                    nef_atom = atom_id[:-1] + nef_atom_prefix

                                    atom_list.append(nef_atom)
                                    details[nef_atom] = None
                                    atom_id_map[atom_id] = nef_atom

                    else:

                        atom_list.append(atom_id)
                        details[atom_id] = None
                        atom_id_map[atom_id] = atom_id

                    proc_atom_list.add(atom_id)

            except KeyError:
                pass

            return (atom_list, details, atom_id_map)

        finally:
            _atom_list = copy.deepcopy(atom_list)
            self.__cachedDictForNefAtom[key] = (_atom_list, details, atom_id_map)
            if leave_unmatched:
                key = (comp_id, str(star_atom_list), str(details), False)
                self.__cachedDictForNefAtom[key] = (_atom_list, details, atom_id_map)

    def get_group(self, comp_id: str, atom_id: str) -> Tuple[Optional[str], Optional[List[str]]]:
        """ Return heavy atom name and list of proton names bonded to the heavy atom.
            @author: Masashi Yokochi
            @return: heavy atom name and list of proton names
        """

        if comp_id in emptyValue:
            return None, None

        if atom_id is None or atom_id[0] not in ('H', '1', '2', '3', 'C', 'N', 'O'):
            return None, None

        if not self.__ccU.updateChemCompDict(comp_id):
            return None, None

        try:

            ccb = next(b for b in self.__ccU.lastBonds
                       if (b[self.__ccU.ccbAtomId1] == atom_id and (atom_id[0] in protonBeginCode or b[self.__ccU.ccbAtomId2][0] in protonBeginCode))
                       or (b[self.__ccU.ccbAtomId2] == atom_id and (atom_id[0] in protonBeginCode or b[self.__ccU.ccbAtomId1][0] in protonBeginCode)))

            hvy_col = self.__ccU.ccbAtomId1 if ccb[self.__ccU.ccbAtomId2 if atom_id[0] in protonBeginCode else self.__ccU.ccbAtomId1] == atom_id else self.__ccU.ccbAtomId2
            pro_col = self.__ccU.ccbAtomId2 if self.__ccU.ccbAtomId1 == hvy_col else self.__ccU.ccbAtomId1

            hvy = ccb[hvy_col]

            return hvy, [b[pro_col] for b in self.__ccU.lastBonds if b[hvy_col] == hvy and b[pro_col][0] in protonBeginCode]

        except StopIteration:
            return None, None

    def get_geminal_group(self, comp_id: str, atom_id: str) -> Tuple[Optional[str], Optional[List[str]]]:
        """ Return geminal heavy atom and list of proton names bonded to the geminal heavy atom.
            @author: Masashi Yokochi
            @return: geminal heavy atom name and list of geminal proton names
        """

        if comp_id in emptyValue:
            return None, None

        if atom_id is None or atom_id[0] not in ('H', '1', '2', '3', 'C', 'N', 'O'):
            return None, None

        if not self.__ccU.updateChemCompDict(comp_id):
            return None, None

        hvy, h_list = self.get_group(comp_id, atom_id)

        if hvy is None:
            return None, None

        h_list_len = len(h_list)

        try:

            ccb = next(b for b in self.__ccU.lastBonds
                       if (b[self.__ccU.ccbAtomId2] == hvy and b[self.__ccU.ccbAtomId1][0] not in protonBeginCode)
                       or (b[self.__ccU.ccbAtomId1] == hvy and b[self.__ccU.ccbAtomId2][0] not in protonBeginCode))

            hvy_conn = ccb[self.__ccU.ccbAtomId1 if ccb[self.__ccU.ccbAtomId2] == hvy else self.__ccU.ccbAtomId2]

            hvy_gem = next(c[self.__ccU.ccbAtomId1 if c[self.__ccU.ccbAtomId2] == hvy_conn else self.__ccU.ccbAtomId2]
                           for c in self.__ccU.lastBonds
                           if (c[self.__ccU.ccbAtomId2] == hvy_conn and c[self.__ccU.ccbAtomId1] != hvy and c[self.__ccU.ccbAtomId1][0] not in protonBeginCode
                               and self.get_group(comp_id, c[self.__ccU.ccbAtomId1])[1] is not None
                               and len(self.get_group(comp_id, c[self.__ccU.ccbAtomId1])[1]) == h_list_len)
                           or (c[self.__ccU.ccbAtomId1] == hvy_conn and c[self.__ccU.ccbAtomId2] != hvy and c[self.__ccU.ccbAtomId2][0] not in protonBeginCode
                               and self.get_group(comp_id, c[self.__ccU.ccbAtomId2])[1] is not None
                               and len(self.get_group(comp_id, c[self.__ccU.ccbAtomId2])[1]) == h_list_len))

            if hvy[0] != hvy_gem[0]:
                return None, None

            return self.get_group(comp_id, hvy_gem)

        except StopIteration:
            return None, None

    def __nef2star_seq_row(self, nef_tags: List[str], star_tags: List[str], loop_data: List[list],
                           report=None) -> Tuple[List[list], List[list]]:
        """ Translate rows in sequence loop from NEF into NMR-STAR.
            @change: rename the original translate_seq_row() to __nef2star_seq_row() by Masashi Yokochi
            @param nef_tags: list of NEF tags
            @param star_tags: list of NMR-STAR tags
            @param loop_data: loop data of NEF
            @param report: NMR data processing report
            @return: rows of NMR-STAR, rows of _Entity_deleted_atom loop (residue variants), otherwise None
        """

        out_row, aux_row = [], []

        chain_index = nef_tags.index('_nef_sequence.chain_code')
        seq_index = nef_tags.index('_nef_sequence.sequence_code')
        comp_index = nef_tags.index('_nef_sequence.residue_name')

        for _star_chain, nef_chain in enumerate(self.authChainId, start=1):

            seq_list = sorted(set(int(row[seq_index]) for row in loop_data if row[chain_index] == nef_chain))

            if len(seq_list) == 0:
                continue

            cif_chain = cif_ps = None
            if report is not None:
                seq_align = report.getSequenceAlignmentWithNmrChainId(nef_chain)
                if seq_align is not None:
                    cif_chain = seq_align['test_chain_id']  # label_asym_id
                    cif_ps = report.getModelPolymerSequenceOf(cif_chain, label_scheme=True)
                    if cif_ps is not None and 'auth_chain_id' in cif_ps:
                        cif_chain = cif_ps['auth_chain_id']  # auth_asym_id

            offset = None

            for _nef_seq in seq_list:

                _cif_seq = None
                if cif_chain is not None:
                    try:
                        if seq_align is not None:
                            _cif_seq = seq_align['test_seq_id'][seq_align['ref_seq_id'].index(_nef_seq)]  # label_seq_id
                            if offset is None:
                                offset = _cif_seq - _nef_seq
                        if cif_ps is not None and 'auth_seq_id' in cif_ps:
                            _cif_seq = cif_ps['auth_seq_id'][cif_ps['seq_id'].index(_cif_seq)]  # auth_seq_id
                    except (IndexError, ValueError):
                        pass

                nef_seq = str(_nef_seq)

                if offset is None:
                    offset = 1 - _nef_seq

                _star_seq = _nef_seq + offset

                row = next(row for row in loop_data if row[chain_index] == nef_chain and row[seq_index] == nef_seq)

                if _cif_seq is None and report is not None and row[chain_index] not in emptyValue and row[seq_index] not in emptyValue:
                    _cif_chain_, _cif_seq_ = report.getLabelSeqSchemeOf(row[chain_index], int(row[seq_index]))
                    if _cif_seq_ is not None:
                        _star_chain = letterToDigit(_cif_chain_)
                        _star_seq = _cif_seq_

                out = [None] * len(star_tags)

                variant = None

                for tag in nef_tags:

                    auth_tag, data_tag, _ = self.get_star_tag(tag)

                    if auth_tag is None:
                        continue

                    data = row[nef_tags.index(tag)]

                    if tag == '_nef_sequence.chain_code':
                        if cif_chain is None:
                            out[star_tags.index(auth_tag)] = data
                        else:
                            out[star_tags.index(auth_tag)] = cif_chain
                    elif tag == '_nef_sequence.sequence_code':
                        if _cif_seq is None:
                            out[star_tags.index(auth_tag)] = data
                        else:
                            out[star_tags.index(auth_tag)] = str(_cif_seq)
                    else:
                        out[star_tags.index(auth_tag)] = data
                        if tag == '_nef_sequence.residue_variant' and data not in emptyValue and '-' in data:
                            variant = data

                    if auth_tag != data_tag:

                        data_index = star_tags.index(data_tag)

                        if tag == '_nef_sequence.chain_code':
                            out[data_index] = _star_chain
                        elif tag == '_nef_sequence.sequence_code':
                            out[data_index] = _star_seq
                        elif data in NEF_BOOLEAN_VALUES:
                            out[data_index] = 'yes' if data in trueValue else 'no'
                        else:
                            out[data_index] = data

                out_row.append(out)

                self.authSeqMap[(nef_chain, _nef_seq)] = (_star_chain, _star_seq)
                self.selfSeqMap[(nef_chain, _nef_seq)] = (nef_chain if cif_chain is None else cif_chain,
                                                          _nef_seq if _cif_seq is None else _cif_seq)

                if variant is not None:
                    aux = [None] * len(ENTITY_DELETED_ATOM_ITEMS)
                    for col, aux_tag in enumerate(ENTITY_DELETED_ATOM_ITEMS):
                        if aux_tag == 'Entity_assembly_ID':
                            aux[col] = _star_chain
                        elif aux_tag == 'Comp_index_ID':
                            aux[col] = _star_seq
                        elif aux_tag == 'Auth_entity_assembly_ID':
                            aux[col] = nef_chain
                        elif aux_tag == 'Auth_seq_ID':
                            aux[col] = _nef_seq
                        elif aux_tag in ('Comp_ID', 'Auth_comp_ID'):
                            aux[col] = row[comp_index]

                    for _variant in variant.split(','):
                        _variant_ = _variant.strip(' ')
                        if _variant_.startswith('-'):
                            atom_list = self.get_star_atom(row[comp_index], _variant_[1:])[0]
                            if len(atom_list) > 0:
                                for atom in atom_list:
                                    _aux = copy.copy(aux)
                                    for col, aux_tag in enumerate(ENTITY_DELETED_ATOM_ITEMS):
                                        if aux_tag == 'ID':
                                            _aux[col] = len(aux_row) + 1
                                        elif aux_tag == 'Atom_ID':
                                            _aux[col] = atom
                                        elif aux_tag == 'Auth_variant_ID':
                                            _aux[col] = _variant_[1:]

                                    aux_row.append(_aux)

        return out_row, aux_row

    def __star2nef_seq_row(self, star_tags: List[str], nef_tags: List[str], loop_data: List[list],
                           report=None, entity_del_atom_loop: Optional[pynmrstar.Loop] = None) -> List[list]:
        """ Translate rows in sequence loop from NMR-STAR into NEF.
            @author: Masashi Yokochi
            @param star_tags: list of NMR-STAR tags
            @param nef_tags: list of NEF tags
            @param loop_data: loop data of NMR-STAR
            @param report: NMR data processing report
            @return: rows of NEF
        """

        out_row = []

        has_nef_index = '_Chem_comp_assembly.NEF_index' in star_tags

        chain_index = star_tags.index('_Chem_comp_assembly.Entity_assembly_ID')
        seq_index = star_tags.index('_Chem_comp_assembly.Comp_index_ID')
        comp_index = star_tags.index('_Chem_comp_assembly.Comp_ID')

        auth_asym_index = auth_seq_index = -1
        if '_Chem_comp_assembly.Auth_asym_ID' in star_tags and '_Chem_comp_assembly.Auth_seq_ID' in star_tags:
            auth_asym_index = star_tags.index('_Chem_comp_assembly.Auth_asym_ID')
            auth_seq_index = star_tags.index('_Chem_comp_assembly.Auth_seq_ID')

        if entity_del_atom_loop is not None:
            aux_tags = entity_del_atom_loop.get_tag_names()
            aux_chain_index = aux_tags.index('_Entity_deleted_atom.Entity_assembly_ID')
            aux_seq_index = aux_tags.index('_Entity_deleted_atom.Comp_index_ID')
            aux_atom_index = aux_tags.index('_Entity_deleted_atom.Atom_ID')

        self.star2NefChainMapping = {}
        self.star2CifChainMapping = {}

        auth_scheme, seq_list = {}, {}

        for cid, star_chain in enumerate(self.authChainId):

            seq_list[star_chain] = sorted(set(int(row[seq_index]) for row in loop_data if row[chain_index] == star_chain))

            if len(seq_list[star_chain]) == 0:
                continue

            nef_chain = indexToLetter(cid)

            self.star2NefChainMapping[star_chain] = nef_chain

        seq_align = None

        if report is not None:

            for star_chain in self.authChainId:

                if len(seq_list[star_chain]) == 0:
                    continue

                cif_chain = cif_ps = None
                if report is not None:
                    seq_align = report.getSequenceAlignmentWithNmrChainId(star_chain)
                    if seq_align is not None:
                        cif_chain = seq_align['test_chain_id']  # label_asym_id
                        cif_ps = report.getModelPolymerSequenceOf(cif_chain, label_scheme=True)
                        if cif_ps is not None and 'auth_chain_id' in cif_ps:
                            cif_chain = cif_ps['auth_chain_id']  # auth_asym_id

                self.star2CifChainMapping[star_chain] = cif_chain

                auth_scheme[star_chain] = cif_ps is not None

            for k, v in self.star2NefChainMapping.items():
                if self.star2CifChainMapping[k] is None:
                    for _k_ in [_k for _k, _v in self.star2NefChainMapping.items() if _v != v]:
                        if self.star2NefChainMapping[_k_] not in self.star2CifChainMapping.values():
                            self.star2CifChainMapping[k] = self.star2NefChainMapping[_k_]
                            break

            for k, v in self.star2NefChainMapping.items():
                if self.star2CifChainMapping[k] is None:
                    self.star2CifChainMapping[k] = v

        index = 1

        for star_chain in self.authChainId:

            _star_chain = int(star_chain)

            if len(seq_list[star_chain]) == 0:
                continue

            nef_chain = self.star2NefChainMapping[star_chain]

            cif_chain = cif_ps = None
            if report is not None:
                cif_chain = self.star2CifChainMapping[star_chain]
                seq_align = report.getSequenceAlignmentWithNmrChainId(star_chain)
                if star_chain in auth_scheme and auth_scheme[star_chain]:
                    cif_ps = report.getModelPolymerSequenceOf(cif_chain, label_scheme=False)

            offset = None

            for _star_seq in seq_list[star_chain]:

                _cif_seq = None
                if cif_chain is not None:
                    try:
                        if None not in (report, seq_align):
                            _cif_seq = seq_align['test_seq_id'][seq_align['ref_seq_id'].index(_star_seq)]  # label_seq_id
                            if offset is None:
                                offset = _cif_seq - _star_seq
                        if cif_ps is not None and 'auth_seq_id' in cif_ps:
                            _cif_seq = cif_ps['auth_seq_id'][cif_ps['seq_id'].index(_cif_seq)]  # auth_seq_id
                    except IndexError:
                        pass

                star_seq = str(_star_seq)

                if offset is None:
                    offset = 1 - _star_seq

                _nef_seq = (_star_seq + offset) if _cif_seq is None else _cif_seq

                row = next(row for row in loop_data if row[chain_index] == star_chain and row[seq_index] == star_seq)

                if _cif_seq is None and not self.__bmrb_only and auth_asym_index != -1 and auth_seq_index != -1:
                    if row[auth_asym_index] not in emptyValue and row[auth_seq_index] not in emptyValue:
                        cif_chain = row[auth_asym_index]
                        _cif_seq = int(row[auth_seq_index])
                        nef_chain = cif_chain
                        _nef_seq = _cif_seq
                        if star_chain in self.star2CifChainMapping and cif_chain != self.star2CifChainMapping[star_chain]:
                            self.star2CifChainMapping[star_chain] = cif_chain

                out = [None] * len(nef_tags)

                if not has_nef_index:
                    out[0] = index

                for tag in star_tags:

                    nef_tag, _ = self.get_nef_tag(tag)

                    if nef_tag is None:
                        continue

                    data = row[star_tags.index(tag)]

                    data_index = nef_tags.index(nef_tag)

                    if nef_tag == '_nef_sequence.chain_code':
                        if cif_chain is None:
                            out[data_index] = nef_chain
                        else:
                            out[data_index] = cif_chain
                    elif nef_tag == '_nef_sequence.sequence_code':
                        if _cif_seq is None:
                            out[data_index] = _nef_seq
                        else:
                            out[data_index] = _cif_seq
                    elif data in STAR_BOOLEAN_VALUES:
                        out[data_index] = 'true' if data in trueValue else 'false'
                    elif nef_tag == '_nef_sequence.residue_variant':
                        if data not in emptyValue or entity_del_atom_loop is None:
                            out[data_index] = data
                        else:
                            star_atom_list = [{'atom_id': k[aux_atom_index], 'ambig_code': None, 'value': None} for k in entity_del_atom_loop
                                              if k[aux_chain_index] == star_chain and k[aux_seq_index] == star_seq]
                            if len(star_atom_list) == 0:
                                out[data_index] = data
                            else:
                                atom_list = self.get_nef_atom(row[comp_index], star_atom_list)[0]
                                if len(atom_list) == 0:
                                    out[data_index] = data
                                else:
                                    _atom_list = ['-' + a for a in atom_list]
                                    out[data_index] = ','.join(_atom_list)

                    else:
                        out[data_index] = data

                index += 1

                out_row.append(out)

                self.authSeqMap[(_star_chain, _star_seq)] = (nef_chain, _nef_seq)
                self.selfSeqMap[(_star_chain, _star_seq)] = (_star_chain if cif_chain is None else cif_chain,
                                                             _star_seq if _cif_seq is None else _cif_seq)

        return out_row

    def __nef2star_bond_row(self, nef_tags: List[str], star_tags: List[str], loop_data: List[list]) -> List[list]:
        """ Translate rows in bond loop from NEF into NMR-STAR.
            @author: Masashi Yokochi
            @param nef_tags: list of NEF tags
            @param star_tags: list of NMR-STAR tags
            @param loop_data: loop data of NEF
            @return: rows of NMR-STAR
        """

        out_row = []

        nef_comp_index_1 = nef_tags.index('_nef_covalent_links.residue_name_1')
        nef_atom_index_1 = nef_tags.index('_nef_covalent_links.atom_name_1')
        nef_comp_index_2 = nef_tags.index('_nef_covalent_links.residue_name_2')
        nef_atom_index_2 = nef_tags.index('_nef_covalent_links.atom_name_2')

        if '_Bond.ID' in star_tags:
            star_id_index = star_tags.index('_Bond.ID')
        else:
            star_id_index = -1

        star_type_index = star_tags.index('_Bond.Type')
        star_value_order_index = star_tags.index('_Bond.Value_order')

        seq_ident_tags = self.get_seq_ident_tags(nef_tags, 'nef')

        chain_tag_1 = chain_tag_2 = None
        seq_tag_1 = seq_tag_2 = None

        for tag in seq_ident_tags:
            chain_tag = tag['chain_tag']
            seq_tag = tag['seq_tag']

            if chain_tag.endswith('_1'):
                chain_tag_1 = chain_tag
                seq_tag_1 = seq_tag
            else:
                chain_tag_2 = chain_tag
                seq_tag_2 = seq_tag

        with io.StringIO() as key_f:

            key_indices = [star_tags.index(tag) for tag in ['_Bond.Entity_assembly_ID_1', '_Bond.Comp_index_ID_1', '_Bond.Atom_ID_1',
                                                            '_Bond.Entity_assembly_ID_2', '_Bond.Comp_index_ID_2', '_Bond.Atom_ID_2']]

            index = 1

            for row in loop_data:

                buf_row = []

                tag_map, self_tag_map = {}, {}

                for tag in seq_ident_tags:
                    chain_tag = tag['chain_tag']
                    seq_tag = tag['seq_tag']

                    nef_chain = row[nef_tags.index(chain_tag)]
                    _nef_seq = row[nef_tags.index(seq_tag)]
                    if isinstance(_nef_seq, str) and _nef_seq not in emptyValue:
                        _nef_seq = int(_nef_seq)

                    seq_key = (nef_chain, _nef_seq)

                    try:
                        tag_map[chain_tag], tag_map[seq_tag] = self.authSeqMap[seq_key]
                        self_tag_map[chain_tag], self_tag_map[seq_tag] = self.selfSeqMap[seq_key]
                    except KeyError:
                        tag_map[chain_tag] = nef_chain
                        tag_map[seq_tag] = _nef_seq
                        self_tag_map[chain_tag] = nef_chain
                        self_tag_map[seq_tag] = _nef_seq

                intra_residue = row[nef_tags.index(chain_tag_1)] == row[nef_tags.index(chain_tag_2)]\
                    and row[nef_tags.index(seq_tag_1)] == row[nef_tags.index(seq_tag_2)]

                atom_list_1 = self.get_star_atom(row[nef_comp_index_1], row[nef_atom_index_1])[0]
                atom_list_2 = self.get_star_atom(row[nef_comp_index_2], row[nef_atom_index_2])[0]

                for atom_1 in atom_list_1:

                    for atom_2 in atom_list_2:

                        if intra_residue and atom_2 == atom_1:
                            continue

                        buf = [None] * len(star_tags)

                        for tag in nef_tags:

                            auth_tag, data_tag, _ = self.get_star_tag(tag)

                            if auth_tag is None:
                                continue

                            data = row[nef_tags.index(tag)]

                            if 'chain_code' in tag or 'sequence_code' in tag:
                                buf[star_tags.index(auth_tag)] = self_tag_map[tag]
                            else:
                                buf[star_tags.index(auth_tag)] = data

                            if auth_tag != data_tag:

                                data_index = star_tags.index(data_tag)

                                if 'chain_code' in tag or 'sequence_code' in tag:
                                    buf[data_index] = tag_map[tag]
                                elif tag == '_nef_covalent_links.atom_name_1':
                                    buf[data_index] = atom_1
                                elif tag == '_nef_covalent_links.atom_name_2':
                                    buf[data_index] = atom_2
                                else:
                                    buf[data_index] = data

                        # 'amide': (C=O)-N
                        # 'directed': N-O
                        # 'disulfide': S-S
                        # 'ester': (C=O)-O
                        # 'ether': -O-
                        # 'hydrogen': (O/N/F)-H-(O/N/F)
                        # 'metal coordination': (N/O/S)-Metal
                        # 'peptide': (C=O)-N
                        # 'thioether': -S-
                        # 'oxime': >C=N-OH
                        # 'thioester': -(C=O)-S-
                        # 'phosphoester': ?
                        # 'phosphodiester': -(PO4)-
                        # 'diselenide': Se-Se
                        buf[star_type_index] = 'covalent'
                        if atom_1 == 'SG' and atom_2 == 'SG':
                            buf[star_type_index] = 'disulfide'
                        elif atom_1 == 'SE' and atom_2 == 'SE':
                            buf[star_type_index] = 'diselenide'
                        elif (atom_1 in NON_METAL_ELEMENTS and (atom_2 in PARAMAGNETIC_ELEMENTS or atom_2 in FERROMAGNETIC_ELEMENTS)) or\
                             (atom_2 in NON_METAL_ELEMENTS and (atom_1 in PARAMAGNETIC_ELEMENTS or atom_1 in FERROMAGNETIC_ELEMENTS)):
                            buf[star_type_index] = 'metal coordination'
                        elif {atom_1, atom_2} == {'C', 'N'}\
                                and row[nef_tags.index(chain_tag_1)] == row[nef_tags.index(chain_tag_2)]\
                                and row[nef_tags.index(seq_tag_1)] != row[nef_tags.index(seq_tag_2)]:
                            buf[star_type_index] = 'peptide'
                        buf[star_value_order_index] = 'sing'

                        buf_row.append(buf)

                keys = set()

                for b in buf_row:

                    if key_f.tell() > 0:
                        key_f.truncate(0)
                        key_f.seek(0)

                    for j in key_indices:
                        key_f.write(f'{b[j]} ')

                    key = key_f.getvalue()

                    if key in keys:
                        continue

                    keys.add(key)

                    if star_id_index != -1:
                        b[star_id_index] = index

                    index += 1

                    out_row.append(b)

            return out_row

    def __nef2star_cs_row(self, nef_tags: List[str], star_tags: List[str], loop_data: List[list], leave_unmatched: bool = False) -> List[list]:
        """ Translate rows in chemical shift loop from NEF into NMR-STAR.
            @change: rename from original translate_cs_row() to __nef2star_cs_row() by Masashi Yokochi
            @param nef_tags: list of NEF tags
            @param star_tags: list of NMR-STAR tags
            @param loop_data: loop data of NEF
            @return: rows of NMR-STAR
        """

        out_row = []

        chain_index = nef_tags.index('_nef_chemical_shift.chain_code')
        seq_index = nef_tags.index('_nef_chemical_shift.sequence_code')
        comp_index = nef_tags.index('_nef_chemical_shift.residue_name')
        atom_index = nef_tags.index('_nef_chemical_shift.atom_name')
        value_index = nef_tags.index('_nef_chemical_shift.value')

        if '_Atom_chem_shift.ID' in star_tags:
            star_id_index = star_tags.index('_Atom_chem_shift.ID')
        else:
            star_id_index = -1

        star_ambig_code_index = star_tags.index('_Atom_chem_shift.Ambiguity_code')
        star_ambig_set_id_index = star_tags.index('_Atom_chem_shift.Ambiguity_set_ID')
        star_details_index = star_tags.index('_Atom_chem_shift.Details')

        if self.insert_original_pdb_cs_items:
            star_original_chain_index = star_tags.index('_Atom_chem_shift.Original_PDB_strand_ID')
            star_original_seq_index = star_tags.index('_Atom_chem_shift.Original_PDB_residue_no')
            star_original_comp_index = star_tags.index('_Atom_chem_shift.Original_PDB_residue_name')
            star_original_atom_index = star_tags.index('_Atom_chem_shift.Original_PDB_atom_name')

        index = 1

        for nef_chain in self.authChainId:

            mapped_seq_id = [s for c, s in self.authSeqMap if c == nef_chain]
            unmapped_seq_id = sorted(set(int(row[seq_index]) for row in loop_data
                                         if row[chain_index] == nef_chain
                                         and row[seq_index] not in emptyValue
                                         and intPattern.match(row[seq_index]) is not None
                                         and int(row[seq_index]) not in mapped_seq_id))

            if len(unmapped_seq_id) > 0:
                mapped_seq_id.extend(unmapped_seq_id)

            for _nef_seq in sorted(mapped_seq_id):

                nef_seq = str(_nef_seq)

                try:
                    star_chain, _star_seq = self.authSeqMap[(nef_chain, _nef_seq)]
                    cif_chain, _cif_seq = self.selfSeqMap[(nef_chain, _nef_seq)]
                except KeyError:
                    star_chain = nef_chain
                    _star_seq = _nef_seq
                    cif_chain = nef_chain
                    _cif_seq = _nef_seq

                in_row = [row for row in loop_data
                          if row[chain_index] == nef_chain and row[seq_index] == nef_seq and row[value_index] not in emptyValue]

                if len(in_row) == 0:
                    continue

                for row in in_row:

                    atom_list, ambiguity_code, details = self.get_star_atom(row[comp_index], row[atom_index], None, leave_unmatched)

                    for atom in atom_list:

                        out = [None] * len(star_tags)

                        for tag in nef_tags:

                            auth_tag, data_tag, _ = self.get_star_tag(tag)

                            if auth_tag is None:
                                continue

                            data = row[nef_tags.index(tag)]

                            if tag == '_nef_chemical_shift.chain_code':
                                out[star_tags.index(auth_tag)] = cif_chain
                            elif tag == '_nef_chemical_shift.sequence_code':
                                out[star_tags.index(auth_tag)] = _cif_seq
                            else:
                                out[star_tags.index(auth_tag)] = data

                            if auth_tag != data_tag:

                                if tag == '_nef_chemical_shift.atom_name':
                                    out[star_tags.index(data_tag)] = atom
                                    if self.insert_original_pdb_cs_items:
                                        out[star_original_atom_index] = row[atom_index]
                                elif tag == '_nef_chemical_shift.chain_code':
                                    out[star_tags.index(data_tag)] = star_chain
                                    if self.insert_original_pdb_cs_items:
                                        out[star_original_chain_index] = nef_chain
                                elif tag == '_nef_chemical_shift.sequence_code':
                                    out[star_tags.index(data_tag)] = _star_seq
                                    if self.insert_original_pdb_cs_items:
                                        out[star_original_seq_index] = _nef_seq
                                elif tag == '_nef_chemical_shift.residue_name':
                                    out[star_tags.index(data_tag)] = data
                                    if self.insert_original_pdb_cs_items:
                                        out[star_original_comp_index] = row[comp_index]
                                else:
                                    out[star_tags.index(data_tag)] = data

                        if star_id_index != -1:
                            out[star_id_index] = index

                        out[star_ambig_code_index] = ambiguity_code
                        out[star_ambig_set_id_index] = None
                        out[star_details_index] = details

                        index += 1

                        out_row.append(out)

        return out_row

    def __star2nef_cs_row(self, star_tags: List[str], nef_tags: List[str], loop_data: List[list]) -> List[list]:
        """ Translate rows in chemical shift loop from NMR-STAR into NEF.
            @author: Masashi Yokochi
            @param star_tags: list of NMR-STAR tags
            @param nef_tags: list of NEF tags
            @param loop_data: loop data of NMR-STAR
            @return: rows of NEF
        """

        out_row = []

        chain_index = star_tags.index('_Atom_chem_shift.Entity_assembly_ID')
        seq_index = star_tags.index('_Atom_chem_shift.Comp_index_ID')
        comp_index = star_tags.index('_Atom_chem_shift.Comp_ID')
        atom_index = star_tags.index('_Atom_chem_shift.Atom_ID')
        ambig_index = star_tags.index('_Atom_chem_shift.Ambiguity_code')
        value_index = star_tags.index('_Atom_chem_shift.Val')

        for star_chain in self.authChainId:

            _star_chain = int(star_chain)
            _cif_chain = self.star2CifChainMapping.get(star_chain)

            mapped_seq_id = [s for c, s in self.authSeqMap if c == _star_chain]
            unmapped_seq_id = set(int(row[seq_index]) for row in loop_data
                                  if row[chain_index] == star_chain
                                  and row[seq_index] not in emptyValue
                                  and intPattern.match(row[seq_index]) is not None
                                  and int(row[seq_index]) not in mapped_seq_id)

            if len(unmapped_seq_id) > 0:
                mapped_seq_id.extend(unmapped_seq_id)

            for _star_seq in sorted(mapped_seq_id):

                star_seq = str(_star_seq)

                in_row = [row for row in loop_data
                          if row[chain_index] == star_chain and row[seq_index] == star_seq and row[value_index] not in emptyValue]

                if len(in_row) == 0:
                    continue

                star_atom_list = [{'atom_id': row[atom_index], 'ambig_code': row[ambig_index], 'value': row[value_index]} for row in in_row]

                atom_list, _, atom_id_map = self.get_nef_atom(in_row[0][comp_index], star_atom_list)

                if len(atom_list) == 0:
                    continue

                seq_key = (_star_chain, _star_seq)

                try:
                    cif_chain, _cif_seq = self.authSeqMap[seq_key]
                except KeyError:
                    try:
                        cif_chain = self.selfSeqMap[(_star_chain, 1)][0]
                        _cif_seq = _star_seq
                    except KeyError:
                        if _star_chain in emptyValue or _star_chain not in self.authChainId:
                            nef_chain = _star_chain
                        else:
                            cid = self.authChainId.index(_star_chain)
                            nef_chain = indexToLetter(cid)
                        cif_chain = nef_chain
                        _cif_seq = _star_seq

                if _cif_chain is not None:
                    cif_chain = _cif_chain

                if seq_key not in self.atomIdMap:
                    self.atomIdMap[seq_key] = {}

                self.atomIdMap[seq_key].update(atom_id_map)

                for atom in atom_list:

                    out = [None] * len(nef_tags)

                    star_atom = next((k for k, v in atom_id_map.items() if v == atom), atom)
                    row = next((row for row in in_row if row[atom_index] == star_atom), None)

                    if row is None:

                        if star_atom.endswith('%'):
                            star_atom = star_atom.replace('%', '')
                            row = next((row for row in in_row if row[atom_index] == star_atom), None)

                        if row is None:
                            continue

                    for tag in star_tags:

                        nef_tag, _ = self.get_nef_tag(tag)

                        if nef_tag is None:
                            continue

                        data_index = nef_tags.index(nef_tag)

                        if nef_tag == '_nef_chemical_shift.atom_name':
                            out[data_index] = atom
                        elif nef_tag == '_nef_chemical_shift.chain_code':
                            out[data_index] = cif_chain
                        elif nef_tag == '_nef_chemical_shift.sequence_code':
                            out[data_index] = _cif_seq
                        else:
                            out[data_index] = row[star_tags.index(tag)]

                    out_row.append(out)

        return out_row

    def get_seq_ident_tags(self, in_tags: List[str], file_type: str) -> List[dict]:  # pylint: disable=no-self-use
        """ Return list of tags utilized for sequence identification.
            @change: rename from original get_residue_identifier() to get_seq_ident_tags() by Masashi Yokochi
            @change: return list of dictionary
            @param in_tags: list of tags
            @param file_type: input file type either 'nef' or 'nmr-star'
            @return: list of tags utilized for sequence identification in given tags
        """

        out_tags = []

        for j in range(1, MAX_DIM_NUM_OF_SPECTRA):

            chain_tag_suffix = f".chain_code_{j}" if file_type == 'nef' else f".Entity_assembly_ID_{j}"

            try:
                chain_tag = next(tag for tag in in_tags if tag.endswith(chain_tag_suffix))
            except StopIteration:
                break

            seq_tag_suffix = f".sequence_code_{j}" if file_type == 'nef' else f".Comp_index_ID_{j}"

            try:
                seq_tag = next(tag for tag in in_tags if tag.endswith(seq_tag_suffix))
            except StopIteration:
                break

            out_tags.append({'chain_tag': chain_tag, 'seq_tag': seq_tag})

        return out_tags

    def get_atom_keys(self, in_tags: List[str], file_type: str) -> List[dict]:  # pylint: disable=no-self-use
        """ Return list of keys utilized for atom identification.
            @change: return list of dictionary
            @param in_tags: list of tags
            @param file_type: input file type either 'nef' or 'nmr-star'
            @return: list of keys utilized for atom identification in given tags
        """

        out_tags = []

        for j in range(1, MAX_DIM_NUM_OF_SPECTRA):

            chain_tag_suffix = f".chain_code_{j}" if file_type == 'nef' else f".Entity_assembly_ID_{j}"

            try:
                chain_tag = next(tag for tag in in_tags if tag.endswith(chain_tag_suffix))
            except StopIteration:
                break

            seq_tag_suffix = f".sequence_code_{j}" if file_type == 'nef' else f".Comp_index_ID_{j}"

            try:
                seq_tag = next(tag for tag in in_tags if tag.endswith(seq_tag_suffix))
            except StopIteration:
                break

            atom_tag_suffix = f".atom_name_{j}" if file_type == 'nef' else f".Atom_ID_{j}"

            try:
                atom_tag = next(tag for tag in in_tags if tag.endswith(atom_tag_suffix))
            except StopIteration:
                break

            out_tags.append({'chain_tag': chain_tag.split('.')[1], 'seq_tag': seq_tag.split('.')[1], 'atom_tag': atom_tag.split('.')[1]})

        return out_tags

    def __nef2star_dist_row(self, nef_tags: List[str], star_tags: List[str], loop_data: List[list]) -> List[list]:
        """ Translate rows in distance restraint loop from NEF into NMR-STAR.
            @change: rename the original translate_restraint_row() to __nef2star_dist_row() by Masashi Yokochi
            @param nef_tags: list of NEF tags
            @param star_tags: list of NMR-STAR tags
            @param loop_data: loop data of NEF
            @return: rows of NMR-STAR
        """

        out_row = []

        nef_comp_index_1 = nef_tags.index('_nef_distance_restraint.residue_name_1')
        nef_atom_index_1 = nef_tags.index('_nef_distance_restraint.atom_name_1')
        nef_comp_index_2 = nef_tags.index('_nef_distance_restraint.residue_name_2')
        nef_atom_index_2 = nef_tags.index('_nef_distance_restraint.atom_name_2')

        seq_ident_tags = self.get_seq_ident_tags(nef_tags, 'nef')

        chain_tag_1 = chain_tag_2 = None
        seq_tag_1 = seq_tag_2 = None

        for tag in seq_ident_tags:
            chain_tag = tag['chain_tag']
            seq_tag = tag['seq_tag']

            if chain_tag.endswith('_1'):
                chain_tag_1 = chain_tag
                seq_tag_1 = seq_tag
            else:
                chain_tag_2 = chain_tag
                seq_tag_2 = seq_tag

        with io.StringIO() as key_f:

            try:
                index_index = star_tags.index('_Gen_dist_constraint.Index_ID')
            except ValueError:
                index_index = -1

            try:
                id_index = star_tags.index('_Gen_dist_constraint.ID')
            except ValueError:
                id_index = -1

            try:
                member_code_index = star_tags.index('_Gen_dist_constraint.Member_logic_code')
            except ValueError:
                member_code_index = -1

            key_indices = [star_tags.index(tag) for tag in ['_Gen_dist_constraint.Entity_assembly_ID_1',
                                                            '_Gen_dist_constraint.Comp_index_ID_1',
                                                            '_Gen_dist_constraint.Atom_ID_1',
                                                            '_Gen_dist_constraint.Entity_assembly_ID_2',
                                                            '_Gen_dist_constraint.Comp_index_ID_2',
                                                            '_Gen_dist_constraint.Atom_ID_2']]

            in_id_index = nef_tags.index('_nef_distance_restraint.restraint_id')

            id_list = sorted(set(int(row[in_id_index]) for row in loop_data))

            index = 1

            for _id, row_id in enumerate(id_list, start=1):

                in_row = [row for row in loop_data if row[in_id_index] == str(row_id)]

                buf_row = []

                for row in in_row:

                    tag_map, self_tag_map = {}, {}

                    for tag in seq_ident_tags:
                        chain_tag = tag['chain_tag']
                        seq_tag = tag['seq_tag']

                        nef_chain = row[nef_tags.index(chain_tag)]
                        _nef_seq = row[nef_tags.index(seq_tag)]
                        if isinstance(_nef_seq, str) and _nef_seq not in emptyValue:
                            _nef_seq = int(_nef_seq)

                        seq_key = (nef_chain, _nef_seq)

                        try:
                            tag_map[chain_tag], tag_map[seq_tag] = self.authSeqMap[seq_key]
                            self_tag_map[chain_tag], self_tag_map[seq_tag] = self.selfSeqMap[seq_key]
                        except KeyError:
                            tag_map[chain_tag] = nef_chain
                            tag_map[seq_tag] = _nef_seq
                            self_tag_map[chain_tag] = nef_chain
                            self_tag_map[seq_tag] = _nef_seq

                    intra_residue = row[nef_tags.index(chain_tag_1)] == row[nef_tags.index(chain_tag_2)]\
                        and row[nef_tags.index(seq_tag_1)] == row[nef_tags.index(seq_tag_2)]

                    atom_list_1 = self.get_star_atom(row[nef_comp_index_1], row[nef_atom_index_1])[0]
                    atom_list_2 = self.get_star_atom(row[nef_comp_index_2], row[nef_atom_index_2])[0]

                    or_code = len(in_row) > 1 or len(atom_list_1) * len(atom_list_2) > 1

                    for atom_1 in atom_list_1:

                        for atom_2 in atom_list_2:

                            if intra_residue and atom_2 == atom_1:
                                continue

                            buf = [None] * len(star_tags)

                            for tag in nef_tags:

                                auth_tag, data_tag, _ = self.get_star_tag(tag)

                                if auth_tag is None:
                                    continue

                                data = row[nef_tags.index(tag)]

                                if 'chain_code' in tag or 'sequence_code' in tag:
                                    buf[star_tags.index(auth_tag)] = self_tag_map[tag]
                                else:
                                    buf[star_tags.index(auth_tag)] = data

                                if auth_tag != data_tag:

                                    data_index = star_tags.index(data_tag)

                                    if 'chain_code' in tag or 'sequence_code' in tag:
                                        buf[data_index] = tag_map[tag]
                                    elif tag == '_nef_distance_restraint.atom_name_1':
                                        buf[data_index] = atom_1
                                        if self.insert_original_atom_name_items:
                                            buf[star_tags.index(auth_tag)] = atom_1
                                            buf[star_tags.index('_Gen_dist_constraint.Auth_atom_name_1')] = row[nef_atom_index_1]
                                    elif tag == '_nef_distance_restraint.atom_name_2':
                                        buf[data_index] = atom_2
                                        if self.insert_original_atom_name_items:
                                            buf[star_tags.index(auth_tag)] = atom_2
                                            buf[star_tags.index('_Gen_dist_constraint.Auth_atom_name_2')] = row[nef_atom_index_2]
                                    else:
                                        buf[data_index] = data

                            if id_index != -1:
                                buf[id_index] = _id

                            if or_code and member_code_index != -1:
                                buf[member_code_index] = 'OR'

                            buf_row.append(buf)

                keys = set()

                for row in buf_row:

                    if key_f.tell() > 0:
                        key_f.truncate(0)
                        key_f.seek(0)

                    for j in key_indices:
                        key_f.write(f'{row[j]} ')

                    key = key_f.getvalue()

                    if key in keys:
                        continue

                    keys.add(key)

                    if index_index != -1:
                        row[index_index] = index

                    index += 1

                    out_row.append(row)

            return out_row

    def __star2nef_dist_row(self, star_tags: List[str], nef_tags: List[str], loop_data: List[list]) -> List[list]:
        """ Translate rows in distance restraint loop from NMR-STAR into NEF.
            @author: Masashi Yokochi
            @param star_tags: list of NMR-STAR tags
            @param nef_tags: list of NEF tags
            @param loop_data: loop data of NMR-STAR
            @return: rows of NEF
        """

        out_row = []

        comp_1_index = star_tags.index('_Gen_dist_constraint.Comp_ID_1')
        comp_2_index = star_tags.index('_Gen_dist_constraint.Comp_ID_2')

        seq_ident_tags = self.get_seq_ident_tags(star_tags, 'nmr-star')

        chain_tag_1 = None

        for tag in seq_ident_tags:
            chain_tag = tag['chain_tag']
            seq_tag = tag['seq_tag']

            if chain_tag.endswith('_1'):
                chain_tag_1 = chain_tag
            else:
                pass

        with io.StringIO() as key_f:

            try:
                index_index = nef_tags.index('_nef_distance_restraint.index')
            except ValueError:
                index_index = -1

            try:
                id_index = nef_tags.index('_nef_distance_restraint.id')
            except ValueError:
                id_index = -1

            key_indices = [nef_tags.index(tag) for tag in ['_nef_distance_restraint.chain_code_1',
                                                           '_nef_distance_restraint.sequence_code_1',
                                                           '_nef_distance_restraint.atom_name_1',
                                                           '_nef_distance_restraint.chain_code_2',
                                                           '_nef_distance_restraint.sequence_code_2',
                                                           '_nef_distance_restraint.atom_name_2']]

            in_id_index = star_tags.index('_Gen_dist_constraint.ID')

            id_list = sorted(set(int(row[in_id_index]) for row in loop_data))

            index = 1

            for _id, row_id in enumerate(id_list, start=1):

                in_row = [row for row in loop_data if row[in_id_index] == str(row_id)]

                buf_row = []

                for row in in_row:

                    tag_map = {}

                    seq_key_1 = seq_key_2 = None

                    for tag in seq_ident_tags:
                        chain_tag = tag['chain_tag']
                        seq_tag = tag['seq_tag']

                        star_chain = row[star_tags.index(chain_tag)]
                        _star_chain = star_chain
                        if isinstance(star_chain, str) and star_chain not in emptyValue:
                            _star_chain = int(star_chain)

                        _star_seq = row[star_tags.index(seq_tag)]
                        if isinstance(_star_seq, str) and _star_seq not in emptyValue:
                            _star_seq = int(_star_seq)

                        seq_key = (_star_chain, _star_seq)

                        try:
                            tag_map[chain_tag], tag_map[seq_tag] = self.authSeqMap[seq_key]
                        except KeyError:
                            try:
                                nef_chain = self.selfSeqMap[(_star_chain, 1)][0]
                            except KeyError:
                                if _star_chain in emptyValue or _star_chain not in self.authChainId:
                                    nef_chain = _star_chain
                                else:
                                    cid = self.authChainId.index(_star_chain)
                                    nef_chain = indexToLetter(cid)
                            tag_map[chain_tag] = nef_chain
                            tag_map[seq_tag] = _star_seq

                        if self.star2CifChainMapping is not None and star_chain in self.star2CifChainMapping:
                            tag_map[chain_tag] = self.star2CifChainMapping[star_chain]

                        if chain_tag == chain_tag_1:
                            seq_key_1 = seq_key
                        else:
                            seq_key_2 = seq_key

                    buf = [None] * len(nef_tags)

                    for tag in star_tags:

                        nef_tag, _ = self.get_nef_tag(tag)

                        if nef_tag is None:
                            continue

                        data = row[star_tags.index(tag)]

                        data_index = nef_tags.index(nef_tag)

                        if 'chain_code' in nef_tag or 'sequence_code' in nef_tag:
                            buf[data_index] = tag_map[tag]
                        elif nef_tag == '_nef_distance_restraint.atom_name_1':
                            try:
                                if self.atomIdMap is not None:
                                    buf[data_index] = self.atomIdMap[seq_key_1][data]
                            except KeyError:
                                atom_list = self.get_nef_atom(row[comp_1_index], [{'atom_id': data, 'ambig_code': None, 'value': None}])[0]
                                if len(atom_list) > 0:
                                    buf[data_index] = atom_list[0]
                                else:
                                    buf[data_index] = data
                        elif nef_tag == '_nef_distance_restraint.atom_name_2':
                            try:
                                if self.atomIdMap is not None:
                                    buf[data_index] = self.atomIdMap[seq_key_2][data]
                            except KeyError:
                                atom_list = self.get_nef_atom(row[comp_2_index], [{'atom_id': data, 'ambig_code': None, 'value': None}])[0]
                                if len(atom_list) > 0:
                                    buf[data_index] = atom_list[0]
                                else:
                                    buf[data_index] = data
                        else:
                            buf[data_index] = data

                    if id_index != -1:
                        buf_row[id_index] = _id

                    buf_row.append(buf)

                keys = set()

                for row in buf_row:

                    if key_f.tell() > 0:
                        key_f.truncate(0)
                        key_f.seek(0)

                    for j in key_indices:
                        key_f.write(f'{row[j]} ')

                    key = key_f.getvalue()

                    if key in keys:
                        continue

                    keys.add(key)

                    if index_index != -1:
                        row[index_index] = index

                    index += 1

                    out_row.append(row)

            return out_row

    def __nef2star_dihed_row(self, nef_tags: List[str], star_tags: List[str], loop_data: List[list]) -> List[list]:
        """ Translate rows in dihedral angle restraint loop from NEF into NMR-STAR.
            @author: Masashi Yokochi
            @param nef_tags: list of NEF tags
            @param star_tags: list of NMR-STAR tags
            @param loop_data: loop data of NEF
            @return: rows of NMR-STAR
        """

        out_row = []

        nef_comp_index_1 = nef_tags.index('_nef_dihedral_restraint.residue_name_1')
        nef_atom_index_1 = nef_tags.index('_nef_dihedral_restraint.atom_name_1')
        nef_comp_index_2 = nef_tags.index('_nef_dihedral_restraint.residue_name_2')
        nef_atom_index_2 = nef_tags.index('_nef_dihedral_restraint.atom_name_2')
        nef_comp_index_3 = nef_tags.index('_nef_dihedral_restraint.residue_name_3')
        nef_atom_index_3 = nef_tags.index('_nef_dihedral_restraint.atom_name_3')
        nef_comp_index_4 = nef_tags.index('_nef_dihedral_restraint.residue_name_4')
        nef_atom_index_4 = nef_tags.index('_nef_dihedral_restraint.atom_name_4')

        seq_ident_tags = self.get_seq_ident_tags(nef_tags, 'nef')

        chain_tag_1 = chain_tag_2 = chain_tag_3 = chain_tag_4 = None
        seq_tag_1 = seq_tag_2 = seq_tag_3 = seq_tag_4 = None

        for tag in seq_ident_tags:
            chain_tag = tag['chain_tag']
            seq_tag = tag['seq_tag']

            if chain_tag.endswith('_1'):
                chain_tag_1 = chain_tag
                seq_tag_1 = seq_tag
            elif chain_tag.endswith('_2'):
                chain_tag_2 = chain_tag
                seq_tag_2 = seq_tag
            elif chain_tag.endswith('_3'):
                chain_tag_3 = chain_tag
                seq_tag_3 = seq_tag
            else:
                chain_tag_4 = chain_tag
                seq_tag_4 = seq_tag

        with io.StringIO() as key_f:

            try:
                index_index = star_tags.index('_Torsion_angle_constraint.Index_ID')
            except ValueError:
                index_index = -1

            try:
                id_index = star_tags.index('_Torsion_angle_constraint.ID')
            except ValueError:
                id_index = -1

            key_indices = [star_tags.index(tag) for tag in ['_Torsion_angle_constraint.Entity_assembly_ID_1',
                                                            '_Torsion_angle_constraint.Comp_index_ID_1',
                                                            '_Torsion_angle_constraint.Atom_ID_1',
                                                            '_Torsion_angle_constraint.Entity_assembly_ID_2',
                                                            '_Torsion_angle_constraint.Comp_index_ID_2',
                                                            '_Torsion_angle_constraint.Atom_ID_2',
                                                            '_Torsion_angle_constraint.Entity_assembly_ID_3',
                                                            '_Torsion_angle_constraint.Comp_index_ID_3',
                                                            '_Torsion_angle_constraint.Atom_ID_3',
                                                            '_Torsion_angle_constraint.Entity_assembly_ID_4',
                                                            '_Torsion_angle_constraint.Comp_index_ID_4',
                                                            '_Torsion_angle_constraint.Atom_ID_4']]

            in_id_index = nef_tags.index('_nef_dihedral_restraint.restraint_id')

            id_list = sorted(set(int(row[in_id_index]) for row in loop_data))

            index = 1

            for _id, row_id in enumerate(id_list, start=1):

                in_row = [row for row in loop_data if row[in_id_index] == str(row_id)]

                buf_row = []

                for row in in_row:

                    tag_map, self_tag_map = {}, {}

                    for tag in seq_ident_tags:
                        chain_tag = tag['chain_tag']
                        seq_tag = tag['seq_tag']

                        nef_chain = row[nef_tags.index(chain_tag)]
                        _nef_seq = row[nef_tags.index(seq_tag)]
                        if isinstance(_nef_seq, str) and _nef_seq not in emptyValue:
                            _nef_seq = int(_nef_seq)

                        seq_key = (nef_chain, _nef_seq)

                        try:
                            tag_map[chain_tag], tag_map[seq_tag] = self.authSeqMap[seq_key]
                            self_tag_map[chain_tag], self_tag_map[seq_tag] = self.selfSeqMap[seq_key]
                        except KeyError:
                            tag_map[chain_tag] = nef_chain
                            tag_map[seq_tag] = _nef_seq
                            self_tag_map[chain_tag] = nef_chain
                            self_tag_map[seq_tag] = _nef_seq

                    intra_residue_12 = row[nef_tags.index(chain_tag_1)] == row[nef_tags.index(chain_tag_2)]\
                        and row[nef_tags.index(seq_tag_1)] == row[nef_tags.index(seq_tag_2)]
                    intra_residue_13 = row[nef_tags.index(chain_tag_1)] == row[nef_tags.index(chain_tag_3)]\
                        and row[nef_tags.index(seq_tag_1)] == row[nef_tags.index(seq_tag_3)]
                    intra_residue_14 = row[nef_tags.index(chain_tag_1)] == row[nef_tags.index(chain_tag_4)]\
                        and row[nef_tags.index(seq_tag_1)] == row[nef_tags.index(seq_tag_4)]
                    intra_residue_23 = row[nef_tags.index(chain_tag_2)] == row[nef_tags.index(chain_tag_3)]\
                        and row[nef_tags.index(seq_tag_2)] == row[nef_tags.index(seq_tag_3)]
                    intra_residue_24 = row[nef_tags.index(chain_tag_2)] == row[nef_tags.index(chain_tag_4)]\
                        and row[nef_tags.index(seq_tag_2)] == row[nef_tags.index(seq_tag_4)]
                    intra_residue_34 = row[nef_tags.index(chain_tag_3)] == row[nef_tags.index(chain_tag_4)]\
                        and row[nef_tags.index(seq_tag_3)] == row[nef_tags.index(seq_tag_4)]

                    atom_list_1 = self.get_star_atom(row[nef_comp_index_1], row[nef_atom_index_1])[0]
                    atom_list_2 = self.get_star_atom(row[nef_comp_index_2], row[nef_atom_index_2])[0]
                    atom_list_3 = self.get_star_atom(row[nef_comp_index_3], row[nef_atom_index_3])[0]
                    atom_list_4 = self.get_star_atom(row[nef_comp_index_4], row[nef_atom_index_4])[0]

                    for atom_1 in atom_list_1:

                        for atom_2 in atom_list_2:

                            if intra_residue_12 and atom_2 == atom_1:
                                continue

                            for atom_3 in atom_list_3:

                                if (intra_residue_13 and atom_3 == atom_1) or (intra_residue_23 and atom_3 == atom_2):
                                    continue

                                for atom_4 in atom_list_4:

                                    if (intra_residue_14 and atom_4 == atom_1) or (intra_residue_24 and atom_4 == atom_2) or (intra_residue_34 and atom_4 == atom_3):
                                        continue

                                    buf = [None] * len(star_tags)

                                    for tag in nef_tags:

                                        auth_tag, data_tag, _ = self.get_star_tag(tag)

                                        if auth_tag is None:
                                            continue

                                        data = row[nef_tags.index(tag)]

                                        if 'chain_code' in tag or 'sequence_code' in tag:
                                            buf[star_tags.index(auth_tag)] = self_tag_map[tag]
                                        else:
                                            buf[star_tags.index(auth_tag)] = data

                                        if auth_tag != data_tag:

                                            data_index = star_tags.index(data_tag)

                                            if 'chain_code' in tag or 'sequence_code' in tag:
                                                buf[data_index] = tag_map[tag]
                                            elif tag == '_nef_dihedral_restraint.atom_name_1':
                                                buf[data_index] = atom_1
                                                if self.insert_original_atom_name_items:
                                                    buf[star_tags.index(auth_tag)] = atom_1
                                                    buf[star_tags.index('_Torsion_angle_constraint.Auth_atom_name_1')] = row[nef_atom_index_1]
                                            elif tag == '_nef_dihedral_restraint.atom_name_2':
                                                buf[data_index] = atom_2
                                                if self.insert_original_atom_name_items:
                                                    buf[star_tags.index(auth_tag)] = atom_2
                                                    buf[star_tags.index('_Torsion_angle_constraint.Auth_atom_name_2')] = row[nef_atom_index_2]
                                            elif tag == '_nef_dihedral_restraint.atom_name_3':
                                                buf[data_index] = atom_3
                                                if self.insert_original_atom_name_items:
                                                    buf[star_tags.index(auth_tag)] = atom_3
                                                    buf[star_tags.index('_Torsion_angle_constraint.Auth_atom_name_3')] = row[nef_atom_index_3]
                                            elif tag == '_nef_dihedral_restraint.atom_name_4':
                                                buf[data_index] = atom_4
                                                if self.insert_original_atom_name_items:
                                                    buf[star_tags.index(auth_tag)] = atom_4
                                                    buf[star_tags.index('_Torsion_angle_constraint.Auth_atom_name_4')] = row[nef_atom_index_4]
                                            else:
                                                buf[data_index] = data

                                    if id_index != -1:
                                        buf[id_index] = _id

                                    buf_row.append(buf)

                keys = set()

                for row in buf_row:

                    if key_f.tell() > 0:
                        key_f.truncate(0)
                        key_f.seek(0)

                    for j in key_indices:
                        key_f.write(f'{row[j]} ')

                    key = key_f.getvalue()

                    if key in keys:
                        continue

                    keys.add(key)

                    if index_index != -1:
                        row[index_index] = index

                    index += 1

                    out_row.append(row)

            return out_row

    def __nef2star_rdc_row(self, nef_tags: List[str], star_tags: List[str], loop_data: List[list]) -> List[list]:
        """ Translate rows in RDC restraint loop from NEF into NMR-STAR.
            @author: Masashi Yokochi
            @param nef_tags: list of NEF tags
            @param star_tags: list of NMR-STAR tags
            @param loop_data: loop data of NEF
            @return: rows of NMR-STAR
        """

        out_row = []

        nef_comp_index_1 = nef_tags.index('_nef_rdc_restraint.residue_name_1')
        nef_atom_index_1 = nef_tags.index('_nef_rdc_restraint.atom_name_1')
        nef_comp_index_2 = nef_tags.index('_nef_rdc_restraint.residue_name_2')
        nef_atom_index_2 = nef_tags.index('_nef_rdc_restraint.atom_name_2')

        seq_ident_tags = self.get_seq_ident_tags(nef_tags, 'nef')

        chain_tag_1 = chain_tag_2 = None
        seq_tag_1 = seq_tag_2 = None

        for tag in seq_ident_tags:
            chain_tag = tag['chain_tag']
            seq_tag = tag['seq_tag']

            if chain_tag.endswith('_1'):
                chain_tag_1 = chain_tag
                seq_tag_1 = seq_tag
            else:
                chain_tag_2 = chain_tag
                seq_tag_2 = seq_tag

        with io.StringIO() as key_f:

            try:
                index_index = star_tags.index('_RDC_constraint.Index_ID')
            except ValueError:
                index_index = -1

            try:
                id_index = star_tags.index('_RDC_constraint.ID')
            except ValueError:
                id_index = -1

            key_indices = [star_tags.index(tag) for tag in ['_RDC_constraint.Entity_assembly_ID_1',
                                                            '_RDC_constraint.Comp_index_ID_1',
                                                            '_RDC_constraint.Atom_ID_1',
                                                            '_RDC_constraint.Entity_assembly_ID_2',
                                                            '_RDC_constraint.Comp_index_ID_2',
                                                            '_RDC_constraint.Atom_ID_2']]

            in_id_index = nef_tags.index('_nef_rdc_restraint.restraint_id')

            id_list = sorted(set(int(row[in_id_index]) for row in loop_data))

            index = 1

            for _id, row_id in enumerate(id_list, start=1):

                in_row = [row for row in loop_data if row[in_id_index] == str(row_id)]

                buf_row = []

                for row in in_row:

                    tag_map, self_tag_map = {}, {}

                    for tag in seq_ident_tags:
                        chain_tag = tag['chain_tag']
                        seq_tag = tag['seq_tag']

                        nef_chain = row[nef_tags.index(chain_tag)]
                        _nef_seq = row[nef_tags.index(seq_tag)]
                        if isinstance(_nef_seq, str) and _nef_seq not in emptyValue:
                            _nef_seq = int(_nef_seq)

                        seq_key = (nef_chain, _nef_seq)

                        try:
                            tag_map[chain_tag], tag_map[seq_tag] = self.authSeqMap[seq_key]
                            self_tag_map[chain_tag], self_tag_map[seq_tag] = self.selfSeqMap[seq_key]
                        except KeyError:
                            tag_map[chain_tag] = nef_chain
                            tag_map[seq_tag] = _nef_seq
                            self_tag_map[chain_tag] = nef_chain
                            self_tag_map[seq_tag] = _nef_seq

                    intra_residue = row[nef_tags.index(chain_tag_1)] == row[nef_tags.index(chain_tag_2)]\
                        and row[nef_tags.index(seq_tag_1)] == row[nef_tags.index(seq_tag_2)]

                    atom_list_1 = self.get_star_atom(row[nef_comp_index_1], row[nef_atom_index_1])[0]
                    atom_list_2 = self.get_star_atom(row[nef_comp_index_2], row[nef_atom_index_2])[0]

                    for atom_1 in atom_list_1:

                        for atom_2 in atom_list_2:

                            if intra_residue and atom_2 == atom_1:
                                continue

                            buf = [None] * len(star_tags)

                            for tag in nef_tags:

                                auth_tag, data_tag, _ = self.get_star_tag(tag)

                                if auth_tag is None:
                                    continue

                                data = row[nef_tags.index(tag)]

                                if 'chain_code' in tag or 'sequence_code' in tag:
                                    buf[star_tags.index(auth_tag)] = self_tag_map[tag]
                                else:
                                    buf[star_tags.index(auth_tag)] = data

                                if auth_tag != data_tag:

                                    data_index = star_tags.index(data_tag)

                                    if 'chain_code' in tag or 'sequence_code' in tag:
                                        buf[data_index] = tag_map[tag]
                                    elif tag == '_nef_rdc_restraint.atom_name_1':
                                        buf[data_index] = atom_1
                                        if self.insert_original_atom_name_items:
                                            buf[star_tags.index(auth_tag)] = atom_1
                                            buf[star_tags.index('_RDC_constraint.Auth_atom_name_1')] = row[nef_atom_index_1]
                                    elif tag == '_nef_rdc_restraint.atom_name_2':
                                        buf[data_index] = atom_2
                                        if self.insert_original_atom_name_items:
                                            buf[star_tags.index(auth_tag)] = atom_2
                                            buf[star_tags.index('_RDC_constraint.Auth_atom_name_2')] = row[nef_atom_index_2]
                                    else:
                                        buf[data_index] = data

                            if id_index != -1:
                                buf[id_index] = _id

                            buf_row.append(buf)

                keys = set()

                for row in buf_row:

                    if key_f.tell() > 0:
                        key_f.truncate(0)
                        key_f.seek(0)

                    for j in key_indices:
                        key_f.write(f'{row[j]} ')

                    key = key_f.getvalue()

                    if key in keys:
                        continue

                    keys.add(key)

                    if index_index != -1:
                        row[index_index] = index

                    index += 1

                    out_row.append(row)

            return out_row

    def __nef2star_peak_row(self, nef_tags: List[str], star_tags: List[str], loop_data: List[list], leave_unmatched: bool = False) -> List[list]:
        """ Translate rows in spectral peak loop from NEF into NMR-STAR.
            @author: Masashi Yokochi
            @param nef_tags: list of NEF tags
            @param star_tags: list of NMR-STAR tags
            @param loop_data: loop data of NEF
            @return: rows of NMR-STAR
        """

        out_row = []

        nef_comp_indices, nef_atom_indices = [], []

        seq_ident_tags = self.get_seq_ident_tags(nef_tags, 'nef')

        num_dim = len(seq_ident_tags)

        for d in range(1, num_dim + 1):
            nef_comp_indices.append(nef_tags.index(f"_nef_peak.residue_name_{d}"))
            nef_atom_indices.append(nef_tags.index(f"_nef_peak.atom_name_{d}"))

        with io.StringIO() as key_f, io.StringIO() as msg_f:

            try:
                index_index = star_tags.index('_Peak_row_format.Index_ID')
            except ValueError:
                index_index = -1

            key_indices = [star_tags.index(tag) for tag in [k for k in star_tags
                                                            if k.startswith('_Peak_row_format.Entity_assembly_ID')
                                                            or k.startswith('_Peak_row_format.Comp_index_ID')
                                                            or k.startswith('_Peak_row_format.Atom_ID')]]

            id_index = nef_tags.index('_nef_peak.peak_id')

            id_list = sorted(set(int(row[id_index]) for row in loop_data))

            index = 1

            for row_id in id_list:

                in_row = [row for row in loop_data if row[id_index] == str(row_id)]

                buf_row = []

                for row in in_row:

                    tag_map, self_tag_map = {}, {}

                    for tag in seq_ident_tags:
                        chain_tag = tag['chain_tag']
                        seq_tag = tag['seq_tag']

                        nef_chain = row[nef_tags.index(chain_tag)]
                        _nef_seq = row[nef_tags.index(seq_tag)]
                        if isinstance(_nef_seq, str) and _nef_seq not in emptyValue:
                            _nef_seq = int(_nef_seq)

                        seq_key = (nef_chain, _nef_seq)

                        try:
                            tag_map[chain_tag], tag_map[seq_tag] = self.authSeqMap[seq_key]
                            self_tag_map[chain_tag], self_tag_map[seq_tag] = self.selfSeqMap[seq_key]
                        except KeyError:
                            tag_map[chain_tag] = nef_chain
                            tag_map[seq_tag] = _nef_seq
                            self_tag_map[chain_tag] = nef_chain
                            self_tag_map[seq_tag] = _nef_seq

                    if msg_f.tell() > 0:
                        msg_f.truncate(0)
                        msg_f.seek(0)

                    a = []

                    for nef_comp_index, nef_atom_index in zip(nef_comp_indices, nef_atom_indices):
                        atom_list = self.get_star_atom(row[nef_comp_index], row[nef_atom_index])[0]
                        len_atom_list = len(atom_list)
                        if len_atom_list == 0:
                            atom_list.append('.')
                        elif len_atom_list > 1 and leave_unmatched:
                            msg_f.write(f"{row[nef_atom_index]} -> {atom_list}, ")

                        a.append(atom_list)

                    pos = msg_f.tell() - 2
                    if pos > 0:
                        msg_f.truncate(pos)
                        msg_f.seek(pos)

                    details = msg_f.getvalue()

                    if num_dim == 1:

                        for comb in itertools.product(a[0]):
                            buf_row.append(self.__nef2star_peak_row__(nef_tags, star_tags, tag_map, self_tag_map, row, details, comb))

                    elif num_dim == 2:

                        for comb in itertools.product(a[0], a[1]):
                            buf_row.append(self.__nef2star_peak_row__(nef_tags, star_tags, tag_map, self_tag_map, row, details, comb))

                    elif num_dim == 3:

                        for comb in itertools.product(a[0], a[1], a[2]):
                            buf_row.append(self.__nef2star_peak_row__(nef_tags, star_tags, tag_map, self_tag_map, row, details, comb))

                    elif num_dim == 4:

                        for comb in itertools.product(a[0], a[1], a[2], a[3]):
                            buf_row.append(self.__nef2star_peak_row__(nef_tags, star_tags, tag_map, self_tag_map, row, details, comb))

                    elif num_dim == 5:

                        for comb in itertools.product(a[0], a[1], a[2], a[3], a[4]):
                            buf_row.append(self.__nef2star_peak_row__(nef_tags, star_tags, tag_map, self_tag_map, row, details, comb))

                    elif num_dim == 6:

                        for comb in itertools.product(a[0], a[1], a[2], a[3], a[4], a[5]):
                            buf_row.append(self.__nef2star_peak_row__(nef_tags, star_tags, tag_map, self_tag_map, row, details, comb))

                    elif num_dim == 7:

                        for comb in itertools.product(a[0], a[1], a[2], a[3], a[4], a[5], a[6]):
                            buf_row.append(self.__nef2star_peak_row__(nef_tags, star_tags, tag_map, self_tag_map, row, details, comb))

                    elif num_dim == 8:

                        for comb in itertools.product(a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7]):
                            buf_row.append(self.__nef2star_peak_row__(nef_tags, star_tags, tag_map, self_tag_map, row, details, comb))

                    elif num_dim == 9:

                        for comb in itertools.product(a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7], a[8]):
                            buf_row.append(self.__nef2star_peak_row__(nef_tags, star_tags, tag_map, self_tag_map, row, details, comb))

                    elif num_dim == 10:

                        for comb in itertools.product(a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7], a[8], a[9]):
                            buf_row.append(self.__nef2star_peak_row__(nef_tags, star_tags, tag_map, self_tag_map, row, details, comb))

                    elif num_dim == 11:

                        for comb in itertools.product(a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7], a[8], a[9], a[10]):
                            buf_row.append(self.__nef2star_peak_row__(nef_tags, star_tags, tag_map, self_tag_map, row, details, comb))

                    elif num_dim == 12:

                        for comb in itertools.product(a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7], a[8], a[9], a[10], a[11]):
                            buf_row.append(self.__nef2star_peak_row__(nef_tags, star_tags, tag_map, self_tag_map, row, details, comb))

                    elif num_dim == 13:

                        for comb in itertools.product(a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7], a[8], a[9], a[10], a[11], a[12]):
                            buf_row.append(self.__nef2star_peak_row__(nef_tags, star_tags, tag_map, self_tag_map, row, details, comb))

                    elif num_dim == 14:

                        for comb in itertools.product(a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7], a[8], a[9], a[10], a[11], a[12], a[13]):
                            buf_row.append(self.__nef2star_peak_row__(nef_tags, star_tags, tag_map, self_tag_map, row, details, comb))

                    elif num_dim == 15:

                        for comb in itertools.product(a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7], a[8], a[9], a[10], a[11], a[12], a[13], a[14]):
                            buf_row.append(self.__nef2star_peak_row__(nef_tags, star_tags, tag_map, self_tag_map, row, details, comb))

                keys = set()

                for row in buf_row:

                    if key_f.tell() > 0:
                        key_f.truncate(0)
                        key_f.seek(0)

                    for j in key_indices:
                        key_f.write(f'{row[j]} ')

                    key = key_f.getvalue()

                    if key in keys:
                        continue

                    keys.add(key)

                    if index_index != -1:
                        row[index_index] = index

                    index += 1

                    out_row.append(row)

            return out_row

    def __nef2star_peak_row__(self, nef_tags: List[str], star_tags: List[str], tag_map: dict, self_tag_map: dict, row: list, details, comb: List[str]) -> list:
        """ Translate rows in spectral peak loop from NEF into NMR-STAR.
            @author: Masashi Yokochi
        """

        buf = [None] * len(star_tags)

        for tag in nef_tags:

            auth_tag, data_tag, _ = self.get_star_tag(tag)

            if auth_tag is None:
                continue

            data = row[nef_tags.index(tag)]

            if 'chain_code' in tag or 'sequence_code' in tag:
                buf[star_tags.index(auth_tag)] = self_tag_map[tag]
            else:
                buf[star_tags.index(auth_tag)] = data

            if auth_tag != data_tag:

                data_index = star_tags.index(data_tag)

                if 'chain_code' in tag or 'sequence_code' in tag:
                    buf[data_index] = tag_map[tag]
                elif tag.startswith('_nef_peak.atom_name'):
                    buf[data_index] = comb[int(tag[20:]) - 1]
                else:
                    buf[data_index] = data

            if len(details) > 0:
                details_index = star_tags.index('_Peak_row_format.Details')

                buf[details_index] = details

        return buf

    def __star2nef_peak_row(self, star_tags: List[str], nef_tags: List[str], loop_data: List[list]) -> List[list]:
        """ Translate rows in spectral peak loop from NMR-STAR into NEF.
            @author: Masashi Yokochi
            @param star_tags: list of NMR-STAR tags
            @param nef_tags: list of NEF tags
            @param loop_data: loop data of NMR-STAR
            @return: rows of NEF
        """

        out_row, comp_indices = [], []

        seq_ident_tags = self.get_seq_ident_tags(star_tags, 'nmr-star')

        num_dim = len(seq_ident_tags)

        for d in range(1, num_dim + 1):
            comp_indices.append(star_tags.index(f"_Peak_row_format.Comp_ID_{d}"))

        with io.StringIO() as key_f:

            try:
                index_index = nef_tags.index('_nef_peak.index')
            except ValueError:
                index_index = -1

            key_indices = [nef_tags.index(tag) for tag in [k for k in nef_tags
                                                           if k.startswith('_nef_peak.chain_code')
                                                           or k.startswith('_nef_peak.sequence_code')
                                                           or k.startswith('_nef_peak.atom_name')]]

            id_index = star_tags.index('_Peak_row_format.ID')

            id_list = sorted(set(int(row[id_index]) for row in loop_data))

            index = 1

            for row_id in id_list:

                in_row = [row for row in loop_data if row[id_index] == str(row_id)]

                buf_row = []

                for row in in_row:

                    tag_map = {}

                    s = []

                    for tag in seq_ident_tags:
                        chain_tag = tag['chain_tag']
                        seq_tag = tag['seq_tag']

                        star_chain = row[star_tags.index(chain_tag)]
                        _star_chain = star_chain
                        if isinstance(star_chain, str) and star_chain not in emptyValue:
                            _star_chain = int(star_chain)

                        _star_seq = row[star_tags.index(seq_tag)]
                        if isinstance(_star_seq, str) and _star_seq not in emptyValue:
                            _star_seq = int(_star_seq)

                        seq_key = (_star_chain, _star_seq)

                        try:
                            tag_map[chain_tag], tag_map[seq_tag] = self.authSeqMap[seq_key]
                        except KeyError:
                            try:
                                nef_chain = self.selfSeqMap[(_star_chain, 1)][0]
                            except KeyError:
                                if _star_chain in emptyValue or _star_chain not in self.authChainId:
                                    nef_chain = _star_chain
                                else:
                                    cid = self.authChainId.index(_star_chain)
                                    nef_chain = indexToLetter(cid)
                            tag_map[chain_tag] = nef_chain
                            tag_map[seq_tag] = _star_seq

                        if self.star2CifChainMapping is not None and star_chain in self.star2CifChainMapping:
                            tag_map[chain_tag] = self.star2CifChainMapping[star_chain]

                        s.append(seq_key)

                    buf = [None] * len(nef_tags)

                    for tag in star_tags:

                        nef_tag, _ = self.get_nef_tag(tag)

                        if nef_tag is None:
                            continue

                        data = row[star_tags.index(tag)]

                        data_index = nef_tags.index(nef_tag)

                        if 'chain_code' in nef_tag or 'sequence_code' in nef_tag:
                            buf[data_index] = tag_map[tag]
                        elif nef_tag.startswith('_nef_peak.atom_name'):
                            try:
                                if self.atomIdMap is not None:
                                    buf[data_index] = self.atomIdMap[s[int(nef_tag[20:]) - 1]][data]
                            except KeyError:
                                atom_list = self.get_nef_atom(row[comp_indices[int(nef_tag[20:]) - 1]],
                                                              [{'atom_id': data, 'ambig_code': None, 'value': None}])[0]
                                if len(atom_list) > 0:
                                    buf[data_index] = atom_list[0]
                                else:
                                    buf[data_index] = data
                        else:
                            buf[data_index] = data

                    buf_row.append(buf)

                keys = set()

                for row in buf_row:

                    if key_f.tell() > 0:
                        key_f.truncate(0)
                        key_f.seek(0)

                    for j in key_indices:
                        key_f.write(f'{row[j]} ')

                    key = key_f.getvalue()

                    if key in keys:
                        continue

                    keys.add(key)

                    if index_index != -1:
                        row[index_index] = index

                    index += 1

                    out_row.append(row)

            return out_row

    def __nef2star_row(self, nef_tags: List[str], star_tags: List[str], in_row: List[list]) -> List[list]:
        """ Translate rows in a loop from NEF into NMR-STAR.
            @change: rename from original translate_row() to __nef2star_row() by Masashi Yokochi
            @param nef_tags: list of NEF tags
            @param star_tags: list of NMR-STAR tags
            @param in_row: rows of NEF
            @return: rows of NMR-STAR
        """

        out_row = []

        tag_map, self_tag_map = {}, {}

        for tag in self.get_seq_ident_tags(nef_tags, 'nef'):
            chain_tag = tag['chain_tag']
            seq_tag = tag['seq_tag']

            nef_chain = in_row[nef_tags.index(chain_tag)]
            _nef_seq = in_row[nef_tags.index(seq_tag)]
            if isinstance(_nef_seq, str) and _nef_seq not in emptyValue:
                _nef_seq = int(_nef_seq)

            seq_key = (nef_chain, _nef_seq)

            try:
                tag_map[chain_tag], tag_map[seq_tag] = self.authSeqMap[seq_key]
                self_tag_map[chain_tag], self_tag_map[seq_tag] = self.selfSeqMap[seq_key]
            except KeyError:
                tag_map[chain_tag] = nef_chain
                tag_map[seq_tag] = _nef_seq
                self_tag_map[chain_tag] = nef_chain
                self_tag_map[seq_tag] = _nef_seq

        if len(nef_tags) != len(star_tags):

            out = [None] * len(star_tags)

            for tag in nef_tags:

                auth_tag, data_tag, _ = self.get_star_tag(tag)

                if auth_tag is None:
                    continue

                data = in_row[nef_tags.index(tag)]

                if 'chain_code' in tag or 'sequence_code' in tag:
                    out[star_tags.index(auth_tag)] = self_tag_map[tag]
                else:
                    out[star_tags.index(auth_tag)] = data

                if auth_tag != data_tag:

                    data_index = star_tags.index(data_tag)

                    if 'chain_code' in tag or 'sequence_code' in tag:
                        out[data_index] = tag_map[tag]
                    elif data in NEF_BOOLEAN_VALUES:
                        out[data_index] = 'yes' if data in trueValue else 'no'
                    else:
                        out[data_index] = data

            out_row.append(out)

        else:
            out_row.append(in_row)

        return out_row

    def __star2nef_row(self, star_tags: List[str], nef_tags: List[str], in_row: List[list]) -> List[list]:
        """ Translate rows in a loop from NMR-STAR into NEF.
            @author: Masashi Yokochi
            @param star_tags: list of NMR-STAR tags
            @param nef_tags: list of NEF tags
            @param in_row: rows of NMR-STAR
            @return: rows of NEF
        """

        out_row = []

        tag_map = {}

        for tag in self.get_seq_ident_tags(star_tags, 'nmr-star'):
            chain_tag = tag['chain_tag']
            seq_tag = tag['seq_tag']

            star_chain = in_row[star_tags.index(chain_tag)]
            _star_chain = star_chain
            if isinstance(star_chain, str) and star_chain not in emptyValue:
                _star_chain = int(star_chain)

            _star_seq = in_row[star_tags.index(seq_tag)]
            if isinstance(_star_seq, str) and _star_seq not in emptyValue:
                _star_seq = int(_star_seq)

            try:
                tag_map[chain_tag], tag_map[seq_tag] = self.authSeqMap[(_star_chain, _star_seq)]
            except (KeyError, TypeError):
                try:
                    nef_chain = self.selfSeqMap[(_star_chain, 1)][0]
                except (KeyError, TypeError):
                    if _star_chain in emptyValue or _star_chain not in self.authChainId:
                        nef_chain = _star_chain
                    else:
                        cid = self.authChainId.index(_star_chain)
                        nef_chain = indexToLetter(cid)
                tag_map[chain_tag] = nef_chain
                tag_map[seq_tag] = _star_seq

            if self.star2CifChainMapping is not None and star_chain in self.star2CifChainMapping:
                tag_map[chain_tag] = self.star2CifChainMapping[star_chain]

        out = [None] * len(nef_tags)

        for tag in star_tags:

            nef_tag, _ = self.get_nef_tag(tag)

            if nef_tag is None:
                continue

            data = in_row[star_tags.index(tag)]

            data_index = nef_tags.index(nef_tag)

            if 'chain_code' in nef_tag or 'sequence_code' in nef_tag:
                out[data_index] = tag_map[tag]
            elif data in STAR_BOOLEAN_VALUES:
                out[data_index] = 'true' if data in trueValue else 'false'
            else:
                out[data_index] = data

        out_row.append(out)

        return out_row

    def __star2nef_peak_can(self, in_sf: pynmrstar.Saveframe, out_sf: pynmrstar.Saveframe) -> Optional[int]:
        """ Translate NMR-STAR canonical spectral peak loops (_Peak, _Peak_general_char, _Peak.char, _Assigned_peak_chem_shift) into NEF.
            @author: Masashi Yokochi
            @param in_sf: input saveframe
            @param out_sf: output saveframe
            @return: assigned chemical shift list id
        """

        try:
            num_dim = int(in_sf.get_tag('Number_of_spectral_dimensions')[0])
        except ValueError:
            return None

        try:
            pk_loop = in_sf.get_loop('_Peak')
        except KeyError:
            return None

        try:
            pk_gen_char_loop = in_sf.get_loop('_Peak_general_char')
        except KeyError:
            pk_gen_char_loop = None

        try:
            pk_char_loop = in_sf.get_loop('_Peak_char')
        except KeyError:
            return None

        try:
            pk_assign_loop = in_sf.get_loop('_Assigned_peak_chem_shift')
        except KeyError:
            pk_assign_loop = None

        out_lp = pynmrstar.Loop.from_scratch()
        out_tags = ['_nef_peak.index', '_nef_peak.peak_id',
                    '_nef_peak.volume', '_nef_peak.volume_uncertainty',
                    '_nef_peak.height', '_nef_peak.height_uncertainty']
        for d in range(1, num_dim + 1):
            out_tags.append(f"_nef_peak.position_{d}")
            out_tags.append(f"_nef_peak.position_uncertainty_{d}")
        for d in range(1, num_dim + 1):
            out_tags.append(f"_nef_peak.chain_code_{d}")
            out_tags.append(f"_nef_peak.sequence_code_{d}")
            out_tags.append(f"_nef_peak.residue_name_{d}")
            out_tags.append(f"_nef_peak.atom_name_{d}")

        out_lp.add_tag(out_tags)

        pk_tags = pk_loop.get_tag_names()

        pk_id_col = pk_tags.index('_Peak.ID')

        if pk_gen_char_loop is not None:
            pk_gen_char_tags = pk_gen_char_loop.get_tag_names()
            pk_gen_char_id_col = pk_gen_char_tags.index('_Peak_general_char.Peak_ID')
            pk_gen_char_val_col = pk_gen_char_tags.index('_Peak_general_char.Intensity_val')
            pk_gen_char_val_err_col = pk_gen_char_tags.index('_Peak_general_char.Intensity_val_err')
            pk_gen_char_type_col = pk_gen_char_tags.index('_Peak_general_char.Measurement_method')

        pk_char_tags = pk_char_loop.get_tag_names()

        pk_char_id_col = pk_char_tags.index('_Peak_char.Peak_ID')
        pk_char_dim_id_col = pk_char_tags.index('_Peak_char.Spectral_dim_ID')
        pk_char_pos_col = pk_char_tags.index('_Peak_char.Chem_shift_val')
        pk_char_pos_err_col = pk_char_tags.index('_Peak_char.Chem_shift_val_err')

        if pk_assign_loop is not None:
            pk_assign_tags = pk_assign_loop.get_tag_names()
            pk_assign_id_col = pk_assign_tags.index('_Assigned_peak_chem_shift.Peak_ID')
            pk_assign_dim_id_col = pk_assign_tags.index('_Assigned_peak_chem_shift.Spectral_dim_ID')
            pk_assign_chain_id_col = pk_assign_tags.index('_Assigned_peak_chem_shift.Entity_assembly_ID')
            pk_assign_seq_id_col = pk_assign_tags.index('_Assigned_peak_chem_shift.Comp_index_ID')
            pk_assign_comp_id_col = pk_assign_tags.index('_Assigned_peak_chem_shift.Comp_ID')
            pk_assign_atom_id_col = pk_assign_tags.index('_Assigned_peak_chem_shift.Atom_ID')
            pk_assign_cs_list_id_col = pk_assign_tags.index('_Assigned_peak_chem_shift.Assigned_chem_shift_list_ID')

        cs_list_id_set = set()

        index = 1

        for pk in pk_loop:

            out = [None] * len(out_tags)

            pk_id = pk[pk_id_col]

            out[0] = index
            out[1] = pk_id

            if pk_gen_char_loop is not None:
                out[2], out[3] = next(((pk_gen_char[pk_gen_char_val_col], pk_gen_char[pk_gen_char_val_err_col])
                                       for pk_gen_char in pk_gen_char_loop.data
                                       if pk_gen_char[pk_gen_char_id_col] == pk_id
                                       and pk_gen_char[pk_gen_char_type_col] == 'volume'), (None, None))

                out[4], out[5] = next(((pk_gen_char[pk_gen_char_val_col], pk_gen_char[pk_gen_char_val_err_col])
                                       for pk_gen_char in pk_gen_char_loop.data
                                       if pk_gen_char[pk_gen_char_id_col] == pk_id
                                       and pk_gen_char[pk_gen_char_type_col] == 'height'), (None, None))

            col = 6

            for d in range(1, num_dim + 1):
                out[col], out[col + 1] = next(((pk_char[pk_char_pos_col], pk_char[pk_char_pos_err_col]) for pk_char in pk_char_loop.data
                                               if pk_char[pk_char_id_col] == pk_id and int(pk_char[pk_char_dim_id_col]) == d), (None, None))
                col += 2

            if pk_assign_loop is not None:
                for d in range(1, num_dim + 1):
                    pk_assign = next((pk_assign for pk_assign in pk_assign_loop.data
                                      if pk_assign[pk_assign_id_col] == pk_id and int(pk_assign[pk_assign_dim_id_col]) == d), None)

                    if pk_assign is not None:

                        _star_chain = pk_assign[pk_assign_chain_id_col]
                        if isinstance(_star_chain, str) and _star_chain not in emptyValue:
                            _star_chain = int(_star_chain)

                        _star_seq = pk_assign[pk_assign_seq_id_col]
                        if isinstance(_star_seq, str) and _star_seq not in emptyValue:
                            _star_seq = int(_star_seq)

                        seq_key = (_star_chain, _star_seq)

                        try:
                            nef_chain, nef_seq = self.authSeqMap[seq_key]
                        except KeyError:
                            try:
                                nef_chain = self.selfSeqMap[(_star_chain, 1)][0]
                            except KeyError:
                                if _star_chain in emptyValue or _star_chain not in self.authChainId:
                                    nef_chain = _star_chain
                                else:
                                    cid = self.authChainId.index(_star_chain)
                                    nef_chain = indexToLetter(cid)
                            nef_seq = _star_seq

                        if self.star2CifChainMapping is not None and _star_chain in self.star2CifChainMapping:
                            nef_chain = self.star2CifChainMapping[_star_chain]

                        out[col] = nef_chain
                        out[col + 1] = nef_seq

                        comp_id = pk_assign[pk_assign_comp_id_col]
                        atom_id = _atom_id = pk_assign[pk_assign_atom_id_col]

                        try:
                            if self.atomIdMap is not None:
                                _atom_id = self.atomIdMap[seq_key][atom_id]
                        except KeyError:
                            atom_list = self.get_nef_atom(comp_id,
                                                          [{'atom_id': atom_id, 'ambig_code': None, 'value': None}])[0]
                            if len(atom_list) > 0:
                                _atom_id = atom_list[0]

                        out[col + 2] = comp_id
                        out[col + 3] = _atom_id

                        cs_list_id = pk_assign[pk_assign_cs_list_id_col]

                        if cs_list_id not in emptyValue:
                            cs_list_id_set.add(cs_list_id)

                    col += 4

            out_lp.add_data(out)

            index += 1

        out_sf.add_loop(out_lp)

        return None if len(cs_list_id_set) == 0 else list(cs_list_id_set)[0]

    def nef_to_nmrstar(self, nef_file: str, star_file: Optional[str] = None,
                       report=None, leave_unmatched: bool = False) -> Tuple[bool, dict]:
        """ Convert NEF file to NMR-STAR file.
            @param nef_file: input NEF file path
            @param star_file: output NMR-STAR file path
            @param report: NMR data processing report object (optional)
        """

        (file_path, file_name) = ntpath.split(os.path.realpath(nef_file))

        info, error = [], []

        if star_file is None:
            star_file = file_path + '/' + file_name.split('.')[0] + '.str'

        is_ok, data_type, nef_data = self.read_input_file(nef_file)

        nef_data = self.__c2S.normalize_nef(nef_data)

        self.resolve_sf_names_for_cif(nef_data)  # DAOTHER-7389, issue #4

        try:
            star_data = pynmrstar.Entry.from_scratch(nef_data.entry_id)
        except Exception:  # AttributeError:
            star_data = pynmrstar.Entry.from_scratch(file_name.split('.')[0])
            # warning.append('Not a complete Entry')

        if not is_ok:
            error.append('Input file not readable.')
            return False, {'info': info, 'error': error}

        if data_type == 'Entry':
            if len(nef_data.get_loops_by_category('nef_sequence')) == 0:  # DAOTHER-6694
                error.append("Missing mandatory '_nef_sequence' category.")
                return False, {'info': info, 'error': error}
            self.authChainId = sorted(set(nef_data.get_loops_by_category('nef_sequence')[0].get_tag('chain_code')))

        elif data_type == 'Saveframe':
            self.authChainId = sorted(set(nef_data[0].get_tag('chain_code')))

        else:
            self.authChainId = sorted(set(nef_data.get_tag('chain_code')))

        self.authSeqMap = None
        self.selfSeqMap = None

        asm_id = 0
        cs_list_id = 0
        dist_list_id = 0
        dihed_list_id = 0
        rdc_list_id = 0
        peak_list_id = 0

        # DAOTHER-9623
        def get_red_sf_framecode(sf):

            pattern = re.compile(fr'{sf.category}(_|_\d+)?$')

            return sf.name if pattern.match(sf.name) or not sf.name.startswith(f'{sf.category}_') else sf.name[len(sf.category) + 1:]

        if data_type == 'Entry':

            red_sf_framecodes = [get_red_sf_framecode(sf) for sf in nef_data]
            dup_sf_framecodes = set(sf_framecode for sf_framecode in red_sf_framecodes if red_sf_framecodes.count(sf_framecode) > 1)

            for saveframe in nef_data:

                sf_framecode = get_red_sf_framecode(saveframe)
                if sf_framecode in dup_sf_framecodes:
                    sf_framecode = saveframe.name

                sf = pynmrstar.Saveframe.from_scratch(sf_framecode)

                if saveframe.category == 'nef_nmr_meta_data':
                    sf.set_tag_prefix('Entry')

                elif saveframe.category == 'nef_molecular_system':
                    asm_id += 1
                    sf.set_tag_prefix('Assembly')

                elif saveframe.category == 'nef_chemical_shift_list':
                    cs_list_id += 1
                    sf.set_tag_prefix('Assigned_chem_shift_list')

                elif saveframe.category == 'nef_distance_restraint_list':
                    dist_list_id += 1
                    sf.set_tag_prefix('Gen_dist_constraint_list')

                elif saveframe.category == 'nef_dihedral_restraint_list':
                    dihed_list_id += 1
                    sf.set_tag_prefix('Torsion_angle_constraint_list')

                elif saveframe.category == 'nef_rdc_restraint_list':
                    rdc_list_id += 1
                    sf.set_tag_prefix('RDC_constraint_list')

                elif saveframe.category == 'nef_nmr_spectrum':
                    peak_list_id += 1
                    sf.set_tag_prefix('Spectral_peak_list')

                else:
                    continue

                for tag in saveframe.tags:

                    if tag[0].lower() == 'sf_category':
                        star_sf_cat = self.get_star_sf_cat(saveframe.category)
                        if star_sf_cat is not None:
                            sf.add_tag('Sf_category', star_sf_cat)
                        sf.add_tag('Sf_framecode', sf_framecode)
                    elif saveframe.category == 'nef_distance_restraint_list' and tag[0] == 'restraint_origin':
                        nef_tag = f"{saveframe.tag_prefix}.{tag[0]}"
                        auth_tag = self.get_star_tag(nef_tag)[0]
                        if auth_tag is not None:
                            sf.add_tag(auth_tag, tag[1] if tag[1] not in altDistanceConstraintType['nmr-star'] else altDistanceConstraintType['nmr-star'][tag[1]])
                    elif saveframe.category == 'nef_dihedral_restraint_list' and tag[0] == 'restraint_origin':
                        nef_tag = f"{saveframe.tag_prefix}.{tag[0]}"
                        auth_tag = self.get_star_tag(nef_tag)[0]
                        if auth_tag is not None:
                            sf.add_tag(auth_tag, tag[1] if tag[1] not in altDihedralAngleConstraintType['nmr-star'] else altDihedralAngleConstraintType['nmr-star'][tag[1]])
                    elif saveframe.category == 'nef_rdc_restraint_list' and tag[0] == 'restraint_origin':
                        nef_tag = f"{saveframe.tag_prefix}.{tag[0]}"
                        auth_tag = self.get_star_tag(nef_tag)[0]
                        if auth_tag is not None:
                            sf.add_tag(auth_tag, tag[1] if tag[1] not in altRdcConstraintType['nmr-star'] else altRdcConstraintType['nmr-star'][tag[1]])
                    elif tag[0].lower() != 'sf_framecode':
                        nef_tag = f"{saveframe.tag_prefix}.{tag[0]}"
                        auth_tag = self.get_star_tag(nef_tag)[0]
                        if auth_tag is not None:
                            sf.add_tag(auth_tag, tag[1])

                has_covalent_links = any(loop for loop in saveframe if loop.category == '_nef_covalent_links')
                aux_rows = []

                for loop in saveframe:

                    lp = pynmrstar.Loop.from_scratch()
                    tags = self.get_star_loop_tags(loop.get_tag_names())

                    if len(tags) == 0:
                        continue

                    lp.add_tag(tags)

                    if loop.category == '_nef_sequence':
                        if self.authSeqMap is None:
                            self.authSeqMap = {}
                            self.selfSeqMap = {}
                        rows, aux_rows = self.__nef2star_seq_row(loop.get_tag_names(), lp.get_tag_names(), loop.data, report)
                        for d in rows:
                            d[lp.get_tag_names().index('_Chem_comp_assembly.Assembly_ID')] = asm_id
                            lp.add_data(d)

                    elif loop.category == '_nef_covalent_links':
                        rows = self.__nef2star_bond_row(loop.get_tag_names(), lp.get_tag_names(), loop.data)
                        for d in rows:
                            d[lp.get_tag_names().index('_Bond.Assembly_ID')] = asm_id
                            lp.add_data(d)

                    elif loop.category == '_nef_chemical_shift':
                        rows = self.__nef2star_cs_row(loop.get_tag_names(), lp.get_tag_names(), loop.data, leave_unmatched)
                        for d in rows:
                            d[lp.get_tag_names().index('_Atom_chem_shift.Assigned_chem_shift_list_ID')] = cs_list_id
                            lp.add_data(d)

                    elif loop.category == '_nef_distance_restraint':
                        rows = self.__nef2star_dist_row(loop.get_tag_names(), lp.get_tag_names(), loop.data)
                        for d in rows:
                            d[lp.get_tag_names().index('_Gen_dist_constraint.Gen_dist_constraint_list_ID')] = dist_list_id
                            lp.add_data(d)

                    elif loop.category == '_nef_dihedral_restraint':
                        rows = self.__nef2star_dihed_row(loop.get_tag_names(), lp.get_tag_names(), loop.data)
                        for d in rows:
                            d[lp.get_tag_names().index('_Torsion_angle_constraint.Torsion_angle_constraint_list_ID')] = dihed_list_id
                            lp.add_data(d)

                    elif loop.category == '_nef_rdc_restraint':
                        rows = self.__nef2star_rdc_row(loop.get_tag_names(), lp.get_tag_names(), loop.data)
                        for d in rows:
                            d[lp.get_tag_names().index('_RDC_constraint.RDC_constraint_list_ID')] = rdc_list_id
                            lp.add_data(d)

                    elif loop.category == '_nef_peak':
                        rows = self.__nef2star_peak_row(loop.get_tag_names(), lp.get_tag_names(), loop.data, leave_unmatched)
                        for d in rows:
                            d[lp.get_tag_names().index('_Peak_row_format.Spectral_peak_list_ID')] = peak_list_id
                            lp.add_data(d)

                    else:

                        for data in loop:

                            if loop.category == '_nef_spectrum_dimension':
                                rows = self.__nef2star_row(loop.get_tag_names(), lp.get_tag_names(), data)
                                for d in rows:
                                    d[lp.get_tag_names().index('_Spectral_dim.Spectral_peak_list_ID')] = peak_list_id
                                    lp.add_data(d)

                            elif loop.category == '_nef_spectrum_dimension_transfer':
                                rows = self.__nef2star_row(loop.get_tag_names(), lp.get_tag_names(), data)
                                for d in rows:
                                    d[lp.get_tag_names().index('_Spectral_dim_transfer.Spectral_peak_list_ID', )] = peak_list_id
                                    lp.add_data(d)

                            else:
                                rows = self.__nef2star_row(loop.get_tag_names(), lp.get_tag_names(), data)
                                for d in rows:
                                    lp.add_data(d)

                    sf.add_loop(lp)

                    if len(aux_rows) > 0 and ((loop.category == '_nef_sequence' and not has_covalent_links)
                                              or (loop.category == '_nef_covalent_links' and has_covalent_links)):
                        lp = pynmrstar.Loop.from_scratch()
                        for _tag in ENTITY_DELETED_ATOM_ITEMS:
                            lp.add_tag('_Entity_deleted_atom.' + _tag)
                        for d in aux_rows:
                            d[lp.get_tag_names().index('_Entity_deleted_atom.Assembly_ID')] = asm_id
                            lp.add_data(d)
                        sf.add_loop(lp)

                if saveframe.category == 'nef_nmr_meta_data':
                    sf.add_tag('NMR_STAR_version', NMR_STAR_VERSION)

                    try:
                        loop = sf.get_loop('_Software_applied_methods')
                        row = []
                        for t in loop.tags:
                            if t == 'Software_name':
                                row.append(__package_name__)
                            # elif t == 'Script_name':
                            #     row.append(self.nef_to_nmrstar.__name__)
                            else:
                                row.append('.')
                        loop.add_data(row)
                    except KeyError:
                        pass

                elif saveframe.category == 'nef_molecular_system':
                    sf.add_tag('ID', asm_id)

                elif saveframe.category == 'nef_chemical_shift_list':
                    sf.add_tag('ID', cs_list_id)

                elif saveframe.category == 'nef_distance_restraint_list':
                    sf.add_tag('ID', dist_list_id)

                elif saveframe.category == 'nef_dihedral_restraint_list':
                    sf.add_tag('ID', dihed_list_id)

                elif saveframe.category == 'nef_rdc_restraint_list':
                    sf.add_tag('ID', rdc_list_id)

                elif saveframe.category == 'nef_nmr_spectrum':
                    sf.add_tag('ID', peak_list_id)

                else:
                    continue

                star_data.add_saveframe(sf)

        elif data_type in ('Saveframe', 'Loop'):

            if data_type == 'Saveframe':
                saveframe = nef_data

                sf_framecode = get_red_sf_framecode(saveframe)

                sf = pynmrstar.Saveframe.from_scratch(sf_framecode)

                if saveframe.category == 'nef_nmr_meta_data':
                    sf.set_tag_prefix('Entry')

                elif saveframe.category == 'nef_molecular_system':
                    asm_id += 1
                    sf.set_tag_prefix('Assembly')

                elif saveframe.category == 'nef_chemical_shift_list':
                    cs_list_id += 1
                    sf.set_tag_prefix('Assigned_chem_shift_list')

                elif saveframe.category == 'nef_distance_restraint_list':
                    dist_list_id += 1
                    sf.set_tag_prefix('Gen_dist_constraint_list')

                elif saveframe.category == 'nef_dihedral_restraint_list':
                    dihed_list_id += 1
                    sf.set_tag_prefix('Torsion_angle_constraint_list')

                elif saveframe.category == 'nef_rdc_restraint_list':
                    rdc_list_id += 1
                    sf.set_tag_prefix('RDC_constraint_list')

                elif saveframe.category == 'nef_nmr_spectrum':
                    peak_list_id += 1
                    sf.set_tag_prefix('Spectral_peak_list')

                for tag in saveframe.tags:

                    if tag[0].lower() == 'sf_category':
                        star_sf_cat = self.get_star_sf_cat(saveframe.category)
                        if star_sf_cat is not None:
                            sf.add_tag('Sf_category', star_sf_cat)
                        sf.add_tag('Sf_framecode', sf_framecode)
                    elif saveframe.category == 'nef_distance_restraint_list' and tag[0] == 'restraint_origin':
                        nef_tag = f"{saveframe.tag_prefix}.{tag[0]}"
                        auth_tag = self.get_star_tag(nef_tag)[0]
                        if auth_tag is not None:
                            sf.add_tag(auth_tag, tag[1] if tag[1] not in altDistanceConstraintType['nmr-star'] else altDistanceConstraintType['nmr-star'][tag[1]])
                    elif saveframe.category == 'nef_dihedral_restraint_list' and tag[0] == 'restraint_origin':
                        nef_tag = f"{saveframe.tag_prefix}.{tag[0]}"
                        auth_tag = self.get_star_tag(nef_tag)[0]
                        if auth_tag is not None:
                            sf.add_tag(auth_tag, tag[1] if tag[1] not in altDihedralAngleConstraintType['nmr-star'] else altDihedralAngleConstraintType['nmr-star'][tag[1]])
                    elif saveframe.category == 'nef_rdc_restraint_list' and tag[0] == 'restraint_origin':
                        nef_tag = f"{saveframe.tag_prefix}.{tag[0]}"
                        auth_tag = self.get_star_tag(nef_tag)[0]
                        if auth_tag is not None:
                            sf.add_tag(auth_tag, tag[1] if tag[1] not in altRdcConstraintType['nmr-star'] else altRdcConstraintType['nmr-star'][tag[1]])
                    elif tag[0].lower() != 'sf_framecode':
                        nef_tag = f"{saveframe.tag_prefix}.{tag[0]}"
                        auth_tag = self.get_star_tag(nef_tag)[0]
                        if auth_tag is not None:
                            sf.add_tag(auth_tag, tag[1])

            else:

                if nef_data.category == '_nef_program_script':
                    sf = pynmrstar.Saveframe.from_scratch('entry')
                    sf.set_tag_prefix('Entry')
                    sf.add_tag('Sf_category', 'entry_information')

                elif nef_data.category == '_audit':  # DAOTHER-6327
                    sf = pynmrstar.Saveframe.from_scratch('entry')
                    sf.set_tag_prefix('Entry')
                    sf.add_tag('Sf_category', 'entry_information')

                elif nef_data.category == '_nef_sequence':
                    asm_id += 1
                    sf = pynmrstar.Saveframe.from_scratch('assembly')
                    sf.set_tag_prefix('Assembly')
                    sf.add_tag('Sf_category', 'assembly')

                elif nef_data.category == '_nef_chemical_shift':
                    cs_list_id += 1
                    sf = pynmrstar.Saveframe.from_scratch(f"assigned_chem_shift_list_{cs_list_id}")
                    sf.set_tag_prefix('Assigned_chem_shift_list')
                    sf.add_tag('Sf_category', 'assigned_chemical_shifts')

                elif nef_data.category == '_nef_distance_restraint':
                    dist_list_id += 1
                    sf = pynmrstar.Saveframe.from_scratch(f"gen_dist_constraint_list_{dist_list_id}")
                    sf.set_tag_prefix('Gen_dist_constraint_list')
                    sf.add_tag('Sf_category', 'general_distance_constraints')

                elif nef_data.category == '_nef_dihedral_restraint':
                    dihed_list_id += 1
                    sf = pynmrstar.Saveframe.from_scratch(f"torsion_angle_constraint_list_{dihed_list_id}")
                    sf.set_tag_prefix('Torsion_angle_constraint_list')
                    sf.add_tag('Sf_category', 'torsion_angle_constraints')

                elif nef_data.category == '_nef_rdc_restraint':
                    rdc_list_id += 1
                    sf = pynmrstar.Saveframe.from_scratch(f"rdc_constraint_list_{rdc_list_id}")
                    sf.set_tag_prefix('RDC_constraint_list')
                    sf.add_tag('Sf_category', 'RDC_constraints')

                elif nef_data.category == '_nef_peak':
                    peak_list_id += 1
                    sf = pynmrstar.Saveframe.from_scratch(f"spectral_peak_list_{peak_list_id}")
                    sf.set_tag_prefix('Spectral_peak_list')
                    sf.add_tag('Sf_category', 'spectral_peak_list')

                else:
                    error.append(f"Loop category {nef_data.category} is not supported.")
                    return False, {'info': info, 'error': error}

                sf.add_tag('Sf_framecode', sf.name)

                saveframe = [nef_data]

            has_covalent_links = any(loop for loop in saveframe if loop.category == '_nef_covalent_links')
            aux_rows = []

            for loop in saveframe:

                lp = pynmrstar.Loop.from_scratch()
                tags = self.get_star_loop_tags(loop.get_tag_names())

                if len(tags) == 0:
                    continue

                lp.add_tag(tags)

                if loop.category == '_nef_sequence':
                    if self.authSeqMap is None:
                        self.authSeqMap = {}
                        self.selfSeqMap = {}
                    rows, aux_rows = self.__nef2star_seq_row(loop.get_tag_names(), lp.get_tag_names(), loop.data, report)
                    for d in rows:
                        d[lp.get_tag_names().index('_Chem_comp_assembly.Assembly_ID')] = asm_id
                        lp.add_data(d)

                elif loop.category == '_nef_covalent_links':
                    rows = self.__nef2star_bond_row(loop.get_tag_names(), lp.get_tag_names(), loop.data)
                    for d in rows:
                        d[lp.get_tag_names().index('_Bond.Assembly_ID')] = asm_id
                        lp.add_data(d)

                elif loop.category == '_nef_chemical_shift':
                    rows = self.__nef2star_cs_row(loop.get_tag_names(), lp.get_tag_names(), loop.data, leave_unmatched)
                    for d in rows:
                        d[lp.get_tag_names().index('_Atom_chem_shift.Assigned_chem_shift_list_ID')] = cs_list_id
                        lp.add_data(d)

                elif loop.category == '_nef_distance_restraint':
                    rows = self.__nef2star_dist_row(loop.get_tag_names(), lp.get_tag_names(), loop.data)
                    for d in rows:
                        d[lp.get_tag_names().index('_Gen_dist_constraint.Gen_dist_constraint_list_ID')] = dist_list_id
                        lp.add_data(d)

                elif loop.category == '_nef_dihedral_restraint':
                    rows = self.__nef2star_dihed_row(loop.get_tag_names(), lp.get_tag_names(), loop.data)
                    for d in rows:
                        d[lp.get_tag_names().index('_Torsion_angle_constraint.Torsion_angle_constraint_list_ID')] = dihed_list_id
                        lp.add_data(d)

                elif loop.category == '_nef_rdc_restraint':
                    rows = self.__nef2star_rdc_row(loop.get_tag_names(), lp.get_tag_names(), loop.data)
                    for d in rows:
                        d[lp.get_tag_names().index('_RDC_constraint.RDC_constraint_list_ID')] = rdc_list_id
                        lp.add_data(d)

                elif loop.category == '_nef_peak':
                    rows = self.__nef2star_peak_row(loop.get_tag_names(), lp.get_tag_names(), loop.data, leave_unmatched)
                    for d in rows:
                        d[lp.get_tag_names().index('_Peak_row_format.Spectral_peak_list_ID')] = peak_list_id
                        lp.add_data(d)

                else:

                    for data in loop:

                        if loop.category == '_nef_spectrum_dimension':
                            rows = self.__nef2star_row(loop.get_tag_names(), lp.get_tag_names(), data)
                            for d in rows:
                                d[lp.get_tag_names().index('_Spectral_dim.Spectral_peak_list_ID')] = peak_list_id
                                lp.add_data(d)

                        elif loop.category == '_nef_spectrum_dimension_transfer':
                            rows = self.__nef2star_row(loop.get_tag_names(), lp.get_tag_names(), data)
                            for d in rows:
                                d[lp.get_tag_names().index('_Spectral_dim_transfer.Spectral_peak_list_ID', )] = peak_list_id
                                lp.add_data(d)

                        else:
                            rows = self.__nef2star_row(loop.get_tag_names(), lp.get_tag_names(), data)
                            for d in rows:
                                lp.add_data(d)

                sf.add_loop(lp)

                if len(aux_rows) > 0 and ((loop.category == '_nef_sequence' and not has_covalent_links)
                                          or (loop.category == '_nef_covalent_links' and has_covalent_links)):
                    lp = pynmrstar.Loop.from_scratch()
                    for _tag in ENTITY_DELETED_ATOM_ITEMS:
                        lp.add_tag('_Entity_deleted_atom.' + _tag)
                    for d in aux_rows:
                        d[lp.get_tag_names().index('_Entity_deleted_atom.Assembly_ID')] = asm_id
                        lp.add_data(d)
                    sf.add_loop(lp)

            if sf.category == 'nef_nmr_meta_data':
                sf.add_tag('NMR_STAR_version', NMR_STAR_VERSION)

                try:
                    loop = sf.get_loop('_Software_applied_methods')
                    row = []
                    for t in loop.tags:
                        if t == 'Software_name':
                            row.append(__package_name__)
                        # elif t == 'Script_name':
                        #     row.append(self.nef_to_nmrstar.__name__)
                        else:
                            row.append('.')
                    loop.add_data(row)
                except KeyError:
                    pass

            elif sf.category == 'nef_molecular_system':
                sf.add_tag('ID', asm_id)

            elif sf.category == 'nef_chemical_shift_list':
                sf.add_tag('ID', cs_list_id)

            elif sf.category == 'nef_distance_restraint_list':
                sf.add_tag('ID', dist_list_id)

            elif sf.category == 'nef_dihedral_restraint_list':
                sf.add_tag('ID', dihed_list_id)

            elif sf.category == 'nef_rdc_restraint_list':
                sf.add_tag('ID', rdc_list_id)

            elif sf.category == 'nef_nmr_spectrum':
                sf.add_tag('ID', peak_list_id)

            star_data.add_saveframe(sf)

        # star_data.normalize()  # do not invoke normalize() to preserve ID
        self.__c2S.normalize_str(star_data)

        star_data.write_to_file(star_file, show_comments=False, skip_empty_loops=True, skip_empty_tags=False)

        info.append(f"File {star_file} successfully written.")

        return True, {'info': info, 'error': error}

    def nmrstar_to_nef(self, star_file: str, nef_file: Optional[str] = None,
                       report=None) -> Tuple[bool, dict]:
        """ Convert NMR-STAR file to NEF file.
            @author: Masashi Yokochi
            @param star_file: input NMR-STAR file path
            @param nef_file: output NEF file path
            @param report: NMR data processing report object (optional)
        """

        (file_path, file_name) = ntpath.split(os.path.realpath(star_file))

        info, error = [], []

        if nef_file is None:
            nef_file = file_path + '/' + file_name.split('.')[0] + '.nef'

        is_ok, data_type, star_data = self.read_input_file(star_file)

        star_data = self.__c2S.normalize_str(star_data)

        self.resolve_sf_names_for_cif(star_data)  # DAOTHER-7389, issue #4

        try:
            nef_data = pynmrstar.Entry.from_scratch(star_data.entry_id)
        except Exception:  # AttributeError:
            nef_data = pynmrstar.Entry.from_scratch(file_name.split('.')[0])
            # warning.append('Not a complete Entry.')

        if not is_ok:
            error.append('Input file not readable.')
            return False, {'info': info, 'error': error}

        asm_id = 0
        cs_list_id = 0
        dist_list_id = 0
        dihed_list_id = 0
        rdc_list_id = 0
        peak_list_id = 0

        if data_type == 'Entry':
            if len(star_data.get_loops_by_category('Chem_comp_assembly')) == 0:  # DAOTHER-6694
                error.append("Missing mandatory '_Chem_comp_assembly' category.")
                return False, {'info': info, 'error': error}
            self.authChainId = sorted(set(star_data.get_loops_by_category('Chem_comp_assembly')[0].get_tag('Entity_assembly_ID')),
                                      key=lambda x: float(re.sub(r'[^\d]+', '', x)))

        elif data_type == 'Saveframe':
            self.authChainId = sorted(set(star_data[0].get_tag('Entity_assembly_ID')),
                                      key=lambda x: float(re.sub(r'[^\d]+', '', x)))

        else:
            self.authChainId = sorted(set(star_data.get_tag('Entity_assembly_ID')),
                                      key=lambda x: float(re.sub(r'[^\d]+', '', x)))

        self.authSeqMap = None
        self.selfSeqMap = None
        self.atomIdMap = None

        # DAOTHER-9623
        def get_nef_sf_framecode(sf, prefix):
            return sf.name if sf.name.startswith(prefix) else f'{prefix}_{sf.name}'

        if data_type == 'Entry':

            for saveframe in star_data:

                nef_sf_cat = self.get_nef_sf_cat(saveframe.category)

                if nef_sf_cat is None:
                    continue

                sf_framecode = get_nef_sf_framecode(saveframe, nef_sf_cat)

                sf = pynmrstar.Saveframe.from_scratch(sf_framecode)

                sf.set_tag_prefix(nef_sf_cat)

                sf.add_tag('sf_category', nef_sf_cat)
                sf.add_tag('sf_framecode', sf.name)

                for tag in saveframe.tags:
                    tag_name = tag[0].lower()
                    if tag_name in ('sf_category', 'sf_framecode'):
                        continue
                    if saveframe.category == 'entry_information':
                        if tag_name == 'source_data_format':
                            sf.add_tag('format_name', NEF_FORMAT_NAME)
                        elif tag_name == 'source_data_format_version':
                            sf.add_tag('format_version', NEF_VERSION)
                        else:
                            nef_tag, _ = self.get_nef_tag(saveframe.tag_prefix + '.' + tag[0])
                            if nef_tag is not None:
                                sf.add_tag(nef_tag, tag[1])
                    elif saveframe.category == 'general_distance_constraints' and tag_name == 'constraint_type':
                        nef_tag, _ = self.get_nef_tag(saveframe.tag_prefix + '.' + tag[0])
                        if nef_tag is not None:
                            sf.add_tag(nef_tag, tag[1] if tag[1] not in altDistanceConstraintType['nef'] else altDistanceConstraintType['nef'][tag[1]])
                    elif saveframe.category == 'torsion_angle_constraints' and tag_name == 'constraint_type':
                        nef_tag, _ = self.get_nef_tag(saveframe.tag_prefix + '.' + tag[0])
                        if nef_tag is not None:
                            sf.add_tag(nef_tag, tag[1] if tag[1] not in altDihedralAngleConstraintType['nef'] else altDihedralAngleConstraintType['nef'][tag[1]])
                    elif saveframe.category == 'RDC_constraints' and tag_name == 'constraint_type':
                        nef_tag, _ = self.get_nef_tag(saveframe.tag_prefix + '.' + tag[0])
                        if nef_tag is not None:
                            sf.add_tag(nef_tag, tag[1] if tag[1] not in altRdcConstraintType['nef'] else altRdcConstraintType['nef'][tag[1]])
                    else:
                        nef_tag, _ = self.get_nef_tag(saveframe.tag_prefix + '.' + tag[0])
                        if nef_tag is not None:
                            sf.add_tag(nef_tag, tag[1])

                entity_del_atom_loop = next((loop for loop in saveframe if loop.category == '_Entity_deleted_atom'), None)

                has_pk_can_format = has_pk_row_format = False

                for loop in saveframe:

                    try:

                        lp = pynmrstar.Loop.from_scratch()
                        tags = self.get_nef_loop_tags(loop.get_tag_names())
                        tag_set = set(tags)
                        if len(tags) > len(tag_set):
                            tags = list(tag_set)

                        if len(tags) == 0:
                            continue

                        lp.add_tag(tags)

                        if loop.category == '_Chem_comp_assembly':
                            if self.authSeqMap is None:
                                self.authSeqMap = {}
                                self.selfSeqMap = {}
                            rows = self.__star2nef_seq_row(loop.get_tag_names(), lp.get_tag_names(), loop.data, report,
                                                           entity_del_atom_loop)
                            for d in rows:
                                lp.add_data(d)

                        elif loop.category == '_Atom_chem_shift':
                            if self.atomIdMap is None:
                                self.atomIdMap = {}

                            rows = self.__star2nef_cs_row(loop.get_tag_names(), lp.get_tag_names(), loop.data)
                            for d in rows:
                                lp.add_data(d)

                        elif loop.category == '_Gen_dist_constraint':
                            rows = self.__star2nef_dist_row(loop.get_tag_names(), lp.get_tag_names(), loop.data)
                            for d in rows:
                                lp.add_data(d)

                        elif loop.category == '_Peak_row_format':
                            rows = self.__star2nef_peak_row(loop.get_tag_names(), lp.get_tag_names(), loop.data)
                            for d in rows:
                                lp.add_data(d)
                            has_pk_row_format = True

                        elif len(tags) > 0:
                            for data in loop:
                                rows = self.__star2nef_row(loop.get_tag_names(), lp.get_tag_names(), data)
                                for d in rows:
                                    lp.add_data(d)

                        elif loop.category == '_Peak':
                            has_pk_can_format = True

                        sf.add_loop(lp)

                    except ValueError:
                        pass

                if saveframe.category == 'entry_information':
                    has_format_name = has_format_ver = False
                    for tags in sf.tags:
                        if tags[0] == 'format_name':
                            has_format_name = True
                        elif tags[0] == 'format_version':
                            has_format_ver = True

                    if not has_format_name:
                        sf.add_tag('format_name', NEF_FORMAT_NAME)
                    if not has_format_ver:
                        sf.add_tag('format_version', NEF_VERSION)

                    try:
                        loop = sf.get_loop('_nef_program_script')
                        row = []
                        for t in loop.tags:
                            if t == 'program_name':
                                row.append(__package_name__)
                            # elif t == 'script_name':
                            #     row.append(self.nmrstar_to_nef.__name__)
                            else:
                                row.append('.')
                        loop.add_data(row)
                    except KeyError:
                        pass

                if saveframe.category == 'spectral_peak_list' and has_pk_can_format and not has_pk_row_format:
                    cs_list_id = self.__star2nef_peak_can(saveframe, sf)
                    if cs_list_id is not None and (len(sf.get_tag('chemical_shift_list')) == 0 or sf.get_tag('chemical_shift_list') in emptyValue):
                        for cs_sf in star_data:
                            if cs_sf.get_tag('Sf_category')[0] == 'assigned_chemical_shifts' and cs_sf.get_tag('ID')[0] == cs_list_id and cs_sf.name not in emptyValue:
                                if len(sf.get_tag('chemical_shift_list')) == 0:
                                    sf.add_tag('chemical_shift_list', cs_sf.name)
                                else:
                                    sf.tags[sf.tags.index('chemical_shift_list')][1] = cs_sf.name
                                break

                nef_data.add_saveframe(sf)

        elif data_type in ('Saveframe', 'Loop'):

            if data_type == 'Saveframe':
                saveframe = star_data

                nef_sf_cat = self.get_nef_sf_cat(saveframe.category)

                if nef_sf_cat is not None:

                    sf_framecode = sf_framecode = get_nef_sf_framecode(saveframe, nef_sf_cat)

                    sf = pynmrstar.Saveframe.from_scratch(sf_framecode)

                    sf.set_tag_prefix(nef_sf_cat)

                    sf.add_tag('sf_category', nef_sf_cat)
                    sf.add_tag('sf_framecode', sf.name)

                    for tag in saveframe.tags:
                        tag_name = tag[0].lower()
                        if tag_name in ('sf_category', 'sf_framecode'):
                            continue
                        if saveframe.category == 'entry_information':
                            if tag_name == 'source_data_format':
                                sf.add_tag('format_name', NEF_FORMAT_NAME)
                            elif tag_name == 'source_data_format_version':
                                sf.add_tag('format_version', NEF_VERSION)
                            else:
                                nef_tag, _ = self.get_nef_tag(saveframe.tag_prefix + '.' + tag[0])
                                if nef_tag is not None:
                                    sf.add_tag(nef_tag, tag[1])
                        elif saveframe.category == 'general_distance_constraints' and tag_name == 'constraint_type':
                            nef_tag, _ = self.get_nef_tag(saveframe.tag_prefix + '.' + tag[0])
                            if nef_tag is not None:
                                sf.add_tag(nef_tag, tag[1] if tag[1] not in altDistanceConstraintType['nef'] else altDistanceConstraintType['nef'][tag[1]])
                        elif saveframe.category == 'torsion_angle_constraints' and tag_name == 'constraint_type':
                            nef_tag, _ = self.get_nef_tag(saveframe.tag_prefix + '.' + tag[0])
                            if nef_tag is not None:
                                sf.add_tag(nef_tag, tag[1] if tag[1] not in altDihedralAngleConstraintType['nef'] else altDihedralAngleConstraintType['nef'][tag[1]])
                        elif saveframe.category == 'RDC_constraints' and tag_name == 'constraint_type':
                            nef_tag, _ = self.get_nef_tag(saveframe.tag_prefix + '.' + tag[0])
                            if nef_tag is not None:
                                sf.add_tag(nef_tag, tag[1] if tag[1] not in altRdcConstraintType['nef'] else altRdcConstraintType['nef'][tag[1]])
                        else:
                            nef_tag, _ = self.get_nef_tag(saveframe.tag_prefix + '.' + tag[0])
                            if nef_tag is not None:
                                sf.add_tag(nef_tag, tag[1])

            else:

                if star_data.category == '_Software_applied_methods':
                    sf = pynmrstar.Saveframe.from_scratch('nef_nmr_meta_data')
                    sf.set_tag_prefix('nef_nmr_meta_data')
                    sf.add_tag('sf_category', 'nef_molecular_system')

                elif star_data.category == '_Assembly':
                    asm_id += 1
                    sf = pynmrstar.Saveframe.from_scratch('nef_molecular_system')
                    sf.set_tag_prefix('nef_molecular_system')
                    sf.add_tag('sf_category', 'nef_molecular_system')

                elif star_data.category == '_Atom_chem_shift':
                    cs_list_id += 1
                    sf = pynmrstar.Saveframe.from_scratch(f"nef_chemical_shift_list_{cs_list_id}")
                    sf.set_tag_prefix('nef_chemical_shift_list')
                    sf.add_tag('sf_category', 'nef_chemical_shift_list')

                elif star_data.category == '_Gen_dist_constraint':
                    dist_list_id += 1
                    sf = pynmrstar.Saveframe.from_scratch(f"nef_distance_restraint_list_{dist_list_id}")
                    sf.set_tag_prefix('nef_distance_restraint_list')
                    sf.add_tag('sf_category', 'nef_distance_restraint_list')

                elif star_data.category == '_Torsion_angle_constraint':
                    dihed_list_id += 1
                    sf = pynmrstar.Saveframe.from_scratch(f"nef_dihedral_restraint_list_{dihed_list_id}")
                    sf.set_tag_prefix('nef_dihedral_restraint_list')
                    sf.add_tag('sf_category', 'nef_dihedral_restraint_list')

                elif star_data.category == '_RDC_constraint':
                    rdc_list_id += 1
                    sf = pynmrstar.Saveframe.from_scratch(f"nef_rdc_restraint_list_{rdc_list_id}")
                    sf.set_tag_prefix('nef_rdc_restraint_list')
                    sf.add_tag('sf_category', 'nef_rdc_restraint_list')

                elif star_data.category == '_Peak_row_format':
                    peak_list_id += 1
                    sf = pynmrstar.Saveframe.from_scratch(f"nef_nmr_spectrum_{peak_list_id}")
                    sf.set_tag_prefix('nef_nmr_spectrum')
                    sf.add_tag('sf_category', 'nef_nmr_spectrum')

                else:
                    error.append(f"Loop category {star_data.category} is not supported.")
                    return False, {'info': info, 'error': error}

                sf.add_tag('sf_framecode', sf.name)

                saveframe = [star_data]

            entity_del_atom_loop = next((loop for loop in saveframe if loop.category == '_Entity_deleted_atom'), None)

            has_pk_can_format = has_pk_row_format = False

            for loop in saveframe:

                try:

                    lp = pynmrstar.Loop.from_scratch()
                    tags = self.get_nef_loop_tags(loop.get_tag_names())
                    tag_set = set(tags)
                    if len(tags) > len(tag_set):
                        tags = list(tag_set)

                    if len(tags) == 0:
                        continue

                    lp.add_tag(tags)

                    if loop.category == '_Chem_comp_assembly':
                        if self.authSeqMap is None:
                            self.authSeqMap = {}
                            self.selfSeqMap = {}
                        rows = self.__star2nef_seq_row(loop.get_tag_names(), lp.get_tag_names(), loop.data, report,
                                                       entity_del_atom_loop)
                        for d in rows:
                            lp.add_data(d)

                    elif loop.category == '_Atom_chem_shift':
                        if self.atomIdMap is None:
                            self.atomIdMap = {}

                        rows = self.__star2nef_cs_row(loop.get_tag_names(), lp.get_tag_names(), loop.data)
                        for d in rows:
                            lp.add_data(d)

                    elif loop.category == '_Gen_dist_constraint':
                        rows = self.__star2nef_dist_row(loop.get_tag_names(), lp.get_tag_names(), loop.data)
                        for d in rows:
                            lp.add_data(d)

                    elif loop.category == '_Peak_row_format':
                        rows = self.__star2nef_peak_row(loop.get_tag_names(), lp.get_tag_names(), loop.data)
                        for d in rows:
                            lp.add_data(d)
                        has_pk_row_format = True

                    elif len(tags) > 0:
                        for data in loop:
                            rows = self.__star2nef_row(loop.get_tag_names(), lp.get_tag_names(), data)
                            for d in rows:
                                lp.add_data(d)

                    elif loop.category == '_Peak':
                        has_pk_can_format = True

                    sf.add_loop(lp)

                except ValueError:
                    pass

            if sf.category == 'entry_information':
                has_format_name = has_format_ver = False
                for tags in sf.tags:
                    if tags[0] == 'format_name':
                        has_format_name = True
                    elif tags[0] == 'format_version':
                        has_format_ver = True

                if not has_format_name:
                    sf.add_tag('format_name', NEF_FORMAT_NAME)
                if not has_format_ver:
                    sf.add_tag('format_version', NEF_VERSION)

                try:
                    loop = sf.get_loop('_nef_program_script')
                    row = []
                    for t in loop.tags:
                        if t == 'program_name':
                            row.append(__package_name__)
                        # elif t == 'script_name':
                        #     row.append(self.nmrstar_to_nef.__name__)
                        else:
                            row.append('.')
                    loop.add_data(row)
                except KeyError:
                    pass

            if sf.category == 'spectral_peak_list' and has_pk_can_format and not has_pk_row_format:
                cs_list_id = self.__star2nef_peak_can(saveframe, sf)
                if cs_list_id is not None and (len(sf.get_tag('chemical_shift_list')) == 0
                                               or sf.get_tag('chemical_shift_list') in emptyValue):
                    for cs_sf in star_data:
                        if cs_sf.get_tag('Sf_category')[0] == 'assigned_chemical_shifts' and cs_sf.get_tag('ID')[0] == cs_list_id and cs_sf.name not in emptyValue:
                            if len(sf.get_tag('chemical_shift_list')) == 0:
                                sf.add_tag('chemical_shift_list', cs_sf.name)
                            else:
                                sf.tags[sf.tags.index('chemical_shift_list')][1] = cs_sf.name
                            break

            nef_data.add_saveframe(sf)

        self.__c2S.normalize_nef(nef_data)

        nef_data.write_to_file(nef_file, show_comments=False, skip_empty_loops=True, skip_empty_tags=False)

        info.append(f"File {nef_file} successfully written.")

        return True, {'info': info, 'error': error}
