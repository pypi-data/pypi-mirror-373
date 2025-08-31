from pathlib import Path

from rdkit import Chem
from rdkit.Chem import AllChem, rdmolfiles

from rdworks import Conf, Mol, MolLibr
from rdworks.utils import compute, precheck_path, guess_mol_id

import pandas as pd
import re
import gzip


conf_name_convention = re.compile(r'[a-zA-Z0-9-_.!@#$%^&*()+=]+.[0-9]+/[0-9]+')


def read_csv(path:str | Path, smiles:str, name:str, std:bool=False, **kwargs) -> MolLibr:
    """Returns a library of molecules reading from a .csv file.

    Other columns will be read as properties.

    Args:
        path (Union[str, Path]): filename or path to a .csv file.
        smiles (str): column for SMILES.
        name (str): column for name.
        std (bool, optional): whether to standardize the input. Defaults to False.

    Raises:
        ValueError: if `smiles` or `name` column is not found in the csv file.

    Returns:
        MolLibr: a library of molecules.
    """
    path = precheck_path(path)
    df = pd.read_csv(path)
    try:
        assert smiles in list(df.columns)
    except:
        raise ValueError(f"Cannot find SMILES column (`smiles=`) {smiles}")
    try:
        assert name in list(df.columns)
    except:
        raise ValueError(f"Cannot find NAME column (`name=`) {name}")
    
    largs = [ (smiles, name, std) for smiles, name in zip(list(df[smiles]), list(df[name])) ]
    libr = MolLibr(compute(Mol, largs, desc='Reading CSV', **kwargs))

    # read other columns as properties
    # A list of dictionaries, where each dictionary represents a row, 
    # with column names as keys and cell values as values: 
    # [{column -> value}, ..., {column -> value}].
    csv_records = df.to_dict('records')
    for mol, row_dict in zip(libr, csv_records):
        mol.props.update({ k:v for (k,v) in row_dict.items() if k not in [smiles, name]})

    return libr


def merge_csv(libr: MolLibr, path:str | Path, on:str='name') -> MolLibr:
    """Returns a copy of MolLibr merged with properties from `on` column of a .csv file.

    Args:
        libr (MolLibr): library to be merged.
        path (Union[str, Path]): filename or path to a .csv file.
        on (str, optional): column for name. Defaults to 'name'.

    Raises:
        ValueError: if `on` column is not found in the csv file.

    Returns:
        MolLibr: a copy of library of molecules.
    """
    path = precheck_path(path)
    df = pd.read_csv(path)
    try:
        assert on in list(df.columns)
    except:
        raise ValueError(f"Cannot find ON column (`on=`) {on}")
    # A list of dictionaries, where each dictionary represents a row, 
    # with column names as keys and cell values as values: 
    # [{column -> value}, ..., {column -> value}].
    csv_records = df.to_dict('records')
    data = {}
    for row_dict in csv_records:
        data[row_dict[on]] = { k:v for (k,v) in row_dict.items() if k != on }
    
    merged_libr = libr.copy()

    for mol in merged_libr:
        if mol.name in data: # mol.props can be partly updated from csv
            mol.props.update(data[mol.name])
    
    return merged_libr


def read_dataframe(df:pd.DataFrame, smiles:str, name:str, std:bool=False) -> MolLibr:
    """Returns rdworks.MolLibr object from a pandas DataFrame.

    Args:
        df (pd.DataFrame): pandas.DataFrame.
        smiles (str): column for SMILES.
        name (str): column for name.
        std (bool, optional): whether to standardize the input. Defaults to False.

    Raises:
        TypeError: if `df` is not pandas DataFrame.
        ValueError: if `smiles` or `name` column is not found.

    Returns:
        MolLibr: a library of molecules.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expects a pandas.DataFrame object")
    try:
        assert smiles in list(df.columns)
    except:
        raise ValueError(f"Cannot find SMILES column (`smiles=`) {smiles}")
    try:
        assert name in list(df.columns)
    except:
        raise ValueError(f"Cannot find NAME column (`name=`) {name}")
    
    return MolLibr(list(df[smiles]), list(df[name]), std=std)



def read_smi(path:str | Path, std:bool = False, **kwargs) -> MolLibr:
    """Read a SMILES file and create a molecular library.

    Args:
        path (str | Path): path to the SMILES file.
        std (bool, optional): whether to standardize. Defaults to False.

    Raises:
        FileNotFoundError: when path does not exist.

    Returns:
        MolLibr: a library of molecules.
    """
    if not Path(path).exists():
        raise FileNotFoundError(f"Path {path} does not exist.")
    if path.suffix == '.gz':
        with gzip.open(path, "rb") as gz:
            largs = [ tuple(line.decode('utf-8').strip().split()[:2] + [std]) for line in gz ]
    else:
        with open(path, "r") as smi:
            largs = [ tuple(line.strip().split()[:2] +[std]) for line in smi ]
    return MolLibr(compute(Mol, largs, desc='Reading SMILES', **kwargs))



def _map_sdf(rdmol:Chem.Mol, name:str, std:bool, props:dict) -> Mol:
    """A map function for `read_sdf()` to return a rdworks.Mol object reading from a SDF entry.

    Args:
        rdmol (Chem.Mol): input molecule.
        name (str): name of the molecule.
        std (bool): whether to standardize the input SMILES.
        props (dict): dictionary of molecule properties.

    Returns:
        Mol: rdworks.Mol object.
    """
    obj = Mol(rdmol, name, std)
    obj.props = props
    return obj


def read_sdf(path:str | Path, std:bool=False, confs:bool=False, props:bool=True, **kwargs) -> MolLibr:
    """Returns a library of molecules reading from a SDF file.

    Args:
        path (Union[str, PosixPath]): filename or path to the .sdf file.
        std (bool, optional): whether to standardize the input. Defaults to False.
        confs (bool, optional): whether to read 3D conformers and keep hydrogens. Defaults to False.
        props (bool, optional): whether to read SDF properties. Defaults to True.

    Returns:
        MolLibr: a library of molecules.
    """
    path = precheck_path(path)
    if path.suffix == '.gz':
        with gzip.open(path, 'rb') as gz:
            # switch ^ True, XOR(^) inverts only if switch is True
            with Chem.ForwardSDMolSupplier(gz, sanitize=True, removeHs=(confs ^ True)) as gzsdf:
                    lrdmols = [ m for m in gzsdf if m is not None ]
    else:
        # switch ^ True, XOR(^) inverts only if switch is True
        with Chem.SDMolSupplier(path, sanitize=True, removeHs=(confs ^ True)) as sdf:
            lrdmols = [ m for m in sdf if m is not None ]
    
    if props:
        lprops = [ m.GetPropsAsDict() for m in lrdmols ]
        try:
            lnames = [ m.GetProp('_Name') for m in lrdmols ]
            assert len(set(lnames)) == len(lrdmols)
        except:
            (k, c, t) = guess_mol_id(lprops)
            if k is None:
                for i, m in enumerate(lrdmols, start=1):
                    name = f'_{i}_'
                    lnames.append(name)
            else:
                lnames = []
                for i, m in enumerate(lrdmols, start=1):
                    try:
                        name = m.GetProp(k)
                    except:
                        name = f'_{i}_'
                    lnames.append(name)
    else:
        lprops = [ None ] * len(lrdmols)
        lnames = [ None ] * len(lrdmols)
    
    largs = [ (rdmol, name, std, props) for rdmol, name, props in zip(lrdmols, lnames, lprops) ]

    obj = MolLibr()
    if confs: 
        # reading 3D SDF (conformers)
        last_smiles = None
        new_mol = None
        for rdmol, name, props in zip(lrdmols, lnames, lprops):
            # rdworks name convention (e.g. xxxx.yy/zzz)
            if conf_name_convention.match(name):
                (isomer_name, _) = name.split('/')
            else:
                isomer_name = name
            smiles = Chem.MolToSmiles(rdmol)  # canonicalized SMILES
            if last_smiles is None or last_smiles != smiles:
                if new_mol:
                    obj.libr.append(new_mol.rename())
                # start a new molecule
                rdmol_2d = Chem.RemoveHs(rdmol)
                AllChem.Compute2DCoords(rdmol_2d)
                # initialize a new molecule with the H-removed 2D
                new_mol = Mol(rdmol_2d, isomer_name, std=False) # atom indices remain unchanged.
            new_conf = Conf(rdmol)
            new_conf.props.update(props)
            new_mol.confs.append(new_conf)
            last_smiles = smiles
        if new_mol: # handle the last molecule
            obj.libr.append(new_mol.rename())
    else: 
        # reading 2D SDF
        obj = MolLibr(compute(_map_sdf, largs, desc='Reading SDF', **kwargs))

    return obj



def read_mae(path:str | Path, std:bool=False, confs:bool=True, **kwargs) -> MolLibr:
    """Returns a library of molecules reading from a Schrodinger Maestro file.

    Args:
        path (Union[str, Path]): filename or path to the .mae or .maegz file.
        std (bool, optional): whether to standardize the input. Defaults to False.
        confs (bool, optional): whether to read 3D conformers. Defaults to True.

    Returns:
        MolLibr: a library of molecules.
    """
    path = precheck_path(path)

    if path.suffix == '.maegz':
        with gzip.open(path, 'rb') as gz:
            # switch ^ True, XOR(^) inverts only if switch is True
            with rdmolfiles.MaeMolSupplier(gz, sanitize=True, removeHs=(confs ^ True)) as maegz:
                    lrdmols = [ m for m in maegz if m is not None ]
    else:
        # switch ^ True, XOR(^) inverts only if switch is True
        with rdmolfiles.MaeMolSupplier(path, sanitize=True, removeHs=(confs ^ True)) as mae:
            lrdmols = [ m for m in mae if m is not None ]

    lnames = [m.GetProp('_Name') for m in lrdmols]
    largs = [(rdmol, name, std) for rdmol, name in zip(lrdmols, lnames)]
    
    obj = MolLibr()

    if confs: # reading 3D SDF (conformers)
        last_smiles = None
        new_mol = None
        for rdmol, name in zip(lrdmols, lnames):
            # rdworks name convention (e.g. xxxx.yy/zzz)
            if conf_name_convention.match(name):
                (isomer_name, _) = name.split('/')
            else:
                isomer_name = name
            smiles = Chem.MolToSmiles(rdmol)  # canonicalized SMILES
            if last_smiles is None or last_smiles != smiles:
                if new_mol:
                    obj.libr.append(new_mol.rename())
                # start a new molecule
                # !!!! rdmol and new_mol do not have consistent atom indices !!!
                # idxmap: original atom index -> canonicalized rdmol atom index
                # smiles = Chem.MolToSmiles(rdmol) # canonicalization creates `_smilesAtomOutputOrder` property
                # idxord_o = ast.literal_eval(rdmol.GetProp("_smilesAtomOutputOrder"))
                # idxmap_o = {o.GetIdx():idxord_o.index(o.GetIdx()) for o in rdmol.GetAtoms()}
                rdmol_2d = Chem.RemoveHs(rdmol)
                AllChem.Compute2DCoords(rdmol_2d)
                new_mol = Mol(rdmol_2d, isomer_name, std=False) # atom indices remain unchanged.

            new_mol.confs.append(Conf(rdmol))
            
            last_smiles = smiles
        if new_mol: # handle the last molecule
            obj.libr.append(new_mol.rename())

    else: # reading 2D SDF
        obj = MolLibr(compute(Mol, largs, desc='Reading Mae', **kwargs))
    
    return obj