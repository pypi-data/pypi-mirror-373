#
#  This file is part of Versionix software
#
#  Copyright (c) 2023 - Sequana Dev Team (https://sequana.readthedocs.io)
#
#  Distributed under the terms of the 3-clause BSD license.
#  The full license is in the LICENSE file, distributed with this software.
#
#  Website:       https://github.com/sequana/versionix
#  Contributors:  https://github.com/sequana/versionix/graphs/contributors
##############################################################################
import re
import shutil
import subprocess
import sys

import colorlog

from versionix import logger

logger = colorlog.getLogger(logger.name)


from .blacklist import blacklist
from .registry import metadata


class Versionix:
    def __init__(self, standalone):

        self.standalone = standalone

    def get_version(self):
        """possibilities"""
        # known options to retrieve version
        # could be empty (eg ktImportText) from kronatools

        if self.standalone in blacklist:
            logger.debug(f"{self.standalone} blacklisted")
            return "?.?.?"

        options = ["--version", "-v", "version", "-V", "-version", ""]
        for option in options:
            cmd = f"{self.standalone} {option}".strip()
            logger.debug(cmd)
            p = subprocess.run(cmd, capture_output=True, universal_newlines=True, shell=True)
            if p.returncode == 0:
                logger.debug(f"return code 0 for {option}")
                stdout = p.stdout.strip()
                stderr = p.stderr.strip()
                if stdout:
                    try:
                        return self.parse_version(stdout)
                    except Exception as err:  # pragma: no cover
                        pass
                elif stderr:  # sometimes the output is on stderr
                    try:
                        return self.parse_version(stderr)
                    except Exception as err:  # pragma: no cover
                        pass
            else:
                logger.debug(f"return code {p.returncode} for {option}")
                stderr = p.stderr.strip()
                if stderr:
                    try:
                        return self.parse_version(stderr)
                    except Exception as err:  # pragma no cover
                        pass

        logger.warning(f"None of {options} looks valid for {self.standalone}")  # pragma: no cover
        # instead of returning None, we return a string ?.?.? to mimic X.Y.Z pattern
        return "?.?.?"  # pragma: no cover

    def parse_version(self, string):

        # valid for
        #    "tools 2.5.2",
        #    "tools v1.1.0",
        #    "tools 3.0.0b1",
        #    "tools, version 0.48.0",
        #    "tools 2.8"
        #    "version: v0.9.21
        # but returns X.Y.Z (or X.Y)

        version = re.search(r"(v?[\d]+\.[\d]+(?:\.[\d]+)?[a-zA-Z0-9]*)", string).group(1)
        version = version.strip("v")
        return version


def get_version(standalone, verbose=True, R=False):
    """Main entry point that returns the version of an existing executable"""
    # we should use check_output in case the standalone opens a GUI (e.g. fastqc --WRONG pops up the GUI)

    # let us check that the standalone exists locally
    # versionix should handle special cases of standlones to be found in containers
    if (
        standalone.startswith("singularity") or standalone.startswith("apptainer") or standalone.startswith("docker")
    ):  # pragma: no cover
        pass
    elif shutil.which(standalone) is None:
        if verbose:
            logger.error(f"{standalone} command not found in your environment")
        sys.exit(1)

    # is it registered ?
    if standalone in metadata.keys():
        version = search_registered(standalone)
        return version

    # Try a generic search
    try:
        v = Versionix(standalone)
        return v.get_version()
    except Exception as err:  # pragma: no cover
        print(err)
        sys.exit(1)


def search_registered(standalone):

    # Otherwise, a search using registered names
    logger.debug(f"Using registered info for {standalone}")
    meta = metadata[standalone]

    # The command used to get the version output
    caller = meta.get("caller", standalone)

    # The options necessary to get the version output
    options = meta.get("options", "")

    # The parser of the version output. If not provided, set to null list to raise an error
    parsers = meta.get("parsers", [])

    if len(parsers) == 0:
        logger.error(f"parsers for {standalone} is incorrect. Must be a list of valid parsers. Check the registry.py")
        raise ValueError(f"parsers for {standalone} is incorrect. Must be a list of valid parsers")

    try:
        cmd = f"{caller} {options}"
        p = subprocess.run(cmd, capture_output=True, universal_newlines=True, shell=True)
        for parser in parsers:
            try:
                version = parser(p)
                return version
            except Exception as err:  # pragma: no cover
                pass
        raise Exception("No parsers could parse the version effectively")  # pragma: no cover
    except Exception as err:  # pragma: no cover
        print(err)
        sys.exit(1)
