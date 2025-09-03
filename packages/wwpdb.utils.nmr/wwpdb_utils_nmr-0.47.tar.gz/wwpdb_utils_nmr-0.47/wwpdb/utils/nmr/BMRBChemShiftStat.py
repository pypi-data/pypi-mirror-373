##
# File: BMRBChemShiftStat.py
# Date: 20-Sep-2019
#
# Updates:
# 26-Feb-2020  M. Yokochi - load csv resource files if pickle is not available
# 04-Mar-2020  M. Yokochi - support lazy import of others (non-standard residues, DAOTHER-5498)
# 16-Apr-2020  M. Yokochi - fix ambiguity code of atom name starts with 'Q' (e.g. LYZ:QZ)
# 20-Nov-2020  M. Yokochi - fix statics extraction for HEM, HEB, HEC from CSV (DAOTHER-6366)
# 25-Jun-2021  M. Yokochi - add getAtomLikeNameSet() (DAOTHER-6830)
# 13-Oct-2021  M. Yokochi - code revision according to PEP8 using Pylint (DAOTHER-7389, issue #5)
# 03-Dec-2021  M. Yokochi - optimize loading performance of other chemical shift statistics (DAOTHER-7514)
# 04-Feb-2022  M. Yokochi - add getPseudoAtoms() (NMR restraint remediation)
# 14-Feb-2022  M. Yokochi - add getSimilarCompIdFromAtomIds() (NMR restraint remediation)
# 25-Feb-2022  M. Yokochi - add peptideLike() (NMR restraint remediation)
# 11-Nov-2022  M. Yokochi - add getProtonsInSameGroup() (NMR restraint remediation)
# 20-Apr-2023  M. Yokochi - change backbone definition to be consistent with NMR restraint validation
# 13-Dec-2023  M. Yokochi - support peptide-like residues containing symmetric aromatic ring (DAOTHER-8945)
# 22-Apr-2024  M. Yokochi - remap chemical shift statistics in reference to CCD (DAOTHER-9317)
##
""" Wrapper class for retrieving BMRB chemical shift statistics.
    @author: Masashi Yokochi
"""
__docformat__ = "restructuredtext en"
__author__ = "Masashi Yokochi"
__email__ = "yokochi@protein.osaka-u.ac.jp"
__license__ = "Apache License 2.0"
__version__ = "1.0.0"

import sys
import os
import csv
import re
import copy
import pickle
import collections
import shutil

from operator import itemgetter
from typing import IO, List, Set, Tuple, Optional

try:
    from wwpdb.utils.nmr.AlignUtil import (emptyValue,
                                           protonBeginCode,
                                           pseProBeginCode)
    from wwpdb.utils.nmr.ChemCompUtil import ChemCompUtil
    from wwpdb.utils.nmr.mr.ParserListenerUtil import translateToStdAtomName
except ImportError:
    from nmr.AlignUtil import (emptyValue,
                               protonBeginCode,
                               pseProBeginCode)
    from nmr.ChemCompUtil import ChemCompUtil
    from nmr.mr.ParserListenerUtil import translateToStdAtomName


class BMRBChemShiftStat:
    """ Wrapper class for retrieving BMRB chemical shift statistics.
    """

    def __init__(self, verbose: bool = False, log: IO = sys.stderr, ccU: Optional[ChemCompUtil] = None):
        self.__class_name__ = self.__class__.__name__
        self.__version__ = __version__

        self.__verbose = verbose
        self.__lfh = log

        # lazy import of others (non-standard residues)
        self.lazy_others = True

        # directory
        self.stat_dir = os.path.dirname(__file__) + '/bmrb_cs_stat/'

        # URL for BMRB chemical shift statistics
        self.url_for_bmrb_cs_stat_dir = 'https://bmrb.io/ftp/pub/bmrb/statistics/chem_shifts/'

        # csv file names
        self.csv_files = ('aa_filt.csv', 'aa_full.csv',
                          'dna_filt.csv', 'dna_full.csv',
                          'rna_filt.csv', 'rna_full.csv',
                          'others.csv')

        # statistics objects
        self.aa_filt = []
        self.aa_full = []

        self.dna_filt = []
        self.dna_full = []

        self.rna_filt = []
        self.rna_full = []

        self.others = []
        self.extras = []

        self.__aa_comp_ids = set()
        self.__dna_comp_ids = set()
        self.__rna_comp_ids = set()
        self.__oth_comp_ids = set()
        self.__ext_comp_ids = set()

        self.__std_comp_ids = set()
        self.__all_comp_ids = set()
        self.__not_comp_ids = set()

        self.aa_threshold = 0.1
        self.na_threshold = 0.25

        self.max_count_th = 10

        # CCD accessing utility
        self.__ccU = ChemCompUtil(self.__verbose, self.__lfh) if ccU is None else ccU

        if not self.loadStatFromPickleFiles():
            self.loadStatFromCsvFiles()

        self.__cachedDictForPeptideLike = {}
        self.__cachedDictForTypeOfCompId = {}
        self.__cachedDictForSimilarCompId = {}
        self.__cachedDictForMethylAtoms = {}
        self.__cachedDictForMethylProtons = {}
        self.__cachedDictForRepMethylProtons = {}
        self.__cachedDictForNonRepMethylProtons = {}
        self.__cachedDictForProtonInSameGroup = {}

    def hasCompId(self, comp_id: str) -> bool:
        """ Return whether a given comp_id has BMRB chemical shift statistics.
        """

        if comp_id in emptyValue:
            return False

        if comp_id in self.__std_comp_ids:
            return True

        self.loadOtherStatFromCsvFiles(comp_id)

        return comp_id in self.__all_comp_ids

    def peptideLike(self, comp_id: str) -> bool:
        """ Return whether a given comp_id is peptide-like component.
        """

        if comp_id in emptyValue:
            return False

        if comp_id in self.__aa_comp_ids:
            return True

        if comp_id in self.__dna_comp_ids or comp_id in self.__rna_comp_ids:
            return False

        if comp_id in self.__cachedDictForPeptideLike:
            return copy.deepcopy(self.__cachedDictForPeptideLike[comp_id])

        result = self.__ccU.peptideLike(comp_id)

        self.__cachedDictForPeptideLike[comp_id] = result

        return copy.deepcopy(result)

    def getTypeOfCompId(self, comp_id: str) -> bool:
        """ Return type of a given comp_id.
            @return: array of bool: peptide, nucleotide, carbohydrate
        """

        if comp_id in emptyValue:
            return [False, False, False]

        if comp_id in self.__aa_comp_ids:
            return [True, False, False]

        if comp_id in self.__dna_comp_ids or comp_id in self.__rna_comp_ids:
            return [False, True, False]

        if comp_id in self.__cachedDictForTypeOfCompId:
            return copy.deepcopy(self.__cachedDictForTypeOfCompId[comp_id])

        results = self.__ccU.getTypeOfCompId(comp_id)

        self.__cachedDictForTypeOfCompId[comp_id] = results

        return copy.deepcopy(results)

    def getSimilarCompIdFromAtomIds(self, atom_ids: List[str]) -> Optional[str]:
        """ Return the most similar comp_id including atom_ids.
            @return: the most similar comp_id, otherwise None
        """

        key = str(atom_ids)
        if key in self.__cachedDictForSimilarCompId:
            return copy.deepcopy(self.__cachedDictForSimilarCompId[key])

        aa_bb = {"C", "CA", "CB", "H", "HA", "HA2", "HA3", "N"}
        dn_bb = {"C1'", "C2'", "C3'", "C4'", "C5'", "H1'", "H2'", "H2''", "H3'", "H4'", "H5'", "H5''", "H5'1", "H5'2", "H2'1", "H2'2", 'P'}
        rn_bb = {"C1'", "C2'", "C3'", "C4'", "C5'", "H1'", "H2'", "H3'", "H4'", "H5'", "H5''", "HO2'", "H5'1", "H5'2", "H2'1", "HO'2", 'P', "O2'"}
        ch_bb = {"C1", "C2", "C3", "C4", "C5", "C6", "H1", "H2", "H3", "H4", "H5", "H61", "H62"}

        try:

            length = len(atom_ids)
            atom_id_set = set(atom_ids)

            match = [len(atom_id_set & aa_bb),
                     len(atom_id_set & dn_bb),
                     len(atom_id_set & rn_bb),
                     len(atom_id_set & ch_bb)]

            max_match = max(match)
            comp_id = None

            if max_match > 0:
                position = match.index(max_match)
                if position == 0:
                    max_score = 0
                    for _comp_id in self.__aa_comp_ids:
                        _atom_id_set = set(item['atom_id'] for item in self.__get(_comp_id))
                        conflict = len(atom_id_set - _atom_id_set)
                        unmapped = len(_atom_id_set - atom_id_set)
                        score = length - conflict - unmapped
                        if score > max_score:
                            max_score = score
                            comp_id = _comp_id
                    if comp_id is not None:
                        return comp_id

                elif position == 1:
                    max_score = 0
                    for _comp_id in self.__dna_comp_ids:
                        _atom_id_set = set(item['atom_id'] for item in self.__get(_comp_id))
                        conflict = len(atom_id_set - _atom_id_set)
                        unmapped = len(_atom_id_set - atom_id_set)
                        score = length - conflict - unmapped
                        if score > max_score:
                            max_score = score
                            comp_id = _comp_id
                    if comp_id is not None:
                        return comp_id

                elif position == 2:
                    max_score = 0
                    for _comp_id in self.__rna_comp_ids:
                        _atom_id_set = set(item['atom_id'] for item in self.__get(_comp_id))
                        conflict = len(atom_id_set - _atom_id_set)
                        unmapped = len(_atom_id_set - atom_id_set)
                        score = length - conflict - unmapped
                        if score > max_score:
                            max_score = score
                            comp_id = _comp_id
                    if comp_id is not None:
                        return comp_id

                if position == 0:
                    comp_id = None
                    max_score = 0
                    for _comp_id in self.__all_comp_ids:
                        if self.getTypeOfCompId(_comp_id)[0]:
                            _atom_id_set = set(item['atom_id'] for item in self.__get(_comp_id))
                            conflict = len(atom_id_set - _atom_id_set)
                            unmapped = len(_atom_id_set - atom_id_set)
                            score = length - conflict - unmapped
                            if score > max_score:
                                max_score = score
                                comp_id = _comp_id
                    if comp_id is not None:
                        return comp_id

                elif position in (1, 2):
                    max_score = 0
                    for _comp_id in self.__all_comp_ids:
                        if self.getTypeOfCompId(_comp_id)[1]:
                            _atom_id_set = set(item['atom_id'] for item in self.__get(_comp_id))
                            conflict = len(atom_id_set - _atom_id_set)
                            unmapped = len(_atom_id_set - atom_id_set)
                            score = length - conflict - unmapped
                            if score > max_score:
                                max_score = score
                                comp_id = _comp_id
                    if comp_id is not None:
                        return comp_id

                else:
                    max_score = 0
                    for _comp_id in self.__all_comp_ids:
                        if self.getTypeOfCompId(_comp_id)[2]:
                            _atom_id_set = set(item['atom_id'] for item in self.__get(_comp_id))
                            conflict = len(atom_id_set - _atom_id_set)
                            unmapped = len(_atom_id_set - atom_id_set)
                            score = length - conflict - unmapped
                            if score > max_score:
                                max_score = score
                                comp_id = _comp_id
                    if comp_id is not None:
                        return comp_id

            else:
                max_score = 0
                for _comp_id in self.__all_comp_ids:
                    peptide_like, nucleotide_like, carbohydrate_like = self.getTypeOfCompId(_comp_id)
                    if not (peptide_like or nucleotide_like or carbohydrate_like):
                        _atom_id_set = set(item['atom_id'] for item in self.__get(_comp_id))
                        conflict = len(atom_id_set - _atom_id_set)
                        unmapped = len(_atom_id_set - atom_id_set)
                        score = length - conflict - unmapped
                        if score > max_score:
                            max_score = score
                            comp_id = _comp_id

            return comp_id

        finally:
            self.__cachedDictForSimilarCompId[key] = comp_id

    def hasSufficientStat(self, comp_id: str, primary: bool = True) -> bool:
        """ Return whether a given comp_id has sufficient chemical shift statistics.
        """

        if comp_id in emptyValue:
            return False

        if comp_id in self.__std_comp_ids:
            return True

        self.loadOtherStatFromCsvFiles(comp_id)

        if comp_id not in self.__all_comp_ids:
            return False

        if primary:
            if any(item for item in self.others if item['comp_id'] == comp_id and item['primary']):
                return True
        else:
            if any(item for item in self.others if item['comp_id'] == comp_id and 'secondary' in item and item['secondary']):
                return True

        return False

    def get(self, comp_id: str, diamagnetic: bool = True) -> List[dict]:
        """ Return BMRB chemical shift statistics for a given comp_id.
        """

        if comp_id in emptyValue:
            return []

        if comp_id in self.__aa_comp_ids:

            if diamagnetic:
                return [item for item in self.aa_filt if item['comp_id'] == comp_id]

            return [item for item in self.aa_full if item['comp_id'] == comp_id]

        if comp_id in self.__dna_comp_ids:

            if diamagnetic:
                return [item for item in self.dna_filt if item['comp_id'] == comp_id]

            return [item for item in self.dna_full if item['comp_id'] == comp_id]

        if comp_id in self.__rna_comp_ids:

            if diamagnetic:
                return [item for item in self.rna_filt if item['comp_id'] == comp_id]

            return [item for item in self.rna_full if item['comp_id'] == comp_id]

        self.loadOtherStatFromCsvFiles(comp_id)

        if comp_id not in self.__all_comp_ids:
            return []

        return [item for item in self.others if item['comp_id'] == comp_id]

    def __get(self, comp_id: str, diamagnetic: bool = True) -> List[dict]:
        """ Return atom list for a given comp_id.
        """

        if comp_id in emptyValue:
            return []

        if comp_id in self.__aa_comp_ids:

            if diamagnetic:
                return [item for item in self.aa_filt if item['comp_id'] == comp_id]

            return [item for item in self.aa_full if item['comp_id'] == comp_id]

        if comp_id in self.__dna_comp_ids:

            if diamagnetic:
                return [item for item in self.dna_filt if item['comp_id'] == comp_id]

            return [item for item in self.dna_full if item['comp_id'] == comp_id]

        if comp_id in self.__rna_comp_ids:

            if diamagnetic:
                return [item for item in self.rna_filt if item['comp_id'] == comp_id]

            return [item for item in self.rna_full if item['comp_id'] == comp_id]

        self.loadOtherStatFromCsvFiles(comp_id)

        if comp_id not in self.__all_comp_ids:
            self.__appendExtraFromCcd(comp_id)

        if comp_id in self.__oth_comp_ids:
            return [item for item in self.others if item['comp_id'] == comp_id]

        if comp_id in self.__ext_comp_ids:
            return [item for item in self.extras if item['comp_id'] == comp_id]

        return []

    def getMaxAmbigCodeWoSetId(self, comp_id: str, atom_id: str, default: int = 0) -> int:
        """ Return maximum ambiguity code of a given atom that does not require declaration of ambiguity set ID.
            @return: one of (1, 2, 3), 0 for not found (by default)
        """

        if comp_id in emptyValue or atom_id in emptyValue:
            return default

        if comp_id not in self.__std_comp_ids:
            self.loadOtherStatFromCsvFiles(comp_id)

        if comp_id not in self.__all_comp_ids:
            self.__appendExtraFromCcd(comp_id)

        try:

            d = next(item['desc'] for item in self.__get(comp_id) if item['atom_id'] == atom_id)

            if 'geminal' in d:
                return 2

            if d.startswith('aroma-opposite'):
                return 3

            return 1

        except StopIteration:
            return default

    def getGeminalAtom(self, comp_id: str, atom_id: str) -> Optional[str]:
        """ Return geminal or aromatic opposite atom of a given atom.
        """

        if comp_id in emptyValue or atom_id in emptyValue:
            return None

        if comp_id not in self.__std_comp_ids:
            self.loadOtherStatFromCsvFiles(comp_id)

        if comp_id not in self.__all_comp_ids:
            self.__appendExtraFromCcd(comp_id)

        cs_stat = self.__get(comp_id)

        try:

            is_proton = atom_id[0] in protonBeginCode

            d = next(item['desc'] for item in cs_stat if item['atom_id'] == atom_id)

            if d == 'methyl-geminal' and is_proton:
                return next(item['atom_id'] for item in cs_stat
                            if item['desc'] == d and item['atom_id'] != atom_id and item['atom_id'][:-2] == atom_id[:-2] and item['atom_id'][-1] == atom_id[-1])

            if d.startswith('aroma-opposite'):
                return next(item['atom_id'] for item in cs_stat
                            if item['desc'] == d and item['atom_id'] != atom_id and item['atom_id'][0] == atom_id[0]
                            and ((d == 'aroma-opposite' and item['atom_id'][:-1] == atom_id[:-1])
                                 or (d != 'aroma-opposite')))

            if 'geminal' in d:

                if is_proton:

                    _atom_id = self.getProtonsInSameGroup(comp_id, atom_id, excl_self=True)

                    return _atom_id[0] if len(_atom_id) > 0 else None

                if not atom_id.endswith("'"):
                    return next(item['atom_id'] for item in cs_stat
                                if item['desc'] == d and item['atom_id'] != atom_id and item['atom_id'][:-1] == atom_id[:-1])

                if atom_id.endswith("''"):
                    return next(item['atom_id'] for item in cs_stat
                                if item['desc'] == d and item['atom_id'] != atom_id and item['atom_id'] == atom_id[:-1])

                return next(item['atom_id'] for item in cs_stat
                            if item['desc'] == d and item['atom_id'] != atom_id and item['atom_id'] == atom_id + "'")

            return None

        except StopIteration:
            return None

    def getAllAtoms(self, comp_id: str, excl_minor_atom: bool = False, primary: bool = False) -> List[str]:
        """ Return all atoms of a given comp_id.
        """

        if comp_id in emptyValue:
            return []

        if comp_id not in self.__std_comp_ids:
            self.loadOtherStatFromCsvFiles(comp_id)

        if comp_id not in self.__all_comp_ids:
            self.__appendExtraFromCcd(comp_id)

        cs_stat = self.__get(comp_id)

        if comp_id in self.__std_comp_ids or primary:
            return [item['atom_id'] for item in cs_stat
                    if (comp_id != 'PRO' or item['atom_id'] != 'H')  # DAOTHER-9317: PRO:H is in BMRB CS statistics
                    and (not excl_minor_atom or (excl_minor_atom and item['primary']))]

        return [item['atom_id'] for item in cs_stat
                if (not excl_minor_atom or 'secondary' not in item or (excl_minor_atom and item['secondary']))]

    def getBackBoneAtoms(self, comp_id: str, excl_minor_atom: bool = False, polypeptide_like: bool = False,
                         polynucleotide_like: bool = False, carbohydrates_like: bool = False) -> List[str]:
        """ Return backbone atoms of a given comp_id.
        """

        if comp_id in emptyValue:
            return []

        if comp_id not in self.__std_comp_ids:
            self.loadOtherStatFromCsvFiles(comp_id)

        if comp_id not in self.__all_comp_ids:
            self.__appendExtraFromCcd(comp_id)

        if polypeptide_like is False and polynucleotide_like is False and carbohydrates_like is False:
            polypeptide_like, polynucleotide_like, carbohydrates_like = self.getTypeOfCompId(comp_id)

        cs_stat = self.__get(comp_id)

        if comp_id in self.__aa_comp_ids:
            return [item['atom_id'] for item in cs_stat
                    if item['atom_id'] in ("C", "CA", "H", "HA", "HA2", "HA3", "N", "O")
                    and (comp_id != 'PRO' or item['atom_id'] != 'H')  # DAOTHER-9317: PRO:H is in BMRB CS statistics
                    and (not excl_minor_atom or (excl_minor_atom and item['primary']))]

        if comp_id in self.__dna_comp_ids:
            return [item['atom_id'] for item in cs_stat
                    if item['atom_id'] in ("C1'", "C2'", "C3'", "C4'", "C5'",
                                           "H1'", "H2'", "H2''", "H3'", "H4'", "H5'", "H5''",
                                           "P", "OP1", "OP2", "O5'", "O3'") and (not excl_minor_atom or (excl_minor_atom and item['primary']))]

        if comp_id in self.__rna_comp_ids:
            return [item['atom_id'] for item in cs_stat
                    if item['atom_id'] in ("C1'", "C2'", "C3'", "C4'", "C5'",
                                           "H1'", "H2'", "H3'", "H4'", "H5'", "H5''", "HO2'",
                                           "P", "OP1", "OP2", "O5'", "O3'") and (not excl_minor_atom or (excl_minor_atom and item['primary']))]

        if polypeptide_like:
            return [item['atom_id'] for item in cs_stat
                    if item['atom_id'] in ("C", "CA", "H", "HA", "HA2", "HA3", "N", "O")
                    and (not excl_minor_atom or (excl_minor_atom and item['primary']))]

        if polynucleotide_like:
            return [item['atom_id'] for item in cs_stat
                    if item['atom_id'] in ("C1'", "C2'", "C3'", "C4'", "C5'",
                                           "H1'", "H2'", "H2''", "H3'", "H4'", "H5'", "H5''", "HO2'",
                                           "P", "OP1", "OP2", "O5'", "O3'") and (not excl_minor_atom or 'secondary' not in item or (excl_minor_atom and item['secondary']))]

        if carbohydrates_like:
            return [item['atom_id'] for item in cs_stat
                    if item["atom_id"] in ("C1", "C2", "C3", "C4", "C5", "C6",
                                           "H1", "H2", "H3", "H4", "H5", "H61", "H62",
                                           "O1", "O4", "O6")
                    and (not excl_minor_atom or 'secondary' not in item or (excl_minor_atom and item['secondary']))]

        return []

    def getAromaticAtoms(self, comp_id: str, excl_minor_atom: bool = False, primary: bool = False) -> List[str]:
        """ Return aromatic atoms of a given comp_id.
        """

        if comp_id in emptyValue:
            return []

        if comp_id not in self.__std_comp_ids:
            self.loadOtherStatFromCsvFiles(comp_id)

        if comp_id not in self.__all_comp_ids:
            self.__appendExtraFromCcd(comp_id)

        cs_stat = self.__get(comp_id)

        if comp_id in self.__std_comp_ids or primary:
            return [item['atom_id'] for item in cs_stat
                    if 'aroma' in item['desc'] and (not excl_minor_atom or (excl_minor_atom and item['primary']))]

        return [item['atom_id'] for item in cs_stat
                if 'aroma' in item['desc'] and (not excl_minor_atom or 'secondary' not in item or (excl_minor_atom and item['secondary']))]

    def getMethylAtoms(self, comp_id: str) -> List[str]:
        """ Return atoms in methyl group of a given comp_id.
        """

        if comp_id in emptyValue:
            return []

        if comp_id in self.__cachedDictForMethylAtoms:
            return copy.deepcopy(self.__cachedDictForMethylAtoms[comp_id])

        result = self.__ccU.getMethylAtoms(comp_id)

        self.__cachedDictForMethylAtoms[comp_id] = result

        return copy.deepcopy(result)

    def getMethylProtons(self, comp_id: str) -> List[str]:
        """ Return all protons in methyl group of a given comp_id.
        """

        if comp_id in emptyValue:
            return []

        if comp_id in self.__cachedDictForMethylProtons:
            return copy.deepcopy(self.__cachedDictForMethylProtons[comp_id])

        result = self.__ccU.getMethylProtons(comp_id)

        self.__cachedDictForMethylProtons[comp_id] = result

        return copy.deepcopy(result)

    def getRepMethylProtons(self, comp_id: str) -> List[str]:
        """ Return representative protons in methyl group of a given comp_id.
        """

        if comp_id in emptyValue:
            return []

        if comp_id in self.__cachedDictForRepMethylProtons:
            return copy.deepcopy(self.__cachedDictForRepMethylProtons[comp_id])

        result = self.__ccU.getRepMethylProtons(comp_id)

        self.__cachedDictForRepMethylProtons[comp_id] = result

        return copy.deepcopy(result)

    def getNonRepMethylProtons(self, comp_id: str) -> List[str]:
        """ Return non-representative protons in methyl group of a given comp_id.
        """

        if comp_id in emptyValue:
            return []

        if comp_id in self.__cachedDictForNonRepMethylProtons:
            return copy.deepcopy(self.__cachedDictForNonRepMethylProtons[comp_id])

        result = self.__ccU.getNonRepMethylProtons(comp_id)

        self.__cachedDictForNonRepMethylProtons[comp_id] = result

        return copy.deepcopy(result)

    def getProtonsInSameGroup(self, comp_id: str, atom_id: str, excl_self: bool = False) -> List[str]:
        """ Return protons in the same group of a given comp_id and atom_id.
        """

        if comp_id in emptyValue or atom_id in emptyValue:
            return []

        key = (comp_id, atom_id, excl_self)
        if key in self.__cachedDictForProtonInSameGroup:
            return copy.deepcopy(self.__cachedDictForProtonInSameGroup[key])

        result = self.__ccU.getProtonsInSameGroup(comp_id, atom_id, excl_self)

        self.__cachedDictForProtonInSameGroup[key] = result

        return copy.deepcopy(result)

    def getSideChainAtoms(self, comp_id: str, excl_minor_atom: bool = False, polypeptide_like: bool = False,
                          polynucleotide_like: bool = False, carbohydrates_like: bool = False) -> List[str]:
        """ Return sidechain atoms of a given comp_id.
        """

        if comp_id in emptyValue:
            return []

        if comp_id not in self.__std_comp_ids:
            self.loadOtherStatFromCsvFiles(comp_id)

        if comp_id not in self.__all_comp_ids:
            self.__appendExtraFromCcd(comp_id)

        if polypeptide_like is False and polynucleotide_like is False and carbohydrates_like is False:
            polypeptide_like, polynucleotide_like, carbohydrates_like = self.getTypeOfCompId(comp_id)

        bb_atoms = self.getBackBoneAtoms(comp_id, excl_minor_atom, polypeptide_like, polynucleotide_like, carbohydrates_like)
        # """
        # try:
        #     if polypeptide_like:
        #         bb_atoms.remove('CB')
        # except ValueError:
        #     pass
        # """
        cs_stat = self.__get(comp_id)

        if comp_id in self.__std_comp_ids or polypeptide_like:
            return [item['atom_id'] for item in cs_stat
                    if item['atom_id'] not in bb_atoms
                    and (comp_id != 'PRO' or item['atom_id'] != 'H')  # DAOTHER-9317: PRO:H is in BMRB CS statistics
                    and (not excl_minor_atom or (excl_minor_atom and item['primary']))]

        return [item['atom_id'] for item in cs_stat
                if item['atom_id'] not in bb_atoms and (not excl_minor_atom or 'secondary' not in item or (excl_minor_atom and item['secondary']))]

    def getCentroidAtoms(self, comp_id: str, excl_minor_atom: bool = False, polypeptide_like: bool = False,
                         polynucleotide_like: bool = False, carbohydrates_like: bool = False) -> List[str]:
        """ Return ROSETTA 'CEN'troid atoms of a given comp_id.
        """

        if comp_id in emptyValue:
            return []

        if comp_id not in self.__std_comp_ids:
            self.loadOtherStatFromCsvFiles(comp_id)

        if comp_id not in self.__all_comp_ids:
            self.__appendExtraFromCcd(comp_id)

        if polypeptide_like is False and polynucleotide_like is False and carbohydrates_like is False:
            polypeptide_like, polynucleotide_like, carbohydrates_like = self.getTypeOfCompId(comp_id)

        bb_atoms = self.getBackBoneAtoms(comp_id, excl_minor_atom, polypeptide_like, polynucleotide_like, carbohydrates_like)

        cs_stat = self.__get(comp_id)

        if comp_id in self.__std_comp_ids or polypeptide_like:
            return [item['atom_id'] for item in cs_stat
                    if item['atom_id'] not in bb_atoms
                    and item['atom_id'][0] not in protonBeginCode
                    and (not excl_minor_atom or (excl_minor_atom and item['primary']))]

        return [item['atom_id'] for item in cs_stat
                if item['atom_id'] not in bb_atoms
                and item['atom_id'][0] not in protonBeginCode
                and (not excl_minor_atom or 'secondary' not in item or (excl_minor_atom and item['secondary']))]

    def getPseudoAtoms(self, comp_id: str, excl_minor_atom: bool = False, primary: bool = False) -> List[str]:
        """ Return all pseudo atoms of a give comp_id.
        """

        if comp_id in emptyValue:
            return []

        if comp_id not in self.__std_comp_ids:
            self.loadOtherStatFromCsvFiles(comp_id)

        if comp_id not in self.__all_comp_ids:
            self.__appendExtraFromCcd(comp_id)

        cs_stat = self.__get(comp_id)

        if comp_id in self.__std_comp_ids or primary:
            return [item['atom_id'] for item in cs_stat
                    if (('methyl' in item['desc'] and item['atom_id'][0] in protonBeginCode) or 'geminal' in item['desc'] or item['desc'].sratswith('aroma-opposite'))
                    and (not excl_minor_atom or (excl_minor_atom and item['primary']))]

        return [item['atom_id'] for item in cs_stat
                if (('methyl' in item['desc'] and item['atom_id'][0] in protonBeginCode) or 'geminal' in item['desc'] or item['desc'].startswith('aroma-opposite'))
                and (not excl_minor_atom or 'secondary' not in item or (excl_minor_atom and item['secondary']))]

    def loadStatFromCsvFiles(self) -> bool:
        """ Load all BMRB chemical shift statistics from CSV files.
        """

        if any(not os.path.exists(self.stat_dir + csv_file) for csv_file in self.csv_files):
            return False

        self.aa_filt = self.loadStatFromCsvFile(self.stat_dir + 'aa_filt.csv', self.aa_threshold)
        self.aa_full = self.loadStatFromCsvFile(self.stat_dir + 'aa_full.csv', self.aa_threshold)

        self.dna_filt = self.loadStatFromCsvFile(self.stat_dir + 'dna_filt.csv', self.na_threshold)
        self.dna_full = self.loadStatFromCsvFile(self.stat_dir + 'dna_full.csv', self.na_threshold)

        self.rna_filt = self.loadStatFromCsvFile(self.stat_dir + 'rna_filt.csv', self.na_threshold)
        self.rna_full = self.loadStatFromCsvFile(self.stat_dir + 'rna_full.csv', self.na_threshold)

        if not self.lazy_others:
            self.others = self.loadStatFromCsvFile(self.stat_dir + 'others.csv', self.aa_threshold, self.na_threshold)

        self.__updateCompIdSet()

        return True

    def loadOtherStatFromCsvFiles(self, comp_id_interest: Optional[str] = None) -> bool:
        """ Load all BMRB chemical shift statistics from CSV files.
        """

        if not self.lazy_others:
            return True

        if comp_id_interest is None:
            self.others = self.loadStatFromCsvFile(self.stat_dir + 'others.csv', self.aa_threshold, self.na_threshold)
            self.__updateCompIdSet()

        elif comp_id_interest not in self.__all_comp_ids and comp_id_interest not in self.__not_comp_ids:
            stat = self.loadStatFromCsvFile(self.stat_dir + 'others.csv', self.aa_threshold, self.na_threshold, comp_id_interest)
            if len(stat) > 0:
                self.others.extend(stat)
                self.__updateCompIdSet()
            else:
                self.__not_comp_ids.add(comp_id_interest)

        return True

    def loadStatFromCsvFile(self, file_name: str, primary_th: float, secondary_th: Optional[float] = None,
                            comp_id_interest: Optional[str] = None) -> List[dict]:
        """ Load BMRB chemical shift statistics from a given CSV file.
        """

        atm_list = []

        with open(file_name, 'r', encoding='utf-8') as ifh:
            reader = csv.DictReader(ifh)

            for row in reader:

                comp_id = row['comp_id']

                if comp_id_interest is not None and comp_id != comp_id_interest:
                    continue

                if not self.__ccU.updateChemCompDict(comp_id):
                    continue

                rep_methyl_protons = self.__ccU.getRepMethylProtons(comp_id)
                non_rep_methyl_protons = self.__ccU.getNonRepMethylProtons(comp_id)
                rep_methylene_protons = self.__ccU.getRepMethyleneOrAminoProtons(comp_id)
                non_rep_methylene_protons = self.__ccU.getNonRepMethyleneOrAminoProtons(comp_id)

                _atom_id = row['atom_id']

                if comp_id == 'ILE':
                    if _atom_id == 'MG':
                        _atom_id = 'MG2'
                    elif _atom_id == 'MD':
                        _atom_id = 'MD1'

                elif comp_id == 'THR' and _atom_id == 'MG':
                    _atom_id = 'MG2'

                elif _atom_id.endswith('"'):
                    _atom_id = _atom_id[:-1] + "''"

                # methyl proton group
                if _atom_id.startswith('M'):
                    _atom_id = re.sub(r'^M', 'H', _atom_id)

                    for i in range(1, 4):
                        _row = {}
                        _row['comp_id'] = comp_id
                        _row['atom_id'] = _atom_id + str(i)

                        __status, __comp_id, __atom_id = self.checkAtomNomenclature(_row['atom_id'], verbose=False)
                        if not __status:
                            continue

                        if _row['comp_id'] != __comp_id:
                            _row['comp_id'] = __comp_id
                        if _row['atom_id'] != __atom_id:
                            _row['atom_id'] = __atom_id

                        _row['count'] = int(row['count'])
                        _row['avg'] = float(row['avg'])
                        try:
                            _row['std'] = float(row['std'])
                        except ValueError:
                            _row['std'] = None
                        _row['min'] = float(row['min'])
                        _row['max'] = float(row['max'])
                        _row['desc'] = 'methyl'
                        _row['primary'] = False
                        _row['norm_freq'] = None

                        if not any(a['comp_id'] == _row['comp_id'] and a['atom_id'] == _row['atom_id'] for a in atm_list):
                            atm_list.append(_row)

                elif comp_id == 'HEM' and re.match(r'^HM[A-D]$', _atom_id) is not None:  # others.csv dependent code

                    for i in ['', 'A', 'B']:
                        _row = {}
                        _row['comp_id'] = comp_id
                        _row['atom_id'] = _atom_id + i

                        __status, __comp_id, __atom_id = self.checkAtomNomenclature(_row['atom_id'], verbose=False)
                        if not __status:
                            continue

                        if _row['comp_id'] != __comp_id:
                            _row['comp_id'] = __comp_id
                        if _row['atom_id'] != __atom_id:
                            _row['atom_id'] = __atom_id

                        _row['count'] = int(row['count'])
                        _row['avg'] = float(row['avg'])
                        try:
                            _row['std'] = float(row['std'])
                        except ValueError:
                            _row['std'] = None
                        _row['min'] = float(row['min'])
                        _row['max'] = float(row['max'])
                        _row['desc'] = 'methyl'
                        _row['primary'] = False
                        _row['norm_freq'] = None

                        if not any(a['comp_id'] == _row['comp_id'] and a['atom_id'] == _row['atom_id'] for a in atm_list):
                            atm_list.append(_row)

                elif comp_id == 'HEB' and (re.match(r'^HM[A-D]1$', _atom_id) is not None or _atom_id == 'HBB1'):  # others.csv dependent code

                    for i in range(1, 4):
                        _row = {}
                        _row['comp_id'] = comp_id
                        _row['atom_id'] = _atom_id[:-1] + str(i)

                        __status, __comp_id, __atom_id = self.checkAtomNomenclature(_row['atom_id'], verbose=False)
                        if not __status:
                            continue

                        if _row['comp_id'] != __comp_id:
                            _row['comp_id'] = __comp_id
                        if _row['atom_id'] != __atom_id:
                            _row['atom_id'] = __atom_id

                        _row['count'] = int(row['count'])
                        _row['avg'] = float(row['avg'])
                        try:
                            _row['std'] = float(row['std'])
                        except ValueError:
                            _row['std'] = None
                        _row['min'] = float(row['min'])
                        _row['max'] = float(row['max'])
                        _row['desc'] = 'methyl'
                        _row['primary'] = False
                        _row['norm_freq'] = None

                        if not any(a['comp_id'] == _row['comp_id'] and a['atom_id'] == _row['atom_id'] for a in atm_list):
                            atm_list.append(_row)

                elif comp_id == 'HEC' and (re.match(r'^HM[A-D]$', _atom_id) is not None or re.match(r'^HB[BC]$', _atom_id) is not None):  # others.csv dependent code

                    for i in range(1, 4):
                        _row = {}
                        _row['comp_id'] = comp_id
                        _row['atom_id'] = _atom_id + str(i)

                        __status, __comp_id, __atom_id = self.checkAtomNomenclature(_row['atom_id'], verbose=False)
                        if not __status:
                            continue

                        if _row['comp_id'] != __comp_id:
                            _row['comp_id'] = __comp_id
                        if _row['atom_id'] != __atom_id:
                            _row['atom_id'] = __atom_id

                        _row['count'] = int(row['count'])
                        _row['avg'] = float(row['avg'])
                        try:
                            _row['std'] = float(row['std'])
                        except ValueError:
                            _row['std'] = None
                        _row['min'] = float(row['min'])
                        _row['max'] = float(row['max'])
                        _row['desc'] = 'methyl'
                        _row['primary'] = False
                        _row['norm_freq'] = None

                        if not any(a['comp_id'] == _row['comp_id'] and a['atom_id'] == _row['atom_id'] for a in atm_list):
                            atm_list.append(_row)

                # DAOTHER-9317: representative methyl group
                elif any(rep_methyl_proton.startswith(_atom_id) for rep_methyl_proton in rep_methyl_protons
                         if rep_methyl_proton != _atom_id and 0 <= len(rep_methyl_proton) - len(_atom_id) <= 1
                         and _atom_id not in non_rep_methyl_protons):

                    rep_methyl_proton = next(rep_methyl_proton for rep_methyl_proton in rep_methyl_protons
                                             if rep_methyl_proton.startswith(_atom_id))

                    for _atom_id in self.__ccU.getProtonsInSameGroup(comp_id, rep_methyl_proton):
                        _row = {}
                        _row['comp_id'] = comp_id
                        _row['atom_id'] = _atom_id

                        __status, __comp_id, __atom_id = self.checkAtomNomenclature(_row['atom_id'], verbose=False)
                        if not __status:
                            continue

                        if _row['comp_id'] != __comp_id:
                            _row['comp_id'] = __comp_id
                        if _row['atom_id'] != __atom_id:
                            _row['atom_id'] = __atom_id

                        _row['count'] = int(row['count'])
                        _row['avg'] = float(row['avg'])
                        try:
                            _row['std'] = float(row['std'])
                        except ValueError:
                            _row['std'] = None
                        _row['min'] = float(row['min'])
                        _row['max'] = float(row['max'])
                        _row['desc'] = 'methyl'
                        _row['primary'] = False
                        _row['norm_freq'] = None

                        if not any(a['comp_id'] == _row['comp_id'] and a['atom_id'] == _row['atom_id'] for a in atm_list):
                            atm_list.append(_row)

                # geminal proton group
                elif _atom_id.startswith('Q'):
                    _atom_id = re.sub(r'^Q', 'H', _atom_id)

                    for i in range(1, 4):
                        _row = {}
                        _row['comp_id'] = comp_id
                        _row['atom_id'] = _atom_id + str(i)

                        __status, __comp_id, __atom_id = self.checkAtomNomenclature(_row['atom_id'], verbose=False)
                        if not __status:
                            continue

                        if _row['comp_id'] != __comp_id:
                            _row['comp_id'] = __comp_id
                        if _row['atom_id'] != __atom_id:
                            _row['atom_id'] = __atom_id

                        _row['count'] = int(row['count'])
                        _row['avg'] = float(row['avg'])
                        try:
                            _row['std'] = float(row['std'])
                        except ValueError:
                            _row['std'] = None
                        _row['min'] = float(row['min'])
                        _row['max'] = float(row['max'])
                        _row['desc'] = 'isolated'
                        _row['primary'] = False
                        _row['norm_freq'] = None

                        if not any(a['comp_id'] == _row['comp_id'] and a['atom_id'] == _row['atom_id'] for a in atm_list):
                            atm_list.append(_row)

                elif not ((comp_id == 'HEM' and re.match(r'^HM[A-D][AB]$', _atom_id) is not None)
                          or (comp_id == 'HEB' and (re.match(r'^HM[A-D][23]$', _atom_id) is not None
                                                    or re.match(r'^HBB[23]', _atom_id) is not None))
                          or (comp_id == 'HEC' and (re.match(r'^HM[A-D][123]$', _atom_id) is not None
                                                    or re.match(r'^HB[BC][123]$', _atom_id) is not None))):
                    _row = {}
                    _row['comp_id'] = comp_id
                    _row['atom_id'] = _atom_id

                    __status, __comp_id, __atom_id = self.checkAtomNomenclature(_row['atom_id'], verbose=False)
                    if not __status:
                        continue

                    if _row['comp_id'] != __comp_id:
                        _row['comp_id'] = __comp_id
                    if _row['atom_id'] != __atom_id:
                        _row['atom_id'] = __atom_id

                    _row['count'] = int(row['count'])
                    _row['avg'] = float(row['avg'])
                    try:
                        _row['std'] = float(row['std'])
                    except ValueError:
                        _row['std'] = None
                    _row['min'] = float(row['min'])
                    _row['max'] = float(row['max'])
                    _row['desc'] = 'isolated'
                    _row['primary'] = False
                    _row['norm_freq'] = None

                    if not any(a['comp_id'] == _row['comp_id'] and a['atom_id'] == _row['atom_id'] for a in atm_list):
                        atm_list.append(_row)

        comp_ids = set(item['comp_id'] for item in atm_list)

        if secondary_th is not None:  # extract rest of atoms for non-standard residues

            for comp_id in comp_ids:

                if self.__ccU.updateChemCompDict(comp_id):

                    peptide_like = self.__ccU.peptideLike()

                    for a in self.__ccU.lastAtomList:

                        if a[self.__ccU.ccaTypeSymbol] not in ('H', 'C', 'N', 'P'):
                            continue

                        if a[self.__ccU.ccaLeavingAtomFlag] != 'Y'\
                           or (peptide_like
                               and a[self.__ccU.ccaNTerminalAtomFlag] == 'N'
                               and a[self.__ccU.ccaCTerminalAtomFlag] == 'N'):

                            if not any(item for item in atm_list if item['comp_id'] == comp_id and item['atom_id'] == a[self.__ccU.ccaAtomId]):
                                _row = {}
                                _row['comp_id'] = comp_id
                                _row['atom_id'] = a[self.__ccU.ccaAtomId]
                                _row['desc'] = 'isolated'
                                _row['primary'] = False
                                _row['norm_freq'] = None
                                _row['count'] = 0

                                if not any(a['comp_id'] == _row['comp_id'] and a['atom_id'] == _row['atom_id'] for a in atm_list):
                                    atm_list.append(_row)

        self.__detectMethylProtonFromAtomNomenclature(comp_ids, atm_list)
        self.__detectGeminalProtonFromAtomNomenclature(comp_ids, atm_list)

        self.__detectGeminalCarbon(comp_ids, atm_list)
        self.__detectGeminalNitrogen(comp_ids, atm_list)

        self.__detectMajorResonance(comp_ids, atm_list, primary_th, secondary_th)

        # DAOTHER-9317: retrieve missing statistics of geminal, aromatic opposit, and gemenal methyl groups

        __atm_list = copy.deepcopy(atm_list)

        atm_list = []

        with open(file_name, 'r', encoding='utf-8') as ifh:
            reader = csv.DictReader(ifh)

            for row in reader:

                comp_id = row['comp_id']

                if comp_id_interest is not None and comp_id != comp_id_interest:
                    continue

                if not self.__ccU.updateChemCompDict(comp_id):
                    continue

                cc_rel_status = self.__ccU.lastChemCompDict['_chem_comp.pdbx_release_status']

                if cc_rel_status == 'OBS' and '_chem_comp.pdbx_replaced_by' in self.__ccU.lastChemCompDict:
                    replaced_by = self.__ccU.lastChemCompDict['_chem_comp.pdbx_replaced_by']
                    if replaced_by in emptyValue or not self.__ccU.updateChemCompDict(replaced_by):
                        continue

                    comp_id = replaced_by

                prev_atm_list = [item for item in __atm_list if item['comp_id'] == comp_id]

                # peptide_like = self.__ccU.peptideLike()

                rep_methyl_protons = self.__ccU.getRepMethylProtons(comp_id)
                non_rep_methyl_protons = self.__ccU.getNonRepMethylProtons(comp_id)
                rep_methylene_protons = self.__ccU.getRepMethyleneOrAminoProtons(comp_id)
                non_rep_methylene_protons = self.__ccU.getNonRepMethyleneOrAminoProtons(comp_id)

                _atom_id = row['atom_id']

                if comp_id == 'ILE':
                    if _atom_id == 'MG':
                        _atom_id = 'MG2'
                    elif _atom_id == 'MD':
                        _atom_id = 'MD1'

                elif comp_id == 'THR' and _atom_id == 'MG':
                    _atom_id = 'MG2'

                elif _atom_id.endswith('"'):
                    _atom_id = _atom_id[:-1] + "''"

                # methyl proton group
                if _atom_id.startswith('M'):
                    _atom_id = re.sub(r'^M', 'H', _atom_id)

                    for i in range(1, 4):
                        _row = {}
                        _row['comp_id'] = comp_id
                        _row['atom_id'] = _atom_id + str(i)

                        __status, __comp_id, __atom_id = self.checkAtomNomenclature(_row['atom_id'], verbose=self.__verbose)
                        if not __status:
                            continue

                        if _row['comp_id'] != __comp_id:
                            _row['comp_id'] = __comp_id
                        if _row['atom_id'] != __atom_id:
                            _row['atom_id'] = __atom_id

                        _row['count'] = int(row['count'])
                        _row['avg'] = float(row['avg'])
                        try:
                            _row['std'] = float(row['std'])
                        except ValueError:
                            _row['std'] = None
                        _row['min'] = float(row['min'])
                        _row['max'] = float(row['max'])
                        _row['desc'] = 'methyl'
                        _row['primary'] = False
                        _row['norm_freq'] = None

                        if not any(a['comp_id'] == _row['comp_id'] and a['atom_id'] == _row['atom_id'] for a in atm_list):
                            atm_list.append(_row)

                elif comp_id == 'HEM' and re.match(r'^HM[A-D]$', _atom_id) is not None:  # others.csv dependent code

                    for i in ['', 'A', 'B']:
                        _row = {}
                        _row['comp_id'] = comp_id
                        _row['atom_id'] = _atom_id + i

                        __status, __comp_id, __atom_id = self.checkAtomNomenclature(_row['atom_id'], verbose=self.__verbose)
                        if not __status:
                            continue

                        if _row['comp_id'] != __comp_id:
                            _row['comp_id'] = __comp_id
                        if _row['atom_id'] != __atom_id:
                            _row['atom_id'] = __atom_id

                        _row['count'] = int(row['count'])
                        _row['avg'] = float(row['avg'])
                        try:
                            _row['std'] = float(row['std'])
                        except ValueError:
                            _row['std'] = None
                        _row['min'] = float(row['min'])
                        _row['max'] = float(row['max'])
                        _row['desc'] = 'methyl'
                        _row['primary'] = False
                        _row['norm_freq'] = None

                        if not any(a['comp_id'] == _row['comp_id'] and a['atom_id'] == _row['atom_id'] for a in atm_list):
                            atm_list.append(_row)

                elif comp_id == 'HEB' and (re.match(r'^HM[A-D]1$', _atom_id) is not None or _atom_id == 'HBB1'):  # others.csv dependent code

                    for i in range(1, 4):
                        _row = {}
                        _row['comp_id'] = comp_id
                        _row['atom_id'] = _atom_id[:-1] + str(i)

                        __status, __comp_id, __atom_id = self.checkAtomNomenclature(_row['atom_id'], verbose=self.__verbose)
                        if not __status:
                            continue

                        if _row['comp_id'] != __comp_id:
                            _row['comp_id'] = __comp_id
                        if _row['atom_id'] != __atom_id:
                            _row['atom_id'] = __atom_id

                        _row['count'] = int(row['count'])
                        _row['avg'] = float(row['avg'])
                        try:
                            _row['std'] = float(row['std'])
                        except ValueError:
                            _row['std'] = None
                        _row['min'] = float(row['min'])
                        _row['max'] = float(row['max'])
                        _row['desc'] = 'methyl'
                        _row['primary'] = False
                        _row['norm_freq'] = None

                        if not any(a['comp_id'] == _row['comp_id'] and a['atom_id'] == _row['atom_id'] for a in atm_list):
                            atm_list.append(_row)

                elif comp_id == 'HEC' and (re.match(r'^HM[A-D]$', _atom_id) is not None or re.match(r'^HB[BC]$', _atom_id) is not None):  # others.csv dependent code

                    for i in range(1, 4):
                        _row = {}
                        _row['comp_id'] = comp_id
                        _row['atom_id'] = _atom_id + str(i)

                        __status, __comp_id, __atom_id = self.checkAtomNomenclature(_row['atom_id'], verbose=self.__verbose)
                        if not __status:
                            continue

                        if _row['comp_id'] != __comp_id:
                            _row['comp_id'] = __comp_id
                        if _row['atom_id'] != __atom_id:
                            _row['atom_id'] = __atom_id

                        _row['count'] = int(row['count'])
                        _row['avg'] = float(row['avg'])
                        try:
                            _row['std'] = float(row['std'])
                        except ValueError:
                            _row['std'] = None
                        _row['min'] = float(row['min'])
                        _row['max'] = float(row['max'])
                        _row['desc'] = 'methyl'
                        _row['primary'] = False
                        _row['norm_freq'] = None

                        if not any(a['comp_id'] == _row['comp_id'] and a['atom_id'] == _row['atom_id'] for a in atm_list):
                            atm_list.append(_row)

                # DAOTHER-9317: representative methyl group
                elif any(rep_methyl_proton.startswith(_atom_id) for rep_methyl_proton in rep_methyl_protons
                         if rep_methyl_proton != _atom_id and 0 <= len(rep_methyl_proton) - len(_atom_id) <= 1
                         and _atom_id not in non_rep_methyl_protons):

                    rep_methyl_proton = next(rep_methyl_proton for rep_methyl_proton in rep_methyl_protons
                                             if rep_methyl_proton.startswith(_atom_id))

                    for _atom_id in self.__ccU.getProtonsInSameGroup(comp_id, rep_methyl_proton):
                        _row = {}
                        _row['comp_id'] = comp_id
                        _row['atom_id'] = _atom_id

                        __status, __comp_id, __atom_id = self.checkAtomNomenclature(_atom_id, verbose=self.__verbose)
                        if not __status:
                            continue

                        if _row['comp_id'] != __comp_id:
                            _row['comp_id'] = __comp_id
                        if _row['atom_id'] != __atom_id:
                            _row['atom_id'] = __atom_id

                        _row['count'] = int(row['count'])
                        _row['avg'] = float(row['avg'])
                        try:
                            _row['std'] = float(row['std'])
                        except ValueError:
                            _row['std'] = None
                        _row['min'] = float(row['min'])
                        _row['max'] = float(row['max'])
                        _row['desc'] = 'methyl'
                        _row['primary'] = False
                        _row['norm_freq'] = None

                        if not any(a['comp_id'] == _row['comp_id'] and a['atom_id'] == _row['atom_id'] for a in atm_list):
                            atm_list.append(_row)

                # geminal proton group
                elif _atom_id.startswith('Q'):
                    _atom_id = re.sub(r'^Q', 'H', _atom_id)

                    for i in range(1, 4):
                        _row = {}
                        _row['comp_id'] = comp_id
                        _row['atom_id'] = _atom_id + str(i)

                        __status, __comp_id, __atom_id = self.checkAtomNomenclature(_row['atom_id'], verbose=self.__verbose)
                        if not __status:
                            continue

                        if _row['comp_id'] != __comp_id:
                            _row['comp_id'] = __comp_id
                        if _row['atom_id'] != __atom_id:
                            _row['atom_id'] = __atom_id

                        _row['count'] = int(row['count'])
                        _row['avg'] = float(row['avg'])
                        try:
                            _row['std'] = float(row['std'])
                        except ValueError:
                            _row['std'] = None
                        _row['min'] = float(row['min'])
                        _row['max'] = float(row['max'])
                        _row['desc'] = 'isolated'
                        _row['primary'] = False
                        _row['norm_freq'] = None

                        if not any(a['comp_id'] == _row['comp_id'] and a['atom_id'] == _row['atom_id'] for a in atm_list):
                            atm_list.append(_row)

                elif not ((comp_id == 'HEM' and re.match(r'^HM[A-D][AB]$', _atom_id) is not None)
                          or (comp_id == 'HEB' and (re.match(r'^HM[A-D][23]$', _atom_id) is not None
                                                    or re.match(r'^HBB[23]', _atom_id) is not None))
                          or (comp_id == 'HEC' and (re.match(r'^HM[A-D][123]$', _atom_id) is not None
                                                    or re.match(r'^HB[BC][123]$', _atom_id) is not None))):

                    has_geminal_stat = any(item['desc'] == 'geminal' for item in prev_atm_list if item['atom_id'] == _atom_id and 'avg' in item)
                    has_aroma_opposit_stat = any(item['desc'].startswith('aroma-opposite') for item in prev_atm_list if item['atom_id'] == _atom_id and 'avg' in item)
                    has_methyl_geminal_stat = any(item['desc'] == 'methyl-geminal' for item in prev_atm_list if item['atom_id'] == _atom_id and 'avg' in item)

                    if len(_atom_id) > 2 and has_geminal_stat:
                        others = self.__ccU.getProtonsInSameGroup(comp_id, _atom_id, exclSelf=True)
                        if len(others) > 0 and not any('avg' in item for item in prev_atm_list if item['atom_id'] == others[0])\
                           and others[0] in rep_methylene_protons\
                           and (not _atom_id.endswith("'") or others[0].endswith("'"))\
                           and (_atom_id.endswith("'") or not others[0].endswith("'")):

                            _atom_id = others[0]

                            _row = {}
                            _row['comp_id'] = comp_id
                            _row['atom_id'] = _atom_id

                            __status, __comp_id, __atom_id = self.checkAtomNomenclature(_atom_id, verbose=self.__verbose)
                            if not __status:
                                continue

                            if _row['comp_id'] != __comp_id:
                                _row['comp_id'] = __comp_id
                            if _row['atom_id'] != __atom_id:
                                _row['atom_id'] = __atom_id

                            _row['count'] = int(row['count'])
                            _row['avg'] = float(row['avg'])
                            try:
                                _row['std'] = float(row['std'])
                            except ValueError:
                                _row['std'] = None
                            _row['min'] = float(row['min'])
                            _row['max'] = float(row['max'])
                            _row['desc'] = 'isolated'
                            _row['primary'] = False
                            _row['norm_freq'] = None

                            if not any(a['comp_id'] == _row['comp_id'] and a['atom_id'] == _row['atom_id'] for a in atm_list):
                                atm_list.append(_row)

                            continue

                    elif len(_atom_id) > 2 and not has_geminal_stat\
                            and any(rep_methylene_proton.startswith(_atom_id[:-1]) for rep_methylene_proton in rep_methylene_protons):
                        rep_methylene_proton = next(rep_methylene_proton for rep_methylene_proton in rep_methylene_protons
                                                    if rep_methylene_proton.startswith(_atom_id[:-1]))
                        others = self.__ccU.getProtonsInSameGroup(comp_id, rep_methylene_proton, exclSelf=True)
                        if len(others) > 0 and any('avg' in item for item in prev_atm_list if item['atom_id'] == others[0])\
                           and others[0] in non_rep_methylene_protons\
                           and (not _atom_id.endswith("'") or others[0].endswith("'"))\
                           and (_atom_id.endswith("'") or not others[0].endswith("'")):

                            _atom_id = others[0]

                            _row = {}
                            _row['comp_id'] = comp_id
                            _row['atom_id'] = _atom_id

                            __status, __comp_id, __atom_id = self.checkAtomNomenclature(_atom_id, verbose=self.__verbose)
                            if not __status:
                                continue

                            if _row['comp_id'] != __comp_id:
                                _row['comp_id'] = __comp_id
                            if _row['atom_id'] != __atom_id:
                                _row['atom_id'] = __atom_id

                            _row['count'] = int(row['count'])
                            _row['avg'] = float(row['avg'])
                            try:
                                _row['std'] = float(row['std'])
                            except ValueError:
                                _row['std'] = None
                            _row['min'] = float(row['min'])
                            _row['max'] = float(row['max'])
                            _row['desc'] = 'isolated'
                            _row['primary'] = False
                            _row['norm_freq'] = None

                            if not any(a['comp_id'] == _row['comp_id'] and a['atom_id'] == _row['atom_id'] for a in atm_list):
                                atm_list.append(_row)

                            continue

                    if len(_atom_id) > 2 and has_aroma_opposit_stat:
                        _item = next(item for item in prev_atm_list if item['atom_id'] == _atom_id and 'avg' in item and item['desc'].startswith('aroma-opposit'))
                        other = next((item['atom_id'] for item in prev_atm_list
                                      if item['desc'] == _item['desc'] and item['atom_id'].startswith(_item['atom_id'][:-1]) and item['atom_id'] != _item['atom_id']), None)

                        if other is not None and not any('avg' in item for item in prev_atm_list if item['atom_id'] == other)\
                           and (not _atom_id.endswith("'") or other.endswith("'"))\
                           and (_atom_id.endswith("'") or not other.endswith("'")):

                            for __atom_id in sorted([_atom_id, other]):
                                _row = {}
                                _row['comp_id'] = comp_id
                                _row['atom_id'] = __atom_id

                                __status, __comp_id, __atom_id = self.checkAtomNomenclature(__atom_id, verbose=self.__verbose)
                                if not __status:
                                    continue

                                if _row['comp_id'] != __comp_id:
                                    _row['comp_id'] = __comp_id
                                if _row['atom_id'] != __atom_id:
                                    _row['atom_id'] = __atom_id

                                _row['count'] = int(row['count'])
                                _row['avg'] = float(row['avg'])
                                try:
                                    _row['std'] = float(row['std'])
                                except ValueError:
                                    _row['std'] = None
                                _row['min'] = float(row['min'])
                                _row['max'] = float(row['max'])
                                _row['desc'] = 'isolated'
                                _row['primary'] = False
                                _row['norm_freq'] = None

                                if not any(a['comp_id'] == _row['comp_id'] and a['atom_id'] == _row['atom_id'] for a in atm_list):
                                    atm_list.append(_row)

                            continue

                    if len(_atom_id) > 3 and has_methyl_geminal_stat:
                        _item = next(item for item in prev_atm_list if item['atom_id'] == _atom_id and 'avg' in item and item['desc'] == 'methyl-geminal')
                        others = [item['atom_id'] for item in prev_atm_list
                                  if item['desc'] == _item['desc'] and item['atom_id'].startswith(_item['atom_id'][:-2]) and item['atom_id'] != _item['atom_id']]

                        if len(others) > 0 and not any('avg' in item for item in prev_atm_list if item['atom_id'] in others)\
                           and (not _atom_id.endswith("'") or others[0].endswith("'"))\
                           and (_atom_id.endswith("'") or not others[0].endswith("'")):
                            others.append(_atom_id)

                            for __atom_id in sorted(others):
                                _row = {}
                                _row['comp_id'] = comp_id
                                _row['atom_id'] = __atom_id

                                __status, __comp_id, __atom_id = self.checkAtomNomenclature(__atom_id, verbose=self.__verbose)
                                if not __status:
                                    continue

                                if _row['comp_id'] != __comp_id:
                                    _row['comp_id'] = __comp_id
                                if _row['atom_id'] != __atom_id:
                                    _row['atom_id'] = __atom_id

                                _row['count'] = int(row['count'])
                                _row['avg'] = float(row['avg'])
                                try:
                                    _row['std'] = float(row['std'])
                                except ValueError:
                                    _row['std'] = None
                                _row['min'] = float(row['min'])
                                _row['max'] = float(row['max'])
                                _row['desc'] = 'isolated'
                                _row['primary'] = False
                                _row['norm_freq'] = None

                                if not any(a['comp_id'] == _row['comp_id'] and a['atom_id'] == _row['atom_id'] for a in atm_list):
                                    atm_list.append(_row)

                            continue

                    _row = {}
                    _row['comp_id'] = comp_id
                    _row['atom_id'] = _atom_id

                    __status, __comp_id, __atom_id = self.checkAtomNomenclature(_row['atom_id'], verbose=self.__verbose)
                    if not __status:
                        continue

                    if _row['comp_id'] != __comp_id:
                        _row['comp_id'] = __comp_id
                    if _row['atom_id'] != __atom_id:
                        _row['atom_id'] = __atom_id

                    _row['count'] = int(row['count'])
                    _row['avg'] = float(row['avg'])
                    try:
                        _row['std'] = float(row['std'])
                    except ValueError:
                        _row['std'] = None
                    _row['min'] = float(row['min'])
                    _row['max'] = float(row['max'])
                    _row['desc'] = 'isolated'
                    _row['primary'] = False
                    _row['norm_freq'] = None

                    if not any(a['comp_id'] == _row['comp_id'] and a['atom_id'] == _row['atom_id'] for a in atm_list):
                        atm_list.append(_row)

        comp_ids = set(item['comp_id'] for item in atm_list)

        if secondary_th is not None:  # extract rest of atoms for non-standard residues

            for comp_id in comp_ids:

                if self.__ccU.updateChemCompDict(comp_id):

                    peptide_like = self.__ccU.peptideLike()

                    for a in self.__ccU.lastAtomList:

                        if a[self.__ccU.ccaTypeSymbol] not in ('H', 'C', 'N', 'P'):
                            continue

                        if a[self.__ccU.ccaLeavingAtomFlag] != 'Y'\
                           or (peptide_like
                               and a[self.__ccU.ccaNTerminalAtomFlag] == 'N'
                               and a[self.__ccU.ccaCTerminalAtomFlag] == 'N'):

                            if not any(item for item in atm_list if item['comp_id'] == comp_id and item['atom_id'] == a[self.__ccU.ccaAtomId]):
                                _row = {}
                                _row['comp_id'] = comp_id
                                _row['atom_id'] = a[self.__ccU.ccaAtomId]
                                _row['desc'] = 'isolated'
                                _row['primary'] = False
                                _row['norm_freq'] = None
                                _row['count'] = 0

                                if not any(a['comp_id'] == _row['comp_id'] and a['atom_id'] == _row['atom_id'] for a in atm_list):
                                    atm_list.append(_row)

        self.__detectMethylProtonFromAtomNomenclature(comp_ids, atm_list)
        self.__detectGeminalProtonFromAtomNomenclature(comp_ids, atm_list)

        self.__detectGeminalCarbon(comp_ids, atm_list)
        self.__detectGeminalNitrogen(comp_ids, atm_list)

        self.__detectMajorResonance(comp_ids, atm_list, primary_th, secondary_th)

        return atm_list

    def __appendExtraFromCcd(self, comp_id: Optional[str]):
        """ Append atom list as extra residue for a given comp_id.
        """

        if comp_id in emptyValue:
            return

        if comp_id in self.__all_comp_ids or comp_id in self.__ext_comp_ids or not self.__ccU.updateChemCompDict(comp_id):
            return

        atm_list = []

        peptide_like = self.__ccU.peptideLike()

        for a in self.__ccU.lastAtomList:

            if a[self.__ccU.ccaTypeSymbol] not in ('H', 'C', 'N', 'P'):
                continue

            if a[self.__ccU.ccaLeavingAtomFlag] != 'Y'\
               or (peptide_like
                   and a[self.__ccU.ccaNTerminalAtomFlag] == 'N'
                   and a[self.__ccU.ccaCTerminalAtomFlag] == 'N'):
                _row = {}
                _row['comp_id'] = comp_id
                _row['atom_id'] = a[self.__ccU.ccaAtomId]
                _row['desc'] = 'isolated'
                _row['primary'] = False
                _row['norm_freq'] = None

                atm_list.append(_row)

        self.__ext_comp_ids.add(comp_id)

        if len(atm_list) == 0:
            return

        comp_ids = [comp_id]

        self.__detectMethylProtonFromAtomNomenclature(comp_ids, atm_list)
        self.__detectGeminalProtonFromAtomNomenclature(comp_ids, atm_list)

        self.__detectGeminalCarbon(comp_ids, atm_list)
        self.__detectGeminalNitrogen(comp_ids, atm_list)

        self.extras.extend(atm_list)

    def checkAtomNomenclature(self, atom_id: str, comp_id: Optional[str] = None, verbose: bool = False
                              ) -> Tuple[bool, Optional[str], Optional[str]]:
        """ Check atom nomenclature.
            @return: status (bool), mapped comp_id, mapped atom_id
        """

        if comp_id is not None:
            self.__ccU.updateChemCompDict(comp_id)

        comp_id = self.__ccU.lastCompId
        peptide_like = self.__ccU.peptideLike()

        cc_rel_status = self.__ccU.lastChemCompDict['_chem_comp.pdbx_release_status']

        if cc_rel_status == 'OBS' and '_chem_comp.pdbx_replaced_by' in self.__ccU.lastChemCompDict:
            replaced_by = self.__ccU.lastChemCompDict['_chem_comp.pdbx_replaced_by']
            if replaced_by not in emptyValue and self.__ccU.updateChemCompDict(replaced_by):
                if verbose:
                    self.__lfh.write(f"+{self.__class_name__}.checkAtomNomenclature() ++ Warning  - {comp_id} is replaced by {replaced_by}\n")

                comp_id = replaced_by
                ref_atom_ids = [a[self.__ccU.ccaAtomId] for a in self.__ccU.lastAtomList]

                cc_rel_status = self.__ccU.lastChemCompDict['_chem_comp.pdbx_release_status']

        if cc_rel_status == 'REL':
            if any(a[self.__ccU.ccaAtomId] for a in self.__ccU.lastAtomList
                   if a[self.__ccU.ccaAtomId] == atom_id
                   and (a[self.__ccU.ccaLeavingAtomFlag] != 'Y'
                        or (peptide_like
                            and a[self.__ccU.ccaNTerminalAtomFlag] == 'N'
                            and a[self.__ccU.ccaCTerminalAtomFlag] == 'N'))):
                return True, comp_id, atom_id

        ref_atom_ids = [a[self.__ccU.ccaAtomId] for a in self.__ccU.lastAtomList]

        if len(ref_atom_ids) == 0 or cc_rel_status != 'REL':
            if verbose:
                self.__lfh.write(f"+{self.__class_name__}.checkAtomNomenclature() ++ Warning  - {comp_id} is not valid CCD ID, status code: {cc_rel_status}\n")
            return False, None, None

        ref_alt_atom_ids = [a[self.__ccU.ccaAltAtomId] for a in self.__ccU.lastAtomList]

        if atom_id in ref_atom_ids and atom_id in ref_alt_atom_ids:
            _ref_atom_id = next(a[self.__ccU.ccaAtomId] for a in self.__ccU.lastAtomList
                                if a[self.__ccU.ccaAltAtomId] == atom_id)

            if atom_id == _ref_atom_id:
                return True, comp_id, atom_id

            if verbose:
                self.__lfh.write(f"+{self.__class_name__}.checkAtomNomenclature() ++ Warning  - {comp_id}:{atom_id} is valid, "
                                 f"but _chem_comp.alt_atom_id matched with different atom_id {_ref_atom_id}\n")

            return True, comp_id, atom_id

        if atom_id in ref_atom_ids and atom_id not in ref_alt_atom_ids:
            return True, comp_id, atom_id

        if atom_id not in ref_atom_ids and atom_id in ref_alt_atom_ids:
            _ref_atom_id = next(a[self.__ccU.ccaAtomId] for a in self.__ccU.lastAtomList
                                if a[self.__ccU.ccaAltAtomId] == atom_id)

            if verbose:
                self.__lfh.write(f"+{self.__class_name__}.checkAtomNomenclature() ++ Warning  - {comp_id}:{atom_id} matched with _chem_comp.alt_atom_id only. "
                                 f"It should be {_ref_atom_id}\n")

            # print(f'case 1. {_comp_id}:{atom_id} -> {comp_id}:{_ref_atom_id}')
            return True, comp_id, _ref_atom_id

        _ref_atom_ids = [a for a in ref_atom_ids if a[0] == atom_id[0] or a[0] == 'H' and atom_id[0] in pseProBeginCode]

        if len(_ref_atom_ids) == 0:
            if verbose:
                self.__lfh.write(f"+{self.__class_name__}.checkAtomNomenclature() ++ Warning  - {comp_id}:{atom_id} did not match with any atom in CCD. No candidates found\n")

            return False, None, None

        if len(atom_id) > 1 and atom_id[0] in ('1', '2', '3') and atom_id[1] == 'H' and atom_id[1:] + atom_id[0] in _ref_atom_ids:
            # print(f'case 2. {_comp_id}:{atom_id} -> {comp_id}:{atom_id[1:] + atom_id[0]}')
            return True, comp_id, atom_id[1:] + atom_id[0]

        if atom_id[-1] == "'" and self.getTypeOfCompId(comp_id)[2] and atom_id[:-1] in _ref_atom_ids:
            # print(f'case 3. {_comp_id}:{atom_id} -> {comp_id}:{atom_id[:-1]}')
            return True, comp_id, atom_id[:-1]

        _atom_id = translateToStdAtomName(atom_id, comp_id, refAtomIdList=_ref_atom_ids, ccU=self.__ccU, unambig=False)
        # prevent wrong atom_id mapping DC:H3 (extended imino proton) -> DC:H3' (DAOTHER-9317, 9511)
        if _atom_id in _ref_atom_ids and (("'" not in atom_id and "'" not in _atom_id) or ("'" in atom_id and "'" in _atom_id)):
            # print(f'case 4. {_comp_id}:{atom_id} -> {comp_id}:{_atom_id}')
            return True, comp_id, _atom_id

        if comp_id == 'DC' and atom_id == 'H3':  # DAOTHER-9198
            return True, 'DNR', 'HN3'

        if comp_id == 'C' and atom_id == 'H3':  # DAOTHER-9198 (RNA linking)
            return True, 'CH', 'HN3'

        if verbose:
            self.__lfh.write(f"+{self.__class_name__}.checkAtomNomenclature() ++ Warning  - {comp_id}:{atom_id} did not match with any atom in CCD, {_ref_atom_ids}\n")

        return False, None, None

    def __detectMethylProtonFromAtomNomenclature(self, comp_ids: List[str], atm_list: List[dict]):
        """ Detect methyl proton from atom nomenclature.
        """

        for comp_id in comp_ids:
            _list = [a for a in atm_list if a['comp_id'] == comp_id]

            h_list = [a for a in _list if a['atom_id'][0] in protonBeginCode and a['desc'] == 'isolated']

            if self.__ccU.updateChemCompDict(comp_id):
                c_h_bonds = collections.Counter([b[self.__ccU.ccbAtomId1] for b in self.__ccU.lastBonds
                                                 if b[self.__ccU.ccbAtomId1].startswith('C') and b[self.__ccU.ccbAtomId2][0] in protonBeginCode])

                for k, v in c_h_bonds.items():
                    if v == 3:

                        for a in _list:
                            if a['atom_id'] == k:
                                a['desc'] = 'methyl'

                        for a in h_list:
                            atom_id = a['atom_id']
                            if any(b for b in self.__ccU.lastBonds
                                   if b[self.__ccU.ccbAtomId1] == k and b[self.__ccU.ccbAtomId2] == atom_id):
                                a['desc'] = 'methyl'

            else:
                h_1 = [a['atom_id'][:-1] for a in h_list if a['atom_id'].endswith('1')]
                h_2 = [a['atom_id'][:-1] for a in h_list if a['atom_id'].endswith('2')]
                h_3 = [a['atom_id'][:-1] for a in h_list if a['atom_id'].endswith('3')]
                h_4 = [a['atom_id'][:-1] for a in h_list if a['atom_id'].endswith('4')]

                h_common = set(h_1) & set(h_2) & set(h_3) - set(h_4)

                for h in h_common:
                    for a in h_list:
                        atom_id = a['atom_id']
                        if atom_id in (h + '1', h + '2', h + '3'):
                            a['desc'] = 'methyl'

    def __detectGeminalProtonFromAtomNomenclature(self, comp_ids: List[str], atm_list: List[dict]):
        """ Detect geminal proton from atom nomenclature.
        """

        for comp_id in comp_ids:
            _list = [a for a in atm_list if a['comp_id'] == comp_id]

            h_list = [a for a in _list if a['atom_id'][0] in protonBeginCode and a['desc'] == 'isolated']

            if self.__ccU.updateChemCompDict(comp_id):
                aro_list = [a[self.__ccU.ccaAtomId] for a in self.__ccU.lastAtomList
                            if a[self.__ccU.ccaAromaticFlag] == 'Y']

                for a in _list:
                    if a['atom_id'] in aro_list:
                        a['desc'] = 'aroma'

                for aro in aro_list:
                    for a in h_list:
                        atom_id = a['atom_id']
                        if any(b for b in self.__ccU.lastBonds
                               if b[self.__ccU.ccbAtomId1] == aro and b[self.__ccU.ccbAtomId2] == atom_id):
                            a['desc'] = 'aroma'

                peptide_like = self.__ccU.peptideLike()

                leaving_atom_list = [a[self.__ccU.ccaAtomId] for a in self.__ccU.lastAtomList
                                     if not (a[self.__ccU.ccaLeavingAtomFlag] != 'Y'
                                             or (peptide_like
                                                 and a[self.__ccU.ccaNTerminalAtomFlag] == 'N'
                                                 and a[self.__ccU.ccaCTerminalAtomFlag] == 'N'))]

                cn_h_bonds = collections.Counter([b[self.__ccU.ccbAtomId1] for b in self.__ccU.lastBonds
                                                  if b[self.__ccU.ccbAtomId2][0] in protonBeginCode and b[self.__ccU.ccbAtomId2] not in leaving_atom_list])

                h_list = [a for a in _list if a['atom_id'][0] in protonBeginCode and a['desc'] == 'isolated']

                for k, v in cn_h_bonds.items():
                    if v == 2:
                        for a in h_list:
                            atom_id = a['atom_id']
                            if any(b for b in self.__ccU.lastBonds
                                   if b[self.__ccU.ccbAtomId1] == k and b[self.__ccU.ccbAtomId2] == atom_id):
                                a['desc'] = 'geminal'

                h_list = [a for a in _list if a['atom_id'][0] in protonBeginCode and a['desc'] == 'aroma']

                hvy_c_list = []

                pair = opp_idx = 0
                for h_1 in h_list:
                    if h_1['atom_id'][-1] in ('1', '2', '3'):
                        hvy_1 = next(b[self.__ccU.ccbAtomId1] for b in self.__ccU.lastBonds
                                     if b[self.__ccU.ccbAtomId2] == h_1['atom_id'])
                        for h_2 in h_list:
                            if h_2['atom_id'][-1] in ('1', '2', '3') and h_list.index(h_1) < h_list.index(h_2):
                                hvy_2 = next(b[self.__ccU.ccbAtomId1] for b in self.__ccU.lastBonds
                                             if b[self.__ccU.ccbAtomId2] == h_2['atom_id'])
                                if hvy_1[:-1] == hvy_2[:-1]:
                                    hvy_1_c = set(b[self.__ccU.ccbAtomId1] for b in self.__ccU.lastBonds
                                                  if b[self.__ccU.ccbAromaticFlag] == 'Y' and b[self.__ccU.ccbAtomId2] == hvy_1) |\
                                        set(b[self.__ccU.ccbAtomId2] for b in self.__ccU.lastBonds
                                            if b[self.__ccU.ccbAromaticFlag] == 'Y' and b[self.__ccU.ccbAtomId1] == hvy_1)
                                    hvy_2_c = set(b[self.__ccU.ccbAtomId1] for b in self.__ccU.lastBonds
                                                  if b[self.__ccU.ccbAromaticFlag] == 'Y' and b[self.__ccU.ccbAtomId2] == hvy_2) |\
                                        set(b[self.__ccU.ccbAtomId2] for b in self.__ccU.lastBonds
                                            if b[self.__ccU.ccbAromaticFlag] == 'Y' and b[self.__ccU.ccbAtomId1] == hvy_2)
                                    set_hvy_c = hvy_1_c & hvy_2_c
                                    if len(set_hvy_c) == 1:
                                        for hvy_c in set_hvy_c:
                                            hvy_c_list.append(hvy_c)
                                        pair += 1

                if pair > 0 and pair % 2 == 0:
                    hvy_c_set_in_ring = set()
                    for hvy_c_1 in hvy_c_list:
                        for hvy_c_2 in hvy_c_list:
                            if hvy_c_1 < hvy_c_2:
                                hvy_set_1 = set(b[self.__ccU.ccbAtomId1] for b in self.__ccU.lastBonds
                                                if b[self.__ccU.ccbAromaticFlag] == 'Y' and b[self.__ccU.ccbAtomId2] == hvy_c_1) |\
                                    set(b[self.__ccU.ccbAtomId2] for b in self.__ccU.lastBonds
                                        if b[self.__ccU.ccbAromaticFlag] == 'Y' and b[self.__ccU.ccbAtomId1] == hvy_c_1)
                                hvy_set_2 = set(b[self.__ccU.ccbAtomId1] for b in self.__ccU.lastBonds
                                                if b[self.__ccU.ccbAromaticFlag] == 'Y' and b[self.__ccU.ccbAtomId2] == hvy_c_2) |\
                                    set(b[self.__ccU.ccbAtomId2] for b in self.__ccU.lastBonds
                                        if b[self.__ccU.ccbAromaticFlag] == 'Y' and b[self.__ccU.ccbAtomId1] == hvy_c_2)

                                in_ring = False
                                for hvy_1 in hvy_set_1:
                                    if in_ring:
                                        break
                                    for hvy_2 in hvy_set_2:
                                        if in_ring:
                                            break
                                        if any(b for b in self.__ccU.lastBonds
                                               if b[self.__ccU.ccbAromaticFlag] == 'Y' and b[self.__ccU.ccbAtomId1] == hvy_1 and b[self.__ccU.ccbAtomId2] == hvy_2) or\
                                           any(b for b in self.__ccU.lastBonds
                                               if b[self.__ccU.ccbAromaticFlag] == 'Y' and b[self.__ccU.ccbAtomId1] == hvy_2 and b[self.__ccU.ccbAtomId2] == hvy_1):
                                            in_ring = True
                                if in_ring:
                                    hvy_c_set_in_ring.add(hvy_c_1)
                                    hvy_c_set_in_ring.add(hvy_c_2)

                    for h_1 in h_list:
                        if h_1['atom_id'][-1] in ('1', '2', '3'):
                            hvy_1 = next(b[self.__ccU.ccbAtomId1] for b in self.__ccU.lastBonds
                                         if b[self.__ccU.ccbAtomId2] == h_1['atom_id'])
                            for h_2 in h_list:
                                if h_2['atom_id'][-1] in ('1', '2', '3') and h_list.index(h_1) < h_list.index(h_2):
                                    hvy_2 = next(b[self.__ccU.ccbAtomId1] for b in self.__ccU.lastBonds
                                                 if b[self.__ccU.ccbAtomId2] == h_2['atom_id'])
                                    if hvy_1[:-1] == hvy_2[:-1]:
                                        hvy_1_c = set(b[self.__ccU.ccbAtomId1] for b in self.__ccU.lastBonds
                                                      if b[self.__ccU.ccbAromaticFlag] == 'Y' and b[self.__ccU.ccbAtomId2] == hvy_1) |\
                                            set(b[self.__ccU.ccbAtomId2] for b in self.__ccU.lastBonds
                                                if b[self.__ccU.ccbAromaticFlag] == 'Y' and b[self.__ccU.ccbAtomId1] == hvy_1)
                                        hvy_2_c = set(b[self.__ccU.ccbAtomId1] for b in self.__ccU.lastBonds
                                                      if b[self.__ccU.ccbAromaticFlag] == 'Y' and b[self.__ccU.ccbAtomId2] == hvy_2) |\
                                            set(b[self.__ccU.ccbAtomId2] for b in self.__ccU.lastBonds
                                                if b[self.__ccU.ccbAromaticFlag] == 'Y' and b[self.__ccU.ccbAtomId1] == hvy_2)
                                        if len(hvy_1_c & hvy_2_c & hvy_c_set_in_ring) > 0:
                                            opp_idx += 1
                                            h_1['desc'] = f'aroma-opposite-{opp_idx}'
                                            h_2['desc'] = f'aroma-opposite-{opp_idx}'
                                            for a in _list:
                                                if a['atom_id'] == hvy_1 or a['atom_id'] == hvy_2:
                                                    a['desc'] = f'aroma-opposite-{opp_idx}'

                if pair == 0 and peptide_like:
                    for h_1 in h_list:
                        hvy_1 = next(b[self.__ccU.ccbAtomId1] for b in self.__ccU.lastBonds
                                     if b[self.__ccU.ccbAtomId2] == h_1['atom_id'])
                        for h_2 in h_list:
                            hvy_2 = next(b[self.__ccU.ccbAtomId1] for b in self.__ccU.lastBonds
                                         if b[self.__ccU.ccbAtomId2] == h_2['atom_id'])
                            if hvy_1[:-1] == hvy_2[:-1]:
                                hvy_1_c = set(b[self.__ccU.ccbAtomId1] for b in self.__ccU.lastBonds
                                              if b[self.__ccU.ccbAromaticFlag] == 'Y' and b[self.__ccU.ccbAtomId2] == hvy_1) |\
                                    set(b[self.__ccU.ccbAtomId2] for b in self.__ccU.lastBonds
                                        if b[self.__ccU.ccbAromaticFlag] == 'Y' and b[self.__ccU.ccbAtomId1] == hvy_1)
                                hvy_2_c = set(b[self.__ccU.ccbAtomId1] for b in self.__ccU.lastBonds
                                              if b[self.__ccU.ccbAromaticFlag] == 'Y' and b[self.__ccU.ccbAtomId2] == hvy_2) |\
                                    set(b[self.__ccU.ccbAtomId2] for b in self.__ccU.lastBonds
                                        if b[self.__ccU.ccbAromaticFlag] == 'Y' and b[self.__ccU.ccbAtomId1] == hvy_2)
                                set_hvy_c = hvy_1_c & hvy_2_c
                                if len(set_hvy_c) == 1:
                                    for hvy_c in set_hvy_c:
                                        hvy_c_list.append(hvy_c)
                                    pair += 1

                    if pair > 0 and pair % 2 == 0:
                        hvy_c_set_in_ring = set()
                        for hvy_c_1 in hvy_c_list:
                            for hvy_c_2 in hvy_c_list:
                                if hvy_c_1 < hvy_c_2:
                                    hvy_set_1 = set(b[self.__ccU.ccbAtomId1] for b in self.__ccU.lastBonds
                                                    if b[self.__ccU.ccbAromaticFlag] == 'Y' and b[self.__ccU.ccbAtomId2] == hvy_c_1) |\
                                        set(b[self.__ccU.ccbAtomId2] for b in self.__ccU.lastBonds
                                            if b[self.__ccU.ccbAromaticFlag] == 'Y' and b[self.__ccU.ccbAtomId1] == hvy_c_1)
                                    hvy_set_2 = set(b[self.__ccU.ccbAtomId1] for b in self.__ccU.lastBonds
                                                    if b[self.__ccU.ccbAromaticFlag] == 'Y' and b[self.__ccU.ccbAtomId2] == hvy_c_2) |\
                                        set(b[self.__ccU.ccbAtomId2] for b in self.__ccU.lastBonds
                                            if b[self.__ccU.ccbAromaticFlag] == 'Y' and b[self.__ccU.ccbAtomId1] == hvy_c_2)

                                    in_ring = False
                                    for hvy_1 in hvy_set_1:
                                        if in_ring:
                                            break
                                        for hvy_2 in hvy_set_2:
                                            if in_ring:
                                                break
                                            if any(b for b in self.__ccU.lastBonds
                                                   if b[self.__ccU.ccbAromaticFlag] == 'Y' and b[self.__ccU.ccbAtomId1] == hvy_1 and b[self.__ccU.ccbAtomId2] == hvy_2) or\
                                               any(b for b in self.__ccU.lastBonds
                                                   if b[self.__ccU.ccbAromaticFlag] == 'Y' and b[self.__ccU.ccbAtomId1] == hvy_2 and b[self.__ccU.ccbAtomId2] == hvy_1):
                                                in_ring = True
                                    if in_ring:
                                        hvy_c_set_in_ring.add(hvy_c_1)
                                        hvy_c_set_in_ring.add(hvy_c_2)

                        for h_1 in h_list:
                            hvy_1 = next(b[self.__ccU.ccbAtomId1] for b in self.__ccU.lastBonds
                                         if b[self.__ccU.ccbAtomId2] == h_1['atom_id'])
                            for h_2 in h_list:
                                if h_list.index(h_1) < h_list.index(h_2):
                                    hvy_2 = next(b[self.__ccU.ccbAtomId1] for b in self.__ccU.lastBonds
                                                 if b[self.__ccU.ccbAtomId2] == h_2['atom_id'])
                                    if hvy_1[:-1] == hvy_2[:-1]:
                                        hvy_1_c = set(b[self.__ccU.ccbAtomId1] for b in self.__ccU.lastBonds
                                                      if b[self.__ccU.ccbAromaticFlag] == 'Y' and b[self.__ccU.ccbAtomId2] == hvy_1) |\
                                            set(b[self.__ccU.ccbAtomId2] for b in self.__ccU.lastBonds
                                                if b[self.__ccU.ccbAromaticFlag] == 'Y' and b[self.__ccU.ccbAtomId1] == hvy_1)
                                        hvy_2_c = set(b[self.__ccU.ccbAtomId1] for b in self.__ccU.lastBonds
                                                      if b[self.__ccU.ccbAromaticFlag] == 'Y' and b[self.__ccU.ccbAtomId2] == hvy_2) |\
                                            set(b[self.__ccU.ccbAtomId2] for b in self.__ccU.lastBonds
                                                if b[self.__ccU.ccbAromaticFlag] == 'Y' and b[self.__ccU.ccbAtomId1] == hvy_2)
                                        if len(hvy_1_c & hvy_2_c & hvy_c_set_in_ring) > 0:
                                            opp_idx += 1
                                            h_1['desc'] = f'aroma-opposite-{opp_idx}'
                                            h_2['desc'] = f'aroma-opposite-{opp_idx}'
                                            for a in _list:
                                                if a['atom_id'] == hvy_1 or a['atom_id'] == hvy_2:
                                                    a['desc'] = f'aroma-opposite-{opp_idx}'

            else:
                h_1 = [a['atom_id'][:-1] for a in h_list if a['atom_id'].endswith('1')]
                h_2 = [a['atom_id'][:-1] for a in h_list if a['atom_id'].endswith('2')]
                h_3 = [a['atom_id'][:-1] for a in h_list if a['atom_id'].endswith('3')]

                c_list = [a for a in _list if a['atom_id'].startswith('C')]

                c_1 = ['H' + a['atom_id'][1:-1] for a in c_list if a['atom_id'].endswith('1')]
                c_2 = ['H' + a['atom_id'][1:-1] for a in c_list if a['atom_id'].endswith('2')]
                c_3 = ['H' + a['atom_id'][1:-1] for a in c_list if a['atom_id'].endswith('3')]

                n_list = [a for a in _list if a['atom_id'].startswith('N')]

                n_1 = ['H' + a['atom_id'][1:-1] for a in n_list if a['atom_id'].endswith('1')]
                n_2 = ['H' + a['atom_id'][1:-1] for a in n_list if a['atom_id'].endswith('2')]
                n_3 = ['H' + a['atom_id'][1:-1] for a in n_list if a['atom_id'].endswith('3')]

                h_common = set(h_1) & set(h_2) - set(h_3)
                cn_common = set(c_1) & set(c_2) | set(c_1) & set(n_2) | set(n_1) & set(c_2)

                for h in h_common:
                    for a in h_list:
                        atom_id = a['atom_id']
                        if atom_id in (h + '1', h + '2'):
                            atom_id = 'N' + a['atom_id'][1:]
                            if not any(n for n in n_list if n['atom_id'] == atom_id):
                                a['desc'] = 'aroma' if h in cn_common and a['avg'] > 5.0 else 'geminal'

                h_common = set(h_2) & set(h_3) - set(h_1)
                cn_common = set(c_2) & set(c_3) | set(c_2) & set(n_3) | set(n_2) & set(c_3)

                for h in h_common:
                    for a in h_list:
                        atom_id = a['atom_id']
                        if atom_id in (h + '2', h + '3'):
                            atom_id = 'N' + a['atom_id'][1:]
                            if not any(n for n in n_list if n['atom_id'] == atom_id):
                                a['desc'] = 'aroma' if h in cn_common and a['avg'] > 5.0 else 'geminal'

                h_list = [a for a in _list if a['atom_id'][0] in protonBeginCode and a['desc'] == 'isolated']

                for h in h_list:
                    if h['avg'] > 5.0:
                        atom_id = 'C' + h['atom_id'][1:]
                        if any(c for c in c_list if c['atom_id'] == atom_id and c['avg'] > 95.0 and c['avg'] < 170.0):
                            h['desc'] = 'aroma'

                h_list = [a for a in _list if a['atom_id'][0] in protonBeginCode and a['desc'] == 'isolated']

                h_c = [a['atom_id'][:-1] for a in h_list if a['atom_id'].endswith("'") and not a['atom_id'].endswith("''")]
                h_cc = [a['atom_id'][:-2] for a in h_list if a['atom_id'].endswith("''")]

                c_c = ['H' + a['atom_id'][1:-1] for a in c_list if a['atom_id'].endswith("'") and not a['atom_id'].endswith("''")]
                c_cc = ['H' + a['atom_id'][1:-2] for a in c_list if a['atom_id'].endswith("''")]

                h_common = set(h_c) & set(h_cc) & set(c_c) - set(c_cc)

                for h in h_common:
                    for a in h_list:
                        atom_id = a['atom_id']
                        if atom_id in (h + "'", h + "''"):
                            atom_id = 'N' + a['atom_id'][1:]
                            if not any(n for n in n_list if n['atom_id'] == atom_id):
                                a['desc'] = 'geminal'

                h_list = [a for a in _list if a['atom_id'][0] in protonBeginCode and a['desc'] == 'aroma']

                h_1 = [a['atom_id'][:-1] for a in h_list if a['atom_id'].endswith('1')]
                h_2 = [a['atom_id'][:-1] for a in h_list if a['atom_id'].endswith('2')]
                h_3 = [a['atom_id'][:-1] for a in h_list if a['atom_id'].endswith('3')]

                h_common = set(h_1) & set(h_2)

                if len(h_common) > 0 and len(h_common) % 2 == 0:
                    for h in h_common:
                        for a in h_list:
                            atom_id = a['atom_id']
                            if atom_id in (h + '1', h + '2'):
                                a['desc'] = 'aroma-opposite'

                h_common = set(h_2) & set(h_3)

                if len(h_common) > 0 and len(h_common) % 2 == 0:
                    for h in h_common:
                        for a in h_list:
                            atom_id = a['atom_id']
                            if atom_id in (h + '2', h + '3'):
                                a['desc'] = 'aroma-opposite'

    def __detectGeminalCarbon(self, comp_ids: List[str], atm_list: List[dict]):
        """ Detect geminal carbon from atom nomenclature.
        """

        for comp_id in comp_ids:
            _list = [a for a in atm_list if a['comp_id'] == comp_id]

            if self.__ccU.updateChemCompDict(comp_id):
                methyl_c_list = [a['atom_id'] for a in _list if a['atom_id'].startswith('C') and a['desc'] == 'methyl']

                for methyl_c_1 in methyl_c_list:
                    for methyl_c_2 in methyl_c_list:
                        if methyl_c_list.index(methyl_c_1) < methyl_c_list.index(methyl_c_2):
                            hvy_1_c = set(b[self.__ccU.ccbAtomId2] for b in self.__ccU.lastBonds
                                          if b[self.__ccU.ccbAtomId1] == methyl_c_1 and b[self.__ccU.ccbAtomId2][0] not in protonBeginCode) |\
                                set(b[self.__ccU.ccbAtomId1] for b in self.__ccU.lastBonds
                                    if b[self.__ccU.ccbAtomId2] == methyl_c_1 and b[self.__ccU.ccbAtomId1][0] not in protonBeginCode)
                            hvy_2_c = set(b[self.__ccU.ccbAtomId2] for b in self.__ccU.lastBonds
                                          if b[self.__ccU.ccbAtomId1] == methyl_c_2 and b[self.__ccU.ccbAtomId2][0] not in protonBeginCode) |\
                                set(b[self.__ccU.ccbAtomId1] for b in self.__ccU.lastBonds
                                    if b[self.__ccU.ccbAtomId2] == methyl_c_2 and b[self.__ccU.ccbAtomId1][0] not in protonBeginCode)
                            hvy_common = hvy_1_c & hvy_2_c
                            if len(hvy_common) > 0:
                                for hvy_c in hvy_common:
                                    v = len([b for b in self.__ccU.lastBonds
                                             if b[self.__ccU.ccbAtomId1] == hvy_c and b[self.__ccU.ccbAtomId2] in methyl_c_list]) +\
                                        len([b for b in self.__ccU.lastBonds
                                             if b[self.__ccU.ccbAtomId2] == hvy_c and b[self.__ccU.ccbAtomId1] in methyl_c_list])

                                    if v in (2, 3):  # '3' accounts for M3L:NZ -> [CM1, CM2, CM3]
                                        for a in _list:
                                            if a['atom_id'] == methyl_c_1 or a['atom_id'] == methyl_c_2:
                                                a['desc'] = 'methyl-geminal'

                                                for methyl_h in [b[self.__ccU.ccbAtomId2] for b in self.__ccU.lastBonds
                                                                 if b[self.__ccU.ccbAtomId1] == methyl_c_1 and b[self.__ccU.ccbAtomId2][0] in protonBeginCode]:
                                                    for b in _list:
                                                        if b['atom_id'] == methyl_h:
                                                            b['desc'] = 'methyl-geminal'

                                                for methyl_h in [b[self.__ccU.ccbAtomId2] for b in self.__ccU.lastBonds
                                                                 if b[self.__ccU.ccbAtomId1] == methyl_c_2 and b[self.__ccU.ccbAtomId2][0] in protonBeginCode]:
                                                    for b in _list:
                                                        if b['atom_id'] == methyl_h:
                                                            b['desc'] = 'methyl-geminal'

            else:
                methyl_list = ['C' + a['atom_id'][1:-1] for a in _list
                               if a['atom_id'][0] in protonBeginCode and a['desc'] == 'methyl' and a['atom_id'].endswith('1')]

                methyl_1 = [a[:-1] for a in methyl_list if a.endswith('1')]
                methyl_2 = [a[:-1] for a in methyl_list if a.endswith('2')]
                methyl_3 = [a[:-1] for a in methyl_list if a.endswith('3')]

                c_list = [a for a in _list if a['atom_id'].startswith('C')]

                for c in c_list:
                    if c['atom_id'] in methyl_list:
                        c['desc'] = 'methyl'
                    elif c['avg'] > 95.0 and c['avg'] < 170.0:
                        c['desc'] = 'aroma'

                methyl_common = set(methyl_1) & set(methyl_2) - set(methyl_3)

                for m in methyl_common:
                    for c in c_list:
                        atom_id = c['atom_id']
                        if atom_id in (m + '1', m + '2'):
                            c['desc'] = 'methyl-geminal'
                            for h in [a for a in _list if a['atom_id'][0] in protonBeginCode and a['desc'] == 'methyl' and a['atom_id'].startswith('H' + atom_id[1:])]:
                                h['desc'] = 'methyl-geminal'

                aroma_list = ['C' + a['atom_id'][1:] for a in _list
                              if a['atom_id'][0] in protonBeginCode and a['desc'] == 'aroma']

                for c in c_list:
                    if c['atom_id'] in aroma_list:
                        c['desc'] = 'aroma'

                aroma_opposite_list = ['C' + a['atom_id'][1:] for a in _list
                                       if a['atom_id'][0] in protonBeginCode and a['desc'] == 'aroma-opposite']

                for c in c_list:
                    if c['atom_id'] in aroma_opposite_list:
                        c['desc'] = 'aroma-opposite'

    def __detectGeminalNitrogen(self, comp_ids: List[str], atm_list: List[dict]):
        """ Detect geminal nitrogen from atom nomenclature.
        """

        for comp_id in comp_ids:
            _list = [a for a in atm_list if a['comp_id'] == comp_id]

            geminal_n_list = ['N' + a['atom_id'][1:-1] for a in _list
                              if a['atom_id'][0] in protonBeginCode and a['desc'] == 'geminal' and a['atom_id'].endswith('1')]

            if self.__ccU.updateChemCompDict(comp_id):
                for geminal_n_1 in geminal_n_list:
                    for geminal_n_2 in geminal_n_list:
                        if geminal_n_list.index(geminal_n_1) < geminal_n_list.index(geminal_n_2):
                            hvy_1_c = set(b[self.__ccU.ccbAtomId2] for b in self.__ccU.lastBonds
                                          if b[self.__ccU.ccbAtomId1] == geminal_n_1 and b[self.__ccU.ccbAtomId2][0] not in protonBeginCode) |\
                                set(b[self.__ccU.ccbAtomId1] for b in self.__ccU.lastBonds
                                    if b[self.__ccU.ccbAtomId2] == geminal_n_1 and b[self.__ccU.ccbAtomId1][0] not in protonBeginCode)
                            hvy_2_c = set(b[self.__ccU.ccbAtomId2] for b in self.__ccU.lastBonds
                                          if b[self.__ccU.ccbAtomId1] == geminal_n_2 and b[self.__ccU.ccbAtomId2][0] not in protonBeginCode) |\
                                set(b[self.__ccU.ccbAtomId1] for b in self.__ccU.lastBonds
                                    if b[self.__ccU.ccbAtomId2] == geminal_n_2 and b[self.__ccU.ccbAtomId1][0] not in protonBeginCode)
                            hvy_common = hvy_1_c & hvy_2_c
                            if len(hvy_common) > 0:
                                for hvy_c in hvy_common:
                                    v = len([b for b in self.__ccU.lastBonds
                                             if b[self.__ccU.ccbAtomId1] == hvy_c and b[self.__ccU.ccbAtomId2] in geminal_n_list]) +\
                                        len([b for b in self.__ccU.lastBonds
                                             if b[self.__ccU.ccbAtomId2] == hvy_c and b[self.__ccU.ccbAtomId1] in geminal_n_list])

                                    if v == 2:
                                        for a in _list:
                                            if a['atom_id'] == geminal_n_1 or a['atom_id'] == geminal_n_2:
                                                a['desc'] = 'geminal'

            else:
                geminal_n_1 = [a[:-1] for a in geminal_n_list if a.endswith('1')]
                geminal_n_2 = [a[:-1] for a in geminal_n_list if a.endswith('2')]
                geminal_n_3 = [a[:-1] for a in geminal_n_list if a.endswith('3')]

                n_list = [a for a in _list if a['atom_id'].startswith('N')]

                for n in n_list:
                    if n['avg'] > 125.0:
                        n['desc'] = 'aroma'
                        atom_id = 'H' + n['atom_id'][1:]
                        try:
                            h = next(a for a in _list if a['atom_id'] == atom_id and a['desc'] == 'isolated')
                            h['desc'] = 'aroma'
                        except StopIteration:
                            pass

                geminal_common = set(geminal_n_1) & set(geminal_n_2) - set(geminal_n_3)

                for g in geminal_common:
                    for n in n_list:
                        atom_id = n['atom_id']
                        if atom_id in (g + '1', g + '2'):
                            n['desc'] = 'geminal'

    def __detectMajorResonance(self, comp_ids: List[str], atm_list: List[dict], primary_th: float, secondary_th: Optional[float] = None):
        """ Detect major resonance based on count of assignments.
        """

        for comp_id in comp_ids:
            _list = [a for a in atm_list if a['comp_id'] == comp_id]

            max_count = max(a['count'] for a in _list)

            for a in _list:
                a['norm_freq'] = float(f"{float(a['count']) / max_count:.3f}")
                if max_count >= self.max_count_th:
                    if a['count'] > max_count * primary_th:
                        a['primary'] = True
                    if (secondary_th is not None) and a['count'] > max_count * secondary_th:
                        a['secondary'] = True

    def writeStatAsPickleFiles(self):
        """ Write all BMRB chemical shift statistics as pickle files.
        """

        def write_stat_as_pickle(obj, file_name):
            """ Write BMRB chemical shift statistics as pickle file.
            """

            if isinstance(obj, list):

                with open(file_name, 'wb') as ofh:
                    pickle.dump(obj, ofh)

        write_stat_as_pickle(self.aa_filt, self.stat_dir + 'aa_filt.pkl')
        write_stat_as_pickle(self.aa_full, self.stat_dir + 'aa_full.pkl')

        write_stat_as_pickle(self.dna_filt, self.stat_dir + 'dna_filt.pkl')
        write_stat_as_pickle(self.dna_full, self.stat_dir + 'dna_full.pkl')

        write_stat_as_pickle(self.rna_filt, self.stat_dir + 'rna_filt.pkl')
        write_stat_as_pickle(self.rna_full, self.stat_dir + 'rna_full.pkl')

        self.loadOtherStatFromCsvFiles()

        write_stat_as_pickle(sorted(self.others, key=itemgetter('comp_id')), self.stat_dir + 'others.pkl')

    def loadStatFromPickleFiles(self) -> bool:
        """ Load all BMRB chemical shift statistics from pickle files if possible.
        """

        pickle_files = (self.stat_dir + 'aa_filt.pkl', self.stat_dir + 'aa_full.pkl',
                        self.stat_dir + 'dna_filt.pkl', self.stat_dir + 'dna_full.pkl',
                        self.stat_dir + 'rna_filt.pkl', self.stat_dir + 'rna_full.pkl',
                        self.stat_dir + 'others.pkl')

        for pickle_file in pickle_files:
            if not os.path.exists(pickle_file):
                return False

        def load_stat_from_pickle(file_name):
            """ Load BMRB chemical shift statistics from pickle file if possible.
            """

            if os.path.exists(file_name):

                with open(file_name, 'rb') as ifh:
                    return pickle.load(ifh)

            return []

        self.aa_filt = load_stat_from_pickle(self.stat_dir + 'aa_filt.pkl')
        self.aa_full = load_stat_from_pickle(self.stat_dir + 'aa_full.pkl')

        self.dna_filt = load_stat_from_pickle(self.stat_dir + 'dna_filt.pkl')
        self.dna_full = load_stat_from_pickle(self.stat_dir + 'dna_full.pkl')

        self.rna_filt = load_stat_from_pickle(self.stat_dir + 'rna_filt.pkl')
        self.rna_full = load_stat_from_pickle(self.stat_dir + 'rna_full.pkl')

        self.others = load_stat_from_pickle(self.stat_dir + 'others.pkl')

        self.__updateCompIdSet()

        return True

    def __updateCompIdSet(self):
        """ Update set of comp_id having BMRB chemical shift statistics.
        """

        self.__aa_comp_ids = set(item['comp_id'] for item in self.aa_filt)
        self.__dna_comp_ids = set(item['comp_id'] for item in self.dna_filt)
        self.__rna_comp_ids = set(item['comp_id'] for item in self.rna_filt)

        self.__all_comp_ids |= self.__aa_comp_ids
        self.__all_comp_ids |= self.__dna_comp_ids
        self.__all_comp_ids |= self.__rna_comp_ids

        self.__std_comp_ids = copy.copy(self.__all_comp_ids)

        self.__oth_comp_ids = set(item['comp_id'] for item in self.others)

        self.__all_comp_ids |= self.__oth_comp_ids

    def updateStatCsvFiles(self) -> bool:
        """ Update BMRB chemical shift statistics.
        """

        import requests  # pylint: disable=import-outside-toplevel
        import datetime  # pylint: disable=import-outside-toplevel
        from dateutil.parser import parse as parsedate  # pylint: disable=import-outside-toplevel

        def update_csv_file(csv_file):
            try:
                print(f'Downloading {self.url_for_bmrb_cs_stat_dir + csv_file} -> {self.stat_dir + csv_file} ...')
                r = requests.get(self.url_for_bmrb_cs_stat_dir + csv_file, timeout=5.0)
                with open(os.path.join(self.stat_dir + csv_file), 'w') as f_out:
                    f_out.write(r.text)
                if csv_file in ('rna_filt.csv', 'rna_full.csv'):
                    src_csv_file = os.path.join(self.stat_dir, csv_file)
                    dst_csv_file = src_csv_file + '~'
                    shutil.copyfile(src_csv_file, dst_csv_file)
                    with open(dst_csv_file, 'r') as f_in, \
                            open(src_csv_file, 'w') as f_out:
                        for line in f_in:
                            row = line.split(',')
                            if row[0] in ('A', 'C', 'G', 'U') and row[1] == '"H5"""':
                                continue
                            f_out.write(line)
                    os.remove(dst_csv_file)

            except Exception as e:
                self.__lfh.write(f"+{self.__class_name__}.updateStatCsvFiles() ++ Error  - {e}\n")

        for csv_file in self.csv_files:

            try:
                r = requests.head(self.url_for_bmrb_cs_stat_dir + csv_file, timeout=5.0)
            except Exception as e:
                self.__lfh.write(f"+{self.__class_name__}.updateStatCsvFiles() ++ Error  - {e}\n")
                return False

            if r.status_code != 200:
                self.__lfh.write(f"+{self.__class_name__}.updateStatCsvFiles() ++ Warning  - {r}\n")
                return False

            url_last_modified = parsedate(r.headers['Last-Modified']).astimezone()

            if not os.path.exists(self.stat_dir + csv_file):
                update_csv_file(csv_file)

            else:
                file_last_modified = datetime.datetime.fromtimestamp(os.path.getmtime(self.stat_dir + csv_file)).astimezone()
                if url_last_modified > file_last_modified:
                    update_csv_file(csv_file)
                else:
                    print(f'{self.stat_dir + csv_file} is update (Last-Modified: {url_last_modified})')

        return True

    def testAtomNomenclatureOfLibrary(self) -> bool:
        """ Report inconsistencies between BMRB chemical shift statistics and current CCD.
            @return: status (bool)
        """

        def check_bmrb_cs_stat(atm_list):

            ret = {'warning': 0, 'error': 0}

            comp_ids = set(item['comp_id'] for item in atm_list)

            for comp_id in comp_ids:

                if not self.__ccU.updateChemCompDict(comp_id):
                    print(f'[Error] {comp_id} does not match with any CCD ID.')
                    ret['error'] += 1
                    continue

                _list = [a for a in atm_list if a['comp_id'] == comp_id]

                ref_atom_ids = [a[self.__ccU.ccaAtomId] for a in self.__ccU.lastAtomList]
                cc_rel_status = self.__ccU.lastChemCompDict['_chem_comp.pdbx_release_status']

                if cc_rel_status == 'OBS' and '_chem_comp.pdbx_replaced_by' in self.__ccU.lastChemCompDict:
                    replaced_by = self.__ccU.lastChemCompDict['_chem_comp.pdbx_replaced_by']
                    if replaced_by not in emptyValue and self.__ccU.updateChemCompDict(replaced_by):
                        print(f'[Warning] {comp_id} is replaced by {replaced_by}.')

                        comp_id = replaced_by

                        ref_atom_ids = [a[self.__ccU.ccaAtomId] for a in self.__ccU.lastAtomList]
                        cc_rel_status = self.__ccU.lastChemCompDict['_chem_comp.pdbx_release_status']

                if len(ref_atom_ids) == 0 or cc_rel_status != 'REL':
                    print(f'[Error] {comp_id} is not valid CCD ID, status code: {cc_rel_status}.')
                    ret['error'] += 1
                    continue

                ref_alt_atom_ids = [a[self.__ccU.ccaAltAtomId] for a in self.__ccU.lastAtomList]

                peptide_like = self.__ccU.peptideLike()

                leaving_atom_list = [a[self.__ccU.ccaAtomId] for a in self.__ccU.lastAtomList
                                     if not (a[self.__ccU.ccaLeavingAtomFlag] != 'Y'
                                             or (peptide_like
                                                 and a[self.__ccU.ccaNTerminalAtomFlag] == 'N'
                                                 and a[self.__ccU.ccaCTerminalAtomFlag] == 'N'))]

                for a in _list:
                    atom_id = a['atom_id']

                    if atom_id in leaving_atom_list:
                        print(f'[Warning] {comp_id}:{atom_id} is leaving atom.')
                        ret['warning'] += 1

                    if atom_id in ref_atom_ids and atom_id in ref_alt_atom_ids:
                        _ref_atom_id = next(a[self.__ccU.ccaAtomId] for a in self.__ccU.lastAtomList
                                            if a[self.__ccU.ccaAltAtomId] == atom_id)
                        if atom_id == _ref_atom_id:
                            continue
                        print(f'[Warning] {comp_id}:{atom_id} is valid, but _chem_comp.alt_atom_id matched with different atom_id {_ref_atom_id}.')
                        ret['warning'] += 1

                    elif atom_id in ref_atom_ids and atom_id not in ref_alt_atom_ids:
                        continue

                    elif atom_id not in ref_alt_atom_ids and atom_id in ref_alt_atom_ids:
                        _ref_atom_id = next(a[self.__ccU.ccaAtomId] for a in self.__ccU.lastAtomList
                                            if a[self.__ccU.ccaAltAtomId] == atom_id)
                        print(f'[Error] {comp_id}:{atom_id} matched with _chem_comp.alt_atom_id only. It should be {_ref_atom_id}.')
                        ret['error'] += 1

                    else:
                        print(f'[Error] {comp_id}:{atom_id} did not match with any atom in CCD.')
                        ret['error'] += 1

            return ret

        status = True

        print('\nBMRB CS statistics name: aa_filt')
        result = check_bmrb_cs_stat(self.aa_filt)
        if result['warning'] == 0 and result['error'] == 0:
            print('OK')
        elif result['error'] > 0:
            print(f"{result['error']} Error, {result['warning']} Warning")
            status = False
        else:
            print(f"{result['warning']} Warning")

        print('\nBMRB CS statistics name: dna_filt')
        result = check_bmrb_cs_stat(self.dna_filt)
        if result['warning'] == 0 and result['error'] == 0:
            print('OK')
        elif result['error'] > 0:
            print(f"{result['error']} Error, {result['warning']} Warning")
            status = False
        else:
            print(f"{result['warning']} Warning")

        print('\nBMRB CS statistics name: rna_filt')
        result = check_bmrb_cs_stat(self.rna_filt)
        if result['warning'] == 0 and result['error'] == 0:
            print('OK')
        elif result['error'] > 0:
            print(f"{result['error']} Error, {result['warning']} Warning")
            status = False
        else:
            print(f"{result['warning']} Warning")

        print('\nBMRB CS statistics name: aa_full')
        result = check_bmrb_cs_stat(self.aa_full)
        if result['warning'] == 0 and result['error'] == 0:
            print('OK')
        elif result['error'] > 0:
            print(f"{result['error']} Error, {result['warning']} Warning")
            status = False
        else:
            print(f"{result['warning']} Warning")

        print('\nBMRB CS statistics name: dna_full')
        result = check_bmrb_cs_stat(self.dna_full)
        if result['warning'] == 0 and result['error'] == 0:
            print('OK')
        elif result['error'] > 0:
            print(f"{result['error']} Error, {result['warning']} Warning")
            status = False
        else:
            print(f"{result['warning']} Warning")

        print('\nBMRB CS statistics name: rna_full')
        result = check_bmrb_cs_stat(self.rna_full)
        if result['warning'] == 0 and result['error'] == 0:
            print('OK')
        elif result['error'] > 0:
            print(f"{result['error']} Error, {result['warning']} Warning")
            status = False
        else:
            print(f"{result['warning']} Warning")

        print('\nBMRB CS statistics name: others')
        result = check_bmrb_cs_stat(self.others)
        if result['warning'] == 0 and result['error'] == 0:
            print('OK')
        elif result['error'] > 0:
            print(f"{result['error']} Error, {result['warning']} Warning")
            status = False
        else:
            print(f"{result['warning']} Warning")

        return status

    def getAtomLikeNameSet(self, excl_minor_atom: bool = False, primary: bool = False, minimum_len: int = 1) -> Set[str]:
        """ Return atom like names of all standard residues.
        """

        name_set = set()

        name_set.add('HN')
        name_set.add('QR')
        name_set.add('O')

        for comp_id in self.__std_comp_ids:

            name_list = self.getAllAtoms(comp_id, excl_minor_atom, primary)
            methyl_list = self.getMethylAtoms(comp_id)

            for name in name_list:

                if len(name) < minimum_len:
                    continue

                name_set.add(name)

                ambig_code = self.getMaxAmbigCodeWoSetId(comp_id, name)

                if name in methyl_list:
                    if len(name) < 3:
                        continue
                    _name = name[:-1]
                    if _name[0] == 'H':
                        name_set.add('M' + _name[1:])
                        if ambig_code == 2:
                            name_set.add('QQ' + _name[1])
                        name_set.add(_name + '#')
                        name_set.add(_name + '%')
                        name_set.add(_name + '*')
                    elif ambig_code == 2:
                        name_set.add(_name + '#')
                        name_set.add(_name + '%')
                        name_set.add(_name + '*')

                elif ambig_code >= 2:
                    geminal_name = self.getGeminalAtom(comp_id, name)
                    if geminal_name is not None:
                        if len(name) < 3:
                            continue
                        _name = name[:-1]
                        if _name[0] == 'H':
                            name_set.add('Q' + _name[1:])
                            if geminal_name[:-1].isdigit():
                                name_set.add(_name + '#')
                                name_set.add(_name + '%')
                                name_set.add(_name + '*')
                                name_set.add(_name + 'X')
                                name_set.add(_name + 'Y')

            if self.__ccU.updateChemCompDict(comp_id):

                for a in self.__ccU.lastAtomList:

                    if a[self.__ccU.ccaLeavingAtomFlag] == 'Y':
                        continue

                    name = a[self.__ccU.ccaAtomId]

                    if len(name) < minimum_len:
                        continue

                    name_set.add(name)

        return name_set
