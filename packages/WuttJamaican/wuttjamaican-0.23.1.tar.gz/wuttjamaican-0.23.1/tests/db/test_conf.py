# -*- coding: utf-8; -*-

import os
import shutil
import tempfile
from unittest import TestCase

from wuttjamaican.conf import WuttaConfig

try:
    import sqlalchemy as sa
    from sqlalchemy import orm
    from sqlalchemy.engine import Engine
    from sqlalchemy.pool import NullPool
    from wuttjamaican.db import conf
except ImportError:
    pass
else:

    class TestGetEngines(TestCase):

        def setUp(self):
            self.tempdir = tempfile.mkdtemp()

        def tearDown(self):
            shutil.rmtree(self.tempdir)

        def write_file(self, filename, content):
            path = os.path.join(self.tempdir, filename)
            with open(path, "wt") as f:
                f.write(content)
            return path

        def test_no_default(self):
            myfile = self.write_file("my.conf", "")
            config = WuttaConfig([myfile])
            self.assertEqual(conf.get_engines(config, "wuttadb"), {})

        def test_default(self):
            myfile = self.write_file(
                "my.conf",
                """\
    [wuttadb]
    default.url = sqlite://
    """,
            )
            config = WuttaConfig([myfile])
            result = conf.get_engines(config, "wuttadb")
            self.assertEqual(len(result), 1)
            self.assertIn("default", result)
            engine = result["default"]
            self.assertEqual(engine.dialect.name, "sqlite")

        def test_default_fallback(self):
            myfile = self.write_file(
                "my.conf",
                """\
    [wuttadb]
    sqlalchemy.url = sqlite://
    """,
            )
            config = WuttaConfig([myfile])
            result = conf.get_engines(config, "wuttadb")
            self.assertEqual(len(result), 1)
            self.assertIn("default", result)
            engine = result["default"]
            self.assertEqual(engine.dialect.name, "sqlite")

        def test_other(self):
            myfile = self.write_file(
                "my.conf",
                """\
    [otherdb]
    keys = first, second
    first.url = sqlite://
    second.url = sqlite://
    """,
            )
            config = WuttaConfig([myfile])
            result = conf.get_engines(config, "otherdb")
            self.assertEqual(len(result), 2)
            self.assertIn("first", result)
            self.assertIn("second", result)

    class TestGetSetting(TestCase):

        def setUp(self):
            Session = orm.sessionmaker()
            engine = sa.create_engine("sqlite://")
            self.session = Session(bind=engine)
            self.session.execute(
                sa.text(
                    """
            create table setting (
                    name varchar(255) primary key,
                    value text
            );
            """
                )
            )

        def tearDown(self):
            self.session.close()

        def test_basic_value(self):
            self.session.execute(sa.text("insert into setting values ('foo', 'bar');"))
            value = conf.get_setting(self.session, "foo")
            self.assertEqual(value, "bar")

        def test_missing_value(self):
            value = conf.get_setting(self.session, "foo")
            self.assertIsNone(value)

    class TestMakeEngineFromConfig(TestCase):

        def test_basic(self):
            engine = conf.make_engine_from_config(
                {
                    "sqlalchemy.url": "sqlite://",
                }
            )
            self.assertIsInstance(engine, Engine)

        def test_poolclass(self):

            engine = conf.make_engine_from_config(
                {
                    "sqlalchemy.url": "sqlite://",
                }
            )
            self.assertNotIsInstance(engine.pool, NullPool)

            engine = conf.make_engine_from_config(
                {
                    "sqlalchemy.url": "sqlite://",
                    "sqlalchemy.poolclass": "sqlalchemy.pool:NullPool",
                }
            )
            self.assertIsInstance(engine.pool, NullPool)

        def test_pool_pre_ping(self):

            engine = conf.make_engine_from_config(
                {
                    "sqlalchemy.url": "sqlite://",
                }
            )
            self.assertFalse(engine.pool._pre_ping)

            engine = conf.make_engine_from_config(
                {
                    "sqlalchemy.url": "sqlite://",
                    "sqlalchemy.pool_pre_ping": "true",
                }
            )
            self.assertTrue(engine.pool._pre_ping)
