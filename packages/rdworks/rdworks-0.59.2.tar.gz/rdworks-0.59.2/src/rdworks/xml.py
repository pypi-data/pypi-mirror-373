"""
This module contains XML definitions for substructure and descriptor matching.

Available descriptors:

    Name          | Description                               | RDKit function
    ------------- | ----------------------------------------- | --------------------------------------
    HAC           | Num. of Non-H atoms                       | Descriptors.HeavyAtomCount
    HBA           | Num. of H-bond acceptors                  | Descriptors.NumHAcceptors
    HBD           | Num. of H-bond donors                     | Descriptors.NumHDonors
    LipinskiHBA   | Num. of Lipinski H-bond acceptors         | rdMolDescriptors.CalcNumLipinskiHBA
    LipinskiHBD   | Num. of Lipinski H-bond donors            | rdMolDescriptors.CalcNumLipinskiHBD
    MolWt         | Molecular weight                          | Descriptors.MolWt
    TPSA          | Topological polar surface area            | Descriptors.TPSA
    LogP          | log(octanol/water partition coefficient)  | Descriptors.MolLogP
    RotBonds      | Num. of rotatable bonds                   | Descriptors.NumRotatableBonds
    RingCount     | Num. of rings                             | Descriptors.RingCount
    FCsp3         | fraction of C atoms that are Sp3          | Descriptors.FractionCSP3
    rdHBD         | Num. of H-bond donors                     | rdMolDescriptors.CalcNumHBD
    rdHBA         | Num. of H-bond acceptors                  | rdMolDescriptors.CalcNumHBA
    rdRingCount   | Num. of rings                             | rdMolDescriptors.CalcNumRings
    rdRotBondst   | Num. of rotatable bonds                   | rdMolDescriptors.CalcNumRotatableBonds
    rdFCsp3       | fraction of C atoms that are Sp3          | rdMolDescriptors.CalcFractionCSP3
    Hetero        | Num. of non-H and non-C atoms             | rdMolDescriptors.CalcNumHeteroatoms
    ALogP         | Wildman-Crippen LogP value                | Crippen.MolLogP
    QED           | Quantitative estimation of drug-likeness  | QED.qed
    PSA           | MOE-like molecular surface area           | MolSurf.TPSA
    StereoCenters | Num. of atom stereo centers               | rdMolDescriptors.CalcNumAtomStereoCenters

References:

    1. `alert_collection.csv` is copied from Patrick Walters' blog and github:
        - http://practicalcheminformatics.blogspot.com/2018/08/filtering-chemical-libraries.html
        - https://github.com/PatWalters/rd_filters
    1. Jeroen Kazius, Ross McGuire, and Roberta Bursi.
        Derivation and Validation of Toxicophores for Mutagenicity Prediction. 
        J. Med. Chem. 2005, 48, 312-320.
    1. J. F. Blake. 
        Identification and Evaluation of Molecular Properties Related to Preclinical Optimization and Clinical Fate. 
        Med Chem. 2005, 1, 649-55.
    1. Mike Hann, Brian Hudson, Xiao Lewell, Rob Lifely, Luke Miller, and Nigel Ramsden. 
        Strategic Pooling of Compounds for High-Throughput Screening. 
        J. Chem. Inf. Comput. Sci. 1999, 39, 897-902.
    1. Jonathan B. Baell and Georgina A. Holloway. New Substructure Filters for Removal of Pan Assay Interference Compounds (PAINS) 
        from Screening Libraries and for Their Exclusion in Bioassays. 
        J. Med. Chem. 2010, 53, 2719-2740.
    1. Bradley C. Pearce, Michael J. Sofia, Andrew C. Good, Dieter M. Drexler, and David A. Stock. 
        An Empirical Process for the Design of High-Throughput Screening Deck Filters. 
        J. Chem. Inf. Model. 2006, 46, 1060-1068.
    1. Ruth Brenk, Alessandro Schipani, Daniel James, Agata Krasowski, Ian Hugh Gilbert, Julie Frearson aand Paul Graham Wyatt. 
        Lessons learnt from assembling screening libraries for drug discovery for neglected diseases. 
        ChemMedChem. 2008, 3, 435-44.
    1. Sivaraman Dandapani, Gerard Rosse, Noel Southall, Joseph M. Salvino, Craig J. Thomas. 
        Selecting, Acquiring, and Using Small Molecule Libraries for High‐Throughput Screening. 
        Curr Protoc Chem Biol. 2012, 4, 177–191.
    1. Huth JR, Mendoza R, Olejniczak ET, Johnson RW, Cothron DA, Liu Y, Lerner CG, Chen J, Hajduk PJ. 
        ALARM NMR: a rapid and robust experimental method to detect reactive false positives in biochemical screens. 
        J Am Chem Soc. 2005, 127, 217-24.
        - identificaiton of thiol reactive compounds by monitoring DTT-dependent 13-C chemical shift changes 
        of the human La protein in the presence of a test compound


Attributes:
    predefined_xml (Dict[Dict]): dictionary of XML files.
"""

import os
import importlib.resources
import pathlib
import xml.etree.ElementTree as ET
from typing import List, Tuple, Union


predefined_xml = {
    "Zinc_fragment" : {
        "Path" : "ZINC_fragment.xml",
        "Description" : "ZINC's fragment-like criteria",
        "Reference" : "ZINC",
    },
    "Zinc_leadlike" : {
        "Path" : "ZINC_leadlike.xml",
        "Description" : "ZINC's lead-like criteria",
        "Reference" : "ZINC",
    },
    "Zinc_druglike" : {
        "Path" : "ZINC_druglike.xml",
        "Description" : "ZINC's drug-like criteria",
        "Reference" : "ZINC",
    },
    "fragment" : {
        "Path" : "fragment.xml",
        "Description" : "fragment",
        "Reference" : "",
    },
    "MLSMR" : {
        "Path" : "ChEMBL_Walters/MLSMR.xml",
        "Description" : "NIH Mol. Lib. Small Molecule Repository filters",
        "Reference" : "Dandapani et al. (2012)",
    },
    "CNS" : {
        "Path" : "CNS.xml",
        "Description" : "CNS MPO descriptors",
        "Reference" : "Wager et al. (2010)",
    },
    "PAINS" : {
        "Path" : "Baell2010_PAINS/Baell2010A.xml",
        "Description" : "Pan Assay Interference (>150 hits)",
        "Reference" : "Baell et al. (2010)",
    },
    "Dundee" : {
        "Path" : "ChEMBL_Walters/Dundee.xml",
        "Description" : "Dundee NTD library filters",
        "Reference" : "Brenk et al. (2008)",
    },
    "BMS" : {
        "Path" : "ChEMBL_Walters/BMS.xml",
        "Description" : "BMS HTS deck filters",
        "Reference" : "Pearce et al. (2006)",
    },
    "LINT" : {
        "Path" : "ChEMBL_Walters/LINT.xml",
        "Description" : "Pfizer LINT filters",
        "Reference" : "Blake (2005)",
    },
    "Toxicophore" : {
        "Path" : "Kazius2005/Kazius2005.xml",
        "Description" : "Toxicophores for mutagenicity",
        "Reference" : "Kazius et al. (2005)",
    },
    "Glaxo" : {
        "Path" : "ChEMBL_Walters/Glaxo.xml",
        "Description" : "Glaxo hard filters",
        "Reference" : "Hann et al. (1999)",
    },
    "Acid" : {
        "Path" : "Hann1999_Glaxo/Hann1999Acid.xml",
        "Description" : "acid",
        "Reference" : "Hann et al. (1999)",
    },
    "Base" : {
        "Path" : "Hann1999_Glaxo/Hann1999Base.xml",
        "Description" : "base",
        "Reference" : "Hann et al. (1999)",
    },
    "Nucleophile" : {
        "Path" : "Hann1999_Glaxo/Hann1999NuPh.xml",
        "Description" : "nucleophile",
        "Reference" : "Hann et al. (1999)",
    },
    "Electrophile" : {
        "Path" : "Hann1999_Glaxo/Hann1999ElPh.xml",
        "Description" : "electrophile",
        "Reference" : "Hann et al. (1999)",
    },
    "Inpharmatica" : {
        "Path" : "ChEMBL_Walters/Inpharmatica.xml",
        "Description" : "Inpharmatica unwanted fragments",
        "Reference" : "ChEMBL",
    },
    "SureChEMBL" : {
        "Path" : "ChEMBL_Walters/SureChEMBL.xml",
        "Description" : "SureChEMBL filter",
        "Reference" : "ChEMBL",
    },
    "Reactive" : {
        "Path" : "misc/reactive.xml",
        "Description" : "reactive functional groups",
        "Reference" : "",
    },
    "Astex_RO3" : {
        "Path" : "Astex_RO3.xml",
        "Description" : "Astex rule of 3",
        "Reference" : "Astex",
    },
    "Asinex_fragment" : {
        "Path" : "Asinex_fragment.xml",
        "Description" : "Asinex's fragment",
        "Reference" : "Asinex",
    },
}


def list_predefined_xml() -> str:
    """Returns text output of list of predefined xml.

    Returns:
        str: text output of list of predefined xml
    """
    s = f"\n| {'Name':<18} | {'Description':<48} | {'Reference':<23} |\n"
    s += f"| {'-'*18} | {'-'*48} | {'-'*23} |\n"
    for k,v in predefined_xml.items():
        s += f"| {k:<18} | {v['Description']:<48} | {v['Reference']:<23} |\n"
    return s


def get_predefined_xml(name:str) -> os.PathLike:
    """Returns matched predefined xml file.
    
    Args:
        name (str): name of predefined entry.
    
    Returns:
        os.PathLike: path to the xml file.
    """
    t = name.upper()
    n = len(t)
    path = None
    for k in predefined_xml:
        if k.upper()[:n] == t:
            datadir = importlib.resources.files('rdworks.predefined')
            path = pathlib.Path(datadir / predefined_xml[k]['Path'])
            break
    if path is None:
      raise ValueError(f'is_matching() cannot find the xml file for {name}')  
    return path


def parse_xml(path:os.PathLike) -> Tuple:
    """Parse a XML file.

    Args:
        path (os.PathLike): filename of the xml.

    Returns:
        Tuple: parsed results.
    """
    tree = ET.parse(path)
    root = tree.getroot()
    terms = []
    try:
        combine = root.attrib['combine'].upper()
    except:
        combine = 'OR' # default
    for child in root:
        name = child.attrib['name']
        if child.tag == 'substructure':
            smarts = child.find('SMARTS').text
            terms.append((name, smarts, 0.0, 0.0))
        elif child.tag == 'descriptor':
            L = child.find('min')
            U = child.find('max')
            lb = float(L.text) if L is not None else None
            ub = float(U.text) if U is not None else None
            terms.append((name, None, lb, ub))
    
    # # parse SMARTS definitions
    # for substructure in tree.findall('substructure'):
    #     name = substructure.get('name')
    #     smarts = substructure.find('SMARTS').text
    #     terms.append((name, smarts, 0.0, 0.0))
    # # parse descriptors lower and upper bounds
    # for descriptor in tree.findall('descriptor'):
    #     name = descriptor.get('name')
    #     L = descriptor.find('min')
    #     U = descriptor.find('max')
    #     lb = float(L.text) if L is not None else None
    #     ub = float(U.text) if U is not None else None
    #     terms.append((name, '', lb, ub))
    
    return (terms, combine)