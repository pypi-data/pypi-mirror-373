# -*- coding: utf-8; -*-

import datetime
import os
import sys
from unittest.mock import patch, MagicMock

from wuttaweb.views import upgrades as mod
from wuttjamaican.exc import ConfigurationError
from wuttaweb.progress import get_progress_session
from wuttaweb.testing import WebTestCase


class TestUpgradeView(WebTestCase):

    def make_view(self):
        return mod.UpgradeView(self.request)

    def test_includeme(self):
        self.pyramid_config.include("wuttaweb.views.upgrades")

    def test_configure_grid(self):
        model = self.app.model
        view = self.make_view()

        # sanity / coverage check
        grid = view.make_grid(model_class=model.Upgrade)
        view.configure_grid(grid)

    def test_grid_row_class(self):
        model = self.app.model
        enum = self.app.enum
        upgrade = model.Upgrade(description="test", status=enum.UpgradeStatus.PENDING)
        data = dict(upgrade)
        view = self.make_view()

        self.assertIsNone(view.grid_row_class(upgrade, data, 1))

        upgrade.status = enum.UpgradeStatus.EXECUTING
        self.assertEqual(
            view.grid_row_class(upgrade, data, 1), "has-background-warning"
        )

        upgrade.status = enum.UpgradeStatus.SUCCESS
        self.assertIsNone(view.grid_row_class(upgrade, data, 1))

        upgrade.status = enum.UpgradeStatus.FAILURE
        self.assertEqual(
            view.grid_row_class(upgrade, data, 1), "has-background-warning"
        )

    def test_configure_form(self):
        self.pyramid_config.add_route("upgrades.download", "/upgrades/{uuid}/download")
        model = self.app.model
        enum = self.app.enum
        user = model.User(username="barney")
        self.session.add(user)
        upgrade = model.Upgrade(
            description="test", created_by=user, status=enum.UpgradeStatus.PENDING
        )
        self.session.add(upgrade)
        self.session.commit()
        view = self.make_view()

        # some fields exist when viewing
        with patch.object(view, "viewing", new=True):
            form = view.make_form(model_class=model.Upgrade, model_instance=upgrade)
            self.assertIn("created", form)
            view.configure_form(form)
            self.assertIn("created", form)

        # but then are removed when creating
        with patch.object(view, "creating", new=True):
            form = view.make_form(model_class=model.Upgrade)
            self.assertIn("created", form)
            view.configure_form(form)
            self.assertNotIn("created", form)

        # test executed, stdout/stderr when viewing
        with patch.object(view, "viewing", new=True):

            # executed is *not* shown by default
            form = view.make_form(model_class=model.Upgrade, model_instance=upgrade)
            self.assertIn("executed", form)
            view.configure_form(form)
            self.assertNotIn("executed", form)
            self.assertNotIn("stdout_file", form)
            self.assertNotIn("stderr_file", form)

            # but it *is* shown if upgrade is executed
            upgrade.executed = datetime.datetime.now()
            upgrade.status = enum.UpgradeStatus.SUCCESS
            form = view.make_form(model_class=model.Upgrade, model_instance=upgrade)
            self.assertIn("executed", form)
            view.configure_form(form)
            self.assertIn("executed", form)
            self.assertIn("stdout_file", form)
            self.assertIn("stderr_file", form)

    def test_objectify(self):
        model = self.app.model
        enum = self.app.enum
        user = model.User(username="barney")
        self.session.add(user)
        self.session.commit()
        view = self.make_view()

        # user and status are auto-set when creating
        self.request.user = user
        self.request.method = "POST"
        self.request.POST = {"description": "new one"}
        with patch.object(view, "creating", new=True):
            form = view.make_model_form()
            self.assertTrue(form.validate())
            upgrade = view.objectify(form)
            self.assertEqual(upgrade.description, "new one")
            self.assertIs(upgrade.created_by, user)
            self.assertEqual(upgrade.status, enum.UpgradeStatus.PENDING)

    def test_download_path(self):
        model = self.app.model
        enum = self.app.enum

        appdir = self.mkdtemp()
        self.config.setdefault("wutta.appdir", appdir)
        self.assertEqual(self.app.get_appdir(), appdir)

        user = model.User(username="barney")
        upgrade = model.Upgrade(
            description="test", created_by=user, status=enum.UpgradeStatus.PENDING
        )
        self.session.add(upgrade)
        self.session.commit()

        view = self.make_view()
        uuid = str(upgrade.uuid)

        # no filename
        path = view.download_path(upgrade, None)
        self.assertIsNone(path)

        # with filename
        path = view.download_path(upgrade, "foo.txt")
        self.assertEqual(
            path,
            os.path.join(appdir, "data", "upgrades", uuid[:2], uuid[2:], "foo.txt"),
        )

    def test_get_upgrade_filepath(self):
        model = self.app.model
        enum = self.app.enum

        appdir = self.mkdtemp()
        self.config.setdefault("wutta.appdir", appdir)
        self.assertEqual(self.app.get_appdir(), appdir)

        user = model.User(username="barney")
        upgrade = model.Upgrade(
            description="test", created_by=user, status=enum.UpgradeStatus.PENDING
        )
        self.session.add(upgrade)
        self.session.commit()

        view = self.make_view()
        uuid = str(upgrade.uuid)

        # no filename
        path = view.get_upgrade_filepath(upgrade)
        self.assertEqual(
            path, os.path.join(appdir, "data", "upgrades", uuid[:2], uuid[2:])
        )

        # with filename
        path = view.get_upgrade_filepath(upgrade, "foo.txt")
        self.assertEqual(
            path,
            os.path.join(appdir, "data", "upgrades", uuid[:2], uuid[2:], "foo.txt"),
        )

    def test_delete_instance(self):
        model = self.app.model
        enum = self.app.enum

        appdir = self.mkdtemp()
        self.config.setdefault("wutta.appdir", appdir)
        self.assertEqual(self.app.get_appdir(), appdir)

        user = model.User(username="barney")
        upgrade = model.Upgrade(
            description="test", created_by=user, status=enum.UpgradeStatus.PENDING
        )
        self.session.add(upgrade)
        self.session.commit()

        view = self.make_view()

        # mock stdout/stderr files
        upgrade_dir = view.get_upgrade_filepath(upgrade)
        stdout = view.get_upgrade_filepath(upgrade, "stdout.log")
        with open(stdout, "w") as f:
            f.write("stdout")
        stderr = view.get_upgrade_filepath(upgrade, "stderr.log")
        with open(stderr, "w") as f:
            f.write("stderr")

        # both upgrade and files are deleted
        self.assertTrue(os.path.exists(upgrade_dir))
        self.assertTrue(os.path.exists(stdout))
        self.assertTrue(os.path.exists(stderr))
        self.assertEqual(self.session.query(model.Upgrade).count(), 1)
        with patch.object(view, "Session", return_value=self.session):
            view.delete_instance(upgrade)
        self.assertFalse(os.path.exists(upgrade_dir))
        self.assertFalse(os.path.exists(stdout))
        self.assertFalse(os.path.exists(stderr))
        self.assertEqual(self.session.query(model.Upgrade).count(), 0)

    def test_execute_instance(self):
        model = self.app.model
        enum = self.app.enum

        appdir = self.mkdtemp()
        self.config.setdefault("wutta.appdir", appdir)
        self.assertEqual(self.app.get_appdir(), appdir)

        user = model.User(username="barney")
        upgrade = model.Upgrade(
            description="test", created_by=user, status=enum.UpgradeStatus.PENDING
        )
        self.session.add(upgrade)
        self.session.commit()

        view = self.make_view()
        self.request.user = user
        python = sys.executable

        # script not yet confiugred
        self.assertRaises(ConfigurationError, view.execute_instance, upgrade, user)

        # script w/ success
        goodpy = self.write_file(
            "good.py",
            """
import sys
sys.stdout.write('hello from good.py')
sys.exit(0)
""",
        )
        self.app.save_setting(
            self.session, "wutta.upgrades.command", f"{python} {goodpy}"
        )
        self.assertIsNone(upgrade.executed)
        self.assertIsNone(upgrade.executed_by)
        self.assertEqual(upgrade.status, enum.UpgradeStatus.PENDING)
        with patch.object(view, "Session", return_value=self.session):
            with patch.object(self.config, "usedb", new=True):
                view.execute_instance(upgrade, user)
        self.assertIsNotNone(upgrade.executed)
        self.assertIs(upgrade.executed_by, user)
        self.assertEqual(upgrade.status, enum.UpgradeStatus.SUCCESS)
        with open(view.get_upgrade_filepath(upgrade, "stdout.log")) as f:
            self.assertEqual(f.read(), "hello from good.py")
        with open(view.get_upgrade_filepath(upgrade, "stderr.log")) as f:
            self.assertEqual(f.read(), "")

        # need a new record for next test
        upgrade = model.Upgrade(
            description="test", created_by=user, status=enum.UpgradeStatus.PENDING
        )
        self.session.add(upgrade)
        self.session.commit()

        # script w/ failure
        badpy = self.write_file(
            "bad.py",
            """
import sys
sys.stderr.write('hello from bad.py')
sys.exit(42)
""",
        )
        self.app.save_setting(
            self.session, "wutta.upgrades.command", f"{python} {badpy}"
        )
        self.assertIsNone(upgrade.executed)
        self.assertIsNone(upgrade.executed_by)
        self.assertEqual(upgrade.status, enum.UpgradeStatus.PENDING)
        with patch.object(view, "Session", return_value=self.session):
            with patch.object(self.config, "usedb", new=True):
                view.execute_instance(upgrade, user)
        self.assertIsNotNone(upgrade.executed)
        self.assertIs(upgrade.executed_by, user)
        self.assertEqual(upgrade.status, enum.UpgradeStatus.FAILURE)
        with open(view.get_upgrade_filepath(upgrade, "stdout.log")) as f:
            self.assertEqual(f.read(), "")
        with open(view.get_upgrade_filepath(upgrade, "stderr.log")) as f:
            self.assertEqual(f.read(), "hello from bad.py")

    def test_execute_progress(self):
        model = self.app.model
        enum = self.app.enum
        view = self.make_view()

        user = model.User(username="barney")
        self.session.add(user)
        upgrade = model.Upgrade(
            description="test", created_by=user, status=enum.UpgradeStatus.PENDING
        )
        self.session.add(upgrade)
        self.session.commit()

        stdout = self.write_file("stdout.log", "hello 001\n")

        self.request.matchdict = {"uuid": upgrade.uuid}
        with patch.multiple(
            mod.UpgradeView,
            Session=MagicMock(return_value=self.session),
            get_upgrade_filepath=MagicMock(return_value=stdout),
        ):

            # nb. this is used to identify progress tracker
            self.request.session.id = "mockid#1"

            # first call should get the full contents
            context = view.execute_progress()
            self.assertFalse(context.get("complete"))
            self.assertFalse(context.get("error"))
            # nb. newline is converted to <br>
            self.assertEqual(context["stdout"], "hello 001<br />")

            # next call should get any new contents
            with open(stdout, "a") as f:
                f.write("hello 002\n")
            context = view.execute_progress()
            self.assertFalse(context.get("complete"))
            self.assertFalse(context.get("error"))
            self.assertEqual(context["stdout"], "hello 002<br />")

            # nb. switch to a different progress tracker
            self.request.session.id = "mockid#2"

            # first call should get the full contents
            context = view.execute_progress()
            self.assertFalse(context.get("complete"))
            self.assertFalse(context.get("error"))
            self.assertEqual(context["stdout"], "hello 001<br />hello 002<br />")

            # mark progress complete
            session = get_progress_session(self.request, "upgrades.execute")
            session.load()
            session["complete"] = True
            session["success_msg"] = "yay!"
            session.save()

            # next call should reflect that
            self.assertEqual(self.request.session.pop_flash(), [])
            context = view.execute_progress()
            self.assertTrue(context.get("complete"))
            self.assertFalse(context.get("error"))
            # nb. this is missing b/c we already got all contents
            self.assertNotIn("stdout", context)
            self.assertEqual(self.request.session.pop_flash(), ["yay!"])

            # nb. switch to a different progress tracker
            self.request.session.id = "mockid#3"

            # first call should get the full contents
            context = view.execute_progress()
            self.assertFalse(context.get("complete"))
            self.assertFalse(context.get("error"))
            self.assertEqual(context["stdout"], "hello 001<br />hello 002<br />")

            # mark progress error
            session = get_progress_session(self.request, "upgrades.execute")
            session.load()
            session["error"] = True
            session["error_msg"] = "omg!"
            session.save()

            # next call should reflect that
            self.assertEqual(self.request.session.pop_flash("error"), [])
            context = view.execute_progress()
            self.assertFalse(context.get("complete"))
            self.assertTrue(context.get("error"))
            # nb. this is missing b/c we already got all contents
            self.assertNotIn("stdout", context)
            self.assertEqual(self.request.session.pop_flash("error"), ["omg!"])

    def test_configure_get_simple_settings(self):
        # sanity/coverage check
        view = self.make_view()
        simple = view.configure_get_simple_settings()
