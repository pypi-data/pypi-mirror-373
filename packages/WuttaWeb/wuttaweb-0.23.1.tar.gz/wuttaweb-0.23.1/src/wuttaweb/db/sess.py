# -*- coding: utf-8; -*-
################################################################################
#
#  wuttaweb -- Web App for Wutta Framework
#  Copyright © 2024 Lance Edgar
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
Database sessions for web app

The web app uses a different database session than other
(e.g. console) apps.  The web session is "registered" to the HTTP
request/response life cycle (aka. transaction) such that the session
is automatically rolled back on error, and automatically committed if
the response is finalized without error.

.. class:: Session

   Primary database session class for the web app.

   Note that you often do not need to "instantiate" this session, and
   can instead call methods directly on the class::

      from wuttaweb.db import Session

      users = Session.query(model.User).all()

   However in certain cases you may still want/need to instantiate it,
   e.g. when passing a "true/normal" session to other logic.  But you
   can always call instance methods as well::

      from wuttaweb.db import Session
      from some_place import some_func

      session = Session()

      # nb. assuming func does not expect a "web" session per se, pass instance
      some_func(session)

      # nb. these behave the same (instance vs. class method)
      users = session.query(model.User).all()
      users = Session.query(model.User).all()
"""

from sqlalchemy import orm
from zope.sqlalchemy.datamanager import register


Session = orm.scoped_session(orm.sessionmaker())

register(Session)
