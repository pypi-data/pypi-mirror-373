""" The Git Status of a file.
"""
from dataclasses import dataclass

from changelist_init.git.git_tracking_status import GitTrackingStatus


@dataclass(frozen=True)
class GitFileStatus:
    """ The Status information of a single File.

    Fields:
    - code (str): The two character code describing the file status.
    - file_path (str): The String path of the file.
    """
    code: str
    file_path: str

    def get_tracking_status(self) -> GitTrackingStatus:
        """ Obtain the Tracking Status of this File.

        Returns:
        GitTrackingStatus - The Tracking Status of this File.
        """
        if len(self.code) != 2:
            exit("Status Code should be two char length.")
        match self.code:
            case '??':
                return GitTrackingStatus.UNTRACKED
        if self.code.startswith(' '):
            return GitTrackingStatus.UNSTAGED
        if self.code.endswith(' '):
            return GitTrackingStatus.STAGED
        # If both code points are non-empty, is partially_staged
        return GitTrackingStatus.PARTIAL_STAGE
