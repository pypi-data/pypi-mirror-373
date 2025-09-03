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

metadata = {
    # special -h option, and prints version within the help message
    "aragorn": {"options": "-h", "parsers": [lambda x: x.stdout.split("\n")[1].split()[1].strip("v")]},
    "art_illumina": {"options": "", "parsers": [lambda x: re.search(r"Q Version (\d+\.\d+\.\d+)", x.stdout).group(1)]},
    "circlator": {"options": "version", "parsers": [lambda x: x.stdout.strip()]},
    "DESeq2": {
        "caller": "Rscript -e \"library(DESeq2);packageVersion('DESeq2')\"",
        "parsers": [lambda x: x.stdout.split()[1].strip("’‘")],
    },
    # dot -v hangs so we need to register this command.
    "dot": {"options": "-V", "parsers": [lambda x: x.stderr.split()[4].strip()]},
    # may be removed
    "idr": {"options": "--version", "parsers": [lambda x: x.stdout.split("\n")[0].split()[1]]},
    # complex output
    "igvtools": {
        "options": "version",
        "parsers": [
            lambda data: [x.split()[2] for x in data.stdout.split("\n") if x.startswith("IGV Version")][0],
        ],
    },
    #
    "picard": {
        "options": "SortVcf --version",
        "parsers": [lambda x: x.stderr.split("\n")[1].split(":")[1].split("-")[0]],
    },
    # actually installed as quast.py but sometimes, may be called quast
    "quast": {"options": "", "parsers": [lambda x: x.stderr.split("\n")[1].split()[1]]},
    #
    "ragtag_scaffold.py": {"caller": "ragtag.py --version", "parsers": [lambda x: x.stdout.split("\n")[0][1:]]},
    # "syri": {
    #    "options": "--version",
    #    # "parser": parser_split_2
    # },
    # "vt": {"options": "--version", "parser": parser_split_2_strip_v},
    "for_testing_empty_parsers": {"options": "", "parsers": []},
    "for_testing_no_parsers": {
        "options": "",
    },
}
