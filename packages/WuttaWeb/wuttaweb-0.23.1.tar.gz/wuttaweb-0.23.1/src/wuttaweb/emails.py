# -*- coding: utf-8; -*-
################################################################################
#
#  wuttaweb -- Web App for Wutta Framework
#  Copyright © 2024-2025 Lance Edgar
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
:term:`Email Settings <email setting>` for WuttaWeb
"""

from wuttjamaican.email import EmailSetting


class feedback(EmailSetting):  # pylint: disable=invalid-name,too-few-public-methods
    """
    Sent when user submits feedback via the web app.
    """

    default_subject = "User Feedback"

    def sample_data(self):  # pylint: disable=empty-docstring
        """ """
        model = self.app.model
        person = model.Person(full_name="Barney Rubble")
        user = model.User(username="barney", person=person)
        return {
            "user": user,
            "user_name": str(person),
            "user_url": "#",
            "referrer": "http://example.com/",
            "client_ip": "127.0.0.1",
            "message": "This app is cool but needs a new feature.\n\nAllow me to describe...",
        }
