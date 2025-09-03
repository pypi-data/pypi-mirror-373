from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any, Set, List, Union

import torch

from foldeverything.data import const
from foldeverything.model.potentials.schedules import ParameterSchedule


class Potential(ABC):
    def __init__(
        self,
        parameters: Optional[
            Dict[str, Union[ParameterSchedule, float, int, bool]]
        ] = None,
    ):
        self.parameters = parameters

    def compute(self, coords, feats, parameters):
        index, args, com_index, union_index = self.compute_args(feats, parameters)
        if index.shape[1] == 0:
            return torch.zeros(coords.shape[:-2], device=coords.device)
        if com_index is not None:
            coords = torch.zeros(
                (*coords.shape[:-2], com_index.max() + 1, 3), device=coords.device
            ).scatter_reduce(
                -2, com_index.unsqueeze(-1).expand_as(coords), coords, "mean"
            )
        value = self.compute_variable(coords, index, compute_gradient=False)
        energy = self.compute_function(value, *args)
        if union_index is not None:
            neg_exp_energy = torch.exp(-1 * parameters["union_lambda"] * energy)
            Z = torch.zeros(
                (*energy.shape[:-1], union_index.max() + 1), device=union_index.device
            ).scatter_reduce(
                -1,
                union_index.expand_as(neg_exp_energy),
                neg_exp_energy,
                "sum",
            )
            energy *= neg_exp_energy / Z[..., union_index]
        return energy.sum(dim=-1)

    def compute_gradient(self, coords, feats, parameters):
        index, args, com_index, union_index = self.compute_args(feats, parameters)
        if index.shape[1] == 0:
            return torch.zeros_like(coords)
        if com_index is not None:
            coords = torch.zeros(
                (*coords.shape[:-2], com_index.max() + 1, 3), device=coords.device
            ).scatter_reduce(
                -2, com_index.unsqueeze(-1).expand_as(coords), coords, "mean"
            )
            com_counts = torch.bincount(com_index)
        value, grad_value = self.compute_variable(coords, index, compute_gradient=True)
        energy, dEnergy = self.compute_function(value, *args, compute_derivative=True)
        if union_index is not None:
            neg_exp_energy = torch.exp(-1 * parameters["union_lambda"] * energy)
            Z = torch.zeros(
                (*energy.shape[:-1], union_index.max() + 1), device=union_index.device
            ).scatter_reduce(
                -1,
                union_index.expand_as(energy),
                neg_exp_energy,
                "sum",
            )
            softmax_energy = neg_exp_energy / Z[..., union_index]
            f = torch.zeros(
                (*energy.shape[:-1], union_index.max() + 1), device=union_index.device
            ).scatter_reduce(
                -1,
                union_index.expand_as(energy),
                energy * softmax_energy,
                "sum",
            )
            dEnergy *= softmax_energy * (
                1 + parameters["union_lambda"] * (energy - f[..., union_index])
            )
        grad_atom = torch.zeros_like(coords).scatter_reduce(
            -2,
            index.flatten(start_dim=0, end_dim=1)
            .unsqueeze(-1)
            .expand((*coords.shape[:-2], -1, 3)),
            dEnergy.tile(grad_value.shape[-3]).unsqueeze(-1)
            * grad_value.flatten(start_dim=-3, end_dim=-2),
            "sum",
        )

        if com_index is not None:
            grad_atom = (grad_atom / com_counts.unsqueeze(-1))[..., com_index, :]

        return grad_atom

    def compute_parameters(self, t):
        if self.parameters is None:
            return None
        parameters = {
            name: (
                parameter
                if not isinstance(parameter, ParameterSchedule)
                else parameter.compute(t)
            )
            for name, parameter in self.parameters.items()
        }
        return parameters

    @abstractmethod
    def compute_function(self, value, *args, compute_derivative=False):
        raise NotImplementedError

    @abstractmethod
    def compute_variable(self, coords, index, compute_gradient=False):
        raise NotImplementedError

    @abstractmethod
    def compute_args(self, t, feats, **parameters):
        raise NotImplementedError


class FlatBottomPotential(Potential):
    def compute_function(
        self, value, k, lower_bounds, upper_bounds, compute_derivative=False
    ):
        energy = torch.zeros_like(value)
        dEnergy = torch.zeros_like(value)
        if lower_bounds is not None:
            neg_overflow_mask = value < lower_bounds
            energy[neg_overflow_mask] = (k * (lower_bounds - value))[neg_overflow_mask]
            dEnergy[neg_overflow_mask] = (
                -1 * k.expand_as(neg_overflow_mask)[neg_overflow_mask]
            )
        if upper_bounds is not None:
            pos_overflow_mask = value > upper_bounds
            energy[pos_overflow_mask] = (k * (value - upper_bounds))[pos_overflow_mask]
            dEnergy[pos_overflow_mask] = (
                1 * k.expand_as(pos_overflow_mask)[pos_overflow_mask]
            )

        if not compute_derivative:
            return energy

        return energy, dEnergy


class HarmonicPotential(Potential):
    def compute_function(self, value, k, v_eq, compute_derivative=False):
        energy = k * (value - v_eq) ** 2
        if not compute_derivative:
            return energy

        dEnergy = 2 * k * (value - v_eq)
        return energy, dEnergy


class PeriodicPotential(Potential):
    def compute_function(self, value, k, n, phase, compute_derivative=False):
        energy = k * (1 + torch.cos(n * value - phase))
        if not compute_derivative:
            return energy

        dEnergy = -1 * k * n * torch.sin(n * value - phase)
        return energy, dEnergy


class DistancePotential(Potential):
    def compute_variable(self, coords, index, compute_gradient=False):
        r_ij = coords.index_select(-2, index[0]) - coords.index_select(-2, index[1])
        r_ij_norm = torch.linalg.norm(r_ij, dim=-1)
        r_hat_ij = r_ij / r_ij_norm.unsqueeze(-1)

        if not compute_gradient:
            return r_ij_norm

        grad_i = r_hat_ij
        grad_j = -1 * r_hat_ij
        grad = torch.stack((grad_i, grad_j), dim=1)

        return r_ij_norm, grad


class AnglePotential(Potential):
    def compute_variable(self, coords, index, compute_gradient=False):
        r_ij = coords.index_select(-2, index[0]) - coords.index_select(-2, index[1])
        r_ij_norm = torch.linalg.norm(r_ij, axis=-1)
        r_hat_ij = r_ij / r_ij_norm.unsqueeze(-1)

        r_kj = coords.index_select(-2, index[2]) - coords.index_select(-2, index[1])
        r_kj_norm = torch.linalg.norm(r_kj, axis=-1)
        r_hat_kj = r_kj / r_kj_norm.unsqueeze(-1)

        cos_theta = (r_hat_ij.unsqueeze(-2) @ r_hat_kj.unsqueeze(-1)).squeeze(-1, -2)
        theta = torch.arccos(cos_theta)

        if not compute_gradient:
            return theta

        dtheta = torch.sqrt(1 - (cos_theta**2)).unsqueeze(-1)
        grad_i = (
            dtheta
            * (r_hat_ij * cos_theta.unsqueeze(-1) - r_hat_kj)
            / r_ij_norm.unsqueeze(-1)
        )
        grad_k = (
            dtheta
            * (r_hat_kj * cos_theta.unsqueeze(-1) - r_hat_ij)
            / r_kj_norm.unsqueeze(-1)
        )
        grad_j = -1 * dtheta * (grad_i + grad_k)
        grad = torch.stack((grad_i, grad_j, grad_k), dim=1)

        return theta, grad


class DihedralPotential(Potential):
    def compute_variable(self, coords, index, compute_gradient=False):
        r_ij = coords.index_select(-2, index[0]) - coords.index_select(-2, index[1])
        r_kj = coords.index_select(-2, index[2]) - coords.index_select(-2, index[1])
        r_kl = coords.index_select(-2, index[2]) - coords.index_select(-2, index[3])

        n_ijk = torch.cross(r_ij, r_kj, dim=-1)
        n_jkl = torch.cross(r_kj, r_kl, dim=-1)

        r_kj_norm = torch.linalg.norm(r_kj, dim=-1)
        n_ijk_norm = torch.linalg.norm(n_ijk, dim=-1)
        n_jkl_norm = torch.linalg.norm(n_jkl, dim=-1)

        sign_phi = torch.sign(
            r_kj.unsqueeze(-2) @ torch.cross(n_ijk, n_jkl, dim=-1).unsqueeze(-1)
        ).squeeze(-1, -2)
        phi = sign_phi * torch.arccos(
            torch.clamp(
                (n_ijk.unsqueeze(-2) @ n_jkl.unsqueeze(-1)).squeeze(-1, -2)
                / (n_ijk_norm * n_jkl_norm),
                -1 + 1e-8,
                1 - 1e-8,
            )
        )

        if not compute_gradient:
            return phi

        a = (
            (r_ij.unsqueeze(-2) @ r_kj.unsqueeze(-1)).squeeze(-1, -2) / (r_kj_norm**2)
        ).unsqueeze(-1)
        b = (
            (r_kl.unsqueeze(-2) @ r_kj.unsqueeze(-1)).squeeze(-1, -2) / (r_kj_norm**2)
        ).unsqueeze(-1)

        grad_i = n_ijk * (r_kj_norm / n_ijk_norm**2).unsqueeze(-1)
        grad_l = -1 * n_jkl * (r_kj_norm / n_jkl_norm**2).unsqueeze(-1)
        grad_j = (a - 1) * grad_i - b * grad_l
        grad_k = (b - 1) * grad_l - a * grad_i
        grad = torch.stack((grad_i, grad_j, grad_k, grad_l), dim=1)
        return phi, grad


class AbsDihedralPotential(DihedralPotential):
    def compute_variable(self, coords, index, compute_gradient=False):
        if not compute_gradient:
            phi = super().compute_variable(
                coords, index, compute_gradient=compute_gradient
            )
            phi = torch.abs(phi)
            return phi

        phi, grad = super().compute_variable(
            coords, index, compute_gradient=compute_gradient
        )
        grad[(phi < 0)[..., None, :, None].expand_as(grad)] *= -1
        phi = torch.abs(phi)

        return phi, grad


class PoseBustersPotential(FlatBottomPotential, DistancePotential):
    def compute_args(self, feats, parameters):
        pair_index = feats["ligand_edge_index"][0]
        lower_bounds = feats["ligand_edge_lower_bounds"][0].float()
        upper_bounds = feats["ligand_edge_upper_bounds"][0].float()
        bond_mask = feats["ligand_edge_bond_mask"][0].bool()
        angle_mask = feats["ligand_edge_bond_mask"][0].bool()

        lower_bounds[bond_mask * ~angle_mask] *= 1.0 - parameters["bond_buffer"]
        upper_bounds[bond_mask * ~angle_mask] *= 1.0 + parameters["bond_buffer"]
        lower_bounds[~bond_mask * angle_mask] *= 1.0 - parameters["angle_buffer"]
        upper_bounds[~bond_mask * angle_mask] *= 1.0 + parameters["angle_buffer"]
        lower_bounds[bond_mask * angle_mask] *= 1.0 - min(
            parameters["angle_buffer"], parameters["angle_buffer"]
        )
        upper_bounds[bond_mask * angle_mask] *= 1.0 + min(
            parameters["angle_buffer"], parameters["angle_buffer"]
        )
        lower_bounds[~bond_mask * ~angle_mask] *= 1.0 - parameters["clash_buffer"]
        upper_bounds[~bond_mask * ~angle_mask] = float("inf")

        k = torch.ones_like(lower_bounds)

        return pair_index, (k, lower_bounds, upper_bounds), None, None


class VDWOverlapPotential(FlatBottomPotential, DistancePotential):
    def compute_args(self, feats, parameters):
        chain_id = feats["asym_id"]
        with torch.autocast("cuda", enabled=False):
            atom_chain_id = (
                torch.bmm(
                    feats["atom_to_token"].float(), chain_id.unsqueeze(-1).float()
                )
                .squeeze(-1)
                .long()
            )[0]

        vdw_radii = torch.zeros(
            const.num_elements, dtype=torch.float32, device=atom_chain_id.device
        )
        vdw_radii[1:119] = torch.tensor(
            const.vdw_radii, dtype=torch.float32, device=atom_chain_id.device
        )
        atom_vdw_radii = (
            feats["ref_element"].float() @ vdw_radii.unsqueeze(-1)
        ).squeeze(-1)[0]

        pair_index = torch.triu_indices(
            atom_chain_id.shape[0],
            atom_chain_id.shape[0],
            1,
            device=atom_chain_id.device,
        )
        pair_pad_mask = feats["atom_pad_mask"][0][pair_index].bool().all(dim=0)
        diff_chain_mask = pair_pad_mask * (
            atom_chain_id[pair_index[0]] != atom_chain_id[pair_index[1]]
        )
        pair_index = pair_index[:, diff_chain_mask]

        lower_bounds = atom_vdw_radii[pair_index].sum(dim=0) - 0.4
        upper_bounds = None
        k = torch.ones_like(lower_bounds)

        return pair_index, (k, lower_bounds, upper_bounds), None, None


class SymmetricChainCOMPotential(FlatBottomPotential, DistancePotential):
    def compute_args(self, feats, parameters):
        chain_id = feats["asym_id"]
        with torch.autocast("cuda", enabled=False):
            atom_chain_id = (
                torch.bmm(
                    feats["atom_to_token"].float(), chain_id.unsqueeze(-1).float()
                )
                .squeeze(-1)
                .long()
            )[0]

        pair_index = []
        for sym_set in feats["chain_symmetries"][0]:
            for i, chain_i in enumerate(sym_set):
                for j, chain_j in enumerate(sym_set):
                    if i <= j:
                        continue
                    pair_index.append([chain_i[0], chain_j[0]])
        pair_index = (
            torch.tensor(pair_index, dtype=torch.long, device=chain_id.device).T
            if len(pair_index) > 0
            else torch.empty((2, 0), dtype=torch.long, device=chain_id.device)
        )

        lower_bounds = torch.full(
            (pair_index.shape[1],),
            parameters["buffer"],
            dtype=torch.float32,
            device=chain_id.device,
        )
        upper_bounds = None
        k = torch.ones_like(lower_bounds)

        return pair_index, (k, lower_bounds, upper_bounds), atom_chain_id, None


class StereoBondAbsPotential(FlatBottomPotential, AbsDihedralPotential):
    def compute_args(self, feats, parameters):
        stereo_bond_index = feats["ligand_stereo_bond_index"][0]
        stereo_bond_orientations = feats["ligand_stereo_bond_orientations"][0].bool()

        lower_bounds = torch.zeros(
            stereo_bond_orientations.shape, device=stereo_bond_orientations.device
        )
        upper_bounds = torch.zeros(
            stereo_bond_orientations.shape, device=stereo_bond_orientations.device
        )
        lower_bounds[stereo_bond_orientations] = torch.pi - parameters["buffer"]
        upper_bounds[stereo_bond_orientations] = float("inf")
        lower_bounds[~stereo_bond_orientations] = float("-inf")
        upper_bounds[~stereo_bond_orientations] = parameters["buffer"]

        k = torch.ones_like(lower_bounds)

        return stereo_bond_index, (k, lower_bounds, upper_bounds), None, None


class StereoBondPotential(PeriodicPotential, DihedralPotential):
    def compute_args(self, feats, parameters):
        stereo_bond_index = feats["ligand_stereo_bond_index"][0]
        stereo_bond_orientations = feats["ligand_stereo_bond_orientations"][0].bool()

        k = torch.ones(
            stereo_bond_orientations.shape, device=stereo_bond_orientations.device
        )
        n = torch.ones_like(k)
        phase = torch.zeros_like(k)
        phase[~stereo_bond_orientations] = torch.pi

        return stereo_bond_index, (k, n, phase), None, None


class ChiralAtomPotential(FlatBottomPotential, DihedralPotential):
    def compute_args(self, feats, parameters):
        chiral_atom_index = feats["ligand_chiral_atom_index"][0]
        chiral_atom_orientations = feats["ligand_chiral_atom_orientations"][0].bool()

        lower_bounds = torch.zeros(
            chiral_atom_orientations.shape, device=chiral_atom_orientations.device
        )
        upper_bounds = torch.zeros(
            chiral_atom_orientations.shape, device=chiral_atom_orientations.device
        )
        lower_bounds[chiral_atom_orientations] = parameters["buffer"]
        upper_bounds[chiral_atom_orientations] = float("inf")
        upper_bounds[~chiral_atom_orientations] = -1 * parameters["buffer"]
        lower_bounds[~chiral_atom_orientations] = float("-inf")

        k = torch.ones_like(lower_bounds)

        return chiral_atom_index, (k, lower_bounds, upper_bounds), None, None


class AromaticRingPotential(FlatBottomPotential, AbsDihedralPotential):
    def compute_args(self, feats, parameters):
        ring_5_index = feats["ligand_aromatic_5_ring_index"][0].T
        ring_6_index = feats["ligand_aromatic_6_ring_index"][0].T
        double_bond_index = feats["ligand_planar_double_bond_index"][0].T

        range_5 = torch.arange(5, device=ring_5_index.device)
        ring_5_improper_index = torch.stack(
            ((range_5 + 1) % 5, (range_5 - 1) % 5, (range_5 + 2) % 5, range_5)
        )
        range_6 = torch.arange(6, device=ring_6_index.device)
        ring_6_improper_index = torch.stack(
            ((range_6 + 1) % 6, (range_6 - 1) % 6, (range_6 + 2) % 6, range_6)
        )
        double_bond_improper_index = torch.tensor(
            [[1, 2, 3, 0], [4, 5, 0, 3]], device=double_bond_index.device
        ).T

        all_improper_index = torch.cat(
            (
                ring_6_index[:, ring_6_improper_index]
                .swapaxes(0, 1)
                .flatten(start_dim=1),
                ring_5_index[:, ring_5_improper_index]
                .swapaxes(0, 1)
                .flatten(start_dim=1),
                double_bond_index[:, double_bond_improper_index]
                .swapaxes(0, 1)
                .flatten(start_dim=1),
            ),
            dim=1,
        )

        lower_bounds = None
        upper_bounds = torch.full(
            (all_improper_index.shape[-1],),
            parameters["buffer"],
            device=all_improper_index.device,
        )
        k = torch.ones_like(upper_bounds)

        return all_improper_index, (k, lower_bounds, upper_bounds), None, None


@dataclass
class GuidanceConfig:
    """Guidance configuration."""

    potentials: Optional[List[Potential]] = None
    guidance_update: Optional[bool] = None
    num_guidance_gd_steps: Optional[int] = None
    guidance_gd_step_size: Optional[int] = None
    fk_steering: Optional[bool] = None
    fk_resampling_interval: Optional[int] = 1
    fk_lambda: Optional[float] = 1.0
    fk_method: Optional[str] = None
    fk_batch_size: Optional[int] = 2
