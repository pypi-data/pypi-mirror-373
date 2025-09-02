""" Container for the Git Status Information.
    Files in Git Status are categorized into 3 groups.
    1. Staged
    2. Unstaged
    3. Untracked
    These three groups are stored in three lists in this data class.
"""
from dataclasses import dataclass, field
from typing import Generator

from changelist_init.git.git_file_status import GitFileStatus
from changelist_init.git.git_tracking_status import GitTrackingStatus


@dataclass(frozen=True)
class GitStatusLists:
    """ The Lists summarizing the current Git Status.
    """
    _lists: dict[GitTrackingStatus, list[GitFileStatus]] = field(default_factory=lambda: {})

    def get_list(
        self, tracking_status: GitTrackingStatus
    ) -> list[GitFileStatus] | None:
        """ Obtain a List of File Status objects with the given Tracking Status.
        """
        return self._lists.get(tracking_status)

    def add_file_status(
        self, file_status: GitFileStatus | None,
    ) -> bool:
        """ Add A File Status to the Lists.
        """
        status = file_status.get_tracking_status()
        if (initial_list := self.get_list(status)) is not None:
            initial_list.append(file_status)
            return True
        self._lists[status] = [file_status]
        return True

    def merge_tracked(self) -> Generator[GitFileStatus, None, None]:
        """ Combine the Tracked Lists.
        These are currently divided into 3 categories: Staged, Unstaged, and PartialStage
        """
        tracked_status = (GitTrackingStatus.STAGED, GitTrackingStatus.UNSTAGED, GitTrackingStatus.PARTIAL_STAGE)
        for e in tracked_status:
            if (tracked_list := self.get_list(e)) is not None:
                yield from tracked_list

    def merge_all(self) -> Generator[GitFileStatus, None, None]:
        """ Combine the Tracked Lists.
        These are currently divided into 3 categories: Staged, Unstaged, and PartialStage
        """
        for e in GitTrackingStatus:
            if (file_list := self.get_list(e)) is not None:
                for f in file_list:
                    yield f
