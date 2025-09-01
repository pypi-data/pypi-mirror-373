
Config Settings
===============

The app uses :term:`config settings<config setting>` to control its
behavior at runtime.

The term "config setting" may be thought of as a combination of these
terms:

* :term:`config file`
* :term:`settings table`

It really refers to the **value** of such a config setting, when you
get right down to it.  The app uses a :term:`config object` to keep
track of its config settings.


.. _reading-config-settings:

Reading Values via Python
-------------------------

Call the config object's :meth:`~wuttjamaican.conf.WuttaConfig.get()`
method to retrieve a value based on the setting name.

Note that raw values are always strings.  The config object has other
methods if you want to interpret the value as a particular type::

   from wuttjamaican.conf import make_config

   config = make_config()

   config.get('foo.bar')
   config.get_int('foo.baz')
   config.get_bool('foo.feature')
   config.get_list('foo.words')

See :class:`~wuttjamaican.conf.WuttaConfig` for full details.


.. _where-config-settings-come-from:

Where Values Come From
----------------------

Config settings usually come from either a :term:`config file` or a
:term:`settings table`.  The :term:`config object` is ultimately
responsible for sorting out which value to return.

Technically the app may also specify some fallback/default values; for
sake of this discussion we'll treat those as if they come from config
file.

All apps are expected to use config file(s), but not all will have a
settings table.  The config file(s) may specify whether a settings
table should be used.

There are only 2 config settings which control this behavior.  For a
typical example which enables both:

.. code-block:: ini

   [wutta.config]
   usedb = true
   preferdb = true

   [wutta.db]
   default.url = sqlite://

Note that to use a settings table you must of course define a DB
connection.

So the ``usedb`` and ``preferdb`` flags may be set to accomplish any
of these scenarios:

* enable both - settings table is checked first, config files used as
  fallback
* enable ``usedb`` but not ``preferdb`` - config files are checked
  first, settings table used as fallback
* disable ``usedb`` - config files only; do not use settings table

Most apps will want to enable both flags so that when the settings
table is updated, it will immediately affect app behavior regardless
of what values are in the config files.

The values for these flags is available at runtime as:

* :attr:`~wuttjamaican.conf.WuttaConfig.usedb`
* :attr:`~wuttjamaican.conf.WuttaConfig.preferdb`

Regardless of what the "normal" behavior is for the config object (per
those flags), you can explcitly request other behavior by passing
similar flags to the config object's
:meth:`~wuttjamaican.conf.WuttaConfig.get()` method::

   config.get('foo.bar', usedb=True, preferdb=True)

   config.get('foo.baz', usedb=False)

Some of the "core" settings in the framework are fetched with
``usedb=False`` so they will never be read from the settings table.
Canonical example of this would be the setting(s) which defines the DB
connection itself.
