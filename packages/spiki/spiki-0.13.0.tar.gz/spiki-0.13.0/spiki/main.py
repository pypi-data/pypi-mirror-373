#!/usr/bin/env python
#   encoding: utf-8

# Copyright (C) 2025 D E Haynes
# This file is part of spiki.

# Spiki is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# Spiki is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even
# the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with spiki.
# If not, see <https://www.gnu.org/licenses/>.


import argparse
import logging
import os.path
from pathlib import Path
import shutil
import sys

from spiki.renderer import Renderer
from spiki.visitor import Visitor

from spiki.plugin import Phase


default_plugin_types = [
    "spiki.plugins.finder:Finder",
    "spiki.plugins.loader:Loader",
    # "spiki.plugins.indexer:Indexer",
    "spiki.plugins.writer:Writer",
]


def setup_logger(level=logging.INFO):
    logging.basicConfig(level=level)
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        handler.setFormatter(
            logging.Formatter(
                fmt="{asctime}|{levelname:>8}|{phase.name:^8}| {name:<16}| {path!s:<72}| {message}",
                datefmt=None, style='{',
                defaults=dict(phase=Phase.CONFIG, path="")
            )
        )


def main(args):
    level = logging.DEBUG if args.debug else logging.INFO
    setup_logger(level=level)
    logger = logging.getLogger("spiki")
    args.output.mkdir(parents=True, exist_ok=True)

    plugin_types = args.plugin or default_plugin_types
    with Visitor(*plugin_types, **vars(args)) as visitor:
        for n, change in enumerate(visitor.walk(*args.paths)):
            pass

    logger.info(f"Completed {n} actions", extra=dict(phase=Phase.REPORT))
    return 0


def parser():
    default_path = Path.cwd().joinpath("output").resolve()
    rv = argparse.ArgumentParser(usage=__doc__, fromfile_prefix_chars="=")
    rv.add_argument("paths", nargs="+", type=Path, help="Specify file paths")
    rv.add_argument("-O", "--output", type=Path, default=default_path, help=f"Specify output directory [{default_path}]")
    rv.add_argument("--plugin", action="append", help=f"Specify plugin list {default_plugin_types}")
    rv.add_argument("--debug", action="store_true", default=False, help=f"Display debug logs")
    rv.convert_arg_line_to_args = lambda x: x.split()
    return rv


def run():
    p = parser()
    args, res = p.parse_known_args()
    rv = main(args)
    sys.exit(rv)


if __name__ == "__main__":
    run()
