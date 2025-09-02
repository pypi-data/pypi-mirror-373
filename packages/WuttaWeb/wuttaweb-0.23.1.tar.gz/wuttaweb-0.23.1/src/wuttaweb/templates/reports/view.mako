## -*- coding: utf-8; mode: html; -*-
<%inherit file="/master/view.mako" />

<%def name="page_layout()">
  ${parent.page_layout()}
  % if report_data is not Undefined:
      <br />
      <a name="report-output"></a>
      <div style="display: flex; justify-content: space-between;">
        <div class="report-header">
          ${self.report_output_header()}
        </div>
        <div class="report-tools">
          ${self.report_tools()}
        </div>
      </div>
      ${self.report_output_body()}
  % endif
</%def>

<%def name="report_output_header()">
  <h4 class="is-size-4"><a href="#report-output">{{ reportData.output_title }}</a></h4>
</%def>

<%def name="report_tools()"></%def>

<%def name="report_output_body()">
  ${self.report_output_table()}
</%def>

<%def name="report_output_table()">
  <b-table :data="reportData.data"
           narrowed
           hoverable>
    % for column in report_columns:
        <b-table-column field="${column['name']}"
                        label="${column['label']}"
                        % if column.get('numeric'):
                            numeric
                        % endif
                        v-slot="props">
          <span v-html="props.row.${column['name']}"></span>
        </b-table-column>
    % endfor
  </b-table>
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  % if report_data is not Undefined:
      <script>

        ThisPageData.reportData = ${json.dumps(report_data)|n}

        WholePageData.mountedHooks.push(function() {
            location.href = '#report-output'
        })

      </script>
  % endif
</%def>
