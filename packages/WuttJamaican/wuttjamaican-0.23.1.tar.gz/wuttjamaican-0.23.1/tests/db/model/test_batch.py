# -*- coding: utf-8; -*-

import uuid as _uuid

from wuttjamaican.testing import DataTestCase

try:
    import sqlalchemy as sa
    from wuttjamaican.db import model
    from wuttjamaican.db.model import batch as mod
except ImportError:
    pass
else:

    class TestBatchMixin(DataTestCase):

        def test_basic(self):

            class MyBatch(mod.BatchMixin, model.Base):
                __tablename__ = "testing_mybatch"

            model.Base.metadata.create_all(bind=self.session.bind)
            metadata = sa.MetaData()
            metadata.reflect(self.session.bind)
            self.assertIn("testing_mybatch", metadata.tables)

            batch = MyBatch(
                id=42, uuid=_uuid.UUID("0675cdac-ffc9-7690-8000-6023de1c8cfd")
            )
            self.assertEqual(
                repr(batch),
                "MyBatch(uuid=UUID('0675cdac-ffc9-7690-8000-6023de1c8cfd'))",
            )
            self.assertEqual(str(batch), "00000042")
            self.assertEqual(batch.id_str, "00000042")

            batch2 = MyBatch()
            self.assertIsNone(batch2.id_str)

    class TestBatchRowMixin(DataTestCase):

        def test_basic(self):

            class MyBatch2(mod.BatchMixin, model.Base):
                __tablename__ = "testing_mybatch2"

            class MyBatchRow2(mod.BatchRowMixin, model.Base):
                __tablename__ = "testing_mybatch_row2"
                __batch_class__ = MyBatch2

            model.Base.metadata.create_all(bind=self.session.bind)
            metadata = sa.MetaData()
            metadata.reflect(self.session.bind)
            self.assertIn("testing_mybatch2", metadata.tables)
            self.assertIn("testing_mybatch_row2", metadata.tables)

            # nb. this gives coverage but doesn't really test much
            batch = MyBatch2(
                id=42, uuid=_uuid.UUID("0675cdac-ffc9-7690-8000-6023de1c8cfd")
            )
            row = MyBatchRow2()
            batch.rows.append(row)
