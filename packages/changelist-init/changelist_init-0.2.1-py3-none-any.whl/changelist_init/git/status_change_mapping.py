""" Maps Git Status data into FileChange data.
"""
from itertools import groupby
from typing import Callable, Iterable, Generator

from changelist_data import file_change
from changelist_data.file_change import FileChange

from changelist_init.git.git_file_status import GitFileStatus


def map_file_status_to_changes(
    git_files: Iterable[GitFileStatus],
) -> Generator[FileChange, None, None]:
    """ Categorize by Status Code, and Map to FileChange data objects.

    Parameters:
    - git_files (Iterable[GitFileStatus]): An iterable or Generator providing GitFileStatus objects.

    Returns:
    FileChange - Yield by Generator.
    """
    for code, group in groupby(git_files, lambda w: w.code):
        mapping_function = get_status_code_change_map(code)
        for file_status in group:
            yield mapping_function(
                map_status_path_to_change(file_status.file_path)
            )


def get_status_code_change_map(
    code: str,
) -> Callable[[str, ], FileChange]:
    """ Get a FileChange mapping callable for a specific code.

    Parameters:
    - code (str): The status code, determining what kind of FileChange (create, modify, delete)

    Returns:
    Callable[str, FileChange] - A function that maps a FileChange path into the FileChange object.
    """
    if code in ('M ', ' M', 'MM'):
        return file_change.update_fc
    if code in ('A ', ' A', 'AM', 'MA'):
        return file_change.create_fc
    if code in ('D ', ' D', 'MD', 'DM'):
        return file_change.delete_fc
    if '?' in code or '!' in code:
        return file_change.create_fc
    exit(f"Unknown Code: {code}")


def map_status_path_to_change(
    status_path: str,
) -> str:
    """ Convert Status File path to FileChange path.
        Adds a leading slash character.
    """
    return '/' + status_path if not status_path.startswith('/') else status_path