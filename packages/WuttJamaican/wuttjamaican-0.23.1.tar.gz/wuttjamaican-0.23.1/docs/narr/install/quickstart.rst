
Quick Start
===========

We have two varieties of "quick start" instructions:

* :ref:`quick-start-generated`
* :ref:`quick-start-manual`


.. _quick-start-generated:

From Generated Code
-------------------

Note that this section describes an app based on WuttaWeb (i.e. not
just WuttJamaican).  We'll name it "Poser" for sake of example.

Make a parent folder for all source code:

.. code-block:: sh

   mkdir -p ~/src

Make and activate a new :term:`virtual environment` for your project:

.. code-block:: sh

   cd /path/to/envs
   python3 -m venv poser
   source poser/bin/activate

Make a new e.g. ``poser`` database in PostgreSQL (or MySQL).  Nothing
special here but for instructions see :ref:`create-appdb`.

Install and run `cookiecutter <https://cookiecutter.readthedocs.io/>`_
with `wuttaweb template
<https://forgejo.wuttaproject.org/wutta/cookiecutter-wuttaweb>`_:

.. code-block:: sh

   pip install cookiecutter
   cookiecutter -o ~/src git+https://forgejo.wuttaproject.org/wutta/cookiecutter-wuttaweb

Assuming you now have project code at ``~/src/poser`` then install
that and run the app installer.  Note the 2nd command name will depend
on your project:

.. code-block:: sh

   pip install -e ~/src/poser
   poser install

If all goes well, you can run the web app with:

.. code-block:: sh

   cd /path/to/envs/poser
   bin/wutta -c app/web.conf webapp -r

And browse it at http://localhost:9080


.. _quick-start-manual:

From Scratch
------------

This shows the *minimum* use case, basically how to make/use the
:term:`config object` and :term:`app handler`.

(See next section for :ref:`db-setup`.)

You should have already made a :term:`virtual environment`.  Install
the package with:

.. code-block:: sh

   pip install WuttJamaican[db]

Create a :term:`config file`, e.g. ``my.conf``:

.. code-block:: ini

   [foo]
   bar = A
   baz = 2
   feature = true
   words = the quick brown fox

In code, load the config and reference its values as needed, and/or
invoke other app/handler logic::

   from wuttjamaican.conf import make_config

   config = make_config('/path/to/my.conf')

   # this call..                        ..returns this value

   config.get('foo.bar')                # 'A'

   config.get('foo.baz')                # '2'
   config.get_int('foo.baz')            # 2

   config.get('foo.feature')            # 'true'
   config.get_bool('foo.feature')       # True

   config.get('foo.words')              # 'the quick brown fox'
   config.get_list('foo.words')         # ['the', 'quick', 'brown', 'fox']

   # now for the app handler..and interacting with DB
   app = config.get_app()
   model = app.model
   session = app.make_session()

   # invoke secondary handler to make new user account
   auth = app.get_auth_handler()
   user = auth.make_user(session=session, username='barney')

   # commit changes to DB
   session.add(user)
   session.commit()

For more info see:

* :func:`~wuttjamaican.conf.make_config()`
* :class:`~wuttjamaican.conf.WuttaConfig` and especially
  :meth:`~wuttjamaican.conf.WuttaConfig.get()`
* :class:`~wuttjamaican.app.AppHandler`


.. _db-setup:

Database Setup
~~~~~~~~~~~~~~

You should already have the package installed (see previous section).

Next you must create the database, as well as any user account needed,
within the DB backend.  This is pretty routine but for instructions
see :ref:`create-appdb`.

Now add the DB info to your :term:`config file` (e.g. ``my.conf`` as
shown above).  Contents for this will look something like (using
``poserdb`` as the DB name):

.. code-block:: ini

   [wutta.db]

   # postgres
   default.url = postgresql://USERNAME:PASSWORD@localhost/poserdb

   # mysql
   default.url = mysql+mysqlconnector://USERNAME:PASSWORD@localhost/poserdb

You also must add some Alembic config, needed for DB schema
migrations:

.. code-block:: ini

   [alembic]
   script_location = wuttjamaican.db:alembic
   version_locations = wuttjamaican.db:alembic/versions

With config file updated you can run the Alembic command to migrate schema:

.. code-block:: sh

   alembic -c /path/to/my.conf upgrade heads

Now you should have all the tables required for a WuttJamaican
:term:`app database`.

If you wish to store :term:`config settings <config setting>` in the
DB, don't forget to add to your config file (see also
:ref:`where-config-settings-come-from`):

.. code-block:: ini

   [wutta.config]
   usedb = true
   preferdb = true
