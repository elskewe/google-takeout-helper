"""
This module extracts and does some simple cleanup of Google Photos takeout
archives.
"""

import distutils.core
import fnmatch
import os
import platform
import subprocess
import re
# from wand.image import Image
import zipfile


# Path to the Google Photos data directory in the extracted takeout data.
# When extracted the photos will be in: <takeout_dir>/Takeout/Google Photos/
PHOTOS_SUBDIR = ('Takeout', 'Google Photos')


def _list_takeout_archives(takeout_dir):
    """Lists the full path of all Google Takeout archives."""
    dir_files = []
    for filename in os.listdir(takeout_dir):
        if fnmatch.fnmatch(filename, 'takeout-*.zip'):
            dir_files.append(os.path.join(takeout_dir, filename))
    return dir_files


def _unzip_photos(takeout_dir, photos_dir, mode='photos'):
    """Extracts all archives to the destination directory.

    `mode` can be either 'photos' (default) or 'albums'. The former extracts the dated folders, the
    latter the rest, assuming they are all albums.
    """
    pattern = re.compile(r'^Takeout/Google Photos/\d{4}-[01]\d-[0-3]\d.*')

    for archive in _list_takeout_archives(takeout_dir):
        print('unzipping: ', archive)
        with zipfile.ZipFile(archive, 'r') as zip_ref:
            # print(zip_ref.namelist())
            for file in zip_ref.infolist():
                # determine whether the current file matches the mode
                if mode == 'photos':
                    is_valid = pattern.match(file.filename)
                elif mode == 'albums':
                    is_valid = not pattern.match(file.filename)
                else:
                    raise ValueError('mode must be either "photos" or "albums"')

                # extract file
                if is_valid:
                    # remove the Takeout/Google Photos part from the target directory
                    file.filename = os.path.relpath(
                        file.filename, 'Takeout/Google Photos')
                    zip_ref.extract(file, os.path.join(
                        photos_dir, mode.title()))


def _clean_up(takeout_dir, photos_dir, delete_archives=False):
    """Cleans up extra files and the compressed archives."""
    if delete_archives:
        takeout_archives = _list_takeout_archives(takeout_dir)
        for archive in takeout_archives:
            print('deleting archive: ', archive)
            os.remove(archive)
    else:
        print('Not deleting archives.')

    # Replace duplicate files with symlinks (Unix) or hardlinks (Windows)
    if platform.system() == 'Windows':
        print('Replacing duplicate files with hardlinks')
        rdfind_call = ('jdupes --link-hard --recurse "' + os.path.join(photos_dir, 'Photos') + '" "' + os.path.join(photos_dir, 'Albums') + '"')
    elif platform.system() == 'Linux':
        print('Replacing duplicate files with symlinks')
        rdfind_call = ('rdfind -checksum sha1 -makesymlinks true "'
                       + os.path.normpath(os.path.join(photos_dir, 'Photos'))
                       + '" "' + os.path.normpath(os.path.join(photos_dir, 'Albums')) + '"')
    else:
        print('OS not supported for duplicate file replacement')
        return
    subprocess.run(rdfind_call, check=True)


def organize_photos_takeout(takeout_dir, photos_dir):
    print('Unzipping photos')
    _unzip_photos(takeout_dir, photos_dir, 'photos')
    print('Unzipping albums')
    _unzip_photos(takeout_dir, photos_dir, 'albums')

    # Clean up.
    answer = input('Delete all takeout archives? y/n: ')
    answer = distutils.util.strtobool(answer)
    _clean_up(takeout_dir, photos_dir, answer)
