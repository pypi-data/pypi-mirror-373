from typing import Text, Any, Dict, Union, List, Type, Callable
import json
import logging
import os
import uuid
import pathlib
import shutil


def delete_directory(path:str) -> None:
    try:
        shutil.rmtree(path)
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))


def delete(filename:str) -> None:
    try:
        os.remove(filename)
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))
    except Exception as e:
        print("Error: %s" % e)


def create_directory(path:str) -> None:
    try:
        os.makedirs(path)
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))


def _filename_without_prefix(file: Text) -> Text:
    """Splits of a filenames prefix until after the first ``_``."""
    return "_".join(file.split("_")[1:])


def list_directory(path: Text) -> List[Text]:
    """Returns all files and folders excluding hidden files.

    If the path points to a file, returns the file. This is a recursive
    implementation returning files in any depth of the path."""

    if not isinstance(path, str):
        raise ValueError(
            "`resource_name` must be a string type. "
            "Got `{}` instead".format(type(path))
        )

    if os.path.isfile(path):
        return [path]
    elif os.path.isdir(path):
        results = []
        for base, dirs, files in os.walk(path, followlinks=True):
            # sort files for same order across runs
            files = sorted(files, key=_filename_without_prefix)
            # add not hidden files
            good_files = filter(lambda x: not x.startswith("."), files)

            results.extend(os.path.join(base, f) for f in good_files)
            # add not hidden directories
            good_directories = filter(lambda x: not x.startswith("."), dirs)

            results.extend(os.path.join(base, f) for f in good_directories)

        return results
    else:
        raise ValueError(
            "Could not locate the resource '{}'.".format(os.path.abspath(path))
        )


def list_files(path: Text) -> List[Text]:
    """Returns all files.

    If the path points to a file, returns the file. This is a recursive
    implementation returning files in any depth of the path."""

    if not isinstance(path, str):
        raise ValueError(
            "`resource_name` must be a string type. "
            "Got `{}` instead".format(type(path))
        )

    if os.path.isfile(path):
        return [path]
    elif os.path.isdir(path):
        results = []
        for base, dirs, files in os.walk(path, followlinks=True):
            # not listing files in cache
            if '__pycache__' in base:
                continue

            # sort files for same order across runs
            files = sorted(files, key=_filename_without_prefix)
            # filter out hidden files
            good_files = filter(lambda x: not x.startswith("."), files)

            # filter out files starting with '_'
            good_files = filter(lambda x: not x.startswith("_"), good_files)

            results.extend(os.path.join(base, f) for f in good_files)
        return results
    else:
        raise ValueError(
            "Could not locate the resource '{}'.".format(os.path.abspath(path))
        )


def get_filename(path:str) -> str:
    filename:str = os.path.basename(path)
    return filename


def get_filename_no_extension(path:str) -> str:
    filename:str = pathlib.Path(path).stem
    return filename


def get_file_extension(path:str) -> str:
    filename, file_extension = os.path.splitext(path)
    return file_extension


def get_uuid_filename(filename:str) -> str:
    uuid_filename:str = str(uuid.uuid4())
    ext:str = get_file_extension(filename)
    return uuid_filename + ext


def get_file_path(path:str) -> str:
    dir_path:str = os.path.dirname(path)
    return dir_path


def get_directory_name(path:str) -> str:
    dir_name = os.path.basename(os.path.dirname(path))
    return dir_name


def get_full_filename(path:str, filename:str) -> str:
    return os.path.join(path, '') + filename


def get_safe_path(path:str) -> str:
    return os.path.join(path, '')
