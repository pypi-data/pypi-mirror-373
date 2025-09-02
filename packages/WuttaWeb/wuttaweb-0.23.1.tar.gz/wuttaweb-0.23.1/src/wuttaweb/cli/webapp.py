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
See also: :ref:`wutta-webapp`
"""

import os
import sys
from typing_extensions import Annotated

import typer
from pyramid.scripts import pserve

from wuttjamaican.cli import wutta_typer


@wutta_typer.command()
def webapp(  # pylint: disable=unused-argument
    ctx: typer.Context,
    auto_reload: Annotated[
        bool,
        typer.Option("--reload", "-r", help="Auto-reload web app when files change."),
    ] = False,
):
    """
    Run the configured web app
    """
    config = ctx.parent.wutta_config

    # we'll need config file(s) to specify for web app
    if not config.files_read:
        sys.stderr.write("no config files found!\n")
        sys.exit(1)

    runner = config.get(f"{config.appname}.web.app.runner", default="pserve")
    if runner == "pserve":

        # run pserve
        argv = ["pserve", f"file+ini:{config.files_read[0]}"]
        if ctx.params["auto_reload"]:
            argv.append("--reload")
        pserve.main(argv=argv)

    elif runner == "uvicorn":

        import uvicorn  # pylint: disable=import-error,import-outside-toplevel

        # need service details from config
        spec = config.require(f"{config.appname}.web.app.spec")
        kw = {
            "host": config.get(f"{config.appname}.web.app.host", default="127.0.0.1"),
            "port": config.get_int(f"{config.appname}.web.app.port", default=8000),
            "reload": ctx.params["auto_reload"],
            "reload_dirs": config.get_list(f"{config.appname}.web.app.reload_dirs"),
            "factory": config.get_bool(
                f"{config.appname}.web.app.factory", default=False
            ),
            "interface": config.get(
                f"{config.appname}.web.app.interface", default="auto"
            ),
            "root_path": config.get(f"{config.appname}.web.app.root_path", default=""),
        }

        # also must inject our config files to env, since there is no
        # other way to specify when running via uvicorn
        os.environ["WUTTA_CONFIG_FILES"] = os.pathsep.join(config.files_read)

        # run uvicorn
        uvicorn.run(spec, **kw)

    else:
        sys.stderr.write(f"unknown web app runner: {runner}\n")
        sys.exit(2)
