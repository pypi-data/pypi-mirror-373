#!/usr/bin/env python
###############################################################################
# (c) Copyright 2018-2020 CERN                                                #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
import os
import sys
import time
from io import BytesIO
from urllib.error import HTTPError
from urllib.request import urlopen
from zipfile import ZipFile

from LbEnv import fixProjectCase


def guess_project_name():
    proj = os.path.basename(os.getcwd())
    if "_" in proj:
        proj = proj.split("_", 1)[0]
    if proj.endswith("Dev"):
        proj = proj[:-3]
    return fixProjectCase(proj)


def main():
    import argparse
    import textwrap

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="\n".join(
            textwrap.wrap(
                "Script to copy test result ref.new files into local "
                "test directories to avoid re-running the tests locally",
                width=80,
            )
        ),
        epilog=textwrap.dedent(
            """\
            Note: the order of options is fixed

            Standard usage:
              check your local cmtconfig
              setup local project structure for the correct project
              get the packages you want to update
              go to the PROJECT_version top directory
              call this script
              go through and replace the references you want to update"""
        ),
    )

    parser.add_argument("slot", help="name of the slot")
    parser.add_argument(
        "build_id",
        nargs="?",
        default=time.strftime("%a"),
        help="build id for the slot (numeric or day name) " "[default: latest build]",
    )
    parser.add_argument(
        "application",
        nargs="?",
        help="application name [default: deduced from current directory]",
    )
    parser.add_argument(
        "destination",
        nargs="?",
        help="where to put the references, if not specified local references "
        "will be updated, but new directories will not be added "
        "[default: current directory]",
    )

    parser.add_argument(
        "-c",
        "--platform",
        default=os.environ.get("BINARY_TAG") or os.environ.get("CMTCONFIG"),
        help="platform to use [default: from $BINARY_TAG or $CMTCONFIG]",
    )

    args = parser.parse_args()

    # if set to True, do not extract files if the directory is missing
    ignore_missing_dirs = True

    if args.application:
        args.application = fixProjectCase(args.application)
    else:
        args.application = guess_project_name()

    if not args.destination:
        args.destination = os.curdir
    else:
        ignore_missing_dirs = False

    if not args.platform:
        parser.error(
            "missing option --platform and cannot be deduced from "
            "the environment (BINARY_TAG or CMTCONFIG)"
        )

    print(
        f"looking for slot: {args.slot}, build_id: {args.build_id}, app: {args.application}, platform: {args.platform}"
    )

    arch_url = (
        "https://s3.cern.ch/lhcb-nightlies-artifacts/"
        "{flavour}/{args.slot}/{args.build_id}/tests/{args.platform}/newrefs/{args.application}.zip"
    ).format(args=args, flavour="nightly")

    try:
        print("Getting data from:", arch_url)
        arch_data = urlopen(arch_url).read()
    except HTTPError:
        # treat HTTP errors as "no data available"
        print("cannot find data for the requested combination")
        exit(1)

    arch = ZipFile(BytesIO(arch_data))

    print("Extracting", "specific" if ignore_missing_dirs else "all", "refs...")

    def should_extract(filename):
        """
        Tell if a filename should be extracted.
        """
        return not ignore_missing_dirs or (  # True means extract everything
            not filename.endswith("/")  # ignore directories
            and os.path.isdir(os.path.dirname(filename))
        )

    for info in arch.infolist():
        if should_extract(info.filename):
            if args.destination == os.curdir:
                print(info.filename)
            else:
                print(
                    info.filename, "->", os.path.join(args.destination, info.filename)
                )

            arch.extract(info, path=args.destination)


if __name__ == "__main__":
    main()
