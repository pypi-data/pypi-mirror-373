
Architecture
============

Handlers are similar to a "plugin" concept in that multiple handlers
may be installed e.g. by different packages.  But whereas one might
"enable" multiple plugins, only *one* handler may be used, for a given
purpose.

There can be many "types" of handlers; each is responsible for a
certain aspect of the overall app.  So it can be thought of as,
"*Which* plugin should *handle* this aspect of the app?"


What a Handler Does
-------------------

Each type of handler does something different.  For instance there
might be an "auth handler" responsible for authenticating user
credentials.

The app itself will define the need for a handler.  For instance if a
user login mechanism is needed, then the app might define the "auth
handler" (e.g. ``AuthHandler``) base class, and add a way to locate
and use it at runtime.

Other packages might then also define "auth handlers" derived from the
base class, and perhaps a way for the app to locate them as well.

The app should probably have a way for the "choice" of auth handler to
be configurable, and possibly expose this choice via admin UI.
