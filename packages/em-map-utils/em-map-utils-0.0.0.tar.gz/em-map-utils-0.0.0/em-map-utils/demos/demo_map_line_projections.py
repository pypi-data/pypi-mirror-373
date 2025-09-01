"""
demo_map_line_projections.py

Author: Ardan Patwardhan
Affiliation: EMBL-EBI, Wellcome Genome Campus, CB10 1SD, UK
Date: 04/08/2025
Description: 
    Plot line projections of a cuboid.
"""

import argparse
import matplotlib.pyplot as plt
import mrcfile
from ..filled_cuboid import filled_cuboid
from ..map_line_projections import MapLineProjections as MLP


def plot_line_projections(in_file, out_file, lengths, box_size):
    """
    Plot line projections of an input file if provided otherwise of a
    cuboid.

    :param in_file: Optional input file.
    :param out_file: Optional output file to save plot.
    :param lengths: Lengths of the cuboid.
    :param box_size: Size of the box containing the cuboid.
    :return: No return value.
    """
    mrc = None
    if in_file is None:
        map_grid = filled_cuboid(lengths, box_size)
    else:
        mrc = mrcfile.open(in_file)
        map_grid = mrc.data

    mlp = MLP(map_grid)
    print(mlp)

    fig, ax = mlp.plot("Line Projections")
    if out_file is not None:
        fig.savefig(out_file)
    plt.show()

    if mrc is not None:
        mrc.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Plot line projections of a cuboid or a specified input MRC file (which takes precedence over the cuboid parameters if specified).')
    parser.add_argument('-i', '--infile', metavar='FILE', type=str,
                        help='Optional input file. If none specified, a cuboid is assumed')
    parser.add_argument('-o', '--outfile', metavar='FILE', type=str,
                        help='Optional file to save the figures to.')
    parser.add_argument('-l', '--lengths', metavar='ZZZ', type=float, nargs=3, default=[70, 40, 20],
                        help='Cuboid dimensions (i,j,k) in voxels.')
    parser.add_argument('-b', '--box_size', metavar='XXX', type=int, nargs=3, default=[100, 100, 100],
                        help='Three lengths of the sides (i,j,k) of the box in voxels.')
    args = parser.parse_args()
    plot_line_projections(args.infile, args.outfile,args.lengths, args.box_size)