# -*- coding: utf-8; -*-

from unittest.mock import MagicMock, patch

from wuttjamaican.testing import ConfigTestCase

from wuttaweb.cli import webapp as mod


class TestWebapp(ConfigTestCase):

    def make_context(self, **kwargs):
        params = {"auto_reload": False}
        params.update(kwargs.get("params", {}))
        ctx = MagicMock(params=params)
        ctx.parent.wutta_config = self.config
        return ctx

    def test_missing_config_file(self):
        # nb. our default config has no files, so can test w/ that
        ctx = self.make_context()
        with patch.object(mod, "sys") as sys:
            sys.exit.side_effect = RuntimeError
            self.assertRaises(RuntimeError, mod.webapp, ctx)
            sys.stderr.write.assert_called_once_with("no config files found!\n")
            sys.exit.assert_called_once_with(1)

    def test_invalid_runner(self):

        # make new config from file, with bad setting
        path = self.write_file(
            "my.conf",
            """
[wutta.web]
app.runner = bogus
""",
        )
        self.config = self.make_config(files=[path])

        ctx = self.make_context()
        with patch.object(mod, "sys") as sys:
            sys.exit.side_effect = RuntimeError
            self.assertRaises(RuntimeError, mod.webapp, ctx)
            sys.stderr.write.assert_called_once_with("unknown web app runner: bogus\n")
            sys.exit.assert_called_once_with(2)

    def test_pserve(self):

        path = self.write_file(
            "my.conf",
            """
[wutta.web]
app.runner = pserve
""",
        )
        self.config = self.make_config(files=[path])

        # normal
        with patch.object(mod, "pserve") as pserve:
            ctx = self.make_context()
            mod.webapp(ctx)
            pserve.main.assert_called_once_with(argv=["pserve", f"file+ini:{path}"])

        # with reload
        with patch.object(mod, "pserve") as pserve:
            ctx = self.make_context(params={"auto_reload": True})
            mod.webapp(ctx)
            pserve.main.assert_called_once_with(
                argv=["pserve", f"file+ini:{path}", "--reload"]
            )

    def test_uvicorn(self):

        path = self.write_file(
            "my.conf",
            """
[wutta.web]
app.runner = uvicorn
app.spec = wuttaweb.app:make_wsgi_app
""",
        )
        self.config = self.make_config(files=[path])

        orig_import = __import__
        uvicorn = MagicMock()

        def mock_import(name, *args, **kwargs):
            if name == "uvicorn":
                return uvicorn
            return orig_import(name, *args, **kwargs)

        # normal
        with patch("builtins.__import__", side_effect=mock_import):
            ctx = self.make_context()
            mod.webapp(ctx)
            uvicorn.run.assert_called_once_with(
                "wuttaweb.app:make_wsgi_app",
                host="127.0.0.1",
                port=8000,
                reload=False,
                reload_dirs=None,
                factory=False,
                interface="auto",
                root_path="",
            )

        # with reload
        uvicorn.run.reset_mock()
        with patch("builtins.__import__", side_effect=mock_import):
            ctx = self.make_context(params={"auto_reload": True})
            mod.webapp(ctx)
            uvicorn.run.assert_called_once_with(
                "wuttaweb.app:make_wsgi_app",
                host="127.0.0.1",
                port=8000,
                reload=True,
                reload_dirs=None,
                factory=False,
                interface="auto",
                root_path="",
            )
