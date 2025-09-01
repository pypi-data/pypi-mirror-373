# -*- coding: utf-8; -*-

import configparser
import os
from unittest import TestCase
from unittest.mock import patch, MagicMock

import pytest

from wuttjamaican import conf as mod

# TODO: get rid of this eventually
from wuttjamaican import conf
from wuttjamaican.exc import ConfigurationError
from wuttjamaican.app import AppHandler
from wuttjamaican.testing import FileTestCase, ConfigTestCase


class TestWuttaConfig(FileTestCase):
    def make_config(self, **kwargs):
        return mod.WuttaConfig(**kwargs)

    def test_contstructor_basic(self):
        config = conf.WuttaConfig()
        self.assertEqual(config.appname, "wutta")
        self.assertEqual(config.files_read, [])

    def test_constructor_valid_files(self):
        myfile = self.write_file("my.conf", "")
        config = conf.WuttaConfig(files=[myfile])
        self.assertEqual(len(config.files_read), 1)
        self.assertEqual(config.files_read[0], myfile)

    def test_constructor_missing_files(self):
        invalid = os.path.join(self.tempdir, "invalid.conf")
        self.assertRaises(FileNotFoundError, conf.WuttaConfig, files=[invalid])

    def test_constructor_required_files_are_present(self):
        first = self.write_file(
            "first.conf",
            """\
[foo]
bar = 1
baz = A
""",
        )

        second = self.write_file(
            "second.conf",
            """\
[wutta.config]
require = %(here)s/first.conf

[foo]
baz = B
""",
        )

        config = conf.WuttaConfig(files=[second])
        self.assertEqual(len(config.files_read), 2)
        # nb. files_read listing is in order of "priority" which is
        # same the as order in which files were initially read
        self.assertEqual(config.files_read[0], second)
        self.assertEqual(config.files_read[1], first)
        self.assertEqual(config.get("foo.bar"), "1")
        self.assertEqual(config.get("foo.baz"), "B")

    def test_constructor_required_files_are_missing(self):
        second = self.write_file(
            "second.conf",
            """\
[wutta.config]
require = %(here)s/first.conf

[foo]
baz = B
""",
        )

        self.assertRaises(FileNotFoundError, conf.WuttaConfig, files=[second])

    def test_constructor_included_files_are_present(self):
        first = self.write_file(
            "first.conf",
            """\
[foo]
bar = 1
baz = A
""",
        )

        second = self.write_file(
            "second.conf",
            """\
[wutta.config]
include = %(here)s/first.conf

[foo]
baz = B
""",
        )

        config = conf.WuttaConfig(files=[second])
        self.assertEqual(len(config.files_read), 2)
        # nb. files_read listing is in order of "priority" which is
        # same the as order in which files were initially read
        self.assertEqual(config.files_read[0], second)
        self.assertEqual(config.files_read[1], first)
        self.assertEqual(config.get("foo.bar"), "1")
        self.assertEqual(config.get("foo.baz"), "B")

    def test_constructor_included_files_are_missing(self):
        second = self.write_file(
            "second.conf",
            """\
[wutta.config]
include = %(here)s/first.conf

[foo]
baz = B
""",
        )

        config = conf.WuttaConfig(files=[second])
        self.assertEqual(len(config.files_read), 1)
        self.assertEqual(config.files_read[0], second)
        self.assertIsNone(config.get("foo.bar"))
        self.assertEqual(config.get("foo.baz"), "B")

    def test_files_only_read_once(self):
        base = self.write_file(
            "base.conf",
            """
[foo]
bar = 1
baz = A
""",
        )

        middle = self.write_file(
            "middle.conf",
            """
[wutta.config]
require = %(here)s/base.conf

[foo]
baz = B
""",
        )

        top = self.write_file(
            "top.conf",
            """
[wutta.config]
require = %(here)s/middle.conf

[foo]
baz = C
""",
        )

        config = conf.WuttaConfig(files=[top, middle, base])
        self.assertEqual(len(config.files_read), 3)
        # nb. files_read listing is in order of "priority" which is
        # same the as order in which files were initially read
        self.assertEqual(config.files_read[0], top)
        self.assertEqual(config.files_read[1], middle)
        self.assertEqual(config.files_read[2], base)
        self.assertEqual(config.get("foo.bar"), "1")
        self.assertEqual(config.get("foo.baz"), "C")

    def test_prioritized_files(self):
        first = self.write_file(
            "first.conf",
            """\
[foo]
bar = 1
""",
        )

        second = self.write_file(
            "second.conf",
            """\
[wutta.config]
require = %(here)s/first.conf
""",
        )

        config = conf.WuttaConfig(files=[second])
        files = config.get_prioritized_files()
        self.assertEqual(len(files), 2)
        self.assertEqual(files[0], second)
        self.assertEqual(files[1], first)

    def test_default_vars_interpolated(self):
        myconf = self.write_file(
            "my.conf",
            """
[foo]
bar = %(here)s/bar.txt
baz = %(__file__)s
""",
        )

        config = conf.WuttaConfig(files=[myconf])
        self.assertEqual(config.get("foo.bar"), f"{self.tempdir}/bar.txt")
        self.assertEqual(config.get("foo.baz"), myconf)

    def test_constructor_defaults(self):
        config = conf.WuttaConfig()
        self.assertEqual(config.defaults, {})
        self.assertIsNone(config.get("foo"))

        config = conf.WuttaConfig(defaults={"foo": "bar"})
        self.assertEqual(config.defaults, {"foo": "bar"})
        self.assertEqual(config.get("foo"), "bar")

    def test_constructor_db_flags(self):
        try:
            # nb. we don't need this import but the test will not
            # behave correctly unless the lib is installed
            import sqlalchemy
        except ImportError:
            pytest.skip("test is not relevant without sqlalchemy")

        myfile = self.write_file(
            "my.conf",
            """\
[wutta.config]
usedb = true
preferdb = true
""",
        )

        # flags are off by default
        config = conf.WuttaConfig()
        self.assertFalse(config.usedb)
        self.assertFalse(config.preferdb)

        # but may override via constructor
        config = conf.WuttaConfig(usedb=True, preferdb=True)
        self.assertTrue(config.usedb)
        self.assertTrue(config.preferdb)

        # and also may override via config file
        config = conf.WuttaConfig(files=[myfile])
        self.assertTrue(config.usedb)
        self.assertTrue(config.preferdb)

    def test_constructor_db_not_supported(self):
        try:
            # nb. we don't need this import but the test will not
            # behave correctly unless the lib is installed
            import sqlalchemy
        except ImportError:
            pytest.skip("test is not relevant without sqlalchemy")

        # flags are off by default
        config = conf.WuttaConfig()
        self.assertFalse(config.usedb)
        self.assertFalse(config.preferdb)

        # but caller may enable the flags (if sqlalchemy available)
        config = conf.WuttaConfig(usedb=True, preferdb=True)
        self.assertTrue(config.usedb)
        self.assertTrue(config.preferdb)

        # but db flags are force-disabled if sqlalchemy not available,
        # regardless of flag values caller provides...

        orig_import = __import__

        def mock_import(name, *args, **kwargs):
            if name == "wuttjamaican.db":
                raise ImportError
            return orig_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            config = conf.WuttaConfig(usedb=True, preferdb=True)
            self.assertFalse(config.usedb)
            self.assertFalse(config.preferdb)

    def test_constructor_may_configure_logging(self):
        myfile = self.write_file(
            "my.conf",
            """\
[wutta.config]
configure_logging = true
""",
        )

        with patch.object(conf.WuttaConfig, "_configure_logging") as method:
            # no logging config by default
            config = conf.WuttaConfig()
            method.assert_not_called()

            # but may override via constructor
            method.reset_mock()
            config = conf.WuttaConfig(configure_logging=True)
            method.assert_called_once()

            # and also may override via config file
            method.reset_mock()
            config = conf.WuttaConfig(files=[myfile])
            method.assert_called_once()

    def test_constructor_configures_logging(self):
        myfile = self.write_file(
            "my.conf",
            """\
[wutta]
timezone.default = America/Chicago

[wutta.config]
configure_logging = true
""",
        )

        with patch("wuttjamaican.conf.logging") as logging:
            # basic constructor attempts logging config
            config = conf.WuttaConfig(configure_logging=True)
            logging.config.fileConfig.assert_called_once()

            # if logging config fails, error is *not* raised
            logging.config.fileConfig.reset_mock()
            logging.config.fileConfig.side_effect = configparser.NoSectionError(
                "logging"
            )
            config = conf.WuttaConfig(configure_logging=True)
            logging.config.fileConfig.assert_called_once()

            # and it works if we specify config file
            logging.config.fileConfig.reset_mock()
            config = conf.WuttaConfig(files=[myfile])
            logging.config.fileConfig.assert_called_once()

    def test_config_has_no_app_after_init(self):
        # initial config should *not* have an app yet, otherwise
        # extensions cannot specify a default app handler
        config = conf.WuttaConfig()
        self.assertIsNone(config._app)

        # but after that we can get an app okay
        app = config.get_app()
        self.assertIsNotNone(app)
        self.assertIs(app, config._app)

    def test_setdefault(self):
        config = conf.WuttaConfig()

        # value is empty by default
        self.assertIsNone(config.get("foo"))

        # but we can change that by setting default
        config.setdefault("foo", "bar")
        self.assertEqual(config.get("foo"), "bar")

        # also, value is returned when we set default
        self.assertIsNone(config.get("baz"))
        self.assertEqual(config.setdefault("baz", "blarg"), "blarg")

    def test_get_require_with_default(self):
        config = conf.WuttaConfig()
        self.assertRaises(ValueError, config.get, "foo", require=True, default="bar")

    def test_get_require_missing(self):
        config = conf.WuttaConfig()
        self.assertRaises(ConfigurationError, config.get, "foo", require=True)

    def test_get_with_default(self):
        config = conf.WuttaConfig()
        # nb. returns None if no default specified
        self.assertIsNone(config.get("foo"))
        self.assertEqual(config.get("foo", default="bar"), "bar")

    def test_get_from_db(self):
        try:
            import sqlalchemy as sa
            from wuttjamaican.db import Session
        except ImportError:
            pytest.skip("test is not relevant without sqlalchemy")

        # minimal config, but at least it needs db cxn info
        config = conf.WuttaConfig(defaults={"wutta.db.default.url": "sqlite://"})

        session = Session()

        # setup table for testing
        session.execute(
            sa.text(
                """
        create table setting (
                name varchar(255) primary key,
                value text
        );
        """
            )
        )
        session.commit()

        # setting not yet defined
        self.assertIsNone(config.get_from_db("foo"))

        # insert setting value to db
        session.execute(sa.text("insert into setting values ('foo', 'bar')"))
        session.commit()

        # now setting returns a value
        self.assertEqual(config.get_from_db("foo"), "bar")

        # also works if we provide the session
        self.assertEqual(config.get_from_db("foo", session=session), "bar")

        session.close()

    def test_get_default(self):
        config = conf.WuttaConfig()
        self.assertIsNone(config.get("foo"))
        self.assertEqual(config.get("foo", default="bar"), "bar")

    def test_get_require(self):
        config = conf.WuttaConfig()
        self.assertIsNone(config.get("foo"))
        self.assertRaises(ConfigurationError, config.get, "foo", require=True)

    def test_get_require_message(self):
        config = conf.WuttaConfig()
        self.assertIsNone(config.get("foo"))
        try:
            config.get("foo", require=True, message="makin stuff up")
        except ConfigurationError as error:
            self.assertIn("makin stuff up", str(error))

    def test_get_preferdb(self):
        try:
            import sqlalchemy as sa
            from wuttjamaican.db import Session
        except ImportError:
            pytest.skip("test is not relevant without sqlalchemy")

        # start out with a default value
        config = conf.WuttaConfig(
            defaults={"wutta.db.default.url": "sqlite://", "foo": "bar"}
        )
        self.assertEqual(config.get("foo"), "bar")

        session = Session()

        # setup table for testing
        session.execute(
            sa.text(
                """
        create table setting (
                name varchar(255) primary key,
                value text
        );
        """
            )
        )
        session.execute(sa.text("insert into setting values ('foo', 'baz')"))
        session.commit()

        # we did not specify usedb=True, so original default is still returned
        self.assertFalse(config.usedb)
        self.assertEqual(config.get("foo"), "bar")

        # usedb but no preferdb means original default is still returned
        self.assertEqual(config.get("foo", usedb=True), "bar")

        # but preferdb should mean newer db value is returned
        self.assertEqual(config.get("foo", usedb=True, preferdb=True), "baz")

        # try a different key to ensure db fallback works if no default present
        session.execute(sa.text("insert into setting values ('blarg', 'blitz')"))
        session.commit()
        self.assertIsNone(config.get("blarg"))
        self.assertEqual(config.get("blarg", usedb=True), "blitz")

        session.close()

    def test_get_ambiguous(self):
        config = conf.WuttaConfig()

        # value is returned if key is not ambiguous
        config.setdefault("foo", "bar")
        self.assertEqual(config.get("foo"), "bar")

        # but None is returned if key is ambiguous
        config.setdefault("foo.bar", "baz")
        self.assertIsNone(config.get("foo"))

    def test_require(self):
        config = conf.WuttaConfig()
        self.assertRaises(ConfigurationError, config.require, "foo")

    def test_get_bool(self):
        config = conf.WuttaConfig()
        self.assertFalse(config.get_bool("foo.bar"))
        config.setdefault("foo.bar", "true")
        self.assertTrue(config.get_bool("foo.bar"))

    def test_get_int(self):
        config = conf.WuttaConfig()
        self.assertIsNone(config.get_int("foo.bar"))
        config.setdefault("foo.bar", "42")
        self.assertEqual(config.get_int("foo.bar"), 42)

    def test_get_list(self):
        config = conf.WuttaConfig()
        self.assertIsNone(config.get_list("foo.bar"))
        config.setdefault("foo.bar", "hello world")
        self.assertEqual(config.get_list("foo.bar"), ["hello", "world"])

    def test_parse_bool_null(self):
        config = self.make_config()
        self.assertIsNone(config.parse_bool(None))

    def test_parse_bool_bool(self):
        config = self.make_config()
        self.assertTrue(config.parse_bool(True))
        self.assertFalse(config.parse_bool(False))

    def test_parse_bool_string_true(self):
        config = self.make_config()
        self.assertTrue(config.parse_bool("true"))
        self.assertTrue(config.parse_bool("yes"))
        self.assertTrue(config.parse_bool("y"))
        self.assertTrue(config.parse_bool("on"))
        self.assertTrue(config.parse_bool("1"))

    def test_parse_bool_string_false(self):
        config = self.make_config()
        self.assertFalse(config.parse_bool("false"))
        self.assertFalse(config.parse_bool("no"))
        self.assertFalse(config.parse_bool("n"))
        self.assertFalse(config.parse_bool("off"))
        self.assertFalse(config.parse_bool("0"))
        # nb. assume false for unrecognized input
        self.assertFalse(config.parse_bool("whatever-else"))

    def test_parse_list_null(self):
        config = self.make_config()
        value = config.parse_list(None)
        self.assertIsInstance(value, list)
        self.assertEqual(len(value), 0)

    def test_parse_list_list_instance(self):
        config = self.make_config()
        mylist = []
        value = config.parse_list(mylist)
        self.assertIs(value, mylist)

    def test_parse_list_single_value(self):
        config = self.make_config()
        value = config.parse_list("foo")
        self.assertEqual(len(value), 1)
        self.assertEqual(value[0], "foo")

    def test_parse_list_single_value_padded_by_spaces(self):
        config = self.make_config()
        value = config.parse_list("   foo   ")
        self.assertEqual(len(value), 1)
        self.assertEqual(value[0], "foo")

    def test_parse_list_slash_is_not_a_separator(self):
        config = self.make_config()
        value = config.parse_list("/dev/null")
        self.assertEqual(len(value), 1)
        self.assertEqual(value[0], "/dev/null")

    def test_parse_list_multiple_values_separated_by_whitespace(self):
        config = self.make_config()
        value = config.parse_list("foo bar baz")
        self.assertEqual(len(value), 3)
        self.assertEqual(value[0], "foo")
        self.assertEqual(value[1], "bar")
        self.assertEqual(value[2], "baz")

    def test_parse_list_multiple_values_separated_by_commas(self):
        config = self.make_config()
        value = config.parse_list("foo,bar,baz")
        self.assertEqual(len(value), 3)
        self.assertEqual(value[0], "foo")
        self.assertEqual(value[1], "bar")
        self.assertEqual(value[2], "baz")

    def test_parse_list_multiple_values_separated_by_whitespace_and_commas(self):
        config = self.make_config()
        value = config.parse_list("  foo,   bar   baz")
        self.assertEqual(len(value), 3)
        self.assertEqual(value[0], "foo")
        self.assertEqual(value[1], "bar")
        self.assertEqual(value[2], "baz")

    def test_parse_list_multiple_values_separated_by_whitespace_and_commas_with_some_quoting(
        self,
    ):
        config = self.make_config()
        value = config.parse_list(
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

    def test_parse_list_multiple_values_separated_by_whitespace_and_commas_with_single_quotes(
        self,
    ):
        config = self.make_config()
        value = config.parse_list(
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

    def test_get_app(self):
        # default handler
        config = conf.WuttaConfig()
        self.assertEqual(config.default_app_handler_spec, "wuttjamaican.app:AppHandler")
        app = config.get_app()
        self.assertIsInstance(app, AppHandler)
        # nb. make extra sure we didn't get a subclass
        self.assertIs(type(app), AppHandler)

        # custom default handler
        config = conf.WuttaConfig()
        config.default_app_handler_spec = "tests.test_conf:CustomAppHandler"
        app = config.get_app()
        self.assertIsInstance(app, CustomAppHandler)

    def test_get_engine_maker(self):
        try:
            from wuttjamaican.db.conf import make_engine_from_config
        except ImportError:
            pytest.skip("test is not relevant without sqlalchemy")

        # default func
        config = conf.WuttaConfig()
        self.assertEqual(
            config.default_engine_maker_spec,
            "wuttjamaican.db.conf:make_engine_from_config",
        )
        make_engine = config.get_engine_maker()
        self.assertIs(make_engine, make_engine_from_config)

        # custom default func
        config = conf.WuttaConfig()
        config.default_engine_maker_spec = (
            "tests.test_conf:custom_make_engine_from_config"
        )
        make_engine = config.get_engine_maker()
        self.assertIs(make_engine, custom_make_engine_from_config)

    def test_production(self):
        config = conf.WuttaConfig()

        # false if not defined
        self.assertFalse(config.production())

        # but config may specify
        config.setdefault("wutta.production", "true")
        self.assertTrue(config.production())


class CustomAppHandler(AppHandler):
    pass


def custom_make_engine_from_config():
    pass


class TestWuttaConfigExtension(TestCase):
    def test_basic(self):
        config = conf.WuttaConfig()
        ext = conf.WuttaConfigExtension()
        self.assertIsNone(ext.key)
        self.assertEqual(repr(ext), "WuttaConfigExtension(key=None)")


class TestGenericDefaultFiles(TestCase):
    def test_linux(self):
        files = conf.generic_default_files("wuttatest")
        self.assertIsInstance(files, list)
        self.assertTrue(len(files) > 1)
        self.assertIn("/etc/wuttatest.conf", files)

    def test_win32(self):
        win32com = MagicMock()
        win32com.shell.SHGetSpecialFolderPath.return_value = r"C:" + os.sep
        with patch.dict("sys.modules", **{"win32com.shell": win32com}):
            with patch("wuttjamaican.conf.sys", platform="win32"):
                files = conf.generic_default_files("wuttatest")
                self.assertIsInstance(files, list)
                self.assertTrue(len(files) > 1)
                self.assertIn(os.path.join("C:", "wuttatest.conf"), files)

    def test_win32_broken(self):
        orig_import = __import__

        def mock_import(name, *args, **kwargs):
            if name == "win32com.shell":
                raise ImportError
            return orig_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            with patch("wuttjamaican.conf.sys", platform="win32"):
                files = conf.generic_default_files("wuttatest")
                self.assertIsInstance(files, list)
                self.assertEqual(len(files), 0)


class TestGetConfigPaths(FileTestCase):
    def test_winsvc(self):
        myconf = self.write_file(
            "my.conf",
            """
[wutta.config]
winsvc.RattailFileMonitor = /path/to/other/file
""",
        )

        files = conf.get_config_paths(files=[myconf], winsvc="RattailFileMonitor")
        self.assertEqual(files, ["/path/to/other/file"])

    def test_nonexistent_default_files(self):
        files = conf.get_config_paths(
            files=None,
            env_files_name="IGNORE_THIS",
            default_files=["/this/does/not/exist"],
        )
        self.assertEqual(files, [])


class TestMakeConfig(FileTestCase):
    # nb. we use appname='wuttatest' in this suite to avoid any
    # "valid" default config files, env vars etc. which may be present
    # on the dev machine

    def test_generic_default_files(self):
        generic = self.write_file("generic.conf", "")

        with patch("wuttjamaican.conf.generic_default_files") as generic_default_files:
            with patch("wuttjamaican.conf.WuttaConfig") as WuttaConfig:
                # generic files are used if nothing is specified
                generic_default_files.return_value = [generic]
                config = conf.make_config(appname="wuttatest")
                generic_default_files.assert_called_once_with("wuttatest")
                WuttaConfig.assert_called_once_with(
                    [generic], appname="wuttatest", usedb=None, preferdb=None
                )

                # make sure empty defaults works too
                generic_default_files.reset_mock()
                generic_default_files.return_value = []
                WuttaConfig.reset_mock()
                config = conf.make_config(appname="wuttatest")
                generic_default_files.assert_called_once_with("wuttatest")
                WuttaConfig.assert_called_once_with(
                    [], appname="wuttatest", usedb=None, preferdb=None
                )

    def test_specify_default_files(self):
        generic = self.write_file("generic.conf", "")
        myfile = self.write_file("my.conf", "")

        with patch("wuttjamaican.conf.generic_default_files") as generic_default_files:
            with patch("wuttjamaican.conf.WuttaConfig") as WuttaConfig:
                # generic defaults are used if nothing specified
                generic_default_files.return_value = [generic]
                config = conf.make_config(appname="wuttatest")
                generic_default_files.assert_called_once_with("wuttatest")
                WuttaConfig.assert_called_once_with(
                    [generic], appname="wuttatest", usedb=None, preferdb=None
                )

                # can specify single default file
                generic_default_files.reset_mock()
                WuttaConfig.reset_mock()
                config = conf.make_config(appname="wuttatest", default_files=myfile)
                generic_default_files.assert_not_called()
                WuttaConfig.assert_called_once_with(
                    [myfile], appname="wuttatest", usedb=None, preferdb=None
                )

                # can specify default files as list
                generic_default_files.reset_mock()
                WuttaConfig.reset_mock()
                config = conf.make_config(appname="wuttatest", default_files=[myfile])
                generic_default_files.assert_not_called()
                WuttaConfig.assert_called_once_with(
                    [myfile], appname="wuttatest", usedb=None, preferdb=None
                )

                # can specify default files as callable
                generic_default_files.reset_mock()
                WuttaConfig.reset_mock()
                config = conf.make_config(
                    appname="wuttatest", default_files=lambda appname: [myfile]
                )
                generic_default_files.assert_not_called()
                WuttaConfig.assert_called_once_with(
                    [myfile], appname="wuttatest", usedb=None, preferdb=None
                )

    def test_specify_plus_files(self):
        generic = self.write_file("generic.conf", "")
        myfile = self.write_file("my.conf", "")

        with patch("wuttjamaican.conf.generic_default_files") as generic_default_files:
            with patch("wuttjamaican.conf.WuttaConfig") as WuttaConfig:
                generic_default_files.return_value = [generic]

                # no plus files by default
                config = conf.make_config(appname="wuttatest")
                generic_default_files.assert_called_once_with("wuttatest")
                WuttaConfig.assert_called_once_with(
                    [generic], appname="wuttatest", usedb=None, preferdb=None
                )

                # can specify single plus file
                generic_default_files.reset_mock()
                WuttaConfig.reset_mock()
                config = conf.make_config(appname="wuttatest", plus_files=myfile)
                generic_default_files.assert_called_once_with("wuttatest")
                WuttaConfig.assert_called_once_with(
                    [generic, myfile], appname="wuttatest", usedb=None, preferdb=None
                )

                # can specify plus files as list
                generic_default_files.reset_mock()
                WuttaConfig.reset_mock()
                config = conf.make_config(appname="wuttatest", plus_files=[myfile])
                generic_default_files.assert_called_once_with("wuttatest")
                WuttaConfig.assert_called_once_with(
                    [generic, myfile], appname="wuttatest", usedb=None, preferdb=None
                )

                # can specify plus files via env
                generic_default_files.reset_mock()
                WuttaConfig.reset_mock()
                config = conf.make_config(
                    appname="wuttatest", env={"WUTTATEST_CONFIG_PLUS_FILES": myfile}
                )
                generic_default_files.assert_called_once_with("wuttatest")
                WuttaConfig.assert_called_once_with(
                    [generic, myfile], appname="wuttatest", usedb=None, preferdb=None
                )

    def test_specify_primary_files(self):
        generic = self.write_file("generic.conf", "")
        myfile = self.write_file("my.conf", "")

        with patch("wuttjamaican.conf.generic_default_files") as generic_default_files:
            with patch("wuttjamaican.conf.WuttaConfig") as WuttaConfig:
                generic_default_files.return_value = [generic]

                # generic files by default
                config = conf.make_config(appname="wuttatest")
                generic_default_files.assert_called_once_with("wuttatest")
                WuttaConfig.assert_called_once_with(
                    [generic], appname="wuttatest", usedb=None, preferdb=None
                )

                # can specify single primary file (nb. no default files)
                generic_default_files.reset_mock()
                WuttaConfig.reset_mock()
                config = conf.make_config(myfile, appname="wuttatest")
                generic_default_files.assert_not_called()
                WuttaConfig.assert_called_once_with(
                    [myfile], appname="wuttatest", usedb=None, preferdb=None
                )

                # can specify primary files as list
                generic_default_files.reset_mock()
                WuttaConfig.reset_mock()
                config = conf.make_config([myfile], appname="wuttatest")
                generic_default_files.assert_not_called()
                WuttaConfig.assert_called_once_with(
                    [myfile], appname="wuttatest", usedb=None, preferdb=None
                )

                # can specify primary files via env
                generic_default_files.reset_mock()
                WuttaConfig.reset_mock()
                config = conf.make_config(
                    appname="wuttatest", env={"WUTTATEST_CONFIG_FILES": myfile}
                )
                generic_default_files.assert_not_called()
                WuttaConfig.assert_called_once_with(
                    [myfile], appname="wuttatest", usedb=None, preferdb=None
                )

    def test_extensions(self):
        generic = self.write_file("generic.conf", "")
        myfile = self.write_file("my.conf", "")

        with patch.object(mod, "WuttaConfig") as WuttaConfig:
            with patch.object(mod, "load_entry_points") as load_entry_points:
                # no entry points loaded if extend=False
                config = mod.make_config(appname="wuttatest", extend=False)
                WuttaConfig.assert_called_once_with(
                    [], appname="wuttatest", usedb=None, preferdb=None
                )
                load_entry_points.assert_not_called()

                # confirm entry points for default appname
                load_entry_points.reset_mock()
                WuttaConfig.reset_mock()
                config = mod.make_config([], appname="wutta")
                WuttaConfig.assert_called_once_with(
                    [], appname="wutta", usedb=None, preferdb=None
                )
                load_entry_points.assert_called_once_with("wutta.config.extensions")

                # confirm entry points for custom appname
                load_entry_points.reset_mock()
                WuttaConfig.reset_mock()
                config = mod.make_config(appname="wuttatest")
                WuttaConfig.assert_called_once_with(
                    [], appname="wuttatest", usedb=None, preferdb=None
                )
                load_entry_points.assert_called_once_with("wuttatest.config.extensions")

                # confirm extensions are invoked
                load_entry_points.reset_mock()
                foo_obj = MagicMock()
                foo_cls = MagicMock(return_value=foo_obj)
                load_entry_points.return_value = {"foo": foo_cls}
                WuttaConfig.reset_mock()
                testconfig = MagicMock()
                WuttaConfig.return_value = testconfig
                config = mod.make_config(appname="wuttatest")
                WuttaConfig.assert_called_once_with(
                    [], appname="wuttatest", usedb=None, preferdb=None
                )
                load_entry_points.assert_called_once_with("wuttatest.config.extensions")
                foo_cls.assert_called_once_with()
                foo_obj.configure.assert_called_once_with(testconfig)
                foo_obj.startup.assert_called_once_with(testconfig)


class TestWuttaConfigProfile(ConfigTestCase):
    def make_profile(self, key):
        return mod.WuttaConfigProfile(self.config, key)

    def test_section(self):
        profile = self.make_profile("default")
        self.assertRaises(NotImplementedError, getattr, profile, "section")

    def test_get_str(self):
        self.config.setdefault("wutta.telemetry.default.submit_url", "/nodes/telemetry")
        with patch.object(mod.WuttaConfigProfile, "section", new="wutta.telemetry"):
            profile = self.make_profile("default")
            self.assertEqual(profile.section, "wutta.telemetry")
            url = profile.get_str("submit_url")
            self.assertEqual(url, "/nodes/telemetry")
