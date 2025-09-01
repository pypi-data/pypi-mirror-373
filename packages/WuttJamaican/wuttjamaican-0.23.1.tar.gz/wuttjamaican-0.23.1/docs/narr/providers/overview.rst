
Overview
========

The :term:`provider` concept is a way to "supplement" the main app
logic.  It is different from a :term:`handler` though:

Providers are *more* analagous to "plugins" than are handlers.  For
instance multiple :term:`app providers<app provider>` may be installed
by various packages and *each of these* will supplement the (one and
only) :term:`app handler`.  See also :doc:`arch`.

So far there is only one provider type defined; see :doc:`app`.
