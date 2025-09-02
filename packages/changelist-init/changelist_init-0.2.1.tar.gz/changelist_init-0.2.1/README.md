# Changelist-Init
Manage your Git File and Commit Message Workflows with Changelists!

## Introduction
Changelist-Init is the package that gets your changelists ready to go!
- Sync changelists with **git**.
- Creates new changelists data file if necessary.

### About
Changelist-Init is a command-line tool (CLI) in an ecosystem of Changelist CLI tools.
It plays the role of adding file changes from **git** into the project changelist data file.

The related packages `sort` and `foci` serve other changelist management functions by reading, and writing to, the project changelist data file.

### Related Packages
The package [`changelist-sort`](https://github.com/DK96-OS/changelist-sort) is for organizing the files in your Changelists.
- Sorts files into Changelists by directory

The package [`changelist-foci`](https://github.com/DK96-OS/changelist-foci) (File Oriented Commit Information) prints a commit message template for your Changelists.
- Various File Name and Path formatting options

The package [`changelist-data`](https://github.com/DK96-OS/changelist-data) is a dependency of all Changelist packages.
- Provides read and write access to data files
- Contains common data classes, handles data serialization

## Package Details

### Changelist Init
The root package init module provides high level methods:
- `initialize_file_changes() -> list[FileChange]`: Get updated FileChange information from Git.
- `merge_file_changes() -> bool`: Merge updated FileChange information into Changelists.

### Input Package
Using the High-Level package method `validate_input`, converts program arguments into `InputData` object.
Parsing and Validation are handled by internal package modules.

#### Data Classes
**Argument Data**:
- changelists_file: The string path to the Changelists Data File.
- workspace_file: The string path to the Workspace File.
- include_untracked: Whether to include untracked files.

**Input Data**:
- storage: The ChangelistData Storage object.
- include_untracked: Whether untracked files are added to changelists. false by default.

#### Internal Modules
**Argument Parser**
**String Validation**

### Git Package
Use the `get_status_lists()` method to obtain updated file information from git.

#### Data Classes

**Git File Status**:
- `get_tracking_status()`

**Git Status Lists**: A Collection of Data processed from Git Status operation.
- `get_list(GitTrackingStatus) -> list[GitFileStatus]`
- `add_file_status(GitFileStatus)`

#### Enum Class

**Git Tracking Status**:
- UNTRACKED
- UNSTAGED
- STAGED
- PARTIAL_STAGE

#### Internal Modules

**Status Runner**:
- `run_git_status() -> str`: Runs a Git Status Porcelain V1 operation, returns the stdout.
- `run_untracked_status() -> str`: Runs a sequence of Git operations to include untracked files in the Git Status output.

**Status Reader**:
- `read_git_status_output(str) -> GitStatusLists`: Read Git Status Porcelain V1 stdout.
- `read_git_status_line(str) -> GitFileStatus | None`: Read a single line of Git Status Porcelain V1. Ignores Directory lines.

**Status Codes**:
- `get_status_code_change_map(str) -> Callable[]`: Construct a FileChange map function for a Git Status code.
