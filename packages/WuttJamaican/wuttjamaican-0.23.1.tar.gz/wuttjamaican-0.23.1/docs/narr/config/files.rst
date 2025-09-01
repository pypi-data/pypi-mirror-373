
Config Files
============

A :term:`config file` is just a text file with :term:`config
settings<config setting>`.


Basic Syntax
------------

Currently only INI-style syntax is supported.  Under the hood a
:class:`~python:configparser.ConfigParser` instance is used to read
the files.

There is no "type hinting" within the config file itself, although you
can ask the config object to interpret values according to a specific
type.  See also :ref:`reading-config-settings`.

The basic syntax looks like this:

.. code-block:: ini

   [myapp]
   foo = A
   bar = 2
   feature = true
   words = the,quick,brown,fox,"did something unusual"
   paths =
       /path/to/first/folder
       "/path/to/folder with spaces"
       /another/one   /and/another

   [more]
   things = go here

Note that ``words`` and ``paths`` show 2 ways of defining lists, for
use with :meth:`~wuttjamaican.conf.WuttaConfig.get_list()`.  This
splits the value by whitespace as well as commas; quotation marks may
be used to avoid unwanted splits.


Specifying via Command Line
---------------------------

While no :term:`commands<command>` are shipped with WuttJamaican,
certain other packages may ship with commands (notably, Rattail).  The
convention is to accept a ``--config`` (or ``-c``) param on the
command line, e.g.:

.. code-block:: sh

   rattail --config=myapp.conf

   rattail -c first.conf -c second.conf


Specifying via Environment Variable
-----------------------------------

Probably most useful for command line scripts etc.  Note that if the
command line itself specifies ``-c`` or ``--config`` then the
environment variables are ignored.

.. code-block:: sh

   WUTTA_CONFIG_FILES=myapp.conf

   WUTTA_CONFIG_FILES=first.conf:second.conf

The env variable name used will depend on the :term:`app name`.


Specifying via Python
---------------------

Pass the files directly to :func:`~wuttjamaican.conf.make_config()`::

   make_config('myapp.conf')

   make_config(['first.conf', 'second.conf'])


File Priority
-------------

If multiple config files are used then the sequence will matter in
terms of value lookup.  Effectively, whenever
:meth:`~wuttjamaican.conf.WuttaConfig.get()` is called on the config
object, each file will be searched until a value is found.

For example let's say you have 3 config files:

* ``app.conf`` ("most specific to the app")
* ``machine.conf`` ("less specific to the app")
* ``site.conf`` ("least specific to the app")

To ensure that sequence you must specify the files in that order (*),
e.g. via command line:

.. code-block:: sh

   wutta -c app.conf -c machine.conf -c site.conf

or via Python::

   config = make_config(['app.conf', 'machine.conf', 'site.conf'])

(*) Actually that isn't always true, but for now let's pretend.

That way, if both ``app.conf`` and ``site.conf`` have a particular
setting defined, the value from ``app.conf`` will "win" and the value
from ``site.conf`` is simply ignored.

The sequence of files actually read into the config object may be
confirmed by inspecting either
:attr:`~wuttjamaican.conf.WuttaConfig.files_read` or (for typical
setups) the log file.


Including More Files
--------------------

When :func:`~wuttjamaican.conf.make_config()` is called, it first
determines the set of config files based on caller params etc.  It
then gives that set of files to the
:class:`~wuttjamaican.conf.WuttaConfig` constructor.

But when these files are actually read into the config object, they
can in turn "include" (or "require") additional files.

For example let's again say you have these 3 config files:

* ``app.conf``
* ``machine.conf``
* ``site.conf``

In the previous section we mentioned you could request all 3 files in
the correct order:

.. code-block:: sh

   wutta -c app.conf -c machine.conf -c site.conf

But another, usually better way is to add config settings such as:

in ``app.conf``

.. code-block:: ini

   [wutta.config]
   include = %(here)s/machine.conf

in ``machine.conf``

.. code-block:: ini

   [wutta.config]
   include = %(here)s/site.conf

And then you need only specify the main file when running the app:

.. code-block:: sh

   wutta -c app.conf

or via Python::

   make_config('app.conf')

Examples above show the ``include`` syntax but ``require`` is similar:

.. code-block:: ini

   [wutta.config]
   require = /path/to/otherfile.conf

If an "included" file is missing it will be skipped, but if a
"required" file is missing an error will be raised.


Default Locations
-----------------

If no config files were specified via any method, then some default
file paths may be tried as fallback.

The actual paths used for defaults will vary based on :term:`app name`
and other details such as operating system.  But as a simple (and
incomplete) example, with app name of ``wutta`` running on Linux,
default paths would include things like:

* ``~/.wutta.conf``
* ``/usr/local/etc/wutta.conf``
* ``/etc/wutta.conf``

While it is hoped that some may find this feature useful, it is
perhaps better to be explicit about which config files you want the
app to use.

Custom apps may also wish to devise ways to override the logic
responsible for choosing default paths.

For more details see :func:`~wuttjamaican.conf.get_config_paths()` and
:func:`~wuttjamaican.conf.generic_default_files()`.
