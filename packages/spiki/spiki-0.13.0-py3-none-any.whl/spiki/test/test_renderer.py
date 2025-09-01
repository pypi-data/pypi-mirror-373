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

import textwrap
import tomllib
import unittest

from spiki.renderer import Renderer


class RendererTests(unittest.TestCase):

    def test_config_option(self):
        toml = textwrap.dedent("""
        [doc]
        config = {tag_mode = "invalid"}
        """)
        template = tomllib.loads(toml)
        r = Renderer()
        with self.assertWarns(UserWarning) as context:
            rv = r.serialize(template)
        self.assertFalse(rv)
        self.assertIn("invalid", format(context.warning))

    def test_config_scope(self):
        toml = textwrap.dedent("""
        [doc.html.body.header.nav]
        attrib = {popovertarget = "menu"}
        config = {tag_mode = "pair"}
        button = "Click for Menu"
        """).strip()
        template = tomllib.loads(toml)
        rv = Renderer().serialize(template)
        self.assertIn("<nav>", rv)
        self.assertIn('<button popovertarget="menu">', rv)

    def test_head(self):
        test = "Essential head content"
        goal = textwrap.dedent(f"""
        <!doctype html>
        <html lang="en">
        <head>
        <title>{test}</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <meta http-equiv="X-UA-Compatible" content="ie=edge">
        </head>
        </html>
        """).strip()

        toml = textwrap.dedent("""
        [doc]
        config = {tag_mode = "open"}

        "!doctype html" = ""

        [doc.html]
        config = {tag_mode = "pair"}
        attrib = {lang = "en"}

        [doc.html.head]
        title = ""

        [[doc.html.head.meta]]
        config = {tag_mode = "open"}
        attrib = {charset = "UTF-8"}

        [[doc.html.head.meta]]
        config = {tag_mode = "void"}
        attrib = {name = "viewport", content = "width=device-width, initial-scale=1.0"}

        [[doc.html.head.meta]]
        config = {tag_mode = "open"}
        attrib = {http-equiv = "X-UA-Compatible", content = "ie=edge"}

        """)

        template = tomllib.loads(toml)
        template["doc"]["html"]["head"]["title"] = test
        rv = Renderer().serialize(template)
        self.assertEqual(rv, goal, template)

    def test_blocks(self):
        test = "Multiple speech blocks"
        toml = textwrap.dedent("""
        [doc]

        [doc.html]
        config = {tag_mode = "pair"}

        [doc.html.head]
        title = ""

        [doc.html.body]
        blocks = [
            '''
            <STAFF.proposing#3> What would you like sir? We have some very good fish today.
                1. Order the Beef Wellington
                2. Go for the Cottage Pie
                3. Try the Dover Sole

            ''',
            '''
            <GUEST.offering> Give me a another minute or two, would you?
            ''',
            '''
            <STAFF.clarifying> Certainly, sir.
            '''
        ]

        """)
        template = tomllib.loads(toml)
        template["doc"]["html"]["head"]["title"] = test
        rv = Renderer().serialize(template)
        self.assertTrue(rv.startswith("<html>"))
        self.assertTrue(rv.endswith("</html>"))
        self.assertIn("<body>", rv)
        self.assertIn("</body>", rv)
        self.assertEqual(rv.count("<blockquote"), 3)
        self.assertEqual(rv.count("</blockquote>"), 3)
        block = rv[rv.index("<blockquote"):rv.index("</blockquote>")]
        for tag in [
            "<cite", "</cite>", "<ol", '<li id="00-1"', '<li id="00-2"', '<li id="00-3"', "</ol>",
        ]:
            self.assertIn(tag, block)

    def test_block_wrap(self):
        test = "Div-wrapped speech blocks"
        toml = textwrap.dedent("""
        [doc]

        [doc.html]
        config = {tag_mode = "pair"}

        [doc.html.head]
        title = ""

        [doc.html.body]
        config = {tag_mode = "pair", block_wrap = "div"}
        blocks = [
            '''
            <STAFF.proposing#3> What would you like sir? We have some very good fish today.
                1. Order the Beef Wellington
                2. Go for the Cottage Pie
                3. Try the Dover Sole

            ''',
            '''
            <GUEST.offering> Give me a another minute or two, would you?
            ''',
            '''
            <STAFF.clarifying> Certainly, sir.
            '''
        ]

        """)
        template = tomllib.loads(toml)
        template["doc"]["html"]["head"]["title"] = test
        rv = Renderer().serialize(template)
        self.assertTrue(rv.startswith("<html>"))
        self.assertTrue(rv.endswith("</html>"))
        self.assertIn("<body>", rv)
        self.assertIn("</body>", rv)
        self.assertEqual(rv.count("<div"), 3)
        self.assertEqual(rv.count("</div>"), 3)
        self.assertEqual(rv.count("<blockquote"), 3)
        self.assertEqual(rv.count("</blockquote>"), 3)
        block = rv[rv.index("<div"):rv.index("</div>")]
        for tag in [
            "<cite", "</cite>", "<ol", '<li id="00-1"', '<li id="00-2"', '<li id="00-3"', "</ol>",
        ]:
            self.assertIn(tag, block)

    def test_context(self):
        test = "Test variable substitution & escaping"
        toml = textwrap.dedent("""
        [metadata]

        [doc]

        [doc.html]
        config = {tag_mode = "pair"}

        [doc.html.head]
        title = "{metadata[title]}"

        [doc.html.body]
        blocks = ["It's vital to {metadata[title]}."]

        """)
        template = tomllib.loads(toml)
        template["metadata"]["title"] = test
        rv = Renderer().serialize(template)
        self.assertTrue(rv.startswith("<html>"))
        self.assertTrue(rv.endswith("</html>"))
        self.assertIn("<head>", rv)
        self.assertIn("</head>", rv)
        self.assertIn("<title>Test variable substitution &amp; escaping</title>", rv)
        self.assertIn("It's vital to Test variable substitution &amp; escaping.", rv)
