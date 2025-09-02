# -*- coding: utf-8; -*-

import datetime
from unittest.mock import patch, MagicMock

from sqlalchemy import orm
from pyramid.httpexceptions import HTTPFound

from wuttjamaican.db import model
from wuttjamaican.batch import BatchHandler
from wuttaweb.views import MasterView, batch as mod
from wuttaweb.progress import SessionProgress
from wuttaweb.testing import WebTestCase


class MockBatch(model.BatchMixin, model.Base):
    __tablename__ = "testing_batch_mock"


class MockBatchRow(model.BatchRowMixin, model.Base):
    __tablename__ = "testing_batch_mock_row"
    __batch_class__ = MockBatch


MockBatch.__row_class__ = MockBatchRow


class MockBatchHandler(BatchHandler):
    model_class = MockBatch


class TestBatchMasterView(WebTestCase):

    def setUp(self):
        self.setup_web()

        # nb. create MockBatch, MockBatchRow
        model.Base.metadata.create_all(bind=self.session.bind)

    def make_handler(self):
        return MockBatchHandler(self.config)

    def make_view(self):
        return mod.BatchMasterView(self.request)

    def test_get_batch_handler(self):
        self.assertRaises(NotImplementedError, mod.BatchMasterView, self.request)

        with patch.object(mod.BatchMasterView, "get_batch_handler", return_value=42):
            view = mod.BatchMasterView(self.request)
            self.assertEqual(view.batch_handler, 42)

    def test_get_fallback_templates(self):
        handler = MockBatchHandler(self.config)
        with patch.object(
            mod.BatchMasterView, "get_batch_handler", return_value=handler
        ):
            view = self.make_view()
            templates = view.get_fallback_templates("view")
            self.assertEqual(
                templates,
                [
                    "/batch/view.mako",
                    "/master/view.mako",
                ],
            )

    def test_render_to_response(self):
        model = self.app.model
        handler = MockBatchHandler(self.config)

        user = model.User(username="barney")
        self.session.add(user)
        batch = handler.make_batch(self.session, created_by=user)
        self.session.add(batch)
        self.session.flush()

        with patch.object(
            mod.BatchMasterView, "get_batch_handler", return_value=handler
        ):
            with patch.object(MasterView, "render_to_response") as render_to_response:
                view = self.make_view()
                response = view.render_to_response("view", {"instance": batch})
                self.assertTrue(render_to_response.called)
                context = render_to_response.call_args[0][1]
                self.assertIs(context["batch"], batch)
                self.assertIs(context["batch_handler"], handler)

    def test_configure_grid(self):
        handler = MockBatchHandler(self.config)
        with patch.multiple(mod.BatchMasterView, create=True, model_class=MockBatch):
            with patch.object(
                mod.BatchMasterView, "get_batch_handler", return_value=handler
            ):
                view = mod.BatchMasterView(self.request)
                grid = view.make_model_grid()
                # nb. coverage only; tests nothing
                view.configure_grid(grid)

    def test_render_batch_id(self):
        handler = MockBatchHandler(self.config)
        with patch.object(
            mod.BatchMasterView, "get_batch_handler", return_value=handler
        ):
            view = mod.BatchMasterView(self.request)
            batch = MockBatch(id=42)

            result = view.render_batch_id(batch, "id", 42)
            self.assertEqual(result, "00000042")

            result = view.render_batch_id(batch, "id", None)
            self.assertIsNone(result)

    def test_get_instance_title(self):
        handler = MockBatchHandler(self.config)
        with patch.object(
            mod.BatchMasterView, "get_batch_handler", return_value=handler
        ):
            view = mod.BatchMasterView(self.request)

            batch = MockBatch(id=42)
            result = view.get_instance_title(batch)
            self.assertEqual(result, "00000042")

            batch = MockBatch(id=43, description="runnin some numbers")
            result = view.get_instance_title(batch)
            self.assertEqual(result, "00000043 runnin some numbers")

    def test_configure_form(self):
        handler = MockBatchHandler(self.config)
        with patch.multiple(mod.BatchMasterView, create=True, model_class=MockBatch):
            with patch.object(
                mod.BatchMasterView, "get_batch_handler", return_value=handler
            ):
                view = mod.BatchMasterView(self.request)

                # creating
                with patch.object(view, "creating", new=True):
                    form = view.make_model_form(model_instance=None)
                    view.configure_form(form)

                batch = MockBatch(id=42)

                # viewing
                with patch.object(view, "viewing", new=True):
                    form = view.make_model_form(model_instance=batch)
                    view.configure_form(form)

                # editing
                with patch.object(view, "editing", new=True):
                    form = view.make_model_form(model_instance=batch)
                    view.configure_form(form)

                # deleting
                with patch.object(view, "deleting", new=True):
                    form = view.make_model_form(model_instance=batch)
                    view.configure_form(form)

                # viewing (executed)
                batch.executed = datetime.datetime.now()
                with patch.object(view, "viewing", new=True):
                    form = view.make_model_form(model_instance=batch)
                    view.configure_form(form)

    def test_objectify(self):
        handler = MockBatchHandler(self.config)
        with patch.multiple(mod.BatchMasterView, create=True, model_class=MockBatch):
            with patch.object(
                mod.BatchMasterView, "get_batch_handler", return_value=handler
            ):
                with patch.object(
                    mod.BatchMasterView, "Session", return_value=self.session
                ):
                    view = mod.BatchMasterView(self.request)

                    # create batch
                    with patch.object(view, "creating", new=True):
                        form = view.make_model_form(model_instance=None)
                        form.validated = {}
                        batch = view.objectify(form)
                        self.assertIsInstance(batch.id, int)
                        self.assertTrue(batch.id > 0)

                    # edit batch
                    with patch.object(view, "editing", new=True):
                        with patch.object(
                            view.batch_handler, "make_batch"
                        ) as make_batch:
                            form = view.make_model_form(model_instance=batch)
                            form.validated = {"description": "foo"}
                            self.assertIsNone(batch.description)
                            batch = view.objectify(form)
                            self.assertEqual(batch.description, "foo")

    def test_redirect_after_create(self):
        self.pyramid_config.add_route("mock_batches.view", "/batch/mock/{uuid}")
        handler = MockBatchHandler(self.config)
        with patch.object(
            mod.BatchMasterView, "get_batch_handler", return_value=handler
        ):
            with patch.multiple(
                mod.BatchMasterView,
                create=True,
                model_class=MockBatch,
                route_prefix="mock_batches",
            ):
                view = mod.BatchMasterView(self.request)
                batch = MockBatch(id=42)

                # typically redirect to view batch
                result = view.redirect_after_create(batch)
                self.assertIsInstance(result, HTTPFound)

                # unless populating in which case thread is launched
                self.request.session.id = "abcdefghijk"
                with patch.object(mod, "threading") as threading:
                    thread = MagicMock()
                    threading.Thread.return_value = thread
                    with patch.object(
                        view.batch_handler, "should_populate", return_value=True
                    ):
                        with patch.object(view, "render_progress") as render_progress:
                            view.redirect_after_create(batch)
                            self.assertTrue(threading.Thread.called)
                            thread.start.assert_called_once_with()
                            self.assertTrue(render_progress.called)

    def test_delete_instance(self):
        model = self.app.model
        handler = self.make_handler()

        user = model.User(username="barney")
        self.session.add(user)

        batch = handler.make_batch(self.session, created_by=user)
        self.session.add(batch)
        self.session.flush()

        with patch.object(
            mod.BatchMasterView, "get_batch_handler", return_value=handler
        ):
            view = self.make_view()

            self.assertEqual(self.session.query(MockBatch).count(), 1)
            view.delete_instance(batch)
            self.assertEqual(self.session.query(MockBatch).count(), 0)

    def test_populate_thread(self):
        model = self.app.model
        handler = MockBatchHandler(self.config)
        with patch.object(
            mod.BatchMasterView, "get_batch_handler", return_value=handler
        ):
            with patch.multiple(
                mod.BatchMasterView, create=True, model_class=MockBatch
            ):
                view = mod.BatchMasterView(self.request)
                user = model.User(username="barney")
                self.session.add(user)
                batch = MockBatch(id=42, created_by=user)
                self.session.add(batch)
                self.session.commit()

                # nb. use our session within thread method
                with patch.object(self.app, "make_session", return_value=self.session):

                    # nb. prevent closing our session
                    with patch.object(self.session, "close") as close:

                        # without progress
                        view.populate_thread(batch.uuid)
                        close.assert_called_once_with()
                        close.reset_mock()

                        # with progress
                        self.request.session.id = "abcdefghijk"
                        view.populate_thread(
                            batch.uuid,
                            progress=SessionProgress(
                                self.request, "populate_mock_batch"
                            ),
                        )
                        close.assert_called_once_with()
                        close.reset_mock()

                        # failure to populate, without progress
                        with patch.object(
                            view.batch_handler, "do_populate", side_effect=RuntimeError
                        ):
                            view.populate_thread(batch.uuid)
                            close.assert_called_once_with()
                            close.reset_mock()

                        # failure to populate, with progress
                        with patch.object(
                            view.batch_handler, "do_populate", side_effect=RuntimeError
                        ):
                            view.populate_thread(
                                batch.uuid,
                                progress=SessionProgress(
                                    self.request, "populate_mock_batch"
                                ),
                            )
                            close.assert_called_once_with()
                            close.reset_mock()

                        # failure for batch to appear
                        self.session.delete(batch)
                        self.session.commit()
                        # nb. should give up waiting after 1 second
                        self.assertRaises(
                            RuntimeError, view.populate_thread, batch.uuid
                        )

    def test_execute(self):
        self.pyramid_config.add_route("mock_batches.view", "/batch/mock/{uuid}")
        model = self.app.model
        handler = MockBatchHandler(self.config)

        user = model.User(username="barney")
        self.session.add(user)
        batch = handler.make_batch(self.session, created_by=user)
        self.session.add(batch)
        self.session.commit()

        with patch.multiple(
            mod.BatchMasterView,
            create=True,
            model_class=MockBatch,
            route_prefix="mock_batches",
            get_batch_handler=MagicMock(return_value=handler),
            get_instance=MagicMock(return_value=batch),
        ):
            view = self.make_view()

            # batch executes okay
            response = view.execute()
            self.assertEqual(response.status_code, 302)  # redirect to "view batch"
            self.assertFalse(self.request.session.peek_flash("error"))

            # but cannot be executed again
            response = view.execute()
            self.assertEqual(response.status_code, 302)  # redirect to "view batch"
            # nb. flash has error this time
            self.assertTrue(self.request.session.peek_flash("error"))

    def test_get_row_model_class(self):
        handler = MockBatchHandler(self.config)
        with patch.object(
            mod.BatchMasterView, "get_batch_handler", return_value=handler
        ):
            view = self.make_view()

            self.assertRaises(AttributeError, view.get_row_model_class)

            # row class determined from batch class
            with patch.object(
                mod.BatchMasterView, "model_class", new=MockBatch, create=True
            ):
                cls = view.get_row_model_class()
                self.assertIs(cls, MockBatchRow)

            self.assertRaises(AttributeError, view.get_row_model_class)

            # view may specify row class
            with patch.object(
                mod.BatchMasterView, "row_model_class", new=MockBatchRow, create=True
            ):
                cls = view.get_row_model_class()
                self.assertIs(cls, MockBatchRow)

    def test_get_row_grid_data(self):
        handler = MockBatchHandler(self.config)
        model = self.app.model

        user = model.User(username="barney")
        self.session.add(user)

        batch = handler.make_batch(self.session, created_by=user)
        self.session.add(batch)
        row = handler.make_row()
        handler.add_row(batch, row)
        self.session.flush()

        with patch.object(
            mod.BatchMasterView, "get_batch_handler", return_value=handler
        ):

            view = self.make_view()
            self.assertRaises(AttributeError, view.get_row_grid_data, batch)

            Session = MagicMock(return_value=self.session)
            Session.query.side_effect = lambda m: self.session.query(m)
            with patch.multiple(
                mod.BatchMasterView, create=True, Session=Session, model_class=MockBatch
            ):

                view = self.make_view()
                data = view.get_row_grid_data(batch)
                self.assertIsInstance(data, orm.Query)
                self.assertEqual(data.count(), 1)

    def test_configure_row_grid(self):
        handler = MockBatchHandler(self.config)
        model = self.app.model

        user = model.User(username="barney")
        self.session.add(user)

        batch = handler.make_batch(self.session, created_by=user)
        self.session.add(batch)
        row = handler.make_row()
        handler.add_row(batch, row)
        self.session.flush()

        with patch.object(
            mod.BatchMasterView, "get_batch_handler", return_value=handler
        ):

            Session = MagicMock(return_value=self.session)
            Session.query.side_effect = lambda m: self.session.query(m)
            with patch.multiple(
                mod.BatchMasterView, create=True, Session=Session, model_class=MockBatch
            ):

                with patch.object(self.request, "matchdict", new={"uuid": batch.uuid}):
                    view = self.make_view()
                    grid = view.make_row_model_grid(batch)
                    self.assertIn("sequence", grid.labels)
                    self.assertEqual(grid.labels["sequence"], "Seq.")

    def test_render_row_status(self):
        with patch.object(mod.BatchMasterView, "get_batch_handler", return_value=None):
            view = self.make_view()
            row = MagicMock(foo=1, STATUS={1: "bar"})
            self.assertEqual(view.render_row_status(row, "foo", 1), "bar")

    def test_defaults(self):
        # nb. coverage only
        with patch.object(
            mod.BatchMasterView, "model_class", new=MockBatch, create=True
        ):
            mod.BatchMasterView.defaults(self.pyramid_config)
