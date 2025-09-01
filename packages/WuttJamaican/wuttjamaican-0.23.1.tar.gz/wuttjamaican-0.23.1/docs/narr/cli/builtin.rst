
Built-in Commands
=================

WuttJamaican comes with one top-level :term:`command`, and some
:term:`subcommands<subcommand>`.

It uses `Typer`_ for the underlying CLI framework.

.. _Typer: https://typer.tiangolo.com/


``wutta``
---------

This is the top-level command.  Its purpose is to expose subcommands
pertaining to WuttJamaican.

It is installed to the virtual environment in the ``bin`` folder (or
``Scripts`` on Windows):

.. code-block:: sh

   cd /path/to/venv
   bin/wutta --help

Defined in: :mod:`wuttjamaican.cli`

.. program-output:: wutta --help


.. _wutta-make-appdir:

``wutta make-appdir``
---------------------

Make the :term:`app dir` for the current :term:`virtual environment`.

Defined in: :mod:`wuttjamaican.cli.make_appdir`

.. program-output:: wutta make-appdir --help


.. _wutta-make-uuid:

``wutta make-uuid``
-------------------

Print a new universally-unique identifier to standard output.

Defined in: :mod:`wuttjamaican.cli.make_uuid`

.. program-output:: wutta make-uuid --help


.. _wutta-problems:

``wutta problems``
------------------

Find and report on problems with the data or system.

Defined in: :mod:`wuttjamaican.cli.problems`

.. program-output:: wutta problems --help
