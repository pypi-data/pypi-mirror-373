"""
structure_size_and_shape.py

Author: Ardan Patwardhan
Affiliation: EMBL-EBI, Wellcome Genome Campus, CB10 1SD, UK
Date: 07/08/2025
Description: 
    Threshold and align map with a box by determining the principal axes
    of the structure and then aligning the principal axes to the box.
    Estimate the size of the molecule using the widths of the 3
    orthogonal line projections. Estimate the aspericity of the
    structure as a shape measure.
"""

import argparse
import csv
import logging
import matplotlib.pyplot as plt
import mrcfile
import numpy as np
from pathlib import Path
from scipy.special import elliprg
from .map_covariance import MapCovariance as MC
from .map_line_projections import MapLineProjections as MLP
from .map_threshold import  threshold_map

logger = logging.getLogger(__name__)

def asphericity_coefficient(a, b, c):
    """
    Calculate the asphericity coefficient using three orthogonal width
    measures for a structure.
    Tha asphericity coefficient is defined as:
    1 - [ (V/S) / (V0/S0) ]
    where:
    S0 and V0 are the surface area and volume of a sphere with the
    cube root diameter = (abc)^(1/3),
    V is the volume of an ellipsoid with the axes a,b,c,
    S is the surface area of the ellipsoid with axes a,b,c calculated
    using the Carlson symmetric elliptical integral.
    What this formula is based on is that the surface area to volume
    ratio is at a minimum for a sphere compared to any ellipsoid with an
    equivalent volume and the comparison between the ratios increases
    the more the ellipsoid deviated from a sphere.

    :param a: Width along first axis.
    :param b: Width along second axis.
    :param c: Width along third axis.
    :return: Asphericity coefficient.
    """
    rg = elliprg(1.0 / (a * a), 1.0 / (b * b), 1.0 / (c * c))
    rav = np.pow(a*b*c,1/3)
    return 1 - 1 / (rav * rg)

def structure_size_and_shape(entry_file, aligned_file=None, plot_profile=True, csv_file=None, csv_mode="a"):
    """
    Determine the size and shape of  a structure.

    :param entry_file: Name of input MRC file.
    :param aligned_file: Optional name of aligned output MRC file.
    :param plot_profile: Boolean for plotting line projections.
    :param csv_file: Optional name of CSV file to output results to.
    :param csv_mode: Whether to (a)ppend or (w) to CSV file.
    :return: Tuple with physical widths of structure along the principal
        axes, the cube root of these widths (which represents a sphere
        equivalent average), and the asphericity.
    """

    phys_width = 0.0
    cube_root_width = 0.0
    asph = 0.0

    with mrcfile.open(entry_file) as mrc:

        # Threshold map
        map_grid, threshold, hist, prof = threshold_map(mrc.data)

        # Align map's principal axes to those of the box
        aligned_map, rot, cov_info = MC.align_map_principal_axes(map_grid)

        # Some values may be < 0 due to interpolation artifacts -> zero them
        aligned_map = np.where(aligned_map >= threshold, aligned_map, 0)

        # Scaling to Angstrom along eigenvectors
        scale_vec = cov_info.phys_scale_eigenvectors(mrc)

        # Get 1D profile lengths
        prof = MLP(aligned_map)
        phys_width = prof.cum_prof_width * scale_vec
        cube_root_width = np.pow(np.prod(phys_width), 1 / 3)
        asph = asphericity_coefficient(prof.cum_prof_width[0], prof.cum_prof_width[1], prof.cum_prof_width[2])

        print(prof)
        # print(f"Scaled reciprocal e width: {prof.rec_e_width * scale_vec}")
        print(f"Scaled cumulative profile width: {phys_width}")
        print(f"Cube root width: {cube_root_width}")
        print(f"Asphericity coefficient: {asph}")

        # Save measurements to CSV file
        if csv_file:
            csv_mode = csv_mode if Path(csv_file).exists() and csv_mode in ("a","w") else "w"
            with open(csv_file,  csv_mode, newline='') as f:
                fieldnames = ['entry_file', 'width1', 'width2', 'width3', "cube_root_width", "asphericity"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                print(f"Writing {csv_mode}")
                if csv_mode == "w":
                    writer.writeheader()

                writer.writerow({fieldnames[0]: entry_file,
                                 fieldnames[1]: phys_width[0],
                                 fieldnames[2]: phys_width[1],
                                 fieldnames[3]: phys_width[2],
                                 fieldnames[4]: cube_root_width,
                                 fieldnames[5]: asph})
                f.close()


        # Plot 1D profiles
        if plot_profile:
            prof.plot()
            plt.show()

        # Save aligned file to file
        if aligned_file is not None:
            mrc_out = mrcfile.new(aligned_file, overwrite=True, compression='gzip')
            mrc_out.set_data(aligned_map)
            mrc_out.header.origin = mrc.header.origin
            mrc_out.header.nxstart = mrc.header.nxstart
            mrc_out.header.nystart = mrc.header.nystart
            mrc_out.header.nzstart = mrc.header.nzstart
            mrc_out.voxel_size = mrc.voxel_size
            if mrc.header.exttyp:
                mrc_out.set_extended_header(mrc.extended_header)
            mrc_out.close()

    return phys_width, cube_root_width, asph

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Determine the size and shape of structure.')
    parser.add_argument('infile', metavar='FILE', type=str, help="Input map.")
    parser.add_argument('-c', '--csv', metavar='FILE', type=str, help="Optional csv file to output measurements.")
    parser.add_argument('-a', '--align_file', metavar='FILE', type=str, help="Optional output of the aligned map.")
    parser.add_argument('-p', '--plot', action='store_true', help="Plot histogram and line profiles.")
    parser.add_argument("-m", "--mode", choices=['a','w'], default='a', help="CSV output mode.")
    args = parser.parse_args()

    structure_size_and_shape(entry_file = args.infile,
                             aligned_file = args.align_file,
                             plot_profile = args.plot,
                             csv_file = args.csv,
                             csv_mode = args.mode)
