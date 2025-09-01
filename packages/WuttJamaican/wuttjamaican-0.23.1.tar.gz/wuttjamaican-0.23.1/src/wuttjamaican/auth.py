# -*- coding: utf-8; -*-
################################################################################
#
#  WuttJamaican -- Base package for Wutta Framework
#  Copyright © 2023-2025 Lance Edgar
#
#  This file is part of Wutta Framework.
#
#  Wutta Framework is free software: you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option) any
#  later version.
#
#  Wutta Framework is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#
#  You should have received a copy of the GNU General Public License along with
#  Wutta Framework.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Auth Handler

This defines the default :term:`auth handler`.
"""

import secrets
import uuid as _uuid

from wuttjamaican.app import GenericHandler


# nb. this only works if passlib is installed (part of 'db' extra)
try:
    from passlib.context import CryptContext
except ImportError:  # pragma: no cover
    pass
else:
    password_context = CryptContext(schemes=["bcrypt"])


class AuthHandler(GenericHandler):  # pylint: disable=too-many-public-methods
    """
    Base class and default implementation for the :term:`auth
    handler`.

    This is responsible for "authentication and authorization" - for
    instance:

    * authenticate user from login credentials
    * check which permissions a user/role has
    * create/modify users, roles
    * grant/revoke role permissions
    """

    def authenticate_user(self, session, username, password):
        """
        Authenticate the given user credentials, and if successful,
        return the :class:`~wuttjamaican.db.model.auth.User`.

        Default logic will (try to) locate a user with matching
        username, then confirm the supplied password is also a match.

        Custom handlers can authenticate against anything else, using
        the given credentials.  But they still must return a "native"
        ``User`` object for the app to consider the authentication
        successful.  The handler may auto-create the user if needed.

        Generally speaking the credentials will have come directly
        from a user login attempt in the web app etc.  Again the
        default logic assumes a "username" but in practice it may be
        an email address etc. - whatever the user entered.

        See also :meth:`authenticate_user_token()`.

        :param session: Open :term:`db session`.

        :param username: Usually a string, but also may be a
           :class:`~wuttjamaican.db.model.auth.User` instance, in
           which case no user lookup will occur.  (However the user is
           still authenticated otherwise, i.e. the password must be
           correct etc.)

        :param password: Password as string.

        :returns: :class:`~wuttjamaican.db.model.auth.User` instance,
           or ``None``.
        """
        user = self.get_user(username, session=session)
        if user and user.active and user.password:
            if self.check_user_password(user, password):
                return user
        return None

    def authenticate_user_token(self, session, token):
        """
        Authenticate the given user API token string, and if valid,
        return the corresponding user.

        See also :meth:`authenticate_user()`.

        :param session: Open :term:`db session`.

        :param token: Raw token string for the user.

        :returns: :class:`~wuttjamaican.db.model.auth.User` instance,
           or ``None``.
        """
        from sqlalchemy import orm  # pylint: disable=import-outside-toplevel

        model = self.app.model

        try:
            token = (
                session.query(model.UserAPIToken)
                .filter(model.UserAPIToken.token_string == token)
                .one()
            )
        except orm.exc.NoResultFound:
            pass
        else:
            user = token.user
            if user.active:
                return user
        return None

    def check_user_password(self, user, password):
        """
        Check a user's password.

        This will hash the given password and compare it to the hashed
        password we have on file for the given user account.

        This is normally part of the login process, so the
        ``password`` param refers to the password entered by a user;
        this method will determine if it was correct.

        :param user: :class:`~wuttjamaican.db.model.auth.User` instance.

        :param password: User-entered password in plain text.

        :returns: ``True`` if password matches; else ``False``.
        """
        return password_context.verify(password, user.password)

    def get_role(self, session, key):
        """
        Locate and return a :class:`~wuttjamaican.db.model.auth.Role`
        per the given key, if possible.

        :param session: Open :term:`db session`.

        :param key: Value to use when searching for the role.  Can be
           a UUID or name of a role.

        :returns: :class:`~wuttjamaican.db.model.auth.Role` instance;
           or ``None``.
        """
        model = self.app.model

        if not key:
            return None

        # maybe it is a uuid
        if isinstance(key, _uuid.UUID):
            role = session.get(model.Role, key)
            if role:
                return role

        else:  # assuming it is a string
            # try to match on Role.uuid
            try:
                role = session.get(model.Role, _uuid.UUID(key))
                if role:
                    return role
            except ValueError:
                pass

            # try to match on Role.name
            role = session.query(model.Role).filter_by(name=key).first()
            if role:
                return role

        # try settings; if value then recurse
        key = self.config.get(f"{self.appname}.role.{key}", session=session)
        if key:
            return self.get_role(session, key)
        return None

    def get_user(self, obj, session=None):
        """
        Return the :class:`~wuttjamaican.db.model.auth.User`
        associated with the given object, if one can be found.

        This method should accept "any" type of ``obj`` and inspect it
        to determine if/how a user can be found.  It should return the
        "first, most obvious" user in the event that the given object
        is associated with multiple users.

        For instance ``obj`` may be a string in which case a lookup
        may be tried on
        :attr:`~wuttjamaican.db.model.auth.User.username`.  Or it may
        be a :class:`~wuttjamaican.db.model.base.Person` in which case
        their :attr:`~wuttjamaican.db.model.base.Person.user` may be
        returned.

        :param obj: Object for which user should be returned.

        :param session: Open :term:`db session`.  This is optional in
           some cases, i.e. one can be determined automatically if
           ``obj`` is some kind of object already contained in a
           session (e.g. ``Person``).  But a ``session`` must be
           provided if ``obj`` is a simple string and you need to do a
           lookup by username etc.

        :returns: :class:`~wuttjamaican.db.model.auth.User` or ``None``.
        """
        model = self.app.model

        # maybe obj is already a user
        if isinstance(obj, model.User):
            return obj

        # nb. these lookups require a db session
        if session:
            # or maybe it is a uuid
            if isinstance(obj, _uuid.UUID):
                user = session.get(model.User, obj)
                if user:
                    return user

            # or maybe it is a string
            elif isinstance(obj, str):
                # try to match on User.uuid
                try:
                    user = session.get(model.User, _uuid.UUID(obj))
                    if user:
                        return user
                except ValueError:
                    pass

                # try to match on User.username
                user = (
                    session.query(model.User).filter(model.User.username == obj).first()
                )
                if user:
                    return user

        # nb. obj is presumbly another type of object, e.g. Person

        # maybe we can find a person, then get user
        person = self.app.get_person(obj)
        if person:
            return person.user
        return None

    def make_person(self, **kwargs):
        """
        Make and return a new
        :class:`~wuttjamaican.db.model.base.Person`.

        This is a convenience wrapper around
        :class:`~wuttjamaican.people.PeopleHandler.make_person()`.
        """
        people = self.app.get_people_handler()
        return people.make_person(**kwargs)

    def make_user(self, session=None, **kwargs):
        """
        Make and return a new
        :class:`~wuttjamaican.db.model.auth.User`.

        This is mostly a simple wrapper around the
        :class:`~wuttjamaican.db.model.auth.User` constructor.  All
        ``kwargs`` are passed on to the constructor as-is, for
        instance.  It also will add the user to the session, if
        applicable.

        This method also adds one other convenience:

        If there is no ``username`` specified in the ``kwargs`` then
        it will call :meth:`make_unique_username()` to automatically
        provide one.  (Note that the ``kwargs`` will be passed along
        to that call as well.)

        :param session: Open :term:`db session`, if applicable.

        :returns: The new :class:`~wuttjamaican.db.model.auth.User`
           instance.
        """
        model = self.app.model

        if session and "username" not in kwargs:
            kwargs["username"] = self.make_unique_username(session, **kwargs)

        user = model.User(**kwargs)
        if session:
            session.add(user)
        return user

    def delete_user(self, user):
        """
        Delete the given user account.  Use with caution!  As this
        generally cannot be undone.

        Default behavior simply deletes the user account.  Depending
        on the DB schema and data present, this may cause an error
        (i.e. if the user is still referenced by other tables).

        :param user: :class:`~wuttjamaican.db.model.auth.User` to
           delete.
        """
        session = self.app.get_session(user)
        session.delete(user)

    def make_preferred_username(
        self, session, **kwargs
    ):  # pylint: disable=unused-argument
        """
        Generate a "preferred" username, using data from ``kwargs`` as
        hints.

        Note that ``kwargs`` should be of the same sort that might be
        passed to the :class:`~wuttjamaican.db.model.auth.User`
        constructor.

        So far this logic is rather simple:

        If ``kwargs`` contains ``person`` then a username will be
        constructed using the name data from the person
        (e.g. ``'john.doe'``).

        In all other cases it will return ``'newuser'``.

        .. note::

           This method does not confirm if the username it generates
           is actually "available" for a new user.  See
           :meth:`make_unique_username()` for that.

        :param session: Open :term:`db session`.

        :returns: Generated username as string.
        """
        person = kwargs.get("person")
        if person:
            first = (person.first_name or "").strip().lower()
            last = (person.last_name or "").strip().lower()
            if first and last:
                return f"{first}.{last}"
            if first:
                return first
            if last:
                return last

        return "newuser"

    def make_unique_username(self, session, **kwargs):
        """
        Generate a *unique* username, using data from ``kwargs`` as
        hints.

        Note that ``kwargs`` should be of the same sort that might be
        passed to the :class:`~wuttjamaican.db.model.auth.User`
        constructor.

        This method is a convenience which does two things:

        First it calls :meth:`make_preferred_username()` to obtain the
        "preferred" username.  (It passes all ``kwargs`` along when it
        makes that call.)

        Then it checks to see if the resulting username is already
        taken.  If it is, then a "counter" is appended to the
        username, and incremented until a username can be found which
        is *not* yet taken.

        It returns the first "available" (hence unique) username which
        is found.  Note that it is considered unique and therefore
        available *at the time*; however this method does not
        "reserve" the username in any way.  It is assumed that you
        would create the user yourself once you have the username.

        :param session: Open :term:`db session`.

        :returns: Username as string.
        """
        model = self.app.model

        original_username = self.make_preferred_username(session, **kwargs)
        username = original_username

        # check for unique username
        counter = 1
        while True:
            users = (
                session.query(model.User)
                .filter(model.User.username == username)
                .count()
            )
            if not users:
                break
            username = f"{original_username}{counter:02d}"
            counter += 1

        return username

    def set_user_password(self, user, password):
        """
        Set a user's password.

        This will update the
        :attr:`~wuttjamaican.db.model.auth.User.password` attribute
        for the user.  The value will be hashed using ``bcrypt``.

        :param user: :class:`~wuttjamaican.db.model.auth.User` instance.

        :param password: New password in plain text.
        """
        user.password = password_context.hash(password)

    def get_role_administrator(self, session):
        """
        Returns the special "Administrator" role.
        """
        return self._special_role(
            session, _uuid.UUID("d937fa8a965611dfa0dd001143047286"), "Administrator"
        )

    def get_role_anonymous(self, session):
        """
        Returns the special "Anonymous" (aka. "Guest") role.
        """
        return self._special_role(
            session, _uuid.UUID("f8a27c98965a11dfaff7001143047286"), "Anonymous"
        )

    def get_role_authenticated(self, session):
        """
        Returns the special "Authenticated" role.
        """
        return self._special_role(
            session, _uuid.UUID("b765a9cc331a11e6ac2a3ca9f40bc550"), "Authenticated"
        )

    def user_is_admin(self, user):
        """
        Check if given user is a member of the "Administrator" role.

        :rtype: bool
        """
        if user:
            session = self.app.get_session(user)
            admin = self.get_role_administrator(session)
            if admin in user.roles:
                return True

        return False

    def get_permissions(
        self, session, principal, include_anonymous=True, include_authenticated=True
    ):
        """
        Return a set of permission names, which represents all
        permissions effectively granted to the given user or role.

        :param session: Open :term:`db session`.

        :param principal: :class:`~wuttjamaican.db.model.auth.User` or
           :class:`~wuttjamaican.db.model.auth.Role` instance.  Can
           also be ``None``, in which case the "Anonymous" role will
           be assumed.

        :param include_anonymous: Whether the "Anonymous" role should
           be included when checking permissions.  If ``False``, the
           Anonymous permissions will *not* be checked.

        :param include_authenticated: Whether the "Authenticated" role
           should be included when checking permissions.

        :returns: Set of permission names.
        :rtype: set
        """
        # we will use any `roles` attribute which may be present.  in
        # practice we would be assuming a User in this case
        if hasattr(principal, "roles"):
            roles = [role for role in principal.roles if self._role_is_pertinent(role)]

            # here our User assumption gets a little more explicit
            if include_authenticated:
                roles.append(self.get_role_authenticated(session))

        # otherwise a non-null principal is assumed to be a Role
        elif principal is not None:
            roles = [principal]

        # fallback assumption is "no roles"
        else:
            roles = []

        # maybe include anonymous role
        if include_anonymous:
            roles.append(self.get_role_anonymous(session))

        # build the permissions cache
        cache = set()
        for role in roles:
            if hasattr(role, "permissions"):
                cache.update(role.permissions)

        return cache

    def has_permission(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        session,
        principal,
        permission,
        include_anonymous=True,
        include_authenticated=True,
    ):
        """
        Check if the given user or role has been granted the given
        permission.

        .. note::

           While this method is perfectly usable, it is a bit "heavy"
           if you need to make multiple permission checks for the same
           user.  To optimize, call :meth:`get_permissions()` and keep
           the result, then instead of calling ``has_permission()``
           just check if a given permission is contained in the cached
           result set.

           (The logic just described is exactly what this method does,
           except it will not keep the result set, hence calling it
           multiple times for same user is not optimal.)

        :param session: Open :term:`db session`.

        :param principal: Either a
           :class:`~wuttjamaican.db.model.auth.User` or
           :class:`~wuttjamaican.db.model.auth.Role` instance.  It is
           also expected that this may sometimes be ``None``, in which
           case the "Anonymous" role will be assumed.

        :param permission: Name of the permission for which to check.

        :param include_anonymous: Whether the "Anonymous" role should
           be included when checking permissions.  If ``False``, then
           Anonymous permissions will *not* be checked.

        :param include_authenticated: Whether the "Authenticated" role
           should be included when checking permissions.

        :returns: Boolean indicating if the permission is granted.
        """
        perms = self.get_permissions(
            session,
            principal,
            include_anonymous=include_anonymous,
            include_authenticated=include_authenticated,
        )
        return permission in perms

    def grant_permission(self, role, permission):
        """
        Grant a permission to the role.  If the role already has the
        permission, nothing is done.

        :param role: :class:`~wuttjamaican.db.model.auth.Role`
           instance.

        :param permission: Name of the permission as string.
        """
        if permission not in role.permissions:
            role.permissions.append(permission)

    def revoke_permission(self, role, permission):
        """
        Revoke a permission from the role.  If the role does not have
        the permission, nothing is done.

        :param role: A :class:`~rattail.db.model.users.Role` instance.

        :param permission: Name of the permission as string.
        """
        if permission in role.permissions:
            role.permissions.remove(permission)

    ##############################
    # API token methods
    ##############################

    def add_api_token(self, user, description):
        """
        Add and return a new API token for the user.

        This calls :meth:`generate_api_token_string()` to obtain the
        actual token string.

        See also :meth:`delete_api_token()`.

        :param user: :class:`~wuttjamaican.db.model.auth.User`
           instance for which to add the token.

        :param description: String description for the token.

        :rtype: :class:`~wuttjamaican.db.model.auth.UserAPIToken`
        """
        model = self.app.model
        session = self.app.get_session(user)

        # generate raw token
        token_string = self.generate_api_token_string()

        # persist token in DB
        token = model.UserAPIToken(description=description, token_string=token_string)
        user.api_tokens.append(token)
        session.add(token)

        return token

    def generate_api_token_string(self):
        """
        Generate a new *raw* API token string.

        This is called by :meth:`add_api_token()`.

        :returns: Raw API token string.
        """
        return secrets.token_urlsafe()

    def delete_api_token(self, token):
        """
        Delete the given API token.

        See also :meth:`add_api_token()`.

        :param token:
           :class:`~wuttjamaican.db.model.auth.UserAPIToken` instance.
        """
        session = self.app.get_session(token)
        session.delete(token)

    ##############################
    # internal methods
    ##############################

    def _role_is_pertinent(self, role):  # pylint: disable=unused-argument
        """
        Check the role to ensure it is "pertinent" for the current app.

        The idea behind this is for sake of a multi-node system, where
        users and roles are synced between nodes.  Some roles may be
        defined for only certain types of nodes and hence not
        "pertinent" for all nodes.

        As of now there is no actual support for that, but this stub
        method exists for when it will.
        """
        return True

    def _special_role(self, session, uuid, name):
        """
        Fetch a "special" role, creating if needed.
        """
        model = self.app.model
        role = session.get(model.Role, uuid)
        if not role:
            role = model.Role(uuid=uuid, name=name)
            session.add(role)
        return role
