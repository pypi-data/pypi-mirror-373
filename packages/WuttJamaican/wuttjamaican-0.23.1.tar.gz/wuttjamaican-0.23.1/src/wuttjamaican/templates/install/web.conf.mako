## -*- mode: conf; -*-

<%text>############################################################</%text>
#
# ${app_title} - web app config
#
<%text>############################################################</%text>


<%text>##############################</%text>
# wutta
<%text>##############################</%text>

${self.section_wutta_config()}


<%text>##############################</%text>
# pyramid
<%text>##############################</%text>

${self.section_app_main()}

${self.section_server_main()}


<%text>##############################</%text>
# logging
<%text>##############################</%text>

${self.sectiongroup_logging()}


######################################################################
## section templates below
######################################################################

<%def name="section_wutta_config()">
[wutta.config]
require = %(here)s/wutta.conf
</%def>

<%def name="section_app_main()">
[app:main]
#use = egg:wuttaweb
use = egg:${egg_name}

pyramid.reload_templates = true
pyramid.debug_all = true
pyramid.default_locale_name = en
#pyramid.includes = pyramid_debugtoolbar

beaker.session.type = file
beaker.session.data_dir = %(here)s/cache/sessions/data
beaker.session.lock_dir = %(here)s/cache/sessions/lock
beaker.session.secret = ${beaker_secret}
beaker.session.key = ${beaker_key}

exclog.extra_info = true

# required for wuttaweb
wutta.config = %(__file__)s
</%def>

<%def name="section_server_main()">
[server:main]
use = egg:waitress#main
host = ${pyramid_host}
port = ${pyramid_port}

# NOTE: this is needed for local reverse proxy stuff to work with HTTPS
# https://docs.pylonsproject.org/projects/waitress/en/latest/reverse-proxy.html
# https://docs.pylonsproject.org/projects/waitress/en/latest/arguments.html
trusted_proxy = 127.0.0.1
trusted_proxy_headers = x-forwarded-for x-forwarded-host x-forwarded-proto x-forwarded-port
clear_untrusted_proxy_headers = True

# TODO: leave this empty if proxy serves as root site, e.g. https://wutta.example.com/
# url_prefix =

# TODO: or, if proxy serves as subpath of root site, e.g. https://wutta.example.com/backend/
# url_prefix = /backend
</%def>

<%def name="sectiongroup_logging()">
[handler_console]
level = INFO

[handler_file]
args = (${repr(os.path.join(appdir, 'log', 'web.log'))}, 'a', 1000000, 100, 'utf_8')
</%def>
