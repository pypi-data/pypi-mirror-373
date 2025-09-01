
Databases
=========

Most :term:`apps <app>` based on WuttJamaican will have an :term:`app
database`.  This may be used to store :term:`config settings <config
setting>` but usually, lots of other things.

Each app can declare its :term:`app model` which is essentially the
list of tables, each mapped to a Python class via SQLAlchemy ORM.  The
default app model is :mod:`wuttjamaican.db.model`.

But of course any other :term:`database(s) <database>` may be
involved, for integration purposes etc.  So there are some
conveniences around that too.


.. toctree::
   :maxdepth: 3

   app
   other
