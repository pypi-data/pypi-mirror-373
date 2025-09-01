
Sending Email
=============

Here we'll describe enough to get started sending email.


Basics
------

To send an email you (usually) need 3 things:

* key - unique key identifying the type of email
* template - template file to render message body
* context - context dict for template file rendering

And actually the template just needs to exist somewhere it can be
found, but when calling
:meth:`~wuttjamaican.app.AppHandler.send_email()` you only need to
give the key and context::

   app.send_email('poser_alert_foo', {
       'alert_type': 'foo',
       'alert_msg': "foo has unexpected value! or something happened, etc.",
   })

In that example ``alert_type`` and ``alert_msg`` are the context, and
the template file(s) may display either/both however it wants.

If you do not provide all the needed context, you will likely get a
template rendering error.  The only way to know for sure which context
data is needed, is to look at the template file itself.


Email Discovery
---------------

So how does the above work, e.g. how did it find the template?  And
how can you know which are the "possible" email types you can send?

This is covered in more detail in :doc:`custom` but for now we'll
just say:

The template folder(s) must be configured, but otherwise "any email
type key" may be used.  As long as the template(s) is found, the email
can be sent - albeit to global default recipients, unless that is
further configured for the email type.

In other words there is no "central registry" of the possible email
types, per se.  In practice the list of template files, found within
configured template folders, is effectively the list of possible email
types.  (There is no "default template" for sending.)

.. note::

   At this time there are no built-in email templates for
   WuttJamaican.  However there is (at least) one template defined in
   `wuttaweb:email/templates
   <https://forgejo.wuttaproject.org/wutta/wuttaweb/src/branch/master/src/wuttaweb/email/templates>`_.


Email Delivery
--------------

If the email template can be found and rendered, it's time to "really"
send the email.  How does that work?

Various message headers may be specified by caller, but usually they
will be auto-obtained from config.  This includes the sender and
recipients, and subject line.  If neither specifies anything regarding
the current email type, fallback "default" values are used (assuming
those are configured).  This again is explained further in
:doc:`custom`.

So we have a complete message with all headers; the final step is to
send this via SMTP.  While technically this supports sending to an
"external" SMTP server, the suggested use case is to always send to
localhost; to minimize lag and give full flexibility.  (If sending to
localhost you should not need any specific config for that.)

In any case here is sample config if you were to use an external
SMTP server:

.. code-block:: ini

   [wutta.mail]
   smtp.server = smtp.example.com
   smtp.username = mailuser
   smtp.password = mailpass

.. note::

   As of now, TLS is not supported!  Which is because of the preferred
   use of localhost as SMTP server.  Obviously the local MTA software
   (e.g. Postfix) can then send via another relay, and it should
   probably use TLS for that.
