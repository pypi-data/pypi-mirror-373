import numpy as np
import math
import itertools
import logging

from types import SimpleNamespace
from pathlib import Path
from rdworks import Conf, Mol
from rdworks.xtb.wrapper import GFN2xTB

from rdkit import Chem
from rdkit.Chem import (
    AllChem, RemoveHs, CanonSmiles, MolFromSmarts,
    GetFormalCharge, RWMol, AddHs, SanitizeMol, 
    MolToSmiles, MolFromSmiles,
    )

logger = logging.getLogger(__name__)


kT = 0.001987 * 298.0 # (kcal/mol K), standard condition
C = math.log(10) * kT



class Microstates():

    def __init__(self, origin: Mol, calculator: str = 'xTB'):
        self.origin = origin
        self.calculator = calculator
        self.basic_sites = []
        self.acidic_sites = []
        self.states = []
        self.mols = []
        self.reference = None
    

    def enumerate(self) -> None:
        # Qu pKake results must be stored at .confs
        for conf in self.origin:
            pka = conf.props.get('pka', None)
            if pka is None:
                # no protonation/deprotonation sites
                continue
            if isinstance(pka, str) and pka.startswith('tensor'):
                # ex. 'tensor(9.5784)'
                pka = float(pka.replace('tensor(','').replace(')',''))
            if conf.props.get('pka_type') == 'basic':
                self.basic_sites.append(conf.props.get('idx'))
            elif conf.props.get('pka_type') == 'acidic':
                self.acidic_sites.append(conf.props.get('idx'))

        # enumerate protonation/deprotonation sites to generate microstates

        np = len(self.basic_sites)
        nd = len(self.acidic_sites)
        P = [c for n in range(np+1) for c in itertools.combinations(self.basic_sites, n)]
        D = [c for n in range(nd+1) for c in itertools.combinations(self.acidic_sites, n)]
        
        PD = list(itertools.product(P, D))
        
        for (p, d) in PD:
            conf = self.origin.confs[0].copy()
            conf = conf.protonate(p).deprotonate(d).optimize(calculator=self.calculator)
            charge = len(p) - len(d)
            self.states.append(SimpleNamespace(
                charge=charge, 
                protonation_sites=p, 
                deprotonation_sites=d,
                conf=conf,
                smiles=Mol(conf).smiles,
                delta_m=None,
                PE=None))
            
        # sort microstates by ascending charges
        self.states = sorted(self.states, key=lambda x: x.charge)


    @staticmethod
    def Boltzmann_weighted_average(potential_energies: list) -> float:
        """Calculate Boltzmann weighted average potential energy at pH 0.

        Args:
            potential_energies (list): a list of potential energies.

        Returns:
            float: Boltzmann weighted average potential energy.
        """
        pe_array = np.array(potential_energies)
        pe = pe_array - min(potential_energies)
        Boltzmann_factors = np.exp(-pe/kT)
        Z = np.sum(Boltzmann_factors)
        p = Boltzmann_factors/Z

        return float(np.dot(p, pe_array))


    def populate(self) -> None:
        for microstate in self.states:
            mol = Mol(microstate.conf).make_confs(n=4).optimize_confs()
            # mol = mol.drop_confs(similar=True, similar_rmsd=0.3, verbose=True)
            # mol = mol.optimize_confs(calculator=calculator)
            # mol = mol.drop_confs(k=10, window=15.0, verbose=True)
            PE = []
            for conf in mol.confs:
                conf = conf.optimize(calculator=self.calculator, verbose=True)
                # GFN2xTB requires 3D coordinates
                # xtb = GFN2xTB(conf.rdmol).singlepoint(water='cpcmx', verbose=True)
                PE.append(conf.potential_energy(calculator=self.calculator))
                # xtb = GFN2xTB(conf.rdmol).singlepoint(verbose=True)
                # SimpleNamespace(
                #             PE = datadict['total energy'] * hartree2kcalpermol,
                #             Gsolv = Gsolv,
                #             charges = datadict['partial charges'],
                #             wbo = Wiberg_bond_orders,
                #             )
            microstate.PE = self.Boltzmann_weighted_average(PE)
            logger.info(f"PE= {PE}")
            logger.info(f"Boltzmann weighted= {microstate.PE}")            
            self.mols.append(mol)


    def get_populations(self, pH: float) -> list[tuple]:
        # set the lowest dG as the reference
        self.reference = self.states[np.argmin([microstate.PE for microstate in self.states])]
        for microstate in self.states:
            microstate.delta_m = microstate.charge - self.reference.charge
        dG = []
        for microstate in self.states:
            dG.append((microstate.PE - self.reference.PE) + microstate.delta_m * C * pH)
        dG = np.array(dG)

        logger.info(f"dG= {dG}")
        Boltzmann_factors = np.exp(-dG/kT)
        Z = np.sum(Boltzmann_factors)
        p = Boltzmann_factors/Z
        idx_p = sorted(list(enumerate(p)), key=lambda x: x[1], reverse=True)
        # [(0, p0), (1, p1), ...]

        return idx_p


    def get_ensemble(self) -> list[Mol]:
        return self.mols


    def get_mol(self, idx: int) -> Mol:
        return self.mols[idx]
    

    def count(self) -> int:
        return len(self.states)
    
