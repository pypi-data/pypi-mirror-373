# -*- coding: utf-8; -*-

import datetime
import decimal
import functools
from unittest import TestCase
from unittest.mock import MagicMock, patch

from sqlalchemy import orm
from pyramid import testing
from pyramid.response import Response
from pyramid.httpexceptions import HTTPNotFound

from wuttjamaican.conf import WuttaConfig
from wuttaweb.views import master as mod
from wuttaweb.views import View
from wuttaweb.progress import SessionProgress
from wuttaweb.subscribers import new_request_set_user
from wuttaweb.testing import WebTestCase


class TestMasterView(WebTestCase):

    def make_view(self):
        return mod.MasterView(self.request)

    def test_defaults(self):
        with patch.multiple(
            mod.MasterView,
            create=True,
            model_name="Widget",
            model_key="uuid",
            deletable_bulk=True,
            has_autocomplete=True,
            downloadable=True,
            executable=True,
            configurable=True,
        ):
            mod.MasterView.defaults(self.pyramid_config)

    ##############################
    # class methods
    ##############################

    def test_get_model_class(self):

        # no model class by default
        self.assertIsNone(mod.MasterView.get_model_class())

        # subclass may specify
        MyModel = MagicMock()
        with patch.multiple(mod.MasterView, create=True, model_class=MyModel):
            self.assertIs(mod.MasterView.get_model_class(), MyModel)

    def test_get_model_name(self):

        # error by default (since no model class)
        self.assertRaises(AttributeError, mod.MasterView.get_model_name)

        # subclass may specify model name
        with patch.multiple(mod.MasterView, create=True, model_name="Widget"):
            self.assertEqual(mod.MasterView.get_model_name(), "Widget")

        # or it may specify model class
        MyModel = MagicMock(__name__="Blaster")
        with patch.multiple(mod.MasterView, create=True, model_class=MyModel):
            self.assertEqual(mod.MasterView.get_model_name(), "Blaster")

    def test_get_model_name_normalized(self):

        # error by default (since no model class)
        self.assertRaises(AttributeError, mod.MasterView.get_model_name_normalized)

        # subclass may specify *normalized* model name
        with patch.multiple(
            mod.MasterView, create=True, model_name_normalized="widget"
        ):
            self.assertEqual(mod.MasterView.get_model_name_normalized(), "widget")

        # or it may specify *standard* model name
        with patch.multiple(mod.MasterView, create=True, model_name="Blaster"):
            self.assertEqual(mod.MasterView.get_model_name_normalized(), "blaster")

        # or it may specify model class
        MyModel = MagicMock(__name__="Dinosaur")
        with patch.multiple(mod.MasterView, create=True, model_class=MyModel):
            self.assertEqual(mod.MasterView.get_model_name_normalized(), "dinosaur")

    def test_get_model_title(self):

        # error by default (since no model class)
        self.assertRaises(AttributeError, mod.MasterView.get_model_title)

        # subclass may specify  model title
        with patch.multiple(mod.MasterView, create=True, model_title="Wutta Widget"):
            self.assertEqual(mod.MasterView.get_model_title(), "Wutta Widget")

        # or it may specify model name
        with patch.multiple(mod.MasterView, create=True, model_name="Blaster"):
            self.assertEqual(mod.MasterView.get_model_title(), "Blaster")

        # or it may specify model class
        MyModel = MagicMock(__name__="Dinosaur")
        with patch.multiple(mod.MasterView, create=True, model_class=MyModel):
            self.assertEqual(mod.MasterView.get_model_title(), "Dinosaur")

    def test_get_model_title_plural(self):

        # error by default (since no model class)
        self.assertRaises(AttributeError, mod.MasterView.get_model_title_plural)

        # subclass may specify *plural* model title
        with patch.multiple(mod.MasterView, create=True, model_title_plural="People"):
            self.assertEqual(mod.MasterView.get_model_title_plural(), "People")

        # or it may specify *singular* model title
        with patch.multiple(mod.MasterView, create=True, model_title="Wutta Widget"):
            self.assertEqual(mod.MasterView.get_model_title_plural(), "Wutta Widgets")

        # or it may specify model name
        with patch.multiple(mod.MasterView, create=True, model_name="Blaster"):
            self.assertEqual(mod.MasterView.get_model_title_plural(), "Blasters")

        # or it may specify model class
        MyModel = MagicMock(__name__="Dinosaur")
        with patch.multiple(mod.MasterView, create=True, model_class=MyModel):
            self.assertEqual(mod.MasterView.get_model_title_plural(), "Dinosaurs")

    def test_get_model_key(self):

        # error by default (since no model class)
        self.assertRaises(AttributeError, mod.MasterView.get_model_key)

        # subclass may specify model key
        with patch.multiple(mod.MasterView, create=True, model_key="uuid"):
            self.assertEqual(mod.MasterView.get_model_key(), ("uuid",))

    def test_get_route_prefix(self):

        # error by default (since no model class)
        self.assertRaises(AttributeError, mod.MasterView.get_route_prefix)

        # subclass may specify route prefix
        with patch.multiple(mod.MasterView, create=True, route_prefix="widgets"):
            self.assertEqual(mod.MasterView.get_route_prefix(), "widgets")

        # subclass may specify *normalized* model name
        with patch.multiple(
            mod.MasterView, create=True, model_name_normalized="blaster"
        ):
            self.assertEqual(mod.MasterView.get_route_prefix(), "blasters")

        # or it may specify *standard* model name
        with patch.multiple(mod.MasterView, create=True, model_name="Dinosaur"):
            self.assertEqual(mod.MasterView.get_route_prefix(), "dinosaurs")

        # or it may specify model class
        MyModel = MagicMock(__name__="Truck")
        with patch.multiple(mod.MasterView, create=True, model_class=MyModel):
            self.assertEqual(mod.MasterView.get_route_prefix(), "trucks")

    def test_get_permission_prefix(self):

        # error by default (since no model class)
        self.assertRaises(AttributeError, mod.MasterView.get_permission_prefix)

        # subclass may specify permission prefix
        with patch.object(
            mod.MasterView, "permission_prefix", new="widgets", create=True
        ):
            self.assertEqual(mod.MasterView.get_permission_prefix(), "widgets")

        # subclass may specify route prefix
        with patch.object(mod.MasterView, "route_prefix", new="widgets", create=True):
            self.assertEqual(mod.MasterView.get_permission_prefix(), "widgets")

        # or it may specify model class
        Truck = MagicMock(__name__="Truck")
        with patch.object(mod.MasterView, "model_class", new=Truck, create=True):
            self.assertEqual(mod.MasterView.get_permission_prefix(), "trucks")

    def test_get_url_prefix(self):

        # error by default (since no model class)
        self.assertRaises(AttributeError, mod.MasterView.get_url_prefix)

        # subclass may specify url prefix
        with patch.multiple(mod.MasterView, create=True, url_prefix="/widgets"):
            self.assertEqual(mod.MasterView.get_url_prefix(), "/widgets")

        # or it may specify route prefix
        with patch.multiple(mod.MasterView, create=True, route_prefix="trucks"):
            self.assertEqual(mod.MasterView.get_url_prefix(), "/trucks")

        # or it may specify *normalized* model name
        with patch.multiple(
            mod.MasterView, create=True, model_name_normalized="blaster"
        ):
            self.assertEqual(mod.MasterView.get_url_prefix(), "/blasters")

        # or it may specify *standard* model name
        with patch.multiple(mod.MasterView, create=True, model_name="Dinosaur"):
            self.assertEqual(mod.MasterView.get_url_prefix(), "/dinosaurs")

        # or it may specify model class
        MyModel = MagicMock(__name__="Machine")
        with patch.multiple(mod.MasterView, create=True, model_class=MyModel):
            self.assertEqual(mod.MasterView.get_url_prefix(), "/machines")

    def test_get_instance_url_prefix(self):

        # error by default (since no model class)
        self.assertRaises(AttributeError, mod.MasterView.get_instance_url_prefix)

        # typical example with url_prefix and simple key
        with patch.multiple(
            mod.MasterView, create=True, url_prefix="/widgets", model_key="uuid"
        ):
            self.assertEqual(
                mod.MasterView.get_instance_url_prefix(), "/widgets/{uuid}"
            )

        # typical example with composite key
        with patch.multiple(
            mod.MasterView, create=True, url_prefix="/widgets", model_key=("foo", "bar")
        ):
            self.assertEqual(
                mod.MasterView.get_instance_url_prefix(), "/widgets/{foo}|{bar}"
            )

    def test_get_template_prefix(self):

        # error by default (since no model class)
        self.assertRaises(AttributeError, mod.MasterView.get_template_prefix)

        # subclass may specify template prefix
        with patch.multiple(mod.MasterView, create=True, template_prefix="/widgets"):
            self.assertEqual(mod.MasterView.get_template_prefix(), "/widgets")

        # or it may specify url prefix
        with patch.multiple(mod.MasterView, create=True, url_prefix="/trees"):
            self.assertEqual(mod.MasterView.get_template_prefix(), "/trees")

        # or it may specify route prefix
        with patch.multiple(mod.MasterView, create=True, route_prefix="trucks"):
            self.assertEqual(mod.MasterView.get_template_prefix(), "/trucks")

        # or it may specify *normalized* model name
        with patch.multiple(
            mod.MasterView, create=True, model_name_normalized="blaster"
        ):
            self.assertEqual(mod.MasterView.get_template_prefix(), "/blasters")

        # or it may specify *standard* model name
        with patch.multiple(mod.MasterView, create=True, model_name="Dinosaur"):
            self.assertEqual(mod.MasterView.get_template_prefix(), "/dinosaurs")

        # or it may specify model class
        MyModel = MagicMock(__name__="Machine")
        with patch.multiple(mod.MasterView, create=True, model_class=MyModel):
            self.assertEqual(mod.MasterView.get_template_prefix(), "/machines")

    def test_get_grid_key(self):

        # error by default (since no model class)
        self.assertRaises(AttributeError, mod.MasterView.get_grid_key)

        # subclass may specify grid key
        with patch.multiple(mod.MasterView, create=True, grid_key="widgets"):
            self.assertEqual(mod.MasterView.get_grid_key(), "widgets")

        # or it may specify route prefix
        with patch.multiple(mod.MasterView, create=True, route_prefix="trucks"):
            self.assertEqual(mod.MasterView.get_grid_key(), "trucks")

        # or it may specify *normalized* model name
        with patch.multiple(
            mod.MasterView, create=True, model_name_normalized="blaster"
        ):
            self.assertEqual(mod.MasterView.get_grid_key(), "blasters")

        # or it may specify *standard* model name
        with patch.multiple(mod.MasterView, create=True, model_name="Dinosaur"):
            self.assertEqual(mod.MasterView.get_grid_key(), "dinosaurs")

        # or it may specify model class
        MyModel = MagicMock(__name__="Machine")
        with patch.multiple(mod.MasterView, create=True, model_class=MyModel):
            self.assertEqual(mod.MasterView.get_grid_key(), "machines")

    def test_get_config_title(self):

        # error by default (since no model class)
        self.assertRaises(AttributeError, mod.MasterView.get_config_title)

        # subclass may specify config title
        with patch.multiple(mod.MasterView, create=True, config_title="Widgets"):
            self.assertEqual(mod.MasterView.get_config_title(), "Widgets")

        # subclass may specify *plural* model title
        with patch.multiple(mod.MasterView, create=True, model_title_plural="People"):
            self.assertEqual(mod.MasterView.get_config_title(), "People")

        # or it may specify *singular* model title
        with patch.multiple(mod.MasterView, create=True, model_title="Wutta Widget"):
            self.assertEqual(mod.MasterView.get_config_title(), "Wutta Widgets")

        # or it may specify model name
        with patch.multiple(mod.MasterView, create=True, model_name="Blaster"):
            self.assertEqual(mod.MasterView.get_config_title(), "Blasters")

        # or it may specify model class
        MyModel = MagicMock(__name__="Dinosaur")
        with patch.multiple(mod.MasterView, create=True, model_class=MyModel):
            self.assertEqual(mod.MasterView.get_config_title(), "Dinosaurs")

    def test_get_row_model_class(self):
        model = self.app.model

        # no default
        self.assertIsNone(mod.MasterView.get_row_model_class())

        # class may specify
        with patch.object(
            mod.MasterView, "row_model_class", create=True, new=model.User
        ):
            self.assertIs(mod.MasterView.get_row_model_class(), model.User)

    ##############################
    # support methods
    ##############################

    def test_get_class_hierarchy(self):
        class MyView(mod.MasterView):
            pass

        view = MyView(self.request)
        classes = view.get_class_hierarchy()
        self.assertEqual(classes, [View, mod.MasterView, MyView])

    def test_has_perm(self):
        model = self.app.model
        auth = self.app.get_auth_handler()

        with patch.multiple(mod.MasterView, create=True, model_name="Setting"):
            view = self.make_view()

            # anonymous user
            self.assertFalse(view.has_perm("list"))
            self.assertFalse(self.request.has_perm("list"))

            # reset
            del self.request.user_permissions

            # make user with perms
            barney = model.User(username="barney")
            self.session.add(barney)
            blokes = model.Role(name="Blokes")
            self.session.add(blokes)
            barney.roles.append(blokes)
            auth.grant_permission(blokes, "settings.list")
            self.session.commit()

            # this user has perms
            self.request.user = barney
            self.assertTrue(view.has_perm("list"))
            self.assertTrue(self.request.has_perm("settings.list"))

    def test_has_any_perm(self):
        model = self.app.model
        auth = self.app.get_auth_handler()

        with patch.multiple(mod.MasterView, create=True, model_name="Setting"):
            view = self.make_view()

            # anonymous user
            self.assertFalse(view.has_any_perm("list", "view"))
            self.assertFalse(
                self.request.has_any_perm("settings.list", "settings.view")
            )

            # reset
            del self.request.user_permissions

            # make user with perms
            barney = model.User(username="barney")
            self.session.add(barney)
            blokes = model.Role(name="Blokes")
            self.session.add(blokes)
            barney.roles.append(blokes)
            auth.grant_permission(blokes, "settings.view")
            self.session.commit()

            # this user has perms
            self.request.user = barney
            self.assertTrue(view.has_any_perm("list", "view"))
            self.assertTrue(self.request.has_any_perm("settings.list", "settings.view"))

    def test_make_button(self):
        view = self.make_view()

        # normal
        html = view.make_button("click me")
        self.assertIn("<b-button ", html)
        self.assertIn("click me", html)
        self.assertNotIn("is-primary", html)

        # primary as primary
        html = view.make_button("click me", primary=True)
        self.assertIn("<b-button ", html)
        self.assertIn("click me", html)
        self.assertIn("is-primary", html)

        # primary as variant
        html = view.make_button("click me", variant="is-primary")
        self.assertIn("<b-button ", html)
        self.assertIn("click me", html)
        self.assertIn("is-primary", html)

        # primary as type
        html = view.make_button("click me", type="is-primary")
        self.assertIn("<b-button ", html)
        self.assertIn("click me", html)
        self.assertIn("is-primary", html)

        # with url
        html = view.make_button("click me", url="http://example.com")
        self.assertIn('<b-button tag="a"', html)
        self.assertIn("click me", html)
        self.assertIn('href="http://example.com"', html)

    def test_make_progress(self):

        # basic
        view = self.make_view()
        self.request.session.id = "mockid"
        progress = view.make_progress("foo")
        self.assertIsInstance(progress, SessionProgress)

    def test_render_progress(self):
        self.pyramid_config.add_route("progress", "/progress/{key}")

        # sanity / coverage check
        view = self.make_view()
        progress = MagicMock()
        response = view.render_progress(progress)

    def test_render_to_response(self):
        self.pyramid_config.include("wuttaweb.views.common")
        self.pyramid_config.include("wuttaweb.views.auth")
        self.pyramid_config.add_route("appinfo", "/appinfo/")

        def widgets(request):
            return {}

        self.pyramid_config.add_route("widgets", "/widgets/")
        self.pyramid_config.add_view(widgets, route_name="widgets")

        # basic sanity check using /master/index.mako
        # (nb. it skips /widgets/index.mako since that doesn't exist)
        with patch.multiple(
            mod.MasterView, create=True, model_name="Widget", creatable=False
        ):
            view = mod.MasterView(self.request)
            response = view.render_to_response("index", {})
            self.assertIsInstance(response, Response)

        # basic sanity check using /appinfo/index.mako
        with patch.multiple(
            mod.MasterView,
            create=True,
            model_name="AppInfo",
            route_prefix="appinfo",
            url_prefix="/appinfo",
            creatable=False,
        ):
            view = mod.MasterView(self.request)
            response = view.render_to_response(
                "index",
                {
                    # nb. grid is required for this template
                    "grid": MagicMock(),
                },
            )
            self.assertIsInstance(response, Response)

        # bad template name causes error
        with patch.multiple(mod.MasterView, create=True, model_name="Widget"):
            self.assertRaises(IOError, view.render_to_response, "nonexistent", {})

    def test_get_index_title(self):
        with patch.multiple(
            mod.MasterView, create=True, model_title_plural="Wutta Widgets"
        ):
            view = mod.MasterView(self.request)
            self.assertEqual(view.get_index_title(), "Wutta Widgets")

    def test_get_index_url(self):
        self.pyramid_config.add_route("widgets", "/widgets")
        with patch.multiple(mod.MasterView, create=True, model_name="Widget"):

            # normal
            view = self.make_view()
            self.assertEqual(view.get_index_url(), "http://example.com/widgets")

            # list/index not supported
            view = self.make_view()
            view.listable = False
            self.assertIsNone(view.get_index_url())

    def test_collect_labels(self):

        # no labels by default
        view = self.make_view()
        labels = view.collect_labels()
        self.assertEqual(labels, {})

        # labels come from all classes; subclass wins
        with patch.object(
            View, "labels", new={"foo": "Foo", "bar": "Bar"}, create=True
        ):
            with patch.object(
                mod.MasterView, "labels", new={"foo": "FOO FIGHTERS"}, create=True
            ):
                view = self.make_view()
                labels = view.collect_labels()
                self.assertEqual(labels, {"foo": "FOO FIGHTERS", "bar": "Bar"})

    def test_set_labels(self):
        model = self.app.model
        with patch.object(
            mod.MasterView, "model_class", new=model.Setting, create=True
        ):

            # no labels by default
            view = self.make_view()
            grid = view.make_model_grid(session=self.session)
            view.set_labels(grid)
            self.assertEqual(grid.labels, {})

            # labels come from all classes; subclass wins
            with patch.object(
                mod.MasterView, "labels", new={"name": "SETTING NAME"}, create=True
            ):
                view = self.make_view()
                view.set_labels(grid)
                self.assertEqual(grid.labels, {"name": "SETTING NAME"})

    def test_make_model_grid(self):
        self.pyramid_config.add_route("settings.delete_bulk", "/settings/delete-bulk")
        model = self.app.model

        # no model class
        with patch.multiple(
            mod.MasterView, create=True, model_name="Widget", model_key="uuid"
        ):
            view = mod.MasterView(self.request)
            grid = view.make_model_grid()
            self.assertIsNone(grid.model_class)

        # explicit model class
        with patch.multiple(mod.MasterView, create=True, model_class=model.Setting):
            grid = view.make_model_grid(session=self.session)
            self.assertIs(grid.model_class, model.Setting)

        # no row class by default
        with patch.multiple(mod.MasterView, create=True, model_class=model.Setting):
            grid = view.make_model_grid(session=self.session)
            self.assertIsNone(grid.row_class)

        # can specify row class
        get_row_class = MagicMock()
        with patch.multiple(
            mod.MasterView,
            create=True,
            model_class=model.Setting,
            grid_row_class=get_row_class,
        ):
            grid = view.make_model_grid(session=self.session)
            self.assertIs(grid.row_class, get_row_class)

        # no actions by default
        with patch.multiple(mod.MasterView, create=True, model_class=model.Setting):
            grid = view.make_model_grid(session=self.session)
            self.assertEqual(grid.actions, [])

        # now let's test some more actions logic
        with patch.multiple(
            mod.MasterView,
            create=True,
            model_class=model.Setting,
            viewable=True,
            editable=True,
            deletable=True,
        ):

            # should have 3 actions now, but for lack of perms
            grid = view.make_model_grid(session=self.session)
            self.assertEqual(len(grid.actions), 0)

            # but root user has perms, so gets 3 actions
            with patch.object(self.request, "is_root", new=True):
                grid = view.make_model_grid(session=self.session)
            self.assertEqual(len(grid.actions), 3)

        # no tools by default
        with patch.multiple(mod.MasterView, create=True, model_class=model.Setting):
            grid = view.make_model_grid(session=self.session)
            self.assertEqual(grid.tools, {})

        # delete-results tool added if master/perms allow
        with patch.multiple(
            mod.MasterView, create=True, model_class=model.Setting, deletable_bulk=True
        ):
            with patch.object(self.request, "is_root", new=True):
                grid = view.make_model_grid(session=self.session)
                self.assertIn("delete-results", grid.tools)

    def test_get_grid_data(self):
        model = self.app.model
        self.app.save_setting(self.session, "foo", "bar")
        self.session.commit()
        setting = self.session.query(model.Setting).one()
        view = self.make_view()

        # empty by default
        self.assertIsNone(mod.MasterView.model_class)
        data = view.get_grid_data(session=self.session)
        self.assertEqual(data, [])

        # grid with model class will produce data query
        with patch.multiple(mod.MasterView, create=True, model_class=model.Setting):
            view = mod.MasterView(self.request)
            query = view.get_grid_data(session=self.session)
            self.assertIsInstance(query, orm.Query)
            data = query.all()
            self.assertEqual(len(data), 1)
            self.assertIs(data[0], setting)

    def test_configure_grid(self):
        model = self.app.model

        # uuid field is pruned
        with patch.multiple(mod.MasterView, create=True, model_class=model.Setting):
            view = mod.MasterView(self.request)
            grid = view.make_grid(
                model_class=model.Setting, columns=["uuid", "name", "value"]
            )
            self.assertIn("uuid", grid.columns)
            view.configure_grid(grid)
            self.assertNotIn("uuid", grid.columns)

    def test_grid_render_bool(self):
        model = self.app.model
        view = self.make_view()
        user = model.User(username="barney", active=None)

        # null
        value = view.grid_render_bool(user, "active", None)
        self.assertIsNone(value)

        # true
        user.active = True
        value = view.grid_render_bool(user, "active", True)
        self.assertEqual(value, "Yes")

        # false
        user.active = False
        value = view.grid_render_bool(user, "active", False)
        self.assertEqual(value, "No")

    def test_grid_render_currency(self):
        view = self.make_view()
        obj = {"amount": None}

        # null
        value = view.grid_render_currency(obj, "amount", None)
        self.assertIsNone(value)

        # normal amount
        obj["amount"] = decimal.Decimal("100.42")
        value = view.grid_render_currency(obj, "amount", "100.42")
        self.assertEqual(value, "$100.42")

        # negative amount
        obj["amount"] = decimal.Decimal("-100.42")
        value = view.grid_render_currency(obj, "amount", "-100.42")
        self.assertEqual(value, "($100.42)")

    def test_grid_render_datetime(self):
        view = self.make_view()
        obj = {"dt": None}

        # null
        value = view.grid_render_datetime(obj, "dt", None)
        self.assertIsNone(value)

        # normal
        obj["dt"] = datetime.datetime(2024, 8, 24, 11)
        value = view.grid_render_datetime(obj, "dt", "2024-08-24T11:00:00")
        self.assertEqual(value, "2024-08-24 11:00:00 AM")

    def test_grid_render_enum(self):
        enum = self.app.enum
        view = self.make_view()
        obj = {"status": None}

        # null
        value = view.grid_render_enum(obj, "status", None, enum=enum.UpgradeStatus)
        self.assertIsNone(value)

        # normal
        obj["status"] = enum.UpgradeStatus.SUCCESS
        value = view.grid_render_enum(obj, "status", "SUCCESS", enum=enum.UpgradeStatus)
        self.assertEqual(value, "SUCCESS")

    def test_grid_render_notes(self):
        model = self.app.model
        view = self.make_view()

        # null
        text = None
        role = model.Role(name="Foo", notes=text)
        value = view.grid_render_notes(role, "notes", text)
        self.assertIsNone(value)

        # short string
        text = "hello world"
        role = model.Role(name="Foo", notes=text)
        value = view.grid_render_notes(role, "notes", text)
        self.assertEqual(value, text)

        # long string
        text = "hello world " * 20
        role = model.Role(name="Foo", notes=text)
        value = view.grid_render_notes(role, "notes", text)
        self.assertIn("<span ", value)

    def test_get_instance(self):
        model = self.app.model
        self.app.save_setting(self.session, "foo", "bar")
        self.session.commit()
        self.assertEqual(self.session.query(model.Setting).count(), 1)

        # default not implemented
        view = mod.MasterView(self.request)
        self.assertRaises(NotImplementedError, view.get_instance)

        # fetch from DB if model class is known
        with patch.multiple(mod.MasterView, create=True, model_class=model.Setting):
            view = mod.MasterView(self.request)

            # existing setting is returned
            self.request.matchdict = {"name": "foo"}
            setting = view.get_instance(session=self.session)
            self.assertIsInstance(setting, model.Setting)
            self.assertEqual(setting.name, "foo")
            self.assertEqual(setting.value, "bar")

            # missing setting not found
            self.request.matchdict = {"name": "blarg"}
            self.assertRaises(HTTPNotFound, view.get_instance, session=self.session)

    def test_get_action_route_kwargs(self):
        model = self.app.model
        with patch.object(
            mod.MasterView, "model_class", new=model.Setting, create=True
        ):
            view = self.make_view()

            # dict object
            setting = {"name": "foo", "value": "bar"}
            kw = view.get_action_route_kwargs(setting)
            self.assertEqual(kw, {"name": "foo"})

            # mapped object
            setting = model.Setting(name="foo", value="bar")
            kw = view.get_action_route_kwargs(setting)
            self.assertEqual(kw, {"name": "foo"})

            # non-standard object
            class MySetting:
                def __init__(self, **kw):
                    self.__dict__.update(kw)

            setting = MySetting(name="foo", value="bar")
            kw = view.get_action_route_kwargs(setting)
            self.assertEqual(kw, {"name": "foo"})

    def test_get_action_url_for_dict(self):
        model = self.app.model
        setting = {"name": "foo", "value": "bar"}
        with patch.multiple(mod.MasterView, create=True, model_class=model.Setting):
            mod.MasterView.defaults(self.pyramid_config)
            view = self.make_view()
            url = view.get_action_url_view(setting, 0)
            self.assertEqual(url, self.request.route_url("settings.view", name="foo"))

    def test_get_action_url_for_orm_object(self):
        model = self.app.model
        setting = model.Setting(name="foo", value="bar")
        self.session.add(setting)
        self.session.commit()
        with patch.multiple(mod.MasterView, create=True, model_class=model.Setting):
            mod.MasterView.defaults(self.pyramid_config)
            view = self.make_view()
            url = view.get_action_url_view(setting, 0)
            self.assertEqual(url, self.request.route_url("settings.view", name="foo"))

    def test_get_action_url_for_adhoc_object(self):
        model = self.app.model

        class MockSetting:
            def __init__(self, **kw):
                self.__dict__.update(kw)

        setting = MockSetting(name="foo", value="bar")
        with patch.multiple(mod.MasterView, create=True, model_class=model.Setting):
            mod.MasterView.defaults(self.pyramid_config)
            view = self.make_view()
            url = view.get_action_url_view(setting, 0)
            self.assertEqual(url, self.request.route_url("settings.view", name="foo"))

    def test_get_action_url_view(self):
        model = self.app.model
        setting = model.Setting(name="foo", value="bar")
        self.session.add(setting)
        self.session.commit()

        with patch.multiple(mod.MasterView, create=True, model_class=model.Setting):
            mod.MasterView.defaults(self.pyramid_config)
            view = self.make_view()
            url = view.get_action_url_view(setting, 0)
            self.assertEqual(url, self.request.route_url("settings.view", name="foo"))

    def test_get_action_url_edit(self):
        model = self.app.model
        setting = model.Setting(name="foo", value="bar")
        self.session.add(setting)
        self.session.commit()
        with patch.multiple(mod.MasterView, create=True, model_class=model.Setting):
            mod.MasterView.defaults(self.pyramid_config)
            view = self.make_view()

            # typical
            url = view.get_action_url_edit(setting, 0)
            self.assertEqual(url, self.request.route_url("settings.edit", name="foo"))

            # but null if instance not editable
            with patch.object(view, "is_editable", return_value=False):
                url = view.get_action_url_edit(setting, 0)
                self.assertIsNone(url)

    def test_get_action_url_delete(self):
        model = self.app.model
        setting = model.Setting(name="foo", value="bar")
        self.session.add(setting)
        self.session.commit()
        with patch.multiple(mod.MasterView, create=True, model_class=model.Setting):
            mod.MasterView.defaults(self.pyramid_config)
            view = self.make_view()

            # typical
            url = view.get_action_url_delete(setting, 0)
            self.assertEqual(url, self.request.route_url("settings.delete", name="foo"))

            # but null if instance not deletable
            with patch.object(view, "is_deletable", return_value=False):
                url = view.get_action_url_delete(setting, 0)
                self.assertIsNone(url)

    def test_make_model_form(self):
        model = self.app.model

        # no model class
        with patch.multiple(
            mod.MasterView, create=True, model_name="Widget", model_key="uuid"
        ):
            view = mod.MasterView(self.request)
            form = view.make_model_form()
            self.assertIsNone(form.model_class)

        # explicit model class
        with patch.multiple(mod.MasterView, create=True, model_class=model.Setting):
            form = view.make_model_form()
            self.assertIs(form.model_class, model.Setting)

    def test_configure_form(self):
        model = self.app.model

        # uuid field is pruned
        with patch.multiple(mod.MasterView, create=True, model_class=model.Setting):
            view = mod.MasterView(self.request)
            form = view.make_form(
                model_class=model.Setting, fields=["uuid", "name", "value"]
            )
            self.assertIn("uuid", form.fields)
            view.configure_form(form)
            self.assertNotIn("uuid", form.fields)

    def test_objectify(self):
        model = self.app.model
        self.app.save_setting(self.session, "foo", "bar")
        self.session.commit()
        self.assertEqual(self.session.query(model.Setting).count(), 1)

        # no model class
        with patch.multiple(
            mod.MasterView, create=True, model_name="Widget", model_key="uuid"
        ):
            view = mod.MasterView(self.request)
            form = view.make_model_form(fields=["name", "description"])
            form.validated = {"name": "first"}
            obj = view.objectify(form)
            self.assertIs(obj, form.validated)

        # explicit model class (editing)
        with patch.multiple(
            mod.MasterView, create=True, model_class=model.Setting, editing=True
        ):
            form = view.make_model_form()
            form.validated = {"name": "foo", "value": "blarg"}
            form.model_instance = self.session.query(model.Setting).one()
            obj = view.objectify(form)
            self.assertIsInstance(obj, model.Setting)
            self.assertEqual(obj.name, "foo")
            self.assertEqual(obj.value, "blarg")

        # explicit model class (creating)
        with patch.multiple(
            mod.MasterView, create=True, model_class=model.Setting, creating=True
        ):
            form = view.make_model_form()
            form.validated = {"name": "another", "value": "whatever"}
            obj = view.objectify(form)
            self.assertIsInstance(obj, model.Setting)
            self.assertEqual(obj.name, "another")
            self.assertEqual(obj.value, "whatever")

    def test_persist(self):
        model = self.app.model
        with patch.multiple(mod.MasterView, create=True, model_class=model.Setting):
            view = mod.MasterView(self.request)

            # new instance is persisted
            setting = model.Setting(name="foo", value="bar")
            self.assertEqual(self.session.query(model.Setting).count(), 0)
            view.persist(setting, session=self.session)
            self.session.commit()
            setting = self.session.query(model.Setting).one()
            self.assertEqual(setting.name, "foo")
            self.assertEqual(setting.value, "bar")

    ##############################
    # view methods
    ##############################

    def test_index(self):
        self.pyramid_config.include("wuttaweb.views.common")
        self.pyramid_config.include("wuttaweb.views.auth")
        self.pyramid_config.add_route("settings.create", "/settings/new")
        self.pyramid_config.add_route("settings.view", "/settings/{name}")
        self.pyramid_config.add_route("settings.edit", "/settings/{name}/edit")
        self.pyramid_config.add_route("settings.delete", "/settings/{name}/delete")

        # sanity/coverage check using /settings/
        with patch.multiple(
            mod.MasterView,
            create=True,
            model_name="Setting",
            model_key="name",
            get_index_url=MagicMock(return_value="/settings/"),
            grid_columns=["name", "value"],
        ):
            view = mod.MasterView(self.request)
            response = view.index()

            # then again with data, to include view action url
            data = [{"name": "foo", "value": "bar"}]
            with patch.object(view, "get_grid_data", return_value=data):
                response = view.index()
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.content_type, "text/html")

                # then once more as 'partial' - aka. data only
                self.request.GET = {"partial": "1"}
                response = view.index()
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.content_type, "application/json")

                # redirects when view is reset
                self.request.GET = {"reset-view": "1", "hash": "foo"}
                with patch.object(self.request, "current_route_url"):
                    response = view.index()
                self.assertEqual(response.status_code, 302)

    def test_create(self):
        self.pyramid_config.include("wuttaweb.views.common")
        self.pyramid_config.include("wuttaweb.views.auth")
        self.pyramid_config.add_route("settings.view", "/settings/{name}")
        model = self.app.model

        # sanity/coverage check using /settings/new
        with patch.multiple(
            mod.MasterView,
            create=True,
            model_name="Setting",
            model_key="name",
            get_index_url=MagicMock(return_value="/settings/"),
            form_fields=["name", "value"],
        ):
            view = mod.MasterView(self.request)

            # no setting yet
            self.assertIsNone(self.app.get_setting(self.session, "foo.bar"))

            # get the form page
            response = view.create()
            self.assertIsInstance(response, Response)
            self.assertEqual(response.status_code, 200)
            # self.assertIn('frazzle', response.text)
            # nb. no error
            self.assertNotIn("Required", response.text)

            def persist(setting):
                self.app.save_setting(self.session, setting["name"], setting["value"])
                self.session.commit()

            # post request to save setting
            self.request.method = "POST"
            self.request.POST = {
                "name": "foo.bar",
                "value": "fraggle",
            }
            with patch.object(view, "persist", new=persist):
                response = view.create()
            # nb. should get redirect back to view page
            self.assertEqual(response.status_code, 302)
            # setting should now be in DB
            self.assertEqual(self.app.get_setting(self.session, "foo.bar"), "fraggle")

            # try another post with invalid data (value is required)
            self.request.method = "POST"
            self.request.POST = {}
            with patch.object(view, "persist", new=persist):
                response = view.create()
            # nb. should get a form with errors
            self.assertEqual(response.status_code, 200)
            self.assertIn("Required", response.text)
            # setting did not change in DB
            self.assertEqual(self.app.get_setting(self.session, "foo.bar"), "fraggle")

    def test_view(self):
        self.pyramid_config.include("wuttaweb.views.common")
        self.pyramid_config.include("wuttaweb.views.auth")
        self.pyramid_config.add_route("settings.create", "/settings/new")
        self.pyramid_config.add_route("settings.edit", "/settings/{name}/edit")
        self.pyramid_config.add_route("settings.delete", "/settings/{name}/delete")

        # sanity/coverage check using /settings/XXX
        setting = {"name": "foo.bar", "value": "baz"}
        self.request.matchdict = {"name": "foo.bar"}
        with patch.multiple(
            mod.MasterView,
            create=True,
            model_name="Setting",
            model_key="name",
            get_index_url=MagicMock(return_value="/settings/"),
            grid_columns=["name", "value"],
            form_fields=["name", "value"],
        ):
            view = mod.MasterView(self.request)
            with patch.object(view, "get_instance", return_value=setting):
                response = view.view()

    def test_view_with_rows(self):
        self.pyramid_config.include("wuttaweb.views.common")
        self.pyramid_config.include("wuttaweb.views.auth")
        self.pyramid_config.add_route("people", "/people/")
        model = self.app.model
        person = model.Person(full_name="Whitney Houston")
        self.session.add(person)
        user = model.User(username="whitney", person=person)
        self.session.add(user)
        self.session.commit()

        get_row_grid_data = MagicMock()
        with patch.multiple(
            mod.MasterView,
            create=True,
            Session=MagicMock(return_value=self.session),
            model_class=model.Person,
            route_prefix="people",
            has_rows=True,
            row_model_class=model.User,
            get_row_grid_data=get_row_grid_data,
        ):
            with patch.object(self.request, "matchdict", new={"uuid": person.uuid}):
                view = self.make_view()

                # just for coverage
                get_row_grid_data.return_value = []
                response = view.view()
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.content_type, "text/html")

                # now with data...
                get_row_grid_data.return_value = [user]
                response = view.view()
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.content_type, "text/html")

                # then once more as 'partial' - aka. data only
                with patch.dict(self.request.GET, {"partial": 1}):
                    response = view.view()
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response.content_type, "application/json")

                # redirects when view is reset
                with patch.dict(self.request.GET, {"reset-view": "1", "hash": "foo"}):
                    # nb. mock current route
                    with patch.object(self.request, "current_route_url"):
                        response = view.view()
                        self.assertEqual(response.status_code, 302)

    def test_edit(self):
        self.pyramid_config.include("wuttaweb.views.common")
        self.pyramid_config.include("wuttaweb.views.auth")
        self.pyramid_config.add_route("settings.create", "/settings/new")
        self.pyramid_config.add_route("settings.view", "/settings/{name}")
        self.pyramid_config.add_route("settings.delete", "/settings/{name}/delete")
        model = self.app.model
        self.app.save_setting(self.session, "foo.bar", "frazzle")
        self.session.commit()

        def get_instance():
            setting = self.session.get(model.Setting, "foo.bar")
            return {
                "name": setting.name,
                "value": setting.value,
            }

        # sanity/coverage check using /settings/XXX/edit
        self.request.matchdict = {"name": "foo.bar"}
        with patch.multiple(
            mod.MasterView,
            create=True,
            model_name="Setting",
            model_key="name",
            get_index_url=MagicMock(return_value="/settings/"),
            form_fields=["name", "value"],
        ):
            view = mod.MasterView(self.request)
            with patch.object(view, "get_instance", new=get_instance):

                # get the form page
                response = view.edit()
                self.assertIsInstance(response, Response)
                self.assertEqual(response.status_code, 200)
                self.assertIn("frazzle", response.text)
                # nb. no error
                self.assertNotIn("Required", response.text)

                def persist(setting):
                    self.app.save_setting(self.session, "foo.bar", setting["value"])
                    self.session.commit()

                # post request to save settings
                self.request.method = "POST"
                self.request.POST = {
                    "name": "foo.bar",
                    "value": "froogle",
                }
                with patch.object(view, "persist", new=persist):
                    response = view.edit()
                # nb. should get redirect back to view page
                self.assertEqual(response.status_code, 302)
                # setting should be updated in DB
                self.assertEqual(
                    self.app.get_setting(self.session, "foo.bar"), "froogle"
                )

                # try another post with invalid data (value is required)
                self.request.method = "POST"
                self.request.POST = {}
                with patch.object(view, "persist", new=persist):
                    response = view.edit()
                # nb. should get a form with errors
                self.assertEqual(response.status_code, 200)
                self.assertIn("Required", response.text)
                # setting did not change in DB
                self.assertEqual(
                    self.app.get_setting(self.session, "foo.bar"), "froogle"
                )

    def test_delete(self):
        self.pyramid_config.include("wuttaweb.views.common")
        self.pyramid_config.include("wuttaweb.views.auth")
        self.pyramid_config.add_route("settings.create", "/settings/new")
        self.pyramid_config.add_route("settings.view", "/settings/{name}")
        self.pyramid_config.add_route("settings.edit", "/settings/{name}/edit")
        model = self.app.model
        self.app.save_setting(self.session, "foo.bar", "frazzle")
        self.session.commit()
        self.assertEqual(self.session.query(model.Setting).count(), 1)

        def get_instance():
            setting = self.session.get(model.Setting, "foo.bar")
            return {
                "name": setting.name,
                "value": setting.value,
            }

        # sanity/coverage check using /settings/XXX/delete
        self.request.matchdict = {"name": "foo.bar"}
        with patch.multiple(
            mod.MasterView,
            create=True,
            model_name="Setting",
            model_key="name",
            get_index_url=MagicMock(return_value="/settings/"),
            form_fields=["name", "value"],
        ):
            view = mod.MasterView(self.request)
            with patch.object(view, "get_instance", new=get_instance):

                # get the form page
                response = view.delete()
                self.assertIsInstance(response, Response)
                self.assertEqual(response.status_code, 200)
                self.assertIn("frazzle", response.text)

                def delete_instance(setting):
                    self.app.delete_setting(self.session, setting["name"])

                self.request.method = "POST"
                self.request.POST = {}
                with patch.object(view, "delete_instance", new=delete_instance):

                    # enforces "instance not deletable" rules
                    with patch.object(view, "is_deletable", return_value=False):
                        response = view.delete()
                    # nb. should get redirect back to view page
                    self.assertEqual(response.status_code, 302)
                    # setting remains in DB
                    self.assertEqual(self.session.query(model.Setting).count(), 1)

                    # post request to delete setting
                    response = view.delete()
                    # nb. should get redirect back to view page
                    self.assertEqual(response.status_code, 302)
                    # setting should be gone from DB
                    self.assertEqual(self.session.query(model.Setting).count(), 0)

    def test_delete_instance(self):
        model = self.app.model
        self.app.save_setting(self.session, "foo.bar", "frazzle")
        self.session.commit()
        setting = self.session.query(model.Setting).one()

        with patch.multiple(
            mod.MasterView,
            create=True,
            model_class=model.Setting,
            form_fields=["name", "value"],
        ):
            view = mod.MasterView(self.request)
            view.delete_instance(setting)
            self.session.commit()
            self.assertEqual(self.session.query(model.Setting).count(), 0)

    def test_delete_bulk(self):
        self.pyramid_config.add_route("settings", "/settings/")
        self.pyramid_config.add_route("progress", "/progress/{key}")
        model = self.app.model
        sample_data = [
            {"name": "foo1", "value": "ONE"},
            {"name": "foo2", "value": "two"},
            {"name": "foo3", "value": "three"},
            {"name": "foo4", "value": "four"},
            {"name": "foo5", "value": "five"},
            {"name": "foo6", "value": "six"},
            {"name": "foo7", "value": "seven"},
            {"name": "foo8", "value": "eight"},
            {"name": "foo9", "value": "nine"},
        ]
        for setting in sample_data:
            self.app.save_setting(self.session, setting["name"], setting["value"])
        self.session.commit()
        sample_query = self.session.query(model.Setting)

        with patch.multiple(mod.MasterView, create=True, model_class=model.Setting):
            view = self.make_view()

            # sanity check on sample data
            grid = view.make_model_grid(session=self.session)
            data = grid.get_visible_data()
            self.assertEqual(len(data), 9)

            # and then let's filter it a little
            self.request.GET = {"value": "s", "value.verb": "contains"}
            grid = view.make_model_grid(session=self.session)
            self.assertEqual(len(grid.filters), 2)
            self.assertEqual(len(grid.active_filters), 1)
            data = grid.get_visible_data()
            self.assertEqual(len(data), 2)

            # okay now let's delete those via quick method
            # (user should be redirected back to index)
            with patch.multiple(
                view,
                deletable_bulk_quick=True,
                make_model_grid=MagicMock(return_value=grid),
            ):
                response = view.delete_bulk()
            self.assertEqual(response.status_code, 302)
            self.assertEqual(self.session.query(model.Setting).count(), 7)

            # now use another filter since those records are gone
            self.request.GET = {"name": "foo2", "name.verb": "equal"}
            grid = view.make_model_grid(session=self.session)
            self.assertEqual(len(grid.filters), 2)
            self.assertEqual(len(grid.active_filters), 1)
            data = grid.get_visible_data()
            self.assertEqual(len(data), 1)

            # this time we delete "slowly" with progress
            self.request.session.id = "ignorethis"
            with patch.multiple(
                view,
                deletable_bulk_quick=False,
                make_model_grid=MagicMock(return_value=grid),
            ):
                with patch.object(mod, "threading") as threading:
                    response = view.delete_bulk()
                    threading.Thread.return_value.start.assert_called_once_with()
            # nb. user is shown progress page
            self.assertEqual(response.status_code, 200)

    def test_delete_bulk_action(self):
        self.pyramid_config.add_route("settings", "/settings/")
        model = self.app.model
        sample_data = [
            {"name": "foo1", "value": "ONE"},
            {"name": "foo2", "value": "two"},
            {"name": "foo3", "value": "three"},
            {"name": "foo4", "value": "four"},
            {"name": "foo5", "value": "five"},
            {"name": "foo6", "value": "six"},
            {"name": "foo7", "value": "seven"},
            {"name": "foo8", "value": "eight"},
            {"name": "foo9", "value": "nine"},
        ]
        for setting in sample_data:
            self.app.save_setting(self.session, setting["name"], setting["value"])
        self.session.commit()
        sample_query = self.session.query(model.Setting)

        with patch.multiple(mod.MasterView, create=True, model_class=model.Setting):
            view = self.make_view()

            # basic bulk delete
            self.assertEqual(self.session.query(model.Setting).count(), 9)
            settings = (
                self.session.query(model.Setting)
                .filter(model.Setting.value.ilike("%s%"))
                .all()
            )
            self.assertEqual(len(settings), 2)
            view.delete_bulk_action(settings)
            self.session.commit()
            self.assertEqual(self.session.query(model.Setting).count(), 7)

    def test_do_thread_body(self):
        view = self.make_view()

        # nb. so far this is just proving coverage, in case caller
        # does not specify an error handler

        def func():
            raise RuntimeError

        # with error handler
        onerror = MagicMock()
        view.do_thread_body(func, (), {}, onerror)
        onerror.assert_called_once_with()

        # without error handler
        onerror.reset_mock()
        view.do_thread_body(func, (), {})
        onerror.assert_not_called()

    def test_delete_bulk_thread(self):
        self.pyramid_config.add_route("settings", "/settings/")
        model = self.app.model
        sample_data = [
            {"name": "foo1", "value": "ONE"},
            {"name": "foo2", "value": "two"},
            {"name": "foo3", "value": "three"},
            {"name": "foo4", "value": "four"},
            {"name": "foo5", "value": "five"},
            {"name": "foo6", "value": "six"},
            {"name": "foo7", "value": "seven"},
            {"name": "foo8", "value": "eight"},
            {"name": "foo9", "value": "nine"},
        ]
        for setting in sample_data:
            self.app.save_setting(self.session, setting["name"], setting["value"])
        self.session.commit()
        sample_query = self.session.query(model.Setting)

        with patch.multiple(mod.MasterView, create=True, model_class=model.Setting):
            view = self.make_view()

            # basic delete, no progress
            self.assertEqual(self.session.query(model.Setting).count(), 9)
            settings = self.session.query(model.Setting).filter(
                model.Setting.value.ilike("%s%")
            )
            self.assertEqual(settings.count(), 2)
            with patch.object(self.app, "make_session", return_value=self.session):
                view.delete_bulk_thread(settings)
            self.assertEqual(self.session.query(model.Setting).count(), 7)

            # basic delete, with progress
            settings = self.session.query(model.Setting).filter(
                model.Setting.name == "foo1"
            )
            self.assertEqual(settings.count(), 1)
            with patch.object(self.app, "make_session", return_value=self.session):
                view.delete_bulk_thread(settings, progress=MagicMock())
            self.assertEqual(self.session.query(model.Setting).count(), 6)

            # error, no progress
            settings = self.session.query(model.Setting).filter(
                model.Setting.name == "foo2"
            )
            self.assertEqual(settings.count(), 1)
            with patch.object(self.app, "make_session", return_value=self.session):
                with patch.object(view, "delete_bulk_action", side_effect=RuntimeError):
                    view.delete_bulk_thread(settings)
            # nb. nothing was deleted
            self.assertEqual(self.session.query(model.Setting).count(), 6)

            # error, with progress
            self.assertEqual(settings.count(), 1)
            with patch.object(self.app, "make_session", return_value=self.session):
                with patch.object(view, "delete_bulk_action", side_effect=RuntimeError):
                    view.delete_bulk_thread(settings, progress=MagicMock())
            # nb. nothing was deleted
            self.assertEqual(self.session.query(model.Setting).count(), 6)

    def test_autocomplete(self):
        model = self.app.model

        person1 = model.Person(full_name="George Jones")
        self.session.add(person1)
        person2 = model.Person(full_name="George Strait")
        self.session.add(person2)
        self.session.commit()

        # no results for empty term
        self.request.GET = {}
        view = self.make_view()
        results = view.autocomplete()
        self.assertEqual(len(results), 0)

        # search yields no results
        self.request.GET = {"term": "sally"}
        view = self.make_view()
        with patch.object(view, "autocomplete_data", return_value=[]):
            view = self.make_view()
            results = view.autocomplete()
            self.assertEqual(len(results), 0)

        # search yields 2 results
        self.request.GET = {"term": "george"}
        view = self.make_view()
        with patch.object(view, "autocomplete_data", return_value=[person1, person2]):
            results = view.autocomplete()
            self.assertEqual(len(results), 2)
            self.assertEqual(
                [res["value"] for res in results], [p.uuid for p in [person1, person2]]
            )

    def test_autocomplete_normalize(self):
        model = self.app.model
        view = self.make_view()

        person = model.Person(full_name="Betty Boop", uuid="bogus")
        normal = view.autocomplete_normalize(person)
        self.assertEqual(normal, {"value": "bogus", "label": "Betty Boop"})

    def test_download(self):
        model = self.app.model
        self.app.save_setting(self.session, "foo", "bar")
        self.session.commit()

        with patch.multiple(
            mod.MasterView,
            create=True,
            model_class=model.Setting,
            model_key="name",
            Session=MagicMock(return_value=self.session),
        ):
            view = self.make_view()
            self.request.matchdict = {"name": "foo"}

            # 404 if no filename
            response = view.download()
            self.assertEqual(response.status_code, 404)

            # 404 if bad filename
            self.request.GET = {"filename": "doesnotexist"}
            response = view.download()
            self.assertEqual(response.status_code, 404)

            # 200 if good filename
            foofile = self.write_file("foo.txt", "foo")
            with patch.object(view, "download_path", return_value=foofile):
                response = view.download()
                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    response.content_disposition, 'attachment; filename="foo.txt"'
                )

    def test_execute(self):
        self.pyramid_config.add_route("settings.view", "/settings/{name}")
        self.pyramid_config.add_route("progress", "/progress/{key}")
        model = self.app.model
        self.app.save_setting(self.session, "foo", "bar")
        user = model.User(username="barney")
        self.session.add(user)
        self.session.commit()

        with patch.multiple(
            mod.MasterView,
            create=True,
            model_class=model.Setting,
            model_key="name",
            Session=MagicMock(return_value=self.session),
        ):
            view = self.make_view()
            self.request.matchdict = {"name": "foo"}
            self.request.session.id = "mockid"
            self.request.user = user

            # basic usage; user is shown progress page
            with patch.object(mod, "threading") as threading:
                response = view.execute()
                threading.Thread.return_value.start.assert_called_once_with()
                self.assertEqual(response.status_code, 200)

    def test_execute_thread(self):
        model = self.app.model
        enum = self.app.enum
        user = model.User(username="barney")
        self.session.add(user)
        upgrade = model.Upgrade(
            description="test", created_by=user, status=enum.UpgradeStatus.PENDING
        )
        self.session.add(upgrade)
        self.session.commit()

        with patch.multiple(mod.MasterView, create=True, model_class=model.Upgrade):
            view = self.make_view()

            # basic execute, no progress
            with patch.object(view, "execute_instance") as execute_instance:
                view.execute_thread({"uuid": upgrade.uuid}, user.uuid)
                execute_instance.assert_called_once()

            # basic execute, with progress
            with patch.object(view, "execute_instance") as execute_instance:
                progress = MagicMock()
                view.execute_thread(
                    {"uuid": upgrade.uuid}, user.uuid, progress=progress
                )
                execute_instance.assert_called_once()
                progress.handle_success.assert_called_once_with()

            # error, no progress
            with patch.object(view, "execute_instance") as execute_instance:
                execute_instance.side_effect = RuntimeError
                view.execute_thread({"uuid": upgrade.uuid}, user.uuid)
                execute_instance.assert_called_once()

            # error, with progress
            with patch.object(view, "execute_instance") as execute_instance:
                progress = MagicMock()
                execute_instance.side_effect = RuntimeError
                view.execute_thread(
                    {"uuid": upgrade.uuid}, user.uuid, progress=progress
                )
                execute_instance.assert_called_once()
                progress.handle_error.assert_called_once()

    def test_configure(self):
        self.pyramid_config.include("wuttaweb.views.common")
        self.pyramid_config.include("wuttaweb.views.auth")
        model = self.app.model

        # mock settings
        settings = [
            {"name": "wutta.app_title"},
            {"name": "wutta.foo", "value": "bar"},
            {"name": "wutta.flag", "type": bool},
            {"name": "wutta.number", "type": int, "default": 42},
            {"name": "wutta.value1", "save_if_empty": True},
            {"name": "wutta.value2", "save_if_empty": False},
        ]

        view = mod.MasterView(self.request)
        with patch.object(
            self.request, "current_route_url", return_value="/appinfo/configure"
        ):
            with patch.object(mod, "Session", return_value=self.session):
                with patch.multiple(
                    mod.MasterView,
                    create=True,
                    model_name="AppInfo",
                    route_prefix="appinfo",
                    template_prefix="/appinfo",
                    creatable=False,
                    get_index_url=MagicMock(return_value="/appinfo/"),
                    configure_get_simple_settings=MagicMock(return_value=settings),
                ):

                    # nb. appinfo/configure template requires menu_handlers
                    original_context = view.configure_get_context

                    def get_context(**kw):
                        kw = original_context(**kw)
                        kw["menu_handlers"] = []
                        return kw

                    with patch.object(view, "configure_get_context", new=get_context):

                        # get the form page
                        response = view.configure(session=self.session)
                        self.assertIsInstance(response, Response)

                        # post request to save settings
                        self.request.method = "POST"
                        self.request.POST = {
                            "wutta.app_title": "Wutta",
                            "wutta.foo": "bar",
                            "wutta.flag": "true",
                        }
                        response = view.configure(session=self.session)
                        # nb. should get redirect back to configure page
                        self.assertEqual(response.status_code, 302)

                        # should now have 5 settings
                        count = self.session.query(model.Setting).count()
                        self.assertEqual(count, 5)
                        get_setting = functools.partial(
                            self.app.get_setting, self.session
                        )
                        self.assertEqual(get_setting("wutta.app_title"), "Wutta")
                        self.assertEqual(get_setting("wutta.foo"), "bar")
                        self.assertEqual(get_setting("wutta.flag"), "true")
                        self.assertEqual(get_setting("wutta.number"), "42")
                        self.assertEqual(get_setting("wutta.value1"), "")
                        self.assertEqual(get_setting("wutta.value2"), None)

                        # post request to remove settings
                        self.request.method = "POST"
                        self.request.POST = {"remove_settings": "1"}
                        response = view.configure(session=self.session)
                        # nb. should get redirect back to configure page
                        self.assertEqual(response.status_code, 302)

                        # should now have 0 settings
                        count = self.session.query(model.Setting).count()
                        self.assertEqual(count, 0)

    def test_configure_get_simple_settings(self):
        view = self.make_view()
        settings = view.configure_get_simple_settings()
        self.assertEqual(settings, [])

    def test_configure_gather_settings(self):
        view = self.make_view()

        simple_settings = [
            {"name": "wutta.app_title"},
            {"name": "wutta.foo"},
            {"name": "wutta.flag", "type": bool, "default": True},
            {"name": "wutta.number", "type": int, "default": 42},
            {"name": "wutta.value1", "save_if_empty": True},
            {"name": "wutta.value2", "save_if_empty": False},
            {"name": "wutta.value3", "save_if_empty": False, "default": "baz"},
        ]

        data = {
            "wutta.app_title": "Poser",
            "wutta.foo": "bar",
            "wutta.number": 44,
            "wutta.value1": None,
        }

        with patch.object(
            view, "configure_get_simple_settings", return_value=simple_settings
        ):
            settings = view.configure_gather_settings(data)
            self.assertEqual(len(settings), 6)
            self.assertEqual(
                settings,
                [
                    {"name": "wutta.app_title", "value": "Poser"},
                    {"name": "wutta.foo", "value": "bar"},
                    {"name": "wutta.flag", "value": "false"},
                    {"name": "wutta.number", "value": "44"},
                    {"name": "wutta.value1", "value": ""},
                    {"name": "wutta.value3", "value": "baz"},
                ],
            )

    ##############################
    # row methods
    ##############################

    def test_collect_row_labels(self):

        # default labels
        view = self.make_view()
        labels = view.collect_row_labels()
        self.assertEqual(labels, {})

        # labels come from all classes; subclass wins
        with patch.object(
            View, "row_labels", create=True, new={"foo": "Foo", "bar": "Bar"}
        ):
            with patch.object(
                mod.MasterView, "row_labels", create=True, new={"foo": "FOO FIGHTERS"}
            ):
                view = self.make_view()
                labels = view.collect_row_labels()
                self.assertEqual(labels, {"foo": "FOO FIGHTERS", "bar": "Bar"})

    def test_set_row_labels(self):
        model = self.app.model
        person = model.Person(full_name="Fred Flintstone")
        self.session.add(person)

        with patch.multiple(
            mod.MasterView,
            create=True,
            model_class=model.Person,
            has_rows=True,
            row_model_class=model.User,
        ):

            # no labels by default
            view = self.make_view()
            grid = view.make_row_model_grid(person, key="person.users", data=[])
            view.set_row_labels(grid)
            self.assertEqual(grid.labels, {})

            # labels come from all classes; subclass wins
            with patch.object(
                View, "row_labels", create=True, new={"username": "USERNAME"}
            ):
                with patch.object(
                    mod.MasterView,
                    "row_labels",
                    create=True,
                    new={"username": "UserName"},
                ):
                    view = self.make_view()
                    grid = view.make_row_model_grid(person, key="person.users", data=[])
                    view.set_row_labels(grid)
                    self.assertEqual(grid.labels, {"username": "UserName"})

    def test_get_row_grid_data(self):
        model = self.app.model
        person = model.Person(full_name="Fred Flintstone")
        self.session.add(person)
        view = self.make_view()
        self.assertRaises(NotImplementedError, view.get_row_grid_data, person)

    def test_get_row_grid_columns(self):

        # no default
        view = self.make_view()
        self.assertIsNone(view.get_row_grid_columns())

        # class may specify
        with patch.object(view, "row_grid_columns", create=True, new=["foo", "bar"]):
            self.assertEqual(view.get_row_grid_columns(), ["foo", "bar"])

    def test_get_row_grid_key(self):
        view = self.make_view()
        with patch.multiple(
            mod.MasterView, create=True, model_key="id", grid_key="widgets"
        ):

            self.request.matchdict = {"id": 42}
            self.assertEqual(view.get_row_grid_key(), "widgets.42")

    def test_make_row_model_grid(self):
        model = self.app.model
        person = model.Person(full_name="Barney Rubble")
        self.session.add(person)
        self.session.commit()

        self.request.matchdict = {"uuid": person.uuid}
        with patch.multiple(mod.MasterView, create=True, model_class=model.Person):
            view = self.make_view()

            # specify data
            grid = view.make_row_model_grid(person, data=[])
            self.assertIsNone(grid.model_class)
            self.assertEqual(grid.data, [])

            # fetch data
            with patch.object(view, "get_row_grid_data", return_value=[]):
                grid = view.make_row_model_grid(person)
                self.assertIsNone(grid.model_class)
                self.assertEqual(grid.data, [])

            # view action
            with patch.object(view, "rows_viewable", new=True):
                with patch.object(view, "get_row_action_url_view", return_value="#"):
                    grid = view.make_row_model_grid(person, data=[])
                    self.assertEqual(len(grid.actions), 1)
                    self.assertEqual(grid.actions[0].key, "view")

    def test_get_row_action_url_view(self):
        view = self.make_view()
        row = MagicMock()
        self.assertRaises(NotImplementedError, view.get_row_action_url_view, row, 0)

    def test_get_rows_title(self):
        view = self.make_view()

        # no default
        self.assertIsNone(view.get_rows_title())

        # class may specify
        with patch.object(view, "rows_title", create=True, new="Mock Rows"):
            self.assertEqual(view.get_rows_title(), "Mock Rows")
