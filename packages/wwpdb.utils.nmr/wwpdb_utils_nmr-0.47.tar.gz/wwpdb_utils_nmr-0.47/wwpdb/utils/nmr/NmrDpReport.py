##
# File: NmrDpReport.py
# Date: 29-Jul-2019
#
# Updates:
# 09-Oct-2019  M. Yokochi - add setCorrectedError() to catch missing mandatory saveframe tag
# 10-Oct-2019  M. Yokochi - add 'enum_failure_ignorable' warning type
# 15-Oct-2019  M. Yokochi - add 'encouragement' waring type
# 27-Jan-2020  M. Yokochi - change warning type 'enum_failure' to 'enum_mismatch'
# 05-Feb-2020  M. Yokochi - move conflicted_data error to warning
# 10-Feb-2020  M. Yokochi - add methods to retrieve polymer sequence for sample sequence alignment
# 13-Feb-2020  M. Yokochi - add methods to retrieve content_subtype for apilayer.postModifyNMR
# 14-Feb-2020  M. Yokochi - add methods to pre-populate pdbx_nmr_spectral_peak_list, apilayer.postModifyNMRPeaks
# 21-Feb-2020  M. Yokochi - update content-type definitions
# 28-Feb-2020  M. Yokochi - add support for 'nmr-chemical-shifts' content type (DAOTHER-4515)
# 02-Mar-2020  M. Yokochi - add support for 'nmr-restraints' content type (DAOTHER-4515)
# 13-Mar-2020  M. Yokochi - change warning type from suspicious_data to anomalous_data
# 17-Mar-2020  M. Yokochi - remove irrelevant warning types in corrected_warning
# 18-Mar-2020  M. Yokochi - rename warning type from skipped_sf/lp_category to skipped_saveframe/loop_category
# 23-Mar-2020  M. Yokochi - add 'anomalous_chemical_shift' and 'unusual_chemical_shift' warning types
# 24-Mar-2020  M. Yokochi - add method to retrieve chemical shift reference (DAOTHER-1682)
# 03-Apr-2020  M. Yokochi - add methods to retrieve sequence alignment between coordinate and NMR data
# 15-Apr-2020  M. Yokochi - add getAverageRMSDWithinRange() (DAOTHER-4060)
# 18-Apr-2020  M. Yokochi - fix error of apilayer - getNmrSeqAlignment in NMR legacy deposition (DAOTHER-5594)
# 19-Apr-2020  M. Yokochi - support concatenated CS data in NMR legacy deposition (DAOTHER-5594)
# 19 Apr-2020  M. Yokochi - add 'not_superimposed_model' warning type (DAOTHER-4060)
# 20 Apr-2020  M. Yokochi - add 'concatenated_sequence' warning type (DAOTHER-5594)
# 22-Apr-2020  M. Yokochi - add 'ambiguity_code_mismatch' warning type (DAOTHER-5601)
# 25-Apr-2020  M. Yokochi - add 'entity' content subtype (DAOTHER-5611)
# 25-Apr-2020  M. Yokochi - add 'corrected_format_issue' warning type (DAOTHER-5611)
# 27-Apr-2020  M. Yokochi - add 'auth_atom_nomenclature_mismatch' warning type (DAOTHER-5611)
# 28-Apr-2020  M. Yokochi - prevent system clash due to 'number_of_assignments' (DAOTHER-5611)
# 28-Apr-2020  M. Yokochi - fix 'NOE? (To be decided)' to be 'NOE' (DAOTHER-5626)
# 29-Apr-2020  M. Yokochi - sort 'conflicted_data' and 'inconsistent_data' items (DAOTHER-5622)
# 13-May-2020  M. Yokochi - avoid system crash when format issue occurs (DAOTHER-5673)
# 15-May-2020  M. Yokochi - ignore 'disordered_index' warning (DAOTHER-5485)
# 15-May-2020  M. Yokochi - add 'content_mismatch' error for NMR legacy deposition (DAOTHER-5687)
# 12-Jun-2020  M. Yokochi - performance improvement by reusing cached data
# 25-Jun-2020  M. Yokochi - add 'anomalous_bond_length' warning
# 01-Jul-2020  M. Yokochi - suppress null error/warning in JSON report
# 09-Jul-2020  M. Yokochi - support spectral_peak_alt content subtype (DAOTHER-5926)
# 20-Nov-2020  M. Yokochi - rename 'remarkable_data' warning category to 'unusual/rare_data' (DAOTHER-6372)
# 27-Nov-2020  M. Yokochi - support grouped error/warning message (DAOTHER-6373)
# 17-Dec-2020  M. Yokochi - add 'atom_not_found' error (DAOTHER-6345)
# 21-Jan-2021  M. Yokochi - symptomatic treatment for DAOTHER-6509
# 03-Feb-2021  M. Yokochi - add support for 'identical_chain_id' attribute, which contains mapping of chain id(s), which shares the same entity.
# 30-Mar-2021  M. Yokochi - getNmrSeq1LetterCodeOf() and getModelSeq1LetterCodeOf() do not return any 3-letter code (DAOTHER-6744)
# 24-Jun-2021  M. Yokochi - resolve duplication in grouped error/warning message (DAOTHER-6345, 6830)
# 29-Jun-2021  M. Yokochi - enable to access NMR polymer sequence from auth_asym_id (DAOTHER-7108)
# 02-Jul-2021  M. Yokochi - add content types of NMR restraint file (DAOTHER-6830)
# 24-Aug-2021  M. Yokochi - add content subtype for XPLOR-NIH planarity restraints (DAOTHER-7265)
# 13-Oct-2021  M. Yokochi - code revision according to PEP8 using Pylint (DAOTHER-7389, issue #5)
# 14-Oct-2021  M. Yokochi - add 'incompletely_ssigned_chemical_shift' and 'incompletely_assigned_spectral_peak' (DAOTHER-7389, issue #3)
# 28-Oct-2021  M. Yokochi - add 'corrected_saveframe_name' warning (DAOTHER-7389, issue #4)
# 16-Nov-2021  M. Yokochi - revised error message for malformed XPLOR-NIH RDC restraints (DAOTHER-7478)
# 18-Nov-2021  M. Yokochi - detect content type of XPLOR-NIH hydrogen bond geometry restraints (DAOTHER-7478)
# 21 Dec-2021  M. Yokochi - add 'exactly_overlaid_model' warning type (DAOTHER-7544)
# 27-Jan-2022  M. Yokochi - add restraint types described by XPLOR-NIH, CNS, CYANA, and AMBER systems (NMR restraint remediation)
# 22 Feb-2022  M. Yokochi - add 'complemented_chemical_shift' warning type (DAOTHER-7681, issue #1)
# 04-Mar-2022  M. Yokochi - add coordinate geometry restraints (DAOTHER-7690, NMR restraint remediation)
# 22-Mar-2022  M. Yokochi - add 'nm-res-ros' file type for ROSETTA restraint format (DAOTHER-7690)
# 23-Mar-2022  M. Yokochi - add 'conflicted_mr_data', 'inconsistent_mr_data', 'redundant_mr_data', 'unsupported_mr_data' warning types (DAOTHER-7690)
# 13-Apr-2022  M. Yokochi - add 'label_scheme' option to select label_*_id or auth_*_id scheme of the coordinate file (NMR restraint remediation)
# 14 Apr-2022  M. Yokochi - add 'nm-res-mr' file type for NMR restraint remediation and V5.13
# 17-May-2022  M. Yokochi - add 'nm-res-bio' file type for BIOSYM restraint format (DAOTHER-7825, NMR restraint remediation)
# 01-Jun-2022  M. Yokochi - add 'nm-res-gro' and 'nm-aux-gro' file types for GROMACS restraint format (DAOTHER-7769, NMR restraint remediation)
# 17-Jun-2022  M. Yokochi - add 'nm-res-dyn' file type for DYNAMO/PALES/TALOS restraint format (DAOTHER-7872, NMR restraint remediation)
# 29-Jun-2022  M. Yokochi - add 'insufficient_mr_data' warning type (NMR restraint remediation)
# 06-Jul-2022  M. Yokochi - add 'nm-res-syb' file type for SYBYL restraint format (DAOTHER-7902, NMR restraint remediation)
# 07-Jul-2022  M. Yokochi - add 'nmr-peaks' content type and 'nm-pea-any' file type (NMR restraint remediation)
# 08-Jul-2022  M. Yokochi - add 'anomalous_rdc_vector' warning type for artificial RDCs for protein fibrils using solid-state NMR (NMR restraint remediation, 5w3n)
# 31-Aug-2022  M. Yokochi - separate atom_not_found error and hydrogen_not_instantiated error (NMR restraint remediation)
# 06-Sep-2022  M. Yokochi - add support for branched entity and extra restraints in NMR-STAR format (NMR restraint remediation)
# 13-Sep-2022  M. Yokochi - add 'nm-res-isd' file type for IDS (inference structure determination) restraint format (DAOTHER-8059, NMR restraint remediation)
# 22-Sep-2022  M. Yokochi - add 'nm-res-cha' file type for CHARMM restraint format (DAOTHER-8058, NMR restraint remediation)
# 24-Oct-2022  M. Yokochi - add support for floating chiral stereo assignments (NMR restraint remediation)
# 13-Jan-2023  M. Yokochi - add support for small angle X-ray scattering restraints (NMR restraint remediation)
# 24-Jan-2023  M. Yokochi - add support for heteronuclear relaxation data (NOE, T1, T2, T1rho, Order parameter) (NMR restraint remediation)
# 27-Feb-2023  M. Yokochi - add getLabelSeqSchemOf(), which convert author sequence scheme to label sequence scheme of the coordinates (NMR restraint remediation)
# 13-Dec-2023  M. Yokochi - add 'hydrogen_non_instantiated' warning (DAOTHER-8945)
# 12-Jan-2024  M. Yokochi - getNmrSeq1LetterCodeOf() returns '.' for missing residue, instead of whitespace (DAOTHER-9065)
# 16-Jan-2024  M. Yokochi - add 'nm-res-ari' file type for ARIA restraint format (DAOTHER-9079, NMR restraint remediation)
# 17-Jan-2024  M. Yokochi - add 'coordinate_issue' error (DAOTHER-9084)
# 29-Jan-2024  M. Yokochi - add 'ambiguous_dihedral_angle' warning type (NMR restraint remediation, 6sy2)
# 21-Feb-2024  M. Yokochi - add support for discontinuous model_id (NMR restraint remediation, 2n6j)
# 01-May-2024  M. Yokochi - merge cs/mr sequence extensions containing unknown residues (e.g UNK, DN, N) if necessary (NMR restraint remediation, 6fw4)
# 07-Nov-2024  M. Yokochi - add 'nm-pea-ari', 'nm-pea-pip', 'nm-pea-vie', 'nm-pea-spa', 'nm-pea-top', 'nm-pea-xea', and 'nm-pea-xwi' file types for NMR spectral peak remediation
# 14-Nov-2024  M. Yokochi - add 'nm-aux-cha' file type for CHARMM extended CRD (CARD) file acting as CHARMM topology definition
# 19-Nov-2024  M. Yokochi - add support for pH titration data (NMR restraint remediation)
# 22-Nov-2024  M. Yokochi - add 'nm-res-noa' file type for CYANA NOA (NOE Assignment) file
# 05-Dec-2024  M. Yokochi - add 'nm-aux-xea' file type for XEASY PROT (Assignment) file (NMR restraint remediation)
# 16-Dec-2024  M. Yokochi - add 'nm-pea-vnm' file types for VNMR spectral peak list file (NMR restraint remediation)
# 31-Jan-2025  M. Yokochi - add 'coordinate_issue' and 'assigned_peak_atom_not_found' warning (DAOTHER-8905, 9785, NMR data remediation, standalone NMR data conversion service)
# 07-Feb-2025  M. Yokochi - add 'ignore_error' in NmrDpReportInputSource class (DAOTHER-8905)
# 18-Feb-2025  M. Yokochi - add 'nm-pea-pon' file type for PONDEROSA spectral peak list file (DAOTHER-8905, 9785, NMR data remediation)
# 26-Feb-2025  M. Yokochi - add 'nm-pea-ccp' file type for CCPN tabular spectral peak list file (DAOTHER-8905, 9785, NMR data remediation)
# 05-Mar-2025  M. Yokochi - add 'nm-pea-bar' file type for bare spectral peak list file (DAOTHER-8905, 9785, NMR data remediation)
# 06-Mar-2025  M. Yokochi - add support for coupling constant data (NMR data remediation Phase 2)
# 28-Mar-2025  M. Yokochi - add 'nm-pea-sps' file type for SPARKY's 'save' (aka. ornament) peak list file (DAOTHER-8905, 9785, NMR data remediation Phase 2)
# 09-Apr-2025  M. Yokochi - add 'nm-shi-ari', 'nm-shi-bar', 'nm-shi-gar', 'nm-shi-npi', 'nm-shi-pip', 'nm-shi-ppm', 'nm-shi-st2', and 'nm-shi-xea' file_types (v4.4.0, DAOTHER-9785)
# 23-Apr-2025  M. Yokochi - enable to inherit previous warnings/errors (DAOTHER-9785)
# 24-Apr-2025  M. Yokochi - add NmrDpReportOutputStatistics class for standalone NMR data conversion service (DAOTHER-9785)
# 25-Apr-2025  M. Yokochi - add 'unparsed_data' error to block conversion due to unparsed data with error in standalone NMR data conversion service (DAOTHER-9785)
# 28-May-2025  M. Yokochi - add 'conflicted_peak_list' and 'inconsistent_peak_list' warning types (DAOTHER-10010)
# 29-May-2025  M. Yokochi - add 'unsupported_peak_list' warning type (DAOTHER-10099)
# 06-Aug-2025  M. Yokochi - add 'nm-res-sch' file type for SCHRODINGER/ASL restraint format (DAOTHER-7902, 10172, NMR data remediation)
# 22-Aug-2025  M. Yokochi - add 'nm-pea-oli' file type for OLIVIA spectral peak list file (DAOTHER-8905, 9785)
# 22-Aug-2025  M. Yokochi - add 'nm-shi-oli' file type for OLIVIA spectral peak list file (DAOTHER-9785)
##
""" Wrapper class for NMR data processing report.
    @author: Masashi Yokochi
"""
__docformat__ = "restructuredtext en"
__author__ = "Masashi Yokochi"
__email__ = "yokochi@protein.osaka-u.ac.jp"
__license__ = "Apache License 2.0"
__version__ = "4.7.0"

import sys
import json
import copy
import re

from operator import itemgetter
from typing import Any, IO, List, Tuple, Optional

try:
    from wwpdb.utils.nmr.AlignUtil import (emptyValue,
                                           monDict3,
                                           unknownResidue,
                                           getPrettyJson)
    from wwpdb.utils.nmr.CifToNmrStar import get_value_safe
except ImportError:
    from nmr.AlignUtil import (emptyValue,
                               monDict3,
                               unknownResidue,
                               getPrettyJson)
    from nmr.CifToNmrStar import get_value_safe


class NmrDpReport:
    """ Wrapper class for data processing report of NMR data.
    """

    def __init__(self, verbose: bool = True, log: IO = sys.stdout):
        self.__class_name__ = self.__class__.__name__
        self.__version__ = __version__

        self.__verbose = verbose
        self.__lfh = log

        self.__immutable = False

        self.__report = {'information': {'input_sources': [],
                                         'sequence_alignments': None,
                                         'chain_assignments': None,
                                         'output_statistics': None,
                                         'diamagnetic': True,
                                         'disulfide_bond': False,
                                         'other_bond': False,
                                         'cyclic_polymer': False,
                                         'status': 'OK'
                                         },
                         'error': None,
                         'warning': None,
                         'corrected_warning': None
                         }

        self.status_codes = ('OK', 'Error', 'Warning')

        self.input_sources = [NmrDpReportInputSource(self.__verbose, self.__lfh)]
        self.sequence_alignment = NmrDpReportSequenceAlignment(self.__verbose, self.__lfh)
        self.chain_assignment = NmrDpReportChainAssignment(self.__verbose, self.__lfh)
        self.output_statistics = None
        self.error = NmrDpReportError(self.__verbose, self.__lfh)
        self.warning = NmrDpReportWarning(self.__verbose, self.__lfh)
        self.corrected_warning = None

    def appendInputSource(self):
        """ Append empty input source.
        """

        self.input_sources.append(NmrDpReportInputSource(self.__verbose, self.__lfh))

    def insertInputSource(self, index: int):
        """ Insert empty input source at a given index.
        """

        self.input_sources.insert(index, NmrDpReportInputSource(self.__verbose, self.__lfh))

    def isOk(self) -> bool:
        """ Return whether processing status is OK.
        """

        return self.__report['information']['status'] == 'OK'

    def isError(self) -> bool:
        """ Return whether processing status is Error.
        """

        return self.__report['information']['status'] == 'Error'

    def isDiamagnetic(self) -> bool:
        """ Return whether molecular assembly is diamagnetic.
        """

        return self.__report['information']['diamagnetic']

    def hasDisulfideBond(self) -> bool:
        """ Return whether molecular assembly has disulfide bond.
        """

        return self.__report['information']['disulfide_bond']

    def hasOtherBond(self) -> bool:
        """ Return whether molecular assembly has other bond.
        """

        return self.__report['information']['other_bond']

    def hasCyclicPolymer(self) -> bool:
        """ Return whether molecular assembly contains cyclic polymer.
        """

        return self.__report['information']['cyclic_polymer']

    def getInputSourceDict(self, src_id: int) -> Optional[dict]:
        """ Return input source dictionary of a given index.
            @return: input source of a given index, None otherwise
        """

        if src_id < 0 or src_id >= len(self.input_sources):
            return None

        return self.input_sources[src_id].get()

    def getInputSourceIdOfNmrData(self) -> int:
        """ Return input_source_id of NMR data file.
            @return: index of input source of NMR data file, -1 otherwise
        """

        for in_src in self.input_sources:
            if in_src.get()['content_type'] in ('nmr-data-nef', 'nmr-data-str'):
                return self.input_sources.index(in_src)

        return -1

    def getInputSourceIdsOfNmrLegacyData(self) -> List[int]:
        """ Return array of input_source_id of NMR legacy data file.
            @return: array of index of input source of NMR legacy data file, [] otherwise
        """

        return [self.input_sources.index(in_src) for in_src in self.input_sources
                if in_src.get()['content_type'] in ('nmr-chemical-shifts', 'nmr-restraints')]

    def getInputSourceIdOfCoord(self) -> int:
        """ Return input_source_id of coordinate file.
            @return: index of input source of coordinate file, -1 otherwise
        """

        for in_src in self.input_sources:
            if in_src.get()['content_type'] == 'model':
                return self.input_sources.index(in_src)

        return -1

    def getNmrContentSubTypes(self) -> Optional[dict]:
        """ Return effective NMR content subtypes.
        """

        content_subtype = get_value_safe(self.getInputSourceDict(self.getInputSourceIdOfNmrData()), 'content_subtype')

        if content_subtype is None:
            return None

        return {k: v for k, v in content_subtype.items() if v > 0}

    def getNmrLegacyContentSubTypes(self, src_id: int) -> Optional[dict]:
        """ Return effective NMR content subtypes.
        """

        content_subtype = get_value_safe(self.getInputSourceDict(src_id), 'content_subtype')

        if content_subtype is None:
            return None

        return {k: v for k, v in content_subtype.items() if v > 0}

    def getNmrStatsOfExptlData(self, content_subtype: str) -> Any:
        """ Return stats of experimental data of a given content subtype.
        """

        return get_value_safe(get_value_safe(self.getInputSourceDict(self.getInputSourceIdOfNmrData()), 'stats_of_exptl_data'), content_subtype)

    def getNmrLegacyStatsOfExptlData(self, src_id: int, content_subtype: str) -> Any:
        """ Return stats of experimental data of a given content subtype.
        """

        return get_value_safe(get_value_safe(self.getInputSourceDict(src_id), 'stats_of_exptl_data'), content_subtype)

    def getNmrRestraints(self) -> Optional[dict]:
        """ Return stats of NMR restraints.
            @deprecated: Please extract _Constraint_file loop of converted NMR-STAR file instead (DAOTHER-7407)
        """

        content_subtypes = self.getNmrContentSubTypes()

        if content_subtypes is None:
            return self.__getNmrRestraints()

        restraints = []

        src_id = self.getInputSourceIdOfNmrData()

        nmr_input_source_dic = self.getInputSourceDict(src_id)

        if nmr_input_source_dic is None:
            return None

        file_name = nmr_input_source_dic['file_name']
        file_type = 'NEF' if nmr_input_source_dic['file_type'] == 'nef' else 'NMR-STAR'

        content_subtype = 'dist_restraint'

        if content_subtype in content_subtypes:
            hydrogen_bonds = disulfide_bonds = diselenide_bonds = other_bonds = symmetric = noe_like = 0

            noe_exp_type = None

            for stat in self.getNmrStatsOfExptlData(content_subtype):

                if 'number_of_constraints' not in stat:
                    continue

                for k, v in stat['number_of_constraints'].items():
                    if 'hydrogen_bonds' in k:
                        hydrogen_bonds += v
                    elif 'disulfide_bonds' in k:
                        disulfide_bonds += v
                    elif 'diselenide_bonds' in k:
                        diselenide_bonds += v
                    elif 'other_bonds' in k:
                        other_bonds += v
                    elif k == 'symmetric_constraints':
                        symmetric += v
                    else:
                        if noe_exp_type is None:
                            noe_exp_type = stat['exp_type']
                        noe_like += v
            if noe_like > 0:
                if noe_exp_type.lower() == 'unknown':
                    noe_exp_type = 'NOE'  # ? (To be decided)'
                else:
                    _noe_exp_type = noe_exp_type.lower()
                    if _noe_exp_type in ('csp', 'chemical shift perturbation', 'shift_perturbation'):
                        noe_exp_type = 'CSP'
                    elif _noe_exp_type == 'noe':
                        noe_exp_type = 'NOE'
                    elif _noe_exp_type in ('noe buildup', 'noe build-up', 'noe_build_up'):
                        noe_exp_type = 'NOE buildup'
                    elif _noe_exp_type in ('noe not seen', 'noe_not_seen'):
                        noe_exp_type = 'NOE not seen'
                    elif _noe_exp_type in ('pre', 'paramagnetic relaxation'):
                        noe_exp_type = 'PRE'
                    elif _noe_exp_type == 'pre solvent':
                        noe_exp_type = 'PRE solvent'
                    elif _noe_exp_type == 'roe':
                        noe_exp_type = 'ROE'

                restraint = {'constraint_filename': file_name,
                             'software_name': file_type,
                             'constraint_type': 'distance',
                             'constraint_subtype': noe_exp_type,
                             'constraint_number': noe_like}
                restraints.append(restraint)
            if hydrogen_bonds > 0:
                restraint = {'constraint_filename': file_name,
                             'software_name': file_type,
                             'constraint_type': 'distance',
                             'constraint_subtype': 'hydrogen bond',
                             'constraint_number': hydrogen_bonds}
                restraints.append(restraint)
            if disulfide_bonds > 0:
                restraint = {'constraint_filename': file_name,
                             'software_name': file_type,
                             'constraint_type': 'distance',
                             'constraint_subtype': 'disulfide bond',
                             'constraint_number': disulfide_bonds}
                restraints.append(restraint)
            if diselenide_bonds > 0:
                restraint = {'constraint_filename': file_name,
                             'software_name': file_type,
                             'constraint_type': 'distance',
                             'constraint_subtype': 'diselenide bond',
                             'constraint_number': diselenide_bonds}
                restraints.append(restraint)
            if other_bonds > 0:
                restraint = {'constraint_filename': file_name,
                             'software_name': file_type,
                             'constraint_type': 'distance',
                             'constraint_subtype': 'other bond',
                             'constraint_number': other_bonds}
                restraints.append(restraint)
            if symmetric > 0:
                restraint = {'constraint_filename': file_name,
                             'software_name': file_type,
                             'constraint_type': 'distance',
                             'constraint_subtype': 'symmetry',
                             'constraint_number': symmetric}
                restraints.append(restraint)

        content_subtype = 'dihed_restraint'

        if content_subtype in content_subtypes:
            proteins = nucleic_acids = carbohydrates = others = 0

            for stat in self.getNmrStatsOfExptlData(content_subtype):

                if 'constraints_per_polymer_type' in stat:  # DAOTHER-6509
                    for k, v in stat['constraints_per_polymer_type'].items():
                        if k == 'protein':
                            proteins += v
                        elif k == 'nucleic_acid':
                            nucleic_acids += v
                        elif k == 'carbohydrate':
                            carbohydrates += v
                        elif k == 'other':
                            others += v
                elif 'number_of_constraints_per_polymer_type' in stat:  # DAOTHER-6509
                    for k, v in stat['number_of_constraints_per_polymer_type'].items():
                        if k == 'protein':
                            proteins += v
                        elif k == 'nucleic_acid':
                            nucleic_acids += v
                        elif k == 'carbohydrate':
                            carbohydrates += v
                        elif k == 'other':
                            others += v

            if proteins > 0:
                restraint = {'constraint_filename': file_name,
                             'software_name': file_type,
                             'constraint_type': 'protein dihedral angle',
                             'constraint_subtype': 'Not applicable',
                             'constraint_number': proteins}
                restraints.append(restraint)
            if nucleic_acids > 0:
                restraint = {'constraint_filename': file_name,
                             'software_name': file_type,
                             'constraint_type': 'nucleic acid dihedral angle',
                             'constraint_subtype': 'Not applicable',
                             'constraint_number': nucleic_acids}
                restraints.append(restraint)
            if carbohydrates > 0:
                restraint = {'constraint_filename': file_name,
                             'software_name': file_type,
                             'constraint_type': 'carbohydrate dihedral angle',
                             'constraint_subtype': 'Not applicable',
                             'constraint_number': carbohydrates}
                restraints.append(restraint)
            if others > 0:
                restraint = {'constraint_filename': file_name,
                             'software_name': file_type,
                             'constraint_type': 'other angle',
                             'constraint_subtype': 'Not applicable',
                             'constraint_number': others}
                restraints.append(restraint)

        content_subtype = 'rdc_restraint'

        if content_subtype in content_subtypes:
            rdc_total = 0

            for stat in self.getNmrStatsOfExptlData(content_subtype):

                if 'number_of_constraints' not in stat:
                    continue

                for k, v in stat['number_of_constraints'].items():
                    rdc_total += v

            restraint = {'constraint_filename': file_name,
                         'software_name': file_type,
                         'constraint_type': 'intervector projection angle',
                         'constraint_subtype': 'RDC',
                         'constraint_number': rdc_total}

            restraints.append(restraint)

        return restraints if len(restraints) > 0 else None

    def __getNmrRestraints(self) -> Optional[List[dict]]:
        """ Return stats of NMR restraints. (legacy)
        """

        list_id = self.getInputSourceIdsOfNmrLegacyData()

        if len(list_id) == 0:
            return None

        restraints = []

        for lid in list_id:

            content_subtypes = self.getNmrLegacyContentSubTypes(lid)

            if content_subtypes is None:
                continue

            nmr_input_source_dic = self.getInputSourceDict(lid)

            if nmr_input_source_dic is None:
                continue

            file_name = nmr_input_source_dic['file_name']
            file_type = 'NEF' if nmr_input_source_dic['file_type'] == 'nef' else 'NMR-STAR'

            content_subtype = 'dist_restraint'

            if content_subtype in content_subtypes:

                stats = self.getNmrLegacyStatsOfExptlData(lid, content_subtype)

                if stats is None:
                    continue

                hydrogen_bonds = disulfide_bonds = diselenide_bonds = other_bonds = symmetric = noe_like = 0

                noe_exp_type = None

                for stat in stats:

                    if 'number_of_constraints' not in stat:
                        continue

                    for k, v in stat['number_of_constraints'].items():
                        if 'hydrogen_bonds' in k:
                            hydrogen_bonds += v
                        elif 'disulfide_bonds' in k:
                            disulfide_bonds += v
                        elif 'diselenide_bonds' in k:
                            diselenide_bonds += v
                        elif 'other_bonds' in k:
                            other_bonds += v
                        elif k == 'symmetric_constraints':
                            symmetric += v
                        else:
                            if noe_exp_type is None:
                                noe_exp_type = stat['exp_type']
                            noe_like += v
                if noe_like > 0:
                    if noe_exp_type.lower() == 'unknown':
                        noe_exp_type = 'NOE'  # ? (To be decided)'
                    else:
                        _noe_exp_type = noe_exp_type.lower()
                        if _noe_exp_type in ('csp', 'chemical shift perturbation', 'shift_perturbation'):
                            noe_exp_type = 'CSP'
                        elif _noe_exp_type == 'noe':
                            noe_exp_type = 'NOE'
                        elif _noe_exp_type in ('noe buildup', 'noe build-up', 'noe_build_up'):
                            noe_exp_type = 'NOE buildup'
                        elif _noe_exp_type in ('noe not seen', 'noe_not_seen'):
                            noe_exp_type = 'NOE not seen'
                        elif _noe_exp_type in ('pre', 'paramagnetic relaxation'):
                            noe_exp_type = 'PRE'
                        elif _noe_exp_type == 'pre solvent':
                            noe_exp_type = 'PRE solvent'
                        elif _noe_exp_type == 'roe':
                            noe_exp_type = 'ROE'

                    restraint = {'constraint_filename': file_name,
                                 'software_name': file_type,
                                 'constraint_type': 'distance',
                                 'constraint_subtype': noe_exp_type,
                                 'constraint_number': noe_like}
                    restraints.append(restraint)
                if hydrogen_bonds > 0:
                    restraint = {'constraint_filename': file_name,
                                 'software_name': file_type,
                                 'constraint_type': 'distance',
                                 'constraint_subtype': 'hydrogen bond',
                                 'constraint_number': hydrogen_bonds}
                    restraints.append(restraint)
                if disulfide_bonds > 0:
                    restraint = {'constraint_filename': file_name,
                                 'software_name': file_type,
                                 'constraint_type': 'distance',
                                 'constraint_subtype': 'disulfide bond',
                                 'constraint_number': disulfide_bonds}
                    restraints.append(restraint)
                if diselenide_bonds > 0:
                    restraint = {'constraint_filename': file_name,
                                 'software_name': file_type,
                                 'constraint_type': 'distance',
                                 'constraint_subtype': 'diselenide bond',
                                 'constraint_number': diselenide_bonds}
                    restraints.append(restraint)
                if other_bonds > 0:
                    restraint = {'constraint_filename': file_name,
                                 'software_name': file_type,
                                 'constraint_type': 'distance',
                                 'constraint_subtype': 'other bond',
                                 'constraint_number': other_bonds}
                    restraints.append(restraint)
                if symmetric > 0:
                    restraint = {'constraint_filename': file_name,
                                 'software_name': file_type,
                                 'constraint_type': 'distance',
                                 'constraint_subtype': 'symmetry',
                                 'constraint_number': symmetric}
                    restraints.append(restraint)

            content_subtype = 'dihed_restraint'

            if content_subtype in content_subtypes:

                stats = self.getNmrLegacyStatsOfExptlData(lid, content_subtype)

                if stats is None:
                    continue

                proteins = nucleic_acids = carbohydrates = others = 0

                for stat in stats:

                    if 'constraints_per_polymer_type' in stat:  # DAOTHER-6509
                        for k, v in stat['constraints_per_polymer_type'].items():
                            if k == 'protein':
                                proteins += v
                            elif k == 'nucleic_acid':
                                nucleic_acids += v
                            elif k == 'carbohydrate':
                                carbohydrates += v
                            elif k == 'other':
                                others += v
                    elif 'number_of_constraints_per_polymer_type' in stat:  # DAOTHER-6509
                        for k, v in stat['number_of_constraints_per_polymer_type'].items():
                            if k == 'protein':
                                proteins += v
                            elif k == 'nucleic_acid':
                                nucleic_acids += v
                            elif k == 'carbohydrate':
                                carbohydrates += v
                            elif k == 'other':
                                others += v

                if proteins > 0:
                    restraint = {'constraint_filename': file_name,
                                 'software_name': file_type,
                                 'constraint_type': 'protein dihedral angle',
                                 'constraint_subtype': 'Not applicable',
                                 'constraint_number': proteins}
                    restraints.append(restraint)
                if nucleic_acids > 0:
                    restraint = {'constraint_filename': file_name,
                                 'software_name': file_type,
                                 'constraint_type': 'nucleic acid dihedral angle',
                                 'constraint_subtype': 'Not applicable',
                                 'constraint_number': nucleic_acids}
                    restraints.append(restraint)
                if carbohydrates > 0:
                    restraint = {'constraint_filename': file_name,
                                 'software_name': file_type,
                                 'constraint_type': 'carbohydrate dihedral angle',
                                 'constraint_subtype': 'Not applicable',
                                 'constraint_number': carbohydrates}
                    restraints.append(restraint)
                if others > 0:
                    restraint = {'constraint_filename': file_name,
                                 'software_name': file_type,
                                 'constraint_type': 'other angle',
                                 'constraint_subtype': 'Not applicable',
                                 'constraint_number': others}
                    restraints.append(restraint)

            content_subtype = 'rdc_restraint'

            if content_subtype in content_subtypes:

                stats = self.getNmrLegacyStatsOfExptlData(lid, content_subtype)

                if stats is None:
                    continue

                rdc_total = 0

                for stat in stats:

                    if 'number_of_constraints' not in stat:
                        continue

                    for k, v in stat['number_of_constraints'].items():
                        rdc_total += v

                restraint = {'constraint_filename': file_name,
                             'software_name': file_type,
                             'constraint_type': 'intervector projection angle',
                             'constraint_subtype': 'RDC',
                             'constraint_number': rdc_total}

                restraints.append(restraint)

        return restraints if len(restraints) > 0 else None

    def getNmrPeaks(self) -> List[dict]:
        """ Return stats of NMR spectral peaks.
        """

        content_subtypes = self.getNmrContentSubTypes()

        if content_subtypes is None:
            return self.__getNmrPeaks()

        spectral_peaks = []

        content_subtype = 'spectral_peak'

        if content_subtype in content_subtypes:
            for stat in self.getNmrStatsOfExptlData(content_subtype):
                spectral_peaks.append({'list_id': stat['list_id'],
                                       'sf_framecode': stat['sf_framecode'],
                                       'number_of_spectral_dimensions': stat['number_of_spectral_dimensions'],
                                       'spectral_dim': stat['spectral_dim']})

        content_subtype = 'spectral_peak_alt'

        if content_subtype in content_subtypes:
            for stat in self.getNmrStatsOfExptlData(content_subtype):
                spectral_peaks.append({'list_id': stat['list_id'],
                                       'sf_framecode': stat['sf_framecode'],
                                       'number_of_spectral_dimensions': stat['number_of_spectral_dimensions'],
                                       'spectral_dim': stat['spectral_dim']})

        return spectral_peaks

    def __getNmrPeaks(self) -> List[dict]:
        """ Return stats of NMR spectral peaks. (legacy)
        """

        list_id = self.getInputSourceIdsOfNmrLegacyData()

        if len(list_id) == 0:
            return []

        spectral_peaks = []

        content_subtype = 'spectral_peak'

        for lid in list_id:

            content_subtypes = self.getNmrLegacyContentSubTypes(lid)

            if content_subtypes is None:
                continue

            stats = self.getNmrLegacyStatsOfExptlData(lid, content_subtype)

            if stats is None:
                continue

            for stat in stats:
                spectral_peaks.append({'list_id': stat['list_id'],
                                       'sf_framecode': stat['sf_framecode'],
                                       'number_of_spectral_dimensions': stat['number_of_spectral_dimensions'],
                                       'spectral_dim': stat['spectral_dim']})

        content_subtype = 'spectral_peak_alt'

        for lid in list_id:

            content_subtypes = self.getNmrLegacyContentSubTypes(lid)

            if content_subtypes is None:
                continue

            stats = self.getNmrLegacyStatsOfExptlData(lid, content_subtype)

            if stats is None:
                continue

            for stat in stats:
                spectral_peaks.append({'list_id': stat['list_id'],
                                       'sf_framecode': stat['sf_framecode'],
                                       'number_of_spectral_dimensions': stat['number_of_spectral_dimensions'],
                                       'spectral_dim': stat['spectral_dim']})

        return spectral_peaks

    def getNmrIsotopes(self) -> Optional[dict]:
        """ Return set of isotopes in assigned chemical shifts.
        """

        content_subtypes = self.getNmrContentSubTypes()

        if content_subtypes is None:
            return self.__getNmrIsotopes()

        content_subtype = 'chem_shift'

        if content_subtype not in content_subtypes:
            return None

        isotopes = {}

        pat = re.compile(r'^(\d+)(\D)$')

        for stat in self.getNmrStatsOfExptlData(content_subtype):
            if 'number_of_assignments' in stat:
                for k in stat['number_of_assignments'].keys():
                    try:
                        g = pat.search(k.split('_')[0].upper()).groups()
                        isotopes[g[0]] = g[1]
                    except AttributeError:
                        pass

        return None if len(isotopes) == 0 else isotopes

    def __getNmrIsotopes(self) -> Optional[dict]:
        """ Return set of isotopes in assigned chemical shifts. (legacy)
        """

        list_id = self.getInputSourceIdsOfNmrLegacyData()

        if len(list_id) == 0:
            return None

        content_subtype = 'chem_shift'

        isotopes = {}

        pat = re.compile(r'^(\d+)(\D)$')

        for lid in list_id:

            content_subtypes = self.getNmrLegacyContentSubTypes(lid)

            if content_subtypes is None:
                continue

            stats = self.getNmrLegacyStatsOfExptlData(lid, content_subtype)

            if stats is None:
                continue

            for stat in stats:
                if 'number_of_assignments' in stat:
                    for k in stat['number_of_assignments'].keys():
                        try:
                            g = pat.search(k.split('_')[0].upper()).groups()
                            isotopes[g[0]] = g[1]
                        except AttributeError:
                            pass

        return None if len(isotopes) == 0 else isotopes

    def getNmrChemShiftRefs(self) -> Optional[List[dict]]:
        """ Return stats of NMR chemical shift references.
        """

        content_subtypes = self.getNmrContentSubTypes()

        if content_subtypes is None:
            return self.__getNmrChemShiftRefs()

        content_subtype = 'chem_shift_ref'

        if content_subtype not in content_subtypes:
            return None

        chem_shift_refs = []

        for stat in self.getNmrStatsOfExptlData(content_subtype):
            loop = []

            if stat['loop'] is not None:
                for el in stat['loop']:
                    _l = {}
                    for k, v in el.items():
                        if v is None or k == 'Entry_ID':
                            continue
                        _l[k.lower()] = v
                    loop.append(_l)

            saveframe_tag = {}

            if stat['saveframe_tag'] is not None:
                for k, v in stat['saveframe_tag'].items():
                    if v is None or k == 'Entry_ID' or k.startswith('Sf_'):
                        continue
                    saveframe_tag[k.lower()] = v

            chem_shift_refs.append({'list_id': stat['list_id'], 'sf_framecode': stat['sf_framecode'], 'loop': loop, 'saveframe_tag': saveframe_tag})

        return chem_shift_refs

    def __getNmrChemShiftRefs(self) -> Optional[List[dict]]:
        """ Return stats of NMR chemical shift references. (legacy)
        """

        list_id = self.getInputSourceIdsOfNmrLegacyData()

        if len(list_id) == 0:
            return None

        content_subtype = 'chem_shift_ref'

        chem_shift_refs = []

        for lid in list_id:

            content_subtypes = self.getNmrLegacyContentSubTypes(lid)

            if content_subtypes is None:
                continue

            stats = self.getNmrLegacyStatsOfExptlData(lid, content_subtype)

            if stats is None:
                continue

            for stat in stats:
                loop = []

                if stat['loop'] is not None:
                    for el in stat['loop']:
                        _l = {}
                        for k, v in el.items():
                            if v is None or k == 'Entry_ID':
                                continue
                            _l[k.lower()] = v
                        loop.append(_l)

                saveframe_tag = {}

                if stat['saveframe_tag'] is not None:
                    for k, v in stat['saveframe_tag'].items():
                        if v is None or k == 'Entry_ID' or k.startswith('Sf_'):
                            continue
                        saveframe_tag[k.lower()] = v

                chem_shift_refs.append({'list_id': stat['list_id'], 'sf_framecode': stat['sf_framecode'], 'loop': loop, 'saveframe_tag': saveframe_tag})

        return None if len(chem_shift_refs) == 0 else chem_shift_refs

    def getPolymerSequenceByInputSrcId(self, input_source_id: int) -> Any:
        """ Retrieve polymer sequence of a given input_source_id.
        """

        return get_value_safe(self.getInputSourceDict(input_source_id), 'polymer_sequence')

    def getNmrPolymerSequenceOf(self, nmr_chain_id: str) -> Optional[dict]:
        """ Retrieve NMR polymer sequence having a given chain_id.
        """

        src_id = self.getInputSourceIdOfNmrData()

        if src_id < 0:
            ids = self.getInputSourceIdsOfNmrLegacyData()
            if len(ids) == 0:
                return None
            src_id = ids[0]

        nmr_polymer_sequence = self.getPolymerSequenceByInputSrcId(src_id)

        if nmr_polymer_sequence is None:
            return None

        return next((ps for ps in nmr_polymer_sequence if ps['chain_id'] == nmr_chain_id), None)

    def getModelPolymerSequenceOf(self, cif_chain_id: str, label_scheme: bool = True) -> Optional[dict]:
        """ Retrieve model polymer sequence having a given chain_id.
        """

        cif_polymer_sequence = self.getPolymerSequenceByInputSrcId(self.getInputSourceIdOfCoord())

        if cif_polymer_sequence is None:
            return None

        return next((ps for ps in cif_polymer_sequence
                     if (ps['chain_id'] == cif_chain_id and label_scheme)
                     or ('auth_chain_id' in ps and ps['auth_chain_id'] == cif_chain_id and not label_scheme)), None)

    def getChainIdsForSameEntity(self) -> Optional[dict]:
        """ Return mapping of chain_id in the NMR data, which share the same entity.
        """

        src_id = self.getInputSourceIdOfNmrData()

        if src_id < 0:
            ids = self.getInputSourceIdsOfNmrLegacyData()
            if len(ids) == 0:
                return None
            src_id = ids[0]

        nmr_polymer_sequence = self.getPolymerSequenceByInputSrcId(src_id)

        if nmr_polymer_sequence is None:
            return None

        ret = {}

        for ps in nmr_polymer_sequence:
            if 'identical_chain_id' in ps:
                ret[ps['chain_id']] = ps['identical_chain_id']

        if len(ret) == 0:
            return None

        return ret

    def getAsymIdsForSameEntity(self) -> Optional[dict]:
        """ Return mapping of asym_id in the coordinates, which share the same entity.
        """

        cif_polymer_sequence = self.getPolymerSequenceByInputSrcId(self.getInputSourceIdOfCoord())

        if cif_polymer_sequence is None:
            return None

        ret = {}

        for ps in cif_polymer_sequence:
            if 'identical_chain_id' in ps:
                ret[ps['chain_id']] = ps['identical_chain_id']

        if len(ret) == 0:
            return None

        return ret

    def getNmrSeq1LetterCodeOf(self, nmr_chain_id: str, fullSequence: bool = True, unmappedSeqId: Optional[List] = None) -> Optional[str]:
        """ Retrieve NMR polymer sequence (1-letter code) having a given chain_id.
        """

        src_id = self.getInputSourceIdOfNmrData()

        if src_id < 0:
            ids = self.getInputSourceIdsOfNmrLegacyData()
            if len(ids) == 0:
                return None
            src_id = ids[0]

        nmr_polymer_sequence = self.getPolymerSequenceByInputSrcId(src_id)

        if nmr_polymer_sequence is None:
            return None

        ps = next((ps for ps in nmr_polymer_sequence if ps['chain_id'] == nmr_chain_id), None)

        if ps is None:
            return None

        f = []

        for seq_id, comp_id in zip(ps['seq_id'], ps['comp_id']):

            if not fullSequence and unmappedSeqId is not None and seq_id in unmappedSeqId:
                continue

            if comp_id in monDict3:
                f.append(monDict3[comp_id])
            elif comp_id in emptyValue:
                f.append('.')
            elif comp_id in unknownResidue:
                f.append('UNK')
            else:
                f.append(f'({comp_id})')

        return ''.join(f)

    def getModelSeq1LetterCodeOf(self, cif_chain_id: str, label_scheme: bool = True) -> Optional[str]:
        """ Retrieve model polymer sequence (1-letter code) having a given chain_id.
        """

        cif_polymer_sequence = self.getPolymerSequenceByInputSrcId(self.getInputSourceIdOfCoord())

        if cif_polymer_sequence is None:
            return None

        ps = next((ps for ps in cif_polymer_sequence
                   if (ps['chain_id'] == cif_chain_id and label_scheme)
                   or ('auth_chain_id' in ps and ps['auth_chain_id'] == cif_chain_id and not label_scheme)), None)

        if ps is None:
            return None

        f = []

        for comp_id in ps['comp_id']:
            if comp_id in monDict3:
                f.append(monDict3[comp_id])
            elif comp_id in emptyValue:
                f.append('.')
            elif comp_id in unknownResidue:
                f.append('UNK')
            else:
                f.append(f'({comp_id})')

        return ''.join(f)

    def getNmrPolymerSequenceWithModelChainId(self, cif_chain_id: str, label_scheme: bool = True) -> Optional[dict]:
        """ Retrieve NMR polymer sequence corresponding to a given coordinate chain_id.
        """

        chain_assigns = get_value_safe(self.chain_assignment.get(), 'model_poly_seq_vs_nmr_poly_seq')

        if chain_assigns is None:
            return None

        for ca in chain_assigns:

            if (ca['ref_chain_id'] == cif_chain_id and label_scheme) or\
               ((ca['ref_auth_chain_id'] if 'ref_auth_chain_id' in ca else ca['ref_chain_id']) == cif_chain_id and not label_scheme):
                return self.getNmrPolymerSequenceOf(ca['test_chain_id'])

        return None

    def getSequenceAlignmentWithNmrChainId(self, nmr_chain_id: str) -> Optional[dict]:
        """ Retrieve sequence alignment (nmr vs model) of a given NMR chain_id.
        """

        key = 'nmr_poly_seq_vs_model_poly_seq'

        chain_assigns = get_value_safe(self.chain_assignment.get(), key)

        if chain_assigns is None:
            return None

        for ca in chain_assigns:

            if ca['ref_chain_id'] == nmr_chain_id:

                if ca['conflict'] > 0:
                    return None

                cif_chain_id = ca['test_chain_id']

                sequence_aligns = get_value_safe(self.sequence_alignment.get(), key)

                if sequence_aligns is None:
                    return None

                for sa in sequence_aligns:

                    if sa['ref_chain_id'] == nmr_chain_id and sa['test_chain_id'] == cif_chain_id:

                        if sa['conflict'] > 0:
                            return None

                        return sa

        return None

    def getSequenceAlignmentWithModelChainId(self, cif_chain_id: str, label_scheme: bool = True) -> Optional[dict]:
        """ Retrieve sequence alignment (model vs nmr) of a given coordinate chain_id.
        """

        key = 'model_poly_seq_vs_nmr_poly_seq'

        chain_assigns = get_value_safe(self.chain_assignment.get(), key)

        if chain_assigns is None:
            return None

        for ca in chain_assigns:

            if (ca['ref_chain_id'] == cif_chain_id and label_scheme) or\
               ((ca['ref_auth_chain_id'] if 'ref_auth_chain_id' in ca else ca['ref_chain_id']) == cif_chain_id and not label_scheme):

                if ca['conflict'] > 0:
                    return None

                _cif_chain_id = ca['ref_chain_id']

                nmr_chain_id = ca['test_chain_id']

                sequence_aligns = get_value_safe(self.sequence_alignment.get(), key)

                if sequence_aligns is None:
                    return None

                for sa in sequence_aligns:

                    if sa['ref_chain_id'] == _cif_chain_id and sa['test_chain_id'] == nmr_chain_id:

                        if sa['conflict'] > 0:
                            return None

                        return sa

        return None

    def getModelPolymerSequenceWithNmrChainId(self, nmr_chain_id: str) -> Optional[dict]:
        """ Retrieve coordinate polymer sequence corresponding to a given NMR chain_id.
        """

        chain_assigns = get_value_safe(self.chain_assignment.get(), 'nmr_poly_seq_vs_model_poly_seq')

        if chain_assigns is None:
            return None

        for ca in chain_assigns:

            if ca['ref_chain_id'] == nmr_chain_id:
                return self.getModelPolymerSequenceOf(ca['test_chain_id'])

        return None

    def getNmrSeq1LetterCodeWithModelChainId(self, cif_chain_id: str, label_scheme: bool = True) -> Optional[str]:
        """ Retrieve NMR polymer sequence (1-letter code) corresponding to a given coordinate chain_id.
        """

        fullSequence = self.getInputSourceIdOfNmrData() != -1

        unmappedSeqId = []

        chain_assign_dic = self.chain_assignment.get()

        chain_assigns = get_value_safe(chain_assign_dic, 'model_poly_seq_vs_nmr_poly_seq')

        if chain_assigns is None:
            return None

        if not fullSequence:

            _chain_assigns = get_value_safe(chain_assign_dic, 'nmr_poly_seq_vs_model_poly_seq')

            if _chain_assigns is not None:

                for _ca in _chain_assigns:

                    if (_ca['test_chain_id'] == cif_chain_id and label_scheme) or\
                       ((_ca['test_auth_chain_id'] if 'test_auth_chain_id' in _ca else _ca['test_chain_id']) == cif_chain_id and not label_scheme):

                        if 'unmapped_sequence' in _ca:

                            for unmapped_sequence in _ca['unmapped_sequence']:
                                unmappedSeqId.append(unmapped_sequence['ref_seq_id'])

                        break

            if len(unmappedSeqId) > 0:

                ids = self.getInputSourceIdsOfNmrLegacyData()

                if len(ids) > 0:
                    input_source = self.input_sources[ids[0]]
                    input_source_dic = input_source.get()

                    content_subtype = input_source_dic['content_subtype']

                    if 'entity' in content_subtype:
                        fullSequence = True  # trust full sequence of the entity if cs file is based on existing BMRB entry (DAOTHR-10222)

        for ca in chain_assigns:

            if (ca['ref_chain_id'] == cif_chain_id and label_scheme) or\
               ((ca['ref_auth_chain_id'] if 'ref_auth_chain_id' in ca else ca['ref_chain_id']) == cif_chain_id and not label_scheme):
                return self.getNmrSeq1LetterCodeOf(ca['test_chain_id'], fullSequence=fullSequence, unmappedSeqId=unmappedSeqId)

        return None

    def getModelSeq1LetterCodeWithNmrChainId(self, nmr_chain_id: str) -> Optional[str]:
        """ Retrieve coordinate polymer sequence (1-letter code) corresponding to a given NMR chain_id.
        """

        chain_assigns = get_value_safe(self.chain_assignment.get(), 'nmr_poly_seq_vs_model_poly_seq')

        if chain_assigns is None:
            return None

        for ca in chain_assigns:

            if ca['ref_chain_id'] == nmr_chain_id:
                return self.getModelSeq1LetterCodeOf(ca['test_chain_id'])

        return None

    def getAverageRMSDWithinRange(self, cif_chain_id: str, cif_beg_seq_id: int, cif_end_seq_id: int, label_scheme: bool = True) -> Optional[float]:
        """ Calculate average RMSD of alpha carbons/phosphates within a given range in the ensemble.
        """

        poly_seq = self.getModelPolymerSequenceOf(cif_chain_id, label_scheme)

        if poly_seq is None or 'type' not in poly_seq:
            return None

        stype = poly_seq['type']

        if 'polypeptide' in stype:
            rmsd_label = 'ca_rmsd'
        elif 'ribonucleotide' in stype:
            rmsd_label = 'p_rmsd'
        else:
            return None

        if rmsd_label not in poly_seq:
            return None

        if not (cif_beg_seq_id in poly_seq['seq_id'] and cif_end_seq_id in poly_seq['seq_id'] and label_scheme)\
           and not ('auth_seq_id' in poly_seq and cif_beg_seq_id in poly_seq['auth_seq_id'] and cif_end_seq_id in poly_seq['auth_seq_id'] and not label_scheme):
            return None

        if label_scheme:
            rmsd = [ps[rmsd_label] for ps in poly_seq if ps['seq_id'] >= cif_beg_seq_id and ps['seq_id'] <= cif_end_seq_id and ps[rmsd_label] is not None]
        else:
            rmsd = [ps[rmsd_label] for ps in poly_seq if ps['auth_seq_id'] >= cif_beg_seq_id and ps['auth_seq_id'] <= cif_end_seq_id and ps[rmsd_label] is not None]

        if len(rmsd) == 0:
            return None

        return sum(rmsd) / len(rmsd)

    def getNumberOfSubmittedConformers(self) -> Optional[int]:
        """ Return number of submitted conformers for the ensemble.
        """

        cif_polymer_sequence = self.getPolymerSequenceByInputSrcId(self.getInputSourceIdOfCoord())

        if cif_polymer_sequence is None:
            return None

        total_models = []

        for poly_seq in cif_polymer_sequence:

            if poly_seq is None or 'type' not in poly_seq:
                continue

            stype = poly_seq['type']

            if 'polypeptide' in stype:
                rmsd_label = 'ca_rmsd'
            elif 'ribonucleotide' in stype:
                rmsd_label = 'p_rmsd'
            else:
                continue

            if rmsd_label not in poly_seq:
                continue

            for rmsd in poly_seq[rmsd_label]:
                total_models.append(rmsd['model_id'])

        if len(total_models) == 0:
            return None

        return len(total_models)

    def getLabelSeqSchemeOf(self, auth_asym_id: str, auth_seq_id: int) -> Tuple[Optional[str], Optional[int]]:
        """ Convert author sequence scheme to label sequence scheme of the coordinates.
        """

        src_id = self.getInputSourceIdOfCoord()

        if src_id == -1:
            return None, None

        cif_polymer_sequence = self.getPolymerSequenceByInputSrcId(src_id)

        if cif_polymer_sequence is not None:
            ps = next((ps for ps in cif_polymer_sequence if ps['auth_chain_id'] == auth_asym_id), None)

            if ps is not None:
                if auth_seq_id in ps['auth_seq_id']:
                    return ps['chain_id'], ps['seq_id'][ps['auth_seq_id'].index(auth_seq_id)]

        ps_in_loop = get_value_safe(self.getInputSourceDict(src_id), 'polymer_sequence_in_loop')

        if ps_in_loop is None:
            return None, None

        if 'branched' in ps_in_loop:
            branched_sequence = ps_in_loop['branched']

            for branched in branched_sequence:
                polymer_sequence = branched['polymer_sequence']

                br = next((br for br in polymer_sequence if br['auth_chain_id'] == auth_asym_id), None)

                if br is not None:
                    if auth_seq_id in br['seq_id']:
                        return br['chain_id'], br['seq_id'].index(auth_seq_id) + 1

        if 'non_poly' in ps_in_loop:
            non_poly_sequence = ps_in_loop['non_poly']

            for non_poly in non_poly_sequence:
                polymer_sequence = non_poly['polymer_sequence']

                np = next((np for np in polymer_sequence if np['auth_chain_id'] == auth_asym_id), None)

                if np is not None:
                    if auth_seq_id in np['seq_id']:
                        return np['chain_id'], np['seq_id'].index(auth_seq_id) + 1

        return None, None

    def getTotalErrors(self) -> int:
        """ Return total number of errors.
        """

        return self.error.getTotal()

    def getTotalWarnings(self) -> int:
        """ Return total number of warnings.
        """

        return self.warning.getTotal()

    def __setStatus(self, status: str):
        """ Set processing status.
        """

        if status in self.status_codes:
            self.__report['information']['status'] = status
        else:
            if self.__verbose:
                self.__lfh.write(f'+{self.__class_name__}.__setStatus() ++ Error  - Unknown status {status}\n')
            raise KeyError(f"+{self.__class_name__}.__setStatus() ++ Error  - Unknown status {status}")

    def setError(self):
        """ Set processing status Error.
        """

        if not self.__immutable:
            self.__report['error'] = self.error.get()

            self.__setStatus('Error')

        else:
            if self.__verbose:
                self.__lfh.write(f'+{self.__class_name__}.setError() ++ Warning  - No effects on NMR data processing report because the report is immutable\n')
            raise UserWarning(f'+{self.__class_name__}.setError() ++ Warning  - No effects on NMR data processing report because the report is immutable')

    def setWarning(self):
        """ Set processing status Warning.
        """

        if not self.__immutable:
            self.__report['warning'] = self.warning.get()

            if not self.isError():
                self.__setStatus('Warning')

        else:
            if self.__verbose:
                self.__lfh.write(f'+{self.__class_name__}.setWarning() ++ Warning  - No effects on NMR data processing report because the report is immutable\n')
            raise UserWarning(f'+{self.__class_name__}.setWarning() ++ Warning  - No effects on NMR data processing report because the report is immutable')

    def clean(self):
        """ Clear errors and warnings.
        """

        if not self.__immutable:

            self.error.clean()
            self.warning.clean()

            self.__report['error'] = None if self.error.getTotal() == 0 else self.error.get()
            self.__report['warning'] = None if self.warning.getTotal() == 0 else self.warning.get()

        else:
            if self.__verbose:
                self.__lfh.write(f'+{self.__class_name__}.clean() ++ Warning  - No effects on NMR data processing report because the report is immutable\n')
            raise UserWarning(f'+{self.__class_name__}.clean() ++ Warning  - No effects on NMR data processing report because the report is immutable')

    def setDiamagnetic(self, diamagnetic: bool):
        """ Set diamagetism of molecular assembly.
        """

        if isinstance(diamagnetic, bool):
            self.__report['information']['diamagnetic'] = diamagnetic

        else:
            if self.__verbose:
                self.__lfh.write(f'+{self.__class_name__}.setDiamagnetic() ++ Warning  - No effects on NMR data processing report because input variable is not boolean type\n')
            raise UserWarning(f'+{self.__class_name__}.setDiamagnetic() ++ Warning  - No effects on NMR data processing report because input variable is not boolean type')

    def setDisulfideBond(self, disulfide_bond: bool):
        """ Set whether molecular assembly has a disulfide bond at least or not.
        """

        if isinstance(disulfide_bond, bool):
            self.__report['information']['disulfide_bond'] = disulfide_bond

        else:
            if self.__verbose:
                self.__lfh.write(f'+{self.__class_name__}.setDisulfideBond() ++ Warning  - No effects on NMR data processing report because input variable is not boolean type\n')
            raise UserWarning(f'+{self.__class_name__}.setDisulfideBond() ++ Warning  - No effects on NMR data processing report because input variable is not boolean type')

    def setOtherBond(self, other_bond: bool):
        """ Set whether molecular assemble has an other bond at least or not.
        """

        if isinstance(other_bond, bool):
            self.__report['information']['other_bond'] = other_bond

        else:
            if self.__verbose:
                self.__lfh.write(f'+{self.__class_name__}.setOtherBond() ++ Warning  - No effects on NMR data processing report because input variable is not boolean type\n')
            raise UserWarning(f'+{self.__class_name__}.setOtherBond() ++ Warning  - No effects on NMR data processing report because input variable is not boolean type')

    def setCyclicPolymer(self, cyclic_polymer: bool):
        """ Set whether molecular assemble contains a cyclic polymer or not.
        """

        if isinstance(cyclic_polymer, bool):
            self.__report['information']['cyclic_polymer'] = cyclic_polymer

        else:
            if self.__verbose:
                self.__lfh.write(f'+{self.__class_name__}.setCyclicPolymer() ++ Warning  - No effects on NMR data processing report because input variable is not boolean type\n')
            raise UserWarning(f'+{self.__class_name__}.setCyclicPolymer() ++ Warning  - No effects on NMR data processing report because input variable is not boolean type')

    def setOutputStatistics(self, output_statistics: Any):
        """ Set output statistics.
        """

        if isinstance(output_statistics, NmrDpReportOutputStatistics):
            self.output_statistics = output_statistics
            self.__report['information']['output_statistics'] = output_statistics.get()

        else:
            if self.__verbose:
                self.__lfh.write(f'+{self.__class_name__}.setOutputStatistics() ++ Warning  - No effects on NMR data processing report because input variable is not target type\n')
            raise UserWarning(f'+{self.__class_name__}.setOutputStatistics() ++ Warning  - No effects on NMR data processing report because input variable is not target_type')

    def setMutable(self):
        """ Enable to mute the report.
        """

        self.__immutable = False

    def get(self) -> dict:
        """ Return NMR data processing report.
        """

        if not self.__immutable:
            self.__report['information']['input_sources'] = [input_source.get() for input_source in self.input_sources]
            self.__report['information']['sequence_alignments'] = self.sequence_alignment.get()
            self.__report['information']['chain_assignments'] = self.chain_assignment.get()
            if self.output_statistics is not None:
                self.__report['information']['output_statistics'] = self.output_statistics.get()

            self.__immutable = True

        return self.__report

    def load(self, report: Optional[dict]) -> bool:
        """ Retrieve NMR data processing report from JSON content.
            @return: True for success or False otherwise
        """

        if report is None:
            return False

        self.__report = copy.copy(report)

        self.input_sources = []

        for contents in self.__report['information']['input_sources']:

            input_source = NmrDpReportInputSource(self.__verbose, self.__lfh)
            input_source.put(contents)

            self.input_sources.append(input_source)

        self.sequence_alignment.put(self.__report['information']['sequence_alignments'])
        self.chain_assignment.put(self.__report['information']['chain_assignments'])
        if self.output_statistics is not None:
            self.output_statistics.put(self.__report['information']['output_statistics'])

        if self.__report['error'] is None:
            self.error = NmrDpReportError(self.__verbose, self.__lfh)
        else:
            self.error.put(self.__report['error'])

        if self.__report['warning'] is None:
            self.warning = NmrDpReportWarning(self.__verbose, self.__lfh)
        else:
            self.warning.put(self.__report['warning'])

        self.setMutable()

        return True

    def writeFile(self, out_path: str) -> bool:
        """ Write NMR data processing report as JSON file.
            @return: True for success or False otherwise
        """

        if self.get() is None:
            return False

        with open(out_path, 'w', encoding='utf-8') as file:
            file.write(getPrettyJson(self.get()))

        return True

    def loadFile(self, in_path: str) -> bool:
        """ Retrieve NMR data processing report from JSON file.
            @return: True for success or False otherwise
        """

        with open(in_path, 'r', encoding='utf-8') as file:

            report = json.loads(file.read())

            if report is None:
                return False

            self.load(report)

        return True

    def inheritFormatIssueErrors(self, prev_report):
        """ Inherit format issue errors from the previous report (e.g. nmr-*-consistency-check workflow operation).
        """

        item = 'format_issue'

        if not self.__immutable:

            file_name = self.input_sources[self.getInputSourceIdOfNmrData()].get()['file_name']
            _file_name = prev_report.input_sources[prev_report.getInputSourceIdOfNmrData()].get()['file_name']

            value_list = prev_report.error.getValueList(item, _file_name)

            if value_list is None:
                return

            for c in value_list:

                if 'file_name' in c:
                    c['file_name'] = file_name

                self.error.appendDescription(item, c)

        else:
            if self.__verbose:
                self.__lfh.write(f'+{self.__class_name__}.inheritFormatIssueErrors() ++ Warning  - No effects on NMR data processing report because the report is immutable\n')
            raise UserWarning(f'+{self.__class_name__}.inheritFormatIssueErrors() ++ Warning  - No effects on NMR data processing report because the report is immutable')

    def inheritPreviousErrors(self, prev_report):
        """ Inherit the previous errors.
        """

        if not self.__immutable:

            for item in prev_report.error.get():

                value_list = prev_report.error.getInheritableValueList(item)

                if value_list is None:
                    continue

                for c in value_list:
                    self.error.appendDescription(item, c)

        else:
            if self.__verbose:
                self.__lfh.write(f'+{self.__class_name__}.inheritPreviousNameErrors() ++ Warning  - '
                                 'No effects on NMR data processing report because the report is immutable\n')
            raise UserWarning(f'+{self.__class_name__}.inheritPreviousNameErrors() ++ Warning  - '
                              'No effects on NMR data processing report because the report is immutable')

    def inheritCorrectedFormatIssueWarnings(self, prev_report):
        """ Inherit corrected format issue warnings from the previous report (e.g. nmr-*-consistency-check workflow operation).
        """

        item = 'corrected_format_issue'

        if not self.__immutable:

            file_name = self.input_sources[self.getInputSourceIdOfNmrData()].get()['file_name']
            _file_name = prev_report.input_sources[prev_report.getInputSourceIdOfNmrData()].get()['file_name']

            value_list = prev_report.warning.getValueList(item, _file_name)

            if value_list is None:
                return

            for c in value_list:

                if 'file_name' in c:
                    c['file_name'] = file_name

                self.warning.appendDescription(item, c)

        else:
            if self.__verbose:
                self.__lfh.write(f'+{self.__class_name__}.inheritCorrectedFormatIssueWarnings() ++ Warning  - '
                                 f'No effects on NMR data processing report because the report is immutable\n')
            raise UserWarning(f'+{self.__class_name__}.inheritCorrectedFormatIssueWarnings() ++ Warning  - '
                              'No effects on NMR data processing report because the report is immutable')

    def inheritCorrectedSaveframeNameWarnings(self, prev_report):
        """ Inherit corrected saveframe name warnings from the previous report (e.g. nmr-*-consistency-check workflow operation).
        """

        item = 'corrected_saveframe_name'

        if not self.__immutable:

            file_name = self.input_sources[self.getInputSourceIdOfNmrData()].get()['file_name']
            _file_name = prev_report.input_sources[prev_report.getInputSourceIdOfNmrData()].get()['file_name']

            value_list = prev_report.warning.getValueList(item, _file_name)

            if value_list is None:
                return

            for c in value_list:

                if 'file_name' in c:
                    c['file_name'] = file_name

                self.warning.appendDescription(item, c)

        else:
            if self.__verbose:
                self.__lfh.write(f'+{self.__class_name__}.inheritCorrectedSaveframeNameWarnings() ++ Warning  - '
                                 'No effects on NMR data processing report because the report is immutable\n')
            raise UserWarning(f'+{self.__class_name__}.inheritCorrectedSaveframeNameWarnings() ++ Warning  - '
                              'No effects on NMR data processing report because the report is immutable')

    def inheritPreviousWarnings(self, prev_report):
        """ Inherit the previous warnings.
        """

        if not self.__immutable:

            for item in prev_report.warning.get():

                value_list = prev_report.warning.getInheritableValueList(item)

                if value_list is None:
                    continue

                for c in value_list:
                    self.warning.appendDescription(item, c)

        else:
            if self.__verbose:
                self.__lfh.write(f'+{self.__class_name__}.inheritPreviousNameWarnings() ++ Warning  - '
                                 'No effects on NMR data processing report because the report is immutable\n')
            raise UserWarning(f'+{self.__class_name__}.inheritPreviousNameWarnings() ++ Warning  - '
                              'No effects on NMR data processing report because the report is immutable')

    def setCorrectedError(self, prev_report):
        """ Initialize history of corrected errors in the previous report.
        """

        if not self.__immutable:

            file_name = self.input_sources[self.getInputSourceIdOfNmrData()].get()['file_name']
            _file_name = prev_report.input_sources[prev_report.getInputSourceIdOfNmrData()].get()['file_name']

            for item in prev_report.error.get().keys():

                if item == 'total':
                    continue

                value_list = self.error.getValueList(item, file_name)
                _value_list = prev_report.error.getUniqueValueList(item, _file_name)

                if _value_list is None:
                    continue

                tlist = []

                for _c in _value_list:

                    if value_list is None or\
                       not any(c for c in value_list
                               if 'sf_framecode' in c and 'sf_framecode' in _c and c['sf_framecode'] == _c['sf_framecode'] and c['description'] == _c['description']):
                        tlist.append(_c)

                for c in tlist:
                    self.error.appendDescription(item, c)

                if len(tlist) > 0:
                    self.setError()

        else:
            if self.__verbose:
                self.__lfh.write(f'+{self.__class_name__}.setCorrectedError() ++ Warning  - No effects on NMR data processing report because the report is immutable\n')
            raise UserWarning(f'+{self.__class_name__}.setCorrectedError() ++ Warning  - No effects on NMR data processing report because the report is immutable')

    def setCorrectedWarning(self, prev_report):
        """ Initialize history of corrected warnings in the previous report.
        """

        if not self.__immutable:

            ignorable_warning_types = ['auth_atom_nomenclature_mismatch', 'ccd_mismatch', 'disordered_index', 'enum_mismatch_ignorable',
                                       'skipped_saveframe_category', 'skipped_loop_category',
                                       'anomalous_chemical_shift', 'unusual_chemical_shift',
                                       'complemented_chemical_shift', 'incompletely_assigned_chemical_shift', 'incompletely_assigned_spectral_peak',
                                       'anomalous_data', 'unusual_data', 'unusual/rare_data', 'insufficient_data', 'conflicted_data', 'inconsistent_data',
                                       'total']

            self.corrected_warning = NmrDpReportWarning(self.__verbose, self.__lfh)

            file_name = self.input_sources[self.getInputSourceIdOfNmrData()].get()['file_name']
            _file_name = prev_report.input_sources[prev_report.getInputSourceIdOfNmrData()].get()['file_name']

            for item in prev_report.warning.get().keys():

                if item in ignorable_warning_types:
                    continue

                value_list = self.warning.getValueList(item, file_name)
                _value_list = prev_report.warning.getUniqueValueList(item, _file_name)

                if _value_list is None:
                    continue

                tlist = []

                for _c in _value_list:

                    if value_list is None or not any(c for c in value_list
                                                     if 'sf_framecode' in c and 'sf_framecode' in _c
                                                     and c['sf_framecode'] == _c['sf_framecode']
                                                     and c['description'] == _c['description']):
                        tlist.append(_c)

                for c in tlist:
                    self.corrected_warning.appendDescription(item, c)

            if self.corrected_warning.getTotal() > 0:
                self.__report['corrected_warning'] = self.corrected_warning.get()

            else:
                self.corrected_warning = None

        else:
            if self.__verbose:
                self.__lfh.write(f'+{self.__class_name__}.setCorrectedWarning() ++ Warning  - No effects on NMR data processing report because the report is immutable\n')
            raise UserWarning(f'+{self.__class_name__}.setCorrectedWarning() ++ Warning  - No effects on NMR data processing report because the report is immutable')


class NmrDpReportInputSource:
    """ Wrapper class for data processing report of NMR data (input source).
    """

    def __init__(self, verbose: bool = True, log: IO = sys.stdout):
        self.__class_name__ = self.__class__.__name__

        self.__verbose = verbose
        self.__lfh = log

        self.items = ('file_name', 'file_type', 'original_file_name', 'content_type', 'content_subtype',
                      'polymer_sequence', 'polymer_sequence_in_loop',
                      'non_standard_residue', 'disulfide_bond', 'other_bond',
                      'stats_of_exptl_data', 'ignore_error')
        self.file_types = ('pdbx',
                           'nef', 'nmr-star',
                           'nm-aux-amb', 'nm-aux-cha', 'nm-aux-gro', 'nm-aux-xea',
                           'nm-res-amb', 'nm-res-ari', 'nm-res-bio', 'nm-res-cha', 'nm-res-cns',
                           'nm-res-cya', 'nm-res-dyn', 'nm-res-gro', 'nm-res-isd', 'nm-res-mr',
                           'nm-res-noa', 'nm-res-oth', 'nm-res-ros', 'nm-res-sax', 'nm-res-sch',
                           'nm-res-syb', 'nm-res-xpl',
                           'nm-pea-any', 'nm-pea-ari', 'nm-pea-bar', 'nm-pea-ccp', 'nm-pea-oli',
                           'nm-pea-pip', 'nm-pea-pon', 'nm-pea-spa', 'nm-pea-sps', 'nm-pea-top',
                           'nm-pea-vie', 'nm-pea-vnm', 'nm-pea-xea', 'nm-pea-xwi',
                           'nm-shi-ari', 'nm-shi-bar', 'nm-shi-gar', 'nm-shi-npi', 'nm-shi-oli',
                           'nm-shi-pip', 'nm-shi-ppm', 'nm-shi-st2', 'nm-shi-xea')
        self.content_types = ('model',
                              'nmr-data-nef', 'nmr-data-str',
                              'nmr-chemical-shifts', 'nmr-restraints', 'nmr-peaks')
        self.content_subtypes = ('coordinate', 'non_poly', 'branched',
                                 'entry_info', 'poly_seq', 'entity', 'chem_shift',
                                 'chem_shift_ref', 'dist_restraint', 'dihed_restraint', 'rdc_restraint',
                                 'plane_restraint', 'adist_restraint', 'jcoup_restraint', 'hvycs_restraint',
                                 'procs_restraint', 'rama_restraint', 'radi_restraint', 'diff_restraint',
                                 'nbase_restraint', 'csa_restraint', 'ang_restraint', 'pre_restraint',
                                 'pcs_restraint', 'prdc_restraint', 'pang_restraint', 'pccr_restraint',
                                 'hbond_restraint', 'ssbond_restraint', 'geo_restraint', 'noepk_restraint',
                                 'rdc_raw_data', 'ddc_restraint', 'csp_restraint', 'auto_relax_restraint',
                                 'heteronucl_noe_data', 'heteronucl_t1_data',
                                 'heteronucl_t2_data', 'heteronucl_t1r_data',
                                 'order_param_data', 'ph_titr_data', 'ph_param_data',
                                 'coupling_const_data',
                                 'ccr_d_csa_restraint', 'ccr_dd_restraint',
                                 'fchiral_restraint', 'saxs_restraint', 'other_restraint',
                                 'spectral_peak', 'spectral_peak_alt', 'topology')

        self.__contents = {item: None for item in self.items}

    def setItemValue(self, item: str, value: Any):
        """ Set an item with a given value.
        """

        if item in self.items:

            if item == 'file_type' and value not in self.file_types:
                if self.__verbose:
                    self.__lfh.write(f'+{self.__class_name__}.setItemValue() ++ Error  - Unknown file type {value}\n')
                raise ValueError(f"+{self.__class_name__}.setItemValue() ++ Error  - Unknown file type {value}")

            if item == 'content_type' and value not in self.content_types:
                if self.__verbose:
                    self.__lfh.write(f'+{self.__class_name__}.setItemValue() ++ Error  - Unknown content type {value}\n')
                raise ValueError(f"+{self.__class_name__}.setItemValue() ++ Error  - Unknown content type {value}")

            if item == 'content_subtype':

                for key in value:

                    if key not in self.content_subtypes:
                        if self.__verbose:
                            self.__lfh.write(f'+{self.__class_name__}.setItemValue() ++ Error  - Unknown content subtype in {value.keys()}\n')
                        raise ValueError(f"+{self.__class_name__}.setItemValue() ++ Error  - Unknown content subtype in {value.keys()}")

                non_positive_keys = [key for key in value if int(value[key]) <= 0]

                for key in non_positive_keys:
                    value.pop(key)

                if len(value) > 0:
                    self.__contents[item] = value

            else:
                self.__contents[item] = value

        else:
            if self.__verbose:
                self.__lfh.write(f'+{self.__class_name__}.setItemValue() ++ Error  - Unknown item type {item}\n')
            raise KeyError(f"+{self.__class_name__}.setItemValue() ++ Error  - Unknown item type {item}")

    def get(self) -> dict:
        """ Retrieve contents.
        """

        return self.__contents

    def put(self, contents: dict):
        """ Set contents.
        """

        self.__contents = contents

    def updateNonStandardResidueByExptlData(self, chain_id: str, seq_id: int, content_subtype: str):
        """ Update specified non_starndard_residue by experimental data.
        """

        if self.__contents['non_standard_residue'] is None:
            return

        try:

            c = next(c for c in self.__contents['non_standard_residue'] if c['chain_id'] == chain_id)

            if seq_id in c['seq_id']:
                c['exptl_data'][c['seq_id'].index(seq_id)][content_subtype] = True
            # # should pass because reallocation of chain_id may happen
            # else:
            #     if self.__verbose:
            #         self.__lfh.write(f'+{self.__class_name__}.updateNonStandardResidueByExptlData() ++ Error  - Unknown seq_id {seq_id}\n')
            #     raise KeyError(f"+{self.__class_name__}.updateNonStandardResidueByExptlData() ++ Error  - Unknown seq_id {seq_id}")

        except StopIteration:
            if self.__verbose:
                self.__lfh.write(f'+{self.__class_name__}.updateNonStandardResidueByExptlData() ++ Error  - Unknown chain_id {chain_id}')
            raise KeyError(f"+{self.__class_name__}.updateNonStandardResidueByExptlData() ++ Error  - Unknown chain_id {chain_id}")  # pylint: disable=raise-missing-from


class NmrDpReportSequenceAlignment:
    """ Wrapper class for data processing report of NMR data (sequence alignment).
    """

    def __init__(self, verbose: bool = True, log: IO = sys.stdout):
        self.__class_name__ = self.__class__.__name__

        self.__verbose = verbose
        self.__lfh = log

        self.items = ('model_poly_seq_vs_coordinate', 'model_poly_seq_vs_nmr_poly_seq', 'nmr_poly_seq_vs_model_poly_seq',
                      'model_poly_seq_vs_mr_restraint', 'model_poly_seq_vs_mr_topology', 'model_poly_seq_vs_spectral_peak',
                      'nmr_poly_seq_vs_chem_shift', 'nmr_poly_seq_vs_dist_restraint', 'nmr_poly_seq_vs_dihed_restraint',
                      'nmr_poly_seq_vs_rdc_restraint', 'nmr_poly_seq_vs_spectral_peak', 'nmr_poly_seq_vs_spectral_peak_alt',
                      'nmr_poly_seq_vs_noepk_restraint', 'nmr_poly_seq_vs_jcoup_restraint',
                      'nmr_poly_seq_vs_rdc_raw_data', 'nmr_poly_seq_vs_csa_restraint',
                      'nmr_poly_seq_vs_ddc_restraint', 'nmr_poly_seq_vs_hvycs_restraint',
                      'nmr_poly_seq_vs_procs_restraint', 'nmr_poly_seq_vs_csp_restraint',
                      'nmr_poly_seq_vs_auto_relax_restraint',
                      'nmr_poly_seq_vs_heteronucl_noe_data', 'nmr_poly_seq_vs_heteronucl_t1_data',
                      'nmr_poly_seq_vs_heteronucl_t2_data', 'nmr_poly_seq_vs_heteronucl_t1r_data',
                      'nmr_poly_seq_vs_order_param_data',
                      'nmr_poly_seq_vs_coupling_const_data',
                      'nmr_poly_seq_vs_ccr_d_csa_restraint', 'nmr_poly_seq_vs_ccr_dd_restraint',
                      'nmr_poly_seq_vs_fchiral_restraint', 'nmr_poly_seq_vs_other_restraint')

        self.__contents = {item: None for item in self.items}

    def setItemValue(self, item: str, value: Any):
        """ Set an item with a given value.
        """

        if item in self.items:
            self.__contents[item] = value

        else:
            if self.__verbose:
                self.__lfh.write(f'+{self.__class_name__}.setItemValue() ++ Error  - Unknown item type {item}\n')
            raise KeyError(f"+{self.__class_name__}.setItemValue() ++ Error  - Unknown item type {item}")

    def get(self) -> dict:
        """ Retrieve contents.
        """

        return self.__contents

    def put(self, contents: dict):
        """ Set contents.
        """

        self.__contents = contents


class NmrDpReportChainAssignment:
    """ Wrapper class for data processing report of NMR data (chain assignment).
    """

    def __init__(self, verbose: bool = True, log: IO = sys.stdout):
        self.__class_name__ = self.__class__.__name__

        self.__verbose = verbose
        self.__lfh = log

        self.items = ('model_poly_seq_vs_nmr_poly_seq', 'nmr_poly_seq_vs_model_poly_seq')

        self.__contents = {item: None for item in self.items}

    def setItemValue(self, item: str, value: Any):
        """ Set an item with a given value.
        """

        if item in self.items:
            self.__contents[item] = value

        else:
            if self.__verbose:
                self.__lfh.write(f'+{self.__class_name__}.setItemValue() ++ Error  - Unknown item type {item}\n')
            raise KeyError(f"+{self.__class_name__}.setItemValue() ++ Error  - Unknown item type {item}")

    def get(self) -> dict:
        """ Retrieve contents.
        """

        return self.__contents

    def put(self, contents: dict):
        """ Set contents.
        """

        self.__contents = contents


class NmrDpReportOutputStatistics:
    """ Wrapper class for data processing report of NMR data (output statistics).
    """

    def __init__(self, verbose: bool = True, log: IO = sys.stdout):
        self.__class_name__ = self.__class__.__name__

        self.__verbose = verbose
        self.__lfh = log

        self.items = ('file_name', 'file_type', 'entry_id', 'entry_title', 'entry_authors',
                      'submission_date', 'processed_date', 'processed_site',
                      'assembly_name', 'file_size', 'md5_checksum',
                      'model', 'software', 'assembly', 'entity',
                      'chem_shift', 'dist_restraint', 'dihed_restraint', 'rdc_restraint', 'spectral_peak')

        self.__contents = {item: None for item in self.items}

    def setItemValue(self, item: str, value: Any):
        """ Set an item with a given value.
        """

        if item in self.items:
            self.__contents[item] = value

        else:
            if self.__verbose:
                self.__lfh.write(f'+{self.__class_name__}.setItemValue() ++ Error  - Unknown item type {item}\n')
            raise KeyError(f"+{self.__class_name__}.setItemValue() ++ Error  - Unknown item type {item}")

    def get(self) -> dict:
        """ Retrieve contents.
        """

        return self.__contents

    def put(self, contents: dict):
        """ Set contents.
        """

        self.__contents = contents


class NmrDpReportError:
    """ Wrapper class for data processing report of NMR data (error).
    """

    def __init__(self, verbose: bool = True, log: IO = sys.stdout):
        self.__class_name__ = self.__class__.__name__

        self.__verbose = verbose
        self.__lfh = log

        self.items = ('internal_error', 'format_issue', 'coordinate_issue',
                      'missing_mandatory_content', 'missing_mandatory_item',
                      'content_mismatch', 'sequence_mismatch',
                      'invalid_data', 'invalid_atom_nomenclature', 'invalid_atom_type', 'invalid_isotope_number', 'invalid_ambiguity_code',
                      'atom_not_found', 'hydrogen_not_instantiated', 'multiple_data', 'missing_data', 'duplicated_index', 'anomalous_data',
                      'unparsed_data')

        self.group_items = ('sequence_mismatch',
                            'invalid_data', 'invalid_atom_nomenclature', 'invalid_atom_type', 'invalid_isotope_number', 'invalid_ambiguity_code',
                            'atom_not_found', 'hydrogen_not_instantiated', 'multiple_data', 'missing_data', 'anomalous_data')

        self.__contents = {item: None for item in self.items}

        self.__contents['total'] = 0

        self.chk_row_pat = re.compile(r'^\[Check row of ([^\[]*)\] (.*)$')
        self.chk_rows_pat = re.compile(r'\[Check rows of ([^\[]*)\] (.*)$')

    def appendDescription(self, item: str, value: Any):
        """ Append an error with a give description.
        """

        if item in self.items:

            if item not in self.__contents or self.__contents[item] is None:
                self.__contents[item] = []

            if item != 'internal_error' and 'category' in value:
                value['category'] = value['category'].lstrip('_')

            if item != 'internal_error' and 'description' in value:
                d = value['description']

                if d.startswith("[Check row of"):
                    g = self.chk_row_pat.search(d).groups()

                    loc = {}
                    for k in g[0].split(','):
                        p = k.lstrip()
                        s = p.index(' ')
                        loc[p[0:s]] = p[s:].lstrip()

                    value['row_location'] = loc
                    value['description'] = g[1]

                elif d.startswith("[Check rows of"):
                    g = self.chk_rows_pat.search(d).groups()

                    locs = {}
                    for k in g[0].split(','):
                        p = k.lstrip()
                        q = p.split(' ', 1)
                        locs[q[0]] = re.sub(' vs ', ',', q[1]).split(',')

                    value['row_locations'] = locs
                    value['description'] = g[1]

            if not any(v for v in self.__contents[item] if v == value):

                if item in self.group_items and 'file_name' in value and 'row_location' not in value and 'row_locations' not in value:

                    if 'sf_framecode' in value:
                        v = next((v for v in self.__contents[item]
                                  if 'file_name' in v and v['file_name'] == value['file_name']
                                  and 'sf_framecode' in v and v['sf_framecode'] == value['sf_framecode']
                                  and 'row_location' not in v and 'row_locations' not in v), None)
                    else:
                        v = next((v for v in self.__contents[item]
                                  if 'file_name' in v and v['file_name'] == value['file_name']
                                  and 'sf_framecode' not in v
                                  and 'row_location' not in v and 'row_locations' not in v), None)

                        if v is not None and value['description'] in v['description'].split('\n'):
                            return

                    if v is not None:
                        v['description'] += f"\n{value['description']}"

                        v['subtotal'] += 1

                        return

                    value['subtotal'] = len(value['description'].split('\n')) if 'inheritable' in value else 1

                self.__contents[item].append(value)

                self.__contents['total'] += 1

        else:
            if self.__verbose:
                self.__lfh.write(f'+{self.__class_name__}.appendDescription() ++ Error  - Unknown item type {item}\n')
            raise KeyError(f"+{self.__class_name__}.appendDescription() ++ Error  - Unknown item type {item}")

    def get(self) -> dict:
        """ Retrieve errors.
        """

        return {k: v for k, v in self.__contents.items() if v is not None}

    def put(self, contents: dict):
        """ Set errors.
        """

        self.__contents = contents

    def getTotal(self) -> int:
        """ Return total number of errors.
            @return: total number of errors
        """

        return self.__contents['total']

    def exists(self, file_name: str, sf_framecode: str) -> bool:
        """ Return whether an error specified by file name and saveframe exists.
            @return: True for an error exists or False otherwise
        """

        for item in self.__contents.keys():

            if item in ('total', 'internal_error') or self.__contents[item] is None:
                continue

            if any(c for c in self.__contents[item]
                   if (c['file_name'] == file_name or file_name in emptyValue) and 'sf_framecode' in c and c['sf_framecode'] == sf_framecode):
                return True

        return False

    def getValueList(self, item: str, file_name: str, key: Optional[str] = None) -> Optional[List[dict]]:
        """ Return list of error values specified by item name and file name.
        """

        if item in ('total', 'internal_error') or self.__contents is None or (item not in self.__contents.keys()) or self.__contents[item] is None:
            return None

        return [c for c in self.__contents[item] if c['file_name'] == file_name or (key is None or key in c['description'])]

    def getValueListWithSf(self, item: str, file_name: str, sf_framecode: str, key: Optional[str] = None) -> Optional[List[dict]]:
        """ Return list of error values specified by item name, file name, and saveframe.
        """

        if item in ('total', 'internal_error') or self.__contents is None or (item not in self.__contents.keys()) or self.__contents[item] is None:
            return None

        return [c for c in self.__contents[item]
                if c['file_name'] == file_name and 'sf_framecode' in c and c['sf_framecode'] == sf_framecode and (key is None or key in c['description'])]

    def getInheritableValueList(self, item: str) -> Optional[List[dict]]:
        """ Return list of error values with inheritable flag.
        """

        if item == 'total' or self.__contents is None or (item not in self.__contents.keys()) or self.__contents[item] is None:
            return None

        return [c for c in self.__contents[item] if 'inheritable' in c and c['inheritable']]

    def getInheritableDictBySf(self, sf_framecode: str) -> Optional[dict]:
        """ Return dictionary of list of error values with inheritable flag for a given sf_framecode.
        """

        if sf_framecode in emptyValue or self.__contents is None:
            return None

        d = {}

        for k, v in self.__contents.items():

            if k == 'total' or v is None:
                continue

            dlist = [c for c in v if 'inheritable' in c and c['inheritable'] and 'sf_framecode' in c and c['sf_framecode'] == sf_framecode]

            if len(dlist) == 0:
                continue

            d[k] = dlist

        if len(d) == 0:
            return None

        return d

    def getUniqueValueList(self, item: str, file_name: str) -> Optional[List[dict]]:
        """ Return list of error values having unique sf_framecode and description.
        """

        if item in ('total', 'internal_error') or self.__contents is None or (item not in self.__contents.keys()) or self.__contents[item] is None:
            return None

        rlist = []

        keys = set()

        for c in self.getValueList(item, file_name):

            if 'sf_framecode' not in c:
                continue

            key = c['sf_framecode'] + c['description']

            if key in keys:
                continue

            if 'row_location' in c:
                del c['row_location']

            elif 'row_locations' in c:
                del c['row_locations']

            rlist.append(c)

            keys.add(key)

        return rlist

    def getDescription(self, item: str, file_name: str, sf_framecode: str) -> Optional[str]:
        """ Return error description specified by item name, file name, and saveframe.
        """

        if item in ('total', 'internal_error') or self.__contents is None or (item not in self.__contents.keys()) or self.__contents[item] is None:
            return None

        try:
            c = next(c for c in self.__contents[item] if c['file_name'] == file_name and 'sf_framecode' in c and c['sf_framecode'] == sf_framecode)
            return c['description']
        except StopIteration:
            return None

    def getCombinedDescriptions(self, file_name: str, sf_framecode: str, original_file_name: Optional[str] = None) -> Optional[List[str]]:
        """ Return combined error descriptions specified by file name and saveframe.
        """

        if self.__contents is None:
            return None

        d = []

        for item in self.items:

            if item == 'internal_error' or self.__contents[item] is None:
                continue

            for c in self.__contents[item]:

                if (c['file_name'] == file_name or original_file_name not in emptyValue)\
                   and 'sf_framecode' in c and c['sf_framecode'] == sf_framecode:
                    d.append(item + ': ' + c['description'])

        if len(d) == 0:
            return None

        return d

    def hasChemicalShiftError(self) -> bool:
        """ Return whether errors for anomalous chemical shifts exist.
        """

        if self.__contents is None:
            return False

        return any(item for item in self.__contents if item == 'anomalous_data')

    def sortFormatIssueError(self):
        """ Sort 'format_issue' error
        """

        if self.__contents is None:
            return

        item = 'format_issue'

        if item not in self.__contents or self.__contents[item] is None or len(self.__contents[item]) < 2:
            return

        d = copy.copy(self.__contents[item])

        self.__contents[item] = []

        for c in d:
            if 'must' not in c['description']:
                self.__contents[item].append(c)

        for c in d:
            if 'must' in c['description']:
                self.__contents[item].append(c)

    def clean(self):
        """ Clean-up empty items and update stats.
        """

        if self.__contents is None:
            return

        items = [item for item in self.__contents.keys() if item != 'total' and (self.__contents[item] is None or len(self.__contents[item]) == 0)]

        for item in items:
            del self.__contents[item]

        total = 0
        for item in self.__contents.keys():
            if item != 'total':
                total += len(self.__contents[item])

        self.__contents['total'] = total


class NmrDpReportWarning:
    """ Wrapper class for data processing report of NMR data (warning).
    """

    def __init__(self, verbose: bool = True, log: IO = sys.stdout):
        self.__class_name__ = self.__class__.__name__

        self.__verbose = verbose
        self.__lfh = log

        self.items = ('encouragement', 'missing_content', 'missing_saveframe', 'missing_data', 'enum_mismatch',
                      'enum_mismatch_ignorable', 'corrected_format_issue', 'corrected_saveframe_name',
                      'disordered_index', 'sequence_mismatch',
                      'atom_nomenclature_mismatch', 'auth_atom_nomenclature_mismatch', 'ccd_mismatch', 'ambiguity_code_mismatch',
                      'skipped_saveframe_category', 'skipped_loop_category',
                      'anomalous_bond_length', 'ambiguous_dihedral_angle', 'anomalous_rdc_vector',
                      'anomalous_chemical_shift', 'unusual_chemical_shift',
                      'complemented_chemical_shift', 'incompletely_assigned_chemical_shift', 'incompletely_assigned_spectral_peak',
                      'anomalous_data', 'unusual_data', 'unusual/rare_data', 'insufficient_data',
                      'conflicted_data', 'inconsistent_data', 'redundant_data',
                      'insufficient_mr_data', 'conflicted_mr_data', 'inconsistent_mr_data', 'redundant_mr_data', 'unsupported_mr_data',
                      'conflicted_peak_list', 'inconsistent_peak_list', 'unsupported_peak_list',
                      'concatenated_sequence', 'coordinate_issue', 'not_superimposed_model', 'exactly_overlaid_model',
                      'assigned_peak_atom_not_found', 'hydrogen_not_instantiated')

        self.group_items = ('sequence_mismatch',
                            'atom_nomenclature_mismatch', 'auth_atom_nomenclature_mismatch', 'ccd_mismatch', 'ambiguity_code_mismatch',
                            'anomalous_bond_length', 'ambiguous_dihedral_angle', 'anomalous_rdc_vector',
                            'complemented_chemical_shift', 'incompletely_assigned_chemical_shift', 'incompletely_assigned_spectral_peak',
                            'unusual/rare_data', 'insufficient_data',
                            'conflicted_data', 'inconsistent_data', 'redundant_data',
                            'insufficient_mr_data', 'conflicted_mr_data', 'inconsistent_mr_data', 'redundant_mr_data', 'unsupported_mr_data',
                            'conflicted_peak_list', 'inconsistent_peak_list', 'unsupported_peak_list',
                            'hydrogen_not_instantiated')

        self.mr_err_items = ('hydrogen_not_instantiated', 'coordinate_issue',
                             'ambiguous_dihedral_angle', 'anomalous_rdc_vector', 'anomalous_data',
                             'insufficient_mr_data', 'conflicted_mr_data', 'inconsistent_mr_data', 'redundant_mr_data', 'unsupported_mr_data',
                             'conflicted_peak_list', 'inconsistent_peak_list', 'unsupported_peak_list')

        self.__contents = {item: None for item in self.items}

        self.__contents['total'] = 0

        self.chk_row_pat = re.compile(r'^\[Check row of ([^\[]*)\] (.*)$')
        self.chk_rows_pat = re.compile(r'\[Check rows of ([^\[]*)\] (.*)$')

    def appendDescription(self, item: str, value: Any):
        """ Append a warning with a give description.
        """

        if item in self.items:

            if item not in self.__contents or self.__contents[item] is None:
                self.__contents[item] = []

            if 'category' in value:
                value['category'] = value['category'].lstrip('_')

            if 'description' in value:
                d = value['description']

                if d.startswith("[Check row of"):
                    g = self.chk_row_pat.search(d).groups()

                    loc = {}
                    for k in g[0].split(','):
                        p = k.lstrip()
                        s = p.index(' ')
                        loc[p[0:s]] = p[s:].lstrip()

                    value['row_location'] = loc
                    value['description'] = g[1]

                elif d.startswith("[Check rows of"):
                    g = self.chk_rows_pat.search(d).groups()

                    locs = {}
                    for k in g[0].split(','):
                        p = k.lstrip()
                        q = p.split(' ', 1)
                        locs[q[0]] = re.sub(' vs ', ',', q[1]).split(',')

                    value['row_locations'] = locs
                    value['description'] = g[1]

            if not any(v for v in self.__contents[item] if v == value):

                if item in self.group_items and 'file_name' in value and 'row_location' not in value and 'row_locations' not in value:

                    if 'sf_framecode' in value:
                        v = next((v for v in self.__contents[item]
                                  if 'file_name' in v and v['file_name'] == value['file_name']
                                  and 'sf_framecode' in v and v['sf_framecode'] == value['sf_framecode']
                                  and 'row_location' not in v and 'row_locations' not in v), None)
                    else:
                        v = next((v for v in self.__contents[item]
                                  if 'file_name' in v and v['file_name'] == value['file_name']
                                  and 'sf_framecode' not in v
                                  and 'row_location' not in v and 'row_locations' not in v), None)

                        if v is not None and value['description'] in v['description'].split('\n'):
                            return

                    if v is not None:
                        v['description'] += f"\n{value['description']}"

                        v['subtotal'] += 1

                        return

                    value['subtotal'] = len(value['description'].split('\n')) if 'inheritable' in value else 1

                self.__contents[item].append(value)

                self.__contents['total'] += 1

        else:
            if self.__verbose:
                self.__lfh.write(f'+{self.__class_name__}.appendDescription() ++ Error  - Unknown item type {item}\n')
            raise KeyError(f"+{self.__class_name__}.appendDescription() ++ Error  - Unknown item type {item}")

    def get(self) -> dict:
        """ Retrieve warnings.
        """

        return {k: v for k, v in self.__contents.items() if v is not None}

    def put(self, contents: dict):
        """ Set warnings.
        """

        self.__contents = contents

    def getTotal(self) -> int:
        """ Return total number of warnings.
            @return: total number of warnings
        """

        return self.__contents['total']

    def exists(self, file_name: str, sf_framecode: str) -> bool:
        """ Return whether a warning specified by file name and saveframe exists.
            @return: True for a warning exists or False otherwise
        """

        for item in self.__contents.keys():

            if item in ('total', 'enum_mismatch_ignorable') or self.__contents[item] is None:
                continue

            if any(c for c in self.__contents[item]
                   if (c['file_name'] == file_name or file_name in emptyValue) and 'sf_framecode' in c and c['sf_framecode'] == sf_framecode):
                return True

        return False

    def getValueList(self, item: str, file_name: str, key: Optional[str] = None) -> Optional[List[dict]]:
        """ Return list of warning values specified by item name and file name.
        """

        if item == 'total' or self.__contents is None or (item not in self.__contents.keys()) or self.__contents[item] is None:
            return None

        return [c for c in self.__contents[item] if c['file_name'] == file_name and (key is None or key in c['description'])]

    def getValueListWithSf(self, item: str, file_name: str, sf_framecode: str, key: Optional[str] = None) -> Optional[List[dict]]:
        """ Return list of warning values specified by item name, file name, and saveframe.
        """

        if item == 'total' or self.__contents is None or (item not in self.__contents.keys()) or self.__contents[item] is None:
            return None

        return [c for c in self.__contents[item]
                if c['file_name'] == file_name and 'sf_framecode' in c and c['sf_framecode'] == sf_framecode and (key is None or key in c['description'])]

    def getInheritableValueList(self, item: str) -> Optional[List[dict]]:
        """ Return list of warning values with inheritable flag.
        """

        if item == 'total' or self.__contents is None or (item not in self.__contents.keys()) or self.__contents[item] is None:
            return None

        return [c for c in self.__contents[item] if 'inheritable' in c and c['inheritable']]

    def getInheritableDictBySf(self, sf_framecode: str) -> Optional[dict]:
        """ Return dictionary of list of warning values with inheritable flag for a given sf_framecode.
        """

        if sf_framecode in emptyValue or self.__contents is None:
            return None

        d = {}

        for k, v in self.__contents.items():

            if k == 'total' or v is None:
                continue

            dlist = [c for c in v if 'inheritable' in c and c['inheritable'] and 'sf_framecode' in c and c['sf_framecode'] == sf_framecode]

            if len(dlist) == 0:
                continue

            d[k] = dlist

        if len(d) == 0:
            return None

        return d

    def getUniqueValueList(self, item: str, file_name: str) -> Optional[List[dict]]:
        """ Return list of warning values having unique sf_framecode and description.
        """

        if item == 'total' or self.__contents is None or (item not in self.__contents.keys()) or self.__contents[item] is None:
            return None

        rlist = []

        keys = set()

        for c in self.getValueList(item, file_name):

            if 'sf_framecode' not in c:
                continue

            key = c['sf_framecode'] + c['description']

            if key in keys:
                continue

            if 'row_location' in c:
                del c['row_location']

            elif 'row_locations' in c:
                del c['row_locations']

            rlist.append(c)

            keys.add(key)

        return rlist

    def getDescription(self, item: str, file_name: str, sf_framecode: str) -> Optional[str]:
        """ Return warning description specified by item name, file name, and saveframe.
        """

        if item == 'total' or self.__contents is None or (item not in self.__contents.keys()) or self.__contents[item] is None:
            return None

        try:
            c = next(c for c in self.__contents[item] if c['file_name'] == file_name and 'sf_framecode' in c and c['sf_framecode'] == sf_framecode)
            return c['description']
        except StopIteration:
            return None

    def getCombinedDescriptions(self, file_name: str, sf_framecode: str, original_file_name: Optional[str] = None) -> Optional[List[str]]:
        """ Return combined warning descriptions specified by file name and saveframe.
        """

        if self.__contents is None:
            return None

        d = []

        for item in self.items:

            if item == 'enum_mismatch_ignorable' or self.__contents[item] is None:
                continue

            for c in self.__contents[item]:

                if (c['file_name'] == file_name or original_file_name not in emptyValue)\
                   and 'sf_framecode' in c and c['sf_framecode'] == sf_framecode:
                    d.append(item + ': ' + c['description'])

        if len(d) == 0:
            return None

        return d

    def hasChemicalShiftWarning(self) -> bool:
        """ Return whether warnings for anomalous/unusual chemical shifts exist.
        """

        if self.__contents is None:
            return False

        return any(item in ('anomalous_data', 'anomalous_chemical_shift', 'unusual_data', 'unusual_chemical_shift')
                   for item in self.__contents)

    def sortChemicalShiftValidation(self):
        """ Sort warning about anomalous/unusual chemical shift.
        """

        if self.__contents is None:
            return

        d = []

        anomalous_cs = mixed_status = False

        for item in ['anomalous_data', 'anomalous_chemical_shift', 'unusual_data', 'unusual_chemical_shift']:

            if item not in self.__contents.keys() or self.__contents[item] is None:
                continue

            _d = [c for c in self.__contents[item] if 'sigma' in c] if 'data' in item else self.__contents[item]
            _d_ = copy.copy(_d)

            if len(_d) > 0:

                if 'anomalous' in item:
                    anomalous_cs = True
                    for c in _d:
                        c['status'] = 'A'

                elif anomalous_cs:
                    mixed_status = True

                d.extend(_d)

                for c in _d_:
                    self.__contents[item].remove(c)

                if len(self.__contents[item]) == 0:
                    self.__contents[item] = None

        if len(d) == 0:
            return

        item = 'anomalous_chemical_shift' if anomalous_cs else 'unusual_chemical_shift'

        self.__contents[item] = []

        if mixed_status:
            for c in d:
                if 'status' not in c:
                    c['status'] = 'S'
                if 'sigma' not in c:
                    c['sigma'] = 0.0

            for c in sorted(sorted(d, key=itemgetter('sigma'), reverse=True), key=itemgetter('status')):
                if 'description_alt' in c:
                    c['description'] = c['description_alt']
                    del c['description_alt']
                del c['sigma']
                self.__contents[item].append(c)

        else:
            for c in d:
                if 'status' in c and not anomalous_cs:
                    del c['status']
                if 'sigma' not in c:
                    c['sigma'] = 0.0

            for c in sorted(d, key=itemgetter('sigma'), reverse=True):
                if 'description_alt' in c:
                    c['description'] = c['description_alt']
                    del c['description_alt']
                del c['sigma']
                self.__contents[item].append(c)

    def sortBySigma(self, item: str):
        """ Sort warning about sigma.
        """

        if self.__contents is None:
            return

        if item not in self.__contents or self.__contents[item] is None or len(self.__contents[item]) < 2:
            return

        d = copy.copy(self.__contents[item])

        self.__contents[item] = []

        for c in sorted(d, key=itemgetter('sigma'), reverse=True):
            self.__contents[item].append(c)

    def clean(self):
        """ Clean-up empty items and update stats.
        """

        if self.__contents is None:
            return

        items = [item for item in self.__contents.keys() if item != 'total' and (self.__contents[item] is None or len(self.__contents[item]) == 0)]

        for item in items:
            del self.__contents[item]

        total = 0
        for item in self.__contents.keys():
            if item != 'total':
                total += len(self.__contents[item])

        self.__contents['total'] = total
