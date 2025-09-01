# -*- coding: utf-8; -*-

import os
from unittest.mock import MagicMock, patch

from wuttjamaican.testing import ConfigTestCase
from wuttjamaican.cli import make_appdir as mod
from wuttjamaican.app import AppHandler


here = os.path.dirname(__file__)
example_conf = os.path.join(here, "example.conf")


class TestMakeAppdir(ConfigTestCase):

    def test_basic(self):
        appdir = os.path.join(self.tempdir, "app")
        ctx = MagicMock(params={"config_paths": [example_conf], "appdir_path": appdir})
        ctx.parent.wutta_config = self.config

        with patch.object(AppHandler, "make_appdir") as make_appdir:
            mod.make_appdir(ctx)
            make_appdir.assert_called_once_with(appdir)
