"""
util.py

Author: Ardan Patwardhan
Affiliation: EMBL-EBI, Wellcome Genome Campus, CB10 1SD, UK
Date: 31/07/2025
Description: 
    Utility functions used by various modules.
"""
import mrcfile

def save_map(outfile, map_grid, mrc):
    """
    Save grid as a mrc file copying key header values from an existing
    mrc file.

    :param outfile: Name of file to save map to.
    :param map_grid: Map grid to save.
    :param mrc: MRC file with header information to copy.
    :return: No return value.
    """
    mrc_out = mrcfile.new(outfile, overwrite=True, compression='gzip')
    mrc_out.set_data(map_grid)
    mrc_out.header.origin = mrc.header.origin
    mrc_out.header.nxstart = mrc.header.nxstart
    mrc_out.header.nystart = mrc.header.nystart
    mrc_out.header.nzstart = mrc.header.nzstart
    mrc_out.voxel_size = mrc.voxel_size
    if mrc.header.exttyp:
        mrc_out.set_extended_header(mrc.extended_header)
    mrc_out.close()
