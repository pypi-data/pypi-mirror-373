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
Upgrade Views
"""

import datetime
import logging
import os
import shutil
import subprocess

from sqlalchemy import orm

from wuttjamaican.db.model import Upgrade
from wuttaweb.views import MasterView
from wuttaweb.forms.schema import UserRef, WuttaEnum, FileDownload
from wuttaweb.progress import get_progress_session


log = logging.getLogger(__name__)


class UpgradeView(MasterView):  # pylint: disable=abstract-method
    """
    Master view for upgrades.

    Default route prefix is ``upgrades``.

    Notable URLs provided by this class:

    * ``/upgrades/``
    * ``/upgrades/new``
    * ``/upgrades/XXX``
    * ``/upgrades/XXX/edit``
    * ``/upgrades/XXX/delete``
    """

    model_class = Upgrade
    executable = True
    execute_progress_template = "/upgrade.mako"
    downloadable = True
    configurable = True

    grid_columns = [
        "created",
        "description",
        "status",
        "executed",
        "executed_by",
    ]

    sort_defaults = ("created", "desc")

    def configure_grid(self, grid):  # pylint: disable=empty-docstring
        """ """
        g = grid
        super().configure_grid(g)
        model = self.app.model
        enum = self.app.enum

        # description
        g.set_link("description")

        # created
        g.set_renderer("created", self.grid_render_datetime)

        # created_by
        g.set_link("created_by")
        Creator = orm.aliased(model.User)  # pylint: disable=invalid-name
        g.set_joiner(
            "created_by",
            lambda q: q.join(Creator, Creator.uuid == model.Upgrade.created_by_uuid),
        )
        g.set_filter("created_by", Creator.username, label="Created By Username")

        # status
        g.set_renderer("status", self.grid_render_enum, enum=enum.UpgradeStatus)

        # executed
        g.set_renderer("executed", self.grid_render_datetime)

        # executed_by
        g.set_link("executed_by")
        Executor = orm.aliased(model.User)  # pylint: disable=invalid-name
        g.set_joiner(
            "executed_by",
            lambda q: q.outerjoin(
                Executor, Executor.uuid == model.Upgrade.executed_by_uuid
            ),
        )
        g.set_filter("executed_by", Executor.username, label="Executed By Username")

    def grid_row_class(  # pylint: disable=empty-docstring,unused-argument
        self, upgrade, data, i
    ):
        """ """
        enum = self.app.enum
        if upgrade.status == enum.UpgradeStatus.EXECUTING:
            return "has-background-warning"
        if upgrade.status == enum.UpgradeStatus.FAILURE:
            return "has-background-warning"
        return None

    def configure_form(self, form):  # pylint: disable=empty-docstring
        """ """
        f = form
        super().configure_form(f)
        enum = self.app.enum
        upgrade = f.model_instance

        # never show these
        f.remove("created_by_uuid", "executing", "executed_by_uuid")

        # sequence sanity
        f.fields.set_sequence(
            [
                "description",
                "notes",
                "status",
                "created",
                "created_by",
                "executed",
                "executed_by",
            ]
        )

        # created
        if self.creating or self.editing:
            f.remove("created")

        # created_by
        if self.creating or self.editing:
            f.remove("created_by")
        else:
            f.set_node("created_by", UserRef(self.request))

        # notes
        f.set_widget("notes", "notes")

        # status
        if self.creating:
            f.remove("status")
        else:
            f.set_node("status", WuttaEnum(self.request, enum.UpgradeStatus))

        # executed
        if self.creating or self.editing or not upgrade.executed:
            f.remove("executed")

        # executed_by
        if self.creating or self.editing or not upgrade.executed:
            f.remove("executed_by")
        else:
            f.set_node("executed_by", UserRef(self.request))

        # exit_code
        if self.creating or self.editing or not upgrade.executed:
            f.remove("exit_code")

        # stdout / stderr
        if not (self.creating or self.editing) and upgrade.status in (
            enum.UpgradeStatus.SUCCESS,
            enum.UpgradeStatus.FAILURE,
        ):

            # stdout_file
            f.append("stdout_file")
            f.set_label("stdout_file", "STDOUT")
            url = self.get_action_url(
                "download", upgrade, _query={"filename": "stdout.log"}
            )
            f.set_node("stdout_file", FileDownload(self.request, url=url))
            f.set_default(
                "stdout_file", self.get_upgrade_filepath(upgrade, "stdout.log")
            )

            # stderr_file
            f.append("stderr_file")
            f.set_label("stderr_file", "STDERR")
            url = self.get_action_url(
                "download", upgrade, _query={"filename": "stderr.log"}
            )
            f.set_node("stderr_file", FileDownload(self.request, url=url))
            f.set_default(
                "stderr_file", self.get_upgrade_filepath(upgrade, "stderr.log")
            )

    def delete_instance(self, obj):
        """
        We override this method to delete any files associated with
        the upgrade, in addition to deleting the upgrade proper.
        """
        upgrade = obj
        path = self.get_upgrade_filepath(upgrade, create=False)
        if os.path.exists(path):
            shutil.rmtree(path)

        super().delete_instance(upgrade)

    def objectify(self, form):  # pylint: disable=empty-docstring
        """ """
        upgrade = super().objectify(form)
        enum = self.app.enum

        # set user, status when creating
        if self.creating:
            upgrade.created_by = self.request.user
            upgrade.status = enum.UpgradeStatus.PENDING

        return upgrade

    def download_path(self, obj, filename):  # pylint: disable=empty-docstring
        """ """
        upgrade = obj
        if filename:
            return self.get_upgrade_filepath(upgrade, filename)
        return None

    def get_upgrade_filepath(  # pylint: disable=empty-docstring
        self, upgrade, filename=None, create=True
    ):
        """ """
        uuid = str(upgrade.uuid)
        path = self.app.get_appdir(
            "data", "upgrades", uuid[:2], uuid[2:], create=create
        )
        if filename:
            path = os.path.join(path, filename)
        return path

    def execute_instance(self, obj, user, progress=None):
        """
        This method runs the actual upgrade.

        Default logic will get the script command from config, and run
        it via shell in a subprocess.

        The ``stdout`` and ``stderr`` streams are captured to separate
        log files which are then available to download.

        The upgrade itself is marked as "executed" with status of
        either ``SUCCESS`` or ``FAILURE``.
        """
        upgrade = obj
        enum = self.app.enum

        # locate file paths
        script = self.config.require(f"{self.app.appname}.upgrades.command")
        stdout_path = self.get_upgrade_filepath(upgrade, "stdout.log")
        stderr_path = self.get_upgrade_filepath(upgrade, "stderr.log")

        # record the fact that execution has begun for this upgrade
        # nb. this is done in separate session to ensure it sticks,
        # but also update local object to reflect the change
        with self.app.short_session(commit=True) as s:
            alt = s.merge(upgrade)
            alt.status = enum.UpgradeStatus.EXECUTING
        upgrade.status = enum.UpgradeStatus.EXECUTING

        # run the command
        log.debug("running upgrade command: %s", script)
        with open(stdout_path, "wb") as stdout:
            with open(stderr_path, "wb") as stderr:
                upgrade.exit_code = subprocess.call(
                    script, shell=True, text=True, stdout=stdout, stderr=stderr
                )
        logger = log.warning if upgrade.exit_code != 0 else log.debug
        logger("upgrade command had exit code: %s", upgrade.exit_code)

        # declare it complete
        upgrade.executed = datetime.datetime.now()
        upgrade.executed_by = user
        if upgrade.exit_code == 0:
            upgrade.status = enum.UpgradeStatus.SUCCESS
        else:
            upgrade.status = enum.UpgradeStatus.FAILURE

    def execute_progress(self):  # pylint: disable=empty-docstring
        """ """
        route_prefix = self.get_route_prefix()
        upgrade = self.get_instance()
        session = get_progress_session(self.request, f"{route_prefix}.execute")

        # session has 'complete' flag set when operation is over
        if session.get("complete"):

            # set a flash msg for user if one is defined.  this is the
            # time to do it since user is about to get redirected.
            msg = session.get("success_msg")
            if msg:
                self.request.session.flash(msg)

        elif session.get("error"):  # uh-oh

            # set an error flash msg for user.  this is the time to do it
            # since user is about to get redirected.
            msg = session.get("error_msg", "An unspecified error occurred.")
            self.request.session.flash(msg, "error")

        # our return value will include all from progress session
        data = dict(session)

        # add whatever might be new from upgrade process STDOUT
        path = self.get_upgrade_filepath(upgrade, filename="stdout.log")
        offset = session.get("stdout.offset", 0)
        if os.path.exists(path):
            size = os.path.getsize(path) - offset
            if size > 0:
                # with open(path, 'rb') as f:
                with open(path, "rt", encoding="utf_8") as f:
                    f.seek(offset)
                    chunk = f.read(size)
                    # data['stdout'] = chunk.decode('utf8').replace('\n', '<br />')
                    data["stdout"] = chunk.replace("\n", "<br />")
                session["stdout.offset"] = offset + size
                session.save()

        return data

    def configure_get_simple_settings(self):  # pylint: disable=empty-docstring
        """ """

        script = self.config.get(f"{self.app.appname}.upgrades.command")
        if not script:
            pass

        return [
            # basics
            {"name": f"{self.app.appname}.upgrades.command", "default": script},
        ]

    @classmethod
    def defaults(cls, config):  # pylint: disable=empty-docstring
        """ """

        # nb. Upgrade may come from custom model
        wutta_config = config.registry.settings["wutta_config"]
        app = wutta_config.get_app()
        cls.model_class = app.model.Upgrade

        cls._defaults(config)
        cls._upgrade_defaults(config)

    @classmethod
    def _upgrade_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        permission_prefix = cls.get_permission_prefix()
        instance_url_prefix = cls.get_instance_url_prefix()

        # execution progress
        config.add_route(
            f"{route_prefix}.execute_progress",
            f"{instance_url_prefix}/execute/progress",
        )
        config.add_view(
            cls,
            attr="execute_progress",
            route_name=f"{route_prefix}.execute_progress",
            permission=f"{permission_prefix}.execute",
            renderer="json",
        )


def defaults(config, **kwargs):  # pylint: disable=missing-function-docstring
    base = globals()

    UpgradeView = kwargs.get(  # pylint: disable=invalid-name,redefined-outer-name
        "UpgradeView", base["UpgradeView"]
    )
    UpgradeView.defaults(config)


def includeme(config):  # pylint: disable=missing-function-docstring
    defaults(config)
