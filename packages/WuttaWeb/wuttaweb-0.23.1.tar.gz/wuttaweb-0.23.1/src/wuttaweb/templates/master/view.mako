## -*- coding: utf-8; -*-
<%inherit file="/master/form.mako" />

<%def name="title()">${index_title} &raquo; ${instance_title}</%def>

<%def name="content_title()">${instance_title}</%def>

<%def name="page_layout()">

  % if master.has_rows:
      <div style="display: flex; flex-direction: column;">
        <div style="display: flex; justify-content: space-between;">

          ## main form
          <div style="flex-grow: 1;">
            ${self.page_content()}
          </div>

          ## tool panels
          ${self.tool_panels_wrapper()}

        </div>

        ## rows grid
        <br />
        <h4 class="block is-size-4">${master.get_rows_title() or ''}</h4>
        ${rows_grid.render_vue_tag()}
      </div>

  % else:
      ## no rows, just main form + tool panels
      ${parent.page_layout()}
  % endif
</%def>

<%def name="tool_panels()">
  ${parent.tool_panels()}
  ${self.tool_panel_xref()}
</%def>

<%def name="tool_panel_xref()">
  % if xref_buttons:
      <wutta-tool-panel heading="Cross-Reference">
        % for button in xref_buttons:
            ${button}
        % endfor
      </wutta-tool-panel>
  % endif
</%def>

<%def name="render_vue_templates()">
  ${parent.render_vue_templates()}
  % if master.has_rows:
      ${self.render_vue_template_rows_grid()}
  % endif
</%def>

<%def name="render_vue_template_rows_grid()">
  ${rows_grid.render_vue_template()}
</%def>

<%def name="make_vue_components()">
  ${parent.make_vue_components()}
  % if master.has_rows:
      ${rows_grid.render_vue_finalize()}
  % endif
</%def>
