from __future__ import annotations

import torch
from rdkit import Chem
from foldeverything.data.bond_analyze import get_bond_order
from foldeverything.data.bond_analyze import allowed_bonds
from foldeverything.data import const


def infer_bonds(coords: torch.Tensor, atomic_numbers: torch.Tensor) -> torch.Tensor:

    elem = [const.atomic_num_to_element.get(int(z), "X") for z in atomic_numbers]
    dists = torch.cdist(coords, coords)
    bonds: list[tuple[int,int,int]] = []
    for i in range(len(elem)):
        for j in range(i):
            if elem[i] == "X" or elem[j] == "X":
                continue
            order = get_bond_order(elem[i], elem[j], dists[i, j].item())
            if order > 0:
                bonds.append((i, j, order))
    if not bonds:
        # If no bonds were detected, warning
        max_dist = float(dists.max().item())
        print(
            f"[WARNING] infer_bonds: no bonds inferred for molecule with {coords.shape[0]} atoms. "
            f"Largest inter-atomic distance = {max_dist:.2f} Å."
        )
    if bonds:
        return torch.tensor(bonds, dtype=torch.long, device=coords.device)
    else:
        return torch.empty((0, 3), dtype=torch.long, device=coords.device)


def rdkit_from_prediction(
    coords: torch.Tensor,
    atomic_numbers: torch.Tensor,
    bonds: torch.Tensor,
):
    print("in rdkit_from_prediction")
    rw = Chem.RWMol()
    for z in atomic_numbers.tolist():
        rw.AddAtom(Chem.Atom(int(z)))

    bt_map = {
        1: Chem.BondType.SINGLE,
        2: Chem.BondType.DOUBLE,
        3: Chem.BondType.TRIPLE,
    }
    for i, j, t in bonds.tolist():
        rw.AddBond(int(i), int(j), bt_map[int(t)])

    mol = rw.GetMol()
    try:
        Chem.SanitizeMol(mol, sanitizeOps=Chem.SanitizeFlags.SANITIZE_ALL ^ Chem.SanitizeFlags.SANITIZE_ADJUSTHS)
    except Exception as e:
        # geometrically invalid – keep going, just warn
        print(f"[warn] RDKit sanitise failed ({type(e).__name__}): {e}")
    else:
        print("\033[92m[ok]   RDKit sanitise passed\033[0m")
    #breakpoint()
    conf = Chem.Conformer(len(atomic_numbers))
    for idx, (x, y, z) in enumerate(coords.tolist()):
        conf.SetAtomPosition(idx, (x, y, z))
    mol.AddConformer(conf, assignId=True)
    return mol


def infer_ligand_token_bonds(
    feat: dict[str, torch.Tensor], update: bool = True
) -> tuple[torch.Tensor, torch.Tensor]:

    coords_raw = feat["coords"]
    if coords_raw.dim() == 3:
        coords = coords_raw[0]
    else:
        coords = coords_raw
    elements = torch.argmax(feat["ref_element"], dim=-1)  # (N_at,)
    atom_to_tok = torch.argmax(feat["atom_to_token"].int(), dim=-1)  # (N_at,)
    L = feat["token_pad_mask"].shape[0]

    ligand_mask = feat["mol_type"] == const.chain_type_ids["NONPOLYMER"]
    ligand_token_indices = torch.nonzero(ligand_mask).squeeze(-1)

    token_bonds = torch.zeros(L, L, 1, dtype=torch.float, device=coords.device)
    type_bonds = torch.zeros(L, L, dtype=torch.long, device=coords.device)

    if ligand_token_indices.numel() == 0:
        if update:
            feat["token_bonds"], feat["type_bonds"] = token_bonds, type_bonds
        return token_bonds, type_bonds

    ligand_atom_mask = torch.isin(atom_to_tok, ligand_token_indices)
    if ligand_atom_mask.sum() < 2:  # need at least two atoms to make a bond
        if update:
            feat["token_bonds"], feat["type_bonds"] = token_bonds, type_bonds
        return token_bonds, type_bonds

    coords_lig = coords[ligand_atom_mask]
    elems_lig = elements[ligand_atom_mask]

    bonds = infer_bonds(coords_lig, elems_lig)

    if bonds.numel() > 0:
        global_atom_idx = torch.nonzero(ligand_atom_mask).squeeze(-1)
        for i, j, t in bonds:
            gi = global_atom_idx[i.item()]
            gj = global_atom_idx[j.item()]
            ti, tj = atom_to_tok[gi], atom_to_tok[gj]
            token_bonds[ti, tj, 0] = 1.0
            token_bonds[tj, ti, 0] = 1.0
            type_bonds[ti, tj] = t
            type_bonds[tj, ti] = t
    if update:
        feat["token_bonds"], feat["type_bonds"] = token_bonds, type_bonds

    return token_bonds, type_bonds


# -------------------------------------------------------------
# Simple valence‐based stability check (borrowed from UniGEM)
# -------------------------------------------------------------


def check_stability(
    coords: torch.Tensor,
    atomic_numbers: torch.Tensor,
) -> tuple[bool, int, int]:
    """Assess valence correctness for a single molecule.

    Parameters
    ----------
    coords : (N, 3) tensor in Ångstrom.
    atomic_numbers : (N,) integer tensor of atomic numbers.

    Returns
    -------
    mol_ok : bool
        True if *all* atoms satisfy an allowed valence.
    n_ok : int
        Number of atoms with correct valence.
    N : int
        Total number of atoms in the molecule.
    """

    n_atoms = coords.shape[0]
    if n_atoms == 0:
        return False, 0, 0

    # Square distance matrix (Å) and valence accumulator.
    dists = torch.cdist(coords, coords)
    bond_sum = torch.zeros(n_atoms, dtype=torch.float, device=coords.device)

    # Map atomic numbers to element symbols once for speed.
    elems = [const.atomic_num_to_element.get(int(z), "X") for z in atomic_numbers]

    # Exhaustive pairwise bond inference.
    for i in range(n_atoms):
        ei = elems[i]
        if ei == "X":
            continue
        for j in range(i):
            ej = elems[j]
            if ej == "X":
                continue
            order = get_bond_order(ei, ej, dists[i, j].item(), check_exists=True)
            if order > 0:
                bond_sum[i] += order
                bond_sum[j] += order

    # Compare against allowed valence table.
    n_ok = 0
    for z, v in zip(elems, bond_sum):
        if z not in allowed_bonds:
            # If element not covered by table treat as invalid.
            continue
        allowed = allowed_bonds[z]
        if isinstance(allowed, int):
            if int(v.item()) == allowed:
                n_ok += 1
        else:  # list of possible valences
            if int(v.item()) in allowed:
                n_ok += 1

    mol_ok = n_ok == n_atoms
    return mol_ok, n_ok, n_atoms



def check_stability_from_bonds(
    atomic_numbers: torch.Tensor,
    bonds: torch.Tensor,
) -> tuple[bool, int, int]:

    n_atoms = atomic_numbers.shape[0]
    if n_atoms == 0:
        return False, 0, 0

    bond_sum = torch.zeros(n_atoms, dtype=torch.float, device=atomic_numbers.device)

    if bonds.numel() > 0:
        idx_i = bonds[:, 0].long()
        idx_j = bonds[:, 1].long()
        orders = bonds[:, 2].long()

        for a, b, o in zip(idx_i.tolist(), idx_j.tolist(), orders.tolist()):
            bond_sum[a] += int(o)
            bond_sum[b] += int(o)
    #breakpoint()
    elems = [const.atomic_num_to_element.get(int(z), "X") for z in atomic_numbers]

    n_ok = 0
    for z, v in zip(elems, bond_sum):
        if z not in allowed_bonds:
            continue
        allowed = allowed_bonds[z]
        val = int(v.item())
        if (isinstance(allowed, int) and val == allowed) or (
            isinstance(allowed, (list, tuple)) and val in allowed
        ):
            n_ok += 1
    #breakpoint()
    mol_ok = n_ok == n_atoms
    return mol_ok, n_ok, n_atoms
