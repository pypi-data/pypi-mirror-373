# -*- coding: utf-8; -*-
################################################################################
#
#  WuttJamaican -- Base package for Wutta Framework
#  Copyright © 2023-2025 Lance Edgar
#
#  This file is part of Wutta Framework.
#
#  Wutta Framework is free software: you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option) any
#  later version.
#
#  Wutta Framework is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#
#  You should have received a copy of the GNU General Public License along with
#  Wutta Framework.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Email Handler
"""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from mako.lookup import TemplateLookup
from mako.template import Template
from mako.exceptions import TopLevelLookupException

from wuttjamaican.app import GenericHandler
from wuttjamaican.util import resource_path


log = logging.getLogger(__name__)


class EmailSetting:  # pylint: disable=too-few-public-methods
    """
    Base class for all :term:`email settings <email setting>`.

    Each :term:`email type` which needs to have settings exposed
    e.g. for editing, should define a subclass within the appropriate
    :term:`email module`.

    The name of each subclass should match the :term:`email key` which
    it represents.  For instance::

       from wuttjamaican.email import EmailSetting

       class poser_alert_foo(EmailSetting):
           \"""
           Sent when something happens that we think deserves an alert.
           \"""

           default_subject = "Something happened!"

           def sample_data(self):
               return {
                   'foo': 1234,
                   'msg': "Something happened, thought you should know.",
               }

       # (and elsewhere..)
       app.send_email('poser_alert_foo', {
           'foo': 5678,
           'msg': "Can't take much more, she's gonna blow!",
       })

    Defining a subclass for each email type can be a bit tedious, so
    why do it?  In fact there is no need, if you just want to *send*
    emails.

    The purpose of defining a subclass for each email type is 2-fold,
    but really the answer is "for maintenance sake" -

    * gives the app a way to discover all emails, so settings for each
      can be exposed for editing
    * allows for hard-coded sample context which can be used to render
      templates for preview

    .. attribute:: default_subject

       Default :attr:`Message.subject` for the email, if none is
       configured.

       This is technically a Mako template string, so it will be
       rendered with the email context.  But in most cases that
       feature can be ignored, and this will be a simple string.
    """

    default_subject = None

    def __init__(self, config):
        self.config = config
        self.app = config.get_app()
        self.key = self.__class__.__name__

    def sample_data(self):
        """
        Should return a dict with sample context needed to render the
        :term:`email template` for message body.  This can be used to
        show a "preview" of the email.
        """
        return {}


class Message:  # pylint: disable=too-many-instance-attributes
    """
    Represents an email message to be sent.

    :param to: Recipient(s) for the message.  This may be either a
       string, or list of strings.  If a string, it will be converted
       to a list since that is how the :attr:`to` attribute tracks it.
       Similar logic is used for :attr:`cc` and :attr:`bcc`.

    All attributes shown below may also be specified via constructor.

    .. attribute:: key

       Unique key indicating the "type" of message.  An "ad-hoc"
       message created arbitrarily may not have/need a key; however
       one created via
       :meth:`~wuttjamaican.email.EmailHandler.make_auto_message()`
       will always have a key.

       This key is not used for anything within the ``Message`` class
       logic.  It is used by
       :meth:`~wuttjamaican.email.EmailHandler.make_auto_message()`
       when constructing the message, and the key is set on the final
       message only as a reference.

    .. attribute:: sender

       Sender (``From:``) address for the message.

    .. attribute:: subject

       Subject text for the message.

    .. attribute:: to

       List of ``To:`` recipients for the message.

    .. attribute:: cc

       List of ``Cc:`` recipients for the message.

    .. attribute:: bcc

       List of ``Bcc:`` recipients for the message.

    .. attribute:: replyto

       Optional reply-to (``Reply-To:``) address for the message.

    .. attribute:: txt_body

       String with the ``text/plain`` body content.

    .. attribute:: html_body

       String with the ``text/html`` body content.

    .. attribute:: attachments

       List of file attachments for the message.
    """

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        key=None,
        sender=None,
        subject=None,
        to=None,
        cc=None,
        bcc=None,
        replyto=None,
        txt_body=None,
        html_body=None,
        attachments=None,
    ):
        self.key = key
        self.sender = sender
        self.subject = subject
        self.to = self.get_recips(to)
        self.cc = self.get_recips(cc)
        self.bcc = self.get_recips(bcc)
        self.replyto = replyto
        self.txt_body = txt_body
        self.html_body = html_body
        self.attachments = attachments or []

    def get_recips(self, value):  # pylint: disable=empty-docstring
        """ """
        if value:
            if isinstance(value, str):
                value = [value]
            if not isinstance(value, (list, tuple)):
                raise ValueError("must specify a string, tuple or list value")
        else:
            value = []
        return list(value)

    def as_string(self):
        """
        Returns the complete message as string.  This is called from
        within
        :meth:`~wuttjamaican.email.EmailHandler.deliver_message()` to
        obtain the SMTP payload.
        """
        msg = None

        if self.txt_body and self.html_body:
            txt = MIMEText(self.txt_body, _charset="utf_8")
            html = MIMEText(self.html_body, _subtype="html", _charset="utf_8")
            msg = MIMEMultipart(_subtype="alternative", _subparts=[txt, html])

        elif self.txt_body:
            msg = MIMEText(self.txt_body, _charset="utf_8")

        elif self.html_body:
            msg = MIMEText(self.html_body, "html", _charset="utf_8")

        if not msg:
            raise ValueError("message has no body parts")

        if self.attachments:
            for attachment in self.attachments:
                if isinstance(attachment, str):
                    raise ValueError(
                        "must specify valid MIME attachments; this class cannot "
                        "auto-create them from file path etc."
                    )
            msg = MIMEMultipart(_subtype="mixed", _subparts=[msg] + self.attachments)

        msg["Subject"] = self.subject
        msg["From"] = self.sender

        for addr in self.to:
            msg["To"] = addr
        for addr in self.cc:
            msg["Cc"] = addr
        for addr in self.bcc:
            msg["Bcc"] = addr

        if self.replyto:
            msg.add_header("Reply-To", self.replyto)

        return msg.as_string()


class EmailHandler(GenericHandler):  # pylint: disable=too-many-public-methods
    """
    Base class and default implementation for the :term:`email
    handler`.

    Responsible for sending email messages on behalf of the
    :term:`app`.

    You normally would not create this directly, but instead call
    :meth:`~wuttjamaican.app.AppHandler.get_email_handler()` on your
    :term:`app handler`.
    """

    # nb. this is fallback/default subject for auto-message
    universal_subject = "Automated message"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # prefer configured list of template lookup paths, if set
        templates = self.config.get_list(f"{self.config.appname}.email.templates")
        if not templates:
            # otherwise use all available paths, from app providers
            available = []
            for provider in self.app.providers.values():
                if hasattr(provider, "email_templates"):
                    templates = provider.email_templates
                    if isinstance(templates, str):
                        templates = [templates]
                    if templates:
                        available.extend(templates)
            templates = available

        # convert all to true file paths
        if templates:
            templates = [resource_path(p) for p in templates]

        # will use these lookups from now on
        self.txt_templates = TemplateLookup(directories=templates)
        self.html_templates = TemplateLookup(
            directories=templates,
            # nb. escape HTML special chars
            # TODO: sounds great but i forget why?
            default_filters=["h"],
        )

    def get_email_modules(self):
        """
        Returns a list of all known :term:`email modules <email
        module>`.

        This will discover all email modules exposed by the
        :term:`app`, and/or its :term:`providers <provider>`.

        Calls
        :meth:`~wuttjamaican.app.GenericHandler.get_provider_modules()`
        under the hood, for ``email`` module type.
        """
        return self.get_provider_modules("email")

    def get_email_settings(self):
        """
        Returns a dict of all known :term:`email settings <email
        setting>`, keyed by :term:`email key`.

        This calls :meth:`get_email_modules()` and for each module, it
        discovers all the email settings it contains.
        """
        if "email_settings" not in self.classes:
            self.classes["email_settings"] = {}
            for module in self.get_email_modules():
                for name in dir(module):
                    obj = getattr(module, name)
                    if (
                        isinstance(obj, type)
                        and obj is not EmailSetting
                        and issubclass(obj, EmailSetting)
                    ):
                        self.classes["email_settings"][obj.__name__] = obj

        return self.classes["email_settings"]

    def get_email_setting(self, key, instance=True):
        """
        Retrieve the :term:`email setting` for the given :term:`email
        key` (if it exists).

        :param key: Key for the :term:`email type`.

        :param instance: Whether to return the class, or an instance.

        :returns: :class:`EmailSetting` class or instance, or ``None``
           if the setting could not be found.
        """
        settings = self.get_email_settings()
        if key in settings:
            setting = settings[key]
            if instance:
                setting = setting(self.config)
            return setting
        return None

    def make_message(self, **kwargs):
        """
        Make and return a new email message.

        This is the "raw" factory which is simply a wrapper around the
        class constructor.  See also :meth:`make_auto_message()`.

        :returns: :class:`~wuttjamaican.email.Message` object.
        """
        return Message(**kwargs)

    def make_auto_message(self, key, context=None, default_subject=None, **kwargs):
        """
        Make a new email message using config to determine its
        properties, and auto-generating body from a template.

        Once everything has been collected/prepared,
        :meth:`make_message()` is called to create the final message,
        and that is returned.

        :param key: Unique key for this particular "type" of message.
           This key is used as a prefix for all config settings and
           template names pertinent to the message.

        :param context: Context dict used to render template(s) for
           the message.

        :param default_subject: Optional :attr:`~Message.subject`
           template/string to use, if config does not specify one.

        :param \\**kwargs: Any remaining kwargs are passed as-is to
           :meth:`make_message()`.  More on this below.

        :returns: :class:`~wuttjamaican.email.Message` object.

        This method may invoke some others, to gather the message
        attributes.  Each will check config, or render a template, or
        both.  However if a particular attribute is provided by the
        caller, the corresponding "auto" method is skipped.

        * :meth:`get_auto_sender()`
        * :meth:`get_auto_subject()`
        * :meth:`get_auto_to()`
        * :meth:`get_auto_cc()`
        * :meth:`get_auto_bcc()`
        * :meth:`get_auto_txt_body()`
        * :meth:`get_auto_html_body()`
        """
        context = context or {}
        kwargs["key"] = key
        if "sender" not in kwargs:
            kwargs["sender"] = self.get_auto_sender(key)
        if "subject" not in kwargs:
            kwargs["subject"] = self.get_auto_subject(
                key, context, default=default_subject
            )
        if "to" not in kwargs:
            kwargs["to"] = self.get_auto_to(key)
        if "cc" not in kwargs:
            kwargs["cc"] = self.get_auto_cc(key)
        if "bcc" not in kwargs:
            kwargs["bcc"] = self.get_auto_bcc(key)
        if "txt_body" not in kwargs:
            kwargs["txt_body"] = self.get_auto_txt_body(key, context)
        if "html_body" not in kwargs:
            kwargs["html_body"] = self.get_auto_html_body(key, context)
        return self.make_message(**kwargs)

    def get_auto_sender(self, key):
        """
        Returns automatic
        :attr:`~wuttjamaican.email.Message.sender` address for a
        message, as determined by config.
        """
        # prefer configured sender specific to key
        sender = self.config.get(f"{self.config.appname}.email.{key}.sender")
        if sender:
            return sender

        # fall back to global default
        return self.config.get(
            f"{self.config.appname}.email.default.sender", default="root@localhost"
        )

    def get_auto_replyto(self, key):
        """
        Returns automatic :attr:`~wuttjamaican.email.Message.replyto`
        address for a message, as determined by config.
        """
        # prefer configured replyto specific to key
        replyto = self.config.get(f"{self.config.appname}.email.{key}.replyto")
        if replyto:
            return replyto

        # fall back to global default, if present
        return self.config.get(f"{self.config.appname}.email.default.replyto")

    def get_auto_subject(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self, key, context=None, rendered=True, setting=None, default=None
    ):
        """
        Returns automatic :attr:`~wuttjamaican.email.Message.subject`
        line for a message, as determined by config.

        This calls :meth:`get_auto_subject_template()` and then
        (usually) renders the result using the given context.

        :param key: Key for the :term:`email type`.

        :param context: Dict of context for rendering the subject
           template, if applicable.

        :param rendered: If this is ``False``, the "raw" subject
           template will be returned, instead of the final/rendered
           subject text.

        :param setting: Optional :class:`EmailSetting` class or
           instance.  This is passed along to
           :meth:`get_auto_subject_template()`.

        :param default: Default subject to use if none is configured.

        :returns: Final subject text, either "raw" or rendered.
        """
        template = self.get_auto_subject_template(key, setting=setting, default=default)
        if not rendered:
            return template

        context = context or {}
        return Template(template).render(**context)

    def get_auto_subject_template(self, key, setting=None, default=None):
        """
        Returns the template string to use for automatic subject line
        of a message, as determined by config.

        In many cases this will be a simple string and not a
        "template" per se; however it is still treated as a template.

        The template returned from this method is used to render the
        final subject line in :meth:`get_auto_subject()`.

        :param key: Key for the :term:`email type`.

        :param setting: Optional :class:`EmailSetting` class or
           instance.  This may be used to determine the "default"
           subject if none is configured.  You can specify this as an
           optimization; otherwise it will be fetched if needed via
           :meth:`get_email_setting()`.

        :param default: Default subject to use if none is configured.

        :returns: Final subject template, as raw text.
        """
        # prefer configured subject specific to key
        template = self.config.get(f"{self.config.appname}.email.{key}.subject")
        if template:
            return template

        # or use caller-specified default, if applicable
        if default:
            return default

        # or subject from email setting, if defined
        if not setting:
            setting = self.get_email_setting(key)
        if setting and setting.default_subject:
            return setting.default_subject

        # fall back to global default
        return self.config.get(
            f"{self.config.appname}.email.default.subject",
            default=self.universal_subject,
        )

    def get_auto_to(self, key):
        """
        Returns automatic :attr:`~wuttjamaican.email.Message.to`
        recipient address(es) for a message, as determined by config.
        """
        return self.get_auto_recips(key, "to")

    def get_auto_cc(self, key):
        """
        Returns automatic :attr:`~wuttjamaican.email.Message.cc`
        recipient address(es) for a message, as determined by config.
        """
        return self.get_auto_recips(key, "cc")

    def get_auto_bcc(self, key):
        """
        Returns automatic :attr:`~wuttjamaican.email.Message.bcc`
        recipient address(es) for a message, as determined by config.
        """
        return self.get_auto_recips(key, "bcc")

    def get_auto_recips(self, key, typ):  # pylint: disable=empty-docstring
        """ """
        typ = typ.lower()
        if typ not in ("to", "cc", "bcc"):
            raise ValueError("requested type not supported")

        # prefer configured recips specific to key
        recips = self.config.get_list(f"{self.config.appname}.email.{key}.{typ}")
        if recips:
            return recips

        # fall back to global default
        return self.config.get_list(
            f"{self.config.appname}.email.default.{typ}", default=[]
        )

    def get_auto_txt_body(self, key, context=None):
        """
        Returns automatic :attr:`~wuttjamaican.email.Message.txt_body`
        content for a message, as determined by config.  This renders
        a template with the given context.
        """
        template = self.get_auto_body_template(key, "txt")
        if template:
            context = context or {}
            return template.render(**context)
        return None

    def get_auto_html_body(self, key, context=None):
        """
        Returns automatic
        :attr:`~wuttjamaican.email.Message.html_body` content for a
        message, as determined by config.  This renders a template
        with the given context.
        """
        template = self.get_auto_body_template(key, "html")
        if template:
            context = context or {}
            return template.render(**context)
        return None

    def get_auto_body_template(self, key, mode):  # pylint: disable=empty-docstring
        """ """
        mode = mode.lower()
        if mode == "txt":
            templates = self.txt_templates
        elif mode == "html":
            templates = self.html_templates
        else:
            raise ValueError("requested mode not supported")

        try:
            return templates.get_template(f"{key}.{mode}.mako")
        except TopLevelLookupException:
            pass
        return None

    def get_notes(self, key):
        """
        Returns configured "notes" for the given :term:`email key`.

        :param key: Key for the :term:`email type`.

        :returns: Notes as string if found; otherwise ``None``.
        """
        return self.config.get(f"{self.config.appname}.email.{key}.notes")

    def is_enabled(self, key):
        """
        Returns flag indicating whether the given email type is
        "enabled" - i.e.  whether it should ever be sent out (enabled)
        or always suppressed (disabled).

        All email types are enabled by default, unless config says
        otherwise; e.g. to disable ``foo`` emails:

        .. code-block:: ini

           [wutta.email]

           # nb. this is fallback if specific type is not configured
           default.enabled = true

           # this disables 'foo' but e.g 'bar' is still enabled per default above
           foo.enabled = false

        In a development setup you may want a reverse example, where
        all emails are disabled by default but you can turn on just
        one type for testing:

        .. code-block:: ini

           [wutta.email]

           # do not send any emails unless explicitly enabled
           default.enabled = false

           # turn on 'bar' for testing
           bar.enabled = true

        See also :meth:`sending_is_enabled()` which is more of a
        master shutoff switch.

        :param key: Unique identifier for the email type.

        :returns: True if this email type is enabled, otherwise false.
        """
        for k in set([key, "default"]):
            enabled = self.config.get_bool(f"{self.config.appname}.email.{k}.enabled")
            if enabled is not None:
                return enabled
        return True

    def deliver_message(self, message, sender=None, recips=None):
        """
        Deliver a message via SMTP smarthost.

        :param message: Either a :class:`~wuttjamaican.email.Message`
           object or similar, or a string representing the complete
           message to be sent as-is.

        :param sender: Optional sender address to use for delivery.
           If not specified, will be read from ``message``.

        :param recips: Optional recipient address(es) for delivery.
           If not specified, will be read from ``message``.

        A general rule here is that you can either provide a proper
        :class:`~wuttjamaican.email.Message` object, **or** you *must*
        provide ``sender`` and ``recips``.  The logic is not smart
        enough (yet?) to parse sender/recips from a simple string
        message.

        Note also, this method does not (yet?) have robust error
        handling, so if an error occurs with the SMTP session, it will
        simply raise to caller.

        :returns: ``None``
        """
        if not sender:
            sender = message.sender
            if not sender:
                raise ValueError("no sender identified for message delivery")

        if not recips:
            recips = set()
            if message.to:
                recips.update(message.to)
            if message.cc:
                recips.update(message.cc)
            if message.bcc:
                recips.update(message.bcc)
        elif isinstance(recips, str):
            recips = [recips]

        recips = set(recips)
        if not recips:
            raise ValueError("no recipients identified for message delivery")

        if not isinstance(message, str):
            message = message.as_string()

        # get smtp info
        server = self.config.get(
            f"{self.config.appname}.mail.smtp.server", default="localhost"
        )
        username = self.config.get(f"{self.config.appname}.mail.smtp.username")
        password = self.config.get(f"{self.config.appname}.mail.smtp.password")

        # make sure sending is enabled
        log.debug("sending email from %s; to %s", sender, recips)
        if not self.sending_is_enabled():
            log.debug("nevermind, config says no emails")
            return

        # smtp connect
        session = smtplib.SMTP(server)
        if username and password:
            session.login(username, password)

        # smtp send
        session.sendmail(sender, recips, message)
        session.quit()
        log.debug("email was sent")

    def sending_is_enabled(self):
        """
        Returns boolean indicating if email sending is enabled.

        Set this flag in config like this:

        .. code-block:: ini

           [wutta.mail]
           send_emails = true

        Note that it is OFF by default.
        """
        return self.config.get_bool(
            f"{self.config.appname}.mail.send_emails", default=False
        )

    def send_email(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self, key=None, context=None, message=None, sender=None, recips=None, **kwargs
    ):
        """
        Send an email message.

        This method can send a message you provide, or it can
        construct one automatically from key / config / templates.

        The most common use case is assumed to be the latter, where
        caller does not provide the message proper, but specifies key
        and context so the message is auto-created.  In that case this
        method will also check :meth:`is_enabled()` and skip the
        sending if that returns false.

        :param key: When auto-creating a message, this is the
           :term:`email key` identifying the type of email to send.
           Used to lookup config settings and template files.

        :param context: Context dict for rendering automatic email
           template(s).

        :param message: Optional pre-built message instance, to send
           as-is.  If specified, nothing about the message will be
           auto-assigned from config.

        :param sender: Optional sender address for the
           message/delivery.

           If ``message`` is not provided, then the ``sender`` (if
           provided) will also be used when constructing the
           auto-message (i.e. to set the ``From:`` header).

           In any case if ``sender`` is provided, it will be used for
           the actual SMTP delivery.

        :param recips: Optional list of recipient addresses for
           delivery.  If not specified, will be read from the message
           itself (after auto-generating it, if applicable).

           .. note::

              This param does not affect an auto-generated message; it
              is used for delivery only.  As such it must contain
              *all* true recipients.

              If you provide the ``message`` but not the ``recips``,
              the latter will be read from message headers: ``To:``,
              ``Cc:`` and ``Bcc:``

              If you want an auto-generated message but also want to
              override various recipient headers, then you must
              provide those explicitly::

                 context = {'data': [1, 2, 3]}
                 app.send_email('foo', context, to='me@example.com', cc='bobby@example.com')

        :param \\**kwargs: Any remaining kwargs are passed along to
           :meth:`make_auto_message()`.  So, not used if you provide
           the ``message``.
        """
        if key and not self.is_enabled(key):
            log.debug("skipping disabled email: %s", key)
            return

        if message is None:
            if not key:
                raise ValueError("must specify email key (and/or message object)")

            # auto-create message from key + context
            if sender:
                kwargs["sender"] = sender
            message = self.make_auto_message(key, context or {}, **kwargs)
            if not (message.txt_body or message.html_body):
                raise RuntimeError(
                    f"message (type: {key}) has no body - "
                    "perhaps template file not found?"
                )

        if not (message.txt_body or message.html_body):
            if key:
                msg = f"message (type: {key}) has no body content"
            else:
                msg = "message has no body content"
            raise ValueError(msg)

        self.deliver_message(message, recips=recips)
