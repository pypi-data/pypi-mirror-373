
Package Installation
====================

To install the :term:`package` into your :term:`virtual environment`:

.. code-block:: sh

   pip install WuttJamaican

Note that the above is only for basic config/app system and CLI.  If
you also want an :term:`app database` then add the 'db' extra:

.. code-block:: sh

   pip install WuttJamaican[db]

For more general info see
:doc:`packaging:guides/installing-using-pip-and-virtual-environments`.


Sanity Check
------------

Confirm that worked with:

.. command-output:: pip show WuttJamaican
