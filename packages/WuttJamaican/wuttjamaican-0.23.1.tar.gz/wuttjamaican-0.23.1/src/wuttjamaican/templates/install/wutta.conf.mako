## -*- mode: conf; -*-

<%text>############################################################</%text>
#
# ${app_title} - base config
#
<%text>############################################################</%text>


<%text>##############################</%text>
# wutta
<%text>##############################</%text>

${self.section_wutta()}

${self.section_wutta_config()}

${self.section_wutta_db()}

${self.section_wutta_mail()}

${self.section_wutta_upgrades()}


<%text>##############################</%text>
# alembic
<%text>##############################</%text>

${self.section_alembic()}


<%text>##############################</%text>
# logging
<%text>##############################</%text>

${self.sectiongroup_logging()}


######################################################################
## section templates below
######################################################################

<%def name="section_wutta()">
[wutta]
app_title = ${app_title}
</%def>

<%def name="section_wutta_config()">
[wutta.config]
#require = /etc/wutta/wutta.conf
configure_logging = true
usedb = true
preferdb = true
</%def>

<%def name="section_wutta_db()">
[wutta.db]
default.url = ${db_url}
## TODO
## versioning.enabled = true
</%def>

<%def name="section_wutta_mail()">
[wutta.mail]

# this is the global email shutoff switch
#send_emails = false

# recommended setup is to always talk to postfix on localhost and then
# it can handle any need complexities, e.g. sending to relay
smtp.server = localhost

# by default only email templates from wuttjamaican are used
templates = wuttjamaican:templates/mail

## TODO
## # this is the "default" email profile, from which all others initially
## # inherit, but most/all profiles will override these values
## default.prefix = [${app_title}]
## default.from = wutta@localhost
## default.to = root@localhost
# nb. in test environment it can be useful to disable by default, and
# then selectively enable certain (e.g. feedback, upgrade) emails
#default.enabled = false
</%def>

<%def name="section_wutta_upgrades()">
## TODO
## [wutta.upgrades]
## command = ${os.path.join(appdir, 'upgrade.sh')} --verbose
## files = ${os.path.join(appdir, 'data', 'upgrades')}
</%def>

<%def name="section_alembic()">
[alembic]
script_location = wuttjamaican.db:alembic
version_locations = ${pkg_name}.db:alembic/versions wuttjamaican.db:alembic/versions
</%def>

<%def name="sectiongroup_logging()">
[loggers]
keys = root, beaker, exc_logger, sqlalchemy, txn

[handlers]
keys = file, console, email

[formatters]
keys = generic, console

[logger_root]
handlers = file, console
level = DEBUG

[logger_beaker]
qualname = beaker
handlers =
level = INFO

[logger_exc_logger]
qualname = exc_logger
handlers = email
level = ERROR

[logger_sqlalchemy]
qualname = sqlalchemy.engine
handlers =
# handlers = file
# level = INFO

[logger_txn]
qualname = txn
handlers =
level = INFO

[handler_file]
class = handlers.RotatingFileHandler
args = (${repr(os.path.join(appdir, 'log', 'wutta.log'))}, 'a', 1000000, 100, 'utf_8')
formatter = generic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
formatter = console
# formatter = generic
# level = INFO
# level = WARNING

[handler_email]
class = handlers.SMTPHandler
args = ('localhost', 'wutta@localhost', ['root@localhost'], "[${app_title}] Logging")
formatter = generic
level = ERROR

[formatter_generic]
format = %(asctime)s %(levelname)-5.5s [%(name)s][%(threadName)s] %(funcName)s: %(message)s
datefmt = %Y-%m-%d %H:%M:%S

[formatter_console]
format = %(levelname)-5.5s [%(name)s][%(threadName)s] %(funcName)s: %(message)s
</%def>
