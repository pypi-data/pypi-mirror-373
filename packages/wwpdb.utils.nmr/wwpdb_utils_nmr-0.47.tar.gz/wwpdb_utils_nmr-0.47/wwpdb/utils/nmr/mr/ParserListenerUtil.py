##
# File: ParserListenerUtil.py
# Date: 18-Feb-2022
#
# Updates:
# 13-Sep-2023  M. Yokochi - construct pseudo CCD from the coordinates (DAOTHER-8817)
# 29-Sep-2023  M. Yokochi - add atom name mapping dictionary (DAOTHER-8817, 8828)
# 24-Jan-2024  M. Yokochi - reconstruct polymer/non-polymer sequence based on pdb_mon_id, instead of auth_mon_id (D_1300043061)
# 04-Apr-2024  M. Yokochi - permit dihedral angle restraint across entities due to ligand split (DAOTHER-9063)
# 20-Aug-2024  M. Yokochi - support truncated loop sequence in the model (DAOTHER-9644)
# 10-Sep-2024  M. Yokochi - ignore identical polymer sequence extensions within polynucleotide multiplexes (DAOTHER-9674)
# 19-Nov-2024  M. Yokochi - add support for pH titration data (NMR restraint remediation)
# 06-Mar-2025  M. Yokochi - add support for coupling constant data (NMR restraint remediation Phase 2)
""" Utilities for MR/PT parser listener.
    @author: Masashi Yokochi
"""
__docformat__ = "restructuredtext en"
__author__ = "Masashi Yokochi"
__email__ = "yokochi@protein.osaka-u.ac.jp"
__license__ = "Apache License 2.0"
__version__ = "1.0.0"

import sys
import os
import re
import copy
import collections
import itertools
import numpy
import pynmrstar

from operator import itemgetter
from typing import Any, IO, List, Set, Tuple, Optional

from wwpdb.utils.align.alignlib import PairwiseAlign  # pylint: disable=no-name-in-module

try:
    from wwpdb.utils.nmr.io.CifReader import (SYMBOLS_ELEMENT,
                                              to_np_array)
    from wwpdb.utils.nmr.AlignUtil import (monDict3,
                                           emptyValue,
                                           protonBeginCode,
                                           pseProBeginCode,
                                           aminoProtonCode,
                                           LARGE_ASYM_ID,
                                           LEN_LARGE_ASYM_ID,
                                           MAX_MAG_IDENT_ASYM_ID,
                                           alignPolymerSequence,
                                           assignPolymerSequence,
                                           getScoreOfSeqAlign)
    from wwpdb.utils.nmr.CifToNmrStar import has_key_value
except ImportError:
    from nmr.io.CifReader import (SYMBOLS_ELEMENT,
                                  to_np_array)
    from nmr.AlignUtil import (monDict3,
                               emptyValue,
                               protonBeginCode,
                               pseProBeginCode,
                               aminoProtonCode,
                               LARGE_ASYM_ID,
                               LEN_LARGE_ASYM_ID,
                               MAX_MAG_IDENT_ASYM_ID,
                               alignPolymerSequence,
                               assignPolymerSequence,
                               getScoreOfSeqAlign)
    from nmr.CifToNmrStar import has_key_value

MAX_ERROR_REPORT = 1
MAX_ERR_LINENUM_REPORT = 20

# isotope numbers of NMR observable nucleus
ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS = {'H': [1, 2, 3],
                                   'C': [13],
                                   'N': [15, 14],
                                   'O': [17],
                                   'P': [31],
                                   'S': [33],
                                   'F': [19],
                                   'CD': [113, 111],
                                   'CA': [43]
                                   }

# isotope names of NMR observable nucleus
ISOTOPE_NAMES_OF_NMR_OBS_NUCS = []
for nuc_name, iso_nums in ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS.items():
    for iso_num in iso_nums:
        ISOTOPE_NAMES_OF_NMR_OBS_NUCS.append(f'{iso_num}{nuc_name}')
ISOTOPE_NAMES_OF_NMR_OBS_NUCS = tuple(ISOTOPE_NAMES_OF_NMR_OBS_NUCS)

# nucleus with half spin
HALF_SPIN_NUCLEUS = ('H', 'C', 'N', 'P', 'F', 'CD')


# allowed BMRB ambiguity codes
ALLOWED_AMBIGUITY_CODES = (1, 2, 3, 4, 5, 6, 9)


ALLOWED_ISOTOPE_NUMBERS = []
for isotopeNums in ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS.values():
    ALLOWED_ISOTOPE_NUMBERS.extend(isotopeNums)
ALLOWED_ISOTOPE_NUMBERS = tuple(ALLOWED_ISOTOPE_NUMBERS)

WELL_KNOWN_ISOTOPE_NUMBERS = copy.copy(ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS['H'])
WELL_KNOWN_ISOTOPE_NUMBERS.extend(ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS['C'])
WELL_KNOWN_ISOTOPE_NUMBERS.extend(ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS['N'])
WELL_KNOWN_ISOTOPE_NUMBERS.extend(ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS['P'])
WELL_KNOWN_ISOTOPE_NUMBERS = tuple(WELL_KNOWN_ISOTOPE_NUMBERS)


REPRESENTATIVE_MODEL_ID = 1

REPRESENTATIVE_ALT_ID = 'A'

MAX_PREF_LABEL_SCHEME_COUNT = 100

MAX_OFFSET_ATTEMPT = 1000

MAX_ALLOWED_EXT_SEQ = 2

MIN_EXT_SEQ_FOR_ATOM_SEL_ERR = 12

UNREAL_AUTH_SEQ_NUM = -10000

THRESHHOLD_FOR_CIRCULAR_SHIFT = 355.0

PLANE_LIKE_LOWER_LIMIT = -10.0
PLANE_LIKE_UPPER_LIMIT = 10.0


DIST_RESTRAINT_RANGE = {'min_inclusive': 0.0, 'max_inclusive': 101.0}
DIST_RESTRAINT_ERROR = {'min_exclusive': 0.0, 'max_exclusive': 150.0}


ANGLE_RESTRAINT_RANGE = {'min_inclusive': -420.0, 'max_inclusive': 420.0}  # 2n96, 5o4d, (400) 6gbm (420)
ANGLE_RESTRAINT_ERROR = {'min_exclusive': -450.0, 'max_exclusive': 450.0}


RDC_RESTRAINT_RANGE = {'min_inclusive': -150.0, 'max_inclusive': 150.0}
RDC_RESTRAINT_ERROR = {'min_exclusive': -200.0, 'max_exclusive': 200.0}


CS_RESTRAINT_RANGE = {'min_inclusive': -300.0, 'max_inclusive': 300.0}
CS_RESTRAINT_ERROR = {'min_exclusive': -999.0, 'max_exclusive': 999.0}


CSA_RESTRAINT_RANGE = {'min_inclusive': -300.0, 'max_inclusive': 300.0}
CSA_RESTRAINT_ERROR = {'min_exclusive': -999.0, 'max_exclusive': 999.0}


PCS_RESTRAINT_RANGE = {'min_inclusive': -20.0, 'max_inclusive': 20.0}
PCS_RESTRAINT_ERROR = {'min_exclusive': -40.0, 'max_exclusive': 40.0}


CCR_RESTRAINT_RANGE = {'min_inclusive': -10.0, 'max_inclusive': 10.0}
CCR_RESTRAINT_ERROR = {'min_exclusive': -20.0, 'max_exclusive': 20.0}


PRE_RESTRAINT_RANGE = {'min_inclusive': 0.0, 'max_inclusive': 200.0}
PRE_RESTRAINT_ERROR = {'min_exclusive': -5.0, 'max_exclusive': 10000.0}


T1T2_RESTRAINT_RANGE = {'min_inclusive': 0.0, 'max_inclusive': 20.0}
T1T2_RESTRAINT_ERROR = {'min_exclusive': -0.05, 'max_exclusive': 100.0}


CS_UNCERTAINTY_RANGE = {'min_inclusive': 0.0, 'max_inclusive': 3.0}

DIST_UNCERTAINTY_RANGE = {'min_inclusive': 0.0, 'max_inclusive': 5.0}

ANGLE_UNCERTAINTY_RANGE = {'min_inclusive': 0.0, 'max_inclusive': 90.0}

RDC_UNCERTAINTY_RANGE = {'min_inclusive': 0.0, 'max_inclusive': 5.0}

WEIGHT_RANGE = {'min_inclusive': 0.0, 'max_inclusive': 100.0}

SCALE_RANGE = {'min_inclusive': 0.0, 'max_inclusive': 100.0}

PROBABILITY_RANGE = {'min_inclusive': 0.0, 'max_inclusive': 1.0}


DIST_AMBIG_LOW = 1.0

DIST_AMBIG_BND = 4.0

DIST_AMBIG_MED = 6.0

DIST_AMBIG_UP = 12.0

DIST_AMBIG_UNCERT = 0.05


# @see: https://x3dna.org/highlights/torsion-angles-of-nucleic-acid-structures for nucleic acids
KNOWN_ANGLE_ATOM_NAMES = {'PHI': ['C', 'N', 'CA', 'C'],  # i-1, i, i, i
                          'PSI': ['N', 'CA', 'C', 'N'],  # i, i, i, i+1
                          'OMEGA': ['CA', 'C', 'N', 'CA'],  # i, i, i+1, i+1; modified CYANA definition [O C N (H or CD for Proline residue)]
                          'CHI1': ['N', 'CA', re.compile(r'CB1?'), re.compile(r'^[COS]G1?$')],  # DIV: [N, CA, CB1, CG1]
                          'CHI2': ['CA', 'CB', re.compile(r'^CG1?$'), re.compile(r'^[CNOS]D1?$')],
                          'CHI3': ['CB', 'CG', re.compile(r'^[CS]D$'), re.compile(r'^[CNO]E1?|N$')],
                          'CHI4': ['CG', 'CD', re.compile(r'^[CN]E$'), re.compile(r'^[CN]Z$')],
                          'CHI5': ['CD', 'NE', 'CZ', 'NH1'],
                          'CHI21': ['CA', 'CB', re.compile(r'^[CO]G1$'), re.compile(r'^CD1|HG11?$')],  # ILE: (CG1, CD1), THR: (OG1, HG1), VAL: (CD1, HG11)
                          'CHI22': ['CA', 'CB', 'CG2', 'HG21'],  # ILE or THR or VAL
                          'CHI31': ['CB', re.compile(r'^CG1?$'), 'CD1', 'HD11'],  # ILE: CG1, LEU: CG
                          'CHI32': ['CB', 'CG', re.compile(r'^[CO]D2$'), re.compile(r'^HD21?$')],  # ASP: (OD2, HD2), LEU: (CD2, HD21)
                          'CHI42': ['CG', 'CD', 'OE2', 'HE2'],  # GLU
                          'ALPHA': ["O3'", 'P', "O5'", "C5'"],  # i-1, i, i, i
                          'BETA': ['P', "O5'", "C5'", "C4'"],
                          'GAMMA': ["O5'", "C5'", "C4'", "C3'"],
                          'DELTA': ["C5'", "C4'", "C3'", "O3'"],
                          'EPSILON': ["C4'", "C3'", "O3'", 'P'],  # i, i, i, i+1
                          'ZETA': ["C3'", "O3'", 'P', "O5'"],  # i, i, i+1, i+1
                          # aka. CHIN (nucleic CHI angle)
                          'CHI': {'Y': ["O4'", "C1'", 'N1', 'C2'],  # for pyrimidines (i.e. C, T, U) N1/3
                                  'R': ["O4'", "C1'", 'N9', 'C4']  # for purines (i.e. G, A) N1/3/7/9
                                  },
                          'ETA': ["C4'", 'P', "C4'", 'P'],  # i-1, i, i, i+1
                          'THETA': ['P', "C4'", 'P', "C4'"],  # i, i, i+1, i+1
                          "ETA'": ["C1'", 'P', "C1'", 'P'],  # i-1, i, i, i+1
                          "THETA'": ['P', "C1'", 'P', "C1'"],  # i, i, i+1, i+1
                          'NU0': ["C4'", "O4'", "C1'", "C2'"],
                          'NU1': ["O4'", "C1'", "C2'", "C3'"],
                          'NU2': ["C1'", "C2'", "C3'", "C4'"],
                          'NU3': ["C2'", "C3'", "C4'", "O4'"],
                          'NU4': ["C3'", "C4'", "O4'", "C1'"],
                          'TAU0': ["C4'", "O4'", "C1'", "C2'"],  # identical to NU0
                          'TAU1': ["O4'", "C1'", "C2'", "C3'"],  # identical to NU1
                          'TAU2': ["C1'", "C2'", "C3'", "C4'"],  # identical to NU2
                          'TAU3': ["C2'", "C3'", "C4'", "O4'"],  # identical to NU3
                          'TAU4': ["C3'", "C4'", "O4'", "C1'"],  # identical to NU4
                          'PPA': ["C1'", "C2'", "C3'", "C4'", "O4'"]  # phase angle of pseudorotation made up from five NU[0-4] dihedral angles
                          }

# @see: http://dx.doi.org/10.1107/S0907444909001905
KNOWN_ANGLE_CARBO_ATOM_NAMES = {'PHI': [re.compile(r'^H1|O5$'), 'C1', re.compile(r'^O[14]$'), re.compile(r'^C[46]$')],
                                'PSI': ['C1', re.compile(r'^O[14]$'), re.compile(r'^C[46]$'), re.compile(r'^H4|C[35]$')],
                                'OMEGA': [re.compile(r'^O[14]$'), 'C6', 'C5', re.compile('^H5|C4|O5$')]}

KNOWN_ANGLE_NAMES = KNOWN_ANGLE_ATOM_NAMES.keys()

KNOWN_ANGLE_SEQ_OFFSET = {'PHI': [-1, 0, 0, 0],  # i-1, i, i, i
                          'PSI': [0, 0, 0, 1],  # i, i, i, i+1
                          'OMEGA': [0, 0, 1, 1],  # i, i, i+1, i+1; modified CYANA definition [O C N (H or CD for Proline residue)]
                          'CHI1': [0] * 4,
                          'CHI2': [0] * 4,
                          'CHI3': [0] * 4,
                          'CHI4': [0] * 4,
                          'CHI5': [0] * 4,
                          'CHI21': [0] * 4,  # ILE: (CG1, CD1), THR: (OG1, HG1), VAL: (CD1, HG11)
                          'CHI22': [0] * 4,  # ILE or THR or VAL
                          'CHI31': [0] * 4,  # ILE: CG1, LEU: CG
                          'CHI32': [0] * 4,  # ASP: (OD2, HD2), LEU: (CD2, HD21)
                          'CHI42': [0] * 4,  # GLU
                          'ALPHA': [-1, 0, 0, 0],  # i-1, i, i, i
                          'BETA': [0] * 4,
                          'GAMMA': [0] * 4,
                          'DELTA': [0] * 4,
                          'EPSILON': [0, 0, 0, 1],  # i, i, i, i+1
                          'ZETA': [0, 0, 1, 1],  # i, i, i+1, i+1
                          # aka. CHIN (nucleic CHI angle)
                          'CHI': {'Y': [0] * 4,  # for pyrimidines (i.e. C, T, U) N1/3
                                  'R': [0] * 4  # for purines (i.e. G, A) N1/3/7/9
                                  },
                          'ETA': [-1, 0, 0, 1],  # i-1, i, i, i+1
                          'THETA': [0, 0, 1, 1],  # i, i, i+1, i+1
                          "ETA'": [-1, 0, 0, 1],  # i-1, i, i, i+1
                          "THETA'": [0, 0, 1, 1],  # i, i, i+1, i+1
                          'NU0': [0] * 4,
                          'NU1': [0] * 4,
                          'NU2': [0] * 4,
                          'NU3': [0] * 4,
                          'NU4': [0] * 4,
                          'TAU0': [0] * 4,  # identical to NU0
                          'TAU1': [0] * 4,  # identical to NU1
                          'TAU2': [0] * 4,  # identical to NU2
                          'TAU3': [0] * 4,  # identical to NU3
                          'TAU4': [0] * 4,  # identical to NU4
                          'PPA': [0] * 5  # phase angle of pseudorotation made up from five NU[0-4] dihedral angles
                          }

KNOWN_ANGLE_CARBO_SEQ_OFFSET = {'PHI': [0, 0, 0, -1],  # i, i, i, i-n; for n > 0
                                'PSI': [0, 0, -1, -1],  # i, i, i-n, i-n; for n > 0
                                'OMEGA': [0, -1, -1, -1]  # i, i-n, i-n, i-n; for n > 0
                                }

XPLOR_RDC_PRINCIPAL_AXIS_NAMES = ('OO', 'X', 'Y', 'Z')

XPLOR_ORIGIN_AXIS_COLS = (0, 1, 2, 3)

XPLOR_NITROXIDE_NAMES = ('NO', 'NX', 'NR', 'NAI', 'NAQ', 'NS1', 'OS', 'OS1', 'OAH', 'SLC', 'GD')

NITROOXIDE_ANCHOR_RES_NAMES = ('CYS', 'SER', 'GLU', 'ASP', 'GLN', 'ASN', 'LYS', 'THR', 'HIS',
                               'ILE', 'LEU', 'MET', 'R1A')

HEME_LIKE_RES_NAMES = ('HEM', 'HEB', 'HEC', 'MH0')

LEGACY_PDB_RECORDS = ('HEADER', 'OBSLTE', 'TITLE ', 'SPLIT ', 'CAVEAT', 'COMPND', 'SOURCE', 'KEYWDS', 'EXPDTA',
                      'NUMMDL', 'MDLTYP', 'AUTHOR', 'REVDAT', 'SPRSDE', 'JRNL', 'REMARK',
                      'DBREF', 'DBREF1', 'DBREF2', 'SEQADV', 'SEQRES', 'MODRES',
                      'HET ', 'HETNAM', 'HETSYN', 'FORMUL',
                      'HELIX ', 'SHEET ',
                      'SSBOND', 'LINK ', 'CISPEP',
                      'SITE ',
                      'CRYST1', 'ORIGX1', 'ORIGX2', 'ORIGX3', 'SCALE1', 'SCALE2', 'SCALE3',
                      'MTRIX1', 'MTRIX2', 'MTRIX3',
                      'MODEL ', 'ATOM ', 'ANISOU', 'TER ', 'HETATM', 'ENDMDL',
                      'CONECT',
                      'MASTER')

LEGACY_PDB_RECORDS_WO_REMARK = [record for record in LEGACY_PDB_RECORDS if record != 'REMARK']
LEGACY_PDB_RECORDS_WO_REMARK = tuple(LEGACY_PDB_RECORDS_WO_REMARK)

CYANA_MR_FILE_EXTS = (None, 'upl', 'lol', 'aco', 'rdc', 'pcs', 'upv', 'lov', 'cco')

# limit number of dimensions, note: defined MAX_DIM_NUM_OF_SPECTRA here to avoid circular import
MAX_DIM_NUM_OF_SPECTRA = 16

NMR_STAR_SF_TAG_PREFIXES = {'dist_restraint': '_Gen_dist_constraint_list',
                            'dihed_restraint': '_Torsion_angle_constraint_list',
                            'rdc_restraint': '_RDC_constraint_list',
                            'noepk_restraint': '_Homonucl_NOE_list',
                            'jcoup_restraint': '_J_three_bond_constraint_list',
                            'rdc_raw_data': '_RDC_list',
                            'csa_restraint': '_Chem_shift_anisotropy',
                            'ddc_restraint': '_Dipolar_coupling_list',
                            'hvycs_restraint': '_CA_CB_constraint_list',
                            'procs_restraint': '_H_chem_shift_constraint_list',
                            'csp_restraint': '_Chem_shift_perturbation_list',
                            'auto_relax_restraint': '_Auto_relaxation_list',
                            'heteronucl_noe_data': '_Heteronucl_NOE_list',
                            'heteronucl_t1_data': '_Heteronucl_T1_list',
                            'heteronucl_t2_data': '_Heteronucl_T2_list',
                            'heteronucl_t1r_data': '_Heteronucl_T1rho_list',
                            'order_param_data': '_Order_parameter_list',
                            'ph_titr_data': '_PH_titration_list',
                            'ph_param_data': '_PH_param_list',
                            'coupling_const_data': '_Coupling_constant_list',
                            'ccr_d_csa_restraint': '_Cross_correlation_D_CSA_list',
                            'ccr_dd_restraint': '_Cross_correlation_DD_list',
                            'fchiral_restraint': '_Floating_chirality_assign',
                            'saxs_restraint': '_SAXS_constraint_list',
                            'other_restraint': '_Other_data_type_list',
                            'spectral_peak': '_Spectral_peak_list',
                            'chem_shift': '_Assigned_chem_shift_list'
                            }

NMR_STAR_SF_CATEGORIES = {'dist_restraint': 'general_distance_constraints',
                          'dihed_restraint': 'torsion_angle_constraints',
                          'rdc_restraint': 'RDC_constraints',
                          'noepk_restraint': 'homonucl_NOEs',
                          'jcoup_restraint': 'J_three_bond_constraints',
                          'rdc_raw_data': 'RDCs',
                          'csa_restraint': 'chem_shift_anisotropy',
                          'ddc_restraint': 'dipolar_couplings',
                          'hvycs_restraint': 'CA_CB_chem_shift_constraints',
                          'procs_restraint': 'H_chem_shift_constraints',
                          'csp_restraint': 'chem_shift_perturbation',
                          'auto_relax_restraint': 'auto_relaxation',
                          'heteronucl_noe_data': 'heteronucl_NOEs',
                          'heteronucl_t1_data': 'heteronucl_T1_relaxation',
                          'heteronucl_t2_data': 'heteronucl_T2_relaxation',
                          'heteronucl_t1r_data': 'heteronucl_T1rho_relaxation',
                          'order_param_data': 'order_parameters',
                          'ph_titr_data': 'pH_titration',
                          'ph_param_data': 'pH_param_list',
                          'coupling_const_data': 'coupling_constants',
                          'ccr_d_csa_restraint': 'dipole_CSA_cross_correlations',
                          'ccr_dd_restraint': 'dipole_dipole_cross_correlations',
                          'fchiral_restraint': 'floating_chiral_stereo_assign',
                          'saxs_restraint': 'saxs_constraints',
                          'other_restraint': 'other_data_types',
                          'spectral_peak': 'spectral_peak_list',
                          'chem_shift': 'assigned_chemical_shifts'
                          }

NMR_STAR_SF_TAG_ITEMS = {'dist_restraint': [{'name': 'Sf_category', 'type': 'str', 'mandatory': True},
                                            {'name': 'Sf_framecode', 'type': 'str', 'mandatory': True},
                                            {'name': 'Constraint_type', 'type': 'enum', 'mandatory': False,
                                             'enum': ('NOE', 'NOE build-up', 'NOE not seen', 'ROE', 'ROE build-up',
                                                      'hydrogen bond', 'disulfide bond', 'paramagnetic relaxation',
                                                      'symmetry', 'general distance', 'mutation', 'chemical shift perturbation',
                                                      'undefined', 'unknown')},
                                            {'name': 'Potential_type', 'type': 'enum', 'mandatory': False,
                                             'enum': ('log-harmonic', 'parabolic', 'square-well-parabolic',
                                                      'square-well-parabolic-linear', 'upper-bound-parabolic',
                                                      'lower-bound-parabolic', 'upper-bound-parabolic-linear',
                                                      'lower-bound-parabolic-linear', 'undefined', 'unknown')},
                                            {'name': 'Details', 'type': 'str', 'mandatory': False},
                                            {'name': 'Data_file_name', 'type': 'str', 'mandatory': False},
                                            {'name': 'ID', 'type': 'positive-int', 'mandatory': True},
                                            {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                            ],
                         'dihed_restraint': [{'name': 'Sf_category', 'type': 'str', 'mandatory': True},
                                             {'name': 'Sf_framecode', 'type': 'str', 'mandatory': True},
                                             {'name': 'Constraint_type', 'type': 'enum', 'mandatory': False,
                                              'enum': ('J-couplings', 'backbone chemical shifts', 'undefined', 'unknown')},
                                             {'name': 'Potential_type', 'type': 'enum', 'mandatory': False,
                                              'enum': ('parabolic', 'square-well-parabolic', 'square-well-parabolic-linear',
                                                       'upper-bound-parabolic', 'lower-bound-parabolic', 'upper-bound-parabolic-linear',
                                                       'lower-bound-parabolic-linear', 'undefined', 'unknown')},
                                             {'name': 'Details', 'type': 'str', 'mandatory': False},
                                             {'name': 'Data_file_name', 'type': 'str', 'mandatory': False},
                                             {'name': 'ID', 'type': 'positive-int', 'mandatory': True},
                                             {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                             ],
                         'rdc_restraint': [{'name': 'Sf_category', 'type': 'str', 'mandatory': True},
                                           {'name': 'Sf_framecode', 'type': 'str', 'mandatory': True},
                                           {'name': 'Constraint_type', 'type': 'enum', 'mandatory': False,
                                            'enum': ('RDC', 'undefined', 'unknown')},
                                           {'name': 'Potential_type', 'type': 'enum', 'mandatory': False,
                                            'enum': ('parabolic', 'square-well-parabolic', 'square-well-parabolic-linear',
                                                     'upper-bound-parabolic', 'lower-bound-parabolic', 'upper-bound-parabolic-linear',
                                                     'lower-bound-parabolic-linear', 'undefined', 'unknown')},
                                           {'name': 'Tensor_magnitude', 'type': 'float', 'mandatory': False},
                                           {'name': 'Tensor_rhombicity', 'type': 'positive-float', 'mandatory': False},
                                           {'name': 'Tensor_auth_asym_ID', 'type': 'str', 'mandatory': False},
                                           {'name': 'Tensor_auth_seq_ID', 'type': 'str', 'mandatory': False},
                                           {'name': 'Tensor_auth_comp_ID', 'type': 'str', 'mandatory': False},
                                           {'name': 'Details', 'type': 'str', 'mandatory': False},
                                           {'name': 'Data_file_name', 'type': 'str', 'mandatory': False},
                                           {'name': 'ID', 'type': 'positive-int', 'mandatory': True},
                                           {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                           ],
                         'noepk_restraint': [{'name': 'Sf_category', 'type': 'str', 'mandatory': True},
                                             {'name': 'Sf_framecode', 'type': 'str', 'mandatory': True},
                                             {'name': 'Homonuclear_NOE_val_type', 'type': 'enum', 'mandatory': True,
                                              'enum': ('peak volume', 'peak height', 'contour count', 'na')},
                                             {'name': 'Details', 'type': 'str', 'mandatory': False},
                                             {'name': 'Data_file_name', 'type': 'str', 'mandatory': False},
                                             {'name': 'ID', 'type': 'int', 'mandatory': True},  # allows to have software-native id starting from zero
                                             {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                             ],
                         'jcoup_restraint': [{'name': 'Sf_category', 'type': 'str', 'mandatory': True},
                                             {'name': 'Sf_framecode', 'type': 'str', 'mandatory': True},
                                             {'name': 'Details', 'type': 'str', 'mandatory': False},
                                             {'name': 'Data_file_name', 'type': 'str', 'mandatory': False},
                                             {'name': 'ID', 'type': 'positive-int', 'mandatory': True},
                                             {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                             ],
                         'rdc_raw_data': [{'name': 'Sf_category', 'type': 'str', 'mandatory': True},
                                          {'name': 'Sf_framecode', 'type': 'str', 'mandatory': True},
                                          {'name': 'Spectrometer_frequency_1H', 'type': 'positive-float', 'mandatory': False,
                                           'enforce-non-zero': True},
                                          {'name': 'Details', 'type': 'str', 'mandatory': False},
                                          {'name': 'Data_file_name', 'type': 'str', 'mandatory': False},
                                          {'name': 'ID', 'type': 'positive-int', 'mandatory': True},
                                          {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                          ],
                         'csa_restraint': [{'name': 'Sf_category', 'type': 'str', 'mandatory': True},
                                           {'name': 'Sf_framecode', 'type': 'str', 'mandatory': True},
                                           {'name': 'Spectrometer_frequency_1H', 'type': 'positive-float', 'mandatory': False,
                                            'enforce-non-zero': True},
                                           {'name': 'Val_units', 'type': 'enum', 'mandatory': False,
                                            'enum': ('ppm', 'ppb')},
                                           {'name': 'Details', 'type': 'str', 'mandatory': False},
                                           {'name': 'Data_file_name', 'type': 'str', 'mandatory': False},
                                           {'name': 'ID', 'type': 'positive-int', 'mandatory': True},
                                           {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                           ],
                         'ddc_restraint': [{'name': 'Sf_category', 'type': 'str', 'mandatory': True},
                                           {'name': 'Sf_framecode', 'type': 'str', 'mandatory': True},
                                           {'name': 'Spectrometer_frequency_1H', 'type': 'positive-float', 'mandatory': False,
                                            'enforce-non-zero': True},
                                           {'name': 'Scaling_factor', 'type': 'positive-float', 'mandatory': False},
                                           {'name': 'Fitting_procedure', 'type': 'str', 'mandatory': False},
                                           {'name': 'Details', 'type': 'str', 'mandatory': False},
                                           {'name': 'Data_file_name', 'type': 'str', 'mandatory': False},
                                           {'name': 'ID', 'type': 'positive-int', 'mandatory': True},
                                           {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                           ],
                         'hvycs_restraint': [{'name': 'Sf_category', 'type': 'str', 'mandatory': True},
                                             {'name': 'Sf_framecode', 'type': 'str', 'mandatory': True},
                                             {'name': 'Units', 'type': 'str', 'mandatory': False},
                                             {'name': 'Details', 'type': 'str', 'mandatory': False},
                                             {'name': 'Data_file_name', 'type': 'str', 'mandatory': False},
                                             {'name': 'ID', 'type': 'positive-int', 'mandatory': True},
                                             {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                             ],
                         'procs_restraint': [{'name': 'Sf_category', 'type': 'str', 'mandatory': True},
                                             {'name': 'Sf_framecode', 'type': 'str', 'mandatory': True},
                                             {'name': 'Units', 'type': 'str', 'mandatory': False},
                                             {'name': 'Details', 'type': 'str', 'mandatory': False},
                                             {'name': 'Data_file_name', 'type': 'str', 'mandatory': False},
                                             {'name': 'ID', 'type': 'positive-int', 'mandatory': True},
                                             {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                             ],
                         'csp_restraint': [{'name': 'Sf_category', 'type': 'str', 'mandatory': True},
                                           {'name': 'Sf_framecode', 'type': 'str', 'mandatory': True},
                                           {'name': 'Type', 'type': 'enum', 'mandatory': False,
                                            'enum': ('macromolecular binding', 'ligand binding', 'ligand fragment binding', 'paramagnetic ligand binding')},
                                           {'name': 'Details', 'type': 'str', 'mandatory': False},
                                           {'name': 'Data_file_name', 'type': 'str', 'mandatory': False},
                                           {'name': 'ID', 'type': 'positive-int', 'mandatory': True},
                                           {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                           ],
                         'auto_relax_restraint': [{'name': 'Sf_category', 'type': 'str', 'mandatory': True},
                                                  {'name': 'Sf_framecode', 'type': 'str', 'mandatory': True},
                                                  {'name': 'Temp_calibration_method', 'type': 'enum', 'mandatory': False,
                                                   'enum': ('methanol', 'monoethylene glycol', 'no calibration applied')},
                                                  {'name': 'Temp_control_method', 'type': 'enum', 'mandatory': False,
                                                   'enum': ('single scan interleaving', 'temperature compensation block',
                                                            'single scan interleaving and temperature compensation block',
                                                            'no temperature control applied')},
                                                  {'name': 'Spectrometer_frequency_1H', 'type': 'positive-float', 'mandatory': False,
                                                   'enforce-non-zero': True},
                                                  {'name': 'Exact_field_strength', 'type': 'positive-float', 'mandatory': False,
                                                   'enforce-non-zero': True},
                                                  {'name': 'Common_relaxation_type_name', 'type': 'enum', 'mandatory': False,
                                                   'enum': ('R1', 'R2', 'R1rho', 'ZQ relaxation', 'longitudinal spin order',
                                                            'single quantum antiphase', 'DQ relaxation')},
                                                  {'name': 'Relaxation_coherence_type', 'type': 'enum', 'mandatory': True,
                                                   'enum': ('Iz', 'Sz', '(I+)+(I-)', '(S+)+(S-)', 'I+', 'I-', 'S+', 'S-',
                                                            '(I+S-)+(I-S+)', 'I-S+', 'I+S-', 'IzSz', '((I+)+(I-))Sz', 'Iz((S+)+(S-))',
                                                            'I+Sz', 'I-Sz', 'IzS+', 'IzS-', '(I+S+)+(I-S-)', 'I+S+', 'I-S-')},
                                                  {'name': 'Relaxation_val_units', 'type': 'enum', 'mandatory': True,
                                                   'enum': ('s-1', 'ms-1', 'us-1', 'ns-1', 'ps-1')},
                                                  {'name': 'Rex_units', 'type': 'enum', 'mandatory': False,
                                                   'enum': ('s-1', 'ms-1', 'us-1')},
                                                  {'name': 'Rex_field_strength', 'type': 'positive-float', 'mandatory': False,
                                                   'enforce-non-zero': True},
                                                  {'name': 'Details', 'type': 'str', 'mandatory': False},
                                                  {'name': 'Data_file_name', 'type': 'str', 'mandatory': False},
                                                  {'name': 'ID', 'type': 'positive-int', 'mandatory': True},
                                                  {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                                  ],
                         'heteronucl_noe_data': [{'name': 'Sf_category', 'type': 'str', 'mandatory': True},
                                                 {'name': 'Sf_framecode', 'type': 'str', 'mandatory': True},
                                                 {'name': 'Spectrometer_frequency_1H', 'type': 'positive-float', 'mandatory': False,
                                                  'enforce-non-zero': True},
                                                 {'name': 'Heteronuclear_NOE_val_type', 'type': 'enum', 'mandatory': True,
                                                  'enum': ('peak height', 'peak integral', 'contour count', 'relative intensities', 'na')},
                                                 {'name': 'Details', 'type': 'str', 'mandatory': False},
                                                 {'name': 'Data_file_name', 'type': 'str', 'mandatory': False},
                                                 {'name': 'ID', 'type': 'positive-int', 'mandatory': True},
                                                 {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                                 ],
                         'heteronucl_t1_data': [{'name': 'Sf_category', 'type': 'str', 'mandatory': True},
                                                {'name': 'Sf_framecode', 'type': 'str', 'mandatory': True},
                                                {'name': 'Spectrometer_frequency_1H', 'type': 'positive-float', 'mandatory': False,
                                                 'enforce-non-zero': True},
                                                {'name': 'T1_coherence_type', 'type': 'enum', 'mandatory': True,
                                                 'enum': ('Iz', 'Sz', 'na')},
                                                {'name': 'T1_val_units', 'type': 'enum', 'mandatory': True,
                                                 'enum': ('s', 's-1', 'ms', 'ms-1')},
                                                {'name': 'Details', 'type': 'str', 'mandatory': False},
                                                {'name': 'Data_file_name', 'type': 'str', 'mandatory': False},
                                                {'name': 'ID', 'type': 'positive-int', 'mandatory': True},
                                                {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                                ],
                         'heteronucl_t2_data': [{'name': 'Sf_category', 'type': 'str', 'mandatory': True},
                                                {'name': 'Sf_framecode', 'type': 'str', 'mandatory': True},
                                                {'name': 'Temp_calibration_method', 'type': 'enum', 'mandatory': False,
                                                 'enum': ('methanol', 'monoethylene glycol', 'no calibration applied')},
                                                {'name': 'Temp_control_method', 'type': 'enum', 'mandatory': False,
                                                 'enum': ('single scan interleaving', 'temperature compensation block',
                                                          'single scan interleaving and temperature compensation block',
                                                          'no temperature control applied')},
                                                {'name': 'Spectrometer_frequency_1H', 'type': 'positive-float', 'mandatory': False,
                                                 'enforce-non-zero': True},
                                                {'name': 'T2_coherence_type', 'type': 'enum', 'mandatory': True,
                                                 'enum': ('I(+,-)', 'S(+,-)', 'na')},
                                                {'name': 'T2_val_units', 'type': 'enum', 'mandatory': True,
                                                 'enum': ('s', 's-1', 'ms', 'ms-1')},
                                                {'name': 'Rex_units', 'type': 'enum', 'mandatory': False,
                                                 'enum': ('s-1', 'ms-1', 'us-1')},
                                                {'name': 'Details', 'type': 'str', 'mandatory': False},
                                                {'name': 'Data_file_name', 'type': 'str', 'mandatory': False},
                                                {'name': 'ID', 'type': 'positive-int', 'mandatory': True},
                                                {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                                ],
                         'heteronucl_t1r_data': [{'name': 'Sf_category', 'type': 'str', 'mandatory': True},
                                                 {'name': 'Sf_framecode', 'type': 'str', 'mandatory': True},
                                                 {'name': 'Temp_calibration_method', 'type': 'enum', 'mandatory': False,
                                                  'enum': ('methanol', 'monoethylene glycol', 'no calibration applied')},
                                                 {'name': 'Temp_control_method', 'type': 'enum', 'mandatory': False,
                                                  'enum': ('single scan interleaving', 'temperature compensation block',
                                                           'single scan interleaving and temperature compensation block',
                                                           'no temperature control applied')},
                                                 {'name': 'Spectrometer_frequency_1H', 'type': 'positive-float', 'mandatory': False,
                                                  'enforce-non-zero': True},
                                                 {'name': 'T1rho_coherence_type', 'type': 'enum', 'mandatory': True,
                                                  'enum': ('I(+,-)', 'S(+,-)', 'na')},
                                                 {'name': 'T1rho_val_units', 'type': 'enum', 'mandatory': True,
                                                  'enum': ('s', 's-1', 'ms', 'ms-1')},
                                                 {'name': 'Rex_units', 'type': 'enum', 'mandatory': False,
                                                  'enum': ('s-1', 'ms-1', 'us-1')},
                                                 {'name': 'Details', 'type': 'str', 'mandatory': False},
                                                 {'name': 'Data_file_name', 'type': 'str', 'mandatory': False},
                                                 {'name': 'ID', 'type': 'positive-int', 'mandatory': True},
                                                 {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                                 ],
                         'order_param_data': [{'name': 'Sf_category', 'type': 'str', 'mandatory': True},
                                              {'name': 'Sf_framecode', 'type': 'str', 'mandatory': True},
                                              {'name': 'Tau_e_val_units', 'type': 'enum', 'mandatory': False,
                                               'enum': ('s', 'ms', 'us', 'ns', 'ps')},
                                              {'name': 'Tau_f_val_units', 'type': 'enum', 'mandatory': False,
                                               'enum': ('s', 'ms', 'us', 'ns', 'ps')},
                                              {'name': 'Tau_s_val_units', 'type': 'enum', 'mandatory': False,
                                               'enum': ('s', 'ms', 'us', 'ns', 'ps')},
                                              {'name': 'Rex_val_units', 'type': 'enum', 'mandatory': False,
                                               'enum': ('s-1', 'ms-1', 'us-1')},
                                              {'name': 'Rex_field_strength', 'type': 'positive-float', 'mandatory': False,
                                               'enforce-non-zero': True},
                                              {'name': 'Details', 'type': 'str', 'mandatory': False},
                                              {'name': 'Data_file_name', 'type': 'str', 'mandatory': False},
                                              {'name': 'ID', 'type': 'positive-int', 'mandatory': True},
                                              {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                              ],
                         'ph_titr_data': [{'name': 'Sf_category', 'type': 'str', 'mandatory': True},
                                          {'name': 'Sf_framecode', 'type': 'str', 'mandatory': True},
                                          {'name': 'Expt_observed_param', 'type': 'enum', 'mandatory': True,
                                           'enum': ('chemical shift', 'coupling constant', 'peak height', 'peak volume')},
                                          {'name': 'Details', 'type': 'str', 'mandatory': False},
                                          {'name': 'Data_file_name', 'type': 'str', 'mandatory': False},
                                          {'name': 'ID', 'type': 'positive-int', 'mandatory': True},
                                          {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                          ],
                         'ph_param_data': [{'name': 'Sf_category', 'type': 'str', 'mandatory': True},
                                           {'name': 'Sf_framecode', 'type': 'str', 'mandatory': True},
                                           {'name': 'Observed_NMR_param', 'type': 'enum', 'mandatory': True,
                                            'enum': ('chemical shift', 'coupling constant', 'peak height', 'peak volume')},
                                           {'name': 'PH_titration_list_ID', 'type': 'positive-int', 'mandatory': True,
                                            'default': '1'},
                                           {'name': 'Details', 'type': 'str', 'mandatory': False},
                                           {'name': 'Data_file_name', 'type': 'str', 'mandatory': False},
                                           {'name': 'ID', 'type': 'positive-int', 'mandatory': True},
                                           {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                           ],
                         'coupling_const_data': [{'name': 'Sf_category', 'type': 'str', 'mandatory': True},
                                                 {'name': 'Sf_framecode', 'type': 'str', 'mandatory': True},
                                                 {'name': 'Spectrometer_frequency_1H', 'type': 'positive-float', 'mandatory': False,
                                                  'enforce-non-zero': True},
                                                 {'name': 'Details', 'type': 'str', 'mandatory': False},
                                                 {'name': 'Data_file_name', 'type': 'str', 'mandatory': False},
                                                 {'name': 'ID', 'type': 'positive-int', 'mandatory': True},
                                                 {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                                 ],
                         'ccr_d_csa_restraint': [{'name': 'Sf_category', 'type': 'str', 'mandatory': True},
                                                 {'name': 'Sf_framecode', 'type': 'str', 'mandatory': True},
                                                 {'name': 'Spectrometer_frequency_1H', 'type': 'positive-float', 'mandatory': False,
                                                  'enforce-non-zero': True},
                                                 {'name': 'Val_units', 'type': 'enum', 'mandatory': True,
                                                  'enum': ('s-1', 'ms-1', 'us-1')},
                                                 {'name': 'Details', 'type': 'str', 'mandatory': False},
                                                 {'name': 'Data_file_name', 'type': 'str', 'mandatory': False},
                                                 {'name': 'ID', 'type': 'positive-int', 'mandatory': True},
                                                 {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                                 ],
                         'ccr_dd_restraint': [{'name': 'Sf_category', 'type': 'str', 'mandatory': True},
                                              {'name': 'Sf_framecode', 'type': 'str', 'mandatory': True},
                                              {'name': 'Spectrometer_frequency_1H', 'type': 'positive-float', 'mandatory': False,
                                               'enforce-non-zero': True},
                                              {'name': 'Val_units', 'type': 'enum', 'mandatory': True,
                                               'enum': ('s-1', 'ms-1', 'us-1')},
                                              {'name': 'Details', 'type': 'str', 'mandatory': False},
                                              {'name': 'Data_file_name', 'type': 'str', 'mandatory': False},
                                              {'name': 'ID', 'type': 'positive-int', 'mandatory': True},
                                              {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                              ],
                         'fchiral_restraint': [{'name': 'Sf_category', 'type': 'str', 'mandatory': True},
                                               {'name': 'Sf_framecode', 'type': 'str', 'mandatory': True},
                                               {'name': 'Stereo_count', 'type': 'int', 'mandatory': False},
                                               {'name': 'Stereo_assigned_count', 'type': 'int', 'mandatory': True},
                                               {'name': 'Details', 'type': 'str', 'mandatory': False},
                                               {'name': 'Data_file_name', 'type': 'str', 'mandatory': False},
                                               {'name': 'ID', 'type': 'positive-int', 'mandatory': True},
                                               {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                               ],
                         'saxs_restraint': [{'name': 'Sf_category', 'type': 'str', 'mandatory': True},
                                            {'name': 'Sf_framecode', 'type': 'str', 'mandatory': True},
                                            {'name': 'Details', 'type': 'str', 'mandatory': False},
                                            {'name': 'Data_file_name', 'type': 'str', 'mandatory': False},
                                            {'name': 'ID', 'type': 'positive-int', 'mandatory': True},
                                            {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                            ],
                         'other_restraint': [{'name': 'Sf_category', 'type': 'str', 'mandatory': True},
                                             {'name': 'Sf_framecode', 'type': 'str', 'mandatory': True},
                                             {'name': 'Definition', 'type': 'str', 'mandatory': True},
                                             {'name': 'Details', 'type': 'str', 'mandatory': False},
                                             {'name': 'Data_file_name', 'type': 'str', 'mandatory': False},
                                             {'name': 'ID', 'type': 'positive-int', 'mandatory': True},
                                             {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                             ],
                         'spectral_peak': [{'name': 'Sf_category', 'type': 'str', 'mandatory': True},
                                           {'name': 'Sf_framecode', 'type': 'str', 'mandatory': True},
                                           {'name': 'Number_of_spectral_dimensions', 'type': 'enum-int', 'mandatory': True,
                                            'enum': set(range(1, MAX_DIM_NUM_OF_SPECTRA)),
                                            'enforce-enum': True},
                                           {'name': 'Experiment_class', 'type': 'str', 'mandatory': False},
                                           {'name': 'Experiment_type', 'type': 'str', 'mandatory': False},
                                           {'name': 'Chemical_shift_list', 'type': 'str', 'mandatory': True},
                                           {'name': 'Details', 'type': 'str', 'mandatory': False},
                                           {'name': 'Data_file_name', 'type': 'str', 'mandatory': False},
                                           {'name': 'ID', 'type': 'int', 'mandatory': True},  # allows to have software-native id starting from zero
                                           {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                           ],
                         'chem_shift': [{'name': 'Sf_category', 'type': 'str', 'mandatory': True},
                                        {'name': 'Sf_framecode', 'type': 'str', 'mandatory': True},
                                        {'name': 'Details', 'type': 'str', 'mandatory': False},
                                        {'name': 'Data_file_name', 'type': 'str', 'mandatory': False},
                                        {'name': 'ID', 'type': 'positive-int', 'mandatory': True},
                                        {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                        ]
                         }

NMR_STAR_LP_CATEGORIES = {'dist_restraint': '_Gen_dist_constraint',
                          'dihed_restraint': '_Torsion_angle_constraint',
                          'rdc_restraint': '_RDC_constraint',
                          'noepk_restraint': '_Homonucl_NOE',
                          'jcoup_restraint': '_J_three_bond_constraint',
                          'rdc_raw_data': '_RDC',
                          'csa_restraint': '_CS_anisotropy',
                          'ddc_restraint': '_Dipolar_coupling',
                          'hvycs_restraint': '_CA_CB_constraint',
                          'procs_restraint': '_H_chem_shift_constraint',
                          'csp_restraint': '_Chem_shift_perturbation',
                          'auto_relax_restraint': '_Auto_relaxation',
                          'heteronucl_noe_data': '_Heteronucl_NOE',
                          'heteronucl_t1_data': '_T1',
                          'heteronucl_t2_data': '_T2',
                          'heteronucl_t1r_data': '_T1rho',
                          'order_param_data': '_Order_param',
                          'ph_titr_data': '_PH_titr_result',
                          'ph_param_data': '_PH_param',
                          'coupling_const_data': '_Coupling_constant',
                          'ccr_d_csa_restraint': '_Cross_correlation_D_CSA',
                          'ccr_dd_restraint': '_Cross_correlation_DD',
                          'fchiral_restraint': '_Floating_chirality',
                          'saxs_restraint': '_SAXS_constraint',
                          'other_restraint': '_Other_data',
                          'spectral_peak': '_Peak_row_format',
                          'chem_shift': '_Atom_chem_shift'
                          }

NMR_STAR_LP_KEY_ITEMS = {'dist_restraint': [{'name': 'ID', 'type': 'positive-int', 'auto-increment': True},
                                            {'name': 'Entity_assembly_ID_1', 'type': 'positive-int-as-str', 'default': '1', 'default-from': 'Auth_asym_ID_1'},
                                            {'name': 'Entity_ID_1', 'type': 'positive-int'},
                                            {'name': 'Comp_index_ID_1', 'type': 'int', 'default-from': 'Seq_ID_1'},
                                            {'name': 'Comp_ID_1', 'type': 'str', 'uppercase': True},
                                            {'name': 'Atom_ID_1', 'type': 'str'},
                                            {'name': 'Entity_assembly_ID_2', 'type': 'positive-int-as-str', 'default': '1', 'default-from': 'Auth_asym_ID_2'},
                                            {'name': 'Entity_ID_2', 'type': 'positive-int'},
                                            {'name': 'Comp_index_ID_2', 'type': 'int', 'default-from': 'Seq_ID_2'},
                                            {'name': 'Comp_ID_2', 'type': 'str', 'uppercase': True},
                                            {'name': 'Atom_ID_2', 'type': 'str'}
                                            ],
                         'dihed_restraint': [{'name': 'ID', 'type': 'positive-int', 'auto-increment': True},
                                             {'name': 'Entity_assembly_ID_1', 'type': 'positive-int-as-str', 'default': '1', 'default-from': 'Auth_asym_ID_1'},
                                             {'name': 'Entity_ID_1', 'type': 'positive-int'},
                                             {'name': 'Comp_index_ID_1', 'type': 'int', 'default-from': 'Seq_ID_1'},
                                             {'name': 'Comp_ID_1', 'type': 'str', 'uppercase': True},
                                             {'name': 'Atom_ID_1', 'type': 'str'},
                                             {'name': 'Entity_assembly_ID_2', 'type': 'positive-int-as-str', 'default': '1', 'default-from': 'Auth_asym_ID_2'},
                                             {'name': 'Entity_ID_2', 'type': 'positive-int'},
                                             {'name': 'Comp_index_ID_2', 'type': 'int', 'default-from': 'Seq_ID_2'},
                                             {'name': 'Comp_ID_2', 'type': 'str', 'uppercase': True},
                                             {'name': 'Atom_ID_2', 'type': 'str'},
                                             {'name': 'Entity_assembly_ID_3', 'type': 'positive-int-as-str', 'default': '1', 'default-from': 'Auth_asym_ID_3'},
                                             {'name': 'Entity_ID_3', 'type': 'positive-int'},
                                             {'name': 'Comp_index_ID_3', 'type': 'int', 'default-from': 'Seq_ID_3'},
                                             {'name': 'Comp_ID_3', 'type': 'str', 'uppercase': True},
                                             {'name': 'Atom_ID_3', 'type': 'str'},
                                             {'name': 'Entity_assembly_ID_4', 'type': 'positive-int-as-str', 'default': '1', 'default-from': 'Auth_asym_ID_4'},
                                             {'name': 'Entity_ID_4', 'type': 'positive-int'},
                                             {'name': 'Comp_index_ID_4', 'type': 'int', 'default-from': 'Seq_ID_4'},
                                             {'name': 'Comp_ID_4', 'type': 'str', 'uppercase': True},
                                             {'name': 'Atom_ID_4', 'type': 'str'}
                                             ],
                         'rdc_restraint': [{'name': 'ID', 'type': 'positive-int', 'auto-increment': True},
                                           {'name': 'Entity_assembly_ID_1', 'type': 'positive-int-as-str', 'default': '1', 'default-from': 'Auth_asym_ID_1'},
                                           {'name': 'Entity_ID_1', 'type': 'positive-int'},
                                           {'name': 'Comp_index_ID_1', 'type': 'int', 'default-from': 'Seq_ID_1'},
                                           {'name': 'Comp_ID_1', 'type': 'str', 'uppercase': True},
                                           {'name': 'Atom_ID_1', 'type': 'str'},
                                           {'name': 'Entity_assembly_ID_2', 'type': 'positive-int-as-str', 'default': '1', 'default-from': 'Auth_asym_ID_2'},
                                           {'name': 'Entity_ID_2', 'type': 'positive-int'},
                                           {'name': 'Comp_index_ID_2', 'type': 'int', 'default-from': 'Seq_ID_2'},
                                           {'name': 'Comp_ID_2', 'type': 'str', 'uppercase': True},
                                           {'name': 'Atom_ID_2', 'type': 'str'}
                                           ],
                         'noepk_restraint': [{'name': 'ID', 'type': 'int', 'auto-increment': True},  # allows to have software-native id starting from zero
                                             {'name': 'Entity_assembly_ID_1', 'type': 'positive-int-as-str', 'default': '1'},
                                             {'name': 'Entity_ID_1', 'type': 'positive-int'},
                                             {'name': 'Comp_index_ID_1', 'type': 'int', 'default-from': 'Seq_ID_1'},
                                             {'name': 'Comp_ID_1', 'type': 'str', 'uppercase': True},
                                             {'name': 'Atom_ID_1', 'type': 'str'},
                                             {'name': 'Entity_assembly_ID_2', 'type': 'positive-int-as-str', 'default': '1'},
                                             {'name': 'Entity_ID_2', 'type': 'positive-int'},
                                             {'name': 'Comp_index_ID_2', 'type': 'int', 'default-from': 'Seq_ID_2'},
                                             {'name': 'Comp_ID_2', 'type': 'str', 'uppercase': True},
                                             {'name': 'Atom_ID_2', 'type': 'str'}
                                             ],
                         'jcoup_restraint': [{'name': 'ID', 'type': 'positive-int', 'auto-increment': True},
                                             {'name': 'Entity_assembly_ID_1', 'type': 'positive-int-as-str', 'default': '1', 'default-from': 'Auth_asym_ID_1'},
                                             {'name': 'Entity_ID_1', 'type': 'positive-int'},
                                             {'name': 'Comp_index_ID_1', 'type': 'int', 'default-from': 'Seq_ID_1'},
                                             {'name': 'Comp_ID_1', 'type': 'str', 'uppercase': True},
                                             {'name': 'Atom_ID_1', 'type': 'str'},
                                             {'name': 'Entity_assembly_ID_2', 'type': 'positive-int-as-str', 'default': '1', 'default-from': 'Auth_asym_ID_2'},
                                             {'name': 'Entity_ID_2', 'type': 'positive-int'},
                                             {'name': 'Comp_index_ID_2', 'type': 'int', 'default-from': 'Seq_ID_2'},
                                             {'name': 'Comp_ID_2', 'type': 'str', 'uppercase': True},
                                             {'name': 'Atom_ID_2', 'type': 'str'},
                                             {'name': 'Entity_assembly_ID_3', 'type': 'positive-int-as-str', 'default': '1', 'default-from': 'Auth_asym_ID_3'},
                                             {'name': 'Entity_ID_3', 'type': 'positive-int'},
                                             {'name': 'Comp_index_ID_3', 'type': 'int', 'default-from': 'Seq_ID_3'},
                                             {'name': 'Comp_ID_3', 'type': 'str', 'uppercase': True},
                                             {'name': 'Atom_ID_3', 'type': 'str'},
                                             {'name': 'Entity_assembly_ID_4', 'type': 'positive-int-as-str', 'default': '1', 'default-from': 'Auth_asym_ID_4'},
                                             {'name': 'Entity_ID_4', 'type': 'positive-int'},
                                             {'name': 'Comp_index_ID_4', 'type': 'int', 'default-from': 'Seq_ID_4'},
                                             {'name': 'Comp_ID_4', 'type': 'str', 'uppercase': True},
                                             {'name': 'Atom_ID_4', 'type': 'str'}
                                             ],
                         'rdc_raw_data': [{'name': 'ID', 'type': 'positive-int', 'auto-increment': True},
                                          {'name': 'Entity_assembly_ID_1', 'type': 'positive-int-as-str', 'default': '1'},
                                          {'name': 'Entity_ID_1', 'type': 'positive-int'},
                                          {'name': 'Comp_index_ID_1', 'type': 'int', 'default-from': 'Seq_ID_1'},
                                          {'name': 'Comp_ID_1', 'type': 'str', 'uppercase': True},
                                          {'name': 'Atom_ID_1', 'type': 'str'},
                                          {'name': 'Entity_assembly_ID_2', 'type': 'positive-int-as-str', 'default': '1'},
                                          {'name': 'Entity_ID_2', 'type': 'positive-int'},
                                          {'name': 'Comp_index_ID_2', 'type': 'int', 'default-from': 'Seq_ID_2'},
                                          {'name': 'Comp_ID_2', 'type': 'str', 'uppercase': True},
                                          {'name': 'Atom_ID_2', 'type': 'str'}
                                          ],
                         'csa_restraint': [{'name': 'ID', 'type': 'positive-int', 'auto-increment': True},
                                           {'name': 'Entity_assembly_ID', 'type': 'positive-int-as-str', 'default': '1'},
                                           {'name': 'Entity_ID', 'type': 'positive-int'},
                                           {'name': 'Comp_index_ID', 'type': 'int', 'default-from': 'Seq_ID'},
                                           {'name': 'Comp_ID', 'type': 'str', 'uppercase': True},
                                           {'name': 'Atom_ID', 'type': 'str'}
                                           ],
                         'ddc_restraint': [{'name': 'ID', 'type': 'positive-int', 'auto-increment': True},
                                           {'name': 'Entity_assembly_ID_1', 'type': 'positive-int-as-str', 'default': '1'},
                                           {'name': 'Entity_ID_1', 'type': 'positive-int'},
                                           {'name': 'Comp_index_ID_1', 'type': 'int', 'default-from': 'Seq_ID_1'},
                                           {'name': 'Comp_ID_1', 'type': 'str', 'uppercase': True},
                                           {'name': 'Atom_ID_1', 'type': 'str'},
                                           {'name': 'Entity_assembly_ID_2', 'type': 'positive-int-as-str', 'default': '1'},
                                           {'name': 'Entity_ID_2', 'type': 'positive-int'},
                                           {'name': 'Comp_index_ID_2', 'type': 'int', 'default-from': 'Seq_ID_2'},
                                           {'name': 'Comp_ID_2', 'type': 'str', 'uppercase': True},
                                           {'name': 'Atom_ID_2', 'type': 'str'}
                                           ],
                         'hvycs_restraint': [{'name': 'ID', 'type': 'positive-int', 'auto-increment': True},
                                             {'name': 'Entity_assembly_ID_1', 'type': 'positive-int-as-str', 'default': '1', 'default-from': 'Auth_asym_ID_1'},
                                             {'name': 'Entity_ID_1', 'type': 'positive-int'},
                                             {'name': 'Comp_index_ID_1', 'type': 'int', 'default-from': 'Seq_ID_1'},
                                             {'name': 'Comp_ID_1', 'type': 'str', 'uppercase': True},
                                             {'name': 'Atom_ID_1', 'type': 'str'},
                                             {'name': 'Entity_assembly_ID_2', 'type': 'positive-int-as-str', 'default': '1', 'default-from': 'Auth_asym_ID_2'},
                                             {'name': 'Entity_ID_2', 'type': 'positive-int'},
                                             {'name': 'Comp_index_ID_2', 'type': 'int', 'default-from': 'Seq_ID_2'},
                                             {'name': 'Comp_ID_2', 'type': 'str', 'uppercase': True},
                                             {'name': 'Atom_ID_2', 'type': 'str'},
                                             {'name': 'Entity_assembly_ID_3', 'type': 'positive-int-as-str', 'default': '1', 'default-from': 'Auth_asym_ID_3'},
                                             {'name': 'Entity_ID_3', 'type': 'positive-int'},
                                             {'name': 'Comp_index_ID_3', 'type': 'int', 'default-from': 'Seq_ID_3'},
                                             {'name': 'Comp_ID_3', 'type': 'str', 'uppercase': True},
                                             {'name': 'Atom_ID_3', 'type': 'str'},
                                             {'name': 'Entity_assembly_ID_4', 'type': 'positive-int-as-str', 'default': '1', 'default-from': 'Auth_asym_ID_4'},
                                             {'name': 'Entity_ID_4', 'type': 'positive-int'},
                                             {'name': 'Comp_index_ID_4', 'type': 'int', 'default-from': 'Seq_ID_4'},
                                             {'name': 'Comp_ID_4', 'type': 'str', 'uppercase': True},
                                             {'name': 'Atom_ID_4', 'type': 'str'},
                                             {'name': 'Entity_assembly_ID_5', 'type': 'positive-int-as-str', 'default': '1', 'default-from': 'Auth_asym_ID_5'},
                                             {'name': 'Entity_ID_5', 'type': 'positive-int'},
                                             {'name': 'Comp_index_ID_5', 'type': 'int', 'default-from': 'Seq_ID_5'},
                                             {'name': 'Comp_ID_5', 'type': 'str', 'uppercase': True},
                                             {'name': 'Atom_ID_5', 'type': 'str'}
                                             ],
                         'procs_restraint': [{'name': 'ID', 'type': 'positive-int', 'auto-increment': True},
                                             {'name': 'Entity_assembly_ID', 'type': 'positive-int-as-str', 'default': '1', 'default-from': 'Auth_asym_ID'},
                                             {'name': 'Entity_ID', 'type': 'positive-int'},
                                             {'name': 'Comp_index_ID', 'type': 'int', 'default-from': 'Seq_ID'},
                                             {'name': 'Comp_ID', 'type': 'str', 'uppercase': True},
                                             {'name': 'Atom_ID', 'type': 'str'}
                                             ],
                         'csp_restraint': [{'name': 'ID', 'type': 'positive-int', 'auto-increment': True},
                                           {'name': 'Entity_assembly_ID', 'type': 'positive-int-as-str', 'default': '1'},
                                           {'name': 'Entity_ID', 'type': 'positive-int'},
                                           {'name': 'Comp_index_ID', 'type': 'int', 'default-from': 'Seq_ID'},
                                           {'name': 'Comp_ID', 'type': 'str', 'uppercase': True},
                                           {'name': 'Atom_ID', 'type': 'str'}
                                           ],
                         'auto_relax_restraint': [{'name': 'ID', 'type': 'positive-int', 'auto-increment': True},
                                                  {'name': 'Entity_assembly_ID', 'type': 'positive-int-as-str', 'default': '1'},
                                                  {'name': 'Entity_ID', 'type': 'positive-int'},
                                                  {'name': 'Comp_index_ID', 'type': 'int', 'default-from': 'Seq_ID'},
                                                  {'name': 'Comp_ID', 'type': 'str', 'uppercase': True},
                                                  {'name': 'Atom_ID', 'type': 'str'}
                                                  ],
                         'heteronucl_noe_data': [{'name': 'ID', 'type': 'positive-int', 'auto-increment': True},
                                                 {'name': 'Entity_assembly_ID_1', 'type': 'positive-int-as-str', 'default': '1', 'default-from': 'Auth_asym_ID_1'},
                                                 {'name': 'Entity_ID_1', 'type': 'positive-int'},
                                                 {'name': 'Comp_index_ID_1', 'type': 'int', 'default-from': 'Seq_ID_1'},
                                                 {'name': 'Comp_ID_1', 'type': 'str', 'uppercase': True},
                                                 {'name': 'Atom_ID_1', 'type': 'str'},
                                                 {'name': 'Entity_assembly_ID_2', 'type': 'positive-int-as-str', 'default': '1', 'default-from': 'Auth_asym_ID_2'},
                                                 {'name': 'Entity_ID_2', 'type': 'positive-int'},
                                                 {'name': 'Comp_index_ID_2', 'type': 'int', 'default-from': 'Seq_ID_2'},
                                                 {'name': 'Comp_ID_2', 'type': 'str', 'uppercase': True},
                                                 {'name': 'Atom_ID_2', 'type': 'str'}
                                                 ],
                         'heteronucl_t1_data': [{'name': 'ID', 'type': 'positive-int', 'auto-increment': True},
                                                {'name': 'Entity_assembly_ID', 'type': 'positive-int-as-str', 'default': '1'},
                                                {'name': 'Entity_ID', 'type': 'positive-int'},
                                                {'name': 'Comp_index_ID', 'type': 'int', 'default-from': 'Seq_ID'},
                                                {'name': 'Comp_ID', 'type': 'str', 'uppercase': True},
                                                {'name': 'Atom_ID', 'type': 'str'}
                                                ],
                         'heteronucl_t2_data': [{'name': 'ID', 'type': 'positive-int', 'auto-increment': True},
                                                {'name': 'Entity_assembly_ID', 'type': 'positive-int-as-str', 'default': '1'},
                                                {'name': 'Entity_ID', 'type': 'positive-int'},
                                                {'name': 'Comp_index_ID', 'type': 'int', 'default-from': 'Seq_ID'},
                                                {'name': 'Comp_ID', 'type': 'str', 'uppercase': True},
                                                {'name': 'Atom_ID', 'type': 'str'}
                                                ],
                         'heteronucl_t1r_data': [{'name': 'ID', 'type': 'positive-int', 'auto-increment': True},
                                                 {'name': 'Entity_assembly_ID', 'type': 'positive-int-as-str', 'default': '1'},
                                                 {'name': 'Entity_ID', 'type': 'positive-int'},
                                                 {'name': 'Comp_index_ID', 'type': 'int', 'default-from': 'Seq_ID'},
                                                 {'name': 'Comp_ID', 'type': 'str', 'uppercase': True},
                                                 {'name': 'Atom_ID', 'type': 'str'}
                                                 ],
                         'order_param_data': [{'name': 'ID', 'type': 'positive-int', 'auto-increment': True},
                                              {'name': 'Entity_assembly_ID', 'type': 'positive-int-as-str', 'default': '1'},
                                              {'name': 'Entity_ID', 'type': 'positive-int'},
                                              {'name': 'Comp_index_ID', 'type': 'int', 'default-from': 'Seq_ID'},
                                              {'name': 'Comp_ID', 'type': 'str', 'uppercase': True},
                                              {'name': 'Atom_ID', 'type': 'str'}
                                              ],
                         'ph_titr_data': [{'name': 'ID', 'type': 'positive-int', 'auto-increment': True},
                                          {'name': 'Atm_obs_entity_assembly_ID', 'type': 'positive-int-as-str', 'default': '1'},
                                          {'name': 'Atm_obs_entity_ID', 'type': 'positive-int'},
                                          {'name': 'Atm_obs_comp_index_ID', 'type': 'int', 'default-from': 'Atm_obs_seq_ID'},
                                          {'name': 'Atm_obs_comp_ID', 'type': 'str', 'uppercase': True},
                                          {'name': 'Atm_obs_atom_ID', 'type': 'str'},
                                          {'name': 'Atm_titr_entity_assembly_ID', 'type': 'positive-int-as-str', 'default': '1'},
                                          {'name': 'Atm_titr_entity_ID', 'type': 'positive-int'},
                                          {'name': 'Atm_titr_comp_index_ID', 'type': 'int', 'default-from': 'Atm_titr_seq_ID'},
                                          {'name': 'Atm_titr_comp_ID', 'type': 'str', 'uppercase': True},
                                          {'name': 'Atm_titr_atom_ID', 'type': 'str'}
                                          ],
                         'ph_param_data': [{'name': 'ID', 'type': 'positive-int', 'auto-increment': True}
                                           ],
                         'coupling_const_data': [{'name': 'ID', 'type': 'positive-int', 'auto-increment': True},
                                                 {'name': 'Entity_assembly_ID_1', 'type': 'positive-int-as-str', 'default': '1'},
                                                 {'name': 'Entity_ID_1', 'type': 'positive-int'},
                                                 {'name': 'Comp_index_ID_1', 'type': 'int', 'default-from': 'Seq_ID_1'},
                                                 {'name': 'Comp_ID_1', 'type': 'str', 'uppercase': True},
                                                 {'name': 'Atom_ID_1', 'type': 'str'},
                                                 {'name': 'Entity_assembly_ID_2', 'type': 'positive-int-as-str', 'default': '1'},
                                                 {'name': 'Entity_ID_2', 'type': 'positive-int'},
                                                 {'name': 'Comp_index_ID_2', 'type': 'int', 'default-from': 'Seq_ID_2'},
                                                 {'name': 'Comp_ID_2', 'type': 'str', 'uppercase': True},
                                                 {'name': 'Atom_ID_2', 'type': 'str'}
                                                 ],
                         'ccr_d_csa_restraint': [{'name': 'ID', 'type': 'positive-int', 'auto-increment': True},
                                                 {'name': 'Dipole_entity_assembly_ID_1', 'type': 'positive-int-as-str', 'default': '1'},
                                                 {'name': 'Dipole_entity_ID_1', 'type': 'positive-int'},
                                                 {'name': 'Dipole_comp_index_ID_1', 'type': 'int', 'default-from': 'Dipole_seq_ID_1'},
                                                 {'name': 'Dipole_comp_ID_1', 'type': 'str', 'uppercase': True},
                                                 {'name': 'Dipole_atom_ID_1', 'type': 'str'},
                                                 {'name': 'Dipole_entity_assembly_ID_2', 'type': 'positive-int-as-str', 'default': '1'},
                                                 {'name': 'Dipole_entity_ID_2', 'type': 'positive-int'},
                                                 {'name': 'Dipole_comp_index_ID_2', 'type': 'int', 'default-from': 'Dipole_seq_ID_2'},
                                                 {'name': 'Dipole_comp_ID_2', 'type': 'str', 'uppercase': True},
                                                 {'name': 'Dipole_atom_ID_2', 'type': 'str'},
                                                 {'name': 'CSA_entity_assembly_ID_1', 'type': 'positive-int-as-str', 'default': '1'},
                                                 {'name': 'CSA_entity_ID_1', 'type': 'positive-int'},
                                                 {'name': 'CSA_comp_index_ID_1', 'type': 'int', 'default-from': 'CSA_seq_ID_1'},
                                                 {'name': 'CSA_comp_ID_1', 'type': 'str', 'uppercase': True},
                                                 {'name': 'CSA_atom_ID_1', 'type': 'str'},
                                                 {'name': 'CSA_entity_assembly_ID_2', 'type': 'positive-int-as-str', 'default': '1'},
                                                 {'name': 'CSA_entity_ID_2', 'type': 'positive-int'},
                                                 {'name': 'CSA_comp_index_ID_2', 'type': 'int', 'default-from': 'CSA_seq_ID_2'},
                                                 {'name': 'CSA_comp_ID_2', 'type': 'str', 'uppercase': True},
                                                 {'name': 'CSA_atom_ID_2', 'type': 'str'}
                                                 ],
                         'ccr_dd_restraint': [{'name': 'ID', 'type': 'positive-int', 'auto-increment': True},
                                              {'name': 'Dipole_1_entity_assembly_ID_1', 'type': 'positive-int-as-str', 'default': '1'},
                                              {'name': 'Dipole_1 entity_ID_1', 'type': 'positive-int'},
                                              {'name': 'Dipole_1_comp_index_ID_1', 'type': 'int', 'default-from': 'Dipole_1_seq_ID_1'},
                                              {'name': 'Dipole_1_comp_ID_1', 'type': 'str', 'uppercase': True},
                                              {'name': 'Dipole_1_atom_ID_1', 'type': 'str'},
                                              {'name': 'Dipole_1_entity_assembly_ID_2', 'type': 'positive-int-as-str', 'default': '1'},
                                              {'name': 'Dipole_1_entity_ID_2', 'type': 'positive-int'},
                                              {'name': 'Dipole_1_comp_index_ID_2', 'type': 'int', 'default-from': 'Dipole_1_seq_ID_2'},
                                              {'name': 'Dipole_1_comp_ID_2', 'type': 'str', 'uppercase': True},
                                              {'name': 'Dipole_1_atom_ID_2', 'type': 'str'},
                                              {'name': 'Dipole_2_entity_assembly_ID_1', 'type': 'positive-int-as-str', 'default': '1'},
                                              {'name': 'Dipole_2_entity_ID_1', 'type': 'positive-int'},
                                              {'name': 'Dipole_2_comp_index_ID_1', 'type': 'int', 'default-from': 'Dipole_2_seq_ID_1'},
                                              {'name': 'Dipole_2_comp_ID_1', 'type': 'str', 'uppercase': True},
                                              {'name': 'Dipole_2_atom_ID_1', 'type': 'str'},
                                              {'name': 'Dipole_2_entity_assembly_ID_2', 'type': 'positive-int-as-str', 'default': '1'},
                                              {'name': 'Dipole_2_entity_ID_2', 'type': 'positive-int'},
                                              # NOTICE: 'Dipole_2_comp_index_ID_2' is inferred from NMR-STAR Dictionary
                                              {'name': 'Dipole_2_comp_index_ID_2', 'type': 'int', 'default-from': 'Dipole_2_seq_ID_2'},
                                              {'name': 'Dipole_2_comp_ID_2', 'type': 'str', 'uppercase': True},
                                              {'name': 'Dipole_2_atom_ID_2', 'type': 'str'}
                                              ],
                         'fchiral_restraint': [{'name': 'ID', 'type': 'positive-int', 'auto-increment': True},
                                               {'name': 'Entity_assembly_ID_1', 'type': 'positive-int-as-str', 'default': '1', 'default-from': 'Auth_asym_ID_1'},
                                               {'name': 'Entity_ID_1', 'type': 'positive-int'},
                                               {'name': 'Comp_index_ID_1', 'type': 'int', 'default-from': 'Seq_ID_1'},
                                               {'name': 'Comp_ID_1', 'type': 'str', 'uppercase': True},
                                               {'name': 'Atom_ID_1', 'type': 'str'},
                                               {'name': 'Entity_assembly_ID_2', 'type': 'positive-int-as-str', 'default': '1', 'default-from': 'Auth_asym_ID_2'},
                                               {'name': 'Entity_ID_2', 'type': 'positive-int'},
                                               {'name': 'Comp_index_ID_2', 'type': 'int', 'default-from': 'Seq_ID_2'},
                                               {'name': 'Comp_ID_2', 'type': 'str', 'uppercase': True},
                                               {'name': 'Atom_ID_2', 'type': 'str'}
                                               ],
                         'saxs_restraint': [{'name': 'ID', 'type': 'positive-int', 'auto-increment': True},
                                            {'name': 'Q_value', 'type': 'positive-float'}
                                            ],
                         'other_restraint': [{'name': 'ID', 'type': 'positive-int', 'auto-increment': True},
                                             {'name': 'Entity_assembly_ID', 'type': 'positive-int-as-str', 'default': '1'},
                                             {'name': 'Entity_ID', 'type': 'positive-int'},
                                             {'name': 'Comp_index_ID', 'type': 'int', 'default-from': 'Seq_ID'},
                                             {'name': 'Comp_ID', 'type': 'str', 'uppercase': True},
                                             {'name': 'Atom_ID', 'type': 'str'}
                                             ],
                         'spectral_peak': [{'name': 'ID', 'type': 'int', 'auto-increment': True}],  # allows to have software-native id starting from zero
                         'chem_shift': [{'name': 'ID', 'type': 'positive-int', 'auto-increment': True},
                                        {'name': 'Entity_assembly_ID', 'type': 'positive-int-as-str', 'default': '1', 'default-from': 'Auth_asym_ID'},
                                        {'name': 'Entity_ID', 'type': 'positive-int'},
                                        {'name': 'Comp_index_ID', 'type': 'int', 'default-from': 'Seq_ID_1'},
                                        {'name': 'Comp_ID', 'type': 'str', 'uppercase': True},
                                        {'name': 'Atom_ID', 'type': 'str'},
                                        {'name': 'Occupancy', 'type': 'positive-float', 'default': '.'}
                                        ]
                         }

NMR_STAR_LP_DATA_ITEMS = {'dist_restraint': [{'name': 'Index_ID', 'type': 'index-int', 'mandatory': False},
                                             {'name': 'Combination_ID', 'type': 'positive-int', 'mandatory': False,
                                              'enforce-non-zero': True},
                                             {'name': 'Member_ID', 'type': 'positive-int', 'mandatory': False,
                                              'enforce-non-zero': True},
                                             {'name': 'Member_logic_code', 'type': 'enum', 'mandatory': False,
                                              'enum': ('OR', 'AND'),
                                              'enforce-enum': True},
                                             {'name': 'Target_val', 'type': 'range-float', 'mandatory': False, 'group-mandatory': True, 'void-zero': True,
                                              'clear-bad-pattern': True,
                                              'range': DIST_RESTRAINT_RANGE,
                                              'group': {'member-with': ['Lower_linear_limit',
                                                                        'Upper_linear_limit',
                                                                        'Distance_lower_bound_val',
                                                                        'Distance_upper_bound_val'],
                                                        'coexist-with': None,
                                                        'smaller-than': ['Lower_linear_limit', 'Distance_lower_bound_val'],
                                                        'larger-than': ['Distance_upper_bound_val', 'Upper_linear_limit']}},
                                             {'name': 'Target_val_uncertainty', 'type': 'range-float', 'mandatory': False, 'void-zero': True,
                                              'clear-bad-pattern': True,
                                              'range': DIST_UNCERTAINTY_RANGE},
                                             {'name': 'Lower_linear_limit', 'type': 'range-float', 'mandatory': False, 'group-mandatory': True, 'void-zero': True,
                                              'clear-bad-pattern': True,
                                              'range': DIST_RESTRAINT_RANGE,
                                              'group': {'member-with': ['Target_val',
                                                                        'Upper_linear_limit',
                                                                        'Distance_lower_bound_val',
                                                                        'Distance_upper_bound_val'],
                                                        'coexist-with': None,  # ['Upper_linear_limit', 'Distance_lower_bound_val', 'Distance_upper_bound_val'],
                                                        'smaller-than': None,
                                                        'larger-than': ['Distance_lower_bound_val', 'Distance_upper_bound_val', 'Upper_linear_limit']}},
                                             {'name': 'Distance_lower_bound_val', 'type': 'range-float', 'mandatory': False,
                                              'group-mandatory': True, 'void-zero': True,
                                              'clear-bad-pattern': True,
                                              'range': DIST_RESTRAINT_RANGE,
                                              'group': {'member-with': ['Target_val', 'Lower_linear_limit', 'Upper_linear_limit', 'Distance_upper_bound_val'],
                                                        'coexist-with': None,  # ['Distance_upper_bound_val'],
                                                        'smaller-than': ['Lower_linear_limit'],
                                                        'larger-than': ['Distance_upper_bound_val', 'Upper_linear_limit']}},
                                             {'name': 'Distance_upper_bound_val', 'type': 'range-float', 'mandatory': False,
                                              'group-mandatory': True, 'void-zero': True,
                                              'clear-bad-pattern': True,
                                              'range': DIST_RESTRAINT_RANGE,
                                              'group': {'member-with': ['Target_val', 'Lower_linear_limit', 'Upper_linear_limit', 'Distance_lower_bound_val'],
                                                        'coexist-with': None,  # ['Distance_lower_bound_val'],
                                                        'smaller-than': ['Lower_linear_limit', 'Distance_lower_bound_val'],
                                                        'larger-than': ['Upper_linear_limit']}},
                                             {'name': 'Upper_linear_limit', 'type': 'range-float', 'mandatory': False, 'group-mandatory': True, 'void-zero': True,
                                              'clear-bad-pattern': True,
                                              'range': DIST_RESTRAINT_RANGE,
                                              'group': {'member-with': ['Target_val',
                                                                        'Lower_linear_limit',
                                                                        'Distance_lower_bound_val',
                                                                        'Distance_upper_bound_val'],
                                                        'coexist-with': None,  # ['Lower_linear_limit', 'Distance_lower_bound_val', 'Distance_upper_bound_val'],
                                                        'smaller-than': ['Lower_linear_limit', 'Distance_lower_bound_val', 'Distance_upper_bound_val'],
                                                        'larger-than': None}},
                                             {'name': 'Weight', 'type': 'range-float', 'mandatory': False,
                                              'range': WEIGHT_RANGE},
                                             # 'enforce-non-zero': True},
                                             {'name': 'Distance_val', 'type': 'range-float', 'mandatory': False,
                                                      'range': DIST_RESTRAINT_RANGE},
                                             {'name': 'Auth_asym_ID_1', 'type': 'str', 'mandatory': False},
                                             {'name': 'Auth_seq_ID_1', 'type': 'int', 'mandatory': False},
                                             {'name': 'Auth_comp_ID_1', 'type': 'str', 'mandatory': False},
                                             {'name': 'Auth_atom_ID_1', 'type': 'str', 'mandatory': False},
                                             {'name': 'Auth_atom_name_1', 'type': 'str', 'mandatory': False},
                                             {'name': 'Auth_asym_ID_2', 'type': 'str', 'mandatory': False},
                                             {'name': 'Auth_seq_ID_2', 'type': 'int', 'mandatory': False},
                                             {'name': 'Auth_comp_ID_2', 'type': 'str', 'mandatory': False},
                                             {'name': 'Auth_atom_ID_2', 'type': 'str', 'mandatory': False},
                                             {'name': 'Auth_atom_name_2', 'type': 'str', 'mandatory': False},
                                             {'name': 'Gen_dist_constraint_list_ID', 'type': 'pointer-index', 'mandatory': True,
                                              'default': '1', 'default-from': 'parent'},
                                             {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                             ],
                          'dihed_restraint': [{'name': 'Index_ID', 'type': 'index-int', 'mandatory': False},
                                              {'name': 'Combination_ID', 'type': 'positive-int', 'mandatory': False,
                                               'enforce-non-zero': True},
                                              {'name': 'Torsion_angle_name', 'type': 'str', 'mandatory': False},
                                              {'name': 'Angle_target_val', 'type': 'range-float', 'mandatory': False, 'group-mandatory': True,
                                               'clear-bad-pattern': True,
                                               'range': ANGLE_RESTRAINT_RANGE,
                                               'group': {'member-with': ['Angle_lower_linear_limit',
                                                                         'Angle_upper_linear_limit',
                                                                         'Angle_lower_bound_val',
                                                                         'Angle_upper_bound_val'],
                                                         'coexist-with': None,
                                                         'smaller-than': None,  # (DAOTHER-8442) ['Angle_lower_linear_limit', 'Angle_lower_bound_val'],
                                                         'larger-than': None,  # (DAOTHER-8442) ['Angle_upper_bound_val', 'Angle_upper_linear_limit'],
                                                         'circular-shift': 360.0}},
                                              {'name': 'Angle_target_val_err', 'type': 'range-float', 'mandatory': False, 'void-zero': True,
                                               'clear-bad-pattern': True,
                                               'range': ANGLE_UNCERTAINTY_RANGE},
                                              {'name': 'Angle_lower_linear_limit', 'type': 'range-float', 'mandatory': False, 'group-mandatory': True,
                                               'clear-bad-pattern': True,
                                               'range': ANGLE_RESTRAINT_RANGE,
                                               'group': {'member-with': ['Angle_target_val', 'Angle_upper_linear_limit',
                                                                         'Angle_lower_bound_val', 'Angle_upper_bound_val'],
                                                         'coexist-with': None,  # ['Angle_upper_linear_limit', 'Angle_lower_bound_val', 'Angle_upper_bound_val'],
                                                         'smaller-than': None,
                                                         'larger-than': ['Angle_lower_bound_val'],
                                                         # (DAOTHER-8442) ['Angle_lower_bound_val', 'Angle_upper_bound', 'Angle_upper_linear_limit'],
                                                         'circular-shift': 360.0}},
                                              {'name': 'Angle_lower_bound_val', 'type': 'range-float', 'mandatory': False, 'group-mandatory': True,
                                               'clear-bad-pattern': True,
                                               'range': ANGLE_RESTRAINT_RANGE,
                                               'group': {'member-with': ['Angle_target_val', 'Angle_lower_linear_limit',
                                                                         'Angle_upper_linear_limit', 'Angle_upper_bound_val'],
                                                         'coexist-with': None,  # ['Angle_upper_bound_val'],
                                                         'smaller-than': ['Angle_lower_linear_limit'],
                                                         'larger-than': None,  # (DAOTHER-8442) ['Angle_upper_bound_val', 'Angle_upper_linear_limit'],
                                                         'circular-shift': 360.0}},
                                              {'name': 'Angle_upper_bound_val', 'type': 'range-float', 'mandatory': False, 'group-mandatory': True,
                                               'clear-bad-pattern': True,
                                               'range': ANGLE_RESTRAINT_RANGE,
                                               'group': {'member-with': ['Angle_target_val', 'Angle_lower_linear_limit',
                                                                         'Angle_upper_linear_limit', 'Angle_lower_bound_val'],
                                                         'coexist-with': None,  # ['Angle_lower_bound_val'],
                                                         'smaller-than': None,  # (DAOTHER-8442) ['Angle_lower_bound_val', 'Angle_upper_linear_limit'],
                                                         'larger-than': ['Angle_upper_linear_limit'],
                                                         'circular-shift': 360.0}},
                                              {'name': 'Angle_upper_linear_limit', 'type': 'range-float', 'mandatory': False, 'group-mandatory': True,
                                               'clear-bad-pattern': True,
                                               'range': ANGLE_RESTRAINT_RANGE,
                                               'group': {'member-with': ['Angle_target_val', 'Angle_lower_linear_limit',
                                                                         'Angle_lower_bound_val', 'Angle_upper_bound_val'],
                                                         'coexist-with': None,  # ['Angle_lower_linear_limit', 'Angle_lower_bound_val', 'Angle_upper_bound_val'],
                                                         'smaller-than': ['Angle_upper_bound_val'],
                                                         # (DAOTHER-8442) ['Angle_lower_linear_limit', 'Angle_lower_bound_val', 'Angle_upper_bound_val'],
                                                         'larger-than': None,
                                                         'circular-shift': 360.0}},
                                              {'name': 'Weight', 'type': 'range-float', 'mandatory': False,
                                               'range': WEIGHT_RANGE},
                                              # 'enforce-non-zero': True},
                                              {'name': 'Auth_asym_ID_1', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_seq_ID_1', 'type': 'int', 'mandatory': False},
                                              {'name': 'Auth_comp_ID_1', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_atom_ID_1', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_atom_name_1', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_asym_ID_2', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_seq_ID_2', 'type': 'int', 'mandatory': False},
                                              {'name': 'Auth_comp_ID_2', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_atom_ID_2', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_atom_name_2', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_asym_ID_3', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_seq_ID_3', 'type': 'int', 'mandatory': False},
                                              {'name': 'Auth_comp_ID_3', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_atom_ID_3', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_atom_name_3', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_asym_ID_4', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_seq_ID_4', 'type': 'int', 'mandatory': False},
                                              {'name': 'Auth_comp_ID_4', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_atom_ID_4', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_atom_name_4', 'type': 'str', 'mandatory': False},
                                              {'name': 'Torsion_angle_constraint_list_ID', 'type': 'pointer-index', 'mandatory': True,
                                               'default': '1', 'default-from': 'parent'},
                                              {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                              ],
                          'rdc_restraint': [{'name': 'Index_ID', 'type': 'index-int', 'mandatory': False},
                                            {'name': 'Combination_ID', 'type': 'positive-int', 'mandatory': False,
                                             'enforce-non-zero': True},
                                            {'name': 'Target_value', 'type': 'range-float', 'mandatory': False, 'group-mandatory': True,
                                             'clear-bad-pattern': True,
                                             'range': RDC_RESTRAINT_RANGE,
                                             'group': {'member-with': ['RDC_lower_linear_limit', 'RDC_upper_linear_limit', 'RDC_lower_bound', 'RDC_upper_bound'],
                                                       'coexist-with': None,
                                                       'smaller-than': ['RDC_lower_linear_limit', 'RDC_lower_bound'],
                                                       'larger-than': ['RDC_upper_bound', 'RDC_upper_linear_limit']}},
                                            {'name': 'Target_value_uncertainty', 'type': 'range-float', 'mandatory': False, 'void-zero': True,
                                             'clear-bad-pattern': True,
                                             'range': RDC_UNCERTAINTY_RANGE},
                                            {'name': 'RDC_lower_linear_limit', 'type': 'range-float', 'mandatory': False, 'group-mandatory': True,
                                             'clear-bad-pattern': True,
                                             'range': RDC_RESTRAINT_RANGE,
                                             'group': {'member-with': ['Target_value', 'RDC_upper_linear_limit', 'RDC_lower_bound', 'RDC_upper_bound'],
                                                       'coexist-with': None,  # ['RDC_upper_linear_limit', 'RDC_lower_bound', 'RDC_upper_bound'],
                                                       'smaller-than': None,
                                                       'larger-than': ['RDC_lower_bound', 'RDC_upper_bound', 'RDC_upper_linear_limit']}},
                                            {'name': 'RDC_lower_bound', 'type': 'range-float', 'mandatory': False, 'group-mandatory': True,
                                             'clear-bad-pattern': True,
                                             'range': RDC_RESTRAINT_RANGE,
                                             'group': {'member-with': ['Target_value', 'RDC_lower_linear_limit', 'RDC_upper_linear_limit', 'RDC_upper_bound'],
                                                       'coexist-with': None,  # ['RDC_upper_bound'],
                                                       'smaller-than': ['RDC_lower_linear_limit'],
                                                       'larger-than': ['RDC_upper_bound', 'RDC_upper_linear_limit']}},
                                            {'name': 'RDC_upper_bound', 'type': 'range-float', 'mandatory': False, 'group-mandatory': True,
                                             'clear-bad-pattern': True,
                                             'range': RDC_RESTRAINT_RANGE,
                                             'group': {'member-with': ['Target_value', 'RDC_lower_linear_limit', 'RDC_upper_linear_limit', 'RDC_lower_bound'],
                                                       'coexist-with': None,  # ['RDC_lower_bound'],
                                                       'smaller-than': ['RDC_lower_linear_limit', 'RDC_lower_bound'],
                                                       'larger-than': ['RDC_upper_linear_limit']}},
                                            {'name': 'RDC_upper_linear_limit', 'type': 'range-float', 'mandatory': False, 'group-mandatory': True,
                                             'clear-bad-pattern': True,
                                             'range': RDC_RESTRAINT_RANGE,
                                             'group': {'member-with': ['Target_value', 'RDC_upper_linear_limit', 'RDC_lower_bound', 'RDC_upper_bound'],
                                                       'coexist-with': None,  # ['RDC_upper_linear_limit', 'RDC_lower_bound', 'RDC_upper_bound'],
                                                       'smaller-than': ['RDC_lower_linear_limit', 'RDC_lower_bound', 'RDC_upper_bound'],
                                                       'larger-than': None}},
                                            {'name': 'Weight', 'type': 'range-float', 'mandatory': False,
                                             'range': WEIGHT_RANGE},
                                            # 'enforce-non-zero': True},
                                            {'name': 'RDC_val', 'type': 'range-float', 'mandatory': False,
                                             'clear-bad-pattern': True,
                                             'range': RDC_RESTRAINT_RANGE},
                                            {'name': 'RDC_val_err', 'type': 'range-float', 'mandatory': False, 'void-zero': True,
                                             'clear-bad-pattern': True,
                                             'range': RDC_UNCERTAINTY_RANGE},
                                            {'name': 'RDC_val_scale_factor', 'type': 'range-float', 'mandatory': False,
                                             'range': SCALE_RANGE,
                                             'enforce-non-zero': True},
                                            {'name': 'RDC_distant_dependent', 'type': 'bool', 'mandatory': False},
                                            {'name': 'Auth_asym_ID_1', 'type': 'str', 'mandatory': False},
                                            {'name': 'Auth_seq_ID_1', 'type': 'int', 'mandatory': False},
                                            {'name': 'Auth_comp_ID_1', 'type': 'str', 'mandatory': False},
                                            {'name': 'Auth_atom_ID_1', 'type': 'str', 'mandatory': False},
                                            {'name': 'Auth_atom_name_1', 'type': 'str', 'mandatory': False},
                                            {'name': 'Auth_asym_ID_2', 'type': 'str', 'mandatory': False},
                                            {'name': 'Auth_seq_ID_2', 'type': 'int', 'mandatory': False},
                                            {'name': 'Auth_comp_ID_2', 'type': 'str', 'mandatory': False},
                                            {'name': 'Auth_atom_ID_2', 'type': 'str', 'mandatory': False},
                                            {'name': 'Auth_atom_name_2', 'type': 'str', 'mandatory': False},
                                            {'name': 'RDC_constraint_list_ID', 'type': 'pointer-index', 'mandatory': True, 'default': '1', 'default-from': 'parent'},
                                            {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                            ],
                          'noepk_restraint': [{'name': 'Val', 'type': 'float', 'mandatory': False, 'group-mandatory': True,
                                               'clear-bad-pattern': True,
                                               'group': {'member-with': ['Val_min', 'Val_max'],
                                                         'coexist-with': None,
                                                         'smaller-than': None,
                                                         'larger-than': None}},
                                              {'name': 'Val_err', 'type': 'range-float', 'mandatory': False, 'void-zero': True,
                                               'clear-bad-pattern': True,
                                               'range': {'min_inclusive': 0.0}},
                                              {'name': 'Val_min', 'type': 'float', 'mandatory': False, 'group-mandatory': True,
                                               'clear-bad-pattern': True,
                                               'group': {'member-with': ['Val', 'Val_max'],
                                                         'coexist-with': None,
                                                         'smaller-than': None,
                                                         'larger-than': ['Val_max']}},
                                              {'name': 'Val_max', 'type': 'float', 'mandatory': False, 'group-mandatory': True,
                                               'clear-bad-pattern': True,
                                               'group': {'member-with': ['Val', 'Val_min'],
                                                         'coexist-with': None,
                                                         'smaller-than': ['Val_min'],
                                                         'larger-than': None}},
                                              {'name': 'Auth_entity_assembly_ID_1', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_seq_ID_1', 'type': 'int', 'mandatory': False},
                                              {'name': 'Auth_comp_ID_1', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_atom_ID_1', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_entity_assembly_ID_2', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_seq_ID_2', 'type': 'int', 'mandatory': False},
                                              {'name': 'Auth_comp_ID_2', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_atom_ID_2', 'type': 'str', 'mandatory': False},
                                              {'name': 'Homonucl_NOE_list_ID', 'type': 'pointer-index', 'mandatory': True, 'default': '1', 'default-from': 'parent'},
                                              {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                              ],
                          'jcoup_restraint': [{'name': 'Coupling_constant_val', 'type': 'range-float', 'mandatory': False, 'group-mandatory': True,
                                               'clear-bad-pattern': True,
                                               'range': RDC_RESTRAINT_RANGE,
                                               'group': {'member-with': ['Coupling_constant_lower_bound', 'Coupling_constant_upper_bound'],
                                                         'coexist-with': None,
                                                         'smaller-than': None,
                                                         'larger-than': None}},
                                              {'name': 'Coupling_constant_err', 'type': 'range-float', 'mandatory': False, 'void-zero': True,
                                               'clear-bad-pattern': True,
                                               'range': {'min_inclusive': 0.0}},
                                              {'name': 'Coupling_constant_lower_bound', 'type': 'range-float', 'mandatory': False, 'group-mandatory': True,
                                               'clear-bad-pattern': True,
                                               'range': RDC_RESTRAINT_RANGE,
                                               'group': {'member-with': ['Coupling_constant_upper_bound'],
                                                         'coexist-with': None,
                                                         'smaller-than': None,
                                                         'larger-than': ['Coupling_constant_upper_bound']}},
                                              {'name': 'Coupling_constant_upper_bound', 'type': 'float', 'mandatory': False, 'group-mandatory': True,
                                               'clear-bad-pattern': True,
                                               'range': RDC_RESTRAINT_RANGE,
                                               'group': {'member-with': ['Coupling_constant_lower_bound'],
                                                         'coexist-with': None,
                                                         'smaller-than': ['Coupling_constant_lower_bound'],
                                                         'larger-than': None}},
                                              {'name': 'Auth_asym_ID_1', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_seq_ID_1', 'type': 'int', 'mandatory': False},
                                              {'name': 'Auth_comp_ID_1', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_atom_ID_1', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_asym_ID_2', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_seq_ID_2', 'type': 'int', 'mandatory': False},
                                              {'name': 'Auth_comp_ID_2', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_atom_ID_2', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_asym_ID_3', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_seq_ID_3', 'type': 'int', 'mandatory': False},
                                              {'name': 'Auth_comp_ID_3', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_atom_ID_3', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_asym_ID_4', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_seq_ID_4', 'type': 'int', 'mandatory': False},
                                              {'name': 'Auth_comp_ID_4', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_atom_ID_4', 'type': 'str', 'mandatory': False},
                                              {'name': 'J_three_bond_constraint_list_ID', 'type': 'pointer-index', 'mandatory': True,
                                               'default': '1', 'default-from': 'parent'},
                                              {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                              ],
                          'rdc_raw_data': [{'name': 'RDC_code', 'type': 'str', 'mandatory': True},
                                           {'name': 'Atom_type_1', 'type': 'enum', 'mandatory': True, 'default-from': 'Atom_ID_1',
                                            'enum': set(ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS.keys()),
                                            'enforce-enum': True},
                                           {'name': 'Atom_isotope_number_1', 'type': 'enum-int', 'mandatory': True, 'default-from': 'Atom_ID_1',
                                            'enum': set(ALLOWED_ISOTOPE_NUMBERS),
                                            'enforce-enum': True},
                                           {'name': 'Ambiguity_code_1', 'type': 'enum-int', 'mandatory': False,
                                            'enum': ALLOWED_AMBIGUITY_CODES,
                                            'enforce-enum': True},
                                           {'name': 'Atom_type_2', 'type': 'enum', 'mandatory': True, 'default-from': 'Atom_ID_2',
                                            'enum': set(ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS.keys()),
                                            'enforce-enum': True},
                                           {'name': 'Atom_isotope_number_2', 'type': 'enum-int', 'mandatory': True, 'default-from': 'Atom_ID_2',
                                            'enum': set(ALLOWED_ISOTOPE_NUMBERS),
                                            'enforce-enum': True},
                                           {'name': 'Ambiguity_code_2', 'type': 'enum-int', 'mandatory': False,
                                            'enum': ALLOWED_AMBIGUITY_CODES,
                                            'enforce-enum': True},
                                           {'name': 'Val', 'type': 'float', 'mandatory': False, 'group-mandatory': True,
                                            'clear-bad-pattern': True,
                                            'group': {'member-with': ['Val_min', 'Val_max'],
                                                      'coexist-with': None,
                                                      'smaller-than': None,
                                                      'larger-than': None}},
                                           {'name': 'Val_err', 'type': 'range-float', 'mandatory': False, 'void-zero': True,
                                            'clear-bad-pattern': True,
                                            'range': {'min_inclusive': 0.0}},
                                           {'name': 'Val_min', 'type': 'float', 'mandatory': False, 'group-mandatory': True,
                                            'clear-bad-pattern': True,
                                            'group': {'member-with': ['Val', 'Val_max'],
                                                      'coexist-with': None,
                                                      'smaller-than': None,
                                                      'larger-than': ['Val_max']}},
                                           {'name': 'Val_max', 'type': 'float', 'mandatory': False, 'group-mandatory': True,
                                            'clear-bad-pattern': True,
                                            'group': {'member-with': ['Val', 'Val_min'],
                                                      'coexist-with': None,
                                                      'smaller-than': ['Val_min'],
                                                      'larger-than': None}},
                                           {'name': 'Val_bond_length', 'type': 'range-float', 'mandatory': False,
                                            'range': DIST_RESTRAINT_RANGE},
                                           {'name': 'Auth_entity_assembly_ID_1', 'type': 'str', 'mandatory': False},
                                           {'name': 'Auth_seq_ID_1', 'type': 'int', 'mandatory': False},
                                           {'name': 'Auth_comp_ID_1', 'type': 'str', 'mandatory': False},
                                           {'name': 'Auth_atom_ID_1', 'type': 'str', 'mandatory': False},
                                           {'name': 'Auth_entity_assembly_ID_2', 'type': 'str', 'mandatory': False},
                                           {'name': 'Auth_seq_ID_2', 'type': 'int', 'mandatory': False},
                                           {'name': 'Auth_comp_ID_2', 'type': 'str', 'mandatory': False},
                                           {'name': 'Auth_atom_ID_2', 'type': 'str', 'mandatory': False},
                                           {'name': 'RDC_list_ID', 'type': 'pointer-index', 'mandatory': True,
                                            'default': '1', 'default-from': 'parent'},
                                           {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                           ],
                          'csa_restraint': [{'name': 'Atom_type', 'type': 'enum', 'mandatory': True, 'default-from': 'Atom_ID',
                                             'enum': set(ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS.keys()),
                                             'enforce-enum': True},
                                            {'name': 'Atom_isotope_number', 'type': 'enum-int', 'mandatory': True, 'default-from': 'Atom_ID',
                                             'enum': set(ALLOWED_ISOTOPE_NUMBERS),
                                             'enforce-enum': True},
                                            {'name': 'Val', 'type': 'range-float', 'mandatory': True,
                                             'clear-bad-pattern': True,
                                             'range': CSA_RESTRAINT_RANGE},
                                            {'name': 'Val_err', 'type': 'range-float', 'mandatory': False, 'void-zero': True,
                                             'clear-bad-pattern': True,
                                             'range': {'min_inclusive': 0.0}},
                                            {'name': 'Principal_value_sigma_11_val', 'type': 'range-float', 'mandatory': False, 'group-mandatory': False,
                                             'range': CSA_RESTRAINT_RANGE,
                                             'group': {'member-with': ['Principal_value_sigma_22_val', 'Principal_value_sigma_33_val'],
                                                       'coexist-with': None}},
                                            {'name': 'Principal_value_sigma_22_val', 'type': 'range-float', 'mandatory': False, 'group-mandatory': False,
                                             'range': CSA_RESTRAINT_RANGE,
                                             'group': {'member-with': ['Principal_value_sigma_11_val', 'Principal_value_sigma_33_val'],
                                                       'coexist-with': None}},
                                            {'name': 'Principal_value_sigma_33_val', 'type': 'range-float', 'mandatory': False, 'group-mandatory': False,
                                             'range': CSA_RESTRAINT_RANGE,
                                             'group': {'member-with': ['Principal_value_sigma_11_val', 'Principal_value_sigma_22_val'],
                                                       'coexist-with': None}},
                                            {'name': 'Principal_Euler_angle_alpha_val', 'type': 'range-float', 'mandatory': False, 'group-mandatory': False,
                                             'range': ANGLE_RESTRAINT_RANGE,
                                             'group': {'member-with': ['Principal_Euler_angle_beta_val', 'Principal_Euler_angle_gamma_val'],
                                                       'coexist-with': None}},
                                            {'name': 'Principal_Euler_angle_beta_val', 'type': 'range-float', 'mandatory': False, 'group-mandatory': False,
                                             'range': ANGLE_RESTRAINT_RANGE,
                                             'group': {'member-with': ['Principal_Euler_angle_alpha_val', 'Principal_Euler_angle_gamma_val'],
                                                       'coexist-with': None}},
                                            {'name': 'Principal_Euler_angle_gamma_val', 'type': 'range-float', 'mandatory': False, 'group-mandatory': False,
                                             'range': ANGLE_RESTRAINT_RANGE,
                                             'group': {'member-with': ['Principal_Euler_angle_alpha_val', 'Principal_Euler_angle_beta_val'],
                                                       'coexist-with': None}},
                                            {'name': 'Bond_length', 'type': 'range-float', 'mandatory': False,
                                             'range': DIST_RESTRAINT_RANGE},
                                            {'name': 'Auth_entity_assembly_ID', 'type': 'str', 'mandatory': False},
                                            {'name': 'Auth_seq_ID', 'type': 'int', 'mandatory': False},
                                            {'name': 'Auth_comp_ID', 'type': 'str', 'mandatory': False},
                                            {'name': 'Auth_atom_ID', 'type': 'str', 'mandatory': False},
                                            {'name': 'Chem_shift_anisotropy_ID', 'type': 'pointer-index', 'mandatory': True,
                                             'default': '1', 'default-from': 'parent'},
                                            {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                            ],
                          'ddc_restraint': [{'name': 'Dipolar_coupling_code', 'type': 'str', 'mandatory': True},
                                            {'name': 'Atom_type_1', 'type': 'enum', 'mandatory': True, 'default-from': 'Atom_ID_1',
                                             'enum': set(ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS.keys()),
                                             'enforce-enum': True},
                                            {'name': 'Atom_isotope_number_1', 'type': 'enum-int', 'mandatory': True, 'default-from': 'Atom_ID_1',
                                             'enum': set(ALLOWED_ISOTOPE_NUMBERS),
                                             'enforce-enum': True},
                                            {'name': 'Ambiguity_code_1', 'type': 'enum-int', 'mandatory': False,
                                             'enum': ALLOWED_AMBIGUITY_CODES,
                                             'enforce-enum': True},
                                            {'name': 'Atom_type_2', 'type': 'enum', 'mandatory': True, 'default-from': 'Atom_ID_2',
                                             'enum': set(ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS.keys()),
                                             'enforce-enum': True},
                                            {'name': 'Atom_isotope_number_2', 'type': 'enum-int', 'mandatory': True, 'default-from': 'Atom_ID_2',
                                             'enum': set(ALLOWED_ISOTOPE_NUMBERS),
                                             'enforce-enum': True},
                                            {'name': 'Ambiguity_code_2', 'type': 'enum-int', 'mandatory': False,
                                             'enum': ALLOWED_AMBIGUITY_CODES,
                                             'enforce-enum': True},
                                            {'name': 'Val', 'type': 'float', 'mandatory': False, 'group-mandatory': True,
                                             'clear-bad-pattern': True,
                                             'range': RDC_RESTRAINT_RANGE,
                                             'group': {'member-with': ['Val_min', 'Val_max'],
                                                       'coexist-with': None,
                                                       'smaller-than': None,
                                                       'larger-than': None}},
                                            {'name': 'Val_err', 'type': 'range-float', 'mandatory': False, 'void-zero': True,
                                             'clear-bad-pattern': True,
                                             'range': {'min_inclusive': 0.0}},
                                            {'name': 'Val_min', 'type': 'float', 'mandatory': False, 'group-mandatory': True,
                                             'clear-bad-pattern': True,
                                             'range': RDC_RESTRAINT_RANGE,
                                             'group': {'member-with': ['Val_max'],
                                                       'coexist-with': None,
                                                       'smaller-than': None,
                                                       'larger-than': ['Val_max']}},
                                            {'name': 'Val_max', 'type': 'float', 'mandatory': False, 'group-mandatory': True,
                                             'clear-bad-pattern': True,
                                             'range': RDC_RESTRAINT_RANGE,
                                             'group': {'member-with': ['Val_min'],
                                                       'coexist-with': None,
                                                       'smaller-than': ['Val_min'],
                                                       'larger-than': None}},
                                            {'name': 'Principal_Euler_angle_alpha_val', 'type': 'range-float', 'mandatory': False, 'group-mandatory': False,
                                             'range': ANGLE_RESTRAINT_RANGE,
                                             'group': {'member-with': ['Principal_Euler_angle_beta_val', 'Principal_Euler_angle_gamma_val'],
                                                       'coexist-with': None}},
                                            {'name': 'Principal_Euler_angle_beta_val', 'type': 'range-float', 'mandatory': False, 'group-mandatory': False,
                                             'range': ANGLE_RESTRAINT_RANGE,
                                             'group': {'member-with': ['Principal_Euler_angle_alpha_val', 'Principal_Euler_angle_gamma_val'],
                                                       'coexist-with': None}},
                                            {'name': 'Principal_Euler_angle_gamma_val', 'type': 'range-float', 'mandatory': False, 'group-mandatory': False,
                                             'range': ANGLE_RESTRAINT_RANGE,
                                             'group': {'member-with': ['Principal_Euler_angle_alpha_val', 'Principal_Euler_angle_beta_val'],
                                                       'coexist-with': None}},
                                            {'name': 'Auth_entity_assembly_ID_1', 'type': 'str', 'mandatory': False},
                                            {'name': 'Auth_seq_ID_1', 'type': 'int', 'mandatory': False},
                                            {'name': 'Auth_comp_ID_1', 'type': 'str', 'mandatory': False},
                                            {'name': 'Auth_atom_ID_1', 'type': 'str', 'mandatory': False},
                                            {'name': 'Auth_entity_assembly_ID_2', 'type': 'str', 'mandatory': False},
                                            {'name': 'Auth_seq_ID_2', 'type': 'int', 'mandatory': False},
                                            {'name': 'Auth_comp_ID_2', 'type': 'str', 'mandatory': False},
                                            {'name': 'Auth_atom_ID_2', 'type': 'str', 'mandatory': False},
                                            {'name': 'Dipolar_coupling_list_ID', 'type': 'pointer-index', 'mandatory': True,
                                             'default': '1', 'default-from': 'parent'},
                                            {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                            ],
                          'hvycs_restraint': [{'name': 'CA_chem_shift_val', 'type': 'range-float', 'mandatory': True,
                                               'clear-bad-pattern': True,
                                               'range': CS_RESTRAINT_RANGE},
                                              {'name': 'CA_chem_shift_val_err', 'type': 'range-float', 'mandatory': False, 'void-zero': True,
                                               'clear-bad-pattern': True,
                                               'range': CS_UNCERTAINTY_RANGE},
                                              {'name': 'CB_chem_shift_val', 'type': 'range-float', 'mandatory': False,
                                               'clear-bad-pattern': True,
                                               'range': CS_RESTRAINT_RANGE},
                                              {'name': 'CB_chem_shift_val_err', 'type': 'range-float', 'mandatory': False, 'void-zero': True,
                                               'clear-bad-pattern': True,
                                               'range': CS_UNCERTAINTY_RANGE},
                                              {'name': 'Auth_asym_ID_1', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_seq_ID_1', 'type': 'int', 'mandatory': False},
                                              {'name': 'Auth_comp_ID_1', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_atom_ID_1', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_asym_ID_2', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_seq_ID_2', 'type': 'int', 'mandatory': False},
                                              {'name': 'Auth_comp_ID_2', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_atom_ID_2', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_asym_ID_3', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_seq_ID_3', 'type': 'int', 'mandatory': False},
                                              {'name': 'Auth_comp_ID_3', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_atom_ID_3', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_asym_ID_4', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_seq_ID_4', 'type': 'int', 'mandatory': False},
                                              {'name': 'Auth_comp_ID_4', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_atom_ID_4', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_asym_ID_5', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_seq_ID_5', 'type': 'int', 'mandatory': False},
                                              {'name': 'Auth_comp_ID_5', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_atom_ID_5', 'type': 'str', 'mandatory': False},
                                              {'name': 'CA_CB_constraint_list_ID', 'type': 'pointer-index', 'mandatory': True,
                                               'default': '1', 'default-from': 'parent'},
                                              {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                              ],
                          'procs_restraint': [{'name': 'Atom_type', 'type': 'enum', 'mandatory': True, 'default-from': 'Atom_ID',
                                               'enum': set(ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS.keys()),
                                               'enforce-enum': True},
                                              {'name': 'Atom_isotope_number', 'type': 'enum-int', 'mandatory': True, 'default-from': 'Atom_ID',
                                               'enum': set(ALLOWED_ISOTOPE_NUMBERS),
                                               'enforce-enum': True},
                                              {'name': 'Chem_shift_val', 'type': 'range-float', 'mandatory': True,
                                               'remove-bad-patter': True,
                                               'range': CS_RESTRAINT_RANGE},
                                              {'name': 'Chem_shift_val_err', 'type': 'range-float', 'mandatory': False, 'void-zero': True,
                                               'clear-bad-pattern': True,
                                               'range': CS_UNCERTAINTY_RANGE},
                                              {'name': 'Auth_asym_ID', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_seq_ID', 'type': 'int', 'mandatory': False},
                                              {'name': 'Auth_comp_ID', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_atom_ID', 'type': 'str', 'mandatory': False},
                                              {'name': 'H_chem_shift_constraint_list_ID', 'type': 'pointer-index', 'mandatory': True,
                                               'default': '1', 'default-from': 'parent'},
                                              {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                              ],
                          'csp_restraint': [{'name': 'Atom_type', 'type': 'enum', 'mandatory': True, 'default-from': 'Atom_ID',
                                             'enum': set(ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS.keys()),
                                             'enforce-enum': True},
                                            {'name': 'Atom_isotope_number', 'type': 'enum-int', 'mandatory': True, 'default-from': 'Atom_ID',
                                             'enum': set(ALLOWED_ISOTOPE_NUMBERS),
                                             'enforce-enum': True},
                                            {'name': 'Chem_shift_val', 'type': 'range-float', 'mandatory': False,
                                             'clear-bad-pattern': True,
                                             'range': CS_RESTRAINT_RANGE},
                                            {'name': 'Chem_shift_val_err', 'type': 'range-float', 'mandatory': False, 'void-zero': True,
                                             'clear-bad-pattern': True,
                                             'range': CS_UNCERTAINTY_RANGE},
                                            {'name': 'Difference_chem_shift_val', 'type': 'range-float', 'mandatory': False,
                                             'clear-bad-pattern': True,
                                             'range': CS_RESTRAINT_RANGE},
                                            {'name': 'Difference_chem_shift_val_err', 'type': 'range-float', 'mandatory': False, 'void-zero': True,
                                             'clear-bad-pattern': True,
                                             'range': CS_UNCERTAINTY_RANGE},
                                            {'name': 'Auth_entity_assembly_ID', 'type': 'str', 'mandatory': False},
                                            {'name': 'Auth_seq_ID', 'type': 'int', 'mandatory': False},
                                            {'name': 'Auth_comp_ID', 'type': 'str', 'mandatory': False},
                                            {'name': 'Auth_atom_ID', 'type': 'str', 'mandatory': False},
                                            {'name': 'Chem_shift_perturbation_list_ID', 'type': 'pointer-index', 'mandatory': True,
                                             'default': '1', 'default-from': 'parent'},
                                            {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                            ],
                          'auto_relax_restraint': [{'name': 'Atom_type', 'type': 'enum', 'mandatory': True, 'default-from': 'Atom_ID',
                                                    'enum': set(ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS.keys()),
                                                    'enforce-enum': True},
                                                   {'name': 'Atom_isotope_number', 'type': 'enum-int', 'mandatory': True, 'default-from': 'Atom_ID',
                                                    'enum': set(ALLOWED_ISOTOPE_NUMBERS),
                                                    'enforce-enum': True},
                                                   {'name': 'Auto_relaxation_val', 'type': 'range-float', 'mandatory': True,
                                                    'remove-bad-patter': True,
                                                    'range': PRE_RESTRAINT_RANGE},
                                                   {'name': 'Auto_relaxation_val_err', 'type': 'range-float', 'mandatory': False, 'void-zero': True,
                                                    'clear-bad-pattern': True,
                                                    'range': PRE_RESTRAINT_RANGE},
                                                   {'name': 'Rex_val', 'type': 'range-float', 'mandatory': False,
                                                    'clear-bad-pattern': True,
                                                    'range': PRE_RESTRAINT_RANGE},
                                                   {'name': 'Rex_val_err', 'type': 'range-float', 'mandatory': False, 'void-zero': True,
                                                    'clear-bad-pattern': True,
                                                    'range': PRE_RESTRAINT_RANGE},
                                                   {'name': 'Auth_entity_assembly_ID', 'type': 'str', 'mandatory': False},
                                                   {'name': 'Auth_seq_ID', 'type': 'int', 'mandatory': False},
                                                   {'name': 'Auth_comp_ID', 'type': 'str', 'mandatory': False},
                                                   {'name': 'Auth_atom_ID', 'type': 'str', 'mandatory': False},
                                                   {'name': 'Auto_relaxation_list_ID', 'type': 'pointer-index', 'mandatory': True,
                                                    'default': '1', 'default-from': 'parent'},
                                                   {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                                   ],
                          'heteronucl_noe_data': [{'name': 'Atom_type_1', 'type': 'enum', 'mandatory': True, 'default-from': 'Atom_ID_1',
                                                   'enum': set(ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS.keys()),
                                                   'enforce-enum': True},
                                                  {'name': 'Atom_isotope_number_1', 'type': 'enum-int', 'mandatory': True, 'default-from': 'Atom_ID_1',
                                                   'enum': set(ALLOWED_ISOTOPE_NUMBERS),
                                                   'enforce-enum': True},
                                                  {'name': 'Atom_type_2', 'type': 'enum', 'mandatory': True, 'default-from': 'Atom_ID_2',
                                                   'enum': set(ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS.keys()),
                                                   'enforce-enum': True},
                                                  {'name': 'Atom_isotope_number_2', 'type': 'enum-int', 'mandatory': True, 'default-from': 'Atom_ID_2',
                                                   'enum': set(ALLOWED_ISOTOPE_NUMBERS),
                                                   'enforce-enum': True},
                                                  {'name': 'Val', 'type': 'float', 'mandatory': True,
                                                   'remove-bad-patter': True},
                                                  {'name': 'Val_err', 'type': 'range-float', 'mandatory': False, 'void-zero': True,
                                                   'clear-bad-pattern': True,
                                                   'range': {'min_inclusive': 0.0}},
                                                  {'name': 'Auth_entity_assembly_ID_1', 'type': 'str', 'mandatory': False},
                                                  {'name': 'Auth_seq_ID_1', 'type': 'int', 'mandatory': False},
                                                  {'name': 'Auth_comp_ID_1', 'type': 'str', 'mandatory': False},
                                                  {'name': 'Auth_atom_ID_1', 'type': 'str', 'mandatory': False},
                                                  {'name': 'Auth_entity_assembly_ID_2', 'type': 'str', 'mandatory': False},
                                                  {'name': 'Auth_seq_ID_2', 'type': 'int', 'mandatory': False},
                                                  {'name': 'Auth_comp_ID_2', 'type': 'str', 'mandatory': False},
                                                  {'name': 'Auth_atom_ID_2', 'type': 'str', 'mandatory': False},
                                                  {'name': 'Heteronucl_NOE_list_ID', 'type': 'pointer-index', 'mandatory': True,
                                                   'default': '1', 'default-from': 'parent'},
                                                  {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                                  ],
                          'heteronucl_t1_data': [{'name': 'Atom_type', 'type': 'enum', 'mandatory': True, 'default-from': 'Atom_ID',
                                                  'enum': set(ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS.keys()),
                                                  'enforce-enum': True},
                                                 {'name': 'Atom_isotope_number', 'type': 'enum-int', 'mandatory': True, 'default-from': 'Atom_ID',
                                                  'enum': set(ALLOWED_ISOTOPE_NUMBERS),
                                                  'enforce-enum': True},
                                                 {'name': 'Val', 'type': 'float', 'mandatory': True,
                                                  'remove-bad-patter': True},
                                                 {'name': 'Val_err', 'type': 'range-float', 'mandatory': False, 'void-zero': True,
                                                  'clear-bad-pattern': True,
                                                  'range': {'min_inclusive': 0.0}},
                                                 {'name': 'Auth_entity_assembly_ID', 'type': 'str', 'mandatory': False},
                                                 {'name': 'Auth_seq_ID', 'type': 'int', 'mandatory': False},
                                                 {'name': 'Auth_comp_ID', 'type': 'str', 'mandatory': False},
                                                 {'name': 'Auth_atom_ID', 'type': 'str', 'mandatory': False},
                                                 {'name': 'Heteronucl_T1_list_ID', 'type': 'pointer-index', 'mandatory': True,
                                                  'default': '1', 'default-from': 'parent'},
                                                 {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                                 ],
                          'heteronucl_t2_data': [{'name': 'Atom_type', 'type': 'enum', 'mandatory': True, 'default-from': 'Atom_ID',
                                                  'enum': set(ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS.keys()),
                                                  'enforce-enum': True},
                                                 {'name': 'Atom_isotope_number', 'type': 'enum-int', 'mandatory': True, 'default-from': 'Atom_ID',
                                                  'enum': set(ALLOWED_ISOTOPE_NUMBERS),
                                                  'enforce-enum': True},
                                                 {'name': 'T2_val', 'type': 'float', 'mandatory': True,
                                                  'remove-bad-patter': True},
                                                 {'name': 'T2_val_err', 'type': 'range-float', 'mandatory': False, 'void-zero': True,
                                                  'clear-bad-pattern': True,
                                                  'range': {'min_inclusive': 0.0}},
                                                 {'name': 'Rex_val', 'type': 'float', 'mandatory': False,
                                                  'clear-bad-pattern': True},
                                                 {'name': 'Rex_err', 'type': 'range-float', 'mandatory': False, 'void-zero': True,
                                                  'clear-bad-pattern': True,
                                                  'range': {'min_inclusive': 0.0}},
                                                 {'name': 'Auth_entity_assembly_ID', 'type': 'str', 'mandatory': False},
                                                 {'name': 'Auth_seq_ID', 'type': 'int', 'mandatory': False},
                                                 {'name': 'Auth_comp_ID', 'type': 'str', 'mandatory': False},
                                                 {'name': 'Auth_atom_ID', 'type': 'str', 'mandatory': False},
                                                 {'name': 'Heteronucl_T2_list_ID', 'type': 'pointer-index', 'mandatory': True,
                                                  'default': '1', 'default-from': 'parent'},
                                                 {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                                 ],
                          'heteronucl_t1r_data': [{'name': 'Atom_type', 'type': 'enum', 'mandatory': True, 'default-from': 'Atom_ID',
                                                   'enum': set(ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS.keys()),
                                                   'enforce-enum': True},
                                                  {'name': 'Atom_isotope_number', 'type': 'enum-int', 'mandatory': True, 'default-from': 'Atom_ID',
                                                   'enum': set(ALLOWED_ISOTOPE_NUMBERS),
                                                   'enforce-enum': True},
                                                  {'name': 'T1rho_val', 'type': 'float', 'mandatory': True,
                                                   'remove-bad-patter': True},
                                                  {'name': 'T1rho_val_err', 'type': 'range-float', 'mandatory': False, 'void-zero': True,
                                                   'clear-bad-pattern': True,
                                                   'range': {'min_inclusive': 0.0}},
                                                  {'name': 'Rex_val', 'type': 'float', 'mandatory': False,
                                                   'clear-bad-pattern': True},
                                                  {'name': 'Rex_val_err', 'type': 'range-float', 'mandatory': False, 'void-zero': True,
                                                   'clear-bad-pattern': True,
                                                   'range': {'min_inclusive': 0.0}},
                                                  {'name': 'Auth_entity_assembly_ID', 'type': 'str', 'mandatory': False},
                                                  {'name': 'Auth_seq_ID', 'type': 'int', 'mandatory': False},
                                                  {'name': 'Auth_comp_ID', 'type': 'str', 'mandatory': False},
                                                  {'name': 'Auth_atom_ID', 'type': 'str', 'mandatory': False},
                                                  {'name': 'Heteronucl_T1rho_list_ID', 'type': 'pointer-index', 'mandatory': True,
                                                   'default': '1', 'default-from': 'parent'},
                                                  {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                                  ],
                          'order_param_data': [{'name': 'Atom_type', 'type': 'enum', 'mandatory': True, 'default-from': 'Atom_ID',
                                                'enum': set(ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS.keys()),
                                                'enforce-enum': True},
                                               {'name': 'Atom_isotope_number', 'type': 'enum-int', 'mandatory': True, 'default-from': 'Atom_ID',
                                                'enum': set(ALLOWED_ISOTOPE_NUMBERS),
                                                'enforce-enum': True},
                                               {'name': 'Order_param_val', 'type': 'range-float', 'mandatory': True,
                                                'clear-bad-pattern': True,
                                                'range': PROBABILITY_RANGE},
                                               {'name': 'Order_param_val_fit_err', 'type': 'range-float', 'mandatory': False,
                                                'clear-bad-pattern': True,
                                                'range': PROBABILITY_RANGE},
                                               {'name': 'Tau_e_val', 'type': 'positive-float', 'mandatory': False,
                                                'clear-bad-pattern': True},
                                               {'name': 'Tau_e_val_fit_err', 'type': 'positive-float', 'mandatory': False,
                                                'clear-bad-pattern': True},
                                               {'name': 'Tau_f_val', 'type': 'positive-float', 'mandatory': False,
                                                'clear-bad-pattern': True},
                                               {'name': 'Tau_f_val_fit_err', 'type': 'positive-float', 'mandatory': False,
                                                'clear-bad-pattern': True},
                                               {'name': 'Tau_s_val', 'type': 'positive-float', 'mandatory': False,
                                                'clear-bad-pattern': True},
                                               {'name': 'Tau_s_val_fit_err', 'type': 'positive-float', 'mandatory': False,
                                                'clear-bad-pattern': True},
                                               {'name': 'Rex_val', 'type': 'range-float', 'mandatory': False,
                                                'clear-bad-pattern': True,
                                                'range': PRE_RESTRAINT_RANGE},
                                               {'name': 'Rex_val_fit_err', 'type': 'range-float', 'mandatory': False, 'void-zero': True,
                                                'clear-bad-pattern': True,
                                                'range': PRE_RESTRAINT_RANGE},
                                               {'name': 'Model_free_sum_squared_errs', 'type': 'positive-float', 'mandatory': False,
                                                'clear-bad-pattern': True},
                                               {'name': 'Model_fit', 'type': 'enum', 'mandatory': False,
                                                'enum': ('Rex', 'S2', 'S2, te', 'S2, Rex', 'S2, te, Rex', 'S2f, S2, ts', 'S2f, S2s, ts',
                                                         'S2f, tf, S2, ts', 'S2f, tf, S2s, ts', 'S2f, S2, ts, Rex', 'S2f, S2s, ts, Rex',
                                                         'S2f, tf, S2, ts, Rex', 'S2f, tf, S2s, ts, Rex', 'na')},
                                               {'name': 'Sf2_val', 'type': 'range-float', 'mandatory': False,
                                                'clear-bad-pattern': True,
                                                'range': PROBABILITY_RANGE},
                                               {'name': 'Sf2_val_fit_err', 'type': 'range-float', 'mandatory': False,
                                                'clear-bad-pattern': True,
                                                'range': PROBABILITY_RANGE},
                                               {'name': 'Ss2_val', 'type': 'range-float', 'mandatory': False,
                                                'clear-bad-pattern': True,
                                                'range': PROBABILITY_RANGE},
                                               {'name': 'Ss2_val_fit_err', 'type': 'range-float', 'mandatory': False,
                                                'clear-bad-pattern': True,
                                                'range': PROBABILITY_RANGE},
                                               {'name': 'SH2_val', 'type': 'range-float', 'mandatory': False,
                                                'clear-bad-pattern': True,
                                                'range': PROBABILITY_RANGE},
                                               {'name': 'SH2_val_fit_err', 'type': 'range-float', 'mandatory': False,
                                                'clear-bad-pattern': True,
                                                'range': PROBABILITY_RANGE},
                                               {'name': 'SN2_val', 'type': 'range-float', 'mandatory': False,
                                                'clear-bad-pattern': True,
                                                'range': PROBABILITY_RANGE},
                                               {'name': 'SN2_val_fit_err', 'type': 'range-float', 'mandatory': False,
                                                'clear-bad-pattern': True,
                                                'range': PROBABILITY_RANGE},
                                               {'name': 'Auth_entity_assembly_ID', 'type': 'str', 'mandatory': False},
                                               {'name': 'Auth_seq_ID', 'type': 'int', 'mandatory': False},
                                               {'name': 'Auth_comp_ID', 'type': 'str', 'mandatory': False},
                                               {'name': 'Auth_atom_ID', 'type': 'str', 'mandatory': False},
                                               {'name': 'Order_parameter_list_ID', 'type': 'pointer-index', 'mandatory': True,
                                                'default': '1', 'default-from': 'parent'},
                                               {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                               ],
                          'ph_titr_data': [{'name': 'Atm_obs_atom_type', 'type': 'enum', 'mandatory': True, 'default-from': 'Atm_obs_atom_ID',
                                            'enum': set(ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS.keys()),
                                            'enforce-enum': True},
                                           {'name': 'Atm_obs_atom_isotope_number', 'type': 'enum-int', 'mandatory': True, 'default-from': 'Atm_obs_atom_ID',
                                            'enum': set(ALLOWED_ISOTOPE_NUMBERS),
                                            'enforce-enum': True},
                                           {'name': 'Atm_titr_atom_type', 'type': 'enum', 'mandatory': True, 'default-from': 'Atm_titr_atom_ID',
                                            'enum': set(ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS.keys()),
                                            'enforce-enum': True},
                                           {'name': 'Atm_titr_atom_isotope_number', 'type': 'enum-int', 'mandatory': True, 'default-from': 'Atm_titr_atom_ID',
                                            'enum': set(ALLOWED_ISOTOPE_NUMBERS),
                                            'enforce-enum': True},
                                           {'name': 'Hill_coeff_val', 'type': 'positive-float', 'mandatory': False,
                                            'clear-bad-pattern': True},
                                           {'name': 'Hill_coeff_val_fit_err', 'type': 'positive-float', 'mandatory': False,
                                            'clear-bad-pattern': True},
                                           {'name': 'High_PH_param_fit_val', 'type': 'positive-float', 'mandatory': False,
                                            'clear-bad-pattern': True},
                                           {'name': 'High_PH_param_fit_val_err', 'type': 'positive-float', 'mandatory': False,
                                            'clear-bad-pattern': True},
                                           {'name': 'Low_PH_param_fit_val', 'type': 'positive-float', 'mandatory': False,
                                            'clear-bad-pattern': True},
                                           {'name': 'Low_PH_param_fit_val_err', 'type': 'positive-float', 'mandatory': False,
                                            'clear-bad-pattern': True},
                                           {'name': 'PKa_val', 'type': 'positive-float', 'mandatory': True,
                                            'clear-bad-pattern': True},
                                           {'name': 'PKa_val_fit_err', 'type': 'positive-float', 'mandatory': True,
                                            'clear-bad-pattern': True},
                                           {'name': 'PHmid_val', 'type': 'positive-float', 'mandatory': False,
                                            'clear-bad-pattern': True},
                                           {'name': 'PHmid_val_fit_err', 'type': 'positive-float', 'mandatory': False,
                                            'clear-bad-pattern': True},
                                           {'name': 'Atm_obs_auth_entity_assembly_ID', 'type': 'str', 'mandatory': False},
                                           {'name': 'Atm_obs_auth_seq_ID', 'type': 'int', 'mandatory': False},
                                           {'name': 'Atm_obs_auth_comp_ID', 'type': 'str', 'mandatory': False},
                                           {'name': 'Atm_obs_auth_atom_ID', 'type': 'str', 'mandatory': False},
                                           {'name': 'Atm_titr_auth_entity_assembly_ID', 'type': 'str', 'mandatory': False},
                                           {'name': 'Atm_titr_auth_seq_ID', 'type': 'int', 'mandatory': False},
                                           {'name': 'Atm_titr_auth_comp_ID', 'type': 'str', 'mandatory': False},
                                           {'name': 'Atm_titr_auth_atom_ID', 'type': 'str', 'mandatory': False},
                                           {'name': 'PH_titration_list_ID', 'type': 'pointer-index', 'mandatory': True,
                                            'default': '1', 'default-from': 'parent'},
                                           {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                           ],
                          'ph_param_data': [{'name': 'PH_titr_result_ID', 'type': 'positive-int', 'mandatory': True},
                                            {'name': 'PH_val', 'type': 'positive-float', 'mandatory': True},
                                            {'name': 'PH_val_err', 'type': 'positive-float', 'mandatory': False},
                                            {'name': 'Observed_NMR_param_val', 'type': 'positive-float', 'mandatory': True},
                                            {'name': 'Observed_NMR_param_val_err', 'type': 'positive-float', 'mandatory': False},
                                            {'name': 'PH_param_list_ID', 'type': 'pointer-index', 'mandatory': True,
                                             'default': '1', 'default-from': 'parent'},
                                            {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                            ],
                          'coupling_const_data': [{'name': 'Code', 'type': 'str', 'mandatory': True},
                                                  {'name': 'Atom_type_1', 'type': 'enum', 'mandatory': True, 'default-from': 'Atom_ID_1',
                                                   'enum': set(ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS.keys()),
                                                   'enforce-enum': True},
                                                  {'name': 'Atom_isotope_number_1', 'type': 'enum-int', 'mandatory': True, 'default-from': 'Atom_ID_1',
                                                   'enum': set(ALLOWED_ISOTOPE_NUMBERS),
                                                   'enforce-enum': True},
                                                  {'name': 'Ambiguity_code_1', 'type': 'enum-int', 'mandatory': False,
                                                   'enum': ALLOWED_AMBIGUITY_CODES,
                                                   'enforce-enum': True},
                                                  {'name': 'Atom_type_2', 'type': 'enum', 'mandatory': True, 'default-from': 'Atom_ID_2',
                                                   'enum': set(ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS.keys()),
                                                   'enforce-enum': True},
                                                  {'name': 'Atom_isotope_number_2', 'type': 'enum-int', 'mandatory': True, 'default-from': 'Atom_ID_2',
                                                   'enum': set(ALLOWED_ISOTOPE_NUMBERS),
                                                   'enforce-enum': True},
                                                  {'name': 'Ambiguity_code_2', 'type': 'enum-int', 'mandatory': False,
                                                   'enum': ALLOWED_AMBIGUITY_CODES,
                                                   'enforce-enum': True},
                                                  {'name': 'Val', 'type': 'float', 'mandatory': False, 'group-mandatory': True,
                                                   'clear-bad-pattern': True,
                                                   'group': {'member-with': ['Val_min', 'Val_max'],
                                                             'coexist-with': None,
                                                             'smaller-than': None,
                                                             'larger-than': None}},
                                                  {'name': 'Val_err', 'type': 'range-float', 'mandatory': False, 'void-zero': True,
                                                   'clear-bad-pattern': True,
                                                   'range': {'min_inclusive': 0.0}},
                                                  {'name': 'Val_min', 'type': 'float', 'mandatory': False, 'group-mandatory': True,
                                                   'clear-bad-pattern': True,
                                                   'group': {'member-with': ['Val', 'Val_max'],
                                                             'coexist-with': None,
                                                             'smaller-than': None,
                                                             'larger-than': ['Val_max']}},
                                                  {'name': 'Val_max', 'type': 'float', 'mandatory': False, 'group-mandatory': True,
                                                   'clear-bad-pattern': True,
                                                   'group': {'member-with': ['Val', 'Val_min'],
                                                             'coexist-with': None,
                                                             'smaller-than': ['Val_min'],
                                                             'larger-than': None}},
                                                  {'name': 'Auth_entity_assembly_ID_1', 'type': 'str', 'mandatory': False},
                                                  {'name': 'Auth_seq_ID_1', 'type': 'int', 'mandatory': False},
                                                  {'name': 'Auth_comp_ID_1', 'type': 'str', 'mandatory': False},
                                                  {'name': 'Auth_atom_ID_1', 'type': 'str', 'mandatory': False},
                                                  {'name': 'Auth_entity_assembly_ID_2', 'type': 'str', 'mandatory': False},
                                                  {'name': 'Auth_seq_ID_2', 'type': 'int', 'mandatory': False},
                                                  {'name': 'Auth_comp_ID_2', 'type': 'str', 'mandatory': False},
                                                  {'name': 'Auth_atom_ID_2', 'type': 'str', 'mandatory': False},
                                                  {'name': 'Coupling_constant_list_ID', 'type': 'pointer-index', 'mandatory': True, 'default': '1', 'default-from': 'parent'},
                                                  {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                                  ],
                          'ccr_d_csa_restraint': [{'name': 'Dipole_atom_type_1', 'type': 'enum', 'mandatory': True, 'default-from': 'Dipole_atom_ID_1',
                                                   'enum': set(ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS.keys()),
                                                   'enforce-enum': True},
                                                  {'name': 'Dipole_atom_isotope_number_1', 'type': 'enum-int', 'mandatory': True, 'default-from': 'Dipole_atom_ID_1',
                                                   'enum': set(ALLOWED_ISOTOPE_NUMBERS),
                                                   'enforce-enum': True},
                                                  {'name': 'Dipole_atom_type_2', 'type': 'enum', 'mandatory': True, 'default-from': 'Dipole_atom_ID_2',
                                                   'enum': set(ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS.keys()),
                                                   'enforce-enum': True},
                                                  {'name': 'Dipole_atom_isotope_number_2', 'type': 'enum-int', 'mandatory': True, 'default-from': 'Dipole_atom_ID_2',
                                                   'enum': set(ALLOWED_ISOTOPE_NUMBERS),
                                                   'enforce-enum': True},
                                                  {'name': 'CSA_atom_type_1', 'type': 'enum', 'mandatory': True, 'default-from': 'CSA_atom_ID_1',
                                                   'enum': set(ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS.keys()),
                                                   'enforce-enum': True},
                                                  {'name': 'CSA_atom_isotope_number_1', 'type': 'enum-int', 'mandatory': True, 'default-from': 'CSA_atom_ID_1',
                                                   'enum': set(ALLOWED_ISOTOPE_NUMBERS),
                                                   'enforce-enum': True},
                                                  {'name': 'CSA_atom_type_2', 'type': 'enum', 'mandatory': True, 'default-from': 'CSA_atom_ID_2',
                                                   'enum': set(ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS.keys()),
                                                   'enforce-enum': True},
                                                  {'name': 'CSA_atom_isotope_number_2', 'type': 'enum-int', 'mandatory': True, 'default-from': 'CSA_atom_ID_2',
                                                   'enum': set(ALLOWED_ISOTOPE_NUMBERS),
                                                   'enforce-enum': True},
                                                  {'name': 'Val', 'type': 'range-float', 'mandatory': True,
                                                   'remove-bad-patter': True,
                                                   'range': CCR_RESTRAINT_RANGE},
                                                  {'name': 'Val_err', 'type': 'range-float', 'mandatory': False, 'void-zero': True,
                                                   'clear-bad-pattern': True,
                                                   'range': CCR_RESTRAINT_RANGE},
                                                  {'name': 'Dipole_auth_entity_assembly_ID_1', 'type': 'str', 'mandatory': False},
                                                  {'name': 'Dipole_auth_seq_ID_1', 'type': 'int', 'mandatory': False},
                                                  {'name': 'Dipole_auth_comp_ID_1', 'type': 'str', 'mandatory': False},
                                                  {'name': 'Dipole_auth_atom_ID_1', 'type': 'str', 'mandatory': False},
                                                  {'name': 'Dipole_auth_entity_assembly_ID_2', 'type': 'str', 'mandatory': False},
                                                  {'name': 'Dipole_auth_seq_ID_2', 'type': 'int', 'mandatory': False},
                                                  {'name': 'Dipole_auth_comp_ID_2', 'type': 'str', 'mandatory': False},
                                                  {'name': 'Dipole_auth_atom_ID_2', 'type': 'str', 'mandatory': False},
                                                  {'name': 'CSA_auth_entity_assembly_ID_1', 'type': 'str', 'mandatory': False},
                                                  {'name': 'CSA_auth_seq_ID_1', 'type': 'int', 'mandatory': False},
                                                  {'name': 'CSA_auth_comp_ID_1', 'type': 'str', 'mandatory': False},
                                                  {'name': 'CSA_auth_atom_ID_1', 'type': 'str', 'mandatory': False},
                                                  {'name': 'CSA_auth_entity_assembly_ID_2', 'type': 'str', 'mandatory': False},
                                                  {'name': 'CSA_auth_seq_ID_2', 'type': 'int', 'mandatory': False},
                                                  {'name': 'CSA_auth_comp_ID_2', 'type': 'str', 'mandatory': False},
                                                  {'name': 'CSA_auth_atom_ID_2', 'type': 'str', 'mandatory': False},
                                                  {'name': 'Cross_correlation_D_CSA_list_ID', 'type': 'pointer-index', 'mandatory': True,
                                                   'default': '1', 'default-from': 'parent'},
                                                  {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                                  ],
                          'ccr_dd_restraint': [{'name': 'Dipole_1_atom_type_1', 'type': 'enum', 'mandatory': True, 'default-from': 'Dipole_1_atom_ID_1',
                                                'enum': set(ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS.keys()),
                                                'enforce-enum': True},
                                               {'name': 'Dipole_1_atom_isotope_number_1', 'type': 'enum-int', 'mandatory': True, 'default-from': 'Dipole_1_atom_ID_1',
                                                'enum': set(ALLOWED_ISOTOPE_NUMBERS),
                                                'enforce-enum': True},
                                               {'name': 'Dipole_1_atom_type_2', 'type': 'enum', 'mandatory': True, 'default-from': 'Dipole_1_atom_ID_2',
                                                'enum': set(ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS.keys()),
                                                'enforce-enum': True},
                                               {'name': 'Dipole_1_atom_isotope_number_2', 'type': 'enum-int', 'mandatory': True, 'default-from': 'Dipole_1_atom_ID_2',
                                                'enum': set(ALLOWED_ISOTOPE_NUMBERS),
                                                'enforce-enum': True},
                                               {'name': 'Dipole_2_atom_type_1', 'type': 'enum', 'mandatory': True, 'default-from': 'Dipole_2_atom_ID_1',
                                                'enum': set(ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS.keys()),
                                                'enforce-enum': True},
                                               {'name': 'Dipole_2_atom_isotope_number_1', 'type': 'enum-int', 'mandatory': True, 'default-from': 'Dipole_2_atom_ID_1',
                                                'enum': set(ALLOWED_ISOTOPE_NUMBERS),
                                                'enforce-enum': True},
                                               {'name': 'Dipole_2_atom_type_2', 'type': 'enum', 'mandatory': True, 'default-from': 'Dipole_2_atom_ID_2',
                                                'enum': set(ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS.keys()),
                                                'enforce-enum': True},
                                               {'name': 'Dipole_2_atom_isotope_number_2', 'type': 'enum-int', 'mandatory': True, 'default-from': 'Dipole_2_atom_ID_2',
                                                'enum': set(ALLOWED_ISOTOPE_NUMBERS),
                                                'enforce-enum': True},
                                               {'name': 'Val', 'type': 'range-float', 'mandatory': True,
                                                'remove-bad-patter': True,
                                                'range': CCR_RESTRAINT_RANGE},
                                               {'name': 'Val_err', 'type': 'range-float', 'mandatory': False, 'void-zero': True,
                                                'clear-bad-pattern': True,
                                                'range': CCR_RESTRAINT_RANGE},
                                               {'name': 'Dipole_1_auth_entity_assembly_ID_1', 'type': 'str', 'mandatory': False},
                                               {'name': 'Dipole_1_auth_seq_ID_1', 'type': 'int', 'mandatory': False},
                                               {'name': 'Dipole_1_auth_comp_ID_1', 'type': 'str', 'mandatory': False},
                                               {'name': 'Dipole_1_auth_atom_ID_1', 'type': 'str', 'mandatory': False},
                                               {'name': 'Dipole_1_auth_entity_assembly_ID_2', 'type': 'str', 'mandatory': False},
                                               {'name': 'Dipole_1_auth_seq_ID_2', 'type': 'int', 'mandatory': False},
                                               {'name': 'Dipole_1_auth_comp_ID_2', 'type': 'str', 'mandatory': False},
                                               {'name': 'Dipole_1_auth_atom_ID_2', 'type': 'str', 'mandatory': False},
                                               {'name': 'Dipole_2_auth_entity_assembly_ID_1', 'type': 'str', 'mandatory': False},
                                               {'name': 'Dipole_2_auth_seq_ID_1', 'type': 'int', 'mandatory': False},
                                               {'name': 'Dipole_2_auth_comp_ID_1', 'type': 'str', 'mandatory': False},
                                               {'name': 'Dipole_2_auth_atom_ID_1', 'type': 'str', 'mandatory': False},
                                               {'name': 'Dipole_2_auth_entity_assembly_ID_2', 'type': 'str', 'mandatory': False},
                                               {'name': 'Dipole_2_auth_seq_ID_2', 'type': 'int', 'mandatory': False},
                                               {'name': 'Dipole_2_auth_comp_ID_2', 'type': 'str', 'mandatory': False},
                                               {'name': 'Dipole_2_auth_atom_ID_2', 'type': 'str', 'mandatory': False},
                                               {'name': 'Cross_correlation_DD_list_ID', 'type': 'pointer-index', 'mandatory': True,
                                                'default': '1', 'default-from': 'parent'},
                                               {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                               ],
                          'fchiral_restraint': [{'name': 'Stereospecific_assignment_code', 'type': 'str', 'mandatory': False},
                                                {'name': 'Auth_asym_ID_1', 'type': 'str', 'mandatory': False},
                                                {'name': 'Auth_seq_ID_1', 'type': 'int', 'mandatory': False},
                                                {'name': 'Auth_comp_ID_1', 'type': 'str', 'mandatory': False},
                                                {'name': 'Auth_atom_ID_1', 'type': 'str', 'mandatory': False},
                                                {'name': 'Auth_asym_ID_2', 'type': 'str', 'mandatory': False},
                                                {'name': 'Auth_seq_ID_2', 'type': 'int', 'mandatory': False},
                                                {'name': 'Auth_comp_ID_2', 'type': 'str', 'mandatory': False},
                                                {'name': 'Auth_atom_ID_2', 'type': 'str', 'mandatory': False},
                                                {'name': 'Floating_chirality_assign_ID', 'type': 'pointer-index', 'mandatory': True,
                                                 'default': '1', 'default-from': 'parent'},
                                                {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                                ],
                          'saxs_restraint': [{'name': 'Intensity_val', 'type': 'float', 'mandatory': True,
                                              'remove-bad-patter': True},
                                             {'name': 'Intensity_val_err', 'type': 'float', 'mandatory': True,
                                              'clear-bad-pattern': True},
                                             {'name': 'Weight_val', 'type': 'range-float', 'mandatory': False,
                                              'range': WEIGHT_RANGE},
                                             {'name': 'SAXS_constraint_list_ID', 'type': 'pointer-index', 'mandatory': True,
                                              'default': '1', 'default-from': 'parent'},
                                             {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                             ],
                          'other_restraint': [{'name': 'Atom_type', 'type': 'enum', 'mandatory': True, 'default-from': 'Atom_ID',
                                               'enum': set(ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS.keys()),
                                               'enforce-enum': True},
                                              {'name': 'Atom_isotope_number', 'type': 'enum-int', 'mandatory': True, 'default-from': 'Atom_ID',
                                               'enum': set(ALLOWED_ISOTOPE_NUMBERS),
                                               'enforce-enum': True},
                                              {'name': 'Val', 'type': 'float', 'mandatory': True,
                                               'remove-bad-patter': True},
                                              {'name': 'Val_err', 'type': 'range-float', 'mandatory': False, 'void-zero': True,
                                               'clear-bad-pattern': True,
                                               'range': {'min_inclusive': 0.0}},
                                              {'name': 'Auth_entity_assembly_ID', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_seq_ID', 'type': 'int', 'mandatory': False},
                                              {'name': 'Auth_comp_ID', 'type': 'str', 'mandatory': False},
                                              {'name': 'Auth_atom_ID', 'type': 'str', 'mandatory': False},
                                              {'name': 'Other_data_type_list_ID', 'type': 'pointer-index', 'mandatory': True,
                                               'default': '1', 'default-from': 'parent'},
                                              {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                              ],
                          'peak2d': [{'name': 'Index_ID', 'type': 'index-int', 'mandatory': False},
                                     {'name': 'Position_1', 'type': 'float', 'mandatory': True},
                                     {'name': 'Position_uncertainty_1', 'type': 'float', 'mandatory': False},
                                     {'name': 'Line_width_1', 'type': 'float', 'mandatory': False},
                                     {'name': 'Line_width_uncertainty_1', 'type': 'float', 'mandatory': False},
                                     {'name': 'Entity_assembly_ID_1', 'type': 'positive-int-as-str', 'mandatory': False},
                                     {'name': 'Entity_ID_1', 'type': 'positive-int'},
                                     {'name': 'Comp_index_ID_1', 'type': 'int', 'mandatory': False},
                                     {'name': 'Comp_ID_1', 'type': 'str', 'mandatory': False, 'uppercase': True},
                                     {'name': 'Atom_ID_1', 'type': 'str', 'mandatory': False},
                                     {'name': 'Ambiguity_code_1', 'type': 'enum-int', 'mandatory': False,
                                      'enum': ALLOWED_AMBIGUITY_CODES},
                                     {'name': 'Ambiguity_set_ID_1', 'type': 'positive-int', 'mandatory': False},
                                     {'name': 'Auth_asym_ID_1', 'type': 'str', 'mandatory': False},
                                     {'name': 'Auth_seq_ID_1', 'type': 'int', 'mandatory': False},
                                     {'name': 'Auth_comp_ID_1', 'type': 'str', 'mandatory': False},
                                     {'name': 'Auth_atom_ID_1', 'type': 'str', 'mandatory': False},
                                     {'name': 'Auth_ambiguity_code_1', 'type': 'enum-int', 'mandatory': False,
                                      'enum': ALLOWED_AMBIGUITY_CODES,
                                      'enforce-enum': True},
                                     {'name': 'Position_2', 'type': 'float', 'mandatory': True},
                                     {'name': 'Position_uncertainty_2', 'type': 'float', 'mandatory': False},
                                     {'name': 'Line_width_2', 'type': 'float', 'mandatory': False},
                                     {'name': 'Line_width_uncertainty_2', 'type': 'float', 'mandatory': False},
                                     {'name': 'Entity_assembly_ID_2', 'type': 'positive-int-as-str', 'mandatory': False},
                                     {'name': 'Entity_ID_2', 'type': 'positive-int'},
                                     {'name': 'Comp_index_ID_2', 'type': 'int', 'mandatory': False},
                                     {'name': 'Comp_ID_2', 'type': 'str', 'mandatory': False, 'uppercase': True},
                                     {'name': 'Atom_ID_2', 'type': 'str', 'mandatory': False},
                                     {'name': 'Ambiguity_code_2', 'type': 'enum-int', 'mandatory': False,
                                      'enum': ALLOWED_AMBIGUITY_CODES},
                                     {'name': 'Ambiguity_set_ID_2', 'type': 'positive-int', 'mandatory': False},
                                     {'name': 'Auth_asym_ID_2', 'type': 'str', 'mandatory': False},
                                     {'name': 'Auth_seq_ID_2', 'type': 'int', 'mandatory': False},
                                     {'name': 'Auth_comp_ID_2', 'type': 'str', 'mandatory': False},
                                     {'name': 'Auth_atom_ID_2', 'type': 'str', 'mandatory': False},
                                     {'name': 'Auth_ambiguity_code_2', 'type': 'enum-int', 'mandatory': False,
                                      'enum': ALLOWED_AMBIGUITY_CODES,
                                      'enforce-enum': True},
                                     {'name': 'Volume', 'type': 'float', 'mandatory': False},
                                     {'name': 'Volume_uncertainty', 'type': 'float', 'mandatory': False},
                                     {'name': 'Height', 'type': 'float', 'mandatory': False},
                                     {'name': 'Height_uncertainty', 'type': 'float', 'mandatory': False},
                                     {'name': 'Figure_of_merit', 'type': 'range-float', 'mandatory': False,
                                      'range': WEIGHT_RANGE},
                                     {'name': 'Details', 'type': 'str', 'mandatory': False},
                                     {'name': 'Spectral_peak_list_ID', 'type': 'pointer-index', 'mandatory': True,
                                      'default': '1', 'default-from': 'parent'},
                                     {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                     ],
                          'peak3d': [{'name': 'Index_ID', 'type': 'index-int', 'mandatory': False},
                                     {'name': 'Position_1', 'type': 'float', 'mandatory': True},
                                     {'name': 'Position_uncertainty_1', 'type': 'float', 'mandatory': False},
                                     {'name': 'Line_width_1', 'type': 'float', 'mandatory': False},
                                     {'name': 'Line_width_uncertainty_1', 'type': 'float', 'mandatory': False},
                                     {'name': 'Entity_assembly_ID_1', 'type': 'positive-int-as-str', 'mandatory': False},
                                     {'name': 'Entity_ID_1', 'type': 'positive-int'},
                                     {'name': 'Comp_index_ID_1', 'type': 'int', 'mandatory': False},
                                     {'name': 'Comp_ID_1', 'type': 'str', 'mandatory': False, 'uppercase': True},
                                     {'name': 'Atom_ID_1', 'type': 'str', 'mandatory': False},
                                     {'name': 'Ambiguity_code_1', 'type': 'enum-int', 'mandatory': False,
                                      'enum': ALLOWED_AMBIGUITY_CODES},
                                     {'name': 'Ambiguity_set_ID_1', 'type': 'positive-int', 'mandatory': False},
                                     {'name': 'Auth_asym_ID_1', 'type': 'str', 'mandatory': False},
                                     {'name': 'Auth_seq_ID_1', 'type': 'int', 'mandatory': False},
                                     {'name': 'Auth_comp_ID_1', 'type': 'str', 'mandatory': False},
                                     {'name': 'Auth_atom_ID_1', 'type': 'str', 'mandatory': False},
                                     {'name': 'Auth_ambiguity_code_1', 'type': 'enum-int', 'mandatory': False,
                                      'enum': ALLOWED_AMBIGUITY_CODES,
                                      'enforce-enum': True},
                                     {'name': 'Position_2', 'type': 'float', 'mandatory': True},
                                     {'name': 'Position_uncertainty_2', 'type': 'float', 'mandatory': False},
                                     {'name': 'Line_width_2', 'type': 'float', 'mandatory': False},
                                     {'name': 'Line_width_uncertainty_2', 'type': 'float', 'mandatory': False},
                                     {'name': 'Entity_assembly_ID_2', 'type': 'positive-int-as-str', 'mandatory': False},
                                     {'name': 'Entity_ID_2', 'type': 'positive-int'},
                                     {'name': 'Comp_index_ID_2', 'type': 'int', 'mandatory': False},
                                     {'name': 'Comp_ID_2', 'type': 'str', 'mandatory': False, 'uppercase': True},
                                     {'name': 'Atom_ID_2', 'type': 'str', 'mandatory': False},
                                     {'name': 'Ambiguity_code_2', 'type': 'enum-int', 'mandatory': False,
                                      'enum': ALLOWED_AMBIGUITY_CODES},
                                     {'name': 'Ambiguity_set_ID_2', 'type': 'positive-int', 'mandatory': False},
                                     {'name': 'Auth_asym_ID_2', 'type': 'str', 'mandatory': False},
                                     {'name': 'Auth_seq_ID_2', 'type': 'int', 'mandatory': False},
                                     {'name': 'Auth_comp_ID_2', 'type': 'str', 'mandatory': False},
                                     {'name': 'Auth_atom_ID_2', 'type': 'str', 'mandatory': False},
                                     {'name': 'Auth_ambiguity_code_2', 'type': 'enum-int', 'mandatory': False,
                                      'enum': ALLOWED_AMBIGUITY_CODES,
                                      'enforce-enum': True},
                                     {'name': 'Position_3', 'type': 'float', 'mandatory': True},
                                     {'name': 'Position_uncertainty_3', 'type': 'float', 'mandatory': False},
                                     {'name': 'Line_width_3', 'type': 'float', 'mandatory': False},
                                     {'name': 'Line_width_uncertainty_3', 'type': 'float', 'mandatory': False},
                                     {'name': 'Entity_assembly_ID_3', 'type': 'positive-int-as-str', 'mandatory': False},
                                     {'name': 'Entity_ID_3', 'type': 'positive-int'},
                                     {'name': 'Comp_index_ID_3', 'type': 'int', 'mandatory': False},
                                     {'name': 'Comp_ID_3', 'type': 'str', 'mandatory': False, 'uppercase': True},
                                     {'name': 'Atom_ID_3', 'type': 'str', 'mandatory': False},
                                     {'name': 'Ambiguity_code_3', 'type': 'enum-int', 'mandatory': False,
                                      'enum': ALLOWED_AMBIGUITY_CODES},
                                     {'name': 'Ambiguity_set_ID_3', 'type': 'positive-int', 'mandatory': False},
                                     {'name': 'Auth_asym_ID_3', 'type': 'str', 'mandatory': False},
                                     {'name': 'Auth_seq_ID_3', 'type': 'int', 'mandatory': False},
                                     {'name': 'Auth_comp_ID_3', 'type': 'str', 'mandatory': False},
                                     {'name': 'Auth_atom_ID_3', 'type': 'str', 'mandatory': False},
                                     {'name': 'Auth_ambiguity_code_3', 'type': 'enum-int', 'mandatory': False,
                                      'enum': ALLOWED_AMBIGUITY_CODES,
                                      'enforce-enum': True},
                                     {'name': 'Volume', 'type': 'float', 'mandatory': False},
                                     {'name': 'Volume_uncertainty', 'type': 'float', 'mandatory': False},
                                     {'name': 'Height', 'type': 'float', 'mandatory': False},
                                     {'name': 'Height_uncertainty', 'type': 'float', 'mandatory': False},
                                     {'name': 'Figure_of_merit', 'type': 'range-float', 'mandatory': False,
                                      'range': WEIGHT_RANGE},
                                     {'name': 'Details', 'type': 'str', 'mandatory': False},
                                     {'name': 'Spectral_peak_list_ID', 'type': 'pointer-index', 'mandatory': True,
                                      'default': '1', 'default-from': 'parent'},
                                     {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                     ],
                          'peak4d': [{'name': 'Index_ID', 'type': 'index-int', 'mandatory': False},
                                     {'name': 'Position_1', 'type': 'float', 'mandatory': True},
                                     {'name': 'Position_uncertainty_1', 'type': 'float', 'mandatory': False},
                                     {'name': 'Line_width_1', 'type': 'float', 'mandatory': False},
                                     {'name': 'Line_width_uncertainty_1', 'type': 'float', 'mandatory': False},
                                     {'name': 'Entity_assembly_ID_1', 'type': 'positive-int-as-str', 'mandatory': False},
                                     {'name': 'Entity_ID_1', 'type': 'positive-int'},
                                     {'name': 'Comp_index_ID_1', 'type': 'int', 'mandatory': False},
                                     {'name': 'Comp_ID_1', 'type': 'str', 'mandatory': False, 'uppercase': True},
                                     {'name': 'Atom_ID_1', 'type': 'str', 'mandatory': False},
                                     {'name': 'Ambiguity_code_1', 'type': 'enum-int', 'mandatory': False,
                                      'enum': ALLOWED_AMBIGUITY_CODES},
                                     {'name': 'Ambiguity_set_ID_1', 'type': 'positive-int', 'mandatory': False},
                                     {'name': 'Auth_asym_ID_1', 'type': 'str', 'mandatory': False},
                                     {'name': 'Auth_seq_ID_1', 'type': 'int', 'mandatory': False},
                                     {'name': 'Auth_comp_ID_1', 'type': 'str', 'mandatory': False},
                                     {'name': 'Auth_atom_ID_1', 'type': 'str', 'mandatory': False},
                                     {'name': 'Auth_ambiguity_code_1', 'type': 'enum-int', 'mandatory': False,
                                      'enum': ALLOWED_AMBIGUITY_CODES,
                                      'enforce-enum': True},
                                     {'name': 'Position_2', 'type': 'float', 'mandatory': True},
                                     {'name': 'Position_uncertainty_2', 'type': 'float', 'mandatory': False},
                                     {'name': 'Line_width_2', 'type': 'float', 'mandatory': False},
                                     {'name': 'Line_width_uncertainty_2', 'type': 'float', 'mandatory': False},
                                     {'name': 'Entity_assembly_ID_2', 'type': 'positive-int-as-str', 'mandatory': False},
                                     {'name': 'Entity_ID_2', 'type': 'positive-int'},
                                     {'name': 'Comp_index_ID_2', 'type': 'int', 'mandatory': False},
                                     {'name': 'Comp_ID_2', 'type': 'str', 'mandatory': False, 'uppercase': True},
                                     {'name': 'Atom_ID_2', 'type': 'str', 'mandatory': False},
                                     {'name': 'Ambiguity_code_2', 'type': 'enum-int', 'mandatory': False,
                                      'enum': ALLOWED_AMBIGUITY_CODES},
                                     {'name': 'Ambiguity_set_ID_2', 'type': 'positive-int', 'mandatory': False},
                                     {'name': 'Auth_asym_ID_2', 'type': 'str', 'mandatory': False},
                                     {'name': 'Auth_seq_ID_2', 'type': 'int', 'mandatory': False},
                                     {'name': 'Auth_comp_ID_2', 'type': 'str', 'mandatory': False},
                                     {'name': 'Auth_atom_ID_2', 'type': 'str', 'mandatory': False},
                                     {'name': 'Auth_ambiguity_code_2', 'type': 'enum-int', 'mandatory': False,
                                      'enum': ALLOWED_AMBIGUITY_CODES,
                                      'enforce-enum': True},
                                     {'name': 'Position_3', 'type': 'float', 'mandatory': True},
                                     {'name': 'Position_uncertainty_3', 'type': 'float', 'mandatory': False},
                                     {'name': 'Line_width_3', 'type': 'float', 'mandatory': False},
                                     {'name': 'Line_width_uncertainty_3', 'type': 'float', 'mandatory': False},
                                     {'name': 'Entity_assembly_ID_3', 'type': 'positive-int-as-str', 'mandatory': False},
                                     {'name': 'Entity_ID_3', 'type': 'positive-int'},
                                     {'name': 'Comp_index_ID_3', 'type': 'int', 'mandatory': False},
                                     {'name': 'Comp_ID_3', 'type': 'str', 'mandatory': False, 'uppercase': True},
                                     {'name': 'Atom_ID_3', 'type': 'str', 'mandatory': False},
                                     {'name': 'Ambiguity_code_3', 'type': 'enum-int', 'mandatory': False,
                                      'enum': ALLOWED_AMBIGUITY_CODES},
                                     {'name': 'Ambiguity_set_ID_3', 'type': 'positive-int', 'mandatory': False},
                                     {'name': 'Auth_asym_ID_3', 'type': 'str', 'mandatory': False},
                                     {'name': 'Auth_seq_ID_3', 'type': 'int', 'mandatory': False},
                                     {'name': 'Auth_comp_ID_3', 'type': 'str', 'mandatory': False},
                                     {'name': 'Auth_atom_ID_3', 'type': 'str', 'mandatory': False},
                                     {'name': 'Auth_ambiguity_code_3', 'type': 'enum-int', 'mandatory': False,
                                      'enum': ALLOWED_AMBIGUITY_CODES,
                                      'enforce-enum': True},
                                     {'name': 'Position_4', 'type': 'float', 'mandatory': True},
                                     {'name': 'Position_uncertainty_4', 'type': 'float', 'mandatory': False},
                                     {'name': 'Line_width_4', 'type': 'float', 'mandatory': False},
                                     {'name': 'Line_width_uncertainty_4', 'type': 'float', 'mandatory': False},
                                     {'name': 'Entity_assembly_ID_4', 'type': 'positive-int-as-str', 'mandatory': False},
                                     {'name': 'Entity_ID_4', 'type': 'positive-int'},
                                     {'name': 'Comp_index_ID_4', 'type': 'int', 'mandatory': False},
                                     {'name': 'Comp_ID_4', 'type': 'str', 'mandatory': False, 'uppercase': True},
                                     {'name': 'Atom_ID_4', 'type': 'str', 'mandatory': False},
                                     {'name': 'Ambiguity_code_4', 'type': 'enum-int', 'mandatory': False,
                                      'enum': ALLOWED_AMBIGUITY_CODES},
                                     {'name': 'Ambiguity_set_ID_4', 'type': 'positive-int', 'mandatory': False},
                                     {'name': 'Auth_asym_ID_4', 'type': 'str', 'mandatory': False},
                                     {'name': 'Auth_seq_ID_4', 'type': 'int', 'mandatory': False},
                                     {'name': 'Auth_comp_ID_4', 'type': 'str', 'mandatory': False},
                                     {'name': 'Auth_atom_ID_4', 'type': 'str', 'mandatory': False},
                                     {'name': 'Auth_ambiguity_code_4', 'type': 'enum-int', 'mandatory': False,
                                      'enum': ALLOWED_AMBIGUITY_CODES,
                                      'enforce-enum': True},
                                     {'name': 'Volume', 'type': 'float', 'mandatory': False},
                                     {'name': 'Volume_uncertainty', 'type': 'float', 'mandatory': False},
                                     {'name': 'Height', 'type': 'float', 'mandatory': False},
                                     {'name': 'Height_uncertainty', 'type': 'float', 'mandatory': False},
                                     {'name': 'Figure_of_merit', 'type': 'range-float', 'mandatory': False,
                                      'range': WEIGHT_RANGE},
                                     {'name': 'Details', 'type': 'str', 'mandatory': False},
                                     {'name': 'Spectral_peak_list_ID', 'type': 'pointer-index', 'mandatory': True,
                                      'default': '1', 'default-from': 'parent'},
                                     {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                     ],
                          'chem_shift': [{'name': 'Atom_type', 'type': 'enum', 'mandatory': True, 'default-from': 'Atom_ID',
                                          'enum': set(ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS.keys()),
                                          'enforce-enum': True},
                                         {'name': 'Atom_isotope_number', 'type': 'enum-int', 'mandatory': True, 'default-from': 'Atom_ID',
                                          'enum': set(ALLOWED_ISOTOPE_NUMBERS),
                                          'enforce-enum': True},
                                         {'name': 'Val', 'type': 'range-float', 'mandatory': True,
                                          'remove-bad-patter': True,
                                          'range': CS_RESTRAINT_RANGE},
                                         {'name': 'Val_err', 'type': 'range-float', 'mandatory': False, 'void-zero': True,
                                          'clear-bad-pattern': True,
                                          'range': CS_UNCERTAINTY_RANGE},
                                         {'name': 'Ambiguity_code', 'type': 'enum-int', 'mandatory': False,
                                          'enum': ALLOWED_AMBIGUITY_CODES,
                                          'enforce-enum': True},
                                         {'name': 'Ambiguity_set_ID', 'type': 'positive-int', 'mandatory': False,
                                          'enforce-non-zero': True},
                                         {'name': 'Seq_ID', 'type': 'int', 'mandatory': False},
                                         {'name': 'Auth_asym_ID', 'type': 'str', 'mandatory': False},
                                         {'name': 'Auth_seq_ID', 'type': 'int', 'mandatory': False},
                                         {'name': 'Auth_comp_ID', 'type': 'str', 'mandatory': False},
                                         {'name': 'Auth_atom_ID', 'type': 'str', 'mandatory': False},
                                         {'name': 'Details', 'type': 'str', 'mandatory': False},
                                         {'name': 'Assigned_chem_shift_list_ID', 'type': 'pointer-index', 'mandatory': True,
                                          'default': '1', 'default-from': 'parent'},
                                         {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                         ]
                          }

NMR_STAR_LP_DATA_ITEMS_INS_CODE = {'dist_restraint': copy.copy(NMR_STAR_LP_DATA_ITEMS['dist_restraint'][:-2]),
                                   'dihed_restraint': copy.copy(NMR_STAR_LP_DATA_ITEMS['dihed_restraint'][:-2]),
                                   'rdc_restraint': copy.copy(NMR_STAR_LP_DATA_ITEMS['rdc_restraint'][:-2])
                                   }

NMR_STAR_LP_DATA_ITEMS_INS_CODE['dist_restraint'].extend([{'name': 'PDB_ins_code_1', 'type': 'str', 'mandatory': False},
                                                          {'name': 'PDB_ins_code_2', 'type': 'str', 'mandatory': False},
                                                          {'name': 'Gen_dist_constraint_list_ID', 'type': 'pointer-index', 'mandatory': True,
                                                           'default': '1', 'default-from': 'parent'},
                                                          {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                                          ])

NMR_STAR_LP_DATA_ITEMS_INS_CODE['dihed_restraint'].extend([{'name': 'PDB_ins_code_1', 'type': 'str', 'mandatory': False},
                                                           {'name': 'PDB_ins_code_2', 'type': 'str', 'mandatory': False},
                                                           {'name': 'PDB_ins_code_3', 'type': 'str', 'mandatory': False},
                                                           {'name': 'PDB_ins_code_4', 'type': 'str', 'mandatory': False},
                                                           {'name': 'Torsion_angle_constraint_list_ID', 'type': 'pointer-index', 'mandatory': True,
                                                            'default': '1', 'default-from': 'parent'},
                                                           {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                                           ])

NMR_STAR_LP_DATA_ITEMS_INS_CODE['rdc_restraint'].extend([{'name': 'PDB_ins_code_1', 'type': 'str', 'mandatory': False},
                                                         {'name': 'PDB_ins_code_2', 'type': 'str', 'mandatory': False},
                                                         {'name': 'RDC_constraint_list_ID', 'type': 'pointer-index', 'mandatory': True, 'default': '1', 'default-from': 'parent'},
                                                         {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}
                                                         ])

NMR_STAR_ALT_LP_CATEGORIES = {'spectral_peak': ['_Peak', '_Peak_general_char', '_Peak_char', '_Assigned_peak_chem_shift']
                              }

NMR_STAR_ALT_LP_KEY_ITEMS = {'spectral_peak': {'_Peak': [
                                               {'name': 'ID', 'type': 'int'}],
                                               '_Peak_general_char': [
                                               {'name': 'Peak_ID', 'type': 'int'}],
                                               '_Peak_char': [
                                               {'name': 'Peak_ID', 'type': 'int'},
                                               {'name': 'Spectral_dim_ID', 'type': 'positive-int'}],
                                               '_Assigned_peak_chem_shift': [
                                               {'name': 'Peak_ID', 'type': 'int'},
                                               {'name': 'Spectral_dim_ID', 'type': 'positive-int'}]
                                               }
                             }

NMR_STAR_ALT_LP_DATA_ITEMS = {'spectral_peak': {'_Peak': [
                                                {'name': 'Index_ID', 'type': 'index-int', 'mandatory': False},
                                                {'name': 'Figure_of_merit', 'type': 'range-float', 'mandatory': False,
                                                 'range': WEIGHT_RANGE},
                                                {'name': 'Details', 'type': 'str', 'mandatory': False},
                                                {'name': 'Spectral_peak_list_ID', 'type': 'pointer-index', 'mandatory': True,
                                                 'default': '1', 'default-from': 'parent'},
                                                {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}],
                                                '_Peak_general_char': [
                                                {'name': 'Intensity_val', 'type': 'float', 'mandatory': True},
                                                {'name': 'Intensity_val_err', 'type': 'float', 'mandatory': False},
                                                {'name': 'Measurement_method', 'type': 'enum', 'mandatory': False,
                                                 'enum': ('absolute height', 'height', 'relative height', 'volume', 'number of contours', 'integration')},
                                                {'name': 'Spectral_peak_list_ID', 'type': 'pointer-index', 'mandatory': True,
                                                 'default': '1', 'default-from': 'parent'},
                                                {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}],
                                                '_Peak_char': [
                                                {'name': 'Chem_shift_val', 'type': 'range-float', 'mandatory': True,
                                                 'range': CS_RESTRAINT_RANGE},
                                                {'name': 'Chem_shift_val_err', 'type': 'range-float', 'mandatory': False, 'void-zero': True,
                                                 'range': CS_UNCERTAINTY_RANGE},
                                                {'name': 'Line_width_val', 'type': 'positive-float', 'mandatory': False},
                                                {'name': 'Line_width_val_err', 'type': 'positive-float', 'mandatory': False, 'void-zero': True},
                                                {'name': 'Coupling_pattern', 'type': 'enum', 'mandatory': False,
                                                 'enum': ('d', 'dd', 'ddd', 'dm', 'dt', 'hxt', 'hpt', 'm', 'q', 'qd', 'qn', 's', 'sxt', 't', 'td', 'LR', '1JCH')},
                                                {'name': 'Spectral_peak_list_ID', 'type': 'pointer-index', 'mandatory': True,
                                                 'default': '1', 'default-from': 'parent'},
                                                {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}],
                                                '_Assigned_peak_chem_shift': [
                                                {'name': 'Set_ID', 'type': 'positive-int', 'mandatory': False},
                                                {'name': 'Magnetization_linkage_ID', 'type': 'positive-int', 'mandatory': False},
                                                {'name': 'Val', 'type': 'range-float', 'mandatory': False,
                                                 'range': CS_RESTRAINT_RANGE},
                                                {'name': 'Contribution_fractional_val', 'type': 'range-float', 'mandatory': False,
                                                 'range': WEIGHT_RANGE},
                                                {'name': 'Figure_of_merit', 'type': 'range-float', 'mandatory': False,
                                                 'range': WEIGHT_RANGE},
                                                {'name': 'Assigned_chem_shift_list_ID', 'type': 'pointer-index', 'mandatory': False},
                                                {'name': 'Entity_assembly_ID', 'type': 'positive-int-as-str', 'mandatory': False},
                                                {'name': 'Entity_ID', 'type': 'positive-int'},
                                                {'name': 'Comp_index_ID', 'type': 'int', 'mandatory': False},
                                                {'name': 'Comp_ID', 'type': 'str', 'mandatory': False, 'uppercase': True},
                                                {'name': 'Atom_ID', 'type': 'str', 'mandatory': False},
                                                {'name': 'Ambiguity_code', 'type': 'enum-int', 'mandatory': False,
                                                 'enum': ALLOWED_AMBIGUITY_CODES},
                                                {'name': 'Ambiguity_set_ID', 'type': 'positive-int', 'mandatory': False},
                                                {'name': 'Auth_entity_ID', 'type': 'str', 'mandatory': False},  # NOTICE: '_Assigned_peak_chem_shift.Auth_asym_ID' does not exist
                                                {'name': 'Auth_seq_ID', 'type': 'int', 'mandatory': False},
                                                {'name': 'Auth_comp_ID', 'type': 'str', 'mandatory': False},
                                                {'name': 'Auth_atom_ID', 'type': 'str', 'mandatory': False},
                                                {'name': 'Details', 'type': 'str', 'mandatory': False},
                                                {'name': 'Spectral_peak_list_ID', 'type': 'pointer-index', 'mandatory': True,
                                                 'default': '1', 'default-from': 'parent'},
                                                {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}]}}

NMR_STAR_AUX_LP_CATEGORIES = {'dist_restraint': ['_Gen_dist_constraint_software_param'],
                              'spectral_peak': ['_Spectral_dim', '_Spectral_dim_transfer']
                              }

NMR_STAR_AUX_LP_KEY_ITEMS = {'dist_restraint': {'_Gen_dist_constraint_software_param': [
                                                {'name': 'Software_ID', 'type': 'int'},
                                                {'name': 'Type', 'type': 'str'}]
                                                },
                             'spectral_peak': {'_Spectral_dim': [
                                               {'name': 'ID', 'type': 'int', 'auto-increment': True}  # allows to have software-native id starting from zero
                                               ],
                                               '_Spectral_dim_transfer': [
                                               {'name': 'Spectral_dim_ID_1', 'type': 'positive-int'},
                                               {'name': 'Spectral_dim_ID_2', 'type': 'positive-int'}]
                                               }
                             }

NMR_STAR_AUX_LP_DATA_ITEMS = {'dist_restraint': {'_Gen_dist_constraint_software_param': [
                                                 {'name': 'Value', 'type': 'str', 'mandatory': False},
                                                 {'name': 'Range', 'type': 'str', 'mandatory': False},
                                                 {'name': 'Gen_dist_constraint_list_ID', 'type': 'pointer-index', 'mandatory': True,
                                                  'default': '1', 'default-from': 'parent'},
                                                 {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}]
                                                 },
                              'spectral_peak': {'_Spectral_dim': [
                                                {'name': 'Atom_type', 'type': 'enum', 'mandatory': True,
                                                 'enum': set(ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS.keys()),
                                                 'enforce-enum': True},
                                                {'name': 'Atom_isotope_number', 'type': 'enum-int', 'mandatory': True,
                                                 'enum': set(ALLOWED_ISOTOPE_NUMBERS),
                                                 'enforce-enum': True},
                                                {'name': 'Axis_code', 'type': 'str'},
                                                {'name': 'Spectrometer_frequency', 'type': 'positive-float', 'mandatory': False,
                                                 'enforce-non-zero': True},
                                                {'name': 'Under_sampling_type', 'type': 'enum', 'mandatory': False,
                                                 'enum': ('aliased', 'folded', 'not observed')},
                                                {'name': 'Spectral_region', 'type': 'str', 'mandatory': True},
                                                {'name': 'Sweep_width', 'type': 'positive-float', 'mandatory': False,
                                                 'enforce-non-zero': True},
                                                {'name': 'Sweep_width_units', 'type': 'enum', 'mandatory': True, 'default': 'Hz',
                                                 'enum': ('ppm', 'Hz'),
                                                 'enforce-enum': True},
                                                {'name': 'Value_first_point', 'type': 'float', 'mandatory': False},
                                                {'name': 'Absolute_peak_positions', 'type': 'bool', 'mandatory': False},
                                                {'name': 'Acquisition', 'type': 'bool', 'mandatory': False},
                                                {'name': 'Center_frequency_offset', 'type': 'float', 'mandatory': False},
                                                {'name': 'Spectral_peak_list_ID', 'type': 'pointer-index', 'mandatory': True,
                                                 'default': '1', 'default-from': 'parent'},
                                                {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}],
                                                '_Spectral_dim_transfer': [
                                                {'name': 'Type', 'type': 'enum', 'mandatory': True,
                                                 'enum': ('onebond', 'jcoupling', 'jmultibond', 'relayed', 'relayed-alternate',
                                                          'through-space', 'through-space?'),
                                                 'enforce-enum': True},
                                                {'name': 'Indirect', 'type': 'bool', 'mandatory': False},
                                                {'name': 'Spectral_peak_list_ID', 'type': 'pointer-index', 'mandatory': True,
                                                 'default': '1', 'default-from': 'parent'},
                                                {'name': 'Entry_ID', 'type': 'str', 'mandatory': True}]
                                                }
                              }

CARTN_DATA_ITEMS = [{'name': 'Cartn_x', 'type': 'float', 'alt_name': 'x'},
                    {'name': 'Cartn_y', 'type': 'float', 'alt_name': 'y'},
                    {'name': 'Cartn_z', 'type': 'float', 'alt_name': 'z'}
                    ]

AUTH_ATOM_DATA_ITEMS = [{'name': 'auth_asym_id', 'type': 'str', 'alt_name': 'chain_id'},
                        {'name': 'auth_seq_id', 'type': 'int', 'alt_name': 'seq_id'},
                        {'name': 'label_comp_id', 'type': 'starts-with-alnum', 'alt_name': 'comp_id'},
                        {'name': 'label_atom_id', 'type': 'starts-with-alnum', 'alt_name': 'atom_id'}
                        ]

ATOM_NAME_DATA_ITEMS = [{'name': 'label_comp_id', 'type': 'starts-with-alnum', 'alt_name': 'comp_id'},
                        {'name': 'label_atom_id', 'type': 'starts-with-alnum', 'alt_name': 'atom_id'}
                        ]

AUTH_ATOM_CARTN_DATA_ITEMS = CARTN_DATA_ITEMS
AUTH_ATOM_CARTN_DATA_ITEMS.extend(AUTH_ATOM_DATA_ITEMS)

PTNR1_AUTH_ATOM_DATA_ITEMS = [{'name': 'ptnr1_auth_asym_id', 'type': 'str', 'alt_name': 'chain_id'},
                              {'name': 'ptnr1_auth_seq_id', 'type': 'int', 'alt_name': 'seq_id'},
                              {'name': 'ptnr1_label_comp_id', 'type': 'starts-with-alnum', 'alt_name': 'comp_id'},
                              {'name': 'ptnr1_label_atom_id', 'type': 'starts-with-alnum', 'alt_name': 'atom_id'}
                              ]

PTNR2_AUTH_ATOM_DATA_ITEMS = [{'name': 'ptnr2_auth_asym_id', 'type': 'str', 'alt_name': 'chain_id'},
                              {'name': 'ptnr2_auth_seq_id', 'type': 'int', 'alt_name': 'seq_id'},
                              {'name': 'ptnr2_label_comp_id', 'type': 'starts-with-alnum', 'alt_name': 'comp_id'},
                              {'name': 'ptnr2_label_atom_id', 'type': 'starts-with-alnum', 'alt_name': 'atom_id'}
                              ]

REMEDIATE_BACKBONE_ANGLE_NAME_PAT = re.compile(r'pseudo (PHI|PSI|OMEGA) \(0, (0|1|\-1), (0|1|\-1), 0\)')

SPECTRAL_DIM_TEMPLATE = {'axis_code': None,
                         'spectrometer_frequency': None,
                         'under_sampling_type': None,
                         'atom_type': None,
                         'atom_isotope_number': None,
                         'spectral_region': None,
                         # 'magnetization_linkage_id': None,  not required for _Peak_row_format loop
                         'sweep_width': None,
                         'sweep_width_units': 'Hz',
                         'value_first_point': None,
                         'absolute_peak_positions': None,
                         'acquisition': None,
                         'center_frequency_offset': None,
                         # 'encoding_code': None,  not required for _Peak_row_format loop
                         # 'encoded_reduced_dimension_id': None  not required for _Peak_row_format loop
                         }


def toRegEx(string: str) -> str:
    """ Return regular expression for a given string including XPLOR-NIH wildcard format.
    """

    if '*' in string:  # any string
        return string.replace('*', '.*')
    if '%' in string:  # a single character
        return string.replace('%', '.')
    if '#' in string:  # any number
        return string.replace('#', '[+-]?[0-9\\.]*')
    if '+' in string:  # any digit
        return string.replace('+', '[0-9]*')
    return string


def toNefEx(string: str) -> str:
    """ Return NEF regular expression for a given string including XPLOR-NIH wildcard format.
    """

    if '*' in string:  # any string
        return re.sub(r'\*\*', '*', string)
    if '%' in string:  # a single character
        return re.sub(r'\*\*', '*', string.replace('%', '*'))
    if '#' in string:  # any number
        return re.sub(r'\*\*', '*', string.replace('#', '*'))
    if '+' in string:  # any digit
        return re.sub(r'\%\%', '%', string.replace('+', '%'))
    return string


def stripQuot(string: str) -> str:
    """ Return strippped string by removing single/double quotation marks.
    """

    _string = string.strip()

    while True:
        if (_string[0] == '\'' and _string[-1] == '\'')\
           or (_string[0] == '"' and _string[-1] == '"'):
            _string = _string[1:len(_string) - 1].strip()
        else:
            break

    return _string


def translateToStdAtomName(atomId: str, refCompId: Optional[str] = None,
                           refAtomIdList: Optional[List[str]] = None,
                           ccU=None, unambig: bool = False) -> str:
    """ Translate software specific atom nomenclature for standard residues to the CCD one.
    """

    atomId = atomId.upper()
    lenAtomId = len(atomId)
    lenRefCompId = 0 if refCompId is None else len(refCompId)

    if refAtomIdList is not None:
        if atomId in refAtomIdList:
            return atomId

    if None not in (refCompId, ccU):
        refCompId = translateToStdResName(refCompId, ccU=ccU)
        if ccU.updateChemCompDict(refCompId):
            if refAtomIdList is not None:
                if atomId in refAtomIdList:
                    return atomId
            _refAtomIdList = [cca[ccU.ccaAtomId] for cca in ccU.lastAtomList]
            if "'" not in atomId and atomId in _refAtomIdList:
                return atomId
            # DNA/RNA OH 5/3 prime terminus
            if atomId.startswith("H1'"):
                if refAtomIdList is not None:
                    if atomId == "H1''" and "H1'A" in refAtomIdList:  # 4DG
                        return "H1'A"
                    if atomId == "H1''" and "H1'" in refAtomIdList:
                        return "H1'"
                if atomId == "H1''" and "H1'A" in _refAtomIdList:  # 4DG
                    return "H1'A"
                if atomId == "H1''" and "H1'" in _refAtomIdList:
                    return "H1'"
            elif atomId.startswith("H2'"):
                if refAtomIdList is not None:
                    if atomId == "H2'" and "H2'1" in refAtomIdList:  # DCZ, THM
                        return "H2'1"
                    if atomId == "H2''" and "H2'2" in refAtomIdList:  # DCZ, THM
                        return "H2'2"
                    if atomId == "H2''" and "HO2'" in refAtomIdList:  # 5MC (DAOTHER-9317)
                        return "HO2'"
                    if atomId == "H2''" and "H2'" in refAtomIdList:
                        return "H2'"
                    if atomId == "H2''''" and "H2''" in refAtomIdList:
                        return "H2''"
                    if atomId == "H2''''" and "H2'2" in refAtomIdList:  # DCZ, THM
                        return "H2'2"
                    if atomId == "H2''''" and "HO2'" in refAtomIdList:  # 5MC (DAOTHER-9317)
                        return "HO2'"
                    if atomId == "H2''1" and "H2'1" in refAtomIdList:  # 4EN
                        return "H2'1"
                    if atomId == "H2''2" and "H2'2" in refAtomIdList:  # 4EN
                        return "H2'2"
                    if atomId == "H2''1" and "H2'" in refAtomIdList:
                        return "H2'"
                    if atomId == "H2''2" and "H2''" in refAtomIdList:
                        return "H2''"
                if atomId == "H2'" and "H2'1" in _refAtomIdList:  # DCZ, THM
                    return "H2'1"
                if atomId == "H2''" and "H2'2" in _refAtomIdList:  # DCZ, THM
                    return "H2'2"
                if atomId == "H2''" and "HO2'" in _refAtomIdList:  # 5MC (DAOTHER-9317)
                    return "HO2'"
                if atomId == "H2''" and "H2'" in _refAtomIdList:
                    return "H2'"
                if atomId == "H2''''" and "H2''" in _refAtomIdList:
                    return "H2''"
                if atomId == "H2''''" and "H2'2" in _refAtomIdList:  # DCZ, THM
                    return "H2'2"
                if atomId == "H2''" and "H2'2" in _refAtomIdList:  # DCZ, THM
                    return "H2'2"
                if atomId == "H2''1" and "H2'1" in _refAtomIdList:  # 4EN
                    return "H2'1"
                if atomId == "H2''2" and "H2'2" in _refAtomIdList:  # 4EN
                    return "H2'2"
                if atomId == "H2''1" and "H2'" in _refAtomIdList:
                    return "H2'"
                if atomId == "H2''2" and "H2''" in _refAtomIdList:
                    return "H2''"
            elif atomId.startswith("H3'"):
                if refAtomIdList is not None:
                    if atomId == "H3''" and "H3'A" in refAtomIdList:
                        return "H3'A"
                    if atomId == "H3''" and "H3'" in refAtomIdList:
                        return "H3'"
                if atomId == "H3''" and "H3'A" in _refAtomIdList:
                    return "H3'A"
                if atomId == "H3''" and "H3'" in _refAtomIdList:
                    return "H3'"
            elif atomId.startswith("H4'"):
                if refAtomIdList is not None:
                    if atomId == "H4''" and "H4'A" in refAtomIdList:  # 4DG
                        return "H4'A"
                    if atomId == "H4''" and "H4'" in refAtomIdList:
                        return "H4'"
                if atomId == "H4''" and "H4'A" in _refAtomIdList:  # 4DG
                    return "H4'A"
                if atomId == "H4''" and "H4'" in _refAtomIdList:
                    return "H4'"
            elif atomId.startswith("H5'"):
                if refAtomIdList is not None:
                    if atomId == "H5'" and "H5'1" in refAtomIdList:  # DCZ, THM
                        return "H5'1"
                    if atomId == "H5''" and "H5'2" in refAtomIdList:  # DCZ, THM
                        return "H5'2"
                    if atomId == "H5''''" and "H5''" in refAtomIdList:
                        return "H5''"
                    if atomId == "H5''''" and "H5'2" in refAtomIdList:  # DCZ, THM
                        return "H5'2"
                    if atomId == "H5''" and "H5'A" in refAtomIdList:  # 4DG, 23G
                        return "H5'A"
                    if atomId == "H5''1" and "H5'1" in refAtomIdList:  # 4EN
                        return "H5'1"
                    if atomId == "H5''2" and "H5'2" in refAtomIdList:  # 4EN
                        return "H5'2"
                    if atomId == "H5''1" and "H5'" in refAtomIdList:
                        return "H5'"
                    if atomId == "H5''2" and "H5''" in refAtomIdList:
                        return "H5''"
                if atomId == "H5'" and "H5'1" in _refAtomIdList:  # DCZ, THM
                    return "H5'1"
                if atomId == "H5''" and "H5'2" in _refAtomIdList:  # DCZ, THM
                    return "H5'2"
                if atomId == "H5''''" and "H5''" in _refAtomIdList:
                    return "H5''"
                if atomId == "H5''''" and "H5'2" in _refAtomIdList:  # DCZ, THM
                    return "H5'2"
                if atomId == "H5''" and "H5'A" in _refAtomIdList:  # 4DG, 23G
                    return "H5'A"
                if atomId == "H5''1" and "H5'1" in _refAtomIdList:  # 4EN
                    return "H5'1"
                if atomId == "H5''2" and "H5'2" in _refAtomIdList:  # 4EN
                    return "H5'2"
                if atomId == "H5''1" and "H5'" in _refAtomIdList:
                    return "H5'"
                if atomId == "H5''2" and "H5''" in _refAtomIdList:
                    return "H5''"
            elif atomId == 'H2"':  # 6dm7
                if refAtomIdList is not None:
                    if "H2''" in refAtomIdList:
                        return "H2''"
                    if "H2'2" in refAtomIdList:
                        return "H2'2"
            elif atomId == 'H5"':
                if refAtomIdList is not None:
                    if "H5''" in refAtomIdList:
                        return "H5''"
                    if "H5'2" in refAtomIdList:
                        return "H5'2"
                    if "H5'A" in refAtomIdList:
                        return "H5'A"

            if atomId.startswith('NH'):
                if atomId[1:] in _refAtomIdList:
                    return atomId[1:]

            if atomId in _refAtomIdList:
                return atomId

            peptide, _, carbohydrate = ccU.getTypeOfCompId(refCompId)

            if peptide and atomId in aminoProtonCode and refAtomIdList is not None:
                if atomId[-1] in ('%', '*', '#') and not unambig:
                    for _atomId in aminoProtonCode:
                        if _atomId in refAtomIdList:
                            return _atomId + '%'
                else:
                    for _atomId in aminoProtonCode:
                        if _atomId in refAtomIdList:
                            return _atomId

            if carbohydrate and lenAtomId > 2 and atomId[0] in ('1', '2', '3') and atomId[1] == 'H' and refAtomIdList is not None:
                if atomId[1:] + atomId[0] in refAtomIdList:
                    return atomId[1:] + atomId[0]  # 2yhh: MAN:(1|2)H6 -> H6(1|2)

            if atomId.startswith('M') or atomId.startswith('HM') or atomId.startswith('QM'):  # methyl group
                if refAtomIdList is not None:
                    if 'H' + atomId[1:] + '1' in refAtomIdList:
                        return 'H' + atomId[1:]
                if 'H' + atomId[1:] + '1' in _refAtomIdList:
                    return 'H' + atomId[1:]
                candidates = ccU.getRepMethylProtons(refCompId)
                if len(candidates) == 1:
                    atomId = candidates[0]
                    return atomId[:-1] if atomId.endswith('1') else atomId
            elif refCompId in ('DT', 'T') and atomId.startswith('Q5'):
                return 'H7'
            elif refCompId in ('DT', 'T') and atomId.startswith('H5') and "'" not in atomId:  # 2lsz
                if atomId in ('H51', 'H52', 'H53'):
                    return 'H7' + atomId[-1]
                if atomId in ('H5', 'H5%', 'H5*', 'H5#'):
                    return 'H7'
            elif refCompId in ('DT', 'T') and (atomId.startswith('C5') or atomId == 'CM'):  # 7dju, 7pdu
                return 'C7'
            elif refCompId == 'THM' and refAtomIdList is not None and 'HM51' in refAtomIdList:
                if atomId.startswith('Q7'):
                    return 'HM5'
                if atomId.startswith('H7'):
                    if atomId in ('H71', 'H72', 'H73'):
                        return 'HM5' + atomId[-1]
                    if atomId in ('H7', 'H7%', 'H7*', 'H7#'):
                        return 'HM5'
                if atomId in ('C7', 'CM'):  # 7png, 7pdu
                    return 'C5M'
            elif refCompId in ('DA', 'A') and atomId[0] == 'H' and lenAtomId == 3 and atomId[1].isdigit()\
                    and atomId[1] != '5' and atomId[-1] in ('1', '2'):  # 2lgm exclude H5 for segment identifier via DT:H5
                return 'H6' + atomId[-1]
            elif refCompId in ('DG', 'G') and atomId[0] == 'H' and lenAtomId == 3 and atomId[1].isdigit()\
                    and atomId[1] != '5' and atomId[-1] in ('1', '2'):  # 6g99, 2lgm exclude H5 fir segment identifier via DT:H5
                return 'H2' + atomId[-1]
            elif refCompId in ('DC', 'C') and atomId[0] == 'H' and lenAtomId == 3 and atomId[1].isdigit() and atomId[-1] in ('1', '2'):
                return 'H4' + atomId[-1]
            elif refCompId == 'U' and atomId[0] == 'H' and lenAtomId == 3 and atomId[1].isdigit() and atomId[-1] == '1':  # 6g99
                return 'H3'
            elif refAtomIdList is not None and ((atomId[0] + 'N' + atomId[1:] in refAtomIdList) or (atomId[0] + 'N' + atomId[1:] + '1' in refAtomIdList)):  # 5CM
                return atomId[0] + 'N' + atomId[1:]
            elif (atomId[0] + 'N' + atomId[1:] in _refAtomIdList) or (atomId[0] + 'N' + atomId[1:] + '1' in _refAtomIdList):  # 5CM
                return atomId[0] + 'N' + atomId[1:]
            elif refAtomIdList is not None and atomId[0].endswith('2') and (atomId[0:-1] + 'A') in refAtomIdList:
                return atomId[0:-1] + 'A'
            elif atomId[0].endswith('2') and (atomId[0:-1] + 'A') in _refAtomIdList:
                return atomId[0:-1] + 'A'
            elif refAtomIdList is not None and atomId[0].endswith('3') and (atomId[0:-1] + 'B') in refAtomIdList:
                return atomId[0:-1] + 'B'
            elif atomId[0].endswith('3') and (atomId[0:-1] + 'B') in _refAtomIdList:
                return atomId[0:-1] + 'B'
            elif atomId.startswith('1H'):
                if refAtomIdList is not None:
                    if atomId[1:] + '1' in refAtomIdList:
                        return atomId[1:] + '1'
                    if atomId[1:].endswith("'") and atomId[1:-1] + "1'" in refAtomIdList:
                        return atomId[1:-1] + "1'"
                if atomId[1:] + '1' in _refAtomIdList:
                    return atomId[1:] + '1'
                if atomId[1:].endswith("'") and atomId[1:-1] + "1'" in _refAtomIdList:
                    return atomId[1:-1] + "1'"
            elif atomId.startswith('2H'):
                if refAtomIdList is not None:
                    if atomId[1:] + '2' in refAtomIdList:
                        return atomId[1:] + '2'
                    if atomId[1:].endswith("'") and atomId[1:-1] + "2'" in refAtomIdList:
                        return atomId[1:-1] + "2'"
                if atomId[1:] + '2' in _refAtomIdList:
                    return atomId[1:] + '2'
                if atomId[1:].endswith("'") and atomId[1:-1] + "2'" in _refAtomIdList:
                    return atomId[1:-1] + "2'"
            elif atomId.startswith('3H'):
                if refAtomIdList is not None:
                    if atomId[1:] + '3' in refAtomIdList:
                        return atomId[1:] + '3'
                    if atomId[1:].endswith("'") and atomId[1:-1] + "3'" in refAtomIdList:
                        return atomId[1:-1] + "3'"
                if atomId[1:] + '3' in _refAtomIdList:
                    return atomId[1:] + '3'
                if atomId[1:].endswith("'") and atomId[1:-1] + "3'" in _refAtomIdList:
                    return atomId[1:-1] + "3'"
            elif atomId == "HX'":  # derived from 2mko AMBER RDC restraints
                if refAtomIdList is not None:
                    if "H4'" in refAtomIdList:
                        return "H4'"
                if "H4'" in _refAtomIdList:
                    return "H4'"
            if atomId[0] == 'R' and lenAtomId > 1:  # 2lkk
                _atomId = 'H' + atomId[1:]
                if _atomId in _refAtomIdList:
                    return _atomId
                if _atomId + '2' in _refAtomIdList and not unambig:
                    return _atomId + '%'

            if atomId[0] in ('N', 'O', 'P', 'S', 'F') and refAtomIdList is not None:
                candidates = [_atomId for _atomId in refAtomIdList if _atomId[0] == atomId[0]]
                if len(candidates) == 1:
                    return candidates[0]

            if lenRefCompId == 3 and refCompId in monDict3 and lenAtomId > 1:
                candidates = [_atomId for _atomId in _refAtomIdList if _atomId.startswith(atomId)]
                if len(candidates) == 1 and len(candidates[0]) == lenAtomId + 1 and candidates[0][-1].isdigit():
                    return candidates[0]

            if not unambig:

                # ambiguous atom generated by 'makeDIST_RST'
                if atomId[0] == 'Q':
                    if atomId.startswith('QP'):
                        if refAtomIdList is not None:
                            if 'H' + atomId[2:] + '2' in refAtomIdList:
                                return 'H' + atomId[2:] + '%'
                        if 'H' + atomId[2:] + '2' in _refAtomIdList:
                            return 'H' + atomId[2:] + '%'
                        if refCompId in monDict3:  # 2n9e
                            return 'H' + atomId[2:] + '%'
                    elif atomId in ('QCD', 'QCE') and isLikePheOrTyr(refCompId, ccU):  # 2js7 - peak list
                        return atomId[1:] + '%'
                    else:
                        if refAtomIdList is not None:
                            if 'H' + atomId[1:] + '2' in refAtomIdList:
                                return 'H' + atomId[1:] + '%'
                        if 'H' + atomId[1:] + '2' in _refAtomIdList:
                            return 'H' + atomId[1:] + '%'

                elif atomId[-1] in ('-', '+'):
                    if refAtomIdList is not None:
                        if atomId[:-1] + '2' in refAtomIdList:
                            return atomId[:-1] + '%'
                    if atomId[:-1] + '2' in _refAtomIdList:
                        return atomId[:-1] + '%'
                    if atomId[:-1] in _refAtomIdList:
                        return atomId[:-1]

                elif atomId[0] == 'M':
                    if atomId[-1] in ('X', 'Y'):
                        if refAtomIdList is not None:
                            if 'H' + atomId[1:-1] + '1' in refAtomIdList or 'H' + atomId[1:-1] + '11' in refAtomIdList:
                                return 'H' + atomId[1:-1] + '%'
                        if 'H' + atomId[1:-1] + '1' in _refAtomIdList or 'H' + atomId[1:-1] + '11' in _refAtomIdList:
                            return 'H' + atomId[1:-1] + '%'
                    elif refAtomIdList is not None and ('H' + atomId[1:] + '1' in refAtomIdList or 'H' + atomId[1:] + '11' in refAtomIdList):
                        return 'H' + atomId[1:] + '%'
                    elif 'H' + atomId[1:] + '1' in _refAtomIdList or 'H' + atomId[1:] + '11' in _refAtomIdList:
                        return 'H' + atomId[1:] + '%'

                elif atomId in ('HT', 'HT%', 'HT*', 'HT#'):  # 6e83
                    if refAtomIdList is not None and 'H1' in refAtomIdList:
                        return 'H%'

                elif refAtomIdList is not None and atomId + '2' in refAtomIdList:
                    return atomId + '%'

                elif atomId + '2' in _refAtomIdList:
                    return atomId + '%'

            else:

                if atomId[-1] in ('-', '+'):
                    if refAtomIdList is not None:
                        if atomId[:-1] + ('2' if atomId[-1] == '-' else '3') in refAtomIdList:
                            return atomId[:-1] + ('2' if atomId[-1] == '-' else '3')
                    if atomId[:-1] + ('2' if atomId[-1] == '-' else '3') in _refAtomIdList:
                        return atomId[:-1] + ('2' if atomId[-1] == '-' else '3')
                    if atomId[:-1] in _refAtomIdList:
                        return atomId[:-1]

    if refCompId is not None:

        # GROMACS atom nomenclature
        if refCompId == 'ILE':
            if atomId in ('HD1', 'HD2', 'HD3'):
                return 'HD1' + atomId[-1]
            if atomId == 'CD':
                return 'CD1'

        elif refCompId in ('SER', 'THR', 'TYR'):
            if refCompId == 'TYR' and atomId == 'HO':
                return 'HH'
            if atomId.startswith('HO') and lenAtomId > 2:  # 2n6j
                return 'H' + atomId[2:]

        elif refCompId == 'ASN' and (atomId.startswith('HND')
                                     or ((atomId.startswith('HN') or atomId.startswith('HG')) and atomId[-1] in ('%', '*', '#'))):  # 2kg1
            if atomId == 'HND1':
                return 'HD21'
            if atomId == 'HND2':
                return 'HD22'
            if atomId == 'HND' or ((atomId.startswith('HN') or atomId.startswith('HG')) and atomId[-1] in ('%', '*', '#')) and not unambig:  # 8dhz: ASN/HN#
                return 'HD2'

        elif refCompId == 'GLN' and (atomId.startswith('HNE')
                                     or ((atomId.startswith('HN') or atomId.startswith('HD')) and atomId[-1] in ('%', '*', '#'))):  # 2kg1
            if atomId == 'HNE1':
                return 'HE21'
            if atomId == 'HNE2':
                return 'HE22'
            if atomId == 'HNE' or ((atomId.startswith('HN') or atomId.startswith('HD')) and atomId[-1] in ('%', '*', '#')) and not unambig:
                return 'HE2'  # 5xdi

        elif refCompId == 'ARG' and atomId == 'HNE':  # 8dhz, peak list
            return 'HE'

        elif refCompId == 'ASP' and atomId.startswith('HD'):  # 6fe6
            return 'HD2'

        elif refCompId == 'GLU' and atomId.startswith('HE'):
            return 'HE2'

        elif refCompId in ('HIS', 'OUH'):
            if atomId == 'HNE':  # 2k4w
                return 'HE2'
            if atomId == 'HND':  # 5n14 OUH:HND
                return 'HD1'
            if atomId == 'HE':
                return 'HE1'
            if atomId == 'HD':
                return 'HD2'

        elif refCompId == 'NH2':
            if atomId in ('HN*', 'HN%', 'H*', 'H%', 'QH', 'QN', 'Q1') and not unambig:
                return 'HN%'
            if atomId[-1] not in ('%', '*', '#'):
                if atomId in ('H', 'HN'):
                    return 'HN1'
                if atomId.startswith('H'):
                    return 'HN2'

        elif refCompId == 'ACE':
            if atomId in ('HA', 'HA%', 'HA*', 'HA#', 'HA1', 'HA2', 'HA3', 'QH', 'MH', 'QA', 'MA') and not unambig:
                return 'H%'
            if atomId == 'CA':
                return 'CH3'

        elif refCompId == 'A2G' and atomId == 'HNA':
            return 'HN2'  # 2mk7

        elif refCompId == 'CGU':  # 2mzm
            if atomId.startswith('O1'):
                return 'OE' + atomId[1:]
            if atomId.startswith('O2'):
                return 'OE' + atomId[1:]

        elif refCompId in ('HEB', 'HEC', 'MH0'):
            is_mh0 = refCompId == 'MH0'  # 2n3y
            if atomId[0] in pseProBeginCode:
                if atomId == 'QM1':
                    return 'QMB' if is_mh0 else 'HMB'
                if atomId == 'QT2':
                    return 'QBB' if is_mh0 else 'HBB'
                if atomId.startswith('HT2') and is_mh0:
                    return 'QAB'
                if atomId.startswith('HT2') and refCompId == 'HEC':
                    return 'HAB'
                if atomId in ('HT2', 'HA2', 'HA21', 'HA22') and refCompId == 'HEB':
                    return 'HAB'
                if atomId == 'HA23' and refCompId == 'HEB':
                    return 'HAB2'
                if atomId == 'QM3':
                    return 'QMC' if is_mh0 else 'HMC'
                if atomId == 'QT4':
                    return 'HBC'
                if atomId.startswith('HT4'):
                    return 'QAC' if is_mh0 else 'HAC'
                if atomId == 'QM5':
                    return 'QMD' if is_mh0 else 'HMD'
                if atomId == 'HA62':
                    return 'HAD1'
                if atomId == 'HA63':
                    return 'HAD2'
                if atomId == 'HB62':
                    return 'HBD1'
                if atomId == 'HB63':
                    return 'HBD2'
                if atomId == 'HA71' and is_mh0:
                    return 'H8'
                if atomId == 'HA72' and is_mh0:
                    return 'H9'
                if atomId == 'HA72':
                    return 'HAA1'
                if atomId == 'HA73':
                    return 'HAA2'
                if atomId == 'HB73' and is_mh0:
                    return 'H10'
                if atomId == 'HB74' and is_mh0:
                    return 'H11'
                if atomId == 'HB2' and is_mh0:
                    return 'H16'
                if atomId == 'HB3' and is_mh0:
                    return 'H17'
                if atomId == 'HD1' and is_mh0:
                    return 'H32'
                if atomId == 'HD2' and is_mh0:
                    return 'H33'
                if atomId == 'HE1' and is_mh0:
                    return 'H34'
                if atomId == 'HE2' and is_mh0:
                    return 'H35'
                if atomId == 'HB72':
                    return 'HBA1'
                if atomId == 'HB73':
                    return 'HBA2'
                if atomId == 'HA6':
                    return 'HAD'
                if atomId == 'HB6':
                    return 'HBD'
                if atomId == 'HA7':
                    return 'HAA'
                if atomId == 'HB7':
                    return 'HBA'
                if atomId == 'QM8':
                    return 'QMA' if is_mh0 else 'HMA'
                if atomId == 'HAM':
                    return 'HHA'
                if atomId == 'HBM':
                    return 'HHB'
                if atomId in ('HGM', 'HCM'):
                    return 'HHC'
                if atomId == 'HDM':
                    return 'HHD'

        if refCompId in ('OUD', 'OUE', 'OUH', 'OUI', 'OUK', 'OUR'):  # 5n14
            if atomId == 'QPA':
                return 'HM'
            if atomId == 'QPG' and refCompId == 'OUI':
                return 'HG1'

        if lenRefCompId == 3 and refCompId in monDict3:
            if atomId in ('O1', 'OT1'):
                return 'O'
            if atomId == 'O2' or atomId.startswith('OT'):
                return 'OXT'
            if atomId.startswith('HT') and lenAtomId > 2:
                return 'H' + atomId[2:]
            if atomId == 'NH':  # 2jwu
                return 'N'
            if atomId.startswith('HQ'):  # 1e8e
                return atomId[1:]
            if refCompId in ('PHE', 'TYR'):  # 4ar0
                if atomId == 'HD3':
                    return 'HD1'
                if atomId == 'HE3':
                    return 'HE1'

        # BIOSYM atom nomenclature
        if (atomId[-1] in ('R', 'S', 'Z', 'E') or (lenAtomId > 2 and atomId[-2] in ('R', 'S'))):
            if refCompId in ('CYS', 'ASP', 'HIS', 'SER'):
                if atomId == 'HBR':
                    return 'HB3'
                if atomId == 'HBS':
                    return 'HB2'
            elif refCompId in ('GLU', 'PHE', 'TRP', 'TYR'):
                if atomId == 'HBR':
                    return 'HB2'
                if atomId == 'HBS':
                    return 'HB3'
                if atomId == 'HGR':
                    return 'HG3'
                if atomId == 'HGS':
                    return 'HG2'
            elif refCompId == 'GLY':
                if atomId == 'HAR':
                    return 'HA2'
                if atomId == 'HAS':
                    return 'HA3'
            elif refCompId == 'ILE':
                if atomId == 'HG1R':
                    return 'HG12'
                if atomId == 'HG1S':
                    return 'HG13'
            elif refCompId == 'LYS':
                if atomId == 'HBR':
                    return 'HB2'
                if atomId == 'HBS':
                    return 'HB3'
                if atomId == 'HGR':
                    return 'HG2'
                if atomId == 'HGS':
                    return 'HG3'
                if atomId == 'HDR':
                    return 'HD3'
                if atomId == 'HDS':
                    return 'HD2'
                if atomId == 'HER':
                    return 'HE3'
                if atomId == 'HES':
                    return 'HE2'
            elif refCompId == 'LEU':
                if atomId == 'HBR':
                    return 'HB2'
                if atomId == 'HBS':
                    return 'HB3'
                if atomId.startswith('HDR'):
                    return 'HD1'
                if atomId.startswith('HDS'):
                    return 'HD2'
                if atomId == 'CDR':
                    return 'CD1'
                if atomId == 'CDS':
                    return 'CD2'
            elif refCompId == 'MET':
                if atomId == 'HBR':
                    return 'HB3'
                if atomId == 'HBS':
                    return 'HB2'
                if atomId == 'HGR':
                    return 'HG3'
                if atomId == 'HGS':
                    return 'HG2'
            elif refCompId == 'ASN':
                if atomId == 'HBR':
                    return 'HB3'
                if atomId == 'HBS':
                    return 'HB2'
                if atomId == 'HD2Z':
                    return 'HD22'
                if atomId == 'HD2E':
                    return 'HD21'
            elif refCompId == 'PRO':
                if atomId == 'HBR':
                    return 'HB2'
                if atomId == 'HBS':
                    return 'HB3'
                if atomId == 'HGR':
                    return 'HG3'
                if atomId == 'HGS':
                    return 'HG2'
                if atomId == 'HDR':
                    return 'HD3'
                if atomId == 'HDS':
                    return 'HD2'
            elif refCompId == 'GLN':
                if atomId == 'HBR':
                    return 'HB2'
                if atomId == 'HBS':
                    return 'HB3'
                if atomId == 'HGR':
                    return 'HG3'
                if atomId == 'HGS':
                    return 'HG2'
                if atomId == 'HE2Z':
                    return 'HE22'
                if atomId == 'HE2E':
                    return 'HE21'
            elif refCompId == 'ARG':
                if atomId == 'HBR':
                    return 'HB2'
                if atomId == 'HBS':
                    return 'HB3'
                if atomId == 'HGR':
                    return 'HG3'
                if atomId == 'HGS':
                    return 'HG2'
                if atomId == 'HDR':
                    return 'HD3'
                if atomId == 'HDS':
                    return 'HD2'
                if atomId == 'NHZ':
                    return 'NH1'
                if atomId == 'NHE':
                    return 'NH2'
                if atomId == 'HH1Z':
                    return 'HH11'
                if atomId == 'HH1E':
                    return 'HH12'
                if atomId == 'HH2Z':
                    return 'HH21'
                if atomId == 'HH2E':
                    return 'HH22'
            elif refCompId == 'VAL':
                if atomId.startswith('HGR'):
                    return 'HG1'
                if atomId.startswith('HGS'):
                    return 'HG2'
                if atomId == 'CGR':
                    return 'CG1'
                if atomId == 'CGS':
                    return 'CG2'

    if atomId.endswith("O'1"):
        atomId = atomId[:lenAtomId - 3] + "O1'"
    elif atomId.endswith("O'2"):
        atomId = atomId[:lenAtomId - 3] + "O2'"
    elif atomId.endswith("O'3"):
        atomId = atomId[:lenAtomId - 3] + "O3'"
    elif atomId.endswith("O'4"):
        atomId = atomId[:lenAtomId - 3] + "O4'"
    elif atomId.endswith("O'5"):
        atomId = atomId[:lenAtomId - 3] + "O5'"
    elif atomId.endswith("O'6"):
        atomId = atomId[:lenAtomId - 3] + "O6'"
    elif atomId.endswith("'1") and not atomId.endswith("''1"):
        atomId = atomId.rstrip('1')
    elif atomId.endswith("'2") and not atomId.endswith("''2"):
        atomId = atomId.rstrip('2') + "'"
    elif atomId == 'O1P':
        atomId = 'OP1'
    elif atomId == 'O2P':
        atomId = 'OP2'
    elif atomId == 'O3P':
        atomId = 'OP3'
    elif atomId == 'H3T':
        atomId = "HO3'"
    elif atomId == 'H5T':
        atomId = 'HOP2'
    elif atomId.endswith("''"):
        if atomId[0] in ('C', 'O') and atomId[1].isdigit():
            atomId = atomId[:lenAtomId - 1]
    elif atomId.endswith('"'):
        atomId = atomId[:lenAtomId - 1] + "''"

    if refAtomIdList is not None and atomId not in refAtomIdList:
        if not atomId.endswith("'") and (atomId + "'") in refAtomIdList:
            return atomId + "'"
        if atomId.endswith("''''"):
            if atomId.startswith('H2') and "H2'2" in refAtomIdList:
                return "H2'2"
            if atomId.startswith('H5') and "H5'2" in refAtomIdList:
                return "H5'2"
            if atomId[:-2] in refAtomIdList:
                return atomId[:-2]
        if atomId.endswith("'''"):
            if atomId.startswith('H2') and "H2'1" in refAtomIdList:
                return "H2'1"
            if atomId.startswith('H5') and "H5'1" in refAtomIdList:
                return "H5'1"
            if atomId[:-1] in refAtomIdList:
                return atomId[:-1]
        if atomId == "H2''1" and "H2'" in refAtomIdList:
            return "H2'"
        if atomId == "H5''1" and "H5'" in refAtomIdList:
            return "H5'"
        if atomId in ("H2''2", "H2''"):
            if "HO2'" in refAtomIdList:
                return "HO2'"
            if "H2''" in refAtomIdList:
                return "H2''"
            if atomId == "H2''" and "H2'1" in refAtomIdList:
                return "H2'1"
        if atomId in ("H5''2", "H5''"):
            if "H5''" in refAtomIdList:
                return "H5''"
            if atomId == "H5''" and "H5'1" in refAtomIdList:
                return "H5'1"
        if atomId.endswith("''") and atomId[:-1] in refAtomIdList:
            return atomId[:-1]
        if atomId[0] == 'H' and lenAtomId == 3 and atomId[1].isdigit() and atomId[2] in ('1', '2'):
            n = atomId[1]
            if atomId.endswith('1') and ('HN' + n) in refAtomIdList:
                return 'HN' + n
            if atomId.endswith('2') and ('HN' + n + 'A') in refAtomIdList:
                return 'HN' + n + 'A'
        if atomId[0] == 'H' and lenAtomId == 3 and atomId[1].isdigit():  # DAOTHER-9198: DNR(DC):H3+ -> HN3
            if 'HN' + atomId[1] in refAtomIdList:
                return 'HN' + atomId[1]
        if atomId.startswith("HN'") and ccU.getTypeOfCompId(refCompId)[1]:
            nh2 = ccU.getRepAminoProtons(refCompId)
            if len(nh2) == 1:
                if atomId.endswith("''"):
                    nh2 = ccU.getNonRepAminoProtons(refCompId)
                    if nh2[0] in refAtomIdList:
                        return nh2[0]
                elif nh2[0] in refAtomIdList:
                    return nh2[0]
            elif atomId == "HN'":
                nh = ccU.getImideProtons(refCompId)
                if len(nh) == 1:
                    if nh[0] in refAtomIdList:
                        return nh[0]
        if atomId.startswith('HN') and "'" not in atomId and atomId[-1] in ('%', '*', '#') and not unambig:  # 2ky8: DG:HN* -> H4%
            nh2 = ccU.getRepAminoProtons(refCompId)
            if len(nh2) == 1:
                return nh2[0][:-1] + '%'
        if lenAtomId > 1 and atomId[-1] not in ('%', '*', '#') and refCompId not in monDict3:
            canAtomIdList = [_atomId for _atomId in refAtomIdList if _atomId[0] == atomId[0]]
            if len(canAtomIdList) > 0:
                pA = PairwiseAlign()
                score = -1
                conflict = 0
                _atomId_ = []
                iterAtomId = list(atomId)
                for _atomId in canAtomIdList:
                    pA.setReferenceSequence(iterAtomId, 'REF' + refCompId)
                    pA.addTestSequence(list(_atomId), refCompId)
                    pA.doAlign()

                    myAlign = pA.getAlignment(refCompId)

                    _matched, _, _conflict, _, _ = getScoreOfSeqAlign(myAlign)
                    _score = _matched - _conflict
                    if _score > score or (_score == score and conflict > _conflict):
                        _atomId_ = [_atomId]
                        score = _score
                        conflict = _conflict
                    elif _score == score and _conflict == conflict:
                        _atomId_.append(_atomId)
                if len(_atomId_) == 1 and (score > 1 or len(canAtomIdList) == 1):
                    return _atomId_[0]
        if atomId == 'X':  # micelle cennter
            if 'UNK' in refAtomIdList:  # 2mjq, 2mjr, 2mjs
                return 'UNK'
            if 'UNX' in refAtomIdList:  # 2mjt
                return 'UNX'

        if lenAtomId > 2 and atomId[:2] in SYMBOLS_ELEMENT and atomId[:2] in refAtomIdList and refCompId == atomId[:2]:
            if lenAtomId == 3 and atomId[-1] in ('+', '-', '1', '2', '3'):  # 6f0y, 2m28
                return atomId[:2]

            if lenAtomId == 4 and (atomId.endswith('1+') or atomId.endswith('2+') or atomId.endswith('3+')):
                return atomId[:2]

    if atomId.endswith('+1') or atomId.endswith('+2') or atomId.endswith('+3'):
        if atomId[:-2] in SYMBOLS_ELEMENT:
            return atomId[:-2]

    if lenAtomId > 2 and atomId[0] not in ('H', 'Q', 'M', 'C', 'N') and atomId[:2] in SYMBOLS_ELEMENT:  # 2ma7
        if lenAtomId == 3 and atomId[-1] in ('+', '-', '1', '2', '3'):
            return atomId[:2]

        if lenAtomId == 4 and (atomId.endswith('1+') or atomId.endswith('2+') or atomId.endswith('3+')):
            return atomId[:2]

    if atomId.endswith('++') and not unambig:
        return atomId[:-2] + '*'

    if atomId.endswith('+') and not unambig:
        return atomId[:-1] + '%'

    return atomId


def translateToStdAtomNameOfDmpc(atomId: str, dmpcNameSystemId: int = -1) -> str:
    """ Translate software specific atom nomenclature for DMPC to CCD PX4.
    """

    atomId = atomId.upper()
    lenAtomId = len(atomId)

    if dmpcNameSystemId == 1:  # 2mzi
        if atomId.startswith('CN') and lenAtomId == 3:
            if atomId[-1] == '1':
                return 'C3'
            if atomId[-1] == '2':
                return 'C4'
            if atomId[-1] == '3':
                return 'C5'
        if atomId == 'NTM':
            return 'N1'
        if atomId == 'CA':
            return 'C2'
        if atomId == 'CB':
            return 'C1'
        if atomId == 'P':
            return 'P1'
        if atomId == 'OA':
            return 'O3'
        if atomId == 'OB':
            return 'O1'
        if atomId == 'OC':
            return 'O2'
        if atomId == 'OD':
            return 'O4'
        if atomId == 'CC':
            return 'C6'
        if atomId == 'CD':
            return 'C7'

        if atomId == 'OE':
            return 'O7'
        if atomId == 'OF':
            return 'O8'
        if atomId.startswith('C2') and lenAtomId == 3:
            if atomId[-1] == 'A':
                return 'C8'
            if atomId[-1] == 'B':
                return 'C9'
            if atomId[-1] == 'C':
                return 'C10'
            if atomId[-1] == 'D':
                return 'C11'
            if atomId[-1] == 'E':
                return 'C12'
            if atomId[-1] == 'F':
                return 'C13'
            if atomId[-1] == 'G':
                return 'C14'
            if atomId[-1] == 'H':
                return 'C15'
            if atomId[-1] == 'I':
                return 'C16'
            if atomId[-1] == 'J':
                return 'C17'
            if atomId[-1] == 'K':
                return 'C18'
            if atomId[-1] == 'L':
                return 'C19'
            if atomId[-1] == 'M':
                return 'C20'
            if atomId[-1] == 'N':
                return 'C21'
            if atomId[-1] == 'B':
                return 'C22'

        if atomId == 'CE':
            return 'C8'
        if atomId == 'OG':
            return 'O5'
        if atomId == 'OH':
            return 'O6'
        if atomId.startswith('C1') and lenAtomId == 3:
            if atomId[-1] == 'A':
                return 'C23'
            if atomId[-1] == 'B':
                return 'C24'
            if atomId[-1] == 'C':
                return 'C25'
            if atomId[-1] == 'D':
                return 'C26'
            if atomId[-1] == 'E':
                return 'C27'
            if atomId[-1] == 'F':
                return 'C28'
            if atomId[-1] == 'G':
                return 'C29'
            if atomId[-1] == 'H':
                return 'C30'
            if atomId[-1] == 'I':
                return 'C31'
            if atomId[-1] == 'J':
                return 'C32'
            if atomId[-1] == 'K':
                return 'C33'
            if atomId[-1] == 'L':
                return 'C34'
            if atomId[-1] == 'M':
                return 'C35'
            if atomId[-1] == 'N':
                return 'C36'

    elif dmpcNameSystemId == 2:  # https://ftp.gromacs.org/contrib/topologies/DMPC.zip
        if atomId == 'N4':
            return 'N1'
        if atomId == 'C5':
            return 'C2'
        if atomId == 'C6':
            return 'C1'
        if atomId == 'OS7':
            return 'O3'
        if atomId == 'P8':
            return 'P1'
        if atomId == 'OM9':
            return 'O1'
        if atomId == 'OM10':
            return 'O2'
        if atomId == 'OS11':
            return 'O4'
        if atomId == 'C12':
            return 'C6'
        if atomId == 'C13':
            return 'C7'

        if atomId == 'OS14':
            return 'O5'
        if atomId == 'C15':
            return 'C8'
        if atomId == 'O16':
            return 'O6'
        if atomId == 'C17':
            return 'C9'
        if atomId == 'C18':
            return 'C10'
        if atomId == 'C19':
            return 'C11'
        if atomId == 'C20':
            return 'C12'
        if atomId == 'C21':
            return 'C13'
        if atomId == 'C22':
            return 'C14'
        if atomId == 'C23':
            return 'C15'
        if atomId == 'C24':
            return 'C16'
        if atomId == 'C25':
            return 'C17'
        if atomId == 'C26':
            return 'C18'
        if atomId == 'C27':
            return 'C19'
        if atomId == 'C28':
            return 'C20'
        if atomId == 'C29':
            return 'C21'
        if atomId == 'C30':
            return 'C22'

        if atomId == 'OS31':
            return 'O7'
        if atomId == 'C32':
            return 'C23'
        if atomId == 'O33':
            return 'O8'
        if atomId == 'C34':
            return 'C24'
        if atomId == 'C35':
            return 'C25'
        if atomId == 'C36':
            return 'C26'
        if atomId == 'C37':
            return 'C27'
        if atomId == 'C38':
            return 'C28'
        if atomId == 'C39':
            return 'C29'
        if atomId == 'C40':
            return 'C30'
        if atomId == 'C41':
            return 'C31'
        if atomId == 'C42':
            return 'C32'
        if atomId == 'C43':
            return 'C33'
        if atomId == 'C44':
            return 'C34'
        if atomId == 'C45':
            return 'C35'
        if atomId == 'C46':
            return 'C36'

    elif dmpcNameSystemId == 3:  # https://ftp.gromacs.org/contrib/topologies/AA_DMPC.tar.gz
        if atomId == 'N':
            return 'N1'
        if atomId == 'C13':
            return 'C3'
        if atomId.startswith('H13') and lenAtomId == 3:
            if atomId[-1] == 'A':
                return 'H5'
            if atomId[-1] == 'B':
                return 'H6'
            if atomId[-1] == 'C':
                return 'H7'
        if atomId == 'C14':
            return 'C4'
        if atomId.startswith('H14') and lenAtomId == 3:
            if atomId[-1] == 'A':
                return 'H8'
            if atomId[-1] == 'B':
                return 'H9'
            if atomId[-1] == 'C':
                return 'H10'
        if atomId == 'C15':
            return 'C5'
        if atomId.startswith('H15') and lenAtomId == 3:
            if atomId[-1] == 'A':
                return 'H11'
            if atomId[-1] == 'B':
                return 'H12'
            if atomId[-1] == 'C':
                return 'H13'
        if atomId == 'C12':
            return 'C2'
        if atomId.startswith('H12') and lenAtomId == 3:
            if atomId[-1] == 'A':
                return 'H3'
            if atomId[-1] == 'B':
                return 'H4'
        if atomId == 'C11':
            return 'C1'
        if atomId.startswith('H11') and lenAtomId == 3:
            if atomId[-1] == 'A':
                return 'H1'
            if atomId[-1] == 'B':
                return 'H2'
        if atomId == 'P':
            return 'P1'
        if atomId == 'O13':
            return 'O3'
        if atomId == 'O14':
            return 'O4'
        if atomId == 'O11':
            return 'O1'
        if atomId == 'O12':
            return 'O2'
        if atomId == 'C1':
            return 'C6'
        if atomId == 'HA':
            return 'H14'
        if atomId == 'HB':
            return 'H15'
        if atomId == 'C2':
            return 'C7'
        if atomId == 'HS':
            return 'H16'

        if atomId == 'O21':
            return 'O7'
        if atomId == 'C21':
            return 'C23'
        if atomId == 'O22':
            return 'O8'
        if atomId == 'C3':
            return 'C8'
        if atomId == 'HX':
            return 'C17'
        if atomId == 'HY':
            return 'C18'
        if atomId == 'O31':
            return 'O5'
        if atomId == 'C31':
            return 'C9'
        if atomId == 'O32':
            return 'O6'

        if atomId == 'C32':
            return 'C10'
        if atomId == 'H2X':
            return 'H19'
        if atomId == 'H2Y':
            return 'H20'
        if atomId == 'C33':
            return 'C11'
        if atomId == 'H3X':
            return 'H21'
        if atomId == 'H3Y':
            return 'H22'
        if atomId == 'C34':
            return 'C12'
        if atomId == 'H4X':
            return 'H23'
        if atomId == 'H4Y':
            return 'H24'
        if atomId == 'C35':
            return 'C13'
        if atomId == 'H5X':
            return 'H25'
        if atomId == 'H5Y':
            return 'H26'
        if atomId == 'C36':
            return 'C14'
        if atomId == 'H6X':
            return 'H27'
        if atomId == 'H6Y':
            return 'H28'
        if atomId == 'C37':
            return 'C15'
        if atomId == 'H7X':
            return 'H29'
        if atomId == 'H7Y':
            return 'H39'
        if atomId == 'C38':
            return 'C16'
        if atomId == 'H8X':
            return 'H31'
        if atomId == 'H8Y':
            return 'H32'
        if atomId == 'C39':
            return 'C17'
        if atomId == 'H9X':
            return 'H33'
        if atomId == 'H9Y':
            return 'H34'
        if atomId == 'C310':
            return 'C18'
        if atomId == 'H10X':
            return 'H35'
        if atomId == 'H10Y':
            return 'H36'
        if atomId == 'C311':
            return 'C19'
        if atomId == 'H11X':
            return 'H37'
        if atomId == 'H11Y':
            return 'H38'
        if atomId == 'C312':
            return 'C20'
        if atomId == 'H12X':
            return 'H39'
        if atomId == 'H12Y':
            return 'H40'
        if atomId == 'C313':
            return 'C21'
        if atomId == 'H13X':
            return 'H41'
        if atomId == 'H13Y':
            return 'H42'
        if atomId == 'C314':
            return 'C22'
        if atomId == 'H14X':
            return 'H43'
        if atomId == 'H14Y':
            return 'H44'
        if atomId == 'H14Z':
            return 'H45'

        if atomId == 'C22':
            return 'C24'
        if atomId == 'H2R':
            return 'H46'
        if atomId == 'H2S':
            return 'H47'
        if atomId == 'C23':
            return 'C25'
        if atomId == 'H3R':
            return 'H48'
        if atomId == 'H3S':
            return 'H49'
        if atomId == 'C24':
            return 'C26'
        if atomId == 'H4R':
            return 'H50'
        if atomId == 'H4S':
            return 'H51'
        if atomId == 'C25':
            return 'C27'
        if atomId == 'H5R':
            return 'H52'
        if atomId == 'H5S':
            return 'H53'
        if atomId == 'C26':
            return 'C28'
        if atomId == 'H6R':
            return 'H54'
        if atomId == 'H6S':
            return 'H55'
        if atomId == 'C27':
            return 'C29'
        if atomId == 'H7R':
            return 'H56'
        if atomId == 'H7S':
            return 'H57'
        if atomId == 'C28':
            return 'C30'
        if atomId == 'H8R':
            return 'H58'
        if atomId == 'H8S':
            return 'H59'
        if atomId == 'C29':
            return 'C31'
        if atomId == 'H9R':
            return 'H60'
        if atomId == 'H9S':
            return 'H61'
        if atomId == 'C210':
            return 'C32'
        if atomId == 'H10R':
            return 'H62'
        if atomId == 'H10S':
            return 'H63'
        if atomId == 'C211':
            return 'C33'
        if atomId == 'H11R':
            return 'H64'
        if atomId == 'H11S':
            return 'H65'
        if atomId == 'C212':
            return 'C34'
        if atomId == 'H12R':
            return 'H66'
        if atomId == 'H12S':
            return 'H67'
        if atomId == 'C213':
            return 'C35'
        if atomId == 'H13R':
            return 'H68'
        if atomId == 'H13S':
            return 'H69'
        if atomId == 'C214':
            return 'C36'
        if atomId == 'H14R':
            return 'H70'
        if atomId == 'H14S':
            return 'H71'
        if atomId == 'H14T':
            return 'H72'

    elif dmpcNameSystemId == 4:  # https://ftp.gromacs.org/contrib/topologies/LipidsForGro96_53a6.zip
        if atomId == 'C33':
            return 'C3'
        if atomId == 'C34':
            return 'C4'
        if atomId == 'C35':
            return 'C5'
        if atomId == 'N':
            return 'N1'
        if atomId == 'C32':
            return 'C2'
        if atomId == 'C31':
            return 'C1'
        if atomId == 'O32':
            return 'O3'
        if atomId == 'P':
            return 'P1'
        if atomId == 'O33':
            return 'O1'
        if atomId == 'O34':
            return 'O2'
        if atomId == 'O31':
            return 'O4'
        if atomId == 'C3':
            return 'C6'
        if atomId == 'C2':
            return 'C7'

        if atomId == 'O21':
            return 'O5'
        if atomId == 'C21':
            return 'C23'
        if atomId == 'O22':
            return 'O8'
        if atomId == 'C22':
            return 'C24'
        if atomId == 'C23':
            return 'C25'
        if atomId == 'C24':
            return 'C26'
        if atomId == 'C25':
            return 'C27'
        if atomId == 'C26':
            return 'C28'
        if atomId == 'C27':
            return 'C29'
        if atomId == 'C28':
            return 'C30'
        if atomId == 'C29':
            return 'C31'
        if atomId == 'C210':
            return 'C32'
        if atomId == 'C211':
            return 'C33'
        if atomId == 'C212':
            return 'C34'
        if atomId == 'C213':
            return 'C35'
        if atomId == 'C214':
            return 'C36'

        if atomId == 'C1':
            return 'C8'
        if atomId == 'O11':
            return 'O5'
        if atomId == 'C11':
            return 'C9'
        if atomId == 'O12':
            return 'O6'
        if atomId == 'C12':
            return 'C10'
        if atomId == 'C13':
            return 'C11'
        if atomId == 'C14':
            return 'C12'
        if atomId == 'C15':
            return 'C13'
        if atomId == 'C16':
            return 'C14'
        if atomId == 'C17':
            return 'C15'
        if atomId == 'C18':
            return 'C16'
        if atomId == 'C19':
            return 'C17'
        if atomId == 'C110':
            return 'C18'
        if atomId == 'C111':
            return 'C19'
        if atomId == 'C112':
            return 'C20'
        if atomId == 'C113':
            return 'C21'
        if atomId == 'C114':
            return 'C22'

    return atomId


def translateToStdResName(compId: str, refCompId: Optional[str] = None, ccU=None) -> str:
    """ Translate software specific residue name to standard residue name of CCD.
    """

    if compId is None:
        return None

    lenCompId = len(compId)
    lenRefCompId = 0 if refCompId is None else len(refCompId)

    if lenCompId > 3:
        compId3 = compId[:3]

        if compId3 in monDict3:
            return compId3

        compId3 = compId[1:]  # 1e8e

        if compId3 in monDict3 and compId[0] != 'P':  # 2lyw: PGLU -> PCA
            return compId3

    if compId[-1] in ('5', '3'):

        if compId[-1] == '5' and refCompId in ('DCZ', 'THM', 'OOB'):  # 7png
            return refCompId

        if compId[-1] == '3' and refCompId in ('4DG', 'L3X', 'URT', '23G', 'KAK', 'UZL'):
            return refCompId

        _compId = compId[:-1]

        if _compId in monDict3:
            return _compId

        if _compId == 'HC':
            return 'CH' if refCompId == 'C' else 'DNR'

    if compId.startswith('R') and lenCompId > 1 and compId[1] in ('A', 'C', 'G', 'U'):
        _compId = compId[1:]

        if _compId in monDict3:
            return _compId

        if refCompId is not None and lenRefCompId == 1 and _compId[-1] in ('5', '3'):
            _compId = _compId[:-1]

            if _compId in monDict3:
                return _compId

    if refCompId is not None and refCompId in monDict3 and lenRefCompId == 3:
        if lenCompId >= 3 and compId[:2] == refCompId[:2]:  # 1e8e: HID/HIE/HIF/HIP/HIZ -> HIS, PR. -> PRO, 2k4w: ASM -> ASP + ZN, 2n6j: TYZ -> TYR
            return refCompId
        if 'Z' in compId and compId[0] == refCompId[0]:  # 2n6j: GZC, GZL -> GLU + ZN,
            return refCompId

    if compId in ('HID', 'HIE', 'HIF', 'HIP', 'HIZ', 'HSD', 'HSE'):
        return 'HIS'

    if compId.startswith('CY'):
        if refCompId == 'CYS':  # 6xyv
            return 'CYS'
        if ccU is not None and ccU.updateChemCompDict(compId):
            if ccU.lastChemCompDict['_chem_comp.type'] == 'L-PEPTIDE LINKING'\
               and 'CYSTEINE' in ccU.lastChemCompDict['_chem_comp.name']:
                return 'CYS'

    if compId in ('CYO', 'CYX', 'CYZ', 'CZN'):
        return 'CYS'

    if lenCompId == 3:

        if compId.startswith('D'):
            d_peptide = False
            if ccU is not None and ccU.updateChemCompDict(compId):
                if ccU.lastChemCompDict['_chem_comp.type'] == 'D-PEPTIDE LINKING':
                    d_peptide = True
            if not d_peptide:  # 6qtf, 2lrr
                if compId.startswith('DA'):
                    return 'DA'
                if compId.startswith('DC'):
                    return 'DC'
                if compId.startswith('DG'):
                    return 'DG'
                if compId.startswith('DT'):
                    return 'DT'
                if compId.startswith('DU'):
                    return 'DU'
                if compId.startswith('DI'):
                    return 'DI'

        if compId.startswith('RA'):
            return 'A'
        if compId.startswith('RC'):
            return 'C'
        if compId.startswith('RG'):
            return 'G'
        if compId.startswith('RT'):
            return 'T'
        if compId.startswith('RU'):
            return 'U'
        if compId.startswith('RI'):
            return 'I'

        if compId == 'ADE':
            return 'A' if lenRefCompId == 1 else 'DA'
        if compId == 'CYT':
            return 'C' if lenRefCompId == 1 else 'DC'
        if compId == 'GUA':
            return 'G' if lenRefCompId == 1 else 'DG'
        if compId == 'THY':
            return 'DT'
        if compId == 'INO':
            return 'I' if lenRefCompId == 1 else 'DI'
        if compId == 'HCY':
            return 'CH' if lenRefCompId == 1 else 'DNR'

    if lenCompId == 2 and compId[1] == 'P':
        if compId == 'AP':
            return 'A' if lenRefCompId == 1 else 'DA'
        if compId == 'CP':
            return 'C' if lenRefCompId == 1 else 'DC'
        if compId == 'GP':
            return 'G' if lenRefCompId == 1 else 'DG'
        if compId == 'TP':
            return 'DT'
        if compId == 'UP':
            return 'U'
        if compId == 'IP':
            return 'I' if refCompId == 'I' else 'DI'

    if compId in ('NHE', 'CONH') and refCompId == 'NH2':  # 6hnh, 2m7r
        return 'NH2'

    if compId in ('RADE', 'RA'):
        return 'A'
    if compId in ('RCYT', 'RC'):
        return 'C'
    if compId in ('RGUA', 'RG'):
        return 'G'
    if compId in ('URA', 'URI', 'RU'):
        return 'U'
    if compId in ('RINO', 'RI'):
        return 'I'

    if compId == 'HEMB':
        return 'HEB'
    if compId == 'HEMC':
        return 'HEC'

    if lenCompId >= 3 and compId[:3] in ('H2O', 'WAT'):
        return 'HOH'

    if lenCompId > 3 and compId[3] in ('_', '+', '-'):  # 1e8e
        if ccU is not None and ccU.updateChemCompDict(compId[:3]):
            return compId[:3]

    if ccU is not None and ccU.updateChemCompDict(compId, False):
        if ccU.lastChemCompDict['_chem_comp.pdbx_release_status'] == 'OBS' and '_chem_comp.pdbx_replaced_by' in ccU.lastChemCompDict:
            replaced_by = ccU.lastChemCompDict['_chem_comp.pdbx_replaced_by']
            if replaced_by not in emptyValue and ccU.updateChemCompDict(replaced_by):
                compId = replaced_by

    return compId


def backTranslateFromStdResName(compId: str) -> Set[str]:
    """ Back translate standard residue name to software specific name.
    """

    if compId is None:
        return set()

    if compId == 'DA':
        return {'ADE', }

    if compId == 'DC':
        return {'CYT', }

    if compId == 'DG':
        return {'GUA', }

    if compId == 'DT':
        return {'THY', }

    if compId == 'DI':
        return {'INO', }

    if compId in ('CH', 'DNR'):
        return {'HCY', }

    if compId == 'A':
        return set(['RADE', 'RA'])

    if compId == 'C':
        return set(['RCYT', 'RC'])

    if compId == 'G':
        return set(['RGUA', 'RG'])

    if compId == 'U':
        return set(['URA', 'URI', 'RU'])

    if compId == 'I':
        return set(['RINO', 'RI'])

    return set()


def translateToLigandName(compId: str, refCompId: str, ccU) -> str:
    """ Translate software specific ligand name if possible.
    """

    if ccU.updateChemCompDict(refCompId):
        _compId = translateToStdResName(compId, refCompId, ccU)
        if '_chem_comp.mon_nstd_parent_comp_id' in ccU.lastChemCompDict:  # matches with comp_id in CCD
            if ccU.lastChemCompDict['_chem_comp.mon_nstd_parent_comp_id'] == _compId:
                return refCompId
        if compId.lower() in ccU.lastChemCompDict['_chem_comp.name'].lower():
            return refCompId
    return compId


def coordAssemblyChecker(verbose: bool = True, log: IO = sys.stdout,
                         representativeModelId: int = REPRESENTATIVE_MODEL_ID,
                         representativeAltId: str = REPRESENTATIVE_ALT_ID,
                         cR=None, ccU=None,
                         prevResult: Optional[dict] = None,
                         nmrPolySeq: Optional[List[dict]] = None, fullCheck: bool = True) -> dict:
    """ Check assembly of the coordinates for MR/PT parser listener.
        @return: properties about of the assembly of the cooridnates
    """

    changed = has_nonpoly_only = gen_ent_asm_from_nonpoly = False

    polySeq = None if prevResult is None else prevResult.get('polymer_sequence')
    altPolySeq = None if prevResult is None else prevResult.get('alt_polymer_sequence')
    nonPoly = None if prevResult is None else prevResult.get('non_polymer')
    branched = None if prevResult is None else prevResult.get('branched')
    misPolyLink = None if prevResult is None else prevResult.get('missing_polymer_linkage')
    nmrExtPolySeq = None if prevResult is None else prevResult.get('nmr_ext_poly_seq')
    modResidue = None if prevResult is None else prevResult.get('mod_residue')
    splitLigand = None if prevResult is None else prevResult.get('split_ligand')

    polySeqPdbMonIdName = 'pdb_mon_id' if cR.hasItem('pdbx_poly_seq_scheme', 'pdb_mon_id') else 'mon_id'
    nonPolyPdbMonIdName = 'pdb_mon_id' if cR.hasItem('pdbx_nonpoly_scheme', 'pdb_mon_id') else 'mon_id'
    branchedPdbMonIdName = 'pdb_mon_id' if cR.hasItem('pdbx_branch_scheme', 'pdb_mon_id') else 'mon_id'

    polySeqAuthMonIdName = 'auth_mon_id' if cR.hasItem('pdbx_poly_seq_scheme', 'auth_mon_id') else 'mon_id'
    nonPolyAuthMonIdName = 'auth_mon_id' if cR.hasItem('pdbx_nonpoly_scheme', 'auth_mon_id') else 'mon_id'
    branchedAuthMonIdName = 'auth_mon_id' if cR.hasItem('pdbx_branch_scheme', 'auth_mon_id') else 'mon_id'

    if None in (polySeq, misPolyLink, nmrExtPolySeq, modResidue, splitLigand):
        changed = True

        # loop categories
        _lpCategories = {'poly_seq': 'pdbx_poly_seq_scheme',
                         'non_poly': 'pdbx_nonpoly_scheme',
                         'branched': 'pdbx_branch_scheme',
                         'coordinate': 'atom_site',
                         'mis_poly_link': 'pdbx_validate_polymer_linkage',
                         'mod_residue': 'pdbx_struct_mod_residue'
                         }

        # key items of loop
        _keyItems = {'poly_seq': [{'name': 'asym_id', 'type': 'str', 'alt_name': 'chain_id'},
                                  {'name': 'seq_id', 'type': 'int', 'alt_name': 'seq_id'},
                                  {'name': 'mon_id', 'type': 'starts-with-alnum', 'alt_name': 'comp_id'},
                                  {'name': 'pdb_strand_id', 'type': 'str', 'alt_name': 'auth_chain_id'},
                                  {'name': 'pdb_seq_num', 'type': 'int', 'alt_name': 'auth_seq_id'},
                                  {'name': polySeqPdbMonIdName, 'type': 'str', 'alt_name': 'auth_comp_id', 'default-from': 'mon_id'}
                                  ],
                     'non_poly': [{'name': 'asym_id', 'type': 'str', 'alt_name': 'chain_id'},
                                  {'name': 'pdb_seq_num', 'type': 'int', 'alt_name': 'seq_id'},
                                  {'name': 'mon_id', 'type': 'starts-with-alnum', 'alt_name': 'comp_id'},
                                  {'name': 'pdb_strand_id', 'type': 'str', 'alt_name': 'auth_chain_id'},
                                  {'name': 'auth_seq_num', 'type': 'int', 'alt_name': 'auth_seq_id'},
                                  {'name': nonPolyPdbMonIdName, 'type': 'str', 'alt_name': 'auth_comp_id', 'default-from': 'mon_id'}
                                  ],
                     'branched': [{'name': 'asym_id', 'type': 'str', 'alt_name': 'chain_id'},
                                  {'name': 'pdb_seq_num', 'type': 'int', 'alt_name': 'seq_id'},
                                  {'name': 'mon_id', 'type': 'starts-with-alnum', 'alt_name': 'comp_id'},
                                  {'name': 'pdb_asym_id', 'type': 'str', 'alt_name': 'auth_chain_id'},
                                  {'name': 'auth_seq_num', 'type': 'int', 'alt_name': 'auth_seq_id'},
                                  {'name': branchedPdbMonIdName, 'type': 'str', 'alt_name': 'auth_comp_id', 'default-from': 'mon_id'}
                                  ],
                     'coordinate': [{'name': 'auth_asym_id', 'type': 'str', 'alt_name': 'auth_chain_id'},
                                    {'name': 'label_asym_id', 'type': 'str', 'alt_name': 'chain_id'},
                                    {'name': 'auth_seq_id', 'type': 'int', 'alt_name': 'auth_seq_id'},
                                    {'name': 'label_seq_id', 'type': 'str', 'alt_name': 'seq_id', 'default-from': 'auth_seq_id'},
                                    {'name': 'auth_comp_id', 'type': 'int', 'alt_name': 'auth_comp_id'},
                                    {'name': 'label_comp_id', 'type': 'starts-with-alnum', 'alt_name': 'comp_id'}
                                    ],
                     'mis_poly_link': [{'name': 'auth_asym_id_1', 'type': 'str', 'alt_name': 'auth_chain_id'},
                                       {'name': 'auth_seq_id_1', 'type': 'int'},
                                       {'name': 'auth_asym_id_2', 'type': 'str', 'alt_name': 'test_auth_chain_id'},
                                       {'name': 'auth_seq_id_2', 'type': 'int'}
                                       ],
                     'mod_residue': [{'name': 'auth_asym_id', 'type': 'str', 'alt_name': 'auth_chain_id'},
                                     {'name': 'label_asym_id', 'type': 'str', 'alt_name': 'chain_id'},
                                     {'name': 'auth_seq_id', 'type': 'int', 'alt_name': 'auth_seq_id'},
                                     {'name': 'label_seq_id', 'type': 'int', 'alt_name': 'seq_id', 'default-from': 'auth_seq_id'},
                                     {'name': 'parent_comp_id', 'type': 'str', 'alt_name': 'auth_comp_id'},
                                     {'name': 'label_comp_id', 'type': 'starts-with-alnum', 'alt_name': 'comp_id'}]
                     }

        contentSubtype = 'mis_poly_link'

        lpCategory = _lpCategories[contentSubtype]
        keyItems = _keyItems[contentSubtype]

        # DAOTHER-9644: support for truncated loop in the model
        misPolyLink = []
        if cR.hasCategory(lpCategory):
            filterItems = [{'name': 'PDB_model_num', 'type': 'int',
                            'value': representativeModelId},
                           {'name': 'label_alt_id_1', 'type': 'enum', 'enum': (representativeAltId,)},
                           {'name': 'label_alt_id_2', 'type': 'enum', 'enum': (representativeAltId,)}
                           ]

            try:

                for mis in cR.getDictListWithFilter(lpCategory, keyItems, filterItems):
                    if mis['auth_chain_id'] == mis['test_auth_chain_id']:
                        del mis['test_auth_chain_id']
                        misPolyLink.append(mis)

            except Exception as e:
                if verbose:
                    log.write(f"+ParserListenerUtil.coordAssemblyChecker() ++ Error  - {str(e)}\n")

        contentSubtype = 'poly_seq'

        lpCategory = _lpCategories[contentSubtype]
        keyItems = _keyItems[contentSubtype]

        nmrExtPolySeq = []
        splitLigand = {}

        try:

            if cR.hasItem(lpCategory, 'pdb_ins_code'):
                keyItems.append({'name': 'pdb_ins_code', 'type': 'str', 'alt_name': 'ins_code', 'default': '.'})

            if cR.hasItem(lpCategory, 'auth_mon_id'):
                keyItems.append({'name': 'auth_mon_id', 'type': 'str', 'alt_name': 'alt_comp_id', 'default-from': 'mon_id'})

            try:
                polySeq = cR.getPolymerSequence(lpCategory, keyItems,
                                                withStructConf=False,
                                                withRmsd=False)
            except KeyError:  # pdbx_PDB_ins_code throws KeyError
                polySeq = []

            if len(polySeq) == 0:
                contentSubtype = 'coordinate'

                lpCategory = _lpCategories[contentSubtype]
                keyItems = _keyItems[contentSubtype]

                if cR.hasItem(lpCategory, 'pdbx_PDB_ins_code'):
                    keyItems.append({'name': 'pdbx_PDB_ins_code', 'type': 'str', 'alt_name': 'ins_code', 'default': '.'})

                try:
                    polySeq = cR.getPolymerSequence(lpCategory, keyItems,
                                                    withStructConf=False,
                                                    withRmsd=False)
                except KeyError:
                    polySeq = []
                except ValueError:
                    has_nonpoly_only = True
                    polySeq = []

            if nmrPolySeq is not None:
                pA = PairwiseAlign()
                seqAlign, _ = alignPolymerSequence(pA, polySeq, nmrPolySeq)
                chainAssign, _ = assignPolymerSequence(pA, ccU, 'nmr-star', polySeq, nmrPolySeq, seqAlign)

                for ca in chainAssign:
                    ref_chain_id = ca['ref_chain_id']
                    test_chain_id = ca['test_chain_id']

                    sa = next(sa for sa in seqAlign
                              if sa['ref_chain_id'] == ref_chain_id
                              and sa['test_chain_id'] == test_chain_id)

                    if sa['conflict'] > 0 or sa['unmapped'] == 0:
                        continue

                    ps1 = next(ps1 for ps1 in nmrPolySeq if ps1['chain_id'] == test_chain_id)
                    ps2 = next(ps2 for ps2 in polySeq if ps2['auth_chain_id'] == ref_chain_id)

                    pA.setReferenceSequence(ps1['comp_id'], 'REF' + test_chain_id)
                    pA.addTestSequence(ps2['comp_id'], test_chain_id)
                    pA.doAlign()

                    myAlign = pA.getAlignment(test_chain_id)

                    length = len(myAlign)

                    _matched, unmapped, conflict, offset_1, offset_2 = getScoreOfSeqAlign(myAlign)

                    if conflict == 0 and unmapped > 0:

                        nmr_seq_ids, cif_auth_seq_ids, cif_label_seq_ids = [], [], []

                        for i in range(length):
                            if str(myAlign[i][0]) != '.' and i < len(ps1['seq_id']):
                                nmr_seq_ids.append(ps1['seq_id'][i])
                            else:
                                nmr_seq_ids.append(None)

                        for i in range(length):
                            if str(myAlign[i][1]) != '.' and i < len(ps2['seq_id']):
                                cif_auth_seq_ids.append(ps2['auth_seq_id'][i])
                                cif_label_seq_ids.append(ps2['seq_id'][i])
                            else:
                                cif_auth_seq_ids.append(None)
                                cif_label_seq_ids.append(None)

                        for i in range(length):
                            myPr = myAlign[i]
                            if myPr[0] == myPr[1]:
                                continue

                            nmr_comp_id = str(myPr[0])
                            cif_comp_id = str(myPr[1])

                            if cif_comp_id == '.' and nmr_comp_id != '.':
                                nmr_seq_id = nmr_seq_ids[i] - offset_1 if nmr_seq_ids[i] is not None else None
                                if nmr_seq_id is not None:
                                    offset = None
                                    for _offset in range(1, 20):
                                        if i + _offset < length:
                                            _myPr = myAlign[i + _offset]
                                            if _myPr[0] == _myPr[1]:
                                                offset = _offset
                                                break
                                        if i - _offset >= 0:
                                            _myPr = myAlign[i - _offset]
                                            if _myPr[0] == _myPr[1]:
                                                offset = -_offset
                                                break

                                    if offset is not None and cif_auth_seq_ids[i + offset] is not None:
                                        cif_label_seq_id = cif_label_seq_ids[i + offset] - offset - offset_2
                                        cif_auth_seq_id = cif_auth_seq_ids[i + offset] - offset - offset_2

                                        ps2_seq_id_list = list(filter(None, ps2['seq_id']))

                                        if cif_label_seq_id < min(ps2_seq_id_list):
                                            pos = 0
                                        elif cif_label_seq_id > max(ps2_seq_id_list):
                                            pos = len(ps2['seq_id'])
                                        else:
                                            for idx, _seq_id in enumerate(ps2['seq_id']):
                                                if _seq_id < cif_label_seq_id:
                                                    continue
                                                pos = idx
                                                break

                                        ps2['seq_id'].insert(pos, cif_label_seq_id)
                                        ps2['auth_seq_id'].insert(pos, cif_auth_seq_id)
                                        ps2['comp_id'].insert(pos, nmr_comp_id)
                                        if ps2['comp_id'] is not ps2['auth_comp_id']:  # avoid doulble inserts to 'auth_comp_id'
                                            ps2['auth_comp_id'].insert(pos, nmr_comp_id)

                                        nmrExtPolySeq.append({'auth_chain_id': ps2['auth_chain_id'],
                                                              'chain_id': ps2['chain_id'],
                                                              'seq_id': cif_label_seq_id,
                                                              'auth_seq_id': cif_auth_seq_id,
                                                              'comp_id': nmr_comp_id,
                                                              'auth_comp_id': nmr_comp_id})

            # DAOTHER-9644: support for truncated loop in the model
            if len(misPolyLink) > 0:

                for ps in polySeq:

                    for mis in misPolyLink:

                        if mis['auth_chain_id'] != ps['auth_chain_id']:
                            continue

                        authSeqId1 = mis['auth_seq_id_1']
                        authSeqId2 = mis['auth_seq_id_2']

                        if authSeqId1 in ps['auth_seq_id']\
                           and authSeqId2 in ps['auth_seq_id']\
                           and authSeqId1 < authSeqId2:

                            for authSeqId in range(authSeqId1 + 1, authSeqId2):
                                authSeqIdList = list(filter(None, ps['auth_seq_id']))

                                if authSeqId < min(authSeqIdList):
                                    pos = 0
                                elif authSeqId > max(authSeqIdList):
                                    pos = len(authSeqIdList)
                                else:
                                    for idx, _authSeqId in enumerate(authSeqIdList):
                                        if _authSeqId < authSeqId:
                                            continue
                                        pos = idx
                                        break

                                ps['auth_seq_id'].insert(pos, authSeqId)
                                ps['comp_id'].insert(pos, '.')  # DAOTHER-9644: comp_id must be specified at Macromelucule page
                                if 'auth_comp_id' in ps and ps['comp_id'] is not ps['auth_comp_id']:  # avoid doulble inserts to 'auth_comp_id'
                                    ps['auth_comp_id'].insert(pos, '.')

                            ps['seq_id'] = list(range(1, len(ps['auth_seq_id']) + 1))

            # DAOTHER-9644: simulate pdbx_poly_seq_scheme category
            else:

                entity_poly = cR.getDictList('entity_poly')

                for ps in polySeq:
                    c = ps['chain_id']

                    etype = next((e['type'] for e in entity_poly if 'pdbx_strand_id' in e and c in e['pdbx_strand_id'].split(',')), None)

                    if etype is None:
                        continue

                    if 'polypeptide' in etype:
                        BEG_ATOM = "C"
                        END_ATOM = "N"
                    else:
                        BEG_ATOM = "O3'"
                        END_ATOM = "P"

                    has_ins_code = False

                    for p in range(len(ps['auth_seq_id']) - 1):
                        s_p = ps['auth_seq_id'][p]
                        s_q = ps['auth_seq_id'][p + 1]

                        if None in (s_p, s_q):
                            continue

                        if s_p == s_q:
                            has_ins_code = True
                            continue

                        if s_p + 1 != s_q:

                            if has_ins_code:
                                has_ins_code = False
                                continue

                            auth_seq_id_1 = s_p
                            auth_seq_id_2 = s_q

                            _beg = cR.getDictListWithFilter('atom_site',
                                                            CARTN_DATA_ITEMS,
                                                            [{'name': 'label_asym_id', 'type': 'str', 'value': c},
                                                             {'name': 'auth_seq_id', 'type': 'int', 'value': auth_seq_id_1},
                                                             {'name': 'label_atom_id', 'type': 'starts-with-alnum', 'value': BEG_ATOM},
                                                             {'name': 'pdbx_PDB_model_num', 'type': 'int', 'value': representativeModelId},
                                                             {'name': 'label_alt_id', 'type': 'enum', 'enum': (representativeAltId,)}
                                                             ])

                            _end = cR.getDictListWithFilter('atom_site',
                                                            CARTN_DATA_ITEMS,
                                                            [{'name': 'label_asym_id', 'type': 'str', 'value': c},
                                                             {'name': 'auth_seq_id', 'type': 'int', 'value': auth_seq_id_2},
                                                             {'name': 'label_atom_id', 'type': 'starts-with-alnum', 'value': END_ATOM},
                                                             {'name': 'pdbx_PDB_model_num', 'type': 'int', 'value': representativeModelId},
                                                             {'name': 'label_alt_id', 'type': 'enum', 'enum': (representativeAltId,)}
                                                             ])

                            if len(_beg) == 1 and len(_end) == 1 and numpy.linalg.norm(to_np_array(_beg[0]) - to_np_array(_end[0])) > 5.0:
                                misPolyLink.append({'auth_chain_id': ps['auth_chain_id'],
                                                    'auth_seq_id_1': auth_seq_id_1,
                                                    'auth_seq_id_2': auth_seq_id_2})

                                for auth_seq_id_ in range(auth_seq_id_1 + 1, auth_seq_id_2):
                                    auth_seq_id_list = list(filter(None, ps['auth_seq_id']))

                                    if auth_seq_id_ < min(auth_seq_id_list):
                                        pos = 0
                                    elif auth_seq_id_ > max(auth_seq_id_list):
                                        pos = len(auth_seq_id_list)
                                    else:
                                        for idx, _auth_seq_id_ in enumerate(auth_seq_id_list):
                                            if _auth_seq_id_ < auth_seq_id_:
                                                continue
                                            pos = idx
                                            break

                                    # DAOTHER-9674
                                    if 'unmapped_auth_seq_id' in ps and auth_seq_id_ in ps['unmapped_auth_seq_id']:
                                        continue

                                    ps['auth_seq_id'].insert(pos, auth_seq_id_)
                                    ps['comp_id'].insert(pos, '.')  # DAOTHER-9644: comp_id must be specified at Macromelucule page
                                    if 'auth_comp_id' in ps and ps['comp_id'] is not ps['auth_comp_id']:  # avoid doulble inserts to 'auth_comp_id'
                                        ps['auth_comp_id'].insert(pos, '.')

                                ps['seq_id'] = list(range(1, len(ps['auth_seq_id']) + 1))

            if len(polySeq) > 1:
                ps = copy.copy(polySeq[0])
                ps['auth_seq_id'] = ps['seq_id']
                altPolySeq = [ps]
                authSeqIdList = list(filter(None, ps['auth_seq_id']))
                lastSeqId = max(authSeqIdList)

                for chainId in range(1, len(polySeq)):
                    ps = copy.copy(polySeq[chainId])
                    seq_id_list = list(filter(None, ps['seq_id']))
                    if min(seq_id_list) <= lastSeqId:
                        offset = lastSeqId + 1 - min(seq_id_list)
                    else:
                        offset = 0
                    ps['auth_seq_id'] = [s + offset for s in ps['seq_id']]
                    altPolySeq.append(ps)
                    authSeqIdList = list(filter(None, ps['auth_seq_id']))
                    lastSeqId = max(authSeqIdList)

            for ps in polySeq:
                if 'ins_code' in ps and len(collections.Counter(ps['ins_code']).most_common()) == 1:
                    del ps['ins_code']

        except Exception as e:
            if verbose:
                log.write(f"+ParserListenerUtil.coordAssemblyChecker() ++ Error  - {str(e)}\n")

        contentSubtype = 'non_poly'

        lpCategory = _lpCategories[contentSubtype]
        keyItems = _keyItems[contentSubtype]

        nonPoly = None

        if cR.hasCategory(lpCategory):

            if cR.hasItem(lpCategory, 'pdb_ins_code'):
                keyItems.append({'name': 'pdb_ins_code', 'type': 'str', 'alt_name': 'ins_code', 'default': '.'})

            if cR.hasItem(lpCategory, 'auth_mon_id'):
                keyItems.append({'name': 'auth_mon_id', 'type': 'str', 'alt_name': 'alt_comp_id', 'default-from': 'mon_id'})

            try:
                nonPoly = cR.getPolymerSequence(lpCategory, keyItems,
                                                withStructConf=False,
                                                withRmsd=False)

                internal_conflict = False
                conflict_per_chain = [False] * len(nonPoly)

                for idx, np in enumerate(nonPoly):
                    altAuthSeqIds = []

                    for authSeqId, labelSeqId in zip(np['auth_seq_id'], np['seq_id']):

                        for _np in nonPoly:

                            if _np == np:
                                continue

                            if _np['auth_chain_id'] != np['auth_chain_id']:
                                continue

                            if labelSeqId in _np['auth_seq_id'] or authSeqId in _np['seq_id'] and labelSeqId != authSeqId:
                                altAuthSeqIds.append(labelSeqId)
                                conflict_per_chain[idx] = internal_conflict = True
                                break

                        if not conflict_per_chain[idx]:
                            ps = next((ps for ps in polySeq if ps['auth_chain_id'] == np['auth_chain_id']), None)

                            if ps is None:
                                continue

                            if authSeqId in ps['auth_seq_id'] and labelSeqId not in ps['auth_seq_id']:
                                altAuthSeqIds.append(labelSeqId)

                                if 'ambig_auth_seq_id' not in ps:
                                    ps['ambig_auth_seq_id'] = []
                                ps['ambig_auth_seq_id'].append(authSeqId)

                                conflict_per_chain[idx] = True

                            elif authSeqId not in altAuthSeqIds:
                                altAuthSeqIds.append(authSeqId)

                    if conflict_per_chain[idx]:
                        np['alt_auth_seq_id'] = altAuthSeqIds

                    if 'ins_code' in np and len(collections.Counter(np['ins_code']).most_common()) == 1:
                        del np['ins_code']

                if internal_conflict or any(conflict for conflict in conflict_per_chain):
                    for idx, np in enumerate(nonPoly):
                        if (internal_conflict or conflict_per_chain[idx]) and 'alt_auth_seq_id' in np:
                            np['auth_seq_id'], np['alt_auth_seq_id'] = np['alt_auth_seq_id'], np['auth_seq_id']

            except KeyError:
                nonPoly = None

        elif has_nonpoly_only:
            modelNumName = None if prevResult is None else prevResult.get('model_num_name')
            authAsymId = None if prevResult is None else prevResult.get('auth_asym_id')
            authSeqId = None if prevResult is None else prevResult.get('auth_seq_id')
            authAtomId = None if prevResult is None else prevResult.get('auth_atom_id')

            tags = cR.getAttributeList('atom_site')

            if modelNumName is None:
                modelNumName = 'pdbx_PDB_model_num' if 'pdbx_PDB_model_num' in tags else 'ndb_model'
            if authAsymId is None:
                authAsymId = 'pdbx_auth_asym_id' if 'pdbx_auth_asym_id' in tags else 'auth_asym_id'
            if authSeqId is None:
                authSeqId = 'pdbx_auth_seq_id' if 'pdbx_auth_seq_id' in tags else 'auth_seq_id'
            if authAtomId is None:
                authAtomId = 'auth_atom_id'
            altAuthAtomId = 'pdbx_auth_atom_name' if 'pdbx_auth_atom_name' in tags else None

            dataItems = [{'name': authAsymId, 'type': 'str', 'alt_name': 'chain_id'},
                         {'name': 'label_asym_id', 'type': 'str', 'alt_name': 'alt_chain_id'},
                         {'name': authSeqId, 'type': 'int', 'alt_name': 'seq_id'},
                         {'name': 'label_seq_id', 'type': 'str', 'alt_name': 'alt_seq_id'},
                         {'name': 'auth_comp_id', 'type': 'str', 'alt_name': 'comp_id'},
                         {'name': 'label_comp_id', 'type': 'starts-with-alnum', 'alt_name': 'alt_comp_id'},
                         {'name': authAtomId, 'type': 'str', 'alt_name': 'atom_id'}
                         ]

            has_ins_code = 'pdbx_PDB_ins_code' in tags

            if has_ins_code:
                dataItems.append({'name': 'pdbx_PDB_ins_code', 'type': 'str', 'alt_name': 'ins_code'})

            if altAuthAtomId is not None:
                dataItems.append({'name': altAuthAtomId, 'type': 'str', 'alt_name': 'alt_atom_id'})

            filterItems = [{'name': modelNumName, 'type': 'int',
                            'value': representativeModelId},
                           {'name': 'label_alt_id', 'type': 'enum', 'enum': (representativeAltId,)},
                           {'name': 'group_PDB', 'type': 'str', 'value': 'HETATM'}
                           ]

            coord = cR.getDictListWithFilter('atom_site', dataItems, filterItems)

            if len(coord) > 0:
                nonPoly = []

                compDict, seqDict, insCodeDict, authChainDict = {}, {}, {}, {}

                chainIds = []
                for item in coord:
                    if item['alt_chain_id'] not in chainIds:
                        chainIds.append(item['alt_chain_id'])

                if has_ins_code:
                    sortedSeq = sorted(set((item['alt_chain_id'], int(item['seq_id']), item['ins_code'], item['alt_comp_id']) for item in coord),
                                       key=itemgetter(1))

                    for c in chainIds:
                        compDict[c] = [x[3] for x in sortedSeq if x[0] == c]
                        seqDict[c] = [x[1] for x in sortedSeq if x[0] == c]
                        insCodeDict[c] = [x[2] for x in sortedSeq if x[0] == c]

                else:
                    sortedSeq = sorted(set((item['alt_chain_id'], int(item['seq_id']), item['alt_comp_id']) for item in coord),
                                       key=itemgetter(1))

                    for c in chainIds:
                        compDict[c] = [x[2] for x in sortedSeq if x[0] == c]
                        seqDict[c] = [x[1] for x in sortedSeq if x[0] == c]

                chainIds = []
                for x in sortedSeq:
                    if x[0] not in chainIds:
                        chainIds.append(x[0])

                for item in coord:
                    c = item['alt_chain_id']
                    if c not in authChainDict:
                        authChainDict[c] = item['chain_id']

                for i, c in enumerate(chainIds):
                    ent = {}  # entity

                    ent['chain_id'] = c
                    ent['auth_chain_id'] = authChainDict[c]

                    ent['seq_id'] = seqDict[c]
                    ent['comp_id'] = compDict[c]
                    if c in insCodeDict:
                        if any(i for i in insCodeDict[c] if i not in emptyValue):
                            ent['ins_code'] = insCodeDict[c]

                    ent['auth_seq_id'] = []
                    for s in seqDict[c]:
                        item = next((item for item in coord if item['alt_chain_id'] == c and int(item['seq_id']) == s), None)
                        if item is not None:
                            if item['seq_id'] not in emptyValue:
                                try:
                                    _s = int(item['seq_id'])
                                except ValueError:
                                    _s = None
                                ent['auth_seq_id'].append(_s)
                            else:
                                ent['auth_seq_id'].append(None)
                            ent['gap_in_auth_seq'] = False
                            for p in range(len(ent['auth_seq_id']) - 1):
                                s_p = ent['auth_seq_id'][p]
                                s_q = ent['auth_seq_id'][p + 1]
                                if None in (s_p, s_q):
                                    continue
                                if s_p + 1 != s_q:
                                    ent['gap_in_auth_seq'] = True
                                    break

                    ent['auth_comp_id'] = []
                    for s in seqDict[c]:
                        item = next((item for item in coord if item['alt_chain_id'] == c and int(item['seq_id']) == s), None)
                        if item is not None:
                            comp_id = item['comp_id']
                            if comp_id not in emptyValue:
                                ent['auth_comp_id'].append(comp_id)
                            else:
                                ent['auth_comp_id'].append('.')

                    nonPoly.append(ent)

        contentSubtype = 'branched'

        lpCategory = _lpCategories[contentSubtype]
        keyItems = _keyItems[contentSubtype]

        branched = None

        if cR.hasCategory(lpCategory):

            if cR.hasItem(lpCategory, 'pdb_ins_code'):
                keyItems.append({'name': 'pdb_ins_code', 'type': 'str', 'alt_name': 'ins_code', 'default': '.'})

            if cR.hasItem(lpCategory, 'auth_mon_id'):
                keyItems.append({'name': 'auth_mon_id', 'type': 'str', 'alt_name': 'alt_comp_id', 'default-from': 'mon_id'})

            try:
                branched = cR.getPolymerSequence(lpCategory, keyItems,
                                                 withStructConf=False,
                                                 withRmsd=False)

                internal_conflict = False
                conflict_per_chain = [False] * len(branched)

                for idx, br in enumerate(branched):
                    altAuthSeqIds = []

                    for authSeqId, labelSeqId in zip(br['auth_seq_id'], br['seq_id']):

                        for _br in branched:

                            if _br == br:
                                continue

                            if _br['auth_chain_id'] != br['auth_chain_id']:
                                continue

                            if labelSeqId in _br['auth_seq_id'] or authSeqId in _br['seq_id'] and labelSeqId != authSeqId:
                                altAuthSeqIds.append(labelSeqId)
                                conflict_per_chain[idx] = internal_conflict = True
                                break

                        if not conflict_per_chain[idx]:
                            ps = next((ps for ps in polySeq if ps['auth_chain_id'] == br['auth_chain_id']), None)

                            if ps is None:
                                continue

                            if authSeqId in ps['auth_seq_id'] and labelSeqId not in ps['auth_seq_id']:
                                altAuthSeqIds.append(labelSeqId)

                                if 'ambig_auth_seq_id' not in ps:
                                    ps['ambig_auth_seq_id'] = []
                                ps['ambig_auth_seq_id'].append(authSeqId)

                                conflict_per_chain[idx] = True

                            elif authSeqId not in altAuthSeqIds:
                                altAuthSeqIds.append(authSeqId)

                    if conflict_per_chain[idx]:
                        br['alt_auth_seq_id'] = altAuthSeqIds

                    if 'ins_code' in br and len(collections.Counter(br['ins_code']).most_common()) == 1:
                        del br['ins_code']

                if internal_conflict or any(conflict for conflict in conflict_per_chain):
                    for idx, br in enumerate(branched):
                        if (internal_conflict or conflict_per_chain[idx]) and 'alt_auth_seq_id' in br:
                            br['auth_seq_id'], br['alt_auth_seq_id'] = br['alt_auth_seq_id'], br['auth_seq_id']

                else:
                    for br in branched:
                        orderedAuthSeqIds = sorted(br['auth_seq_id'])
                        altSeqIds = [br['seq_id'][br['auth_seq_id'].index(authSeqId)] for authSeqId in orderedAuthSeqIds]
                        if br['seq_id'] != altSeqIds:
                            br['alt_auth_seq_id'] = altSeqIds

            except KeyError:
                branched = None

        if branched is not None or nonPoly is not None:
            if nonPoly is not None and len(nonPoly) > 0:
                for np in nonPoly:
                    if 'alt_comp_id' in np and 'alt_auth_seq_id' in np:
                        authChainId = np['auth_chain_id']
                        for authSeqId, compId, altAuthSeqId, altCompId in zip(np['auth_seq_id'], np['comp_id'], np['alt_auth_seq_id'], np['alt_comp_id']):
                            for ps in polySeq:
                                if ps['auth_chain_id'] == authChainId and 'alt_comp_id' in ps:
                                    for _authSeqId, _compId, _altCompId in zip(ps['auth_seq_id'], ps['comp_id'], ps['alt_comp_id']):
                                        if _authSeqId == altAuthSeqId and _altCompId == altCompId and compId != _compId:
                                            seqKey = (authChainId, altAuthSeqId, altCompId)
                                            if seqKey not in splitLigand:
                                                splitLigand[seqKey] = [{'auth_seq_id': altAuthSeqId, 'comp_id': _compId, 'atom_ids': []}]
                                            splitLigand[seqKey].append({'auth_seq_id': authSeqId, 'comp_id': compId, 'atom_ids': []})
            if branched is not None and len(branched) > 0:
                for br in branched:
                    if 'alt_comp_id' in br and 'alt_auth_seq_id' in br:
                        authChainId = br['auth_chain_id']
                        for authSeqId, compId, altAuthSeqId, altCompId in zip(br['auth_seq_id'], br['comp_id'], br['alt_auth_seq_id'], br['alt_comp_id']):
                            for ps in polySeq:
                                if ps['auth_chain_id'] == authChainId and 'alt_comp_id' in ps:
                                    for _authSeqId, _compId, _altCompId in zip(ps['auth_seq_id'], ps['comp_id'], ps['alt_comp_id']):
                                        if _authSeqId == altAuthSeqId and _altCompId == altCompId and compId != _compId:
                                            seqKey = (authChainId, altAuthSeqId, altCompId)
                                            if seqKey not in splitLigand:
                                                splitLigand[seqKey] = [{'auth_seq_id': altAuthSeqId, 'comp_id': _compId, 'atom_ids': []}]
                                            splitLigand[seqKey].append({'auth_seq_id': authSeqId, 'comp_id': compId, 'atom_ids': []})

        contentSubtype = 'mod_residue'

        lpCategory = _lpCategories[contentSubtype]
        keyItems = _keyItems[contentSubtype]

        modResidue = []
        if cR.hasCategory(lpCategory):
            modResidue = cR.getDictListWithFilter(lpCategory, keyItems)

    if not fullCheck:
        if not changed:
            return prevResult

        return {'polymer_sequence': polySeq,
                'alt_polymer_sequence': altPolySeq,
                'non_polymer': nonPoly,
                'branched': branched,
                'missing_polymer_linkage': misPolyLink,
                'nmr_ext_poly_seq': nmrExtPolySeq,
                'mod_residue': modResidue}

    modelNumName = None if prevResult is None else prevResult.get('model_num_name')
    authAsymId = None if prevResult is None else prevResult.get('auth_asym_id')
    authSeqId = None if prevResult is None else prevResult.get('auth_seq_id')
    authAtomId = None if prevResult is None else prevResult.get('auth_atom_id')

    coordAtomSite = None if prevResult is None else prevResult.get('coord_atom_site')
    coordUnobsRes = None if prevResult is None else prevResult.get('coord_unobs_res')
    coordUnobsAtom = None if prevResult is None else prevResult.get('coord_unobs_atom')
    labelToAuthSeq = None if prevResult is None else prevResult.get('label_to_auth_seq')
    authToLabelSeq = None if prevResult is None else prevResult.get('auth_to_label_seq')
    authToStarSeq = None if prevResult is None else prevResult.get('auth_to_star_seq')
    authToOrigSeq = None if prevResult is None else prevResult.get('auth_to_orig_seq')
    authToInsCode = None if prevResult is None else prevResult.get('auth_to_ins_code')
    authToEntityType = None if prevResult is None else prevResult.get('auth_to_entity_type')
    authToStarSeqAnn = None if prevResult is None else prevResult.get('auth_to_star_seq_ann')
    labelToAuthChain = None if prevResult is None else prevResult.get('label_to_auth_chain')
    authToLabelChain = None if prevResult is None else prevResult.get('auth_to_label_chain')
    entityAssembly = None if prevResult is None else prevResult.get('entity_assembly')

    # DAOTHER-8817
    chemCompAtom = None if prevResult is None else prevResult.get('chem_comp_atom')
    chemCompBond = None if prevResult is None else prevResult.get('chem_comp_bond')
    chemCompTopo = None if prevResult is None else prevResult.get('chem_comp_topo')
    authAtomNameToId = None if prevResult is None else prevResult.get('auth_atom_name_to_id')
    authAtomNameToIdExt = None if prevResult is None else prevResult.get('auth_atom_name_to_id_ext')

    try:

        tags = cR.getAttributeList('atom_site')

        if modelNumName is None:
            modelNumName = 'pdbx_PDB_model_num' if 'pdbx_PDB_model_num' in tags else 'ndb_model'
        authAsymId = 'auth_asym_id'
        if cR.hasItem('atom_site', 'pdbx_auth_asym_id'):
            coord = cR.getDictListWithFilter('atom_site', [{'name': 'auth_asym_id', 'type': 'str'},
                                                           {'name': 'pdbx_auth_asym_id', 'type': 'str'}])
            auth_asym_id_set, pdbx_auth_asym_id_set = set(), set()
            for c in coord:
                auth_asym_id_set.add(c['auth_asym_id'])
                pdbx_auth_asym_id_set.add(c['pdbx_auth_asym_id'])
            if len(pdbx_auth_asym_id_set) >= len(auth_asym_id_set):  # DAOTHER-10105: do not trust pdbx_auth_asym_id when the chain is split
                authAsymId = 'pdbx_auth_asym_id'
        if authSeqId is None:
            authSeqId = 'pdbx_auth_seq_id' if 'pdbx_auth_seq_id' in tags else 'auth_seq_id'
        if authAtomId is None:
            authAtomId = 'auth_atom_id'
        altAuthCompId = 'pdbx_auth_comp_id' if 'pdbx_auth_comp_id' in tags else None
        altAuthAtomId = 'pdbx_auth_atom_name' if 'pdbx_auth_atom_name' in tags else None

        if None in (coordAtomSite, labelToAuthSeq, authToLabelSeq, chemCompAtom, authAtomNameToId, authAtomNameToIdExt):
            changed = True

            dataItems = [{'name': authAsymId, 'type': 'str', 'alt_name': 'chain_id'},
                         {'name': 'label_asym_id', 'type': 'str', 'alt_name': 'alt_chain_id'},
                         {'name': authSeqId, 'type': 'int', 'alt_name': 'seq_id'},
                         {'name': 'label_seq_id', 'type': 'str', 'alt_name': 'alt_seq_id'},
                         {'name': 'auth_comp_id', 'type': 'str', 'alt_name': 'comp_id'},
                         {'name': authAtomId, 'type': 'str', 'alt_name': 'atom_id'},
                         {'name': 'type_symbol', 'type': 'str'}
                         ]

            if authAsymId != 'auth_asym_id':  # DAOTHER-8817
                dataItems.append({'name': 'auth_asym_id', 'type': 'str', 'alt_name': 'auth_chain_id'})
            if altAuthCompId is not None:
                dataItems.append({'name': altAuthCompId, 'type': 'str', 'alt_name': 'alt_comp_id'})
            if altAuthAtomId is not None:
                dataItems.append({'name': altAuthAtomId, 'type': 'str', 'alt_name': 'alt_atom_id'})

            filterItems = [{'name': modelNumName, 'type': 'int',
                            'value': representativeModelId},
                           {'name': 'label_alt_id', 'type': 'enum', 'enum': (representativeAltId,)}
                           ]

            if len(polySeq) > LEN_LARGE_ASYM_ID:
                filterItems.append({'name': authAsymId, 'type': 'enum', 'enum': LARGE_ASYM_ID,
                                    'fetch_first_match': True})  # to process large assembly avoiding forced timeout

            coord = cR.getDictListWithFilter('atom_site', dataItems, filterItems)

            # DAOTHER-8572: taking consideration of multiple mapping from auth_asym_id(s) to label_asym_id
            authToLabelChain = {}
            for ps in polySeq:
                if ps['auth_chain_id'] not in authToLabelChain:
                    authToLabelChain[ps['auth_chain_id']] = ps['chain_id']
                elif isinstance(authToLabelChain[ps['auth_chain_id']], str):
                    if ps['chain_id'] == authToLabelChain[ps['auth_chain_id']]:
                        continue
                    authToLabelChain[ps['auth_chain_id']] = [authToLabelChain[ps['auth_chain_id']], ps['chain_id']]
                else:
                    if ps['chain_id'] in authToLabelChain[ps['auth_chain_id']]:
                        continue
                    authToLabelChain[ps['auth_chain_id']].append(ps['chain_id'])
            labelToAuthChain = {ps['chain_id']: ps['auth_chain_id'] for ps in polySeq}

            if cR.hasCategory('pdbx_entity_branch'):

                for br in branched:
                    authToLabelChain[br['auth_chain_id']] = br['chain_id']
                    labelToAuthChain[br['chain_id']] = br['auth_chain_id']

                labelToAuthSeqForBranched = {}

                entities = cR.getDictList('entity')

                dataItems = [{'name': 'asym_id', 'type': 'str', 'alt_name': 'alt_chain_id'},
                             {'name': 'auth_seq_num', 'type': 'int', 'alt_name': 'alt_seq_id'},
                             {'name': 'pdb_seq_num', 'type': 'int', 'alt_name': 'seq_id'}
                             ]

                for entity in entities:
                    entityId = int(entity['id'])
                    entityType = entity['type']

                    if entityType == 'branched':
                        mappings = cR.getDictListWithFilter('pdbx_branch_scheme',
                                                            dataItems,
                                                            [{'name': 'entity_id', 'type': 'int', 'value': entityId}
                                                             ])

                        for item in mappings:
                            seqKey = (item['alt_chain_id'], item['seq_id'])
                            labelToAuthSeqForBranched[seqKey] = item['alt_seq_id']

                for c in coord:
                    if c['alt_seq_id'] is None:
                        seqKey = (c['alt_chain_id'], c['seq_id'])
                        if seqKey in labelToAuthSeqForBranched:
                            c['seq_id'], c['alt_seq_id'] = labelToAuthSeqForBranched[seqKey], str(c['seq_id'])

            coordAtomSite, labelToAuthSeq = {}, {}

            # DAOTHER-8817
            chemCompAtom, chemCompBond, chemCompTopo = {}, {}, {}

            # DAOTHER-8828
            authAtomNameToId, authAtomNameToIdExt = {}, {}

            chainIds = set(c['chain_id'] for c in coord)
            for chainId in chainIds:
                seqIds = set(c['seq_id'] for c in coord if c['chain_id'] == chainId)
                for seqId in seqIds:
                    seqKey = (chainId, seqId)
                    compId = next(c['comp_id'] for c in coord
                                  if c['chain_id'] == chainId and c['seq_id'] is not None and c['seq_id'] == seqId)
                    atomIds = [c['atom_id'] for c in coord
                               if c['chain_id'] == chainId and c['seq_id'] is not None and c['seq_id'] == seqId and c['comp_id'] == compId]
                    typeSymbols = [c['type_symbol'] for c in coord
                                   if c['chain_id'] == chainId and c['seq_id'] is not None and c['seq_id'] == seqId and c['comp_id'] == compId]
                    authChainId = chainId
                    if authAsymId != 'auth_asym_id':  # DAOTHER-8817
                        authChainId = next(c['auth_chain_id'] for c in coord
                                           if c['chain_id'] == chainId and c['seq_id'] is not None and c['seq_id'] == seqId and c['comp_id'] == compId)
                    coordAtomSite[seqKey] = {'chain_id': authChainId, 'comp_id': compId, 'atom_id': atomIds, 'type_symbol': typeSymbols}
                    if altAuthCompId is not None:
                        altCompIds = [c['comp_id'] for c in coord
                                      if c['chain_id'] == chainId and c['seq_id'] is not None and c['seq_id'] == seqId and c['comp_id'] == compId]
                        coordAtomSite[seqKey]['alt_comp_id'] = altCompIds
                    if altAuthAtomId is not None:
                        altAtomIds = [c['alt_atom_id'] for c in coord
                                      if c['chain_id'] == chainId and c['seq_id'] is not None and c['seq_id'] == seqId and c['comp_id'] == compId]
                        coordAtomSite[seqKey]['alt_atom_id'] = altAtomIds
                    altSeqId = next((c['alt_seq_id'] for c in coord if c['chain_id'] == chainId and c['seq_id'] == seqId and c['comp_id'] == compId), None)
                    if chainId in authToLabelChain and altSeqId is not None and altSeqId.isdigit():
                        if isinstance(authToLabelChain[chainId], str):
                            _seqKey = (authToLabelChain[chainId], int(altSeqId))
                            if _seqKey in labelToAuthSeq:
                                continue
                            labelToAuthSeq[_seqKey] = seqKey
                        else:
                            for _chainId in authToLabelChain[chainId]:  # DAOTHER-8572: select possible auth_asym_id(s)
                                ps = next((ps for ps in polySeq if ps['chain_id'] == _chainId), None)
                                if seqId in ps['auth_seq_id']:
                                    _seqKey = (_chainId, int(altSeqId))
                                    if _seqKey in labelToAuthSeq:
                                        continue
                                    labelToAuthSeq[_seqKey] = seqKey
                    else:
                        if seqKey not in labelToAuthSeq:
                            labelToAuthSeq[seqKey] = seqKey
                        if chainId != authChainId:
                            altKey = (authChainId, seqId)
                            coordAtomSite[altKey] = coordAtomSite[seqKey]
                    if splitLigand is not None and len(splitLigand) > 0:
                        found = False
                        for (_authChainId, _, _), ligList in splitLigand.items():
                            if _authChainId != authChainId:
                                continue
                            for lig in ligList:
                                if lig['auth_seq_id'] == seqId and lig['comp_id'] == compId:
                                    lig['atom_ids'] = atomIds
                                    found = True
                                    break
                            if found:
                                break
                    compIds = list(set(c['comp_id'] for c in coord
                                       if c['chain_id'] == chainId and c['seq_id'] is not None and c['seq_id'] == seqId))
                    if len(compIds) > 1:  # 2kny: split implict ins_code of atom_site
                        coordAtomSite[seqKey]['split_comp_id'] = compIds
                        for compId in compIds:
                            seqKey = (chainId, seqId, compId)
                            atomIds = [c['atom_id'] for c in coord
                                       if c['chain_id'] == chainId and c['seq_id'] is not None and c['seq_id'] == seqId and c['comp_id'] == compId]
                            typeSymbols = [c['type_symbol'] for c in coord
                                           if c['chain_id'] == chainId and c['seq_id'] is not None and c['seq_id'] == seqId and c['comp_id'] == compId]
                            coordAtomSite[seqKey] = {'chain_id': authChainId, 'comp_id': compId, 'atom_id': atomIds, 'type_symbol': typeSymbols, 'split_comp_id': compIds}
                            if altAuthCompId is not None:
                                altCompIds = [c['comp_id'] for c in coord
                                              if c['chain_id'] == chainId and c['seq_id'] is not None and c['seq_id'] == seqId and c['comp_id'] == compId]
                                coordAtomSite[seqKey]['alt_comp_id'] = altCompIds
                            if altAuthAtomId is not None:
                                altAtomIds = [c['alt_atom_id'] for c in coord
                                              if c['chain_id'] == chainId and c['seq_id'] is not None and c['seq_id'] == seqId and c['comp_id'] == compId]
                                coordAtomSite[seqKey]['alt_atom_id'] = altAtomIds
                            altSeqId = next((c['alt_seq_id'] for c in coord if c['chain_id'] == chainId and c['seq_id'] == seqId and c['comp_id'] == compId), None)
                            if chainId in authToLabelChain and altSeqId is not None and altSeqId.isdigit():
                                if isinstance(authToLabelChain[chainId], str):
                                    _seqKey = (authToLabelChain[chainId], int(altSeqId))
                                    if _seqKey in labelToAuthSeq:
                                        continue
                                    labelToAuthSeq[(authToLabelChain[chainId], int(altSeqId))] = (chainId, seqId)
                                else:
                                    for _chainId in authToLabelChain[chainId]:  # DAOTHER-8572: select possible auth_asym_id(s)
                                        ps = next((ps for ps in polySeq if ps['chain_id'] == _chainId), None)
                                        if seqId in ps['auth_seq_id']:
                                            _seqKey = (_chainId, int(altSeqId))
                                            if _seqKey in labelToAuthSeq:
                                                continue
                                            labelToAuthSeq[(_chainId, int(altSeqId))] = (chainId, seqId)
                            else:
                                _seqKey = (seqKey[0], seqKey[1])
                                if _seqKey not in labelToAuthSeq:
                                    labelToAuthSeq[_seqKey] = _seqKey
                                if chainId != authChainId:
                                    altKey = (authChainId, seqId, compId)
                                    coordAtomSite[altKey] = coordAtomSite[seqKey]

                    # DAOTHER-8817
                    if compId not in monDict3:

                        if compId not in chemCompAtom:
                            chemCompAtom[compId] = atomIds

                            dataItems = [{'name': 'Cartn_x', 'type': 'float', 'alt_name': 'x'},
                                         {'name': 'Cartn_y', 'type': 'float', 'alt_name': 'y'},
                                         {'name': 'Cartn_z', 'type': 'float', 'alt_name': 'z'},
                                         {'name': authAtomId, 'type': 'str', 'alt_name': 'atom_id'}
                                         ]

                            filterItems = [{'name': modelNumName, 'type': 'int',
                                            'value': representativeModelId},
                                           {'name': authAsymId, 'type': 'str', 'value': chainId},
                                           {'name': authSeqId, 'type': 'int', 'value': seqId},
                                           {'name': 'label_alt_id', 'type': 'enum', 'enum': (representativeAltId,)}
                                           ]

                            resCoordDict = {c['atom_id']: to_np_array(c) for c in cR.getDictListWithFilter('atom_site', dataItems, filterItems)}

                            chemCompBond[compId], chemCompTopo[compId] = {}, {}

                            for proton in atomIds:
                                if proton[0] in protonBeginCode:

                                    bonded = None
                                    distance = 1.5

                                    for heavy in atomIds:
                                        if heavy[0] not in protonBeginCode and proton in resCoordDict and heavy in resCoordDict:
                                            _distance = numpy.linalg.norm(resCoordDict[proton] - resCoordDict[heavy])

                                            if _distance < distance:
                                                distance = _distance
                                                bonded = heavy

                                    if bonded is not None:
                                        if bonded not in chemCompBond[compId]:
                                            chemCompBond[compId][bonded] = []
                                        chemCompBond[compId][bonded].append(proton)

                            for heavy in atomIds:
                                if heavy[0] not in protonBeginCode:
                                    for heavy2 in atomIds:
                                        if heavy2[0] not in protonBeginCode and heavy2 != heavy and heavy in resCoordDict and heavy2 in resCoordDict:
                                            _distance = numpy.linalg.norm(resCoordDict[heavy] - resCoordDict[heavy2])

                                            if _distance < 2.5:
                                                if heavy not in chemCompTopo[compId]:
                                                    chemCompTopo[compId][heavy] = []
                                                chemCompTopo[compId][heavy].append(heavy2)

                            if altAuthAtomId is not None:
                                for c in coord:
                                    if c['chain_id'] == chainId and c['seq_id'] is not None and c['seq_id'] == seqId:
                                        _compId = c['comp_id']
                                        if compId == _compId:
                                            if compId not in authAtomNameToId:
                                                authAtomNameToId[compId] = {}
                                            authAtomNameToId[compId][c['alt_atom_id']] = c['atom_id']
                                        if _compId not in authAtomNameToIdExt:
                                            authAtomNameToIdExt[_compId] = {}
                                        authAtomNameToIdExt[_compId][c['alt_atom_id']] = c['atom_id']

                        # DAOTHER-8751, 8817 (D_1300043061)
                        elif altAuthAtomId is not None and compId in authAtomNameToId and len(atomIds) != len(authAtomNameToId[compId]):
                            for c in coord:
                                if c['chain_id'] == chainId and c['seq_id'] is not None and c['seq_id'] == seqId:
                                    _compId = c['comp_id']
                                    if _compId not in authAtomNameToIdExt:
                                        authAtomNameToIdExt[_compId] = {}
                                    if c['alt_atom_id'] not in authAtomNameToIdExt[_compId]:
                                        authAtomNameToIdExt[_compId][c['alt_atom_id']] = c['atom_id']

            authToLabelSeq = {v: k for k, v in labelToAuthSeq.items()}

        if coordUnobsAtom is None:
            coordUnobsAtom = {}

            if cR.hasCategory('pdbx_unobs_or_zero_occ_atoms'):

                filterItemByRepModelId = [{'name': 'PDB_model_num', 'type': 'int', 'value': representativeModelId}]

                unobs = cR.getDictListWithFilter('pdbx_unobs_or_zero_occ_atoms',
                                                 [{'name': 'auth_asym_id', 'type': 'str', 'alt_name': 'chain_id'},
                                                  {'name': 'auth_seq_id', 'type': 'str', 'alt_name': 'seq_id'},
                                                  {'name': 'auth_comp_id', 'type': 'str', 'alt_name': 'comp_id'},
                                                  {'name': 'label_atom_id', 'type': 'str', 'alt_name': 'atom_id'}
                                                  ],
                                                 filterItemByRepModelId)

                if len(unobs) > 0:
                    chainIds = set(u['chain_id'] for u in unobs)
                    for chainId in chainIds:
                        seqIds = set(int(u['seq_id']) for u in unobs if u['chain_id'] == chainId and u['seq_id'] is not None)
                        for seqId in seqIds:
                            seqKey = (chainId, seqId)
                            compId = next(u['comp_id'] for u in unobs
                                          if u['chain_id'] == chainId and u['seq_id'] is not None and int(u['seq_id']) == seqId)
                            atomIds = [u['atom_id'] for u in unobs
                                       if u['chain_id'] == chainId and u['seq_id'] is not None and int(u['seq_id']) == seqId]
                            if len(atomIds) > 0:
                                coordUnobsAtom[seqKey] = {'comp_id': compId, 'atom_ids': atomIds}

        if coordUnobsRes is None:
            changed = True

            coordUnobsRes = {}

            if cR.hasCategory('pdbx_unobs_or_zero_occ_residues'):

                filterItemByRepModelId = [{'name': 'PDB_model_num', 'type': 'int', 'value': representativeModelId}]

                unobs = cR.getDictListWithFilter('pdbx_unobs_or_zero_occ_residues',
                                                 [{'name': 'auth_asym_id', 'type': 'str', 'alt_name': 'chain_id'},
                                                  {'name': 'auth_seq_id', 'type': 'str', 'alt_name': 'seq_id'},
                                                  {'name': 'auth_comp_id', 'type': 'str', 'alt_name': 'comp_id'}
                                                  ],
                                                 filterItemByRepModelId)

                if len(unobs) > 0:
                    chainIds = set(u['chain_id'] for u in unobs)
                    for chainId in chainIds:
                        seqIds = set(int(u['seq_id']) for u in unobs if u['chain_id'] == chainId and u['seq_id'] is not None)
                        for seqId in seqIds:
                            seqKey = (chainId, seqId)
                            compId = next(u['comp_id'] for u in unobs
                                          if u['chain_id'] == chainId and u['seq_id'] is not None and int(u['seq_id']) == seqId)
                            coordUnobsRes[seqKey] = {'comp_id': compId}

                    if any(seqKey for seqKey in coordUnobsRes.keys() if seqKey not in authToLabelSeq):

                        tags = cR.getAttributeList('pdbx_unobs_or_zero_occ_residues')

                        if 'label_asym_id' in tags and 'label_seq_id' in tags:

                            unobs = cR.getDictListWithFilter('pdbx_unobs_or_zero_occ_residues',
                                                             [{'name': 'auth_asym_id', 'type': 'str'},
                                                              {'name': 'auth_seq_id', 'type': 'str'},
                                                              {'name': 'label_asym_id', 'type': 'str'},
                                                              {'name': 'label_seq_id', 'type': 'str'}
                                                              ],
                                                             filterItemByRepModelId)

                            if len(unobs) > 0:
                                for u in unobs:
                                    if None not in (u['auth_asym_id'], u['auth_seq_id'], u['label_asym_id'], u['label_seq_id']):
                                        authSeqKey = (u['auth_asym_id'], int(u['auth_seq_id']))
                                        labelSeqKey = (u['label_asym_id'], int(u['label_seq_id']))

                                        if authSeqKey not in authToLabelSeq:
                                            authToLabelSeq[authSeqKey] = labelSeqKey
                                        if labelSeqKey not in labelToAuthSeq:
                                            labelToAuthSeq[labelSeqKey] = authSeqKey

        if len(nmrExtPolySeq) > 0:
            changed = True

            if coordUnobsRes is None:
                coordUnobsRes = {}

            for extSeq in nmrExtPolySeq:
                authSeqKey = (extSeq['auth_chain_id'], extSeq['auth_seq_id'])
                labelSeqKey = (extSeq['chain_id'], extSeq['seq_id'])
                if authSeqKey not in coordUnobsRes:
                    coordUnobsRes[authSeqKey] = {'comp_id': extSeq['comp_id']}
                if authSeqKey not in authToLabelSeq:
                    authToLabelSeq[authSeqKey] = labelSeqKey
                if labelSeqKey not in labelToAuthSeq:
                    labelToAuthSeq[labelSeqKey] = authSeqKey

        if len(misPolyLink) > 0:  # DAOTHER-9644: support for truncated loop in the model
            changed = True

            if coordUnobsRes is None:
                coordUnobsRes = {}

            for mis in misPolyLink:
                authChainId = mis['auth_chain_id']
                authSeqId1 = mis['auth_seq_id_1']
                authSeqId2 = mis['auth_seq_id_2']

                ps = next((ps for ps in polySeq if ps['auth_chain_id'] == authChainId), None)

                if ps is not None and authSeqId1 in ps['auth_seq_id'] and authSeqId2 in ps['auth_seq_id']\
                   and authSeqId1 < authSeqId2:

                    chainId = ps['chain_id']

                    for authSeqId in range(authSeqId1 + 1, authSeqId2):
                        authSeqKey = (authChainId, authSeqId)
                        if authSeqKey not in coordUnobsRes:
                            coordUnobsRes[authSeqKey] = {'comp_id': '.'}
                        labelSeqKey = (chainId, ps['seq_id'][ps['auth_seq_id'].index(authSeqId)])
                        if authSeqKey not in authToLabelSeq:
                            authToLabelSeq[authSeqKey] = labelSeqKey
                        if labelSeqKey not in labelToAuthSeq:
                            labelToAuthSeq[labelSeqKey] = authSeqKey

        if None in (authToStarSeq, authToEntityType, entityAssembly, authToStarSeqAnn):
            changed = True

            authToStarSeq, authToOrigSeq, authToInsCode, authToEntityType, authToStarSeqAnn =\
                {}, {}, {}, {}, {}
            entityAssembly = []

            entityAssemblyId = 1

            entities = cR.getDictList('entity')

            for entity in entities:
                entityId = int(entity['id'])
                entityType = entity.get('type', 'polymer')
                entitySrcMethod = entity.get('src_method', '.')
                entityDesc = entity.get('pdbx_description', '.')
                entityFW = entity.get('formula_weight', '.')
                if entityFW not in emptyValue:
                    entityFW = float(entityFW)
                entityCopies = entity.get('pdbx_number_of_molecules', '.')
                if entityCopies not in emptyValue:
                    entityCopies = int(entityCopies)
                entityEC = entity.get('pdbx_ec', '.')
                entityParent = entity.get('pdbx_parent_entity_id', '.')
                if entityParent not in emptyValue:
                    entityParent = int(entityParent)
                entityMutation = entity.get('pdbx_mutation', '.')
                entityFragment = entity.get('pdbx_fragment', '.')
                entityDetails = entity.get('details', '.')

                filterItemByEntityId = [{'name': 'entity_id', 'type': 'int', 'value': entityId}]

                entityRole = '.'
                if cR.hasCategory('entity_name_com'):
                    roles = cR.getDictListWithFilter('entity_name_com',
                                                     [{'name': 'name', 'type': 'str'}
                                                      ],
                                                     filterItemByEntityId)
                    if len(roles) > 0:
                        entityRole = ','.join([role['name'] for role in roles if role['name'] is not None])
                        if len(entityRole) == 0:
                            entityRole = '.'

                if entityType == 'polymer':
                    entityPolyType = oneLetterCodeCan = oneLetterCode = targetIdentifier = '.'
                    nstdMonomer = nstdLinkage = '.'
                    nstdChirality = None
                    if cR.hasCategory('entity_poly'):

                        tags = cR.getAttributeList('entity_poly')

                        hasSeqOneLetterCodeCan = 'pdbx_seq_one_letter_code_can' in tags
                        hasPdbxTargetIdentifier = 'pdbx_target_identifier' in tags
                        hasNstdMonomer = 'nstd_monomer' in tags
                        hasNstdLinkage = 'nstd_linkage' in tags
                        hasNstdChirality = 'nstd_chirality' in tags

                        dataItems = [{'name': 'type', 'type': 'str'},
                                     {'name': 'pdbx_seq_one_letter_code', 'type': 'str'}]

                        if hasSeqOneLetterCodeCan:
                            dataItems.append({'name': 'pdbx_seq_one_letter_code_can', 'type': 'str'})

                        if hasPdbxTargetIdentifier:
                            dataItems.append({'name': 'pdbx_target_identifier', 'type': 'str'})

                        if hasNstdMonomer:
                            dataItems.append({'name': 'nstd_monomer', 'type': 'str'})

                        if hasNstdLinkage:
                            dataItems.append({'name': 'nstd_linkage', 'type': 'str'})

                        if hasNstdChirality:
                            dataItems.append({'name': 'nstd_chirality', 'type': 'str'})

                        polyTypes = cR.getDictListWithFilter('entity_poly',
                                                             dataItems,
                                                             filterItemByEntityId)

                        if len(polyTypes) > 0:
                            polyType = polyTypes[0]
                            entityPolyType = polyType['type']
                            oneLetterCode = polyType['pdbx_seq_one_letter_code']
                            if hasSeqOneLetterCodeCan:
                                oneLetterCodeCan = polyType['pdbx_seq_one_letter_code_can']
                            if hasPdbxTargetIdentifier:
                                targetIdentifier = polyType['pdbx_target_identifier']
                            if hasNstdMonomer:
                                nstdMonomer = polyType['nstd_monomer']
                            if hasNstdLinkage:
                                nstdLinkage = polyType['nstd_linkage']
                            if hasNstdChirality:
                                nstdChirality = polyType['nstd_chirality']

                    if cR.hasCategory('pdbx_poly_seq_scheme'):
                        has_ins_code = cR.hasItem('pdbx_poly_seq_scheme', 'pdb_ins_code')

                        dataItems = [{'name': 'asym_id', 'type': 'str', 'alt_name': 'label_asym_id'},
                                     {'name': 'pdb_strand_id', 'type': 'str', 'alt_name': 'auth_asym_id'},
                                     {'name': 'seq_id', 'type': 'int'},
                                     {'name': 'pdb_seq_num', 'type': 'int', 'alt_name': 'auth_seq_id'},
                                     {'name': 'auth_seq_num', 'type': 'int', 'alt_name': 'alt_seq_id'},
                                     {'name': 'mon_id', 'type': 'starts-with-alnum', 'alt_name': 'comp_id'},
                                     {'name': polySeqAuthMonIdName, 'type': 'str', 'alt_name': 'auth_comp_id', 'default-from': 'mon_id'},  # DAOTHER-8817
                                     {'name': polySeqPdbMonIdName, 'type': 'str', 'alt_name': 'alt_comp_id', 'default-from': 'mon_id'}
                                     ]

                        if has_ins_code:
                            dataItems.append({'name': 'pdb_ins_code', 'type': 'str', 'alt_name': 'ins_code'})

                        mappings = cR.getDictListWithFilter('pdbx_poly_seq_scheme',
                                                            dataItems,
                                                            filterItemByEntityId)

                    else:
                        has_ins_code = cR.hasItem('atom_site', 'pdbx_PDB_ins_code')

                        dataItems = [{'name': 'label_asym_id', 'type': 'str'},
                                     {'name': 'auth_asym_id', 'type': 'str'},
                                     {'name': 'label_seq_id', 'type': 'int', 'alt_name': 'seq_id'},
                                     {'name': 'auth_seq_id', 'type': 'int'},
                                     {'name': 'pdbx_auth_seq_id' if cR.hasItem('atom_site', 'pdbx_auth_seq_id') else 'auth_seq_id',
                                      'type': 'int', 'alt_name': 'alt_seq_id'},
                                     {'name': 'label_comp_id', 'type': 'starts-with-alnum', 'alt_name': 'comp_id'},
                                     {'name': 'pdbx_auth_comp_id' if cR.hasItem('atom_site', 'pdbx_auth_comp_id') else 'auth_comp_id',
                                      'type': 'str', 'alt_name': 'auth_comp_id', 'default-from': 'label_comp_id'},
                                     {'name': 'auth_comp_id', 'type': 'str', 'alt_name': 'alt_comp_id', 'default-from': 'label_comp_id'},
                                     ]

                        if has_ins_code:
                            dataItems.append({'name': 'pdbx_PDB_ins_code', 'type': 'str', 'alt_name': 'ins_code'})

                        filterItems = [{'name': 'label_entity_id', 'type': 'int', 'value': entityId},
                                       {'name': modelNumName, 'type': 'int', 'value': representativeModelId},
                                       ]

                        _mappings = cR.getDictListWithFilter('atom_site',
                                                             dataItems,
                                                             filterItems)

                        mappings = []
                        for item in _mappings:
                            if item not in mappings:
                                mappings.append(item)

                    if len(misPolyLink) > 0:  # DAOTHER-9644: support for truncated loop in the model

                        for item in mappings:
                            if any(mis for mis in misPolyLink if mis['auth_chain_id'] == item['auth_asym_id']):
                                ps = next((ps for ps in polySeq if ps['auth_chain_id'] == item['auth_asym_id']), None)

                                if ps is None:
                                    continue

                                # DAOTHER-9644: insert label_seq_id for truncated loop in the coordinates
                                if item['auth_seq_id'] in ps['auth_seq_id']:
                                    item['seq_id'] = ps['seq_id'][ps['auth_seq_id'].index(item['auth_seq_id'])]

                        for mis in misPolyLink:
                            authChainId = mis['auth_chain_id']

                            if authChainId not in mappings[0]['auth_asym_id']:
                                continue

                            authSeqId1 = mis['auth_seq_id_1']
                            authSeqId2 = mis['auth_seq_id_2']

                            ps = next((ps for ps in polySeq if ps['auth_chain_id'] == authChainId), None)

                            if ps is not None and authSeqId1 in ps['auth_seq_id'] and authSeqId2 in ps['auth_seq_id']\
                               and authSeqId1 < authSeqId2:

                                chainId = ps['chain_id']

                                for authSeqId in range(authSeqId1 + 1, authSeqId2):
                                    idx = ps['auth_seq_id'].index(authSeqId)
                                    mappings.append({'label_asym_id': chainId,
                                                     'auth_asym_id': authChainId,
                                                     'seq_id': ps['seq_id'][idx],
                                                     'auth_seq_id': authSeqId,
                                                     'alt_seq_id': authSeqId,
                                                     'comp_id': ps['comp_id'][idx],  # DAOTHER-9644: comp_id must be specified at Macromelucule page
                                                     'auth_comp_id': ps['auth_comp_id'][idx],
                                                     'alt_comp_id': ps['auth_comp_id'][idx],
                                                     'ins_code': None})

                                mappings = sorted(mappings, key=itemgetter('seq_id'))

                    authAsymIds, labelAsymIds = [], []
                    compIds = set()
                    for item in mappings:
                        if item['auth_asym_id'] not in authAsymIds:
                            authAsymIds.append(item['auth_asym_id'])
                        if item['label_asym_id'] not in labelAsymIds:
                            labelAsymIds.append(item['label_asym_id'])
                        compIds.add(item['comp_id'])

                    # DAOTHER-9674
                    delIdx = []
                    for chainId in labelAsymIds:
                        ps = next(ps for ps in polySeq if ps['chain_id'] == chainId)
                        if 'unmapped_seq_id' not in ps:
                            continue
                        for seqId in ps['unmapped_seq_id']:
                            try:
                                item = next(item for item in mappings
                                            if item['label_asym_id'] == chainId
                                            and item['seq_id'] == seqId)
                                delIdx.append(mappings.index(item))
                            except StopIteration:
                                pass

                    if len(delIdx) > 0:
                        for idx in reversed(delIdx):
                            del mappings[idx]

                    for extSeq in nmrExtPolySeq:
                        if extSeq['auth_chain_id'] not in authAsymIds:
                            continue
                        compIds.add(extSeq['comp_id'])

                    if len(authAsymIds) <= MAX_MAG_IDENT_ASYM_ID:
                        if len(labelAsymIds) == 1:
                            for item in mappings:
                                has_ins_code_val = has_ins_code and item['ins_code'] not in emptyValue
                                seqKey = (item['auth_asym_id'], item['auth_seq_id'], item['comp_id'])
                                authToStarSeq[seqKey] = authToStarSeqAnn[seqKey] = (entityAssemblyId, item['seq_id'], entityId, True)
                                authToOrigSeq[seqKey] = (item['alt_seq_id'], item['alt_comp_id'])
                                if has_ins_code_val:
                                    authToInsCode[seqKey] = item['ins_code']
                                authToEntityType[seqKey] = entityPolyType  # e.g. polypeptide(L), polyribonucleotide, polydeoxyribonucleotide
                                if item['comp_id'] != item['auth_comp_id']:  # DAOTHER-8817
                                    _seqKey = (item['auth_asym_id'], item['auth_seq_id'], item['auth_comp_id'])
                                    authToStarSeqAnn[_seqKey] = authToStarSeq[seqKey]

                            ext_mappings = 0
                            ext_fw = 0.0
                            for extSeq in nmrExtPolySeq:
                                if extSeq['auth_chain_id'] not in authAsymIds:
                                    continue
                                seqKey = (extSeq['auth_chain_id'], extSeq['auth_seq_id'], extSeq['comp_id'])
                                authToStarSeq[seqKey] = authToStarSeqAnn[seqKey] = (entityAssemblyId, extSeq['seq_id'], entityId, True)
                                authToOrigSeq[seqKey] = (extSeq['seq_id'], extSeq['auth_comp_id'])
                                authToEntityType[seqKey] = entityPolyType  # e.g. polypeptide(L), polyribonucleotide, polydeoxyribonucleotide
                                ext_mappings += 1
                                if extSeq['chain_id'] not in monDict3:
                                    nstdMonomer = 'yes'
                                ext_fw += ccU.getEffectiveFormulaWeight(extSeq['comp_id'])

                            for item in mappings:
                                altKey = (item['auth_asym_id'], item['alt_seq_id'], item['comp_id'])
                                if altKey not in authToStarSeq:
                                    has_ins_code_val = has_ins_code and item['ins_code'] not in emptyValue
                                    authToStarSeq[altKey] = authToStarSeqAnn[altKey] = (entityAssemblyId, item['seq_id'], entityId, True)
                                    if has_ins_code_val:
                                        authToInsCode[altKey] = item['ins_code']
                                    authToEntityType[altKey] = entityPolyType
                                    if item['comp_id'] != item['auth_comp_id']:  # DAOTHER-8817
                                        _altKey = (item['auth_asym_id'], item['alt_seq_id'], item['auth_comp_id'])
                                        authToStarSeqAnn[_altKey] = authToStarSeq[altKey]

                            for extSeq in nmrExtPolySeq:
                                if extSeq['auth_chain_id'] not in authAsymIds:
                                    continue
                                altKey = (extSeq['auth_chain_id'], extSeq['auth_seq_id'], extSeq['comp_id'])
                                if altKey not in authToStarSeq:
                                    authToStarSeq[altKey] = authToStarSeqAnn[altKey] = (entityAssemblyId, extSeq['seq_id'], entityId, True)
                                    authToEntityType[altKey] = entityPolyType

                            entityAssembly.append({'entity_assembly_id': entityAssemblyId, 'entity_id': entityId,
                                                   'entity_type': entityType, 'entity_src_method': entitySrcMethod,
                                                   'entity_desc': entityDesc, 'entity_fw': entityFW if ext_mappings == 0 else round(entityFW + ext_fw, 3),
                                                   'entity_copies': entityCopies, 'entity_ec': entityEC,
                                                   'entity_parent': entityParent,
                                                   'entity_mutation': entityMutation,
                                                   'entity_fragment': entityFragment,
                                                   'entity_details': entityDetails,
                                                   'entity_role': entityRole,
                                                   'entity_poly_type': entityPolyType,
                                                   'one_letter_code_can': oneLetterCodeCan,
                                                   'one_letter_code': oneLetterCode,
                                                   'nstd_monomer': nstdMonomer,
                                                   'nstd_linkage': nstdLinkage,
                                                   'nstd_chirality': nstdChirality,
                                                   'target_identifier': targetIdentifier,
                                                   'num_of_monomers': len(mappings) + ext_mappings,
                                                   'auth_asym_id': ','.join(authAsymIds),
                                                   'label_asym_id': ','.join(labelAsymIds),
                                                   'comp_id_set': compIds})
                            entityAssemblyId += 1

                        else:

                            _labelAsymIds = copy.copy(labelAsymIds)

                            for labelAsymId in _labelAsymIds:

                                authAsymIds, labelAsymIds = [], []
                                compIds = set()
                                for item in mappings:
                                    if item['label_asym_id'] != labelAsymId:
                                        continue
                                    if item['auth_asym_id'] not in authAsymIds:
                                        authAsymIds.append(item['auth_asym_id'])
                                    if item['label_asym_id'] not in labelAsymIds:
                                        labelAsymIds.append(item['label_asym_id'])
                                    compIds.add(item['comp_id'])

                                for extSeq in nmrExtPolySeq:
                                    if extSeq['chain_id'] != labelAsymId:
                                        continue
                                    compIds.add(extSeq['comp_id'])

                                if len(authAsymIds) <= MAX_MAG_IDENT_ASYM_ID:
                                    if len(labelAsymIds) == 1:
                                        for item in mappings:
                                            if item['label_asym_id'] != labelAsymId:
                                                continue
                                            has_ins_code_val = has_ins_code and item['ins_code'] not in emptyValue
                                            seqKey = (item['auth_asym_id'], item['auth_seq_id'], item['comp_id'])
                                            authToStarSeq[seqKey] = authToStarSeqAnn[seqKey] = (entityAssemblyId, item['seq_id'], entityId, True)
                                            authToOrigSeq[seqKey] = (item['alt_seq_id'], item['alt_comp_id'])
                                            if has_ins_code_val:
                                                authToInsCode[seqKey] = item['ins_code']
                                            authToEntityType[seqKey] = entityPolyType  # e.g. polypeptide(L), polyribonucleotide, polydeoxyribonucleotide
                                            if item['comp_id'] != item['auth_comp_id']:  # DAOTHER-8817
                                                _seqKey = (item['auth_asym_id'], item['auth_seq_id'], item['auth_comp_id'])
                                                authToStarSeqAnn[_seqKey] = authToStarSeq[seqKey]

                                        ext_mappings = 0
                                        ext_fw = 0.0
                                        for extSeq in nmrExtPolySeq:
                                            if extSeq['chain_id'] != labelAsymId:
                                                continue
                                            seqKey = (extSeq['auth_chain_id'], extSeq['auth_seq_id'], extSeq['comp_id'])
                                            authToStarSeq[seqKey] = authToStarSeqAnn[seqKey] = (entityAssemblyId, extSeq['seq_id'], entityId, True)
                                            authToOrigSeq[seqKey] = (extSeq['seq_id'], extSeq['auth_comp_id'])
                                            authToEntityType[seqKey] = entityPolyType  # e.g. polypeptide(L), polyribonucleotide, polydeoxyribonucleotide
                                            ext_mappings += 1
                                            if extSeq['chain_id'] not in monDict3:
                                                nstdMonomer = 'yes'
                                            ext_fw += ccU.getEffectiveFormulaWeight(extSeq['comp_id'])

                                        for item in mappings:
                                            if item['label_asym_id'] != labelAsymId:
                                                continue
                                            altKey = (item['auth_asym_id'], item['alt_seq_id'], item['comp_id'])
                                            if altKey not in authToStarSeq:
                                                has_ins_code_val = has_ins_code and item['ins_code'] not in emptyValue
                                                authToStarSeq[altKey] = authToStarSeqAnn[altKey] = (entityAssemblyId, item['seq_id'], entityId, True)
                                                if has_ins_code_val:
                                                    authToInsCode[altKey] = item['ins_code']
                                                authToEntityType[altKey] = entityPolyType
                                                if item['comp_id'] != item['auth_comp_id']:  # DAOTHER-8817
                                                    _altKey = (item['auth_asym_id'], item['alt_seq_id'], item['auth_comp_id'])
                                                    authToStarSeqAnn[_altKey] = authToStarSeq[altKey]

                                        for extSeq in nmrExtPolySeq:
                                            if extSeq['chain_id'] != labelAsymId:
                                                continue
                                            altKey = (extSeq['auth_chain_id'], extSeq['auth_seq_id'], extSeq['comp_id'])
                                            if altKey not in authToStarSeq:
                                                authToStarSeq[altKey] = authToStarSeqAnn[altKey] = (entityAssemblyId, extSeq['seq_id'], entityId, True)
                                                authToEntityType[altKey] = entityPolyType

                                        entityAssembly.append({'entity_assembly_id': entityAssemblyId, 'entity_id': entityId,
                                                               'entity_type': entityType, 'entity_src_method': entitySrcMethod,
                                                               'entity_desc': entityDesc, 'entity_fw': entityFW if ext_mappings == 0 else round(entityFW + ext_fw, 3),
                                                               'entity_copies': entityCopies, 'entity_ec': entityEC,
                                                               'entity_parent': entityParent,
                                                               'entity_mutation': entityMutation,
                                                               'entity_fragment': entityFragment,
                                                               'entity_details': entityDetails,
                                                               'entity_role': entityRole,
                                                               'entity_poly_type': entityPolyType,
                                                               'one_letter_code_can': oneLetterCodeCan,
                                                               'one_letter_code': oneLetterCode,
                                                               'nstd_monomer': nstdMonomer,
                                                               'nstd_linkage': nstdLinkage,
                                                               'nstd_chirality': nstdChirality,
                                                               'target_identifier': targetIdentifier,
                                                               'num_of_monomers': len(mappings) + ext_mappings,
                                                               'auth_asym_id': ','.join(authAsymIds),
                                                               'label_asym_id': ','.join(labelAsymIds),
                                                               'comp_id_set': compIds})
                                        entityAssemblyId += 1

                    else:

                        for _authAsymId in authAsymIds:
                            labelAsymIds = []
                            for item in mappings:
                                if item['auth_asym_id'] == _authAsymId:
                                    has_ins_code_val = has_ins_code and item['ins_code'] not in emptyValue
                                    seqKey = (item['auth_asym_id'], item['auth_seq_id'], item['comp_id'])
                                    authToStarSeq[seqKey] = authToStarSeqAnn[seqKey] = (entityAssemblyId, item['seq_id'], entityId, True)
                                    authToOrigSeq[seqKey] = (item['alt_seq_id'], item['alt_comp_id'])
                                    if has_ins_code_val:
                                        authToInsCode[seqKey] = item['ins_code']
                                    authToEntityType[seqKey] = entityPolyType  # e.g. polypeptide(L), polyribonucleotide, polydeoxyribonucleotide
                                    if item['comp_id'] != item['auth_comp_id']:  # DAOTHER-8817
                                        _seqKey = (item['auth_asym_id'], item['auth_seq_id'], item['auth_comp_id'])
                                        authToStarSeqAnn[_seqKey] = authToStarSeq[seqKey]
                                    if item['label_asym_id'] not in labelAsymIds:
                                        labelAsymIds.append(item['label_asym_id'])

                            ext_mappings = 0
                            ext_fw = 0.0
                            for extSeq in nmrExtPolySeq:
                                if extSeq['auth_chain_id'] == _authAsymId:
                                    seqKey = (extSeq['auth_chain_id'], extSeq['auth_seq_id'], extSeq['comp_id'])
                                    authToStarSeq[seqKey] = authToStarSeqAnn[seqKey] = (entityAssemblyId, extSeq['seq_id'], entityId, True)
                                    authToOrigSeq[seqKey] = (extSeq['seq_id'], extSeq['auth_comp_id'])
                                    authToEntityType[seqKey] = entityPolyType  # e.g. polypeptide(L), polyribonucleotide, polydeoxyribonucleotide
                                    ext_mappings += 1
                                    if extSeq['chain_id'] not in monDict3:
                                        nstdMonomer = 'yes'
                                    ext_fw += ccU.getEffectiveFormulaWeight(extSeq['comp_id'])

                            for item in mappings:
                                if item['auth_asym_id'] == _authAsymId:
                                    altKey = (item['auth_asym_id'], item['alt_seq_id'], item['comp_id'])
                                    if altKey not in authToStarSeq:
                                        has_ins_code_val = has_ins_code and item['ins_code'] not in emptyValue
                                        authToStarSeq[altKey] = authToStarSeqAnn[altKey] = (entityAssemblyId, item['seq_id'], entityId, True)
                                        if has_ins_code_val:
                                            authToInsCode[altKey] = item['ins_code']
                                        authToEntityType[altKey] = entityPolyType
                                        if item['comp_id'] != item['auth_comp_id']:  # DAOTHER-8817
                                            _altKey = (item['auth_asym_id'], item['alt_seq_id'], item['auth_comp_id'])
                                            authToStarSeqAnn[_altKey] = authToStarSeq[altKey]

                            for extSeq in nmrExtPolySeq:
                                if extSeq['auth_chain_id'] == _authAsymId:
                                    altKey = (extSeq['auth_chain_id'], extSeq['auth_seq_id'], extSeq['comp_id'])
                                    if altKey not in authToStarSeq:
                                        authToStarSeq[altKey] = authToStarSeqAnn[altKey] = (entityAssemblyId, extSeq['seq_id'], entityId, True)
                                        authToEntityType[altKey] = entityPolyType

                            entityAssembly.append({'entity_assembly_id': entityAssemblyId, 'entity_id': entityId,
                                                   'entity_type': entityType, 'entity_src_method': entitySrcMethod,
                                                   'entity_desc': entityDesc, 'entity_fw': entityFW if ext_mappings == 0 else round(entityFW + ext_fw, 3),
                                                   'entity_copies': 1, 'entity_ec': entityEC,
                                                   'entity_parent': entityParent,
                                                   'entity_mutation': entityMutation,
                                                   'entity_fragment': entityFragment,
                                                   'entity_details': entityDetails,
                                                   'entity_role': entityRole,
                                                   'entity_poly_type': entityPolyType,
                                                   'one_letter_code_can': oneLetterCodeCan,
                                                   'one_letter_code': oneLetterCode,
                                                   'nstd_monomer': nstdMonomer,
                                                   'nstd_linkage': nstdLinkage,
                                                   'nstd_chirality': nstdChirality,
                                                   'target_identifier': targetIdentifier,
                                                   'num_of_monomers': len(mappings) + ext_mappings,
                                                   'auth_asym_id': _authAsymId,
                                                   'label_asym_id': ','.join(labelAsymIds),
                                                   'comp_id_set': compIds})
                            entityAssemblyId += 1

                elif entityType == 'branched':
                    entityPolyType = '.'
                    if cR.hasCategory('pdbx_entity_branch'):
                        polyTypes = cR.getDictListWithFilter('pdbx_entity_branch',
                                                             [{'name': 'type', 'type': 'str'}
                                                              ],
                                                             filterItemByEntityId)
                        if len(polyTypes) > 0:
                            entityPolyType = polyTypes[0]['type']

                    if cR.hasCategory('pdbx_branch_scheme'):
                        has_ins_code = cR.hasItem('pdbx_branch_scheme', 'pdb_ins_code')

                        dataItems = [{'name': 'asym_id', 'type': 'str', 'alt_name': 'label_asym_id'},
                                     {'name': 'pdb_asym_id', 'type': 'str', 'alt_name': 'auth_asym_id'},
                                     {'name': 'num', 'type': 'int', 'alt_name': 'seq_id'},
                                     {'name': 'pdb_seq_num', 'type': 'int', 'alt_name': 'auth_seq_id'},
                                     {'name': 'auth_seq_num', 'type': 'int', 'alt_name': 'alt_seq_id'},
                                     {'name': 'mon_id', 'type': 'starts-with-alnum', 'alt_name': 'comp_id'},
                                     {'name': branchedAuthMonIdName, 'type': 'str', 'alt_name': 'auth_comp_id'},  # DAOTHER-8817
                                     {'name': branchedPdbMonIdName, 'type': 'str', 'alt_name': 'alt_comp_id'}
                                     ]

                        if has_ins_code:
                            dataItems.append({'name': 'pdb_ins_code', 'type': 'str', 'alt_name': 'ins_code'})

                        mappings = cR.getDictListWithFilter('pdbx_branch_scheme',
                                                            dataItems,
                                                            filterItemByEntityId)

                        authAsymIds = []
                        for item in mappings:
                            if item['auth_asym_id'] not in authAsymIds:
                                authAsymIds.append(item['auth_asym_id'])

                        if len(authAsymIds) <= MAX_MAG_IDENT_ASYM_ID:
                            labelAsymIds = []
                            for item in mappings:
                                has_ins_code_val = has_ins_code and item['ins_code'] not in emptyValue
                                seqKey = (item['auth_asym_id'], item['auth_seq_id'], item['comp_id'])
                                authToStarSeq[seqKey] = authToStarSeqAnn[seqKey] = (entityAssemblyId, item['seq_id'], entityId, False)
                                authToOrigSeq[seqKey] = (item['alt_seq_id'], item['alt_comp_id'])
                                if has_ins_code_val:
                                    authToInsCode[seqKey] = item['ins_code']
                                authToEntityType[seqKey] = entityPolyType  # e.g. oligosaccharide
                                if item['comp_id'] != item['auth_comp_id']:  # DAOTHER-8817
                                    _seqKey = (item['auth_asym_id'], item['auth_seq_id'], item['auth_comp_id'])
                                    authToStarSeqAnn[_seqKey] = authToStarSeq[seqKey]
                                if item['label_asym_id'] not in labelAsymIds:
                                    labelAsymIds.append(item['label_asym_id'])

                            for item in mappings:
                                altKey = (item['auth_asym_id'], item['alt_seq_id'], item['comp_id'])
                                if altKey not in authToStarSeq:
                                    has_ins_code_val = has_ins_code and item['ins_code'] not in emptyValue
                                    authToStarSeq[altKey] = authToStarSeqAnn[altKey] = (entityAssemblyId, item['seq_id'], entityId, True)
                                    if has_ins_code_val:
                                        authToInsCode[altKey] = item['ins_code']
                                    authToEntityType[altKey] = entityPolyType
                                    if item['comp_id'] != item['auth_comp_id']:  # DAOTHER-8817
                                        _altKey = (item['auth_asym_id'], item['alt_seq_id'], item['auth_comp_id'])
                                        authToStarSeqAnn[_altKey] = authToStarSeq[altKey]

                            entityAssembly.append({'entity_assembly_id': entityAssemblyId, 'entity_id': entityId,
                                                   'entity_type': entityType, 'entity_src_method': entitySrcMethod,
                                                   'entity_desc': entityDesc, 'entity_fw': entityFW,
                                                   'entity_copies': entityCopies,
                                                   'entity_details': entityDetails,
                                                   'entity_role': entityRole,
                                                   'entity_poly_type': entityPolyType,
                                                   'num_of_monomers': len(mappings),
                                                   'auth_asym_id': ','.join(authAsymIds),
                                                   'label_asym_id': ','.join(labelAsymIds)})
                            entityAssemblyId += 1

                        else:

                            for _authAsymId in authAsymIds:
                                labelAsymIds = []
                                for item in mappings:
                                    if item['auth_asym_id'] == _authAsymId:
                                        has_ins_code_val = has_ins_code and item['ins_code'] not in emptyValue
                                        seqKey = (item['auth_asym_id'], item['auth_seq_id'], item['comp_id'])
                                        authToStarSeq[seqKey] = authToStarSeqAnn[seqKey] = (entityAssemblyId, item['seq_id'], entityId, False)
                                        if has_ins_code_val:
                                            authToInsCode[seqKey] = item['ins_code']
                                        authToEntityType[seqKey] = entityPolyType  # e.g. oligosaccharide
                                        if item['comp_id'] != item['auth_comp_id']:  # DAOTHER-8817
                                            _seqKey = (item['auth_asym_id'], item['auth_seq_id'], item['auth_comp_id'])
                                            authToStarSeqAnn[_seqKey] = authToStarSeq[seqKey]
                                        if item['label_asym_id'] not in labelAsymIds:
                                            labelAsymIds.append(item['label_asym_id'])

                                for item in mappings:
                                    if item['auth_asym_id'] == _authAsymId:
                                        altKey = (item['auth_asym_id'], item['alt_seq_id'], item['comp_id'])
                                        if altKey not in authToStarSeq:
                                            has_ins_code_val = has_ins_code and item['ins_code'] not in emptyValue
                                            authToStarSeq[altKey] = authToStarSeqAnn[altKey] = (entityAssemblyId, item['seq_id'], entityId, True)
                                            if has_ins_code_val:
                                                authToInsCode[altKey] = item['ins_code']
                                            authToEntityType[altKey] = entityPolyType
                                            if item['comp_id'] != item['auth_comp_id']:  # DAOTHER-8817
                                                _altKey = (item['auth_asym_id'], item['alt_seq_id'], item['auth_comp_id'])
                                                authToStarSeqAnn[_altKey] = authToStarSeq[altKey]

                                entityAssembly.append({'entity_assembly_id': entityAssemblyId, 'entity_id': entityId,
                                                       'entity_type': entityType, 'entity_src_method': entitySrcMethod,
                                                       'entity_desc': entityDesc, 'entity_fw': entityFW,
                                                       'entity_copies': 1,
                                                       'entity_details': entityDetails,
                                                       'entity_role': entityRole,
                                                       'entity_poly_type': entityPolyType,
                                                       'num_of_monomers': len(mappings),
                                                       'auth_asym_id': _authAsymId,
                                                       'label_asym_id': ','.join(labelAsymIds)})
                                entityAssemblyId += 1

                elif entityType in ('non-polymer', 'water'):
                    if cR.hasCategory('pdbx_nonpoly_scheme'):
                        has_ins_code = cR.hasItem('pdbx_nonpoly_scheme', 'pdb_ins_code')

                        dataItems = [{'name': 'asym_id', 'type': 'str', 'alt_name': 'label_asym_id'},
                                     {'name': 'pdb_strand_id', 'type': 'str', 'alt_name': 'auth_asym_id'},
                                     {'name': 'ndb_seq_num', 'type': 'int', 'alt_name': 'seq_id'},
                                     {'name': 'pdb_seq_num', 'type': 'int', 'alt_name': 'auth_seq_id'},
                                     {'name': 'auth_seq_num', 'type': 'int', 'alt_name': 'alt_seq_id'},
                                     {'name': 'mon_id', 'type': 'starts-with-alnum', 'alt_name': 'comp_id'},
                                     {'name': nonPolyAuthMonIdName, 'type': 'str', 'alt_name': 'auth_comp_id', 'default-from': 'mon_id'},  # DAOTHER-8817
                                     {'name': nonPolyPdbMonIdName, 'type': 'str', 'alt_name': 'alt_comp_id', 'default-from': 'mon_id'}
                                     ]

                        if has_ins_code:
                            dataItems.append({'name': 'pdb_ins_code', 'type': 'str', 'alt_name': 'ins_code'})

                        mappings = cR.getDictListWithFilter('pdbx_nonpoly_scheme',
                                                            dataItems,
                                                            filterItemByEntityId)

                        authAsymIds = []
                        compId = None
                        for idx, item in enumerate(mappings):
                            has_ins_code_val = has_ins_code and item['ins_code'] not in emptyValue
                            seqKey = (item['auth_asym_id'], item['auth_seq_id'], item['comp_id'])
                            authToStarSeq[seqKey] = authToStarSeqAnn[seqKey] = (entityAssemblyId, idx + 1, entityId, True)
                            authToOrigSeq[seqKey] = (item['alt_seq_id'], item['alt_comp_id'])
                            if has_ins_code_val:
                                authToInsCode[seqKey] = item['ins_code']
                            authToEntityType[seqKey] = entityType
                            if item['comp_id'] != item['auth_comp_id']:  # DAOTHER-8817
                                _seqKey = (item['auth_asym_id'], item['auth_seq_id'], item['auth_comp_id'])
                                authToStarSeqAnn[_seqKey] = authToStarSeq[seqKey]
                            if item['auth_asym_id'] != item['label_asym_id']:  # DAOTHER-8817
                                _seqKey = (item['label_asym_id'], item['auth_seq_id'], item['comp_id'])
                                authToStarSeqAnn[_seqKey] = authToStarSeq[seqKey]
                                if item['comp_id'] != item['auth_comp_id']:  # DAOTHER-8817
                                    _seqKey = (item['label_asym_id'], item['auth_seq_id'], item['auth_comp_id'])
                                    authToStarSeqAnn[_seqKey] = authToStarSeq[seqKey]
                            if item['auth_asym_id'] not in authAsymIds:
                                authAsymIds.append(item['auth_asym_id'])
                            if compId is None:
                                compId = item['comp_id']

                        for idx, item in enumerate(mappings):
                            altKey = (item['auth_asym_id'], item['alt_seq_id'], item['comp_id'])
                            if altKey not in authToStarSeq:
                                has_ins_code_val = has_ins_code and item['ins_code'] not in emptyValue
                                authToStarSeq[altKey] = authToStarSeqAnn[altKey] = (entityAssemblyId, idx + 1, entityId, False)
                                if has_ins_code_val:
                                    authToInsCode[altKey] = item['ins_code']
                                authToEntityType[altKey] = entityType
                                if item['comp_id'] != item['auth_comp_id']:  # DAOTHER-8817
                                    _altKey = (item['auth_asym_id'], item['alt_seq_id'], item['auth_comp_id'])
                                    authToStarSeqAnn[_altKey] = authToStarSeq[altKey]
                                if item['auth_asym_id'] != item['label_asym_id']:  # DAOTHER-8817
                                    _altKey = (item['label_asym_id'], item['alt_seq_id'], item['comp_id'])
                                    authToStarSeqAnn[_altKey] = authToStarSeq[altKey]
                                    if item['comp_id'] != item['auth_comp_id']:  # DAOTHER-8817
                                        _altKey = (item['label_asym_id'], item['alt_seq_id'], item['auth_comp_id'])
                                        authToStarSeqAnn[_altKey] = authToStarSeq[altKey]

                        labelAsymIds = []
                        for item in mappings:
                            if item['label_asym_id'] not in labelAsymIds:
                                labelAsymIds.append(item['label_asym_id'])

                        entityAssembly.append({'entity_assembly_id': entityAssemblyId, 'entity_id': entityId,
                                               'entity_type': entityType, 'entity_src_method': entitySrcMethod,
                                               'entity_desc': entityDesc, 'entity_fw': entityFW,
                                               'entity_copies': entityCopies,
                                               'entity_details': entityDetails,
                                               'entity_role': entityRole,
                                               'auth_asym_id': ','.join(authAsymIds),
                                               'label_asym_id': ','.join(labelAsymIds),
                                               'comp_id': compId})
                        entityAssemblyId += 1

                    elif has_nonpoly_only:
                        gen_ent_asm_from_nonpoly = True

            if gen_ent_asm_from_nonpoly:

                _idx = {}
                for item in nonPoly:
                    for compId in item['comp_id']:
                        if compId not in _idx:
                            _idx[compId] = 0

                for item in nonPoly:
                    for idx, compId in enumerate(item['comp_id']):

                        for entity in entities:
                            entityId = int(entity['id'])
                            entityType = entity.get('type', 'polymer')
                            if entityType not in ('non-polymer', 'water'):
                                continue
                            entitySrcMethod = entity.get('src_method', '.')
                            entityDesc = entity.get('pdbx_description', '.')
                            entityFW = entity.get('formula_weight', '.')
                            if entityFW not in emptyValue:
                                entityFW = float(entityFW)
                            entityCopies = entity.get('pdbx_number_of_molecules', '.')
                            if entityCopies not in emptyValue:
                                entityCopies = int(entityCopies)
                            entityEC = entity.get('pdbx_ec', '.')
                            entityParent = entity.get('pdbx_parent_entity_id', '.')
                            if entityParent not in emptyValue:
                                entityParent = int(entityParent)
                            entityMutation = entity.get('pdbx_mutation', '.')
                            entityFragment = entity.get('pdbx_fragment', '.')
                            if compId != entityFragment:
                                continue
                            entityDetails = entity.get('details', '.')

                            filterItemByEntityId = [{'name': 'entity_id', 'type': 'int', 'value': entityId}]

                            entityRole = '.'
                            if cR.hasCategory('entity_name_com'):
                                roles = cR.getDictListWithFilter('entity_name_com',
                                                                 [{'name': 'name', 'type': 'str'}
                                                                  ],
                                                                 filterItemByEntityId)
                                if len(roles) > 0:
                                    entityRole = ','.join([role['name'] for role in roles if role['name'] is not None])
                                    if len(entityRole) == 0:
                                        entityRole = '.'

                            seqKey = (item['auth_chain_id'], item['auth_seq_id'][idx], compId)
                            authToStarSeq[seqKey] = (entityAssemblyId, _idx[compId] + 1, entityId, True)
                            authToOrigSeq[seqKey] = (item['seq_id'][idx], compId)
                            if 'ins_code' in item and item['ins_code'][idx] not in emptyValue:
                                authToInsCode[seqKey] = item['ins_code'][idx]
                            authToEntityType[seqKey] = entityType

                            authAsymIds, labelAsymIds = [], []
                            for _item in nonPoly:
                                if idx < len(item['comp_id']) and item['comp_id'][idx] == compId:
                                    if _item['auth_chain_id'] not in authAsymIds:
                                        authAsymIds.append(_item['auth_chain_id'])
                                    if _item['chain_id'] not in labelAsymIds:
                                        labelAsymIds.append(_item['chain_id'])

                            _idx[compId] += 1

                            entityAssembly.append({'entity_assembly_id': entityAssemblyId, 'entity_id': entityId,
                                                   'entity_type': entityType, 'entity_src_method': entitySrcMethod,
                                                   'entity_desc': entityDesc, 'entity_fw': entityFW,
                                                   'entity_copies': entityCopies,
                                                   'entity_details': entityDetails,
                                                   'entity_role': entityRole,
                                                   'auth_asym_id': ','.join(authAsymIds),
                                                   'label_asym_id': ','.join(labelAsymIds),
                                                   'fixed_auth_asym_id': item['auth_chain_id'],
                                                   'fixed_label_asym_id': item['chain_id'],
                                                   'comp_id': compId})
                            entityAssemblyId += 1

                            break

    except Exception as e:
        if verbose:
            log.write(f"+ParserListenerUtil.coordAssemblyChecker() ++ Error  - {str(e)}\n")

    if authToInsCode is not None and len(authToInsCode) == 0:
        authToInsCode = None

    if not changed:
        return prevResult

    return {'model_num_name': modelNumName,
            'auth_asym_id': authAsymId,
            'auth_seq_id': authSeqId,
            'auth_atom_id': authAtomId,
            'polymer_sequence': polySeq,
            'alt_polymer_sequence': altPolySeq,
            'non_polymer': nonPoly,
            'branched': branched,
            'missing_polymer_linkage': misPolyLink,
            'nmr_ext_poly_seq': nmrExtPolySeq,
            'mod_residue': modResidue,
            'coord_atom_site': coordAtomSite,
            'coord_unobs_atom': coordUnobsAtom,
            'coord_unobs_res': coordUnobsRes,
            'label_to_auth_seq': labelToAuthSeq,
            'auth_to_label_seq': authToLabelSeq,
            'label_to_auth_chain': labelToAuthChain,
            'auth_to_label_chain': authToLabelChain,
            'auth_to_star_seq': authToStarSeq,
            'auth_to_orig_seq': authToOrigSeq,
            'auth_to_ins_code': authToInsCode,
            'auth_to_entity_type': authToEntityType,
            'auth_to_star_seq_ann': authToStarSeqAnn,
            'entity_assembly': entityAssembly,
            'chem_comp_atom': chemCompAtom,
            'chem_comp_bond': chemCompBond,
            'chem_comp_topo': chemCompTopo,
            'auth_atom_name_to_id': authAtomNameToId,
            'auth_atom_name_to_id_ext': authAtomNameToIdExt,
            'split_ligand': splitLigand}


def extendCoordChainsForExactNoes(modelChainIdExt: dict,
                                  polySeq: List[dict], altPolySeq: List[dict],
                                  coordAtomSite: Optional[dict], coordUnobsRes: Optional[dict],
                                  authToLabelSeq: Optional[dict], authToStarSeq: Optional[dict],
                                  authToOrigSeq: Optional[dict]):
    """ Extend coordinate chains for eNOEs-guided multiple conformers.
    """

    _polySeq = None

    if polySeq is not None:
        _polySeq = copy.copy(polySeq)

        for ps in polySeq:
            if ps['auth_chain_id'] in modelChainIdExt:
                for dstChainId in modelChainIdExt[ps['auth_chain_id']]:
                    if not any(ps for ps in polySeq if ps['auth_chain_id'] == dstChainId):
                        _ps = copy.copy(ps)
                        _ps['chain_id'] = _ps['auth_chain_id'] = dstChainId
                        _polySeq.append(_ps)

    _altPolySeq = None

    if altPolySeq is not None:
        _altPolySeq = copy.copy(altPolySeq)

        for ps in altPolySeq:
            if ps['auth_chain_id'] in modelChainIdExt:
                for dstChainId in modelChainIdExt[ps['auth_chain_id']]:
                    if not any(ps for ps in altPolySeq if ps['auth_chain_id'] == dstChainId):
                        _ps = copy.copy(ps)
                        _ps['chain_id'] = _ps['auth_chain_id'] = dstChainId
                        _altPolySeq.append(_ps)

    _coordAtomSite = None

    if coordAtomSite is not None:
        _coordAtomSite = copy.copy(coordAtomSite)

        for ps in polySeq:
            srcChainId = ps['auth_chain_id']
            if srcChainId in modelChainIdExt:
                for dstChainId in modelChainIdExt[ps['auth_chain_id']]:
                    for seqId in ps['auth_seq_id']:
                        seqKey = (srcChainId, seqId)
                        if seqKey in _coordAtomSite:
                            _seqKey = (dstChainId, seqId)
                            if _seqKey not in _coordAtomSite:
                                _coordAtomSite[_seqKey] = coordAtomSite[seqKey]

    _coordUnobsRes = None

    if coordUnobsRes is not None:
        _coordUnobsRes = copy.copy(coordUnobsRes)

        for ps in polySeq:
            srcChainId = ps['auth_chain_id']
            if srcChainId in modelChainIdExt:
                for dstChainId in modelChainIdExt[ps['auth_chain_id']]:
                    for seqId in ps['auth_seq_id']:
                        seqKey = (srcChainId, seqId)
                        if seqKey in coordUnobsRes:
                            _seqKey = (dstChainId, seqId)
                            if _seqKey not in _coordUnobsRes:
                                _coordUnobsRes[_seqKey] = coordUnobsRes[seqKey]

    _authToLabelSeq = None
    _labelToAuthSeq = None

    if authToLabelSeq is not None:
        _authToLabelSeq = copy.copy(authToLabelSeq)

        for ps in polySeq:
            srcChainId = ps['auth_chain_id']
            if srcChainId in modelChainIdExt:
                for dstChainId in modelChainIdExt[ps['auth_chain_id']]:
                    for seqId in ps['auth_seq_id']:
                        seqKey = (srcChainId, seqId)
                        if seqKey in authToLabelSeq:
                            seqVal = authToLabelSeq[seqKey]
                            _seqKey = (dstChainId, seqId)
                            if _seqKey not in _authToLabelSeq:
                                _authToLabelSeq[_seqKey] = (dstChainId, seqVal[1])

        _labelToAuthSeq = {v: k for k, v in _authToLabelSeq.items()}

    if authToStarSeq is not None:
        _authToStarSeq = copy.copy(authToStarSeq)

        maxAsmEntityId = max(item[0] for item in authToStarSeq.values()) + 1
        asmEntityIdExt = {}

        for ps in polySeq:
            srcChainId = ps['auth_chain_id']
            if srcChainId in modelChainIdExt:
                for dstChainId in modelChainIdExt[ps['auth_chain_id']]:
                    if dstChainId in asmEntityIdExt:
                        continue
                    asmEntityIdExt[dstChainId] = maxAsmEntityId
                    maxAsmEntityId += 1

        for ps in polySeq:
            srcChainId = ps['auth_chain_id']
            if srcChainId in modelChainIdExt:
                for dstChainId in modelChainIdExt[ps['auth_chain_id']]:
                    dstAsmEntityId = asmEntityIdExt[dstChainId]
                    for seqId, compId in zip(ps['auth_seq_id'], ps['comp_id']):
                        seqKey = (srcChainId, seqId, compId)
                        if seqKey in authToStarSeq:
                            seqVal = authToStarSeq[seqKey]
                            _seqKey = (dstChainId, seqId, compId)
                            if _seqKey not in _authToStarSeq:
                                _authToStarSeq[_seqKey] = (dstAsmEntityId, seqVal[1], seqVal[2], seqVal[3])

    _authToOrigSeq = None

    if authToOrigSeq is not None:
        _authToOrigSeq = copy.copy(authToOrigSeq)

        maxAsmEntityId = max(item[0] for item in authToOrigSeq.values()) + 1
        asmEntityIdExt = {}

        for ps in polySeq:
            srcChainId = ps['auth_chain_id']
            if srcChainId in modelChainIdExt:
                for dstChainId in modelChainIdExt[ps['auth_chain_id']]:
                    if dstChainId in asmEntityIdExt:
                        continue
                    asmEntityIdExt[dstChainId] = maxAsmEntityId
                    maxAsmEntityId += 1

        for ps in polySeq:
            srcChainId = ps['auth_chain_id']
            if srcChainId in modelChainIdExt:
                for dstChainId in modelChainIdExt[ps['auth_chain_id']]:
                    dstAsmEntityId = asmEntityIdExt[dstChainId]
                    for seqId, compId in zip(ps['auth_seq_id'], ps['comp_id']):
                        seqKey = (srcChainId, seqId, compId)
                        if seqKey in authToOrigSeq:
                            seqVal = authToOrigSeq[seqKey]
                            _seqKey = (dstChainId, seqId, compId)
                            if _seqKey not in _authToOrigSeq:
                                _authToOrigSeq[_seqKey] = seqVal

    return _polySeq, _altPolySeq, _coordAtomSite, _coordUnobsRes, _labelToAuthSeq, _authToLabelSeq, _authToStarSeq, _authToOrigSeq


def isIdenticalRestraint(atoms: List[dict], nefT=None) -> bool:
    """ Return whether restraint contains identical atom selection.
    """

    try:

        for a1, a2 in itertools.combinations(atoms, 2):
            if a1['chain_id'] == a2['chain_id'] and a1['seq_id'] == a2['seq_id']:
                atomId1 = a1['atom_id']
                atomId2 = a2['atom_id']
                if atomId1 == atomId2:
                    return True
                if nefT is not None:
                    compId = a1['comp_id']
                    _atomId1, _, _ = nefT.get_valid_star_atom(compId, atomId1)
                    _atomId2, _, _ = nefT.get_valid_star_atom(compId, atomId2)
                    for atomId1 in _atomId1:
                        if atomId1 in _atomId2:
                            return True
                    for atomId2 in _atomId2:
                        if atomId2 in _atomId1:
                            return True

    except KeyError:
        pass

    return False


def isLongRangeRestraint(atoms: List[dict], polySeq: Optional[List[dict]] = None) -> bool:
    """ Return whether restraint is neither an intra residue nor sequential residue restraint.
    """

    seqIds = [a['seq_id'] for a in atoms]

    if any(seqId is None for seqId in seqIds):
        return False

    chainIds = [a['chain_id'] for a in atoms]

    if len(collections.Counter(chainIds).most_common()) > 1:
        return True

    commonSeqId = collections.Counter(seqIds).most_common()

    if len(commonSeqId) == 1:
        return False

    for s1, s2 in itertools.combinations(commonSeqId, 2):
        if abs(s1[0] - s2[0]) > 1:
            if polySeq is None:
                return True

            # verify with label_seq_id scheme

            try:

                ps = next(ps for ps in polySeq if ps['auth_chain_id'] == chainIds[0])

                _seqIds = [ps['seq_id'][ps['auth_seq_id'].index(a['seq_id'])] for a in atoms]
                _commonSeqId = collections.Counter(_seqIds).most_common()
                for _s1, _s2 in itertools.combinations(_commonSeqId, 2):
                    if abs(_s1[0] - _s2[0]) > 1:
                        return True

            except Exception:
                return True

    return False


def getAltProtonIdInBondConstraint(atoms: List[dict], csStat) -> Tuple[Optional[str], Optional[str]]:
    """ Return alternative atom_id in swappable proton group, which involves in bond constraint (e.g. amino group in Watson-Crick pair).
        @return: alternative atom_id for the first atom, alternative atom_id for the second atom
    """

    if len(atoms) < 2:
        return None, None

    if any(a is None for a in atoms):
        return None, None

    for a in atoms:
        if 'chain_id' not in a or a['chain_id'] in emptyValue:
            return None, None
        if 'comp_id' not in a or a['comp_id'] in emptyValue:
            return None, None
        if 'atom_id' not in a or a['atom_id'] in emptyValue:
            return None, None

    chainIds = [a['chain_id'] for a in atoms]

    if len(collections.Counter(chainIds).most_common()) == 1:
        return None, None

    compId1 = atoms[0]['comp_id']
    compId2 = atoms[1]['comp_id']

    atomId1 = atoms[0]['atom_id']
    atomId2 = atoms[1]['atom_id']

    if atomId1[0] in protonBeginCode and atomId2[0] not in protonBeginCode:

        ambigCode1 = csStat.getMaxAmbigCodeWoSetId(compId1, atomId1)

        if ambigCode1 not in (2, 3):
            return None, None

        return csStat.getGeminalAtom(compId1, atomId1), None

    if atomId2[0] in protonBeginCode and atomId1[0] not in protonBeginCode:

        ambigCode2 = csStat.getMaxAmbigCodeWoSetId(compId2, atomId2)

        if ambigCode2 not in (2, 3):
            return None, None

        return None, csStat.getGeminalAtom(compId2, atomId2)

    return None, None


def isAsymmetricRangeRestraint(atoms: List[dict], chainIdSet: List[str], symmetric: str) -> bool:
    """ Return whether restraint is asymmetric.
    """

    lenAtoms = len(atoms)

    if len(set((frozenset(atom.items()) for atom in atoms))) != lenAtoms:  # reject identical atom
        return True

    lenChainIdSet = len(chainIdSet)

    chainIds = [a['chain_id'] for a in atoms]
    indices = [chainIdSet.index(c) for c in chainIds]

    for pos, index in enumerate(indices):
        if pos == lenAtoms - 1:
            break
        if index + 1 < lenChainIdSet:
            nextIndex = index + 1
        elif symmetric == 'circular':
            nextIndex = 0
        else:
            return True
        if indices[pos + 1] != nextIndex:
            return True

    seqIds = [a['seq_id'] for a in atoms]

    if any(seqId is None for seqId in seqIds):
        return False

    commonSeqId = collections.Counter(seqIds).most_common()

    if len(commonSeqId) == 1:
        return False

    for s1, s2 in itertools.combinations(commonSeqId, 2):
        if abs(s1[0] - s2[0]) > 1:
            return True

    return False


def guessCompIdFromAtomId(atomIds: List[str], polySeq: List[dict], nefT) -> List[str]:
    """ Try to find candidate comp_ids that matche with a given atom_id.
    """

    if atomIds[0] in ('C', 'CA', 'CB', 'CO', 'H', 'HN', 'HA', 'N', 'O',
                      "C1'", "C2'", "C3'", "C4'", "C5'", "H1'", "H2'", "H2''", "H3'", "H4'", "H5'", "H5''",
                      "H5'1", "H5'2", "H2'1", "H2'2", "HO2'", "H2'1", "HO'2", 'P', "O2'",
                      'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'H1', 'H2', 'H3', 'H4', 'H5', 'H61', 'H62'):
        return None

    candidates = set()

    for ps in polySeq:
        compIds = ps['comp_id']

        for _compId in set(compIds):
            if _compId in monDict3 or _compId == 'ACE':  # 2jw1: avoid early conclusion of GLY assignemt when ACE is in polymer
                _atomId = atomIds[0]
                if _atomId in emptyValue:
                    return None
                if _compId not in monDict3:
                    _atomId = translateToStdAtomName(_atomId, _compId, ccU=nefT.get_ccu())
                _atomId, _, details = nefT.get_valid_star_atom_in_xplor(_compId, _atomId)
                if len(_atomId) > 0 and details is None:
                    candidates.add(_compId)
                    if len(candidates) > 2:
                        return None

    return list(candidates)


def guessCompIdFromAtomIdWoLimit(atomIds: List[str], polySeq: List[dict], nefT, isPolySeq: bool = True) -> List[str]:
    """ Try to find candidate comp_ids that matche with a given atom_id.
    """

    candidates = set()

    for ps in polySeq:
        compIds = ps['comp_id']

        for _compId in set(compIds):
            if _compId in monDict3 or _compId == 'ACE' or not isPolySeq:  # 2jw1: avoid early conclusion of GLY assignemt when ACE is in polymer
                failed = False
                for atomId in atomIds:
                    if atomId in emptyValue:
                        break
                    _atomId = translateToStdAtomName(atomId, _compId, ccU=nefT.get_ccu())
                    _atomId, _, details = nefT.get_valid_star_atom_in_xplor(_compId, _atomId)
                    if len(_atomId) == 0 or details is not None:
                        failed = True
                        break
                if not failed:
                    candidates.add(_compId)

    return list(candidates)


def hasIntraChainRestraint(atomSelectionSet: List[List[dict]]) -> Tuple[bool, Optional[set]]:
    """ Return whether intra-chain distance restraints in the atom selection.
        @return: whether intra-chain distrance restraints, representative set of chain_id
    """

    for atom1, atom2 in itertools.product(atomSelectionSet[0],
                                          atomSelectionSet[1]):
        if atom1['chain_id'] == atom2['chain_id']:
            return True, getRepIntraChainIds(atomSelectionSet)

    return False, None


def hasInterChainRestraint(atomSelectionSet: List[List[dict]]) -> bool:
    """ Return whether inter-chain distance restraints in the atom selection.
    """

    for atom1, atom2 in itertools.product(atomSelectionSet[0],
                                          atomSelectionSet[1]):
        if atom1['chain_id'] != atom2['chain_id']:
            return True

    return False


def getRepIntraChainIds(atomSelectionSet: List[List[dict]]) -> set:
    """ Return representative set of chain id of intra-chain distance restraints in case of large assembly.
    """

    intraChainIds = set()
    for atom1, atom2 in itertools.product(atomSelectionSet[0],
                                          atomSelectionSet[1]):
        if atom1['chain_id'] == atom2['chain_id']:
            intraChainIds.add(atom1['chain_id'])

    if len(intraChainIds) > MAX_MAG_IDENT_ASYM_ID:
        for chainId in LARGE_ASYM_ID:
            if chainId in intraChainIds:
                return {chainId}

    return intraChainIds


def isAmbigAtomSelection(atoms: List[dict], csStat) -> bool:
    """ Return whether an atom selection involves heterogeneous atom groups.
    """

    if len(atoms) < 2:
        return False

    if any(a is None for a in atoms):
        return False

    for a in atoms:
        if 'chain_id' not in a or a['chain_id'] in emptyValue:
            return True
        if 'seq_id' not in a or a['seq_id'] in emptyValue:
            return True
        if 'comp_id' not in a or a['comp_id'] in emptyValue:
            return True
        if 'atom_id' not in a or a['atom_id'] in emptyValue:
            return True

    chainIds = [a['chain_id'] for a in atoms]

    if len(collections.Counter(chainIds).most_common()) > 1:
        return True

    seqIds = [a['seq_id'] for a in atoms]

    if any(seqId is None for seqId in seqIds):
        return False

    commonSeqId = collections.Counter(seqIds).most_common()

    if len(commonSeqId) > 1:
        return True

    atomIds = list(set(a['atom_id'] for a in atoms))

    commonAtomId = collections.Counter(atomIds).most_common()

    if len(commonAtomId) == 1:
        return False

    atomId0 = atomIds[0]
    compId = atoms[0]['comp_id']

    _protonsInGroup = csStat.getProtonsInSameGroup(compId, atomId0, True)
    geminalAtom = csStat.getGeminalAtom(compId, atomId0)

    if geminalAtom is not None:

        if atomId0[0] not in protonBeginCode:
            if set(atomIds) == {atomId0, geminalAtom}:
                return False

        if _protonsInGroup is not None:
            _protonsInGroup.append(geminalAtom)
        else:
            _protonsInGroup = [geminalAtom]

        geminalProtonsInGroup = csStat.getProtonsInSameGroup(compId, geminalAtom, True)
        if geminalProtonsInGroup is not None and len(geminalProtonsInGroup) > 0:
            _protonsInGroup.extend(geminalProtonsInGroup)

    if _protonsInGroup is None or len(_protonsInGroup) == 0:
        return True

    for atomId in atomIds[1:]:
        if atomId not in _protonsInGroup:
            return True

    return False


def getTypeOfDihedralRestraint(polypeptide: bool, polynucleotide: bool, carbohydrates: bool,
                               atoms: List[dict], planeLike: bool,
                               cR=None, ccU=None,
                               representativeModelId: int = REPRESENTATIVE_MODEL_ID,
                               representativeAltId: str = REPRESENTATIVE_ALT_ID,
                               modelNumName: str = 'PDB_model_num') -> Optional[str]:
    """ Return type of dihedral angle restraint.
    """

    seqIds = [a['seq_id'] for a in atoms]

    if any(seqId is None for seqId in seqIds) or any('atom_id' not in a for a in atoms):
        return None

    chainIds = [a['chain_id'] for a in atoms]
    atomIds = [a['atom_id'] for a in atoms]

    # DAOTHER-9063: permit dihedral angle restraint across entities due to ligand split
    def is_connected():
        if None in (cR, ccU):
            return False
        for idx, atom2 in enumerate(atoms):
            if idx == 0:
                continue
            atom1 = atoms[idx - 1]
            if atom1['chain_id'] == atom2['chain_id'] and atom1['seq_id'] == atom2['seq_id']\
               and ccU.hasBond(atom1['comp_id'], atom1['atom_id'], atom2['atom_id']):
                continue
            if not isStructConn(cR, atom1['chain_id'], atom1['seq_id'], atom1['atom_id'],
                                atom2['chain_id'], atom2['seq_id'], atom2['atom_id'],
                                representativeModelId, representativeAltId, modelNumName):
                return False
        return True

    commonChainId = collections.Counter(chainIds).most_common()

    lenCommonChainId = len(commonChainId)

    if lenCommonChainId > 1 and not planeLike:
        return None  # '.' if is_connected() else None

    commonSeqId = collections.Counter(seqIds).most_common()

    lenCommonSeqId = len(commonSeqId)

    if polypeptide:

        if lenCommonSeqId == 2:

            phiPsiCommonAtomIds = ['N', 'CA', 'C']

            # PHI or PSI
            if commonSeqId[0][1] == 3 and commonSeqId[1][1] == 1:

                # PHI
                prevSeqId = commonSeqId[1][0]

                if commonSeqId[0][0] == prevSeqId + 1:

                    j = 0
                    if seqIds[j] == prevSeqId and atomIds[j] == 'C':
                        atomIds.pop(j)
                        if atomIds == phiPsiCommonAtomIds:
                            return 'PHI'

                # PSI
                nextSeqId = commonSeqId[1][0]

                if commonSeqId[0][0] == nextSeqId - 1:

                    j = 3
                    if seqIds[j] == nextSeqId and atomIds[j] == 'N':
                        atomIds.pop(j)
                        if atomIds == phiPsiCommonAtomIds:
                            return 'PSI'

            if atomIds == ['C', 'N', 'CA', 'C']:  # i-1, i, i, i
                if seqIds[0] + 1 == seqIds[3] and (abs(seqIds[1] - seqIds[3]) == 1 or abs(seqIds[2] - seqIds[3]) == 1):
                    return f'pseudo PHI (0, {seqIds[3] - seqIds[1]}, {seqIds[3] - seqIds[2]}, 0)'

            if atomIds == ['N', 'CA', 'C', 'N']:  # i, i, i, i+1
                if seqIds[0] + 1 == seqIds[3] and (abs(seqIds[1] - seqIds[0]) == 1 or abs(seqIds[2] - seqIds[0]) == 1):
                    return f'pseudo PSI (0, {seqIds[0] - seqIds[1]}, {seqIds[0] - seqIds[2]}, 0)'

            # OMEGA
            if atomIds[0] == 'CA' and atomIds[1] == 'N' and atomIds[2] == 'C' and atomIds[3] == 'CA'\
               and seqIds[0] == seqIds[1] and seqIds[1] - 1 == seqIds[2] and seqIds[2] == seqIds[3]:
                return 'OMEGA'

            if atomIds[0] == 'CA' and atomIds[1] == 'C' and atomIds[2] == 'N' and atomIds[3] == 'CA'\
               and seqIds[0] == seqIds[1] and seqIds[1] + 1 == seqIds[2] and seqIds[2] == seqIds[3]:
                return 'OMEGA'

            if atomIds in (['CA', 'N', 'C', 'CA'], ['CA', 'C', 'N', 'CA']):  # i, i, i+1, i+1
                if abs(seqIds[0] - seqIds[3]) == 1 and (abs(seqIds[1] - seqIds[0]) == 1 or abs(seqIds[2] - seqIds[3]) == 1):
                    return f'pseudo OMEGA (0, {seqIds[0] - seqIds[1]}, {seqIds[3] - seqIds[2]}, 0)'

            # OMEGA - modified CYANA definition
            if atomIds[0] == 'O' and atomIds[1] == 'C' and atomIds[2] == 'N'\
               and (atomIds[3] == 'H' or atomIds[3] == 'CD')\
               and seqIds[0] == seqIds[1] and seqIds[1] + 1 == seqIds[2] and seqIds[2] == seqIds[3]:
                return 'OMEGA'

            if atomIds in (['O', 'C', 'N', 'H'], ['O', 'C', 'N', 'CD']):  # i, i, i+1, i+1
                if seqIds[0] + 1 == seqIds[3] and (abs(seqIds[1] - seqIds[0]) == 1 or abs(seqIds[2] - seqIds[3]) == 1):
                    return f'pseudo OMEGA (0, {seqIds[0] - seqIds[1]}, {seqIds[3] - seqIds[2]}, 0)'

        elif lenCommonSeqId == 1:

            testDataType = ['CHI1', 'CHI2', 'CHI3', 'CHI4', 'CHI5',
                            'CHI21', 'CHI22', 'CHI31', 'CHI32', 'CHI42']

            for dataType in testDataType:

                found = True

                for atomId, angAtomId in zip(atomIds, KNOWN_ANGLE_ATOM_NAMES[dataType]):

                    if isinstance(angAtomId, str):
                        if atomId != angAtomId:
                            found = False
                            break

                    else:
                        if not angAtomId.match(atomId):
                            found = False
                            break

                if found:
                    return dataType

        testDataType = ['PHI', 'PSI', 'OMEGA',
                        'CHI1', 'CHI2', 'CHI3', 'CHI4', 'CHI5',
                        'CHI21', 'CHI22', 'CHI31', 'CHI32', 'CHI42']

        for dataType in testDataType:

            found = True

            for atomId, angAtomId in zip(atomIds, KNOWN_ANGLE_ATOM_NAMES[dataType]):

                if isinstance(angAtomId, str):
                    if atomId != angAtomId:
                        found = False
                        break

                else:
                    if not angAtomId.match(atomId):
                        found = False
                        break

            if found and not planeLike:
                return '.' if is_connected() else None

    elif polynucleotide:

        if lenCommonSeqId == 3:

            # ETA or ETA'
            _seqIds = [s - o for s, o in zip(seqIds, KNOWN_ANGLE_SEQ_OFFSET['ETA'])]
            _commonSeqId = collections.Counter(_seqIds).most_common()

            if len(_commonSeqId) == 1:

                testDataType = ['ETA', "ETA'"]

                for dataType in testDataType:

                    found = True

                    for atomId, angAtomId in zip(atomIds, KNOWN_ANGLE_ATOM_NAMES[dataType]):

                        if atomId != angAtomId:
                            found = False
                            break

                    if found:
                        return dataType

        elif lenCommonSeqId == 2:

            # ALPHA or EPSILON or ZETA or THETA or or THETA'
            testDataType = ['ALPHA', 'EPSILON', 'ZETA', 'THETA', "THETA'"]

            for dataType in testDataType:
                _seqIds = [s - o for s, o in zip(seqIds, KNOWN_ANGLE_SEQ_OFFSET[dataType])]
                _commonSeqId = collections.Counter(_seqIds).most_common()

                if len(_commonSeqId) == 1:

                    found = True

                    for atomId, angAtomId in zip(atomIds, KNOWN_ANGLE_ATOM_NAMES[dataType]):

                        if atomId != angAtomId:
                            found = False
                            break

                    if found:
                        return dataType

        elif lenCommonSeqId == 1:

            if 'N1' in atomIds:

                found = True

                for atomId, angAtomId in zip(atomIds, KNOWN_ANGLE_ATOM_NAMES['CHI']['Y']):

                    if atomId != angAtomId:
                        found = False
                        break

                if found:
                    return 'CHI'

            elif 'N9' in atomIds:

                found = True

                for atomId, angAtomId in zip(atomIds, KNOWN_ANGLE_ATOM_NAMES['CHI']['R']):

                    if atomId != angAtomId:
                        found = False
                        break

                if found:
                    return 'CHI'

            else:

                # BETA or GAMMA or DELTA or NU0 or NU1 or NU2 or NU4
                testDataType = ['BETA', 'GAMMA', 'DELTA', 'NU0', 'NU1', 'NU2', 'NU3', 'NU4']

                for dataType in testDataType:

                    found = True

                    for atomId, angAtomId in zip(atomIds, KNOWN_ANGLE_ATOM_NAMES[dataType]):

                        if atomId != angAtomId:
                            found = False
                            break

                    if found:
                        return dataType

        testDataType = ['ETA', "ETA'",
                        'ALPHA', 'EPSILON', 'ZETA', 'THETA', "THETA'",
                        'BETA', 'GAMMA', 'DELTA', 'NU0', 'NU1', 'NU2', 'NU3', 'NU4']

        for dataType in testDataType:

            found = True

            for atomId, angAtomId in zip(atomIds, KNOWN_ANGLE_ATOM_NAMES[dataType]):

                if isinstance(angAtomId, str):
                    if atomId != angAtomId:
                        found = False
                        break

                else:
                    if not angAtomId.match(atomId):
                        found = False
                        break

            if found and not planeLike:
                return '.' if is_connected() else None

        if 'N1' in atomIds:

            found = True

            for atomId, angAtomId in zip(atomIds, KNOWN_ANGLE_ATOM_NAMES['CHI']['Y']):

                if atomId != angAtomId:
                    found = False
                    break

            if found and not planeLike:
                return '.' if is_connected() else None

        elif 'N9' in atomIds:

            found = True

            for atomId, angAtomId in zip(atomIds, KNOWN_ANGLE_ATOM_NAMES['CHI']['R']):

                if atomId != angAtomId:
                    found = False
                    break

            if found and not planeLike:
                return '.' if is_connected() else None

    elif carbohydrates:

        if lenCommonSeqId == 2:

            # PHI or PSI or OMEGA
            testDataType = ['PHI', 'PSI', 'OMEGA']

            for dataType in testDataType:
                seqId1 = seqIds[0]
                seqId4 = seqIds[3]

                if seqId1 > seqId4:
                    m = seqId1 - seqId4
                    _seqIds = [s - o * m for s, o in zip(seqIds, KNOWN_ANGLE_CARBO_SEQ_OFFSET[dataType])]
                    _commonSeqId = collections.Counter(_seqIds).most_common()

                    if len(_commonSeqId) == 1:

                        found = True

                        for atomId, angAtomId in zip(atomIds, KNOWN_ANGLE_CARBO_ATOM_NAMES[dataType]):

                            if isinstance(angAtomId, str):
                                if atomId != angAtomId:
                                    found = False
                                    break

                            else:
                                if not angAtomId.match(atomId):
                                    found = False
                                    break

                        if found:
                            return dataType

        testDataType = ['PHI', 'PSI', 'OMEGA']

        for dataType in testDataType:

            found = True

            for atomId, angAtomId in zip(atomIds, KNOWN_ANGLE_CARBO_ATOM_NAMES[dataType]):

                if isinstance(angAtomId, str):
                    if atomId != angAtomId:
                        found = False
                        break

                else:
                    if not angAtomId.match(atomId):
                        found = False
                        break

            if found and not planeLike:
                return '.' if is_connected() else None

    if planeLike and ccU is not None:

        if lenCommonChainId == 1 and lenCommonSeqId == 1:
            compId = atoms[0]['comp_id']
            if ccU.updateChemCompDict(compId):
                ring = True
                for a in atoms:
                    atomId = a['atom_id']
                    cca = next((cca for cca in ccU.lastAtomList if cca[ccU.ccaAtomId] == atomId), None)
                    if cca is None or cca[ccU.ccaAromaticFlag] != 'Y':
                        bonded = ccU.getBondedAtoms(compId, atomId, exclProton=True)
                        attach = False
                        for b in bonded:
                            _cca = next((_cca for _cca in ccU.lastAtomList if _cca[ccU.ccaAtomId] == b), None)
                            if _cca is not None:
                                if _cca[ccU.ccaAromaticFlag] == 'Y':
                                    attach = True
                        if not attach:
                            ring = False
                            break
                if ring:
                    return 'RING'

        if atoms[0]['chain_id'] == atoms[1]['chain_id'] and atoms[0]['seq_id'] == atoms[1]['seq_id']\
           and atoms[2]['chain_id'] == atoms[3]['chain_id'] and atoms[2]['seq_id'] == atoms[3]['seq_id']:

            if all(a['atom_id'][0] not in protonBeginCode for a in atoms):
                aroma = True
                for a in atoms:
                    compId = a['comp_id']
                    atomId = a['atom_id']
                    if ccU.updateChemCompDict(compId):
                        cca = next((cca for cca in ccU.lastAtomList if cca[ccU.ccaAtomId] == atomId), None)
                        if cca is None:
                            aroma = False
                            break
                        if cca[ccU.ccaAromaticFlag] != 'Y':
                            if ccU.getTypeOfCompId(compId)[1] and atomId[0] in ('C', 'N') and not atomId.endswith("'"):
                                continue
                            bonded = ccU.getBondedAtoms(compId, atomId, exclProton=True)
                            attach = False
                            for b in bonded:
                                _cca = next((_cca for _cca in ccU.lastAtomList if _cca[ccU.ccaAtomId] == b), None)
                                if _cca is not None:
                                    if _cca[ccU.ccaAromaticFlag] == 'Y':
                                        attach = True
                            if not attach:
                                aroma = False
                                break
                if aroma:
                    return 'PLANE'

            if ccU.hasBond(atoms[0]['comp_id'], atoms[0]['atom_id'], atoms[1]['atom_id'])\
               and ccU.hasBond(atoms[2]['comp_id'], atoms[2]['atom_id'], atoms[3]['atom_id']):
                return 'ALIGN'

    return '.' if is_connected() else None


def fixBackboneAtomsOfDihedralRestraint(angleName: str, atoms: List[dict], currentRestraint: str) -> Tuple[str, dict, dict, str]:
    """ Return valid dihedral angle name and remediated protein backbone atoms.
        @return: dihedral angle name,
                 remediated atom_id for the second atom,
                 remediated atom_id for the third atom,
                 message for the remediation ('' for valid dihedral angle restraint)
    """

    msg = ''

    if REMEDIATE_BACKBONE_ANGLE_NAME_PAT.match(angleName):
        g = REMEDIATE_BACKBONE_ANGLE_NAME_PAT.search(angleName).groups()

        angleName = g[0]
        offset1 = int(g[1])
        offset2 = int(g[2])

        atomName0 = f"{atoms[0]['seq_id']}:{atoms[0]['comp_id']}:{atoms[0]['atom_id']}"
        atomName1 = f"{atoms[1]['seq_id']}:{atoms[1]['comp_id']}:{atoms[1]['atom_id']}"
        atomName2 = f"{atoms[2]['seq_id']}:{atoms[2]['comp_id']}:{atoms[2]['atom_id']}"
        atomName3 = f"{atoms[3]['seq_id']}:{atoms[3]['comp_id']}:{atoms[3]['atom_id']}"

        msg = f"[Inconsistent dihedral angle atoms] {currentRestraint}"\
              f"The original dihedral angle irregularly composed of "\
              f"{atomName0}-{atomName1}-{atomName2}-{atomName3} was "

        if offset1 != 0:
            seq_id1 = atoms[1]['seq_id'] + offset1
            for idx, a in enumerate(atoms):
                if idx == 1:
                    continue
                if a['seq_id'] == seq_id1:
                    atoms[1]['chain_id'] = a['chain_id']
                    atoms[1]['seq_id'] = a['seq_id']
                    atoms[1]['comp_id'] = a['comp_id']
                    atomName1 = f"{atoms[1]['seq_id']}:{atoms[1]['comp_id']}:{atoms[1]['atom_id']}"
                    break

        if offset2 != 0:
            seq_id2 = atoms[2]['seq_id'] + offset2
            for idx, a in enumerate(atoms):
                if idx == 2:
                    continue
                if a['seq_id'] == seq_id2:
                    atoms[2]['chain_id'] = a['chain_id']
                    atoms[2]['seq_id'] = a['seq_id']
                    atoms[2]['comp_id'] = a['comp_id']
                    atomName2 = f"{atoms[2]['seq_id']}:{atoms[2]['comp_id']}:{atoms[2]['atom_id']}"
                    break

        msg += f"translated to well-known {angleName!r} angle composed of "\
               f"{atomName0}-{atomName1}-{atomName2}-{atomName3}."

    return angleName, atoms[1], atoms[2], msg


def isLikePheOrTyr(compId: str, ccU) -> bool:
    """ Return whether a given comp_id is amino acid with flippable symmetrical ring like phenylalanine or tryrosine.
    """

    if compId in ('PHE', 'TYR'):
        return True

    if compId in monDict3:
        return False

    if ccU.updateChemCompDict(compId):
        _refAtomIdList = [cca[ccU.ccaAtomId] for cca in ccU.lastAtomList]
        if 'CD1' not in _refAtomIdList or 'CD2' not in _refAtomIdList:
            return False
        _compId = ccU.lastChemCompDict.get('_chem_comp.mon_nstd_parent_comp_id', '?')
        return _compId in ('PHE', 'TYR')

    return False


def isLikeHis(compId: str, ccU) -> bool:
    """ Return whether a given comp_id is like histigine.
    """

    if compId == 'HIS':
        return True

    if compId in monDict3:
        return False

    if ccU.updateChemCompDict(compId):
        _refAtomIdList = [cca[ccU.ccaAtomId] for cca in ccU.lastAtomList]
        if 'ND1' not in _refAtomIdList or 'NE2' not in _refAtomIdList:
            return False
        _compId = ccU.lastChemCompDict.get('_chem_comp.mon_nstd_parent_comp_id', '?')
        return _compId == 'HIS'

    return False


def getRdcCode(atoms: List[dict]) -> Optional[str]:
    """ Return type of residual dipolar coupling restraint.
    """

    if len(atoms) != 2:
        return None

    if any(a is None for a in atoms):
        return None

    atom1 = atoms[0]
    atom2 = atoms[1]

    chain_id_1 = atom1['chain_id']
    chain_id_2 = atom2['chain_id']
    seq_id_1 = atom1['seq_id']
    seq_id_2 = atom2['seq_id']
    atom_id_1 = atom1['atom_id']
    atom_id_2 = atom2['atom_id']

    vector = {atom_id_1, atom_id_2}
    offset = abs(seq_id_1 - seq_id_2)

    if chain_id_1 == chain_id_2:
        if vector == {'H', 'C'} and offset == 1:
            return 'RDC_HNC'
        if vector == {'H', 'N'} and offset == 0:
            return 'RDC_NH'
        if vector == {'C', 'N'} and offset == 1:
            return 'RDC_CN_i_1'
        if vector == {'CA', 'HA'} and offset == 0:
            return 'RDC_CAHA'
        if vector == {'H', 'HA'} and offset == 0:
            return 'RDC_HNHA'
        if vector == {'H', 'HA'} and offset == 1:
            return 'RDC_HNHA_i_1'
        if vector == {'CA', 'C'} and offset == 0:
            return 'RDC_CAC'
        if vector == {'CA', 'N'} and offset == 0:
            return 'RDC_CAN'
        if atom_id_1[0] == atom_id_2[0]:
            if atom_id_1[0] in protonBeginCode:
                return 'RDC_HH'
            if atom_id_1[0] == 'C':
                return 'RDC_CC'
        if offset == 0:
            if atom1['comp_id'] == 'TRP' and vector == {'HE1', 'NE1'}:
                return 'RDC_NH'
            if atom1['comp_id'] == 'ARG' and vector == {'HE', 'NE'}:
                return 'RDC_NH'

    return 'RDC_other'


def startsWithPdbRecord(line: str, ignoreRemark: bool = False) -> bool:
    """ Return whether a given line string starts with legacy PDB records.
    """

    PDB_RECORDS = LEGACY_PDB_RECORDS_WO_REMARK if ignoreRemark else LEGACY_PDB_RECORDS

    if any(line.startswith(pdb_record) for pdb_record in PDB_RECORDS):
        return True

    return any(line[:-1] == pdb_record[:-1] for pdb_record in PDB_RECORDS if pdb_record.endswith(' '))


def isCyclicPolymer(cR, polySeq: List[dict], authAsymId: str,
                    representativeModelId: int = REPRESENTATIVE_MODEL_ID,
                    representativeAltId: str = REPRESENTATIVE_ALT_ID,
                    modelNumName: str = 'PDB_model_num') -> bool:
    """ Return whether a given chain is cyclic polymer based on coordinate annotation.
    """

    if None in (cR, polySeq):
        return False

    ps = next((ps for ps in polySeq if ps['auth_chain_id'] == authAsymId), None)

    if ps is None:
        return False

    labelAsymId = ps['chain_id']
    authSeqIdList = list(filter(None, ps['auth_seq_id']))
    seq_id_list = list(filter(None, ps['seq_id']))
    begAuthSeqId = min(authSeqIdList)
    endAuthSeqId = max(authSeqIdList)
    begLabelSeqId = min(seq_id_list)
    endLabelSeqId = max(seq_id_list)

    try:

        if cR.hasCategory('struct_conn'):
            filterItems = [{'name': 'ptnr1_label_asym_id', 'type': 'str', 'value': labelAsymId},
                           {'name': 'ptnr2_label_asym_id', 'type': 'str', 'value': labelAsymId},
                           {'name': 'ptnr1_label_seq_id', 'type': 'int', 'value': begLabelSeqId},
                           {'name': 'ptnr2_label_seq_id', 'type': 'int', 'value': endLabelSeqId},
                           ]

            if cR.hasItem('struct_conn', 'pdbx_leaving_atom_flag'):
                filterItems.append({'name': 'pdbx_leaving_atom_flag', 'type': 'str', 'value': 'both'})

            struct_conn = cR.getDictListWithFilter('struct_conn',
                                                   [{'name': 'conn_type_id', 'type': 'str'}],
                                                   filterItems)

        else:
            struct_conn = []

    except Exception:
        return False

    if len(struct_conn) == 0:

        try:

            if cR.hasCategory('pdbx_validate_close_contact'):
                close_contact = cR.getDictListWithFilter('pdbx_validate_close_contact',
                                                         [{'name': 'dist', 'type': 'float'}
                                                          ],
                                                         [{'name': 'PDB_model_num', 'type': 'int', 'value': representativeModelId},
                                                          {'name': 'auth_asym_id_1', 'type': 'str', 'value': authAsymId},
                                                          {'name': 'auth_seq_id_1', 'type': 'int', 'value': begAuthSeqId},
                                                          {'name': 'auth_atom_id_1', 'type': 'str', 'value': 'N'},
                                                          {'name': 'auth_asym_id_2', 'type': 'str', 'value': authAsymId},
                                                          {'name': 'auth_seq_id_2', 'type': 'int', 'value': endAuthSeqId},
                                                          {'name': 'auth_atom_id_2', 'type': 'str', 'value': 'C'}
                                                          ])

            else:
                close_contact = []

        except Exception:
            return False

        if len(close_contact) == 0:

            bond = getCoordBondLength(cR, labelAsymId, begLabelSeqId, 'N', labelAsymId, endLabelSeqId, 'C',
                                      representativeAltId, modelNumName, True)

            if bond is None:
                return False

            distance = next((b['distance'] for b in bond if b['model_id'] == representativeModelId), None)

            if distance is None:
                return False

            return 1.0 < distance < 2.4

        return 1.0 < close_contact[0]['dist'] < 2.4

    return struct_conn[0]['conn_type_id'] == 'covale'


def getStructConnPtnr(cR, authAsymId: str, authSeqId: int, authCompId: str = None) -> Optional[List[dict]]:
    """ Return structually connected partner residues for a given residue.
        @return: list of partner residues for a given residue descrived in struct_conn loop
    """

    if cR is None or not cR.hasCategory('struct_conn'):
        return None

    try:

        filterItems = [{'name': 'ptnr1_auth_asym_id', 'type': 'str', 'value': authAsymId},
                       {'name': 'ptnr1_auth_seq_id', 'type': 'int', 'value': authSeqId}
                       ]
        if authCompId is not None:
            filterItems.append({'name': 'ptnr1_auth_comp_id', 'type': 'str', 'value': authCompId})

        struct_conn = cR.getDictListWithFilter('struct_conn',
                                               [{'name': 'ptnr2_auth_asym_id', 'type': 'str', 'alt_name': 'chain_id'},
                                                {'name': 'ptnr2_auth_seq_id', 'type': 'str', 'alt_name': 'seq_id'},
                                                {'name': 'ptnr2_auth_comp_id', 'type': 'str', 'alt_name': 'comp_id'}],
                                               filterItems)

        filterItems = [{'name': 'ptnr2_auth_asym_id', 'type': 'str', 'value': authAsymId},
                       {'name': 'ptnr2_auth_seq_id', 'type': 'int', 'value': authSeqId}
                       ]
        if authCompId is not None:
            filterItems.append({'name': 'ptnr2_auth_comp_id', 'type': 'str', 'value': authCompId})

        struct_conn.extend(cR.getDictListWithFilter('struct_conn',
                                                    [{'name': 'ptnr1_auth_asym_id', 'type': 'str', 'alt_name': 'chain_id'},
                                                     {'name': 'ptnr1_auth_seq_id', 'type': 'str', 'alt_name': 'seq_id'},
                                                     {'name': 'ptnr1_auth_comp_id', 'type': 'str', 'alt_name': 'comp_id'}],
                                                    filterItems))

        if len(struct_conn) == 0:
            return None

    except Exception:
        return None

    return [dict(s) for s in set(frozenset(sc.items()) for sc in struct_conn if isinstance(sc, dict))]


def getWatsonCrickPtnr(cR, authAsymId: str) -> Optional[List[str]]:
    """ Return list of Watson-Crick partner auth_asym_ids for a given auth_asym_id.
        @return: list of partner auth_asym_ids for a given auth_asym_id by Watson-Crick base paring
    """

    if cR is None or not cR.hasCategory('struct_conn'):
        return None

    try:

        filterItems = [{'name': 'ptnr1_auth_asym_id', 'type': 'str', 'value': authAsymId},
                       {'name': 'details', 'type': 'str', 'value': 'WATSON-CRICK'}
                       ]

        struct_conn = cR.getDictListWithFilter('struct_conn',
                                               [{'name': 'ptnr2_auth_asym_id', 'type': 'str', 'alt_name': 'chain_id'}
                                                ],
                                               filterItems)

        filterItems = [{'name': 'ptnr2_auth_asym_id', 'type': 'str', 'value': authAsymId},
                       {'name': 'details', 'type': 'str', 'value': 'WATSON-CRICK'}
                       ]
        struct_conn.extend(cR.getDictListWithFilter('struct_conn',
                                                    [{'name': 'ptnr1_auth_asym_id', 'type': 'str', 'alt_name': 'chain_id'}
                                                     ],
                                                    filterItems))

        if len(struct_conn) == 0:
            return None

    except Exception:
        return None

    return list(set(sc['chain_id'] for sc in struct_conn))


def getStructConnPtnrAtom(cR, authAsymId: str, authSeqId: int, authAtomId: str) -> Optional[dict]:
    """ Return structually connected partner atom for a given atom.
        @return: dictionary of connected partner atom in struct_conn loop
    """

    if cR is None or not cR.hasCategory('struct_conn'):
        return None

    try:

        filterItems = [{'name': 'ptnr1_auth_asym_id', 'type': 'str', 'value': authAsymId},
                       {'name': 'ptnr1_auth_seq_id', 'type': 'int', 'value': authSeqId},
                       {'name': 'ptnr1_label_atom_id', 'type': 'str', 'value': authAtomId}
                       ]

        struct_conn = cR.getDictListWithFilter('struct_conn',
                                               [{'name': 'ptnr2_auth_asym_id', 'type': 'str', 'alt_name': 'chain_id'},
                                                {'name': 'ptnr2_auth_seq_id', 'type': 'str', 'alt_name': 'seq_id'},
                                                {'name': 'ptnr2_auth_comp_id', 'type': 'str', 'alt_name': 'comp_id'},
                                                {'name': 'ptnr2_label_atom_id', 'type': 'str', 'alt_name': 'atom_id'}],
                                               filterItems)

        if len(struct_conn) == 1:
            return struct_conn[0]

        filterItems = [{'name': 'ptnr2_auth_asym_id', 'type': 'str', 'value': authAsymId},
                       {'name': 'ptnr2_auth_seq_id', 'type': 'int', 'value': authSeqId},
                       {'name': 'ptnr2_label_atom_id', 'type': 'str', 'value': authAtomId}
                       ]

        struct_conn = cR.getDictListWithFilter('struct_conn',
                                               [{'name': 'ptnr1_auth_asym_id', 'type': 'str', 'alt_name': 'chain_id'},
                                                {'name': 'ptnr1_auth_seq_id', 'type': 'str', 'alt_name': 'seq_id'},
                                                {'name': 'ptnr1_auth_comp_id', 'type': 'str', 'alt_name': 'comp_id'},
                                                {'name': 'ptnr1_label_atom_id', 'type': 'str', 'alt_name': 'atom_id'}],
                                               filterItems)

        if len(struct_conn) == 1:
            return struct_conn[0]

    except Exception:
        return None

    return None


def isStructConn(cR, authAsymId1: str, authSeqId1: int, authAtomId1: str,
                 authAsymId2: str, authSeqId2: int, authAtomId2: str,
                 representativeModelId: int = REPRESENTATIVE_MODEL_ID,
                 representativeAltId: str = REPRESENTATIVE_ALT_ID,
                 modelNumName: str = 'PDB_model_num') -> bool:
    """ Return whether a given atom pair is structurally connected.
    """

    if cR is None:
        return False

    try:

        if cR.hasCategory('struct_conn'):
            filterItems = [{'name': 'ptnr1_auth_asym_id', 'type': 'str', 'value': authAsymId1},
                           {'name': 'ptnr2_auth_asym_id', 'type': 'str', 'value': authAsymId2},
                           {'name': 'ptnr1_auth_seq_id', 'type': 'int', 'value': authSeqId1},
                           {'name': 'ptnr2_auth_seq_id', 'type': 'int', 'value': authSeqId2},
                           {'name': 'ptnr1_auth_atom_id', 'type': 'int', 'value': authAtomId1},
                           {'name': 'ptnr2_auth_atom_id', 'type': 'int', 'value': authAtomId2}
                           ]

            struct_conn = cR.getDictListWithFilter('struct_conn',
                                                   [{'name': 'conn_type_id', 'type': 'str'}],
                                                   filterItems)

            if len(struct_conn) == 0:
                filterItems = [{'name': 'ptnr1_auth_asym_id', 'type': 'str', 'value': authAsymId2},
                               {'name': 'ptnr2_auth_asym_id', 'type': 'str', 'value': authAsymId1},
                               {'name': 'ptnr1_auth_seq_id', 'type': 'int', 'value': authSeqId2},
                               {'name': 'ptnr2_auth_seq_id', 'type': 'int', 'value': authSeqId1},
                               {'name': 'ptnr1_auth_atom_id', 'type': 'int', 'value': authAtomId2},
                               {'name': 'ptnr2_auth_atom_id', 'type': 'int', 'value': authAtomId1}
                               ]

                struct_conn = cR.getDictListWithFilter('struct_conn',
                                                       [{'name': 'conn_type_id', 'type': 'str'}],
                                                       filterItems)

        else:
            struct_conn = []

    except Exception:
        return False

    if len(struct_conn) == 0:

        try:

            if cR.hasCategory('pdbx_validate_close_contact'):
                close_contact = cR.getDictListWithFilter('pdbx_validate_close_contact',
                                                         [{'name': 'dist', 'type': 'float'}
                                                          ],
                                                         [{'name': 'PDB_model_num', 'type': 'int', 'value': representativeModelId},
                                                          {'name': 'auth_asym_id_1', 'type': 'str', 'value': authAsymId1},
                                                          {'name': 'auth_seq_id_1', 'type': 'int', 'value': authSeqId1},
                                                          {'name': 'auth_atom_id_1', 'type': 'str', 'value': authAtomId1},
                                                          {'name': 'auth_asym_id_2', 'type': 'str', 'value': authAsymId2},
                                                          {'name': 'auth_seq_id_2', 'type': 'int', 'value': authSeqId2},
                                                          {'name': 'auth_atom_id_2', 'type': 'str', 'value': authAtomId2}
                                                          ])

                if len(close_contact) == 0:
                    close_contact = cR.getDictListWithFilter('pdbx_validate_close_contact',
                                                             [{'name': 'dist', 'type': 'float'}
                                                              ],
                                                             [{'name': 'PDB_model_num', 'type': 'int', 'value': representativeModelId},
                                                              {'name': 'auth_asym_id_1', 'type': 'str', 'value': authAsymId2},
                                                              {'name': 'auth_seq_id_1', 'type': 'int', 'value': authSeqId2},
                                                              {'name': 'auth_atom_id_1', 'type': 'str', 'value': authAtomId2},
                                                              {'name': 'auth_asym_id_2', 'type': 'str', 'value': authAsymId1},
                                                              {'name': 'auth_seq_id_2', 'type': 'int', 'value': authSeqId1},
                                                              {'name': 'auth_atom_id_2', 'type': 'str', 'value': authAtomId1}
                                                              ])

            else:
                close_contact = []

        except Exception:
            return False

        if len(close_contact) == 0:

            bond = getCoordBondLength(cR, authAsymId1, authSeqId1, authAtomId1, authAsymId2, authSeqId2, authAtomId2,
                                      representativeAltId, modelNumName, False)

            if bond is None:
                return False

            distance = next((b['distance'] for b in bond if b['model_id'] == representativeModelId), None)

            if distance is None:
                return False

            return 1.0 < distance < 2.4

        return 1.0 < close_contact[0]['dist'] < 2.4

    return struct_conn[0]['conn_type_id'] not in emptyValue


def getCoordBondLength(cR, asymId1: str, seqId1: int, atomId1: str,
                       asymId2: str, seqId2: int, atomId2: str,
                       representativeAltId: int = REPRESENTATIVE_ALT_ID,
                       modelNumName: str = 'PDB_model_num', labelScheme: bool = True) -> Optional[List[dict]]:
    """ Return the bond length of given two atoms.
        @return: list of bond length for each model_id (None for failure case)
    """

    try:

        dataItems = [{'name': 'Cartn_x', 'type': 'float', 'alt_name': 'x'},
                     {'name': 'Cartn_y', 'type': 'float', 'alt_name': 'y'},
                     {'name': 'Cartn_z', 'type': 'float', 'alt_name': 'z'},
                     {'name': modelNumName, 'type': 'int', 'alt_name': 'model_id'}
                     ]

        atom_site_1 = cR.getDictListWithFilter('atom_site',
                                               dataItems,
                                               [{'name': 'label_asym_id' if labelScheme else 'auth_asym_id', 'type': 'str', 'value': asymId1},
                                                {'name': 'label_seq_id' if labelScheme else 'auth_seq_id', 'type': 'int', 'value': seqId1},
                                                {'name': 'label_atom_id' if labelScheme else 'auth_atom_id', 'type': 'str', 'value': atomId1},
                                                {'name': 'label_alt_id', 'type': 'enum', 'enum': (representativeAltId,)}
                                                ])

        atom_site_2 = cR.getDictListWithFilter('atom_site',
                                               dataItems,
                                               [{'name': 'label_asym_id' if labelScheme else 'auth_asym_id', 'type': 'str', 'value': asymId2},
                                                {'name': 'label_seq_id' if labelScheme else 'auth_seq_id', 'type': 'int', 'value': seqId2},
                                                {'name': 'label_atom_id' if labelScheme else 'auth_atom_id', 'type': 'str', 'value': atomId2},
                                                {'name': 'label_alt_id', 'type': 'enum', 'enum': (representativeAltId,)}
                                                ])

    except Exception:
        return None

    model_ids = set(a['model_id'] for a in atom_site_1) | set(a['model_id'] for a in atom_site_2)

    bond = []

    for model_id in model_ids:
        a_1 = next((a for a in atom_site_1 if a['model_id'] == model_id), None)
        a_2 = next((a for a in atom_site_2 if a['model_id'] == model_id), None)

        if None in (a_1, a_2):
            continue

        bond.append({'model_id': model_id, 'distance': float(f"{numpy.linalg.norm(to_np_array(a_1) - to_np_array(a_2)):.3f}")})

    if len(bond) > 0:
        return bond

    return None


def getMetalCoordOf(cR, authSeqId: int, authCompId: str, metalId: str) -> Tuple[Optional[str], Optional[int]]:
    """ Return auth_asym_id and auth_seq_id of a metal element attached to given residue.
    """

    if cR is None:
        return None, None

    is_metal_ion = authCompId in SYMBOLS_ELEMENT

    if cR.hasCategory('struct_conn'):

        bonds = cR.getDictList('struct_conn')

        for bond in bonds:

            if bond['conn_type_id'] != 'metalc':
                continue

            auth_comp_id_1 = bond['ptnr1_auth_comp_id']
            auth_comp_id_2 = bond['ptnr2_auth_comp_id']

            if not is_metal_ion and {auth_comp_id_1, auth_comp_id_2} != {authCompId, metalId}:
                continue

            try:

                auth_seq_id_1 = int(bond['ptnr1_auth_seq_id'])
                auth_seq_id_2 = int(bond['ptnr2_auth_seq_id'])

                if authSeqId == auth_seq_id_1 and (is_metal_ion or authCompId == auth_comp_id_1) and metalId == auth_comp_id_2:
                    return bond['ptnr2_auth_asym_id'], auth_seq_id_2

                if authSeqId == auth_seq_id_2 and (is_metal_ion or authCompId == auth_comp_id_2) and metalId == auth_comp_id_1:
                    return bond['ptnr1_auth_asym_id'], auth_seq_id_1

            except ValueError:
                pass

    return None, None


def getRestraintName(mrSubtype: str, title: bool = False) -> str:
    """ Return human-readable restraint name for a given restraint subtype.
    """

    if mrSubtype.startswith('dist'):
        return "Distance restraints" if title else "distance restraints"
    if mrSubtype.startswith('dihed'):
        return "Dihedral angle restraints" if title else "dihedral angle restraints"
    if mrSubtype.startswith('rdc') and mrSubtype != 'rdc_raw_data':
        return "Residual dipolar coupling restraints" if title else "residual dipolar coupling restraints"
    if mrSubtype == 'rdc_raw_data':
        return "Residual dipolar coupling data" if title else "residual dipolar coupling data"
    if mrSubtype.startswith('plane'):
        return "Planarity constraints" if title else "planarity constraints"
    if mrSubtype.startswith('hbond'):
        return "Hydrogen bond restraints" if title else "hydrogen bond restraints"
    if mrSubtype.startswith('ssbond'):
        return "Disulfide bond constraints" if title else "disulfide bond constraints"
    if mrSubtype.startswith('fchiral'):
        return "Floating chiral stereo assignments" if title else "floating chiral stereo assignments"
    if mrSubtype.startswith('adist'):
        return "Anti-distance restraints" if title else "anti-distance restraints"
    if mrSubtype.startswith('jcoup'):
        return "Scalar J-coupling restraints" if title else "scalar J-coupling restraints"
    if mrSubtype.startswith('hvycs'):
        return "Carbon chemical shift restraints" if title else "carbon chemical shift restraints"
    if mrSubtype.startswith('procs'):
        return "Proton chemical shift restraints" if title else "proton chemical shift restraints"
    if mrSubtype.startswith('rama'):
        return "Dihedral angle database restraints" if title else "dihedral angle database restraints"
    if mrSubtype.startswith('radi'):
        return "Radius of gyration restraints" if title else "radius of gyration restraints"
    if mrSubtype.startswith('diff'):
        return "Diffusion anisotropy restraints" if title else "diffusion anisotropy restraints"
    if mrSubtype.startswith('nbase'):
        return "Nucleic acid base orientation restraints" if title else "nucleic acid base orientation restraints"
    if mrSubtype.startswith('csa'):
        return "Chemical shift anisotropy restraints" if title else "chemical shift anisotropy restraints"
    if mrSubtype.startswith('ddc'):
        return "Dipolar coupling restraints" if title else "dipolar coupling restraints"
    if mrSubtype.startswith('ang'):
        return "Angle databse restraints" if title else "angle database restraints"
    if mrSubtype.startswith('pre'):
        return "Paramagnetic relaxation enhancement restraints" if title else "paramagnetic relaxation enhancement restraints"
    if mrSubtype.startswith('pcs'):
        return "Pseudocontact shift restraints" if title else "pseudocontact shift restraints"
    if mrSubtype.startswith('prdc'):
        return "Paramagnetic RDC restraints" if title else "paramagnetic RDC restraints"
    if mrSubtype.startswith('pang'):
        return "Paramagnetic angle restraints" if title else "paramagnetic angle restraints"
    if mrSubtype.startswith('pccr'):
        return "Paramagnetic CCR restraints" if title else "paramagnetic CCR restraints"
    if mrSubtype.startswith('ccr_d_csa'):
        return "CCR D-CSA restraints"
    if mrSubtype.startswith('ccr_dd'):
        return "CCR D-D restraints"
    if mrSubtype.startswith('geo'):
        return "Coordinate geometry restraints" if title else "coordinate geometry restraints"
    if mrSubtype.startswith('noepk'):
        return "NOESY peak volume restraints"
    if mrSubtype.startswith('saxs'):
        return "Small angle X-ray scattering restraints" if title else "small angle X-ray scattering restraints"
    if mrSubtype == 'heteronucl_noe_data':
        return "Heteronuclear NOE data" if title else "heteronuclear NOE data"
    if mrSubtype == 'heteronucl_t1_data':
        return "Heteronuclear T1 relaxation data" if title else "heteronuclear T1 relaxation data"
    if mrSubtype == 'heteronucl_t2_data':
        return "Heteronuclear T2 relaxation data" if title else "heteronuclear T2 relaxation data"
    if mrSubtype == 'heteronucl_t1r_data':
        return "Heteronuclear T1rho relaxation data" if title else "heteronuclear T1rho relaxation data"
    if mrSubtype == 'order_param_data':
        return "Order parameter data" if title else "order parameter data"
    if mrSubtype == 'ph_titr_data':
        return "pKa value data"
    if mrSubtype == 'ph_param_data':
        return "pH titration data"
    if mrSubtype == 'coupling_const_data':
        return "Coupling constant data"
    if mrSubtype == 'peak2d':
        return "2D spectral peak list"
    if mrSubtype == 'peak3d':
        return "3D spectral peak list"
    if mrSubtype == 'peak4d':
        return "4D spectral peak list"
    if mrSubtype == 'chem_shift':
        return "Assigned chemical shift list" if title else "assigned chemical shift list"

    raise KeyError(f'Internal restraint subtype {mrSubtype!r} is not defined.')


def contentSubtypeOf(mrSubtype: str) -> str:
    """ Return legitimate content subtype of NmrDpUtility.py for a given internal restraint subtype.
    """

    if mrSubtype in ('dist', 'dihed', 'rdc', 'noepk', 'jcoup', 'hvycs', 'procs', 'csa', 'fchiral', 'saxs'):
        return mrSubtype + '_restraint'

    if mrSubtype == 'hbond':
        return 'dist_restraint'

    if mrSubtype == 'ssbond':
        return 'dist_restraint'

    if mrSubtype == 'prdc':
        return 'rdc_restraint'

    if mrSubtype == 'pcs':
        return 'csp_restraint'

    if mrSubtype == 'pre':
        return 'auto_relax_restraint'

    if mrSubtype == 'pccr':
        return 'ccr_dd_restraint'

    if mrSubtype in ('plane', 'adist', 'rama', 'radi', 'diff', 'nbase', 'ang', 'pang', 'geo'):
        return 'other_restraint'

    if mrSubtype.startswith('peak')\
       or mrSubtype == 'spectral_peak':  # for getAltLoops() and getAuxLoops()
        return 'spectral_peak'

    if mrSubtype == 'chem_shift':
        return 'chem_shift'

    raise KeyError(f'Internal restraint subtype {mrSubtype!r} is not defined.')


def incListIdCounter(mrSubtype: str, listIdCounter: dict, reduced: bool = True,
                     reservedListIds: Optional[dict] = None) -> dict:  # for NMR data remediation upgrade to Phase 2
    """ Increment list id counter for a given internal restraint subtype (default)/content subtype (reduced=False).
    """

    if len(listIdCounter) == 0:
        listIdCounter = {'dist_restraint': 0,
                         'dihed_restraint': 0,
                         'rdc_restraint': 0,
                         'noepk_restraint': 0,
                         'jcoup_restraint': 0,
                         'rdc_raw_data': 0,
                         'csa_restraint': 0,
                         'ddc_restraint': 0,
                         'hvycs_restraint': 0,
                         'procs_restraint': 0,
                         'csp_restraint': 0,
                         'auto_relax_restraint': 0,
                         'heteronucl_noe_data': 0,
                         'heteronucl_t1_data': 0,
                         'heteronucl_t2_data': 0,
                         'heteronucl_t1r_data': 0,
                         'order_param_data': 0,
                         'ph_titr_data': 0,
                         'ph_param_data': 0,
                         'coupling_const_data': 0,
                         'ccr_d_csa_restraint': 0,
                         'ccr_dd_restraint': 0,
                         'fchiral_restraint': 0,
                         'saxs_restraint': 0,
                         'other_restraint': 0,
                         'spectral_peak': 0,
                         'chem_shift': 0
                         }

    contentSubtype = (contentSubtypeOf(mrSubtype) if reduced else mrSubtype) if mrSubtype is not None else 'other_restraint'

    if contentSubtype is None or contentSubtype not in listIdCounter:
        return listIdCounter

    listIdCounter[contentSubtype] += 1

    if reservedListIds is not None and contentSubtype in reservedListIds:
        while True:
            if listIdCounter[contentSubtype] not in reservedListIds[contentSubtype]:
                break
            listIdCounter[contentSubtype] += 1

    return listIdCounter


def decListIdCounter(mrSubtype: str, listIdCounter: dict, reduced: bool = True,
                     reservedListIds: Optional[dict] = None) -> dict:  # for NMR data remediation upgrade to Phase 2
    """ Decrement list id counter for a given internal restraint subtype (default)/content subtype (reduced=False).
    """

    if len(listIdCounter) == 0:
        listIdCounter = {'dist_restraint': 0,
                         'dihed_restraint': 0,
                         'rdc_restraint': 0,
                         'noepk_restraint': 0,
                         'jcoup_restraint': 0,
                         'rdc_raw_data': 0,
                         'csa_restraint': 0,
                         'ddc_restraint': 0,
                         'hvycs_restraint': 0,
                         'procs_restraint': 0,
                         'csp_restraint': 0,
                         'auto_relax_restraint': 0,
                         'heteronucl_noe_data': 0,
                         'heteronucl_t1_data': 0,
                         'heteronucl_t2_data': 0,
                         'heteronucl_t1r_data': 0,
                         'order_param_data': 0,
                         'ph_titr_data': 0,
                         'ph_param_data': 0,
                         'coupling_const_data': 0,
                         'ccr_d_csa_restraint': 0,
                         'ccr_dd_restraint': 0,
                         'fchiral_restraint': 0,
                         'saxs_restraint': 0,
                         'other_restraint': 0,
                         'spectral_peak': 0,
                         'chem_shift': 0
                         }

    contentSubtype = (contentSubtypeOf(mrSubtype) if reduced else mrSubtype) if mrSubtype is not None else 'other_restraint'

    if contentSubtype is None or contentSubtype not in listIdCounter:
        return listIdCounter

    listIdCounter[contentSubtype] -= 1

    if reservedListIds is not None and contentSubtype in reservedListIds:
        while True:
            if listIdCounter[contentSubtype] not in reservedListIds[contentSubtype]:
                break
            listIdCounter[contentSubtype] -= 1

    return listIdCounter


def getReadableFactor(factor: dict, fileType='nm-res-xpl') -> str:
    """ Return human readable XPLOR-NIH/CNS/CHARMM/SCHRODINGER factor expression.
    """

    _factor = {k: sorted(list(set(v))) if isinstance(v, list) else v for k, v in factor.items()}

    key_order = ['chain_id', 'auth_chain_id', 'alt_chain_id', 'seq_id', 'comp_id', 'alt_comp_id', 'type_symbol', 'atom_id', 'alt_atom_id']

    key_map = {'chain_id': 'segidentifier',
               'auth_chain_id': 'original segidentifier',
               'alt_chain_id': 'original segidentifier',
               'seq_id': 'residue',
               'comp_id': 'resname',
               'alt_comp_id': 'original resname',
               'type_symbol': 'chemical',
               'atom_id': 'name',
               'alt_atom_id': 'original name'}

    if fileType == 'nm-res-sch':  # DAOTHER-10172: Schrodinger/ASL
        key_map = {'chain_id': 'chain.name',
                   'auth_chain_id': 'original chain.name',
                   'alt_chain_id': 'original chain.name',
                   'seq_id': 'residue.number',
                   'comp_id': 'residue.ptype',
                   'alt_comp_id': 'original residue.ptype',
                   'type_symbol': 'atom.element',
                   'atom_id': 'atom.ptype',
                   'alt_atom_id': 'original atom.ptype'}

    for k in _factor.keys():

        if k in key_map or k == 'is_poly':
            continue

        key_order.append(k)
        key_map[k] = k

    __factor = {}

    for k in key_order:

        if k not in _factor:
            continue

        v = _factor[k]

        if v in emptyValue or (isinstance(v, list) and (len(v) == 0 or v[0] in emptyValue)):
            continue

        if k == 'atom_id' and 'alt_atom_id' in _factor:
            _v = _factor['alt_atom_id']
            if _v in ('%', '*', '#') or (len(_v) == 2 and _v[-1] in ('%', '*', '#')) or (_v.startswith('HT') and len(v) > 1):
                continue

        if k in ('chain_id', 'seq_id') and isinstance(v, list) and len(v) > 20:
            v = 'specified elsewhere or unspecified'

        if k in ('auth_chain_id', 'alt_chain_id'):
            if v == _factor['chain_id']:
                continue

        if k == 'alt_comp_id' and v == _factor['comp_id']:
            continue

        if k == 'alt_atom_id' and v == _factor['atom_id']:
            continue

        __factor[key_map[k]] = (v if len(v) > 1 else v[0]) if isinstance(v, list) else v

    return str(__factor)


def getReadableParamagCenter(factor: dict) -> str:
    """ Return human readable paramagnetic center.
    """

    _factor = {k: sorted(list(set(v))) if isinstance(v, list) else v for k, v in factor.items()}

    key_order = ['chain_id', 'seq_id', 'comp_id', 'alt_comp_id', 'atom_id', 'alt_atom_id']

    __factor = []

    for k in key_order:

        if k not in _factor:
            continue

        v = _factor[k]

        if v in emptyValue or (isinstance(v, list) and (len(v) == 0 or v[0] in emptyValue)):
            continue

        if k == 'atom_id' and 'alt_atom_id' in _factor:
            _v = _factor['alt_atom_id']
            if _v in ('%', '*', '#') or (len(_v) == 2 and _v[-1] in ('%', '*', '#')) or (_v.startswith('HT') and len(v) > 1):
                continue

        if k in ('chain_id', 'seq_id') and isinstance(v, list) and len(v) > 20:
            continue

        __factor.append(str((v if len(v) > 1 else v[0]) if isinstance(v, list) else v))

        if k.startswith('alt'):
            __factor[-1] = f'({__factor[-1]})'

    return '/'.join(__factor)


def retrieveOriginalFileName(filePath: str) -> str:
    """ Retrieve original filename by omitting internal sufixes used in NMR data remediation.
    """

    if filePath in emptyValue:
        return None

    fileName = os.path.basename(filePath)
    if fileName.endswith('-corrected'):
        fileName = fileName[:-10]
    if fileName.endswith('-ignored'):
        fileName = fileName[:-8]
    if '-selected-as-' in fileName:
        idx = fileName.index('-selected-as-')
        fileName = fileName[:idx]
    if '-ignored-as-' in fileName:
        idx = fileName.index('-ignored-as-')
        fileName = fileName[:idx]

    if fileName.endswith('.mr'):
        if fileName.endswith('-corrected.mr'):
            fileName = fileName[:-13] + '.mr'
        if fileName.endswith('-trimmed.mr'):
            fileName = fileName[:-11] + '.mr'
        if fileName.endswith('-remediated.mr'):
            fileName = fileName[:-13] + '.mr'

        if '-div_' in fileName:
            idx = fileName.index('-div_')
            fileName = fileName[:idx] + '.mr'

    if fileName.endswith('.str'):
        if fileName.endswith('-corrected.str'):
            fileName = fileName[:-14] + '.str'
        if fileName.endswith('-trimmed.str'):
            fileName = fileName[:-12] + '.str'
        if fileName.endswith('-remediated.str'):
            fileName = fileName[:-14] + '.str'

        if '-div_' in fileName:
            idx = fileName.index('-div_')
            fileName = fileName[:idx] + '.str'

    if fileName.endswith('.cif'):
        if fileName.endswith('-corrected.cif'):
            fileName = fileName[:-14] + '.cif'
        if fileName.endswith('-trimmed.cif'):
            fileName = fileName[:-12] + '.cif'
        if fileName.endswith('-remediated.cif'):
            fileName = fileName[:-14] + '.cif'

        if '-div_' in fileName:
            idx = fileName.index('-div_')
            fileName = fileName[:idx] + '.cif'

    return fileName


def getSaveframe(mrSubtype: str, sf_framecode: str,
                 listId: Optional[int] = None, entryId: Optional[str] = None, fileName: Optional[str] = None,
                 constraintType: Optional[str] = None, potentialType: Optional[str] = None,
                 rdcCode: Optional[str] = None, alignCenter: Optional[dict] = None,
                 cyanaParameter: Optional[dict] = None, reduced: bool = True,
                 numOfDim: Optional[int] = None, spectrumName: Optional[str] = None) -> Optional[pynmrstar.Saveframe]:
    """ Return pynmrstar saveframe for a given internal restraint subtype (default)/content subtype (reduced=False).
        @return: pynmrstar saveframe
    """

    contentSubtype = (contentSubtypeOf(mrSubtype) if reduced else mrSubtype) if mrSubtype is not None else 'other_restraint'

    if contentSubtype is None:
        return None

    if contentSubtype not in NMR_STAR_SF_CATEGORIES:
        return None

    sf = pynmrstar.Saveframe.from_scratch(sf_framecode)
    sf.set_tag_prefix(NMR_STAR_SF_TAG_PREFIXES[contentSubtype])

    for sf_tag_item in NMR_STAR_SF_TAG_ITEMS[contentSubtype]:
        tag_item_name = sf_tag_item['name']

        if tag_item_name == 'Sf_category':
            sf.add_tag(tag_item_name, NMR_STAR_SF_CATEGORIES[contentSubtype])
        elif tag_item_name == 'Sf_framecode':
            sf.add_tag(tag_item_name, sf_framecode)
        elif tag_item_name == 'ID' and listId is not None:
            sf.add_tag(tag_item_name, listId)
        elif tag_item_name == 'Entry_ID' and entryId is not None:
            sf.add_tag(tag_item_name, entryId)
        elif tag_item_name == 'Data_file_name' and fileName is not None:
            if fileName.endswith('-corrected'):
                sf.add_tag(tag_item_name, re.sub(r'-corrected$', '', fileName))
            elif '-ignored-as' in fileName:
                sf.add_tag(tag_item_name, re.sub(r'-ignored-as.*', '', fileName))
            elif '-selected-as' in fileName:
                sf.add_tag(tag_item_name, re.sub(r'-selected-as.*', '', fileName))
            else:
                sf.add_tag(tag_item_name, fileName)
        elif tag_item_name == 'Constraint_type' and (mrSubtype == 'hbond'
                                                     or (constraintType is not None
                                                         and constraintType == 'hydrogen bond')):
            sf.add_tag(tag_item_name, 'hydrogen bond')
        elif tag_item_name == 'Constraint_type' and (mrSubtype == 'ssbond'
                                                     or (constraintType is not None
                                                         and constraintType == 'disulfide bond')):
            sf.add_tag(tag_item_name, 'disulfide bond')
        elif tag_item_name == 'Constraint_type' and constraintType is not None and constraintType == 'diselenide bond':
            sf.add_tag(tag_item_name, 'diselenide bond')
        elif tag_item_name == 'Constraint_type' and constraintType is not None and constraintType == 'metal coordination':
            sf.add_tag(tag_item_name, 'metal coordination')
        elif tag_item_name == 'Constraint_type' and mrSubtype.startswith('rdc'):
            sf.add_tag(tag_item_name, 'RDC')
        elif tag_item_name == 'Constraint_type' and constraintType is not None:
            if constraintType.startswith('ambiguous'):
                sf.add_tag(tag_item_name, constraintType[10:])
            else:
                sf.add_tag(tag_item_name, constraintType)
        elif tag_item_name == 'Constraint_type' and mrSubtype.startswith('dist'):
            sf.add_tag(tag_item_name, 'NOE')
        elif tag_item_name == 'Potential_type':
            sf.add_tag(tag_item_name, potentialType)
        elif tag_item_name == 'Homonuclear_NOE_val_type' and mrSubtype.startswith('noepk'):
            sf.add_tag(tag_item_name, 'peak volume')
        elif tag_item_name == 'Val_units' and (mrSubtype.startswith('csa') or mrSubtype in ('pccr', 'ccr_dd_restraint')):
            sf.add_tag(tag_item_name, 'ppm')
        elif tag_item_name == 'Units' and (mrSubtype.startswith('hvycs') or mrSubtype.startswith('procs')):
            sf.add_tag(tag_item_name, 'ppm')
        elif tag_item_name == 'Type' and mrSubtype in ('pcs', 'csp_restraint'):
            sf.add_tag(tag_item_name, 'paramagnetic ligand binding')
        elif tag_item_name == 'Common_relaxation_type_name' and mrSubtype in ('pre', 'auto_relax_restraint'):
            sf.add_tag(tag_item_name, 'paramagnetic relaxation enhancement')
        elif tag_item_name == 'Relaxation_coherence_type' and mrSubtype in ('pre', 'auto_relax_restraint'):
            sf.add_tag(tag_item_name, "S+")
        elif tag_item_name == 'Relaxation_val_units' and mrSubtype in ('pre', 'auto_relax_restraint'):
            sf.add_tag(tag_item_name, 's-1')
        elif tag_item_name == 'Rex_units' and mrSubtype in ('pre', 'auto_relax_restraint'):
            sf.add_tag(tag_item_name, 's-1')
        elif tag_item_name == 'Definition' and contentSubtype == 'other_restraint' and constraintType is not None:
            sf.add_tag(tag_item_name, constraintType)
        elif tag_item_name == 'Tensor_auth_asym_ID' and mrSubtype in ('prdc', 'rdc_restraint') and alignCenter is not None\
                and 'chain_id' in alignCenter:
            chainId = alignCenter['chain_id']
            if isinstance(chainId, list):
                if len(chainId) > 0:
                    chainId = chainId[0]
                else:
                    chainId = None
            sf.add_tag(tag_item_name, chainId)
        elif tag_item_name == 'Tensor_auth_seq_ID' and mrSubtype in ('prdc', 'rdc_restraint') and alignCenter is not None\
                and 'seq_id' in alignCenter:
            seqId = alignCenter['seq_id']
            if isinstance(seqId, list):
                if len(seqId) > 0:
                    seqId = seqId[0]
                else:
                    seqId = None
            sf.add_tag(tag_item_name, seqId)
        elif tag_item_name == 'Tensor_auth_comp_ID' and mrSubtype in ('prdc', 'rdc_restraint') and alignCenter is not None\
                and 'comp_id' in alignCenter:
            compId = alignCenter['comp_id']
            if isinstance(compId, list):
                if len(compId) > 0:
                    compId = compId[0]
                else:
                    compId = None
            sf.add_tag(tag_item_name, compId)
        elif tag_item_name == 'Tensor_magnitude' and mrSubtype.startswith('rdc') and cyanaParameter is not None:
            sf.add_tag(tag_item_name, cyanaParameter['magnitude'])
        elif tag_item_name == 'Tensor_rhombicity' and mrSubtype.startswith('rdc') and cyanaParameter is not None:
            sf.add_tag(tag_item_name, cyanaParameter['rhombicity'])
        elif tag_item_name == 'Details' and mrSubtype is not None and mrSubtype.startswith('rdc')\
                and mrSubtype != 'rdc_raw_data' and rdcCode is not None:
            sf.add_tag(tag_item_name, rdcCode)
        elif tag_item_name == 'Details' and mrSubtype in ('pcs', 'csp_restraint') and cyanaParameter is not None:
            sf.add_tag(tag_item_name, f"Tensor_magnitude {cyanaParameter['magnitude']}, "
                       f"Tensor_rhombicity {cyanaParameter['rhombicity']}, "
                       f"Paramagnetic_center_seq_ID {cyanaParameter['orientation_center_seq_id']}")
        elif tag_item_name == 'Number_of_spectral_dimensions' and numOfDim is not None:
            sf.add_tag(tag_item_name, numOfDim)
        elif tag_item_name == 'Experiment_type' and spectrumName is not None:
            sf.add_tag(tag_item_name, spectrumName)
        else:
            sf.add_tag(tag_item_name, '.')

    return sf


def getLoop(mrSubtype: str, reduced: bool = True, hasInsCode: bool = False) -> Optional[pynmrstar.Loop]:
    """ Return pynmrstar loop for a given internal restraint subtype (default)/content subtype (reduced=False)..
        @return: pynmrstar loop
    """

    contentSubtype = contentSubtypeOf(mrSubtype) if reduced else mrSubtype

    if contentSubtype is None:
        return None

    if contentSubtype not in NMR_STAR_LP_CATEGORIES:
        return None

    if contentSubtype == 'other_restraint' and reduced:
        return {'tags': [], 'data': []}  # dictionary for _Other_data_type_list.Text_data

    prefix = NMR_STAR_LP_CATEGORIES[contentSubtype] + '.'

    lp = pynmrstar.Loop.from_scratch()

    tags = [prefix + item['name'] for item in NMR_STAR_LP_KEY_ITEMS[contentSubtype]]
    if hasInsCode and contentSubtype in NMR_STAR_LP_DATA_ITEMS_INS_CODE:
        tags.extend([prefix + item['name'] for item in NMR_STAR_LP_DATA_ITEMS_INS_CODE[contentSubtype]])
    else:
        tags.extend([prefix + item['name'] for item in NMR_STAR_LP_DATA_ITEMS[contentSubtype]])

    lp.add_tag(tags)

    return lp


def getPkLoop(pkSubtype: str) -> Optional[pynmrstar.Loop]:
    """ Return pynmrstar peak_row_format loop for a given internal peak subtype
        @return: pynmrstar loop
    """

    contentSubtype = contentSubtypeOf(pkSubtype)

    if contentSubtype is None:
        return None

    if contentSubtype not in NMR_STAR_LP_CATEGORIES:
        return None

    prefix = NMR_STAR_LP_CATEGORIES[contentSubtype] + '.'

    lp = pynmrstar.Loop.from_scratch()

    tags = [prefix + item['name'] for item in NMR_STAR_LP_KEY_ITEMS[contentSubtype]]
    tags.extend([prefix + item['name'] for item in NMR_STAR_LP_DATA_ITEMS[pkSubtype]])

    lp.add_tag(tags)

    return lp


def getAltLoops(mrSubtype: str) -> Optional[List[pynmrstar.Loop]]:
    """ Return pynmrstar alternative loops for a given internal restraint subtype
        @return: list of pynmrstar loops
    """

    contentSubtype = contentSubtypeOf(mrSubtype)

    if contentSubtype is None:
        return None

    if contentSubtype not in NMR_STAR_ALT_LP_CATEGORIES:
        return None

    alt_lps = []

    for catName in NMR_STAR_ALT_LP_CATEGORIES[contentSubtype]:

        prefix = catName + '.'

        alt_lp = pynmrstar.Loop.from_scratch()

        tags = [prefix + item['name'] for item in NMR_STAR_ALT_LP_KEY_ITEMS[contentSubtype][catName]]
        tags.extend([prefix + item['name'] for item in NMR_STAR_ALT_LP_DATA_ITEMS[contentSubtype][catName]])

        alt_lp.add_tag(tags)

        alt_lps.append(alt_lp)

    return alt_lps


def getAuxLoops(mrSubtype: str) -> Optional[List[pynmrstar.Loop]]:
    """ Return pynmrstar auxiliary loops for a given internal restraint subtype.
        @return: list of pynmrstar loops
    """

    contentSubtype = contentSubtypeOf(mrSubtype)

    if contentSubtype is None:
        return None

    if contentSubtype not in NMR_STAR_AUX_LP_CATEGORIES:
        return None

    aux_lps = []

    for catName in NMR_STAR_AUX_LP_CATEGORIES[contentSubtype]:

        prefix = catName + '.'

        aux_lp = pynmrstar.Loop.from_scratch()

        tags = [prefix + item['name'] for item in NMR_STAR_AUX_LP_KEY_ITEMS[contentSubtype][catName]]
        tags.extend([prefix + item['name'] for item in NMR_STAR_AUX_LP_DATA_ITEMS[contentSubtype][catName]])

        aux_lp.add_tag(tags)

        aux_lps.append(aux_lp)

    return aux_lps


def getStarAtom(authToStarSeq: Optional[dict], authToOrigSeq: Optional[dict], offsetHolder: dict,
                atom: List[dict], aux_atom: Optional[dict] = None, asis: bool = False) -> Optional[str]:
    """ Return NMR-STAR sequence including entity ID for a given auth atom of the cooridnates.
        @return: a dictionary of NMR-STAR sequence/entity, None otherwise
    """

    def retrieve_label_comp_id(_seqId, _compId):
        if authToOrigSeq is not None:
            for _seqKey in authToStarSeq.keys():
                if _seqKey[1] == _seqId and _seqKey in authToOrigSeq:
                    if _compId == authToOrigSeq[_seqKey][1]:
                        return _seqKey[2]
        return _compId

    starAtom = copy.copy(atom)

    chainId = atom['chain_id']
    seqId = atom['seq_id']
    if 'comp_id' not in atom:
        atom['comp_id'] = starAtom['comp_id'] = None
    compId = atom['comp_id']
    seqKey = (chainId, seqId, compId)

    if authToOrigSeq is not None:
        if seqKey in authToOrigSeq:
            _compId = authToOrigSeq[seqKey][1]
            if compId != _compId:
                starAtom['comp_id'] = _compId
        else:
            _compId = retrieve_label_comp_id(seqId, compId)
            if compId != _compId:
                compId = _compId
                seqKey = (chainId, seqId, _compId)

    if 'atom_id' not in atom:
        starAtom['atom_id'] = None

    has_aux_atom = False
    if aux_atom is not None:
        auxChainId = aux_atom['chain_id']
        auxSeqId = aux_atom['seq_id']
        auxCompId = aux_atom.get('comp_id')
        if chainId == auxChainId and seqId != auxSeqId:
            auxSeqKey = (auxChainId, auxSeqId, auxCompId)

            if authToOrigSeq is not None:
                if auxSeqKey in authToOrigSeq:
                    _auxCompId = authToOrigSeq[auxSeqKey][1]
                    if auxCompId != _auxCompId:
                        auxCompId = _auxCompId
                else:
                    _auxCompId = retrieve_label_comp_id(auxSeqId, auxCompId)
                    if auxCompId != _auxCompId:
                        auxCompId = _auxCompId
                        auxSeqKey = (auxChainId, auxSeqId, auxCompId)

            has_aux_atom = True

    if seqKey in authToStarSeq and chainId not in offsetHolder:
        starAtom['chain_id'], starAtom['seq_id'], starAtom['entity_id'], _ = authToStarSeq[seqKey]
        return starAtom

    if asis:
        for seqKey in authToStarSeq:
            if seqKey[0] != chainId or not isinstance(seqKey[1], int):
                continue
            if seqKey[1] - MAX_ALLOWED_EXT_SEQ <= seqId <= seqKey[1] + MAX_ALLOWED_EXT_SEQ:
                offset = seqId - seqKey[1]
                starAtom['chain_id'], starAtom['seq_id'], starAtom['entity_id'], _ = authToStarSeq[seqKey]
                starAtom['seq_id'] += offset
                return starAtom

    if chainId in offsetHolder and seqId is not None:
        offset = offsetHolder[chainId]
        seqKey = (chainId, seqId + offset, compId)
        if has_aux_atom:
            auxSeqKey = (auxChainId, auxSeqId + offset, auxCompId)
        if seqKey in authToStarSeq and (not has_aux_atom or (has_aux_atom and auxSeqKey in authToStarSeq)):
            starAtom['chain_id'], starAtom['seq_id'], starAtom['entity_id'], _ = authToStarSeq[seqKey]
            atom['seq_id'] = seqId + offset
            return starAtom

    elif f'_{chainId}' in offsetHolder and seqId is not None:
        offset = offsetHolder[f'_{chainId}']
        seqKey = (chainId, seqId + offset, compId)
        if seqKey in authToStarSeq:
            starAtom['chain_id'], starAtom['seq_id'], starAtom['entity_id'], _ = authToStarSeq[seqKey]
            atom['seq_id'] = seqId + offset
            return starAtom

    if seqKey in authToStarSeq:
        starAtom['chain_id'], starAtom['seq_id'], starAtom['entity_id'], _ = authToStarSeq[seqKey]
        return starAtom

    if seqId is not None:
        for offset in range(1, MAX_OFFSET_ATTEMPT):
            seqKey = (chainId, seqId + offset, compId)
            if has_aux_atom:
                auxSeqKey = (auxChainId, auxSeqId + offset, auxCompId)
            if seqKey in authToStarSeq and (not has_aux_atom or (has_aux_atom and auxSeqKey in authToStarSeq)):
                starAtom['chain_id'], starAtom['seq_id'], starAtom['entity_id'], _ = authToStarSeq[seqKey]
                offsetHolder[chainId] = offset
                if has_aux_atom and compId in monDict3 and auxCompId in monDict3:
                    offsetHolder[f'_{chainId}'] = offset
                atom['seq_id'] = seqId + offset
                return starAtom
            seqKey = (chainId, seqId - offset, compId)
            if has_aux_atom:
                auxSeqKey = (auxChainId, auxSeqId + offset, auxCompId)
            if seqKey in authToStarSeq and (not has_aux_atom or (has_aux_atom and auxSeqKey in authToStarSeq)):
                starAtom['chain_id'], starAtom['seq_id'], starAtom['entity_id'], _ = authToStarSeq[seqKey]
                offsetHolder[chainId] = -offset
                if has_aux_atom and compId in monDict3 and auxCompId in monDict3:
                    offsetHolder[f'_{chainId}'] = -offset
                atom['seq_id'] = seqId - offset
                return starAtom

    _seqKey = next((_seqKey for _seqKey in authToStarSeq if chainId == _seqKey[0] and seqId == _seqKey[1]), None)
    _auxSeqKey = None
    if has_aux_atom:
        _auxSeqKey = next((_auxSeqKey for _auxSeqKey in authToStarSeq if auxChainId == _auxSeqKey[0] and auxSeqId == _auxSeqKey[1]), None)

    if _seqKey is not None and (not has_aux_atom or (has_aux_atom and _auxSeqKey is not None)):
        if compId in emptyValue or compId not in monDict3:
            starAtom['chain_id'], starAtom['seq_id'], starAtom['entity_id'], _ = authToStarSeq[_seqKey]
            if compId in emptyValue or compId != _seqKey[2]:
                atom['comp_id'] = starAtom['comp_id'] = _seqKey[2]
            return starAtom

    if chainId in offsetHolder and compId in monDict3:
        del offsetHolder[chainId]

    return None


def getInsCode(authToInsCode: Optional[dict], offsetHolder: dict, atom: List[dict]) -> Optional[str]:
    """ Return PDB_ins_code for a given auth atom of the cooridnates.
        @return: PDB_ins_code
    """

    if authToInsCode is None:
        return None

    chainId = atom['chain_id']
    seqId = atom['seq_id']
    compId = atom.get('comp_id')
    seqKey = (chainId, seqId, compId)

    if seqKey in authToInsCode:
        return authToInsCode[seqKey]

    if chainId in offsetHolder:
        offset = offsetHolder[chainId]
        seqKey = (chainId, seqId + offset, compId)
        if seqKey in authToInsCode:
            return authToInsCode[seqKey]

    for offset in range(1, MAX_OFFSET_ATTEMPT):
        seqKey = (chainId, seqId + offset, compId)
        if seqKey in authToInsCode:
            offsetHolder[chainId] = offset
            return authToInsCode[seqKey]
        seqKey = (chainId, seqId - offset, compId)
        if seqKey in authToInsCode:
            offsetHolder[chainId] = -offset
            return authToInsCode[seqKey]

    _seqKey = next((_seqKey for _seqKey in authToInsCode if chainId == _seqKey[0] and seqId == _seqKey[1]), None)

    if _seqKey is not None:
        if compId in emptyValue or compId not in monDict3:
            if compId in emptyValue or compId != _seqKey[2]:
                atom['comp_id'] = _seqKey[2]
            return authToInsCode[_seqKey]

    return None


def getRow(mrSubtype: str, id: int, indexId: int,
           combinationId: Optional[int], memberId: Optional[int], code: Optional[str],
           listId: int, entryId: str, dstFunc: dict,
           authToStarSeq: Optional[dict], authToOrigSeq: Optional[dict],
           authToInsCode: Optional[dict], offsetHolder: dict,
           atom1: dict, atom2: Optional[dict] = None, atom3: Optional[dict] = None,
           atom4: Optional[dict] = None, atom5: Optional[dict] = None,
           asis1: bool = False, asis2: bool = False, asis3: bool = False,
           asis4: bool = False, asis5: bool = False) -> Optional[List[Any]]:
    """ Return row data for a given internal restraint subtype.
        @return: data array
    """

    contentSubtype = contentSubtypeOf(mrSubtype)

    if contentSubtype is None or contentSubtype == 'other_restraint':
        return None

    has_ins_code = authToInsCode is not None and contentSubtype in NMR_STAR_LP_DATA_ITEMS_INS_CODE

    key_size = len(NMR_STAR_LP_KEY_ITEMS[contentSubtype])
    data_size = len(NMR_STAR_LP_DATA_ITEMS_INS_CODE[contentSubtype]) if has_ins_code else len(NMR_STAR_LP_DATA_ITEMS[contentSubtype])

    float_row_idx = []

    row = [None] * (key_size + data_size)

    row[0] = id

    if code == 'OR' or isinstance(memberId, int):
        if atom1 is not None:
            atom1 = copy.copy(atom1)
        if atom2 is not None:
            atom2 = copy.copy(atom2)
        if atom3 is not None:
            atom3 = copy.copy(atom3)
        if atom4 is not None:
            atom4 = copy.copy(atom4)
        if atom5 is not None:
            atom5 = copy.copy(atom5)

    star_atom1, star_atom2, star_atom3, star_atom4, star_atom5 = None, None, None, None, None
    ins_code1, ins_code2, ins_code3, ins_code4, ins_code5 = None, None, None, None, None

    if atom1 is not None:
        if 'asis' in atom1:
            asis1 = True
        star_atom1 = getStarAtom(authToStarSeq, authToOrigSeq, offsetHolder, atom1, atom2, asis=asis1)
        if star_atom1 is None:
            star_atom1 = getStarAtom(authToStarSeq, authToOrigSeq, offsetHolder, atom1, asis=asis1)
        if 'atom_id' not in atom1:
            atom1['atom_id'] = None
        if has_ins_code:
            ins_code1 = getInsCode(authToInsCode, offsetHolder, atom1)

    if atom2 is not None:
        if 'asis' in atom2:
            asis2 = True
        star_atom2 = getStarAtom(authToStarSeq, authToOrigSeq, offsetHolder, atom2, atom1, asis=asis2)
        if star_atom2 is None:
            star_atom2 = getStarAtom(authToStarSeq, authToOrigSeq, offsetHolder, atom2, asis=asis2)
        if 'atom_id' not in atom2:
            atom2['atom_id'] = None
        if has_ins_code:
            ins_code2 = getInsCode(authToInsCode, offsetHolder, atom2)

    if atom3 is not None:
        if 'asis' in atom3:
            asis3 = True
        star_atom3 = getStarAtom(authToStarSeq, authToOrigSeq, offsetHolder, atom3, atom1, asis=asis3)
        if star_atom3 is None:
            star_atom3 = getStarAtom(authToStarSeq, authToOrigSeq, offsetHolder, atom3, asis=asis3)
        if 'atom_id' not in atom3:
            atom3['atom_id'] = None
        if has_ins_code:
            ins_code3 = getInsCode(authToInsCode, offsetHolder, atom3)

    if atom4 is not None:
        if 'asis' in atom4:
            asis4 = True
        star_atom4 = getStarAtom(authToStarSeq, authToOrigSeq, offsetHolder, atom4, atom1, asis=asis4)
        if star_atom4 is None:
            star_atom4 = getStarAtom(authToStarSeq, authToOrigSeq, offsetHolder, atom4, asis=asis4)
        if 'atom_id' not in atom4:
            atom4['atom_id'] = None
        if has_ins_code:
            ins_code4 = getInsCode(authToInsCode, offsetHolder, atom4)

    if atom5 is not None:
        if 'asis' in atom5:
            asis5 = True
        star_atom5 = getStarAtom(authToStarSeq, authToOrigSeq, offsetHolder, atom5, atom1, asis=asis5)
        if star_atom5 is None:
            star_atom5 = getStarAtom(authToStarSeq, authToOrigSeq, offsetHolder, atom5, asis=asis5)
        if 'atom_id' not in atom5:
            atom5['atom_id'] = None
        if has_ins_code:
            ins_code5 = getInsCode(authToInsCode, offsetHolder, atom5)

    if star_atom1 is None and star_atom2 is not None:  # procs
        row[1], row[2], row[3], row[4], row[5] =\
            star_atom2['chain_id'], star_atom2['entity_id'], star_atom2['seq_id'], star_atom2['comp_id'], star_atom2['atom_id']
    elif mrSubtype != 'fchiral':
        if star_atom1 is not None:
            row[1], row[2], row[3], row[4], row[5] =\
                star_atom1['chain_id'], star_atom1['entity_id'], star_atom1['seq_id'], star_atom1['comp_id'], star_atom1['atom_id']
        if star_atom2 is not None:
            row[6], row[7], row[8], row[9], row[10] =\
                star_atom2['chain_id'], star_atom2['entity_id'], star_atom2['seq_id'], star_atom2['comp_id'], star_atom2['atom_id']
    else:
        if star_atom1 is not None:
            row[1], row[2], row[3], row[4], row[5] =\
                star_atom1['chain_id'], star_atom1['entity_id'], star_atom1['seq_id'], star_atom1['comp_id'], star_atom1['auth_atom_id']
        if star_atom2 is not None:
            row[6], row[7], row[8], row[9], row[10] =\
                star_atom2['chain_id'], star_atom2['entity_id'], star_atom2['seq_id'], star_atom2['comp_id'], star_atom2['auth_atom_id']

    if mrSubtype in ('dist', 'dihed', 'rdc', 'hbond', 'ssbond', 'prdc'):
        row[key_size] = indexId

    row[-2] = listId
    row[-1] = entryId

    if mrSubtype in ('dist', 'hbond', 'ssbond'):
        row[key_size + 1] = combinationId
        row[key_size + 2] = memberId
        row[key_size + 3] = code
        if has_key_value(dstFunc, 'target_value'):
            row[key_size + 4] = dstFunc['target_value']
            float_row_idx.append(key_size + 4)
        if has_key_value(dstFunc, 'target_value_uncertainty'):
            row[key_size + 5] = dstFunc['target_value_uncertainty']
            float_row_idx.append(key_size + 5)
        if has_key_value(dstFunc, 'lower_linear_limit'):
            row[key_size + 6] = dstFunc['lower_linear_limit']
            float_row_idx.append(key_size + 6)
        if has_key_value(dstFunc, 'lower_limit'):
            row[key_size + 7] = dstFunc['lower_limit']
            float_row_idx.append(key_size + 7)
        if has_key_value(dstFunc, 'upper_limit'):
            row[key_size + 8] = dstFunc['upper_limit']
            float_row_idx.append(key_size + 8)
        if has_key_value(dstFunc, 'upper_linear_limit'):
            row[key_size + 9] = dstFunc['upper_linear_limit']
            float_row_idx.append(key_size + 9)
        if has_key_value(dstFunc, 'weight'):
            row[key_size + 10] = dstFunc['weight']
        # Distance_val

        row[key_size + 12], row[key_size + 13], row[key_size + 14], row[key_size + 15] =\
            atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id']
        if has_key_value(atom1, 'auth_atom_id'):
            row[key_size + 16] = atom1['auth_atom_id']
        row[key_size + 17], row[key_size + 18], row[key_size + 19], row[key_size + 20] =\
            atom2['chain_id'], atom2['seq_id'], atom2['comp_id'], atom2['atom_id']
        if has_key_value(atom2, 'auth_atom_id'):
            row[key_size + 21] = atom2['auth_atom_id']

        if has_ins_code:
            row[key_size + 22] = ins_code1
            row[key_size + 23] = ins_code2

    elif mrSubtype == 'dihed':
        if None not in (atom1, star_atom3):
            row[11], row[12], row[13], row[14], row[15] =\
                star_atom3['chain_id'], star_atom3['entity_id'], star_atom3['seq_id'], star_atom3['comp_id'], star_atom3['atom_id']
        elif star_atom5 is not None:  # PPA, phase angle of pseudorotation
            row[11], row[12], row[13], row[14] =\
                star_atom5['chain_id'], star_atom5['entity_id'], star_atom5['seq_id'], star_atom5['comp_id']
        if None not in (atom2, star_atom4):
            row[16], row[17], row[18], row[19], row[20] =\
                star_atom4['chain_id'], star_atom4['entity_id'], star_atom4['seq_id'], star_atom4['comp_id'], star_atom4['atom_id']
        elif star_atom5 is not None:  # PPA, phase angle of pseudorotation
            row[16], row[17], row[18], row[19] =\
                star_atom5['chain_id'], star_atom5['entity_id'], star_atom5['seq_id'], star_atom5['comp_id']

        row[key_size + 1] = combinationId
        row[key_size + 2] = code
        if has_key_value(dstFunc, 'target_value'):
            row[key_size + 3] = dstFunc['target_value']
            float_row_idx.append(key_size + 3)
        if has_key_value(dstFunc, 'target_value_uncertainty'):
            row[key_size + 4] = dstFunc['target_value_uncertainty']
            float_row_idx.append(key_size + 4)
        if has_key_value(dstFunc, 'lower_linear_limit'):
            row[key_size + 5] = dstFunc['lower_linear_limit']
            float_row_idx.append(key_size + 5)
        if has_key_value(dstFunc, 'lower_limit'):
            row[key_size + 6] = dstFunc['lower_limit']
            float_row_idx.append(key_size + 6)
        if has_key_value(dstFunc, 'upper_limit'):
            row[key_size + 7] = dstFunc['upper_limit']
            float_row_idx.append(key_size + 7)
        if has_key_value(dstFunc, 'upper_linear_limit'):
            row[key_size + 8] = dstFunc['upper_linear_limit']
            float_row_idx.append(key_size + 8)
        if has_key_value(dstFunc, 'weight'):
            row[key_size + 9] = dstFunc['weight']

        if atom1 is not None:
            row[key_size + 10], row[key_size + 11], row[key_size + 12], row[key_size + 13] =\
                atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id']
            if has_key_value(atom1, 'auth_atom_id'):
                row[key_size + 14] = atom1['auth_atom_id']
        elif atom5 is not None:  # PPA, phase angle of pseudorotation
            row[key_size + 10], row[key_size + 11], row[key_size + 12] =\
                atom5['chain_id'], atom5['seq_id'], atom5['comp_id']
        if atom2 is not None:
            row[key_size + 15], row[key_size + 16], row[key_size + 17], row[key_size + 18] =\
                atom2['chain_id'], atom2['seq_id'], atom2['comp_id'], atom2['atom_id']
            if has_key_value(atom2, 'auth_atom_id'):
                row[key_size + 19] = atom2['auth_atom_id']
        elif atom5 is not None:  # PPA, phase angle of pseudorotation
            row[key_size + 15], row[key_size + 16], row[key_size + 17] =\
                atom5['chain_id'], atom5['seq_id'], atom5['comp_id']
        if atom3 is not None:
            row[key_size + 20], row[key_size + 21], row[key_size + 22], row[key_size + 23] =\
                atom3['chain_id'], atom3['seq_id'], atom3['comp_id'], atom3['atom_id']
            if has_key_value(atom3, 'auth_atom_id'):
                row[key_size + 24] = atom3['auth_atom_id']
        elif atom5 is not None:  # PPA, phase angle of pseudorotation
            row[key_size + 20], row[key_size + 21], row[key_size + 22] =\
                atom5['chain_id'], atom5['seq_id'], atom5['comp_id']
        if atom4 is not None:
            row[key_size + 25], row[key_size + 26], row[key_size + 27], row[key_size + 28] =\
                atom4['chain_id'], atom4['seq_id'], atom4['comp_id'], atom4['atom_id']
            if has_key_value(atom4, 'auth_atom_id'):
                row[key_size + 29] = atom4['auth_atom_id']
        elif atom5 is not None:  # PPA, phase angle of pseudorotation
            row[key_size + 25], row[key_size + 26], row[key_size + 27] =\
                atom5['chain_id'], atom5['seq_id'], atom5['comp_id']
            if has_key_value(atom5, 'auth_atom_id'):
                row[key_size + 29] = atom5['auth_atom_id']

        if has_ins_code:
            row[key_size + 30] = ins_code1 if atom1 is not None else ins_code5
            row[key_size + 31] = ins_code2 if atom2 is not None else ins_code5
            row[key_size + 32] = ins_code3 if atom3 is not None else ins_code5
            row[key_size + 33] = ins_code4 if atom4 is not None else ins_code5

    elif mrSubtype in ('rdc', 'prdc'):
        row[key_size + 1] = combinationId
        if has_key_value(dstFunc, 'target_value'):
            row[key_size + 2] = dstFunc['target_value']
            float_row_idx.append(key_size + 2)
        if has_key_value(dstFunc, 'target_value_uncertainty'):
            row[key_size + 3] = dstFunc['target_value_uncertainty']
            float_row_idx.append(key_size + 3)
        if has_key_value(dstFunc, 'lower_linear_limit'):
            row[key_size + 4] = dstFunc['lower_linear_limit']
            float_row_idx.append(key_size + 4)
        if has_key_value(dstFunc, 'lower_limit'):
            row[key_size + 5] = dstFunc['lower_limit']
            float_row_idx.append(key_size + 5)
        if has_key_value(dstFunc, 'upper_limit'):
            row[key_size + 6] = dstFunc['upper_limit']
            float_row_idx.append(key_size + 6)
        if has_key_value(dstFunc, 'upper_linear_limit'):
            row[key_size + 7] = dstFunc['upper_linear_limit']
            float_row_idx.append(key_size + 7)
        if has_key_value(dstFunc, 'weight'):
            row[key_size + 8] = dstFunc['weight']
        # RDC_val
        # RDC_val_err
        # RDC_val_scale_factor
        # RDC_distance_depedent

        row[key_size + 13], row[key_size + 14], row[key_size + 15], row[key_size + 16] =\
            atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id']
        if has_key_value(atom1, 'auth_atom_id'):
            row[key_size + 17] = atom1['auth_atom_id']
        row[key_size + 18], row[key_size + 19], row[key_size + 20], row[key_size + 21] =\
            atom2['chain_id'], atom2['seq_id'], atom2['comp_id'], atom2['atom_id']
        if has_key_value(atom2, 'auth_atom_id'):
            row[key_size + 22] = atom2['auth_atom_id']

        if has_ins_code:
            row[key_size + 22] = ins_code1
            row[key_size + 23] = ins_code2

    elif mrSubtype == 'noepk':
        if has_key_value(dstFunc, 'target_value'):
            row[key_size] = dstFunc['target_value']
            float_row_idx.append(key_size)
        if has_key_value(dstFunc, 'target_value_uncertainty'):
            row[key_size + 1] = dstFunc['target_value_uncertainty']
            float_row_idx.append(key_size + 1)
        if has_key_value(dstFunc, 'lower_limit'):
            row[key_size + 2] = dstFunc['lower_limit']
            float_row_idx.append(key_size + 2)
        if has_key_value(dstFunc, 'upper_limit'):
            row[key_size + 3] = dstFunc['upper_limit']
            float_row_idx.append(key_size + 3)

        row[key_size + 4], row[key_size + 5], row[key_size + 6], row[key_size + 7] =\
            atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id']
        row[key_size + 8], row[key_size + 9], row[key_size + 10], row[key_size + 11] =\
            atom2['chain_id'], atom2['seq_id'], atom2['comp_id'], atom2['atom_id']

    elif mrSubtype == 'jcoup':
        if star_atom3 is not None:
            row[11], row[12], row[13], row[14], row[15] =\
                star_atom3['chain_id'], star_atom3['entity_id'], star_atom3['seq_id'], star_atom3['comp_id'], star_atom3['atom_id']
        if star_atom4 is not None:
            row[16], row[17], row[18], row[19], row[20] =\
                star_atom4['chain_id'], star_atom4['entity_id'], star_atom4['seq_id'], star_atom4['comp_id'], star_atom4['atom_id']

        if has_key_value(dstFunc, 'target_value'):
            row[key_size] = dstFunc['target_value']
            float_row_idx.append(key_size)
        if has_key_value(dstFunc, 'target_value_uncertainty'):
            row[key_size + 1] = dstFunc['target_value_uncertainty']
            float_row_idx.append(key_size + 1)
        if has_key_value(dstFunc, 'lower_limit'):
            row[key_size + 2] = dstFunc['lower_limit']
            float_row_idx.append(key_size + 2)
        if has_key_value(dstFunc, 'upper_limit'):
            row[key_size + 3] = dstFunc['upper_limit']
            float_row_idx.append(key_size + 3)

        row[key_size + 4], row[key_size + 5], row[key_size + 6], row[key_size + 7] =\
            atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id']
        row[key_size + 8], row[key_size + 9], row[key_size + 10], row[key_size + 11] =\
            atom2['chain_id'], atom2['seq_id'], atom2['comp_id'], atom2['atom_id']
        row[key_size + 12], row[key_size + 13], row[key_size + 14], row[key_size + 15] =\
            atom3['chain_id'], atom3['seq_id'], atom3['comp_id'], atom3['atom_id']
        row[key_size + 16], row[key_size + 17], row[key_size + 18], row[key_size + 19] =\
            atom4['chain_id'], atom4['seq_id'], atom4['comp_id'], atom4['atom_id']

    elif mrSubtype == 'csa':
        if atom1 is not None:
            row[key_size] = atomType = atom1['atom_id'][0]
            row[key_size + 1] = ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS[atomType][0]
        if has_key_value(dstFunc, 'target_value'):
            row[key_size + 2] = dstFunc['target_value']
            float_row_idx.append(key_size + 2)
        if has_key_value(dstFunc, 'target_value_uncertainty'):
            row[key_size + 3] = dstFunc['target_value_uncertainty']
            float_row_idx.append(key_size + 3)
        # Principal_value_sigma_11_val
        # Principal_value_sigma_22_val
        # Principal_value_sigma_33_val
        # Principal_Euler_angle_alpha_val
        # Principal_Euler_angle_beta_val
        # Principal_Euler_angle_gamma_val
        # Bond_length

        row[key_size + 11], row[key_size + 12], row[key_size + 13], row[key_size + 14] =\
            atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id']

    elif mrSubtype == 'hvycs':
        if star_atom3 is not None:
            row[11], row[12], row[13], row[14], row[15] =\
                star_atom3['chain_id'], star_atom3['entity_id'], star_atom3['seq_id'], star_atom3['comp_id'], star_atom3['atom_id']
        if star_atom4 is not None:
            row[16], row[17], row[18], row[19], row[20] =\
                star_atom4['chain_id'], star_atom4['entity_id'], star_atom4['seq_id'], star_atom4['comp_id'], star_atom4['atom_id']
        if star_atom5 is not None:
            row[21], row[22], row[23], row[24], row[25] =\
                star_atom5['chain_id'], star_atom5['entity_id'], star_atom5['seq_id'], star_atom5['comp_id'], star_atom5['atom_id']

        row[key_size] = dstFunc['ca_shift']
        # CA_chem_shift_val_err
        if has_key_value(dstFunc, 'cb_shift'):
            row[key_size + 2] = dstFunc['cb_shift']
        # CB_chem_shift_val_err
        row[key_size + 4], row[key_size + 5], row[key_size + 6], row[key_size + 7] =\
            atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id']
        row[key_size + 8], row[key_size + 9], row[key_size + 10], row[key_size + 11] =\
            atom2['chain_id'], atom2['seq_id'], atom2['comp_id'], atom2['atom_id']
        row[key_size + 12], row[key_size + 13], row[key_size + 14], row[key_size + 15] =\
            atom3['chain_id'], atom3['seq_id'], atom3['comp_id'], atom3['atom_id']
        row[key_size + 16], row[key_size + 17], row[key_size + 18], row[key_size + 19] =\
            atom4['chain_id'], atom4['seq_id'], atom4['comp_id'], atom4['atom_id']
        row[key_size + 20], row[key_size + 21], row[key_size + 22], row[key_size + 23] =\
            atom5['chain_id'], atom5['seq_id'], atom5['comp_id'], atom5['atom_id']

    elif mrSubtype == 'procs':
        if atom1 is not None:
            row[key_size] = atomType = atom1['atom_id'][0]
            row[key_size + 1] = ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS[atomType][0]
        elif atom2 is not None:
            row[key_size] = atomType = atom2['atom_id'][0]
            row[key_size + 1] = ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS[atomType][0]
        row[key_size + 2] = dstFunc['obs_value'] if atom2 is None else dstFunc['obs_value_2']
        # Chem_shift_val_err

        if atom2 is None:
            row[key_size + 4], row[key_size + 5], row[key_size + 6], row[key_size + 7] =\
                atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id']
        else:
            row[key_size + 4], row[key_size + 5], row[key_size + 6], row[key_size + 7] =\
                atom2['chain_id'], atom2['seq_id'], atom2['comp_id'], atom2['atom_id']

    elif mrSubtype == 'pcs':
        if atom1 is not None:
            row[key_size] = atomType = atom1['atom_id'][0]
            row[key_size + 1] = ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS[atomType][0]
        # Chem_shift_val
        # Chem_shift_val_err
        if has_key_value(dstFunc, 'target_value'):
            row[key_size + 4] = dstFunc['target_value']
            float_row_idx.append(key_size + 4)
        if has_key_value(dstFunc, 'lower_value') and has_key_value(dstFunc, 'upper_value'):
            row[key_size + 5] = (dstFunc['upper_value'] - dstFunc['lower_value']) / 2.0
            float_row_idx.append(key_size + 5)

        row[key_size + 6], row[key_size + 7], row[key_size + 8], row[key_size + 9] =\
            atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id']

    elif mrSubtype == 'pre':
        if atom1 is not None:
            row[key_size] = atomType = atom1['atom_id'][0]
            row[key_size + 1] = ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS[atomType][0]
        if has_key_value(dstFunc, 'target_value'):
            row[key_size + 2] = dstFunc['target_value']
            float_row_idx.append(key_size + 2)
        if has_key_value(dstFunc, 'lower_value') and has_key_value(dstFunc, 'upper_value'):
            row[key_size + 3] = (dstFunc['upper_value'] - dstFunc['lower_value']) / 2.0
            float_row_idx.append(key_size + 3)
        # Rex_val
        # Rex_val_err

        row[key_size + 6], row[key_size + 7], row[key_size + 8], row[key_size + 9] =\
            atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id']

    elif mrSubtype == 'pccr':
        if star_atom3 is not None:
            row[11], row[12], row[13], row[14], row[15] =\
                star_atom3['chain_id'], star_atom3['entity_id'], star_atom3['seq_id'], star_atom3['comp_id'], star_atom3['atom_id']
        if star_atom4 is not None:
            row[16], row[17], row[18], row[19], row[20] =\
                star_atom4['chain_id'], star_atom4['entity_id'], star_atom4['seq_id'], star_atom4['comp_id'], star_atom4['atom_id']

        row[key_size] = atom1['atom_id']
        # Dipole_1_atom_isotope_number_1
        # Dipole_1_atom_type_2
        # Dipole_1_atom_isotope_number_2
        if atom3 is not None:
            row[key_size + 4] = atomType = atom3['atom_id'][0]
            row[key_size + 5] = ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS[atomType][0]
        if atom4 is not None:
            row[key_size + 6] = atomType = atom4['atom_id'][0]
            row[key_size + 7] = ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS[atomType][0]
        if has_key_value(dstFunc, 'target_value'):
            row[key_size + 8] = dstFunc['target_value']
            float_row_idx.append(key_size + 8)
        if has_key_value(dstFunc, 'lower_value') and has_key_value(dstFunc, 'upper_value'):
            row[key_size + 9] = (dstFunc['upper_value'] - dstFunc['lower_value']) / 2.0
            float_row_idx.append(key_size + 9)

        row[key_size + 10], row[key_size + 11], row[key_size + 12], row[key_size + 13] =\
            atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id']
        # Dipole_1_auth_entity_assembly_ID_2
        # Dipole_1_auth_seq_ID_2
        # Dipole_1_auth_comp_ID_2
        # Dipole_1_auth_atom_ID_2
        row[key_size + 18], row[key_size + 19], row[key_size + 20], row[key_size + 21] =\
            atom3['chain_id'], atom3['seq_id'], atom3['comp_id'], atom3['atom_id']
        row[key_size + 22], row[key_size + 23], row[key_size + 24], row[key_size + 25] =\
            atom4['chain_id'], atom4['seq_id'], atom4['comp_id'], atom4['atom_id']

    elif mrSubtype == 'fchiral':
        row[key_size] = code
        row[key_size + 1], row[key_size + 2], row[key_size + 3], row[key_size + 4] =\
            atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['auth_atom_id']
        row[key_size + 5], row[key_size + 6], row[key_size + 7], row[key_size + 8] =\
            atom2['chain_id'], atom2['seq_id'], atom2['comp_id'], atom2['auth_atom_id']

    elif mrSubtype == 'saxs':
        row[1] = code
        if has_key_value(dstFunc, 'target_value'):
            row[key_size] = dstFunc['target_value']
        if has_key_value(dstFunc, 'target_value_uncertainty'):
            row[key_size + 1] = dstFunc['target_value_uncertainty']
        if has_key_value(dstFunc, 'weight'):
            row[key_size + 2] = dstFunc['weight']

    if len(float_row_idx) > 0:
        max_eff_digits = 0
        for idx in float_row_idx:
            val = row[idx]
            if '.' in val and val[-1] == '0':
                period = val.index('.')
                last = len(val) - 1
                while val[last] == '0':
                    last -= 1
                eff_digits = last - period
                if eff_digits > 0 and eff_digits > max_eff_digits:
                    max_eff_digits = eff_digits
        for idx in float_row_idx:
            val = row[idx]
            if '.' in val and val[-1] == '0':
                first_digit = val.index('.') + 1
                eff_digits = len(val) - first_digit
                if 0 < max_eff_digits < eff_digits:
                    row[idx] = row[idx][0:first_digit + max_eff_digits]
                else:
                    row[idx] = row[idx][0:first_digit + 1]

    return row


def getPkRow(pkSubtype: str, id: int, indexId: int,
             listId: int, entryId: str, dstFunc: dict,
             authToStarSeq: Optional[dict], authToOrigSeq: Optional[dict], offsetHolder: dict,
             atom1: Optional[dict] = None, atom2: Optional[dict] = None,
             atom3: Optional[dict] = None, atom4: Optional[dict] = None,
             asis1: bool = False, asis2: bool = False, asis3: bool = False, asis4: bool = False,
             ambig_code1: Optional[int] = None, ambig_code2: Optional[int] = None,
             ambig_code3: Optional[int] = None, ambig_code4: Optional[int] = None,
             details: Optional[str] = None) -> Optional[List[Any]]:
    """ Return row data for a given internal peak subtype.
        @return: data array
    """

    contentSubtype = contentSubtypeOf(pkSubtype)

    if contentSubtype is None:
        return None

    key_size = len(NMR_STAR_LP_KEY_ITEMS[contentSubtype])
    data_size = len(NMR_STAR_LP_DATA_ITEMS[pkSubtype])

    row = [None] * (key_size + data_size)

    row[0] = id

    star_atom1, star_atom2, star_atom3, star_atom4 = None, None, None, None

    if atom1 is not None:
        if 'asis' in atom1:
            asis1 = True
        star_atom1 = getStarAtom(authToStarSeq, authToOrigSeq, offsetHolder, atom1, atom2, asis=asis1)
        if star_atom1 is None:
            star_atom1 = getStarAtom(authToStarSeq, authToOrigSeq, offsetHolder, atom1, asis=asis1)
        if isinstance(ambig_code1, int) and star_atom1 is not None:
            star_atom1['atom_id'] = atom1['auth_atom_id']
            if 'orig_atom_id' in atom1:
                atom1['atom_id'] = atom1['orig_atom_id']

    if atom2 is not None:
        if 'asis' in atom2:
            asis2 = True
        star_atom2 = getStarAtom(authToStarSeq, authToOrigSeq, offsetHolder, atom2, atom1, asis=asis2)
        if star_atom2 is None:
            star_atom2 = getStarAtom(authToStarSeq, authToOrigSeq, offsetHolder, atom2, asis=asis2)
        if isinstance(ambig_code2, int) and star_atom2 is not None:
            star_atom2['atom_id'] = atom2['auth_atom_id']
            if 'orig_atom_id' in atom2:
                atom2['atom_id'] = atom2['orig_atom_id']

    if atom3 is not None:
        if 'asis' in atom3:
            asis3 = True
        star_atom3 = getStarAtom(authToStarSeq, authToOrigSeq, offsetHolder, atom3, atom1, asis=asis3)
        if star_atom3 is None:
            star_atom3 = getStarAtom(authToStarSeq, authToOrigSeq, offsetHolder, atom3, asis=asis3)
        if isinstance(ambig_code3, int) and star_atom3 is not None:
            star_atom3['atom_id'] = atom3['auth_atom_id']
            if 'orig_atom_id' in atom3:
                atom3['atom_id'] = atom3['orig_atom_id']

    if atom4 is not None:
        if 'asis' in atom4:
            asis4 = True
        star_atom4 = getStarAtom(authToStarSeq, authToOrigSeq, offsetHolder, atom4, atom1, asis=asis4)
        if star_atom4 is None:
            star_atom4 = getStarAtom(authToStarSeq, authToOrigSeq, offsetHolder, atom4, asis=asis4)
        if isinstance(ambig_code4, int) and star_atom4 is not None:
            star_atom4['atom_id'] = atom4['auth_atom_id']
            if 'orig_atom_id' in atom4:
                atom4['atom_id'] = atom4['orig_atom_id']

    row[key_size] = indexId

    _key_size = key_size

    row[_key_size + 1] = dstFunc['position_1']
    if has_key_value(dstFunc, 'position_uncertainty_1'):
        row[_key_size + 2] = dstFunc['position_uncertainty_1']
    if has_key_value(dstFunc, 'line_width_1'):
        row[_key_size + 3] = dstFunc['line_width_1']
    if has_key_value(dstFunc, 'line_width_uncertainty_1'):
        row[_key_size + 4] = dstFunc['line_width_uncertainty_1']
    if atom1 is not None:
        if star_atom1 is not None:
            row[_key_size + 5], row[_key_size + 6], row[_key_size + 7], row[_key_size + 8], row[_key_size + 9] =\
                star_atom1['chain_id'], star_atom1['entity_id'], star_atom1['seq_id'], star_atom1['comp_id'], star_atom1['atom_id']
        row[_key_size + 12], row[_key_size + 13], row[_key_size + 14], row[_key_size + 15] =\
            atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id']
        if ambig_code1 is not None:
            row[_key_size + 10] = row[_key_size + 16] = ambig_code1

    _key_size += 16

    row[_key_size + 1] = dstFunc['position_2']
    if has_key_value(dstFunc, 'position_uncertainty_2'):
        row[_key_size + 2] = dstFunc['position_uncertainty_2']
    if has_key_value(dstFunc, 'line_width_2'):
        row[_key_size + 3] = dstFunc['line_width_2']
    if has_key_value(dstFunc, 'line_width_uncertainty_2'):
        row[_key_size + 4] = dstFunc['line_width_uncertainty_2']
    if atom2 is not None:
        if star_atom2 is not None:
            row[_key_size + 5], row[_key_size + 6], row[_key_size + 7], row[_key_size + 8], row[_key_size + 9] =\
                star_atom2['chain_id'], star_atom2['entity_id'], star_atom2['seq_id'], star_atom2['comp_id'], star_atom2['atom_id']
        row[_key_size + 12], row[_key_size + 13], row[_key_size + 14], row[_key_size + 15] =\
            atom2['chain_id'], atom2['seq_id'], atom2['comp_id'], atom2['atom_id']
        if ambig_code2 is not None:
            row[_key_size + 10] = row[_key_size + 16] = ambig_code2

    if pkSubtype in ('peak3d', 'peak4d'):

        _key_size += 16

        row[_key_size + 1] = dstFunc['position_3']
        if has_key_value(dstFunc, 'position_uncertainty_3'):
            row[_key_size + 2] = dstFunc['position_uncertainty_3']
        if has_key_value(dstFunc, 'line_width_3'):
            row[_key_size + 3] = dstFunc['line_width_3']
        if has_key_value(dstFunc, 'line_width_uncertainty_3'):
            row[_key_size + 4] = dstFunc['line_width_uncertainty_3']
        if atom3 is not None:
            if star_atom3 is not None:
                row[_key_size + 5], row[_key_size + 6], row[_key_size + 7], row[_key_size + 8], row[_key_size + 9] =\
                    star_atom3['chain_id'], star_atom3['entity_id'], star_atom3['seq_id'], star_atom3['comp_id'], star_atom3['atom_id']
            row[_key_size + 12], row[_key_size + 13], row[_key_size + 14], row[_key_size + 15] =\
                atom3['chain_id'], atom3['seq_id'], atom3['comp_id'], atom3['atom_id']
            if ambig_code3 is not None:
                row[_key_size + 10] = row[_key_size + 16] = ambig_code3

    if pkSubtype == 'peak4d':

        _key_size += 16

        row[_key_size + 1] = dstFunc['position_4']
        if has_key_value(dstFunc, 'position_uncertainty_4'):
            row[_key_size + 2] = dstFunc['position_uncertainty_4']
        if has_key_value(dstFunc, 'line_width_4'):
            row[_key_size + 3] = dstFunc['line_width_4']
        if has_key_value(dstFunc, 'line_width_uncertainty_4'):
            row[_key_size + 4] = dstFunc['line_width_uncertainty_4']
        if atom4 is not None:
            if star_atom4 is not None:
                row[_key_size + 5], row[_key_size + 6], row[_key_size + 7], row[_key_size + 8], row[_key_size + 9] =\
                    star_atom4['chain_id'], star_atom4['entity_id'], star_atom4['seq_id'], star_atom4['comp_id'], star_atom4['atom_id']
            row[_key_size + 12], row[_key_size + 13], row[_key_size + 14], row[_key_size + 15] =\
                atom4['chain_id'], atom4['seq_id'], atom4['comp_id'], atom4['atom_id']
            if ambig_code4 is not None:
                row[_key_size + 10] = row[_key_size + 16] = ambig_code4

    if has_key_value(dstFunc, 'volume'):
        row[-8] = dstFunc['volume']
    if has_key_value(dstFunc, 'volume_uncertainty'):
        row[-7] = dstFunc['volume_uncertainty']
    if has_key_value(dstFunc, 'height'):
        row[-6] = dstFunc['height']
    if has_key_value(dstFunc, 'height_uncertainty'):
        row[-5] = dstFunc['height_uncertainty']
    if has_key_value(dstFunc, 'figure_of_merit'):
        row[-4] = dstFunc['figure_of_merit']
    if details is not None:
        row[-3] = details
    row[-2] = listId
    row[-1] = entryId

    return row


def getAltPkRow(pkSubtype: str, _indexId: int, indexId: int, listId: int, entryId: str, dstFunc: dict, details: Optional[str] = None) -> Optional[List[Any]]:
    """ Return row data for a _Peak loop.
        @return: data array
    """

    contentSubtype = contentSubtypeOf(pkSubtype)

    if contentSubtype is None:
        return None

    catName = '_Peak'

    key_size = len(NMR_STAR_ALT_LP_KEY_ITEMS[contentSubtype][catName])
    data_size = len(NMR_STAR_ALT_LP_DATA_ITEMS[contentSubtype][catName])

    row = [None] * (key_size + data_size)

    row[0] = indexId

    row[1] = _indexId

    if has_key_value(dstFunc, 'figure_of_merit'):
        row[2] = dstFunc['figure_of_merit']

    if details is not None:
        row[3] = details

    row[-2] = listId
    row[-1] = entryId

    return row


def getPkGenCharRow(pkSubtype: str, indexId: int, listId: int, entryId: str, dstFunc: dict, volume_or_height: str) -> Optional[List[Any]]:
    """ Return row data for a _Peak_general_char loop.
        @return: data array
    """

    contentSubtype = contentSubtypeOf(pkSubtype)

    if contentSubtype is None:
        return None

    catName = '_Peak_general_char'

    key_size = len(NMR_STAR_ALT_LP_KEY_ITEMS[contentSubtype][catName])
    data_size = len(NMR_STAR_ALT_LP_DATA_ITEMS[contentSubtype][catName])

    row = [None] * (key_size + data_size)

    row[0] = indexId

    if has_key_value(dstFunc, volume_or_height):
        row[1] = dstFunc[volume_or_height]
        if has_key_value(dstFunc, f'{volume_or_height}_uncertainty'):
            row[2] = dstFunc[f'{volume_or_height}_uncertainty']
        row[3] = volume_or_height

    row[-2] = listId
    row[-1] = entryId

    return row if row[1] is not None else None


def getPkCharRow(pkSubtype: str, indexId: int, listId: int, entryId: str, dstFunc: dict, dimId: int) -> Optional[List[Any]]:
    """ Return row data for a _Peak_char loop.
        @return: data array
    """

    contentSubtype = contentSubtypeOf(pkSubtype)

    if contentSubtype is None:
        return None

    catName = '_Peak_char'

    key_size = len(NMR_STAR_ALT_LP_KEY_ITEMS[contentSubtype][catName])
    data_size = len(NMR_STAR_ALT_LP_DATA_ITEMS[contentSubtype][catName])

    row = [None] * (key_size + data_size)

    row[0] = indexId
    row[1] = dimId

    if has_key_value(dstFunc, f'position_{dimId}'):
        row[2] = dstFunc[f'position_{dimId}']
    if has_key_value(dstFunc, f'position_uncertainty_{dimId}'):
        row[3] = dstFunc[f'position_uncertainty_{dimId}']
    if has_key_value(dstFunc, f'line_width_{dimId}'):
        row[4] = dstFunc[f'line_width_{dimId}']
    # if has_key_value(dstFunc, f'line_width_uncertainty_{dimId}'):
    #     row[5] = dstFunc[f'line_width_uncertainty_{dimId}']
    # row[6]: Coupling_pattern

    row[-2] = listId
    row[-1] = entryId

    return row


def getPkChemShiftRow(pkSubtype: str, indexId: int, listId: int, entryId: str, dstFunc: dict, setId: Optional[int], dimId: int,
                      authToStarSeq: Optional[dict], authToOrigSeq: Optional[dict], offsetHolder: dict,
                      atom: dict, asis: bool, ambig_code: Optional[int], details: Optional[str] = None) -> Optional[List[Any]]:
    """ Return row data for a _Assigned_peak_chem_shift loop.
        @return: data array
    """

    contentSubtype = contentSubtypeOf(pkSubtype)

    if contentSubtype is None:
        return None

    catName = '_Assigned_peak_chem_shift'

    key_size = len(NMR_STAR_ALT_LP_KEY_ITEMS[contentSubtype][catName])
    data_size = len(NMR_STAR_ALT_LP_DATA_ITEMS[contentSubtype][catName])

    row = [None] * (key_size + data_size)

    row[0] = indexId
    row[1] = dimId

    row[2] = setId
    # row[3]: Magnetization_linkage_ID

    if has_key_value(dstFunc, f'position_{dimId}'):
        row[4] = dstFunc[f'position_{dimId}']

    # row[5]: Contribution_fractional_val

    if has_key_value(dstFunc, 'figure_of_merit'):
        row[6] = dstFunc['figure_of_merit']

    # row[7]: Assigned_chem_shift_list_ID

    star_atom = None

    if atom is not None:
        if 'asis' in atom:
            asis = True
        star_atom = getStarAtom(authToStarSeq, authToOrigSeq, offsetHolder, atom, asis=asis)
        if star_atom is not None:
            if isinstance(ambig_code, int):
                star_atom['atom_id'] = atom['auth_atom_id']
                if 'orig_atom_id' in atom:
                    atom['atom_id'] = atom['orig_atom_id']
            row[8], row[9], row[10], row[11], row[12] =\
                star_atom['chain_id'], star_atom['entity_id'], star_atom['seq_id'], star_atom['comp_id'], star_atom['atom_id']
        row[13] = ambig_code
        # row[14]: Ambiguity_set_ID

        row[15], row[16], row[17], row[18] =\
            atom['chain_id'], atom['seq_id'], atom['comp_id'], atom['auth_atom_id']

    row[19] = details

    row[-2] = listId
    row[-1] = entryId

    return row


def getSpectralDimRow(id: int, listId: int, entryId: str, meta: dict) -> List[Any]:
    """ Return row data for a _Spectral_dim loop.
        @return: data array
    """

    content_subtype = 'spectral_peak'
    lp_category = '_Spectral_dim'

    key_size = len(NMR_STAR_AUX_LP_KEY_ITEMS[content_subtype][lp_category])
    data_items = NMR_STAR_AUX_LP_DATA_ITEMS[content_subtype][lp_category]

    row = [None] * (key_size + len(data_items))

    row[0] = id

    for idx, data_item in enumerate(data_items, start=key_size):
        data_name = data_item['name'].lower()
        if data_name in meta:
            row[idx] = meta[data_name]

    row[-2] = listId
    row[-1] = entryId

    return row


def getSpectralDimTransferRow(listId: int, entryId: str, meta: dict) -> List[Any]:
    """ Return row data for a _Spectral_dim_transfer loop.
        @return: data array
    """

    content_subtype = 'spectral_peak'
    lp_category = '_Spectral_dim_transfer'

    key_items = NMR_STAR_AUX_LP_KEY_ITEMS[content_subtype][lp_category]
    data_items = NMR_STAR_AUX_LP_DATA_ITEMS[content_subtype][lp_category]

    key_size = len(key_items)

    row = [None] * (key_size + len(data_items))

    for idx, key_item in enumerate(key_items):
        key_name = key_item['name'].lower()
        row[idx] = meta[key_name]

    for idx, data_item in enumerate(data_items, start=key_size):
        data_name = data_item['name'].lower()
        if data_name in meta:
            row[idx] = meta[data_name]

    row[-2] = listId
    row[-1] = entryId

    return row


def getCsRow(csSubtype: str, indexId: int,
             listId: int, entryId: str, dstFunc: dict,
             entityAssembly: Optional[dict],
             atom: dict, ambig_code: Optional[int] = None,
             details: Optional[str] = None) -> Optional[List[Any]]:
    """ Return row data for _Atom_chem_shift loop.
        @return: data array
    """

    contentSubtype = contentSubtypeOf(csSubtype)

    if contentSubtype is None:
        return None

    key_size = len(NMR_STAR_LP_KEY_ITEMS[contentSubtype])
    data_size = len(NMR_STAR_LP_DATA_ITEMS[contentSubtype])

    row = [None] * (key_size + data_size)
    row[0] = indexId
    row[1] = atom['chain_id']
    if entityAssembly is not None and atom['chain_id'] in entityAssembly:
        row[2] = entityAssembly[atom['chain_id']]['entity_id']
    row[3], row[4], row[5] = atom['seq_id'], atom['comp_id'], atom['atom_id']
    if has_key_value(dstFunc, 'occupancy'):
        row[6] = dstFunc['occupancy']

    row[key_size] = atomType = atom['atom_id'][0]
    row[key_size + 1] = ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS[atomType][0]
    row[key_size + 2] = dstFunc['position']
    if has_key_value(dstFunc, 'position_uncertainty'):
        row[key_size + 3] = dstFunc['position_uncertainty']
    row[key_size + 4] = ambig_code
    # row[key_size + 5]: Ambiguity_set_ID
    row[key_size + 6] = atom['seq_id']
    if entityAssembly is not None and atom['chain_id'] in entityAssembly:
        authAsymId = entityAssembly[atom['chain_id']]['auth_asym_id']
        if authAsymId not in emptyValue:
            row[key_size + 7] = authAsymId
    row[key_size + 8], row[key_size + 9], row[key_size + 10] =\
        atom['auth_seq_id' if 'auth_seq_id' in atom else 'seq_id'], \
        atom['auth_comp_id' if 'auth_comp_id' in atom else 'comp_id'], \
        atom['auth_atom_id' if 'auth_atom_id' in atom else 'atom_id']

    if details is not None:
        row[-3] = details
    row[-2] = listId
    row[-1] = entryId

    return row


def getMaxEffDigits(vals: List[str]) -> int:
    """ Return maximum effective precision of float strings.
    """

    max_eff_digits = 0
    for val in vals:
        if '.' in val:
            period = val.index('.')
            last = len(val) - 1
            while val[last] == '0':
                last -= 1
            eff_digits = last - period
            if eff_digits > 0 and eff_digits > max_eff_digits:
                max_eff_digits = eff_digits
    return max_eff_digits


def roundString(string: str, maxEffDigits: int) -> str:
    """ Return rounded float string for a given maximum effective precision.
    """

    if '.' in string:
        first_digit = string.index('.') + 1
        eff_digits = len(string) - first_digit
        if 0 < maxEffDigits < eff_digits:
            return string[0:first_digit + maxEffDigits]
        return string[0:first_digit + 1]
    return string


def resetCombinationId(mrSubtype: str, row: List[Any]) -> List[Any]:
    """ Reset Combination_ID.
        @return: data array
    """

    if mrSubtype not in ('dist', 'dihed', 'rdc', 'prdc'):
        return row

    contentSubtype = contentSubtypeOf(mrSubtype)

    if contentSubtype is None or contentSubtype == 'other_restraint':
        return row

    key_size = len(NMR_STAR_LP_KEY_ITEMS[contentSubtype])

    row[key_size + 1] = '.'

    return row


def resetMemberId(mrSubtype: str, row: List[Any]) -> List[Any]:
    """ Reset Member_ID and Member_logic_code.
        @return: data array
    """

    if mrSubtype not in ('dist', 'hbond', 'ssbond'):
        return row

    contentSubtype = contentSubtypeOf(mrSubtype)

    if contentSubtype is None or contentSubtype == 'other_restraint':
        return row

    key_size = len(NMR_STAR_LP_KEY_ITEMS[contentSubtype])

    row[key_size + 2] = row[key_size + 3] = '.'

    return row


def getDstFuncForHBond(atom1: dict, atom2: dict) -> dict:
    """ Return default upper/lower limits for a hydrogen bond.
    """

    dstFunc = {'weight': '1.0'}

    atom_id_1_ = atom1['atom_id'][0]
    atom_id_2_ = atom2['atom_id'][0]

    if (atom_id_1_ == 'F' and atom_id_2_ in protonBeginCode) or (atom_id_2_ == 'F' and atom_id_1_ in protonBeginCode):
        dstFunc['lower_limit'] = '1.2'
        dstFunc['upper_limit'] = '1.5'

    elif (atom_id_1_ == 'F' and atom_id_2_ == 'F') or (atom_id_2_ == 'F' and atom_id_1_ == 'F'):
        dstFunc['lower_limit'] = '2.2'
        dstFunc['upper_limit'] = '2.5'

    elif (atom_id_1_ == 'O' and atom_id_2_ in protonBeginCode) or (atom_id_2_ == 'O' and atom_id_1_ in protonBeginCode):
        dstFunc['lower_limit'] = '1.5'
        dstFunc['upper_limit'] = '2.5'

    elif (atom_id_1_ == 'O' and atom_id_2_ == 'N') or (atom_id_2_ == 'O' and atom_id_1_ == 'N'):
        dstFunc['lower_limit'] = '2.5'
        dstFunc['upper_limit'] = '3.5'

    elif (atom_id_1_ == 'O' and atom_id_2_ == 'O') or (atom_id_2_ == 'O' and atom_id_1_ == 'O'):
        dstFunc['lower_limit'] = '2.5'
        dstFunc['upper_limit'] = '3.5'

    elif (atom_id_1_ == 'N' and atom_id_2_ in protonBeginCode) or (atom_id_2_ == 'N' and atom_id_1_ in protonBeginCode):
        dstFunc['lower_limit'] = '1.5'
        dstFunc['upper_limit'] = '2.5'

    elif (atom_id_1_ == 'N' and atom_id_2_ == 'N') or (atom_id_2_ == 'N' and atom_id_1_ == 'N'):
        dstFunc['lower_limit'] = '2.5'
        dstFunc['upper_limit'] = '3.5'

    return getDstFuncAsNoe()


def getDstFuncForSsBond(atom1: dict, atom2: dict) -> dict:
    """ Return default upper/lower limits for a disulfide bond.
    """

    dstFunc = {'weight': '1.0'}

    atom_id_1 = atom1['atom_id']
    atom_id_2 = atom2['atom_id']

    atom_id_1_ = atom_id_1[0]
    atom_id_2_ = atom_id_2[0]

    if atom_id_1_ == 'S' and atom_id_2_ == 'S' and not atom_id_1.startswith('SE') and not atom_id_2.startswith('SE'):
        dstFunc['lower_limit'] = '1.9'
        dstFunc['upper_limit'] = '2.3'

    elif atom_id_1.startswith('SE') and atom_id_2.startswith('SE'):
        dstFunc['lower_limit'] = '2.1'
        dstFunc['upper_limit'] = '2.6'

    return dstFunc


def getDstFuncAsNoe() -> dict:
    """ Return default upper/lower limits as an NOE.
    """

    return {'weight': '1.0', 'lower_limit': '2.0', 'upper_limit': str(DIST_AMBIG_MED)}


def getRowForStrMr(contentSubtype: str, id: int, indexId: int, memberId: Optional[int], code: Optional[str],
                   listId: int, entryId: str, originalTagNames: List[str], originalRow: List[Any],
                   authToStarSeq: Optional[dict], authToOrigSeq: Optional[dict],
                   authToInsCode: Optional[dict], offsetHolder: dict,
                   atoms: List[dict], annotationMode: bool) -> List[Any]:
    """ Return row data for a given constraint subtype and corresponding NMR-STAR row.
        @return: data array
    """

    has_ins_code = authToInsCode is not None and contentSubtype in NMR_STAR_LP_DATA_ITEMS_INS_CODE

    key_size = len(NMR_STAR_LP_KEY_ITEMS[contentSubtype])
    data_size = len(NMR_STAR_LP_DATA_ITEMS_INS_CODE[contentSubtype]) if has_ins_code else len(NMR_STAR_LP_DATA_ITEMS[contentSubtype])

    float_row_idx = []

    row = [None] * (key_size + data_size)

    row[0] = id

    atom_dim_num = len(atoms)

    atom1 = atoms[0]
    atom2 = atoms[1] if atom_dim_num > 1 else None
    atom3 = atoms[2] if atom_dim_num > 2 else None
    atom4 = atoms[3] if atom_dim_num > 3 else None
    atom5 = atoms[4] if atom_dim_num > 4 else None

    if code == 'OR' or isinstance(memberId, int):
        if atom1 is not None:
            atom1 = copy.copy(atom1)
        if atom2 is not None:
            atom2 = copy.copy(atom2)
        if atom3 is not None:
            atom3 = copy.copy(atom3)
        if atom4 is not None:
            atom4 = copy.copy(atom4)
        if atom5 is not None:
            atom5 = copy.copy(atom5)

    if isinstance(atom1, list):
        atom1 = atom1[0] if len(atom1) > 0 else None
    if atom2 is not None and isinstance(atom2, list):
        atom2 = atom2[0] if len(atom2) > 0 else None
    if atom3 is not None and isinstance(atom3, list):
        atom3 = atom3[0] if len(atom3) > 0 else None
    if atom4 is not None and isinstance(atom4, list):
        atom4 = atom4[0] if len(atom4) > 0 else None
    if atom5 is not None and isinstance(atom5, list):
        atom5 = atom5[0] if len(atom5) > 0 else None

    star_atom1, star_atom2, star_atom3, star_atom4, star_atom5 = None, None, None, None, None
    ins_code1, ins_code2, ins_code3, ins_code4 = None, None, None, None

    if atom1 is not None:
        star_atom1 = getStarAtom(authToStarSeq, authToOrigSeq, offsetHolder, atom1, atom2)
        if star_atom1 is None:
            star_atom1 = getStarAtom(authToStarSeq, authToOrigSeq, offsetHolder, atom1)
        if 'atom_id' not in atom1:
            atom1['atom_id'] = None
        ins_code1 = getInsCode(authToInsCode, offsetHolder, atom1)

    if atom2 is not None:
        star_atom2 = getStarAtom(authToStarSeq, authToOrigSeq, offsetHolder, atom2, atom1)
        if star_atom2 is None:
            star_atom2 = getStarAtom(authToStarSeq, authToOrigSeq, offsetHolder, atom2)
        if 'atom_id' not in atom2:
            atom2['atom_id'] = None
        ins_code2 = getInsCode(authToInsCode, offsetHolder, atom2)

    if atom3 is not None:
        star_atom3 = getStarAtom(authToStarSeq, authToOrigSeq, offsetHolder, atom3, atom1)
        if star_atom3 is None:
            star_atom3 = getStarAtom(authToStarSeq, authToOrigSeq, offsetHolder, atom3)
        if 'atom_id' not in atom3:
            atom3['atom_id'] = None
        ins_code3 = getInsCode(authToInsCode, offsetHolder, atom3)

    if atom4 is not None:
        star_atom4 = getStarAtom(authToStarSeq, authToOrigSeq, offsetHolder, atom4, atom1)
        if star_atom4 is None:
            star_atom4 = getStarAtom(authToStarSeq, authToOrigSeq, offsetHolder, atom4)
        if 'atom_id' not in atom4:
            atom4['atom_id'] = None
        ins_code4 = getInsCode(authToInsCode, offsetHolder, atom4)

    if atom5 is not None:
        star_atom5 = getStarAtom(authToStarSeq, authToOrigSeq, offsetHolder, atom5, atom1)
        if star_atom5 is None:
            star_atom5 = getStarAtom(authToStarSeq, authToOrigSeq, offsetHolder, atom5)
        if 'atom_id' not in atom5:
            atom5['atom_id'] = None

    if star_atom1 is None and star_atom2 is not None:  # procs
        row[1], row[2], row[3], row[4], row[5] =\
            star_atom2['chain_id'], star_atom2['entity_id'], star_atom2['seq_id'], star_atom2['comp_id'], star_atom2['atom_id']
    elif contentSubtype != 'fchiral_restraint':
        if star_atom1 is not None:
            row[1], row[2], row[3], row[4], row[5] =\
                star_atom1['chain_id'], star_atom1['entity_id'], star_atom1['seq_id'], star_atom1['comp_id'], star_atom1['atom_id']
        if star_atom2 is not None:
            row[6], row[7], row[8], row[9], row[10] =\
                star_atom2['chain_id'], star_atom2['entity_id'], star_atom2['seq_id'], star_atom2['comp_id'], star_atom2['atom_id']
    else:
        if star_atom1 is not None:
            row[1], row[2], row[3], row[4], row[5] =\
                star_atom1['chain_id'], star_atom1['entity_id'], star_atom1['seq_id'], star_atom1['comp_id'], star_atom1['auth_atom_id']
        if star_atom2 is not None:
            row[6], row[7], row[8], row[9], row[10] =\
                star_atom2['chain_id'], star_atom2['entity_id'], star_atom2['seq_id'], star_atom2['comp_id'], star_atom2['auth_atom_id']

    if contentSubtype in ('dist_restraint', 'dihed_restraint', 'rdc_restraint'):
        row[key_size] = indexId

    row[-2] = listId
    row[-1] = entryId

    def get_row_value(tag):
        if tag not in originalTagNames:
            return None

        val = originalRow[originalTagNames.index(tag)]

        if val in emptyValue:
            return None

        return val

    if contentSubtype == 'dist_restraint':
        val = get_row_value('Combination_ID')
        if val is not None:
            row[key_size + 1] = val

        row[key_size + 2] = memberId
        row[key_size + 3] = code

        val = get_row_value('Target_val')
        if val is not None:
            row[key_size + 4] = val
            float_row_idx.append(key_size + 4)
        val = get_row_value('Target_val_uncertainty')
        if val is not None:
            row[key_size + 5] = str(abs(float(val)))
            float_row_idx.append(key_size + 5)
        val = get_row_value('Lower_linear_limit')
        if val is not None:
            row[key_size + 6] = val
            float_row_idx.append(key_size + 6)
        val = get_row_value('Distance_lower_bound_val')
        if val is not None:
            row[key_size + 7] = val
            float_row_idx.append(key_size + 7)
        val = get_row_value('Distance_upper_bound_val')
        if val is not None:
            row[key_size + 8] = val
            float_row_idx.append(key_size + 8)
        val = get_row_value('Upper_linear_limit')
        if val is not None:
            row[key_size + 9] = str(abs(float(val)))
            float_row_idx.append(key_size + 9)
        val = get_row_value('Weight')
        if val is not None:
            row[key_size + 10] = val
        val = get_row_value('Distance_val')
        if val is not None:
            row[key_size + 11] = val

        if atom1 is not None:
            row[key_size + 12], row[key_size + 13], row[key_size + 14], row[key_size + 15] =\
                atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id']
        if annotationMode:
            val = get_row_value('Auth_atom_name_1')
            if val is not None:
                row[key_size + 16] = val
        elif has_key_value(atom1, 'auth_atom_id'):
            row[key_size + 16] = atom1['auth_atom_id']
        if atom2 is not None:
            row[key_size + 17], row[key_size + 18], row[key_size + 19], row[key_size + 20] =\
                atom2['chain_id'], atom2['seq_id'], atom2['comp_id'], atom2['atom_id']
        if annotationMode:
            val = get_row_value('Auth_atom_name_2')
            if val is not None:
                row[key_size + 21] = val
        elif has_key_value(atom2, 'auth_atom_id'):
            row[key_size + 21] = atom2['auth_atom_id']

        if authToInsCode is not None:
            row[key_size + 22] = ins_code1
            row[key_size + 23] = ins_code2

    elif contentSubtype == 'dihed_restraint':
        if star_atom3 is not None:
            row[11], row[12], row[13], row[14], row[15] =\
                star_atom3['chain_id'], star_atom3['entity_id'], star_atom3['seq_id'], star_atom3['comp_id'], star_atom3['atom_id']
        if star_atom4 is not None:
            row[16], row[17], row[18], row[19], row[20] =\
                star_atom4['chain_id'], star_atom4['entity_id'], star_atom4['seq_id'], star_atom4['comp_id'], star_atom4['atom_id']

        val = get_row_value('Combination_ID')
        if val is not None:
            row[key_size + 1] = val
        val = get_row_value('Torsion_angle_name')
        if val is not None:
            row[key_size + 2] = val
        val = get_row_value('Angle_target_val')
        if val is not None:
            row[key_size + 3] = val
            float_row_idx.append(key_size + 3)
        val = get_row_value('Angle_target_val_err')
        if val is not None:
            row[key_size + 4] = str(abs(float(val)))
            float_row_idx.append(key_size + 4)
        val = get_row_value('Angle_lower_linear_limit')
        if val is not None:
            row[key_size + 5] = val
            float_row_idx.append(key_size + 5)
        val = get_row_value('Angle_lower_bound_val')
        if val is not None:
            row[key_size + 6] = val
            float_row_idx.append(key_size + 6)
        val = get_row_value('Angle_upper_bound_val')
        if val is not None:
            row[key_size + 7] = val
            float_row_idx.append(key_size + 7)
        val = get_row_value('Angle_upper_linear_limit')
        if val is not None:
            row[key_size + 8] = val
            float_row_idx.append(key_size + 8)
        val = get_row_value('Weight')
        if val is not None:
            row[key_size + 9] = str(abs(float(val)))

        if atom1 is not None:
            row[key_size + 10], row[key_size + 11], row[key_size + 12], row[key_size + 13] =\
                atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id']
        if annotationMode:
            val = get_row_value('Auth_atom_name_1')
            if val is not None:
                row[key_size + 14] = val
        elif has_key_value(atom1, 'auth_atom_id'):
            row[key_size + 14] = atom1['auth_atom_id']
        if atom2 is not None:
            row[key_size + 15], row[key_size + 16], row[key_size + 17], row[key_size + 18] =\
                atom2['chain_id'], atom2['seq_id'], atom2['comp_id'], atom2['atom_id']
        if annotationMode:
            val = get_row_value('Auth_atom_name_2')
            if val is not None:
                row[key_size + 19] = val
        elif has_key_value(atom2, 'auth_atom_id'):
            row[key_size + 19] = atom2['auth_atom_id']
        if atom3 is not None:
            row[key_size + 20], row[key_size + 21], row[key_size + 22], row[key_size + 23] =\
                atom3['chain_id'], atom3['seq_id'], atom3['comp_id'], atom3['atom_id']
        if annotationMode:
            val = get_row_value('Auth_atom_name_3')
            if val is not None:
                row[key_size + 24] = val
        elif has_key_value(atom3, 'auth_atom_id'):
            row[key_size + 24] = atom3['auth_atom_id']
        if atom4 is not None:
            row[key_size + 25], row[key_size + 26], row[key_size + 27], row[key_size + 28] =\
                atom4['chain_id'], atom4['seq_id'], atom4['comp_id'], atom4['atom_id']
        if annotationMode:
            val = get_row_value('Auth_atom_name_4')
            if val is not None:
                row[key_size + 29] = val
        elif has_key_value(atom4, 'auth_atom_id'):
            row[key_size + 29] = atom4['auth_atom_id']

        if authToInsCode is not None:
            row[key_size + 30] = ins_code1
            row[key_size + 31] = ins_code2
            row[key_size + 32] = ins_code3
            row[key_size + 33] = ins_code4

    elif contentSubtype == 'rdc_restraint':
        val = get_row_value('Combination_ID')
        if val is not None:
            row[key_size + 1] = val
        val = get_row_value('Target_value')
        if val is not None:
            row[key_size + 2] = str(abs(float(val)))
            float_row_idx.append(key_size + 2)
        val = get_row_value('Target_value_uncertainty')
        if val is not None:
            row[key_size + 3] = val
            float_row_idx.append(key_size + 3)
        val = get_row_value('RDC_lower_linear_limit')
        if val is not None:
            row[key_size + 4] = val
            float_row_idx.append(key_size + 4)
        val = get_row_value('RDC_lower_bound')
        if val is not None:
            row[key_size + 5] = val
            float_row_idx.append(key_size + 5)
        val = get_row_value('RDC_upper_bound')
        if val is not None:
            row[key_size + 6] = val
            float_row_idx.append(key_size + 6)
        val = get_row_value('RDC_upper_linear_limit')
        if val is not None:
            row[key_size + 7] = val
            float_row_idx.append(key_size + 7)
        val = get_row_value('Weight')
        if val is not None:
            row[key_size + 8] = str(abs(float(val)))
        val = get_row_value('RDC_val')
        if val is not None:
            row[key_size + 9] = val
            float_row_idx.append(key_size + 9)
        val = get_row_value('RDC_val_err')
        if val is not None:
            row[key_size + 10] = str(abs(float(val)))
            float_row_idx.append(key_size + 10)
        val = get_row_value('RDC_val_scale_factor')
        if val is not None:
            row[key_size + 11] = str(abs(float(val)))
        val = get_row_value('RDC_distance_dependent')
        if val is not None:
            row[key_size + 12] = val

        if atom1 is not None:
            row[key_size + 13], row[key_size + 14], row[key_size + 15], row[key_size + 16] =\
                atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id']
        if annotationMode:
            val = get_row_value('Auth_atom_name_1')
            if val is not None:
                row[key_size + 17] = val
        elif has_key_value(atom1, 'auth_atom_id'):
            row[key_size + 17] = atom1['auth_atom_id']
        if atom2 is not None:
            row[key_size + 18], row[key_size + 19], row[key_size + 20], row[key_size + 21] =\
                atom2['chain_id'], atom2['seq_id'], atom2['comp_id'], atom2['atom_id']
        if annotationMode:
            val = get_row_value('Auth_atom_name_2')
            if val is not None:
                row[key_size + 22] = val
        elif has_key_value(atom2, 'auth_atom_id'):
            row[key_size + 22] = atom2['auth_atom_id']

        if authToInsCode is not None:
            row[key_size + 23] = ins_code1
            row[key_size + 24] = ins_code2

    elif contentSubtype == 'noepk_restraint':
        val = get_row_value('Val')
        if val is not None:
            row[key_size] = val
            float_row_idx.append(key_size)
        val = get_row_value('Val_err')
        if val is not None:
            row[key_size + 1] = str(abs(float(val)))
            float_row_idx.append(key_size + 1)
        val = get_row_value('Val_min')
        if val is not None:
            row[key_size + 2] = val
            float_row_idx.append(key_size + 2)
        val = get_row_value('Val_max')
        if val is not None:
            row[key_size + 3] = val
            float_row_idx.append(key_size + 3)

        if atom1 is not None:
            row[key_size + 4], row[key_size + 5], row[key_size + 6], row[key_size + 7] =\
                atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id']
        if atom2 is not None:
            row[key_size + 8], row[key_size + 9], row[key_size + 10], row[key_size + 11] =\
                atom2['chain_id'], atom2['seq_id'], atom2['comp_id'], atom2['atom_id']

    elif contentSubtype == 'jcoup_restraint':
        if star_atom3 is not None:
            row[11], row[12], row[13], row[14], row[15] =\
                star_atom3['chain_id'], star_atom3['entity_id'], star_atom3['seq_id'], star_atom3['comp_id'], star_atom3['atom_id']
        if star_atom4 is not None:
            row[16], row[17], row[18], row[19], row[20] =\
                star_atom4['chain_id'], star_atom4['entity_id'], star_atom4['seq_id'], star_atom4['comp_id'], star_atom4['atom_id']

        val = get_row_value('Coupling_constant_val')
        if val is not None:
            row[key_size] = val
            float_row_idx.append(key_size)
        val = get_row_value('Coupling_constant_err')
        if val is not None:
            row[key_size + 1] = str(abs(float(val)))
            float_row_idx.append(key_size + 1)
        val = get_row_value('Coupling_constant_lower_bound')
        if val is not None:
            row[key_size + 2] = val
            float_row_idx.append(key_size + 2)
        val = get_row_value('Coupling_constant_upper_bound')
        if val is not None:
            row[key_size + 3] = val
            float_row_idx.append(key_size + 3)

        if atom1 is not None:
            row[key_size + 4], row[key_size + 5], row[key_size + 6], row[key_size + 7] =\
                atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id']
        if atom2 is not None:
            row[key_size + 8], row[key_size + 9], row[key_size + 10], row[key_size + 11] =\
                atom2['chain_id'], atom2['seq_id'], atom2['comp_id'], atom2['atom_id']
        if atom3 is not None:
            row[key_size + 12], row[key_size + 13], row[key_size + 14], row[key_size + 15] =\
                atom3['chain_id'], atom3['seq_id'], atom3['comp_id'], atom3['atom_id']
        if atom4 is not None:
            row[key_size + 16], row[key_size + 17], row[key_size + 18], row[key_size + 19] =\
                atom4['chain_id'], atom4['seq_id'], atom4['comp_id'], atom4['atom_id']

    elif contentSubtype == 'rdc_raw_data':
        row[key_size] = getRdcCode([atom1, atom2])
        if atom1 is not None:
            row[key_size + 1] = atomType = atom1['atom_id'][0]
            row[key_size + 2] = ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS[atomType][0]
        val = get_row_value('Ambiguity_code_1')
        if val is not None and val in ('1', '2', '3'):
            row[key_size + 3] = val
        if atom2 is not None:
            row[key_size + 4] = atomType = atom2['atom_id'][0]
            row[key_size + 5] = ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS[atomType][0]
        val = get_row_value('Ambiguity_code_2')
        if val is not None and val in ('1', '2', '3'):
            row[key_size + 6] = val
            val = get_row_value('Val')
        if val is not None:
            row[key_size + 7] = val
            float_row_idx.append(key_size + 7)
        val = get_row_value('Val_err')
        if val is not None:
            row[key_size + 8] = str(abs(float(val)))
            float_row_idx.append(key_size + 8)
        val = get_row_value('Val_min')
        if val is not None:
            row[key_size + 9] = val
            float_row_idx.append(key_size + 9)
        val = get_row_value('Val_max')
        if val is not None:
            row[key_size + 10] = val
        val = get_row_value('Val_bond_length')
        if val is not None:
            row[key_size + 11] = val

        if atom1 is not None:
            row[key_size + 12], row[key_size + 13], row[key_size + 14], row[key_size + 15] =\
                atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id']
        if atom2 is not None:
            row[key_size + 16], row[key_size + 17], row[key_size + 18], row[key_size + 19] =\
                atom2['chain_id'], atom2['seq_id'], atom2['comp_id'], atom2['atom_id']

    elif contentSubtype == 'csa_restraint':
        row[key_size] = atomType = atom1['atom_id'][0]
        row[key_size + 1] = ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS[atomType][0]
        val = get_row_value('Val')
        if val is not None:
            row[key_size + 2] = val
            float_row_idx.append(key_size + 2)
        val = get_row_value('Val_err')
        if val is not None:
            row[key_size + 3] = str(abs(float(val)))
            float_row_idx.append(key_size + 3)
        val = get_row_value('Principal_value_sigma_11_val')
        if val is not None:
            row[key_size + 4] = val
        val = get_row_value('Principal_value_sigma_22_val')
        if val is not None:
            row[key_size + 5] = val
        val = get_row_value('Principal_value_sigma_33_val')
        if val is not None:
            row[key_size + 6] = val
        val = get_row_value('Principal_Euler_angle_alpha_val')
        if val is not None:
            row[key_size + 7] = val
        val = get_row_value('Principal_Euler_angle_beta_val')
        if val is not None:
            row[key_size + 8] = val
        val = get_row_value('Principal_Euler_angle_gamma_val')
        if val is not None:
            row[key_size + 9] = val
        val = get_row_value('Bond_length')
        if val is not None:
            row[key_size + 10] = val

        if atom1 is not None:
            row[key_size + 11], row[key_size + 12], row[key_size + 13], row[key_size + 14] =\
                atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id']

    elif contentSubtype == 'ddc_restraint':
        val = get_row_value('Dipolar_coupling_code')
        if val is not None:
            row[key_size] = val
        if atom1 is not None:
            row[key_size + 1] = atomType = atom1['atom_id'][0]
            row[key_size + 2] = ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS[atomType][0]
        val = get_row_value('Ambiguity_code_1')
        if val is not None and val in ('1', '2', '3'):
            row[key_size + 3] = val
        if atom2 is not None:
            row[key_size + 4] = atomType = atom2['atom_id'][0]
            row[key_size + 5] = ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS[atomType][0]
        val = get_row_value('Ambiguity_code_2')
        if val is not None and val in ('1', '2', '3'):
            row[key_size + 6] = val
        val = get_row_value('Val')
        if val is not None:
            row[key_size + 7] = str(abs(float(val)))
            float_row_idx.append(key_size + 7)
        val = get_row_value('Val_err')
        if val is not None:
            row[key_size + 8] = val
            float_row_idx.append(key_size + 8)
        val = get_row_value('Val_min')
        if val is not None:
            row[key_size + 9] = val
            float_row_idx.append(key_size + 9)
        val = get_row_value('Val_max')
        if val is not None:
            row[key_size + 10] = val
            float_row_idx.append(key_size + 10)
        val = get_row_value('Principal_Euler_angle_alpha_val')
        if val is not None:
            row[key_size + 11] = val
        val = get_row_value('Principal_Euler_angle_beta_val')
        if val is not None:
            row[key_size + 12] = val
        val = get_row_value('Principal_Euler_angle_gamma_val')
        if val is not None:
            row[key_size + 13] = val

        if atom1 is not None:
            row[key_size + 14], row[key_size + 15], row[key_size + 16], row[key_size + 17] =\
                atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id']
        if atom2 is not None:
            row[key_size + 18], row[key_size + 19], row[key_size + 20], row[key_size + 21] =\
                atom2['chain_id'], atom2['seq_id'], atom2['comp_id'], atom2['atom_id']

    elif contentSubtype == 'hvycs_restraint':
        if star_atom3 is not None:
            row[11], row[12], row[13], row[14], row[15] =\
                star_atom3['chain_id'], star_atom3['entity_id'], star_atom3['seq_id'], star_atom3['comp_id'], star_atom3['atom_id']
        if star_atom4 is not None:
            row[16], row[17], row[18], row[19], row[20] =\
                star_atom4['chain_id'], star_atom4['entity_id'], star_atom4['seq_id'], star_atom4['comp_id'], star_atom4['atom_id']
        if star_atom5 is not None:
            row[21], row[22], row[23], row[24], row[25] =\
                star_atom5['chain_id'], star_atom5['entity_id'], star_atom5['seq_id'], star_atom5['comp_id'], star_atom5['atom_id']

        val = get_row_value('CA_chem_shift_val')
        if val is not None:
            row[key_size] = val
            float_row_idx.append(key_size)
        val = get_row_value('CA_chem_shift_val_err')
        if val is not None:
            row[key_size + 1] = str(abs(float(val)))
            float_row_idx.append(key_size + 1)
        val = get_row_value('CB_chem_shift_val')
        if val is not None:
            row[key_size + 2] = val
            float_row_idx.append(key_size + 2)
        val = get_row_value('CB_chem_shift_val_err')
        if val is not None:
            row[key_size + 3] = str(abs(float(val)))
            float_row_idx.append(key_size + 3)

        if atom1 is not None:
            row[key_size + 4], row[key_size + 5], row[key_size + 6], row[key_size + 7] =\
                atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id']
        if atom2 is not None:
            row[key_size + 8], row[key_size + 9], row[key_size + 10], row[key_size + 11] =\
                atom2['chain_id'], atom2['seq_id'], atom2['comp_id'], atom2['atom_id']
        if atom3 is not None:
            row[key_size + 12], row[key_size + 13], row[key_size + 14], row[key_size + 15] =\
                atom3['chain_id'], atom3['seq_id'], atom3['comp_id'], atom3['atom_id']
        if atom4 is not None:
            row[key_size + 16], row[key_size + 17], row[key_size + 18], row[key_size + 19] =\
                atom4['chain_id'], atom4['seq_id'], atom4['comp_id'], atom4['atom_id']
        if atom5 is not None:
            row[key_size + 20], row[key_size + 21], row[key_size + 22], row[key_size + 23] =\
                atom5['chain_id'], atom5['seq_id'], atom5['comp_id'], atom5['atom_id']

    elif contentSubtype == 'procs_restraint':
        if atom1 is not None:
            row[key_size] = atomType = atom1['atom_id'][0]
            row[key_size + 1] = ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS[atomType][0]
        val = get_row_value('Chem_shift_val')
        if val is not None:
            row[key_size + 2] = val
            float_row_idx.append(key_size + 2)
        val = get_row_value('Chem_shift_val_err')
        if val is not None:
            row[key_size + 3] = str(abs(float(val)))
            float_row_idx.append(key_size + 3)

        if atom1 is None:
            row[key_size + 4], row[key_size + 5], row[key_size + 6], row[key_size + 7] =\
                atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id']

    elif contentSubtype == 'csp_restraint':
        if atom1 is not None:
            row[key_size] = atomType = atom1['atom_id'][0]
            row[key_size + 1] = ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS[atomType][0]
        val = get_row_value('Chem_shift_val')
        if val is not None:
            row[key_size + 2] = val
            float_row_idx.append(key_size + 2)
        val = get_row_value('Chem_shift_val_err')
        if val is not None:
            row[key_size + 3] = str(abs(float(val)))
            float_row_idx.append(key_size + 3)
        val = get_row_value('Difference_chem_shift_val')
        if val is not None:
            row[key_size + 4] = val
            float_row_idx.append(key_size + 4)
        val = get_row_value('Difference_chem_shift_val_err')
        if val is not None:
            row[key_size + 5] = str(abs(float(val)))
            float_row_idx.append(key_size + 5)

        if atom1 is not None:
            row[key_size + 6], row[key_size + 7], row[key_size + 8], row[key_size + 9] =\
                atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id']

    elif contentSubtype == 'auto_relax_restraint':
        if atom1 is not None:
            row[key_size] = atomType = atom1['atom_id'][0]
            row[key_size + 1] = ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS[atomType][0]
        val = get_row_value('Auto_relaxation_val')
        if val is not None:
            row[key_size + 2] = val
            float_row_idx.append(key_size + 2)
        val = get_row_value('Auto_relaxation_val_err')
        if val is not None:
            row[key_size + 3] = str(abs(float(val)))
            float_row_idx.append(key_size + 3)
        val = get_row_value('Rex_val')
        if val is not None:
            row[key_size + 4] = val
            float_row_idx.append(key_size + 4)
        val = get_row_value('Rex_val_err')
        if val is not None:
            row[key_size + 5] = str(abs(float(val)))
            float_row_idx.append(key_size + 5)

        if atom1 is not None:
            row[key_size + 6], row[key_size + 7], row[key_size + 8], row[key_size + 9] =\
                atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id']

    elif contentSubtype == 'heteronucl_noe_data':
        if atom1 is not None:
            row[key_size] = atomType = atom1['atom_id'][0]
            row[key_size + 1] = ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS[atomType][0]
        if atom2 is not None:
            row[key_size + 2] = atomType = atom2['atom_id'][0]
            row[key_size + 3] = ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS[atomType][0]
        val = get_row_value('Val')
        if val is not None:
            row[key_size + 4] = val
            float_row_idx.append(key_size + 4)
        val = get_row_value('Val_err')
        if val is not None:
            row[key_size + 5] = val
            float_row_idx.append(key_size + 5)

        if atom1 is not None:
            row[key_size + 6], row[key_size + 7], row[key_size + 8], row[key_size + 9] =\
                atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id']
        if atom2 is not None:
            row[key_size + 10], row[key_size + 11], row[key_size + 12], row[key_size + 13] =\
                atom2['chain_id'], atom2['seq_id'], atom2['comp_id'], atom2['atom_id']

    elif contentSubtype == 'heteronucl_t1_data':
        if atom1 is not None:
            row[key_size] = atomType = atom1['atom_id'][0]
            row[key_size + 1] = ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS[atomType][0]
        val = get_row_value('Val')
        if val is not None:
            row[key_size + 2] = val
            float_row_idx.append(key_size + 2)
        val = get_row_value('Val_err')
        if val is not None:
            row[key_size + 3] = val
            float_row_idx.append(key_size + 3)

        if atom1 is not None:
            row[key_size + 4], row[key_size + 5], row[key_size + 6], row[key_size + 7] =\
                atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id']

    elif contentSubtype == 'heteronucl_t2_data':
        if atom1 is not None:
            row[key_size] = atomType = atom1['atom_id'][0]
            row[key_size + 1] = ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS[atomType][0]
        val = get_row_value('T2_val')
        if val is not None:
            row[key_size + 2] = val
            float_row_idx.append(key_size + 2)
        val = get_row_value('T2_val_err')
        if val is not None:
            row[key_size + 3] = val
            float_row_idx.append(key_size + 3)
        val = get_row_value('Rex_val')
        if val is not None:
            row[key_size + 4] = val
            float_row_idx.append(key_size + 4)
        val = get_row_value('Rex_err')
        if val is not None:
            row[key_size + 5] = val
            float_row_idx.append(key_size + 5)

        if atom1 is not None:
            row[key_size + 6], row[key_size + 7], row[key_size + 8], row[key_size + 9] =\
                atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id']

    elif contentSubtype == 'heteronucl_t1r_data':
        if atom1 is not None:
            row[key_size] = atomType = atom1['atom_id'][0]
            row[key_size + 1] = ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS[atomType][0]
        val = get_row_value('T1rho_val')
        if val is not None:
            row[key_size + 2] = val
            float_row_idx.append(key_size + 2)
        val = get_row_value('T1rho_val_err')
        if val is not None:
            row[key_size + 3] = val
            float_row_idx.append(key_size + 3)
        val = get_row_value('Rex_val')
        if val is not None:
            row[key_size + 4] = val
            float_row_idx.append(key_size + 4)
        val = get_row_value('Rex_val_err')
        if val is not None:
            row[key_size + 5] = val
            float_row_idx.append(key_size + 5)

        if atom1 is not None:
            row[key_size + 6], row[key_size + 7], row[key_size + 8], row[key_size + 9] =\
                atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id']

    elif contentSubtype == 'order_param_data':
        if atom1 is not None:
            row[key_size] = atomType = atom1['atom_id'][0]
            row[key_size + 1] = ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS[atomType][0]
        val = get_row_value('Order_param_val')
        if val is not None:
            row[key_size + 2] = val
            float_row_idx.append(key_size + 2)
        val = get_row_value('Order_param_val_fit_err')
        if val is not None:
            row[key_size + 3] = val
            float_row_idx.append(key_size + 3)
        val = get_row_value('Tau_e_val')
        if val is not None:
            row[key_size + 4] = val
            float_row_idx.append(key_size + 4)
        val = get_row_value('Tau_e_val_fit_err')
        if val is not None:
            row[key_size + 5] = val
            float_row_idx.append(key_size + 5)
        val = get_row_value('Tau_f_val')
        if val is not None:
            row[key_size + 6] = val
            float_row_idx.append(key_size + 6)
        val = get_row_value('Tau_f_val_fit_err')
        if val is not None:
            row[key_size + 7] = val
            float_row_idx.append(key_size + 7)
        val = get_row_value('Tau_s_val')
        if val is not None:
            row[key_size + 8] = val
            float_row_idx.append(key_size + 8)
        val = get_row_value('Tau_s_val_fit_err')
        if val is not None:
            row[key_size + 9] = val
            float_row_idx.append(key_size + 9)
        val = get_row_value('Rex_val')
        if val is not None:
            row[key_size + 10] = val
            float_row_idx.append(key_size + 10)
        val = get_row_value('Rex_val_fit_err')
        if val is not None:
            row[key_size + 11] = val
            float_row_idx.append(key_size + 11)
        val = get_row_value('Model_free_sum_squared_errs')
        if val is not None:
            row[key_size + 12] = val
            float_row_idx.append(key_size + 12)
        val = get_row_value('Model_fit')
        if val is not None:
            row[key_size + 13] = val
        val = get_row_value('Sf2_val')
        if val is not None:
            row[key_size + 14] = val
            float_row_idx.append(key_size + 14)
        val = get_row_value('Sf2_val_fit_err')
        if val is not None:
            row[key_size + 15] = val
            float_row_idx.append(key_size + 15)
        val = get_row_value('Ss2_val')
        if val is not None:
            row[key_size + 16] = val
            float_row_idx.append(key_size + 16)
        val = get_row_value('Ss2_val_fit_err')
        if val is not None:
            row[key_size + 17] = val
            float_row_idx.append(key_size + 17)
        val = get_row_value('SH2_val')
        if val is not None:
            row[key_size + 18] = val
            float_row_idx.append(key_size + 18)
        val = get_row_value('SH2_val_fit_err')
        if val is not None:
            row[key_size + 19] = val
            float_row_idx.append(key_size + 19)
        val = get_row_value('SN2_val')
        if val is not None:
            row[key_size + 20] = val
            float_row_idx.append(key_size + 20)
        val = get_row_value('SN2_val_fit_err')
        if val is not None:
            row[key_size + 21] = val
            float_row_idx.append(key_size + 21)

        if atom1 is not None:
            row[key_size + 22], row[key_size + 23], row[key_size + 24], row[key_size + 25] =\
                atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id']

    elif contentSubtype == 'ph_titr_data':
        if atom1 is not None:
            row[key_size] = atomType = atom1['atom_id'][0]
            row[key_size + 1] = ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS[atomType][0]
        if atom2 is not None:
            row[key_size + 2] = atomType = atom2['atom_id'][0]
            row[key_size + 3] = ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS[atomType][0]
        val = get_row_value('Hill_coeff_val')
        if val is not None:
            row[key_size + 4] = val
            float_row_idx.append(key_size + 4)
        val = get_row_value('Hill_coeff_val_fit_err')
        if val is not None:
            row[key_size + 5] = val
            float_row_idx.append(key_size + 5)
        val = get_row_value('High_PH_param_val')
        if val is not None:
            row[key_size + 6] = val
            float_row_idx.append(key_size + 6)
        val = get_row_value('High_PH_param_val_fit_err')
        if val is not None:
            row[key_size + 7] = val
            float_row_idx.append(key_size + 7)
        val = get_row_value('Low_PH_param_val')
        if val is not None:
            row[key_size + 8] = val
            float_row_idx.append(key_size + 8)
        val = get_row_value('Low_PH_param_val_fit_err')
        if val is not None:
            row[key_size + 9] = val
            float_row_idx.append(key_size + 9)
        val = get_row_value('PKa_val')
        if val is not None:
            row[key_size + 10] = val
            float_row_idx.append(key_size + 10)
        val = get_row_value('PKa_val_fit_err')
        if val is not None:
            row[key_size + 11] = val
            float_row_idx.append(key_size + 11)
        val = get_row_value('PHmid_val')
        if val is not None:
            row[key_size + 12] = val
            float_row_idx.append(key_size + 12)
        val = get_row_value('PHmid_val_fit_err')
        if val is not None:
            row[key_size + 13] = val
            float_row_idx.append(key_size + 13)

        if atom1 is not None:
            row[key_size + 14], row[key_size + 15], row[key_size + 16], row[key_size + 17] =\
                atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id']

        if atom2 is not None:
            row[key_size + 18], row[key_size + 19], row[key_size + 20], row[key_size + 21] =\
                atom2['chain_id'], atom2['seq_id'], atom2['comp_id'], atom2['atom_id']

    elif contentSubtype == 'ph_param_data':
        val = get_row_value('PH_titr_result_ID')
        if val is not None:
            row[key_size] = val
        val = get_row_value('PH_val')
        if val is not None:
            row[key_size + 1] = val
            float_row_idx.append(key_size + 1)
        val = get_row_value('PH_val_err')
        if val is not None:
            row[key_size + 2] = val
            float_row_idx.append(key_size + 2)
        val = get_row_value('Observed_NMR_param_val')
        if val is not None:
            row[key_size + 3] = val
            float_row_idx.append(key_size + 3)
        val = get_row_value('Observed_NMR_param_val_err')
        if val is not None:
            row[key_size + 4] = val
            float_row_idx.append(key_size + 4)

    elif contentSubtype == 'coupling_const_data':
        val = get_row_value('Code')
        if val is not None:
            row[key_size] = val
        if atom1 is not None:
            row[key_size + 1] = atomType = atom1['atom_id'][0]
            row[key_size + 2] = ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS[atomType][0]
        val = get_row_value('Ambiguity_code_1')
        if val is not None and val in ('1', '2', '3'):
            row[key_size + 3] = val
        if atom2 is not None:
            row[key_size + 4] = atomType = atom2['atom_id'][0]
            row[key_size + 5] = ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS[atomType][0]
        val = get_row_value('Ambiguity_code_2')
        if val is not None and val in ('1', '2', '3'):
            row[key_size + 6] = val
        val = get_row_value('Val')
        if val is not None:
            row[key_size + 7] = str(abs(float(val)))
            float_row_idx.append(key_size + 7)
        val = get_row_value('Val_err')
        if val is not None:
            row[key_size + 8] = val
            float_row_idx.append(key_size + 8)
        val = get_row_value('Val_min')
        if val is not None:
            row[key_size + 9] = val
            float_row_idx.append(key_size + 9)
        val = get_row_value('Val_max')
        if val is not None:
            row[key_size + 10] = val
            float_row_idx.append(key_size + 10)

        if atom1 is not None:
            row[key_size + 11], row[key_size + 12], row[key_size + 13], row[key_size + 14] =\
                atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id']
        if atom2 is not None:
            row[key_size + 15], row[key_size + 16], row[key_size + 17], row[key_size + 18] =\
                atom2['chain_id'], atom2['seq_id'], atom2['comp_id'], atom2['atom_id']

    elif contentSubtype.startswith('ccr'):
        if star_atom3 is not None:
            row[11], row[12], row[13], row[14], row[15] =\
                star_atom3['chain_id'], star_atom3['entity_id'], star_atom3['seq_id'], star_atom3['comp_id'], star_atom3['atom_id']
        if star_atom4 is not None:
            row[16], row[17], row[18], row[19], row[20] =\
                star_atom4['chain_id'], star_atom4['entity_id'], star_atom4['seq_id'], star_atom4['comp_id'], star_atom4['atom_id']

        if atom1 is not None:
            row[key_size] = atomType = atom1['atom_id'][0]
            row[key_size + 1] = ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS[atomType][0]
        if atom2 is not None:
            row[key_size + 2] = atomType = atom2['atom_id'][0]
            row[key_size + 3] = ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS[atomType][0]
        if atom3 is not None:
            row[key_size + 4] = atomType = atom3['atom_id'][0]
            row[key_size + 5] = ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS[atomType][0]
        if atom4 is not None:
            row[key_size + 6] = atomType = atom4['atom_id'][0]
            row[key_size + 7] = ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS[atomType][0]
        val = get_row_value('Val')
        if val is not None:
            row[key_size + 8] = val
            float_row_idx.append(key_size + 8)
        val = get_row_value('Val_err')
        if val is not None:
            row[key_size + 9] = str(abs(float(val)))
            float_row_idx.append(key_size + 9)

        if atom1 is not None:
            row[key_size + 10], row[key_size + 11], row[key_size + 12], row[key_size + 13] =\
                atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['atom_id']
        if atom2 is not None:
            row[key_size + 14], row[key_size + 15], row[key_size + 16], row[key_size + 17] =\
                atom2['chain_id'], atom2['seq_id'], atom2['comp_id'], atom2['atom_id']
        if atom3 is not None:
            row[key_size + 18], row[key_size + 19], row[key_size + 20], row[key_size + 21] =\
                atom3['chain_id'], atom3['seq_id'], atom3['comp_id'], atom3['atom_id']
        if atom4 is not None:
            row[key_size + 22], row[key_size + 23], row[key_size + 24], row[key_size + 25] =\
                atom4['chain_id'], atom4['seq_id'], atom4['comp_id'], atom4['atom_id']

    elif contentSubtype == 'fchiral_restraint':
        val = get_row_value('Stereospecific_assignment_code')
        if val is not None:
            row[key_size] = val
        if atom1 is not None:
            row[key_size + 1], row[key_size + 2], row[key_size + 3], row[key_size + 4] =\
                atom1['chain_id'], atom1['seq_id'], atom1['comp_id'], atom1['auth_atom_id']
        if atom2 is not None:
            row[key_size + 5], row[key_size + 6], row[key_size + 7], row[key_size + 8] =\
                atom2['chain_id'], atom2['seq_id'], atom2['comp_id'], atom2['auth_atom_id']

    elif contentSubtype == 'saxs_restraint':
        row[1] = code
        val = get_row_value('Intensity_val')
        if val is not None:
            row[key_size] = val
        val = get_row_value('Intensity_err_val')
        if val is not None:
            row[key_size + 1] = val
        val = get_row_value('Weight_val')
        if val is not None:
            row[key_size + 2] = str(abs(float(val)))

    elif contentSubtype == 'other_restraint':
        if atom1 is not None:
            row[key_size] = atomType = atom1['atom_id'][0]
            row[key_size + 1] = ISOTOPE_NUMBERS_OF_NMR_OBS_NUCS[atomType][0]
        val = get_row_value('Val')
        if val is not None:
            row[key_size + 2] = val
            float_row_idx.append(key_size + 2)
        val = get_row_value('Val_err')
        if val is not None:
            row[key_size + 3] = str(abs(float(val)))
            float_row_idx.append(key_size + 3)

    if len(float_row_idx) > 0:
        max_eff_digits = 0
        for idx in float_row_idx:
            val = row[idx]
            if '.' in val and val[-1] == '0':
                period = val.index('.')
                last = len(val) - 1
                while val[last] == '0':
                    last -= 1
                eff_digits = last - period
                if eff_digits > 0 and eff_digits > max_eff_digits:
                    max_eff_digits = eff_digits
        for idx in float_row_idx:
            val = row[idx]
            if '.' in val and val[-1] == '0':
                first_digit = val.index('.') + 1
                eff_digits = len(val) - first_digit
                if 0 < max_eff_digits < eff_digits:
                    row[idx] = row[idx][0:first_digit + max_eff_digits]
                else:
                    row[idx] = row[idx][0:first_digit + 1]

    return row


def getAuxRow(mrSubtype: str, catName: str, listId: int, entryId: str, inDict: dict) -> Optional[List[Any]]:
    """ Return aux row data for a given category.
        @return: data array
    """

    contentSubtype = contentSubtypeOf(mrSubtype)

    if contentSubtype is None:
        return None

    if contentSubtype not in NMR_STAR_AUX_LP_CATEGORIES:
        return None

    if catName not in NMR_STAR_AUX_LP_CATEGORIES[contentSubtype]:
        return None

    key_names = [key['name'] for key in NMR_STAR_AUX_LP_KEY_ITEMS[contentSubtype][catName]]
    data_names = [data['name'] for data in NMR_STAR_AUX_LP_DATA_ITEMS[contentSubtype][catName]]

    key_names.extend(data_names)

    row = [None] * len(key_names)

    row[-2] = listId
    row[-1] = entryId

    for k, v in inDict.items():
        if k in key_names:
            row[key_names.index(k)] = v

    return row


def assignCoordPolymerSequenceWithChainId(caC: dict, nefT,
                                          refChainId: str, seqId: int, compId: str, atomId: str
                                          ) -> Tuple[List[Tuple[str, int, str, bool]], str]:
    """ Assign polymer sequences of the coordinates.
        @return possible assignments to the coordinate, warning message (None for valid case)
    """

    warningMessage = None

    polySeq = caC['polymer_sequence']
    altPolySeq = caC['alt_polymer_sequence']
    nonPoly = caC['non_polymer']
    branched = caC['branched']
    authToLabelSeq = caC['auth_to_label_seq']

    hasNonPoly = nonPoly is not None and len(nonPoly) > 0
    hasBranched = branched is not None and len(branched) > 0

    nonPolySeq = None

    chainAssign = set()
    _seqId = seqId

    for ps in polySeq:
        chainId, seqId = getRealChainSeqId(nefT.get_ccu(), ps, _seqId, compId)
        if refChainId != chainId:
            continue
        if seqId in ps['auth_seq_id']:
            idx = ps['auth_seq_id'].index(seqId)
            cifCompId = ps['comp_id'][idx]
            origCompId = ps['auth_comp_id'][idx]
            if cifCompId != compId:
                compIds = [_compId for _seqId, _compId in zip(ps['auth_seq_id'], ps['comp_id']) if _seqId == seqId]
                if compId in compIds:
                    cifCompId = compId
                    origCompId = next(origCompId for _seqId, _compId, origCompId in zip(ps['auth_seq_id'], ps['comp_id'], ps['auth_comp_id'])
                                      if _seqId == seqId and _compId == compId)
            if compId in (cifCompId, origCompId):
                if len(nefT.get_valid_star_atom(cifCompId, atomId)[0]) > 0:
                    chainAssign.add((chainId, seqId, cifCompId, True))
            elif len(nefT.get_valid_star_atom(cifCompId, atomId)[0]) > 0:
                chainAssign.add((chainId, seqId, cifCompId, True))

        elif 'gap_in_auth_seq' in ps and ps['gap_in_auth_seq']:
            authSeqIdList = list(filter(None, ps['auth_seq_id']))
            if len(authSeqIdList) > 0:
                minAuthSeqId = min(authSeqIdList)
                maxAuthSeqId = max(authSeqIdList)
                if minAuthSeqId <= seqId <= maxAuthSeqId:
                    _seqId_ = seqId + 1
                    while _seqId_ <= maxAuthSeqId:
                        if _seqId_ in ps['auth_seq_id']:
                            break
                        _seqId_ += 1
                    if _seqId_ not in ps['auth_seq_id']:
                        _seqId_ = seqId - 1
                        while _seqId_ >= minAuthSeqId:
                            if _seqId_ in ps['auth_seq_id']:
                                break
                            _seqId_ -= 1
                    if _seqId_ in ps['auth_seq_id']:
                        idx = ps['auth_seq_id'].index(_seqId_) - (_seqId_ - seqId)
                        try:
                            seqId_ = ps['auth_seq_id'][idx]
                            cifCompId = ps['comp_id'][idx]
                            origCompId = ps['auth_comp_id'][idx]
                            if cifCompId != compId:
                                compIds = [_compId for _seqId, _compId in zip(ps['auth_seq_id'], ps['comp_id']) if _seqId == seqId]
                                if compId in compIds:
                                    cifCompId = compId
                                    origCompId = next(origCompId for _seqId, _compId, origCompId in zip(ps['auth_seq_id'], ps['comp_id'], ps['auth_comp_id'])
                                                      if _seqId == seqId and _compId == compId)
                            if compId in (cifCompId, origCompId):
                                if len(nefT.get_valid_star_atom(cifCompId, atomId)[0]) > 0:
                                    chainAssign.add((chainId, seqId_, cifCompId, True))
                                elif len(nefT.get_valid_star_atom(cifCompId, atomId)[0]) > 0:
                                    chainAssign.add((chainId, seqId_, cifCompId, True))
                        except IndexError:
                            pass

    if hasNonPoly or hasBranched:

        if hasNonPoly and hasBranched:
            nonPolySeq = nonPoly
            nonPolySeq.extend(branched)
        elif hasNonPoly:
            nonPolySeq = nonPoly
        else:
            nonPolySeq = branched

        ligands = 0
        if hasNonPoly:
            for np in nonPoly:
                ligands += np['comp_id'].count(compId)
            if ligands == 0:
                for np in nonPoly:
                    if 'alt_comp_id' in np:
                        ligands += np['alt_comp_id'].count(compId)

        for np in nonPolySeq:
            chainId, seqId = getRealChainSeqId(nefT.get_ccu(), np, _seqId, compId)
            if refChainId != chainId:
                continue
            if seqId in np['auth_seq_id']\
               or (ligands == 1 and (compId in np['comp_id'] or ('alt_comp_id' in np and compId in np['alt_comp_id']))):
                idx = np['auth_seq_id'].index(seqId) if seqId in np['auth_seq_id']\
                    else np['seq_id'].index(seqId) if seqId in np['seq_id'] else 0
                cifCompId = np['comp_id'][idx]
                origCompId = np['auth_comp_id'][idx]
                if 'alt_auth_seq_id' in np and seqId not in np['auth_seq_id'] and seqId in np['alt_auth_seq_id']:
                    seqId = next(_seqId_ for _seqId_, _altSeqId_ in zip(np['auth_seq_id'], np['alt_auth_seq_id']) if _altSeqId_ == seqId)
                if compId in (cifCompId, origCompId):
                    if len(nefT.get_valid_star_atom(cifCompId, atomId)[0]) > 0:
                        chainAssign.add((chainId, seqId, cifCompId, False))
                else:
                    _atomId, _, details = nefT.get_valid_star_atom(cifCompId, atomId)
                    if len(_atomId) > 0 and (details is None or compId not in monDict3):
                        chainAssign.add((chainId, seqId, cifCompId, False))

    if len(chainAssign) == 0:
        for ps in polySeq:
            chainId = ps['chain_id']
            if refChainId != chainId:
                continue
            seqKey = (chainId, _seqId)
            if seqKey in authToLabelSeq:
                _, seqId = authToLabelSeq[seqKey]
                if seqId in ps['seq_id']:
                    idx = ps['seq_id'].index(seqId)
                    cifCompId = ps['comp_id'][idx]
                    origCompId = ps['auth_comp_id'][idx]
                    if cifCompId != compId:
                        compIds = [_compId for _seqId, _compId in zip(ps['auth_seq_id'], ps['comp_id']) if _seqId == seqId]
                        if compId in compIds:
                            cifCompId = compId
                            origCompId = next(origCompId for _seqId, _compId, origCompId in zip(ps['auth_seq_id'], ps['comp_id'], ps['auth_comp_id'])
                                              if _seqId == seqId and _compId == compId)
                    if compId in (cifCompId, origCompId):
                        if len(nefT.get_valid_star_atom(cifCompId, atomId)[0]) > 0:
                            chainAssign.add((ps['auth_chain_id'], _seqId, cifCompId, True))
                    elif len(nefT.get_valid_star_atom(cifCompId, atomId)[0]) > 0:
                        chainAssign.add((ps['auth_chain_id'], _seqId, cifCompId, True))

        if nonPolySeq is not None:
            for np in nonPolySeq:
                chainId = np['auth_chain_id']
                if refChainId != chainId:
                    continue
                seqKey = (chainId, _seqId)
                if seqKey in authToLabelSeq:
                    _, seqId = authToLabelSeq[seqKey]
                    if seqId in np['seq_id']:
                        idx = np['seq_id'].index(seqId)
                        cifCompId = np['comp_id'][idx]
                        origCompId = np['auth_comp_id'][idx]
                        if compId in (cifCompId, origCompId):
                            if len(nefT.get_valid_star_atom(cifCompId, atomId)[0]) > 0:
                                chainAssign.add((np['auth_chain_id'], _seqId, cifCompId, False))
                        else:
                            _atomId, _, details = nefT.get_valid_star_atom(cifCompId, atomId)
                            if len(_atomId) > 0 and (details is None or compId not in monDict3):
                                chainAssign.add((np['auth_chain_id'], _seqId, cifCompId, False))

    if len(chainAssign) == 0 and altPolySeq is not None:
        for ps in altPolySeq:
            chainId = ps['auth_chain_id']
            if refChainId != chainId:
                continue
            if _seqId in ps['auth_seq_id']:
                cifCompId = ps['comp_id'][ps['auth_seq_id'].index(_seqId)]
                if cifCompId != compId:
                    compIds = [_compId for _seqId, _compId in zip(ps['auth_seq_id'], ps['comp_id']) if _seqId == seqId]
                    if compId in compIds:
                        cifCompId = compId
                chainAssign.add((chainId, _seqId, cifCompId, True))

    if len(chainAssign) == 0:
        if seqId == 1 or (refChainId, seqId - 1) in caC['coord_unobs_res']:
            if atomId in aminoProtonCode and atomId != 'H1':
                return assignCoordPolymerSequenceWithChainId(caC, nefT, refChainId, seqId, compId, 'H1')

        if seqId < 1 and len(polySeq) == 1:
            warningMessage = f"[Atom not found] "\
                f"{_seqId}:{compId}:{atomId} is not present in the coordinates. "\
                f"The residue number '{_seqId}' is not present in polymer sequence of chain {refChainId} of the coordinates. "\
                "Please update the sequence in the Macromolecules page."
        else:
            warningMessage = f"[Atom not found] "\
                f"{_seqId}:{compId}:{atomId} is not present in the coordinates."

    return list(chainAssign), warningMessage


def selectCoordAtoms(cR, caC: dict, nefT, chainAssign: List[Tuple[str, int, str, bool]],
                     authChainId: str, seqId: int, compId: str, atomId: str, authAtomId: str,
                     allowAmbig: bool = True, enableWarning: bool = True, preferAuthAtomName: bool = False,
                     representativeModelId: int = REPRESENTATIVE_MODEL_ID, representativeAltId: str = REPRESENTATIVE_ALT_ID,
                     modelNumName: str = 'PDB_model_num', offset: int = 1) -> Tuple[List[dict], str]:
    """ Select atoms of the coordinates.
        @return atom selection, warning mesage (None for valid case)
    """

    atomSelection = []
    warningMessage = None

    origAtomId = atomId

    for chainId, cifSeqId, cifCompId, isPolySeq in chainAssign:
        seqKey, coordAtomSite = getCoordAtomSiteOf(caC, authChainId, chainId, cifSeqId, cifCompId)

        if preferAuthAtomName and coordAtomSite is not None:
            if compId in caC['auth_atom_name_to_id'] and cifCompId == coordAtomSite['comp_id']:
                if authAtomId in caC['auth_atom_name_to_id'][compId]:
                    _atomId = caC['auth_atom_name_to_id'][compId][authAtomId]
                    if _atomId in coordAtomSite['atom_id']:
                        atomId = _atomId
                elif 'split_comp_id' not in coordAtomSite and origAtomId in caC['auth_atom_name_to_id'][compId]:
                    _atomId = caC['auth_atom_name_to_id'][compId][origAtomId]
                    if _atomId in coordAtomSite['atom_id']:
                        atomId = _atomId
            if 'alt_atom_id' in coordAtomSite and authAtomId in coordAtomSite['alt_atom_id']:
                if coordAtomSite['comp_id'] != cifCompId:
                    continue
                atomId = coordAtomSite['atom_id'][coordAtomSite['alt_atom_id'].index(authAtomId)]
            # DAOTHER-8751, 8817 (D_1300043061)
            elif 'alt_comp_id' in coordAtomSite and 'alt_atom_id' in coordAtomSite\
                 and authAtomId in coordAtomSite['alt_atom_id']:
                _compId = coordAtomSite['alt_comp_id'][coordAtomSite['alt_atom_id'].index(authAtomId)]
                if _compId != cifCompId:
                    continue
                if _compId in caC['auth_atom_name_to_id_ext'] and authAtomId in caC['auth_atom_name_to_id_ext'][_compId]\
                   and len(set(coordAtomSite['alt_comp_id'])) > 1:
                    atomId = caC['auth_atom_name_to_id_ext'][_compId][authAtomId]
                else:
                    atomId = coordAtomSite['atom_id'][coordAtomSite['alt_atom_id'].index(authAtomId)]
            elif 'split_comp_id' in coordAtomSite:
                found = False
                for _compId in coordAtomSite['split_comp_id']:
                    _seqKey, _coordAtomSite = getCoordAtomSiteOf(caC, authChainId, chainId, cifSeqId, _compId)
                    if _coordAtomSite is None:
                        continue
                    if 'alt_comp_id' in _coordAtomSite and 'alt_atom_id' in _coordAtomSite\
                       and authAtomId in _coordAtomSite['alt_atom_id']:
                        _compId = _coordAtomSite['alt_comp_id'][_coordAtomSite['alt_atom_id'].index(authAtomId)]
                        if _compId == cifCompId:
                            if authAtomId in _coordAtomSite['alt_atom_id']:
                                atomId = _coordAtomSite['atom_id'][_coordAtomSite['alt_atom_id'].index(authAtomId)]
                            compId = _compId
                            coordAtomSite = _coordAtomSite
                            found = True
                            break
                    if authAtomId in _coordAtomSite['alt_atom_id']:
                        compId = _compId
                        coordAtomSite = _coordAtomSite
                        found = True
                        break
                if not found or (found and compId != cifCompId):
                    continue

        if (coordAtomSite is not None and atomId in coordAtomSite['atom_id']) or preferAuthAtomName:
            _atomId = [atomId]
        else:
            _atomId = []
            if not isPolySeq and atomId[0] in ('Q', 'M') and coordAtomSite is not None:
                pattern = re.compile(fr'H{atomId[1:]}\d+') if compId in monDict3 else re.compile(fr'H{atomId[1:]}\S?$')
                atomIdList = [a for a in coordAtomSite['atom_id'] if re.search(pattern, a) and a[-1] in ('1', '2', '3')]
                if len(atomIdList) > 1:
                    hvyAtomIdList = [a for a in coordAtomSite['atom_id'] if a[0] in ('C', 'N')]
                    hvyAtomId = None
                    for canHvyAtomId in hvyAtomIdList:
                        if isStructConn(cR, authChainId, cifSeqId, canHvyAtomId, authChainId, cifSeqId, atomIdList[0],
                                        representativeModelId=representativeModelId, representativeAltId=representativeAltId,
                                        modelNumName=modelNumName):
                            hvyAtomId = canHvyAtomId
                            break
                    if hvyAtomId is not None:
                        for _atomId_ in atomIdList:
                            if isStructConn(cR, authChainId, cifSeqId, hvyAtomId, authChainId, cifSeqId, _atomId_,
                                            representativeModelId=representativeModelId, representativeAltId=representativeAltId,
                                            modelNumName=modelNumName):
                                _atomId.append(_atomId_)
            if len(_atomId) > 1:
                details = None
            else:
                _atomId, _, details = nefT.get_valid_star_atom_in_xplor(cifCompId, atomId, leave_unmatched=True)
                if details is not None and len(atomId) > 1 and not atomId[-1].isalpha():
                    _atomId, _, details = nefT.get_valid_star_atom_in_xplor(cifCompId, atomId[:-1], leave_unmatched=True)
                    if atomId[-1].isdigit() and int(atomId[-1]) <= len(_atomId):
                        _atomId = [_atomId[int(atomId[-1]) - 1]]

            if details is not None or atomId.endswith('"'):
                ccU = nefT.get_ccu()
                _atomId_ = translateToStdAtomName(atomId, cifCompId, ccU=ccU)
                if _atomId_ != atomId:
                    if atomId.startswith('HT') and len(_atomId_) == 2:
                        _atomId_ = 'H'
                    __atomId = nefT.get_valid_star_atom_in_xplor(cifCompId, _atomId_)[0]
                    if coordAtomSite is not None:
                        if any(_atomId_ for _atomId_ in __atomId if _atomId_ in coordAtomSite['atom_id']):
                            _atomId = __atomId
                        elif __atomId[0][0] in protonBeginCode:
                            __bondedTo = ccU.getBondedAtoms(cifCompId, __atomId[0])
                            if len(__bondedTo) > 0 and __bondedTo[0] in coordAtomSite['atom_id']:
                                _atomId = __atomId
                elif coordAtomSite is not None:
                    _atomId = []

        if coordAtomSite is not None\
           and not any(_atomId_ for _atomId_ in _atomId if _atomId_ in coordAtomSite['atom_id'])\
           and atomId in coordAtomSite['atom_id']:
            _atomId = [atomId]

        if coordAtomSite is None and not isPolySeq:
            nonPoly = caC['non_polymer']
            branched = caC['branched']

            hasNonPoly = nonPoly is not None and len(nonPoly) > 0
            hasBranched = branched is not None and len(branched) > 0

            if hasNonPoly or hasBranched:
                if hasNonPoly and hasBranched:
                    nonPolySeq = nonPoly
                    nonPolySeq.extend(branched)
                elif hasNonPoly:
                    nonPolySeq = nonPoly
                else:
                    nonPolySeq = branched

                try:
                    for np in nonPolySeq:
                        if np['auth_chain_id'] == chainId and cifSeqId in np['auth_seq_id']:
                            cifSeqId = np['seq_id'][np['auth_seq_id'].index(cifSeqId)]
                            seqKey, coordAtomSite = getCoordAtomSiteOf(caC, authChainId, chainId, cifSeqId, cifCompId)
                            if coordAtomSite is not None:
                                break
                except ValueError:
                    pass

        lenAtomId = len(_atomId)
        if compId != cifCompId and compId in monDict3 and cifCompId in monDict3:
            multiChain = insCode = False
            if len(chainAssign) > 0:
                chainIds = [ca[0] for ca in chainAssign]
                multiChain = len(collections.Counter(chainIds).most_common()) > 1
            ps = next((ps for ps in caC['polymer_sequence'] if ps['auth_chain_id'] == chainId), None)
            if ps is not None:
                compIds = [_compId for _seqId, _compId in zip(ps['auth_seq_id'], ps['comp_id']) if _seqId == cifSeqId]
                if compId in compIds:
                    insCode = True
                    cifCompId = compId
            if not multiChain and not insCode:
                if enableWarning:
                    warningMessage = f"[Sequence mismatch] "\
                        f"Residue name {compId!r} of the restraint does not match with {chainId}:{cifSeqId}:{cifCompId} of the coordinates."
                continue

        if lenAtomId == 0:
            if seqId == 1 and isPolySeq and cifCompId == 'ACE' and cifCompId != compId and offset == 0:
                return selectCoordAtoms(cR, caC, nefT, chainAssign, authChainId, seqId, compId, atomId,
                                        allowAmbig, enableWarning, preferAuthAtomName,
                                        representativeModelId=representativeModelId, representativeAltId=representativeAltId,
                                        modelNumName=modelNumName, offset=1)
            if enableWarning:
                warningMessage = f"[Invalid atom nomenclature] "\
                    f"{seqId}:{compId}:{atomId} is invalid atom nomenclature."
            continue
        if lenAtomId > 1 and not allowAmbig:
            if enableWarning:
                warningMessage = f"[Invalid atom selection] "\
                    f"Ambiguous atom selection '{seqId}:{compId}:{atomId}' is not allowed as a angle restraint."
            continue

        for cifAtomId in _atomId:
            _atomSelection = {'chain_id': chainId, 'seq_id': cifSeqId, 'comp_id': cifCompId,
                              'atom_id': cifAtomId, 'auth_atom_id': authAtomId}
            if _atomSelection not in atomSelection:
                atomSelection.append(_atomSelection)

            warningMessage = testCoordAtomIdConsistency(caC, nefT.get_ccu(), authChainId, chainId, cifSeqId, cifCompId, cifAtomId, seqKey, coordAtomSite, enableWarning)
            if warningMessage is not None and warningMessage.startswith('Ignorable'):
                warningMessage = None
                atomSelection.pop()

    return atomSelection, warningMessage


def getRealChainSeqId(ccU, ps: dict, seqId: int, compId: Optional[str] = None) -> Tuple[str, int]:
    """ Return effective sequence key according to polymer sequence of the coordinates.
        @return: sequence key
    """

    if compId is not None:
        compId = translateToStdResName(compId, ccU=ccU)
    if seqId in ps['auth_seq_id']:
        if compId is None:
            return ps['auth_chain_id'], seqId
        idx = ps['auth_seq_id'].index(seqId)
        if compId in (ps['comp_id'][idx], ps['auth_comp_id'][idx]):
            return ps['auth_chain_id'], seqId
    return ps['auth_chain_id'], seqId


def getCoordAtomSiteOf(caC: dict, authChainId: str, chainId: str, seqId: int,
                       compId: Optional[str] = None, asis: bool = True) -> Tuple[Tuple[str, int], dict]:
    """ Return sequence key and its attributes in coordAssemblyChecker (caC).
        @return: sequence key, attributes in the coordAssemblyChecker's 'coord_atom_site' for a given residue
    """

    seqKey = (chainId, seqId)
    _seqKey = (seqKey[0], seqKey[1], compId)

    coordAtomSites = caC['coord_atom_site']
    coordAtomSite = None

    if asis:
        if compId is not None and _seqKey in coordAtomSites:
            coordAtomSite = coordAtomSites[_seqKey]
        elif seqKey in coordAtomSites:
            coordAtomSite = coordAtomSites[seqKey]
        elif authChainId != chainId and (authChainId, seqId) in coordAtomSites:
            seqKey = (authChainId, seqId)
            _seqKey = (seqKey[0], seqKey[1], compId)
            if compId is not None and _seqKey in coordAtomSites:
                coordAtomSite = coordAtomSites[_seqKey]
            coordAtomSite = coordAtomSites[seqKey]
        else:
            labelToAuthSeq = caC['label_to_auth_seq']
            if seqKey in labelToAuthSeq:
                seqKey = labelToAuthSeq[seqKey]
                _seqKey = (seqKey[0], seqKey[1], compId)
                if compId is not None and _seqKey in coordAtomSites:
                    coordAtomSite = coordAtomSites[_seqKey]
                elif seqKey in coordAtomSites:
                    coordAtomSite = coordAtomSites[seqKey]
            else:
                ps = next((ps for ps in caC['polymer_sequence'] if ps['auth_chain_id'] == chainId), None)
                if ps is not None and seqId in ps['auth_seq_id']:
                    seqKey = (chainId, ps['seq_id'][ps['auth_seq_id'].index(seqId)])
                    _seqKey = (seqKey[0], seqKey[1], compId)
                    if compId is not None and _seqKey in coordAtomSites:
                        coordAtomSite = coordAtomSites[_seqKey]
                    elif seqKey in coordAtomSites:
                        coordAtomSite = coordAtomSites[seqKey]
                    else:  # DAOTHER-10105: handle inconsistency between auth_asym_id and pdbx_auth_asym_id due to chain split while annotation
                        for _chainId in caC['label_to_auth_chain']:
                            if _chainId == chainId:
                                continue
                            _ps = next((_ps for _ps in caC['polymer_sequence'] if _ps['auth_chain_id'] == _chainId), None)
                            if _ps is not None and seqId not in _ps['auth_seq_id']:
                                seqKey = (_chainId, seqId)
                                _seqKey = (seqKey[0], seqKey[1], compId)
                                if compId is not None and _seqKey in coordAtomSites:
                                    coordAtomSite = coordAtomSites[_seqKey]
                                    break
                                if seqKey in coordAtomSites:
                                    coordAtomSite = coordAtomSites[seqKey]
                                    break

    return seqKey, coordAtomSite


def testCoordAtomIdConsistency(caC: dict, ccU, authChainId: str, chainId: str, seqId: int, compId: str, atomId: str,
                               seqKey: Tuple[str, int], coordAtomSite: Optional[dict], enableWarning: bool = True) -> Optional[str]:
    """ Check existence of specified atom in the coordinates.
        @return: waring message (None for valid case)
    """

    found = False

    if coordAtomSite is not None:
        if atomId in coordAtomSite['atom_id']:
            found = True
        elif 'alt_atom_id' in coordAtomSite and atomId in coordAtomSite['alt_atom_id']:
            found = True
        else:
            _seqKey, _coordAtomSite = getCoordAtomSiteOf(caC, authChainId, chainId, seqId, compId, asis=False)
            if _coordAtomSite is not None and _coordAtomSite['comp_id'] == compId:
                if atomId in _coordAtomSite['atom_id']:
                    found = True
                    seqKey = _seqKey
                elif 'alt_atom_id' in _coordAtomSite and atomId in _coordAtomSite['alt_atom_id']:
                    found = True
                    seqKey = _seqKey

    else:
        _seqKey, _coordAtomSite = getCoordAtomSiteOf(caC, authChainId, chainId, seqId, compId, asis=False)
        if _coordAtomSite is not None and _coordAtomSite['comp_id'] == compId:
            if atomId in _coordAtomSite['atom_id']:
                found = True
                seqKey = _seqKey
            elif 'alt_atom_id' in _coordAtomSite and atomId in _coordAtomSite['alt_atom_id']:
                found = True
                seqKey = _seqKey

    if found:
        return None

    _seqKey, _coordAtomSite = getCoordAtomSiteOf(caC, authChainId, chainId, seqId, compId, asis=False)
    if _coordAtomSite is not None and _coordAtomSite['comp_id'] == compId:
        if atomId in _coordAtomSite['atom_id']:
            found = True
            seqKey = _seqKey
        elif 'alt_atom_id' in _coordAtomSite and atomId in _coordAtomSite['alt_atom_id']:
            found = True
            seqKey = _seqKey

    if found:
        return None

    if ccU.updateChemCompDict(compId):
        cca = next((cca for cca in ccU.lastAtomList if cca[ccU.ccaAtomId] == atomId), None)
        if cca is not None and seqKey not in caC['coord_unobs_res'] and ccU.lastChemCompDict['_chem_comp.pdbx_release_status'] == 'REL':
            checked = False
            ps = next((ps for ps in caC['polymer_sequence'] if ps['auth_chain_id'] == chainId), None)
            authSeqIdList = list(filter(None, ps['auth_seq_id'])) if ps is not None else None
            if seqId == 1 or (chainId, seqId - 1) in caC['coord_unobs_res'] or (ps is not None and min(authSeqIdList) == seqId):
                if aminoProtonCode and atomId != 'H1':
                    testCoordAtomIdConsistency(caC, ccU, authChainId, chainId, seqId, compId, 'H1', seqKey, coordAtomSite)
                    return None
                if atomId in aminoProtonCode or atomId == 'P' or atomId.startswith('HOP'):
                    checked = True
            if not checked:
                if atomId[0] in protonBeginCode:
                    bondedTo = ccU.getBondedAtoms(compId, atomId)
                    if len(bondedTo) > 0:
                        if coordAtomSite is not None and bondedTo[0] in coordAtomSite['atom_id'] and cca[ccU.ccaLeavingAtomFlag] != 'Y':
                            return f"[Hydrogen not instantiated] "\
                                f"{chainId}:{seqId}:{compId}:{atomId} is not properly instantiated in the coordinates. "\
                                "Please re-upload the model file."
                        if bondedTo[0][0] == 'O':
                            return 'Ignorable hydroxyl group'
                if enableWarning:
                    if chainId in LARGE_ASYM_ID:
                        if seqKey in caC['coord_unobs_atom']\
                                and (atomId in caC['coord_unobs_atom'][seqKey]['atom_ids']
                                     or (atomId[0] in protonBeginCode and any(bondedTo for bondedTo in ccU.getBondedAtoms(compId, atomId, exclProton=True)
                                                                              if bondedTo in caC['coord_unobs_atom'][seqKey]['atom_ids']))):
                            return 'Ignorable missing atom'
                        return f"[Atom not found] "\
                            f"{chainId}:{seqId}:{compId}:{atomId} is not present in the coordinates."

    return None


def getDistConstraintType(atomSelectionSet: List[List[dict]], dstFunc: dict, csStat, hint: str = '.') -> Optional[str]:
    """ Return distance constraint type for _Constraint_file.Constraint_type tag value.
        @return 'hydrogen bond', 'disulfide bond', etc., None for unclassified distance constraint
    """

    if len(atomSelectionSet) != 2:
        return None

    atom1 = atomSelectionSet[0][0]
    atom2 = atomSelectionSet[1][0]

    if None in (atom1, atom2):
        return None

    atom_id_1 = atom1['atom_id'] if 'atom_id' in atom1 else atom1['auth_atom_id']
    atom_id_2 = atom2['atom_id'] if 'atom_id' in atom2 else atom2['auth_atom_id']

    if None in (atom_id_1, atom_id_2):
        return None

    if ('comp_id' in atom1 and atom1['comp_id'] == atom_id_1)\
       or ('comp_id' in atom2 and atom2['comp_id'] == atom_id_2):
        return 'metal coordination'

    upperLimit = 0.0
    if 'upper_limit' in dstFunc and dstFunc['upper_limit'] is not None:
        upperLimit = float(dstFunc['upper_limit'])
    lowerLimit = -1.0
    if 'lower_limit' in dstFunc and dstFunc['lower_limit'] is not None:
        lowerLimit = float(dstFunc['lower_limit'])

    atom_id_1_ = atom_id_1[0]
    atom_id_2_ = atom_id_2[0]

    def is_like_hbond():
        if (atom_id_1_ == 'F' and atom_id_2_ in protonBeginCode) or (atom_id_2_ == 'F' and atom_id_1_ in protonBeginCode):
            return True

        if (atom_id_1_ == 'F' and atom_id_2_ == 'F') or (atom_id_2_ == 'F' and atom_id_1_ == 'F'):
            return True

        if (atom_id_1_ == 'O' and atom_id_2_ in protonBeginCode) or (atom_id_2_ == 'O' and atom_id_1_ in protonBeginCode):
            return True

        if (atom_id_1_ == 'O' and atom_id_2_ == 'N') or (atom_id_2_ == 'O' and atom_id_1_ == 'N'):
            return True

        if (atom_id_1_ == 'O' and atom_id_2_ == 'O') or (atom_id_2_ == 'O' and atom_id_1_ == 'O'):
            return True

        if (atom_id_1_ == 'N' and atom_id_2_ in protonBeginCode) or (atom_id_2_ == 'N' and atom_id_1_ in protonBeginCode):
            return True

        if (atom_id_1_ == 'N' and atom_id_2_ == 'N') or (atom_id_2_ == 'N' and atom_id_1_ == 'N'):
            return True

        return False

    if atom1['chain_id'] == atom2['chain_id'] and atom1['seq_id'] == atom2['seq_id']:
        if upperLimit == 0.0 and 0.0 < lowerLimit <= 1.8\
           and atom_id_1_ not in protonBeginCode and atom_id_2_ not in protonBeginCode:
            return 'covalent bond'
        if upperLimit >= DIST_AMBIG_UP or lowerLimit >= DIST_AMBIG_UP:
            if is_like_hbond():
                return 'ambiguous hydrogen bond'
            return 'general distance'
        return None

    _hint = hint.lower()

    def is_like_sebond():
        return (atom_id_1 == 'SE' and atom_id_2 == 'SE') or 'diselenide' in _hint

    def is_like_ssbond():
        return (atom_id_1 == 'SG' and atom_id_2 == 'SG') or ('disulfide' in _hint or ('ss' in _hint and 'bond' in _hint))

    def is_like_sebond_support():
        return ((atom_id_1 == 'SE' and atom_id_2 == 'CB') or (atom_id_2 == 'SE' and atom_id_1 == 'CB'))\
            and 'comp_id' in atom1 and 'comp_id' in atom2 and atom1['comp_id'] == atom2['comp_id']

    def is_like_ssbond_support():
        return ((atom_id_1 == 'SG' and atom_id_2 == 'CB') or (atom_id_2 == 'SG' and atom_id_1 == 'CB'))\
            and 'comp_id' in atom1 and 'comp_id' in atom2 and atom1['comp_id'] == atom2['comp_id']

    ambig = len(atomSelectionSet[0]) * len(atomSelectionSet[1]) > 1\
        and (isAmbigAtomSelection(atomSelectionSet[0], csStat)
             or isAmbigAtomSelection(atomSelectionSet[1], csStat))

    if atom1['chain_id'] != atom2['chain_id'] or ambig:
        if (upperLimit >= DIST_AMBIG_UP or ambig) and ('pre' in _hint or 'paramag' in _hint):
            return 'paramagnetic relaxation'
        if (upperLimit >= DIST_AMBIG_UP or ambig) and ('cidnp' in _hint):
            return 'photo cidnp'
        if (upperLimit <= DIST_AMBIG_LOW or upperLimit >= DIST_AMBIG_MED or ambig) and ('csp' in _hint or 'perturb' in _hint):
            return 'chemical shift perturbation'
        if (upperLimit <= DIST_AMBIG_LOW or upperLimit >= DIST_AMBIG_MED or ambig) and 'mutat' in _hint:
            return 'mutation'
        if (upperLimit <= DIST_AMBIG_LOW or upperLimit >= DIST_AMBIG_MED or ambig) and 'protect' in _hint:
            return 'hydrogen exchange protection'
        if atom1['chain_id'] != atom2['chain_id'] and 'symm' in _hint:
            return 'symmetry'

    if 'build' in _hint and 'up' in _hint:
        if 'roe' in _hint:
            return 'ROE build-up'
        return 'NOE build-up'

    if 'not' in _hint and 'seen' in _hint:
        if (upperLimit <= DIST_AMBIG_LOW or upperLimit >= DIST_AMBIG_MED):
            return 'NOE not seen'

    if upperLimit >= DIST_AMBIG_UP or lowerLimit >= DIST_AMBIG_UP:

        if upperLimit > DIST_AMBIG_BND or (atom1['chain_id'] == atom2['chain_id'] and atom1['seq_id'] == atom2['seq_id']):

            if is_like_sebond():
                return 'ambiguous diselenide bond'

            if is_like_ssbond():
                return 'ambiguous disulfide bond'

            if is_like_hbond():
                return 'ambiguous hydrogen bond'

        return 'general distance'

    if upperLimit <= DIST_AMBIG_LOW or upperLimit > DIST_AMBIG_BND or ambig:

        if upperLimit > DIST_AMBIG_BND or (atom1['chain_id'] == atom2['chain_id'] and atom1['seq_id'] == atom2['seq_id']):

            if is_like_sebond():
                return 'ambiguous diselenide bond'

            if is_like_ssbond():
                return 'ambiguous disufide bond'

            if is_like_hbond():
                return 'ambiguous hydrogen bond'

        if upperLimit >= DIST_AMBIG_MED and lowerLimit <= 0.0:
            return 'general distance'

        if upperLimit <= DIST_AMBIG_LOW and lowerLimit > 0.0:

            if is_like_sebond():
                return 'diselenide bond (lower bound)'

            if is_like_ssbond():
                return 'disufide bond (lower bound)'

            if is_like_hbond():
                return 'hydrogen bond (lower bound)'

            if upperLimit > 0:
                return 'general distance'

            return 'NOE (lower bound)' if 'roe' not in _hint else 'ROE (lower bound)'

        return None if 'roe' not in _hint else 'ROE'

    if is_like_sebond_support():
        return 'reinforced diselenide bond'

    if is_like_ssbond_support():
        return 'reinforced disulfide bond'

    if is_like_sebond():
        return 'diselenide bond' if upperLimit > DIST_AMBIG_LOW or lowerLimit <= 0.0 else 'deselenide bond (lower bond)'

    if is_like_ssbond():
        return 'disulfide bond' if upperLimit > DIST_AMBIG_LOW or lowerLimit <= 0.0 else 'disulfide bond (lower bond)'

    if is_like_hbond():
        return 'hydrogen bond' if upperLimit > DIST_AMBIG_LOW or lowerLimit <= 0.0 else 'hydrogen bond (lower bond)'

    return None if 'roe' not in _hint else 'ROE'


def getPotentialType(fileType: str, mrSubtype: str, dstFunc: dict) -> Optional[str]:
    """ Return NMR-STAR potential type for a given function.
        @return potential type, None for unmatched case
    """

    if 'lower_linear_limit' in dstFunc and 'upper_linear_limit' in dstFunc:
        return 'square-well-parabolic-linear'

    if 'lower_linear_limit' in dstFunc:
        return 'lower-bound-parabolic-linear'

    if 'upper_linear_limit' in dstFunc:
        return 'upper-bound-parabolic-linear'

    if 'lower_limit' in dstFunc and 'upper_limit' in dstFunc:
        return 'square-well-parabolic'

    if 'lower_limit' in dstFunc:
        return 'lower-bound-parabolic'

    if 'upper_limit' in dstFunc:
        return 'upper-bound-parabolic'

    if 'target_value' in dstFunc and fileType in ('nm-res-xpl', 'nm-res-cns', 'nmr-star') and mrSubtype == 'dist':
        return 'log-harmonic'

    if 'target_value' in dstFunc and mrSubtype in ('dist', 'dihed', 'rdc'):
        return 'parabolic'

    return None


def getPdbxNmrSoftwareName(name: str) -> str:
    """ Return _pdbx_nmr_software.name enumarated value for a given software name.
    """

    if name == 'AMBER':
        return 'Amber'
    if name == 'BIOSYM':
        return 'Discover'
    if name in 'ISD':
        return 'Inferential Structure Determination (ISD)'
    if name == 'ROSETTA':
        return 'Rosetta'
    if name == 'XPLOR-NIH':
        return 'X-PLOR NIH'
    if name == 'XPLOR-NIH/CNS':
        return 'X-PLOR NIH/CNS'
    if name == 'NMRPIPE':
        return 'NMRPipe'
    if name == 'NMRVIEW':
        return 'NMRView'
    if name == 'SPARKY':
        return 'Sparky'
    if name == 'TOPSPIN':
        return 'TopSpin'
    if name == 'XWINNMR':
        return 'XwinNMR'
    if name == 'CCPN':
        return 'CcpNmr Analysis'
    if name == 'SCHRODINGER/ASL':
        return 'MacroModel'
    if name == 'OLIVIA':
        return 'Olivia'
    return name  # 'ARIA', 'CHARMM', 'CNS', 'CYANA', 'DYNAMO', 'PALES', 'TALOS', 'GROMACS', 'SYBYL', 'VNMR', 'XEASY'
