import os
import pathlib
import copy
import operator
import numpy as np
import math

from collections import defaultdict
from typing import List, Tuple, Union, Iterator

from rdkit import Chem, Geometry
from rdkit.Chem import Draw, AllChem, rdMMPA, rdDepictor

from rdworks.mol import Mol, rd_descriptor, rd_descriptor_f
from rdworks.mollibr import MolLibr
from rdworks.display import render_svg


def get_attachment_orientation(mol: Chem.Mol, dummy_atom_idx: int | None = None):
    """
    Get the orientation of attachment points (dummy atoms) in a molecule.
    
    Args:
        mol: RDKit molecule object
        dummy_atom_idx: Index of specific dummy atom (if None, finds all dummy atoms)
    
    Returns:
        Dictionary with dummy atom indices as keys and orientation info as values
    """
    # Ensure molecule has 2D coordinates
    if not mol.GetNumConformers():
        rdDepictor.Compute2DCoords(mol)
    
    conf = mol.GetConformer()
    orientations = {}
    
    # Find dummy atoms (atomic number 0)
    dummy_atoms = []
    if dummy_atom_idx is not None:
        dummy_atoms = [dummy_atom_idx]
    else:
        for atom in mol.GetAtoms():
            if atom.GetAtomicNum() == 0:  # Dummy atom
                dummy_atoms.append(atom.GetIdx())
    
    for dummy_idx in dummy_atoms:
        dummy_atom = mol.GetAtomWithIdx(dummy_idx)
        dummy_pos = np.array(conf.GetAtomPosition(dummy_idx))[:2]  # Get x, y coordinates
        
        # Get the neighboring atom (should be exactly one for attachment point)
        neighbors = list(dummy_atom.GetNeighbors())
        if len(neighbors) != 1:
            print(f"Warning: Dummy atom {dummy_idx} has {len(neighbors)} neighbors")
            continue
            
        neighbor_idx = neighbors[0].GetIdx()
        neighbor_pos = np.array(conf.GetAtomPosition(neighbor_idx))[:2]
        
        # Calculate direction vector from neighbor to dummy atom
        direction_vector = dummy_pos - neighbor_pos
        
        # Normalize the vector
        if np.linalg.norm(direction_vector) > 0:
            direction_vector = direction_vector / np.linalg.norm(direction_vector)
        
        # Calculate angle in degrees (0° = right, 90° = up, 180° = left, 270° = down)
        angle_rad = math.atan2(direction_vector[1], direction_vector[0])
        angle_deg = math.degrees(angle_rad)
        
        # Normalize angle to 0-360 range
        if angle_deg < 0:
            angle_deg += 360
            
        # Determine cardinal direction
        if angle_deg <= 45 or angle_deg > 315:
            cardinal = "right"
        elif angle_deg <= 135:
            cardinal = "up"
        elif angle_deg <= 225:
            cardinal = "left"
        else:
            cardinal = "down"
        
        orientations[dummy_idx] = {
            'angle_deg': angle_deg,
            'direction_vector': direction_vector,
            'cardinal': cardinal,
            'neighbor_idx': neighbor_idx,
            'dummy_pos': dummy_pos,
            'neighbor_pos': neighbor_pos
        }
    
    return orientations



def orient_rgroup_to_attachment(rgroup_mol: Chem.Mol, scaffold_orientations: dict) -> Chem.Mol:
    """
    Orient an R-group molecule to match the attachment point orientation of a scaffold.
    
    Args:
        scaffold_mol: Scaffold molecule with dummy atom
        rgroup_mol: R-group molecule with dummy atom
        scaffold_dummy_idx: Index of dummy atom in scaffold
        rgroup_dummy_idx: Index of dummy atom in R-group
    
    Returns:
        Oriented R-group molecule
    """
    # Get orientations
    scaffold_dummy_atom_idx = list(scaffold_orientations.keys())
    if len(scaffold_dummy_atom_idx) == 0:
        print("Error: No dummy atoms found in scaffold molecule")
        return rgroup_mol
    
    rgroup_orientations = get_attachment_orientation(rgroup_mol)

    rgroup_dummy_atom_idx = list(rgroup_orientations.keys())
    if len(rgroup_dummy_atom_idx) == 0:
        print("Error: No dummy atoms found in R-group molecule")
        return rgroup_mol
    
    scaffold_info = scaffold_orientations[scaffold_dummy_atom_idx[0]]
    rgroup_info = rgroup_orientations[rgroup_dummy_atom_idx[0]]
    # Calculate rotation needed
    # We want the R-group attachment to point in the opposite direction of scaffold attachment
    target_angle = scaffold_info['angle_deg'] + 180  # Opposite direction
    current_angle = rgroup_info['angle_deg']
    rotation_angle = target_angle - current_angle
    
    # copy of input molecule
    oriented_mol = Chem.Mol(rgroup_mol)
    
    # Apply rotation to R-group coordinates
    rdDepictor.Compute2DCoords(oriented_mol)
    conf = oriented_mol.GetConformer()
    
    # Get center of rotation (R-group dummy atom position)
    center = rgroup_info['dummy_pos']
    
    # Rotate all atoms
    for i in range(oriented_mol.GetNumAtoms()):
        pos = np.array(conf.GetAtomPosition(i))[:2]
        
        # Translate to origin
        pos_centered = pos - center
        
        # Apply rotation
        angle_rad = math.radians(rotation_angle)
        cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
        rotation_matrix = np.array([[cos_a, -sin_a], [sin_a, cos_a]])
        pos_rotated = np.dot(rotation_matrix, pos_centered)
        
        # Translate back
        pos_final = pos_rotated + center
        
        # Update coordinates
        conf.SetAtomPosition(i, (pos_final[0], pos_final[1], 0.0))
    
    return oriented_mol


def calculate_bond_length(mol: Chem.Mol, atom1_idx: int, atom2_idx: int) -> float:
    """
    Calculate the 2D distance between two bonded atoms.
    
    Args:
        mol: RDKit molecule
        atom1_idx: Index of first atom
        atom2_idx: Index of second atom
    
    Returns:
        Bond length in 2D coordinates
    """
    if not mol.GetNumConformers():
        rdDepictor.Compute2DCoords(mol)
    
    conf = mol.GetConformer()
    pos1 = np.array(conf.GetAtomPosition(atom1_idx))[:2]
    pos2 = np.array(conf.GetAtomPosition(atom2_idx))[:2]
    
    return np.linalg.norm(pos2 - pos1)



def get_average_bond_length(mol: Chem.Mol, bond_type: str = "C-C") -> float:
    """
    Calculate the average bond length for a specific bond type in a molecule.
    
    Args:
        mol: RDKit molecule
        bond_type: Type of bond to measure (e.g., "C-C", "C-N", "any")
    
    Returns:
        Average bond length
    """
    if not mol.GetNumConformers():
        rdDepictor.Compute2DCoords(mol)
    
    bond_lengths = []
    
    for bond in mol.GetBonds():
        atom1 = bond.GetBeginAtom()
        atom2 = bond.GetEndAtom()
        
        # Filter by bond type if specified
        if bond_type == "any":
            include_bond = True
        elif bond_type == "C-C":
            include_bond = (atom1.GetSymbol() == "C" and atom2.GetSymbol() == "C")
        elif bond_type == "C-N":
            include_bond = ((atom1.GetSymbol() == "C" and atom2.GetSymbol() == "N") or
                          (atom1.GetSymbol() == "N" and atom2.GetSymbol() == "C"))
        else:
            # Parse custom bond type like "C-O"
            symbols = bond_type.split("-")
            if len(symbols) == 2:
                include_bond = ((atom1.GetSymbol() == symbols[0] and atom2.GetSymbol() == symbols[1]) or
                              (atom1.GetSymbol() == symbols[1] and atom2.GetSymbol() == symbols[0]))
            else:
                include_bond = False
        
        if include_bond:
            length = calculate_bond_length(mol, atom1.GetIdx(), atom2.GetIdx())
            bond_lengths.append(length)
    
    return np.mean(bond_lengths) if bond_lengths else 0.0


def scale_molecule_coordinates(mol: Chem.Mol, target_bond_length: float, reference_bond_type: str = "any"):
    """
    Scale molecule coordinates to achieve a target bond length.
    
    Args:
        mol: RDKit molecule to scale
        target_bond_length: Desired bond length
        reference_bond_type: Bond type to use as reference for scaling
    
    Returns:
        New molecule with scaled coordinates
    """
    # copy of input molecule
    if not isinstance(mol, Chem.Mol):
        raise TypeError("Input must be an RDKit Mol object")
    
    scaled_mol = Chem.Mol(mol)
    
    # Ensure 2D coordinates exist
    if not scaled_mol.GetNumConformers():
        rdDepictor.Compute2DCoords(scaled_mol)
    
    # Calculate current average bond length
    current_avg_length = get_average_bond_length(scaled_mol, reference_bond_type)
    
    if current_avg_length == 0:
        # print(f"Warning: No {reference_bond_type} bonds found in molecule")
        return scaled_mol
    
    # Calculate scaling factor
    scale_factor = target_bond_length / current_avg_length
    
    # Apply scaling to all coordinates
    conf = scaled_mol.GetConformer()
    for i in range(scaled_mol.GetNumAtoms()):
        pos = conf.GetAtomPosition(i)
        new_pos = (pos.x * scale_factor, pos.y * scale_factor, pos.z)
        conf.SetAtomPosition(i, new_pos)
    
    return scaled_mol



def standardize_rgroup_scales(molecules: list[Chem.Mol], 
                              target_bond_length: float | None = None,
                              reference_bond_type: str = "C-C") -> list[Chem.Mol]:
    """
    Standardize the scale of multiple R-group molecules to have identical bond lengths.
    
    Args:
        molecules: List of RDKit molecules
        target_bond_length: Target bond length (if None, uses average across all molecules)
        reference_bond_type: Bond type to use as reference
    
    Returns:
        List of molecules with standardized scales
    """
    # Ensure all molecules have 2D coordinates
    for mol in molecules:
        if not mol.GetNumConformers():
            rdDepictor.Compute2DCoords(mol)
    
    # Calculate target bond length if not provided
    if target_bond_length is None:
        all_avg_lengths = []
        for mol in molecules:
            avg_length = get_average_bond_length(mol, reference_bond_type)
            if avg_length > 0:
                all_avg_lengths.append(avg_length)
        
        if all_avg_lengths:
            target_bond_length = np.mean(all_avg_lengths)
        else:
            # print(f"Warning: No {reference_bond_type} bonds found in any molecule")
            target_bond_length = 1.0  # Default value
    
    # Scale all molecules
    scaled_molecules = []
    for mol in molecules:
        scaled_mol = scale_molecule_coordinates(mol, target_bond_length, reference_bond_type)
        scaled_molecules.append(scaled_mol)
    
    return scaled_molecules


def create_uniform_grid_image(molecules: list[Chem.Mol],
                              legends: list[str] | None = None,
                              mols_per_row: int = 4,
                              sub_img_size: tuple[int, int] = (300, 300),
                              target_bond_length: float | None = None,
                              reference_bond_type: str = "C-C"):
    """
    Create a grid image of molecules with uniform scaling.
    
    Args:
        molecules: List of RDKit molecules
        legends: Optional list of molecule names/labels
        mols_per_row: Number of molecules per row
        sub_img_size: Size of each molecule image
        target_bond_length: Target bond length for scaling
        reference_bond_type: Bond type to use as reference
    
    Returns:
        PIL Image object
    """
    # Standardize scales
    scaled_molecules = standardize_rgroup_scales(molecules, 
                                                 target_bond_length, 
                                                 reference_bond_type)
    
    # Create grid image
    img = Draw.MolsToGridImage(
        scaled_molecules,
        molsPerRow = mols_per_row,
        subImgSize = sub_img_size,
        legends = legends
    )
    
    return img



class MatchedSeries:
    def __init__(self, 
                 mollibr:MolLibr,
                 sort_props:Union[List,str,None]=None,
                 core_min:int=5, core_max:int=30, size_min:int=3) -> None :
        """Initialize.

        Documented here: [MMS with rdkit](https://iwatobipen.wordpress.com/2016/02/01/create-matched-molecular-series-with-rdkit/),
        [Mishima-syk](https://github.com/Mishima-syk/py4chemoinformatics/blob/master/ch07_graph.asciidoc), 
        and [rdkit docs](http://rdkit.org/docs/source/rdkit.Chem.rdMMPA.html).            

        Examples:
            >>> import rdworks
            >>> libr = rdworks.read_smi('test.smi')
            >>> series = rdworks.MatchedSeries(libr)
        
        Args:
            mollibr (MolLibr): a library of molecules.
            sort_props (Union[List,str,None], optional): how to sort molecules within a series. Defaults to None.
            core_min (int, optional): min number of atoms for a core. Defaults to 5.
            core_max (int, optional): max number of atoms for a core. Defaults to 30.
            size_min (int, optional): min number of molecules for a series. Defaults to 3.

        Raises:
            TypeError: if `mollibr` is not rdworks.MolLibr object.
        """
        if isinstance(mollibr, MolLibr):
            self.mollibr = copy.deepcopy(mollibr) # a copy of MolLibr
        else:
            raise TypeError('MatchedSeries() expects rdworks.MolLibr object')
        if isinstance(sort_props, list):
            self.sort_props = sort_props
        elif isinstance(sort_props, str):
            self.sort_props = [ sort_props ]
        else:
            self.sort_props = [ 'HAC' ]
        self.core_min = core_min
        self.core_max = core_max
        self.size_min = size_min # minimum numer of R-groups in a series
        # for consistent drawing
        self.template_pattern = None
        self.template_coord2D = None
        self.series = self.libr_to_series() 
        
        
    def __str__(self) -> str:
        """Returns a string representation of object.

        Returns:
            str: string representation.
        """
        return f"<rdworks.MatchedSeries({self.count()})>"
    

    def __iter__(self) -> Iterator:
        """Yields an iterator of molecules.

        Yields:
            Iterator: iterator of molecules.
        """
        return iter(self.series)
    
    
    def __next__(self) -> Tuple:
        """Next series.

        Returns:
            Tuple: (scaffold_SMILES, [(r-group_SMILES, rdworks.Mol, *sort_props_values)
        """
        return next(self.series)
    

    def __getitem__(self, index:Union[int,slice]) -> Tuple:
        """Operator `[]`.

        Args:
            index (Union[int,slice]): index or indexes.

        Raises:
            ValueError: if series is empty or index is out of range.

        Returns:
            Tuple: (scaffold_SMILES, [(r-group_SMILES, rdworks.Mol, *sort_props_values)
        """
        if self.count() == 0:
            raise ValueError(f"MatchedSeries is empty")
        try:
            return self.series[index]
        except:
            raise ValueError(f"index should be 0..{self.count()-1}")
        

    def count(self) -> int:
        """Returns the count of series.

        Returns:
            int: count of series.
        """
        return len(self.series)
    

    def libr_to_series(self) -> List[Tuple]:
        """Returns a list of molecular series.

        Raises:
            RuntimeError: if a molecular cut cannot be defined.

        Returns:
            List[Tuple]: 
                [
                (scaffold_SMILES, [(r-group_SMILES, rdworks.Mol, *sort_props_values), ...,]),  
                ...,
                ]
        """
        series = defaultdict(list)
        for mol in self.mollibr:
            # make a single cut
            list_of_frag = rdMMPA.FragmentMol(mol.rdmol, maxCuts=1, resultsAsMols=False)
            # note: default parameters: maxCuts=3, maxCutBonds=20, resultsAsMols=True
            for _, cut in list_of_frag:
                try:
                    frag_smiles_1, frag_smiles_2 = cut.split('.')
                except:
                    raise RuntimeError(f'{mol.name} fragment_tuple= {cut}')
                n1 = Chem.MolFromSmiles(frag_smiles_1).GetNumHeavyAtoms()
                n2 = Chem.MolFromSmiles(frag_smiles_2).GetNumHeavyAtoms()
                # split scaffold core and rgroup symmetrically
                if n1 >= self.core_min and n1 <= self.core_max and n1 > n2: 
                    # frag_1 is the scaffold and frag_2 is the rgroup
                    series[frag_smiles_1].append((frag_smiles_2, mol))
                if n2 >= self.core_min and n2 <= self.core_max and n2 > n1: 
                    # frag_2 is the scaffold and frag_1 is the rgroup
                    series[frag_smiles_2].append((frag_smiles_1, mol))    
        # convert dict to list and remove size < self.size_min
        series = [(k,v) for k,v in series.items() if len(v) >= self.size_min]
        # sort by size (from the largest to the smallest)
        series = sorted(series, key=lambda x: len(x[1]), reverse=True)
        # sort by self.sort_props
        series_r_group_sorted = []
        for (scaffold_smi, r_group_) in series:
            r_group = []
            for (r_smi, mol) in r_group_:
                values = []
                for p in self.sort_props:
                    try:
                        v = mol.props[p]
                    except:
                        if p in rd_descriptor_f:
                            v = rd_descriptor_f[p](mol.rdmol) # calc. on the fly
                            mol.props.update({p:v})
                        else:
                            v = None
                    values.append(v)
                r_group.append((r_smi, mol, *values)) # unpack values i.e. a=[2,3] b=(1,*a) == (1,2,3)
            r_group = sorted(r_group, key=operator.itemgetter(slice(2, 2+len(self.sort_props))))
            series_r_group_sorted.append((scaffold_smi, r_group))
        return series_r_group_sorted
    

    def template(self, SMARTS:str, rdmol:Chem.Mol) -> None:
        """Sets drawing layout template.

        Args:
            SMARTS (str): SMARTS for template pattern.
            rdmol (Chem.Mol): template molecule.
        """
        
        self.template_pattern = Chem.MolFromSmarts(SMARTS)
        matched = rdmol.GetSubstructMatch(self.template_pattern)
        coords = [rdmol.GetConformer().GetAtomPosition(x) for x in matched]
        self.template_coords2D = [Geometry.Point2D(pt.x, pt.y) for pt in coords]


    def depict(self, smiles:str) -> Chem.Mol:
        """Draws a molecule according to self.template in a consistent way.

        Args:
            smiles (str): input molecule.

        Returns:
            Chem.Mol: 2D coordinated Chem.Mol for depiction.
        """
        rdmol_2d = Chem.MolFromSmiles(smiles)
        try:
            matched = rdmol_2d.GetSubstructMatch(self.template_pattern)
            coordDict = {}
            for i, coord in enumerate(self.template_coords2D):
                coordDict[matched[i]] = coord
            AllChem.Compute2DCoords(rdmol_2d, coordMap=coordDict)
        except:
            pass
        return rdmol_2d


    def report(self,
               workdir: os.PathLike = pathlib.Path("."),
               prefix: str = "mmseries",
               num_columns: int = 5,
               rgroup_width: int = 200,
               rgroup_height: int = 200,
               rgroup_max: int | None = None,
               scaffold_width: int = 300,
               scaffold_height: int = 300,
               ) -> None:
        """Writes individual series and an overview of series as HTML files.

        Args:
            workdir (os.PathLike, optional): working directory. Defaults to pathlib.Path(".").
            prefix (str, optional): prefix of output files. Defaults to "mmseries".
            num_columns (int, optional): number of molecules per row. Defaults to 5.
            rgroup_width (int, optional): width. Defaults to 200.
            rgroup_height (int, optional): height. Defaults to 200.
            rgroup_max (int, optional): max number of R-group molecules. Defaults to None.
            scaffold_width (int, optional): width. Defaults to 300.
            scaffold_height (int, optional): height. Defaults to 300.
        """
        scaffold_mols = []
        scaffold_legends = []
        scaffold_svgs = []
        
        for idx, (scaffold_smiles, list_tuples_r_groups) in enumerate(self.series, start=1):
            num = len(list_tuples_r_groups)
            scaffold_mols.append(Chem.MolFromSmiles(scaffold_smiles))
            scaffold_legends.append(f'Series #{idx} (n={num})')
            r_group_mols = []
            r_group_legends = []
            for (r_group_smiles, m, *values) in list_tuples_r_groups:
                # (r-group_SMILES, rdworks.Mol, *sort_props_values)
                values = list(map(str, values))
                r_group_mols.append(Chem.MolFromSmiles(r_group_smiles))
                r_group_legends.append(f'{m.name}\n{",".join(values)}')

            # individual series
            scaffold_svgs.append(render_svg(scaffold_mols[-1], 
                                        width = scaffold_width, 
                                        height = scaffold_height, 
                                        legend = scaffold_legends[-1]))
            
            # new HTML file
            HTML = '<html>'
            HTML += '<head>'
            HTML += '<meta charset="UTF-8">'
            HTML += '<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">'
            HTML += '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">'
            HTML += '<title>Matched Series Report</title>'
            HTML += '</head>'
            HTML += '<body>'
            HTML += f'<div>{scaffold_svgs[-1]}</div>'
            
            scaffold_orientations = get_attachment_orientation(scaffold_mols[-1])
            # orient r-group to scaffold attachment
            r_group_mols = [orient_rgroup_to_attachment(rg, scaffold_orientations) for rg in r_group_mols]
            # scale r-group coordinates
            r_group_mols = standardize_rgroup_scales(r_group_mols, 
                                                     target_bond_length=1.2,
                                                     reference_bond_type="C-C")
            HTML += '<table class="table table-bordered">'
            HTML += '<tbody>'
            HTML += '<tr>'
            truncated = False
            for i, (mol, legend) in enumerate(zip(r_group_mols, r_group_legends), start=1):
                if rgroup_max is not None and i > rgroup_max:
                    truncated = True
                    break
                rgroup_svg = render_svg(mol,
                                        width = rgroup_width, 
                                        height = rgroup_height, 
                                        legend = legend)
                HTML += f'<td>{rgroup_svg}</td>'
                if i % num_columns == 0:
                    HTML += '</tr><tr>'
            if i % num_columns != 0:
                HTML += '</tr>'
            HTML += '</tbody></table>'
            if truncated:
                HTML += f'<p>Note: R-groups are truncated to {rgroup_max} molecules</p>'
            HTML += '<script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>'
            HTML += '<script src="https://cdn.jsdelivr.net/npm/popper.js@1.12.9/dist/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>'
            HTML += '<script src="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>'
            HTML += '</body>'
            HTML += '</html>'

            # individual series
            with open(workdir / f"{prefix}-{idx:03d}-count-{num:03d}.html", "w") as html:    
                html.write(HTML)

        # overview of scaffolds
        HTML = '<html>'
        HTML += '<head>'
        HTML += '<meta charset="UTF-8">'
        HTML += '<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">'
        HTML += '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">'
        HTML += '<title>Matched Series Overview Report</title>'
        HTML += '</head>'
        HTML += '<body>'
        HTML += '<table class="table table-bordered">'
        HTML += '<tbody>'
        HTML += '<tr>'
        for i, svg in enumerate(scaffold_svgs, start=1):
            HTML += f'<td>{svg}</td>'
            if i % num_columns == 0:
                HTML += '</tr><tr>'
        if i % num_columns != 0:
            HTML += '</tr>'
        HTML += '</tbody></table>'
        HTML += '<script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>'
        HTML += '<script src="https://cdn.jsdelivr.net/npm/popper.js@1.12.9/dist/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>'
        HTML += '<script src="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>'
        HTML += '</body>'
        HTML += '</html>'

        with open(workdir / f"{prefix}-overview.html", "w") as html:
            html.write(HTML)