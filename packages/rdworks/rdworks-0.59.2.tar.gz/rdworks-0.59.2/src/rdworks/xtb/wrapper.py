import os
import resource
import subprocess
import json
import tempfile
import logging
import shutil
import re

from pathlib import Path
from types import SimpleNamespace

from rdkit import Chem
from rdkit.Chem import rdmolops
from rdkit.Geometry import Point3D


logger = logging.getLogger(__name__)


# In ASE, the default energy unit is eV (electron volt).
# It will be converted to kcal/mol
# CODATA 2018 energy conversion factor
hartree2ev = 27.211386245988
hartree2kcalpermol = 627.50947337481
ev2kcalpermol = 23.060547830619026


class GFN2xTB:
    def __init__(self, molecule: Chem.Mol, ncores: int | None = None):
        assert isinstance(molecule, Chem.Mol), "molecule is not rdkit.Chem.Mol type"
        assert molecule.GetConformer().Is3D(), "molecule is not a 3D conformer"
        assert self.is_xtb_ready(), "xtb is not accessible"

        self.rdmol = molecule
        self.charge = rdmolops.GetFormalCharge(self.rdmol)
        self.natoms = molecule.GetNumAtoms()
        self.symbols = [ atom.GetSymbol() for atom in molecule.GetAtoms() ]
        self.positions = molecule.GetConformer().GetPositions().tolist()

        if ncores is None:
            ncores = os.cpu_count()

        # Parallelisation
        os.environ['OMP_STACKSIZE'] = '4G'
        os.environ['OMP_NUM_THREADS'] = f'{ncores},1'
        os.environ['OMP_MAX_ACTIVE_LEVELS'] = '1'
        os.environ['MKL_NUM_THREADS'] = f'{ncores}'
        
        # unlimit the system stack
        resource.setrlimit(resource.RLIMIT_STACK, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))


    @staticmethod
    def is_xtb_ready() -> bool:
        """Check if xtb is available.

        Returns:
            bool: True if `xtb` is available, False otherwise.
        """
        return shutil.which('xtb') is not None


    @staticmethod
    def is_optimize_ready() -> bool:
        try:
            h2o = [
                '$coord',
                ' 0.00000000000000      0.00000000000000     -0.73578586109551      o',
                ' 1.44183152868459      0.00000000000000      0.36789293054775      h',
                '-1.44183152868459      0.00000000000000      0.36789293054775      h',
                '$end',
            ]

            with tempfile.TemporaryDirectory() as temp_dir:
                test_geometry = os.path.join(temp_dir, 'coord')
                with open(test_geometry, 'w') as f:
                    f.write('\n'.join(h2o))
                proc = subprocess.run(['xtb', test_geometry, '--opt'],
                                      cwd=temp_dir,
                                      capture_output=True, 
                                      text=True,
                                      encoding='utf-8')
                assert proc.returncode == 0

            return True

        except:
            print("""                          
Conda installed xTB has the Fortran runtime error in geometry optimization. 
Please install xtb using the compiled binary:
                    
$ wget https://github.com/grimme-lab/xtb/releases/download/v6.7.1/xtb-6.7.1-linux-x86_64.tar.xz
$ tar -xf xtb-6.7.1-linux-x86_64.tar.xz
$ cp -r xtb-dist/bin/*      /usr/local/bin/
$ cp -r xtb-dist/lib/*      /usr/local/lib/
$ cp -r xtb-dist/include/*  /usr/local/include/
$ cp -r xtb-dist/share      /usr/local/ """)
            
            return False


    @staticmethod
    def is_cpx_ready() -> bool:
        """Checks if the CPCM-X command-line tool, `cpx`, is accessible in the system.

        Returns:
            bool: True if the cpx is found, False otherwise.
        """
        return shutil.which('cpx') is not None
    

    @staticmethod
    def is_cpcmx_ready() -> bool:
        """Checks if xtb works with the `--cpcmx` option.

        xtb distributed by the conda does not include CPCM-X function (as of June 17, 2025). 
        xtb installed from the github source codes by using meson and ninja includes it.

        Returns:
            bool: True if the --cpcmx option is working, False otherwise.
        """
        if GFN2xTB.is_xtb_ready():
            with tempfile.TemporaryDirectory() as temp_dir: # tmpdir is a string
                cmd = ['xtb', '--cpcmx']
                proc = subprocess.run(cmd, cwd=temp_dir, capture_output=True, text=True, encoding='utf-8')
                # we are expecting an error because no input file is given
                assert proc.returncode != 0
                for line in proc.stdout.split('\n'):
                    line = line.strip()
                    if 'CPCM-X library was not included' in line:
                        return False
        
        return True


    @staticmethod
    def is_ready() -> bool:
        """Check if `xtb` and `cpx` are accessible and `xtb --cpcmx` are available.

        Returns:
            bool: True if both `xtb` and `cpx` are accessible, False otherwise.
        """
        return all([GFN2xTB.is_xtb_ready(),
                    GFN2xTB.is_cpx_ready(),
                    GFN2xTB.is_cpcmx_ready(),
                    GFN2xTB.is_optimize_ready()])
    

    @staticmethod
    def version() -> str | None:
        """Check xtb version.

        Returns:
            str | None: version statement.
        """
        if GFN2xTB.is_xtb_ready():
            with tempfile.TemporaryDirectory() as temp_dir: # tmpdir is a string
                cmd = ['xtb', '--version']
                proc = subprocess.run(cmd, cwd=temp_dir, capture_output=True, text=True, encoding='utf-8')
                assert proc.returncode == 0, "GFN2xTB() Error: xtb not available"
                match = re.search('xtb\s+version\s+(?P<version>[\d.]+)', proc.stdout)
                if match:
                    return match.group('version')
            
        return None
    

    def to_xyz(self) -> str:
        """Export to XYZ formatted string.

        Returns:
            str: XYZ formatted string
        """
        lines = [f'{self.natoms}', ' ']
        for e, (x, y, z) in zip(self.symbols, self.positions):
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

        for (x, y, z), e in zip(self.positions, self.symbols):
            lines.append(f"{x:20.15f} {y:20.15f} {z:20.15f} {e}")
        
        lines.append("$end")

        return '\n'.join(lines)


    def load_xyz(self, geometry_input_path: Path) -> Chem.Mol:
        """Load geometry.

        Args:
            geometry_input_path (Path): pathlib.Path to the xyz 

        Returns:
            Chem.Mol: rdkit Chem.Mol object.
        """
        rdmol_opt = Chem.Mol(self.rdmol)
        with open(geometry_input_path, 'r') as f:
            for lineno, line in enumerate(f):
                if lineno == 0:
                    assert int(line.strip()) == self.natoms
                    continue
                elif lineno == 1: # comment or title
                    continue
                (symbol, x, y, z) = line.strip().split()
                x, y, z = float(x), float(y), float(z)
                atom = rdmol_opt.GetAtomWithIdx(lineno-2)
                assert symbol == atom.GetSymbol()
                rdmol_opt.GetConformer().SetAtomPosition(atom.GetIdx(), Point3D(x, y, z))
        
        return rdmol_opt


    def load_wbo(self, wbo_path: Path) -> dict[tuple[int, int], float]:
        """Load Wiberg bond order.

        singlepoint() creates a wbo output file.

        Args:
            wbo_path (Path): path to the wbo file.

        Returns:
            dict(tuple[int, int], float): { (i, j) : wbo, ... } where i and j are atom indices for a bond.
        """

        with open(wbo_path, 'r') as f:
            # Wiberg bond order (WBO)
            Wiberg_bond_orders = {}
            for line in f:
                line = line.strip()
                if line:
                    # wbo output has 1-based indices
                    (i, j, wbo) = line.split()
                    # changes to 0-based indices
                    i = int(i) - 1
                    j = int(j) - 1
                    # wbo ouput indices are ascending order
                    ij = (i, j) if i < j else (j, i)
                    Wiberg_bond_orders[ij] = float(wbo)

            return Wiberg_bond_orders


    def singlepoint(self, water: str | None = None, verbose: bool = False) -> SimpleNamespace:
        """Calculate single point energy.
        
        Total energy from xtb output in atomic units (Eh, hartree) is converted to kcal/mol.

        Options:
            ```sh
            -c, --chrg INT
                specify molecular charge as INT, overrides .CHRG file and xcontrol option
            
            --scc, --sp
                performs a single point calculation
            
            --gfn INT
                specify parametrisation of GFN-xTB (default = 2)
            
            --json
                write xtbout.json file
            
            --alpb SOLVENT [STATE]
                analytical linearized Poisson-Boltzmann (ALPB) model,
                available solvents are acetone, acetonitrile, aniline, benzaldehyde,
                benzene, ch2cl2, chcl3, cs2, dioxane, dmf, dmso, ether, ethylacetate, furane,
                hexandecane, hexane, methanol, nitromethane, octanol, woctanol, phenol, toluene,
                thf, water.
                The solvent input is not case-sensitive. The Gsolv
                reference state can be chosen as reference, bar1M, or gsolv (default).

            -g, --gbsa SOLVENT [STATE]
                generalized born (GB) model with solvent accessable surface (SASA) model,
                available solvents are acetone, acetonitrile, benzene (only GFN1-xTB), CH2Cl2,
                CHCl3, CS2, DMF (only GFN2-xTB), DMSO, ether, H2O, methanol,
                n-hexane (only GFN2-xTB), THF and toluene.
                The solvent input is not case-sensitive.
                The Gsolv reference state can be chosen as reference, bar1M, or gsolv (default).

            --cosmo SOLVENT/EPSILON
                domain decomposition conductor-like screening model (ddCOSMO),
                available solvents are all solvents that are available for alpb.
                Additionally, the dielectric constant can be set manually or an ideal conductor
                can be chosen by setting epsilon to infinity.

            --tmcosmo SOLVENT/EPSILON
                same as --cosmo, but uses TM convention for writing the .cosmo files.

            --cpcmx SOLVENT
                extended conduction-like polarizable continuum solvation model (CPCM-X),
                available solvents are all solvents included in the Minnesota Solvation Database.
            ```

        Args:
            water (str, optional) : water solvation model (choose 'gbsa' or 'alpb')
                alpb: ALPB solvation model (Analytical Linearized Poisson-Boltzmann).
                gbsa: generalized Born (GB) model with Surface Area contributions.

        Returns:
            SimpleNamespace(PE(total energy in kcal/mol), charges, wbo) 
        """

        with tempfile.TemporaryDirectory() as temp_dir: # tmpdir is a string
            workdir = Path(temp_dir)
            
            geometry_input_path = workdir / 'geometry.xyz'
            xtbout_path = workdir / 'xtbout.json'
            wbo_path = workdir / 'wbo'
            geometry_output_path = workdir / 'xtbtopo.mol'
            
            with open(geometry_input_path, 'w') as geometry:
                geometry.write(self.to_xyz())
            
            cmd = ['xtb', geometry_input_path.as_posix()]
            options = ['-c', str(self.charge), '--sp', '--gfn', '2', '--json']
            
            if water is not None and isinstance(water, str):
                if water == 'gbsa':
                    options += ['--gbsa', 'H2O']
                    # it does not provide Gsolv contribution to the total energy
                elif water == 'alpb':
                    options += ['--alpb', 'water']
                    # it does not provide Gsolv contribution to the total energy
                elif water == 'cpcmx' and self.is_cpcmx_ready():
                    options += ['--cpcmx', 'water']

            if verbose:
                logger.info(f"singlepoint() {' '.join(cmd+options)}")

            # 'xtbout.json', 'xtbrestart', 'xtbtopo.mol', 'charges', and 'wbo' files will be 
            # created in the current working directory.
            proc = subprocess.run(cmd + options, cwd=temp_dir, capture_output=True, text=True, encoding='utf-8')
            # if proc.returncode == 0:
            #     print("Standard Output:")
            #     print(proc.stdout)
            # else:
            #     print("Error:")
            #     print(proc.stderr)
            
            if proc.returncode == 0:
                if xtbout_path.is_file():
                    with open(xtbout_path, 'r') as f:
                        datadict = json.load(f) # takes the file object as input

                Gsolv = None
                                 
                if water is not None:
                    #  Free Energy contributions:                       [Eh]        [kcal/mol]
                    # -------------------------------------------------------------------------
                    #  solvation free energy (dG_solv):             -0.92587E-03    -0.58099
                    #  gas phase energy (E)                         -0.52068E+01
                    # -------------------------------------------------------------------------
                    #  total free energy (dG)                       -0.52077E+01
                    for line in proc.stdout.splitlines():
                        if 'solvation free energy' in line:
                            m = re.search(r"solvation free energy \(dG_solv\)\:\s+[-+]?\d*\.?\d+E[-+]?\d*\s+(?P<kcalpermol>[-+]?\d*\.?\d+)", line)
                            Gsolv = float(m.group('kcalpermol'))
                
                Wiberg_bond_orders = self.load_wbo(wbo_path)

                return SimpleNamespace(
                    natoms = self.natoms,
                    charge = self.charge,
                    PE = datadict['total energy'] * hartree2kcalpermol,
                    Gsolv = Gsolv, 
                    charges = datadict['partial charges'], 
                    wbo = Wiberg_bond_orders,
                    ) 
        
        # something went wrong if it reaches here          
        return SimpleNamespace()
                        


    def optimize(self, water: str | None = None, verbose: bool = False) -> SimpleNamespace:
        """Optimize geometry.

        Options:
            ```sh
            -c, --chrg INT
              specify molecular charge as INT, overrides .CHRG file and xcontrol option
            -o, --opt [LEVEL]
              call ancopt(3) to perform a geometry optimization, levels from crude, sloppy,
              loose, normal (default), tight, verytight to extreme can be chosen
            --gfn INT
              specify parametrisation of GFN-xTB (default = 2)
            --json
              write xtbout.json file
            ```

        Notes:
            Conda installed xtb has Fortran runtime error when optimizing geometry.
            ```sh
            Fortran runtime errror:
                At line 852 of file ../src/optimizer.f90 (unit = 6, file = 'stdout')
                Fortran runtime error: Missing comma between descriptors
                (1x,"("f7.2"%)")
                            ^
                Error termination.
            ```

        Args:
            water (str, optional) : water solvation model (choose 'gbsa' or 'alpb')
                alpb: ALPB solvation model (Analytical Linearized Poisson-Boltzmann).
                gbsa: generalized Born (GB) model with Surface Area contributions.

        Returns:
            (total energy in kcal/mol, optimized geometry)
        """
        with tempfile.TemporaryDirectory() as temp_dir: # tmpdir is a string
            workdir = Path(temp_dir)
            
            geometry_input_path = workdir / 'geometry.xyz'
            xtbout_path = workdir / 'xtbout.json'
            geometry_output_path = workdir / 'xtbopt.xyz'
            wbo_path = workdir / 'wbo'
            
            with open(geometry_input_path, 'w') as geometry:
                geometry.write(self.to_xyz())

            cmd = ['xtb', geometry_input_path.as_posix()]
            options = ['-c', str(self.charge), '-o', 'normal', '--gfn', '2', '--json']

            if water is not None and isinstance(water, str):
                if water == 'gbsa':
                    options += ['--gbsa', 'H2O']
                elif water == 'alpb':
                    options += ['--alpb', 'water']
                elif water == 'cpcmx':
                    logger.warning('optimize with --cpcmx option is not implemented in xtb yet')

            if verbose:
                logger.info(f"optimize() {' '.join(cmd+options)}")

            proc = subprocess.run(cmd + options, cwd=temp_dir, capture_output=True, text=True, encoding='utf-8')

            if proc.returncode == 0 and xtbout_path.is_file():
                with open(xtbout_path, 'r') as f:
                    datadict = json.load(f) # takes the file object as input
                
                Wiberg_bond_orders = self.load_wbo(wbo_path)
                rdmol_opt = self.load_xyz(geometry_output_path)
            
                return SimpleNamespace(
                        natoms = self.natoms,
                        charge = self.charge,
                        PE = datadict['total energy'] * hartree2kcalpermol,
                        charges = datadict['partial charges'],
                        wbo = Wiberg_bond_orders,
                        geometry = rdmol_opt,
                )

        # something went wrong if it reaches here
        return SimpleNamespace()
    

    def esp(self, water: str | None = None, verbose: bool = False) -> None:
        """Calculate electrostatic potential
        
        Example:
            v = py3Dmol.view()
            v.addVolumetricData(dt,
                                "cube.gz", {
                                    'isoval': 0.005,
                                    'smoothness': 2,
                                    'opacity':.9,
                                    'voldata': esp,
                                    'volformat': 'cube.gz',
                                    'volscheme': {
                                        'gradient':'rwb',
                                        'min':-.1,
                                        'max':.1,
                                        }
                                    });
            v.addModel(dt,'cube')
            v.setStyle({'stick':{}})
            v.zoomTo()
            v.show()
        """
        with tempfile.TemporaryDirectory() as temp_dir: # tmpdir is a string
            workdir = Path(temp_dir)
            if verbose:
                logger.info(f'xtb.optimize workdir= {temp_dir}')
            
            geometry_input_path = workdir / 'geometry.xyz'
            xtb_esp_dat = workdir / 'xtb_esp_dat'

            with open(geometry_input_path, 'w') as geometry:
                geometry.write(self.to_xyz())

            cmd = ['xtb', geometry_input_path.as_posix()]

            options = ['--esp', '--gfn', '2']

            if water is not None and isinstance(water, str):
                if water == 'gbsa':
                    options += ['--gbsa', 'H2O']
                elif water == 'alpb':
                    options += ['--alpb', 'water']

            proc = subprocess.run(cmd + options, cwd=temp_dir, capture_output=True, text=True, encoding='utf-8')
            # output files: xtb_esp.cosmo, xtb_esp.dat, xtb_esp_profile.dat

            if proc.returncode == 0 and xtb_esp_dat.is_file():
                with open(xtb_esp_dat, 'r') as f:
                    pass
        
        return None
