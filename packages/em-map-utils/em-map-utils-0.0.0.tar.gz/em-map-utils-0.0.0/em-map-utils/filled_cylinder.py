"""
filled_cylinder.py

Author: Ardan Patwardhan
Affiliation: EMBL-EBI, Wellcome Genome Campus, CB10 1SD, UK
Date: 28/07/2025
Description: 
    Generate a 3D volume containing a filled cylinder.
"""

import argparse
import mrcfile
import numpy as np

def filled_cylinder(diameter = 50,
                    length = 100,
                    box_size = (100, 100, 100),
                    inside_value = 1.0,
                    outside_value = 0.0,
                    cent_coos = None,
                    alignment_axis = "i",
                    dtype = np.float32):
    """
    Generate a 3D volume containing a filled cylinder.

    Note: Coordinate system is (i,j,k) going from the slowest to fastest
        varying axis.

    :param diameter: Diameter of cylinder in voxels.
    :param length: Length of cylinder in voxels.
    :param box_size: Lengths of the sides of the 3D volume along the
        (i,j,k) axes.
    :param inside_value: Map value inside and on the cylinder.
    :param outside_value: Map value outside the cylinder.
    :param cent_coos: Centre (i,j,k) coordinates of the cylinder.
    :param alignment_axis: Long axis ('i', 'j' or 'k') of cylinder.
    :param dtype: Data type of 3D volume. Note: it cannot be
        float64 for the current MRC format.
    :return: 3D numpy grid with filled cylinder.
    """
    cent_coos = np.asarray(cent_coos or (np.asarray(box_size) - 1) / 2)
    alignment_axis = alignment_axis if alignment_axis in ["i", "j", "k"] else "i"
    radius = diameter/2.0
    half_length = length/2.0
    aligned_cent = cent_coos if alignment_axis == "i" else (cent_coos[1], cent_coos[2], cent_coos[0]) if alignment_axis == "j" else (cent_coos[2], cent_coos[0], cent_coos[1])

    def f(i, j, k):
        (coos0, coos1, coos2) = (i, j, k) if alignment_axis == "i" else (j, k, i) if alignment_axis == "j" else (k, i, j)
        return inside_value if abs(coos0 - aligned_cent[0]) <= half_length and ((coos1 - aligned_cent[1])**2 + (coos2 - aligned_cent[2])**2) <= radius**2 else outside_value

    fvec = np.vectorize(f)
    return np.fromfunction(fvec, box_size).astype(dtype)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a 3D volume containing a filled cylinder. Note: Coordinate system is (i,j,k) going from the slowest to fastest varying axis.')
    parser.add_argument('outfile', metavar='FILE', type=str, help='Output filename.')
    parser.add_argument('-d', '--diameter', metavar='DIAM', type=float, default=40, help='Diameter of cylinder in voxels.')
    parser.add_argument('-l', '--length', metavar='LEN', type=float, default=70, help='Length of cylinder in voxels.')
    parser.add_argument('-b', '--box_size', metavar='XXX', type=int, nargs=3, default=[100, 100, 100], help='Three lengths of the sides (i,j,k) of the box in voxels.')
    parser.add_argument('-c', '--cent_coos', metavar='YYY', type=float, nargs=3, help='Centre coordinates (i,j,k) of cylinder in voxels.')
    parser.add_argument('-i', '--inside_value', metavar='VAL', type=float, default=1.0, help='Map value inside and on the cylinder.')
    parser.add_argument('-o', '--outside_value', metavar='VAL', type=float, default=0.0, help='Map value outside the cylinder.')
    parser.add_argument('-a', '--alignment_axis', choices= ['i', 'j', 'k'], default='i', help="Long axis of cylinder ('i', 'j' or 'k').")
    parser.add_argument('-v', '--voxel', metavar='ÅÅÅ', type=float, default=1.0,  help='Voxel size in Ångström.')
    args = parser.parse_args()
    cylinder = filled_cylinder(diameter=args.diameter,
                               length=args.length,
                               box_size=args.box_size,
                               inside_value=args.inside_value,
                               outside_value=args.outside_value,
                               cent_coos=args.cent_coos,
                               alignment_axis=args.alignment_axis)

    # Save map to file
    mrc_out = mrcfile.new(args.outfile, overwrite=True, compression='gzip')
    mrc_out.set_data(cylinder)
    mrc_out.voxel_size = args.voxel
    mrc_out.close()