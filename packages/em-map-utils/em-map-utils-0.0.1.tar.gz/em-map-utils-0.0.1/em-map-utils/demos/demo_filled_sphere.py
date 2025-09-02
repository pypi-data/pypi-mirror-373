"""
demo_filled_sphere.py

Author: Ardan Patwardhan
Affiliation: EMBL-EBI, Wellcome Genome Campus, CB10 1SD, UK
Date: 30/07/2025
Description: 
    Plot orthogonal surface views of a filled sphere.
"""

import argparse
import matplotlib.pyplot as plt
from ..filled_sphere import filled_sphere
from .ortho_surface_views import ortho_surface_views

def plot_filled_sphere(diameter, box_size, cent_coos, out_file):
    """
    Plot orthogonal projections of a filled sphere.

    :param diameter: Diameter of the filled sphere.
    :param box_size: Size of box representing 3D volume.
    :param cent_coos: Centre coordinates of filled sphere.
    :param out_file: Optional output file name to save png figure.
    :return: No return value.
    """
    sphere = filled_sphere(diameter=diameter, box_size=box_size, cent_coos=cent_coos)
    fig, ax = ortho_surface_views(sphere, fig_title="Filled sphere")
    if out_file:
        fig.savefig(out_file)
    plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Plot orthogonal surface views of a 3D volume containing a filled sphere. Note: Coordinate system is (i,j,k) going from the slowest to fastest varying axis.')
    parser.add_argument('-o', '--outfile', metavar='FILE', type=str, help='Optional file to save the figure to.')
    parser.add_argument('-d', '--diameter', metavar='DIAM', type=float, default=50,
                        help='Diameter of the filled sphere in voxels.')
    parser.add_argument('-b', '--box_size', metavar='XXX', type=int, nargs=3, default=[100, 100, 100],
                        help='Three lengths of the sides (i,j,k) of the box in voxels.')
    parser.add_argument('-c', '--cent_coos', metavar='YYY', type=float, nargs=3,
                        help='Centre coordinates (i,j,k) of sphere in voxels.')
    args = parser.parse_args()
    plot_filled_sphere(diameter=args.diameter,
                       box_size=args.box_size,
                       cent_coos=args.cent_coos,
                       out_file=args.outfile)

