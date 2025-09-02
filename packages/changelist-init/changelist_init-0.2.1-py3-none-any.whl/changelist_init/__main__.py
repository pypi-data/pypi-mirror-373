#!/usr/bin/python
from sys import argv, path


def main(): # Have to import after appending parent dir to path
    import changelist_init
    input_data = changelist_init.input.validate_input(argv[1:])
    # Generate FileChange info from git, update ChangelistDataStorage object.
    if not changelist_init.init_storage(
        storage=input_data.storage,
        include_untracked=input_data.include_untracked,
    ):
        exit("Failed to Merge new FileChanges into Changelists.")
    # Write Changelist Data file
    if not input_data.storage.write_to_storage():
        exit("Failed to Write Changelist Data File!")


if __name__ == "__main__":
    from pathlib import Path
    # Get the directory of the current file (__file__ is the path to the script being executed)
    current_directory = Path(__file__).resolve().parent.parent
    # Add the directory to sys.path
    path.append(str(current_directory))
    main()