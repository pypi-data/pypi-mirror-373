# -*- coding: utf-8; -*-
################################################################################
#
#  WuttJamaican -- Base package for Wutta Framework
#  Copyright © 2023 Lance Edgar
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
WuttJamaican -  app database

For convenience, from this ``wuttjamaican.db`` namespace you can
access the following:

* :class:`~wuttjamaican.db.sess.Session`
* :class:`~wuttjamaican.db.sess.short_session`
* :class:`~wuttjamaican.db.conf.get_setting`
* :class:`~wuttjamaican.db.conf.get_engines`
"""

from .sess import Session, short_session
from .conf import get_setting, get_engines
