import copy
import itertools
import pandas as pd
import gzip

from pathlib import Path
from collections.abc import Iterable
from collections import defaultdict
from typing import Self, Iterator
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

from rdkit import Chem, DataStructs, Geometry
from rdkit.Chem import Draw, AllChem, rdFMCS, rdDepictor
from rdkit.ML.Cluster import Butina
from rdkit.SimDivFilters.rdSimDivPickers import MaxMinPicker
from PIL import Image

from rdworks import Conf, Mol
from rdworks.display import render_matrix_grid
from rdworks.xml import list_predefined_xml


class MolLibr:
    def __init__(self, 
                 molecules: Iterable | None = None,
                 names: Iterable | None = None,
                 std:bool=False,
                 max_workers:int=4,
                 chunksize:int=10,
                 progress:bool=False) -> None:
        """Create a rdworks.MolLibr object.

        Args:
            molecules (Iterable | None, optional): a list/tuple/set of molecules 
                (rdworks.Mol | SMILES | rdkit.Chem.Mol). Defaults to None.
            names (Iterable | None, optional): a list/tuple/set of names. Defaults to None.
            std (bool, optional): whether to standardize molecules. Defaults to False.
            max_workers (int, optional): max workers for parallel calculation. Defaults to 4.
            chunksize (int, optional): chunksize for parallel calculation. Defaults to 100.
            progress (bool, optional): whether to show progress bar. Defaults to False.

        Raises:
            ValueError: if counts of molecules and names differ.
            TypeError: if molecule is not rdworks.Mol | SMILES | rdkit.Chem.Mol )
        """
        self.libr = []
        self.max_workers = max_workers
        self.chunksize = chunksize
        self.progress = progress
        self.query = None
        self.threshold = None
        self.clusters = None

        assert isinstance(molecules, Iterable) or molecules is None, "molecules must be iterable or None"
        assert isinstance(names, Iterable) or names is None, "names must be iterable or None"
        
        if isinstance(molecules, Iterable):
            if isinstance(names, Iterable):
                assert len(molecules) == len(names), "molecules and names must be the same counts"
            
            if names is None:
                names = [''] * len(molecules)
            
            for molecular_input, name in zip(molecules, names):
                if isinstance(molecular_input, Mol):
                    _mol = molecular_input
                
                elif isinstance(molecular_input, Chem.Mol) or isinstance(molecular_input, str):
                    _mol = Mol(molecular_input, name=name, std=std)
                
                elif isinstance(molecular_input, Conf):
                    _mol = Mol(molecular_input.rdmol,
                                name=molecular_input.name, 
                                std=std).props.update(molecular_input.props)

                self.libr.append(_mol)
            
            if not any(names):
                self.rename(prefix='entry')
    

    def copy(self) -> Self:
        """Returns a copy of self.

        Returns:
            Self: rdworks.MolLibr object.
        """
        return copy.deepcopy(self)
    
    
    def __str__(self) -> str:
        """Returns string representation.

        Returns:
            str: string representation.
        """
        
        return f"<MolLibr({self.count()})>"
    

    def __iter__(self) -> Iterator:
        """Yields an iterator of molecules.

        Yields:
            Iterator: iterator of molecules.
        """
        return iter(self.libr)
    

    def __next__(self) -> Mol:
        """Next molecule.

        Returns:
            Mol: next molecule.
        """
        return next(self.libr)
    

    def __eq__(self, other: Self) -> bool:
        """Operator `==`.

        Args:
            other (rdworks.MolLibr): other rdworks.MolLibr object.

        Returns:
            Bool: True if other MolLibr object is identical with self.
        """
        if isinstance(other, MolLibr):
            return len(frozenset(self.libr) - frozenset(other.libr)) == 0
        
        return False
        

    def __getitem__(self, index: int | slice) -> Mol | Self:
        """Operator `[]`.

        Args:
            index (Union[int, slice]): index or slice of indexes.

        Returns:
            Mol or MolLibr specified by single index or slice.
        """
        assert self.count() != 0, "library is empty"
        if isinstance(index, slice):
            return MolLibr(self.libr[index])
        else:
            return self.libr[index]
        

    def __setitem__(self, index: int, molecule: Mol) -> Self:
        """Set item.

        Args:
            index (int): index
            molecule (Mol): molecule to replace
        
        Returns:
            Modified self.
        """
        self.libr[index] = molecule

        return self


    def __add__(self, other: Mol | Self) -> Self:
        """Operator `+`.

        Returns a new object, leaving the original objects unchanged (conventional behavior).

        Args:
            other (object): other Mol or MolLibr object.

        Returns:
            A new MolLibr object.
        """
        assert isinstance(other, Mol | MolLibr), "'+' operator expects Mol or MolLibr object"
        
        new_object = self.copy()

        if isinstance(other, Mol):
            new_object.libr.append(other)
        
        elif isinstance(other, MolLibr):
            new_object.libr.extend(other.libr)

        return new_object


    def __iadd__(self, other: Mol | Self) -> Self:
        """Operator `+=`.

        Args:
            other (object): other Mol or MolLibr object.

        Returns:
            modified self.
        """
        assert isinstance(other, Mol | MolLibr), "'+=' operator expects Mol or MolLibr object"

        if isinstance(other, Mol):
            self.libr.append(other)
        
        elif isinstance(other, MolLibr):
            self.libr.extend(other.libr)

        return self


    def __sub__(self, other: Mol | Self) -> Self:
        """Operator `-`.

        Returns a new object, leaving the original objects unchanged (conventional behavior).

        Args:
            other (Mol | MolLibr): other rdworks.Mol or rdworks.MolLibr object.

        Returns:
            A new MolLibr object.
        """
        assert isinstance(other, Mol | MolLibr), "'-' operator expects Mol or MolLibr object"

        if isinstance(other, Mol):
            difference = frozenset(self.libr) - frozenset([other])
        
        elif isinstance(other, MolLibr):
            difference = frozenset(self.libr) - frozenset(other.libr)

        new_object = self.copy()
        new_object.libr = list(difference)

        return new_object
    

    def __isub__(self, other: Mol | Self) -> Self:
        """Operator `-=`.

        Args:
            other (Mol | MolLibr): other molecule or library.

        Returns:
            Modified self.
        """
        assert isinstance(other, Mol | MolLibr), "'-=' operator expects Mol or MolLibr object"

        if isinstance(other, Mol):
            difference = frozenset(self.libr) - frozenset([other])
        
        elif isinstance(other, MolLibr):
            difference = frozenset(self.libr) - frozenset(other.libr)

        self.libr = list(difference)
        
        return self


    def __and__(self, other: Mol | Self) -> Self:
        """Operator `&`.

        Returns a new object, leaving the original objects unchanged (conventional behavior).

        Args:
            other (Mol | MolLibr): other molecule or library.

        Returns:
            A new MolLibr object.
        """
        assert isinstance(other, Mol | MolLibr), "'&' operator expects Mol or MolLibr object"

        if isinstance(other, Mol):
            intersection = frozenset(self.libr) & frozenset([other])

        elif isinstance(other, MolLibr):
            intersection = frozenset(self.libr) & frozenset(other.libr)
        
        new_object = self.copy()
        new_object.libr = list(intersection)
        
        return new_object


    def __iand__(self, other: Mol | Self) -> Self:
        """Operator `&=`.

        Args:
            other (Mol | Self): other molecule or library.

        Returns:
            Modified self.
        """
        assert isinstance(other, Mol | MolLibr), "'&=' operator expects Mol or MolLibr object"

        if isinstance(other, Mol):
            intersection = frozenset(self.libr) & frozenset([other])
        
        elif isinstance(other, MolLibr):
            intersection = frozenset(self.libr) & frozenset(other.libr)

        self.libr = list(intersection)
        
        return self
    

    @staticmethod
    def _mask_similar(mol:Mol, targs:tuple) -> bool:
        """A mask function to return True if molecule is similar with target molecules, `targs`.

        Args:
            mol (Mol): subject rdworks.Mol object.
            targs (tuple): a tuple of rdworks.Mol objects to compare.

        Returns:
            bool: True if molecule is similar with target molecules.
        """
        return mol.is_similar(*targs) # unpack tuple of arguments
    

    @staticmethod
    def _mask_drop(mol:Mol, terms:str | Path) -> bool:
        """A mask function to return True if molecule matches `terms`.

        Note that molecules matching the terms will be dropped (NOT be included) in the compression.

        Args:
            mol (Mol): subject rdworks.Mol object.
            terms (str | Path): rule.

        Returns:
            bool: True if molecule matches the terms.
        """
        return not mol.is_matching(terms)
    
    @staticmethod
    def _map_qed(mol:Mol, properties:list[str]=['QED', 'MolWt', 'LogP', 'TPSA', 'HBD']) -> dict:
        """A map function to apply Mol.qed(`properties`) on `mol`.

        The default behavior of map() is to pass the elements of the iterable to the function by reference. 
        This means that if the function modifies the elements of the iterable, 
        those changes will be reflected in the iterable itself.

        Args:
            mol (Mol): subject rdworks.Mol object.
            properties (list[str], optional): properties. Defaults to ['QED', 'MolWt', 'LogP', 'TPSA', 'HBD'].

        Returns:
            dict: dictionary of properties.
        """
        return mol.qed(properties)

    
    def compute(self, **kwargs) -> Self:
        """Change settings for parallel computing.

        Args:
            max_workers (int, optional): max number of workers. Defaults to 4.
            chunksize (int, optional): chunksize of splitted workload. Defaults to 10.
            progress (bool, optional): whether to show progress bar. Defaults to False.

        Returns:
            Self: rdworks.MolLibr object.
        """
        self.max_workers = kwargs.get('max_workers', self.max_workers)
        self.chunksize = kwargs.get('chunksize', self.chunksize)
        self.progress = kwargs.get('progress', self.progress)
        
        return self


    def rename(self, prefix: str | None = None, sep: str='.', start: int=1) -> Self:
        """Rename molecules with serial numbers in-place and their conformers.
        
        Molecules will be named by a format, `{prefix}{sep}{serial_number}` and 
        conformers will be named accordingly.

        Examples:
            >>> a.rename(prefix='a')

        Args:
            prefix (str, optional): prefix for new name. If prefix is not given and set to None,
                                    molecules will not renamed but conformers will be still renamed. 
                                    This is useful after dropping some conformers and rename them serially.
            sep (str): separator between prefix and serial number (default: `.`)
            start (int): start number of serial number.

        Returns:
            Self: rdworks.MolLibr object.
        """

        num = self.count()
        num_digits = len(str(num)) # ex. '100' -> 3
        if prefix: 
            # use prefix to rename molecules AND conformers
            for (serial, mol) in enumerate(self.libr, start=start):
                if num > 1:
                    serial_str = str(serial)
                    while len(serial_str) < num_digits:
                        serial_str = '0' + serial_str
                    mol.rename(prefix=f"{prefix}{sep}{serial_str}")
                else:
                    mol.rename(prefix)
        else:
            # rename molecules using serial numbers if they have duplicate names
            # name -> name.1, name.2, ...
            count_names = defaultdict(list)
            for idx, mol in enumerate(self.libr):
                count_names[mol.name].append(idx)
            not_unique_names = [name for name, l in count_names.items() if len(l) > 1]
            for idx, mol in enumerate(self.libr):
                if mol.name in not_unique_names:
                    serial = count_names[mol.name].index(idx) + 1
                    mol.rename(f'{mol.name}.{serial}')
            # rename conformers
            for mol in self.libr:
                mol.rename()
        
        return self
    

    def overlap(self, other: Self) -> Self:
        """Returns a common subset with `other` library.

        Args:
            other (Self): rdworks.MolLibr object.

        Returns:
            Self: common subset of rdworks.MolLibr.
        """
        return self.__and__(other)
    

    def similar(self, query: Mol, threshold: float = 0.2, **kwargs) -> Self:
        """Returns a copy of subset that are similar to `query`.

        Args:
            query (Mol): query molecule.
            threshold (float, optional): similarity threshold. Defaults to 0.2.

        Raises:
            TypeError: if query is not rdworks.Mol type.

        Returns:
            Self: a copy of self.
        """
        obj = self.copy().compute(**kwargs)
        
        if isinstance(query, Mol):
            largs = [(query, threshold),] * obj.count()
        else:
            raise TypeError("MolLibr.similar() expects Mol object")
        with ProcessPoolExecutor(max_workers=obj.max_workers) as executor:
            if self.progress:
                mask = list(tqdm(executor.map(MolLibr._mask_similar, obj.libr, largs, chunksize=obj.chunksize),
                    desc="Similar",
                    total=obj.count()))
            else:
                mask = list(executor.map(MolLibr._mask_similar, obj.libr, largs, chunksize=obj.chunksize))
            obj.libr = list(itertools.compress(obj.libr, mask))
        
        return obj



    def unique(self, report=False) -> Self:
        """Removes duplicates and returns a copy of unique library.

        Args:
            report (bool, optional): whether to report duplicates. Defaults to False.

        Returns:
            Self: a copy of self.
        """
        obj = self.copy()
        
        U = {} # unique SMILES
        mask = []
        for mol in obj.libr:
            if mol.smiles in U:
                mask.append(False)
                # ignore the same name or recorded aka
                if (mol.name != U[mol.smiles].name) and (mol.name not in U[mol.smiles].props['aka']):
                    U[mol.smiles].props['aka'].append(mol.name)
            else:
                mask.append(True)
                U[mol.smiles] = mol
        obj.libr = list(itertools.compress(obj.libr, mask))
        if report:
            print("duplicates:")
            for mol in obj.libr:
                if len(mol.props['aka']) > 0:
                    print(f"  {mol.name}({len(mol.props['aka'])}) - {','.join(mol.props['aka'])}")
            print(f"de-duplicated to {obj.count()} molecules")
        
        return obj
    

    def qed(self, properties:list[str]=['QED', 'MolWt', 'LogP', 'TPSA', 'HBD'], **kwargs) -> Self:
        """Returns a copy of self with calculated quantitative estimate of drug-likeness (QED).

        Args:
            properties (list[str], optional): _description_. Defaults to ['QED', 'MolWt', 'LogP', 'TPSA', 'HBD'].

        Returns:
            Self: self.
        """
        self = self.compute(**kwargs)
        lprops = [ properties, ] * self.count()
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            if self.progress:
                self.libr = list(tqdm(
                    executor.map(MolLibr._map_qed, self.libr, lprops, chunksize=self.chunksize),
                    desc="QED Properties",
                    total=self.count()
                    ))
            else:
                self.libr = list(
                    executor.map(MolLibr._map_qed, self.libr, lprops, chunksize=self.chunksize)
                    )
        
        return self
    

    def drop(self, terms: str | Path | None = None, invert: bool = False, **kwargs) -> Self:
        """Drops matched molecules and returns a copy of library with remaining molecules.

        Args:
            terms (str | Path | None, optional): matching terms. Defaults to None.
            invert (bool, optional): whether to invert selection by the `terms`. Defaults to False.

        Returns:
            Self: a copy of self.
        """
        if not terms:
            print(list_predefined_xml())
            return self
        
        obj = self.copy().compute(**kwargs)
        
        lterms = [ terms ] * obj.count()
        with ProcessPoolExecutor(max_workers=obj.max_workers) as executor:
            if obj.progress:
                mask = list(tqdm(
                    executor.map(MolLibr._mask_drop, obj.libr, lterms, chunksize=obj.chunksize),
                    desc="Drop",
                    total=obj.count()))
            else:
                mask = list(
                    executor.map(MolLibr._mask_drop, obj.libr, lterms, chunksize=obj.chunksize))
            if invert:
                mask = [not b for b in mask]
            obj.libr = list(itertools.compress(obj.libr, mask))
        
        return obj
    

    @staticmethod
    def _mcs_coord_map(subject:Mol, r:Chem.Mol) -> dict:
        s = subject.rdmol
        lcs = rdFMCS.FindMCS([r, s])
        # reference matching indices
        r_indices = r.GetSubstructMatch(lcs.queryMol)
        # subject matching indices
        s_indices = s.GetSubstructMatch(lcs.queryMol)
        # reference matching coordinates (2D)
        r_xy = []
        for i in r_indices:
            pt = r.GetConformer().GetAtomPosition(i)
            r_xy.append(Geometry.Point2D(pt.x, pt.y))
        coord_map = { i : xy for i, xy in zip(s_indices, r_xy) }
        
        return coord_map


    def align_drawing(self, 
                      ref: int = 0, 
                      mcs: bool = True, 
                      scaffold: str = "", 
                      coordgen:bool = True, 
                      **kwargs,
                      ) -> Self:
        """Align 2D drawings by using MCS or scaffold SMILES.

        Args:
            ref (int, optional): index to the reference. Defaults to 0.
            mcs (bool, optional): whether to use MCS(maximum common substructure). Defaults to True.
            scaffold (str, optional): whether to use scaffold (SMILES). Defaults to "".

        Returns:
            Self: self
        """

        obj = self.copy().compute(**kwargs)
        
        if scaffold:
            # scaffold (SMILES) of the reference 2D drawing
            ref_2d_rdmol = Chem.MolFromSmiles(scaffold)
        else:
            # maximum common substructure to the reference 2D drawing
            assert ref >=0 and ref < obj.count(), f"ref should be [0,{obj.count()-1}]"
            ref_2d_rdmol = obj.libr[ref].rdmol

        rdDepictor.SetPreferCoordGen(coordgen)
        rdDepictor.Compute2DCoords(ref_2d_rdmol)
        # AllChem.Compute2DCoords(ref_2d_rdmol)
        
        with ProcessPoolExecutor(max_workers=obj.max_workers) as executor:
            if obj.progress:
                coord_maps = list(tqdm(
                    executor.map(MolLibr._mcs_coord_map, 
                        obj.libr, # subject
                        itertools.repeat(ref_2d_rdmol), # infinite iterator
                        chunksize=obj.chunksize),
                    desc="align drawingp",
                    total=obj.count()))
            else:
                coord_maps = list(
                    executor.map(MolLibr._mcs_coord_map,
                        obj.libr, # subject
                        itertools.repeat(ref_2d_rdmol), # infinite iterator
                        chunksize=obj.chunksize))
        
        for mol, coord_map in zip(obj.libr, coord_maps):
            rdDepictor.Compute2DCoords(mol.rdmol, coordMap=coord_map)
            # AllChem.Compute2DCoords(mol.rdmol, coordMap=coord_map)


        # for idx, mol in enumerate(obj.libr):
        #     if mcs and idx == ref:
        #         continue

        #     # largest common substructure
        #     lcs = rdFMCS.FindMCS([ref_2d_rdmol, mol.rdmol])

        #     # matching indices
        #     ref_xy_coords = []
        #     for i in ref_2d_rdmol.GetSubstructMatch(lcs.queryMol):
        #         pt = ref_2d_rdmol.GetConformer().GetAtomPosition(i)
        #         ref_xy_coords.append(Geometry.Point2D(pt.x, pt.y))
        #     sub_indices = mol.rdmol.GetSubstructMatch(lcs.queryMol)
        #     coord_map = { i : xy for i, xy in zip(sub_indices, ref_xy_coords) }
        #     AllChem.Compute2DCoords(mol.rdmol, coordMap=coord_map)

        return obj


    def pick(self, n: int, **kwargs) -> Self:
        """Picks n diverse molecules.

        Args:
            n (int): number of molecules to pick.

        Returns:
            Self: a copy of self.
        """
        obj = self.copy()
        raise NotImplementedError
        return obj
    



    ##################################################
    ### endpoints
    ##################################################

    
    def count(self) -> int:
        """Returns number of molecules.

        Returns:
            int: count of molecules.
        """
        return len(self.libr)
    

    def cluster(self, 
                threshold: float = 0.3, 
                ordered: bool = True, 
                drop_singleton: bool = True,
                ) -> list:
        """Clusters molecules using fingerprint.

        Args:
            threshold (float, optional): Tanimoto similarity threshold. Defaults to 0.3.
            ordered (bool, optional): order clusters by size of cluster. Defaults to True.
            drop_singleton (bool, optional): exclude singletons. Defaults to True.

        Returns:
            list: [(centroid_1, idx, idx,), (centroid_2, idx, idx,), ...]
        """
        for mol in self.libr:
            if not mol.fp:
                mol.fp = mol.MFP2.GetFingerprint(mol.rdmol)
        fps = [ mol.fp for mol in self.libr if mol.fp ]
        n = len(fps)
        # first generate the distance matrix:
        dmat = []
        for i in range(1, n):
            sims = DataStructs.BulkTanimotoSimilarity(fps[i], fps[:i])
            dmat.extend([1-x for x in sims])
        # Butina hierarchical clustering:
        # clusters is a list of list of indices
        clusters = Butina.ClusterData(dmat, 
                                      nPts=n, 
                                      distThresh=threshold, 
                                      isDistData=True, 
                                      reordering=True)
        if ordered:
            # in the order of cluster size, from the largest to the smallest
            clusters = sorted(clusters, key=lambda indices: len(indices), reverse=True)
        
        if drop_singleton:
            clusters = [indices for indices in clusters if len(indices) > 1]
        
        return clusters
    

    
    def to_sdf(self, 
                path: str | Path, 
                confs: bool = False, 
                props: bool = True, 
                separate: bool = False,
                ) -> None:
        """Writes to .sdf or .sdf.gz file.

        Chem.SDWriter is supposed to write all non-private molecular properties.

        `dirname/filename.sdf` -> `dirname/filename_{molecule name}.sdf`
        `dirname/filename.sdf.gz` -> `dirname/filename_{molecule name}.sdf.gz`

        Args:
            path (str or PosixPath) : output filename or path
            confs (bool) : whether to write 3D coordinates and conformer properties. Defaults to False.
            props (bool) : whether to write SDF properties. Defaults to True.
            separate (bool) : write each molecule to separate files. Defaults to False.
        """
        if isinstance(path, str):
            path = Path(path)
        # PurePosixPath('my/dir/mol.sdf.gz').suffix -> '.gz'
        # PurePosixPath('my/dir/mol.sdf.gz').suffixes -> ['.sdf', '.gz']
        # PurePosixPath('my/dir/mol.sdf').name -> 'mol.sdf'
        # PurePosixPath('my/dir/mol.sdf').with_name('mol2.sdf') -> PurePath('my/dir/mol2.sdf')
        suffix = path.suffix 
        suffixes = ''.join(path.suffixes) 
        prefix = path.name.replace(suffixes, '')
        if separate:
            for mol in self.libr:
                if suffix == '.gz':
                    with gzip.open(path.with_name(f'{prefix}_{mol.name}.sdf.gz'), "wt") as f:
                        f.write(mol.to_sdf(confs, props))
                else:
                    with open(path.with_name(f'{prefix}_{mol.name}.sdf'), "w") as f:
                        f.write(mol.to_sdf(confs, props))

        else:
            if suffix == '.gz':
                with gzip.open(path, "wt") as f:
                    for mol in self.libr:
                        f.write(mol.to_sdf(confs, props))
            else:
                with open(path, "w") as f:
                    for mol in self.libr:
                        f.write(mol.to_sdf(confs, props))


    def to_smi(self, path: str | Path) -> None:
        """Writes to .smi file.

        Args:
            path (str | Path): output filename or path.
        """
        if isinstance(path, Path):
            path = path.as_posix() # convert to string
        if path.endswith('.gz'):
            with gzip.open(path, "wt") as smigz:
                for mol in self.libr:
                    smigz.write(f'{mol.smiles} {mol.name}\n')
        else:
            with open(path, "w") as smi:
                for mol in self.libr:
                    smi.write(f'{mol.smiles} {mol.name}\n')


    def to_svg(self, 
               mols_per_row: int = 5,
               width: int = 200, 
               height: int = 200,
               atom_index: bool = False,
               redraw: bool = False,
               coordgen: bool = False) -> str:
        """Writes to a .svg strings for Jupyter notebook.

        Args:
            path (str | Path): output filename or path.
            mols_per_row (int, optional): number of molecules per row. Defaults to 5.
            width (int, optional): width. Defaults to 200.
            height (int, optional): height. Defaults to 200.
            atom_index (bool, optional): whether to show atom index. Defaults to False.
            redraw (bool, optional): whether to redraw. Defaults to False.
            coordgen (bool, optional): whether to use coordgen. Defaults to False.
        """
        
        rdmols  = [mol.rdmol for mol in self.libr]
        legends = [mol.name for mol in self.libr]

        svg_string = render_matrix_grid(rdmols, 
                                        legends,
                                        mols_per_row = mols_per_row, 
                                        width = width, 
                                        height = height,
                                        atom_index = atom_index,
                                        redraw = redraw,
                                        coordgen = coordgen,
                                        svg = True,
                                        )
        
        return svg_string



    def to_png(self,
               filename: str | Path | None = None,
               mols_per_row: int = 5,
               width: int = 200, 
               height: int = 200,
               atom_index: bool = False,
               redraw: bool = False,
               coordgen: bool = False,
               ) -> Image.Image | None:
        """Writes to a .png file.

        Args:
            mols_per_row (int, optional): number of molecules per row. Defaults to 5.
            width (int, optional): width. Defaults to 200.
            height (int, optional): height. Defaults to 200.
            atom_index (bool, optional): whether to show atom index. Defaults to False.
            redraw (bool, optional): whether to redraw. Defaults to False.
            coordgen (bool, optional): whether to use coordgen. Defaults to False.
        """
        rdmols  = [mol.rdmol for mol in self.libr]
        legends = [mol.name for mol in self.libr]

        img = render_matrix_grid(rdmols, 
                                legends,
                                mols_per_row = mols_per_row, 
                                width = width, 
                                height = height,
                                atom_index = atom_index,
                                redraw = redraw,
                                coordgen = coordgen,
                                svg = False,
                                )
        
        if filename is None:
            return img
        else:
            if isinstance(filename, Path):
                filename = filename.as_posix()
            img.save(filename)


    def to_html(self) -> str:
        """Writes to HTML strings.

        Returns:
            str: HTML strings.
        """
        HTML = "<html><body>"
        for mol in self.libr:
            HTML += mol.to_html(htmlbody=False)
        HTML += "</body></html>"
        return HTML


    def to_dataframe(self, 
                     name: str = 'name', 
                     smiles: str = 'smiles', 
                     confs: bool = False,
                     ) -> pd.DataFrame:
        """Returns a Pandas DataFrame.

        Args:
            name (str, optional): column name for name. Defaults to 'name'.
            smiles (str, optional): column name for SMILES. Defaults to 'smiles'.
            confs (bool, optional): whether to include conformer properties. Defaults to False.

        Returns:
            pd.DataFrame: pandas DataFrame.
        """
        if confs:
            exclude = ['coord']
            property_columns = set()
            for mol in self.libr:
                for conf in mol.confs:
                    for k in conf.props:
                        if k not in exclude:
                            property_columns.add(k)
            property_columns = property_columns - set([name, smiles])
            data = {name:[], smiles:[]}
            data.update({k:[] for k in property_columns})
            for mol in self.libr:
                for conf in mol.confs:
                    data[name].append(conf.name)
                    data[smiles].append(mol.smiles)
                    for k in property_columns:
                        if k in conf.props:
                            data[k].append(conf.props[k])
                        else:
                            data[k].append(None)
        else:
            property_columns = set()
            for mol in self.libr:
                for k in mol.props:
                    property_columns.add(k)
            property_columns = property_columns - set([name, smiles])
            data = {name:[], smiles:[]}
            data.update({k:[] for k in property_columns})
            for mol in self.libr:
                data[name].append(mol.name)
                data[smiles].append(mol.smiles)
                for k in property_columns:
                    if k in mol.props:
                        data[k].append(mol.props[k])
                    else:
                        data[k].append(None)
        
        return pd.DataFrame(data)


    def to_csv(self, 
               path: str | Path, 
               confs: bool = False, 
               decimals:int = 3,
               ) -> None:
        """Writes to a .csv file.

        Args:
            path (str | Path): output filename or path.
            confs (bool, optional): whether to include conformer properties. Defaults to False.
            decimals (int, optional): decimal places for float numbers. Defaults to 3.
        """
        df = self.to_dataframe(confs=confs)
        df.to_csv(path, index=False, float_format=f'%.{decimals}f')


    @staticmethod
    def _mask_nnp_ready(mol: Mol, model: str) -> bool:
        """A mask function to return True if molecule is NNP ready. 

        Args:
            mol (Mol): rdworks.Mol object.
            model (str): name of NNP model.

        Returns:
            bool: True if molecule is NNP ready.
        """
        return mol.nnp_ready(model)
    

    def nnp_ready(self, model: str, **kwargs) -> Self:
        """Returns a copy of subset of library that is ready to given neural network potential.

        Examples:
            >>> libr = rdworks.MolLibr(drug_smiles, drug_names)
            >>> ani2x_compatible_subset = libr.nnp_ready('ANI-2x', progress=False)

        Args:
            model (str): name of model.

        Returns:
            Self: subset of library.
        """
        obj = self.copy().compute(**kwargs)
        lmodel = [model,] * self.count()
        with ProcessPoolExecutor(max_workers=obj.max_workers) as executor:
            if obj.progress:
                mask = list(tqdm(
                    executor.map(self._mask_nnp_ready, obj.libr, lmodel, chunksize=obj.chunksize),
                    desc="NNP ready",
                    total=obj.count()))
            else:
                mask = list(
                    executor.map(self._mask_nnp_ready, obj.libr, lmodel, chunksize=obj.chunksize))
            obj.libr = list(itertools.compress(obj.libr, mask))
        
        return obj
    

    def to_nnbatches(self, batchsize: int = 1000) -> list:
        """Split workload flexibily into a numer of batches.

        - Each batch has up to `batchsize` number of atoms.
        - Conformers originated from a same molecule can be splitted into multiple batches.
        - Or one batch can contain conformers originated from multiple molecules.

        coord: coordinates of input molecules (N, m, 3) where N is the number of structures and
        m is the number of atoms in each structure.
        numbers: atomic numbers in the molecule (include H). (N, m)
        charges: (N,)

        Args:
            batchsize: max. number of atoms in a batch.

        Returns:
            list: list of batches.
        """

        pre_batches = []
        batch_confs = []
        batch_mols = []
        batch_n_atoms = 0

        for mol in self.libr:
            for conf in mol.confs:
                n_atoms = conf.props['atoms']
                if (batch_n_atoms + n_atoms) > batchsize:
                    pre_batches.append((batch_mols, batch_confs, batch_n_atoms))
                    # start over a new batch
                    batch_mols =  [mol]
                    batch_confs = [conf]
                    batch_n_atoms = n_atoms
                else:
                    batch_mols.append(mol)
                    batch_confs.append(conf)
                    batch_n_atoms += n_atoms
        
        if batch_n_atoms > 0: # last remaining batch
            pre_batches.append((batch_mols, batch_confs, batch_n_atoms))
        
        batches = []
        
        for i, (batch_mols, batch_confs, batch_n_atoms) in enumerate(pre_batches, start=1):
            charges = [mol.props['charge'] for mol in batch_mols]
            coord = [conf.rdmol.GetConformer().GetPositions().tolist() for conf in batch_confs]
            # to be consistent with legacy code
            coord = [[tuple(xyz) for xyz in inner] for inner in coord]
            # numbers should be got from conformers because of hydrogens
            numbers = [[a.GetAtomicNum() for a in conf.rdmol.GetAtoms()] for conf in batch_confs]
            batches.append((coord, numbers, charges, batch_confs, batch_mols))
        
        return batches