""" The Arguments Received from the Command Line Input.
- This DataClass is created after the argument syntax is validated.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class ArgumentData:
    """ The syntactically valid arguments received by the Program.

**Fields:**
 - changelists_file (str?): The string path to the Changelists Data File.
 - workspace_file (str?): The string path to the Workspace File.
 - include_untracked (bool): Whether to include untracked files.
 - generate_sort_xml (bool): Generate the config.xml file for the project..
    """
    changelists_file: str | None = None
    workspace_file: str | None = None
    include_untracked: bool = False
    generate_sort_xml: bool = False