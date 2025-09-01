# -*- coding: utf-8; -*-

import sys
from unittest import TestCase
from unittest.mock import patch, MagicMock

import pytest

from wuttjamaican import util as mod
from wuttjamaican.progress import ProgressBase


class A:
    pass


class B(A):
    pass


class C(B):
    pass


class TestGetClassHierarchy(TestCase):

    def test_basic(self):

        classes = mod.get_class_hierarchy(A)
        self.assertEqual(classes, [A])

        classes = mod.get_class_hierarchy(B)
        self.assertEqual(classes, [A, B])

        classes = mod.get_class_hierarchy(C)
        self.assertEqual(classes, [A, B, C])

        classes = mod.get_class_hierarchy(C, topfirst=False)
        self.assertEqual(classes, [C, B, A])


class TestLoadEntryPoints(TestCase):

    def test_empty(self):
        # empty set returned for unknown group
        result = mod.load_entry_points("this_should_never_exist!!!!!!")
        self.assertEqual(result, {})

    def test_basic(self):
        # load some entry points which should "always" be present,
        # even in a testing environment.  basic sanity check
        result = mod.load_entry_points("console_scripts", ignore_errors=True)
        self.assertTrue(len(result) >= 1)
        self.assertIn("pip", result)

    def test_basic_pre_python_3_10(self):

        # the goal here is to get coverage for code which would only
        # run on python 3,9 and older, but we only need that coverage
        # if we are currently testing python 3.10+
        if sys.version_info.major == 3 and sys.version_info.minor < 10:
            pytest.skip("this test is not relevant before python 3.10")

        import importlib.metadata

        real_entry_points = importlib.metadata.entry_points()

        class FakeEntryPoints(dict):
            def get(self, group, default):
                return real_entry_points.select(group=group)

        importlib = MagicMock()
        importlib.metadata.entry_points.return_value = FakeEntryPoints()

        with patch.dict("sys.modules", **{"importlib": importlib}):

            # load some entry points which should "always" be present,
            # even in a testing environment.  basic sanity check
            result = mod.load_entry_points("console_scripts", ignore_errors=True)
            self.assertTrue(len(result) >= 1)
            self.assertIn("pytest", result)

    def test_basic_pre_python_3_8(self):

        # the goal here is to get coverage for code which would only
        # run on python 3.7 and older, but we only need that coverage
        # if we are currently testing python 3.8+
        if sys.version_info.major == 3 and sys.version_info.minor < 8:
            pytest.skip("this test is not relevant before python 3.8")

        from importlib.metadata import entry_points

        real_entry_points = entry_points()

        class FakeEntryPoints(dict):
            def get(self, group, default):
                if hasattr(real_entry_points, "select"):
                    return real_entry_points.select(group=group)
                return real_entry_points.get(group, [])

        importlib_metadata = MagicMock()
        importlib_metadata.entry_points.return_value = FakeEntryPoints()

        orig_import = __import__

        def mock_import(name, *args, **kwargs):
            if name == "importlib.metadata":
                raise ImportError
            if name == "importlib_metadata":
                return importlib_metadata
            return orig_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):

            # load some entry points which should "always" be present,
            # even in a testing environment.  basic sanity check
            result = mod.load_entry_points("console_scripts", ignore_errors=True)
            self.assertTrue(len(result) >= 1)
            self.assertIn("pytest", result)

    def test_error(self):

        # skip if < 3.8
        if sys.version_info.major == 3 and sys.version_info.minor < 8:
            pytest.skip("this requires python 3.8 for entry points via importlib")

        entry_point = MagicMock()
        entry_point.load.side_effect = NotImplementedError

        entry_points = MagicMock()
        entry_points.select.return_value = [entry_point]

        importlib = MagicMock()
        importlib.metadata.entry_points.return_value = entry_points

        with patch.dict("sys.modules", **{"importlib": importlib}):

            # empty set returned if errors suppressed
            result = mod.load_entry_points("wuttatest.thingers", ignore_errors=True)
            self.assertEqual(result, {})
            importlib.metadata.entry_points.assert_called_once_with()
            entry_points.select.assert_called_once_with(group="wuttatest.thingers")
            entry_point.load.assert_called_once_with()

            # error is raised, if not suppressed
            importlib.metadata.entry_points.reset_mock()
            entry_points.select.reset_mock()
            entry_point.load.reset_mock()
            self.assertRaises(
                NotImplementedError, mod.load_entry_points, "wuttatest.thingers"
            )
            importlib.metadata.entry_points.assert_called_once_with()
            entry_points.select.assert_called_once_with(group="wuttatest.thingers")
            entry_point.load.assert_called_once_with()


class TestLoadObject(TestCase):

    def test_missing_spec(self):
        self.assertRaises(ValueError, mod.load_object, None)

    def test_basic(self):
        result = mod.load_object("unittest:TestCase")
        self.assertIs(result, TestCase)


class TestMakeUUID(TestCase):

    def test_basic(self):
        uuid = mod.make_uuid()
        self.assertEqual(len(uuid), 32)


class TestParseBool(TestCase):

    def test_null(self):
        self.assertIsNone(mod.parse_bool(None))

    def test_bool(self):
        self.assertTrue(mod.parse_bool(True))
        self.assertFalse(mod.parse_bool(False))

    def test_string_true(self):
        self.assertTrue(mod.parse_bool("true"))
        self.assertTrue(mod.parse_bool("yes"))
        self.assertTrue(mod.parse_bool("y"))
        self.assertTrue(mod.parse_bool("on"))
        self.assertTrue(mod.parse_bool("1"))

    def test_string_false(self):
        self.assertFalse(mod.parse_bool("false"))
        self.assertFalse(mod.parse_bool("no"))
        self.assertFalse(mod.parse_bool("n"))
        self.assertFalse(mod.parse_bool("off"))
        self.assertFalse(mod.parse_bool("0"))
        # nb. assume false for unrecognized input
        self.assertFalse(mod.parse_bool("whatever-else"))


class TestParseList(TestCase):

    def test_null(self):
        value = mod.parse_list(None)
        self.assertIsInstance(value, list)
        self.assertEqual(len(value), 0)

    def test_list_instance(self):
        mylist = []
        value = mod.parse_list(mylist)
        self.assertIs(value, mylist)

    def test_single_value(self):
        value = mod.parse_list("foo")
        self.assertEqual(len(value), 1)
        self.assertEqual(value[0], "foo")

    def test_single_value_padded_by_spaces(self):
        value = mod.parse_list("   foo   ")
        self.assertEqual(len(value), 1)
        self.assertEqual(value[0], "foo")

    def test_slash_is_not_a_separator(self):
        value = mod.parse_list("/dev/null")
        self.assertEqual(len(value), 1)
        self.assertEqual(value[0], "/dev/null")

    def test_multiple_values_separated_by_whitespace(self):
        value = mod.parse_list("foo bar baz")
        self.assertEqual(len(value), 3)
        self.assertEqual(value[0], "foo")
        self.assertEqual(value[1], "bar")
        self.assertEqual(value[2], "baz")

    def test_multiple_values_separated_by_commas(self):
        value = mod.parse_list("foo,bar,baz")
        self.assertEqual(len(value), 3)
        self.assertEqual(value[0], "foo")
        self.assertEqual(value[1], "bar")
        self.assertEqual(value[2], "baz")

    def test_multiple_values_separated_by_whitespace_and_commas(self):
        value = mod.parse_list("  foo,   bar   baz")
        self.assertEqual(len(value), 3)
        self.assertEqual(value[0], "foo")
        self.assertEqual(value[1], "bar")
        self.assertEqual(value[2], "baz")

    def test_multiple_values_separated_by_whitespace_and_commas_with_some_quoting(self):
        value = mod.parse_list(
            """
        foo
        "C:\\some path\\with spaces\\and, a comma",
        baz
        """
        )
        self.assertEqual(len(value), 3)
        self.assertEqual(value[0], "foo")
        self.assertEqual(value[1], "C:\\some path\\with spaces\\and, a comma")
        self.assertEqual(value[2], "baz")

    def test_multiple_values_separated_by_whitespace_and_commas_with_single_quotes(
        self,
    ):
        value = mod.parse_list(
            """
        foo
        'C:\\some path\\with spaces\\and, a comma',
        baz
        """
        )
        self.assertEqual(len(value), 3)
        self.assertEqual(value[0], "foo")
        self.assertEqual(value[1], "C:\\some path\\with spaces\\and, a comma")
        self.assertEqual(value[2], "baz")


class TestMakeTitle(TestCase):

    def test_basic(self):
        text = mod.make_title("foo_bar")
        self.assertEqual(text, "Foo Bar")


class TestMakeFullName(TestCase):

    def test_basic(self):
        name = mod.make_full_name("Fred", "", "Flintstone", "")
        self.assertEqual(name, "Fred Flintstone")


class TestProgressLoop(TestCase):

    def test_basic(self):

        def act(obj, i):
            pass

        # with progress
        mod.progress_loop(act, [1, 2, 3], ProgressBase, message="whatever")

        # without progress
        mod.progress_loop(act, [1, 2, 3], None, message="whatever")


class TestResourcePath(TestCase):

    def test_basic(self):

        # package spec is resolved to path
        path = mod.resource_path("wuttjamaican:util.py")
        self.assertTrue(path.endswith("wuttjamaican/util.py"))

        # absolute path returned as-is
        self.assertEqual(
            mod.resource_path("/tmp/doesnotexist.txt"), "/tmp/doesnotexist.txt"
        )

    def test_basic_pre_python_3_9(self):

        # the goal here is to get coverage for code which would only
        # run on python 3.8 and older, but we only need that coverage
        # if we are currently testing python 3.9+
        if sys.version_info.major == 3 and sys.version_info.minor < 9:
            pytest.skip("this test is not relevant before python 3.9")

        from importlib.resources import files, as_file

        orig_import = __import__

        def mock_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "importlib.resources":
                raise ImportError
            if name == "importlib_resources":
                return MagicMock(files=files, as_file=as_file)
            return orig_import(name, globals, locals, fromlist, level)

        with patch("builtins.__import__", side_effect=mock_import):

            # package spec is resolved to path
            path = mod.resource_path("wuttjamaican:util.py")
            self.assertTrue(path.endswith("wuttjamaican/util.py"))

            # absolute path returned as-is
            self.assertEqual(
                mod.resource_path("/tmp/doesnotexist.txt"), "/tmp/doesnotexist.txt"
            )


class TestSimpleError(TestCase):

    def test_with_description(self):
        try:
            raise RuntimeError("just testin")
        except Exception as error:
            result = mod.simple_error(error)
        self.assertEqual(result, "RuntimeError: just testin")

    def test_without_description(self):
        try:
            raise RuntimeError
        except Exception as error:
            result = mod.simple_error(error)
        self.assertEqual(result, "RuntimeError")
