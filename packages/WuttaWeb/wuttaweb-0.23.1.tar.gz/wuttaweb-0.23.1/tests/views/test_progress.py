# -*- coding: utf-8; -*-

from pyramid import testing

from wuttaweb.views import progress as mod
from wuttaweb.progress import get_progress_session
from wuttaweb.testing import WebTestCase


class TestProgressView(WebTestCase):

    def test_includeme(self):
        self.pyramid_config.include("wuttaweb.views.progress")

    def test_basic(self):
        self.request.session.id = "mockid"
        self.request.matchdict = {"key": "foo"}

        # first call with no setup, will create the progress session
        # but it should be "empty" - except not really since beaker
        # adds some keys by default
        context = mod.progress(self.request)
        self.assertIsInstance(context, dict)

        # now let's establish a progress session of our own
        progsess = get_progress_session(self.request, "bar")
        progsess["maximum"] = 2
        progsess["value"] = 1
        progsess.save()

        # then call view, check results
        self.request.matchdict = {"key": "bar"}
        context = mod.progress(self.request)
        self.assertEqual(context["maximum"], 2)
        self.assertEqual(context["value"], 1)
        self.assertNotIn("complete", context)

        # now mark it as complete, check results
        progsess["complete"] = True
        progsess["success_msg"] = "yay!"
        progsess.save()
        context = mod.progress(self.request)
        self.assertTrue(context["complete"])
        self.assertEqual(context["success_msg"], "yay!")

        # now do that all again, with error
        progsess = get_progress_session(self.request, "baz")
        progsess["maximum"] = 2
        progsess["value"] = 1
        progsess.save()
        self.request.matchdict = {"key": "baz"}
        context = mod.progress(self.request)
        self.assertEqual(context["maximum"], 2)
        self.assertEqual(context["value"], 1)
        self.assertNotIn("complete", context)
        self.assertNotIn("error", context)
        progsess["error"] = True
        progsess["error_msg"] = "omg!"
        progsess.save()
        context = mod.progress(self.request)
        self.assertTrue(context["error"])
        self.assertEqual(context["error_msg"], "omg!")
