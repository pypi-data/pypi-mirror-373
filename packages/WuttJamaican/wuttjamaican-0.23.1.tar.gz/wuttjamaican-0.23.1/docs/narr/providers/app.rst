
App Providers
=============

An :term:`app provider` is a :term:`provider` which can "extend" the
main :term:`app handler`.

The provider generally does this by adding extra methods to the app
handler.  Note that it does this regardless of which app handler is
configured to be used.

:class:`~wuttjamaican.app.AppProvider` is the base class.


Adding a new Provider
---------------------

First define your provider class.  Note that the method names should
include a "prefix" unique to your project (``poser_`` in this case).
This is to avoid naming collisions with the app handler itself, as
well as other app providers.  So e.g. in ``poser/app.py``::

   from wuttjamaican.app import AppProvider

   class PoserAppProvider(AppProvider):
       """
       App provider for Poser system
       """

       # nb. method name uses 'poser_' prefix
       def poser_do_something(self, **kwargs):
           """
           Do something for Poser
           """
           print("did something")

Register the :term:`entry point` in your ``setup.cfg``:

.. code-block:: ini

   [options.entry_points]

   wutta.providers =
       poser = poser.app:PoserAppProvider

Assuming you have not customized the app handler proper, then you will
be using the *default* app handler yet it will behave as though it has
the "provided" methods::

   from wuttjamaican.conf import make_config

   # make normal app
   config = make_config()
   app = config.get_app()

   # whatever this does..
   app.poser_do_something()
