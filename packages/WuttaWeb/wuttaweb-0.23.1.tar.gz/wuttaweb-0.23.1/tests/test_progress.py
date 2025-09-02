# -*- coding: utf-8; -*-

from unittest import TestCase

from pyramid import testing
from beaker.session import Session as BeakerSession

from wuttjamaican.testing import ConfigTestCase

from wuttaweb import progress as mod


class TestGetBasicSession(TestCase):

    def setUp(self):
        self.request = testing.DummyRequest()

    def test_basic(self):
        session = mod.get_basic_session(self.request)
        self.assertIsInstance(session, BeakerSession)
        self.assertFalse(session.use_cookies)


class TestGetProgressSession(TestCase):

    def setUp(self):
        self.request = testing.DummyRequest()

    def test_basic(self):
        self.request.session.id = "mockid"
        session = mod.get_progress_session(self.request, "foo")
        self.assertIsInstance(session, BeakerSession)
        self.assertEqual(session.id, "mockid.progress.foo")


class TestSessionProgress(ConfigTestCase):

    def setUp(self):
        self.setup_config()
        self.request = testing.DummyRequest(wutta_config=self.config)
        self.request.session.id = "mockid"

    def test_error_url(self):
        factory = mod.SessionProgress(self.request, "foo", success_url="/blart")
        self.assertEqual(factory.error_url, "/blart")

    def test_basic(self):

        # sanity / coverage check
        factory = mod.SessionProgress(self.request, "foo")
        prog = factory("doing things", 2)
        prog.update(1)
        prog.update(2)
        prog.handle_success()

    def test_error(self):

        # sanity / coverage check
        factory = mod.SessionProgress(self.request, "foo")
        prog = factory("doing things", 2)
        prog.update(1)
        try:
            raise RuntimeError("omg")
        except Exception as error:
            prog.handle_error(error)
