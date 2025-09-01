
Architecture
============

:term:`Providers<provider>` are similar to a "plugin" concept in that
multiple providers may be installed by different
:term:`packages<package>`.  But whereas plugins are typically limited
to a particular interface (method list/signatures etc.) a provider can
also "bolt on" entirely new methods which may be used elsewhere in the
:term:`app`.

In that sense providers can perhaps be more accurately thought of as
"extensions" rather than plugins.

Providers may be related to :term:`handlers<handler>` in some cases,
but not all.  But whereas there is only *one handler* configured for a
given portion of the app, multiple providers of the same type would
*all contribute* to the overall app.  In other words they are always
enabled if installed.  (Some may require a :term:`config setting` to
be "active" - but that is up to each provider.)

There can be many "types" of providers; each pertains to a certain
aspect of the overall app.  A given type of provider will apply to a
certain "parent" class.


What a Provider Does
--------------------

Each type of provider pertains to a certain parent class.  The app
itself will define the need for a provider type.

For instance there might be a "dashboard" class which can show various
blocks of info (charts etc.).  Providers might be used to supplement the
parent dashboard class, by adding extra blocks to the display.

But in that example, providers look an awful lot like plugins.

For a better (and real) example see :doc:`app`.
