# -*- coding: utf-8; -*-

from unittest import TestCase

try:
    import sqlalchemy as sa
    from sqlalchemy import orm
    from wuttjamaican.db.model import base as mod
    from wuttjamaican.db.model.auth import User
except ImportError:
    pass
else:

    class MockUser(mod.Base):
        __tablename__ = "mock_user"
        uuid = mod.uuid_column(sa.ForeignKey("user.uuid"), default=False)
        user = orm.relationship(
            User,
            backref=orm.backref("_mock", uselist=False, cascade="all, delete-orphan"),
        )
        favorite_color = sa.Column(sa.String(length=100), nullable=False)

    class TestWuttaModelBase(TestCase):

        def test_make_proxy(self):
            self.assertFalse(hasattr(User, "favorite_color"))
            MockUser.make_proxy(User, "_mock", "favorite_color")
            self.assertTrue(hasattr(User, "favorite_color"))
            user = User(favorite_color="green")
            self.assertEqual(user.favorite_color, "green")

    class TestSetting(TestCase):

        def test_basic(self):
            setting = mod.Setting()
            self.assertEqual(str(setting), "")
            setting.name = "foo"
            self.assertEqual(str(setting), "foo")

    class TestPerson(TestCase):

        def test_basic(self):
            person = mod.Person()
            self.assertEqual(str(person), "")
            person.full_name = "Barney Rubble"
            self.assertEqual(str(person), "Barney Rubble")

        def test_users(self):
            person = mod.Person()
            self.assertIsNone(person.user)

            user = User()
            person.users.append(user)
            self.assertIs(person.user, user)
