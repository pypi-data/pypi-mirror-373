from typing import Any, Optional, Dict, Tuple, Text, List
import os


class DirectoryUtil:
    @staticmethod
    def _filename_without_prefix(file:str) -> str:
        """Splits of a filenames prefix until after the first ``_``."""
        return "_".join(file.split("_")[1:])


    @staticmethod
    def get_filenames(path:str) -> List[str]:
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
                files = sorted(files, key=DirectoryUtil._filename_without_prefix)
    
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


    @staticmethod
    def get_filenames_sorted(path:str):
        items = os.listdir(path)
        sorted_items = sorted(items)

        return sorted_items
