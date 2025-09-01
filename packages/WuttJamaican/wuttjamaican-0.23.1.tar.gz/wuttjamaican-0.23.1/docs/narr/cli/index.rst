
Command Line
============

Most apps will need some sort of command line usage, via cron or
otherwise.  There are two main aspects to it:

There is a proper CLI framework based on `Typer`_, with top-level
:term:`commands<command>` and :term:`subcommands<subcommand>`.  The
``wutta`` command is built-in and includes some subcommands, but each
app can define more of either as needed.  Such (sub)commands are
installed as part of a :term:`package`.

.. _Typer: https://typer.tiangolo.com

But sometimes you just need an :term:`ad hoc script` which is a single
file and can be placed anywhere, usually *not* installed as part of a
package.

.. toctree::
   :maxdepth: 2

   builtin
   custom
   scripts
