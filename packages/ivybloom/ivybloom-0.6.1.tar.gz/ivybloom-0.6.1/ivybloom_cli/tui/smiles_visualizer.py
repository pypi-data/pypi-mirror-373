from __future__ import annotations

from typing import Optional, Tuple


def _braille_from_bitmap(bitmap: "list[list[int]]", use_truecolor: bool = False) -> str:
    base = 0x2800
    h = len(bitmap)
    w = len(bitmap[0]) if h else 0
    cell_h = h // 4
    cell_w = w // 2
    lines = []
    for cy in range(cell_h):
        sb = []
        for cx in range(cell_w):
            mask = 0
            # 2x4 cell
            for dy in range(4):
                for dx in range(2):
                    y = cy * 4 + dy
                    x = cx * 2 + dx
                    if y < h and x < w and bitmap[y][x]:
                        if dx == 0:
                            mask |= [1, 2, 4, 64][dy]
                        else:
                            mask |= [8, 16, 32, 128][dy]
            ch = chr(base + mask) if mask else " "
            sb.append(ch)
        lines.append("".join(sb))
    return "\n".join(lines)


def render_smiles_unicode(smiles: str, width: int = 80, height: int = 20) -> str:
    """Render a SMILES string to a braille-based depiction.

    Tries RDKit if available; otherwise returns a textual summary.
    """
    try:
        from rdkit import Chem  # type: ignore
        from rdkit.Chem import Draw  # type: ignore
        from PIL import Image  # type: ignore
    except Exception:
        return f"SMILES: {smiles}\n[dim](RDKit not available for depiction)[/dim]"
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return f"Invalid SMILES: {smiles}"
        mol = Chem.AddHs(mol)
        size = (max(100, width * 12), max(80, height * 16))
        img = Draw.MolToImage(mol, size=size)
        # Convert to monochrome bitmap scaled to 2*width x 4*height pixels
        target_w = width * 2
        target_h = height * 4
        img = img.convert("L").resize((target_w, target_h), Image.BILINEAR)
        pixels = img.load()
        bitmap = [[1 if pixels[x, y] < 200 else 0 for x in range(target_w)] for y in range(target_h)]
        return _braille_from_bitmap(bitmap)
    except Exception as e:
        return f"SMILES render failed: {e}"


def summarize_smiles(smiles: str) -> str:
    try:
        from rdkit import Chem  # type: ignore
        from rdkit.Chem import Descriptors  # type: ignore
    except Exception:
        return f"SMILES: {smiles}"
    try:
        mol = Chem.MolFromSmiles(smiles)
        if not mol:
            return f"Invalid SMILES: {smiles}"
        mw = Descriptors.MolWt(mol)
        logp = Descriptors.MolLogP(mol)
        rings = Chem.GetSSSR(mol)
        formula = Chem.rdMolDescriptors.CalcMolFormula(mol)  # type: ignore
        return f"SMILES: {smiles}\nFormula: {formula}\nMW: {mw:.1f}\nlogP: {logp:.2f}\nRings: {int(rings)}"
    except Exception:
        return f"SMILES: {smiles}"


