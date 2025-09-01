import os
import hashlib
import tarfile
from urllib.request import urlretrieve

from ..lowlevel import debug


def show_progress(block_num, block_size, total_size):
    print(f'- {round(block_num * block_size / total_size * 100, 2)}% downloaded', end="\r")


def main(args):
    global debugprint0, debugprint1, debugprint2
    global timestamp0, timestamp1, timestamp2
    debugprint0, debugprint1, debugprint2 = debug.debugprint
    timestamp0, timestamp1, timestamp2 = debug.timestamp
    starttime = timestamp0(msg="\n# cleanifier download")

    if args.dir is not None and not os.path.isdir(args.dir):
        raise ValueError(f'Provided directory {args.dir} does not exist!')

    if args.version == 'exact':
        url = 'https://zenodo.org/records/15639519/files/cleanifier_exact.tar?download=1'
        filename = f'{args.dir}/cleanifier_exact.tar' if args.dir is not None else 'cleanifier_exact.tar'
        md5 = '03ff2d054a4f2360d3bb7ff9800c5f4a'
    elif args.version == 'probabilistic':
        url = 'https://zenodo.org/records/15639519/files/cleanifier_probabilistic.tar?download=1'
        filename = f'{args.dir}/cleanifier_probabilistic.tar' if args.dir is not None else 'cleanifier_probabilistic.tar'
        md5 = '47ccaa4e7935909586d66df9c0d9296e'
    else:
        raise ValueError(f"Only exact or probabilistic version supported, but {args.version} provided")

    urlretrieve(url, filename, show_progress)
    timestamp0(starttime, msg=f'- Finished download of {filename}')

    if args.checksum:
        timestamp0(starttime, msg='- Compute checksum.')
        with open(filename, "rb") as f:
            file_hash = hashlib.md5()
            while chunk := f.read(8192):
                file_hash.update(chunk)

        if file_hash.hexdigest() != md5:
            raise RuntimeError("Wrong checksum. Please retry download.")

        timestamp0(starttime, msg='- Checksum verified.')

    if tarfile.is_tarfile(filename):
        with tarfile.open(filename) as tar:
            directory = args.dir if args.dir is not None else '.'
            tar.extractall(directory)
        timestamp0(starttime, msg='- Tarball successfully extracted.')
    else:
        raise RuntimeError("Downloaded file not a tar file.")
