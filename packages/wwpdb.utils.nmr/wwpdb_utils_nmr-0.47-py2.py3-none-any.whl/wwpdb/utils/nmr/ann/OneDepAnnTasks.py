##
# File: OneDepAnnTasks.py
# Date: 19-Dec-2024
#
# Updates:
##
""" Wrapper class for OneDep annotation tasks - merge NMRIF metadata.
    @author: Masashi Yokochi
"""
__docformat__ = "restructuredtext en"
__author__ = "Masashi Yokochi"
__email__ = "yokochi@protein.osaka-u.ac.jp"
__license__ = "Apache License 2.0"
__version__ = "1.0.0"

import sys
# import csv
import pynmrstar
import re
import collections

from typing import IO, List

from wwpdb.utils.align.alignlib import PairwiseAlign  # pylint: disable=no-name-in-module

try:
    from wwpdb.utils.nmr.AlignUtil import (emptyValue,
                                           getScoreOfSeqAlign)
    from wwpdb.utils.nmr.io.mmCIFUtil import mmCIFUtil
    from wwpdb.utils.nmr.CifToNmrStar import (get_first_sf_tag,
                                              set_sf_tag,
                                              retrieve_symbolic_labels)
except ImportError:
    from nmr.AlignUtil import (emptyValue,
                               getScoreOfSeqAlign)
    from nmr.io.mmCIFUtil import mmCIFUtil
    from nmr.CifToNmrStar import (get_first_sf_tag,
                                  set_sf_tag,
                                  retrieve_symbolic_labels)


NMR_SOFTWERE_LIST = ('3D-DART', '3DNA', '4D-CHAINS', '4DSPOT', 'ABACUS', 'ACME', 'ADAPT-NMR', 'AGNuS', 'ALMOST',
                     'Amber', 'AmberTools', 'AMIX', 'AnalysisAssign', 'ANATOLIA', 'Anglesearch', 'ANSIG',
                     'APES', 'AQUA', 'ARIA', 'ARIA2alpha', 'ARMOR', 'ArShift', 'ARTINA', 'ASCAN', 'ASDP',
                     'ATNOS', 'ATSAS', 'AUDANA', 'AURELIA', 'AUREMOL', 'AutoAssign', 'AutoDock', 'AutoProc',
                     'AutoStructure', 'AVS', 'Azara', 'BACKTOR', 'BACUS', 'BATCH', 'BATMAN', 'BIOGRAF', 'BIRDER',
                     'Burrow-owl', 'CALIBA', 'calRW', 'calRW+', 'CambridgeCS', 'CAMERA', 'CamShift',
                     'CamShift-MD', 'CANDID', 'CAPP', 'CARA', 'CATCH23', 'CATIA', 'CCNMR', 'CcpNmr Analysis',
                     'CcpNmr Analysis Assign', 'CcpNmr ChemBuild', 'CcpNmr Analysis Metabolomics',
                     'CcpNmr Analysis Screen', 'CHA3Shift', 'CHARMM', 'CHARMM-GUI', 'CHEMEX', 'CHESHIRE',
                     'CHIFIT', 'Chimera', 'CINDY', 'CING', 'Circos', 'cleaner3D', 'CLUSTAL W/X', 'Cluster 3.0',
                     'CMXW', 'CNS', 'CNSSOLVE', 'CNX', 'COMPASS', 'CoMAND', 'Complete SCS search', 'CONCOORD',
                     'CONGEN', 'CORMA', 'CPMD', 'CSCDP', 'CS-RDC-NOE Rosetta', 'CS-ROSETTA', 'CS23D', 'CSI',
                     'curvefit', 'Curves', 'Curves+', 'CYANA', 'CYRANGE', 'DADAS', 'DANGLE', 'Delta', 'DGEOM',
                     'DIAMOD', 'DIANA', 'DINOSAUR', 'DipoCoup', 'Discover', 'Discovery Studio', 'DISGEO',
                     'DISMAN', 'DISNMR', 'DNAminiCarlo', 'Dreamwalker', 'DSPACE', 'DSSP', 'DUPLEX', 'DYANA',
                     'DYNAMO', 'Dynamic Meccano', 'EC-NMR', 'ELM', 'EMBOSS', 'ENSEMBLE', 'EREF', 'EZ-ASSIGN',
                     'FANMEM', 'FANTOM', 'FAWN', 'Felix', 'FindCore', 'FINDFAM', 'FIRM', 'FISI',
                     'Flexible-meccano', 'FMCGUI', 'Foldit', 'FuDA', 'G2G', 'GAPRO', 'GARANT', 'GASyCS',
                     'Gaussian', 'GeNMR', 'GENXPK', 'Gifa', 'GLOMSA', 'GLXCC', 'GRAMM-X', 'GROMACS', 'GROMOS',
                     'GUARDD', 'HABAS', 'HADDOCK', 'HBPLUS', 'hmsIST', 'HOLE', 'HYPER', 'HyperChem', 'ICMD',
                     'In-house / custom', 'INCA', 'INDYANA', 'Inferential Structure Determination (ISD)',
                     'INFIT', 'Insight', 'Insight II', 'interhlx', 'I-PINE', 'IRMA', 'JUMNA', 'KUJIRA',
                     'MacroModel', 'MAGRO', 'MagRO-NMRView', 'MAPPER', 'MARBLE', 'MARDIGRAS', 'MARS', 'MATCH',
                     'Mathematica', 'Matlab', 'MC-Sym', 'MCASSIGN', 'MCCL', 'MDDGUI', 'MddNMR', 'MEDUSA',
                     'MestreLab (Mnova / MestReNova / MestReC)', 'MFT', 'MIDGE', 'miniCarlo', 'Minuit',
                     'MNMR', 'ModelFree', 'MODELLER', 'Module', 'Module 2', 'MOE', 'MOLMOL', 'MolProbity',
                     'MolSkop', 'Monte', 'MORASS', 'MORCAD', 'MULDER', 'MUNIN', 'NAB', 'NAMD', 'NAMFIS', 'NDEE',
                     'NESSY', 'NHFIT', 'NMR Structure Tools', 'NMR-SPIRIT', 'nmr2st', 'NMRCLUST', 'NMRDraw',
                     'NMRCompass', 'NMRe', 'NMRest', 'NMRFAM-SPARKY', 'NMRFx', 'nmrglue', 'NMRLAB', 'NMRPipe',
                     'NMRtist', 'NMRspy', 'NMRSwarm', 'NMRView', 'NMRViewJ', 'NOAH', 'NOEID', 'NOEMOL', 'NOTE',
                     'NUCFIT', 'NUCHEMICS', 'NUCLSQ', 'Numbat', 'O', 'Olivia', 'Omega', 'OPAL', 'OPALp',
                     'Orderten_SVD', 'OTOKO', 'PACES', 'PALES', 'PANAV', 'PARADYANA', 'PASA', 'PASTA',
                     'PASTE/PAPST', 'PdbStat', 'PECAN', 'PELE web server', 'PEPFLEX-II', 'pfit', 'PINE',
                     'PINE Server', 'PINE-SPARKY', 'PINT', 'PIPATH', 'PIPP', 'PISTACHIO', 'PLATON', 'PLUMED',
                     'PLUMED2', 'Poky', 'PONDEROSA', 'PONDEROSA-C/S', 'POSE', 'PREDITOR', 'PRESTO', 'Prime',
                     'PROCHECK / PROCHECK-NMR', 'PRODRG', 'ProFit', 'PROMOTIF', 'Pronto', 'Pronto3D', 'PROSA',
                     'Protein Constructor', 'PSEUDODYANA', 'PSEUDOREM', 'PSVS', 'PyMOL', 'PyRPF', 'QM/MM',
                     'qMDD', 'QUANTA', 'QUEEN', 'RADAR', 'RANDMARDI', 'RasMol', 'RASP', 'RDC-PANDA', 'rDOCK',
                     'RECOORD', 'REDCAT', 'REDcRAFT', 'REGINE', 'relax', 'RelaxFit', 'RELAZ', 'REPENT',
                     'RESTRICT', 'Rosetta', 'Rowland NMR Toolkit (RNMRTK)', 'RUNMR', 'S3EPY', 'SANE', 'SCRUB',
                     'SCULPTOR', 'SCWRL', 'SHIFTCALC', 'SHIFTX', 'Shine', 'SideR',
                     'Signal Separation Algorithm (SSA)', 'SIMPSON', 'smartnotebook', 'Smol', 'SNARF', 'SOLARIA',
                     'SOPHIE', 'Sparky', 'SPARTA', 'SPARTA+', 'SPEDREF', 'SPHINX/LINSHA', 'SpinEvolution',
                     'SPINS', 'SpinSight', 'SpinWorks', 'SPIRIT', 'SPSCAN', 'STAPP', 'Structural Fitting',
                     'SUPPOSE', 'Swiss-PdbViewer', 'SYBYL', 'SYBYL-X', 'TALOS', 'TALOS-N', 'TALOS+', 'tecmag',
                     'TENSOR', 'TENSOR2', 'Tinker', 'TopSpin', 'TRIPOS', 'TORC', 'Turbo-Frodo', 'UBNMR',
                     'UCSF Chimera', 'UCSF MidasPlus', 'UNIO', 'UXNMR', 'VADAR', 'VEMBED', 'VERIFY3D', 'VMD',
                     'VNMR', 'VnmrJ', 'WHAT IF', 'xcrvfit', 'XEASY', 'Xipp', 'Xndee', 'X-PLOR', 'X-PLOR NIH',
                     'XVNMR', 'XwinNMR', 'XSSP', 'xyza2pipe', 'YARIA', 'YARM', 'YASAP', 'YASARA')


range_value_pattern = re.compile(r'^(.+)\s*-\s*(.+)$')


def get_nmr_software(name: str) -> str:
    """ Return enumeration value for NMR software.
    """

    if name in emptyValue or name in NMR_SOFTWERE_LIST:
        return name

    _name = name.lower()

    for software in NMR_SOFTWERE_LIST:
        if software.lower() == _name:
            return software

    pA = PairwiseAlign()

    score = -100
    candidate = name

    for software in NMR_SOFTWERE_LIST:
        _software = software.lower()

        pA.setReferenceSequence([c for c in _software], 'REFNAME')  # pylint: disable=unnecessary-comprehension
        pA.addTestSequence([c for c in _name], 'NAME')  # pylint: disable=unnecessary-comprehension
        pA.doAlign()

        myAlign = pA.getAlignment('NAME')

        length = len(myAlign)

        if length == 0:
            continue

        _matched, unmapped, conflict, _, _ = getScoreOfSeqAlign(myAlign)

        _score = _matched - unmapped - conflict

        if _score > score:
            candidate = software
            score = _score

    return name if score < 0 else candidate


class OneDepAnnTasks:
    """ Wrapper class for OneDep annotation tasks.
    """

    def __init__(self, verbose: bool, log: IO,
                 sfCategoryList: List[str], entryId: str):
        self.__class_name__ = self.__class__.__name__
        self.__version__ = __version__

        self.__verbose = verbose
        self.__lfh = log

        self.__sfCategoryList = sfCategoryList
        self.__entryId = entryId

        # derived from wwpdb.apps.deposit.depui.constant.REQUIREMENTS
        self.__cifPages = ['nmrsample',
                           'nmrdatacollection',
                           'nmrsoftware',
                           'nmrchemshiftreference',
                           'nmrchemshiftconnection',
                           'nmrconstraints',
                           'nmrspectralpeaklist',
                           'nmrrefinement']

        self.__cifRequirements = {'nmrsample': ['pdbx_nmr_sample_details',
                                                'pdbx_nmr_exptl_sample',
                                                'pdbx_nmr_exptl_sample_conditions'],
                                  'nmrdatacollection': ['pdbx_nmr_spectrometer',
                                                        'pdbx_nmr_exptl',
                                                        'pdbx_nmr_sample_details',
                                                        'pdbx_nmr_exptl_sample_conditions'],
                                  'nmrsoftware': ['pdbx_nmr_software',
                                                  'pdbx_nmr_software_task'],
                                  'nmrchemshiftreference': ['pdbx_nmr_chem_shift_reference',
                                                            'pdbx_nmr_chem_shift_ref'],
                                  'nmrchemshiftconnection': ['pdbx_nmr_assigned_chem_shift_list',
                                                             'pdbx_nmr_chem_shift_experiment',
                                                             'pdbx_nmr_chem_shift_reference',
                                                             'pdbx_nmr_systematic_chem_shift_offset',
                                                             'pdbx_nmr_chem_shift_software',
                                                             'pdbx_nmr_software',
                                                             'pdbx_nmr_exptl',
                                                             'pdbx_nmr_sample_details',
                                                             'pdbx_nmr_exptl_sample_conditions'],
                                  'nmrconstraints': ['pdbx_nmr_constraint_file'],
                                  'nmrspectralpeaklist': ['pdbx_nmr_spectral_peak_list',
                                                          'pdbx_nmr_spectral_dim',
                                                          'pdbx_nmr_spectral_peak_software',
                                                          'pdbx_nmr_exptl',
                                                          'pdbx_nmr_sample_details',
                                                          'pdbx_nmr_software'],
                                  'nmrrefinement': ['pdbx_nmr_ensemble',
                                                    'pdbx_nmr_representative',
                                                    'pdbx_nmr_refine',
                                                    'pdbx_nmr_software',
                                                    'pdbx_initial_refinement_model']
                                  }

        self.__nmrIfCategories = set()
        for catList in self.__cifRequirements.values():
            for cat in catList:
                self.__nmrIfCategories.add(cat)

        self.__pages = ('sample',
                        'spectrometer',
                        'experiment',
                        'software',
                        'chem_shift_ref',
                        'chem_shift',
                        'constraint',
                        'spectral_peak',
                        'refinement')

        self.__sfCategory = {'sample': ['sample', 'sample_conditions'],
                             'spectrometer': ['NMR_spectrometer_list', 'NMR_spectrometer'],
                             'experiment': ['experiment_list'],
                             'software': ['software'],
                             'chem_shift_ref': ['chem_shift_reference'],
                             'chem_shift': ['assigned_chemical_shifts'],
                             'constraint': ['constraint_statistics'],
                             'spectral_peak': ['spectral_peak_list'],
                             'refinement': ['conformer_statistics', 'conformer_family_coord_set']
                             }

        self.__sfTagPrefix = {'sample': ['_Sample', '_Sample_condition_list'],
                              'spectrometer': ['_NMR_spectrometer_list', '_NMR_spectrometer'],
                              'experiment': ['_Experiment_list'],
                              'software': ['_Software'],
                              'chem_shift_ref': ['_Chem_shift_reference'],
                              'chem_shift': ['_Assigned_chem_shift_list'],
                              'constraint': ['_Constraint_stat_list'],
                              'spectral_peak': ['_Spectral_peak_list'],
                              'refinement': ['_Conformer_stat_list', '_Conformer_family_coord_set']
                              }

        self.__sfNewFlag = {'sample': [True, True],
                            'spectrometer': [True, True],
                            'experiment': [True],
                            'software': [True],
                            'chem_shift_ref': [True],
                            'chem_shift': [False],
                            'constraint': [False],
                            'spectral_peak': [False],
                            'refinement': [True, True]
                            }

        self.__lpCategory = {'sample': {'_Sample': ['_Sample_component'],
                                        '_Sample_condition_list': ['_Sample_condition_variable']},
                             'spectrometer': {'_NMR_spectrometer_list': ['_NMR_spectrometer_view']},
                             'experiment': {'_Experiment_list': ['_Experiment']},
                             'software': {'_Software': ['_Vendor', '_Task']},
                             'chem_shift_ref': {'_Chem_shift_reference': ['_Chem_shift_ref']},
                             'chem_shift': {'_Assigned_chem_shift_list': ['_Chem_shift_experiment', '_Systematic_chem_shift_offset', '_Chem_shift_software']},
                             'constraint': {'_Constraint_stat_list': ['_Constraint_file']},
                             'spectral_peak': {'_Spectral_peak_list': ['_Spectral_dim', '_Spectral_peak_software']},
                             'refinement': {'_Conformer_family_coord_set': ['_Conformer_family_refinement', '_Conformer_family_software']}
                             }

        self.__lpNewFlag = {'sample': {'_Sample': [True],
                                       '_Sample_condition_list': [True]},
                            'spectrometer': {'_NMR_spectrometer_list': [True]},
                            'experiment': {'_Experiment_list': [True]},
                            'software': {'_Software': [True, True]},
                            'chem_shift_ref': {'_Chem_shift_reference': [True]},
                            'chem_shift': {'_Assigned_chem_shift_list': [True, True, True]},
                            'constraint': {'_Constraint_stat_list': [False]},
                            'spectral_peak': {'_Spectral_peak_list': [False]},
                            'refinement': {'_Conformer_family_coord_set': [True, True]}
                            }

        # tagmap.csv is derived from onedep2bmrb @see https://github.com/bmrb-io/onedep2bmrb/blob/master/testfiles/tagmap.csv

        sfCatList = []
        for v in self.__sfTagPrefix.values():
            sfCatList.extend(v)

        sfCatList = [c[1:] for c in sfCatList]

        lpCatList = []
        for v in self.__lpCategory.values():
            for _v in v.values():
                lpCatList.extend(_v)

        lpCatList = [c[1:] for c in lpCatList]
        # """
        # self.tagMap = self.load_csv_data('./lib/tagmap.csv', transpose=False)
        #
        # self.__sfTagMap = []
        # for tag_map in self.tagMap:
        #     if tag_map[2] in sfCatList and tag_map[0] in self.__nmrIfCategories:
        #         if tag_map not in self.__sfTagMap:
        #             print(f'                           ({tag_map[0]!r}, {tag_map[1]!r}, {"_" + tag_map[2]!r}, {tag_map[3]!r}, '
        #                   f'{int(tag_map[4]) if len(tag_map[4]) > 0 else None}, {int(tag_map[5]) if len(tag_map[5]) > 0 else None}),')
        #             self.__sfTagMap.append(tag_map)
        # """
        self.__sfTagMap = [('pdbx_nmr_assigned_chem_shift_list', 'chem_shift_13C_err', '_Assigned_chem_shift_list', 'Chem_shift_13C_err', 1, None),
                           ('pdbx_nmr_assigned_chem_shift_list', 'chem_shift_15N_err', '_Assigned_chem_shift_list', 'Chem_shift_15N_err', 1, None),
                           ('pdbx_nmr_assigned_chem_shift_list', 'chem_shift_19F_err', '_Assigned_chem_shift_list', 'Chem_shift_19F_err', 1, None),
                           ('pdbx_nmr_assigned_chem_shift_list', 'chem_shift_1H_err', '_Assigned_chem_shift_list', 'Chem_shift_1H_err', 1, None),
                           ('pdbx_nmr_assigned_chem_shift_list', 'chem_shift_2H_err', '_Assigned_chem_shift_list', 'Chem_shift_2H_err', 1, None),
                           ('pdbx_nmr_assigned_chem_shift_list', 'chem_shift_31P_err', '_Assigned_chem_shift_list', 'Chem_shift_31P_err', 1, None),
                           ('pdbx_nmr_assigned_chem_shift_list', 'chem_shift_reference_id', '_Assigned_chem_shift_list', 'Chem_shift_reference_ID', 1, None),
                           # add pdbx_nmr_assigned_chem_shift_list.chem_shift_reference_label
                           ('pdbx_nmr_assigned_chem_shift_list', 'chem_shift_reference_label', '_Assigned_chem_shift_list', 'Chem_shift_reference_label', 1, None),
                           ('pdbx_nmr_assigned_chem_shift_list', 'conditions_id', '_Assigned_chem_shift_list', 'Sample_condition_list_ID', 1, None),
                           # ('pdbx_nmr_assigned_chem_shift_list', 'conditions_id', '_Sample_condition_list', 'ID', 1, None),
                           ('pdbx_nmr_assigned_chem_shift_list', 'conditions_label', '_Assigned_chem_shift_list', 'Sample_condition_list_label', 1, None),
                           ('pdbx_nmr_assigned_chem_shift_list', 'data_file_name', '_Assigned_chem_shift_list', 'Data_file_name', 1, None),
                           ('pdbx_nmr_assigned_chem_shift_list', 'details', '_Assigned_chem_shift_list', 'Details', 1, None),
                           ('pdbx_nmr_assigned_chem_shift_list', 'entry_id', '_Assigned_chem_shift_list', 'Entry_ID', 1, None),
                           ('pdbx_nmr_assigned_chem_shift_list', 'error_derivation_method', '_Assigned_chem_shift_list', 'Error_derivation_method', 1, None),
                           ('pdbx_nmr_assigned_chem_shift_list', 'id', '_Assigned_chem_shift_list', 'ID', 1, None),
                           ('pdbx_nmr_assigned_chem_shift_list', 'label', '_Assigned_chem_shift_list', 'Sf_framecode', 1, None),
                           ('pdbx_nmr_chem_shift_reference', 'carbon_shifts_flag', '_Chem_shift_reference', 'Carbon_shifts_flag', 1, None),
                           ('pdbx_nmr_chem_shift_reference', 'details', '_Chem_shift_reference', 'Details', 1, None),
                           ('pdbx_nmr_chem_shift_reference', 'entry_id', '_Chem_shift_reference', 'Entry_ID', 1, None),
                           ('pdbx_nmr_chem_shift_reference', 'id', '_Chem_shift_reference', 'ID', 1, None),
                           ('pdbx_nmr_chem_shift_reference', 'label', '_Chem_shift_reference', 'Sf_framecode', 1, None),
                           ('pdbx_nmr_chem_shift_reference', 'nitrogen_shifts_flag', '_Chem_shift_reference', 'Nitrogen_shifts_flag', 1, None),
                           ('pdbx_nmr_chem_shift_reference', 'other_shifts_flag', '_Chem_shift_reference', 'Other_shifts_flag', 1, None),
                           ('pdbx_nmr_chem_shift_reference', 'phosphorus_shifts_flag', '_Chem_shift_reference', 'Phosphorus_shifts_flag', 1, None),
                           ('pdbx_nmr_chem_shift_reference', 'proton_shifts_flag', '_Chem_shift_reference', 'Proton_shifts_flag', 1, None),
                           ('pdbx_nmr_chem_shift_software', 'software_label', '_Software', 'Sf_framecode', 1, None),
                           ('pdbx_nmr_ensemble', 'average_constraint_violations_per_residue', '_Constraint_stat_list', 'Constr_violations_per_residue_avg', 1, None),
                           ('pdbx_nmr_ensemble', 'average_constraints_per_residue', '_Constraint_stat_list', 'Constraints_per_residue_avg', 1, None),
                           ('pdbx_nmr_ensemble', 'conformer_selection_criteria', '_Conformer_stat_list', 'Conformer_selection_criteria', 1, None),
                           ('pdbx_nmr_ensemble', 'conformers_calculated_total_number', '_Conformer_stat_list', 'Conformer_calculated_total_num', 1, None),
                           ('pdbx_nmr_ensemble', 'conformers_submitted_total_number', '_Conformer_stat_list', 'Conformer_submitted_total_num', 1, None),
                           ('pdbx_nmr_ensemble', 'distance_constraint_violation_method', '_Constraint_stat_list', 'Dist_constr_violat_stat_calc_method', 1, None),
                           ('pdbx_nmr_ensemble', 'entry_id', '_Conformer_stat_list', 'Entry_ID', 1, None),
                           ('pdbx_nmr_ensemble', 'representative_conformer', '_Conformer_stat_list', 'Representative_conformer', 1, None),
                           # ('pdbx_nmr_exptl_sample_conditions', 'conditions_id', '_Sample_condition_list', 'ID', 1, None),
                           # replaced by
                           ('pdbx_nmr_exptl_sample_conditions', 'conditions_id', '_Sample_condition_list', 'Sf_framecode', 1, None),
                           # ('pdbx_nmr_exptl_sample_conditions', 'label', '_Sample_condition_list', 'Sf_framecode', 1, None),
                           ('pdbx_nmr_representative', 'conformer_id', '_Conformer_stat_list', 'Representative_conformer', 1, None),
                           ('pdbx_nmr_representative', 'entry_id', '_Conformer_stat_list', 'Entry_ID', 1, None),
                           ('pdbx_nmr_representative', 'selection_criteria', '_Conformer_stat_list', 'Rep_conformer_selection_criteria', 1, None),
                           ('pdbx_nmr_sample_details', 'contents', '_Sample', 'Details', 1, 0),
                           ('pdbx_nmr_sample_details', 'solution_id', '_Sample', 'ID', 1, None),
                           ('pdbx_nmr_sample_details', 'solvent_system', '_Sample', 'Solvent_system', 1, None),
                           ('pdbx_nmr_sample_details', 'type', '_Sample', 'Type', 1, None),
                           # add pdbx_nmr_sample_details.label
                           ('pdbx_nmr_sample_details', 'label', '_Sample', 'Sf_framecode', 1, None),
                           # ('pdbx_nmr_software', 'authors', '_Software', 'ID', 5, None),
                           ('pdbx_nmr_software', 'details', '_Software', 'Details', 1, None),
                           ('pdbx_nmr_software', 'details', '_Spectral_peak_list', 'Text_data_format', 1, None),
                           # map_code '-11' indicates children loops has metadata to be merged
                           ('pdbx_nmr_software', 'name', '_Software', 'Name', -11, None),
                           # ('pdbx_nmr_software', 'name', '_Software', 'Sf_framecode', 1, None),
                           ('pdbx_nmr_software', 'ordinal', '_Software', 'ID', 1, None),
                           ('pdbx_nmr_software', 'version', '_Software', 'Version', 1, None),
                           ('pdbx_nmr_spectral_peak_list', 'conditions_id', '_Spectral_peak_list', 'Sample_condition_list_ID', 1, None),
                           # add pdbx_nmr_spectral_peak_list.conditions_label
                           ('pdbx_nmr_spectral_peak_list', 'conditions_label', '_Spectral_peak_list', 'Sample_condition_list_label', 1, None),
                           ('pdbx_nmr_spectral_peak_list', 'data_file_name', '_Spectral_peak_list', 'Data_file_name', 1, None),
                           ('pdbx_nmr_spectral_peak_list', 'details', '_Spectral_peak_list', 'Details', 1, None),
                           ('pdbx_nmr_spectral_peak_list', 'entry_id', '_Spectral_peak_list', 'Entry_ID', 1, None),
                           ('pdbx_nmr_spectral_peak_list', 'experiment_id', '_Spectral_peak_list', 'Experiment_ID', 1, None),
                           ('pdbx_nmr_spectral_peak_list', 'id', '_Spectral_peak_list', 'ID', 1, None),
                           ('pdbx_nmr_spectral_peak_list', 'number_of_spectral_dimensions', '_Spectral_peak_list', 'Number_of_spectral_dimensions', 1, None),
                           ('pdbx_nmr_spectral_peak_list', 'solution_id', '_Spectral_peak_list', 'Sample_ID', 1, None),
                           # add pdbx_nmr_spectral_peak_list.solution_label
                           ('pdbx_nmr_spectral_peak_list', 'solution_label', '_Spectral_peak_list', 'Sample_label', 1, None),
                           # add pdbx_nmr_spectral_peak_list.assigned_chem_shift_list_id
                           ('pdbx_nmr_spectral_peak_list', 'assigned_chem_shift_list_id', '_Spectral_peak_list', 'Assigned_chem_shift_list_ID', 1, None),
                           # add pdbx_nmr_spectral_peak_list.assigned_chem_shift_list_label
                           ('pdbx_nmr_spectral_peak_list', 'assigned_chem_shift_list_label', '_Spectral_peak_list', 'Assigned_chem_shift_list_label', 1, None),
                           ('pdbx_nmr_spectral_peak_list', 'text_data_format', '_Software', 'Details', 1, None),
                           ('pdbx_nmr_spectral_peak_list', 'text_data_format', '_Spectral_peak_list', 'Text_data_format', 1, None),
                           # add pdbx_nmr_spectral_peak_list.label
                           ('pdbx_nmr_spectral_peak_list', 'label', '_Spectral_peak_list', 'Sf_framecode', 1, None),
                           ('pdbx_nmr_spectrometer', 'details', '_NMR_spectrometer', 'Details', 1, None),
                           ('pdbx_nmr_spectrometer', 'field_strength', '_NMR_spectrometer', 'Field_strength', 1, None),
                           ('pdbx_nmr_spectrometer', 'manufacturer', '_NMR_spectrometer', 'Manufacturer', 1, None),
                           ('pdbx_nmr_spectrometer', 'model', '_NMR_spectrometer', 'Model', 1, None),
                           ('pdbx_nmr_spectrometer', 'name', '_NMR_spectrometer', 'Sf_framecode', 1, None),
                           ('pdbx_nmr_spectrometer', 'spectrometer_id', '_NMR_spectrometer', 'ID', 1, None)
                           ]

        self.__uniqSfTagMap = []
        sf_map = {}
        sf_cif_tags = []
        for tag_map in self.__sfTagMap:
            cif_category, sf_tag_prefix = tag_map[0], tag_map[2]
            if cif_category not in sf_map:
                sf_map[cif_category] = []
            sf_map[cif_category].append(sf_tag_prefix)
        for cif_category, v in sf_map.items():
            sf_map[cif_category] = collections.Counter(v).most_common()
            tag_maps = [tag_map for tag_map in self.__sfTagMap if tag_map[0] == cif_category]
            for tag_map in tag_maps:
                sf_cif_tag, sf_tag_prefix = tag_map[1], tag_map[2]
                if sf_tag_prefix == sf_map[cif_category][0][0]:
                    sf_cif_tags.append(f'{cif_category}.{sf_cif_tag}')
                    self.__uniqSfTagMap.append(tag_map)
            for tag_map in tag_maps:
                sf_cif_tag, sf_tag_prefix = tag_map[1], tag_map[2]
                if sf_tag_prefix != sf_map[cif_category][0][0]:
                    if f'{cif_category}.{sf_cif_tag}' not in sf_cif_tags:
                        sf_cif_tags.append(f'{cif_category}.{sf_cif_tag}')
                        self.__uniqSfTagMap.append(tag_map)

        self.__uniqSfCatMap = {}
        for tag_map in self.__uniqSfTagMap:
            cif_category, sf_tag_prefix = tag_map[0], tag_map[2]
            if cif_category not in self.__uniqSfCatMap:
                sf_category = None
                for page in self.__pages:
                    for _sf_tag_prefix, _sf_category in zip(self.__sfTagPrefix[page], self.__sfCategory[page]):
                        if _sf_tag_prefix == sf_tag_prefix:
                            sf_category = _sf_category
                            break
                    if sf_category is not None:
                        break
                self.__uniqSfCatMap[cif_category] = (sf_category, sf_tag_prefix)
        # 'pdbx_nmr_exptl' category has no effective item to relate '_Experiment_list'
        self.__uniqSfCatMap['pdbx_nmr_exptl'] = ('experiment_list', '_Experiment_list')
        # 'pdbx_nmr_refine' category has no effective item to relate '_Conformer_family_coord_set'
        self.__uniqSfCatMap['pdbx_nmr_refine'] = ('conformer_family_coord_set', '_Conformer_family_coord_set')

        # add pdbx_nmr_sample_condisions.label, pdbx_nmr_sample_condisions.conditions_id
        self.__sfTagMap.extend([('pdbx_nmr_exptl_sample_conditions', 'label', '_Sample_condition_list', 'Details', 1, None),
                                ('pdbx_nmr_exptl_sample_conditions', 'conditions_id', '_Sample_condition_list', 'ID', 1, None)])

        # """
        # self.__lpTagMap = []
        # for tag_map in self.tagMap:
        #     if tag_map[2] in lpCatList and tag_map[0] in self.__nmrIfCategories:
        #         if tag_map not in self.__lpTagMap:
        #             print(f'                           ({tag_map[0]!r}, {tag_map[1]!r}, {"_" + tag_map[2]!r}, {tag_map[3]!r}, '
        #                   f'{int(tag_map[4]) if len(tag_map[4]) > 0 else None}, {int(tag_map[5]) if len(tag_map[5]) > 0 else None}),')
        #             self.__lpTagMap.append(tag_map)
        # """
        self.__lpTagMap = [('pdbx_nmr_chem_shift_experiment', 'assigned_chem_shift_list_id', '_Chem_shift_experiment', 'Assigned_chem_shift_list_ID', 1, None),
                           ('pdbx_nmr_chem_shift_experiment', 'entry_id', '_Chem_shift_experiment', 'Entry_ID', 1, None),
                           ('pdbx_nmr_chem_shift_experiment', 'experiment_id', '_Chem_shift_experiment', 'Experiment_ID', 1, None),
                           ('pdbx_nmr_chem_shift_experiment', 'experiment_name', '_Chem_shift_experiment', 'Experiment_name', 1, None),
                           ('pdbx_nmr_chem_shift_experiment', 'sample_state', '_Chem_shift_experiment', 'Sample_state', 1, None),
                           ('pdbx_nmr_chem_shift_experiment', 'solution_id', '_Chem_shift_experiment', 'Sample_ID', 1, None),
                           ('pdbx_nmr_chem_shift_ref', 'atom_group', '_Chem_shift_ref', 'Atom_group', 1, None),
                           ('pdbx_nmr_chem_shift_ref', 'atom_isotope_number', '_Chem_shift_ref', 'Atom_isotope_number', 1, None),
                           ('pdbx_nmr_chem_shift_ref', 'atom_type', '_Chem_shift_ref', 'Atom_type', 1, None),
                           ('pdbx_nmr_chem_shift_ref', 'chem_shift_reference_id', '_Chem_shift_ref', 'Chem_shift_reference_ID', 1, None),
                           ('pdbx_nmr_chem_shift_ref', 'chem_shift_units', '_Chem_shift_ref', 'Chem_shift_units', 1, None),
                           ('pdbx_nmr_chem_shift_ref', 'chem_shift_val', '_Chem_shift_ref', 'Chem_shift_val', 1, None),
                           ('pdbx_nmr_chem_shift_ref', 'correction_val', '_Chem_shift_ref', 'Correction_val', 1, None),
                           ('pdbx_nmr_chem_shift_ref', 'entry_id', '_Chem_shift_ref', 'Entry_ID', 1, None),
                           ('pdbx_nmr_chem_shift_ref', 'external_ref_axis', '_Chem_shift_ref', 'External_ref_axis', 1, None),
                           ('pdbx_nmr_chem_shift_ref', 'external_ref_loc', '_Chem_shift_ref', 'External_ref_loc', 1, None),
                           ('pdbx_nmr_chem_shift_ref', 'external_ref_sample_geometry', '_Chem_shift_ref', 'External_ref_sample_geometry', 1, None),
                           ('pdbx_nmr_chem_shift_ref', 'indirect_shift_ratio', '_Chem_shift_ref', 'Indirect_shift_ratio', 1, None),
                           ('pdbx_nmr_chem_shift_ref', 'mol_common_name', '_Chem_shift_ref', 'Mol_common_name', 1, None),
                           ('pdbx_nmr_chem_shift_ref', 'rank', '_Chem_shift_ref', 'Rank', 1, None),
                           ('pdbx_nmr_chem_shift_ref', 'ref_correction_type', '_Chem_shift_ref', 'Ref_correction_type', 1, None),
                           ('pdbx_nmr_chem_shift_ref', 'ref_method', '_Chem_shift_ref', 'Ref_method', 1, None),
                           ('pdbx_nmr_chem_shift_ref', 'ref_type', '_Chem_shift_ref', 'Ref_type', 1, None),
                           ('pdbx_nmr_chem_shift_ref', 'solvent', '_Chem_shift_ref', 'Solvent', 1, None),
                           ('pdbx_nmr_chem_shift_software', 'assigned_chem_shift_list_id', '_Chem_shift_software', 'Assigned_chem_shift_list_ID', 1, None),
                           ('pdbx_nmr_chem_shift_software', 'entry_id', '_Chem_shift_software', 'Entry_ID', 1, None),
                           ('pdbx_nmr_chem_shift_software', 'software_id', '_Chem_shift_software', 'Software_ID', 1, None),
                           ('pdbx_nmr_constraint_file', 'constraint_filename', '_Constraint_file', 'Constraint_filename', 1, None),
                           ('pdbx_nmr_constraint_file', 'constraint_number', '_Constraint_file', 'Constraint_number', 1, None),
                           ('pdbx_nmr_constraint_file', 'constraint_subtype', '_Constraint_file', 'Constraint_subtype', 1, None),
                           ('pdbx_nmr_constraint_file', 'constraint_type', '_Constraint_file', 'Constraint_type', 1, None),
                           ('pdbx_nmr_constraint_file', 'entry_id', '_Constraint_file', 'Entry_ID', 1, None),
                           ('pdbx_nmr_constraint_file', 'id', '_Constraint_file', 'ID', 1, None),
                           ('pdbx_nmr_constraint_file', 'software_name', '_Constraint_file', 'Software_name', 1, None),
                           ('pdbx_nmr_constraint_file', 'software_ordinal', '_Constraint_file', 'Software_ID', 1, None),
                           ('pdbx_nmr_exptl', 'conditions_id', '_Experiment', 'Sample_condition_list_ID', 1, None),
                           ('pdbx_nmr_exptl', 'experiment_id', '_Experiment', 'ID', 1, None),
                           ('pdbx_nmr_exptl', 'sample_state', '_Experiment', 'Sample_state', 1, None),
                           ('pdbx_nmr_exptl', 'solution_id', '_Experiment', 'Sample_ID', 1, None),
                           ('pdbx_nmr_exptl', 'spectrometer_id', '_Experiment', 'NMR_spectrometer_ID', 1, None),
                           ('pdbx_nmr_exptl', 'type', '_Experiment', 'Name', 1, None),
                           ('pdbx_nmr_exptl_sample', 'component', '_Sample_component', 'Mol_common_name', 1, None),
                           ('pdbx_nmr_exptl_sample', 'concentration', '_Sample_component', 'Concentration_val', 1, None),
                           ('pdbx_nmr_exptl_sample', 'concentration_err', '_Sample_component', 'Concentration_val_err', 1, None),
                           ('pdbx_nmr_exptl_sample', 'concentration_range', '_Sample_component', 'Concentration_val_max', -22, None),
                           ('pdbx_nmr_exptl_sample', 'concentration_range', '_Sample_component', 'Concentration_val_min', -22, None),
                           ('pdbx_nmr_exptl_sample', 'concentration_units', '_Sample_component', 'Concentration_val_units', 1, None),
                           ('pdbx_nmr_exptl_sample', 'isotopic_labeling', '_Sample_component', 'Isotopic_labeling', 1, None),
                           ('pdbx_nmr_exptl_sample', 'solution_id', '_Sample_component', 'Sample_ID', 1, None),
                           # ('pdbx_nmr_exptl_sample_conditions', 'conditions_id', '_Sample_condition_variable', 'Sample_condition_list_ID', 1, None),
                           # replaced by
                           ('pdbx_nmr_exptl_sample_conditions', 'conditions_id', '_Sample_condition_variable', 'Sample_condition_list_ID',
                            33, '_Sample_condition_list.Sf_framecode'),
                           # add pdbx_nmr_exptl_sample_conditions.label
                           ('pdbx_nmr_exptl_sample_conditions', 'label', '_Sample_condition_variable', 'Sample_condition_list_ID',
                            -33, '_Sample_condition_list.Sf_framecode'),
                           ('pdbx_nmr_exptl_sample_conditions', 'ionic_strength', '_Sample_condition_variable', 'Type', -22, 0),
                           ('pdbx_nmr_exptl_sample_conditions', 'ionic_strength', '_Sample_condition_variable', 'Val', -22, 0),
                           ('pdbx_nmr_exptl_sample_conditions', 'ionic_strength_err', '_Sample_condition_variable', 'Val_err', -22, None),
                           ('pdbx_nmr_exptl_sample_conditions', 'ionic_strength_units', '_Sample_condition_variable', 'Val_units', -22, None),
                           ('pdbx_nmr_exptl_sample_conditions', 'pH', '_Sample_condition_variable', 'Type', -22, 0),
                           ('pdbx_nmr_exptl_sample_conditions', 'pH', '_Sample_condition_variable', 'Val', -22, 0),
                           ('pdbx_nmr_exptl_sample_conditions', 'pH_err', '_Sample_condition_variable', 'Val_err', -22, None),
                           ('pdbx_nmr_exptl_sample_conditions', 'pH_units', '_Sample_condition_variable', 'Val_units', -22, None),
                           ('pdbx_nmr_exptl_sample_conditions', 'pressure', '_Sample_condition_variable', 'Type', -22, 0),
                           ('pdbx_nmr_exptl_sample_conditions', 'pressure', '_Sample_condition_variable', 'Val', -22, 0),
                           ('pdbx_nmr_exptl_sample_conditions', 'pressure_err', '_Sample_condition_variable', 'Val_err', -22, 0),
                           ('pdbx_nmr_exptl_sample_conditions', 'pressure_units', '_Sample_condition_variable', 'Val_units', -22, None),
                           ('pdbx_nmr_exptl_sample_conditions', 'temperature', '_Sample_condition_variable', 'Type', -22, 0),
                           ('pdbx_nmr_exptl_sample_conditions', 'temperature', '_Sample_condition_variable', 'Val', -22, 0),
                           ('pdbx_nmr_exptl_sample_conditions', 'temperature_err', '_Sample_condition_variable', 'Val_err', -22, None),
                           ('pdbx_nmr_exptl_sample_conditions', 'temperature_units', '_Sample_condition_variable', 'Val_units', -22, None),
                           ('pdbx_nmr_refine', 'details', '_Conformer_family_refinement', 'Refine_details', 1, None),
                           ('pdbx_nmr_refine', 'method', '_Conformer_family_refinement', 'Refine_method', 1, None),
                           # add pdbx_nmr_refine.software_ordinal
                           ('pdbx_nmr_refine', 'software_ordinal', '_Conformer_family_refinement', 'Software_ID', 1, None),
                           # add pdbx_nmr_refine.details
                           ('pdbx_nmr_refine', 'details', '_Conformer_family_refinement', 'Refine_details', 1, None),
                           # map_code '-11' indicates metadata need to be merged with parent saveframe tags
                           ('pdbx_nmr_software', 'authors', '_Vendor', 'Name', -11, None),
                           ('pdbx_nmr_software', 'classification', '_Task', 'Task', -11, None),
                           # the next two items are errors of tagmap.csv
                           # ('pdbx_nmr_software', 'classification', '_Task', 'Software_ID', 5, None),
                           # ('pdbx_nmr_software', 'name', '_Vendor', 'Software_ID', 5, None),
                           # replaced by the next two lines
                           ('pdbx_nmr_software', 'ordinal', '_Vendor', 'Software_ID', 1, None),
                           ('pdbx_nmr_software', 'ordinal', '_Task', 'Software_ID', 1, None),
                           #
                           ('pdbx_nmr_spectral_dim', 'atom_isotope_number', '_Spectral_dim', 'Atom_isotope_number', 1, None),
                           ('pdbx_nmr_spectral_dim', 'atom_type', '_Spectral_dim', 'Atom_type', 1, None),
                           ('pdbx_nmr_spectral_dim', 'center_frequency_offset', '_Spectral_dim', 'Center_frequency_offset', 1, None),
                           ('pdbx_nmr_spectral_dim', 'encoded_source_dimension_id', '_Spectral_dim', 'Encoded_reduced_dimension_ID', 1, None),
                           ('pdbx_nmr_spectral_dim', 'encoding_code', '_Spectral_dim', 'Encoding_code', 1, None),
                           ('pdbx_nmr_spectral_dim', 'entry_id', '_Spectral_dim', 'Entry_ID', 1, None),
                           ('pdbx_nmr_spectral_dim', 'id', '_Spectral_dim', 'ID', 1, None),
                           ('pdbx_nmr_spectral_dim', 'magnetization_linkage_id', '_Spectral_dim', 'Magnetization_linkage_ID', 1, None),
                           ('pdbx_nmr_spectral_dim', 'spectral_peak_list_id', '_Spectral_dim', 'Spectral_peak_list_ID', 1, None),
                           ('pdbx_nmr_spectral_dim', 'spectral_region', '_Spectral_dim', 'Spectral_region', 1, None),
                           ('pdbx_nmr_spectral_dim', 'sweep_width', '_Spectral_dim', 'Sweep_width', 1, None),
                           ('pdbx_nmr_spectral_dim', 'sweep_width_units', '_Spectral_dim', 'Sweep_width_units', 1, None),
                           ('pdbx_nmr_spectral_dim', 'under_sampling_type', '_Spectral_dim', 'Under_sampling_type', 1, None),
                           # add pdbx_nmr_spectral_peak_software.spectral_peak_list_id
                           ('pdbx_nmr_spectral_peak_software', 'spectral_peak_list_id', '_Spectral_peak_software', 'Spectral_peak_list_ID', 1, None),
                           # add pdbx_nmr_spectral_peak_software.software_id
                           ('pdbx_nmr_spectral_peak_software', 'spectral_peak_list_id', '_Spectral_peak_software', 'Software_ID', 1, None),
                           ('pdbx_nmr_spectrometer', 'field_strength', '_NMR_spectrometer_view', 'Field_strength', 1, None),
                           ('pdbx_nmr_spectrometer', 'manufacturer', '_NMR_spectrometer_view', 'Manufacturer', 1, None),
                           ('pdbx_nmr_spectrometer', 'model', '_NMR_spectrometer_view', 'Model', 1, None),
                           ('pdbx_nmr_spectrometer', 'spectrometer_id', '_NMR_spectrometer_view', 'ID', 1, None),
                           ('pdbx_nmr_systematic_chem_shift_offset', 'assigned_chem_shift_list_id', '_Systematic_chem_shift_offset', 'Assigned_chem_shift_list_ID', 1, None),
                           ('pdbx_nmr_systematic_chem_shift_offset', 'atom_isotope_number', '_Systematic_chem_shift_offset', 'Atom_isotope_number', 1, None),
                           ('pdbx_nmr_systematic_chem_shift_offset', 'atom_type', '_Systematic_chem_shift_offset', 'Atom_type', 1, None),
                           ('pdbx_nmr_systematic_chem_shift_offset', 'entry_id', '_Systematic_chem_shift_offset', 'Entry_ID', 1, None),
                           ('pdbx_nmr_systematic_chem_shift_offset', 'type', '_Systematic_chem_shift_offset', 'Type', 1, None),
                           ('pdbx_nmr_systematic_chem_shift_offset', 'val', '_Systematic_chem_shift_offset', 'Val', 1, None),
                           ('pdbx_nmr_systematic_chem_shift_offset', 'val_err', '_Systematic_chem_shift_offset', 'Val_err', 1, None)
                           ]

        self.__uniqLpCatMap = {}
        for tag_map in self.__lpTagMap:
            cif_category, lp_category = tag_map[0], tag_map[2]
            if cif_category not in self.__uniqLpCatMap:
                self.__uniqLpCatMap[cif_category] = []
            self.__uniqLpCatMap[cif_category].append(lp_category)
        for cif_category, v in self.__uniqLpCatMap.items():
            lp_categories = [_v[0] for _v in collections.Counter(v).most_common()]
            sf_tag_prefix = None
            for page in self.__pages:
                for _sf_tag_prefix, _lp_categories in self.__lpCategory[page].items():
                    if lp_categories[0] in _lp_categories:
                        sf_tag_prefix = _sf_tag_prefix
                        break
                if sf_tag_prefix is not None:
                    break
            self.__uniqLpCatMap[cif_category] = (sf_tag_prefix, lp_categories)

        # adit_item_tbl_o.csv is derived from onedep2bmrb @see https://github.com/bmrb-io/onedep2bmrb/blob/master/testfiles/adit_item_tbl_o.csv

        # """
        # self.__defSfTag = []
        # self.__defLpTag = []
        # self.__sfItem = self.load_csv_data('./lib/adit_item_tbl_o.csv')
        # title = self.__sfItem[0]
        # originalTagCol = title.index('originalTag')
        # aditExistsCol = title.index('aditExists')
        # internalFlgCol = title.index('internalFlg')
        # for row in self.__sfItem:
        #     tag, init_tag, internal = row[originalTagCol], row[aditExistsCol], row[internalFlgCol]
        #     if init_tag != 'Y' or internal == 'Y':
        #         continue
        #     if tag.startswith('_') and '.' in tag:
        #         category, item = tag.split('.')
        #         is_sf_tag_prefix = is_lp_category = False
        #         for page in self.__pages:
        #             if category in self.__sfTagPrefix[page]:
        #                 is_sf_tag_prefix = True
        #                 break
        #             for v in self.__lpCategory[page].values():
        #                 if category in v:
        #                     is_lp_category = True
        #                     break
        #             if is_lp_category:
        #                 break
        #         if is_sf_tag_prefix:
        #             self.__defSfTag.append(tag)
        #             print(f'                           {tag!r},')
        #         if is_lp_category:
        #             self.__defLpTag.append(tag)
        #             print(f'                           {tag!r},')
        # """
        self.__defSfTag = ['_Sample.Sf_category',
                           '_Sample.Sf_framecode',
                           '_Sample.Entry_ID',
                           '_Sample.ID',
                           '_Sample.Type',
                           '_Sample.Sub_type',
                           '_Sample.Details',
                           '_Sample.Aggregate_sample_number',
                           '_Sample.Solvent_system',
                           '_Sample_condition_list.Sf_category',
                           '_Sample_condition_list.Sf_framecode',
                           '_Sample_condition_list.Entry_ID',
                           '_Sample_condition_list.ID',
                           '_Sample_condition_list.Details',
                           '_Software.Sf_category',
                           '_Software.Sf_framecode',
                           '_Software.Entry_ID',
                           '_Software.ID',
                           '_Software.Name',
                           '_Software.Version',
                           '_Software.Details',
                           '_NMR_spectrometer.Sf_category',
                           '_NMR_spectrometer.Sf_framecode',
                           '_NMR_spectrometer.Entry_ID',
                           '_NMR_spectrometer.ID',
                           '_NMR_spectrometer.Details',
                           '_NMR_spectrometer.Manufacturer',
                           '_NMR_spectrometer.Model',
                           '_NMR_spectrometer.Serial_number',
                           '_NMR_spectrometer.Field_strength',
                           '_NMR_spectrometer_list.Sf_category',
                           '_NMR_spectrometer_list.Sf_framecode',
                           '_NMR_spectrometer_list.Entry_ID',
                           '_NMR_spectrometer_list.ID',
                           '_Experiment_list.Sf_category',
                           '_Experiment_list.Sf_framecode',
                           '_Experiment_list.Entry_ID',
                           '_Experiment_list.ID',
                           '_Experiment_list.Details',
                           '_Chem_shift_reference.Sf_category',
                           '_Chem_shift_reference.Sf_framecode',
                           '_Chem_shift_reference.Entry_ID',
                           '_Chem_shift_reference.ID',
                           '_Chem_shift_reference.Details',
                           '_Assigned_chem_shift_list.Sf_category',
                           '_Assigned_chem_shift_list.Sf_framecode',
                           '_Assigned_chem_shift_list.Entry_ID',
                           '_Assigned_chem_shift_list.ID',
                           '_Assigned_chem_shift_list.Sample_condition_list_ID',
                           '_Assigned_chem_shift_list.Sample_condition_list_label',
                           '_Assigned_chem_shift_list.Chem_shift_reference_ID',
                           '_Assigned_chem_shift_list.Chem_shift_reference_label',
                           '_Assigned_chem_shift_list.Chem_shift_1H_err',
                           '_Assigned_chem_shift_list.Chem_shift_13C_err',
                           '_Assigned_chem_shift_list.Chem_shift_15N_err',
                           '_Assigned_chem_shift_list.Chem_shift_31P_err',
                           '_Assigned_chem_shift_list.Chem_shift_2H_err',
                           '_Assigned_chem_shift_list.Chem_shift_19F_err',
                           '_Assigned_chem_shift_list.Error_derivation_method',
                           '_Assigned_chem_shift_list.Details',
                           '_Assigned_chem_shift_list.Text_data_format',
                           '_Assigned_chem_shift_list.Text_data',
                           '_Spectral_peak_list.Sf_category',
                           '_Spectral_peak_list.Sf_framecode',
                           '_Spectral_peak_list.Entry_ID',
                           '_Spectral_peak_list.ID',
                           '_Spectral_peak_list.Sample_ID',
                           '_Spectral_peak_list.Sample_label',
                           '_Spectral_peak_list.Sample_condition_list_ID',
                           '_Spectral_peak_list.Sample_condition_list_label',
                           '_Spectral_peak_list.Experiment_ID',
                           '_Spectral_peak_list.Experiment_name',
                           '_Spectral_peak_list.Number_of_spectral_dimensions',
                           '_Spectral_peak_list.Details',
                           '_Spectral_peak_list.Text_data_format',
                           '_Spectral_peak_list.Text_data',
                           '_Conformer_stat_list.Sf_category',
                           '_Conformer_stat_list.Sf_framecode',
                           '_Conformer_stat_list.Entry_ID',
                           '_Conformer_stat_list.ID',
                           '_Conformer_stat_list.Text_data_format',
                           '_Conformer_stat_list.Text_data',
                           '_Conformer_stat_list.Original_conformer_stats_file_ID',
                           '_Conformer_stat_list.Conf_family_coord_set_ID',
                           '_Conformer_stat_list.Conf_family_coord_set_label',
                           '_Conformer_stat_list.Representative_conformer_ID',
                           '_Conformer_stat_list.Representative_conformer_label',
                           '_Conformer_stat_list.Conformer_calculated_total_num',
                           '_Conformer_stat_list.Conformer_submitted_total_num',
                           '_Conformer_stat_list.Conformer_selection_criteria',
                           '_Conformer_stat_list.Representative_conformer',
                           '_Conformer_stat_list.Rep_conformer_selection_criteria',
                           '_Conformer_stat_list.Statistical_struct_param_details',
                           '_Conformer_stat_list.Details',
                           '_Conformer_family_coord_set.Sf_category',
                           '_Conformer_family_coord_set.Sf_framecode',
                           '_Conformer_family_coord_set.Entry_ID',
                           '_Conformer_family_coord_set.ID',
                           '_Conformer_family_coord_set.File_name',
                           '_Conformer_family_coord_set.Constraints_PDB_file_ID',
                           '_Conformer_family_coord_set.PDB_accession_code',
                           '_Conformer_family_coord_set.Sample_condition_list_ID',
                           '_Conformer_family_coord_set.Sample_condition_list_label',
                           '_Conformer_family_coord_set.Atom_site_uncertainty_desc',
                           '_Conformer_family_coord_set.Atom_site_ordered_flag_desc',
                           '_Conformer_family_coord_set.Details',
                           '_Constraint_stat_list.Sf_category',
                           '_Constraint_stat_list.Sf_framecode',
                           '_Constraint_stat_list.Entry_ID',
                           '_Constraint_stat_list.ID',
                           '_Constraint_stat_list.Details',
                           '_Constraint_stat_list.Text_data_format',
                           '_Constraint_stat_list.Text_data',
                           '_Constraint_stat_list.Stats_not_available',
                           '_Constraint_stat_list.NOE_interproton_dist_evaluation',
                           '_Constraint_stat_list.NOE_pseudoatom_corrections',
                           '_Constraint_stat_list.NOE_dist_averaging_method',
                           '_Constraint_stat_list.ROE_interproton_dist_evaluation',
                           '_Constraint_stat_list.ROE_pseudoatom_corrections',
                           '_Constraint_stat_list.ROE_dist_averaging_method',
                           '_Constraint_stat_list.NOE_tot_num',
                           '_Constraint_stat_list.RDC_tot_num',
                           '_Constraint_stat_list.Dihedral_angle_tot_num',
                           '_Constraint_stat_list.Protein_dihedral_angle_tot_num',
                           '_Constraint_stat_list.NA_dihedral_angle_tot_num',
                           '_Constraint_stat_list.NOE_intraresidue_tot_num',
                           '_Constraint_stat_list.NOE_sequential_tot_num',
                           '_Constraint_stat_list.NOE_medium_range_tot_num',
                           '_Constraint_stat_list.NOE_long_range_tot_num',
                           '_Constraint_stat_list.NOE_unique_tot_num',
                           '_Constraint_stat_list.NOE_intraresidue_unique_tot_num',
                           '_Constraint_stat_list.NOE_sequential_unique_tot_num',
                           '_Constraint_stat_list.NOE_medium_range_unique_tot_num',
                           '_Constraint_stat_list.NOE_long_range_unique_tot_num',
                           '_Constraint_stat_list.NOE_unamb_intramol_tot_num',
                           '_Constraint_stat_list.NOE_unamb_intermol_tot_num',
                           '_Constraint_stat_list.NOE_ambig_intramol_tot_num',
                           '_Constraint_stat_list.NOE_ambig_intermol_tot_num',
                           '_Constraint_stat_list.NOE_interentity_tot_num',
                           '_Constraint_stat_list.NOE_other_tot_num',
                           '_Constraint_stat_list.ROE_tot_num',
                           '_Constraint_stat_list.ROE_intraresidue_tot_num',
                           '_Constraint_stat_list.ROE_sequential_tot_num',
                           '_Constraint_stat_list.ROE_medium_range_tot_num',
                           '_Constraint_stat_list.ROE_long_range_tot_num',
                           '_Constraint_stat_list.ROE_unambig_intramol_tot_num',
                           '_Constraint_stat_list.ROE_unambig_intermol_tot_num',
                           '_Constraint_stat_list.ROE_ambig_intramol_tot_num',
                           '_Constraint_stat_list.ROE_ambig_intermol_tot_num',
                           '_Constraint_stat_list.ROE_other_tot_num',
                           '_Constraint_stat_list.RDC_HH_tot_num',
                           '_Constraint_stat_list.RDC_HNC_tot_num',
                           '_Constraint_stat_list.RDC_NH_tot_num',
                           '_Constraint_stat_list.RDC_CC_tot_num',
                           '_Constraint_stat_list.RDC_CN_i_1_tot_num',
                           '_Constraint_stat_list.RDC_CAHA_tot_num',
                           '_Constraint_stat_list.RDC_HNHA_tot_num',
                           '_Constraint_stat_list.RDC_HNHA_i_1_tot_num',
                           '_Constraint_stat_list.RDC_CAC_tot_num',
                           '_Constraint_stat_list.RDC_CAN_tot_num',
                           '_Constraint_stat_list.RDC_intraresidue_tot_num',
                           '_Constraint_stat_list.RDC_sequential_tot_num',
                           '_Constraint_stat_list.RDC_medium_range_tot_num',
                           '_Constraint_stat_list.RDC_long_range_tot_num',
                           '_Constraint_stat_list.RDC_other_tot_num',
                           '_Constraint_stat_list.RDC_unambig_intramol_tot_num',
                           '_Constraint_stat_list.RDC_unambig_intermol_tot_num',
                           '_Constraint_stat_list.RDC_ambig_intramol_tot_num',
                           '_Constraint_stat_list.RDC_ambig_intermol_tot_num',
                           '_Constraint_stat_list.RDC_intermol_tot_num',
                           '_Constraint_stat_list.Protein_phi_angle_tot_num',
                           '_Constraint_stat_list.Protein_psi_angle_tot_num',
                           '_Constraint_stat_list.Protein_chi_one_angle_tot_num',
                           '_Constraint_stat_list.Protein_other_angle_tot_num',
                           '_Constraint_stat_list.Protein_ambig_dihedral_tot_num',
                           '_Constraint_stat_list.Protein_other_tot_num',
                           '_Constraint_stat_list.NA_alpha_angle_tot_num',
                           '_Constraint_stat_list.NA_beta_angle_tot_num',
                           '_Constraint_stat_list.NA_gamma_angle_tot_num',
                           '_Constraint_stat_list.NA_delta_angle_tot_num',
                           '_Constraint_stat_list.NA_epsilon_angle_tot_num',
                           '_Constraint_stat_list.NA_chi_angle_tot_num',
                           '_Constraint_stat_list.NA_sugar_pucker_tot_num',
                           '_Constraint_stat_list.NA_other_angle_tot_num',
                           '_Constraint_stat_list.NA_amb_dihedral_angle_tot_num',
                           '_Constraint_stat_list.NA_other_tot_num',
                           '_Constraint_stat_list.H_bonds_constrained_tot_num',
                           '_Constraint_stat_list.Constr_def_H_bonds_tot_num',
                           '_Constraint_stat_list.SS_bonds_constrained_tot_num',
                           '_Constraint_stat_list.Constr_def_SS_bonds_tot_num',
                           '_Constraint_stat_list.Derived_coupling_const_tot_num',
                           '_Constraint_stat_list.Derived_CACB_chem_shift_tot_num',
                           '_Constraint_stat_list.Derived_1H_chem_shifts_tot_num',
                           '_Constraint_stat_list.Derived_photo_cidnps_tot_num',
                           '_Constraint_stat_list.Derived_paramag_relax_tot_num',
                           '_Constraint_stat_list.Assumed_distances_tot_num',
                           '_Constraint_stat_list.Assumed_angles_tot_num',
                           '_Constraint_stat_list.Constraints_per_residue_avg',
                           '_Constraint_stat_list.Constr_violations_per_residue_avg',
                           '_Constraint_stat_list.Dist_constr_violat_stat_calc_method'
                           ]

        self.__defLpTag = ['_Sample_component.ID',
                           '_Sample_component.Mol_common_name',
                           '_Sample_component.Isotopic_labeling',
                           '_Sample_component.Assembly_ID',
                           '_Sample_component.Assembly_label',
                           '_Sample_component.Entity_ID',
                           '_Sample_component.Entity_label',
                           '_Sample_component.Product_ID',
                           '_Sample_component.Type',
                           '_Sample_component.Concentration_val',
                           '_Sample_component.Concentration_val_min',
                           '_Sample_component.Concentration_val_max',
                           '_Sample_component.Concentration_val_units',
                           '_Sample_component.Concentration_val_err',
                           '_Sample_component.Vendor',
                           '_Sample_component.Vendor_product_name',
                           '_Sample_component.Vendor_product_code',
                           '_Sample_component.Entry_ID',
                           '_Sample_component.Sample_ID',
                           '_Sample_condition_variable.Type',
                           '_Sample_condition_variable.Val',
                           '_Sample_condition_variable.Val_err',
                           '_Sample_condition_variable.Val_units',
                           '_Sample_condition_variable.Entry_ID',
                           '_Sample_condition_variable.Sample_condition_list_ID',
                           '_Vendor.Name',
                           '_Vendor.Address',
                           '_Vendor.Electronic_address',
                           '_Vendor.Entry_ID',
                           '_Vendor.Software_ID',
                           '_Task.Task',
                           '_Task.Entry_ID',
                           '_Task.Software_ID',
                           '_NMR_spectrometer_view.ID',
                           '_NMR_spectrometer_view.Name',
                           '_NMR_spectrometer_view.Manufacturer',
                           '_NMR_spectrometer_view.Model',
                           '_NMR_spectrometer_view.Serial_number',
                           '_NMR_spectrometer_view.Field_strength',
                           '_NMR_spectrometer_view.Details',
                           '_NMR_spectrometer_view.Citation_ID',
                           '_NMR_spectrometer_view.Citation_label',
                           '_NMR_spectrometer_view.Entry_ID',
                           '_NMR_spectrometer_view.NMR_spectrometer_list_ID',
                           '_Experiment.ID',
                           '_Experiment.Name',
                           '_Experiment.Raw_data_flag',
                           '_Experiment.NMR_spec_expt_ID',
                           '_Experiment.NMR_spec_expt_label',
                           '_Experiment.MS_expt_ID',
                           '_Experiment.MS_expt_label',
                           '_Experiment.SAXS_expt_ID',
                           '_Experiment.SAXS_expt_label',
                           '_Experiment.FRET_expt_ID',
                           '_Experiment.FRET_expt_label',
                           '_Experiment.EMR_expt_ID',
                           '_Experiment.EMR_expt_label',
                           '_Experiment.Sample_ID',
                           '_Experiment.Sample_label',
                           '_Experiment.Sample_state',
                           '_Experiment.Sample_volume',
                           '_Experiment.Sample_volume_units',
                           '_Experiment.Sample_condition_list_ID',
                           '_Experiment.Sample_condition_list_label',
                           '_Experiment.Sample_spinning_rate',
                           '_Experiment.Sample_angle',
                           '_Experiment.NMR_tube_type',
                           '_Experiment.NMR_spectrometer_ID',
                           '_Experiment.NMR_spectrometer_label',
                           '_Experiment.NMR_spectrometer_probe_ID',
                           '_Experiment.NMR_spectrometer_probe_label',
                           '_Experiment.NMR_spectral_processing_ID',
                           '_Experiment.NMR_spectral_processing_label',
                           '_Experiment.Mass_spectrometer_ID',
                           '_Experiment.Mass_spectrometer_label',
                           '_Experiment.Xray_instrument_ID',
                           '_Experiment.Xray_instrument_label',
                           '_Experiment.Fluorescence_instrument_ID',
                           '_Experiment.Fluorescence_instrument_label',
                           '_Experiment.EMR_instrument_ID',
                           '_Experiment.EMR_instrument_label',
                           '_Experiment.Chromatographic_system_ID',
                           '_Experiment.Chromatographic_system_label',
                           '_Experiment.Chromatographic_column_ID',
                           '_Experiment.Chromatographic_column_label',
                           '_Experiment.Entry_ID',
                           '_Experiment.Experiment_list_ID',
                           '_Chem_shift_ref.Atom_type',
                           '_Chem_shift_ref.Atom_isotope_number',
                           '_Chem_shift_ref.Mol_common_name',
                           '_Chem_shift_ref.Atom_group',
                           '_Chem_shift_ref.Concentration_val',
                           '_Chem_shift_ref.Concentration_units',
                           '_Chem_shift_ref.Solvent',
                           '_Chem_shift_ref.Rank',
                           '_Chem_shift_ref.Chem_shift_units',
                           '_Chem_shift_ref.Chem_shift_val',
                           '_Chem_shift_ref.Ref_method',
                           '_Chem_shift_ref.Ref_type',
                           '_Chem_shift_ref.Indirect_shift_ratio',
                           '_Chem_shift_ref.External_ref_loc',
                           '_Chem_shift_ref.External_ref_sample_geometry',
                           '_Chem_shift_ref.External_ref_axis',
                           '_Chem_shift_ref.Indirect_shift_ratio_cit_ID',
                           '_Chem_shift_ref.Indirect_shift_ratio_cit_label',
                           '_Chem_shift_ref.Ref_correction_type',
                           '_Chem_shift_ref.Correction_val',
                           '_Chem_shift_ref.Correction_val_cit_ID',
                           '_Chem_shift_ref.Correction_val_cit_label',
                           '_Chem_shift_ref.Entry_ID',
                           '_Chem_shift_ref.Chem_shift_reference_ID',
                           '_Chem_shift_experiment.Experiment_ID',
                           '_Chem_shift_experiment.Experiment_name',
                           '_Chem_shift_experiment.Sample_ID',
                           '_Chem_shift_experiment.Sample_label',
                           '_Chem_shift_experiment.Sample_state',
                           '_Chem_shift_experiment.Entry_ID',
                           '_Chem_shift_experiment.Assigned_chem_shift_list_ID',
                           '_Systematic_chem_shift_offset.Type',
                           '_Systematic_chem_shift_offset.Atom_type',
                           '_Systematic_chem_shift_offset.Atom_isotope_number',
                           '_Systematic_chem_shift_offset.Val',
                           '_Systematic_chem_shift_offset.Val_err',
                           '_Systematic_chem_shift_offset.Entry_ID',
                           '_Systematic_chem_shift_offset.Assigned_chem_shift_list_ID',
                           '_Chem_shift_software.Software_ID',
                           '_Chem_shift_software.Software_label',
                           '_Chem_shift_software.Method_ID',
                           '_Chem_shift_software.Method_label',
                           '_Chem_shift_software.Entry_ID',
                           '_Chem_shift_software.Assigned_chem_shift_list_ID',
                           '_Spectral_dim.ID',
                           '_Spectral_dim.Atom_type',
                           '_Spectral_dim.Atom_isotope_number',
                           '_Spectral_dim.Spectral_region',
                           '_Spectral_dim.Magnetization_linkage_ID',
                           '_Spectral_dim.Under_sampling_type',
                           '_Spectral_dim.Sweep_width',
                           '_Spectral_dim.Sweep_width_units',
                           '_Spectral_dim.Center_frequency_offset',
                           '_Spectral_dim.Encoding_code',
                           '_Spectral_dim.Encoded_reduced_dimension_ID',
                           '_Spectral_dim.Entry_ID',
                           '_Spectral_dim.Spectral_peak_list_ID',
                           '_Conformer_family_refinement.Refine_method',
                           '_Conformer_family_refinement.Refine_details',
                           '_Conformer_family_refinement.Software_ID',
                           '_Conformer_family_refinement.Software_label',
                           '_Conformer_family_refinement.Entry_ID',
                           '_Conformer_family_refinement.Conformer_family_coord_set_ID',
                           '_Conformer_family_software.Software_ID',
                           '_Conformer_family_software.Software_label',
                           '_Conformer_family_software.Method_ID',
                           '_Conformer_family_software.Method_label',
                           '_Conformer_family_software.Entry_ID',
                           '_Conformer_family_software.Conformer_family_coord_set_ID',
                           '_Constraint_file.ID',
                           '_Constraint_file.Constraint_filename',
                           '_Constraint_file.Software_ID',
                           '_Constraint_file.Software_label',
                           '_Constraint_file.Software_name',
                           '_Constraint_file.Block_ID',
                           '_Constraint_file.Constraint_type',
                           '_Constraint_file.Constraint_subtype',
                           '_Constraint_file.Constraint_subsubtype',
                           '_Constraint_file.Constraint_number',
                           '_Constraint_file.Entry_ID',
                           '_Constraint_file.Constraint_stat_list_ID'
                           ]

        self.__allowedSfTags = ['_Sample.Sf_category',
                                '_Sample.Sf_framecode',
                                '_Sample.Entry_ID',
                                '_Sample.Sf_ID',
                                '_Sample.ID',
                                '_Sample.Name',
                                '_Sample.Type',
                                '_Sample.Sub_type',
                                '_Sample.Details',
                                '_Sample.Aggregate_sample_number',
                                '_Sample.Solvent_system',
                                '_Sample.Preparation_date',
                                '_Sample.Preparation_expiration_date',
                                '_Sample.Polycrystallization_protocol',
                                '_Sample.Single_crystal_protocol',
                                '_Sample.Crystal_grow_apparatus',
                                '_Sample.Crystal_grow_atmosphere',
                                '_Sample.Crystal_grow_details',
                                '_Sample.Crystal_grow_method',
                                '_Sample.Crystal_grow_method_cit_ID',
                                '_Sample.Crystal_grow_pH',
                                '_Sample.Crystal_grow_pH_range',
                                '_Sample.Crystal_grow_pressure',
                                '_Sample.Crystal_grow_pressure_esd',
                                '_Sample.Crystal_grow_seeding',
                                '_Sample.Crystal_grow_seeding_cit_ID',
                                '_Sample.Crystal_grow_temp',
                                '_Sample.Crystal_grow_temp_details',
                                '_Sample.Crystal_grow_temp_esd',
                                '_Sample.Crystal_grow_time',
                                '_Sample.Oriented_sample_prep_protocol',
                                '_Sample.Lyophilization_cryo_protectant',
                                '_Sample.Storage_protocol',
                                '_Sample_condition_list.Sf_category',
                                '_Sample_condition_list.Sf_framecode',
                                '_Sample_condition_list.Entry_ID',
                                '_Sample_condition_list.Sf_ID',
                                '_Sample_condition_list.ID',
                                '_Sample_condition_list.Name',
                                '_Sample_condition_list.Details',
                                '_NMR_spectrometer_list.Sf_category',
                                '_NMR_spectrometer_list.Sf_framecode',
                                '_NMR_spectrometer_list.Entry_ID',
                                '_NMR_spectrometer_list.Sf_ID',
                                '_NMR_spectrometer_list.ID',
                                '_NMR_spectrometer_list.Name',
                                '_NMR_spectrometer.Sf_category',
                                '_NMR_spectrometer.Sf_framecode',
                                '_NMR_spectrometer.Entry_ID',
                                '_NMR_spectrometer.Sf_ID',
                                '_NMR_spectrometer.ID',
                                '_NMR_spectrometer.Name',
                                '_NMR_spectrometer.Details',
                                '_NMR_spectrometer.Manufacturer',
                                '_NMR_spectrometer.Model',
                                '_NMR_spectrometer.Serial_number',
                                '_NMR_spectrometer.Field_strength',
                                '_Experiment_list.Sf_category',
                                '_Experiment_list.Sf_framecode',
                                '_Experiment_list.Entry_ID',
                                '_Experiment_list.Sf_ID',
                                '_Experiment_list.ID',
                                '_Experiment_list.Details',
                                '_Software.Sf_category',
                                '_Software.Sf_framecode',
                                '_Software.Entry_ID',
                                '_Software.Sf_ID',
                                '_Software.ID',
                                '_Software.Type',
                                '_Software.Name',
                                '_Software.Version',
                                '_Software.DOI',
                                '_Software.Details',
                                '_Chem_shift_reference.Sf_category',
                                '_Chem_shift_reference.Sf_framecode',
                                '_Chem_shift_reference.Entry_ID',
                                '_Chem_shift_reference.Sf_ID',
                                '_Chem_shift_reference.ID',
                                '_Chem_shift_reference.Name',
                                '_Chem_shift_reference.Proton_shifts_flag',
                                '_Chem_shift_reference.Carbon_shifts_flag',
                                '_Chem_shift_reference.Nitrogen_shifts_flag',
                                '_Chem_shift_reference.Phosphorus_shifts_flag',
                                '_Chem_shift_reference.Other_shifts_flag',
                                '_Chem_shift_reference.Details',
                                '_Assigned_chem_shift_list.Sf_category',
                                '_Assigned_chem_shift_list.Sf_framecode',
                                '_Assigned_chem_shift_list.Entry_ID',
                                '_Assigned_chem_shift_list.Sf_ID',
                                '_Assigned_chem_shift_list.ID',
                                '_Assigned_chem_shift_list.Name',
                                '_Assigned_chem_shift_list.Data_file_name',
                                '_Assigned_chem_shift_list.Sample_condition_list_ID',
                                '_Assigned_chem_shift_list.Sample_condition_list_label',
                                '_Assigned_chem_shift_list.Chem_shift_reference_ID',
                                '_Assigned_chem_shift_list.Chem_shift_reference_label',
                                '_Assigned_chem_shift_list.Chem_shift_1H_err',
                                '_Assigned_chem_shift_list.Chem_shift_13C_err',
                                '_Assigned_chem_shift_list.Chem_shift_15N_err',
                                '_Assigned_chem_shift_list.Chem_shift_31P_err',
                                '_Assigned_chem_shift_list.Chem_shift_2H_err',
                                '_Assigned_chem_shift_list.Chem_shift_19F_err',
                                '_Assigned_chem_shift_list.Error_derivation_method',
                                '_Assigned_chem_shift_list.Details',
                                '_Assigned_chem_shift_list.Text_data_format',
                                '_Assigned_chem_shift_list.Text_data',
                                '_Constraint_stat_list.Sf_category',
                                '_Constraint_stat_list.Sf_framecode',
                                '_Constraint_stat_list.Entry_ID',
                                '_Constraint_stat_list.Sf_ID',
                                '_Constraint_stat_list.ID',
                                '_Constraint_stat_list.Name',
                                '_Constraint_stat_list.Data_file_name',
                                '_Constraint_stat_list.Details',
                                '_Constraint_stat_list.Text_data_format',
                                '_Constraint_stat_list.Text_data',
                                '_Constraint_stat_list.Stats_not_available',
                                '_Constraint_stat_list.NOE_interproton_dist_evaluation',
                                '_Constraint_stat_list.NOE_pseudoatom_corrections',
                                '_Constraint_stat_list.NOE_dist_averaging_method',
                                '_Constraint_stat_list.ROE_interproton_dist_evaluation',
                                '_Constraint_stat_list.ROE_pseudoatom_corrections',
                                '_Constraint_stat_list.ROE_dist_averaging_method',
                                '_Constraint_stat_list.NOE_tot_num',
                                '_Constraint_stat_list.RDC_tot_num',
                                '_Constraint_stat_list.Dihedral_angle_tot_num',
                                '_Constraint_stat_list.Protein_dihedral_angle_tot_num',
                                '_Constraint_stat_list.NA_dihedral_angle_tot_num',
                                '_Constraint_stat_list.NOE_intraresidue_tot_num',
                                '_Constraint_stat_list.NOE_sequential_tot_num',
                                '_Constraint_stat_list.NOE_medium_range_tot_num',
                                '_Constraint_stat_list.NOE_long_range_tot_num',
                                '_Constraint_stat_list.NOE_unique_tot_num',
                                '_Constraint_stat_list.NOE_intraresidue_unique_tot_num',
                                '_Constraint_stat_list.NOE_sequential_unique_tot_num',
                                '_Constraint_stat_list.NOE_medium_range_unique_tot_num',
                                '_Constraint_stat_list.NOE_long_range_unique_tot_num',
                                '_Constraint_stat_list.NOE_unamb_intramol_tot_num',
                                '_Constraint_stat_list.NOE_unamb_intermol_tot_num',
                                '_Constraint_stat_list.NOE_ambig_intramol_tot_num',
                                '_Constraint_stat_list.NOE_ambig_intermol_tot_num',
                                '_Constraint_stat_list.NOE_interentity_tot_num',
                                '_Constraint_stat_list.NOE_other_tot_num',
                                '_Constraint_stat_list.ROE_tot_num',
                                '_Constraint_stat_list.ROE_intraresidue_tot_num',
                                '_Constraint_stat_list.ROE_sequential_tot_num',
                                '_Constraint_stat_list.ROE_medium_range_tot_num',
                                '_Constraint_stat_list.ROE_long_range_tot_num',
                                '_Constraint_stat_list.ROE_unambig_intramol_tot_num',
                                '_Constraint_stat_list.ROE_unambig_intermol_tot_num',
                                '_Constraint_stat_list.ROE_ambig_intramol_tot_num',
                                '_Constraint_stat_list.ROE_ambig_intermol_tot_num',
                                '_Constraint_stat_list.ROE_other_tot_num',
                                '_Constraint_stat_list.RDC_HH_tot_num',
                                '_Constraint_stat_list.RDC_HNC_tot_num',
                                '_Constraint_stat_list.RDC_NH_tot_num',
                                '_Constraint_stat_list.RDC_CC_tot_num',
                                '_Constraint_stat_list.RDC_CN_i_1_tot_num',
                                '_Constraint_stat_list.RDC_CAHA_tot_num',
                                '_Constraint_stat_list.RDC_HNHA_tot_num',
                                '_Constraint_stat_list.RDC_HNHA_i_1_tot_num',
                                '_Constraint_stat_list.RDC_CAC_tot_num',
                                '_Constraint_stat_list.RDC_CAN_tot_num',
                                '_Constraint_stat_list.RDC_intraresidue_tot_num',
                                '_Constraint_stat_list.RDC_sequential_tot_num',
                                '_Constraint_stat_list.RDC_medium_range_tot_num',
                                '_Constraint_stat_list.RDC_long_range_tot_num',
                                '_Constraint_stat_list.RDC_other_tot_num',
                                '_Constraint_stat_list.RDC_unambig_intramol_tot_num',
                                '_Constraint_stat_list.RDC_unambig_intermol_tot_num',
                                '_Constraint_stat_list.RDC_ambig_intramol_tot_num',
                                '_Constraint_stat_list.RDC_ambig_intermol_tot_num',
                                '_Constraint_stat_list.RDC_intermol_tot_num',
                                '_Constraint_stat_list.Protein_phi_angle_tot_num',
                                '_Constraint_stat_list.Protein_psi_angle_tot_num',
                                '_Constraint_stat_list.Protein_chi_one_angle_tot_num',
                                '_Constraint_stat_list.Protein_other_angle_tot_num',
                                '_Constraint_stat_list.Protein_ambig_dihedral_tot_num',
                                '_Constraint_stat_list.Protein_other_tot_num',
                                '_Constraint_stat_list.NA_alpha_angle_tot_num',
                                '_Constraint_stat_list.NA_beta_angle_tot_num',
                                '_Constraint_stat_list.NA_gamma_angle_tot_num',
                                '_Constraint_stat_list.NA_delta_angle_tot_num',
                                '_Constraint_stat_list.NA_epsilon_angle_tot_num',
                                '_Constraint_stat_list.NA_chi_angle_tot_num',
                                '_Constraint_stat_list.NA_sugar_pucker_tot_num',
                                '_Constraint_stat_list.NA_other_angle_tot_num',
                                '_Constraint_stat_list.NA_amb_dihedral_angle_tot_num',
                                '_Constraint_stat_list.NA_other_tot_num',
                                '_Constraint_stat_list.H_bonds_constrained_tot_num',
                                '_Constraint_stat_list.Constr_def_H_bonds_tot_num',
                                '_Constraint_stat_list.SS_bonds_constrained_tot_num',
                                '_Constraint_stat_list.Constr_def_SS_bonds_tot_num',
                                '_Constraint_stat_list.Derived_coupling_const_tot_num',
                                '_Constraint_stat_list.Derived_CACB_chem_shift_tot_num',
                                '_Constraint_stat_list.Derived_1H_chem_shifts_tot_num',
                                '_Constraint_stat_list.Derived_photo_cidnps_tot_num',
                                '_Constraint_stat_list.Derived_paramag_relax_tot_num',
                                '_Constraint_stat_list.Assumed_distances_tot_num',
                                '_Constraint_stat_list.Assumed_angles_tot_num',
                                '_Constraint_stat_list.Constraints_per_residue_avg',
                                '_Constraint_stat_list.Constr_violations_per_residue_avg',
                                '_Constraint_stat_list.Dist_constr_violat_stat_calc_method',
                                '_Spectral_peak_list.Sf_category',
                                '_Spectral_peak_list.Sf_framecode',
                                '_Spectral_peak_list.Entry_ID',
                                '_Spectral_peak_list.Sf_ID',
                                '_Spectral_peak_list.ID',
                                '_Spectral_peak_list.Name',
                                '_Spectral_peak_list.Data_file_name',
                                '_Spectral_peak_list.Sample_ID',
                                '_Spectral_peak_list.Sample_label',
                                '_Spectral_peak_list.Sample_condition_list_ID',
                                '_Spectral_peak_list.Sample_condition_list_label',
                                '_Spectral_peak_list.Experiment_ID',
                                '_Spectral_peak_list.Experiment_name',
                                '_Spectral_peak_list.Experiment_class',
                                '_Spectral_peak_list.Experiment_type',
                                '_Spectral_peak_list.Number_of_spectral_dimensions',
                                '_Spectral_peak_list.Chemical_shift_list',
                                '_Spectral_peak_list.Assigned_chem_shift_list_ID',
                                '_Spectral_peak_list.Assigned_chem_shift_list_label',
                                '_Spectral_peak_list.Details',
                                '_Spectral_peak_list.Text_data_format',
                                '_Spectral_peak_list.Text_data',
                                '_Conformer_stat_list.Sf_category',
                                '_Conformer_stat_list.Sf_framecode',
                                '_Conformer_stat_list.Entry_ID',
                                '_Conformer_stat_list.Sf_ID',
                                '_Conformer_stat_list.ID',
                                '_Conformer_stat_list.Name',
                                '_Conformer_stat_list.Conformer_ensemble_only',
                                '_Conformer_stat_list.Both_ensemble_and_rep_conformer',
                                '_Conformer_stat_list.Representative_conformer_only',
                                '_Conformer_stat_list.Data_file_name',
                                '_Conformer_stat_list.Text_data_format',
                                '_Conformer_stat_list.Text_data',
                                '_Conformer_stat_list.Original_conformer_stats_file_ID',
                                '_Conformer_stat_list.Conf_family_coord_set_ID',
                                '_Conformer_stat_list.Conf_family_coord_set_label',
                                '_Conformer_stat_list.Representative_conformer_ID',
                                '_Conformer_stat_list.Representative_conformer_label',
                                '_Conformer_stat_list.Conformer_calculated_total_num',
                                '_Conformer_stat_list.Conformer_submitted_total_num',
                                '_Conformer_stat_list.Conformer_selection_criteria',
                                '_Conformer_stat_list.Representative_conformer',
                                '_Conformer_stat_list.Rep_conformer_selection_criteria',
                                '_Conformer_stat_list.Statistical_struct_param_details',
                                '_Conformer_stat_list.Details',
                                '_Conformer_family_coord_set.Sf_category',
                                '_Conformer_family_coord_set.Sf_framecode',
                                '_Conformer_family_coord_set.Entry_ID',
                                '_Conformer_family_coord_set.Sf_ID',
                                '_Conformer_family_coord_set.ID',
                                '_Conformer_family_coord_set.Name',
                                '_Conformer_family_coord_set.File_name',
                                '_Conformer_family_coord_set.Constraints_PDB_file_ID',
                                '_Conformer_family_coord_set.PDB_accession_code',
                                '_Conformer_family_coord_set.Sample_condition_list_ID',
                                '_Conformer_family_coord_set.Sample_condition_list_label',
                                '_Conformer_family_coord_set.Atom_site_uncertainty_desc',
                                '_Conformer_family_coord_set.Atom_site_ordered_flag_desc',
                                '_Conformer_family_coord_set.Details']

    # """
    # def load_csv_data(self, csv_file, transpose=False):
    #     """ Load CSV data to list.
    #         @param cvs_file: input CSV file path
    #         @param transpose: transpose CSV data
    #         @return: list object
    #     ""
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
    # """

    def merge(self, master_entry: pynmrstar.Entry, nmrif) -> bool:
        """ Merge NMRIF metadata to NMR-STAR.
        """

        if not isinstance(master_entry, pynmrstar.Entry):
            return False

        for page in self.__pages:

            for sf_category, sf_tag_prefix, new_flag in zip(self.__sfCategory[page], self.__sfTagPrefix[page], self.__sfNewFlag[page]):

                cif_categories = set(tag_map[0] for tag_map in self.__sfTagMap if tag_map[2] == sf_tag_prefix)
                if len(cif_categories) == 0:
                    if sf_category == 'NMR_spectrometer_list':
                        cif_categories = {'pdbx_nmr_spectrometer'}
                    elif sf_category == 'experiment_list':
                        cif_categories = {'pdbx_nmr_exptl'}
                    elif sf_category == 'conformer_family_coord_set':
                        cif_categories = {'pdbx_nmr_refine'}
                has_cif_category = False
                for cif_category in cif_categories:
                    if nmrif.hasCategory(cif_category) and nmrif.getRowLength(cif_category) > 0:
                        has_cif_category = True
                        break
                    if self.__verbose:
                        self.__lfh.write(f"+{self.__class_name__}.perform() ++ Warning  - {cif_category!r} saveframe category does not exist in NMRIF\n")
                if not has_cif_category:
                    continue

                if new_flag:
                    if sf_category in self.__sfCategoryList:
                        for sf in master_entry.get_saveframes_by_category(sf_category):
                            del master_entry[sf]

                elif sf_category not in self.__sfCategoryList:
                    if self.__verbose:
                        self.__lfh.write(f"+{self.__class_name__}.perform() ++ Warning  - {sf_category!r} category does not exist in NMR data\n")
                    continue

                sf_tag_maps = [tag_map for tag_map in self.__sfTagMap if tag_map[2] == sf_tag_prefix]
                sf_framecode_map = next((tag_map for tag_map in sf_tag_maps if tag_map[3] == 'Sf_framecode'), None)
                sf_id_map = next((tag_map for tag_map in sf_tag_maps if tag_map[3] == 'ID'), None)
                def_sf_tags = [tag.split('.')[1] for tag in self.__defSfTag if tag.split('.')[0] == sf_tag_prefix]

                sf_rows = {}
                for cif_category in cif_categories:
                    if nmrif.hasCategory(cif_category) and nmrif.getRowLength(cif_category) > 0:
                        sf_rows[cif_category] = nmrif.getDictList(cif_category)

                list_ids = []
                if sf_id_map is not None and sf_id_map[0] in sf_rows:
                    for row in sf_rows[sf_id_map[0]]:
                        if sf_id_map[1] in row and row[sf_id_map[1]].isdigit():
                            list_ids.append(int(row[sf_id_map[1]]))

                # map_code: '50' @see https://github.com/bmrb-io/onedep2bmrb/blob/master/pdbx2bmrb/convert.py#L202
                insert_one = sf_id_map is None or sf_id_map[4] == 50

                if len(list_ids) == 0:
                    if not insert_one:
                        if self.__verbose:
                            self.__lfh.write(f"+{self.__class_name__}.perform() ++ Warning  - {sf_id_map[0]}.{sf_id_map[1]} is not set in NMRIF\n")
                        continue
                    list_ids.append(1)

                list_ids = sorted(list_ids)

                # map_code: '5' @see https://github.com/bmrb-io/onedep2bmrb/blob/master/pdbx2bmrb/convert.py#L148
                list_id_dict = {list_id: order for order, list_id in enumerate(list_ids, 1)}
                sf_framecodes = []

                for list_id in list_ids:
                    reset = new_flag
                    has_uniq_sf_tag = False
                    sf = None

                    for cif_category, rows in sf_rows.items():

                        if sf_id_map is None or sf_id_map[0] == cif_category:

                            for row in rows:

                                if sf_id_map is None or (sf_id_map[1] in row and row[sf_id_map[1]] == str(list_id)):
                                    sf_name = sf_framecode = None
                                    if sf_framecode_map is not None and sf_framecode_map[1] in row:
                                        sf_name = sf_framecode = row[sf_framecode_map[1]]
                                        if sf_name is not None and sf_name.isdigit():
                                            sf_name = '?'
                                    try:
                                        master_entry.get_saveframe_by_name(sf_framecode)
                                        sf_framecode = f'{sf_category}_{list_id_dict[list_id]}'
                                    except KeyError:
                                        pass
                                    if sf_framecode in emptyValue or sf_framecode.isdigit() or sf_framecode in sf_framecodes or ' ' in sf_framecode:
                                        sf_framecode = f'{sf_category}_{list_id_dict[list_id]}'
                                    sf_framecodes.append(sf_framecode)
                                    if sf is None:

                                        if new_flag:
                                            sf = pynmrstar.Saveframe.from_scratch(sf_framecode, sf_tag_prefix)
                                            sf.add_tag('Sf_framecode', sf_framecode)
                                            sf.add_tag('Sf_category', sf_category)
                                            sf.add_tag('ID', str(list_id_dict[list_id]))
                                            if sf_name is not None and sf_name != sf_framecode:
                                                sf.add_tag('Name', sf_name)

                                        else:

                                            try:
                                                sf = master_entry.get_saveframe_by_name(sf_framecode)
                                                if sf.tag_prefix == sf_tag_prefix:
                                                    set_sf_tag(sf, 'ID', list_id_dict[list_id])
                                                else:
                                                    try:
                                                        sf = master_entry.get_saveframes_by_tag_and_value(f'{sf_tag_prefix}.ID', str(list_id))[0]
                                                        set_sf_tag(sf, 'ID', str(list_id))
                                                    except IndexError:
                                                        try:
                                                            sf = master_entry.get_saveframes_by_tag_and_value(f'{sf_tag_prefix}.ID', list_id)[0]
                                                            set_sf_tag(sf, 'ID', str(list_id))
                                                        except IndexError:
                                                            sf = None
                                            except KeyError:
                                                try:
                                                    sf = master_entry.get_saveframes_by_tag_and_value(f'{sf_tag_prefix}.ID', str(list_id_dict[list_id]))[0]
                                                    set_sf_tag(sf, 'ID', list_id_dict[list_id])
                                                except IndexError:
                                                    try:
                                                        sf = master_entry.get_saveframes_by_tag_and_value(f'{sf_tag_prefix}.ID', list_id_dict[list_id])[0]
                                                    except IndexError:
                                                        sf = pynmrstar.Saveframe.from_scratch(sf_framecode, sf_tag_prefix)
                                                        sf.add_tag('Sf_framecode', sf_framecode)
                                                        sf.add_tag('Sf_category', sf_category)
                                                        sf.add_tag('ID', str(list_id_dict[list_id]))
                                                        if sf_name is not None and sf_name != sf_framecode:
                                                            sf.add_tag('Name', sf_name)
                                                        reset = True

                                        set_sf_tag(sf, 'Entry_ID', self.__entryId)

                                    for tag_map in sf_tag_maps:
                                        if tag_map[0] == cif_category and tag_map[1] in row and tag_map[3] not in ('Sf_framecode', 'Sf_category', 'ID', 'Entry_ID'):
                                            if row[tag_map[1]] in emptyValue:
                                                _id = get_first_sf_tag(sf, tag_map[3])
                                                if isinstance(_id, int) or len(_id) > 0:
                                                    continue
                                            set_sf_tag(sf, tag_map[3], row[tag_map[1]])
                                            has_uniq_sf_tag = True

                                    if not has_uniq_sf_tag and reset:
                                        has_uniq_sf_tag = True

                                    for def_sf_tag in def_sf_tags:
                                        if def_sf_tag == 'Sf_framecode':
                                            continue
                                        if any(tag for tag in sf.tags if tag[0] == def_sf_tag):
                                            continue
                                        if not def_sf_tag.endswith('_label'):
                                            sf.add_tag(def_sf_tag, '.')
                                            continue
                                        parent_sf_tag_prefix = f'_{def_sf_tag[:-6]}'
                                        parent_list_id = get_first_sf_tag(sf, f'{parent_sf_tag_prefix[1:]}_ID')
                                        if parent_list_id in emptyValue:
                                            sf.add_tag(def_sf_tag, '.')
                                            continue
                                        try:
                                            parent_sf = master_entry.get_saveframes_by_tag_and_value(f'{parent_sf_tag_prefix}.ID', parent_list_id)[0]
                                            parent_sf_framecode = get_first_sf_tag(parent_sf, 'Sf_framecode')
                                            if len(parent_sf_framecode) > 0:
                                                sf.add_tag(def_sf_tag, f'${parent_sf_framecode}')
                                        except IndexError:
                                            try:
                                                parent_sf = master_entry.get_saveframes_by_tag_and_value(f'{parent_sf_tag_prefix}.ID', int(parent_list_id)
                                                                                                         if isinstance(parent_list_id, str) else str(parent_list_id))[0]
                                                parent_sf_framecode = get_first_sf_tag(parent_sf, 'Sf_framecode')
                                                if len(parent_sf_framecode) > 0:
                                                    sf.add_tag(def_sf_tag, f'${parent_sf_framecode}')
                                            except IndexError:
                                                sf.add_tag(def_sf_tag, '?')

                    if sf is None:
                        continue

                    # prevent duplication of spectral peak list
                    if sf_category == 'spectral_peak_list':
                        data_file_name = get_first_sf_tag(sf, 'Data_file_name')
                        if data_file_name not in emptyValue:
                            if len(master_entry.get_saveframes_by_tag_and_value('Data_file_name', data_file_name)) > 0:
                                sf = master_entry.get_saveframes_by_tag_and_value('Data_file_name', data_file_name)[0]
                                has_uniq_sf_tag = False
                            elif len(master_entry.get_saveframes_by_tag_and_value('Experiment_type', data_file_name)) > 0:
                                sf = master_entry.get_saveframes_by_tag_and_value('Experiment_type', data_file_name)[0]
                                has_uniq_sf_tag = False

                    if page not in self.__lpCategory or sf_tag_prefix not in self.__lpCategory[page]:
                        if reset and has_uniq_sf_tag:
                            master_entry.add_saveframe(sf)
                        else:
                            if self.__verbose:
                                self.__lfh.write(f"+{self.__class_name__}.perform() ++ Warning  - Could not identify loop category for {sf_category!r}\n")
                        continue

                    if reset and has_uniq_sf_tag:
                        master_entry.add_saveframe(sf)

                    for lp_category, new_flag in zip(self.__lpCategory[page][sf_tag_prefix], self.__lpNewFlag[page][sf_tag_prefix]):
                        reset = new_flag
                        lp = None

                        cif_categories = set(tag_map[0] for tag_map in self.__lpTagMap if tag_map[2] == lp_category)
                        lp_tag_dict = {tag_map[3]: (tag_map[1], tag_map[4]) for tag_map in self.__lpTagMap if tag_map[2] == lp_category and tag_map[4] != -33}
                        if 'Entry_ID' not in lp_tag_dict.keys():
                            lp_tag_dict['Entry_ID'] = (None, None)
                        lp_tags = list(lp_tag_dict.keys())

                        for cif_category in cif_categories:
                            if not nmrif.hasCategory(cif_category) or nmrif.getRowLength(cif_category) == 0:
                                if self.__verbose:
                                    self.__lfh.write(f"+{self.__class_name__}.perform() ++ Warning  - {cif_category!r} loop category does not exist in NMRIF\n")

                        list_id_tag = f'{sf_tag_prefix[1:]}_ID'
                        lp_list_id_tag = lp_tag_dict[list_id_tag][0] if list_id_tag in lp_tag_dict else None
                        def_lp_tags = [tag.split('.')[1] for tag in self.__defLpTag if tag.split('.')[0] == lp_category]
                        has_id_tag = 'ID' in lp_tag_dict
                        need_processing = any(map_code == -22 for cif_tag, map_code in lp_tag_dict.values()
                                              if cif_tag is not None and not cif_tag.endswith('range'))

                        lp_rows = {}
                        for cif_category in cif_categories:
                            if nmrif.hasCategory(cif_category) and nmrif.getRowLength(cif_category) > 0:
                                lp_rows[cif_category] = nmrif.getDictList(cif_category)

                        for cif_category, rows in lp_rows.items():

                            for row in rows:

                                if lp_list_id_tag is None or (lp_list_id_tag in row and row[lp_list_id_tag] == str(list_id)):

                                    if lp is None:

                                        if new_flag:
                                            lp = pynmrstar.Loop.from_scratch(lp_category)
                                            lp.add_tag(lp_tags)

                                            for def_lp_tag in def_lp_tags:
                                                if def_lp_tag not in lp.tags:
                                                    lp.add_tag(def_lp_tag)

                                        else:

                                            try:
                                                lp = sf.get_loop(lp_category)
                                                for tag in lp_tags:
                                                    if tag not in lp.tags:
                                                        lp.add_tag(tag)
                                                        for _row in lp.data:
                                                            _row.append('.' if tag != 'Entry_ID' else self.__entryId)

                                                for def_lp_tag in def_lp_tags:
                                                    if def_lp_tag not in lp.tags:
                                                        lp.add_tag(def_lp_tag)
                                                        for _row in lp.data:
                                                            _row.append('.')

                                            except KeyError:
                                                lp = pynmrstar.Loop.from_scratch(lp_category)
                                                lp.add_tag(lp_tags)

                                                for def_lp_tag in def_lp_tags:
                                                    if def_lp_tag not in lp.tags:
                                                        lp.add_tag(def_lp_tag)

                                                reset = True

                                    has_uniq_lp_row = False

                                    if need_processing:
                                        lp_list_id_col = -1 if list_id_tag not in lp.tags else lp.tags.index(list_id_tag)
                                        entry_id_col = -1 if 'Entry_ID' not in lp.tags else lp.tags.index('Entry_ID')
                                        type_col = -1 if 'Type' not in lp.tags else lp.tags.index('Type')
                                        val_col = -1 if 'Val' not in lp.tags else lp.tags.index('Val')
                                        val_err_col = -1 if 'Val_err' not in lp.tags else lp.tags.index('Val_err')
                                        val_units_col = -1 if 'Val_units' not in lp.tags else lp.tags.index('Val_units')

                                        for _type in ['ionic_strength', 'pH', 'pressure', 'temperature']:
                                            if _type in row:
                                                _val = row[_type]
                                                if _val in emptyValue:
                                                    continue
                                                _row = [None] * len(lp.tags)
                                                if lp_list_id_col != -1:
                                                    _row[lp_list_id_col] = str(list_id_dict[list_id])
                                                if entry_id_col != -1:
                                                    _row[entry_id_col] = self.__entryId
                                                if type_col != -1:
                                                    _row[type_col] = _type.replace('_', ' ')  # ionic_strength (NMRIF) -> ionic strength (NMR-STAR)
                                                if val_col != -1:
                                                    _row[val_col] = _val
                                                if val_err_col != -1 and f'{_type}_err' in row:
                                                    _row[val_err_col] = row[f'{_type}_err']
                                                if val_units_col != -1 and f'{_type}_units' in row:
                                                    _row[val_units_col] = row[f'{_type}_units']
                                                has_uniq_lp_row = True
                                                lp.add_data(_row)

                                    else:

                                        if reset:
                                            _row = [None] * len(lp.tags)

                                        elif has_id_tag:
                                            cif_id_tag = lp_tag_dict['ID'][0]
                                            id_col = lp.tags.index('ID')

                                        for tag, (cif_tag, map_code) in lp_tag_dict.items():

                                            if reset:
                                                if tag == list_id_tag:
                                                    col = lp.tags.index(list_id_tag)
                                                    _row[col] = str(list_id_dict[list_id])
                                                elif tag == 'Enry_ID':
                                                    col = lp.tags.index('Entry_ID')
                                                    _row[col] = self.__entryId
                                                elif cif_tag in row:
                                                    col = lp.tags.index(tag)
                                                    if map_code != -22:
                                                        _row[col] = row[cif_tag]
                                                        has_uniq_lp_row = True
                                                    else:  # map_code: '-22' @see https://github.com/bmrb-io/onedep2bmrb/blob/master/pdbx2bmrb/convert.py#L239
                                                        if cif_tag.endswith('range'):
                                                            if row[cif_tag] not in emptyValue:
                                                                try:
                                                                    g = range_value_pattern.search(row[cif_tag]).groups()
                                                                    if tag.endswith('max'):
                                                                        _max = g[1]
                                                                        try:
                                                                            __max = max(float(g[0]), float(g[1]))
                                                                            if float(_max) < __max:
                                                                                _max = g[0]
                                                                        except ValueError:
                                                                            pass
                                                                        _row[col] = _max
                                                                    elif tag.endswith('min'):
                                                                        _min = g[0]
                                                                        try:
                                                                            __min = min(float(g[0]), float(g[1]))
                                                                            if float(_min) > __min:
                                                                                _min = g[1]
                                                                        except ValueError:
                                                                            pass
                                                                        _row[col] = _min
                                                                except AttributeError:
                                                                    continue
                                                                has_uniq_lp_row = True

                                            elif has_id_tag:
                                                _row = next((_row for _row in lp.data if _row[id_col] == row[cif_id_tag]), None)

                                                if _row is None or tag == 'ID':
                                                    continue

                                                if tag == list_id_tag:
                                                    col = lp.tags.index(list_id_tag)
                                                    _row[col] = str(list_id_dict[list_id])
                                                elif tag == 'Enry_ID':
                                                    col = lp.tags.index('Entry_ID')
                                                    _row[col] = self.__entryId
                                                elif cif_tag in row:
                                                    col = lp.tags.index(tag)
                                                    if map_code != -22:
                                                        _row[col] = row[cif_tag]
                                                    else:  # map_code: '-22' @see https://github.com/bmrb-io/onedep2bmrb/blob/master/pdbx2bmrb/convert.py#L239
                                                        if cif_tag.endswith('range'):
                                                            if row[cif_tag] not in emptyValue:
                                                                try:
                                                                    g = range_value_pattern.search(row[cif_tag]).groups()
                                                                    if tag.endswith('max'):
                                                                        _max = g[1]
                                                                        try:
                                                                            __max = max(float(g[0]), float(g[1]))
                                                                            if float(_max) < __max:
                                                                                _max = g[0]
                                                                        except ValueError:
                                                                            pass
                                                                        _row[col] = _max
                                                                    elif tag.endswith('min'):
                                                                        _min = g[0]
                                                                        try:
                                                                            __min = min(float(g[0]), float(g[1]))
                                                                            if float(_min) > __min:
                                                                                _min = g[1]
                                                                        except ValueError:
                                                                            pass
                                                                        _row[col] = _min
                                                                except AttributeError:
                                                                    continue

                                    if reset and has_uniq_lp_row and not need_processing:

                                        # _NMR_spectrometer_view.NMR_spectrometer_list_ID, _Experiment.Experiment_list_ID
                                        if list_id_tag in lp.tags:
                                            lp_list_id_col = lp.tags.index(list_id_tag)
                                            if _row[lp_list_id_col] in emptyValue:
                                                _row[lp_list_id_col] = str(list_id_dict[list_id])

                                        lp.add_data(_row)

                            if reset and lp is not None and len(lp) > 0:

                                try:

                                    loop = sf.get_loop(lp_category)

                                    del sf[loop]

                                except KeyError:
                                    pass

                                sf.add_loop(lp)

        # synchronize software
        cif_category = 'pdbx_nmr_software'
        if nmrif.hasCategory(cif_category) and nmrif.getRowLength(cif_category) > 0:
            attrs = nmrif.getAttributeList(cif_category)
            if 'ordinal' in attrs and 'name' in attrs:
                ordinal_col = attrs.index('ordinal')
                name_col = attrs.index('name')
                data = nmrif.getRowList(cif_category)
                sorted_ord = sorted([int(row[ordinal_col]) for row in data])
                sw_ord_to_id = {str(_ord): str(_id) for _id, _ord in enumerate(sorted_ord, start=1)}
                sw_name_to_id = {}
                for row in data:
                    _ord = row[ordinal_col]
                    _name = row[name_col]
                    if _name not in sw_name_to_id:
                        sw_name_to_id[_name] = sw_ord_to_id[_ord]

                for lp in master_entry.get_loops_by_category('_Chem_shift_software'):
                    if 'Software_ID' in lp.tags:
                        sw_id_col = lp.tags.index('Software_ID')
                        for idx, row in enumerate(lp):
                            sw_id = row[sw_id_col]
                            if sw_id in emptyValue:
                                continue
                            if isinstance(sw_id, int):
                                sw_id = str(sw_id)
                            if sw_id not in sw_ord_to_id.values() and sw_id in sw_ord_to_id:
                                lp.data[idx][sw_id_col] = sw_ord_to_id[sw_id]

                for lp in master_entry.get_loops_by_category('_Conformer_family_refinement'):
                    if 'Software_ID' in lp.tags:
                        sw_id_col = lp.tags.index('Software_ID')
                        for idx, row in enumerate(lp):
                            sw_id = row[sw_id_col]
                            if sw_id in emptyValue:
                                continue
                            if isinstance(sw_id, int):
                                sw_id = str(sw_id)
                            if sw_id not in sw_ord_to_id.values() and sw_id in sw_ord_to_id:
                                lp.data[idx][sw_id_col] = sw_ord_to_id[sw_id]

                for lp in master_entry.get_loops_by_category('_Constraint_file'):
                    if 'Software_ID' in lp.tags and 'Software_name' in lp.tags:
                        sw_id_col = lp.tags.index('Software_ID')
                        sw_name_col = lp.tags.index('Software_name')
                        for idx, row in enumerate(lp):
                            sw_id = row[sw_id_col]
                            sw_name = row[sw_name_col]
                            if sw_name in emptyValue:
                                continue
                            if isinstance(sw_id, int):
                                sw_id = str(sw_id)
                            if sw_name in sw_name_to_id:
                                _sw_id = sw_name_to_id[sw_name]
                                if sw_id != _sw_id:
                                    parent_sf = master_entry.get_saveframes_by_tag_and_value('_Software.ID', sw_id)
                                    if len(parent_sf) > 0 and get_first_sf_tag(parent_sf[0], 'Name') == sw_name:
                                        continue
                                    lp.data[idx][sw_id_col] = _sw_id
                            elif '/' in sw_name:
                                for _sw_name in sw_name.split('/'):
                                    if _sw_name in sw_name_to_id:
                                        _sw_id = sw_name_to_id[_sw_name]
                                        lp.data[idx][sw_id_col] = _sw_id
                                        lp.data[idx][sw_name_col] = _sw_name
                                        break

        # resolve through-space?
        pk_list_sf_category = 'spectral_peak_list'
        exp_list_sf_category = 'experiment_list'
        if pk_list_sf_category in self.__sfCategoryList and exp_list_sf_category in self.__sfCategoryList:
            exp_list_sf = master_entry.get_saveframes_by_category(exp_list_sf_category)[0]
            exp_lp_category = '_Experiment'
            try:
                exp_lp = exp_list_sf.get_loop(exp_lp_category)
            except KeyError:
                exp_lp = None
            if exp_lp is not None:
                exp_tags = ['ID', 'Name']
                if set(exp_tags) & set(exp_lp.tags) == set(exp_tags):
                    exp_dict = {int(row[0]) if isinstance(row[0], str) else row[0]: row[1]
                                for row in exp_lp.get_tag(exp_tags)}

                    for sf in master_entry.get_saveframes_by_category(pk_list_sf_category):
                        exp_id = get_first_sf_tag(sf, 'Experiment_ID')
                        if exp_id in emptyValue:
                            continue
                        if isinstance(exp_id, str):
                            exp_id = int(exp_id)
                        if exp_id not in exp_dict:
                            continue
                        exp_class = _exp_class = get_first_sf_tag(sf, 'Experiment_class')
                        if not exp_class.endswith('through-space?'):
                            continue
                        exp_name = exp_dict[exp_id].lower()
                        if 'noe' in exp_name or 'roe' in exp_name\
                           or 'rfdr' in exp_name or 'darr' in exp_name or 'redor' in exp_name:
                            _exp_class = 'through-space'
                        elif 'tocsy' in exp_name:
                            _exp_class = 'relayed'
                        elif 'copy' in exp_name:
                            _exp_class = 'jcoupling'
                        if exp_class != _exp_class:
                            set_sf_tag(sf, 'Experiment_class', exp_class[:-14] + _exp_class)
                            try:
                                lp = sf.get_loop('_Spectral_dim_transfer')
                                type_col = lp.tags.index('Type')
                                for idx, row in enumerate(lp):
                                    if row[type_col] == 'through-space?':
                                        lp.data[idx][type_col] = _exp_class
                            except KeyError:
                                pass

        allowed_sf_tags = set(self.__allowedSfTags)

        for page in self.__pages:

            for sf_category, sf_tag_prefix in zip(self.__sfCategory[page], self.__sfTagPrefix[page]):

                for sf in master_entry.get_saveframes_by_category(sf_category):
                    sf_tags = set(f'{sf_tag_prefix}.{tag[0]}' for tag in sf.tags)

                    extra_sf_tags = list(set(sf_tags) - set(allowed_sf_tags))

                    if len(extra_sf_tags) > 0:
                        sf.remove_tag(extra_sf_tags)

        retrieve_symbolic_labels(master_entry)

        return True

    def extract(self, master_entry: pynmrstar.Entry, cR, file_path: str) -> bool:
        """ Extract NMRIF metadata from NMR-STAR (as primary source) and model (as secondary source).
        """

        def replace_none(array, default: str = '.'):
            for idx, val in enumerate(array):
                if val is None or val == 'None':
                    array[idx] = default
                elif not isinstance(val, str):
                    array[idx] = str(val)
            return array

        cifObj = mmCIFUtil(self.__verbose, self.__lfh)

        cifObj.addDataBlock(self.__entryId)

        if not isinstance(master_entry, pynmrstar.Entry):

            if cR is None:
                return False

            for cif_category in self.__nmrIfCategories:

                if cR.hasCategory(cif_category):
                    row_list = cR.getRowList(cif_category)
                    if len(row_list) > 0:
                        item_tags = cR.getAttributeList(cif_category)
                        cifObj.addCategory(self.__entryId, cif_category, item_tags)
                        cifObj.appendRowList(self.__entryId, cif_category, row_list)

            try:
                cifObj.writeToFile(file_path)
            except Exception:
                return False

            return True

        for cif_category, (sf_category, sf_tag_prefix) in self.__uniqSfCatMap.items():

            if sf_category in self.__sfCategoryList:
                sf_tag_maps = [tag_map for tag_map in self.__uniqSfTagMap if tag_map[0] == cif_category and tag_map[2] == sf_tag_prefix]
                sf_tags = [tag_map[3] for tag_map in sf_tag_maps]
                sf_map_code = [tag_map[4] for tag_map in sf_tag_maps]
                has_id_tag = 'ID' in sf_tags
                has_uniq_sf_tags = not all(sf_tag in ('ID', 'Sf_framecode') for sf_tag in sf_tags)

                lp_categories, lp_cat_map = [], []
                for _cif_category, (_sf_tag_prefix, _lp_categories) in self.__uniqLpCatMap.items():
                    if _sf_tag_prefix == sf_tag_prefix:
                        lp_categories.extend(_lp_categories)
                        lp_cat_map.append((_cif_category, _lp_categories))

                sf_cif_tags = [tag_map[1] for tag_map in sf_tag_maps]

                sf_cif_category = cif_category

                if -11 not in sf_map_code:

                    if has_uniq_sf_tags:
                        cifObj.addCategory(self.__entryId, cif_category, sf_cif_tags)

                    for idx, sf in enumerate(master_entry.get_saveframes_by_category(sf_category), start=1):
                        tag_values = [get_first_sf_tag(sf, sf_tag, '?') for sf_tag in sf_tags]
                        list_id = idx
                        if has_id_tag:
                            tag_values[sf_tags.index('ID')] = list_id
                        if has_uniq_sf_tags:
                            tag_values = replace_none(tag_values, '?')
                            cifObj.appendRow(self.__entryId, sf_cif_category, tag_values)

                        if len(lp_cat_map) > 0:
                            list_id_tag = f'{sf_tag_prefix[1:]}_ID'

                            for cif_category, lp_categories in lp_cat_map:

                                if len(lp_categories) == 1:
                                    lp_category = lp_categories[0]

                                    try:
                                        lp = sf.get_loop(lp_category)
                                    except KeyError:
                                        continue

                                    lp_tag_maps = [tag_map for tag_map in self.__lpTagMap if tag_map[0] == cif_category and tag_map[2] == lp_category]
                                    lp_cif_tags = [tag_map[1] for tag_map in lp_tag_maps]
                                    lp_tags = [tag_map[3] for tag_map in lp_tag_maps]
                                    lp_map_codes = [tag_map[4] for tag_map in lp_tag_maps]
                                    lp_aux_tags = [tag_map[5] for tag_map in lp_tag_maps]
                                    has_list_id_tag = list_id_tag in lp_tags

                                    if -11 in lp_map_codes:
                                        continue

                                    if -22 not in lp_map_codes:

                                        if cif_category not in cifObj.getCategoryNameList(self.__entryId):
                                            cifObj.addCategory(self.__entryId, cif_category, lp_cif_tags)

                                        missing_lp_tags = set(lp_tags) - set(lp.tags)

                                        if len(missing_lp_tags) == 0:
                                            dat = lp.get_tag(lp_tags)

                                            for row in dat:
                                                for col, dst_val in enumerate(row):
                                                    if abs(lp_map_codes[col]) != 33:
                                                        continue
                                                    dst_tag = lp_tags[col].replace('_ID', '.ID', 1)  # Software_ID -> Software.ID
                                                    found = False
                                                    for _sf in master_entry.get_saveframes_by_tag_and_value(dst_tag, dst_val):
                                                        row[col] = _sf.get_tag(lp_aux_tags[col])[0]
                                                        found = True
                                                        break
                                                    if not found and isinstance(dst_val, int):
                                                        for _sf in master_entry.get_saveframes_by_tag_and_value(dst_tag, str(dst_val)):
                                                            row[col] = _sf.get_tag(lp_aux_tags[col])[0]
                                                            found = True
                                                    if found:
                                                        if lp_aux_tags[col] == '_Software.Name':
                                                            row[col] = get_nmr_software(row[col])
                                                    else:
                                                        row[col] = '?'
                                                _row = ['.'] * len(lp_cif_tags)
                                                for cif_item in lp_cif_tags:
                                                    tag_map = next(tag_map for tag_map in lp_tag_maps if tag_map[1] == cif_item)
                                                    if tag_map[3] not in lp_tags:
                                                        continue
                                                    _row[lp_cif_tags.index(tag_map[1])] = list_id if has_list_id_tag and tag_map[3] == list_id_tag\
                                                        else row[lp_tags.index(tag_map[3])]
                                                    if tag_map[4] == 33:
                                                        _tag_map = next((tag_map for tag_map in lp_tag_maps if tag_map[1] == cif_item and tag_map[4] == -33), None)
                                                        if _tag_map is not None:
                                                            _row[lp_cif_tags.index(tag_map[1])] = row[lp_tags.index(tag_map[3])]
                                                _row = replace_none(_row)
                                                cifObj.appendRow(self.__entryId, cif_category, _row)

                                        else:
                                            _lp_tags = [tag for tag in lp_tags if tag not in missing_lp_tags]
                                            _lp_map_codes = [next(tag_map[4] for tag_map in lp_tag_maps if tag_map[3] == tag) for tag in _lp_tags]
                                            _lp_aux_tags = [next(tag_map[5] for tag_map in lp_tag_maps if tag_map[3] == tag) for tag in _lp_tags]

                                            dat = lp.get_tag(_lp_tags)

                                            for row in dat:
                                                for col, dst_val in enumerate(row):
                                                    if abs(_lp_map_codes[col]) != 33:
                                                        continue
                                                    dst_tag = _lp_tags[col].replace('_ID', '.ID', 1)
                                                    found = False
                                                    for _sf in master_entry.get_saveframes_by_tag_and_value(dst_tag, dst_val):
                                                        row[col] = _sf.get_tag(_lp_aux_tags[col])[0]
                                                        found = True
                                                        break
                                                    if not found and isinstance(dst_val, int):
                                                        for _sf in master_entry.get_saveframes_by_tag_and_value(dst_tag, str(dst_val)):
                                                            row[col] = _sf.get_tag(_lp_aux_tags[col])[0]
                                                            found = True
                                                    if found:
                                                        if _lp_aux_tags[col] == '_Software.Name':
                                                            row[col] = get_nmr_software(row[col])
                                                    else:
                                                        row[col] = '?'
                                                _row = ['.'] * len(lp_cif_tags)
                                                for idx, cif_item in enumerate(lp_cif_tags):
                                                    tag_map = next(tag_map for tag_map in lp_tag_maps if tag_map[1] == cif_item)
                                                    if tag_map[3] not in _lp_tags:
                                                        continue
                                                    _row[lp_cif_tags.index(tag_map[1])] = list_id if has_list_id_tag and tag_map[3] == list_id_tag\
                                                        else row[_lp_tags.index(tag_map[3])]
                                                    if tag_map[4] == 33:
                                                        _tag_map = next((tag_map for tag_map in lp_tag_maps if tag_map[1] == cif_item and tag_map[4] == -33), None)
                                                        if _tag_map is not None:
                                                            _row[lp_cif_tags.index(tag_map[1])] = row[_lp_tags.index(tag_map[3])]
                                                _row = replace_none(_row)
                                                cifObj.appendRow(self.__entryId, cif_category, _row)

                                    elif any(cif_item.endswith('range') for cif_item in lp_cif_tags)\
                                            and any(lp_item.endswith('max') for lp_item in lp_tags)\
                                            and any(lp_item.endswith('min') for lp_item in lp_tags):

                                        lp_cif_tags = sorted(list(set(lp_cif_tags)))
                                        lp_tags = list(set(lp_tags))

                                        if cif_category not in cifObj.getCategoryNameList(self.__entryId):
                                            cifObj.addCategory(self.__entryId, cif_category, lp_cif_tags)

                                        missing_lp_tags = set(lp_tags) - set(lp.tags)

                                        _lp_tags = [tag for tag in lp_tags if tag not in missing_lp_tags]
                                        _lp_map_codes = [next(tag_map[4] for tag_map in lp_tag_maps if tag_map[3] == tag) for tag in _lp_tags]
                                        _lp_aux_tags = [next(tag_map[5] for tag_map in lp_tag_maps if tag_map[3] == tag) for tag in _lp_tags]

                                        dat = lp.get_tag(_lp_tags)

                                        for row in dat:
                                            for col, dst_val in enumerate(row):
                                                if abs(_lp_map_codes[col]) != 33:
                                                    continue
                                                dst_tag = _lp_tags[col].replace('_ID', '.ID', 1)
                                                found = False
                                                for _sf in master_entry.get_saveframes_by_tag_and_value(dst_tag, dst_val):
                                                    row[col] = _sf.get_tag(_lp_aux_tags[col])[0]
                                                    found = True
                                                    break
                                                if not found and isinstance(dst_val, int):
                                                    for _sf in master_entry.get_saveframes_by_tag_and_value(dst_tag, str(dst_val)):
                                                        row[col] = _sf.get_tag(_lp_aux_tags[col])[0]
                                                        found = True
                                                if found:
                                                    if _lp_aux_tags[col] == '_Software.Name':
                                                        row[col] = get_nmr_software(row[col])
                                                else:
                                                    row[col] = '?'
                                            _row = ['.'] * len(lp_cif_tags)
                                            for idx, cif_item in enumerate(lp_cif_tags):
                                                tag_map = next(tag_map for tag_map in lp_tag_maps if tag_map[1] == cif_item)
                                                if tag_map[3] not in _lp_tags:
                                                    continue
                                                if has_list_id_tag and tag_map[3] == list_id_tag:
                                                    _row[lp_cif_tags.index(tag_map[1])] = list_id
                                                if tag_map[4] == 33:
                                                    _tag_map = next((tag_map for tag_map in lp_tag_maps if tag_map[1] == cif_item and tag_map[4] == -33), None)
                                                    if _tag_map is not None:
                                                        _row[lp_cif_tags.index(_tag_map[1])] = row[_lp_tags.index(tag_map[3])]
                                                elif tag_map[4] != -22:
                                                    if tag_map[3] in _lp_tags:
                                                        _row[idx] = row[_lp_tags.index(tag_map[3])]
                                                elif cif_item.endswith('range'):
                                                    max_lp_item = next((lp_tag for lp_tag in _lp_tags if lp_tag.endswith('max')), None)
                                                    min_lp_item = next((lp_tag for lp_tag in _lp_tags if lp_tag.endswith('min')), None)
                                                    if None not in (max_lp_item, min_lp_item)\
                                                       and row[_lp_tags.index(max_lp_item)] not in emptyValue\
                                                       and row[_lp_tags.index(max_lp_item)] not in emptyValue:
                                                        _row[idx] = f'{row[_lp_tags.index(min_lp_item)]}-{row[_lp_tags.index(max_lp_item)]}'
                                            _row = replace_none(_row)
                                            cifObj.appendRow(self.__entryId, cif_category, _row)

                                    elif any(lp_item == 'Type' for lp_item in lp_tags) and any(lp_item == 'Val' for lp_item in lp_tags):

                                        lp_cif_tags = sorted(list(set(lp_cif_tags)))
                                        lp_tags = list(set(lp_tags))

                                        if cif_category not in cifObj.getCategoryNameList(self.__entryId):
                                            cifObj.addCategory(self.__entryId, cif_category, lp_cif_tags)

                                        missing_lp_tags = set(lp_tags) - set(lp.tags)

                                        _lp_tags = [tag for tag in lp_tags if tag not in missing_lp_tags]
                                        _lp_map_codes = [next(tag_map[4] for tag_map in lp_tag_maps if tag_map[3] == tag) for tag in _lp_tags]
                                        _lp_aux_tags = [next(tag_map[5] for tag_map in lp_tag_maps if tag_map[3] == tag) for tag in _lp_tags]

                                        dat = lp.get_tag(_lp_tags)

                                        row = ['.'] * len(lp_cif_tags)

                                        for _row in dat:
                                            for col, dst_val in enumerate(_row):
                                                if abs(_lp_map_codes[col]) != 33:
                                                    continue
                                                dst_tag = _lp_tags[col].replace('_ID', '.ID', 1)
                                                found = False
                                                for _sf in master_entry.get_saveframes_by_tag_and_value(dst_tag, dst_val):
                                                    _row[col] = _sf.get_tag(_lp_aux_tags[col])[0]
                                                    found = True
                                                    break
                                                if not found and isinstance(dst_val, int):
                                                    for _sf in master_entry.get_saveframes_by_tag_and_value(dst_tag, str(dst_val)):
                                                        _row[col] = _sf.get_tag(_lp_aux_tags[col])[0]
                                                        found = True
                                                if found:
                                                    if _lp_aux_tags[col] == '_Software.Name':
                                                        _row[col] = get_nmr_software(_row[col])
                                                else:
                                                    _row[col] = '?'
                                            _type = _row[_lp_tags.index('Type')]
                                            _val = _row[_lp_tags.index('Val')]
                                            _val_err = _val_units = '?'
                                            for idx, lp_tag in enumerate(_lp_tags):
                                                if lp_tag in ('Type', 'Val'):
                                                    pass
                                                elif lp_tag == 'Val_err':
                                                    _val_err = _row[_lp_tags.index('Val_err')]
                                                elif lp_tag == 'Val_units':
                                                    _val_units = _row[_lp_tags.index('Val_units')]
                                                else:
                                                    tag_map = next(tag_map for tag_map in lp_tag_maps if tag_map[3] == lp_tag)
                                                    row[lp_cif_tags.index(tag_map[1])] = list_id if lp_tag == list_id_tag else _row[lp_tags.index(lp_tag)]
                                                    if tag_map[4] == 33:
                                                        _tag_map = next((tag_map for tag_map in lp_tag_maps if tag_map[3] == lp_tag and tag_map[4] == -33), None)
                                                        if _tag_map is not None:
                                                            row[lp_cif_tags.index(_tag_map[1])] = _row[lp_tags.index(lp_tag)]

                                            if _type in ('ionic strength', 'pH', 'pressure', 'temperature'):
                                                if ' ' in _type:  # ionic strength (NMR-STAR) -> ionic_streandth (NMRIF)
                                                    _type = _type.replace(' ', '_')
                                                if _type in lp_cif_tags:
                                                    row[lp_cif_tags.index(_type)] = _val
                                                if f'{_type}_err' in lp_cif_tags:
                                                    row[lp_cif_tags.index(f'{_type}_err')] = _val_err
                                                if f'{_type}_units' in lp_cif_tags:
                                                    row[lp_cif_tags.index(f'{_type}_units')] = _val_units
                                        row = replace_none(row)
                                        cifObj.appendRow(self.__entryId, cif_category, row)

                                else:

                                    lps = [None] * len(lp_categories)
                                    lp_tag_maps = [None] * len(lp_categories)
                                    lp_cif_tags, lp_items, lp_map_codes = [], [], []

                                    for lp_idx, lp_category in enumerate(lp_categories):

                                        try:
                                            lps[lp_idx] = sf.get_loop(lp_category)
                                        except KeyError:
                                            continue

                                        lp_tag_maps[lp_idx] = [tag_map for tag_map in self.__lpTagMap if tag_map[0] == cif_category and tag_map[2] == lp_category]
                                        lp_tags[lp_idx] = [tag_map[3] for tag_map in lp_tag_maps[lp_idx]]
                                        if list_id_tag not in lp_tags[lp_idx]:
                                            lps[lp_idx] = None
                                            continue
                                        for tag_map in lp_tag_maps[lp_idx]:
                                            cif_item, lp_item, map_code = tag_map[1], tag_map[3], tag_map[4]
                                            if cif_item not in lp_cif_tags:
                                                lp_cif_tags.append(cif_item)
                                                lp_items.append(lp_item)
                                                lp_map_codes.append(map_code)

                                    if -11 in lp_map_codes:
                                        continue

                                    if len(lp_cif_tags) > 0:
                                        if cif_category not in cifObj.getCategoryNameList(self.__entryId):
                                            cifObj.addCategory(self.__entryId, cif_category, lp_cif_tags)

                                        row = ['.'] * len(lp_cif_tags)

                                        for lp_idx, lp in enumerate(lps):
                                            if lp is None:
                                                continue

                                            missing_lp_tags = set(lp_tags[lp_idx]) - set(lp.tags)

                                            if len(missing_lp_tags) == 0:
                                                _lp_tags = lp_tags[lp_idx]
                                                _lp_map_codes = [next(tag_map[4] for tag_map in lp_tag_maps[lp_idx] if tag_map[3] == tag) for tag in _lp_tags]
                                                _lp_aux_tags = [next(tag_map[5] for tag_map in lp_tag_maps[lp_idx] if tag_map[3] == tag) for tag in _lp_tags]

                                                dat = lp.get_tag(_lp_tags)

                                                for _row in dat:
                                                    for col, dst_val in enumerate(_row):
                                                        if abs(_lp_map_codes[col]) != 33:
                                                            continue
                                                        dst_tag = _lp_tags[col].replace('_ID', '.ID', 1)
                                                        found = False
                                                        for _sf in master_entry.get_saveframes_by_tag_and_value(dst_tag, dst_val):
                                                            _row[col] = _sf.get_tag(_lp_aux_tags[col])[0]
                                                            found = True
                                                            break
                                                        if not found and isinstance(dst_val, int):
                                                            for _sf in master_entry.get_saveframes_by_tag_and_value(dst_tag, str(dst_val)):
                                                                _row[col] = _sf.get_tag(_lp_aux_tags[col])[0]
                                                                found = True
                                                        if found:
                                                            if _lp_aux_tags[col] == '_Software.Name':
                                                                _row[col] = get_nmr_software(_row[col])
                                                        else:
                                                            _row[col] = '?'
                                                    for idx, lp_item in enumerate(_lp_tags):
                                                        tag_map = next(tag_map for tag_map in lp_tag_maps[lp_idx] if tag_map[3] == lp_item)
                                                        row[lp_items.index(lp_item)] = list_id if lp_item == list_id_tag else _row[idx]
                                                        if tag_map[4] == 33:
                                                            _tag_map = next((tag_map for tag_map in lp_tag_maps[lp_idx] if tag_map[3] == lp_item and tag_map[4] == -33), None)
                                                            if _tag_map is not None:
                                                                row[lp_cif_tags.index(_tag_map[1])] = _row[idx]
                                                    break

                                            else:
                                                _lp_tags = [tag for tag in lp_tags[lp_idx] if tag not in missing_lp_tags]
                                                _lp_map_codes = [next(tag_map[4] for tag_map in lp_tag_maps[lp_idx] if tag_map[3] == tag) for tag in _lp_tags]
                                                _lp_aux_tags = [next(tag_map[5] for tag_map in lp_tag_maps[lp_idx] if tag_map[3] == tag) for tag in _lp_tags]

                                                dat = lp.get_tag(_lp_tags)

                                                for _row in dat:
                                                    for col, dst_val in enumerate(_row):
                                                        if abs(_lp_map_codes[col]) != 33:
                                                            continue
                                                        dst_tag = _lp_tags[col].replace('_ID', '.ID', 1)
                                                        found = False
                                                        for _sf in master_entry.get_saveframes_by_tag_and_value(dst_tag, dst_val):
                                                            _row[col] = _sf.get_tag(_lp_aux_tags[col])[0]
                                                            found = True
                                                            break
                                                        if not found and isinstance(dst_val, int):
                                                            for _sf in master_entry.get_saveframes_by_tag_and_value(dst_tag, str(dst_val)):
                                                                _row[col] = _sf.get_tag(_lp_aux_tags[col])[0]
                                                                found = True
                                                        if found:
                                                            if _lp_aux_tags[col] == '_Software.Name':
                                                                _row[col] = get_nmr_software(_row[col])
                                                        else:
                                                            _row[col] = '?'
                                                    for idx, lp_item in enumerate(_lp_tags):
                                                        tag_map = next(tag_map for tag_map in lp_tag_maps[lp_idx] if tag_map[3] == lp_item)
                                                        row[lp_items.index(lp_item)] = list_id if lp_item == list_id_tag else _row[idx]
                                                        if tag_map[4] == 33:
                                                            _tag_map = next((tag_map for tag_map in lp_tag_maps[lp_idx] if tag_map[3] == lp_item and tag_map[4] == -33), None)
                                                            if _tag_map is not None:
                                                                row[lp_cif_tags.index(_tag_map[1])] = _row[idx]
                                                    break

                                        row = replace_none(row)
                                        cifObj.appendRow(self.__entryId, cif_category, row)

                else:

                    if len(lp_cat_map) == 0:

                        if has_uniq_sf_tags:

                            sf_cif_tags = [tag_map[1] for tag_map in sf_tag_maps]
                            cifObj.addCategory(self.__entryId, cif_category, sf_cif_tags)

                            for idx, sf in enumerate(master_entry.get_saveframes_by_category(sf_category), start=1):
                                tag_values = [get_first_sf_tag(sf, sf_tag, '?') for sf_tag in sf_tags]
                                list_id = idx
                                if has_id_tag:
                                    tag_values[sf_tags.index('ID')] = list_id
                                if sf_tag_prefix == '_Software' and 'Name' in sf_tags:
                                    tag_values[sf_tags.index('Name')] = get_nmr_software(tag_values[sf_tags.index('Name')])
                                tag_values = replace_none(tag_values, '?')
                                cifObj.appendRow(self.__entryId, sf_cif_category, tag_values)

                        continue

                    sf_lp_cif_tags = sf_cif_tags

                    for cif_category, lp_categories in lp_cat_map:

                        for lp_category in lp_categories:
                            lp_tag_maps = [tag_map for tag_map in self.__lpTagMap if tag_map[0] == cif_category and tag_map[2] == lp_category and tag_map[4] == -11]
                            lp_cif_tags = [tag_map[1] for tag_map in lp_tag_maps]
                            sf_lp_cif_tags.extend(lp_cif_tags)

                    cifObj.addCategory(self.__entryId, sf_cif_category, sf_lp_cif_tags)

                    for idx, sf in enumerate(master_entry.get_saveframes_by_category(sf_category), start=1):
                        tag_values = [get_first_sf_tag(sf, sf_tag, '?') for sf_tag in sf_tags]
                        list_id = idx
                        if has_id_tag:
                            tag_values[sf_tags.index('ID')] = list_id
                        if sf_tag_prefix == '_Software' and 'Name' in sf_tags:
                            tag_values[sf_tags.index('Name')] = get_nmr_software(tag_values[sf_tags.index('Name')])

                        _row = ['?'] * len(sf_lp_cif_tags)
                        for idx, tag_value in enumerate(tag_values):
                            _row[idx] = tag_value

                        for cif_category, lp_categories in lp_cat_map:

                            for lp_category in lp_categories:

                                try:
                                    lp = sf.get_loop(lp_category)
                                except KeyError:
                                    continue

                                lp_tag_maps = [tag_map for tag_map in self.__lpTagMap if tag_map[0] == cif_category and tag_map[2] == lp_category and tag_map[4] == -11]
                                lp_cif_tags = [tag_map[1] for tag_map in lp_tag_maps]
                                lp_tags = [tag_map[3] for tag_map in lp_tag_maps]

                                missing_lp_tags = set(lp_tags) - set(lp.tags)

                                _lp_tags = [tag for tag in lp_tags if tag not in missing_lp_tags]

                                dat = lp.get_tag(_lp_tags)

                                for row in dat:

                                    if len(_lp_tags) == 1:
                                        tag_map = next(tag_map for tag_map in lp_tag_maps if tag_map[3] == _lp_tags[0])
                                        _row[sf_lp_cif_tags.index(tag_map[1])] = row

                                    else:

                                        for idx, lp_item in enumerate(_lp_tags):
                                            tag_map = next(tag_map for tag_map in lp_tag_maps if tag_map[3] == lp_item)
                                            _row[sf_lp_cif_tags.index(tag_map[1])] = row[idx]

                                    break

                        _row = replace_none(_row, '?')
                        cifObj.appendRow(self.__entryId, sf_cif_category, _row)

        # merge categories of model file as secondary source of NMRIF
        if cR is not None:
            primary_categories = cifObj.getCategoryNameList(self.__entryId)
            secondary_categories = cR.getCategoryNameList()

            target_categories = []
            for cif_page in self.__cifPages:
                # safe merge
                if not any(cif_category in primary_categories for cif_category in self.__cifRequirements[cif_page]):
                    for cif_category in self.__cifRequirements[cif_page]:
                        if cif_category in secondary_categories and cif_category not in target_categories:
                            target_categories.append(cif_category)
                # unsafe merge (cherry picking because of cross-page category such as pdbx_nmr_software)
                else:
                    for cif_category in self.__cifRequirements[cif_page]:
                        if cif_category not in primary_categories and cif_category in secondary_categories\
                           and cif_category not in target_categories:
                            target_categories.append(cif_category)

            if len(target_categories) > 0:
                for cif_category in target_categories:
                    row_list = cR.getRowList(cif_category)
                    if len(row_list) > 0:
                        cifObj.addCategory(self.__entryId, cif_category, cR.getAttributeList(cif_category))
                        cifObj.appendRowList(self.__entryId, cif_category, row_list)

        try:
            cifObj.writeToFile(file_path)
        except Exception:
            return False

        return True


if __name__ == "__main__":
    ann = OneDepAnnTasks(False, sys.stderr, None, None)
