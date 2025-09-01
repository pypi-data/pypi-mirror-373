
Ad Hoc Scripts
==============

It can be useful to write :term:`ad hoc scripts<ad hoc script>` for
certain things, as opposed to a proper :term:`subcommand`.  This is
especially true when first getting acquainted with the framework.

A script is just a text file with Python code.  To run it you
generally must invoke the Python interpreter somehow and explicitly
tell it the path to your script.

Note that a script is (usually) not installed as part of a
:term:`package`.  They can live anywhere.

Below we'll walk through creating a script.


Hello World
-----------

First to establish a baseline, here is a starting point script which
we'll name ``hello.py``::

   print('hello world')

Run that like so:

.. code-block:: sh

   $ python hello.py
   hello world


Better Standards
~~~~~~~~~~~~~~~~

Keeping it simple, but improving that script per recommended patterns::

   def hello():
       print('hello world')

   if __name__ == '__main__':
       hello()

Runs the same:

.. code-block:: sh

   $ python hello.py
   hello world


Configurability
---------------

If you have a :term:`config file` e.g. named ``my.conf``:

.. code-block:: ini

   [hello]
   name = George

Then you can make a :term:`config object` to access its values.  Note
that this also gives you access to the :term:`app handler`::

   from wuttjamaican.conf import make_config

   def hello(config):
       app = config.get_app()
       print('hello', config.get('hello.name'))
       print('from', app.get_title())

   if __name__ == '__main__':
       config = make_config('my.conf')
       hello(config)

Output should now be different:

.. code-block:: sh

   $ python hello.py
   hello George
   from WuttJamaican

You are likely to need more imports; it is generally wise to do those
*within the function* as opposed to the top of the module.  This is to
ensure the :func:`~wuttjamaican.conf.make_config()` call happens
before all packages are imported::

   from wuttjamaican.conf import make_config

   def hello(config):

       # do extra imports here
       from otherpkg import something

       app = config.get_app()
       print('hello', config.get('hello.name'))
       print('from', app.get_title())

       something(config)

   if __name__ == '__main__':
       config = make_config('my.conf')
       hello(config)


Logging
-------

Logging behavior is determined by the config file(s).  If they contain
no directives pertaining to the logging config then some default
behavior will be used.

In any case your script should not need to worry about that, but is
free to make logging calls.  The configured logging behavior would
determine whether such messages are output to the console and/or file
etc.

There are 3 steps to logging:

* import the :mod:`python:logging` module
* call :func:`~python:logging.getLogger()` to get a logger
* call methods on the logger, e.g. :meth:`~python:logging.Logger.debug()`

Here is the script with logging incorporated::

   # nb. it is always safe to import from standard library at the
   # top of module, that will not interfere with make_config()
   import logging

   from wuttjamaican.conf import make_config

   log = logging.getLogger(__name__)
   log.debug("still at top of module")

   def hello(config):

       # do extra imports here
       from otherpkg import something

       log.debug("saying hello")
       app = config.get_app()
       print('hello', config.get('hello.name'))
       print('from', app.get_title())

       log.debug("about to do something")
       if something(config):
           log.info("something seems to have worked")
       else:
           log.warn("oh no! something failed")

   if __name__ == '__main__':
       log.debug("entered the __main__ block")
       config = make_config('my.conf')
       log.debug("made config object: %s", config)
       hello(config)
       log.debug("all done")
