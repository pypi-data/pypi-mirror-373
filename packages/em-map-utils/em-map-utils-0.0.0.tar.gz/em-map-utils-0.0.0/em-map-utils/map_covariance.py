"""
map_covariance.py

Author: Ardan Patwardhan
Affiliation: EMBL-EBI, Wellcome Genome Campus, CB10 1SD, UK
Date: 31/07/2025
Description: 
    Class for handling the covariance matrix of the map value
    distribution and related eigenvectors and eigenvalues.
"""

import argparse
import logging
import mrcfile
import numpy as np
from numpy import linalg as LA
from scipy.spatial.transform import Rotation as R
from .map_rotate import map_rotate

logger = logging.getLogger(__name__)

class MapCovariance:

    # Right-handed axes systems (24 in total).
    # Each column is one basis vector.
    # For some operations we need to find the closest RHS system. We
    # get determine a full set of RHS systems with the x,y, and z axes.
    RHAS_XYZ = np.array([np.diag([1, 1, 1]),
                         np.diag([1, -1, -1]),
                         np.diag([-1, 1, -1]),
                         np.diag([-1, -1, 1])])
    RHAS_ZYX = np.flip(np.array([np.diag([-1, -1, -1]),
                                 np.diag([-1, 1, -1]),
                                 np.diag([1, -1, 1]),
                                 np.diag([1, 1, -1])]), 2)
    RHAS_BASE = np.concatenate((RHAS_XYZ, RHAS_ZYX))
    RHAS_ALL = np.concatenate((RHAS_BASE, np.roll(RHAS_BASE, 1, axis=2), np.roll(RHAS_BASE, -1, axis=2)), axis=0)

    @staticmethod
    def sign_align_eigenvectors(evecs1, evecs2):
        """
        Two eigenvector systems may be very similar but look very different due to the signs.
        Here we change the signs of evec2 to make it as similar to evec1 while keeping to a
        right-handed system. In order to maintain a right handed system, two vectors need to
        change sign.

        Note: Eigenvectors are specified in different columns, e.g evecs[:,0], evecs[:,1], evecs[:,2].

        :param evecs1: First set of eigenvectors
        :param evecs2: Second set of eigenvectors
        :return: Second set of eigenvectors where the signs of the eigenvectors have been adjusted
        """

        evecs3 = evecs2

        # Check if 1st eigenvectors are anti-parallel
        if np.dot(evecs1[:, 0], evecs2[:, 0]) < np.dot(evecs1[:, 0], -evecs2[:, 0]):

            # If 2nd eigenvectors are anti-parallel, swap signs of #1 and #2, else #1 and #3
            if np.dot(evecs1[:, 1], evecs2[:, 1]) < np.dot(evecs1[:, 1], -evecs2[:, 1]):
                evecs3 = np.array([-evecs2[:, 0], -evecs2[:, 1], evecs2[:, 2]]).T
            else:
                evecs3 = np.array([-evecs2[:, 0], evecs2[:, 1], -evecs2[:, 2]]).T

        # Check if 2st eigenvectors are anti-parallel, if so swap signs of #2 and #3
        elif np.dot(evecs1[:, 1], evecs2[:, 1]) < np.dot(evecs1[:, 1], -evecs2[:, 1]):
            evec3 = np.array([evecs2[:, 0], -evecs2[:, 1], -evecs2[:, 2]]).T

        return evecs3

    @classmethod
    def find_closest_rhas(cls, vecs):
        """
        Given a triplet of basis vectors, find the closest match right
        handed coordinate system.

        :param vecs: Triplet of vectors, one in each column.
        :return: Closest matching right-handed system with each column
            representing a basis vector.
        """
        vec_dot = np.einsum('jk,ijk->i', vecs, cls.RHAS_ALL)
        ind = np.argmax(vec_dot)

        logger.debug(f"Scalar product of vector set with right-handed systems: {vec_dot}")

        return cls.RHAS_ALL[ind], ind

    @classmethod
    def align_map_principal_axes(cls,
                                 map_grid,
                                 axes=None,
                                 dtype=np.float32):
        """
        Determine the principal axes that corresponds to a map grid and rotate the map
        so that the principal axes are aligned with the axes specified.
        Notes:
        1) The axis vectors in axes are in columns, e.g., axis 0 = axes[:,0], axis 1 = axes[:,1].
        2) The principal axis will be ordered by eigenvalue in descending order and the first axis
           will be aligned to axes[:,0]

        :param map_grid: Map grid to be aligned.
        :param axes: Axis vectors to use as a reference when aligning principal axes. If None, the closest right-handed system to the eigenvectors will be used.
        :param dtype: Data type of the output arrays.
        :return: Aligned map grid, applied rotation, eigenvalues, and eigenvectors.
        """
        # Get eigenvectors/values for map
        map1_cov_info = cls(map_grid)
        # map1_cov_matrix, map1_centre_coos, map1_eigenvalues, map1_eigenvectors = map_covariance_matrix(map_grid)

        if axes is None:
            axes = cls.find_closest_rhas(map1_cov_info.eigenvectors)[0]

        # print(f'axes={axes}')
        # print_eigen_info("Map 1 before aligning first eigenvectors", map1_cov_matrix, map1_eigenvalues,
        #                  map1_eigenvectors)

        # Translation to move centre coos to centre of box
        box_centre = (np.asarray(np.shape(map_grid)) - 1.0) / 2.0
        map1_trans = box_centre - map1_cov_info.centre_coos
        logger.debug("Input map")
        logger.debug(f"Map translation: {map1_trans}")

        # Check that the first axis and first eigenvector are parallel
        # and not anti-parallel. In the latter case, negate the first
        # and one more of map2's eigenvectors to minimise the alignment
        # rotation needed to bring them into register and preserve a
        # right-handed system.
        map1_cov_info.eigenvectors = cls.sign_align_eigenvectors(axes, map1_cov_info.eigenvectors)
        logger.debug(map1_cov_info)
        # print_eigen_info("Map to align", map1_cov_matrix, map1_eigenvalues, map1_eigenvectors)

        # Calculate rotation to map eigenvectors onto axes
        rot1, rssd1 = R.align_vectors(axes.T, map1_cov_info.eigenvectors.T, weights=[np.inf, 1, 1])

        # Apply back rotation on map1 and calculate the eigenvectors/values
        map2 = map_rotate(map_grid, rot1, initial_translation=map1_trans)

        map2_cov_info = cls(map2)
        # map2_cov_matrix, map2_centre_coos, map2_eigenvalues, map2_eigenvectors = map_covariance_matrix(map2)
        # print_eigen_info("Map 2 before aligning first eigenvectors", map1_cov_matrix, map1_eigenvalues,
        #                  map1_eigenvectors)
        map2_cov_info.eigenvectors = cls.sign_align_eigenvectors(axes, map2_cov_info.eigenvectors)
        logger.debug(f"Aligned map: \n{map2_cov_info}\n")
        # print_eigen_info("Aligned map", map2_cov_matrix, map2_eigenvalues, map2_eigenvectors)

        return map2, rot1, map2_cov_info

    @classmethod
    def map_rotate_forward_backward(cls, map_grid, rotation):
        """
        Rotate map by the given rotation, estimate the rotation using
        the map's principal axes. Rotate the map back so that the map
        is once again aligned to the input map and then find the diff
        between the rotation matrices of the input and back-rotated map.
        This method is useful for testing purposes.

        :param map_grid: Input map.
        :param rotation: SciPy rotation to apply to input map.
        :return: Tuple with rotated map, back-rotated map and back
            rotation.
        """

        map1_cov_info = cls(map_grid)
        logger.debug("Input map")
        logger.debug(map1_cov_info)

        # Rotate map1
        rot_map = map_rotate(map_grid, rotation)

        # Align map
        back_rot_map, rot2, back_rot_map_cov_info = cls.align_map_principal_axes(rot_map, map1_cov_info.eigenvectors)

        inv_rot1_matrix = rotation.inv().as_matrix()
        inv_rot2_matrix = rot2.as_matrix()
        logger.debug(f"\nInverse of input rotation matrix:\n{inv_rot1_matrix}\n")
        logger.debug(f"\nBack rotation from eigenvectors:\n{inv_rot2_matrix}\n")
        logger.debug(f"\nDifference matrix:\n{inv_rot1_matrix - inv_rot2_matrix}\n")

        return rot_map, back_rot_map, rot2

    def phys_scale_eigenvectors(self, mrc):
        """
        Using the voxel sizes from an MRC file to scale the eigen-
        vectors to Ångstroms. Note although the voxel size in the three
        dimensions is almost always the same in cryoEM, this routine
        takes into account that they may not be. However this feature
        has not been tested.

        :param mrc: MRC file with voxel sizes.
        :return: Vector with scalings for each of the eigenvectors.
        """

        # Get voxel sizes along i,j,k from sizes along x,y,z
        vox = (mrc.voxel_size.x, mrc.voxel_size.y, mrc.voxel_size.z)
        vox_ijk = np.array([vox[mrc.header.maps - 1],
                            vox[mrc.header.mapr - 1],
                            vox[mrc.header.mapc - 1]]).reshape((3, 1))
        svec = np.sqrt(np.sum((self.eigenvectors * vox_ijk) ** 2, axis=0))
        logger.debug(f"Scaling vector: {svec}")

        return svec

    def lengths_from_eigenvalues(self, mrc):
        """
        The eigenvalues are related to the extent of the map value
        distribution along the principal axes. This routine attempts
        to estimate the physical extents of the map value distribution
        using different estimates.

        :param mrc: MRC file contain voxel sizes.
        :return: Tuple with FWHM, two sigma and sphere diameter lengths.
        """
        scale_vec = self.phys_scale_eigenvectors(mrc)
        sigma = scale_vec * np.sqrt(self.eigenvalues)

        two_sigma = 2 * sigma
        logger.debug(f"Two sigma lengths: {two_sigma}")

        fwhm = 2 * np.sqrt(2 * np.log(2)) * sigma
        logger.debug(f"FWHM: {fwhm}")

        sphere_diameter = 2 * np.sqrt(5) * sigma
        logger.debug(f"Sphere diameter: {sphere_diameter}")

        return fwhm, two_sigma, sphere_diameter

    def __init__(self, map_grid):
        """
        Setup class with the covariance matrix of the map value
        distribution, the centre coordinates, eigenvectors, and
        eigenvalues.
    
        :param map_grid: 3D volume as numpy grid
        """

        sum_grid_values = map_grid.sum()
        grid_ranges = [range(x) for x in np.shape(map_grid)]
        index_grid = np.ogrid[grid_ranges]
        self.centre_coos = [np.einsum('ijk,ijk', gx, map_grid, optimize=True) for gx in index_grid] / sum_grid_values

        def f(u, v):
            return np.einsum('ijk,ijk,ijk', index_grid[u], index_grid[v], map_grid, optimize=True) / sum_grid_values - \
                self.centre_coos[u] * self.centre_coos[v]

        fvec = np.vectorize(f)
        self.cov_matrix = np.fromfunction(fvec, (3, 3), dtype=int)
        eval, evec = LA.eig(self.cov_matrix)
        logger.debug("Eigen-info prior to sorting and right-handed system adjustment.")
        logger.debug(f'Eigenvalues: {eval}')
        logger.debug(f'Eigenvectors: \n{evec}\n')

        # Make all eigenvalues positive.
        eval = abs(eval)

        # Sort indices for eigenvalues in descending order of eigenvalues
        idx = np.argsort(-eval)
        self.eigenvalues = eval[idx]
        self.eigenvectors = evec[:, idx]

        # To ensure that the eigenvectors span a right handed system, the third eigenvector should be the cross product of the other two
        vec = np.cross(self.eigenvectors[:, 0], self.eigenvectors[:, 1])
        self.eigenvectors[:, 2] = vec / LA.norm(vec)

        logger.debug("Eigen-info after sorting and right-handed system adjustment.")
        logger.debug(f'Eigenvalues: {self.eigenvalues}')
        logger.debug(f'Eigenvectors: \n{self.eigenvectors}\n')

    def __str__(self):
        str = f"Map covariance parameters:\n" \
            + f"Covariance matrix:\n{self.cov_matrix}\n" \
            + f"Centre coordinates: \n{self.centre_coos}\n" \
            + f"Eigenvectors: \n{self.eigenvectors}\n" \
            + f"Eigenvalues: \n{self.eigenvalues}\n"

        return str

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Determine the covariance matrix of the map value distribution, and the corresponding eigenvectors (principal axes) and eigenvalues.')
    parser.add_argument('infile', metavar='FILE', type=str, help="Input map.")
    args = parser.parse_args()

    with mrcfile.open(args.infile) as mrc:
        map_cov_info = MapCovariance(mrc.data)
        print(map_cov_info)