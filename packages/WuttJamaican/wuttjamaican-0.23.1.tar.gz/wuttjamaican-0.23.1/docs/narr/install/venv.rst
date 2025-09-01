
Virtual Environment
===================

Regardless of platform, you are strongly encouraged to use a
:term:`virtual environment` for your :term:`app`.  This allows you to
experiment with installation without affecting the rest of your
system.

See also the upstream definition for :term:`packaging:Virtual
Environment`.


Choosing a Location
-------------------

It can be helpful to standardize the location of all your virtual
environments regardless of their purpose.  The tool you use to create
a virtual environment may or may not have opinions on where that
should be.

WuttJamaican should not assume anything as far as where the virtual
environments live.  But if you have no preference you might consider:

* Linux - ``/srv/envs``
* Windows - ``C:\envs``

So for instance if you run Linux and make a new virtual environment
named ``poser`` then it would live in ``/srv/envs/poser`` according to
the above.


Creating a Virtual Environment
------------------------------

For our purposes, on Linux you can do this:

.. code-block:: sh

   python3 -m venv /srv/envs/poser

Please also see
:doc:`packaging:guides/installing-using-pip-and-virtual-environments`
in upstream docs.
