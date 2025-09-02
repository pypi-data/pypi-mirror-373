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
Views for email settings
"""

import colander

from wuttaweb.views import MasterView
from wuttaweb.forms.schema import EmailRecipients


class EmailSettingView(MasterView):  # pylint: disable=abstract-method
    """
    Master view for :term:`email settings <email setting>`.
    """

    model_name = "email_setting"
    model_key = "key"
    model_title = "Email Setting"
    url_prefix = "/email/settings"
    filterable = False
    sortable = True
    sort_on_backend = False
    paginated = False
    creatable = False
    deletable = False

    labels = {
        "key": "Email Key",
        "replyto": "Reply-To",
    }

    grid_columns = [
        "key",
        "subject",
        "to",
        "enabled",
    ]

    # TODO: why does this not work?
    sort_defaults = "key"

    form_fields = [
        "key",
        "description",
        "subject",
        "sender",
        "replyto",
        "to",
        "cc",
        "bcc",
        "notes",
        "enabled",
    ]

    def __init__(self, request, context=None):
        super().__init__(request, context=context)
        self.email_handler = self.app.get_email_handler()

    def get_grid_data(self, columns=None, session=None):
        """
        This view calls
        :meth:`~wuttjamaican:wuttjamaican.email.EmailHandler.get_email_settings()`
        on the :attr:`email_handler` to obtain its grid data.
        """
        data = []
        for setting in self.email_handler.get_email_settings().values():
            data.append(self.normalize_setting(setting))
        return data

    def normalize_setting(self, setting):  # pylint: disable=empty-docstring
        """ """
        key = setting.__name__
        return {
            "key": key,
            "description": setting.__doc__,
            "subject": self.email_handler.get_auto_subject(
                key, rendered=False, setting=setting
            ),
            "sender": self.email_handler.get_auto_sender(key),
            "replyto": self.email_handler.get_auto_replyto(key) or colander.null,
            "to": self.email_handler.get_auto_to(key),
            "cc": self.email_handler.get_auto_cc(key),
            "bcc": self.email_handler.get_auto_bcc(key),
            "notes": self.email_handler.get_notes(key) or colander.null,
            "enabled": self.email_handler.is_enabled(key),
        }

    def configure_grid(self, grid):  # pylint: disable=empty-docstring
        """ """
        g = grid
        super().configure_grid(g)

        # key
        g.set_searchable("key")
        g.set_link("key")

        # subject
        g.set_searchable("subject")
        g.set_link("subject")

        # to
        g.set_renderer("to", self.render_to_short)

    def render_to_short(  # pylint: disable=empty-docstring,unused-argument
        self, setting, field, value
    ):
        """ """
        recips = value
        if not recips:
            return None

        if len(recips) < 3:
            return ", ".join(recips)

        recips = ", ".join(recips[:2])
        return f"{recips}, ..."

    def get_instance(  # pylint: disable=empty-docstring,arguments-differ,unused-argument
        self, **kwargs
    ):
        """ """
        key = self.request.matchdict["key"]
        setting = self.email_handler.get_email_setting(key, instance=False)
        if setting:
            return self.normalize_setting(setting)

        raise self.notfound()

    def get_instance_title(self, instance):  # pylint: disable=empty-docstring
        """ """
        setting = instance
        return setting["subject"]

    def configure_form(self, form):  # pylint: disable=empty-docstring
        """ """
        f = form
        super().configure_form(f)

        # description
        f.set_readonly("description")

        # replyto
        f.set_required("replyto", False)

        # to
        f.set_node("to", EmailRecipients())

        # cc
        f.set_node("cc", EmailRecipients())

        # bcc
        f.set_node("bcc", EmailRecipients())

        # notes
        f.set_widget("notes", "notes")
        f.set_required("notes", False)

        # enabled
        f.set_node("enabled", colander.Boolean())

    def persist(  # pylint: disable=too-many-branches,empty-docstring,arguments-differ,unused-argument
        self, setting, **kwargs
    ):
        """ """
        session = self.Session()
        key = self.request.matchdict["key"]

        def save(name, value):
            self.app.save_setting(
                session, f"{self.config.appname}.email.{key}.{name}", value
            )

        def delete(name):
            self.app.delete_setting(
                session, f"{self.config.appname}.email.{key}.{name}"
            )

        # subject
        if setting["subject"]:
            save("subject", setting["subject"])
        else:
            delete("subject")

        # sender
        if setting["sender"]:
            save("sender", setting["sender"])
        else:
            delete("sender")

        # replyto
        if setting["replyto"]:
            save("replyto", setting["replyto"])
        else:
            delete("replyto")

        # to
        if setting["to"]:
            save("to", setting["to"])
        else:
            delete("to")

        # cc
        if setting["cc"]:
            save("cc", setting["cc"])
        else:
            delete("cc")

        # bcc
        if setting["bcc"]:
            save("bcc", setting["bcc"])
        else:
            delete("bcc")

        # notes
        if setting["notes"]:
            save("notes", setting["notes"])
        else:
            delete("notes")

        # enabled
        save("enabled", "true" if setting["enabled"] else "false")

    def render_to_response(self, template, context):  # pylint: disable=empty-docstring
        """ """
        if self.viewing:
            setting = context["instance"]
            context["setting"] = setting
            context["has_html_template"] = self.email_handler.get_auto_body_template(
                setting["key"], "html"
            )
            context["has_txt_template"] = self.email_handler.get_auto_body_template(
                setting["key"], "txt"
            )

        return super().render_to_response(template, context)

    def preview(self):
        """
        View for showing a rendered preview of a given email template.

        This will render the email template according to the "mode"
        requested - i.e. HTML or TXT.
        """
        key = self.request.matchdict["key"]
        setting = self.email_handler.get_email_setting(key)
        context = setting.sample_data()
        mode = self.request.params.get("mode", "html")

        if mode == "txt":
            body = self.email_handler.get_auto_txt_body(key, context)
            self.request.response.content_type = "text/plain"

        else:  # html
            body = self.email_handler.get_auto_html_body(key, context)

        self.request.response.text = body
        return self.request.response

    @classmethod
    def defaults(cls, config):  # pylint: disable=empty-docstring
        """ """
        cls._email_defaults(config)
        cls._defaults(config)

    @classmethod
    def _email_defaults(cls, config):
        """ """
        route_prefix = cls.get_route_prefix()
        permission_prefix = cls.get_permission_prefix()
        model_title_plural = cls.get_model_title_plural()
        instance_url_prefix = cls.get_instance_url_prefix()

        # fix permission group
        config.add_wutta_permission_group(
            permission_prefix, model_title_plural, overwrite=False
        )

        # preview
        config.add_route(f"{route_prefix}.preview", f"{instance_url_prefix}/preview")
        config.add_view(
            cls,
            attr="preview",
            route_name=f"{route_prefix}.preview",
            permission=f"{permission_prefix}.view",
        )


def defaults(config, **kwargs):  # pylint: disable=missing-function-docstring
    base = globals()

    EmailSettingView = kwargs.get(  # pylint: disable=invalid-name,redefined-outer-name
        "EmailSettingView", base["EmailSettingView"]
    )
    EmailSettingView.defaults(config)


def includeme(config):  # pylint: disable=missing-function-docstring
    defaults(config)
