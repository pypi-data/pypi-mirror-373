""" Git Management Package.
"""
from typing import Generator

from changelist_data.file_change import FileChange

from changelist_init.git import status_runner, status_reader, status_change_mapping
from changelist_init.git.git_status_lists import GitStatusLists


def get_status_lists(
    include_untracked: bool = False,
) -> GitStatusLists:
    """ Executes the Complete Git Status into File Change Operation.

**Parameters:**
 - include_untracked (bool): Whether to include untracked files in Git Status.

**Returns:**
 list[FileChange] - The List of FileChange information from Git Status.
    """
    return status_reader.read_git_status_output(
        status_runner.run_git_status() if not include_untracked else status_runner.run_untracked_status()
    )


def generate_file_changes(
    include_untracked: bool,
) -> Generator[FileChange, None, None]:
    """ Initialize FileChanges with a Generator.

**Parameters:**
 - include_untracked: Whether to include untracked files in the output.

**Returns:**
 Generator[FileChange] - Those precious File Changes.
    """
    status_lists = get_status_lists(include_untracked)
    yield from status_change_mapping.map_file_status_to_changes(
        status_lists.merge_all() if include_untracked else status_lists.merge_tracked()
    )