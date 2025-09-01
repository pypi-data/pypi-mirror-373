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

import importlib.resources
import pathlib
import tempfile
import textwrap
import tomllib
import unittest

import spiki
from spiki.plugin import Phase
from spiki.renderer import Renderer
from spiki.visitor import Visitor


class VisitorTests(unittest.TestCase):

    def test_example_atom(self):
        plugin_types = [
            "spiki.plugins.finder:Finder",
            "spiki.plugins.loader:Loader",
            # "spiki.plugins.indexer:Indexer",
            "spiki.plugins.writer:Writer",
        ]
        examples = importlib.resources.files("spiki.examples")
        witness = []
        with (
            tempfile.TemporaryDirectory() as output_name,
            Visitor(*plugin_types) as visitor,
        ):
            visitor.options = dict(
                output=pathlib.Path(output_name).resolve(),
                paths=[examples.joinpath("atom")],
            )

            self.assertFalse(visitor.state)
            for change in visitor.walk(*visitor.options["paths"]):
                witness.append(change)

            output_path = pathlib.Path(output_name)
            files = list(output_path.glob("*.html"))

        self.assertEqual(len(visitor.state), 1, visitor.state)
        path = list(visitor.state)[0]
        self.assertEqual("a.toml", path.name)
        self.assertEqual(
            visitor.state[path].node["doc"]["html"]["body"]["main"]["blocks"],
            ["    Hello, World!\n\n    "]
        )

        doc = visitor.state[path].doc
        self.assertIsInstance(doc, str)
        self.assertLess(doc.index("<head"), doc.index("<body"))
        self.assertEqual(doc.count("<meta"), 3)

        self.assertEqual(len([i for i in witness if i.phase == Phase.SURVEY]), 1)
        self.assertEqual(len([i for i in witness if i.phase == Phase.INGEST]), 2)
        self.assertEqual(len([i for i in witness if i.phase == Phase.ENRICH]), 1)
        self.assertEqual(len([i for i in witness if i.phase == Phase.RENDER]), 1)
        self.assertEqual(len([i for i in witness if i.phase == Phase.EXPORT]), 2)

        self.assertEqual(len(files), 1)
        self.assertEqual(files[0].name, "a.html")

    def test_example_basic(self):
        plugin_types = [
            "spiki.plugins.finder:Finder",
            "spiki.plugins.loader:Loader",
            # "spiki.plugins.indexer:Indexer",
            "spiki.plugins.writer:Writer",
        ]
        examples = importlib.resources.files("spiki.examples")
        witness = []
        with (
            tempfile.TemporaryDirectory() as output_name,
            Visitor(*plugin_types) as visitor,
        ):
            visitor.options = dict(
                output=pathlib.Path(output_name).resolve(),
                paths=[examples.joinpath("basic")],
            )

            self.assertFalse(visitor.state)
            for change in visitor.walk(*visitor.options["paths"]):
                witness.append(change)

            output_path = pathlib.Path(output_name)
            files = list(output_path.glob("*.css")) + list(output_path.glob("*.html"))

        self.assertEqual(len(visitor.state), 10, visitor.state)
        path = list(visitor.state)[0]
        self.assertEqual("a.toml", path.name)

        doc = visitor.state[path].doc
        self.assertIsInstance(doc, str)
        self.assertLess(doc.index("<head"), doc.index("<body"))
        self.assertEqual(doc.count("<meta"), 3)
        self.assertLess(doc.index("<nav"), doc.index("<blockquote"), visitor.state[path].node)

        self.assertEqual(len([i for i in witness if i.phase == Phase.SURVEY]), 10)
        self.assertEqual(len([i for i in witness if i.phase == Phase.INGEST]), 20)
        self.assertEqual(len([i for i in witness if i.phase == Phase.ENRICH]), 10)
        self.assertEqual(len([i for i in witness if i.phase == Phase.RENDER]), 10)
        self.assertEqual(len([i for i in witness if i.phase == Phase.EXPORT]), 11)

        file_names = sorted([i.name for i in files])
        self.assertEqual(len(files), 7, files)
        self.assertEqual(file_names[0], "a.html")
        self.assertEqual(file_names[2], "basics.css")
