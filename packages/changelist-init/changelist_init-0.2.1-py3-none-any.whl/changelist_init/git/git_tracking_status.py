""" Git Tracking Status Enum.
"""
from enum import Enum, auto


class GitTrackingStatus(Enum):
    UNTRACKED = auto()
    UNSTAGED = auto()
    STAGED = auto()
    PARTIAL_STAGE = auto()
