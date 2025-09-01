# -*- coding: utf-8; -*-

from unittest import TestCase
from unittest.mock import MagicMock

from wuttjamaican.conf import WuttaConfig

try:
    import sqlalchemy as sa
    from sqlalchemy import orm
    from wuttjamaican.db import sess
except ImportError:
    pass
else:

    class TestShortSession(TestCase):

        def test_none(self):
            with sess.short_session() as s:
                self.assertIsInstance(s, sess.Session.class_)

        def test_factory(self):
            TestSession = orm.sessionmaker()
            with sess.short_session(factory=TestSession) as s:
                self.assertIsInstance(s, TestSession.class_)

        def test_instance(self):
            # nb. nothing really happens if we provide the session instance
            session = MagicMock()
            with sess.short_session(session=session) as s:
                pass
            session.commit.assert_not_called()
            session.close.assert_not_called()

        def test_config(self):
            config = MagicMock()
            TestSession = orm.sessionmaker()
            config.get_app.return_value.make_session = TestSession
            # nb. config may be first arg (or kwarg)
            with sess.short_session(config) as s:
                self.assertIsInstance(s, TestSession.class_)

        def test_without_commit(self):
            session = MagicMock()
            TestSession = MagicMock(return_value=session)
            with sess.short_session(factory=TestSession, commit=False) as s:
                pass
            session.commit.assert_not_called()
            session.close.assert_called_once_with()

        def test_with_commit(self):
            session = MagicMock()
            TestSession = MagicMock(return_value=session)
            with sess.short_session(factory=TestSession, commit=True) as s:
                pass
            session.commit.assert_called_once_with()
            session.close.assert_called_once_with()
