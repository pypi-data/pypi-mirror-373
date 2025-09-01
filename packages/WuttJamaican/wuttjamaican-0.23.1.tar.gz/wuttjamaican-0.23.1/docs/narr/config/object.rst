
Config Object
=============

The app has a global :term:`config object` to track its settings.
This object is an instance of :class:`~wuttjamaican.conf.WuttaConfig`
and is usually available as e.g. ``self.config`` within code.


Creating the Config Object
--------------------------

All apps create the config object by calling
:func:`~wuttjamaican.conf.make_config()` during startup.  The desired
config files may be specified directly via call params, or indirectly
via environment variables.  (See also :doc:`files`.)

In some cases, notably the :term:`command` line interface, there is
already code in place to handle the ``make_config()`` call, and you
must specify the config files in another way - command line parameters
in this case.

One-off scripts should create the config object before doing anything
else.  To be safe this should happen before other modules are
imported::

   from wuttjamaican.conf import make_config

   config = make_config()

   from otherlib import foo

   foo(config)


Creating the App Handler
------------------------

The config object is also responsible for creating the :term:`app handler`.

Whereas the process of creating the config object is "stable" and
"always" produces an object of the same class, the app handler is more
likely to vary.  So while there is a default
:class:`~wuttjamaican.app.AppHandler` provided, it is expected that
some apps will want to override that.

The relationship between config object and app handler may be thought
of as "one-to-one" since each app will have a global config object as
well as a global app handler.  But the config object does come first,
to solve the "chicken-vs-egg" problem::

   from wuttjamaican.conf import make_config

   config = make_config()

   app = config.get_app()


Extending the Config Object
---------------------------

Some packages may need to "extend" the config object somehow, to add
various attributes which they may reference later when certain code
runs.

A typical example would be for an "integration" package, which is
responsible for communicating with a third party database.  This
package might extend the config by loading some database connections
based on config values, and attaching those directly to the config
object (and usually, configuring a ``Session`` class).

But here is a simpler example; add this to e.g. ``poser/config.py``::

   from wuttjamaican.conf import WuttaConfigExtension

   class PoserConfigExtension(WuttaConfigExtension):
       """
       Custom config extension for Poser
       """
       key = 'poser'

       def configure(self, config):
           foo = config.setdefault('poser.foo', 'bar')
           config.poser_foo = foo

Then you must register an :term:`entry point` in your ``setup.cfg``:

.. code-block:: ini

   [options.entry_points]
   wutta.config.extensions =
        poser = poser.config:PoserConfigExtension

After your ``poser`` package is installed, the extension logic should
automatically run when the config object is being made.
