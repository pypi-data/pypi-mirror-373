## -*- coding: utf-8; -*-
<%inherit file="/page.mako" />

<%def name="title()">Configure ${config_title}</%def>

<%def name="extra_styles()">
  ${parent.extra_styles()}
  <style>

    .wutta-form-wrapper {
        width: 75%;
    }

  </style>
</%def>

<%def name="page_content()">
  <br />
  ${self.buttons_content()}

  ${h.form(request.url, enctype='multipart/form-data', ref='saveSettingsForm', **{'@submit': 'saveSettingsFormSubmit'})}
    ${h.csrf_token(request)}
    <div class="wutta-form-wrapper">
      ${self.form_content()}
    </div>
  ${h.end_form()}

  <b-modal has-modal-card
           :active.sync="purgeSettingsShowDialog">
    <div class="modal-card">

      <header class="modal-card-head">
        <p class="modal-card-title">Remove All Settings</p>
      </header>

      <section class="modal-card-body">
        <p class="block">
          Really remove all settings for ${config_title} from the DB?
        </p>
        <p class="block">
          Note that when you <span class="is-italic">save</span>
          settings, any existing settings are first removed and then
          new ones are saved.
        </p>
        <p class="block">
          But here you can remove existing without saving new
          ones.&nbsp; It is basically "factory reset" for
          ${config_title}.
        </p>
      </section>

      <footer class="modal-card-foot">
        <b-button @click="purgeSettingsShowDialog = false">
          Cancel
        </b-button>
        ${h.form(request.url, **{'@submit': 'purgingSettings = true'})}
        ${h.csrf_token(request)}
        ${h.hidden('remove_settings', 'true')}
        <b-button type="is-danger"
                  native-type="submit"
                  :disabled="purgingSettings"
                  icon-pack="fas"
                  icon-left="trash">
          {{ purgingSettings ? "Working, please wait..." : "Remove All Settings for ${config_title}" }}
        </b-button>
        ${h.end_form()}
      </footer>
    </div>
  </b-modal>

</%def>

<%def name="buttons_content()">
  <div class="level">
    <div class="level-left">

      <div class="level-item">
        ${self.intro_message()}
      </div>

      <div class="level-item">
        ${self.save_undo_buttons()}
      </div>
    </div>

    <div class="level-right">
      <div class="level-item">
        ${self.purge_button()}
      </div>
    </div>
  </div>
</%def>

<%def name="intro_message()">
  <p class="block">
    This page lets you modify the settings for ${config_title}.
  </p>
</%def>

<%def name="save_undo_buttons()">
  <div class="buttons"
       v-if="settingsNeedSaved">
    <b-button type="is-primary"
              @click="saveSettings"
              :disabled="savingSettings"
              icon-pack="fas"
              icon-left="save">
      {{ savingSettings ? "Working, please wait..." : "Save All Settings" }}
    </b-button>
    <b-button tag="a" href="${request.url}"
              icon-pack="fas"
              icon-left="undo"
              @click="undoChanges = true"
              :disabled="undoChanges">
      {{ undoChanges ? "Working, please wait..." : "Undo All Changes" }}
    </b-button>
  </div>
</%def>

<%def name="purge_button()">
  <b-button type="is-danger"
            @click="purgeSettingsShowDialog = true"
            icon-pack="fas"
            icon-left="trash">
    Remove All Settings
  </b-button>
</%def>

<%def name="form_content()">
  <b-notification type="is-warning"
                  :closable="false">
    <h4 class="block is-size-4">
      TODO: you must define the
      <span class="is-family-monospace">&lt;%def name="form_content()"&gt;</span>
      template block
    </h4>
    <p class="block">
      or if you need more control, define the
      <span class="is-family-monospace">&lt;%def name="page_content()"&gt;</span>
      template block
    </p>
    <p class="block">
      for a real-world example see template at
      <span class="is-family-monospace">wuttaweb:templates/appinfo/configure.mako</span>
    </p>
  </b-notification>
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    % if simple_settings is not Undefined:
        ThisPageData.simpleSettings = ${json.dumps(simple_settings)|n}
    % endif

    ThisPageData.purgeSettingsShowDialog = false
    ThisPageData.purgingSettings = false

    ThisPageData.settingsNeedSaved = false
    ThisPageData.undoChanges = false
    ThisPageData.savingSettings = false
    ThisPageData.validators = []

    ThisPage.methods.saveSettings = function() {

        for (let validator of this.validators) {
            let msg = validator.call(this)
            if (msg) {
                this.$buefy.toast.open({
                    message: msg,
                    type: 'is-warning',
                    duration: 4000, // 4 seconds
                })
                return
            }
        }

        this.savingSettings = true
        this.$refs.saveSettingsForm.submit()
    }

    // nb. this is here to avoid auto-submitting form when user
    // presses ENTER while some random input field has focus
    ThisPage.methods.saveSettingsFormSubmit = function(event) {
        if (!this.savingSettings) {
            event.preventDefault()
        }
    }

    // cf. https://stackoverflow.com/a/56551646
    ThisPage.methods.beforeWindowUnload = function(e) {
        if (this.settingsNeedSaved && !this.savingSettings && !this.undoChanges && !this.purgingSettings) {
            e.preventDefault()
            e.returnValue = ''
        }
    }

    ThisPage.created = function() {
        window.addEventListener('beforeunload', this.beforeWindowUnload)
    }

  </script>
</%def>


${parent.body()}
