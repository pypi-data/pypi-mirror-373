
Overview
========

The app uses a global :term:`config object` to keep track of its
:term:`config settings<config setting>`.  See also :doc:`object`.

The app must call :func:`~wuttjamaican.conf.make_config()` during
startup to obtain the config object.

Values come (mostly) from :term:`config files<config file>` and/or the
:term:`settings table`.  For more about those see:

* :doc:`settings`
* :doc:`files`
* :doc:`table`

Values are always strings in their raw format, as returned by
:meth:`~wuttjamaican.conf.WuttaConfig.get()`.  But the config object
also has methods to coerce values to various types, e.g.:

* :meth:`~wuttjamaican.conf.WuttaConfig.get_bool()`
* :meth:`~wuttjamaican.conf.WuttaConfig.get_int()`
* :meth:`~wuttjamaican.conf.WuttaConfig.get_list()`

The config object is also responsible for creating the :term:`app
handler`::

   from wuttjamaican.conf import make_config

   config = make_config()
   app = config.get_app()

   if config.get_bool('foo.bar'):
       print('YES for foo.bar')
   else:
       print('NO for foo.bar')

   with app.short_session() as session:
       print(session.bind)
