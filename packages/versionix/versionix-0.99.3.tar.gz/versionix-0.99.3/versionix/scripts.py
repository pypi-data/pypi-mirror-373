###########################################################################
# Versionix is a project to manage reproducible containers                #
#                                                                         #
# Authors: see CONTRIBUTORS.rst                                           #
# Copyright © 2023 Sequana dev team                                       #
# See the COPYRIGHT file for details                                      #
#                                                                         #
# Versionix is free software: you can redistribute it and/or modify       #
# it under the terms of the GNU General Public License as published by    #
# the Free Software Foundation, either version 3 of the License, or       #
# (at your option) any later version.                                     #
#                                                                         #
# Versionix  is distributed in the hope that it will be useful,           #
# but WITHOUT ANY WARRANTY; without even the implied warranty of          #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           #
# GNU General Public License for more details.                            #
#                                                                         #
# You should have received a copy of the GNU General Public License       #
# along with this program (COPYING file).                                 #
# If not, see <http://www.gnu.org/licenses/>.                             #
###########################################################################
""".. rubric:: Standalone application dedicated to Damona"""
import sys

import colorlog
import rich_click as click

from versionix import version
from versionix.parser import get_version

__all__ = ["main"]

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

click.rich_click.USE_MARKDOWN = True
click.rich_click.SHOW_METAVARS_COLUMN = True
click.rich_click.APPEND_METAVARS_HELP = True
click.rich_click.STYLE_ERRORS_SUGGESTION = "magenta italic"
click.rich_click.SHOW_ARGUMENTS = True

logger = colorlog.getLogger(__name__)


@click.command()
@click.argument("standalone", required=False, type=click.STRING, default=None)
@click.version_option(version)
@click.option("--registered", is_flag=True, help="Prints the list of registered tools")
@click.option(
    "--logger-level",
    type=click.Choice(["INFO", "DEBUG", "WARNING", "ERROR"]),
    help="level for debugging",
    default="INFO",
)
def main(**kwargs):
    """Versionix returns the version of bioinformatics software.

    ----

        versionix fastqc

    You can check the list of registered tools as follows

        versionix --registered


    """

    from versionix import logger

    logger._set_level(kwargs["logger_level"])

    if kwargs["registered"]:
        from versionix.registry import metadata

        names = sorted(metadata.keys())
        for name in names:
            click.echo(f"{name}")
    else:
        if kwargs["standalone"] is None:
            click.echo(
                "No standalone was provided. You must provide one. You can use --registered to see the current list'"
            )
            sys.exit(1)
        else:
            click.echo(get_version(kwargs["standalone"]))
