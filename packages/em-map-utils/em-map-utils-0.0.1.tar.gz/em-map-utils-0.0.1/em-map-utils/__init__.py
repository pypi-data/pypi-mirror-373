"""
__init__.py

Author: Ardan Patwardhan
Affiliation: EMBL-EBI, Wellcome Genome Campus, CB10 1SD, UK
Date: 28/07/2025
Description: 
    em-map-utils: Package for creating and manipulating cryoEM maps in
    the MRC/CCP4/EMDB map formats.

    This file contains initialisation for this package.
"""

__author__ = "Ardan Patwardhan"

# Setup logging
import logging
import sys

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s.%(msecs)d, %(funcName)s|%(levelname)s: %(message)s',
                    datefmt='%Y-%b-%d at %H:%M:%S',
                    stream=sys.stdout)
# Set matplotlib log level to WARNING. It is DEBUG by default.
logging.getLogger("matplotlib").setLevel(logging.WARNING)


