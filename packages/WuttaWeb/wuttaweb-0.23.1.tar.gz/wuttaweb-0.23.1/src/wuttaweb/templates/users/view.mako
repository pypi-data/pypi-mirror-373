## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />

<%def name="page_content()">
  ${parent.page_content()}

  % if master.has_perm('manage_api_tokens'):
      <b-modal :active.sync="newTokenShowDialog"
               has-modal-card>
        <div class="modal-card">
          <header class="modal-card-head">
            <p class="modal-card-title">
              New API Token
            </p>
          </header>
          <section class="modal-card-body">

            <div v-if="!newTokenSaved">
              <b-field label="Description"
                       :type="{'is-danger': !newTokenDescription}">
                <b-input v-model.trim="newTokenDescription"
                         expanded
                         ref="newTokenDescription">
                </b-input>
              </b-field>
            </div>

            <div v-if="newTokenSaved">
              <p class="block">
                Your new API token is shown below.
              </p>
              <p class="block">
                IMPORTANT:&nbsp; You must record this token elsewhere
                for later reference.&nbsp; You will NOT be able to
                recover the value if you lose it.
              </p>
              <b-field horizontal label="API Token">
                {{ newTokenRaw }}
              </b-field>
              <b-field horizontal label="Description">
                {{ newTokenDescription }}
              </b-field>
            </div>

          </section>
          <footer class="modal-card-foot">
            <b-button @click="newTokenShowDialog = false">
              {{ newTokenSaved ? "Close" : "Cancel" }}
            </b-button>
            <b-button v-if="!newTokenSaved"
                      type="is-primary"
                      icon-pack="fas"
                      icon-left="save"
                      @click="newTokenSave()"
                      :disabled="!newTokenDescription || newTokenSaving">
              {{ newTokenSaving ? "Working, please wait..." : "Save" }}
            </b-button>
          </footer>
        </div>
      </b-modal>
  % endif
</%def>

<%def name="render_form_tag()">
  % if master.has_perm('manage_api_tokens'):
      ${form.render_vue_tag(**{'@new-token': 'newTokenInit', '@delete-token': 'deleteTokenInit'})}
  % else:
      ${form.render_vue_tag()}
  % endif
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>
    % if master.has_perm('manage_api_tokens'):

        ThisPageData.newTokenShowDialog = false
        ThisPageData.newTokenDescription = null
        ThisPageData.newTokenRaw = null
        ThisPageData.newTokenSaved = false
        ThisPageData.newTokenSaving = false

        ThisPage.methods.newTokenInit = function() {
            this.newTokenDescription = null
            this.newTokenRaw = null
            this.newTokenSaved = false
            this.newTokenShowDialog = true
            this.$nextTick(() => {
                this.$refs.newTokenDescription.focus()
            })
        }

        ThisPage.methods.newTokenSave = function() {
            this.newTokenSaving = true

            const url = '${master.get_action_url('add_api_token', instance)}'
            const params = {
                description: this.newTokenDescription,
            }

            this.wuttaPOST(url, params, response => {
                this.newTokenSaving = false
                this.newTokenRaw = response.data.token_string
                ${form.vue_component}Data.gridContext['users.view.api_tokens'].data.push(response.data)
                this.newTokenSaved = true
            }, response => {
                this.newTokenSaving = false
            })
        }

        ThisPage.methods.deleteTokenInit = function(token) {
            if (!confirm("Really delete this API token?")) {
                return
            }

            const url = '${master.get_action_url('delete_api_token', instance)}'
            const params = {uuid: token.uuid}
            this.wuttaPOST(url, params, response => {
                const i = ${form.vue_component}Data.gridContext['users.view.api_tokens'].data.indexOf(token)
                ${form.vue_component}Data.gridContext['users.view.api_tokens'].data.splice(i, 1)
            })
        }

    % endif
  </script>
</%def>
