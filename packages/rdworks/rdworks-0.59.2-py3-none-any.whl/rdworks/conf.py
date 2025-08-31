import io
import copy
import json
import numpy as np
import ase
import itertools

from collections import namedtuple
from collections.abc import Callable
from typing import Self

from mendeleev import element
from ase.optimize import FIRE

from rdkit import Chem
from rdkit.Chem import rdMolTransforms, AllChem, rdMolAlign, rdmolops
from rdkit.Chem.Draw import rdMolDraw2D
from PIL import Image

from rdworks.std import clean_2d
from rdworks.torsion import get_torsion_atoms, create_torsion_fragment
from rdworks.units import ev2kcalpermol, pm2angstrom
from rdworks.utils import recursive_round, compress_string, decompress_string
from rdworks.xtb.wrapper import GFN2xTB
from rdworks.display import render_png, render_svg


class Conf:
    """Container for 3D conformers."""
    
    def __init__(self, 
                 molecule: str | Chem.Mol | None = None, 
                 name: str = '',
                 compressed: bool = False) -> None:
        """Initialize.

        Args:
            molecule (Chem.Mol | MolBlock string): Molecule for 3D conformer.
            name (str): Name prefix of the generated conformers. Defaults to ''.
            compressed (bool): whether the MolBlock string is compressed or not. 
                Defaults to False.

        Raises:
            ValueError: if `molecule` is not rdkit.Chem.Mol object.
        """
        assert isinstance(molecule, str | Chem.Mol) or molecule is None

        self.name = name
        self.rdmol = None   # must contain one and only one rdkit conformer
        self.natoms = 0
        self.charge = 0     # molecular formal charge
        self.spin = 1       # molecular spin multiplicity for ASE
        # Molecular spin multiplicity describes the number of possible orientations of 
        # spin angular momentum for a given molecule, essentially indicating the total 
        # number of unpaired electrons.
        # Spin Angular Momentum (S): up (+1/2) or down (-1/2)
        # Spin Multiplicity (2S + 1)
        # 0 unpaired electron  has S = 0,   2S + 1 = 0, called a singlet. 
        # 1 unpaired electron  has S = 1/2, 2S + 1 = 2, called a doublet (radical). 
        # 2 unpaired electrons has S = 1,   2S + 1 = 3, called a triplet.  
        
        self.props = {}

        if molecule is None:
            return

        if isinstance(molecule, str): # 3-D MolBLock string
            if compressed:
                molecule = decompress_string(molecule)
            try:
                self.rdmol = Chem.MolFromMolBlock(molecule, 
                                                  sanitize=False, 
                                                  removeHs=False, 
                                                  strictParsing=True)
            except:
                ValueError(f'Conf() Error: invalid MolBlock string')

        elif isinstance(molecule, Chem.Mol): # 3-D
            try:
                self.rdmol = molecule
            except:
                ValueError(f'Conf() Error: invalid Chem.Mol object')

        num_atoms = self.rdmol.GetNumAtoms()
        tot_atoms = self.rdmol.GetNumAtoms(onlyExplicit=False)
        
        assert num_atoms == tot_atoms, "Conf() Error: missing hydrogens"
        
        self.natoms = num_atoms
        self.charge = rdmolops.GetFormalCharge(self.rdmol)
        self.props.update({'atoms': self.natoms, 'charge': self.charge})
     
        assert self.rdmol.GetConformer().Is3D(), "Conf() Error: not 3D"

        

    def __str__(self) -> str:
        """Returns a string representation.

        Returns:
            str: string representation.
        """
        return f"<rdworks.Conf({self.rdmol} name={self.name} atoms={self.natoms})>"
       

    def copy(self) -> Self:
        """Returns a copy of self.

        Returns:
            Self: `rdworks.Conf` object.
        """
        return copy.deepcopy(self)
    

    def rename(self, name:str) -> Self:
        """Rename and returns self.

        Args:
            name (str): a new name for conformers.

        Raises:
            ValueError: if `name` is not given.

        Returns:
            Self: `rdworks.Conf` object.
        """
        if not name:
            raise ValueError('rdworks.Conf.rename() expects a name')
        self.name = name
        self.rdmol.SetProp('_Name', name)
        return self
    

    def sync(self, coord: np.ndarray | list) -> Self:
        """Synchronize the conformer coordinates with the provided `coord`.

        Args:
            coord (np.array): 3D coordinates.

        Raises:
            ValueError: if `coord` does not have the correct shape (natoms, 3).

        Returns:
            Self: `rdworks.Conf` object.
        """
        if isinstance(coord, np.ndarray) and coord.shape != (self.natoms, 3):
            raise ValueError(f"`coord.shape` should be ({self.natoms},3)")
        elif isinstance(coord, list) and len(coord) != self.natoms:
            raise ValueError(f"`coord` should be length of {self.natoms}")
        for i, a in enumerate(self.rdmol.GetAtoms()):
            self.rdmol.GetConformer().SetAtomPosition(a.GetIdx(), coord[i])
        
        return self


    def set_torsion(self, i:int, j:int, k:int, l:int, degree:float) -> Self:
        """Set dihedral angle (i-j-k-l) in degrees.

        Args:
            i (int): atom index
            j (int): atom index
            k (int): atom index
            l (int): atom index
            degree (float): dihedral angle in degrees

        Returns:
            Self: modified Conf object
        """
        rdMolTransforms.SetDihedralDeg(self.rdmol.GetConformer(), i, j, k, l, degree)

        return self
    
    
    def optimize(self, 
                 calculator: str | Callable = 'MMFF94',
                 fmax:float=0.05, 
                 max_iter:int=1000,
                 **kwargs) -> Self:
        """Optimize 3D geometry.

        Args:
            calculator (str | Callable): MMFF94 (= MMFF), MMFF94s, UFF, or ASE calculator.
                `MMFF94` or `MMFF` - Intended for general use, including organic molecules and proteins, 
                    and primarily relies on data from quantum mechanical calculations. 
                    It's often used in molecular dynamics simulations.
                `MMFF94s` - A "static" variant of MMFF94, with adjusted parameters for out-of-plane 
                    bending and dihedral torsions to favor planar geometries for specific nitrogen atoms. 
                    This makes it better suited for geometry optimization studies where a static, 
                    time-averaged structure is desired. The "s" stands for "static".
                `UFF` - UFF refers to the "Universal Force Field," a force field model used for 
                    molecular mechanics calculations. It's a tool for geometry optimization, 
                    energy minimization, and exploring molecular conformations in 3D space. 
                    UFF is often used to refine conformers generated by other methods, 
                    such as random conformer generation, to produce more physically plausible 
                    and stable structures.
            fmax (float, optional): fmax for the calculator convergence. Defaults to 0.05.
            max_iter (int, optional): max iterations for the calculator. Defaults to 1000.
            
        Args for xTB:
            water (str, optional): water solvation model (choose 'gbsa' or 'alpb')
                alpb: ALPB solvation model (Analytical Linearized Poisson-Boltzmann).
                gbsa: generalized Born (GB) model with Surface Area contributions.

        Returns:
            Self: self
        """
        if isinstance(calculator, str) :
            
            PE_start = self.singlepoint(calculator)
            PE_final = None
            
            if calculator.lower() == 'xTB'.lower():
                water = kwargs.get('water', None)
                results = GFN2xTB(self.rdmol).optimize(water=water)
                # SimpleNamespace(
                #         PE = datadict['total energy'] * hartree2kcalpermol,
                #         charges = datadict['partial charges'],
                #         wbo = Wiberg_bond_orders,
                #         geometry = rdmol_opt,
                # )
                try:
                    self.rdmol = results.geometry
                    PE_final = results.PE
                    retcode = 0
                except:
                    retcode = 1
                
            elif calculator.lower() == 'MMFF94'.lower() or calculator.lower() == 'MMFF'.lower():
                retcode = Chem.rdForceFieldHelpers.MMFFOptimizeMolecule(self.rdmol, 
                                                                        mmffVariant='MMFF94',
                                                                        maxIters=max_iter)
                # returns 0 if the optimization converged
            elif calculator.lower() == 'MMFF94s'.lower():
                retcode = Chem.rdForceFieldHelpers.MMFFOptimizeMolecule(self.rdmol, 
                                                                        mmffVariant='MMFF94s',
                                                                        maxIters=max_iter)
                # returns 0 if the optimization converged
            elif calculator.lower() == 'UFF'.lower():
                retcode = Chem.rdForceFieldHelpers.UFFOptimizeMolecule(self.rdmol,
                                                                       maxIters=max_iter)
                # returns 0 if the optimization converged

            if PE_final is None:
                PE_final = self.singlepoint(calculator)
            
            self.props.update({
                'E_tot_init(kcal/mol)': PE_start , # energy before optimization
                'E_tot(kcal/mol)': PE_final, # energy after optimization
                'Converged' : retcode == 0, # True or False
            })
            
            return self

        else:
            # assuming ASE calculator
            with io.StringIO() as logfile:
                ase_atoms = ase.Atoms(symbols=self.symbols(), positions=self.positions())
                ase_atoms.info['charge'] = self.charge
                ase_atoms.info['spin'] = self.spin
                ase_atoms.calc = calculator
                FIRE(ase_atoms, logfile=logfile).run(fmax=fmax)
                lines = [l.strip().split()[1:] for l in logfile.getvalue().split('\n') if l.startswith('FIRE')]
                data = [(float(e), float(f)) for (_, _, e, f) in lines]
                self.props.update({
                    'E_tot_init(kcal/mol)': data[0][0] * ev2kcalpermol, # energy before optimization
                    'E_tot(kcal/mol)': data[-1][0] * ev2kcalpermol, # energy after optimization
                    'Converged' : data[-1][1] < fmax, # True or False
                })
                
                # update atomic coordinates
                return self.sync(ase_atoms.get_positions())
 
    
    def protonate(self, atom_indices: list[int]) -> Self:
        """Protonate given non-hydrogen atoms.

        Args:
            atom_indices (list[int]): atom indices of non-hydrogen atoms to protonate.

        Returns:
            Self: self.
        """
        for idx in atom_indices:
            atom = self.rdmol.GetAtomWithIdx(idx)
            h = atom.GetNumExplicitHs()
            c = atom.GetFormalCharge()
            atom.SetNumExplicitHs(h+1)
            atom.SetFormalCharge(c+1)            
            Chem.SanitizeMol(self.rdmol)
            self.rdmol = Chem.AddHs(self.rdmol, addCoords=True)
            # The Chem.AddHs function in RDKit returns a new Mol object with hydrogens added to the molecule. 
            # It modifies the input molecule by adding hydrogens, 
            # but the original molecule remains unchanged.
        
        return self
    

    def deprotonate(self, atom_indices: list[int]) -> Self:
        """Deprotonate given non-hydrogen atoms.

        Args:
            atom_indices (list[int]): atom indices of non-hydrogen atoms to deprotonate.

        Returns:
            Self: self.
        """
        for idx in atom_indices:
            bonded_H_idx = None
            atom = self.rdmol.GetAtomWithIdx(idx)
            h = atom.GetNumExplicitHs()
            if h-1 >= 0 :
                atom.SetNumExplicitHs(h-1) # (h-1) must be unsigned int
            c = atom.GetFormalCharge()
            atom.SetFormalCharge(c-1)            
            neighbors = atom.GetNeighbors()
            
            for neighbor in neighbors:
                if neighbor.GetAtomicNum() == 1:
                    bonded_H_idx = neighbor.GetIdx()
                    break

            if bonded_H_idx is not None:
                edit_mol = Chem.EditableMol(self.rdmol)
                edit_mol.RemoveAtom(bonded_H_idx)
                self.rdmol = edit_mol.GetMol()
                Chem.SanitizeMol(self.rdmol)
        
        return self


    ##################################################
    ### Endpoint methods
    ##################################################

    def check_bonds(self, tolerance:float=0.25) -> bool:
        """Check bond lengths.

        Args:
            tolerance (float, optional): tolerance from the sum of 
                van der Waals radii of bonded atoms. Defaults to 0.25 (A).

        Returns:
            bool: True if all bond lengths are accceptable.
        """

        for bond in self.rdmol.GetBonds():
            idx1 = bond.GetBeginAtomIdx()
            idx2 = bond.GetEndAtomIdx()
            nuc1 = self.rdmol.GetAtomWithIdx(idx1).GetAtomicNum()
            nuc2 = self.rdmol.GetAtomWithIdx(idx2).GetAtomicNum()
            sum_radii = (element(nuc1).vdw_radius + element(nuc2).vdw_radius) * pm2angstrom
            bond_length = rdMolTransforms.GetBondLength(self.rdmol.GetConformer(), idx1, idx2)
            if abs(bond_length - sum_radii) > tolerance:
                return False
            
        return True
    

    def charge(self) -> int:
        """Returns molecular formal charge.

        Returns:
            int: charge
        """
        return self.charge
    

    def positions(self) -> np.array:
        """Returns the coordinates.

        Returns:
            np.array: the coordinates.
        """
        return np.array(self.rdmol.GetConformer().GetPositions().tolist())


    def symbols(self) -> list[str]:
        """Returns the element symbols.

        Returns:
            list: list of element symbols.
        """
        return [ a.GetSymbol() for a in self.rdmol.GetAtoms() ]


    def numbers(self) -> list[int]:
        """Returns the atomic numbers.

        Returns:
            list: list of atomic numbers.
        """
        return [ a.GetAtomicNum() for a in self.rdmol.GetAtoms() ]


    def cog(self) -> np.array:
        """Returns the center of geometry (COG).

        Returns:
            np.array: the center of geometry (COG).
        """
        xyz = []
        for i in range(0, self.natoms):
            pos = self.rdmol.GetConformer().GetAtomPositions(i)
            xyz.append([pos.x, pos.y, pos.z])
        return np.mean(xyz, axis=0)


    def rg(self) -> float:
        """Returns the radius of gyration (Rg).

        Returns:
            float: the radius of gyration (Rg).
        """
        xyz = []
        for i in range(0, self.natoms):
            pos = self.rdmol.GetConformer().GetAtomPositions(i)
            xyz.append([pos.x, pos.y, pos.z])
        xyz = np.array(xyz)
        cog = np.mean(xyz, axis=0)
        a = xyz-cog
        b = np.einsum('ij,ij->i', a, a)
        return np.sqrt(np.mean(b))


    def singlepoint(self, calculator: str | Callable = 'MMFF94', **kwargs) -> float:
        """Get potential energy and set `E_tot(kcal/mol)` in the self.props.

        Args:
            calculator (str | Callable): MMFF94 (= MMFF), MMFF94s, UFF, or ASE calculator.
                `MMFF94` or `MMFF` - Intended for general use, including organic molecules and proteins, 
                    and primarily relies on data from quantum mechanical calculations. 
                    It's often used in molecular dynamics simulations.
                `MMFF94s` - A "static" variant of MMFF94, with adjusted parameters for out-of-plane 
                    bending and dihedral torsions to favor planar geometries for specific nitrogen atoms. 
                    This makes it better suited for geometry optimization studies where a static, 
                    time-averaged structure is desired. The "s" stands for "static".
                `UFF` - UFF refers to the "Universal Force Field," a force field model used for 
                    molecular mechanics calculations. It's a tool for geometry optimization, 
                    energy minimization, and exploring molecular conformations in 3D space. 
                    UFF is often used to refine conformers generated by other methods, 
                    such as random conformer generation, to produce more physically plausible 
                    and stable structures.

        Returns:
            float | None: potential energy in kcal/mol or None.
        """
        if isinstance(calculator, str):
            if calculator.lower() == 'xTB'.lower():
                water = kwargs.get('water', None)
                results = GFN2xTB(self.rdmol).singlepoint(water=water)
                # SimpleNamespace(
                #     PE = datadict['total energy'] * hartree2kcalpermol,
                #     Gsolv = Gsolv, 
                #     charges = datadict['partial charges'], 
                #     wbo = Wiberg_bond_orders,
                #     )
                PE = results.PE
            
            elif calculator.lower() == 'MMFF94'.lower() or calculator.lower() == 'MMFF'.lower():
                mp = Chem.rdForceFieldHelpers.MMFFGetMoleculeProperties(self.rdmol, mmffVariant='MMFF94')
                ff = Chem.rdForceFieldHelpers.MMFFGetMoleculeForceField(self.rdmol, mp)
                PE = ff.CalcEnergy()
            
            elif calculator.lower() == 'MMFF94s'.lower():
                mp = Chem.rdForceFieldHelpers.MMFFGetMoleculeProperties(self.rdmol, mmffVariant='MMFF94s')
                ff = Chem.rdForceFieldHelpers.MMFFGetMoleculeForceField(self.rdmol, mp)
                PE = ff.CalcEnergy()
            
            elif calculator.lower() == 'UFF'.lower():
                ff = Chem.rdForceFieldHelpers.UFFGetMoleculeForceField(self.rdmol)
                PE = ff.CalcEnergy()
            
            else:
                raise ValueError("Unsupported calculator")                
            
            self.props.update({'E_tot(kcal/mol)': PE})

            return PE
        
        else:
            try:
                ase_atoms = ase.Atoms(symbols=self.symbols(), positions=self.positions())
                ase_atoms.info['charge'] = self.charge
                ase_atoms.info['spin'] = self.spin
                ase_atoms.calc = calculator
                PE = ase_atoms.get_potential_energy() # np.array
                if isinstance(PE, float):
                    PE = ev2kcalpermol * PE
                elif isinstance(PE, np.ndarray | list):
                    PE = ev2kcalpermol * float(PE[0]) # np.float64 to float
                self.props.update({'E_tot(kcal/mol)': PE})
            
                return PE
            
            except:
                raise RuntimeError("ASE calculator error")


    def torsion_atoms(self, strict: bool = True) -> dict[int, tuple]:
        """Determine torsion/dihedral angle atoms (i-j-k-l) and rotating group for each rotatable bond (j-k).

        Args:
            strict (bool): whether to exclude amide/imide/ester/acid bonds.

        Returns:
            {torsion_key: (i, j, k, l), ...,}
        """
        return {i: d[:4] for i, d in enumerate(get_torsion_atoms(self.rdmol, strict))}
    

    def torsion_energies_one(self,
                             calculator: str | Callable,
                             indices: tuple,
                             simplify: bool = True,
                             fmax: float = 0.05,
                             interval: float = 20.0,
                             use_converged_only: bool = True,
                             **kwargs) -> Self:
        """Calculate potential energy profile for a torsion angle.

        Args:
            calculator (str | Callable): 'MMFF', 'UFF', or ASE calculator.
            indices (tuple): atom indices (i,j,k,l) for a torsion angle
            simplify (bool, optional): whether to use fragementation. Defaults to True.
            fmax (float, optional): convergence limit for optimize. Defaults to 0.05.
            interval (float, optional): angle intervals. Defaults to 20.0.
            use_converged_only (bool, optional): whether to use only converged data. Defaults to True.

        Returns:
            Self: modified self.
        """
        ref_conf = self.copy()

        data = {'indices': indices,
                'angle': [], 
                'init': [], 
                'last': [], 
                'Converged': [],
                }
        
        if simplify:
            (frag, frag_ijkl, frag_created, wbo_filtered) = create_torsion_fragment(ref_conf.rdmol, indices)
            frag_conf = Conf(frag)
            for angle in np.arange(-180.0, 180.0, interval): 
                # Iterated numpy.ndarray does not contain the last 180: -180., ..., (180).
                conf = frag_conf.copy()
                conf.set_torsion(*frag_ijkl, angle) # atoms bonded to `l` move.
                conf = conf.optimize(calculator, fmax, **kwargs)
                data['angle'].append(angle)
                # conf.optimize() updates coordinates and conf.props: 
                #   `E_tot_init(kcal/mol)`, `E_tot(kcal/mol)`, `Converged`.
                data['init'].append(conf.props['E_tot_init(kcal/mol)'])
                data['last'].append(conf.props['E_tot(kcal/mol)'])
                data['Converged'].append(conf.props['Converged'])
                frag_cleaned, _ = clean_2d(frag, reset_isotope=True, remove_H=True)
                # to serialize the molecule
                data['frag'] = Chem.MolToMolBlock(frag_cleaned)
                data['frag_indices'] = frag_ijkl
        else:
            for angle in np.arange(-180.0, 180.0, interval): 
                # Iterated numpy.ndarray does not contain the last 180: -180., ..., (180).
                conf = ref_conf.copy()
                conf.set_torsion(*indices, angle) # atoms bonded to `l` move.
                conf = conf.optimize(calculator, fmax, **kwargs)
                data['angle'].append(angle)
                # conf.optimize() updates coordinates and conf.props: 
                #   `E_tot_init(kcal/mol)`, `E_tot(kcal/mol)`, `Converged`.
                data['init'].append(conf.props['E_tot_init(kcal/mol)'])
                data['last'].append(conf.props['E_tot(kcal/mol)'])
                data['Converged'].append(conf.props['Converged'])
        
        # Post-processing        
        if use_converged_only:
            data['angle'] = list(itertools.compress(data['angle'], data['Converged']))
            data['init' ] = list(itertools.compress(data['init' ], data['Converged']))
            data['last' ] = list(itertools.compress(data['last' ], data['Converged']))
        
        relax = np.array(data['init']) - np.median(data['last'])
        E_rel = relax - np.min(relax)

        torsion_energy_profile = {
            'indices' : data['indices'],
            'angle' : np.round(np.array(data['angle']), 1).tolist(), # np.ndarray -> list for serialization
            'E_rel(kcal/mol)': np.round(E_rel, 2).tolist(), # np.ndarray -> list for serialization
            }
        
        if simplify:
            torsion_energy_profile.update({
                'frag' : data.get('frag', None),
                'frag_indices' : data.get('frag_indices', None),
            })

        self.props['torsion'] = torsion_energy_profile
        self.props['torsion_calculator'] = str(calculator)

        return self
    

    def torsion_energies_batch(self,
                             batchoptimizer: Callable,
                             indices: tuple,
                             simplify: bool = True,
                             fmax: float = 0.05,
                             interval: float = 20.0,
                             use_converged_only: bool = True,
                             **kwargs) -> Self:
        """Calculate potential energy profile for torsion angles in a batch.

        Args:
            batchoptimizer (Callable): BatchOptimizer.
            indices (tuple): atom indices (i,j,k,l) for a torsion angle
            simplify (bool, optional): whether to use fragementation. Defaults to True.
            fmax (float, optional): convergence limit for optimize. Defaults to 0.05.
            interval (float, optional): angle intervals. Defaults to 20.0.
            use_converged_only (bool, optional): whether to use only converged data. Defaults to True.

        Returns:
            Self: modified self.
        """
        ref_conf = self.copy()

        data = {'indices': indices,
                'angle': [], 
                'init': [], 
                'last': [], 
                'Converged': [],
                }
        
        confs = []
        if simplify:
            (frag, frag_ijkl, frag_created, wbo_filtered) = create_torsion_fragment(ref_conf.rdmol, indices)
            frag_conf = Conf(frag)
            for angle in np.arange(-180.0, 180.0, interval): 
                # Iterated numpy.ndarray does not contain the last 180: -180., ..., (180).
                conf = frag_conf.copy()
                conf.set_torsion(*frag_ijkl, angle) # atoms bonded to `l` move.
                frag_cleaned, _ = clean_2d(frag, reset_isotope=True, remove_H=True)
                # to serialize the molecule
                data['frag'] = Chem.MolToMolBlock(frag_cleaned)
                data['frag_indices'] = frag_ijkl
                data['angle'].append(angle)
                confs.append(conf)
      
        else:
            for angle in np.arange(-180.0, 180.0, interval): 
                # Iterated numpy.ndarray does not contain the last 180: -180., ..., (180).
                conf = ref_conf.copy()
                conf.set_torsion(*indices, angle) # atoms bonded to `l` move.
                data['angle'].append(angle)
                confs.append(conf)
                
        batchsize_atoms = kwargs.get('batchsize_atoms', 16384)
        batches = prep_confs_batches(confs, batchsize_atoms)

        for batch in batches:
            optimized = batchoptimizer(batch.rdmols).run()
            for rdmol in optimized.mols:
                # conf.optimize() updates coordinates and conf.props: 
                #   `E_tot_init(kcal/mol)`, `E_tot(kcal/mol)`, `Converged`.
                data['init'].append(float(rdmol.GetProp('E_tot_init(kcal/mol)')))
                data['last'].append(float(rdmol.GetProp('E_tot(kcal/mol)')))
                data['Converged'].append(True if rdmol.GetProp('Converged') == 'True' else False)

        # Post-processing        
        if use_converged_only:
            data['angle'] = list(itertools.compress(data['angle'], data['Converged']))
            data['init' ] = list(itertools.compress(data['init' ], data['Converged']))
            data['last' ] = list(itertools.compress(data['last' ], data['Converged']))
        
        relax = np.array(data['init']) - np.median(data['last'])
        E_rel = relax - np.min(relax)

        torsion_energy_profile = {
            'indices' : data['indices'],
            'angle' : np.round(np.array(data['angle']), 1).tolist(), # np.ndarray -> list for serialization
            'E_rel(kcal/mol)': np.round(E_rel, 2).tolist(), # np.ndarray -> list for serialization
            }
        
        if simplify:
            torsion_energy_profile.update({
                'frag' : data.get('frag', None),
                'frag_indices' : data.get('frag_indices', None),
            })

        self.props['torsion'] = torsion_energy_profile
        self.props['torsion_calculator'] = str(batchoptimizer)

        return self

        
    def torsion_energies(self,
                         calculator: str | Callable,
                         torsion_key: int | None = None,
                         simplify: bool = True, 
                         fmax: float = 0.05,
                         interval: float = 20.0,
                         use_converged_only: bool = True,
                         **kwargs,
                         ) -> Self:
        """Calculates potential energy profiles for each torsion angle using ASE optimizer.

        It uses the first conformer as a reference.

        Args:
            calculator (str | Callable): 'MMFF', 'UFF', or ASE calculator.
            torsion_key (int | None): key to the torsion indices to calculate. Defaults to None (all).
            simplify (bool, optional): whether to use fragment surrogate. Defaults to True.
            fmax (float, optional): fmax of ASE optimizer. Defaults to 0.05.
            interval (float, optional): interval of torsion angles in degree. Defaults to 15.0.
            use_converged_only (bool, optional): whether to use only converged data. Defaults to True.
            batchsize_atoms (int, optional): max number of atoms in a batch. 
                Defaults to 16384(=16*1024). Disable batch optimization if smaller than conf.natoms.

        Returns:
            Self: modified self.
        """

        torsion_atoms_dict = self.torsion_atoms() # {0: (5, 4, 3, 1)}
        if (torsion_key is not None) and torsion_atoms_dict.get(torsion_key):
            torsion_atoms_dict = {torsion_key: torsion_atoms_dict.get(torsion_key)}
            # single torsion angle atom indices

        conf = self.copy()
        torsion_energy_profiles = {}
        if 'batchsize_atoms' in kwargs and kwargs.get('batchsize_atoms') >= conf.natoms:
            batchsize_atoms = kwargs.get('batchsize_atoms')
            for tk, indices in torsion_atoms_dict.items():
                conf = conf.torsion_energies_batch(calculator, 
                                                indices, 
                                                simplify, 
                                                fmax, 
                                                interval, 
                                                use_converged_only,
                                                batchsize_atoms=batchsize_atoms,
                                                )
                torsion_energy_profiles[tk] = conf.props['torsion']
        else:
            for tk, indices in torsion_atoms_dict.items():
                conf = conf.torsion_energies_one(calculator, 
                                                indices, 
                                                simplify, 
                                                fmax,
                                                interval, 
                                                use_converged_only,
                                                )
                torsion_energy_profiles[tk] = conf.props['torsion']
        
        self.props['torsion'] = torsion_energy_profiles
        self.props['torsion_calculator'] = str(calculator)

        return self
    

    def torsion_angle(self, i: int, j: int, k: int, l: int) -> float:
        """Get dihedral angle (i-j-k-l) in degrees.

        Args:
            i (int): atom index
            j (int): atom index
            k (int): atom index
            l (int): atom index

        Returns:
            float: dihedral angle in degrees.
        """
        degree = rdMolTransforms.GetDihedralDeg(self.rdmol.GetConformer(), i, j, k, l)

        return degree


    def dumps(self, key:str='') -> str:
        """Returns JSON dumps of the `props`.

        Args:
            key (str): a key for the `props` dictionary. Defaults to '' (all).

        Returns:
            str: JSON dumps.
        """
        if key:
            return json.dumps({key:self.props[key]})
        else:
            return json.dumps(self.props)
    

    def serialize(self, decimals: int = 3, compressed: bool = False) -> str:
        """Serialize information necessary to rebuild a Conf object.
        Args:
            decimals (int, optional): number of decimal places for float data type. Defaults to 3.

        Returns:
            str: serialized string for json.loads()
        """
        serialized = json.dumps({
            'name' : self.name,
            'natoms': self.natoms,
            'charge': self.charge,
            'spin': self.spin,
            'props' : recursive_round(self.props, decimals),
            'molblock' : self.to_molblock(),
            })

        if compressed:
            serialized = compress_string(serialized)
            
        return serialized


    def deserialize(self, serialized: str, compressed: bool = False) -> Self:
        """De-serialize information and rebuild a Conf object.
        
        Example:
            serialized = conf1.serialize()
            conf2 = Conf().deserialize(serialized)

        Args:
            serialized (str): serialized string.

        Returns:
            Self: modified self.
        """
        if compressed:
            serialized = decompress_string(serialized)

        data = json.loads(serialized)

        self.name = data['name']
        self.natoms = int(data['natoms'])
        self.charge = int(data['charge'])
        self.spin = int(data['spin'])
        self.props = data['props']
        self.rdmol = Chem.MolFromMolBlock(data['molblock'], sanitize=False, removeHs=False)

        return self


    def to_molblock(self, compressed: bool = False) -> str:
        """Returns MolBlock"""
        molblock = Chem.MolToMolBlock(self.rdmol)
        if compressed:
            molblock = compress_string(molblock)
        return molblock


    def to_xyz(self) -> str:
        """Returns XYZ formatted strings.

        Returns:
            str: XYZ formatted strings.
        """
        lines = [f'{self.natoms}', ' ']
        for e, (x, y, z) in zip(self.symbols(), self.positions()):
            lines.append(f'{e:5} {x:23.14f} {y:23.14f} {z:23.14f}')
        
        return '\n'.join(lines)


    def to_turbomole_coord(self, bohr: bool = False) -> str:
        """Returns TURBOMOLE coord file formatted strings.

        Turbomole coord file format:

            - It starts with the keyword `$coord`.
            - Each line after the $coord line specifies an atom, consisting of:
                - Three real numbers representing the Cartesian coordinates (x, y, z).
                - A string for the element name.
                - Optional: an "f" label at the end to indicate that the atom's coordinates are frozen during optimization.
            - Coordinates can be given in Bohr (default), Ångström (`$coord angs`), or fractional coordinates (`$coord frac`).
            - Optional data groups like periodicity (`$periodic`), lattice parameters (`$lattice`), and cell parameters (`$cell`) can also be included. 
            - Regarding precision:
                The precision of the coordinates is crucial for accurate calculations, especially geometry optimizations.
                Tools like the TURBOMOLEOptimizer might check for differences in atomic positions with a tolerance of 1e-13. 

        Args:
            bohr (bool): whether to use Bohr units of the coordinates. Defaults to False.
                Otherwise, Angstrom units will be used.
        
        Returns:
            str: TURBOMOLE coord formatted file.
        """
        if bohr:
            lines = ["$coord"]
        else:
            lines = ["$coord angs"]

        for (x, y, z), e in zip(self.positions(), self.symbols()):
            lines.append(f"{x:20.15f} {y:20.15f} {z:20.15f} {e}")
        
        lines.append("$end")

        return '\n'.join(lines)
        

    def to_sdf(self, props:bool=True) -> str:
        """Returns the SDF-formatted strings.

        Args:
            props (bool, optional): include `props as SDF properties. Defaults to True.

        Returns:
            str: strings in the SDF format.
        """
        in_memory = io.StringIO()
        with Chem.SDWriter(in_memory) as f:
            rdmol = Chem.Mol(self.rdmol)
            rdmol.SetProp('_Name', self.name)
            if props:
                for k,v in self.props.items():
                    rdmol.SetProp(k, str(v))
            f.write(rdmol)
        return in_memory.getvalue()


    def to_smi(self) -> str:
        """Returns SMILES containing explicit hydrogens

        Returns:
            str: SMILES
        """
        return Chem.MolToSmiles(self.rdmol)
    

    def to_png(self,
               width: int = 300, 
               height: int = 300,
               legend: str = '', 
               atom_index: bool = False, 
               highlight_atoms: list[int] | None = None,
               highlight_bonds: list[int] | None = None,
               redraw: bool = False,
               coordgen: bool = False,
               trim: bool = True) -> Image.Image:
        """Draw 2D molecule in PNG format.

        Args:
            width (int, optional): width. Defaults to 300.
            height (int, optional): height. Defaults to 300.
            legend (str, optional): legend. Defaults to ''.
            atom_index (bool, optional): whether to show atom index. Defaults to False.
            highlight_atoms (list[int] | None, optional): atom(s) to highlight. Defaults to None.
            highlight_bonds (list[int] | None, optional): bond(s) to highlight. Defaults to None.
            redraw (bool, optional): whether to redraw. Defaults to False.
            coordgen (bool, optional): whether to use coordgen. Defaults to False.
            trim (bool, optional): whether to trim white margins. Default to True.
        
        Returns:
            Image.Image: output PIL Image object.
        """
        
        return render_png(self.rdmol,
                          width = width, 
                          height = height, 
                          legend = legend, 
                          atom_index = atom_index, 
                          highlight_atoms = highlight_atoms,
                          highlight_bonds = highlight_bonds,
                          redraw = redraw, 
                          coordgen = coordgen, 
                          trim = trim)
    
    
    def to_svg(self,
               width: int = 300,
               height: int = 300,
               legend: str = '', 
               atom_index: bool = False, 
               highlight_atoms: list[int] | None = None,
               highlight_bonds: list[int] | None = None,
               redraw: bool = False,
               coordgen: bool = False,
               optimize: bool = True) -> str:
        """Draw 2D molecule in SVG format.

        Examples:
            For Jupyternotebook, wrap the output with SVG:

            >>> from IPython.display import SVG
            >>> SVG(libr[0].to_svg())

        Args:
            width (int, optional): width. Defaults to 300.
            height (int, optional): height. Defaults to 300.
            legend (str, optional): legend. Defaults to ''.
            atom_index (bool, optional): whether to show atom index. Defaults to False.
            highlight_atoms (list[int] | None, optional): atom(s) to highlight. Defaults to None.
            highlight_bonds (list[int] | None, optional): bond(s) to highlight. Defaults to None.
            redraw (bool, optional): whether to redraw. Defaults to False.
            coordgen (bool, optional): whether to use coordgen. Defaults to False.
            optimize (bool, optional): whether to optimize SVG string. Defaults to True.

        Returns:
            str: SVG string
        """
        return render_svg(self.rdmol, 
                          width = width, 
                          height = height, 
                          legend = legend, 
                          atom_index = atom_index, 
                          highlight_atoms = highlight_atoms,
                          highlight_bonds = highlight_bonds,
                          redraw = redraw, 
                          coordgen = coordgen, 
                          optimize = optimize)
    

def prep_confs_batches(confs: list[Conf], batchsize_atoms: int = 16384) -> list[namedtuple]:
    """Prepare batches of Chem.Mol conformers for batch optimization.

    - Each batch has up to `batchsize_atoms` number of atoms.
    - Each batch (namedtuple) has `rdmols`, `size`, `num_atoms` attributes.
    - Note that this function is not necessary for torsion energies 
        the batch-optimization of torsion energies are performed using internally prepared batches 
        of a series of conformers with different dihedral angles.

    Args:
        batchsize_atoms (int): max number of atoms in one batch. Defaults to 16384(=16*1024).

    Returns:
        list: list of batches.
    """
    Batch = namedtuple('Batch', ['rdmols', 'size', 'num_atoms'])
    batches = []
    batch_confs = []
    batch_atoms = 0
    for conf in confs:
        if (batch_atoms + conf.natoms) > batchsize_atoms:
            batches.append(Batch(rdmols=batch_confs, size=len(batch_confs), num_atoms=batch_atoms))
            # start over a new batch
            batch_confs = [ conf.rdmol ]
            batch_atoms = conf.natoms
        else:
            batch_confs.append(conf.rdmol)
            batch_atoms += conf.natoms
    if batch_atoms > 0: # last remaining batch
        batches.append(Batch(rdmols=batch_confs, size=len(batch_confs), num_atoms=batch_atoms))

    return batches


def batch_optimize(confs: list[Conf], calculator: Callable, **kwargs) -> list[Conf]:
    """Batch optimize a list of Conf objects using a given ASE calculator.

    Args:
        confs (list[Conf]): list of Conf objects to be optimized.
        calculator (Callable): batch optimizer.

    Returns:
        list[Conf]: list of optimized Conf objects.
    """
    batchsize_atoms = kwargs.get('batchsize_atoms', 16384)
    batches = prep_confs_batches(confs, batchsize_atoms=batchsize_atoms)
    optimized_confs = []
    for batch in batches:
        optimized = calculator(batch.rdmols, **kwargs).run()
        for rdmol in optimized.mols:
            conf = Conf(rdmol)
            conf.props = {
                'E_tot_init(kcal/mol)': float(rdmol.GetProp('E_tot_init(kcal/mol)')),
                'E_tot(kcal/mol)': float(rdmol.GetProp('E_tot(kcal/mol)')),
                'Converged': True if rdmol.GetProp('Converged') == 'True' else False,
            }
            optimized_confs.append(conf)
    
    return optimized_confs


def batch_singlepoint(confs: list[Conf], calculator: Callable, **kwargs) -> list[Conf]:
    """Batch singlepoint calculation for a list of Conf objects using a given ASE calculator.

    Args:
        confs (list[Conf]): list of Conf objects to be calculated.
        calculator (Callable): batch calculator.

    Returns:
        list[Conf]: list of Conf objects with updated properties.
    """
    batchsize_atoms = kwargs.get('batchsize_atoms', 16384)
    batches = prep_confs_batches(confs, batchsize_atoms=batchsize_atoms)
    calculated_confs = []
    for batch in batches:
        calculated = calculator(batch.rdmols, **kwargs).run()
        for rdmol in calculated.mols:
            conf = Conf(rdmol)
            conf.props = {
                'E_tot(kcal/mol)': float(rdmol.GetProp('E_tot(kcal/mol)')),
            }
            calculated_confs.append(conf)
    
    return calculated_confs
