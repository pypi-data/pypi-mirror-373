## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />

<%def name="tool_panels()">
  ${parent.tool_panels()}
  ${self.tool_panel_execution()}
</%def>

<%def name="tool_panel_execution()">
  <wutta-tool-panel heading="Execution">
    % if batch.executed:
        <b-notification :closable="false">
          <p class="block">
            Batch was executed<br />
            ${app.render_time_ago(batch.executed)}<br />
            by ${batch.executed_by}
          </p>
        </b-notification>
    % elif why_not_execute:
        <b-notification type="is-warning" :closable="false">
          <p class="block">
            Batch cannot be executed:
          </p>
          <p class="block">
            ${why_not_execute}
          </p>
        </b-notification>
    % else:
        % if master.has_perm('execute'):
            <b-notification type="is-success" :closable="false">
              <p class="block">
                Batch can be executed
              </p>
              <b-button type="is-primary"
                        @click="executeInit()"
                        icon-pack="fas"
                        icon-left="arrow-circle-right">
                Execute Batch
              </b-button>

              <b-modal has-modal-card
                       :active.sync="executeShowDialog">
                <div class="modal-card">

                  <header class="modal-card-head">
                    <p class="modal-card-title">Execute ${model_title}</p>
                  </header>

                  ## TODO: forcing black text b/c of b-notification
                  ## wrapping button, which has white text
                  <section class="modal-card-body has-text-black">
                    <p class="block has-text-weight-bold">
                      What will happen when this batch is executed?
                    </p>
                    <div class="content">
                      ${execution_described|n}
                    </div>
                    ${h.form(master.get_action_url('execute', batch), ref='executeForm')}
                    ${h.csrf_token(request)}
                    ${h.end_form()}
                  </section>

                  <footer class="modal-card-foot">
                    <b-button @click="executeShowDialog = false">
                      Cancel
                    </b-button>
                    <b-button type="is-primary"
                              @click="executeSubmit()"
                              icon-pack="fas"
                              icon-left="arrow-circle-right"
                              :disabled="executeSubmitting">
                      {{ executeSubmitting ? "Working, please wait..." : "Execute Batch" }}
                    </b-button>
                  </footer>

                </div>
              </b-modal>
            </b-notification>

        % else:
            <b-notification type="is-warning" :closable="false">
              <p class="block">
                Batch may be executed,<br />
                but you do not have permission.
              </p>
            </b-notification>
        % endif
    % endif
  </wutta-tool-panel>
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  % if not batch.executed and not why_not_execute and master.has_perm('execute'):
      <script>

        ThisPageData.executeShowDialog = false
        ThisPageData.executeSubmitting = false

        ThisPage.methods.executeInit = function() {
            this.executeShowDialog = true
        }

        ThisPage.methods.executeSubmit = function() {
            this.executeSubmitting = true
            this.$refs.executeForm.submit()
        }

      </script>
  % endif
</%def>
