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
Progress Indicators
"""

from wuttjamaican.progress import ProgressBase

from beaker.session import Session as BeakerSession


def get_basic_session(request, **kwargs):
    """
    Create/get a "basic" Beaker session object.
    """
    kwargs["use_cookies"] = False
    return BeakerSession(request, **kwargs)


def get_progress_session(request, key, **kwargs):
    """
    Create/get a Beaker session object, to be used for progress.
    """
    kwargs["id"] = f"{request.session.id}.progress.{key}"
    return get_basic_session(request, **kwargs)


class SessionProgress(ProgressBase):  # pylint: disable=too-many-instance-attributes
    """
    Progress indicator which uses Beaker session storage to track
    current status.

    This is a subclass of
    :class:`wuttjamaican:wuttjamaican.progress.ProgressBase`.

    A view callable can create one of these, and then pass it into
    :meth:`~wuttjamaican.app.AppHandler.progress_loop()` or similar.

    As the loop updates progress along the way, this indicator will
    update the Beaker session to match.

    Separately then, the client side can send requests for the
    :func:`~wuttaweb.views.progress.progress()` view, to fetch current
    status out of the Beaker session.

    :param request: Current :term:`request` object.

    :param key: Unique key for this progress indicator.  Used to
       distinguish progress indicators in the Beaker session.

    Note that in addition to
    :meth:`~wuttjamaican:wuttjamaican.progress.ProgressBase.update()`
    and
    :meth:`~wuttjamaican:wuttjamaican.progress.ProgressBase.finish()`
    this progres class has some extra attributes and methods:

    .. attribute:: success_msg

       Optional message to display to the user (via session flash)
       when the operation completes successfully.

    .. attribute:: success_url

       URL to which user should be redirected, once the operation
       completes.

    .. attribute:: error_url

       URL to which user should be redirected, if the operation
       encounters an error.  If not specified, will fall back to
       :attr:`success_url`.
    """

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments,super-init-not-called
        self, request, key, success_msg=None, success_url=None, error_url=None
    ):
        self.request = request
        self.config = self.request.wutta_config
        self.app = self.config.get_app()
        self.key = key
        self.success_msg = success_msg
        self.success_url = success_url
        self.error_url = error_url or self.success_url
        self.session = get_progress_session(request, key)
        self.clear()

    def __call__(self, message, maximum):
        self.clear()
        self.session["message"] = message
        self.session["maximum"] = maximum
        self.session["maximum_display"] = f"{maximum:,d}"
        self.session["value"] = 0
        self.session.save()
        return self

    def clear(self):  # pylint: disable=empty-docstring
        """ """
        self.session.clear()
        self.session["complete"] = False
        self.session["error"] = False
        self.session.save()

    def update(self, value):  # pylint: disable=empty-docstring
        """ """
        self.session.load()
        self.session["value"] = value
        self.session.save()

    def handle_error(self, error, error_url=None):
        """
        This should be called by the view code, within a try/catch
        block upon error.

        The session storage will be updated to reflect details of the
        error.  Next time client requests the progress status it will
        learn of the error and redirect the user.

        :param error: :class:`python:Exception` instance.

        :param error_url: Optional redirect URL; if not specified
           :attr:`error_url` is used.
        """
        self.session.load()
        self.session["error"] = True
        self.session["error_msg"] = self.app.render_error(error)
        self.session["error_url"] = error_url or self.error_url
        self.session.save()

    def handle_success(self, success_msg=None, success_url=None):
        """
        This should be called by the view code, when the long-running
        operation completes.

        The session storage will be updated to reflect the completed
        status.  Next time client requests the progress status it will
        discover it has completed, and redirect the user.

        :param success_msg: Optional message to display to the user
           (via session flash) when the operation completes
           successfully.  If not specified :attr:`success_msg` (or
           nothing) is used

        :param success_url: Optional redirect URL; if not specified
           :attr:`success_url` is used.
        """
        self.session.load()
        self.session["complete"] = True
        self.session["success_msg"] = success_msg or self.success_msg
        self.session["success_url"] = success_url or self.success_url
        self.session.save()
