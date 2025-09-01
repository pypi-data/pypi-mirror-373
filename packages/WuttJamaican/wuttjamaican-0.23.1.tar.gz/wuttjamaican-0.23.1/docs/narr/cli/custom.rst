
Custom Commands
===============

WuttJamaican comes with :doc:`/narr/cli/builtin`.

Using the same framework, each :term:`package` can define additional
top-level :term:`command(s)<command>` and
:term:`subcommands<subcommand>` as needed.


Top-Level Command
-----------------

You must "define" *and* "register" your top-level command.  Assuming a
basic Poser example:

.. code-block:: none

   poser-project
   ├── poser
   │   ├── __init__.py
   │   └── cli.py
   └── pyproject.toml

Add the command definition to the ``poser.cli`` module::

   from wuttjamaican.cli import make_typer

   poser_typer = make_typer(
       name='poser',
       help="Poser - the killer app"
   )

Then register the command as script in ``pyproject.toml``:

.. code-block:: toml

   [project.scripts]
   poser = "poser.cli:poser_typer"

Then reinstall your project:

.. code-block:: sh

   pip install -e ~/src/poser

And now you can run your command:

.. code-block:: sh

   poser --help

But it won't really do anything until you add subcommands.


Subcommands
-----------

You must "define" the subcommand of course, but do not need to
"register" it.  (That happens via function decorator; see below.)

However you *do* need to ensure all modules containing subcommands are
"eagerly imported" so the runtime discovery process finds everything.

Here we'll define the ``poser hello`` subcommand, by adding it to our
``poser.cli`` module (from example above)::

   import sys
   import typer
   from wuttjamaican.cli import make_typer

   # top-level command
   poser_typer = make_typer(
       name='poser',
       help="Poser - the killer app"
   )

   # nb. function decorator will auto-register the subcommand
   @poser_typer.command()
   def hello(
           ctx: typer.Context,
   ):
       """
       Hello world example
       """
       config = ctx.parent.wutta_config
       app = config.get_app()

       name = config.get('hello.name', default="WhoAreYou")
       sys.stdout.write(f'hello {name}\n')

       title = app.get_title()
       sys.stdout.write(f'from {title}\n')

   # TODO: you may need to import other modules here, if they contain
   # subcommands and would not be automatically imported otherwise.
   # nb. *this* current module *is* automatically imported, only
   # because of the top-level command registration in pyproject.toml

No need to re-install, you can now use the subcommand:

.. code-block:: sh

   poser hello --help
