""" Reader for the Git Status Output String.
"""
from changelist_init.git.git_file_status import GitFileStatus
from changelist_init.git.git_status_lists import GitStatusLists


def read_git_status_output(
    status_string: str,
) -> GitStatusLists:
    """ Read the Git Status Output String.

    Fields:
    - status_string (str): The output of Git Status operation.

    Returns:
    GitStatusList - An object containing organized Git Status output.
    """
    if not isinstance(status_string, str):
        raise TypeError("Must be a String!")
    status_lists = GitStatusLists()
    for f in status_string.splitlines():
        if (file_status := read_git_status_line(f)) is not None:
            status_lists.add_file_status(file_status)
        else:
            print(f"Skipped: ${f}")
    return status_lists


def read_git_status_line(
    file_status_line: str
) -> GitFileStatus | None:
    """ Read a line of output from Git Status, into a GitFileStatus object.
    """
    if not isinstance(file_status_line, str):
        return None
    if len(file_status_line.strip()) < 3:
        return None
    if file_status_line.endswith('/'):
        return None
    return GitFileStatus(
        code=file_status_line[:2],
        file_path=file_status_line[3:],
    )
