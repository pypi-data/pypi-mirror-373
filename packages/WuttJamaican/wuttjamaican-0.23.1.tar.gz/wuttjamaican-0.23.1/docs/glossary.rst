.. _glossary:

Glossary
========

.. glossary::
   :sorted:

   ad hoc script
     Python script (text) file used for ad-hoc automation etc.  See
     also :doc:`narr/cli/scripts`.

   app
     Depending on context, may refer to the software application
     overall, or the :term:`app name`, or the :term:`app handler`.

   app database
     The main :term:`database` used by the :term:`app`.  There is
     normally just one database (for simple apps) which uses
     PostgreSQL for the backend.  The app database contains the
     :term:`settings table` as well as :term:`data models <data
     model>`.

     For more info see :doc:`narr/db/app`.

   app dir
     Folder containing app-specific config files, log files, etc.
     Usually this is named ``app`` and is located at the root of the
     virtual environment.

     Can be retrieved via
     :meth:`~wuttjamaican.app.AppHandler.get_appdir()`.

   app enum
      Python module whose namespace contains all the "enum" values
      used by the :term:`app`.  Available on the :term:`app handler`
      as :attr:`~wuttjamaican.app.AppHandler.enum`.

   app handler
     Python object representing the core :term:`handler` for the
     :term:`app`.  There is normally just one "global" app handler;
     see also :doc:`narr/handlers/app`.

   app model
      Python module whose namespace contains all the :term:`data
      models<data model>` used by the :term:`app`.

   app name
     This refers to the canonical name for the underlying app/config
     system.  It does not refer to the overall app; contrast with
     :term:`app title`.

     In most cases (i.e. by default) this will simply be ``wutta``.
     This value affects the naming conventions for config files as
     well as setting names etc.

     The primary reason for this abstraction is so that the Rattail
     Project could leverage the Wutta config logic without having to
     rewrite all config files in the wild.

     See also :attr:`~wuttjamaican.conf.WuttaConfig.appname`.

   app provider
     A :term:`provider` which pertains to the :term:`app handler`.
     See :doc:`narr/providers/app`.

   app title
     Human-friendly name for the :term:`app` (e.g. "Wutta Poser").

     See also the :term:`app name` which serves a very different
     purpose.

   auth handler
      A :term:`handler` responsible for user authentication and
      authorization (login, permissions) and related things.

      See also :class:`~wuttjamaican.auth.AuthHandler`.

   batch
     This refers to a process whereby bulk data operations may be
     performed, with preview and other tools to allow the user to
     refine as needed before "executing" the batch.

     The term "batch" may refer to such a feature overall, or the
     :term:`data model` used, or the specific data for a single batch,
     etc.

     See also :term:`batch handler` and :term:`batch row`, and the
     :class:`~wuttjamaican.db.model.batch.BatchMixin` base class.

   batch handler
     This refers to a :term:`handler` meant to process a given type of
     :term:`batch`.

     There may be multiple handlers registered for a given
     :term:`batch type`, but (usually) only one will be configured for
     use.

   batch row
     A row of data within a :term:`batch`.

     May also refer to the :term:`data model` class used for such a row.

     See also the :class:`~wuttjamaican.db.model.batch.BatchRowMixin`
     base class.

   batch type
     This term is used to distinguish :term:`batches <batch>` according
     to which underlying table is used to store their data, essentially.

     For instance a "pricing batch" would use one table, whereas an
     "inventory batch" would use another.  And each "type" would be
     managed by its own :term:`batch handler`.

     The batch type is set on the model class but is also available on
     the handler:

     * :attr:`wuttjamaican.db.model.batch.BatchMixin.batch_type`
     * :attr:`wuttjamaican.batch.BatchHandler.batch_type`

   command
     A top-level command line interface for the app.  Note that
     top-level commands don't usually "do" anything per se, and are
     mostly a way to group :term:`subcommands<subcommand>`.  See also
     :doc:`narr/cli/index`.

   config
     Depending on context, may refer to any of: :term:`config file`,
     :term:`config object`, :term:`config setting`.  See also
     :doc:`narr/config/index`.

   config extension
      A registered extension for the :term:`config object`.  What
      happens is, a config object is created and then extended by each
      of the registered config extensions.

      The intention is that all config extensions will have been
      applied before the :term:`app handler` is created.

   config file
     A file which contains :term:`config settings<config setting>`.
     See also :doc:`narr/config/files`.

   config object
     Python object representing the full set of :term:`config
     settings<config setting>` for the :term:`app`.  Usually it gets
     some of the settings from :term:`config files<config file>`, but
     it may also get some from the :term:`settings table`.  See also
     :doc:`narr/config/object`.

   config setting
     The value of a setting as obtained from a :term:`config object`.
     Depending on context, sometimes this refers specifically to
     values obtained from the :term:`settings table` as opposed to
     :term:`config file`.  See also :doc:`narr/config/settings`.

   data model
     Usually, a Python class which maps to a :term:`database` table.

     The :term:`app` (assuming it has an :term:`app database`) will
     have an "official" set of data models, represented as the
     :term:`app model`.

   database
     Generally refers to a relational database which may be queried
     using SQL.  More specifically, one supported by `SQLAlchemy`_.

     .. _SQLAlchemy: https://www.sqlalchemy.org

     Most :term:`apps<app>` will have at least one :term:`app
     database`.  See also :doc:`narr/db/index`.

   db handler
     The :term:`handler` responsible for various operations involving
     the :term:`app database` (and possibly other :term:`databases
     <database>`).

     See also the :class:`~wuttjamaican.db.handler.DatabaseHandler`
     base class.

   db session
     The "session" is a SQLAlchemy abstraction for an open database
     connection, essentially.

     For the :term:`app database`, the class used is
     :class:`~wuttjamaican.db.sess.Session`; other databases may use
     different classes.

   email handler
      The :term:`handler` responsible for sending email on behalf of
      the :term:`app`.

      Default is :class:`~wuttjamaican.email.EmailHandler`.

   email key
     String idenfier for a certain :term:`email type`.  Each email key
     must be unique across the app, so the correct template files and
     other settings are used when sending etc.

   email module
     This refers to a Python module which contains :term:`email
     setting` definitions.

   email setting
     This refers to the settings for a particular :term:`email type`,
     i.e. its sender and recipients, subject etc.  So each email type
     has a "collection" of settings, and that collection is referred
     to simply as an "email setting" in the singular.

   email template
      Usually this refers to the HTML or TXT template file, used to
      render the message body when sending an email.

   email type
     The :term:`app` is capable of sending many types of emails,
     e.g. daily reports, alerts of various kinds etc.  Each "type" of
     email then will have its own template(s) and sender/recipient
     settings etc.  See also :term:`email key`.

   entry point
     This refers to a "setuptools-style" entry point specifically,
     which is a mechanism used to register "plugins" and the like.
     This lets the app / config discover features dynamically.  Most
     notably used to register :term:`commands<command>` and
     :term:`subcommands<subcommand>`.

     For more info see the `Python Packaging User Guide`_.

     .. _Python Packaging User Guide: https://packaging.python.org/en/latest/specifications/entry-points/

   handler
     Similar to a "plugin" concept but only *one* handler may be used
     for a given purpose.  See also :doc:`narr/handlers/index`.

   install handler
      The :term:`handler` responsible for installing a new instance of
      the :term:`app`.

      Default is :class:`~wuttjamaican.install.InstallHandler`.

   package
     Generally refers to a proper Python package, i.e. a collection of
     modules etc. which is installed via ``pip``.  See also
     :doc:`narr/install/pkg`.

   problem check
      This refers to a special "report" which runs (usually) on a
      nighty basis.  Such a report is only looking for "problems"
      and if any are found, an email notification is sent.

      Apps can define custom problem checks (based on
      :class:`~wuttjamaican.problems.ProblemCheck`), which can then be
      ran via the :term:`problem handler`.

   problem handler
      The :term:`handler` responsible for finding and reporting on
      "problems" with the data or system.  Most typically this runs
      nightly :term:`checks <problem check>` and will send email if
      problems are found.

      Default handler is
      :class:`~wuttjamaican.problems.ProblemHandler`.

   provider
     Python object which "provides" extra functionality to some
     portion of the :term:`app`.  Similar to a "plugin" concept; see
     :doc:`narr/providers/index`.

   report
     The concept of a report is intentionally vague, in the context of
     WuttJamaican.  Basically it is something which can be "ran"
     (usually with :term:`report params`) to generate a data set.  The
     output can be viewed in the app UI, or it can be saved to file.

     The base class is :class:`~wuttjamaican.reports.Report`.  See
     also :term:`report handler`.

   report handler
     The :term:`handler` responsible for running :term:`reports
     <report>`, for display in app UI or saved to file etc.

     Base class is :class:`~wuttjamaican.reports.ReportHandler`.

   report key
     Unique key which identifies a particular :term:`report`.

   report module
     This refers to a Python module which contains :term:`report`
     definitions.

   report params
     This refers to the input parameters used when running a
     :term:`report`.  It is usually a simple mapping of key/value
     pairs.

   settings table
     Table in the :term:`app database` which is used to store
     :term:`config settings<config setting>`.  See also
     :doc:`narr/config/table`.

   spec
     As the term is used in Wutta Project context, this refers to a
     string designating the import path to a particular object (class,
     function etc.).

     Also the term implies a certain format, namely a dotted module
     path followed by colon (``:``), then object name.

     For instance, ``wuttjamaican.app:AppHandler`` is the spec string
     for the :class:`wuttjamaican.app.AppHandler` class (and note, the
     hyperlink does not use colon, but our "spec" always does).

     See also :meth:`~wuttjamaican.app.AppHandler.load_object()` (on
     the :term:`app handler`) which can return any object from spec.

   subcommand
     A top-level :term:`command` may expose one or more subcommands,
     for the overall command line interface.  Subcommands are usually
     the real workhorse; each can perform a different function with a
     custom arg set.  See also :doc:`narr/cli/index`.

   virtual environment
     This term comes from the broader Python world and refers to an
     isolated way to install :term:`packages<package>`.  See also
     :doc:`narr/install/venv`.
