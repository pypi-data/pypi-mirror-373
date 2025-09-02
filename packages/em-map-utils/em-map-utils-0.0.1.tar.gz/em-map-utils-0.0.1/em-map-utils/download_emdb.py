"""
download_emdb.py

Author: Ardan Patwardhan
Affiliation: EMBL-EBI, Wellcome Genome Campus, CB10 1SD, UK
Date: 26/08/2025
Description: 
    Functions for downloading EMDB maps and other data from EMDB sites.
"""
import argparse
import multiprocessing as mp
import re
import requests
from http import HTTPStatus
import logging
from pathlib import Path
from .farm_function import FarmFunction


logger = logging.getLogger(__name__)

# Pattern to match 4-6 digit EMDB codes with or without EMD- prefix in
# upper or lower case.
emdbid_pattern = re.compile(r"^(EMD-)?(\d{4,6})$", re.IGNORECASE)

# Download sites for EMDB structures
emdb_root = {'EBI': 'https://ftp.ebi.ac.uk/pub/databases/emdb/structures',
             'PDBJ': 'https://ftp.pdbj.org/pub/emdb/structures',
             'RCSB': 'https://files.rcsb.org/pub/emdb/structures'}

def read_emdb_ids_from(filename):
    """
    Read EMDB ids from file.

    Each line is expected to have one EMDB ID and no other characters.

    :param filename: Name of file to read.
    :return: List of EMDB IDs.
    """
    emdb_ids = []
    with open(filename, 'r') as file:
        for line in file:
            match = emdbid_pattern.match(line.strip())
            if match:
                emdb_ids.append("EMD-" + match.group(2))
            else:
                logger.warning(f"Ignoring line. Could not parse EMDB ID  from text: {line}")
    return emdb_ids

def get_emdb_map_name(emdb_id):
    """
    Get EMDB map name from EMDB ID.

    Maps are named as emd_XXX.map.gz, where XXX is 4 - 6 digits.

    :param emdb_id: EMDB ID string.
    :return: Map name.
    """
    if emdb_id.isnumeric():
        map_name = 'emd_' + emdb_id
    else:
        map_name = 'emd_' + emdb_id[4:]
    return map_name + '.map.gz'

def get_map_download_path(download_dir, emdb_id):
    """
    Create full path to where EMDB map will be downloaded.

    :param download_dir: Download directory.
    :param emdb_id: EMDB ID string.
    :return: Map download path.
    """
    return Path(download_dir) / get_emdb_map_name(emdb_id)

def get_emdb_map_url(emdb_id, loc='EBI'):
    """
    Get EMDB map URL from EMDB ID and EMDB location.

    :param emdb_id: EMDB ID string.
    :param loc: One of the 3 sites from the emdb_root dictionary.
    :return: EMDB map URL.
    """
    return f'{emdb_root[loc]}/{emdb_id.upper()}/map/{get_emdb_map_name(emdb_id)}'

def download_emdb_map(emdb_id, download_dir, loc='EBI', resume=True, chunk_size=2**16):
    """
    Download EMDB map from EMDB ID and EMDB location.

    :param emdb_id: EMDB ID of map to be downloaded.
    :param download_dir: Directory to download to.
    :param loc: EMDB location to download from.
    :param resume: If TRUE and the map has been partially downloaded,
        continue from where it left off.
    :param chunk_size: Chunk size of requests used during download.
    :return: True if the download was successful.
    """
    map_url = get_emdb_map_url(emdb_id, loc=loc)
    map_path = get_map_download_path(download_dir, emdb_id)
    logger.debug(f'Downloading {map_url} to {map_path}')
    if map_path.exists() and resume:
        start_pos = map_path.stat().st_size
        logger.debug(f'Resuming from {start_pos} bytes')
        file_mode = 'ab'
        req_headers = {'Range': f'bytes={start_pos}-'}
    else:
        start_pos = 0
        file_mode = 'wb'
        req_headers = {}

    response = requests.get(map_url, headers=req_headers, stream=True, verify=True, allow_redirects=True)
    response.raw.decode_content = True

    # If the full file has already been downloaded, the request returns a 416 error
    if resume == True and response.status_code == HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE:
        logger.debug(f'Map {map_path} has already been downloaded')
        return True

    # If something else did not work
    if response.status_code not in [HTTPStatus.OK, HTTPStatus.PARTIAL_CONTENT]:
        logger.error(f'Error downloading, status code: {response.status_code}')
        return False

    logger.debug(f'Response status code: {response.status_code}')

    with open(map_path, file_mode) as f:
        for chunk in response.iter_content(chunk_size=chunk_size):
            f.write(chunk)
        logger.debug(f'Finished downloading {map_path}')
        return True

    logger.error(f'Error downloading {map_path}')
    return False

def main():
    """
    Download EMDB map or a list of maps from a EMDB site.

    If a list of files is provided, then multiprocessing is used to
    download EMDB maps.
    :return:
    """
    mp.set_start_method("fork", force=True)
    mp.freeze_support()

    parser = argparse.ArgumentParser(
        description='Download EMDB map (-e option) or maps (-l option).')
    parser.add_argument('download_dir', metavar='DIR', type=str, help="Directory to download EMDB maps to.")
    parser.add_argument('-e', '--emdb_id', metavar='XXX', type=str, default="EMD-0001",
                        help='EMDB ID used to download EMDB map.')
    parser.add_argument('-l', '--emdb_list', metavar='XXX', type=str,
                        help='Text file with list of EMDB IDs to download. One EMDB ID per line.')
    parser.add_argument('-s', '--site', metavar='YYY', choices=['EBI', 'RCSB', 'PDBJ'], default='EBI',
                        help='wwPDB site to download data from. Note: Download speeds can vary considerably.')
    parser.add_argument('-r', '--resume', action='store_true',
                        help='Do not overwrite existing files. Instead try and resume the download(s).')
    parser.add_argument('-c', '--chunk_size', metavar='VAL', type=int, default=2 ** 16,
                        help='The map is downloaded in chunks of this size.')
    parser.add_argument('-w', '--num_workers', metavar='VAL', type=int, default=5,
                        help='Number of workers to use for download. Only relevant with -l option.')
    parser.add_argument('-t', '--max_tries', metavar='VAL', type=int, default=2,
                        help='Number of attempts to download a map. Only relevant with -l option.')
    parser.add_argument('-m', '--monitoring_interval', metavar='VAL', type=int, default=5,
                        help='Interval in seconds between each worker check. Only relevant with -l option.')
    parser.add_argument('-f', '--file_stem', metavar='FILE', type=str, default='emdb-download',
                        help='File stem name excluding suffix to use for output json and database. Will be prefixed with download_dir. Only relevant with -l option.')
    parser.add_argument('--retry', action='store_true',
                        help='Retry items that failed. Only works with the --resume flag. Only relevant with -l option.')
    args = parser.parse_args()

    if args.emdb_list is None:
        download_emdb_map(args.download_dir, args.emdb_id, loc=args.site, resume=args.resume,
                          chunk_size=args.chunk_size)
    else:
        if args.resume:
            id_list = []
        else:
            id_list = read_emdb_ids_from(args.emdb_list)
        file_root = Path(args.download_dir) / args.file_stem

        ff = FarmFunction(download_emdb_map, id_list, args=[args.download_dir],
                          kwargs={'loc': args.site, 'resume': args.resume, 'chunk_size': args.chunk_size},
                          num_workers=args.num_workers,
                          max_tries=args.max_tries,
                          monitoring_interval=args.monitoring_interval,
                          file_root=file_root,
                          resume=args.resume,
                          retry=args.retry)

if __name__ == '__main__':
    main()
