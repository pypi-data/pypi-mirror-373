# -*- coding: utf-8; -*-

from unittest.mock import patch, MagicMock

from wuttjamaican.testing import DataTestCase

try:
    import sqlalchemy as sa
    from wuttjamaican.db import handler as mod
except ImportError:
    pass
else:

    class TestDatabaseHandler(DataTestCase):

        def make_handler(self, **kwargs):
            return mod.DatabaseHandler(self.config, **kwargs)

        def test_next_counter_value_sqlite(self):
            handler = self.make_handler()

            # counter table should not exist yet
            metadata = sa.MetaData()
            metadata.reflect(self.session.bind)
            self.assertNotIn("_counter_testing", metadata.tables)

            # using sqlite as backend, should make table for counter
            value = handler.next_counter_value(self.session, "testing")
            self.assertEqual(value, 1)

            # counter table should exist now
            metadata.reflect(self.session.bind)
            self.assertIn("_counter_testing", metadata.tables)

            # counter increments okay
            value = handler.next_counter_value(self.session, "testing")
            self.assertEqual(value, 2)
            value = handler.next_counter_value(self.session, "testing")
            self.assertEqual(value, 3)

        def test_next_counter_value_postgres(self):
            handler = self.make_handler()

            # counter table should not exist
            metadata = sa.MetaData()
            metadata.reflect(self.session.bind)
            self.assertNotIn("_counter_testing", metadata.tables)

            # nb. we have to pretty much mock this out, can't really
            # test true sequence behavior for postgres since tests are
            # using sqlite backend.

            # using postgres as backend, should use "sequence"
            with patch.object(handler, "get_dialect", return_value="postgresql"):
                with patch.object(self.session, "execute") as execute:
                    execute.return_value.scalar.return_value = 1
                    value = handler.next_counter_value(self.session, "testing")
                    self.assertEqual(value, 1)
                    execute.return_value.scalar.assert_called_once_with()

            # counter table should still not exist
            metadata.reflect(self.session.bind)
            self.assertNotIn("_counter_testing", metadata.tables)
