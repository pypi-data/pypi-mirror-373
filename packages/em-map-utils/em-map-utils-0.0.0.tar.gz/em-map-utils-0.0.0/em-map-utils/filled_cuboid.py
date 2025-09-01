"""
filled_cuboid.py

Author: Ardan Patwardhan
Affiliation: EMBL-EBI, Wellcome Genome Campus, CB10 1SD, UK
Date: 28/07/2025
Description: 
     Generate a 3D volume containing a filled cuboid.
"""

import argparse
import mrcfile
import numpy as np

def filled_cuboid(lengths = (80, 50, 20),
                  box_size = (100, 100, 100),
                  inside_value = 1.0,
                  outside_value = 0.0,
                  cent_coos = None,
                  dtype = np.float32):
    """
    Generate a cuboid of given lengths.

    Note: Coordinate system is (i,j,k) going from the slowest to fastest
        varying axis.

    :param lengths: Tuple/list/array of cuboid lengths aligned to box
        axes.
    :param box_size: Tuple/list/array of box dimensions.
    :param inside_value: Voxel value inside and on cuboid.
    :param outside_value: Voxel value outside cuboid.
    :param cent_coos: Centre coordinates of cuboid as tuple/list or
        array. If None, the centre of the box is used.
    :param dtype: Data type of 3D volume. Note: it cannot be
        float64 for the current MRC format.
    :return: 3D numpy grid with a cuboid.
    """
    cent_coos = np.asarray(cent_coos or (np.asarray(box_size) - 1) / 2)
    half_lengths = np.asarray(lengths)/2.0

    def f(i, j, k):
        v = np.array([i,j,k])
        return inside_value if np.all(abs(v - cent_coos) < half_lengths) else outside_value

    fvec = np.vectorize(f)
    return np.fromfunction(fvec, box_size).astype(dtype)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a 3D volume containing a filled cuboid. Note: Coordinate system is (i,j,k) going from the slowest to fastest varying axis.')
    parser.add_argument('outfile', metavar='FILE', type=str, help='Output filename.')
    parser.add_argument('-l', '--lengths', metavar='ZZZ', type=float, nargs=3, default=[70, 40, 20], help='Cuboid dimensions (i,j,k) in voxels.')
    parser.add_argument('-b', '--box_size', metavar='XXX', type=int, nargs=3, default=[100, 100, 100], help='Three lengths of the sides (i,j,k) of the box in voxels.')
    parser.add_argument('-c', '--cent_coos', metavar='YYY', type=float, nargs=3, help='Centre coordinates (i,j,k) of cuboid in voxels.')
    parser.add_argument('-i', '--inside_value', metavar='VAL', type=float, default=1.0, help='Map value inside and on the cuboid.')
    parser.add_argument('-o', '--outside_value', metavar='VAL', type=float, default=0.0, help='Map value outside the cuboid.')
    parser.add_argument('-v', '--voxel', metavar='ÅÅÅ', type=float, default=1.0,  help='Voxel size in Ångström.')
    args = parser.parse_args()
    cuboid = filled_cuboid(lengths=args.lengths,
                           box_size=args.box_size,
                           inside_value=args.inside_value,
                           outside_value=args.outside_value,
                           cent_coos=args.cent_coos)

    # Save map to file
    mrc_out = mrcfile.new(args.outfile, overwrite=True, compression='gzip')
    mrc_out.set_data(cuboid)
    mrc_out.voxel_size = args.voxel
    mrc_out.close()