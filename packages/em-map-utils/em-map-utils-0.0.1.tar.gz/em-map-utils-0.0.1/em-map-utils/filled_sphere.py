"""
filled_sphere.py

Author: Ardan Patwardhan
Affiliation: EMBL-EBI, Wellcome Genome Campus, CB10 1SD, UK
Date: 28/07/2025
Description: 
    Generate a 3D volume of filled sphere.
"""

import argparse
import mrcfile
import numpy as np

def filled_sphere(diameter = 50,
                  box_size = (100, 100, 100),
                  inside_value = 1.0,
                  outside_value = 0.0,
                  cent_coos = None,
                  dtype = np.float32):
    """
    Generate a 3D volume containing a filled sphere.

    Note: Coordinate system is (i,j,k) going from the slowest to fastest
        varying axis.

    :param diameter: Diameter of the filled sphere in voxels.
    :param box_size: Lengths of the sides of the 3D volume along the
        (i,j,k) axes.
    :param inside_value: Map value inside and on the filled sphere.
    :param outside_value: Map value outside the filled sphere.
    :param cent_coos: Centre (i,j,k) coordinates of the filled sphere.
        If none are specified, the centre of the box is used.
    :param dtype: Data type of 3D volume. Note: it cannot be
        float64 for the current MRC format.
    :return: 3D numpy grid with filled sphere.
    """
    cent_coos = np.asarray(cent_coos or (np.asarray(box_size) - 1) / 2)
    radius = diameter/2.0

    def f(i, j, k):
        return inside_value if np.sqrt((i-cent_coos[0])**2 + (j-cent_coos[1])**2 + (k-cent_coos[2])**2) <= radius else outside_value

    fvec = np.vectorize(f)
    return np.fromfunction(fvec, box_size).astype(dtype)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a 3D volume containing a filled sphere. Note: Coordinate system is (i,j,k) going from the slowest to fastest varying axis.')
    parser.add_argument('outfile', metavar='FILE', type=str, help='Output filename.')
    parser.add_argument('-d', '--diameter', metavar='DIAM', type=float, default=50, help='Diameter of the filled sphere in voxels.')
    parser.add_argument('-b', '--box_size', metavar='XXX', type=int, nargs=3, default=[100, 100, 100], help='Three lengths of the sides (i,j,k) of the box in voxels.')
    parser.add_argument('-c', '--cent_coos', metavar='YYY', type=float, nargs=3, help='Centre coordinates (i,j,k) of sphere in voxels.')
    parser.add_argument('-i', '--inside_value', metavar='VAL', type=float, default=1.0, help='Map value inside and on the sphere.')
    parser.add_argument('-o', '--outside_value', metavar='VAL', type=float, default=0.0, help='Map value outside the sphere.')
    parser.add_argument('-v', '--voxel', metavar='ÅÅÅ', type=float, default=1.0,  help='Voxel size in Ångström.')
    args = parser.parse_args()
    sphere = filled_sphere(diameter = args.diameter,
                           box_size = args.box_size,
                           inside_value = args.inside_value,
                           outside_value = args.outside_value,
                           cent_coos = args.cent_coos)

    # Save map to file
    mrc_out = mrcfile.new(args.outfile, overwrite=True, compression='gzip')
    mrc_out.set_data(sphere)
    mrc_out.voxel_size = args.voxel
    mrc_out.close()