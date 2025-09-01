"""
demo_farm_function.py

Author: Ardan Patwardhan
Affiliation: EMBL-EBI, Wellcome Genome Campus, CB10 1SD, UK
Date: 25/08/2025
Description: 
    Demo usage of farm function using a dummy function that can fail 50
    percent of the time.
"""
import argparse
import multiprocessing as mp
import random
import time
from ..farm_function import FarmFunction

def dummy(x, y, z):
    """
    Dummy function that fails 50% of the time randomly.
    :param x: Not used. Included for testing purposes.
    :param y: Not used. Included for testing purposes.
    :param z: Not used. Included for testing purposes.
    :return: Tuple (status, result_dict) where status is whether the
        function is successful or not, and result_dict is a dictionary
        containing the results of the function.
    """
    time.sleep(random.randint(1,10))
    return  random.random() < 0.5, { 'x': random.randint(1,10), 'y': 'This is a test', 'z': random.random() }

if __name__ == '__main__':
    mp.set_start_method("fork", force=True)
    mp.freeze_support()
    parser = argparse.ArgumentParser(
        description='Run multiple instances of function which fails randomly and generates random output.')
    parser.add_argument("file_root", metavar='FILE', type=str, help="File root including path for database and output file.")
    parser.add_argument('-n', '--num_values', metavar='XXX', type=int, default=50,
                        help='Number of function evaluations.')
    parser.add_argument('-w', '--num_workers', metavar='YYY', type=int, default=14,
                        help='Number of worker processes.')
    parser.add_argument('-r', '--resume', action='store_true',
                        help='Continue from previous run.')
    parser.add_argument('-t', '--retry', action='store_true',
                        help='Retry items that failed. Only works with the --resume flag.')
    parser.add_argument('-i', '--ignore_new_values', action='store_true',
                        help='Just resume from old database and do not generate new values. Must be used with --resume flag.')
    args = parser.parse_args()
    print('Starting test')
    print(f'MP start method: {mp.get_start_method()}')

    val = [] if args.resume and args.ignore_new_values else list(range(args.num_values))
    ff = FarmFunction(dummy, val, [1], {'z': 0},
                      num_workers=args.num_workers,
                      file_root=args.file_root,
                      resume=args.resume,
                      retry=args.retry)