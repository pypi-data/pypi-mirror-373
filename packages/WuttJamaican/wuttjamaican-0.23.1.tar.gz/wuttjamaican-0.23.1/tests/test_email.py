# -*- coding: utf-8; -*-

from email.mime.text import MIMEText
from unittest import TestCase
from unittest.mock import patch, MagicMock

import pytest

from wuttjamaican import email as mod
from wuttjamaican.util import resource_path
from wuttjamaican.exc import ConfigurationError
from wuttjamaican.testing import ConfigTestCase, FileTestCase


class TestEmailSetting(ConfigTestCase):

    def test_constructor(self):
        setting = mod.EmailSetting(self.config)
        self.assertIs(setting.config, self.config)
        self.assertIs(setting.app, self.app)
        self.assertEqual(setting.key, "EmailSetting")

    def test_sample_data(self):
        setting = mod.EmailSetting(self.config)
        self.assertEqual(setting.sample_data(), {})


class TestMessage(FileTestCase):

    def make_message(self, **kwargs):
        return mod.Message(**kwargs)

    def test_get_recips(self):
        msg = self.make_message()

        # set as list
        recips = msg.get_recips(["sally@example.com"])
        self.assertEqual(recips, ["sally@example.com"])

        # set as tuple
        recips = msg.get_recips(("barney@example.com",))
        self.assertEqual(recips, ["barney@example.com"])

        # set as string
        recips = msg.get_recips("wilma@example.com")
        self.assertEqual(recips, ["wilma@example.com"])

        # set as null
        recips = msg.get_recips(None)
        self.assertEqual(recips, [])

        # otherwise error
        self.assertRaises(ValueError, msg.get_recips, {"foo": "foo@example.com"})

    def test_as_string(self):

        # error if no body
        msg = self.make_message()
        self.assertRaises(ValueError, msg.as_string)

        # txt body
        msg = self.make_message(sender="bob@example.com", txt_body="hello world")
        complete = msg.as_string()
        self.assertIn("From: bob@example.com", complete)

        # html body
        msg = self.make_message(
            sender="bob@example.com", html_body="<p>hello world</p>"
        )
        complete = msg.as_string()
        self.assertIn("From: bob@example.com", complete)

        # txt + html body
        msg = self.make_message(
            sender="bob@example.com",
            txt_body="hello world",
            html_body="<p>hello world</p>",
        )
        complete = msg.as_string()
        self.assertIn("From: bob@example.com", complete)

        # html + attachment
        csv_part = MIMEText("foo,bar\n1,2", "csv", "utf_8")
        msg = self.make_message(
            sender="bob@example.com",
            html_body="<p>hello world</p>",
            attachments=[csv_part],
        )
        complete = msg.as_string()
        self.assertIn("Content-Type: multipart/mixed; boundary=", complete)
        self.assertIn('Content-Type: text/csv; charset="utf_8"', complete)

        # error if improper attachment
        csv_path = self.write_file("data.csv", "foo,bar\n1,2")
        msg = self.make_message(
            sender="bob@example.com",
            html_body="<p>hello world</p>",
            attachments=[csv_path],
        )
        self.assertRaises(ValueError, msg.as_string)
        try:
            msg.as_string()
        except ValueError as err:
            self.assertIn("must specify valid MIME attachments", str(err))

        # everything
        msg = self.make_message(
            sender="bob@example.com",
            subject="meeting follow-up",
            to="sally@example.com",
            cc="marketing@example.com",
            bcc="bob@example.com",
            replyto="sales@example.com",
            txt_body="hello world",
            html_body="<p>hello world</p>",
        )
        complete = msg.as_string()
        self.assertIn("From: bob@example.com", complete)
        self.assertIn("Subject: meeting follow-up", complete)
        self.assertIn("To: sally@example.com", complete)
        self.assertIn("Cc: marketing@example.com", complete)
        self.assertIn("Bcc: bob@example.com", complete)
        self.assertIn("Reply-To: sales@example.com", complete)


class mock_foo(mod.EmailSetting):
    default_subject = "MOCK FOO!"

    def sample_data(self):
        return {"foo": "mock"}


class TestEmailHandler(ConfigTestCase):

    def make_handler(self, **kwargs):
        return mod.EmailHandler(self.config, **kwargs)

    def test_constructor_lookups(self):

        # empty lookup paths by default, if no providers
        with patch.object(self.app, "providers", new={}):
            handler = self.make_handler()
        self.assertEqual(handler.txt_templates.directories, [])
        self.assertEqual(handler.html_templates.directories, [])

        # provider may specify paths as list
        providers = {
            "wuttatest": MagicMock(email_templates=["wuttjamaican:email-templates"]),
        }
        with patch.object(self.app, "providers", new=providers):
            handler = self.make_handler()
        path = resource_path("wuttjamaican:email-templates")
        self.assertEqual(handler.txt_templates.directories, [path])
        self.assertEqual(handler.html_templates.directories, [path])

        # provider may specify paths as string
        providers = {
            "wuttatest": MagicMock(email_templates="wuttjamaican:email-templates"),
        }
        with patch.object(self.app, "providers", new=providers):
            handler = self.make_handler()
        path = resource_path("wuttjamaican:email-templates")
        self.assertEqual(handler.txt_templates.directories, [path])
        self.assertEqual(handler.html_templates.directories, [path])

    def test_get_email_modules(self):

        # no providers, no email modules
        with patch.object(self.app, "providers", new={}):
            handler = self.make_handler()
            self.assertEqual(handler.get_email_modules(), [])

        # provider may specify modules as list
        providers = {
            "wuttatest": MagicMock(email_modules=["wuttjamaican.email"]),
        }
        with patch.object(self.app, "providers", new=providers):
            handler = self.make_handler()
            modules = handler.get_email_modules()
            self.assertEqual(len(modules), 1)
            self.assertIs(modules[0], mod)

        # provider may specify modules as string
        providers = {
            "wuttatest": MagicMock(email_modules="wuttjamaican.email"),
        }
        with patch.object(self.app, "providers", new=providers):
            handler = self.make_handler()
            modules = handler.get_email_modules()
            self.assertEqual(len(modules), 1)
            self.assertIs(modules[0], mod)

    def test_get_email_settings(self):

        # no providers, no email settings
        with patch.object(self.app, "providers", new={}):
            handler = self.make_handler()
            self.assertEqual(handler.get_email_settings(), {})

        # provider may define email settings (via modules)
        providers = {
            "wuttatest": MagicMock(email_modules=["tests.test_email"]),
        }
        with patch.object(self.app, "providers", new=providers):
            handler = self.make_handler()
            settings = handler.get_email_settings()
            self.assertEqual(len(settings), 1)
            self.assertIn("mock_foo", settings)

    def test_get_email_setting(self):

        providers = {
            "wuttatest": MagicMock(email_modules=["tests.test_email"]),
        }

        with patch.object(self.app, "providers", new=providers):
            handler = self.make_handler()

            # as instance
            setting = handler.get_email_setting("mock_foo")
            self.assertIsInstance(setting, mod.EmailSetting)
            self.assertIsInstance(setting, mock_foo)

            # as class
            setting = handler.get_email_setting("mock_foo", instance=False)
            self.assertTrue(issubclass(setting, mod.EmailSetting))
            self.assertIs(setting, mock_foo)

    def test_make_message(self):
        handler = self.make_handler()
        msg = handler.make_message()
        self.assertIsInstance(msg, mod.Message)

    def test_make_auto_message(self):
        handler = self.make_handler()

        # # error if default sender not defined
        # self.assertRaises(ConfigurationError, handler.make_auto_message, 'foo')

        # message is empty by default
        msg = handler.make_auto_message("foo")
        self.assertIsInstance(msg, mod.Message)
        self.assertEqual(msg.key, "foo")
        self.assertEqual(msg.sender, "root@localhost")
        self.assertEqual(msg.subject, "Automated message")
        self.assertEqual(msg.to, [])
        self.assertEqual(msg.cc, [])
        self.assertEqual(msg.bcc, [])
        self.assertIsNone(msg.replyto)
        self.assertIsNone(msg.txt_body)
        self.assertIsNone(msg.html_body)

        # override defaults
        self.config.setdefault("wutta.email.default.sender", "bob@example.com")
        self.config.setdefault("wutta.email.default.subject", "Attention required")

        # message is empty by default
        msg = handler.make_auto_message("foo")
        self.assertIsInstance(msg, mod.Message)
        self.assertEqual(msg.key, "foo")
        self.assertEqual(msg.sender, "bob@example.com")
        self.assertEqual(msg.subject, "Attention required")
        self.assertEqual(msg.to, [])
        self.assertEqual(msg.cc, [])
        self.assertEqual(msg.bcc, [])
        self.assertIsNone(msg.replyto)
        self.assertIsNone(msg.txt_body)
        self.assertIsNone(msg.html_body)

        # but if there is a proper email profile configured for key,
        # then we should get back a more complete message
        self.config.setdefault("wutta.email.test_foo.subject", "hello foo")
        self.config.setdefault("wutta.email.test_foo.to", "sally@example.com")
        self.config.setdefault("wutta.email.templates", "tests:email-templates")
        handler = self.make_handler()
        msg = handler.make_auto_message("test_foo")
        self.assertEqual(msg.key, "test_foo")
        self.assertEqual(msg.sender, "bob@example.com")
        self.assertEqual(msg.subject, "hello foo")
        self.assertEqual(msg.to, ["sally@example.com"])
        self.assertEqual(msg.cc, [])
        self.assertEqual(msg.bcc, [])
        self.assertIsNone(msg.replyto)
        self.assertEqual(msg.txt_body, "hello from foo txt template\n")
        self.assertEqual(msg.html_body, "<p>hello from foo html template</p>\n")

        # *some* auto methods get skipped if caller specifies the
        # kwarg at all; others get skipped if kwarg is empty

        # sender
        with patch.object(handler, "get_auto_sender") as get_auto_sender:
            msg = handler.make_auto_message("foo", sender=None)
            get_auto_sender.assert_not_called()
            msg = handler.make_auto_message("foo")
            get_auto_sender.assert_called_once_with("foo")

        # subject
        with patch.object(handler, "get_auto_subject") as get_auto_subject:
            msg = handler.make_auto_message("foo", subject=None)
            get_auto_subject.assert_not_called()
            msg = handler.make_auto_message("foo")
            get_auto_subject.assert_called_once_with("foo", {}, default=None)

        # to
        with patch.object(handler, "get_auto_to") as get_auto_to:
            msg = handler.make_auto_message("foo", to=None)
            get_auto_to.assert_not_called()
            get_auto_to.return_value = None
            msg = handler.make_auto_message("foo")
            get_auto_to.assert_called_once_with("foo")

        # cc
        with patch.object(handler, "get_auto_cc") as get_auto_cc:
            msg = handler.make_auto_message("foo", cc=None)
            get_auto_cc.assert_not_called()
            get_auto_cc.return_value = None
            msg = handler.make_auto_message("foo")
            get_auto_cc.assert_called_once_with("foo")

        # bcc
        with patch.object(handler, "get_auto_bcc") as get_auto_bcc:
            msg = handler.make_auto_message("foo", bcc=None)
            get_auto_bcc.assert_not_called()
            get_auto_bcc.return_value = None
            msg = handler.make_auto_message("foo")
            get_auto_bcc.assert_called_once_with("foo")

        # txt_body
        with patch.object(handler, "get_auto_txt_body") as get_auto_txt_body:
            msg = handler.make_auto_message("foo", txt_body=None)
            get_auto_txt_body.assert_not_called()
            msg = handler.make_auto_message("foo")
            get_auto_txt_body.assert_called_once_with("foo", {})

        # html_body
        with patch.object(handler, "get_auto_html_body") as get_auto_html_body:
            msg = handler.make_auto_message("foo", html_body=None)
            get_auto_html_body.assert_not_called()
            msg = handler.make_auto_message("foo")
            get_auto_html_body.assert_called_once_with("foo", {})

    def test_get_auto_sender(self):
        handler = self.make_handler()

        # basic global default
        self.assertEqual(handler.get_auto_sender("foo"), "root@localhost")

        # can set global default
        self.config.setdefault("wutta.email.default.sender", "bob@example.com")
        self.assertEqual(handler.get_auto_sender("foo"), "bob@example.com")

        # can set for key
        self.config.setdefault("wutta.email.foo.sender", "sally@example.com")
        self.assertEqual(handler.get_auto_sender("foo"), "sally@example.com")

    def test_get_auto_replyto(self):
        handler = self.make_handler()

        # null by default
        self.assertIsNone(handler.get_auto_replyto("foo"))

        # can set global default
        self.config.setdefault("wutta.email.default.replyto", "george@example.com")
        self.assertEqual(handler.get_auto_replyto("foo"), "george@example.com")

        # can set for key
        self.config.setdefault("wutta.email.foo.replyto", "kathy@example.com")
        self.assertEqual(handler.get_auto_replyto("foo"), "kathy@example.com")

    def test_get_auto_subject_template(self):
        handler = self.make_handler()

        # global default
        template = handler.get_auto_subject_template("foo")
        self.assertEqual(template, "Automated message")

        # can configure alternate global default
        self.config.setdefault("wutta.email.default.subject", "Wutta Message")
        template = handler.get_auto_subject_template("foo")
        self.assertEqual(template, "Wutta Message")

        # can configure just for key
        self.config.setdefault("wutta.email.foo.subject", "Foo Message")
        template = handler.get_auto_subject_template("foo")
        self.assertEqual(template, "Foo Message")

        # EmailSetting can provide default subject
        providers = {
            "wuttatest": MagicMock(email_modules=["tests.test_email"]),
        }
        with patch.object(self.app, "providers", new=providers):
            handler = self.make_handler()
            template = handler.get_auto_subject_template("mock_foo")
            self.assertEqual(template, "MOCK FOO!")

            # caller can provide default subject
            template = handler.get_auto_subject_template(
                "mock_foo", default="whatever is clever"
            )
            self.assertEqual(template, "whatever is clever")

    def test_get_auto_subject(self):
        handler = self.make_handler()

        # global default
        subject = handler.get_auto_subject("foo")
        self.assertEqual(subject, "Automated message")

        # can configure alternate global default
        self.config.setdefault("wutta.email.default.subject", "Wutta Message")
        subject = handler.get_auto_subject("foo")
        self.assertEqual(subject, "Wutta Message")

        # caller can provide default subject
        subject = handler.get_auto_subject("foo", default="whatever is clever")
        self.assertEqual(subject, "whatever is clever")

        # can configure just for key
        self.config.setdefault("wutta.email.foo.subject", "Foo Message")
        subject = handler.get_auto_subject("foo")
        self.assertEqual(subject, "Foo Message")

        # proper template is rendered
        self.config.setdefault("wutta.email.bar.subject", "${foo} Message")
        subject = handler.get_auto_subject("bar", {"foo": "FOO"})
        self.assertEqual(subject, "FOO Message")

        # unless we ask it not to
        subject = handler.get_auto_subject("bar", {"foo": "FOO"}, rendered=False)
        self.assertEqual(subject, "${foo} Message")

    def test_get_auto_recips(self):
        handler = self.make_handler()

        # error if bad type requested
        self.assertRaises(ValueError, handler.get_auto_recips, "foo", "doesnotexist")

        # can configure global default
        self.config.setdefault("wutta.email.default.to", "admin@example.com")
        recips = handler.get_auto_recips("foo", "to")
        self.assertEqual(recips, ["admin@example.com"])

        # can configure just for key
        self.config.setdefault("wutta.email.foo.to", "bob@example.com")
        recips = handler.get_auto_recips("foo", "to")
        self.assertEqual(recips, ["bob@example.com"])

    def test_get_auto_body_template(self):
        from mako.template import Template

        handler = self.make_handler()

        # error if bad request
        self.assertRaises(ValueError, handler.get_auto_body_template, "foo", "BADTYPE")

        # empty by default
        template = handler.get_auto_body_template("foo", "txt")
        self.assertIsNone(template)

        # but returns a template if it exists
        providers = {
            "wuttatest": MagicMock(email_templates=["tests:email-templates"]),
        }
        with patch.object(self.app, "providers", new=providers):
            handler = self.make_handler()
        template = handler.get_auto_body_template("test_foo", "txt")
        self.assertIsInstance(template, Template)
        self.assertEqual(template.uri, "test_foo.txt.mako")

    def test_get_auto_txt_body(self):
        handler = self.make_handler()

        # empty by default
        body = handler.get_auto_txt_body("some-random-email")
        self.assertIsNone(body)

        # but returns body if template exists
        providers = {
            "wuttatest": MagicMock(email_templates=["tests:email-templates"]),
        }
        with patch.object(self.app, "providers", new=providers):
            handler = self.make_handler()
        body = handler.get_auto_txt_body("test_foo")
        self.assertEqual(body, "hello from foo txt template\n")

    def test_get_auto_html_body(self):
        handler = self.make_handler()

        # empty by default
        body = handler.get_auto_html_body("some-random-email")
        self.assertIsNone(body)

        # but returns body if template exists
        providers = {
            "wuttatest": MagicMock(email_templates=["tests:email-templates"]),
        }
        with patch.object(self.app, "providers", new=providers):
            handler = self.make_handler()
        body = handler.get_auto_html_body("test_foo")
        self.assertEqual(body, "<p>hello from foo html template</p>\n")

    def test_get_notes(self):
        handler = self.make_handler()

        # null by default
        self.assertIsNone(handler.get_notes("foo"))

        # configured notes
        self.config.setdefault("wutta.email.foo.notes", "hello world")
        self.assertEqual(handler.get_notes("foo"), "hello world")

    def test_is_enabled(self):
        handler = self.make_handler()

        # enabled by default
        self.assertTrue(handler.is_enabled("default"))
        self.assertTrue(handler.is_enabled("foo"))

        # specific type disabled
        self.config.setdefault("wutta.email.foo.enabled", "false")
        self.assertFalse(handler.is_enabled("foo"))

        # default is disabled
        self.assertTrue(handler.is_enabled("bar"))
        self.config.setdefault("wutta.email.default.enabled", "false")
        self.assertFalse(handler.is_enabled("bar"))

    def test_deliver_message(self):
        handler = self.make_handler()

        msg = handler.make_message(sender="bob@example.com", to="sally@example.com")
        with patch.object(msg, "as_string", return_value="msg-str"):

            # no smtp session since sending email is disabled by default
            with patch.object(mod, "smtplib") as smtplib:
                session = MagicMock()
                smtplib.SMTP.return_value = session
                handler.deliver_message(msg)
                smtplib.SMTP.assert_not_called()
                session.login.assert_not_called()
                session.sendmail.assert_not_called()

            # now let's enable sending
            self.config.setdefault("wutta.mail.send_emails", "true")

            # smtp login not attempted by default
            with patch.object(mod, "smtplib") as smtplib:
                session = MagicMock()
                smtplib.SMTP.return_value = session
                handler.deliver_message(msg)
                smtplib.SMTP.assert_called_once_with("localhost")
                session.login.assert_not_called()
                session.sendmail.assert_called_once_with(
                    "bob@example.com", {"sally@example.com"}, "msg-str"
                )

            # but login attempted if config has credentials
            self.config.setdefault("wutta.mail.smtp.username", "bob")
            self.config.setdefault("wutta.mail.smtp.password", "seekrit")
            with patch.object(mod, "smtplib") as smtplib:
                session = MagicMock()
                smtplib.SMTP.return_value = session
                handler.deliver_message(msg)
                smtplib.SMTP.assert_called_once_with("localhost")
                session.login.assert_called_once_with("bob", "seekrit")
                session.sendmail.assert_called_once_with(
                    "bob@example.com", {"sally@example.com"}, "msg-str"
                )

        # error if no sender
        msg = handler.make_message(to="sally@example.com")
        self.assertRaises(ValueError, handler.deliver_message, msg)

        # error if no recips
        msg = handler.make_message(sender="bob@example.com")
        self.assertRaises(ValueError, handler.deliver_message, msg)

        # can set recips as list
        msg = handler.make_message(sender="bob@example.com")
        with patch.object(msg, "as_string", return_value="msg-str"):
            with patch.object(mod, "smtplib") as smtplib:
                session = MagicMock()
                smtplib.SMTP.return_value = session
                handler.deliver_message(msg, recips=["sally@example.com"])
                smtplib.SMTP.assert_called_once_with("localhost")
                session.sendmail.assert_called_once_with(
                    "bob@example.com", {"sally@example.com"}, "msg-str"
                )

        # can set recips as string
        msg = handler.make_message(sender="bob@example.com")
        with patch.object(msg, "as_string", return_value="msg-str"):
            with patch.object(mod, "smtplib") as smtplib:
                session = MagicMock()
                smtplib.SMTP.return_value = session
                handler.deliver_message(msg, recips="sally@example.com")
                smtplib.SMTP.assert_called_once_with("localhost")
                session.sendmail.assert_called_once_with(
                    "bob@example.com", {"sally@example.com"}, "msg-str"
                )

        # can set recips via to
        msg = handler.make_message(sender="bob@example.com", to="sally@example.com")
        with patch.object(msg, "as_string", return_value="msg-str"):
            with patch.object(mod, "smtplib") as smtplib:
                session = MagicMock()
                smtplib.SMTP.return_value = session
                handler.deliver_message(msg)
                smtplib.SMTP.assert_called_once_with("localhost")
                session.sendmail.assert_called_once_with(
                    "bob@example.com", {"sally@example.com"}, "msg-str"
                )

        # can set recips via cc
        msg = handler.make_message(sender="bob@example.com", cc="sally@example.com")
        with patch.object(msg, "as_string", return_value="msg-str"):
            with patch.object(mod, "smtplib") as smtplib:
                session = MagicMock()
                smtplib.SMTP.return_value = session
                handler.deliver_message(msg)
                smtplib.SMTP.assert_called_once_with("localhost")
                session.sendmail.assert_called_once_with(
                    "bob@example.com", {"sally@example.com"}, "msg-str"
                )

        # can set recips via bcc
        msg = handler.make_message(sender="bob@example.com", bcc="sally@example.com")
        with patch.object(msg, "as_string", return_value="msg-str"):
            with patch.object(mod, "smtplib") as smtplib:
                session = MagicMock()
                smtplib.SMTP.return_value = session
                handler.deliver_message(msg)
                smtplib.SMTP.assert_called_once_with("localhost")
                session.sendmail.assert_called_once_with(
                    "bob@example.com", {"sally@example.com"}, "msg-str"
                )

    def test_sending_is_enabled(self):
        handler = self.make_handler()

        # off by default
        self.assertFalse(handler.sending_is_enabled())

        # but can be turned on
        self.config.setdefault("wutta.mail.send_emails", "true")
        self.assertTrue(handler.sending_is_enabled())

    def test_send_email(self):
        handler = self.make_handler()
        with patch.object(handler, "deliver_message") as deliver_message:

            # specify message w/ no body
            msg = handler.make_message()
            self.assertRaises(ValueError, handler.send_email, message=msg)
            self.assertFalse(deliver_message.called)

            # again, but also specify key
            msg = handler.make_message()
            self.assertRaises(ValueError, handler.send_email, "foo", message=msg)
            self.assertFalse(deliver_message.called)

            # specify complete message
            deliver_message.reset_mock()
            msg = handler.make_message(txt_body="hello world")
            handler.send_email(message=msg)
            deliver_message.assert_called_once_with(msg, recips=None)

            # again, but also specify key
            deliver_message.reset_mock()
            msg = handler.make_message(txt_body="hello world")
            handler.send_email("foo", message=msg)
            deliver_message.assert_called_once_with(msg, recips=None)

            # no key, no message
            deliver_message.reset_mock()
            self.assertRaises(ValueError, handler.send_email)

            # auto-create message w/ no template
            deliver_message.reset_mock()
            self.assertRaises(
                RuntimeError, handler.send_email, "foo", sender="foo@example.com"
            )
            self.assertFalse(deliver_message.called)

            # auto create w/ body
            deliver_message.reset_mock()
            handler.send_email("foo", sender="foo@example.com", txt_body="hello world")
            self.assertTrue(deliver_message.called)

            # type is disabled
            deliver_message.reset_mock()
            self.config.setdefault("wutta.email.foo.enabled", False)
            handler.send_email("foo", sender="foo@example.com", txt_body="hello world")
            self.assertFalse(deliver_message.called)

            # default is disabled
            deliver_message.reset_mock()
            handler.send_email("bar", sender="bar@example.com", txt_body="hello world")
            self.assertTrue(deliver_message.called)
            deliver_message.reset_mock()
            self.config.setdefault("wutta.email.default.enabled", False)
            handler.send_email("bar", sender="bar@example.com", txt_body="hello world")
            self.assertFalse(deliver_message.called)
