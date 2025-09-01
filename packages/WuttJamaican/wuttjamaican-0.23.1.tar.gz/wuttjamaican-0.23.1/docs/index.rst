
WuttJamaican
============

This package aims to provide a "base layer" for apps regardless of
platform or environment (console, web, GUI).

It comes from patterns developed within the `Rattail Project`_, and
roughly corresponds with the "base and data layers" as described in
:doc:`rattail-manual:index`.

.. _Rattail Project: https://rattailproject.org/

Good documentation and 100% `test coverage`_ are priorities for this
project.

.. _test coverage: https://buildbot.rattailproject.org/coverage/wuttjamaican/

.. image:: https://img.shields.io/badge/linting-pylint-yellowgreen
    :target: https://github.com/pylint-dev/pylint

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black


Features
--------

* flexible configuration, using config files and/or DB settings table
* flexible architecture, abstracting various portions of the overall app
* flexible command line interface, using `Typer`_
* flexible database support, using `SQLAlchemy`_

.. _Typer: https://typer.tiangolo.com
.. _SQLAlchemy: https://www.sqlalchemy.org

See also these projects which build on WuttJamaican:

* `WuttaWeb <https://rattailproject.org/docs/wuttaweb/>`_ - web app
  framework
* `WuttaSync <https://rattailproject.org/docs/wuttasync/>`_ - data
  import/export and real-time sync
* :doc:`wutta-continuum:index` - data versioning with
  SQLAchemy-Continuum

And for something completely different...go give a listen to `Victor
Wooten's song <https://www.youtube.com/watch?v=ZrcjlK9e8rg>`_!




Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: Documentation

   glossary
   narr/install/index
   narr/config/index
   narr/db/index
   narr/cli/index
   narr/email/index
   narr/handlers/index
   narr/providers/index

.. toctree::
   :maxdepth: 1
   :caption: API

   api/wuttjamaican.app
   api/wuttjamaican.auth
   api/wuttjamaican.batch
   api/wuttjamaican.cli
   api/wuttjamaican.cli.base
   api/wuttjamaican.cli.make_appdir
   api/wuttjamaican.cli.make_uuid
   api/wuttjamaican.cli.problems
   api/wuttjamaican.conf
   api/wuttjamaican.db
   api/wuttjamaican.db.conf
   api/wuttjamaican.db.handler
   api/wuttjamaican.db.model
   api/wuttjamaican.db.model.auth
   api/wuttjamaican.db.model.base
   api/wuttjamaican.db.model.batch
   api/wuttjamaican.db.model.upgrades
   api/wuttjamaican.db.sess
   api/wuttjamaican.db.util
   api/wuttjamaican.email
   api/wuttjamaican.enum
   api/wuttjamaican.exc
   api/wuttjamaican.install
   api/wuttjamaican.people
   api/wuttjamaican.problems
   api/wuttjamaican.progress
   api/wuttjamaican.reports
   api/wuttjamaican.testing
   api/wuttjamaican.util
