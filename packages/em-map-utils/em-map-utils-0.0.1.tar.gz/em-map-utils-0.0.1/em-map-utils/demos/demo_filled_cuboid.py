"""
demo_filled_cuboid.py

Author: Ardan Patwardhan
Affiliation: EMBL-EBI, Wellcome Genome Campus, CB10 1SD, UK
Date: 30/07/2025
Description: 
    Plot orthogonal surface views of a filled cuboid.
"""

import argparse
import matplotlib.pyplot as plt
from ..filled_cuboid import filled_cuboid
from .ortho_surface_views import ortho_surface_views

def plot_filled_cuboid(lengths, box_size, cent_coos, out_file):
    """
    Plot orthogonal projections of a filled cuboid.

    :param lengths: 3 lengths of the sides of the cuboid.
    :param box_size: 3 lengths of the box sides.
    :param cent_coos: Centre coordinates of the cuboid.
    :param out_file: Optional file to save the figure to.
    :return: No return value.
    """

    cuboid = filled_cuboid(lengths=lengths, box_size=box_size, cent_coos=cent_coos)
    fig, ax = ortho_surface_views(cuboid, fig_title="Filled cuboid")
    if out_file:
        fig.savefig(out_file)
    plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Plot orthogonal surface views of a 3D volume containing a filled cuboid. Note: Coordinate system is (i,j,k) going from the slowest to fastest varying axis.')
    parser.add_argument('-o', '--outfile', metavar='FILE', type=str, help='Optional file to save the figure to.')
    parser.add_argument('-l', '--lengths', metavar='ZZZ', type=float, nargs=3, default=[70, 40, 20],
                        help='Cuboid dimensions (i,j,k) in voxels.')
    parser.add_argument('-b', '--box_size', metavar='XXX', type=int, nargs=3, default=[100, 100, 100],
                        help='Three lengths of the sides (i,j,k) of the box in voxels.')
    parser.add_argument('-c', '--cent_coos', metavar='YYY', type=float, nargs=3,
                        help='Centre coordinates (i,j,k) of cuboid in voxels.')
    args = parser.parse_args()
    plot_filled_cuboid(lengths=args.lengths,
                       box_size=args.box_size,
                       cent_coos=args.cent_coos,
                       out_file=args.outfile)