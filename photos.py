"""
This module extracts and does some simple cleanup of Google Photos takeout
archives.
"""

import argparse
import distutils.core
import fnmatch
import os
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


def _unzip_archives(takeout_dir):
    """Extracts all archives to the archive directory."""
    for archive in _list_takeout_archives(takeout_dir):
        print('unzipping: ', archive)
        with zipfile.ZipFile(archive, 'r') as zip_ref:
            zip_ref.extractall(takeout_dir)

# def _convert_heic_files(takeout_dir):
#     """Convert HEIC files to JPG in place and keep the original."""
#     for dirpath, _, filenames in os.walk(os.path.join(takeout_dir,
#                                                       *PHOTOS_SUBDIR)):
#         heic_files = [os.path.join(dirpath, name) for name in filenames if
#                       name.endswith('.HEIC')]

#         for heic_file in heic_files:
#             with Image(filename=heic_file) as original:
#                 with original.convert('jpeg') as converted:
#                     jpg_file = os.path.splitext(heic_file)[0] + '.jpg'
#                     print('Saved converted JPG: ', jpg_file)
#                     converted.save(filename=jpg_file)


def _delete_metadata_files(takeout_dir):
    """Deletes all metadata files in the Photos data."""
    for dirpath, _, filenames in os.walk(os.path.join(takeout_dir,
                                                      *PHOTOS_SUBDIR)):
        metadata_files = [os.path.join(dirpath, name) for name in filenames if
                          name.endswith('.json')]

        for metadata_file in metadata_files:
            os.remove(metadata_file)


def _clean_up(takeout_dir, delete_archives=False):
    """Cleans up extra files and the compressed archives."""
    if delete_archives:
        takeout_archives = _list_takeout_archives(takeout_dir)
        for archive in takeout_archives:
            print('deleting archive: ', archive)
            os.remove(archive)
    else:
        print('Not deleting archives.')


def organize_photos_takeout(takeout_dir, photos_dir):
    _unzip_archives(takeout_dir)

    # answer = input('Convert HEIC to JPG and keep original? y/n: ')
    # answer = distutils.util.strtobool(answer)
    # if answer:
    #     _convert_heic_files(takeout_dir)

    # Clean up.
    answer = input('Delete all takeout archives? y/n: ')
    answer = distutils.util.strtobool(answer)
    _clean_up(takeout_dir, photos_dir, answer)
