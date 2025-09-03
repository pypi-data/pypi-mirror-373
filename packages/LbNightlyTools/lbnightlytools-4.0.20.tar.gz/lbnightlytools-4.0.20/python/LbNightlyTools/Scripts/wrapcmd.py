###############################################################################
# (c) Copyright 2013-2023 CERN                                                #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""
Simple script to be used in CMake launcher rules.

A launcher rule defined as

   set_property(GLOBAL PROPERTY RULE_LAUNCH_COMPILE "lbn-wrapcmd <CMAKE_CURRENT_BINARY_DIR> <TARGET_NAME>")

produces log files like SubDir/1234-TargetName-abcd-build.log for each compile command.
"""

import os
import sys
from hashlib import md5
from pathlib import Path
from shlex import quote
from subprocess import PIPE, STDOUT, run
from time import time


def main():
    if len(sys.argv) < 4:
        exit(
            "error: wrong number of arguments.\n"
            f"Usage: {os.path.basename(sys.argv[0])} current_binary_dir target command [args ...]"
        )

    current_binary_dir = Path(sys.argv[1])
    target = sys.argv[2]

    cmd = sys.argv[3:]
    cmd_line = " ".join(quote(a) for a in cmd).encode()
    cmd_hash = md5(cmd_line).hexdigest()[:32]
    logfile = current_binary_dir / f"{int(time() * 1e9)}-{target}-{cmd_hash}-build.log"

    os.makedirs(current_binary_dir, exist_ok=True)
    with logfile.open("wb") as f:
        f.write(b"\033[0;32m(")
        f.write(bytes(current_binary_dir))
        f.write(b")$ ")
        f.write(cmd_line)
        f.write(b"\033[0m\n")

        # cat is used for merging, we do not need to capture the output
        result = run(cmd, stdout=PIPE, stderr=STDOUT) if cmd[0] != "cat" else run(cmd)
        if result.stdout:
            f.write(result.stdout)
            sys.stdout.buffer.write(result.stdout)
        if result.returncode:
            f.write(b"\033[0;31m[command exited with ")
            f.write(str(result.returncode).encode())
            f.write(b"]\033[0m\n")
        sys.exit(result.returncode)
