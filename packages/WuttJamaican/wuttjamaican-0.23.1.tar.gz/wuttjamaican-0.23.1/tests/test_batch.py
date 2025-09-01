# -*- coding: utf-8; -*-

import os
from unittest.mock import patch

from wuttjamaican import batch as mod

try:
    import sqlalchemy as sa
    from wuttjamaican.db import model
    from wuttjamaican.testing import DataTestCase
except ImportError:
    pass
else:

    class MockBatch(model.BatchMixin, model.Base):
        __tablename__ = "testing_batch_mock"

    class MockBatchRow(model.BatchRowMixin, model.Base):
        __tablename__ = "testing_batch_mock_row"
        __batch_class__ = MockBatch

    class MockBatchHandler(mod.BatchHandler):
        model_class = MockBatch

    class TestBatchHandler(DataTestCase):

        def make_handler(self, **kwargs):
            return MockBatchHandler(self.config, **kwargs)

        def test_model_class(self):
            handler = mod.BatchHandler(self.config)
            self.assertRaises(NotImplementedError, getattr, handler, "model_class")

        def test_batch_type(self):
            with patch.object(mod.BatchHandler, "model_class", new=MockBatch):
                handler = mod.BatchHandler(self.config)
                self.assertEqual(handler.batch_type, "testing_batch_mock")

        def test_make_batch(self):
            handler = self.make_handler()
            batch = handler.make_batch(self.session)
            self.assertIsInstance(batch, MockBatch)

        def test_consume_batch_id(self):
            handler = self.make_handler()

            first = handler.consume_batch_id(self.session)
            second = handler.consume_batch_id(self.session)
            self.assertEqual(second, first + 1)

            third = handler.consume_batch_id(self.session, as_str=True)
            self.assertEqual(third, f"{first + 2:08d}")

        def test_get_data_path(self):
            model = self.app.model
            user = model.User(username="barney")
            self.session.add(user)

            with patch.object(mod.BatchHandler, "model_class", new=MockBatch):
                handler = self.make_handler()

                # root storage (default)
                with patch.object(self.app, "get_appdir", return_value=self.tempdir):
                    path = handler.get_data_path()
                    self.assertEqual(
                        path,
                        os.path.join(
                            self.tempdir, "data", "batch", "testing_batch_mock"
                        ),
                    )

                # root storage (configured)
                self.config.setdefault("wutta.batch.storage_path", self.tempdir)
                path = handler.get_data_path()
                self.assertEqual(path, os.path.join(self.tempdir, "testing_batch_mock"))

                batch = handler.make_batch(self.session, created_by=user)
                self.session.add(batch)
                self.session.flush()

                # batch-specific
                path = handler.get_data_path(batch)
                uuid = batch.uuid.hex
                final = os.path.join(uuid[-2:], uuid[:-2])
                self.assertEqual(
                    path, os.path.join(self.tempdir, "testing_batch_mock", final)
                )

                # with filename
                path = handler.get_data_path(batch, "input.csv")
                self.assertEqual(
                    path,
                    os.path.join(
                        self.tempdir, "testing_batch_mock", final, "input.csv"
                    ),
                )

                # makedirs
                path = handler.get_data_path(batch)
                self.assertFalse(os.path.exists(path))
                path = handler.get_data_path(batch, makedirs=True)
                self.assertTrue(os.path.exists(path))

        def test_should_populate(self):
            handler = self.make_handler()
            batch = handler.make_batch(self.session)
            self.assertFalse(handler.should_populate(batch))

        def test_do_populate(self):
            handler = self.make_handler()
            batch = handler.make_batch(self.session)
            # nb. coverage only; tests nothing
            handler.do_populate(batch)

        def test_make_row(self):
            handler = self.make_handler()
            row = handler.make_row()
            self.assertIsInstance(row, MockBatchRow)

        def test_add_row(self):
            handler = self.make_handler()
            batch = handler.make_batch(self.session)
            self.session.add(batch)
            row = handler.make_row()
            self.assertIsNone(batch.row_count)
            handler.add_row(batch, row)
            self.assertEqual(batch.row_count, 1)

        def test_remove_row(self):
            model = self.app.model
            handler = self.make_handler()
            user = model.User(username="barney")
            self.session.add(user)
            batch = handler.make_batch(self.session, created_by=user)
            self.session.add(batch)
            row = handler.make_row()
            handler.add_row(batch, row)
            self.session.flush()
            self.assertEqual(batch.row_count, 1)
            handler.do_remove_row(row)
            self.session.flush()
            self.assertEqual(batch.row_count, 0)

        def test_get_effective_rows(self):
            model = self.app.model
            handler = self.make_handler()

            user = model.User(username="barney")
            self.session.add(user)
            batch = handler.make_batch(self.session, created_by=user)
            self.session.add(batch)
            self.session.flush()

            self.assertEqual(handler.get_effective_rows(batch), [])

            row = handler.make_row()
            handler.add_row(batch, row)
            self.session.flush()

            rows = handler.get_effective_rows(batch)
            self.assertEqual(len(rows), 1)
            self.assertIs(rows[0], row)

        def test_do_execute(self):
            model = self.app.model
            user = model.User(username="barney")
            self.session.add(user)

            handler = self.make_handler()
            batch = handler.make_batch(self.session, created_by=user)
            self.session.add(batch)
            self.session.flush()

            # error if execution not allowed
            with patch.object(handler, "why_not_execute", return_value="bad batch"):
                self.assertRaises(RuntimeError, handler.do_execute, batch, user)

            # nb. coverage only; tests nothing
            self.assertIsNone(batch.executed)
            self.assertIsNone(batch.executed_by)
            handler.do_execute(batch, user)
            self.assertIsNotNone(batch.executed)
            self.assertIs(batch.executed_by, user)

            # error if execution already happened
            self.assertRaises(ValueError, handler.do_execute, batch, user)

        def test_do_delete(self):
            model = self.app.model
            handler = self.make_handler()

            user = model.User(username="barney")
            self.session.add(user)

            # simple delete
            batch = handler.make_batch(self.session, created_by=user)
            self.session.add(batch)
            self.session.flush()
            self.assertEqual(self.session.query(MockBatch).count(), 1)
            handler.do_delete(batch, user)
            self.assertEqual(self.session.query(MockBatch).count(), 0)

            # delete w/ rows
            batch = handler.make_batch(self.session, created_by=user)
            self.session.add(batch)
            for i in range(5):
                row = handler.make_row()
                handler.add_row(batch, row)
            self.session.flush()
            self.assertEqual(self.session.query(MockBatch).count(), 1)
            handler.do_delete(batch, user)
            self.assertEqual(self.session.query(MockBatch).count(), 0)

            # delete w/ files
            self.config.setdefault("wutta.batch.storage_path", self.tempdir)
            batch = handler.make_batch(self.session, created_by=user)
            self.session.add(batch)
            self.session.flush()
            path = handler.get_data_path(batch, "data.txt", makedirs=True)
            with open(path, "wt") as f:
                f.write("foo=bar")
            self.assertEqual(self.session.query(MockBatch).count(), 1)
            path = handler.get_data_path(batch)
            self.assertTrue(os.path.exists(path))
            handler.do_delete(batch, user)
            self.assertEqual(self.session.query(MockBatch).count(), 0)
            self.assertFalse(os.path.exists(path))

            # delete w/ files (dry-run)
            self.config.setdefault("wutta.batch.storage_path", self.tempdir)
            batch = handler.make_batch(self.session, created_by=user)
            self.session.add(batch)
            self.session.flush()
            path = handler.get_data_path(batch, "data.txt", makedirs=True)
            with open(path, "wt") as f:
                f.write("foo=bar")
            self.assertEqual(self.session.query(MockBatch).count(), 1)
            path = handler.get_data_path(batch)
            self.assertTrue(os.path.exists(path))
            handler.do_delete(batch, user, dry_run=True)
            # nb. batch appears missing from session even in dry-run
            self.assertEqual(self.session.query(MockBatch).count(), 0)
            # nb. but its files remain intact
            self.assertTrue(os.path.exists(path))
