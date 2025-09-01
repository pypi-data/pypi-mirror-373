
Settings Table
==============

Sometimes the :term:`config settings<config setting>` may come from a
:term:`settings table` as opposed to :term:`config file`.

The settings table resides in the :term:`app database`.

Note that as of writing, the WuttJamaican package *does not address*
how to create or setup the app database.  However it does have the
ability to query the settings table if present.


Table Structure
---------------

Currently the table *must* be named ``setting`` and have (at least) 2
columns, ``name`` and ``value``:

.. code-block:: sql

   CREATE TABLE setting (
       name VARCHAR(255) NOT NULL PRIMARY KEY,
       value TEXT
   );


Configuring the DB Connection
-----------------------------

You must add some entries to your config file, to tell the app where
its database lives, and that it should be used for this purpose:

.. code-block:: ini

   [wutta.config]
   usedb = true
   preferdb = true

   [wutta.db]
   default.url = postgresql://wutta:wuttapass@localhost/wuttadb

This uses `SQLAlchemy`_ under the hood, so it should support anything
that does; see also
:meth:`~wuttjamaican.app.AppHandler.make_engine_from_config()`.

.. _SQLAlchemy: https://www.sqlalchemy.org

See :ref:`where-config-settings-come-from` for more about the
``usedb`` and ``preferdb`` flags.


Querying the Table
------------------

Normally there is no need to query directly, but rather the
:term:`config object` may do so automatically.

Assuming the config object knows to look in the settings table, then
it's just a matter of calling its normal
:meth:`~wuttjamaican.conf.WuttaConfig.get()` and similar methods::

   from wuttjamaican.conf import make_config

   config = make_config()
   
   config.get('foo.bar')
   config.get_bool('foo.flag')

If your config object does *not* check the settings table by default,
you can always ask it to explicitly::

   config.get('foo.bar', usedb=True, preferdb=True)
