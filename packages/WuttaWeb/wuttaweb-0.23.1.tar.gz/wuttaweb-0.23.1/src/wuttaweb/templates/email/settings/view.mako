## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />

<%def name="tool_panels()">
  ${parent.tool_panels()}
  ${self.tool_panel_preview()}
</%def>

<%def name="tool_panel_preview()">
  <wutta-tool-panel heading="Email Preview">

    <b-button type="is-primary"
              % if has_html_template:
              tag="a" target="_blank"
              href="${master.get_action_url('preview', setting)}?mode=html"
              % else:
              disabled
              title="HTML template not found"
              % endif
              icon-pack="fas"
              icon-left="external-link-alt">
      Preview HTML
    </b-button>

    <b-button type="is-primary"
              % if has_txt_template:
              tag="a" target="_blank"
              href="${master.get_action_url('preview', setting)}?mode=txt"
              % else:
              disabled
              title="TXT template not found"
              % endif
              icon-pack="fas"
              icon-left="external-link-alt">
      Preview TXT
    </b-button>

  </wutta-tool-panel>
</%def>
