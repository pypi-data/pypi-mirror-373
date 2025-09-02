"""
demo_map_covariance.py

Author: Ardan Patwardhan
Affiliation: EMBL-EBI, Wellcome Genome Campus, CB10 1SD, UK
Date: 04/08/2025
Description: 
    Demonstrate the use of estimating map principal axes.
    A cuboid is first rotated by a known angle. The principal axes of
    the rotated map are used to estimate the back rotation of the map
    which is then applied to the map. Orthogonal surface views of the
    initial cuboid and the back-rotated cuboid are plotted and can be
    compared. They should be the same unless something has gone wrong
    with either the map rotation or the principal axes determination.
"""
import argparse
import logging
import matplotlib.pyplot as plt
import mrcfile
from pathlib import Path
from scipy.spatial.transform import Rotation as R
from ..filled_cuboid import filled_cuboid
from ..map_covariance import MapCovariance as MC
from ..map_rotate import map_rotate
from .ortho_surface_views import ortho_surface_views

logger = logging.getLogger(__name__)

def plot_back_rotated_cuboid(in_file, lengths, box_size, rotation, out_file):
    """
    A cuboid (or an optionally specified input map) is first rotated
    by a known angle. The principal axes of the rotated map are used to
    estimate the back rotation of the map which is then applied to the
    map. Orthogonal surface views of the initial map and the
    back-rotated map are plotted and can be compared.

    :param in_file: Path to the optional input map or None.
    :param lengths: Lengths of the cuboid.
    :param box_size: Size of the 3D volume box.
    :param rotation: Euler angle of rotation in an intrinsic frame following Z-Y'-Z" convention.
    :param out_file: Optional file to save the figure to.
    :return: No return value.
    """
    mrc = None
    if in_file is None:
        map_grid = filled_cuboid(lengths=lengths, box_size=box_size)
    else:
        mrc = mrcfile.open(in_file)
        map_grid = mrc.data

    fig1, ax1 = ortho_surface_views(map_grid, fig_title="Initial map")
    if out_file:
        fig1.savefig(out_file + "-inp.png")

    # Note: In scipy the axis order is reversed (i,j,k) map to (x,y,z)
    rot = R.from_euler('XYX', rotation, degrees=True)

    rot_map, back_rot_map, back_rot = MC.map_rotate_forward_backward(map_grid, rot)

    fig2, ax2 = ortho_surface_views(back_rot_map, fig_title="Back-rotated map")

    if out_file:
        fig2.savefig(out_file + "-back.png")
    plt.show()

    if mrc is not None:
        mrc.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Plot orthogonal surface views of a cuboid (or optionally an input map), and a map which has had a known rotation and a corresponding back rotation based on the principal axes applied to it. Note: Coordinate system is (i,j,k) going from the slowest to fastest varying axis.')
    parser.add_argument('-i', '--infile', metavar='FILE', type=str,
                        help='Optional input file. If none specified, a cuboid is used.')
    parser.add_argument('-o', '--outfile', metavar='FILE', type=str, help='Optional file root (do not add .png) to save the figures to.')
    parser.add_argument('-l', '--lengths', metavar='ZZZ', type=float, nargs=3, default=[70, 40, 20],
                        help='Cuboid dimensions (i,j,k) in voxels.')
    parser.add_argument('-b', '--box_size', metavar='XXX', type=int, nargs=3, default=[100, 100, 100],
                        help='Three lengths of the sides (i,j,k) of the box in voxels.')
    parser.add_argument('-r', '--rotation', metavar='RRR', type=float, nargs=3, default=[20, 0,0], help="Relative Euler angle in degrees using Z-Y\'-Z\" order and a right handed convention.")
    args = parser.parse_args()

    plot_back_rotated_cuboid(args.infile, args.lengths, args.box_size, args.rotation, args.outfile)