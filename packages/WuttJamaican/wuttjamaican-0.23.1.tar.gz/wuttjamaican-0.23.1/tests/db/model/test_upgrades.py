# -*- coding: utf-8; -*-

from unittest import TestCase

try:
    from wuttjamaican.db.model import upgrades as mod
except ImportError:
    pass
else:

    class TestUpgrade(TestCase):

        def test_str(self):
            upgrade = mod.Upgrade(description="upgrade foo")
            self.assertEqual(str(upgrade), "upgrade foo")
