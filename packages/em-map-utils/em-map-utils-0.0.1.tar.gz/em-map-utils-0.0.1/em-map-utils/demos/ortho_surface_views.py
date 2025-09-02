"""
ortho_surface_views.py

Author: Ardan Patwardhan
Affiliation: EMBL-EBI, Wellcome Genome Campus, CB10 1SD, UK
Date: 30/07/2025
Description: 
    Plot orthogonal surface views in the i, j and k directions of a
    3D numpy grid.
"""
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


def ortho_surface_views(map_grid, fig_title=None, color_map="YlOrRd", fig_size=(18, 6)):
    """
    Plot orthogonal surface views in the i, j and k directions of a
    3D numpy grid.


    :param map_grid: 3D numpy grid.
    :param fig_title: Title for the overall figure. Default is None.
    :param color_map: Color map of the figure. Default is "YlOrRd".
    :param fig_size: Size of the figure. Default is (7, 21)
    :return: figure object and subplot objects as tuple (fig, ax).
    """
    map_bounds = (np.min(map_grid), np.max(map_grid))
    thresh = map_bounds[0] + 0.5 * (map_bounds[1] - map_bounds[0])

    fig, ax = plt.subplots(1, 3, subplot_kw={"projection": "3d", "proj_type": "ortho"}, figsize=fig_size)
    fig.subplots_adjust(left=0.01, right=0.99, bottom = 0.01, top=0.99, wspace=0.01, hspace=0.01)
    if fig_title is not None:
        fig.suptitle(fig_title)

    cmap = plt.colormaps[color_map]
    face_colors = cmap(map_grid)
    col_norm = mpl.colors.Normalize(vmin=map_bounds[0], vmax=map_bounds[1])

    for x in ax:
        x.set_aspect('equal')
        x.set_xlim(0, map_grid.shape[0])
        x.set_ylim(0, map_grid.shape[1])
        x.set_zlim(0, map_grid.shape[2])
        x.set(xlabel='i axis',
              ylabel='j axis',
              zlabel='k axis')
        x.voxels(filled=map_grid >= thresh, facecolors=face_colors, norm=col_norm)

    ax[0].view_init(elev=90, azim=-90, roll=0)
    ax[1].view_init(elev=0, azim=-90, roll=0)
    ax[2].view_init(elev=0, azim=0, roll=0)

    return fig, ax
