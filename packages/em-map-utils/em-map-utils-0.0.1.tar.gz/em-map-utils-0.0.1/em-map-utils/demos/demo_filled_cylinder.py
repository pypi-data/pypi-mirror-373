"""
demo_filled_cylinder.py

Author: Ardan Patwardhan
Affiliation: EMBL-EBI, Wellcome Genome Campus, CB10 1SD, UK
Date: 30/07/2025
Description: 
    Plot orthogonal surface views of a filled sphere.
"""

import argparse
import matplotlib.pyplot as plt
from ..filled_cylinder import filled_cylinder
from .ortho_surface_views import ortho_surface_views

def plot_filled_cylinder(diameter, length, box_size, cent_coos, alignment_axis, out_file):
    """
    Plot orthogonal projections of a filled cylinder.

    :param diameter: Diameter of the filled cylinder.
    :param length: Length of the filled cylinder.
    :param box_size: Size of box representing 3D volume.
    :param cent_coos: Centre coordinates of the filled cylinder.
    :param alignment_axis: Alignment axis of the filled cylinder.
    :param out_file: Optional output file name to save png figure.
    :return: No return value.
    """
    cylinder = filled_cylinder(diameter=diameter,
                               length=length,
                               box_size=box_size,
                               cent_coos=cent_coos,
                               alignment_axis= alignment_axis)
    fig, ax = ortho_surface_views(cylinder, fig_title="Filled cylinder")
    if out_file:
        fig.savefig(out_file)
    plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot orthogonal surface views of a filled cylinder. Note: Coordinate system is (i,j,k) going from the slowest to fastest varying axis.')
    parser.add_argument('-o', '--outfile', metavar='FILE', type=str, help='Optional file to save the figure to.')
    parser.add_argument('-d', '--diameter', metavar='DIAM', type=float, default=40, help='Diameter of cylinder in voxels.')
    parser.add_argument('-l', '--length', metavar='LEN', type=float, default=70, help='Length of cylinder in voxels.')
    parser.add_argument('-b', '--box_size', metavar='XXX', type=int, nargs=3, default=[100, 100, 100], help='Three lengths of the sides (i,j,k) of the box in voxels.')
    parser.add_argument('-c', '--cent_coos', metavar='YYY', type=float, nargs=3, help='Centre coordinates (i,j,k) of cylinder in voxels.')
    parser.add_argument('-a', '--alignment_axis', choices= ['i', 'j', 'k'], default='i', help="Long axis of cylinder ('i', 'j' or 'k').")
    args = parser.parse_args()
    plot_filled_cylinder(diameter=args.diameter,
                         length=args.length,
                         box_size=args.box_size,
                         cent_coos=args.cent_coos,
                         alignment_axis=args.alignment_axis,
                         out_file=args.outfile)