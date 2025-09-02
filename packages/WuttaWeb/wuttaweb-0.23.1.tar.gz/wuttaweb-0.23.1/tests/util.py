# -*- coding: utf-8; -*-

from wuttjamaican.conf import WuttaConfig
from wuttjamaican.testing import FileConfigTestCase
from wuttaweb.menus import MenuHandler


class DataTestCase(FileConfigTestCase):
    """
    Base class for test suites requiring a full (typical) database.
    """

    def setUp(self):
        self.setup_db()

    def setup_db(self):
        self.setup_files()
        self.config = WuttaConfig(
            defaults={
                "wutta.db.default.url": "sqlite://",
            }
        )
        self.app = self.config.get_app()

        # init db
        model = self.app.model
        model.Base.metadata.create_all(bind=self.config.appdb_engine)
        self.session = self.app.make_session()

    def tearDown(self):
        self.teardown_db()

    def teardown_db(self):
        self.teardown_files()


class NullMenuHandler(MenuHandler):
    """
    Dummy menu handler for testing.
    """

    def make_menus(self, request, **kwargs):
        return []
