# -*- coding: utf-8; -*-

from unittest import TestCase

from wuttjamaican import progress as mod


class TestProgressBase(TestCase):

    def test_basic(self):

        # sanity / coverage check
        prog = mod.ProgressBase("testing", 2)
        prog.update(1)
        prog.update(2)
        prog.finish()


class TestConsoleProgress(TestCase):

    def test_basic(self):

        # sanity / coverage check
        prog = mod.ConsoleProgress("testing", 2)
        prog.update(1)
        prog.update(2)
        prog.finish()
