# SASA computation in numpy based on: https://ljmartin.github.io/blog/21_sasa_in_numpy.html

import numpy as np
from scipy.spatial.distance import cdist
import time


def golden_spiral(num_pts=150, radius=1):
    """
    Sample points evenly spread around a 3D unit sphere
    See stackoverflow post:
    https://stackoverflow.com/questions/9600801/evenly-distributing-n-points-on-a-sphere
    """
    indices = np.arange(0, num_pts, dtype=float) + 0.5
    phi = np.arccos(1 - 2 * indices / num_pts)
    theta = np.pi * (1 + 5**0.5) * indices
    x, y, z = np.cos(theta) * np.sin(phi), np.sin(theta) * np.sin(phi), np.cos(phi)
    points = np.vstack([x, y, z]).T
    return points


def calc_sasa(xyz, radii, solvent_radius=1.4, n=150):
    """
    xyz = (n_atoms,3) array of 3d atom coordinates
    radii = (1,) array of atom radii
    """
    pts = golden_spiral(n)  # points sampling the surface of a sphere.

    # generate a sphere of 'atom points', ap, on the vdw surface.
    ap = np.tile(pts, (xyz.shape[0], 1))

    # extend their distance from (0,0,0) by the radius+1.4
    sp = ap * (np.repeat(radii + solvent_radius + 1e-5, n)[:, None])
    sp = sp + np.repeat(xyz, n, axis=0)  # now translate to the atom centers
    fraction_outside = (
        ((cdist(sp, xyz) - (radii + solvent_radius)).min(1) > 0).reshape(-1, n).mean(1)
    )
    sasa = fraction_outside * (4 * np.pi * (radii + 1.4) ** 2)
    return sasa
