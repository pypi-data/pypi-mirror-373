"""
demo_map_rotate.py

Author: Ardan Patwardhan
Affiliation: EMBL-EBI, Wellcome Genome Campus, CB10 1SD, UK
Date: 31/07/2025
Description: 
    Rotate a simple map and show the orthogonal surface views.
"""

import argparse
import matplotlib.pyplot as plt
import mrcfile
from scipy.spatial.transform import Rotation as R
from ..filled_cuboid import filled_cuboid
from ..map_rotate import map_rotate
from .ortho_surface_views import ortho_surface_views

def plot_rotated_map(in_file, lengths, box_size, rotation, translation, out_file):
    """
    Rotate a cuboid (or an optionally specified map) and show the
    orthogonal surface views.

    :param in_file: Optional input file - if none is provided a cuboid
        is used as the input.
    :param lengths: Lengths of the cuboid.
    :param box_size: Size of the 3D volume box.
    :param rotation: Euler angle of rotation in an intrinsic frame following Z-Y'-Z" convention.
    :param translation: An initial translation vector.
    :param out_file: Optional file to save the figure to.
    :return: No return value.
    """
    mrc = None
    if in_file is None:
        map_grid = filled_cuboid(lengths=lengths, box_size=box_size)
    else:
        mrc = mrcfile.open(in_file)
        map_grid = mrc.data

    # Note: In scipy the axis order is reversed (i,j,k) map to (x,y,z)
    rot = R.from_euler('XYX', rotation, degrees=True)

    rot_map = map_rotate(map_grid, rotation=rot, initial_translation=translation)
    fig, ax = ortho_surface_views(rot_map, fig_title="Rotated map")
    if out_file:
        fig.savefig(out_file)
    plt.show()

    if mrc is not None:
        mrc.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Plot orthogonal surface views of a rotated cuboid. Note: Coordinate system is (i,j,k) going from the slowest to fastest varying axis.')
    parser.add_argument('-i', '--infile', metavar='FILE', type=str,
                        help='Optional input file. If none specified, a cuboid is used.')
    parser.add_argument('-o', '--outfile', metavar='FILE', type=str, help='Optional file to save the figure to.')
    parser.add_argument('-l', '--lengths', metavar='ZZZ', type=float, nargs=3, default=[70, 40, 20],
                        help='Cuboid dimensions (i,j,k) in voxels.')
    parser.add_argument('-b', '--box_size', metavar='XXX', type=int, nargs=3, default=[100, 100, 100],
                        help='Three lengths of the sides (i,j,k) of the box in voxels.')
    parser.add_argument('-t', '--translation', metavar='TTT', type=float, nargs=3,
                        help='Optional initial translation prior to rotation.')
    parser.add_argument('-r', '--rotation', metavar='RRR', type=float, nargs=3, default=[20, 0,0], help="Relative Euler angle in degrees using Z-Y\'-Z\" order and a right handed convention.")
    args = parser.parse_args()
    plot_rotated_map(args.infile, args.lengths, args.box_size, args.rotation, args.translation, args.outfile)