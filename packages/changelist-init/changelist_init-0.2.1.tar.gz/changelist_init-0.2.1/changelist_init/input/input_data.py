""" Valid Input Data Class.
"""
from dataclasses import dataclass

from changelist_data.storage import ChangelistDataStorage


@dataclass(frozen=True)
class InputData:
    """ A Data Class Containing Program Input.

**Fields:**
 - storage (ChangelistDataStorage): The Storage object used for Data IO.
 - include_untracked (bool): Whether to include untracked files.
    """
    storage: ChangelistDataStorage
    include_untracked: bool = False
