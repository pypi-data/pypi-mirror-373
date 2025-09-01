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

"""
https://stackoverflow.com/questions/61679282/create-web-server-using-only-standard-library
https://html.spec.whatwg.org/multipage/
"""

from collections import ChainMap
from collections.abc import Generator
import copy
import enum
import html
import sys
import textwrap
from types import SimpleNamespace
import warnings

from spiki.speechmark import SpeechMark


class Renderer:

    class Options(enum.Enum):
        tag_mode    = ["open", "pair", "void"]
        block_wrap  = ["div", "section", "none"]
        block_site  = ["above", "below", "stripe"]

    def __init__(self, template: dict = None, *, config: dict = None):
        self.template = template or dict()
        self.state = SimpleNamespace(attrib={}, blocks=[], config=ChainMap(config or dict()))
        self.sm = SpeechMark()

    @staticmethod
    def check_config(config: dict, options: enum.Enum):
        for option in options:
            try:
                if config[option.name] not in option.value:
                    warnings.warn(f"'{config[option.name]}' is not one of {option.value}")
            except KeyError:
                continue
        return config

    def get_option(self, option: "Option"):
        rv = self.state.config.get(option.name, None)
        return rv in option.value and rv

    def gen_blocks(self, **kwargs) -> Generator[str]:
        block_wrap = self.get_option(self.Options.block_wrap)
        for n, block in enumerate(self.state.blocks):
            if block_wrap:
                yield f'<{block_wrap} id="{n:02d}">'
            block = block.format(**kwargs)
            for line in self.sm.feed(textwrap.dedent(block).strip(), terminate=True):
                yield line.replace('<li id="', f'<li id="{n:02d}-')
            self.sm.reset()
            if block_wrap:
                yield f"</{block_wrap}>"

    def gen_nodes(self, tree: dict, **kwargs) -> Generator[str]:
        attrs =  (" " + " ".join(f'{k}="{html.escape(v)}"' for k, v in self.state.attrib.items())).rstrip()
        tag_mode = self.get_option(self.Options.tag_mode)
        pool = [(node, v) for node, v in tree.items() if isinstance(v, str)]
        for node, entry in pool:
            entry = html.escape(entry.format(**kwargs))
            if tag_mode == "open":
                yield f"<{node}{attrs}>"
            elif tag_mode == "pair":
                yield f"<{node}{attrs}>{entry}</{node}>"
            elif tag_mode == "void":
                yield f"<{node}{attrs} />"

    def walk(self, tree: dict, path: list = None, context: dict = None) -> Generator[str]:
        path = path or list()
        context = context or dict()

        self.state.attrib = tree.pop("attrib", {})
        blocks = tree.pop("blocks", "")
        # print(f"{blocks=}")
        self.state.blocks = [blocks] if isinstance(blocks, str) else blocks
        self.state.config = self.state.config.new_child(self.check_config(tree.pop("config", {}), self.Options))

        attrs = (" " + " ".join(f'{k}="{html.escape(v)}"' for k, v in self.state.attrib.items())).rstrip()
        tag_mode = self.get_option(self.Options.tag_mode)

        try:
            tag = next(i for i in reversed(path) if isinstance(i, str))
            if any(i for i in tree.values() if isinstance(i, str)):
                params = ""
            else:
                params = attrs

            if tag_mode in ["open", "pair"]:
                yield f"<{tag}{params}>"
            elif tag_mode == "void":
                yield f"<{tag}{params} />"
        except StopIteration:
            pass

        block_site = self.get_option(self.Options.block_site)
        if block_site == "above":
            yield from self.gen_blocks(**context)
            yield from self.gen_nodes(tree, **context)
        else:
            yield from self.gen_nodes(tree, **context)
            yield from self.gen_blocks(**context)

        pool = [(k, v) for k, v in tree.items() if isinstance(v, list)]
        for node, entry in pool:
            for n, item in enumerate(entry):
                yield from self.walk(item, path=path + [node, n], context=context)

        pool = [(k, v) for k, v in tree.items() if isinstance(v, dict)]
        for node, entry in pool:
            yield from self.walk(entry, path=path + [node], context=context)

        try:
            tag = next(i for i in reversed(path) if isinstance(i, str))
            if tag_mode == "pair":
                yield f"</{tag}>"
        except StopIteration:
            pass

        self.state.config.maps.pop(0)

    def serialize(self, template: dict = None) -> str:
        self.template.update(template or dict())
        context = copy.deepcopy(self.template)
        tree = context.pop("doc", dict())
        return "\n".join(filter(None, self.walk(tree, path=[], context=context)))
