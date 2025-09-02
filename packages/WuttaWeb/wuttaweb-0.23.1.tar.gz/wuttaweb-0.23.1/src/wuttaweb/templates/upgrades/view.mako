## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />

<%def name="page_content()">
  ${parent.page_content()}
  % if instance.status == app.enum.UpgradeStatus.PENDING and master.has_perm('execute'):
      <div class="buttons"
           style="margin: 2rem 5rem;">

        ${h.form(master.get_action_url('execute', instance), **{'@submit': 'executeFormSubmit'})}
          ${h.csrf_token(request)}
          <b-button type="is-primary"
                    native-type="submit"
                    icon-pack="fas"
                    icon-left="arrow-circle-right"
                    :disabled="executeFormSubmitting">
            {{ executeFormSubmitting ? "Working, please wait..." : "Execute this upgrade" }}
          </b-button>
        ${h.end_form()}
      </div>
  % endif
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  % if instance.status == app.enum.UpgradeStatus.PENDING and master.has_perm('execute'):
      <script>

        ThisPageData.executeFormSubmitting = false

        ThisPage.methods.executeFormSubmit = function() {
            this.executeFormSubmitting = true
        }

      </script>
  % endif
</%def>
