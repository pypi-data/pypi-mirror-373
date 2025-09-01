
Custom Emails
=============

It is fairly straightforward to add a new type of email for your app
to send.


Configure Template Dir
----------------------

Your project should contain a folder dedicated to email templates;
these would be committed to your repo as for other project files.
This is often ``email/templates`` or ``templates/email`` under the
package root.

Also the app config must include this path for the email templates
setting.  The order matters here as the first template found via
lookup will be used, for a given key (and content-type).  To include
"Poser" as well as built-in WuttaWeb template dirs:

.. code-block:: ini

   [wutta.email]
   templates =
       poser:templates/email
       wuttaweb:email/templates

Often you can set this in your :term:`config extension` instead of
needing to set it in the config file::

    from wuttjamaican.conf import WuttaConfigExtension

    class PoserConfigExtension(WuttaConfigExtension):

        def configure(self, config):
            config.setdefault('wutta.email.templates',
                              'poser:templates/email wuttaweb:email/templates')

However the config file value, if set, will override the extension
default.


Create the Template
-------------------

Now that you have a configured template folder, create the template
file(s) within it.  Each type of email is expected to have templates
for one or both of the ``text/plain`` and ``text/html`` content-types
(using ``txt`` and ``html`` as shorthand name, respectively).

Template files must use the :doc:`Mako template language <mako:index>`
and be named based on the :attr:`~wuttjamaican.email.Message.key` for
the email type, as well as content-type.

Therefore a new email of type ``poser_alert_foo`` would need one or
both of these defined:

* ``poser_alert_foo.html.mako``
* ``poser_alert_foo.txt.mako``

It is generally a good idea to create both templates but for internal
emails, it is often sufficient to define only the HTML template.  And
styles for email messages are notoriously wonky but again, for
internal use one need not worry about that so much.

Keep in mind, any context you wish to reference within the template,
must be provided by caller when sending email.

.. note::

   At this time there are no built-in email templates for
   WuttJamaican.  However there is (at least) one template defined in
   `wuttaweb:email/templates
   <https://forgejo.wuttaproject.org/wutta/wuttaweb/src/branch/master/src/wuttaweb/email/templates>`_
   which you can reference as a real example.


Configure Sending
-----------------

With template file in the right place, your email can already be used.
However it would be sent only to the (app-wide) "default" recipients,
and with generic subject line.

To fix that you can add to your config file, again based on your email
key:

.. code-block:: ini

   [wutta.email]
   poser_alert_foo.subject = HIGH ALERT TYPE ${alert_type.upper()}
   poser_alert_foo.sender = poser@example.com
   poser_alert_foo.to = alert-monitor@example.com
   poser_alert_foo.cc = admin@example.com

Note the subject line can be a Mako template string, referencing the
template context etc.


Test Sending
------------

Now you should be all set.  When sending the email, you must provide
any context which may be needed for the template rendering.  Assuming
you have that, call :meth:`~wuttjamaican.app.AppHandler.send_email()`
on your :term:`app handler`, giving it key and context::

   app.send_email('poser_alert_foo', {
       'alert_type': 'foo',
       'alert_msg': "foo has unexpected value! or something happened, etc.",
   })
