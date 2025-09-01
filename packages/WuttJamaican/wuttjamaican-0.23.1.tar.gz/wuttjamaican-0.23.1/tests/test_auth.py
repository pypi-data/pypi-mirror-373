# -*- coding: utf-8; -*-

from unittest import TestCase

from wuttjamaican import auth as mod
from wuttjamaican.conf import WuttaConfig

try:
    import sqlalchemy as sa
except ImportError:
    pass
else:

    class TestAuthHandler(TestCase):

        def setUp(self):
            self.config = WuttaConfig()
            self.app = self.config.get_app()
            self.handler = self.make_handler()

            self.engine = sa.create_engine("sqlite://")
            self.app.model.Base.metadata.create_all(bind=self.engine)
            self.session = self.make_session()

        def tearDown(self):
            self.session.close()
            self.app.model.Base.metadata.drop_all(bind=self.engine)

        def make_session(self):
            return self.app.make_session(bind=self.engine)

        def make_handler(self):
            return mod.AuthHandler(self.config)

        def test_authenticate_user(self):
            model = self.app.model
            barney = model.User(username="barney")
            self.handler.set_user_password(barney, "goodpass")
            self.session.add(barney)
            self.session.commit()

            # login ok
            user = self.handler.authenticate_user(self.session, "barney", "goodpass")
            self.assertIs(user, barney)

            # can also pass user instead of username
            user = self.handler.authenticate_user(self.session, barney, "goodpass")
            self.assertIs(user, barney)

            # bad password
            user = self.handler.authenticate_user(self.session, "barney", "BADPASS")
            self.assertIsNone(user)

            # bad username
            user = self.handler.authenticate_user(self.session, "NOBODY", "goodpass")
            self.assertIsNone(user)

            # inactive user
            user = self.handler.authenticate_user(self.session, "barney", "goodpass")
            self.assertIs(user, barney)
            barney.active = False
            user = self.handler.authenticate_user(self.session, "barney", "goodpass")
            self.assertIsNone(user)

        def test_authenticate_user_token(self):
            model = self.app.model
            barney = model.User(username="barney")
            self.session.add(barney)
            token = self.handler.add_api_token(barney, "test token")
            self.session.commit()

            user = self.handler.authenticate_user_token(self.session, None)
            self.assertIsNone(user)

            user = self.handler.authenticate_user_token(
                self.session, token.token_string
            )
            self.assertIs(user, barney)

            barney.active = False
            self.session.flush()
            user = self.handler.authenticate_user_token(
                self.session, token.token_string
            )
            self.assertIsNone(user)

            barney.active = True
            self.session.flush()
            user = self.handler.authenticate_user_token(
                self.session, token.token_string
            )
            self.assertIs(user, barney)

            user = self.handler.authenticate_user_token(self.session, "bad-token")
            self.assertIsNone(user)

        def test_check_user_password(self):
            model = self.app.model
            barney = model.User(username="barney")
            self.handler.set_user_password(barney, "goodpass")
            self.session.add(barney)
            self.session.commit()

            # basics
            self.assertTrue(self.handler.check_user_password(barney, "goodpass"))
            self.assertFalse(self.handler.check_user_password(barney, "BADPASS"))

        def test_get_role(self):
            model = self.app.model
            myrole = model.Role(name="My Role")
            self.session.add(myrole)
            self.session.commit()

            # empty key is ignored
            role = self.handler.get_role(self.session, None)
            self.assertIsNone(role)

            # key may be uuid
            role = self.handler.get_role(self.session, myrole.uuid)
            self.assertIs(role, myrole)

            # key may be name
            role = self.handler.get_role(self.session, myrole.name)
            self.assertIs(role, myrole)

            # key may be represented within a setting
            self.config.usedb = True
            role = self.handler.get_role(self.session, "mykey")
            self.assertIsNone(role)
            setting = model.Setting(name="wutta.role.mykey", value=myrole.uuid.hex)
            self.session.add(setting)
            self.session.commit()
            role = self.handler.get_role(self.session, "mykey")
            self.assertIs(role, myrole)

        def test_get_user(self):
            model = self.app.model
            myuser = model.User(username="myuser")
            self.session.add(myuser)
            self.session.commit()

            # empty obj is ignored
            user = self.handler.get_user(None)
            self.assertIsNone(user)

            # user is returned as-is
            user = self.handler.get_user(myuser)
            self.assertIs(user, myuser)

            # match on User.uuid
            user = self.handler.get_user(myuser.uuid, session=self.session)
            self.assertIs(user, myuser)

            # match on User.uuid (str)
            user = self.handler.get_user(myuser.uuid.hex, session=self.session)
            self.assertIs(user, myuser)

            # match on User.username
            user = self.handler.get_user(myuser.username, session=self.session)
            self.assertIs(user, myuser)

            # find user from person
            myperson = model.Person(full_name="My Name")
            self.session.add(myperson)
            user.person = myperson
            self.session.commit()
            user = self.handler.get_user(myperson)
            self.assertIs(user, myuser)

        def test_make_person(self):
            model = self.app.model
            handler = self.handler

            person = handler.make_person()
            self.assertIsInstance(person, model.Person)
            self.assertIsNone(person.first_name)
            self.assertIsNone(person.last_name)
            self.assertIsNone(person.full_name)
            self.assertNotIn(person, self.session)

            person = handler.make_person(first_name="Barney", last_name="Rubble")
            self.assertIsInstance(person, model.Person)
            self.assertEqual(person.first_name, "Barney")
            self.assertEqual(person.last_name, "Rubble")
            self.assertEqual(person.full_name, "Barney Rubble")
            self.assertNotIn(person, self.session)

        def test_make_user(self):
            model = self.app.model

            # empty user
            user = self.handler.make_user()
            self.assertIsInstance(user, model.User)
            self.assertIsNone(user.username)

            # user is added to session
            user = self.handler.make_user(session=self.session)
            self.assertIn(user, self.session)
            self.session.rollback()
            self.assertNotIn(user, self.session)

            # default username
            # nb. this behavior requires a session
            user = self.handler.make_user(session=self.session)
            self.assertEqual(user.username, "newuser")

        def test_delete_user(self):
            model = self.app.model

            # basics
            myuser = model.User(username="myuser")
            self.session.add(myuser)
            self.session.commit()
            user = self.session.query(model.User).one()
            self.assertIs(user, myuser)
            self.handler.delete_user(user)
            self.session.commit()
            self.assertEqual(self.session.query(model.User).count(), 0)

        def test_make_preferred_username(self):
            model = self.app.model

            # default
            name = self.handler.make_preferred_username(self.session)
            self.assertEqual(name, "newuser")

            # person/first+last
            person = model.Person(first_name="Barney", last_name="Rubble")
            name = self.handler.make_preferred_username(self.session, person=person)
            self.assertEqual(name, "barney.rubble")

            # person/first
            person = model.Person(first_name="Barney")
            name = self.handler.make_preferred_username(self.session, person=person)
            self.assertEqual(name, "barney")

            # person/last
            person = model.Person(last_name="Rubble")
            name = self.handler.make_preferred_username(self.session, person=person)
            self.assertEqual(name, "rubble")

        def test_make_unique_username(self):
            model = self.app.model

            # default
            name = self.handler.make_unique_username(self.session)
            self.assertEqual(name, "newuser")
            user = model.User(username=name)
            self.session.add(user)
            self.session.commit()

            # counter invoked if name exists
            name = self.handler.make_unique_username(self.session)
            self.assertEqual(name, "newuser01")
            user = model.User(username=name)
            self.session.add(user)
            self.session.commit()

            # starts by getting preferred name
            person = model.Person(first_name="Barney", last_name="Rubble")
            name = self.handler.make_unique_username(self.session, person=person)
            self.assertEqual(name, "barney.rubble")
            user = model.User(username=name)
            self.session.add(user)
            self.session.commit()

            # counter invoked if name exists
            name = self.handler.make_unique_username(self.session, person=person)
            self.assertEqual(name, "barney.rubble01")

        def test_set_user_password(self):
            model = self.app.model
            myuser = model.User(username="myuser")
            self.session.add(myuser)

            # basics
            self.assertIsNone(myuser.password)
            self.handler.set_user_password(myuser, "goodpass")
            self.session.commit()
            self.assertIsNotNone(myuser.password)
            # nb. password is hashed
            self.assertNotEqual(myuser.password, "goodpass")

            # confirm login works with new password
            user = self.handler.authenticate_user(self.session, "myuser", "goodpass")
            self.assertIs(user, myuser)

        def test_get_role_administrator(self):
            model = self.app.model

            self.assertEqual(self.session.query(model.Role).count(), 0)
            role = self.handler.get_role_administrator(self.session)
            self.assertEqual(self.session.query(model.Role).count(), 1)
            self.assertEqual(role.name, "Administrator")

        def test_get_role_anonymous(self):
            model = self.app.model

            self.assertEqual(self.session.query(model.Role).count(), 0)
            role = self.handler.get_role_anonymous(self.session)
            self.assertEqual(self.session.query(model.Role).count(), 1)
            self.assertEqual(role.name, "Anonymous")

        def test_get_role_authenticated(self):
            model = self.app.model

            self.assertEqual(self.session.query(model.Role).count(), 0)
            role = self.handler.get_role_authenticated(self.session)
            self.assertEqual(self.session.query(model.Role).count(), 1)
            self.assertEqual(role.name, "Authenticated")

        def test_user_is_admin(self):
            model = self.app.model

            # non-user is not admin
            self.assertFalse(self.handler.user_is_admin(None))

            # new user but not yet admin
            user = self.handler.make_user(session=self.session)
            self.session.commit()
            self.assertFalse(self.handler.user_is_admin(user))

            # but we can make them an admin
            admin = self.handler.get_role_administrator(self.session)
            user.roles.append(admin)
            self.session.commit()
            self.assertTrue(self.handler.user_is_admin(user))

        def test_get_permissions(self):
            model = self.app.model

            # empty default for role
            role = model.Role()
            perms = self.handler.get_permissions(self.session, role)
            self.assertIsInstance(perms, set)
            self.assertEqual(len(perms), 0)

            # empty default for user
            user = model.User()
            perms = self.handler.get_permissions(self.session, user)
            self.assertIsInstance(perms, set)
            self.assertEqual(len(perms), 0)

            # role perms
            myrole = model.Role(name="My Role")
            self.session.add(myrole)
            self.handler.grant_permission(myrole, "foo")
            self.session.commit()
            perms = self.handler.get_permissions(self.session, myrole)
            self.assertEqual(perms, {"foo"})

            # user perms
            myuser = model.User(username="myuser")
            self.session.add(myuser)
            self.session.commit()
            perms = self.handler.get_permissions(self.session, myuser)
            self.assertEqual(len(perms), 0)
            myuser.roles.append(myrole)
            self.session.commit()
            perms = self.handler.get_permissions(self.session, myuser)
            self.assertEqual(perms, {"foo"})

            # invalid principal
            perms = self.handler.get_permissions(self.session, RuntimeError)
            self.assertEqual(perms, set())

            # missing principal
            perms = self.handler.get_permissions(self.session, None)
            self.assertEqual(perms, set())

        def test_has_permission(self):
            model = self.app.model

            # false default for role
            role = model.Role()
            self.assertFalse(self.handler.has_permission(self.session, role, "foo"))

            # empty default for user
            user = model.User()
            self.assertFalse(self.handler.has_permission(self.session, user, "foo"))

            # role perms
            myrole = model.Role(name="My Role")
            self.session.add(myrole)
            self.session.commit()
            self.assertFalse(self.handler.has_permission(self.session, myrole, "foo"))
            self.handler.grant_permission(myrole, "foo")
            self.session.commit()
            self.assertTrue(self.handler.has_permission(self.session, myrole, "foo"))

            # user perms
            myuser = model.User(username="myuser")
            self.session.add(myuser)
            self.session.commit()
            self.assertFalse(self.handler.has_permission(self.session, myuser, "foo"))
            myuser.roles.append(myrole)
            self.session.commit()
            self.assertTrue(self.handler.has_permission(self.session, myuser, "foo"))

            # invalid principal
            self.assertFalse(
                self.handler.has_permission(self.session, RuntimeError, "foo")
            )

            # missing principal
            self.assertFalse(self.handler.has_permission(self.session, None, "foo"))

        def test_grant_permission(self):
            model = self.app.model
            myrole = model.Role(name="My Role")
            self.session.add(myrole)
            self.session.commit()

            # no perms yet
            self.assertEqual(self.session.query(model.Permission).count(), 0)

            # grant one perm, and confirm
            self.handler.grant_permission(myrole, "foo")
            self.session.commit()
            self.assertEqual(self.session.query(model.Permission).count(), 1)
            perm = self.session.query(model.Permission).one()
            self.assertIs(perm.role, myrole)
            self.assertEqual(perm.permission, "foo")

            # grant same perm again, confirm just one exists
            self.handler.grant_permission(myrole, "foo")
            self.session.commit()
            self.assertEqual(self.session.query(model.Permission).count(), 1)
            perm = self.session.query(model.Permission).one()
            self.assertIs(perm.role, myrole)
            self.assertEqual(perm.permission, "foo")

        def test_revoke_permission(self):
            model = self.app.model
            myrole = model.Role(name="My Role")
            self.session.add(myrole)
            self.handler.grant_permission(myrole, "foo")
            self.session.commit()

            # just the one perm
            self.assertEqual(self.session.query(model.Permission).count(), 1)

            # revoke it, then confirm
            self.handler.revoke_permission(myrole, "foo")
            self.session.commit()
            self.assertEqual(self.session.query(model.Permission).count(), 0)

            # revoke again, confirm
            self.handler.revoke_permission(myrole, "foo")
            self.session.commit()
            self.assertEqual(self.session.query(model.Permission).count(), 0)

        def test_generate_api_token_string(self):
            token = self.handler.generate_api_token_string()
            # TODO: not sure how to propertly test this yet...
            self.assertEqual(len(token), 43)

        def test_add_api_token(self):
            model = self.app.model
            barney = model.User(username="barney")
            self.session.add(barney)

            token = self.handler.add_api_token(barney, "test token")
            self.assertIs(token.user, barney)
            self.assertEqual(token.description, "test token")
            # TODO: not sure how to propertly test this yet...
            self.assertEqual(len(token.token_string), 43)

        def test_delete_api_token(self):
            model = self.app.model
            barney = model.User(username="barney")
            self.session.add(barney)
            token = self.handler.add_api_token(barney, "test token")
            self.session.commit()

            self.session.refresh(barney)
            self.assertEqual(len(barney.api_tokens), 1)
            self.handler.delete_api_token(token)
            self.session.refresh(barney)
            self.assertEqual(len(barney.api_tokens), 0)
