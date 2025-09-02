"""
map_line_projections.py

Author: Ardan Patwardhan
Affiliation: EMBL-EBI, Wellcome Genome Campus, CB10 1SD, UK
Date: 04/08/2025
Description: 
    Create orthogonal line projections from a map.
"""

import argparse
import logging
import matplotlib.pyplot as plt
import mrcfile
import numpy as np
from scipy.optimize import curve_fit

logger = logging.getLogger(__name__)

class MapLineProjections:
    """
    Class to create orthogonal line projections from a map.
    """

    PERM_IDX = np.array([[0,1,2],
                 [1,2,0],
                 [2,0,1],], dtype=int)

    @staticmethod
    def fit_exp4_func(x, a, b, c, d):
        """
        Fitting function y = a * exp(-b * (x - c)^4) + d
        :param x: x value for calculation of fitting function.
        :param a: Scale factor.
        :param b: Scaling of exponential.
        :param c: Centre x of exponential.
        :param d: Baseline offset of exponential.
        :return: Function evaluated at x.
        """
        return a * np.exp(-b * ((x - c) ** 4)) + d

    def fit_exp4(self):
        """
        Fit fit_exp4_func to the 3 line projections.
        :return: Fitted profiles to the 3 line projections.
        """

        abounds = (self.min + 0.1 * self.range, self.min + 10 * self.range)
        bbounds = [ (1 / (20 * self.variance[idx]**2), 5 / self.variance[idx]**2) for idx in MapLineProjections.PERM_IDX[:,0] ]
        cbounds = [ (0.9 * self.cent_coords[idx], 1.1 * self.cent_coords[idx]) for idx in MapLineProjections.PERM_IDX[:,0] ]
        dbounds = (self.min, self.min + 0.01 * self.range)
        prof_fit = list(map(lambda idx: curve_fit(MapLineProjections.fit_exp4_func, self.coords[idx], self.map_prof[idx],
                            bounds=([abounds[0][idx], bbounds[idx][0],cbounds[idx][0], dbounds[0][idx]], [abounds[1][idx],bbounds[idx][1],cbounds[idx][1],dbounds[1][idx]])),
                            MapLineProjections.PERM_IDX[:,0]))
        #logger.debug(f"Fitting parameters:\n{prof_fit}")
        logger.debug(f"Fit parameter a: ({prof_fit[0][0][0]}, {prof_fit[1][0][0]}, {prof_fit[2][0][0]})")
        logger.debug(f"Fit parameter b: ({prof_fit[0][0][1]}, {prof_fit[1][0][1]}, {prof_fit[2][0][1]})")
        logger.debug(f"Fit parameter c: ({prof_fit[0][0][2]}, {prof_fit[1][0][2]}, {prof_fit[2][0][2]})")
        logger.debug(f"Fit parameter d: ({prof_fit[0][0][3]}, {prof_fit[1][0][3]}, {prof_fit[2][0][3]})")

        return prof_fit

    def cumulative_profile_width(self, threshold = 0.005):
        """
        Determine the cumulative profile of each of the 3 line proj-
        ections. Then determine the indices where the profile crosses
        T and 1 -T where T is some threshold value. The width is then
        taken as the difference between these indices.

        :param threshold: Threshold value for width calculation.
        :return: Array of 3 widths.
        """

        y = -np.asarray(self.min).reshape(3,1)
        x = np.add(self.map_prof, y)
        cum_sum = np.cumsum(x, axis=1) / np.asarray(np.sum(x, axis=1)).reshape(3,1)

        # Find threshold value and threshold map
        idx1 = np.apply_along_axis(np.searchsorted, 1, cum_sum, threshold)
        idx2 = np.apply_along_axis(np.searchsorted, 1, cum_sum, 1 - threshold)

        return idx2 - idx1

    def plot(self, fig_title=None, fig_size=(18, 6)):
        """
        Plot line projections and corresponding fitted curves.

        :param fig_title: Figure title.
        :param fig_size: Figure size.
        :return: Tuple of figure and axes objects..
        """

        fig, ax = plt.subplots(1, 3, subplot_kw={}, figsize=fig_size)
        fig.subplots_adjust(left=0.05, right=0.95, bottom=0.05, top=0.85, wspace=0.15, hspace=0.05)
        if fig_title is not None:
            fig.suptitle(fig_title)

        for idx in MapLineProjections.PERM_IDX[:,0]:
            ax[idx].plot(self.map_prof[idx])
            ax[idx].plot(self.coords[idx], MapLineProjections.fit_exp4_func(self.coords[idx], *self.prof_fit[idx][0]))

            ax[idx].set(xlabel='Index', ylabel='Sum',
               title=f'1D profile in index: {idx}')
            ax[idx].grid()

        return fig, ax

    def __init__(self, map_grid):
        """
        Generate orthogonal line projections from a grid. Calculate
        various estimates for the width of the profile.

        :param map_grid: Input map for line projection calculations.
        """
        self.map_grid = map_grid

         # Coordinates along the 3 axis (they may not be equal in length)
        self.coords = tuple(map(lambda len: np.arange(len), map_grid.shape))

        # 1D profiles along each axis
        self.map_prof = tuple(map(lambda x: map_grid.sum(axis=(x[1],x[2])), MapLineProjections.PERM_IDX))

        # Basic stats
        self.min, self.max = np.min(self.map_prof, axis=1), np.max(self.map_prof, axis=1)
        self.range = self.max - self.min

        # Sum each profile
        self.sum = tuple(map(lambda x: np.sum(x), self.map_prof))

        # Centre coordinate of each profile
        self.cent_coords = tuple(map(lambda idx: np.dot(self.coords[idx], self.map_prof[idx]) / self.sum[idx], MapLineProjections.PERM_IDX[:,0]))

        # Variance and sigma of each profile
        self.variance = tuple(map(lambda idx: (np.dot(np.square(self.coords[idx]), self.map_prof[idx]) / self.sum[idx]) - self.cent_coords[idx]**2 , MapLineProjections.PERM_IDX[:,0]))
        self.sigma = np.sqrt(self.variance)
        self.two_sigma = 2 * self.sigma

        # Width from cumulative sum profile
        self.cum_prof_width = self.cumulative_profile_width()

        # Fit exp4 profile
        self.prof_fit = self.fit_exp4()

        # FWHM of profile
        log2 = np.log(2)
        self.prof_fit_fwhm = list(map(lambda idx: 2 * (log2 / self.prof_fit[idx][0][1]) ** 0.25, MapLineProjections.PERM_IDX[:, 0]))

        # Reciprocal e width of profile
        self.prof_fit_rec_e_width  = list(map(lambda idx: 2 * np.pow(self.prof_fit[idx][0][1], -0.25), MapLineProjections.PERM_IDX[:, 0]))



    def __str__(self):

        str = f"Profile parameters:\n" + \
            f"Min: {self.min}\n" + \
            f"Max: {self.max}\n" + \
            f"Range: {self.range}\n" + \
            f"Sum: {self.sum}\n" + \
            f"Centre: {self.cent_coords}\n" + \
            f"Variance: {self.variance}\n" + \
            f"Sigma: {self.sigma}\n" + \
            f"Two-sigma: {self.two_sigma}\n" + \
            f"Cumulative profile width: {self.cum_prof_width}\n" + \
            f"FWHM of fit: {self.prof_fit_fwhm}\n" + \
            f"Reciprocal e width of fit: {self.prof_fit_rec_e_width}"
        return str

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Determine line projections of a map and various related statistical measures, including the widths of the profiles.')
    parser.add_argument('infile', metavar='FILE', type=str, help="Input map.")
    args = parser.parse_args()

    with mrcfile.open(args.infile) as mrc:
        mlp = MapLineProjections(mrc.data)
        print(mlp)

