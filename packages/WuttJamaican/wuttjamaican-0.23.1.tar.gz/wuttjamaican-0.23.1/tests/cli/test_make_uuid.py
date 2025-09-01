# -*- coding: utf-8; -*-

import os
from unittest import TestCase
from unittest.mock import MagicMock, patch

from wuttjamaican.cli import make_uuid as mod


here = os.path.dirname(__file__)
example_conf = os.path.join(here, "example.conf")


class TestMakeUuid(TestCase):

    def test_basic(self):
        ctx = MagicMock(params={"config_paths": [example_conf]})
        with patch.object(mod, "sys") as sys:
            mod.make_uuid(ctx)
            sys.stdout.write.assert_called_once()
