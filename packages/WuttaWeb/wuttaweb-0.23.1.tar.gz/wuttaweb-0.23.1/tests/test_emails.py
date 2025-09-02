# -*- coding: utf-8; -*-

from wuttjamaican.testing import DataTestCase
from wuttjamaican.email import EmailSetting

from wuttaweb import emails as mod


class TestAllSettings(DataTestCase):

    def check_setting(self, setting):
        self.assertIsNotNone(setting.default_subject)
        setting = setting(self.config)
        context = setting.sample_data()
        self.assertIsInstance(context, dict)

    def test_all(self):
        for name in dir(mod):
            obj = getattr(mod, name)
            if (
                isinstance(obj, type)
                and obj is not EmailSetting
                and issubclass(obj, EmailSetting)
            ):
                self.check_setting(obj)
