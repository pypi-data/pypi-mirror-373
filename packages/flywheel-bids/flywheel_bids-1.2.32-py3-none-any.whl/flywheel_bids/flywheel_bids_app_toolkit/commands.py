"""Module containing methods related to manipulating the bids_app_command
configuration free-text or other methods that input a BIDS App command.
"""

import logging
import os
import re
import sys
from pathlib import Path
from typing import List

from flywheel_gear_toolkit.interfaces.command_line import (
    build_command_list,
    exec_command,
)

from .context import BIDSAppContext

log = logging.getLogger(__name__)


def clean_generated_bids_command(cmd: List[str]):
    """Helper method to deal with potential Flywheel oddities for the BIDS
    commandline.

    Args:
        cmd (List): BIDS app commandline input that has been parsed into a
            comma-separated list (e.g., ['qsiprep','bids_dir','output_dir','participant'])

    Returns:
        out_cmd (List): modified commandline input that has been checked for
            common formatting issues/errors
    """
    out_cmd = list()
    for ii, cc in enumerate(cmd):
        if cc.startswith("--verbose"):
            # The app takes a "-v/--verbose" boolean flag (either present or not),
            # while the config verbose argument would be "--verbose=v".
            # So replace "--verbose=<v|vv|vvv>' with '-<v|vv|vvv>':
            cmd[ii] = "-" + cc.split("=")[1]
        elif " " in cc:
            # When there are spaces in an element of the list, it means that the
            # argument is a space-separated list, so take out the "=" separating the
            # argument from the value. e.g.:
            #     "--foo=bar fam" -> "--foo bar fam"
            # this allows argparse "nargs" to work properly
            cmd[ii] = cc.replace("=", " ")
        if "---" in cc:
            # When submitting a command in bids_app_command, the use of "--" is common.
            # Ensure that there are only ever two dashes for a kwarg
            cmd[ii] = re.sub("----", "--", cmd[ii])
            cmd[ii] = re.sub("---", "--", cmd[ii])

        # Some of the apps are starting to look for paths, not strings. This tidbit will correct the first couple of args to use paths for the BIDS directory and output directory
        if os.path.sep in cc and "=" not in cc:
            cmd[ii] = Path(cc).as_posix()

        # add each space separated element separately so they don't get grouped by quotes later
        if " " in cmd[ii]:
            out_cmd.extend(cmd[ii].split(" "))
        else:
            out_cmd.append(cmd[ii])

    return out_cmd


def generate_bids_command(app_context: BIDSAppContext) -> List[str]:
    """Build the main BIDS app command line command to run.

    This method should be the same for FW and XNAT instances. It is also BIDS-App
    generic.

    Args:
       app_context (BIDSAppContext): Details about the gear setup and BIDS options

    Returns:
        cmd (list of str): command to execute
    """
    # Common to all BIDS Apps (https://github.com/BIDS-Apps), start with the command
    # itself and the 3 positional args: bids path, output dir, analysis-level
    # ("participant"/"group").
    # This should be done here in case there are nargs='*' arguments
    # (PV: Not sure if this is the case anymore. Their template seems to
    # suggest so, but not the general documentation.)
    cmd = [
        str(app_context.bids_app_binary),
        str(app_context.bids_dir),
        str(app_context.analysis_output_dir),
        str(app_context.analysis_level),
    ]

    cmd = build_command_list(cmd, app_context.bids_app_options)

    cmd = clean_generated_bids_command(cmd)

    log.info("command is: %s", str(cmd))
    return cmd


def run_bids_algo(app_context: BIDSAppContext, command: List[str]) -> int:
    """Run the algorithm.

    Args:
        app_context (BIDSAppContext): Details about the gear setup and BIDS options
        command (List): BIDS command that has been updated for Flywheel paths and
                        parsed to a comma-separated list

    Returns:
        run_error (int): any error encountered running the app. (0: no error)
    """
    if not Path(app_context.analysis_output_dir).exists():
        # Create output directory
        log.info("Creating output directory %s", app_context.analysis_output_dir)
        Path(app_context.analysis_output_dir).mkdir(parents=True, exist_ok=True)

    # This is what it is all about
    # Turn off logging b/c of log limits and redirect for offline logs
    # Potentially add "> log_file" to the command to hard force the output to log file.
    log_file = Path(app_context.output_dir) / Path(
        app_context.bids_app_binary + "_log.txt"
    )
    # GTK requires str not PosixPath for log_file
    # if log.getEffectiveLevel() == 10:
    # tee may mess up the nipype output entirely.
    #     command.extend(["|", "tee", str(log_file)])
    # else:
    command.extend([">>", str(log_file)])

    exec_command(
        command,
        dry_run=app_context.gear_dry_run,
        shell=True,
        cont_output=False,
    )
    return 0


def validate_kwargs(app_context: BIDSAppContext, alt_run_cmd: List = None):
    """Make sure that the user-defined command string contains kwargs that the BIDS
    algorithm will accept.

    Args:
        alt_run_cmd (List): If the BIDS algorithm is run from a different command than
                the BIDS app binary name (e.g., cpac) within the FW gear container, enter the command that will provide the usage (e.g., for C-PAC `python /code/run.py --help`)
    """
    if alt_run_cmd:
        cmd = alt_run_cmd
    else:
        cmd = [str(app_context.bids_app_binary), "--help"]
    help_file, _, _ = exec_command(
        cmd,
        shell=True,
        stdout_msg="Checking bids_app_command kwargs against usage",
    )
    invalid_args = []
    for kw in app_context.bids_app_options.keys():
        if kw not in help_file:
            invalid_args.append(kw)
    if invalid_args:
        log.info(
            f"Found {len(invalid_args)} invalid arguments: {', '.join(invalid_args)}"
        )
        sys.exit("Gear cannot run the algorithm with invalid arguments. Exiting.")
