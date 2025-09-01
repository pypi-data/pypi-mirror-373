
Logging to Email
================

It's possible to configure logging such that when "errors" are logged,
an email can be sent to some recipient(s).

You can set this up however you like of course; see upstream docs for
more info:

* :doc:`python:library/logging`
* :ref:`python:smtp-handler`

But the example shown below does as follows:

* root logger is DEBUG+ and uses 3 handlers: file, console, email

* file handler

  * writes to ``app/log/wutta.log`` (you should specify absolute path instead)

  * will auto-rotate log file when size reaches 10MB

  * uses "generic" entry formatter

* console handler

  * writes to STDERR for the current process

  * writes only INFO+ entries (so no DEBUG)

  * uses "console" entry formatter

* email handler

  * writes only ERROR+ entries (so no DEBUG, INFO or WARNING)

  * email is From: sender and To: recip(s) with Subject: as shown

  * uses "generic" entry formatter (for message body)

.. note::

   This will *not* send email when "uncaught exceptions" occur.  This
   will only send email when an error is *logged*.  For example::

      import logging

      log = logging.getLogger(__name__)

      log.debug("do not email this")
      log.info("nor this")
      log.warning("nor this")

      log.error("but *do* email this")

      try:
          raise RuntimeError
      except:
          log.exception("this also gets emailed")

      # nb. no email is sent *here*, although possibly further up the
      # stack another try/except block could be setup to log uncaught
      # errors, in which case email may still be sent.
      raise RuntimeError("this will just raise up the stack")

Now here is the example, which can be added to a normal :term:`config
file` (modifying as needed):

.. code-block:: ini

   [loggers]
   keys = root

   [handlers]
   keys = file, console, email

   [formatters]
   keys = generic, console

   [logger_root]
   handlers = file, console, email
   level = DEBUG

   [handler_file]
   class = handlers.RotatingFileHandler
   args = ('app/log/wutta.log', 'a', 1000000, 100, 'utf_8')
   formatter = generic

   [handler_console]
   class = StreamHandler
   args = (sys.stderr,)
   formatter = console
   level = INFO

   [handler_email]
   class = handlers.SMTPHandler
   args = ('localhost', 'poser@localhost', ['root@localhost', 'other@localhost'], "[Poser] Logging")
   formatter = generic
   level = ERROR

   [formatter_generic]
   format = %(asctime)s %(levelname)-5.5s [%(name)s][%(threadName)s] %(funcName)s: %(message)s
   datefmt = %Y-%m-%d %H:%M:%S

   [formatter_console]
   format = %(levelname)-5.5s [%(name)s][%(threadName)s] %(funcName)s: %(message)s
