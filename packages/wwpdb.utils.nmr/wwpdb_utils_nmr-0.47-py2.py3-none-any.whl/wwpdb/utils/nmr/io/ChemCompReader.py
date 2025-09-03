##
# File: ChemCompReader.py
# Date: 31-May-2010  John Westbrook
#
# Update:
# 06-Aug-2010 - jdw - generalized construction of methods to apply to any category
#                     add accessors for lists of dictionaries
# 12-May-2011 - rps - added check for None when asking for category Object in __getDataList()
# 24-Oct-2012 - rps - updated to reflect reorganization of modules in pdbx packages
# 17-Jan-2025 - my  - added is_reserved_lig_code() from AlignUtil.py (DAOTHER-7204, 7388)
##
""" A collection of classes parsing CCD CIF files.
"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook, Masashi Yokochi"
__email__ = "jwest@rcsb.rutgers.edu, yokochi@protein.osaka-u.ac.jp"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "1.0.3"

import sys
import os
import re

from mmcif.api.PdbxContainers import DataContainer
from mmcif.io.PdbxReader import PdbxReader

from typing import IO, List, Optional

try:
    from wwpdb.utils.nmr.AlignUtil import emptyValue
except ImportError:
    from nmr.AlignUtil import emptyValue


ccd_id_pattern = re.compile(r'(\w{1,3}|\w{5})')


def is_reserved_lig_code(comp_id: str) -> bool:
    """ Return a given comp_id is reserved for new ligands. (DAOTHER-7204, 7388)
    """

    if comp_id in ('LIG', 'DRG', 'INH'):
        return True

    if len(comp_id) == 2 and comp_id[0].isdigit() and comp_id[1].isdigit() and comp_id != '00':
        return True

    return False


class ChemCompReader:
    """ Accessor methods for parsing CCD CIF files.
    """

    def __init__(self, verbose: bool = True, log: IO = sys.stdout):
        self.__class_name__ = self.__class__.__name__
        self.__version__ = __version__

        self.__verbose = verbose
        self.__lfh = log
        self.__debug = False

        # the primary datablock
        self.__dBlock = None

        # the top file tree of CCD
        self.__topCachePath = None

        # the current file path
        self.__filePath = None

        # the current compId
        self.__compId = None

        # the compId of the current datablock
        self.__lastCompId = None

        # items of CCD category
        self.__itemDict = {
            'chem_comp': [
                ('_chem_comp.id', '%s', 'str', ''),
                ('_chem_comp.name', '%s', 'str', ''),
                ('_chem_comp.type', '%s', 'str', ''),
                ('_chem_comp.pdbx_type', '%s', 'str', ''),
                ('_chem_comp.formula', '%s', 'str', ''),
                ('_chem_comp.mon_nstd_parent_comp_id', '%s', 'str', ''),
                ('_chem_comp.pdbx_synonyms', '%s', 'str', ''),
                ('_chem_comp.pdbx_formal_charge', '%s', 'str', ''),
                ('_chem_comp.pdbx_initial_date', '%s', 'str', ''),
                ('_chem_comp.pdbx_modified_date', '%s', 'str', ''),
                ('_chem_comp.pdbx_ambiguous_flag', '%s', 'str', ''),
                ('_chem_comp.pdbx_release_status', '%s', 'str', ''),
                ('_chem_comp.pdbx_replaced_by', '%s', 'str', ''),
                ('_chem_comp.pdbx_replaces', '%s', 'str', ''),
                ('_chem_comp.formula_weight', '%s', 'str', ''),
                ('_chem_comp.one_letter_code', '%s', 'str', ''),
                ('_chem_comp.three_letter_code', '%s', 'str', ''),
                ('_chem_comp.pdbx_model_coordinates_details', '%s', 'str', ''),
                ('_chem_comp.pdbx_model_coordinates_missing_flag', '%s', 'str', ''),
                ('_chem_comp.pdbx_ideal_coordinates_details', '%s', 'str', ''),
                ('_chem_comp.pdbx_ideal_coordinates_missing_flag', '%s', 'str', ''),
                ('_chem_comp.pdbx_model_coordinates_db_code', '%s', 'str', ''),
                ('_chem_comp.pdbx_subcomponent_list', '%s', 'str', ''),
                ('_chem_comp.pdbx_processing_site', '%s', 'str', '')
            ],
            'chem_comp_atom': [
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
                ('_chem_comp_atom.pdbx_ordinal', '%s', 'str', ''),
                ('_chem_comp_atom.pdbx_backbone_atom_flag', '%s', 'str', ''),
                ('_chem_comp_atom.pdbx_n_terminal_atom_flag', '%s', 'str', ''),
                ('_chem_comp_atom.pdbx_c_terminal_atom_flag', '%s', 'str', '')
            ],
            'chem_comp_bond': [
                ('_chem_comp_bond.comp_id', '%s', 'str', ''),
                ('_chem_comp_bond.atom_id_1', '%s', 'str', ''),
                ('_chem_comp_bond.atom_id_2', '%s', 'str', ''),
                ('_chem_comp_bond.value_order', '%s', 'str', ''),
                ('_chem_comp_bond.pdbx_aromatic_flag', '%s', 'str', ''),
                ('_chem_comp_bond.pdbx_stereo_config', '%s', 'str', ''),
                ('_chem_comp_bond.pdbx_ordinal', '%s', 'str', '')
            ],
            'chem_comp_descriptor': [
                ('_pdbx_chem_comp_descriptor.comp_id', '%s', 'str', ''),
                ('_pdbx_chem_comp_descriptor.type', '%s', 'str', ''),
                ('_pdbx_chem_comp_descriptor.program', '%s', 'str', ''),
                ('_pdbx_chem_comp_descriptor.program_version', '%s', 'str', ''),
                ('_pdbx_chem_comp_descriptor.descriptor', '%s', 'str', '')
            ],
            'chem_comp_identifier': [
                ('_pdbx_chem_comp_identifier.comp_id', '%s', 'str', ''),
                ('_pdbx_chem_comp_identifier.type', '%s', 'str', ''),
                ('_pdbx_chem_comp_identifier.program', '%s', 'str', ''),
                ('_pdbx_chem_comp_identifier.program_version', '%s', 'str', ''),
                ('_pdbx_chem_comp_identifier.identifier', '%s', 'str', '')
            ]
        }

    def setCachePath(self, topCachePath: str = '/data/components/ligand-dict-v4'):
        """ Set the top file tree of CCD.
        """

        self.__topCachePath = topCachePath

    def setCompId(self, compId: str, ligand: bool = True) -> bool:
        """ Set compId and CCD CIF file path based on file tree of CCD.
        """

        if compId in emptyValue:
            return False

        self.__compId = compId.upper()

        if not ccd_id_pattern.match(self.__compId) or (not ligand and is_reserved_lig_code(self.__compId)):
            return False

        self.__filePath = os.path.join(self.__topCachePath,
                                       self.__compId[-2:] if len(self.__compId) > 3 else self.__compId[0],
                                       self.__compId,
                                       self.__compId + '.cif')

        if not os.access(self.__filePath, os.R_OK):
            if self.__verbose:
                self.__lfh.write(f"+{self.__class_name__}.setCompId() ++ Error  - Missing file {self.__filePath}\n")
            return False

        return True

    def setFilePath(self, filePath: str, compId: str) -> bool:
        """ Set compId and CCD CIF file path.
        """

        try:

            if compId in emptyValue:
                return False

            self.__compId = compId.upper()

            if not ccd_id_pattern.match(self.__compId) or is_reserved_lig_code(self.__compId):
                return False

            self.__filePath = filePath

            if not os.access(self.__filePath, os.R_OK):
                if self.__verbose:
                    self.__lfh.write(f"+{self.__class_name__}.setFilePath() ++ Error  - Missing file {self.__filePath}\n")
                return False

            return True

        except Exception as e:
            if self.__verbose:
                self.__lfh.write(f"+{self.__class_name__}.setFilePath() ++ Error  - Set {self.__filePath} failed {str(e)}\n")
            return False

    def getAtomList(self) -> List[list]:
        """ Get a list of list of data from the chem_comp_atom category.
        """

        self.__updateDataBlock()

        return self.__getRowList(catName='chem_comp_atom')

    def getBonds(self) -> List[list]:
        """ Get a list of list of data from the chem_comp_bond category.
        """

        self.__updateDataBlock()

        return self.__getRowList(catName='chem_comp_bond')

    def getChemCompDict(self) -> dict:
        """ Get a dictionary of the chem_comp category.
        """

        try:

            self.__updateDataBlock()

            return self.__getDictList(catName='chem_comp')[0]

        except Exception:
            return {}

    def __updateDataBlock(self) -> bool:
        """ Update the definition data for the input compId.
            @return: True for success or False otherwise
        """

        if self.__compId == self.__lastCompId:
            return True

        try:

            if self.__setDataBlock(self.__getDataBlock()):
                self.__lastCompId = self.__compId
                return True

            return False

        except Exception as e:
            if self.__verbose:
                self.__lfh.write(f"+{self.__class_name__}.__updateDataBlock() ++ Error  - {str(e)}\n")
            return False

    def __getDataBlock(self, blockId: Optional[str] = None) -> Optional[DataContainer]:
        """ Worker method to read CCD CIF file and set the target datablock.
            @return: the first datablock if no blockId is provided
        """

        try:

            with open(self.__filePath, 'r', encoding='utf-8') as ifh:
                myBlockList = []
                pRd = PdbxReader(ifh)
                pRd.read(myBlockList)

            if blockId is not None:

                for block in myBlockList:
                    if (block.getType() == 'data' and block.getName() == blockId):
                        if self.__verbose and self.__debug:
                            block.printIt(self.__lfh)
                        return block

            else:

                for block in myBlockList:
                    if block.getType() == 'data':
                        if self.__verbose and self.__debug:
                            block.printIt(self.__lfh)
                        return block

        except Exception as e:
            if self.__verbose:
                self.__lfh.write(f"+{self.__class_name__}.__getDataBlock() ++ Error  - {str(e)}\n")

        return None

    def __setDataBlock(self, dataBlock: Optional[DataContainer]) -> bool:
        """ Assigns the input datablock as the active internal datablock.
        """

        if dataBlock is None:
            self.__dBlock = None
            return False

        try:

            if dataBlock.getType() == 'data':
                self.__dBlock = dataBlock
                return True

        except Exception:
            pass

        self.__dBlock = None

        return False

    def __getDictList(self, catName: str = 'chem_comp') -> List[dict]:
        """ Return a list of dictionaries of the input category.
        """

        catObj = self.__dBlock.getObj(catName)

        if catObj is None:
            return []

        itDict = {itName: idxIt for idxIt, itName in enumerate(catObj.getItemNameList())}

        colDict = {}
        for itTup in self.__itemDict[catName]:
            colDict[itTup[0]] = itDict[itTup[0]] if itTup[0] in itDict else -1

        dList = []
        for row in catObj.getRowList():
            dList.append({itName: '' if idxIt < 0 else row[idxIt] for itName, idxIt in colDict.items()})

        return dList

    def __getRowList(self, catName: str = 'chem_comp_bond') -> List[list]:
        """ Return a list a list of data from the input category including
            data types and default value replacement.
        """

        catObj = self.__dBlock.getObj(catName)

        if catObj is None:
            return []

        def apply_type(ctype, default, val):
            if val in emptyValue:
                return default
            if ctype == 'int':
                return int(val)
            if ctype == 'float':
                return float(val)
            return val

        itDict = {itName: idxIt for idxIt, itName in enumerate(catObj.getItemNameList())}

        colTupList = []
        for itTup in self.__itemDict[catName]:
            colTupList.append((itDict[itTup[0]] if itTup[0] in itDict else -1, itTup[2], itTup[3]))

        dList = []
        for row in catObj.getRowList():
            uR = []
            for cTup in colTupList:
                uR.append(apply_type(cTup[1], cTup[2], cTup[2] if cTup[0] < 0 else row[cTup[0]]))
            dList.append(uR)

        return dList
