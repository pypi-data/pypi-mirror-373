# -*- coding: utf-8; -*-

from unittest import TestCase

try:
    import sqlalchemy as sa
    from wuttjamaican.db.model import auth as model
    from wuttjamaican.db.model.base import Person
except ImportError:
    pass
else:

    class TestRole(TestCase):

        def test_basic(self):
            role = model.Role()
            self.assertEqual(str(role), "")
            role.name = "Managers"
            self.assertEqual(str(role), "Managers")

    class TestPermission(TestCase):

        def test_basic(self):
            perm = model.Permission()
            self.assertEqual(str(perm), "")
            perm.permission = "users.create"
            self.assertEqual(str(perm), "users.create")

    class TestUser(TestCase):

        def test_str(self):
            user = model.User()
            self.assertEqual(str(user), "")
            user.username = "barney"
            self.assertEqual(str(user), "barney")

        def test_str_with_person(self):
            user = model.User()
            self.assertEqual(str(user), "")

            person = Person(full_name="Barney Rubble")
            user.person = person
            self.assertEqual(str(user), "Barney Rubble")

    class TestUserAPIToken(TestCase):

        def test_str(self):
            token = model.UserAPIToken()
            self.assertEqual(str(token), "")
            token.description = "test token"
            self.assertEqual(str(token), "test token")
