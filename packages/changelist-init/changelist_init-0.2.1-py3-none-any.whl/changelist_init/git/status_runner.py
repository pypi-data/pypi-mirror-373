""" Runner for Git Status Operation
"""
import subprocess


def run_git_status() -> str:
    """ Run a Git Status Process and Return the Output.

    Returns:
    str - The output of the Git Status Operation.
    """
    result = subprocess.run(
        args=['git', '--no-optional-locks', 'status', '--porcelain', '--no-renames'],
        capture_output=True,
        text=True,
        universal_newlines=True,
        shell=False,
        timeout=5,
    )
    if (error := result.stderr) is not None and not len(error) < 1:
        exit(f"Git Status Runner Error: {error}")
    return result.stdout


def run_untracked_status() -> str:
    """ Configure git for obtaining untracked files, then reset.
        - Uses multiple git commands to achieve the desired result.
        - Runs a Git Add command, then a soft reset.
    """
    # Add All Untracked Paths without staging
    git_add_output = subprocess.run(
        args=['git', 'add', '-N', '.'],
        capture_output=True,
        text=True,
        universal_newlines=True,
        shell=False,
        timeout=3,
    )
    if (error := git_add_output.stderr) is not None and not len(error) < 1:
        exit(f"Git Add Error: {error}")
    #
    result = run_git_status()
    # Before returning result, reset git to keep staging area clean
    # Use a soft reset, instead of default (mixed)
    git_reset_output = subprocess.run(
        args=['git', 'reset', '-q', '--soft'],
        capture_output=True,
        text=True,
        universal_newlines=True,
        shell=False,
        timeout=3,
    )
    if (error := git_reset_output.stderr) is not None and not len(error) < 1:
        exit(f"Git Reset Error: {error}")
    return result
