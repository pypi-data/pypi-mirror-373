# -*- coding: utf-8; -*-

import os
from unittest import TestCase
from unittest.mock import MagicMock, patch

import typer

from wuttjamaican.conf import WuttaConfig
from wuttjamaican.cli import base as mod


here = os.path.dirname(__file__)
example_conf = os.path.join(here, "example.conf")


class TestMakeCliConfig(TestCase):

    def test_basic(self):
        ctx = MagicMock(params={"config_paths": [example_conf]})
        config = mod.make_cli_config(ctx)
        self.assertIsInstance(config, WuttaConfig)
        self.assertEqual(config.files_read, [example_conf])


class TestTyperCallback(TestCase):

    def test_basic(self):
        ctx = MagicMock(params={"config_paths": [example_conf]})
        mod.typer_callback(ctx)
        self.assertIsInstance(ctx.wutta_config, WuttaConfig)
        self.assertEqual(ctx.wutta_config.files_read, [example_conf])


class TestTyperEagerImports(TestCase):

    def test_basic(self):
        typr = mod.make_typer(name="foobreezy")
        with patch.object(mod, "load_entry_points") as load_entry_points:
            mod.typer_eager_imports(typr)
            load_entry_points.assert_called_once_with("foobreezy.typer_imports")


class TestMakeTyper(TestCase):

    def test_basic(self):
        typr = mod.make_typer()
        self.assertIsInstance(typr, typer.Typer)
