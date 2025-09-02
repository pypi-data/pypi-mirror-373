"""
map_threshold.py

Author: Ardan Patwardhan
Affiliation: EMBL-EBI, Wellcome Genome Campus, CB10 1SD, UK
Date: 05/08/2025
Description: 
    Threshold map.
"""

import argparse
import logging
import matplotlib.pyplot as plt
import mrcfile
import numpy as np
from .map_line_projections import MapLineProjections
from .util import save_map

logger = logging.getLogger(__name__)

class MapHistogram:
    """
    Class to represent the map histogram, the related cumulative
    distribution function and histogram of the background (noise) in a
    map.
    """

    def plot_map_histogram(self):
        """
        Plot the map histogram.

        :return: A tuple with the figure and axes objects.
        """
        fig, ax = plt.subplots()
        plt.yscale('log')
        ax.plot(self.bins[:-1], self.map_histogram)

        ax.set(xlabel='Intensity', ylabel='Normalised frequency',
               title='Histogram')
        return fig, ax

    def plot_map_cdf(self):
        """
        Plot the map cumulative distribution function.

        :return: A tuple with the figure and axes objects.
        """
        fig, ax = plt.subplots()
        # plt.yscale('log')
        ax.plot(self.bins[:-1], self.cum_dist_func)

        ax.set(xlabel='Intensity', ylabel='Cumulative frequency',
               title='Cumulative Distribution Function')
        return fig, ax

    def plot_bg_histogram(self):
        """
        Plots the background histogram.

        :return: A tuple with the figure and axes objects.
        """
        fig, ax = plt.subplots()
        plt.yscale('log')
        ax.plot(self.bg_histogram)

        ax.set(xlabel='Index', ylabel='Normalised frequency',
               title='Background histogram')
        return fig, ax

    def __init__(self, map_grid, histogram_bins = 5000, sigma_factor = 3.0):
        """
        Calculate the histogram of an input map and estimate the
        background level. It is assumed that the strongest peak in the
        histogram is due to background and is to the left of the signal.
        Hence, the part of the histogram to the left of the peak will be
        mainly due to background.

        :param map_grid: 3D input map.
        :param histogram_bins: Number of bins to use for the histogram.
        :param sigma_factor: The background level is set to the
            intensity of the peak + this factor multiplied by the
            standard deviation. of the peak.
        """

        self.sigma_factor = sigma_factor

        # Make histogram of map
        self.map_histogram, self.bins = np.histogram(map_grid.astype(np.float64), bins=histogram_bins, density=True)
        self.bin_width = self.bins[1] - self.bins[0]

        # Cumulative distribution function of map histogram
        self.cum_dist_func = np.cumsum(self.map_histogram) * self.bin_width

        # Find index of peak (mode) in histogram
        self.map_hist_max_idx = np.argmax(self.map_histogram)
        self.map_hist_max_val = self.bins[self.map_hist_max_idx] + 0.5 * self.bin_width

        # Check if max_idx = 0
        if self.map_hist_max_idx == 0:
            logger.debug("Warning: Histogram peak found at index = 0 which is abnormal.")

        # Check if max_idx is equal to the max histogram index
        if self.map_hist_max_idx == self.map_histogram.size - 1:
            print("Warning: Histogram peak found at right edge of histogram which would imply no information to the right of background peak.")
            print("Warning: Using index of the left edge of the histogram instead.")
            self.map_hist_max_idx = 0

        # Calculate map histogram stats
        mhist_sum = np.sum(self.map_histogram) * self.bin_width
        mhist_grid = self.bins[:-1] + 0.5 * self.bin_width

        self.map_mean = (np.dot(self.map_histogram, mhist_grid) / mhist_sum)
        self.map_var = (np.dot(self.map_histogram, mhist_grid**2) / mhist_sum) - self.map_mean ** 2
        self.map_sigma = np.sqrt(self.map_var)

        # Make new histogram taking the old one up to the peak and then mirroring it onto the right
        self.bg_histogram = np.concatenate((self.map_histogram[0:self.map_hist_max_idx + 1], self.map_histogram[self.map_hist_max_idx - 1::-1]))

        # Calculate stats of background histogram

        bhist_len = np.size(self.bg_histogram)
        bhist_grid = np.ogrid[0:bhist_len]

        self.bg_hist_sum = np.sum(self.bg_histogram)
        self.bg_frac = self.bg_hist_sum / np.sum(self.map_histogram)
        self.bg_mean_idx = np.dot(bhist_grid, self.bg_histogram) / self.bg_hist_sum
        self.bg_var_idx = (np.dot(bhist_grid**2, self.bg_histogram) / self.bg_hist_sum) - self.bg_mean_idx**2
        self.bg_mean = self.bins[0] + self.bg_mean_idx * self.bin_width
        self.bg_var = self.bg_var_idx * self.bin_width**2
        self.bg_sigma = np.sqrt(self.bg_var)
        self.bg_threshold = self.bg_mean + sigma_factor * self.bg_sigma

    def __str__(self):
        str = f"Histogram info:\n" + \
              f"Index of peak in map histogram is {self.map_hist_max_idx} with a map value {self.map_hist_max_val}" + \
              f"Mean value of map  is {self.map_mean}" + \
              f"Variance of map  is {self.map_var}" + \
              f"Standard deviation of map  is {self.map_sigma}" + \
              f"Sum of background histogram is {self.bg_hist_sum}\n" + \
              f"Background / (Signal + Background) is {self.bg_frac}\n" + \
              f"Signal fraction is {1 - self.bg_frac}\n" + \
              f"Mean index of background histogram is {self.bg_mean_idx}\n" + \
              f"Variance (in index scale) of background histogram is {self.bg_var_idx}\n" + \
              f"Mean value of background in map value scale is {self.bg_mean}\n" + \
              f"Variance of background in map value scale is {self.bg_var}\n" + \
              f"Standard deviation of background is {np.sqrt(self.bg_var)}\n" + \
              f"Threshold of background histogram is {self.bg_threshold}\n"
        return str

def threshold_map(map_grid):
    """
    Determine a threshold level for the map which is suitable for
    visualisation. A two-step procedure is used. First the background
    sigma in the map is estimated and a threshold is calculated based
    on this. The map is thresholded and then orthogonal line projection
    profiles are calculated. A second threshold is calculated based on
    the width of these profiles. The threshold ultimately selected is
    higher of the two values.
    Note: This algorithm exploits the characteristics of cryoEM maps
        and may not work on synthetic maps.

    :param map_grid: Input map.
    :return: A tuple with the thresholded map, the threshold level,
        the histogram object and the line profile object.
    """

    # Calculate the histogram and estimate the background level
    sigma_factor = 3
    hist = MapHistogram(map_grid, sigma_factor=sigma_factor)
    logger.debug(hist)

    # Set values below background_threshold to 0 in data
    map_grid1 = np.where(map_grid >= hist.bg_threshold, map_grid, 0)

    # 1D profiles along each axis
    prof = MapLineProjections(map_grid1)
    logger.debug(prof)

    # Fraction of box size
    box_fraction = 0.63 * np.prod(np.asarray(prof.two_sigma)) / np.prod(np.asarray(map_grid1.shape))
    # box_fraction = np.prod(np.asarray(eq_length)) / np.prod(np.asarray(map_grid.shape))
    logger.debug(f"Fraction of box taken up by structure: {box_fraction}")

    # Find threshold value and check if it is greater than the background threshold
    idx = np.searchsorted(hist.cum_dist_func, 1 - box_fraction)
    threshold = hist.bins[idx] + 0.5 * hist.bin_width
    threshold = threshold if threshold > hist.bg_threshold else hist.bg_threshold
    logger.debug(f"Threshold: {threshold}")

    # Threshold map
    map_grid1 = np.where(map_grid1 >= threshold, map_grid1, 0)

    return map_grid1, threshold, hist, prof

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Threshold map.')
    parser.add_argument('infile', metavar='FILE', type=str, help="Input map.")
    parser.add_argument('outfile', metavar='FILE', type=str, help="Thresholded map.")
    parser.add_argument('-p', '--plot', action='store_true', help="Plot histogram and line profiles.")
    args = parser.parse_args()

    with mrcfile.open(args.infile) as mrc:
        map_grid1, threshold, hist, prof = threshold_map(mrc.data)
        print(hist)
        print(f"Map threshold is {threshold}")
        if args.plot:
            prof.plot()
            fig1, ax1 = hist.plot_map_histogram()
            fig2, ax2 = hist.plot_map_cdf()
            fig3, ax3 = hist.plot_bg_histogram()
            plt.show()
        save_map(args.outfile, map_grid1, mrc)