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

from collections.abc import Callable
from collections.abc import Generator
import contextlib
import copy
import dataclasses
import datetime
import decimal
import logging
from numbers import Number
import os.path
from pathlib import Path
import pkgutil
import shutil
import string
import tempfile
import tomllib
import warnings

from spiki.plugin import Change
from spiki.plugin import Phase


class Visitor(contextlib.ExitStack):

    @staticmethod
    def location_of(node: dict) -> Path:
        try:
            return node["registry"]["index"]["registry"]["path"].resolve()
        except (AttributeError, KeyError, TypeError):
            return node["registry"]["path"].resolve()

    @staticmethod
    def url_of(node: dict) -> str:
        root = node["registry"]["root"]
        parent = Visitor.location_of(node).relative_to(root).parent
        return parent.joinpath(node["metadata"]["slug"]).with_suffix(".html").as_posix()

    def __init__(self, *plugin_types: tuple[Callable], **kwargs):
        super().__init__()
        self.index_name = "index.toml"
        self.state = dict()
        self.running = None
        self.space = None
        self.logger = logging.getLogger("visitor")
        self.plugins = list(filter(None, (self.init_plugin(i) for i in plugin_types)))
        self.options = kwargs

    def __enter__(self):
        self.space = Path(tempfile.mkdtemp()).resolve()
        self.running = [self.enter_context(p) for p in self.plugins]
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        rv = super().__exit__(exc_type, exc_val, exc_tb)
        shutil.rmtree(self.space, ignore_errors=True)
        return rv

    @property
    def root(self) -> Path:
        paths = [i.resolve() for i in self.options.get("paths", [])]
        return Path(os.path.commonprefix(paths))

    def init_plugin(self, type_name: str):
        try:
            cls = pkgutil.resolve_name(type_name)
        except (AttributeError, ModuleNotFoundError) as error:
            self.logger.warning(f"'{type_name}' not resolved. Plugin not loaded.")
            return None

        plugin = cls(self)
        return plugin

    def ancestors(self, path: Path) -> list[Path]:
        return sorted(
            (p for p in self.nodes
             if path.is_relative_to(p.parent)
             and p.name == self.index_name
            ),
            key=lambda x: len(format(x))
        )

    def walk(self, *paths: list[Path]) -> Generator[tuple[Path, dict, str]]:
        paths = [i.resolve() for i in paths]
        for phase in [Phase.CONFIG, Phase.SURVEY]:
            for path in paths:
                for plugin in self.running:
                    try:
                        changes = list(plugin(phase, path=path) or [])
                    except Exception as error:
                        self.logger.warning(error, extra=dict(phase=phase), exc_info=True)
                        continue

                    for change in changes:
                        try:
                            yield dataclasses.replace(change, phase=phase)
                            self.state[change.path] = dataclasses.replace(
                                self.state.setdefault(change.path, change),
                                phase=phase,
                            )
                        except TypeError:
                            continue
            else:
                for change in filter(None, (plugin(phase) for plugin in self.running)):
                    yield dataclasses.replace(change, phase=phase)

        for phase in list(Phase)[2:]:
            for path in list(self.state):
                for plugin in self.running:
                    state = self.state[path]
                    try:
                        change = plugin(phase, path=path, text=state.text, node=state.node, doc=state.doc)
                    except Exception as error:
                        self.logger.warning(error, extra=dict(phase=phase), exc_info=True)
                        continue

                    try:
                        yield dataclasses.replace(change, phase=phase)
                    except TypeError:
                        continue

                    if change.text:
                        self.state[path].text = change.text
                    if change.node:
                        self.state[path].node.update(change.node)
                    if change.doc:
                        self.state[path].doc = change.doc
            else:
                for change in filter(None, (plugin(phase) for plugin in self.running)):
                    yield dataclasses.replace(change, phase=phase)
