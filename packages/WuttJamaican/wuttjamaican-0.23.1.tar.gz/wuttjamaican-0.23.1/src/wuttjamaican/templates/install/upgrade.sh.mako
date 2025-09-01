#!/bin/sh -e
<%text>##################################################</%text>
#
# ${app_title} - upgrade script
#
<%text>##################################################</%text>

if [ "$1" = "--verbose" ]; then
    VERBOSE='--verbose'
    QUIET=
else
    VERBOSE=
    QUIET='--quiet'
fi

cd ${envdir}

PIP='bin/pip'
ALEMBIC='bin/alembic'

# upgrade pip and friends
$PIP install $QUIET --disable-pip-version-check --upgrade pip
$PIP install $QUIET --upgrade setuptools wheel

# upgrade app proper
$PIP install $QUIET --upgrade --upgrade-strategy eager '${pypi_name}'

# migrate schema
$ALEMBIC -c app/wutta.conf upgrade heads
