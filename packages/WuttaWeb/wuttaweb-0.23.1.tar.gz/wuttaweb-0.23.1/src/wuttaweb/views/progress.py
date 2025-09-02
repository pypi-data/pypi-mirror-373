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
Progress Views
"""

from wuttaweb.progress import get_progress_session


def progress(request):
    """
    View which returns JSON with current progress status.

    The URL is like ``/progress/XXX`` where ``XXX`` is the "key" to a
    particular progress indicator, tied to a long-running operation.

    This key is used to lookup the progress status within the Beaker
    session storage.  See also
    :class:`~wuttaweb.progress.SessionProgress`.
    """
    key = request.matchdict["key"]
    session = get_progress_session(request, key)

    # session has 'complete' flag set when operation is over
    if session.get("complete"):

        # set a flash msg for user if one is defined.  this is the
        # time to do it since user is about to get redirected.
        msg = session.get("success_msg")
        if msg:
            request.session.flash(msg)

    elif session.get("error"):  # uh-oh

        # set an error flash msg for user.  this is the time to do it
        # since user is about to get redirected.
        msg = session.get("error_msg", "An unspecified error occurred.")
        request.session.flash(msg, "error")

    # nb. we return the session as-is; since it is dict-like (and only
    # contains relevant progress data) it can be used directly for the
    # JSON response context
    return session


def defaults(config, **kwargs):  # pylint: disable=missing-function-docstring
    base = globals()

    progress = kwargs.get(  # pylint: disable=redefined-outer-name
        "progress", base["progress"]
    )
    config.add_route("progress", "/progress/{key}")
    config.add_view(progress, route_name="progress", renderer="json")


def includeme(config):  # pylint: disable=missing-function-docstring
    defaults(config)
