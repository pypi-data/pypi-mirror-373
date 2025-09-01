
App Database
============

The :term:`app database` is used at minimum to store the
:term:`settings table`, but usually also has tables for other
:term:`data models <data model>` used by the app.

If you *only* want a settings table but do not need the app database
to serve any other purpose, see :doc:`/narr/config/table`.


.. _create-appdb:

Create the Database
-------------------

There is not currently any tooling in WuttJamaican to *create* the
database (unless using a SQLite file, which may happen automatically).

PostgreSQL is the recommended backend for production, as it is the
only one with rigorous usage thus far.  MySQL should also work though
and you're free to experiment.  Theoretically anything supported by
SQLAlchemy should work; see :doc:`sqlalchemy:dialects/index`.

You may need to install additional Python and/or OS packages to
support your desired backend.

PostgreSQL
~~~~~~~~~~

Install APT packages if needed:

.. code-block:: sh

   sudo apt install postgresql libpq-dev

Install Python packages (to :term:`virtual environment`) if needed:

.. code-block:: sh

   pip install psycopg2

Make a new DB user ("myuser") if needed:

.. code-block:: sh

   sudo -u postgres createuser myuser

And if so, also set the password:

.. code-block:: sh

   sudo -u postgres psql -c "ALTER USER myuser PASSWORD 'mypassword'"

And finally create the DB ("myappdb" owned by "myuser"):

.. code-block:: sh

   sudo -u postgres createdb -O myuser myappdb

MySQL
~~~~~

Install APT packages if needed:

.. code-block:: sh

   sudo apt install default-mysql-server

Install Python packages (to :term:`virtual environment`) if needed:

.. code-block:: sh

   pip install mysql-connector-python

Make a new DB user ("myuser") if needed:

.. code-block:: sh

   sudo mysql -e "CREATE USER myuser@localhost"

And if so, also set the password:

.. code-block:: sh

   sudo mysql -e "ALTER USER myuser@localhost  IDENTIFIED BY 'mypassword'"

Create the DB ("myappdb"):

.. code-block:: sh

   sudo mysqladmin create myappdb

And grant all perms (to "myuser" for "myappdb"):

.. code-block:: sh

   sudo mysql -e "GRANT ALL ON myappdb.* TO myuser@localhost"


Configure the Connection
------------------------

Once you have a database ready, add to your :term:`config file` the
details, for example:

.. code-block:: ini

   [wutta.db]

   # postgres
   default.url = postgresql://myuser:mypassword@localhost/myappdb

   # mysql
   default.url = mysql+mysqlconnector://myuser:mypassword@localhost/myappdb

You also most likely want to prefer settings from the DB over those
found in the config file(s).  See also
:ref:`where-config-settings-come-from` but the gist is, you should add
this config:

.. code-block:: ini

   [wutta.config]
   usedb = true
   preferdb = true


Install the Schema
------------------

So far there is not a tool to "create all tables" for the :term:`app
model` in one step per se.  Rather, we use Alembic to "apply all
migrations" to get to the latest schema.  (The end result is the
same.)

See also the :doc:`Alembic docs <alembic:index>`, but our process is
fairly simple.

First add some Alembic settings to your :term:`config file`:

.. code-block:: ini

   [alembic]
   script_location = wuttjamaican.db:alembic
   version_locations = wuttjamaican.db:alembic/versions

Usually the ``script_location`` shown above will work fine, but the
``version_locations`` may vary depending on which packages contribute
to your overall app model.

For instance a Poser app which also uses :doc:`Wutta-Continuum
<wutta-continuum:index>` may specify this instead:

.. code-block:: ini

   [alembic]
   script_location = wuttjamaican.db:alembic
   version_locations = wutta_continuum.db:alembic/versions poser.db:alembic/versions wuttjamaican.db:alembic/versions

Note that is really specifying 3 different packages, and the sequence matters (*):

* ``wutta_continuum.db:alembic/versions``
* ``poser.db:alembic/versions``
* ``wuttjamaican.db:alembic/versions``

(*) While it does seem to matter, this is not yet fully understood.
You may need to experiment.

In any case once you've added the Alembic settings you can migrate schema:

.. code-block:: sh

   alembic -c /path/to/my.conf upgrade heads

If you have multiple packages for schema (as shown above) and you get
errors here, you may need to try a different package sequence in
config.

But if the migration went okay then you now have a complete app database.


Multiple Databases
------------------

Some scenarios may require multiple app databases.  A notable example
would be a multi-store retail environment, where each store runs a
separate app but a "host" (master) node has connections to all store
databases.

Using that example, the host config might look like:

.. code-block:: ini

   [wutta.db]
   # nb. the localhost ("host") node is default
   keys = default, store001, store002, store003

   default.url = postgresql://wutta:wuttapass@localhost/wutta-host

   store001.url = postgresql://wutta:wuttapass@store001/wutta-store
   store002.url = postgresql://wutta:wuttapass@store002/wutta-store
   store003.url = postgresql://wutta:wuttapass@store003/wutta-store

And to be thorough, each store config might look like:

.. code-block:: ini

   [wutta.db]
   # nb. the localhost ("store") node is default
   keys = default, host

   default.url = postgresql://wutta:wuttapass@localhost/wutta-store

   host.url = postgresql://wutta:wuttapass@host-server/wutta-host
