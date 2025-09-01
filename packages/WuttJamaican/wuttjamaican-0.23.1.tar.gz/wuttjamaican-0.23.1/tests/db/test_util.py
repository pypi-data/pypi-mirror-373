# -*- coding: utf-8; -*-

import uuid as _uuid
from unittest import TestCase
from unittest.mock import MagicMock


try:
    import sqlalchemy as sa
    from sqlalchemy.dialects.postgresql import UUID as PGUUID
    from wuttjamaican.db import util as mod
    from wuttjamaican.db.model.base import Setting
    from wuttjamaican.util import make_true_uuid
    from wuttjamaican.testing import DataTestCase
except ImportError:
    pass
else:

    class TestModelBase(TestCase):

        def test_dict_behavior(self):
            setting = Setting()
            self.assertEqual(list(iter(setting)), [("name", None), ("value", None)])
            self.assertIsNone(setting.name)
            self.assertIsNone(setting["name"])
            setting.name = "foo"
            self.assertEqual(setting["name"], "foo")
            self.assertRaises(KeyError, lambda: setting["notfound"])

    class TestUUID(TestCase):

        def test_load_dialect_impl(self):
            typ = mod.UUID()
            dialect = MagicMock()

            # TODO: this doesn't really test anything, but gives us
            # coverage at least..

            # postgres
            dialect.name = "postgresql"
            dialect.type_descriptor.return_value = 42
            result = typ.load_dialect_impl(dialect)
            self.assertTrue(dialect.type_descriptor.called)
            self.assertEqual(result, 42)

            # other
            dialect.name = "mysql"
            dialect.type_descriptor.return_value = 43
            dialect.type_descriptor.reset_mock()
            result = typ.load_dialect_impl(dialect)
            self.assertTrue(dialect.type_descriptor.called)
            self.assertEqual(result, 43)

        def test_process_bind_param_postgres(self):
            typ = mod.UUID()
            dialect = MagicMock()
            dialect.name = "postgresql"

            # null
            result = typ.process_bind_param(None, dialect)
            self.assertIsNone(result)

            # string
            uuid_str = make_true_uuid().hex
            result = typ.process_bind_param(uuid_str, dialect)
            self.assertEqual(result, uuid_str)

            # uuid
            uuid_true = make_true_uuid()
            result = typ.process_bind_param(uuid_true, dialect)
            self.assertEqual(result, str(uuid_true))

        def test_process_bind_param_other(self):
            typ = mod.UUID()
            dialect = MagicMock()
            dialect.name = "mysql"

            # null
            result = typ.process_bind_param(None, dialect)
            self.assertIsNone(result)

            # string
            uuid_str = make_true_uuid().hex
            result = typ.process_bind_param(uuid_str, dialect)
            self.assertEqual(result, uuid_str)

            # uuid
            uuid_true = make_true_uuid()
            result = typ.process_bind_param(uuid_true, dialect)
            self.assertEqual(result, uuid_true.hex)

        def test_process_result_value(self):
            typ = mod.UUID()
            dialect = MagicMock()

            # null
            result = typ.process_result_value(None, dialect)
            self.assertIsNone(result)

            # string
            uuid_str = make_true_uuid().hex
            result = typ.process_result_value(uuid_str, dialect)
            self.assertIsInstance(result, _uuid.UUID)
            self.assertEqual(result.hex, uuid_str)

            # uuid
            uuid_true = make_true_uuid()
            result = typ.process_result_value(uuid_true, dialect)
            self.assertIs(result, uuid_true)

    class TestUUIDColumn(TestCase):

        def test_basic(self):
            column = mod.uuid_column()
            self.assertIsInstance(column, sa.Column)
            self.assertIsInstance(column.type, mod.UUID)

    class TestUUIDFKColumn(TestCase):

        def test_basic(self):
            column = mod.uuid_fk_column("foo.bar")
            self.assertIsInstance(column, sa.Column)
            self.assertIsInstance(column.type, mod.UUID)

    class TestMakeTopoSortkey(DataTestCase):

        def test_basic(self):
            model = self.app.model
            sortkey = mod.make_topo_sortkey(model)
            original = ["User", "Person", "UserRole", "Role"]

            # models are sorted so dependants come later
            result = sorted(original, key=sortkey)
            self.assertTrue(result.index("Role") < result.index("UserRole"))
            self.assertTrue(result.index("User") < result.index("UserRole"))
            self.assertTrue(result.index("Person") < result.index("User"))
