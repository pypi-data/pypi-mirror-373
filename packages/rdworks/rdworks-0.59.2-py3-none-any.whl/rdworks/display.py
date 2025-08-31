import numpy as np

from PIL import Image, ImageChops
from io import BytesIO

from rdkit import Chem
from rdkit.Chem import AllChem, Draw, rdDepictor, rdMolTransforms
from rdkit.Chem.Draw import rdMolDraw2D
from rdkit.Chem.Draw import MolsMatrixToGridImage # new in RDKit 2023.09.1

# SVG optimization
from scour.scour import scourString


# https://greglandrum.github.io/rdkit-blog/posts/2023-05-26-drawing-options-explained.html


def trim_png(img:Image.Image) -> Image.Image:
    """Removes white margin around molecular drawing.

    Args:
        img (Image.Image): input PIL Image object.

    Returns:
        Image.Image: output PIL Image object.
    """
    bg = Image.new(img.mode, img.size, img.getpixel((0,0)))
    diff = ImageChops.difference(img,bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    
    if bbox:
        return img.crop(bbox)
    
    return img


def get_highlight_bonds(rdmol: Chem.Mol, atom_indices: list[int]) -> list[int] | None:
    """Get bond indices for bonds between atom indices.

    Args:
        rdmol (Chem.Mol): rdkit Chem.Mol object.
        atom_indices (list[int]): atom indices.

    Returns:
        list[int]: bond indices.
    """
    bond_indices = []
    for bond in rdmol.GetBonds():
        if bond.GetBeginAtomIdx() in atom_indices and bond.GetEndAtomIdx() in atom_indices:
            bond_indices.append(bond.GetIdx())
    
    if bond_indices:
        return bond_indices
    else:
        return None


def render_2D_mol(rdmol:Chem.Mol,
                  moldrawer:rdMolDraw2D, 
                  redraw: bool = False,
                  coordgen: bool = False,
                  legend: str = '', 
                  atom_index: bool = False, 
                  highlight_atoms: list[int] | None = None,
                  highlight_bonds: list[int] | None = None,
                  ) -> str:
    
    rdmol_2d = Chem.Mol(rdmol)
    
    if redraw or rdmol_2d.GetNumConformers() == 0:
        rdDepictor.SetPreferCoordGen(coordgen)
        rdmol_2d = Chem.RemoveHs(rdmol_2d)
        rdDepictor.Compute2DCoords(rdmol_2d)

    rdDepictor.StraightenDepiction(rdmol_2d)

    if (highlight_bonds is None) and (highlight_atoms is not None):
        # highlight bonds between the highlighted atoms
        highlight_bonds = get_highlight_bonds(rdmol_2d, highlight_atoms)

    draw_options = moldrawer.drawOptions()

    draw_options.addAtomIndices = atom_index
    # draw_options.setHighlightColour((0,.9,.9,.8)) # Cyan highlight
    # draw_options.addBondIndices = True
    # draw_options.noAtomLabels = True
    draw_options.atomLabelDeuteriumTritium = True  # D, T
    # draw_options.explicitMethyl = True
    draw_options.singleColourWedgeBonds = True
    draw_options.addStereoAnnotation = True
    # draw_options.fillHighlights = False
    # draw_options.highlightRadius = .4
    # draw_options.highlightBondWidthMultiplier = 12
    # draw_options.variableAtomRadius = 0.2
    # draw_options.variableBondWidthMultiplier = 40
    # draw_options.setVariableAttachmentColour((.5,.5,1))
    # draw_options.baseFontSize = 1.0 # default is 0.6
    # draw_options.annotationFontScale = 1
    # draw_options.rotate = 30 # rotation angle in degrees
    # draw_options.padding = 0.2 # default is 0.05

    # for atom in rdmol_2d.GetAtoms():
    #     for key in atom.GetPropsAsDict():
    #         atom.ClearProp(key)
    # if index: # index hides polar hydrogens
    #     for atom in rdmol_2d.GetAtoms():
    #        atom.SetProp("atomLabel", str(atom.GetIdx()))
    #     #    # atom.SetProp("atomNote", str(atom.GetIdx()))
    #     #    # atom.SetProp("molAtomMapNumber", str(atom.GetIdx()))        

    moldrawer.DrawMolecule(rdmol_2d, 
                           legend=legend, 
                           highlightAtoms=highlight_atoms, 
                           highlightBonds=highlight_bonds)
    moldrawer.FinishDrawing()
    
    return moldrawer.GetDrawingText()


def render_svg(rdmol: Chem.Mol, 
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
        rdmol (Chem.Mol): rdkit Chem.Mol object.
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

    svg_string = render_2D_mol(rdmol,
                                moldrawer = rdMolDraw2D.MolDraw2DSVG(width, height),
                                redraw = redraw, 
                                coordgen = coordgen,
                                legend = legend, 
                                atom_index = atom_index, 
                                highlight_atoms = highlight_atoms, 
                                highlight_bonds = highlight_bonds,
                                )

    if optimize:
        scour_options = {
            'strip_comments': True,
            'strip_ids': True,
            'shorten_ids': True,
            'compact_paths': True,
            'indent_type': 'none',
        }
        svg_string = scourString(svg_string, options=scour_options)

    return svg_string


def render_png(rdmol: Chem.Mol, 
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
        rdmol (Chem.Mol): rdkit Chem.Mol object.
        width (int, optional): width. Defaults to 300.
        height (int, optional): height. Defaults to 300.
        legend (str, optional): legend. Defaults to ''.
        atom_index (bool, optional): whether to show atom index. Defaults to False.
        highlight_atoms (list[int] | None, optional): atom(s) to highlight. Defaults to None.
        highlight_bonds (list[int] | None, optional): bond(s) to highlight. Defaults to None.
        redraw (bool, optional): whether to redraw. Defaults to False.
        coordgen (bool, optional): whether to use coordgen. Defaults to False.
    
    Returns:
        Image.Image: output PIL Image object.
    """

    png_string = render_2D_mol(rdmol,
                                moldrawer = rdMolDraw2D.MolDraw2DCairo(width, height),
                                redraw = redraw, 
                                coordgen = coordgen,
                                legend = legend, 
                                atom_index = atom_index, 
                                highlight_atoms = highlight_atoms, 
                                highlight_bonds = highlight_bonds,
                                )

    img = Image.open(BytesIO(png_string))

    if trim:
        img = trim_png(img)

    return img


def render_matrix_grid(rdmol: list[Chem.Mol],
                        legend: list[str] | None,
                        highlight_atoms: list[list[int]] | None = None,
                        highlight_bonds: list[list[int]] | None = None,
                        mols_per_row: int = 5,
                        width: int = 200,
                        height: int = 200,
                        atom_index: bool = False,
                        redraw: bool = False,
                        coordgen: bool = False,
                        svg: bool = True,
                        ) -> str | Image.Image:
    """Rendering a grid image from a list of molecules.

    Args:
        rdmol (list[Chem.Mol]): list of rdkit Chem.Mol objects.
        legend (list[str]): list of legends
        highlight_atoms (list[list[int]] | None, optional): list of atom(s) to highlight. Defaults to None.
        highlight_bonds (list[list[int]] | None, optional): list of bond(s) to highlight. Defaults to None.
        mols_per_row (int, optional): molecules per row. Defaults to 5.
        width (int, optional): width. Defaults to 200.
        height (int, optional): height. Defaults to 200.
        atom_index (bool, optional): whether to show atom index. Defaults to False.
        redraw (bool, optional): whether to redraw 2D. Defaults to False.
        coordgen (bool, optional): whether to use coordgen to depict. Defaults to False.

    Returns:
        str | Image.Image: SVG string or PIL Image object.

    Reference:
        https://greglandrum.github.io/rdkit-blog/posts/2023-10-25-molsmatrixtogridimage.html
    """

    n = len(rdmol)

    if isinstance(legend, list):
        assert len(legend) == n, "number of legends and molecules must be the same"
    elif legend is None:
        legend = ['',] * n
    
    if isinstance(highlight_atoms, list):
        assert len(highlight_atoms) == n, "number of highlights and molecules must be the same"
    elif highlight_atoms is None:
        highlight_atoms = [ (), ] * n

    if isinstance(highlight_bonds, list):
        assert len(highlight_bonds) == n, "number of highlights and molecules must be the same"    
    elif highlight_bonds is None:
        highlight_bonds = [ (), ] * n

    rdmol_matrix = []
    legend_matrix = []
    highlight_atoms_matrix = []
    highlight_bonds_matrix = []

    for i in range(0, n, mols_per_row):
        rdmol_matrix.append(rdmol[i:(i + mols_per_row)])
        legend_matrix.append(legend[i:(i + mols_per_row)])
        highlight_atoms_matrix.append(highlight_atoms[i:(i + mols_per_row)])
        highlight_bonds_matrix.append(highlight_bonds[i:(i + mols_per_row)])

    return MolsMatrixToGridImage(
            molsMatrix = rdmol_matrix,
            subImgSize = (width, height),
            legendsMatrix = legend_matrix,
            highlightAtomListsMatrix = highlight_atoms_matrix,
            highlightBondListsMatrix = highlight_bonds_matrix,
            useSVG = svg,
            returnPNG = False # whether to return PNG data (True) or a PIL object (False)
            )
    

def rescale(rdmol:Chem.Mol, factor:float=1.5) -> Chem.Mol:
    """Returns a copy of `rdmol` by a `factor`.

    Args:
        rdmol (Chem.Mol): input molecule.
        factor (float): scaling factor.
    
    Returns:
        Chem.Mol: a copy of rescaled rdkit.Chem.Mol object.
    """
    transformed_rdmol = Chem.Mol(rdmol)
    center = AllChem.ComputeCentroid(transformed_rdmol.GetConformer())
    tf = np.identity(4, np.float)
    tf[0][3] -= center[0]
    tf[1][3] -= center[1]
    tf[0][0] = tf[1][1] = tf[2][2] = factor
    AllChem.TransformMol(transformed_rdmol, tf)
    return transformed_rdmol


def rotation_matrix(axis:str, degree:float) -> np.ndarray:
    """Returns a numpy rotation matrix of shape (4,4).
    
    Args:
        axis (str): 'x' or 'y' or 'z'.
        degree (float): degree of rotation.

    Returns:
        np.ndarray: a numpy array of shape (4,4).
    """
    rad = (np.pi/180.0) * degree
    c = np.cos(rad)
    s = np.sin(rad)
    if axis.lower() == 'x':
        return np.array([
            [1., 0., 0., 0.],
            [0., c, -s,  0.],
            [0., s,  c,  0.],
            [0., 0., 0., 1.],
            ])
    elif axis.lower() == 'y':
        return np.array([
            [ c,  0., s,  0.],
            [ 0., 1., 0., 0.],
            [-s,  0., c,  0.],
            [ 0., 0., 0., 1.],
            ])
    elif axis.lower() == 'z':
        return np.array([
            [c, -s,  0., 0.],
            [s,  c,  0., 0.],
            [0., 0., 1., 0.],
            [0., 0., 0., 1.],
            ])


def rotate(rdmol:Chem.Mol, axis:str, degree:float) -> None:
    """Rotate `rdmol` around given axis and degree.

    Input `rdmol` will be modified.

    Args:
        rdmol (Chem.Mol): input molecule.
        axis (str): axis of rotation, 'x' or 'y' or 'z'.
        degree (float): degree of rotation.
    """
    try:
        conf = rdmol.GetConformer()
    except:
        AllChem.Compute2DCoords(rdmol)
        conf = rdmol.GetConformer()
    R = rotation_matrix(axis, degree)
    rdMolTransforms.TransformConformer(conf, R)
