
Other Databases
===============

Connecting to "external" (non-app) :term:`databases<database>`
essentially works the same as for the :term:`app database`.


WordPress Example
-----------------

As a somewhat contrived example, let's say the app needs to query a
WordPress database directly.

WuttJamaican only reserves a single config file section for itself,
which may vary (per :term:`app name`) but by default is ``wutta.db``:

.. code-block:: ini

   [wutta.db]
   default.url = sqlite://

But any other config file section is up for grabs.  Some other
packages may effectively reserve other sections, but if we assume
nobody has yet reserved the ``wordpress.db`` section, might add
something like:

.. code-block:: ini

   [wordpress.db]
   default.url = mysql://wutta:wuttapass@localhost/wordpress

Then in the app code you can load the connection(s) with
:func:`~wuttjamaican.db.conf.get_engines()`::

   from wuttjamaican.conf import make_config
   from wuttjamaican.db.conf import get_engines

   config = make_config()
   engines = get_engines(config, 'wordpress.db')

As you might imagine, "rinse and repeat" for other types of databases
besides WordPress.


Multiple Databases
------------------

As with the app database, you can have multiple databases per type.

To continue with the previous example, let's say you have a
"production" WordPress site but also a "staging" site and the app must
query both.

There should always be a "default" database chosen, so in this case
we'll choose "production" for that:

.. code-block:: ini

   [wordpress.db]
   keys = default, staging
   default.url = mysql://wutta:wuttapass@localhost/wordpress
   staging.url = mysql://wutta:wuttapass@localhost/wordpress_test

Then in the app code you can reference both a la::

   from sqlalchemy import orm
   from wuttjamaican.conf import make_config
   from wuttjamaican.db.conf import get_engines

   config = make_config()
   engines = get_engines(config, 'wordpress.db')

   Session = orm.sessionmaker()
   Session.configure(bind=engines['default'])

   prod_sess = Session()
   stag_sess = Session(bind=engines['staging'])
