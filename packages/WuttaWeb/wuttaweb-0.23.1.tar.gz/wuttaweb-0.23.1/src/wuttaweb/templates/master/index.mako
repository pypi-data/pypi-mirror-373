## -*- coding: utf-8; -*-
<%inherit file="/page.mako" />

<%def name="title()">${index_title}</%def>

## nb. avoid hero bar for index page
<%def name="content_title()"></%def>

<%def name="page_content()">
  % if grid is not Undefined:
      ${self.render_grid_tag()}
  % endif
</%def>

<%def name="render_grid_tag()">
  ${grid.render_vue_tag()}
</%def>

<%def name="render_vue_templates()">
  ${parent.render_vue_templates()}
  ${self.render_vue_template_grid()}
</%def>

<%def name="render_vue_template_grid()">
  % if grid is not Undefined:
      ${grid.render_vue_template()}
  % endif
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  % if master.deletable_bulk and master.has_perm('delete_bulk'):
      <script>

        ${grid.vue_component}Data.deleteResultsSubmitting = false

        ${grid.vue_component}.computed.deleteResultsDisabled = function() {
            if (this.deleteResultsSubmitting) {
                return true
            }
            if (!this.recordCount) {
                return true
            }
            return false
        }

        ${grid.vue_component}.methods.deleteResultsSubmit = function() {

            ## TODO: should give a better dialog here
            const msg = "You are about to delete "
                  + this.recordCount.toLocaleString('en')
                  + " records.\n\nAre you sure?"
            if (!confirm(msg)) {
                return
            }

            this.deleteResultsSubmitting = true
            this.$refs.deleteResultsForm.submit()
        }

      </script>
  % endif
</%def>

<%def name="make_vue_components()">
  ${parent.make_vue_components()}
  % if grid is not Undefined:
      ${grid.render_vue_finalize()}
  % endif
</%def>
