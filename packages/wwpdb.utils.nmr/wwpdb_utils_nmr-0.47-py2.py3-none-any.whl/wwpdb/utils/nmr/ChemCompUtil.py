##
# File: ChemCompUtil.py
# Date: 18-Feb-2022
#
# Updates:
# 27-Apr-2022  M. Yokochi - enable to use cached data for standard residues
# 11-Nov-2022  M. Yokochi - add getProtonsInSameGroup() (NMR restraint remediation)
# 13-Jun-2023  M. Yokochi - add getEffectiveFormulaWeight()
# 07-Dec-2023  M. Yokochi - add support for PTM items (backbone, n_terminal, c_terminal atom flags)
# 13-Dec-2023  M. Yokochi - add getAtomsBasedOnGreekLetterSystem(), peptideLike() and getTypeOfCompId() (DAOTHER-8945)
# 19-Apr-2024  M. Yokochi - add getRepMethyleneOrAminoProtons() and getNonRepMethyleneOrAminoProtons() (DAOTHER-9317)
# 24-Jun-2025  M. Yokochi - add hasIntervenedAtom() (DAOTHER-7829, 2ky8, D_1300056761)
##
""" Wrapper class for retrieving chemical component dictionary.
    @author: Masashi Yokochi
"""
__docformat__ = "restructuredtext en"
__author__ = "Masashi Yokochi"
__email__ = "yokochi@protein.osaka-u.ac.jp"
__license__ = "Apache License 2.0"
__version__ = "1.0.0"

import os
import sys
import pickle

from rmsd.calculate_rmsd import NAMES_ELEMENT, ELEMENT_WEIGHTS  # noqa: F401 pylint: disable=no-name-in-module, import-error, unused-import
from typing import IO, List, Tuple, Optional


try:
    from wwpdb.utils.config.ConfigInfo import getSiteId
    from wwpdb.utils.config.ConfigInfoApp import ConfigInfoAppCc
    from wwpdb.utils.nmr.io.ChemCompReader import (ChemCompReader,
                                                   ccd_id_pattern,
                                                   is_reserved_lig_code)
    from wwpdb.utils.nmr.AlignUtil import (emptyValue,
                                           monDict3,
                                           protonBeginCode)
    cICc = ConfigInfoAppCc(getSiteId())
    CC_CVS_PATH = cICc.get_site_cc_cvs_path()
except ImportError:
    from nmr.io.ChemCompReader import (ChemCompReader,
                                       ccd_id_pattern,
                                       is_reserved_lig_code)
    from nmr.AlignUtil import (emptyValue,
                               monDict3,
                               protonBeginCode)
    CC_CVS_PATH = os.path.dirname(__file__) + '/ligand_dict'  # need to setup 'ligand_dict' CCD resource for NMR restraint processing


class ChemCompUtil:
    """ Wrapper class for retrieving chemical component dictionary.
    """

    def __init__(self, verbose: bool = False, log: IO = sys.stderr):

        # pickle file name of cached dictionary for standard residues
        self.__cacheFile = os.path.dirname(__file__) + '/chem_comp_util/std_chem_comp.pkl'

        self.__ccR = ChemCompReader(verbose, log)
        self.__ccR.setCachePath(CC_CVS_PATH)

        self.lastCompId = None
        self.lastStatus = False
        self.lastChemCompDict = None
        self.lastAtomList = None
        self.lastBonds = None

        # taken from wwpdb.utils.nmr.io.ChemCompReader
        _chemCompAtomDict = [
            ('_chem_comp_atom.comp_id', '%s', 'str', ''),
            ('_chem_comp_atom.atom_id', '%s', 'str', ''),
            ('_chem_comp_atom.alt_atom_id', '%s', 'str', ''),
            ('_chem_comp_atom.type_symbol', '%s', 'str', ''),
            ('_chem_comp_atom.charge', '%s', 'str', ''),
            ('_chem_comp_atom.pdbx_align', '%s', 'str', ''),
            ('_chem_comp_atom.pdbx_aromatic_flag', '%s', 'str', ''),
            ('_chem_comp_atom.pdbx_leaving_atom_flag', '%s', 'str', ''),
            ('_chem_comp_atom.pdbx_stereo_config', '%s', 'str', ''),
            ('_chem_comp_atom.model_Cartn_x', '%s', 'str', ''),
            ('_chem_comp_atom.model_Cartn_y', '%s', 'str', ''),
            ('_chem_comp_atom.model_Cartn_z', '%s', 'str', ''),
            ('_chem_comp_atom.pdbx_model_Cartn_x_ideal', '%s', 'str', ''),
            ('_chem_comp_atom.pdbx_model_Cartn_y_ideal', '%s', 'str', ''),
            ('_chem_comp_atom.pdbx_model_Cartn_z_ideal', '%s', 'str', ''),
            ('_chem_comp_atom.pdbx_component_atom_id', '%s', 'str', ''),
            ('_chem_comp_atom.pdbx_component_comp_id', '%s', 'str', ''),
            ('_chem_comp_atom.pdbx_ordinal', '%s', 'str', ' '),
            ('_chem_comp_atom.pdbx_backbone_atom_flag', '%s', 'str', ''),
            ('_chem_comp_atom.pdbx_n_terminal_atom_flag', '%s', 'str', ''),
            ('_chem_comp_atom.pdbx_c_terminal_atom_flag', '%s', 'str', '')
        ]

        atomId = next(d for d in _chemCompAtomDict if d[0] == '_chem_comp_atom.atom_id')
        self.ccaAtomId = _chemCompAtomDict.index(atomId)

        altAtomId = next(d for d in _chemCompAtomDict if d[0] == '_chem_comp_atom.alt_atom_id')
        self.ccaAltAtomId = _chemCompAtomDict.index(altAtomId)

        aromaticFlag = next(d for d in _chemCompAtomDict if d[0] == '_chem_comp_atom.pdbx_aromatic_flag')
        self.ccaAromaticFlag = _chemCompAtomDict.index(aromaticFlag)

        leavingAtomFlag = next(d for d in _chemCompAtomDict if d[0] == '_chem_comp_atom.pdbx_leaving_atom_flag')
        self.ccaLeavingAtomFlag = _chemCompAtomDict.index(leavingAtomFlag)

        typeSymbol = next(d for d in _chemCompAtomDict if d[0] == '_chem_comp_atom.type_symbol')
        self.ccaTypeSymbol = _chemCompAtomDict.index(typeSymbol)

        cartnX = next(d for d in _chemCompAtomDict if d[0] == '_chem_comp_atom.model_Cartn_x')
        cartnY = next(d for d in _chemCompAtomDict if d[0] == '_chem_comp_atom.model_Cartn_y')
        cartnZ = next(d for d in _chemCompAtomDict if d[0] == '_chem_comp_atom.model_Cartn_z')
        self.ccaCartnX = _chemCompAtomDict.index(cartnX)
        self.ccaCartnY = _chemCompAtomDict.index(cartnY)
        self.ccaCartnZ = _chemCompAtomDict.index(cartnZ)

        backboneAtomFlag = next(d for d in _chemCompAtomDict if d[0] == '_chem_comp_atom.pdbx_backbone_atom_flag')
        self.ccaBackboneAtomFlag = _chemCompAtomDict.index(backboneAtomFlag)

        nTerminalAtomFlag = next(d for d in _chemCompAtomDict if d[0] == '_chem_comp_atom.pdbx_n_terminal_atom_flag')
        self.ccaNTerminalAtomFlag = _chemCompAtomDict.index(nTerminalAtomFlag)

        cTerminalAtomFlag = next(d for d in _chemCompAtomDict if d[0] == '_chem_comp_atom.pdbx_c_terminal_atom_flag')
        self.ccaCTerminalAtomFlag = _chemCompAtomDict.index(cTerminalAtomFlag)

        # taken from wwpdb.utils.nmr.io.ChemCompReader
        _chemCompBondDict = [
            ('_chem_comp_bond.comp_id', '%s', 'str', ''),
            ('_chem_comp_bond.atom_id_1', '%s', 'str', ''),
            ('_chem_comp_bond.atom_id_2', '%s', 'str', ''),
            ('_chem_comp_bond.value_order', '%s', 'str', ''),
            ('_chem_comp_bond.pdbx_aromatic_flag', '%s', 'str', ''),
            ('_chem_comp_bond.pdbx_stereo_config', '%s', 'str', ''),
            ('_chem_comp_bond.pdbx_ordinal', '%s', 'str', '')
        ]

        atomId1 = next(d for d in _chemCompBondDict if d[0] == '_chem_comp_bond.atom_id_1')
        self.ccbAtomId1 = _chemCompBondDict.index(atomId1)

        atomId2 = next(d for d in _chemCompBondDict if d[0] == '_chem_comp_bond.atom_id_2')
        self.ccbAtomId2 = _chemCompBondDict.index(atomId2)

        aromaticFlag = next(d for d in _chemCompBondDict if d[0] == '_chem_comp_bond.pdbx_aromatic_flag')
        self.ccbAromaticFlag = _chemCompBondDict.index(aromaticFlag)

        valueOrder = next(d for d in _chemCompBondDict if d[0] == '_chem_comp_bond.value_order')
        self.ccbValueOrder = _chemCompBondDict.index(valueOrder)

        def load_dict_from_pickle(file_name):
            """ Load cached dictionary from pickle file.
            """

            if os.path.exists(file_name):

                with open(file_name, 'rb') as ifh:
                    return pickle.load(ifh)

            return {}

        self.__cachedDict = load_dict_from_pickle(self.__cacheFile)
        self.__failedCompId = []

    def updateChemCompDict(self, compId: str, ligand: bool = True) -> bool:
        """ Update CCD information for a given comp_id.
            @return: True for successfully update CCD information or False for the case a given comp_id does not exist in CCD
        """

        if compId in emptyValue:
            return False

        compId = compId.upper()

        if not ccd_id_pattern.match(compId) or (not ligand and is_reserved_lig_code(compId)):
            return False

        if compId in self.__failedCompId:
            return False

        if compId != self.lastCompId:
            self.lastStatus = False if '_' in compId else self.__ccR.setCompId(compId, ligand)
            self.lastCompId = compId

            if self.lastStatus:
                if compId in self.__cachedDict:
                    self.lastChemCompDict = self.__cachedDict[compId]['chem_comp']
                    self.lastAtomList = self.__cachedDict[compId]['chem_comp_atom']
                    self.lastBonds = self.__cachedDict[compId]['chem_comp_bond']
                else:
                    self.lastChemCompDict = self.__ccR.getChemCompDict()
                    self.lastAtomList = self.__ccR.getAtomList()
                    self.lastBonds = self.__ccR.getBonds()
                    self.__cachedDict[compId] = {'chem_comp': self.lastChemCompDict,
                                                 'chem_comp_atom': self.lastAtomList,
                                                 'chem_comp_bond': self.lastBonds}

            else:
                self.__failedCompId.append(compId)

        return self.lastStatus

    def getMethylAtoms(self, compId: str) -> List[str]:
        """ Return atoms in methyl group of a given comp_id.
        """

        if compId != self.lastCompId and not self.updateChemCompDict(compId):
            return []

        atmList = []

        carbons = (a[self.ccaAtomId] for a in self.lastAtomList if a[self.ccaTypeSymbol] == 'C')

        for carbon in carbons:
            protons = [(b[self.ccbAtomId1] if b[self.ccbAtomId1] != carbon else b[self.ccbAtomId2])
                       for b in self.lastBonds
                       if (b[self.ccbAtomId1] == carbon and b[self.ccbAtomId2][0] in protonBeginCode)
                       or (b[self.ccbAtomId2] == carbon and b[self.ccbAtomId1][0] in protonBeginCode)]
            if len(protons) != 3:
                continue
            atmList.append(carbon)
            atmList.extend(protons)

        return atmList

    def getMethylProtons(self, compId: str) -> List[str]:
        """ Return all protons in methyl group of a given comp_id.
        """

        if compId != self.lastCompId and not self.updateChemCompDict(compId):
            return []

        atmList = []

        carbons = (a[self.ccaAtomId] for a in self.lastAtomList if a[self.ccaTypeSymbol] == 'C')

        for carbon in carbons:
            protons = [(b[self.ccbAtomId1] if b[self.ccbAtomId1] != carbon else b[self.ccbAtomId2])
                       for b in self.lastBonds
                       if (b[self.ccbAtomId1] == carbon and b[self.ccbAtomId2][0] in protonBeginCode)
                       or (b[self.ccbAtomId2] == carbon and b[self.ccbAtomId1][0] in protonBeginCode)]
            if len(protons) != 3:
                continue
            atmList.extend(protons)

        return atmList

    def getRepMethylProtons(self, compId: str) -> List[str]:
        """ Return representative protons in methyl group of a given comp_id.
        """

        if compId != self.lastCompId and not self.updateChemCompDict(compId):
            return []

        atmList = []

        carbons = (a[self.ccaAtomId] for a in self.lastAtomList if a[self.ccaTypeSymbol] == 'C')

        for carbon in carbons:
            protons = [(b[self.ccbAtomId1] if b[self.ccbAtomId1] != carbon else b[self.ccbAtomId2])
                       for b in self.lastBonds
                       if (b[self.ccbAtomId1] == carbon and b[self.ccbAtomId2][0] in protonBeginCode)
                       or (b[self.ccbAtomId2] == carbon and b[self.ccbAtomId1][0] in protonBeginCode)]
            if len(protons) != 3:
                continue
            atmList.append(protons[0])

        return atmList

    def getNonRepMethylProtons(self, compId: str) -> List[str]:
        """ Return non-representative protons in methyl group of a given comp_id.
        """

        if compId != self.lastCompId and not self.updateChemCompDict(compId):
            return []

        atmList = []

        carbons = (a[self.ccaAtomId] for a in self.lastAtomList if a[self.ccaTypeSymbol] == 'C')

        for carbon in carbons:
            protons = [(b[self.ccbAtomId1] if b[self.ccbAtomId1] != carbon else b[self.ccbAtomId2])
                       for b in self.lastBonds
                       if (b[self.ccbAtomId1] == carbon and b[self.ccbAtomId2][0] in protonBeginCode)
                       or (b[self.ccbAtomId2] == carbon and b[self.ccbAtomId1][0] in protonBeginCode)]
            if len(protons) != 3:
                continue
            atmList.extend(protons[1:])

        return atmList

    def getRepMethyleneOrAminoProtons(self, compId: str) -> List[str]:
        """ Return representative protons in methylene/amino group of a given comp_id.
        """

        if compId != self.lastCompId and not self.updateChemCompDict(compId):
            return []

        atmList = []

        corns = (a[self.ccaAtomId] for a in self.lastAtomList if a[self.ccaTypeSymbol] in ('C', 'N'))

        for corn in corns:
            protons = [(b[self.ccbAtomId1] if b[self.ccbAtomId1] != corn else b[self.ccbAtomId2])
                       for b in self.lastBonds
                       if (b[self.ccbAtomId1] == corn and b[self.ccbAtomId2][0] in protonBeginCode)
                       or (b[self.ccbAtomId2] == corn and b[self.ccbAtomId1][0] in protonBeginCode)]
            if len(protons) != 2:
                continue
            atmList.append(protons[0])

        return atmList

    def getNonRepMethyleneOrAminoProtons(self, compId: str) -> List[str]:
        """ Return non-representative protons in methylene/amino group of a given comp_id.
        """

        if compId != self.lastCompId and not self.updateChemCompDict(compId):
            return []

        atmList = []

        corns = (a[self.ccaAtomId] for a in self.lastAtomList if a[self.ccaTypeSymbol] in ('C', 'N'))

        for corn in corns:
            protons = [(b[self.ccbAtomId1] if b[self.ccbAtomId1] != corn else b[self.ccbAtomId2])
                       for b in self.lastBonds
                       if (b[self.ccbAtomId1] == corn and b[self.ccbAtomId2][0] in protonBeginCode)
                       or (b[self.ccbAtomId2] == corn and b[self.ccbAtomId1][0] in protonBeginCode)]
            if len(protons) != 2:
                continue
            atmList.extend(protons[1:])

        return atmList

    def getRepAminoProtons(self, compId: str) -> List[str]:
        """ Return representative protons in amino group of a given comp_id.
        """

        if compId != self.lastCompId and not self.updateChemCompDict(compId):
            return []

        atmList = []

        ns = (a[self.ccaAtomId] for a in self.lastAtomList if a[self.ccaTypeSymbol] == 'N')

        for n in ns:
            protons = [(b[self.ccbAtomId1] if b[self.ccbAtomId1] != n else b[self.ccbAtomId2])
                       for b in self.lastBonds
                       if (b[self.ccbAtomId1] == n and b[self.ccbAtomId2][0] in protonBeginCode)
                       or (b[self.ccbAtomId2] == n and b[self.ccbAtomId1][0] in protonBeginCode)]
            if len(protons) != 2:
                continue
            atmList.append(protons[0])

        return atmList

    def getNonRepAminoProtons(self, compId: str) -> List[str]:
        """ Return non-representative protons in amino group of a given comp_id.
        """

        if compId != self.lastCompId and not self.updateChemCompDict(compId):
            return []

        atmList = []

        ns = (a[self.ccaAtomId] for a in self.lastAtomList if a[self.ccaTypeSymbol] == 'N')

        for n in ns:
            protons = [(b[self.ccbAtomId1] if b[self.ccbAtomId1] != n else b[self.ccbAtomId2])
                       for b in self.lastBonds
                       if (b[self.ccbAtomId1] == n and b[self.ccbAtomId2][0] in protonBeginCode)
                       or (b[self.ccbAtomId2] == n and b[self.ccbAtomId1][0] in protonBeginCode)]
            if len(protons) != 2:
                continue
            atmList.extend(protons[1:])

        return atmList

    def getImideProtons(self, compId: str) -> List[str]:
        """ Return imide protons of a given comp_id.
        """

        if compId != self.lastCompId and not self.updateChemCompDict(compId):
            return []

        atmList = []

        ns = (a[self.ccaAtomId] for a in self.lastAtomList if a[self.ccaTypeSymbol] == 'N')

        for n in ns:
            protons = [(b[self.ccbAtomId1] if b[self.ccbAtomId1] != n else b[self.ccbAtomId2])
                       for b in self.lastBonds
                       if (b[self.ccbAtomId1] == n and b[self.ccbAtomId2][0] in protonBeginCode)
                       or (b[self.ccbAtomId2] == n and b[self.ccbAtomId1][0] in protonBeginCode)]
            if len(protons) != 1:
                continue
            acyl_c = [(b[self.ccbAtomId1] if b[self.ccbAtomId1] != n else b[self.ccbAtomId2])
                      for b in self.lastBonds
                      if (b[self.ccbAtomId1] == n and b[self.ccbAtomId2][0] == 'C')
                      or (b[self.ccbAtomId2] == n and b[self.ccbAtomId1][0] == 'C')]
            if len(acyl_c) != 2:
                continue
            acyl_o = [(b[self.ccbAtomId1] if b[self.ccbAtomId1] not in acyl_c else b[self.ccbAtomId2])
                      for b in self.lastBonds if b[self.ccbValueOrder] == 'DOUB'
                      and ((b[self.ccbAtomId1] in acyl_c and b[self.ccbAtomId2][0] == 'O')
                           or (b[self.ccbAtomId2] in acyl_c and b[self.ccbAtomId1][0] == 'O'))]
            if len(acyl_o) != 2:
                continue
            atmList.append(protons[0])

        return atmList

    def getBondedAtoms(self, compId: str, atomId: str, exclProton: bool = False, onlyProton: bool = False) -> List[str]:
        """ Return bonded atoms to a given atom.
        """

        if compId != self.lastCompId and not self.updateChemCompDict(compId):
            return []

        bondedAtoms = [(b[self.ccbAtomId1] if b[self.ccbAtomId1] != atomId else b[self.ccbAtomId2])
                       for b in self.lastBonds if atomId in (b[self.ccbAtomId1], b[self.ccbAtomId2])]

        if not exclProton and not onlyProton:
            return bondedAtoms

        allProtons = [a[self.ccaAtomId] for a in self.lastAtomList if a[self.ccaTypeSymbol] == 'H']

        return [a for a in bondedAtoms if (exclProton and a not in allProtons) or (onlyProton and a in allProtons)]

    def getProtonsInSameGroup(self, compId: str, atomId: str, exclSelf: bool = False) -> List[str]:
        """ Return protons in the same group of a given comp_id and atom_id.
        """

        if compId != self.lastCompId and not self.updateChemCompDict(compId):
            return []

        bondedTo = self.getBondedAtoms(compId, atomId)

        if len(bondedTo) == 0:
            return []

        attached = self.getBondedAtoms(compId, bondedTo[0], onlyProton=True)

        return [p for p in attached if (exclSelf and p != atomId) or not exclSelf]

    def getAtomsBasedOnGreekLetterSystem(self, compId: str, atomId: str) -> List[str]:
        """ Return atoms match with greek letter system of a given comp_id.
        """

        if len(atomId) < 2:
            return []

        elem = atomId[0]

        if elem not in ('H', 'C', 'N', 'O', 'S', 'P'):
            return []

        greekLetter = atomId[1]

        if greekLetter not in ('A', 'B', 'G', 'D', 'E', 'Z', 'H'):
            return []

        if compId != self.lastCompId and not self.updateChemCompDict(compId):
            return []

        touched = ['N', 'C', 'O', 'OXT']
        parents = ['CA']

        if not any(a[self.ccaAtomId] == 'CA' for a in self.lastAtomList):
            if not any(a[self.ccaAtomId] == 'C' for a in self.lastAtomList):  # ACA:QA -> H21, H22 (5nwu)
                return []
            bonded = [(b[self.ccbAtomId1] if b[self.ccbAtomId1] != 'C' else b[self.ccbAtomId2])
                      for b in self.lastBonds if 'C' in (b[self.ccbAtomId1], b[self.ccbAtomId2])]
            if len(bonded) == 0:
                return []
            parents = [b for b in bonded if b not in touched]
            if len(parents) == 0:
                return []

        for letter in ['A', 'B', 'G', 'D', 'E', 'Z', 'H']:

            if greekLetter == letter:
                atoms = parents
                for p in parents:
                    atoms.extend(self.getBondedAtoms(compId, p, onlyProton=True))
                return sorted(list(set(a for a in atoms if a[0] == elem)))

            touched.extend(parents)

            _parents = []
            for p in parents:
                _parents.extend([a for a in self.getBondedAtoms(compId, p, exclProton=True) if a not in touched])

            if len(_parents) == 0:
                return []

            parents = list(set(_parents))

        return []

    def hasBond(self, compId: str, atomId1: str, atomId2: str) -> bool:
        """ Return whether given two atoms are connected by a covalent bond.
        """

        return atomId2 in self.getBondedAtoms(compId, atomId1)

    def hasIntervenedAtom(self, compId: str, atomId1: str, atomId2: str) -> bool:
        """ Return whether given two atoms are connected through an intervened atom.
        """

        return len(set(self.getBondedAtoms(compId, atomId1)) & set(self.getBondedAtoms(compId, atomId2))) == 1

    def peptideLike(self, compId: Optional[str] = None) -> bool:
        """ Return whether a given comp_id is peptide-like component.
        """

        if compId is not None:
            if not self.updateChemCompDict(compId):
                return False

        ctype = self.lastChemCompDict['_chem_comp.type'].upper()

        if 'PEPTIDE' in ctype:
            return True

        if 'DNA' in ctype or 'RNA' in ctype or 'SACCHARIDE' in ctype:
            return False

        peptide_like = len([a for a in self.lastAtomList
                            if a[self.ccaAtomId] in ("C", "CA", "H", "HA", "HA2", "HA3", "N", "O")])

        nucleotide_like = len([a for a in self.lastAtomList
                               if a[self.ccaAtomId] in ("C1'", "C2'", "C3'", "C4'", "C5'",
                                                        "H1'", "H2'", "H2''", "H3'", "H4'", "H5'", "H5''", "HO2'",
                                                        "P", "OP1", "OP2", "O5'", "O3'")])

        carbohydrate_like = len([a for a in self.lastAtomList
                                 if a[self.ccaAtomId] in ("C1", "C2", "C3", "C4", "C5", "C6",
                                                          "H1", "H2", "H3", "H4", "H5", "H61", "H62",
                                                          "O1", "O4", "O6")])

        return peptide_like > nucleotide_like and peptide_like > carbohydrate_like

    def getTypeOfCompId(self, compId: Optional[str] = None) -> Tuple[bool, bool, bool]:
        """ Return type of a given comp_id.
            @return: array of bool: peptide, nucleotide, carbohydrate
        """

        if compId is not None:
            if not self.updateChemCompDict(compId):
                return False, False, False

        results = [False] * 3

        ctype = self.lastChemCompDict['_chem_comp.type'].upper()

        if 'PEPTIDE' in ctype:
            results[0] = True
            return results

        if 'DNA' in ctype or 'RNA' in ctype:
            results[1] = True
            return results

        if 'SACCHARIDE' in ctype:
            results[2] = True
            return results

        peptide_like = len([a for a in self.lastAtomList
                            if a[self.ccaAtomId] in ("C", "CA", "H", "HA", "HA2", "HA3", "N", "O")])

        nucleotide_like = len([a for a in self.lastAtomList
                               if a[self.ccaAtomId] in ("C1'", "C2'", "C3'", "C4'", "C5'",
                                                        "H1'", "H2'", "H2''", "H3'", "H4'", "H5'", "H5''", "HO2'",
                                                        "P", "OP1", "OP2", "O5'", "O3'")])

        carbohydrate_like = len([a for a in self.lastAtomList
                                 if a[self.ccaAtomId] in ("C1", "C2", "C3", "C4", "C5", "C6",
                                                          "H1", "H2", "H3", "H4", "H5", "H61", "H62",
                                                          "O1", "O4", "O6")])

        results[0] = peptide_like > nucleotide_like and peptide_like > carbohydrate_like
        results[1] = nucleotide_like > peptide_like and nucleotide_like > carbohydrate_like
        results[2] = carbohydrate_like > peptide_like and carbohydrate_like > nucleotide_like

        return results

    def getEffectiveFormulaWeight(self, compId: str) -> float:
        """ Return effective formula weight of a given comp_id.
        """

        if not self.updateChemCompDict(compId):
            return 0.0

        if '_chem_comp.formula_weight' not in self.lastChemCompDict:
            return 0.0

        try:

            fw = float(self.lastChemCompDict['_chem_comp.formula_weight'])

        except ValueError:
            return 0.0

        peptide_like = self.peptideLike()

        leavingTypeSymbols = [a[self.ccaTypeSymbol] for a in self.lastAtomList
                              if not (a[self.ccaLeavingAtomFlag] != 'Y'
                                      or (peptide_like
                                          and a[self.ccaNTerminalAtomFlag] == 'N'
                                          and a[self.ccaCTerminalAtomFlag] == 'N'))]

        try:

            for symbol in leavingTypeSymbols:
                fw -= ELEMENT_WEIGHTS[NAMES_ELEMENT[symbol.title()]]

        except KeyError:
            return 0.0

        return fw

    def write_std_dict_as_pickle(self):
        """ Write dictionary for standard residues as pickle file.
        """

        for compId in monDict3:
            self.updateChemCompDict(compId)

        def write_dict_as_pickle(obj, file_name):
            """ Write dictionary as pickle file.
            """

            if isinstance(obj, dict):

                with open(file_name, 'wb') as ofh:
                    pickle.dump(obj, ofh)

        write_dict_as_pickle(self.__cachedDict, self.__cacheFile)
