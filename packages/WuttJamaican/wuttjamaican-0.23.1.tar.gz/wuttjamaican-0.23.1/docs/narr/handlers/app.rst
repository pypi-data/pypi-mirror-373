
App Handler
===========

There is one special "global" type of :term:`handler` which
corresponds to the :term:`app` itself, whereas all other handlers
correspond to some "portion" of the app.

The :term:`app handler` provides:

* various "global" utilities
* primary interface for obtaining all other handlers

The base class and default app handler is
:class:`wuttjamaican.app.AppHandler`.

The :term:`config object` is responsible for creating the app handler
via :meth:`~wuttjamaican.conf.WuttaConfig.get_app()`::

   from wuttjamaican.conf import make_config

   config = make_config()
   app = config.get_app()


Overriding the App Handler
--------------------------

It is expected that many apps will want a more customized app handler.
To do this, first create your app handler class e.g. in
``poser/app.py``::

   from wuttjamaican.app import AppHandler

   class PoserAppHandler(AppHandler):
       """
       Custom app handler for the Poser system.
       """

       def make_session(self, **kwargs):
           """
           Override this method to specify extra/default params etc.
           """
           #kwargs.setdefault('foo', 'bar')
           session = super().make_session(**kwargs)
           return session

       def hello(self):
           """
           Extra method to print a hello message.
           """
           print("hello from", self.appname)


Then in your config file, specify that your app handler should be used
instead of the default.  Note that the config section will need to
match whatever the :term:`app name` is.  (And note that the app name
is not necessarily the same as your :term:`package` name!)

.. code-block:: ini

   # nb. this is the default
   [wutta]
   app.handler = poser.app:PoserAppHandler

   # but if appname is 'foobar' then it should be this
   [foobar]
   app.handler = poser.app:PoserAppHandler
