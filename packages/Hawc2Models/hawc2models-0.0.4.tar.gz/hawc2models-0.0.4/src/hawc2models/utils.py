from pathlib import Path
import shutil
import os
import pooch

# A automatically deleted tmp folder would be more appropriate on most systems, but
# on Sophia it will be /tmp (i.e. the compute node ram disk, which is difficult to clean up afterwards)
download_cache_folder = Path.home() / 'tmp_hawc2models'


def download(url, known_hash=None, unzip=False):
    # Download a file and save it locally, returning the path to it.
    # Running this again will not cause a download. Pooch will check the hash
    # (checksum) of the downloaded file against the given value to make sure
    # it's the right file (not corrupted or outdated).

    processor = None
    if unzip:
        processor = pooch.Unzip()

    ret = pooch.retrieve(url=url,
                         path=download_cache_folder,
                         known_hash=known_hash,
                         processor=processor
                         )
    return ret


def delete_download_cache():
    if download_cache_folder.exists():
        shutil.rmtree(download_cache_folder)


def get_all_subclasses(cls):
    all_subclasses = []

    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(get_all_subclasses(subclass))

    return all_subclasses
