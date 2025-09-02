# -*- coding: utf-8; -*-

import decimal
import json
import uuid as _uuid
from unittest import TestCase
from unittest.mock import patch, MagicMock

import colander
from fanstatic import Library, Resource
from pyramid import testing

from wuttjamaican.conf import WuttaConfig
from wuttjamaican.testing import ConfigTestCase, DataTestCase
from wuttjamaican.util import resource_path

from wuttaweb import util as mod
from wuttaweb.app import establish_theme
from wuttaweb.grids import Grid
from wuttaweb.testing import WebTestCase


class TestFieldList(TestCase):

    def test_insert_before(self):
        fields = mod.FieldList(["f1", "f2"])
        self.assertEqual(fields, ["f1", "f2"])

        # typical
        fields.insert_before("f1", "XXX")
        self.assertEqual(fields, ["XXX", "f1", "f2"])
        fields.insert_before("f2", "YYY")
        self.assertEqual(fields, ["XXX", "f1", "YYY", "f2"])

        # appends new field if reference field is invalid
        fields.insert_before("f3", "ZZZ")
        self.assertEqual(fields, ["XXX", "f1", "YYY", "f2", "ZZZ"])

    def test_insert_after(self):
        fields = mod.FieldList(["f1", "f2"])
        self.assertEqual(fields, ["f1", "f2"])

        # typical
        fields.insert_after("f1", "XXX")
        self.assertEqual(fields, ["f1", "XXX", "f2"])
        fields.insert_after("XXX", "YYY")
        self.assertEqual(fields, ["f1", "XXX", "YYY", "f2"])

        # appends new field if reference field is invalid
        fields.insert_after("f3", "ZZZ")
        self.assertEqual(fields, ["f1", "XXX", "YYY", "f2", "ZZZ"])

    def test_set_sequence(self):
        fields = mod.FieldList(["f5", "f1", "f3", "f4", "f2"])

        # setting sequence will only "sort" for explicit fields.
        # other fields remain in original order, but at the end.
        fields.set_sequence(["f1", "f2", "f3"])
        self.assertEqual(fields, ["f1", "f2", "f3", "f5", "f4"])


class TestGetLibVer(TestCase):

    def setUp(self):
        self.config = WuttaConfig()
        self.request = testing.DummyRequest()
        self.request.wutta_config = self.config

    def test_buefy_default(self):
        version = mod.get_libver(self.request, "buefy")
        self.assertEqual(version, "0.9.25")

    def test_buefy_custom_old(self):
        self.config.setdefault("wuttaweb.buefy_version", "0.9.29")
        version = mod.get_libver(self.request, "buefy")
        self.assertEqual(version, "0.9.29")

    def test_buefy_custom_old_tailbone(self):
        self.config.setdefault("tailbone.libver.buefy", "0.9.28")
        version = mod.get_libver(self.request, "buefy", prefix="tailbone")
        self.assertEqual(version, "0.9.28")

    def test_buefy_custom_new(self):
        self.config.setdefault("wuttaweb.libver.buefy", "0.9.29")
        version = mod.get_libver(self.request, "buefy")
        self.assertEqual(version, "0.9.29")

    def test_buefy_configured_only(self):
        version = mod.get_libver(self.request, "buefy", configured_only=True)
        self.assertIsNone(version)

    def test_buefy_default_only(self):
        self.config.setdefault("wuttaweb.libver.buefy", "0.9.29")
        version = mod.get_libver(self.request, "buefy", default_only=True)
        self.assertEqual(version, "0.9.25")

    def test_buefy_css_default(self):
        version = mod.get_libver(self.request, "buefy.css")
        self.assertEqual(version, "0.9.25")

    def test_buefy_css_custom_old(self):
        # nb. this uses same setting as buefy (js)
        self.config.setdefault("wuttaweb.buefy_version", "0.9.29")
        version = mod.get_libver(self.request, "buefy.css")
        self.assertEqual(version, "0.9.29")

    def test_buefy_css_custom_new(self):
        # nb. this uses same setting as buefy (js)
        self.config.setdefault("wuttaweb.libver.buefy", "0.9.29")
        version = mod.get_libver(self.request, "buefy.css")
        self.assertEqual(version, "0.9.29")

    def test_buefy_css_configured_only(self):
        version = mod.get_libver(self.request, "buefy.css", configured_only=True)
        self.assertIsNone(version)

    def test_buefy_css_default_only(self):
        self.config.setdefault("wuttaweb.libver.buefy", "0.9.29")
        version = mod.get_libver(self.request, "buefy.css", default_only=True)
        self.assertEqual(version, "0.9.25")

    def test_vue_default(self):
        version = mod.get_libver(self.request, "vue")
        self.assertEqual(version, "2.6.14")

    def test_vue_custom_old(self):
        self.config.setdefault("wuttaweb.vue_version", "3.4.31")
        version = mod.get_libver(self.request, "vue")
        self.assertEqual(version, "3.4.31")

    def test_vue_custom_new(self):
        self.config.setdefault("wuttaweb.libver.vue", "3.4.31")
        version = mod.get_libver(self.request, "vue")
        self.assertEqual(version, "3.4.31")

    def test_vue_configured_only(self):
        version = mod.get_libver(self.request, "vue", configured_only=True)
        self.assertIsNone(version)

    def test_vue_default_only(self):
        self.config.setdefault("wuttaweb.libver.vue", "3.4.31")
        version = mod.get_libver(self.request, "vue", default_only=True)
        self.assertEqual(version, "2.6.14")

    def test_vue_resource_default(self):
        version = mod.get_libver(self.request, "vue_resource")
        self.assertEqual(version, "1.5.3")

    def test_vue_resource_custom(self):
        self.config.setdefault("wuttaweb.libver.vue_resource", "1.5.3")
        version = mod.get_libver(self.request, "vue_resource")
        self.assertEqual(version, "1.5.3")

    def test_fontawesome_default(self):
        version = mod.get_libver(self.request, "fontawesome")
        self.assertEqual(version, "5.3.1")

    def test_fontawesome_custom(self):
        self.config.setdefault("wuttaweb.libver.fontawesome", "5.6.3")
        version = mod.get_libver(self.request, "fontawesome")
        self.assertEqual(version, "5.6.3")

    def test_bb_vue_default(self):
        version = mod.get_libver(self.request, "bb_vue")
        self.assertEqual(version, "3.5.18")

    def test_bb_vue_custom(self):
        self.config.setdefault("wuttaweb.libver.bb_vue", "3.4.30")
        version = mod.get_libver(self.request, "bb_vue")
        self.assertEqual(version, "3.4.30")

    def test_bb_oruga_default(self):
        version = mod.get_libver(self.request, "bb_oruga")
        self.assertEqual(version, "0.11.4")

    def test_bb_oruga_custom(self):
        self.config.setdefault("wuttaweb.libver.bb_oruga", "0.8.11")
        version = mod.get_libver(self.request, "bb_oruga")
        self.assertEqual(version, "0.8.11")

    def test_bb_oruga_bulma_default(self):
        version = mod.get_libver(self.request, "bb_oruga_bulma")
        self.assertEqual(version, "0.7.3")
        version = mod.get_libver(self.request, "bb_oruga_bulma_css")
        self.assertEqual(version, "0.7.3")

    def test_bb_oruga_bulma_custom(self):
        self.config.setdefault("wuttaweb.libver.bb_oruga_bulma", "0.2.11")
        version = mod.get_libver(self.request, "bb_oruga_bulma")
        self.assertEqual(version, "0.2.11")

    def test_bb_fontawesome_svg_core_default(self):
        version = mod.get_libver(self.request, "bb_fontawesome_svg_core")
        self.assertEqual(version, "7.0.0")

    def test_bb_fontawesome_svg_core_custom(self):
        self.config.setdefault("wuttaweb.libver.bb_fontawesome_svg_core", "6.5.1")
        version = mod.get_libver(self.request, "bb_fontawesome_svg_core")
        self.assertEqual(version, "6.5.1")

    def test_bb_free_solid_svg_icons_default(self):
        version = mod.get_libver(self.request, "bb_free_solid_svg_icons")
        self.assertEqual(version, "7.0.0")

    def test_bb_free_solid_svg_icons_custom(self):
        self.config.setdefault("wuttaweb.libver.bb_free_solid_svg_icons", "6.5.1")
        version = mod.get_libver(self.request, "bb_free_solid_svg_icons")
        self.assertEqual(version, "6.5.1")

    def test_bb_vue_fontawesome_default(self):
        version = mod.get_libver(self.request, "bb_vue_fontawesome")
        self.assertEqual(version, "3.1.1")

    def test_bb_vue_fontawesome_custom(self):
        self.config.setdefault("wuttaweb.libver.bb_vue_fontawesome", "3.0.8")
        version = mod.get_libver(self.request, "bb_vue_fontawesome")
        self.assertEqual(version, "3.0.8")


libcache = Library("testing", "libcache")
vue_js = Resource(libcache, "vue.js")
vue_resource_js = Resource(libcache, "vue_resource.js")
buefy_js = Resource(libcache, "buefy.js")
buefy_css = Resource(libcache, "buefy.css")
fontawesome_js = Resource(libcache, "fontawesome.js")
bb_vue_js = Resource(libcache, "bb_vue.js")
bb_oruga_js = Resource(libcache, "bb_oruga.js")
bb_oruga_bulma_js = Resource(libcache, "bb_oruga_bulma.js")
bb_oruga_bulma_css = Resource(libcache, "bb_oruga_bulma.css")
bb_fontawesome_svg_core_js = Resource(libcache, "bb_fontawesome_svg_core.js")
bb_free_solid_svg_icons_js = Resource(libcache, "bb_free_solid_svg_icons.js")
bb_vue_fontawesome_js = Resource(libcache, "bb_vue_fontawesome.js")


class TestGetLibUrl(TestCase):

    def setUp(self):
        self.config = WuttaConfig()
        self.request = testing.DummyRequest(wutta_config=self.config)
        self.pyramid_config = testing.setUp(request=self.request)

    def tearDown(self):
        testing.tearDown()

    def setup_fanstatic(self, register=True):
        self.pyramid_config.include("pyramid_fanstatic")
        if register:
            self.config.setdefault("wuttaweb.static_libcache.module", "tests.test_util")

        needed = MagicMock()
        needed.library_url = MagicMock(return_value="/fanstatic")
        self.request.environ["fanstatic.needed"] = needed
        self.request.script_name = "/wutta"

    def test_unknown(self):
        url = mod.get_liburl(self.request, "unknown")
        self.assertIsNone(url)

    def test_buefy_default(self):
        url = mod.get_liburl(self.request, "buefy")
        self.assertEqual(url, "https://unpkg.com/buefy@0.9.25/dist/buefy.min.js")

    def test_buefy_custom(self):
        self.config.setdefault("wuttaweb.liburl.buefy", "/lib/buefy.js")
        url = mod.get_liburl(self.request, "buefy")
        self.assertEqual(url, "/lib/buefy.js")

    def test_buefy_custom_tailbone(self):
        self.config.setdefault("tailbone.liburl.buefy", "/tailbone/buefy.js")
        url = mod.get_liburl(self.request, "buefy", prefix="tailbone")
        self.assertEqual(url, "/tailbone/buefy.js")

    def test_buefy_default_only(self):
        self.config.setdefault("wuttaweb.liburl.buefy", "/lib/buefy.js")
        url = mod.get_liburl(self.request, "buefy", default_only=True)
        self.assertEqual(url, "https://unpkg.com/buefy@0.9.25/dist/buefy.min.js")

    def test_buefy_configured_only(self):
        url = mod.get_liburl(self.request, "buefy", configured_only=True)
        self.assertIsNone(url)

    def test_buefy_fanstatic(self):
        self.setup_fanstatic()
        url = mod.get_liburl(self.request, "buefy")
        self.assertEqual(url, "/wutta/fanstatic/buefy.js")

    def test_buefy_fanstatic_tailbone(self):
        self.setup_fanstatic(register=False)
        self.config.setdefault("tailbone.static_libcache.module", "tests.test_util")
        url = mod.get_liburl(self.request, "buefy", prefix="tailbone")
        self.assertEqual(url, "/wutta/fanstatic/buefy.js")

    def test_buefy_css_default(self):
        url = mod.get_liburl(self.request, "buefy.css")
        self.assertEqual(url, "https://unpkg.com/buefy@0.9.25/dist/buefy.min.css")

    def test_buefy_css_custom(self):
        self.config.setdefault("wuttaweb.liburl.buefy.css", "/lib/buefy.css")
        url = mod.get_liburl(self.request, "buefy.css")
        self.assertEqual(url, "/lib/buefy.css")

    def test_buefy_css_fanstatic(self):
        self.setup_fanstatic()
        url = mod.get_liburl(self.request, "buefy.css")
        self.assertEqual(url, "/wutta/fanstatic/buefy.css")

    def test_vue_default(self):
        url = mod.get_liburl(self.request, "vue")
        self.assertEqual(url, "https://unpkg.com/vue@2.6.14/dist/vue.min.js")

    def test_vue_custom(self):
        self.config.setdefault("wuttaweb.liburl.vue", "/lib/vue.js")
        url = mod.get_liburl(self.request, "vue")
        self.assertEqual(url, "/lib/vue.js")

    def test_vue_fanstatic(self):
        self.setup_fanstatic()
        url = mod.get_liburl(self.request, "vue")
        self.assertEqual(url, "/wutta/fanstatic/vue.js")

    def test_vue_resource_default(self):
        url = mod.get_liburl(self.request, "vue_resource")
        self.assertEqual(url, "https://cdn.jsdelivr.net/npm/vue-resource@1.5.3")

    def test_vue_resource_custom(self):
        self.config.setdefault("wuttaweb.liburl.vue_resource", "/lib/vue-resource.js")
        url = mod.get_liburl(self.request, "vue_resource")
        self.assertEqual(url, "/lib/vue-resource.js")

    def test_vue_resource_fanstatic(self):
        self.setup_fanstatic()
        url = mod.get_liburl(self.request, "vue_resource")
        self.assertEqual(url, "/wutta/fanstatic/vue_resource.js")

    def test_fontawesome_default(self):
        url = mod.get_liburl(self.request, "fontawesome")
        self.assertEqual(url, "https://use.fontawesome.com/releases/v5.3.1/js/all.js")

    def test_fontawesome_custom(self):
        self.config.setdefault("wuttaweb.liburl.fontawesome", "/lib/fontawesome.js")
        url = mod.get_liburl(self.request, "fontawesome")
        self.assertEqual(url, "/lib/fontawesome.js")

    def test_fontawesome_fanstatic(self):
        self.setup_fanstatic()
        url = mod.get_liburl(self.request, "fontawesome")
        self.assertEqual(url, "/wutta/fanstatic/fontawesome.js")

    def test_bb_vue_default(self):
        url = mod.get_liburl(self.request, "bb_vue")
        self.assertEqual(
            url, "https://unpkg.com/vue@3.5.18/dist/vue.esm-browser.prod.js"
        )

    def test_bb_vue_custom(self):
        self.config.setdefault("wuttaweb.liburl.bb_vue", "/lib/vue.js")
        url = mod.get_liburl(self.request, "bb_vue")
        self.assertEqual(url, "/lib/vue.js")

    def test_bb_vue_fanstatic(self):
        self.setup_fanstatic()
        url = mod.get_liburl(self.request, "bb_vue")
        self.assertEqual(url, "/wutta/fanstatic/bb_vue.js")

    def test_bb_oruga_default(self):
        url = mod.get_liburl(self.request, "bb_oruga")
        self.assertEqual(
            url, "https://unpkg.com/@oruga-ui/oruga-next@0.11.4/dist/oruga.mjs"
        )

    def test_bb_oruga_custom(self):
        self.config.setdefault("wuttaweb.liburl.bb_oruga", "/lib/oruga.js")
        url = mod.get_liburl(self.request, "bb_oruga")
        self.assertEqual(url, "/lib/oruga.js")

    def test_bb_oruga_fanstatic(self):
        self.setup_fanstatic()
        url = mod.get_liburl(self.request, "bb_oruga")
        self.assertEqual(url, "/wutta/fanstatic/bb_oruga.js")

    def test_bb_oruga_bulma_default(self):
        url = mod.get_liburl(self.request, "bb_oruga_bulma")
        self.assertEqual(
            url, "https://unpkg.com/@oruga-ui/theme-bulma@0.7.3/dist/bulma.js"
        )

    def test_bb_oruga_bulma_custom(self):
        self.config.setdefault("wuttaweb.liburl.bb_oruga_bulma", "/lib/oruga_bulma.js")
        url = mod.get_liburl(self.request, "bb_oruga_bulma")
        self.assertEqual(url, "/lib/oruga_bulma.js")

    def test_bb_oruga_bulma_fanstatic(self):
        self.setup_fanstatic()
        url = mod.get_liburl(self.request, "bb_oruga_bulma")
        self.assertEqual(url, "/wutta/fanstatic/bb_oruga_bulma.js")

    def test_bb_oruga_bulma_css_default(self):
        url = mod.get_liburl(self.request, "bb_oruga_bulma_css")
        self.assertEqual(
            url, "https://unpkg.com/@oruga-ui/theme-bulma@0.7.3/dist/bulma.css"
        )

    def test_bb_oruga_bulma_css_custom(self):
        self.config.setdefault(
            "wuttaweb.liburl.bb_oruga_bulma_css", "/lib/oruga-bulma.css"
        )
        url = mod.get_liburl(self.request, "bb_oruga_bulma_css")
        self.assertEqual(url, "/lib/oruga-bulma.css")

    def test_bb_oruga_bulma_css_fanstatic(self):
        self.setup_fanstatic()
        url = mod.get_liburl(self.request, "bb_oruga_bulma_css")
        self.assertEqual(url, "/wutta/fanstatic/bb_oruga_bulma.css")

    def test_bb_fontawesome_svg_core_default(self):
        url = mod.get_liburl(self.request, "bb_fontawesome_svg_core")
        self.assertEqual(
            url,
            "https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-svg-core@7.0.0/+esm",
        )

    def test_bb_fontawesome_svg_core_custom(self):
        self.config.setdefault(
            "wuttaweb.liburl.bb_fontawesome_svg_core", "/lib/fontawesome-svg-core.js"
        )
        url = mod.get_liburl(self.request, "bb_fontawesome_svg_core")
        self.assertEqual(url, "/lib/fontawesome-svg-core.js")

    def test_bb_fontawesome_svg_core_fanstatic(self):
        self.setup_fanstatic()
        url = mod.get_liburl(self.request, "bb_fontawesome_svg_core")
        self.assertEqual(url, "/wutta/fanstatic/bb_fontawesome_svg_core.js")

    def test_bb_free_solid_svg_icons_default(self):
        url = mod.get_liburl(self.request, "bb_free_solid_svg_icons")
        self.assertEqual(
            url,
            "https://cdn.jsdelivr.net/npm/@fortawesome/free-solid-svg-icons@7.0.0/+esm",
        )

    def test_bb_free_solid_svg_icons_custom(self):
        self.config.setdefault(
            "wuttaweb.liburl.bb_free_solid_svg_icons", "/lib/free-solid-svg-icons.js"
        )
        url = mod.get_liburl(self.request, "bb_free_solid_svg_icons")
        self.assertEqual(url, "/lib/free-solid-svg-icons.js")

    def test_bb_free_solid_svg_icons_fanstatic(self):
        self.setup_fanstatic()
        url = mod.get_liburl(self.request, "bb_free_solid_svg_icons")
        self.assertEqual(url, "/wutta/fanstatic/bb_free_solid_svg_icons.js")

    def test_bb_vue_fontawesome_default(self):
        url = mod.get_liburl(self.request, "bb_vue_fontawesome")
        self.assertEqual(
            url, "https://cdn.jsdelivr.net/npm/@fortawesome/vue-fontawesome@3.1.1/+esm"
        )

    def test_bb_vue_fontawesome_custom(self):
        self.config.setdefault(
            "wuttaweb.liburl.bb_vue_fontawesome", "/lib/vue-fontawesome.js"
        )
        url = mod.get_liburl(self.request, "bb_vue_fontawesome")
        self.assertEqual(url, "/lib/vue-fontawesome.js")

    def test_bb_vue_fontawesome_fanstatic(self):
        self.setup_fanstatic()
        url = mod.get_liburl(self.request, "bb_vue_fontawesome")
        self.assertEqual(url, "/wutta/fanstatic/bb_vue_fontawesome.js")


class TestGetFormData(TestCase):

    def setUp(self):
        self.config = WuttaConfig()

    def make_request(self, **kwargs):
        kwargs.setdefault("wutta_config", self.config)
        kwargs.setdefault("POST", {"foo1": "bar"})
        kwargs.setdefault("json_body", {"foo2": "baz"})
        return testing.DummyRequest(**kwargs)

    def test_default(self):
        request = self.make_request()
        data = mod.get_form_data(request)
        self.assertEqual(data, {"foo1": "bar"})

    def test_is_xhr(self):
        request = self.make_request(POST=None, is_xhr=True)
        data = mod.get_form_data(request)
        self.assertEqual(data, {"foo2": "baz"})

    def test_content_type(self):
        request = self.make_request(POST=None, content_type="application/json")
        data = mod.get_form_data(request)
        self.assertEqual(data, {"foo2": "baz"})


class TestGetModelFields(ConfigTestCase):

    def test_empty_model_class(self):
        fields = mod.get_model_fields(self.config, None)
        self.assertIsNone(fields)

    def test_unknown_model_class(self):
        fields = mod.get_model_fields(self.config, TestCase)
        self.assertIsNone(fields)

    def test_basic(self):
        model = self.app.model
        fields = mod.get_model_fields(self.config, model.Setting)
        self.assertEqual(fields, ["name", "value"])

    def test_include_fk(self):
        model = self.app.model

        # fk excluded by default
        fields = mod.get_model_fields(self.config, model.User)
        self.assertNotIn("person_uuid", fields)
        self.assertIn("person", fields)

        # fk can be included
        fields = mod.get_model_fields(self.config, model.User, include_fk=True)
        self.assertIn("person_uuid", fields)
        self.assertIn("person", fields)

    def test_avoid_versions(self):
        model = self.app.model

        mapper = MagicMock(
            iterate_properties=[
                MagicMock(key="uuid"),
                MagicMock(key="full_name"),
                MagicMock(key="first_name"),
                MagicMock(key="middle_name"),
                MagicMock(key="last_name"),
                MagicMock(key="versions"),
            ]
        )

        with patch.object(mod, "sa") as sa:
            sa.inspect.return_value = mapper

            with patch.object(self.app, "continuum_is_enabled", return_value=True):
                fields = mod.get_model_fields(self.config, model.Person)
                # nb. no versions field
                self.assertEqual(
                    set(fields),
                    set(
                        ["uuid", "full_name", "first_name", "middle_name", "last_name"]
                    ),
                )


class TestGetCsrfToken(TestCase):

    def setUp(self):
        self.config = WuttaConfig()
        self.request = testing.DummyRequest(wutta_config=self.config)

    def test_same_token(self):

        # same token returned for same request
        # TODO: dummy request is always returning same token!
        # so this isn't really testing anything.. :(
        first = mod.get_csrf_token(self.request)
        self.assertIsNotNone(first)
        second = mod.get_csrf_token(self.request)
        self.assertEqual(first, second)

        # TODO: ideally would make a new request here and confirm it
        # gets a different token, but see note above..

    def test_new_token(self):

        # nb. dummy request always returns same token, so must
        # trick it into thinking it doesn't have one yet
        with patch.object(self.request.session, "get_csrf_token", return_value=None):
            token = mod.get_csrf_token(self.request)
            self.assertIsNotNone(token)


class TestRenderCsrfToken(TestCase):

    def setUp(self):
        self.config = WuttaConfig()
        self.request = testing.DummyRequest(wutta_config=self.config)

    def test_basics(self):
        html = mod.render_csrf_token(self.request)
        self.assertIn('type="hidden"', html)
        self.assertIn('name="_csrf"', html)
        token = mod.get_csrf_token(self.request)
        self.assertIn(f'value="{token}"', html)


class TestMakeJsonSafe(TestCase):

    def setUp(self):
        self.config = WuttaConfig()
        self.app = self.config.get_app()

    def test_null(self):
        value = mod.make_json_safe(colander.null)
        self.assertIsNone(value)

        value = mod.make_json_safe(None)
        self.assertIsNone(value)

    def test_invalid(self):
        model = self.app.model
        person = model.Person(full_name="Betty Boop")
        self.assertRaises(TypeError, json.dumps, person)
        value = mod.make_json_safe(person, key="person")
        self.assertEqual(value, "Betty Boop")

    def test_uuid(self):
        uuid = _uuid.uuid4()
        value = mod.make_json_safe(uuid)
        self.assertEqual(value, uuid.hex)

    def test_decimal(self):
        value = decimal.Decimal("42.42")
        self.assertNotEqual(value, 42.42)
        result = mod.make_json_safe(value)
        self.assertEqual(result, 42.42)

    def test_dict(self):
        model = self.app.model
        person = model.Person(full_name="Betty Boop")

        data = {
            "foo": "bar",
            "person": person,
        }

        self.assertRaises(TypeError, json.dumps, data)
        value = mod.make_json_safe(data)
        self.assertEqual(
            value,
            {
                "foo": "bar",
                "person": "Betty Boop",
            },
        )

    def test_list(self):
        model = self.app.model
        person = model.Person(full_name="Betty Boop")

        data = [
            "foo",
            "bar",
            person,
        ]

        self.assertRaises(TypeError, json.dumps, data)
        value = mod.make_json_safe(data)
        self.assertEqual(
            value,
            [
                "foo",
                "bar",
                "Betty Boop",
            ],
        )


class TestRenderVueFinalize(TestCase):

    def basic(self):
        html = mod.render_vue_finalize("wutta-grid", "WuttaGrid")
        self.assertIn("<script>", html)
        self.assertIn("Vue.component('wutta-grid', WuttaGrid)", html)


class TestMakeUsersGrid(WebTestCase):

    def test_make_users_grid(self):
        self.pyramid_config.add_route("users.view", "/users/{uuid}/view")
        self.pyramid_config.add_route("users.edit", "/users/{uuid}/edit")
        model = self.app.model
        person = model.Person(full_name="John Doe")
        self.session.add(person)
        user = model.User(username="john", person=person)
        self.session.add(user)
        self.session.commit()

        # basic (no actions because not prvileged)
        grid = mod.make_users_grid(self.request, key="blah.users", data=person.users)
        self.assertIsInstance(grid, Grid)
        self.assertFalse(grid.linked_columns)
        self.assertFalse(grid.actions)

        # key may be derived from route_prefix
        grid = mod.make_users_grid(self.request, route_prefix="foo")
        self.assertIsInstance(grid, Grid)
        self.assertEqual(grid.key, "foo.view.users")

        # view + edit actions (because root)
        with patch.object(self.request, "is_root", new=True):
            grid = mod.make_users_grid(
                self.request, key="blah.users", data=person.users
            )
            self.assertIsInstance(grid, Grid)
            self.assertIn("username", grid.linked_columns)
            self.assertEqual(len(grid.actions), 2)
            self.assertEqual(grid.actions[0].key, "view")
            self.assertEqual(grid.actions[1].key, "edit")

            # render grid to ensure coverage for link urls
            grid.render_vue_template()


class TestGetAvailableThemes(TestCase):

    def setUp(self):
        self.config = WuttaConfig()
        self.app = self.config.get_app()

    def test_defaults(self):
        themes = mod.get_available_themes(self.config)
        self.assertEqual(themes, ["default", "butterfly"])

    def test_sorting(self):
        self.config.setdefault("wuttaweb.themes.keys", "default, foo2, foo4, foo1")
        themes = mod.get_available_themes(self.config)
        self.assertEqual(themes, ["default", "foo1", "foo2", "foo4"])

    def test_default_omitted(self):
        self.config.setdefault("wuttaweb.themes.keys", "butterfly, foo")
        themes = mod.get_available_themes(self.config)
        self.assertEqual(themes, ["default", "butterfly", "foo"])

    def test_default_notfirst(self):
        self.config.setdefault("wuttaweb.themes.keys", "butterfly, foo, default")
        themes = mod.get_available_themes(self.config)
        self.assertEqual(themes, ["default", "butterfly", "foo"])


class TestGetEffectiveTheme(DataTestCase):

    def test_default(self):
        theme = mod.get_effective_theme(self.config)
        self.assertEqual(theme, "default")

    def test_override_config(self):
        self.app.save_setting(self.session, "wuttaweb.theme", "butterfly")
        self.session.commit()
        theme = mod.get_effective_theme(self.config)
        self.assertEqual(theme, "butterfly")

    def test_override_param(self):
        theme = mod.get_effective_theme(self.config, theme="butterfly")
        self.assertEqual(theme, "butterfly")

    def test_invalid(self):
        self.assertRaises(
            ValueError, mod.get_effective_theme, self.config, theme="invalid"
        )


class TestThemeTemplatePath(DataTestCase):

    def test_default(self):
        path = mod.get_theme_template_path(self.config, theme="default")
        # nb. even though the path does not exist, we still want to
        # pretend like it does, hence prev call should return this:
        expected = resource_path("wuttaweb:templates/themes/default")
        self.assertEqual(path, expected)

    def test_default(self):
        path = mod.get_theme_template_path(self.config, theme="butterfly")
        expected = resource_path("wuttaweb:templates/themes/butterfly")
        self.assertEqual(path, expected)

    def test_custom(self):
        self.config.setdefault("wuttaweb.themes.keys", "default, butterfly, poser")
        self.config.setdefault("wuttaweb.theme.poser", "/tmp/poser-theme")
        path = mod.get_theme_template_path(self.config, theme="poser")
        self.assertEqual(path, "/tmp/poser-theme")


class TestSetAppTheme(WebTestCase):

    def test_basic(self):

        # establish default
        settings = self.request.registry.settings
        self.assertNotIn("wuttaweb.theme", settings)
        establish_theme(settings)
        self.assertEqual(settings["wuttaweb.theme"], "default")

        # set to butterfly
        mod.set_app_theme(self.request, "butterfly", session=self.session)
        self.assertEqual(settings["wuttaweb.theme"], "butterfly")

        # set back to default
        mod.set_app_theme(self.request, "default", session=self.session)
        self.assertEqual(settings["wuttaweb.theme"], "default")
