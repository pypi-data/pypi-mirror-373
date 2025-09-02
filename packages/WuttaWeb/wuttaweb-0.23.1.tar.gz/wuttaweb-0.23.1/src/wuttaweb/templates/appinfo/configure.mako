## -*- coding: utf-8; -*-
<%inherit file="/configure.mako" />

<%def name="form_content()">

  <h3 class="block is-size-3">Basics</h3>
  <div class="block" style="padding-left: 2rem; width: 50%;">

    <b-field grouped>

      <b-field label="App Title">
        <b-input name="${app.appname}.app_title"
                 v-model="simpleSettings['${app.appname}.app_title']"
                 @input="settingsNeedSaved = true">
        </b-input>
      </b-field>

      <b-field label="Node Type">
        ## TODO: should be a dropdown, app handler defines choices
        <b-input name="${app.appname}.node_type"
                 v-model="simpleSettings['${app.appname}.node_type']"
                 @input="settingsNeedSaved = true">
        </b-input>
      </b-field>

      <b-field label="Node Title">
        <b-input name="${app.appname}.node_title"
                 v-model="simpleSettings['${app.appname}.node_title']"
                 @input="settingsNeedSaved = true">
        </b-input>
      </b-field>

    </b-field>

    <b-field>
      <b-checkbox name="${app.appname}.production"
                  v-model="simpleSettings['${app.appname}.production']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Production Mode
      </b-checkbox>
      <span style="width: 1rem;" />
      <b-checkbox name="wuttaweb.themes.expose_picker"
                  v-model="simpleSettings['wuttaweb.themes.expose_picker']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Expose Theme Picker
      </b-checkbox>
    </b-field>

    <b-field label="Menu Handler">
      <input type="hidden"
             name="${app.appname}.web.menus.handler.spec"
             :value="simpleSettings['${app.appname}.web.menus.handler.spec']" />
      <b-select v-model="simpleSettings['${app.appname}.web.menus.handler.spec']"
                @input="settingsNeedSaved = true">
        <option :value="null">(use default)</option>
        <option v-for="handler in menuHandlers"
                :key="handler.spec"
                :value="handler.spec">
          {{ handler.spec }}
        </option>
      </b-select>
    </b-field>

  </div>

  <h3 class="block is-size-3">User/Auth</h3>
  <div class="block" style="padding-left: 2rem; width: 50%;">

    <div style="display: flex; align-items: center;">
      <b-checkbox name="wuttaweb.home_redirect_to_login"
                  v-model="simpleSettings['wuttaweb.home_redirect_to_login']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Home Page auto-redirect to Login
      </b-checkbox>
      <${b}-tooltip position="${'right' if request.use_oruga else 'is-right'}">
        <b-icon pack="fas" icon="info-circle" />
        <template #content>
          <p class="block">
            If set, show the Login page instead of Home page for Anonymous users.
          </p>
          <p class="block has-text-weight-bold">
            This only "enforces" Login for the Home page, not for
            other pages.  Anonymous users can see whatever the role
            permissions authorize.
          </p>
          <p class="block">
            If not set, Anonymous users will see the Home page without being redirected.
          </p>
        </template>
      </${b}-tooltip>
    </div>

  </div>

  <h3 class="block is-size-3">Email</h3>
  <div class="block" style="padding-left: 2rem; width: 50%;">

    <b-field>
      <b-checkbox name="${config.appname}.mail.send_emails"
                  v-model="simpleSettings['${config.appname}.mail.send_emails']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Enable email sending
      </b-checkbox>
    </b-field>

    <div v-show="simpleSettings['${config.appname}.mail.send_emails']">

      <b-field label="Default Sender">
        <b-input name="${app.appname}.email.default.sender"
                 v-model="simpleSettings['${app.appname}.email.default.sender']"
                 @input="settingsNeedSaved = true"
                 expanded />
      </b-field>

      <b-field label="Default Recipient(s)">
        <b-input name="${app.appname}.email.default.to"
                 v-model="simpleSettings['${app.appname}.email.default.to']"
                 @input="settingsNeedSaved = true"
                 expanded />
      </b-field>

      <b-field label="Default Subject (optional)">
        <b-input name="${app.appname}.email.default.subject"
                 v-model="simpleSettings['${app.appname}.email.default.subject']"
                 @input="settingsNeedSaved = true"
                 expanded />
      </b-field>

      <b-field label="Feedback Recipient(s) (optional)">
        <b-input name="${app.appname}.email.feedback.to"
                 v-model="simpleSettings['${app.appname}.email.feedback.to']"
                 @input="settingsNeedSaved = true"
                 expanded />
      </b-field>

      <b-field label="Feedback Subject (optional)">
        <b-input name="${app.appname}.email.feedback.subject"
                 v-model="simpleSettings['${app.appname}.email.feedback.subject']"
                 @input="settingsNeedSaved = true"
                 expanded />
      </b-field>

    </div>

  </div>

  <h3 class="block is-size-3">Web Libraries</h3>
  <div class="block" style="padding-left: 2rem;">

    <${b}-table :data="weblibs">

      <${b}-table-column field="title"
                      label="Name"
                      v-slot="props">
        {{ props.row.title }}
      </${b}-table-column>

      <${b}-table-column field="configured_version"
                      label="Version"
                      v-slot="props">
        {{ props.row.configured_version || props.row.default_version }}
      </${b}-table-column>

      <${b}-table-column field="configured_url"
                      label="URL Override"
                      v-slot="props">
        {{ props.row.configured_url }}
      </${b}-table-column>

      <${b}-table-column field="live_url"
                      label="Effective (Live) URL"
                      v-slot="props">
        <span v-if="props.row.modified"
              class="has-text-warning">
          save settings and refresh page to see new URL
        </span>
        <span v-if="!props.row.modified">
          {{ props.row.live_url }}
        </span>
      </${b}-table-column>

      <${b}-table-column field="actions"
                      label="Actions"
                      v-slot="props">
        <a href="#"
           @click.prevent="editWebLibraryInit(props.row)">
          % if request.use_oruga:
              <o-icon icon="edit" />
          % else:
              <i class="fas fa-edit"></i>
          % endif
          Edit
        </a>
      </${b}-table-column>

    </${b}-table>

    % for weblib in weblibs or []:
        ${h.hidden('wuttaweb.libver.{}'.format(weblib['key']), **{':value': "simpleSettings['wuttaweb.libver.{}']".format(weblib['key'])})}
        ${h.hidden('wuttaweb.liburl.{}'.format(weblib['key']), **{':value': "simpleSettings['wuttaweb.liburl.{}']".format(weblib['key'])})}
    % endfor

    <${b}-modal has-modal-card
                % if request.use_oruga:
                    v-model:active="editWebLibraryShowDialog"
                % else:
                    :active.sync="editWebLibraryShowDialog"
                % endif
                >
      <div class="modal-card">

        <header class="modal-card-head">
          <p class="modal-card-title">Web Library: {{ editWebLibraryRecord.title }}</p>
        </header>

        <section class="modal-card-body">

          <b-field grouped>

            <b-field label="Default Version">
              <b-input v-model="editWebLibraryRecord.default_version"
                       disabled>
              </b-input>
            </b-field>

            <b-field label="Override Version">
              <b-input v-model="editWebLibraryVersion">
              </b-input>
            </b-field>

          </b-field>

          <b-field label="Override URL">
            <b-input v-model="editWebLibraryURL"
                     expanded />
          </b-field>

          <b-field label="Effective URL (as of last page load)">
            <b-input v-model="editWebLibraryRecord.live_url"
                     disabled
                     expanded />
          </b-field>

        </section>

        <footer class="modal-card-foot">
          <b-button type="is-primary"
                    @click="editWebLibrarySave()"
                    icon-pack="fas"
                    icon-left="save">
            Save
          </b-button>
          <b-button @click="editWebLibraryShowDialog = false">
            Cancel
          </b-button>
        </footer>
      </div>
    </${b}-modal>

  </div>
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    ThisPageData.menuHandlers = ${json.dumps(menu_handlers)|n}

    ThisPageData.weblibs = ${json.dumps(weblibs or [])|n}

    ThisPageData.editWebLibraryShowDialog = false
    ThisPageData.editWebLibraryRecord = {}
    ThisPageData.editWebLibraryVersion = null
    ThisPageData.editWebLibraryURL = null

    ThisPage.methods.editWebLibraryInit = function(row) {
        this.editWebLibraryRecord = row
        this.editWebLibraryVersion = row.configured_version
        this.editWebLibraryURL = row.configured_url
        this.editWebLibraryShowDialog = true
    }

    ThisPage.methods.editWebLibrarySave = function() {
        this.editWebLibraryRecord.configured_version = this.editWebLibraryVersion
        this.editWebLibraryRecord.configured_url = this.editWebLibraryURL
        this.editWebLibraryRecord.modified = true

        this.simpleSettings[`wuttaweb.libver.${'$'}{this.editWebLibraryRecord.key}`] = this.editWebLibraryVersion
        this.simpleSettings[`wuttaweb.liburl.${'$'}{this.editWebLibraryRecord.key}`] = this.editWebLibraryURL

        this.settingsNeedSaved = true
        this.editWebLibraryShowDialog = false
    }

    ThisPage.methods.validateEmailSettings = function() {
        if (this.simpleSettings['${config.appname}.mail.send_emails']) {
            if (!this.simpleSettings['${config.appname}.email.default.sender']) {
                return "Default Sender is required to send email."
            }
            if (!this.simpleSettings['${config.appname}.email.default.to']) {
                return "Default Recipient(s) are required to send email."
            }
        }
    }

    ThisPageData.validators.push(ThisPage.methods.validateEmailSettings)

  </script>
</%def>


${parent.body()}
